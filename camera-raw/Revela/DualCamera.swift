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
    private var backDevice: AVCaptureDevice?
    private var frontDevice: AVCaptureDevice?
    /// Já chegou quadro da traseira desde o último start (na fila da dupla): erro antes disso é "não abriu".
    private var gotFrame = false

    /// Imagem montada para o visor (selfie espelhada, como num espelho), as duas câmeras separadas (para a foto e o
    /// vídeo montarem com o espelho dos Ajustes) e o horário do quadro. Na fila da câmera dupla.
    var onFrame: ((_ preview: CIImage, _ back: CIImage, _ front: CIImage?, _ time: CMTime) -> Void)?
    var onAudio: ((CMSampleBuffer) -> Void)?
    /// A dupla não abriu (no main): o app volta para a foto em vez de ficar com a tela preta.
    var onFailure: (() -> Void)?
    /// Ligação, outro app na câmera ou erro (no main): o app fecha a gravação e salva o que deu.
    var onInterrupted: (() -> Void)?

    override init() {
        super.init()
        let center = NotificationCenter.default
        center.addObserver(self, selector: #selector(sessionInterrupted(_:)),
                           name: AVCaptureSession.wasInterruptedNotification, object: session)
        center.addObserver(self, selector: #selector(sessionFailed(_:)),
                           name: AVCaptureSession.runtimeErrorNotification, object: session)
    }

    @objc private func sessionInterrupted(_ note: Notification) {
        dlog("Câmera dupla interrompida")
        DispatchQueue.main.async { self.onInterrupted?() }
    }

    @objc private func sessionFailed(_ note: Notification) {
        let error = note.userInfo?[AVCaptureSessionErrorKey] as? AVError
        dlog("❌ Câmera dupla: \(error?.localizedDescription ?? "erro")")
        queue.async {
            // Erro antes do primeiro quadro: a dupla não chegou a abrir. O app volta para a FOTO, como numa montagem
            // recusada (antes ficava na DUPLA com a tela preta)
            guard self.gotFrame else {
                DispatchQueue.main.async { self.onFailure?() }
                return
            }
            DispatchQueue.main.async { self.onInterrupted?() }
            // Os serviços de mídia reiniciaram: liga de novo
            guard let error, error.code == .mediaServicesWereReset else { return }
            if self.configured, !self.session.isRunning { self.session.startRunning() }
        }
    }

    /// Revelar de novo aberto: a dupla descansa junto com a câmera principal.
    func pause() {
        queue.async {
            if self.session.isRunning { self.session.stopRunning() }
        }
    }

    func resume() {
        queue.async {
            if self.configured, !self.session.isRunning { self.session.startRunning() }
        }
    }

    func start(withAudio: Bool) {
        queue.async {
            self.gotFrame = false
            if !self.configured {
                self.configured = self.configure(withAudio: withAudio)
                guard self.configured else {
                    // Uma câmera ligou e a outra não: solta tudo para a próxima tentativa começar limpa
                    self.releaseEverything()
                    DispatchQueue.main.async { self.onFailure?() }
                    return
                }
                // As duas câmeras juntas passaram da cota do hardware: volta aos formatos de antes
                if self.session.hardwareCost > 1 { self.useLighterFormats() }
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
            gotFrame = false
            releaseEverything()
            configured = false
            backDevice = nil
            frontDevice = nil
            dlog("Câmera dupla desligada e câmeras soltas")
        }
    }

    /// Tira ligações, entradas e saídas da sessão dupla (também depois de uma montagem pela metade).
    private func releaseEverything() {
        guard !session.inputs.isEmpty || !session.outputs.isEmpty else { return }
        attempt("Soltar a câmera dupla") {
            session.beginConfiguration()
            session.connections.forEach { session.removeConnection($0) }
            session.inputs.forEach { session.removeInput($0) }
            session.outputs.forEach { session.removeOutput($0) }
            session.commitConfiguration()
        }
    }

    private func configure(withAudio: Bool) -> Bool {
        guard let back = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let front = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            dlog("❌ Câmera dupla: câmeras não encontradas")
            return false
        }
        backDevice = back
        frontDevice = front
        // O som fica por conta do app (CameraModel.prepareAudioSession): a configuração automática calava outros apps
        session.automaticallyConfiguresApplicationAudioSession = false
        session.beginConfiguration()
        defer { session.commitConfiguration() }
        // Cada câmera num formato que aceita rodar junto com a outra, no máximo 1920 de largura
        for (device, isFront) in [(back, false), (front, true)] {
            if let best = Self.format(for: device, front: isFront, fourByThree: true) {
                Self.use(best, on: device)
            }
        }
        var connected = false
        // A frontal chega espelhada, como no visor; a foto e o vídeo desespelham com fileFront (sem perda)
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

    /// Formato de uma câmera da dupla. Traseira em 4:3 (1920×1440): a foto e o visor 3:4 mostram o quadro inteiro, sem
    /// cortar a selfie do canto. Frontal no menor 4:3 com 1280 ou mais (o quadrinho usa 30% da largura: mais que isso só
    /// gastava a cota de hardware das duas juntas). `fourByThree: false`: o maior até 1920, como antes.
    private static func format(for device: AVCaptureDevice, front: Bool, fourByThree: Bool) -> AVCaptureDevice.Format? {
        func dims(_ f: AVCaptureDevice.Format) -> CMVideoDimensions { CMVideoFormatDescriptionGetDimensions(f.formatDescription) }
        let usable = device.formats.filter { $0.isMultiCamSupported && dims($0).width <= 1920 }
        if fourByThree {
            let fours = usable.filter {
                let d = dims($0)
                return d.height > 0 && abs(Double(d.width) / Double(d.height) - 4.0 / 3.0) < 0.02
            }
            if front, let small = fours.filter({ dims($0).width >= 1280 }).min(by: { dims($0).width < dims($1).width }) {
                return small
            }
            if let big = fours.max(by: { dims($0).width < dims($1).width }) { return big }
        }
        // Frontal no recurso (a cota já estourou): o menor com 1280 ou mais. O maior até 1920 era justo o mais pesado
        if front, let small = usable.filter({ dims($0).width >= 1280 }).min(by: { dims($0).width < dims($1).width }) {
            return small
        }
        return usable.max(by: { dims($0).width < dims($1).width })
    }

    private static func use(_ format: AVCaptureDevice.Format, on device: AVCaptureDevice) {
        guard (try? device.lockForConfiguration()) != nil else { return }
        attempt("Formato da câmera dupla") {
            device.activeFormat = format
            // Sem zoom: o objeto da câmera é o mesmo da sessão principal e podia vir com o zoom do VÍDEO
            if device.videoZoomFactor != 1 { device.videoZoomFactor = 1 }
        }
        device.unlockForConfiguration()
        let d = CMVideoFormatDescriptionGetDimensions(format.formatDescription)
        dlog("Câmera dupla: \(device.localizedName) em \(d.width)×\(d.height)")
    }

    /// Formatos mais leves quando o 4:3 passou da cota de hardware: traseira no maior até 1920, frontal no menor com 1280.
    private func useLighterFormats() {
        dlog(String(format: "Câmera dupla: custo de hardware %.2f com 4:3, voltando aos formatos de antes", session.hardwareCost))
        session.beginConfiguration()
        for (device, isFront) in [(backDevice, false), (frontDevice, true)] {
            guard let device, let format = Self.format(for: device, front: isFront, fourByThree: false) else { continue }
            Self.use(format, on: device)
        }
        session.commitConfiguration()
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
        gotFrame = true
        let front = latestFront
        onFrame?(Self.compose(back: image, front: front), image, front, CMSampleBufferGetPresentationTimeStamp(sampleBuffer))
    }

    /// Selfie da foto e do vídeo. Ela chega espelhada (como no visor) e gira junto com a traseira quando a foto/vídeo
    /// é posta em pé (`degrees`, o giro da traseira). Com o espelho dos Ajustes ligado fica assim; desligado, é
    /// desespelhada no eixo que vira o horizontal depois do giro (com o iPhone deitado, o vertical do quadro): antes
    /// saía sempre espelhada, e o espelho dos Ajustes espelhava a cena de trás inteira.
    static func fileFront(_ front: CIImage, mirrored: Bool, degrees: CGFloat) -> CIImage {
        guard !mirrored else { return front }
        let quarterTurns = (Int((degrees / 90).rounded()) % 2 + 2) % 2
        return front.oriented(quarterTurns == 0 ? .upMirrored : .downMirrored)
    }

    /// A frontal ocupa 30% da largura, no canto de cima à direita, com cantos arredondados.
    static func compose(back: CIImage, front: CIImage?) -> CIImage {
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
