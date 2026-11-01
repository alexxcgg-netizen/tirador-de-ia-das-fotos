"""Verificacao L00 (6): serie de memoria nula de observaveis.serie_memoria e SNR do sistema A.

Caminho independente do de memorias.py / observaveis.py:
  - projecao angular por coeficientes de Gaunt (simbolos 3j do sympy), sem a grade de CalculadoraMemoria:
        E_L0(u) = sum_{a,b} hdot_a conj(hdot_b) (-1)^m sqrt((2la+1)(2lb+1)(2L+1)/4pi) (la lb L; m -m 0)(la lb L; 2 -2 0)
    (a formula de Gaunt e conferida antes por quadratura direta com harmonicos.sYlm);
  - normalizacao de Favata 2009 (eq. 3.3): dh^mem_L0/du = sqrt((L-2)!/(L+2)!) E_L0(u)  (r h / M, G = c = 1);
  - integral no tempo por antiderivada de spline cubica (scipy), nao pelos pesos de trapezio;
  - SNR por outro tratamento: interpolacao linear a 8192 Hz, valor final mantido 2 s e levado a zero por uma
    janela de Planck de 16 s, sem taper inicial.
Compara a serie (parte real, Delta h_+) em varios instantes e o valor final com serie_memoria e com o
deslocamento de janela de memorias_observaveis, em dt = 0.25 e 0.125; e as SNRs (aLIGO, A+, ET, CE).
Saida: resultados/revisao/verif_L00_serie_nula.txt
"""
import os
import sys
import time
from math import factorial, pi, sqrt

import numpy as np
from scipy.interpolate import CubicSpline
from sympy.physics.wigner import wigner_3j

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import deteccao as Dt                                    # noqa: E402
import observaveis as O                                  # noqa: E402
from harmonicos import sYlm                              # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_serie_nula.txt")
L = []
T0 = time.time()
SA = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, D=400.0, iota=np.radians(50.0), F=10.0)


def log(s=""):
    print(s, flush=True)
    L.append(s)


def gaunt(la, lb, m, Lo):
    v = wigner_3j(la, lb, Lo, m, -m, 0) * wigner_3j(la, lb, Lo, 2, -2, 0)
    return (-1) ** m * sqrt((2 * la + 1) * (2 * lb + 1) * (2 * Lo + 1) / (4 * pi)) * float(v)


# conferencia da formula de Gaunt por quadratura (Gauss-Legendre 40 x 64)
x, wl = np.polynomial.legendre.leggauss(40)
th = np.arccos(x)
ph = 2 * np.pi * np.arange(64) / 64
TH, PH = np.meshgrid(th, ph, indexing="ij")
W = wl[:, None] * (2 * np.pi / 64)
pior = 0.0
for (la, lb, m, Lo) in ((2, 2, 2, 2), (2, 3, 2, 3), (3, 3, -1, 4), (2, 2, 1, 2), (4, 3, 3, 5), (5, 5, 5, 8), (2, 4, -2, 4)):
    num = np.sum(W * sYlm(-2, la, m, TH, PH) * np.conj(sYlm(-2, lb, m, TH, PH)) * np.conj(sYlm(0, Lo, 0, TH, PH)))
    pior = max(pior, abs(num - gaunt(la, lb, m, Lo)))
log("Gaunt (3j do sympy) contra quadratura com harmonicos.sYlm, 7 casos: max |dif| = %.1e" % pior)

LS = list(range(2, 9))
Losc = B.lista_osc()
G = {}
for Lo in LS:
    for a in Losc:
        for b in Losc:
            if a[1] == b[1]:
                g = gaunt(a[0], b[0], a[1], Lo)
                if abs(g) > 1e-14:
                    G[(Lo, a, b)] = g
log("coeficientes de Gaunt nao nulos (L = 2..8, modos oscilatorios): %d" % len(G))


def serie_indep(t, h, ti, iota, phi, Ms, Ds, Lmax=8, deriv="ordem8"):
    """Serie nula independente: (t_fino, Re/Im da serie em unidades fisicas, antiderivada por L)."""
    k = int(np.searchsorted(t, ti))
    j0 = max(k - 40, 0)
    tt = t[j0:]
    if deriv == "ordem8":
        Hd = {a: O.derivada(h[a][:, None], t[1] - t[0])[j0:, 0] for a in Losc}
    else:
        Hd = {a: CubicSpline(t, h[a].real)(tt, 1) + 1j * CubicSpline(t, h[a].imag)(tt, 1) for a in Losc}
    S = {}
    for Lo in LS:
        if Lo > Lmax:
            continue
        E = np.zeros(len(tt), dtype=complex)
        for (LL, a, b), g in G.items():
            if LL == Lo:
                E += g * Hd[a] * np.conj(Hd[b])
        taxa = sqrt(factorial(Lo - 2) / factorial(Lo + 2)) * E
        cs_r, cs_i = CubicSpline(tt, taxa.real).antiderivative(), CubicSpline(tt, taxa.imag).antiderivative()
        S[Lo] = (cs_r, cs_i)
    Y = {Lo: complex(sYlm(-2, Lo, 0, iota, phi)) for Lo in S}

    def avaliar(u):
        tot = 0j
        for Lo, (cr, ci) in S.items():
            tot = tot + ((cr(u) - cr(ti)) + 1j * (ci(u) - ci(ti))) * Y[Lo]
        return tot * Ms / Ds
    return avaliar


