import CoreImage
import CoreImage.CIFilterBuiltins
import ImageIO
import UIKit

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
}

enum Look: String, CaseIterable, Identifiable {
    case neutro = "Neutro"
    case filme = "Filme"
    case cine = "Cine"
    case suave = "Suave"
    case prata = "Prata"

    var id: String { rawValue }

    var subtitle: String {
        switch self {
        case .neutro: return "Fiel ao sensor"
        case .filme: return "Negativo colorido, grão fino"
        case .cine: return "Sombras frias, pele quente"
        case .suave: return "Baixo contraste, preto lavado"
        case .prata: return "P&B de alto contraste"
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
        }
    }
}

/// Revela o DNG com a nossa própria curva, sem o processamento de "aparência" da Apple.
enum Developer {
    struct Output {
        let heic: Data
        let thumbnail: UIImage?
    }

    static let displayP3 = CGColorSpace(name: CGColorSpace.displayP3)!
    static let linearP3 = CGColorSpace(name: CGColorSpace.extendedLinearDisplayP3)!

    private static let context = CIContext(options: [
        .workingColorSpace: linearP3,
        .workingFormat: CIFormat.RGBAh,
        .cacheIntermediates: false,
    ])

    private static let library: Data? = {
        guard let url = Bundle.main.url(forResource: "default", withExtension: "metallib") else { return nil }
        return try? Data(contentsOf: url)
    }()

    private static let toneKernel: CIColorKernel? = library.flatMap {
        try? CIColorKernel(functionName: "revelaTone", fromMetalLibraryData: $0)
    }

    private static let previewKernel: CIColorKernel? = library.flatMap {
        try? CIColorKernel(functionName: "revelaPreview", fromMetalLibraryData: $0)
    }

    private static let noise = CIFilter.randomGenerator().outputImage!

    static func develop(dng: Data, look: Look) -> Output? {
        guard let raw = CIRAWFilter(imageData: dng, identifierHint: "com.adobe.raw-image") else { return nil }

        // Desliga o "look" da Apple: sem boost de contraste e sem tone mapping local.
        raw.boostAmount = 0
        raw.boostShadowAmount = 0
        if raw.isLocalToneMapSupported { raw.localToneMapAmount = 0 }
        raw.extendedDynamicRangeAmount = 0

        guard let linear = raw.outputImage else { return nil }

        let graded = apply(toneKernel, to: linear, look: look.params, extra: [])

        // A orientação já foi aplicada pelo CIRAWFilter; não deixar a tag girar a foto de novo.
        var properties = linear.properties
        properties[kCGImagePropertyOrientation as String] = nil
        if var tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any] {
            tiff[kCGImagePropertyTIFFOrientation as String] = nil
            properties[kCGImagePropertyTIFFDictionary as String] = tiff
        }
        let output = graded.settingProperties(properties)

        guard let heic = context.heifRepresentation(
            of: output,
            format: .RGBA8,
            colorSpace: displayP3,
            options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.92]
        ) else { return nil }

        return Output(heic: heic, thumbnail: thumbnail(of: graded))
    }

    /// Aplica o look ao vídeo do visor, para ver o resultado antes de fotografar.
    static func preview(_ image: CIImage, look: Look, zebra: Bool) -> CIImage {
        apply(previewKernel, to: image, look: look.params, extra: [zebra ? 1 : 0] as [Any])
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
