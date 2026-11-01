"""Figura de L12: constantes c_L e folga da memoria nula de binarias (le resultados/exp28_*.json).
Saida: figuras/e28_limite_memoria.png"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(AQUI, "..", "resultados")
c = json.load(open(os.path.join(R, "exp28_constantes.json")))
f = json.load(open(os.path.join(R, "exp28_folga.json")))
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "text.color": "#52514e", "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0",
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
Lg = sorted(int(k) for k in c["L_grande"])
L2 = sorted(int(k) for k in c if k.isdigit())
ax[0].semilogx(L2, [c[str(L)]["c"] for L in L2], color="#2a78d6", lw=2, marker="o", ms=4, label="c_L (radiação com ℓ ≤ L)")
ax[0].semilogx(Lg, [c["L_grande"][str(L)] for L in Lg], color="#2a78d6", lw=1, ls="--", marker="s", ms=3,
               label="c_L, método 1D (L até 128)")
ax[0].axhline(4, color="#52514e", lw=1, ls=":", label="supremo 4 (feixe para o observador)")
ax[0].axhline(17 / 24, color="#eb6834", lw=1.5, ls="--", label="quadrupolo de binária, de lado: 17/24")
ax[0].set_xlabel("L (maior multipolo da radiação)")
ax[0].set_ylabel("sup |D Δh| / E_rad")
ax[0].set_title("Constante ótima da desigualdade memória–energia", loc="left", fontsize=9)
ax[0].legend(frameon=False, fontsize=7.5)
cores = ["#2a78d6", "#eb6834", "#1baf7a", "#52514e"]
sel = [(1.0, 0.0, 0.0), (1.0, 0.8, 0.8), (4.0, 0.0, 0.0), (8.0, 0.0, 0.0)]
for cor, (q, a, b) in zip(cores, sel):
    s = [x for x in f["sistemas"] if x["q"] == q and x["chi1"] == a and x["chi2"] == b][0]
    io = sorted(int(k) for k in s["iotas"])
    ax[1].plot(io, [s["iotas"][str(i)]["r_sobre_ce2"] for i in io], color=cor, lw=2, marker="o", ms=4,
               label="q=%g, χ=%g: |DΔh|/(c(e₂)E_jan)" % (q, a))
    ax[1].plot(io, [s["iotas"][str(i)]["limite_area_chi"] for i in io], color=cor, lw=1.2, ls="--",
               label="  idem com E_max da lei da área")
ax[1].set_xlabel("inclinação ι (graus)")
ax[1].set_ylabel("memória nula / limite")
ax[1].set_title("Folga em binárias reais (NRHybSur3dq8_CCE, desde 10 Hz)", loc="left", fontsize=9)
ax[1].legend(frameon=False, fontsize=6.5, ncol=1)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e28_limite_memoria.png"), dpi=140)
