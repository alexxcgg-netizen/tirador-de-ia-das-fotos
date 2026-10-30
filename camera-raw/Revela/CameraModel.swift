import AVFoundation
import ImageIO
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
    case fast = "RÁPIDO"
    case action = "AÇÃO"
    case freeze = "CONGELAR"
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
        case .photo, .fast, .action, .freeze, .portrait, .flash: return 1
        case .night, .moon, .average: return 8
        case .stars: return 16
        case .focusStack: return 7
        }
    }

    /// Como juntar os quadros, quando há mais de um.
    var stackKind: Developer.StackKind? {
        switch self {
        case .photo, .fast, .action, .freeze, .portrait, .flash: return nil
        case .focusStack: return .focus
        case .night, .stars, .moon, .average: return .average
        }
    }

    var hint: String {
        switch self {
        case .photo: return ""
        case .fast: return "Disparo sem atraso em 12 MP (HEIC, ou RAW no RAW puro). Toque várias vezes ou segure para rajada."
        case .action: return "4K a 120 fps: toque grava 1 s, segure para mais. O app salva as 8 fotos mais nítidas e o vídeo."
        case .freeze: return "Obturador rapidíssimo para congelar movimento. Precisa de muita luz; segure para rajada."
        case .portrait: return "Lente 2× a 1,5–2 m: o rosto fica com as proporções que as pessoas veem. Look Portra 400."
        case .night: return "8 fotos a 1/15 s alinhadas e somadas: noite limpa, sem o processamento da Apple."
        case .stars: return "16 exposições de 1 s com foco no infinito, sem aviões nem satélites. Use tripé ou apoie o iPhone."
        case .moon: return "Lente 8×, foco no infinito e exposição para a Lua. 8 fotos somadas para mais detalhe."
        case .flash: return "Uma foto RAW com o flash."
        case .focusStack: return "7 fotos com foco do perto ao longe, juntadas no mais nítido. Apoie o iPhone."
        case .average: return "8 fotos somadas: menos ruído, ou água lisa com obturador lento."
        }
    }
}

extension CaptureMode {
    /// Segurar o botão faz rajada.
    var holdsForBurst: Bool { self == .fast || self == .freeze }
    /// Foto leve de 12 MP, priorizando velocidade.
    var usesFastFormat: Bool { self == .fast || self == .freeze }
    /// O ISO se ajusta sozinho a um obturador fixo (prioridade de obturador).
    var fixesShutter: Bool { self == .freeze || self == .action }
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
    private var previewAngleObservation: NSKeyValueObservation?
    /// Camada invisível: só serve para o iPhone dizer o ângulo certo do visor de cada câmera.
    let angleLayer = AVCaptureVideoPreviewLayer()
    /// Ângulo e espelho aplicados ao vídeo do visor (para converter toques em pontos do sensor).
    private var previewAngle: CGFloat = 90
    private var previewMirrored = false
    private var loggedBufferSize = false
    /// Look de antes do Retrato, para devolver ao sair dele.
    private var lookBeforePortrait: Look?
    private let processingQueue = DispatchQueue(label: "revela.processing", qos: .userInitiated)
    private let actionRecorder = ActionRecorder()
    /// Formato especial do sensor (120/240 fps) ligado agora.
    private var specialFormatActive = false
    /// No modo AÇÃO o visor desenha 1 de cada 2 quadros (120 fps é demais para a tela).
    private var renderEvery = 1
    private var holding = false
    private var burstTimer: Timer?
    private var shutterPriorityISO: Float = 0
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
    @Published var look: Look = .portra { didSet { optionsChanged() } }
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
    /// Guarda também o DNG na galeria (ocupa uns 50 MB por foto).
    @Published var saveDNG = false { didSet { defaults.set(saveDNG, forKey: "saveDNG") } }
    /// Frase curta que aparece no visor explicando o botão que você tocou.
    @Published var toast: String?

