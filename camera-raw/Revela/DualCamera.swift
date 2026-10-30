import AVFoundation
import CoreImage
import CoreImage.CIFilterBuiltins

/// Câmera dupla: traseira e frontal ao mesmo tempo (AVCaptureMultiCamSession).
/// Entrega a imagem montada: a traseira inteira e a frontal num quadrinho com cantos arredondados.
final class DualCamera: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate, AVCaptureAudioDataOutputSampleBufferDelegate {
    static var isSupported: Bool { AVCaptureMultiCamSession.isMultiCamSupported }

    private let session = AVCaptureMultiCamSession()
    private let backOutput = AVCaptureVideoDataOutput()
    private let frontOutput = AVCaptureVideoDataOutput()
    private let audioOutput = AVCaptureAudioDataOutput()
    private let queue = DispatchQueue(label: "revela.dual", qos: .userInteractive)
    private var latestFront: CIImage?
    private var configured = false

    /// Imagem montada + horário do quadro (na fila da câmera dupla).
    var onFrame: ((CIImage, CMTime) -> Void)?
    var onAudio: ((CMSampleBuffer) -> Void)?

    func start(withAudio: Bool) {
        queue.async {
            if !self.configured {
                self.configured = self.configure(withAudio: withAudio)
                guard self.configured else { return }
            }
            self.session.startRunning()
            dlog("Câmera dupla ligada · custo de hardware \(String(format: "%.2f", self.session.hardwareCost))")
        }
    }

    /// Para e solta as câmeras (espera terminar), para a sessão principal poder reabrir a câmera de trás no formato de foto.
    func stopAndRelease() {
        queue.sync {
            if session.isRunning { session.stopRunning() }
            latestFront = nil
            guard configured else { return }
            session.beginConfiguration()
            session.connections.forEach { session.removeConnection($0) }
            session.inputs.forEach { session.removeInput($0) }
            session.outputs.forEach { session.removeOutput($0) }
            session.commitConfiguration()
            configured = false
            dlog("Câmera dupla desligada e câmeras soltas")
        }
    }

    private func configure(withAudio: Bool) -> Bool {
        guard let back = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let front = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            dlog("❌ Câmera dupla: câmeras não encontradas")
            return false
        }
        session.beginConfiguration()
        defer { session.commitConfiguration() }
        // Cada câmera num formato que aceita rodar junto com a outra, no máximo 1920 de largura
        for device in [back, front] {
            let formats = device.formats.filter {
                let d = CMVideoFormatDescriptionGetDimensions($0.formatDescription)
                return $0.isMultiCamSupported && d.width <= 1920
            }
            if let best = formats.max(by: {
                CMVideoFormatDescriptionGetDimensions($0.formatDescription).width < CMVideoFormatDescriptionGetDimensions($1.formatDescription).width
            }), (try? device.lockForConfiguration()) != nil {
                device.activeFormat = best
                device.unlockForConfiguration()
            }
        }
        var connected = false
        attempt("Ligar as duas câmeras") {
            connected = connect(back, to: backOutput, mirrored: false) && connect(front, to: frontOutput, mirrored: true)
        }
        guard connected else { return false }
        if withAudio, let mic = AVCaptureDevice.default(for: .audio), let input = try? AVCaptureDeviceInput(device: mic),
           session.canAddInput(input), session.canAddOutput(audioOutput) {
            session.addInput(input)
            session.addOutput(audioOutput)
            audioOutput.setSampleBufferDelegate(self, queue: queue)
        }
        return true
    }

    private func connect(_ device: AVCaptureDevice, to output: AVCaptureVideoDataOutput, mirrored: Bool) -> Bool {
        guard let input = try? AVCaptureDeviceInput(device: device), session.canAddInput(input) else {
            dlog("❌ Câmera dupla: não abriu \(device.localizedName)")
            return false
        }
        session.addInputWithNoConnections(input)
        guard session.canAddOutput(output) else { return false }
        session.addOutputWithNoConnections(output)
        output.alwaysDiscardsLateVideoFrames = true
        output.setSampleBufferDelegate(self, queue: queue)
        guard let port = input.ports(for: .video, sourceDeviceType: device.deviceType, sourceDevicePosition: device.position).first else {
            return false
        }
        let connection = AVCaptureConnection(inputPorts: [port], output: output)
        guard session.canAddConnection(connection) else {
            dlog("❌ Câmera dupla: o iPhone recusou a ligação de \(device.localizedName)")
            return false
        }
        session.addConnection(connection)
        if connection.isVideoRotationAngleSupported(90) { connection.videoRotationAngle = 90 }
        if mirrored, connection.isVideoMirroringSupported {
            connection.automaticallyAdjustsVideoMirroring = false
            connection.isVideoMirrored = true
        }
        return true
    }

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        if output === audioOutput {
            onAudio?(sampleBuffer)
            return
        }
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let image = CIImage(cvPixelBuffer: pixelBuffer)
        if output === frontOutput {
            latestFront = image
            return
        }
        onFrame?(compose(back: image, front: latestFront), CMSampleBufferGetPresentationTimeStamp(sampleBuffer))
    }

    /// A frontal ocupa 30% da largura, no canto de cima à direita, com cantos arredondados.
    private func compose(back: CIImage, front: CIImage?) -> CIImage {
        guard let front else { return back }
        let b = back.extent
        let width = b.width * 0.3
        let scale = width / front.extent.width
        let height = front.extent.height * scale
        let margin = b.width * 0.04
        let origin = CGPoint(x: b.maxX - width - margin, y: b.maxY - height - margin)
        let placed = front
            .transformed(by: CGAffineTransform(translationX: -front.extent.minX, y: -front.extent.minY))
            .transformed(by: CGAffineTransform(scaleX: scale, y: scale))
            .transformed(by: CGAffineTransform(translationX: origin.x, y: origin.y))
        let rect = CGRect(origin: origin, size: CGSize(width: width, height: height))
        let shape = CIFilter.roundedRectangleGenerator()
        shape.extent = rect
        shape.radius = Float(width * 0.12)
        shape.color = CIColor.white
        guard let mask = shape.outputImage else { return placed.composited(over: back) }
        return placed.applyingFilter("CIBlendWithAlphaMask", parameters: [
            kCIInputBackgroundImageKey: back,
            kCIInputMaskImageKey: mask,
        ])
    }
}
