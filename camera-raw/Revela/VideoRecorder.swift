import AVFoundation
import CoreImage

/// Grava vídeo com o look já aplicado: cada quadro passa pela revelação e vai para um arquivo HEVC, com o som do microfone.
/// Todas as chamadas podem vir de qualquer fila; o trabalho roda numa fila própria.
final class VideoRecorder {
    private let queue = DispatchQueue(label: "revela.recorder")
    private var writer: AVAssetWriter?
    private var videoInput: AVAssetWriterInput?
    private var audioInput: AVAssetWriterInput?
    private var adaptor: AVAssetWriterInputPixelBufferAdaptor?
    private var started = false
    private var recording = false
    private var frames = 0
    private var url: URL?
    private let lock = NSLock()
    private let colorSpace = CGColorSpace(name: CGColorSpace.itur_709) ?? CGColorSpaceCreateDeviceRGB()

    var isRecording: Bool {
        lock.lock()
        defer { lock.unlock() }
        return recording
    }

    /// `transform` gira o vídeo na reprodução (iPhone deitado durante a gravação).
    func start(width: Int, height: Int, fps: Int, transform: CGAffineTransform) {
        queue.async {
            let url = FileManager.default.temporaryDirectory.appendingPathComponent("video-\(UUID().uuidString).mov")
            guard let writer = try? AVAssetWriter(outputURL: url, fileType: .mov) else {
                dlog("❌ Vídeo: não criou o arquivo")
                return
            }
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
                    AVVideoAverageBitRateKey: width * height * fps / 4,
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
                return
            }
            writer.add(video)
            if writer.canAdd(audio) { writer.add(audio) }
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
            self.lock.unlock()
            dlog("Vídeo: gravando \(width)×\(height) a \(fps) fps")
        }
    }

    /// Um quadro já revelado (luz linear de tela, como sai do Developer.preview).
    func append(_ image: CIImage, at time: CMTime) {
        queue.async {
            guard self.isRecording, let writer = self.writer, let input = self.videoInput, let adaptor = self.adaptor else { return }
            if !self.started {
                guard writer.startWriting() else {
                    dlog("❌ Vídeo: \(writer.error?.localizedDescription ?? "não começou")")
                    return
                }
                writer.startSession(atSourceTime: time)
                self.started = true
            }
            guard input.isReadyForMoreMediaData, let pool = adaptor.pixelBufferPool else { return }
            var buffer: CVPixelBuffer?
            CVPixelBufferPoolCreatePixelBuffer(nil, pool, &buffer)
            guard let buffer else { return }
            let bounds = CGRect(x: 0, y: 0, width: CVPixelBufferGetWidth(buffer), height: CVPixelBufferGetHeight(buffer))
            let placed = image.transformed(by: CGAffineTransform(translationX: -image.extent.minX, y: -image.extent.minY))
            Developer.context.render(placed, to: buffer, bounds: bounds, colorSpace: self.colorSpace)
            if adaptor.append(buffer, withPresentationTime: time) { self.frames += 1 }
        }
    }

    func appendAudio(_ sampleBuffer: CMSampleBuffer) {
        queue.async {
            guard self.isRecording, self.started, let input = self.audioInput, input.isReadyForMoreMediaData else { return }
            input.append(sampleBuffer)
        }
    }

    func stop(completion: @escaping (URL?, Int) -> Void) {
        queue.async {
            self.lock.lock()
            self.recording = false
            self.lock.unlock()
            guard let writer = self.writer, self.started, writer.status == .writing else {
                completion(nil, 0)
                return
            }
            self.videoInput?.markAsFinished()
            self.audioInput?.markAsFinished()
            let url = self.url, frames = self.frames
            writer.finishWriting {
                completion(writer.status == .completed ? url : nil, frames)
            }
            self.writer = nil
        }
    }
}
