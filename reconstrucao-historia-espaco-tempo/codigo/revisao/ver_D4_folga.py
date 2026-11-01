"""Verificacao adversarial D4 (L12): razao r = |D Dh_nula|/E_janela de exp28_folga por caminho independente.

Usa so a geracao e a matriz de Gram da janela de observaveis (B = int hdot hdot^dag com os pesos da janela); a memoria
no observador e calculada pela INTEGRAL DE THORNE direta numa grade fina (nucleo K = (n'.mbar)^2/(1 - n'.N), limitado,
|K| <= 1), sem memorias.py. Harmonicos da fluencia por harmonicos.sYlm (so para F; a projecao em modos nao e usada).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import observaveis as O                               # noqa: E402
import binarias as B                                  # noqa: E402
from harmonicos import sYlm                           # noqa: E402

nth, nph = 400, 400
x, wx = np.polynomial.legendre.leggauss(nth)
th = np.arccos(x)
ph = 2 * np.pi * (np.arange(nph) + 0.5) / nph
TH, PH = np.meshgrid(th, ph, indexing="ij")
W = wx[:, None] * np.full(nph, 2 * np.pi / nph)[None, :]
n = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)], -1)

for (q, c1, c2, r_d4, e2_d4) in ((1.0, 0.0, 0.0, 0.77327, 0.9888), (4.0, 0.0, 0.0, 0.67404, 0.8816),
                                  (1.2, 0.3, -0.2, 0.77688, 0.9839)):
    t, h, ti = O.gerar_janela(q, c1, c2, 65.0, 10.0)
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    Hd = O.derivada(H, t[1] - t[0])
    w = O.pesos_janela(t, ti)
    Bm, _ = O.gram_pesos(H, Hd, w)
    del H, Hd, t, h
    E = np.real(np.trace(Bm)) / (16 * np.pi)
    e2 = sum(np.real(Bm[k, k]) for k, (l, m) in enumerate(Losc) if l == 2) / np.real(np.trace(Bm))
    Yg = np.array([sYlm(-2, l, m, TH, PH) for (l, m) in Losc])
    F = np.real(np.einsum("jk,jab,kab->ab", Bm, Yg, Yg.conj(), optimize=True)) / (16 * np.pi)
    del Yg
    print("q=%.1f chi=(%.1f,%.1f): E_janela (tr B/16pi) = %.6f ; int F = %.6f ; e2 = %.4f (D4 %.4f)" % (
        q, c1, c2, E, np.sum(W * F), e2, e2_d4))
    io = np.pi / 2
    best = 0
    for p0 in 2 * np.pi * np.arange(48) / 48:
        N = np.array([np.sin(io) * np.cos(p0), np.sin(io) * np.sin(p0), np.cos(io)])
        eth = np.array([np.cos(io) * np.cos(p0), np.cos(io) * np.sin(p0), -np.sin(io)])
        eph = np.array([-np.sin(p0), np.cos(p0), 0.0])
        mbar = (eth - 1j * eph) / np.sqrt(2)
        den = 1 - n @ N
        K = np.where(den > 1e-14, (n @ mbar) ** 2 / np.maximum(den, 1e-14), 0.0)
        z = 4 * np.sum(W * F * K)
        best = max(best, abs(z))
    print("   iota = 90: r = max_phi |D Dh|/E = %.5f (D4 %.5f; dif rel %.1e) ; r/c(e2) e r/4 = %.4f, %.4f" % (
        best / E, r_d4, abs(best / E - r_d4) / r_d4, best / E / 1.0, best / E / 4))
