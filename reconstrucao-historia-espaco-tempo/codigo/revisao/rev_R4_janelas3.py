"""Revisor R4, tarefa 4 (continuacao 2): valores singulares precisos e perfil em q_B por continuacao.

a) Valores singulares do jacobiano 8 x 6 em A (como em rev_R4_janelas2, impressos com 3 algarismos) e, para
   comparar, os da diferenca entre janelas (memoria acumulada entre 10 e 20 Hz).
b) Perfil do menor residuo das 8 equacoes (10 + 20 Hz) com q_B fixo, por continuacao: cada q_B parte da
   solucao do q_B vizinho (e da solucao do exp07 quando existe). Os valores sao limites superiores do minimo.
Saida: resultados/revisao/rev_R4_janelas3.txt
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_janelas as W                              # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    t0 = time.time()
    A = W.A
    alvos = {f: W.quatro(A, f) for f in (10.0, 20.0)}
    nomes = ["q", "c1", "c2", "M", "iota", "D"]
    passo = dict(q=1e-3, c1=1e-3, c2=1e-3, M=1e-2, iota=1e-4, D=1e-2)
    esc = np.array([0.1, 0.1, 0.1, 1.0, 0.01, 0.01 * A["D"]])
    J = np.zeros((8, 6))
    for j, n in enumerate(nomes):
        rp = W.residuos(dict(A, **{n: A[n] + passo[n]}), alvos, (10.0, 20.0))
        rm = W.residuos(dict(A, **{n: A[n] - passo[n]}), alvos, (10.0, 20.0))
        J[:, j] = (rp - rm) / (2 * passo[n])
    Js = J * esc
    log("a) valores singulares (colunas escaladas por 0.1, 0.1, 0.1, 1 M_sol, 0.01 rad, 0.01 D):")
    log("   10 Hz (4 x 6): " + " ".join("%.2e" % x for x in np.linalg.svd(Js[:4], compute_uv=False)))
    log("   20 Hz (4 x 6): " + " ".join("%.2e" % x for x in np.linalg.svd(Js[4:], compute_uv=False)))
    _, s8, Vt = np.linalg.svd(Js)
    log("   10 + 20 Hz (8 x 6): " + " ".join("%.2e" % x for x in s8))
    log("   direcao mais fraca (q, chi1, chi2, M, iota, D) em unidades da escala: " + " ".join("%+.3f" % x for x in Vt[-1]))
    v = Vt[-1] * esc
    def chieff(q, c1, c2):
        return (q * c1 + c2) / (1 + q)

    def eta(q):
        return q / (1 + q) ** 2

    e6 = 1e-6
    dce = (chieff(A["q"] + e6 * v[0], A["c1"] + e6 * v[1], A["c2"] + e6 * v[2]) - chieff(A["q"], A["c1"], A["c2"])) / e6
    det = (eta(A["q"] + e6 * v[0]) - eta(A["q"])) / e6
    log("   nessa direcao, por unidade: dq %+.3f, d chi_eff %+.4f, d eta %+.4f, dM %+.3f M_sol" % (v[0], dce, det, v[3]))
    W._cache.clear()
    log()
    log("b) perfil por continuacao em q_B (8 equacoes, 5 livres)")
    sol = {}
    base = dict(A)
    ordem = [1.3, 1.5, 1.75, 2.0, 2.5, 3.0, 1.1, 1.0]
    for qB in ordem:
        vizinhos = [sol[k] for k in sol if abs(k - qB) <= 0.51]
        vizinhos = sorted(vizinhos, key=lambda p: abs(p["q"] - qB))[:2] or [base]
        partidas = [dict(p, q=qB) for p in vizinhos]
        if (qB, 0.0) in W.P:
            partidas.append(W.P[(qB, 0.0)])
        melhor = None
        for x0 in partidas:
            par, r = W.resolver(x0, ["c1", "c2", "M", "iota", "D"], dict(q=qB), alvos, (10.0, 20.0), max_nfev=80)
            m = float(np.max(np.abs(r.fun)))
            if melhor is None or m < melhor[0]:
                melhor = (m, par, r)
            W._cache.clear()
        m, par, r = melhor
        sol[qB] = par
        log("  q_B = %.2f: max|res| = %.2e (%d partidas) -> %s ; chi_eff %+.4f" % (
            qB, m, len(partidas), W.fmt(par), (par["q"] * par["c1"] + par["c2"]) / (1 + par["q"])))
        log("      residuos 10 Hz: %s | 20 Hz: %s" % (" ".join("%+.1e" % x for x in r.fun[:4]), " ".join("%+.1e" % x for x in r.fun[4:])))
    log("  (A: chi_eff %+.4f)" % ((A["q"] * A["c1"] + A["c2"]) / (1 + A["q"])))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(W.RES, "rev_R4_janelas3.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
