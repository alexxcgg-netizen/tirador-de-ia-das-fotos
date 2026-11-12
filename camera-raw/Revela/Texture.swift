import CoreImage
import Foundation

/// Modo TEXTURA: uma foto RAW de frente para a superfície vira um pacote PBR para Blender e Unreal.
/// Albedo (sem o degradê de luz, no brilho padrão), repetível sem emenda, altura, normal (OpenGL e DirectX), AO e aspereza.
/// Protótipo em Python nas fotos do laboratório (sebe e mato): degradê de luz 3,2 → 1,5 e 1,7 → 1,3; emenda ÷ miolo
/// 0,8–1,1 (sem tratar: 2,5–4).
extension Developer {
    private static let tileBlendKernel: CIKernel? = library.flatMap { try? CIKernel(functionName: "revelaTileBlend", fromMetalLibraryData: $0) }
    private static let normalKernel: CIKernel? = library.flatMap { try? CIKernel(functionName: "revelaNormalFromHeight", fromMetalLibraryData: $0) }
    private static let textureHeightKernel = kernel("revelaTextureHeight")
    private static let textureRangeKernel = kernel("revelaTextureRange")
    private static let textureAOKernel = kernel("revelaTextureAO")
    private static let textureRoughKernel = kernel("revelaTextureRough")

    /// Tamanho do lado das texturas (0 = o máximo que a foto dá). Lido de qualquer fila (UserDefaults é seguro).
    static var textureSide: Int {
        let v = UserDefaults.standard.integer(forKey: "textureSide")
        return v == 0 && UserDefaults.standard.object(forKey: "textureSide") == nil ? 4096 : v
    }

    /// Monta o pacote numa pasta nova em Documentos/Texturas e devolve a foto para a galeria (o albedo) e a pasta.
    static func texturePack(_ frame: CapturedFrame, options: DevelopOptions) -> (output: Output, folder: URL)? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard let tileBlendKernel, let normalKernel, let textureHeightKernel, let textureRangeKernel,
              let textureAOKernel, let textureRoughKernel, let logLumaKernel,
              let full = image(from: frame) else { return nil }
        // Quadrado do meio (a superfície fotografada de frente)
        let fe = full.extent
        let side0 = floor(min(fe.width, fe.height))
        let crop = CGRect(x: (fe.midX - side0 / 2).rounded(), y: (fe.midY - side0 / 2).rounded(), width: side0, height: side0)
        let square = full.cropped(to: crop).transformed(by: CGAffineTransform(translationX: -crop.minX, y: -crop.minY))
        let S = Int(side0)
        let se = CGRect(x: 0, y: 0, width: S, height: S)

