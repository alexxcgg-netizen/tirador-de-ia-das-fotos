import CoreImage
import Darwin
import ImageIO
import UIKit
import UniformTypeIdentifiers
import Vision
import os

/// Super resolução de verdade: várias fotos de 48 MP com o tremido natural da mão. Cada uma vê o detalhe
/// num lugar um pouquinho diferente; alinhadas com precisão de fração de pixel, ampliadas e somadas,
/// viram uma foto de até ~100 MP com mais detalhe real (e bem menos ruído) do que uma foto sozinha.
extension Developer {
    /// Tamanho da foto final (pixels).
    static let superResolutionTarget: Double = 100_000_000

    /// Alinhamento de uma foto: o geral (deslocamento, giro, escala) e o que sobrou em cada um dos 9 pedaços.
    /// Calibragem da super resolução (o laboratório testa variações; o app usa a padrão).
    struct SRTuning {
        /// Tamanho do núcleo de cada pixel na grade grande (em pixels grandes).
        // 0,45 com a Richardson–Lucy (laboratório 86ab1f0: +4,12/+6,09/+4,48 dB). A desconvolução regularizada (tv) só
        // ganhava no iPhone 12 Pro (+4,77) e perdia no XS (+4,72) e no Pixel (+4,30): fica desligada
        var splatSigma: Double = 0.45
        /// Borrão da desconvolução final, × o fator de ampliação.
        // 0,45 × fator com 3 passos (laboratório b22822c: +1,85/+2,67/+1,84 dB contra +1,66/+1,98/+1,73 com 0,35 × 2)
        var deconvScale: Double = 0.4
        var deconvIterations = 3
        /// Tolerância do anti-fantasma na junção (maior = aceita mais diferença da referência). O serrilhado diferente
        /// em cada foto é justamente o que a super resolução aproveita: tolerância apertada demais o jogava fora
        var ghostK: Float = 0.1
        /// Limpeza de brilho depois da desconvolução (× o ruído medido na junção). A desconvolução realça o ruído e a
        /// super resolução não tinha limpeza nenhuma (a foto ampliada de comparação tem o ruído suavizado pela ampliação)
        var denoise: Float = 0
        /// Desconvolução regularizada (Huber-TV, brilho/cor) em vez da Richardson–Lucy. Estudo em Python nas 24 fotos
        /// do laboratório: +5,4 dB (RL × 3: +4,5; RL × 10: +4,9). Borradura: caixa 2×2 do sensor ⊗ gaussiana 0,45 px
        var tv = false
        var tvLumaLambda: Float = 2e-4
        var tvChromaLambda: Float = 2e-3
        var tvDelta: Float = 0.01
        var tvIterations = 30
        /// Limpeza só da cor depois da Richardson–Lucy (Huber-TV sem desfazer borrão: o detalhe do brilho fica)
        var chromaClean: Float = 0
        /// MAP com as fotos todas de uma vez (ampliação 2×): resolve o problema inteiro (cada foto = média 2×2 da cena
        /// borrada, deslocada) com Huber-TV conjunta brilho/cor. Estudo nas fotos das três câmeras do laboratório:
        /// +6,3/+7,7/+6,8 dB contra +4,1/+5,3/+5,6 da regressão de núcleo + RL (simulação do app)
        var map = true
        var mapIterations = 16
        var mapLumaLambda: Float = 2e-4
        var mapChromaLambda: Float = 6e-4
        var mapDelta: Float = 0.003
        /// Anti-fantasma do MAP (troca a amostra pela referência, em vez de só tirar peso): bem mais tolerante que o da
        /// junção antiga, só para movimento de verdade. Com 0,1 o serrilhado das bordas virava "fantasma" e a referência
        /// ampliada (borrada) entrava no lugar (laboratório ea18328: XS +1,93, iPhone 12 +3,65)
        var mapGhostK: Float = 0.5
    }
    static var srTuning = SRTuning()

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
        // Nitidez no centro de uma versão em ¼ (em ⅛ a foto tremida passava, como na NOITE)
        let allScores = allFrames.map { frame -> Float in
            guard let small = image(from: frame, scale: 0.25) else { return 0 }
            let e = small.extent
            let side = min(512, e.width, e.height)
            return sharpnessScore(small.cropped(to: CGRect(x: (e.midX - side / 2).rounded(), y: (e.midY - side / 2).rounded(),
                                                           width: side, height: side)))
        }
        var chosen = Array(allFrames.indices)
        if let keep, keep < allFrames.count {
            // Pelo menos `keep`, e toda foto nítida (≥ 85% da melhor) também entra: mais fotos = mais detalhe
            // (protótipo com a cena do laboratório: 10 fotos +4,1 dB, 16 +4,7, 24 +5,1). Antes ficavam só as `keep`
            let best = allScores.max() ?? 0
            let ranked = chosen.sorted { allScores[$0] > allScores[$1] }
            chosen = ranked.enumerated().filter { $0.offset < max(2, keep) || allScores[$0.element] >= 0.85 * best }.map(\.element).sorted()
            dlog("Super resolução: usando as \(chosen.count) mais nítidas de \(allFrames.count)")
        }
        var frames = chosen.map { allFrames[$0] }
        var scores = chosen.map { allScores[$0] }
        var refIndex = scores.indices.max { scores[$0] < scores[$1] } ?? 0
        guard let reference = image(from: frames[refIndex]) else { return nil }
        let full = reference.extent
        var cropOptions = options
        cropOptions.originalAspect = false
        let region = cropOptions.cropRect(in: full)
        let factor = CGFloat(min(2, max(1, (superResolutionTarget / Double(region.width * region.height)).squareRoot())))
        let outExtent = CGRect(x: 0, y: 0, width: (region.width * factor).rounded(.down), height: (region.height * factor).rounded(.down))
        dlog(String(format: "Super resolução: %d fotos (referência %d) · recorte %.0f×%.0f · ampliação %.2f× → %.0f×%.0f",
                    frames.count, refIndex + 1, region.width, region.height, factor, outExtent.width, outExtent.height))

