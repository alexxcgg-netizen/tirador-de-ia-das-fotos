"""Figura de L13: transferencia lambda_l(beta)/lambda_l(1) e SNR em banda de memoria lenta (le exp29_canais.json).
Saida: figuras/e29_canais.png"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(AQUI, "..", "resultados", "exp29_canais.json")))
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "text.color": "#52514e", "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0",
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
b = r["transferencia"]["betas"]
for cor, l in zip(["#2a78d6", "#eb6834", "#1baf7a", "#52514e"], ["2", "3", "4", "8"]):
    ax[0].loglog(b, r["transferencia"]["tabela"][l], color=cor, lw=2, marker="o", ms=3, label="ℓ = %s" % l)
ax[0].set_xlabel("velocidade das partículas β")
ax[0].set_ylabel("λ_ℓ(β) / λ_ℓ(1)")
ax[0].set_title("Transferência fluência → memória (ℓ = 0, 1: zero)", loc="left", fontsize=9)
ax[0].legend(frameon=False, fontsize=8)
for cor, nome in zip(["#2a78d6", "#eb6834"], ["aLIGO", "CE"]):
    d = r["perfil"][nome]
    ax[1].loglog([x[0] for x in d], [x[2] for x in d], color=cor, lw=2, marker="o", ms=4, label=nome)
ax[1].set_xlabel("tempo de subida τ da memória (s)")
ax[1].set_ylabel("SNR / SNR do degrau rápido")
ax[1].set_title("Memória lenta (neutrinos de ~1 s) some da banda", loc="left", fontsize=9)
ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e29_canais.png"), dpi=140)
