"""Verificacao independente (R2v) dos itens 1, 2 e 7 da revisao R2: piso numerico das memorias.

O substituto devolve a onda numa grade fixa de passo dt que comeca no primeiro ponto em que a frequencia
do modo (2,2) passa de f_low (gwsurrogate/new/surrogate.py, _coorbital_to_inertial_frame). Quando M muda,
f0 = M f_fis muda e o primeiro ponto salta de dt: as memorias adimensionais sao uma escada em M.

1) Varredura M_A (1 + e), e de 0 a 1.2e-5 em passos de 2e-7, niveis A e C (mesma onda): saltos e
   variacao entre saltos (memorias adimensionais d, s, c, g, sem as escalas M/D, M^2/D, (M/D)^2).
2) Distancia de cada par 'exato' do exp07 a uma aresta da escada: M_B (1 +- e) com e = 1e-10 ... 1e-5.
3) Convergencia em dt: delta dos pares com dt = 0.25, 0.125 e 0.0625 M (A e B no mesmo dt), nivel A.
4) Inicio suave: a integracao comeca no instante exato t_i em que omega_22 = 2 pi f0 (interpolacao
   linear), com o primeiro ponto pesado pela fracao de passo; a derivada vem da serie mais longa (gerada
   desde 0.99 f0). Mede (a) a suavidade em M, (b) o delta dos pares do exp07 com inicio suave em dt = 0.25 e
   0.125, (c) a variacao das memorias de A entre dt 0.25 e 0.125 com inicio suave.
Saida: resultados/revisao/rev_R2v_escada.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
from deteccao import MSUN_S                             # noqa: E402
from harmonicos import Dfrak, ethb2_de_escalar          # noqa: E402
from memorias import gram                               # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
F = 10.0
linhas = []
POT = {"deslocamento": 1, "spin": 2, "cm": 2, "giroscopica": 2}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A = dados["A"]
EXATOS = [p for p in dados["pares"] if max(abs(x) for x in p["dif"].values()) < 1e-5]


def par_de(p):
    return dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])


def adim(par, dt=0.25, niveis=("A",)):
    """Memorias adimensionais no observador (d, s, c, g), por nivel, e (n, t0) da grade."""
    f0 = par["M"] * MSUN_S * F
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=f0, dt=dt)
    out = {}
    for n in niveis:
        mem, _ = B.memorias(par["q"], par["c1"], par["c2"], f0=f0, dt=dt, nivel=n, t=t, h=h)
        out[n] = B.no_observador(mem, par["iota"])
    n0, t0 = len(t), t[0]
    del t, h
    return out, n0, t0


def fisicas(v, par):
    """Escalas triviais: deslocamento M/D, spin e CM M^2/D, giroscopica (M/D)^2 (unidades arbitrarias comuns)."""
    return {k: v[k] * par["M"] ** POT[k] / par["D"] ** (1 if k != "giroscopica" else 2) for k in B.TIPOS}


def delta(vA, pA, vB, pB):
    a, b = fisicas(vA, pA), fisicas(vB, pB)
    return max(abs(b[k] / a[k] - 1) for k in B.TIPOS)


# ---------------------------------------------------------------- inicio suave
def memorias_suave(q, c1, c2, f0, dt, nivel="A"):
    """Como binarias.memorias, mas com a janela comecando no instante exato t_i (omega_22 = 2 pi f0)."""
    t, h = B.gerar(q, c1, c2, f0=0.99 * f0, dt=dt)
    eta = q / (1 + q) ** 2
    x0 = (np.pi * f0) ** (2 / 3)
    c_osc, c_full = B.calculadoras()
    Losc = B.lista_osc()
    Hosc = np.stack([h[k] for k in Losc], axis=1)
    if nivel == "A":
        H, calc = Hosc, c_osc
    else:
        H = np.concatenate([Hosc, np.stack([h[k] for k in B.MODOS_M0], axis=1)], axis=1)
        calc = c_full
    Hd = B.derivada4(H, dt)
    # omega_22 como no gwsurrogate (diferenca para frente da fase), atribuida ao ponto da esquerda
    fase = np.unwrap(np.angle(h[(2, 2)]))
    om = np.abs(np.diff(fase)) / dt
    w_low = 2 * np.pi * f0
    k = int(np.argmax(om > w_low))                     # primeiro ponto com omega > omega_low
    ti = t[k - 1] + (w_low - om[k - 1]) / (om[k] - om[k - 1]) * dt
    # pesos: 1 para t >= t[k], fracao (t[k] - t_i)/dt no ponto k - 1, 0 antes
    pesos = np.zeros(len(t))
    pesos[k:] = 1.0
    pesos[k - 1] = (t[k] - ti) / dt
    Bm, Am = gram(H * np.sqrt(pesos)[:, None], Hd * np.sqrt(pesos)[:, None], dt)
    m = calc.memorias_gram(Bm, Am)
    E_rad = m["energia_total"] + 0.5 * eta * x0 * (1 + x0 * (-0.75 - eta / 12))
    Mf = 1.0 - E_rad
    out = B._mem_m0(m)
    pre = {(2, 0): B.favata_h20(x0, eta), (4, 0): B.lrr_h40(x0, eta)}
    if nivel == "C":
        for l in (2, 4):
            out["deslocamento"][(l, 0)] = complex(h[(l, 0)][-1])
        S30 = np.sum(pesos * h[(3, 0)]) * dt
        out["spin"] = {kk: (S30 if kk == (3, 0) else 0j) for kk in out["spin"]}
        spin_pot30 = 2j * S30 / ethb2_de_escalar(3)
        out["giroscopica"][(3, 0)] = (-Dfrak(3) * spin_pot30 + 0.25 * m["helicidade_modos"][(3, 0)])
        for l in (5, 7):
            out["giroscopica"][(l, 0)] = 0.25 * m["helicidade_modos"][(l, 0)]
    else:
        for l in (2, 4):
            out["deslocamento"][(l, 0)] = out["deslocamento"][(l, 0)] + pre[(l, 0)]
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            dK = -1.5 * Mf * dPhi / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    del t, h, H, Hd, Hosc
    return out, ti


def adim_suave(par, dt=0.25, nivel="A"):
    f0 = par["M"] * MSUN_S * F
    mem, ti = memorias_suave(par["q"], par["c1"], par["c2"], f0, dt, nivel)
    return B.no_observador(mem, par["iota"]), ti


if __name__ == "__main__":
    t_ini = time.time()
    # ------------------------------------------------------------ 1) escada em M, niveis A e C
    log("1) Escada em M: A com M -> M (1 + e), e de 0 a 1.2e-5 em passos de 2e-7; memorias adimensionais.")
    es = np.arange(0, 1.2e-5 + 1e-13, 2e-7)
    serie = {"A": [], "C": []}
    ns, t0s = [], []
    for e in es:
        v, n, t0 = adim(dict(A, M=A["M"] * (1 + e)), niveis=("A", "C"))
        for nv in ("A", "C"):
            serie[nv].append([v[nv][k] for k in B.TIPOS])
        ns.append(n)
        t0s.append(t0)
    ns = np.array(ns)
    saltos = [i for i in range(1, len(es)) if ns[i] != ns[i - 1]]
    log("   n amostras: %s ; posicoes dos saltos (e): %s" % (sorted(set(ns.tolist())),
                                                         " ".join("%.1e" % es[i] for i in saltos)))
    if len(saltos) >= 2:
        # t_i ~ (M f)^(-8/3) em unidades de M: d t_i / d ln M = -(8/3) t_i, espacamento = 3 dt / (8 |t_i|)
        log("   espacamento entre saltos: %s (previsto 3 dt / (8 |t_i|): %.2e)"
            % (" ".join("%.2e" % (es[saltos[j + 1]] - es[saltos[j]]) for j in range(len(saltos) - 1)),
               3 * 0.25 / (8 * abs(t0s[0]))))
    for nv in ("A", "C"):
        s = np.array(serie[nv])
        rel = s / s[0] - 1
        for i in saltos:
            d = rel[i] - rel[i - 1]
            log("   nivel %s, salto em e = %.1e (n %d -> %d): %s" % (nv, es[i], ns[i - 1], ns[i],
                " ".join("%s %+.2e" % (k[:4], x) for k, x in zip(B.TIPOS, d))))
        sem = [i for i in range(1, len(es)) if i not in saltos]
        dmax = np.max(np.abs(np.array([rel[i] - rel[i - 1] for i in sem])), axis=0)
        log("   nivel %s, maior variacao num passo de 2e-7 SEM salto: %s" % (nv, " ".join(
            "%s %.2e" % (k[:4], x) for k, x in zip(B.TIPOS, dmax))))
    log("   (%.0f s)" % (time.time() - t_ini))

    # ------------------------------------------------------------ 2) pares exatos e arestas
    log("")
    log("2) Pares 'exatos' do exp07: n amostras e delta (nivel A, dt 0.25) com M_B (1 + e).")
    vA, nA, _ = adim(A)
    for p in EXATOS:
        pB = par_de(p)
        v0, n0, _ = adim(pB)
        txt = []
        for e in (-1e-5, -1e-6, -1e-7, -1e-8, -1e-9, -1e-10, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5):
            pe = dict(pB, M=pB["M"] * (1 + e))
            ve, ne, _ = adim(pe)
            # o D_B fica fixo; a mudanca trivial de escala de M e removida comparando com a escala de M_B
            dd = max(abs(ve["A"][k] / v0["A"][k] - 1) for k in B.TIPOS)
            txt.append("%+.0e: n%+d dif %.1e" % (e, ne - n0, dd))
        log("   par (%.0f, %+.1f): n = %d, delta = %.1e | %s" % (p["qB"], p["c2B"], n0, delta(vA["A"], A, v0["A"], pB),
                                                           " ; ".join(txt)))
    log("   (%.0f s)" % (time.time() - t_ini))

    # ------------------------------------------------------------ 3) convergencia em dt
    log("")
    log("3) Convergencia em dt (A e B no mesmo dt), nivel A.")
    vAdt = {dt: adim(A, dt)[0]["A"] for dt in (0.25, 0.125, 0.0625)}
    for dt in (0.125, 0.0625):
        log("   memorias de A, dt %.4f contra 0.25: %s" % (dt, " ".join(
            "%s %+.1e" % (k[:4], vAdt[dt][k] / vAdt[0.25][k] - 1) for k in B.TIPOS)))
    for p in EXATOS:
        pB = par_de(p)
        ds = [delta(vAdt[dt], A, adim(pB, dt)[0]["A"], pB) for dt in (0.25, 0.125, 0.0625)]
        log("   par (%.0f, %+.1f): delta dt 0.25 %.1e ; dt 0.125 %.1e ; dt 0.0625 %.1e" % (p["qB"], p["c2B"], *ds))
    log("   (%.0f s)" % (time.time() - t_ini))

    # ------------------------------------------------------------ 4) inicio suave
    log("")
    log("4) Inicio suave (t_i exato por interpolacao, primeiro ponto com peso fracionario), nivel A.")
    v0s, ti0 = adim_suave(A)
    log("   conferencia: inicio suave contra o original (dt 0.25): %s" % " ".join(
        "%s %+.1e" % (k[:4], v0s[k] / vA["A"][k] - 1) for k in B.TIPOS))
    es2 = np.arange(0, 1.2e-5 + 1e-13, 1e-6)
    ss = []
    for e in es2:
        v, ti = adim_suave(dict(A, M=A["M"] * (1 + e)))
        ss.append([v[k] for k in B.TIPOS])
    ss = np.array(ss)
    rel = ss / ss[0] - 1
    dif = np.abs(np.diff(rel, axis=0))
    log("   a) varredura e de 0 a 1.2e-5 em passos de 1e-6: maior variacao por passo %s ; variacao total %s"
        % (" ".join("%s %.1e" % (k[:4], x) for k, x in zip(B.TIPOS, dif.max(axis=0))),
           " ".join("%s %+.1e" % (k[:4], x) for k, x in zip(B.TIPOS, rel[-1]))))
    # segunda diferenca: mede a falta de suavidade (salto) separada da inclinacao
    d2 = np.abs(np.diff(rel, 2, axis=0))
    log("      maior segunda diferenca (suavidade) %s" % " ".join("%s %.1e" % (k[:4], x) for k, x in zip(B.TIPOS, d2.max(axis=0))))
    for e in (1e-10, 1e-9):
        v, _ = adim_suave(dict(A, M=A["M"] * (1 + e)))
        log("      e = %.0e: variacao %s" % (e, " ".join("%s %+.1e" % (k[:4], v[k] / v0s[k] - 1) for k in B.TIPOS)))
    vAs = {dt: adim_suave(A, dt)[0] for dt in (0.25, 0.125)}
    log("   c) memorias de A com inicio suave, dt 0.125 contra 0.25: %s" % " ".join(
        "%s %+.1e" % (k[:4], vAs[0.125][k] / vAs[0.25][k] - 1) for k in B.TIPOS))
    for p in EXATOS:
        pB = par_de(p)
        ds = [delta(vAs[dt], A, adim_suave(pB, dt)[0], pB) for dt in (0.25, 0.125)]
        log("   b) par (%.0f, %+.1f): delta com inicio suave: dt 0.25 %.1e ; dt 0.125 %.1e" % (p["qB"], p["c2B"], *ds))
    log("   (%.0f s)" % (time.time() - t_ini))
    with open(os.path.join(RES, "revisao", "rev_R2v_escada.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
