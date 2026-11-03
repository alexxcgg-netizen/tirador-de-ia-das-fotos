import CoreImage
import Darwin
import ImageIO
import UIKit
import UniformTypeIdentifiers
import Vision

/// Super resolução de verdade: várias fotos de 48 MP com o tremido natural da mão. Cada uma vê o detalhe
/// num lugar um pouquinho diferente; alinhadas com precisão de fração de pixel, ampliadas e somadas,
/// viram uma foto de até ~100 MP com mais detalhe real (e bem menos ruído) do que uma foto sozinha.
extension Developer {
    /// Tamanho da foto final (pixels).
    static let superResolutionTarget: Double = 100_000_000

    static func superResolution(_ frames: [CapturedFrame], options: DevelopOptions, sharpen: Double = 0.6) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard frames.count >= 2 else { return frames.first.flatMap { develop($0, options: options) } }

        // Referência: a foto mais nítida da sequência
        let scores = frames.map { frame in image(from: frame, scale: 0.125).map(sharpnessScore) ?? 0 }
        let refIndex = scores.indices.max { scores[$0] < scores[$1] } ?? 0
        guard let reference = image(from: frames[refIndex]) else { return nil }
        let full = reference.extent
        var cropOptions = options
        cropOptions.originalAspect = false
        let region = cropOptions.cropRect(in: full)
        let factor = CGFloat(min(2, max(1, (superResolutionTarget / Double(region.width * region.height)).squareRoot())))
        let outExtent = CGRect(x: 0, y: 0, width: (region.width * factor).rounded(.down), height: (region.height * factor).rounded(.down))
        dlog(String(format: "Super resolução: %d fotos (referência %d) · recorte %.0f×%.0f · ampliação %.2f× → %.0f×%.0f",
                    frames.count, refIndex + 1, region.width, region.height, factor, outExtent.width, outExtent.height))

        // 1) Alinhamento: grosso pelo Vision numa versão pequena, fino (fração de pixel) em 9 pedaços da foto
        let transforms = alignTransforms(frames: frames, refIndex: refIndex, reference: reference, region: region)
        dlog("Super resolução: alinhado em \(Diagnostics.ms(since: t0))")

