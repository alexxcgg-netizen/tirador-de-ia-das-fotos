"""Experimento 11: robustez dos pares degenerados (niveis A, B, C).

Para cada par (A, B) achado no exp07 (nivel A: memorias de ordem quadratica a partir dos modos
oscilatorios), recalcula as quatro memorias de A e de B nos niveis
  B (fluxos com a deformacao completa, inclusive os modos de memoria: termos cubicos) e
  C (memoria completa de RN, direto dos modos m = 0 do NRHybSur3dq8_CCE),
mede a diferenca, e resolve de novo no nivel C (partindo da solucao do nivel A) para ver se a
familia degenerada sobrevive, e quanto ela se desloca.
Classificacao: exata (< 1e-8 depois de resolver), aproximada (resolvida so ate 1%), destruida (> 1%).
Tambem: o par global do exp06 (A1 x q = 1.25) no nivel C.
Saida: resultados/exp11_robustez.txt
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


dados = json.load(open(os.path.join(AQUI, "..", "resultados", "exp07_pares.json")))
A = E7.A
for nivel in ("A", "B", "C"):
    alvo, _ = E7.fisicos(A, nivel)
    log("A no nivel %s: " % nivel + ", ".join("%s %.5e" % kv for kv in alvo.items()))
alvoC, _ = E7.fisicos(A, "C")
for p in dados["pares"]:
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    difs = {}
    for nivel in ("A", "B", "C"):
        alvo, _ = E7.fisicos(A, nivel)
        v, _ = E7.fisicos(par, nivel)
        difs[nivel] = max(abs((v[k] - alvo[k]) / alvo[k]) for k in B.TIPOS)
    novo, r = E7.resolver(alvoC, p["qB"], p["c2B"], (p["iota"], p["c1"], p["M"]), nivel="C")
    classe = "exata" if r < 1e-8 else ("aproximada" if r < 1e-2 else "destruida")
    log("par q_B = %.1f, chi2_B = %+.1f: max dif. memorias  A %.1e | B %.1e | C %.1e  -> resolvido em C: residuo %.1e (%s); "
        "desloca M %+.3f, chi1 %+.4f, D %+.2f Mpc, iota %+.2f graus"
        % (p["qB"], p["c2B"], difs["A"], difs["B"], difs["C"], r, classe, novo["M"] - p["M"], novo["c1"] - p["c1"],
           novo["D"] - p["D"], np.degrees(novo["iota"] - p["iota"])))

# par global do exp06
vA = np.array(B.vetor(B.memorias(1.2, 0.3, -0.2, nivel="C")[0])[0])
mu, c1, c2 = 0.9982, 0.372, -0.274
vB = np.array(B.vetor(B.memorias(1.25, c1, c2, nivel="C")[0])[0]) * mu ** np.array([1, 1, 2, 2, 2, 2, 2])
vAa = np.array(B.vetor(B.memorias(1.2, 0.3, -0.2, nivel="A")[0])[0])
vBa = np.array(B.vetor(B.memorias(1.25, c1, c2, nivel="A")[0])[0]) * mu ** np.array([1, 1, 2, 2, 2, 2, 2])
log("par global A1 (q 1.2) x (q 1.25, chi 0.372/-0.274, M x0.9982): max dif. nivel A %.1e ; nivel C %.1e (componentes: %s)"
    % (np.max(np.abs((vBa - vAa) / vAa)), np.max(np.abs((vB - vA) / vA)), np.array2string((vB - vA) / vA, precision=4)))
with open(os.path.join(AQUI, "..", "resultados", "exp11_robustez.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
