import CoreImage
import CoreImage.CIFilterBuiltins
import ImageIO
import UIKit
import Vision

struct LookParams {
    var exposure: Float = 0
    var saturation: Float = 1
    var warmth: Float = 0
    var mono: Float = 0
    var toe: Float = 0
    var contrast: Float = 1
    var grain: Float = 0
    var shadowTint = SIMD3<Float>(0, 0, 0)
    var highTint = SIMD3<Float>(0, 0, 0)

    /// Mistura com o Neutro (`amount` 0…1) e escala o grão.
    func scaled(amount: Float, grain grainScale: Float) -> LookParams {
        let n = LookParams()
        func mix(_ a: Float, _ b: Float) -> Float { a + (b - a) * amount }
        return LookParams(
            exposure: mix(n.exposure, exposure), saturation: mix(n.saturation, saturation),
            warmth: mix(n.warmth, warmth), mono: mix(n.mono, mono), toe: mix(n.toe, toe),
            contrast: mix(n.contrast, contrast), grain: grain * amount * grainScale,
            shadowTint: shadowTint * amount, highTint: highTint * amount)
    }
}

enum Look: String, CaseIterable, Identifiable {
    case neutro = "Neutro"
    case filme = "Filme"
    case cine = "Cine"
    case suave = "Suave"
    case prata = "Prata"
    case paisagem = "Paisagem"
    case retrato = "Retrato"
    case slide = "Slide"
    case dourado = "Dourado"
    case nordico = "Nórdico"
    case vintage = "Vintage"
    case bleach = "Bleach"
    case neon = "Neon"
    case noite = "Noite"
    case sepia = "Sépia"

    var id: String { rawValue }

    var subtitle: String {
        switch self {
        case .neutro: return "Fiel ao sensor"
        case .filme: return "Negativo colorido, grão fino"
        case .cine: return "Sombras frias, pele quente"
        case .suave: return "Baixo contraste, preto lavado"
        case .prata: return "P&B de alto contraste"
        case .paisagem: return "Céu e verde vivos, muito detalhe"
        case .retrato: return "Pele quente, contraste macio"
        case .slide: return "Cromo saturado, preto profundo"
        case .dourado: return "Fim de tarde, luz quente"
        case .nordico: return "Frio, claro e dessaturado"
        case .vintage: return "Foto antiga, cor desbotada"
        case .bleach: return "Pouca cor, muito contraste"
        case .neon: return "Noite urbana, ciano e magenta"
        case .noite: return "Sombras azuis, luzes limpas"
        case .sepia: return "Monocromático marrom"
        }
    }

    var params: LookParams {
        switch self {
        case .neutro:
            return LookParams()
        case .filme:
            return LookParams(saturation: 0.9, warmth: 0.03, toe: 0.004, contrast: 1.06, grain: 0.035,
                              shadowTint: SIMD3(0, 0.002, 0.004), highTint: SIMD3(0.012, 0.005, -0.01))
        case .cine:
            return LookParams(saturation: 0.8, toe: 0.002, contrast: 1.12, grain: 0.02,
                              shadowTint: SIMD3(-0.003, 0.004, 0.008), highTint: SIMD3(0.03, 0.012, -0.02))
        case .suave:
            return LookParams(saturation: 0.85, warmth: 0.015, toe: 0.012, contrast: 0.88, grain: 0.015)
        case .prata:
            return LookParams(mono: 1, toe: 0.003, contrast: 1.2, grain: 0.05)
        case .paisagem:
            return LookParams(saturation: 1.22, warmth: 0.01, contrast: 1.1,
                              shadowTint: SIMD3(0, 0.001, 0.003), highTint: SIMD3(0.004, 0.004, 0))
        case .retrato:
            return LookParams(exposure: 0.1, saturation: 0.92, warmth: 0.035, toe: 0.003, contrast: 0.94, grain: 0.012,
                              highTint: SIMD3(0.014, 0.006, -0.004))
        case .slide:
            return LookParams(saturation: 1.3, warmth: 0.01, contrast: 1.22, grain: 0.015,
                              shadowTint: SIMD3(0.001, -0.001, 0.003))
        case .dourado:
            return LookParams(saturation: 1.05, warmth: 0.07, toe: 0.003, contrast: 1.05, grain: 0.02,
                              shadowTint: SIMD3(0.002, 0.0005, -0.002), highTint: SIMD3(0.035, 0.018, -0.025))
        case .nordico:
            return LookParams(exposure: 0.15, saturation: 0.7, warmth: -0.035, toe: 0.01, contrast: 0.92, grain: 0.012,
                              shadowTint: SIMD3(-0.001, 0.001, 0.004), highTint: SIMD3(-0.004, 0.002, 0.008))
        case .vintage:
            return LookParams(saturation: 0.72, warmth: 0.05, toe: 0.02, contrast: 0.86, grain: 0.07,
                              shadowTint: SIMD3(0.004, 0.003, -0.001), highTint: SIMD3(0.02, 0.012, -0.03))
        case .bleach:
            return LookParams(saturation: 0.45, toe: 0.001, contrast: 1.3, grain: 0.04,
                              highTint: SIMD3(0.004, 0.004, 0.002))
        case .neon:
            return LookParams(saturation: 1.18, warmth: -0.04, contrast: 1.15, grain: 0.03,
                              shadowTint: SIMD3(-0.002, 0.004, 0.009), highTint: SIMD3(0.03, -0.01, 0.03))
        case .noite:
            return LookParams(exposure: -0.1, saturation: 0.85, warmth: -0.02, contrast: 1.08, grain: 0.03,
                              shadowTint: SIMD3(-0.002, 0.001, 0.007), highTint: SIMD3(0.006, 0.004, 0))
        case .sepia:
            return LookParams(mono: 1, toe: 0.006, contrast: 1.05, grain: 0.04,
                              shadowTint: SIMD3(0.004, 0.002, -0.002), highTint: SIMD3(0.045, 0.022, -0.03))
        }
    }
}

