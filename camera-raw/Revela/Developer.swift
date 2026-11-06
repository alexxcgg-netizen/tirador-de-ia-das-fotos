import CoreImage
import CoreImage.CIFilterBuiltins
import ImageIO
import UIKit
import Vision
import simd

/// Calibragem do tom (o laboratório testa variações; o app usa os valores padrão).
struct ToneTuning {
    /// Quanto a cena entra na curva fílmica (antes 0,8: a foto saía apagada, branco em 0,7).
    var filmicGain: Float = 0.93
    /// Quanto do "preto levantado" e do deslocamento de cada filme vale (antes 1: névoa nos filmes suaves).
    var toeScale: Float = 0.5
    var offsetScale: Float = 0.6
    /// Saturação de base de todos os filmes (o Neutro tinha 30% menos cor que a Apple).
    var saturation: Float = 1.2
    /// Tons locais: as sombras sobem mais (× na força) e as luzes descem menos.
    var shadowRatio: Float = 1.8
    var highlightRatio: Float = 0.25
    /// Puxa a luz média da foto de um quadro só até perto de −3 EV (0 = não mexe).
    // 0,15 (era 0,4): como a Apple, entardecer continua entardecer (laboratório: iPhone XS ficou igual à Apple)
    var keyPull: Float = 0.15
    /// Cor que acompanha a luz da cena (efeito Hunt): dia claro com mais cor, cena escura com menos.
    var keyedSaturation: Float = 0.18
    /// Quanto o céu e as nuvens sobem (EV): o branco (p99) ficava 0,05–0,08 abaixo da Apple.
    var highlightBoost: Float = 0.7
    /// Estica a saída da curva fílmica (1 = como era): sobe o branco; o ganho de entrada desce junto para o meio ficar.
    // 1,2 com o ganho de entrada 0,93: branco p99 0,83 → 0,86–0,87 sem mexer no meio (laboratórios a0c9ce1 e 2f641bc)
    var whiteScale: Float = 1.2
    /// Nas luzes fortes, quanto da curva segue o canal mais forte (mantém poste laranja laranja).
    var hueKeep: Float = 0.5
}

/// Só para achar o pacote onde está o metallib.
private final class BundleToken {}

/// Tudo que um look faz com a imagem. Os valores neutros não mudam nada.
struct LookParams {
    var exposure: Float = 0
    var saturation: Float = 1
    var mono: Float = 0
    var toe: Float = 0
    var contrast: Float = 1
    var grain: Float = 0
    /// Tamanho do grão: 1 é fino, 2,5 é grão de Super 8.
    var grainSize: Float = 1.4
    /// Mistura de canais (como os corantes do filme reagem a cada cor).
    var matR = SIMD3<Float>(1, 0, 0)
    var matG = SIMD3<Float>(0, 1, 0)
    var matB = SIMD3<Float>(0, 0, 1)
    /// Curva de cada cor depois da curva fílmica (ASC CDL).
    var slope = SIMD3<Float>(1, 1, 1)
    var offset = SIMD3<Float>(0, 0, 0)
    var power = SIMD3<Float>(1, 1, 1)
    var shadowTint = SIMD3<Float>(0, 0, 0)
    var highTint = SIMD3<Float>(0, 0, 0)
    var vignette: Float = 0
    /// Brilho colorido em volta das luzes fortes (o vermelho do CineStill).
    var halation: Float = 0
    var halationColor = SIMD3<Float>(1, 0.3, 0.1)
    /// Brilho suave e largo em volta das luzes.
    var bloom: Float = 0
    /// LUT importada (.cube), aplicada depois da curva, e o quanto dela entra.
    var lut: LUTCube?
    var lutAmount: Float = 1
    /// Quanto a pele fica de fora do look (0 = nada, 1 = pele neutra).
    var skinProtect: Float = 0
    /// Cor densa: as cores fortes escurecem um pouco, como os corantes do negativo (em vez de ficarem neon).
    var density: Float = 0
    /// Grão colorido (0 = só de brilho, 1 = cada cor com o seu), como no filme colorido de verdade.
    var grainColor: Float = 0

    static func make(_ build: (inout LookParams) -> Void) -> LookParams {
        var p = LookParams()
        build(&p)
        return p
    }

    /// Mistura com o Neutro (`amount` 0…1) e escala o grão.
    func scaled(amount a: Float, grain grainScale: Float) -> LookParams {
        let n = LookParams()
        func mix(_ x: Float, _ y: Float) -> Float { x + (y - x) * a }
        func mix(_ x: SIMD3<Float>, _ y: SIMD3<Float>) -> SIMD3<Float> { x + (y - x) * a }
        var p = self
        p.exposure = mix(n.exposure, exposure)
        p.saturation = mix(n.saturation, saturation)
        p.mono = mix(n.mono, mono)
        p.toe = mix(n.toe, toe)
        p.contrast = mix(n.contrast, contrast)
        p.grain = grain * a * grainScale
        p.matR = mix(n.matR, matR)
        p.matG = mix(n.matG, matG)
        p.matB = mix(n.matB, matB)
        p.slope = mix(n.slope, slope)
        p.offset = mix(n.offset, offset)
        p.power = mix(n.power, power)
        p.shadowTint = shadowTint * a
        p.highTint = highTint * a
        p.vignette = vignette * a
        p.halation = halation * a
        p.bloom = bloom * a
        p.lutAmount = lutAmount * a
        p.density = density * a
        return p
    }
}

/// Tipos de filme, para a lista não virar uma fileira enorme.
enum LookFamily: String, CaseIterable, Identifiable {
    case neutro = "Neutro"
    case cor = "Cor"
    case fuji = "Fuji"
    case cinema = "Cinema"
    case slide = "Slide"
    case criativo = "Criativo"
    case pb = "P&B"

    var id: String { rawValue }
    var looks: [Look] { Look.allCases.filter { $0.family == self } }
}

enum Look: String, CaseIterable, Identifiable {
    case neutro = "Neutro"
    // Negativos coloridos
    case portra = "Portra 400"
    case gold = "Gold 200"
    case ultramax = "Ultramax 400"
    case ektar = "Ektar 100"
    case agfaVista = "Agfa Vista 200"
    case lomo = "Lomo 800"
    // Fuji
    case superia = "Superia 400"
    case pro400h = "Pro 400H"
    case classicChrome = "Classic Chrome"
    case classicNeg = "Classic Neg"
    case eterna = "Eterna"
    // Cinema
    case vision250d = "Vision3 250D"
    case vision500t = "Vision3 500T"
    case cinestill = "CineStill 800T"
    case blockbuster = "Blockbuster"
    case technicolor = "Technicolor"
    case bleach = "Bleach Bypass"
    case matrix = "Matrix"
    // Cromos (slide)
    case velvia = "Velvia 50"
    case kodachrome = "Kodachrome"
    case ektachrome = "Ektachrome E100"
    // Criativos
    case pastel = "Pastel"
    case cross = "Cross-process"
    case polaroid = "Polaroid"
    case super8 = "Super 8"
    // Preto e branco
    case trix = "Tri-X 400"
    case hp5 = "HP5"
    case delta3200 = "Delta 3200"
    case noir = "Noir"
    case sepia = "Sépia"

    var id: String { rawValue }

    var family: LookFamily {
        switch self {
        case .neutro: return .neutro
        case .portra, .gold, .ultramax, .ektar, .agfaVista, .lomo: return .cor
        case .superia, .pro400h, .classicChrome, .classicNeg, .eterna: return .fuji
        case .vision250d, .vision500t, .cinestill, .blockbuster, .technicolor, .bleach, .matrix: return .cinema
        case .velvia, .kodachrome, .ektachrome: return .slide
        case .pastel, .cross, .polaroid, .super8: return .criativo
        case .trix, .hp5, .delta3200, .noir, .sepia: return .pb
        }
    }

    var subtitle: String {
        switch self {
        case .neutro: return "Fiel ao sensor, sem look"
        case .portra: return "Pele quente, cor suave e pastel"
        case .gold: return "Amarelo quente, cara de anos 90"
        case .ektar: return "Cor forte e limpa, céu azul"
        case .velvia: return "Saturação extrema, paisagem"
        case .kodachrome: return "Vermelho profundo, cor clássica"
        case .pro400h: return "Verde ciano, luz clara e fria"
        case .cinestill: return "Noite azul, halo vermelho nas luzes"
        case .blockbuster: return "Sombras azul-petróleo, pele laranja"
        case .technicolor: return "Cor de cinema dos anos 50"
        case .bleach: return "Pouca cor, contraste de prata"
        case .matrix: return "Verde frio, contraste duro"
        case .pastel: return "Rosa e amarelo, contraste baixo"
        case .cross: return "Revelado errado: amarelo e azul"
        case .polaroid: return "Instantânea, preto lavado"
        case .super8: return "Filme caseiro, grão grosso"
        case .trix: return "P&B de reportagem, grão forte"
        case .hp5: return "P&B suave, grão médio"
        case .noir: return "P&B de cinema, preto profundo"
        case .sepia: return "Monocromático marrom antigo"
        case .ultramax: return "Quente e barato, cara de férias"
        case .agfaVista: return "Vermelho forte, sombra verde-azulada"
        case .lomo: return "Saturado, cantos escuros"
        case .superia: return "Verde nas sombras, foto de família"
        case .classicChrome: return "Cor seca e documental, céu ciano"
        case .classicNeg: return "Contraste firme, sombra verde-azulada"
        case .eterna: return "Cinema: pouca cor, verde suave"
        case .vision250d: return "Filme de cinema de dia, suave"
        case .vision500t: return "Cinema de noite: frio com luz quente"
        case .ektachrome: return "Cromo de azul limpo"
        case .delta3200: return "P&B de noite, grão grosso"
        }
    }

    /// Filmes que mexem muito na cor deixam a pele mais de fora, como um colorista faria.
    var skinProtect: Float {
        switch self {
        case .blockbuster, .matrix: return 0.7
        case .cross: return 0.6
        case .bleach: return 0.5
        case .technicolor, .velvia, .cinestill: return 0.4
        case .lomo, .agfaVista: return 0.35
        case .gold, .ektar, .kodachrome, .pastel, .polaroid, .super8, .ultramax, .classicNeg, .vision500t, .ektachrome: return 0.3
        case .classicChrome, .eterna: return 0.2
        case .vision250d, .superia: return 0.1
        case .neutro, .portra, .pro400h, .trix, .hp5, .delta3200, .noir, .sepia: return 0
        }
    }

    /// O look com o que todo filme de verdade tem: cor densa e grão colorido (o Neutro fica intocado).
    var params: LookParams {
        var p = baseParams
        guard self != .neutro else { return p }
        if p.mono < 0.5 {
            if p.density == 0 { p.density = family == .slide ? 0.55 : 0.4 }
            if p.grainColor == 0 { p.grainColor = 0.35 }
        }
        return p
    }

