"""Verificacao D8 (L19): refaz, a partir das series guardadas (resultados/exp38_series.npz), o teste pontual, o
melhor deslocamento e a identificacao do transiente com o QNM (2,0,0), mudando o inicio do ajuste e comparando
com hipoteses falsas (frequencia do (2,2,0), exponencial sem oscilacao, (2,0,0) + sobretom (2,0,1)).
Tambem: a parte da variancia de D em [pico, +100 M] (nao so u >= 16 M) explicada pelo QNM.
"""
import os
import numpy as np
from scipy.optimize import least_squares, minimize_scalar

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "..", "resultados")
d = np.load(os.path.join(RES, "exp38_series.npz"))
SIS = {"q1.0_+0.0_+0.0": (1.0, 0.0, 0.0), "q4.0_+0.0_+0.0": (4.0, 0.0, 0.0), "q1.2_+0.3_-0.2": (1.2, 0.3, -0.2)}


def remanescente(q, c1, c2):
    import qnm
    import surfinBH
    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    mf = float(fit.mf(q, [0, 0, c1], [0, 0, c2])[0])
    chif = float(fit.chif(q, [0, 0, c1], [0, 0, c2])[0][2])
    w = {}
    for (l, m, n) in ((2, 0, 0), (2, 0, 1), (2, 2, 0)):
        w[(l, m, n)] = complex(qnm.modes_cache(s=-2, l=l, m=m, n=n)(a=abs(chif))[0]) / mf
    return mf, chif, w


def frac_var(y, model_fun, p0):
    r = least_squares(lambda p: y - model_fun(p), p0)
    return 1 - np.var(r.fun) / np.var(y), r.x


for nome, (q, c1, c2) in SIS.items():
    u = d[nome + "_u"].astype(float)
    S = d[nome + "_S2"].astype(float)
    R = d[nome + "_R2"].astype(float)
    taxa = d[nome + "_taxa2"].astype(float)
    D = R - S
    mf, chif, w = remanescente(q, c1, c2)
    w200, w201, w220 = w[(2, 0, 0)], w[(2, 0, 1)], w[(2, 2, 0)]
    print("\n%s: M_f %.4f chi_f %.4f ; w200 %.4f %.4f ; w220 %.4f %.4f" % (nome, mf, chif, w200.real, w200.imag, w220.real, w220.imag))
    desl = S[-1]
    # teste pontual
    s = (u >= -60) & (u <= 60)
    Dl = D[s] - D[s][0]
    A_ = np.stack([np.ones(s.sum()), -taxa[s]], axis=1)
    cf, *_ = np.linalg.lstsq(A_, Dl, rcond=None)
    res = Dl - A_ @ cf
    print("  pontual: max|D|/desl %.3f ; (M_f/2) max dS/du / desl %.4f ; delta ajustado %.2f M R2 %.3f"
          % (np.max(np.abs(Dl)) / desl, 0.5 * mf * np.max(np.abs(taxa[s])) / desl, cf[1],
             1 - np.sum(res ** 2) / np.sum((Dl - Dl.mean()) ** 2)))
    upk = u[np.argmax(np.abs(np.where((u > -20) & (u < 60), D - D[np.searchsorted(u, -60)], 0)))]
    print("  pico de |D| em u = %.2f M" % upk)
    for t0 in (upk, 8.0, 12.0, 16.0, 20.0, 30.0):
        sel = (u >= t0) & (u <= t0 + 150)
        tt, y = u[sel] - t0, D[sel]
        out = []
        for rot, w_ in (("200", w200), ("220(falso)", w220)):
            f = lambda p, w_=w_: p[0] + p[1] * np.exp(w_.imag * tt) * np.cos(w_.real * tt + p[2])
            fv, _ = frac_var(y, f, [y[-1], np.max(np.abs(y - y[-1])), 0.0])
            out.append("%s %.3f" % (rot, fv))
        fexp = lambda p: p[0] + p[1] * np.exp(-p[2] * tt)
        fv, _ = frac_var(y, fexp, [y[-1], y[0] - y[-1], 0.1])
        out.append("exp sem oscilacao %.3f" % fv)
        f2 = lambda p: (p[0] + p[1] * np.exp(w200.imag * tt) * np.cos(w200.real * tt + p[2])
                        + p[3] * np.exp(w201.imag * tt) * np.cos(w201.real * tt + p[4]))
        fv2, _ = frac_var(y, f2, [y[-1], np.max(np.abs(y - y[-1])), 0.0, 0.0, 0.0])
        out.append("200+201 %.3f" % fv2)
        flivre = lambda p: p[0] + p[1] * np.exp(-p[4] * tt) * np.cos(p[3] * tt + p[2])
        fvl, xl = frac_var(y, flivre, [y[-1], np.max(np.abs(y - y[-1])), 0.0, w200.real, -w200.imag])
        out.append("livre %.3f (w %.4f, g %.4f)" % (fvl, xl[3], xl[4]))
        f200 = lambda p: p[0] + p[1] * np.exp(w200.imag * tt) * np.cos(w200.real * tt + p[2])
        _, x200 = frac_var(y, f200, [y[-1], np.max(np.abs(y - y[-1])), 0.0])
        out.append("A/desl em t0: %.3f" % (abs(x200[1]) / desl))
        print("  inicio %.1f M: " % t0 + " ; ".join(out))
    # melhor deslocamento temporal
    s2 = (u >= -100) & (u <= 100)

    def custo(dd):
        Ssh = np.interp(u[s2] - dd, u, S)
        A2 = np.stack([Ssh, np.ones(s2.sum())], axis=1)
        c2_, *_ = np.linalg.lstsq(A2, R[s2], rcond=None)
        return float(np.sum((R[s2] - A2 @ c2_) ** 2))
    r_ = minimize_scalar(custo, bounds=(-10, 20), method="bounded", options=dict(xatol=1e-4))
    print("  melhor deslocamento %.2f M ; em [-100, 30]: " % r_.x, end="")
    s2 = (u >= -100) & (u <= 30)
    print("%.2f M" % minimize_scalar(custo, bounds=(-10, 20), method="bounded").x)
