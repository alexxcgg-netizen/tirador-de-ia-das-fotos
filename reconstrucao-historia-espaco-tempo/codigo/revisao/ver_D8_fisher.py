"""Verificacao D8 (L19, exp39): sigma_delta = 1/||ds_n/dt|| para o sistema A (M = 65, D = 400 Mpc, iota = 50 graus)
com um produto interno escrito aqui (FFT de ds/dt reamostrado por spline, janela de Tukey so no inicio de ds/dt,
sem tratamento do degrau final: ds/dt e um pulso), e rho da memoria nula por |s~| = |FT(ds/dt)|/(2 pi f).
Varia: fs (2048, 4096), taper inicial (0.1 s, 0.5 s), PSD (aLIGO, A+, ET, CE com f_min = 10 Hz).
Tambem refaz a conta sigma(M_f)/M_f: o atraso so depende de M_f pela parte ordinaria, delta_ord(obs)."""
import os
import sys
import numpy as np
from scipy.interpolate import CubicSpline

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import observaveis as O
from deteccao import psd_serie, MSUN_S
from harmonicos import Dfrak

Q, C1, C2, M, DMPC, IOTA = 1.2, 0.3, -0.2, 65.0, 400.0, np.radians(50.0)
t, h, ti = O.gerar_janela(Q, C1, C2, M, 10.0)
mem, aux = O.memorias_observaveis(Q, C1, C2, M, 10.0, t=t, h=h, t_i=ti)
v = O.no_observador_completo(mem, IOTA, 0.0)
mo = {k: dict(x) for k, x in mem.items()}
mo["cm"] = {k: -1.5 * aux["M_f"] * mem["deslocamento"][k] / Dfrak(k[0]) for k in mem["deslocamento"]}
d_tot = -v["cm"] / v["deslocamento"]
d_ord = -O.no_observador_completo(mo, IOTA, 0.0)["cm"] / v["deslocamento"]
print("delta_tot %.4f M (%.1f us), delta_ord %.4f M (%.1f us), M_f %.5f" % (d_tot, d_tot * M * MSUN_S * 1e6, d_ord,
                                                                       d_ord * M * MSUN_S * 1e6, aux["M_f"]))
ts, sn = O.serie_memoria(t, h, ti, IOTA, 0.0, M, DMPC, tipo="nula")
del t, h
s = sn.real
ts1, s1 = ts[1:], s[1:]
cs = CubicSpline(ts1, s1)
for fs in (2048.0, 4096.0):
    dt = 1 / fs
    tt = np.arange(ts1[0], ts1[-1], dt)
    ds = cs(tt, 1)
    for tap in (0.1, 0.5):
        w = np.ones_like(tt)
        nt = int(tap / dt)
        w[:nt] = 0.5 * (1 - np.cos(np.pi * np.arange(nt) / nt))
        x = ds * w
        n = 1
        while n < 4 * len(x):
            n *= 2
        X = np.fft.rfft(x, n) * dt
        f = np.fft.rfftfreq(n, dt)
        df = f[1] - f[0]
        linha = []
        for det in ("aLIGO", "A+", "ET", "CE"):
            Sn = psd_serie(det, len(f), df, 10.0)
            ok = (f >= 10.0) & np.isfinite(Sn)
            nd = np.sqrt(4 * np.sum(np.abs(X[ok]) ** 2 / Sn[ok]) * df)
            rho = np.sqrt(4 * np.sum(np.abs(X[ok]) ** 2 / (2 * np.pi * f[ok]) ** 2 / Sn[ok]) * df)
            sig = 1 / nd
            linha.append("%s rho %.3f sigma %.0f us delta/sigma %.3f (ord %.3f) sigma(Mf)/Mf %.2f"
                         % (det, rho, sig * 1e6, d_tot * M * MSUN_S / sig, d_ord * M * MSUN_S / sig,
                            sig / (d_ord * M * MSUN_S)))
        print("fs %.0f taper %.1f s: " % (fs, tap) + " | ".join(linha))