    private var baseParams: LookParams {
        switch self {
        case .neutro:
            return LookParams()
        case .ultramax:
            return .make {
                $0.saturation = 1.15; $0.contrast = 1.08; $0.toe = 0.006
                $0.slope = SIMD3(1.08, 1.02, 0.86); $0.offset = SIMD3(0.006, 0.004, 0.0)
                $0.shadowTint = SIMD3(0.002, 0.002, -0.002); $0.highTint = SIMD3(0.035, 0.02, -0.03)
                $0.grain = 0.05; $0.grainSize = 1.6; $0.vignette = 0.18; $0.halation = 0.1
            }
        case .agfaVista:
            return .make {
                $0.saturation = 1.25; $0.contrast = 1.12
                $0.matR = SIMD3(1.12, -0.08, -0.04); $0.matG = SIMD3(-0.02, 1.02, 0.0)
                $0.slope = SIMD3(1.04, 0.98, 1.02)
                $0.shadowTint = SIMD3(-0.004, 0.006, 0.01); $0.highTint = SIMD3(0.02, 0.004, -0.01)
                $0.grain = 0.04; $0.grainSize = 1.5; $0.vignette = 0.2
            }
        case .lomo:
            return .make {
                $0.saturation = 1.4; $0.contrast = 1.25; $0.toe = 0.01
                $0.slope = SIMD3(1.06, 1.0, 0.9); $0.power = SIMD3(1.0, 1.0, 1.06)
                $0.shadowTint = SIMD3(0.0, 0.004, 0.012); $0.highTint = SIMD3(0.03, 0.02, -0.02)
                $0.grain = 0.07; $0.grainSize = 1.8; $0.vignette = 0.5; $0.halation = 0.15; $0.bloom = 0.06
            }
        case .superia:
            return .make {
                $0.saturation = 1.08; $0.contrast = 1.05; $0.toe = 0.006
                $0.matG = SIMD3(0.02, 1.0, 0.0)
                $0.slope = SIMD3(0.97, 1.03, 0.98); $0.offset = SIMD3(0.0, 0.006, 0.004)
                $0.shadowTint = SIMD3(-0.004, 0.01, 0.004); $0.highTint = SIMD3(0.012, 0.01, -0.008)
                $0.grain = 0.04; $0.grainSize = 1.5; $0.vignette = 0.1; $0.halation = 0.06
            }
        case .classicChrome:
            return .make {
                $0.saturation = 0.72; $0.contrast = 1.12; $0.toe = 0.006
                $0.matR = SIMD3(1.02, -0.02, 0.0); $0.matB = SIMD3(0.0, 0.04, 0.96)
                $0.slope = SIMD3(1.0, 0.99, 0.97); $0.power = SIMD3(1.04, 1.02, 1.0)
                $0.shadowTint = SIMD3(-0.002, 0.002, 0.006); $0.highTint = SIMD3(0.01, 0.006, -0.004)
                $0.grain = 0.02; $0.grainSize = 1.2; $0.vignette = 0.08
            }
        case .classicNeg:
            return .make {
                $0.saturation = 0.95; $0.contrast = 1.2
                $0.slope = SIMD3(1.03, 0.98, 0.95); $0.offset = SIMD3(0.0, 0.004, 0.006); $0.power = SIMD3(1.06, 1.0, 0.98)
                $0.shadowTint = SIMD3(-0.006, 0.008, 0.012); $0.highTint = SIMD3(0.02, 0.006, -0.004)
                $0.grain = 0.03; $0.grainSize = 1.3; $0.vignette = 0.12
            }
        case .eterna:
            return .make {
                $0.saturation = 0.7; $0.contrast = 0.85; $0.toe = 0.01
                $0.slope = SIMD3(0.98, 1.02, 1.0); $0.offset = SIMD3(0.002, 0.006, 0.006)
                $0.shadowTint = SIMD3(-0.002, 0.006, 0.008); $0.highTint = SIMD3(0.006, 0.004, -0.002)
                $0.grain = 0.02; $0.grainSize = 1.2; $0.vignette = 0.1; $0.density = 0.25
            }
        case .vision250d:
            return .make {
                $0.saturation = 0.92; $0.contrast = 0.95; $0.toe = 0.004
                $0.matR = SIMD3(1.03, -0.02, -0.01)
                $0.slope = SIMD3(1.02, 1.0, 0.97); $0.offset = SIMD3(0.002, 0.002, 0.003)
                $0.highTint = SIMD3(0.012, 0.006, -0.004)
                $0.halation = 0.15; $0.halationColor = SIMD3(1.0, 0.35, 0.15)
                $0.grain = 0.025; $0.grainSize = 1.3; $0.vignette = 0.1
            }
        case .vision500t:
            return .make {
                $0.saturation = 0.95; $0.contrast = 1.05; $0.toe = 0.006
                $0.slope = SIMD3(0.88, 0.97, 1.12); $0.offset = SIMD3(0.0, 0.003, 0.008)
                $0.shadowTint = SIMD3(-0.004, 0.004, 0.012); $0.highTint = SIMD3(0.03, 0.012, -0.01)
                $0.halation = 0.35; $0.halationColor = SIMD3(1.0, 0.3, 0.1); $0.bloom = 0.08
                $0.grain = 0.05; $0.grainSize = 1.6; $0.vignette = 0.12
            }
        case .ektachrome:
            return .make {
                $0.saturation = 1.2; $0.contrast = 1.2
                $0.matB = SIMD3(-0.02, -0.02, 1.06)
                $0.slope = SIMD3(0.98, 1.0, 1.05); $0.power = SIMD3(1.02, 1.02, 1.0)
                $0.shadowTint = SIMD3(-0.002, 0.0, 0.008)
                $0.grain = 0.012; $0.grainSize = 1.0; $0.vignette = 0.12
            }
        case .delta3200:
            return .make {
                $0.mono = 1; $0.contrast = 1.1; $0.toe = 0.02
                $0.matR = SIMD3(1.05, -0.03, -0.02)
                $0.grain = 0.16; $0.grainSize = 2.2; $0.vignette = 0.15
            }
        case .portra:
            return .make {
                $0.saturation = 0.82; $0.contrast = 0.9; $0.toe = 0.008
                $0.matR = SIMD3(1.04, -0.02, -0.02); $0.matG = SIMD3(0.05, 0.92, 0.03); $0.matB = SIMD3(-0.02, 0.06, 0.96)
                $0.slope = SIMD3(1.05, 1.0, 0.92); $0.offset = SIMD3(0.006, 0.004, 0.003); $0.power = SIMD3(0.98, 1.0, 1.05)
                $0.highTint = SIMD3(0.02, 0.01, -0.006)
                $0.grain = 0.035; $0.grainSize = 1.4; $0.vignette = 0.12; $0.halation = 0.08
            }
        case .gold:
            return .make {
                $0.saturation = 1.12; $0.contrast = 1.06; $0.toe = 0.006
                $0.matG = SIMD3(0.06, 0.94, 0.0)
                $0.slope = SIMD3(1.1, 1.03, 0.8); $0.offset = SIMD3(0.008, 0.005, 0.0)
                $0.shadowTint = SIMD3(0.004, 0.002, -0.003); $0.highTint = SIMD3(0.04, 0.025, -0.04)
                $0.grain = 0.045; $0.grainSize = 1.6; $0.vignette = 0.22; $0.halation = 0.12
            }
        case .ektar:
            return .make {
                $0.saturation = 1.38; $0.contrast = 1.12
                $0.matR = SIMD3(1.1, -0.06, -0.04); $0.matG = SIMD3(-0.03, 1.07, -0.04); $0.matB = SIMD3(-0.02, -0.05, 1.07)
                $0.slope = SIMD3(1.02, 1.0, 1.04)
                $0.grain = 0.015; $0.grainSize = 1.1; $0.vignette = 0.08
            }
        case .velvia:
            return .make {
                $0.saturation = 1.6; $0.contrast = 1.18
                $0.matR = SIMD3(1.12, -0.08, -0.04); $0.matG = SIMD3(-0.06, 1.12, -0.06); $0.matB = SIMD3(-0.02, -0.08, 1.1)
                $0.slope = SIMD3(1.04, 0.96, 1.06); $0.power = SIMD3(1.02, 1.02, 1.0)
                $0.shadowTint = SIMD3(0.002, -0.002, 0.006)
                $0.grain = 0.012; $0.grainSize = 1.0; $0.vignette = 0.18
            }
        case .kodachrome:
            return .make {
                $0.saturation = 1.25; $0.contrast = 1.22
                $0.matR = SIMD3(1.15, -0.1, -0.05); $0.matG = SIMD3(-0.02, 1.0, 0.02); $0.matB = SIMD3(-0.04, -0.02, 1.06)
                $0.slope = SIMD3(1.05, 0.98, 0.94); $0.offset = SIMD3(0.0, 0.002, 0.005)
                $0.shadowTint = SIMD3(-0.003, 0.002, 0.008); $0.highTint = SIMD3(0.025, 0.012, -0.012)
                $0.grain = 0.025; $0.grainSize = 1.2; $0.vignette = 0.2
            }
        case .pro400h:
            return .make {
                $0.exposure = 0.15; $0.saturation = 0.8; $0.contrast = 0.88; $0.toe = 0.012
                $0.matG = SIMD3(0.0, 0.92, 0.1); $0.matB = SIMD3(0.0, 0.05, 0.98)
                $0.slope = SIMD3(0.96, 1.02, 1.04); $0.offset = SIMD3(0.003, 0.007, 0.008)
                $0.highTint = SIMD3(0.012, 0.0, 0.014)
                $0.grain = 0.03; $0.grainSize = 1.3; $0.vignette = 0.06
            }
        case .cinestill:
            return .make {
                $0.saturation = 1.08; $0.contrast = 1.1; $0.toe = 0.006
                $0.slope = SIMD3(0.78, 0.94, 1.22); $0.offset = SIMD3(0.0, 0.002, 0.006)
                $0.shadowTint = SIMD3(-0.003, 0.005, 0.012)
                $0.halation = 0.9; $0.halationColor = SIMD3(1.0, 0.22, 0.08); $0.bloom = 0.2
                $0.grain = 0.055; $0.grainSize = 1.6; $0.vignette = 0.15
            }
        case .blockbuster:
            return .make {
                $0.saturation = 1.1; $0.contrast = 1.2
                $0.slope = SIMD3(1.06, 1.0, 0.94)
                $0.shadowTint = SIMD3(-0.008, 0.008, 0.018); $0.highTint = SIMD3(0.06, 0.025, -0.045)
                $0.grain = 0.015; $0.vignette = 0.28; $0.bloom = 0.08
            }
        case .technicolor:
            return .make {
                $0.saturation = 1.2; $0.contrast = 1.15
                $0.matR = SIMD3(1.3, -0.18, -0.12); $0.matG = SIMD3(-0.12, 1.25, -0.13); $0.matB = SIMD3(-0.1, -0.18, 1.28)
                $0.slope = SIMD3(1.05, 1.0, 0.97)
                $0.grain = 0.02; $0.vignette = 0.15; $0.bloom = 0.06
            }
        case .bleach:
            return .make {
                $0.saturation = 0.32; $0.contrast = 1.3
                $0.power = SIMD3(1.06, 1.06, 1.05); $0.highTint = SIMD3(0.012, 0.012, 0.01)
                $0.grain = 0.055; $0.grainSize = 1.5; $0.vignette = 0.28
            }
        case .matrix:
            return .make {
                $0.saturation = 0.68; $0.contrast = 1.22
                $0.slope = SIMD3(0.82, 1.08, 0.78)
                $0.shadowTint = SIMD3(-0.002, 0.008, 0.0); $0.highTint = SIMD3(0.0, 0.025, -0.012)
                $0.grain = 0.03; $0.vignette = 0.32
            }
        case .pastel:
            return .make {
                $0.exposure = 0.2; $0.saturation = 0.92; $0.contrast = 0.78; $0.toe = 0.03
                $0.slope = SIMD3(1.06, 1.0, 0.95); $0.offset = SIMD3(0.012, 0.009, 0.013)
                $0.shadowTint = SIMD3(0.008, 0.003, 0.006); $0.highTint = SIMD3(0.03, 0.02, 0.008)
                $0.grain = 0.012
            }
        case .cross:
            return .make {
                $0.saturation = 1.3; $0.contrast = 1.28
                $0.slope = SIMD3(0.95, 1.06, 0.74); $0.power = SIMD3(0.95, 0.94, 1.25); $0.offset = SIMD3(0.0, 0.0, 0.02)
                $0.shadowTint = SIMD3(0.0, 0.003, 0.016); $0.highTint = SIMD3(0.03, 0.045, -0.04)
                $0.grain = 0.045; $0.grainSize = 1.6; $0.vignette = 0.32
            }
        case .polaroid:
            return .make {
                $0.saturation = 0.85; $0.contrast = 0.84; $0.toe = 0.035
                $0.slope = SIMD3(1.05, 1.0, 0.9); $0.offset = SIMD3(0.008, 0.016, 0.022)
                $0.highTint = SIMD3(0.035, 0.022, -0.02)
                $0.grain = 0.03; $0.vignette = 0.38; $0.bloom = 0.12
            }
        case .super8:
            return .make {
                $0.saturation = 1.12; $0.contrast = 1.12; $0.toe = 0.018
                $0.slope = SIMD3(1.12, 1.0, 0.78); $0.offset = SIMD3(0.006, 0.003, 0.0)
                $0.highTint = SIMD3(0.03, 0.015, -0.02)
                $0.grain = 0.13; $0.grainSize = 2.5; $0.vignette = 0.55
                $0.halation = 0.25; $0.halationColor = SIMD3(1.0, 0.5, 0.2); $0.bloom = 0.15
            }
        case .trix:
            return .make {
                $0.mono = 1; $0.contrast = 1.22; $0.toe = 0.002
                $0.matR = SIMD3(1.15, -0.1, -0.05)  // como um filtro amarelo: céu mais escuro
                $0.grain = 0.1; $0.grainSize = 1.8; $0.vignette = 0.15
            }
        case .hp5:
            return .make {
                $0.mono = 1; $0.contrast = 1.05; $0.toe = 0.01
                $0.grain = 0.065; $0.grainSize = 1.5; $0.vignette = 0.1
            }
        case .noir:
            return .make {
                $0.mono = 1; $0.contrast = 1.42; $0.power = SIMD3(1.08, 1.08, 1.08)
                $0.grain = 0.045; $0.vignette = 0.5; $0.bloom = 0.1
            }
        case .sepia:
            return .make {
                $0.mono = 1; $0.contrast = 1.05; $0.toe = 0.012
                $0.slope = SIMD3(1.12, 1.0, 0.76); $0.offset = SIMD3(0.006, 0.003, 0.0)
                $0.grain = 0.055; $0.grainSize = 1.6; $0.vignette = 0.3
            }
        }
    }
}

enum AspectRatio: String, CaseIterable, Identifiable {
    case r43 = "4:3"
    case r11 = "1:1"
    case r169 = "16:9"
    case xpan = "65:24"

    var id: String { rawValue }

    /// Lado maior ÷ lado menor.
    var ratio: CGFloat {
        switch self {
        case .r43: return 4.0 / 3.0
        case .r11: return 1
        case .r169: return 16.0 / 9.0
        case .xpan: return 65.0 / 24.0
        }
    }

    /// Recorte centralizado: primeiro o zoom digital, depois a proporção (mantendo a orientação da imagem).
    func crop(_ rect: CGRect, zoom: CGFloat) -> CGRect {
        var w = rect.width / zoom, h = rect.height / zoom
        let long = max(w, h), short = min(w, h)
        if long / short > ratio {
            if h > w { h = w * ratio } else { w = h * ratio }
        } else {
            if h > w { w = h / ratio } else { h = w / ratio }
        }
        return CGRect(x: rect.midX - w / 2, y: rect.midY - h / 2, width: w, height: h).integral
    }
}

