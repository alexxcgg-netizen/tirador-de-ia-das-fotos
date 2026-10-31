"""Experimento 4: historias que nao deixam nenhum sinal no infinito nulo futuro.

Perturbacao de paridade impar, l = 2, de um buraco negro de Schwarzschild (M = 1):
    d2psi/dt2 - d2psi/dr*2 + V(r) psi = 0,   V = (1 - 2/r)(6/r^2 - 6/r^3).

Construcao (teoria de espalhamento: Dafermos-Rodnianski-Shlapentokh-Rothman 2018,
Masaood 2022): comeco no fim da historia com um pacote perto do horizonte caindo para
dentro, evoluo para tras no tempo e uso o resultado como dado inicial. Evoluindo para
frente, uma onda que chega de longe encontra, na barreira de potencial, um pulso que sai
de perto do horizonte; as partes refletidas se cancelam e TODA a energia cai no buraco.

Historia A: nada acontece (psi = 0).
Historia B: o dado ajustado (onda entra, tudo cai no horizonte).
Historia C: a mesma onda de entrada, sem o pulso de compensacao (parte e refletida).

Esquema leapfrog (exatamente reversivel no tempo), diferencas finitas de 4a ordem.
Saida: resultados/exp04_horizonte.txt, figuras/e5_horizonte.png
"""
import os

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def r_de_rstar(rs):
    """Inverte r* = r + 2 ln(r/2 - 1): r = 2(1 + W(exp(r*/2 - 1))), W por Newton em w + ln w = x."""
    x = rs / 2.0 - 1.0
    w = np.exp(np.minimum(x, 1.0))          # para x << 0, W(e^x) = e^x (pode dar 0 em ponto flutuante)
    m = x > -30
    wm = np.where(x[m] > 1, x[m], np.exp(np.minimum(x[m], 1.0)))
    for _ in range(60):
        wm = wm - (wm + np.log(wm) - x[m]) / (1.0 + 1.0 / wm)
    w[m] = wm
    return 2.0 * (1.0 + w)


dr = 0.1
rs = np.arange(-2000.0, 2000.0 + dr / 2, dr)
r = r_de_rstar(rs)
V = (1 - 2 / r) * (6 / r ** 2 - 6 / r ** 3)
dt = 0.05
ok = rs > -10   # mais perto do horizonte r/2-1 perde precisao por cancelamento (so na conferencia)
log("max V = %.4f em r = %.3f (r* = %.2f); verificacao r(r*) para r* > -10: max|r* - (r + 2 ln(r/2-1))| = %.1e"
    % (V.max(), r[np.argmax(V)], rs[np.argmax(V)], np.max(np.abs(rs[ok] - (r[ok] + 2 * np.log(r[ok] / 2 - 1))))))


def laplaciano(p):
    out = np.zeros_like(p)
    out[2:-2] = (-p[4:] + 16 * p[3:-1] - 30 * p[2:-2] + 16 * p[1:-3] - p[:-4]) / (12 * dr ** 2)
    return out


def evoluir(p0, p1, passos, sondas=()):
    """Leapfrog: p_{n+1} = 2 p_n - p_{n-1} + dt^2 (psi'' - V psi). Registra psi nas sondas."""
    reg = {s: [] for s in sondas}
    idx = {s: int(round((s - rs[0]) / dr)) for s in sondas}
    pm, pc = p0.copy(), p1.copy()
    for _ in range(passos):
        pn = 2 * pc - pm + dt ** 2 * (laplaciano(pc) - V * pc)
        for s in sondas:
            i = idx[s]
            reg[s].append(pc[i - 2:i + 3].copy())
        pm, pc = pc, pn
    return pm, pc, {s: np.array(v) for s, v in reg.items()}


def pacote(x, x0=-80.0, s=8.0, w0=0.4):
    return np.exp(-0.5 * ((x - x0) / s) ** 2) * np.cos(w0 * (x - x0))


