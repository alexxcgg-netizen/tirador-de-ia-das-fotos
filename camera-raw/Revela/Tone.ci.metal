#include <CoreImage/CoreImage.h>
using namespace metal;

namespace revela {
    // Curva fílmica (aproximação ACES de Narkowicz): cena linear -> display linear
    inline float3 filmic(float3 x) {
        const float a = 2.51f, b = 0.03f, c = 2.43f, d = 0.59f, e = 0.14f;
        return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0f, 1.0f);
    }
}

extern "C" {
namespace coreimage {
    // s: imagem RAW revelada em luz linear (sem o "boost" da Apple)
    // n: ruído para o grão
    float4 revelaTone(sample_t s, sample_t n,
                      float exposure, float saturation, float warmth, float mono,
                      float toe, float contrast, float grain) {
        float3 c = max(s.rgb, float3(0.0f)) * exp2(exposure);
        c *= float3(1.0f + warmth, 1.0f, 1.0f - warmth);

        const float3 w = float3(0.2126f, 0.7152f, 0.0722f);
        float l = dot(c, w);
        c = mix(float3(l), c, saturation);
        c = mix(c, float3(l), mono);
        c = max(c, float3(1e-6f));

        // Contraste em escala logarítmica, ancorado no cinza médio (18%)
        c = 0.18f * pow(c / 0.18f, float3(contrast));

        float3 t = revela::filmic(c * 0.8f);
        t = toe + (1.0f - toe) * t;

        // Grão mais forte nos meios-tons, como em filme
        float tl = dot(t, w);
        t += (n.r - 0.5f) * grain * 4.0f * tl * (1.0f - tl);

        return float4(clamp(t, 0.0f, 1.0f), 1.0f);
    }
}
}
