"""Experimento 10: binarias excentricas — historias de formacao diferentes, mesmas memorias?

Uma binaria formada por captura dinamica chega a banda com excentricidade; uma que evoluiu isolada
chega circular. Um observador consegue separa-las so pelas quatro memorias?

O modelo excentrico de RN/EOB (TEOBResumS-Dali) nao pode ser compilado neste ambiente, e o pacote
TEOBResumS do PyPI (4.4.1) e quase circular: ele ignora o parametro de excentricidade. Por isso:
  Parte 1: conferencia entre modelos no caso circular (TEOB 4.4.1 x NRHybSur3dq8_CCE, nivel A).
  Parte 2: modelo proprio pn_excentrico.py (quadrupolo newtoniano + evolucao de Peters), so a
           inspiral (de 10 Hz ate a separatriz p = 6 + 2e). Memorias de janela (sem parte anterior).
  Parte 3: par de observador: A circular (M = 65, q = 1.2, D = 400 Mpc, iota = 50 graus) e B excentrico
           (e0 em 10 Hz), resolvendo (M_B, eta_B, iota_B) e D_B para igualar as quatro memorias;
           compara as formas de onda (aLIGO, inspiral).
Saida: resultados/exp10_excentricas.txt
"""
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import pn_excentrico as PE                              # noqa: E402
from memorias import CalculadoraMemoria, gram           # noqa: E402
from harmonicos import Dfrak, ethb2_de_escalar          # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


MODOS_TEOB = [(2, 1), (2, 2), (3, 1), (3, 2), (3, 3), (4, 1), (4, 2), (4, 3), (4, 4), (5, 5)]
LISTA_T = []
for (l, m) in MODOS_TEOB:
    LISTA_T += [(l, m), (l, -m)]
LISTA_PN = [(2, 2), (2, -2), (2, 1), (2, -1), (2, 0)]
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]


def k_teob(l, m):
    return int(l * (l - 1) / 2 + m - 2)


def teob_circular(q, c1, c2, f0):
    import EOBRun_module as E
    ks = [k_teob(l, m) for (l, m) in MODOS_TEOB]
    pars = {"M": 1.0, "q": q, "chi1": c1, "chi2": c2, "LambdaAl2": 0., "LambdaBl2": 0., "domain": 0,
            "arg_out": "yes", "use_mode_lm": ks, "output_lm": ks, "srate_interp": 4.0,
            "use_geometric_units": "yes", "initial_frequency": f0, "interp_uniform_grid": "yes",
            "distance": 1., "inclination": 0.}
    t, hp, hc, hlm, dyn = E.EOBRunPy(pars)
    nu = q / (1 + q) ** 2
    h = {}
    for (l, m) in MODOS_TEOB:
        A, ph = hlm[str(k_teob(l, m))]
        h[(l, m)] = nu * A * np.exp(-1j * ph)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    return np.asarray(t), h


def memorias_de_modos(t, h, lista, calc, eta, x0=None, com_pre=True):
    dt = t[1] - t[0]
    H = np.stack([h[k] for k in lista], axis=1)
    m = calc.memorias_gram(*gram(H, B.derivada4(H, dt), dt))
    out = B._mem_m0(m)
    E = m["energia_total"]
    if com_pre:
        out["deslocamento"][(2, 0)] += B.favata_h20(x0, eta)
        out["deslocamento"][(4, 0)] += B.lrr_h40(x0, eta)
        E += 0.5 * eta * x0
    Mf = 1 - E
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dK = -1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    return out


