"""Revisor R4, tarefa 4 (continuacao): perfil do residuo de duas janelas e jacobiano 8 x 6 em A.

a) Jacobiano das memorias relativas (4 com janela de 10 Hz; 8 com 10 + 20 Hz) em relacao a
   (q, chi1, chi2, M, iota, D) no ponto A, diferencas centrais; valores singulares com as colunas na escala
   (0.1, 0.1, 0.1, 1 M_sol, 0.01 rad, 1% de D). Posto 4 (uma janela) => familia de dimensao 2; posto 6 (duas)
   => A isolado localmente; o menor valor singular mede a direcao mais fraca.
b) Perfil: para q_B fixo em 1.1, 1.3, 2.0, 3.0, 4 partidas (a solucao de uma janela do exp07 quando existe e
   3 aleatorias) com 5 livres; menor residuo max|r| das 8 equacoes.
Saida: resultados/revisao/rev_R4_janelas2.txt
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
    s4 = np.linalg.svd(Js[:4], compute_uv=False)
    U, s8, Vt = np.linalg.svd(Js)
    log("a) jacobiano em A (colunas escaladas por 0.1, 0.1, 0.1, 1 M_sol, 0.01 rad, 0.01 D)")
    log("   uma janela (4 x 6): valores singulares %s" % np.array2string(s4, precision=3))
    log("   duas janelas (8 x 6): valores singulares %s" % np.array2string(s8, precision=3))
    log("   direcao mais fraca (em unidades da escala) (q, chi1, chi2, M, iota, D): %s" % np.array2string(Vt[-1], precision=3))
    log("   segunda mais fraca: %s" % np.array2string(Vt[-2], precision=3))
    # residuo linear previsto ao andar dq = -0.2 (q 1.2 -> 1.0) ao longo da direcao mais fraca
    v = Vt[-1] / abs(Vt[-1][0]) * 0.2 / 0.1
    log("   previsao linear: andar ate |dq| = 0.2 na direcao mais fraca da residuo de norma %.2e" % (s8[-1] * np.linalg.norm(v)))
    W._cache.clear()
    log()
    log("b) perfil em q_B (8 equacoes, 5 livres, 4 partidas)")
    rng = np.random.default_rng(11)
    for qB in (1.1, 1.3, 2.0, 3.0):
        partidas = []
        if (qB, 0.0) in W.P:
            partidas.append(W.P[(qB, 0.0)])
        while len(partidas) < 4:
            partidas.append(dict(q=qB, c1=rng.uniform(-0.6, 0.7), c2=rng.uniform(-0.6, 0.6), M=rng.uniform(62, 76),
                                 iota=np.radians(rng.uniform(40, 62)), D=rng.uniform(370, 420)))
        melhor = None
        todos = []
        for x0 in partidas:
            par, r = W.resolver(x0, ["c1", "c2", "M", "iota", "D"], dict(q=qB), alvos, (10.0, 20.0))
            m = float(np.max(np.abs(r.fun)))
            todos.append(m)
            if melhor is None or m < melhor[0]:
                melhor = (m, par, r)
            W._cache.clear()
        m, par, r = melhor
        log("  q_B = %.1f: melhor max|res| = %.2e (todas: %s) -> %s" % (qB, m, " ".join("%.1e" % x for x in todos), W.fmt(par)))
        log("      residuos 10 Hz: %s | 20 Hz: %s" % (" ".join("%+.1e" % x for x in r.fun[:4]), " ".join("%+.1e" % x for x in r.fun[4:])))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(W.RES, "rev_R4_janelas2.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
