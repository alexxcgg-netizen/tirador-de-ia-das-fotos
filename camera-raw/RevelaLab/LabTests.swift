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

    private func save(_ image: CIImage, _ name: String, maxSide: CGFloat = 900) {
        let e = image.extent
        let s = min(1, maxSide / max(e.width, e.height))
        var small = image
        if s < 1 {
            small = image.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: s, kCIInputAspectRatioKey: 1])
        }
        small = small.cropped(to: small.extent.integral)
        let url = outDir.appendingPathComponent(name + ".jpg")
        try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        do {
            try Developer.context.writeJPEGRepresentation(of: small, to: url, colorSpace: Developer.displayP3,
                                                          options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.86])
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
            let noise = CIFilter(name: "CIRandomGenerator")!.outputImage!.cropped(to: e)
                .applyingFilter("CIColorMatrix", parameters: [
                    "inputRVector": CIVector(x: 0.012, y: 0, z: 0, w: 0), "inputGVector": CIVector(x: 0, y: 0.012, z: 0, w: 0),
                    "inputBVector": CIVector(x: 0, y: 0, z: 0.012, w: 0), "inputBiasVector": CIVector(x: -0.006, y: -0.006, z: -0.006, w: 0),
                ])
            var night = noise.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: dark]).cropped(to: e)
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
            for points in [0, 6] {
                let t0 = CFAbsoluteTimeGetCurrent()
                let finished = Developer.nightFinish(night, iso: 3200, frameCount: 12, starPoints: points)
                let out = Developer.developed(finished, options: o).0
                save(out, "noite/\(name)_1_noite_\(points)pontas")
                dlog("\(name) noite (\(points) pontas): \(Diagnostics.ms(since: t0))")
                if points == 6 {
                    let c = CGPoint(x: e.minX + e.width * 0.62, y: e.minY + e.height * 0.55)
                    save(out.cropped(to: CGRect(x: c.x - 300, y: c.y - 300, width: 600, height: 600)), "noite/\(name)_2_estrela_zoom", maxSide: 600)
                }
            }
        }
    }

    /// Calibragens do tom lado a lado (o app usa a padrão; as outras são para comparar).
    func test4Tuning() throws {
        let variants: [(String, ToneTuning)] = [
            ("a_antiga", ToneTuning(filmicGain: 0.8, toeScale: 1, offsetScale: 1, saturation: 1, shadowRatio: 1, highlightRatio: 1, keyPull: 0)),
            ("b_padrao", ToneTuning()),
            ("c_mais_clara", ToneTuning(filmicGain: 1.12, keyPull: 0.45)),
            ("d_mais_cor", ToneTuning(saturation: 1.22, shadowRatio: 2.0, highlightRatio: 0.3)),
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
}
