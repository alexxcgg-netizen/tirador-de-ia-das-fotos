"""L03 (H03.8, alternativa): a parte nula da CM de banda na inspiral depende de dt (numerica) ou e do modelo?

q = 1, sem spin, M = 50 (adimensional em M f): parte nula da CM (2,0) por banda com dt = 0.25 e 0.125, e a sua razao a
parte ordinaria. Saida: resultados/exp20_cm_dt.txt
"""
import os

import numpy as np

import exp20_comum as C
from deteccao import MSUN_S
from harmonicos import Dfrak

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BORDAS = [0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.010]
linhas = []
for dt in (0.25, 0.125):
    rr = C.janelas(1.0, 0.0, 0.0, 50.0, [b / (50.0 * MSUN_S) for b in BORDAS], dt=dt)
    nula = np.array([m["cm"][(2, 0)].real + 1.5 * a["M_f"] * m["deslocamento"][(2, 0)].real / Dfrak(2) for m, a in rr])
    tot = np.array([m["cm"][(2, 0)].real for m, a in rr])
    fr = (nula[:-1] - nula[1:]) / (tot[:-1] - tot[1:])
    linhas.append("dt = %.3f: parte nula / CM total por banda %s" % (dt, " ".join("[%.3f,%.3f] %+.3e" % (BORDAS[j], BORDAS[j + 1], fr[j]) for j in range(len(fr)))))
    linhas.append("           parte nula por banda %s" % " ".join("%+.4e" % z for z in (nula[:-1] - nula[1:])))
print("\n".join(linhas))
open(os.path.join(RAIZ, "resultados", "exp20_cm_dt.txt"), "w").write("\n".join(linhas) + "\n")
