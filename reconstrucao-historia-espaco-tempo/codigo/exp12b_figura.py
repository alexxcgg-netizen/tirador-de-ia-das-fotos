"""Figura do exp12: binaria circular A e excentrica B com as mesmas quatro memorias (SEOBNRv5EHM).

Le resultados/exp12_pares.json; desenha h_+ no observador e a frequencia de onda instantanea do modo (2,2).
Saida: figuras/e12_excentrica.png
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import deteccao as Dt                                   # noqa: E402
import exp12_excentricas_imr as E                       # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
dados = json.load(open(os.path.join(AQUI, "..", "resultados", "exp12_pares.json")))
A = dados["A"]
p = [x for x in dados["pares"] if x["e0"] == 0.3 and x["qB"] == 2.0][0]
parB = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"], e=p["e0"])

import matplotlib                                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for par, cor, nome in ((A, "#2a78d6", "A circular: M = 65, q = 1,2, χ = (+0,30, −0,20), ι = 50°, D = 400 Mpc"),
                       (parB, "#eb6834", "B e₀ = 0,3 (10 Hz): M = %.1f, q = 2, χ = (%+.2f, 0), ι = %.0f°, D = %.0f Mpc"
                        % (parB["M"], parB["c1"], np.degrees(parB["iota"]), parB["D"]))):
    t, h = E.onda(par)
    ts, s = Dt.strain_observador(t, h, E.LISTA, par["M"], par["D"], par["iota"])
    tp = ts[np.argmax(np.abs(s))]
    off = 0.0 if par is A else -3.0
    ax[0].plot(ts - tp, s.real * 1e21 + off, color=cor, lw=0.8, label=nome)
    Ms = par["M"] * Dt.MSUN_S
    f22 = -np.gradient(np.unwrap(np.angle(h[(2, 2)])), t) / (2 * np.pi * Ms)
    ax[1].plot(ts - tp, f22, color=cor, lw=1.2)
ax[0].set_xlim(-0.6, 0.03)
ax[0].set_ylim(-4.6, 1.6)
ax[0].set_yticks([])
ax[0].set_xlabel("tempo até o pico (s)")
ax[0].set_ylabel("h₊ × 10²¹ (B deslocada para baixo)")
ax[0].set_title("Mesmas quatro memórias (diferença ~1e-5, o ruído numérico do modelo); match aLIGO %.2f"
                % p["match_ligo"], loc="left", fontsize=8)
ax[0].legend(frameon=False, fontsize=6.5, loc="upper left")
ax[1].set_xlim(-3.0, 0.03)
ax[1].set_ylim(0, 150)
ax[1].set_xlabel("tempo até o pico (s)")
ax[1].set_ylabel("frequência de onda do modo (2,2) (Hz)")
ax[1].set_title("A excentricidade aparece na frequência, não nas memórias", loc="left", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e12_excentrica.png"), dpi=140)
print("ok")
