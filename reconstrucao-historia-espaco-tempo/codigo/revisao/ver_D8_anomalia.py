"""Verificacao D8 (L16, exp40_anomalia): dependencia de desl20, E_rad e M_f na anomalia l0 (SEOBNRv5EHM),
com quadratura propria: derivada de 2a ordem (np.gradient), integrais de Gaunt calculadas aqui por quadratura
de Gauss-Legendre x trapezio em phi (sYlm conferido contra a formula fechada de -2Y22), sem o (2,0) newtoniano,
janela desde o inicio da onda e, como variante, desde t = -3000 M e -100 M. 16 valores de l0 (o exp40 usou 12).
Sistema A do exp12 (q = 1.2, chi = (0.3, -0.2), M = 65), e0 = 0.05, 0.1, 0.2; e o B (q = 2) em e0 = 0.2.
"""
import os
import sys
import time
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
RES = os.path.join(AQUI, "..", "..", "resultados")
SIS = {"A": (1.2, 0.3, -0.2, 65.0), "B": (2.0, 0.0596, 0.0, 72.5875)}
L0S = tuple(2 * np.pi * k / 16 for k in range(16))
MODOS = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3)]
LISTA = []
for (_l, _m) in MODOS:
    LISTA += [(_l, _m), (_l, -_m)]


def gaunt20():
    from harmonicos import sYlm
    x, wx = np.polynomial.legendre.leggauss(40)
    th = np.arccos(x)
    ph = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    W = wx[:, None] * (2 * np.pi / len(ph)) * np.ones_like(PH)
    # confere sYlm
    y22 = np.vectorize(lambda a, b: complex(sYlm(-2, 2, 2, a, b)))(TH[::7, ::9], PH[::7, ::9])
    ref = 0.125 * np.sqrt(5 / np.pi) * (1 + np.cos(TH[::7, ::9])) ** 2 * np.exp(2j * PH[::7, ::9])
    assert np.max(np.abs(y22 - ref)) < 1e-12, np.max(np.abs(y22 - ref))
    Y = np.array([np.vectorize(lambda a, b, l=l, m=m: complex(sYlm(-2, l, m, a, b)))(TH, PH) for (l, m) in LISTA])
    Y20 = np.vectorize(lambda a, b: complex(sYlm(0, 2, 0, a, b)))(TH, PH)
    G = np.einsum("jab,kab,ab->jk", Y, Y.conj(), Y20.conj() * W)
    return G


def ponto(arg):
    nome, e0, l0, G = arg
    import exp40_comum as C
    q, c1, c2, M = SIS[nome]
    t, h, dyn, nu, tsh = C.gerar(q, c1, c2, M, e0, l0)
    H = np.stack([h[k] for k in LISTA], axis=1)
    dt = t[1] - t[0]
    Hd = np.gradient(H, dt, axis=0)
    out = {}
    for rot, t0 in (("ini", t[0]), ("m3000", -3000.0), ("m100", -100.0)):
        s = t >= t0
        w = np.full(s.sum(), dt); w[0] *= 0.5; w[-1] *= 0.5
        Bm = (Hd[s] * w[:, None]).T @ Hd[s].conj()
        E20 = np.real(np.sum(Bm * G))                           # int (|hdot|^2)_20 du
        desl20 = 0.5 * np.sqrt(24) * 0.25 * E20 / 3.0           # (1/2) ethb2 Dfrak^-1 (1/4) int ...
        Erad = float(np.real(np.trace(Bm))) / (16 * np.pi)
        out[rot] = (desl20, Erad)
    Elig = 1.0 - nu * float(np.interp(t[0] + tsh, dyn[:, 0], dyn[:, 8]))
    out["Mf"] = 1.0 - out["ini"][1] - Elig
    del t, h, H, Hd, dyn
    return (nome, e0, l0), out


def harm(y):
    Y = np.fft.rfft(y) / len(y)
    return 2 * abs(Y[1]) / abs(Y[0].real), 2 * abs(Y[2]) / abs(Y[0].real)


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    G = gaunt20()
    tarefas = [("A", e0, l0, G) for e0 in (0.05, 0.1, 0.2) for l0 in L0S] + [("B", 0.2, l0, G) for l0 in L0S]
    with mp.get_context("spawn").Pool(2) as pool:
        res = dict(pool.map(ponto, tarefas, chunksize=4))
    linhas = []
    for nome, e0 in [("A", 0.05), ("A", 0.1), ("A", 0.2), ("B", 0.2)]:
        p = [res[(nome, e0, l0)] for l0 in L0S]
        y = np.array([x["ini"][0] for x in p]); E = np.array([x["ini"][1] for x in p]); Mf = np.array([x["Mf"] for x in p])
        y3 = np.array([x["m3000"][0] for x in p]); y1 = np.array([x["m100"][0] for x in p])
        a1, a2 = harm(y)
        # 12 pontos (subconjunto l0 = 2 pi k/12 nao coincide; usa 8 pontos pares como subamostragem)
        a1_8, _ = harm(y[::2])
        linhas.append("%s e0 %.2f: desl20 media %.5e a1 %.2e (a1/e0 %.3f) a2/a1 %.2f [8 pontos: a1 %.2e] ; E_rad a1 %.2e ;"
                      " M_f a1 %.2e ; var desde -3000 M / total %.3f ; ultimos 100 M / total %.3f (corr %.3f)"
                      % (nome, e0, y.mean(), a1, a1 / e0, a2 / a1, a1_8, harm(E)[0], harm(Mf)[0],
                         np.std(y3) / np.std(y), np.std(y1) / np.std(y), np.corrcoef(y1, y)[0, 1]))
    a = [harm(np.array([res[("A", e0, l0)]["ini"][0] for l0 in L0S]))[0] for e0 in (0.05, 0.1, 0.2)]
    linhas.append("expoente de a1(desl20) em e0 (A, 0.05-0.2): %.3f" % np.polyfit(np.log([0.05, 0.1, 0.2]), np.log(a), 1)[0])
    linhas.append("(%.0f s)" % (time.time() - t0))
    print("\n".join(linhas))
    open(os.path.join(RES, "ver_D8_anomalia.txt"), "w").write("\n".join(linhas) + "\n")
