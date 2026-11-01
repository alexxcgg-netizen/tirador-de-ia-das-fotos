"""exp33 (L10) - parte secular x termos de borda dos multipolos m != 0 das memorias (NRSur7dq4, nivel A).

Para sistemas alinhado (AL1) e precessantes (P1, P3, P6):
  (a) series acumuladas M_lm(t) = int_{t_i}^t (taxa) du do deslocamento (taxa nula) e do spin (int h^B du), para
      (2, 0), (2, 1), (2, 2), (3, 1), (3, 3), (4, 1); media movel sobre um periodo orbital local (parte secular);
      fracao secular = |media em t = -200 M| / |valor final| e o salto na fusao (ultimos 200 M);
  (b) dependencia do valor final no inicio da janela: inicio t_s varrido sobre um periodo orbital em torno de t_i
      (32 valores); amplitude da oscilacao de cada multipolo (termo de borda inicial) contra a media;
  (c) modelo "eixo precessante": taxa_2m(t) ~ rho(t) sqrt(4pi/5) conj(Y_2m(zc(t))), rho = projecao da taxa no padrao
      axissimetrico em torno do eixo coprecessante zc(t); acumulado do modelo contra o real (l = 2, deslocamento).
Saidas: resultados/exp33_secular.txt, figuras/e33_secular.png
"""
import os
import time

import numpy as np

import exp33_comum as C
import observaveis as O
from harmonicos import sYlm

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
F0 = C.F0_PADRAO
SIS = {"AL1": (1.2, (0, 0, 0.3), (0, 0, -0.2)),
       "P1": (2.0, (0.5, 0.0, 0.2), (0.0, -0.3, 0.1)),
       "P3": (3.0, (0.7, 0.0, 0.0), (0.0, 0.0, 0.1)),
       "P6": (4.0, (0.8, 0.0, -0.1), (0.0, 0.0, 0.1))}
SAIDA = [(2, 0), (2, 1), (2, 2), (3, 1), (3, 3), (4, 1)]
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def taxas(t, h, bloco=2048):
    calc = C.calculadora(tuple(C.MODOS))
    H = np.stack([h[k] for k in C.MODOS], axis=1)
    Hd = O.derivada(H, t[1] - t[0], 8)
    n = len(t)
    D = np.zeros((n, len(SAIDA)), dtype=complex)
    S = np.zeros_like(D)
    for i in range(0, n, bloco):
        hB, _, dm = calc.partes_instantaneas(H[i:i + bloco], Hd[i:i + bloco], SAIDA)
        D[i:i + bloco] = dm
        S[i:i + bloco] = hB
    del H, Hd
    return D, S


def acumular(t, R, t_s):
    """int_{t_s}^{t_k} R du para todo k (trapezio com o subintervalo parcial, como pesos_janela); 0 antes de t_s."""
    dt = t[1] - t[0]
    k = int(np.searchsorted(t, t_s, side="left"))
    a = (t_s - t[k - 1]) / dt
    L = t[k] - t_s
    out = np.zeros_like(R)
    Rs = (1 - a) * R[k - 1] + a * R[k]
    out[k] = 0.5 * L * (Rs + R[k])
    out[k + 1:] = out[k] + np.cumsum(0.5 * dt * (R[k:-1] + R[k + 1:]), axis=0)
    return out


