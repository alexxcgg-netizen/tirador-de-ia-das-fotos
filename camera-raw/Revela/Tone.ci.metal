#include <CoreImage/CoreImage.h>
using namespace metal;

namespace revela {
    constant float3 kLuma = float3(0.2126f, 0.7152f, 0.0722f);
    constant float kA = 2.51f, kB = 0.03f, kC = 2.43f, kD = 0.59f, kE = 0.14f;

    // Curva fílmica (aproximação ACES de Narkowicz): cena linear -> display linear
    inline float3 filmic(float3 x) {
        return clamp((x * (kA * x + kB)) / (x * (kC * x + kD) + kE), 0.0f, 1.0f);
    }

    // HDR: peso de cada pixel de um quadro (evita o estourado e o muito escuro, que tem ruído)
    inline float hdrWeight(float3 c, float floorWeight) {
        float peak = max(c.r, max(c.g, c.b));
        float l = dot(c, kLuma);
        float w = (1.0f - smoothstep(0.75f, 0.97f, peak)) * smoothstep(0.0f, 0.04f, l);
        return max(w, floorWeight);
    }

    // Quanto um quadro "bate" com a referência (1 = igual, 0 = algo se mexeu).
    // A tolerância cresce com a raiz da luz (o ruído do sensor cresce assim). Referência estourada: sempre 1.
    inline float ghost(float3 frame, float3 ref, float k) {
        float rp = max(ref.r, max(ref.g, ref.b));
        if (rp > 0.85f) return 1.0f;
        float d = abs(dot(frame - ref, kLuma));
        float sigma = k * sqrt(max(dot(ref, kLuma), 0.0005f)) + 0.004f;
        float x = d / sigma;
        return exp(-0.5f * x * x);
    }

    // Inversa da curva: estima a luz da cena a partir de uma imagem já com curva (vídeo, HEIC)
    inline float3 inverseFilmic(float3 v) {
        float3 x = clamp(v, 0.0f, 0.985f);
        float3 A = x * kC - kA;
        float3 B = x * kD - kB;
        float3 C = x * kE;
        float3 D = sqrt(max(B * B - 4.0f * A * C, 0.0f));
        return (-B - D) / (2.0f * A);
    }
}

