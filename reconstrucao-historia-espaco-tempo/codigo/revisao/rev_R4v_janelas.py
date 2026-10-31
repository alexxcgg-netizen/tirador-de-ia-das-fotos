"""Verificador R4v, item 7: duas janelas (10 e 20 Hz) com B resolvido de novo (NRHybSur3dq8_CCE, nivel A).

 a) avalia as 8 diferencas (4 memorias desde 10 Hz e desde 20 Hz) no par (2, 0) original do exp07 e no ponto
    q_B = 2 que o revisor R4 relatou (parametros impressos com 4 algarismos), e refina esse ponto com
    least_squares (q_B = 2 fixo, 5 livres) partindo dele;
 b) uma partida independente: a solucao do exp07 para q_B = 2 com chi2 = -0.2 (o chi2 de A);
 c) valores singulares do jacobiano 8 x 6 em A com passos diferentes dos do R4 (metade e o dobro).
Mesma cadeia do exp07/exp14: B.memorias_fisicas(..., nivel="A") + B.valores_fisicos. Cache so de memorias.
Saida: resultados/revisao/rev_R4v_janelas.txt
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

AQUI = os.path.dirname(os.path.abspath(__file__))
COD = os.path.dirname(AQUI)
RAIZ = os.path.dirname(COD)
sys.path.insert(0, COD)
import binarias as B                                    # noqa: E402

RES = os.path.join(RAIZ, "resultados", "revisao")
TIP = B.TIPOS
linhas = []
_cache = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def mem(q, c1, c2, M, f):
    k = (float(q), float(c1), float(c2), float(M), float(f))
    if k not in _cache:
        _cache[k] = B.memorias_fisicas(q, c1, c2, M, f, nivel="A")[0]
    return _cache[k]


def quatro(par, f):
    return B.valores_fisicos(mem(par["q"], par["c1"], par["c2"], par["M"], f), par["iota"], par["M"], par["D"])


def res8(par, alvos):
    r = []
    for f in (10.0, 20.0):
        v = quatro(par, f)
        r += [(v[k] - alvos[f][k]) / abs(alvos[f][k]) for k in TIP]
    return np.array(r)


def fmt(par):
    return "q %.4f chi1 %+.4f chi2 %+.4f M %.3f iota %.2f graus D %.1f" % (
        par["q"], par["c1"], par["c2"], par["M"], np.degrees(par["iota"]), par["D"])


def fr(r):
    return "max %.2e | 10 Hz: %s | 20 Hz: %s" % (np.max(np.abs(r)), " ".join("%+.1e" % x for x in r[:4]),
                                                 " ".join("%+.1e" % x for x in r[4:]))


def refinar(x0, alvos, nfev=40):
    livres = ["c1", "c2", "M", "iota", "D"]
    lo = [-0.8, -0.8, 35.0, 0.05, 50.0]
    hi = [0.8, 0.8, 250.0, np.pi - 0.05, 3000.0]

    def montar(x):
        return dict(q=2.0, **dict(zip(livres, x)))
    r = least_squares(lambda x: res8(montar(x), alvos), [x0[n] for n in livres], bounds=(lo, hi), x_scale="jac",
                      diff_step=1e-6, xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=nfev)
    return montar(r.x), r


if __name__ == "__main__":
    t0 = time.time()
    DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp07_pares.json")))
    A = DADOS["A"]
    p20 = [p for p in DADOS["pares"] if p["qB"] == 2.0 and p["c2B"] == 0.0][0]
    B20 = dict(M=p20["M"], q=2.0, c1=p20["c1"], c2=0.0, D=p20["D"], iota=p20["iota"])
    alvos = {f: quatro(A, f) for f in (10.0, 20.0)}
    t1 = time.time()
    log("a) par (2, 0) original do exp07: %s" % fr(res8(B20, alvos)))
    log("   (%.1f s por par de avaliacoes)" % (time.time() - t1))
    R4 = dict(q=2.0, c1=0.4185, c2=-0.2021, M=68.173, iota=np.radians(51.99), D=395.3)
    log("   ponto q_B = 2 do R4 (rev_R4_janelas3, 4 algarismos): %s" % fr(res8(R4, alvos)))
    par, r = refinar(R4, alvos)
    log("   refinado a partir dele (%d aval.): %s -> %s ; norma %.2e" % (r.nfev, fr(r.fun), fmt(par), np.linalg.norm(r.fun)))
    _cache.clear()
    log()
    x0 = dict(B20, c2=-0.2)
    par, r = refinar(x0, alvos, nfev=60)
    log("b) partida independente (par (2, 0) com chi2 = -0.2): (%d aval.) %s -> %s ; norma %.2e"
        % (r.nfev, fr(r.fun), fmt(par), np.linalg.norm(r.fun)))
    _cache.clear()
    log()
    log("c) valores singulares do jacobiano em A (colunas escaladas por 0.1, 0.1, 0.1, 1 Msol, 0.01 rad, 0.01 D)")
    nomes = ["q", "c1", "c2", "M", "iota", "D"]
    esc = np.array([0.1, 0.1, 0.1, 1.0, 0.01, 0.01 * A["D"]])
    base = dict(q=1e-3, c1=1e-3, c2=1e-3, M=1e-2, iota=1e-4, D=1e-2)
    for fator in (0.5, 2.0):
        J = np.zeros((8, 6))
        for j, n in enumerate(nomes):
            h = base[n] * fator
            J[:, j] = (res8(dict(A, **{n: A[n] + h}), alvos) - res8(dict(A, **{n: A[n] - h}), alvos)) / (2 * h)
        Js = J * esc
        log("   passos x %.1f: 10 Hz %s ; 10 + 20 Hz %s" % (
            fator, " ".join("%.2e" % s for s in np.linalg.svd(Js[:4], compute_uv=False)),
            " ".join("%.2e" % s for s in np.linalg.svd(Js, compute_uv=False))))
        Jd = Js[4:] - Js[:4]
        log("            so a diferenca 20 Hz - 10 Hz (4 x 6): %s" % " ".join("%.2e" % s for s in np.linalg.svd(Jd, compute_uv=False)))
        _cache.clear()
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "rev_R4v_janelas.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
