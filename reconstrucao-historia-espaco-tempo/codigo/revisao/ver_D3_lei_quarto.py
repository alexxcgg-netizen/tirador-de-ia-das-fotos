"""Verificacao D3: lei (Mf)^(1/4) num modelo de brinquedo com transformada EXATA (funcao gama incompleta).

Modelo (M = 1): h(tau) = A' tau^(-1/4) para tau >= tau_m (inspiral de ordem dominante), e o resto da memoria
total, Delta H - A' tau_m^(-1/4), depositado de uma vez em tau_m (fusao abrupta). Com e^{+i w tau} (t = t_c - tau):
  hdot~(w) = (A'/4) int_{tau_m}^inf tau^(-5/4) e^{i w tau} d tau + (Delta H - A' tau_m^(-1/4)) e^{i w tau_m}
           = (A'/4) (-i w)^(1/4) Gamma(-1/4, -i w tau_m) + ...
T(w) = hdot~/Delta H; previsao 1 - |T| ~ c cos(pi/8) w^(1/4), c = |Gamma(-1/4)| (5/eta)^(1/4)/(16 x*).
Confere a derivacao do relatorio L05 (secao 2) de forma independente (sem NR). Tambem: janela finita tau <= tau_w.
"""
import mpmath as mp
import numpy as np

mp.mp.dps = 30


def caso(eta, xs, tau_m, tau_w=None):
    Q = 1.0
    A1 = Q * eta * 0.25 * (5 / eta) ** 0.25
    dH = Q * eta * xs
    resto = dH - A1 * tau_m ** -0.25
    c = abs(float(mp.gamma(-0.25))) * (5 / eta) ** 0.25 / (16 * xs)
    out = []
    for w in (1e-5, 1e-4, 1e-3, 1e-2, 3e-2):
        z = -1j * w
        I = (A1 / 4) * z ** 0.25 * mp.gammainc(-0.25, z * tau_m)     # int_{tau_m}^inf tau^(-5/4) e^{-z tau}
        if tau_w is not None:                                         # janela: so tau <= tau_w
            I -= (A1 / 4) * z ** 0.25 * mp.gammainc(-0.25, z * tau_w)
        T = (I + resto * mp.exp(1j * w * tau_m)) / dH
        prev = c * np.cos(np.pi / 8) * w ** 0.25
        out.append((w, 1 - abs(complex(T)), prev, (1 - abs(complex(T))) / prev,
                    float(mp.arg(1 - T)) if abs(1 - T) > 0 else 0.0))
    return c, resto / dH, out


def main():
    for eta, xs, tau_m, tau_w in ((0.25, 0.45, 50.0, None), (0.25, 0.45, 10.0, None), (0.16, 0.25, 50.0, None),
                                  (0.25, 0.45, 50.0, 1e5), (0.25, 0.45, 50.0, 1e4)):
        c, fr, out = caso(eta, xs, tau_m, tau_w)
        print("eta %.2f x* %.2f tau_m %.0f janela %s: c = %.4f ; fracao depositada na fusao %.3f" % (
            eta, xs, tau_m, tau_w, c, fr))
        for w, num, prev, r, fase in out:
            print("   w M = %.0e: 1-|T| %.5f ; previsto %.5f ; razao %.4f ; arg(1-T) %.3f (previsto -pi/8 = %.3f)" % (
                w, num, prev, r, fase, -np.pi / 8))


if __name__ == "__main__":
    main()
