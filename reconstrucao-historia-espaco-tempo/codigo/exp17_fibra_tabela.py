"""Experimento 17 (L02): tabela de multipolos de memoria para o mapa global da fibra de A.

Para cada (q_B, chi2_B) da grade q_B = 1.0, 1.25, ..., 4.0 e chi2_B = -0.8, -0.6, ..., 0.8, tabela os multipolos de
janela (nivel A, desl='janela', todos os m com l <= 8, referencial do pico, borda inicial suprimida) em
  chi1: 13 nos de Chebyshev em [-0.8, 0.8] (interpolacao baricentrica);
  M   : 40 valores log-espacados em [45, 130] M_sol (todos da mesma onda; spline cubica em ln M).
Por que M em [45, 130] e nao [35, 250]: a razao r = CM/(M desl) no observador (exp17_interpretacao.txt, item 6) fica
em [-0.62, -0.18] na grade de jacobianos (q <= 5, |chi| <= 0.6; [-0.62, -0.35] para q <= 3), e a equacao do CM da
M_B = M_A r_A / r_B, com r_A = -0.53: M_B >= 56 sempre; M_B > 130 exigiria r_B > -0.265, o que so ocorre para q >~ 4
com spins grandes. A busca (exp17_fibra.py) marca minimos na borda M = 130 para conferir se a faixa basta.
A tabela fica no diretorio de rascunho passado em argv[2] (nao e resultado; ~2 MB por ponto).
Uso: python exp17_fibra_tabela.py i0:i1 DIRETORIO
"""
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

QB = tuple(np.round(np.arange(1.0, 4.0001, 0.25), 2))
C2B = tuple(np.round(np.arange(-0.8, 0.8001, 0.2), 2))
NCHI = 13
CHI1 = tuple(0.8 * np.cos(np.pi * (np.arange(NCHI) + 0.5) / NCHI)[::-1])
MNOS = tuple(np.exp(np.linspace(np.log(45.0), np.log(130.0), 40)))


def chaves():
    import exp17_comum as C
    r = C.memorias_varias(1.2, 0.3, -0.2, [120.0])[0]
    return {t: sorted(r["mem_pico"][t]) for t in C.TIPOS}


def ponto(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    qB, c2B, K, pasta = arg
    nome = os.path.join(pasta, "tab_%.2f_%+.2f.npz" % (qB, c2B))
    if os.path.exists(nome):
        return nome
    import exp17_comum as C
    t0 = time.time()
    X = np.zeros((NCHI, len(MNOS), sum(len(K[t]) for t in C.TIPOS)), dtype=complex)
    aux = np.zeros((NCHI, len(MNOS), 4))
    for i, c1 in enumerate(CHI1):
        res = C.memorias_varias(qB, c1, c2B, list(MNOS))
        for j, r in enumerate(res):
            X[i, j] = np.concatenate([np.array([r["mem_pico"][t][k] for k in K[t]]) for t in C.TIPOS])
            aux[i, j] = [r["aux"]["M_f"], r["aux"]["E_janela"], r["aux"]["E_lig"], r["aux"]["Phi_pico"]]
    np.savez(nome, X=X, aux=aux, chi1=np.array(CHI1), M=np.array(MNOS), qB=qB, c2B=c2B)
    print("tabela q_B=%.2f chi2_B=%+.2f: %.0f s" % (qB, c2B, time.time() - t0), flush=True)
    return nome


if __name__ == "__main__":
    import multiprocessing as mp
    pasta = sys.argv[2]
    os.makedirs(pasta, exist_ok=True)
    K = chaves()
    np.savez(os.path.join(pasta, "chaves.npz"), **{t: np.array(K[t]) for t in K})
    pts = [(q, c, K, pasta) for q in QB for c in C2B]
    i0, i1 = map(int, sys.argv[1].split(":"))
    t0 = time.time()
    with mp.get_context("spawn").Pool(2) as pool:
        pool.map(ponto, pts[i0:i1], chunksize=1)
    print("total %.0f s" % (time.time() - t0))
