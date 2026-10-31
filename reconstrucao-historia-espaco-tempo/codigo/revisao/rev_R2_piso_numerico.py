"""Revisao R2: piso numerico do nivel A, simetria por componente e membros da familia perto de A.

1) Discretizacao do inicio da janela. O substituto devolve a onda numa grade de passo dt = 0.25 M que comeca
   no primeiro ponto depois de f_low; quando M muda, o primeiro ponto salta de dt e as memorias saltam.
   Varre M_A (1 + e) com passos de 5e-7 e mede os saltos (spin e giroscopica sao as mais sensiveis).
2) Os pares do exp07 recalculados com dt = 0.125 M (A e B com o mesmo dt): a coincidencia de 1e-10 se mantem?
3) Parte impar em chi_a por multipolo (q = 1, chi_s = +0.3 e -0.5, d = 0.1), niveis A e C.
4) Membros da familia degenerada perto de A (q_B = 1.1, 1.3, 1.5 com chi2_B = -0.2): match e rho_crit, para
   mostrar que o rho_crit nao e limitado ao longo da familia (ela passa por A).
Saida: resultados/revisao/rev_R2_piso_numerico.txt
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import rev_R2_comum as C                                # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
F = 10.0
linhas = []
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def fis(par, dt=0.25, nivel="A"):
    mem, aux, t, h = B.memorias_fisicas(par["q"], par["c1"], par["c2"], par["M"], F, nivel=nivel, dt=dt)
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"]), len(t)


dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A = dados["A"]

log("1) Saltos das memorias de A (nivel A) com M -> M (1 + e), e de 0 a 3e-5 em passos de 5e-7.")
log("   As escalas triviais (M/D, M^2/D, (M/D)^2) sao removidas: compara-se d, s, c, g adimensionais.")
es = np.arange(0, 3.0e-5 + 1e-12, 5e-7)
serie_v, serie_n = [], []
for e in es:
    par = dict(A, M=A["M"] * (1 + e))
    v, n = fis(par)
    pot = {"deslocamento": 1, "spin": 2, "cm": 2, "giroscopica": 2}
    serie_v.append([v[k] / (1 + e) ** pot[k] for k in B.TIPOS])
    serie_n.append(n)
serie_v = np.array(serie_v)
rel = serie_v / serie_v[0] - 1
saltos = [i for i in range(1, len(es)) if serie_n[i] != serie_n[i - 1]]
log("   n amostras ao longo da varredura: %s" % sorted(set(serie_n)))
for i in saltos:
    d = rel[i] - rel[i - 1]
    log("   salto entre e = %.1e e %.1e: n %d -> %d ; variacao das memorias no passo: %s"
        % (es[i - 1], es[i], serie_n[i - 1], serie_n[i], " ".join("%s %+.2e" % (k[:4], x) for k, x in zip(B.TIPOS, d))))
sem = [i for i in range(1, len(es)) if i not in saltos]
dmax = np.max(np.abs(np.array([rel[i] - rel[i - 1] for i in sem])), axis=0)
log("   maior variacao num passo SEM salto: %s" % " ".join("%s %.2e" % (k[:4], x) for k, x in zip(B.TIPOS, dmax)))

log("")
log("2) Pares do exp07 com dt = 0.25 M (como no exp07) e dt = 0.125 M (A e B no mesmo dt), nivel A.")
alvo = {}
for dt in (0.25, 0.125):
    alvo[dt] = fis(A, dt)[0]
for p in dados["pares"]:
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    out = []
    for dt in (0.25, 0.125):
        v, n = fis(par, dt)
        out.append(max(abs(v[k] / alvo[dt][k] - 1) for k in B.TIPOS))
    log("   par (%.0f, %+.1f): delta com dt 0.25 = %.1e ; com dt 0.125 = %.1e" % (p["qB"], p["c2B"], out[0], out[1]))
mudA = max(abs(alvo[0.125][k] / alvo[0.25][k] - 1) for k in B.TIPOS)
log("   memorias de A: variacao relativa maxima entre dt 0.25 e 0.125: %.1e (%s)"
    % (mudA, " ".join("%s %+.1e" % (k[:4], alvo[0.125][k] / alvo[0.25][k] - 1) for k in B.TIPOS)))

log("")
log("3) Parte impar em chi_a por multipolo, q = 1, d = 0.1: |[v(+d) - v(-d)]/2| / |v(0)| e parte par.")
for chi_s in (-0.5, 0.3):
    d = 0.1
    vv = {}
    for c1, c2, nome in ((chi_s, chi_s, "0"), (chi_s + d, chi_s - d, "+"), (chi_s - d, chi_s + d, "-")):
        t, h = B.gerar(1.0, c1, c2)
        vv[nome] = {n: B.vetor(B.memorias(1.0, c1, c2, nivel=n, t=t, h=h)[0])[0] for n in ("A", "C")}
    for n in ("A", "C"):
        imp = np.abs((vv["+"][n] - vv["-"][n]) / 2 / vv["0"][n])
        par = np.abs(((vv["+"][n] + vv["-"][n]) / 2 - vv["0"][n]) / vv["0"][n])
        log("   chi_s %+.1f nivel %s: impar %s" % (chi_s, n, " ".join("%s %.1e" % (k, x) for k, x in zip(NOMES, imp))))
        log("   %s par   %s" % (" " * 15, " ".join("%s %.1e" % (k, x) for k, x in zip(NOMES, par))))

log("")
log("4) Membros da familia (mesmas 4 memorias de A no observador, nivel A) perto de A: chi2_B = -0.2.")
alvo07 = dados["alvo"]
lista = B.lista_osc() + B.MODOS_M0
tA, hA = B.gerar(A["q"], A["c1"], A["c2"], f0=A["M"] * Dt.MSUN_S * F)
tsA, sA = Dt.strain_observador(tA, hA, lista, A["M"], A["D"], A["iota"])
for qB in (1.1, 1.3, 1.5):
    par, r = E7.resolver(alvo07, qB, -0.2, (A["iota"], 0.3, 65.0))
    tB, hB = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * F)
    tsB, sB = Dt.strain_observador(tB, hB, lista, par["M"], par["D"], par["iota"])
    for psd in ("aLIGO", "ET"):
        c = C.comparar(tsA, sA, tsB, sB, psd, F, up=16)
        k = C.criterios(c)
        log("   q_B %.1f: M %.3f chi1 %+.4f D %.2f iota %.2f graus | residuo %.1e | %-5s match %.5f SNR_B/SNR_A %.4f "
            "rho_crit igual %.1f exato %.1f"
            % (qB, par["M"], par["c1"], par["D"], np.degrees(par["iota"]), r, psd, c["match"], k["r"],
               k["rc_igual"], k["rc_exato"]))
    del tB, hB, tsB, sB
with open(os.path.join(RES, "revisao", "rev_R2_piso_numerico.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
