"""Revisao R2: funcoes comuns (produto interno com variantes de tratamento do sinal).

Mesmo produto interno de deteccao.produto, com tres opcoes a mais:
  up      fator de refinamento da busca no tempo (zero padding do espectro cruzado antes da FFT inversa):
          a busca do exp07 e feita na grade de 1/fs; up = 16 da resolucao 1/(16 fs);
  taper   janela de cosseno (meia Tukey) nos primeiros taper segundos da serie;
  fim     tratamento do valor final nao nulo dos modos m = 0 (memoria): 'nada' (como no exp07: a serie
          com zeros apos o fim tem um degrau abrupto), ou 'rampa' (subtrai o valor inicial, mantem o valor
          final por 4 s e leva a zero por um cosseno de 8 s, como no exp15).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import deteccao as Dt                                   # noqa: E402

_psd_cache = {}


def psd(nome, n, df, fmin):
    k = (nome, n, round(df, 15), fmin)
    if k not in _psd_cache:
        _psd_cache.clear()
        _psd_cache[k] = Dt.psd_serie(nome, n, df, fmin)
    return _psd_cache[k]


def preparar(t, h, dt, taper=0.0, fim="nada", t_hold=4.0, t_rampa=8.0):
    """Serie complexa h_+ - i h_x na grade dt (alinhada pelo pico, como deteccao.comparar) com tratamento."""
    _, x = Dt._reamostrar(t - t[np.argmax(np.abs(h))], h, dt)
    if fim == "rampa":
        x = x - x[0]
        n_hold, n_rampa = int(t_hold / dt), int(t_rampa / dt)
        rampa = x[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
        x = np.concatenate([x, np.full(n_hold, x[-1]), rampa])
    if taper > 0:
        n = int(taper / dt)
        w = np.ones(len(x))
        w[:n] = 0.5 * (1 - np.cos(np.pi * np.arange(n) / n))
        x = x * w
    return x


def produto(a_t, b_t, dt, nome_psd, fmin, up=1, n_min=0):
    """(a|a), (b|b), match (so h_+), maximizado no tempo (resolucao dt/up) e na fase."""
    n = 1
    while n < max(2 * max(len(a_t), len(b_t)), n_min):
        n *= 2
    A = np.fft.rfft(a_t.real, n) * dt
    Bf = np.fft.rfft(b_t.real, n) * dt
    f = np.fft.rfftfreq(n, dt)
    ok = f >= fmin
    df = f[1] - f[0]
    Sn = psd(nome_psd, len(f), df, fmin)
    aa = 4 * np.sum(np.abs(A[ok]) ** 2 / Sn[ok]) * df
    bb = 4 * np.sum(np.abs(Bf[ok]) ** 2 / Sn[ok]) * df
    N = n * up
    integrando = np.zeros(N, dtype=complex)
    integrando[:len(f)] = np.where(ok, A * np.conj(Bf) / Sn, 0)
    serie = np.fft.ifft(integrando) * N * df * 4
    return aa, bb, float(np.max(np.abs(serie)) / np.sqrt(aa * bb))


def comparar(tA, hA, tB, hB, nome_psd, fmin, fs=4096.0, up=1, taper=0.0, fim="nada"):
    """Como deteccao.comparar (so h_+), com as variantes. Devolve dict com match, snr_A, snr_B."""
    dt = 1.0 / fs
    a = preparar(tA, hA, dt, taper, fim)
    b = preparar(tB, hB, dt, taper, fim)
    aa, bb, m = produto(a, b, dt, nome_psd, fmin, up=up)
    return dict(match=m, snr_A=np.sqrt(aa), snr_B=np.sqrt(bb))


def criterios(c):
    """Criterios de distinguibilidade a partir de match e SNRs.

    dd_real     (dh|dh) na SNR real = rho_A^2 + rho_B^2 - 2 rho_A rho_B match (identidade exata, com o
                deslocamento de tempo e fase que maximiza a sobreposicao);
    rc_igual    1/sqrt(2(1 - match)) (supoe normas iguais; criterio do 07);
    rc_exato    SNR de A em que (dh|dh) = 1, mantendo a razao r = rho_B/rho_A (as duas fontes mais longe
                pelo mesmo fator): 1/sqrt(1 + r^2 - 2 r match);
    rc_ampl     SNR de A em que (dh|dh) = 1 se a amplitude de B for livre (minimo sobre a amplitude):
                1/sqrt(1 - match^2).
    """
    rA, rB, m = c["snr_A"], c["snr_B"], c["match"]
    r = rB / rA
    return dict(dd_real=rA ** 2 + rB ** 2 - 2 * rA * rB * m, r=r,
                rc_igual=1 / np.sqrt(max(2 * (1 - m), 1e-300)),
                rc_exato=1 / np.sqrt(max(1 + r * r - 2 * r * m, 1e-300)),
                rc_ampl=1 / np.sqrt(max(1 - m * m, 1e-300)))
