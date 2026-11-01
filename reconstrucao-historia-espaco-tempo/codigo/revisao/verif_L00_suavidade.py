"""Verificacao L00 (2): suavidade das memorias de janela de observaveis.py (sem escada) em M, q, chi1, chi2.

Independente dos testes do D0 (que usam 13 valores de M em 1.2e-5):
  (a) varredura em M de 0 a 4e-5 (81 valores; t_i atravessa ~7 nos da rede): ajuste polinomial de grau 3
      em e = Delta M / M e residuo maximo; niveis A e C (m = 0) e todos os m (phi = 0.8 rad, nivel A);
  (b) o mesmo em q (passo 2e-6) e em chi1 (passo 2e-6);
  (c) dependencia do inicio auxiliar FRAC_INICIO (0.80 ... 0.97): o gwsurrogate trunca a grade esparsa em
      initIdx (funcao de f_low) antes de interpolar, o que poderia criar outra escada;
  (d) a correcao de fase: |dphi| (fase do (2,2) em t_i antes da correcao) e a fase residual depois, numa
      grade de M e q; |dphi| perto de pi trocaria o sinal dos m impares (ambiguidade de pi);
  (e) jacobiano por diferencas centrais com passos h, h/2, h/4: razao das diferencas sucessivas (4 se suave).
Saida: resultados/revisao/verif_L00_suavidade.txt
"""
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import observaveis as O                                 # noqa: E402
from deteccao import MSUN_S                             # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_suavidade.txt")
L = []
T0 = time.time()
P0 = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, F=10.0, iota=np.radians(50.0))


def log(s=""):
    print(s, flush=True)
    L.append(s)


def valores(q, c1, c2, M, nivel="A", todos_m=False, phi=0.0):
    t, h, ti = O.gerar_janela(q, c1, c2, M, P0["F"])
    m, aux = O.memorias_observaveis(q, c1, c2, M, P0["F"], nivel=nivel, t=t, h=h, t_i=ti, todos_m=todos_m)
    del t, h
    v = O.no_observador_completo(m, P0["iota"], phi)
    return np.array([v[k] for k in O.TIPOS] + [aux["M_f"]]), ti


def residuo_poly(x, V, grau=3):
    """max |V - ajuste| / |V| por coluna, com x normalizado."""
    xn = (x - x.mean()) / (x.max() - x.min())
    out = []
    for j in range(V.shape[1]):
        c = np.polyfit(xn, V[:, j], grau)
        out.append(np.max(np.abs(V[:, j] - np.polyval(c, xn))) / np.max(np.abs(V[:, j])))
    return np.array(out)


def fmt(v, f="%.1e"):
    return " ".join("%s %s" % (k[:4], f % x) for k, x in zip(list(O.TIPOS) + ["M_f"], v))


def varredura(nome, xs, fun):
    V, T = [], []
    for x in xs:
        v, ti = fun(x)
        V.append(v)
        T.append(ti)
    V, T = np.array(V), np.array(T)
    r = residuo_poly(xs, V)
    d2 = np.abs(np.diff(V, 2, axis=0)).max(axis=0) / np.abs(V).max(axis=0)
    nos = len(np.unique(np.floor(T / 0.25)))
    log("  %-38s t_i varia %.3f M (%d intervalos da rede): residuo grau 3 %s" % (nome, np.ptp(T), nos - 1, fmt(r)))
    log("  %-38s max |2a dif.|/|V| %s" % ("", fmt(d2)))
    return V


log("(a) varredura em M = 65 (1 + e), e = 0 .. 4e-5, 81 valores (sistema A, observador iota = 50 graus)")
es = np.linspace(0, 4e-5, 81)
varredura("nivel A, m = 0", es, lambda e: valores(P0["q"], P0["c1"], P0["c2"], P0["M"] * (1 + e)))
varredura("nivel C, m = 0", es, lambda e: valores(P0["q"], P0["c1"], P0["c2"], P0["M"] * (1 + e), nivel="C"))
varredura("nivel A, todos os m, phi = 0.8", es,
          lambda e: valores(P0["q"], P0["c1"], P0["c2"], P0["M"] * (1 + e), todos_m=True, phi=0.8))
log("  (%.0f s)" % (time.time() - T0))
# contraste: binarias na mesma varredura (so nivel A, m = 0)
V = []
for e in es[::2]:
    m, aux, t, h = B.memorias_fisicas(P0["q"], P0["c1"], P0["c2"], P0["M"] * (1 + e), P0["F"])
    del t, h
    v = B.no_observador(m, P0["iota"])
    V.append([v[k] for k in O.TIPOS] + [aux["M_f"]])
V = np.array(V)
log("  contraste binarias (41 valores): residuo grau 3 %s" % fmt(residuo_poly(es[::2], V)))
log("  (%.0f s)" % (time.time() - T0))

log("")
log("(b) varreduras em q e chi1 (nivel A; m = 0 e todos os m com phi = 0.8)")
qs = P0["q"] + np.arange(41) * 2e-6
varredura("q = 1.2 + k 2e-6, m = 0", qs, lambda q: valores(q, P0["c1"], P0["c2"], P0["M"]))
varredura("q = 1.2 + k 2e-6, todos os m", qs, lambda q: valores(q, P0["c1"], P0["c2"], P0["M"], todos_m=True, phi=0.8))
cs = P0["c1"] + np.arange(41) * 2e-6
varredura("chi1 = 0.3 + k 2e-6, m = 0", cs, lambda c: valores(P0["q"], c, P0["c2"], P0["M"]))
varredura("chi1 = 0.3 + k 2e-6, todos os m", cs, lambda c: valores(P0["q"], c, P0["c2"], P0["M"], todos_m=True, phi=0.8))
log("  (%.0f s)" % (time.time() - T0))

