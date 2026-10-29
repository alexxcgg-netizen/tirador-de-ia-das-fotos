import AVFoundation
import Photos
import UIKit

enum RawMode: String, CaseIterable, Identifiable {
    case proRAW = "ProRAW"
    case bayer = "RAW puro"

    var id: String { rawValue }
}

enum Lens: String, CaseIterable, Identifiable {
    case ultraWide = "0.5×"
    case wide = "1×"
    case tele = "4×"

    var id: String { rawValue }

    var deviceType: AVCaptureDevice.DeviceType {
        switch self {
        case .ultraWide: return .builtInUltraWideCamera
        case .wide: return .builtInWideAngleCamera
        case .tele: return .builtInTelephotoCamera
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

final class CameraModel: NSObject, ObservableObject {
    static let allISO: [Float] = [25, 32, 40, 50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640,
                                  800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800]
    static let allShutter: [Double] = [8000, 6400, 5000, 4000, 3200, 2500, 2000, 1600, 1250, 1000, 800, 640,
                                       500, 400, 320, 250, 200, 160, 125, 100, 80, 60, 50, 40, 30, 25, 20,
                                       15, 13, 10, 8, 6, 5, 4, 3, 2, 1].map { 1 / $0 }

    let session = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()
    private let sessionQueue = DispatchQueue(label: "revela.session")
    private var device: AVCaptureDevice?
    private var rotationCoordinator: AVCaptureDevice.RotationCoordinator?
    private var inFlight: [Int64: PhotoProcessor] = [:]
    private var readoutTimer: Timer?

    @Published var authorized = true
    @Published var availableLenses: [Lens] = []
    @Published var lens: Lens = .wide
    @Published var rawMode: RawMode = .proRAW
    @Published var proRAWSupported = true
    @Published var look: Look = .filme

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
    @Published var processing = 0
    @Published var message: String?
    @Published var thumbnail: UIImage?

    var selectedISO: Float { isoStops[min(max(Int(isoIndex), 0), isoStops.count - 1)] }
    var selectedShutter: Double { shutterStops[min(max(Int(shutterIndex), 0), shutterStops.count - 1)] }

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
            self.setupSession(lens: lens, mode: mode)
            if !self.session.isRunning { self.session.startRunning() }
        }
        startReadout()
    }

    func select(lens newLens: Lens) {
        guard newLens != lens else { return }
        lens = newLens
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
        if let dims = device?.activeFormat.supportedMaxPhotoDimensions.max(by: {
            Int($0.width) * Int($0.height) < Int($1.width) * Int($1.height)
        }) {
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
        }
    }

    // MARK: - Captura

    func capture() {
        let look = self.look
        let mode = self.rawMode
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        processing += 1

        sessionQueue.async {
            let types = self.photoOutput.availableRawPhotoPixelFormatTypes
            let format: OSType?
            if mode == .proRAW && self.photoOutput.isAppleProRAWEnabled {
                format = types.first { AVCapturePhotoOutput.isAppleProRAWPixelFormat($0) }
            } else {
                format = types.first { AVCapturePhotoOutput.isBayerRAWPixelFormat($0) }
            }
            guard let format else {
                DispatchQueue.main.async {
                    self.processing -= 1
                    self.message = "Esta lente não oferece \(mode.rawValue). Tente outra lente ou o outro modo."
                }
                return
            }

            let settings = AVCapturePhotoSettings(rawPixelFormatType: format)
            if AVCapturePhotoOutput.isAppleProRAWPixelFormat(format) {
                settings.maxPhotoDimensions = self.photoOutput.maxPhotoDimensions
            }
            if let angle = self.rotationCoordinator?.videoRotationAngleForHorizonLevelCapture,
               let connection = self.photoOutput.connection(with: .video),
               connection.isVideoRotationAngleSupported(angle) {
                connection.videoRotationAngle = angle
            }

            let id = settings.uniqueID
            let processor = PhotoProcessor(look: look) { result in
                self.sessionQueue.async { self.inFlight[id] = nil }
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
            self.inFlight[id] = processor
            self.photoOutput.capturePhoto(with: settings, delegate: processor)
        }
    }

    private func post(_ text: String) {
        DispatchQueue.main.async { self.message = text }
    }
}

// MARK: - Processamento de cada foto

final class PhotoProcessor: NSObject, AVCapturePhotoCaptureDelegate {
    private let look: Look
    private let completion: (Result<UIImage?, Error>) -> Void
    private var dng: Data?
    private var captureError: Error?

    init(look: Look, completion: @escaping (Result<UIImage?, Error>) -> Void) {
        self.look = look
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
        let completion = self.completion
        if let error = error ?? captureError {
            completion(.failure(error))
            return
        }
        guard let dng else {
            completion(.failure(RevelaError.noRawData))
            return
        }
        let look = self.look
        DispatchQueue.global(qos: .userInitiated).async {
            let developed = Developer.develop(dng: dng, look: look)
            Library.save(dng: dng, developed: developed?.heic) { error in
                if let error {
                    completion(.failure(error))
                } else if developed == nil {
                    completion(.failure(RevelaError.developFailed))
                } else {
                    completion(.success(developed?.thumbnail))
                }
            }
        }
    }
}

enum Library {
    /// Salva como um único item na galeria: a foto revelada + o DNG original (par RAW+HEIC).
    static func save(dng: Data, developed: Data?, completion: @escaping (Error?) -> Void) {
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
                    request.addResource(with: .alternatePhoto, data: dng, options: rawOptions)
                } else {
                    request.addResource(with: .photo, data: dng, options: rawOptions)
                }
            }, completionHandler: { _, error in
                completion(error)
            })
        }
    }
}
