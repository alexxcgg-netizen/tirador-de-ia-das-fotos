import AVFoundation
import CoreLocation
import CoreMotion
import ImageIO
import Photos
import UIKit
import Vision

enum RawMode: String, CaseIterable, Identifiable {
    case proRAW = "ProRAW"
    case bayer = "RAW puro"

    var id: String { rawValue }
}

/// As câmeras físicas. O zoom (0,5× a 25×) escolhe uma delas e recorta o centro do sensor de 48 MP.
enum Lens: String, CaseIterable, Identifiable {
    case macro = "Macro"
    case ultraWide = "0.5×"
    case wide = "1×"
    case tele = "4×"
    case front = "Frente"

    var id: String { rawValue }

    var deviceType: AVCaptureDevice.DeviceType {
        switch self {
        case .macro, .ultraWide: return .builtInUltraWideCamera
        case .wide, .front: return .builtInWideAngleCamera
        case .tele: return .builtInTelephotoCamera
        }
    }

    var position: AVCaptureDevice.Position { self == .front ? .front : .back }

    /// Mesma câmera física (troca só o recorte, sem reabrir a sessão).
    func sameCamera(as other: Lens) -> Bool { deviceType == other.deviceType && position == other.position }

    /// Zoom desta câmera sem recorte, em relação à 1×.
    var baseZoom: CGFloat {
        switch self {
        case .macro, .ultraWide: return 0.5
        case .wide, .front: return 1
        case .tele: return 4
        }
    }
}

/// Tempo de cada foto no modo NOITE.
enum NightTime: String, CaseIterable, Identifiable {
    case auto = "Auto"
    case s15 = "1/15"
    case s4 = "1/4"
    case s2 = "1/2"
    case s1 = "1 s"

    var id: String { rawValue }

    var seconds: Double? {
        switch self {
        case .auto: return nil
        case .s15: return 1.0 / 15
        case .s4: return 1.0 / 4
        case .s2: return 1.0 / 2
        case .s1: return 1
        }
    }
}

enum CaptureMode: String, CaseIterable, Identifiable {
    case photo = "FOTO"
    case fast = "RÁPIDO"
    case action = "AÇÃO"
    case freeze = "CONGELAR"
    case portrait = "RETRATO"
    case panorama = "PANORAMA"
    case video = "VÍDEO"
    case cinematic = "CINEMÁTICO"
    case dual = "DUPLA"
    case scan = "3D"
    case document = "DOC"
    case hdr = "HDR"
    case longExposure = "LONGA"
    case superRes = "SUPER RES"
    case superZoom = "SUPER ZOOM"
    case night = "NOITE"
    case stars = "ESTRELAS"
    case moon = "LUA"
    case flash = "FLASH"
    case focusStack = "FOCO EMPILHADO"
    case average = "MÉDIA"

    var id: String { rawValue }

    /// Ícone na telinha de modos.
    var symbol: String {
        switch self {
        case .photo: return "camera"
        case .fast: return "bolt"
        case .action: return "figure.run"
        case .freeze: return "stopwatch"
        case .portrait: return "person.crop.circle"
        case .panorama: return "pano"
        case .video: return "video"
        case .cinematic: return "film"
        case .dual: return "rectangle.on.rectangle"
        case .scan: return "cube.transparent"
        case .document: return "doc.viewfinder"
        case .hdr: return "circle.lefthalf.filled"
        case .longExposure: return "timer"
        case .superRes: return "square.grid.3x3"
        case .superZoom: return "plus.magnifyingglass"
        case .night: return "moon.stars"
        case .stars: return "sparkles"
        case .moon: return "moon"
        case .flash: return "bolt.circle"
        case .focusStack: return "square.stack.3d.down.right"
        case .average: return "square.stack.3d.up"
        }
    }

    var frameCount: Int {
        switch self {
        case .photo, .fast, .action, .freeze, .portrait, .hdr, .flash, .longExposure, .video, .cinematic, .dual, .scan,
             .document, .panorama: return 1
        case .superRes: return 8
        case .superZoom: return 16
        case .night, .average: return 8
        case .moon: return 5
        case .stars: return 16
        case .focusStack: return 7
        }
    }

    /// Como juntar os quadros, quando há mais de um.
    var stackKind: Developer.StackKind? {
        switch self {
        case .photo, .fast, .action, .freeze, .portrait, .hdr, .flash, .longExposure, .superRes, .superZoom, .video, .cinematic,
             .dual, .scan, .document, .panorama: return nil
        case .focusStack: return .focus
        case .night, .stars, .average: return .average
        case .moon: return nil
        }
    }

