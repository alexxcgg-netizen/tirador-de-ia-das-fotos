import Foundation

/// Calibragem da revelação que o Claude manda pela ponte (calibragem.json no ramo revela-sync).
/// Muda tom, cor, NOITE, estrela e SUPER ZOOM sem precisar de versão nova; fica guardada entre aberturas.
/// Chaves com ponto, por exemplo {"tom.ombro": 1.2, "noite.alvo": -3.8}. {"padrao": true} volta tudo ao normal.
enum Calibration {
    private static let storeKey = "calibragemRemota"

    /// Tudo montado à parte e trocado de uma vez no fim: uma revelação em andamento não pega metade padrão, metade calibrada
    private struct Tunings {
        var tone = ToneTuning(), night = NightTuning(), star = StarTuning(), sr = Developer.SRTuning()
    }
    private typealias Setter = (inout Tunings, Double) -> Void
    /// Cada chave, com o que ela muda e o intervalo aceito (fora dele o valor é preso no limite).
    private static let fields: [(key: String, range: ClosedRange<Double>, set: Setter)] = [
        ("tom.curva", 0.6...1.6, { $0.tone.filmicGain = Float($1) }),
        ("tom.ombro", 0.9...1.5, { $0.tone.whiteScale = Float($1) }),
        ("tom.saturacao", 0.6...1.6, { $0.tone.saturation = Float($1) }),
        ("tom.sombras", 0...3, { $0.tone.shadowRatio = Float($1) }),
        ("tom.luzes", 0...2, { $0.tone.highlightRatio = Float($1) }),
        ("tom.puxaLuz", 0...1, { $0.tone.keyPull = Float($1) }),
        ("tom.corPelaLuz", 0...0.5, { $0.tone.keyedSaturation = Float($1) }),
        ("tom.ceu", 0...1.5, { $0.tone.highlightBoost = Float($1) }),
        ("tom.nevoa", 0...1.5, { $0.tone.toeScale = Float($1) }),
        ("tom.corDaLuz", 0...1, { $0.tone.hueKeep = Float($1) }),
        ("noite.alvo", -6...(-2.5), { $0.night.liftTarget = Float($1) }),
        ("noite.maximo", 0...4, { $0.night.liftMax = Float($1) }),
        ("noite.preto", 0...1.2, { $0.night.blackFactor = Float($1) }),
        ("noite.pretoMax", 0...0.12, { $0.night.blackCap = Float($1) }),
        ("noite.sombras", 0.5...1, { $0.night.shadowStrength = Float($1) }),
        ("estrela.comprimento", 0.2...3, { $0.star.length = Float($1) }),
        ("estrela.forca", 0...3, { $0.star.strength = Float($1) }),
        ("estrela.halo", 0...3, { $0.star.glow = Float($1) }),
        ("estrela.largura", 0.3...3, { $0.star.width = Float($1) }),
        ("estrela.sol", 0...80, { $0.star.dayBoost = Float($1) }),
        ("zoom.nucleo", 0.3...1.2, { $0.sr.splatSigma = $1 }),
        ("zoom.desconv", 0...1, { $0.sr.deconvScale = $1 }),
        ("zoom.passos", 0...8, { $0.sr.deconvIterations = Int($1.rounded()) }),
    ]

    /// Aplica (e guarda) o que veio. Devolve as chaves que valeram.
    @discardableResult
    static func apply(_ d: [String: Any], save: Bool = true) -> [String] {
        // Sempre parte do padrão: a calibragem é o arquivo inteiro, não somado à anterior
        var next = Tunings()
        var applied: [String] = []
        if (d["padrao"] as? Bool) != true {
            for field in fields {
                guard let number = (d[field.key] as? NSNumber)?.doubleValue, number.isFinite else { continue }
                field.set(&next, min(max(number, field.range.lowerBound), field.range.upperBound))
                applied.append(field.key)
            }
        }
        Developer.tuning = next.tone
        Developer.nightTuning = next.night
        Developer.starTuning = next.star
        Developer.srTuning = next.sr
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
