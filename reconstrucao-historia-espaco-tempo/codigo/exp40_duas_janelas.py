"""Experimento 40, parte 2 (linha L16, tarefa 3): com e0 e l0 livres e DUAS janelas, uma excentrica imita A?

A circular (SEOBNRv5EHM, e0 = 0) e B com (M, q, chi1, chi2, D, iota, e0, l0): oito incognitas. Equacoes: as quatro
memorias no observador (m = 0) em duas janelas, desde 10 Hz e desde 20 Hz de frequencia orbital media (ver
exp40_comum.instante_freq_media), com as correcoes da L16 ((2,0) oscilatorio, E_lig EOB). D sai do deslocamento
da 1a janela; sobram 7 equacoes e 7 incognitas, resolvidas por least_squares com passos grandes (tremor ~1e-5).
Partidas: os pares do exp12 (l0 = 0 e pi) e pontos da familia aproximada circular de duas janelas do rev_R4
(NRHybSur3dq8_CCE) com e0 = 0,05.
Controle: o mesmo problema com e0 = 0 fixo (5 incognitas, 7 equacoes) mede o piso da familia circular neste
modelo.
Para as melhores solucoes: match da onda (h_+, comparar2) com A em aLIGO e ET.
Saida: resultados/exp40_duas_janelas.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp40_comum as C                                 # noqa: E402

NOMES = [("deslocamento", 0), ("spin", 0), ("cm", 0), ("giroscopica", 0),
         ("deslocamento", 1), ("spin", 1), ("cm", 1), ("giroscopica", 1)]
LIM_INF = [0.05, -0.8, 35.0, 1.0, -0.8, 0.02, -2 * np.pi]
LIM_SUP = [np.pi - 0.05, 0.8, 250.0, 8.0, 0.8, 0.4, 4 * np.pi]


def valores(q, c1, c2, M, e0, l0, iota, D):
    res, _ = C.avaliar(q, c1, c2, M, e0, l0)
    return [C.fisicos(r["com"][0], iota, M, D) for r in res], [r["com"][1] for r in res]


def residuos(p, alvo, e0_fixo=None):
    if e0_fixo is None:
        iota, c1, M, q, c2, e0, l0 = p
    else:
        iota, c1, M, q, c2 = p
        e0, l0 = e0_fixo, 0.0
    v1, _ = valores(q, c1, c2, M, e0, l0, iota, 1.0)
    D = v1[0]["deslocamento"] / alvo[0]["deslocamento"]
    v = [{k: x / D if k != "giroscopica" else x / D ** 2 for k, x in vj.items()} for vj in v1]
    r = np.array([(v[j][k] - alvo[j][k]) / abs(alvo[j][k]) for (k, j) in NOMES])
    return r[1:], D


def resolver(arg):
    alvo, x0, e0_fixo, rotulo = arg
    from scipy.optimize import least_squares
    t0 = time.time()
    if e0_fixo is None:
        lb, ub, xs = LIM_INF, LIM_SUP, [0.05, 0.05, 1.0, 0.05, 0.05, 0.02, 0.3]
    else:
        lb, ub, xs = LIM_INF[:5], LIM_SUP[:5], [0.05, 0.05, 1.0, 0.05, 0.05]
    x0 = np.clip(np.array(x0, float), np.array(lb) + 1e-9, np.array(ub) - 1e-9)

    def f(p):
        try:
            return residuos(p, alvo, e0_fixo)[0]
        except Exception:
            return np.full(7, 1.0)
    melhor = None
    x = x0
    # custo: cada iteracao gasta 1 + n avaliacoes (jacobiano por diferencas); nfev nao conta as do jacobiano
    for ds, nmax in ((1e-2, 22), (3e-3, 12)):
        r = least_squares(f, x, bounds=(lb, ub), diff_step=ds, x_scale=xs, xtol=1e-10, ftol=1e-10, gtol=1e-10,
                          max_nfev=nmax)
        x = r.x
        val = float(np.max(np.abs(r.fun)))
        if melhor is None or val < melhor[1]:
            melhor = (r.x.copy(), val, r.fun.copy(), int(r.nfev))
    xb, val, fun, nfev = melhor
    res, D = residuos(xb, alvo, e0_fixo)
    return dict(rotulo=rotulo, x0=list(map(float, x0)), x=list(map(float, xb)), D=float(D),
                max_res=float(np.max(np.abs(res))), res=list(map(float, res)), e0_fixo=e0_fixo,
                tempo_s=time.time() - t0)


def match(sol, alvoA):
    import observaveis as O
    from deteccao import strain_observador
    out = {}
    tA, hA, *_ = C.gerar(C.A["q"], C.A["c1"], C.A["c2"], C.A["M"], 0.0, 0.0)
    tsA, sA = strain_observador(tA, hA, C.LISTA, C.A["M"], C.A["D"], C.A["iota"])
    del tA, hA
    iota, c1, M, q, c2, e0, l0 = sol["x"] if sol["e0_fixo"] is None else (*sol["x"], sol["e0_fixo"], 0.0)
    tB, hB, *_ = C.gerar(q, c1, c2, M, e0, l0)
    tsB, sB = strain_observador(tB, hB, C.LISTA, M, sol["D"], iota)
    del tB, hB
    for det in ("aLIGO", "ET"):
        c = O.comparar2(tsA, sA, tsB, sB, det, 10.0)
        out[det] = dict(match=c["match"], snr_A=c["snr_A"], rho_crit=c["rho_crit"])
    return out


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    resA, _ = C.avaliar(C.A["q"], C.A["c1"], C.A["c2"], C.A["M"], 0.0, 0.0)
    alvo = [C.fisicos(r["com"][0], C.A["iota"], C.A["M"], C.A["D"]) for r in resA]
    pares = json.load(open(os.path.join(C.RES, "exp12_pares.json")))["pares"]
    partidas = []
    for p in pares:
        partidas.append(([p["iota"], p["c1"], p["M"], p["qB"], p["c2B"], p["e0"], 0.0],
                         "exp12 e0=%.1f qB=%.1f l0=0" % (p["e0"], p["qB"])))
    partidas = [x for x in partidas if "e0=0.3 qB=1.2" not in x[1]]      # sem solucao nem numa janela (exp40_pares)
    p = pares[3]
    partidas.append(([p["iota"], p["c1"], p["M"], p["qB"], p["c2B"], p["e0"], np.pi],
                     "exp12 e0=%.1f qB=%.1f l0=pi" % (p["e0"], p["qB"])))
    for (q_, c1_, c2_, M_, io_) in ((1.1, 0.3452, -0.2390, 64.856, 49.91), (1.3, 0.2982, -0.1949, 65.233, 50.15),
                                    (2.0, 0.4185, -0.2021, 68.173, 51.99)):
        partidas.append(([np.radians(io_), c1_, M_, q_, c2_, 0.05, 0.0],
                         "familia circular R4 q=%.1f, e0=0.05, l0=0" % q_))
    tarefas = [(alvo, x0, None, rot) for (x0, rot) in partidas]
    # controle circular (e0 = 0): partidas da familia R4
    for (q_, c1_, c2_, M_, io_) in ((1.3, 0.2982, -0.1949, 65.233, 50.15), (2.0, 0.4185, -0.2021, 68.173, 51.99)):
        tarefas.append((alvo, [np.radians(io_), c1_, M_, q_, c2_], 0.0, "controle circular q=%.1f" % q_))
    with mp.get_context("spawn").Pool(2) as pool:
        sols = pool.map(resolver, tarefas)
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)
    log("exp40_duas_janelas: A circular x B (e0, l0 livres), memorias m = 0 no observador em duas janelas (10 e 20 Hz)")
    log("A (com correcoes): janela 10 Hz " + ", ".join("%s %.5e" % kv for kv in alvo[0].items()))
    log("                   janela 20 Hz " + ", ".join("%s %.5e" % kv for kv in alvo[1].items()))
    for s in sols:
        x = s["x"]
        if s["e0_fixo"] is None:
            par = "iota %.2f graus chi1 %+.4f M %.3f q %.3f chi2 %+.4f e0 %.4f l0 %.3f rad D %.2f" % (
                np.degrees(x[0]), x[1], x[2], x[3], x[4], x[5], x[6] % (2 * np.pi), s["D"])
        else:
            par = "iota %.2f graus chi1 %+.4f M %.3f q %.3f chi2 %+.4f (e0 = 0) D %.2f" % (
                np.degrees(x[0]), x[1], x[2], x[3], x[4], s["D"])
        log()
        log("%s: max|res| = %.2e (%.0f s) -> %s" % (s["rotulo"], s["max_res"], s["tempo_s"], par))
        log("    residuos [spin1 cm1 giro1 | desl2 spin2 cm2 giro2]: " + " ".join("%+.1e" % r for r in s["res"]))
    boas = sorted([s for s in sols if s["e0_fixo"] is None], key=lambda s: s["max_res"])[:3]
    log()
    for s in boas:
        if s["max_res"] < 3e-3:
            m = match(s, alvo)
            s["match"] = m
            log("onda (h_+) da solucao '%s' (max|res| %.1e): match aLIGO %.4f (SNR_A %.1f, rho_crit %.2f) ; ET %.4f (rho_crit %.2f)"
                % (s["rotulo"], s["max_res"], m["aLIGO"]["match"], m["aLIGO"]["snr_A"], m["aLIGO"]["rho_crit"],
                   m["ET"]["match"], m["ET"]["rho_crit"]))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(C.RES, "exp40_duas_janelas.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(C.RES, "exp40_duas_janelas.json"), "w") as f:
        json.dump(dict(alvo=alvo, solucoes=sols), f, indent=1, default=float)
