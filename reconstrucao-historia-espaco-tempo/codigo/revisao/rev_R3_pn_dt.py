"""Revisor R3: convergencia de pn_excentrico em dt e o peso das pontas na soma de Riemann.

A grade de pn_excentrico termina exatamente na separatriz, onde o fluxo e maximo. A soma de Riemann de memorias.gram
(soma simples vezes dt, as duas pontas com peso inteiro) difere da regra do trapezio por (dt/2)(f_0 + f_N): erro de
primeira ordem em dt proporcional ao fluxo na separatriz. Aqui: dt = 0.5, 0.25, 0.125 com a soma do codigo e com pesos
de trapezio, e = 0 e e = 0.3.
Saida: resultados/revisao/rev_R3_pn_dt.txt
"""
import os
import sys

import numpy as np

from rev_R3_comum import B, CalculadoraMemoria, SAIDA, CODIGO, Dfrak, ethb2_de_escalar

sys.path.insert(0, CODIGO)
import pn_excentrico as PE                              # noqa: E402
import deteccao as Dt                                   # noqa: E402

NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
L = [(2, 2), (2, -2), (2, 0)]
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def mem(eta, e0, f0, dt, trapezio):
    t, h, r, a, e = PE.modos(eta, e0, f0, dt=dt)
    dt = t[1] - t[0]
    H = np.stack([h[k] for k in L], axis=1)
    Hd = B.derivada4(H, dt)
    w = np.full(len(t), dt)
    if trapezio:
        w[0] = w[-1] = dt / 2
    Bm = (Hd.T * w) @ Hd.conj()
    Am = (H.T * w) @ Hd.conj()
    m = CalculadoraMemoria(L).memorias_gram(Bm, Am)
    out = B._mem_m0(m)
    x0 = (np.pi * f0) ** (2 / 3)
    Mf = 1.0 - m["energia_total"] - 0.5 * eta * x0 * (1 - (0.75 + eta / 12) * x0)
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dK = -1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    return B.vetor(out)[0]


if __name__ == "__main__":
    eta = 1.2 / 2.2 ** 2
    f0 = 65.0 * Dt.MSUN_S * 10.0
    for e0 in (0.0, 0.3):
        for trap in (False, True):
            vs = {dt: mem(eta, e0, f0, dt, trap) for dt in (0.5, 0.25, 0.125)}
            d1 = (vs[0.25] - vs[0.5]) / np.abs(vs[0.125])
            d2 = (vs[0.125] - vs[0.25]) / np.abs(vs[0.125])
            log("e0 = %.1f, %s:" % (e0, "trapezio" if trap else "soma do codigo (pontas com peso inteiro)"))
            log("   v(0.25)-v(0.5):   " + " ".join("%s %+.1e" % (n, x) for n, x in zip(NOMES, d1)))
            log("   v(0.125)-v(0.25): " + " ".join("%s %+.1e" % (n, x) for n, x in zip(NOMES, d2)))
    with open(os.path.join(SAIDA, "rev_R3_pn_dt.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
