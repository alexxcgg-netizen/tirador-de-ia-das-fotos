"""Figura da linha L16 (exp40): anomalia, pares corrigidos e duas janelas.
Le resultados/exp40_anomalia.json, exp40_pares.json, exp40_duas_janelas.json, exp40_jacobiano.json.
Saida: figuras/e40_excentricas.png
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
AZ, LA, VE, TX, CI = "#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#a9a8a2"
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": TX, "xtick.color": TX, "ytick.color": TX, "text.color": TX,
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
an = json.load(open(os.path.join(RES, "exp40_anomalia.json")))
jac = json.load(open(os.path.join(RES, "exp40_jacobiano.json")))
pa = json.load(open(os.path.join(RES, "exp40_pares.json")))
dj = json.load(open(os.path.join(RES, "exp40_duas_janelas.json")))
fig, ax = plt.subplots(2, 2, figsize=(11, 7.6))

# (a) 1o harmonico em l0 de desl20 contra e0
E0S = (0.02, 0.05, 0.1, 0.2, 0.3)
for nome, cor in (("A", AZ), ("B", LA)):
    a = [an["SEOB"]["%s_%.2f" % (nome, e)]["desl20"]["a1"] for e in E0S]
    ax[0, 0].loglog(E0S, a, color=cor, marker="o", ms=4, lw=1.6, label="SEOBNRv5EHM, sistema %s" % nome)
e_p = (0.1, 0.2, 0.3)
for var, cor, rot in (("secular", CI, "PN, fim na separatriz secular"), ("r8", VE, "PN, fim em r(t) < 8 M")):
    a = [max(an["PN"]["%s_%.2f" % (var, e)]["desl20"]["a1"], 1e-12) for e in e_p]
    ax[0, 0].loglog(e_p, a, color=cor, marker="^", ms=4, lw=1.0, label=rot)
ax[0, 0].set_xlabel("e0 na frequência média de 10 Hz")
ax[0, 0].set_ylabel("amplitude relativa do 1º harmônico em l0 (deslocamento)")
ax[0, 0].set_title("(a) A anomalia muda a memória de deslocamento", loc="left", fontsize=9)
ax[0, 0].legend(frameon=False, fontsize=6.5)

# (b) desl20(l0) para o sistema B
L0 = np.arange(12) * 30.0
for e, cor in ((0.1, VE), (0.2, AZ), (0.3, LA)):
    v = np.array(an["SEOB"]["B_%.2f" % e]["desl20"]["valores"])
    ax[0, 1].plot(L0, v / v.mean() - 1, color=cor, marker="o", ms=3, lw=1.4, label="SEOBNRv5EHM, e0 = %.1f" % e)
ax[0, 1].set_xlabel("anomalia relativística inicial l0 (graus)")
ax[0, 1].set_ylabel("deslocamento / média − 1")
ax[0, 1].set_title("(b) Sistema B (q = 2): ~1 harmônico em l0", loc="left", fontsize=9)
ax[0, 1].legend(frameon=False, fontsize=7)

# (c) pares do exp12 com as correcoes
rot, v12, vcor, vres = [], [], [], []
for p in pa["pares"]:
    rot.append("e0 %.1f\nq %.1f" % (p["e0"], p["qB"]))
    v12.append(p["antes"]["exp12"]["max"])
    vcor.append(p["antes"]["com"]["max"])
    vres.append(p["depois"]["residuo"] if "depois" in p else np.nan)
x = np.arange(len(rot))
ax[1, 0].bar(x - 0.25, v12, 0.25, color=CI, label="cadeia do exp12")
ax[1, 0].bar(x, vcor, 0.25, color=LA, label="com (2,0) oscilatório e E_lig excêntrica")
ax[1, 0].bar(x + 0.25, vres, 0.25, color=AZ, label="resolvido de novo com as correções")
ax[1, 0].axhline(1e-5, color=TX, lw=0.8, ls="--")
ax[1, 0].text(-0.4, 1.3e-5, "tremor do modelo", fontsize=7)
ax[1, 0].set_yscale("log")
ax[1, 0].set_xticks(x)
ax[1, 0].set_xticklabels(rot, fontsize=7)
ax[1, 0].set_ylabel("max |diferença relativa| das 4 memórias")
ax[1, 0].set_title("(c) Pares de uma janela: as correções não os destroem", loc="left", fontsize=9)
ax[1, 0].legend(frameon=False, fontsize=7)

# (d) duas janelas
sol = dj["solucoes"] + jac["buscas"]
rr = [s["max_res"] for s in sol]
cores = [CI if s["e0_fixo"] is not None else (VE if "controle" in s["rotulo"] else AZ) for s in sol]
ax[1, 1].bar(np.arange(len(sol)), rr, color=cores)
ax[1, 1].axhline(1e-5, color=TX, lw=0.8, ls="--")
ax[1, 1].set_yscale("log")
ax[1, 1].set_xticks(np.arange(len(sol)))
ax[1, 1].set_xticklabels([str(k + 1) for k in range(len(sol))], fontsize=7)
ax[1, 1].set_xlabel("partida (azul: e0, l0 livres desde pares do exp12 e da família R4;\n"
                    "cinza: controle circular; verde: família circular + e0 = 0,03)")
ax[1, 1].set_ylabel("melhor max |resíduo| (7 equações)")
ax[1, 1].set_title("(d) Duas janelas (10 e 20 Hz), 8 incógnitas", loc="left", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "e40_excentricas.png"), dpi=140)
print("ok")
