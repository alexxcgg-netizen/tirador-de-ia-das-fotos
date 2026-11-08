import AVFoundation
import CoreImage

/// Modo AÇÃO: grava os quadros do visor em 4K a 120 fps enquanto o botão está apertado,
/// depois escolhe os mais nítidos e transforma em fotos.
/// Tudo aqui roda na fila de vídeo da câmera (a nota de nitidez, numa fila própria).
final class ActionRecorder {
    /// Segurar mais que isso não grava mais: 5 s a 120 fps já são 600 quadros e uns 100 MB
    static let maxSeconds = 5.0
    typealias Score = (index: Int, score: Float)

    private var writer: AVAssetWriter?
    private var input: AVAssetWriterInput?
    private var startTime: CMTime?
    private var transform = CGAffineTransform.identity
    private(set) var frameTimes: [CMTime] = []
    private(set) var isRecording = false
    private(set) var url: URL?

    // Nota de nitidez de cada quadro, dada na hora numa versão pequena. Antes cada quadro era aberto de novo do HEVC
    // depois de gravar (busca exata num vídeo de GOP longo): minutos para 5 s segurando
    private let scoreQueue = DispatchQueue(label: "revela.action.score", qos: .utility)
    private let scoreLock = NSLock()
    private var scoring = false
    private var generation = 0
    private var scores: [Score] = []

