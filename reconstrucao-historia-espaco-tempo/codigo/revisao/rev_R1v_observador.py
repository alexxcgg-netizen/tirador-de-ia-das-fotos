"""Verificacao independente (R1v) dos itens 1, 2, 3, 7 e 12 da revisao R1 do 07.

Nivel A (modos oscilatorios do NRHybSur3dq8_CCE), sistema A do exp07 e pares de exp07_pares.json.
  V1  multipolos m != 0 das memorias no observador (todos os (l, m) com l <= 8) contra so m = 0,
      em funcao do azimute phi; teste da borda inicial cortando o inicio por fracoes de orbita.
  V2  deslocamento total (com a parte 3PN antes de 10 Hz) contra deslocamento de janela.
  V3  anatomia da memoria de CM (ordinaria l = 2, l = 4, nula) e integral bruta de h_+^{m=0} (nivel C).
  V7  posto do jacobiano 4 x 6 em varias inclinacoes (linhas divididas por |F(A, 50 graus)|).
  V12 duas janelas (10 e 20 Hz): razoes F(20)/F(10) e jacobiano 8 x 6.
Saida: resultados/revisao/rev_R1v_observador.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
from harmonicos import sYlm, Dfrak, ethb2_de_escalar    # noqa: E402
from memorias import gram                               # noqa: E402

linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
PARES = json.load(open(os.path.join(AQUI, "..", "..", "resultados", "exp07_pares.json")))["pares"]


def mem_todos(q, c1, c2, M, f_fis=10.0, dt=0.25, i0=0, modos=None):
    """Memorias de nivel A com TODOS os (l, m), como em binarias.memorias (deslocamento total em m = 0).

    i0 corta as primeiras amostras (teste da borda inicial). Devolve (mem, aux, pre) onde pre e a parte
    do deslocamento anterior a janela (so m = 0)."""
    f0 = M * Dt.MSUN_S * f_fis
    if modos is None:
        t, h = B.gerar(q, c1, c2, f0=f0, dt=dt)
    else:
        t, h = modos
    eta = q / (1 + q) ** 2
    c_osc, _ = B.calculadoras()
    L = B.lista_osc()
    H = np.stack([h[k] for k in L], axis=1)[i0:]
    Hd = B.derivada4(H, dt)
    m = c_osc.memorias_gram(*gram(H, Hd, dt))
    # x0 no inicio efetivo da janela: frequencia do (2,2) na amostra i0 (so muda se i0 > 0)
    if i0 == 0:
        x0 = (np.pi * f0) ** (2 / 3)
    else:
        ph = np.unwrap(np.angle(h[(2, 2)]))
        om = -np.gradient(ph, dt)[i0] / 2
        x0 = om ** (2 / 3)
    E_rad = m["energia_total"] + 0.5 * eta * x0 * (1 + x0 * (-0.75 - eta / 12))
    Mf = 1.0 - E_rad
    out = {tp: {k: v for k, v in m[tp].items() if k[0] <= 8} for tp in B.TIPOS}
    pre = {(2, 0): B.favata_h20(x0, eta), (4, 0): B.lrr_h40(x0, eta)}
    for k, v in pre.items():
        out["deslocamento"][k] = out["deslocamento"][k] + v
    cm_ord = {}
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            cm_ord[(l, mm)] = 0.5 * ethb2_de_escalar(l) * (-1.5 * Mf * dPhi / Dfrak(l))
    cm_nul = dict(out["cm"])
    for k, v in cm_ord.items():
        out["cm"][k] = out["cm"].get(k, 0j) + v
    aux = dict(Mf=Mf, eta=eta, x0=x0, cm_ord=cm_ord, cm_nul=cm_nul, t=t)
    return out, aux, pre


def obs(mem, iota, phi=0.0, so_m0=False):
    """Quatro memorias adimensionais no observador (iota, phi), como binarias.no_observador."""
    v = {}
    for tp in B.TIPOS:
        s = 0 if tp == "giroscopica" else -2
        z = sum(c * sYlm(s, l, m, iota, phi) for (l, m), c in mem[tp].items()
                if (m == 0 or not so_m0))
        v[tp] = float(-np.imag(z)) if tp == "spin" else float(np.real(z))
    return v


def fis(v, M, D):
    Ms, Ds = M * Dt.MSUN_S, D * Dt.MPC_S
    return np.array([v["deslocamento"] * Ms / Ds, v["spin"] * Ms * Ms / Ds, v["cm"] * Ms * Ms / Ds,
                     v["giroscopica"] * (Ms / Ds) ** 2])


# ------------------------------------------------------------------ V1
log("V1. multipolos m != 0 no observador (nivel A, sistema A, iota = 50 graus, janela desde 10 Hz)")
tA, hA = B.gerar(A["q"], A["c1"], A["c2"], f0=A["M"] * Dt.MSUN_S * 10.0, dt=0.25)
memA, auxA, preA = mem_todos(A["q"], A["c1"], A["c2"], A["M"], modos=(tA, hA))
phis = np.radians(np.arange(0, 360, 5.0))
r0 = fis(obs(memA, A["iota"], so_m0=True), A["M"], A["D"])
rel = np.array([fis(obs(memA, A["iota"], p), A["M"], A["D"]) / r0 - 1 for p in phis])
for k, tp in enumerate(B.TIPOS):
    log("  %-13s (todos os m)/(so m = 0) - 1 ao longo de phi: min %+.2e max %+.2e" % (tp, rel[:, k].min(), rel[:, k].max()))
for tp in B.TIPOS:
    mz = max(abs(v) for k, v in memA[tp].items() if k[1] == 0)
    kk = max((k for k in memA[tp] if k[1] != 0), key=lambda k: abs(memA[tp][k]))
    log("    %-13s maior m != 0: %s |.| = %.2e ; maior m = 0: %.2e" % (tp, kk, abs(memA[tp][kk]), mz))
# teste da borda inicial: cortar 0, 1/4, 1/2, 3/4 de orbita no inicio
om0 = (np.pi * A["M"] * Dt.MSUN_S * 10.0)       # Omega orbital = pi f M (adimensional)
n_orb = int(round(2 * np.pi / om0 / 0.25))
log("  borda inicial: periodo orbital em 10 Hz = %d amostras; cortes de 0, 1/4, 1/2, 3/4 de orbita" % n_orb)
amostra = {}
for frac in (0.0, 0.25, 0.5, 0.75):
    mm, _, _ = mem_todos(A["q"], A["c1"], A["c2"], A["M"], modos=(tA, hA), i0=int(frac * n_orb))
    amostra[frac] = mm
for tp, k in (("spin", (2, -1)), ("spin", (2, 1)), ("giroscopica", (2, -1)), ("cm", (2, -2)), ("deslocamento", (3, -1))):
    vals = np.array([amostra[f][tp][k] for f in sorted(amostra)])
    log("    %-13s %s: valores %s ; dispersao/|media| = %.1e" % (
        tp, k, " ".join("%.3e%+.3ei" % (z.real, z.imag) for z in vals), np.std(np.abs(vals - vals.mean())) / abs(vals.mean())
        if abs(vals.mean()) > 0 else 0))
# o mesmo, com a janela terminando 300 M antes do pico (so inspiral): borda inicial + borda final artificial
ipk = np.argmax(np.abs(hA[(2, 2)]))
h_insp = {k: v[:ipk - 1200] for k, v in hA.items()}
mi, _, _ = mem_todos(A["q"], A["c1"], A["c2"], A["M"], modos=(tA[:ipk - 1200], h_insp))
for tp, k in (("spin", (2, -1)), ("giroscopica", (2, -1))):
    log("    so inspiral (ate 300 M antes do pico): %-11s %s |.| = %.2e (janela inteira: %.2e)" % (tp, k, abs(mi[tp][k]), abs(memA[tp][k])))

# par (2, 0) no observador com todos os m
p2 = [p for p in PARES if p["qB"] == 2.0 and p["c2B"] == 0.0][0]
memB, auxB, preB = mem_todos(2.0, p2["c1"], 0.0, p2["M"])
log("  par (q_B = 2, chi2 = 0): (B - A)/|A| no observador, mesmo phi para A e B")
for pd in (0, 90, 180, 270):
    p = np.radians(pd)
    a0 = fis(obs(memA, A["iota"], so_m0=True), A["M"], A["D"])
    b0 = fis(obs(memB, p2["iota"], so_m0=True), p2["M"], p2["D"])
    a1 = fis(obs(memA, A["iota"], p), A["M"], A["D"])
    b1 = fis(obs(memB, p2["iota"], p), p2["M"], p2["D"])
    log("    phi = %3d: so m = 0: %s | todos os m: %s" % (pd, " ".join("%+.1e" % x for x in (b0 - a0) / np.abs(a0)),
                                                       " ".join("%+.1e" % x for x in (b1 - a1) / np.abs(a1))))
# phi_B livre: min sobre phi_B do max_k |B(phi_B) - A(phi_A)|/|A|
grade = np.radians(np.arange(0, 360, 1.0))
FB = np.array([fis(obs(memB, p2["iota"], p), p2["M"], p2["D"]) for p in grade])
for pa in (0, 90):
    a1 = fis(obs(memA, A["iota"], np.radians(pa)), A["M"], A["D"])
    d = np.max(np.abs(FB - a1) / np.abs(a1), axis=1)
    log("    phi_A = %3d: min sobre phi_B de max_k |dif| = %.1e (em phi_B = %.0f graus)" % (pa, d.min(), np.degrees(grade[np.argmin(d)])))

# ------------------------------------------------------------------ V2 e V3
log("\nV2. deslocamento total x de janela (nivel A, l <= 8, m = 0)")


def desl_partes(mem, pre, iota, M, D):
    tot = obs(mem, iota, so_m0=True)["deslocamento"]
    pr = sum(c * sYlm(-2, l, 0, iota, 0.0) for (l, _), c in pre.items()).real
    Ms, Ds = M * Dt.MSUN_S, D * Dt.MPC_S
    return tot * Ms / Ds, (tot - pr) * Ms / Ds


dA_tot, dA_jan = desl_partes(memA, preA, A["iota"], A["M"], A["D"])
log("  A: total = %.5e ; janela = %.5e ; fracao antes de 10 Hz = %.4f" % (dA_tot, dA_jan, 1 - dA_jan / dA_tot))
for p in PARES:
    if p["qB"] == 2.0 and p["c2B"] == 0.0:
        mB, preB_ = memB, preB
    else:
        mB, _, preB_ = mem_todos(p["qB"], p["c1"], p["c2B"], p["M"])
    dt_, dj_ = desl_partes(mB, preB_, p["iota"], p["M"], p["D"])
    log("  B (q = %.0f, chi2 = %+.1f): total (B-A)/A = %+.1e ; janela (B-A)/A = %+.2e" % (
        p["qB"], p["c2B"], dt_ / dA_tot - 1, dj_ / dA_jan - 1))

log("\nV3. memoria de CM no observador (nivel A): anatomia e integral bruta")
Y = {l: sYlm(-2, l, 0, A["iota"], 0.0).real for l in range(2, 9)}
c_ord2 = (auxA["cm_ord"][(2, 0)] * Y[2]).real
c_ord4 = (auxA["cm_ord"][(4, 0)] * Y[4]).real
c_nul = sum((v * Y[l]).real for (l, m), v in auxA["cm_nul"].items() if m == 0)
d_tot = sum((v * Y[l]).real for (l, m), v in memA["deslocamento"].items() if m == 0)
c_tot = obs(memA, A["iota"], so_m0=True)["cm"]
log("  M_f/M = %.4f ; CM/(M d) = %.4f ; ordinaria l=2: %.4f ; l=4: %.4f ; nula: %.4f ; -M_f/2 = %.4f" % (
    auxA["Mf"], c_tot / d_tot, c_ord2 / d_tot, c_ord4 / d_tot, c_nul / d_tot, -auxA["Mf"] / 2))
log("  CM_20/J_20 (deformacao, so a parte ordinaria) = %.6f M (previsao -M_f/2 = %.6f)" % (
    (auxA["cm_ord"][(2, 0)] / memA["deslocamento"][(2, 0)]).real, -auxA["Mf"] / 2))
FA = fis(obs(memA, A["iota"], so_m0=True), A["M"], A["D"])
log("  A em unidades fisicas (so m = 0): desl %.4e ; spin %.4e s ; CM %.4e s ; giro %.4e rad ; CM/desl = %.4e s = %.4f M" % (
    FA[0], FA[1], FA[2], FA[3], FA[2] / FA[0], FA[2] / FA[0] / (A["M"] * Dt.MSUN_S)))
# integral bruta de h_+^{m=0} com os modos m = 0 de RN (nivel C)
Ms, Ds = A["M"] * Dt.MSUN_S, A["D"] * Dt.MPC_S
hp = sum(hA[(l, 0)].real * sYlm(-2, l, 0, A["iota"], 0.0).real for l in (2, 4))
hp_rel = hp - hp[0]
ipk = np.argmax(np.abs(hA[(2, 2)]))
for nome, fim in (("ate o fim da serie", len(hp)), ("ate o pico + 50 M", ipk + 200)):
    I_bruta = np.sum(hp[:fim]) * 0.25 * Ms * Ms / Ds
    I_rel = np.sum(hp_rel[:fim]) * 0.25 * Ms * Ms / Ds
    log("  int h_+^{m=0} du (%s): bruta = %.3e s ; com h_+ - h_+(u_i) = %.3e s ; razao (com subtracao)/CM = %.2e" % (
        nome, I_bruta, I_rel, I_rel / FA[2]))
log("  duracao da serie: %.2f s ; Delta h_+ de RN na janela = %.4e" % ((tA[-1] - tA[0]) * Ms, hp_rel[-1] * Ms / Ds))
del hA, tA

# ------------------------------------------------------------------ V7 e V12
log("\nV7/V12. jacobianos (colunas ln M, q, chi1, chi2, ln D, iota)")


def F_intr(q, c1, c2, M, f_fis):
    mem, _, _ = mem_todos(q, c1, c2, M, f_fis=f_fis)
    return {k: v for k, v in mem.items()}


def janela(mem):
    """mesma memoria com o deslocamento de janela (sem a parte anterior)."""
    return mem


PASSO = float(os.environ.get("PASSO_R1V", "1e-3"))
passo = dict(lnM=PASSO, q=PASSO, c1=PASSO, c2=PASSO)
log("  passo das diferencas centrais: %.0e" % PASSO)
pontos = {}
for ff in (10.0, 20.0):
    pontos[(ff, "0")] = mem_todos(A["q"], A["c1"], A["c2"], A["M"], f_fis=ff)
    for nome, hstep in passo.items():
        for sg in (+1, -1):
            q, c1, c2, M = A["q"], A["c1"], A["c2"], A["M"]
            if nome == "lnM":
                M = M * np.exp(sg * hstep)
            elif nome == "q":
                q = q + sg * hstep
            elif nome == "c1":
                c1 = c1 + sg * hstep
            else:
                c2 = c2 + sg * hstep
            pontos[(ff, nome, sg)] = (mem_todos(q, c1, c2, M, f_fis=ff), M)
log("  (%d pontos calculados, %.0f s)" % (len(pontos), time.time() - T0))


def jac(iota, ff, escala, desl_janela=False):
    def val(mm, M, D, io):
        mem, aux, pre = mm
        v = obs(mem, io, so_m0=True)
        if desl_janela:
            v["deslocamento"] -= sum(c * sYlm(-2, l, 0, io, 0.0) for (l, _), c in pre.items()).real
        return fis(v, M, D)
    F0 = val(pontos[(ff, "0")], A["M"], A["D"], iota)
    J = np.zeros((4, 6))
    for j, nome in enumerate(("lnM", "q", "c1", "c2")):
        (mp, Mp), (mn, Mn) = pontos[(ff, nome, 1)], pontos[(ff, nome, -1)]
        J[:, j] = (val(mp, Mp, A["D"], iota) - val(mn, Mn, A["D"], iota)) / (2 * passo[nome])
    J[:, 4] = -F0 * np.array([1, 1, 1, 2])
    di = 1e-5
    J[:, 5] = (val(pontos[(ff, "0")], A["M"], A["D"], iota + di) - val(pontos[(ff, "0")], A["M"], A["D"], iota - di)) / (2 * di)
    return F0, J / escala[:, None]


esc, _ = jac(A["iota"], 10.0, np.ones(4))
esc = np.abs(esc)
for ig in (50.0, 70.0, 89.0, 89.9, 90.0, 30.0, 10.0, 0.5, 0.0):
    F0, J = jac(np.radians(ig), 10.0, esc)
    sv = np.linalg.svd(J, compute_uv=False)
    log("  iota = %5.1f: F/|F_A| = %s ; sv = %s" % (ig, np.array2string(F0 / esc, precision=3), np.array2string(sv, precision=3)))
F0, J = jac(A["iota"], 10.0, esc)
u, s, vt = np.linalg.svd(J[:, :4])
log("  so intrinsecos (D, iota fixos) em 50 graus: sv = %s ; direcao quase nula = %s" % (
    np.array2string(s, precision=3), np.array2string(vt[-1], precision=3)))

F10, J10 = jac(A["iota"], 10.0, esc)
F20, J20 = jac(A["iota"], 20.0, esc)
log("  F(20 Hz)/F(10 Hz) (desl, spin, CM, giro) = %s" % np.array2string(F20 / F10, precision=5))
s8 = np.linalg.svd(np.vstack([J10, J20]), compute_uv=False)
log("  8 x 6 (10 + 20 Hz): sv = %s" % np.array2string(s8, precision=3))
sdif = np.linalg.svd(np.vstack([J10, J20 - J10]), compute_uv=False)
log("  10 Hz + diferencas: sv = %s" % np.array2string(sdif, precision=3))
for k, tp in enumerate(B.TIPOS):
    log("    linha da diferenca %-13s %s" % (tp, np.array2string(J20[k] - J10[k], precision=4)))
# com o deslocamento de janela (o que um detector com corte em baixa frequencia ve)
F10j, J10j = jac(A["iota"], 10.0, esc, desl_janela=True)
F20j, J20j = jac(A["iota"], 20.0, esc, desl_janela=True)
log("  com deslocamento de JANELA: desl(20)/desl(10) = %.4f ; sv 8 x 6 = %s" % (
    F20j[0] / F10j[0], np.array2string(np.linalg.svd(np.vstack([J10j, J20j]), compute_uv=False), precision=3)))
log("  linha da diferenca do deslocamento de janela: %s" % np.array2string(J20j[0] - J10j[0], precision=4))
# normalizacao por janela (cada linha dividida pelo |F| da propria janela), como no jacobiano relativo
J20r = J20 * (np.abs(F10) / np.abs(F20))[:, None]
log("  linhas de cada janela divididas pelo |F| da propria janela: sv 8 x 6 = %s" % np.array2string(
    np.linalg.svd(np.vstack([J10, J20r]), compute_uv=False), precision=3))
for k, tp in enumerate(B.TIPOS):
    log("    linha da diferenca relativa %-13s %s" % (tp, np.array2string(J20r[k] - J10[k], precision=4)))
log("(%.0f s)" % (time.time() - T0))
sufixo = "" if PASSO == 1e-3 else "_passo%.0e" % PASSO
with open(os.path.join(AQUI, "..", "..", "resultados", "revisao", "rev_R1v_observador%s.txt" % sufixo), "w") as f:
    f.write("\n".join(linhas) + "\n")