        // 2) Cada foto ampliada (Lanczos) e só então deslocada: o deslocamento de fração de pixel perde menos detalhe
        let toRegion = CGAffineTransform(translationX: -region.minX * factor, y: -region.minY * factor)
        func upscaled(_ i: Int) -> CIImage? {
            guard let img = i == refIndex ? reference : image(from: frames[i]), let m = transforms[i] else { return nil }
            let inUpscaled = CGAffineTransform(scaleX: 1 / factor, y: 1 / factor)
                .concatenating(m)
                .concatenating(CGAffineTransform(scaleX: factor, y: factor))
            return img
                .applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: factor, kCIInputAspectRatioKey: 1])
                .transformed(by: inUpscaled)
                .transformed(by: toRegion)
                .cropped(to: outExtent)
        }
        guard let refUp = upscaled(refIndex), let robustColorKernel, let robustWeightKernel, let divideKernel else { return nil }

        // 3) Junção robusta: onde algo se mexeu entre as fotos, fica a referência (sem fantasma)
        let refBlur = blurred(refUp, extent: outExtent)
        var sumColor = refUp
        var sumWeight = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: outExtent)
        var used = 1
        for i in frames.indices where i != refIndex {
            guard let up = upscaled(i) else { continue }
            let upBlur = blurred(up, extent: outExtent)
            guard let color = robustColorKernel.apply(extent: outExtent, arguments: [up, upBlur, refBlur, Float(0.1)]),
                  let weight = robustWeightKernel.apply(extent: outExtent, arguments: [upBlur, refBlur, Float(0.1)]) else { continue }
            sumColor = add(sumColor, color)
            sumWeight = add(sumWeight, weight)
            used += 1
        }
        guard let merged = divideKernel.apply(extent: outExtent, arguments: [sumColor, sumWeight]) else { return nil }
        let sharpened = merged
            .applyingFilter("CIUnsharpMask", parameters: [kCIInputRadiusKey: Double(factor) * 1.1, kCIInputIntensityKey: sharpen])
            .cropped(to: outExtent)

        var opts = options
        opts.zoom = 1
        opts.originalAspect = true
        let (graded, _) = developed(sharpened.settingProperties(reference.properties), options: opts)

        // 4) Foto gigante revelada em faixas, direto num arquivo mapeado (não cabe inteira na memória)
        guard let heic = renderInStrips(graded, extent: outExtent, properties: reference.properties) else {
            dlog("❌ Super resolução: não consegui gravar a foto")
            return nil
        }
        dlog(String(format: "Super resolução revelada: %d fotos · %.0f MP · %@ · %@ · memória livre %@", used,
                    outExtent.width * outExtent.height / 1_000_000, "\(heic.count / 1_048_576) MB",
                    Diagnostics.ms(since: t0), Diagnostics.freeMemory))
        return Output(heic: heic, thumbnail: thumbnail(fromHEIC: heic), sameSizeAsRaw: false)
    }

    // MARK: - Alinhamento fino

    /// Para cada foto, a transformação (deslocamento, um pouco de giro e escala) que a leva em cima da referência.
    private static func alignTransforms(frames: [CapturedFrame], refIndex: Int, reference: CIImage,
                                        region: CGRect) -> [CGAffineTransform?] {
        let alignScale: CGFloat = 0.25
        let patch = 160, search = 16
        var result = [CGAffineTransform?](repeating: nil, count: frames.count)
        result[refIndex] = .identity
        guard let smallRef = image(from: frames[refIndex], scale: Float(alignScale)) else { return result }
        let refHandler = VNImageRequestHandler(ciImage: smallRef, options: [:])

        // 9 pedaços espalhados pelo recorte
        var centers: [CGPoint] = []
        for fy in [0.2, 0.5, 0.8] {
            for fx in [0.2, 0.5, 0.8] {
                centers.append(CGPoint(x: (region.minX + region.width * CGFloat(fx)).rounded(),
                                       y: (region.minY + region.height * CGFloat(fy)).rounded()))
            }
        }
        let half = CGFloat(patch / 2)
        // Os 9 pedaços saem numa leitura só (um RAW aberto uma vez, em vez de nove)
        let refPatches = grayPatches(reference, rects: centers.map { c in
            CGRect(x: c.x - half, y: c.y - half, width: CGFloat(patch), height: CGFloat(patch))
        })

        for i in frames.indices where i != refIndex {
            autoreleasepool {
                guard let img = image(from: frames[i]), let small = image(from: frames[i], scale: Float(alignScale)) else { return }
                var coarse = CGPoint.zero
                let request = VNTranslationalImageRegistrationRequest(targetedCIImage: small, options: [:])
                if (try? refHandler.perform([request])) != nil,
                   let observation = request.results?.first as? VNImageTranslationAlignmentObservation {
                    coarse = CGPoint(x: (observation.alignmentTransform.tx / alignScale).rounded(),
                                     y: (observation.alignmentTransform.ty / alignScale).rounded())
                }
                // Pares (ponto na foto, ponto na referência) com precisão de fração de pixel
                var pairs: [(frame: CGPoint, ref: CGPoint)] = []
                let s = CGFloat(search)
                let imgPatches = grayPatches(img, rects: centers.map { c in
                    CGRect(x: c.x - half - coarse.x - s, y: c.y - half - coarse.y - s,
                           width: CGFloat(patch) + 2 * s, height: CGFloat(patch) + 2 * s)
                })
                for (k, c) in centers.enumerated() {
                    guard let refPatch = refPatches[k], let imgPatch = imgPatches[k],
                          let shift = subpixelShift(ref: refPatch, img: imgPatch, size: patch, search: search) else { continue }
                    // O que está em c na referência está em c − grosso + (u, −v) nesta foto (linhas do bitmap descem)
                    pairs.append((CGPoint(x: c.x - coarse.x + shift.x, y: c.y - coarse.y - shift.y), c))
                }
                let fitted = fitSimilarity(pairs)
                result[i] = fitted ?? CGAffineTransform(translationX: coarse.x, y: coarse.y)
                let t = result[i]!
                dlog(String(format: "Super resolução: foto %d · %d/9 pedaços · desloca %.2f, %.2f px · giro %.3f°",
                            i + 1, pairs.count, t.tx, t.ty, atan2(t.b, t.a) * 180 / .pi))
            }
        }
        return result
    }

    /// Luminância (raiz, para o escuro pesar parecido com o claro) de vários pedaços, linha 0 em cima.
    /// Todos os pedaços vão lado a lado numa imagem só e saem numa leitura.
    private static func grayPatches(_ image: CIImage, rects: [CGRect]) -> [[Float]?] {
        guard let first = rects.first else { return [] }
        let w = Int(first.width), h = Int(first.height)
        let columns = 3
        let rows = (rects.count + columns - 1) / columns
        let atlasExtent = CGRect(x: 0, y: 0, width: w * columns, height: h * rows)
        var atlas = CIImage(color: .black).cropped(to: atlasExtent)
        for (k, rect) in rects.enumerated() {
            // Célula k: coluna k % 3, linha k / 3 contando de cima (o bitmap começa em cima)
            let cx = CGFloat((k % columns) * w), cy = CGFloat((rows - 1 - k / columns) * h)
            let piece = image.cropped(to: rect)
                .transformed(by: CGAffineTransform(translationX: cx - rect.minX, y: cy - rect.minY))
            atlas = piece.composited(over: atlas)
        }
        guard let cg = context.createCGImage(atlas, from: atlasExtent, format: .RGBAf, colorSpace: linearP3),
              let data = cg.dataProvider?.data, let bytes = CFDataGetBytePtr(data),
              cg.width == w * columns, cg.height == h * rows else { return rects.map { _ in nil } }
        let rowFloats = cg.bytesPerRow / 4
        return bytes.withMemoryRebound(to: Float.self, capacity: rowFloats * h * rows) { f in
            rects.indices.map { k -> [Float]? in
                let ox = (k % columns) * w, oy = (k / columns) * h
                var gray = [Float](repeating: 0, count: w * h)
                for y in 0..<h {
                    for x in 0..<w {
                        let o = (oy + y) * rowFloats + (ox + x) * 4
                        gray[y * w + x] = max(0, 0.2126 * f[o] + 0.7152 * f[o + 1] + 0.0722 * f[o + 2]).squareRoot()
                    }
                }
                return gray
            }
        }
    }

    /// Procura o deslocamento (em pixels do bitmap) que melhor encaixa o pedaço da foto no da referência:
    /// primeiro em meia resolução numa área grande, depois em resolução cheia perto do melhor, e refina com
    /// uma parábola. Os pedaços são normalizados (média 0, desvio 1): a exposição pode mudar entre as fotos.
    /// nil se o pedaço é liso demais ou se o encaixe saiu da área de busca.
    private static func subpixelShift(ref rawRef: [Float], img rawImg: [Float], size n: Int, search s: Int) -> CGPoint? {
        func normalized(_ a: [Float]) -> ([Float], Float) {
            let mean = a.reduce(0, +) / Float(a.count)
            let variance = a.reduce(0) { $0 + ($1 - mean) * ($1 - mean) } / Float(a.count)
            let std = max(variance.squareRoot(), 1e-6)
            return (a.map { ($0 - mean) / std }, variance)
        }
        let (ref, refVariance) = normalized(rawRef)
        // Pedaço liso (céu, parede) não diz nada sobre o deslocamento
        guard refVariance > 0.0004 else { return nil }
        let (img, _) = normalized(rawImg)
        let wide = n + 2 * s

        // Diferença entre a referência e a foto deslocada (u, v), olhando 1 de cada `step` pixels
        func ssd(_ u: Int, _ v: Int, step: Int) -> Float {
            var sum: Float = 0
            ref.withUnsafeBufferPointer { r in
                img.withUnsafeBufferPointer { m in
                    var y = 0
                    while y < n {
                        let ro = y * n, io = (y + s + v) * wide + s + u
                        var x = 0
                        while x < n {
                            let d = r[ro + x] - m[io + x]
                            sum += d * d
                            x += step
                        }
                        y += step
                    }
                }
            }
            return sum
        }

        // 1) Busca larga de 2 em 2 pixels, olhando 1 de cada 2
        var best = (u: 0, v: 0, cost: Float.greatestFiniteMagnitude)
        for v in stride(from: -s + 2, through: s - 2, by: 2) {
            for u in stride(from: -s + 2, through: s - 2, by: 2) {
                let c = ssd(u, v, step: 2)
                if c < best.cost { best = (u, v, c) }
            }
        }
        // 2) Fina: todos os pixels, ±2 em volta do melhor
        var fine = (u: best.u, v: best.v, cost: Float.greatestFiniteMagnitude)
        var costs: [Int: Float] = [:]
        for v in (best.v - 2)...(best.v + 2) {
            for u in (best.u - 2)...(best.u + 2) where abs(u) < s && abs(v) < s {
                let c = ssd(u, v, step: 1)
                costs[v * 1000 + u] = c
                if c < fine.cost { fine = (u, v, c) }
            }
        }
        // Na borda da busca: o deslocamento é maior que a busca (o grosso errou)
        guard abs(fine.u) < s - 1, abs(fine.v) < s - 1 else { return nil }
        func at(_ u: Int, _ v: Int) -> Float { costs[v * 1000 + u] ?? ssd(u, v, step: 1) }
        func parabola(_ a: Float, _ b: Float, _ c: Float) -> Float {
            let den = a - 2 * b + c
            return den > 1e-9 ? max(-0.5, min(0.5, (a - c) / (2 * den))) : 0
        }
        let du = parabola(at(fine.u - 1, fine.v), fine.cost, at(fine.u + 1, fine.v))
        let dv = parabola(at(fine.u, fine.v - 1), fine.cost, at(fine.u, fine.v + 1))
        return CGPoint(x: CGFloat(Float(fine.u) + du), y: CGFloat(Float(fine.v) + dv))
    }

    /// Melhor deslocamento + giro + escala (mínimos quadrados) que leva os pontos da foto nos da referência.
    /// Tira os pedaços que não concordam (algo se mexeu ali) e calcula de novo.
    private static func fitSimilarity(_ pairs: [(frame: CGPoint, ref: CGPoint)]) -> CGAffineTransform? {
        func fit(_ ps: [(frame: CGPoint, ref: CGPoint)]) -> CGAffineTransform? {
            guard !ps.isEmpty else { return nil }
            let n = CGFloat(ps.count)
            let qx = ps.reduce(0) { $0 + $1.frame.x } / n, qy = ps.reduce(0) { $0 + $1.frame.y } / n
            let px = ps.reduce(0) { $0 + $1.ref.x } / n, py = ps.reduce(0) { $0 + $1.ref.y } / n
            guard ps.count >= 3 else { return CGAffineTransform(translationX: px - qx, y: py - qy) }
            var d: CGFloat = 0, sa: CGFloat = 0, sb: CGFloat = 0
            for p in ps {
                let ax = p.frame.x - qx, ay = p.frame.y - qy, bx = p.ref.x - px, by = p.ref.y - py
                d += ax * ax + ay * ay
                sa += ax * bx + ay * by
                sb += ax * by - ay * bx
            }
            guard d > 0 else { return nil }
            let a = sa / d, b = sb / d
            // Mão tremendo gira e aproxima muito pouco; fora disso, a conta errou: fica só o deslocamento
            guard abs(a - 1) < 0.02, abs(b) < 0.02 else { return CGAffineTransform(translationX: px - qx, y: py - qy) }
            return CGAffineTransform(a: a, b: b, c: -b, d: a, tx: px - (a * qx - b * qy), ty: py - (b * qx + a * qy))
        }
        guard var t = fit(pairs) else { return nil }
        let kept = pairs.filter { p in
            let m = p.frame.applying(t)
            return hypot(m.x - p.ref.x, m.y - p.ref.y) < 1.5
        }
        if kept.count >= 3, kept.count < pairs.count, let refit = fit(kept) { t = refit }
        return t
    }

    // MARK: - Gravar a foto gigante

    /// Revela a imagem em faixas dentro de um arquivo mapeado e grava o HEIC a partir dele.
    private static func renderInStrips(_ image: CIImage, extent: CGRect, properties: [String: Any]) -> Data? {
        let w = Int(extent.width), h = Int(extent.height)
        let bytesPerRow = w * 4
        let size = bytesPerRow * h
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("superres-\(UUID().uuidString).raw")
        let fd = open(url.path, O_RDWR | O_CREAT | O_TRUNC, 0o644)
        guard fd >= 0 else { return nil }
        defer {
            close(fd)
            try? FileManager.default.removeItem(at: url)
        }
        guard ftruncate(fd, off_t(size)) == 0 else { return nil }
        guard let base = mmap(nil, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0), base != MAP_FAILED else { return nil }
        defer { munmap(base, size) }
        guard let ctx = CGContext(data: base, width: w, height: h, bitsPerComponent: 8, bytesPerRow: bytesPerRow,
                                  space: displayP3, bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
        // Faixas de ~16 MP: o Core Image só abre das fotos o pedaço que cada faixa precisa
        let stripHeight = max(256, 16_000_000 / max(w, 1))
        var y = 0
        while y < h {
            let rows = min(stripHeight, h - y)
            let rect = CGRect(x: 0, y: CGFloat(y), width: CGFloat(w), height: CGFloat(rows))
            autoreleasepool {
                if let strip = context.createCGImage(image, from: rect, format: .RGBA8, colorSpace: displayP3) {
                    ctx.draw(strip, in: rect)
                }
            }
            y += rows
        }
        guard let provider = CGDataProvider(dataInfo: nil, data: UnsafeRawPointer(base), size: size, releaseData: { _, _, _ in }),
              let big = CGImage(width: w, height: h, bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: bytesPerRow,
                                space: displayP3, bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.noneSkipLast.rawValue),
                                provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent) else { return nil }
        let out = NSMutableData()
        guard let destination = CGImageDestinationCreateWithData(out, UTType.heic.identifier as CFString, 1, nil) else { return nil }
        var props: [CFString: Any] = [kCGImageDestinationLossyCompressionQuality: 0.9]
        if let exif = properties[kCGImagePropertyExifDictionary as String] { props[kCGImagePropertyExifDictionary] = exif }
        if let tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any] {
            var t = tiff
            t[kCGImagePropertyTIFFOrientation as String] = nil
            props[kCGImagePropertyTIFFDictionary] = t
        }
        CGImageDestinationAddImage(destination, big, props as CFDictionary)
        guard CGImageDestinationFinalize(destination) else { return nil }
        return out as Data
    }

    private static func thumbnail(fromHEIC data: Data) -> UIImage? {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              let cg = CGImageSourceCreateThumbnailAtIndex(source, 0, [
                  kCGImageSourceCreateThumbnailFromImageAlways: true,
                  kCGImageSourceThumbnailMaxPixelSize: 400,
                  kCGImageSourceCreateThumbnailWithTransform: true,
              ] as CFDictionary) else { return nil }
        return UIImage(cgImage: cg)
    }
}
