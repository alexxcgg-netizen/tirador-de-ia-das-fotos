"""Experimento 7: pares de binarias com as MESMAS quatro memorias para um observador real.

Sistema A (tipo GW150914, referencial do detector): M = 65 M_sol, q = 1.2, chi1 = +0.3,
chi2 = -0.2, D = 400 Mpc, inclinacao 50 graus. Janela das memorias de spin, CM e giroscopica
a partir de f = 10 Hz (inicio da observacao); deslocamento total.

Para um observador, as quatro memorias valem (M = G M_det/c^3, D em segundos):
  Delta h_+ = (M/D) d(iota; lambda),  int h_x du = (M^2/D) s(...),  int h_+ du = (M^2/D) c(...),
  Phi_giro = (M/D)^2 g(...),   lambda = (q, chi1, chi2) e a janela depende de M.
Sao 4 equacoes para 6 incognitas (M, D, iota, q, chi1, chi2): a familia degenerada tem
dimensao >= 2. Fixo q_B e chi2_B; D_B sai da equacao do deslocamento; resolvo as outras tres em
(iota_B, chi1_B, M_B). Depois comparo as formas de onda completas (aLIGO e ET).
Saida: resultados/exp07_binarias_observador.txt, figuras/e7_pares_observador.png
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


F_FIS = 10.0
A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
TIPOS = B.TIPOS
_cache = {}


def mem_cache(q, c1, c2, M, nivel="A"):
    """So as memorias ficam no cache: a forma de onda desde 10 Hz ocupa ate centenas de MB por ponto."""
    k = (round(q, 9), round(c1, 9), round(c2, 9), round(M, 9), nivel)
    if k not in _cache:
        mem, aux, _, _ = B.memorias_fisicas(q, c1, c2, M, F_FIS, nivel=nivel)
        _cache[k] = (mem, {c: v for c, v in aux.items() if c != "t"})
    return _cache[k]


def fisicos(par, nivel="A"):
    mem, aux = mem_cache(par["q"], par["c1"], par["c2"], par["M"], nivel)
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"]), aux


def onda(par):
    """Modos (t, h) do ponto, gerados de novo."""
    return B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * F_FIS, dt=0.25)


def resolver(alvo, qB, c2B, x0, nivel="A"):
    """Resolve (iota, chi1, M) com D eliminado pela equacao do deslocamento."""
    def montar(p):
        iota, c1, M = p
        par = dict(M=M, q=qB, c1=c1, c2=c2B, D=1.0, iota=iota)
        v1, _ = fisicos(par, nivel)
        par["D"] = v1["deslocamento"] / alvo["deslocamento"]     # D_B (Mpc) que iguala o deslocamento
        return par

    def res(p):
        par = montar(p)
        v, _ = fisicos(par, nivel)
        return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in ("spin", "cm", "giroscopica")])

    r = least_squares(res, x0, bounds=([0.05, -0.8, 35.0], [np.pi - 0.05, 0.8, 250.0]),
                      diff_step=1e-4, xtol=1e-14, ftol=1e-14, gtol=1e-14)
    return montar(r.x), np.max(np.abs(r.fun))


def _resolver_caso(arg):
    alvo, qB, c2B = arg
    melhor = None
    for x0 in [(A["iota"], 0.0, 60.0), (np.radians(30), 0.4, 80.0), (np.radians(80), -0.4, 50.0),
               (np.radians(120), 0.0, 70.0)]:
        try:
            par, r = resolver(alvo, qB, c2B, x0)
        except Exception:                               # fora do dominio do modelo
            continue
        if melhor is None or r < melhor[1]:
            melhor = (par, r)
        if melhor[1] < 1e-9:
            break
    return melhor


def figura(pares):
    """A e dois pares B com as mesmas quatro memorias (residuo < 1e-5), h_+ perto da fusao."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                         "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                         "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                         "axes.spines.right": False})
    lista = B.lista_osc() + B.MODOS_M0
    exatos = [p for p in pares if max(abs(x) for x in p["dif"].values()) < 1e-5 and p["c2B"] == 0.0 and p["qB"] in (2.0, 3.0)]
    fig, ax = plt.subplots(len(exatos) + 1, 1, figsize=(8, 2.4 * (len(exatos) + 1)), sharex=True)
    tA, hA = onda(A)
    tsA, sA = Dt.strain_observador(tA, hA, lista, A["M"], A["D"], A["iota"])
    ax[0].plot(tsA - tsA[np.argmax(np.abs(sA))], sA.real * 1e21, color="#2a78d6", lw=0.8)
    ax[0].set_title("A: M = 65, q = 1,2, χ = (+0,3, −0,2), ι = 50°, D = 400 Mpc", loc="left", fontsize=8)
    for i, p in enumerate(exatos, 1):
        tB, hB = onda(dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"]))
        tsB, sB = Dt.strain_observador(tB, hB, lista, p["M"], p["D"], p["iota"])
        ax[i].plot(tsB - tsB[np.argmax(np.abs(sB))], sB.real * 1e21, color="#eb6834", lw=0.8)
        ax[i].set_title("B: M = %.1f, q = %.0f, χ = (%+.2f, %+.1f), ι = %.0f°, D = %.0f Mpc — memórias iguais a A (dif. %.0e); match aLIGO %.2f"
                        % (p["M"], p["qB"], p["c1"], p["c2B"], np.degrees(p["iota"]), p["D"],
                           max(abs(x) for x in p["dif"].values()), p["match_ligo"]), loc="left", fontsize=8)
    for a in ax:
        a.set_ylabel("h₊ × 10²¹")
        a.set_xlim(-0.25, 0.05)
    ax[-1].set_xlabel("tempo até o pico (s)")
    fig.tight_layout()
    fig.savefig(os.path.join(AQUI, "..", "figuras", "e7_pares_observador.png"), dpi=140)


if __name__ == "__main__":
    t0 = time.time()
    alvo, auxA = fisicos(A)
    tA, hA = onda(A)
    log("Sistema A: M = %.1f, q = %.2f, chi = (%+.2f, %+.2f), D = %.0f Mpc, iota = %.1f graus"
        % (A["M"], A["q"], A["c1"], A["c2"], A["D"], np.degrees(A["iota"])))
    log("  memorias no observador: desl Delta h_+ = %.4e ; spin int h_x du = %.4e s ; CM int h_+ du = %.4e s ; giro = %.4e rad"
        % (alvo["deslocamento"], alvo["spin"], alvo["cm"], alvo["giroscopica"]))
    log("  recuo |v| = %.1f km/s ; M_f/M = %.4f" % (np.linalg.norm(auxA["v_recuo"]) * 299792.458, auxA["M_f"]))
    lista = B.lista_osc() + B.MODOS_M0
    tsA, sA = Dt.strain_observador(tA, hA, lista, A["M"], A["D"], A["iota"])
    pares = []
    casos = [(1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0), (6.0, 0.0), (2.0, 0.5), (3.0, -0.5)]
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(4) as pool:
        sols = pool.map(_resolver_caso, [(alvo, qB, c2B) for qB, c2B in casos])
    for (qB, c2B), melhor in zip(casos, sols):
        if melhor is None:
            log("q_B = %.1f: sem solucao no dominio" % qB)
            continue
        par, r = melhor
        vB, auxB = fisicos(par)
        tB, hB = onda(par)
        dif = {k: (vB[k] - alvo[k]) / abs(alvo[k]) for k in TIPOS}
        tsB, sB = Dt.strain_observador(tB, hB, lista, par["M"], par["D"], par["iota"])
        cmp_ligo = Dt.comparar(tsA, sA, tsB, sB, "aLIGO", fmin=F_FIS)
        cmp_et = Dt.comparar(tsA, sA, tsB, sB, "ET", fmin=F_FIS)
        log("q_B = %.1f, chi2_B = %+.1f -> M_B = %.2f, chi1_B = %+.3f, D_B = %.1f Mpc, iota_B = %.1f graus | max dif. memorias = %.1e"
            % (qB, c2B, par["M"], par["c1"], par["D"], np.degrees(par["iota"]), max(abs(x) for x in dif.values())))
        log("     onda (h_+): match aLIGO = %.3f (SNR_A %.1f, rho_crit %.2f) ; match ET = %.3f (SNR_A %.0f, rho_crit %.2f) ; recuo B = %.0f km/s"
            % (cmp_ligo["+"]["match"], cmp_ligo["+"]["snr_A"], cmp_ligo["+"]["rho_crit"],
               cmp_et["+"]["match"], cmp_et["+"]["snr_A"], cmp_et["+"]["rho_crit"],
               np.linalg.norm(auxB["v_recuo"]) * 299792.458))
        pares.append(dict(qB=qB, c2B=c2B, M=par["M"], c1=par["c1"], D=par["D"], iota=par["iota"],
                          dif=dif, match_ligo=cmp_ligo["+"]["match"], match_et=cmp_et["+"]["match"],
                          rho_crit_ligo=cmp_ligo["+"]["rho_crit"], snrA_ligo=cmp_ligo["+"]["snr_A"]))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(AQUI, "..", "resultados", "exp07_binarias_observador.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(AQUI, "..", "resultados", "exp07_pares.json"), "w") as f:
        json.dump(dict(A=A, alvo=alvo, pares=pares), f, indent=1, default=float)

    figura(pares)
