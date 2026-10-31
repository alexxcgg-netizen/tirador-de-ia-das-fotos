"""Verificacao independente (R1v) dos itens 4 e 5 da revisao R1 do 07: o que um detector ve da memoria.

Sinal so de memoria: modos m = 0 do NRHybSur3dq8_CCE ((2,0), (3,0), (4,0)), no observador (iota, D) de
cada sistema, a partir de 10 Hz, menos o valor inicial; o valor final e mantido 4 s e levado a zero por
um cosseno de 8 s (como no exp15). h_+ = Re h (l par), h_x = -Im h (l impar).
  D1  SNR da memoria em h_+ e em h_x (detector otimo para cada polarizacao), aLIGO e CE; f_rms e sigma_t.
  D2  fracao do valor DC (int h_x du) presente no espectro e fracao acumulada nos ultimos T segundos.
  D3  match entre as memorias de A e de cada B do exp07 (amplitude livre, com sinal; maximizado so no
      tempo, com refinamento continuo do atraso; e tambem maximizado no tempo e na fase, como cota).
Saida: resultados/revisao/rev_R1v_detector.txt
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize_scalar

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
from harmonicos import sYlm                             # noqa: E402

linhas = []
T0 = time.time()
FS, FMIN = 4096.0, 10.0
DT = 1 / FS


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
PARES = json.load(open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")))["pares"]
PARES = [p for p in PARES if p["qB"] in (1.0, 2.0, 3.0) and abs(max(abs(x) for x in p["dif"].values())) < 1e-5]


def sinal_memoria(par):
    """(t_s, h complexo) so de memoria, reamostrado, com t = 0 no pico do (2,2).

    h_+ (degrau de deslocamento): menos o valor inicial (memoria anterior a janela e um offset), valor
    final mantido 4 s e levado a zero por um cosseno de 8 s (como no exp15).
    h_x (pulso da memoria de spin): NAO se subtrai o valor inicial (o pulso volta a zero sozinho depois do
    ringdown); o inicio e suavizado por um cosseno de 1 s (so altera f < ~1 Hz)."""
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * FMIN, dt=0.25)
    Ms, Ds = par["M"] * Dt.MSUN_S, par["D"] * Dt.MPC_S
    z = sum(h[(l, 0)] * sYlm(-2, l, 0, par["iota"], 0.0).real for l in (2, 3, 4)) * Ms / Ds
    ts = (t - t[np.argmax(np.abs(h[(2, 2)]))]) * Ms
    tt = np.arange(ts[0], ts[-1], DT)
    hp = np.interp(tt, ts, z.real)
    hx = -np.interp(tt, ts, z.imag)
    info = dict(hx0=hx[0], I_x=np.sum(hx) * DT, dh=hp[-1] - hp[0], tt=tt.copy(), hx=hx.copy(), hp=hp - hp[0])
    hp = hp - hp[0]
    nr0 = int(1 * FS)
    hx[:nr0] *= 0.5 * (1 - np.cos(np.pi * np.arange(nr0) / nr0))
    nh, nr = int(4 * FS), int(8 * FS)
    hp = np.concatenate([hp, np.full(nh, hp[-1]), hp[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(nr) / nr))])
    hx = np.concatenate([hx, np.zeros(nh + nr)])
    s = hp - 1j * hx
    tt = tt[0] + DT * np.arange(len(s))
    del h
    return tt, s, info


N = 2 ** 19
f = np.fft.rfftfreq(N, DT)
df = f[1] - f[0]
PSD = {nome: Dt.psd_serie(nome, len(f), df, FMIN) for nome in ("aLIGO", "CE")}


def espectro(tt, s, pol):
    x = s.real if pol == "+" else -s.imag
    X = np.fft.rfft(x, N) * DT
    return X * np.exp(-2j * np.pi * f * tt[0])          # referencia de tempo: t = 0 no pico


def prod(X, Y, Sn):
    return 4 * np.sum((X * np.conj(Y) / Sn).real) * df


def match(X, Y, Sn):
    """max sobre o atraso tau de |Re (X|Y e^{2 pi i f tau})| / norma (amplitude livre com sinal), e cota com fase."""
    xx, yy = prod(X, X, Sn), prod(Y, Y, Sn)
    w = np.where(np.isfinite(Sn), X * np.conj(Y) / Sn, 0)
    serie = np.fft.irfft(w, N) * N * df * 4 / 2          # Re (X|Y deslocado) em atrasos k*DT (fator 1/2: irfft)
    # serie e real; o maximo de |serie| da a melhor amplitude (com sinal) na grade
    k = np.argmax(np.abs(serie))
    tau0 = k * DT if k < N // 2 else (k - N) * DT

    def neg(tau):
        return -abs(4 * np.sum((w * np.exp(2j * np.pi * f * tau)).real) * df)
    r = minimize_scalar(neg, bracket=(tau0 - DT, tau0, tau0 + DT), tol=1e-12)
    m_t = -r.fun / np.sqrt(xx * yy)
    # cota maximizando tambem a fase (serie analitica)
    z = np.zeros(N, dtype=complex)
    z[:len(f)] = w
    m_f = np.max(np.abs(np.fft.ifft(z) * N * df * 4)) / np.sqrt(xx * yy)
    return np.sqrt(xx), np.sqrt(yy), m_t, m_f


ttA, sA, infoA = sinal_memoria(A)
log("D1. SNR da memoria do sistema A (iota = 50 graus), detector otimo para cada polarizacao")
for nome, Sn in PSD.items():
    for pol in ("+", "x"):
        X = espectro(ttA, sA, pol)
        rho = np.sqrt(prod(X, X, Sn))
        frms = np.sqrt(4 * np.sum(f ** 2 * np.abs(X) ** 2 / Sn) * df) / rho
        log("  %-5s %s: rho_mem = %.3f ; f_rms = %.1f Hz ; sigma_t = 1/(2 pi rho f_rms) = %.2e s" % (
            nome, pol, rho, frms, 1 / (2 * np.pi * rho * frms)))
log("  CM/Delta h_+ (tabela 3.3, nivel A) = %.3e s ; M = %.3e s" % (-3.0687e-26 / 1.8292e-22, A["M"] * Dt.MSUN_S))

log("\nD2. espectro e acumulacao da memoria de spin (h_x) e de deslocamento (h_+) de A")
hx, hp, tA_ = infoA["hx"], infoA["hp"], infoA["tt"]
I_x = infoA["I_x"]
log("  int h_x du (desde 10 Hz, sem suavizar) = %.4e s ; h_x(u_i) = %.3e (pico %.3e) ; Delta h_+ na janela = %.4e" % (
    I_x, infoA["hx0"], np.max(np.abs(hx)), infoA["dh"]))
Xx, Xp = espectro(ttA, sA, "x"), espectro(ttA, sA, "+")
for fv in (1.0, 5.0, 10.0, 20.0, 50.0, 100.0):
    j = np.argmin(np.abs(f - fv))
    log("    f = %5.1f Hz: |h~_x|/|int h_x du| = %.3f ; |2 pi f h~_+|/Delta h_+ = %.3f" % (
        f[j], abs(Xx[j]) / abs(I_x), abs(2 * np.pi * f[j] * Xp[j]) / abs(infoA["dh"])))
cum = np.cumsum(hx) * DT
for T in (0.01, 0.1, 1.0, 3.0):
    j = np.argmin(np.abs(tA_ + T))
    log("    ultimos %.2f s antes do pico (ate o fim): fracao de int h_x du = %.3f ; fracao de Delta h_+ = %.3f" % (
        T, 1 - cum[j] / cum[-1], 1 - hp[j] / hp[-1]))

log("\nD3. match entre memorias resolvidas no tempo (A x B do exp07), amplitude livre")
for nome, Sn in PSD.items():
    for pol in ("+", "x"):
        X = espectro(ttA, sA, pol)
        X2 = X * np.exp(2j * np.pi * f * 3.3e-4)          # controle: A deslocado de 0,33 ms
        _, _, mt, mf = match(X, X2, Sn)
        log("  controle %s %s (A x A deslocado): 1 - match = %.1e" % (nome, pol, 1 - mt))
for p in PARES:
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    ttB, sB, _ = sinal_memoria(par)
    out = []
    for nome, Sn in PSD.items():
        for pol in ("+", "x"):
            X, Y = espectro(ttA, sA, pol), espectro(ttB, sB, pol)
            ra, rb, mt, mf = match(X, Y, Sn)
            out.append("%s %s: rhoA %.2f rhoB %.2f match_t %.5f (rho_crit %.1f) match_t,fase %.5f (rho_crit %.1f)" % (
                nome, pol, ra, rb, mt, 1 / np.sqrt(2 * (1 - mt)), mf, 1 / np.sqrt(2 * (1 - mf))))
    log("  B (q = %.0f, chi2 = %+.1f, M = %.2f, iota = %.1f):" % (p["qB"], p["c2B"], p["M"], np.degrees(p["iota"])))
    for o in out:
        log("     " + o)
    del sB
log("(%.0f s)" % (time.time() - T0))
with open(os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1v_detector.txt"), "w") as fh:
    fh.write("\n".join(linhas) + "\n")
