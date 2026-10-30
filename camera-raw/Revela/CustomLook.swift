import Foundation

/// Filme criado por quem usa: parte de um look pronto e mexe em cor, contraste, grão e luz.
struct CustomLook: Codable, Identifiable, Equatable {
    var id = UUID()
    var name = "Meu filme"
    /// Look de partida (rawValue de `Look`).
    var base = Look.portra.rawValue
    var exposure: Float = 0
    var contrast: Float = 1
    var saturation: Float = 1
    /// Quente (+) ou frio (−).
    var warmth: Float = 0
    /// Magenta (+) ou verde (−).
    var tint: Float = 0
    /// Preto lavado, como filme velho.
    var fade: Float = 0
    /// Cor nas sombras: azul-petróleo (−) ou quente (+).
    var shadowColor: Float = 0
    var grain: Float = 0.04
    var grainSize: Float = 1.4
    var vignette: Float = 0.12
    var halation: Float = 0.05
    var bloom: Float = 0
    var blackAndWhite = false

    var baseLook: Look { Look(rawValue: base) ?? .neutro }

    /// Novo filme começando pelo look escolhido, com o grão, a vinheta e o brilho dele.
    static func starting(from look: Look) -> CustomLook {
        let p = look.params
        var c = CustomLook()
        c.name = "Meu \(look.rawValue)"
        c.base = look.rawValue
        c.grain = p.grain
        c.grainSize = p.grainSize
        c.vignette = p.vignette
        c.halation = p.halation
        c.bloom = p.bloom
        c.blackAndWhite = p.mono > 0.5
        return c
    }

    var params: LookParams {
        var p = baseLook.params
        p.exposure += exposure
        p.contrast *= contrast
        p.saturation *= saturation
        p.slope *= SIMD3<Float>(1 + warmth * 0.12, 1 - tint * 0.08, 1 - warmth * 0.12)
        p.offset += SIMD3<Float>(repeating: fade * 0.05)
        let warmShadow = SIMD3<Float>(0.012, 0.006, -0.008), coolShadow = SIMD3<Float>(-0.008, 0.004, 0.014)
        p.shadowTint += shadowColor > 0 ? warmShadow * shadowColor : coolShadow * -shadowColor
        p.grain = grain
        p.grainSize = grainSize
        p.vignette = vignette
        p.halation = halation
        p.bloom = bloom
        if blackAndWhite { p.mono = 1 }
        return p
    }
}

/// Os filmes próprios ficam guardados no aparelho.
enum CustomLookStore {
    private static let key = "customLooks"

    static func load() -> [CustomLook] {
        guard let data = UserDefaults.standard.data(forKey: key) else { return [] }
        return (try? JSONDecoder().decode([CustomLook].self, from: data)) ?? []
    }

    static func save(_ looks: [CustomLook]) {
        if let data = try? JSONEncoder().encode(looks) { UserDefaults.standard.set(data, forKey: key) }
    }
}
