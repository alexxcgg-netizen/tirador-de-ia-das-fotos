import AVFoundation
import Photos
import UIKit
import Vision

enum RawMode: String, CaseIterable, Identifiable {
    case proRAW = "ProRAW"
    case bayer = "RAW puro"

    var id: String { rawValue }
}

/// Cada "lente" do app é uma câmera física + um recorte digital do sensor de 48 MP.
enum Lens: String, CaseIterable, Identifiable {
    case macro = "Macro"
    case ultraWide = "0.5×"
    case wide = "1×"
    case wide2x = "2×"
    case tele = "4×"
    case tele8x = "8×"
    case front = "Frente"

    var id: String { rawValue }

    var deviceType: AVCaptureDevice.DeviceType {
        switch self {
        case .macro, .ultraWide: return .builtInUltraWideCamera
        case .wide, .wide2x, .front: return .builtInWideAngleCamera
        case .tele, .tele8x: return .builtInTelephotoCamera
        }
    }

    var position: AVCaptureDevice.Position { self == .front ? .front : .back }

    /// Mesma câmera física (troca só o recorte, sem reabrir a sessão).
    func sameCamera(as other: Lens) -> Bool { deviceType == other.deviceType && position == other.position }

    /// Recorte central do sensor. 2× de 48 MP = 12 MP com qualidade óptica.
    var zoom: CGFloat {
        switch self {
        case .macro, .wide2x, .tele8x: return 2
        default: return 1
        }
    }
}

enum CaptureMode: String, CaseIterable, Identifiable {
    case photo = "FOTO"
    case portrait = "RETRATO"
    case night = "NOITE"
    case stars = "ESTRELAS"
    case moon = "LUA"
    case flash = "FLASH"
    case focusStack = "FOCO EMPILHADO"
    case average = "MÉDIA"

    var id: String { rawValue }

    var frameCount: Int {
        switch self {
        case .photo, .portrait, .flash: return 1
        case .night, .moon, .average: return 8
        case .stars: return 16
        case .focusStack: return 7
        }
    }

    /// Como juntar os quadros, quando há mais de um.
    var stackKind: Developer.StackKind? {
        switch self {
        case .photo, .portrait, .flash: return nil
        case .focusStack: return .focus
        case .night, .stars, .moon, .average: return .average
        }
    }

    var hint: String {
        switch self {
        case .photo: return ""
        case .portrait: return "Lente 2× a 1,5–2 m: o rosto fica com as proporções que as pessoas veem."
        case .night: return "8 fotos a 1/15 s alinhadas e somadas: noite limpa, sem o processamento da Apple."
        case .stars: return "16 exposições longas com foco no infinito. Use tripé ou apoie o iPhone."
        case .moon: return "Lente 8×, foco no infinito e exposição para a Lua. 8 fotos somadas para mais detalhe."
        case .flash: return "Uma foto RAW com o flash."
        case .focusStack: return "7 fotos com foco do perto ao longe, juntadas no mais nítido. Apoie o iPhone."
        case .average: return "8 fotos somadas: menos ruído, ou água lisa com obturador lento."
        }
    }
}

enum RevelaError: LocalizedError {
    case noRawData
    case developFailed
    case photosDenied

    var errorDescription: String? {
        switch self {
        case .noRawData: return "A câmera não entregou o arquivo RAW."
        case .developFailed: return "Não foi possível revelar o RAW. O DNG foi salvo mesmo assim."
        case .photosDenied: return "Sem permissão para salvar na galeria. Libere em Ajustes → Revela → Fotos."
        }
    }
}