enum AspectRatio: String, CaseIterable, Identifiable {
    case r43 = "4:3"
    case r11 = "1:1"
    case r169 = "16:9"
    case xpan = "65:24"

    var id: String { rawValue }

    /// Lado maior ÷ lado menor.
    var ratio: CGFloat {
        switch self {
        case .r43: return 4.0 / 3.0
        case .r11: return 1
        case .r169: return 16.0 / 9.0
        case .xpan: return 65.0 / 24.0
        }
    }

    /// Recorte centralizado: primeiro o zoom digital, depois a proporção (mantendo a orientação da imagem).
    func crop(_ rect: CGRect, zoom: CGFloat) -> CGRect {
        var w = rect.width / zoom, h = rect.height / zoom
        let long = max(w, h), short = min(w, h)
        if long / short > ratio {
            if h > w { h = w * ratio } else { w = h * ratio }
        } else {
            if h > w { w = h / ratio } else { h = w / ratio }
        }
        return CGRect(x: rect.midX - w / 2, y: rect.midY - h / 2, width: w, height: h).integral
    }
}

/// Um quadro vindo da câmera: DNG, ou HEIC quando a câmera não oferece RAW (ex.: a da frente).
struct CapturedFrame {
    let data: Data
    let isRaw: Bool
}

/// Tudo que define como a foto é revelada.
struct DevelopOptions {
    var look: Look = .filme
    var amount: Float = 1
    var grain: Float = 1
    var zoom: CGFloat = 1
    var aspect: AspectRatio = .r43
    /// Inverte na horizontal, como num espelho.
    var mirror = false

    var params: LookParams { look.params.scaled(amount: amount, grain: grain) }
}

/// Revela o DNG com a nossa própria curva, sem o processamento de "aparência" da Apple.
enum Developer {
    struct Output {
        let heic: Data
        let thumbnail: UIImage?
    }

    static let displayP3 = CGColorSpace(name: CGColorSpace.displayP3)!
    static let linearP3 = CGColorSpace(name: CGColorSpace.extendedLinearDisplayP3)!

    static let context = CIContext(options: [
        .workingColorSpace: linearP3,
        .workingFormat: CIFormat.RGBAh,
        .cacheIntermediates: false,
    ])

    private static let library: Data? = {
        guard let url = Bundle.main.url(forResource: "default", withExtension: "metallib") else { return nil }
        return try? Data(contentsOf: url)
    }()

    private static func kernel(_ name: String) -> CIColorKernel? {
        library.flatMap { try? CIColorKernel(functionName: name, fromMetalLibraryData: $0) }
    }

    private static let toneKernel = kernel("revelaTone")
    private static let previewKernel = kernel("revelaPreview")
    private static let peakingKernel = kernel("revelaPeaking")
    private static let sharpnessKernel = kernel("revelaSharpness")
    private static let pickKernel = kernel("revelaPick")

    private static let noise = CIFilter.randomGenerator().outputImage!

    // MARK: - Foto

