"""Figura do exp38/exp39 (linha L19): degrau de memoria de RN x degrau previsto pelo fluxo; atraso de centroide;
mensurabilidade. Le resultados/exp38_series.npz, exp38_cm_atraso.json e exp39_cm_mensuravel.json.
Saida: figuras/e38_cm_atraso.png
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "..", "figuras")
AZ, LA, VE, TX = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": TX, "xtick.color": TX, "ytick.color": TX, "text.color": TX,
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
ser = np.load(os.path.join(RES, "exp38_series.npz"))
js = json.load(open(os.path.join(RES, "exp38_cm_atraso.json")))
m39 = json.load(open(os.path.join(RES, "exp39_cm_mensuravel.json")))
fig, ax = plt.subplots(2, 2, figsize=(11, 7.6))

# (a) degraus normalizados perto da fusao, q = 1 e q = 4
for nome, cor, rot in (("q1.0_+0.0_+0.0", AZ, "q = 1"), ("q4.0_+0.0_+0.0", LA, "q = 4")):
    u = ser[nome + "_u"]
    R, S = ser[nome + "_R2"], ser[nome + "_S2"]
    o = [x for x in js if abs(x["q"] - float(nome[1:4])) < 1e-9 and x["c1"] == 0.0][0]
    d = o["l2"]["delta_ord"]
    s = (u > -60) & (u < 80)
    us, Rs, Ss = u[s], R[s] - np.interp(-60, u, R), S[s] - np.interp(-60, u, S)
    ax[0, 0].plot(us, Rs / Rs[-1], color=cor, lw=1.8, label="%s: modo (2,0) de RN" % rot)
    ax[0, 0].plot(us, Ss / Ss[-1], color=cor, lw=1.0, ls="--", label="%s: memória nula pelo fluxo" % rot)
    ax[0, 0].plot(us + d, Ss / Ss[-1], color=TX, lw=0.7, ls=":")
ax[0, 0].plot([], [], color=TX, lw=0.7, ls=":", label="fluxo atrasado de M_f/2")
ax[0, 0].set_xlabel("tempo desde o pico do (2,2) (M)")
ax[0, 0].set_ylabel("degrau desde −60 M (normalizado)")
ax[0, 0].set_title("(a) O degrau de RN não é o do fluxo atrasado de M_f/2", loc="left", fontsize=9)
ax[0, 0].legend(frameon=False, fontsize=7)

# (b) D(u) contra -delta_ord dS/du, q = 1
nome = "q1.0_+0.0_+0.0"
u = ser[nome + "_u"]
D = ser[nome + "_R2"] - ser[nome + "_S2"]
tx = ser[nome + "_taxa2"]
o = [x for x in js if x["q"] == 1.0 and x["c1"] == 0.0][0]
step = ser[nome + "_S2"][-1]
s = (u > -100) & (u < 120)
ax[0, 1].plot(u[s], (D[s] - np.interp(-100, u, D)) / step, color=AZ, lw=1.6, label="D = RN − fluxo (q = 1)")
ax[0, 1].plot(u[s], -o["l2"]["delta_ord"] * tx[s] / step, color=LA, lw=1.4, label="previsão do atraso: −(M_f/2) dS/du")
q_ = o["qnm"]
t16 = u[s] >= 16
ax[0, 1].set_xlabel("tempo desde o pico do (2,2) (M)")
ax[0, 1].set_ylabel("fração do deslocamento final")
ax[0, 1].set_title("(b) Transiente: toque (2,0,0) com período 2π/%.3f M, não atraso" % q_["omega_200"][0],
                   loc="left", fontsize=9)
ax[0, 1].legend(frameon=False, fontsize=7)

# (c) atraso de centroide em funcao do inicio u_s
us_ = [-1000, -500, -300, -200, -100]
for o in js:
    dc = [o["l2"]["delta_c"][str(x)] for x in us_]
    cor = AZ if o["c1"] == 0.0 and o["c2"] == 0.0 else (LA if o["c1"] > 0 else VE)
    ax[1, 0].plot(us_, dc, color=cor, lw=1.0, marker="o", ms=3)
ax[1, 0].axhline(0.5, color=TX, lw=1.0, ls="--")
ax[1, 0].text(-990, 0.62, "M_f/2 (parte ordinária)", fontsize=7)
ax[1, 0].plot([], [], color=AZ, marker="o", ms=3, label="sem spin, q = 1 a 8")
ax[1, 0].plot([], [], color=LA, marker="o", ms=3, label="com spin positivo")
ax[1, 0].plot([], [], color=VE, marker="o", ms=3, label="q = 1, χ = −0,6")
ax[1, 0].set_xlabel("início da comparação u_s (M antes do pico)")
ax[1, 0].set_ylabel("atraso de centroide (M)")
ax[1, 0].set_title("(c) Atraso de centroide depende do início: a deriva domina", loc="left", fontsize=9)
ax[1, 0].legend(frameon=False, fontsize=7)

# (d) mensurabilidade
dets = ["aLIGO_10", "A+_10", "ET_10", "CE_10"]
x = np.arange(len(dets))
for k, (o, cor) in enumerate(zip(m39, (VE, AZ, LA, TX))):
    ax[1, 1].bar(x + (k - 1.5) * 0.2, [o["det"][d]["razao_tot"] for d in dets], width=0.2, color=cor,
                 label="M = %.0f M☉" % o["M"])
ax[1, 1].set_yscale("log")
ax[1, 1].axhline(1.0, color=TX, lw=0.8, ls="--")
ax[1, 1].set_xticks(x)
ax[1, 1].set_xticklabels(["aLIGO", "A+", "ET", "CE"])
ax[1, 1].set_ylabel("atraso / σ do atraso (D = 400 Mpc, ι = 50°)")
ax[1, 1].set_title("(d) Medir M_f pelo atraso: só CE chega a ~1–3σ", loc="left", fontsize=9)
ax[1, 1].legend(frameon=False, fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "e38_cm_atraso.png"), dpi=140)
print("ok")
