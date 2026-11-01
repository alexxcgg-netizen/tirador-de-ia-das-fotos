"""Experimento 31 (linha L08, agente D5): varios modos nos fluxos projetados; separacao; fase sem ruido.

 1. Pesos angulares: projecoes L = 2..8 (m = 0) do fluxo de energia E_L e do fluxo de momento angular J_L para cada
    par de modos (proprios e cruzados com o mesmo m), por sinais circulares sinteticos (Omega = 1):
        E_L = Omega^2 sum_p m_p^2 gE[L,p] X_p ,   J_L = Im(h^B_L) = Omega sum_p m_p gJ[L,p] X_p ,
    X_p = |h_lm|^2 (par proprio) ou Re(h_lm conj h_l'm) (cruzado).
 2. Decomposicao dos E_L e J_L do substituto em contribuicoes de pares (sistemas A, q = 4, q = 1 chi = 0.6).
 3. Separacao: em cada instante, (Omega, X_p) por minimos quadrados com as 7 projecoes (E_2,4,6,8; J_3,5,7), para
    varios conjuntos de pares; erro em Omega e em |h22| contra o verdadeiro; fase e sobreposicao do (2,2)
    reconstruido (sem ruido).
 4. Um observador (iota = 50 graus, h+ e hx separados): Omega_obs = K(iota) hdot+_mem / (2 hx_mem); o fator K(iota)
    so e conhecido se iota for; erro de escala com iota errado.
 5. Multipolos m != 0 do fluxo resolvido no tempo: arg E_{4,4}(t) e arg E_{2,1}(t) contra a fase orbital.
Saidas: resultados/exp31_varios_modos.txt, .json, figuras/e31_varios_modos.png
"""
import json
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np                                        # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import binarias as B                                      # noqa: E402
import exp24_comum as X                                   # noqa: E402
import exp30_comum as C                                   # noqa: E402
import observaveis as O                                   # noqa: E402
from harmonicos import sYlm                               # noqa: E402
from memorias import CalculadoraMemoria                   # noqa: E402

linhas = []
res = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


