"""Revisao R2, item 4: robustez da SNR da memoria do exp15 a escolhas de tratamento do sinal.

Reproduz o exp15 (sistema A: M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus) e varia:
  (a) o tempo em que o valor final e mantido e a rampa de cosseno ate zero: (4, 8) s [exp15], (2, 4) s,
      (8, 16) s, e (0, 0) s (sem tratamento: degrau abrupto no fim da serie);
  (b) a frequencia de inicio: janela (inicio da onda) e f_min do produto interno em 10 ou 20 Hz,
      separando os dois efeitos (janela 10 Hz com f_min 20 Hz; janela 20 Hz com f_min 20 Hz);
  (c) uma janela de Tukey (cosseno) de 0.5 s no inicio da onda oscilatoria (o exp15 nao aplica nenhuma).
Saida: resultados/revisao/rev_R2_exp15_robustez.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402

M, D, IOTA = 65.0, 400.0, np.radians(50.0)
fs = 4096.0
dt = 1 / fs
PSDS = ("aLIGO", "A+", "ET", "CE")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def serie(t, h, lista):
    ts, s = Dt.strain_observador(t, h, lista, M, D, IOTA)
    tt = np.arange(ts[0], ts[-1], dt)
    return np.interp(tt, ts, s.real) + 1j * np.interp(tt, ts, s.imag)


def sinal_memoria(t, h, t_hold, t_rampa):
    """Parte m = 0 menos o valor inicial; valor final mantido t_hold s e levado a zero por cosseno de t_rampa s."""
    mem = serie(t, h, B.MODOS_M0)
    mem = mem - mem[0]
    n_hold, n_rampa = int(t_hold * fs), int(t_rampa * fs)
    rampa = mem[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / max(n_rampa, 1)))
    return np.concatenate([mem, np.full(n_hold, mem[-1]), rampa])


def tukey_inicio(x, T):
    """Janela de cosseno (meia Tukey) nos primeiros T segundos."""
    n = int(T * fs)
    w = np.ones(len(x))
    w[:n] = 0.5 * (1 - np.cos(np.pi * np.arange(n) / n))
    return x * w


def snr(x, psd, fmin):
    return np.sqrt(Dt.produto(x, x, dt, psd, fmin)[0])


ondas = {}
for fjan in (10.0, 20.0):
    ondas[fjan] = B.gerar(1.2, 0.3, -0.2, f0=M * Dt.MSUN_S * fjan, dt=0.25)

log("Revisao R2 do exp15 (SNR da memoria do sistema A). SNR da memoria = parte m = 0 de h_+; onda = modos m != 0.")
log("")
log("(a) tempo de manutencao / rampa no fim (janela 10 Hz, f_min 10 Hz):")
t, h = ondas[10.0]
osc = serie(t, h, B.lista_osc())
base = {}
for (th, tr) in [(4, 8), (2, 4), (8, 16), (0, 0)]:
    mem = sinal_memoria(t, h, th, tr)
    vals = {p: snr(mem, p, 10.0) for p in PSDS}
    if (th, tr) == (4, 8):
        base = vals
    log("  hold %d s, rampa %2d s: " % (th, tr) + " ; ".join(
        "%s %.4f (%+.2e)" % (p, vals[p], vals[p] / base[p] - 1) for p in PSDS))
log("  (entre parenteses: variacao relativa contra o exp15, hold 4 s e rampa 8 s)")
log("")
log("(b) frequencia de inicio (hold 4 s, rampa 8 s):")
for fjan, fmin in [(10.0, 10.0), (10.0, 20.0), (20.0, 20.0), (20.0, 10.0)]:
    t, h = ondas[fjan]
    mem = sinal_memoria(t, h, 4, 8)
    osc_b = serie(t, h, B.lista_osc())
    sm = {p: snr(mem, p, fmin) for p in PSDS}
    so = {p: snr(osc_b, p, fmin) for p in PSDS}
    log("  janela %2.0f Hz, f_min %2.0f Hz: " % (fjan, fmin) + " ; ".join(
        "%s mem %.3f osc %.1f razao %.2e" % (p, sm[p], so[p], sm[p] / so[p]) for p in PSDS))
log("")
log("(c) janela de Tukey de 0.5 s no inicio da onda oscilatoria (janela 10 Hz, f_min 10 Hz):")
t, h = ondas[10.0]
osc = serie(t, h, B.lista_osc())
for T in (0.25, 0.5, 1.0):
    ot = tukey_inicio(osc, T)
    log("  Tukey %.2f s: " % T + " ; ".join(
        "%s osc %.2f -> %.2f (%+.2e)" % (p, snr(osc, p, 10.0), snr(ot, p, 10.0), snr(ot, p, 10.0) / snr(osc, p, 10.0) - 1)
        for p in PSDS))
with open(os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R2_exp15_robustez.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
