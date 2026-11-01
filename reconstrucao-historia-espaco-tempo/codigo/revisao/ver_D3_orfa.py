"""Verificacao D3: memoria orfa, 1 - match minimo (plano h+_B, hx_B; tempo livre; M livre) por pipeline independente.

Serie de B por observaveis.serie_memoria em M_ref = 45.5 (inicio 10 Hz em M_ref, isto e, abaixo de 10 Hz para
M > 45.5) e reescalada no tempo para outros M; espectro por reamostragem + hold + rampa (ver_D3_comum). Busca em ln M
por varredura (25 pontos em [0.7, 1.5] M_A) e refino de Brent. Busca no tempo por produto cruzado com zero padding
x16 e refino continuo. Compara com exp26_orfa_A.json.
Uso: python revisao/ver_D3_orfa.py
"""
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, ".."))

IOTA = np.radians(50.0)
M_REF = 45.5
FMAX = 1000.0
PONTOS = [("exp07 qB=4", 4.0, 0.7999999228484043, 0.0), ("exp07 qB=2", 2.0, 0.217402923496751, 0.0),
          ("exp07 qB=6", 6.0, 0.8, 0.0), ("canto 1,+.8,+.8", 1.0, 0.8, 0.8), ("canto 6,-.8,-.8", 6.0, -0.8, -0.8),
          ("canto 6,+.8,+.8", 6.0, 0.8, 0.8), ("q=5, 0, 0", 5.0, 0.0, 0.0)]


def espectros_em(ts_ref, hp, hx, M):
    import ver_D3_comum as V
    ts = ts_ref * (M / M_REF)
    if ts[0] < V.T_INI + 1.0:                       # corta o inicio muito abaixo de 10 Hz (fora da banda)
        k = int(np.searchsorted(ts, V.T_INI + 1.0))
        ts, hp, hx = ts[k:], hp[k:] - hp[k], hx[k:] - hx[k]
    f, Sp = V.espectro(V.grade(ts, hp))
    _, Sx = V.espectro(V.grade(ts, hx))
    sel = f <= FMAX
    return f[sel], Sp[sel], Sx[sel]


