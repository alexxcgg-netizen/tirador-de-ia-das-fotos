import CoreImage
import Metal
import UIKit
import XCTest

/// Laboratório: revela RAWs de verdade com o código do app e grava as imagens para o Claude olhar.
/// Roda no simulador do iPhone, no GitHub (workflow "Revela (laboratório)").
final class LabTests: XCTestCase {
    private let env = ProcessInfo.processInfo.environment
    private var inDir: URL { URL(fileURLWithPath: env["LAB_IN"] ?? "/tmp/lab/in") }
    private var outDir: URL { URL(fileURLWithPath: env["LAB_OUT"] ?? "/tmp/lab/out") }

    override class func tearDown() {
        let env = ProcessInfo.processInfo.environment
        let out = URL(fileURLWithPath: env["LAB_OUT"] ?? "/tmp/lab/out")
        LabLog.lock.lock()
        let text = LabLog.lines.joined(separator: "\n")
        LabLog.lock.unlock()
        try? text.write(to: out.appendingPathComponent("log.txt"), atomically: true, encoding: .utf8)
        super.tearDown()
    }

    private func raws() -> [URL] {
        let files = (try? FileManager.default.contentsOfDirectory(at: inDir, includingPropertiesForKeys: nil)) ?? []
        return files.filter { $0.pathExtension.lowercased() == "dng" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
    }

    /// Pastas medidas em PSNR/ruído fino: PNG (sem perda). O JPEG 0,86 errava ~40 dB sozinho e escondia a melhora
    private let losslessFolders = ["superres/", "superres_var/", "foto_fusao/", "noite_mao/", "noite_filme/", "hdr/"]

    private func save(_ image: CIImage, _ name: String, maxSide: CGFloat = 900) {
        let e = image.extent
        let s = min(1, maxSide / max(e.width, e.height))
        var small = image
        if s < 1 {
            small = image.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: s, kCIInputAspectRatioKey: 1])
        }
        small = small.cropped(to: small.extent.integral)
        let lossless = losslessFolders.contains { name.hasPrefix($0) }
        let url = outDir.appendingPathComponent(name + (lossless ? ".png" : ".jpg"))
        try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        do {
            if lossless {
                try Developer.context.writePNGRepresentation(of: small, to: url, format: .RGBA8, colorSpace: Developer.displayP3)
            } else {
                try Developer.context.writeJPEGRepresentation(of: small, to: url, colorSpace: Developer.displayP3,
                                                              options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.86])
            }
        } catch {
            dlog("❌ não gravou \(name): \(error)")
        }
    }

    private func frame(_ url: URL) throws -> CapturedFrame {
        CapturedFrame(data: try Data(contentsOf: url), isRaw: true)
    }

    private func options(_ look: Look) -> DevelopOptions {
        var o = DevelopOptions()
        o.look = look
        o.originalAspect = true
        return o
    }

    private func reduced(_ scene: CIImage, to side: CGFloat) -> CIImage {
        let e = scene.extent
        let s = side / max(e.width, e.height)
        return scene.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: s, kCIInputAspectRatioKey: 1])
            .cropped(to: CGRect(x: 0, y: 0, width: (e.width * s).rounded(.down), height: (e.height * s).rounded(.down)))
    }

    func test0Environment() {
        dlog("GPU: \(MTLCreateSystemDefaultDevice()?.name ?? "nenhuma")")
        dlog("Kernels: \(Developer.kernelStatus)")
        dlog("RAWs: \(raws().map(\.lastPathComponent))")
        XCTAssertFalse(raws().isEmpty)
    }

    /// Cada filme numa versão pequena de cada RAW (a cena é aberta uma vez só).
    func test1Looks() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let scene = Developer.scene(for: try frame(url), scale: 0.5) else { dlog("❌ \(name) não abriu"); continue }
            let small = Developer.materialize(reduced(scene, to: 720), extent: reduced(scene, to: 720).extent)
            for (i, look) in Look.allCases.enumerated() {
                let (graded, _) = Developer.developed(small, options: options(look))
                save(graded, "looks/\(name)/\(String(format: "%02d", i))_\(look.rawValue)", maxSide: 720)
            }
            dlog("Filmes de \(name) gravados")
        }
    }

    /// Foto inteira: o nosso caminho (Neutro e Portra) e o da Apple, com recorte 100% no meio.
    func test2Foto() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            let f = try frame(url)
            for look in [Look.neutro, .portra] {
                let t0 = CFAbsoluteTimeGetCurrent()
                guard let out = Developer.develop(f, options: options(look)), let full = CIImage(data: out.heic) else { continue }
                dlog("\(name) \(look.rawValue): revelação inteira \(Diagnostics.ms(since: t0))")
                save(full, "foto/\(name)_\(look.rawValue)", maxSide: 1600)
                let e = full.extent
                let crop = CGRect(x: e.midX - 512, y: e.midY - 512, width: 1024, height: 1024)
                save(full.cropped(to: crop), "foto/\(name)_\(look.rawValue)_100pct", maxSide: 1024)
            }
            // Como a Apple revela o mesmo RAW (com o "boost" e os tons locais dela), para comparar
            if let raw = CIRAWFilter(imageData: f.data, identifierHint: "com.adobe.raw-image"), let apple = raw.outputImage {
                save(apple, "foto/\(name)_apple", maxSide: 1600)
                let ae = apple.extent
                save(apple.cropped(to: CGRect(x: ae.midX - 512, y: ae.midY - 512, width: 1024, height: 1024)), "foto/\(name)_apple_100pct", maxSide: 1024)
            }
        }
    }

    /// NOITE: a cena 4 paradas mais escura, com ruído de 12 fotos juntadas e luzes fortes, passando pelo fim da NOITE.
    func test3Night() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let linear = Developer.image(from: try frame(url), scale: 0.5) else { continue }
            let e = linear.extent
            let dark = Developer.scaled(linear, by: 1.0 / 16)
            // Ruído de sensor (já reduzido pela soma) e luzes de poste
            var night = Developer.add(dark.cropped(to: e), sensorNoise(e.integral, seed: 300, amplitude: 0.012)).cropped(to: e)
            for (fx, fy) in [(0.3, 0.6), (0.62, 0.55), (0.8, 0.7)] {
                let c = CGPoint(x: e.minX + e.width * fx, y: e.minY + e.height * fy)
                let lamp = CIFilter(name: "CIRadialGradient", parameters: [
                    "inputCenter": CIVector(cgPoint: c), "inputRadius0": 4, "inputRadius1": 14,
                    "inputColor0": CIColor(red: 30, green: 24, blue: 14, colorSpace: Developer.linearP3)!,
                    "inputColor1": CIColor(red: 0, green: 0, blue: 0, alpha: 0),
                ])!.outputImage!.cropped(to: e)
                night = lamp.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: night]).cropped(to: e)
            }
            night = Developer.materialize(night, extent: e)
            var o = options(.neutro)
            o.originalAspect = true
            save(Developer.developed(night, options: o).0, "noite/\(name)_0_antes")
            for points in [0, 6, 18] {
                let t0 = CFAbsoluteTimeGetCurrent()
                let finished = Developer.nightFinish(night, iso: 3200, frameCount: 12, starPoints: points)
                let out = Developer.developed(finished, options: o).0
                save(out, "noite/\(name)_1_noite_\(points)pontas")
                dlog("\(name) noite (\(points) pontas): \(Diagnostics.ms(since: t0))")
                if points > 0 {
                    let c = CGPoint(x: e.minX + e.width * 0.62, y: e.minY + e.height * 0.55)
                    save(out.cropped(to: CGRect(x: c.x - 300, y: c.y - 300, width: 600, height: 600)), "noite/\(name)_2_estrela_zoom_\(points)", maxSide: 600)
                }
            }
        }
    }

    /// Calibragens do tom lado a lado (o app usa a padrão; as outras são para comparar).
    func test4Tuning() throws {
        let variants: [(String, ToneTuning)] = [
            ("a_antiga", ToneTuning(filmicGain: 0.8, toeScale: 1, offsetScale: 1, saturation: 1, shadowRatio: 1, highlightRatio: 1,
                                    keyPull: 0, keyedSaturation: 0, highlightBoost: 0, whiteScale: 1, hueKeep: 0)),
            ("b_padrao", ToneTuning()),
            // Ombro da curva mais aberto (branco p99 vs Apple), com o ganho de entrada menor para o meio ficar
            ("c_ombro_1_25", ToneTuning(filmicGain: 0.9, highlightBoost: 0.7, whiteScale: 1.25)),
            ("d_ceu_1_0", ToneTuning(highlightBoost: 1.0)),
        ]
        let looks: [Look] = [.neutro, .portra, .classicChrome, .superia, .velvia, .trix]
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            let f = try frame(url)
            for (label, tuning) in variants {
                Developer.tuning = tuning
                guard let scene = Developer.scene(for: f, scale: 0.5) else { continue }
                let small = Developer.materialize(reduced(scene, to: 1000), extent: reduced(scene, to: 1000).extent)
                for look in looks {
                    let (graded, _) = Developer.developed(small, options: options(look))
                    save(graded, "tom/\(name)/\(look.rawValue)/\(label)", maxSide: 1000)
                }
            }
        }
        Developer.tuning = ToneTuning()
    }

    /// RETRATO sem profundidade de verdade: um mapa que vai de nítido (embaixo) a bem borrado (em cima),
    /// com luzes no fundo, para ver bolinhas de luz e se a cor do que está nítido vaza para o borrão.
    func test5Portrait() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let scene = Developer.scene(for: try frame(url), scale: 0.5) else { continue }
            let e = scene.extent
            var lit = scene
            for (fx, fy) in [(0.2, 0.8), (0.45, 0.85), (0.7, 0.78), (0.85, 0.9)] {
                let c = CGPoint(x: e.minX + e.width * fx, y: e.minY + e.height * fy)
                let lamp = CIFilter(name: "CIRadialGradient", parameters: [
                    "inputCenter": CIVector(cgPoint: c), "inputRadius0": 3, "inputRadius1": 6,
                    "inputColor0": CIColor(red: 6, green: 5, blue: 3.5, colorSpace: Developer.linearP3)!,
                    "inputColor1": CIColor(red: 0, green: 0, blue: 0, alpha: 0),
                ])!.outputImage!.cropped(to: e)
                lit = lamp.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: lit]).cropped(to: e)
            }
            // Embaixo nítido (sujeito), em cima borrado (fundo): degrau no meio para ver a borda
            let map = CIFilter(name: "CISmoothLinearGradient", parameters: [
                "inputPoint0": CIVector(x: e.midX, y: e.minY + e.height * 0.45),
                "inputPoint1": CIVector(x: e.midX, y: e.minY + e.height * 0.5),
                "inputColor0": CIColor(red: 0, green: 0, blue: 0), "inputColor1": CIColor(red: 1, green: 1, blue: 1),
            ])!.outputImage!.cropped(to: e)
            let t0 = CFAbsoluteTimeGetCurrent()
            let blurred = Developer.bokeh(Developer.materialize(lit, extent: e), map: map, radius: e.width * 0.025, extent: e)
            let out = Developer.developed(blurred, options: options(.neutro)).0
            save(out, "retrato/\(name)", maxSide: 1200)
            // Vazamento: a mesma cena com o sujeito trocado por magenta forte. Tudo que muda no fundo, logo acima da
            // borda, veio do sujeito. O mesmo com um desfoque comum (borra tudo e mistura pelo mapa) para comparar
            let radius = e.width * 0.025
            let magenta = CIImage(color: CIColor(red: 1.5, green: 0, blue: 1.5, colorSpace: Developer.linearP3)!).cropped(to: e)
            let swapped = lit.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: magenta, kCIInputMaskImageKey: map])
            let ours2 = Developer.bokeh(Developer.materialize(swapped, extent: e), map: map, radius: radius, extent: e)
            func naive(_ x: CIImage) -> CIImage {
                let b = x.clampedToExtent().applyingGaussianBlur(sigma: Double(radius) / 2).cropped(to: e)
                return b.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: x, kCIInputMaskImageKey: map])
            }
            let band = CGRect(x: e.minX, y: e.minY + e.height * 0.5, width: e.width, height: radius * 1.5)
            func leak(_ a: CIImage, _ b: CIImage) -> Float {
                let d = a.applyingFilter("CIDifferenceBlendMode", parameters: [kCIInputBackgroundImageKey: b]).cropped(to: band)
                    .applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: band)])
                var px = [Float](repeating: 0, count: 4)
                Developer.context.render(d, toBitmap: &px, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                                         format: .RGBAf, colorSpace: nil)
                return (px[0] + px[1] + px[2]) / 3
            }
            let leakOurs = leak(blurred, ours2), leakNaive = leak(naive(lit), naive(swapped))
            dlog(String(format: "RETRATO %@: vazamento nosso %.5f · desfoque comum %.5f", name, leakOurs, leakNaive))
            dlog("\(name) retrato: \(Diagnostics.ms(since: t0))")
        }
    }

    /// SUPER ZOOM: 10 fotos geradas do RAW (cada uma deslocada uma fração de pixel, com metade da resolução e ruído).
    /// Compara uma foto ampliada, a super resolução e o original de verdade.
    func test6SuperResolution() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let truthRaw = Developer.image(from: try frame(url), scale: 0.5) else { continue }
            let truth = Developer.materialize(truthRaw.cropped(to: truthRaw.extent.integral), extent: truthRaw.extent.integral)
            let e = truth.extent
            // Deslocamentos fixos (como uma mão tremendo, frações de pixel variadas): cada rodada mede o mesmo
            // 24 fotos, como o SUPER ZOOM tira agora (as 10 de sempre + 14 fixas, espalhadas em ±3 px)
            var fixed: [(CGFloat, CGFloat)] = [(0, 0), (1.3, -0.7), (-2.1, 1.6), (0.4, 2.7), (-1.6, -2.4),
                                               (2.6, 0.9), (-0.8, -1.2), (1.9, 2.2), (-2.7, 0.3), (0.7, -2.9)]
            for k in 0..<14 {
                let a = Double(k) * 2.399963, r = 0.6 + 2.3 * (Double(k) + 0.5) / 14
                fixed.append((CGFloat(r * cos(a)), CGFloat(r * sin(a))))
            }
            var lows: [CIImage] = []
            for i in 0..<fixed.count {
                let (dx, dy) = fixed[i]
                // Deslocamento bicúbico: o bilinear borrava cada foto (menos a de referência) antes do "sensor", um
                // detalhe perdido que nenhuma super resolução recupera (o protótipo em Python desloca sem borrar)
                let shifted = (Developer.warpCubic(truth, transform: CGAffineTransform(translationX: dx, y: dy), residuals: [],
                                                   grid: CIVector(x: 0, y: 0, z: 1, w: 1), extent: e)
                               ?? truth.clampedToExtent().transformed(by: CGAffineTransform(translationX: dx, y: dy))).cropped(to: e)
                // Como o sensor: cada pixel soma a luz de um quadrado 2×2 (sem filtro antes: tem serrilhado, que é
                // justamente o que a super resolução recupera)
                let quarter = { (x: CGFloat, y: CGFloat) in
                    Developer.scaled(shifted.clampedToExtent().transformed(by: CGAffineTransform(translationX: -x, y: -y)), by: 0.25)
                }
                var box = quarter(0, 0)
                for (x, y) in [(1, 0), (0, 1), (1, 1)] as [(CGFloat, CGFloat)] {
                    box = quarter(x, y).applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: box])
                }
                let low = box.samplingNearest().transformed(by: CGAffineTransform(scaleX: 0.5, y: 0.5))
                let le = CGRect(x: 0, y: 0, width: (e.width / 2).rounded(.down), height: (e.height / 2).rounded(.down))
                // Ruído de sensor de foto com pouca luz (desvio ~0,6%)
                let noisy = Developer.add(low.cropped(to: le), sensorNoise(le, seed: 400 + i, amplitude: 0.02)).cropped(to: le)
                lows.append(Developer.materialize(noisy, extent: le))
            }
            // Fotos de entrada em PNG de 16 bits (luz linear × 0,5), para rodar o protótipo em Python nas mesmas fotos
            do {  // as três câmeras (para estudar por que cada cena prefere uma desconvolução)
                let lin = CGColorSpace(name: CGColorSpace.linearDisplayP3)!
                for (i, low) in lows.enumerated() {
                    let url = outDir.appendingPathComponent("superres_cru/\(name)_\(i).png")
                    try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
                    try? Developer.context.writePNGRepresentation(of: Developer.scaled(low, by: 0.5), to: url, format: .RGBA16, colorSpace: lin)
                }
                let url = outDir.appendingPathComponent("superres_cru/\(name)_verdade.png")
                try? Developer.context.writePNGRepresentation(of: Developer.scaled(truth, by: 0.5), to: url, format: .RGBA16, colorSpace: lin)
                dlog("SUPER ZOOM cru: deslocamentos " + fixed.map { String(format: "(%.1f, %.1f)", $0.0, $0.1) }.joined(separator: " "))
            }
            Developer.decodeOverride = { frame, scale in
                let i = Int(frame.data.first ?? 0)
                guard lows.indices.contains(i) else { return nil }
                let img = lows[i]
                guard scale < 0.999 else { return img }
                return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                    .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                        height: (img.extent.height * CGFloat(scale)).rounded(.down)))
            }
            defer { Developer.decodeOverride = nil }
            let frames = (0..<fixed.count).map { CapturedFrame(data: Data([UInt8($0)]), isRaw: true) }
            let t0 = CFAbsoluteTimeGetCurrent()
            // Como o modo SUPER ZOOM: pelo menos 10, e toda foto nítida entra
            let out = Developer.superResolution(frames, options: options(.neutro), keep: 10)
            dlog("\(name) super resolução: \(Diagnostics.ms(since: t0))")
            let opts = options(.neutro)
            let crop = CGRect(x: e.midX - 300, y: e.midY - 300, width: 600, height: 600)
            let originalCrop = Developer.developed(truth, options: opts).0.cropped(to: crop)
            save(originalCrop, "superres/\(name)_0_original", maxSide: 600)
            // Quanto o HEIC 0,9 (o do SUPER ZOOM) erra sozinho: se for perto do que o SUPER ZOOM alcança, ele é o limite
            let flat = originalCrop.transformed(by: CGAffineTransform(translationX: -crop.minX, y: -crop.minY))
            if let heif = Developer.context.heifRepresentation(of: flat, format: .RGBA8, colorSpace: Developer.displayP3,
                                                               options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.9]),
               let back = CIImage(data: heif) {
                save(back, "superres/\(name)_3_original_heic", maxSide: 600)
            }
            let single = lows[0].applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: 2, kCIInputAspectRatioKey: 1])
            // A ampliada também passa pelo HEIC (no aparelho as duas seriam HEIC; antes só a super resolução levava a perda)
            var singleOut = Developer.developed(single, options: opts).0.cropped(to: crop)
            let flatSingle = singleOut.transformed(by: CGAffineTransform(translationX: -crop.minX, y: -crop.minY))
            if let heif = Developer.context.heifRepresentation(of: flatSingle, format: .RGBA8, colorSpace: Developer.displayP3,
                                                               options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.9]),
               let back = CIImage(data: heif) {
                singleOut = back
            }
            save(singleOut, "superres/\(name)_1_uma_ampliada", maxSide: 600)
            if let heic = out?.heic, let sr = CIImage(data: heic) {
                let se = sr.extent
                dlog("\(name) super resolução: \(Int(se.width))×\(Int(se.height)) (original \(Int(e.width))×\(Int(e.height)))")
                let c = CGRect(x: se.midX - 300, y: se.midY - 300, width: 600, height: 600)
                save(sr.cropped(to: c), "superres/\(name)_2_super", maxSide: 600)
            }
            // Variações da calibragem (para escolher a melhor no placar)
            let variants: [(String, Developer.SRTuning)] = [
                // Estudo em Python nas 24 fotos do teste: núcleo 0,6 + RL 0,9 px (0,45 × 2) com 10 passos = +4,90 dB
                ("limpeza_cor", .init(chromaClean: 2e-3)),
                ("tv_desconv", .init(splatSigma: 0.6, tv: true)),
            ]
            for (label, tuning) in variants {
                Developer.srTuning = tuning
                if let heic = Developer.superResolution(frames, options: options(.neutro), keep: 10)?.heic,
                   let sr = CIImage(data: heic) {
                    let se = sr.extent
                    save(sr.cropped(to: CGRect(x: se.midX - 300, y: se.midY - 300, width: 600, height: 600)),
                         "superres_var/\(name)_\(label)", maxSide: 600)
                }
            }
            Developer.srTuning = .init()
        }
    }

    /// NOITE de verdade (empilhamento): 8 fotos escuras, cada uma com o seu ruído e um tremidinho,
    /// e um "carro" (retângulo claro) passando em 3 delas. Mostra se some o ruído e se aparece fantasma.
    func test7NightStack() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let truthRaw = Developer.image(from: try frame(url), scale: 0.5) else { continue }
            let e = truthRaw.extent.integral
            let dark = Developer.materialize(Developer.scaled(truthRaw, by: 1.0 / 16).cropped(to: e), extent: e)
            var frames: [CIImage] = []
            for i in 0..<8 {
                var img = dark.clampedToExtent()
                    .transformed(by: CGAffineTransform(translationX: CGFloat(i % 3) * 0.7, y: CGFloat(i % 2) * 0.6)).cropped(to: e)
                if (2...4).contains(i) {
                    let car = CIImage(color: CIColor(red: 0.08, green: 0.05, blue: 0.03))
                        .cropped(to: CGRect(x: e.minX + e.width * (0.2 + 0.15 * CGFloat(i - 2)), y: e.minY + e.height * 0.3,
                                            width: e.width * 0.12, height: e.height * 0.07))
                    img = car.composited(over: img).cropped(to: e)
                }
                // Ruído de sensor limpo (o CIRandomGenerator sorteia a transparência e virava pontinhos)
                let noisy = Developer.add(img, sensorNoise(e, seed: 200 + i)).cropped(to: e)
                // Com o ISO da foto (como o RAW de verdade traz): sem ele o app achava ISO 800 e limpava pouco a pilha,
                // enquanto a foto única de comparação ia como ISO 3200
                frames.append(Developer.materialize(noisy, extent: e).settingProperties(iso3200))
            }
            Developer.decodeOverride = { frame, scale in
                let i = Int(frame.data.first ?? 0)
                guard frames.indices.contains(i) else { return nil }
                let img = frames[i]
                guard scale < 0.999 else { return img }
                return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                    .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                        height: (img.extent.height * CGFloat(scale)).rounded(.down)))
            }
            defer { Developer.decodeOverride = nil }
            let captured = (0..<8).map { CapturedFrame(data: Data([UInt8($0)]), isRaw: true) }
            var o = options(.neutro)
            o.originalAspect = true
            let single = Developer.developed(Developer.nightFinish(frames[0], iso: 3200, frameCount: 1, starPoints: 0), options: o).0
            save(single, "noite_pilha/\(name)_0_uma_foto", maxSide: 1200)
            // A mesma cena sem ruído: o placar mede o ruído só onde ela é lisa de verdade (a textura fina das nuvens,
            // numa NOITE já limpa, contava como ruído)
            let ideal = Developer.developed(Developer.nightFinish(dark.settingProperties(iso3200), iso: 3200, frameCount: 8, starPoints: 0), options: o).0
            save(ideal, "noite_pilha/\(name)_9_ideal", maxSide: 1200)
            // NOITE juntada com filme em 100% (como a foto da sala do Alex, com Ektar): o grão não pode virar pontinhos
            for (look, label) in [(Look.neutro, "neutro"), (Look.ektar, "ektar")] {
                guard let out = Developer.stack(captured, kind: .average, robust: true, starPoints: 0, options: options(look)),
                      let img = CIImage(data: out.heic) else { continue }
                let ie = img.extent
                save(img.cropped(to: CGRect(x: ie.midX - 400, y: ie.midY - 300, width: 800, height: 600).integral),
                     "noite_filme/\(name)_\(label)_100pct", maxSide: 800)
            }
            let t0 = CFAbsoluteTimeGetCurrent()
            if let out = Developer.stack(captured, kind: .average, robust: true, starPoints: 0, options: o), let img = CIImage(data: out.heic) {
                dlog("\(name) noite empilhada: \(Diagnostics.ms(since: t0))")
                save(img, "noite_pilha/\(name)_1_oito_fotos", maxSide: 1200)
                let ie = img.extent
                save(img.cropped(to: CGRect(x: ie.minX + ie.width * 0.15, y: ie.minY + ie.height * 0.2, width: ie.width * 0.5, height: ie.height * 0.3)),
                     "noite_pilha/\(name)_2_zoom_carro", maxSide: 900)
            }
        }
    }

    /// Estrela no sol de dia, para comparar com as fotos do iPhone 18 Pro em f/1.8 e f/4.
    func test8SunStar() throws {
        guard let url = raws().first(where: { $0.lastPathComponent.hasPrefix("iphone12") }) ?? raws().first,
              let scene = Developer.scene(for: try frame(url), scale: 0.5) else { return }
        let e = scene.extent
        let c = CGPoint(x: e.midX, y: e.minY + e.height * 0.8)
        let sun = CIFilter(name: "CIRadialGradient", parameters: [
            "inputCenter": CIVector(cgPoint: c), "inputRadius0": 10, "inputRadius1": 26,
            "inputColor0": CIColor(red: 400, green: 380, blue: 340, colorSpace: Developer.linearP3)!,
            "inputColor1": CIColor(red: 0, green: 0, blue: 0, alpha: 0),
        ])!.outputImage!.cropped(to: e)
        // Como no RAW de verdade: o sol chega estourado (cortado no branco do sensor)
        let lit = Developer.materialize(sun.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: scene])
            .applyingFilter("CIColorClamp", parameters: ["inputMinComponents": CIVector(x: 0, y: 0, z: 0, w: 0),
                                                         "inputMaxComponents": CIVector(x: 1.2, y: 1.2, z: 1.2, w: 1)])
            .cropped(to: e), extent: e)
        for points in [6, 18] {
            var o = options(.neutro)
            o.starPoints = points
            let out = Developer.developed(lit, options: o).0
            save(out, "sol/estrela_\(points)", maxSide: 1600)
            let s = min(e.width, e.height) * 0.3
            save(out.cropped(to: CGRect(x: c.x - s, y: c.y - s, width: 2 * s, height: 2 * s)), "sol/estrela_\(points)_zoom", maxSide: 700)
        }
    }

    /// HDR: a mesma cena com o dobro do contraste, fotografada em −2, 0 e +2 (cada uma cortada no branco do sensor,
    /// com o ruído que cada exposição teria). Compara a foto normal sozinha com o HDR juntado.
    func test9HDR() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let base = Developer.image(from: try frame(url), scale: 0.5) else { continue }
            let e = base.extent.integral
            let scene = Developer.scaled(base, by: 2.5).cropped(to: e)
            var frames: [CIImage] = []
            var clean: [CIImage] = []
            for (i, bias) in [-2, 0, 2].enumerated() {
                let gain = Float(pow(2.0, Double(bias)))
                let clampOne = { (x: CIImage) in x.applyingFilter("CIColorClamp", parameters: [
                    "inputMinComponents": CIVector(x: 0, y: 0, z: 0, w: 0), "inputMaxComponents": CIVector(x: 1, y: 1, z: 1, w: 1)]).cropped(to: e) }
                let exposed = clampOne(Developer.add(Developer.scaled(scene, by: gain), sensorNoise(e.integral, seed: 500 + i, amplitude: 0.01)))
                frames.append(Developer.materialize(exposed, extent: e))
                // As mesmas sem ruído: o placar mede o ruído como diferença para elas (nas sombras com textura, a medida
                // sozinha confundia folhagem e reflexo com ruído)
                clean.append(Developer.materialize(clampOne(Developer.scaled(scene, by: gain)), extent: e))
            }
            var useClean = false
            Developer.decodeOverride = { frame, scale in
                let i = Int(frame.data.first ?? 0)
                guard frames.indices.contains(i) else { return nil }
                let img = useClean ? clean[i] : frames[i]
                guard scale < 0.999 else { return img }
                return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                    .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                        height: (img.extent.height * CGFloat(scale)).rounded(.down)))
            }
            defer { Developer.decodeOverride = nil }
            let captured: [CapturedFrame] = [-2, 0, 2].enumerated().map { i, bias in
                var f = CapturedFrame(data: Data([UInt8(i)]), isRaw: true)
                f.exposureBias = Float(bias)
                return f
            }
            var o = options(.neutro)
            o.originalAspect = true
            save(Developer.developed(Developer.enhanced(frames[1]), options: o).0, "hdr/\(name)_0_foto_normal", maxSide: 1200)
            let t0 = CFAbsoluteTimeGetCurrent()
            var ho = o
            ho.hdrCompress = true
            if let out = Developer.hdr(captured, options: ho), let img = CIImage(data: out.heic) {
                dlog("\(name) HDR: \(Diagnostics.ms(since: t0))")
                save(img, "hdr/\(name)_1_hdr", maxSide: 1200)
            }
            useClean = true
            save(Developer.developed(Developer.enhanced(clean[1]), options: o).0, "hdr/\(name)_0_foto_normal_ideal", maxSide: 1200)
            if let out = Developer.hdr(captured, options: ho), let img = CIImage(data: out.heic) {
                save(img, "hdr/\(name)_1_hdr_ideal", maxSide: 1200)
            }
        }
    }

    /// FOTO 3×: 8 fotos do mesmo instante (mão mexendo de leve, luz de interior, ISO alto) juntadas, contra a foto única
    /// e contra a mesma cena sem ruído (o "ideal"). O placar quer ⅓ do erro da foto única (+4,8 dB) e ⅓ do ruído.
    func test12PhotoFusion() throws {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let base = Developer.image(from: try frame(url), scale: 0.5) else { continue }
            let e = base.extent.integral
            let truth = Developer.materialize(Developer.scaled(base.cropped(to: e), by: 0.25), extent: e)
            let shifts: [(CGFloat, CGFloat)] = [(0, 0), (0.8, -0.5), (-1.3, 0.9), (1.7, 1.2), (-0.6, -1.8), (2.2, -0.3), (-1.9, 1.6), (0.4, 2.1)]
            var frames: [CIImage] = []
            for (i, (dx, dy)) in shifts.enumerated() {
                let moved = truth.clampedToExtent().transformed(by: CGAffineTransform(translationX: dx, y: dy)).cropped(to: e)
                let noisy = Developer.add(moved, sensorNoise(e, seed: 600 + i, amplitude: 0.035)).cropped(to: e)
                frames.append(Developer.materialize(noisy, extent: e).settingProperties(iso800))
            }
            Developer.decodeOverride = { frame, scale in
                let i = Int(frame.data.first ?? 0)
                guard frames.indices.contains(i) else { return nil }
                let img = frames[i]
                guard scale < 0.999 else { return img }
                return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                    .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                        height: (img.extent.height * CGFloat(scale)).rounded(.down)))
            }
            defer { Developer.decodeOverride = nil }
            let o = options(.neutro)
            // As três pela mesma revelação completa (tons locais, nitidez, limpeza) que a FOTO usa
            guard let idealOut = Developer.finish(truth.settingProperties(iso800), options: o), let ideal = CIImage(data: idealOut.heic),
                  let singleOut = Developer.finish(frames[0], options: o), let single = CIImage(data: singleOut.heic) else { continue }
            let captured = (0..<shifts.count).map { CapturedFrame(data: Data([UInt8($0)]), isRaw: true) }
            let t0 = CFAbsoluteTimeGetCurrent()
            guard let out = Developer.fuse(captured, options: o), let fused = CIImage(data: out.heic) else { continue }
            dlog("\(name) FOTO juntada (\(shifts.count) fotos): \(Diagnostics.ms(since: t0))")
            for (img, label) in [(ideal, "0_ideal"), (single, "1_uma"), (fused, "2_juntada")] {
                let ie = img.extent
                save(img.cropped(to: CGRect(x: ie.midX - 400, y: ie.midY - 300, width: 800, height: 600).integral),
                     "foto_fusao/\(name)_\(label)", maxSide: 800)
            }
        }
    }

    /// Ruído de sensor: uniforme ±0,015 em cada cor, sorteado em memória com semente fixa (o teste dá sempre igual).
    /// O CIRandomGenerator sorteia também a transparência (o filtro de cor divide por ela) e não serve para isso.
    /// Cada semente cai num trecho bem longe da sequência (antes a foto 6 repetia o ruído da 0 andado 2 px).
    /// EXIF de foto de noite (ISO 3200), como o RAW de verdade traz
    private let iso3200: [String: Any] = [kCGImagePropertyExifDictionary as String: [kCGImagePropertyExifISOSpeedRatings as String: [3200]]]
    private let iso800: [String: Any] = [kCGImagePropertyExifDictionary as String: [kCGImagePropertyExifISOSpeedRatings as String: [800]]]

    private func sensorNoise(_ e: CGRect, seed index: Int, amplitude: Float = 0.03) -> CIImage {
        let w = Int(e.width), h = Int(e.height)
        var seed = UInt64(index + 1) << 40
        var values = [Float](repeating: 1, count: w * h * 4)
        for k in 0..<(w * h) {
            for c in 0..<3 {
                seed &+= 0x9E3779B97F4A7C15
                var z = seed
                z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
                z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
                z ^= z >> 31
                values[k * 4 + c] = (Float(z >> 40) / Float(1 << 24) - 0.5) * amplitude
            }
        }
        return CIImage(bitmapData: values.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: w * 16,
                       size: CGSize(width: w, height: h), format: .RGBAf, colorSpace: nil)
            .transformed(by: CGAffineTransform(translationX: e.minX, y: e.minY))
    }

    /// NOITE na mão como a do Alex: o caminho da mão medido na sequência das 23:13:48 (iPhone 17 Pro Max, até 39 px na
    /// foto cheia; aqui em meia resolução), um borrão de mexidinha em cada foto e duas fotos bem tremidas. Comparado com a
    /// mesma cena no tripé (mesmo ruído, sem mexer): o placar quer o detalhe no centro ≥ 90% do tripé.
    func test11HandheldNight() throws {
        guard let url = raws().first(where: { $0.lastPathComponent.hasPrefix("iphone12") }) ?? raws().first,
              let base = Developer.image(from: try frame(url), scale: 0.5) else { return }
        let e = base.extent.integral
        let truth = Developer.materialize(base.cropped(to: e), extent: e)
        let path: [(CGFloat, CGFloat)] = [(0, 0), (-6.5, -15), (-7.5, -16), (-15.5, -0.5), (-13, 5), (-2.5, 5.5),
                                          (-5, 12), (-5.5, 19.5), (3, 8), (6, -4), (10, 2), (14, 9)]
        // Três: tripé, mão e a mesma cena sem ruído e sem mexer (a régua: o erro de cada uma contra ela)
        for (handheld, clean) in [(false, false), (true, false), (false, true)] {
            var frames: [CIImage] = []
            for (i, (px, py)) in path.enumerated() {
                var img = truth.clampedToExtent()
                // Deslocamento inteiro (sem interpolar: qualquer filtro amolece a foto já no teste, antes do app; as do tripé
                // não eram deslocadas). A fração da mão de verdade fica no borrão de movimento logo abaixo
                let (dx, dy) = (px.rounded(), py.rounded())
                if handheld {
                    // Inteiro: o deslocamento é exato, sem filtro nenhum
                    img = truth.clampedToExtent().transformed(by: CGAffineTransform(translationX: dx, y: dy))
                    // Borrão da mexidinha durante a foto, na direção em que a mão ia (as fotos 4 e 8 tremeram bem)
                    let next = path[min(i + 1, path.count - 1)], prev = path[max(i - 1, 0)]
                    let angle = atan2(next.1 - prev.1, next.0 - prev.0)
                    // 1 px nas normais (1/8 s; nas NOITEs do Alex as de 1/10 s saíram nítidas), 9 px nas tremidas
                    let length: CGFloat = (i == 3 || i == 7) ? 9 : 1
                    // Borrão de movimento de verdade: média de cópias deslocadas ao longo do caminho (o CIMotionBlur com
                    // raio pequeno borrava muito mais que 1 px e o teste ficava mais duro que a mão)
                    let taps = 7
                    var sum: CIImage?
                    for t in 0..<taps {
                        let f = (CGFloat(t) / CGFloat(taps - 1) - 0.5) * length
                        let moved = Developer.warpCubic(truth, transform: CGAffineTransform(translationX: dx + f * cos(angle), y: dy + f * sin(angle)),
                                                        residuals: [], grid: CIVector(x: 0, y: 0, z: 1, w: 1), extent: e) ?? img
                        sum = sum.map { Developer.add($0, moved) } ?? moved
                    }
                    if let sum { img = Developer.scaled(sum, by: 1 / Float(taps)).clampedToExtent() }
                }
                // Luz de fim de tarde e ruído leve: aqui mede-se a nitidez (alinhamento + fotos tremidas fora); o ruído do
                // escuro já tem o teste da pilha. No escuro total a medida de borda contava o ruído como "detalhe"
                img = Developer.add(Developer.scaled(img.cropped(to: e), by: 0.25), sensorNoise(e, seed: 100 + i, amplitude: clean ? 0 : 0.01)).cropped(to: e)
                frames.append(Developer.materialize(img, extent: e).settingProperties(iso3200))
            }
            Developer.decodeOverride = { frame, scale in
                let i = Int(frame.data.first ?? 0)
                guard frames.indices.contains(i) else { return nil }
                let img = frames[i]
                guard scale < 0.999 else { return img }
                return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                    .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                        height: (img.extent.height * CGFloat(scale)).rounded(.down)))
            }
            defer { Developer.decodeOverride = nil }
            let captured = (0..<path.count).map { CapturedFrame(data: Data([UInt8($0)]), isRaw: true) }
            let t0 = CFAbsoluteTimeGetCurrent()
            // A régua sem desfazer borrão: ela não tem borrão nenhum, e desfazer o que não existe deixava a régua
            // supernítida (halo nas bordas), e a foto na mão era cobrada contra esse halo
            let savedNight = Developer.nightTuning
            if clean { Developer.nightTuning.deblurIterations = 0 }
            defer { Developer.nightTuning = savedNight }
            guard let out = Developer.stack(captured, kind: .average, robust: true, starPoints: 0, options: options(.neutro)),
                  let img = CIImage(data: out.heic) else { continue }
            let name = clean ? "ideal" : (handheld ? "mao" : "tripe")
            dlog("NOITE \(name): \(path.count) fotos em \(Diagnostics.ms(since: t0))")
            let ie = img.extent
            if handheld {
                // Uma foto só tirada na mão (a 1ª, revelada sozinha pela NOITE): o 3× é ⅓ do erro dela contra a cena sem ruído
                let single = Developer.developed(Developer.nightFinish(frames[0], iso: 3200, frameCount: 1, starPoints: 0),
                                                 options: options(.neutro)).0
                let se = single.extent
                save(single.cropped(to: CGRect(x: se.midX - 400, y: se.midY - 300, width: 800, height: 600).integral),
                     "noite_mao/uma_100pct", maxSide: 800)
            }
            // Centro em 100% (sem reduzir): é onde a nitidez aparece
            save(img.cropped(to: CGRect(x: ie.midX - 400, y: ie.midY - 300, width: 800, height: 600).integral), "noite_mao/\(name)_100pct", maxSide: 800)
            save(img, "noite_mao/\(name)", maxSide: 1200)
        }
    }

    /// Alinhamento com deslocamentos de mão de verdade (10–26 px, em todas as direções, e um de 170 px como nas NOITEs
    /// do Alex), de dia e no escuro com ruído.
    /// O registro "desloca x, y" de cada foto tem que dar o contrário do deslocamento aplicado.
    func test10Alignment() throws {
        guard let url = raws().first(where: { $0.lastPathComponent.hasPrefix("iphone12") }) ?? raws().first,
              let base = Developer.image(from: try frame(url), scale: 0.5) else { return }
        let e = base.extent.integral
        let truth = Developer.materialize(base.cropped(to: e), extent: e)
        let shifts: [(CGFloat, CGFloat)] = [(0, 0), (12.4, -7.3), (-18.6, 15.2), (25.1, 22.7), (-9.8, -26.4), (5.3, 3.1), (-140.6, 96.2)]
        for dark in [false, true] {
            var frames: [CIImage] = []
            for (i, (dx, dy)) in shifts.enumerated() {
                var img = truth.clampedToExtent().transformed(by: CGAffineTransform(translationX: dx, y: dy)).cropped(to: e)
                if dark {
                    // Ruído de sensor: uniforme ±0,015 em cada cor, sorteado em memória com semente fixa (o teste dá
                    // sempre igual). Antes vinha do CIRandomGenerator, que sorteia também a transparência: o filtro de
                    // cor divide por ela e o "ruído" virava uma mistura que nenhum sensor tem (Python com ruído limpo: 0,09 px)
                    let noise = sensorNoise(e, seed: i)
                    img = Developer.add(Developer.scaled(img, by: 1.0 / 16), noise).cropped(to: e)
                }
                frames.append(Developer.materialize(img, extent: e))
            }
            Developer.decodeOverride = { frame, scale in
                let i = Int(frame.data.first ?? 0)
                guard frames.indices.contains(i) else { return nil }
                let img = frames[i]
                guard scale < 0.999 else { return img }
                return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                    .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                        height: (img.extent.height * CGFloat(scale)).rounded(.down)))
            }
            defer { Developer.decodeOverride = nil }
            dlog("ALINHAMENTO \(dark ? "escuro" : "dia"): esperado " + shifts.dropFirst().map { String(format: "(%.1f, %.1f)", -$0.0, -$0.1) }.joined(separator: " "))
            let captured = (0..<shifts.count).map { CapturedFrame(data: Data([UInt8($0)]), isRaw: true) }
            Developer.logTiles = !dark
            _ = Developer.fineWarps(captured, reference: frames[0])
            Developer.logTiles = false
            dlog("ALINHAMENTO \(dark ? "escuro" : "dia"): fim")
        }
    }
}
