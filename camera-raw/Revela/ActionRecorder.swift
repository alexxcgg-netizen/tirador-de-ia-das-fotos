import AVFoundation
import CoreImage

/// Modo AÇÃO: grava os quadros do visor em 4K a 120 fps enquanto o botão está apertado,
/// depois escolhe os mais nítidos e transforma em fotos.
/// Tudo aqui roda na fila de vídeo da câmera.
final class ActionRecorder {
    private var writer: AVAssetWriter?
    private var input: AVAssetWriterInput?
    private var startTime: CMTime?
    private(set) var frameTimes: [CMTime] = []
    private(set) var isRecording = false
    private(set) var url: URL?

    func start() {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("acao-\(UUID().uuidString).mov")
        self.url = url
        writer = nil
        input = nil
        startTime = nil
        frameTimes = []
        isRecording = true
    }

    func append(_ sampleBuffer: CMSampleBuffer) {
        guard isRecording, let url, let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let time = CMSampleBufferGetPresentationTimeStamp(sampleBuffer)
        if writer == nil {
            guard let writer = try? AVAssetWriter(outputURL: url, fileType: .mov) else {
                dlog("❌ AÇÃO: não criou o arquivo de vídeo")
                isRecording = false
                return
            }
            let settings: [String: Any] = [
                AVVideoCodecKey: AVVideoCodecType.hevc,
                AVVideoWidthKey: CVPixelBufferGetWidth(pixelBuffer),
                AVVideoHeightKey: CVPixelBufferGetHeight(pixelBuffer),
                AVVideoCompressionPropertiesKey: [
                    AVVideoAverageBitRateKey: 160_000_000,
                    AVVideoExpectedSourceFrameRateKey: 120,
                ],
            ]
            let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
            input.expectsMediaDataInRealTime = true
            guard writer.canAdd(input) else {
                dlog("❌ AÇÃO: o codificador recusou \(CVPixelBufferGetWidth(pixelBuffer))×\(CVPixelBufferGetHeight(pixelBuffer))")
                isRecording = false
                return
            }
            writer.add(input)
            writer.startWriting()
            writer.startSession(atSourceTime: time)
            self.writer = writer
            self.input = input
            startTime = time
            dlog("AÇÃO gravando \(CVPixelBufferGetWidth(pixelBuffer))×\(CVPixelBufferGetHeight(pixelBuffer))")
        }
        guard let input, input.isReadyForMoreMediaData else { return }
        if input.append(sampleBuffer) { frameTimes.append(time) }
    }

    var duration: Double {
        guard let startTime, let last = frameTimes.last else { return 0 }
        return (last - startTime).seconds
    }

    /// Termina o arquivo e devolve o endereço e o instante de cada quadro, contado a partir do início do vídeo.
    func stop(completion: @escaping (URL?, [CMTime]) -> Void) {
        isRecording = false
        guard let writer, let input, writer.status == .writing, let startTime else { return completion(nil, []) }
        input.markAsFinished()
        let times = frameTimes.map { $0 - startTime }
        let url = self.url
        writer.finishWriting {
            completion(writer.status == .completed ? url : nil, times)
        }
    }

    /// Dá nota de nitidez a cada quadro (numa versão pequena) e devolve os melhores, espaçados entre si.
    static func sharpestFrames(in url: URL, times: [CMTime], count: Int) -> [CGImage] {
        let asset = AVURLAsset(url: url)
        let scorer = AVAssetImageGenerator(asset: asset)
        scorer.requestedTimeToleranceBefore = .zero
        scorer.requestedTimeToleranceAfter = .zero
        scorer.maximumSize = CGSize(width: 640, height: 640)

        var scores: [(index: Int, score: Float)] = []
        var failures = 0
        for (i, time) in times.enumerated() {
            guard let image = try? scorer.copyCGImage(at: time, actualTime: nil) else {
                failures += 1
                continue
            }
            scores.append((i, Developer.sharpnessScore(CIImage(cgImage: image))))
        }
        if failures > 0 {
            dlog("AÇÃO: \(failures) de \(times.count) quadros não abriram (duração do vídeo \(String(format: "%.2f", asset.duration.seconds)) s)")
        }
        // Os mais nítidos, com pelo menos 3 quadros de distância (para não salvar 8 fotos iguais)
        var chosen: [Int] = []
        for candidate in scores.sorted(by: { $0.score > $1.score }) where chosen.count < count {
            if chosen.allSatisfy({ abs($0 - candidate.index) >= 3 }) { chosen.append(candidate.index) }
        }
        chosen.sort()
        dlog("AÇÃO: \(times.count) quadros avaliados, escolhidos \(chosen.map { "#\($0)" }.joined(separator: " "))")

        let full = AVAssetImageGenerator(asset: asset)
        full.requestedTimeToleranceBefore = .zero
        full.requestedTimeToleranceAfter = .zero
        return chosen.compactMap { try? full.copyCGImage(at: times[$0], actualTime: nil) }
    }
}
