"""Revisao R2: rho_crit ao longo da familia degenerada perto de A (q_B -> q_A = 1.2, chi2_B = -0.2).
Compara o match sem tratamento (exp07) e com janela de cosseno de 0.5 s no inicio e rampa no fim.

A familia de um observador passa por A; logo, para q_B -> 1.2, B -> A e o match -> 1. Mede 1 - match
(aLIGO, busca no tempo x16) para q_B = 1.15, 1.18, 1.19, 1.21, 1.22, 1.25 e verifica se 1 - match ~ (dq)^2,
o que da a largura da familia que a onda nao separa numa SNR dada: dq ~ dq_ref * rho_crit(dq_ref) / rho.
Saida: resultados/revisao/rev_R2_familia_perto.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import rev_R2_comum as C                                # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
F = 10.0
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A, alvo = dados["A"], dados["alvo"]
lista = B.lista_osc() + B.MODOS_M0
tA, hA = B.gerar(A["q"], A["c1"], A["c2"], f0=A["M"] * Dt.MSUN_S * F)
tsA, sA = Dt.strain_observador(tA, hA, lista, A["M"], A["D"], A["iota"])
dqs, mis, mist = [], [], []
for qB in (1.15, 1.18, 1.19, 1.21, 1.22, 1.25):
    par, r = E7.resolver(alvo, qB, -0.2, (A["iota"], 0.3, 65.0))
    tB, hB = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * F)
    tsB, sB = Dt.strain_observador(tB, hB, lista, par["M"], par["D"], par["iota"])
    c = C.comparar(tsA, sA, tsB, sB, "aLIGO", F, up=16)
    k = C.criterios(c)
    # com janela de cosseno de 0.5 s no inicio e a memoria levada a zero por rampa no fim
    ct = C.comparar(tsA, sA, tsB, sB, "aLIGO", F, up=16, taper=0.5, fim="rampa")
    kt = C.criterios(ct)
    dqs.append(abs(qB - 1.2))
    mis.append(1 - c["match"])
    mist.append(1 - ct["match"])
    log("q_B %.2f: M %.4f chi1 %+.5f D %.3f iota %.3f graus | residuo %.1e | aLIGO 1-match %.3e, SNR_B/SNR_A %.4f, "
        "rho_crit igual %.1f exato %.1f | com janela e rampa: 1-match %.3e, rho_crit exato %.1f"
        % (qB, par["M"], par["c1"], par["D"], np.degrees(par["iota"]), r,
           1 - c["match"], k["r"], k["rc_igual"], k["rc_exato"], 1 - ct["match"], kt["rc_exato"]))
    del tB, hB, tsB, sB
p = np.polyfit(np.log(dqs), np.log(mis), 1)
log("ajuste sem janela: 1 - match = %.3g dq^%.2f" % (np.exp(p[1]), p[0]))
p = np.polyfit(np.log(dqs), np.log(mist), 1)
log("ajuste com janela e rampa: 1 - match = %.3g dq^%.2f (usado abaixo)" % (np.exp(p[1]), p[0]))
for rho in (10, 66, 899):
    # (dh|dh) ~ 2 rho^2 (1 - match) = 1  =>  1 - match = 1/(2 rho^2)
    dq = (1 / (2 * rho ** 2) / np.exp(p[1])) ** (1 / p[0])
    log("  SNR %4d: membros com |q_B - 1.2| < %.4f nao sao separados pela onda (criterio do 07, extrapolacao do ajuste)"
        % (rho, dq))
with open(os.path.join(RES, "revisao", "rev_R2_familia_perto.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
