"""Verificacao L00 (3) e (4): parte ordinaria da memoria de CM e a opcao todos_m de observaveis.py.

(3) CM. Recalcula a parte nula (CalculadoraMemoria.memorias_gram com os pesos da janela, sem passar por
    memorias_observaveis) e confere, multipolo a multipolo (l <= 8, todos os m), que
        cm = cm_nula(janela) - (3/2) M_f DeltaJ / Dfrak(l)
    com DeltaJ = deslocamento da opcao desl (nivel A: nulo da janela, + Favata/LRR em 'total'; nivel C:
    h_l0(fim) - h_l0(t_i) para l = 2, 4). Janelas curtas: cm20 com 'janela' deve ir a zero linearmente com
    a duracao; com 'total' fica o termo de borda -(M_f/2) h20_Favata(x_i). Tamanho da convencao
    alternativa M_f Phi_f - M_i Phi_i (que exige o deslocamento total em t_i, inobservavel).
(4) todos_m contra codigo/revisao/rev_R1_m_nao_nulo.py: copia exata de memorias_todas/observador do rev_R1,
    reproduz os numeros do rev_R1_m_nao_nulo.txt; compara multipolos (com as mesmas formulas: derivada de
    4a ordem, E_lig 1PN, desl='total') depois de uma rotacao azimutal unica alpha (as duas convencoes
    de fase orbital diferem: rev_R1 zera a fase no primeiro ponto da grade de binarias, observaveis em t_i);
    faixas em phi numa grade fina (720 valores) e nas grades de 12 (rev_R1) e 24 (D0) valores.
Saida: resultados/revisao/verif_L00_cm_mnao0.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import deteccao as Dt                                    # noqa: E402
import observaveis as O                                  # noqa: E402
from harmonicos import sYlm, Dfrak, ethb2_de_escalar     # noqa: E402
from memorias import gram                                # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_cm_mnao0.txt")
L = []
T0 = time.time()
SA = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, F=10.0, iota=np.radians(50.0))


def log(s=""):
    print(s, flush=True)
    L.append(s)


# ============================================================================ (3) CM
log("(3) Memoria de CM: cm = nula(janela) - (3/2) M_f DeltaJ/Dfrak(l), multipolo a multipolo (sistema A)")
t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
w = O.pesos_janela(t, ti)
x_i = (np.pi * SA["M"] * Dt.MSUN_S * SA["F"]) ** (2 / 3)
eta = SA["q"] / (1 + SA["q"]) ** 2
c_osc, c_full = B.calculadoras()
for nivel in ("A", "C"):
    Hl = [h[k] for k in B.lista_osc()] + ([h[k] for k in B.MODOS_M0] if nivel == "C" else [])
    H = np.stack(Hl, axis=1)
    Hd = O.derivada(H, 0.25)
    raw = (c_osc if nivel == "A" else c_full).memorias_gram(*O.gram_pesos(H, Hd, w))
    del H, Hd
    for desl in ("janela", "total"):
        m, aux = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], nivel=nivel, desl=desl,
                                        todos_m=True, t=t, h=h, t_i=ti)
        pior = 0.0
        for (l, mm), v in m["cm"].items():
            if l < 2:
                continue
            dJ = raw["deslocamento"][(l, mm)]
            if nivel == "C" and mm == 0 and l in (2, 4):
                fim = h[(l, 0)][-1]
                dJ = fim if desl == "total" else fim - O._interp_em(t, h[(l, 0)], ti)
            elif nivel == "A" and desl == "total" and (l, mm) == (2, 0):
                dJ = dJ + B.favata_h20(x_i, eta)
            elif nivel == "A" and desl == "total" and (l, mm) == (4, 0):
                dJ = dJ + B.lrr_h40(x_i, eta)
            esperado = raw["cm"][(l, mm)] - 1.5 * aux["M_f"] * dJ / Dfrak(l)
            pior = max(pior, abs(v - esperado))
            # o deslocamento usado tem de ser o mesmo que memorias_observaveis devolve
            pior = max(pior, abs(m["deslocamento"][(l, mm)] - dJ))
        esc = max(abs(v) for v in m["cm"].values())
        cm20, nula20 = m["cm"][(2, 0)].real, raw["cm"][(2, 0)].real
        log("  nivel %s, desl='%s': max |cm - (nula - 1.5 M_f dJ/Dfrak)| / max|cm| = %.1e ; cm20 = %+.6f, parte nula"
            " %+.6f (%.1f%%), ordinaria %+.6f" % (nivel, desl, pior / esc, cm20, nula20, 100 * nula20 / cm20,
                                                cm20 - nula20))
del t, h
# fração no observador e o atraso equivalente: CM ~ -(M_f/2) Delta h_+ + nula
m, aux = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
v = O.no_observador_completo(m, SA["iota"], 0.0)
mo = {tp: dict(m[tp]) for tp in O.TIPOS}
mo["cm"] = {k: -1.5 * aux["M_f"] * m["deslocamento"][k] / Dfrak(k[0]) for k in m["cm"] if k[0] >= 2}
vo = O.no_observador_completo(mo, SA["iota"], 0.0)
log("  observador (iota 50, m = 0, 'janela'): CM %+.6f ; so ordinaria %+.6f (%.1f%%) ; -(M_f/2) Delta h_+ = %+.6f"
    % (v["cm"], vo["cm"], 100 * vo["cm"] / v["cm"], -0.5 * aux["M_f"] * v["deslocamento"]))

log("")
log("  Janelas curtas desde t_i (q = 1, chi = 0, 10 Hz, M = 65): cm20 e desl20 contra a duracao")
t, h, ti = O.gerar_janela(1.0, 0.0, 0.0, SA["M"], 10.0)
x1 = (np.pi * SA["M"] * Dt.MSUN_S * 10.0) ** (2 / 3)
for dur in (10.0, 25.0, 50.0, 100.0, 200.0, 400.0):
    n = int(np.searchsorted(t, ti + dur)) + 1
    tc, hc = t[:n], {k: v[:n] for k, v in h.items()}
    mj, aj = O.memorias_observaveis(1.0, 0.0, 0.0, SA["M"], 10.0, desl="janela", t=tc, h=hc, t_i=ti)
    mt, at = O.memorias_observaveis(1.0, 0.0, 0.0, SA["M"], 10.0, desl="total", t=tc, h=hc, t_i=ti)
    log("    duracao %5.0f M: 'janela' desl20 %+.3e cm20 %+.3e (cm20/duracao %+.3e) ; 'total' cm20 %+.4e"
        " (-(M_f/2) Favata = %+.4e)" % (tc[-1] - ti, mj["deslocamento"][(2, 0)].real, mj["cm"][(2, 0)].real,
                                       mj["cm"][(2, 0)].real / (tc[-1] - ti), mt["cm"][(2, 0)].real,
                                       -0.5 * at["M_f"] * B.favata_h20(x1, 0.25)))
del t, h
# convencao alternativa M_f Phi_f - M_i Phi_i, com Phi_i do deslocamento total em t_i (Favata)
mj, aj = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], desl="janela")
Mi = 1 - aj["E_lig"]
alt = mj["cm"][(2, 0)].real - 1.5 * (aj["M_f"] - Mi) * B.favata_h20(x_i, eta) / Dfrak(2)
log("  convencao M_f Phi_f - M_i Phi_i (Phi_i = Favata em x_i) contra M_f Delta Phi: cm20 %+.6f contra %+.6f (%.2f%%)"
    % (alt, mj["cm"][(2, 0)].real, 100 * (alt / mj["cm"][(2, 0)].real - 1)))
log("  (%.0f s)" % (time.time() - T0))


# ============================================================================ (4) todos_m contra rev_R1
def memorias_todas(q, c1, c2, M, rampa_s=0.0, dt=0.25):
    """Copia exata de codigo/revisao/rev_R1_m_nao_nulo.py (nivel A, deslocamento total, todos os m)."""
    t, h = B.gerar(q, c1, c2, f0=M * Dt.MSUN_S * 10.0, dt=dt)
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    del h
    if rampa_s > 0:
        n = int(rampa_s / (M * Dt.MSUN_S) / dt)
        H[:n] *= (0.5 * (1 - np.cos(np.pi * np.arange(n) / n)))[:, None]
    Hd = B.derivada4(H, dt)
    calc = B.calculadoras()[0]
    m = calc.memorias_gram(*gram(H, Hd, dt))
    del H, Hd
    eta = q / (1 + q) ** 2
    x0 = (np.pi * M * Dt.MSUN_S * 10.0) ** (2 / 3)
    Mf = 1 - (m["energia_total"] + 0.5 * eta * x0 * (1 + x0 * (-0.75 - eta / 12)))
    pre = {(2, 0): B.favata_h20(x0, eta), (4, 0): B.lrr_h40(x0, eta)}
    out = {k: {} for k in B.TIPOS}
    for (l, mm), v in m["deslocamento"].items():
        if l <= 8:
            out["deslocamento"][(l, mm)] = v + pre.get((l, mm), 0.0)
    for (l, mm), v in m["spin"].items():
        if l <= 8:
            out["spin"][(l, mm)] = v
    for (l, mm), v in m["giroscopica"].items():
        if l <= 8:
            out["giroscopica"][(l, mm)] = v
    for (l, mm), v in m["cm"].items():
        if l <= 8:
            dJ = out["deslocamento"][(l, mm)]
            out["cm"][(l, mm)] = v + 0.5 * ethb2_de_escalar(l) * (-1.5 * Mf * (2 * dJ / ethb2_de_escalar(l)) / Dfrak(l))
    return out


def observador(mem, iota, phi, so_m0):
    vals = {}
    for tipo in B.TIPOS:
        s = 0 if tipo == "giroscopica" else -2
        z = sum(c * sYlm(s, l, m, iota, phi) for (l, m), c in mem[tipo].items() if (m == 0 or not so_m0))
        vals[tipo] = float(-np.imag(z)) if tipo == "spin" else float(np.real(z))
    return vals


def faixas(mem, phis, iota=SA["iota"]):
    base = observador(mem, iota, 0.0, True)
    R = np.array([[observador(mem, iota, ph, False)[tp] / base[tp] - 1 for tp in B.TIPOS] for ph in phis])
    return R.min(axis=0), R.max(axis=0)


log("")
log("(4) todos_m contra rev_R1_m_nao_nulo.py (sistema A, janela abrupta, desl total)")
with open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")) as fh:
    A = json.load(fh)["A"]
log("  parametros de A no exp07_pares.json: q %.3f chi (%+.2f, %+.2f) M %.1f D %.0f iota %.4f" % (
    A["q"], A["c1"], A["c2"], A["M"], A["D"], A["iota"]))
R1 = memorias_todas(A["q"], A["c1"], A["c2"], A["M"], 0.0)
ph12 = np.linspace(0, 2 * np.pi, 13)[:-1]
ph24 = np.linspace(0, 2 * np.pi, 25)[:-1]
ph720 = np.linspace(0, 2 * np.pi, 721)[:-1]
mn, mx = faixas(R1, ph12, A["iota"])
log("  copia do rev_R1, grade de 12 phi (deve reproduzir rev_R1_m_nao_nulo.txt): %s" % " ".join(
    "%s [%+.2e, %+.2e]" % (tp[:4], a, b) for tp, a, b in zip(B.TIPOS, mn, mx)))
Ob, aob = O.memorias_observaveis(A["q"], A["c1"], A["c2"], A["M"], 10.0, desl="total", todos_m=True, ordem_deriv=4,
                                 ordem_elig=1)
# rotacao azimutal: multipolo (L, M) -> e^{-i M alpha}; alpha pelo maior m != 0 (spin (2, -1))
z1, z2 = Ob["spin"][(2, -1)], R1["spin"][(2, -1)]
alpha = -np.angle(z1 / z2) / (-1)
log("  rotacao azimutal estimada pelo spin (2,-1): alpha = %+.3e rad ; |obs|/|rev_R1| - 1 = %+.1e" % (alpha, abs(z1) / abs(z2) - 1))
for tp in B.TIPOS:
    piorm0, piorm, piorm_sem = 0.0, 0.0, 0.0
    esc0 = max(abs(v) for k, v in R1[tp].items() if k[1] == 0)
    escm = max(abs(v) for k, v in R1[tp].items() if k[1] != 0)
    for k, v in R1[tp].items():
        if k[1] == 0:
            piorm0 = max(piorm0, abs(Ob[tp][k] - v) / esc0)
        else:
            piorm = max(piorm, abs(Ob[tp][k] - v * np.exp(-1j * k[1] * alpha)) / escm)
            piorm_sem = max(piorm_sem, abs(Ob[tp][k] - v) / escm)
    log("    %-13s m = 0: max dif./max|m=0| %.1e ; m != 0: max dif./max|m!=0| %.1e com rotacao (%.1e sem)"
        % (tp, piorm0, piorm, piorm_sem))
for nome, ph in (("12", ph12), ("24", ph24), ("720", ph720)):
    a1, b1 = faixas(R1, ph, A["iota"])
    a2, b2 = faixas(Ob, ph, A["iota"])
    log("  grade de %3s phi: rev_R1 %s" % (nome, " ".join("%s [%+.3e, %+.3e]" % (tp[:4], a, b)
                                                      for tp, a, b in zip(B.TIPOS, a1, b1))))
    log("  %16s observaveis %s" % ("", " ".join("%s [%+.3e, %+.3e]" % (tp[:4], a, b)
                                                 for tp, a, b in zip(B.TIPOS, a2, b2))))
Oj, _ = O.memorias_observaveis(A["q"], A["c1"], A["c2"], A["M"], 10.0, desl="janela", todos_m=True)
a2, b2 = faixas(Oj, ph720, A["iota"])
log("  observaveis padrao (desl='janela', ordem 8, 3PN), 720 phi: %s" % " ".join(
    "%s [%+.3e, %+.3e]" % (tp[:4], a, b) for tp, a, b in zip(B.TIPOS, a2, b2)))
# no_observador_completo contra observador do rev_R1 (mesmo mem, mesmo phi)
d = max(abs(O.no_observador_completo(Ob, A["iota"], ph)[tp] - observador(Ob, A["iota"], ph, False)[tp])
        / abs(observador(Ob, A["iota"], ph, False)[tp]) for ph in ph24 for tp in B.TIPOS)
log("  no_observador_completo contra observador(rev_R1) no mesmo dicionario: max dif. relativa %.1e" % d)
log("  (%.0f s)" % (time.time() - T0))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
