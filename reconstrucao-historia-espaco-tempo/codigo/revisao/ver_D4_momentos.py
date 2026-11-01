"""Verificacao adversarial D4 (L14): a vantagem das janelas de energia igual e das JANELAS ou da VARIAVEL adaptada?

Hipotese rival: no modelo 2 de exp36 (ruido branco comum na serie F) a informacao retida depende so do espaco das
linhas. Momentos em tau = t/T geram polinomios em t (nao resolvem a fusao); janelas de energia igual geram constantes
por partes com cortes concentrados na fusao. Teste: "momentos adaptados" mu_n = int c(t)^n F dt, com c(t) a fracao
acumulada nominal da memoria (a mesma informacao usada para escolher os cortes de energia igual). Espaco das linhas:
polinomios em c(t). Se reterem tanto quanto as janelas de energia igual, a conclusao de H14.2 e sobre a variavel
(adaptacao), nao sobre janelas x momentos. Tambem: condicionamento dos momentos adaptados (monomios e Legendre em c).
Copia o necessario de exp36 (sem executar aquele script, que regravaria os resultados).
"""
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import observaveis as O                               # noqa: E402
import binarias as B                                  # noqa: E402
from deteccao import MSUN_S, MPC_S                    # noqa: E402
from harmonicos import Grade, Dfrak, ethb2_de_escalar  # noqa: E402

P0 = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2)
D_MPC = 400.0
TA, TB, FS = -4.0, 0.04, 4096.0
tg = np.arange(TA, TB + 0.5 / FS, 1 / FS)
N = len(tg)
wq = np.full(N, 1 / FS)
wq[0] = wq[-1] = 0.5 / FS
Losc = B.lista_osc()
gg = Grade(30, 60)
Y = np.array([gg.Y(-2, l, m).ravel() for (l, m) in Losc])
Y20 = gg.Y(0, 2, 0).ravel()
G = (Y * (gg.peso.ravel() * np.conj(Y20))) @ Y.conj().T
C = 0.5 * ethb2_de_escalar(2) * 0.25 * G / Dfrak(2)


def fluxo(M, q, c1, c2):
    t, h, ti = O.gerar_janela(q, c1, c2, M, 10.0)
    H = np.stack([h[k] for k in Losc], axis=1)
    Hd = O.derivada(H, t[1] - t[0])
    rate = np.real(np.einsum("ta,ab,tb->t", Hd, C, Hd.conj()))
    Ms, Ds = M * MSUN_S, D_MPC * MPC_S
    sp = CubicSpline(t * Ms, rate * (M * MSUN_S / Ds) / Ms)
    del t, h, H, Hd
    return sp


sp0 = fluxo(**{"M": P0["M"], "q": P0["q"], "c1": P0["c1"], "c2": P0["c2"]})
F0 = sp0(tg)
cum = np.concatenate([[0], np.cumsum(0.5 * (F0[1:] + F0[:-1]) / FS)])
cfr = cum / cum[-1]                                     # fracao acumulada nominal c(t) em [0, 1]

h = 1e-3
d = np.zeros((6, N))
d[0] = F0
for j, campo in enumerate(["M", "q", "c1", "c2"], 1):
    pp, pm = dict(P0), dict(P0)
    if campo == "M":
        pp["M"] *= np.exp(h); pm["M"] *= np.exp(-h)
    else:
        pp[campo] += h; pm[campo] -= h
    d[j] = (fluxo(**pp)(tg) - fluxo(**pm)(tg)) / (2 * h)
d[5] = -sp0.derivative()(tg)
NOMES = ["lnA", "lnM", "q", "chi1", "chi2", "t0"]


def cr(J):
    Q, R = np.linalg.qr(J)
    Ri = np.linalg.inv(R)
    return np.sqrt(np.sum(Ri ** 2, axis=1))


Jw = d.T * np.sqrt(wq)[:, None]
sfull = cr(Jw)


def retida(Lrows):
    """Lrows: K x N funcoes de linha (sem peso); devolve sigma_full / sigma_K."""
    Lb = Lrows * np.sqrt(wq)
    Q, _ = np.linalg.qr(Lb.T)
    return sfull / cr(Q.T @ Jw)


def base_leg(var, K):
    x = 2 * (var - var.min()) / (var.max() - var.min()) - 1
    return np.array([np.polynomial.legendre.Legendre.basis(k)(x) for k in range(K)])


def janelas_energia(K):
    s = [TA] + [tg[np.searchsorted(cfr, k / K)] for k in range(1, K)]
    return np.array([(tg >= sk).astype(float) for sk in s])


def cond(Lrows):
    A = Lrows * np.sqrt(wq)
    A = A / np.linalg.norm(A, axis=1, keepdims=True)
    sv = np.linalg.svd(A, compute_uv=False)
    return sv[0] / sv[-1]


tau = tg / (TB - TA)
print("modelo 2 (ruido branco comum em F): fracao retida sigma_serie/sigma_K para (lnA, lnM, q, chi1, chi2, t0)")
print("  K | funcional                      | " + " | ".join("%7s" % n for n in NOMES) + " | cond (monomios)")
for K in (6, 12, 32, 64):
    linhas = [("momentos em t (exp36)", base_leg(tau, K), np.array([tau ** n for n in range(K)])),
              ("janelas energia igual (exp36)", janelas_energia(K), janelas_energia(K)),
              ("momentos na fracao c(t)", base_leg(cfr, K), np.array([cfr ** n for n in range(K)])),
              ("momentos em ln(t_c - t)", base_leg(np.log(0.06 - tg), K),
               np.array([((np.log(0.06 - tg) - np.log(0.06 - tg).min()) / np.ptp(np.log(0.06 - tg))) ** n
                         for n in range(K)]))]
    for nome, Lb, Lmon in linhas:
        r = retida(Lb)
        print("  %2d | %-30s | " % (K, nome) + " | ".join("%7.2e" % v for v in r) + " | %.1e" % cond(Lmon))

# sensibilidade ao inicio da janela dos momentos adaptados (fracao c(t) definida com a janela original)
print()
mask = tg >= -3.0
for nome, var in (("momentos em t (origem na fusao)", tau), ("momentos na fracao c(t)", cfr)):
    Lm = np.array([var ** n for n in range(10)]) * wq
    m4, m3 = Lm @ F0, (Lm * mask) @ F0
    print("  inicio -4 s -> -3 s, %s: variacao relativa n=0..9: %s" % (
        nome, " ".join("%.1e" % v for v in np.abs(m3 - m4) / np.abs(m4))))
# com origem no inicio para a variavel c: (1 - c)^n concentra peso na fusao? (momentos "da fusao para tras")
Lm = np.array([(1 - cfr) ** n for n in range(10)]) * wq
m4, m3 = Lm @ F0, (Lm * mask) @ F0
print("  inicio -4 s -> -3 s, momentos em (1 - c(t)): %s" % " ".join("%.1e" % v for v in np.abs(m3 - m4) / np.abs(m4)))
