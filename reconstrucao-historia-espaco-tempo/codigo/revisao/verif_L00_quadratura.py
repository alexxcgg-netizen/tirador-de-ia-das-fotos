"""Verificacao L00 (1): pesos de quadratura de observaveis.pesos_janela com t_i fora da grade.

Testes, todos com funcoes conhecidas (integral analitica):
  (a) exatidao para f = 1 e f = t (o trapezio com f(t_i) interpolado linearmente e exato para lineares);
  (b) f = (t - c)^2: o erro tem forma fechada  E = (T - t_k) dt^2/6 + L^3/6 + L a (1 - a) dt^2/2
      (trapezio composto de t_k ao fim + trapezio do subintervalo parcial + erro da interpolacao linear de
      f(t_i)); compara-se o erro medido com essa formula (deve coincidir ate o arredondamento);
  (c) f = cos(w t + p) e f = exp(-(t - t0)^2 / s^2): erro relativo e ordem de convergencia em dt;
  (d) continuidade em t_i: I(t_i) atravessando um no da grade (salto, derivada numerica = -f_lin(t_i));
  (e) gram_pesos contra a soma explicita;
  (f) rede deslocada (t_desloc = 0.37), grade de tempos grandes (t ~ -1.6e4 como no sistema A): pesos somam T - t_i.
Saida: resultados/revisao/verif_L00_quadratura.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import observaveis as O                                 # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_quadratura.txt")
L = []


def log(s=""):
    print(s, flush=True)
    L.append(s)


rng = np.random.default_rng(12345)
log("(a) exatidao para f = 1 e f = t, 200 valores aleatorios de t_i fora da grade (dt = 0.25, t ~ -16430)")
dt = 0.25
t = (np.arange(-65800, 541) + 0.0) * dt
pior1, piort = 0.0, 0.0
for _ in range(200):
    ti = -16430.0 + rng.uniform(-3, 3)
    w = O.pesos_janela(t, ti)
    T = t[-1]
    pior1 = max(pior1, abs(np.sum(w) - (T - ti)) / (T - ti))
    piort = max(piort, abs(np.sum(w * t) - 0.5 * (T ** 2 - ti ** 2)) / abs(0.5 * (T ** 2 - ti ** 2)))
log("  max erro relativo: f = 1 %.1e ; f = t %.1e" % (pior1, piort))

log("")
log("(b) f = (t - c)^2 (c = -100): erro medido contra a formula fechada do erro")
c = -100.0
pior = 0.0
for _ in range(200):
    ti = -16430.0 + rng.uniform(-3, 3)
    w = O.pesos_janela(t, ti)
    T = t[-1]
    k = int(np.searchsorted(t, ti, side="left"))
    a = (ti - t[k - 1]) / dt
    Lp = t[k] - ti
    exato = ((T - c) ** 3 - (ti - c) ** 3) / 3
    medido = np.sum(w * (t - c) ** 2) - exato
    prev = (T - t[k]) * dt ** 2 / 6 + Lp ** 3 / 6 + Lp * a * (1 - a) * dt ** 2 / 2
    pior = max(pior, abs(medido - prev) / abs(exato))
log("  max |erro medido - formula| / integral = %.1e (erro tipico %.1e relativo)" % (pior, prev / exato))

log("")
log("(c) funcoes suaves; erro relativo para dt = 0.5, 0.25, 0.125 (t_i = -16430.1234567, fim em 135)")
ti = -16430.1234567
for nome, f, F in (
        ("cos(0.02 t + 0.3)", lambda x: np.cos(0.02 * x + 0.3), lambda x: np.sin(0.02 * x + 0.3) / 0.02),
        ("cos(0.5 t + 0.3) (2.5 pontos/rad^-1)", lambda x: np.cos(0.5 * x + 0.3), lambda x: np.sin(0.5 * x + 0.3) / 0.5),
        ("exp(-(t+16000)^2/400^2)", lambda x: np.exp(-((x + 16000) / 400) ** 2),
         lambda x: 400 * np.sqrt(np.pi) / 2 * __import__("scipy").special.erf((x + 16000) / 400))):
    errs = []
    for d in (0.5, 0.25, 0.125):
        tt = np.arange(int(-16440 / d), int(135 / d) + 1) * d
        w = O.pesos_janela(tt, ti)
        ex = F(tt[-1]) - F(ti)
        errs.append((np.sum(w * f(tt)) - ex) / abs(ex))
    log("  %-40s erros %+.2e %+.2e %+.2e ; razoes %.2f %.2f" % (nome, errs[0], errs[1], errs[2], errs[0] / errs[1],
                                                                errs[1] / errs[2]))

log("")
log("(d) continuidade de I(t_i) = sum w f ao atravessar o no t = -16430.0 (f = cos(0.5 t + 0.3), dt = 0.25)")
f = lambda x: np.cos(0.5 * x + 0.3)                     # noqa: E731
eps = 1e-9
for no in (-16430.0,):
    Ia = np.sum(O.pesos_janela(t, no - eps) * f(t))
    Ib = np.sum(O.pesos_janela(t, no + eps) * f(t))
    I0 = np.sum(O.pesos_janela(t, no) * f(t))
    log("  I(no - 1e-9) - I(no) = %+.3e ; I(no + 1e-9) - I(no) = %+.3e ; esperado -+f(no) 1e-9 = %+.3e"
        % (Ia - I0, Ib - I0, -f(no) * eps))
# derivada numerica contra -f_lin(t_i) num ponto interior de um subintervalo
for ti in (-16430.0 + 0.0731, -16430.0 + 0.1987):
    h = 1e-6
    d = (np.sum(O.pesos_janela(t, ti + h) * f(t)) - np.sum(O.pesos_janela(t, ti - h) * f(t))) / (2 * h)
    k = int(np.searchsorted(t, ti))
    a = (ti - t[k - 1]) / dt
    flin = (1 - a) * f(t[k - 1]) + a * f(t[k])
    log("  t_i = %.4f: dI/dt_i numerico %+.10f ; -f_lin(t_i) %+.10f ; -f(t_i) %+.10f" % (ti, d, -flin, -f(ti)))
# varredura fina: salto maximo entre pontos vizinhos contra a variacao esperada
tis = -16430.5 + np.linspace(0, 1.0, 4001)
I = np.array([np.sum(O.pesos_janela(t, x) * f(t)) for x in tis])
dI = np.diff(I)
esperado = -f(0.5 * (tis[1:] + tis[:-1])) * np.diff(tis)
log("  varredura de 4001 valores de t_i em 1 M (4 nos): max |dI - (-f dt_i)| = %.1e (escala |dI| ~ %.1e)"
    % (np.max(np.abs(dI - esperado)), np.max(np.abs(dI))))
d2 = np.diff(I, 2)
log("  segunda diferenca: max %.2e ; nos nos (saltos de I'') e fora: mediana %.2e" % (np.max(np.abs(d2)), np.median(np.abs(d2))))

log("")
log("(e) gram_pesos contra a soma explicita (matrizes complexas aleatorias 3000 x 5)")
tt = t[-3000:]
H = rng.normal(size=(3000, 5)) + 1j * rng.normal(size=(3000, 5))
Hd = rng.normal(size=(3000, 5)) + 1j * rng.normal(size=(3000, 5))
w = O.pesos_janela(tt, tt[100] + 0.1)
Bm, Am = O.gram_pesos(H, Hd, w)
Bx = np.einsum("t,tj,tk->jk", w, Hd, Hd.conj())
Ax = np.einsum("t,tj,tk->jk", w, H, Hd.conj())
log("  max |B - B_explicito| / max|B| = %.1e ; A: %.1e" % (np.abs(Bm - Bx).max() / np.abs(Bx).max(),
                                                           np.abs(Am - Ax).max() / np.abs(Ax).max()))

log("")
log("(f) rede deslocada (t_k = (k + 0.37) dt), t_i no meio: soma dos pesos contra T - t_i")
t2 = (np.arange(-65800, 541) + 0.37) * dt
for ti in (-16430.2044, t2[50000], t2[50000] + 1e-12, t2[50000] - 1e-12):
    w = O.pesos_janela(t2, ti)
    log("  t_i = %.12f: sum w - (T - t_i) = %+.1e ; min(w) = %.3e" % (ti, np.sum(w) - (t2[-1] - ti), w[w != 0].min()))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