        // Memória: cada foto guardada pronta custa recorte × 8 bytes, e a referência ampliada e as faixas da desconvolução
        // somam por cima. Com 24 fotos a 8× chegava a ~1,4 GB (o iPhone mata o app). Fica com as mais nítidas que cabem
        let padFull = 0.1 * max(full.width, full.height)
        let sourceFit = region.insetBy(dx: -padFull, dy: -padFull).intersection(full).integral
        let perFrame = Double(sourceFit.width * sourceFit.height) * 8
        let outBytes = Double(outExtent.width * outExtent.height) * 8
        // Proporcional à memória livre de verdade (o 17 Pro Max tem bem mais que os 700 MB fixos de antes, que cortavam para
        // 12 fotos uma cena de 12 MP), até 1,5 GB
        #if targetEnvironment(simulator)
        let available = 4_000_000_000.0  // o simulador não tem limite (e devolve ~0)
        #else
        let available = Double(os_proc_available_memory())
        #endif
        let budget = min(1_500_000_000, (available > 0 ? available : 1_500_000_000) * 0.45) - outBytes * 4
        let fit = max(min(frames.count, max(2, keep ?? 2)), Int(max(0, budget) / max(perFrame, 1)))
        if frames.count > fit {
            let ranked = frames.indices.sorted { scores[$0] > scores[$1] }.prefix(fit).sorted()
            frames = ranked.map { frames[$0] }
            scores = ranked.map { scores[$0] }
            refIndex = scores.indices.max { scores[$0] < scores[$1] } ?? 0
            dlog("Super resolução: memória livre \(Int(available / 1e6)) MB → ficam \(fit) fotos")
        }

        // 1) Alinhamento: grosso pelo Vision, fino (fração de pixel) em 9 pedaços, e o que sobra em cada região
        let centers = tileCenters(in: region)
        let alignments = alignTransforms(frames: frames, refIndex: refIndex, reference: reference, centers: centers)
        dlog("Super resolução: alinhado em \(Diagnostics.ms(since: t0))")

        // 2) Cada foto ampliada (Lanczos) e só então deslocada: o deslocamento de fração de pixel perde menos detalhe
        let toRegion = CGAffineTransform(translationX: -region.minX * factor, y: -region.minY * factor)
        // Cada RAW aberto uma vez só: o pedaço que interessa vai para a memória de vídeo. Sem isso, cada faixa da
        // foto gigante abria as 10 fotos de novo. Só quando cabe (no SUPER ZOOM o recorte é pequeno)
        let pad = 0.1 * max(full.width, full.height)
        let source = region.insetBy(dx: -pad, dy: -pad).intersection(full).integral
        let prepare = Double(source.width * source.height) * 8 * Double(frames.count) <= budget
        // Guardado: a junção nova e a antiga (reserva) pedem a mesma foto, e ela é aberta uma vez só
        var cache: [Int: CIImage] = [:]
        func decoded(_ i: Int) -> CIImage? {
            if let hit = cache[i] { return hit }
            guard let img = i == refIndex ? reference : image(from: frames[i]) else { return nil }
            let ready = prepare ? materialize(img.cropped(to: source), extent: source) : img
            cache[i] = ready
            return ready
        }
        let grid = CIVector(x: (centers[0].x - region.minX) * factor, y: (centers[0].y - region.minY) * factor,
                            z: (centers[1].x - centers[0].x) * factor, w: (centers[3].y - centers[0].y) * factor)
        func upscaled(_ i: Int) -> CIImage? {
            guard let a = alignments[i], let img = decoded(i) else { return nil }
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
        guard var merged = divideKernel.apply(extent: outExtent, arguments: [sumColor, sumWeight]) else { return nil }
        // Regressão de núcleo (como o Google no Pixel): cada pixel de cada foto no lugar exato da grade grande.
        // No protótipo com RAWs de verdade: +4 dB sobre uma foto ampliada (o jeito antigo dava +0,5)
        var splatted = false
        // A referência ampliada é lida 16 vezes por foto (cor e peso): guardada pronta quando cabe na memória
        let refReady = Double(outExtent.width * outExtent.height) * 8 < 450_000_000 ? materialize(refUp, extent: outExtent) : refUp
        var solved = false
        if srTuning.map, factor > 1.99,
           let map = mapMerge(frames: frames, decoded: decoded, alignments: alignments, refUp: refReady,
                              region: region, factor: factor, outExtent: outExtent, grid: grid, centers: centers) {
            merged = map.image
            used = map.used
            splatted = true
            solved = true
        } else if let splat = splatMerge(frames: frames, decoded: decoded, alignments: alignments, refUp: refReady,
                                         region: region, factor: factor, outExtent: outExtent, grid: grid) {
            merged = splat.image
            used = splat.used
            splatted = true
        }

        var opts = options
        opts.zoom = 1
        opts.originalAspect = true
        // O brilho em volta das luzes é calculado na foto inteira e aqui ela é revelada em faixas: fica de fora
        opts.noGlow = true
        let properties = reference.properties

        // 4) Foto gigante revelada em faixas, cada uma desconvoluída (desfaz o borrão da lente e da ampliação)
        // Do 5º passo em diante quase não muda nada e cada passo custa o mesmo: 4 bastam (Lua: 6)
        // Depois da regressão de núcleo só falta um pouco: 2 passos com borrão de 0,35 × o fator (protótipo:
        // o borrão antigo de 1,35 px com 4 passos tirava 1,5 dB). Lua um passo a mais
        // O MAP já desfez o borrão do sensor e da lente: sem desconvolução depois
        let iterations = solved ? 0 : (splatted ? srTuning.deconvIterations + (sharpen >= 0.8 ? 1 : 0) : (sharpen >= 0.8 ? 6 : 4))
        let sigma = splatted ? srTuning.deconvScale * Double(factor) : Double(0.55 * factor + 0.25)
        // Ruído da junção (antes da desconvolução, que o realça ~1,5×) para a limpeza final
        let cleanup = srTuning.denoise
        let noise = cleanup > 0 ? measuredNoise(merged) * 1.5 : 0
        if cleanup > 0 { dlog(String(format: "Super resolução: limpeza %.2f · ruído medido %.4f", cleanup, noise)) }
        guard let heic = renderInStrips(merged, extent: outExtent, properties: properties, iterations: iterations, sigma: sigma,
                                        grade: { strip in
            let clean = cleanup > 0 ? lumaDenoise(strip, strength: cleanup, noise: noise * cleanup) : strip
            return developed(clean.settingProperties(properties), options: opts).0
        }) else {
            dlog("❌ Super resolução: não consegui gravar a foto")
            return nil
        }
        dlog(String(format: "Super resolução revelada: %d fotos · %.0f MP · %@ · desconvolução %d passos · %@ · memória livre %@", used,
                    outExtent.width * outExtent.height / 1_000_000, "\(heic.count / 1_048_576) MB", iterations,
                    Diagnostics.ms(since: t0), Diagnostics.freeMemory))
        return Output(heic: heic, thumbnail: thumbnail(fromHEIC: heic), sameSizeAsRaw: false)
    }

