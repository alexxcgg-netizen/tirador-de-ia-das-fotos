"""Verificacao adversarial D3 (L05-L07): pipeline INDEPENDENTE do exp24_comum.

Diferencas deliberadas em relacao ao exp24_comum:
  - serie da memoria nula vem de observaveis.serie_memoria (quadratura de memorias.partes_instantaneas, nao os
    tensores esparsos do exp24);
  - espectro por FFT de uma serie reamostrada no tempo FISICO (fs fixo), com t = 0 no pico do (2,2), valor final
    mantido T_HOLD s e levado a zero por rampa de cosseno de T_RAMPA s (metodo do L00), em vez do espectro exato do
    degrau mantido;
  - derivada em ln M por DIFERENCA FINITA FISICA (regenera a onda em M e^{+-h} com inicio da janela em 10 Hz), nao
    pela lei de escala; derivada em cos iota por diferenca finita com serie_memoria em iota +- d;
  - produto interno pela soma de Riemann simples f >= 10 Hz (sem peso fracionario).
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import observaveis as O                       # noqa: E402
from deteccao import psd_serie                # noqa: E402

FS = 4096.0
T_INI = -12.0        # s, inicio da grade comum (antes de qualquer t_i usado)
T_HOLD = 4.0
T_RAMPA = 8.0
NFFT = 2 ** 18 * 2   # 128 s a 4096 Hz -> df = 1/128 Hz
TAPER = 0.48         # s (como T_tap = 1500 M de A)
FMIN = 10.0


def serie(q, c1, c2, M, iotas, f_ini=10.0, D=400.0):
    """Lista (por iota) de (ts, hp, hx) fisicos; ts com t = 0 no pico."""
    t, h, ti = O.gerar_janela(q, c1, c2, M, f_ini)
    out = []
    for io in iotas:
        ts, s = O.serie_memoria(t, h, ti, io, 0.0, M, D, tipo="nula", magnetica=True)
        out.append((ts, s.real.copy(), -s.imag.copy()))
    del t, h
    return out


def grade(ts, x):
    """Reamostra x(ts) na grade comum, zero antes de t_i, taper de cosseno de TAPER s, hold e rampa."""
    from scipy.interpolate import CubicSpline
    dt = 1.0 / FS
    tg = T_INI + np.arange(int((ts[-1] - T_INI) * FS) + 1) * dt
    if ts[0] < T_INI + 1.0:
        raise ValueError("T_INI pequeno")
    y = np.zeros_like(tg)
    sel = tg >= ts[0]
    y[sel] = CubicSpline(ts, x)(tg[sel])
    u = tg[sel] - ts[0]
    w = np.where(u < TAPER, 0.5 * (1 - np.cos(np.pi * u / TAPER)), 1.0)
    y[sel] *= w
    nh, nr = int(T_HOLD * FS), int(T_RAMPA * FS)
    y = np.concatenate([y, np.full(nh, y[-1]), y[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(nr) / nr))])
    if len(y) > NFFT:
        raise ValueError("NFFT pequeno")
    return y


def espectro(y):
    """FFT com fase referida a t = 0 (pico): s~(f) = dt sum y_j exp(-2 pi i f t_j)."""
    dt = 1.0 / FS
    Y = np.fft.rfft(y, NFFT) * dt
    f = np.fft.rfftfreq(NFFT, dt)
    return f, Y * np.exp(-2j * np.pi * f * T_INI)


_W = {}


def pesos(nome, f):
    chave = (nome, len(f))
    if chave not in _W:
        df = f[1] - f[0]
        S = psd_serie(nome, len(f), df, FMIN)
        _W[chave] = np.where(np.isfinite(S) & (f >= FMIN), 1.0 / S, 0.0)
    return _W[chave]


def prod(a, b, w, df):
    return 4.0 * df * float(np.real(np.sum(a * np.conj(b) * w)))


SIG_PRIOR = dict(lnM=np.log(3.0) / np.sqrt(12), q=3.0 / np.sqrt(12), c1=1.6 / np.sqrt(12), c2=1.6 / np.sqrt(12),
                 lnD=np.log(5.0) / np.sqrt(12), cosi=2.0 / np.sqrt(12), t0=0.05, psi=np.pi / np.sqrt(12))


def analise(G, nomes, sig, intr=("lnM", "q", "c1", "c2")):
    sp = np.array([sig[n] for n in nomes])
    Gw = G * np.outer(sp, sp)
    lam, V = np.linalg.eigh(Gw)
    o = np.argsort(lam)[::-1]
    lam, V = lam[o], V[:, o]
    lc = np.clip(lam, 0, None)
    Cp = np.linalg.inv(Gw + np.eye(len(nomes)))
    idx = [nomes.index(n) for n in intr]
    return dict(lam=lam, V=V, d_ef=float(np.sum(lc / (lc + 1))), I=float(0.5 * np.sum(np.log2(1 + lc))),
                I_intr=float(-0.5 * np.log2(np.linalg.det(Cp[np.ix_(idx, idx)]))),
                post=np.sqrt(np.diag(Cp)) * sp)