log("")
log("(c) inicio auxiliar FRAC_INICIO (onda gerada desde FRAC f0): multipolos (todos os m) contra FRAC = 0.9")
ref, aref = O.memorias_observaveis(P0["q"], P0["c1"], P0["c2"], P0["M"], P0["F"], todos_m=True)
for M in (65.0, 30.0, 120.0):
    ref, aref = O.memorias_observaveis(P0["q"], P0["c1"], P0["c2"], M, P0["F"], todos_m=True)
    t0, h0, ti0 = O.gerar_janela(P0["q"], P0["c1"], P0["c2"], M, P0["F"])
    txt = []
    for fr in (0.80, 0.85, 0.88, 0.93, 0.95, 0.97):
        O.FRAC_INICIO = fr
        t1, h1, ti1 = O.gerar_janela(P0["q"], P0["c1"], P0["c2"], M, P0["F"])
        m1, a1 = O.memorias_observaveis(P0["q"], P0["c1"], P0["c2"], M, P0["F"], todos_m=True, t=t1, h=h1, t_i=ti1)
        # modos nos instantes comuns t >= t_i - 10
        j0 = int(np.searchsorted(t0, ti0 - 10.0))
        j1 = int(np.searchsorted(t1, t0[j0] - 1e-9))
        n = min(len(t0) - j0, len(t1) - j1)
        dm = max(np.max(np.abs(h1[k][j1:j1 + n] - h0[k][j0:j0 + n])) / np.max(np.abs(h0[k])) for k in h0)
        dt_ = abs(t1[j1] - t0[j0])
        dmem = max(max(abs(m1[tp][k] - ref[tp][k]) for k in ref[tp]) / max(abs(v) for v in ref[tp].values())
                   for tp in O.TIPOS)
        txt.append("%.2f: modos %.0e mem %.0e ti %.0e" % (fr, dm, dmem, ti1 - ti0))
        del t1, h1
        O.FRAC_INICIO = 0.9
    del t0, h0
    log("  M = %5.1f (desalinh. de rede %.0e): %s" % (M, dt_, " | ".join(txt)))
log("  (%.0f s)" % (time.time() - T0))

log("")
log("(d) fase do (2,2) em t_i antes (dphi) e depois da correcao, grade de M (20..150) e q (1, 1.2, 2, 4, 8)")
sur = B._sur()
pior_dphi, pior_res = 0.0, 0.0
for q in (1.0, 1.2, 2.0, 4.0, 8.0):
    for (c1, c2) in ((0.0, 0.0), (0.6, -0.4), (-0.7, 0.7)):
        for M in (20.0, 35.0, 50.0, 65.0, 80.0, 100.0, 150.0):
            t, h, ti = O.gerar_janela(q, c1, c2, M, P0["F"])
            k = int(np.searchsorted(t, ti))
            fase = np.unwrap(np.angle(h[(2, 2)][k - 30:k + 30]))
            res = O._fase_em(t[k - 30:k + 30], fase, ti, 30)
            res = float(np.angle(np.exp(1j * res)))
            # dphi = res - (fase antes da correcao) : refaz a chamada sem correcao
            f0 = M * MSUN_S * P0["F"]
            hh = sur(q, [0, 0, c1], [0, 0, c2], times=t[k - 30:k + 30], f_low=O.FRAC_INICIO * f0, f_ref=f0,
                     mode_list=[(2, 2)])[1][(2, 2)]
            # obs.: com so (2,2) e menos tempos o refIdx do gwsurrogate e o mesmo (busca na rede dada)
            f2 = O._fase_em(t[k - 30:k + 30], np.unwrap(np.angle(hh)), ti, 30)
            dphi = float(np.angle(np.exp(1j * f2)))
            pior_dphi = max(pior_dphi, abs(dphi))
            pior_res = max(pior_res, abs(res))
            del t, h
log("  max |dphi| = %.3e rad (omega_22 dt em 10 Hz, M = 150: %.3e) ; max |fase residual| = %.1e rad"
    % (pior_dphi, 2 * np.pi * 150 * MSUN_S * 10 * 0.25, pior_res))
log("  (%.0f s)" % (time.time() - T0))

log("")
log("(e) jacobiano por diferencas centrais (nivel A, todos os m, phi = 0.8): D(h) - D(h/2) e D(h/2) - D(h/4)")
base = dict(q=P0["q"], c1=P0["c1"], c2=P0["c2"], M=P0["M"])
for par, h0 in (("M", 1e-3 * 65), ("q", 1e-3), ("c1", 1e-3), ("c2", 1e-3)):
    Ds = []
    for h in (h0, h0 / 2, h0 / 4):
        vp = dict(base)
        vm = dict(base)
        vp[par] += h
        vm[par] -= h
        a = valores(vp["q"], vp["c1"], vp["c2"], vp["M"], todos_m=True, phi=0.8)[0]
        b = valores(vm["q"], vm["c1"], vm["c2"], vm["M"], todos_m=True, phi=0.8)[0]
        Ds.append((a - b) / (2 * h))
    Ds = np.array(Ds)
    r = (Ds[0] - Ds[1]) / (Ds[1] - Ds[2])
    rel = np.abs(Ds[1] - Ds[2]) / np.abs(Ds[2])
    log("  %-2s h = %.1e: razao %s ; |D(h/2) - D(h/4)|/|D| %s" % (par, h0, fmt(r, "%.2f"), fmt(rel)))
log("  (%.0f s)" % (time.time() - T0))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