# 1) fim da historia: pacote caindo no horizonte, psi = g(t + r*). Invertendo o tempo ele "sai".
#    Evoluo no tempo invertido tau: psi(tau, r*) = g(-tau + r*) -> p(tau=0) = g(r*), p(tau=dt) = g(r* - dt)
T_rev = 700.0
n_rev = int(round(T_rev / dt))
q0 = pacote(rs)
# segunda camada de tempo de uma onda que so sai, segundo a relacao de dispersao DISCRETA do esquema
# (leapfrog + laplaciano de 4a ordem): 2(1 - cos w dt)/dt^2 = (30 - 32 cos k dr + 2 cos 2k dr)/(12 dr^2)
k = 2 * np.pi * np.fft.fftfreq(len(rs), d=dr)
Lk = (30 - 32 * np.cos(k * dr) + 2 * np.cos(2 * k * dr)) / (12 * dr ** 2)
wd = np.sign(k) * np.arccos(1 - 0.5 * dt ** 2 * Lk) / dt
q1 = np.real(np.fft.ifft(np.fft.fft(q0) * np.exp(-1j * wd * dt)))
qa, qb, _ = evoluir(q0, q1, n_rev)
# 2) dado inicial da historia B (inverter o tempo de novo troca a ordem dos dois niveis)
B0, B1 = qb.copy(), qa.copy()
# 3) historia C: so a onda que chega de longe (apaga a regiao r* < 0, onde esta o pulso de compensacao)
corte = 0.5 * (1 + np.tanh((rs - 0.0) / 5.0))
C0, C1 = B0 * corte, B1 * corte
log("energia ~ int (psi_t^2 + psi_r^2 + V psi^2) no dado inicial: B = %.4e, parte de dentro (r*<0) = %.4e, C = %.4e"
    % tuple(np.sum(((b1 - b0) / dt) ** 2 + np.gradient(b0, dr) ** 2 + V * b0 ** 2) * dr
            for b0, b1 in ((B0, B1), (B0 * (1 - corte), B1 * (1 - corte)), (C0, C1))))

T_fwd = 1800.0
n_fwd = int(round(T_fwd / dt))
obs, hor = 800.0, -600.0
res = {}
for nome, (a0, a1) in {"B": (B0, B1), "C": (C0, C1)}.items():
    _, _, reg = evoluir(a0, a1, n_fwd, sondas=(obs, hor))
    # parte que sai, (d/dt - d/dr*) psi, no observador; parte que entra no horizonte, (d/dt + d/dr*) psi
    out = {}
    for s, sinal in ((obs, -1), (hor, +1)):
        P = reg[s]
        dpdt = np.gradient(P[:, 2], dt)
        dpdr = (-P[:, 4] + 8 * P[:, 3] - 8 * P[:, 1] + P[:, 0]) / (12 * dr)
        out[s] = dpdt + sinal * dpdr
    res[nome] = out
    log("historia %s: int Phi_out^2 dt no observador (r*=%g) = %.3e ; int Phi_in^2 dt no horizonte (r*=%g) = %.3e ; max|psi| no observador = %.2e"
        % (nome, obs, np.sum(out[obs] ** 2) * dt, hor, np.sum(out[hor] ** 2) * dt, np.max(np.abs(reg[obs][:, 2]))))
log("historia A (nada acontece): tudo zero por construcao.")
log("Conclusao: A e B sao indistinguiveis no infinito nulo (B nao emite nada para fora), mas em B")
log("uma onda inteira caiu no buraco negro. C mostra que, sem o ajuste, parte seria refletida.")
with open(os.path.join(AQUI, "..", "resultados", "exp04_horizonte.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")

# figura: diagrama espaco-tempo de B e C e sinal que sai
import matplotlib                                                    # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                      # noqa: E402
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def diagrama(a0, a1, passos=36000, cada=300, sub=20):
    pm, pc = a0.copy(), a1.copy()
    quadros = []
    for k in range(passos):
        if k % cada == 0:
            quadros.append(np.abs(pc[::sub]))
        pn = 2 * pc - pm + dt ** 2 * (laplaciano(pc) - V * pc)
        pm, pc = pc, pn
    return np.array(quadros)


fig, ax = plt.subplots(1, 3, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1, 1, 1.2]})
for j, (nome, (a0, a1)) in enumerate({"B: tudo cai no horizonte": (B0, B1), "C: sem o pulso de compensação": (C0, C1)}.items()):
    D = diagrama(a0, a1)
    ext = [rs[0], rs[-1], 0, T_fwd]
    ax[j].imshow(D, origin="lower", aspect="auto", extent=ext, cmap="Blues", vmin=0, vmax=0.6 * D.max())
    ax[j].set_title(nome, loc="left", fontsize=9)
    ax[j].set_xlabel("r* (unidades de M)")
    ax[j].axvline(obs, color="#eb6834", lw=1, ls="--")
    ax[j].text(obs + 30, 80, "observador", color="#eb6834", fontsize=7)
ax[0].set_ylabel("t (unidades de M)")
tt = np.arange(n_fwd) * dt
for nome, cor in (("C", "#eb6834"), ("B", "#2a78d6")):
    y = np.abs(res[nome][obs]) + 1e-300
    ax[2].semilogy(tt, y, color=cor, lw=1.2, label="história %s" % nome)
ax[2].set_ylim(1e-18, 1)
ax[2].set_xlabel("t (unidades de M)")
ax[2].set_ylabel("|(∂t − ∂r*)ψ| no observador")
ax[2].legend(frameon=False, fontsize=8)
ax[2].set_title("O que chega lá fora", loc="left", fontsize=9)
ax[2].grid(True, color="#e6e5e0")
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e5_horizonte.png"), dpi=140)