def media_orbital(t, y, w_orb):
    """Media movel de y sobre um periodo orbital local 2 pi / w_orb(t)."""
    dt = t[1] - t[0]
    cs = np.concatenate([np.zeros((1,) + y.shape[1:], dtype=y.dtype), np.cumsum(y, axis=0)])
    out = np.full_like(y, np.nan)
    for j in range(len(t)):
        m = int(round(np.pi / w_orb[j] / dt))
        if j - m < 0 or j + m >= len(t):
            continue
        out[j] = (cs[j + m + 1] - cs[j - m]) / (2 * m + 1)
    return out


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    log("exp33_secular: parte secular e termos de borda dos m != 0 (NRSur7dq4, nivel A, f0 = %.4f)" % F0)
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.5))
    for a in ax.ravel():
        a.set_facecolor("#fcfcfb")
        a.grid(color="#e6e5e0")
        for s in a.spines.values():
            s.set_color("#52514e")
        a.tick_params(colors="#52514e")
    cores = {"AL1": "#52514e", "P1": "#2a78d6", "P3": "#eb6834", "P6": "#1baf7a"}
    for nome, (q, cA, cB) in SIS.items():
        t, h, dyn = C.gerar7(q, cA, cB, f_ref=F0)
        ti = C.instante_orbital(t, dyn["orbphase"], F0)
        w_orb = O.derivada(np.asarray(dyn["orbphase"])[:, None], t[1] - t[0], 8)[:, 0]
        D, S = taxas(t, h)
        MD = acumular(t, D, ti)
        MS = acumular(t, S, ti)
        mem, aux = C.memorias7(q, t, h, dyn, ti)
        log("")
        log("%s q %.2f chiA %s chiB %s ; t_i = %.1f M" % (nome, q, cA, cB, ti))
        log("  conferencia: acumulado final contra memorias7: deslocamento (2,1) %.2e, spin (2,1) %.2e (dif. relativa)" % (
            abs(MD[-1, 1] - mem["deslocamento"][(2, 1)]) / abs(mem["deslocamento"][(2, 1)]),
            abs(MS[-1, 1] - mem["spin"][(2, 1)]) / abs(mem["spin"][(2, 1)])))
        avD = media_orbital(t, MD, np.abs(w_orb))
        avS = media_orbital(t, MS, np.abs(w_orb))
        j200 = int(np.searchsorted(t, -200.0))
        j1000 = int(np.searchsorted(t, -1000.0))
        for k, lm in enumerate(SAIDA):
            fD, fS = abs(MD[-1, k]), abs(MS[-1, k])
            log("  %s: desl final %.3e ; |media orbital em -1000 M| / final %.3f ; em -200 M %.3f ; |oscilacao em -200 M|"
                " %.2e || spin final %.3e ; media -1000 M / final %.3f ; -200 M %.3f" % (
                    lm, fD, abs(avD[j1000, k]) / fD, abs(avD[j200, k]) / fD, np.std(MD[j200 - 200:j200 + 200, k] -
                                                                                  avD[j200 - 200:j200 + 200, k]),
                    fS, abs(avS[j1000, k]) / fS, abs(avS[j200, k]) / fS))
        # (b) inicio da janela num periodo orbital
        P = 2 * np.pi / abs(np.interp(ti, t, w_orb))
        ts = ti + np.linspace(-0.5, 0.5, 32, endpoint=False) * P
        fin = np.array([acumular(t, D, x)[-1] for x in ts])
        finS = np.array([acumular(t, S, x)[-1] for x in ts])
        X = np.stack([np.ones_like(ts), ts - ti], axis=1)

        def oscil(F):
            cf = np.linalg.lstsq(X, F, rcond=None)[0]
            r = F - X @ cf
            return np.max(np.abs(r), axis=0) / np.abs(cf[0]), np.abs(cf[1]) * P / np.abs(cf[0])
        oD, dD = oscil(fin)
        oS, dS = oscil(finS)
        log("  (b) inicio da janela varrido num periodo orbital (P = %.1f M): termo de borda inicial = max|residuo da reta|"
            "/|valor|, e deriva secular num periodo /|valor|" % P)
        log("      deslocamento: " + " ; ".join("%s %.1e (deriva %.1e)" % (lm, oD[k], dD[k]) for k, lm in enumerate(SAIDA)))
        log("      spin:         " + " ; ".join("%s %.1e (deriva %.1e)" % (lm, oS[k], dS[k]) for k, lm in enumerate(SAIDA)))
        # (c) modelo do eixo precessante para l = 2
        zc = np.array([C.eixo_copr(dyn["q_copr"][:, k]) for k in range(len(t))])
        th, ph = np.arccos(np.clip(zc[:, 2], -1, 1)), np.arctan2(zc[:, 1], zc[:, 0])
        Yc = np.stack([np.sqrt(4 * np.pi / 5) * np.conj(sYlm(0, 2, m, th, ph)) for m in (0, 1, 2)], axis=1)
        # rho = projecao da taxa (2, m) sobre o padrao axissimetrico girado (inclui m < 0 por realidade)
        D2 = {0: D[:, 0], 1: D[:, 1], 2: D[:, 2]}
        rho = np.real(D2[0] * np.conj(Yc[:, 0]) + 2 * np.real(D2[1] * np.conj(Yc[:, 1])) +
                      2 * np.real(D2[2] * np.conj(Yc[:, 2])))
        Dmod = rho[:, None] * Yc
        Mmod = acumular(t, Dmod, ti)
        avM = media_orbital(t, Mmod, np.abs(w_orb))
        for k, m in enumerate((0, 1, 2)):
            log("  (c) modelo do eixo precessante (2,%d): final modelo/real %.3f ; medias orbitais em -200 M modelo/real %.3f"
                " ; fase (graus) %.1f" % (m, abs(Mmod[-1, k]) / abs(MD[-1, m]), abs(avM[j200, k]) / abs(avD[j200, m]),
                                         np.degrees(np.angle(Mmod[-1, k] / MD[-1, m]))))
        sel = t >= ti
        tt = t[sel]
        ax[0, 0].plot(tt, np.abs(MD[sel, 1]) / abs(MD[-1, 0]), color=cores[nome], lw=0.8, label=nome)
        ax[0, 0].plot(tt, np.abs(avD[sel, 1]) / abs(MD[-1, 0]), color=cores[nome], lw=1.8, ls="--")
        ax[0, 1].plot(tt, np.abs(MS[sel, 1]) / abs(MS[-1, 0] if abs(MS[-1, 0]) > 0 else 1), color=cores[nome], lw=0.8,
                      label=nome)
        ax[1, 0].plot((ts - ti) / P, np.abs(fin[:, 2]) / np.abs(fin[:, 2]).mean(), color=cores[nome], marker="o", ms=3,
                      label=nome)
        if nome != "AL1":
            ax[1, 1].plot(tt, np.abs(MD[sel, 1]), color=cores[nome], lw=0.8, label=nome + " real")
            ax[1, 1].plot(tt, np.abs(Mmod[sel, 1]), color=cores[nome], lw=1.6, ls=":", label=nome + " modelo")
        del t, h, dyn, D, S, MD, MS
        log("  (%.0f s)" % (time.time() - T0))
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_xlim(-2000, 100)
    ax[0, 0].set_xlabel("t (M)", color="#52514e")
    ax[0, 0].set_ylabel("|desl (2,1)(t)| / |desl (2,0) final|", color="#52514e")
    ax[0, 0].set_title("deslocamento (2,1) acumulado; tracejado: media orbital", color="#52514e", fontsize=10)
    ax[0, 0].legend(fontsize=8)
    ax[0, 1].set_yscale("log")
    ax[0, 1].set_xlim(-2000, 100)
    ax[0, 1].set_xlabel("t (M)", color="#52514e")
    ax[0, 1].set_ylabel("|spin (2,1)(t)| / |spin (2,0) final|", color="#52514e")
    ax[0, 1].set_title("memoria de spin (2,1) acumulada", color="#52514e", fontsize=10)
    ax[1, 0].set_xlabel("deslocamento do inicio da janela (periodos orbitais)", color="#52514e")
    ax[1, 0].set_ylabel("|desl (2,2) final| / media", color="#52514e")
    ax[1, 0].set_title("dependencia no inicio da janela (termo de borda inicial)", color="#52514e", fontsize=10)
    ax[1, 0].legend(fontsize=8)
    ax[1, 1].set_xlim(-2000, 100)
    ax[1, 1].set_xlabel("t (M)", color="#52514e")
    ax[1, 1].set_ylabel("|desl (2,1)(t)|", color="#52514e")
    ax[1, 1].set_title("modelo do eixo precessante (pontilhado) contra o real", color="#52514e", fontsize=10)
    ax[1, 1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e33_secular.png"), dpi=130, facecolor="#fcfcfb")
    with open(os.path.join(RAIZ, "resultados", "exp33_secular.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    main()