if __name__ == "__main__":
    # ---------- parte 1 ----------
    calcT = CalculadoraMemoria(LISTA_T)
    log("Parte 1: TEOBResumS 4.4.1 (circular) x NRHybSur3dq8_CCE, ambos no nivel A, janela M f0 = 0.004")
    for (q, c1, c2) in [(1.2, 0.3, -0.2), (1.0, 0.0, 0.0), (3.0, 0.6, 0.0)]:
        t, h = teob_circular(q, c1, c2, 0.004)
        eta = q / (1 + q) ** 2
        vT = B.vetor(memorias_de_modos(t, h, LISTA_T, calcT, eta, (np.pi * 0.004) ** (2 / 3)))[0]
        vS = B.vetor(B.memorias(q, c1, c2, f0=0.004, nivel="A")[0])[0]
        log("  q=%.1f chi=(%+.1f,%+.1f): " % (q, c1, c2) + " ".join("%s %+.3f" % (n, (a - b) / abs(b)) for n, a, b in zip(NOMES, vT, vS)))

    # ---------- parte 2 ----------
    calcP = CalculadoraMemoria(LISTA_PN)
    F_FIS = 10.0

    def mem_pn(M, eta, e0):
        f0 = M * Dt.MSUN_S * F_FIS
        t, h, r, a, e = PE.modos(eta, e0, f0)
        return memorias_de_modos(t, h, LISTA_PN, calcP, eta, com_pre=False), t, h

    log("Parte 2 (PN newtoniano, inspiral de 10 Hz a separatriz; M = 65, q = 1.2): memorias relativas ao caso circular")
    eta0 = 1.2 / 2.2 ** 2
    v0 = B.vetor(mem_pn(65.0, eta0, 0.0)[0])[0]
    calc22 = CalculadoraMemoria(LISTA_PN[:2])
    for e0 in (0.05, 0.1, 0.2, 0.3, 0.4):
        me, t, h = mem_pn(65.0, eta0, e0)
        ve = B.vetor(me)[0]
        # o que o SEOBNRv5EHM perde: ele nao tem a parte oscilatoria do modo (2,0) de orbitas excentricas
        v22 = B.vetor(memorias_de_modos(t, h, LISTA_PN[:2], calc22, eta0, com_pre=False))[0]
        log("  e0 = %.2f: " % e0 + " ".join("%s %+.3f" % (n, (a - b) / abs(b)) for n, a, b in zip(NOMES, ve, v0) if n != "desl40" and n != "cm40")
            + " | sem o modo (2,0): " + " ".join("%s %+.1e" % (n, (a - b) / abs(b)) for n, a, b in zip(NOMES, v22, ve) if n in ("desl20", "spin30", "giro30")))

    # ---------- parte 3 ----------
    A = dict(M=65.0, eta=eta0, e=0.0, D=400.0, iota=np.radians(50.0))
    _c = {}

    def fis(par):
        k = (round(par["M"], 9), round(par["eta"], 12), par["e"])
        if k not in _c:
            _c[k] = mem_pn(par["M"], par["eta"], par["e"])
        mem, t, h = _c[k]
        return B.valores_fisicos(mem, par["iota"], par["M"], par["D"]), t, h

    alvo, tA, hA = fis(A)
    log("Parte 3: A circular (M = 65, q = 1.2, D = 400 Mpc, iota = 50 graus): " + ", ".join("%s %.4e" % kv for kv in alvo.items()))
    for eB in (0.1, 0.2, 0.3):
        def montar(p):
            iota, eta, M = p
            par = dict(M=M, eta=eta, e=eB, D=1.0, iota=iota)
            v, _, _ = fis(par)
            par["D"] = v["deslocamento"] / alvo["deslocamento"]
            return par

        def res(p):
            v, _, _ = fis(montar(p))
            return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in ("spin", "cm", "giroscopica")])

        melhor = None
        for x0 in ((A["iota"], eta0, 65.0), (np.radians(40), 0.2, 70.0), (np.radians(65), 0.24, 55.0)):
            r = least_squares(res, x0, bounds=([0.05, 0.05, 30.0], [np.pi - 0.05, 0.25, 200.0]),
                              diff_step=1e-5, xtol=1e-14, ftol=1e-14, gtol=1e-14)
            if melhor is None or np.max(np.abs(r.fun)) < melhor[1]:
                melhor = (r.x, np.max(np.abs(r.fun)))
        par = montar(melhor[0])
        vB, tB, hB = fis(par)
        qB = (1 - 2 * par["eta"] + np.sqrt(max(1 - 4 * par["eta"], 0))) / (2 * par["eta"])
        tsA, sA = Dt.strain_observador(tA, hA, LISTA_PN, A["M"], A["D"], A["iota"])
        tsB, sB = Dt.strain_observador(tB, hB, LISTA_PN, par["M"], par["D"], par["iota"])
        # alinhar pelo fim (a inspiral termina na separatriz)
        cl = Dt.comparar(tsA - tsA[-1] + tsA[np.argmax(np.abs(sA))], sA, tsB - tsB[-1] + tsB[np.argmax(np.abs(sB))], sB, "aLIGO", fmin=F_FIS)["+"]
        log("  B e0 = %.1f: M_B = %.2f, q_B = %.2f, D_B = %.1f Mpc, iota_B = %.1f graus | max dif. memorias = %.1e | onda: match aLIGO %.3f (SNR_A %.0f, rho_crit %.2f)"
            % (eB, par["M"], qB, par["D"], np.degrees(par["iota"]), melhor[1], cl["match"], cl["snr_A"], cl["rho_crit"]))
    with open(os.path.join(AQUI, "..", "resultados", "exp10_excentricas.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
