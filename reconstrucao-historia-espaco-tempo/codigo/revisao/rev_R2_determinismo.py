"""Revisao R2: as memorias de um mesmo ponto sao reprodutiveis entre avaliacoes?

Motivo: rodando o exp07 de novo (serial, rev_R2_roda_exp07.py), os parametros das solucoes saem identicos
bit a bit aos do exp07_pares.json original, mas o 'max dif. memorias' muda (par (3, 0): 3.0e-6 no original,
7.9e-8 agora). No original, as memorias de B eram recalculadas no processo principal; aqui vem do cache do
otimizador. Este script recalcula as memorias dos pares e de A varias vezes, em ordens diferentes, sem cache,
e mede a dispersao relativa. Tambem varia M em passos minusculos (1e-9 relativo) para ver se a funcao
memoria(M) tem saltos (grade de tempo do substituto dependente de f_low).
Saida: resultados/revisao/rev_R2_determinismo.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
F = 10.0
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A = dados["A"]
alvo = dados["alvo"]


def fis(par, nivel="A"):
    mem, aux, t, h = B.memorias_fisicas(par["q"], par["c1"], par["c2"], par["M"], F, nivel=nivel)
    v = B.valores_fisicos(mem, par["iota"], par["M"], par["D"])
    return v, len(t), t[0]


def pares():
    for p in dados["pares"]:
        yield (p["qB"], p["c2B"]), dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])


log("1) Repeticao: memorias de A e dos pares, 3 passagens em ordens diferentes (sem cache).")
vals = {}
ordem = [("A", A)] + list(pares())
for rodada, seq in enumerate([ordem, ordem[::-1], ordem[1::2] + ordem[0::2]]):
    for nome, par in seq:
        v, n, t0 = fis(par)
        vals.setdefault(str(nome), []).append((v, n, t0))
for nome, lst in vals.items():
    disp = max(max(abs(x[0][k] / lst[0][0][k] - 1) for x in lst) for k in B.TIPOS)
    ns = sorted(set(x[1] for x in lst))
    dif_alvo = [max(abs(x[0][k] / alvo[k] - 1) for k in B.TIPOS) for x in lst]
    log("  %-12s dispersao relativa entre passagens %.1e ; n amostras %s ; max dif. contra o alvo do json: %s"
        % (nome, disp, ns, " ".join("%.1e" % d for d in dif_alvo)))

log("")
log("2) Suavidade em M: memorias de B (par (3, 0)) com M -> M (1 + e), e de 1e-12 a 1e-6.")
p3 = dict(list(pares()))[(3.0, 0.0)]
v0, n0, t00 = fis(p3)
for e in (1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6):
    q = dict(p3, M=p3["M"] * (1 + e))
    v, n, t0 = fis(q)
    # a escala M/D e M^2/D muda por (1 + e) ou (1 + 2e); a parte nao trivial e o resto
    log("  e = %.0e: n amostras %d (base %d), t0 %.6f (base %.6f) | variacao relativa: %s"
        % (e, n, n0, t0, t00, " ".join("%s %+.2e" % (k[:4], v[k] / v0[k] - 1) for k in B.TIPOS)))
with open(os.path.join(RES, "revisao", "rev_R2_determinismo.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
