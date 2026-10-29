import CoreImage
import CoreImage.CIFilterBuiltins
import ImageIO
import UIKit

struct LookParams {
    var exposure: Float
    var saturation: Float
    var warmth: Float
    var mono: Float
    var toe: Float
    var contrast: Float
    var grain: Float
}

enum Look: String, CaseIterable, Identifiable {
    case neutro = "Neutro"
    case filme = "Filme"
    case pb = "P&B"

    var id: String { rawValue }

    var params: LookParams {
        switch self {
        case .neutro:
            return LookParams(exposure: 0, saturation: 1, warmth: 0, mono: 0, toe: 0, contrast: 1, grain: 0)
        case .filme:
            return LookParams(exposure: 0, saturation: 0.88, warmth: 0.025, mono: 0, toe: 0.004, contrast: 1.08, grain: 0.035)
        case .pb:
            return LookParams(exposure: 0, saturation: 1, warmth: 0, mono: 1, toe: 0.003, contrast: 1.18, grain: 0.05)
        }
    }
}

/// Revela o DNG com a nossa própria curva, sem o processamento de "aparência" da Apple.
enum Developer {
    struct Output {
        let heic: Data
        let thumbnail: UIImage?
    }

    private static let displayP3 = CGColorSpace(name: CGColorSpace.displayP3)!

    private static let context = CIContext(options: [
        .workingColorSpace: CGColorSpace(name: CGColorSpace.extendedLinearDisplayP3)!,
        .workingFormat: CIFormat.RGBAh,
        .cacheIntermediates: false,
    ])

    private static let kernel: CIColorKernel? = {
        guard let url = Bundle.main.url(forResource: "default", withExtension: "metallib"),
              let data = try? Data(contentsOf: url) else { return nil }
        return try? CIColorKernel(functionName: "revelaTone", fromMetalLibraryData: data)
    }()

    static func develop(dng: Data, look: Look) -> Output? {
        guard let raw = CIRAWFilter(imageData: dng, identifierHint: "com.adobe.raw-image") else { return nil }

        // Desliga o "look" da Apple: sem boost de contraste e sem tone mapping local.
        raw.boostAmount = 0
        raw.boostShadowAmount = 0
        if raw.isLocalToneMapSupported { raw.localToneMapAmount = 0 }
        raw.extendedDynamicRangeAmount = 0

        guard let linear = raw.outputImage else { return nil }

        let graded = grade(linear, look: look.params)

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

    private static func grade(_ image: CIImage, look p: LookParams) -> CIImage {
        guard let kernel else { return image }
        let noise = CIFilter.randomGenerator().outputImage!
            .transformed(by: CGAffineTransform(scaleX: 1.6, y: 1.6))
        let arguments: [Any] = [image, noise, p.exposure, p.saturation, p.warmth, p.mono, p.toe, p.contrast, p.grain]
        return kernel.apply(extent: image.extent, arguments: arguments) ?? image
    }

    private static func thumbnail(of image: CIImage) -> UIImage? {
        let scale = 400 / max(image.extent.width, image.extent.height)
        let small = image.samplingLinear().transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        guard let cg = context.createCGImage(small, from: small.extent, format: .RGBA8, colorSpace: displayP3) else { return nil }
        return UIImage(cgImage: cg)
    }
}