        // 1) Albedo: divide pelo brilho de grande escala (em log, numa versão de 256 px) e põe a mediana no cinza médio
        let n = 256
        let small = square.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: Double(n) / Double(S),
                                                                                 kCIInputAspectRatioKey: 1])
        var pixels = [Float](repeating: 0, count: n * n * 4)
        gpu.render(small, toBitmap: &pixels, rowBytes: n * 16, bounds: CGRect(x: 0, y: 0, width: n, height: n),
                   format: .RGBAf, colorSpace: nil)
        var logY = [Float](repeating: 0, count: n * n)
        for i in 0..<(n * n) {
            let y = 0.2126 * pixels[i * 4] + 0.7152 * pixels[i * 4 + 1] + 0.0722 * pixels[i * 4 + 2]
            logY[i] = log(max(y, 1e-4))
        }
        let low = blurred(logY, size: n, sigma: Float(n) / 6)
        let meanLog = logY.reduce(0, +) / Float(n * n)
        var gain = [Float](repeating: 1, count: n * n)
        var corrected = [Float](repeating: 0, count: n * n)
        for i in 0..<(n * n) {
            gain[i] = exp(meanLog - low[i])
            corrected[i] = exp(logY[i]) * gain[i]
        }
        let sorted = corrected.sorted()
        let median = sorted[sorted.count / 2], top = sorted[Int(Float(sorted.count - 1) * 0.995)]
        // Brilho padrão do PBR: mediana em 0,18, sem passar de 0,9 no p99,5 (albedo de verdade não chega a 1)
        let k = min(0.18 / max(median, 1e-5), 0.9 / max(top, 1e-5))
        var gainPixels = [Float](repeating: 1, count: n * n * 4)
        for i in 0..<(n * n) {
            let g = gain[i] * k
            gainPixels[i * 4] = g; gainPixels[i * 4 + 1] = g; gainPixels[i * 4 + 2] = g; gainPixels[i * 4 + 3] = 1
        }
        let gainImage = CIImage(bitmapData: gainPixels.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: n * 16,
                                size: CGSize(width: n, height: n), format: .RGBAf, colorSpace: nil)
            .clampedToExtent().samplingLinear()
            .transformed(by: CGAffineTransform(scaleX: CGFloat(S) / CGFloat(n), y: CGFloat(S) / CGFloat(n)))
            .cropped(to: se)
        let albedoFull = materialize(square.applyingFilter("CIMultiplyCompositing", parameters: [kCIInputBackgroundImageKey: gainImage])
            .cropped(to: se), extent: se)

        // 2) Repetível: a borda final de cada eixo misturada com a inicial (faixa de ¼)
        let overlap = (Double(S) * 0.25).rounded()
        let T = S - Int(overlap)
        let te = CGRect(x: 0, y: 0, width: T, height: T)
        let mean = areaAverage(albedoFull, extent: se)
        guard let tiled = tileBlendKernel.apply(extent: te, roiCallback: { _, _ in se }, arguments: [
            albedoFull, CIVector(x: CGFloat(S), y: CGFloat(S), z: CGFloat(overlap), w: CGFloat(overlap)),
            CIVector(x: CGFloat(mean.x), y: CGFloat(mean.y), z: CGFloat(mean.z)),
        ]) else { return nil }

        // 3) No tamanho pedido (a redução repete as bordas: sem emenda de novo no redimensionamento)
        let wanted = textureSide
        let side = wanted > 0 ? min(wanted, T) : T
        let oe = CGRect(x: 0, y: 0, width: side, height: side)
        let resized: CIImage = side == T ? tiled : tiled.applyingFilter("CIAffineTile", parameters: [kCIInputTransformKey: NSValue(cgAffineTransform: .identity)])
            .applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: Double(side) / Double(T), kCIInputAspectRatioKey: 1])
            .cropped(to: oe)
        let albedo = materialize(resized.cropped(to: oe), extent: oe)

        // 4) Altura: brilho (log) em três escalas, repetido nas bordas para as escalas grandes não criarem emenda
        guard let logY2 = logLumaKernel.apply(extent: oe, arguments: [albedo]) else { return nil }
        let wrap = logY2.applyingFilter("CIAffineTile", parameters: [kCIInputTransformKey: NSValue(cgAffineTransform: .identity)])
        let f = Double(side) / 1024
        func blur(_ sigma: Double) -> CIImage { wrap.applyingGaussianBlur(sigma: max(0.3, sigma * f)).cropped(to: oe) }
        guard let rawHeight = textureHeightKernel.apply(extent: oe, arguments: [blur(0.5), blur(4), blur(2), blur(16), blur(8), blur(64)]) else { return nil }
        let heightReady = materialize(rawHeight, extent: oe)
        let lo = areaExtreme(heightReady, extent: oe, maximum: false), hi = areaExtreme(heightReady, extent: oe, maximum: true)
        guard let ranged = textureRangeKernel.apply(extent: oe, arguments: [heightReady, lo, hi]) else { return nil }
        let height = materialize(ranged, extent: oe)
        let heightWrap = height.applyingFilter("CIAffineTile", parameters: [kCIInputTransformKey: NSValue(cgAffineTransform: .identity)])

        // 5) Normal (OpenGL para o Blender, DirectX para a Unreal): força proporcional ao lado (relevo por largura da textura)
        let strength = Float(6.0 * Double(side) / 380.0)
        let roi: CIKernelROICallback = { _, r in r.insetBy(dx: -2, dy: -2) }
        guard let normalGL = normalKernel.apply(extent: oe, roiCallback: roi, arguments: [heightWrap, strength, Float(0)]),
              let normalDX = normalKernel.apply(extent: oe, roiCallback: roi, arguments: [heightWrap, strength, Float(1)]),
              let ao = textureAOKernel.apply(extent: oe, arguments: [heightWrap.applyingGaussianBlur(sigma: 6 * f).cropped(to: oe), height]),
              let rough = textureRoughKernel.apply(extent: oe, arguments: [albedo, top * k]) else { return nil }

        // 6) Arquivos: albedo em sRGB; os mapas de dado sem conversão de cor (mesmo espaço linear do trabalho)
        let stamp = Int(Date().timeIntervalSince1970)
        let folder = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("Texturas/textura-\(stamp)", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
        func write(_ image: CIImage, _ name: String, color: Bool) -> Bool {
            ForegroundGate.shared.wait()
            let url = folder.appendingPathComponent("textura_\(name).png")
            do {
                try context.writePNGRepresentation(of: image.cropped(to: oe), to: url, format: .RGBA16, colorSpace: color ? srgb : linearP3)
                return true
            } catch {
                dlog("❌ TEXTURA: não gravou \(name): \(error.localizedDescription)")
                return false
            }
        }
        let wrote = [write(albedo, "albedo", color: true), write(normalGL, "normal_gl", color: false),
                     write(normalDX, "normal_dx", color: false), write(height, "altura", color: false),
                     write(ao, "ao", color: false), write(rough, "aspereza", color: false)]
        guard wrote.allSatisfy({ $0 }) else { return nil }
        let readme = """
        Textura do Revela (\(side)×\(side) px, repetível sem emenda)

        textura_albedo.png     cor (Base Color), sRGB
        textura_normal_gl.png  normal OpenGL (Blender: Normal Map, Non-Color)
        textura_normal_dx.png  normal DirectX (Unreal Engine)
        textura_altura.png     altura/deslocamento (Non-Color)
        textura_ao.png         oclusão de ambiente (Non-Color)
        textura_aspereza.png   roughness (Non-Color)

        Blender: Principled BSDF; Base Color ← albedo; Normal ← Normal Map ← normal_gl; Roughness ← aspereza.
        Unreal: importe normal_dx como Normalmap; altura, ao e aspereza com sRGB desligado.
        """
        try? readme.write(to: folder.appendingPathComponent("LEIA-ME.txt"), atomically: true, encoding: .utf8)

        // A galeria recebe o albedo revelado no Neutro (para achar a textura depois)
        var o = options
        o.look = .neutro
        o.custom = nil
        o.zoom = 1
        o.originalAspect = true
        guard let output = finish(albedo, options: o) else { return nil }
        dlog("TEXTURA: \(side)×\(side) px a partir de \(S) px, pacote em \(folder.lastPathComponent) · \(Diagnostics.ms(since: t0))")
        return (output, folder)
    }

    /// Desfoque gaussiano separável num mapa n×n pequeno (bordas espelhadas).
    private static func blurred(_ values: [Float], size n: Int, sigma: Float) -> [Float] {
        let radius = Int((3 * sigma).rounded(.up))
        var weights = [Float](repeating: 0, count: 2 * radius + 1)
        var total: Float = 0
        for i in -radius...radius {
            let w = exp(-Float(i * i) / (2 * sigma * sigma))
            weights[i + radius] = w
            total += w
        }
        for i in weights.indices { weights[i] /= total }
        func mirror(_ i: Int) -> Int {
            var j = i
            while j < 0 || j >= n { j = j < 0 ? -j - 1 : 2 * n - j - 1 }
            return j
        }
        var pass = [Float](repeating: 0, count: n * n)
        var out = [Float](repeating: 0, count: n * n)
        for y in 0..<n {
            for x in 0..<n {
                var acc: Float = 0
                for k in -radius...radius { acc += values[y * n + mirror(x + k)] * weights[k + radius] }
                pass[y * n + x] = acc
            }
        }
        for y in 0..<n {
            for x in 0..<n {
                var acc: Float = 0
                for k in -radius...radius { acc += pass[mirror(y + k) * n + x] * weights[k + radius] }
                out[y * n + x] = acc
            }
        }
        return out
    }

    private static func areaAverage(_ image: CIImage, extent: CGRect) -> SIMD3<Float> {
        let avg = image.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: extent)])
        var px = [Float](repeating: 0, count: 4)
        let at = avg.extent
        gpu.render(avg, toBitmap: &px, rowBytes: 16, bounds: CGRect(x: at.minX, y: at.minY, width: 1, height: 1),
                   format: .RGBAf, colorSpace: nil)
        return SIMD3(px[0], px[1], px[2])
    }

    private static func areaExtreme(_ image: CIImage, extent: CGRect, maximum: Bool) -> Float {
        let filtered = image.applyingFilter(maximum ? "CIAreaMaximum" : "CIAreaMinimum",
                                            parameters: [kCIInputExtentKey: CIVector(cgRect: extent)])
        var px = [Float](repeating: 0, count: 4)
        let at = filtered.extent
        gpu.render(filtered, toBitmap: &px, rowBytes: 16, bounds: CGRect(x: at.minX, y: at.minY, width: 1, height: 1),
                   format: .RGBAf, colorSpace: nil)
        return px[0]
    }
}