    /// Junta as fotos por regressão de núcleo: para cada pixel da foto grande, os 16 pixels mais perto de cada foto
    /// (já no lugar pelo alinhamento) entram com peso pela distância; fotos que não batem (movimento) quase não contam.
    private static func splatMerge(frames: [CapturedFrame], decoded: (Int) -> CIImage?, alignments: [Alignment?],
                                   refUp: CIImage, region: CGRect, factor: CGFloat, outExtent: CGRect,
                                   grid: CIVector) -> (image: CIImage, used: Int)? {
        guard let splatKernel, let divideKernel else { return nil }
        var colorSum: CIImage?, weightSum: CIImage?
        var used = 0
        for i in frames.indices {
            guard let a = alignments[i], let src = decoded(i) else { continue }
            let inv = a.transform.inverted()
            var r = a.residuals.map { CGPoint(x: $0.x * factor, y: $0.y * factor) }
            if r.count != 9 { r = Array(repeating: .zero, count: 9) }
            let reach = (r.map { max(abs($0.x), abs($0.y)) }.max() ?? 0) / factor + 4
            let roi: CIKernelROICallback = { index, rect in
                if index == 1 { return rect.insetBy(dx: -2, dy: -2) }
                let corners = [CGPoint(x: rect.minX, y: rect.minY), CGPoint(x: rect.maxX, y: rect.minY),
                               CGPoint(x: rect.minX, y: rect.maxY), CGPoint(x: rect.maxX, y: rect.maxY)]
                    .map { CGPoint(x: $0.x / factor + region.minX, y: $0.y / factor + region.minY).applying(inv) }
                let xs = corners.map(\.x), ys = corners.map(\.y)
                return CGRect(x: xs.min()!, y: ys.min()!, width: xs.max()! - xs.min()!, height: ys.max()! - ys.min()!)
                    .insetBy(dx: -reach, dy: -reach)
            }
            let common: [Any] = [
                src, refUp,
                CIVector(x: inv.a, y: inv.c, z: inv.tx), CIVector(x: inv.b, y: inv.d, z: inv.ty),
                CIVector(x: factor, y: region.minX, z: region.minY, w: CGFloat(srTuning.splatSigma)),
                CIVector(x: r[0].x, y: r[0].y, z: r[1].x, w: r[1].y),
                CIVector(x: r[2].x, y: r[2].y, z: r[3].x, w: r[3].y),
                CIVector(x: r[4].x, y: r[4].y, z: r[5].x, w: r[5].y),
                CIVector(x: r[6].x, y: r[6].y, z: r[7].x, w: r[7].y),
                CIVector(x: r[8].x, y: r[8].y),
                grid, srTuning.ghostK,
            ]
            guard let color = splatKernel.apply(extent: outExtent, roiCallback: roi, arguments: common + [Float(0)]),
                  let weight = splatKernel.apply(extent: outExtent, roiCallback: roi, arguments: common + [Float(1)]) else { continue }
            colorSum = colorSum.map { add($0, color) } ?? color
            weightSum = weightSum.map { add($0, weight) } ?? weight
            used += 1
        }
        guard used >= 2, let colorSum, let weightSum,
              let merged = divideKernel.apply(extent: outExtent, arguments: [colorSum, weightSum]) else { return nil }
        dlog("Super resolução: \(used) fotos juntadas por regressão de núcleo (cada pixel no lugar exato)")
        return (merged, used)
    }

    /// Se a 1ª linha de um CIImage(bitmapData:) vira o topo (y maior): medido uma vez, para a tabela do MAP não sair de
    /// ponta-cabeça (trocaria pedaço e fase)
    private static let bitmapFirstRowIsTop: Bool = {
        let data: [Float] = [1, 1, 1, 1, 0, 0, 0, 1]
        let img = CIImage(bitmapData: data.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: 16,
                          size: CGSize(width: 1, height: 2), format: .RGBAf, colorSpace: nil)
        var probe = [Float](repeating: -1, count: 4)
        context.render(img, toBitmap: &probe, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBAf, colorSpace: nil)
        let top = probe[0] < 0.5
        dlog("Super resolução: 1ª linha do bitmap = \(top ? "topo" : "base")")
        return top
    }()

    private static func srMitchell(_ v: Double) -> Double {
        let x = abs(v)
        if x < 1 { return (7 * x * x * x - 12 * x * x + 16.0 / 3) / 6 }
        if x < 2 { return ((-7.0 / 3) * x * x * x + 12 * x * x - 20 * x + 32.0 / 3) / 6 }
        return 0
    }
    private static func srH(_ d: Double) -> Double { 0.5 * (srMitchell(d + 0.5) + srMitchell(d - 0.5)) }

    /// Núcleo 1D de AᵀA para uma foto cujas amostras caem em o + 2i (pixels grandes), no pixel grande de fase `a`
    /// (centro em a + ½): k[d] = Σᵢ h(a + ½ − pᵢ)·h(a + ½ + d − pᵢ), d = −3…3
    private static func phaseKernel(offset o: Double, phase a: Int) -> [Double] {
        (-3...3).map { d in
            (-8...8).reduce(0.0) { sum, i in
                let p = o + 2 * Double(i)
                return sum + srH(Double(a) + 0.5 - p) * srH(Double(a) + 0.5 + Double(d) - p)
            }
        }
    }

