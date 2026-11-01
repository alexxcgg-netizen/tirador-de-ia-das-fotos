"""Experimento 19 (L18): espectro de multipolos m = 0 de memoria ate l = 10.

Para q = 1, 2, 4, 8 e spins (0, 0), (+0.6, +0.6), (-0.6, -0.6), (+0.6, -0.6), janela desde M f0 = 0.004 (como o
estudo global do exp06), nivel A (fluxo dos modos oscilatorios), deslocamento de janela. Para cada tipo de memoria:
|X_l0| por l, decaimento com l, quantos multipolos acima de 1e-2 e 1e-3 do maior, numero efetivo
(razao de participacao (sum |X|^2)^2 / sum |X|^4) e dependencia em q.
Conteudo de modos de entrada (a memoria de l alto exige modos de entrada de l alto):
  (a) NRHybSur3dq8_CCE: (2,2), (2,1), (3,3), (3,2), (4,4), (4,3), (5,5) e m < 0 (o padrao das linhas);
  (b) NRHybSur3dq8 (sem CCE): acrescenta (3,1) e (4,2);
  (c) subconjuntos de (a): so (2,+-2); l_in <= 3; l_in <= 4.
Conferencia analitica: a ordem dominante pos-newtoniana do deslocamento (Favata 2009, eq. 4.3; parte de inspiral),
  H_60 ~ -(4195/(1419264 sqrt 273)) x (1 - 3612 eta/839), H_80 ~ (75601/(213497856 sqrt 119)) x^2 (1 - 452070/75601 eta + 733320/75601 eta^2),
  H_10,0 ~ -(525221/(6452379648 sqrt 154)) x^3 (1 - ...), relativos a H_20 = 5/(14 sqrt 6).
Saidas: resultados/exp19_espectro.txt, resultados/exp19_espectro.json, figuras/e19_espectro.png
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402
from deteccao import MSUN_S                              # noqa: E402

F0 = 0.004
M_REF = F0 / (MSUN_S * 10.0)            # M tal que f0 = 0.004 com f_ini = 10 Hz (so define a janela)
QS = (1.0, 2.0, 4.0, 8.0)
SPINS = ((0.0, 0.0), (0.6, 0.6), (-0.6, -0.6), (0.6, -0.6))
LS = {"deslocamento": (2, 4, 6, 8, 10), "spin": (3, 5, 7, 9), "cm": (2, 4, 6, 8, 10), "giroscopica": (1, 3, 5, 7, 9)}
CCE = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3), (5, 5)]
HYB = CCE + [(3, 1), (4, 2)]
SAIDA = os.path.join(AQUI, "..", "resultados", "exp19_espectro")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def com_neg(L):
    out = []
    for (l, m) in L:
        out += [(l, m), (l, -m)]
    return out


def espectro(q, c1, c2, modos, modelo="NRHybSur3dq8_CCE"):
    r = C.memorias_varias(q, c1, c2, [M_REF], lmax=10, media=False, modos=com_neg(modos), modelo=modelo)[0]
    mem = r["mem_ti"]
    out = {}
    for tipo, ls in LS.items():
        vals = []
        for l in ls:
            z = mem[tipo].get((l, 0), 0j)
            vals.append(float(np.abs(z)))
        out[tipo] = vals
    return out, r["aux"]


def pn_desl(eta, x):
    H2 = 5 / (14 * np.sqrt(6))
    H4 = 1 / (504 * np.sqrt(2))
    H6 = 4195 / (1419264 * np.sqrt(273)) * x * abs(1 - 3612 / 839 * eta)
    H8 = 75601 / (213497856 * np.sqrt(119)) * x ** 2 * abs(1 - 452070 / 75601 * eta + 733320 / 75601 * eta ** 2)
    H10 = 525221 / (6452379648 * np.sqrt(154)) * x ** 3 * abs(1 - 79841784 / 9979199 * eta + 198570240 / 9979199 * eta ** 2
                                                           - 172307520 / 9979199 * eta ** 3)
    return np.array([H2, H4, H6, H8, H10]) / H2


def resumo(vals):
    v = np.array(vals)
    mx = v.max()
    rel = v / mx
    n2 = int(np.sum(rel >= 1e-2))
    n3 = int(np.sum(rel >= 1e-3))
    npart = float((v ** 2).sum() ** 2 / (v ** 4).sum())
    return rel, n2, n3, npart


if __name__ == "__main__":
    t0 = time.time()
    dados = {}
    log("Experimento 19 (L18): multipolos m = 0 de memoria ate l = 10 (nivel A, janela desde M f0 = %.3f)" % F0)
    log("Modelo padrao: NRHybSur3dq8_CCE com os modos %s (e m < 0)" % CCE)
    log("Colunas: |X_l0| / max_l |X_l0| por tipo; n(>=1e-2), n(>=1e-3); N_ef = (sum|X|^2)^2/sum|X|^4")
    for q in QS:
        for (c1, c2) in SPINS:
            esp, aux = espectro(q, c1, c2, CCE)
            dados[(q, c1, c2, "CCE")] = esp
            log("")
            log("q = %.0f, chi = (%+.1f, %+.1f): E_janela = %.5f, M_f = %.5f" % (q, c1, c2, aux["E_janela"], aux["M_f"]))
            for tipo, ls in LS.items():
                rel, n2, n3, npart = resumo(esp[tipo])
                log("  %-12s l = %-16s |X|max = %.3e  rel = %s  n2 = %d n3 = %d N_ef = %.3f"
                    % (tipo, ",".join(str(l) for l in ls), max(esp[tipo]), " ".join("%.1e" % x for x in rel), n2, n3, npart))
    # conteudo de modos de entrada
    log("")
    log("Conteudo de modos de entrada (spins nulos): deslocamento |X_l0|/|X_20| para l = 2..10")
    sub = {"so (2,2)": [(2, 2)], "l_in<=3": [(2, 2), (2, 1), (3, 3), (3, 2)], "l_in<=4": [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)],
           "CCE (l_in<=5)": CCE}
    for q in QS:
        for nome, L in sub.items():
            esp, _ = espectro(q, 0.0, 0.0, L)
            dados[(q, 0.0, 0.0, nome)] = esp
            r = np.array(esp["deslocamento"]) / esp["deslocamento"][0]
            rs = np.array(esp["spin"]) / esp["spin"][0] if esp["spin"][0] > 0 else np.zeros(4)
            log("  q = %.0f  %-14s desl %s | spin (l=3..9)/l=3 %s" % (q, nome, " ".join("%.2e" % x for x in r),
                                                                      " ".join("%.2e" % x for x in rs)))
        esp, _ = espectro(q, 0.0, 0.0, HYB, modelo="NRHybSur3dq8")
        dados[(q, 0.0, 0.0, "HYB")] = esp
        r = np.array(esp["deslocamento"]) / esp["deslocamento"][0]
        rs = np.array(esp["spin"]) / esp["spin"][0]
        log("  q = %.0f  %-14s desl %s | spin (l=3..9)/l=3 %s" % (q, "NRHybSur3dq8+(3,1),(4,2)", " ".join("%.2e" % x for x in r),
                                                                  " ".join("%.2e" % x for x in rs)))
        eta = q / (1 + q) ** 2
        for x in (1 / 6, 0.2, 0.25):
            log("  q = %.0f  PN dominante (inspiral ate x = %.3f): desl %s" % (q, x, " ".join("%.2e" % v for v in pn_desl(eta, x))))
    log("(%.0f s)" % (time.time() - t0))
    with open(SAIDA + ".txt", "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(SAIDA + ".json", "w") as fh:
        json.dump({"%s|%s|%s|%s" % k: v for k, v in dados.items()}, fh, indent=0)

    # figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                         "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                         "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                         "axes.spines.right": False, "text.color": "#52514e"})
    cores = {1.0: "#2a78d6", 2.0: "#eb6834", 4.0: "#1baf7a", 8.0: "#52514e"}
    nomes = {"deslocamento": "deslocamento", "spin": "spin", "cm": "centro de massa", "giroscopica": "giroscópica"}
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.4), sharey=True)
    for ax, tipo in zip(axs, LS):
        for q in QS:
            v = np.array(dados[(q, 0.0, 0.0, "CCE")][tipo])
            ax.semilogy(LS[tipo], v / v.max(), "o-", color=cores[q], lw=1.2, ms=4, label="q = %.0f" % q)
            v = np.array(dados[(q, 0.6, 0.6, "CCE")][tipo])
            ax.semilogy(LS[tipo], v / v.max(), "s--", color=cores[q], lw=0.8, ms=3, alpha=0.7)
        ax.axhline(1e-2, color="#c9c8c2", lw=0.8)
        ax.axhline(1e-3, color="#c9c8c2", lw=0.8, ls=":")
        ax.set_title(nomes[tipo], fontsize=9)
        ax.set_xlabel("ℓ")
    axs[0].set_ylabel("|X_ℓ0| / máx")
    axs[0].legend(fontsize=7, frameon=False)
    fig.suptitle("Espectro de multipolos m = 0 da memória (nível A, NRHybSur3dq8_CCE; cheio: χ = 0, tracejado: χ = (0,6; 0,6))",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(AQUI, "..", "figuras", "e19_espectro.png"), dpi=140)
