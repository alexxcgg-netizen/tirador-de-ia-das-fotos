"""Verificador R4v, item 1 (origem do tremor): a onda muda desde o primeiro ponto ou so perto da fusao?

B (e0 = 0.2, q_B = 2) do exp12 e o circular A, com M e M (1 + eps). Compara h22 amostra a amostra (alinhado no
INICIO, mesmo indice), por trechos, e a energia irradiada int |dh/dt|^2 (todos os modos) por trecho.
Saida: resultados/revisao/rev_R4v_origem.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
COD = os.path.dirname(AQUI)
RAIZ = os.path.dirname(COD)
sys.path.insert(0, COD)
import deteccao as Dt                                   # noqa: E402
import exp12_excentricas_imr as E                       # noqa: E402

RES = os.path.join(RAIZ, "resultados", "revisao")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def comparar(rot, q, c1, c2, M, e0, eps):
    ta, ha = E.gerar(q, c1, c2, M * Dt.MSUN_S * E.F_FIS, e0)
    tb, hb = E.gerar(q, c1, c2, M * (1 + eps) * Dt.MSUN_S * E.F_FIS, e0)
    n = min(len(ta), len(tb))
    ip = np.argmax(np.abs(ha[(2, 2)]))
    s = ta[:n] - ta[ip]
    log("%s, M (1 + %.0e): %d x %d amostras ; t0 %.4f x %.4f ; t_fim %.4f x %.4f ; indice do pico %d x %d"
        % (rot, eps, len(ta), len(tb), ta[0], tb[0], ta[-1], tb[-1], ip, np.argmax(np.abs(hb[(2, 2)]))))
    a, b = ha[(2, 2)][:n], hb[(2, 2)][:n]
    dr = np.abs(b - a) / np.abs(a)
    dt = ta[1] - ta[0]
    def edot(h):
        return sum(np.abs(np.gradient(h[k][:n], dt)) ** 2 for k in E.LISTA)
    ea, eb = edot(ha), edot(hb)
    for (u1, u2) in [(s[0], s[0] + 10), (s[0] + 10, s[0] + 1000), (s[0] + 1000, -5000), (-5000, -1000), (-1000, -100), (-100, 0), (0, s[-1] + 1)]:
        sel = (s >= u1) & (s < u2)
        if not np.any(sel):
            continue
        dE = (np.sum(eb[sel]) - np.sum(ea[sel])) / np.sum(ea[sel])
        log("   t - t_pico em [%8.1f, %8.1f): max |dh22|/|h22| (mesmo indice) %.1e ; energia do trecho, var. rel. %+.1e"
            % (u1, u2, np.max(dr[sel]), dE))
    del ta, ha, tb, hb


if __name__ == "__main__":
    DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp12_pares.json")))
    p = [x for x in DADOS["pares"] if x["e0"] == 0.2 and x["qB"] == 2.0][0]
    comparar("B (0.2, 2)", 2.0, p["c1"], 0.0, p["M"], 0.2, 1e-15)
    comparar("B (0.2, 2)", 2.0, p["c1"], 0.0, p["M"], 0.2, 1e-12)
    A = DADOS["A"]
    comparar("A (circular)", A["q"], A["c1"], A["c2"], A["M"], 0.0, 1e-12)
    with open(os.path.join(RES, "rev_R4v_origem.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
