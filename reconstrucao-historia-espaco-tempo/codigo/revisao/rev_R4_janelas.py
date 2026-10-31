"""Revisor R4, tarefa 4: dependencia de janela (exp14) e teste de uma SEGUNDA janela (NRHybSur3dq8_CCE, nivel A).

a) Confere a linha (2, 0) da tabela de janelas do 07 §3.6: par q_B = 2, chi2_B = 0 do exp07 com a janela
   comecando em 5, 10 e 20 Hz (mesma funcao do exp14: B.memorias_fisicas + B.valores_fisicos).
b) Duas janelas: 8 equacoes (as quatro memorias com janela desde 10 Hz e desde 20 Hz) para as 6 incognitas
   (q_B, chi1_B, chi2_B, M_B, iota_B, D_B). least_squares a partir do par (2, 0):
     b1) as 6 livres (atencao: B = A e solucao trivial; registro para onde o otimizador vai);
     b2) q_B fixo (1.0, 1.5, 2.0, 3.0) e as outras 5 livres: menor residuo para B != A (perfil em q_B);
     b3) uma janela so (10 Hz), q_B = 2 e 5 livres: controle (deve dar ~1e-10, familia de dimensao 1 aqui).
   Residuos relativos (m_B - m_A)/|m_A|. Cache so de memorias (dicionarios), chave sem arredondamento.
Saida: resultados/revisao/rev_R4_janelas.txt e .json
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
        m, _, _, _ = B.memorias_fisicas(q, c1, c2, M, f, nivel="A")
        _cache[k] = m
    return _cache[k]


def quatro(par, f):
    return B.valores_fisicos(mem(par["q"], par["c1"], par["c2"], par["M"], f), par["iota"], par["M"], par["D"])


def dif(v, a):
    return {k: (v[k] - a[k]) / abs(a[k]) for k in TIP}


DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp07_pares.json")))
A = DADOS["A"]
P = {(p["qB"], p["c2B"]): dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
     for p in DADOS["pares"]}
JANELAS = (10.0, 20.0)
LIM = dict(q=(1.0, 8.0), c1=(-0.8, 0.8), c2=(-0.8, 0.8), M=(35.0, 250.0), iota=(0.05, np.pi - 0.05), D=(50.0, 3000.0))


def residuos(par, alvos, janelas):
    r = []
    for f in janelas:
        v = quatro(par, f)
        r += [(v[k] - alvos[f][k]) / abs(alvos[f][k]) for k in TIP]
    return np.array(r)


def resolver(x0, livres, fixos, alvos, janelas, max_nfev=100):
    def montar(x):
        par = dict(fixos)
        par.update(dict(zip(livres, x)))
        return par

    lo = [LIM[n][0] for n in livres]
    hi = [LIM[n][1] for n in livres]
    x0 = np.clip([x0[n] for n in livres], np.array(lo) + 1e-9, np.array(hi) - 1e-9)
    r = least_squares(lambda x: residuos(montar(x), alvos, janelas), x0, bounds=(lo, hi), x_scale="jac",
                      diff_step=1e-5, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=max_nfev)
    return montar(r.x), r


def fmt(par):
    return "q %.4f chi1 %+.4f chi2 %+.4f M %.3f iota %.2f graus D %.1f Mpc" % (
        par["q"], par["c1"], par["c2"], par["M"], np.degrees(par["iota"]), par["D"])


if __name__ == "__main__":
    t0 = time.time()
    out = {}
    log("a) Par (2, 0) do exp07 (q_B = 2, chi2_B = 0): diferenca relativa B - A com a janela comecando em f_ini (nivel A)")
    B20 = P[(2.0, 0.0)]
    alvos = {}
    for f in (5.0, 10.0, 20.0):
        alvos[f] = quatro(A, f)
        d = dif(quatro(B20, f), alvos[f])
        log("  %4.0f Hz: " % f + " ".join("%s %+.2e" % (k[:4], d[k]) for k in TIP))
        out["a_%g" % f] = d
    log("  (exp14: 5 Hz desl +1.9e-04 spin -1.3e-02 cm +1.7e-04 giro -9.0e-03 ; 20 Hz desl -6.8e-04 spin +2.0e-02 cm -1.2e-04 giro +1.4e-02)")
    _cache.clear()
    log()
    log("b) Duas janelas (10 e 20 Hz): 8 equacoes")
    out["b"] = []
    # b3 controle: uma janela
    par, r = resolver(B20, ["c1", "c2", "M", "iota", "D"], dict(q=2.0), alvos, (10.0,))
    log("  b3 controle, so 10 Hz, q_B = 2 fixo, 5 livres: max|res| = %.2e (%d aval.) -> %s" % (np.max(np.abs(r.fun)), r.nfev, fmt(par)))
    # b1 todas livres
    par, r = resolver(B20, ["q", "c1", "c2", "M", "iota", "D"], {}, alvos, JANELAS)
    dA = max(abs(par[k] / A[k] - 1) for k in ("q", "M", "D"))
    log("  b1 6 livres a partir do par (2, 0): max|res| = %.2e, norma %.2e (%d aval.) -> %s ; distancia a A (max rel. em q, M, D) %.1e"
        % (np.max(np.abs(r.fun)), np.linalg.norm(r.fun), r.nfev, fmt(par), dA))
    log("      residuos: " + " ".join("%+.1e" % x for x in r.fun))
    out["b"].append(dict(caso="b1", par=par, res=r.fun.tolist()))
    _cache.clear()
    # b2 perfil em q_B
    partida = {1.0: P[(1.0, 0.0)], 1.5: dict(B20, q=1.5, c1=0.15, M=67.0), 2.0: B20, 3.0: P[(3.0, 0.0)]}
    for qB, x0 in partida.items():
        par, r = resolver(x0, ["c1", "c2", "M", "iota", "D"], dict(q=qB), alvos, JANELAS)
        # segunda partida: chi2 deslocado
        par2, r2 = resolver(dict(x0, c2=x0["c2"] + 0.3), ["c1", "c2", "M", "iota", "D"], dict(q=qB), alvos, JANELAS)
        if np.linalg.norm(r2.fun) < np.linalg.norm(r.fun):
            par, r = par2, r2
        log("  b2 q_B = %.1f fixo, 5 livres (melhor de 2 partidas): max|res| = %.2e, norma %.2e (%d aval.) -> %s"
            % (qB, np.max(np.abs(r.fun)), np.linalg.norm(r.fun), r.nfev, fmt(par)))
        log("      residuos 10 Hz: %s | 20 Hz: %s" % (" ".join("%+.1e" % x for x in r.fun[:4]), " ".join("%+.1e" % x for x in r.fun[4:])))
        out["b"].append(dict(caso="b2", qB=qB, par=par, res=r.fun.tolist()))
        _cache.clear()
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "rev_R4_janelas.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(RES, "rev_R4_janelas.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
