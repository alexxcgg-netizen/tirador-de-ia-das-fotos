"""Revisor R3: fisica e numerica de pn_excentrico.py e exp12_excentricas_imr.py.

 (a) modo (2,0) oscilatorio de orbitas excentricas: o SEOBNRv5EHM nao o tem e o exp12 o omite dos fluxos.
     Com o modelo newtoniano (pn_excentrico, que o tem) mede-se quanto ele pesa nas memorias de janela.
 (b) convergencia de pn_excentrico em dt (0.5 -> 0.25) e no numero de pontos de quadratura.
 (c) M_f no exp12: energia de ligacao 1PN de orbita excentrica (frequencia orbital media fixa) contra a circular usada.
 (d) SEOBNRv5EHM: grade de tempo uniforme? ruido sob passos de 1e-6 em M, componente a componente, e se ele vem do
     fim da onda (fusao) ou do comeco (inspiral).
Saida: resultados/revisao/rev_R3_excentricas.txt
"""
import os
import sys
import time

import numpy as np

from rev_R3_comum import B, gram, CalculadoraMemoria, SAIDA, CODIGO

sys.path.insert(0, CODIGO)
import pn_excentrico as PE                              # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp12_excentricas_imr as E12                     # noqa: E402

NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def mem_pn(eta, e0, f0, lista, dt=0.5):
    t, h, r, a, e = PE.modos(eta, e0, f0, dt=dt)
    dt = t[1] - t[0]
    calc = CalculadoraMemoria(lista)
    x0 = (np.pi * f0) ** (2 / 3)
    out, aux = E12.memorias_janela(t, h, lista, calc, eta, x0)
    return B.vetor(out)[0], aux


if __name__ == "__main__":
    t00 = time.time()
    M, q = 65.0, 1.2
    eta = q / (1 + q) ** 2
    f0 = M * Dt.MSUN_S * 10.0
    x0 = (np.pi * f0) ** (2 / 3)
    L_com = [(2, 2), (2, -2), (2, 0)]
    L_sem = [(2, 2), (2, -2)]
    log("(a) modelo newtoniano + Peters (M = 65, q = 1.2, 10 Hz): memorias de janela sem o modo (2,0) oscilatorio, relativas ao caso com ele")
    for e0 in (0.0, 0.1, 0.2, 0.3):
        v1, a1 = mem_pn(eta, e0, f0, L_com)
        v0, a0 = mem_pn(eta, e0, f0, L_sem)
        log("  e0 = %.1f: " % e0 + " ".join("%s %+.1e" % (n, x) for n, x in zip(NOMES, (v0 - v1) / np.abs(v1)))
            + " ; E_janela %+.1e" % ((a0["E_janela"] - a1["E_janela"]) / a1["E_janela"]))
    log("  (%.0f s)" % (time.time() - t00))

    log()
    log("(b) pn_excentrico: dt = 0.5 -> 0.25 (e0 = 0.3, com o (2,0))")
    v1, _ = mem_pn(eta, 0.3, f0, L_com, dt=0.5)
    v2, _ = mem_pn(eta, 0.3, f0, L_com, dt=0.25)
    log("  " + " ".join("%s %+.1e" % (n, x) for n, x in zip(NOMES, (v2 - v1) / np.abs(v1))))
    log("  (%.0f s)" % (time.time() - t00))

    log()
    log("(c) energia de ligacao 1PN, frequencia orbital media fixa: E = (eta x/2)[1 - (3/4 + eta/12) x - 2 x e^2/(1-e^2)]")
    log("    (de n = eps^(3/2)[1 + (eta-15) eps/8] e K = 1 + 3x/(1-e^2), Damour-Deruelle); o exp12 usa a circular")
    for e0 in (0.1, 0.2, 0.3):
        dM = 0.5 * eta * x0 * 2 * x0 * e0 ** 2 / (1 - e0 ** 2)
        log("  e0 = %.1f: M_f(exp12) - M_f(1PN excentrica) = %+.2e (relativo a parte ordinaria de CM: ~%.1e)" % (e0, -dM, dM))

    log()
    log("(d) SEOBNRv5EHM (M = 65, q = 1.2, chi = (0.3, -0.2), 10 Hz)")
    for e0 in (0.0, 0.2):
        vs, vs_ins, ts = [], [], []
        for k in range(4):
            Mk = 65.0 * (1 + k * 1e-6)
            fk = Mk * Dt.MSUN_S * 10.0
            t, h = E12.gerar(1.2, 0.3, -0.2, fk, e0)
            dtt = np.diff(t)
            if k == 0:
                log("  e0 = %.1f: %d pontos, dt = %.6f, max|dt_i - dt|/dt = %.1e, t0 - t_pico = %.0f M"
                    % (e0, len(t), dtt[0], np.max(np.abs(dtt - dtt[0])) / dtt[0], t[0] - t[np.argmax(np.abs(h[(2, 2)]))]))
            etak = eta
            xk = (np.pi * fk) ** (2 / 3)
            out, aux = E12.memorias_janela(t, h, E12.LISTA, E12.calc(), etak, xk)
            vs.append(B.vetor(out)[0])
            tp = t[np.argmax(np.abs(h[(2, 2)]))]
            sel = t < tp - 500
            out2, _ = E12.memorias_janela(t[sel], {kk: vv[sel] for kk, vv in h.items()}, E12.LISTA, E12.calc(), etak, xk)
            vs_ins.append(B.vetor(out2)[0])
            ts.append((t[0], t[-1], tp))
            del t, h
        dv = np.abs(np.diff(vs, axis=0)) / np.abs(vs[0])
        dvi = np.abs(np.diff(vs_ins, axis=0)) / np.abs(vs_ins[0])
        log("    variacao relativa sob dM/M = 1e-6 (onda inteira), max sobre 3 passos: "
            + " ".join("%s %.1e" % (n, x) for n, x in zip(NOMES, dv.max(axis=0))))
        log("    so ate t_pico - 500 M:                                         "
            + " ".join("%s %.1e" % (n, x) for n, x in zip(NOMES, dvi.max(axis=0))))
        log("    (t0, t_fim, t_pico) dos 4 casos: " + "; ".join("(%.2f, %.2f, %.2f)" % z for z in ts))
        log("  (%.0f s)" % (time.time() - t00))
    with open(os.path.join(SAIDA, "rev_R3_excentricas.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
