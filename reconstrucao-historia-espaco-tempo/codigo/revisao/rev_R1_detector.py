"""Revisao R1 (item i): o que um detector em solo mede das quatro memorias.

Sistema A do exp07 e pares B do exp07_pares.json; modos m = 0 do NRHybSur3dq8_CCE (nivel C) no observador.
  D1  memoria de spin: h_x^{m=0}(t) e um pulso; int h_x du e o valor do espectro em f = 0.
      Mostro |h~_x(f)| / |int h_x du| em varias frequencias e a fracao de int h_x du acumulada nos
      ultimos T segundos antes do pico (o que um detector com corte em 10 Hz pode ver).
  D2  deslocamento: fracao do degrau (desde 10 Hz) acumulada nos ultimos T segundos; |2 pi f h~_+(f)| / Delta h.
  D3  memoria de CM como atraso: CM / Delta h_+ (segundos) contra a incerteza de tempo de chegada de um
      sinal so de memoria, sigma_t = 1/(2 pi rho f_rms), em aLIGO e CE.
  D4  cenario de memoria orfa: match entre as memorias resolvidas no tempo (so m = 0) de A e de cada B,
      com amplitude livre (match normalizado), para h_+ e h_x; rho_crit = 1/sqrt(2(1 - match)).
Saida: resultados/revisao/rev_R1_detector.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import deteccao as Dt                                    # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1_detector.txt")
linhas = []
T0 = time.time()
FS = 4096.0
DT = 1 / FS
F_FIS = 10.0


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def serie_memoria(par):
    """h_+ - i h_x (so modos m = 0) no observador, reamostrado, menos o valor inicial; t = 0 no pico de (2,2)."""
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * F_FIS, dt=0.25)
    ts, s = Dt.strain_observador(t, h, B.MODOS_M0, par["M"], par["D"], par["iota"])
    tpk = ts[np.argmax(np.abs(h[(2, 2)]))]
    del h
    tt = np.arange(ts[0], ts[-1], DT)
    zp = np.interp(tt, ts, s.real)
    zx = -np.interp(tt, ts, s.imag)
    # h_+ (l par, eletrica): tira a memoria acumulada antes da janela. h_x (l impar, magnetica) e um pulso que
    # ja vai a zero no passado: nao se subtrai nada; so uma rampa de 0.5 s no inicio (potencia abaixo de ~2 Hz).
    n_r = int(0.5 * FS)
    zx[:n_r] *= 0.5 * (1 - np.cos(np.pi * np.arange(n_r) / n_r))
    return tt - tpk, (zp - zp[0]) - 1j * zx


def estender(z):
    """Mantem o valor final por 4 s e leva a zero com cosseno de 8 s (como no exp15)."""
    n_hold, n_rampa = int(4 * FS), int(8 * FS)
    rampa = z[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
    return np.concatenate([z, np.full(n_hold, z[-1]), rampa])


def espectros(a, b, nome_psd, fmin=F_FIS):
    """Produto interno com ruido: (a|a), (b|b), match (max sobre tempo; parte real, sem maximizar fase)."""
    n = 1
    while n < 2 * max(len(a), len(b)):
        n *= 2
    Af = np.fft.rfft(a, n) * DT
    Bf = np.fft.rfft(b, n) * DT
    f = np.fft.rfftfreq(n, DT)
    df = f[1] - f[0]
    Sn = Dt.psd_serie(nome_psd, len(f), df, fmin)
    ok = f >= fmin
    aa = 4 * np.sum(np.abs(Af[ok]) ** 2 / Sn[ok]) * df
    bb = 4 * np.sum(np.abs(Bf[ok]) ** 2 / Sn[ok]) * df
    w = np.where(ok, Af * np.conj(Bf) / Sn, 0)
    sobre = 16                                                 # resolucao temporal DT/16 na maximizacao
    integ = np.zeros(n * sobre, dtype=complex)
    integ[:len(f)] = w
    serie = np.fft.ifft(integ) * n * sobre * df * 4
    f2 = 4 * np.sum(f[ok] ** 2 * np.abs(Af[ok]) ** 2 / Sn[ok]) * df / aa
    return aa, bb, float(np.max(serie.real) / np.sqrt(aa * bb)), float(np.max(np.abs(serie)) / np.sqrt(aa * bb)), np.sqrt(f2)


with open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")) as fh:
    J = json.load(fh)
A = dict(J["A"])
tA, zA = serie_memoria(A)
hp, hx = zA.real, -zA.imag
log("Sistema A: duracao da janela desde 10 Hz = %.2f s ; Delta h_+ (janela, NR) = %.4e ; int h_x du (janela, NR) = %.4e s"
    % (tA[-1] - tA[0], hp[-1], np.sum(hx) * DT))
log("  (07 tabela 3.3, nivel A: Delta h_+ total = 1.829e-22 ; int h_x du = -2.498e-25 s ; CM = -3.069e-26 s)")

# ---------------- D1 e D2
log("")
log("D1/D2 fracao acumulada nos ultimos T segundos antes do pico de (2,2) (ate o fim da serie):")
Sx = np.cumsum(hx) * DT
for T in (0.005, 0.01, 0.02, 0.05, 0.1, 0.3, 1.0, 3.0):
    k = np.searchsorted(tA, -T)
    fr_s = (Sx[-1] - Sx[k]) / Sx[-1]
    fr_d = (hp[-1] - hp[k]) / hp[-1]
    log("  T = %5.3f s: spin %.3f ; deslocamento %.3f" % (T, fr_s, fr_d))
zx = estender(hx + 0j).real
zp = estender(hp + 0j).real
n = 1
while n < 2 * len(zx):
    n *= 2
fq = np.fft.rfftfreq(n, DT)
Hx = np.fft.rfft(zx, n) * DT
Hp = np.fft.rfft(zp, n) * DT
log("  espectro: f (Hz), |h~_x(f)|/|int h_x du|, |2 pi f h~_+(f)|/Delta h_+(janela)")
for f0 in (0.05, 0.5, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0):
    k = np.argmin(np.abs(fq - f0))
    log("    %6.2f  %.3f  %.3f" % (fq[k], np.abs(Hx[k]) / abs(Sx[-1]), 2 * np.pi * fq[k] * np.abs(Hp[k]) / abs(hp[-1])))

# ---------------- D3
log("")
cmA = J["alvo"]["cm"]
dA = J["alvo"]["deslocamento"]
log("D3 CM como atraso do degrau: CM/Delta h_+ = %.3e s (= %.2f M) ; M_f/2 = %.3e s"
    % (cmA / dA, cmA / dA / (A["M"] * Dt.MSUN_S), 0.5 * 0.9497 * A["M"] * Dt.MSUN_S))
for psd in ("aLIGO", "CE"):
    aa, _, _, _, frms = espectros(zp, zp, psd)
    rho = np.sqrt(aa)
    log("  %-5s: rho_mem(h_+) = %.2f ; f_rms = %.1f Hz ; sigma_t = 1/(2 pi rho f_rms) = %.2e s (%.1f x |CM/Delta h|)"
        % (psd, rho, frms, 1 / (2 * np.pi * rho * frms), 1 / (2 * np.pi * rho * frms) / abs(cmA / dA)))

# ---------------- D4
log("")
log("D4 memoria orfa: match entre as memorias resolvidas no tempo (m = 0) de A e B, amplitude livre")
# controle numerico: A contra A com M 1e-4 maior e D 10% maior (o match deve ser ~1)
parC = dict(A)
parC["M"] = A["M"] * (1 + 1e-4)
parC["D"] = A["D"] * 1.1
_, zC = serie_memoria(parC)
for pol, sel in (("+", lambda z: z.real), ("x", lambda z: -z.imag)):
    aa, bb, mre, _, _ = espectros(estender(sel(zA) + 0j).real, estender(sel(zC) + 0j).real, "aLIGO")
    log("  controle (A x A com M*(1+1e-4), D*1.1), %s aLIGO: 1 - match = %.1e" % (pol, 1 - mre))
for p in J["pares"]:
    if (p["qB"], p["c2B"]) not in ((1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (2.0, 0.5)):
        continue
    parB = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    tB, zB = serie_memoria(parB)
    out = []
    for pol, sel in (("+", lambda z: z.real), ("x", lambda z: -z.imag)):
        a = estender(sel(zA) + 0j).real
        b = estender(sel(zB) + 0j).real
        for psd in ("aLIGO", "CE"):
            aa, bb, mre, mabs, _ = espectros(a, b, psd)
            out.append("%s %s: rho_A %.2f rho_B %.2f match %.5f (rho_crit %.1f)"
                       % (pol, psd, np.sqrt(aa), np.sqrt(bb), mre, 1 / np.sqrt(max(2 * (1 - mre), 1e-300))))
    log("  B (q=%.0f, chi2=%.1f, M=%.2f): %s" % (p["qB"], p["c2B"], p["M"], " | ".join(out)))
    log("     Delta h_+ janela NR: A %.4e, B %.4e ; int h_x du janela NR: A %.4e, B %.4e"
        % (zA.real[-1], zB.real[-1], -np.sum(zA.imag) * DT, -np.sum(zB.imag) * DT))
log("(%.0f s)" % (time.time() - T0))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(linhas) + "\n")