final class CameraModel: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    static let allISO: [Float] = [25, 32, 40, 50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640,
                                  800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800]
    static let allShutter: [Double] = [8000, 6400, 5000, 4000, 3200, 2500, 2000, 1600, 1250, 1000, 800, 640,
                                       500, 400, 320, 250, 200, 160, 125, 100, 80, 60, 50, 40, 30, 25, 20,
                                       15, 13, 10, 8, 6, 5, 4, 3, 2, 1].map { 1 / $0 }

    let session = AVCaptureSession()
    let renderer = PreviewRenderer()
    private let photoOutput = AVCapturePhotoOutput()
    private let videoOutput = AVCaptureVideoDataOutput()
    private let sessionQueue = DispatchQueue(label: "revela.session")
    private let videoQueue = DispatchQueue(label: "revela.video", qos: .userInteractive)
    private var device: AVCaptureDevice?
    private var rotationCoordinator: AVCaptureDevice.RotationCoordinator?
    private var inFlight: [Int64: RawCaptureDelegate] = [:]
    private var readoutTimer: Timer?
    private var lastBackLens: Lens = .wide
    private var videoFrameIndex = 0
    private var facelessFrames = 0
    private var lastFaceFocus = Date.distantPast
    /// Campo de visão do lado curto da imagem (retrato), para estimar a distância do rosto.
    private var shortSideFOV: Double = 1.0
    private let defaults = UserDefaults.standard

    @Published var authorized = true
    @Published var availableLenses: [Lens] = []
    @Published var hasFront = false
    @Published var lens: Lens = .wide
    @Published var rawMode: RawMode = .proRAW
    @Published var proRAWSupported = true
    @Published private(set) var captureMode: CaptureMode = .photo
    /// Ajustes que uma cena (Lua, Estrelas) ligou sozinha e que voltam ao sair dela.
    private var sceneTookOver = false

    // Revelação
    @Published var look: Look = .filme { didSet { optionsChanged() } }
    @Published var lookAmount: Float = 1 { didSet { optionsChanged() } }
    @Published var grainAmount: Float = 1 { didSet { optionsChanged() } }
    @Published var aspect: AspectRatio = .r43 { didSet { optionsChanged() } }

    // Ajudas do visor
    @Published var zebra = false { didSet { renderer.options.zebra = zebra } }
    @Published var peaking = false { didSet { renderer.options.peaking = peaking } }
    @Published var loupe = false { didSet { renderer.loupe = loupe } }
    @Published var showGrid = true
    /// Salva a foto invertida, como num espelho.
    @Published var mirror = false { didSet { optionsChanged() } }
    /// Rosto encontrado no visor (0…1, origem no canto de cima à esquerda) e distância estimada em metros.
    @Published var faceRect: CGRect?
    @Published var faceDistance: Double?
    @Published var timerSeconds = 0
    @Published var countdown = 0
    @Published var histogram: [Float] = []
    @Published var flash = false
    /// Ponto do último toque para focar, em coordenadas normalizadas do visor.
    @Published var focusPoint: CGPoint?

    @Published var isoStops: [Float] = [100]
    @Published var shutterStops: [Double] = [1.0 / 60]

    @Published var manualExposure = false { didSet { updateExposure() } }
    @Published var isoIndex: Double = 0 { didSet { updateExposure() } }
    @Published var shutterIndex: Double = 0 { didSet { updateExposure() } }
    @Published var evBias: Float = 0 { didSet { updateExposure() } }
    @Published var manualWB = false { didSet { updateWhiteBalance() } }
    @Published var kelvin: Float = 5600 { didSet { updateWhiteBalance() } }
    @Published var manualFocus = false { didSet { updateFocus() } }
    @Published var lensPosition: Float = 0.5 { didSet { updateFocus() } }

    @Published var readoutISO: Float = 0
    @Published var readoutShutter: Double = 0
    @Published var readoutLensPosition: Float = 0
    @Published var processing = 0
    /// "3/7" enquanto uma sequência está sendo fotografada.
    @Published var stackProgress: String?
    @Published var message: String?
    @Published var thumbnail: UIImage?

    var selectedISO: Float { isoStops[min(max(Int(isoIndex), 0), isoStops.count - 1)] }
    var selectedShutter: Double { shutterStops[min(max(Int(shutterIndex), 0), shutterStops.count - 1)] }

    var developOptions: DevelopOptions {
        DevelopOptions(look: look, amount: lookAmount, grain: grainAmount, zoom: lens.zoom, aspect: aspect, mirror: mirror)
    }

    override init() {
        super.init()
        Diagnostics.shared.startMonitoring()
        if let saved = defaults.string(forKey: "look").flatMap(Look.init(rawValue:)) { look = saved }
        if let saved = defaults.string(forKey: "aspect").flatMap(AspectRatio.init(rawValue:)) { aspect = saved }
        if defaults.object(forKey: "lookAmount") != nil { lookAmount = defaults.float(forKey: "lookAmount") }
        if defaults.object(forKey: "grainAmount") != nil { grainAmount = defaults.float(forKey: "grainAmount") }
        mirror = defaults.bool(forKey: "mirror")
        optionsChanged()
        renderer.onHistogram = { [weak self] bins in self?.histogram = bins }
    }

    private func optionsChanged() {
        renderer.options.develop = developOptions
        defaults.set(look.rawValue, forKey: "look")
        defaults.set(aspect.rawValue, forKey: "aspect")
        defaults.set(lookAmount, forKey: "lookAmount")
        defaults.set(grainAmount, forKey: "grainAmount")
        defaults.set(mirror, forKey: "mirror")
    }

    // MARK: - Sessão

    func start() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            configure()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async {
                    self.authorized = granted
                    if granted { self.configure() }
                }
            }
        default:
            authorized = false
        }
    }

    private func configure() {
        availableLenses = Lens.allCases.filter {
            $0 != .front && AVCaptureDevice.default($0.deviceType, for: .video, position: $0.position) != nil
        }
        hasFront = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) != nil
        let lens = self.lens
        let mode = self.rawMode
        sessionQueue.async {
            if #available(iOS 18.0, *), self.session.supportsControls {
                self.session.setControlsDelegate(self, queue: self.sessionQueue)
            }
            self.setupSession(lens: lens, mode: mode)
            if !self.session.isRunning { self.session.startRunning() }
        }
        startReadout()
    }

    func select(lens newLens: Lens) {
        guard newLens != lens else { return }
        let old = lens
        lens = newLens
        optionsChanged()
        if newLens == .macro {
            peaking = true
            if !manualFocus { lensPosition = 0 }
        } else if old == .macro {
            peaking = false
        }
        if newLens != .front { lastBackLens = newLens }
        faceRect = nil
        faceDistance = nil
        // Mesma câmera física (ex.: 1× -> 2×): só muda o recorte, sem reabrir a sessão
        guard !newLens.sameCamera(as: old) else { return }
        let mode = rawMode
        sessionQueue.async {
            self.setupSession(lens: newLens, mode: mode)
            DispatchQueue.main.async {
                self.updateExposure()
                self.updateWhiteBalance()
                self.updateFocus()
            }
        }
    }

    /// Botão de virar a câmera.
    func flipCamera() {
        select(lens: lens == .front ? lastBackLens : .front)
    }

    func select(mode: RawMode) {
        rawMode = mode
        sessionQueue.async { self.applyRawMode(mode) }
    }

    /// Cada cena ajusta a câmera para o que ela pede.
    func select(captureMode mode: CaptureMode) {
        guard mode != captureMode else { return }
        if sceneTookOver {
            manualExposure = false
            manualFocus = false
            sceneTookOver = false
        }
        captureMode = mode
        dlog("Modo: \(mode.rawValue)")
        switch mode {
        case .moon:
            let tele = availableLenses.contains(.tele8x) ? Lens.tele8x : (availableLenses.contains(.tele) ? .tele : .wide2x)
            select(lens: tele)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { self.applyScene(iso: 50, shutter: 1.0 / 500) }
        case .portrait:
            if lens != .front { select(lens: availableLenses.contains(.wide2x) ? .wide2x : .wide) }
            look = .retrato
        case .stars:
            select(lens: .wide)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { self.applyScene(iso: 2000, shutter: 10) }
        default:
            break
        }
    }

    /// Foco no infinito + exposição manual (o obturador fica no mais próximo que a lente aceita).
    private func applyScene(iso: Float, shutter: Double) {
        sceneTookOver = true
        manualFocus = true
        lensPosition = 1
        isoIndex = Double(Self.nearestIndex(of: iso, in: isoStops))
        shutterIndex = Double(Self.nearestIndex(of: Float(shutter), in: shutterStops.map { Float($0) }))
        manualExposure = true
        dlog("Cena ajustou: ISO \(Int(selectedISO)), \(String(format: "%.4f", selectedShutter)) s, foco 1.0")
    }

    func cycleAspect() {
        let all = AspectRatio.allCases
        aspect = all[(all.firstIndex(of: aspect)! + 1) % all.count]
    }

    private func setupSession(lens: Lens, mode: RawMode) {
        session.beginConfiguration()
        session.sessionPreset = .photo
        session.inputs.forEach { session.removeInput($0) }

        guard let dev = AVCaptureDevice.default(lens.deviceType, for: .video, position: lens.position)
                ?? AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: dev),
              session.canAddInput(input) else {
            session.commitConfiguration()
            post("Não foi possível abrir a câmera.")
            dlog("❌ Não abriu a câmera \(lens.rawValue)")
            return
        }
        session.addInput(input)
        if !session.outputs.contains(photoOutput), session.canAddOutput(photoOutput) {
            session.addOutput(photoOutput)
        }
        if !session.outputs.contains(videoOutput), session.canAddOutput(videoOutput) {
            videoOutput.alwaysDiscardsLateVideoFrames = true
            videoOutput.setSampleBufferDelegate(self, queue: videoQueue)
            session.addOutput(videoOutput)
        }
        // O app é só em retrato; o visor da câmera da frente fica espelhado, como num espelho
        if let connection = videoOutput.connection(with: .video) {
            if connection.isVideoRotationAngleSupported(90) { connection.videoRotationAngle = 90 }
            if connection.isVideoMirroringSupported {
                connection.automaticallyAdjustsVideoMirroring = false
                connection.isVideoMirrored = dev.position == .front
            }
        }
        if #available(iOS 18.0, *) { installCameraControls(for: dev) }
        session.commitConfiguration()

        device = dev
        rotationCoordinator = AVCaptureDevice.RotationCoordinator(device: dev, previewLayer: nil)
        applyRawMode(mode)
        let dims = CMVideoFormatDescriptionGetDimensions(dev.activeFormat.formatDescription)
        let aspect = Double(min(dims.width, dims.height)) / Double(max(dims.width, dims.height))
        let halfLong = Double(dev.activeFormat.videoFieldOfView) * .pi / 360
        shortSideFOV = 2 * atan(tan(halfLong) * aspect)
        dlog("Câmera aberta: \(dev.localizedName) (\(lens.rawValue)) · vídeo \(dims.width)×\(dims.height) · ProRAW \(photoOutput.isAppleProRAWSupported ? "sim" : "não") · RAW: \(photoOutput.availableRawPhotoPixelFormatTypes.count) formato(s)")

        let format = dev.activeFormat
        let isos = Self.allISO.filter { $0 >= format.minISO && $0 <= format.maxISO }
        let shutters = Self.allShutter.filter {
            $0 >= format.minExposureDuration.seconds && $0 <= format.maxExposureDuration.seconds
        }
        DispatchQueue.main.async {
            let oldISO = self.isoStops.isEmpty ? 100 : self.selectedISO
            let oldShutter = self.shutterStops.isEmpty ? 1.0 / 60 : self.selectedShutter
            self.isoStops = isos.isEmpty ? [format.minISO] : isos
            self.shutterStops = shutters.isEmpty ? [format.minExposureDuration.seconds] : shutters
            self.isoIndex = Double(Self.nearestIndex(of: oldISO, in: self.isoStops))
            self.shutterIndex = Double(Self.nearestIndex(of: Float(oldShutter), in: self.shutterStops.map { Float($0) }))
        }
    }

    private func applyRawMode(_ mode: RawMode) {
        session.beginConfiguration()
        let proSupported = photoOutput.isAppleProRAWSupported
        photoOutput.isAppleProRAWEnabled = proSupported && mode == .proRAW
        photoOutput.maxPhotoQualityPrioritization = .quality
        if let dims = device?.activeFormat.supportedMaxPhotoDimensions.max(by: { $0.pixels < $1.pixels }) {
            photoOutput.maxPhotoDimensions = dims
        }
        session.commitConfiguration()
        DispatchQueue.main.async { self.proRAWSupported = proSupported }
    }

    private static func nearestIndex(of value: Float, in list: [Float]) -> Int {
        let target = log2(max(value, 1e-6))
        func distance(_ i: Int) -> Float { abs(log2(max(list[i], 1e-6)) - target) }
        return list.indices.min(by: { distance($0) < distance($1) }) ?? 0
    }

    // MARK: - Controles manuais

    private func updateExposure() {
        guard !isoStops.isEmpty, !shutterStops.isEmpty else { return }
        let manual = manualExposure
        let iso = selectedISO
        let shutter = selectedShutter
        let bias = evBias
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            let f = d.activeFormat
            if manual, d.isExposureModeSupported(.custom) {
                let seconds = min(max(shutter, f.minExposureDuration.seconds), f.maxExposureDuration.seconds)
                let duration = CMTime(seconds: seconds, preferredTimescale: 1_000_000_000)
                d.setExposureModeCustom(duration: duration, iso: min(max(iso, f.minISO), f.maxISO), completionHandler: nil)
            } else if d.isExposureModeSupported(.continuousAutoExposure) {
                d.exposureMode = .continuousAutoExposure
                d.setExposureTargetBias(min(max(bias, d.minExposureTargetBias), d.maxExposureTargetBias), completionHandler: nil)
            }
        }
    }

    private func updateWhiteBalance() {
        let manual = manualWB
        let kelvin = self.kelvin
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if manual, d.isLockingWhiteBalanceWithCustomDeviceGainsSupported {
                var gains = d.deviceWhiteBalanceGains(for: .init(temperature: kelvin, tint: 0))
                let maxGain = d.maxWhiteBalanceGain
                gains.redGain = min(max(gains.redGain, 1), maxGain)
                gains.greenGain = min(max(gains.greenGain, 1), maxGain)
                gains.blueGain = min(max(gains.blueGain, 1), maxGain)
                d.setWhiteBalanceModeLocked(with: gains, completionHandler: nil)
            } else if d.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
                d.whiteBalanceMode = .continuousAutoWhiteBalance
            }
        }
    }

    private func updateFocus() {
        let manual = manualFocus
        let position = lensPosition
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if manual, d.isLockingFocusWithCustomLensPositionSupported {
                d.setFocusModeLocked(lensPosition: min(max(position, 0), 1), completionHandler: nil)
            } else if d.isFocusModeSupported(.continuousAutoFocus) {
                d.focusMode = .continuousAutoFocus
            }
        }
    }

    private func startReadout() {
        readoutTimer?.invalidate()
        readoutTimer = Timer.scheduledTimer(withTimeInterval: 0.25, repeats: true) { [weak self] _ in
            guard let self, let d = self.device else { return }
            self.readoutISO = d.iso
            self.readoutShutter = d.exposureDuration.seconds
            self.readoutLensPosition = d.lensPosition
        }
    }

    /// Toque no visor: foca e mede a luz naquele ponto. `point` vai de 0 a 1 nos dois eixos.
    func focus(at point: CGPoint) {
        focusPoint = point
        // O visor mostra o centro ampliado pelo zoom digital
        let zoom = lens.zoom
        let sensorPoint = CGPoint(x: 0.5 + (point.x - 0.5) / zoom, y: 0.5 + (point.y - 0.5) / zoom)
        // Sensor fica deitado: girar 90° do retrato para as coordenadas da câmera (na da frente o visor é espelhado)
        let devicePoint = lens == .front
            ? CGPoint(x: sensorPoint.y, y: sensorPoint.x)
            : CGPoint(x: sensorPoint.y, y: 1 - sensorPoint.x)
        let manualFocus = self.manualFocus
        let manualExposure = self.manualExposure
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if !manualFocus, d.isFocusPointOfInterestSupported, d.isFocusModeSupported(.autoFocus) {
                d.focusPointOfInterest = devicePoint
                d.focusMode = .autoFocus
            }
            if !manualExposure, d.isExposurePointOfInterestSupported, d.isExposureModeSupported(.continuousAutoExposure) {
                d.exposurePointOfInterest = devicePoint
                d.exposureMode = .continuousAutoExposure
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
            if self.focusPoint == point { self.focusPoint = nil }
        }
    }

    func cycleTimer() {
        timerSeconds = timerSeconds == 0 ? 3 : (timerSeconds == 3 ? 10 : 0)
    }

    /// Botão do app, volume ou Controle da Câmera.
    func shutter() {
        guard countdown == 0, stackProgress == nil else { return }
        guard timerSeconds > 0 else { return capture() }
        countdown = timerSeconds
        tick()
    }

    private func tick() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            guard self.countdown > 0 else { return }
            self.countdown -= 1
            if self.countdown == 0 { self.capture() } else {
                UIImpactFeedbackGenerator(style: .light).impactOccurred()
                self.tick()
            }
        }
    }

    // MARK: - Captura

    private func capture() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        processing += 1
        flash = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.12) { self.flash = false }

        let options = developOptions
        let mode = captureMode
        let t0 = CFAbsoluteTimeGetCurrent()
        dlog("📸 \(mode.rawValue) · \(lens.rawValue) · \(rawMode.rawValue) · look \(look.rawValue) · \(aspect.rawValue) · " +
             (manualExposure ? "ISO \(Int(selectedISO)) \(String(format: "%.4f", selectedShutter))s" : "auto ISO \(Int(readoutISO)) \(String(format: "%.4f", readoutShutter))s"))
        guard mode.frameCount > 1 else {
            let flash = mode == .flash
            sessionQueue.async {
                self.captureRAW(forStack: false, flash: flash) { result in
                    dlog("RAW recebido: \(Diagnostics.ms(since: t0))")
                    self.process(result.map { [$0] }, mode: mode, options: options, started: t0)
                }
            }
            return
        }

        // Sequência: no foco empilhado, cada quadro com o foco um pouco mais longe
        let count = mode.frameCount
        let center = manualFocus ? lensPosition : readoutLensPosition
        let span: Float = lens == .macro ? 0.1 : 0.16
        let positions: [Float]? = mode == .focusStack
            ? (0..<count).map { i in
                let start = max(0, center - span / 2), end = min(1, center + span / 2)
                return start + (end - start) * Float(i) / Float(count - 1)
            }
            : nil
        stackProgress = "0/\(count)"
        let nightPlan = mode == .night && !manualExposure
        sessionQueue.async {
            let run = {
                self.shootSequence(index: 0, count: count, positions: positions, frames: []) { result in
                    dlog("Sequência de \(count) fotografada: \(Diagnostics.ms(since: t0))")
                    DispatchQueue.main.async {
                        self.stackProgress = nil
                        self.updateFocus()
                        self.updateExposure()
                    }
                    self.process(result, mode: mode, options: options, started: t0)
                }
            }
            // Noite: troca o automático por 1/15 s e ISO equivalente, para cada quadro ter menos ruído
            guard nightPlan, let d = self.device, (try? d.lockForConfiguration()) != nil else { return run() }
            let f = d.activeFormat
            let current = d.exposureDuration.seconds
            let target = min(max(current, 1.0 / 15), f.maxExposureDuration.seconds)
            let iso = min(max(d.iso * Float(current / target), f.minISO), f.maxISO)
            dlog(String(format: "Noite: %.4fs ISO %.0f → %.4fs ISO %.0f", current, d.iso, target, iso))
            d.setExposureModeCustom(duration: CMTime(seconds: target, preferredTimescale: 1_000_000_000), iso: iso) { _ in
                self.sessionQueue.async { run() }
            }
            d.unlockForConfiguration()
        }
    }

    private func shootSequence(index: Int, count: Int, positions: [Float]?, frames: [CapturedFrame],
                               completion: @escaping (Result<[CapturedFrame], Error>) -> Void) {
        guard index < count else { return completion(.success(frames)) }
        let shoot = {
            self.captureRAW(forStack: true) { result in
                switch result {
                case .failure(let error):
                    completion(.failure(error))
                case .success(let data):
                    DispatchQueue.main.async { self.stackProgress = "\(index + 1)/\(count)" }
                    self.sessionQueue.async {
                        self.shootSequence(index: index + 1, count: count, positions: positions,
                                           frames: frames + [data], completion: completion)
                    }
                }
            }
        }
        guard let positions, let d = device, d.isLockingFocusWithCustomLensPositionSupported,
              (try? d.lockForConfiguration()) != nil else { return shoot() }
        // Espera a lente chegar na posição antes de fotografar
        d.setFocusModeLocked(lensPosition: positions[index]) { _ in
            self.sessionQueue.async { shoot() }
        }
        d.unlockForConfiguration()
    }

    /// Fotografa um RAW e devolve o DNG. Em sequências usa 12 MP para caber na memória.
    private func captureRAW(forStack: Bool, flash: Bool = false, completion: @escaping (Result<CapturedFrame, Error>) -> Void) {
        let mode = rawMode
        let types = photoOutput.availableRawPhotoPixelFormatTypes
        let format: OSType?
        if mode == .proRAW && photoOutput.isAppleProRAWEnabled {
            format = types.first { AVCapturePhotoOutput.isAppleProRAWPixelFormat($0) }
        } else {
            format = types.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) }
        }
        let settings: AVCapturePhotoSettings
        if let format {
            settings = AVCapturePhotoSettings(rawPixelFormatType: format)
        } else {
            // Sem RAW nesta câmera (pode acontecer na da frente): HEIC, com o nosso look por cima
            dlog("Sem \(mode.rawValue) em \(device?.localizedName ?? "?"): usando HEIC")
            settings = photoOutput.availablePhotoCodecTypes.contains(.hevc)
                ? AVCapturePhotoSettings(format: [AVVideoCodecKey: AVVideoCodecType.hevc])
                : AVCapturePhotoSettings()
            settings.photoQualityPrioritization = .quality
        }
        if let format, AVCapturePhotoOutput.isAppleProRAWPixelFormat(format), let d = device {
            let all = d.activeFormat.supportedMaxPhotoDimensions
            let target: CMVideoDimensions? = forStack
                ? all.filter { $0.pixels >= 11_000_000 }.min(by: { $0.pixels < $1.pixels })
                : all.max(by: { $0.pixels < $1.pixels })
            if let target, target.pixels <= photoOutput.maxPhotoDimensions.pixels {
                settings.maxPhotoDimensions = target
            }
        } else if format == nil, !forStack {
            settings.maxPhotoDimensions = photoOutput.maxPhotoDimensions
        }
        if flash {
            if photoOutput.supportedFlashModes.contains(.on) {
                settings.flashMode = .on
            } else {
                dlog("⚠️ Flash não disponível nesta lente/formato")
                DispatchQueue.main.async { self.message = "O flash não está disponível nesta lente." }
            }
        }
        if let angle = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture,
           let connection = photoOutput.connection(with: .video),
           connection.isVideoRotationAngleSupported(angle) {
            connection.videoRotationAngle = angle
        }

        let id = settings.uniqueID
        let delegate = RawCaptureDelegate { result in
            self.sessionQueue.async { self.inFlight[id] = nil }
            completion(result)
        }
        inFlight[id] = delegate
        photoOutput.capturePhoto(with: settings, delegate: delegate)
    }

    /// Revela (e junta, se for sequência) e salva na galeria.
    private func process(_ result: Result<[CapturedFrame], Error>, mode: CaptureMode, options: DevelopOptions,
                         started t0: CFAbsoluteTime) {
        let done: (Result<UIImage?, Error>) -> Void = { result in
            switch result {
            case .success: dlog("✅ Salvo na galeria. Total: \(Diagnostics.ms(since: t0)) · memória livre \(Diagnostics.freeMemory)")
            case .failure(let error): dlog("❌ \(error.localizedDescription)")
            }
            DispatchQueue.main.async {
                self.processing -= 1
                switch result {
                case .success(let thumb):
                    if let thumb { self.thumbnail = thumb }
                case .failure(let error):
                    self.message = error.localizedDescription
                }
            }
        }
        switch result {
        case .failure(let error):
            done(.failure(error))
        case .success(let frames):
            DispatchQueue.global(qos: .userInitiated).async {
                let output: Developer.Output?
                if let kind = mode.stackKind {
                    output = Developer.stack(frames, kind: kind, options: options)
                } else {
                    output = frames.first.flatMap { Developer.develop($0, options: options) }
                }
                // Na foto simples o DNG vai junto; nas sequências, o DNG do primeiro quadro
                let dng = frames.first.flatMap { $0.isRaw ? $0.data : nil }
                let original = frames.first.flatMap { $0.isRaw ? nil : $0.data }
                Library.save(dng: dng, developed: output?.heic ?? original) { error in
                    if let error {
                        done(.failure(error))
                    } else if output == nil {
                        done(.failure(RevelaError.developFailed))
                    } else {
                        done(.success(output?.thumbnail))
                    }
                }
            }
        }
    }

    /// Tudo que a câmera deste iPhone oferece, para o relatório.
    func describeCapabilities(completion: @escaping (String) -> Void) {
        let settings = "- Ajustes: lente \(lens.rawValue), \(rawMode.rawValue), modo \(captureMode.rawValue), look \(look.rawValue) \(Int(lookAmount * 100))% grão \(grainAmount)×, \(aspect.rawValue), " +
            "exposição \(manualExposure ? "manual ISO \(Int(selectedISO)) \(selectedShutter)s" : "auto EV \(evBias)"), " +
            "balanço \(manualWB ? "\(Int(kelvin))K" : "auto"), foco \(manualFocus ? "manual \(lensPosition)" : "auto"), " +
            "peaking \(peaking), zebra \(zebra), espelhar \(mirror)" +
            (faceDistance.map { String(format: ", rosto a %.2f m", $0) } ?? "") + "\n"
        sessionQueue.async {
            var out = settings
            out += "- Kernels de revelação: \(Developer.kernelStatus)\n"
            out += "- ProRAW suportado: \(self.photoOutput.isAppleProRAWSupported), ligado: \(self.photoOutput.isAppleProRAWEnabled)\n"
            let types = self.photoOutput.availableRawPhotoPixelFormatTypes
            out += "- Formatos RAW agora: " + types.map {
                AVCapturePhotoOutput.isAppleProRAWPixelFormat($0) ? "ProRAW" : (AVCapturePhotoOutput.isBayerRAWPixelFormat($0) ? "Bayer" : "outro")
            }.joined(separator: ", ") + "\n"
            let maxDims = self.photoOutput.maxPhotoDimensions
            out += "- Resolução máxima da foto: \(maxDims.width)×\(maxDims.height)\n"
            out += "- Flash: " + self.photoOutput.supportedFlashModes.map { $0 == .on ? "on" : ($0 == .auto ? "auto" : "off") }.joined(separator: ", ") + "\n"
            if #available(iOS 18.0, *) { out += "- Controle da Câmera: \(self.session.supportsControls ? "sim" : "não")\n" }

            var seen = Set<String>()
            for lens in Lens.allCases where seen.insert("\(lens.deviceType.rawValue)-\(lens.position.rawValue)").inserted {
                guard let d = AVCaptureDevice.default(lens.deviceType, for: .video, position: lens.position) else {
                    out += "\n### \(lens.deviceType.rawValue): não existe neste iPhone\n"
                    continue
                }
                let f = d.activeFormat
                out += "\n### \(d.localizedName)\n"
                out += "- ISO \(Int(f.minISO))–\(Int(f.maxISO)) · obturador \(String(format: "%.5f", f.minExposureDuration.seconds))–\(String(format: "%.3f", f.maxExposureDuration.seconds)) s\n"
                out += "- Abertura f/\(d.lensAperture) · campo de visão \(Int(f.videoFieldOfView))° · foco mínimo \(d.minimumFocusDistance) mm\n"
                out += "- Fotos: " + f.supportedMaxPhotoDimensions.map { "\($0.width)×\($0.height)" }.joined(separator: ", ") + "\n"
                out += "- Flash: \(d.hasFlash ? "sim" : "não") · foco manual: \(d.isLockingFocusWithCustomLensPositionSupported ? "sim" : "não")\n"
            }
            DispatchQueue.main.async { completion(out) }
        }
    }

    private func post(_ text: String) {
        DispatchQueue.main.async { self.message = text }
    }

    // MARK: - Visor

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        renderer.enqueue(CIImage(cvPixelBuffer: pixelBuffer))
        videoFrameIndex += 1
        if videoFrameIndex % 5 == 0 { detectFace(in: pixelBuffer) }
    }

    /// Acha o maior rosto e estima a distância pelo tamanho dele (um rosto tem uns 16 cm de largura).
    private func detectFace(in pixelBuffer: CVPixelBuffer) {
        let request = VNDetectFaceRectanglesRequest()
        guard (try? VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up).perform([request])) != nil else { return }
        let face = request.results?.max(by: { $0.boundingBox.width < $1.boundingBox.width })
        guard let box = face?.boundingBox, box.width > 0.02 else {
            facelessFrames += 1
            if facelessFrames == 3 {
                DispatchQueue.main.async {
                    self.faceRect = nil
                    self.faceDistance = nil
                }
            }
            return
        }
        facelessFrames = 0
        let distance = 0.16 / (2 * tan(shortSideFOV / 2) * Double(box.width))
        // Vision usa origem embaixo; o visor, em cima
        let rect = CGRect(x: box.minX, y: 1 - box.maxY, width: box.width, height: box.height)
        DispatchQueue.main.async {
            self.faceRect = rect
            self.faceDistance = self.faceDistance.map { $0 * 0.6 + distance * 0.4 } ?? distance
            self.focusOnFaceIfNeeded(rect)
        }
    }

    /// No Retrato, mantém o foco e a luz no rosto.
    private func focusOnFaceIfNeeded(_ rect: CGRect) {
        guard captureMode == .portrait, !manualFocus, Date().timeIntervalSince(lastFaceFocus) > 1 else { return }
        lastFaceFocus = Date()
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let devicePoint = lens == .front ? CGPoint(x: center.y, y: center.x) : CGPoint(x: center.y, y: 1 - center.x)
        let manualExposure = self.manualExposure
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if d.isFocusPointOfInterestSupported, d.isFocusModeSupported(.continuousAutoFocus) {
                d.focusPointOfInterest = devicePoint
                d.focusMode = .continuousAutoFocus
            }
            if !manualExposure, d.isExposurePointOfInterestSupported, d.isExposureModeSupported(.continuousAutoExposure) {
                d.exposurePointOfInterest = devicePoint
                d.exposureMode = .continuousAutoExposure
            }
        }
    }

    /// Conselho de distância para o rosto não sair deformado.
    var distanceAdvice: (text: String, good: Bool)? {
        guard let d = faceDistance, lens != .macro else { return nil }
        let meters = String(format: "%.1f m", d)
        if captureMode == .portrait && lens != .front {
            if d < 0.9 { return ("Rosto a \(meters): muito perto, dê um passo para trás", false) }
            if d < 1.3 { return ("Rosto a \(meters): mais meio passo para trás", false) }
            return ("Rosto a \(meters): distância boa para retrato", true)
        }
        if (lens == .wide || lens == .ultraWide) && d < 0.7 {
            return ("Rosto a \(meters): de perto a grande-angular deforma. Use RETRATO", false)
        }
        return nil
    }

    // MARK: - Controle da Câmera (iPhone 16 e 17)

    @available(iOS 18.0, *)
    private func installCameraControls(for device: AVCaptureDevice) {
        guard session.supportsControls else { return }
        session.controls.forEach { session.removeControl($0) }

        let exposure = AVCaptureSystemExposureBiasSlider(device: device)
        let looks = AVCaptureIndexPicker("Look", symbolName: "camera.filters",
                                         localizedIndexTitles: Look.allCases.map(\.rawValue))
        looks.selectedIndex = Look.allCases.firstIndex(of: look) ?? 0
        looks.setActionQueue(.main) { [weak self] index in
            guard let self, Look.allCases.indices.contains(index) else { return }
            self.look = Look.allCases[index]
        }
        let focus = AVCaptureSlider("Foco", symbolName: "camera.macro", in: 0...1)
        focus.value = lensPosition
        focus.setActionQueue(.main) { [weak self] value in
            guard let self else { return }
            self.manualFocus = true
            self.lensPosition = value
        }
        for control in [exposure, looks, focus] as [AVCaptureControl] where session.canAddControl(control) {
            session.addControl(control)
        }
    }
}

