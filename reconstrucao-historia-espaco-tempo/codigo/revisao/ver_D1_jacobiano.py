"""Verificacao adversarial D1 (L01): jacobiano T0 independente de exp17_comum.memorias_varias.

Caminho independente: cada avaliacao chama observaveis.memorias_observaveis (uma onda por chamada, m = 0, nivel A,
deslocamento de janela), passos DIFERENTES dos do exp17 (q, chi: 1e-2 e 2e-3; ln M: 1e-3 e 2e-4; exp17 usou 4e-3 e
1e-4), dt = 0.25 e (no ponto A) dt = 0.125. Escala 'abs' do exp17: linhas / |F(iota = 50 graus)|.
Pontos: A (exp07), dois pontos fora da grade do exp17, um perto do locus q = 1, chi1 = chi2, e um extremo.
Tambem: suavidade em M (escada do item 1 da revisao) e vetor singular ESQUERDO da direcao quase nula intrinseca
(se a direcao fraca vem de spin ~ giro, ele deve ser ~ (0, a, 0, b) com a, b ~ +-1/sqrt2).
Saida: resultados/ver_D1_jacobiano.txt
"""
import os
import sys
import time

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
SAIDA = os.path.join(AQUI, "..", "..", "resultados", "ver_D1_jacobiano.txt")
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")
KD = np.array([1.0, 1.0, 1.0, 2.0])
D0 = 400.0


def F(p, iota, dt=0.25):
    import observaveis as O
    lnM, q, c1, c2 = p
    M = float(np.exp(lnM))
    m, a = O.memorias_observaveis(q, c1, c2, M, 10.0, dt=dt)
    v = O.valores_fisicos_completo(m, iota, 0.0, M, D0)
    vp = O.valores_fisicos_completo(m, iota + 1e-6, 0.0, M, D0)
    vm = O.valores_fisicos_completo(m, iota - 1e-6, 0.0, M, D0)
    v50 = O.valores_fisicos_completo(m, np.radians(50.0), 0.0, M, D0)
    f = np.array([v[k] for k in TIPOS])
    di = np.array([(vp[k] - vm[k]) / 2e-6 for k in TIPOS])
    f50 = np.array([v50[k] for k in TIPOS])
    return f, di, f50


def tarefa(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    nome, p0, iota, passos, dt = arg
    t0 = time.time()
    f0, di, f50 = F(p0, iota, dt)
    cols = {}
    for h in passos:
        J = np.zeros((4, 4))
        for k in range(4):
            hk = h[k]
            pp, pm = np.array(p0, float), np.array(p0, float)
            pp[k] += hk
            pm[k] -= hk
            J[:, k] = (F(pp, iota, dt)[0] - F(pm, iota, dt)[0]) / (2 * hk)
        cols[tuple(h)] = J
    return dict(nome=nome, p0=p0, iota=iota, dt=dt, f0=f0, di=di, f50=f50, J=cols, tempo=time.time() - t0)


def svd(J, s):
    Js = J * s[:, None]
    U, sv, Vt = np.linalg.svd(Js)
    return sv, U, Vt


if __name__ == "__main__":
    import multiprocessing as mp
    PASSOS = [(1e-3, 1e-2, 1e-2, 1e-2), (2e-4, 2e-3, 2e-3, 2e-3)]
    io50 = np.radians(50.0)
    pts = [("A", (np.log(65.0), 1.2, 0.3, -0.2), io50, PASSOS, 0.25),
           ("A_dt0.125", (np.log(65.0), 1.2, 0.3, -0.2), io50, PASSOS[1:], 0.125),
           ("fora1 q2.5 (-0.3,+0.5) M45", (np.log(45.0), 2.5, -0.3, 0.5), np.radians(35.0), PASSOS, 0.25),
           ("fora2 q7.5 (+0.75,-0.75) M100", (np.log(100.0), 7.5, 0.75, -0.75), np.radians(65.0), PASSOS, 0.25),
           ("perto q1 q1.05 (+0.2,+0.2) M65", (np.log(65.0), 1.05, 0.2, 0.2), io50, PASSOS, 0.25)]
    with mp.get_context("spawn").Pool(2) as pool:
        res = pool.map(tarefa, pts, chunksize=1)
    L = []

    def log(s=""):
        print(s, flush=True)
        L.append(s)

    log("Verificacao D1: jacobiano T0 por caminho independente (observaveis.memorias_observaveis, uma onda por avaliacao).")
    log("Colunas (ln M, q, chi1, chi2 | ln D, iota); escala abs = linhas / |F(iota=50)|. Passos (lnM, q, chi1, chi2).")
    for r in res:
        log("")
        log("== %s: p = %s, iota = %.1f graus, dt = %.3f (%.0f s)" % (r["nome"], np.round(r["p0"], 4), np.degrees(r["iota"]),
                                                                    r["dt"], r["tempo"]))
        s = 1 / np.abs(r["f50"])
        Js = list(r["J"].items())
        for h, J in Js:
            Jfull = np.column_stack([J, -KD * r["f0"], r["di"]])
            sv_l, _, _ = svd(Jfull, s)
            sv_i, U, Vt = svd(Jfull[:, [0, 1, 2, 3, 5]], s)
            sv_n, Un, Vtn = svd(J, s)
            log("  passos %s:" % (h,))
            log("    T0 livre      sigma = %s" % np.array2string(sv_l, precision=5))
            log("    T0 iota conh. sigma = %s" % np.array2string(sv_i, precision=5))
            log("    T0 intrinseco sigma = %s ; sigma4/sigma1 = %.3e" % (np.array2string(sv_n, precision=5), sv_n[-1] / sv_n[0]))
            log("      v (direita, menor sigma) em (lnM, q, chi1, chi2) = %s" % np.array2string(Vtn[-1] * np.sign(Vtn[-1][1]), precision=4))
            log("      u (esquerda, menor sigma) em (desl, spin, CM, giro) = %s" % np.array2string(Un[:, -1] * np.sign(Un[1, -1]), precision=4))
            Jr = J * s[:, None]
            a, b = Jr[1] / np.linalg.norm(Jr[1]), Jr[3] / np.linalg.norm(Jr[3])
            log("      angulo entre as linhas spin e giro (intrinseco, escala abs): %.3e rad" % np.arccos(min(1, abs(a @ b))))
        if len(Js) == 2:
            (h1, J1), (h2, J2) = Js
            E = (J1 - J2) * s[:, None]
            log("  |J(h1) - J(h2)|_F (intrinseco, escala abs) = %.2e (comparar com sigma4 intrinseco)" % np.linalg.norm(E))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
