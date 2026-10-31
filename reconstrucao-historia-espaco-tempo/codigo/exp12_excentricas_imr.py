"""Experimento 12: binarias excentricas com inspiral, fusao e ringdown (SEOBNRv5EHM).

Modelo: SEOBNRv5EHM (Gamboa et al. 2024, arXiv:2412.12823; pyseobnr 0.3.7), EOB excentrico de spins
alinhados calibrado a RN. Modos (2,2), (2,1), (3,3), (3,2), (4,4), (4,3); os m < 0 saem da simetria
equatorial h_{l,-m} = (-1)^l conj(h_lm). O modelo nao tem modos m = 0 (nem a memoria, nem a parte
oscilatoria do (2,0) de orbitas excentricas), entao so o nivel A existe aqui: memorias quadraticas
a partir dos modos oscilatorios. Nao ha RN com memoria para orbitas excentricas (nivel C impossivel).
Inicio: frequencia orbital media (EccIC = 1), M <omega> = pi M f com f = 10 Hz; e0 e anomalia
relativistica 0 (periastro) nessa frequencia.
Janela: as quatro memorias, inclusive o deslocamento, acumulam a partir de 10 Hz (o deslocamento de
janela e o que um detector com corte em baixa frequencia mede). Massa final para a parte ordinaria da
memoria de CM: M_f = 1 - E_janela - E_lig(x0), E_lig = (eta x0/2)(1 - (3/4 + eta/12) x0).

Partes:
 1. Conferencia de convencoes: SEOBNRv5EHM (e0 = 0) x NRHybSur3dq8_CCE, mesmos modos, nivel A, mesma janela.
 2. Memorias globais em funcao de e0 (M = 65, q = 1.2, chi = (0.3, -0.2)).
 3. Pares de observador: A circular (o mesmo do exp07) x B excentrico (e0 em 10 Hz). Fixos q_B, chi2_B e e0;
    D_B sai da equacao do deslocamento; (iota_B, chi1_B, M_B) resolvidos nas outras tres. Depois a onda.
 4. Refutacao: partidas aleatorias para um caso e o sinal da suavidade do modelo (ruido numerico).
Saida: resultados/exp12_excentricas_imr.txt, resultados/exp12_pares.json
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
from memorias import CalculadoraMemoria, gram           # noqa: E402
from harmonicos import Dfrak, ethb2_de_escalar          # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
MODOS = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)]
LISTA = []
for (l, m) in MODOS:
    LISTA += [(l, m), (l, -m)]
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
F_FIS = 10.0
A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0), e=0.0)
_calc = []
_cache = {}


def calc():
    if not _calc:
        _calc.append(CalculadoraMemoria(LISTA))
    return _calc[0]


def gerar(q, c1, c2, f0, e0):
    """t (em M), modos h_lm = r h / M de SEOBNRv5EHM, inicio na frequencia de onda media M f0."""
    from pyseobnr.generate_waveform import generate_modes_opt
    t, modos = generate_modes_opt(q, c1, c2, np.pi * f0, eccentricity=e0, rel_anomaly=0.0,
                                  approximant="SEOBNRv5EHM")
    h = {}
    for chave, v in modos.items():
        l, m = (int(x) for x in chave.split(","))
        h[(l, m)] = np.asarray(v)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    return np.asarray(t), h


def memorias_janela(t, h, lista, calculadora, eta, x0):
    """Memorias m = 0 acumuladas na janela (deslocamento incluso), nivel A, e auxiliares."""
    dt = t[1] - t[0]
    H = np.stack([h[k] for k in lista], axis=1)
    m = calculadora.memorias_gram(*gram(H, B.derivada4(H, dt), dt))
    out = B._mem_m0(m)
    Mf = 1.0 - m["energia_total"] - 0.5 * eta * x0 * (1 - (0.75 + eta / 12) * x0)
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dK = -1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    P = B.momento_irradiado(m["energia_modos"])
    return out, dict(M_f=Mf, E_janela=m["energia_total"], v_recuo=-P / Mf)


def mem_ehm(q, c1, c2, M, e0):
    k = (round(q, 9), round(c1, 9), round(c2, 9), round(M, 9), round(e0, 9))
    if k not in _cache:
        f0 = M * Dt.MSUN_S * F_FIS
        t, h = gerar(q, c1, c2, f0, e0)
        eta = q / (1 + q) ** 2
        _cache[k] = memorias_janela(t, h, LISTA, calc(), eta, (np.pi * f0) ** (2 / 3))
    return _cache[k]


def fisicos(par):
    mem, aux = mem_ehm(par["q"], par["c1"], par["c2"], par["M"], par["e"])
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"]), aux


def onda(par):
    return gerar(par["q"], par["c1"], par["c2"], par["M"] * Dt.MSUN_S * F_FIS, par["e"])


def resolver(alvo, qB, c2B, eB, x0):
    def montar(p):
        iota, c1, M = p
        par = dict(M=M, q=qB, c1=c1, c2=c2B, D=1.0, iota=iota, e=eB)
        v1, _ = fisicos(par)
        par["D"] = v1["deslocamento"] / alvo["deslocamento"]
        return par

    def res(p):
        v, _ = fisicos(montar(p))
        return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in ("spin", "cm", "giroscopica")])

    r = least_squares(res, x0, bounds=([0.05, -0.8, 35.0], [np.pi - 0.05, 0.8, 250.0]),
                      diff_step=1e-3, xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=150)
    return montar(r.x), float(np.max(np.abs(r.fun)))


def _caso(arg):
    alvo, qB, c2B, eB, partidas = arg
    melhor = None
    for x0 in partidas:
        try:
            par, r = resolver(alvo, qB, c2B, eB, x0)
        except Exception:                               # fora do dominio do modelo
            continue
        if melhor is None or r < melhor[1]:
            melhor = (par, r)
        if melhor[1] < 1e-9:
            break
    return melhor


PARTIDAS = [(A["iota"], A["c1"], 65.0), (np.radians(35), 0.5, 75.0), (np.radians(70), -0.3, 55.0)]


if __name__ == "__main__":
    import multiprocessing as mp
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)

    t0 = time.time()
    # ---------- parte 1 ----------
    log("Parte 1: SEOBNRv5EHM (e0 = 0) x NRHybSur3dq8_CCE, mesmos modos, nivel A, janela M f0 = 0.004 (deslocamento de janela)")
    calcS = CalculadoraMemoria(LISTA)
    for (q, c1, c2) in [(1.2, 0.3, -0.2), (1.0, 0.0, 0.0), (3.0, 0.6, 0.0)]:
        eta = q / (1 + q) ** 2
        x0 = (np.pi * 0.004) ** (2 / 3)
        tE, hE = gerar(q, c1, c2, 0.004, 0.0)
        vE = B.vetor(memorias_janela(tE, hE, LISTA, calcS, eta, x0)[0])[0]
        tS, hS = B.gerar(q, c1, c2, f0=0.004, dt=0.25)
        vS = B.vetor(memorias_janela(tS, hS, LISTA, calcS, eta, x0)[0])[0]
        log("  q=%.1f chi=(%+.1f,%+.1f): " % (q, c1, c2)
            + " ".join("%s %+.3f" % (n, (a - b) / abs(b)) for n, a, b in zip(NOMES, vE, vS)))

    # ---------- parte 2 ----------
    log()
    log("Parte 2: memorias globais (referencial da fonte) relativas ao caso circular; M = 65, q = 1.2, chi = (+0.3, -0.2), janela desde 10 Hz")
    v0 = B.vetor(mem_ehm(1.2, 0.3, -0.2, 65.0, 0.0)[0])[0]
    log("  e0 = 0.00: " + " ".join("%s %+.4e" % (n, x) for n, x in zip(NOMES, v0)) + "  (valores absolutos)")
    for e0 in (0.05, 0.1, 0.2, 0.3):
        ve = B.vetor(mem_ehm(1.2, 0.3, -0.2, 65.0, e0)[0])[0]
        log("  e0 = %.2f: " % e0 + " ".join("%s %+.4f" % (n, (a - b) / abs(b)) for n, a, b in zip(NOMES, ve, v0)))
    # suavidade: variacao relativa sob passos minusculos em M (ruido numerico do modelo)
    vs = [B.vetor(mem_ehm(1.2, 0.3, -0.2, 65.0 * (1 + k * 1e-6), 0.2)[0])[0] for k in range(4)]
    d1 = np.max(np.abs(np.diff(vs, axis=0)) / np.abs(vs[0]), axis=1)
    log("  ruido numerico (e0 = 0.2): maior variacao relativa sob passos de 1e-6 em M: %s" % np.array2string(d1, precision=2))

    # ---------- parte 3 ----------
    log()
    alvo, auxA = fisicos(A)
    log("Parte 3: A circular (M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus), SEOBNRv5EHM e0 = 0:")
    log("  " + ", ".join("%s %.5e" % kv for kv in alvo.items()) + " ; recuo %.0f km/s" % (np.linalg.norm(auxA["v_recuo"]) * 299792.458))
    casos = [(1.2, -0.2, 0.1), (1.2, -0.2, 0.2), (1.2, -0.2, 0.3), (2.0, 0.0, 0.2), (2.0, 0.0, 0.3), (1.0, 0.0, 0.2)]
    with mp.get_context("spawn").Pool(4) as pool:
        sols = pool.map(_caso, [(alvo, qB, c2B, eB, PARTIDAS) for (qB, c2B, eB) in casos])
    tA, hA = onda(A)
    tsA, sA = Dt.strain_observador(tA, hA, LISTA, A["M"], A["D"], A["iota"])
    pares = []
    for (qB, c2B, eB), melhor in zip(casos, sols):
        if melhor is None:
            log("  B e0 = %.1f, q_B = %.1f: sem solucao no dominio" % (eB, qB))
            continue
        par, r = melhor
        vB, auxB = fisicos(par)
        dif = {k: (vB[k] - alvo[k]) / abs(alvo[k]) for k in B.TIPOS}
        tB, hB = onda(par)
        tsB, sB = Dt.strain_observador(tB, hB, LISTA, par["M"], par["D"], par["iota"])
        cl = Dt.comparar(tsA, sA, tsB, sB, "aLIGO", fmin=F_FIS)["+"]
        ce = Dt.comparar(tsA, sA, tsB, sB, "ET", fmin=F_FIS)["+"]
        log("  B e0 = %.1f, q_B = %.1f, chi2_B = %+.1f -> M_B = %.2f, chi1_B = %+.3f, D_B = %.1f Mpc, iota_B = %.1f graus | max dif. memorias = %.1e"
            % (eB, qB, c2B, par["M"], par["c1"], par["D"], np.degrees(par["iota"]), max(abs(x) for x in dif.values())))
        log("       onda (h_+): match aLIGO = %.3f (SNR_A %.1f, rho_crit %.2f) ; match ET = %.3f (SNR_A %.0f, rho_crit %.2f) ; recuo B = %.0f km/s"
            % (cl["match"], cl["snr_A"], cl["rho_crit"], ce["match"], ce["snr_A"], ce["rho_crit"],
               np.linalg.norm(auxB["v_recuo"]) * 299792.458))
        pares.append(dict(e0=eB, qB=qB, c2B=c2B, M=par["M"], c1=par["c1"], D=par["D"], iota=par["iota"], residuo=r,
                          match_ligo=cl["match"], match_et=ce["match"], rho_crit_ligo=cl["rho_crit"]))

    # ---------- parte 4 ----------
    log()
    rng = np.random.default_rng(5)
    aleat = [(rng.uniform(0.3, np.pi - 0.3), rng.uniform(-0.7, 0.7), rng.uniform(45, 110)) for _ in range(8)]
    with mp.get_context("spawn").Pool(4) as pool:
        outs = pool.map(_caso, [(alvo, 1.2, -0.2, 0.3, [x0]) for x0 in aleat])
    log("Parte 4 (refutacao): e0 = 0.3, q_B = 1.2, 8 partidas aleatorias -> residuos: "
        + ", ".join("%.1e" % o[1] if o else "falhou" for o in outs))
    sol = [(o[0]["M"], o[0]["c1"], np.degrees(o[0]["iota"]), o[0]["D"]) for o in outs if o and o[1] < 1e-6]
    if sol:
        log("  solucoes com residuo < 1e-6 (M, chi1, iota, D): " + "; ".join("(%.2f, %+.3f, %.1f, %.1f)" % s for s in sol))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(AQUI, "..", "resultados", "exp12_excentricas_imr.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(AQUI, "..", "resultados", "exp12_pares.json"), "w") as f:
        json.dump(dict(A=A, alvo=alvo, pares=pares), f, indent=1, default=float)