    var hint: String {
        switch self {
        case .photo: return ""
        case .fast: return "Disparo sem atraso em 12 MP (HEIC, ou RAW no RAW puro). Toque várias vezes ou segure para rajada."
        case .action: return "4K a 120 fps: toque grava 1 s, segure para mais. O app salva as 8 fotos mais nítidas e o vídeo."
        case .freeze: return "Obturador rapidíssimo para congelar movimento. Precisa de muita luz; segure para rajada."
        case .portrait: return "2× a 1,5–2 m, fundo desfocado pela profundidade (LiDAR). Escolha o quanto borra acima."
        case .video: return "Vídeo 1080p com o look gravado junto. Toque para começar e parar."
        case .cinematic: return "Vídeo com o fundo desfocado, como o Modo Cinema do iPhone. O foco segue as pessoas; dá para mudar depois no app Fotos."
        case .dual: return "Câmera de trás e da frente juntas. Toque: foto. Segure: vídeo enquanto segura."
        case .scan: return "Scanner 3D com LiDAR."
        case .document: return "Documentos de várias páginas, sem marca d'água, num PDF só."
        case .panorama: return "Toque e gire o iPhone devagar para a direita, sem subir nem descer. Toque de novo para terminar."
        case .hdr: return "3 fotos RAW (escura, normal, clara) juntadas: céu com cor e sombra com detalhe. Segure firme."
        case .longExposure: return "Junta segundos de vídeo numa foto: Seda deixa água e nuvens lisas, Rastros desenha as luzes. Funciona na mão (o app alinha cada quadro); apoiado fica ainda mais nítido."
        case .superRes: return "8 fotos de 48 MP (fica com as 6 mais nítidas), alinhadas por região em fração de pixel: até 100 MP com mais detalhe real. Segure firme; leva uns segundos."
        case .superZoom: return "Zoom de 8× a 25× na mão: 16 fotos rápidas e sem tremido (fica com as 10 mais nítidas), alinhadas e desconvoluídas."
        case .night: return "Fotos alinhadas em fração de pixel e somadas sem fantasma, mais uma curta para os postes não estourarem. Apoiado no escuro: 1 s por foto. ✦ põe estrela nas luzes."
        case .stars: return "16 exposições de 1 s com foco no infinito, sem aviões nem satélites. Use tripé ou apoie o iPhone."
        case .moon: return "Zoom 8×, foco no infinito e exposição para a Lua. 5 fotos de 48 MP juntadas no sub-pixel: mais detalhe nas crateras."
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

final class CameraModel: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate,
                         AVCaptureAudioDataOutputSampleBufferDelegate, AVCaptureFileOutputRecordingDelegate,
                         AVCaptureDepthDataOutputDelegate {
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
    /// Fotos de um quadro só e leves (12 MP): revelam aqui e não esperam uma NOITE ou SUPER ZOOM na frente
    private let quickQueue = DispatchQueue(label: "revela.quick", qos: .userInitiated)
    private let actionRecorder = ActionRecorder()
    /// Formato especial do sensor (120/240 fps) ligado agora.
    private var specialFormatActive = false
    /// No modo AÇÃO o visor desenha 1 de cada 2 quadros (120 fps é demais para a tela).
    private var renderEvery = 1
    private var holding = false
    private var burstTimer: Timer?
    private var shutterPriorityISO: Float = 0
    private var inFlight: [Int64: NSObject] = [:]
    /// Lado da sessão: Retrato pede a câmera com profundidade; HDR desliga o ProRAW (bracketing é com RAW puro).
    private var depthWanted = false
    /// O modo anterior trocou o formato do sensor: depois de reabrir, o tamanho da foto é refeito.
    private var formatWasSpecial = false
    /// SUPER ZOOM ligado (lido na fila da sessão, para estabilizar o visor).
    private var superZoomWanted = false
    private var hdrWanted = false
    private var lastBackZoom: CGFloat = 1
    private let personRequest: VNGeneratePersonSegmentationRequest = {
        let request = VNGeneratePersonSegmentationRequest()
        request.qualityLevel = .balanced
        request.outputPixelFormat = kCVPixelFormatType_OneComponent8
        return request
    }()
    /// Lido na fila de vídeo: o Retrato precisa da máscara de pessoa para o visor.
    private var portraitPreviewOn = false
    private let motion = CMMotionManager()
    private var recentRotation: [Double] = []
    private let longExposure = LongExposure()
    // Vídeo
    private let movieOutput = AVCaptureMovieFileOutput()
    private let audioOutput = AVCaptureAudioDataOutput()
    private var audioInput: AVCaptureDeviceInput?
    private let recorder = VideoRecorder()
    private let dual = DualCamera()
    private let dualLock = NSLock()
    private var latestDualFrame: CIImage?
    /// Lado da sessão: modo de vídeo comum, modo cinema (fundo desfocado) e câmera dupla.
    private var videoWanted = false
    private var cinematicWanted = false
    /// Com o modo cinema ligado o iPhone não deixa mexer no foco (fecharia o app).
    private var cinematicActive = false
    private var dualActive = false
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
    /// A câmera que está de fato entregando os quadros (muda só quando a troca termina).
    @Published private(set) var activeLens: Lens = .wide
    /// Só a última lente pedida abre: toques rápidos em sequência não enfileiram várias trocas.
    private let lensRequestLock = NSLock()
    private var lensRequest = 0
    @Published var hasFront = false
    @Published var lens: Lens = .wide
    /// Zoom em relação à 1× (0,5× a 25×). A pinça e os botões mexem aqui.
    @Published private(set) var zoom: CGFloat = 1
    /// Retrato: abertura simulada (f/1.4 borra muito, f/16 quase nada).
    static let apertures: [Float] = [1.4, 2, 2.8, 4, 8, 16]
    /// f/4 de começo: desfoque bonito sem "recortado" (f/1,4 continua a um toque).
    @Published var portraitAperture: Float = 4 { didSet { updatePortraitPreview() } }
    /// Retrato: o que você tocou no visor fica nítido (no lugar do rosto). Coordenadas do visor.
    private var portraitTap: CGPoint?

    /// O que fica nítido no Retrato, no visor: o ponto tocado, senão o centro do rosto.
    private var portraitChoice: CGPoint? {
        if let portraitTap { return portraitTap }
        guard let face = faceRect else { return nil }
        return CGPoint(x: face.midX, y: face.midY)
    }

    /// Ponto do visor -> ponto da foto inteira (o visor mostra o centro ampliado pelo recorte).
    private func photoPoint(fromView point: CGPoint?) -> CGPoint? {
        guard let point else { return nil }
        let c: CGFloat = crop
        let x: CGFloat = 0.5 + (point.x - 0.5) / c
        let y: CGFloat = 0.5 + (point.y - 0.5) / c
        return CGPoint(x: x, y: y)
    }
    @Published var nightTime: NightTime = .auto
    static let longSeconds: [Double] = [1, 2, 4, 8]
    @Published var longSecondsChoice: Double = 2
    @Published var longStyle: LongExposure.Style = .silk
    /// Segundos que faltam na exposição longa (nil = parada).
    @Published var longRemaining: Double?
    @Published var rgbHistogram = false
    static let videoRates = [24, 30, 60]
    @Published var videoFPS = 30
    @Published var isRecordingVideo = false
    /// Scanner 3D aberto (a câmera normal fica parada, porque o ARKit usa o sensor).
    @Published var showScanner = false
    @Published var recordingStarted: Date?
    /// Modo cinema: abertura simulada e os limites que a câmera aceita.
    @Published var cinematicAperture: Float = 2.8
    @Published var cinematicRange: ClosedRange<Float> = 2...16
    /// Números que mudam o tempo todo: publicados à parte (ver LiveStats).
    let live = LiveStats()
    @Published var falseColor = false { didSet { renderer.options.falseColor = falseColor } }
    @Published var nightFrames = 8
    /// NOITE: raios nas luzes fortes (0 = sem; 6 ou 8 pontas).
    @Published var nightStarPoints = UserDefaults.standard.object(forKey: "nightStarPoints") as? Int ?? 6 {
        didSet { defaults.set(nightStarPoints, forKey: "nightStarPoints") }
    }
    /// iPhone parado (apoiado ou no tripé), pelo giroscópio.
    @Published var isSteady = false
    @Published var rawMode: RawMode = .proRAW
    @Published var proRAWSupported = true
    @Published private(set) var captureMode: CaptureMode = .photo
    /// Ajustes que uma cena (Lua, Estrelas) ligou sozinha e que voltam ao sair dela.
    private var sceneTookOver = false

    // Revelação
    @Published var look: Look = .portra { didSet { optionsChanged() } }
    /// Filme próprio escolhido (nil = vale o `look`).
    @Published var customLook: CustomLook? { didSet { optionsChanged() } }
    @Published var customLooks: [CustomLook] = CustomLookStore.load()
    /// Nome do look em uso, pronto ou próprio.
    var lookName: String { customLook?.name ?? look.rawValue }
    /// Pele protegida nos filmes fortes (a pele fica natural, o resto pega o look).
    @Published var skinProtection = UserDefaults.standard.object(forKey: "skinProtection") as? Bool ?? true {
        didSet {
            defaults.set(skinProtection, forKey: "skinProtection")
            renderer.options.develop = developOptions
        }
    }
    /// Cada foto sai também em mais dois looks (fotos de um quadro só).
    @Published var multiLook = UserDefaults.standard.bool(forKey: "multiLook") {
        didSet { defaults.set(multiLook, forKey: "multiLook") }
    }
    /// Os dois looks extras: "b:<nome do look pronto>" ou "c:<id do filme próprio>".
    @Published var extraLookIDs: [String] = UserDefaults.standard.stringArray(forKey: "extraLooks")
        ?? ["b:" + Look.kodachrome.rawValue, "b:" + Look.trix.rawValue] {
        didSet { defaults.set(extraLookIDs, forKey: "extraLooks") }
    }

    /// Todos os looks para escolher como extra: os próprios primeiro.
    struct LookChoice: Identifiable {
        let id: String
        let name: String
    }

    var lookChoices: [LookChoice] {
        customLooks.map { LookChoice(id: "c:" + $0.id.uuidString, name: $0.name) }
            + Look.allCases.map { LookChoice(id: "b:" + $0.rawValue, name: $0.rawValue) }
    }

    /// Escolha em uso, no mesmo formato de `lookChoices`.
    var currentLookID: String { customLook.map { "c:" + $0.id.uuidString } ?? "b:" + look.rawValue }

    func chooseLook(id: String) {
        if id.hasPrefix("c:") {
            if let custom = customLooks.first(where: { "c:" + $0.id.uuidString == id }) { customLook = custom }
        } else if let base = Look(rawValue: String(id.dropFirst(2))) {
            choose(look: base)
        }
    }

    /// Miniaturas da faixa de filmes: o que o visor mostra agora, em cada look.
    func lookThumbnails(ids: [String], maxSide: CGFloat = 120, completion: @escaping ([String: UIImage]) -> Void) {
        let base = developOptions
        var preview = renderer.options
        let pairs: [(String, Developer.PreviewOptions)] = ids.compactMap { id in
            guard let o = options(swappingLookTo: id, from: base) else { return nil }
            preview.develop = o
            return (id, preview)
        }
        renderer.snapshotQueue.async { [renderer] in
            let images = renderer.lookSnapshots(pairs.map(\.1), maxSide: maxSide)
            var out: [String: UIImage] = [:]
            for (pair, image) in zip(pairs, images) { if let image { out[pair.0] = image } }
            DispatchQueue.main.async { completion(out) }
        }
    }

    /// As opções de revelação da foto, trocando só o look.
    private func options(swappingLookTo id: String, from base: DevelopOptions) -> DevelopOptions? {
        var o = base
        if id.hasPrefix("c:") {
            guard let custom = customLooks.first(where: { "c:" + $0.id.uuidString == id }) else { return nil }
            o.custom = custom
        } else {
            guard let look = Look(rawValue: String(id.dropFirst(2))) else { return nil }
            o.custom = nil
            o.look = look
        }
        return o
    }
    @Published var lookAmount: Float = 1 { didSet { optionsChanged() } }
    @Published var grainAmount: Float = 1 { didSet { optionsChanged() } }
    @Published var aspect: AspectRatio = .r43 { didSet { optionsChanged() } }

    // Ajudas do visor
    @Published var zebra = false { didSet { renderer.options.zebra = zebra } }
    @Published var peaking = false { didSet { renderer.options.peaking = peaking } }
    @Published var loupe = false { didSet { renderer.loupe = loupe } }
    @Published var showGrid = true
    @Published var showLevel = UserDefaults.standard.object(forKey: "showLevel") as? Bool ?? true {
        didSet { defaults.set(showLevel, forKey: "showLevel") }
    }
    /// Foco e exposição travados (segurar o dedo no visor). Um toque solta.
    @Published var aeafLocked = false

    // Modos na fileira: ordem e quais aparecem
    @Published var modeOrder: [CaptureMode] = CameraModel.loadModeOrder()
    @Published var hiddenModes: Set<CaptureMode> = Set((UserDefaults.standard.stringArray(forKey: "hiddenModes") ?? [])
        .compactMap(CaptureMode.init(rawValue:)))
    var visibleModes: [CaptureMode] { modeOrder.filter { !hiddenModes.contains($0) || $0 == captureMode } }

    private static func loadModeOrder() -> [CaptureMode] {
        let saved = (UserDefaults.standard.stringArray(forKey: "modeOrder") ?? []).compactMap(CaptureMode.init(rawValue:))
        // Modos novos (de versões futuras) entram no fim
        return saved + CaptureMode.allCases.filter { !saved.contains($0) }
    }

    func saveModes() {
        defaults.set(modeOrder.map(\.rawValue), forKey: "modeOrder")
        defaults.set(hiddenModes.map(\.rawValue), forKey: "hiddenModes")
    }

    // Economia: iPhone parado e sem toque por 30 s -> visor a 15 quadros por segundo
    @Published private(set) var idle = false
    private var lastInteraction = Date()

    /// Qualquer toque na tela acorda o visor.
    func userInteracted() {
        lastInteraction = Date()
        if idle { setIdle(false) }
    }

    private func setIdle(_ on: Bool) {
        idle = on
        idleThrottle = on
        dlog(on ? "Visor em economia (metade dos quadros)" : "Visor normal")
    }

    /// Lido na fila de vídeo.
    private var idleThrottle = false

    // Estabilização do vídeo
    enum Stabilization: String, CaseIterable, Identifiable {
        case off = "Sem"
        case standard = "Normal"
        case strong = "Forte"
        var id: String { rawValue }
        var mode: AVCaptureVideoStabilizationMode {
            switch self {
            case .off: return .off
            case .standard: return .standard
            // A "aprimorada" (cinematicExtendedEnhanced) parou de entregar quadros ao trocar de lente: ficou de fora
            case .strong: return .cinematicExtended
            }
        }
    }
    @Published var stabilization: Stabilization = Stabilization(rawValue: UserDefaults.standard.string(forKey: "stabilization") ?? "") ?? .strong {
        didSet {
            defaults.set(stabilization.rawValue, forKey: "stabilization")
            sessionQueue.async { self.applyStabilization() }
        }
    }

    /// Visor a até 60 quadros por segundo nos modos de foto (cai para 30 no escuro).
    @Published var preview60 = UserDefaults.standard.bool(forKey: "preview60") {
        didSet {
            defaults.set(preview60, forKey: "preview60")
            sessionQueue.async { self.applyPreviewRate() }
        }
    }

    // Retrato: profundidade ao vivo (LiDAR / TrueDepth) para o bokeh no visor
    private let depthOutput = AVCaptureDepthDataOutput()
    private let depthQueue = DispatchQueue(label: "revela.depth", qos: .userInitiated)
    /// O iPhone já gira a profundidade para ficar em pé (senão o app gira).
    private var depthRotated = false
    private var depthMirrored = false
    private var depthFrameIndex = 0

    // Exposição para RAW (ETTR): o mais claro possível sem estourar; a revelação desconta
    @Published var ettr = UserDefaults.standard.bool(forKey: "ettr") {
        didSet {
            defaults.set(ettr, forKey: "ettr")
            if !ettr { ettrBias = 0 }
            updateExposure()
        }
    }
    /// Quanto a câmera está expondo a mais (paradas), decidido olhando as altas luzes do vídeo.
    @Published private(set) var ettrBias: Float = 0
    var ettrActive: Bool {
        ettr && !manualExposure && ![.video, .cinematic, .dual, .panorama, .action, .freeze, .longExposure].contains(captureMode)
    }
    /// Lido na fila de vídeo.
    private var ettrRunning = false

    // Macro
    /// Com a 1×, chegou perto demais para focar: troca sozinho para o macro (e volta ao afastar).
    @Published var autoMacro = UserDefaults.standard.object(forKey: "autoMacro") as? Bool ?? true {
        didSet { defaults.set(autoMacro, forKey: "autoMacro") }
    }
    /// Zoom dentro do macro: 1× (12 MP), 2× e 3× (recorte do sensor de 48 MP + super resolução).
    @Published var macroZoom: CGFloat = 1 { didSet { renderer.options.develop = developOptions } }
    static let macroZooms: [CGFloat] = [1, 2, 3]
    /// Macro empilhado: várias fotos com o foco andando um pouquinho, juntadas no mais nítido.
    @Published var macroStack = false
    /// Lanterna como luz contínua no macro (0 = desligada).
    @Published var macroLight: Float = 0 { didSet { applyTorch() } }
    static let macroLights: [Float] = [0, 0.1, 0.35, 1]
    /// O macro entrou sozinho (só nesse caso ele sai sozinho).
    private var macroIsAuto = false
    private var closeFocusTicks = 0
    private var farFocusTicks = 0
    private var lastAutoMacroSwitch = Date.distantPast
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
    var faceRect: CGRect? {
        didSet {
            if faceRect != live.face { live.face = faceRect }
            updateAdvice()
        }
    }
    var faceDistance: Double? { didSet { updateAdvice() } }

    private func updateAdvice() {
        let advice = distanceAdvice.map { LiveStats.FaceAdvice(text: $0.text, good: $0.good) }
        if advice != live.advice { live.advice = advice }
    }
    @Published var timerSeconds = 0
    @Published var countdown = 0
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

    var readoutISO: Float = 0
    var readoutShutter: Double = 0
    var readoutLensPosition: Float = 0
    @Published var processing = 0 {
        // Revelar de novo pediu para a câmera descansar enquanto a foto ainda saía: descansa agora
        didSet { if processing == 0, oldValue > 0, pauseWanted { pauseSession() } }
    }
    private var pauseWanted = false
    /// "3/7" enquanto uma sequência está sendo fotografada.
    @Published var stackProgress: String?
    @Published var message: String?
    @Published var thumbnail: UIImage?

    var selectedISO: Float { isoStops[min(max(Int(isoIndex), 0), isoStops.count - 1)] }
    var selectedShutter: Double { shutterStops[min(max(Int(shutterIndex), 0), shutterStops.count - 1)] }

    /// Recorte central do sensor da câmera atual para chegar no zoom pedido.
    /// Vale para a câmera que está entregando a imagem agora (`activeLens`): enquanto a outra lente abre,
    /// o 4× já aparece como recorte da 1×, sem esperar.
    var crop: CGFloat {
        if activeLens == .front { return lens == .front ? min(max(zoom, 1), 3) : 1 }
        if lens == .front { return 1 }
        let wanted = lens == .macro ? macroZoom : zoom
        return max(1, wanted / activeLens.baseZoom)
    }

    var minZoom: CGFloat { lens == .front ? 1 : (availableLenses.contains(.ultraWide) ? 0.5 : 1) }
    var maxZoom: CGFloat { lens == .front ? 3 : (availableLenses.contains(.tele) ? 25 : 10) }

    /// "2,7×" para mostrar no visor.
    var zoomText: String {
        let z = lens == .macro ? macroZoom : zoom
        let text = z < 10 ? String(format: "%.1f", z) : String(format: "%.0f", z)
        return text.replacingOccurrences(of: ".0", with: "").replacingOccurrences(of: ".", with: ",") + "×"
    }

    var developOptions: DevelopOptions {
        var o = DevelopOptions(look: look, custom: customLook, amount: lookAmount, grain: grainAmount, zoom: crop, aspect: aspect, mirror: mirror)
        o.skinProtection = skinProtection
        // ETTR: a câmera expôs mais claro; a revelação volta para a exposição que você escolheu
        if ettrActive { o.exposureOffset = evBias - ettrBias }
        return o
    }

    /// Pinça e botões. `settle` escolhe a melhor câmera física para esse zoom (no fim do gesto, para não piscar no meio).
    func setZoom(_ value: CGFloat, settle: Bool = true) {
        zoomRamp?.invalidate()
        zoomRamp = nil
        zoom = min(max(value, minZoom), maxZoom)
        if settle { selectBestLens(for: zoom) }
        renderer.options.develop = developOptions
    }

    /// `margin`: durante a pinça, só troca de lente depois de passar um pouco do limite (não fica trocando para lá e para cá).
    private func selectBestLens(for z: CGFloat, margin: CGFloat = 0) {
        guard lens != .front, lens != .macro || margin == 0 else { return }
        let toUltra: CGFloat = lens == .ultraWide ? 1 + margin : 1 - margin
        let toTele: CGFloat = lens == .tele ? 4 - margin * 4 : 4 + margin * 4
        let best: Lens
        if z < toUltra && availableLenses.contains(.ultraWide) { best = .ultraWide }
        else if z >= toTele && availableLenses.contains(.tele) { best = .tele }
        else { best = .wide }
        if best != lens { select(lens: best) }
    }

    /// Pinça: a lente certa já começa a abrir no meio do gesto; até ela chegar, o visor recorta a lente atual.
    func pinchZoom(_ value: CGFloat) {
        userInteracted()
        // No macro a pinça mexe no zoom do macro (1× a 3×), sem trocar de lente
        if lens == .macro {
            macroZoom = min(max(value, 1), 3)
            return
        }
        zoomRamp?.invalidate()
        zoomRamp = nil
        zoom = min(max(value, minZoom), maxZoom)
        selectBestLens(for: zoom, margin: 0.05)
        renderer.options.develop = developOptions
    }

    private var zoomRamp: Timer?

    /// Botões de zoom: a lente nova começa a abrir na hora e o visor desliza até o zoom pedido (~0,2 s).
    func animateZoom(to value: CGFloat) {
        userInteracted()
        let target = min(max(value, minZoom), maxZoom)
        if lens == .macro { select(lens: .wide) }
        zoomRamp?.invalidate()
        selectBestLens(for: target)
        let start = zoom
        guard abs(start - target) > 0.01 else { setZoom(target, settle: false); return }
        let t0 = CACurrentMediaTime()
        let duration = 0.22
        zoomRamp = Timer.scheduledTimer(withTimeInterval: 1.0 / 120, repeats: true) { [weak self] timer in
            guard let self else { timer.invalidate(); return }
            let t = min(1, (CACurrentMediaTime() - t0) / duration)
            let eased = 1 - pow(1 - t, 3)
            // Desliza em escala de "paradas" de zoom: 1→2 e 2→4 levam o mesmo tempo
            self.zoom = start * pow(target / start, CGFloat(eased))
            self.renderer.options.develop = self.developOptions
            if t >= 1 {
                timer.invalidate()
                self.zoomRamp = nil
                self.zoom = target
                self.renderer.options.develop = self.developOptions
            }
        }
    }

    override init() {
        super.init()
        Diagnostics.shared.startMonitoring()
        // O teste de modos estava no meio quando o app fechou: anota em qual modo
        if let stuck = defaults.string(forKey: "selfTestCurrent") {
            dlog("💥 Teste de modos: o app fechou no modo \(stuck)")
            defaults.removeObject(forKey: "selfTestCurrent")
        }
        if let saved = defaults.string(forKey: "look").flatMap(Look.init(rawValue:)) { look = saved }
        if let id = defaults.string(forKey: "customLook").flatMap(UUID.init(uuidString:)) {
            customLook = customLooks.first { $0.id == id }
        }
        if let saved = defaults.string(forKey: "aspect").flatMap(AspectRatio.init(rawValue:)) { aspect = saved }
        if defaults.object(forKey: "lookAmount") != nil { lookAmount = defaults.float(forKey: "lookAmount") }
        if defaults.object(forKey: "grainAmount") != nil { grainAmount = defaults.float(forKey: "grainAmount") }
        mirror = defaults.bool(forKey: "mirror")
        saveDNG = defaults.bool(forKey: "saveDNG")
        optionsChanged()
        renderer.onHistogram = { [weak self] bins, rgb in
            self?.live.histogram = bins
            self?.live.histogramRGB = rgb
        }
    }

    private func optionsChanged() {
        renderer.options.develop = developOptions
        defaults.set(look.rawValue, forKey: "look")
        defaults.set(customLook?.id.uuidString, forKey: "customLook")
        defaults.set(aspect.rawValue, forKey: "aspect")
        defaults.set(lookAmount, forKey: "lookAmount")
        defaults.set(grainAmount, forKey: "grainAmount")
        defaults.set(mirror, forKey: "mirror")
    }

    /// Escolhe um look pronto (sai do filme próprio).
    func choose(look newLook: Look) {
        customLook = nil
        look = newLook
    }

    /// Salva (ou atualiza) um filme próprio e já deixa ele escolhido.
    func saveCustomLook(_ custom: CustomLook) {
        if let i = customLooks.firstIndex(where: { $0.id == custom.id }) { customLooks[i] = custom } else { customLooks.append(custom) }
        CustomLookStore.save(customLooks)
        customLook = custom
        dlog("Filme próprio salvo: \(custom.name) (base \(custom.base))")
        syncLooksUp()
    }

    /// Filmes próprios mudaram aqui: manda para o Claude (se conectado) e lembra quais ele já tem.
    private func syncLooksUp() {
        let looks = customLooks
        Task { @MainActor in
            // Só marca como "o Claude já tem" depois que subiu de verdade (senão um filme novo pareceria apagado lá)
            if await ClaudeSync.shared.pushLooks(looks) {
                self.defaults.set(looks.map(\.id.uuidString), forKey: "syncedLookIDs")
            }
        }
    }

    /// Filmes vindos do Claude: atualiza os que existem, cria os novos e apaga os que ele apagou.
    /// Os criados aqui que o Claude ainda não tem sobem para ele.
    func applyRemoteLooks(_ remote: [CustomLook]) {
        let synced = Set(defaults.stringArray(forKey: "syncedLookIDs") ?? [])
        let remoteIDs = Set(remote.map(\.id))
        var merged: [CustomLook] = []
        var localOnly = false
        for look in customLooks where !remoteIDs.contains(look.id) {
            // Já tinha subido e sumiu de lá: o Claude apagou. Nunca subiu: é novo daqui
            if !synced.contains(look.id.uuidString) {
                merged.append(look)
                localOnly = true
            }
        }
        // Filmes de lá: mantém a LUT que só existe neste iPhone
        for var look in remote {
            if let local = customLooks.first(where: { $0.id == look.id }), look.lutFile == nil { look.lutFile = local.lutFile }
            merged.append(look)
        }
        let changed = merged != customLooks
        if changed {
            customLooks = merged
            CustomLookStore.save(merged)
            if let current = customLook { customLook = merged.first { $0.id == current.id } }
            dlog("Claude: filmes próprios atualizados (\(merged.count))")
            show("Filmes atualizados pelo Claude")
        }
        if localOnly { syncLooksUp() } else { defaults.set(merged.map(\.id.uuidString), forKey: "syncedLookIDs") }
    }

    /// Acha um filme pelo nome (pronto ou próprio) e devolve o id do jeito dos looks extras.
    private func lookID(named name: String) -> String? {
        if let custom = customLooks.first(where: { $0.name.caseInsensitiveCompare(name) == .orderedSame }) {
            return "c:" + custom.id.uuidString
        }
        if let look = Look.allCases.first(where: { $0.rawValue.caseInsensitiveCompare(name) == .orderedSame }) {
            return "b:" + look.rawValue
        }
        return nil
    }

    /// Ajustes vindos do Claude (`ajustes.json`): só as chaves presentes.
    func applyRemoteSettings(_ d: [String: Any]) {
        var applied: [String] = []
        if let name = d["look"] as? String, let id = lookID(named: name) {
            if id.hasPrefix("c:") { customLook = customLooks.first { "c:" + $0.id.uuidString == id } }
            else if let look = Look(rawValue: String(id.dropFirst(2))) { choose(look: look) }
            applied.append("look")
        }
        if let v = d["intensidade"] as? Double { lookAmount = Float(min(max(v, 0), 1)); applied.append("intensidade") }
        if let v = d["grao"] as? Double { grainAmount = Float(min(max(v, 0), 2)); applied.append("grão") }
        if let v = d["ettr"] as? Bool { ettr = v; applied.append("ETTR") }
        if let v = d["protegerPele"] as? Bool { skinProtection = v; applied.append("pele") }
        if let v = d["macroAutomatico"] as? Bool { autoMacro = v; applied.append("macro automático") }
        if let v = d["visor60"] as? Bool { preview60 = v; applied.append("visor 60") }
        if let v = d["tresLooks"] as? Bool { multiLook = v; applied.append("três looks") }
        if let names = d["looksExtras"] as? [String] {
            let ids = names.compactMap(lookID(named:))
            if !ids.isEmpty { extraLookIDs = Array(ids.prefix(2)); applied.append("looks extras") }
        }
        if let v = d["estabilizacao"] as? String, let s = Stabilization(rawValue: v) { stabilization = s; applied.append("estabilização") }
        if let v = d["nivel"] as? Bool { showLevel = v; applied.append("nível") }
        if let v = d["grade"] as? Bool { showGrid = v; applied.append("grade") }
        if let names = d["modosEscondidos"] as? [String] {
            hiddenModes = Set(names.compactMap(CaptureMode.init(rawValue:))).subtracting([.photo])
            applied.append("modos escondidos")
        }
        if let names = d["ordemDosModos"] as? [String] {
            let first = names.compactMap(CaptureMode.init(rawValue:))
            modeOrder = first + modeOrder.filter { !first.contains($0) }
            applied.append("ordem dos modos")
        }
        if applied.contains(where: { $0.hasPrefix("modos") || $0.hasPrefix("ordem") }) { saveModes() }
        guard !applied.isEmpty else { return }
        dlog("Claude: ajustes aplicados (\(applied.joined(separator: ", ")))")
        show("Ajustes atualizados pelo Claude")
    }

    /// Os ajustes de agora, para o `estado.json` que o Claude lê.
    var settingsSnapshot: [String: Any] {
        [
            "look": lookName,
            "intensidade": Double(lookAmount),
            "grao": Double(grainAmount),
            "ettr": ettr,
            "protegerPele": skinProtection,
            "macroAutomatico": autoMacro,
            "visor60": preview60,
            "tresLooks": multiLook,
            "looksExtras": extraLookIDs.map { id in
                id.hasPrefix("c:") ? (customLooks.first { "c:" + $0.id.uuidString == id }?.name ?? id) : String(id.dropFirst(2))
            },
            "estabilizacao": stabilization.rawValue,
            "nivel": showLevel,
            "grade": showGrid,
            "modosEscondidos": hiddenModes.map(\.rawValue).sorted(),
            "ordemDosModos": modeOrder.map(\.rawValue),
            "modo": captureMode.rawValue,
            "lente": lens.rawValue,
            "filmesProprios": customLooks.map(\.name),
        ]
    }

    func deleteCustomLook(_ custom: CustomLook) {
        if let file = custom.lutFile, !customLooks.contains(where: { $0.id != custom.id && $0.lutFile == file }) {
            LUTStore.delete(file)
        }
        customLooks.removeAll { $0.id == custom.id }
        CustomLookStore.save(customLooks)
        if customLook?.id == custom.id { customLook = nil }
        syncLooksUp()
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
        // Logo ao abrir o foco ainda não assentou: o macro automático espera uns segundos
        lastAutoMacroSwitch = Date()
        availableLenses = Lens.allCases.filter {
            $0 != .front && AVCaptureDevice.default($0.deviceType, for: .video, position: $0.position) != nil
        }
        hasFront = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) != nil
        let lens = self.lens
        let mode = self.rawMode
        // A primeira foto era a mais lenta (o Metal monta os filtros na primeira vez): monta agora, enquanto você enquadra
        let warmOptions = developOptions
        quickQueue.asyncAfter(deadline: .now() + 1.5) { Developer.warmUp(options: warmOptions) }
        sessionQueue.async {
            // O delegate precisa existir antes de qualquer controle ser adicionado
            if #available(iOS 18.0, *) {
                self.session.setControlsDelegate(self, queue: self.sessionQueue)
            }
            dlog("Abrindo a câmera…")
            self.setupSession(lens: lens, mode: mode)
            if !self.session.isRunning {
                dlog("Ligando a sessão…")
                self.session.startRunning()
                dlog("Sessão ligada: \(self.session.isRunning ? "rodando" : "parada")")
            }
        }
        startReadout()
        startSteadyMonitor()
    }

    /// Giroscópio: o iPhone está parado (apoiado ou no tripé)?
    private func startSteadyMonitor() {
        guard motion.isDeviceMotionAvailable, !motion.isDeviceMotionActive else { return }
        motion.deviceMotionUpdateInterval = 0.1
        motion.startDeviceMotionUpdates(to: .main) { [weak self] data, _ in
            guard let self, let r = data?.rotationRate else { return }
            self.recentRotation.append((r.x * r.x + r.y * r.y + r.z * r.z).squareRoot())
            if self.recentRotation.count > 15 { self.recentRotation.removeFirst() }
            let steady = self.recentRotation.count == 15 && (self.recentRotation.max() ?? 1) < 0.03
            if steady != self.isSteady { self.isSteady = steady }
            // Mexeu no iPhone: acorda. Parado e sem toque por 30 s (e nada acontecendo): economia
            if !steady, self.idle, (self.recentRotation.last ?? 0) > 0.08 { self.userInteracted() }
            let busy = self.isRecordingVideo || self.longRemaining != nil || self.panoramaProgress != nil
                || self.processing > 0 || self.stackProgress != nil || self.actionRecording
            if !self.idle, steady, !busy, Date().timeIntervalSince(self.lastInteraction) > 30 { self.setIdle(true) }
        }
    }

    func select(lens newLens: Lens) {
        // No meio de uma rajada ou gravação a câmera não troca (trocar ali fechava o app no CONGELAR)
        guard newLens != lens, !bursting, !actionRecording, stackProgress == nil, longRemaining == nil,
              panoramaProgress == nil, !isRecordingVideo else { return }
        let old = lens
        lens = newLens
        optionsChanged()
        if newLens == .macro {
            peaking = true
            if !manualFocus { lensPosition = 0 }
        } else if old == .macro {
            peaking = false
            macroIsAuto = false
            macroZoom = 1
            macroStack = false
            if macroLight > 0 { macroLight = 0 }
        }
        if newLens == .front {
            lastBackLens = old
            lastBackZoom = zoom
            zoom = 1
        } else if old == .front {
            zoom = lastBackZoom
        }
        if newLens != .front && newLens != .macro { lastBackLens = newLens }
        faceRect = nil
        faceDistance = nil
        // Mesma câmera física (ex.: 1× -> 2×): só muda o recorte, sem reabrir a sessão
        guard !newLens.sameCamera(as: old) else { return }
        let mode = rawMode
        lensRequestLock.lock()
        lensRequest += 1
        let request = lensRequest
        lensRequestLock.unlock()
        // A imagem não pula: fica parada e esmaece para a lente nova (borrada quando a nova mostra mais)
        let widerView = newLens == .front || old == .front || newLens.baseZoom < old.baseZoom
        renderer.beginLensTransition(blur: widerView)
        sessionQueue.async {
            self.lensRequestLock.lock()
            let stale = request != self.lensRequest
            self.lensRequestLock.unlock()
            // Já pediram outra lente depois desta: pula direto para a última
            guard !stale else { return }
            let t0 = CFAbsoluteTimeGetCurrent()
            self.setupSession(lens: newLens, mode: mode)
            dlog("Troca de lente \(old.rawValue) → \(newLens.rawValue): \(Diagnostics.ms(since: t0))")
            DispatchQueue.main.async {
                self.renderer.endLensTransition()
                self.updateExposure()
                self.updateWhiteBalance()
                self.updateFocus()
                // A câmera nova abre no formato de foto: AÇÃO e CONGELAR precisam do formato rápido de novo
                if self.captureMode.fixesShutter { self.applySpecialFormat() }
                if self.macroLight > 0 { self.applyTorch() }
            }
        }
    }

    /// Botão de virar a câmera.
    func flipCamera() {
        if lens == .front {
            select(lens: lastBackLens)
            optionsChanged()
        } else {
            select(lens: .front)
        }
    }

    func select(mode: RawMode) {
        rawMode = mode
        sessionQueue.async { self.applyRawMode(mode) }
    }

    /// Cada cena ajusta a câmera para o que ela pede.
    func select(captureMode mode: CaptureMode) {
        if mode == .scan {
            openScanner()
            return
        }
        if mode == .document {
            openDocumentScanner()
            return
        }
        guard mode != captureMode else { return }
        if panoramaProgress != nil { finishPanorama() }
        if mode == .panorama, lens != .front, crop > 1.01 { setZoom(lens.baseZoom) }
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
        let oldMode = captureMode
        captureMode = mode
        portraitTap = nil
        dlog("Modo: \(mode.rawValue)")
        // A exposição para RAW vale só nos modos de foto: liga ou desliga conforme o modo
        if ettr { updateExposure() }
        // SUPER ZOOM começa no 8× (tele) e estabiliza o visor
        if mode == .superZoom, lens != .front, zoom < 8 { animateZoom(to: 8) }
        if mode == .superZoom || oldMode == .superZoom {
            let on = mode == .superZoom
            sessionQueue.async {
                self.superZoomWanted = on
                self.applyStabilization()
            }
        }
        // Câmera dupla usa uma sessão própria
        if mode == .dual || oldMode == .dual { switchDual(on: mode == .dual) }
        if mode == .video || mode == .cinematic || mode == .dual { requestMicrophone() }

        // Retrato troca para a câmera com profundidade; HDR precisa do RAW puro; vídeo e cinema mudam o formato
        let wantsDepth = mode == .portrait, wantsHDR = mode == .hdr
        let wantsVideo = mode == .video, wantsCinematic = mode == .cinematic
        let changed = wantsDepth != (oldMode == .portrait) || wantsHDR != (oldMode == .hdr)
            || wantsVideo != (oldMode == .video) || wantsCinematic != (oldMode == .cinematic)
        if changed {
            let reopen = wantsDepth != (oldMode == .portrait) || wantsVideo != (oldMode == .video)
                || wantsCinematic != (oldMode == .cinematic)
            if wantsCinematic && lens != .front && zoom != 1 { setZoom(1) }
            let lens = self.lens, raw = rawMode
            sessionQueue.async {
                self.depthWanted = wantsDepth
                self.hdrWanted = wantsHDR
                self.videoWanted = wantsVideo
                self.cinematicWanted = wantsCinematic
                if reopen { self.setupSession(lens: lens, mode: raw) } else { self.applyRawMode(raw) }
                DispatchQueue.main.async {
                    self.updateExposure()
                    self.updateWhiteBalance()
                    self.updateFocus()
                }
            }
        }
        // Depois da reabertura (mesma fila): senão a reabertura desfazia o sensor rápido da AÇÃO e do CONGELAR
        if mode.fixesShutter || leavingSpecial { applySpecialFormat() }
        if mode == .fast { prepareFastCapture() }
        updatePortraitPreview()

        switch mode {
        case .moon:
            setZoom(8)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                // Saiu da LUA nesse meio segundo: não trava a exposição do modo novo
                guard self.captureMode == .moon else { return }
                self.applyScene(iso: 50, shutter: 1.0 / 500)
            }
        case .portrait:
            if lens != .front { setZoom(2) }
            lookBeforePortrait = look
            look = .portra
        case .hdr:
            // O bracketing mexe na exposição sozinho a partir do automático
            manualExposure = false
        case .stars:
            setZoom(1)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                guard self.captureMode == .stars else { return }
                self.applyScene(iso: 2000, shutter: 10)
            }
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

    private func updatePortraitPreview() {
        let on = captureMode == .portrait
        portraitPreviewOn = on
        renderer.portraitBlur = on ? 2.8 / portraitAperture : 0
        if !on {
            renderer.setPersonMask(nil)
            renderer.setDepth(nil, focus: 0)
        }
    }

    func cycleAspect() {
        let all = AspectRatio.allCases
        aspect = all[(all.firstIndex(of: aspect)! + 1) % all.count]
    }

    private func setupSession(lens: Lens, mode: RawMode) {
        specialFormatActive = false
        cinematicActive = false
        session.beginConfiguration()
        // Tira só a câmera; o microfone fica (tirar e pôr de novo deixa a troca mais lenta)
        session.inputs.forEach { input in
            if let d = (input as? AVCaptureDeviceInput)?.device, d.hasMediaType(.video) { session.removeInput(input) }
        }
        session.sessionPreset = cinematicWanted ? .inputPriority : (videoWanted && session.canSetSessionPreset(.hd1920x1080) ? .hd1920x1080 : .photo)

        // Retrato: a câmera que entrega profundidade (principal + LiDAR, ou a TrueDepth na frente)
        let types: [AVCaptureDevice.DeviceType]
        if cinematicWanted {
            // Modo cinema: a câmera dupla de trás (calcula profundidade) ou a TrueDepth na frente
            types = lens == .front ? [.builtInTrueDepthCamera, .builtInWideAngleCamera] : [.builtInDualWideCamera, .builtInWideAngleCamera]
        } else if depthWanted && (lens == .wide || lens == .front) {
            types = lens == .front ? [.builtInTrueDepthCamera, .builtInWideAngleCamera]
                                   : [.builtInLiDARDepthCamera, .builtInDualWideCamera, .builtInWideAngleCamera]
        } else {
            types = [lens.deviceType]
        }
        guard let dev = types.lazy.compactMap({ AVCaptureDevice.default($0, for: .video, position: lens.position) }).first
                ?? AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: dev),
              session.canAddInput(input) else {
            attempt("Salvar a configuração") { session.commitConfiguration() }
            post("Não foi possível abrir a câmera.")
            dlog("❌ Não abriu a câmera \(lens.rawValue)")
            return
        }
        session.addInput(input)
        if cinematicWanted {
            // Cinema: grava com o AVCaptureMovieFileOutput, que guarda a profundidade para editar o foco depois
            if session.outputs.contains(videoOutput) { session.removeOutput(videoOutput) }
            if session.outputs.contains(photoOutput) { session.removeOutput(photoOutput) }
            if !session.outputs.contains(movieOutput), session.canAddOutput(movieOutput) { session.addOutput(movieOutput) }
            configureCinematic(device: dev, input: input)
        } else if session.outputs.contains(movieOutput) {
            session.removeOutput(movieOutput)
        }
        // Microfone só nos modos de vídeo
        if videoWanted || cinematicWanted {
            if audioInput == nil, AVCaptureDevice.authorizationStatus(for: .audio) == .authorized,
               let mic = AVCaptureDevice.default(for: .audio), let micInput = try? AVCaptureDeviceInput(device: mic),
               session.canAddInput(micInput) {
                session.addInput(micInput)
                audioInput = micInput
            } else if let audioInput, session.canAddInput(audioInput) {
                session.addInput(audioInput)
            }
            if videoWanted, !session.outputs.contains(audioOutput), session.canAddOutput(audioOutput) {
                audioOutput.setSampleBufferDelegate(self, queue: videoQueue)
                session.addOutput(audioOutput)
            }
        } else {
            if session.outputs.contains(audioOutput) { session.removeOutput(audioOutput) }
            if let audioInput, session.inputs.contains(audioInput) { session.removeInput(audioInput) }
            audioInput = nil
        }
        if !cinematicWanted, !session.outputs.contains(photoOutput), session.canAddOutput(photoOutput) {
            session.addOutput(photoOutput)
        }
        if !cinematicWanted, !session.outputs.contains(videoOutput), session.canAddOutput(videoOutput) {
            videoOutput.alwaysDiscardsLateVideoFrames = true
            // Vídeo do visor no tamanho da tela em vez de 12 MP (onde o iOS oferecer)
            setPreviewSized(true)
            videoOutput.setSampleBufferDelegate(self, queue: videoQueue)
            session.addOutput(videoOutput)
        }
        // No VÍDEO o arquivo precisa do 1080p cheio; nos outros modos o visor basta no tamanho da tela
        if session.outputs.contains(videoOutput) { setPreviewSized(!videoWanted) }
        // O visor da câmera da frente fica espelhado, como num espelho. O ângulo vem do RotationCoordinator, logo abaixo.
        if let connection = videoOutput.connection(with: .video) {
            attempt("Girar e espelhar o visor") {
                if connection.isVideoRotationAngleSupported(90) { connection.videoRotationAngle = 90 }
                if connection.isVideoMirroringSupported {
                    connection.automaticallyAdjustsVideoMirroring = false
                    connection.isVideoMirrored = dev.position == .front
                }
            }
            previewAngle = 90
            previewMirrored = connection.isVideoMirrored
        }
        if #available(iOS 18.0, *) { attempt("Controle da Câmera") { installCameraControls(for: dev) } }
        if !(depthWanted && !cinematicWanted), session.outputs.contains(depthOutput) { session.removeOutput(depthOutput) }
        device = dev
        // RAW, profundidade e disparo rápido entram na mesma configuração: o iPhone remonta a câmera uma vez só
        if session.outputs.contains(photoOutput) {
            attempt("Configurar a foto (RAW, profundidade, disparo rápido)") { configurePhotoOutput(mode) }
        }
        dlog("Abrindo \(dev.localizedName): salvando a configuração…")
        guard attempt("Salvar a configuração", { session.commitConfiguration() }) else {
            // A câmera recusou esta combinação: volta para a foto comum em vez de ficar sem imagem
            if depthWanted || videoWanted || cinematicWanted || hdrWanted {
                depthWanted = false
                videoWanted = false
                cinematicWanted = false
                hdrWanted = false
                setupSession(lens: lens, mode: mode)
                DispatchQueue.main.async {
                    // Só força FOTO se o modo pedido ainda é um desses (você pode já ter trocado)
                    guard [.portrait, .video, .cinematic, .hdr].contains(self.captureMode) else { return }
                    self.select(captureMode: .photo)
                    self.message = "A câmera recusou esse modo agora. Voltei para FOTO; o relatório mostra o motivo."
                }
            }
            return
        }
        dlog("Configuração aceita")
        if formatWasSpecial {
            // O modo anterior (AÇÃO, CINEMÁTICO, DUPLA) mexeu no formato: o tamanho da foto é refeito agora
            formatWasSpecial = false
            applyRawMode(mode)
        }

        loggedBufferSize = false
        if videoWanted { applyVideoFrameRate() }
        applyStabilization()
        applyPreviewRate()
        if depthWanted, !cinematicWanted { configureLiveDepth(dev) }
        // Cada câmera é montada num ângulo; o coordinator, com a camada do visor, diz o ângulo certo
        DispatchQueue.main.async {
            self.activeLens = lens
            self.optionsChanged()
            self.makeRotationCoordinator(for: dev)
        }
        // Se o ProRAW só ficou disponível depois de salvar, liga agora
        if mode == .proRAW, photoOutput.isAppleProRAWSupported, !photoOutput.isAppleProRAWEnabled, !depthWanted, !hdrWanted {
            applyRawMode(mode)
        }
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
            if let connection = self?.angleLayer.connection, connection.isVideoRotationAngleSupported(angle) {
                connection.videoRotationAngle = angle
            }
            self?.sessionQueue.async { self?.applyPreviewAngle(angle, device: dev) }
        }
    }

    private func applyPreviewAngle(_ angle: CGFloat, device dev: AVCaptureDevice) {
        guard dev == device, let connection = videoOutput.connection(with: .video),
              connection.isVideoRotationAngleSupported(angle) else { return }
        if connection.videoRotationAngle != angle {
            attempt("Girar o visor") { connection.videoRotationAngle = angle }
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
        guard session.outputs.contains(photoOutput) else { return }
        session.beginConfiguration()
        defer { attempt("Salvar a foto") { session.commitConfiguration() } }
        attempt("Configurar a foto (RAW, profundidade, disparo rápido)") { configurePhotoOutput(mode) }
    }

    private func configurePhotoOutput(_ mode: RawMode) {
        let proSupported = photoOutput.isAppleProRAWSupported
        let depth = depthWanted && photoOutput.isDepthDataDeliverySupported
        // Profundidade e bracketing não combinam com ProRAW nem com o disparo sem atraso
        let special = depth || hdrWanted
        if photoOutput.isFastCapturePrioritizationSupported { photoOutput.isFastCapturePrioritizationEnabled = false }
        if photoOutput.isResponsiveCaptureSupported { photoOutput.isResponsiveCaptureEnabled = false }
        if photoOutput.isZeroShutterLagSupported { photoOutput.isZeroShutterLagEnabled = false }
        photoOutput.isAppleProRAWEnabled = proSupported && mode == .proRAW && !special
        photoOutput.maxPhotoQualityPrioritization = .quality
        if photoOutput.isDepthDataDeliverySupported { photoOutput.isDepthDataDeliveryEnabled = depth }
        if photoOutput.isPortraitEffectsMatteDeliverySupported { photoOutput.isPortraitEffectsMatteDeliveryEnabled = depth }
        // Máscaras finas de cabelo e óculos para o bokeh não borrar o contorno
        let mattes = photoOutput.availableSemanticSegmentationMatteTypes.filter { $0 == .hair || $0 == .glasses }
        photoOutput.enabledSemanticSegmentationMatteTypes = depth ? mattes : []
        if !special {
            // Disparo sem atraso: a câmera guarda os quadros de antes do toque e usa o do instante certo
            if photoOutput.isZeroShutterLagSupported { photoOutput.isZeroShutterLagEnabled = true }
            if photoOutput.isResponsiveCaptureSupported { photoOutput.isResponsiveCaptureEnabled = true }
            if photoOutput.isFastCapturePrioritizationSupported { photoOutput.isFastCapturePrioritizationEnabled = true }
        }
        if depthWanted { dlog("Retrato: \(device?.localizedName ?? "?") · profundidade \(depth ? "sim" : "não") · máscara de pessoa \(photoOutput.isPortraitEffectsMatteDeliveryEnabled ? "sim" : "não")") }
        if let dims = device?.activeFormat.supportedMaxPhotoDimensions.max(by: { $0.pixels < $1.pixels }) {
            photoOutput.maxPhotoDimensions = dims
        }
        DispatchQueue.main.async { self.proRAWSupported = proSupported }
    }

    private static func nearestIndex(of value: Float, in list: [Float]) -> Int {
        let target = log2(max(value, 1e-6))
        func distance(_ i: Int) -> Float { abs(log2(max(list[i], 1e-6)) - target) }
        return list.indices.min(by: { distance($0) < distance($1) }) ?? 0
    }

    // MARK: - Controles manuais

    private func updateExposure() {
        // Voltou para o automático (troca de lente, fim de sequência…): a trava AE/AF acabou
        aeafLocked = false
        guard !isoStops.isEmpty, !shutterStops.isEmpty else { return }
        let manual = manualExposure
        let iso = selectedISO
        let shutter = selectedShutter
        let bias = ettrActive ? ettrBias : evBias
        ettrRunning = ettrActive
        renderer.options.develop = developOptions
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            let f = d.activeFormat
            attempt("Exposição") {
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
            guard !self.cinematicActive, let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            attempt("Foco") {
                if manual, d.isLockingFocusWithCustomLensPositionSupported {
                    d.setFocusModeLocked(lensPosition: min(max(position, 0), 1), completionHandler: nil)
                } else if d.isFocusModeSupported(.continuousAutoFocus) {
                    d.focusMode = .continuousAutoFocus
                }
            }
        }
    }

    /// Macro automático: a 1× com a lente no limite de perto por quase 1 s -> macro.
    /// No macro que entrou sozinho, assunto longe de novo por 1,5 s -> volta para a 1×.
    private func checkAutoMacro(lensPosition: Float, focusMode: AVCaptureDevice.FocusMode) {
        // Depois de um toque o foco fica em .autoFocus: também vale (é justamente quando se chega perto)
        guard autoMacro, !manualFocus, !aeafLocked, focusMode != .locked, captureMode == .photo,
              Date().timeIntervalSince(lastAutoMacroSwitch) > 5, activeLens == lens else {
            closeFocusTicks = 0
            farFocusTicks = 0
            return
        }
        if lens == .wide, zoom < 1.5, availableLenses.contains(.macro) {
            // A 1× só foca a partir de 20 cm: no limite por 1,5 s seguidos = perto demais
            closeFocusTicks = lensPosition <= 0.01 ? closeFocusTicks + 1 : 0
            if closeFocusTicks >= 6 {
                closeFocusTicks = 0
                lastAutoMacroSwitch = Date()
                macroIsAuto = true
                dlog("Macro automático: ligou (1× sem conseguir focar de perto)")
                select(lens: .macro)
                macroIsAuto = true
                show("Macro automático. Afaste para voltar à 1×.")
            }
        } else if lens == .macro, macroIsAuto {
            // Volta só com o assunto bem longe (não perto dos 20 cm, onde ficava trocando) por 3 s
            farFocusTicks = lensPosition >= 0.75 ? farFocusTicks + 1 : 0
            if farFocusTicks >= 12 {
                farFocusTicks = 0
                lastAutoMacroSwitch = Date()
                dlog("Macro automático: voltou para a 1×")
                select(lens: .wide)
                setZoom(1, settle: false)
            }
        }
    }

    /// Lanterna ligada na intensidade escolhida (só no macro).
    private func applyTorch() {
        let level = lens == .macro ? macroLight : 0
        sessionQueue.async {
            guard let d = self.device, d.hasTorch, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            attempt("Luz do macro") {
                if level <= 0 {
                    if d.torchMode != .off { d.torchMode = .off }
                } else {
                    try? d.setTorchModeOn(level: min(level, AVCaptureDevice.maxAvailableTorchLevel))
                }
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
            // Só avisa a tela quando muda de verdade
            if abs(self.live.iso - d.iso) > 1 { self.live.iso = d.iso }
            if abs(self.live.shutter - d.exposureDuration.seconds) > 1e-5 { self.live.shutter = d.exposureDuration.seconds }
            self.adjustShutterPriority()
            self.checkAutoMacro(lensPosition: d.lensPosition, focusMode: d.focusMode)
        }
    }

    /// Segurar o dedo no visor: foca e mede a luz ali e trava as duas coisas até o próximo toque.
    func lockFocusExposure(at point: CGPoint) {
        focus(at: point)
        aeafLocked = true
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        dlog("Trava AE/AF")
        let manualExposure = self.manualExposure
        // Espera o foco e a exposição chegarem no ponto, depois trava
        sessionQueue.asyncAfter(deadline: .now() + 0.6) {
            guard self.aeafLocked, let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            attempt("Travar a exposição") {
                if !manualExposure, d.isExposureModeSupported(.locked) { d.exposureMode = .locked }
            }
        }
    }

    /// Toque no visor: foca e mede a luz naquele ponto. `point` vai de 0 a 1 nos dois eixos.
    func focus(at point: CGPoint) {
        userInteracted()
        aeafLocked = false
        if captureMode == .portrait {
            portraitTap = point
            show("Isto fica nítido no Retrato")
        }
        focusPoint = point
        // O visor mostra o centro ampliado pelo zoom digital
        let zoom = crop
        let sensorPoint = CGPoint(x: 0.5 + (point.x - 0.5) / zoom, y: 0.5 + (point.y - 0.5) / zoom)
        let devicePoint = self.sensorPoint(fromView: sensorPoint)
        let manualFocus = self.manualFocus
        let manualExposure = self.manualExposure
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if !manualFocus, !self.cinematicActive, d.isFocusPointOfInterestSupported, d.isFocusModeSupported(.autoFocus) {
                d.focusPointOfInterest = devicePoint
                d.focusMode = .autoFocus
            }
            if !manualExposure, d.isExposurePointOfInterestSupported, d.isExposureModeSupported(.continuousAutoExposure) {
                d.exposurePointOfInterest = devicePoint
                d.exposureMode = .continuousAutoExposure
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
            if self.focusPoint == point, !self.aeafLocked { self.focusPoint = nil }
        }
    }

    func cycleTimer() {
        timerSeconds = timerSeconds == 0 ? 3 : (timerSeconds == 3 ? 10 : 0)
    }

    /// Botão do app, volume ou Controle da Câmera.
    func shutter() {
        userInteracted()
        guard countdown == 0, stackProgress == nil else { return }
        if captureMode == .video || captureMode == .cinematic {
            toggleRecording()
            return
        }
        if captureMode == .panorama {
            togglePanorama()
            return
        }
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
        } else if captureMode == .dual {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                if self.holding && !self.isRecordingVideo { self.startDualRecording() }
            }
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
        } else if captureMode == .dual && isRecordingVideo {
            stopRecording()
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
            guard self.session.outputs.contains(self.photoOutput) else { return }
            attempt("Preparar o disparo rápido") { self.photoOutput.setPreparedPhotoSettingsArray([settings], completionHandler: nil) }
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
            // Só formatos YUV comuns: o ProRes RAW também tem 4K 120, mas só aceita o vídeo deitado (ângulo 0) e fecha o app
            let preference: [FourCharCode] = [kCVPixelFormatType_420YpCbCr8BiPlanarFullRange,
                                              kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange,
                                              kCVPixelFormatType_420YpCbCr10BiPlanarFullRange,
                                              kCVPixelFormatType_420YpCbCr10BiPlanarVideoRange]
            func rank(_ f: AVCaptureDevice.Format) -> Int {
                preference.firstIndex(of: CMFormatDescriptionGetMediaSubType(f.formatDescription)) ?? preference.count
            }
            let candidates = d.formats.filter { f in
                rank(f) < preference.count && f.videoSupportedFrameRateRanges.contains { $0.maxFrameRate >= rate }
            }
            func pixels(_ f: AVCaptureDevice.Format) -> Int {
                let dims = CMVideoFormatDescriptionGetDimensions(f.formatDescription)
                return Int(dims.width) * Int(dims.height)
            }
            // Mesmo tamanho: fica o de 8 bits (mais leve para o visor e para o gravador)
            let chosen = rate >= 240
                ? candidates.min(by: { (pixels($0), rank($0)) < (pixels($1), rank($1)) })
                : candidates.max(by: { (pixels($0), -rank($0)) < (pixels($1), -rank($1)) })
            guard let format = chosen else {
                dlog("⚠️ \(d.localizedName) não tem formato com \(Int(rate)) fps")
                DispatchQueue.main.async { self.message = "Esta lente não grava a \(Int(rate)) fps. Tente a 1×." }
                return
            }
            self.session.beginConfiguration()
            attempt("Trocar o sensor para \(Int(rate)) fps") {
            // O formato rápido não aceita ProRAW nem 48 MP: desliga antes de trocar
            self.photoOutput.isAppleProRAWEnabled = false
            self.session.sessionPreset = .inputPriority
            self.setPreviewSized(mode != .action)
            if (try? d.lockForConfiguration()) != nil {
                d.activeFormat = format
                let duration = CMTime(value: 1, timescale: CMTimeScale(rate))
                d.activeVideoMinFrameDuration = duration
                d.activeVideoMaxFrameDuration = duration
                d.unlockForConfiguration()
            }
            if let dims = format.supportedMaxPhotoDimensions.max(by: { $0.pixels < $1.pixels }) {
                self.photoOutput.maxPhotoDimensions = dims
            }
            }
            let accepted = attempt("Salvar o sensor a \(Int(rate)) fps") { self.session.commitConfiguration() }
            guard accepted else {
                // A câmera recusou: volta ao formato de foto em vez de ficar travada no meio do caminho
                self.setupSession(lens: lens, mode: rawMode)
                DispatchQueue.main.async { self.message = "A câmera não aceitou \(Int(rate)) fps nesta lente." }
                return
            }
            self.specialFormatActive = true
            self.formatWasSpecial = true
            self.applyRawMode(rawMode)
            let dims = CMVideoFormatDescriptionGetDimensions(format.formatDescription)
            dlog("Sensor em \(dims.width)×\(dims.height) a \(Int(rate)) fps (\(mode.rawValue))")
            DispatchQueue.main.async { self.startShutterPriority() }
        }
    }

    private func setPreviewSized(_ on: Bool) {
        guard videoOutput.responds(to: Selector(("setDeliversPreviewSizedOutputBuffers:"))),
              videoOutput.responds(to: Selector(("setAutomaticallyConfiguresOutputBufferDimensions:"))) else { return }
        attempt("Vídeo do visor no tamanho da tela") {
            // O iOS só deixa escolher o tamanho depois de desligar a escolha automática
            videoOutput.setValue(false, forKey: "automaticallyConfiguresOutputBufferDimensions")
            videoOutput.setValue(on, forKey: "deliversPreviewSizedOutputBuffers")
        }
    }

    /// Obturador fixo (CONGELAR 1/4000…, AÇÃO 1/1000) e ISO calculado a partir da luz atual.
    private func startShutterPriority() {
        guard captureMode.fixesShutter, !manualExposure else {
            lowLight = false
            shutterPriorityISO = 0
            // Saiu do CONGELAR/AÇÃO: volta para o automático (ou para o manual que estava)
            updateExposure()
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
            d.safeCustomExposure(seconds: seconds, iso: iso)
            dlog(String(format: "Prioridade de obturador: 1/%.0f s · ISO %.0f", 1 / seconds, iso))
        }
    }

    /// A cada 1/4 s, corrige o ISO pelo brilho do visor (o obturador fica parado).
    private func adjustShutterPriority() {
        guard captureMode.fixesShutter, !manualExposure, shutterPriorityISO > 0, live.histogram.count == 64 else { return }
        let total = live.histogram.reduce(0, +)
        guard total > 0 else { return }
        let mean = live.histogram.enumerated().reduce(Float(0)) { $0 + Float($1.offset) / 63 * $1.element } / total
        let ratio = pow(0.42 / max(mean, 0.02), 2.2)
        guard abs(ratio - 1) > 0.08 else { return }
        let step = pow(min(max(ratio, 0.5), 2), 0.6)
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            let f = d.activeFormat
            let iso = min(max(self.shutterPriorityISO * step, f.minISO), f.maxISO)
            self.shutterPriorityISO = iso
            d.safeCustomExposure(seconds: nil, iso: iso)
            let dark = iso >= f.maxISO * 0.95 && ratio > 1.2
            DispatchQueue.main.async { if self.lowLight != dark { self.lowLight = dark } }
        }
    }

    // MARK: - Captura

    private func capture() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        // A miniatura aparece na hora (o quadro do visor); a foto revelada troca por ela quando ficar pronta
        // (feita fora da fila principal: renderizar 1600 px ali travava o toque)
        let shotDate = Date()
        lastQuickPhoto = nil
        let previewOptions = renderer.options
        renderer.snapshotQueue.async { [renderer] in
            guard let quick = renderer.snapshot(maxSide: 1600, options: previewOptions) else { return }
            DispatchQueue.main.async {
                // Se a foto revelada já chegou, não troca a de verdade pela prévia
                guard self.lastShotDate == shotDate, self.processing > 0 else { return }
                self.thumbnail = quick
                self.lastQuickPhoto = quick
            }
        }
        lastShotDate = shotDate
        processing += 1
        flash = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.12) { self.flash = false }

        let options = developOptions
        var mode = captureMode
        // Macro: empilhado vira foco empilhado; 2× e 3× usam a super resolução para não perder detalhe
        if mode == .photo, lens == .macro {
            if macroStack { mode = .focusStack } else if macroZoom > 1 { mode = .superRes }
        }
        let t0 = CFAbsoluteTimeGetCurrent()
        dlog("📸 \(mode.rawValue) · \(lens.rawValue) zoom \(zoomText) · \(rawMode.rawValue) · look \(lookName) · \(aspect.rawValue) · " +
             (manualExposure ? "ISO \(Int(selectedISO)) \(String(format: "%.4f", selectedShutter))s" : "auto ISO \(Int(readoutISO)) \(String(format: "%.4f", readoutShutter))s"))
        if mode == .action {
            // AÇÃO sem segurar: grava 1 segundo
            processing -= 1
            startAction()
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { self.stopAction() }
            return
        }
        if mode == .hdr {
            sessionQueue.async { self.captureHDR(options: options, started: t0) }
            return
        }
        if mode == .longExposure {
            startLongExposure(options: options, started: t0)
            return
        }
        if mode == .dual {
            saveDualPhoto(options: options, started: t0)
            return
        }
        // O que fica nítido no Retrato: o ponto que você tocou, senão o rosto (visor -> foto, desfazendo o recorte)
        let portraitFocus = photoPoint(fromView: portraitChoice)
        let aperture = portraitAperture
        // Três looks: lidos aqui (na fila principal); rajada não entra (seriam centenas de fotos)
        let extraLooks = multiLook && !mode.holdsForBurst
            ? extraLookIDs.compactMap { self.options(swappingLookTo: $0, from: options) } : []
        guard mode.frameCount > 1 || mode == .night else {
            let flash = mode == .flash
            let fast = mode.usesFastFormat
            let portrait = mode == .portrait
            sessionQueue.async {
                self.captureRAW(forStack: false, flash: flash, fast: fast, portrait: portrait) { result in
                    dlog("RAW recebido: \(Diagnostics.ms(since: t0))")
                    self.process(result.map { [$0] }, mode: mode, options: options, started: t0,
                                 aperture: aperture, focusPoint: portraitFocus, extraLooks: extraLooks)
                }
            }
            return
        }

        // Sequência: no foco empilhado, cada quadro com o foco um pouco mais longe
        let macroStacking = mode == .focusStack && lens == .macro
        // Escuro de verdade com o iPhone apoiado: mais fotos (cada uma de 1 s, logo abaixo)
        let veryDark = mode == .night && isSteady && nightTime == .auto && readoutISO >= 3200
        let normalCount = mode == .night ? (veryDark ? max(nightFrames, 12) : nightFrames) : (macroStacking ? 6 : mode.frameCount)
        // NOITE: mais uma foto curta no fim, só para as luzes fortes (postes) não estourarem
        let shortLast = mode == .night && !manualExposure
        let count = normalCount + (shortLast ? 1 : 0)
        let center = manualFocus ? lensPosition : readoutLensPosition
        let span: Float = lens == .macro ? 0.1 : 0.16
        let positions: [Float]? = mode == .focusStack
            ? (0..<count).map { i in
                let start = max(0, center - span / 2), end = min(1, center + span / 2)
                return start + (end - start) * Float(i) / Float(count - 1)
            }
            : nil
        stackProgress = "0/\(count)"
        // Macro empilhado em 48 MP: o recorte do macro precisa do sensor inteiro
        // SUPER ZOOM em 12 MP: nas fotos de 48 MP o iPhone ignora o obturador rápido (o relatório mostrou 1/30 s
        // pedido 1/170) e cada uma leva 1,6 s; em 12 MP o obturador vale e saem 3 por segundo, quase sem tremido
        let fullResolution = mode == .superRes || mode == .moon || macroStacking
        let nightPlan = mode == .night && !manualExposure
        // Noite: tempo escolhido, ou no Auto 1/2 s se o iPhone está apoiado e 1/8 s na mão
        let nightSeconds = nightTime.seconds ?? (veryDark ? 1.0 : (isSteady ? 0.5 : 1.0 / 8))
        let nightAuto = nightTime == .auto
        // Super resolução: obturador rápido (foto tremida não cria detalhe) — 1/60 na 1×, 1/120 na 4×, 1/240 a 8×…
        let fastPlan = (mode == .superRes || mode == .superZoom) && !manualExposure
        let fastSeconds = min(1.0 / 60, 1.0 / (30 * max(Double(zoom), 1)))
        let lockFocus = !manualFocus
        let waitForStill = mode == .superZoom
        sessionQueue.async {
            let run = {
                self.shootSequence(index: 0, count: count, positions: positions, frames: [], fullResolution: fullResolution,
                                   shortLast: shortLast) { result in
                    dlog("Sequência de \(count) fotografada: \(Diagnostics.ms(since: t0))")
                    DispatchQueue.main.async {
                        self.stackProgress = nil
                        self.updateFocus()
                        self.updateExposure()
                        self.updateWhiteBalance()
                    }
                    self.process(result, mode: mode, options: options, started: t0)
                }
            }
            let begin = {
                guard nightPlan || fastPlan, let d = self.device, (try? d.lockForConfiguration()) != nil else { return run() }
                let f = d.activeFormat
                if fastPlan {
                    // Todas as fotos iguais: cor e foco travados na primeira (a exposição fica fixa logo abaixo)
                    attempt("Travar cor e foco") {
                        if d.isWhiteBalanceModeSupported(.locked) { d.whiteBalanceMode = .locked }
                        if lockFocus, d.isFocusModeSupported(.locked) { d.focusMode = .locked }
                    }
                }
                let current = d.exposureDuration.seconds
                var target = nightPlan ? nightSeconds : min(fastSeconds, current)
                // Sem passar do ISO máximo: se falta luz, fica no mais rápido que ainda expõe certo
                if fastPlan { target = max(target, current * Double(d.iso) / Double(f.maxISO)) }
                target = min(max(target, f.minExposureDuration.seconds), f.maxExposureDuration.seconds)
                // NOITE no breu: o automático do iPhone fica abaixo do que ele mesmo queria (falta de ISO no visor).
                // O que faltava (até 2 paradas) entra no ISO, que nas fotos longas ainda tem folga
                let deficit = nightPlan && nightAuto ? min(2, max(0, -d.exposureTargetOffset)) : 0
                let iso = min(max(d.iso * Float(current / target) * exp2(deficit), f.minISO), f.maxISO)
                dlog(String(format: "%@: %.4fs ISO %.0f → %.4fs ISO %.0f · %d fotos%@", nightPlan ? "Noite" : "Super resolução",
                            current, d.iso, target, iso, count, deficit > 0.1 ? String(format: " · +%.1f EV", deficit) : ""))
                // Se a câmera parar no meio (ligação, Central de Controle), a resposta pode nunca vir: segue sozinho
                let go = self.onceOnSessionQueue(timeout: 2 + target * 2, run)
                d.safeCustomExposure(seconds: target, iso: iso) { _ in go() }
                d.unlockForConfiguration()
            }
            if waitForStill { self.waitUntilStill(then: begin) } else { begin() }
        }
    }

    /// SUPER ZOOM: espera a mão firmar (giroscópio quase parado por 0,4 s), no máximo 2,5 s, e então dispara.
    /// Na mão não precisa ficar 100% parado: espera no máximo 1 s um momento mais calmo da mão.
    private func waitUntilStill(timeout: Double = 1, then action: @escaping () -> Void) {
        let deadline = Date().addingTimeInterval(timeout)
        func check() {
            let recent = recentRotation.suffix(4)
            if (recent.count == 4 && (recent.max() ?? 1) < 0.12) || Date() > deadline {
                dlog(Date() > deadline ? "Super zoom: disparou com a mão mexendo (1 s)" : "Super zoom: mão calma, disparando")
                sessionQueue.async(execute: action)
                return
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { check() }
        }
        DispatchQueue.main.async {
            self.show("Segure o melhor que der…")
            check()
        }
    }

    /// Fotos de 48 MP de uma sequência vão para um arquivo e voltam mapeadas: o iOS lê do disco quando precisa,
    /// em vez de segurar 6 × 70 MB na memória. O arquivo some sozinho quando a foto é solta.
    private func spilled(_ frame: CapturedFrame) -> CapturedFrame {
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent("sequencia", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let url = dir.appendingPathComponent(UUID().uuidString)
        guard (try? frame.data.write(to: url)) != nil,
              let mapped = try? Data(contentsOf: url, options: .alwaysMapped) else { return frame }
        // Apagar já: o mapeamento continua valendo até a foto ser solta, e o espaço volta sozinho
        try? FileManager.default.removeItem(at: url)
        var copy = CapturedFrame(data: mapped, isRaw: frame.isRaw, hasDepth: frame.hasDepth)
        copy.exposureBias = frame.exposureBias
        return copy
    }

    /// `shortLast`: a última foto sai 3 paradas mais escura (1/8 do tempo), para as luzes fortes.
    private func shootSequence(index: Int, count: Int, positions: [Float]?, frames: [CapturedFrame],
                               fullResolution: Bool = false, shortLast: Bool = false,
                               completion: @escaping (Result<[CapturedFrame], Error>) -> Void) {
        guard index < count else { return completion(.success(frames)) }
        let isShort = shortLast && index == count - 1
        let shoot = {
            self.captureRAW(forStack: !fullResolution) { result in
                switch result {
                case .failure(let error):
                    completion(.failure(error))
                case .success(var data):
                    if isShort { data.exposureBias = -3 }
                    DispatchQueue.main.async { self.stackProgress = "\(index + 1)/\(count)" }
                    self.sessionQueue.async {
                        self.shootSequence(index: index + 1, count: count, positions: positions,
                                           frames: frames + [self.spilled(data)],
                                           fullResolution: fullResolution, shortLast: shortLast, completion: completion)
                    }
                }
            }
        }
        if isShort, let d = device, (try? d.lockForConfiguration()) != nil {
            // Mesmo ISO, 1/8 do tempo: espera a câmera aplicar e fotografa
            let f = d.activeFormat
            let duration = max(d.exposureDuration.seconds / 8, f.minExposureDuration.seconds)
            let go = onceOnSessionQueue(timeout: 2 + duration * 2, shoot)
            d.safeCustomExposure(seconds: duration, iso: d.iso) { _ in go() }
            d.unlockForConfiguration()
            return
        }
        guard let positions, let d = device, d.isLockingFocusWithCustomLensPositionSupported,
              (try? d.lockForConfiguration()) != nil else { return shoot() }
        // Espera a lente chegar na posição antes de fotografar
        let go = onceOnSessionQueue(timeout: 2, shoot)
        d.setFocusModeLocked(lensPosition: positions[index]) { _ in go() }
        d.unlockForConfiguration()
    }

    /// Gatilho que roda `action` uma vez só na fila da câmera: quando a câmera responder ou, se ela não responder, após `timeout` s.
    private func onceOnSessionQueue(timeout: Double, _ action: @escaping () -> Void) -> () -> Void {
        let lock = NSLock()
        var done = false
        let fire: () -> Void = {
            lock.lock()
            let first = !done
            done = true
            lock.unlock()
            if first { self.sessionQueue.async(execute: action) }
        }
        sessionQueue.asyncAfter(deadline: .now() + timeout, execute: fire)
        return fire
    }

    /// Fotografa um RAW e devolve o DNG. Em sequências usa 12 MP para caber na memória.
    private func captureRAW(forStack: Bool, flash: Bool = false, fast: Bool = false, portrait: Bool = false,
                            completion: @escaping (Result<CapturedFrame, Error>) -> Void) {
        let mode = rawMode
        let types = photoOutput.availableRawPhotoPixelFormatTypes
        let format: OSType?
        let withDepth = portrait && photoOutput.isDepthDataDeliveryEnabled
        if withDepth {
            // Retrato: HEIC com o mapa de profundidade e a máscara de pessoa dentro
            format = nil
        } else if fast {
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
        } else if withDepth, let d = device {
            // Profundidade costuma vir até 12 MP; mais que isso pode ser recusado
            let dims = d.activeFormat.supportedMaxPhotoDimensions
                .filter { $0.pixels <= 12_600_000 && $0.pixels <= photoOutput.maxPhotoDimensions.pixels }
                .max(by: { $0.pixels < $1.pixels })
            if let dims { settings.maxPhotoDimensions = dims }
        } else if format == nil, !forStack {
            settings.maxPhotoDimensions = photoOutput.maxPhotoDimensions
        }
        if withDepth {
            settings.isDepthDataDeliveryEnabled = true
            settings.embedsDepthDataInPhoto = true
            if photoOutput.isPortraitEffectsMatteDeliveryEnabled {
                settings.isPortraitEffectsMatteDeliveryEnabled = true
                settings.embedsPortraitEffectsMatteInPhoto = true
            }
            if !photoOutput.enabledSemanticSegmentationMatteTypes.isEmpty {
                settings.enabledSemanticSegmentationMatteTypes = photoOutput.enabledSemanticSegmentationMatteTypes
                settings.embedsSemanticSegmentationMattesInPhoto = true
            }
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
            completion(result.map { frame in
                var f = frame
                f.hasDepth = withDepth
                return f
            })
        }
        inFlight[id] = delegate
        let accepted = attempt("Tirar a foto") { photoOutput.capturePhoto(with: settings, delegate: delegate) }
        if !accepted {
            inFlight[id] = nil
            completion(.failure(RevelaError.noRawData))
        }
    }

    // MARK: - Vídeo, cinema e câmera dupla

    private func openScanner() {
        guard SceneScanner.isSupported else {
            message = "O scanner 3D precisa de um iPhone com LiDAR."
            return
        }
        let fromDual = captureMode == .dual
        if fromDual { select(captureMode: .photo) }
        if isRecordingVideo { stopRecording() }
        dlog("Scanner 3D aberto")
        sessionQueue.async {
            if self.session.isRunning { self.session.stopRunning() }
            // Saindo da DUPLA as câmeras ainda estão sendo soltas: o ARKit falhava ("Required sensor failed")
            DispatchQueue.main.asyncAfter(deadline: .now() + (fromDual ? 0.8 : 0)) { self.showScanner = true }
        }
    }

    @Published var showDocument = false

    // MARK: - Teste de modos

    /// Prévia da última foto (o visor no instante do clique), para o Revelar de novo abrir na hora.
    var lastQuickPhoto: UIImage?
    var lastShotDate = Date.distantPast

    /// "NOITE (12/23)" enquanto o teste roda.
    @Published var selfTestProgress: String?
    private var selfTestCancelled = false

    /// Entra em cada modo (e em cada lente), espera, confere se a imagem chega e anota tudo no relatório.
    /// Se o app fechar no meio, a próxima abertura anota em qual modo foi.
    func runModeSelfTest() {
        guard selfTestProgress == nil else { return }
        selfTestCancelled = false
        let modes = CaptureMode.allCases.filter { $0 != .photo }
        let lenses = availableLenses.filter { $0 != .macro } + (hasFront ? [.front] : []) + [.wide]
        var steps: [(name: String, action: () -> Void, waitsForFrames: Bool)] = []
        for mode in modes {
            let previewless = mode == .cinematic || mode == .scan || mode == .document
            steps.append((mode.rawValue, { self.select(captureMode: mode) }, !previewless))
            if mode == .scan { steps.append(("fechar 3D", { self.showScanner = false; self.scannerClosed() }, false)) }
            if mode == .document { steps.append(("fechar DOC", { self.showDocument = false; self.documentClosed() }, false)) }
            steps.append(("FOTO", { self.select(captureMode: .photo) }, true))
        }
        for lens in lenses {
            steps.append(("lente \(lens.rawValue)", { self.select(lens: lens) }, true))
        }
        dlog("🧪 Teste de modos: \(steps.count) passos")
        var problems: [String] = []
        func run(_ index: Int) {
            guard !selfTestCancelled, index < steps.count else {
                defaults.removeObject(forKey: "selfTestCurrent")
                selfTestProgress = nil
                let summary = problems.isEmpty ? "tudo ok" : "sem imagem em: " + problems.joined(separator: ", ")
                dlog("🧪 Teste de modos \(selfTestCancelled ? "cancelado" : "concluído"): \(summary)")
                message = selfTestCancelled ? "Teste cancelado." :
                    (problems.isEmpty ? "Teste concluído: todos os modos abriram com imagem." :
                        "Teste concluído. Sem imagem em: \(problems.joined(separator: ", ")). Mande o relatório.")
                return
            }
            let step = steps[index]
            selfTestProgress = "\(step.name) (\(index + 1)/\(steps.count))"
            defaults.set(step.name, forKey: "selfTestCurrent")
            let before = renderer.enqueuedCount
            let t0 = CFAbsoluteTimeGetCurrent()
            step.action()
            DispatchQueue.main.asyncAfter(deadline: .now() + 3.2) {
                let frames = self.renderer.enqueuedCount &- before
                let running = self.session.isRunning || self.dualActiveForUI
                let ok = !step.waitsForFrames || frames > 5
                if !ok { problems.append(step.name) }
                dlog(String(format: "🧪 %@: %@ · %d quadros em 3 s · sessão %@ · %@", step.name, ok ? "ok" : "SEM IMAGEM",
                            frames, running ? "rodando" : "parada", Diagnostics.ms(since: t0)))
                run(index + 1)
            }
        }
        run(0)
    }

    func cancelModeSelfTest() { selfTestCancelled = true }

    /// A câmera dupla roda numa sessão própria.
    private var dualActiveForUI: Bool { captureMode == .dual }

    // MARK: - Panorama

    private let panorama = PanoramaCapture()
    /// Giro feito (0…1 de 180°) enquanto o panorama está gravando; nil parado.
    @Published var panoramaProgress: Double?
    @Published var panoramaWarning: String?

    private func togglePanorama() {
        if panoramaProgress != nil { return finishPanorama() }
        guard lens != .front else {
            message = "O panorama usa as câmeras de trás."
            return
        }
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        dlog("📸 PANORAMA · \(lens.rawValue) · look \(lookName)")
        panoramaProgress = 0
        panoramaWarning = nil
        panorama.onProgress = { [weak self] progress, warning in
            guard let self, self.panoramaProgress != nil else { return }
            self.panoramaProgress = progress
            if warning != self.panoramaWarning { self.panoramaWarning = warning }
        }
        panorama.onLimit = { [weak self] in
            guard let self, self.panoramaProgress != nil else { return }
            self.finishPanorama()
        }
        let step = shortSideFOV * 0.42
        sessionQueue.async {
            // Luz, cor e foco travados: as emendas não mudam de brilho nem de cor
            if let d = self.device, (try? d.lockForConfiguration()) != nil {
                attempt("Travar para o panorama") {
                    if d.isExposureModeSupported(.locked) { d.exposureMode = .locked }
                    if d.isWhiteBalanceModeSupported(.locked) { d.whiteBalanceMode = .locked }
                    if d.isFocusModeSupported(.locked) { d.focusMode = .locked }
                }
                d.unlockForConfiguration()
            }
            // Quadros em resolução cheia enquanto gira
            self.session.beginConfiguration()
            self.setPreviewSized(false)
            attempt("Salvar a configuração") { self.session.commitConfiguration() }
            self.panorama.start(step: step)
        }
    }

    private func finishPanorama() {
        guard panoramaProgress != nil else { return }
        panoramaProgress = nil
        panoramaWarning = nil
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
        processing += 1
        var options = developOptions
        options.zoom = 1
        let fov = shortSideFOV
        let t0 = CFAbsoluteTimeGetCurrent()
        // Na mesma fila do começo: um toque duplo rápido não deixa o fim passar na frente do começo
        sessionQueue.async { self.panorama.finish { frames in
            self.sessionQueue.async {
                self.session.beginConfiguration()
                self.setPreviewSized(true)
                attempt("Salvar a configuração") { self.session.commitConfiguration() }
            }
            DispatchQueue.main.async {
                self.updateExposure()
                self.updateWhiteBalance()
                self.updateFocus()
            }
            guard frames.count >= 2 else {
                DispatchQueue.main.async {
                    self.processing -= 1
                    self.message = "Gire mais o iPhone para fazer o panorama."
                }
                return
            }
            self.processingQueue.async {
                let output = Developer.panorama(frames, fov: fov, options: options)
                var stored = options
                stored.originalAspect = true
                let keep = self.keepNeutral(output, options: stored, mode: CaptureMode.panorama.rawValue)
                Library.save(dng: nil, developed: output?.heic, tryPair: false, onSaved: keep) { error in
                    DispatchQueue.main.async {
                        self.processing -= 1
                        if let error { self.message = error.localizedDescription }
                        else if output == nil { self.message = "Não consegui emendar o panorama." }
                        else if let thumb = output?.thumbnail { self.thumbnail = thumb }
                    }
                    dlog(output == nil ? "❌ Panorama falhou" : "✅ Panorama salvo. Total: \(Diagnostics.ms(since: t0))")
                }
            }
        } }
    }

    private func openDocumentScanner() {
        let fromDual = captureMode == .dual
        if fromDual { select(captureMode: .photo) }
        if isRecordingVideo { stopRecording() }
        dlog("Scanner de documentos aberto")
        sessionQueue.async {
            if self.session.isRunning { self.session.stopRunning() }
            DispatchQueue.main.asyncAfter(deadline: .now() + (fromDual ? 0.8 : 0)) { self.showDocument = true }
        }
    }

    /// Revelar de novo aberto: a câmera descansa (bateria e GPU livres para revelar).
    func pauseSession() {
        pauseWanted = true
        // Com foto ainda saindo da câmera, parar a sessão perderia a foto (para quando ela terminar)
        guard !isRecordingVideo, panoramaProgress == nil, processing == 0 else { return }
        pauseWanted = false
        sessionQueue.async {
            if self.session.isRunning { self.session.stopRunning() }
        }
    }

    func resumeSession() {
        pauseWanted = false
        sessionQueue.async {
            if !self.session.isRunning, !self.dualActive { self.session.startRunning() }
        }
    }

    func documentClosed() {
        dlog("Scanner de documentos fechado")
        sessionQueue.async {
            if !self.session.isRunning { self.session.startRunning() }
        }
    }

    func scannerClosed() {
        dlog("Scanner 3D fechado")
        sessionQueue.async {
            if !self.session.isRunning { self.session.startRunning() }
        }
    }

    private func requestMicrophone() {
        guard AVCaptureDevice.authorizationStatus(for: .audio) == .notDetermined else { return }
        AVCaptureDevice.requestAccess(for: .audio) { granted in
            dlog("Microfone: \(granted ? "liberado" : "negado (vídeo sem som)")")
            guard granted else { return }
            // Reabre a sessão para incluir o microfone
            DispatchQueue.main.async {
                let lens = self.lens, raw = self.rawMode
                self.sessionQueue.async { self.setupSession(lens: lens, mode: raw) }
            }
        }
    }

    private func applyVideoFrameRate() {
        guard let d = device else { return }
        let fps = Double(DispatchQueue.main.sync { self.videoFPS })
        guard d.activeFormat.videoSupportedFrameRateRanges.contains(where: { $0.minFrameRate <= fps && fps <= $0.maxFrameRate }),
              (try? d.lockForConfiguration()) != nil else {
            dlog("⚠️ Vídeo: \(Int(fps)) fps não disponível neste formato")
            return
        }
        let duration = CMTime(value: 1, timescale: CMTimeScale(fps))
        attempt("Quadros do vídeo") {
            // Primeiro solta o máximo (senão o mínimo novo pode ficar acima do máximo antigo)
            d.activeVideoMaxFrameDuration = .invalid
            d.activeVideoMinFrameDuration = duration
            d.activeVideoMaxFrameDuration = duration
        }
        d.unlockForConfiguration()
    }

    /// Estabilização só nos modos de vídeo (na foto ela atrasaria o visor).
    private func applyStabilization() {
        // No SUPER ZOOM o visor também fica estabilizado: a 25× a imagem pula muito para enquadrar
        let wanted: Stabilization = (videoWanted || cinematicWanted) ? DispatchQueue.main.sync { self.stabilization }
            : (superZoomWanted ? .strong : .off)
        let mode = wanted.mode
        for output in [videoOutput, movieOutput] as [AVCaptureOutput] where session.outputs.contains(output) {
            guard let connection = output.connection(with: .video), connection.isVideoStabilizationSupported else { continue }
            let supported = device?.activeFormat.isVideoStabilizationModeSupported(mode) ?? false
            let chosen: AVCaptureVideoStabilizationMode = supported ? mode : (wanted == .off ? .off : .standard)
            if connection.preferredVideoStabilizationMode != chosen {
                attempt("Estabilização") { connection.preferredVideoStabilizationMode = chosen }
                if wanted != .off { dlog("Estabilização: \(wanted.rawValue)\(supported ? "" : " (este formato só aceita a normal)")") }
            }
        }
    }

    /// 60 quadros no visor quando o formato de foto aceita; o automático ainda pode baixar para 30 no escuro.
    private func applyPreviewRate() {
        guard !videoWanted, !cinematicWanted, !specialFormatActive, let d = device else { return }
        let want60 = DispatchQueue.main.sync { self.preview60 }
        let maxRate = d.activeFormat.videoSupportedFrameRateRanges.map(\.maxFrameRate).max() ?? 30
        let fast = want60 && maxRate >= 60
        guard (try? d.lockForConfiguration()) != nil else { return }
        attempt("Quadros do visor") {
            // .invalid devolve o padrão do formato (o automático continua livre para alongar a exposição no escuro)
            d.activeVideoMinFrameDuration = fast ? CMTime(value: 1, timescale: 60) : .invalid
            d.activeVideoMaxFrameDuration = .invalid
        }
        d.unlockForConfiguration()
        if want60 { dlog(fast ? "Visor até 60 quadros/s" : "Visor: \(d.localizedName) não passa de \(Int(maxRate)) quadros/s no formato de foto") }
    }

    func setVideoFPS(_ fps: Int) {
        videoFPS = fps
        sessionQueue.async { self.applyVideoFrameRate() }
    }

    /// Cinema: escolhe um formato 1080p que suporta o modo e liga o desfoque simulado.
    private func configureCinematic(device dev: AVCaptureDevice, input: AVCaptureDeviceInput) {
        formatWasSpecial = true
        guard #available(iOS 26.0, *) else {
            post("O vídeo com fundo desfocado precisa do iOS 26 ou mais novo.")
            return
        }
        let formats = dev.formats.filter { $0.isCinematicVideoCaptureSupported }
        func dims(_ f: AVCaptureDevice.Format) -> CMVideoDimensions { CMVideoFormatDescriptionGetDimensions(f.formatDescription) }
        guard let format = formats.first(where: { dims($0).width == 1920 && dims($0).height == 1080 }) ?? formats.first else {
            dlog("⚠️ Cinema: \(dev.localizedName) não tem formato para o modo cinema")
            post("Esta câmera não grava no modo cinema. Tente a 1× ou a frontal.")
            return
        }
        if (try? dev.lockForConfiguration()) != nil {
            dev.activeFormat = format
            dev.unlockForConfiguration()
        }
        guard input.isCinematicVideoCaptureSupported else {
            dlog("⚠️ Cinema: a entrada não suporta o modo cinema")
            return
        }
        guard attempt("Ligar o modo cinema", { input.isCinematicVideoCaptureEnabled = true }) else { return }
        cinematicActive = true
        let minA = format.minSimulatedAperture, maxA = format.maxSimulatedAperture
        if minA > 0, maxA >= minA {
            let wanted = DispatchQueue.main.sync { self.cinematicAperture }
            attempt("Abertura do modo cinema") { input.simulatedAperture = min(max(wanted, minA), maxA) }
            DispatchQueue.main.async {
                self.cinematicRange = minA...maxA
                if !(minA...maxA).contains(self.cinematicAperture) { self.cinematicAperture = format.defaultSimulatedAperture }
            }
        }
        let d = dims(format)
        dlog("Cinema: \(dev.localizedName) \(d.width)×\(d.height) · abertura f/\(minA)–f/\(maxA)")
    }

    func setCinematicAperture(_ value: Float) {
        cinematicAperture = value
        guard !isRecordingVideo else { return }
        sessionQueue.async {
            guard #available(iOS 26.0, *), self.cinematicActive,
                  let input = self.session.inputs.compactMap({ $0 as? AVCaptureDeviceInput }).first(where: { $0.device.hasMediaType(.video) }),
                  input.device.activeFormat.minSimulatedAperture > 0 else { return }
            let f = input.device.activeFormat
            attempt("Abertura do modo cinema") { input.simulatedAperture = min(max(value, f.minSimulatedAperture), f.maxSimulatedAperture) }
        }
    }

    private func toggleRecording() {
        if isRecordingVideo { stopRecording() } else { startRecording() }
    }

    /// Giro do vídeo na reprodução quando o iPhone está deitado (o visor fica sempre em pé).
    private var recordingTransform: CGAffineTransform {
        guard let coordinator = rotationCoordinator else { return .identity }
        let delta = coordinator.videoRotationAngleForHorizonLevelCapture - coordinator.videoRotationAngleForHorizonLevelPreview
        return CGAffineTransform(rotationAngle: delta * .pi / 180)
    }

    private func startRecording() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        isRecordingVideo = true
        recordingStarted = Date()
        if captureMode == .cinematic {
            let angle = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture
            sessionQueue.async {
                if let angle, let c = self.movieOutput.connection(with: .video), c.isVideoRotationAngleSupported(angle) {
                    c.videoRotationAngle = angle
                }
                let url = FileManager.default.temporaryDirectory.appendingPathComponent("cinema-\(UUID().uuidString).mov")
                attempt("Gravar no modo cinema") { self.movieOutput.startRecording(to: url, recordingDelegate: self) }
                dlog("Cinema: gravando")
            }
        } else {
            let fps = videoFPS
            let transform = recordingTransform
            videoQueue.async {
                let size = self.lastFrameSize
                self.recorder.start(width: Int(size.width), height: Int(size.height), fps: fps, transform: transform)
            }
        }
    }

    func stopRecording() {
        guard isRecordingVideo else { return }
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
        isRecordingVideo = false
        recordingStarted = nil
        if movieOutput.isRecording {
            sessionQueue.async { self.movieOutput.stopRecording() }
            return
        }
        processing += 1
        recorder.stop { url, frames in
            dlog("Vídeo: \(frames) quadros gravados")
            guard let url else {
                DispatchQueue.main.async {
                    self.processing -= 1
                    self.message = "O vídeo não foi gravado."
                }
                return
            }
            Library.saveVideo(url) { error in
                try? FileManager.default.removeItem(at: url)
                DispatchQueue.main.async {
                    self.processing -= 1
                    if let error { self.message = error.localizedDescription } else { self.show("Vídeo salvo na galeria") }
                }
            }
        }
    }

    func fileOutput(_ output: AVCaptureFileOutput, didFinishRecordingTo outputFileURL: URL,
                    from connections: [AVCaptureConnection], error: Error?) {
        // O arquivo pode estar bom mesmo com erro (ex.: parou por falta de espaço)
        let finished = (error as NSError?)?.userInfo[AVErrorRecordingSuccessfullyFinishedKey] as? Bool ?? (error == nil)
        dlog("Cinema: gravação terminou\(finished ? "" : " com erro: \(error?.localizedDescription ?? "")")")
        DispatchQueue.main.async {
            self.isRecordingVideo = false
            self.recordingStarted = nil
        }
        guard finished else {
            DispatchQueue.main.async { self.message = "O vídeo no modo cinema não foi gravado." }
            return
        }
        Library.saveVideo(outputFileURL) { saveError in
            try? FileManager.default.removeItem(at: outputFileURL)
            DispatchQueue.main.async {
                if let saveError { self.message = saveError.localizedDescription }
                else { self.show("Vídeo cinema salvo. No app Fotos dá para mudar o foco e o desfoque.") }
            }
        }
    }

    /// Tamanho do último quadro do visor (para o gravador saber a resolução). Lido na fila de vídeo.
    private var lastFrameSize = CGSize(width: 1080, height: 1920)

    /// Quadro com o look e o zoom, do jeito que vai para o arquivo de vídeo.
    private func recordingImage(_ frame: CIImage) -> CIImage {
        var options = renderer.options
        options.zebra = false
        options.peaking = false
        options.falseColor = false
        let c = options.develop.zoom
        var image = frame
        if c > 1.01 {
            let e = frame.extent
            let rect = CGRect(x: e.midX - e.width / c / 2, y: e.midY - e.height / c / 2, width: e.width / c, height: e.height / c)
            image = frame.cropped(to: rect)
                .transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))
                .transformed(by: CGAffineTransform(scaleX: c, y: c))
                .transformed(by: CGAffineTransform(translationX: e.minX, y: e.minY))
                .cropped(to: e)
        }
        return Developer.preview(image, options: options)
    }

    private func switchDual(on: Bool) {
        guard DualCamera.isSupported else {
            if on { message = "Este iPhone não usa as duas câmeras ao mesmo tempo." }
            return
        }
        if on {
            dual.onFrame = { [weak self] image, time in
                guard let self else { return }
                self.dualLock.lock()
                self.latestDualFrame = image
                self.dualLock.unlock()
                self.renderer.enqueue(image)
                if self.recorder.isRecording { self.recorder.append(self.recordingImage(image), at: time) }
            }
            dual.onAudio = { [weak self] buffer in self?.recorder.appendAudio(buffer) }
            dual.onFailure = { [weak self] in
                // Só volta se ainda estiver na DUPLA (você pode já ter trocado de modo)
                guard let self, self.captureMode == .dual else { return }
                self.message = "A câmera dupla não abriu agora. Voltei para FOTO."
                self.select(captureMode: .photo)
            }
            sessionQueue.async {
                self.dualActive = true
                self.formatWasSpecial = true
                if self.session.isRunning { self.session.stopRunning() }
                self.dual.start(withAudio: AVCaptureDevice.authorizationStatus(for: .audio) == .authorized)
            }
        } else {
            if isRecordingVideo { stopRecording() }
            let lens = self.lens, raw = rawMode
            sessionQueue.async {
                // A dupla deixou a câmera de trás em 1080p sem RAW: desmonta a dupla e reabre a câmera no formato de foto
                self.dual.stopAndRelease()
                self.dualActive = false
                self.setupSession(lens: lens, mode: raw)
                if !self.session.isRunning { self.session.startRunning() }
            }
        }
    }

    private func startDualRecording() {
        dualLock.lock()
        let size = latestDualFrame?.extent.size ?? CGSize(width: 1080, height: 1920)
        dualLock.unlock()
        isRecordingVideo = true
        recordingStarted = Date()
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        recorder.start(width: Int(size.width), height: Int(size.height), fps: 30, transform: .identity)
    }

    private func saveDualPhoto(options: DevelopOptions, started t0: CFAbsoluteTime) {
        dualLock.lock()
        let frame = latestDualFrame
        dualLock.unlock()
        guard let frame else {
            processing -= 1
            return
        }
        var opts = options
        opts.zoom = 1
        processingQueue.async {
            let output = Developer.developVideoImage(frame, options: opts)
            Library.save(dng: nil, developed: output?.heic, tryPair: false) { error in
                dlog(error == nil ? "✅ Foto dupla salva: \(Diagnostics.ms(since: t0))" : "❌ \(error!.localizedDescription)")
                DispatchQueue.main.async {
                    self.processing -= 1
                    if let thumb = output?.thumbnail { self.thumbnail = thumb }
                }
            }
        }
    }

    // MARK: - Exposição longa

    private func startLongExposure(options: DevelopOptions, started t0: CFAbsoluteTime) {
        let seconds = longSecondsChoice
        let style = longStyle
        // Apoiado não precisa alinhar; na mão, cada quadro é alinhado com o primeiro
        let handheld = !isSteady
        let manual = manualExposure
        stackProgress = "0 s"
        longRemaining = seconds
        dlog("Exposição longa: \(seconds) s · \(style.rawValue)\(handheld ? " · na mão (alinhando)" : " · apoiado")")
        sessionQueue.async {
            // Vídeo em resolução cheia durante a exposição, e cada quadro exposto o quadro inteiro (sem buracos no movimento)
            self.session.beginConfiguration()
            self.setPreviewSized(false)
            attempt("Salvar a configuração") { self.session.commitConfiguration() }
            if !manual, let d = self.device, (try? d.lockForConfiguration()) != nil {
                let f = d.activeFormat
                let target = min(1.0 / 30, f.maxExposureDuration.seconds)
                let iso = min(max(d.iso * Float(d.exposureDuration.seconds / target), f.minISO), f.maxISO)
                d.safeCustomExposure(seconds: target, iso: iso)
                d.unlockForConfiguration()
            }
            self.videoQueue.async {
                self.longExposure.start(seconds: seconds, style: style, handheld: handheld) { image, count in
                    self.finishLongExposure(image, frames: count, options: options, started: t0)
                }
            }
        }
        tickLongExposure(until: CFAbsoluteTimeGetCurrent() + seconds)
    }

    private func tickLongExposure(until end: CFAbsoluteTime) {
        let left = end - CFAbsoluteTimeGetCurrent()
        guard left > 0, longRemaining != nil else { return }
        longRemaining = left
        stackProgress = String(format: "%.1f s", left).replacingOccurrences(of: ".", with: ",")
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { self.tickLongExposure(until: end) }
    }

    private func finishLongExposure(_ image: CIImage?, frames: Int, options: DevelopOptions, started t0: CFAbsoluteTime) {
        dlog("Exposição longa: \(frames) quadros somados \(image.map { "\(Int($0.extent.width))×\(Int($0.extent.height))" } ?? "—")")
        sessionQueue.async {
            self.session.beginConfiguration()
            self.setPreviewSized(true)
            attempt("Salvar a configuração") { self.session.commitConfiguration() }
        }
        DispatchQueue.main.async {
            self.longRemaining = nil
            self.stackProgress = nil
            self.updateExposure()
        }
        guard let image else {
            DispatchQueue.main.async {
                self.processing -= 1
                self.message = "A exposição longa não recebeu imagem."
            }
            return
        }
        processingQueue.async {
            let output = Developer.developVideoImage(image, options: options)
            let keep = self.keepNeutral(output, options: options, mode: CaptureMode.longExposure.rawValue)
            Library.save(dng: nil, developed: output?.heic, tryPair: false, onSaved: keep) { error in
                dlog(error == nil ? "✅ Exposição longa salva. Total: \(Diagnostics.ms(since: t0))" : "❌ \(error!.localizedDescription)")
                DispatchQueue.main.async {
                    self.processing -= 1
                    if let thumb = output?.thumbnail { self.thumbnail = thumb }
                    if let error { self.message = error.localizedDescription }
                }
            }
        }
    }

    /// HDR: 3 RAW de uma vez (−2, 0 e +2 EV) com o bracketing do próprio sensor.
    private func captureHDR(options: DevelopOptions, started t0: CFAbsoluteTime) {
        let biases: [Float] = [-2, 0, 2]
        guard photoOutput.maxBracketedCapturePhotoCount >= biases.count else {
            dlog("⚠️ HDR: esta câmera não faz \(biases.count) fotos de bracketing")
            DispatchQueue.main.async {
                self.processing -= 1
                self.message = "Esta lente não faz HDR. Tente a 1×."
            }
            return
        }
        let brackets = biases.map { AVCaptureAutoExposureBracketedStillImageSettings.autoExposureSettings(exposureTargetBias: $0) }
        let bayer = photoOutput.availableRawPhotoPixelFormatTypes.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) }
        let settings = AVCapturePhotoBracketSettings(
            rawPixelFormatType: bayer ?? 0,
            processedFormat: bayer == nil ? [AVVideoCodecKey: AVVideoCodecType.hevc] : nil,
            bracketedSettings: brackets)
        if photoOutput.isLensStabilizationDuringBracketedCaptureSupported { settings.isLensStabilizationEnabled = true }
        if let angle = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture,
           let connection = photoOutput.connection(with: .video),
           connection.isVideoRotationAngleSupported(angle) {
            connection.videoRotationAngle = angle
        }
        dlog("HDR: bracketing \(bayer != nil ? "RAW puro" : "HEIC") \(biases.map { String(format: "%+.0f", $0) }.joined(separator: " ")) EV")
        let id = settings.uniqueID
        let delegate = BracketCaptureDelegate { result in
            self.sessionQueue.async { self.inFlight[id] = nil }
            dlog("HDR: quadros recebidos: \(Diagnostics.ms(since: t0))")
            self.process(result, mode: .hdr, options: options, started: t0)
        }
        inFlight[id] = delegate
        let accepted = attempt("Tirar o HDR") { photoOutput.capturePhoto(with: settings, delegate: delegate) }
        if !accepted {
            inFlight[id] = nil
            DispatchQueue.main.async {
                self.processing -= 1
                self.message = "O iPhone recusou o HDR nesta lente. Tente a 1×."
            }
        }
    }

    /// Revela (e junta, se for sequência) e salva na galeria.
    private func process(_ result: Result<[CapturedFrame], Error>, mode: CaptureMode, options: DevelopOptions,
                         started t0: CFAbsoluteTime, aperture: Float = 2.8, focusPoint: CGPoint? = nil,
                         extraLooks: [DevelopOptions] = []) {
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
            // Uma revelação pesada por vez: na rajada as fotos entram numa fila em vez de lotar a memória.
            // A foto simples e leve vai por outra fila e sai na frente
            let light = frames.count == 1 && (frames.first?.data.count ?? .max) < 40_000_000 && mode.stackKind == nil
                && mode != .hdr && mode != .superRes && mode != .superZoom && mode != .moon
            (light ? quickQueue : processingQueue).async {
                let output: Developer.Output?
                if mode == .hdr {
                    output = Developer.hdr(frames, options: options)
                } else if mode == .superRes {
                    output = Developer.superResolution(frames, options: options, keep: 6)
                } else if mode == .superZoom {
                    output = Developer.superResolution(frames, options: options, keep: 10)
                } else if mode == .moon {
                    output = Developer.superResolution(frames, options: options, sharpen: 0.9)
                } else if let kind = mode.stackKind {
                    output = Developer.stack(frames, kind: kind, removeOutliers: mode == .stars, robust: mode == .night,
                                             starPoints: mode == .night ? self.nightStarPoints : 0, options: options)
                } else if let first = frames.first, first.hasDepth {
                    output = Developer.developPortrait(first.data, aperture: aperture, focusPoint: focusPoint, options: options)
                } else {
                    output = frames.first.flatMap { Developer.develop($0, options: options) }
                }
                // Na foto simples o DNG vai junto; nas sequências, o DNG do primeiro quadro
                let dng = frames.first.flatMap { $0.isRaw ? $0.data : nil }
                let original = frames.first.flatMap { $0.isRaw ? nil : $0.data }
                let keepDNG = self.saveDNG
                // Foto de um quadro só: guarda o original para dar para revelar de novo depois
                let single = frames.count == 1 && mode.stackKind == nil && mode != .hdr && mode != .superRes
                let keep: ((String) -> Void)? = single ? { id in
                    if let first = frames.first {
                        SourceStore.keep(first, options: options, assetID: id, mode: mode.rawValue,
                                         aperture: aperture, focusPoint: focusPoint)
                    }
                } : self.keepNeutral(output, options: options, mode: mode.rawValue)
                defer {
                    // Três looks: depois da foto principal, a mesma foto revelada em cada look extra
                    if single, output != nil, let first = frames.first {
                        for extra in extraLooks {
                            let t1 = CFAbsoluteTimeGetCurrent()
                            guard let scene = Developer.scene(for: first, aperture: first.hasDepth ? aperture : nil, focusPoint: focusPoint),
                                  let out = Developer.finish(scene, options: extra) else { continue }
                            Library.save(dng: nil, developed: out.heic, tryPair: false) { _ in }
                            dlog("Look extra \(extra.lookName): \(Diagnostics.ms(since: t1))")
                        }
                    }
                }
                Library.save(dng: keepDNG ? dng : nil, developed: output?.heic ?? original,
                             tryPair: output?.sameSizeAsRaw ?? false, onSaved: keep) { error in
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

    /// Fotos de vários quadros (HDR, noite, panorama…): guarda uma versão neutra já juntada,
    /// para o Revelar de novo abrir a última foto qualquer que seja o modo. Roda na fila de revelação.
    private func keepNeutral(_ output: Developer.Output?, options: DevelopOptions, mode: String) -> ((String) -> Void)? {
        guard let scene = output?.scene else { return nil }
        // Depois que a foto principal já está salva: a versão neutra não atrasa a foto
        return { id in
            self.processingQueue.async {
                self.storeNeutral(scene: scene, options: options, mode: mode, assetID: id)
            }
        }
    }

    private func storeNeutral(scene: CIImage, options: DevelopOptions, mode: String, assetID id: String) {
        var neutral = options
        neutral.look = .neutro
        neutral.custom = nil
        neutral.amount = 0
        neutral.grain = 0
        neutral.hdrCompress = false
        guard let plain = Developer.finish(scene, options: neutral) else { return }
        // Já recortada e espelhada: guardada sem recorte nem espelho extra
        var stored = options
        stored.zoom = 1
        stored.mirror = false
        stored.originalAspect = true
        // A versão neutra já saiu com a exposição descontada (ETTR): não desconta de novo ao reabrir
        stored.exposureOffset = 0
        var frame = CapturedFrame(data: plain.heic, isRaw: false)
        frame.toned = true
        SourceStore.keep(frame, options: stored, assetID: id, mode: mode, aperture: 2.8, focusPoint: nil)
    }

    /// Tudo que a câmera deste iPhone oferece, para o relatório.
    func describeCapabilities(completion: @escaping (String) -> Void) {
        let settings = "- Ajustes: lente \(lens.rawValue) zoom \(zoomText) (recorte \(String(format: "%.2f", crop))), \(rawMode.rawValue), modo \(captureMode.rawValue), look \(lookName) \(Int(lookAmount * 100))% grão \(grainAmount)×, \(aspect.rawValue), " +
            "exposição \(manualExposure ? "manual ISO \(Int(selectedISO)) \(selectedShutter)s" : "auto EV \(evBias)"), " +
            "balanço \(manualWB ? "\(Int(kelvin))K" : "auto"), foco \(manualFocus ? "manual \(lensPosition)" : "auto"), " +
            "peaking \(peaking), zebra \(zebra), espelhar \(mirror), guardar DNG \(saveDNG), visor \(Int(previewAngle))°, " +
            "cor falsa \(falseColor), histograma colorido \(rgbHistogram), " +
            "congelar 1/\(Int((1 / freezeShutter).rounded()))\(freezeMax ? " máx" : "")" +
            (faceDistance.map { String(format: ", rosto a %.2f m", $0) } ?? "") + "\n"
        let extras = "- Extras: localização \(Locator.shared.enabled ? Locator.shared.statusText : "desligada"), " +
            "instalação até \(Expiration.text), economia \(idle ? "ligada agora" : "não"), visor 60 \(preview60), " +
            "estabilização \(stabilization.rawValue), proteger pele \(skinProtection), macro automático \(autoMacro), " +
            "três looks \(multiLook), filme próprio \(customLook?.name ?? "—"), modos escondidos \(hiddenModes.count)\n"
        sessionQueue.async {
            var out = settings + extras
            out += "- Originais guardados: \(SourceStore.totalBytes() / 1_048_576) MB\n"
            out += "- Kernels de revelação: \(Developer.kernelStatus)\n"
            out += "- Profundidade: entrega \(self.photoOutput.isDepthDataDeliverySupported ? "sim" : "não") · bracketing até \(self.photoOutput.maxBracketedCapturePhotoCount) fotos\n"
            let lidar = AVCaptureDevice.default(.builtInLiDARDepthCamera, for: .video, position: .back) != nil
            out += "- LiDAR: \(lidar ? "sim" : "não") · parado agora: \(self.isSteady ? "sim" : "não")\n"
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
        if output === audioOutput {
            recorder.appendAudio(sampleBuffer)
            return
        }
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        actionRecorder.append(sampleBuffer)
        let frame = CIImage(cvPixelBuffer: pixelBuffer)
        if longExposure.isRunning { longExposure.add(frame) }
        if panorama.isRunning { panorama.offer(frame) }
        if recorder.isRecording {
            recorder.append(recordingImage(frame), at: CMSampleBufferGetPresentationTimeStamp(sampleBuffer))
        }
        let every = idleThrottle ? max(renderEvery, 2) : renderEvery
        if videoFrameIndex % every == 0 { renderer.enqueue(frame) }
        lastFrameSize = CGSize(width: CVPixelBufferGetWidth(pixelBuffer), height: CVPixelBufferGetHeight(pixelBuffer))
        if !loggedBufferSize {
            loggedBufferSize = true
            dlog("Vídeo do visor chegando em \(CVPixelBufferGetWidth(pixelBuffer))×\(CVPixelBufferGetHeight(pixelBuffer))")
        }
        videoFrameIndex += 1
        if !idleThrottle, videoFrameIndex % (8 * renderEvery) == 0 { detectFace(in: frame) }
        if ettrRunning, videoFrameIndex % 10 == 5 { analyzeHighlights(frame) }
        // Retrato: máscara de pessoa para borrar o fundo no visor
        if portraitPreviewOn, videoFrameIndex % 2 == 0,
           (try? VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up).perform([personRequest])) != nil,
           let mask = personRequest.results?.first?.pixelBuffer {
            renderer.setPersonMask(CIImage(cvPixelBuffer: mask))
        }
    }

    /// ETTR: mede quanto do quadro está estourado ou quase (numa versão de 96 px).
    private func analyzeHighlights(_ frame: CIImage) {
        let scale = 96 / max(frame.extent.width, frame.extent.height)
        let small = frame.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        let e = small.extent.integral
        let w = Int(e.width), h = Int(e.height)
        guard w > 4, h > 4 else { return }
        var pixels = [UInt8](repeating: 0, count: w * h * 4)
        Developer.context.render(small, toBitmap: &pixels, rowBytes: w * 4, bounds: e, format: .RGBA8,
                                 colorSpace: CGColorSpace(name: CGColorSpace.sRGB))
        var clipped = 0, bright = 0
        for i in stride(from: 0, to: pixels.count, by: 4) {
            let peak = max(pixels[i], pixels[i + 1], pixels[i + 2])
            if peak >= 250 { clipped += 1 }
            if peak >= 225 { bright += 1 }
        }
        let n = Float(w * h)
        let clippedShare = Float(clipped) / n, brightShare = Float(bright) / n
        DispatchQueue.main.async { self.stepETTR(clipped: clippedShare, bright: brightShare) }
    }

    /// Um passo do ETTR: estourou → desce; sobrando espaço nas altas luzes → sobe.
    private func stepETTR(clipped: Float, bright: Float) {
        guard ettrActive else { return }
        var next = ettrBias
        if clipped > 0.004 {
            next -= clipped > 0.02 ? 0.4 : 0.15
        } else if bright < 0.003 {
            next += 0.1
        } else {
            return
        }
        next = min(max(next, -3), 2)
        guard abs(next - ettrBias) > 0.01 else { return }
        ettrBias = next
        renderer.options.develop = developOptions
        sessionQueue.async {
            guard let d = self.device, d.exposureMode == .continuousAutoExposure,
                  (try? d.lockForConfiguration()) != nil else { return }
            d.setExposureTargetBias(min(max(next, d.minExposureTargetBias), d.maxExposureTargetBias), completionHandler: nil)
            d.unlockForConfiguration()
        }
    }

    // MARK: - Profundidade ao vivo (Retrato)

    /// Liga a saída de profundidade na câmera do Retrato. Roda numa configuração própria, e se a câmera
    /// recusar, o Retrato continua com o desfoque pela máscara de pessoa.
    private func configureLiveDepth(_ dev: AVCaptureDevice) {
        let formats = dev.activeFormat.supportedDepthDataFormats.filter {
            let t = CMFormatDescriptionGetMediaSubType($0.formatDescription)
            return t == kCVPixelFormatType_DisparityFloat16 || t == kCVPixelFormatType_DepthFloat16
        }
        guard let best = formats.max(by: {
            CMVideoFormatDescriptionGetDimensions($0.formatDescription).width < CMVideoFormatDescriptionGetDimensions($1.formatDescription).width
        }) else {
            dlog("Retrato: \(dev.localizedName) não entrega profundidade ao vivo neste formato")
            return
        }
        let ok = attempt("Profundidade ao vivo") {
            session.beginConfiguration()
            if !session.outputs.contains(depthOutput), session.canAddOutput(depthOutput) {
                session.addOutput(depthOutput)
                depthOutput.isFilteringEnabled = true
                depthOutput.alwaysDiscardsLateDepthData = true
                depthOutput.setDelegate(self, callbackQueue: depthQueue)
            }
            if (try? dev.lockForConfiguration()) != nil {
                dev.activeDepthDataFormat = best
                dev.unlockForConfiguration()
            }
            if let c = depthOutput.connection(with: .depthData) {
                c.isEnabled = true
                depthRotated = c.isVideoRotationAngleSupported(90)
                if depthRotated { c.videoRotationAngle = 90 }
                depthMirrored = false
                if c.isVideoMirroringSupported {
                    c.automaticallyAdjustsVideoMirroring = false
                    c.isVideoMirrored = dev.position == .front && depthRotated
                    depthMirrored = c.isVideoMirrored
                }
            }
            session.commitConfiguration()
        }
        if !ok {
            // Fecha a configuração que ficou aberta e tira a saída
            attempt("Fechar a configuração") { session.commitConfiguration() }
            attempt("Tirar a profundidade ao vivo") {
                session.beginConfiguration()
                if session.outputs.contains(depthOutput) { session.removeOutput(depthOutput) }
                session.commitConfiguration()
            }
        } else {
            let d = CMVideoFormatDescriptionGetDimensions(best.formatDescription)
            dlog("Retrato: profundidade ao vivo \(d.width)×\(d.height)\(depthRotated ? "" : " (girada pelo app)")")
        }
    }

    func depthDataOutput(_ output: AVCaptureDepthDataOutput, didOutput depthData: AVDepthData,
                         timestamp: CMTime, connection: AVCaptureConnection) {
        guard portraitPreviewOn else { return }
        depthFrameIndex += 1
        guard depthFrameIndex % 2 == 0 else { return }
        let disparity = depthData.depthDataType == kCVPixelFormatType_DisparityFloat16
            ? depthData : depthData.converting(toDepthDataType: kCVPixelFormatType_DisparityFloat16)
        let buffer = disparity.depthDataMap
        // Ponto em foco: o rosto (no visor, que mostra o centro ampliado) ou um pouco acima do centro
        let viewPoint = photoPoint(fromView: portraitChoice) ?? CGPoint(x: 0.5, y: 0.45)
        var image = CIImage(cvPixelBuffer: buffer)
        let samplePoint: CGPoint
        if depthRotated {
            samplePoint = viewPoint
        } else {
            image = image.oriented(previewMirrored ? .leftMirrored : .right)
            samplePoint = sensorPoint(fromView: viewPoint)
        }
        renderer.setDepth(image, focus: Self.sampleDisparity(buffer, at: samplePoint))
    }

    /// Média da disparidade num quadradinho em volta do ponto (0…1, origem em cima à esquerda).
    private static func sampleDisparity(_ buffer: CVPixelBuffer, at p: CGPoint) -> Float {
        CVPixelBufferLockBaseAddress(buffer, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
        guard let base = CVPixelBufferGetBaseAddress(buffer) else { return 0 }
        let w = CVPixelBufferGetWidth(buffer), h = CVPixelBufferGetHeight(buffer)
        let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
        let cx = min(max(Int(p.x * CGFloat(w)), 0), w - 1), cy = min(max(Int(p.y * CGFloat(h)), 0), h - 1)
        var sum: Float = 0
        var n: Float = 0
        for y in max(0, cy - 3)...min(h - 1, cy + 3) {
            let row = (base + y * rowBytes).assumingMemoryBound(to: Float16.self)
            for x in max(0, cx - 3)...min(w - 1, cx + 3) {
                let v = Float(row[x])
                if v.isFinite, v > 0 {
                    sum += v
                    n += 1
                }
            }
        }
        return n > 0 ? sum / n : 0
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
        guard captureMode == .portrait, !manualFocus, !aeafLocked, portraitTap == nil,
              Date().timeIntervalSince(lastFaceFocus) > 1 else { return }
        lastFaceFocus = Date()
        let devicePoint = sensorPoint(fromView: CGPoint(x: rect.midX, y: rect.midY))
        let manualExposure = self.manualExposure
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if !self.cinematicActive, d.isFocusPointOfInterestSupported, d.isFocusModeSupported(.continuousAutoFocus) {
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
            self.choose(look: Look.allCases[index])
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

/// Recebe as 3 fotos do bracketing do HDR.
final class BracketCaptureDelegate: NSObject, AVCapturePhotoCaptureDelegate {
    private let completion: (Result<[CapturedFrame], Error>) -> Void
    private var frames: [CapturedFrame] = []
    private var captureError: Error?

    init(completion: @escaping (Result<[CapturedFrame], Error>) -> Void) {
        self.completion = completion
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error {
            captureError = error
            return
        }
        guard let data = photo.fileDataRepresentation() else { return }
        let bias = (photo.bracketSettings as? AVCaptureAutoExposureBracketedStillImageSettings)?.exposureTargetBias ?? 0
        frames.append(CapturedFrame(data: data, isRaw: photo.isRawPhoto, exposureBias: bias))
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishCaptureFor resolvedSettings: AVCaptureResolvedPhotoSettings, error: Error?) {
        if let error = error ?? captureError {
            completion(.failure(error))
        } else if frames.isEmpty {
            completion(.failure(RevelaError.noRawData))
        } else {
            completion(.success(frames))
        }
    }
}

enum Library {
    static func saveVideo(_ url: URL, completion: @escaping (Error?) -> Void) {
        let location = Locator.shared.current
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else { return completion(RevelaError.photosDenied) }
            PHPhotoLibrary.shared().performChanges({
                let request = PHAssetCreationRequest.forAsset()
                request.addResource(with: .video, fileURL: url, options: nil)
                request.location = location
            }, completionHandler: { _, error in completion(error) })
        }
    }

    /// Salva a foto revelada; com o DNG, tenta juntar os dois num item só (par RAW+HEIC).
    /// Se a galeria já recusou o par antes, salva separado direto.
    /// `onSaved` recebe o identificador do item criado na galeria (para achar o original depois).
    static func save(dng: Data?, developed: Data?, tryPair: Bool, location: CLLocation? = Locator.shared.current,
                     onSaved: ((String) -> Void)? = nil, completion: @escaping (Error?) -> Void) {
        guard dng != nil || developed != nil else { return completion(RevelaError.noRawData) }
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else {
                completion(RevelaError.photosDenied)
                return
            }
            let rawOptions = PHAssetResourceCreationOptions()
            rawOptions.uniformTypeIdentifier = "com.adobe.raw-image"
            let pairRefused = UserDefaults.standard.bool(forKey: "pairRefused")

            var createdID: String?
            func finished(_ error: Error?) {
                if error == nil, let createdID { onSaved?(createdID) }
                completion(error)
            }
            func saveSeparately() {
                PHPhotoLibrary.shared().performChanges({
                    if let developed {
                        let request = PHAssetCreationRequest.forAsset()
                        request.addResource(with: .photo, data: developed, options: nil)
                        request.location = location
                        createdID = request.placeholderForCreatedAsset?.localIdentifier
                    }
                    if let dng {
                        let request = PHAssetCreationRequest.forAsset()
                        request.addResource(with: .photo, data: dng, options: rawOptions)
                        request.location = location
                        if createdID == nil { createdID = request.placeholderForCreatedAsset?.localIdentifier }
                    }
                }, completionHandler: { _, error in finished(error) })
            }

            guard let developed, let dng, tryPair, !pairRefused else { return saveSeparately() }
            PHPhotoLibrary.shared().performChanges({
                let request = PHAssetCreationRequest.forAsset()
                request.addResource(with: .photo, data: developed, options: nil)
                request.addResource(with: .alternatePhoto, data: dng, options: rawOptions)
                request.location = location
                createdID = request.placeholderForCreatedAsset?.localIdentifier
            }, completionHandler: { _, error in
                guard let error else { return finished(nil) }
                createdID = nil
                // A galeria recusou o par: não tenta mais e salva os dois separados
                dlog("Par HEIC+DNG recusado (\(error.localizedDescription)); daqui em diante salvo separado")
                UserDefaults.standard.set(true, forKey: "pairRefused")
                saveSeparately()
            })
        }
    }
}

extension AVCaptureDevice {
    /// Exposição manual sem fechar o app: tempo e ISO presos ao que o formato aceita, e a câmera pode recusar.
    /// Se recusar, chama `completion` mesmo assim (a sequência continua com a exposição que estiver).
    @discardableResult
    func safeCustomExposure(seconds: Double?, iso: Float, completion: ((CMTime) -> Void)? = nil) -> Bool {
        let f = activeFormat
        guard isExposureModeSupported(.custom), iso.isFinite else {
            completion?(.invalid)
            return false
        }
        let duration: CMTime
        if let seconds, seconds.isFinite, seconds > 0 {
            duration = CMTimeClampToRange(CMTime(seconds: seconds, preferredTimescale: 1_000_000_000),
                                          range: CMTimeRange(start: f.minExposureDuration, end: f.maxExposureDuration))
        } else {
            duration = AVCaptureDevice.currentExposureDuration
        }
        let clampedISO = min(max(iso, f.minISO), f.maxISO)
        let ok = attempt("Exposição manual") {
            setExposureModeCustom(duration: duration, iso: clampedISO, completionHandler: completion)
        }
        if !ok { completion?(.invalid) }
        return ok
    }
}