    /// SUPER ZOOM 3×: MAP com todas as fotos. b = Aᵀy/K (retroprojeção), começa em Σh·y/Σh e faz FISTA com AᵀA exato
    /// para deslocamento (por pedaço da grade 3×3, a fase de cada foto vem do alinhamento dela ali) e Huber-TV conjunta.
    private static func mapMerge(frames: [CapturedFrame], decoded: (Int) -> CIImage?, alignments: [Alignment?],
                                 refUp: CIImage, region: CGRect, factor: CGFloat, outExtent: CGRect,
                                 grid: CIVector, centers: [CGPoint]) -> (image: CIImage, used: Int)? {
        guard let splatHKernel, let mapStepKernel, let divideKernel, centers.count == 9 else { return nil }
        let t = srTuning
        var colorSum: CIImage?, weightSum: CIImage?
        var used = 0
        // Núcleos de AᵀA: 9 pedaços × 4 fases × 7×7 (somados nas fotos, ÷ K no fim)
        var table = [Double](repeating: 0, count: 9 * 4 * 49)
        for i in frames.indices {
            guard let a = alignments[i], let src = decoded(i) else { continue }
            let inv = a.transform.inverted()
            var r = a.residuals.map { CGPoint(x: $0.x * factor, y: $0.y * factor) }
            if r.count != 9 { r = Array(repeating: .zero, count: 9) }
            let reach = (r.map { max(abs($0.x), abs($0.y)) }.max() ?? 0) / factor + 4
            let roi: CIKernelROICallback = { index, rect in
                if index == 1 { return rect.insetBy(dx: -2, dy: -2) }
                let corners = [CGPoint(x: rect.minX, y: rect.minY), CGPoint(x: rect.maxX, y: rect.minY),
                               CGPoint(x: rect.minX, y: rect.maxY), CGPoint(x: rect.maxX, y: rect.maxY)]
                    .map { CGPoint(x: $0.x / factor + region.minX, y: $0.y / factor + region.minY).applying(inv) }
                let xs = corners.map(\.x), ys = corners.map(\.y)
                return CGRect(x: xs.min()!, y: ys.min()!, width: xs.max()! - xs.min()!, height: ys.max()! - ys.min()!)
                    .insetBy(dx: -reach, dy: -reach)
            }
            let common: [Any] = [
                src, refUp,
                CIVector(x: inv.a, y: inv.c, z: inv.tx), CIVector(x: inv.b, y: inv.d, z: inv.ty),
                CIVector(x: factor, y: region.minX, z: region.minY, w: 0),
                CIVector(x: r[0].x, y: r[0].y, z: r[1].x, w: r[1].y),
                CIVector(x: r[2].x, y: r[2].y, z: r[3].x, w: r[3].y),
                CIVector(x: r[4].x, y: r[4].y, z: r[5].x, w: r[5].y),
                CIVector(x: r[6].x, y: r[6].y, z: r[7].x, w: r[7].y),
                CIVector(x: r[8].x, y: r[8].y),
                grid, t.mapGhostK,
            ]
            guard let color = splatHKernel.apply(extent: outExtent, roiCallback: roi, arguments: common + [Float(0)]),
                  let weight = splatHKernel.apply(extent: outExtent, roiCallback: roi, arguments: common + [Float(1)]) else { continue }
            colorSum = colorSum.map { add($0, color) } ?? color
            weightSum = weightSum.map { add($0, weight) } ?? weight
            used += 1
            // Fase desta foto em cada pedaço: onde cai o centro do pixel da foto mais perto do centro do pedaço
            for tile in 0..<9 {
                let c = CGPoint(x: grid.x + CGFloat(tile % 3) * grid.z, y: grid.y + CGFloat(tile / 3) * grid.w)
                let q = CGPoint(x: (c.x - r[tile].x) / factor + region.minX, y: (c.y - r[tile].y) / factor + region.minY).applying(inv)
                let qc = CGPoint(x: floor(q.x) + 0.5, y: floor(q.y) + 0.5).applying(a.transform)
                let px = Double((qc.x - region.minX) * factor + r[tile].x), py = Double((qc.y - region.minY) * factor + r[tile].y)
                let ox = px - 2 * floor(px / 2), oy = py - 2 * floor(py / 2)
                for ay in 0..<2 {
                    let ky = phaseKernel(offset: oy, phase: ay)
                    for ax in 0..<2 {
                        let kx = phaseKernel(offset: ox, phase: ax)
                        let base = ((tile * 2 + ay) * 2 + ax) * 49
                        for dy in 0..<7 { for dx in 0..<7 { table[base + dy * 7 + dx] += ky[dy] * kx[dx] } }
                    }
                }
            }
        }
        guard used >= 2, let colorSum, let weightSum else { return nil }
        let k = Float(used)
        let e = outExtent
        let b = materialize(scaled(colorSum, by: 1 / k).cropped(to: e), extent: e)
        let wsum = materialize(weightSum.cropped(to: e), extent: e)
        guard let start = divideKernel.apply(extent: e, arguments: [scaled(b, by: k), wsum]) else { return nil }
        // Tabela como imagem (14 × 126): x = fase x·7 + dx, y = (pedaço·2 + fase y)·7 + dy (linhas da imagem de baixo para cima)
        let tw = 14, th = 126
        var pixels = [Float](repeating: 0, count: tw * th * 4)
        for tile in 0..<9 { for ay in 0..<2 { for ax in 0..<2 { for dy in 0..<7 { for dx in 0..<7 {
            let v = Float(table[((tile * 2 + ay) * 2 + ax) * 49 + dy * 7 + dx] / Double(used))
            let x = ax * 7 + dx, y = (tile * 2 + ay) * 7 + dy
            let row = bitmapFirstRowIsTop ? th - 1 - y : y
            let o = (row * tw + x) * 4
            pixels[o] = v; pixels[o + 1] = v; pixels[o + 2] = v; pixels[o + 3] = 1
        } } } } }
        let tableImage = CIImage(bitmapData: pixels.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: tw * 16,
                                 size: CGSize(width: tw, height: th), format: .RGBAf, colorSpace: nil).samplingNearest()
        let delta = t.mapDelta, w = t.mapChromaLambda / max(t.mapLumaLambda, 1e-9)
        let lam = CIVector(x: CGFloat(t.mapLumaLambda), y: CGFloat(t.mapChromaLambda), z: CGFloat(t.mapChromaLambda))
        let tauY = 1 / (0.25 + 8 * t.mapLumaLambda / delta), tauC = 1 / (0.25 + 8 * t.mapChromaLambda / delta)
        let tau = CIVector(x: CGFloat(tauY), y: CGFloat(tauC), z: CGFloat(tauC))
        let tableExtent = tableImage.extent
        let roi: CIKernelROICallback = { index, rect in
            switch index {
            case 2: return rect
            case 3: return tableExtent
            default: return rect.insetBy(dx: -4, dy: -4)
            }
        }
        var x = materialize(start, extent: e), previous = x
        var tk: Double = 1, beta: Double = 0
        for _ in 0..<t.mapIterations {
            let ok: Bool = autoreleasepool {
                guard let next = mapStepKernel.apply(extent: e, roiCallback: roi, arguments: [
                    x.clampedToExtent(), previous.clampedToExtent(), b, tableImage, grid, Float(beta), lam, tau, delta, w,
                ]) else { return false }
                previous = x
                x = materialize(next, extent: e)
                return true
            }
            guard ok else { return nil }
            let tn = (1 + (1 + 4 * tk * tk).squareRoot()) / 2
            beta = (tk - 1) / tn
            tk = tn
        }
        dlog("Super resolução: \(used) fotos resolvidas juntas (MAP, \(t.mapIterations) passos)")
        return (x, used)
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
                if let cubic = warpCubic(image, transform: alignment.transform, residuals: alignment.residuals, grid: grid, extent: e) {
                    return cubic
                }
                // Borda repetida: o quadro deslocado não deixa faixa vazia (escura ou colorida) na beirada
                var out = image.clampedToExtent().transformed(by: alignment.transform)
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

    /// 16 pontos de medida (4×4) no mesmo recorte da grade 3×3 (que fica em 20%, 50% e 80%): em 14%, 38%, 62% e 86%.
    private static func measureCenters(fromGrid g: [CGPoint]) -> [CGPoint] {
        guard g.count == 9 else { return g }
        let w = (g[2].x - g[0].x) / 0.6, h = (g[6].y - g[0].y) / 0.6
        let x0 = g[0].x - 0.2 * w, y0 = g[0].y - 0.2 * h
        var out: [CGPoint] = []
        for fy in [0.14, 0.38, 0.62, 0.86] {
            for fx in [0.14, 0.38, 0.62, 0.86] {
                out.append(CGPoint(x: (x0 + w * CGFloat(fx)).rounded(), y: (y0 + h * CGFloat(fy)).rounded()))
            }
        }
        return out
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

    /// Laboratório: registra a medida de cada pedaço (para achar erro sistemático)
    static var logTiles = false

    /// Para cada foto, a transformação (deslocamento, um pouco de giro e escala) que a leva em cima da referência.
    private static func alignTransforms(frames: [CapturedFrame], refIndex: Int, reference: CIImage,
                                        centers: [CGPoint]) -> [Alignment?] {
        let alignScale: CGFloat = 0.25
        // Pedaço proporcional à foto (160 px em 2000 px, até 320 px em 4000 px+): na NOITE do Pixel (4072 px, bem
        // escura) os de 160 px erravam até 2 px, a junção recusava as fotos e o ruído ficava em 0,71 da foto única
        // Busca de ±10 px nos pedaços grandes (o grosso em dois níveis já acerta com menos de 1 px): mesma conta de antes
        let patch = min(320, max(160, Int(reference.extent.width / 12) / 16 * 16)), search = patch >= 256 ? 10 : 16
        var result = [Alignment?](repeating: nil, count: frames.count)
        result[refIndex] = Alignment(transform: .identity, residuals: [CGPoint](repeating: .zero, count: 9))
        guard let smallRef = image(from: frames[refIndex], scale: Float(alignScale)) else { return result }

        let half = CGFloat(patch / 2)
        // Medido em 16 pedaços (4×4) e não nos 9 da grade: mais medidas = giro e região mais certos com a mão
        // mexendo, e um pedaço com algo se mexendo pesa menos. O resultado volta para a grade 3×3 dos desenhos da GPU
        let measure = measureCenters(fromGrid: centers)
        // Os pedaços saem numa leitura só (um RAW aberto uma vez, em vez de dezesseis)
        let refPatches = grayPatches(reference, rects: measure.map { c in
            CGRect(x: c.x - half, y: c.y - half, width: CGFloat(patch), height: CGFloat(patch))
        })

        for i in frames.indices where i != refIndex {
            autoreleasepool {
                guard let img = image(from: frames[i]), let small = image(from: frames[i], scale: Float(alignScale)) else { return }
                // Grosso: busca nossa no centro, em ¹⁄₁₆ e depois em ¼ (até ±300 px). O Vision errava feio com a mão de verdade
                // (laboratório: andou 5 px, ele disse 28; andou 26, disse 48) e aí a busca fina não achava nada ("0/9")
                // Se o centro for liso demais para medir, parte do zero (o chute do Vision era pior que nada)
                var precise = coarseShift(ref: smallRef, img: small, scale: alignScale) ?? .zero
                var coarse = CGPoint(x: precise.x.rounded(), y: precise.y.rounded())
                // Pulo maior que a busca alcança (±300 px) é erro. As fotos do Alex andaram até 295 px: o limite antigo
                // (8% = 240 px na vertical) jogava fora um quadro bom
                let e = reference.extent
                if abs(coarse.x) > e.width * 0.12 || abs(coarse.y) > e.height * 0.12 { coarse = .zero; precise = .zero }
                // Pares (ponto na foto, ponto na referência) com precisão de fração de pixel
                var pairs: [(frame: CGPoint, ref: CGPoint)] = []
                var pairTile: [Int] = []
                let s = CGFloat(search)
                let imgPatches = grayPatches(img, rects: measure.map { c in
                    CGRect(x: c.x - half - coarse.x - s, y: c.y - half - coarse.y - s,
                           width: CGFloat(patch) + 2 * s, height: CGFloat(patch) + 2 * s)
                })
                for (k, c) in measure.enumerated() {
                    guard let refPatch = refPatches[k], let imgPatch = imgPatches[k],
                          let shift = subpixelShift(ref: refPatch, img: imgPatch, size: patch, search: search) else { continue }
                    // O que está em c na referência está em c − grosso + (u, −v) nesta foto (linhas do bitmap descem)
                    pairs.append((CGPoint(x: c.x - coarse.x + shift.x, y: c.y - coarse.y - shift.y), c))
                    pairTile.append(k)
                    if logTiles {
                        dlog(String(format: "PEDACO foto %d · %d · em %.0f, %.0f · grosso %.0f, %.0f · fino %.3f, %.3f · desloca %.3f, %.3f",
                                    i + 1, k, c.x, c.y, coarse.x, coarse.y, shift.x, shift.y, coarse.x - shift.x, coarse.y + shift.y))
                    }
                }
                // Os pedaços concordam entre si? No escuro cada pedaço pequeno erra mais de 1 px e o ajuste "inventava"
                // giro (laboratório com ruído limpo: 0,07°, que nas bordas vira 3,4 px). Então: com menos de 3 pedaços,
                // ou com eles discordando (sobra típica acima de 0,5 px), vale o pedaço grande do centro na foto cheia,
                // só deslocamento. O teste de "encaixe ambíguo" fica brando: o lugar já é conhecido (±6 px)
                var t = pairs.count >= 3 ? fitSimilarity(pairs) : nil
                // Sobra típica (a do meio: um pedaço com algo se mexendo não conta)
                let spread: CGFloat = t.map { fit in
                    let d = pairs.map { p -> CGFloat in
                        let m = p.frame.applying(fit)
                        return hypot(m.x - p.ref.x, m.y - p.ref.y)
                    }.sorted()
                    return d[d.count / 2]
                } ?? .infinity
                // Com menos de 10 dos 16 pedaços (escuro: só os com textura passam) os poucos que sobram podem concordar no
                // erro (NOITE do Pixel: 7/16, errando 0,9 px juntos por causa do carro que passa): vale o pedaço grande do
                // centro, maior nas fotos grandes
                let few = pairs.count < 10
                if t == nil || spread > 0.5 || few {
                    let size = min(768, max(512, Int(reference.extent.width / 6) / 16 * 16))
                    if let full = centerShift(ref: reference, img: img, search: 6, size: size, start: precise, ambiguity: 0.97) {
                        precise = full
                    } else {
                        dlog("Super resolução: foto \(i + 1) · centro na foto cheia não encaixou (fica o grosso)")
                    }
                    if t != nil { dlog(String(format: "Super resolução: foto %d · %@ (%.2f px): só deslocamento pelo centro", i + 1,
                                              few ? "poucos pedaços" : "pedaços discordam", spread)) }
                    t = CGAffineTransform(translationX: precise.x, y: precise.y)
                }
                let transform = t ?? CGAffineTransform(translationX: precise.x, y: precise.y)
                let trusted = spread <= 0.5 && !few
                // O que sobrou em cada pedaço depois do geral (até 1,5 px; mais que isso é algo que se mexeu),
                // levado para os 9 pontos da grade pela média dos pedaços em volta (peso cai com a distância)
                // Só os pedaços que concordam com a maioria (o que errou feio não vira "região que se mexeu")
                var measured: [(at: CGPoint, r: CGPoint)] = []
                let limit = max(0.25, 2.5 * spread)
                for (n, pair) in pairs.enumerated() where trusted {
                    let placed = pair.frame.applying(transform)
                    let r = CGPoint(x: pair.ref.x - placed.x, y: pair.ref.y - placed.y)
                    if hypot(r.x, r.y) < min(1.5, limit) { measured.append((measure[pairTile[n]], r)) }
                }
                let reachGrid = 1.2 * max(abs(centers[1].x - centers[0].x), abs(centers[3].y - centers[0].y), 1)
                let residuals = centers.map { g -> CGPoint in
                    var sum = CGPoint.zero, weight: CGFloat = 0
                    for m in measured {
                        let w = max(0, 1 - hypot(m.at.x - g.x, m.at.y - g.y) / reachGrid)
                        sum.x += m.r.x * w; sum.y += m.r.y * w; weight += w
                    }
                    return weight > 0.05 ? CGPoint(x: sum.x / weight, y: sum.y / weight) : .zero
                }
                result[i] = Alignment(transform: transform, residuals: residuals)
                let worst = residuals.map { hypot($0.x, $0.y) }.max() ?? 0
                dlog(String(format: "Super resolução: foto %d · %d/16 pedaços · desloca %.2f, %.2f px · giro %.3f° · região até %.2f px · sobra %.2f px",
                            i + 1, pairs.count, transform.tx, transform.ty, atan2(transform.b, transform.a) * 180 / .pi, worst,
                            spread.isFinite ? spread : -1))
            }
        }
        return result
    }

    /// Deslocamento grosso entre duas versões pequenas (escala `scale`): pedaço grande do centro, em dois níveis
    /// (até ±320 px na foto cheia), com a fração de pixel. Mesmo sentido do grosso do Vision (o que soma em c − grosso).
    static func coarseShift(ref: CIImage, img: CIImage, scale: CGFloat) -> CGPoint? {
        // As fotos de noite do Alex (iPhone 17 Pro Max, na mão) andaram 40–130 px entre o 1º e o último quadro, e
        // até 350 px numa delas: ±96 px não alcançava. Primeiro uma busca larga numa versão 4× menor ainda
        // (±20 px lá = ±320 px na foto cheia), depois a busca de sempre, curta, em volta dela
        var start = CGPoint.zero
        let k: CGFloat = 0.25
        func tiny(_ i: CIImage) -> CIImage {
            i.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: k, kCIInputAspectRatioKey: 1])
        }
        if let wide = centerShift(ref: tiny(ref), img: tiny(img), search: 20, size: 128, start: .zero) {
            start = CGPoint(x: wide.x / k, y: wide.y / k)
        }
        // A busca larga pode falhar (centro liso): aí a de sempre, ±24 px a partir do zero
        let near = start == .zero ? 24 : 8
        // Em volta de um lugar já achado a janela é curta: o teste de encaixe ambíguo fica mais brando
        guard let shift = centerShift(ref: ref, img: img, search: near, size: 256, start: start,
                                      ambiguity: start == .zero ? 0.8 : 0.93)
                ?? (start == .zero ? nil : centerShift(ref: ref, img: img, search: 24, size: 256, start: .zero)) else { return nil }
        // Na foto o ponto c da referência está em c − grosso: o grosso na escala cheia (com a fração)
        return CGPoint(x: shift.x / scale, y: shift.y / scale)
    }

