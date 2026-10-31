"""Experimento 14: os pares degenerados do exp07 sob duas perguntas de refutacao.

1. A degenerescencia depende da janela? As memorias de spin, CM e giroscopica acumulam desde o
   inicio da janela (f = 10 Hz no exp07). Um observador com outra banda (5 Hz para ET, 20 Hz para
   detectores antigos) mede outras memorias. Recalculo A e B (os pares com residuo < 1e-6 no nivel A)
   com a janela comecando em 5, 7, 15 e 20 Hz e meco a diferenca maxima.
2. O observavel de fase Omega_mem(u) = (d h20/du) / (C |h30|) (exp09) separa os pares? Calculo
   Omega_mem com os modos m = 0 de RN (nivel C) para A e para B, em tempo fisico (s antes do pico), e
   comparo a diferenca A - B com o erro do proprio estimador (Omega_mem - Omega verdadeira).
Saida: resultados/exp14_janela_e_fase_pares.txt
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
C_OM = 5.039682                                         # calibracao do exp09 (modo (2,2) puro)
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


dados = json.load(open(os.path.join(AQUI, "..", "resultados", "exp07_pares.json")))
A = dados["A"]
pares = [p for p in dados["pares"] if max(abs(x) for x in p["dif"].values()) < 1e-6]


def quatro(par, f_ini):
    mem, _, _, _ = B.memorias_fisicas(par["q"], par["c1"], par["c2"], par["M"], f_ini, nivel="A")
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"])


log("1. Dependencia da janela (nivel A): diferenca relativa B - A de cada memoria quando a janela comeca em f_ini")
alvos = {f: quatro(A, f) for f in (5.0, 7.0, 10.0, 15.0, 20.0)}
for p in pares:
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    partes = []
    for f, alvo in alvos.items():
        v = quatro(par, f)
        d = {k: (v[k] - alvo[k]) / abs(alvo[k]) for k in B.TIPOS}
        partes.append("%2.0f Hz: desl %+.1e spin %+.1e cm %+.1e giro %+.1e" % (f, d["deslocamento"], d["spin"], d["cm"], d["giroscopica"]))
    log("  par q_B = %.1f, chi2_B = %+.1f:" % (p["qB"], p["c2B"]))
    for s in partes:
        log("     " + s)

log()
log("2. Omega_mem(t) = (d h20/dt)/(C |h30|) com os modos m = 0 de RN (NRHybSur3dq8_CCE, nivel C), tempo antes do pico")


def omegas(par):
    Ms = par["M"] * Dt.MSUN_S
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * 10.0, dt=0.25)
    dt = t[1] - t[0]
    om_mem = np.gradient(h[(2, 0)].real, dt) / (C_OM * np.abs(h[(3, 0)]))
    om_ver = -0.5 * np.gradient(np.unwrap(np.angle(h[(2, 2)])), dt)
    tp = t[np.argmax(np.abs(h[(2, 2)]))]
    return (t - tp) * Ms, om_mem / Ms, om_ver / Ms          # segundos, rad/s


tA, mA, vA = omegas(A)
instantes = [-2.0, -1.0, -0.5, -0.2, -0.1, -0.05]
for p in pares:
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"])
    tB, mB, vB = omegas(par)
    partes = []
    for ti in instantes:
        if ti < max(tA[0], tB[0]):
            continue
        a_mem, b_mem = np.interp(ti, tA, mA), np.interp(ti, tB, mB)
        a_ver, b_ver = np.interp(ti, tA, vA), np.interp(ti, tB, vB)
        partes.append("t = %+.2f s: Omega_mem A %.1f, B %.1f rad/s (B/A - 1 = %+.3f) | verdadeira B/A - 1 = %+.3f | erro do estimador A %+.3f, B %+.3f"
                      % (ti, a_mem, b_mem, b_mem / a_mem - 1, b_ver / a_ver - 1, a_mem / a_ver - 1, b_mem / b_ver - 1))
    log("  par q_B = %.1f, chi2_B = %+.1f (M_B = %.2f):" % (p["qB"], p["c2B"], p["M"]))
    for s in partes:
        log("     " + s)
with open(os.path.join(AQUI, "..", "resultados", "exp14_janela_e_fase_pares.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
