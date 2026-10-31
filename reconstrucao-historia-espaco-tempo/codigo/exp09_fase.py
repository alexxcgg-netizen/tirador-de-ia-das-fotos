"""Experimento 9: um observavel de memoria que preserva a fase.

As memorias convencionais sao INTEGRAIS no tempo de fluxos quadraticos e por isso perdem a fase
(Teorema 1). As TAXAS dessas memorias, no tempo, nao perdem. Para radiacao quase circular
(modos h_lm ~ a_lm e^{-i m phi(u)}) vale a relacao de orbita circular
    dE/du = Omega dJ_z/du,
e as duas taxas aparecem nos modos de memoria m = 0 da propria deformacao:
    d h_20/du   ~ fluxo de energia (taxa da memoria de deslocamento),
    h_30        ~ fluxo de momento angular (modo de memoria de spin, Nichols 2017).
Logo  Omega_mem(u) = (d h_20/du) / (C |h_30|),  com C fixado pela estrutura angular do modo (2,2).
Integrando: phi_mem(u) = int Omega_mem du; e a amplitude sai do fluxo de energia.

1. Calibra C com um sinal (2,2) sintetico e o codigo validado (exp01).
2. Aplica aos modos m = 0 do NRHybSur3dq8_CCE (memoria de RN, nivel C) e compara com a fase
   verdadeira do modo (2,2): erro em Omega, fase acumulada, sobreposicao da onda reconstruida.
3. Fontes artificiais A (chirp) e B (anti-chirp) do exp02: memorias integradas iguais, mas
   Omega_mem(u) diferentes.
Saida: resultados/exp09_fase.txt, figuras/e9_fase.png
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import fontes as F                                      # noqa: E402
from memorias import CalculadoraMemoria                 # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


# ---------- 1. calibracao com sinal (2,2) sintetico ----------
t = np.arange(0, 4000, 0.25)
Om = 0.02 + 0.03 * t / t[-1]
phi = np.cumsum(Om) * 0.25
A22 = 0.1 * (Om / 0.05) ** (2 / 3)
h22 = A22 * np.exp(-2j * phi)
L = [(2, 2), (2, -2)]
H = np.stack([h22, np.conj(h22)], axis=1)
Hd = B.derivada4(H, 0.25)
calc = CalculadoraMemoria(L, lmax_saida=4)
hB, _, dmem = calc.partes_instantaneas(H, Hd, [(2, 0), (3, 0)])
sl = slice(100, -100)
C_om = np.median(dmem[sl, 0].real / (np.abs(hB[sl, 1]) * Om[sl]))
C_E = np.median(dmem[sl, 0].real / np.abs(Hd[sl, 0]) ** 2)
log("Calibracao (modo 22 puro): d h20/du = C_E |dH22/du|^2 com C_E = %.6f ; Omega = (d h20/du)/(C |h30|) com C = %.6f"
    % (C_E, C_om))
log("  (previsao analitica: C = 5.0396 ; dispersao relativa de C ao longo do sinal: %.1e)"
    % (np.std(dmem[sl, 0].real / (np.abs(hB[sl, 1]) * Om[sl])) / C_om))


def reconstruir(t, h20, h30, h22):
    """Omega, fase e (2,2) reconstruidos so com os modos de memoria m = 0."""
    dt = t[1] - t[0]
    dh20 = np.gradient(h20.real, dt)
    Om_mem = dh20 / (C_om * np.abs(h30))
    Om_true = -0.5 * np.gradient(np.unwrap(np.angle(h22)), dt)
    return Om_mem, Om_true


def overlap(a, b):
    xc = np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b)))
    return float(np.max(np.abs(xc)) / np.sqrt(np.sum(np.abs(a) ** 2) * np.sum(np.abs(b) ** 2)))


# ---------- 2. memoria de RN (NRHybSur3dq8_CCE) ----------
resultados = {}
for (q, c1, c2) in [(1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (1.0, 0.6, 0.6), (3.0, 0.6, 0.0)]:
    t, h = B.gerar(q, c1, c2, f0=0.006, dt=0.25)
    Om_mem, Om_true = reconstruir(t, h[(2, 0)], h[(3, 0)], h[(2, 2)])
    tpk = t[np.argmax(np.abs(h[(2, 2)]))]
    insp = (t < tpk - 200) & (t > t[0] + 50)
    merg = (t >= tpk - 200) & (t < tpk + 30)
    erro_insp = np.median(np.abs(Om_mem[insp] / Om_true[insp] - 1))
    erro_merg = np.median(np.abs(Om_mem[merg] / Om_true[merg] - 1))
    # fase acumulada e onda reconstruida na inspiral (ate 200 M antes do pico)
    dt = t[1] - t[0]
    phi_mem = np.cumsum(Om_mem[insp]) * dt
    phi_true = np.cumsum(Om_true[insp]) * dt
    dphi = phi_mem - phi_true
    flux22 = np.gradient(h[(2, 0)].real, dt)[insp] / C_E
    A_rec = np.sqrt(np.maximum(flux22, 0)) / (2 * Om_mem[insp])
    h22_rec = A_rec * np.exp(-2j * phi_mem)
    ov = overlap(h[(2, 2)][insp], h22_rec)
    razao = np.max(np.abs(h[(3, 0)])) / np.max(np.abs(h[(2, 2)]))
    log("q=%.0f chi=(%.1f,%.1f): erro mediano em Omega: inspiral %.2e, fusao %.2e | fase acumulada %.1f rad em %d ciclos de (2,2), erro de fase %.2f rad | sobreposicao do (2,2) reconstruido (inspiral) %.4f | max|h30|/max|h22| = %.1e"
        % (q, c1, c2, erro_insp, erro_merg, 2 * phi_true[-1], int(phi_true[-1] / np.pi), 2 * np.abs(dphi[-1]), ov, razao))
    resultados[(q, c1, c2)] = (t - tpk, Om_mem, Om_true)
    # diagnostico: as mesmas taxas previstas pelas leis de balanco (modos oscilatorios, nivel A)
    Lo = B.lista_osc()
    Ho = np.stack([h[k] for k in Lo], axis=1)
    hBp, _, dmp = CalculadoraMemoria(Lo, lmax_saida=4).partes_instantaneas(Ho, B.derivada4(Ho, dt), [(2, 0), (3, 0)])
    Om_bal = dmp[:, 0].real / (C_om * np.abs(hBp[:, 1]))
    e_bi = np.median(np.abs(Om_bal[insp] / Om_true[insp] - 1))
    e_bm = np.median(np.abs(Om_bal[merg] / Om_true[merg] - 1))
    acum_pred = np.cumsum(dmp[:, 0].real) * dt
    acum_rn = h[(2, 0)].real - h[(2, 0)][0].real
    Dif = acum_rn - acum_pred
    log("      com as taxas das leis de balanco: erro em Omega inspiral %.2e, fusao %.2e | h20 de RN - memoria acumulada pelo fluxo: no fim %.1e (%.1f%% do total), maximo %.1e em t - t_pico = %.0f M"
        % (e_bi, e_bm, Dif[-1], 100 * Dif[-1] / acum_rn[-1], np.max(np.abs(Dif)), t[np.argmax(np.abs(Dif))] - tpk))

# ---------- 3. fontes artificiais: memorias iguais, Omega_mem diferente ----------
u, du = F.grade_tempo()
HA, _ = F.fonte_girante(u, du)
HBb = F.aplicar_fase(HA, F.fase_antichirp(len(u), du))
calcF = CalculadoraMemoria(F.LISTA, lmax_saida=4)
art = {}
for nome, Hx in (("A chirp", HA), ("B anti-chirp", HBb)):
    hBx, _, dmx = calcF.partes_instantaneas(Hx, F.derivar(Hx, du, 1), [(2, 0), (3, 0)])
    ok = np.abs(hBx[:, 1]) > 0.05 * np.max(np.abs(hBx[:, 1]))   # so onde o modo de spin e relevante
    Omx = np.full(len(u), np.nan)
    Omx[ok] = dmx[ok, 0].real / (C_om * np.abs(hBx[ok, 1]))
    art[nome] = Omx
    log("%s: Omega_mem no inicio da emissao = %.4f, no fim = %.4f" % (nome, Omx[ok][0], Omx[ok][-1]))

with open(os.path.join(AQUI, "..", "resultados", "exp09_fase.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")

import matplotlib                                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
tt, om, ot = resultados[(1.0, 0.0, 0.0)]
om = np.where(tt < 15, om, np.nan)      # depois do pico h30 -> 0 e a razao perde sentido
ax[0].plot(tt, ot, color="#52514e", lw=2.5, label="Ω verdadeira (fase do modo 2,2)")
ax[0].plot(tt, om, color="#2a78d6", lw=1.2, ls="--", label="Ω só dos modos de memória (2,0) e (3,0)")
tt2, om2, ot2 = resultados[(4.0, 0.0, 0.0)]
om2 = np.where(tt2 < 15, om2, np.nan)
ax[0].plot(tt2, om2, color="#eb6834", lw=1.2, ls="--", label="idem, q = 4")
ax[0].plot(tt2, ot2, color="#eb6834", lw=0.8, alpha=0.6)
ax[0].set_xlim(-1500, 60)
ax[0].set_ylim(0, 0.45)
ax[0].set_xlabel("tempo até o pico (M)")
ax[0].set_ylabel("frequência orbital Ω (1/M)")
ax[0].set_title("RN (NRHybSur3dq8_CCE): Ω recuperada da memória (até 15 M após o pico)", loc="left", fontsize=9)
ax[0].legend(frameon=False, fontsize=7)
for nome, cor in (("A chirp", "#2a78d6"), ("B anti-chirp", "#eb6834")):
    ax[1].plot(u, art[nome], color=cor, lw=1.5, label=nome)
ax[1].set_xlim(-3000, 2500)
ax[1].set_xlabel("u (M)")
ax[1].set_ylabel("Ω_mem (1/M)")
ax[1].set_title("Fontes artificiais: memórias integradas iguais, Ω_mem(u) oposta", loc="left", fontsize=9)
ax[1].legend(frameon=False, fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e9_fase.png"), dpi=140)