    /// Deslocamento "grosso" (o que soma em c − grosso) entre as versões dadas, pelo pedaço do centro, buscando
    /// ±`search` px em volta de `start` (mesma escala e mesmo sentido do resultado).
    private static func centerShift(ref: CIImage, img: CIImage, search s: Int, size: Int, start: CGPoint,
                                    ambiguity: Float = 0.8) -> CGPoint? {
        let e = ref.extent
        let n = min(size, Int(min(e.width, e.height) * 0.6) / 2 * 2)
        guard n >= 48 else { return nil }
        let rect = CGRect(x: (e.midX - CGFloat(n) / 2).rounded(), y: (e.midY - CGFloat(n) / 2).rounded(), width: CGFloat(n), height: CGFloat(n))
        let o = CGPoint(x: start.x.rounded(), y: start.y.rounded())
        guard let refPatch = grayPatches(ref, rects: [rect]).first ?? nil,
              let imgPatch = grayPatches(img, rects: [rect.offsetBy(dx: -o.x, dy: -o.y).insetBy(dx: -CGFloat(s), dy: -CGFloat(s))]).first ?? nil,
              let shift = subpixelShift(ref: refPatch, img: imgPatch, size: n, search: s, ambiguity: ambiguity) else { return nil }
        // O ponto c da referência está em c − o + (u, −v) nesta foto
        return CGPoint(x: o.x - shift.x, y: o.y + shift.y)
    }