/// Um quadro vindo da câmera: DNG, ou HEIC quando a câmera não oferece RAW.
struct CapturedFrame {
    let data: Data
    let isRaw: Bool
    /// HEIC com mapa de profundidade e máscara de pessoa (Retrato).
    var hasDepth = false
    /// Desvio de exposição do quadro no HDR (−2, 0, +2).
    var exposureBias: Float = 0
    /// Versão neutra já revelada (NOITE, HDR, LONGA, PANORAMA): os tons locais já foram aplicados.
    var toned = false
}

/// Tudo que define como a foto é revelada.
struct DevelopOptions {
    var look: Look = .portra
    /// Filme próprio: quando existe, vale no lugar do `look`.
    var custom: CustomLook?
    var amount: Float = 1
    var grain: Float = 1
    var zoom: CGFloat = 1
    var aspect: AspectRatio = .r43
    /// Inverte na horizontal, como num espelho.
    var mirror = false
    /// HDR: um pouco menos de contraste e um pouco mais de luz, para caber o céu e a sombra.
    var hdrCompress = false
    /// Mantém a proporção da foto original (Revelar de novo).
    var originalAspect = false
    /// Pele protegida nos filmes fortes.
    var skinProtection = true
    /// Exposição para RAW: a foto foi exposta mais clara de propósito; a revelação desconta (em paradas).
    var exposureOffset: Float = 0
    /// Sem halo/brilho nas luzes (foto revelada em faixas, onde o brilho não teria a foto inteira).
    var noGlow = false
    /// Estrela no sol e nas luzes fortes das fotos de dia (0 = sem).
    var starPoints = 0

    func cropRect(in extent: CGRect) -> CGRect {
        guard originalAspect else { return aspect.crop(extent, zoom: zoom) }
        let w = extent.width / zoom, h = extent.height / zoom
        return CGRect(x: extent.midX - w / 2, y: extent.midY - h / 2, width: w, height: h).integral
    }

    var params: LookParams {
        var p = (custom?.params ?? look.params).scaled(amount: amount, grain: grain)
        p.skinProtect = skinProtection && custom?.lutFile == nil ? (custom?.baseLook ?? look).skinProtect * amount : 0
        p.exposure += exposureOffset
        if noGlow {
            p.halation = 0
            p.bloom = 0
        }
        if hdrCompress {
            p.contrast *= 0.85
            p.exposure += 0.15
        }
        return p
    }

    var lookName: String { custom?.name ?? look.rawValue }
}

/// Revela o DNG com a nossa própria curva, sem o processamento de "aparência" da Apple.
enum Developer {
    static var tuning = ToneTuning()

    struct Output {
        let heic: Data
        let thumbnail: UIImage?
        /// O recorte deixou a foto do mesmo tamanho do DNG (necessário para a galeria aceitar o par).
        let sameSizeAsRaw: Bool
        /// A luz de cena que gerou a foto (para guardar uma versão neutra e revelar de novo depois).
        var scene: CIImage?
    }

    static let displayP3 = CGColorSpace(name: CGColorSpace.displayP3)!
    static let linearP3 = CGColorSpace(name: CGColorSpace.extendedLinearDisplayP3)!

    static let context = CIContext(options: [
        .workingColorSpace: linearP3,
        .workingFormat: CIFormat.RGBAh,
        .cacheIntermediates: false,
    ])

    private static let library: Data? = {
        // No app vem no pacote principal; no laboratório de testes, no pacote dos testes
        guard let url = Bundle.main.url(forResource: "default", withExtension: "metallib")
                ?? Bundle(for: BundleToken.self).url(forResource: "default", withExtension: "metallib") else { return nil }
        return try? Data(contentsOf: url)
    }()

    private static func kernel(_ name: String) -> CIColorKernel? {
        library.flatMap { try? CIColorKernel(functionName: name, fromMetalLibraryData: $0) }
    }

    private static let toneKernel = kernel("revelaTone")
    private static let toSceneKernel = kernel("revelaToScene")
    private static let highlightsKernel = kernel("revelaHighlights")
    private static let peakingKernel = kernel("revelaPeaking")
    private static let sharpnessKernel = kernel("revelaSharpness")
    private static let pickKernel = kernel("revelaPick")
    private static let clipKernel = kernel("revelaClip")
    private static let addKernel = kernel("revelaAdd")
    private static let hdrColorKernel = kernel("revelaHDRColor")
    private static let hdrWeightKernel = kernel("revelaHDRWeight")
    static let divideKernel = kernel("revelaDivide")
    static let paperKernel = kernel("revelaPaper")
    private static let hdrGhostColorKernel = kernel("revelaHDRGhostColor")
    private static let hdrGhostWeightKernel = kernel("revelaHDRGhostWeight")
    static let robustColorKernel = kernel("revelaRobustColor")
    static let robustWeightKernel = kernel("revelaRobustWeight")
    private static let logLumaKernel = kernel("revelaLogLuma")
    private static let skinMixKernel = kernel("revelaSkinMix")
    private static let chromaKernel = kernel("revelaChroma")
    private static let peakKernel = kernel("revelaPeak")
    private static let highColorKernel = kernel("revelaHighColor")
    private static let subKernel = kernel("revelaSub")
    private static let divideAddKernel = kernel("revelaDivideAdd")
    private static let bokehSourceKernel = kernel("revelaBokehSource")
    private static let shrinkKernel = kernel("revelaShrink")
    private static let recoverKernel = kernel("revelaRecover")
    private static let bandKernel = kernel("revelaBand")
    private static let shadowsHighlightsKernel = kernel("revelaShadowsHighlights")
    private static let localToneKernel = kernel("revelaLocalTone")
    static let splatKernel: CIKernel? = library.flatMap { try? CIKernel(functionName: "revelaSplat", fromMetalLibraryData: $0) }
    static let gridWarpKernel: CIWarpKernel? = library.flatMap {
        try? CIWarpKernel(functionName: "revelaGridWarp", fromMetalLibraryData: $0)
    }
    static let ratioKernel = kernel("revelaRatio")
    static let multiplyKernel = kernel("revelaMultiply")
    static let cylinderKernel: CIWarpKernel? = library.flatMap {
        try? CIWarpKernel(functionName: "revelaCylinder", fromMetalLibraryData: $0)
    }
    private static let blurMapKernel = kernel("revelaBlurMap")
    static let maxKernel = kernel("revelaMax")
    static let sumKernel = kernel("revelaAdd")
    private static let falseColorKernel = kernel("revelaFalseColor")

    private static let noise = CIFilter.randomGenerator().outputImage!

