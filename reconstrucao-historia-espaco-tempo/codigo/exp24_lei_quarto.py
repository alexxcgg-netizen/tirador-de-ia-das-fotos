"""Experimento 24c: a memoria na banda nao e um degrau puro; correcao (M f)^(1/4) da cauda da inspiral.

Derivacao [D] (ordem dominante PN, Favata 2009): na inspiral h+_obs(tau) = Q eta x(tau), x = (1/4)(eta tau/5M)^(-1/4),
tau = t_c - t, Q = 8 sqrt(pi/5) [5/(14 sqrt6) Y20(iota) + 1/(504 sqrt2) Y40(iota)]. A taxa e (A'/4) tau^(-5/4),
A' = Q eta (1/4)(5M/eta)^(1/4), e com int_0^inf tau^(s-1)(e^{i w tau} - 1) d tau = Gamma(s)(-i w)^(-s) (s = -1/4):
    s~(f) = [Delta H_tot + (A'/4) Gamma(-1/4) (-2 pi i f)^(1/4) + O(f)] / (2 pi i f)      (referencia em t_c)
Delta H_tot = memoria TOTAL (desde x = 0): o inicio da janela se cancela entre o degrau e a cauda. Logo
    T(f) = 2 pi i f s~(f) / Delta H_tot = 1 - c (2 pi f M)^(1/4) e^(-i pi/8) + ...,   c = |Gamma(-1/4)| (5/eta)^(1/4)/(16 x*)
com x* = Delta H_tot/(Q eta). A forma na banda depende dos parametros intrinsecos so pela combinacao c M^(1/4), isto
e, por M/(eta x*^4) (no regime f M << 1). Teste: |T| numerico (espectro exato da serie nula) contra a previsao.
Saida: resultados/exp24_lei_quarto.txt
"""
import os
import sys

import numpy as np
from scipy.special import gamma

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp24_comum as C                                   # noqa: E402
import observaveis as O                                   # noqa: E402
from harmonicos import sYlm                               # noqa: E402

LINHAS = []


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


def main():
    iota = np.radians(50.0)
    Y = C._Ylist(iota)
    Q = 8 * np.sqrt(np.pi / 5) * (5 / (14 * np.sqrt(6)) * Y[0] + 1 / (504 * np.sqrt(2)) * Y[2])
    log("Teste da lei (M f)^(1/4): T(F) = 2 pi i F S+(F)/Delta H_tot, iota = 50 graus, janela desde M f0 = 0.0016.")
    log("Previsao: 1 - |T| ~ c cos(pi/8) (2 pi F)^(1/4), c = |Gamma(-1/4)| (5/eta)^(1/4)/(16 x*), x* = Delta H_tot/(Q eta).")
    casos = [(1.2, 0.3, -0.2), (1.0, 0.0, 0.0), (4.0, 0.0, 0.0), (1.0, 0.8, 0.8), (1.0, -0.8, -0.8), (3.0, 0.5, -0.5)]
    Mref = 20.0
    saida = {}
    fi = 0.0016 / (Mref * C.MSUN_S)
    for (q, c1, c2) in casos:
        eta = q / (1 + q) ** 2
        t, h, ti = O.gerar_janela(q, c1, c2, Mref, fi)
        mem, aux = O.memorias_observaveis(q, c1, c2, Mref, fi, t=t, h=h, t_i=ti, desl="total")
        memw, _ = O.memorias_observaveis(q, c1, c2, Mref, fi, t=t, h=h, t_i=ti, desl="janela")
        E = C.EspectroMemoria(q, c1, c2, Mref, fi, N=2 ** 20, Fmax=0.3, T_tap=10000.0, t=t, h=h, t_i=ti)
        del t, h
        dHtot = sum(float(np.real(mem["deslocamento"][(L, 0)])) * float(np.real(sYlm(-2, L, 0, iota, 0.0)))
                    for L in range(2, 9) if (L, 0) in mem["deslocamento"])
        dHw = float(np.real(E.final @ Y))
        xs = dHtot / (Q * eta)
        c = abs(gamma(-0.25)) * (5 / eta) ** 0.25 / (16 * xs)
        hp = E.Sp_ @ Y
        F = E.F
        T = 2j * np.pi * F * hp / dHtot
        log("")
        log("q %.1f chi (%.1f, %.1f): Delta H_tot = %.5f (janela %.5f) ; x* = %.4f ; c previsto = %.4f"
            % (q, c1, c2, dHtot, dHw, xs, c))
        Fs = np.array([1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2])
        lin = []
        for F0 in Fs:
            j = int(np.argmin(np.abs(F - F0)))
            prev = c * np.cos(np.pi / 8) * (2 * np.pi * F[j]) ** 0.25
            lin.append((F[j], 1 - abs(T[j]), prev))
        for Fj, num, prev in lin:
            log("   M f = %.1e: 1-|T| numerico %.4f ; previsto (ordem dominante) %.4f ; razao %.3f"
                % (Fj, num, prev, num / prev))
        sel = (F > 1e-4) & (F < 1e-3)
        a, b = np.polyfit(np.log(2 * np.pi * F[sel]), np.log(np.clip(1 - np.abs(T[sel]), 1e-12, None)), 1)
        log("   inclinacao log-log de 1-|T| em M f in [1e-4, 1e-3]: %.3f (previsto 0.25)" % a)
        sub = np.unique(np.geomspace(5e-5, 0.2, 120).astype(float))
        jj = np.unique([int(np.argmin(np.abs(F - x))) for x in sub])
        saida["q%.1f_c%.1f_%.1f" % (q, c1, c2)] = dict(F=F[jj].tolist(), um_menos_T=(1 - np.abs(T[jj])).tolist(),
                                                     c=c, xs=xs, inclinacao=a, dHtot=dHtot, dHw=dHw)
        del E
    import json
    with open(os.path.join(C.RES, "exp24_lei_quarto.json"), "w") as fh:
        json.dump(saida, fh)
    with open(os.path.join(C.RES, "exp24_lei_quarto.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")


if __name__ == "__main__":
    main()
