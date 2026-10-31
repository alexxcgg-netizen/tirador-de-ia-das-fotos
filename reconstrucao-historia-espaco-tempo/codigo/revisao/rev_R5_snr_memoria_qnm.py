"""Revisor R5: a SNR da memoria do exp15 inclui o toque de modos quase normais dos modos m = 0?

Motivacao (literatura): os modos m = 0 de CCE contem memoria e tambem oscilacao de ringdown
(Rossello-Sastre, Husa, Bera 2024, arXiv:2405.17302; Valencia et al. 2024, arXiv:2406.16636), e
Siddhant, Grant, Nichols 2026 (arXiv:2608.23739, nota 7) dizem que essa parte quase normal nao deve
entrar nas buscas de memoria. O exp15 usa os modos m = 0 completos do NRHybSur3dq8_CCE.

Compara a SNR (h_+, detector otimo, f_min 10 Hz) do sistema A do exp07 para:
  C     : modos m = 0 do substituto (como no exp15);
  A     : sinal de memoria nula nao oscilatorio: h_l0(u0) + int dmem du (eletrico) + hB (magnetico),
          com os fluxos dos modos oscilatorios (nivel A);
  A+EJ  : A mais a parte eletrica instantanea hEJ;
  C - A : o resto (toque quase normal, erro do modelo, partes lineares).
Mesmo tratamento de borda do exp15 (valor final mantido 4 s e levado a zero por cosseno de 8 s).
Saida: resultados/revisao/rev_R5_snr_memoria_qnm.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from rev_R3_comum import B, taxas_instantaneas, SAIDA          # noqa: E402
import deteccao as Dt                                          # noqa: E402

M, D, IOTA, F = 65.0, 400.0, np.radians(50.0), 10.0
dt_m = 0.25
t, h = B.gerar(1.2, 0.3, -0.2, f0=M * Dt.MSUN_S * F, dt=dt_m)
fs = 4096.0
dt = 1 / fs
linhas = []


def log(s):
    print(s, flush=True)
    linhas.append(s)


# sinal de memoria nula (nivel A) nos modos m = 0
c_osc, _ = B.calculadoras()
Losc = B.lista_osc()
H = np.stack([h[k] for k in Losc], axis=1)
Hd = B.derivada4(H, dt_m)
L0 = [(2, 0), (3, 0), (4, 0)]
hB, hEJ, dmem = taxas_instantaneas(c_osc, H, Hd, L0)
del H, Hd
hA, hAEJ, hC = {}, {}, {}
for j, k in enumerate(L0):
    base = h[k][0] + np.cumsum(dmem[:, j]) * dt_m + hB[:, j]
    hA[k] = base
    hAEJ[k] = base + hEJ[:, j]
    hC[k] = h[k]
hR = {k: hC[k] - hA[k] for k in L0}


def serie(hh):
    ts, s = Dt.strain_observador(t, hh, L0, M, D, IOTA)
    tt = np.arange(ts[0], ts[-1], dt)
    return np.interp(tt, ts, s.real) + 1j * np.interp(tt, ts, s.imag)


def com_borda(s):
    s = s - s[0]
    n_hold, n_rampa = int(4 * fs), int(8 * fs)
    rampa = s[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
    return np.concatenate([s, np.full(n_hold, s[-1]), rampa])


sinais = {"C (exp15)": com_borda(serie(hC)), "A": com_borda(serie(hA)), "A+EJ": com_borda(serie(hAEJ))}
sinais["C - A"] = sinais["C (exp15)"] - sinais["A"]
log("Sistema A do exp07 (M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus), janela 10 Hz.")
log("Degrau final de h_+ (m = 0): C = %.4e ; A = %.4e ; A+EJ = %.4e" % (
    sinais["C (exp15)"][-int(12 * fs)].real, sinais["A"][-int(12 * fs)].real, sinais["A+EJ"][-int(12 * fs)].real))
for psd in ("aLIGO", "A+", "ET", "CE"):
    partes = []
    for nome, s in sinais.items():
        aa = Dt.produto(s, s, dt, psd, F)[0]
        partes.append("%s %.3f" % (nome, np.sqrt(aa)))
    _, _, mt = Dt.produto(sinais["C (exp15)"], sinais["A"], dt, psd, F)
    log("%-5s: SNR  " % psd + " ; ".join(partes) + " ; match(C, A) = %.4f" % mt)
# onde (em frequencia) esta a SNR de A e do resto C - A
log("Divisao em bandas (SNR acumulada em [f_a, f_b] Hz):")
bandas = [(10, 30), (30, 100), (100, 180), (180, 300), (300, 1000)]
for psd in ("aLIGO", "CE"):
    for nome in ("A", "C - A"):
        s = sinais[nome]
        partes = ["[%d,%d] %.3f" % (fa, fb, np.sqrt(Dt.produto(s, s, dt, psd, fa, fmax=fb)[0])) for fa, fb in bandas]
        log("  %-5s %-6s: " % (psd, nome) + " ; ".join(partes))
# frequencia de pico do resto (espectro de amplitude de h_+)
r = sinais["C - A"].real
n = 1
while n < 2 * len(r):
    n *= 2
R = np.abs(np.fft.rfft(r, n)) * dt
fr = np.fft.rfftfreq(n, dt)
sel = fr > 30
log("Pico do espectro |FFT(h_+)| do resto C - A acima de 30 Hz: %.1f Hz" % fr[sel][np.argmax(R[sel])])
os.makedirs(SAIDA, exist_ok=True)
with open(os.path.join(SAIDA, "rev_R5_snr_memoria_qnm.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
