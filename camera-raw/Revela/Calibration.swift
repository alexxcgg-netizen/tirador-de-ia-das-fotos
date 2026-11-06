import Foundation

/// Calibragem da revelação que o Claude manda pela ponte (calibragem.json no ramo revela-sync).
/// Muda tom, cor, NOITE, estrela e SUPER ZOOM sem precisar de versão nova; fica guardada entre aberturas.
/// Chaves com ponto, por exemplo {"tom.ombro": 1.2, "noite.alvo": -3.8}. {"padrao": true} volta tudo ao normal.
enum Calibration {
    private static let storeKey = "calibragemRemota"

    private typealias Setter = (Double) -> Void
    /// Cada chave, com o que ela muda e o intervalo aceito (fora dele o valor é preso no limite).
    private static let fields: [(key: String, range: ClosedRange<Double>, set: Setter)] = [
        ("tom.curva", 0.6...1.6, { Developer.tuning.filmicGain = Float($0) }),
        ("tom.ombro", 0.9...1.5, { Developer.tuning.whiteScale = Float($0) }),
        ("tom.saturacao", 0.6...1.6, { Developer.tuning.saturation = Float($0) }),
        ("tom.sombras", 0...3, { Developer.tuning.shadowRatio = Float($0) }),
        ("tom.luzes", 0...2, { Developer.tuning.highlightRatio = Float($0) }),
        ("tom.puxaLuz", 0...1, { Developer.tuning.keyPull = Float($0) }),
        ("tom.corPelaLuz", 0...0.5, { Developer.tuning.keyedSaturation = Float($0) }),
        ("tom.ceu", 0...1.5, { Developer.tuning.highlightBoost = Float($0) }),
        ("tom.nevoa", 0...1.5, { Developer.tuning.toeScale = Float($0) }),
        ("tom.corDaLuz", 0...1, { Developer.tuning.hueKeep = Float($0) }),
        ("noite.alvo", -6...(-2.5), { Developer.nightTuning.liftTarget = Float($0) }),
        ("noite.maximo", 0...4, { Developer.nightTuning.liftMax = Float($0) }),
        ("noite.preto", 0...1.2, { Developer.nightTuning.blackFactor = Float($0) }),
        ("noite.pretoMax", 0...0.12, { Developer.nightTuning.blackCap = Float($0) }),
        ("noite.sombras", 0.5...1, { Developer.nightTuning.shadowStrength = Float($0) }),
        ("estrela.comprimento", 0.2...3, { Developer.starTuning.length = Float($0) }),
        ("estrela.forca", 0...3, { Developer.starTuning.strength = Float($0) }),
        ("estrela.halo", 0...3, { Developer.starTuning.glow = Float($0) }),
        ("estrela.largura", 0.3...3, { Developer.starTuning.width = Float($0) }),
        ("estrela.sol", 0...80, { Developer.starTuning.dayBoost = Float($0) }),
        ("zoom.nucleo", 0.3...1.2, { Developer.srTuning.splatSigma = $0 }),
        ("zoom.desconv", 0...1, { Developer.srTuning.deconvScale = $0 }),
        ("zoom.passos", 0...8, { Developer.srTuning.deconvIterations = Int($0.rounded()) }),
    ]

    /// Aplica (e guarda) o que veio. Devolve as chaves que valeram.
    @discardableResult
    static func apply(_ d: [String: Any], save: Bool = true) -> [String] {
        // Sempre parte do padrão: a calibragem é o arquivo inteiro, não somado à anterior
        Developer.tuning = ToneTuning()
        Developer.nightTuning = NightTuning()
        Developer.starTuning = StarTuning()
        Developer.srTuning = Developer.SRTuning()
        var applied: [String] = []
        if (d["padrao"] as? Bool) != true {
            for field in fields {
                guard let number = (d[field.key] as? NSNumber)?.doubleValue, number.isFinite else { continue }
                field.set(min(max(number, field.range.lowerBound), field.range.upperBound))
                applied.append(field.key)
            }
        }
        if save {
            let clean = d.filter { key, _ in key == "padrao" || fields.contains { $0.key == key } }
            if let data = try? JSONSerialization.data(withJSONObject: clean) { UserDefaults.standard.set(data, forKey: storeKey) }
        }
        return applied
    }

    /// A calibragem guardada (abertura do app).
    static func loadSaved() {
        guard let data = UserDefaults.standard.data(forKey: storeKey),
              let d = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] else { return }
        let applied = apply(d, save: false)
        if !applied.isEmpty { dlog("Calibragem do Claude em uso: \(applied.joined(separator: ", "))") }
    }

    /// Para o relatório: o que está diferente do padrão.
    static var summary: String {
        guard let data = UserDefaults.standard.data(forKey: storeKey),
              let d = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any], !d.isEmpty else {
            return "padrão (nenhuma calibragem remota)"
        }
        return d.sorted { $0.key < $1.key }.map { "\($0.key) = \($0.value)" }.joined(separator: ", ")
    }
}
