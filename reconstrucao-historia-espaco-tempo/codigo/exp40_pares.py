"""Experimento 40, parte 1 (linha L16, tarefas 1 e 2): os pares circular x excentrica do exp12 com as correcoes.

Correcoes (exp40_comum): modo (2,0) oscilatorio newtoniano das orbitas excentricas nos fluxos; energia de
ligacao excentrica (Hamiltoniana EOB) em M_f; derivada de 8a ordem. Para cada par do exp12 (l0 = 0):
  a) diferencas B - A (janela de 10 Hz) com: cadeia do exp12 (sem (2,0), E_lig 1PN), so o (2,0), so a E_lig EOB,
     as duas correcoes;
  b) resolve de novo (iota_B, chi1_B, M_B; D_B pelo deslocamento) com as correcoes, otimizador robusto ao
     tremor do SEOBNRv5EHM (~1e-5): least_squares com passos grandes (diff_step 3e-3 e 1e-2), partindo da
     solucao do exp12 e de duas partidas perturbadas; guarda o melhor reavaliado;
  c) conferencia do (2,0) newtoniano: |h20|/|h22| nas duas primeiras orbitas contra o modelo PN (pn_excentrico).
Saida: resultados/exp40_pares.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp40_comum as C                                 # noqa: E402

PARES = json.load(open(os.path.join(C.RES, "exp12_pares.json")))["pares"]


def alvo_A():
    res, _ = C.avaliar(C.A["q"], C.A["c1"], C.A["c2"], C.A["M"], 0.0, 0.0, freqs=(10.0,), variantes=True)
    out = {}
    for chave in ("com", "exp12", "so20"):
        out[chave] = C.fisicos(res[0][chave][0], C.A["iota"], C.A["M"], C.A["D"])
    # so E_lig EOB sem (2,0): 'sem' da avaliacao com tambem_sem20
    res2, _ = C.avaliar(C.A["q"], C.A["c1"], C.A["c2"], C.A["M"], 0.0, 0.0, freqs=(10.0,), tambem_sem20=True)
    out["soelig"] = C.fisicos(res2[0]["sem"][0], C.A["iota"], C.A["M"], C.A["D"])
    return out


def resolver(alvo, qB, c2B, eB, x0, diff_step):
    from scipy.optimize import least_squares

    def montar(p):
        iota, c1, M = p
        res, _ = C.avaliar(qB, c1, c2B, M, eB, 0.0, freqs=(10.0,))
        v1 = C.fisicos(res[0]["com"][0], iota, M, 1.0)
        D = v1["deslocamento"] / alvo["deslocamento"]
        return dict(M=M, q=qB, c1=c1, c2=c2B, D=D, iota=iota, e=eB), res[0]["com"]

    def f(p):
        par, (mem, _) = montar(p)
        v = C.fisicos(mem, par["iota"], par["M"], par["D"])
        return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in ("spin", "cm", "giroscopica")])

    r = least_squares(f, x0, bounds=([0.05, -0.8, 35.0], [np.pi - 0.05, 0.8, 250.0]), diff_step=diff_step,
                      x_scale=[0.05, 0.05, 1.0], xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=60)
    par, (mem, aux) = montar(r.x)
    v = C.fisicos(mem, par["iota"], par["M"], par["D"])
    d = C.dif_rel(v, alvo)
    return par, max(abs(x) for x in d.values()), d, int(r.nfev)


def caso(arg):
    alvo_todos, p = arg
    t0 = time.time()
    out = dict(e0=p["e0"], qB=p["qB"], c2B=p["c2B"], exp12=dict(M=p["M"], c1=p["c1"], D=p["D"], iota=p["iota"],
                                                               residuo=p["residuo"]))
    res, ex = C.avaliar(p["qB"], p["c1"], p["c2B"], p["M"], p["e0"], 0.0, freqs=(10.0,), variantes=True)
    res2, _ = C.avaliar(p["qB"], p["c1"], p["c2B"], p["M"], p["e0"], 0.0, freqs=(10.0,), tambem_sem20=True)
    variantes = dict(com=res[0]["com"], exp12=res[0]["exp12"], so20=res[0]["so20"], soelig=res2[0]["sem"])
    out["antes"] = {}
    for nome, (mem, aux) in variantes.items():
        v = C.fisicos(mem, p["iota"], p["M"], p["D"])
        d = C.dif_rel(v, alvo_todos[nome])
        out["antes"][nome] = dict(d, max=max(abs(x) for x in d.values()), M_f=aux["M_f"], E_lig=aux["E_lig"])
    out["max_h20_osc"] = ex["max_h20_osc"]
    alvo = alvo_todos["com"]
    melhor = None
    partidas = [(p["iota"], p["c1"], p["M"]), (p["iota"] + 0.02, p["c1"] + 0.02, p["M"] * 1.003),
                (p["iota"] - 0.02, p["c1"] - 0.02, p["M"] * 0.997)]
    tent = []
    for x0 in partidas:
        for ds in (3e-3, 1e-2):
            try:
                par, r, d, nfev = resolver(alvo, p["qB"], p["c2B"], p["e0"], np.array(x0), ds)
            except Exception as exc:                        # fora do dominio do modelo
                tent.append(("falhou", str(exc)[:60]))
                continue
            tent.append((r, nfev, ds))
            if melhor is None or r < melhor[1]:
                melhor = (par, r, d)
        if melhor is not None and melhor[1] < 1.5e-5:
            break
    out["tentativas"] = tent
    if melhor:
        par, r, d = melhor
        out["depois"] = dict(par=par, residuo=r, dif=d)
    out["tempo_s"] = time.time() - t0
    return out


def conferir_h20():
    """|h20_osc|/|h22| nas duas primeiras orbitas: EOB (formula newtoniana na dinamica) x modelo PN newtoniano."""
    import pn_excentrico as PN
    from deteccao import MSUN_S
    linhas = []
    for (q, c1, c2, M, e0) in ((2.0, 0.06, 0.0, 72.6, 0.2), (1.2, 0.3, -0.2, 65.0, 0.1), (1.2, 0.3, -0.2, 65.0, 0.3)):
        t, h, dyn, nu, ts_ = C.gerar(q, c1, c2, M, e0, 0.0)
        h20 = C.h20_newton(t, dyn, nu, ts_)
        f0 = M * MSUN_S * 10.0
        T = 2 * 2 * np.pi / (np.pi * f0)                     # duas orbitas medias
        s = t < t[0] + T
        r_eob = np.max(np.abs(h20[s][50:])) / np.max(np.abs(h[(2, 2)][s][50:]))
        del t, h, dyn, h20
        eta = q / (1 + q) ** 2
        tp, hp, *_ = PN.modos(eta, e0, f0, dt=0.5)
        sp = tp < tp[0] + T
        r_pn = np.max(np.abs(hp[(2, 0)][sp][20:])) / np.max(np.abs(hp[(2, 2)][sp][20:]))
        del tp, hp
        linhas.append("  q = %.1f, e0 = %.1f: max|h20_osc|/max|h22| (2 orbitas) EOB-newtoniano %.4f ; PN newtoniano %.4f ; razao %.3f"
                      % (q, e0, r_eob, r_pn, r_eob / r_pn))
    return linhas


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)
    alvo = alvo_A()
    log("exp40_pares: pares do exp12 (A circular x B excentrica, janela desde 10 Hz) com as correcoes da L16")
    log("A (SEOBNRv5EHM, e0 = 0), valores com as correcoes: " + ", ".join("%s %.6e" % kv for kv in alvo["com"].items()))
    log("  cadeia do exp12 (derivada de 8a ordem) contra exp12_pares.json:")
    a12 = json.load(open(os.path.join(C.RES, "exp12_pares.json")))["alvo"]
    log("   " + " ".join("%s %+.2e" % (k, (alvo["exp12"][k] - a12[k]) / abs(a12[k])) for k in C.TIPOS))
    with mp.get_context("spawn").Pool(2) as pool:
        outs = pool.map(caso, [(alvo, p) for p in PARES])
    js = []
    for o in outs:
        js.append(o)
        log()
        log("B e0 = %.1f, q_B = %.1f, chi2_B = %+.1f (exp12: M %.3f chi1 %+.4f D %.2f iota %.2f graus, residuo %.1e) ; max|h20_osc| = %.2e"
            % (o["e0"], o["qB"], o["c2B"], o["exp12"]["M"], o["exp12"]["c1"], o["exp12"]["D"],
               np.degrees(o["exp12"]["iota"]), o["exp12"]["residuo"], o["max_h20_osc"]))
        for nome, rot in (("exp12", "cadeia do exp12        "), ("so20", "so (2,0) oscilatorio    "),
                          ("soelig", "so E_lig EOB excentrica "), ("com", "as duas correcoes       ")):
            d = o["antes"][nome]
            log("   %s: max %.2e [desl %+.2e spin %+.2e cm %+.2e giro %+.2e] ; E_lig B %.6e"
                % (rot, d["max"], d["deslocamento"], d["spin"], d["cm"], d["giroscopica"], d["E_lig"]))
        if "depois" in o:
            dp = o["depois"]
            par = dp["par"]
            log("   resolvido de novo com as correcoes: max %.2e [%s] -> M %.4f (%+.1e) chi1 %+.4f (%+.1e) D %.2f iota %.3f graus"
                % (dp["residuo"], " ".join("%s %+.1e" % (k[:4], v) for k, v in dp["dif"].items()), par["M"],
                   par["M"] / o["exp12"]["M"] - 1, par["c1"], par["c1"] - o["exp12"]["c1"], par["D"],
                   np.degrees(par["iota"])))
        log("   tentativas (residuo, avaliacoes, diff_step): " + "; ".join(str(x) for x in o["tentativas"]))
    log()
    log("Conferencia do (2,0) newtoniano:")
    for s in conferir_h20():
        log(s)
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(C.RES, "exp40_pares.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(C.RES, "exp40_pares.json"), "w") as f:
        json.dump(dict(alvo=alvo, pares=js), f, indent=1, default=float)