    // Modos rápidos
    @Published var bursting = false
    @Published var burstCount = 0
    @Published var actionRecording = false
    static let freezeSpeeds: [Double] = [1.0 / 1000, 1.0 / 2000, 1.0 / 4000, 1.0 / 8000, 1.0 / 16000]
    @Published var freezeShutter: Double = 1.0 / 4000 { didSet { startShutterPriority() } }
    /// CONGELAR com o sensor no modo de 240 fps: lê as linhas bem mais rápido (raios menos tortos), mas a foto tem ~2 MP.
    @Published var freezeMax = false { didSet { applySpecialFormat() } }
    @Published var lowLight = false
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
        saveDNG = defaults.bool(forKey: "saveDNG")
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

    func show(_ text: String) {
        toast = text
        let current = text
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.6) {
            if self.toast == current { self.toast = nil }
        }
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
        angleLayer.session = session
        availableLenses = Lens.allCases.filter {
            $0 != .front && AVCaptureDevice.default($0.deviceType, for: .video, position: $0.position) != nil
        }
        hasFront = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) != nil
        let lens = self.lens
        let mode = self.rawMode
        sessionQueue.async {
            // O delegate precisa existir antes de qualquer controle ser adicionado
            if #available(iOS 18.0, *) {
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
        if captureMode == .portrait, let previous = lookBeforePortrait {
            if look == .portra { look = previous }
            lookBeforePortrait = nil
        }
        let leavingSpecial = captureMode == .action || captureMode == .freeze
        captureMode = mode
        dlog("Modo: \(mode.rawValue)")
        if mode.fixesShutter || leavingSpecial { applySpecialFormat() }
        if mode == .fast { prepareFastCapture() }
        switch mode {
        case .moon:
            let tele = availableLenses.contains(.tele8x) ? Lens.tele8x : (availableLenses.contains(.tele) ? .tele : .wide2x)
            select(lens: tele)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { self.applyScene(iso: 50, shutter: 1.0 / 500) }
        case .portrait:
            if lens != .front { select(lens: availableLenses.contains(.wide2x) ? .wide2x : .wide) }
            lookBeforePortrait = look
            look = .portra
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
            // Vídeo do visor no tamanho da tela em vez de 12 MP (onde o iOS oferecer)
            if videoOutput.responds(to: Selector(("setDeliversPreviewSizedOutputBuffers:"))) {
                videoOutput.setValue(true, forKey: "deliversPreviewSizedOutputBuffers")
            }
            videoOutput.setSampleBufferDelegate(self, queue: videoQueue)
            session.addOutput(videoOutput)
        }
        // O visor da câmera da frente fica espelhado, como num espelho. O ângulo vem do RotationCoordinator, logo abaixo.
        if let connection = videoOutput.connection(with: .video) {
            if connection.isVideoRotationAngleSupported(90) { connection.videoRotationAngle = 90 }
            if connection.isVideoMirroringSupported {
                connection.automaticallyAdjustsVideoMirroring = false
                connection.isVideoMirrored = dev.position == .front
            }
            previewAngle = 90
            previewMirrored = connection.isVideoMirrored
        }
        if #available(iOS 18.0, *) { installCameraControls(for: dev) }
        session.commitConfiguration()

        device = dev
        loggedBufferSize = false
        // Cada câmera é montada num ângulo; o coordinator, com a camada do visor, diz o ângulo certo
        DispatchQueue.main.async { self.makeRotationCoordinator(for: dev) }
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

    private func makeRotationCoordinator(for dev: AVCaptureDevice) {
        let coordinator = AVCaptureDevice.RotationCoordinator(device: dev, previewLayer: angleLayer)
        rotationCoordinator = coordinator
        previewAngleObservation = coordinator.observe(\.videoRotationAngleForHorizonLevelPreview, options: [.initial, .new]) {
            [weak self] coordinator, _ in
            let angle = coordinator.videoRotationAngleForHorizonLevelPreview
            self?.sessionQueue.async { self?.applyPreviewAngle(angle, device: dev) }
        }
    }

    private func applyPreviewAngle(_ angle: CGFloat, device dev: AVCaptureDevice) {
        guard dev == device, let connection = videoOutput.connection(with: .video),
              connection.isVideoRotationAngleSupported(angle) else { return }
        if connection.videoRotationAngle != angle {
            connection.videoRotationAngle = angle
            dlog("Visor de \(dev.localizedName): girado \(Int(angle))°\(connection.isVideoMirrored ? ", espelhado" : "")")
        }
        previewAngle = angle
        previewMirrored = connection.isVideoMirrored
    }

    /// Ponto no visor (0…1, origem em cima à esquerda) -> ponto do sensor, desfazendo espelho e rotação.
    private func sensorPoint(fromView point: CGPoint) -> CGPoint {
        var p = point
        if previewMirrored { p.x = 1 - p.x }
        switch Int(previewAngle.rounded()) % 360 {
        case 0: return p
        case 180: return CGPoint(x: 1 - p.x, y: 1 - p.y)
        case 270: return CGPoint(x: 1 - p.y, y: p.x)
        default: return CGPoint(x: p.y, y: 1 - p.x)
        }
    }

    private func applyRawMode(_ mode: RawMode) {
        session.beginConfiguration()
        let proSupported = photoOutput.isAppleProRAWSupported
        photoOutput.isAppleProRAWEnabled = proSupported && mode == .proRAW
        photoOutput.maxPhotoQualityPrioritization = .quality
        // Disparo sem atraso: a câmera guarda os quadros de antes do toque e usa o do instante certo
        if photoOutput.isZeroShutterLagSupported { photoOutput.isZeroShutterLagEnabled = true }
        if photoOutput.isResponsiveCaptureSupported { photoOutput.isResponsiveCaptureEnabled = true }
        if photoOutput.isFastCapturePrioritizationSupported { photoOutput.isFastCapturePrioritizationEnabled = true }
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
            self.adjustShutterPriority()
        }
    }

    /// Toque no visor: foca e mede a luz naquele ponto. `point` vai de 0 a 1 nos dois eixos.
    func focus(at point: CGPoint) {
        focusPoint = point
        // O visor mostra o centro ampliado pelo zoom digital
        let zoom = lens.zoom
        let sensorPoint = CGPoint(x: 0.5 + (point.x - 0.5) / zoom, y: 0.5 + (point.y - 0.5) / zoom)
        let devicePoint = self.sensorPoint(fromView: sensorPoint)
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

    // MARK: - Segurar o botão: rajada e AÇÃO

    func beginHold() {
        guard !holding, countdown == 0, stackProgress == nil else { return }
        holding = true
        if captureMode == .action {
            startAction()
        } else if captureMode.holdsForBurst {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                if self.holding && !self.bursting { self.startBurst() }
            }
        }
    }

    func endHold() {
        guard holding else { return }
        holding = false
        if captureMode == .action {
            // Toque rápido: completa pelo menos 1 segundo de gravação
            let recorded = actionRecordingStarted.map { Date().timeIntervalSince($0) } ?? 0
            DispatchQueue.main.asyncAfter(deadline: .now() + max(0, 1.0 - recorded)) { self.stopAction() }
        } else if bursting {
            stopBurst()
        } else {
            shutter()
        }
    }

    func cancelHold() {
        holding = false
        if bursting { stopBurst() }
        if actionRecording { stopAction() }
    }

    private func startBurst() {
        bursting = true
        burstCount = 0
        dlog("Rajada começou (\(captureMode.rawValue))")
        UIImpactFeedbackGenerator(style: .rigid).impactOccurred()
        burstTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            self?.burstTick()
        }
    }

    private func burstTick() {
        guard bursting else { return }
        guard burstCount < 60 else { return stopBurst() }
        let options = developOptions
        let mode = captureMode
        sessionQueue.async {
            // No máximo 3 fotos esperando a câmera, para a rajada não engasgar
            guard self.inFlight.count < 3 else { return }
            DispatchQueue.main.async {
                self.burstCount += 1
                self.processing += 1
            }
            let t0 = CFAbsoluteTimeGetCurrent()
            self.captureRAW(forStack: false, fast: true) { result in
                self.process(result.map { [$0] }, mode: mode, options: options, started: t0)
            }
        }
    }

    private func stopBurst() {
        burstTimer?.invalidate()
        burstTimer = nil
        bursting = false
        dlog("Rajada: \(burstCount) fotos")
        show("\(burstCount) fotos na rajada")
    }

    private var actionRecordingStarted: Date?

    private func startAction() {
        guard !actionRecording else { return }
        actionRecording = true
        actionRecordingStarted = Date()
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        videoQueue.async { self.actionRecorder.start() }
    }

    private func stopAction() {
        guard actionRecording else { return }
        actionRecording = false
        actionRecordingStarted = nil
        processing += 1
        let options = developOptions
        let t0 = CFAbsoluteTimeGetCurrent()
        videoQueue.async {
            let duration = self.actionRecorder.duration
            self.actionRecorder.stop { url, times in
                dlog(String(format: "AÇÃO: %d quadros em %.2f s (%.0f fps)", times.count, duration,
                            duration > 0 ? Double(times.count) / duration : 0))
                guard let url, !times.isEmpty else {
                    DispatchQueue.main.async {
                        self.processing -= 1
                        self.message = "Não foi possível gravar o modo AÇÃO."
                    }
                    return
                }
                DispatchQueue.main.async { self.show("Escolhendo as fotos mais nítidas…") }
                self.processingQueue.async {
                    let frames = ActionRecorder.sharpestFrames(in: url, times: times, count: 8)
                    var thumb: UIImage?
                    let group = DispatchGroup()
                    for frame in frames {
                        guard let output = Developer.developVideoFrame(frame, options: options) else { continue }
                        thumb = output.thumbnail
                        group.enter()
                        Library.save(dng: nil, developed: output.heic, tryPair: false) { _ in group.leave() }
                    }
                    group.enter()
                    Library.saveVideo(url) { _ in group.leave() }
                    group.wait()
                    try? FileManager.default.removeItem(at: url)
                    dlog("✅ AÇÃO: \(frames.count) fotos + vídeo salvos. Total: \(Diagnostics.ms(since: t0))")
                    DispatchQueue.main.async {
                        self.processing -= 1
                        if let thumb { self.thumbnail = thumb }
                        self.show("\(frames.count) fotos nítidas + vídeo em câmera lenta salvos")
                    }
                }
            }
        }
    }

    /// Deixa a primeira foto do RÁPIDO pronta antes do toque.
    private func prepareFastCapture() {
        sessionQueue.async {
            let settings = self.photoOutput.availablePhotoCodecTypes.contains(.hevc)
                ? AVCapturePhotoSettings(format: [AVVideoCodecKey: AVVideoCodecType.hevc])
                : AVCapturePhotoSettings()
            settings.photoQualityPrioritization = .speed
            self.photoOutput.setPreparedPhotoSettingsArray([settings], completionHandler: nil)
        }
    }

    // MARK: - Formatos especiais do sensor (AÇÃO 4K 120 fps, CONGELAR 240 fps)

    private func applySpecialFormat() {
        let mode = captureMode
        let wantedRate: Double? = mode == .action ? 120 : (mode == .freeze && freezeMax ? 240 : nil)
        let lens = self.lens
        let rawMode = self.rawMode
        renderEvery = mode == .action ? 2 : 1
        sessionQueue.async {
            guard let d = self.device else { return }
            guard let rate = wantedRate else {
                if self.specialFormatActive {
                    self.specialFormatActive = false
                    self.setPreviewSized(true)
                    self.setupSession(lens: lens, mode: rawMode)
                    dlog("Sensor de volta ao formato de foto")
                }
                DispatchQueue.main.async { self.startShutterPriority() }
                return
            }
            // AÇÃO: o maior formato com 120 fps. CONGELAR máx.: o formato mais rápido (leitura mais curta)
            let candidates = d.formats.filter { f in f.videoSupportedFrameRateRanges.contains { $0.maxFrameRate >= rate } }
            func pixels(_ f: AVCaptureDevice.Format) -> Int {
                let dims = CMVideoFormatDescriptionGetDimensions(f.formatDescription)
                return Int(dims.width) * Int(dims.height)
            }
            let chosen = rate >= 240 ? candidates.min(by: { pixels($0) < pixels($1) }) : candidates.max(by: { pixels($0) < pixels($1) })
            guard let format = chosen else {
                dlog("⚠️ \(d.localizedName) não tem formato com \(Int(rate)) fps")
                DispatchQueue.main.async { self.message = "Esta lente não grava a \(Int(rate)) fps. Tente a 1×." }
                return
            }
            self.session.beginConfiguration()
            self.session.sessionPreset = .inputPriority
            self.setPreviewSized(mode != .action)
            if (try? d.lockForConfiguration()) != nil {
                d.activeFormat = format
                let duration = CMTime(value: 1, timescale: CMTimeScale(rate))
                d.activeVideoMinFrameDuration = duration
                d.activeVideoMaxFrameDuration = duration
                d.unlockForConfiguration()
            }
            self.session.commitConfiguration()
            self.specialFormatActive = true
            self.applyRawMode(rawMode)
            let dims = CMVideoFormatDescriptionGetDimensions(format.formatDescription)
            dlog("Sensor em \(dims.width)×\(dims.height) a \(Int(rate)) fps (\(mode.rawValue))")
            DispatchQueue.main.async { self.startShutterPriority() }
        }
    }

    private func setPreviewSized(_ on: Bool) {
        if videoOutput.responds(to: Selector(("setDeliversPreviewSizedOutputBuffers:"))) {
            videoOutput.setValue(on, forKey: "deliversPreviewSizedOutputBuffers")
        }
    }

    /// Obturador fixo (CONGELAR 1/4000…, AÇÃO 1/1000) e ISO calculado a partir da luz atual.
    private func startShutterPriority() {
        guard captureMode.fixesShutter, !manualExposure else {
            lowLight = false
            return
        }
        let shutter = captureMode == .action ? 1.0 / 1000 : freezeShutter
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            let f = d.activeFormat
            let seconds = min(max(shutter, f.minExposureDuration.seconds), f.maxExposureDuration.seconds)
            // Mesma quantidade de luz que o automático estava usando, com o obturador novo
            let iso = min(max(d.iso * Float(d.exposureDuration.seconds / seconds), f.minISO), f.maxISO)
            self.shutterPriorityISO = iso
            d.setExposureModeCustom(duration: CMTime(seconds: seconds, preferredTimescale: 1_000_000_000), iso: iso, completionHandler: nil)
            dlog(String(format: "Prioridade de obturador: 1/%.0f s · ISO %.0f", 1 / seconds, iso))
        }
    }

    /// A cada 1/4 s, corrige o ISO pelo brilho do visor (o obturador fica parado).
    private func adjustShutterPriority() {
        guard captureMode.fixesShutter, !manualExposure, shutterPriorityISO > 0, histogram.count == 64 else { return }
        let total = histogram.reduce(0, +)
        guard total > 0 else { return }
        let mean = histogram.enumerated().reduce(Float(0)) { $0 + Float($1.offset) / 63 * $1.element } / total
        let ratio = pow(0.42 / max(mean, 0.02), 2.2)
        guard abs(ratio - 1) > 0.08 else { return }
        let step = pow(min(max(ratio, 0.5), 2), 0.6)
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            let f = d.activeFormat
            let iso = min(max(self.shutterPriorityISO * step, f.minISO), f.maxISO)
            self.shutterPriorityISO = iso
            d.setExposureModeCustom(duration: AVCaptureDevice.currentExposureDuration, iso: iso, completionHandler: nil)
            let dark = iso >= f.maxISO * 0.95 && ratio > 1.2
            DispatchQueue.main.async { if self.lowLight != dark { self.lowLight = dark } }
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
        if mode == .action {
            // AÇÃO sem segurar: grava 1 segundo
            processing -= 1
            startAction()
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { self.stopAction() }
            return
        }
        guard mode.frameCount > 1 else {
            let flash = mode == .flash
            let fast = mode.usesFastFormat
            sessionQueue.async {
                self.captureRAW(forStack: false, flash: flash, fast: fast) { result in
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
    private func captureRAW(forStack: Bool, flash: Bool = false, fast: Bool = false,
                            completion: @escaping (Result<CapturedFrame, Error>) -> Void) {
        let mode = rawMode
        let types = photoOutput.availableRawPhotoPixelFormatTypes
        let format: OSType?
        if fast {
            // Rápido: RAW de 12 MP no RAW puro; com ProRAW, HEIC de 12 MP (o mais rápido de todos)
            format = mode == .bayer ? types.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) } : nil
        } else if mode == .proRAW && photoOutput.isAppleProRAWEnabled {
            format = types.first { AVCapturePhotoOutput.isAppleProRAWPixelFormat($0) }
        } else {
            format = types.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) }
        }
        let settings: AVCapturePhotoSettings
        if let format {
            settings = AVCapturePhotoSettings(rawPixelFormatType: format)
        } else {
            // Sem RAW nesta câmera (pode acontecer na da frente): HEIC, com o nosso look por cima
            if !fast { dlog("Sem \(mode.rawValue) em \(device?.localizedName ?? "?"): usando HEIC") }
            settings = photoOutput.availablePhotoCodecTypes.contains(.hevc)
                ? AVCapturePhotoSettings(format: [AVVideoCodecKey: AVVideoCodecType.hevc])
                : AVCapturePhotoSettings()
            settings.photoQualityPrioritization = fast ? .speed : .quality
        }
        if let format, AVCapturePhotoOutput.isAppleProRAWPixelFormat(format), let d = device {
            let all = d.activeFormat.supportedMaxPhotoDimensions
            let target: CMVideoDimensions? = forStack
                ? all.filter { $0.pixels >= 11_000_000 }.min(by: { $0.pixels < $1.pixels })
                : all.max(by: { $0.pixels < $1.pixels })
            if let target, target.pixels <= photoOutput.maxPhotoDimensions.pixels {
                settings.maxPhotoDimensions = target
            }
        } else if format == nil, fast, let d = device {
            let twelve = d.activeFormat.supportedMaxPhotoDimensions
                .filter { $0.pixels >= 11_000_000 && $0.pixels <= photoOutput.maxPhotoDimensions.pixels }
                .min(by: { $0.pixels < $1.pixels })
            settings.maxPhotoDimensions = twelve ?? photoOutput.maxPhotoDimensions
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
            // Uma revelação por vez: na rajada as fotos entram numa fila em vez de lotar a memória
            processingQueue.async {
                let output: Developer.Output?
                if let kind = mode.stackKind {
                    output = Developer.stack(frames, kind: kind, removeOutliers: mode == .stars, options: options)
                } else {
                    output = frames.first.flatMap { Developer.develop($0, options: options) }
                }
                // Na foto simples o DNG vai junto; nas sequências, o DNG do primeiro quadro
                let dng = frames.first.flatMap { $0.isRaw ? $0.data : nil }
                let original = frames.first.flatMap { $0.isRaw ? nil : $0.data }
                let keepDNG = self.saveDNG
                Library.save(dng: keepDNG ? dng : nil, developed: output?.heic ?? original,
                             tryPair: output?.sameSizeAsRaw ?? false) { error in
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
            "peaking \(peaking), zebra \(zebra), espelhar \(mirror), guardar DNG \(saveDNG), visor \(Int(previewAngle))°, " +
            "congelar 1/\(Int((1 / freezeShutter).rounded()))\(freezeMax ? " máx" : "")" +
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
        actionRecorder.append(sampleBuffer)
        let frame = CIImage(cvPixelBuffer: pixelBuffer)
        if videoFrameIndex % renderEvery == 0 { renderer.enqueue(frame) }
        if !loggedBufferSize {
            loggedBufferSize = true
            dlog("Vídeo do visor chegando em \(CVPixelBufferGetWidth(pixelBuffer))×\(CVPixelBufferGetHeight(pixelBuffer))")
        }
        videoFrameIndex += 1
        if videoFrameIndex % (8 * renderEvery) == 0 { detectFace(in: frame) }
    }

    /// Acha o maior rosto e estima a distância pelo tamanho dele (um rosto tem uns 16 cm de largura).
    private func detectFace(in frame: CIImage) {
        // Vision numa versão pequena: acha o rosto do mesmo jeito, gastando bem menos
        let scale = min(1, 480 / max(frame.extent.width, frame.extent.height))
        let small = frame.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        let request = VNDetectFaceRectanglesRequest()
        guard (try? VNImageRequestHandler(ciImage: small, orientation: .up).perform([request])) != nil else { return }
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
        let devicePoint = sensorPoint(fromView: CGPoint(x: rect.midX, y: rect.midY))
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
        // O que a foto usou de verdade (pode ser diferente do visor, por exemplo com flash)
        if let exif = photo.metadata[kCGImagePropertyExifDictionary as String] as? [String: Any] {
            let iso = (exif[kCGImagePropertyExifISOSpeedRatings as String] as? [NSNumber])?.first?.intValue ?? 0
            let time = (exif[kCGImagePropertyExifExposureTime as String] as? NSNumber)?.doubleValue ?? 0
            let flash = (exif[kCGImagePropertyExifFlash as String] as? NSNumber)?.intValue ?? 0
            let fired = flash & 1 == 1 ? "disparou" : "não disparou"
            dlog("Foto real: ISO \(iso) · " + String(format: "%.4f", time) + " s · flash \(fired)")
        }
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
    static func saveVideo(_ url: URL, completion: @escaping (Error?) -> Void) {
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else { return completion(RevelaError.photosDenied) }
            PHPhotoLibrary.shared().performChanges({
                PHAssetCreationRequest.forAsset().addResource(with: .video, fileURL: url, options: nil)
            }, completionHandler: { _, error in completion(error) })
        }
    }

    /// Salva a foto revelada; com o DNG, tenta juntar os dois num item só (par RAW+HEIC).
    /// Se a galeria já recusou o par antes, salva separado direto.
    static func save(dng: Data?, developed: Data?, tryPair: Bool, completion: @escaping (Error?) -> Void) {
        guard dng != nil || developed != nil else { return completion(RevelaError.noRawData) }
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else {
                completion(RevelaError.photosDenied)
                return
            }
            let rawOptions = PHAssetResourceCreationOptions()
            rawOptions.uniformTypeIdentifier = "com.adobe.raw-image"
            let pairRefused = UserDefaults.standard.bool(forKey: "pairRefused")

            func saveSeparately() {
                PHPhotoLibrary.shared().performChanges({
                    if let developed { PHAssetCreationRequest.forAsset().addResource(with: .photo, data: developed, options: nil) }
                    if let dng { PHAssetCreationRequest.forAsset().addResource(with: .photo, data: dng, options: rawOptions) }
                }, completionHandler: { _, error in completion(error) })
            }

            guard let developed, let dng, tryPair, !pairRefused else { return saveSeparately() }
            PHPhotoLibrary.shared().performChanges({
                let request = PHAssetCreationRequest.forAsset()
                request.addResource(with: .photo, data: developed, options: nil)
                request.addResource(with: .alternatePhoto, data: dng, options: rawOptions)
            }, completionHandler: { _, error in
                guard let error else { return completion(nil) }
                // A galeria recusou o par: não tenta mais e salva os dois separados
                dlog("Par HEIC+DNG recusado (\(error.localizedDescription)); daqui em diante salvo separado")
                UserDefaults.standard.set(true, forKey: "pairRefused")
                saveSeparately()
            })
        }
    }
}