    /// Grão de filme: ruído em três tamanhos somados (0,6, 1,2 e 2,4 px, pesos 1, ½, ¼), como os grãos de prata
    /// de vários tamanhos. Antes era ruído de 1 pixel ampliado, que vira um quadriculado. Feito uma vez (1024 px)
    /// e repetido lado a lado; cada foto pega um pedaço diferente.
    private static let grainTexture: CIImage = {
        let side: CGFloat = 1024, pad: CGFloat = 16
        let source = noise.cropped(to: CGRect(x: 0, y: 0, width: side + 2 * pad, height: side + 2 * pad))
        // Desvio do ruído uniforme (0,289) cai com o borrão (≈ 0,28/σ): cada camada volta ao mesmo desvio total
        var sum = CIImage(color: CIColor(red: 0.5, green: 0.5, blue: 0.5)).cropped(to: source.extent)
        for (sigma, weight) in [(0.6, 1.0), (1.2, 0.5), (2.4, 0.25)] as [(Double, Double)] {
            let k = CGFloat(weight * 2.08)
            let layer = source.clampedToExtent().applyingGaussianBlur(sigma: sigma).cropped(to: source.extent)
                .applyingFilter("CIColorMatrix", parameters: [
                    "inputRVector": CIVector(x: k, y: 0, z: 0, w: 0), "inputGVector": CIVector(x: 0, y: k, z: 0, w: 0),
                    "inputBVector": CIVector(x: 0, y: 0, z: k, w: 0), "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 0),
                    "inputBiasVector": CIVector(x: -0.5 * k, y: -0.5 * k, z: -0.5 * k, w: 0),
                ])
            sum = layer.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: sum]).cropped(to: source.extent)
        }
        let tile = materialize(sum.cropped(to: CGRect(x: pad, y: pad, width: side, height: side)),
                               extent: CGRect(x: pad, y: pad, width: side, height: side))
            .transformed(by: CGAffineTransform(translationX: -pad, y: -pad))
        return tile.applyingFilter("CIAffineTile", parameters: [kCIInputTransformKey: NSValue(cgAffineTransform: .identity)])
    }()

    /// Valor de cena em que o vídeo do iPhone já chega estourado (0,97 na tela), para a zebra.
    private static var zebraThreshold: Float {
        let x: Float = 0.97, a: Float = 2.51, b: Float = 0.03, c: Float = 2.43, d: Float = 0.59, e: Float = 0.14
        let A = x * c - a, B = x * d - b, C = x * e
        return (-B - (B * B - 4 * A * C).squareRoot()) / (2 * A) / tuning.filmicGain
    }

    /// Diz se os kernels de Metal carregaram (sem eles a revelação sai sem look).
    static var kernelStatus: String {
        let names = ["revelaTone": toneKernel, "revelaToScene": toSceneKernel, "revelaHighlights": highlightsKernel,
                     "revelaPeaking": peakingKernel, "revelaSharpness": sharpnessKernel, "revelaPick": pickKernel,
                     "revelaClip": clipKernel, "revelaAdd": addKernel, "revelaHDRColor": hdrColorKernel,
                     "revelaHDRWeight": hdrWeightKernel, "revelaDivide": divideKernel, "revelaPaper": paperKernel, "revelaBlurMap": blurMapKernel,
                     "revelaMax": maxKernel, "revelaFalseColor": falseColorKernel]
        var missing = names.filter { $0.value == nil }.map(\.key).sorted()
        if cylinderKernel == nil { missing.append("revelaCylinder") }
        if gridWarpKernel == nil { missing.append("revelaGridWarp") }
        if ratioKernel == nil { missing.append("revelaRatio") }
        if multiplyKernel == nil { missing.append("revelaMultiply") }
        let more: [String: CIColorKernel?] = ["revelaHDRGhostColor": hdrGhostColorKernel, "revelaHDRGhostWeight": hdrGhostWeightKernel,
                                              "revelaRobustColor": robustColorKernel, "revelaRobustWeight": robustWeightKernel,
                                              "revelaLogLuma": logLumaKernel, "revelaLocalTone": localToneKernel,
                                              "revelaSkinMix": skinMixKernel, "revelaBand": bandKernel,
                                              "revelaShadowsHighlights": shadowsHighlightsKernel, "revelaChroma": chromaKernel,
                                              "revelaRecover": recoverKernel]
        missing += more.filter { $0.value == nil }.map(\.key).sorted()
        return missing.isEmpty ? "todos carregados" : "FALTANDO: " + missing.joined(separator: ", ")
    }

    // MARK: - Abrir os quadros

    /// RAW -> luz linear da cena, sem boost de contraste e sem tone mapping local da Apple.
    /// `neutralExposure`: sem a exposição de base do DNG (HDR: o branco do sensor fica em 1,0 em todos os quadros).
    static func linear(dng: Data, scale: Float = 1, neutralExposure: Bool = false) -> CIImage? {
        guard let raw = CIRAWFilter(imageData: dng, identifierHint: "com.adobe.raw-image") else { return nil }
        raw.boostAmount = 0
        raw.boostShadowAmount = 0
        if raw.isLocalToneMapSupported { raw.localToneMapAmount = 0 }
        raw.extendedDynamicRangeAmount = 0
        if neutralExposure { raw.baselineExposure = 0 }
        if scale < 1 {
            raw.scaleFactor = scale
            raw.isDraftModeEnabled = true
        }
        guard let image = raw.outputImage else { return nil }

        // A orientação já foi aplicada pelo CIRAWFilter; não deixar a tag girar a foto de novo.
        var properties = image.properties
        properties[kCGImagePropertyOrientation as String] = nil
        if var tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any] {
            tiff[kCGImagePropertyTIFFOrientation as String] = nil
            properties[kCGImagePropertyTIFFDictionary as String] = tiff
        }
        return image.settingProperties(properties)
    }

    /// HEIC já processado pela Apple -> luz de cena aproximada (desfaz a curva antes do look).
    static func processed(_ data: Data, scale: Float = 1) -> CIImage? {
        guard var image = CIImage(data: data, options: [.applyOrientationProperty: true]) else { return nil }
        var properties = image.properties
        properties[kCGImagePropertyOrientation as String] = nil
        if scale < 1 { image = image.transformed(by: CGAffineTransform(scaleX: CGFloat(scale), y: CGFloat(scale))) }
        let scene = toSceneKernel?.apply(extent: image.extent, arguments: [image, tuning.filmicGain]) ?? image
        return scene.settingProperties(properties)
    }

    /// Só o laboratório usa: troca a abertura do arquivo por imagens geradas (ex.: fotos deslocadas para a super resolução).
    static var decodeOverride: ((CapturedFrame, Float) -> CIImage?)?

    static func image(from frame: CapturedFrame, scale: Float = 1) -> CIImage? {
        if let decodeOverride, let image = decodeOverride(frame, scale) { return image }
        return frame.isRaw ? linear(dng: frame.data, scale: scale) : processed(frame.data, scale: scale)
    }

    // MARK: - Foto

    static func develop(_ frame: CapturedFrame, options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard let image = image(from: frame) else {
            dlog("❌ Não abriu o \(frame.isRaw ? "DNG" : "HEIC") (\(frame.data.count / 1024) KB)")
            return nil
        }
        // O RAW pequeno (rápido) serve para os tons locais: o grande é aberto uma vez só, na revelação
        let preview = frame.isRaw ? self.image(from: frame, scale: 0.125) : nil
        let output = finish(enhanced(image, preview: preview), options: options)
        dlog("Revelação \(options.lookName) \(Int(image.extent.width))×\(Int(image.extent.height)) · \(frame.isRaw ? "DNG" : "HEIC") \(frame.data.count / 1_048_576) MB: \(Diagnostics.ms(since: t0))\(output == nil ? " · FALHOU" : "")")
        return output
    }

    /// Revela uma imagem minúscula com o caminho inteiro (tons locais, ruído, filme, HEIC): o Metal monta os filtros
    /// e o codificador de HEIC acorda antes da primeira foto de verdade.
    static func warmUp(options: DevelopOptions) {
        let t0 = CFAbsoluteTimeGetCurrent()
        let tiny = CIImage(color: CIColor(red: 0.2, green: 0.18, blue: 0.15)).cropped(to: CGRect(x: 0, y: 0, width: 256, height: 192))
        var opts = options
        opts.zoom = 1
        _ = finish(enhanced(tiny), options: opts)
        _ = finish(nightDenoise(tiny, strength: 0.5), options: opts)
        dlog("Revelação aquecida: \(Diagnostics.ms(since: t0))")
    }

    /// Luz de cena -> recorte, look e HEIC de 10 bits.
    static func finish(_ scene: CIImage, options: DevelopOptions) -> Output? {
        let (graded, rect) = developed(scene, options: options)

        guard let heic = try? context.heif10Representation(
            of: graded,
            colorSpace: displayP3,
            options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.92]
        ) else { return nil }

        let same = abs(rect.width - scene.extent.width) < 2 && abs(rect.height - scene.extent.height) < 2
        var output = Output(heic: heic, thumbnail: thumbnail(of: graded), sameSizeAsRaw: same)
        output.scene = scene
        return output
    }

    /// Recorte (zoom e proporção), espelho e look. Devolve também o recorte usado, em coordenadas da cena.
    static func developed(_ scene: CIImage, options: DevelopOptions) -> (CIImage, CGRect) {
        let rect = options.cropRect(in: scene.extent)
        var cropped = scene.cropped(to: rect)
            .transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))
        if options.mirror {
            cropped = cropped.transformed(by: CGAffineTransform(scaleX: -1, y: 1).translatedBy(x: -rect.width, y: 0))
        }
        // Estrela de dia: só nas luzes pequenas e estouradas (sol, poste, reflexo), nunca em nuvem ou céu claro.
        // Fica de fora na foto revelada em faixas (a estrela precisa da foto inteira)
        if options.starPoints > 0, !options.noGlow {
            cropped = dayStar(cropped, points: options.starPoints)
        }
        return (grade(cropped, look: options.params, zebra: false).settingProperties(scene.properties), rect)
    }

    /// Versão pequena revelada, para mostrar na tela (Revelar de novo).
    static func render(_ scene: CIImage, options: DevelopOptions) -> UIImage? {
        let (graded, _) = developed(scene, options: options)
        guard let cg = context.createCGImage(graded, from: graded.extent, format: .RGBA8, colorSpace: displayP3) else { return nil }
        return UIImage(cgImage: cg)
    }

    /// Ajustes do Revelar de novo, aplicados na luz de cena (antes do filme).
    struct Adjust: Equatable {
        var exposure: Float = 0
        /// Quente (+) ou frio (−).
        var temperature: Float = 0
        /// Magenta (+) ou verde (−).
        var tint: Float = 0
        var shadows: Float = 0
        var highlights: Float = 0
        /// Graus para endireitar o horizonte.
        var straighten: Float = 0
        /// Recorte centralizado (1 = foto inteira).
        var crop: Float = 1

        var isNeutral: Bool { self == Adjust() }
    }

    static func adjusted(_ scene: CIImage, _ a: Adjust) -> CIImage {
        guard !a.isNeutral else { return scene }
        let e = scene.extent
        var out = scene
        // Balanço de branco e exposição: ganhos por canal na luz linear (como no RAW)
        let ev = pow(2, a.exposure)
        let r = CGFloat(ev * pow(2, a.temperature * 0.35))
        let g = CGFloat(ev * pow(2, -a.tint * 0.25))
        let b = CGFloat(ev * pow(2, -a.temperature * 0.35))
        if r != 1 || g != 1 || b != 1 {
            out = out.applyingFilter("CIColorMatrix", parameters: [
                "inputRVector": CIVector(x: r, y: 0, z: 0, w: 0),
                "inputGVector": CIVector(x: 0, y: g, z: 0, w: 0),
                "inputBVector": CIVector(x: 0, y: 0, z: b, w: 0),
                "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
            ])
        }
        if a.shadows != 0 || a.highlights != 0, let shadowsHighlightsKernel {
            out = shadowsHighlightsKernel.apply(extent: e, arguments: [out, a.shadows, a.highlights]) ?? out
        }
        // Endireitar: gira em volta do centro e corta o maior retângulo que cabe sem borda
        var rect = e
        if abs(a.straighten) > 0.01 {
            let angle = CGFloat(a.straighten) * .pi / 180
            let c = CGPoint(x: e.midX, y: e.midY)
            out = out.clampedToExtent()
                .transformed(by: CGAffineTransform(translationX: -c.x, y: -c.y).concatenating(CGAffineTransform(rotationAngle: angle))
                    .concatenating(CGAffineTransform(translationX: c.x, y: c.y)))
            let w = e.width, h = e.height
            let cosA = abs(cos(angle)), sinA = abs(sin(angle))
            let k = min(w / (w * cosA + h * sinA), h / (w * sinA + h * cosA))
            rect = CGRect(x: c.x - w * k / 2, y: c.y - h * k / 2, width: w * k, height: h * k)
        }
        if a.crop > 1.001 {
            let k = 1 / CGFloat(a.crop)
            rect = CGRect(x: rect.midX - rect.width * k / 2, y: rect.midY - rect.height * k / 2,
                          width: rect.width * k, height: rect.height * k)
        }
        rect = rect.integral
        return out.cropped(to: rect).transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))
            .settingProperties(scene.properties)
    }

    /// A foto tem mapa de profundidade (Retrato do Revela ou do app Câmera)?
    static func hasDepth(_ data: Data) -> Bool {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil) else { return false }
        return CGImageSourceCopyAuxiliaryDataInfoAtIndex(source, 0, kCGImageAuxiliaryDataTypeDisparity) != nil
            || CGImageSourceCopyAuxiliaryDataInfoAtIndex(source, 0, kCGImageAuxiliaryDataTypeDepth) != nil
    }

    /// Luz de cena de qualquer foto: RAW, HEIC/JPEG, ou retrato com o desfoque escolhido.
    static func scene(for frame: CapturedFrame, scale: Float = 1, aperture: Float? = nil, focusPoint: CGPoint? = nil) -> CIImage? {
        if frame.hasDepth, let aperture {
            return portraitScene(frame.data, aperture: aperture, focusPoint: focusPoint, scale: CGFloat(scale))
        }
        guard let opened = image(from: frame, scale: scale) else { return nil }
        // A versão neutra guardada já tem os tons locais: aplicar de novo deixaria a foto lavada
        if frame.toned { return opened }
        return enhanced(opened, preview: scale < 0.5 ? nil : image(from: frame, scale: 0.125))
    }

    /// Foto de um quadro só: tons locais suaves (céu e sombra equilibrados) e, com ISO alto, menos ruído colorido.
    /// O ProRAW já vem de várias fotos juntadas pela Apple; isto só acerta o que a curva do filme não faz.
    static func enhanced(_ scene: CIImage, preview: CIImage? = nil) -> CIImage {
        let exif = scene.properties[kCGImagePropertyExifDictionary as String] as? [String: Any]
        let iso = (exif?[kCGImagePropertyExifISOSpeedRatings as String] as? [NSNumber])?.first?.floatValue ?? 100
        var out = localTone(scene, strength: 0.85, preview: preview, keyPull: tuning.keyPull,
                            highlightBoost: tuning.highlightBoost)
        // Cor pela luz da cena, como a Apple: dia claro (−3,3 EV) ganha ~12% de cor, entardecer (−4,7 EV) perde ~12%
        let saturation = min(1.15, max(0.85, 1 + tuning.keyedSaturation * (lastKey + 4)))
        if abs(saturation - 1) > 0.01 {
            out = out.applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: saturation]).cropped(to: out.extent)
        }
        if iso >= 800 {
            out = nightDenoise(out, strength: min(0.8, log2(iso / 400) / 6))
        }
        // Nitidez fina, leve (a Apple tem um pouco mais de "mordida" nas folhas): raio pelo tamanho da foto,
        // menos com ISO alto (para não afiar o ruído)
        let e = scene.extent
        if max(e.width, e.height) >= 1500 {
            // Raio pelo tamanho, até 1,35 px; força 0,26 (0,32 dava borda 1,4× a da Apple na foto de 48 MP)
            let radius = 0.9 * min(1.5, max(1, max(e.width, e.height) / 4032))
            // Foto bem grande (48 MP): um pouco menos (borda 1,31× a da Apple no laboratório)
            let big = max(e.width, e.height) > 5000
            let amount = iso >= 1600 ? 0.13 : (big ? 0.21 : 0.26)
            out = out.applyingFilter("CIUnsharpMask", parameters: [kCIInputRadiusKey: radius, kCIInputIntensityKey: amount]).cropped(to: e)
        }
        return out.settingProperties(scene.properties)
    }

    /// Halation/bloom + o kernel do look.
    private static func grade(_ scene: CIImage, look p: LookParams, zebra: Bool) -> CIImage {
        guard let toneKernel else { return scene }
        let glowing = addGlow(to: scene, look: p)
        let size = CGFloat(p.grainSize)
        let grainNoise = grainTexture
            .transformed(by: CGAffineTransform(translationX: .random(in: 0...1024), y: .random(in: 0...1024)))
            .transformed(by: CGAffineTransform(scaleX: size, y: size))
        let e = scene.extent
        let arguments: [Any] = [
            glowing, grainNoise,
            p.exposure, p.saturation * tuning.saturation, p.mono, p.toe * tuning.toeScale, p.contrast, p.grain,
            vector(p.matR), vector(p.matG), vector(p.matB),
            vector(p.slope), vector(p.offset * tuning.offsetScale), vector(p.power),
            vector(p.shadowTint), vector(p.highTint),
            p.vignette, CIVector(x: e.minX, y: e.minY, z: e.width, w: e.height),
            zebra ? zebraThreshold : Float(0),
            CIVector(x: CGFloat(p.density), y: CGFloat(p.grainColor), z: CGFloat(tuning.filmicGain), w: CGFloat(tuning.hueKeep)),
            tuning.whiteScale,
        ]
        var toned = toneKernel.apply(extent: e, arguments: arguments) ?? scene
        if p.skinProtect > 0.01, p.mono < 0.5, let skinMixKernel {
            // Mesma luz e textura do look, sem a cor dele: é para essa versão que a pele puxa
            var neutral = arguments
            neutral[3] = min(p.saturation, 1.05) * tuning.saturation
            neutral[8] = vector(SIMD3(1, 0, 0)); neutral[9] = vector(SIMD3(0, 1, 0)); neutral[10] = vector(SIMD3(0, 0, 1))
            neutral[11] = vector(SIMD3(1, 1, 1)); neutral[12] = vector(SIMD3(0, 0, 0)); neutral[13] = vector(SIMD3(1, 1, 1))
            neutral[14] = vector(SIMD3(0, 0, 0)); neutral[15] = vector(SIMD3(0, 0, 0))
            if let plain = toneKernel.apply(extent: e, arguments: neutral) {
                toned = skinMixKernel.apply(extent: e, arguments: [toned, plain, scene, p.skinProtect]) ?? toned
            }
        }
        guard let lut = p.lut, p.lutAmount > 0.001 else { return toned }
        // A LUT espera a imagem já codificada para a tela (sRGB/Rec. 709), como num editor de vídeo
        let cubed = toned.applyingFilter("CIColorCubeWithColorSpace", parameters: [
            "inputCubeDimension": lut.dimension,
            "inputCubeData": lut.data,
            "inputColorSpace": sRGB,
        ]).cropped(to: e)
        guard p.lutAmount < 0.999 else { return cubed }
        return toned.applyingFilter("CIDissolveTransition", parameters: [
            kCIInputTargetImageKey: cubed,
            kCIInputTimeKey: p.lutAmount,
        ]).cropped(to: e)
    }

    private static let sRGB = CGColorSpace(name: CGColorSpace.sRGB)!

    /// Brilho em volta das luzes fortes, calculado numa versão pequena da imagem (o resultado é borrado de qualquer jeito).
    private static func addGlow(to scene: CIImage, look p: LookParams) -> CIImage {
        guard p.halation > 0.001 || p.bloom > 0.001, let highlightsKernel else { return scene }
        let e = scene.extent
        let small: CGFloat = 0.25
        let shortSide = min(e.width, e.height) * small
        // Reduz primeiro e só então separa as luzes: o filtro roda em 1/16 dos pixels (no 48 MP fazia diferença)
        let shrunk = scene.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: small, kCIInputAspectRatioKey: 1])
        let reduced = (highlightsKernel.apply(extent: shrunk.extent, arguments: [shrunk, Float(0.9)]) ?? shrunk).clampedToExtent()
        var out = scene
        func glow(sigma: CGFloat, color: SIMD3<Float>, amount: Float) {
            let blurred = reduced.applyingGaussianBlur(sigma: Double(sigma))
                .transformed(by: CGAffineTransform(scaleX: 1 / small, y: 1 / small))
                .cropped(to: e)
                .applyingFilter("CIColorMatrix", parameters: [
                    "inputRVector": CIVector(x: CGFloat(color.x * amount), y: 0, z: 0, w: 0),
                    "inputGVector": CIVector(x: 0, y: CGFloat(color.y * amount), z: 0, w: 0),
                    "inputBVector": CIVector(x: 0, y: 0, z: CGFloat(color.z * amount), w: 0),
                    "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
                ])
            out = blurred.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: out])
        }
        if p.halation > 0.001 { glow(sigma: shortSide * 0.006, color: p.halationColor, amount: p.halation * 0.8) }
        if p.bloom > 0.001 { glow(sigma: shortSide * 0.03, color: SIMD3(1, 0.95, 0.9), amount: p.bloom) }
        return out
    }

    // MARK: - Quadros de vídeo (modo AÇÃO)

    /// Quadro de vídeo (já com a curva da Apple) -> look e HEIC.
    static func developVideoFrame(_ frame: CGImage, options: DevelopOptions) -> Output? {
        let image = CIImage(cgImage: frame)
        let scene = toSceneKernel?.apply(extent: image.extent, arguments: [image, tuning.filmicGain]) ?? image
        return finish(scene, options: options)
    }

    /// Imagem de vídeo (exposição longa) -> look e HEIC.
    static func developVideoImage(_ image: CIImage, options: DevelopOptions) -> Output? {
        let scene = toSceneKernel?.apply(extent: image.extent, arguments: [image, tuning.filmicGain]) ?? image
        return finish(scene, options: options)
    }

    // MARK: - Super resolução

    /// Nota de nitidez (média do |laplaciano|): quanto maior, menos tremida/borrada.
    static func sharpnessScore(_ image: CIImage) -> Float {
        let scale = min(1, 512 / max(image.extent.width, image.extent.height))
        let small = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        let laplacian = small.applyingFilter("CIConvolution3X3", parameters: [
            "inputWeights": CIVector(values: [0, 1, 0, 1, -4, 1, 0, 1, 0], count: 9),
            "inputBias": 0,
        ])
        guard let abs = sharpnessKernel?.apply(extent: small.extent, arguments: [laplacian]) else { return 0 }
        let average = abs.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: small.extent)])
        var pixel = [Float](repeating: 0, count: 4)
        context.render(average, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                       format: .RGBAf, colorSpace: nil)
        return pixel[0]
    }

    // MARK: - Empilhamento

    enum StackKind { case focus, average }

    /// Junta vários quadros em lotes pequenos (para não esgotar a memória):
    /// foco empilhado (pega o pedaço mais nítido de cada um) ou média (menos ruído / exposição longa).
    /// `starPoints`: NOITE, raios em volta das luzes fortes, como numa lente fechada (0 = sem).
    static func stack(_ allFrames: [CapturedFrame], kind: StackKind, removeOutliers: Bool = false,
                      robust: Bool = false, starPoints: Int = 0, options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        // NOITE: a foto curta (para as luzes) fica de fora da soma
        let shortFrame = allFrames.first { $0.exposureBias < -1 }
        var frames = allFrames.filter { $0.exposureBias >= -1 }
        if robust, frames.count > 2 {
            // Noite: a referência (que manda onde algo se mexeu) é a foto mais nítida, não a primeira
            let scores = frames.map { frame in image(from: frame, scale: 0.125).map(sharpnessScore) ?? 0 }
            if let best = scores.indices.max(by: { scores[$0] < scores[$1] }), best != 0 {
                frames.swapAt(0, best)
                dlog(String(format: "Noite: referência é a foto %d (a mais nítida)", best + 1))
            }
        }
        guard let reference = frames.first.flatMap({ image(from: $0) }) else { return nil }
        let extent = reference.extent
        dlog("Empilhando \(frames.count) quadros (\(kind == .focus ? "foco" : "média")) · \(Int(extent.width))×\(Int(extent.height)) · memória livre \(Diagnostics.freeMemory)")

        // Alinha numa versão pequena de cada quadro (rápido e leve); aplica depois no tamanho cheio.
        // NOITE: alinhamento fino (fração de pixel e por região), o mesmo da super resolução
        let alignScale: Float = 0.25
        guard let smallReference = image(from: frames[0], scale: alignScale) else { return nil }
        var warps: [(CIImage) -> CIImage] = [{ $0 }]
        if robust {
            warps = fineWarps(frames, reference: reference)
        } else {
            for frame in frames.dropFirst() {
                guard let small = image(from: frame, scale: alignScale) else { warps.append({ $0 }); continue }
                warps.append(alignment(of: small, to: smallReference, scale: CGFloat(alignScale),
                                       fullExtent: extent, homography: kind == .focus))
            }
        }
        dlog("Alinhamento: \(Diagnostics.ms(since: t0))")

        func aligned(_ i: Int) -> CIImage? {
            image(from: frames[i]).map { warps[i]($0).cropped(to: extent) }
        }

        let merged: CIImage?
        switch kind {
        case .average where robust:
            merged = robustMerge(count: frames.count, extent: extent, frame: aligned).map { night in
                let exif = reference.properties[kCGImagePropertyExifDictionary as String] as? [String: Any]
                let iso = (exif?[kCGImagePropertyExifISOSpeedRatings as String] as? [NSNumber])?.first?.floatValue ?? 800
                var out = materialize(night, extent: extent)
                // Postes e letreiros: a foto curta devolve a luz onde a junção estourou
                if let shortFrame, let recoverKernel, let short = image(from: shortFrame),
                   let smallShort = image(from: shortFrame, scale: alignScale) {
                    let gain = Float(pow(2.0, Double(-shortFrame.exposureBias)))
                    let warp = alignment(of: scaled(smallShort, by: gain), to: smallReference, scale: CGFloat(alignScale),
                                         fullExtent: extent, homography: false)
                    let alignedShort = warp(short).cropped(to: extent)
                    out = recoverKernel.apply(extent: extent, arguments: [out, alignedShort, gain]) ?? out
                    dlog(String(format: "Noite: luzes fortes recuperadas da foto curta (%.0f×)", gain))
                }
                return nightFinish(out, iso: iso, frameCount: frames.count, starPoints: starPoints)
            }
        case .average:
            var mean = average(count: frames.count, extent: extent, frame: aligned)
            if removeOutliers, let first = mean, let clipKernel {
                // Segunda passada: cada quadro é limitado ao que a média permite
                mean = average(count: frames.count, extent: extent) { i in
                    aligned(i).flatMap { clipKernel.apply(extent: extent, arguments: [$0, first, Float(0.6)]) }
                }
                dlog("Estrelas: pontos que apareceram em poucos quadros removidos")
            }
            merged = mean
        case .focus:
            merged = focusMerge(count: frames.count, extent: extent, frame: aligned)
        }
        guard let merged else { return nil }
        let output = finish(merged.settingProperties(reference.properties), options: options)
        dlog("Empilhamento + revelação: \(Diagnostics.ms(since: t0)) · memória livre \(Diagnostics.freeMemory)\(output == nil ? " · FALHOU" : "")")
        return output
    }

    /// Vision compara a versão pequena com a de referência. Translação para o tremido da mão;
    /// homografia no foco empilhado, porque a imagem também cresce um pouco quando o foco muda.
    private static func alignment(of small: CIImage, to reference: CIImage, scale: CGFloat,
                                  fullExtent: CGRect, homography: Bool) -> (CIImage) -> CIImage {
        let handler = VNImageRequestHandler(ciImage: reference, options: [:])
        if homography {
            let request = VNHomographicImageRegistrationRequest(targetedCIImage: small, options: [:])
            if (try? handler.perform([request])) != nil,
               let observation = request.results?.first as? VNImageHomographicAlignmentObservation {
                let s = simd_float3x3(diagonal: SIMD3(Float(scale), Float(scale), 1))
                let h = s.inverse * observation.warpTransform * s
                let e = fullExtent
                func map(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
                    let v = h * SIMD3(Float(x), Float(y), 1)
                    return CGPoint(x: CGFloat(v.x / v.z), y: CGFloat(v.y / v.z))
                }
                let corners = [map(e.minX, e.maxY), map(e.maxX, e.maxY), map(e.maxX, e.minY), map(e.minX, e.minY)]
                let original = [CGPoint(x: e.minX, y: e.maxY), CGPoint(x: e.maxX, y: e.maxY),
                                CGPoint(x: e.maxX, y: e.minY), CGPoint(x: e.minX, y: e.minY)]
                let maxShift = zip(corners, original).map { hypot($0.x - $1.x, $0.y - $1.y) }.max() ?? 0
                if maxShift < e.width * 0.08 {
                    dlog(String(format: "Quadro alinhado (homografia), canto mais deslocado %.0f px", maxShift))
                    return { image in
                        image.applyingFilter("CIPerspectiveTransform", parameters: [
                            "inputTopLeft": CIVector(cgPoint: corners[0]), "inputTopRight": CIVector(cgPoint: corners[1]),
                            "inputBottomRight": CIVector(cgPoint: corners[2]), "inputBottomLeft": CIVector(cgPoint: corners[3]),
                        ])
                    }
                }
                dlog(String(format: "Homografia exagerada (%.0f px); usando só translação", maxShift))
            }
        }
        let request = VNTranslationalImageRegistrationRequest(targetedCIImage: small, options: [:])
        guard (try? handler.perform([request])) != nil,
              let observation = request.results?.first as? VNImageTranslationAlignmentObservation else {
            dlog("Alinhamento falhou num quadro (usado sem alinhar)")
            return { $0 }
        }
        let t = observation.alignmentTransform
        let tx = t.tx / scale, ty = t.ty / scale
        // No escuro o Vision às vezes "acha" um pulo de metade da foto: isso é erro, a mão não anda tanto
        if abs(tx) > fullExtent.width * 0.08 || abs(ty) > fullExtent.height * 0.08 {
            dlog(String(format: "Alinhamento absurdo (%.0f, %.0f px): quadro usado sem deslocar", tx, ty))
            return { $0 }
        }
        dlog(String(format: "Quadro deslocado %.0f, %.0f px", tx, ty))
        return { $0.transformed(by: CGAffineTransform(translationX: tx, y: ty)) }
    }

    /// Soma em lotes de 3, guardando o parcial em memória de vídeo: nunca há mais de 3 RAW abertos ao mesmo tempo.
    /// Estrela nas luzes: as luzes bem fortes ganham raios, como numa lente fechada em f/11–f/16.
    /// Feito numa versão pequena (os raios são suaves de qualquer jeito) e somado à luz da cena.
    /// NOITE depois de juntar: clareia, tira ruído, tons locais e estrelas nas luzes.
    static func nightFinish(_ merged: CIImage, iso: Float, frameCount: Int, starPoints: Int) -> CIImage {
        let extent = merged.extent
        // ISO alto (pouca luz): tira o ruído colorido e um pouco do granulado; sombra levantada nos tons locais
        let strength = min(1, max(0.25, log2(max(iso, 100) / 200) / 6)) / sqrt(Float(max(frameCount, 1)) / 8)
        dlog(String(format: "Noite: ISO %.0f · redução de ruído %.2f", iso, strength))
        var out = merged
        // O iPhone mede o breu escuro demais: clareia até uma luz de noite (não de dia), até 3 paradas
        let lift = nightLift(out)
        if lift > 0.1 { out = scaled(out, by: exp2(lift)).cropped(to: extent) }
        // Mais claro = mais ruído aparente: a redução acompanha
        let cleanup = min(1, strength + lift * 0.12)
        out = nightDenoise(out, strength: cleanup)
        out = lumaDenoise(out, strength: cleanup)
        // Noite com cara de noite: preto de verdade (sem véu cinza). O "chão" de luz que o ruído e o céu
        // deixam é medido na foto (o mais escuro de uma versão pequena e borrada) e tirado quase todo
        let floor = darkFloor(out)
        // Até 0,06 (era 0,03: no laboratório o chão chegava a 0,044 e o preto ficava cinza)
        let blackPoint = max(0.0035, min(0.06, floor * 0.9))
        dlog(String(format: "Noite: preto em %.4f (chão %.4f)", blackPoint, floor))
        out = out.applyingFilter("CIColorMatrix", parameters: [
            "inputRVector": CIVector(x: CGFloat(1 + blackPoint * 2), y: 0, z: 0, w: 0),
            "inputGVector": CIVector(x: 0, y: CGFloat(1 + blackPoint * 2), z: 0, w: 0),
            "inputBVector": CIVector(x: 0, y: 0, z: CGFloat(1 + blackPoint * 2), w: 0),
            "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
            "inputBiasVector": CIVector(x: CGFloat(-blackPoint), y: CGFloat(-blackPoint), z: CGFloat(-blackPoint), w: 0),
        ]).cropped(to: extent)
        // As sombras sobem pouco
        out = localTone(out, strength: 0.86)
        if starPoints > 0 { out = starBurst(out, points: starPoints, threshold: 1.5 * exp2(lift)) }
        return out
    }

    /// Luz do canto mais escuro (versão pequena e borrada, para um pixel solto não contar).
    /// O "chão" de luz: os 2% mais escuros de uma versão pequena (antes era o mínimo de uma versão borrada, que
    /// apagava galhos e árvores finas e deixava o preto cinza: p1 0,12 no laboratório).
    static func darkFloor(_ scene: CIImage) -> Float {
        let e = scene.extent
        let k = min(1, 256 / max(e.width, e.height))
        let small = scene.transformed(by: CGAffineTransform(translationX: -e.minX, y: -e.minY))
            .transformed(by: CGAffineTransform(scaleX: k, y: k))
        let se = small.extent.integral
        let w = Int(se.width), h = Int(se.height)
        guard w >= 4, h >= 4 else { return 0 }
        var pixels = [Float](repeating: 0, count: w * h * 4)
        context.render(small, toBitmap: &pixels, rowBytes: w * 16, bounds: CGRect(x: 0, y: 0, width: w, height: h),
                       format: .RGBAf, colorSpace: nil)
        var lumas = [Float]()
        lumas.reserveCapacity(w * h)
        for i in stride(from: 0, to: pixels.count, by: 4) {
            let l = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2]
            if l.isFinite { lumas.append(max(0, l)) }
        }
        guard !lumas.isEmpty else { return 0 }
        lumas.sort()
        return lumas[lumas.count / 50]
    }

    /// Quantas paradas clarear a NOITE: leva a luz média (em log, então um poste não engana) até uns −4 EV.
    static func nightLift(_ scene: CIImage) -> Float {
        guard let logLumaKernel else { return 0 }
        let e = scene.extent
        let small = scene.transformed(by: CGAffineTransform(translationX: -e.minX, y: -e.minY))
            .transformed(by: CGAffineTransform(scaleX: 1.0 / 16, y: 1.0 / 16))
        let se = small.extent
        guard se.width >= 4, se.height >= 4, let logL = logLumaKernel.apply(extent: se, arguments: [small]) else { return 0 }
        let average = logL.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: se)])
        var pixel = [Float](repeating: 0, count: 4)
        context.render(average, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                       format: .RGBAf, colorSpace: nil)
        guard pixel[0].isFinite else { return 0 }
        // −3,95 EV (era −4,2): no laboratório a noite saía com luz média 0,16–0,18; o Night Sight fica um pouco mais claro
        let lift = min(3, max(0, -3.95 - pixel[0]))
        dlog(String(format: "Noite: luz média %.1f EV · clareia %.1f paradas", pixel[0], lift))
        return lift
    }

    private static func smallExtentFor(_ e: CGRect, _ k: CGFloat) -> CGRect {
        CGRect(x: e.minX * k, y: e.minY * k, width: e.width * k, height: e.height * k)
    }

    /// Estrela nas luzes, medida nas fotos do iPhone 18 Pro (lente de abertura variável, Austin Mann, Dunton):
    /// - f/2.8–f/4 (6 pontas): um raio em pé e dois a ±60°; raios suaves, fortes no centro e sumindo como a
    ///   difração de verdade (a luz cai com o quadrado da distância); o sol chega a ~14% da largura da foto;
    ///   as pontas puxam para o quente (o vermelho se espalha mais); brilho suave em volta da luz.
    /// - f/1.8 (`points` 18): muitos raios curtos e finos, quase um sol.
    /// Estrela nas fotos de dia: o estourado (perto do branco máximo da foto) e pequeno vira estrela.
    static func dayStar(_ scene: CIImage, points: Int) -> CIImage {
        let e = scene.extent
        let small = scene.transformed(by: CGAffineTransform(translationX: -e.minX, y: -e.minY))
            .transformed(by: CGAffineTransform(scaleX: 1.0 / 8, y: 1.0 / 8))
        let se = small.extent.integral
        guard se.width >= 4, se.height >= 4 else { return scene }
        let maximum = small.applyingFilter("CIAreaMaximum", parameters: [kCIInputExtentKey: CIVector(cgRect: se)])
        var pixel = [Float](repeating: 0, count: 4)
        context.render(maximum, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                       format: .RGBAf, colorSpace: nil)
        let white = max(pixel[0], max(pixel[1], pixel[2]))
        // Sem nada estourado (nem sol nem lâmpada): sem estrela
        guard white.isFinite, white > 0.6 else { return scene }
        return starBurst(scene, points: points, threshold: white * 0.82 / 1.3, compactOnly: true, boost: 26)
    }

    static func starBurst(_ scene: CIImage, points: Int, threshold: Float = 1.5,
                          compactOnly: Bool = false, boost: Float = 1) -> CIImage {
        guard let highlightsKernel, points >= 4 else { return scene }
        let e = scene.extent
        let k: CGFloat = 0.5
        guard let bright = highlightsKernel.apply(extent: e, arguments: [scene, threshold * 1.3]) else { return scene }
        var small = bright.transformed(by: CGAffineTransform(scaleX: k, y: k)).clampedToExtent()
        let smallRect = smallExtentFor(e, k)
        if compactOnly {
            // Só o que é pequeno: tira o que sobrevive a uma "abertura" de 14 px (nuvem, céu, parede clara)
            let opened = small.applyingFilter("CIMorphologyMinimum", parameters: [kCIInputRadiusKey: 14])
                .applyingFilter("CIMorphologyMaximum", parameters: [kCIInputRadiusKey: 14])
            small = (subKernel?.apply(extent: smallRect, arguments: [small, opened]) ?? small).clampedToExtent()
        }
        // De dia o sol chega estourado (a energia de verdade foi cortada): o reforço devolve a força dos raios
        if boost != 1 { small = scaled(small, by: boost).clampedToExtent() }
        // Cada luz vira o ponto do centro dela, com a energia toda: os raios saem desse ponto, finos
        if let peakKernel {
            let r: CGFloat = 6
            let soft = small.applyingGaussianBlur(sigma: Double(r / 2))
            let maxed = soft.applyingFilter("CIMorphologyMaximum", parameters: [kCIInputRadiusKey: r])
            let area = Float(CGFloat.pi * r * r * 0.15)
            // Largura do raio: no iPhone 18 em f/4 o raio é suave e largo (~0,5% da foto); em f/1.8, fino
            let width: Double = points > 8 ? 1.0 : 2.0
            small = (peakKernel.apply(extent: smallRect, arguments: [soft, maxed, area]) ?? small)
                .applyingGaussianBlur(sigma: width).clampedToExtent()
        }
        let side = min(e.width, e.height) * k
        let many = points > 8
        let directions = points / 2
        // Comprimentos dobrando e pesos caindo pela metade: o brilho ao longo do raio cai ~1/r², como na difração
        // Os raios do iPhone 18 vão longe, cada vez mais transparentes: comprimentos dobrando, peso caindo 40%
        let base: CGFloat = many ? 0.007 : 0.009
        let fade: Float = many ? 0.2 : 0.8
        var layers: [(length: CGFloat, weight: Float, warm: Bool)] = []
        var weight: Float = 0.5 * fade
        // De dia (sol) um quinto comprimento: no iPhone 18 os raios do sol chegam a ~14% da foto
        for i in 0..<(compactOnly ? 5 : 4) {
            let length: CGFloat = side * base * CGFloat(1 << i)
            layers.append((length, weight, i >= 2))
            weight *= 0.6
        }
        var neutral = CIImage(color: .black).cropped(to: smallRect)
        var warm = CIImage(color: .black).cropped(to: smallRect)
        for i in 0..<directions {
            // Um raio em pé (como no iPhone 18); na de 18 pontas, um pouco girada para não ficar em grade
            let angle = Double.pi / 2 + Double.pi * Double(i) / Double(directions) + (many ? 0.08 : 0)
            for layer in layers {
                let streak = scaled(small.applyingFilter("CIMotionBlur", parameters: [kCIInputRadiusKey: layer.length,
                                                                                         kCIInputAngleKey: angle])
                    .cropped(to: smallRect), by: layer.weight)
                if layer.warm {
                    warm = streak.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: warm])
                } else {
                    neutral = streak.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: neutral])
                }
            }
        }
        // As pontas longe da luz puxam para o pêssego, como nas fotos do iPhone 18
        let warmed = warm.applyingFilter("CIColorMatrix", parameters: [
            "inputRVector": CIVector(x: 1.0, y: 0, z: 0, w: 0), "inputGVector": CIVector(x: 0, y: 0.84, z: 0, w: 0),
            "inputBVector": CIVector(x: 0, y: 0, z: 0.66, w: 0), "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        ])
        // Brilho suave em volta da luz (a lente nunca é perfeita)
        // Brilho em volta da luz: largo e suave (no iPhone 18 o sol tem um halo grande e claro)
        let glow = scaled(small.applyingGaussianBlur(sigma: Double(side * 0.03)).cropped(to: smallRect), by: compactOnly ? 1.4 : 0.5)
            .applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey:
                scaled(small.applyingGaussianBlur(sigma: Double(side * 0.008)).cropped(to: smallRect), by: 0.3)])
        let rays = warmed.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: neutral])
            .applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: glow])
        let full = rays
            .transformed(by: CGAffineTransform(scaleX: 1 / k, y: 1 / k))
            .cropped(to: e)
        dlog("Noite: estrela de \(points) pontas (como o iPhone 18 em \(many ? "f/1.8" : "f/2.8–f/4"))")
        return full.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: scene]).cropped(to: e)
    }

    /// Ruído de brilho em duas faixas (fina e média): tira o chuvisco sem borrar as bordas fortes.
    static func lumaDenoise(_ scene: CIImage, strength: Float) -> CIImage {
        guard strength > 0.05, let shrinkKernel else { return scene }
        let e = scene.extent
        var out = scene
        for (sigma, k) in [(1.0, 0.05), (2.5, 0.03)] as [(Double, Float)] {
            let blur = out.clampedToExtent().applyingGaussianBlur(sigma: sigma).cropped(to: e)
            out = shrinkKernel.apply(extent: e, arguments: [out, blur, k * strength]) ?? out
        }
        return out
    }

    /// Ruído da noite: o colorido (o pior) some tirando a cor de uma versão borrada e o brilho da original;
    /// o granulado de brilho diminui pouco, para não virar pintura.
    static func nightDenoise(_ scene: CIImage, strength: Float) -> CIImage {
        guard strength > 0.01, let chromaKernel else { return scene }
        let e = scene.extent
        let sigma = Double(2 + 5 * strength)
        let soft = scene.clampedToExtent().applyingGaussianBlur(sigma: sigma).cropped(to: e)
        let chroma = chromaKernel.apply(extent: e, arguments: [scene, soft, min(1, strength * 1.3)]) ?? scene
        return chroma
            .applyingFilter("CINoiseReduction", parameters: ["inputNoiseLevel": 0.005 + 0.03 * Double(strength),
                                                           "inputSharpness": 0.5])
            .cropped(to: e)
    }

    /// NOITE sem fantasma: o primeiro quadro é a referência; os outros só somam onde batem com ela.
    /// Onde algo se mexeu (pessoa, carro, folha), fica a referência (com um pouco mais de ruído ali, sem duplicar).
    private static func robustMerge(count: Int, extent: CGRect, frame: (Int) -> CIImage?) -> CIImage? {
        guard let reference = frame(0) else { return nil }
        guard let robustColorKernel, let robustWeightKernel, let divideKernel, count > 1 else {
            return average(count: count, extent: extent, frame: frame)
        }
        if let merged = twoBandMerge(count: count, extent: extent, reference: reference, frame: frame) { return merged }
        let refBlur = materialize(blurred(reference, extent: extent), extent: extent)
        var sumColor = materialize(reference, extent: extent)
        var sumWeight = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: extent)
        let k: Float = 0.1
        for i in 1..<count {
            // Aberto e alinhado uma vez só: a cor e o peso leem daqui (antes cada um abria o RAW de novo)
            guard let opened = frame(i) else { continue }
            let image = materialize(opened, extent: extent)
            let imageBlur = materialize(blurred(image, extent: extent), extent: extent)
            guard let color = robustColorKernel.apply(extent: extent, arguments: [image, imageBlur, refBlur, k]),
                  let weight = robustWeightKernel.apply(extent: extent, arguments: [imageBlur, refBlur, k]) else { continue }
            sumColor = materialize(add(sumColor, color), extent: extent)
            sumWeight = materialize(add(sumWeight, weight), extent: extent)
        }
        dlog("Noite: quadros juntados só onde nada se mexeu")
        guard let merged = divideKernel.apply(extent: extent, arguments: [sumColor, sumWeight]) else { return nil }
        return materialize(merged, extent: extent)
    }

    /// Junção em duas faixas, como o HDR+ do Google: a parte lisa de cada foto entra quase sempre (tolerância larga),
    /// e o detalhe fino só onde a foto bate com a referência. Onde alguém se mexeu, só o detalhe é recusado:
    /// a região fica com o ruído baixo das 12 fotos, em vez de uma mancha com o ruído de uma foto só.
    private static func twoBandMerge(count: Int, extent: CGRect, reference: CIImage, frame: (Int) -> CIImage?) -> CIImage? {
        guard let robustColorKernel, let robustWeightKernel, let highColorKernel, let subKernel, let divideAddKernel else { return nil }
        let k: Float = 0.1
        // Memória: só o detalhe fica no tamanho cheio. A parte lisa (borrão de 6 px) vive em ¼ do tamanho e a
        // comparação de movimento (borrão de 2,5 px) em ½ — já são borradas, não perdem nada. Antes eram ~15 imagens
        // de 12 MP ao mesmo tempo (~1,5 GB) e o iOS matava o app no meio da NOITE (relatório da 0.26)
        let quarter: CGFloat = 0.25, half: CGFloat = 0.5
        func small(_ s: CGFloat) -> CGRect {
            CGRect(x: 0, y: 0, width: (extent.width * s).rounded(.down), height: (extent.height * s).rounded(.down))
        }
        func shrink(_ image: CIImage, blur: Double, by s: CGFloat) -> CIImage {
            let r = small(s)
            let reduced = image.clampedToExtent().applyingGaussianBlur(sigma: blur).cropped(to: extent)
                .transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY).concatenating(CGAffineTransform(scaleX: s, y: s)))
                .cropped(to: r)
            return materialize(reduced, extent: r)
        }
        func grow(_ image: CIImage, by s: CGFloat) -> CIImage {
            image.clampedToExtent()
                .transformed(by: CGAffineTransform(scaleX: 1 / s, y: 1 / s).concatenating(CGAffineTransform(translationX: extent.minX, y: extent.minY)))
                .cropped(to: extent)
        }
        let ref = materialize(reference, extent: extent)
        let refLow = shrink(ref, blur: 6, by: quarter)
        let refBlur = shrink(ref, blur: 2.5, by: half)
        let refBlurUp = grow(refBlur, by: half)
        guard let refHigh = subKernel.apply(extent: extent, arguments: [ref, grow(refLow, by: quarter)]) else { return nil }
        var lowSum = refLow
        var lowWeight = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: small(quarter))
        var highSum = materialize(refHigh, extent: extent)
        var highWeight = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: small(half))
        for i in 1..<count {
            autoreleasepool {
                guard let opened = frame(i) else { return }
                let image = materialize(opened, extent: extent)
                let imageLow = shrink(image, blur: 6, by: quarter)
                let imageBlur = shrink(image, blur: 2.5, by: half)
                guard let lc = robustColorKernel.apply(extent: small(quarter), arguments: [imageLow, imageLow, refLow, k * 2.5]),
                      let lw = robustWeightKernel.apply(extent: small(quarter), arguments: [imageLow, refLow, k * 2.5]),
                      let hw = robustWeightKernel.apply(extent: small(half), arguments: [imageBlur, refBlur, k]),
                      let hc = highColorKernel.apply(extent: extent, arguments: [image, grow(imageLow, by: quarter),
                                                                                grow(imageBlur, by: half), refBlurUp, k]) else { return }
                lowSum = materialize(add(lowSum, lc), extent: small(quarter))
                lowWeight = materialize(add(lowWeight, lw), extent: small(quarter))
                highWeight = materialize(add(highWeight, hw), extent: small(half))
                highSum = materialize(add(highSum, hc), extent: extent)
            }
        }
        dlog("Noite: junção em duas faixas (liso sempre, detalhe só onde nada se mexeu) · memória livre \(Diagnostics.freeMemory)")
        guard let merged = divideAddKernel.apply(extent: extent, arguments: [grow(lowSum, by: quarter), grow(lowWeight, by: quarter),
                                                                           highSum, grow(highWeight, by: half)]) else { return nil }
        return materialize(merged, extent: extent)
    }

    private static func average(count: Int, extent: CGRect, frame: (Int) -> CIImage?) -> CIImage? {
        var sum: CIImage?
        var used = 0
        for i in 0..<count {
            guard let image = frame(i) else { continue }
            sum = sum.map { add($0, image) } ?? image
            used += 1
            if used % 3 == 0, let partial = sum { sum = materialize(partial, extent: extent) }
        }
        guard let sum, used > 0 else { return nil }
        let k = CGFloat(1) / CGFloat(used)
        let mean = sum.applyingFilter("CIColorMatrix", parameters: [
            "inputRVector": CIVector(x: k, y: 0, z: 0, w: 0),
            "inputGVector": CIVector(x: 0, y: k, z: 0, w: 0),
            "inputBVector": CIVector(x: 0, y: 0, z: k, w: 0),
            "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        ])
        return materialize(mean, extent: extent)
    }

    private static func sharpness(_ image: CIImage) -> CIImage? {
        let laplacian = image.applyingFilter("CIConvolution3X3", parameters: [
            "inputWeights": CIVector(values: [0, 1, 0, 1, -4, 1, 0, 1, 0], count: 9),
            "inputBias": 0,
        ])
        guard let s = sharpnessKernel?.apply(extent: image.extent, arguments: [laplacian]) else { return nil }
        return s.clampedToExtent().applyingGaussianBlur(sigma: 6).cropped(to: image.extent)
    }

    private static func focusMerge(count: Int, extent: CGRect, frame: (Int) -> CIImage?) -> CIImage? {
        guard let first = frame(0), let firstSharpness = sharpness(first), let pickKernel else { return nil }
        var result = materialize(first, extent: extent)
        var resultSharpness = materialize(firstSharpness, extent: extent)
        for i in 1..<max(count, 1) {
            guard let image = frame(i), let s = sharpness(image),
                  let mask = pickKernel.apply(extent: extent, arguments: [s, resultSharpness]) else { continue }
            let softMask = mask.clampedToExtent().applyingGaussianBlur(sigma: 2).cropped(to: extent)
            let blended = image.applyingFilter("CIBlendWithMask", parameters: [
                kCIInputBackgroundImageKey: result,
                kCIInputMaskImageKey: softMask,
            ])
            let maxSharpness = s.applyingFilter("CIMaximumCompositing", parameters: [kCIInputBackgroundImageKey: resultSharpness])
            result = materialize(blended, extent: extent)
            resultSharpness = materialize(maxSharpness, extent: extent)
        }
        return result
    }

    /// Calcula a imagem agora e guarda num buffer de meia precisão, para soltar tudo que veio antes.
    static func materialize(_ image: CIImage, extent: CGRect) -> CIImage {
        let w = Int(extent.width), h = Int(extent.height)
        var buffer: CVPixelBuffer?
        let attributes: [CFString: Any] = [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any],
                                           kCVPixelBufferMetalCompatibilityKey: true]
        guard CVPixelBufferCreate(nil, w, h, kCVPixelFormatType_64RGBAHalf, attributes as CFDictionary, &buffer) == kCVReturnSuccess,
              let buffer else { return image }
        let shifted = image.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
        context.render(shifted, to: buffer, bounds: CGRect(x: 0, y: 0, width: w, height: h), colorSpace: linearP3)
        return CIImage(cvPixelBuffer: buffer, options: [.colorSpace: linearP3])
            .transformed(by: CGAffineTransform(translationX: extent.minX, y: extent.minY))
    }

    static func add(_ a: CIImage, _ b: CIImage) -> CIImage {
        addKernel?.apply(extent: a.extent, arguments: [a, b])
            ?? b.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: a])
    }

    // MARK: - HDR

    /// Junta os quadros do bracketing (escuro, normal, claro): cada pixel vem dos quadros em que não estourou
    /// nem ficou escuro demais, todos trazidos para a mesma exposição.
    static func hdr(_ frames: [CapturedFrame], options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        let sorted = frames.sorted { $0.exposureBias < $1.exposureBias }
        guard let reference = sorted.min(by: { abs($0.exposureBias) < abs($1.exposureBias) }),
              let refImage = hdrImage(reference), let hdrColorKernel, let hdrWeightKernel, let divideKernel else { return nil }
        let extent = refImage.extent
        dlog("HDR: \(sorted.count) quadros (\(sorted.map { String(format: "%+.0f", $0.exposureBias) }.joined(separator: " ")) EV) · \(Int(extent.width))×\(Int(extent.height))")

        // Alinha cada quadro (já trazido para a exposição normal) com o de referência
        let small: Float = 0.25
        guard let refSmall = hdrImage(reference, scale: small) else { return nil }
        let refBlur = materialize(blurred(refImage, extent: extent), extent: extent)
        var sumColor: CIImage?
        var sumWeight: CIImage?
        for (index, frame) in sorted.enumerated() {
            let gain = Float(pow(2.0, Double(-frame.exposureBias)))
            guard let image = hdrImage(frame) else { continue }
            var aligned = image
            let isReference = frame.exposureBias == reference.exposureBias
            if !isReference, let smallImage = hdrImage(frame, scale: small) {
                let warp = alignment(of: scaled(smallImage, by: gain), to: refSmall, scale: CGFloat(small),
                                     fullExtent: extent, homography: false)
                aligned = warp(image).cropped(to: extent)
            }
            // O mais escuro e o de referência sempre contam um pouco (o escuro é o único com detalhe no estourado)
            let floor: Float = index == 0 ? 0.01 : (isReference ? 0.02 : 0)
            let color: CIImage?, weight: CIImage?
            if !isReference, let hdrGhostColorKernel, let hdrGhostWeightKernel {
                // Sem fantasma: onde algo se mexeu entre as fotos, fica só o quadro de referência
                let frameBlur = blurred(aligned, extent: extent)
                let k: Float = 0.12
                color = hdrGhostColorKernel.apply(extent: extent, arguments: [aligned, frameBlur, refBlur, gain, floor, k])
                weight = hdrGhostWeightKernel.apply(extent: extent, arguments: [aligned, frameBlur, refBlur, gain, floor, k])
            } else {
                color = hdrColorKernel.apply(extent: extent, arguments: [aligned, gain, floor])
                weight = hdrWeightKernel.apply(extent: extent, arguments: [aligned, floor])
            }
            guard let color, let weight else { continue }
            sumColor = materialize(sumColor.map { add($0, color) } ?? color, extent: extent)
            sumWeight = materialize(sumWeight.map { add($0, weight) } ?? weight, extent: extent)
        }
        guard let sumColor, let sumWeight,
              var merged = divideKernel.apply(extent: extent, arguments: [sumColor, sumWeight]) else { return nil }
        // Devolve a exposição de base do DNG normal (tirada para alinhar o branco dos quadros)
        if reference.isRaw, let raw = CIRAWFilter(imageData: reference.data, identifierHint: "com.adobe.raw-image") {
            merged = scaled(merged, by: Float(pow(2.0, Double(raw.baselineExposure))))
        }
        merged = materialize(merged, extent: extent)
        merged = localTone(merged, strength: 0.62)
        var hdrOptions = options
        hdrOptions.hdrCompress = true
        let output = finish(merged.settingProperties(refImage.properties), options: hdrOptions)
        dlog("HDR revelado: \(Diagnostics.ms(since: t0))\(output == nil ? " · FALHOU" : "")")
        return output
    }

    /// Versão levemente borrada, para comparar quadros sem confundir ruído com movimento.
    static func blurred(_ image: CIImage, extent: CGRect) -> CIImage {
        image.clampedToExtent().applyingGaussianBlur(sigma: 2.5).cropped(to: extent)
    }

    /// Tons locais: cada região tem a "luz de fundo" puxada para perto da média (céu desce, sombra sobe)
    /// e o detalhe fica. Calculado numa versão pequena: a luz de fundo é borrada de qualquer jeito.
    /// `preview`: a mesma foto já pequena (RAW aberto em 1/8, rápido). Sem ela, a cena é reduzida aqui; com ela,
    /// o RAW grande é aberto uma vez só (antes abria três vezes e a foto levava 7 s para revelar).
    /// Luz média (log2) da última cena que passou pelos tons locais (para a cor acompanhar a luz).
    private static var lastKey: Float = -4

    static func localTone(_ scene: CIImage, strength: Float, preview: CIImage? = nil, keyPull: Float = 0,
                          highlightBoost: Float = 0) -> CIImage {
        guard let logLumaKernel, let localToneKernel else { return scene }
        let e = scene.extent
        let source = preview ?? scene.transformed(by: CGAffineTransform(scaleX: 0.125, y: 0.125))
        let se = source.extent
        guard se.width >= 8, se.height >= 8,
              let logL = logLumaKernel.apply(extent: se, arguments: [source]) else { return scene }
        // Guardado pequeno na memória: o borrão e a média leem daqui, sem abrir a foto de novo
        let small = materialize(logL, extent: se)
            .transformed(by: CGAffineTransform(translationX: -se.minX, y: -se.minY))
        let smallExtent = CGRect(origin: .zero, size: se.size)
        // Duas larguras de borrão misturadas: menos auréola nas bordas fortes
        let short = min(smallExtent.width, smallExtent.height)
        let wide = small.clampedToExtent().applyingGaussianBlur(sigma: Double(short * 0.06)).cropped(to: smallExtent)
        let tight = small.clampedToExtent().applyingGaussianBlur(sigma: Double(short * 0.015)).cropped(to: smallExtent)
        let mixedSmall = tight.applyingFilter("CIDissolveTransition", parameters: [kCIInputTargetImageKey: wide, kCIInputTimeKey: 0.5])
        let base = materialize(mixedSmall, extent: smallExtent).clampedToExtent()
            .transformed(by: CGAffineTransform(scaleX: e.width / smallExtent.width, y: e.height / smallExtent.height))
            .transformed(by: CGAffineTransform(translationX: e.minX, y: e.minY))
            .cropped(to: e)
        let average = small.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: smallExtent)])
        var pixel = [Float](repeating: 0, count: 4)
        context.render(average, toBitmap: &pixel, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                       format: .RGBAf, colorSpace: nil)
        dlog(String(format: "Tons locais: luz média %.2f EV · força %.2f", pixel[0], 1 - strength))
        if pixel[0].isFinite { lastKey = pixel[0] }
        let t = tuning
        let shadow = max(0.3, 1 - (1 - strength) * t.shadowRatio)
        let high = min(1, 1 - (1 - strength) * t.highlightRatio)
        // Foto de um quadro: aproxima a luz média de −3 EV (a medição do iPhone deixa a foto escura demais)
        let shift = keyPull > 0 ? min(0.8, max(-0.5, (-3.0 - pixel[0]) * keyPull)) : 0
        if shift != 0 { dlog(String(format: "Tons locais: ajuste de luz %+.2f EV", shift)) }
        // Detalhe ×1,08; nas fotos bem grandes (48 MP) ×1,04: lá o realce já é mais fino e dava borda 1,31× a da Apple
        let detail: CGFloat = max(e.width, e.height) > 5000 ? 1.04 : 1.08
        let shape = CIVector(x: CGFloat(shadow), y: CGFloat(high), z: detail, w: CGFloat(shift))
        return localToneKernel.apply(extent: e, arguments: [scene, base, pixel[0], shape, highlightBoost]) ?? scene
    }

    private static func hdrImage(_ frame: CapturedFrame, scale: Float = 1) -> CIImage? {
        if let decodeOverride, let image = decodeOverride(frame, scale) { return image }
        return frame.isRaw ? linear(dng: frame.data, scale: scale, neutralExposure: true) : processed(frame.data, scale: scale)
    }

    static func scaled(_ image: CIImage, by k: Float) -> CIImage {
        let v = CGFloat(k)
        return image.applyingFilter("CIColorMatrix", parameters: [
            "inputRVector": CIVector(x: v, y: 0, z: 0, w: 0),
            "inputGVector": CIVector(x: 0, y: v, z: 0, w: 0),
            "inputBVector": CIVector(x: 0, y: 0, z: v, w: 0),
            "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        ])
    }

    // MARK: - Retrato com desfoque

    /// HEIC com mapa de profundidade: borra o fundo conforme a distância até o plano em foco.
    /// `aperture` imita a abertura de uma lente (f/1.4 borra muito, f/16 quase nada).
    /// `focusPoint`: onde está o rosto (0…1, origem em cima à esquerda); nil = centro.
    static func developPortrait(_ data: Data, aperture: Float, focusPoint: CGPoint?, options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        guard let scene = portraitScene(data, aperture: aperture, focusPoint: focusPoint) else { return nil }
        let output = finish(scene, options: options)
        dlog(String(format: "Retrato revelado f/%.1f: ", aperture) + Diagnostics.ms(since: t0) + (output == nil ? " · FALHOU" : ""))
        return output
    }

    /// Retrato -> luz de cena já com o fundo desfocado. `scale` < 1 para a prévia na tela.
    static func portraitScene(_ data: Data, aperture: Float, focusPoint: CGPoint?, scale: CGFloat = 1) -> CIImage? {
        guard let raw = CIImage(data: data) else { return nil }
        let orientationValue = (raw.properties[kCGImagePropertyOrientation as String] as? NSNumber)?.uint32Value ?? 1
        let orientation = CGImagePropertyOrientation(rawValue: orientationValue) ?? .up
        func upright(_ image: CIImage) -> CIImage {
            let o = image.oriented(orientation)
            return o.transformed(by: CGAffineTransform(translationX: -o.extent.minX, y: -o.extent.minY))
        }
        var image = upright(raw)
        if scale < 1 { image = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale)) }
        let extent = image.extent
        var properties = raw.properties
        properties[kCGImagePropertyOrientation as String] = nil

        guard let disparityRaw = CIImage(data: data, options: [.auxiliaryDisparity: true]), let blurMapKernel else {
            dlog("Retrato: a foto veio sem profundidade; revelando sem desfoque")
            let scene = toSceneKernel?.apply(extent: extent, arguments: [image, tuning.filmicGain]) ?? image
            return scene.settingProperties(properties)
        }
        func fit(_ aux: CIImage) -> CIImage {
            let a = upright(aux)
            return a.transformed(by: CGAffineTransform(scaleX: extent.width / a.extent.width, y: extent.height / a.extent.height))
                .cropped(to: extent)
        }
        let disparity = fit(disparityRaw)
        var matte = CIImage(data: data, options: [.auxiliaryPortraitEffectsMatte: true]).map(fit)
            ?? CIImage(color: .black).cropped(to: extent)
        // Cabelo e óculos têm máscaras próprias, bem mais finas: entram junto para não borrar fio de cabelo
        for option in [CIImageOption.auxiliarySemanticSegmentationHairMatte, .auxiliarySemanticSegmentationGlassesMatte] {
            if let extra = CIImage(data: data, options: [option: true]).map(fit), let maxKernel {
                matte = maxKernel.apply(extent: extent, arguments: [matte, extra]) ?? matte
            }
        }
        // Qualquer coisa em primeiro plano (roupa, objeto, planta, bicho), não só pessoa: o recorte do iOS protege o assunto
        if let subject = subjectMask(image, focus: focusPoint ?? CGPoint(x: 0.5, y: 0.5)), let maxKernel {
            matte = maxKernel.apply(extent: extent, arguments: [matte, subject]) ?? matte
        }

        // Profundidade do plano em foco: média num quadradinho em volta do rosto (ou do centro)
        let p = focusPoint ?? CGPoint(x: 0.5, y: 0.45)
        let box = CGRect(x: p.x * extent.width - extent.width * 0.05, y: (1 - p.y) * extent.height - extent.width * 0.05,
                         width: extent.width * 0.1, height: extent.width * 0.1).intersection(extent)
        let average = disparity.applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: box)])
        var pixel = [Float](repeating: 0, count: 4)
        // O pixel da média fica na origem do quadradinho, não em (0, 0)
        context.render(average, toBitmap: &pixel, rowBytes: 16, bounds: average.extent,
                       format: .RGBAf, colorSpace: nil)
        let focus = pixel[0]

        let strength = Float(2.8 / max(aperture, 0.7)) * 3
        let radius = min(extent.width, extent.height) * 0.014 * CGFloat(2.8 / max(aperture, 0.7))
        guard let map = blurMapKernel.apply(extent: extent, arguments: [disparity, matte, focus, strength]) else { return nil }
        let sharp = toSceneKernel?.apply(extent: extent, arguments: [image, tuning.filmicGain]) ?? image
        let scene = bokeh(sharp, map: map, radius: radius, extent: extent)
        if scale >= 1 { dlog(String(format: "Retrato: f/%.1f · foco na disparidade %.2f · bokeh até %.0f px", aperture, focus, radius)) }
        return scene.settingProperties(properties)
    }

    /// Recorte do assunto pelo iOS (VNGenerateForegroundInstanceMaskRequest). Com um ponto escolhido,
    /// fica só o objeto que está nele; sem ponto, tudo o que está em primeiro plano.
    static func subjectMask(_ image: CIImage, focus: CGPoint?) -> CIImage? {
        let e = image.extent
        let s = min(1, 1024 / max(e.width, e.height))
        let small = image
            .transformed(by: CGAffineTransform(translationX: -e.minX, y: -e.minY))
            .transformed(by: CGAffineTransform(scaleX: s, y: s))
        let request = VNGenerateForegroundInstanceMaskRequest()
        let handler = VNImageRequestHandler(ciImage: small, options: [:])
        guard (try? handler.perform([request])) != nil, let result = request.results?.first,
              !result.allInstances.isEmpty else { return nil }
        var instances = result.allInstances
        if let focus {
            // Qual objeto está no ponto (o mapa de rótulos começa em cima à esquerda)
            let labels = result.instanceMask
            CVPixelBufferLockBaseAddress(labels, .readOnly)
            if let base = CVPixelBufferGetBaseAddress(labels) {
                let w = CVPixelBufferGetWidth(labels), h = CVPixelBufferGetHeight(labels)
                let x = min(max(Int(focus.x * CGFloat(w)), 0), w - 1), y = min(max(Int(focus.y * CGFloat(h)), 0), h - 1)
                let label = Int((base + y * CVPixelBufferGetBytesPerRow(labels)).assumingMemoryBound(to: UInt8.self)[x])
                if label != 0, result.allInstances.contains(label) { instances = IndexSet(integer: label) }
            }
            CVPixelBufferUnlockBaseAddress(labels, .readOnly)
        }
        guard let buffer = try? result.generateScaledMaskForImage(forInstances: instances, from: handler) else { return nil }
        let mask = CIImage(cvPixelBuffer: buffer)
        dlog("Retrato: assunto recortado pelo iOS (\(instances.count) objeto(s))")
        return mask
            .transformed(by: CGAffineTransform(scaleX: e.width / mask.extent.width, y: e.height / mask.extent.height))
            .transformed(by: CGAffineTransform(translationX: e.minX, y: e.minY))
            .cropped(to: e)
    }

    /// Mapa de quanto borrar, para o visor (mesma conta da foto final).
    static func blurMap(disparity: CIImage, matte: CIImage, focus: Float, strength: Float) -> CIImage? {
        blurMapKernel?.apply(extent: disparity.extent, arguments: [disparity, matte, focus, strength])
    }

    /// Bokeh rápido para o visor: duas camadas em um quarto da resolução (a 30 quadros por segundo).
    static func liveBokeh(_ image: CIImage, map: CIImage, radius: CGFloat) -> CIImage {
        guard let bandKernel, radius > 1 else { return image }
        let e = image.extent
        let k: CGFloat = 0.25
        let small = image.transformed(by: CGAffineTransform(scaleX: k, y: k)).clampedToExtent()
        var result = image
        var lower: Float = 0
        for level in [Float(0.5), 1.0] {
            let r = radius * CGFloat(level) * k
            let layer = small
                .cropped(to: CGRect(x: e.minX * k - r * 2, y: e.minY * k - r * 2, width: e.width * k + r * 4, height: e.height * k + r * 4))
                .applyingFilter("CIBokehBlur", parameters: [kCIInputRadiusKey: r, "inputRingAmount": 0.1, "inputSoftness": 1.0])
                .transformed(by: CGAffineTransform(scaleX: 1 / k, y: 1 / k))
                .cropped(to: e)
            guard let mask = bandKernel.apply(extent: e, arguments: [map, lower, level]) else { continue }
            result = layer.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: result, kCIInputMaskImageKey: mask])
            lower = level
        }
        return result.cropped(to: e)
    }

    /// Bokeh de lente: o fundo borrado com o formato da abertura (disco), em luz de cena, então cada
    /// pontinho de luz vira uma bolinha clara. Quatro camadas de desfoque misturadas pelo mapa de profundidade.
    static func bokeh(_ scene: CIImage, map: CIImage, radius: CGFloat, extent: CGRect) -> CIImage {
        guard let bandKernel, radius > 1 else { return scene }
        var result = scene
        var lower: Float = 0
        for level in [Float(0.2), 0.45, 0.7, 1.0] {
            let r = radius * CGFloat(level)
            // Desfoques grandes em meia resolução: o resultado é borrado de qualquer jeito
            let k: CGFloat = r > 14 ? 0.5 : 1
            let smallExtent = CGRect(x: 0, y: 0, width: extent.width * k, height: extent.height * k)
            // Só o que é fundo entra no borrão (com alfa), e depois divide pelo alfa borrado: a cor da pessoa
            // não vaza para o fundo (antes ficava um halo da roupa/pele em volta do recorte)
            // (a primeira camada, quase nítida, usa a cena inteira: ela cobre também a borda da pessoa)
            let weighted = lower > 0.01 ? bokehSourceKernel?.apply(extent: extent, arguments: [scene, map, lower * 0.5]) : nil
            let layer = (weighted ?? scene)
                .transformed(by: CGAffineTransform(scaleX: k, y: k))
                .clampedToExtent()
                .cropped(to: smallExtent.insetBy(dx: -r * k * 2, dy: -r * k * 2))
                .applyingFilter("CIBokehBlur", parameters: [
                    kCIInputRadiusKey: r * k,
                    "inputRingAmount": 0.12,
                    "inputRingSize": 0.08,
                    "inputSoftness": 1.0,
                ])
                .applyingFilter("CIUnpremultiply")
                .settingAlphaOne(in: smallExtent.insetBy(dx: -r * k * 2, dy: -r * k * 2))
                .transformed(by: CGAffineTransform(scaleX: 1 / k, y: 1 / k))
                .cropped(to: extent)
            guard let mask = bandKernel.apply(extent: extent, arguments: [map, lower, level]) else { continue }
            result = layer.applyingFilter("CIBlendWithMask", parameters: [
                kCIInputBackgroundImageKey: result,
                kCIInputMaskImageKey: mask,
            ])
            lower = level
        }
        return result.cropped(to: extent)
    }

    // MARK: - Visor

    struct PreviewOptions {
        var develop = DevelopOptions()
        var zebra = false
        var peaking = false
        var falseColor = false
    }

    /// Aplica o look ao vídeo do visor, para ver o resultado antes de fotografar.
    static func preview(_ image: CIImage, options: PreviewOptions) -> CIImage {
        let scene = toSceneKernel?.apply(extent: image.extent, arguments: [image, tuning.filmicGain]) ?? image
        var out = grade(scene, look: options.develop.params, zebra: options.zebra)
        if options.falseColor, let falseColorKernel {
            out = falseColorKernel.apply(extent: out.extent, arguments: [out]) ?? out
        }
        if options.peaking, let peakingKernel {
            let edges = image.applyingFilter("CIEdges", parameters: [kCIInputIntensityKey: 3.0])
            out = peakingKernel.apply(extent: image.extent, arguments: [out, edges, 0.18]) ?? out
        }
        return out
    }

    private static func vector(_ v: SIMD3<Float>) -> CIVector {
        CIVector(x: CGFloat(v.x), y: CGFloat(v.y), z: CGFloat(v.z))
    }

    private static func thumbnail(of image: CIImage) -> UIImage? {
        let scale = 400 / max(image.extent.width, image.extent.height)
        let small = image.samplingLinear().transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        guard let cg = context.createCGImage(small, from: small.extent, format: .RGBA8, colorSpace: displayP3) else { return nil }
        return UIImage(cgImage: cg)
    }
}
