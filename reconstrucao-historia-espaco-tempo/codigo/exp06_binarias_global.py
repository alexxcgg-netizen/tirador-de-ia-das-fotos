"""Experimento 6: memorias de binarias reais (NRHybSur3dq8_CCE) e degenerescencia global.

Parte 1. Os tres niveis (A quadratico, B com termos cubicos, C memoria completa de RN) em varios
         sistemas; massa final e recuo contra o ajuste de RN NRSur3dq8Remnant (surfinBH).
Parte 2. Degenerescencia global (ceu inteiro, referencial da fonte, janela fixa M f0 = 0.004):
         vetor de 7 multipolos m = 0 [desl (2,0),(4,0); spin (3,0); CM (2,0),(4,0); giro (1,0),(3,0)]
         com escala exata em M (desl ~ M, demais ~ M^2). Para cada q_B, minimiza a maior diferenca
         relativa sobre (M_B/M_A, chi1_B, chi2_B). Tambem: valores singulares do jacobiano.
Saida: resultados/exp06_binarias_global.txt, figuras/e6_degenerescencia_global.png
"""
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
ESCALA = np.array([1, 1, 2, 2, 2, 2, 2])          # potencia de M de cada componente do vetor
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
REFERENCIAS = {"A1": (1.2, 0.3, -0.2), "A2": (3.0, 0.6, 0.0), "A3": (1.0, -0.5, -0.5)}
QS = [1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0]
_cache = {}


def v_adim(q, c1, c2, nivel="A"):
    k = (round(q, 10), round(c1, 10), round(c2, 10), nivel)
    if k not in _cache:
        mem, aux = B.memorias(q, c1, c2, nivel=nivel)
        _cache[k] = (B.vetor(mem)[0], aux)
    return _cache[k]


def vetor_escalado(mu, q, c1, c2, nivel="A"):
    v, _ = v_adim(q, c1, c2, nivel)
    return v * mu ** ESCALA


def melhor_par(alvo, qB, nivel="A", x0=(1.0, 0.0, 0.0)):
    def res(p):
        mu, c1, c2 = p
        return (vetor_escalado(mu, qB, c1, c2, nivel) - alvo) / np.abs(alvo)
    r = least_squares(res, x0, bounds=([0.2, -0.8, -0.8], [5.0, 0.8, 0.8]), diff_step=1e-3, xtol=1e-12, ftol=1e-12,
                      max_nfev=120)
    return r.x, np.max(np.abs(r.fun))


def _caso(arg):
    nome, qB = arg
    qa, ca1, ca2 = REFERENCIAS[nome]
    alvo = vetor_escalado(1.0, qa, ca1, ca2)
    melhor = None
    for x0 in [(1.0, 0.0, 0.0), (1.0, 0.5, -0.5), (1.0, -0.5, 0.5)]:
        xs, r = melhor_par(alvo, qB, x0=x0)
        if melhor is None or r < melhor[0]:
            melhor = (r, xs)
    return nome, qB, melhor


