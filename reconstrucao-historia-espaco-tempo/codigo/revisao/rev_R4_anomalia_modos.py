"""Revisor R4, tarefa 2 (diagnostico 2): qual modo carrega a dependencia em l0 perto da fusao?

B (e0 = 0.2, q = 2, chi1 = 0.0596, M = 72.59) do exp12, SEOBNRv5EHM, l0 = 0 e pi. Para cada modo (l, m > 0):
energia irradiada nos trechos t < -500 M, -500 M < t < -100 M, -100 M < t < 0, t > 0 (tempo do pico de |h22|),
e |h_lm| maximo. Saida: resultados/revisao/rev_R4_anomalia_modos.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402
import binarias as Bn                                   # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


q, c1, c2, M = 2.0, 0.05960457850002948, 0.0, 72.5875185658003
f0 = M * C.Dt.MSUN_S * C.F_FIS
MODOS = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)]
TRECHOS = [(-1e9, -500.0), (-500.0, -100.0), (-100.0, 0.0), (0.0, 1e9)]


def por_modo(e0, l0):
    t, h = C.gerar(q, c1, c2, f0, e0, l0)
    dt = t[1] - t[0]
    tp = t[np.argmax(np.abs(h[(2, 2)]))]
    s = t - tp
    out = {}
    for k in MODOS:
        hd = Bn.derivada4(h[k][:, None], dt)[:, 0]
        dE = 2 * np.abs(hd) ** 2 / (16 * np.pi)          # m e -m
        out[k] = ([np.sum(dE[(s > a) & (s <= b)]) * dt for a, b in TRECHOS], np.max(np.abs(h[k])),
                  s[np.argmax(np.abs(h[k]))])
    return out


if __name__ == "__main__":
    log("Energia por modo e trecho (tempo antes do pico de |h22|), B (e0 = 0.2, q = 2), l0 = pi relativo a l0 = 0")
    r0 = por_modo(0.2, 0.0)
    r1 = por_modo(0.2, np.pi)
    rc = por_modo(0.0, 0.0)
    for k in MODOS:
        e0v, a0, tp0 = r0[k]
        e1v, a1, tp1 = r1[k]
        ecv, ac, tpc = rc[k]
        log("  (%d,%d): E(l0=0) por trecho %s ; l0=pi/l0=0 - 1: %s ; |h| max %+.1e (t_pico %+.1f -> %+.1f M) ; circular/l0=0 - 1: %s"
            % (k[0], k[1], " ".join("%.3e" % x for x in e0v), " ".join("%+.1e" % (b / a - 1) for a, b in zip(e0v, e1v)),
               a1 / a0 - 1, tp0, tp1, " ".join("%+.1e" % (b / a - 1) for a, b in zip(e0v, ecv))))
    tot0 = np.sum([r0[k][0] for k in MODOS], axis=0)
    tot1 = np.sum([r1[k][0] for k in MODOS], axis=0)
    log("  total: E(l0=0) %s ; l0=pi/l0=0 - 1: %s" % (" ".join("%.3e" % x for x in tot0), " ".join("%+.1e" % (b / a - 1) for a, b in zip(tot0, tot1))))
    with open(os.path.join(C.RES, "rev_R4_anomalia_modos.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
