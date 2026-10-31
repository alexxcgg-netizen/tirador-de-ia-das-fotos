"""Revisor R3: funcoes comuns (taxas instantaneas de memoria em blocos, decomposicao por pares de modos).

Nada aqui guarda formas de onda completas em caches: cada funcao recebe (t, h) e devolve so series m = 0.
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
CODIGO = os.path.join(AQUI, "..")
sys.path.insert(0, CODIGO)
import binarias as B                                           # noqa: E402
from memorias import CalculadoraMemoria, gram                  # noqa: E402
from harmonicos import Dfrak, ethb2_de_escalar                 # noqa: E402

SAIDA = os.path.join(CODIGO, "..", "resultados", "revisao")


def taxas_instantaneas(calc, H, Hd, lista_saida, bloco=2048):
    """hB(u), hEJ(u), dmem(u) (modos em (-2)Y_lm) calculados em blocos de tempo (economia de memoria)."""
    n = H.shape[0]
    hB = np.zeros((n, len(lista_saida)), dtype=complex)
    hEJ = np.zeros_like(hB)
    dmem = np.zeros_like(hB)
    for i in range(0, n, bloco):
        a, b, c = calc.partes_instantaneas(H[i:i + bloco], Hd[i:i + bloco], lista_saida)
        hB[i:i + bloco], hEJ[i:i + bloco], dmem[i:i + bloco] = a, b, c
    return hB, hEJ, dmem


def x_de_h22(t, h22):
    """x = (M omega_orb)^(2/3) a partir da frequencia do modo (2,2): omega_orb = -dphi22/dt / 2."""
    fase = np.unwrap(np.angle(h22))
    w = -np.gradient(fase, t)
    return np.abs(w / 2) ** (2 / 3)


def h30_pn_lo(x, eta):
    """|h_30| de ordem dominante (Blanchet LRR, H_30 = -(2/5) i sqrt(6/7) nu x^(5/2)): (16/5) sqrt(6 pi/35) nu^2 x^(7/2)."""
    return 16 / 5 * np.sqrt(6 * np.pi / 35) * eta ** 2 * x ** 3.5


def spin_por_pares(calc, B_, A_, lista, saida=(3, 0)):
    """Contribuicao de cada par nao ordenado de modos {(l,|m|) x (l',|m|)} para a memoria de spin (modo saida).

    A memoria de spin e linear em A (via A^dag - A); zera-se A fora dos blocos do par (incluindo os m < 0).
    """
    idx = {lm: k for k, lm in enumerate(lista)}
    grupos = {}
    for (l, m) in lista:
        grupos.setdefault((l, abs(m)), []).append(idx[(l, m)])
    chaves = sorted(grupos)
    out = {}
    for i, g1 in enumerate(chaves):
        for g2 in chaves[i:]:
            msk = np.zeros_like(A_, dtype=bool)
            for a in grupos[g1]:
                for b in grupos[g2]:
                    msk[a, b] = True
                    msk[b, a] = True
            Am = np.where(msk, A_, 0)
            v = calc.memorias_gram(B_, Am)["spin"][saida]
            if abs(v) > 0:
                out[(g1, g2)] = v
    return out