    /// Luminância (raiz, para o escuro pesar parecido com o claro) de vários pedaços, linha 0 em cima.
    /// Todos os pedaços vão lado a lado numa imagem só e saem numa leitura.
    private static func grayPatches(_ raw: CIImage, rects: [CGRect]) -> [[Float]?] {
        guard let first = rects.first else { return [] }
        // Um leve borrão antes de comparar: no escuro o ruído enganava a busca (o laboratório mostrou "deslocamentos"
        // de 13 px e giros de 0,5° em fotos que andaram menos de 1,5 px). O deslocamento continua o mesmo
        let image = raw.clampedToExtent().applyingGaussianBlur(sigma: 1.2)
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
    private static func subpixelShift(ref rawRef: [Float], img rawImg: [Float], size n: Int, search s: Int,
                                      ambiguity: Float = 0.8) -> CGPoint? {
        func normalized(_ a: [Float]) -> ([Float], Float) {
            let mean = a.reduce(0, +) / Float(a.count)
            let variance = a.reduce(0) { $0 + ($1 - mean) * ($1 - mean) } / Float(a.count)
            let std = max(variance.squareRoot(), 1e-6)
            return (a.map { ($0 - mean) / std }, variance)
        }
        let (ref, refVariance) = normalized(rawRef)
        // Pedaço liso (céu, parede) não diz nada sobre o deslocamento
        guard refVariance > 0.0004 else { return nil }
        // A foto fica sem normalizar: cada janela testada é normalizada por ela mesma (correlação normalizada de
        // verdade). Antes a janela inteira (maior) era normalizada de uma vez: com degradê (céu, chão) a mesma imagem
        // contra ela mesma dava 0,3 px de deslocamento falso em y. Em Python: erro típico 0,30 → 0,005 px
        let img = rawImg
        let wide = n + 2 * s

        // Diferença entre a referência e a janela (u, v) normalizada, olhando 1 de cada `step` pixels
        func ssd(_ u: Int, _ v: Int, step: Int) -> Float {
            var rm: Float = 0, sm: Float = 0, sm2: Float = 0, sr: Float = 0, sr2: Float = 0, count: Float = 0
            ref.withUnsafeBufferPointer { r in
                img.withUnsafeBufferPointer { m in
                    var y = 0
                    while y < n {
                        let ro = y * n, io = (y + s + v) * wide + s + u
                        var x = 0
                        while x < n {
                            let a = r[ro + x], b = m[io + x]
                            rm += a * b; sm += b; sm2 += b * b; sr += a; sr2 += a * a
                            count += 1
                            x += step
                        }
                        y += step
                    }
                }
            }
            let mean = sm / count
            let sd = max((sm2 / count - mean * mean).squareRoot(), 1e-6)
            return sr2 + count - 2 / sd * (rm - mean * sr)
        }

        // 1) Busca larga de 2 em 2 pixels, olhando 1 de cada 2
        var best = (u: 0, v: 0, cost: Float.greatestFiniteMagnitude)
        var costSum: Float = 0, costCount: Float = 0
        for v in stride(from: -s + 2, through: s - 2, by: 2) {
            for u in stride(from: -s + 2, through: s - 2, by: 2) {
                let c = ssd(u, v, step: 2)
                costSum += c
                costCount += 1
                if c < best.cost { best = (u, v, c) }
            }
        }
        // Encaixe ambíguo (o melhor quase igual à média, típico de pedaço liso com ruído): não serve
        guard best.cost < ambiguity * costSum / max(costCount, 1) else { return nil }
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
        let start = (u: Float(fine.u) + du, v: Float(fine.v) + dv)
        // A parábola "gruda" no pixel inteiro (no laboratório escuro: 18,6 → 18,97; 140,6 → 141,07). Lucas–Kanade
        // em cima dela acha a fração pelo gradiente, sem esse vício
        let refined = lucasKanade(ref: ref, img: img, size: n, search: s, start: start)
        return CGPoint(x: CGFloat(refined.u), y: CGFloat(refined.v))
    }

    /// Refino da fração de pixel por Lucas–Kanade (3 passos), no mesmo sentido do `subpixelShift`: o pixel (x, y)
    /// da referência cai em (x + s + u, y + s + v) do pedaço maior. Se sair a mais de 1 px do começo, fica o começo.
    private static func lucasKanade(ref: [Float], img: [Float], size n: Int, search s: Int,
                                    start: (u: Float, v: Float)) -> (u: Float, v: Float) {
        let wide = n + 2 * s
        var u = start.u, v = start.v
        img.withUnsafeBufferPointer { m in
            ref.withUnsafeBufferPointer { r in
                func sample(_ x: Float, _ y: Float) -> Float {
                    let x0 = Int(x.rounded(.down)), y0 = Int(y.rounded(.down))
                    guard x0 >= 0, y0 >= 0, x0 + 1 < wide, y0 + 1 < wide else { return 0 }
                    let fx = x - Float(x0), fy = y - Float(y0)
                    let o = y0 * wide + x0
                    let top = m[o] + (m[o + 1] - m[o]) * fx
                    let bottom = m[o + wide] + (m[o + wide + 1] - m[o + wide]) * fx
                    return top + (bottom - top) * fy
                }
                for _ in 0..<3 {
                    // A janela da foto normalizada por ela mesma (média e desvio), como a referência
                    var sm: Float = 0, sm2: Float = 0, count: Float = 0
                    for y in 2..<(n - 2) {
                        let py = Float(y + s) + v
                        for x in 2..<(n - 2) {
                            let val = sample(Float(x + s) + u, py)
                            sm += val; sm2 += val * val; count += 1
                        }
                    }
                    let mean = sm / count
                    let inv = 1 / max((sm2 / count - mean * mean).squareRoot(), 1e-6)
                    var axx: Float = 0, axy: Float = 0, ayy: Float = 0, bx: Float = 0, by: Float = 0
                    // Uma borda de 2 px fica de fora (o gradiente precisa dos vizinhos)
                    for y in 2..<(n - 2) {
                        let py = Float(y + s) + v
                        for x in 2..<(n - 2) {
                            let px = Float(x + s) + u
                            let gx = (sample(px + 1, py) - sample(px - 1, py)) * 0.5 * inv
                            let gy = (sample(px, py + 1) - sample(px, py - 1)) * 0.5 * inv
                            let e = r[y * n + x] - (sample(px, py) - mean) * inv
                            axx += gx * gx; axy += gx * gy; ayy += gy * gy
                            bx += gx * e; by += gy * e
                        }
                    }
                    let det = axx * ayy - axy * axy
                    guard det > 1e-6 else { break }
                    let dx = (ayy * bx - axy * by) / det, dy = (axx * by - axy * bx) / det
                    u += dx; v += dy
                    if abs(dx) < 0.005 && abs(dy) < 0.005 { break }
                }
            }
        }
        guard u.isFinite, v.isFinite, abs(u - start.u) <= 1, abs(v - start.v) <= 1 else { return start }
        return (u, v)
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
        func residual(_ p: (frame: CGPoint, ref: CGPoint), _ t: CGAffineTransform) -> CGFloat {
            let m = p.frame.applying(t)
            return hypot(m.x - p.ref.x, m.y - p.ref.y)
        }
        var kept = pairs.filter { residual($0, t) < 1.5 }
        if kept.count >= 3, kept.count < pairs.count, let refit = fit(kept) { t = refit }
        // Robusto: os pedaços que discordam da maioria (céu liso, reflexo na água) saem e a conta é refeita.
        // No laboratório 11 de 16 pedaços acertavam 0,001 px e 5 erravam 0,2–1,8 px: esses puxavam tudo (giro falso,
        // sobra de 0,24 px, até 1,5 dB a menos no SUPER ZOOM)
        for _ in 0..<2 {
            let r = kept.map { residual($0, t) }.sorted()
            guard r.count >= 4 else { break }
            let limit = max(0.12, 2.5 * r[r.count / 2])
            let inliers = kept.filter { residual($0, t) <= limit }
            guard inliers.count >= 4, inliers.count < kept.count, let refit = fit(inliers) else { break }
            kept = inliers
            t = refit
        }
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
        // 0,95: no SUPER ZOOM o HEIC 0,9 sozinho errava quase o que a super resolução ganha (Pixel: 42 dB vs 40 dB)
        var props: [CFString: Any] = [kCGImageDestinationLossyCompressionQuality: 0.95]
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
    /// Desconvolução regularizada (FISTA): minimiza ‖P·x − observada‖² + Σ λ·Huber(|∇u|), u = cor em brilho/2 cores.
    /// P = caixa 2×2 do sensor (binomial 3×3) ⊗ gaussiana 0,45 px (simétrica: a transposta é ela mesma)
    /// Restauração com Huber-TV (FISTA): minimiza ‖P·x − observada‖² + Σ λ·Huber(|∇u|), u = cor em brilho/2 cores.
    /// P = (caixa 2×2 do sensor, se `box`) ⊗ gaussiana `sigma` (0 = nenhuma: só tira ruído). Faixa `rect` com margem.
    static func tvRestore(_ image: CIImage, strip rect: CGRect, extent: CGRect, box: Bool, sigma: Double,
                          luma: Float, chroma: Float, delta: Float = 0.01, iterations: Int) -> CIImage? {
        guard iterations > 0, let tvFluxKernel, let tvStepKernel, let momentumKernel, let subKernel = srSubKernel else { return nil }
        let margin = CGFloat(6 * iterations + 8)
        let big = rect.insetBy(dx: 0, dy: -margin).intersection(extent).integral
        let observed = materialize(image.cropped(to: big), extent: big)
        func psf(_ x: CIImage) -> CIImage {
            var y = x.clampedToExtent()
            if box {
                y = y.applyingFilter("CIConvolution3X3", parameters: [
                    "inputWeights": CIVector(values: [1, 2, 1, 2, 4, 2, 1, 2, 1].map { $0 / 16 }, count: 9), "inputBias": 0])
            }
            if sigma > 0.05 { y = y.applyingGaussianBlur(sigma: sigma) }
            return y.cropped(to: big)
        }
        let lam = CIVector(x: CGFloat(luma), y: CGFloat(chroma), z: CGFloat(chroma))
        // FISTA só converge com passo ≤ 1/L (L = 1 do borrão normalizado + 8λ/δ da Huber-TV); 1,8/L estourava com λ pequeno
        let tau = Float(1 / (1 + 8 * Double(max(luma, chroma)) / Double(delta)))
        let roi: CIKernelROICallback = { _, r in r.insetBy(dx: -2, dy: -2) }
        var x = observed, z = observed
        var tk: Float = 1
        for _ in 0..<iterations {
            // Cada passo num pool próprio: os buffers de render de um passo não se acumulam até o fim da faixa
            let ok: Bool = autoreleasepool {
                guard let residual = subKernel.apply(extent: big, arguments: [psf(z), observed]),
                      let fx = tvFluxKernel.apply(extent: big, roiCallback: roi, arguments: [z.clampedToExtent(), delta, Float(0)]),
                      let fy = tvFluxKernel.apply(extent: big, roiCallback: roi, arguments: [z.clampedToExtent(), delta, Float(1)]) else { return false }
                let dataGrad = materialize(psf(materialize(residual, extent: big)), extent: big)
                guard let next = tvStepKernel.apply(extent: big, roiCallback: roi, arguments: [
                    z.clampedToExtent(), materialize(fx, extent: big).clampedToExtent(), materialize(fy, extent: big).clampedToExtent(),
                    dataGrad.clampedToExtent(), lam, tau]) else { return false }
                let xn = materialize(next, extent: big)
                let tn = (1 + (1 + 4 * tk * tk).squareRoot()) / 2
                guard let zn = momentumKernel.apply(extent: big, arguments: [xn, x, (tk - 1) / tn]) else { return false }
                z = materialize(zn, extent: big)
                x = xn
                tk = tn
                return true
            }
            guard ok else { return nil }
        }
        return x.cropped(to: rect)
    }

    /// A mesma restauração na foto inteira, em faixas de 512 linhas (memória: cada faixa só vive dentro do laço)
    static func tvRestoreStrips(_ image: CIImage, extent: CGRect, box: Bool, sigma: Double, luma: Float, chroma: Float,
                                iterations: Int) -> CIImage? {
        let e = extent.integral
        var out = CIImage(color: .clear).cropped(to: e)
        var y = e.minY
        while y < e.maxY {
            let rows = min(512, e.maxY - y)
            let rect = CGRect(x: e.minX, y: y, width: e.width, height: rows)
            var ok = true
            autoreleasepool {
                if let strip = tvRestore(image, strip: rect, extent: e, box: box, sigma: sigma, luma: luma, chroma: chroma,
                                         iterations: iterations) {
                    out = strip.composited(over: out)
                } else { ok = false }
            }
            guard ok else { return nil }
            y += rows
        }
        return materialize(out, extent: e)
    }

    private static func deconvolved(_ image: CIImage, strip rect: CGRect, extent: CGRect, iterations: Int, sigma: Double) -> CIImage {
        let t = srTuning
        if t.tv, iterations > 0, let tv = tvRestore(image, strip: rect, extent: extent, box: true, sigma: 0.45,
                                                    luma: t.tvLumaLambda, chroma: t.tvChromaLambda, delta: t.tvDelta,
                                                    iterations: t.tvIterations) { return tv }
        guard iterations > 0, let ratioKernel, let multiplyKernel else { return image.cropped(to: rect) }
        let margin = CGFloat(ceil(sigma * 3 * 2 * Double(iterations))) + 4
        let big = rect.insetBy(dx: 0, dy: -margin).intersection(extent).integral
        let observed = materialize(image.cropped(to: big), extent: big)
        var estimate = observed
        func blur(_ x: CIImage) -> CIImage { x.clampedToExtent().applyingGaussianBlur(sigma: sigma).cropped(to: big) }
        for _ in 0..<iterations {
            let ok: Bool = autoreleasepool {
                guard let ratio = ratioKernel.apply(extent: big, arguments: [observed, blur(estimate)]),
                      let next = multiplyKernel.apply(extent: big, arguments: [estimate, blur(ratio)]) else { return false }
                estimate = materialize(next, extent: big)
                return true
            }
            guard ok else { break }
        }
        if t.chromaClean > 0, let clean = tvRestore(estimate, strip: rect, extent: big, box: false, sigma: 0, luma: 0,
                                                     chroma: t.chromaClean, iterations: 20) {
            return clean
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
