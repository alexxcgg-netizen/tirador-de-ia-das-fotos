"""Verificacao adversarial D1 (H1.7b): identidade do limite (2,2) com sinais SINTETICOS (sem substituto).

h22(t) arbitrario (amplitude e fase aleatorias e suaves, |h22| != 0 nas pontas), h2-2 = conj(h22). Calcula as memorias
com memorias.CalculadoraMemoria([(2,2),(2,-2)]) pelas matrizes de Gram e compara as razoes com as constantes do
relatorio (J20/E = 0.0735760, S30/H = -0.0291996, G10/H = 0.162868, G30/H = -0.0533109, CM nula = 0) e com as
formulas analiticas desta verificacao:
  C_E = sqrt30/(42 sqrt pi) ; C_J = sqrt210/(280 sqrt pi) ;
  G10/H = (1/4) int (|-2Y22|^2 - |-2Y2-2|^2) Y10 dOmega = (1/4)(5/4) sqrt(3/4pi)(16/15) ;
  G30/H = (1/4) Hel30 - Dfrak(3) spin_pot30, Hel30 = (5/4) sqrt(7/4pi) (4/35).
Tambem: um sinal com h2-2 != conj(h22) (precessante 'de brinquedo') deve QUEBRAR a proporcionalidade.
Saida: resultados/ver_D1_reducao22.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from memorias import CalculadoraMemoria, gram       # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "ver_D1_reducao22.txt")


def suave(rng, t, n=6):
    y = np.zeros_like(t)
    for _ in range(n):
        y += rng.normal() * np.sin(rng.uniform(0.2, 3) * t + rng.uniform(0, 6))
    return y


if __name__ == "__main__":
    calc = CalculadoraMemoria([(2, 2), (2, -2)], lmax_saida=8)
    rng = np.random.default_rng(1)
    t = np.linspace(0, 40, 40001)
    dt = t[1] - t[0]
    L = ["Sinais sinteticos (2,+-2); razoes por sinal"]
    an = dict(CE=np.sqrt(30) / (42 * np.sqrt(np.pi)), CJ=np.sqrt(210) / (280 * np.sqrt(np.pi)),
              G10=0.25 * 1.25 * np.sqrt(3 / (4 * np.pi)) * 16 / 15, Hel30=1.25 * np.sqrt(7 / (4 * np.pi)) * 4 / 35)
    L.append("analitico: C_E = %.7f ; C_J = %.7f ; G10/H = %.6f ; (1/4) Hel30/H = %.7f" % (an["CE"], an["CJ"], an["G10"],
                                                                                           0.25 * an["Hel30"]))
    for k in range(6):
        amp = 1.0 + 0.3 * suave(rng, t) ** 2
        fase = np.cumsum(1.0 + 0.5 * np.tanh(suave(rng, t))) * dt * rng.uniform(0.5, 3) + suave(rng, t)
        h22 = amp * np.exp(-1j * fase)
        if k < 5:
            h2m2 = np.conj(h22)
        else:                                   # quebra a simetria de reflexao
            h2m2 = np.conj(h22) * (0.7 + 0.2j)
        H = np.stack([h22, h2m2], axis=1)
        Hd = np.gradient(H, dt, axis=0, edge_order=2)
        m = calc.memorias_gram(*gram(H, Hd, dt))
        hd22 = Hd[:, 0]
        w = np.full(len(t), dt)
        w[0] = w[-1] = dt / 2
        E = np.sum(w * np.abs(hd22) ** 2)
        Hh = np.sum(w * np.imag(np.conj(h22) * hd22))
        borda = abs(h22[-1]) ** 2 - abs(h22[0]) ** 2
        L.append("sinal %d%s: J20/E = %.7f ; S30/H = %.7f ; G10/H = %.6f ; G30/H = %.7f ; CM nula 20 = %.1e (borda |h|^2 = %.2f) ;"
                 " S30/G10 = %.6f" % (k, " (h2-2 != conj h22)" if k == 5 else "",
                                      m["deslocamento"][(2, 0)].real / E, m["spin"][(3, 0)].imag / Hh,
                                      m["giroscopica"][(1, 0)].real / Hh, m["giroscopica"][(3, 0)].real / Hh,
                                      abs(m["cm"][(2, 0)]), borda, m["spin"][(3, 0)].imag / m["giroscopica"][(1, 0)].real))
    print("\n".join(L))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
