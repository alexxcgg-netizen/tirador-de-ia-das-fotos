"""Figura e17_fibra.png: a fibra T0 de A no plano (q_B, chi2_B) e a regiao de existencia em T.

Le resultados/exp17_fibra.json. Paineis: chi1_B, M_B, D_B e iota_B das solucoes T0 (polidas quando disponiveis);
cinza = sem solucao com |chi1| <= 0.8; contorno da regiao com solucao T para algum phi'_B (todos os m);
marcador = numero de solucoes T0 distintas no ponto (> 1 seria fibra com varias folhas).
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import matplotlib                                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                          # noqa: E402
from matplotlib.colors import LinearSegmentedColormap    # noqa: E402

plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e", "text.color": "#52514e",
                     "font.size": 9, "axes.grid": False, "axes.spines.top": False, "axes.spines.right": False})
d = json.load(open(os.path.join(AQUI, "..", "resultados", "exp17_fibra.json")))
P = d["pontos"]
qs = sorted(set(v["qB"] for v in P.values()))
cs = sorted(set(v["c2B"] for v in P.values()))
nq, nc = len(qs), len(cs)
camp = {k: np.full((nc, nq), np.nan) for k in ("chi1", "M", "D", "iota")}
nsol = np.zeros((nc, nq), int)
nT = np.zeros((nc, nq), int)
for v in P.values():
    i, j = cs.index(v["c2B"]), qs.index(v["qB"])
    ok = [s["exato"] for s in v["T0"] if "exato" in s and s["exato"]["res"] < 1e-8 and not s["exato"]["no_limite"]]
    nsol[i, j] = len(ok)
    if ok:
        s = min(ok, key=lambda x: x["chi1"])                 # folha principal (a outra fica junto de chi1 = 0.8)
        for k in camp:
            camp[k][i, j] = np.degrees(s[k]) if k == "iota" else s[k]
    interior = lambda x: abs(abs(x["chi1"]) - 0.8) > 1e-6 and 45.5 < x["M"] < 129.5
    nT[i, j] = sum(any(x["res_interp"] < 1e-6 and interior(x) for x in lst) for lst in v["T"].values())
cmap = LinearSegmentedColormap.from_list("az", ["#d7e6f7", "#2a78d6", "#123c70"])
cmap.set_bad("#e6e5e0")
fig, axs = plt.subplots(1, 4, figsize=(14, 3.8), sharey=True)
tit = {"chi1": "χ1 da binária B", "M": "M_B (M☉)", "D": "D_B (Mpc)", "iota": "ι_B (graus)"}
dq, dc = qs[1] - qs[0], cs[1] - cs[0]
ext = [qs[0] - dq / 2, qs[-1] + dq / 2, cs[0] - dc / 2, cs[-1] + dc / 2]
for ax, k in zip(axs, ("chi1", "M", "D", "iota")):
    im = ax.imshow(np.ma.masked_invalid(camp[k]), origin="lower", extent=ext, aspect="auto", cmap=cmap)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    ax.contour(qs, cs, (nT > 0).astype(float), levels=[0.5], colors="#eb6834", linewidths=1.2)
    for i in range(nc):
        for j in range(nq):
            if nsol[i, j] > 1:
                ax.text(qs[j], cs[i], str(nsol[i, j]), ha="center", va="center", fontsize=7, color="#eb6834")
    ax.plot([1.2], [-0.2], marker="*", color="#1baf7a", ms=11, mec="#fcfcfb")
    ax.set_title(tit[k], fontsize=9)
    ax.set_xlabel("q_B")
axs[0].set_ylabel("χ2_B")
fig.suptitle("Fibra das quatro memórias de A (estrela verde) no observador: T0 (só m = 0) em cores; cinza: sem solução com |χ1| ≤ 0,8;"
             " laranja: borda da região com solução em T (todos os m, algum φ'_B)", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e17_fibra.png"), dpi=140)
print("pontos com solucao T0: %d de %d ; com mais de uma: %d ; com solucao T: %d" % ((nsol > 0).sum(), nsol.size, (nsol > 1).sum(), (nT > 0).sum()))
