import CoreImage
import CoreVideo
import Foundation
import UIKit
import XCTest

/// Prevenção: cada teste aqui reproduz um defeito achado na revisão de código, para ele não voltar sem ninguém ver.
/// Cenas pequenas (recortes reduzidos dos RAWs de exemplo ou cenas sintéticas), para o laboratório inteiro caber em
/// ~1 h. As medidas ficam no placar.py (seção "Prevenção"); aqui só se gera, revela pelo caminho do app e grava.
///
/// Regra de justiça (vale para todo teste novo): a régua (ideal / foto única / cena limpa) passa pelo MESMO caminho de
/// revelação que o app usa no modo testado. Senão o teste mede a diferença entre caminhos, não o defeito.
final class PrevencaoTests: XCTestCase {
    private let env = ProcessInfo.processInfo.environment
    private var inDir: URL { URL(fileURLWithPath: env["LAB_IN"] ?? "/tmp/lab/in") }
    private var outDir: URL { URL(fileURLWithPath: env["LAB_OUT"] ?? "/tmp/lab/out") }

    /// O registro inteiro (de todas as classes) também vai para o log.txt no fim desta classe: a que terminar por
    /// último grava tudo.
    override class func tearDown() {
        let env = ProcessInfo.processInfo.environment
        let out = URL(fileURLWithPath: env["LAB_OUT"] ?? "/tmp/lab/out")
        LabLog.lock.lock()
        let text = LabLog.lines.joined(separator: "\n")
        LabLog.lock.unlock()
        try? text.write(to: out.appendingPathComponent("log.txt"), atomically: true, encoding: .utf8)
        super.tearDown()
    }

    // MARK: - Ajudantes

