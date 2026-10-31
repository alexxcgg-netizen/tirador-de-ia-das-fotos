"""Verificador R4v, item 3 (continuacao): least_squares (trf) com jacobiano proprio de passos grandes.

Mesmo problema de rev_R4v_resolver (3 equacoes em iota, chi1, M; D do deslocamento), mas com o otimizador
de regiao de confianca do scipy usando o jacobiano por diferencas centrais (h_chi1, h_M grandes diante do
tremor), em vez do diff_step = 1e-3 do exp12. Varias partidas: a solucao do json e deslocamentos dela.
Uso: python revisao/rev_R4v_resolver2.py <e0> <qB> [h_c h_M]
Saida: resultados/revisao/rev_R4v_resolver2_e<e0>_q<qB>.txt
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4v_resolver as R                            # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    t0 = time.time()
    eB, qB = float(sys.argv[1]), float(sys.argv[2])
    hc = float(sys.argv[3]) if len(sys.argv) > 3 else 2e-3
    hM = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05
    DADOS = json.load(open(os.path.join(R.RAIZ, "resultados", "exp12_pares.json")))
    pj = [x for x in DADOS["pares"] if x["e0"] == eB and x["qB"] == qB][0]
    c2B = pj["c2B"]
    alvo = DADOS["alvo"]
    TRES = ("spin", "cm", "giroscopica")

    def obs(x):
        iota, c1, M = x
        m = R.mem(qB, c1, c2B, M, eB)
        v1 = R.B.valores_fisicos(m, iota, M, 1.0)
        D = v1["deslocamento"] / alvo["deslocamento"]
        v = R.B.valores_fisicos(m, iota, M, D)
        return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in TRES]), D

    def jac(x):
        J = np.zeros((3, 3))
        for j, hj in enumerate((1e-5, hc, hM)):
            xp, xm = np.array(x, float), np.array(x, float)
            xp[j] += hj
            xm[j] -= hj
            J[:, j] = (obs(xp)[0] - obs(xm)[0]) / (2 * hj)
        return J

    x_json = np.array([pj["iota"], pj["c1"], pj["M"]])
    partidas = [x_json, x_json + [0.0, 0.02, 0.0], x_json + [0.0, -0.02, 0.0], x_json + [0.01, 0.0, 0.3]]
    log("caso e0 = %.1f, q_B = %.1f, chi2_B = %+.1f ; least_squares trf com jacobiano central (h_chi1 %.0e, h_M %.2f) ; residuo json %.2e"
        % (eB, qB, c2B, hc, hM, pj["residuo"]))
    melhor = None
    for i, x0 in enumerate(partidas):
        r = least_squares(lambda x: obs(x)[0], x0, jac=jac, bounds=([0.05, -0.8, 35.0], [np.pi - 0.05, 0.8, 250.0]),
                          x_scale=[0.01, 0.01, 0.1], xtol=1e-10, ftol=1e-12, gtol=1e-12, max_nfev=25)
        rr, D = obs(r.x)
        m = float(np.max(np.abs(rr)))
        log("  partida %d (%+.3f, %+.4f, %.3f): max|r| %.3e r [%s] -> iota %.4f graus chi1 %+.5f M %.4f D %.2f (%d aval. de f, %s)"
            % (i, np.degrees(x0[0]), x0[1], x0[2], m, " ".join("%+.2e" % z for z in rr), np.degrees(r.x[0]), r.x[1], r.x[2], D,
               r.nfev, r.message[:40]))
        if melhor is None or m < melhor:
            melhor = m
        if m < 1.5e-5:
            break
    log("melhor max|r| = %.3e ; (%d avaliacoes do modelo, %.0f s)" % (melhor, len(R._mem), time.time() - t0))
    with open(os.path.join(R.RES, "rev_R4v_resolver2_e%.1f_q%.1f.txt" % (eB, qB)), "w") as f:
        f.write("\n".join(linhas) + "\n")