Ms, Ds = SA["M"] * Dt.MSUN_S, SA["D"] * Dt.MPC_S
for dt in (0.25, 0.125):
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], dt=dt)
    ts, s = O.serie_memoria(t, h, ti, SA["iota"], 0.0, SA["M"], SA["D"], tipo="nula")
    m, _ = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], t=t, h=h, t_i=ti, dt=dt)
    alvo = O.valores_fisicos_completo(m, SA["iota"], 0.0, SA["M"], SA["D"])["deslocamento"]
    f8 = serie_indep(t, h, ti, SA["iota"], 0.0, Ms, Ds)
    fs_ = serie_indep(t, h, ti, SA["iota"], 0.0, Ms, Ds, deriv="spline")
    log("")
    log("dt = %.3f M: valor final Re s: serie_memoria %.10e ; deslocamento de janela %.10e ; independente (deriv. 8a"
        " ordem) %.10e (dif. %+.1e) ; independente (deriv. spline) %.10e (dif. %+.1e)"
        % (dt, s[-1].real, alvo, f8(t[-1]).real, f8(t[-1]).real / s[-1].real - 1, fs_(t[-1]).real,
           fs_(t[-1]).real / s[-1].real - 1))
    txt = []
    for u in (ti + 100.0, -5000.0, -1000.0, -100.0, -20.0, 0.0, 20.0, 50.0):
        j = int(np.argmin(np.abs(ts / Ms - u)))
        uu = ts[j] / Ms
        txt.append("u=%.0f: %+.1e" % (uu, f8(uu).real / s[j].real - 1))
    log("  Re s(u) independente / serie_memoria - 1: " + " ; ".join(txt))
    log("  max |Im s| (so m = 0, deve ser 0): serie_memoria %.1e ; independente %.1e" % (
        np.max(np.abs(s.imag)), abs(f8(t[-1]).imag)))
    del t, h
log("  (%.0f s)" % (time.time() - T0))


# ------------------------------------------------------------------ SNR por outro tratamento
def planck(n):
    """Janela de Planck decrescente de 1 a 0 em n amostras."""
    x = np.linspace(0, 1, n)
    w = np.zeros(n)
    w[0] = 1.0
    mid = (x > 0) & (x < 1)
    z = 1 / x[mid] - 1 / (1 - x[mid])
    w[mid] = 1 / (1 + np.exp(-np.clip(z, -700, 700)))
    return w


def snr_indep(tsec, hp, psd, fs=8192.0, fmin=10.0, hold=2.0, rampa=16.0):
    dt = 1 / fs
    tg = np.arange(tsec[0], tsec[-1], dt)
    x = np.interp(tg, tsec, hp)
    x = x - x[0]
    x = np.concatenate([x, np.full(int(hold * fs), x[-1]), x[-1] * planck(int(rampa * fs))])
    n = 1
    while n < 2 * len(x):
        n *= 2
    X = np.fft.rfft(x, n) * dt
    f = np.fft.rfftfreq(n, dt)
    df = f[1] - f[0]
    S = Dt.psd_serie(psd, len(f), df, fmin)
    ok = f >= fmin
    return float(np.sqrt(4 * np.sum(np.abs(X[ok]) ** 2 / S[ok]) * df))


log("")
log("SNR (h_+) da memoria nula de A, D = 400 Mpc, iota 50, phi 0, f_min 10 Hz:")
t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
ts, s = O.serie_memoria(t, h, ti, SA["iota"], 0.0, SA["M"], SA["D"], tipo="nula")
f8 = serie_indep(t, h, ti, SA["iota"], 0.0, Ms, Ds)
f4 = serie_indep(t, h, ti, SA["iota"], 0.0, Ms, Ds, Lmax=4)
uu = np.concatenate([[ti], t[t > ti]])
s8 = np.array([f8(u) for u in uu[::1]]) if False else None
# avaliacao vetorizada da serie independente
s8 = f8(uu).real
s4 = f4(uu).real
del t, h
ref_n = {"aLIGO": 0.470, "A+": 0.892, "ET": 8.642, "CE": 34.096}      # rev_R5_snr_memoria_qnm.txt, 'A' (l <= 4)
for psd in ("aLIGO", "A+", "ET", "CE"):
    a = O.snr2(ts, s, psd, 10.0)
    b = snr_indep(ts, s.real, psd)
    c = snr_indep(uu * Ms, s8, psd)
    d = snr_indep(uu * Ms, s4, psd)
    e = snr_indep(ts, s.real, psd, fs=4096.0, hold=4.0, rampa=8.0)
    log("  %-5s: snr2 %.4f ; outro tratamento (8192 Hz, Planck 16 s) %.4f ; serie independente L <= 8 %.4f ;"
        " L <= 4 %.4f (rev_R5 %.3f) ; 4096 Hz, 4 s + 8 s %.4f" % (psd, a, b, c, d, ref_n[psd], e))
log("  (%.0f s)" % (time.time() - T0))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
