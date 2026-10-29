import AVFoundation
import Photos
import UIKit

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

    var id: String { rawValue }

    var deviceType: AVCaptureDevice.DeviceType {
        switch self {
        case .macro, .ultraWide: return .builtInUltraWideCamera
        case .wide, .wide2x: return .builtInWideAngleCamera
        case .tele, .tele8x: return .builtInTelephotoCamera
        }
    }

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
    case focusStack = "FOCO EMPILHADO"
    case average = "MÉDIA"

    var id: String { rawValue }

    var frameCount: Int {
        switch self {
        case .photo: return 1
        case .focusStack: return 7
        case .average: return 8
        }
    }

    var hint: String {
        switch self {
        case .photo: return ""
        case .focusStack: return "7 fotos com foco do perto ao longe, juntadas no mais nítido. Apoie o iPhone."
        case .average: return "8 fotos somadas: menos ruído à noite, ou água lisa com obturador lento."
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
    private let defaults = UserDefaults.standard

    @Published var authorized = true
    @Published var availableLenses: [Lens] = []
    @Published var lens: Lens = .wide
    @Published var rawMode: RawMode = .proRAW
    @Published var proRAWSupported = true
    @Published var captureMode: CaptureMode = .photo

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
        DevelopOptions(look: look, amount: lookAmount, grain: grainAmount, zoom: lens.zoom, aspect: aspect)
    }

    override init() {
        super.init()
        if let saved = defaults.string(forKey: "look").flatMap(Look.init(rawValue:)) { look = saved }
        if let saved = defaults.string(forKey: "aspect").flatMap(AspectRatio.init(rawValue:)) { aspect = saved }
        if defaults.object(forKey: "lookAmount") != nil { lookAmount = defaults.float(forKey: "lookAmount") }
        if defaults.object(forKey: "grainAmount") != nil { grainAmount = defaults.float(forKey: "grainAmount") }
        optionsChanged()
        renderer.onHistogram = { [weak self] bins in self?.histogram = bins }
    }

    private func optionsChanged() {
        renderer.options.develop = developOptions
        defaults.set(look.rawValue, forKey: "look")
        defaults.set(aspect.rawValue, forKey: "aspect")
        defaults.set(lookAmount, forKey: "lookAmount")
        defaults.set(grainAmount, forKey: "grainAmount")
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
            AVCaptureDevice.default($0.deviceType, for: .video, position: .back) != nil
        }
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
        // Mesma câmera física (ex.: 1× -> 2×): só muda o recorte, sem reabrir a sessão
        guard newLens.deviceType != old.deviceType else { return }
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

    func select(mode: RawMode) {
        rawMode = mode
        sessionQueue.async { self.applyRawMode(mode) }
    }

    func cycleAspect() {
        let all = AspectRatio.allCases
        aspect = all[(all.firstIndex(of: aspect)! + 1) % all.count]
    }

    private func setupSession(lens: Lens, mode: RawMode) {
        session.beginConfiguration()
        session.sessionPreset = .photo
        session.inputs.forEach { session.removeInput($0) }

        guard let dev = AVCaptureDevice.default(lens.deviceType, for: .video, position: .back)
                ?? AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: dev),
              session.canAddInput(input) else {
            session.commitConfiguration()
            post("Não foi possível abrir a câmera.")
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
        // O app é só em retrato
        if let connection = videoOutput.connection(with: .video), connection.isVideoRotationAngleSupported(90) {
            connection.videoRotationAngle = 90
        }
        if #available(iOS 18.0, *) { installCameraControls(for: dev) }
        session.commitConfiguration()

        device = dev
        rotationCoordinator = AVCaptureDevice.RotationCoordinator(device: dev, previewLayer: nil)
        applyRawMode(mode)

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
        // Sensor fica deitado: girar 90° do retrato para as coordenadas da câmera
        let devicePoint = CGPoint(x: sensorPoint.y, y: 1 - sensorPoint.x)
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
        guard mode != .photo else {
            sessionQueue.async {
                self.captureRAW(forStack: false) { result in
                    self.process(result.map { [$0] }, mode: mode, options: options)
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
        sessionQueue.async {
            self.shootSequence(index: 0, count: count, positions: positions, frames: []) { result in
                DispatchQueue.main.async {
                    self.stackProgress = nil
                    self.updateFocus()
                }
                self.process(result, mode: mode, options: options)
            }
        }
    }

    private func shootSequence(index: Int, count: Int, positions: [Float]?, frames: [Data],
                               completion: @escaping (Result<[Data], Error>) -> Void) {
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
    private func captureRAW(forStack: Bool, completion: @escaping (Result<Data, Error>) -> Void) {
        let mode = rawMode
        let types = photoOutput.availableRawPhotoPixelFormatTypes
        let format: OSType?
        if mode == .proRAW && photoOutput.isAppleProRAWEnabled {
            format = types.first { AVCapturePhotoOutput.isAppleProRAWPixelFormat($0) }
        } else {
            format = types.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) }
        }
        guard let format else {
            DispatchQueue.main.async {
                self.message = "Esta lente não oferece \(mode.rawValue). Tente outra lente ou o outro modo."
            }
            return completion(.failure(RevelaError.noRawData))
        }

        let settings = AVCapturePhotoSettings(rawPixelFormatType: format)
        if AVCapturePhotoOutput.isAppleProRAWPixelFormat(format), let d = device {
            let all = d.activeFormat.supportedMaxPhotoDimensions
            let target: CMVideoDimensions? = forStack
                ? all.filter { $0.pixels >= 11_000_000 }.min(by: { $0.pixels < $1.pixels })
                : all.max(by: { $0.pixels < $1.pixels })
            if let target, target.pixels <= photoOutput.maxPhotoDimensions.pixels {
                settings.maxPhotoDimensions = target
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
    private func process(_ result: Result<[Data], Error>, mode: CaptureMode, options: DevelopOptions) {
        let done: (Result<UIImage?, Error>) -> Void = { result in
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
                switch mode {
                case .photo: output = frames.first.flatMap { Developer.develop(dng: $0, options: options) }
                case .focusStack: output = Developer.stack(frames, kind: .focus, options: options)
                case .average: output = Developer.stack(frames, kind: .average, options: options)
                }
                // Na foto simples o DNG vai junto; nas sequências, o DNG do primeiro quadro
                Library.save(dng: frames.first, developed: output?.heic) { error in
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

    private func post(_ text: String) {
        DispatchQueue.main.async { self.message = text }
    }

    // MARK: - Visor

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        renderer.enqueue(CIImage(cvPixelBuffer: pixelBuffer))
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
    private let completion: (Result<Data, Error>) -> Void
    private var dng: Data?
    private var captureError: Error?

    init(completion: @escaping (Result<Data, Error>) -> Void) {
        self.completion = completion
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error {
            captureError = error
            return
        }
        if photo.isRawPhoto { dng = photo.fileDataRepresentation() }
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishCaptureFor resolvedSettings: AVCaptureResolvedPhotoSettings, error: Error?) {
        if let error = error ?? captureError {
            completion(.failure(error))
        } else if let dng {
            completion(.success(dng))
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
