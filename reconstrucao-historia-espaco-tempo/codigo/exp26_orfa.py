"""Experimento 26 (L05, item 7 da revisao): memoria orfa. Regiao de binarias B cuja memoria nula, vista por UM
detector, e indistinguivel da de A com amplitude, instante, polarizacao e inclinacao livres.

Para cada ponto intrinseco (q, chi1, chi2) de uma sequencia de Sobol (mais pontos especiais: A, os pares do exp07),
minimiza 1 - match sobre ln M (varredura + Brent) e cos iota (Nelder-Mead), com o tempo e o par (F+, Fx) livres:
o conjunto dos sinais de B num detector, com ceu, D e psi livres, e o plano gerado por h+_B e hx_B, e o match
maximo e sqrt(c^T G^-1 c)/rho_A, c = ((s_A|h+_B(.-tau)), (s_A|hx_B(.-tau))), G = Gram(h+_B, hx_B), maximizado em
tau (FFT + refino continuo). Sem maximizar fase (sinal nao oscilatorio). Espectros de B por interpolacao em F da
forma adimensional (exp24_comum; inicio da janela em M f0 fixo, verificado no exp24 T3: 1-match < 1e-9).
Criterio: 1 - match < 1/(2 rho_A^2) (CE, ET), rho_A do sinal so de memoria (exp24).
Sistemas: A (M = 65, D = 400 Mpc) e massa baixa (M = 6, D com rho_CE = 34 e D = 400 Mpc).
Uso: python exp26_orfa.py [A|baixa]  -> resultados/exp26_orfa_<sist>.json e .txt
"""
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CFG = {
    "A": dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, iota=np.radians(50.0), f0=65.0 * 4.925490947641267e-06 * 10.0,
              N=2 ** 19, T_tap=1500.0, fmax_banda=1000.0, Fmax_B=0.8, lnM_faixa=(np.log(0.55), np.log(1.9)),
              qmax=6.0, n_sobol=160),
    "baixa": dict(M=6.0, q=1.2, c1=0.3, c2=-0.2, iota=np.radians(50.0), f0=0.0016,
                  N=2 ** 20, T_tap=10000.0, fmax_banda=8000.0, Fmax_B=0.6, lnM_faixa=(np.log(0.5), np.log(2.0)),
                  qmax=6.0, n_sobol=64),
}
PSDS = ("ET", "CE")


def _init(sist):
    global C, G
    import exp24_comum as C_
    from deteccao import MSUN_S
    C = C_
    cfg = CFG[sist]
    E = C.EspectroMemoria(cfg["q"], cfg["c1"], cfg["c2"], cfg["M"], cfg["f0"] / (cfg["M"] * MSUN_S), N=cfg["N"],
                          T_tap=cfg["T_tap"])
    hp, hx, _, _ = E.canais(cfg["iota"])
    f, sA = C.fisico(E.F, hp, cfg["M"], 400.0)
    sel = f <= cfg["fmax_banda"]
    f, sA = f[sel], sA[sel]
    df = f[1] - f[0]
    W = {p: C.psd_grade(p, len(f), df) for p in PSDS}
    G = dict(cfg=cfg, f=f, df=df, sA=sA, W=W, rhoA={p: np.sqrt(C.produto(sA, sA, W[p], df)) for p in PSDS},
             MSUN_S=MSUN_S)
    del E


def _match_plano(sA, bp, bx, w, df, f, up=2):
    """max_tau sqrt(c^T G^-1 c)/|s_A| para o plano (bp, bx); devolve (match, tau)."""
    from scipy.optimize import minimize_scalar
    aa = C.produto(sA, sA, w, df)
    Gm = np.array([[C.produto(bp, bp, w, df), C.produto(bp, bx, w, df)],
                   [C.produto(bx, bp, w, df), C.produto(bx, bx, w, df)]])
    Gi = np.linalg.inv(Gm)
    Op, tau = C.overlap_tempo(sA, bp, w, df, up=up)
    Ox, _ = C.overlap_tempo(sA, bx, w, df, up=up)
    st = Gi[0, 0] * Op ** 2 + 2 * Gi[0, 1] * Op * Ox + Gi[1, 1] * Ox ** 2
    j = int(np.argmax(st))
    sel = w > 0
    fs_ = f[sel]
    cp = (sA * np.conj(bp) * w * 4 * df)[sel]
    cx = (sA * np.conj(bx) * w * 4 * df)[sel]

    def menos(t_):
        e = np.exp(2j * np.pi * fs_ * t_)
        a, b = np.real(np.sum(cp * e)), np.real(np.sum(cx * e))
        return -(Gi[0, 0] * a * a + 2 * Gi[0, 1] * a * b + Gi[1, 1] * b * b)

    h = abs(tau[1] - tau[0])
    r = minimize_scalar(menos, bounds=(tau[j] - 2 * h, tau[j] + 2 * h), method="bounded", options=dict(xatol=1e-9))
    best = max(st[j], -r.fun)
    return float(np.sqrt(max(best, 0) / aa)), float(r.x)


