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

    /// Alinhamento de uma foto: o geral (deslocamento, giro, escala) e o que sobrou em cada um dos 9 pedaços.
    struct Alignment {
        var transform: CGAffineTransform
        /// Correção por região, em pixels da foto (0 onde o pedaço não deu ou discordou).
        var residuals: [CGPoint]
    }

    /// `keep`: tira mais fotos do que usa e fica com as mais nítidas. `sharpen` ≥ 0,8 desconvolui mais (Lua).
    static func superResolution(_ allFrames: [CapturedFrame], options: DevelopOptions, sharpen: Double = 0.6,
                                keep: Int? = nil) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard allFrames.count >= 2 else { return allFrames.first.flatMap { develop($0, options: options) } }

        // As mais nítidas (as tremidas só borrariam a soma); a referência é a mais nítida de todas
        let allScores = allFrames.map { frame in image(from: frame, scale: 0.125).map(sharpnessScore) ?? 0 }
        var chosen = Array(allFrames.indices)
        if let keep, keep < allFrames.count {
            chosen = Array(chosen.sorted { allScores[$0] > allScores[$1] }.prefix(max(2, keep))).sorted()
            dlog("Super resolução: usando as \(chosen.count) mais nítidas de \(allFrames.count)")
        }
        let frames = chosen.map { allFrames[$0] }
        let scores = chosen.map { allScores[$0] }
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

        // 1) Alinhamento: grosso pelo Vision, fino (fração de pixel) em 9 pedaços, e o que sobra em cada região
        let centers = tileCenters(in: region)
        let alignments = alignTransforms(frames: frames, refIndex: refIndex, reference: reference, centers: centers)
        dlog("Super resolução: alinhado em \(Diagnostics.ms(since: t0))")

        // 2) Cada foto ampliada (Lanczos) e só então deslocada: o deslocamento de fração de pixel perde menos detalhe
        let toRegion = CGAffineTransform(translationX: -region.minX * factor, y: -region.minY * factor)
        let grid = CIVector(x: (centers[0].x - region.minX) * factor, y: (centers[0].y - region.minY) * factor,
                            z: (centers[1].x - centers[0].x) * factor, w: (centers[3].y - centers[0].y) * factor)
        func upscaled(_ i: Int) -> CIImage? {
            guard let img = i == refIndex ? reference : image(from: frames[i]), let a = alignments[i] else { return nil }
            let inUpscaled = CGAffineTransform(scaleX: 1 / factor, y: 1 / factor)
                .concatenating(a.transform)
                .concatenating(CGAffineTransform(scaleX: factor, y: factor))
            var out = img
                .applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: factor, kCIInputAspectRatioKey: 1])
                .transformed(by: inUpscaled)
                .transformed(by: toRegion)
            // Alinhamento por região: cada canto se mexe um pouco diferente (obturador do sensor, mão girando)
            let r = a.residuals.map { CGPoint(x: $0.x * factor, y: $0.y * factor) }
            if let gridWarpKernel, r.count == 9, r.contains(where: { hypot($0.x, $0.y) > 0.25 }) {
                let reach = (r.map { max(abs($0.x), abs($0.y)) }.max() ?? 0) + 2
                let source = out
                out = gridWarpKernel.apply(extent: outExtent, roiCallback: { _, rect in rect.insetBy(dx: -reach, dy: -reach) },
                                           image: source, arguments: [
                    CIVector(x: r[0].x, y: r[0].y, z: r[1].x, w: r[1].y),
                    CIVector(x: r[2].x, y: r[2].y, z: r[3].x, w: r[3].y),
                    CIVector(x: r[4].x, y: r[4].y, z: r[5].x, w: r[5].y),
                    CIVector(x: r[6].x, y: r[6].y, z: r[7].x, w: r[7].y),
                    CIVector(x: r[8].x, y: r[8].y),
                    grid,
                ]) ?? source
            }
            return out.cropped(to: outExtent)
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

        var opts = options
        opts.zoom = 1
        opts.originalAspect = true
        // O brilho em volta das luzes é calculado na foto inteira e aqui ela é revelada em faixas: fica de fora
        opts.noGlow = true
        let properties = reference.properties

        // 4) Foto gigante revelada em faixas, cada uma desconvoluída (desfaz o borrão da lente e da ampliação)
        let iterations = sharpen >= 0.8 ? 7 : 5
        let sigma = Double(0.55 * factor + 0.25)
        guard let heic = renderInStrips(merged, extent: outExtent, properties: properties, iterations: iterations, sigma: sigma,
                                        grade: { developed($0.settingProperties(properties), options: opts).0 }) else {
            dlog("❌ Super resolução: não consegui gravar a foto")
            return nil
        }
        dlog(String(format: "Super resolução revelada: %d fotos · %.0f MP · %@ · desconvolução %d passos · %@ · memória livre %@", used,
                    outExtent.width * outExtent.height / 1_000_000, "\(heic.count / 1_048_576) MB", iterations,
                    Diagnostics.ms(since: t0), Diagnostics.freeMemory))
        return Output(heic: heic, thumbnail: thumbnail(fromHEIC: heic), sameSizeAsRaw: false)
    }

    /// Alinhamento fino para a NOITE: para cada foto, uma função que a coloca em cima da referência (a primeira).
    static func fineWarps(_ frames: [CapturedFrame], reference: CIImage) -> [(CIImage) -> CIImage] {
        let e = reference.extent
        let centers = tileCenters(in: e)
        let alignments = alignTransforms(frames: frames, refIndex: 0, reference: reference, centers: centers)
        let grid = CIVector(x: centers[0].x, y: centers[0].y, z: centers[1].x - centers[0].x, w: centers[3].y - centers[0].y)
        return alignments.map { alignment in
            guard let alignment else { return { $0 } }
            return { image in
                var out = image.transformed(by: alignment.transform)
                let r = alignment.residuals
                if let gridWarpKernel, r.count == 9, r.contains(where: { hypot($0.x, $0.y) > 0.25 }) {
                    let reach = (r.map { max(abs($0.x), abs($0.y)) }.max() ?? 0) + 2
                    let source = out
                    out = gridWarpKernel.apply(extent: e, roiCallback: { _, rect in rect.insetBy(dx: -reach, dy: -reach) },
                                               image: source, arguments: [
                        CIVector(x: r[0].x, y: r[0].y, z: r[1].x, w: r[1].y),
                        CIVector(x: r[2].x, y: r[2].y, z: r[3].x, w: r[3].y),
                        CIVector(x: r[4].x, y: r[4].y, z: r[5].x, w: r[5].y),
                        CIVector(x: r[6].x, y: r[6].y, z: r[7].x, w: r[7].y),
                        CIVector(x: r[8].x, y: r[8].y),
                        grid,
                    ]) ?? source
                }
                return out.cropped(to: e)
            }
        }
    }

    /// 9 pedaços espalhados pelo recorte (linha de baixo primeiro, como o Core Image conta).
    private static func tileCenters(in region: CGRect) -> [CGPoint] {
        var centers: [CGPoint] = []
        for fy in [0.2, 0.5, 0.8] {
            for fx in [0.2, 0.5, 0.8] {
                centers.append(CGPoint(x: (region.minX + region.width * CGFloat(fx)).rounded(),
                                       y: (region.minY + region.height * CGFloat(fy)).rounded()))
            }
        }
        return centers
    }

    // MARK: - Alinhamento fino

    /// Para cada foto, a transformação (deslocamento, um pouco de giro e escala) que a leva em cima da referência.
    private static func alignTransforms(frames: [CapturedFrame], refIndex: Int, reference: CIImage,
                                        centers: [CGPoint]) -> [Alignment?] {
        let alignScale: CGFloat = 0.25
        let patch = 160, search = 16
        var result = [Alignment?](repeating: nil, count: frames.count)
        result[refIndex] = Alignment(transform: .identity, residuals: [CGPoint](repeating: .zero, count: 9))
        guard let smallRef = image(from: frames[refIndex], scale: Float(alignScale)) else { return result }
        let refHandler = VNImageRequestHandler(ciImage: smallRef, options: [:])

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
                // No escuro o Vision às vezes "acha" um pulo enorme: a mão não anda tanto
                let e = reference.extent
                if abs(coarse.x) > e.width * 0.08 || abs(coarse.y) > e.height * 0.08 { coarse = .zero }
                // Pares (ponto na foto, ponto na referência) com precisão de fração de pixel
                var pairs: [(frame: CGPoint, ref: CGPoint)] = []
                var pairTile: [Int] = []
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
                    pairTile.append(k)
                }
                let t = fitSimilarity(pairs) ?? CGAffineTransform(translationX: coarse.x, y: coarse.y)
                // O que sobrou em cada pedaço depois do geral (até 1,5 px; mais que isso é algo que se mexeu)
                var residuals = [CGPoint](repeating: .zero, count: 9)
                for (n, pair) in pairs.enumerated() {
                    let placed = pair.frame.applying(t)
                    let r = CGPoint(x: pair.ref.x - placed.x, y: pair.ref.y - placed.y)
                    if hypot(r.x, r.y) < 1.5 { residuals[pairTile[n]] = r }
                }
                result[i] = Alignment(transform: t, residuals: residuals)
                let worst = residuals.map { hypot($0.x, $0.y) }.max() ?? 0
                dlog(String(format: "Super resolução: foto %d · %d/9 pedaços · desloca %.2f, %.2f px · giro %.3f° · região até %.2f px",
                            i + 1, pairs.count, t.tx, t.ty, atan2(t.b, t.a) * 180 / .pi, worst))
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
    private static func renderInStrips(_ image: CIImage, extent: CGRect, properties: [String: Any],
                                       iterations: Int, sigma: Double, grade: (CIImage) -> CIImage) -> Data? {
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
                let scene = deconvolved(image, strip: rect, extent: extent, iterations: iterations, sigma: sigma)
                // A faixa vai numa tela do tamanho da foto: a vinheta do filme continua centrada na foto inteira
                let canvas = scene.composited(over: CIImage(color: .clear).cropped(to: extent))
                if let strip = context.createCGImage(grade(canvas), from: rect, format: .RGBA8, colorSpace: displayP3) {
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

    /// Richardson–Lucy numa faixa (com margem, para a borda da faixa não mudar): a estimativa é refinada
    /// comparando com o observado depois de borrar com o mesmo borrão da lente. Pouco ruído porque as fotos já foram somadas.
    private static func deconvolved(_ image: CIImage, strip rect: CGRect, extent: CGRect, iterations: Int, sigma: Double) -> CIImage {
        guard iterations > 0, let ratioKernel, let multiplyKernel else { return image.cropped(to: rect) }
        let margin = CGFloat(ceil(sigma * 3 * 2 * Double(iterations))) + 4
        let big = rect.insetBy(dx: 0, dy: -margin).intersection(extent).integral
        let observed = materialize(image.cropped(to: big), extent: big)
        var estimate = observed
        func blur(_ x: CIImage) -> CIImage { x.clampedToExtent().applyingGaussianBlur(sigma: sigma).cropped(to: big) }
        for _ in 0..<iterations {
            guard let ratio = ratioKernel.apply(extent: big, arguments: [observed, blur(estimate)]),
                  let next = multiplyKernel.apply(extent: big, arguments: [estimate, blur(ratio)]) else { break }
            estimate = materialize(next, extent: big)
        }
        return estimate.cropped(to: rect)
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
