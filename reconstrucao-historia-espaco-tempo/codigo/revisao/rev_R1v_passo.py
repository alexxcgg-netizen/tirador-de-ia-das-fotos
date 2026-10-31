"""R1v: sensibilidade da derivada em ln M ao passo (jacobiano de duas janelas, item 12)."""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402

A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
linhas = []


def F(M, ff):
    mem, _, _, _ = B.memorias_fisicas(A["q"], A["c1"], A["c2"], M, ff, nivel="A")
    v = B.valores_fisicos(mem, A["iota"], M, A["D"])
    return np.array([v[k] for k in B.TIPOS])


for ff in (10.0, 20.0):
    F0 = F(A["M"], ff)
    for h in (1e-4, 3e-4, 1e-3, 3e-3):
        d = (F(A["M"] * np.exp(h), ff) - F(A["M"] * np.exp(-h), ff)) / (2 * h) / np.abs(F0)
        s = "f_i = %.0f Hz, passo %.0e: d F/d ln M / |F| (desl, spin, CM, giro) = %s" % (ff, h, np.array2string(d, precision=5))
        print(s, flush=True)
        linhas.append(s)
with open(os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1v_passo.txt"), "w") as fh:
    fh.write("\n".join(linhas) + "\n")
