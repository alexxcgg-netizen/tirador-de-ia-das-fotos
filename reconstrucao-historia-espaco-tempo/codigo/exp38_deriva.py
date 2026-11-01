"""exp38 (L19), alternativa: atraso de centroide com a deriva da inspiral removida por um ajuste.

Hipotese de trabalho: a deriva de D = RN - fluxo antes da fusao e um erro de normalizacao da taxa do (2,0) do
substituto (D ~ beta [S(u) - S(u_s)] + gamma na inspiral). Ajusta beta, gamma em [u_s, u_a] (u_a = -60 M, antes
do transiente da fusao), subtrai o ajuste de D em toda a janela e recalcula o atraso de centroide
    delta = -[int D' du - u_f D'(u_f)] / Delta R.
Variantes: u_s = -1000, -500, -300 M; ajuste so com gamma (deslocamento constante) ou com beta e gamma; com e sem
normalizacao final dos degraus. Usa as series guardadas pelo exp38 (q = 1, q = 4, sistema A).
Saida: resultados/exp38_deriva.txt
"""
import os

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
ser = np.load(os.path.join(RES, "exp38_series.npz"))
nomes = sorted({k.rsplit("_", 1)[0] for k in ser.files})
linhas = ["exp38_deriva: atraso de centroide (l = 2) com a deriva da inspiral ajustada e removida",
          "colunas: u_s, u_a, modelo da deriva -> beta, gamma/desl, delta (M) ; delta_ord = (3/2) M_f/Dfrak(2) ~ 0.48 M"]
for nome in nomes:
    u = ser[nome + "_u"].astype(float)
    R = ser[nome + "_R2"].astype(float)
    S = ser[nome + "_S2"].astype(float)
    linhas.append("")
    linhas.append(nome)
    for us in (-1000.0, -500.0, -300.0):
        s = u >= us
        t, r, x = u[s], R[s] - np.interp(us, u, R), S[s] - np.interp(us, u, S)
        D = r - x
        for ua in (-60.0, -100.0):
            a = t <= ua
            for modelo in ("gamma", "beta+gamma"):
                if modelo == "gamma":
                    A = np.ones((a.sum(), 1))
                    cf, *_ = np.linalg.lstsq(A, D[a], rcond=None)
                    Dfit = cf[0] * np.ones_like(D)
                    beta, gam = 0.0, cf[0]
                else:
                    A = np.stack([x[a], np.ones(a.sum())], axis=1)
                    cf, *_ = np.linalg.lstsq(A, D[a], rcond=None)
                    Dfit = cf[0] * x + cf[1]
                    beta, gam = cf
                Dp = D - Dfit
                area = np.trapezoid(Dp, t)
                delta = -(area - t[-1] * Dp[-1]) / r[-1]
                # variante normalizada: forca D'(u_f) = 0 escalando o fluxo corrigido
                xc = x + Dfit
                lam = r[-1] / xc[-1]
                Dn = r - lam * xc
                delta_n = -(np.trapezoid(Dn, t)) / r[-1]
                linhas.append("  u_s %6.0f u_a %5.0f %-10s: beta %+.3e gamma/desl %+.2e -> delta %+.3f M ; "
                              "normalizado %+.3f M ; D'(fim)/desl %+.1e"
                              % (us, ua, modelo, beta, gam / r[-1], delta, delta_n, Dp[-1] / r[-1]))
with open(os.path.join(RES, "exp38_deriva.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
print("\n".join(linhas))
