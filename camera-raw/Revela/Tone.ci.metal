#include <CoreImage/CoreImage.h>
using namespace metal;

namespace revela {
    constant float3 kLuma = float3(0.2126f, 0.7152f, 0.0722f);
    constant float kA = 2.51f, kB = 0.03f, kC = 2.43f, kD = 0.59f, kE = 0.14f;

    // Curva fílmica (aproximação ACES de Narkowicz): cena linear -> display linear
    inline float3 filmic(float3 x) {
        return clamp((x * (kA * x + kB)) / (x * (kC * x + kD) + kE), 0.0f, 1.0f);
    }

    // Inversa da curva: usada no preview para estimar a luz da cena a partir do vídeo do iPhone
    inline float3 inverseFilmic(float3 v) {
        float3 x = clamp(v, 0.0f, 0.985f);
        float3 A = x * kC - kA;
        float3 B = x * kD - kB;
        float3 C = x * kE;
        float3 D = sqrt(max(B * B - 4.0f * A * C, 0.0f));
        return (-B - D) / (2.0f * A);
    }

    // A revelação em si: cena linear -> display linear
    inline float3 grade(float3 scene, float noise,
                        float exposure, float saturation, float warmth, float mono,
                        float toe, float contrast, float grain, float3 shadowTint, float3 highTint) {
        float3 c = max(scene, float3(0.0f)) * exp2(exposure);
        c *= float3(1.0f + warmth, 1.0f, 1.0f - warmth);

        float l = dot(c, kLuma);
        c = mix(float3(l), c, saturation);
        c = mix(c, float3(l), mono);
        c = max(c, float3(1e-6f));

        // Contraste em escala logarítmica, ancorado no cinza médio (18%)
        c = 0.18f * pow(c / 0.18f, float3(contrast));

        float3 t = filmic(c * 0.8f);
        t = toe + (1.0f - toe) * t;

        // Split toning: uma cor nas sombras, outra nas altas luzes
        float tl = dot(t, kLuma);
        float shadowWeight = (1.0f - tl) * (1.0f - tl);
        t += shadowTint * shadowWeight * shadowWeight + highTint * tl * tl;
        t = max(t, float3(0.0f));

        // Grão mais forte nos meios-tons, como em filme
        tl = dot(t, kLuma);
        t += (noise - 0.5f) * grain * 4.0f * tl * (1.0f - tl);

        return clamp(t, 0.0f, 1.0f);
    }
}

extern "C" {
namespace coreimage {
    // Foto: s é o RAW revelado em luz linear (sem o "boost" da Apple)
    float4 revelaTone(sample_t s, sample_t n,
                      float exposure, float saturation, float warmth, float mono,
                      float toe, float contrast, float grain, float3 shadowTint, float3 highTint) {
        float3 t = revela::grade(s.rgb, n.r, exposure, saturation, warmth, mono,
                                 toe, contrast, grain, shadowTint, highTint);
        return float4(t, 1.0f);
    }

    // Preview ao vivo: s é o vídeo da câmera (já com a curva do iPhone)
    float4 revelaPreview(sample_t s, sample_t n,
                         float exposure, float saturation, float warmth, float mono,
                         float toe, float contrast, float grain, float3 shadowTint, float3 highTint,
                         float zebra, destination dest) {
        float3 scene = revela::inverseFilmic(s.rgb) / 0.8f;
        float3 t = revela::grade(scene, n.r, exposure, saturation, warmth, mono,
                                 toe, contrast, grain, shadowTint, highTint);

        // Zebra: listras onde o sensor já estourou
        if (zebra > 0.5f && max(s.r, max(s.g, s.b)) > 0.97f) {
            float2 p = dest.coord();
            float stripe = fmod(p.x + p.y, 18.0f) < 9.0f ? 1.0f : 0.0f;
            t = mix(t, float3(stripe), 0.55f);
        }
        return float4(t, 1.0f);
    }
}
}
