"""L04, tarefa 4 (pre-calculo): bandas elementares numa grade comum em M f, memorias, jacobianos e matriz de Gram do ruido.

Para cada fonte (A; q=3 chi=(0.6,0); M=30; M=150; D=400 Mpc, iota=50 graus, phi=0, so m=0):
  * bordas e_0 = 10 Hz e e_k = pontos da grade comum G (geometrica, razao (0.030/0.0014)^(1/48), de M f = 0.0014 a ~0.050)
    acima de 10 Hz e abaixo de 0.9 f_22(pico);
  * janelas [t_i(e_k), fim]: deslocamento e spin no observador (exp20_comum.janelas, nivel A) e o jacobiano d ln|y|/d theta
    (theta = q, chi1, chi2, M, iota, D; 5 pontos) -> bandas elementares nitidas [e_k, e_{k+1}] e [e_last, fim];
  * series de memoria nula no observador (observaveis.serie_memoria, + e x com a parte magnetica) particionadas por uma
    particao da unidade suave em ln f (transicao de meia largura eps = 0.3 Delta ln f em cada borda, f = frequencia do (2,2)
    monotonizada): u_k^d(t) = int w_k dS_+ (deslocamento, polarizacao +) e u_k^s(t) = w_k h^B_x(t) (spin, polarizacao x);
  * matrizes de Gram G_jk = (u_j|u_k) para CE e ET (mesmo tratamento de observaveis.snr2: Tukey 0.5 s, rampa final,
    spline a 4096 Hz). diag(G) = SNR^2 de cada banda; a soma de G = SNR^2 da serie inteira.
Saida: resultados/exp23_prep_<fonte>.npz e .txt (so numeros).
Uso: python exp23_preparar.py FONTE [FONTE ...]
"""
import os
import sys
import time

import numpy as np

import exp20_comum as C
import observaveis as O
from deteccao import MSUN_S, MPC_S

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = {
    "A": dict(q=1.2, c1=0.3, c2=-0.2, M=65.0),
    "q3": dict(q=3.0, c1=0.6, c2=0.0, M=65.0),
    "M30": dict(q=1.2, c1=0.3, c2=-0.2, M=30.0),
    "M150": dict(q=1.2, c1=0.3, c2=-0.2, M=150.0),
}
GRADE_MF = 0.0014 * (0.030 / 0.0014) ** (np.arange(57) / 48)   # 49 pontos ate 0.030 e mais 8 ate ~0.050 (fusao)
FRAC_PICO = 0.9                    # so bordas abaixo de 0.9 f_22(pico): t_i e procurado antes do pico
DETS = ("CE", "ET")
EPS = 0.3 * np.log(GRADE_MF[1] / GRADE_MF[0])


def degrau(lnf, ln_e):
    """Degrau suave de 0 a 1 em torno de ln_e (cosseno elevado, meia largura EPS)."""
    z = np.clip((lnf - ln_e) / EPS, -1.0, 1.0)
    return 0.5 * (1 + np.sin(0.5 * np.pi * z))


def gram(series, t, nome_psd, fmin=5.0, fs=4096.0):
    """Matriz (u_j|u_k) com o tratamento de observaveis.preparar (parte real de cada serie)."""
    X = [O.preparar(t, u, fs) for u in series]
    nmax = max(len(x) for x in X)
    n = 1
    while n < 2 * nmax:
        n *= 2
    dt = 1.0 / fs
    f = np.fft.rfftfreq(n, dt)
    ok = f >= fmin
    df = f[1] - f[0]
    Sn = O._psd(nome_psd, len(f), df, fmin)
    F = np.array([(np.fft.rfft(x.real, n) * dt)[ok] / np.sqrt(Sn[ok]) for x in X])
    G = 4 * np.real(F @ F.conj().T) * df
    return G