    private func raws() -> [URL] {
        let files = (try? FileManager.default.contentsOfDirectory(at: inDir, includingPropertiesForKeys: nil)) ?? []
        return files.filter { $0.pathExtension.lowercased() == "dng" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
    }

    private func firstRaw() -> URL? {
        let all = raws()
        return all.first(where: { $0.lastPathComponent.hasPrefix("iphone12") }) ?? all.first
    }

    private func options(_ look: Look = .neutro) -> DevelopOptions {
        var o = DevelopOptions()
        o.look = look
        o.originalAspect = true
        o.grain = 0
        return o
    }

    private func isoProps(_ value: Int) -> [String: Any] {
        [kCGImagePropertyExifDictionary as String: [kCGImagePropertyExifISOSpeedRatings as String: [value]]]
    }

    private func image(_ output: Developer.Output?) -> CIImage? {
        guard let heic = output?.heic else { return nil }
        return CIImage(data: heic)
    }

    /// Tudo em PNG (sem perda) e no tamanho cheio: o placar mede posições e diferenças finas.
    private func savePNG(_ image: CIImage, _ name: String) {
        let e = image.extent.integral
        let flat = image.cropped(to: e).transformed(by: CGAffineTransform(translationX: -e.minX, y: -e.minY))
        let url = outDir.appendingPathComponent(name + ".png")
        try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        do {
            try Developer.context.writePNGRepresentation(of: flat, to: url, format: .RGBA8, colorSpace: Developer.displayP3)
        } catch {
            dlog("❌ não gravou \(name): \(error)")
        }
    }

    /// Cena linear (luz do RAW) com tamanho exato e origem em 0: o miolo do RAW na proporção pedida, reduzido com
    /// Lanczos (com margem, para a borda não escurecer).
    private func scene(_ url: URL, width: Int, height: Int, rawScale: Float = 0.5) -> CIImage? {
        guard let data = try? Data(contentsOf: url),
              let base = Developer.linear(dng: data, scale: rawScale) else { return nil }
        let e = base.extent.integral
        let aspect = CGFloat(width) / CGFloat(height)
        let margin: CGFloat = 8
        var cw = e.width - 2 * margin, ch = cw / aspect
        if ch > e.height - 2 * margin {
            ch = e.height - 2 * margin
            cw = ch * aspect
        }
        let s = CGFloat(width) / cw
        let crop = CGRect(x: e.midX - cw / 2 - margin, y: e.midY - ch / 2 - margin, width: cw + 2 * margin, height: ch + 2 * margin)
        var moved = base.cropped(to: crop).transformed(by: CGAffineTransform(translationX: -crop.minX, y: -crop.minY))
        if abs(s - 1) > 0.001 {
            moved = moved.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: s, kCIInputAspectRatioKey: 1])
        }
        let out = CGRect(x: 0, y: 0, width: width, height: height)
        let placed = moved.transformed(by: CGAffineTransform(translationX: -margin * s, y: -margin * s)).cropped(to: out)
        return Developer.materialize(placed, extent: out)
    }

    /// O app abre os quadros pelo `Developer.decodeOverride`: aqui ele recebe as imagens geradas (índice no 1º byte).
    /// Quem chama zera o override depois (`defer { Developer.decodeOverride = nil }`).
    private func feed(_ frames: [CIImage]) -> [CapturedFrame] {
        Developer.decodeOverride = { frame, scale in
            let i = Int(frame.data.first ?? 0)
            guard frames.indices.contains(i) else { return nil }
            let img = frames[i]
            guard scale < 0.999 else { return img }
            return img.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: scale, kCIInputAspectRatioKey: 1])
                .cropped(to: CGRect(x: 0, y: 0, width: (img.extent.width * CGFloat(scale)).rounded(.down),
                                    height: (img.extent.height * CGFloat(scale)).rounded(.down)))
        }
        return frames.indices.map { CapturedFrame(data: Data([UInt8($0)]), isRaw: true) }
    }

    /// Ruído de sensor uniforme (±amplitude/2) em cada cor, com semente fixa (igual ao do LabTests).
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

    /// Como o sensor do teste do SUPER ZOOM: desloca a cena (bicúbico, na resolução da cena) e soma quadrados 2×2
    /// (meia resolução, com o serrilhado que a super resolução recupera). Deslocamento em pixels da cena.
    private func sensor(_ truth: CIImage, dx: CGFloat, dy: CGFloat) -> CIImage {
        let e = truth.extent
        let shifted = (Developer.warpCubic(truth, transform: CGAffineTransform(translationX: dx, y: dy), residuals: [],
                                           grid: CIVector(x: 0, y: 0, z: 1, w: 1), extent: e)
                       ?? truth.clampedToExtent().transformed(by: CGAffineTransform(translationX: dx, y: dy))).cropped(to: e)
        let quarter = { (x: CGFloat, y: CGFloat) in
            Developer.scaled(shifted.clampedToExtent().transformed(by: CGAffineTransform(translationX: -x, y: -y)), by: 0.25)
        }
        var box = quarter(0, 0)
        for (x, y) in [(1, 0), (0, 1), (1, 1)] as [(CGFloat, CGFloat)] {
            box = quarter(x, y).applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: box])
        }
        let low = box.samplingNearest().transformed(by: CGAffineTransform(scaleX: 0.5, y: 0.5))
        let le = CGRect(x: 0, y: 0, width: (e.width / 2).rounded(.down), height: (e.height / 2).rounded(.down))
        return low.cropped(to: le)
    }

    /// Desloca uma imagem por fração de pixel (bicúbico do app; sem ele, a transformação comum).
    private func shifted(_ image: CIImage, dx: CGFloat, dy: CGFloat) -> CIImage {
        let e = image.extent
        return (Developer.warpCubic(image, transform: CGAffineTransform(translationX: dx, y: dy), residuals: [],
                                    grid: CIVector(x: 0, y: 0, z: 1, w: 1), extent: e)
                ?? image.clampedToExtent().transformed(by: CGAffineTransform(translationX: dx, y: dy))).cropped(to: e)
    }

    // MARK: - 1. Geometria (funções puras, sem imagem)

    /// Recorte pela lente que tirou a foto e o ponto do Retrato (espelho, giro, recorte) — `CaptureGeometry`, ainda
    /// não ligado no CameraModel — e o recorte de proporção/zoom que a revelação já usa (`AspectRatio`, `DevelopOptions`).
    func testP01Geometria() {
        var ok = 0, total = 0
        func pass(_ good: Bool, _ what: String) {
            total += 1
            if good { ok += 1 } else { dlog("GEOMETRIA ❌ " + what) }
            XCTAssertTrue(good, what)
        }
        func near(_ a: CGFloat, _ b: CGFloat) -> Bool { abs(a - b) < 1e-6 }
        func crop(_ label: String, wanted: CGFloat, base: CGFloat, front: Bool = false, expect: CGFloat) {
            let got = CaptureGeometry.cropFactor(wantedZoom: wanted, captureBaseZoom: base, front: front)
            pass(near(got, expect), String(format: "recorte %@: %.3f (esperado %.3f)", label, Double(got), Double(expect)))
        }
        crop("2× na grande-angular", wanted: 2, base: 1, expect: 2)
        crop("8× na tele", wanted: 8, base: 4, expect: 2)
        crop("4× com a foto vinda da tele", wanted: 4, base: 4, expect: 1)
        crop("4× com a foto ainda vinda da grande-angular (troca de lente no meio)", wanted: 4, base: 1, expect: 4)
        crop("1× com a foto ainda vinda da ultra-angular", wanted: 1, base: 0.5, expect: 2)
        crop("0,5× na ultra-angular", wanted: 0.5, base: 0.5, expect: 1)
        crop("2× pedido e foto da tele (não recorta para menos de 1)", wanted: 2, base: 4, expect: 1)
        crop("frente 2×", wanted: 2, base: 1, front: true, expect: 2)
        crop("frente 5× (limite 3×)", wanted: 5, base: 1, front: true, expect: 3)
        crop("lente desconhecida (0)", wanted: 3, base: 0, expect: 1)
        crop("zoom inválido", wanted: .nan, base: 1, expect: 1)

        func point(_ label: String, _ view: CGPoint, crop c: CGFloat = 1, mirrored: Bool = false, turns: Int = 0, expect: CGPoint) {
            let got = CaptureGeometry.photoPoint(fromView: view, crop: c, mirrored: mirrored, quarterTurns: turns)
            pass(near(got.x, expect.x) && near(got.y, expect.y),
                 String(format: "ponto %@: (%.3f, %.3f) (esperado (%.3f, %.3f))", label, Double(got.x), Double(got.y),
                        Double(expect.x), Double(expect.y)))
        }
        point("sem nada", CGPoint(x: 0.3, y: 0.7), expect: CGPoint(x: 0.3, y: 0.7))
        point("centro com recorte 3×", CGPoint(x: 0.5, y: 0.5), crop: 3, expect: CGPoint(x: 0.5, y: 0.5))
        point("recorte 2×", CGPoint(x: 0.25, y: 0.75), crop: 2, expect: CGPoint(x: 0.375, y: 0.625))
        point("espelho", CGPoint(x: 0.2, y: 0.4), mirrored: true, expect: CGPoint(x: 0.8, y: 0.4))
        point("espelho + recorte 2×", CGPoint(x: 0.2, y: 0.4), crop: 2, mirrored: true, expect: CGPoint(x: 0.65, y: 0.45))
        point("um quarto de volta", CGPoint(x: 0.9, y: 0.2), turns: 1, expect: CGPoint(x: 0.2, y: 0.1))
        point("quarto anti-horário (−1)", CGPoint(x: 0.9, y: 0.2), turns: -1, expect: CGPoint(x: 0.8, y: 0.9))
        point("espelho + quarto de volta", CGPoint(x: 0.9, y: 0.2), mirrored: true, turns: 1, expect: CGPoint(x: 0.2, y: 0.9))
        point("recorte inválido (0,5) conta como 1", CGPoint(x: 0.1, y: 0.9), crop: 0.5, expect: CGPoint(x: 0.1, y: 0.9))
        point("fora do visor fica na borda", CGPoint(x: 1.2, y: -0.1), expect: CGPoint(x: 1, y: 0))

        // Ida e volta: o caminho do visor (gira, recorta, espelha) desfeito pela função volta ao mesmo ponto
        func forward(_ p: CGPoint, crop c: CGFloat, mirrored: Bool, turns: Int) -> CGPoint {
            var x = p.x, y = p.y
            for _ in 0..<(((turns % 4) + 4) % 4) { (x, y) = (1 - y, x) }
            x = 0.5 + (x - 0.5) * c
            y = 0.5 + (y - 0.5) * c
            if mirrored { x = 1 - x }
            return CGPoint(x: x, y: y)
        }
        var roundTrip = 0, roundTripOK = 0
        for c in [1, 1.7, 3] as [CGFloat] {
            for mirrored in [false, true] {
                for turns in -1...3 {
                    for (fx, fy) in [(-0.4, -0.3), (0.35, -0.2), (0.1, 0.45), (-0.25, 0.3)] as [(CGFloat, CGFloat)] {
                        let p = CGPoint(x: 0.5 + fx / c, y: 0.5 + fy / c)
                        let back = CaptureGeometry.photoPoint(fromView: forward(p, crop: c, mirrored: mirrored, turns: turns),
                                                              crop: c, mirrored: mirrored, quarterTurns: turns)
                        roundTrip += 1
                        if abs(back.x - p.x) < 1e-6, abs(back.y - p.y) < 1e-6 { roundTripOK += 1 }
                    }
                }
            }
        }
        pass(roundTripOK == roundTrip, "ida e volta do ponto do Retrato: \(roundTripOK)/\(roundTrip)")

        // O que a revelação já faz: proporção e zoom centrados
        func rect(_ label: String, _ got: CGRect, _ expect: CGRect) {
            pass(near(got.minX, expect.minX) && near(got.minY, expect.minY) && near(got.width, expect.width) && near(got.height, expect.height),
                 "\(label): \(got) (esperado \(expect))")
        }
        let land = CGRect(x: 0, y: 0, width: 4000, height: 3000), port = CGRect(x: 0, y: 0, width: 3000, height: 4000)
        rect("4:3 com zoom 2×", AspectRatio.r43.crop(land, zoom: 2), CGRect(x: 1000, y: 750, width: 2000, height: 1500))
        rect("16:9 deitada", AspectRatio.r169.crop(land, zoom: 1), CGRect(x: 0, y: 375, width: 4000, height: 2250))
        rect("1:1 em pé", AspectRatio.r11.crop(port, zoom: 1), CGRect(x: 0, y: 500, width: 3000, height: 3000))
        var keep = DevelopOptions()
        keep.originalAspect = true
        keep.zoom = 2
        rect("proporção original com zoom 2×", keep.cropRect(in: land), CGRect(x: 1000, y: 750, width: 2000, height: 1500))
        dlog("GEOMETRIA: \(ok)/\(total) casos certos")
    }

    // MARK: - 2. LONGA (seda e rastros)

    /// LONGA com quadros de vídeo de 8 bits (BGRA, como a câmera entrega) direto no acumulador do app:
    /// - seda, 240 quadros (8 s a 30 fps) de uma rampa clara com pontilhado no tempo: a média tem que sair igual à
    ///   média exata (meia precisão somando 240 quadros arredonda cada soma e faz degraus no céu);
    /// - rastros numa rampa clara: o máximo exato, sem degraus a mais que os da entrada;
    /// - quadros escuros só com ruído (preto 12, σ 2 códigos): os rastros não podem levantar o preto mais que ~1σ
    ///   (o máximo de 60 quadros de ruído sobe ~2,3σ: preto vira cinza); a seda não levanta nada.
    func testP02Longa() {
        let w = 512, h = 64
        func lin(_ v: Double) -> Double { v <= 0.04045 ? v / 12.92 : pow((v + 0.055) / 1.055, 2.4) }
        func enc(_ l: Double) -> Double {
            let x = max(0, l)
            return x <= 0.0031308 ? x * 12.92 : 1.055 * pow(x, 1 / 2.4) - 0.055
        }
        func makeFrame(_ codes: [UInt8]) -> CIImage? {
            var buffer: CVPixelBuffer?
            let attributes: [CFString: Any] = [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any]]
            guard CVPixelBufferCreate(nil, w, h, kCVPixelFormatType_32BGRA, attributes as CFDictionary, &buffer) == kCVReturnSuccess,
                  let buffer else { return nil }
            CVPixelBufferLockBaseAddress(buffer, [])
            if let base = CVPixelBufferGetBaseAddress(buffer) {
                let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
                let p = base.assumingMemoryBound(to: UInt8.self)
                for y in 0..<h {
                    for x in 0..<w {
                        let v = codes[y * w + x]
                        let o = y * rowBytes + x * 4
                        p[o] = v
                        p[o + 1] = v
                        p[o + 2] = v
                        p[o + 3] = 255
                    }
                }
            }
            CVPixelBufferUnlockBaseAddress(buffer, [])
            return CIImage(cvPixelBuffer: buffer, options: [.colorSpace: Developer.displayP3])
        }
        /// Roda o acumulador do app como a câmera: start, um add por quadro, stop.
        func accumulate(_ style: LongExposure.Style, _ count: Int, _ codes: (Int) -> [UInt8]) -> (image: CIImage?, frames: Int) {
            let long = LongExposure()
            var result: CIImage?
            var used = 0
            long.start(seconds: 3600, style: style, handheld: false) { image, n in
                result = image
                used = n
            }
            for i in 0..<count {
                autoreleasepool {
                    if let frame = makeFrame(codes(i)) { long.add(frame) }
                }
            }
            long.stop()
            return (result, used)
        }
        /// Luz linear do resultado (sem conversão de cor: o espaço de trabalho do app é linear P3)
        func readLinear(_ image: CIImage) -> [Float] {
            var px = [Float](repeating: 0, count: w * h * 4)
            Developer.context.render(image, toBitmap: &px, rowBytes: w * 16, bounds: CGRect(x: 0, y: 0, width: w, height: h),
                                     format: .RGBAf, colorSpace: nil)
            return px
        }
        func row(_ px: [Float]) -> [Double] {
            (0..<w).map { x in Double(px[((h / 2) * w + x) * 4 + 1]) }
        }

        // Rampa clara (0,55 → 0,95 na tela) com pontilhado no tempo: a média exata dos códigos é uma rampa lisa
        func rampCodes(_ i: Int) -> [UInt8] {
            let d = (Double(i + 1) * 0.6180339887498949).truncatingRemainder(dividingBy: 1)
            let line: [UInt8] = (0..<w).map { x in
                let v = 0.55 + 0.40 * Double(x) / Double(w - 1)
                return UInt8(min(255, Int((v * 255 + d).rounded(.down))))
            }
            var all = [UInt8](repeating: 0, count: w * h)
            for y in 0..<h { for x in 0..<w { all[y * w + x] = line[x] } }
            return all
        }
        func rampLine(_ i: Int) -> [Int] {
            let all = rampCodes(i)
            return (0..<w).map { Int(all[$0]) }
        }

        // Controle da medida: 1 quadro passa igual (se não, a medida está errada, não o app)
        if let img = accumulate(.silk, 1, rampCodes).image {
            let got = row(readLinear(img)), line = rampLine(0)
            let err = (0..<w).map { abs(enc(got[$0]) - Double(line[$0]) / 255) * 255 }.max() ?? 0
            dlog(String(format: "LONGA controle (1 quadro): erro máximo %.2f códigos", err))
        } else {
            dlog("❌ LONGA controle: sem saída")
        }

        let silkCount = 240
        let lines = (0..<silkCount).map(rampLine)
        let silk = accumulate(.silk, silkCount, rampCodes)
        if let img = silk.image {
            let got = row(readLinear(img))
            var worst = 0.0
            var lo = 1.0, hi = 0.0
            for x in 0..<w {
                let exact = enc(lines.reduce(0.0) { $0 + lin(Double($1[x]) / 255) } / Double(silkCount))
                worst = max(worst, abs(enc(got[x]) - exact) * 255)
                lo = min(lo, exact)
                hi = max(hi, exact)
            }
            let levels = Set(got.map { Int((enc($0) * 1023).rounded()) }).count
            dlog(String(format: "LONGA seda rampa (%d de %d quadros): erro máximo %.2f códigos · níveis %d em %.0f códigos",
                        silk.frames, silkCount, worst, levels, (hi - lo) * 255))
            if let out = image(Developer.developVideoImage(img, options: options())) { savePNG(out, "longa/seda_rampa_revelada") }
        } else {
            dlog("❌ LONGA seda rampa: sem saída")
        }

        let trailCount = 60
        let trails = accumulate(.trails, trailCount, rampCodes)
        if let img = trails.image {
            let got = row(readLinear(img))
            var worst = 0.0
            for x in 0..<w {
                let exact = Double((0..<trailCount).map { lines[$0][x] }.max() ?? 0) / 255
                worst = max(worst, abs(enc(got[x]) - exact) * 255)
            }
            dlog(String(format: "LONGA rastros rampa (%d de %d quadros): erro máximo %.2f códigos", trails.frames, trailCount, worst))
        } else {
            dlog("❌ LONGA rastros rampa: sem saída")
        }

        // Escuro só com ruído: preto 12, σ 2 códigos (gaussiano, sorteio fixo)
        var state: UInt64 = 0x10_6A_0001
        func uniform() -> Double {
            state &+= 0x9E3779B97F4A7C15
            var z = state
            z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
            z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
            z ^= z >> 31
            return Double(z >> 11) / Double(UInt64(1) << 53)
        }
        let darkCount = 60
        let dark: [[UInt8]] = (0..<darkCount).map { _ in
            (0..<(w * h)).map { _ in
                let g = (-2 * log(max(uniform(), 1e-12))).squareRoot() * cos(2 * Double.pi * uniform())
                return UInt8(min(255, max(0, Int((12 + 2 * g).rounded()))))
            }
        }
        let first = dark[0].map { Double($0) / 255 }
        let mean0 = first.reduce(0, +) / Double(first.count)
        let sigma0 = (first.reduce(0) { $0 + ($1 - mean0) * ($1 - mean0) } / Double(first.count)).squareRoot()
        for style in [LongExposure.Style.trails, .silk] {
            let label = style == .trails ? "rastros" : "seda"
            let run = accumulate(style, darkCount) { dark[$0] }
            guard let img = run.image else {
                dlog("❌ LONGA \(label) escuro: sem saída")
                continue
            }
            let px = readLinear(img)
            var sum = 0.0
            for k in 0..<(w * h) { sum += enc(Double(px[k * 4 + 1])) }
            let mean = sum / Double(w * h)
            dlog(String(format: "LONGA %@ escuro (%d de %d quadros): preto sobe %.2f σ (média %.4f → %.4f, σ de 1 quadro %.4f)",
                        label, run.frames, darkCount, (mean - mean0) / max(sigma0, 1e-9), mean0, mean, sigma0))
            if style == .trails, let out = image(Developer.developVideoImage(img, options: options())) {
                savePNG(out, "longa/rastros_escuro_revelada")
            }
        }
    }

    // MARK: - 3. PANORAMA

    /// PANORAMA pelo `Developer.panorama` (o mesmo do app): 4 quadros em pé tirados de uma cena cilíndrica conhecida
    /// (projeção de verdade, não recortes planos), com o giroscópio errando um pouco (0,6–1,2°, o Vision tem que
    /// acertar). Comparado com a mesma cena revelada pelo mesmo caminho (developVideoImage): o placar quer as emendas
    /// tão boas quanto o miolo dos quadros e nenhum salto de exposição nelas.
    func testP03Panorama() {
        guard let url = firstRaw(), let pano = scene(url, width: 1500, height: 900) else { return }
        let pw = 1500, ph = 900
        var panoPx = [Float](repeating: 0, count: pw * ph * 4)
        Developer.context.render(pano, toBitmap: &panoPx, rowBytes: pw * 16, bounds: CGRect(x: 0, y: 0, width: pw, height: ph),
                                 format: .RGBAf, colorSpace: nil)
        // Sem nada estourado (o quadro HEIF corta em 1 e a régua não: o corte viraria "salto de exposição" falso)
        for k in 0..<(pw * ph) {
            for c in 0..<3 { panoPx[k * 4 + c] = min(max(panoPx[k * 4 + c] * 0.7, 0), 0.95) }
            panoPx[k * 4 + 3] = 1
        }
        let fw = 600, fh = 800
        let fov = 1.0
        let f = Double(fw) / 2 / tan(fov / 2)
        let thetas: [Double] = [0, 0.42, 0.84, 1.26]
        let yawError: [Double] = [0, 0.010, -0.006, 0.012]
        let x0 = 380.0, yc = Double(ph) / 2
        func sample(_ px: Double, _ py: Double, _ c: Int) -> Float {
            let x = min(max(px, 0), Double(pw - 1)), y = min(max(py, 0), Double(ph - 1))
            let ix = min(Int(x), pw - 2), iy = min(Int(y), ph - 2)
            let fx = Float(x - Double(ix)), fy = Float(y - Double(iy))
            let i00 = (iy * pw + ix) * 4 + c
            let a = panoPx[i00], b = panoPx[i00 + 4], c0 = panoPx[i00 + pw * 4], d = panoPx[i00 + pw * 4 + 4]
            return (a * (1 - fx) + b * fx) * (1 - fy) + (c0 * (1 - fx) + d * fx) * fy
        }
        var frames: [PanoramaCapture.Frame] = []
        for (i, theta) in thetas.enumerated() {
            var px = [Float](repeating: 1, count: fw * fh * 4)
            for r in 0..<fh {
                let v = Double(r) + 0.5 - Double(fh) / 2
                for c in 0..<fw {
                    let u = Double(c) + 0.5 - Double(fw) / 2
                    let bigX = x0 + f * (theta + atan(u / f))
                    let bigY = yc + v * f / (u * u + f * f).squareRoot()
                    let o = (r * fw + c) * 4
                    for ch in 0..<3 { px[o + ch] = sample(bigX - 0.5, bigY - 0.5, ch) }
                }
            }
            let img = CIImage(bitmapData: px.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: fw * 16,
                              size: CGSize(width: fw, height: fh), format: .RGBAf, colorSpace: nil)
            // Como o app guarda cada quadro do giro: HEIF de 8 bits
            guard let data = Developer.context.heifRepresentation(of: img, format: .RGBA8, colorSpace: Developer.displayP3, options: [:]) else {
                dlog("❌ PANORAMA: quadro \(i) não virou HEIF")
                return
            }
            frames.append(PanoramaCapture.Frame(data: data, yaw: theta + yawError[i]))
        }
        var o = options()
        o.zoom = 1
        let t0 = CFAbsoluteTimeGetCurrent()
        guard let out = image(Developer.panorama(frames, fov: fov, options: o)) else {
            dlog("❌ PANORAMA: sem saída")
            return
        }
        dlog("PANORAMA: emendado em \(Diagnostics.ms(since: t0)) · \(Int(out.extent.width))×\(Int(out.extent.height))")
        // O mesmo recorte que o app faz, com as posições certas (o placar ainda procura ±8 px)
        let W = Double(fw), H = Double(fh)
        let positions = thetas.map { f * $0 }
        let curve = H / 2 * (1 - cos(fov / 2))
        let empty = max(0, W / 2 - f * fov / 2) + 2
        let left = (positions.min() ?? 0) + empty, right = (positions.max() ?? 0) + W - empty
        let rect = CGRect(x: left, y: curve, width: right - left, height: max(H - 2 * curve, H * 0.5)).integral
        let truthFull = CIImage(bitmapData: panoPx.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: pw * 16,
                                size: CGSize(width: pw, height: ph), format: .RGBAf, colorSpace: nil)
        let truthRect = rect.offsetBy(dx: CGFloat(x0 - W / 2), dy: CGFloat(yc - H / 2))
        let truthCrop = truthFull.cropped(to: truthRect).transformed(by: CGAffineTransform(translationX: -truthRect.minX, y: -truthRect.minY))
        var to = o
        to.originalAspect = true
        guard let truth = image(Developer.developVideoImage(truthCrop, options: to)) else { return }
        savePNG(out, "panorama/emendado")
        savePNG(truth, "panorama/verdade")
        // Onde ficam as emendas (a mistura vai de 30% a 70% da parte repetida) e o miolo de um quadro só, em x da saída
        let ox = Double(rect.minX)
        var zones: [(Double, Double)] = []
        for i in 1..<positions.count {
            let start = positions[i], end = positions[i - 1] + W
            zones.append((start + (end - start) * 0.3 - ox, start + (end - start) * 0.7 - ox))
        }
        var cores: [(Double, Double)] = []
        var cursor = 12.0
        for z in zones {
            if z.0 - 8 - cursor > 20 { cores.append((cursor, z.0 - 8)) }
            cursor = z.1 + 8
        }
        if Double(rect.width) - 12 - cursor > 20 { cores.append((cursor, Double(rect.width) - 12)) }
        let text = { (r: [(Double, Double)]) in r.map { String(format: "%.0f-%.0f", $0.0, $0.1) }.joined(separator: " ") }
        dlog("PANORAMA: emendas \(text(zones)) · miolos \(text(cores))")
    }

    // MARK: - 4. ESTRELAS

    /// ESTRELAS (o modo: média com corte dos pontos que aparecem em poucas fotos, `removeOutliers`): céu sintético com
    /// 170 estrelas (gaussianas de 1,2 px), chão escuro parado e 3 pixels quentes fixos no sensor. Nas 16 fotos o céu
    /// gira (5 px nos cantos) e deriva 1,7 px. Comparado com as mesmas 16 fotos sem o céu andar (o pico de uma foto):
    /// o placar quer o pico das estrelas ≥ 80% (sem rastro apagando), a largura ≤ 1,5× e os pixels quentes fora
    /// (≤ 10% do excesso numa foto só).
    func testP04Estrelas() {
        let w = 1024, h = 768, n = 16
        let e = CGRect(x: 0, y: 0, width: w, height: h)
        let cx = Double(w) / 2, cy = Double(h) / 2
        let totalAngle = 5.0 / (cx * cx + cy * cy).squareRoot()
        let drift = (x: 1.5, y: 0.8)
        // Pixels quentes em coordenadas do Core Image (origem embaixo), longe do chão
        let hot: [(x: Int, y: Int)] = [(212, 530), (640, 300), (871, 610)]
        var state: UInt64 = 0xA57E_0001
        func uniform() -> Double {
            state &+= 0x9E3779B97F4A7C15
            var z = state
            z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
            z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
            z ^= z >> 31
            return Double(z >> 11) / Double(UInt64(1) << 53)
        }
        var stars: [(x: Double, y: Double, amp: Double)] = []
        while stars.count < 170 {
            let x = 24 + uniform() * Double(w - 48), y = 24 + uniform() * Double(h - 48)
            // Nem perto de um pixel quente (nos dois sentidos da linha do bitmap)
            let nearHot = hot.contains { p in
                abs(x - Double(p.x)) < 14 && min(abs(y - Double(p.y)), abs(y - Double(h - 1 - p.y))) < 14
            }
            if nearHot { continue }
            stars.append((x: x, y: y, amp: 0.06 + 0.3 * uniform() * uniform()))
        }
        let groundColor = CIColor(red: 0.002, green: 0.002, blue: 0.0025, colorSpace: Developer.linearP3)!
        var ground = CIImage(color: groundColor).cropped(to: CGRect(x: 0, y: 0, width: w, height: 110))
        for (x, width, height) in [(80, 40, 170), (300, 25, 150), (520, 60, 185), (760, 30, 160), (930, 45, 175)] {
            ground = CIImage(color: groundColor).cropped(to: CGRect(x: x, y: 0, width: width, height: height)).composited(over: ground)
        }
        var hotImage = CIImage.empty()
        for p in hot {
            let dot = CIImage(color: CIColor(red: 0.5, green: 0.5, blue: 0.5, colorSpace: Developer.linearP3)!)
                .cropped(to: CGRect(x: p.x, y: p.y, width: 1, height: 1))
            hotImage = dot.composited(over: hotImage)
        }
        let props = isoProps(3200)
        func frame(_ i: Int, moving: Bool) -> CIImage {
            var px = [Float](repeating: 1, count: w * h * 4)
            var seed = UInt64(i + 1) << 40 | 0x5747
            for k in 0..<(w * h) {
                let sky = Float(0.007 + 0.003 * Double(k / w) / Double(h))
                for c in 0..<3 {
                    seed &+= 0x9E3779B97F4A7C15
                    var z = seed
                    z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
                    z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
                    z ^= z >> 31
                    px[k * 4 + c] = sky + (Float(z >> 40) / Float(1 << 24) - 0.5) * 0.006
                }
            }
            let t = moving ? Double(i) / Double(n - 1) : 0
            let a = totalAngle * t, ca = cos(a), sa = sin(a)
            let dx = drift.x * t, dy = drift.y * t
            let sigma = 1.2
            for s in stars {
                let rx = s.x - cx, ry = s.y - cy
                let x = cx + ca * rx - sa * ry + dx, y = cy + sa * rx + ca * ry + dy
                let xa = max(0, Int(x) - 5), xb = min(w - 1, Int(x) + 5)
                let ya = max(0, Int(y) - 5), yb = min(h - 1, Int(y) + 5)
                guard xa <= xb, ya <= yb else { continue }
                for yy in ya...yb {
                    for xx in xa...xb {
                        let ddx = Double(xx) + 0.5 - x, ddy = Double(yy) + 0.5 - y
                        let g = Float(s.amp * exp(-(ddx * ddx + ddy * ddy) / (2 * sigma * sigma)))
                        let o = (yy * w + xx) * 4
                        px[o] += g
                        px[o + 1] += g * 0.97
                        px[o + 2] += g * 0.92
                    }
                }
            }
            var img = CIImage(bitmapData: px.withUnsafeBufferPointer { Data(buffer: $0) }, bytesPerRow: w * 16,
                              size: CGSize(width: w, height: h), format: .RGBAf, colorSpace: nil)
            img = Developer.add(img, hotImage).cropped(to: e)
            img = ground.composited(over: img).cropped(to: e)
            return Developer.materialize(img, extent: e).settingProperties(props)
        }
        let o = options()
        func run(_ frames: [CIImage]) -> CIImage? {
            let captured = feed(frames)
            defer { Developer.decodeOverride = nil }
            // Como o modo ESTRELAS chama
            return image(Developer.stack(captured, kind: .average, removeOutliers: true, robust: false, starPoints: 0, options: o))
        }
        let still = (0..<n).map { frame($0, moving: false) }
        if let single = image(Developer.finish(still[0], options: o)) { savePNG(single, "estrelas/uma_foto") }
        let t0 = CFAbsoluteTimeGetCurrent()
        if let out = run(still) { savePNG(out, "estrelas/parado") }
        let moving = (0..<n).map { frame($0, moving: true) }
        if let out = run(moving) {
            savePNG(out, "estrelas/girando")
        } else {
            dlog("❌ ESTRELAS: sem saída")
        }
        let hotText = hot.map { "\($0.x),\(h - 1 - $0.y)" }.joined(separator: " ")
        dlog("ESTRELAS: pixels quentes \(hotText) · \(stars.count) estrelas · giro de 5 px nos cantos · \(Diagnostics.ms(since: t0))")
    }

    // MARK: - 5. MÉDIA

    /// MÉDIA (média simples, sem anti-fantasma): 8 fotos com deslocamentos de fração de pixel (sensor com soma 2×2,
    /// como no teste do SUPER ZOOM). Sem ruído mede a nitidez contra a foto ideal (≥ 0,9: o encaixe bilinear amolece);
    /// com ruído, o ruído tem que cair perto de 1/√8 do de uma foto.
    func testP05Media() {
        guard let url = firstRaw(), let truth = scene(url, width: 1440, height: 1080) else { return }
        let shifts: [(CGFloat, CGFloat)] = [(0, 0), (0.35, 0.2), (-0.4, 0.3), (0.25, -0.45), (-0.3, -0.25), (0.45, 0.4),
                                            (-0.2, 0.5), (0.15, -0.35)]
        let props = isoProps(400)
        var clean: [CIImage] = [], noisy: [CIImage] = []
        for (i, (dx, dy)) in shifts.enumerated() {
            // Deslocamento em pixels da foto = 2× em pixels da cena
            let low = sensor(truth, dx: dx * 2, dy: dy * 2)
            let le = low.extent
            clean.append(Developer.materialize(low, extent: le).settingProperties(props))
            let withNoise = Developer.add(low, sensorNoise(le, seed: 700 + i, amplitude: 0.03)).cropped(to: le)
            noisy.append(Developer.materialize(withNoise, extent: le).settingProperties(props))
        }
        let o = options()
        // Régua e foto única pela mesma revelação que a MÉDIA usa no fim (finish)
        if let ideal = image(Developer.finish(clean[0], options: o)) { savePNG(ideal, "media/ideal") }
        if let one = image(Developer.finish(noisy[0], options: o)) { savePNG(one, "media/uma") }
        for (frames, label) in [(clean, "nitidez"), (noisy, "ruido")] {
            let captured = feed(frames)
            let t0 = CFAbsoluteTimeGetCurrent()
            let out = image(Developer.stack(captured, kind: .average, removeOutliers: false, robust: false, starPoints: 0, options: o))
            Developer.decodeOverride = nil
            if let out {
                savePNG(out, "media/\(label)")
                dlog("MÉDIA \(label): \(frames.count) fotos em \(Diagnostics.ms(since: t0))")
            } else {
                dlog("❌ MÉDIA \(label): sem saída")
            }
        }
    }

    // MARK: - 6. FOCO EMPILHADO

    /// FOCO EMPILHADO: duas fotos, cada uma nítida numa metade (a outra metade borrada, σ 3 px). O resultado tem que
    /// ficar nítido nas duas metades (≥ 0,85 da cena nítida), sem halo na divisa; e com a 2ª foto +0,3 EV mais clara
    /// (o FOCO não trava a exposição) a divisa não pode virar um degrau visível.
    func testP06Foco() {
        guard let url = firstRaw(), let sharp = scene(url, width: 1024, height: 768) else { return }
        let e = sharp.extent
        let props = isoProps(100)
        let blurred = Developer.materialize(sharp.clampedToExtent().applyingGaussianBlur(sigma: 3).cropped(to: e), extent: e)
        let leftHalf = CGRect(x: 0, y: 0, width: e.width / 2, height: e.height)
        let a = Developer.materialize(sharp.cropped(to: leftHalf).composited(over: blurred).cropped(to: e), extent: e).settingProperties(props)
        let b = Developer.materialize(blurred.cropped(to: leftHalf).composited(over: sharp).cropped(to: e), extent: e).settingProperties(props)
        let brighter = Developer.materialize(Developer.scaled(b, by: Float(pow(2.0, 0.3))).cropped(to: e), extent: e).settingProperties(props)
        let o = options()
        if let ideal = image(Developer.finish(sharp.settingProperties(props), options: o)) { savePNG(ideal, "foco/nitida") }
        if let soft = image(Developer.finish(blurred.settingProperties(props), options: o)) { savePNG(soft, "foco/borrada") }
        for (pair, label) in [([a, b], "junta"), ([a, brighter], "junta_exposicao")] {
            let captured = feed(pair)
            // Como o modo FOCO EMPILHADO chama
            let out = image(Developer.stack(captured, kind: .focus, removeOutliers: false, robust: false, starPoints: 0, options: o))
            Developer.decodeOverride = nil
            if let out { savePNG(out, "foco/\(label)") } else { dlog("❌ FOCO \(label): sem saída") }
        }
        dlog("FOCO: divisa no meio (x = 50%), 2ª foto +0,3 EV na junta_exposicao")
    }

    // MARK: - 7. FOTO 3× igual à FOTO

    /// A mesma cena sem ruído pela FOTO de uma foto (develop: tons locais, cor pela luz, nitidez) e pela FOTO 3×
    /// (fuse de 4 fotos idênticas): brilho médio, meio (p50), saturação e contraste local têm que bater. Pega a FOTO 3×
    /// pulando a finalização da FOTO (a foto juntada saía com outra cara).
    func testP07FotoConsistencia() {
        for url in raws() {
            let name = url.deletingPathExtension().lastPathComponent
            guard let s = scene(url, width: 1600, height: 1200) else { continue }
            let shot = s.settingProperties(isoProps(200))
            let captured = feed([shot, shot, shot, shot])
            defer { Developer.decodeOverride = nil }
            let o = options()
            guard let single = image(Developer.develop(captured[0], options: o)) else {
                dlog("❌ FOTO consistência \(name): foto única sem saída")
                continue
            }
            let t0 = CFAbsoluteTimeGetCurrent()
            guard let fused = image(Developer.fuse(captured, options: o)) else {
                dlog("❌ FOTO consistência \(name): FOTO 3× sem saída")
                continue
            }
            savePNG(single, "foto_consistencia/\(name)_uma")
            savePNG(fused, "foto_consistencia/\(name)_juntada")
            dlog("FOTO consistência \(name): FOTO 3× de 4 fotos idênticas em \(Diagnostics.ms(since: t0))")
        }
    }

    // MARK: - 8. NOITE com uma foto que não é da cena

    /// NOITE (8 fotos escuras, ruído de ISO 3200) em que a 6ª foto não é da cena: puro ruído (lente tampada, quadro
    /// corrompido) ou a cena de ponta-cabeça (o alinhamento não acha nada). A foto tem que ficar de fora: o resultado
    /// igual ao das outras 7 (placar: PSNR ≥ 35 dB). Hoje a foto de ruído é a "mais nítida" e vira a referência.
    func testP08NoiteFotoRuim() {
        guard let url = firstRaw(), let base = scene(url, width: 1024, height: 768) else { return }
        let e = base.extent
        let props = isoProps(3200)
        let dark = Developer.materialize(Developer.scaled(base, by: 1.0 / 16).cropped(to: e), extent: e)
        var good: [CIImage] = []
        for i in 0..<8 {
            let moved = shifted(dark, dx: CGFloat(i % 3) * 0.7, dy: CGFloat(i % 2) * 0.6)
            let noisy = Developer.add(moved, sensorNoise(e, seed: 900 + i)).cropped(to: e)
            good.append(Developer.materialize(noisy, extent: e).settingProperties(props))
        }
        let bad = 5
        let gray = CIImage(color: CIColor(red: 0.012, green: 0.012, blue: 0.012, colorSpace: Developer.linearP3)!).cropped(to: e)
        let noiseFrame = Developer.materialize(Developer.add(gray, sensorNoise(e, seed: 990, amplitude: 0.08)).cropped(to: e), extent: e)
            .settingProperties(props)
        let upsideDown = good[bad].transformed(by: CGAffineTransform(a: -1, b: 0, c: 0, d: -1, tx: e.width, ty: e.height))
        let otherScene = Developer.materialize(upsideDown.cropped(to: e), extent: e).settingProperties(props)
        let o = options()
        var withoutBad = good
        withoutBad.remove(at: bad)
        var noiseSet = good
        noiseSet[bad] = noiseFrame
        var otherSet = good
        otherSet[bad] = otherScene
        for (frames, label) in [(withoutBad, "sem"), (noiseSet, "ruido"), (otherSet, "outra_cena")] {
            let captured = feed(frames)
            let t0 = CFAbsoluteTimeGetCurrent()
            let out = image(Developer.stack(captured, kind: .average, robust: true, starPoints: 0, options: o))
            Developer.decodeOverride = nil
            if let out {
                savePNG(out, "noite_ruim/\(label)")
                dlog("NOITE foto ruim \(label): \(frames.count) fotos em \(Diagnostics.ms(since: t0))")
            } else {
                dlog("❌ NOITE foto ruim \(label): sem saída")
            }
        }
    }

    // MARK: - 9. Fantasma de movimento (NOITE, FOTO 3×, SUPER ZOOM)

    private enum GhostMode: String {
        case noite, foto3x, superzoom
    }

    /// Os 8 lugares do vulto (a foto i usa o lugar i % 8), em fração da cena, origem embaixo (Core Image).
    /// No céu o vulto fica na faixa clara de cima.
    private func ghostSpots(sky: Bool) -> [CGRect] {
        (0..<8).map { k in CGRect(x: 0.08 + 0.1 * CGFloat(k), y: sky ? 0.65 : 0.35, width: 0.05, height: 0.30) }
    }

    /// Para o placar: x, y, largura, altura em fração, origem EM CIMA à esquerda (como o PNG).
    private func spotsText(_ spots: [CGRect]) -> String {
        spots.map { String(format: "%.3f,%.3f,%.3f,%.3f", Double($0.minX), Double(1 - $0.maxY), Double($0.width), Double($0.height)) }
            .joined(separator: ";")
    }

    private func ghostRun(_ mode: GhostMode, frames: [CIImage], options o: DevelopOptions) -> CIImage? {
        let captured = feed(frames)
        defer { Developer.decodeOverride = nil }
        switch mode {
        case .noite: return image(Developer.stack(captured, kind: .average, robust: true, starPoints: 0, options: o))
        case .foto3x: return image(Developer.fuse(captured, options: o))
        case .superzoom: return image(Developer.superResolution(captured, options: o, keep: 10))
        }
    }

    /// Um "vulto" do tamanho de uma pessoa (5% × 30% da cena) andando: em cada foto num lugar diferente (8 lugares; no
    /// SUPER ZOOM, 24 fotos, cada lugar em 3). Claro, escuro, e escuro na frente de um céu claro (canal > 0,85: o
    /// anti-fantasma do app desligava acima disso). Cada versão contra a mesma cena sem vulto (mesmo ruído, mesmos
    /// deslocamentos, mesma revelação): no lugar da foto de referência o vulto aparece inteiro; nos outros 7 lugares o
    /// que sobrar é fantasma (placar: ≤ 5% do contraste do vulto). No céu a revelação desconta 1,5–2,5 EV (como no
    /// ETTR), para o céu não estourar na tela e esconder o fantasma.
    func testP09Fantasmas() {
        guard let url = firstRaw(), let base = scene(url, width: 1024, height: 768),
              let truthSR = scene(url, width: 1536, height: 1152) else { return }
        let skyColor = CIColor(red: 0.62, green: 0.80, blue: 0.97, colorSpace: Developer.linearP3)!
        var srShifts: [(CGFloat, CGFloat)] = [(0, 0), (1.3, -0.7), (-2.1, 1.6), (0.4, 2.7), (-1.6, -2.4),
                                              (2.6, 0.9), (-0.8, -1.2), (1.9, 2.2), (-2.7, 0.3), (0.7, -2.9)]
        for k in 0..<14 {
            let a = Double(k) * 2.399963, r = 0.6 + 2.3 * (Double(k) + 0.5) / 14
            srShifts.append((CGFloat(r * cos(a)), CGFloat(r * sin(a))))
        }
        let photoShifts: [(CGFloat, CGFloat)] = [(0, 0), (0.8, -0.5), (-1.3, 0.9), (1.7, 1.2), (-0.6, -1.8), (2.2, -0.3),
                                                 (-1.9, 1.6), (0.4, 2.1)]
        // Tremidinho do tripé da NOITE (como no teste da pilha)
        let nightShifts: [(CGFloat, CGFloat)] = [(0, 0), (0.7, 0.6), (1.4, 0), (0, 0.6), (0.7, 0), (1.4, 0.6), (0, 0), (0.7, 0.6)]
        for mode in [GhostMode.noite, .foto3x, .superzoom] {
            // Luz das fotos de cada modo: NOITE 1/16 (ISO 3200), FOTO 3× ¼ (interior, ISO 800), SUPER ZOOM cheia
            let gain: Float = mode == .noite ? 1.0 / 16 : (mode == .foto3x ? 0.25 : 1)
            let src = mode == .superzoom ? truthSR : base
            let e = src.extent
            let lit = Developer.materialize(Developer.scaled(src, by: gain).cropped(to: e), extent: e)
            let count = mode == .superzoom ? 24 : 8
            var shifts = nightShifts
            if mode == .foto3x { shifts = photoShifts }
            if mode == .superzoom { shifts = srShifts }
            let amplitude: Float = mode == .noite ? 0.012 : 0.02
            let props = isoProps(mode == .noite ? 3200 : (mode == .foto3x ? 800 : 400))
            let seedBase = mode == .noite ? 1100 : (mode == .foto3x ? 1200 : 1300)
            let g = CGFloat(gain)
            let brightObject = CIColor(red: 0.7 * g, green: 0.66 * g, blue: 0.6 * g, colorSpace: Developer.linearP3)!
            let darkObject = CIColor(red: 0.004 * g, green: 0.004 * g, blue: 0.005 * g, colorSpace: Developer.linearP3)!

            func frames(object: CIColor?, sky: Bool) -> [CIImage] {
                let spots = ghostSpots(sky: sky)
                var background = lit
                if sky {
                    background = CIImage(color: skyColor).cropped(to: CGRect(x: 0, y: e.height * 0.6, width: e.width, height: e.height * 0.4))
                        .composited(over: lit).cropped(to: e)
                }
                return (0..<count).map { i -> CIImage in
                    var shot = background
                    if let object {
                        let r = spots[i % 8]
                        let rect = CGRect(x: r.minX * e.width, y: r.minY * e.height, width: r.width * e.width, height: r.height * e.height).integral
                        shot = CIImage(color: object).cropped(to: rect).composited(over: background).cropped(to: e)
                    }
                    let (dx, dy) = shifts[i % shifts.count]
                    let moved = mode == .superzoom ? sensor(shot, dx: dx, dy: dy) : shifted(shot, dx: dx, dy: dy)
                    let fe = moved.extent
                    let noisy = Developer.add(moved, sensorNoise(fe, seed: seedBase + i, amplitude: amplitude)).cropped(to: fe)
                    return Developer.materialize(noisy, extent: fe).settingProperties(props)
                }
            }

            let runs: [(String, CIColor?, Bool)] = [("limpo", nil, false), ("claro", brightObject, false), ("escuro", darkObject, false),
                                                    ("limpo_ceu", nil, true), ("ceu", darkObject, true)]
            for (label, object, sky) in runs {
                var o = options()
                if sky { o.exposureOffset = mode == .noite ? -2.5 : -1.5 }
                let t0 = CFAbsoluteTimeGetCurrent()
                guard let out = ghostRun(mode, frames: frames(object: object, sky: sky), options: o) else {
                    dlog("❌ FANTASMA \(mode.rawValue) \(label): sem saída")
                    continue
                }
                savePNG(out, "fantasma/\(mode.rawValue)_\(label)")
                if object != nil { dlog("FANTASMA \(mode.rawValue) \(label): vulto em \(spotsText(ghostSpots(sky: sky)))") }
                dlog("FANTASMA \(mode.rawValue) \(label): \(count) fotos em \(Diagnostics.ms(since: t0))")
            }
        }
    }

    // MARK: - 10. Saída grande (LUA / SUPER RES de 48 MP)

    /// LUA como o app chama (`superResolution(sharpen: 0.9)`, 5 fotos) com fotos de 12 MP: a saída é 2× = 48 MP. Tem que
    /// terminar, usar as 5 fotos (a conta de memória cortava para 2) e caber na memória (pico medido pelo
    /// phys_footprint; placar: acréscimo ≤ 2500 MB).
    func testP10LuaGrande() {
        guard let url = firstRaw(), let truth = scene(url, width: 3000, height: 4000, rawScale: 1) else { return }
        let e = truth.extent
        let props = isoProps(100)
        let shifts: [(CGFloat, CGFloat)] = [(0, 0), (0.6, -0.4), (-0.5, 0.7), (0.3, 0.5), (-0.7, -0.3)]
        let frames = shifts.map { Developer.materialize(shifted(truth, dx: $0.0, dy: $0.1), extent: e).settingProperties(props) }
        let captured = feed(frames)
        defer { Developer.decodeOverride = nil }
        let before = LabMemory.footprint()
        dlog(String(format: "LUA 48 MP: início · %d fotos de %.0f×%.0f · memória %.0f MB", frames.count, Double(e.width), Double(e.height),
                    Double(before) / 1_048_576))
        let meter = LabMemoryPeak()
        meter.start()
        let t0 = CFAbsoluteTimeGetCurrent()
        let out = Developer.superResolution(captured, options: options(), sharpen: 0.9)
        let elapsed = Diagnostics.ms(since: t0)
        let peak = meter.stop()
        var size = "sem saída"
        if let heic = out?.heic, let img = CIImage(data: heic) {
            let ie = img.extent
            size = String(format: "%.0f×%.0f (%.1f MP)", Double(ie.width), Double(ie.height), Double(ie.width * ie.height) / 1_000_000)
            let side = min(1024, ie.width, ie.height)
            savePNG(img.cropped(to: CGRect(x: (ie.midX - side / 2).rounded(), y: (ie.midY - side / 2).rounded(), width: side, height: side)),
                    "lua/centro_100pct")
        }
        let extra = peak > before ? peak - before : 0
        dlog(String(format: "LUA 48 MP: fim · saída %@ · %@ · memória pico %.0f MB (acréscimo %.0f MB)", size, elapsed,
                    Double(peak) / 1_048_576, Double(extra) / 1_048_576))
    }
}
