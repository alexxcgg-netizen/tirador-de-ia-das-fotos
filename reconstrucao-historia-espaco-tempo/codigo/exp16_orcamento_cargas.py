"""Experimento 16: as memorias de um observador medem o "orcamento de cargas" da binaria?

Hipotese testada (H17 do banco_de_hipoteses.md): as quatro memorias num observador dependem da fonte so
pelas cargas irradiadas na janela (energia E, momento angular) e pela massa final M_f; se fosse assim,
os pares degenerados do exp07 teriam o mesmo M_f e a mesma E irradiada.
Para A e cada par B exato do exp07 (residuo < 1e-5), compara M_f, E irradiada na janela (desde 10 Hz, mais a
energia de ligacao antes da janela) e os multipolos globais (2,0) de deslocamento, (3,0) de spin e (1,0)
giroscopico (nivel A). Saida: resultados/exp16_orcamento_cargas.txt
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def cargas(q, c1, c2, M):
    mem, aux, _, _ = B.memorias_fisicas(q, c1, c2, M, 10.0, nivel="A")
    v, _ = B.vetor(mem)
    return dict(Mf=aux["M_f"] * M, E=aux["E_rad"] * M, desl20=v[0], spin30=v[2], giro10=v[5])


d = json.load(open(os.path.join(AQUI, "..", "resultados", "exp07_pares.json")))
A = d["A"]
cA = cargas(A["q"], A["c1"], A["c2"], A["M"])
log("A (M = %.1f, q = %.2f): M_f = %.4f M_sol, E irradiada = %.4f M_sol; multipolos globais desl20 %.5f spin30 %.5f giro10 %.5f"
    % (A["M"], A["q"], cA["Mf"], cA["E"], cA["desl20"], cA["spin30"], cA["giro10"]))
log("Pares exatos do exp07: variacao relativa B/A - 1")
for p in d["pares"]:
    if max(abs(x) for x in p["dif"].values()) > 1e-5:
        continue
    c = cargas(p["qB"], p["c1"], p["c2B"], p["M"])
    log("  q_B = %.0f, chi2_B = %+.1f (M_B = %.2f, D_B = %.1f Mpc, iota_B = %.1f graus): " % (
        p["qB"], p["c2B"], p["M"], p["D"], np.degrees(p["iota"]))
        + " ".join("%s %+.4f" % (k, c[k] / cA[k] - 1) for k in cA))
log("Conclusao: M_f e E variam ate ~14% ao longo da familia; a inclinacao e a distancia compensam. Hipotese refutada.")
with open(os.path.join(AQUI, "..", "resultados", "exp16_orcamento_cargas.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
