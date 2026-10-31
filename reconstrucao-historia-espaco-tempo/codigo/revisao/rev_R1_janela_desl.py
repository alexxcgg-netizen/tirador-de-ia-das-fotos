"""Revisao R1: os pares do exp07 foram casados com o deslocamento TOTAL (parte anterior a 10 Hz pela formula
3PN de Favata). Um detector so ve o que acumula na banda. Quanto os pares diferem no deslocamento de janela?
Nivel A (o mesmo do exp07), observador de cada sistema, unidades fisicas.
Saida: resultados/revisao/rev_R1_janela_desl.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import deteccao as Dt                                    # noqa: E402
from harmonicos import sYlm                              # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1_janela_desl.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def desl(q, c1, c2, M, D, iota):
    mem, aux, t, h = B.memorias_fisicas(q, c1, c2, M, 10.0, nivel="A")
    del t, h
    eta = q / (1 + q) ** 2
    x0 = aux["x0"]
    pre = {(2, 0): B.favata_h20(x0, eta), (4, 0): B.lrr_h40(x0, eta)}
    ls = sorted(l for (l, m) in mem["deslocamento"] if m == 0 and l <= 8)       # mesma soma de no_observador
    tot = sum(mem["deslocamento"][(l, 0)].real * sYlm(-2, l, 0, iota, 0.0).real for l in ls)
    jan = sum((mem["deslocamento"][(l, 0)].real - pre.get((l, 0), 0.0)) * sYlm(-2, l, 0, iota, 0.0).real for l in ls)
    f = M * Dt.MSUN_S / (D * Dt.MPC_S)
    return tot * f, jan * f


with open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")) as fh:
    J = json.load(fh)
A = J["A"]
tA, jA = desl(A["q"], A["c1"], A["c2"], A["M"], A["D"], A["iota"])
log("A: deslocamento total = %.5e ; de janela (desde 10 Hz) = %.5e ; fracao anterior a 10 Hz = %.3f" % (tA, jA, 1 - jA / tA))
for p in J["pares"]:
    tB, jB = desl(p["qB"], p["c1"], p["c2B"], p["M"], p["D"], p["iota"])
    log("B (q=%.0f, chi2=%+.1f): total (B-A)/A = %+.1e ; janela (B-A)/A = %+.2e" % (p["qB"], p["c2B"], tB / tA - 1, jB / jA - 1))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(linhas) + "\n")