if __name__ == "__main__":
    import multiprocessing as mp
    import surfinBH
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)

    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    c_kms = 299792.458
    log("Parte 1: niveis A, B, C (diferenca relativa de cada multipolo em relacao a C)")
    log("%-22s | %s | %s" % ("sistema (q,chi1,chi2)", " ".join("%8s" % n for n in NOMES), "M_f nosso/RN   recuo nosso/RN (km/s)"))
    sistemas = [(1, 0, 0), (2, 0, 0), (4, 0, 0), (8, 0, 0), (1, 0.6, 0.6), (1, -0.6, -0.6), (3, 0.6, 0.0), (2, 0.8, -0.8)]
    difA = []
    for (q, c1, c2) in sistemas:
        vA, auxA = v_adim(q, c1, c2, "A")
        vB, _ = v_adim(q, c1, c2, "B")
        vC, _ = v_adim(q, c1, c2, "C")
        dA = (vA - vC) / np.abs(vC)
        dB = (vB - vC) / np.abs(vC)
        difA.append(dA)
        mf, _ = fit.mf(q, [0, 0, c1], [0, 0, c2])
        vf, vfe = fit.vf(q, [0, 0, c1], [0, 0, c2])
        log("A: %-19s | %s | %.4f/%.4f  %6.1f/%6.1f+-%.1f" % (
            (q, c1, c2), " ".join("%+8.4f" % x for x in dA), auxA["M_f"], mf,
            np.linalg.norm(auxA["v_recuo"]) * c_kms, np.linalg.norm(vf) * c_kms, np.linalg.norm(vfe) * c_kms))
        log("B: %-19s | %s |" % ("", " ".join("%+8.4f" % x for x in dB)))
    difA = np.array(difA)
    log("max |A - C|/|C| por componente: " + " ".join("%s %.3f" % (n, x) for n, x in zip(NOMES, np.max(np.abs(difA), axis=0))))
    log("Valores absolutos (nivel C) dos sistemas:")
    for (q, c1, c2) in sistemas:
        vC, aux = v_adim(q, c1, c2, "C")
        log("  %-16s " % ((q, c1, c2),) + " ".join("%s=%+.5f" % (n, x) for n, x in zip(NOMES, vC)))

    log()
    log("Parte 2: degenerescencia global (nivel A)")
    curvas = {}
    for nome, (qa, ca1, ca2) in REFERENCIAS.items():
        alvo = vetor_escalado(1.0, qa, ca1, ca2)
        p0 = np.array([0.0, qa, ca1, ca2])
        J = np.zeros((7, 4))
        for j in range(4):
            e = np.zeros(4)
            e[j] = 1e-3
            vp = vetor_escalado(np.exp(p0[0] + e[0]), qa + e[1], ca1 + e[2], ca2 + e[3])
            vm = vetor_escalado(np.exp(p0[0] - e[0]), qa - e[1], ca1 - e[2], ca2 - e[3])
            J[:, j] = (vp - vm) / (2e-3) / np.abs(alvo)
        U, S, Vt = np.linalg.svd(J)
        log("%s %s: valores singulares do jacobiano relativo = %s ; direcao mais fraca (lnM, q, chi1, chi2) = %s"
            % (nome, (qa, ca1, ca2), np.array2string(S, precision=3), np.array2string(Vt[-1], precision=3)))
        curvas[nome] = [(qa, 0.0, (1.0, ca1, ca2))]
    tarefas = [(nome, qB) for nome in REFERENCIAS for qB in QS if abs(qB - REFERENCIAS[nome][0]) > 1e-9]
    t0 = time.time()
    with mp.get_context("spawn").Pool(3) as pool:
        for nome, qB, (r, xs) in pool.imap(_caso, tarefas):
            curvas[nome].append((qB, r, tuple(xs)))
            log("   %s q_B = %4.2f: menor diferenca maxima = %.3e com M_B/M_A = %.4f, chi1 = %+.3f, chi2 = %+.3f"
                % (nome, qB, r, *xs))
    for nome in curvas:
        curvas[nome].sort()
    log("   (%.0f s)" % (time.time() - t0))
    with open(os.path.join(AQUI, "..", "resultados", "exp06_binarias_global.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                         "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                         "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    cores = {"A1": "#2a78d6", "A2": "#eb6834", "A3": "#1baf7a"}
    for nome, res in curvas.items():
        qa = REFERENCIAS[nome][0]
        xs = [r[0] for r in res if abs(r[0] - qa) > 1e-9]
        ys = [r[1] for r in res if abs(r[0] - qa) > 1e-9]
        ax.semilogy(xs, ys, color=cores[nome], lw=2, marker="o", ms=4,
                    label="%s: q=%.1f, χ=(%.1f, %.1f)" % ((nome,) + REFERENCIAS[nome]))
    ax.axhline(0.01, color="#52514e", lw=1, ls="--")
    ax.text(6.0, 0.0112, "1% (diferença entre os níveis A e C)", ha="right", fontsize=7, color="#52514e")
    ax.set_xlabel("razão de massas q_B imposta à binária B")
    ax.set_ylabel("menor diferença máxima nas memórias")
    ax.set_title("Céu inteiro: quão parecidas as memórias de outra binária podem ficar", loc="left", fontsize=9)
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(AQUI, "..", "figuras", "e6_degenerescencia_global.png"), dpi=140)
