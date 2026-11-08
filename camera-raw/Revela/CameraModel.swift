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
        // 24: com todas as nítidas juntadas, o detalhe sobe com o número de fotos (laboratório: 16 +4,7 dB, 24 +5,1)
        case .superZoom: return 24
        case .night, .average: return 8
        // LUA como o SUPER ZOOM: 16 fotos rápidas de 12 MP (com 5 de 48 MP a conta de memória deixava 2 e cada uma levava 1,6 s)
        case .moon: return 16
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
        case .photo: return "Com pouca luz (ISO 320 ou mais) cada toque junta várias fotos do mesmo instante: FOTO 3×, um terço do ruído. O selo 3× no visor avisa. Com sol, uma foto de 48 MP."
        case .fast: return "Disparo sem atraso em 12 MP (HEIC, ou RAW no RAW puro). Toque várias vezes ou segure para rajada."
        case .action: return "4K a 120 fps: toque grava 1 s, segure para mais. O app salva as 8 fotos mais nítidas e o vídeo."
        case .freeze: return "Obturador rapidíssimo para congelar movimento. Precisa de muita luz; segure para rajada."
        case .portrait: return "2× a 1,5–2 m, fundo desfocado pela profundidade (LiDAR). Escolha o quanto borra acima."
        case .video: return "Vídeo 4K (1080p a 60 fps) com o look gravado junto. Toque para começar e parar."
        case .cinematic: return "Vídeo com o fundo desfocado, como o Modo Cinema do iPhone. O foco segue as pessoas; dá para mudar depois no app Fotos."
        case .dual: return "Câmera de trás e da frente juntas. Toque: foto. Segure: vídeo enquanto segura."
        case .scan: return "Scanner 3D com LiDAR."
        case .document: return "Documentos de várias páginas, sem marca d'água, num PDF só."
        case .panorama: return "Toque e gire o iPhone devagar para a direita, sem subir nem descer. Toque de novo para terminar."
        case .hdr: return "3 fotos RAW (escura, normal, clara) juntadas: céu com cor e sombra com detalhe. Segure firme."
        case .longExposure: return "Junta segundos de vídeo numa foto: Seda deixa água e nuvens lisas, Rastros desenha as luzes. Funciona na mão (o app alinha cada quadro); apoiado fica ainda mais nítido."
        case .superRes: return "8 fotos de 48 MP, todas as nítidas (pelo menos 6) alinhadas por região em fração de pixel e resolvidas juntas: até 100 MP com mais detalhe real. Segure firme; leva uns segundos."
        case .superZoom: return "Zoom de 8× a 25× na mão: 24 fotos rápidas e sem tremido; todas as nítidas são alinhadas e resolvidas juntas numa conta só, que tira o borrão sem inventar detalhe."
        case .night: return "Fotos alinhadas em fração de pixel e somadas sem fantasma, mais uma curta para os postes não estourarem. Apoiado no escuro: 1 s por foto. ✦ põe estrela nas luzes."
        case .stars: return "16 exposições de 1 s com foco no infinito, sem aviões nem satélites. Use tripé ou apoie o iPhone."
        case .moon: return "Zoom 8×, foco no infinito e exposição para a Lua. 16 fotos rápidas (fica com as 8 ou mais nítidas) juntadas no sub-pixel: mais detalhe nas crateras."
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
    case saveFailed(String)

    var errorDescription: String? {
        switch self {
        case .noRawData: return "A câmera não entregou o arquivo RAW."
        case .developFailed: return "Não foi possível revelar o RAW. O DNG foi salvo mesmo assim."
        case .photosDenied: return "Sem permissão para salvar na galeria. Libere em Ajustes → Revela → Fotos."
        case .saveFailed(let detail):
            return "A galeria não aceitou salvar (\(detail)). Confira o espaço livre do iPhone e a permissão em Ajustes → Revela → Fotos."
        }
    }

    /// Erro do sistema que vai para a tela: com a explicação em português na frente (o texto do iOS sozinho não dizia o que fazer).
    static func explained(_ error: Error) -> Error {
        if error is RevelaError { return error }
        return RevelaError.saveFailed(error.localizedDescription)
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
    /// A lente que a sessão abriu de verdade (fila da câmera). O recorte da foto sai dela, não do activeLens do main
    private var sessionLens: Lens = .wide
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
    // O que o app sabia na hora do disparo (vai no info.json do laboratório). Escrito na fila principal e lido na fila
    // da câmera: com trava (um Dictionary lido no meio da escrita derruba o app)
    private let shotLock = NSLock()
    private var storedShotContext: [String: Any] = [:]
    private var shotContext: [String: Any] {
        get { shotLock.lock(); defer { shotLock.unlock() }; return storedShotContext }
        set { shotLock.lock(); storedShotContext = newValue; shotLock.unlock() }
    }
    /// Cópia do giroscópio para a fila da câmera (o original é da fila principal)
    private let rotationLock = NSLock()
    private var sharedRotation: [Double] = []
    private let longExposure = LongExposure()
    // Vídeo
    private let movieOutput = AVCaptureMovieFileOutput()
    private let audioOutput = AVCaptureAudioDataOutput()
    private var audioInput: AVCaptureDeviceInput?
    private let recorder = VideoRecorder()
    private let dual = DualCamera()
    private let dualLock = NSLock()
    /// Último quadro da DUPLA: as duas câmeras separadas e quando chegou (CFAbsoluteTime). Apagado ao entrar e sair da
    /// DUPLA: a foto usava um quadro velho da visita anterior.
    private var latestDualFrame: (back: CIImage, front: CIImage?, arrived: CFAbsoluteTime)?
    /// Selfie do arquivo da gravação DUPLA em andamento: espelhada? e o giro do vídeo. Escrito na principal, lido na fila da dupla.
    private var dualRecordingInset: (mirrored: Bool, degrees: CGFloat) = (false, 0)
    /// Número da gravação atual do VideoRecorder: o começo atrasado de uma gravação já parada não grava escondido.
    private var recordingID = 0
    /// CINEMÁTICO: arquivo da gravação atual (um fim atrasado de outro arquivo não mexe no estado da nova).
    private var cinematicURL: URL?
    /// Lado da sessão: modo de vídeo comum, modo cinema (fundo desfocado) e câmera dupla.
    private var videoWanted = false
    private var cinematicWanted = false
    /// Com o modo cinema ligado o iPhone não deixa mexer no foco (fecharia o app).
    private var cinematicActive = false
    private var dualActive = false
    private var readoutTimer: Timer?
    /// Ligação, app no fundo, erro da câmera (ver observeInterruptions).
    private var observers: [NSObjectProtocol] = []
    /// DUPLA: ângulo da câmera de trás, para a foto e o vídeo saírem em pé com o iPhone deitado.
    private var dualRotation: AVCaptureDevice.RotationCoordinator?
    /// O CINEMÁTICO grava pelo AVCaptureMovieFileOutput; os outros pelo VideoRecorder.
    private var recordingCinematic = false
    /// Por que a última gravação parou sozinha (vai na mensagem de quando ela for salva).
    private var recordingProblem: String?
    /// Gravação: inverter o quadro na horizontal (a frente chega espelhada do visor; o espelho dos Ajustes decide).
    /// Escrito na principal, lido na fila da câmera a cada quadro.
    private let recordingFlipLock = NSLock()
    private var storedRecordingFlip = false
    private var recordingFlip: Bool {
        get { recordingFlipLock.lock(); defer { recordingFlipLock.unlock() }; return storedRecordingFlip }
        set { recordingFlipLock.lock(); storedRecordingFlip = newValue; recordingFlipLock.unlock() }
    }
    /// AÇÃO: giro (graus) e espelho do começo da gravação, para as fotos saírem em pé.
    private var actionUpright: (degrees: CGFloat, mirrored: Bool) = (0, false)
    /// VÍDEO: zoom pedido ao sensor. Escrito na principal, aplicado na fila da sessão (só o último pedido vale).
    private let sensorZoomLock = NSLock()
    private var sensorZoomWanted: CGFloat = 1
    private var sensorZoomSmooth = false
    private var sensorZoomPending = false
    /// Quadros por segundo do VÍDEO, do lado da sessão (copiado da principal ao entrar no modo e ao trocar).
    private var sessionVideoFPS = 30
    private var lastBackLens: Lens = .wide
    private var videoFrameIndex = 0
    private var facelessFrames = 0
    private var lastFaceFocus = Date.distantPast
    /// Campo de visão do lado curto da imagem (retrato), para estimar a distância do rosto.
    private var shortSideFOV: Double = 1.0
    /// Zoom do sensor nos quadros que chegam (lido na fila de vídeo): com 2× o rosto ocupa o dobro do quadro
    private var frameZoom: CGFloat = 1
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
    /// Sem @Published: na pinça e na rampa dos botões ele muda a 120 Hz e redesenhava a tela inteira a cada passo.
    /// A tela é avisada no máximo 20 vezes por segundo, e sempre com o valor final
    private(set) var zoom: CGFloat = 1 {
        didSet {
            if zoom != oldValue { announceZoom() }
            updateVideoZoom()
        }
    }
    private var zoomAnnouncePending = false
    private var lastZoomAnnounce: CFTimeInterval = 0

    private func announceZoom() {
        guard !zoomAnnouncePending else { return }
        let now = CACurrentMediaTime()
        if now - lastZoomAnnounce >= 0.05 {
            lastZoomAnnounce = now
            objectWillChange.send()
            return
        }
        zoomAnnouncePending = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
            self.zoomAnnouncePending = false
            self.lastZoomAnnounce = CACurrentMediaTime()
            self.objectWillChange.send()
        }
    }
    /// Retrato: abertura simulada (f/1.4 borra muito, f/16 quase nada).
    static let apertures: [Float] = [1.4, 2, 2.8, 4, 8, 16]
    /// f/4 de começo: desfoque bonito sem "recortado" (f/1,4 continua a um toque).
    @Published var portraitAperture: Float = 4 { didSet { updatePortraitPreview() } }
    /// Retrato: o que você tocou no visor fica nítido (no lugar do rosto). Coordenadas do visor.
    private var portraitTap: CGPoint?
    /// Retrato: a câmera aberta entrega profundidade (sem ela a foto sai sem desfoque, e o visor também não borra)
    @Published private(set) var portraitDepthReady = false

    /// O que fica nítido no Retrato, no quadro inteiro do vídeo: o ponto tocado (desfazendo o recorte do visor), senão o
    /// centro do rosto. O rosto já vem no quadro inteiro: desfazer o recorte nele também puxava o rosto para o centro no 2×
    private var portraitChoice: CGPoint? {
        if let portraitTap { return framePoint(fromView: portraitTap) }
        guard let face = faceRect else { return nil }
        return CGPoint(x: face.midX, y: face.midY)
    }

    /// Ponto do visor -> ponto do quadro inteiro do vídeo (o visor mostra o centro ampliado pelo recorte).
    private func framePoint(fromView point: CGPoint) -> CGPoint {
        let c: CGFloat = crop
        let x: CGFloat = 0.5 + (point.x - 0.5) / c
        let y: CGFloat = 0.5 + (point.y - 0.5) / c
        return CGPoint(x: x, y: y)
    }

    /// Ponto do quadro do vídeo -> ponto da foto. Na câmera da frente o visor é espelhado (a foto não); o visor fica sempre
    /// em pé e a foto gira com o iPhone (deitado, a foto sai deitada). Roda na fila da câmera, logo antes do disparo
    private func photoPoint(fromFrame point: CGPoint?) -> CGPoint? {
        guard var p = point else { return nil }
        let connection = photoOutput.connection(with: .video)
        if previewMirrored { p.x = 1 - p.x }
        let capture = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture ?? connection?.videoRotationAngle ?? previewAngle
        // Quanto a foto gira a mais que o visor (sentido horário)
        let delta = ((Int((capture - previewAngle).rounded()) % 360) + 360) % 360
        switch delta {
        case 90: p = CGPoint(x: 1 - p.y, y: p.x)
        case 180: p = CGPoint(x: 1 - p.x, y: 1 - p.y)
        case 270: p = CGPoint(x: p.y, y: 1 - p.x)
        default: break
        }
        if connection?.isVideoMirrored == true { p.x = 1 - p.x }
        return CGPoint(x: min(max(p.x, 0), 1), y: min(max(p.y, 0), 1))
    }
    // Escolhas do dia a dia guardadas entre aberturas (como a estabilização e o ETTR)
    @Published var nightTime: NightTime = NightTime(rawValue: UserDefaults.standard.string(forKey: "nightTime") ?? "") ?? .auto {
        didSet { defaults.set(nightTime.rawValue, forKey: "nightTime") }
    }
    static let longSeconds: [Double] = [1, 2, 4, 8]
    @Published var longSecondsChoice: Double = 2
    @Published var longStyle: LongExposure.Style = .silk
    /// Segundos que faltam na exposição longa (nil = parada).
    @Published var longRemaining: Double?
    @Published var rgbHistogram = UserDefaults.standard.bool(forKey: "rgbHistogram") {
        didSet { defaults.set(rgbHistogram, forKey: "rgbHistogram") }
    }
    static let videoRates = [24, 30, 60]
    @Published var videoFPS = UserDefaults.standard.object(forKey: "videoFPS") as? Int ?? 30 {
        didSet { defaults.set(videoFPS, forKey: "videoFPS") }
    }
    /// VÍDEO: resolução e quadros por segundo que a câmera aceitou de fato (ex.: "4K\n30 fps").
    @Published private(set) var videoFormatLabel = "1080p\n30 fps"
    @Published var isRecordingVideo = false
    /// CINEMÁTICO: do toque de parar até o arquivo fechar. Conta como ocupado: trocar de modo ou descansar a câmera
    /// nesse meio tirava o AVCaptureMovieFileOutput da sessão com o arquivo ainda aberto.
    @Published private(set) var recordingFinishing = false
    /// Scanner 3D aberto (a câmera normal fica parada, porque o ARKit usa o sensor).
    @Published var showScanner = false
    @Published var recordingStarted: Date?
    /// Modo cinema: abertura simulada e os limites que a câmera aceita.
    @Published var cinematicAperture: Float = 2.8
    @Published var cinematicRange: ClosedRange<Float> = 2...16
    /// Números que mudam o tempo todo: publicados à parte (ver LiveStats).
    let live = LiveStats()
    @Published var falseColor = UserDefaults.standard.bool(forKey: "falseColor") {
        didSet {
            renderer.options.falseColor = falseColor
            defaults.set(falseColor, forKey: "falseColor")
        }
    }
    @Published var nightFrames = UserDefaults.standard.object(forKey: "nightFrames") as? Int ?? 8 {
        didSet { defaults.set(nightFrames, forKey: "nightFrames") }
    }
    /// NOITE: raios nas luzes fortes (0 = sem; 6 ou 8 pontas).
    @Published var nightStarPoints = UserDefaults.standard.object(forKey: "nightStarPoints") as? Int ?? 6 {
        didSet { defaults.set(nightStarPoints, forKey: "nightStarPoints") }
    }
    /// iPhone parado (apoiado ou no tripé), pelo giroscópio.
    @Published var isSteady = false
    @Published var rawMode: RawMode = RawMode(rawValue: UserDefaults.standard.string(forKey: "rawMode") ?? "") ?? .proRAW {
        didSet { defaults.set(rawMode.rawValue, forKey: "rawMode") }
    }
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
    @Published var zebra = UserDefaults.standard.bool(forKey: "zebra") {
        didSet {
            renderer.options.zebra = zebra
            defaults.set(zebra, forKey: "zebra")
        }
    }
    @Published var peaking = UserDefaults.standard.bool(forKey: "peaking") {
        didSet {
            renderer.options.peaking = peaking
            // O macro liga (e ao sair desliga) o peaking sozinho: isso não vira preferência
            if lens != .macro, !macroTogglingPeaking { defaults.set(peaking, forKey: "peaking") }
        }
    }
    /// Troca de peaking feita pelo macro (entrando/saindo), não por você
    private var macroTogglingPeaking = false
    /// O peaking que você tinha antes de o macro ligar o dele (volta ao sair)
    private var peakingBeforeMacro = false
    @Published var loupe = false { didSet { renderer.loupe = loupe } }
    @Published var showGrid = UserDefaults.standard.object(forKey: "showGrid") as? Bool ?? true {
        didSet { defaults.set(showGrid, forKey: "showGrid") }
    }
    @Published var showLevel = UserDefaults.standard.object(forKey: "showLevel") as? Bool ?? true {
        didSet { defaults.set(showLevel, forKey: "showLevel") }
    }
    /// Foco e exposição travados (segurar o dedo no visor). Um toque solta.
    @Published var aeafLocked = false {
        // A trava acabou (toque, troca de lente, fim de sequência): o quadrado do foco não fica parado no visor
        didSet { if oldValue, !aeafLocked, focusPoint != nil { focusPoint = nil } }
    }

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
        // HEIC (RETRATO; RÁPIDO com ProRAW) já vem com a curva da Apple: expor mais claro e descontar depois só estourava
        let heic = captureMode == .portrait || (captureMode == .fast && rawMode == .proRAW)
        return ettr && !manualExposure && !heic
            && ![.video, .cinematic, .dual, .panorama, .action, .freeze, .longExposure].contains(captureMode)
    }
    /// Lido na fila de vídeo.
    private var ettrRunning = false

    // Macro
    /// Com a 1×, chegou perto demais para focar: troca sozinho para o macro (e volta ao afastar).
    @Published var autoMacro = UserDefaults.standard.object(forKey: "autoMacro") as? Bool ?? true {
        didSet { defaults.set(autoMacro, forKey: "autoMacro") }
    }
    /// Zoom dentro do macro: 1× (12 MP), 2× e 3× (recorte do sensor de 48 MP + super resolução).
    @Published var macroZoom: CGFloat = 1 {
        didSet {
            renderer.options.develop = developOptions
            updateVideoZoom()
        }
    }
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
    @Published var timerSeconds = UserDefaults.standard.integer(forKey: "timerSeconds") {
        didSet { defaults.set(timerSeconds, forKey: "timerSeconds") }
    }
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
    /// Guarda as fotos cruas de cada disparo (todas da sequência) no app Arquivos, para o laboratório do Claude.
    /// FOTO 3×: cada toque tira várias fotos do mesmo instante e junta (⅓ do ruído). Desligado = uma foto só, mais rápida
    @Published var photoFusion = UserDefaults.standard.object(forKey: "photoFusion") as? Bool ?? true {
        didSet { defaults.set(photoFusion, forKey: "photoFusion") }
    }
    @Published var labCapture = UserDefaults.standard.bool(forKey: "labCapture") {
        didSet { defaults.set(labCapture, forKey: "labCapture") }
    }
    @Published var processing = 0 {
        // Revelar de novo pediu para a câmera descansar enquanto a foto ainda saía: descansa agora
        didSet {
            if processing == 0, oldValue > 0, pauseWanted { pauseSession() }
            developingChanged(from: oldValue)
        }
    }
    /// O que está revelando agora e desde quando (aviso no visor nas revelações longas).
    @Published private(set) var developingLabel: String?
    @Published private(set) var developingSince: Date?

    private func developingChanged(from old: Int) {
        if processing > old {
            developingLabel = fusionWillTrigger ? "FOTO 3×" : (lens == .macro && captureMode == .photo ? "MACRO" : captureMode.rawValue)
        }
        if processing > 0, old <= 0 {
            developingSince = Date()
            // Foi para o fundo no meio da revelação: o iOS dá um tempo para a foto terminar de sair
            BackgroundWork.shared.begin("revelar")
        } else if processing <= 0, old > 0 {
            developingLabel = nil
            developingSince = nil
            BackgroundWork.shared.end("revelar")
        }
    }
    private var pauseWanted = false
    /// "3/7" enquanto uma sequência está sendo fotografada.
    @Published var stackProgress: String?
    /// NOITE: mira como a do iPhone. Quanto o iPhone saiu de onde estava no disparo (pontos de tela) e quando acaba
    /// Muda 10×/s: mora no `aim` (só a mira se redesenha)
    let aim = AimState()
    var aimOffset: CGSize {
        get { aim.offset }
        set { if aim.offset != newValue { aim.offset = newValue } }
    }
    @Published var nightEnd: Date?
    @Published var message: String?
    @Published var thumbnail: UIImage?

    var selectedISO: Float { isoStops[min(max(Int(isoIndex), 0), isoStops.count - 1)] }
    var selectedShutter: Double { shutterStops[min(max(Int(shutterIndex), 0), shutterStops.count - 1)] }


    /// Recorte central do sensor da câmera atual para chegar no zoom pedido.
    /// Vale para a câmera que está entregando a imagem agora (`activeLens`): enquanto a outra lente abre,
    /// o 4× já aparece como recorte da 1×, sem esperar.
    /// O que sobra para recortar depois do zoom do sensor: é o que o visor e a revelação recortam.
    /// No VÍDEO o zoom inteiro vai para o sensor e na DUPLA o quadro é o da sessão dupla: nada a recortar
    var crop: CGFloat {
        if captureMode == .video || captureMode == .dual { return 1 }
        return max(1, totalCrop / sensorZoom)
    }

    /// Recorte total em relação à lente atual (sem descontar o zoom do sensor).
    var totalCrop: CGFloat {
        if activeLens == .front { return lens == .front ? min(max(zoom, 1), 3) : 1 }
        if lens == .front { return 1 }
        let wanted = lens == .macro ? macroZoom : zoom
        return max(1, wanted / activeLens.baseZoom)
    }

    /// Zoom feito no próprio sensor (videoZoomFactor), só nos modos que saem em HEIC (RETRATO; RÁPIDO e CONGELAR com
    /// ProRAW): o 2× vem do meio do sensor de 48 MP em 12 MP de verdade, em vez de recortar 2× um HEIC de 12 MP (3 MP).
    /// O quadro do visor e a foto já chegam ampliados: os dois recortam só o que sobra (`crop`). (O VÍDEO tem o seu, contínuo)
    @Published private(set) var sensorZoom: CGFloat = 1

    // RETRATO: só onde há profundidade (1× e 2× da câmera principal com LiDAR; a da frente com TrueDepth).
    // Gravando, a lente não troca: o zoom fica no que a câmera atual alcança (abaixo disso o número mentiria)
    var minZoom: CGFloat {
        if isRecordingVideo, lens != .front, lens != .macro { return lens.baseZoom }
        return lens == .front || captureMode == .portrait ? 1 : (availableLenses.contains(.ultraWide) ? 0.5 : 1)
    }
    var maxZoom: CGFloat {
        let normal: CGFloat = lens == .front ? 3 : (captureMode == .portrait ? 2 : (availableLenses.contains(.tele) ? 25 : 10))
        if isRecordingVideo, lens != .front, lens != .macro { return min(normal, lens.baseZoom * 6) }
        return normal
    }

    /// "2,7×" para mostrar no visor.
    var zoomText: String {
        let z = lens == .macro ? macroZoom : zoom
        let text = z < 10 ? String(format: "%.1f", z) : String(format: "%.0f", z)
        return text.replacingOccurrences(of: ".0", with: "").replacingOccurrences(of: ".", with: ",") + "×"
    }

    var developOptions: DevelopOptions {
        var o = DevelopOptions(look: look, custom: customLook, amount: lookAmount, grain: grainAmount, zoom: crop, aspect: aspect, mirror: mirror)
        o.skinProtection = skinProtection
        o.steady = isSteady
        // ETTR: a câmera expôs mais claro; a revelação volta para a exposição que você escolheu
        if ettrActive { o.exposureOffset = evBias - ettrBias }
        // Estrela de dia: sol e luzes fortes (a NOITE põe a dela depois de juntar as fotos)
        if Self.dayStarModes.contains(captureMode), lens != .macro { o.starPoints = nightStarPoints }
        return o
    }

    /// Modos de uma foto só que ganham a estrela nas luzes fortes. FLASH não: o reflexo do flash (olho, óculos, vidro)
    /// é a luz estourada da foto e virava estrela
    static let dayStarModes: Set<CaptureMode> = [.photo, .fast, .freeze, .hdr]

    /// Pinça e botões. `settle` escolhe a melhor câmera física para esse zoom (no fim do gesto, para não piscar no meio).
    func setZoom(_ value: CGFloat, settle: Bool = true) {
        zoomRamp?.invalidate()
        zoomRamp = nil
        zoom = min(max(value, minZoom), maxZoom)
        if settle { selectBestLens(for: zoom) }
        renderer.options.develop = developOptions
        // O zoom do sensor muda no fim do gesto (no meio ele piscaria); para trás do que o sensor já ampliou, na hora
        if settle || totalCrop < sensorZoom - 0.01 { applySensorZoom() }
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
        // DUPLA: câmeras fixas da sessão dupla, sem zoom (trocar a lente aqui reabria a sessão principal por cima dela)
        guard captureMode != .dual else { return }
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
        // Voltando para trás do que o sensor já ampliou: o recorte não desfaz zoom, o sensor precisa voltar já
        if totalCrop < sensorZoom - 0.01 { applySensorZoom() }
    }

    private var zoomRamp: Timer?

    /// Botões de zoom: a lente nova começa a abrir na hora e o visor desliza até o zoom pedido (~0,2 s).
    func animateZoom(to value: CGFloat) {
        userInteracted()
        let target = min(max(value, minZoom), maxZoom)
        if captureMode == .portrait, lens != .front, value > maxZoom + 0.01 {
            show("RETRATO vai até 2×: a profundidade (LiDAR) só existe na câmera principal")
        }
        if lens == .macro { select(lens: .wide) }
        zoomRamp?.invalidate()
        selectBestLens(for: target)
        let start = zoom
        guard abs(start - target) > 0.01 else { setZoom(target, settle: true); return }
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
                self.applySensorZoom()
            } else if self.totalCrop < self.sensorZoom - 0.01 {
                self.applySensorZoom()
            }
        }
    }

    override init() {
        super.init()
        // Portão da GPU já na abertura: a revelação que sobrar quando o app for para o fundo espera ele voltar
        _ = ForegroundGate.shared
        Diagnostics.shared.startMonitoring()
        // A calibragem que o Claude mandou pela ponte continua valendo depois de fechar o app
        Calibration.loadSaved()
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
        // Ajudas do visor guardadas: o didSet não roda no init, então o visor recebe aqui
        renderer.options.zebra = zebra
        renderer.options.peaking = peaking
        renderer.options.falseColor = falseColor
        optionsChanged()
        renderer.onHistogram = { [weak self] bins, rgb in
            self?.live.histogram = bins
            self?.live.histogramRGB = rgb
        }
        // O arquivo do vídeo falhou no meio (disco cheio, codificador): fecha e salva o que deu
        recorder.onFailure = { [weak self] reason in self?.recordingFailed(reason) }
        observeInterruptions()
    }

    private func optionsChanged() {
        renderer.options.develop = developOptions
        // Lente trocada ou câmera reaberta: o zoom do sensor (VÍDEO) vale para a câmera nova
        updateVideoZoom()
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

    func show(_ text: String, seconds: Double = 2.6) {
        toast = text
        let current = text
        DispatchQueue.main.asyncAfter(deadline: .now() + seconds) {
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
            // A sessão de áudio fica por conta do app (prepareAudioSession): a automática calava a música de outro app
            // ao entrar no VÍDEO
            self.session.automaticallyConfiguresApplicationAudioSession = false
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

    /// NOITE na mão, como o Night Sight: o tempo de cada foto vem do quanto a mão está mexendo agora.
    /// Borrão aceito ≈ 3 px (o estabilizador da lente tira a maior parte); mão firme vai até 1/8 s, tremendo fica em 1/15 s.
    /// Era 6 px e 1/3 s, depois 4 px e 1/4 s: nas NOITEs do Alex as de 1/4 s ainda borravam (as de 1/15 s, nítidas)
    private var handheldNightSeconds: Double { Self.handheldSeconds(recentRotation, zoom: Double(zoom)) }

    private static func handheldSeconds(_ rotation: [Double], zoom: Double) -> Double {
        let sorted = rotation.sorted()
        guard !sorted.isEmpty else { return 1.0 / 8 }
        let typical = max(sorted[sorted.count / 2], 0.004)  // rad/s
        let focalPixels = 2628 * max(zoom, 1)
        // Na mão, como o modo Noite do iPhone: fotos curtas e mais delas. Nas NOITEs do Alex as de 1/15 s saíram nítidas
        // e as de 1/4 s já borravam com as mexidinhas da mão: agora de 1/15 a 1/8 s (borrão aceito 3 px)
        let seconds = min(1.0 / 8, max(1.0 / 15, 3 / (typical * focalPixels)))
        dlog(String(format: "Noite na mão: mão a %.3f rad/s → %.3f s por foto", typical, seconds))
        return seconds
    }

    /// Giroscópio: o iPhone está parado (apoiado ou no tripé)?
    private func startSteadyMonitor() {
        guard motion.isDeviceMotionAvailable, !motion.isDeviceMotionActive else { return }
        motion.deviceMotionUpdateInterval = 0.1
        motion.startDeviceMotionUpdates(to: .main) { [weak self] data, _ in
            guard let self, let r = data?.rotationRate else { return }
            self.recentRotation.append((r.x * r.x + r.y * r.y + r.z * r.z).squareRoot())
            if self.recentRotation.count > 15 { self.recentRotation.removeFirst() }
            self.rotationLock.lock(); self.sharedRotation = self.recentRotation; self.rotationLock.unlock()
            // Mira da NOITE: soma o giro desde o disparo. Câmera de trás olha para −z: girar em +x aponta para cima
            // (a mira sobe), girar em +y aponta para a esquerda. ~480 pontos por radiano na 1× em pé
            if self.nightEnd != nil {
                let k = 480 * Double(max(self.zoom, 1)) * 0.1
                let next = CGSize(width: self.aimOffset.width - r.y * k, height: self.aimOffset.height - r.x * k)
                self.aimOffset = CGSize(width: min(max(next.width, -70), 70), height: min(max(next.height, -70), 70))
            }
            let steady = self.recentRotation.count == 15 && (self.recentRotation.max() ?? 1) < 0.03
            if steady != self.isSteady { self.isSteady = steady }
            // Mexeu no iPhone: acorda. Parado e sem toque por 30 s (e nada acontecendo): economia
            if !steady, self.idle, (self.recentRotation.last ?? 0) > 0.08 { self.userInteracted() }
            let busy = self.isRecordingVideo || self.longRemaining != nil || self.panoramaProgress != nil
                || self.processing > 0 || self.stackProgress != nil || self.actionRecording
            if !self.idle, steady, !busy, Date().timeIntervalSince(self.lastInteraction) > 30 { self.setIdle(true) }
        }
    }

    func select(lens requested: Lens) {
        // RETRATO só nas câmeras com profundidade (principal com LiDAR, frente com TrueDepth): na 0,5×, 4× e macro a foto
        // saía sem desfoque nenhum enquanto o visor mostrava o fundo borrado
        let newLens: Lens = captureMode == .portrait && requested != .front ? .wide : requested
        // No meio de uma rajada ou gravação a câmera não troca (trocar ali fechava o app no CONGELAR)
        // Na DUPLA as câmeras são as da sessão dupla: reabrir a principal disputava o sensor com ela
        guard newLens != lens, !bursting, !actionRecording, stackProgress == nil, longRemaining == nil,
              panoramaProgress == nil, !isRecordingVideo, captureMode != .dual else { return }
        let old = lens
        lens = newLens
        optionsChanged()
        if newLens == .macro {
            peakingBeforeMacro = peaking
            macroTogglingPeaking = true
            peaking = true
            macroTogglingPeaking = false
            if !manualFocus { lensPosition = 0 }
        } else if old == .macro {
            // Saindo do macro o peaking volta ao que você tinha (antes desligava e gravava "desligado" como preferência)
            macroTogglingPeaking = true
            peaking = peakingBeforeMacro
            macroTogglingPeaking = false
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
            zoom = min(max(lastBackZoom, minZoom), maxZoom)
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
        // RÁPIDO com ProRAW sai em HEIC (sem ETTR, com o zoom do sensor); com RAW puro, em RAW
        if ettr { updateExposure() }
        applySensorZoom()
    }

    /// Cada cena ajusta a câmera para o que ela pede. `force`: só para as voltas internas (modo que falhou volta para a
    /// FOTO), que não podem ficar presas na guarda de "ocupado".
    func select(captureMode mode: CaptureMode, force: Bool = false) {
        // Gravando, numa sequência, contando o timer ou no meio do panorama: trocar de modo estragava o que estava
        // saindo. Espera terminar (o teste de modos troca sozinho e passa)
        if mode != captureMode, isBusy, selfTestProgress == nil, !force {
            show("Espere terminar…")
            UINotificationFeedbackGenerator().notificationOccurred(.warning)
            return
        }
        if mode == .scan {
            openScanner()
            return
        }
        if mode == .document {
            openDocumentScanner()
            return
        }
        guard mode != captureMode else { return }
        // Trocar de modo no meio de uma gravação: fecha o arquivo antes (senão ficava gravando sem fim, ou sem salvar)
        if isRecordingVideo { stopRecording() }
        if actionRecording { stopAction() }
        if panoramaProgress != nil { finishPanorama() }
        if mode == .panorama, lens != .front, totalCrop > 1.01 { setZoom(lens.baseZoom) }
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
        // VÍDEO e DUPLA: o visor mostra o quadro inteiro do arquivo e o zoom sai da revelação (antes de abrir a DUPLA,
        // o sensor volta a 1 na mesma fila)
        renderer.fitWhole = mode == .video || mode == .dual
        renderer.options.develop = developOptions
        updateVideoZoom()
        if oldMode == .video, mode != .video {
            // Saindo do VÍDEO o sensor pode estar ampliado (zoom contínuo do vídeo): volta ao que o modo novo pede
            // (1, ou o 2× dos modos HEIC), na fila da sessão antes de a DUPLA abrir
            requestedSensorZoom = 0
            applySensorZoom()
        }
        dlog("Modo: \(mode.rawValue)")
        // O macro automático é coisa da FOTO: saindo dela ele não volta sozinho e ficava preso. Na NOITE do terraço
        // do Alex (longe) a foto saiu da ultra-angular recortada 2× em vez da 1× (f/1.78, bem melhor no escuro)
        if mode != .photo, lens == .macro, macroIsAuto {
            dlog("Macro automático: desligou ao sair da FOTO")
            select(lens: .wide)
            setZoom(1, settle: false)
        }
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
            let lens = self.lens, raw = rawMode, fps = videoFPS
            sessionQueue.async {
                self.depthWanted = wantsDepth
                self.hdrWanted = wantsHDR
                self.videoWanted = wantsVideo
                self.cinematicWanted = wantsCinematic
                self.sessionVideoFPS = fps
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
        applySensorZoom()

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
        // Sem profundidade a foto sai sem desfoque: o visor também não borra (antes mostrava um fundo que não vinha)
        renderer.portraitBlur = on && portraitDepthReady ? 2.8 / portraitAperture : 0
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
        // DUPLA ligada: as câmeras estão na sessão dupla e reabrir aqui disputava o sensor com ela.
        // Os pedidos (videoWanted…) já ficaram guardados; a saída da DUPLA reabre com eles
        guard !dualActive else {
            dlog("Sessão principal: reabertura adiada (DUPLA ligada)")
            return
        }
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
        // VÍDEO: formato do sensor escolhido de propósito (o preset 1080p travava em 30 fps). Sem um que sirva, fica o preset
        let videoChoice = videoWanted && !cinematicWanted ? videoFormat(for: dev, fps: sessionVideoFPS) : nil
        if videoChoice != nil { session.sessionPreset = .inputPriority }
        session.addInput(input)
        if (try? dev.lockForConfiguration()) != nil {
            attempt("Formato e zoom do vídeo") {
                if let videoChoice { dev.activeFormat = videoChoice }
                // Fora do VÍDEO o zoom é recorte da revelação: o sensor volta a 1 (o objeto da câmera guarda o zoom do VÍDEO)
                if !videoWanted, dev.videoZoomFactor != 1 { dev.videoZoomFactor = 1 }
            }
            dev.unlockForConfiguration()
        }
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
            if AVCaptureDevice.authorizationStatus(for: .audio) == .authorized { Self.prepareAudioSession() }
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
        sessionLens = lens
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
                    self.select(captureMode: .photo, force: true)
                    self.message = "A câmera recusou esse modo agora. Voltei para FOTO; o relatório mostra o motivo."
                }
            }
            return
        }
        dlog("Configuração aceita")
        // O microfone já saiu da captura: fora dos modos de vídeo a sessão de áudio é solta
        if !videoWanted, !cinematicWanted { Self.releaseAudioSession() }
        if formatWasSpecial {
            // O modo anterior (AÇÃO, CINEMÁTICO, DUPLA) mexeu no formato: o tamanho da foto é refeito agora
            formatWasSpecial = false
            applyRawMode(mode)
        }

        loggedBufferSize = false
        if videoWanted { applyVideoFormat() }
        applyStabilization()
        applyPreviewRate()
        if depthWanted, !cinematicWanted { configureLiveDepth(dev) }
        // O zoom do sensor fica guardado na câmera (ela volta com o 2× de antes): começa em 1 e o main pede o do modo
        if dev.videoZoomFactor != 1, (try? dev.lockForConfiguration()) != nil {
            attempt("Zoom do sensor") { dev.videoZoomFactor = 1 }
            dev.unlockForConfiguration()
        }
        frameZoom = max(dev.videoZoomFactor, 1)
        // Cada câmera é montada num ângulo; o coordinator, com a camada do visor, diz o ângulo certo
        DispatchQueue.main.async {
            self.activeLens = lens
            self.sensorZoom = 1
            self.requestedSensorZoom = 1
            self.optionsChanged()
            self.makeRotationCoordinator(for: dev)
            self.applySensorZoom()
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
        let opened = sessionLens
        DispatchQueue.main.async {
            self.portraitDepthReady = depth
            self.updatePortraitPreview()
            self.applySensorZoom()
            // Só avisa da câmera que ficou (no caminho para o RETRATO a sessão pode abrir antes a lente de onde se veio)
            if depth == false, self.captureMode == .portrait, self.lens == opened {
                self.show("Sem profundidade nesta câmera: o RETRATO sai sem desfoque")
            }
        }
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
            // A 1× só foca a partir de 20 cm: no limite por 1,5 s seguidos = perto demais.
            // No escuro não: o foco sem contraste para no limite e parecia "perto" (terraço do Alex, à noite)
            let dark = readoutISO >= 1600
            closeFocusTicks = lensPosition <= 0.01 && !dark ? closeFocusTicks + 1 : 0
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
        // O visor mostra o centro ampliado pelo zoom digital (e, no vídeo, o quadro encaixado com faixas)
        let zoom = crop
        let framed = fittedPoint(fromView: point)
        let sensorPoint = CGPoint(x: 0.5 + (framed.x - 0.5) / zoom, y: 0.5 + (framed.y - 0.5) / zoom)
        let devicePoint = self.sensorPoint(fromView: sensorPoint)
        let manualFocus = self.manualFocus
        let manualExposure = self.manualExposure
        // Vídeo: foco contínuo naquele ponto. O .autoFocus focava uma vez e travava ali enquanto a cena mudava
        let videoLike = [CaptureMode.video, .action, .dual].contains(captureMode)
        let focusMode: AVCaptureDevice.FocusMode = videoLike ? .continuousAutoFocus : .autoFocus
        sessionQueue.async {
            guard let d = self.device, (try? d.lockForConfiguration()) != nil else { return }
            defer { d.unlockForConfiguration() }
            if !manualFocus, !self.cinematicActive, d.isFocusPointOfInterestSupported, d.isFocusModeSupported(focusMode) {
                d.focusPointOfInterest = devicePoint
                d.focusMode = focusMode
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

    /// Cada contagem tem um número: cancelar e começar outra no mesmo segundo não deixa a antiga contar junto.
    private var countdownRun = 0

    /// Toque no botão durante a contagem do timer: cancela.
    func cancelCountdown() {
        guard countdown > 0 else { return }
        countdown = 0
        countdownRun += 1
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
        show("Timer cancelado")
    }

    private func tick() {
        let run = countdownRun
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            guard self.countdown > 0, run == self.countdownRun else { return }
            self.countdown -= 1
            if self.countdown == 0 { self.capture() } else {
                UIImpactFeedbackGenerator(style: .light).impactOccurred()
                self.tick()
            }
        }
    }

    // MARK: - Segurar o botão: rajada e AÇÃO

    /// O disparo já saiu no toque (modos em que segurar não faz nada): soltar não dispara de novo
    private var firedOnPress = false

    func beginHold() {
        // Toque durante a contagem do timer: cancela a foto
        if countdown > 0 {
            cancelCountdown()
            return
        }
        // Sequência ainda saindo: o toque não vale (vibra avisando, em vez de ignorar calado)
        if stackProgress != nil, !holding {
            UINotificationFeedbackGenerator().notificationOccurred(.warning)
            return
        }
        guard !holding, countdown == 0, stackProgress == nil else { return }
        holding = true
        firedOnPress = false
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
        } else {
            // Segurar não faz nada neste modo: dispara já no toque (no soltar, o tempo do dedo na tela virava atraso)
            firedOnPress = true
            shutter()
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
        } else if !firedOnPress {
            shutter()
        }
        firedOnPress = false
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
        let wanted = lens == .macro ? macroZoom : zoom, shotLens = lens, ettrOn = ettrActive, ev = evBias
        sessionQueue.async {
            // No máximo 3 fotos esperando a câmera, para a rajada não engasgar
            guard self.inFlight.count < 3 else { return }
            DispatchQueue.main.async {
                self.burstCount += 1
                self.processing += 1
            }
            let t0 = CFAbsoluteTimeGetCurrent()
            let shot = self.shotOptions(options, zoom: wanted, lens: shotLens, ettr: ettrOn, ev: ev)
            self.captureRAW(forStack: false, fast: true) { result in
                // Rajada: o original não fica guardado (60 fotos encheriam os 12 lugares do Revelar de novo)
                self.process(result.map { [$0] }, mode: mode, options: shot, started: t0, keepOriginal: false)
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
        if let free = Self.freeDiskBytes(), free < 300 * 1_048_576 {
            message = "Quase sem espaço no iPhone (\(free / 1_048_576) MB livres). Libere espaço para usar a AÇÃO."
            return
        }
        actionRecording = true
        let started = Date()
        actionRecordingStarted = started
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        // iPhone deitado: o vídeo gira na reprodução e as fotos saem em pé (a frente chega espelhada: giro ao contrário)
        let mirrored = activeLens == .front
        let degrees = captureDelta
        actionUpright = (degrees, mirrored)
        // O vídeo segue o espelho dos Ajustes, como as fotos e o VÍDEO: o quadro (espelhado só na frente) é virado na
        // reprodução quando não bate com o espelho. Antes a frente saía sempre espelhada e as fotos não
        let rotation = Self.playbackRotation(degrees: degrees, mirrored: mirror)
        let transform = mirrored != mirror ? CGAffineTransform(scaleX: -1, y: 1).concatenating(rotation) : rotation
        videoQueue.async { self.actionRecorder.start(transform: transform) }
        // Segurando demais: para sozinho no limite (a escolha das fotos e o arquivo cresciam sem fim)
        DispatchQueue.main.asyncAfter(deadline: .now() + ActionRecorder.maxSeconds) {
            if self.actionRecording, self.actionRecordingStarted == started { self.stopAction() }
        }
    }

    private func stopAction() {
        guard actionRecording else { return }
        actionRecording = false
        actionRecordingStarted = nil
        processing += 1
        let options = developOptions
        let t0 = CFAbsoluteTimeGetCurrent()
        let upright = actionUpright
        let properties = Self.videoPhotoProperties()
        // O app pode ir para o fundo no meio (o vídeo e as fotos ainda estão sendo salvos)
        let task = BackgroundTask("Revela: salvar AÇÃO")
        videoQueue.async {
            let duration = self.actionRecorder.duration
            self.actionRecorder.stop { url, times, scores in
                dlog(String(format: "AÇÃO: %d quadros em %.2f s (%.0f fps)", times.count, duration,
                            duration > 0 ? Double(times.count) / duration : 0))
                guard let url, !times.isEmpty else {
                    DispatchQueue.main.async {
                        self.processing -= 1
                        self.message = "Não foi possível gravar o modo AÇÃO."
                        task.end()
                    }
                    return
                }
                DispatchQueue.main.async { self.show("Escolhendo as fotos mais nítidas…") }
                self.processingQueue.async {
                    // As notas já vieram da gravação: só os escolhidos são abertos do vídeo
                    let chosen = ActionRecorder.choose(scores, frameCount: times.count, count: 8)
                    let frames = ActionRecorder.frames(in: url, at: chosen.map { times[$0] })
                    var thumb: UIImage?
                    var saved = 0
                    var denied = false
                    let group = DispatchGroup()
                    for frame in frames {
                        let image = Self.upright(CIImage(cgImage: frame), degrees: upright.degrees, unmirror: upright.mirrored)
                            .settingProperties(properties)
                        guard let output = Developer.developVideoImage(image, options: options) else { continue }
                        thumb = output.thumbnail
                        group.enter()
                        Library.save(dng: nil, developed: output.heic, tryPair: false) { error in
                            if error == nil { saved += 1 } else { denied = true }
                            group.leave()
                        }
                        // Uma por vez: as respostas da galeria chegam em outra fila
                        group.wait()
                    }
                    var videoError: Error?
                    group.enter()
                    Library.saveVideo(url) { error in
                        videoError = error
                        group.leave()
                    }
                    group.wait()
                    // Sem a galeria o vídeo não some: fica em Arquivos → Revela → Vídeos
                    let failure = videoError, savedCount = saved, anyDenied = denied, preview = thumb
                    let kept: URL? = failure == nil ? nil : Self.keepInDocuments(url)
                    if failure == nil { try? FileManager.default.removeItem(at: url) }
                    dlog("✅ AÇÃO: \(savedCount) de \(frames.count) fotos\(failure == nil ? " + vídeo" : "") salvos. Total: \(Diagnostics.ms(since: t0))")
                    DispatchQueue.main.async {
                        self.processing -= 1
                        if let preview { self.thumbnail = preview }
                        if let videoError = failure {
                            let what: String = anyDenied ? "As fotos e o vídeo não foram para a galeria" : "O vídeo não foi para a galeria"
                            let whereKept: String = kept != nil ? " O vídeo ficou em Arquivos → No meu iPhone → Revela → Vídeos." : ""
                            self.message = "\(what) (\(videoError.localizedDescription)).\(whereKept)"
                        } else {
                            self.show("\(savedCount) fotos nítidas + vídeo em câmera lenta salvos")
                        }
                        task.end()
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

    /// Fotos de uma vez (FOTO, FLASH, RETRATO) entre o toque e a revelação pronta (main). Cada uma sai sozinha da conta
    /// em 30 s, mesmo se a câmera nunca responder (senão o botão ficaria preso para sempre)
    private var pendingSingles: Set<Int> = []
    private var singleSerial = 0
    /// Disparo cuja miniatura está na tela (início do disparo): a foto revelada de um disparo antigo não cobre a mais nova
    private var shownShot: CFAbsoluteTime = 0
    /// RAW puro no zoom: o aviso sai uma vez
    private var warnedBayerZoom = false
    /// Cada disparo que segura o botão (FOTO 3×, HDR) ganha um número: o tempo-limite só solta o botão do próprio disparo
    private var busyToken = 0
    /// Último zoom do sensor pedido (main): pedir o mesmo de novo não enfileira nada
    private var requestedSensorZoom: CGFloat = 1

    /// Segura o botão enquanto as fotos chegam. Se a câmera parar no meio (ligação, Central de Controle) a resposta pode
    /// nunca vir: em 8 s solta sozinho, mas só se ainda for este disparo (antes o de um disparo velho soltava o novo)
    private func holdShutter(_ label: String) -> Int {
        busyToken &+= 1
        let token = busyToken
        stackProgress = label
        DispatchQueue.main.asyncAfter(deadline: .now() + 8) { self.releaseShutter(token, label: label) }
        return token
    }

    /// Solta o botão de um disparo (main). Se outro disparo já começou ou a sequência passou para "1/4", não mexe.
    private func releaseShutter(_ token: Int, label: String) {
        guard busyToken == token, stackProgress == label else { return }
        stackProgress = nil
    }

    /// O que só a fila da câmera sabe na hora do disparo: a lente aberta de verdade, o zoom do sensor e a exposição que a
    /// câmera estava pedindo. No main o activeLens só muda quando a troca termina: tocar no 4× e disparar logo recortava
    /// 4× a foto que já vinha da tele (16×). Roda na fila da câmera
    private func shotOptions(_ options: DevelopOptions, zoom wanted: CGFloat, lens wantedLens: Lens,
                             ettr: Bool, ev: Float) -> DevelopOptions {
        var o = options
        let open = sessionLens
        let sensor = max(device?.videoZoomFactor ?? 1, 1)
        // A mesma conta que o laboratório testa (CaptureGeometry, PrevencaoTests.testP01Geometria)
        if open == .front || wantedLens == .front {
            o.zoom = open == .front && wantedLens == .front
                ? CaptureGeometry.cropFactor(wantedZoom: wanted, captureBaseZoom: 1, front: true) : 1
        } else {
            o.zoom = CaptureGeometry.cropFactor(wantedZoom: wanted, captureBaseZoom: open.baseZoom * sensor)
        }
        // ETTR: desconta o quanto a câmera estava expondo a mais agora (no toque o valor do main podia estar atrasado)
        if ettr, let d = device, d.exposureMode != .custom {
            o.exposureOffset = ev - d.exposureTargetBias
        }
        return o
    }

    /// Zoom do sensor que o modo pede (main): só o 2× da câmera principal, nos modos que saem em HEIC.
    private var wantedSensorZoom: CGFloat {
        // RETRATO só com profundidade: sem ela a foto sai em ProRAW, e o RAW não segue o zoom do sensor do mesmo jeito
        let heic = (captureMode == .portrait && portraitDepthReady)
            || (captureMode.usesFastFormat && rawMode == .proRAW && !(captureMode == .freeze && freezeMax))
        guard heic, lens == .wide, activeLens == .wide, zoom >= 1.99 else { return 1 }
        return 2
    }

    /// Põe o zoom do sensor no que o modo pede, se o formato faz esse zoom em resolução de verdade (senão fica o recorte)
    private func applySensorZoom() {
        // No VÍDEO o zoom do sensor é contínuo (updateVideoZoom) e na DUPLA a câmera é da sessão dupla
        guard captureMode != .video, !dualActive else { return }
        let wanted = wantedSensorZoom
        guard wanted != requestedSensorZoom else { return }
        requestedSensorZoom = wanted
        let portrait = captureMode == .portrait
        sessionQueue.async {
            guard let d = self.device else { return }
            var factor = wanted
            if factor > 1 {
                let depth = portrait && self.photoOutput.isDepthDataDeliveryEnabled
                if !CameraModel.nativeZoom(factor, on: d.activeFormat, depth: depth) || factor > d.activeFormat.videoMaxZoomFactor {
                    dlog("Zoom do sensor \(Int(factor))× indisponível em \(d.localizedName)\(depth ? " com profundidade" : ""): recorte")
                    factor = 1
                }
            }
            if abs(d.videoZoomFactor - factor) > 0.001, (try? d.lockForConfiguration()) != nil {
                if attempt("Zoom do sensor", { d.videoZoomFactor = factor }) {
                    dlog("Zoom do sensor: \(String(format: "%.1f", factor))× em \(d.localizedName)")
                }
                d.unlockForConfiguration()
            }
            let applied = max(d.videoZoomFactor, 1)
            self.frameZoom = applied
            DispatchQueue.main.async {
                guard self.sensorZoom != applied else { return }
                self.sensorZoom = applied
                self.renderer.options.develop = self.developOptions
            }
        }
    }

    /// O formato entrega esse zoom em resolução de verdade (meio do sensor de 48 MP)? E, no Retrato, com profundidade
    /// (fora das faixas de profundidade o iPhone recusa o zoom ou para de mandar a profundidade)?
    /// Lido por KVC: as listas existem desde o iOS 16/17.2 e o tipo no Swift muda entre versões do SDK
    private static func nativeZoom(_ factor: CGFloat, on format: AVCaptureDevice.Format, depth: Bool) -> Bool {
        let nativeKey = "secondaryNativeResolutionZoomFactors"
        guard format.responds(to: NSSelectorFromString(nativeKey)),
              let natives = format.value(forKey: nativeKey) as? [NSNumber],
              natives.contains(where: { abs(CGFloat($0.doubleValue) - factor) < 0.01 }) else { return false }
        guard depth else { return true }
        let depthKey = "supportedVideoZoomRangesForDepthDataDelivery"
        guard format.responds(to: NSSelectorFromString(depthKey)),
              let ranges = format.value(forKey: depthKey) as? [NSObject] else { return false }
        return ranges.contains { range in
            guard let low = range.value(forKey: "minZoomFactor") as? NSNumber,
                  let high = range.value(forKey: "maxZoomFactor") as? NSNumber else { return false }
            return factor >= CGFloat(low.doubleValue) - 0.01 && factor <= CGFloat(high.doubleValue) + 0.01
        }
    }

    private func capture() {
        // Fotos de uma vez (48 MP: 75–100 MB cada até revelar) na fila: toques rápidos enfileiravam várias e o iOS fechava
        // o app por memória. No RÁPIDO e no CONGELAR (12 MP) não: lá tocar várias vezes é o modo
        if !captureMode.usesFastFormat, pendingSingles.count >= 3 {
            show("Ainda revelando as últimas fotos: um instante")
            return
        }
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        // A miniatura aparece na hora (o quadro do visor); a foto revelada troca por ela quando ficar pronta
        // (feita fora da fila principal: renderizar 1600 px ali travava o toque)
        let shotDate = Date()
        let shotStart = CFAbsoluteTimeGetCurrent()
        lastQuickPhoto = nil
        let previewOptions = renderer.options
        renderer.snapshotQueue.async { [renderer] in
            guard let quick = renderer.snapshot(maxSide: 1600, options: previewOptions) else { return }
            DispatchQueue.main.async {
                // Se a foto revelada já chegou, não troca a de verdade pela prévia
                guard self.lastShotDate == shotDate, self.processing > 0, shotStart >= self.shownShot else { return }
                self.thumbnail = quick
                self.lastQuickPhoto = quick
                self.shownShot = shotStart
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
        // Recorte e ETTR acertados na fila da câmera, com a lente que estiver aberta lá na hora (ver shotOptions)
        let wantedZoom = lens == .macro ? macroZoom : zoom, shotLens = lens, ettrOn = ettrActive, ev = evBias
        let fix: (DevelopOptions) -> DevelopOptions = { self.shotOptions($0, zoom: wantedZoom, lens: shotLens, ettr: ettrOn, ev: ev) }
        // Três looks: lidos aqui (na fila principal); rajada não entra (seriam centenas de fotos)
        let extraLooks = multiLook && !mode.holdsForBurst
            ? extraLookIDs.compactMap { self.options(swappingLookTo: $0, from: options) } : []
        if mode == .hdr {
            // Botão parado durante o bracketing (antes dava para disparar outro HDR por cima)
            let token = holdShutter("HDR")
            sessionQueue.async { self.captureHDR(options: fix(options), started: t0, token: token, extraLooks: extraLooks) }
            return
        }
        if mode == .longExposure {
            startLongExposure(options: options, started: t0, adjust: fix)
            return
        }
        if mode == .dual {
            saveDualPhoto(options: options, started: t0)
            return
        }
        // O que fica nítido no Retrato, no quadro inteiro do vídeo (vira ponto da foto na fila da câmera, com espelho e giro)
        let portraitFrame = mode == .portrait ? portraitChoice : nil
        let aperture = portraitAperture
        // Recorte com a lente para onde se está indo (o activeLens ainda pode ser a anterior)
        let targetCrop = lens == .front ? 1 : max(1, wantedZoom / lens.baseZoom)
        // FOTO 3×: várias fotos do mesmo instante, juntadas (como o Deep Fusion / HDR+). Com luz forte (ISO baixo) o
        // ruído já é mínimo e a foto única de 48 MP tem mais detalhe que a junção em 12 MP: fica a de sempre.
        // No zoom com ProRAW também: as fotos da junção são de 12 MP e o 2× virava 3 MP; a única de 48 MP dá 12 MP
        let zoomedProRAW = rawMode == .proRAW && targetCrop >= 1.5
        if mode == .photo, photoFusion, lens != .macro, lens != .front, !zoomedProRAW,
           (manualExposure ? selectedISO : readoutISO) >= CameraModel.fusionMinISO {
            let raw = rawMode
            let locks = (exposure: !manualExposure, whiteBalance: !manualWB, focus: !manualFocus)
            // Botão parado até as fotos chegarem (cada toque segurava mais 8 RAW na memória enquanto a junção corria)
            let token = holdShutter("FOTO 3×")
            sessionQueue.async {
                self.captureFusion(raw: raw, options: fix(options), locks: locks, started: t0, token: token, extraLooks: extraLooks)
            }
            return
        }
        // RAW puro no zoom: o sensor só entrega 12 MP em RAW puro, e o 2× sai recortado (3 MP)
        if rawMode == .bayer, targetCrop >= 1.5, lens != .macro, [.photo, .flash, .fast, .freeze].contains(mode), !warnedBayerZoom {
            warnedBayerZoom = true
            show("RAW puro no zoom sai recortado de 12 MP. Para mais detalhe no 2×, use ProRAW (48 MP)")
        }
        guard mode.frameCount > 1 || mode == .night else {
            let flash = mode == .flash
            let fast = mode.usesFastFormat
            let portrait = mode == .portrait
            var pending: Int?
            if !fast {
                singleSerial &+= 1
                let id = singleSerial
                pendingSingles.insert(id)
                pending = id
                DispatchQueue.main.asyncAfter(deadline: .now() + 30) { _ = self.pendingSingles.remove(id) }
            }
            let pendingShot = pending
            sessionQueue.async {
                let shot = fix(options)
                let portraitFocus = self.photoPoint(fromFrame: portraitFrame)
                self.captureRAW(forStack: false, flash: flash, fast: fast, portrait: portrait) { result in
                    dlog("RAW recebido: \(Diagnostics.ms(since: t0))")
                    self.process(result.map { [$0] }, mode: mode, options: shot, started: t0,
                                 aperture: aperture, focusPoint: portraitFocus, extraLooks: extraLooks, pendingShot: pendingShot)
                }
            }
            return
        }

        // Sequência: no foco empilhado, cada quadro com o foco um pouco mais longe
        let macroStacking = mode == .focusStack && lens == .macro
        // Escuro de verdade com o iPhone apoiado: mais fotos (cada uma de 1 s, logo abaixo)
        let veryDark = mode == .night && isSteady && nightTime == .auto && readoutISO >= 3200
        // Para o laboratório: por que o app escolheu este tempo (apoiado? quanto a mão mexia? o visor estava em quê?)
        let rotation = recentRotation.sorted()
        shotContext = [
            "lente": lens.rawValue, "tempoNoite": nightTime.rawValue, "apoiado": isSteady,
            "maoRadPorS": rotation.isEmpty ? 0 : rotation[rotation.count / 2], "maoMaxRadPorS": rotation.last ?? 0,
            "isoVisor": Double(readoutISO), "macroAutomatico": macroIsAuto,
        ]
        // NOITE na mão (Auto): fotos mais curtas, então mais delas para juntar a mesma luz (4 → 6, 8 → 12, 16 fica)
        let handheldNight = mode == .night && !isSteady && nightTime == .auto && !manualExposure
        let nightCount = veryDark ? max(nightFrames, 12) : (handheldNight ? min(16, nightFrames * 3 / 2) : nightFrames)
        let normalCount = mode == .night ? nightCount : (macroStacking ? 6 : mode.frameCount)
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
        // LUA também em 12 MP, como o SUPER ZOOM (a 8× o recorte cabe nos 12 MP e a junção dobra a resolução)
        let fullResolution = mode == .superRes || macroStacking
        let nightPlan = mode == .night && !manualExposure
        // Noite: tempo escolhido, ou no Auto 1/2 s se o iPhone está apoiado e 1/8 s na mão
        let nightSeconds = nightTime.seconds ?? (veryDark ? 1.0 : (isSteady ? 0.5 : handheldNightSeconds))
        let nightAuto = nightTime == .auto
        // Super resolução: obturador rápido (foto tremida não cria detalhe) — 1/60 na 1×, 1/120 na 4×, 1/240 a 8×…
        let fastPlan = (mode == .superRes || mode == .superZoom) && !manualExposure
        let fastSeconds = min(1.0 / 60, 1.0 / (30 * max(Double(zoom), 1)))
        let lockFocus = !manualFocus
        // LUA e FOCO EMPILHADO: todas as fotos com a mesma cor (e no foco empilhado a mesma luz; a LUA já vem com exposição
        // manual). Antes nada travava: cada foto do foco empilhado saía com um brilho e a junção marcava as emendas
        let lockPlan = (mode == .moon || mode == .focusStack) && !nightPlan && !fastPlan
        let lockExposure = mode == .focusStack && !manualExposure
        let waitForStill = mode == .superZoom || mode == .moon
        sessionQueue.async {
            let shot = fix(options)
            let run = {
                // NOITE precisa de pelo menos 4 para valer a junção; os outros modos seguem com 2
                self.shootSequence(index: 0, count: count, positions: positions, frames: [], fullResolution: fullResolution,
                                   shortLast: shortLast, handGuard: nightPlan && nightAuto && nightSeconds > 0.26,
                                   minimumFrames: mode == .night ? 4 : 2) { result in
                    dlog("Sequência de \(count) fotografada: \(Diagnostics.ms(since: t0))")
                    DispatchQueue.main.async {
                        self.stackProgress = nil
                        self.nightEnd = nil
                        self.updateFocus()
                        self.updateExposure()
                        self.updateWhiteBalance()
                    }
                    self.process(result, mode: mode, options: shot, started: t0)
                }
            }
            let begin = {
                guard nightPlan || fastPlan || lockPlan, let d = self.device, (try? d.lockForConfiguration()) != nil else { return run() }
                if lockPlan {
                    attempt("Travar cor e luz da sequência") {
                        if d.isWhiteBalanceModeSupported(.locked) { d.whiteBalanceMode = .locked }
                        if lockExposure, d.isExposureModeSupported(.locked) { d.exposureMode = .locked }
                    }
                    d.unlockForConfiguration()
                    return run()
                }
                let f = d.activeFormat
                if fastPlan || nightPlan {
                    // Todas as fotos iguais: cor e foco travados na primeira (a exposição fica fixa logo abaixo).
                    // NOITE também: numa NOITE do Alex o balanço de branco mudou 23% entre as fotos da sequência
                    // (cada uma com uma cor), e no escuro o foco procura entre uma foto e outra
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
                if nightPlan {
                    // Contagem da mira: cada foto leva o tempo dela e mais ~0,06 s de leitura
                    let total = Double(count) * (target + 0.06)
                    DispatchQueue.main.async {
                        self.aimOffset = .zero
                        self.nightEnd = Date().addingTimeInterval(total)
                    }
                }
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
    /// `minimumFrames`: se uma foto falha no meio, segue com as que já chegaram quando são pelo menos essas
    private func shootSequence(index: Int, count: Int, positions: [Float]?, frames: [CapturedFrame],
                               fullResolution: Bool = false, shortLast: Bool = false, handGuard: Bool = false,
                               minimumFrames: Int = 2,
                               completion: @escaping (Result<[CapturedFrame], Error>) -> Void) {
        guard index < count else { return completion(.success(frames)) }
        let isShort = shortLast && index == count - 1
        // NOITE com fotos longas (o iPhone parecia apoiado): se a mão mexe no meio, o resto sai no tempo de mão.
        // Na NOITE do Alex de 16 × 1 s o celular andou 350 px e todas as fotos saíram tremidas
        if handGuard, index > 0, !isShort, let d = device {
            rotationLock.lock(); let rotation = sharedRotation; rotationLock.unlock()
            // Mesmo critério do "apoiado" (abaixo de 0,03 rad/s): passou disso, já não está apoiado
            let moving = (rotation.suffix(5).max() ?? 0) > 0.035
            let current = d.exposureDuration.seconds
            let seconds = Self.handheldSeconds(rotation.suffix(10).map { $0 }, zoom: Double(zoom))
            if moving, current > seconds * 1.3, (try? d.lockForConfiguration()) != nil {
                let f = d.activeFormat
                let target = max(seconds, f.minExposureDuration.seconds)
                let iso = min(max(d.iso * Float(current / target), f.minISO), f.maxISO)
                dlog(String(format: "Noite: a mão mexeu na foto %d → %.3fs ISO %.0f nas restantes", index + 1, target, iso))
                let next = { self.shootSequence(index: index, count: count, positions: positions, frames: frames,
                                                fullResolution: fullResolution, shortLast: shortLast,
                                                minimumFrames: minimumFrames, completion: completion) }
                // O quadro longo que já estava sendo exposto precisa passar (senão a próxima ainda sai longa)
                let go = onceOnSessionQueue(timeout: 2 + target * 2 + current) {
                    self.sessionQueue.asyncAfter(deadline: .now() + current + 0.05, execute: next)
                }
                d.safeCustomExposure(seconds: target, iso: iso) { _ in go() }
                d.unlockForConfiguration()
                return
            }
        }
        let shoot = {
            self.captureRAW(forStack: !fullResolution) { result in
                switch result {
                case .failure(let error):
                    // Uma foto que falha no meio não joga fora as que já chegaram (antes a sequência inteira se perdia)
                    let normal = frames.filter { $0.exposureBias >= -1 }.count
                    if normal >= minimumFrames {
                        dlog("⚠️ Sequência: a foto \(index + 1) de \(count) falhou (\(error.localizedDescription)); seguindo com \(frames.count)")
                        completion(.success(frames))
                    } else {
                        completion(.failure(error))
                    }
                case .success(var data):
                    if isShort { data.exposureBias = -3 }
                    DispatchQueue.main.async { self.stackProgress = "\(index + 1)/\(count)" }
                    self.sessionQueue.async {
                        self.shootSequence(index: index + 1, count: count, positions: positions,
                                           frames: frames + [self.spilled(data)],
                                           fullResolution: fullResolution, shortLast: shortLast, handGuard: handGuard,
                                           minimumFrames: minimumFrames, completion: completion)
                    }
                }
            }
        }
        if isShort, let d = device, (try? d.lockForConfiguration()) != nil {
            // Mesmo ISO, 1/8 do tempo: espera a câmera aplicar e fotografa
            let f = d.activeFormat
            let long = d.exposureDuration.seconds
            let duration = max(long / 8, f.minExposureDuration.seconds)
            // Com fotos longas (1 s) o quadro que já estava sendo exposto ainda é longo: nas NOITEs do Alex a "curta"
            // saiu com 1 s. Espera esse quadro passar antes de fotografar
            let settle = long > 0.2 ? long + 0.05 : 0
            let go = onceOnSessionQueue(timeout: 2 + duration * 2 + settle) {
                if settle > 0 { self.sessionQueue.asyncAfter(deadline: .now() + settle, execute: shoot) } else { shoot() }
            }
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
            // ProRAW de uma foto (FOTO, FLASH): a junção da Apple no máximo (sem isso saía em .balanced). Nas sequências
            // fica o padrão, para as fotos saírem perto uma da outra; RAW puro é um quadro só (não tem o que priorizar)
            if AVCapturePhotoOutput.isAppleProRAWPixelFormat(format), !forStack {
                let wanted: AVCapturePhotoOutput.QualityPrioritization = fast ? .speed : .quality
                let limit = photoOutput.maxPhotoQualityPrioritization
                settings.photoQualityPrioritization = wanted.rawValue <= limit.rawValue ? wanted : limit
            }
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
        if actionRecording { stopAction() }
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
                    if d.isWhiteBalanceModeSupported(.locked) { d.whiteBalanceMode = .locked }
                    if d.isFocusModeSupported(.locked) { d.focusMode = .locked }
                }
                // Girando, o automático travado em 1/30–1/60 s borrava 20–60 px: obturador até 1/250 s, o ISO compensa (até o
                // máximo; se faltar luz, o tempo sobe só o que falta). Exposição manual = travada também
                let f = d.activeFormat
                let current = d.exposureDuration.seconds
                var seconds = min(current, 1.0 / 250)
                var iso = d.iso * Float(current / max(seconds, 1e-6))
                if iso > f.maxISO {
                    seconds = min(current, seconds * Double(iso / f.maxISO))
                    iso = f.maxISO
                }
                if current.isFinite, seconds < current * 0.95 {
                    dlog(String(format: "Panorama: %.4fs ISO %.0f → %.4fs ISO %.0f", current, d.iso, seconds, iso))
                    d.safeCustomExposure(seconds: seconds, iso: iso)
                } else {
                    attempt("Travar a luz do panorama") {
                        if d.isExposureModeSupported(.locked) { d.exposureMode = .locked }
                    }
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
                // O fim do panorama chega depois: se já trocou para AÇÃO/VÍDEO, o formato novo decidiu o tamanho dos
                // quadros (voltar ao tamanho da tela aqui deixava a AÇÃO gravando quadros pequenos)
                guard !self.specialFormatActive, !self.videoWanted, !self.dualActive else { return }
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
        if actionRecording { stopAction() }
        dlog("Scanner de documentos aberto")
        sessionQueue.async {
            if self.session.isRunning { self.session.stopRunning() }
            DispatchQueue.main.asyncAfter(deadline: .now() + (fromDual ? 0.8 : 0)) { self.showDocument = true }
        }
    }

    /// Revelar de novo aberto: a câmera descansa (bateria e GPU livres para revelar).
    func pauseSession() {
        pauseWanted = true
        // Com foto ainda saindo da câmera, parar a sessão perderia a foto (para quando ela terminar). O arquivo do
        // CINEMÁTICO fechando também (o cinematicFinished chama de novo)
        guard !isRecordingVideo, !recordingFinishing, panoramaProgress == nil, processing == 0 else { return }
        pauseWanted = false
        sessionQueue.async {
            if self.session.isRunning { self.session.stopRunning() }
            // A DUPLA roda na sessão dela: também descansa
            if self.dualActive { self.dual.pause() }
        }
    }

    func resumeSession() {
        pauseWanted = false
        sessionQueue.async {
            if self.dualActive {
                self.dual.resume()
            } else if !self.session.isRunning {
                self.session.startRunning()
            }
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
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .notDetermined:
            break
        case .authorized:
            return
        default:
            // Negado: avisa agora (antes o vídeo saía mudo sem ninguém saber por quê)
            show("Sem permissão do microfone: o vídeo vai sair sem som. Libere em Ajustes → Revela → Microfone.")
            return
        }
        AVCaptureDevice.requestAccess(for: .audio) { granted in
            dlog("Microfone: \(granted ? "liberado" : "negado (vídeo sem som)")")
            DispatchQueue.main.async {
                guard granted else {
                    self.show("Sem microfone: o vídeo vai sair sem som.")
                    return
                }
                let lens = self.lens, raw = self.rawMode
                let inDual = self.captureMode == .dual
                self.sessionQueue.async {
                    if self.dualActive {
                        // A DUPLA abriu antes da permissão (sem som): reabre com o microfone
                        guard inDual else { return }
                        Self.prepareAudioSession()
                        self.dual.stopAndRelease()
                        self.dual.start(withAudio: true)
                    } else {
                        // Reabre a sessão para incluir o microfone
                        self.setupSession(lens: lens, mode: raw)
                    }
                }
            }
        }
    }

    /// VÍDEO: formato do sensor escolhido de propósito (o preset 1080p travava em 30 fps). 4K até 30 fps; a 60 fps, 1080p:
    /// o look é revelado em cada quadro na GPU e 4K a 60 seriam 4× os pixels do 1080p60 (o arquivo engasgaria descartando
    /// quadros). 8 bits: o caminho do Core Image até o codificador é o testado. Sem binning (lê o sensor inteiro, mais nítido)
    /// e com a estabilização forte, quando houver.
    private func videoFormat(for d: AVCaptureDevice, fps: Int) -> AVCaptureDevice.Format? {
        let rate = Double(fps)
        let eightBit: [FourCharCode] = [kCVPixelFormatType_420YpCbCr8BiPlanarFullRange, kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange]
        let widths: [Int32] = fps <= 30 ? [3840, 1920] : [1920]
        func score(_ f: AVCaptureDevice.Format) -> Int {
            (f.isVideoBinned ? 0 : 2) + (f.isVideoStabilizationModeSupported(.cinematicExtended) ? 1 : 0)
        }
        for width in widths {
            let matches = d.formats.filter { f in
                let dims = CMVideoFormatDescriptionGetDimensions(f.formatDescription)
                return dims.width == width && dims.height == width * 9 / 16
                    && eightBit.contains(CMFormatDescriptionGetMediaSubType(f.formatDescription))
                    && f.videoSupportedFrameRateRanges.contains { $0.minFrameRate <= rate && rate <= $0.maxFrameRate }
            }
            if let best = matches.max(by: { score($0) < score($1) }) { return best }
        }
        dlog("⚠️ Vídeo: \(d.localizedName) sem formato 4K/1080p a \(fps) fps")
        return nil
    }

    /// Formato e quadros por segundo do VÍDEO, e mostra o que a câmera aceitou de fato. Na fila da sessão.
    private func applyVideoFormat() {
        guard videoWanted, !cinematicWanted, !dualActive, let d = device else { return }
        let fps = sessionVideoFPS
        let rate = Double(fps)
        let format = videoFormat(for: d, fps: fps)
        guard (try? d.lockForConfiguration()) != nil else { return }
        attempt("Formato e quadros do vídeo") {
            if let format, d.activeFormat != format { d.activeFormat = format }
            if d.activeFormat.videoSupportedFrameRateRanges.contains(where: { $0.minFrameRate <= rate && rate <= $0.maxFrameRate }) {
                let duration = CMTime(value: 1, timescale: CMTimeScale(fps))
                // Primeiro solta o máximo (senão o mínimo novo pode ficar acima do máximo antigo)
                d.activeVideoMaxFrameDuration = .invalid
                d.activeVideoMinFrameDuration = duration
                d.activeVideoMaxFrameDuration = duration
            } else {
                dlog("⚠️ Vídeo: \(fps) fps não disponível neste formato")
            }
        }
        d.unlockForConfiguration()
        // O formato de vídeo não é o de foto: ao voltar para a foto, o tamanho dela é refeito (como na AÇÃO)
        formatWasSpecial = true
        let dims = CMVideoFormatDescriptionGetDimensions(d.activeFormat.formatDescription)
        let frame = d.activeVideoMinFrameDuration
        let actual = frame.value > 0 ? Int((Double(frame.timescale) / Double(frame.value)).rounded()) : fps
        let short = min(dims.width, dims.height)
        let name = short >= 2160 ? "4K" : "\(short)p"
        dlog("Vídeo: sensor em \(dims.width)×\(dims.height) a \(actual) fps")
        DispatchQueue.main.async {
            self.videoFormatLabel = "\(name)\n\(actual) fps"
            if actual != fps { self.show("Esta câmera não grava a \(fps) fps neste formato: gravando a \(actual)") }
            // Formato novo: o zoom do sensor é aplicado de novo
            self.updateVideoZoom()
        }
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
        guard !isRecordingVideo else { return }
        videoFPS = fps
        sessionQueue.async {
            self.sessionVideoFPS = fps
            // 4K ↔ 1080p pode trocar o formato: o tamanho do quadro e a estabilização são refeitos
            self.loggedBufferSize = false
            self.applyVideoFormat()
            self.applyStabilization()
        }
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

    /// Quanto o iPhone está girado em relação ao visor (graus, múltiplo de 90): 0 em pé, ±90 deitado. O visor fica sempre em pé.
    private var captureDelta: CGFloat {
        guard let coordinator = rotationCoordinator else { return 0 }
        return coordinator.videoRotationAngleForHorizonLevelCapture - coordinator.videoRotationAngleForHorizonLevelPreview
    }

    /// DUPLA: o mesmo, pela câmera de trás da sessão dupla (as ligações dela ficam sempre a 90°).
    private var dualDelta: CGFloat {
        guard let coordinator = dualRotation else { return 0 }
        return coordinator.videoRotationAngleForHorizonLevelCapture - 90
    }

    /// Giro do vídeo na reprodução. Quadro espelhado: o giro vai ao contrário (espelhar inverte o sentido da rotação;
    /// a frente deitada saía de ponta-cabeça).
    private static func playbackRotation(degrees: CGFloat, mirrored: Bool) -> CGAffineTransform {
        CGAffineTransform(rotationAngle: (mirrored ? -degrees : degrees) * .pi / 180)
    }

    /// Orientação que põe em pé uma imagem girada `degrees` (o mesmo sentido do giro do vídeo).
    private static func orientation(degrees: CGFloat) -> CGImagePropertyOrientation {
        switch (Int(degrees.rounded()) % 360 + 360) % 360 {
        case 90: return .right
        case 180: return .down
        case 270: return .left
        default: return .up
        }
    }

    /// Quadro do visor -> foto em pé: desfaz o espelho da frente (a revelação espelha de novo se o espelho estiver ligado)
    /// e gira o que o iPhone estava deitado.
    private static func upright(_ image: CIImage, degrees: CGFloat, unmirror: Bool) -> CIImage {
        let straight = unmirror ? image.oriented(.upMirrored) : image
        return straight.oriented(orientation(degrees: degrees))
    }

    /// Metadados básicos das fotos tiradas de quadros de vídeo (AÇÃO, DUPLA): data, aparelho e app. Já em pé (orientação 1).
    private static func videoPhotoProperties() -> [String: Any] {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
        let stamp = formatter.string(from: Date())
        return [
            kCGImagePropertyOrientation as String: 1,
            kCGImagePropertyExifDictionary as String: [
                kCGImagePropertyExifDateTimeOriginal as String: stamp,
                kCGImagePropertyExifDateTimeDigitized as String: stamp,
            ] as [String: Any],
            kCGImagePropertyTIFFDictionary as String: [
                kCGImagePropertyTIFFMake as String: "Apple",
                kCGImagePropertyTIFFModel as String: UIDevice.current.model,
                kCGImagePropertyTIFFSoftware as String: "Revela",
                kCGImagePropertyTIFFDateTime as String: stamp,
            ] as [String: Any],
        ]
    }

    /// Sessão de áudio do app para gravar sem calar a música de outro app (a configuração automática da câmera
    /// parava o Spotify só de entrar no VÍDEO). A2DP: fone Bluetooth continua tocando com qualidade. Na fila da sessão.
    static func prepareAudioSession() {
        let audio = AVAudioSession.sharedInstance()
        do {
            try audio.setCategory(.playAndRecord, mode: .videoRecording,
                                  options: [.mixWithOthers, .defaultToSpeaker, .allowBluetoothA2DP])
            try audio.setActive(true)
            audioSessionActive = true
        } catch {
            dlog("⚠️ Sessão de áudio: \(error.localizedDescription)")
        }
    }

    /// A sessão de áudio está ativa por nós (lido e escrito na fila da sessão).
    private static var audioSessionActive = false

    /// Fora dos modos com microfone (VÍDEO, CINEMÁTICO, DUPLA) a sessão de áudio é solta: antes ficava ativa até fechar
    /// o app, segurando o microfone e a rota do som. Na fila da sessão, depois de o microfone sair da captura.
    static func releaseAudioSession() {
        guard audioSessionActive else { return }
        audioSessionActive = false
        do {
            try AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
            dlog("Sessão de áudio solta")
        } catch {
            dlog("⚠️ Sessão de áudio (soltar): \(error.localizedDescription)")
        }
    }

    /// Serviços de mídia reiniciados ou interrupção do som terminada (ligação, Siri): nos modos com microfone a sessão de
    /// áudio é configurada e ativada de novo (senão o vídeo seguinte podia sair mudo).
    private func restoreAudioSession(_ why: String) {
        guard [.video, .cinematic, .dual].contains(captureMode),
              AVCaptureDevice.authorizationStatus(for: .audio) == .authorized else { return }
        dlog("Sessão de áudio de novo: \(why)")
        sessionQueue.async { Self.prepareAudioSession() }
    }

    private static func freeDiskBytes() -> Int64? {
        let url = URL(fileURLWithPath: NSTemporaryDirectory())
        return (try? url.resourceValues(forKeys: [.volumeAvailableCapacityForImportantUsageKey]))?.volumeAvailableCapacityForImportantUsage
    }

    /// Antes de gravar: espaço livre e microfone. Sem espaço nenhum não começa (o arquivo morreria nos primeiros segundos).
    private func prepareToRecord() -> Bool {
        recordingProblem = nil
        if let free = Self.freeDiskBytes() {
            let mb = free / 1_048_576
            if mb < 300 {
                message = "Quase sem espaço no iPhone (\(mb) MB livres). Libere espaço para gravar vídeo."
                return false
            }
            if mb < 1024 { show("Pouco espaço: \(mb) MB livres, dá para poucos minutos de vídeo") }
        }
        if AVCaptureDevice.authorizationStatus(for: .audio) != .authorized {
            show("Sem permissão do microfone: o vídeo vai sair sem som (Ajustes → Revela → Microfone)")
        }
        return true
    }

    /// Ligação, outro app pegando a câmera, app indo para o fundo, erro da câmera: fecha a gravação e salva o que já foi
    /// gravado (antes o arquivo ficava aberto e se perdia).
    private func observeInterruptions() {
        let center = NotificationCenter.default
        observers.append(center.addObserver(forName: AVCaptureSession.wasInterruptedNotification, object: session,
                                            queue: .main) { [weak self] note in
            let reason = (note.userInfo?[AVCaptureSessionInterruptionReasonKey] as? NSNumber)?.intValue ?? -1
            dlog("Câmera interrompida (motivo \(reason))")
            self?.endCaptureForInterruption("a câmera foi interrompida")
        })
        observers.append(center.addObserver(forName: AVCaptureSession.runtimeErrorNotification, object: session,
                                            queue: .main) { [weak self] note in
            guard let self else { return }
            let error = note.userInfo?[AVCaptureSessionErrorKey] as? AVError
            dlog("❌ Erro da câmera: \(error?.localizedDescription ?? "?")")
            self.endCaptureForInterruption("erro da câmera")
            // Os serviços de mídia do iPhone reiniciaram: a sessão precisa ser ligada de novo
            guard let error, error.code == .mediaServicesWereReset, !self.showScanner, !self.showDocument else { return }
            self.sessionQueue.async {
                if !self.dualActive, !self.session.isRunning { self.session.startRunning() }
            }
        })
        observers.append(center.addObserver(forName: UIApplication.didEnterBackgroundNotification, object: nil,
                                            queue: .main) { [weak self] _ in
            self?.endCaptureForInterruption("o app foi para o fundo")
        })
        observers.append(center.addObserver(forName: AVAudioSession.mediaServicesWereResetNotification, object: nil,
                                            queue: .main) { [weak self] _ in
            self?.restoreAudioSession("serviços de mídia reiniciados")
        })
        observers.append(center.addObserver(forName: AVAudioSession.interruptionNotification,
                                            object: AVAudioSession.sharedInstance(), queue: .main) { [weak self] note in
            guard let raw = (note.userInfo?[AVAudioSessionInterruptionTypeKey] as? NSNumber)?.uintValue,
                  AVAudioSession.InterruptionType(rawValue: raw) == .ended else { return }
            self?.restoreAudioSession("a interrupção do som terminou")
        })
    }

    private func endCaptureForInterruption(_ why: String) {
        // O dedo pode nunca "soltar" o botão (ligação no meio da DUPLA segurada)
        holding = false
        if isRecordingVideo {
            dlog("Gravação fechada: \(why)")
            stopRecording()
        }
        if actionRecording { stopAction() }
        // Panorama no meio: fecha com o que já girou (as travas voltam e a guarda de "ocupado" solta)
        if panoramaProgress != nil { finishPanorama() }
    }

    /// O arquivo do VideoRecorder falhou no meio.
    private func recordingFailed(_ reason: String) {
        dlog("❌ Vídeo: \(reason)")
        recordingProblem = reason
        if isRecordingVideo { stopRecording() } else { message = reason }
    }

    /// Ponto do visor (0…1) -> ponto do quadro, antes do zoom digital. No VÍDEO/DUPLA o quadro aparece encaixado (faixas
    /// dos lados); nos outros ele preenche o 3:4 e, se a proporção for outra (AÇÃO em 16:9), sobra quadro fora da tela.
    private func fittedPoint(fromView p: CGPoint) -> CGPoint {
        let frame = renderer.drawnFrameSize, view = renderer.drawnViewSize
        guard frame.width > 0, frame.height > 0, view.width > 0, view.height > 0 else { return p }
        let frameAspect = frame.width / frame.height, viewAspect = view.width / view.height
        guard abs(frameAspect - viewAspect) > 0.01 else { return p }
        var q = p
        // Encaixado e mais estreito, ou preenchendo e mais largo: a diferença fica na horizontal
        if (frameAspect < viewAspect) == renderer.fitWhole {
            q.x = 0.5 + (p.x - 0.5) * viewAspect / frameAspect
        } else {
            q.y = 0.5 + (p.y - 0.5) * frameAspect / viewAspect
        }
        return CGPoint(x: min(max(q.x, 0), 1), y: min(max(q.y, 0), 1))
    }

    /// Modos em que o visor mostra o quadro inteiro do vídeo (sem a máscara da proporção da foto).
    var showsWholeFrame: Bool { [.video, .cinematic, .dual].contains(captureMode) }

    /// VÍDEO: o zoom vai para o sensor (videoZoomFactor), que recorta antes de reduzir para o 4K/1080p: detalhe cheio
    /// em vez de ampliar o quadro pronto. Fora do VÍDEO o sensor fica em 1 (as fotos recortam na revelação).
    /// Só o último pedido vale (a pinça e os botões pedem até 120 vezes por segundo). Na fila principal.
    private func updateVideoZoom() {
        // Fora do VÍDEO quem manda no zoom do sensor é o applySensorZoom (2× dos modos HEIC; 1 no resto)
        guard captureMode == .video else { return }
        let video = true
        let factor = totalCrop
        sensorZoomLock.lock()
        sensorZoomWanted = factor
        sensorZoomSmooth = video
        let post = !sensorZoomPending
        sensorZoomPending = true
        sensorZoomLock.unlock()
        if post { sessionQueue.async { self.applyVideoZoom() } }
    }

    /// Na fila da sessão.
    private func applyVideoZoom() {
        sensorZoomLock.lock()
        let factor = sensorZoomWanted, smooth = sensorZoomSmooth
        sensorZoomPending = false
        sensorZoomLock.unlock()
        // Na DUPLA a câmera de trás pode ser a mesma da sessão dupla: não mexe
        guard !dualActive, let d = device else { return }
        let top = min(d.maxAvailableVideoZoomFactor, d.activeFormat.videoMaxZoomFactor)
        let target = min(max(factor, d.minAvailableVideoZoomFactor), max(top, 1))
        guard abs(d.videoZoomFactor - target) > 0.001, (try? d.lockForConfiguration()) != nil else { return }
        attempt("Zoom do sensor") {
            // Rampa curta: a pinça fica suave no arquivo (pulos de zoom a cada quadro apareciam no vídeo)
            if smooth { d.ramp(toVideoZoomFactor: target, withRate: 10) } else { d.videoZoomFactor = target }
        }
        d.unlockForConfiguration()
    }

    private func startRecording() {
        // O arquivo do cinema anterior ainda fechando: gravar por cima dele no mesmo AVCaptureMovieFileOutput falhava
        if captureMode == .cinematic, recordingFinishing {
            show("Espere o vídeo anterior terminar de salvar")
            return
        }
        guard prepareToRecord() else { return }
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        isRecordingVideo = true
        recordingStarted = Date()
        if captureMode == .cinematic {
            recordingCinematic = true
            let angle = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture
            let url = FileManager.default.temporaryDirectory.appendingPathComponent("cinema-\(UUID().uuidString).mov")
            cinematicURL = url
            sessionQueue.async {
                if let angle, let c = self.movieOutput.connection(with: .video), c.isVideoRotationAngleSupported(angle) {
                    c.videoRotationAngle = angle
                }
                // Fragmentos de 2 s e reserva de espaço: parando no meio (disco, ligação), o arquivo continua abrindo
                self.movieOutput.movieFragmentInterval = CMTime(seconds: 2, preferredTimescale: 600)
                self.movieOutput.minFreeDiskSpaceLimit = 200 * 1_048_576
                // Sem o modo cinema montado (formato recusado) o startRecording lança exceção: o botão não pode ficar
                // vermelho gravando nada
                var ok = false
                if self.session.outputs.contains(self.movieOutput), self.movieOutput.connection(with: .video) != nil {
                    ok = attempt("Gravar no modo cinema") { self.movieOutput.startRecording(to: url, recordingDelegate: self) }
                }
                dlog(ok ? "Cinema: gravando" : "❌ Cinema: a gravação não começou")
                guard !ok else { return }
                DispatchQueue.main.async {
                    guard self.cinematicURL == url else { return }
                    self.cinematicURL = nil
                    self.recordingCinematic = false
                    self.isRecordingVideo = false
                    self.recordingStarted = nil
                    self.cinematicFinished()
                    self.message = "O vídeo no modo cinema não começou. Tente de novo ou troque de lente; o relatório mostra o motivo."
                }
            }
        } else {
            recordingCinematic = false
            recordingID += 1
            let id = recordingID
            // O arquivo sai espelhado só com o espelho dos Ajustes ligado (a frente chega espelhada do visor)
            recordingFlip = (activeLens == .front) != mirror
            let transform = Self.playbackRotation(degrees: captureDelta, mirrored: mirror)
            // Pela fila da sessão: uma troca pedida antes do toque (FOTO → VÍDEO 4K, 4K ↔ 1080p, lente) termina antes de
            // o gravador armar, e os quadros por segundo vêm da câmera como ficou (o arquivo nasce do primeiro quadro)
            sessionQueue.async {
                self.recorder.start(id: id, fps: self.sessionFrameRate(), transform: transform)
            }
        }
    }

    /// CINEMÁTICO: o arquivo fechou (ou desistiu de esperar). Revelar de novo pediu para a câmera descansar: agora pode.
    private func cinematicFinished() {
        guard recordingFinishing else { return }
        recordingFinishing = false
        if pauseWanted { pauseSession() }
    }

    /// Quadros por segundo que a câmera está entregando agora. Na fila da sessão.
    private func sessionFrameRate() -> Int {
        guard let frame = device?.activeVideoMinFrameDuration, frame.isValid, frame.value > 0 else { return sessionVideoFPS }
        return Int((Double(frame.timescale) / Double(frame.value)).rounded())
    }

    func stopRecording() {
        guard isRecordingVideo else { return }
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
        isRecordingVideo = false
        recordingStarted = nil
        if recordingCinematic {
            recordingCinematic = false
            // Até o arquivo fechar (fileOutput didFinish) conta como ocupado; se o aviso nunca vier, solta em 10 s
            recordingFinishing = true
            let url = cinematicURL
            DispatchQueue.main.asyncAfter(deadline: .now() + 10) {
                guard self.recordingFinishing, self.cinematicURL == url else { return }
                dlog("⚠️ Cinema: o arquivo não avisou que fechou em 10 s")
                self.cinematicURL = nil
                self.cinematicFinished()
            }
            sessionQueue.async { self.movieOutput.stopRecording() }
            return
        }
        processing += 1
        // O app pode estar indo para o fundo (ligação): tempo extra para fechar o arquivo e salvar
        let task = BackgroundTask("Revela: salvar vídeo")
        recorder.stop(id: recordingID) { url, _, partial in
            guard let url else {
                DispatchQueue.main.async {
                    self.processing -= 1
                    self.message = self.recordingProblem ?? "O vídeo não foi gravado."
                    self.recordingProblem = nil
                    task.end()
                }
                return
            }
            self.saveVideoFile(url, partial: partial, savedText: "Vídeo salvo na galeria") {
                self.processing -= 1
                task.end()
            }
        }
    }

    /// Salva o vídeo na galeria. Sem permissão (ou se a galeria recusar), o arquivo não é apagado: vai para
    /// Arquivos → No meu iPhone → Revela → Vídeos e o app avisa. `completion` roda na fila principal.
    private func saveVideoFile(_ url: URL, partial: Bool, savedText: String, completion: @escaping () -> Void) {
        Library.saveVideo(url) { error in
            if error == nil { try? FileManager.default.removeItem(at: url) }
            let kept: URL? = error == nil ? nil : Self.keepInDocuments(url)
            DispatchQueue.main.async {
                let problem = self.recordingProblem
                self.recordingProblem = nil
                if let error {
                    self.message = "Não deu para salvar na galeria (\(error.localizedDescription))."
                        + (kept != nil ? " O vídeo ficou em Arquivos → No meu iPhone → Revela → Vídeos." : "")
                } else if partial || problem != nil {
                    self.message = (problem ?? "A gravação parou antes da hora.") + " Salvei na galeria o que foi gravado."
                } else {
                    self.show(savedText)
                }
                completion()
            }
        }
    }

    /// Guarda o vídeo nos Documentos do app (aparecem no app Arquivos). Devolve o endereço novo.
    private static func keepInDocuments(_ url: URL) -> URL? {
        let folder = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("Vídeos", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        let stamp = ISO8601DateFormatter().string(from: Date()).replacingOccurrences(of: ":", with: "-")
        let target = folder.appendingPathComponent("video-\(stamp)-\(UUID().uuidString.prefix(4)).mov")
        do {
            try FileManager.default.moveItem(at: url, to: target)
            dlog("Vídeo guardado em Documentos/Vídeos/\(target.lastPathComponent)")
            return target
        } catch {
            dlog("❌ Não guardou o vídeo nos Documentos: \(error.localizedDescription)")
            return nil
        }
    }

    func fileOutput(_ output: AVCaptureFileOutput, didFinishRecordingTo outputFileURL: URL,
                    from connections: [AVCaptureConnection], error: Error?) {
        // O arquivo pode estar bom mesmo com erro (ex.: parou por falta de espaço ou por uma ligação)
        let finished = (error as NSError?)?.userInfo[AVErrorRecordingSuccessfullyFinishedKey] as? Bool ?? (error == nil)
        dlog("Cinema: gravação terminou\(error == nil ? "" : " com erro: \(error?.localizedDescription ?? "")")")
        DispatchQueue.main.async {
            // Fim atrasado de um arquivo antigo: salva (abaixo), mas não mexe no estado da gravação de agora
            guard outputFileURL.lastPathComponent == self.cinematicURL?.lastPathComponent else { return }
            self.cinematicURL = nil
            // Parou sozinha (disco, ligação): o botão volta
            if self.recordingCinematic {
                self.recordingCinematic = false
                self.isRecordingVideo = false
                self.recordingStarted = nil
            }
            self.cinematicFinished()
        }
        guard finished else {
            DispatchQueue.main.async { self.message = "O vídeo no modo cinema não foi gravado." }
            return
        }
        let partial = error != nil
        DispatchQueue.main.async {
            let task = BackgroundTask("Revela: salvar vídeo cinema")
            self.saveVideoFile(outputFileURL, partial: partial,
                               savedText: "Vídeo cinema salvo. No app Fotos dá para mudar o foco e o desfoque.") { task.end() }
        }
    }

    /// Quadro com o look e o zoom, do jeito que vai para o arquivo de vídeo. Na fila da câmera.
    private func recordingImage(_ frame: CIImage) -> CIImage {
        // Cópia travada: a principal muda `renderer.options` enquanto isto roda em outra fila
        var options = renderer.threadSafeOptions
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
        if recordingFlip {
            // Espelho em volta do próprio quadro
            let e = image.extent
            image = image.transformed(by: CGAffineTransform(a: -1, b: 0, c: 0, d: 1, tx: 2 * e.minX + e.width, ty: 0))
        }
        return Developer.preview(image, options: options)
    }

    private func switchDual(on: Bool) {
        guard DualCamera.isSupported else {
            if on { message = "Este iPhone não usa as duas câmeras ao mesmo tempo." }
            return
        }
        if on {
            // O ângulo da câmera de trás diz se o iPhone está deitado (a foto e o vídeo da dupla saem em pé)
            if let back = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) {
                dualRotation = AVCaptureDevice.RotationCoordinator(device: back, previewLayer: angleLayer)
            }
            dual.onFrame = { [weak self] preview, back, front, time in
                guard let self else { return }
                self.dualLock.lock()
                self.latestDualFrame = (back, front, CFAbsoluteTimeGetCurrent())
                let inset = self.dualRecordingInset
                self.dualLock.unlock()
                self.renderer.enqueue(preview)
                if self.recorder.isRecording {
                    // O arquivo: a cena de trás sem espelho e a selfie com o espelho dos Ajustes (o visor, como espelho)
                    let selfie = front.map { DualCamera.fileFront($0, mirrored: inset.mirrored, degrees: inset.degrees) }
                    self.recorder.append(self.recordingImage(DualCamera.compose(back: back, front: selfie)), at: time)
                }
            }
            dual.onAudio = { [weak self] buffer in self?.recorder.appendAudio(buffer) }
            dual.onFailure = { [weak self] in
                // Só volta se ainda estiver na DUPLA (você pode já ter trocado de modo)
                guard let self, self.captureMode == .dual else { return }
                // Timer contando, dedo segurando ou gravação: a guarda de "ocupado" barrava a volta e a mensagem já
                // dizia "Voltei para FOTO". Cancela tudo e volta mesmo assim
                if self.countdown > 0 {
                    self.countdown = 0
                    self.countdownRun += 1
                }
                self.holding = false
                if self.isRecordingVideo { self.stopRecording() }
                self.message = "A câmera dupla não abriu agora. Voltei para FOTO."
                self.select(captureMode: .photo, force: true)
            }
            // Ligação, fundo ou erro na sessão dupla: fecha a gravação e salva o que deu
            dual.onInterrupted = { [weak self] in self?.endCaptureForInterruption("a câmera dupla foi interrompida") }
            let withAudio = AVCaptureDevice.authorizationStatus(for: .audio) == .authorized
            // Quadro de uma visita anterior à DUPLA não serve para a foto nem para a gravação
            dualLock.lock()
            latestDualFrame = nil
            dualLock.unlock()
            sessionQueue.async {
                self.dualActive = true
                self.formatWasSpecial = true
                if self.session.isRunning { self.session.stopRunning() }
                if withAudio { Self.prepareAudioSession() }
                self.dual.start(withAudio: withAudio)
            }
        } else {
            dualRotation = nil
            if isRecordingVideo { stopRecording() }
            dualLock.lock()
            latestDualFrame = nil
            dualLock.unlock()
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

    /// Quadro da DUPLA de agora (até 0,5 s). Nil com a dupla ainda abrindo, parada ou descansando.
    private func freshDualFrame() -> (back: CIImage, front: CIImage?, arrived: CFAbsoluteTime)? {
        dualLock.lock()
        defer { dualLock.unlock() }
        guard let frame = latestDualFrame, CFAbsoluteTimeGetCurrent() - frame.arrived <= 0.5 else { return nil }
        return frame
    }

    private func startDualRecording(waited: Int = 0) {
        // A dupla ainda abrindo: espera o primeiro quadro enquanto o dedo segura (até ~3 s)
        guard freshDualFrame() != nil else {
            if waited >= 30 {
                show("Espere a câmera dupla abrir")
                return
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                guard self.holding, !self.isRecordingVideo, self.captureMode == .dual else { return }
                self.startDualRecording(waited: waited + 1)
            }
            return
        }
        guard prepareToRecord() else { return }
        isRecordingVideo = true
        recordingStarted = Date()
        recordingCinematic = false
        recordingID += 1
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        // A cena de trás nunca espelha; a selfie segue o espelho dos Ajustes (antes o espelho invertia o quadro todo).
        // O giro acompanha o iPhone deitado
        let degrees = dualDelta
        recordingFlip = false
        dualLock.lock()
        dualRecordingInset = (mirror, degrees)
        dualLock.unlock()
        recorder.start(id: recordingID, fps: 30, transform: Self.playbackRotation(degrees: degrees, mirrored: false))
    }

    private func saveDualPhoto(options: DevelopOptions, started t0: CFAbsoluteTime) {
        // Quadro velho (visita anterior, dupla abrindo ou descansando) saía como foto de agora
        guard let frame = freshDualFrame() else {
            processing -= 1
            show("Espere a câmera dupla abrir")
            return
        }
        var opts = options
        opts.zoom = 1
        // O quadro inteiro, como no visor e no vídeo: a proporção da foto cortava a selfie do canto
        opts.originalAspect = true
        // O espelho dos Ajustes vale só para a selfie (abaixo); a cena de trás espelhada não é a cena
        opts.mirror = false
        let degrees = dualDelta
        let selfie = frame.front.map { DualCamera.fileFront($0, mirrored: options.mirror, degrees: degrees) }
        let composite = DualCamera.compose(back: frame.back, front: selfie)
        let properties = Self.videoPhotoProperties()
        processingQueue.async {
            // Em pé com o iPhone deitado, e com data e aparelho no arquivo
            let upright = composite.oriented(Self.orientation(degrees: degrees)).settingProperties(properties)
            let output = Developer.developVideoImage(upright, options: opts)
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

    private func startLongExposure(options base: DevelopOptions, started t0: CFAbsoluteTime,
                                   adjust: @escaping (DevelopOptions) -> DevelopOptions = { $0 }) {
        let seconds = longSecondsChoice
        let style = longStyle
        // Apoiado não precisa alinhar; na mão, cada quadro é alinhado com o primeiro
        let handheld = !isSteady
        let manual = manualExposure
        stackProgress = "0 s"
        longRemaining = seconds
        dlog("Exposição longa: \(seconds) s · \(style.rawValue)\(handheld ? " · na mão (alinhando)" : " · apoiado")")
        sessionQueue.async {
            // Recorte com a lente aberta de verdade (os quadros vêm dela)
            let options = adjust(base)
            // Vídeo em resolução cheia durante a exposição, e cada quadro exposto o quadro inteiro (sem buracos no movimento)
            self.session.beginConfiguration()
            self.setPreviewSized(false)
            attempt("Salvar a configuração") { self.session.commitConfiguration() }
            if !manual, let d = self.device, (try? d.lockForConfiguration()) != nil {
                let f = d.activeFormat
                let current = d.exposureDuration.seconds
                // 1/30 s, mas nunca mais longo do que o ISO mínimo aguenta: de dia 1/30 s com o ISO preso no mínimo
                // estourava até 5 paradas. Com luz demais fica mais curto (o movimento sai menos liso)
                let longest = current * Double(d.iso) / Double(f.minISO)
                let wanted = longest.isFinite && longest > 0 ? min(1.0 / 30, longest) : 1.0 / 30
                let target = min(max(wanted, f.minExposureDuration.seconds), f.maxExposureDuration.seconds)
                let iso = min(max(d.iso * Float(current / target), f.minISO), f.maxISO)
                d.safeCustomExposure(seconds: target, iso: iso)
                d.unlockForConfiguration()
                dlog(String(format: "Exposição longa: %.4f s ISO %.0f → %.4f s ISO %.0f", current, d.iso, target, iso))
                if target < 0.8 / 30 {
                    let text = String(format: "Luz demais para 1/30 s (ficou 1/%.0f s): o movimento sai menos liso. Um filtro ND ajuda", 1 / target)
                    DispatchQueue.main.async { self.show(text) }
                }
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
        // 4×/s basta para a contagem (10×/s redesenhava a tela inteira à toa)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { self.tickLongExposure(until: end) }
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
    private func captureHDR(options: DevelopOptions, started t0: CFAbsoluteTime, token: Int = 0,
                            extraLooks: [DevelopOptions] = []) {
        let biases: [Float] = [-2, 0, 2]
        guard photoOutput.maxBracketedCapturePhotoCount >= biases.count else {
            dlog("⚠️ HDR: esta câmera não faz \(biases.count) fotos de bracketing")
            DispatchQueue.main.async {
                self.processing -= 1
                self.releaseShutter(token, label: "HDR")
                self.message = "Esta lente não faz HDR. Tente a 1×."
            }
            return
        }
        // O desvio do bracketing é absoluto: a partir do que a câmera já estava pedindo (EV do usuário, Controle da
        // Câmera ou ETTR). Com −2/0/+2 fixos o EV escolhido sumia, e com ETTR a revelação descontava o que não tinha sido
        // exposto (o HDR estourava)
        let base: Float = device.map { min(max($0.exposureTargetBias, $0.minExposureTargetBias + 2), $0.maxExposureTargetBias - 2) } ?? 0
        let brackets = biases.map { AVCaptureAutoExposureBracketedStillImageSettings.autoExposureSettings(exposureTargetBias: base + $0) }
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
        dlog("HDR: bracketing \(bayer != nil ? "RAW puro" : "HEIC") \(biases.map { String(format: "%+.0f", $0) }.joined(separator: " ")) EV" +
             (abs(base) > 0.05 ? String(format: " a partir de %+.1f", base) : ""))
        // (a revelação desconta o ETTR pelo que a câmera estava pedindo no disparo: ver shotOptions)
        let id = settings.uniqueID
        // Os quadros guardam o desvio em relação ao do meio (−2, 0, +2): é o que a junção do HDR espera
        let delegate = BracketCaptureDelegate(baseBias: base) { result in
            self.sessionQueue.async { self.inFlight[id] = nil }
            DispatchQueue.main.async { self.releaseShutter(token, label: "HDR") }
            dlog("HDR: quadros recebidos: \(Diagnostics.ms(since: t0))")
            self.process(result, mode: .hdr, options: options, started: t0, extraLooks: extraLooks)
        }
        inFlight[id] = delegate
        let accepted = attempt("Tirar o HDR") { photoOutput.capturePhoto(with: settings, delegate: delegate) }
        if !accepted {
            inFlight[id] = nil
            DispatchQueue.main.async {
                self.processing -= 1
                self.releaseShutter(token, label: "HDR")
                self.message = "O iPhone recusou o HDR nesta lente. Tente a 1×."
            }
        }
    }

    /// FOTO 3×. RAW puro: 8 fotos num disparo só (bracketing do sensor, ~0,25 s; o iPhone 17 Pro Max faz até 8).
    /// ProRAW (cada uma já vem com a junção da Apple): 4 seguidas, e a nossa junção por cima.
    private func captureFusion(raw: RawMode, options: DevelopOptions, locks: (exposure: Bool, whiteBalance: Bool, focus: Bool),
                               started t0: CFAbsoluteTime, token: Int = 0, extraLooks: [DevelopOptions] = []) {
        let bayer = photoOutput.availableRawPhotoPixelFormatTypes.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) }
        let count = min(8, photoOutput.maxBracketedCapturePhotoCount)
        if raw == .bayer, !photoOutput.isAppleProRAWEnabled, let bayer, count >= 4, let d = device {
            // Todas com a exposição que a câmera está usando agora (o automático já com o EV, o Controle da Câmera e o
            // ETTR; ou a manual). O bracketing automático com desvio 0 é absoluto: ignorava o EV e, com ETTR, a revelação
            // descontava o que não tinha sido exposto (FOTO 3× 1 parada escura)
            let duration = d.exposureDuration, iso = d.iso
            let brackets = (0..<count).map { _ in
                AVCaptureManualExposureBracketedStillImageSettings.manualExposureSettings(exposureDuration: duration, iso: iso)
            }
            let settings = AVCapturePhotoBracketSettings(rawPixelFormatType: bayer, processedFormat: nil, bracketedSettings: brackets)
            if photoOutput.isLensStabilizationDuringBracketedCaptureSupported { settings.isLensStabilizationEnabled = true }
            if let angle = rotationCoordinator?.videoRotationAngleForHorizonLevelCapture,
               let connection = photoOutput.connection(with: .video), connection.isVideoRotationAngleSupported(angle) {
                connection.videoRotationAngle = angle
            }
            dlog("FOTO 3×: \(count) RAW puro num disparo")
            let id = settings.uniqueID
            let delegate = BracketCaptureDelegate { result in
                self.sessionQueue.async {
                    self.inFlight[id] = nil
                    switch result {
                    case .success(let frames):
                        dlog("FOTO 3×: \(frames.count) fotos recebidas: \(Diagnostics.ms(since: t0))")
                        // Para o disco (mapeadas): na fila de revelação elas não ocupam a memória do app
                        let stored = frames.map(self.spilled)
                        DispatchQueue.main.async { self.releaseShutter(token, label: "FOTO 3×") }
                        self.process(.success(stored), mode: .photo, options: options, started: t0, extraLooks: extraLooks)
                    case .failure(let error):
                        // Recusa que só chega depois (no fim da captura): tenta as fotos seguidas em vez de perder a foto
                        dlog("FOTO 3×: o bracketing falhou (\(error.localizedDescription)); fotos seguidas")
                        self.fusionSequence(raw: raw, options: options, locks: locks, started: t0, extraLooks: extraLooks)
                    }
                }
            }
            inFlight[id] = delegate
            if attempt("Tirar a FOTO 3×", { photoOutput.capturePhoto(with: settings, delegate: delegate) }) { return }
            inFlight[id] = nil
            dlog("FOTO 3×: o iPhone recusou o bracketing; fotos seguidas")
        }
        fusionSequence(raw: raw, options: options, locks: locks, started: t0, extraLooks: extraLooks)
    }

    /// FOTO 3× em fotos seguidas: luz, cor e foco travados na primeira (sem isso cada foto saía com um brilho e uma cor,
    /// e a junção robusta tratava a diferença como movimento e quase não tirava ruído)
    private func fusionSequence(raw: RawMode, options: DevelopOptions, locks: (exposure: Bool, whiteBalance: Bool, focus: Bool),
                                started t0: CFAbsoluteTime, extraLooks: [DevelopOptions] = []) {
        let n = 4
        dlog("FOTO 3×: \(n) fotos seguidas (\(raw.rawValue))")
        DispatchQueue.main.async { self.stackProgress = "0/\(n)" }
        // Como estava antes de travar: no fim volta exatamente para isso. Antes voltava sempre para o automático e a trava
        // AE/AF que você tinha feito (segurar no visor) sumia sem aviso
        let locked = device
        let before = locked.map { (exposure: $0.exposureMode, whiteBalance: $0.whiteBalanceMode, focus: $0.focusMode) }
        if let d = locked, (try? d.lockForConfiguration()) != nil {
            _ = attempt("Travar a FOTO 3×") {
                if locks.exposure, d.isExposureModeSupported(.locked) { d.exposureMode = .locked }
                if locks.whiteBalance, d.isWhiteBalanceModeSupported(.locked) { d.whiteBalanceMode = .locked }
                if locks.focus, d.isFocusModeSupported(.locked) { d.focusMode = .locked }
            }
            d.unlockForConfiguration()
        }
        shootSequence(index: 0, count: n, positions: nil, frames: []) { result in
            DispatchQueue.main.async { self.stackProgress = nil }
            // Só o que era contínuo volta a ser contínuo; o que já estava travado fica travado, no mesmo ponto (os pontos de
            // foco e luz não mudaram). Na fila da câmera: a resposta de erro chega por outra fila
            self.sessionQueue.async {
                guard let d = locked, d == self.device, let before, (try? d.lockForConfiguration()) != nil else { return }
                _ = attempt("Destravar a FOTO 3×") {
                    if locks.exposure, before.exposure == .continuousAutoExposure,
                       d.isExposureModeSupported(.continuousAutoExposure) { d.exposureMode = .continuousAutoExposure }
                    if locks.whiteBalance, before.whiteBalance == .continuousAutoWhiteBalance,
                       d.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) { d.whiteBalanceMode = .continuousAutoWhiteBalance }
                    if locks.focus, before.focus == .continuousAutoFocus, !self.cinematicActive,
                       d.isFocusModeSupported(.continuousAutoFocus) { d.focusMode = .continuousAutoFocus }
                }
                d.unlockForConfiguration()
            }
            dlog("FOTO 3×: fotos recebidas: \(Diagnostics.ms(since: t0))")
            self.process(result, mode: .photo, options: options, started: t0, extraLooks: extraLooks)
        }
    }

    /// Revela (e junta, se for sequência) e salva na galeria.
    /// `keepOriginal`: guarda o original para o Revelar de novo (a rajada não guarda). `pendingShot`: o número dela na conta
    /// de fotos de uma vez esperando revelação (`pendingSingles`).
    private func process(_ result: Result<[CapturedFrame], Error>, mode: CaptureMode, options: DevelopOptions,
                         started t0: CFAbsoluteTime, aperture: Float = 2.8, focusPoint: CGPoint? = nil,
                         extraLooks: [DevelopOptions] = [], keepOriginal: Bool = true, pendingShot: Int? = nil) {
        let done: (Result<UIImage?, Error>) -> Void = { result in
            switch result {
            case .success: dlog("✅ Salvo na galeria. Total: \(Diagnostics.ms(since: t0)) · memória livre \(Diagnostics.freeMemory)")
            case .failure(let error): dlog("❌ \(error.localizedDescription)")
            }
            DispatchQueue.main.async {
                self.processing -= 1
                if let pendingShot { _ = self.pendingSingles.remove(pendingShot) }
                switch result {
                case .success(let thumb):
                    // A revelada de um disparo antigo não cobre a prévia (ou a revelada) de um disparo mais novo
                    if let thumb, t0 >= self.shownShot {
                        self.thumbnail = thumb
                        self.shownShot = t0
                    }
                case .failure(let error):
                    self.message = error.localizedDescription
                }
            }
        }
        switch result {
        case .failure(let error):
            done(.failure(error))
        case .success(let received):
            // DNG grande (48 MP, 75–100 MB) vai para o disco e volta mapeado: esperando na fila não ocupa a memória do app
            let frames = received.count == 1 && (received.first?.data.count ?? 0) >= 40_000_000 ? received.map(self.spilled) : received
            // Laboratório: as fotos cruas da sequência vão para o app Arquivos, para o Claude testar em cima delas
            if labCapture { LabCapture.save(frames, mode: mode.rawValue, options: options, extra: shotContext) }
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
                    // Pelo menos 8 das 16 (e toda nítida); a nitidez é medida onde está a Lua
                    output = Developer.superResolution(frames, options: options, keep: 8, moon: true)
                } else if mode == .photo, frames.count > 1 {
                    output = Developer.fuse(frames, options: options)
                } else if let kind = mode.stackKind {
                    output = Developer.stack(frames, kind: kind, removeOutliers: mode == .stars, robust: mode == .night,
                                             starPoints: mode == .night ? self.nightStarPoints : 0, options: options)
                } else if let first = frames.first, first.hasDepth {
                    output = Developer.developPortrait(first.data, aperture: aperture, focusPoint: focusPoint, options: options)
                } else {
                    output = frames.first.flatMap { Developer.develop($0, options: options) }
                }
                // Na foto simples o DNG vai junto; nas sequências, o DNG do quadro de exposição normal (no HDR o primeiro
                // era o de −2 EV, escuro)
                let paired = frames.first(where: { $0.exposureBias == 0 }) ?? frames.first
                let dng = paired.flatMap { $0.isRaw ? $0.data : nil }
                let original = paired.flatMap { $0.isRaw ? nil : $0.data }
                let keepDNG = self.saveDNG
                // Foto de um quadro só: guarda o original para dar para revelar de novo depois
                let single = frames.count == 1 && mode.stackKind == nil && mode != .hdr && mode != .superRes
                var keep: ((String) -> Void)? = single ? { id in
                    if let first = frames.first {
                        SourceStore.keep(first, options: options, assetID: id, mode: mode.rawValue,
                                         aperture: aperture, focusPoint: focusPoint)
                    }
                } : self.keepNeutral(output, options: options, mode: mode.rawValue)
                if !keepOriginal { keep = nil }
                defer {
                    // Três looks: depois da foto principal, a mesma cena da revelação (já com tons locais, junção ou
                    // desfoque) em cada look extra. Antes ficava de fora na FOTO 3× e no HDR, e abria o arquivo de novo
                    if let scene = output?.scene {
                        for var extra in extraLooks {
                            let t1 = CFAbsoluteTimeGetCurrent()
                            // Recorte e ETTR são os da fila da câmera (os extras foram montados no toque)
                            extra.zoom = options.zoom
                            extra.exposureOffset = options.exposureOffset
                            extra.hdrCompress = mode == .hdr
                            guard let out = Developer.finish(scene, options: extra) else { continue }
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
        neutral.starPoints = 0
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
        let settings = "- Ajustes: lente \(lens.rawValue) zoom \(zoomText) (recorte \(String(format: "%.2f", crop)), sensor \(String(format: "%.1f", sensorZoom))×), \(rawMode.rawValue), modo \(captureMode.rawValue), look \(lookName) \(Int(lookAmount * 100))% grão \(grainAmount)×, \(aspect.rawValue), " +
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
        // Ponto em foco no quadro inteiro (o toque já sem o recorte do visor; o rosto já vem assim) ou um pouco acima do centro
        let viewPoint = portraitChoice ?? CGPoint(x: 0.5, y: 0.45)
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
        let distance = 0.16 / (2 * tan(shortSideFOV / 2) / Double(frameZoom) * Double(box.width))
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
    /// Desvio que a câmera já pedia (o bracketing foi montado a partir dele): cada quadro guarda o desvio relativo
    private let baseBias: Float

    init(baseBias: Float = 0, completion: @escaping (Result<[CapturedFrame], Error>) -> Void) {
        self.baseBias = baseBias
        self.completion = completion
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error {
            captureError = error
            dlog("Bracketing: uma foto falhou (\(error.localizedDescription))")
            return
        }
        guard let data = photo.fileDataRepresentation() else { return }
        // Arredondado a 1/100: −2 + 0,3 − 0,3 não dá −2 exato em Float e o quadro "0" deixava de ser achado
        let bias = (photo.bracketSettings as? AVCaptureAutoExposureBracketedStillImageSettings)
            .map { (($0.exposureTargetBias - baseBias) * 100).rounded() / 100 } ?? 0
        frames.append(CapturedFrame(data: data, isRaw: photo.isRawPhoto, exposureBias: bias))
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishCaptureFor resolvedSettings: AVCaptureResolvedPhotoSettings, error: Error?) {
        // Uma foto ruim não perde o disparo inteiro: com 2 ou mais a junção ainda funciona
        if frames.count >= 2 {
            if let error = error ?? captureError { dlog("Bracketing: seguindo com \(frames.count) fotos (\(error.localizedDescription))") }
            completion(.success(frames))
        } else if let error = error ?? captureError {
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
            }, completionHandler: { _, error in completion(error.map(RevelaError.explained)) })
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
                // O erro do iOS vai para a tela: com a explicação em português na frente
                completion(error.map(RevelaError.explained))
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
