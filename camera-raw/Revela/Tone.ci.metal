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
    // boost: peso pela luz que a foto recebeu (exposição²). Com o mesmo peso, a de −2 EV (4× o ruído) sujava a
    // sombra e o HDR ficava com mais ruído que a foto normal; como no HDR+, a mais clara manda onde não estourou
    inline float hdrWeight(float3 c, float floorWeight, float boost) {
        float peak = max(c.r, max(c.g, c.b));
        float l = dot(c, kLuma);
        float w = (1.0f - smoothstep(0.75f, 0.97f, peak)) * smoothstep(0.0f, 0.04f, l);
        return max(w * boost, floorWeight);
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

    // O mesmo para fotos de exposição igual (NOITE, FOTO 3×): só não compara onde as DUAS estouraram. Com uma só
    // estourada (céu claro, carro branco passando) é movimento; antes a referência estourada aceitava qualquer coisa
    inline float ghostEqual(float3 frame, float3 ref, float k) {
        float rp = max(ref.r, max(ref.g, ref.b)), fp = max(frame.r, max(frame.g, frame.b));
        if (min(rp, fp) > 0.85f) return 1.0f;
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
    // gain: o mesmo da curva fílmica do filme (ida e volta dá a mesma imagem)
    float4 revelaToScene(sample_t s, float gain) {
        return float4(revela::inverseFilmic(s.rgb) / gain, 1.0f);
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
                      float vignette, float4 frame, float zebraThreshold, float4 film, float white,
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

        float3 t = revela::filmic(c * film.z);
        // Luz forte colorida (poste de sódio, letreiro, pôr do sol): a curva por canal vira laranja → amarelo → branco.
        // Parte da curva aplicada pelo canal mais forte mantém a cor da luz
        float cm = max(c.r, max(c.g, c.b)) * film.z;
        float3 hueKeep = c * film.z * (revela::filmic(float3(cm)).r / max(cm, 1e-5f));
        t = mix(t, hueKeep, film.w * smoothstep(0.35f, 1.4f, cm));
        // Ombro mais aberto: a curva ACES segura as luzes mais que a da Apple (branco p99 0,05–0,08 abaixo).
        // Esticar a saída (com o ganho de entrada menor) sobe o branco mais que o meio
        t = min(t * white, float3(1.0f));
        t = toe + (1.0f - toe) * t;
        t = pow(max(t * slope + offset, float3(0.0f)), power);

        // Cor densa: no negativo, cor forte é mais corante, então fica mais escura (não vira neon)
        float mx = max(t.r, max(t.g, t.b)), mn = min(t.r, min(t.g, t.b));
        float sat = (mx - mn) / max(mx, 1e-4f);
        t *= 1.0f - film.x * 0.28f * sat * sat * smoothstep(0.05f, 0.5f, mx);

        // Split toning: uma cor nas sombras, outra nas altas luzes
        float tl = dot(t, revela::kLuma);
        float sw = (1.0f - tl) * (1.0f - tl);
        t += shadowTint * sw * sw + highTint * tl * tl;
        t = max(t, float3(0.0f));

        // Vinheta: cantos mais escuros, como numa lente antiga
        float2 p = (dest.coord() - (frame.xy + frame.zw * 0.5f)) / (frame.zw * 0.5f);
        float r = length(p) / 1.4142f;
        t *= 1.0f - vignette * smoothstep(0.35f, 1.0f, r);

        // Grão como no filme: forte nas sombras e meios-tons, quase nada no preto e no branco.
        // No colorido cada cor tem um pouco do seu próprio grão
        tl = dot(t, revela::kLuma);
        float response = smoothstep(0.0f, 0.12f, tl) * pow(max(1.0f - tl, 0.0f), 1.4f) * 1.6f;
        float3 g = float3(n.r) + film.y * (float3(n.g, n.b, 0.5f * (n.g + n.b)) - float3(n.r));
        t += (g - 0.5f) * grain * response;
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
    float4 revelaHDRColor(sample_t s, float gain, float floorWeight, float boost) {
        float3 c = max(s.rgb, float3(0.0f));
        return float4(c * gain * revela::hdrWeight(c, floorWeight, boost), 1.0f);
    }

    float4 revelaHDRWeight(sample_t s, float floorWeight, float boost) {
        float w = revela::hdrWeight(max(s.rgb, float3(0.0f)), floorWeight, boost);
        return float4(w, w, w, 1.0f);
    }

    // HDR sem fantasma: o quadro (já na exposição normal) só conta onde bate com o de referência.
    // Onde a referência estourou não dá para comparar: aí o quadro escuro manda.
    float4 revelaHDRGhostColor(sample_t s, sample_t sBlur, sample_t refBlur, float gain, float floorWeight, float k, float boost) {
        float3 c = max(s.rgb, float3(0.0f));
        float g = revela::ghost(max(sBlur.rgb, float3(0.0f)) * gain, max(refBlur.rgb, float3(0.0f)), k);
        return float4(c * gain * revela::hdrWeight(c, floorWeight, boost) * g, 1.0f);
    }

    float4 revelaHDRGhostWeight(sample_t s, sample_t sBlur, sample_t refBlur, float gain, float floorWeight, float k, float boost) {
        float g = revela::ghost(max(sBlur.rgb, float3(0.0f)) * gain, max(refBlur.rgb, float3(0.0f)), k);
        float w = revela::hdrWeight(max(s.rgb, float3(0.0f)), floorWeight, boost) * g;
        return float4(w, w, w, 1.0f);
    }

    // HDR: joelho só nas luzes (cena linear). Abaixo de knee nada muda; acima, a luz chega no máximo a top, sem
    // estourar, mantendo a cor (escala o RGB todo). Antes o HDR só tirava contraste e ainda clareava 0,15 parada
    float4 revelaKnee(sample_t s, float knee, float top) {
        float3 c = max(s.rgb, float3(0.0f));
        float l = max(c.r, max(c.g, c.b));
        if (l <= knee) return float4(c, 1.0f);
        float span = max(top - knee, 1e-4f);
        float l2 = knee + span * (1.0f - exp(-(l - knee) / span));
        return float4(c * (l2 / l), 1.0f);
    }

    // NOITE sem fantasma: cada quadro conta menos onde difere da referência (algo se mexeu).
    float4 revelaRobustColor(sample_t s, sample_t sBlur, sample_t refBlur, float k) {
        float g = revela::ghostEqual(max(sBlur.rgb, float3(0.0f)), max(refBlur.rgb, float3(0.0f)), k);
        return float4(max(s.rgb, float3(0.0f)) * g, 1.0f);
    }

    // Junção em duas faixas (como o HDR+): o detalhe (s − parte lisa) entra só onde o quadro bate com a referência.
    // A parte lisa usa os kernels de sempre com tolerância maior. Sem limitar em zero: o detalhe tem sinal
    float4 revelaHighColor(sample_t s, sample_t low, sample_t sBlur, sample_t refBlur, float k) {
        float g = revela::ghostEqual(max(sBlur.rgb, float3(0.0f)), max(refBlur.rgb, float3(0.0f)), k);
        return float4((s.rgb - low.rgb) * g, 1.0f);
    }

    float4 revelaSub(sample_t a, sample_t b) {
        return float4(a.rgb - b.rgb, 1.0f);
    }

    float4 revelaDivideAdd(sample_t lowSum, sample_t lowWeight, sample_t highSum, sample_t highWeight) {
        float3 lo = lowSum.rgb / max(lowWeight.r, 1e-4f);
        float3 hi = highSum.rgb / max(highWeight.r, 1e-4f);
        return float4(max(lo + hi, float3(0.0f)), 1.0f);
    }

    float4 revelaRobustWeight(sample_t sBlur, sample_t refBlur, float k) {
        float g = revela::ghostEqual(max(sBlur.rgb, float3(0.0f)), max(refBlur.rgb, float3(0.0f)), k);
        return float4(g, g, g, 1.0f);
    }

    // Tons locais: log da luminância (para borrar e achar a "luz de fundo" de cada região)
    float4 revelaLogLuma(sample_t s) {
        float l = log2(max(dot(max(s.rgb, float3(0.0f)), revela::kLuma), 1e-5f));
        return float4(l, l, l, 1.0f);
    }

    // Tons locais: aproxima a luz de fundo de cada região da média (strength < 1) e mantém o detalhe.
    // shape: x = força nas sombras, y = força nas altas luzes, z = detalhe, w = deslocamento global (EV).
    // Sombras sobem mais do que as luzes descem: o céu não fica cinza
    // high: quanto as regiões claras (céu, nuvem; 1 a 3 EV acima da média) sobem, em EV — o branco da Apple é mais alto
    float4 revelaLocalTone(sample_t s, sample_t base, float mean, float4 shape, float high) {
        float3 c = max(s.rgb, float3(0.0f));
        float lg = log2(max(dot(c, revela::kLuma), 1e-5f));
        float b = base.r;
        float d = b - mean;
        float k = d < 0.0f ? shape.x : shape.y;
        float target = mean + d * k + (lg - b) * shape.z + shape.w + high * smoothstep(1.0f, 3.0f, d);
        return float4(c * exp2(clamp(target - lg, -3.0f, 3.0f)), 1.0f);
    }

    float4 revelaDivide(sample_t sum, sample_t weight) {
        return float4(sum.rgb / max(weight.r, 1e-4f), 1.0f);
    }

    // Divide, mas onde quase nada de peso chegou (fundo longe de qualquer pixel "fundo de verdade") usa a reserva:
    // dividir quase zero por quase zero dava preto ou ruído
    float4 revelaDivideFallback(sample_t sum, sample_t weight, sample_t fallback) {
        float w = weight.r;
        float3 c = sum.rgb / max(w, 1e-4f);
        return float4(mix(max(fallback.rgb, float3(0.0f)), c, smoothstep(0.02f, 0.2f, w)), 1.0f);
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

    // Encaixe numa passada só e bicúbico (Catmull-Rom): a foto vai para cima da referência pelo geral (inversa em
    // inv0/inv1) e pelo que sobrou em cada região (grade 3×3). Antes eram duas passadas bilineares (geral e região),
    // e cada uma amolecia a foto quando o deslocamento tinha fração de pixel (a NOITE na mão perdia detalhe)
    // Mitchell–Netravali (B = C = ⅓): quase tão nítido quanto o Catmull-Rom e sem o repique nas bordas, que com
    // ruído virava borda pontilhada na NOITE (laboratório: 570–940 pontinhos por MP nas persianas do XS)
    // Mitchell (B = C = ⅓). Testado B = 0,2, C = 0,4: NOITE na mão 0,78 → 0,82, mas as bordas voltaram a pontilhar
    // (69–98 → 192–267/MP no Neutro). Antes: entre o Mitchell (⅓, ⅓, que amolecia: 0,93 do
    // detalhe numa média de 10 encaixadas) e o Catmull-Rom (0, ½, que repicava e pontilhava a borda com ruído)
    inline float catmull(float x) {
        const float B = 1.0f / 3.0f, C = 1.0f / 3.0f;
        x = fabs(x);
        return x < 1.0f ? ((12.0f - 9.0f * B - 6.0f * C) * x * x * x + (-18.0f + 12.0f * B + 6.0f * C) * x * x + (6.0f - 2.0f * B)) / 6.0f
             : (x < 2.0f ? ((-B - 6.0f * C) * x * x * x + (6.0f * B + 30.0f * C) * x * x + (-12.0f * B - 48.0f * C) * x + (8.0f * B + 24.0f * C)) / 6.0f : 0.0f);
    }
    float4 revelaWarpCubic(sampler src, float3 inv0, float3 inv1, float4 a, float4 b, float4 c, float4 d, float2 e,
                           float4 grid, destination dest) {
        float2 o[9] = { a.xy, a.zw, b.xy, b.zw, c.xy, c.zw, d.xy, d.zw, e };
        float2 p = dest.coord();
        float u = clamp((p.x - grid.x) / grid.z, 0.0f, 2.0f);
        float v = clamp((p.y - grid.y) / grid.w, 0.0f, 2.0f);
        int i0 = min(int(u), 1), j0 = min(int(v), 1);
        float fu = u - float(i0), fv = v - float(j0);
        float2 residual = mix(mix(o[j0 * 3 + i0], o[j0 * 3 + i0 + 1], fu), mix(o[(j0 + 1) * 3 + i0], o[(j0 + 1) * 3 + i0 + 1], fu), fv);
        float2 r = p - residual;
        float2 q = float2(dot(inv0, float3(r, 1.0f)), dot(inv1, float3(r, 1.0f)));
        float2 base = floor(q - 0.5f);
        float2 f = q - 0.5f - base;
        float4 acc = float4(0.0f);
        for (int j = -1; j <= 2; j++) {
            float wy = catmull(float(j) - f.y);
            for (int i = -1; i <= 2; i++) {
                float w = catmull(float(i) - f.x) * wy;
                acc += src.sample(src.transform(base + float2(float(i), float(j)) + 0.5f)) * w;
            }
        }
        return float4(acc.rgb, 1.0f);
    }

    // Super resolução: o ponto da foto que cai no pixel grande p — pelo alinhamento geral (inversa em inv0/inv1) e pelo
    // que sobrou em cada uma das 9 regiões (grade 3×3 com centros em x0 + i·dx, y0 + j·dy), m = (fator, origem x, origem y, σ)
    inline float2 srSource(float2 p, float3 inv0, float3 inv1, float4 m, float4 a, float4 b, float4 c, float4 d, float2 e,
                           float4 grid) {
        float2 o[9] = { a.xy, a.zw, b.xy, b.zw, c.xy, c.zw, d.xy, d.zw, e };
        float u = clamp((p.x - grid.x) / grid.z, 0.0f, 2.0f);
        float v = clamp((p.y - grid.y) / grid.w, 0.0f, 2.0f);
        int i0 = min(int(u), 1), j0 = min(int(v), 1);
        float fu = u - float(i0), fv = v - float(j0);
        float2 residual = mix(mix(o[j0 * 3 + i0], o[j0 * 3 + i0 + 1], fu), mix(o[(j0 + 1) * 3 + i0], o[(j0 + 1) * 3 + i0 + 1], fu), fv);
        float2 r = (p - residual) / m.x + m.yz;
        return float2(dot(inv0, float3(r, 1.0f)), dot(inv1, float3(r, 1.0f)));
    }
    // Amostra dentro do que foi aberto da foto (valid = minX, minY, maxX, maxY)? Fora dele o Core Image devolve 0, que
    // entrava com peso cheio e escurecia a beirada da foto grande
    inline float srValid(float2 cpos, float4 valid) {
        return (cpos.x > valid.x && cpos.y > valid.y && cpos.x < valid.z && cpos.y < valid.w) ? 1.0f : 0.0f;
    }

    // Super resolução por regressão de núcleo (Wronski et al. 2019, Google "Handheld Multi-Frame Super-Resolution"):
    // cada pixel de cada foto vai para onde ele caiu na grade grande (com o alinhamento em fração de pixel),
    // pesado pela distância (gaussiana de σ = m.w pixels grandes). Antes cada foto era ampliada e depois tirada a média:
    // isso borrava e a desconvolução forte voltava a estragar (protótipo: +4 dB de PSNR com este jeito).
    // gm: mapa de movimento da foto (1 = igual à referência; onde algo se mexeu ela quase não conta). Devolve Σ w·cor·g;
    // o peso (Σ w·g) sai do revelaSplatWeight, que não abre a foto
    float4 revelaSplat(sampler src, sampler gm, float3 inv0, float3 inv1, float4 m, float4 a, float4 b, float4 c,
                       float4 d, float2 e, float4 grid, float4 valid, destination dest) {
        float2 p = dest.coord();
        float2 q = srSource(p, inv0, inv1, m, a, b, c, d, e, grid);
        float2 base = floor(q - 0.5f);
        float3 acc = float3(0.0f);
        float inv2s2 = 1.0f / (2.0f * m.w * m.w);
        for (int j = -1; j <= 2; j++) {
            for (int i = -1; i <= 2; i++) {
                float2 cpos = base + float2(float(i), float(j)) + 0.5f;
                float2 dd = (cpos - q) * m.x;
                float w = exp(-dot(dd, dd) * inv2s2) * srValid(cpos, valid);
                acc += max(src.sample(src.transform(cpos)).rgb, float3(0.0f)) * w;
            }
        }
        float g = clamp(gm.sample(gm.transform(p)).r, 0.0f, 1.0f);
        return float4(acc * g, 1.0f);
    }

    float4 revelaSplatWeight(sampler gm, float3 inv0, float3 inv1, float4 m, float4 a, float4 b, float4 c,
                             float4 d, float2 e, float4 grid, float4 valid, destination dest) {
        float2 p = dest.coord();
        float2 q = srSource(p, inv0, inv1, m, a, b, c, d, e, grid);
        float2 base = floor(q - 0.5f);
        float wsum = 0.0f;
        float inv2s2 = 1.0f / (2.0f * m.w * m.w);
        for (int j = -1; j <= 2; j++) {
            for (int i = -1; i <= 2; i++) {
                float2 cpos = base + float2(float(i), float(j)) + 0.5f;
                float2 dd = (cpos - q) * m.x;
                wsum += exp(-dot(dd, dd) * inv2s2) * srValid(cpos, valid);
            }
        }
        float g = clamp(gm.sample(gm.transform(p)).r, 0.0f, 1.0f);
        return float4(float3(wsum * g), 1.0f);
    }

    // SUPER ZOOM: desconvolução regularizada (MAP com Huber-TV), como no estudo em Python (+5,4 dB contra +4,5 do
    // Richardson–Lucy nas 24 fotos do laboratório). Cor separada em brilho e duas cores (base ortonormal): o brilho
    // pode ter detalhe fino, a cor é mantida lisa (λ 10× maior), que é onde o ruído colorido some
    inline float3 tvU(float3 c) {
        return float3((c.r + c.g + c.b) * 0.57735027f, (c.r - c.g) * 0.70710678f, (c.r + c.g - 2.0f * c.b) * 0.40824829f);
    }
    inline float3 tvUt(float3 u) {
        return float3(u.x * 0.57735027f + u.y * 0.70710678f + u.z * 0.40824829f,
                      u.x * 0.57735027f - u.y * 0.70710678f + u.z * 0.40824829f,
                      u.x * 0.57735027f - 2.0f * u.z * 0.40824829f);
    }
    // SUPER ZOOM 3× (MAP com as 24 fotos de uma vez). Cada pixel de cada foto = média de 2×2 pixels grandes da cena,
    // já borrada pela lente/interpolação (Mitchell): h(d) = ½[m(d + ½) + m(d − ½)], alcance 2,5 px grandes
    inline float srMitchell(float x) {
        x = fabs(x);
        if (x < 1.0f) return (7.0f * x * x * x - 12.0f * x * x + 16.0f / 3.0f) / 6.0f;
        if (x < 2.0f) return ((-7.0f / 3.0f) * x * x * x + 12.0f * x * x - 20.0f * x + 32.0f / 3.0f) / 6.0f;
        return 0.0f;
    }
    inline float srH(float d) { return 0.5f * (srMitchell(d + 0.5f) + srMitchell(d - 0.5f)); }

    // Retroprojeção de uma foto (Aᵀy): cada pixel grande soma h·valor dos pixels da foto em volta, × o mapa de movimento:
    // onde a foto não bate com a referência a amostra SAI (antes virava a referência ampliada, borrada: no estudo em Python a
    // pessoa andando ia de +4,26 para +6,31 dB tirando em vez de trocar). O mapa compara versões borradas: o serrilhado das
    // bordas (que a super resolução aproveita) fica com peso 1
    float4 revelaSplatH(sampler src, sampler gm, float3 inv0, float3 inv1, float4 m, float4 a, float4 b, float4 c,
                        float4 d, float2 e, float4 grid, float4 valid, destination dest) {
        float2 p = dest.coord();
        float2 q = srSource(p, inv0, inv1, m, a, b, c, d, e, grid);
        float2 base = floor(q - 0.5f);
        float3 acc = float3(0.0f);
        for (int j = -1; j <= 2; j++) {
            for (int i = -1; i <= 2; i++) {
                float2 cpos = base + float2(float(i), float(j)) + 0.5f;
                float2 dd = (cpos - q) * m.x;
                float w = srH(dd.x) * srH(dd.y) * srValid(cpos, valid);
                acc += max(src.sample(src.transform(cpos)).rgb, float3(0.0f)) * w;
            }
        }
        float g = clamp(gm.sample(gm.transform(p)).r, 0.0f, 1.0f);
        return float4(acc * g, 1.0f);
    }

    // Σh da mesma foto (só a geometria: não abre a foto), somado ao acumulado: r = Σh·g (para o começo Σh·g·y/Σh·g),
    // g = Σh (para W = Σh·g/Σh, a fração das amostras que ficou em cada pixel). Fora da transparência (pré-multiplicação)
    float4 revelaSplatHWeight(sample_t accum, sample_t gm, float3 inv0, float3 inv1, float4 m, float4 a, float4 b,
                              float4 c, float4 d, float2 e, float4 grid, float4 valid, destination dest) {
        float2 p = dest.coord();
        float2 q = srSource(p, inv0, inv1, m, a, b, c, d, e, grid);
        float2 base = floor(q - 0.5f);
        float wsum = 0.0f;
        for (int j = -1; j <= 2; j++) {
            for (int i = -1; i <= 2; i++) {
                float2 cpos = base + float2(float(i), float(j)) + 0.5f;
                float2 dd = (cpos - q) * m.x;
                wsum += srH(dd.x) * srH(dd.y) * srValid(cpos, valid);
            }
        }
        float g = clamp(gm.r, 0.0f, 1.0f);
        return float4(accum.r + wsum * g, accum.g + wsum, 0.0f, 1.0f);
    }

    // Um passo de FISTA do MAP sobre z (= x + β(x − x_anterior), calculado uma vez por passo antes; antes era refeito
    // 56 vezes por pixel aqui dentro): dado = AᵀA·z − b, com AᵀA exato para deslocamento (núcleo 7×7 por fase do pixel e
    // por pedaço da grade 3×3, na tabela, misturando os 4 pedaços em volta como o alinhamento por região; antes trocava de
    // pedaço de uma vez no meio do caminho); Huber-TV conjunta brilho/cor (as bordas da cor seguem as do brilho).
    // Passo diagonal 1/(‖AᵀA‖ + 8λ/δ) em cada canal: converge
    struct SRFlux { float3 x; float3 y; };
    inline SRFlux srFlux(float3 u0, float3 ux, float3 uy, float w, float delta) {
        float3 gx = ux - u0, gy = uy - u0;
        float n = sqrt(gx.x * gx.x + gy.x * gy.x + w * (gx.y * gx.y + gy.y * gy.y + gx.z * gx.z + gy.z * gy.z));
        float s = 1.0f / max(n, delta);
        SRFlux f;
        f.x = gx * s;
        f.y = gy * s;
        return f;
    }
    // ws: as somas de peso (r = Σh·g, g = Σh); o dado vira W·AᵀA·z − b, W = r/g (só as amostras que ficaram contam)
    float4 revelaMAPStep(sampler z, sampler b, sampler tab, sampler ws, float4 grid, float3 lam, float3 tau,
                         float delta, float w, destination dest) {
        float2 p = dest.coord();
        float u = clamp((p.x - grid.x) / grid.z, 0.0f, 2.0f);
        float v = clamp((p.y - grid.y) / grid.w, 0.0f, 2.0f);
        int i0 = min(int(u), 1), j0 = min(int(v), 1);
        float fu = u - float(i0), fv = v - float(j0);
        float w00 = (1.0f - fu) * (1.0f - fv), w10 = fu * (1.0f - fv), w01 = (1.0f - fu) * fv, w11 = fu * fv;
        int ax = int(floor(p.x)) & 1, ay = int(floor(p.y)) & 1;
        // Tabela: x = fase x·7 + dx, y = (pedaço·2 + fase y)·7 + dy; pedaço = j·3 + i (o vizinho em x soma 14 linhas, em y 42)
        float tx = float(ax * 7) + 3.5f;
        float y00 = float((j0 * 3 + i0) * 14 + ay * 7) + 3.5f;
        float3 conv = float3(0.0f);
        for (int dy = -3; dy <= 3; dy++) {
            for (int dx = -3; dx <= 3; dx++) {
                float kx = tx + float(dx), ky = y00 + float(dy);
                float kv = w00 * tab.sample(tab.transform(float2(kx, ky))).r
                         + w10 * tab.sample(tab.transform(float2(kx, ky + 14.0f))).r
                         + w01 * tab.sample(tab.transform(float2(kx, ky + 42.0f))).r
                         + w11 * tab.sample(tab.transform(float2(kx, ky + 56.0f))).r;
                conv += kv * z.sample(z.transform(p + float2(float(dx), float(dy)))).rgb;
            }
        }
        float3 z0 = z.sample(z.transform(p)).rgb;
        float4 wsp = ws.sample(ws.transform(p));
        float W = clamp(wsp.r / max(wsp.g, 1e-6f), 0.0f, 1.0f);
        float3 G = W * conv - b.sample(b.transform(p)).rgb;
        float3 u0 = tvU(z0);
        float3 uxp = tvU(z.sample(z.transform(p + float2(1.0f, 0.0f))).rgb), uyp = tvU(z.sample(z.transform(p + float2(0.0f, 1.0f))).rgb);
        float3 uxm = tvU(z.sample(z.transform(p - float2(1.0f, 0.0f))).rgb), uym = tvU(z.sample(z.transform(p - float2(0.0f, 1.0f))).rgb);
        float3 uxmyp = tvU(z.sample(z.transform(p + float2(-1.0f, 1.0f))).rgb), uymxp = tvU(z.sample(z.transform(p + float2(1.0f, -1.0f))).rgb);
        SRFlux f0 = srFlux(u0, uxp, uyp, w, delta);
        SRFlux fl = srFlux(uxm, u0, uxmyp, w, delta);
        SRFlux fd = srFlux(uym, uymxp, u0, w, delta);
        float3 dv = (f0.x - fl.x) + (f0.y - fd.y);
        float3 stepU = tau * (tvU(G) - lam * dv);
        return float4(max(z0 - tvUt(stepU), float3(0.0f)), 1.0f);
    }

    // Fluxo de Huber: ∇u / max(|∇u|, δ), um eixo por vez (axis 0 = x, 1 = y), diferença para a frente
    float4 revelaTVFlux(sampler x, float delta, float axis, destination dest) {
        float2 p = dest.coord();
        float3 u0 = tvU(x.sample(x.transform(p)).rgb);
        float3 gx = tvU(x.sample(x.transform(p + float2(1.0f, 0.0f))).rgb) - u0;
        float3 gy = tvU(x.sample(x.transform(p + float2(0.0f, 1.0f))).rgb) - u0;
        float3 s = 1.0f / max(sqrt(gx * gx + gy * gy), float3(delta));
        return float4(axis < 0.5f ? gx * s : gy * s, 1.0f);
    }
    // Um passo: z − τ·(gradiente dos dados + λ·gradiente da Huber-TV), sem valor negativo.
    // A divergência é a diferença para trás (a transposta da diferença para a frente do fluxo)
    float4 revelaTVStep(sampler z, sampler fx, sampler fy, sampler dataGrad, float3 lam, float tau, destination dest) {
        float2 p = dest.coord();
        float3 dv = fx.sample(fx.transform(p)).rgb - fx.sample(fx.transform(p - float2(1.0f, 0.0f))).rgb
                  + fy.sample(fy.transform(p)).rgb - fy.sample(fy.transform(p - float2(0.0f, 1.0f))).rgb;
        float3 g = dataGrad.sample(dataGrad.transform(p)).rgb + tvUt(-dv * lam);
        return float4(max(z.sample(z.transform(p)).rgb - tau * g, float3(0.0f)), 1.0f);
    }
    // Aceleração de Nesterov (FISTA): z = x_novo + β·(x_novo − x)
    float4 revelaMomentum(sample_t xn, sample_t x, float beta) {
        return float4(xn.rgb + beta * (xn.rgb - x.rgb), 1.0f);
    }

    // Desconvolução (Richardson–Lucy): quanto a imagem observada difere da estimativa borrada
    float4 revelaRatio(sample_t observed, sample_t blurred) {
        float3 r = max(observed.rgb, float3(0.0f)) / max(blurred.rgb, float3(1e-4f));
        return float4(clamp(r, 0.6f, 1.6f), 1.0f);
    }

    float4 revelaMultiply(sample_t a, sample_t b) {
        return float4(max(a.rgb, float3(0.0f)) * b.rgb, 1.0f);
    }

    // NOITE: onde a foto curta (escura, multiplicada de volta) é mais clara que a junção, a junção estourou ali
    // (poste, letreiro): fica a curta, com cor e forma da luz.
    float4 revelaRecover(sample_t merged, sample_t shortFrame, float gain) {
        float3 m = max(merged.rgb, float3(0.0f));
        float3 s = max(shortFrame.rgb, float3(0.0f)) * gain;
        float lm = dot(m, revela::kLuma), ls = dot(s, revela::kLuma);
        float w = smoothstep(0.05f, 0.3f, (ls - lm) / max(lm, 1e-3f));
        return float4(mix(m, max(m, s), w), 1.0f);
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

    // Retrato: o fundo entra no desfoque pesado pelo quanto é fundo (alfa) e com as luzes mais fortes,
    // para virarem bolinhas de luz como numa lente aberta (a média borrada apagaria as luzes)
    float4 revelaBokehSource(sample_t s, sample_t map, float threshold) {
        float3 c = max(s.rgb, float3(0.0f));
        float y = dot(c, revela::kLuma);
        c *= 1.0f + 2.5f * smoothstep(0.75f, 1.0f, y);
        // threshold > 1 = camada do fundo: só o que é claramente fundo (rampa de 0,55 a 0,95 do mapa)
        // Fundo de verdade: só o que tem 92% ou mais de fundo no mapa (55–95% ainda levava até 45% de sujeito; 85%: vazamento
        // 0,36/0,12/0,10 de um desfoque comum)
        float w = threshold > 1.0f ? smoothstep(0.92f, 1.0f, map.r) : smoothstep(threshold * 0.5f, threshold, map.r);
        // Opaco: a cor já vem × peso, e o peso sai à parte (revelaBokehWeight); no fim um divide pelo outro
        return float4(c * w, 1.0f);
    }

    float4 revelaBokehWeight(sample_t map, float threshold) {
        float w = threshold > 1.0f ? smoothstep(0.92f, 1.0f, map.r) : smoothstep(threshold * 0.5f, threshold, map.r);
        return float4(w, w, w, 1.0f);
    }

    // Centro das luzes fortes: só o pixel mais alto de cada luz (borrada) fica, com a energia dela toda.
    // Os raios saem dele e ficam finos, como a difração de verdade (antes saíam da luz inteira e ficavam grossos)
    float4 revelaPeak(sample_t b, sample_t m, float gain) {
        float l = dot(b.rgb, revela::kLuma), lm = dot(m.rgb, revela::kLuma);
        return (l > 1e-4f && l >= lm * 0.999f) ? float4(b.rgb * gain, 1.0f) : float4(0.0f, 0.0f, 0.0f, 1.0f);
    }

    // Ruído de brilho por faixa (ondaletas): o detalhe menor que o ruído some, o maior fica.
    // O limite cresce com a raiz da luz, como o ruído do sensor
    // Ponto solto (mais claro ou mais escuro que todos os 8 vizinhos): volta para o limite dos vizinhos, sem borrar
    // nada em volta. A limpeza de brilho alisa o ruído pequeno mas deixa passar inteiro o pixel que foge muito, e a
    // NOITE ficava lisa com pontinhos soltos (laboratório: 377 por megapixel no céu do Pixel)
    float4 revelaDespeckle(sampler src, destination dest) {
        float2 p = dest.coord();
        float4 c = src.sample(src.transform(p));
        float3 lo = float3(1e9f), hi = float3(-1e9f);
        for (int j = -1; j <= 1; j++) {
            for (int i = -1; i <= 1; i++) {
                if (i == 0 && j == 0) continue;
                float3 n = src.sample(src.transform(p + float2(float(i), float(j)))).rgb;
                lo = min(lo, n);
                hi = max(hi, n);
            }
        }
        // Estrela e poste longe também são pontos soltos, mas bem mais claros que tudo em volta: esses ficam
        float lc = dot(max(c.rgb, float3(0.0f)), revela::kLuma), lh = dot(max(hi, float3(0.0f)), revela::kLuma);
        if (lc > max(0.35f, 3.0f * lh)) return float4(c.rgb, 1.0f);
        return float4(clamp(c.rgb, lo, hi), 1.0f);
    }

    float4 revelaShrink(sample_t s, sample_t blur, float threshold, float floorT) {
        float3 d = s.rgb - blur.rgb;
        float dl = dot(d, revela::kLuma);
        // Limiar pela luz (ruído de fóton) e nunca abaixo do ruído medido na foto (no escuro manda o ruído eletrônico,
        // que não cai com a luz: a regra só da raiz deixava o granulado fino nas sombras da NOITE)
        float t = max(threshold * sqrt(max(dot(max(blur.rgb, float3(0.0f)), revela::kLuma), 0.0004f)), floorT);
        float k = abs(dl) > 1e-6f ? max(abs(dl) - t, 0.0f) / abs(dl) : 0.0f;
        // Um pouco do ruído volta (15%): sem isso vira pintura
        k = mix(0.15f, 1.0f, k);
        return float4(blur.rgb + d * k, 1.0f);
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

    // Mapa de movimento das junções de fotos iguais (NOITE, FOTO 3×, SUPER ZOOM/RES), nas versões já borradas (o borrão
    // mata o serrilhado e o ruído fino): z = |ΔY| / √var, var = p.x·Y + p.y (ruído ajustado na própria rajada) +
    // (p.z·|∇Y_ref|)² (o que um erro de encaixe de p.z px explica numa borda: sem isso a borda serrilhada parada virava
    // movimento — estudo em Python no SUPER ZOOM: 0,15 px de erro derrubava +6,36 para +2,34 dB). g = 1 até z = lim.x e
    // 0 a partir de lim.y. Sem exceção para o estourado: antes a referência acima de 0,85 aceitava tudo (céu claro, carro
    // branco passando) e a pessoa escura na frente do céu saía translúcida
    float4 revelaMotion(sampler f, sampler r, float4 p, float2 lim, destination dest) {
        float2 q = dest.coord();
        float yf = dot(max(f.sample(f.transform(q)).rgb, float3(0.0f)), revela::kLuma);
        float yr = dot(max(r.sample(r.transform(q)).rgb, float3(0.0f)), revela::kLuma);
        float2 ex = float2(1.0f, 0.0f), ey = float2(0.0f, 1.0f);
        float gx = 0.5f * dot(r.sample(r.transform(q + ex)).rgb - r.sample(r.transform(q - ex)).rgb, revela::kLuma);
        float gy = 0.5f * dot(r.sample(r.transform(q + ey)).rgb - r.sample(r.transform(q - ey)).rgb, revela::kLuma);
        float var = p.x * yr + p.y + p.z * p.z * (gx * gx + gy * gy);
        float z = abs(yf - yr) / sqrt(max(var, 1e-12f));
        float g = clamp((lim.y - z) / max(lim.y - lim.x, 1e-3f), 0.0f, 1.0f);
        return float4(g, g, g, 1.0f);
    }

    // Cor × peso (mapa de movimento ou peso do foco, no canal r)
    float4 revelaMulG(sample_t s, sample_t g) {
        return float4(max(s.rgb, float3(0.0f)) * g.r, 1.0f);
    }

    // Detalhe (s − parte lisa) × peso. Sem limitar em zero: o detalhe tem sinal
    float4 revelaHighG(sample_t s, sample_t low, sample_t g) {
        return float4((s.rgb - low.rgb) * g.r, 1.0f);
    }

    // Mediana de 9 (rede de trocas de Paeth/Devillard, cada cor à parte)
    inline float3 median9(float3 p0, float3 p1, float3 p2, float3 p3, float3 p4, float3 p5, float3 p6, float3 p7, float3 p8) {
#define REVELA_CX(a, b) { float3 t_ = min(a, b); b = max(a, b); a = t_; }
        REVELA_CX(p1, p2); REVELA_CX(p4, p5); REVELA_CX(p7, p8);
        REVELA_CX(p0, p1); REVELA_CX(p3, p4); REVELA_CX(p6, p7);
        REVELA_CX(p1, p2); REVELA_CX(p4, p5); REVELA_CX(p7, p8);
        REVELA_CX(p0, p3); REVELA_CX(p5, p8); REVELA_CX(p4, p7);
        REVELA_CX(p3, p6); REVELA_CX(p1, p4); REVELA_CX(p2, p5);
        REVELA_CX(p4, p7); REVELA_CX(p4, p2); REVELA_CX(p6, p4);
        REVELA_CX(p4, p2);
#undef REVELA_CX
        return p4;
    }
    inline float3 median3x3(sampler s, float2 p) {
        return median9(s.sample(s.transform(p + float2(-1.0f, -1.0f))).rgb, s.sample(s.transform(p + float2(0.0f, -1.0f))).rgb,
                       s.sample(s.transform(p + float2(1.0f, -1.0f))).rgb, s.sample(s.transform(p + float2(-1.0f, 0.0f))).rgb,
                       s.sample(s.transform(p)).rgb, s.sample(s.transform(p + float2(1.0f, 0.0f))).rgb,
                       s.sample(s.transform(p + float2(-1.0f, 1.0f))).rgb, s.sample(s.transform(p + float2(0.0f, 1.0f))).rgb,
                       s.sample(s.transform(p + float2(1.0f, 1.0f))).rgb);
    }

    // ESTRELAS: pixel quente (fixo no sensor). No mínimo das fotos sem alinhar as estrelas somem (o céu anda ≥ 3 px) e o
    // quente fica. Quente = passa da mediana 3×3 em volta por mais de 6σ do ruído (noise) e por mais de metade do nível
    // dela (uma luz de verdade se espalha pela lente e os vizinhos sobem junto)
    float4 revelaHotMask(sampler mn, float noise, destination dest) {
        float2 p = dest.coord();
        float c = dot(max(mn.sample(mn.transform(p)).rgb, float3(0.0f)), revela::kLuma);
        float med = dot(max(median3x3(mn, p), float3(0.0f)), revela::kLuma);
        float excess = c - med;
        float hot = (excess > 6.0f * noise && excess > 0.5f * med) ? 1.0f : 0.0f;
        return float4(hot, hot, hot, 1.0f);
    }

    // O quente vira a mediana 3×3 (cada cor) em cada foto, antes de alinhar
    float4 revelaHotFix(sampler f, sampler mask, destination dest) {
        float2 p = dest.coord();
        if (mask.sample(mask.transform(p)).r < 0.5f) return float4(f.sample(f.transform(p)).rgb, 1.0f);
        return float4(median3x3(f, p), 1.0f);
    }

    // ESTRELAS: corte do que passou (avião, satélite) depois de alinhar: acima de média + κ·max(desvio entre as fotos,
    // ruído), em vez de 1,6 × a média (que com as fotos desalinhadas apagava ~55% das estrelas, que andam)
    float4 revelaSigmaClip(sample_t x, sample_t mean, sample_t meanSq, float kappa, float noise) {
        float3 m = mean.rgb;
        float3 s = sqrt(max(meanSq.rgb - m * m, float3(0.0f)));
        float3 limit = m + kappa * max(s, float3(noise));
        return float4(min(x.rgb, limit), 1.0f);
    }

    // NOITE: onde poucas fotos entraram (quem se mexeu ficou só com a referência) a limpeza é mais forte, pelo que falta de
    // 1/√N_eff: 0 onde entraram todas, perto de 1 onde só a referência
    float4 revelaCoverageMask(sample_t coverage, float frames) {
        float m = clamp(1.0f - sqrt(max(coverage.r, 0.0f) / max(frames, 1.0f)), 0.0f, 1.0f);
        return float4(m, m, m, 1.0f);
    }

    // ESTRELAS: qual jeito explica melhor esta foto aqui, parado (chão) ou girando com o céu. > 0 = céu
    float4 revelaSkyEvidence(sample_t still, sample_t stillMean, sample_t turned, sample_t skyMean) {
        float du = abs(dot(still.rgb - stillMean.rgb, revela::kLuma));
        float da = abs(dot(turned.rgb - skyMean.rgb, revela::kLuma));
        float e = du - da;
        return float4(e, e, e, 1.0f);
    }

    float4 revelaSkyMask(sample_t e, float t) {
        float m = smoothstep(-t, t, e.r);
        return float4(m, m, m, 1.0f);
    }

    // FOCO EMPILHADO: peso pela nitidez relativa (s ÷ nitidez típica), preso para caber na meia precisão (a soma de 7 fotos
    // não estoura). Potência alta = quase sempre a mais nítida, mas sem a troca dura (0/1) que fazia auréola
    float4 revelaFocusWeight(sample_t s, float typical, float power) {
        float r = clamp(max(s.r, 0.0f) / max(typical, 1e-6f), 0.18f, 6.7f);
        float w = pow(r, power);
        return float4(w, w, w, 1.0f);
    }

    // LONGA rastros: a luz que passou acima da média até aqui (e do ruído: t.x + t.y × média), o maior de todos. No fim:
    // média + isso. O máximo puro das fotos com ruído subia o preto ~3σ (céu cinza)
    float4 revelaTrail(sample_t previous, sample_t frame, sample_t total, float invCount, float2 t) {
        float3 mean = max(total.rgb, float3(0.0f)) * invCount;
        float3 e = max(frame.rgb - mean - (t.x + t.y * mean), float3(0.0f));
        return float4(max(previous.rgb, e), 1.0f);
    }
}
}
