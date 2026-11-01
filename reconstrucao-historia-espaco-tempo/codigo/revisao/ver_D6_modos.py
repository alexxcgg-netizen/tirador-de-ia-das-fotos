"""Verificacao adversarial D6 (L10, validacao): por quadratura direta no ceu (lal.SpinWeightedSphericalHarmonic,
sem memorias.py), a memoria nula m = 0 (l = 2, 4) de ondas NRSur7dq4 com spins alinhados, com e sem os modos
(3, +-1), (4, +-1), (4, +-2) (ausentes no nivel A do CCE e de binarias.MODOS_OSC).

dot a_l0 ~ C_l int dOmega |hdot|^2 Y_l0 : a razao entre dois conjuntos de modos no mesmo l nao depende de C_l.
Janela: f_22 (pela fase do proprio h22) >= 0.007 ate o fim. Derivadas por spline cubico.
Tambem: valor final do modo inercial (2,0) do NRSur7dq4 (alinhado: = coorbital) contra a memoria esperada.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import lal
from scipy.interpolate import CubicSpline
import gwsurrogate

sur = gwsurrogate.LoadSurrogate("NRSur7dq4")
F0 = 0.007
MODOS = [(l, m) for l in range(2, 5) for m in range(-l, l + 1) if m != 0]
FALTAM = {(3, 1), (3, -1), (4, 1), (4, -1), (4, 2), (4, -2)}

# grade de Gauss-Legendre
NT, NP = 24, 48
xg, wg = np.polynomial.legendre.leggauss(NT)
TH = np.arccos(xg)
PH = np.arange(NP) * 2 * np.pi / NP
W = np.outer(wg, np.full(NP, 2 * np.pi / NP))


def Y(s, l, m):
    return np.array([[lal.SpinWeightedSphericalHarmonic(t, p, s, l, m) for p in PH] for t in TH])


Ym2 = {k: Y(-2, *k) for k in MODOS}
from scipy.special import sph_harm_y
Y0 = {l: sph_harm_y(l, 0, TH[:, None], PH[None, :]) for l in (2, 3, 4)}

for (q, cA, cB) in [(1.0, 0.0, 0.0), (1.2, 0.3, -0.2), (2.0, -0.5, 0.5), (3.0, 0.5, 0.3), (3.9, 0.0, 0.0)]:
    dt = 0.25
    t = np.arange(-4000, 100, dt)
    tt, h, _ = sur(q, [0, 0, cA], [0, 0, cB], times=t, f_low=0, f_ref=0)
    fase = np.unwrap(np.angle(h[(2, 2)]))
    f22 = -CubicSpline(tt, fase).derivative()(tt) / (2 * np.pi)
    i0 = int(np.nonzero((f22 >= F0) & (tt < 0))[0][0])
    sel = slice(i0, len(tt))
    hd = {k: CubicSpline(tt, h[k]).derivative()(tt)[sel] for k in MODOS}
    res = {}
    for nome, conj in (("todos m!=0", MODOS), ("sem (3,1),(4,1),(4,2)", [k for k in MODOS if k not in FALTAM])):
        acc = {l: 0.0 for l in (2, 3, 4)}
        # fluxo no ceu, por blocos de tempo
        nT = len(tt[sel])
        for a in range(0, nT, 2000):
            b = min(nT, a + 2000)
            campo = sum(hd[k][a:b, None, None] * Ym2[k][None] for k in conj)
            Fl = np.abs(campo) ** 2
            wt = np.full(b - a, dt)
            if a == 0:
                wt[0] *= 0.5
            if b == nT:
                wt[-1] *= 0.5
            for l in (2, 3, 4):
                acc[l] += np.sum(wt * np.einsum("tij,ij->t", Fl, W * Y0[l].real))
        res[nome] = acc
    A, B = res["todos m!=0"], res["sem (3,1),(4,1),(4,2)"]
    h20f = h[(2, 0)][-1]
    print("q %.1f chi (%+.1f, %+.1f): t_i %.1f ; razao (todos - sem)/sem: l=2 %+.2e, l=4 %+.2e ; (l=3 %.1e de l=2) ;"
          " |h20(t_fim)| %.2e, max|h20| %.2e" % (q, cA, cB, tt[i0], (A[2] - B[2]) / B[2], (A[4] - B[4]) / B[4],
                                                abs(A[3] / A[2]), abs(h20f), np.max(np.abs(h[(2, 0)]))))
    del h, hd