def preparar_fonte(nome):
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)

    t0 = time.time()
    par = dict(FONTES[nome], D=400.0, iota=float(np.radians(50.0)), phi=0.0)
    Ms, Ds = par["M"] * MSUN_S, par["D"] * MPC_S
    mf10 = 10.0 * Ms
    t, h, ti = O.gerar_janela(par["q"], par["c1"], par["c2"], par["M"], 10.0)
    w22, _ = O._freq22(t, h[(2, 2)])
    mf_pico = float(w22[np.argmax(np.abs(h[(2, 2)]))] / (2 * np.pi))
    del t, h
    G_mf = GRADE_MF[(GRADE_MF > mf10 * 1.0001) & (GRADE_MF < FRAC_PICO * mf_pico)]
    log("  M f do pico do (2,2): %.4f ; bordas ate %.4f" % (mf_pico, G_mf[-1]))
    bordas_mf = np.concatenate([[mf10], G_mf])
    bordas_hz = bordas_mf / Ms
    log("fonte %s: %s ; %d bordas de %.2f a %.2f Hz (M f %.5f a %.4f)"
        % (nome, par, len(bordas_hz), bordas_hz[0], bordas_hz[-1], bordas_mf[0], bordas_mf[-1]))
    t0 = time.time()
    # janelas nitidas e jacobiano (deslocamento e spin)
    tipos = ("deslocamento", "spin")
    Jw, y0 = C.jacobiano(par, list(bordas_hz), tipos=tipos)
    nb = len(bordas_hz)
    Jw = Jw.reshape(nb, 2, 6)
    y0 = y0.reshape(nb, 2)
    Y = y0                                                 # valores brutos (jacobiano devolve y0 sem log)
    log("  jacobiano das janelas: %.0f s" % (time.time() - t0))
    dY = Y[:, :, None] * Jw                                # derivada bruta
    # bandas elementares nitidas: [e_k, e_{k+1}] e a ultima [e_last, fim]
    Vb = np.concatenate([Y[:-1] - Y[1:], Y[-1:]], axis=0)
    dVb = np.concatenate([dY[:-1] - dY[1:], dY[-1:]], axis=0)
    # series
    t1 = time.time()
    t, h, ti = O.gerar_janela(par["q"], par["c1"], par["c2"], par["M"], 10.0)
    ts, sd = O.serie_memoria(t, h, ti, par["iota"], 0.0, par["M"], par["D"], tipo="nula")
    _, sdb = O.serie_memoria(t, h, ti, par["iota"], 0.0, par["M"], par["D"], tipo="nula", magnetica=True)
    hB = sdb - sd                                          # parte magnetica instantanea (h_+ - i h_x)
    w22, _ = O._freq22(t, h[(2, 2)])
    k = int(np.searchsorted(t, ti, side="left"))
    w_s = np.concatenate([[np.interp(ti, t, w22)], w22[k:]])
    f_s = np.maximum.accumulate(np.maximum(w_s, 1e-12)) / (2 * np.pi)      # M f monotonizada
    del t, h, sdb
    lnf = np.log(f_s)
    lnf_mid = 0.5 * (lnf[1:] + lnf[:-1])
    lnb = np.log(bordas_mf)
    T = [np.ones_like(lnf)] + [degrau(lnf, e) for e in lnb[1:]]
    Tm = [np.ones_like(lnf_mid)] + [degrau(lnf_mid, e) for e in lnb[1:]]
    wb = [T[j] - T[j + 1] for j in range(nb - 1)] + [T[-1]]
    wbm = [Tm[j] - Tm[j + 1] for j in range(nb - 1)] + [Tm[-1]]
    dS = np.diff(sd)
    ud = [np.concatenate([[0.0], np.cumsum(wm * dS)]) for wm in wbm]           # complexo (h_+ - i h_x)
    us = [1j * w * hB for w in wb]                         # Re(i hB) = -Im(hB) = h_x (magnetica)
    dts = np.diff(ts)
    # valores das bandas suaves (deslocamento = Re do fim; spin = int h_x dt)
    Vd_suave = np.array([u[-1].real for u in ud])
    hx = -np.imag(hB)
    Vs_suave = np.array([np.sum(0.5 * (w[1:] * hx[1:] + w[:-1] * hx[:-1]) * dts) for w in wb])
    log("  series e particao: %.0f s ; soma das bandas suaves: desl %.6e (janela %.6e), spin %.6e s (janela %.6e)"
        % (time.time() - t1, Vd_suave.sum(), Y[0, 0], Vs_suave.sum(), Y[0, 1]))
    log("  bandas suaves / nitidas - 1: desl %s" % " ".join("%+.0e" % z for z in (Vd_suave / Vb[:, 0] - 1)[::6]))
    log("                               spin %s" % " ".join("%+.0e" % z for z in (Vs_suave / Vb[:, 1] - 1)[::6]))
    out = dict(bordas_hz=bordas_hz, bordas_mf=bordas_mf, Y=Y, dY=dY, Vb=Vb, dVb=dVb, Vd_suave=Vd_suave,
               Vs_suave=Vs_suave, par=np.array([par[n] for n in C.NOMES[:6]]))
    for det in DETS:
        t2 = time.time()
        Gd = gram(ud, ts, det)
        Gs = gram(us, ts, det)
        snr_d = O.snr2(ts, sd, det, 5.0)
        snr_s = O.snr2(ts, 1j * hB, det, 5.0)
        out["Gd_" + det] = Gd
        out["Gs_" + det] = Gs
        log("  %s: SNR deslocamento: serie %.4f, sqrt(soma G) %.4f, sqrt(soma diag) %.4f ; spin (x): serie %.4f, "
            "sqrt(soma G) %.4f, sqrt(soma diag) %.4f (%.0f s)"
            % (det, snr_d, np.sqrt(Gd.sum()), np.sqrt(np.trace(Gd)), snr_s, np.sqrt(Gs.sum()), np.sqrt(np.trace(Gs)),
               time.time() - t2))
        log("     SNR por banda (desl): " + " ".join("%.2g" % z for z in np.sqrt(np.diag(Gd))[::4]))
        log("     SNR por banda (spin): " + " ".join("%.2g" % z for z in np.sqrt(np.diag(Gs))[::4]))
        # SNR com fmin = 10 Hz, para comparar com L00
        log("     (fmin = 10 Hz: desl %.4f, spin %.4f)" % (O.snr2(ts, sd, det, 10.0), O.snr2(ts, 1j * hB, det, 10.0)))
    del ud, us, sd, hB
    np.savez(os.path.join(RAIZ, "resultados", "exp23_prep_%s.npz" % nome), **out)
    log("  (%.0f s)" % (time.time() - t0))
    with open(os.path.join(RAIZ, "resultados", "exp23_prep_%s.txt" % nome), "w") as fh:
        fh.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        preparar_fonte(nome)