T0 = time.time()
LOSC = B.lista_osc()
LS = X.LS                                                 # 2..8
iE = [LS.index(L) for L in (2, 4, 6, 8)]
iJ = [LS.index(L) for L in (3, 5, 7)]
PROPRIOS = [(2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (4, 3), (5, 5)]
CRUZADOS = [((2, 2), (3, 2)), ((3, 3), (4, 3))]

# ====================================================================== 1. pesos
tt = np.arange(0, 100, 0.05)


def taxas_sint(modos):
    Hm = np.zeros((len(tt), len(LOSC)), complex)
    for (l, m), c in modos.items():
        Hm[:, LOSC.index((l, m))] += c * np.exp(-1j * m * tt)
        Hm[:, LOSC.index((l, -m))] += (-1) ** l * np.conj(c * np.exp(-1j * m * tt))
    R, HB = X.taxas_m0(Hm, O.derivada(Hm, 0.05))
    return R[1000].real, HB[1000].imag, np.max(np.abs(R[1000].imag)), np.max(np.abs(HB[1000].real))


gE, gJ, mp, nomes = [], [], [], []
log("== 1. Pesos angulares (sinais circulares sinteticos, Omega = 1): E_L/(m^2 X) e J_L/(m X)")
log("   par           gE: L=2       L=4       L=6       L=8   |  gJ: L=3       L=5       L=7")
for p in PROPRIOS:
    R, J, ri, ji = taxas_sint({p: 1.0})
    m = p[1]
    gE.append(R / m ** 2)
    gJ.append(J / m)
    mp.append(m)
    nomes.append("%d%d" % p)
for p, q_ in CRUZADOS:
    m = p[1]
    R, J, _, _ = taxas_sint({p: 1.0, q_: 1.0})
    Ri, Ji, _, _ = taxas_sint({p: 1.0, q_: 1j})
    R -= m * m * (gE[PROPRIOS.index(p)] + gE[PROPRIOS.index(q_)])
    J -= m * (gJ[PROPRIOS.index(p)] + gJ[PROPRIOS.index(q_)])
    Ri -= m * m * (gE[PROPRIOS.index(p)] + gE[PROPRIOS.index(q_)])
    Ji -= m * (gJ[PROPRIOS.index(p)] + gJ[PROPRIOS.index(q_)])
    gE.append(R / m ** 2)
    gJ.append(J / m)
    mp.append(m)
    nomes.append("%d%dx%d%d" % (p + q_))
    log("   (parte imaginaria do cruzado %s x %s: max |E| = %.1e, max |J| = %.1e: nao contribui)"
        % (p, q_, np.max(np.abs(Ri)), np.max(np.abs(Ji))))
gE, gJ, mp = np.array(gE), np.array(gJ), np.array(mp)
for k, nm in enumerate(nomes):
    log("   %-9s " % nm + " ".join("%+.6f" % gE[k, i] for i in iE) + " | " + " ".join("%+.6f" % gJ[k, i] for i in iJ))
log("   C_E = %.6f (gE[22,L=2]) ; C_J = %.6f (gJ[22,L=3]) ; zero exato de gE[L=2] para l = 3 (3j (3 3 2; 2 -2 0) ~ 3*2^2 - 3*4 = 0)"
    % (gE[0, 0], gJ[0, iJ[0]]))
res["pesos"] = dict(nomes=nomes, m=mp.tolist(), gE=gE[:, iE].tolist(), gJ=gJ[:, iJ].tolist())
# vies do estimador de um modo por cada par: Omega_est/Omega - 1 ~ r (m gE2/gE2_22 * ... )
log("   vies linear do estimador de um modo, Omega_est/Omega - 1 ~ b_p X_p/|h22|^2 com"
    " b_p = (m_p^2 gE2_p/(4 gE2_22) - m_p gJ3_p/(2 gJ3_22)):")
b = mp ** 2 * gE[:, 0] / (4 * gE[0, 0]) - mp * gJ[:, iJ[0]] / (2 * gJ[0, iJ[0]])
log("   " + " ; ".join("%s %+.3f" % (nm, bb) for nm, bb in zip(nomes, b)))
res["vies_linear"] = dict(zip(nomes, b.tolist()))


# ====================================================================== 2-3. substituto
def X_verdadeiros(h, sel):
    out = []
    for p in PROPRIOS:
        out.append(np.abs(h[p][sel]) ** 2)
    for p, q_ in CRUZADOS:
        out.append(np.real(h[p][sel] * np.conj(h[q_][sel])))
    return np.array(out)                                   # (npares, n)


def ajuste(y, Om0, conj, pesos="rel", grade=np.linspace(0.75, 1.30, 221)):
    """Para cada instante: min_{Omega, X} ||W (A(Omega) X - y)||; A tem linhas E (Omega^2 m^2 gE) e J (Omega m gJ)."""
    idx = [nomes.index(c) for c in conj]
    AE = (mp[idx, None] ** 2 * gE[idx][:, iE]).T            # (4, k)
    AJ = (mp[idx, None] * gJ[idx][:, iJ]).T                 # (3, k)
    n = y.shape[1]
    if pesos == "rel":                                     # cada projecao com o mesmo peso relativo
        W = 1.0 / np.abs(y)
    else:                                                  # "esc": linhas E divididas por |E_2|, J por |J_3|
        W = np.concatenate([np.repeat(1 / np.abs(y[:1]), 4, axis=0), np.repeat(1 / np.abs(y[4:5]), 3, axis=0)])
    melhor = np.full(n, np.inf)
    cbest = np.ones(n)
    res_c = []
    for c in grade:
        Om = c * Om0
        A = np.concatenate([Om[:, None, None] ** 2 * AE[None], Om[:, None, None] * AJ[None]], axis=1)   # (n,7,k)
        Aw = A * W.T[:, :, None]
        yw = (y * W).T
        AtA = np.einsum("nij,nik->njk", Aw, Aw)
        Aty = np.einsum("nij,ni->nj", Aw, yw)
        Xs = np.linalg.solve(AtA + 1e-300 * np.eye(len(idx))[None], Aty[..., None])[..., 0]
        r = np.sum((np.einsum("nij,nj->ni", Aw, Xs) - yw) ** 2, axis=1)
        res_c.append(r)
        mm = r < melhor
        melhor[mm], cbest[mm] = r[mm], c
    res_c = np.array(res_c)
    # refinamento parabolico em c
    j = np.argmin(res_c, axis=0)
    j = np.clip(j, 1, len(grade) - 2)
    ar = np.arange(n)
    y0, y1, y2 = res_c[j - 1, ar], res_c[j, ar], res_c[j + 1, ar]
    den = y0 - 2 * y1 + y2
    frac = np.where(den > 0, 0.5 * (y0 - y2) / np.where(den > 0, den, 1), 0)
    cfin = grade[j] + frac * (grade[1] - grade[0])
    Om = cfin * Om0
    A = np.concatenate([Om[:, None, None] ** 2 * AE[None], Om[:, None, None] * AJ[None]], axis=1)
    Aw = A * W.T[:, :, None]
    Xs = np.linalg.solve(np.einsum("nij,nik->njk", Aw, Aw), np.einsum("nij,ni->nj", Aw, (y * W).T)[..., None])[..., 0]
    borda = (j <= 1) | (j >= len(grade) - 2)
    return Om, Xs.T, borda


SIST = [("A", dict(q=1.2, c1=0.3, c2=-0.2)), ("q=4", dict(q=4.0, c1=0.0, c2=0.0, f0=0.006)),
        ("q=1 chi=(0.6,0.6)", dict(q=1.0, c1=0.6, c2=0.6, f0=0.006)), ("q=2", dict(q=2.0, c1=0.0, c2=0.0, f0=0.006))]
CONJ = {"S1 so (2,2)": ["22"], "S2 +22x32": ["22", "22x32"], "S3 +21": ["22", "22x32", "21"],
        "S4 +33,44": ["22", "22x32", "21", "33", "44"], "S5 +32,33x43": ["22", "22x32", "21", "33", "44", "32"]}
res["sistemas"] = {}
fig = {}
for nome_s, par in SIST:
    t1 = time.time()
    t, hh, ti = C.gerar(par["q"], par["c1"], par["c2"], f0=par.get("f0"))
    sel = (t >= ti - 60) & (t <= C.T_FIM + 30)
    t = t[sel]
    h = {k: v[sel] for k, v in hh.items()}
    del hh
    dt = t[1] - t[0]
    P, H, aa, psid, psi = C.fluxos_modo(h[(2, 2)], dt)
    tpk = t[np.argmax(aa)]
    Om_v = 0.5 * psid
    _, _, R, HB = C.fluxos_memoria(t, h)
    y = np.concatenate([R[:, iE].real.T, HB[:, iJ].imag.T])         # (7, n)
    log("")
    log("== 2. %s: decomposicao de E_2 e J_3 em pares (fracao do total, X_p verdadeiros, aproximacao circular)" % nome_s)
    Xv = X_verdadeiros(h, slice(None))
    AE_all = (mp[:, None] ** 2 * gE[:, iE]).T
    AJ_all = (mp[:, None] * gJ[:, iJ]).T
    out = {"frac": {}}
    for tq in (-1000.0, -200.0, -50.0, -10.0, 10.0):
        k = int(np.argmin(np.abs(t - tq)))
        cE = Om_v[k] ** 2 * AE_all[0] * Xv[:, k]
        cJ = Om_v[k] * AJ_all[0] * Xv[:, k]
        modeloE, modeloJ = np.sum(cE), np.sum(cJ)
        log("   t = %+7.1f: E_2 = %.3e (modelo circular/real - 1 = %+.1e) " % (tq, y[0, k], modeloE / y[0, k] - 1)
            + " ".join("%s %.1e" % (nm, c / modeloE) for nm, c in zip(nomes, cE) if abs(c / modeloE) > 1e-4))
        log("              J_3 = %.3e (modelo/real - 1 = %+.1e) " % (y[4, k], modeloJ / y[4, k] - 1)
            + " ".join("%s %.1e" % (nm, c / modeloJ) for nm, c in zip(nomes, cJ) if abs(c / modeloJ) > 1e-4))
        out["frac"][str(tq)] = dict(E2={nm: float(c / modeloE) for nm, c in zip(nomes, cE)},
                                    J3={nm: float(c / modeloJ) for nm, c in zip(nomes, cJ)},
                                    modeloE=float(modeloE / y[0, k] - 1), modeloJ=float(modeloJ / y[4, k] - 1))
    # vies previsto do estimador de um modo pelo (2,2)x(3,2)
    r32 = Xv[nomes.index("22x32")] / Xv[0]
    Om1 = (R[:, 0].real / C.C_E) / (2 * HB[:, 1].imag / C.C_J)
    reg = C.regioes(t, ti, tpk)
    for rn in ("inspiral (t_i+20, t_p-200)", "fim da inspiral (t_p-200, t_p)"):
        m = reg[rn]
        log("   %s: vies medido do estimador de um modo (mediana) %+.2e ; previsto por b_22x32 r_32 %+.2e ;"
            " pela soma linear de todos os pares %+.2e"
            % (rn.split(" (")[0], np.median(Om1[m] / Om_v[m] - 1), np.median(b[nomes.index("22x32")] * r32[m]),
               np.median(np.sum(b[:, None] * Xv[:, m] / Xv[0, m], axis=0))))
    # -------- 3. separacao
    log("== 3. %s: separacao (Omega, X_p) por instante com as 7 projecoes; erros relativos mediana/max" % nome_s)
    Om0 = Om1.copy()
    dom = (t > ti + 20) & (t < tpk + 30)
    ii = np.nonzero(dom)[0]
    ii = np.unique(np.concatenate([ii[::4], ii[t[ii] > tpk - 300]]))     # 1 M na inspiral, 0.25 M perto da fusao
    out["sep"] = {}
    for nome_c, conj in CONJ.items():
        for pesos in ("rel", "esc"):
            Om_f, Xf, borda = ajuste(y[:, ii], Om0[ii], conj, pesos)
            Omf = np.full(len(t), np.nan)
            Omf[dom] = np.interp(t[dom], t[ii], Om_f)
            X22 = np.full(len(t), np.nan)
            X22[dom] = np.interp(t[dom], t[ii], Xf[0])
            o = {"borda": int(np.sum(borda))}
            partes = []
            for rn, m in reg.items():
                mm = m & dom
                if not np.any(mm):
                    continue
                o[rn] = dict(Om=C.erro_rel(Omf, Om_v, mm), a=C.erro_rel(np.sqrt(np.abs(X22)), aa, mm))
                partes.append("%s: Omega %.1e/%.1e |h22| %.1e/%.1e" % (rn.split(" (")[0], *o[rn]["Om"], *o[rn]["a"]))
            # fase e sobreposicao (sem ruido): psi = 2 int Omega desde t_i
            fv = C.fase_acumulada(psid, t, ti, dt)
            fr = C.fase_acumulada(np.where(np.isfinite(Omf), 2 * Omf, 2 * Om0), t, ti, dt)
            kpk = int(np.argmin(np.abs(t - tpk)))
            jan = (t >= ti) & (t <= tpk + 30)
            hrec = np.sqrt(np.abs(np.where(np.isfinite(X22), X22, aa ** 2))) * np.exp(-1j * fr)
            o["fase_pico"] = float(fr[kpk] - fv[kpk])
            o["overlap"] = C.overlap_fase(hrec[jan], (aa * np.exp(-1j * fv))[jan])
            log("   %-14s %s (borda da grade %d): " % (nome_c, pesos, o["borda"]) + " | ".join(partes)
                + " | erro de fase no pico %+.3f rad ; sobreposicao %.5f" % (o["fase_pico"], o["overlap"]))
            out["sep"][nome_c + " " + pesos] = o
            if nome_s == "A" and pesos == "esc":
                fig.setdefault("A", dict(t=t - tpk, Om_v=Om_v, Om1=Om1))[nome_c] = Omf
    # separacao com so as projecoes de menor ordem (E_2, E_4, J_3) nao e possivel com mais de 1 par + Omega:
    # contagem: 3 equacoes; (Omega, X22, X22x32) = 3 incognitas
    idx = [nomes.index("22"), nomes.index("22x32")]
    AE = (mp[idx, None] ** 2 * gE[idx][:, [iE[0], iE[1]]]).T
    AJ = (mp[idx, None] * gJ[idx][:, [iJ[0]]]).T
    A3 = np.concatenate([AE, AJ])                           # 3 x 2 (a menos de Omega)
    log("   so (E_2, E_4, J_3) com (Omega, X22, X22x32): matriz angular 3x2 = %s ; numero de condicao %.1f"
        % (np.round(A3, 5).tolist(), np.linalg.cond(A3)))
    # -------- 4. observador
    iota = np.radians(50.0)
    Y = {L: float(np.real(sYlm(-2, L, 0, iota, 0.0))) for L in LS}
    hp_dot = sum(R[:, LS.index(L)].real * Y[L] for L in (2, 4, 6, 8))
    hx = -sum(HB[:, LS.index(L)].imag * Y[L] for L in (3, 5, 7))

    def K(io):
        Yi = {L: float(np.real(sYlm(-2, L, 0, io, 0.0))) for L in (2, 3, 4)}
        return -gJ[0, iJ[0]] * Yi[3] / (gE[0, iE[0]] * Yi[2] + gE[0, iE[1]] * Yi[4])
    Om_obs = K(iota) * hp_dot / (2 * hx)
    m = reg["inspiral (t_i+20, t_p-200)"]
    m2 = reg["fim da inspiral (t_p-200, t_p)"]
    o4 = dict(insp=C.erro_rel(Om_obs, Om_v, m), fim=C.erro_rel(Om_obs, Om_v, m2))
    log("== 4. %s, observador iota = 50 graus (h+ e hx separados, sem ruido): Omega_obs = K(iota) hdot+/(2 hx)" % nome_s)
    log("   erro com iota conhecido: inspiral %.1e/%.1e ; fim da inspiral %.1e/%.1e" % (*o4["insp"], *o4["fim"]))
    for di in (-10, -5, 5, 10):
        log("   iota errado por %+d graus: K'/K - 1 = %+.3f (Omega e o numero de ciclos escalam por esse fator)"
            % (di, K(iota + np.radians(di)) / K(iota) - 1))
        o4["K_%+d" % di] = float(K(iota + np.radians(di)) / K(iota) - 1)
    out["observador"] = o4
    # -------- 5. multipolos m != 0
    if nome_s in ("A", "q=4"):
        Hm = np.stack([h[k] for k in LOSC], axis=1)
        Hd = O.derivada(Hm, dt)
        calc = CalculadoraMemoria(LOSC, lmax_saida=8)
        kk = np.nonzero((t > tpk - 2000) & (t < tpk))[0][::8]
        _, _, dm = calc.partes_instantaneas(Hm[kk], Hd[kk], [(4, 4), (3, 1), (2, 1), (2, 0)])
        del Hm, Hd
        fase22 = psi[kk]                                    # h22 ~ exp(-i psi22), psi22 = 2 phi_orb
        d44 = np.unwrap(np.angle(dm[:, 0])) + fase22 * 2    # E_44 ~ hdot22 hdot22 ~ exp(-4 i phi_orb)
        d31 = np.unwrap(np.angle(dm[:, 1])) + fase22 / 2    # todos os pares com m - m' = 1 ~ exp(-i phi_orb)
        log("== 5. %s: multipolos m != 0 do fluxo de energia resolvido no tempo (t_p-2000 a t_p)" % nome_s)
        log("   arg E_44 + 4 phi_orb: variacao (max - min) %.2e rad (fase orbital acumulada no trecho: %.1f rad)"
            % (np.ptp(d44), 0.5 * (fase22[-1] - fase22[0])))
        log("   arg E_31 + phi_orb: variacao %.2e rad ; |E_21|/|E_20| max = %.1e (zero por reflexao: so L + M par)"
            % (np.ptp(d31), np.max(np.abs(dm[:, 2]) / np.abs(dm[:, 3]))))
        out["m_nao_nulo"] = dict(var44=float(np.ptp(d44)), var31=float(np.ptp(d31)),
                                 fase_orb=float(0.5 * (fase22[-1] - fase22[0])),
                                 amp44=float(np.median(np.abs(dm[:, 0]) / np.abs(dm[:, 3]))),
                                 amp31=float(np.median(np.abs(dm[:, 1]) / np.abs(dm[:, 3]))))
        log("   |E_44|/|E_20| mediano = %.2e ; |E_31|/|E_20| mediano = %.2e" % (out["m_nao_nulo"]["amp44"], out["m_nao_nulo"]["amp31"]))
    res["sistemas"][nome_s] = out
    del h, R, HB
    log("   (%.0f s)" % (time.time() - t1))


def limpa(x):
    if isinstance(x, dict):
        return {str(k): limpa(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [limpa(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    return x


with open(os.path.join(C.RES, "exp31_varios_modos.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(C.RES, "exp31_varios_modos.json"), "w") as f:
    json.dump(limpa(res), f, indent=1)

import matplotlib                                         # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                           # noqa: E402
C.estilo(plt)
fg, ax = plt.subplots(1, 2, figsize=(10.5, 3.9))
F = fig["A"]
x = ax[0]
m = (F["t"] > -3000) & (F["t"] < 25)
x.semilogy(F["t"][m], np.abs(F["Om1"][m] / F["Om_v"][m] - 1), color=C.COR["laranja"], lw=0.9,
           label="um modo: (E₂, J₃) → Ω (exp09)")
for nome_c, cor in (("S2 +22x32", C.COR["verde"]), ("S4 +33,44", C.COR["azul"])):
    x.semilogy(F["t"][m], np.abs(F[nome_c][m] / F["Om_v"][m] - 1) + 1e-12, color=cor, lw=0.9,
               label="7 projeções (pesos esc.), pares " + nome_c.split(" ")[0])
x.set_xlabel("t - t_pico (M)")
x.set_ylabel("|Ω reconstruída / Ω verdadeira − 1|")
x.set_ylim(1e-6, 1)
x.set_title("Sistema A: separar os modos melhora Ω (sem ruído)", loc="left", fontsize=9)
x.legend(frameon=False, fontsize=7)
x = ax[1]
nn = ["22", "21", "33", "32", "44", "22x32", "33x43"]
xs = np.arange(len(nn))
for j, (L, cor) in enumerate(((2, C.COR["azul"]), (4, C.COR["verde"]), (6, C.COR["laranja"]))):
    v = [mp[nomes.index(n_)] ** 2 * gE[nomes.index(n_), LS.index(L)] for n_ in nn]
    x.bar(xs + (j - 1) * 0.27, v, width=0.27, color=cor, label="E_L, L = %d" % L)
x.set_xticks(xs)
x.set_xticklabels(nn)
x.axhline(0, color=C.COR["texto"], lw=0.6)
x.set_ylabel("peso m² gE (par de amplitude unitária)")
x.set_title("Pesos angulares do fluxo de energia por par de modos", loc="left", fontsize=9)
x.legend(frameon=False, fontsize=7)
fg.tight_layout()
fg.savefig(os.path.join(C.FIG, "e31_varios_modos.png"), dpi=140)
log("tempo total %.0f s" % (time.time() - T0))
with open(os.path.join(C.RES, "exp31_varios_modos.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