def match_plano(sA, bp, bx, w, df, f, up=16):
    from scipy.optimize import minimize_scalar
    import ver_D3_comum as V
    aa = V.prod(sA, sA, w, df)
    G = np.array([[V.prod(bp, bp, w, df), V.prod(bp, bx, w, df)], [V.prod(bx, bp, w, df), V.prod(bx, bx, w, df)]])
    Gi = np.linalg.inv(G)
    cp = sA * np.conj(bp) * w * 4 * df
    cx = sA * np.conj(bx) * w * 4 * df
    n = len(f)
    Nt = 2 * (n - 1) * up

    def serie_t(c):
        full = np.zeros(Nt // 2 + 1, dtype=complex)
        full[:n] = c
        return 0.5 * Nt * np.fft.irfft(full, n=Nt)

    Op, Ox = serie_t(cp), serie_t(cx)
    st = Gi[0, 0] * Op ** 2 + 2 * Gi[0, 1] * Op * Ox + Gi[1, 1] * Ox ** 2
    j = int(np.argmax(st))
    tau = j / (Nt * (f[1] - f[0]))
    sel = w > 0
    fs_, cps, cxs = f[sel], cp[sel], cx[sel]

    def menos(t_):
        e = np.exp(2j * np.pi * fs_ * t_)
        a, b = np.real(np.sum(cps * e)), np.real(np.sum(cxs * e))
        return -(Gi[0, 0] * a * a + 2 * Gi[0, 1] * a * b + Gi[1, 1] * b * b)

    h = 1.0 / (Nt * (f[1] - f[0]))
    r = minimize_scalar(menos, bounds=(tau - 2 * h, tau + 2 * h), method="bounded", options=dict(xatol=1e-10))
    best = max(st[j], -r.fun)
    # so h+ de B (psi_B = 0, amplitude com sinal livre): para medir quanto o plano ajuda
    bpp = V.prod(bp, bp, w, df)
    so_p = np.max(np.abs(Op)) / np.sqrt(aa * bpp)
    return float(np.sqrt(max(best, 0) / aa)), float(so_p)


def match_rede(sA, sAx, bp, bx, w, df, f, up=16):
    """Rede ideal (+ e x co-localizados): dados (sA, sAx); molde a [c bp + s bx, -s bp + c bx], c = cos 2psi.
    O conjunto dos moldes e o plano gerado por u1 = (bp, bx) e u2 = (bx, -bp) no espaco de dois canais."""
    import ver_D3_comum as V
    aa = V.prod(sA, sA, w, df) + V.prod(sAx, sAx, w, df)
    g11 = V.prod(bp, bp, w, df) + V.prod(bx, bx, w, df)
    g12 = V.prod(bp, bx, w, df) - V.prod(bx, bp, w, df)          # = 0
    n = len(f)
    Nt = 2 * (n - 1) * up

    def serie_t(c):
        full = np.zeros(Nt // 2 + 1, dtype=complex)
        full[:n] = c
        return 0.5 * Nt * np.fft.irfft(full, n=Nt)
    k = w * 4 * df
    O1 = serie_t(sA * np.conj(bp) * k) + serie_t(sAx * np.conj(bx) * k)
    O2 = serie_t(sA * np.conj(bx) * k) - serie_t(sAx * np.conj(bp) * k)
    G = np.array([[g11, g12], [g12, g11]])
    Gi = np.linalg.inv(G)
    st = Gi[0, 0] * O1 ** 2 + 2 * Gi[0, 1] * O1 * O2 + Gi[1, 1] * O2 ** 2
    return float(np.sqrt(max(st.max(), 0) / aa)), float(np.sqrt(aa))


def ponto(args):
    from scipy.optimize import minimize_scalar
    import ver_D3_comum as V
    V.T_INI = -40.0
    V.NFFT = 2 ** 19
    rot, q, c1, c2 = args
    t1 = time.time()
    (ts, hp, hx), = V.serie(q, c1, c2, M_REF, [IOTA])
    (tsA, hpA, hxA), = V.serie(1.2, 0.3, -0.2, 65.0, [IOTA])
    f, sA, sAx = espectros_em(tsA * (M_REF / 65.0), hpA, hxA, 65.0)
    df = f[1] - f[0]
    W = {p: V.pesos(p, f) for p in ("ET", "CE")}
    out = dict(rotulo=rot, q=q, c1=c1, c2=c2)
    cache = {}

    def mm(lnM, p):
        key = round(lnM, 10)
        if key not in cache:
            cache[key] = espectros_em(ts, hp, hx, float(np.exp(lnM)))
        _, bp, bx = cache[key]
        m, mp_ = match_plano(sA, bp, bx, W[p], df, f)
        return 1 - m, 1 - mp_

    grade = np.log(65.0) + np.linspace(np.log(0.7), np.log(1.5), 25)
    for p in ("CE", "ET"):
        v = np.array([mm(g, p)[0] for g in grade])
        j = int(np.argmin(v))
        r = minimize_scalar(lambda x: mm(x, p)[0], bounds=(grade[max(j - 1, 0)], grade[min(j + 1, 24)]),
                            method="bounded", options=dict(xatol=1e-4))
        out[p] = dict(mm_min=float(r.fun), M_star=float(np.exp(r.x)), mm_M65=float(mm(np.log(65.0), p)[0]),
                      mm_so_hplus_Mstar=float(mm(float(r.x), p)[1]), perfil=v.tolist(), borda=bool(j in (0, 24)))
    # rede ideal: minimo em ln M na mesma grade + Brent
    for p in ("CE",):
        def mr(x):
            _, bp, bx = cache.get(round(x, 10)) or espectros_em(ts, hp, hx, float(np.exp(x)))
            return 1 - match_rede(sA, sAx, bp, bx, W[p], df, f)[0]
        v = np.array([mr(g) for g in grade])
        j = int(np.argmin(v))
        r = minimize_scalar(mr, bounds=(grade[max(j - 1, 0)], grade[min(j + 1, 24)]), method="bounded",
                            options=dict(xatol=1e-4))
        out["rede_" + p] = dict(mm_min=float(r.fun), M_star=float(np.exp(r.x)),
                                rho_rede=match_rede(sA, sAx, sA, sAx, W[p], df, f)[1])
        print("   rede %s: mm_min %.3e M* %.2f rho %.2f" % (p, r.fun, np.exp(r.x), out["rede_" + p]["rho_rede"]), flush=True)
    out["rhoA"] = {p: float(np.sqrt(V.prod(sA, sA, W[p], df))) for p in W}
    out["tempo"] = time.time() - t1
    return out


def main():
    t0 = time.time()
    ref = {}
    J = json.load(open(os.path.join(AQUI, "..", "..", "resultados", "exp26_orfa_A.json")))
    for pt in J["pontos"]:
        ref[(round(pt["q"], 4), round(pt["c1"], 4), round(pt["c2"], 4))] = pt
    ctx = mp.get_context("spawn")
    res = []
    with ctx.Pool(2) as pool:
        for r in pool.imap(ponto, PONTOS):
            k = (round(r["q"], 4), round(r["c1"], 4), round(r["c2"], 4))
            e = ref.get(k)
            if e is not None and "CE" in e:
                r["exp26"] = {p: dict(mm_M=e[p]["mm_M"], M_star=float(np.exp(e[p]["lnM_M"])), mm_MA=e[p]["mm_MA"])
                              for p in ("CE", "ET")}
            res.append(r)
            print(r["rotulo"], "rhoA", r["rhoA"], flush=True)
            for p in ("CE", "ET"):
                print("   %s: mm_min %.3e M* %.2f mm(M=65) %.3e | so h+ %.3e | borda %s" % (
                    p, r[p]["mm_min"], r[p]["M_star"], r[p]["mm_M65"], r[p]["mm_so_hplus_Mstar"], r[p]["borda"]),
                    "| exp26:", r.get("exp26", {}).get(p), flush=True)
    with open(os.path.join(AQUI, "..", "..", "resultados", "ver_D3_orfa.json"), "w") as fh:
        json.dump(dict(pontos=res, tempo=time.time() - t0), fh, default=float, indent=1)
    print("tempo %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
