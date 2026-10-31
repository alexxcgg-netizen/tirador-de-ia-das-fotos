"""Verificacao independente (R2v) do item 1 da revisao R2: os pares 'exatos' resolvidos de novo no nivel C.

Para cada par 'exato' do exp07, repete a resolucao do exp11 (nivel C, partindo da solucao do nivel A) e,
para o par (2, +0.5), resolve uma segunda vez partindo da solucao obtida ('a partir do ultimo ponto', como diz
o 07 §3.4). Depois recalcula o residuo SEM o cache do exp07 (que arredonda os parametros em 9 casas) e mede
o numero de amostras e o residuo com M_B (1 +- 1e-10): a solucao esta numa aresta da escada?
Por fim, o tamanho do degrau da escada no nivel C perto da solucao do par (2, +0.5).
Saida: resultados/revisao/rev_R2v_nivelC.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402
from deteccao import MSUN_S                             # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def residuo_sem_cache(par, alvo):
    """Residuo maximo das 4 memorias (D_B ja fixado) e n amostras, calculados sem cache."""
    mem, _, t, _ = B.memorias_fisicas(par["q"], par["c1"], par["c2"], par["M"], E7.F_FIS, nivel="C")
    v = B.valores_fisicos(mem, par["iota"], par["M"], par["D"])
    return max(abs(v[k] / alvo[k] - 1) for k in B.TIPOS), len(t), v


dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A = E7.A
t0 = time.time()
alvoC, _ = E7.fisicos(A, "C")
exatos = [x for x in dados["pares"] if max(abs(y) for y in x["dif"].values()) < 1e-5]
sol22 = None
for p in exatos:
    E7._cache.clear()
    novo, r = E7.resolver(alvoC, p["qB"], p["c2B"], (p["iota"], p["c1"], p["M"]), nivel="C")
    rs, n, v = residuo_sem_cache(novo, alvoC)
    txt = []
    for e in (-1e-10, 1e-10):
        re_, ne, _ = residuo_sem_cache(dict(novo, M=novo["M"] * (1 + e)), alvoC)
        txt.append("M (1 %+.0e): n%+d residuo %.1e" % (e, ne - n, re_))
    log("par (%.0f, %+.1f): resolvido em C, residuo do otimizador %.2e ; recalculado sem cache %.2e (%s) ; %s (%.0f s)"
        % (p["qB"], p["c2B"], r, rs, " ".join("%s %+.1e" % (k[:4], v[k] / alvoC[k] - 1) for k in B.TIPOS),
           " ; ".join(txt), time.time() - t0))
    if p["qB"] == 2.0 and p["c2B"] == 0.5:
        sol22 = novo
        E7._cache.clear()
        novo2, r2 = E7.resolver(alvoC, p["qB"], p["c2B"], (novo["iota"], novo["c1"], novo["M"]), nivel="C")
        rs2, _, _ = residuo_sem_cache(novo2, alvoC)
        log("   (2, +0.5) resolvido uma 2a vez partindo da 1a solucao: residuo do otimizador %.2e ; sem cache %.2e ; "
            "mudanca M %.1e chi1 %.1e" % (r2, rs2, novo2["M"] - novo["M"], novo2["c1"] - novo["c1"]))
# escada no nivel C perto da solucao do par (2, +0.5)
log("Escada no nivel C perto da solucao (2, +0.5): M_B (1 + e), e de 0 a 1.2e-5 em passos de 4e-7.")
serie, ns = [], []
for e in np.arange(0, 1.2e-5 + 1e-13, 4e-7):
    f0 = sol22["M"] * (1 + e) * MSUN_S * E7.F_FIS
    t, h = B.gerar(sol22["q"], sol22["c1"], sol22["c2"], f0=f0)
    mem, _ = B.memorias(sol22["q"], sol22["c1"], sol22["c2"], f0=f0, nivel="C", t=t, h=h)
    vv = B.no_observador(mem, sol22["iota"])
    serie.append([vv[k] for k in B.TIPOS])
    ns.append(len(t))
    del t, h
serie = np.array(serie)
rel = serie / serie[0] - 1
for i in range(1, len(ns)):
    if ns[i] != ns[i - 1]:
        d = rel[i] - rel[i - 1]
        log("   salto n %d -> %d: %s" % (ns[i - 1], ns[i], " ".join("%s %+.2e" % (k[:4], x) for k, x in zip(B.TIPOS, d))))
log("(%.0f s)" % (time.time() - t0))
with open(os.path.join(RES, "revisao", "rev_R2v_nivelC.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