def _ponto(args):
    """Minimiza 1 - match sobre (ln M, cos iota) para um ponto intrinseco; devolve numeros."""
    from scipy.interpolate import CubicSpline
    from scipy.optimize import minimize, minimize_scalar
    q, c1, c2, rotulo = args
    cfg, f, df = G["cfg"], G["f"], G["df"]
    t1 = time.time()
    try:
        E = C.EspectroMemoria(q, c1, c2, cfg["M"], cfg["f0"] / (cfg["M"] * G["MSUN_S"]), N=cfg["N"],
                              T_tap=cfg["T_tap"], Fmax=cfg["Fmax_B"])
    except Exception as ex:                       # fora do dominio do substituto
        return dict(q=q, c1=c1, c2=c2, rotulo=rotulo, erro=str(ex))
    splP = CubicSpline(E.F, E.Sp_)
    splX = CubicSpline(E.F, E.Sx_)
    del E

    def sinais(lnM, cosi):
        Ms = np.exp(lnM) * G["MSUN_S"]
        F = Ms * f
        Y = C._Ylist(float(np.arccos(np.clip(cosi, -1, 1))))
        k = Ms * Ms
        return k * (splP(F) @ Y), k * (splX(F) @ Y)

    out = dict(q=q, c1=c1, c2=c2, rotulo=rotulo)
    cos0 = np.cos(cfg["iota"])
    lnMA = np.log(cfg["M"])
    grade = lnMA + np.linspace(cfg["lnM_faixa"][0], cfg["lnM_faixa"][1], 17)
    vals = {p: [] for p in PSDS}
    for lm in grade:
        bp, bx = sinais(lm, cos0)
        for p in PSDS:
            vals[p].append(1 - _match_plano(G["sA"], bp, bx, G["W"][p], df, f)[0])
    out["grade_lnM"] = grade.tolist()
    for p in PSDS:
        v = np.array(vals[p])
        out["perfil_" + p] = v.tolist()
        j = int(np.argmin(v))
        lo, hi = grade[max(j - 1, 0)], grade[min(j + 1, len(grade) - 1)]

        def fM(lm):
            bp, bx = sinais(lm, cos0)
            return 1 - _match_plano(G["sA"], bp, bx, G["W"][p], df, f)[0]

        r = minimize_scalar(fM, bounds=(lo, hi), method="bounded", options=dict(xatol=3e-5))
        lim = 1.0 / (2 * (34.09 if p == "CE" else 8.64) ** 2) * G.get("fator_lim", 1.0)
        if r.fun > 5 * lim:                       # longe da regiao: nao refina em cos iota
            out[p] = dict(mm_M=float(r.fun), lnM_M=float(r.x), mm=float(r.fun), lnM=float(r.x), cosi=float(cos0),
                          mm_MA=float(fM(lnMA)))
            continue

        def f2(x):
            if abs(x[1]) > 1:
                return 1.0
            bp, bx = sinais(x[0], x[1])
            return 1 - _match_plano(G["sA"], bp, bx, G["W"][p], df, f)[0]

        r2 = minimize(f2, [r.x, cos0], method="Nelder-Mead",
                      options=dict(xatol=1e-5, fatol=1e-9, initial_simplex=[[r.x, cos0], [r.x + 0.01, cos0],
                                                                            [r.x, cos0 + 0.1]], maxiter=80))
        melhor = (r2.fun, r2.x[0], r2.x[1]) if r2.fun < r.fun else (r.fun, r.x, cos0)
        out[p] = dict(mm_M=float(r.fun), lnM_M=float(r.x), mm=float(melhor[0]), lnM=float(melhor[1]),
                      cosi=float(melhor[2]), mm_MA=float(fM(lnMA)))
    out["tempo"] = time.time() - t1
    return out


def main():
    sist = sys.argv[1] if len(sys.argv) > 1 else "A"
    cfg = CFG[sist]
    from scipy.stats import qmc
    pts = []
    pts.append((cfg["q"], cfg["c1"], cfg["c2"], "A"))
    if sist == "A":
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "exp07_pares.json")) as fh:
            J = json.load(fh)
        for pr in J["pares"]:
            pts.append((pr["qB"], float(np.clip(pr["c1"], -0.8, 0.8)), pr["c2B"], "exp07 qB=%g c2B=%g" % (pr["qB"], pr["c2B"])))
    for qq in (1.0, 3.0, 6.0):
        for cc in (-0.8, 0.8):
            pts.append((qq, cc, cc, "canto"))
    sob = qmc.Sobol(d=3, scramble=True, seed=2026).random(cfg["n_sobol"])
    for u in sob:
        pts.append((1.0 + u[0] * (cfg["qmax"] - 1.0), -0.8 + 1.6 * u[1], -0.8 + 1.6 * u[2], "sobol"))
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(2, initializer=_init, initargs=(sist,)) as pool:
        res = []
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "exp26_orfa_%s" % sist)
        parcial = open(base + "_parcial.jsonl", "w")
        for i, r in enumerate(pool.imap(_ponto, pts, chunksize=1)):
            res.append(r)
            parcial.write(json.dumps(r, default=float) + "\n")
            parcial.flush()
            if i % 10 == 0:
                print("%d/%d %.0f s" % (i + 1, len(pts), time.time() - t0), flush=True)
    _init(sist)
    rho = G["rhoA"]
    saida = dict(sist=sist, cfg={k: (list(v) if isinstance(v, tuple) else v) for k, v in cfg.items()},
                 rhoA_D400=rho, pontos=res, tempo=time.time() - t0)
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "exp26_orfa_%s" % sist)
    with open(base + ".json", "w") as fh:
        json.dump(saida, fh, default=float)
    print("rho_A (D = 400 Mpc):", rho, "tempo", time.time() - t0)


if __name__ == "__main__":
    main()
