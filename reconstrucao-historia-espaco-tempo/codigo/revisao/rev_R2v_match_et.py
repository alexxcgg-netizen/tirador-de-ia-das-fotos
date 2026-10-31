"""Verificacao (R2v), item 3: largura da vizinhanca de A que a onda nao separa, no ET (com a curva do ET).

O R2 estimou |q_B - 1.2| < 0.0006 na SNR 899 do ET extrapolando o ajuste de 1 - match feito com a curva do
aLIGO. Aqui o 1 - match e calculado com a PSD do ET (lalsimulation, ET-D, f_min = 10 Hz), pelo ouro de
rev_R2v_match3 (inicio 5 Hz, f_ref = 10 Hz, tempo continuo), fixo em phi_B = 0 e maximizado em phi_B.
Saida: resultados/revisao/rev_R2v_match_et.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import deteccao as Dt                                   # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402
import rev_R2v_match2 as R2M                            # noqa: E402
import rev_R2v_match3 as R3                             # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def psd_et(n, df, fmin):
    k = ("ET", n, round(df, 15), fmin)
    if k not in R2M._psd:
        R2M._psd.clear()
        R2M._psd[k] = Dt.psd_serie("ET", n, df, fmin)
    return R2M._psd[k]


R2M.psd = psd_et                                        # o Comparador de rev_R2v_match3 passa a usar o ET
dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A, alvo = dados["A"], dados["alvo"]
cA, mA = R3.ouro_m(A)
cp = R3.Comparador(R3.serie_phi(cA, mA, 0.0))
del cA, mA
log("SNR de A no ET (ouro, f_min 10 Hz): %.1f" % np.sqrt(cp.aa))
dq, y0, yp = [], [], []
for qB in (1.19, 1.195, 1.205, 1.21):
    pB, r = E7.resolver(alvo, qB, -0.2, (A["iota"], 0.3, 65.0))
    cB, mB = R3.ouro_m(pB)
    cp.preparar_B(cB, mB)
    del cB, mB
    o = cp.um_menos(0.0)
    op, _ = cp.max_phi()
    dq.append(abs(qB - 1.2))
    y0.append(o)
    yp.append(op)
    log("q_B %.3f: ET 1-match ouro %.3e (rho_crit %.1f) ; max. em phi_B %.3e (rho_crit %.1f)"
        % (qB, o, 1 / np.sqrt(2 * o), op, 1 / np.sqrt(2 * op)))
rho = np.sqrt(cp.aa)
for nome, y in (("phi_B = 0", y0), ("max. phi_B", yp)):
    p = np.polyfit(np.log(dq), np.log(y), 1)
    log("%-11s: 1-match = %.3g dq^%.2f -> |dq| nao separado na SNR do ET (%.0f): %.5f"
        % (nome, np.exp(p[1]), p[0], rho, (1 / (2 * rho ** 2) / np.exp(p[1])) ** (1 / p[0])))
with open(os.path.join(RES, "revisao", "rev_R2v_match_et.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