    /// RAW -> luz linear da cena, sem boost de contraste e sem tone mapping local da Apple.
    static func linear(dng: Data) -> CIImage? {
        guard let raw = CIRAWFilter(imageData: dng, identifierHint: "com.adobe.raw-image") else { return nil }
        raw.boostAmount = 0
        raw.boostShadowAmount = 0
        if raw.isLocalToneMapSupported { raw.localToneMapAmount = 0 }
        raw.extendedDynamicRangeAmount = 0
        guard let image = raw.outputImage else { return nil }

        // A orientação já foi aplicada pelo CIRAWFilter; não deixar a tag girar a foto de novo.
        var properties = image.properties
        properties[kCGImagePropertyOrientation as String] = nil
        if var tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any] {
            tiff[kCGImagePropertyTIFFOrientation as String] = nil
            properties[kCGImagePropertyTIFFDictionary as String] = tiff
        }
        return image.settingProperties(properties)
    }

    /// HEIC já processado pela Apple -> luz linear de tela (o look é aplicado como no visor).
    static func processed(_ data: Data) -> CIImage? {
        guard let image = CIImage(data: data, options: [.applyOrientationProperty: true]) else { return nil }
        var properties = image.properties
        properties[kCGImagePropertyOrientation as String] = nil
        return image.settingProperties(properties)
    }

    static func image(from frame: CapturedFrame) -> CIImage? {
        frame.isRaw ? linear(dng: frame.data) : processed(frame.data)
    }

    static func develop(_ frame: CapturedFrame, options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard let image = image(from: frame) else {
            dlog("❌ Não abriu o \(frame.isRaw ? "DNG" : "HEIC") (\(frame.data.count / 1024) KB)")
            return nil
        }
        let output = finish(image, options: options, displayReferred: !frame.isRaw)
        dlog("Revelação \(options.look.rawValue) \(Int(image.extent.width))×\(Int(image.extent.height)) · \(frame.isRaw ? "DNG" : "HEIC") \(frame.data.count / 1_048_576) MB: \(Diagnostics.ms(since: t0))\(output == nil ? " · FALHOU" : "")")
        return output
    }

    /// Diz se os kernels de Metal carregaram (sem eles a revelação sai sem look).
    static var kernelStatus: String {
        let names = ["revelaTone": toneKernel, "revelaPreview": previewKernel, "revelaPeaking": peakingKernel,
                     "revelaSharpness": sharpnessKernel, "revelaPick": pickKernel]
        let missing = names.filter { $0.value == nil }.map(\.key).sorted()
        return missing.isEmpty ? "todos carregados" : "FALTANDO: " + missing.joined(separator: ", ")
    }

    /// Luz linear -> look, recorte e HEIC de 10 bits.
    static func finish(_ linear: CIImage, options: DevelopOptions, displayReferred: Bool = false) -> Output? {
        let rect = options.aspect.crop(linear.extent, zoom: options.zoom)
        var cropped = linear.cropped(to: rect)
            .transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))
        if options.mirror {
            cropped = cropped.transformed(by: CGAffineTransform(scaleX: -1, y: 1).translatedBy(x: -rect.width, y: 0))
        }
        // Imagem já com a curva da Apple: usa o kernel do visor, que desfaz a curva antes do look
        let graded = (displayReferred
            ? apply(previewKernel, to: cropped, look: options.params, extra: [0])
            : apply(toneKernel, to: cropped, look: options.params, extra: []))
            .settingProperties(linear.properties)

        guard let heic = try? context.heif10Representation(
            of: graded,
            colorSpace: displayP3,
            options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.92]
        ) else { return nil }

        return Output(heic: heic, thumbnail: thumbnail(of: graded))
    }

    // MARK: - Empilhamento

    enum StackKind { case focus, average }

    /// Junta vários RAW: foco empilhado (pega o pedaço mais nítido de cada quadro) ou média (menos ruído / exposição longa).
    static func stack(_ frames: [CapturedFrame], kind: StackKind, options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        let images = frames.compactMap { image(from: $0) }
        guard let reference = images.first else { return nil }
        dlog("Empilhando \(images.count) de \(frames.count) quadros (\(kind == .focus ? "foco" : "média")) · \(Int(reference.extent.width))×\(Int(reference.extent.height))")
        let aligned = [reference] + images.dropFirst().map { align($0, to: reference) }
        dlog("Alinhamento: \(Diagnostics.ms(since: t0))")

        let merged: CIImage
        switch kind {
        case .average:
            merged = average(aligned)
        case .focus:
            merged = focusMerge(aligned) ?? average(aligned)
        }
        let output = finish(merged.cropped(to: reference.extent).settingProperties(reference.properties), options: options,
                            displayReferred: !(frames.first?.isRaw ?? true))
        dlog("Empilhamento + revelação: \(Diagnostics.ms(since: t0))\(output == nil ? " · FALHOU" : "")")
        return output
    }

    /// Corrige o tremido entre quadros (só translação, que é o que a mão faz em frações de segundo).
    private static func align(_ image: CIImage, to reference: CIImage) -> CIImage {
        let request = VNTranslationalImageRegistrationRequest(targetedCIImage: image, options: [:])
        let handler = VNImageRequestHandler(ciImage: reference, options: [:])
        guard (try? handler.perform([request])) != nil,
              let observation = request.results?.first as? VNImageTranslationAlignmentObservation else {
            dlog("Alinhamento falhou num quadro (usado sem alinhar)")
            return image
        }
        let t = observation.alignmentTransform
        dlog(String(format: "Quadro deslocado %.1f, %.1f px", t.tx, t.ty))
        return image.transformed(by: t)
    }

    private static func average(_ images: [CIImage]) -> CIImage {
        guard var sum = images.first else { return CIImage.empty() }
        for image in images.dropFirst() {
            sum = image.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: sum])
        }
        let k = CGFloat(1) / CGFloat(images.count)
        return sum.applyingFilter("CIColorMatrix", parameters: [
            "inputRVector": CIVector(x: k, y: 0, z: 0, w: 0),
            "inputGVector": CIVector(x: 0, y: k, z: 0, w: 0),
            "inputBVector": CIVector(x: 0, y: 0, z: k, w: 0),
            "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        ])
    }

    private static func sharpness(_ image: CIImage) -> CIImage? {
        let laplacian = image.applyingFilter("CIConvolution3X3", parameters: [
            "inputWeights": CIVector(values: [0, 1, 0, 1, -4, 1, 0, 1, 0], count: 9),
            "inputBias": 0,
        ])
        guard let s = sharpnessKernel?.apply(extent: image.extent, arguments: [laplacian]) else { return nil }
        return s.clampedToExtent().applyingGaussianBlur(sigma: 6).cropped(to: image.extent)
    }

    private static func focusMerge(_ images: [CIImage]) -> CIImage? {
        guard var result = images.first, var resultSharpness = sharpness(result), let pickKernel else { return nil }
        for image in images.dropFirst() {
            guard let s = sharpness(image),
                  let mask = pickKernel.apply(extent: image.extent, arguments: [s, resultSharpness]) else { continue }
            let softMask = mask.clampedToExtent().applyingGaussianBlur(sigma: 2).cropped(to: image.extent)
            result = image.applyingFilter("CIBlendWithMask", parameters: [
                kCIInputBackgroundImageKey: result,
                kCIInputMaskImageKey: softMask,
            ])
            resultSharpness = s.applyingFilter("CIMaximumCompositing", parameters: [kCIInputBackgroundImageKey: resultSharpness])
        }
        return result
    }

    // MARK: - Visor

    struct PreviewOptions {
        var develop = DevelopOptions()
        var zebra = false
        var peaking = false
    }

    /// Aplica o look ao vídeo do visor, para ver o resultado antes de fotografar.
    static func preview(_ image: CIImage, options: PreviewOptions) -> CIImage {
        var out = apply(previewKernel, to: image, look: options.develop.params, extra: [options.zebra ? 1 : 0] as [Any])
        if options.peaking, let peakingKernel {
            let edges = image.applyingFilter("CIEdges", parameters: [kCIInputIntensityKey: 3.0])
            out = peakingKernel.apply(extent: image.extent, arguments: [out, edges, 0.18]) ?? out
        }
        return out
    }

    private static func apply(_ kernel: CIColorKernel?, to image: CIImage, look p: LookParams, extra: [Any]) -> CIImage {
        guard let kernel else { return image }
        // Grão que muda a cada quadro, como em filme
        let grainNoise = noise
            .transformed(by: CGAffineTransform(translationX: .random(in: 0...512), y: .random(in: 0...512)))
            .transformed(by: CGAffineTransform(scaleX: 1.6, y: 1.6))
        let arguments: [Any] = [image, grainNoise, p.exposure, p.saturation, p.warmth, p.mono, p.toe, p.contrast, p.grain,
                                vector(p.shadowTint), vector(p.highTint)] + extra
        return kernel.apply(extent: image.extent, arguments: arguments) ?? image
    }

    private static func vector(_ v: SIMD3<Float>) -> CIVector {
        CIVector(x: CGFloat(v.x), y: CGFloat(v.y), z: CGFloat(v.z))
    }

    private static func thumbnail(of image: CIImage) -> UIImage? {
        let scale = 400 / max(image.extent.width, image.extent.height)
        let small = image.samplingLinear().transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        guard let cg = context.createCGImage(small, from: small.extent, format: .RGBA8, colorSpace: displayP3) else { return nil }
        return UIImage(cgImage: cg)
    }
}
