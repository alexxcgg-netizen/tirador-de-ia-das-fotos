import AVFoundation
import CoreImage
import UIKit

/// Grava vídeo com o look já aplicado: cada quadro passa pela revelação e vai para um arquivo HEVC, com o som do microfone.
/// Todas as chamadas podem vir de qualquer fila; o trabalho roda numa fila própria.
final class VideoRecorder {
    private let queue = DispatchQueue(label: "revela.recorder", qos: .userInitiated)
    private var writer: AVAssetWriter?
    private var videoInput: AVAssetWriterInput?
    private var audioInput: AVAssetWriterInput?
    private var adaptor: AVAssetWriterInputPixelBufferAdaptor?
    private var started = false
    private var frames = 0
    private var url: URL?
    private var failureReported = false
    // Com trava: lidos na fila da câmera a cada quadro
    private let lock = NSLock()
    private var recording = false
    /// Quadros esperando a revelação. Acima de 2 o quadro novo é descartado: antes cada um entrava numa fila sem fim
    /// segurando um buffer da câmera, e quando a revelação não acompanhava a câmera ficava sem buffers
    private var pending = 0
    private var dropped = 0
    private let colorSpace = CGColorSpace(name: CGColorSpace.itur_709) ?? CGColorSpaceCreateDeviceRGB()

    /// O arquivo falhou no meio (disco cheio, codificador): chamado uma vez por gravação, na fila principal, com o motivo.
    /// Definido uma vez antes da primeira gravação.
    var onFailure: ((String) -> Void)?

    var isRecording: Bool {
        lock.lock()
        defer { lock.unlock() }
        return recording
    }

