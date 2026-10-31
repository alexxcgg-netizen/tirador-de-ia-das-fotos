"""Unidades fisicas, curvas de ruido e sobreposicao (match) de formas de onda.

Produto interno: (a|b) = 4 Re int_fmin^fmax a~(f) conj(b~(f)) / S_n(f) df.
Sobreposicao (match): max_{t,fase} (a|b) / sqrt((a|a)(b|b)), via transformada inversa do
espectro cruzado (o modulo da serie complexa maximiza sobre a fase).
Criterio de distinguibilidade (Lindblom et al. 2008): (dh|dh) > 1, o que para normas iguais da
(dh|dh) ~ 2 rho^2 (1 - match). Chamamos rho_crit = 1/sqrt(2(1 - match)): acima dessa razao
sinal-ruido as duas ondas sao distinguiveis.
"""
import numpy as np

MSUN_S = 4.925490947641267e-06          # G M_sol / c^3 em segundos
MPC_S = 3.0856775814913673e22 / 299792458.0


def psd_serie(nome, n, df, flow):
    """PSD (strain^2/Hz) nas frequencias k*df, k = 0..n-1, pelas funcoes do lalsimulation; inf abaixo de flow."""
    import lal
    import lalsimulation as ls
    f = {"aLIGO": ls.SimNoisePSDaLIGODesignSensitivityT1800044,
         "A+": ls.SimNoisePSDaLIGOAPlusDesignSensitivityT1800042,
         "ET": ls.SimNoisePSDEinsteinTelescopeP1600143,
         "CE": ls.SimNoisePSDCosmicExplorerP1600143}[nome]
    serie = lal.CreateREAL8FrequencySeries("psd", lal.LIGOTimeGPS(0), 0.0, df, lal.DimensionlessUnit, n)
    f(serie, flow)
    out = serie.data.data.copy()
    out[(out <= 0) | (np.arange(n) * df < flow)] = np.inf
    return out


def strain_observador(t, h, lista, M_msun, D_mpc, iota, phi=0.0):
    """h_+ - i h_x no observador, em unidades fisicas; t (adimensional) -> segundos."""
    from harmonicos import sYlm
    Y = np.array([sYlm(-2, l, m, iota, phi) for (l, m) in lista])
    H = np.stack([h[k] for k in lista], axis=1) @ Y
    return t * M_msun * MSUN_S, H * (M_msun * MSUN_S) / (D_mpc * MPC_S)


def _reamostrar(t, x, dt):
    tt = np.arange(t[0], t[-1], dt)
    return tt, np.interp(tt, t, x.real) + 1j * np.interp(tt, t, x.imag)


def produto(a_t, b_t, dt, nome_psd, fmin, fmax=None, pol="+"):
    """Retorna (a|a), (b|b), match. pol='+' usa h_+ (detector otimo para +), 'x' usa h_x."""
    sel = (lambda z: z.real) if pol == "+" else (lambda z: -z.imag)
    n = 1
    while n < 2 * max(len(a_t), len(b_t)):
        n *= 2
    A = np.fft.rfft(sel(a_t), n) * dt
    B = np.fft.rfft(sel(b_t), n) * dt
    f = np.fft.rfftfreq(n, dt)
    fmax = fmax or f[-1]
    ok = (f >= fmin) & (f <= fmax)
    df = f[1] - f[0]
    Sn = psd_serie(nome_psd, len(f), df, fmin)
    aa = 4 * np.sum(np.abs(A[ok]) ** 2 / Sn[ok]) * df
    bb = 4 * np.sum(np.abs(B[ok]) ** 2 / Sn[ok]) * df
    integrando = np.zeros(n, dtype=complex)
    w = np.where(ok, A * np.conj(B) / Sn, 0)
    integrando[:len(f)] = w
    serie = np.fft.ifft(integrando) * n * df * 4          # complexo: |.| maximiza sobre a fase
    return aa, bb, float(np.max(np.abs(serie)) / np.sqrt(aa * bb))


def comparar(tA, hA, tB, hB, nome_psd, fmin, fs=4096.0):
    """Alinha (pelo pico), reamostra e devolve match (+ e x), SNR de A e rho_crit."""
    dt = 1.0 / fs
    ta, a = _reamostrar(tA - tA[np.argmax(np.abs(hA))], hA, dt)
    tb, b = _reamostrar(tB - tB[np.argmax(np.abs(hB))], hB, dt)
    out = {}
    for pol in ("+", "x"):
        aa, bb, m = produto(a, b, dt, nome_psd, fmin, pol=pol)
        out[pol] = dict(match=m, snr_A=np.sqrt(aa), snr_B=np.sqrt(bb),
                        rho_crit=1 / np.sqrt(max(2 * (1 - m), 1e-300)))
    return out
