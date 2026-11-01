"""Verificacao L00, complemento de (2): de onde vem o residuo ~3e-10 das varreduras em q e chi (verif_L00_suavidade),
e se o inicio auxiliar FRAC_INICIO = 0.9 basta quando f0 e maior (janelas desde 20-45 Hz ou M ate 300).

  (a) q = 1.2 + k 2e-6 (41 valores), M = 65, 10 Hz: residuo do ajuste cubico de t_i, de |h22| num instante fixo,
      e da energia de janela sum w |hdot_lm|^2 de cada modo (antes e depois do pico, para o (2,2));
  (b) memorias (todos os m) com FRAC_INICIO = 0.8, 0.9, 0.95 contra 0.6, para (M, f_ini) com f0 de 0.003 a 0.015.
  (c) memorias com todos os m num phi fixo (relativo a fase em t_i) em funcao de M (e = 0..0.03): periodo da
      oscilacao contra o previsto 2 pi / (|m| omega_orb dt_i/de).
Saida: resultados/revisao/verif_L00_ruido.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import observaveis as O                                  # noqa: E402
from deteccao import MSUN_S                              # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_ruido.txt")
L = []


def log(s=""):
    print(s, flush=True)
    L.append(s)


qs = 1.2 + np.arange(41) * 2e-6
xn = (qs - qs.mean()) / np.ptp(qs)


def res(y):
    y = np.array(y)
    c = np.polyfit(xn, y, 3)
    return np.max(np.abs(y - np.polyval(c, xn))) / np.abs(y).max()


Lo = [k for k in B.lista_osc() if k[1] > 0]
E = {k: [] for k in Lo}
Epre, Epos, T, A22 = [], [], [], []
for q in qs:
    t, h, ti = O.gerar_janela(q, 0.3, -0.2, 65.0, 10.0)
    w = O.pesos_janela(t, ti)
    for k in Lo:
        e = w * np.abs(O.derivada(h[k][:, None], 0.25)[:, 0]) ** 2
        E[k].append(np.sum(e))
        if k == (2, 2):
            j0 = int(np.searchsorted(t, 0.0))
            Epre.append(np.sum(e[:j0]))
            Epos.append(np.sum(e[j0:]))
    T.append(ti)
    A22.append(abs(h[(2, 2)][int(np.searchsorted(t, -1000.0))]))
    del t, h
log("(a) q = 1.2 + k 2e-6, k = 0..40 (M = 65, 10 Hz): residuo relativo do ajuste cubico")
log("  t_i %.1e (|t_i| = %.0f M, residuo absoluto %.1e M) ; |h22|(t = -1000 M) %.1e" % (
    res(T), abs(T[0]), res(T) * abs(T[0]), res(A22)))
log("  energia de janela por modo: " + " ; ".join("%s %.1e" % (k, res(E[k])) for k in Lo))
log("  (2,2): antes do pico %.1e ; depois do pico %.1e" % (res(Epre), res(Epos)))

log("")
log("(b) FRAC_INICIO: max dif. relativa dos multipolos (todos os m) contra FRAC = 0.6")


def mem(M, F, fr):
    O.FRAC_INICIO = fr
    try:
        return O.memorias_observaveis(1.2, 0.3, -0.2, M, F, todos_m=True)
    finally:
        O.FRAC_INICIO = 0.9


def dif(ma, mb):
    return max(max(abs(ma[tp][k] - mb[tp][k]) for k in mb[tp]) / max(abs(v) for v in mb[tp].values())
               for tp in O.TIPOS)


for (M, F) in ((65, 10), (120, 10), (65, 20), (65, 30), (200, 10), (65, 45), (300, 10)):
    ref, ar = mem(M, F, 0.6)
    out = []
    for fr in (0.8, 0.9, 0.95):
        m, a = mem(M, F, fr)
        out.append("%.2f: %.0e (t_i %+.0e M)" % (fr, dif(m, ref), a["t_i"] - ar["t_i"]))
    log("  M %3d f_ini %2d Hz (f0 = %.4f, t_i = %8.1f M): %s" % (M, F, M * MSUN_S * F, ar["t_i"], " | ".join(out)))

log("")
log("(c) memorias com todos os m num phi fixo (relativo a fase em t_i) oscilam em M: M = 65 (1 + e), e = 0..0.03")
es = np.linspace(0, 0.03, 61)
V, T = [], []
for e in es:
    t, h, ti = O.gerar_janela(1.2, 0.3, -0.2, 65.0 * (1 + e), 10.0)
    m, a = O.memorias_observaveis(1.2, 0.3, -0.2, 65.0 * (1 + e), 10.0, t=t, h=h, t_i=ti, todos_m=True)
    m0 = {tp: {k: v for k, v in m[tp].items() if k[1] == 0} for tp in O.TIPOS}
    va = O.no_observador_completo(m, np.radians(50.0), 0.8)
    vb = O.no_observador_completo(m0, np.radians(50.0), 0.8)
    V.append([va[tp] / vb[tp] - 1 for tp in O.TIPOS])
    T.append(ti)
    del t, h
V, T = np.array(V), np.array(T)
w_orb = np.pi * 65.0 * MSUN_S * 10.0
taxa = np.polyfit(es[:5], T[:5], 1)[0]
log("  dt_i/de = %.4g M ; omega_orb(t_i) dt_i/de = %.1f rad: periodo previsto em e para |m| = 1: %.4f"
    % (taxa, abs(w_orb * taxa), 2 * np.pi / abs(w_orb * taxa)))
for i, tp in enumerate(O.TIPOS):
    y = V[:, i] - V[:, i].mean()
    F = np.abs(np.fft.rfft(y, 4096))
    fr = np.fft.rfftfreq(4096, es[1] - es[0])
    j = int(np.argmax(F[1:])) + 1
    log("  %-13s (todos os m)/(m = 0) - 1: faixa [%+.2e, %+.2e] ; periodo dominante em e: %.4f" % (
        tp, V[:, i].min(), V[:, i].max(), 1 / fr[j]))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