extern "C" {
namespace coreimage {
    // Vídeo do visor ou HEIC da Apple -> luz linear de cena (aproximada)
    float4 revelaToScene(sample_t s) {
        return float4(revela::inverseFilmic(s.rgb) / 0.8f, 1.0f);
    }

    // Altas luzes da cena, para o halation e o bloom
    float4 revelaHighlights(sample_t s, float threshold) {
        float3 c = max(s.rgb, float3(0.0f));
        float l = dot(c, revela::kLuma);
        float k = max(l - threshold, 0.0f) / max(l, 1e-4f);
        return float4(c * k, 1.0f);
    }

    // A revelação: luz de cena -> look de filme -> display linear.
    //   mat*: mistura de canais (como os corantes de cada filme reagem às cores)
    //   slope/offset/power: curva de cada cor (ASC CDL), aplicada depois da curva fílmica
    //   frame: x, y, largura, altura da imagem (para a vinheta)
    float4 revelaTone(sample_t s, sample_t n,
                      float exposure, float saturation, float mono, float toe, float contrast, float grain,
                      float3 matR, float3 matG, float3 matB,
                      float3 slope, float3 offset, float3 power,
                      float3 shadowTint, float3 highTint,
                      float vignette, float4 frame, float zebraThreshold,
                      destination dest) {
        float3 scene = max(s.rgb, float3(0.0f)) * exp2(exposure);
        float peak = max(scene.r, max(scene.g, scene.b));

        float3 c = float3(dot(matR, scene), dot(matG, scene), dot(matB, scene));
        c = max(c, float3(0.0f));
        float l = dot(c, revela::kLuma);
        c = mix(float3(l), c, saturation);
        c = mix(c, float3(l), mono);
        c = max(c, float3(1e-6f));

        // Contraste em escala logarítmica, ancorado no cinza médio (18%)
        c = 0.18f * pow(c / 0.18f, float3(contrast));

        float3 t = revela::filmic(c * 0.8f);
        t = toe + (1.0f - toe) * t;
        t = pow(max(t * slope + offset, float3(0.0f)), power);

        // Split toning: uma cor nas sombras, outra nas altas luzes
        float tl = dot(t, revela::kLuma);
        float sw = (1.0f - tl) * (1.0f - tl);
        t += shadowTint * sw * sw + highTint * tl * tl;
        t = max(t, float3(0.0f));

        // Vinheta: cantos mais escuros, como numa lente antiga
        float2 p = (dest.coord() - (frame.xy + frame.zw * 0.5f)) / (frame.zw * 0.5f);
        float r = length(p) / 1.4142f;
        t *= 1.0f - vignette * smoothstep(0.35f, 1.0f, r);

        // Grão mais forte nos meios-tons, como em filme
        tl = dot(t, revela::kLuma);
        t += (n.r - 0.5f) * grain * 4.0f * tl * (1.0f - tl);
        t = clamp(t, 0.0f, 1.0f);

        // Zebra (só no visor): listras onde a luz estourou
        if (zebraThreshold > 0.0f && peak > zebraThreshold) {
            float2 q = dest.coord();
            float stripe = fmod(q.x + q.y, 18.0f) < 9.0f ? 1.0f : 0.0f;
            t = mix(t, float3(stripe), 0.55f);
        }
        return float4(t, 1.0f);
    }

    // Focus peaking: pinta de âmbar as bordas que estão em foco
    float4 revelaPeaking(sample_t image, sample_t edges, float threshold) {
        float e = dot(edges.rgb, revela::kLuma);
        float k = smoothstep(threshold, threshold * 1.6f, e);
        return float4(mix(image.rgb, float3(1.0f, 0.62f, 0.16f), k), image.a);
    }

    // Empilhamento de foco: nitidez local = |laplaciano| da luminância
    float4 revelaSharpness(sample_t laplacian) {
        float s = abs(dot(laplacian.rgb, revela::kLuma));
        return float4(s, s, s, 1.0f);
    }

    // 1 onde o quadro novo é mais nítido que o resultado acumulado
    float4 revelaPick(sample_t candidate, sample_t current) {
        float m = candidate.r > current.r * 1.05f ? 1.0f : 0.0f;
        return float4(m, m, m, 1.0f);
    }

    // Soma simples (alfa sempre 1, para a média e o HDR não acumularem alfa)
    float4 revelaAdd(sample_t a, sample_t b) {
        return float4(a.rgb + b.rgb, 1.0f);
    }

    // HDR: cor do quadro trazida para a exposição normal (gain) e multiplicada pelo peso
    float4 revelaHDRColor(sample_t s, float gain, float floorWeight) {
        float3 c = max(s.rgb, float3(0.0f));
        return float4(c * gain * revela::hdrWeight(c, floorWeight), 1.0f);
    }

    float4 revelaHDRWeight(sample_t s, float floorWeight) {
        float w = revela::hdrWeight(max(s.rgb, float3(0.0f)), floorWeight);
        return float4(w, w, w, 1.0f);
    }

    // HDR sem fantasma: o quadro (já na exposição normal) só conta onde bate com o de referência.
    // Onde a referência estourou não dá para comparar: aí o quadro escuro manda.
    float4 revelaHDRGhostColor(sample_t s, sample_t sBlur, sample_t refBlur, float gain, float floorWeight, float k) {
        float3 c = max(s.rgb, float3(0.0f));
        float g = revela::ghost(max(sBlur.rgb, float3(0.0f)) * gain, max(refBlur.rgb, float3(0.0f)), k);
        return float4(c * gain * revela::hdrWeight(c, floorWeight) * g, 1.0f);
    }

    float4 revelaHDRGhostWeight(sample_t s, sample_t sBlur, sample_t refBlur, float gain, float floorWeight, float k) {
        float g = revela::ghost(max(sBlur.rgb, float3(0.0f)) * gain, max(refBlur.rgb, float3(0.0f)), k);
        float w = revela::hdrWeight(max(s.rgb, float3(0.0f)), floorWeight) * g;
        return float4(w, w, w, 1.0f);
    }

    // NOITE sem fantasma: cada quadro conta menos onde difere da referência (algo se mexeu).
    float4 revelaRobustColor(sample_t s, sample_t sBlur, sample_t refBlur, float k) {
        float g = revela::ghost(max(sBlur.rgb, float3(0.0f)), max(refBlur.rgb, float3(0.0f)), k);
        return float4(max(s.rgb, float3(0.0f)) * g, 1.0f);
    }

    float4 revelaRobustWeight(sample_t sBlur, sample_t refBlur, float k) {
        float g = revela::ghost(max(sBlur.rgb, float3(0.0f)), max(refBlur.rgb, float3(0.0f)), k);
        return float4(g, g, g, 1.0f);
    }

    // Tons locais: log da luminância (para borrar e achar a "luz de fundo" de cada região)
    float4 revelaLogLuma(sample_t s) {
        float l = log2(max(dot(max(s.rgb, float3(0.0f)), revela::kLuma), 1e-5f));
        return float4(l, l, l, 1.0f);
    }

    // Tons locais: aproxima a luz de fundo de cada região da média (strength < 1) e mantém o detalhe.
    float4 revelaLocalTone(sample_t s, sample_t base, float mean, float strength) {
        float3 c = max(s.rgb, float3(0.0f));
        float lg = log2(max(dot(c, revela::kLuma), 1e-5f));
        float b = base.r;
        float target = mean + (b - mean) * strength + (lg - b) * 1.08f;
        return float4(c * exp2(clamp(target - lg, -3.0f, 3.0f)), 1.0f);
    }

    float4 revelaDivide(sample_t sum, sample_t weight) {
        return float4(sum.rgb / max(weight.r, 1e-4f), 1.0f);
    }

    // Panorama: projeta a foto num cilindro (girar a câmera vira só deslizar para o lado).
    float2 revelaCylinder(float f, float2 center, destination dest) {
        float2 d = dest.coord() - center;
        float theta = d.x / f;
        return center + float2(f * tan(theta), d.y / cos(theta));
    }

    // Super resolução: alinhamento por regiões. Desloca cada ponto pelo que sobrou do alinhamento geral,
    // misturando os 9 pedaços (grade 3×3 com centros em x0 + i·dx, y0 + j·dy).
    float2 revelaGridWarp(float4 a, float4 b, float4 c, float4 d, float2 e, float4 grid, destination dest) {
        float2 o[9] = { a.xy, a.zw, b.xy, b.zw, c.xy, c.zw, d.xy, d.zw, e };
        float2 p = dest.coord();
        float u = clamp((p.x - grid.x) / grid.z, 0.0f, 2.0f);
        float v = clamp((p.y - grid.y) / grid.w, 0.0f, 2.0f);
        int i = min(int(u), 1), j = min(int(v), 1);
        float fu = u - float(i), fv = v - float(j);
        float2 bottom = mix(o[j * 3 + i], o[j * 3 + i + 1], fu);
        float2 top = mix(o[(j + 1) * 3 + i], o[(j + 1) * 3 + i + 1], fu);
        return p - mix(bottom, top, fv);
    }

    // Desconvolução (Richardson–Lucy): quanto a imagem observada difere da estimativa borrada
    float4 revelaRatio(sample_t observed, sample_t blurred) {
        float3 r = max(observed.rgb, float3(0.0f)) / max(blurred.rgb, float3(1e-4f));
        return float4(clamp(r, 0.6f, 1.6f), 1.0f);
    }

    float4 revelaMultiply(sample_t a, sample_t b) {
        return float4(max(a.rgb, float3(0.0f)) * b.rgb, 1.0f);
    }

    // Documento: página ÷ papel (a página sem o texto) = papel branco por igual, sem sombra.
    float4 revelaPaper(sample_t page, sample_t paper) {
        return float4(clamp(page.rgb / max(paper.rgb, float3(0.04f)), 0.0f, 1.0f), 1.0f);
    }

    // Retrato: quanto borrar cada ponto, pela distância até o plano em foco.
    // A máscara de pessoa (matte) protege o rosto e o cabelo.
    float4 revelaBlurMap(sample_t disparity, sample_t matte, float focus, float strength) {
        float v = clamp(abs(disparity.r - focus) * strength, 0.0f, 1.0f) * (1.0f - matte.r);
        return float4(v, v, v, 1.0f);
    }

    // Bokeh em camadas: quanto desta camada entra (0 abaixo de lo, 1 acima de hi)
    float4 revelaBand(sample_t m, float lo, float hi) {
        float v = clamp((m.r - lo) / max(hi - lo, 1e-4f), 0.0f, 1.0f);
        return float4(v, v, v, 1.0f);
    }

    // Proteção de pele: onde a cena original tem cor de pele, o look forte dá lugar à versão neutra
    float4 revelaSkinMix(sample_t looked, sample_t neutral, sample_t scene, float amount) {
        float3 c = pow(clamp(scene.rgb, 0.0f, 1.0f), float3(1.0f / 2.2f));
        float y = dot(c, float3(0.299f, 0.587f, 0.114f));
        float cb = (c.b - y) * 0.564f + 0.5f;
        float cr = (c.r - y) * 0.713f + 0.5f;
        float2 d = float2((cr - 0.585f) / 0.07f, (cb - 0.415f) / 0.08f);
        float skin = 1.0f - smoothstep(0.6f, 1.0f, length(d));
        skin *= smoothstep(0.08f, 0.2f, y) * (1.0f - smoothstep(0.92f, 0.99f, y));
        return float4(mix(looked.rgb, neutral.rgb, skin * amount), 1.0f);
    }

    // Revelar de novo: sombras (+ clareia) e altas luzes (− recupera), em paradas de luz
    float4 revelaShadowsHighlights(sample_t s, float shadows, float highlights) {
        float3 c = max(s.rgb, float3(0.0f));
        float x = log2(max(dot(c, revela::kLuma), 1e-5f) / 0.18f);
        float sw = 1.0f - smoothstep(-2.5f, 0.5f, x);
        float hw = smoothstep(-0.5f, 2.5f, x);
        float ev = shadows * 1.5f * sw + highlights * 1.5f * hw;
        return float4(c * exp2(ev), 1.0f);
    }

    // Ruído colorido: cor da versão borrada, brilho da original (amount 0 = original, 1 = toda a cor borrada)
    float4 revelaChroma(sample_t s, sample_t soft, float amount) {
        float3 c = max(s.rgb, float3(0.0f));
        float3 b = max(soft.rgb, float3(0.0f));
        float l = dot(c, revela::kLuma), lb = dot(b, revela::kLuma);
        float3 clean = b * (l / max(lb, 1e-5f));
        return float4(mix(c, clean, amount), 1.0f);
    }

    // Exposição longa no estilo rastros: fica o mais claro de cada ponto (luzes de carro, estrelas)
    float4 revelaMax(sample_t a, sample_t b) {
        return float4(max(a.rgb, b.rgb), 1.0f);
    }

    // Cor falsa: pinta cada faixa de brilho de uma cor, para acertar a exposição no olho
    float4 revelaFalseColor(sample_t s) {
        float l = dot(max(s.rgb, float3(0.0f)), revela::kLuma);
        float v = pow(l, 1.0f / 2.2f);
        float3 c = float3(v * 0.85f);
        if (v < 0.03f) c = float3(0.45f, 0.0f, 0.6f);          // preto sem detalhe
        else if (v < 0.12f) c = float3(0.05f, 0.25f, 0.9f);    // sombra funda
        else if (v > 0.40f && v < 0.47f) c = float3(0.2f, 0.75f, 0.25f);  // cinza médio (18%)
        else if (v > 0.62f && v < 0.70f) c = float3(0.95f, 0.55f, 0.65f); // pele bem exposta
        if (v > 0.93f) c = float3(1.0f, 0.85f, 0.0f);          // quase estourando
        if (v > 0.985f) c = float3(1.0f, 0.1f, 0.1f);          // estourado
        return float4(c * c, 1.0f);
    }

    // Estrelas: corta o que brilha muito acima da média (avião, satélite, pixel quente)
    float4 revelaClip(sample_t frame, sample_t mean, float allowance) {
        float3 limit = mean.rgb * (1.0f + allowance) + 0.0004f;
        return float4(min(frame.rgb, limit), 1.0f);
    }
}
}
