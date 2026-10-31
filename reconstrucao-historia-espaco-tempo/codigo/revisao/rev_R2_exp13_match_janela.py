"""Revisao R2: o 1 - match do exp13 (q = 1, direcao chi_a) com janela no inicio, rampa no fim e busca fina.

O rev_R2_familia_perto.py mostrou que o match sem janela (deteccao.comparar) tem um piso de 1 - match
~ 2e-3 em aLIGO quando os inicios das duas ondas (10 Hz) nao coincidem em relacao ao pico. Aqui: os pares
do exp13 com (i) a busca do exp07, (ii) busca x16, (iii) busca x16 + cosseno de 0.5 s + rampa no fim.
Saida: resultados/revisao/rev_R2_exp13_match_janela.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import rev_R2_comum as C                                # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
M, D, IOTA, F = 65.0, 400.0, np.radians(50.0), 10.0
LISTA = B.lista_osc() + B.MODOS_M0
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def strain(c1, c2):
    t, h = B.gerar(1.0, c1, c2, f0=M * Dt.MSUN_S * F)
    ts, s = Dt.strain_observador(t, h, LISTA, M, D, IOTA)
    return ts, s, t[0]


for chi_s, deltas in ((-0.5, [0.0125, 0.025, 0.05, 0.1, 0.2, 0.3]),
                      (0.3, [0.0125, 0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5])):
    tsA, sA, t0A = strain(chi_s, chi_s)
    ys = {k: [] for k in ("base", "x16", "jan")}
    log("chi_s = %+.1f" % chi_s)
    for d in deltas:
        tsB, sB, t0B = strain(chi_s + d, chi_s - d)
        c0 = C.comparar(tsA, sA, tsB, sB, "aLIGO", F)
        c1 = C.comparar(tsA, sA, tsB, sB, "aLIGO", F, up=16)
        c2 = C.comparar(tsA, sA, tsB, sB, "aLIGO", F, up=16, taper=0.5, fim="rampa")
        for k, c in (("base", c0), ("x16", c1), ("jan", c2)):
            ys[k].append(1 - c["match"])
        log("  d = %.4f: inicio de B - inicio de A = %+.1f M | 1-match: exp07 %.3e ; x16 %.3e ; x16 + janela + rampa %.3e "
            "(rho_crit %.1f)" % (d, t0B - t0A, 1 - c0["match"], 1 - c1["match"], 1 - c2["match"],
                                 1 / np.sqrt(2 * (1 - c2["match"]))))
        del tsB, sB
    ld = np.log(deltas)
    log("  expoentes 1-match: exp07 %.2f ; x16 %.2f ; x16 + janela + rampa %.2f"
        % tuple(np.polyfit(ld, np.log(ys[k]), 1)[0] for k in ("base", "x16", "jan")))
    log("  coeficiente com janela: rho_crit * d = %s" % " ".join(
        "%.1f" % (d / np.sqrt(2 * y)) for d, y in zip(deltas, ys["jan"])))
with open(os.path.join(RES, "revisao", "rev_R2_exp13_match_janela.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