    /// `transform` gira o vídeo na reprodução (iPhone deitado na hora).
    func start(transform: CGAffineTransform) {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("acao-\(UUID().uuidString).mov")
        self.url = url
        self.transform = transform
        writer = nil
        input = nil
        startTime = nil
        frameTimes = []
        scoreLock.lock()
        generation += 1
        scores = []
        scoreLock.unlock()
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
            // Fragmentos de 0,5 s: se o arquivo falhar no meio ou não fechar, ele ainda abre até o último pedaço salvo
            writer.movieFragmentInterval = CMTime(seconds: 0.5, preferredTimescale: 600)
            let settings: [String: Any] = [
                AVVideoCodecKey: AVVideoCodecType.hevc,
                AVVideoWidthKey: CVPixelBufferGetWidth(pixelBuffer),
                AVVideoHeightKey: CVPixelBufferGetHeight(pixelBuffer),
                AVVideoCompressionPropertiesKey: [
                    AVVideoAverageBitRateKey: 160_000_000,
                    AVVideoExpectedSourceFrameRateKey: 120,
                    // Quadro-chave a cada 1/4 s: abrir um quadro exato do vídeo decodifica no máximo 30, não centenas
                    AVVideoMaxKeyFrameIntervalKey: 30,
                ],
            ]
            let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
            input.expectsMediaDataInRealTime = true
            input.transform = transform
            guard writer.canAdd(input) else {
                dlog("❌ AÇÃO: o codificador recusou \(CVPixelBufferGetWidth(pixelBuffer))×\(CVPixelBufferGetHeight(pixelBuffer))")
                isRecording = false
                return
            }
            writer.add(input)
            // startSession num arquivo que não começou derruba o app (exceção do AVFoundation)
            guard writer.startWriting() else {
                dlog("❌ AÇÃO: o arquivo não começou (\(writer.error?.localizedDescription ?? "?"))")
                isRecording = false
                return
            }
            writer.startSession(atSourceTime: time)
            self.writer = writer
            self.input = input
            startTime = time
            dlog("AÇÃO gravando \(CVPixelBufferGetWidth(pixelBuffer))×\(CVPixelBufferGetHeight(pixelBuffer))")
        }
        guard let writer, writer.status == .writing else {
            if self.writer?.status == .failed {
                dlog("❌ AÇÃO: o arquivo falhou (\(self.writer?.error?.localizedDescription ?? "?"))")
                isRecording = false
            }
            return
        }
        if let startTime, (time - startTime).seconds > Self.maxSeconds { return }
        guard let input, input.isReadyForMoreMediaData, input.append(sampleBuffer) else { return }
        frameTimes.append(time)
        score(pixelBuffer, index: frameTimes.count - 1)
    }

    /// Uma nota por vez: se a anterior ainda está sendo calculada, este quadro fica sem nota (não segura buffers da câmera).
    private func score(_ pixelBuffer: CVPixelBuffer, index: Int) {
        scoreLock.lock()
        let busy = scoring
        if !busy { scoring = true }
        let token = generation
        scoreLock.unlock()
        guard !busy else { return }
        let image = CIImage(cvPixelBuffer: pixelBuffer)
        scoreQueue.async {
            let value = Developer.sharpnessScore(image)
            self.scoreLock.lock()
            if token == self.generation { self.scores.append((index: index, score: value)) }
            self.scoring = false
            self.scoreLock.unlock()
        }
    }

    var duration: Double {
        guard let startTime, let last = frameTimes.last else { return 0 }
        return (last - startTime).seconds
    }

    /// Termina o arquivo e devolve o endereço, o instante de cada quadro (contado do início do vídeo) e as notas de nitidez.
    func stop(completion: @escaping (URL?, [CMTime], [Score]) -> Void) {
        isRecording = false
        guard let writer, let input, let startTime else {
            if let url { try? FileManager.default.removeItem(at: url) }
            return completion(nil, [], [])
        }
        let times = frameTimes.map { $0 - startTime }
        let url = self.url
        let deliver: (Bool) -> Void = { closed in
            // Na fila das notas: a última que estava sendo calculada termina antes
            self.scoreQueue.async {
                self.scoreLock.lock()
                let scores = self.scores
                self.scoreLock.unlock()
                // Não fechou ou falhou no meio: com os fragmentos de 0,5 s o arquivo abre até o último pedaço salvo
                // (os quadros de depois dele simplesmente não abrem). Antes apagava tudo
                let usable = closed || VideoRecorder.hasData(url)
                if !closed { dlog("⚠️ AÇÃO: o arquivo não fechou (\(writer.error?.localizedDescription ?? "?"))\(usable ? "; usando o que foi salvo" : "")") }
                if !usable, let url { try? FileManager.default.removeItem(at: url) }
                completion(usable ? url : nil, times, scores)
            }
        }
        guard writer.status == .writing else { return deliver(false) }
        input.markAsFinished()
        writer.finishWriting { deliver(writer.status == .completed) }
    }

    /// Os mais nítidos, com pelo menos 3 quadros de distância (para não salvar 8 fotos iguais). Em ordem.
    static func choose(_ scores: [Score], frameCount: Int, count: Int) -> [Int] {
        var chosen: [Int] = []
        for candidate in scores.sorted(by: { $0.score > $1.score }) where chosen.count < count {
            guard candidate.index < frameCount else { continue }
            if chosen.allSatisfy({ abs($0 - candidate.index) >= 3 }) { chosen.append(candidate.index) }
        }
        // Sem notas (a GPU não deu conta): quadros espaçados ao longo da gravação
        if chosen.isEmpty, frameCount > 0 {
            let n = min(count, frameCount)
            chosen = (0..<n).map { $0 * frameCount / n }
        }
        chosen.sort()
        dlog("AÇÃO: \(scores.count) de \(frameCount) quadros com nota, escolhidos \(chosen.map { "#\($0)" }.joined(separator: " "))")
        return chosen
    }

    /// Abre só os quadros escolhidos, em resolução cheia (sem o giro do vídeo: quem chama põe em pé).
    static func frames(in url: URL, at times: [CMTime]) -> [CGImage] {
        let generator = AVAssetImageGenerator(asset: AVURLAsset(url: url))
        generator.requestedTimeToleranceBefore = .zero
        generator.requestedTimeToleranceAfter = .zero
        return times.compactMap { try? generator.copyCGImage(at: $0, actualTime: nil) }
    }
}
