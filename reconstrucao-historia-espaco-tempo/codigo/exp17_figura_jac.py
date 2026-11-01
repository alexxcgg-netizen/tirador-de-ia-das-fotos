"""Figura e17_jacobiano.png: valores singulares do jacobiano das memorias no observador em funcao de iota.

Painel 1-3: ponto A (M 65, q 1.2, chi (0.3, -0.2), D 400 Mpc), escala 'abs' (linhas / |F(50 graus)|), conjuntos T0, T
(phi' = 0.7) e O (phi' = 0.7), casos 'livre' (cheio) e 'iota e D conhecidos' (tracejado), e o limiar tau (Weyl).
Painel 4: ultimo valor singular de T0 livre na grade (faixa min-max e mediana sobre q, chi1, chi2, M) e de T0 intrinseco.
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_analise_jac as J                            # noqa: E402

import matplotlib                                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                          # noqa: E402

plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e", "text.color": "#52514e",
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#52514e"]
dA = J.carregar_A()
FrA = J.fref(dA, 1)
ios = np.radians(np.concatenate([np.linspace(0.2, 89.8, 120), [90.0]]))
fig, axs = plt.subplots(1, 4, figsize=(13, 3.6))
for ax, (conj, phi, tit) in zip(axs[:3], (("T0", 0.0, "T0: quatro memórias, só m = 0"),
                                          ("T", 0.7, "T: quatro memórias, todos os m (φ' = 0,7)"),
                                          ("O", 0.7, "O: deslocamento e spin, todos os m"))):
    for caso, ls in (("livre", "-"), ("iotaD", "--")):
        S, T = [], []
        for io in ios:
            r = J.analisar(dA, 1, io, phi, conj, caso, "abs", FrA)
            S.append(r["sv"])
            T.append(r["tau"])
        S = np.array(S)
        for k in range(S.shape[1]):
            ax.semilogy(np.degrees(ios), S[:, k], ls, color=CORES[k], lw=1.2 if ls == "-" else 0.9,
                        label=("σ%d" % (k + 1)) if caso == "livre" else None)
        if caso == "livre":
            ax.semilogy(np.degrees(ios), T, ":", color="#9a9893", lw=1, label="limiar τ")
    ax.set_title(tit, fontsize=9)
    ax.set_xlabel("inclinação ι (graus)")
    ax.set_ylim(1e-9, 30)
axs[0].set_ylabel("valores singulares (linhas / |F(50°)|)")
axs[0].legend(fontsize=7, frameon=False, loc="lower right")
axs[0].text(2, 2e-9, "cheio: todos os parâmetros livres\ntracejado: ι e D conhecidos", fontsize=7)
# painel 4: grade
ax = axs[3]
for caso, cor, nome in (("livre", "#2a78d6", "T0 livre (σ4)"), ("intr", "#eb6834", "T0, D e ι fixos (σ4)")):
    mins, meds, maxs = [], [], []
    for io in J.IOTAS:
        v = []
        for i, p in enumerate(J.PONTOS):
            dp = J.carregar_ponto(i)
            for j in range(len(J.MS)):
                r = J.analisar(dp, j, np.radians(io), 0.0, "T0", caso, "abs", J.fref(dp, j))
                v.append(r["sv"][-1])
        v = np.array(v)
        mins.append(v.min())
        meds.append(np.median(v))
        maxs.append(v.max())
    ax.fill_between(J.IOTAS, mins, maxs, color=cor, alpha=0.18)
    ax.semilogy(J.IOTAS, meds, "o-", color=cor, ms=3, lw=1.2, label=nome)
ax.set_yscale("log")
ax.set_title("grade: q, χ1, χ2, M (faixa mín–máx)", fontsize=9)
ax.set_xlabel("inclinação ι (graus)")
ax.legend(fontsize=7, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e17_jacobiano.png"), dpi=140)
print("ok")
