import CoreImage
import Foundation

/// Copiar a cor de uma foto: mede a foto de referência (contraste, saturação, cor dos meios-tons
/// e das sombras, preto lavado) e monta um filme próprio parecido, que dá para ajustar depois.
enum ColorMatch {
    private static let context = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.sRGB)!])

    static func look(from data: Data, name: String) -> CustomLook? {
        guard let image = CIImage(data: data, options: [.applyOrientationProperty: true]) else { return nil }
        let side: CGFloat = 160
        let scale = side / max(image.extent.width, image.extent.height)
        let small = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        let e = small.extent.integral
        let w = Int(e.width), h = Int(e.height)
        guard w > 8, h > 8 else { return nil }
        var pixels = [UInt8](repeating: 0, count: w * h * 4)
        context.render(small, toBitmap: &pixels, rowBytes: w * 4, bounds: e, format: .RGBA8,
                       colorSpace: CGColorSpace(name: CGColorSpace.sRGB))

        var lumas: [Float] = []
        lumas.reserveCapacity(w * h)
        var chromaSum: Float = 0
        var mid = SIMD3<Float>(0, 0, 0), midCount: Float = 0
        var dark = SIMD3<Float>(0, 0, 0), darkCount: Float = 0
        for i in stride(from: 0, to: pixels.count, by: 4) {
            let c = SIMD3<Float>(Float(pixels[i]), Float(pixels[i + 1]), Float(pixels[i + 2])) / 255
            let l = 0.2126 * c.x + 0.7152 * c.y + 0.0722 * c.z
            lumas.append(l)
            chromaSum += c.max() - c.min()
            if l > 0.3 && l < 0.7 { mid += c; midCount += 1 }
            if l < 0.25 { dark += c; darkCount += 1 }
        }
        lumas.sort()
        let n = Float(lumas.count)
        let mean = lumas.reduce(0, +) / n
        let variance = lumas.reduce(0) { $0 + ($1 - mean) * ($1 - mean) } / n
        let std = variance.squareRoot()
        let black = lumas[Int(Float(lumas.count) * 0.02)]
        let chroma = chromaSum / n

        func clamp(_ v: Float, _ lo: Float, _ hi: Float) -> Float { min(max(v, lo), hi) }
        var look = CustomLook()
        look.name = name
        look.base = Look.neutro.rawValue
        look.contrast = clamp(std / 0.21, 0.7, 1.5)
        look.saturation = clamp(chroma / 0.2, 0, 1.7)
        look.blackAndWhite = chroma < 0.035
        look.fade = clamp((black - 0.02) / 0.12, 0, 1)
        look.exposure = clamp(log2(max(mean, 0.02) / 0.42) * 0.6, -0.6, 0.6)
        if midCount > 0 {
            let m = mid / midCount
            look.warmth = clamp((m.x - m.z) * 4, -1, 1)
            look.tint = clamp(((m.x + m.z) / 2 - m.y) * 6, -1, 1)
        }
        if darkCount > 0 {
            let d = dark / darkCount
            look.shadowColor = clamp((d.x - d.z) * 10, -1, 1)
        }
        look.grain = 0.02
        look.vignette = 0.1
        look.halation = 0.03
        dlog(String(format: "Cor copiada: contraste %.2f · saturação %.2f · temperatura %.2f · tom %.2f · sombras %.2f · preto %.2f%@",
                    look.contrast, look.saturation, look.warmth, look.tint, look.shadowColor, look.fade,
                    look.blackAndWhite ? " · P&B" : ""))
        return look
    }
}
