"""Experimento 5: a torre de memorias determina a forma de onda? (continuacao analitica)

As memorias de ordem n sao momentos temporais da noticia (news),
    mu_n = int u^n N(u) du     (Siddhant, Grant & Nichols 2024),
e sao os coeficientes de Taylor de N~(w) = int N e^{iwu} du em w = 0:
    N~(w) = sum_n (i w)^n mu_n / n!.
Se N decai rapido, N~ e inteira e a torre inteira determina N (Freidel, Pranzetti &
Raclariu 2022/24). Aqui medimos QUAO mal condicionada e essa reconstrucao.

Modelo: N(u) = exp(-u^2/2 sigma^2) cos(w0 u). Com a = w0 sigma (~ numero de ciclos),
    mu_n = sigma^(n+1) sqrt(2 pi) e^{-a^2/2} He_n(a) (-1)^(n/2)   (n par; zero se n impar),
    N~(w0) = (sigma sqrt(2pi)/2)(1 + e^{-2a^2}).
Cada momento e medido com erro relativo eps; reconstruo N~(w0) somando a serie truncada.

Segunda parte: cauda tardia N ~ c/u^2 (Laddha & Sen 2019). Os momentos com n >= 1 divergem
com o corte U: mu_1 ~ c ln U, mu_2 ~ c U. A torre nem existe sem regularizacao.
Saida: resultados/exp05_torre_momentos.txt, figuras/e5_torre_momentos.png
"""
import os

import mpmath as mp
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
mp.mp.dps = 150
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def termos(a, nmax):
    """T_n = (i w0)^n mu_n / n! em unidades de sigma sqrt(2pi) e^{-a^2/2}: T_n = a^n He_n(a)/n! (n par)."""
    a = mp.mpf(a)
    He = [mp.mpf(1), a]
    for k in range(1, nmax):
        He.append(a * He[k] - k * He[k - 1])
    T = []
    fat = mp.mpf(1)
    pot = mp.mpf(1)
    for k in range(nmax + 1):
        if k > 0:
            fat *= k
            pot *= a
        T.append(pot * He[k] / fat if k % 2 == 0 else mp.mpf(0))
    return T


rng = np.random.default_rng(3)
resultados = {}
log("a = w0 sigma | soma |T_n| / |N~(w0)| (amplificacao do ruido) | e^{a^2/4} (ajuste empirico)")
for a in (1, 2, 3, 4, 6, 8, 10, 12):
    nmax = int(4 * a * a + 60)
    T = termos(a, nmax)
    exato = (1 + mp.e ** (-2 * mp.mpf(a) ** 2)) / 2 * mp.e ** (mp.mpf(a) ** 2 / 2)   # mesma normalizacao
    amp = sum(abs(t) for t in T) / exato
    log("  a = %2d | %.3e | %.3e" % (a, float(amp), float(mp.e ** (mp.mpf(a) ** 2 / 4))))
    erros = {}
    for eps in (1e-3, 1e-6, 1e-12, 1e-24, 1e-48):
        ruido = rng.normal(size=nmax + 1)
        s = sum(t * (1 + mp.mpf(eps) * mp.mpf(float(x))) for t, x in zip(T, ruido))
        erros[eps] = float(abs(s - exato) / exato)
    resultados[a] = (float(amp), erros)

log()
log("erro relativo na reconstrucao de N~(w0) pela torre de momentos:")
log("  a  | " + " | ".join("eps=%.0e" % e for e in (1e-3, 1e-6, 1e-12, 1e-24, 1e-48)))
for a, (amp, erros) in resultados.items():
    log("  %2d | " % a + " | ".join("%9.1e" % erros[e] for e in sorted(erros, reverse=True)))
log()
log("Leitura: para errar menos de 10% e preciso eps < 0.1 / amplificacao; com a = 12 (~4 ciclos em +-sigma)")
log("ja se exige eps ~ %.0e. Uma fusao de buracos negros tem dezenas de ciclos na banda (a >> 12)." % (0.1 / resultados[12][0]))

# cauda 1/u^2: momentos com corte U
log()
log("Cauda N = c/u^2 para u > 1 (c = 1): momentos truncados em U")
for U in (1e2, 1e4, 1e6, 1e8):
    m1 = np.log(U)            # int_1^U u * u^-2 du
    m2 = U - 1                # int_1^U u^2 * u^-2 du
    log("  U = %.0e : mu_1 = %.2f   mu_2 = %.2e" % (U, m1, m2))
with open(os.path.join(AQUI, "..", "resultados", "exp05_torre_momentos.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")

import matplotlib                                                   # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(6.4, 3.8))
aa = list(resultados)
ax.semilogy(aa, [resultados[a][0] for a in aa], color="#2a78d6", lw=2, marker="o", ms=5,
            label="amplificação do ruído (calculada)")
ax.semilogy(aa, [np.exp(a * a / 4) for a in aa], color="#eb6834", lw=1.5, ls="--", label="e^(a²/4)")
ax.set_xlabel("a = ω₀σ  (cresce com o número de ciclos do sinal)")
ax.set_ylabel("erro na forma de onda / erro nas memórias")
ax.set_title("Reconstruir a onda a partir da torre de memórias: instabilidade explosiva", loc="left", fontsize=9)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e5_torre_momentos.png"), dpi=140)
