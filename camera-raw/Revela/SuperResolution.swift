import CoreImage
import CoreVideo
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

    /// Calibragem da super resolução (o laboratório testa variações; o app usa a padrão).
    struct SRTuning {
        /// Núcleo de cada pixel na grade grande (regressão de núcleo, a junção da SUPER RES), em pixels DA FOTO: este valor
        /// ÷ √fotos, preso em 0,22–0,55. Antes era fixo em pixels grandes (0,45): na SUPER RES (ampliação 1,43×) dava 0,31 px
        /// da foto, quase vizinho mais próximo, com buracos entre as 6 fotos. Com 24 fotos fica 0,245 px da foto (0,49 px
        /// grande no 2×), perto dos 0,45 que o laboratório escolheu com a RL (86ab1f0: +4,12/+6,09/+4,48 dB)
        var splatSigma: Double = 1.2
        /// Borrão da desconvolução final, × o fator de ampliação.
        // 0,45 × fator com 3 passos (laboratório b22822c: +1,85/+2,67/+1,84 dB contra +1,66/+1,98/+1,73 com 0,35 × 2)
        var deconvScale: Double = 0.4
        var deconvIterations = 3
        /// Anti-fantasma da regressão de núcleo: escala do limite do mapa de movimento (0,1 = o padrão; maior aceita mais
        /// diferença). O mapa compara versões borradas: antes a regra era no pixel e com ISO 800+ recusava o próprio ruído
        var ghostK: Float = 0.1
        /// Limpeza de brilho depois da desconvolução (× o ruído medido na junção). A desconvolução realça o ruído e a
        /// super resolução não tinha limpeza nenhuma (a foto ampliada de comparação tem o ruído suavizado pela ampliação)
        var denoise: Float = 0
        /// Desconvolução regularizada (Huber-TV, brilho/cor) em vez da Richardson–Lucy. Estudo em Python nas 24 fotos
        /// do laboratório: +5,4 dB (RL × 3: +4,5; RL × 10: +4,9). Borradura: caixa 2×2 do sensor ⊗ gaussiana 0,45 px
        // No app (86ab1f0) só ganhava no iPhone 12 Pro (+4,77) e perdia no XS (+4,72) e no Pixel (+4,30): fica desligada
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
        /// Anti-fantasma do MAP: escala do limite do mapa de movimento (0,5 = o padrão; 1000 = nada é recusado). A amostra
        /// recusada vira a referência. O mapa compara versões borradas (1,5 px da foto): o serrilhado some e só movimento de
        /// verdade passa do limite. Na regra antiga (no pixel, sem borrar), 0,1 fazia o serrilhado das bordas virar
        /// "fantasma" e a referência ampliada (borrada) entrava (laboratório ea18328: XS +1,93, iPhone 12 +3,65)
        var mapGhostK: Float = 0.5
        /// λ pelo ruído medido e pelo número de fotos (o dado é ÷ K: λ ∝ σ²/K). Calibrado no laboratório com 24 fotos; o ruído
        /// é o do modelo ajustado na rajada (diferença borrada dos mapas de movimento, na luz média), estimado ≈ mapNoiseRef no
        /// laboratório (ruído ±0,01 nas fotos pequenas). O registro mostra o medido para acertar este número
        var mapAutoLambda = true
        var mapNoiseRef: Float = 0.0016
        /// Tons locais, cor pela luz e nitidez da FOTO (enhanced), com o ISO de uma foto com a luz de todas. O laboratório
        /// desliga: ele mede contra a cena revelada sem isso
        var enhance = true
    }
    static var srTuning = SRTuning()

    /// Alinhamento de uma foto: o geral (deslocamento, giro, escala) e o que sobrou em cada um dos 9 pedaços.
    struct Alignment {
        var transform: CGAffineTransform
        /// Correção por região, em pixels da foto (0 onde o pedaço não deu ou discordou).
        var residuals: [CGPoint]
    }

    /// `keep`: tira mais fotos do que usa e fica com pelo menos essas (as mais nítidas). `moon`: LUA — a nitidez é medida
    /// onde está a Lua (a parte mais clara), não no centro (céu preto quando ela está fora do meio: todas empatavam no
    /// ruído), e sem os tons locais da FOTO (o ajuste de luz clarearia o céu preto e estouraria a Lua)
    static func superResolution(_ captured: [CapturedFrame], options: DevelopOptions, keep: Int? = nil,
                                moon: Bool = false) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard captured.count >= 2 else { return captured.first.flatMap { develop($0, options: options) } }
        // Abertas sem a redução de ruído e a nitidez do RAW: a junção tira o ruído e o MAP desfaz o borrão
        let allFrames = captured.map { frame -> CapturedFrame in
            var f = frame
            f.merge = true
            return f
        }

        // As mais nítidas (as tremidas só borrariam a soma); a referência é a mais nítida de todas
        // Nitidez num pedaço de 512 px de uma versão em ¼ (em ⅛ a foto tremida passava, como na NOITE). Na LUA o pedaço é
        // ~3× a Lua (medida na 1ª foto, o mesmo em todas para as notas compararem): com 512 px em ¼ a Lua (~26–31 px) era
        // 1/20 do pedaço, o ruído do céu mandava na nota e a foto com turbulência passava dos 85%
        let moonSide: CGFloat? = moon ? allFrames.first.flatMap { image(from: $0, scale: 0.25) }.map { moonWindow($0) } : nil
        let allScores = allFrames.map { frame -> Float in
            guard let small = image(from: frame, scale: 0.25) else { return 0 }
            let e = small.extent
            let side = min(moonSide ?? 512, e.width, e.height)
            let c = moon ? brightestPoint(small) : CGPoint(x: e.midX, y: e.midY)
            let x = min(max(c.x - side / 2, e.minX), e.maxX - side), y = min(max(c.y - side / 2, e.minY), e.maxY - side)
            return sharpnessScore(small.cropped(to: CGRect(x: x.rounded(), y: y.rounded(), width: side, height: side)))
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
        // A mais nítida que encaixa nas outras (a de puro ruído tem o laplaciano mais alto: trustedReference)
        var refIndex = trustedReference(frames, scores: scores)
        guard let reference = image(from: frames[refIndex]) else { return nil }
        let full = reference.extent
        var cropOptions = options
        cropOptions.originalAspect = false
        let region = cropOptions.cropRect(in: full)
        let factor = CGFloat(min(2, max(1, (superResolutionTarget / Double(region.width * region.height)).squareRoot())))
        let outExtent = CGRect(x: 0, y: 0, width: (region.width * factor).rounded(.down), height: (region.height * factor).rounded(.down))
        let outPixels = Double(outExtent.width * outExtent.height)
        // MAP (ampliação 2×) na foto inteira até 25 MP; acima (SUPER RES no 2×, XPAN, RAW puro na 1×, LUA de 48 MP: 48–96 MP)
        // em faixas com margem. Na foto inteira ele guardava 5–6 imagens do tamanho da final em meia precisão (2,3–3,8 GB),
        // fora da conta de memória
        let useMAP = srTuning.map && factor > 1.99
        let stripMAP = useMAP && outPixels > 25_000_000
        let stripPixels = 8_000_000.0
        dlog(String(format: "Super resolução: %d fotos (referência %d) · recorte %.0f×%.0f · ampliação %.2f× → %.0f×%.0f%@",
                    frames.count, refIndex + 1, region.width, region.height, factor, outExtent.width, outExtent.height,
                    stripMAP ? " · MAP em faixas" : ""))

        // Memória: cada foto guardada pronta custa recorte × 8 bytes. Por cima: a referência ampliada pronta, o MAP (b, Σh, x,
        // anterior, z e o próximo: 6 do tamanho dele, inteiro ou faixa), a faixa da gravação e os mapas de movimento. Com 24
        // fotos a 8× chegava a ~1,4 GB (o iPhone mata o app). Fica com as mais nítidas que cabem: pelo menos `keep` (sem
        // `keep`, todas; antes caía para 2 quando a conta dava negativa, como na LUA de 48 MP)
        let padFull = 0.1 * max(full.width, full.height)
        let sourceFit = region.insetBy(dx: -padFull, dy: -padFull).intersection(full).integral
        let perFrame = Double(sourceFit.width * sourceFit.height) * 8
        // (a referência ampliada só entra na reserva: o MAP tira a amostra recusada em vez de trocá-la por ela)
        let refBytes = 0.0
        let mapBytes = useMAP ? 6 * 8 * (stripMAP ? stripPixels * 1.3 : outPixels) : 0
        let workBytes = stripPixels * 8 * (useMAP ? 3 : 5)
        let motionBytes = 300_000_000.0
        // Proporcional à memória livre de verdade (o 17 Pro Max tem bem mais que os 700 MB fixos de antes, que cortavam para
        // 12 fotos uma cena de 12 MP), até 1,5 GB só de fotos
        #if targetEnvironment(simulator)
        let available = 4_000_000_000.0  // o simulador não tem limite (e devolve ~0)
        #else
        let available = Double(os_proc_available_memory())
        #endif
        let freeBytes = available > 0 ? available : 2_500_000_000
        let budget = min(1_500_000_000, freeBytes * 0.6 - refBytes - mapBytes - workBytes - motionBytes)
        let minimum = min(frames.count, max(2, keep ?? frames.count))
        let fit = max(minimum, Int(max(0, budget) / max(perFrame, 1)))
        if frames.count > fit {
            // A referência escolhida fica (a de ruído pode ser a mais nítida e entrar entre as que cabem)
            let refFrame = refIndex
            var keepIndices = Array(frames.indices.sorted { scores[$0] > scores[$1] }.prefix(fit))
            if !keepIndices.contains(refFrame), !keepIndices.isEmpty { keepIndices[keepIndices.count - 1] = refFrame }
            let ranked = keepIndices.sorted()
            frames = ranked.map { frames[$0] }
            scores = ranked.map { scores[$0] }
            refIndex = ranked.firstIndex(of: refFrame) ?? 0
            dlog("Super resolução: memória livre \(Int(available / 1e6)) MB → ficam \(fit) fotos")
        }

        // 1) Alinhamento: grosso pela nossa busca, fino (fração de pixel) em 16 pedaços, e o que sobra em cada região.
        // Foto em que nada encaixou fica de fora (nil)
        let centers = tileCenters(in: region)
        let alignments = alignTransforms(frames: frames, refIndex: refIndex, reference: reference, centers: centers)
        dlog("Super resolução: alinhado em \(Diagnostics.ms(since: t0)) (\(alignments.compactMap { $0 }.count)/\(frames.count) fotos)")

        let toRegion = CGAffineTransform(translationX: -region.minX * factor, y: -region.minY * factor)
        // Cada RAW aberto uma vez só: o pedaço que interessa vai para a memória de vídeo. Sem isso, cada faixa da
        // foto gigante abria as 10 fotos de novo. Só quando cabe (no SUPER ZOOM o recorte é pequeno)
        let source = sourceFit
        let prepare = perFrame * Double(frames.count) <= budget
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

        // 2) Mapa de movimento de cada foto (guardado): a foto alinhada na grade da referência e borrada 1,25 px contra a
        // referência borrada (estudo em Python no SUPER ZOOM: 1–1,5 px; com 0,7 o serrilhado passava). z = |ΔY| / √var,
        // var = ruído da rajada pela luz (a·Y + b, ajustado em até 2 fotos) + (0,1 px de erro de encaixe × gradiente)²;
        // g = 1 até z = 3 e 0 a partir de 5, recusa alargada 2 px e alisada 1 px. Sem exceção para o estourado.
        // Na escala da foto quando cabe (laboratório, rajadas pequenas); na de 24 fotos do SUPER ZOOM, ~0,7
        let tolerance = useMAP ? srTuning.mapGhostK / 0.5 : srTuning.ghostK / 0.1
        let regionPixels = Double(region.width * region.height)
        let ms = CGFloat(min(1, max(0.25, (motionBytes / (Double(frames.count) * regionPixels * 8)).squareRoot())))
        let mRegion = CGRect(x: region.minX * ms, y: region.minY * ms, width: region.width * ms, height: region.height * ms).integral
        let mGrid = CIVector(x: centers[0].x * ms, y: centers[0].y * ms, z: (centers[1].x - centers[0].x) * ms,
                             w: (centers[3].y - centers[0].y) * ms)
        let mBlur = Double(max(0.6, 1.25 * ms))
        var motions = [CIImage?](repeating: nil, count: frames.count)
        // Ruído para o λ do MAP: o do modelo ajustado, na luz média da referência (fotos alinhadas: a textura não conta, ao
        // contrário do ruído medido numa foto só; borradas: o serrilhado, que muda de foto para foto, também não)
        var frameNoise: Float = 0
        let tMotion = CFAbsoluteTimeGetCurrent()
        if let small = image(from: frames[refIndex], scale: Float(ms)) {
            let refSmall = materialize(small.clampedToExtent().applyingGaussianBlur(sigma: mBlur).cropped(to: mRegion), extent: mRegion)
            func blurredFrame(_ i: Int) -> CIImage? {
                guard let a = alignments[i], let img = image(from: frames[i], scale: Float(ms)) else { return nil }
                let toSmall = CGAffineTransform(scaleX: 1 / ms, y: 1 / ms).concatenating(a.transform)
                    .concatenating(CGAffineTransform(scaleX: ms, y: ms))
                let r = a.residuals.map { CGPoint(x: $0.x * ms, y: $0.y * ms) }
                guard let warped = warpCubic(img, transform: toSmall, residuals: r, grid: mGrid, extent: mRegion) else { return nil }
                return warped.clampedToExtent().applyingGaussianBlur(sigma: mBlur).cropped(to: mRegion)
            }
            var fits: [(a: Float, b: Float)] = []
            // As (até) 2 fotos do ajuste do ruído ficam prontas e servem de novo para o mapa delas (antes o encaixe e o borrão
            // eram feitos duas vezes nessas fotos)
            var fitted: [Int: CIImage] = [:]
            for i in frames.indices where i != refIndex && fits.count < 2 {
                autoreleasepool {
                    guard let f = blurredFrame(i) else { return }
                    let ready = materialize(f, extent: mRegion)
                    fitted[i] = ready
                    if let m = noiseModel(ready, refSmall, extent: mRegion) { fits.append(m) }
                }
            }
            if !fits.isEmpty {
                let sumA = fits.reduce(Float(0)) { $0 + $1.a }, sumB = fits.reduce(Float(0)) { $0 + $1.b }
                let model: (a: Float, b: Float) = (a: sumA / Float(fits.count), b: sumB / Float(fits.count))
                for i in frames.indices where i != refIndex {
                    autoreleasepool {
                        guard let f = fitted.removeValue(forKey: i) ?? blurredFrame(i),
                              let g = motionWeights(f, refSmall, extent: mRegion, model: model, misregistration: Float(0.1 * ms),
                                                    lo: 3 * tolerance, hi: 5 * tolerance, erosion: Float(max(1, 2 * ms)),
                                                    smooth: Double(max(0.5, ms))) else { return }
                        motions[i] = materialize(g, extent: mRegion)
                    }
                }
                let average = refSmall.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: mRegion)])
                let one = average.transformed(by: CGAffineTransform(translationX: -average.extent.minX, y: -average.extent.minY))
                var pixel = [Float](repeating: 0, count: 4)
                gpu.render(one, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                               format: .RGBAf, colorSpace: nil)
                let meanY = max(0, 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2])
                frameNoise = (model.a * (meanY.isFinite ? meanY : 0) + model.b).squareRoot()
                // O tempo dos mapas e o total desde o começo (antes só o total: lido como se fosse o dos mapas)
                dlog(String(format: "Super resolução: mapas de movimento em %.2f× · ruído a %.2e b %.2e · σ na luz média %.4f · mapas %@ · total %@",
                            ms, model.a, model.b, frameNoise, Diagnostics.ms(since: tMotion), Diagnostics.ms(since: t0)))
            } else {
                dlog("Super resolução: sem medida de ruído na rajada: nenhuma foto recusada por movimento")
            }
        }
        let smallToOut = CGAffineTransform(scaleX: 1 / ms, y: 1 / ms)
            .concatenating(CGAffineTransform(translationX: -region.minX, y: -region.minY))
            .concatenating(CGAffineTransform(scaleX: factor, y: factor))
        let allSame = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: outExtent)
        func motionOut(_ i: Int) -> CIImage {
            guard motions.indices.contains(i), let m = motions[i] else { return allSame }
            return m.clampedToExtent().transformed(by: smallToOut).cropped(to: outExtent)
        }

        // 3) Junção. MAP (2×): todas as fotos de uma vez; senão regressão de núcleo (cada pixel no lugar exato) + RL
        var scene: ((CGRect) -> CIImage?)?
        var used = 1
        var solved = false, splatted = false
        var merged: CIImage?
        if useMAP {
            if let plan = mapSolver(frames: frames, decoded: decoded, alignments: alignments, motion: motionOut,
                                    region: region, factor: factor, grid: grid, centers: centers, noise: frameNoise) {
                if stripMAP {
                    // Cada faixa resolvida com margem: cada passo olha ±3 px, 16 passos = 48 px; a margem é maior
                    let margin = CGFloat(3 * srTuning.mapIterations + 24)
                    let fallback = splatMerge(frames: frames, decoded: decoded, alignments: alignments, motion: motionOut,
                                              region: region, factor: factor, outExtent: outExtent, grid: grid)?.image
                    // A faixa de reserva leva a mesma desconvolução da regressão de núcleo (3 passos, 0,4 × o fator): sem ela
                    // saía uma faixa visivelmente mais mole no meio da foto resolvida pelo MAP
                    let fallbackSteps = srTuning.deconvIterations + (moon ? 1 : 0)
                    let fallbackSigma = srTuning.deconvScale * Double(factor)
                    scene = { rect in
                        let big = rect.insetBy(dx: 0, dy: -margin).intersection(outExtent).integral
                        if let x = plan.solve(big) { return x.cropped(to: rect) }
                        dlog("⚠️ Super resolução: faixa do MAP sem memória; essa faixa vai pela regressão de núcleo + desconvolução")
                        return fallback.map { deconvolved($0, strip: rect, extent: outExtent, iterations: fallbackSteps, sigma: fallbackSigma) }
                    }
                    used = plan.used
                    solved = true
                } else if let x = plan.solve(outExtent) {
                    scene = { rect in x.cropped(to: rect) }
                    used = plan.used
                    solved = true
                } else {
                    dlog("⚠️ Super resolução: o MAP não coube na memória; vai pela regressão de núcleo")
                }
            }
        }
        if !solved {
            if let splat = splatMerge(frames: frames, decoded: decoded, alignments: alignments, motion: motionOut,
                                      region: region, factor: factor, outExtent: outExtent, grid: grid) {
                merged = splat.image
                used = splat.used
                splatted = true
            } else if let robustColorKernel, let robustWeightKernel, let divideKernel, let refUp = upscaled(refIndex) {
                // Reserva (kernel novo não carregou): cada foto ampliada, junção robusta (onde algo se mexeu fica a referência)
                let refBlur = blurred(refUp, extent: outExtent)
                var sumColor = refUp
                var sumWeight = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: outExtent)
                for i in frames.indices where i != refIndex {
                    guard let up = upscaled(i) else { continue }
                    let upBlur = blurred(up, extent: outExtent)
                    guard let color = robustColorKernel.apply(extent: outExtent, arguments: [up, upBlur, refBlur, Float(0.1)]),
                          let weight = robustWeightKernel.apply(extent: outExtent, arguments: [upBlur, refBlur, Float(0.1)]) else { continue }
                    sumColor = add(sumColor, color)
                    sumWeight = add(sumWeight, weight)
                    used += 1
                }
                merged = divideKernel.apply(extent: outExtent, arguments: [sumColor, sumWeight])
            }
        } else if !stripMAP {
            // Resolvido na foto inteira: as fotos guardadas e os mapas saem da memória antes da gravação
            cache.removeAll()
            motions = motions.map { _ in nil }
        }

        var opts = options
        opts.zoom = 1
        opts.originalAspect = true
        // O brilho em volta das luzes é calculado na foto inteira e aqui ela é revelada em faixas: fica de fora
        opts.noGlow = true
        let properties = reference.properties

        // 4) Foto gigante revelada em faixas, cada uma desconvoluída (desfaz o borrão da lente e da ampliação)
        // Do 5º passo em diante quase não muda nada e cada passo custa o mesmo: 4 bastam (Lua: 6)
        // Depois da regressão de núcleo só falta um pouco: 3 passos com borrão de 0,4 × o fator (protótipo:
        // o borrão antigo de 1,35 px com 4 passos tirava 1,5 dB). Lua um passo a mais
        // O MAP já desfez o borrão do sensor e da lente: sem desconvolução depois
        let iterations = solved ? 0 : (splatted ? srTuning.deconvIterations + (moon ? 1 : 0) : (moon ? 6 : 4))
        let sigma = splatted ? srTuning.deconvScale * Double(factor) : Double(0.55 * factor + 0.25)
        if scene == nil, let merged {
            scene = { rect in deconvolved(merged, strip: rect, extent: outExtent, iterations: iterations, sigma: sigma) }
        }
        guard let scene else { return nil }
        // Ruído da junção (antes da desconvolução, que o realça ~1,5×) para a limpeza final
        let cleanup = srTuning.denoise
        var noise: Float = 0
        if cleanup > 0 {
            let side = min(512, outExtent.height)
            if let probe = scene(CGRect(x: 0, y: (outExtent.midY - side / 2).rounded(), width: outExtent.width, height: side)) {
                noise = measuredNoise(probe) * 1.5
            }
            dlog(String(format: "Super resolução: limpeza %.2f · ruído medido %.4f", cleanup, noise))
        }
        // Revelada como a FOTO (tons locais, cor pela luz, nitidez), com o ISO de uma foto com a luz de todas. A luz de fundo
        // dos tons locais vem da referência pequena (borrada de qualquer jeito): calculada uma vez, não em cada faixa
        let effectiveISO = max(25, isoOf(reference) / Float(max(used, 1)))
        var tonePreview: CIImage?
        if srTuning.enhance, !moon, let small = image(from: frames[refIndex], scale: 0.125) {
            let k: CGFloat = 0.125
            let r = CGRect(x: region.minX * k, y: region.minY * k, width: region.width * k, height: region.height * k)
                .integral.intersection(small.extent)
            if r.width >= 8, r.height >= 8 {
                let pe = CGRect(origin: .zero, size: r.size)
                tonePreview = materialize(small.cropped(to: r).transformed(by: CGAffineTransform(translationX: -r.minX, y: -r.minY)), extent: pe)
            }
        }
        let grade: (CIImage) -> CIImage = { canvas in
            var s = canvas.settingProperties(properties)
            if cleanup > 0 { s = lumaDenoise(s, strength: cleanup, noise: noise * cleanup) }
            if let tonePreview {
                s = enhanced(withISO(s, effectiveISO), preview: tonePreview).settingProperties(properties)
            }
            return developed(s, options: opts).0
        }
        // Margem das faixas para o que olha os vizinhos na revelação (limpeza de cor até 18 px, nitidez): sem emenda
        guard let heic = renderInStrips(extent: outExtent, properties: properties, stripPixels: stripPixels,
                                        margin: tonePreview == nil && cleanup <= 0 ? 0 : 24, scene: scene, grade: grade) else {
            dlog("❌ Super resolução: não consegui gravar a foto")
            return nil
        }
        dlog(String(format: "Super resolução revelada: %d fotos · %.0f MP · %@ · %@ · %@ · memória livre %@", used,
                    outExtent.width * outExtent.height / 1_000_000, "\(heic.count / 1_048_576) MB",
                    solved ? "MAP" : "desconvolução \(iterations) passos", Diagnostics.ms(since: t0), Diagnostics.freeMemory))
        return Output(heic: heic, thumbnail: thumbnail(fromHEIC: heic), sameSizeAsRaw: false)
    }

    /// Junta as fotos por regressão de núcleo: para cada pixel da foto grande, os 16 pixels mais perto de cada foto
    /// (já no lugar pelo alinhamento) entram com peso pela distância; onde o mapa de movimento diz que a foto não bate
    /// (algo se mexeu), ela quase não conta. O peso sai de um kernel que não abre a foto
    private static func splatMerge(frames: [CapturedFrame], decoded: (Int) -> CIImage?, alignments: [Alignment?],
                                   motion: (Int) -> CIImage, region: CGRect, factor: CGFloat, outExtent: CGRect,
                                   grid: CIVector) -> (image: CIImage, used: Int)? {
        guard let splatKernel, let splatWeightKernel, let divideKernel else { return nil }
        let usable = frames.indices.filter { alignments[$0] != nil }.count
        let sigmaFrame = min(0.55, max(0.22, srTuning.splatSigma / Double(max(usable, 1)).squareRoot()))
        let sigmaOut = CGFloat(sigmaFrame) * factor
        var colorSum: CIImage?, weightSum: CIImage?
        var used = 0
        for i in frames.indices {
            guard let a = alignments[i], let src = decoded(i) else { continue }
            let inv = a.transform.inverted()
            var r = a.residuals.map { CGPoint(x: $0.x * factor, y: $0.y * factor) }
            if r.count != 9 { r = Array(repeating: .zero, count: 9) }
            let reach = (r.map { max(abs($0.x), abs($0.y)) }.max() ?? 0) / factor + 4
            let roi: CIKernelROICallback = { index, rect in
                if index != 0 { return rect.insetBy(dx: -2, dy: -2) }
                let corners = [CGPoint(x: rect.minX, y: rect.minY), CGPoint(x: rect.maxX, y: rect.minY),
                               CGPoint(x: rect.minX, y: rect.maxY), CGPoint(x: rect.maxX, y: rect.maxY)]
                    .map { CGPoint(x: $0.x / factor + region.minX, y: $0.y / factor + region.minY).applying(inv) }
                let xs = corners.map(\.x), ys = corners.map(\.y)
                return CGRect(x: xs.min()!, y: ys.min()!, width: xs.max()! - xs.min()!, height: ys.max()! - ys.min()!)
                    .insetBy(dx: -reach, dy: -reach)
            }
            let v = src.extent
            let geometry: [Any] = [
                CIVector(x: inv.a, y: inv.c, z: inv.tx), CIVector(x: inv.b, y: inv.d, z: inv.ty),
                CIVector(x: factor, y: region.minX, z: region.minY, w: sigmaOut),
                CIVector(x: r[0].x, y: r[0].y, z: r[1].x, w: r[1].y),
                CIVector(x: r[2].x, y: r[2].y, z: r[3].x, w: r[3].y),
                CIVector(x: r[4].x, y: r[4].y, z: r[5].x, w: r[5].y),
                CIVector(x: r[6].x, y: r[6].y, z: r[7].x, w: r[7].y),
                CIVector(x: r[8].x, y: r[8].y),
                grid, CIVector(x: v.minX, y: v.minY, z: v.maxX, w: v.maxY),
            ]
            let gm = motion(i)
            guard let color = splatKernel.apply(extent: outExtent, roiCallback: roi, arguments: ([src, gm] as [Any]) + geometry),
                  let weight = splatWeightKernel.apply(extent: outExtent, roiCallback: { _, rect in rect.insetBy(dx: -2, dy: -2) },
                                                       arguments: ([gm] as [Any]) + geometry) else { continue }
            colorSum = colorSum.map { add($0, color) } ?? color
            weightSum = weightSum.map { add($0, weight) } ?? weight
            used += 1
        }
        guard used >= 2, let colorSum, let weightSum,
              let merged = divideKernel.apply(extent: outExtent, arguments: [colorSum, weightSum]) else { return nil }
        dlog(String(format: "Super resolução: %d fotos juntadas por regressão de núcleo (núcleo %.2f px da foto)", used, sigmaFrame))
        return (merged, used)
    }

    /// Se a 1ª linha de um CIImage(bitmapData:) vira o topo (y maior): medido uma vez, para a tabela do MAP não sair de
    /// ponta-cabeça (trocaria pedaço e fase)
    private static let bitmapFirstRowIsTop: Bool = {
        let data: [Float] = [1, 1, 1, 1, 0, 0, 0, 1]
        let img = CIImage(bitmapData: data.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: 16,
                          size: CGSize(width: 1, height: 2), format: .RGBAf, colorSpace: nil)
        var probe = [Float](repeating: -1, count: 4)
        gpu.render(img, toBitmap: &probe, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBAf, colorSpace: nil)
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
    /// Devolve quem resolve uma região (a foto inteira, ou uma faixa com margem: o resultado no meio da faixa é o mesmo da
    /// foto inteira, porque cada passo só olha ±3 px), e quantas fotos entraram
    private static func mapSolver(frames: [CapturedFrame], decoded: (Int) -> CIImage?, alignments: [Alignment?],
                                  motion: (Int) -> CIImage, region: CGRect, factor: CGFloat,
                                  grid: CIVector, centers: [CGPoint], noise: Float) -> (solve: (CGRect) -> CIImage?, used: Int)? {
        guard let splatHKernel, let splatHWeightKernel, let mapStepKernel, let momentumKernel, let divideKernel,
              centers.count == 9 else { return nil }
        let t = srTuning
        struct Input {
            let src: CIImage
            let gm: CIImage
            let inv: CGAffineTransform
            let reach: CGFloat
            let geometry: [Any]
        }
        var inputs: [Input] = []
        // Núcleos de AᵀA: 9 pedaços × 4 fases × 7×7 (somados nas fotos, ÷ K no fim)
        var table = [Double](repeating: 0, count: 9 * 4 * 49)
        for i in frames.indices {
            guard let a = alignments[i], let src = decoded(i) else { continue }
            let inv = a.transform.inverted()
            var r = a.residuals.map { CGPoint(x: $0.x * factor, y: $0.y * factor) }
            if r.count != 9 { r = Array(repeating: .zero, count: 9) }
            let reach = (r.map { max(abs($0.x), abs($0.y)) }.max() ?? 0) / factor + 4
            let v = src.extent
            let geometry: [Any] = [
                CIVector(x: inv.a, y: inv.c, z: inv.tx), CIVector(x: inv.b, y: inv.d, z: inv.ty),
                CIVector(x: factor, y: region.minX, z: region.minY, w: 0),
                CIVector(x: r[0].x, y: r[0].y, z: r[1].x, w: r[1].y),
                CIVector(x: r[2].x, y: r[2].y, z: r[3].x, w: r[3].y),
                CIVector(x: r[4].x, y: r[4].y, z: r[5].x, w: r[5].y),
                CIVector(x: r[6].x, y: r[6].y, z: r[7].x, w: r[7].y),
                CIVector(x: r[8].x, y: r[8].y),
                grid, CIVector(x: v.minX, y: v.minY, z: v.maxX, w: v.maxY),
            ]
            inputs.append(Input(src: src, gm: motion(i), inv: inv, reach: reach, geometry: geometry))
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
        guard inputs.count >= 2 else { return nil }
        let used = inputs.count
        let k = Float(used)
        // Tabela como imagem, por célula da grade (os 4 pedaços dos cantos de cada célula numa leitura): 14 × 56, x = fase x·7 + dx,
        // y = (célula·2 + fase y)·7 + dy (linhas da imagem de baixo para cima), célula = j·2 + i (i, j = 0…1). Na 1ª imagem
        // R, G, B = pedaços (i, j), (i + 1, j), (i, j + 1); na 2ª, R = (i + 1, j + 1). Antes eram 4 leituras por toque (196 por
        // pixel por passo, o passo mais pesado do SUPER ZOOM); agora 2 (98)
        let tw = 14, th = 56
        var pixelsA = [Float](repeating: 0, count: tw * th * 4)
        var pixelsB = [Float](repeating: 0, count: tw * th * 4)
        func tableValue(_ tile: Int, _ ay: Int, _ ax: Int, _ dy: Int, _ dx: Int) -> Float {
            Float(table[((tile * 2 + ay) * 2 + ax) * 49 + dy * 7 + dx] / Double(used))
        }
        for cj in 0..<2 { for ci in 0..<2 { for ay in 0..<2 { for ax in 0..<2 { for dy in 0..<7 { for dx in 0..<7 {
            let cell = cj * 2 + ci, tile = cj * 3 + ci
            let x = ax * 7 + dx, y = (cell * 2 + ay) * 7 + dy
            let row = bitmapFirstRowIsTop ? th - 1 - y : y
            let o = (row * tw + x) * 4
            pixelsA[o] = tableValue(tile, ay, ax, dy, dx)
            pixelsA[o + 1] = tableValue(tile + 1, ay, ax, dy, dx)
            pixelsA[o + 2] = tableValue(tile + 3, ay, ax, dy, dx)
            pixelsA[o + 3] = 1
            let v = tableValue(tile + 4, ay, ax, dy, dx)
            pixelsB[o] = v; pixelsB[o + 1] = v; pixelsB[o + 2] = v; pixelsB[o + 3] = 1
        } } } } } }
        let tableImage = CIImage(bitmapData: pixelsA.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: tw * 16,
                                 size: CGSize(width: tw, height: th), format: .RGBAf, colorSpace: nil).samplingNearest()
        let tableCorner = CIImage(bitmapData: pixelsB.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: tw * 16,
                                  size: CGSize(width: tw, height: th), format: .RGBAf, colorSpace: nil).samplingNearest()
        // λ ∝ σ²/K: o dado é dividido por K (mais fotos = dado mais confiável) e o ruído entra ao quadrado. Calibrado com 24
        // fotos e o ruído do laboratório. A medida ainda não foi calibrada (o registro mostra o valor): de metade ao dobro do
        // calibrado não mexe; fora disso, o quadrado do quanto passou (até 4× para cada lado)
        var scale: Float = 1
        if t.mapAutoLambda {
            let ratio = noise > 0 ? noise / t.mapNoiseRef : 1
            let excess: Float = ratio > 2 ? ratio / 2 : (ratio < 0.5 ? ratio / 0.5 : 1)
            let noiseScale = min(4, max(0.25, excess * excess))
            scale = noiseScale * min(4, max(0.5, 24 / k))
            dlog(String(format: "Super resolução: MAP · ruído da diferença borrada %.4f (calibrado %.4f) · %d fotos → λ × %.2f",
                        noise, t.mapNoiseRef, used, scale))
        }
        let lumaLambda = t.mapLumaLambda * scale, chromaLambda = t.mapChromaLambda * scale
        let delta = t.mapDelta, w = chromaLambda / max(lumaLambda, 1e-9)
        let lam = CIVector(x: CGFloat(lumaLambda), y: CGFloat(chromaLambda), z: CGFloat(chromaLambda))
        let tauY = 1 / (0.25 + 8 * lumaLambda / delta), tauC = 1 / (0.25 + 8 * chromaLambda / delta)
        let tau = CIVector(x: CGFloat(tauY), y: CGFloat(tauC), z: CGFloat(tauC))
        let tableExtent = tableImage.extent
        // Argumentos do passo: 0 z (±4 px), 1 b, 2 e 3 as tabelas (inteiras), 4 pesos
        let stepROI: CIKernelROICallback = { index, rect in
            switch index {
            case 1, 4: return rect
            case 2, 3: return tableExtent
            default: return rect.insetBy(dx: -4, dy: -4)
            }
        }
        let iterations = t.mapIterations
        let solve: (CGRect) -> CIImage? = { rect in
            let e = rect.integral
            var colorSum: CIImage?
            var weightSum = CIImage(color: CIColor(red: 0, green: 0, blue: 0)).cropped(to: e)
            var pending = 0
            for input in inputs {
                let inv = input.inv, reach = input.reach
                let roi: CIKernelROICallback = { index, r in
                    if index != 0 { return r.insetBy(dx: -2, dy: -2) }
                    let corners = [CGPoint(x: r.minX, y: r.minY), CGPoint(x: r.maxX, y: r.minY),
                                   CGPoint(x: r.minX, y: r.maxY), CGPoint(x: r.maxX, y: r.maxY)]
                        .map { CGPoint(x: $0.x / factor + region.minX, y: $0.y / factor + region.minY).applying(inv) }
                    let xs = corners.map(\.x), ys = corners.map(\.y)
                    return CGRect(x: xs.min()!, y: ys.min()!, width: xs.max()! - xs.min()!, height: ys.max()! - ys.min()!)
                        .insetBy(dx: -reach, dy: -reach)
                }
                let colorArgs: [Any] = ([input.src, input.gm] as [Any]) + input.geometry
                guard let color = splatHKernel.apply(extent: e, roiCallback: roi, arguments: colorArgs),
                      let weight = splatHWeightKernel.apply(extent: e, arguments: ([weightSum, input.gm] as [Any]) + input.geometry) else { return nil }
                colorSum = colorSum.map { add($0, color) } ?? color
                weightSum = weight
                pending += 1
                // Em lotes de 3 fotos guardados: sem uma cadeia de 24 somas, e cada foto só vive aqui
                if pending == 3, let partial = colorSum {
                    guard let c = materializedOrNil(partial, extent: e), let ws = materializedOrNil(weightSum, extent: e) else { return nil }
                    colorSum = c
                    weightSum = ws
                    pending = 0
                }
            }
            // b = Σh·g·y/K, começo Σh·g·y/Σh·g, e as somas de peso (r = Σh·g, g = Σh) para o W do passo; a soma de cor sai
            // da memória antes dos passos (ficam b, pesos, x, anterior, z e o próximo)
            func prepared() -> (b: CIImage, ws: CIImage, x0: CIImage)? {
                guard let cs = colorSum,
                      let b = materializedOrNil(scaled(cs, by: 1 / k).cropped(to: e), extent: e),
                      let ws = materializedOrNil(weightSum.cropped(to: e), extent: e),
                      let start = divideKernel.apply(extent: e, arguments: [scaled(b, by: k), ws]),
                      let x0 = materializedOrNil(start, extent: e) else { return nil }
                return (b, ws, x0)
            }
            guard let ready = prepared() else { return nil }
            colorSum = nil
            weightSum = CIImage.empty()
            let b = ready.b, ws = ready.ws
            var x = ready.x0, previous = ready.x0
            var tk: Double = 1, beta: Double = 0
            for _ in 0..<iterations {
                let ok: Bool = autoreleasepool {
                    // z = x + β(x − anterior), uma vez por passo (antes refeito 56 vezes por pixel dentro do passo)
                    let z: CIImage
                    if beta == 0 {
                        z = x
                    } else {
                        guard let momentum = momentumKernel.apply(extent: e, arguments: [x, previous, Float(beta)]),
                              let zReady = materializedOrNil(momentum, extent: e) else { return false }
                        z = zReady
                    }
                    guard let next = mapStepKernel.apply(extent: e, roiCallback: stepROI, arguments: [
                        z.clampedToExtent(), b, tableImage, tableCorner, ws, grid, lam, tau, delta, w,
                    ]), let xn = materializedOrNil(next, extent: e) else { return false }
                    previous = x
                    x = xn
                    return true
                }
                guard ok else { return nil }
                let tn = (1 + (1 + 4 * tk * tk).squareRoot()) / 2
                beta = (tk - 1) / tn
                tk = tn
            }
            return x
        }
        dlog("Super resolução: \(used) fotos resolvidas juntas (MAP, \(iterations) passos)")
        return (solve, used)
    }

    // MARK: - Ferramentas das junções

    /// Calcula a imagem agora e guarda num buffer de meia precisão; nil se não houve memória para o buffer (o `materialize`
    /// devolve a imagem preguiçosa calada, e o MAP seguia montando uma cadeia de 16 passos que estourava a memória)
    static func materializedOrNil(_ image: CIImage, extent: CGRect) -> CIImage? {
        let w = Int(extent.width), h = Int(extent.height)
        guard w > 0, h > 0 else { return nil }
        var buffer: CVPixelBuffer?
        let attributes: [CFString: Any] = [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any],
                                           kCVPixelBufferMetalCompatibilityKey: true]
        guard CVPixelBufferCreate(nil, w, h, kCVPixelFormatType_64RGBAHalf, attributes as CFDictionary, &buffer) == kCVReturnSuccess,
              let buffer else { return nil }
        let shifted = image.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
        gpu.render(shifted, to: buffer, bounds: CGRect(x: 0, y: 0, width: w, height: h), colorSpace: linearP3)
        return CIImage(cvPixelBuffer: buffer, options: [.colorSpace: linearP3])
            .transformed(by: CGAffineTransform(translationX: extent.minX, y: extent.minY))
    }

    /// Desvio do ruído na diferença de duas imagens já alinhadas: mediana do |Δ brilho| num pedaço do centro ÷ 0,6745.
    /// A mediana não liga para o pouco que se mexeu ou ficou de borda; o que sobra é o ruído das duas
    static func diffNoise(_ a: CIImage, _ b: CIImage, extent: CGRect) -> Float {
        guard let srSubKernel else { return 0 }
        let side = min(256, extent.width, extent.height).rounded(.down)
        guard side >= 16 else { return 0 }
        let rect = CGRect(x: (extent.midX - side / 2).rounded(), y: (extent.midY - side / 2).rounded(), width: side, height: side)
        guard let d = srSubKernel.apply(extent: rect, arguments: [a, b]) else { return 0 }
        let n = Int(side)
        var pixels = [Float](repeating: 0, count: n * n * 4)
        gpu.render(d.transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY)), toBitmap: &pixels,
                       rowBytes: n * 16, bounds: CGRect(x: 0, y: 0, width: n, height: n), format: .RGBAf, colorSpace: nil)
        var values = [Float]()
        values.reserveCapacity(n * n)
        for i in stride(from: 0, to: pixels.count, by: 4) {
            let l = abs(0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2])
            if l.isFinite { values.append(l) }
        }
        guard !values.isEmpty else { return 0 }
        values.sort()
        return values[values.count / 2] / 0.6745
    }

    /// Quanto multiplicar a foto para ter o brilho da referência (luz que pisca, exposição que andou): sem isso alguns % de
    /// diferença viravam "movimento" na foto inteira. Mediana da razão pixel a pixel no centro (quem se mexeu é minoria e
    /// não conta, ao contrário da média). Preso entre −15% e +18% (`lo`/`hi`); perto de 1 (menos de 1%) devolve 1
    static func exposureGain(_ frame: CIImage, _ reference: CIImage, extent: CGRect, lo: Float = 0.85, hi: Float = 1.18) -> Float {
        let side = min(320, extent.width, extent.height).rounded(.down)
        guard side >= 16 else { return 1 }
        let rect = CGRect(x: (extent.midX - side / 2).rounded(), y: (extent.midY - side / 2).rounded(), width: side, height: side)
        let n = Int(side)
        func lumas(_ image: CIImage) -> [Float] {
            var pixels = [Float](repeating: 0, count: n * n * 4)
            gpu.render(image.transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY)), toBitmap: &pixels,
                           rowBytes: n * 16, bounds: CGRect(x: 0, y: 0, width: n, height: n), format: .RGBAf, colorSpace: nil)
            var out = [Float](repeating: 0, count: n * n)
            for k in 0..<(n * n) {
                let o = k * 4
                let l: Float = 0.2126 * pixels[o] + 0.7152 * pixels[o + 1] + 0.0722 * pixels[o + 2]
                out[k] = l
            }
            return out
        }
        let a = lumas(frame), b = lumas(reference)
        var ratios: [Float] = []
        ratios.reserveCapacity(a.count)
        for k in a.indices where a[k].isFinite && b[k].isFinite && a[k] > 0.002 && b[k] > 0.002 {
            ratios.append(b[k] / a[k])
        }
        guard ratios.count > a.count / 4 else { return 1 }
        ratios.sort()
        let gain = min(hi, max(lo, ratios[ratios.count / 2]))
        return abs(gain - 1) < 0.01 ? 1 : gain
    }

    /// Ruído da diferença de duas versões borradas e alinhadas, pela luz: var = a·Y + b, ajustado na própria rajada. Numa
    /// versão de ~0,25 MP: 8 faixas de luz com o mesmo número de pixels, σ de cada uma pela mediana do |ΔY| ÷ 0,6745 (quem se
    /// mexeu é minoria e a mediana não liga), mínimos quadrados com peso 1/var² (o erro de cada σ² é relativo).
    /// Estourado fora: onde as duas fotos cortaram no branco ΔY = 0 exato (sem ruído nenhum). Com ≥ ~6% da cena estourada
    /// a faixa de cima dava σ = 0, peso 1e24, e o ajuste desabava para σ ≈ 1e-4 em tudo (6,8× menor que o de verdade,
    /// estudo em Python): o mapa de movimento recusava ~54% do liso parado e a FOTO 3×/NOITE saíam com o ruído de uma foto.
    /// Agora: fora quem está a 5% do máximo (em qualquer cor) e quem tem |ΔY| = 0 exato; faixa com mediana 0 não entra; o
    /// peso não passa do de ¼ da variância típica (uma faixa meio estourada não manda sozinha); b ≥ ¼ da faixa mais escura;
    /// e o ajuste tem que dar, na luz do meio, entre ½ e 2× o ruído típico de todas as amostras (senão vale esse)
    static func noiseModel(_ frame: CIImage, _ reference: CIImage, extent: CGRect) -> (a: Float, b: Float)? {
        let s = CGFloat(min(1, (250_000 / max(1, Double(extent.width * extent.height))).squareRoot()))
        let w = Int((extent.width * s).rounded(.down)), h = Int((extent.height * s).rounded(.down))
        guard w >= 16, h >= 16 else { return nil }
        let bounds = CGRect(x: 0, y: 0, width: w, height: h)
        let toSmall = CGAffineTransform(translationX: -extent.minX, y: -extent.minY).concatenating(CGAffineTransform(scaleX: s, y: s))
        // Brilho e a maior cor de cada pixel (a maior cor acha o estourado mesmo quando só um canal cortou)
        func lumas(_ image: CIImage) -> (luma: [Float], peak: [Float]) {
            var pixels = [Float](repeating: 0, count: w * h * 4)
            gpu.render(image.cropped(to: extent).transformed(by: toSmall), toBitmap: &pixels, rowBytes: w * 16, bounds: bounds,
                           format: .RGBAf, colorSpace: nil)
            var out = [Float](repeating: 0, count: w * h)
            var peak = [Float](repeating: 0, count: w * h)
            for k in 0..<(w * h) {
                let o = k * 4
                let r = max(pixels[o], 0), g = max(pixels[o + 1], 0), b = max(pixels[o + 2], 0)
                out[k] = 0.2126 * r + 0.7152 * g + 0.0722 * b
                peak[k] = max(r, max(g, b))
            }
            return (out, peak)
        }
        let (yf, pf) = lumas(frame), (yr, pr) = lumas(reference)
        var top: Float = 0
        for k in 0..<(w * h) {
            if pr[k].isFinite { top = max(top, pr[k]) }
            if pf[k].isFinite { top = max(top, pf[k]) }
        }
        func gather(below clip: Float) -> [(y: Float, d: Float)] {
            var out: [(y: Float, d: Float)] = []
            out.reserveCapacity(w * h)
            for k in 0..<(w * h) where yf[k].isFinite && yr[k].isFinite && pr[k] < clip && pf[k] < clip {
                let d = abs(yf[k] - yr[k])
                if d > 0 { out.append((yr[k], d)) }
            }
            return out
        }
        var samples = gather(below: 0.95 * top)
        // Quase tudo perto do máximo sem estourar (céu claro tomando a foto): fica só a regra do ΔY = 0
        if samples.count < 800 { samples = gather(below: .infinity) }
        guard samples.count >= 800 else { return nil }
        // Ruído típico de todas as amostras (a referência da conferência no fim)
        var all = samples.map { $0.d }
        all.sort()
        let typical = all[all.count / 2] / 0.6745
        samples.sort { $0.y < $1.y }
        let middleY = samples[samples.count / 2].y
        var ys: [Float] = [], vs: [Float] = []
        for bin in 0..<8 {
            let lo = samples.count * bin / 8, hi = samples.count * (bin + 1) / 8
            guard hi - lo >= 50 else { continue }
            var ds = [Float]()
            ds.reserveCapacity(hi - lo)
            var sumY: Float = 0
            for k in lo..<hi {
                ds.append(samples[k].d)
                sumY += samples[k].y
            }
            ds.sort()
            let sigma = ds[ds.count / 2] / 0.6745
            if !(sigma > 1e-7) { continue }
            ys.append(sumY / Float(hi - lo))
            vs.append(sigma * sigma)
        }
        guard ys.count >= 2, typical.isFinite, typical > 0 else { return nil }
        let sortedV = vs.sorted()
        let vFloor = 0.25 * sortedV[sortedV.count / 2]
        func weight(_ v: Float) -> Float {
            let c = max(v, vFloor)
            return 1 / (c * c)
        }
        var sw: Float = 0, sy: Float = 0, sv: Float = 0
        for k in ys.indices {
            let wk = weight(vs[k])
            sw += wk
            sy += wk * ys[k]
            sv += wk * vs[k]
        }
        let my = sy / sw, mv = sv / sw
        var sxx: Float = 0, sxv: Float = 0
        for k in ys.indices {
            let wk = weight(vs[k])
            sxx += wk * (ys[k] - my) * (ys[k] - my)
            sxv += wk * (ys[k] - my) * (vs[k] - mv)
        }
        var a: Float = sxx > 0 ? sxv / sxx : 0
        var b: Float = mv - a * my
        if !a.isFinite || a < 0 {
            a = 0
            b = mv
        }
        // b nunca abaixo de ¼ da variância da faixa mais escura (vs[0]: as faixas vêm do escuro para o claro)
        let bFloor = max(1e-10, 0.25 * vs[0])
        if !b.isFinite || b < bFloor { b = bFloor }
        let atMiddle = (a * middleY + b).squareRoot()
        if !atMiddle.isFinite || atMiddle < 0.5 * typical || atMiddle > 2 * typical {
            dlog(String(format: "Junção: ajuste do ruído fora (σ no meio %.5f, típico %.5f): vale o típico", atMiddle, typical))
            return (0, typical * typical)
        }
        return (a, b)
    }

    /// Mapa de movimento (1 = igual, 0 = mexeu) entre duas versões já borradas e alinhadas: z = |ΔY| / √(a·Y + b +
    /// (misregistration·|∇Y_ref|)²), g = 1 até z = lo e 0 a partir de hi; depois a recusa alargada (mínimo em `erosion` px:
    /// a borda de quem se mexe também sai) e alisada (σ `smooth`)
    static func motionWeights(_ frame: CIImage, _ reference: CIImage, extent: CGRect, model: (a: Float, b: Float),
                              misregistration: Float, lo: Float, hi: Float, erosion: Float, smooth: Double) -> CIImage? {
        guard let motionKernel else { return nil }
        let p = CIVector(x: CGFloat(model.a), y: CGFloat(model.b), z: CGFloat(misregistration), w: 0)
        let lim = CIVector(x: CGFloat(lo), y: CGFloat(hi))
        guard let raw = motionKernel.apply(extent: extent, roiCallback: { _, r in r.insetBy(dx: -1, dy: -1) },
                                           arguments: [frame.clampedToExtent(), reference.clampedToExtent(), p, lim]) else { return nil }
        var g = raw
        if erosion >= 0.5 {
            g = g.clampedToExtent().applyingFilter("CIMorphologyMinimum", parameters: [kCIInputRadiusKey: erosion]).cropped(to: extent)
        }
        if smooth > 0.05 { g = g.clampedToExtent().applyingGaussianBlur(sigma: smooth).cropped(to: extent) }
        return g
    }

    /// NOITE: onde poucas fotos entraram (quem se mexeu ficou só com a referência) sobra o ruído de uma foto só no meio da
    /// noite lisa. Lá a limpeza é mais forte, pelo que falta de 1/√N_eff (N_eff = Σ g dos mapas de movimento); onde entraram
    /// todas nada muda
    static func coverageDenoise(_ scene: CIImage, coverage: CIImage?, frames: Int) -> CIImage {
        guard let coverage, frames >= 3, let coverageMaskKernel else { return scene }
        let e = scene.extent
        guard let mask = coverageMaskKernel.apply(extent: e, arguments: [coverage.clampedToExtent().cropped(to: e), Float(frames)])
        else { return scene }
        let noise = measuredNoise(scene)
        let strong = lumaDenoise(nightDenoise(scene, strength: 1), strength: 1, noise: noise * 2.5)
        return strong.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: scene, kCIInputMaskImageKey: mask])
            .cropped(to: e)
    }

    /// ISO do EXIF da imagem (100 sem EXIF)
    static func isoOf(_ image: CIImage) -> Float {
        let exif = image.properties[kCGImagePropertyExifDictionary as String] as? [String: Any]
        return (exif?[kCGImagePropertyExifISOSpeedRatings as String] as? [NSNumber])?.first?.floatValue ?? 100
    }

    /// A mesma imagem dizendo outro ISO (a limpeza e a nitidez da revelação seguem o ISO)
    static func withISO(_ image: CIImage, _ iso: Float) -> CIImage {
        var properties = image.properties
        var exif = properties[kCGImagePropertyExifDictionary as String] as? [String: Any] ?? [:]
        exif[kCGImagePropertyExifISOSpeedRatings as String] = [NSNumber(value: iso)]
        properties[kCGImagePropertyExifDictionary as String] = exif
        return image.settingProperties(properties)
    }

    /// Junção de várias fotos revelada como a FOTO (tons locais, cor pela luz, nitidez; limpeza só se ainda precisar): o ISO
    /// vira o de uma foto com a luz de todas (n fotos ≈ ISO ÷ n). Antes saía sem nada disso, mais chapada que a FOTO
    static func multiFrameEnhanced(_ scene: CIImage, frames: Int, preview: CIImage?) -> CIImage {
        let iso = max(25, isoOf(scene) / Float(max(frames, 1)))
        return enhanced(withISO(scene, iso), preview: preview).settingProperties(scene.properties)
    }

    /// Referência das junções: a mais nítida, a não ser que ela não encaixe em nenhuma das 3 seguintes enquanto essas encaixam
    /// entre si. Uma foto de puro ruído (lente tampada, quadro corrompido) tem o laplaciano mais alto e virava a referência:
    /// todas as boas saíam por não encaixar nela e sobrava só o ruído. Encaixe = o grosso do centro em ¼ (o mesmo do
    /// alinhamento, com o mesmo limite de 12% da foto). No escuro liso o grosso pode falhar entre fotos boas: aí nada muda
    static func trustedReference(_ frames: [CapturedFrame], scores: [Float]) -> Int {
        let ranked = scores.indices.sorted { scores[$0] > scores[$1] }
        guard ranked.count >= 3 else { return ranked.first ?? 0 }
        let top = Array(ranked.prefix(4))
        let smalls = top.map { image(from: frames[$0], scale: 0.25) }
        var known: [Int: Bool] = [:]
        func aligns(_ a: Int, _ b: Int) -> Bool {
            let key = min(a, b) * 8 + max(a, b)
            if let hit = known[key] { return hit }
            var ok = false
            if let x = smalls[a], let y = smalls[b], let shift = coarseShift(ref: x, img: y, scale: 0.25) {
                let e = x.extent
                ok = abs(shift.x) <= e.width / 0.25 * 0.12 && abs(shift.y) <= e.height / 0.25 * 0.12
            }
            known[key] = ok
            return ok
        }
        let others = Array(1..<top.count)
        guard others.allSatisfy({ !aligns(0, $0) }) else { return top[0] }
        let othersAgree = others.contains { a in others.contains { b in b > a && aligns(a, b) } }
        guard othersAgree else { return top[0] }
        dlog(String(format: "Junção: a mais nítida (foto %d) não encaixa em nenhuma das outras: referência é a foto %d", top[0] + 1, top[1] + 1))
        return top[1]
    }

    /// LUA: lado do pedaço da nota de nitidez (na versão dada, ¼): ~3× o diâmetro da Lua, medido pelo que passa de metade do
    /// pico (acima do fundo) num pedaço de 256 px em volta do mais claro; preso em 64–512 px (512 é o de antes)
    static func moonWindow(_ small: CIImage) -> CGFloat {
        let e = small.extent
        let c = brightestPoint(small)
        let side = min(256, e.width, e.height).rounded(.down)
        guard side >= 16 else { return 512 }
        let x = min(max(c.x - side / 2, e.minX), e.maxX - side).rounded(), y = min(max(c.y - side / 2, e.minY), e.maxY - side).rounded()
        let rect = CGRect(x: x, y: y, width: side, height: side)
        let n = Int(side)
        var pixels = [Float](repeating: 0, count: n * n * 4)
        let piece = small.clampedToExtent().applyingGaussianBlur(sigma: 1).cropped(to: rect)
            .transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))
        gpu.render(piece, toBitmap: &pixels, rowBytes: n * 16, bounds: CGRect(x: 0, y: 0, width: n, height: n), format: .RGBAf, colorSpace: nil)
        var lumas = [Float](repeating: 0, count: n * n)
        for k in 0..<(n * n) {
            let l: Float = 0.2126 * pixels[k * 4] + 0.7152 * pixels[k * 4 + 1] + 0.0722 * pixels[k * 4 + 2]
            lumas[k] = l.isFinite ? l : 0
        }
        let sorted = lumas.sorted()
        let background = sorted[sorted.count / 2], peak = sorted[sorted.count - 1]
        guard peak > background else { return 512 }
        let half = background + 0.5 * (peak - background)
        let area = lumas.reduce(0) { $0 + ($1 >= half ? 1 : 0) }
        let diameter = 2 * (CGFloat(area) / .pi).squareRoot()
        let window = min(512, max(64, 3 * diameter)).rounded()
        dlog(String(format: "LUA: Lua com ~%.0f px em ¼ → nota de nitidez num pedaço de %.0f px", diameter, window))
        return window
    }

    /// LUA: onde está o mais claro (a Lua) numa versão pequena da foto
    static func brightestPoint(_ image: CIImage) -> CGPoint {
        let e = image.extent
        let fallback = CGPoint(x: e.midX, y: e.midY)
        let k = min(1, 64 / max(e.width, e.height))
        let w = Int((e.width * k).rounded(.down)), h = Int((e.height * k).rounded(.down))
        guard w >= 4, h >= 4 else { return fallback }
        let te = CGRect(x: 0, y: 0, width: w, height: h)
        let tiny = image.transformed(by: CGAffineTransform(translationX: -e.minX, y: -e.minY))
            .applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: k, kCIInputAspectRatioKey: 1])
            .clampedToExtent().applyingGaussianBlur(sigma: 1.5).cropped(to: te)
        var pixels = [Float](repeating: 0, count: w * h * 4)
        gpu.render(tiny, toBitmap: &pixels, rowBytes: w * 16, bounds: te, format: .RGBAf, colorSpace: nil)
        var best = -Float.greatestFiniteMagnitude
        var at = -1
        for i in 0..<(w * h) {
            let o = i * 4
            let l: Float = 0.2126 * pixels[o] + 0.7152 * pixels[o + 1] + 0.0722 * pixels[o + 2]
            if l.isFinite, l > best {
                best = l
                at = i
            }
        }
        guard at >= 0 else { return fallback }
        let row = at / w, col = at % w
        let y = renderFirstRowIsTop ? h - 1 - row : row
        return CGPoint(x: e.minX + (CGFloat(col) + 0.5) / k, y: e.minY + (CGFloat(y) + 0.5) / k)
    }

    /// Se a 1ª linha que o render(toBitmap:) escreve é o topo da imagem (y maior): medido uma vez
    private static let renderFirstRowIsTop: Bool = {
        let rect = CGRect(x: 0, y: 0, width: 1, height: 2)
        let top = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: CGRect(x: 0, y: 1, width: 1, height: 1))
        let probeImage = top.composited(over: CIImage(color: CIColor(red: 0, green: 0, blue: 0)).cropped(to: rect))
        var probe = [Float](repeating: -1, count: 8)
        gpu.render(probeImage, toBitmap: &probe, rowBytes: 16, bounds: rect, format: .RGBAf, colorSpace: nil)
        return probe[0] > 0.5
    }()

    // MARK: - Foco empilhado

    /// FOCO EMPILHADO em duas faixas, sem decisão dura (a troca 0/1 de antes fazia auréola nas bordas): a parte lisa de cada
    /// foto (borrão de 4 px, em ¼) pesa pela nitidez da região (borrão largo, potência 2); o detalhe pesa pela nitidez em volta
    /// (3 px, potência 8: quase sempre a mais nítida, com transição suave). Duas passadas: a 1ª acha, em cada lugar, a nitidez
    /// da MAIS nítida das fotos (¼); a 2ª pesa cada foto por r = nitidez ÷ essa, em (0, 1]. Antes o peso era relativo a 2× a
    /// média da 1ª foto e preso em 6,7: com a 1ª toda fora de foco a melhor e a vizinha prendiam juntas e pesavam igual
    /// (estudo em Python, 4 fotos, 1ª com borrão de 6 px: 0,57–0,62 da nitidez da cena; agora 0,97–0,98). Potência 8 no
    /// lugar de 4: a vizinha com borrão de 1 px pesava ~1/11 da nítida e amolecia a borda (0,84 → 0,97; auréola igual,
    /// 0,065 → 0,069). nil se faltar kernel (fica a escolha de antes)
    static func focusFusion(count: Int, extent: CGRect, frame: (Int) -> CIImage?) -> CIImage? {
        guard count >= 2, let focusWeightKernel, let focusSharpnessKernel, let mulGKernel, let highGKernel,
              let fusionDivideAddKernel, let maxKernel else { return nil }
        let quarter: CGFloat = 0.25
        let qe = CGRect(x: 0, y: 0, width: (extent.width * quarter).rounded(.down), height: (extent.height * quarter).rounded(.down))
        guard qe.width >= 8, qe.height >= 8 else { return nil }
        func toQuarter(_ image: CIImage, blur: Double) -> CIImage {
            image.clampedToExtent().applyingGaussianBlur(sigma: blur).cropped(to: extent)
                .transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY)
                    .concatenating(CGAffineTransform(scaleX: quarter, y: quarter)))
                .cropped(to: qe)
        }
        func fromQuarter(_ image: CIImage) -> CIImage {
            image.clampedToExtent()
                .transformed(by: CGAffineTransform(scaleX: 1 / quarter, y: 1 / quarter)
                    .concatenating(CGAffineTransform(translationX: extent.minX, y: extent.minY)))
                .cropped(to: extent)
        }
        // |laplaciano| do brilho numa versão levemente borrada (0,8 px): o ruído não conta como nitidez
        func sharpness(_ image: CIImage) -> CIImage? {
            let lap = image.clampedToExtent().applyingGaussianBlur(sigma: 0.8).applyingFilter("CIConvolution3X3", parameters: [
                "inputWeights": CIVector(values: [0, 1, 0, 1, -4, 1, 0, 1, 0], count: 9), "inputBias": 0,
            ]).cropped(to: extent)
            return focusSharpnessKernel.apply(extent: extent, arguments: [lap])
        }
        func detailOf(_ s: CIImage) -> CIImage { s.clampedToExtent().applyingGaussianBlur(sigma: 3).cropped(to: extent) }
        func regionalOf(_ s: CIImage) -> CIImage { toQuarter(s, blur: 4).clampedToExtent().applyingGaussianBlur(sigma: 6).cropped(to: qe) }
        func mean(_ image: CIImage) -> Float {
            let average = image.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: qe)])
            let one = average.transformed(by: CGAffineTransform(translationX: -average.extent.minX, y: -average.extent.minY))
            var pixel = [Float](repeating: 0, count: 4)
            gpu.render(one, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBAf, colorSpace: nil)
            return pixel[0].isFinite ? max(pixel[0], 0) : 0
        }
        // Brilho de cada foto igual ao da 1ª: a 2ª foto +0,3 EV fazia um degrau de 0,034 na divisa (laboratório; meta 0,02) e a
        // mais clara também parecia mais "nítida" (o laplaciano cresce com a luz). Razão das médias do brilho no miolo: o desfoque
        // espalha a luz mas não muda a média (estudo em Python, P06 +0,3 EV: degrau 0,026 → 0,000). Presa entre ½ e 2×
        let core = extent.insetBy(dx: (extent.width * 0.2).rounded(), dy: (extent.height * 0.2).rounded())
        func coreLuma(_ image: CIImage) -> Float {
            let average = image.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: core)])
            let one = average.transformed(by: CGAffineTransform(translationX: -average.extent.minX, y: -average.extent.minY))
            var pixel = [Float](repeating: 0, count: 4)
            gpu.render(one, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBAf, colorSpace: nil)
            let l: Float = 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]
            return l.isFinite ? max(l, 0) : 0
        }
        var gains = [Float](repeating: 1, count: count)
        var referenceLuma: Float = 0
        func leveled(_ i: Int, _ image: CIImage) -> CIImage {
            gains[i] == 1 ? image : scaled(image, by: gains[i]).cropped(to: image.extent)
        }
        // 1ª passada: em cada lugar, a nitidez da mais nítida (detalhe e região, em ¼; o detalhe encolhido com borrão de 1,5 px
        // para não serrilhar)
        var bestDetail: CIImage?, bestRegional: CIImage?
        for i in 0..<count {
            autoreleasepool {
                guard let raw = frame(i) else { return }
                let l = coreLuma(raw.cropped(to: extent))
                if referenceLuma <= 0 {
                    referenceLuma = l
                } else if l > 0 {
                    let g = min(2, max(0.5, referenceLuma / l))
                    if abs(g - 1) > 0.005 {
                        gains[i] = g
                        dlog(String(format: "Foco empilhado: foto %d com %+.2f EV de diferença: brilho igualado ao da 1ª", i + 1, log2(1 / g)))
                    }
                }
                let opened = leveled(i, raw)
                guard let s = sharpness(opened.cropped(to: extent)) else { return }
                let d = toQuarter(detailOf(s), blur: 1.5), r = regionalOf(s)
                var nextDetail: CIImage? = d, nextRegional: CIImage? = r
                if let previous = bestDetail { nextDetail = maxKernel.apply(extent: qe, arguments: [previous, d]) }
                if let previous = bestRegional { nextRegional = maxKernel.apply(extent: qe, arguments: [previous, r]) }
                guard let readyDetail = nextDetail, let readyRegional = nextRegional else { return }
                bestDetail = materialize(readyDetail, extent: qe)
                bestRegional = materialize(readyRegional, extent: qe)
            }
        }
        guard let bestDetail, let bestRegional else { return nil }
        // ε = ¼ da nitidez média da melhor: no liso (nitidez ≪ ε) todas as fotos valem quase igual
        let epsDetail = max(1e-6, 0.25 * mean(bestDetail)), epsRegional = max(1e-6, 0.25 * mean(bestRegional))
        let bestDetailFull = fromQuarter(bestDetail)
        var lowSum: CIImage?, lowWeight: CIImage?, highSum: CIImage?, highWeight: CIImage?
        var used = 0
        for i in 0..<count {
            autoreleasepool {
                guard let opened = frame(i) else { return }
                let image = materialize(leveled(i, opened).cropped(to: extent), extent: extent)
                guard let s = sharpness(image) else { return }
                let low = materialize(toQuarter(image, blur: 4), extent: qe)
                guard let wd = focusWeightKernel.apply(extent: extent, arguments: [detailOf(s), bestDetailFull, epsDetail, Float(8)]),
                      let wl = focusWeightKernel.apply(extent: qe, arguments: [regionalOf(s), bestRegional, epsRegional, Float(2)]),
                      let lc = mulGKernel.apply(extent: qe, arguments: [low, wl]),
                      let hc = highGKernel.apply(extent: extent, arguments: [image, fromQuarter(low), wd]) else { return }
                lowSum = materialize(lowSum.map { add($0, lc) } ?? lc, extent: qe)
                lowWeight = materialize(lowWeight.map { add($0, wl) } ?? wl, extent: qe)
                highSum = materialize(highSum.map { add($0, hc) } ?? hc, extent: extent)
                highWeight = materialize(highWeight.map { add($0, wd) } ?? wd, extent: extent)
                used += 1
            }
        }
        guard used >= 2, let lowSum, let lowWeight, let highSum, let highWeight,
              let merged = fusionDivideAddKernel.apply(extent: extent, arguments: [fromQuarter(lowSum), fromQuarter(lowWeight),
                                                                                  highSum, highWeight]) else { return nil }
        dlog("Foco empilhado: \(used) fotos em duas faixas, pesos pela nitidez relativa à mais nítida de cada lugar")
        return materialize(merged, extent: extent)
    }

    // MARK: - Estrelas

    /// ESTRELAS (tripé, 16 fotos): o céu gira (~0,35 px por foto de 1,5 s na 1×, ~5,5 px na sequência) e o chão fica parado.
    /// Antes: só deslocamento pelo centro (num céu de estrelas não achava nada, ou grudava no chão), o corte de passageiros
    /// (avião) em 1,6 × a média das fotos desalinhadas apagava ~55% das estrelas, que andam, e os pixels quentes ficavam.
    /// Agora: (1) céu alinhado pelos pedaços (giro + deslocamento, ajuste robusto: o céu é a maioria); (2) pixel quente pelo
    /// mínimo das fotos sem alinhar (sozinho, parado, e onde o céu andou ≥ 3 px naquele pixel: revelaHotMask), trocado pela
    /// mediana 3×3 em cada foto antes de alinhar, só no céu; (3) corte do avião depois de alinhar, acima de média + 3·max(desvio,
    /// ruído), média e desvio sem as 2 maiores de cada pixel; (4) chão sem alinhar (média sem as 2 maiores, puxada de volta),
    /// sem mexer nos quentes onde a evidência diz chão com clareza (uma luz parada de 1 px no chão é igual a um quente), por uma
    /// máscara do que explica melhor cada lugar: o céu girando ou o chão parado. Memória (12 MP, 96 MB por imagem): as somas saem assim que as médias ficam
    /// prontas (antes a soma parada ficava viva até o fim por uma imagem preguiçosa e as médias do céu eram guardadas à parte)
    /// e a máscara dos quentes fica em 1 byte por pixel: no máximo ~8 imagens vivas (~0,8 GB) em vez de ~11 (~1,05 GB),
    /// mesmo com as 2 maiores de cada pixel guardadas. nil se não der
    static func starStack(_ frames: [CapturedFrame], options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard frames.count >= 3, let hotMaskKernel, let hotFixKernel, let sigmaClipKernel, let squareKernel,
              let skyEvidenceKernel, let skyMaskKernel, let maxKernel, let secondMaxKernel, let trimmedMeanKernel,
              let trimmedSpreadKernel else { return nil }
        // Referência no meio da sequência: o céu anda no máximo metade do total em relação a ela
        let mid = frames.count / 2
        let ordered = [frames[mid]] + frames.indices.filter { $0 != mid }.map { frames[$0] }
        guard let reference = image(from: ordered[0]) else { return nil }
        let extent = reference.extent
        let n = ordered.count
        dlog("Estrelas: \(n) fotos · \(Int(extent.width))×\(Int(extent.height)) · memória livre \(Diagnostics.freeMemory)")
        // 1) Céu: o alinhamento fino da NOITE (o chão, minoria, sai como pedaço que discorda)
        let centers = tileCenters(in: extent)
        let alignments = alignTransforms(frames: ordered, refIndex: 0, reference: reference, centers: centers, stars: true)
        let grid = CIVector(x: centers[0].x, y: centers[0].y, z: centers[1].x - centers[0].x, w: centers[3].y - centers[0].y)
        func warp(_ i: Int, _ image: CIImage) -> CIImage? {
            guard let a = alignments[i] else { return nil }
            return warpCubic(image, transform: a.transform, residuals: a.residuals, grid: grid, extent: extent)?.cropped(to: extent)
        }
        // Quanto o céu andou em cada pixel, da 1ª à última foto que encaixou (em `ordered` a ordem no tempo é 1…mid, 0, mid+1…):
        // T_última(p) − T_primeira(p) = M·p + c (o giro é pequeno e o caminho é quase reta). Abaixo de 3 px as estrelas não somem
        // do mínimo. Antes só no centro: perto do polo a estrela quase não anda e era apagada como quente
        let timeOrder = Array(1...mid) + [0] + Array((mid + 1)..<n)
        let timed = timeOrder.compactMap { alignments[$0] }
        var spanM = CIVector(x: 0, y: 0, z: 0, w: 0), spanC = CIVector(x: 0, y: 0)
        var maxSpan: CGFloat = 0, centerSpan: CGFloat = 0
        if let first = timed.first?.transform, let last = timed.last?.transform {
            let m = CIVector(x: last.a - first.a, y: last.c - first.c, z: last.b - first.b, w: last.d - first.d)
            let c = CIVector(x: last.tx - first.tx, y: last.ty - first.ty)
            spanM = m
            spanC = c
            func moved(_ p: CGPoint) -> CGFloat {
                hypot(m.x * p.x + m.y * p.y + c.x, m.z * p.x + m.w * p.y + c.y)
            }
            for p in [CGPoint(x: extent.minX, y: extent.minY), CGPoint(x: extent.maxX, y: extent.minY),
                      CGPoint(x: extent.minX, y: extent.maxY), CGPoint(x: extent.maxX, y: extent.maxY)] {
                maxSpan = max(maxSpan, moved(p))
            }
            centerSpan = moved(CGPoint(x: extent.midX, y: extent.midY))
        }
        dlog(String(format: "Estrelas: céu alinhado em %@ (%d/%d fotos) · andou %.1f px no centro, até %.1f px", Diagnostics.ms(since: t0),
                    timed.count, n, centerSpan, maxSpan))
        // Soma, soma dos quadrados e as duas maiores de cada pixel (a 2ª antes da maior: usa a maior de antes). Com elas, a média
        // sem as 2 maiores: o que passou em até 2 fotos (avião, satélite, farol) não entra
        struct Moments {
            var sum: CIImage?
            var squares: CIImage?
            var top1: CIImage?
            var top2: CIImage?
            var count = 0
        }
        func accumulate(_ s: inout Moments, _ x: CIImage) -> Bool {
            guard let square = squareKernel.apply(extent: extent, arguments: [x, x]) else { return false }
            if let t1 = s.top1 {
                let second: CIImage?
                if let t2 = s.top2 {
                    second = secondMaxKernel.apply(extent: extent, arguments: [t1, t2, x])
                } else {
                    second = x.applyingFilter("CIMinimumCompositing", parameters: [kCIInputBackgroundImageKey: t1])
                }
                guard let secondReady = second, let firstReady = maxKernel.apply(extent: extent, arguments: [t1, x]) else { return false }
                s.top2 = materialize(secondReady.cropped(to: extent), extent: extent)
                s.top1 = materialize(firstReady, extent: extent)
            } else {
                s.top1 = x
            }
            s.sum = materialize(s.sum.map { add($0, x) } ?? x, extent: extent)
            s.squares = materialize(s.squares.map { add($0, square) } ?? square, extent: extent)
            s.count += 1
            return true
        }
        func trimmedMean(_ s: Moments, unbias: Float) -> CIImage? {
            guard let sum = s.sum, let squares = s.squares, let t1 = s.top1, let t2 = s.top2, s.count >= 3 else { return nil }
            return trimmedMeanKernel.apply(extent: extent, arguments: [sum, squares, t1, t2, Float(s.count), unbias])
        }
        // 2) Sem alinhar: o mínimo (só o pixel quente sobra) e a média (o chão)
        let noise = measuredNoise(reference)
        var hotMask: CIImage?
        var stillMean: CIImage?
        do {
            var minimum: CIImage?
            var still = Moments()
            for i in 0..<n {
                autoreleasepool {
                    guard let img = image(from: ordered[i]) else { return }
                    let frame = materialize(img.cropped(to: extent), extent: extent)
                    guard accumulate(&still, frame) else { return }
                    if maxSpan >= 3 {
                        let lower = minimum.map { frame.applyingFilter("CIMinimumCompositing", parameters: [kCIInputBackgroundImageKey: $0]) } ?? frame
                        minimum = materialize(lower.cropped(to: extent), extent: extent)
                    }
                }
            }
            // O chão: a média sem as 2 maiores de cada pixel, puxada de volta (0,275 × o desvio aparado). No céu liso a máscara
            // céu × chão não decide (os dois explicam igual) e a mistura pega o chão em parte: com a média simples aqui a trilha do
            // avião voltava por esse caminho, mesmo cortada no céu. A média pronta: as somas saem da memória no fim do bloco
            guard let robust = trimmedMean(still, unbias: 0.275) else { return nil }
            let mean = materialize(robust, extent: extent)
            stillMean = mean
            if let minimum {
                hotMask = hotMaskKernel.apply(extent: extent, roiCallback: { index, r in index == 0 ? r.insetBy(dx: -1, dy: -1) : r },
                                              arguments: [minimum.clampedToExtent(), mean.clampedToExtent(), max(Float(1e-4), noise),
                                                          spanM, spanC])
                    .map { compactMask($0, extent: extent) }
            }
        }
        guard let stillMean else { return nil }
        func fixHot(_ image: CIImage) -> CIImage {
            guard let hotMask else { return image }
            return hotFixKernel.apply(extent: extent, roiCallback: { index, r in index == 0 ? r.insetBy(dx: -1, dy: -1) : r },
                                      arguments: [image.clampedToExtent(), hotMask])?.cropped(to: extent) ?? image
        }
        func fixed(_ i: Int) -> CIImage? {
            image(from: ordered[i]).map { fixHot($0.cropped(to: extent)) }
        }
        let half: CGFloat = 0.5
        let he = CGRect(x: 0, y: 0, width: (extent.width * half).rounded(.down), height: (extent.height * half).rounded(.down))
        func toHalf(_ image: CIImage) -> CIImage {
            image.clampedToExtent().applyingGaussianBlur(sigma: 1.5).cropped(to: extent)
                .transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY)
                    .concatenating(CGAffineTransform(scaleX: half, y: half)))
                .cropped(to: he)
        }
        // 3) Céu: as mesmas somas das fotos alinhadas (sem os quentes). No fim, média e desvio sem as 2 maiores (o limite do
        // corte) e a média simples em ½ (para a evidência céu × chão); as somas saem da memória no fim do bloco
        var robustMean: CIImage?, robustSpread: CIImage?, skyHalf: CIImage?
        do {
            var sky = Moments()
            for i in 0..<n {
                autoreleasepool {
                    guard let f = fixed(i), let aligned = warp(i, f) else { return }
                    _ = accumulate(&sky, materialize(aligned, extent: extent))
                }
            }
            guard let sum = sky.sum, let squares = sky.squares, let t1 = sky.top1, let t2 = sky.top2, sky.count >= 3,
                  let m = trimmedMean(sky, unbias: 0),
                  let sd = trimmedSpreadKernel.apply(extent: extent, arguments: [sum, squares, t1, t2, Float(sky.count)]) else { return nil }
            robustMean = materialize(m, extent: extent)
            robustSpread = materialize(sd, extent: extent)
            skyHalf = materialize(toHalf(scaled(sum, by: 1 / Float(sky.count)).cropped(to: extent)), extent: he)
        }
        guard let robustMean, let robustSpread, let skyHalf else { return nil }
        // 4) Corte do que passou (avião, satélite) contra a média robusta já alinhada (as estrelas não são cortadas: estão no
        // mesmo lugar em todas) e, ao mesmo tempo, a evidência céu × chão em ½ (borrada 1,5 px). A evidência do chão compara a
        // foto sem mexer nos quentes com a média parada (também sem mexer): a luz parada de 1 px não vira "céu"
        let stillHalf = materialize(toHalf(stillMean), extent: he)
        var clippedSum: CIImage?
        var clippedCount = 0
        var evidence: CIImage?
        for i in 0..<n {
            autoreleasepool {
                guard let opened = image(from: ordered[i]) else { return }
                let raw = materialize(opened.cropped(to: extent), extent: extent)
                guard let aligned = warp(i, fixHot(raw)) else { return }
                if let clipped = sigmaClipKernel.apply(extent: extent, arguments: [aligned, robustMean, robustSpread, Float(3),
                                                                                    max(Float(1e-4), noise)]) {
                    clippedSum = materialize(clippedSum.map { add($0, clipped) } ?? clipped, extent: extent)
                    clippedCount += 1
                }
                if let e = skyEvidenceKernel.apply(extent: he, arguments: [toHalf(raw), stillHalf, toHalf(aligned), skyHalf]) {
                    evidence = materialize(evidence.map { add($0, e) } ?? e, extent: he)
                }
            }
        }
        guard let clippedSum, clippedCount >= 3 else { return nil }
        let sky = scaled(clippedSum, by: 1 / Float(clippedCount)).cropped(to: extent)
        var merged = sky
        if let evidence {
            // Evidência média alisada (8 px de ½): a estrela espalha "céu" em volta; no liso sem nada as duas médias são
            // iguais e a mistura não importa. Limite na escala do ruído que sobra depois de borrar
            let soft = scaled(evidence, by: 1 / Float(clippedCount)).clampedToExtent().applyingGaussianBlur(sigma: 8).cropped(to: he)
            let t = max(Float(1e-5), noise * 0.05)
            func toFull(_ small: CIImage) -> CIImage {
                small.clampedToExtent()
                    .transformed(by: CGAffineTransform(scaleX: 1 / half, y: 1 / half)
                        .concatenating(CGAffineTransform(translationX: extent.minX, y: extent.minY)))
                    .cropped(to: extent)
            }
            if let maskHalf = skyMaskKernel.apply(extent: he, arguments: [soft, t]) {
                // O chão sem os quentes, menos onde a evidência diz chão com clareza (abaixo de −5t: estrutura parada, como a luz
                // de um poste): lá nada é mexido (o quente e a luz parada de 1 px são iguais). No liso a evidência não decide (os
                // dois explicam igual) e o quente do céu voltaria pela mistura se o chão viesse inteiro sem tirar
                var ground = stillMean
                let bias = CGFloat(5 * t)
                let shifted = soft.applyingFilter("CIColorMatrix", parameters: ["inputBiasVector": CIVector(x: bias, y: bias, z: bias, w: 0)])
                if hotMask != nil, let fixHalf = skyMaskKernel.apply(extent: he, arguments: [shifted.cropped(to: he), t]) {
                    ground = fixHot(stillMean).applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: stillMean,
                                                                                              kCIInputMaskImageKey: toFull(fixHalf)])
                        .cropped(to: extent)
                }
                merged = sky.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: ground,
                                                                           kCIInputMaskImageKey: toFull(maskHalf)]).cropped(to: extent)
            }
        }
        var out = materialize(merged, extent: extent)
        // Revelação do céu: tons locais (sem o ajuste de luz da FOTO, que clarearia o céu inteiro) e a cor limpa pelo ISO de
        // uma foto com a luz de todas; sem nitidez (realçaria o ruído) e sem tirar pontos soltos (as estrelas são pontos)
        let effectiveISO = isoOf(reference) / Float(clippedCount)
        out = localTone(out, strength: 0.85)
        if effectiveISO >= 200 { out = nightDenoise(out, strength: min(0.6, log2(effectiveISO / 100) / 6)) }
        let output = finish(out.settingProperties(reference.properties), options: options)
        dlog(String(format: "Estrelas: %d fotos (céu alinhado, chão parado%@) · %@%@", clippedCount,
                    hotMask == nil ? "" : ", quentes tirados no céu", Diagnostics.ms(since: t0), output == nil ? " · FALHOU" : ""))
        return output
    }

    /// Máscara 0/1 guardada em 1 byte por pixel (R8) em vez de 8 (RGBA em meia precisão): 12 MB em vez de 96 MB a 12 MP.
    /// A ida (render) e a volta (bitmapData) podem contar as linhas de cima para baixo ou ao contrário: medido uma vez cada
    /// (as mesmas medidas da tabela do MAP e da LUA); se discordam, a volta é virada
    private static func compactMask(_ mask: CIImage, extent: CGRect) -> CIImage {
        let w = Int(extent.width), h = Int(extent.height)
        guard w > 0, h > 0 else { return mask }
        var bytes = Data(count: w * h)
        let shifted = mask.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
        bytes.withUnsafeMutableBytes { (raw: UnsafeMutableRawBufferPointer) in
            guard let base = raw.baseAddress else { return }
            gpu.render(shifted, toBitmap: base, rowBytes: w, bounds: CGRect(x: 0, y: 0, width: w, height: h), format: .R8, colorSpace: nil)
        }
        // Quantos quentes a máscara achou (no laboratório o caminho nunca rodava e o registro não dizia nada)
        let found = bytes.reduce(0) { $0 + ($1 >= 128 ? 1 : 0) }
        dlog("Estrelas: \(found) pixels quentes achados (parados no sensor, onde o céu andou ≥ 3 px)")
        var compact = CIImage(bitmapData: bytes, bytesPerRow: w, size: CGSize(width: w, height: h), format: .R8, colorSpace: nil)
        if bitmapFirstRowIsTop != renderFirstRowIsTop {
            compact = compact.transformed(by: CGAffineTransform(a: 1, b: 0, c: 0, d: -1, tx: 0, ty: CGFloat(h)))
        }
        return compact.transformed(by: CGAffineTransform(translationX: extent.minX, y: extent.minY))
    }

    /// Alinhamento fino para a NOITE: para cada foto, uma função que a coloca em cima da referência (a primeira).
    /// nil = a foto não encaixou em nada e fica de fora (antes entrava sem deslocar)
    /// `softening`: recebe o quanto o encaixe Catmull-Rom amolece a média, de 0 (todas em pixel inteiro, como no tripé) a ~1 (todas
    /// em meio pixel): média de [fx(1 − fx) + fy(1 − fy)] ÷ 0,5 das frações do deslocamento de cada foto que entrou (a referência
    /// conta 0)
    static func fineWarps(_ frames: [CapturedFrame], reference: CIImage,
                          softening: ((Float) -> Void)? = nil) -> [((CIImage) -> CIImage)?] {
        let e = reference.extent
        let centers = tileCenters(in: e)
        let alignments = alignTransforms(frames: frames, refIndex: 0, reference: reference, centers: centers)
        let grid = CIVector(x: centers[0].x, y: centers[0].y, z: centers[1].x - centers[0].x, w: centers[3].y - centers[0].y)
        if let softening {
            let placed = alignments.compactMap { $0 }
            let total = placed.reduce(Float(0)) { sum, a in
                let fx = Float(a.transform.tx - a.transform.tx.rounded(.down)), fy = Float(a.transform.ty - a.transform.ty.rounded(.down))
                return sum + (fx * (1 - fx) + fy * (1 - fy)) / 0.5
            }
            softening(placed.isEmpty ? 0 : total / Float(placed.count))
        }
        return alignments.map { alignment -> ((CIImage) -> CIImage)? in
            guard let alignment else { return nil }
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
    /// `stars` (ESTRELAS): o céu de estrelas é quase todo "liso" pela regra de sempre (variância do pedaço > 0,0004 na raiz do
    /// brilho): no laboratório só os 4 pedaços de baixo, com o chão parado, passavam ("4/16 pedaços", "andou 0,0 px") e o céu
    /// nunca era alinhado — as estrelas viravam rastro (pico 0,66) e o caminho dos quentes não rodava (quentes 1,12). Com
    /// `stars`: liso = variância abaixo de 3× o ruído do próprio pedaço, mediana 3×3 antes de comparar (o quente fixo no sensor
    /// puxava o encaixe para o zero) e giro + deslocamento pelo que mais pedaços confirmam (o chão parado discorda). Estudo em
    /// Python com os quadros do P04/P04b: 16/16 pedaços, erro até 0,29 px nos cantos (antes 1,4 e 5,1 px)
    private static func alignTransforms(frames: [CapturedFrame], refIndex: Int, reference: CIImage,
                                        centers: [CGPoint], stars: Bool = false) -> [Alignment?] {
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
        }, median: stars)
        // Quando um pedaço é liso demais para medir: a regra de sempre, ou (estrelas) abaixo de 3× o ruído do próprio pedaço
        let flat: [Float] = refPatches.map { p -> Float in
            guard stars, let p else { return 0.0004 }
            return max(1e-7, 3 * patchNoiseVariance(p, size: patch))
        }
        // Os pedaços da referência que o grosso e o centro leem são os mesmos em todas as fotos: lidos uma vez só
        let refCache = RefPatches()

        for i in frames.indices where i != refIndex {
            autoreleasepool {
                guard let img = image(from: frames[i]), let small = image(from: frames[i], scale: Float(alignScale)) else { return }
                // Grosso: busca nossa no centro, em ¹⁄₁₆ e depois em ¼ (até ±300 px). O Vision errava feio com a mão de verdade
                // (laboratório: andou 5 px, ele disse 28; andou 26, disse 48) e aí a busca fina não achava nada ("0/9")
                // Se o centro for liso demais para medir, parte do zero (o chute do Vision era pior que nada)
                let coarseFound = coarseShift(ref: smallRef, img: small, scale: alignScale, cache: refCache)
                var precise = coarseFound ?? .zero
                var coarseOK = coarseFound != nil
                var coarse = CGPoint(x: precise.x.rounded(), y: precise.y.rounded())
                // Pulo maior que a busca alcança (±300 px) é erro. As fotos do Alex andaram até 295 px: o limite antigo
                // (8% = 240 px na vertical) jogava fora um quadro bom
                let e = reference.extent
                if abs(coarse.x) > e.width * 0.12 || abs(coarse.y) > e.height * 0.12 { coarse = .zero; precise = .zero; coarseOK = false }
                // Pares (ponto na foto, ponto na referência) com precisão de fração de pixel
                var pairs: [(frame: CGPoint, ref: CGPoint)] = []
                var pairTile: [Int] = []
                let s = CGFloat(search)
                let imgPatches = grayPatches(img, rects: measure.map { c in
                    CGRect(x: c.x - half - coarse.x - s, y: c.y - half - coarse.y - s,
                           width: CGFloat(patch) + 2 * s, height: CGFloat(patch) + 2 * s)
                }, median: stars)
                for (k, c) in measure.enumerated() {
                    guard let refPatch = refPatches[k], let imgPatch = imgPatches[k],
                          let shift = subpixelShift(ref: refPatch, img: imgPatch, size: patch, search: search, flat: flat[k]) else { continue }
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
                // Estrelas: giro + deslocamento pelo que mais pedaços confirmam; só eles contam na sobra e na correção por região
                var agreeing: Set<Int>?
                if stars, let found = consensusSimilarity(pairs) {
                    t = found.transform
                    agreeing = Set(found.inliers)
                }
                // Sobra típica (a do meio: um pedaço com algo se mexendo não conta)
                let spread: CGFloat = t.map { fit in
                    let d = pairs.enumerated().filter { agreeing?.contains($0.offset) ?? true }.map { item -> CGFloat in
                        let m = item.element.frame.applying(fit)
                        return hypot(m.x - item.element.ref.x, m.y - item.element.ref.y)
                    }.sorted()
                    return d.isEmpty ? .infinity : d[d.count / 2]
                } ?? .infinity
                // Com menos de 10 dos 16 pedaços (escuro: só os com textura passam) os poucos que sobram podem concordar no
                // erro (NOITE do Pixel: 7/16, errando 0,9 px juntos por causa do carro que passa): vale o pedaço grande do
                // centro, maior nas fotos grandes. Estrelas: vale o giro que 4+ pedaços confirmaram (o centro só translada)
                let few = stars ? agreeing == nil : pairs.count < 10
                var centerOK = false
                if t == nil || spread > 0.5 || few {
                    let size = min(768, max(512, Int(reference.extent.width / 6) / 16 * 16))
                    if let full = centerShift(ref: reference, img: img, search: 6, size: size, start: precise, ambiguity: 0.97,
                                              cache: refCache) {
                        precise = full
                        centerOK = true
                    } else if pairs.count >= 2 || (pairs.count == 1 && !coarseOK) {
                        // Sem o centro (céu liso, Lua fora do meio, estrelas): o deslocamento típico dos pedaços que encaixaram
                        // (fração de pixel) vale mais que o grosso em ¼ — ou que nada, quando o grosso também não achou
                        let dx = pairs.map { $0.ref.x - $0.frame.x }.sorted(), dy = pairs.map { $0.ref.y - $0.frame.y }.sorted()
                        precise = CGPoint(x: dx[dx.count / 2], y: dy[dy.count / 2])
                        dlog("Super resolução: foto \(i + 1) · centro não encaixou: deslocamento pelos \(pairs.count) pedaços")
                    } else {
                        dlog("Super resolução: foto \(i + 1) · centro na foto cheia não encaixou (fica o grosso)")
                    }
                    // Nada encaixou (nem o grosso, nem um pedaço, nem o centro): a foto fica de fora. Antes entrava sem
                    // deslocar e a junção somava uma foto fora do lugar
                    if !coarseOK && pairs.isEmpty && !centerOK {
                        dlog("Super resolução: foto \(i + 1) · nada encaixou: fica de fora")
                        return
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
                for (n, pair) in pairs.enumerated() where trusted && (agreeing?.contains(n) ?? true) {
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
    static func coarseShift(ref: CIImage, img: CIImage, scale: CGFloat, cache: RefPatches? = nil) -> CGPoint? {
        // As fotos de noite do Alex (iPhone 17 Pro Max, na mão) andaram 40–130 px entre o 1º e o último quadro, e
        // até 350 px numa delas: ±96 px não alcançava. Primeiro uma busca larga numa versão 4× menor ainda
        // (±20 px lá = ±320 px na foto cheia), depois a busca de sempre, curta, em volta dela
        var start = CGPoint.zero
        let k: CGFloat = 0.25
        func tiny(_ i: CIImage) -> CIImage {
            i.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: k, kCIInputAspectRatioKey: 1])
        }
        if let wide = centerShift(ref: tiny(ref), img: tiny(img), search: 20, size: 128, start: .zero, cache: cache) {
            start = CGPoint(x: wide.x / k, y: wide.y / k)
        }
        // A busca larga pode falhar (centro liso): aí a de sempre, ±24 px a partir do zero
        let near = start == .zero ? 24 : 8
        // Em volta de um lugar já achado a janela é curta: o teste de encaixe ambíguo fica mais brando
        guard let shift = centerShift(ref: ref, img: img, search: near, size: 256, start: start,
                                      ambiguity: start == .zero ? 0.8 : 0.93, cache: cache)
                ?? (start == .zero ? nil : centerShift(ref: ref, img: img, search: 24, size: 256, start: .zero, cache: cache))
        else { return nil }
        // Na foto o ponto c da referência está em c − grosso: o grosso na escala cheia (com a fração)
        return CGPoint(x: shift.x / scale, y: shift.y / scale)
    }

    /// Deslocamento "grosso" (o que soma em c − grosso) entre as versões dadas, pelo pedaço do centro, buscando
    /// ±`search` px em volta de `start` (mesma escala e mesmo sentido do resultado).
    private static func centerShift(ref: CIImage, img: CIImage, search s: Int, size: Int, start: CGPoint,
                                    ambiguity: Float = 0.8, cache: RefPatches? = nil) -> CGPoint? {
        let e = ref.extent
        let n = min(size, Int(min(e.width, e.height) * 0.6) / 2 * 2)
        guard n >= 48 else { return nil }
        let rect = CGRect(x: (e.midX - CGFloat(n) / 2).rounded(), y: (e.midY - CGFloat(n) / 2).rounded(), width: CGFloat(n), height: CGFloat(n))
        let o = CGPoint(x: start.x.rounded(), y: start.y.rounded())
        // O pedaço da referência não depende da foto: com `cache` (mesma referência em todas as fotos) é lido uma vez só
        let refPatch: [Float]?
        if let cache {
            let key = "\(Int(e.minX)),\(Int(e.minY)),\(Int(e.width)),\(Int(e.height))|\(Int(rect.minX)),\(Int(rect.minY)),\(n)"
            refPatch = cache.patch(key) { grayPatches(ref, rects: [rect]).first ?? nil }
        } else {
            refPatch = grayPatches(ref, rects: [rect]).first ?? nil
        }
        guard let refPatch,
              let imgPatch = grayPatches(img, rects: [rect.offsetBy(dx: -o.x, dy: -o.y).insetBy(dx: -CGFloat(s), dy: -CGFloat(s))]).first ?? nil,
              let shift = subpixelShift(ref: refPatch, img: imgPatch, size: n, search: s, ambiguity: ambiguity) else { return nil }
        // O ponto c da referência está em c − o + (u, −v) nesta foto
        return CGPoint(x: o.x - shift.x, y: o.y + shift.y)
    }

    /// Luminância (raiz, para o escuro pesar parecido com o claro) de vários pedaços, linha 0 em cima.
    /// Todos os pedaços vão lado a lado numa imagem só e saem numa leitura.
    /// `median` (ESTRELAS): mediana 3×3 antes do borrão: o pixel quente (fixo no sensor, claro como uma estrela) some e as
    /// estrelas, que têm vizinhos claros, ficam
    private static func grayPatches(_ raw: CIImage, rects: [CGRect], median: Bool = false) -> [[Float]?] {
        guard let first = rects.first else { return [] }
        // Um leve borrão antes de comparar: no escuro o ruído enganava a busca (o laboratório mostrou "deslocamentos"
        // de 13 px e giros de 0,5° em fotos que andaram menos de 1,5 px). O deslocamento continua o mesmo
        let base = median ? raw.clampedToExtent().applyingFilter("CIMedianFilter") : raw.clampedToExtent()
        let image = base.applyingGaussianBlur(sigma: 1.2)
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
        guard let cg = gpu.createCGImage(atlas, from: atlasExtent, format: .RGBAf, colorSpace: linearP3),
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
                                      ambiguity: Float = 0.8, flat: Float = 0.0004) -> CGPoint? {
        func normalized(_ a: [Float]) -> ([Float], Float) {
            let mean = a.reduce(0, +) / Float(a.count)
            let variance = a.reduce(0) { $0 + ($1 - mean) * ($1 - mean) } / Float(a.count)
            let std = max(variance.squareRoot(), 1e-6)
            return (a.map { ($0 - mean) / std }, variance)
        }
        let (ref, refVariance) = normalized(rawRef)
        // Pedaço liso (céu, parede) não diz nada sobre o deslocamento
        guard refVariance > flat else { return nil }
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

    /// Pedaços da referência já lidos (chave: escala e lugar). Uma por alinhamento: a referência é a mesma em todas as fotos
    final class RefPatches {
        private var store: [String: [Float]] = [:]
        func patch(_ key: String, _ make: () -> [Float]?) -> [Float]? {
            if let hit = store[key] { return hit }
            let made = make()
            if let made { store[key] = made }
            return made
        }
    }

    /// Ruído (variância) de um pedaço já borrado 1,2 px: mediana de |diferença entre vizinhos| (x e y, 1 de cada 2) ÷ 0,6745,
    /// ao quadrado, ÷ 0,32 (no ruído branco borrado 1,2 px a diferença entre vizinhos tem 0,32 da variância). As estrelas são
    /// poucas e não mexem na mediana
    private static func patchNoiseVariance(_ p: [Float], size n: Int) -> Float {
        guard n >= 4, p.count >= n * n else { return 0 }
        var d: [Float] = []
        d.reserveCapacity(n * n / 2)
        var y = 0
        while y < n - 1 {
            var x = 0
            while x < n - 1 {
                let v = p[y * n + x]
                d.append(abs(p[y * n + x + 1] - v))
                d.append(abs(p[(y + 1) * n + x] - v))
                x += 2
            }
            y += 2
        }
        guard !d.isEmpty else { return 0 }
        d.sort()
        let m = d[d.count / 2] / 0.6745
        return m.isFinite ? m * m / 0.32 : 0
    }

    /// ESTRELAS: o céu inteiro gira junto e o chão parado discorda. O ajuste robusto de sempre começa da média de todos os
    /// pedaços e, com o chão em 4 dos 16 a menos de 1,5 px do céu, ficava torto (estudo em Python, polo: erro até 0,92 px). Aqui:
    /// cada par de pedaços dá um giro + deslocamento exato; vale o que mais pedaços confirmam (sobra ≤ 0,4 px), refeito por
    /// mínimos quadrados neles (polo: 0,26 px). nil com menos de 4 confirmando
    private static func consensusSimilarity(_ pairs: [(frame: CGPoint, ref: CGPoint)]) -> (transform: CGAffineTransform, inliers: [Int])? {
        guard pairs.count >= 4 else { return nil }
        var best: [Int] = []
        var bestCost = CGFloat.infinity
        for i in 0..<(pairs.count - 1) {
            for j in (i + 1)..<pairs.count {
                // ref = s·foto + t em números complexos: s = Δref / Δfoto (giro e escala), t pelo 1º ponto
                let fx = pairs[j].frame.x - pairs[i].frame.x, fy = pairs[j].frame.y - pairs[i].frame.y
                let rx = pairs[j].ref.x - pairs[i].ref.x, ry = pairs[j].ref.y - pairs[i].ref.y
                let d = fx * fx + fy * fy
                guard d > 100 else { continue }
                let a = (fx * rx + fy * ry) / d, b = (fx * ry - fy * rx) / d
                guard abs(a - 1) < 0.02, abs(b) < 0.02 else { continue }
                let tx = pairs[i].ref.x - (a * pairs[i].frame.x - b * pairs[i].frame.y)
                let ty = pairs[i].ref.y - (b * pairs[i].frame.x + a * pairs[i].frame.y)
                let t = CGAffineTransform(a: a, b: b, c: -b, d: a, tx: tx, ty: ty)
                var inliers: [Int] = []
                var cost: CGFloat = 0
                for (k, p) in pairs.enumerated() {
                    let m = p.frame.applying(t)
                    let r = hypot(m.x - p.ref.x, m.y - p.ref.y)
                    if r <= 0.4 {
                        inliers.append(k)
                        cost += r
                    }
                }
                if inliers.count > best.count || (inliers.count == best.count && cost < bestCost) {
                    best = inliers
                    bestCost = cost
                }
            }
        }
        guard best.count >= 4, let refit = fitSimilarity(best.map { pairs[$0] }) else { return nil }
        return (refit, best)
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

    /// Revela a foto em faixas dentro de um arquivo mapeado e grava o HEIC a partir dele. `scene(r)` dá a cena pronta
    /// (juntada e desconvoluída) nas linhas r; cada faixa pede `margin` linhas a mais em cima e embaixo para o que olha os
    /// vizinhos na revelação (tons locais, nitidez, limpeza) não marcar a emenda.
    /// 16 bits por cor e HEIC de 10 bits: em 8 bits o degradê do céu depois do MAP virava faixas. Sem o contexto de 16
    /// bits, 8 como antes
    private static func renderInStrips(extent: CGRect, properties: [String: Any], stripPixels: Double, margin: CGFloat,
                                       scene: (CGRect) -> CIImage?, grade: (CIImage) -> CIImage) -> Data? {
        let w = Int(extent.width), h = Int(extent.height)
        guard w > 0, h > 0 else { return nil }
        let size = w * h * 8
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
        var deep = true
        var made = CGContext(data: base, width: w, height: h, bitsPerComponent: 16, bytesPerRow: w * 8, space: displayP3,
                             bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder16Little.rawValue)
        if made == nil {
            deep = false
            made = CGContext(data: base, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4, space: displayP3,
                             bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)
        }
        guard let ctx = made else { return nil }
        // Faixas de ~8 MP: o Core Image só abre das fotos o pedaço que cada faixa precisa (e o MAP em faixas resolve uma por vez)
        let stripHeight = max(256, Int(stripPixels) / max(w, 1))
        let canvasBase = CIImage(color: .clear).cropped(to: extent)
        var y = 0
        while y < h {
            let rows = min(stripHeight, h - y)
            let rect = CGRect(x: 0, y: CGFloat(y), width: CGFloat(w), height: CGFloat(rows))
            let padded = rect.insetBy(dx: 0, dy: -margin).intersection(extent).integral
            let ok: Bool = autoreleasepool {
                guard let strip = scene(padded) else { return false }
                // A faixa vai numa tela do tamanho da foto: a vinheta do filme continua centrada na foto inteira
                let canvas = strip.cropped(to: padded).composited(over: canvasBase)
                guard let cg = gpu.createCGImage(grade(canvas), from: rect, format: deep ? .RGBA16 : .RGBA8,
                                                     colorSpace: displayP3) else { return false }
                ctx.draw(cg, in: rect)
                return true
            }
            guard ok else {
                dlog("❌ Super resolução: a faixa das linhas \(y)–\(y + rows) não saiu")
                return nil
            }
            y += rows
        }
        guard let provider = CGDataProvider(dataInfo: nil, data: UnsafeRawPointer(base), size: size, releaseData: { _, _, _ in }),
              let big = CGImage(width: w, height: h, bitsPerComponent: ctx.bitsPerComponent, bitsPerPixel: ctx.bitsPerPixel,
                                bytesPerRow: ctx.bytesPerRow, space: displayP3, bitmapInfo: ctx.bitmapInfo,
                                provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent) else { return nil }
        let exif = properties[kCGImagePropertyExifDictionary as String]
        var tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
        tiff?[kCGImagePropertyTIFFOrientation as String] = nil
        // 0,98: no SUPER ZOOM o HEIC já era o limite (Pixel: super resolução 42,0 dB, HEIC 0,9 sozinho 42,2 dB)
        // 10 bits pelo Core Image (como a FOTO) até 50 MP (a FOTO de 48 MP já passa por esse caminho); acima, o ImageIO direto
        if deep, w * h <= 50_000_000 {
            var meta: [String: Any] = [:]
            if let exif { meta[kCGImagePropertyExifDictionary as String] = exif }
            if let tiff { meta[kCGImagePropertyTIFFDictionary as String] = tiff }
            let image = CIImage(cgImage: big).settingProperties(meta)
            if let data = try? gpu.heif10Representation(of: image, colorSpace: displayP3, options: [
                kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.98,
            ]) {
                return data
            }
            dlog("⚠️ Super resolução: o HEIC de 10 bits falhou; gravando pelo ImageIO")
        }
        let out = NSMutableData()
        guard let destination = CGImageDestinationCreateWithData(out, UTType.heic.identifier as CFString, 1, nil) else { return nil }
        var props: [CFString: Any] = [kCGImageDestinationLossyCompressionQuality: 0.98]
        if let exif { props[kCGImagePropertyExifDictionary] = exif }
        if let tiff { props[kCGImagePropertyTIFFDictionary] = tiff }
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