    /// `transform` gira o vídeo na reprodução (iPhone deitado durante a gravação).
    func start(width: Int, height: Int, fps: Int, transform: CGAffineTransform) {
        queue.async {
            self.failureReported = false
            let url = FileManager.default.temporaryDirectory.appendingPathComponent("video-\(UUID().uuidString).mov")
            guard let writer = try? AVAssetWriter(outputURL: url, fileType: .mov) else {
                dlog("❌ Vídeo: não criou o arquivo")
                self.reportFailure("Não foi possível criar o arquivo do vídeo.")
                return
            }
            // Fragmentos de 2 s: se a gravação falhar ou o app fechar no meio, o arquivo ainda abre até o último pedaço salvo
            writer.movieFragmentInterval = CMTime(seconds: 2, preferredTimescale: 600)
            // ~0,2 bit por pixel: o grão do filme é ruído de propósito e pede mais bits que um vídeo limpo
            // (4K30 ≈ 50 Mb/s, 1080p60 ≈ 25 Mb/s, 1080p30 ≈ 12 Mb/s)
            let bitRate = Int(Double(width * height * max(fps, 1)) * 0.2)
            let video = AVAssetWriterInput(mediaType: .video, outputSettings: [
                AVVideoCodecKey: AVVideoCodecType.hevc,
                AVVideoWidthKey: width,
                AVVideoHeightKey: height,
                AVVideoColorPropertiesKey: [
                    AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                    AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                    AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2,
                ],
                AVVideoCompressionPropertiesKey: [
                    AVVideoAverageBitRateKey: bitRate,
                    AVVideoExpectedSourceFrameRateKey: fps,
                ],
            ])
            video.expectsMediaDataInRealTime = true
            video.transform = transform
            let audio = AVAssetWriterInput(mediaType: .audio, outputSettings: [
                AVFormatIDKey: kAudioFormatMPEG4AAC,
                AVNumberOfChannelsKey: 1,
                AVSampleRateKey: 48_000,
                AVEncoderBitRateKey: 128_000,
            ])
            audio.expectsMediaDataInRealTime = true
            guard writer.canAdd(video) else {
                dlog("❌ Vídeo: o codificador recusou \(width)×\(height)")
                self.reportFailure("O codificador recusou o vídeo \(width)×\(height).")
                return
            }
            writer.add(video)
            if writer.canAdd(audio) { writer.add(audio) }
            // A revelação desenha direto nos buffers do próprio codificador (sem cópia no meio)
            self.adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: video, sourcePixelBufferAttributes: [
                kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
                kCVPixelBufferWidthKey as String: width,
                kCVPixelBufferHeightKey as String: height,
                kCVPixelBufferIOSurfacePropertiesKey as String: [:] as [String: Any],
            ])
            self.writer = writer
            self.videoInput = video
            self.audioInput = writer.inputs.contains(audio) ? audio : nil
            self.url = url
            self.started = false
            self.frames = 0
            self.lock.lock()
            self.recording = true
            self.dropped = 0
            self.lock.unlock()
            dlog("Vídeo: gravando \(width)×\(height) a \(fps) fps · \(bitRate / 1_000_000) Mb/s")
        }
    }

    /// Um quadro já revelado (luz linear de tela, como sai do Developer.preview).
    func append(_ image: CIImage, at time: CMTime) {
        lock.lock()
        guard recording else {
            lock.unlock()
            return
        }
        guard pending < 2 else {
            dropped += 1
            lock.unlock()
            return
        }
        pending += 1
        lock.unlock()
        queue.async {
            self.write(image, at: time)
            self.lock.lock()
            self.pending -= 1
            self.lock.unlock()
        }
    }

    /// Na fila do gravador.
    private func write(_ image: CIImage, at time: CMTime) {
        guard isRecording, let writer, let input = videoInput, let adaptor else { return }
        if !started {
            guard writer.startWriting() else {
                dlog("❌ Vídeo: \(writer.error?.localizedDescription ?? "não começou")")
                reportFailure(Self.failureText(writer.error))
                return
            }
            writer.startSession(atSourceTime: time)
            started = true
        }
        guard writer.status == .writing else {
            dlog("❌ Vídeo: o arquivo parou (\(writer.error?.localizedDescription ?? "?"))")
            reportFailure(Self.failureText(writer.error))
            return
        }
        guard input.isReadyForMoreMediaData, let pool = adaptor.pixelBufferPool else {
            lock.lock()
            dropped += 1
            lock.unlock()
            return
        }
        var buffer: CVPixelBuffer?
        CVPixelBufferPoolCreatePixelBuffer(nil, pool, &buffer)
        guard let buffer else { return }
        let bounds = CGRect(x: 0, y: 0, width: CVPixelBufferGetWidth(buffer), height: CVPixelBufferGetHeight(buffer))
        let placed = image.transformed(by: CGAffineTransform(translationX: -image.extent.minX, y: -image.extent.minY))
        Developer.context.render(placed, to: buffer, bounds: bounds, colorSpace: colorSpace)
        if adaptor.append(buffer, withPresentationTime: time) {
            frames += 1
        } else if writer.status == .failed {
            dlog("❌ Vídeo: o codificador falhou (\(writer.error?.localizedDescription ?? "?"))")
            reportFailure(Self.failureText(writer.error))
        }
    }

    func appendAudio(_ sampleBuffer: CMSampleBuffer) {
        guard isRecording else { return }
        queue.async {
            guard self.isRecording, self.started, let writer = self.writer, writer.status == .writing,
                  let input = self.audioInput, input.isReadyForMoreMediaData else { return }
            input.append(sampleBuffer)
        }
    }

    /// Fecha o arquivo. `partial`: a gravação falhou no meio e o arquivo vai até o último fragmento salvo.
    func stop(completion: @escaping (_ url: URL?, _ frames: Int, _ partial: Bool) -> Void) {
        lock.lock()
        recording = false
        lock.unlock()
        queue.async {
            let writer = self.writer, url = self.url, frames = self.frames, started = self.started
            let videoInput = self.videoInput, audioInput = self.audioInput
            self.writer = nil
            self.videoInput = nil
            self.audioInput = nil
            self.adaptor = nil
            self.url = nil
            self.started = false
            self.lock.lock()
            let dropped = self.dropped
            self.lock.unlock()
            dlog("Vídeo: \(frames) quadros gravados\(dropped > 0 ? ", \(dropped) descartados (a revelação não acompanhou)" : "")")
            guard let writer, started else {
                if let url { try? FileManager.default.removeItem(at: url) }
                completion(nil, 0, false)
                return
            }
            guard writer.status == .writing else {
                // Falhou no meio: com os fragmentos de 2 s o arquivo costuma abrir até o último pedaço
                completion(Self.hasData(url) ? url : nil, frames, true)
                return
            }
            videoInput?.markAsFinished()
            audioInput?.markAsFinished()
            writer.finishWriting {
                if writer.status == .completed {
                    completion(url, frames, false)
                } else {
                    dlog("❌ Vídeo: não fechou o arquivo (\(writer.error?.localizedDescription ?? "?"))")
                    completion(Self.hasData(url) ? url : nil, frames, true)
                }
            }
        }
    }

    /// Na fila do gravador: para de aceitar quadros e avisa o app (uma vez).
    private func reportFailure(_ text: String) {
        lock.lock()
        recording = false
        lock.unlock()
        guard !failureReported else { return }
        failureReported = true
        let callback = onFailure
        DispatchQueue.main.async { callback?(text) }
    }

    private static func failureText(_ error: Error?) -> String {
        let code = (error as NSError?)?.code
        if code == AVError.Code.diskFull.rawValue {
            return "Acabou o espaço do iPhone e a gravação parou."
        }
        return "A gravação parou por um erro (\(error?.localizedDescription ?? "desconhecido"))."
    }

    /// O arquivo existe e tem alguma coisa dentro (um pedaço de vídeo de verdade, não só o cabeçalho).
    private static func hasData(_ url: URL?) -> Bool {
        guard let url, let size = (try? url.resourceValues(forKeys: [.fileSizeKey]))?.fileSize else { return false }
        return size > 100_000
    }
}

/// Tempo extra para terminar de salvar quando o app vai para o fundo no meio (ligação, botão de início).
/// Termine com `end()`, na fila principal.
final class BackgroundTask {
    private var id = UIBackgroundTaskIdentifier.invalid

    init(_ name: String) {
        id = UIApplication.shared.beginBackgroundTask(withName: name) { [weak self] in self?.end() }
    }

    func end() {
        guard id != .invalid else { return }
        UIApplication.shared.endBackgroundTask(id)
        id = .invalid
    }
}