@available(iOS 18.0, *)
extension CameraModel: AVCaptureSessionControlsDelegate {
    func sessionControlsDidBecomeActive(_ session: AVCaptureSession) {}
    func sessionControlsWillEnterFullscreenAppearance(_ session: AVCaptureSession) {}
    func sessionControlsWillExitFullscreenAppearance(_ session: AVCaptureSession) {}
    func sessionControlsDidBecomeInactive(_ session: AVCaptureSession) {}
}

private extension CMVideoDimensions {
    var pixels: Int { Int(width) * Int(height) }
}

// MARK: - Recebe um RAW

final class RawCaptureDelegate: NSObject, AVCapturePhotoCaptureDelegate {
    private let completion: (Result<CapturedFrame, Error>) -> Void
    private var dng: Data?
    private var processed: Data?
    private var captureError: Error?

    init(completion: @escaping (Result<CapturedFrame, Error>) -> Void) {
        self.completion = completion
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error {
            captureError = error
            return
        }
        if photo.isRawPhoto { dng = photo.fileDataRepresentation() } else { processed = photo.fileDataRepresentation() }
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishCaptureFor resolvedSettings: AVCaptureResolvedPhotoSettings, error: Error?) {
        if let error = error ?? captureError {
            completion(.failure(error))
        } else if let dng {
            completion(.success(CapturedFrame(data: dng, isRaw: true)))
        } else if let processed {
            completion(.success(CapturedFrame(data: processed, isRaw: false)))
        } else {
            completion(.failure(RevelaError.noRawData))
        }
    }
}

enum Library {
    /// Salva como um único item na galeria: a foto revelada + o DNG original (par RAW+HEIC).
    static func save(dng: Data?, developed: Data?, completion: @escaping (Error?) -> Void) {
        guard dng != nil || developed != nil else { return completion(RevelaError.noRawData) }
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else {
                completion(RevelaError.photosDenied)
                return
            }
            PHPhotoLibrary.shared().performChanges({
                let request = PHAssetCreationRequest.forAsset()
                let rawOptions = PHAssetResourceCreationOptions()
                rawOptions.uniformTypeIdentifier = "com.adobe.raw-image"
                if let developed {
                    request.addResource(with: .photo, data: developed, options: nil)
                    if let dng { request.addResource(with: .alternatePhoto, data: dng, options: rawOptions) }
                } else if let dng {
                    request.addResource(with: .photo, data: dng, options: rawOptions)
                }
            }, completionHandler: { _, error in
                completion(error)
            })
        }
    }
}
