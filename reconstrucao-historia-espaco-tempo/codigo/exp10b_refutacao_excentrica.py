"""Tentativa de refutacao do exp10, parte 3: busca com varios pontos de partida de uma binaria
excentrica (e0 = 0.1, 0.2 e 0.3 em 10 Hz, modelo PN newtoniano sem spins) com as mesmas quatro
memorias da binaria circular A. Se algum ponto de partida achar residuo < 1e-6, o resultado "sem spins,
as memorias separam excentrica de circular" cai. Registra tambem se eta para no limite fisico 1/4.
Saida: resultados/exp10b_refutacao_excentrica.txt
"""
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import pn_excentrico as PE                              # noqa: E402
from memorias import CalculadoraMemoria                 # noqa: E402
from exp10_excentricas import LISTA_PN, memorias_de_modos  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
F_FIS = 10.0
ETA0 = 1.2 / 2.2 ** 2
_c = {}
_calc = []


def fis(M, eta, e, iota, D):
    if not _calc:
        _calc.append(CalculadoraMemoria(LISTA_PN))
    k = (round(M, 9), round(eta, 12), e)
    if k not in _c:
        t, h, r, a, ee = PE.modos(eta, e, M * Dt.MSUN_S * F_FIS)
        _c[k] = memorias_de_modos(t, h, LISTA_PN, _calc[0], eta, com_pre=False)
    return B.valores_fisicos(_c[k], iota, M, D)


def _rodar(arg):
    eB, x0 = arg
    alvo = fis(65.0, ETA0, 0.0, np.radians(50.0), 400.0)

    def res(p):
        iota, eta, M = p
        v1 = fis(M, eta, eB, iota, 1.0)
        D = v1["deslocamento"] / alvo["deslocamento"]
        v = fis(M, eta, eB, iota, D)
        return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in ("spin", "cm", "giroscopica")])
    try:
        r = least_squares(res, x0, bounds=([0.05, 0.05, 30.0], [np.pi - 0.05, 0.25, 200.0]),
                          diff_step=1e-5, xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=200)
        return eB, float(np.max(np.abs(r.fun))), tuple(r.x)
    except Exception:
        return eB, None, None


if __name__ == "__main__":
    import multiprocessing as mp
    rng = np.random.default_rng(11)
    tarefas = [(eB, (rng.uniform(0.2, np.pi - 0.2), rng.uniform(0.08, 0.25), rng.uniform(35, 150)))
               for eB in (0.1, 0.2, 0.3) for _ in range(12)]
    with mp.get_context("spawn").Pool(4) as pool:
        saidas = pool.map(_rodar, tarefas)
    linhas = []
    for eB in (0.1, 0.2, 0.3):
        ok = sorted([(r, x) for e, r, x in saidas if e == eB and r is not None], key=lambda z: z[0])
        r, x = ok[0]
        s = ("e0 = %.1f: melhor residuo em %d partidas = %.2e (iota %.1f graus, eta %.4f%s, M %.2f); tres melhores: %s"
             % (eB, len(ok), r, np.degrees(x[0]), x[1], " = limite 1/4" if x[1] > 0.25 - 1e-6 else "", x[2],
                ", ".join("%.1e" % z[0] for z in ok[:3])))
        print(s, flush=True)
        linhas.append(s)
    with open(os.path.join(AQUI, "..", "resultados", "exp10b_refutacao_excentrica.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
