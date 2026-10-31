"""Revisor R3: normalizacao de pn_excentrico no limite circular contra as formulas de ordem dominante.

e0 = 0: desl20 de janela = (4/7) sqrt(5 pi/6) eta (x_f - x0) [Favata], spin30 = sqrt(3 pi/70) eta (x0^-1/2 - x_f^-1/2) [Nichols],
com x0 = (pi M f0)^(2/3) e x_f = 1/a_f (separatriz p = 6: a_f = 6). Erro esperado ~1e-3 (discretizacao, ver rev_R3_pn_dt).
Saida: resultados/revisao/rev_R3_pn_circular.txt
"""
import os
import sys

import numpy as np

from rev_R3_comum import B, CalculadoraMemoria, gram, SAIDA, CODIGO

sys.path.insert(0, CODIGO)
import pn_excentrico as PE                              # noqa: E402
import deteccao as Dt                                   # noqa: E402

L = [(2, 2), (2, -2), (2, 0)]
eta = 1.2 / 2.2 ** 2
f0 = 65.0 * Dt.MSUN_S * 10.0
linhas = []
for dt in (0.5, 0.125):
    t, h, r, a, e = PE.modos(eta, 0.0, f0, dt=dt)
    dt_ = t[1] - t[0]
    H = np.stack([h[k] for k in L], axis=1)
    m = CalculadoraMemoria(L).memorias_gram(*gram(H, B.derivada4(H, dt_), dt_))
    x0, xf = 1 / a[0], 1 / a[-1]
    d_esp = 4 / 7 * np.sqrt(5 * np.pi / 6) * eta * (xf - x0)
    s_esp = np.sqrt(3 * np.pi / 70) * eta * (x0 ** -0.5 - xf ** -0.5)
    s = ("dt=%.3f: x0 = %.5f (pi f0)^(2/3) = %.5f, x_f = %.5f ; desl20/Favata = %.6f ; spin30/Nichols = %.6f ; E/(eta(x_f-x0)/2) = %.6f"
         % (dt, x0, (np.pi * f0) ** (2 / 3), xf, m["deslocamento"][(2, 0)].real / d_esp, abs(m["spin"][(3, 0)]) / s_esp,
            m["energia_total"] / (0.5 * eta * (xf - x0))))
    print(s)
    linhas.append(s)
with open(os.path.join(SAIDA, "rev_R3_pn_circular.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
