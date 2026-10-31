"""Revisor R3: decomposicao da taxa instantanea hB_30 (nivel A) por conjuntos de modos no comeco da janela (parte PN).

Confere que a razao |hB_30|/LO = 0.92 do nivel A vem das correcoes PN de amplitude do (2,2) mais modos superiores.
Saida: resultados/revisao/rev_R3_taxa_pares.txt
"""
import os

import numpy as np

from rev_R3_comum import B, CalculadoraMemoria, x_de_h22, h30_pn_lo, SAIDA

linhas = []
CONJ = {"(2,2)": [(2, 2), (2, -2)],
        "(2,2)+(3,2)": [(2, 2), (2, -2), (3, 2), (3, -2)],
        "(2,2)+(3,2)+(4,4)": [(2, 2), (2, -2), (3, 2), (3, -2), (4, 4), (4, -4)],
        "todos": B.lista_osc()}
for q in (1.0, 8.0):
    t, h = B.gerar(q, 0.0, 0.0)
    eta = q / (1 + q) ** 2
    sel = slice(0, 2048)
    x = x_de_h22(t, h[(2, 2)])[sel]
    lo = h30_pn_lo(x, eta)
    k = 200
    s = "q=%.0f x=%.4f: |hB_30|/LO por conjunto de modos: " % (q, x[k])
    for nome, L in CONJ.items():
        c = CalculadoraMemoria(L)
        H = np.stack([h[kk] for kk in L], axis=1)
        Hd = B.derivada4(H, 0.25)
        hB, _, _ = c.partes_instantaneas(H[sel], Hd[sel], [(3, 0)])
        s += "%s %.4f; " % (nome, abs(hB[k, 0]) / lo[k])
    s += "(|h22|/|h22_LO|)^2 = %.4f" % ((np.abs(h[(2, 2)][sel][k]) / (8 * np.sqrt(np.pi / 5) * eta * x[k])) ** 2)
    print(s)
    linhas.append(s)
    del t, h
with open(os.path.join(SAIDA, "rev_R3_taxa_pares.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
