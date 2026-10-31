"""Experimento 15: quanto da razao sinal-ruido do sistema A esta na memoria.

Sistema A do exp07 (M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus), NRHybSur3dq8_CCE.
Sinal so de memoria: a parte m = 0 da deformacao no observador, (2,0) + (3,0) + (4,0), menos o valor no
inicio da janela (10 Hz). Para nao criar um degrau artificial no fim da serie (a FFT e periodica), o valor
final e mantido por 4 s e depois levado a zero por um cosseno de 8 s: isso so poe potencia abaixo de ~0.1 Hz,
fora da banda. Compara com a SNR da onda oscilatoria (todos os modos m != 0).
Saida: resultados/exp15_snr_memoria.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
M, D, IOTA, F = 65.0, 400.0, np.radians(50.0), 10.0
t, h = B.gerar(1.2, 0.3, -0.2, f0=M * Dt.MSUN_S * F, dt=0.25)
fs = 4096.0
dt = 1 / fs
linhas = []


def serie(lista):
    ts, s = Dt.strain_observador(t, h, lista, M, D, IOTA)
    tt = np.arange(ts[0], ts[-1], dt)
    return np.interp(tt, ts, s.real) + 1j * np.interp(tt, ts, s.imag)


mem = serie(B.MODOS_M0)
mem = mem - mem[0]
n_hold, n_rampa = int(4 * fs), int(8 * fs)
rampa = mem[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
mem = np.concatenate([mem, np.full(n_hold, mem[-1]), rampa])
osc = serie(B.lista_osc())
for psd in ("aLIGO", "A+", "ET", "CE"):
    aa_m = Dt.produto(mem, mem, dt, psd, F)[0]
    aa_o = Dt.produto(osc, osc, dt, psd, F)[0]
    s = "%-5s: SNR da memoria (h_+, parte m = 0) = %.2f ; SNR da onda oscilatoria = %.0f ; razao = %.1e" % (
        psd, np.sqrt(aa_m), np.sqrt(aa_o), np.sqrt(aa_m / aa_o))
    print(s, flush=True)
    linhas.append(s)
s = ("Precisao relativa minima de cada memoria ~ 1/SNR_memoria (Cramer-Rao, um parametro de amplitude): "
     "diferencas de 1e-3 a 5e-2 entre memorias exigem SNR de memoria de 20 a 1000.")
print(s)
linhas.append(s)
with open(os.path.join(AQUI, "..", "resultados", "exp15_snr_memoria.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
