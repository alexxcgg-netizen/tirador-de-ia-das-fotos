"""Experimento 36 (L14): memorias superiores (momentos temporais do fluxo) x janelas cumulativas.

Fluxo: F(t) = d m_20/dt, taxa da memoria nula de deslocamento no multipolo (2,0) (projecao l = 2 do fluxo de energia),
de uma binaria real (NRHybSur3dq8_CCE, sistema A: M = 65 Msun, q = 1.2, chi = (0.3, -0.2)), D = 400 Mpc, numa janela
fisica fixa de dados t in [T_a, T_b] = [-4 s, +0.04 s] (t = 0 no pico do (2,2) para t0 = 0).
Funcionais (K de cada):
  momentos  mu_n = int tau^n F dt,  tau = (t - t_ref)/T, T = T_b - T_a, n = 0..K-1 (t_ref = fusao, inicio, meio)
  janelas   W_k  = int_{s_k}^{T_b} F dt, s_0 = T_a < s_1 < ... (uniformes no tempo, ou de energia igual)
Partes:
  (a) conferencia: int F = deslocamento (2,0) de janela de observaveis.memorias_observaveis (com t_i no instante T_a)
  (b) numeros de condicao dos operadores K x N (L^2: linhas l_i(t_j) sqrt(w_j)), K = 1..24, com e sem normalizacao
  (c) reconstrucao da curva de memoria m(t) a partir de K funcionais com ruido independente sigma = eps * Delta m
  (d) Fisher sobre theta = (ln A, ln M, q, chi1, chi2, t0): modelo 1 (ruido independente igual por medida) e
      modelo 2 (ruido branco comum na serie F: informacao retida pela projecao no espaco das linhas)
  (e) origem do tempo e inicio da janela: mudanca dos momentos quando T_a passa de -4 s para -3 s
Saida: resultados/exp36_janelas_momentos.txt, .json; figuras/e36_janelas_momentos.png
"""
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import observaveis as O                               # noqa: E402
import binarias as B                                  # noqa: E402
from deteccao import MSUN_S, MPC_S                    # noqa: E402
from harmonicos import Grade, Dfrak, ethb2_de_escalar  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "..", "figuras")
linhas = []
res = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


P0 = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2)
D_MPC = 400.0
TA, TB, FS = -4.0, 0.04, 4096.0
tg = np.arange(TA, TB + 0.5 / FS, 1 / FS)
N = len(tg)
wq = np.full(N, 1 / FS)
wq[0] = wq[-1] = 0.5 / FS                              # trapezio
Losc = B.lista_osc()

# coeficientes de Gaunt: dmem_20/du = sum_ab hdot_a conj(hdot_b) C_ab
gg = Grade(30, 60)
Y = np.array([gg.Y(-2, l, m).ravel() for (l, m) in Losc])
Y20 = gg.Y(0, 2, 0).ravel()
G = (Y * (gg.peso.ravel() * np.conj(Y20))) @ Y.conj().T
C = 0.5 * ethb2_de_escalar(2) * 0.25 * G / Dfrak(2)


def fluxo(M, q, c1, c2, devolver_mem=False):
    """Spline de F(t) (deformacao/s) em t fisico (s), t = 0 no pico; e o deslocamento (2,0) de janela desde T_a."""
    t, h, ti = O.gerar_janela(q, c1, c2, M, 10.0)
    H = np.stack([h[k] for k in Losc], axis=1)
    Hd = O.derivada(H, t[1] - t[0])
    rate = np.real(np.einsum("ta,ab,tb->t", Hd, C, Hd.conj()))
    Ms, Ds = M * MSUN_S, D_MPC * MPC_S
    ts = t * Ms
    Fphys = rate * (M * MSUN_S / Ds) / Ms                 # d(m_20 M/D)/dt em 1/s; m_20 em unidades de deformacao
    sp = CubicSpline(ts, Fphys)
    extra = None
    if devolver_mem:
        # deslocamento (2,0) de janela com t_i = T_a (em M) pela infraestrutura
        w = O.pesos_janela(t, TA / Ms)
        Bm, Am = O.gram_pesos(H, Hd, w)
        m = B.calculadoras()[0].memorias_gram(Bm, Am)
        extra = complex(m["deslocamento"][(2, 0)]) * M * MSUN_S / Ds
    del t, h, H, Hd
    return sp, extra


def amostrar(sp, t0=0.0, lnA=0.0):
    return np.exp(lnA) * sp(tg - t0)


log("(a) Conferencia do fluxo")
sp0, mem20 = fluxo(P0["M"], P0["q"], P0["c1"], P0["c2"], devolver_mem=True)
F0 = amostrar(sp0)
Dm = float(np.sum(wq * F0))
log("  int_{T_a}^{T_b} F dt = %.10e ; deslocamento (2,0) de janela (observaveis, t_i = T_a) = %.10e ; dif rel %.1e" % (
    Dm, mem20.real, abs(Dm - mem20.real) / abs(mem20.real)))
log("  N = %d amostras (fs = %.0f Hz), janela [%.2f, %.2f] s; pico de F em t = %.4f s" % (N, FS, TA, TB, tg[np.argmax(F0)]))
cum = np.concatenate([[0], np.cumsum(0.5 * (F0[1:] + F0[:-1]) / FS)])
for fr in (0.1, 0.25, 0.5, 0.75, 0.9):
    log("  fracao %.2f da memoria acumulada em t = %.4f s" % (fr, tg[np.searchsorted(cum, fr * cum[-1])]))


# ------------------------------------------------------------------ operadores
def op_momentos(K, tref):
    tau = (tg - tref) / (TB - TA)
    return np.array([tau ** n for n in range(K)]) * wq


def cortes(K, tipo, Fn=F0):
    if tipo == "uniforme":
        return TA + (TB - TA) * np.arange(K) / K
    c = np.concatenate([[0], np.cumsum(0.5 * (Fn[1:] + Fn[:-1]) / FS)])
    c = c / c[-1]
    s = [TA] + [tg[np.searchsorted(c, k / K)] for k in range(1, K)]
    return np.array(s)


def op_janelas(K, tipo):
    s = cortes(K, tipo)
    return np.array([(tg >= sk).astype(float) for sk in s]) * wq


def cond_L2(Lm, normalizar=False):
    A = Lm / np.sqrt(wq)                                   # operador em L^2: l_i(t_j) sqrt(w_j)
    if normalizar:
        A = A / np.linalg.norm(A, axis=1, keepdims=True)
    s = np.linalg.svd(A, compute_uv=False)
    return s[0] / s[-1]


TREFS = {"fusao": 0.0, "inicio": TA, "meio": 0.5 * (TA + TB)}
log()
log("(b) Numero de condicao (sigma_max/sigma_min) do operador K x N em L^2 [entre colchetes: linhas normalizadas]")
log("   K | mom(fusao) | mom(inicio) | mom(meio) | jan(uniforme) | jan(energia igual)")
conds = {}
for K in (1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24):
    r = [cond_L2(op_momentos(K, TREFS[k]), nz) for k in TREFS for nz in (False, True)]
    r += [cond_L2(op_janelas(K, k), nz) for k in ("uniforme", "energia") for nz in (False, True)]
    conds[K] = r
    log("  %2d | %.2e [%.2e] | %.2e [%.2e] | %.2e [%.2e] | %.2e [%.2e] | %.2e [%.2e]" % ((K,) + tuple(r)))
Ks = np.array([K for K in conds if K >= 4])
for j, nome in enumerate(["mom(fusao)", "mom(inicio)", "mom(meio)"]):
    y = np.log([conds[K][2 * j + 1] for K in Ks])
    a = np.polyfit(Ks, y, 1)
    log("  %s normalizado: ln cond ~ %.4f K  (fator %.3f por momento)" % (nome, a[0], np.exp(a[0])))
for j, nome in enumerate(["jan(uniforme)", "jan(energia)"]):
    y = np.log([conds[K][6 + 2 * j + 1] for K in Ks])
    a = np.polyfit(np.log(Ks), y, 1)
    log("  %s normalizado: cond ~ K^%.3f" % (nome, a[0]))
res["condicao"] = {int(k): v for k, v in conds.items()}

# ------------------------------------------------------------------ (c) reconstrucao da curva de memoria
log()
log("(c) Reconstrucao de m(t) = int_{T_a}^t F a partir de K funcionais com ruido sigma = eps |Delta m| (erro max |m_hat - m| / Delta m)")
rng = np.random.default_rng(36)


def recon_mom(K, y, tref):
    """Solucao de norma minima em L^2 (polinomio de grau K-1 em tau) pelos momentos; em base de Legendre."""
    tau = (tg - tref) / (TB - TA)
    a, b = tau[0], tau[-1]
    x = (2 * tau - (a + b)) / (b - a)
    P = np.array([np.polynomial.legendre.Legendre.basis(k)(x) for k in range(K)])     # K x N
    Mon = np.array([tau ** n for n in range(K)])
    # momentos = Mon w P^T c  ->  c = solve(Mon w P^T, y)
    Gm = (Mon * wq) @ P.T
    c = np.linalg.solve(Gm, y)
    return c @ P


def recon_jan(K, y, tipo):
    s = cortes(K, tipo)
    mk = y[0] - y                                    # m(s_k) = W_0 - W_k
    xs = np.concatenate([s, [TB]])
    ys = np.concatenate([mk, [y[0]]])
    return np.interp(tg, xs, ys)


def erro_m(mhat):
    """erro maximo na curva de memoria, em unidades da memoria total da janela"""
    return float(np.max(np.abs(mhat - cum)) / abs(cum[-1]))


log("   K | eps | mom(fusao) | mom(inicio) | jan(uniforme) | jan(energia igual)")
recs = {}
for K in (2, 4, 6, 8, 12, 16, 20):
    for eps in (0.0, 1e-6, 1e-3, 3e-2):
        out = []
        for tipo in ("fusao", "inicio"):
            Lm = op_momentos(K, TREFS[tipo])
            y0 = Lm @ F0
            er = []
            for rep in range(20 if eps > 0 else 1):
                y = y0 + eps * abs(Dm) * rng.normal(size=K)
                Fh = recon_mom(K, y, TREFS[tipo])
                er.append(erro_m(np.concatenate([[0], np.cumsum(0.5 * (Fh[1:] + Fh[:-1]) / FS)])))
            out.append(np.median(er))
        for tipo in ("uniforme", "energia"):
            Lm = op_janelas(K, tipo)
            y0 = Lm @ F0
            er = []
            for rep in range(20 if eps > 0 else 1):
                y = y0 + eps * abs(Dm) * rng.normal(size=K)
                er.append(erro_m(recon_jan(K, y, tipo)))
            out.append(np.median(er))
        recs[(K, eps)] = out
        log("  %2d | %.0e | %.2e | %.2e | %.2e | %.2e" % ((K, eps) + tuple(out)))
res["reconstrucao"] = {"%d_%g" % k: v for k, v in recs.items()}

# ------------------------------------------------------------------ (d) Fisher
log()
log("(d) Fisher sobre theta = (ln A, ln M, q, chi1, chi2, t0 [s])")
NOMES = ["lnA", "lnM", "q", "chi1", "chi2", "t0"]
hq, hc, hM = 1e-3, 1e-3, 1e-3


def derivadas(fator):
    d = np.zeros((6, N))
    d[0] = F0
    for j, (campo, hh) in enumerate([("M", hM * fator), ("q", hq * fator), ("c1", hc * fator), ("c2", hc * fator)], 1):
        pp, pm = dict(P0), dict(P0)
        if campo == "M":
            pp["M"] *= np.exp(hh)
            pm["M"] *= np.exp(-hh)
        else:
            pp[campo] += hh
            pm[campo] -= hh
        d[j] = (amostrar(fluxo(pp["M"], pp["q"], pp["c1"], pp["c2"])[0])
                - amostrar(fluxo(pm["M"], pm["q"], pm["c1"], pm["c2"])[0])) / (2 * hh)
    d[5] = -sp0.derivative()(tg)
    return d


deriv = derivadas(1.0)
deriv2 = derivadas(0.5)
for j in range(1, 5):
    log("  conferencia da derivada em %s: |D(h) - D(h/2)| / |D| = %.1e" % (
        NOMES[j], np.linalg.norm(deriv[j] - deriv2[j]) / np.linalg.norm(deriv[j])))



def cr(J, cov_inv=None):
    """Desvios de Cramer-Rao por QR (ruido branco unitario): Cov = R^-1 R^-T; e o menor valor singular relativo de J
    com colunas normalizadas (direcao mais fraca)."""
    Q, R = np.linalg.qr(J)
    Ri = np.linalg.inv(R)
    sv = np.linalg.svd(J / np.linalg.norm(J, axis=0), compute_uv=False)
    return np.sqrt(np.sum(Ri ** 2, axis=1)), sv[-1] / sv[0]


log("  modelo 1: ruido independente sigma = eps |Delta m| por medida; desvios de Cramer-Rao / eps (todos os 6 livres)")
log("   K | funcional | " + " | ".join("%8s" % n for n in NOMES) + " | sv_min/sv_max de J | var. com passo h/2")
fis1 = {}
for K in (6, 8, 10, 12, 16, 20, 24):
    for nome, Lm in [("mom(fusao)", op_momentos(K, 0.0)), ("mom(inicio)", op_momentos(K, TA)),
                     ("jan(unif)", op_janelas(K, "uniforme")), ("jan(energ)", op_janelas(K, "energia"))]:
        J = Lm @ deriv.T                                  # K x 6
        s, cI = cr(J / abs(Dm))
        s2, _ = cr(Lm @ deriv2.T / abs(Dm))
        est = float(np.max(np.abs(s2 / s - 1)))
        fis1[(K, nome)] = dict(sigma=s.tolist(), sv_rel=cI, var_h2=est)
        log("  %2d | %-11s | " % (K, nome) + " | ".join("%8.2e" % v for v in s) + " | %.1e | %.1e" % (cI, est))
res["fisher_modelo1"] = {"%d_%s" % k: v for k, v in fis1.items()}
log()
log("  modelo 1, subconjuntos (demais parametros fixos): desvios / eps")
SUB = {"(lnA,lnM,t0)": [0, 1, 5], "(lnA,lnM,q,t0)": [0, 1, 2, 5], "(lnA,lnM,q,chi1,t0)": [0, 1, 2, 3, 5]}
fis1s = {}
for K in (4, 6, 8, 12, 20):
    for nome, Lm in [("mom(fusao)", op_momentos(K, 0.0)), ("mom(inicio)", op_momentos(K, TA)),
                     ("jan(unif)", op_janelas(K, "uniforme")), ("jan(energ)", op_janelas(K, "energia"))]:
        partes = []
        for sn, idx in SUB.items():
            if len(idx) > K:
                partes.append("%s: -" % sn)
                continue
            s, svr = cr((Lm @ deriv.T / abs(Dm))[:, idx])
            s2, _ = cr((Lm @ deriv2.T / abs(Dm))[:, idx])
            fis1s[(K, nome, sn)] = dict(sigma=s.tolist(), sv_rel=svr, var_h2=float(np.max(np.abs(s2 / s - 1))))
            partes.append("%s: lnM %.2e, %s %.2e (sv %.0e, var %.0e)" % (
                sn, s[1], NOMES[idx[-2]] if len(idx) > 3 else "t0", s[-2] if len(idx) > 3 else s[-1], svr,
                fis1s[(K, nome, sn)]["var_h2"]))
        log("  %2d | %-11s | " % (K, nome) + " ; ".join(partes))
res["fisher_modelo1_sub"] = {"%d_%s_%s" % k: v for k, v in fis1s.items()}

log()
log("  modelo 2: ruido branco comum na serie F (sigma_F por amostra); informacao retida por K funcionais =")
log("  projecao das derivadas no espaco das linhas (momentos: polinomios de grau < K; janelas: constantes por partes).")
log("  razao sigma_CR(serie inteira)/sigma_CR(K funcionais) (1 = toda a informacao):")
Jfull = deriv.T                                           # N x 6
Ifull = Jfull.T @ Jfull
sfull = np.sqrt(np.diag(np.linalg.inv(Ifull)))
log("   K | funcional | " + " | ".join("%8s" % n for n in NOMES))
fis2 = {}


def base_polinomios(K, tref):
    tau = (tg - tref) / (TB - TA)
    x = (2 * tau - (tau[0] + tau[-1])) / (tau[-1] - tau[0])
    return np.array([np.polynomial.legendre.Legendre.basis(k)(x) for k in range(K)])


for K in (6, 8, 12, 16, 24, 32, 64):
    for nome in ("momentos", "jan(unif)", "jan(energ)"):
        if nome == "momentos":
            Lb = base_polinomios(K, 0.0) * np.sqrt(wq)     # mesmo espaco de linhas dos momentos (qualquer t_ref)
        else:
            Lb = op_janelas(K, "uniforme" if "unif" in nome else "energia") / np.sqrt(wq)
        Q, _ = np.linalg.qr(Lb.T)                          # N x K, base ortonormal do espaco das linhas
        Jw = Jfull * np.sqrt(wq)[:, None]
        sK, _ = cr(Q.T @ Jw)
        sfw, _ = cr(Jw)
        fis2[(K, nome)] = (sfw / sK).tolist()
        log("  %2d | %-10s | " % (K, nome) + " | ".join("%8.2e" % v for v in sfw / sK))
res["fisher_modelo2"] = {"%d_%s" % k: v for k, v in fis2.items()}

# ------------------------------------------------------------------ (e) origem do tempo e inicio da janela
log()
log("(e) Origem do tempo e inicio da janela")
for K in (4, 8):
    for tipo in ("fusao", "inicio"):
        Lm = op_momentos(K, TREFS[tipo])
        y = Lm @ F0
        # t0 desconhecido: correlacao entre t0 e os demais no modelo 1, K = 8
    log("  K=%d: momentos(fusao)/Delta m = %s" % (K, np.array2string(op_momentos(K, 0.0) @ F0 / Dm, precision=4)))
    log("       momentos(inicio)/Delta m = %s" % np.array2string(op_momentos(K, TA) @ F0 / Dm, precision=4))
# mudar o inicio da janela de -4 para -3 s, mantendo tau definido com a mesma escala T
m4 = op_momentos(10, 0.0) @ F0
mask = tg >= -3.0
m3 = (op_momentos(10, 0.0) * mask) @ F0
log("  inicio da janela -4 s -> -3 s (t_ref = fusao): variacao relativa dos momentos n=0..9:")
log("   " + " ".join("%.2e" % v for v in np.abs(m3 - m4) / np.abs(m4)))
Wu = op_janelas(10, "energia") @ F0
Wu3 = (op_janelas(10, "energia") * mask) @ F0
log("  janelas de energia igual (cortes s_k >= %.3f s): variacao relativa: %s" % (
    cortes(10, "energia")[1], " ".join("%.1e" % v for v in np.abs(Wu3 - Wu) / np.abs(Wu))))
# t0 marginalizado vs fixo, modelo 1, K = 12
for nome, Lm in [("mom(fusao)", op_momentos(12, 0.0)), ("jan(energ)", op_janelas(12, "energia"))]:
    J = Lm @ deriv.T / abs(Dm)
    s6, _ = cr(J)
    s5, _ = cr(J[:, :5])
    log("  K=12 %s: sigma(lnM)/eps com t0 livre %.2e, com t0 fixo %.2e; sigma(q)/eps %.2e / %.2e" % (
        nome, s6[1], s5[1], s6[2], s5[2]))

with open(os.path.join(RES, "exp36_janelas_momentos.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(RES, "exp36_janelas_momentos.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)

# ------------------------------------------------------------------ figura
import matplotlib                                                   # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "text.color": "#52514e", "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0",
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
Kc = sorted(conds)
ax[0].semilogy(Kc, [conds[K][1] for K in Kc], color="#2a78d6", lw=2, marker="o", ms=4, label="momentos (origem na fusão)")
ax[0].semilogy(Kc, [conds[K][3] for K in Kc], color="#2a78d6", lw=1.2, ls="--", marker="s", ms=3,
               label="momentos (origem no início)")
ax[0].semilogy(Kc, [conds[K][7] for K in Kc], color="#eb6834", lw=2, marker="o", ms=4, label="janelas uniformes")
ax[0].semilogy(Kc, [conds[K][9] for K in Kc], color="#1baf7a", lw=2, marker="o", ms=4, label="janelas de energia igual")
ax[0].set_xlabel("número de funcionais K")
ax[0].set_ylabel("número de condição (linhas normalizadas)")
ax[0].set_title("Condicionamento: momentos × janelas", loc="left", fontsize=9)
ax[0].legend(frameon=False, fontsize=7.5)
Kr = sorted({k[0] for k in recs})
ax[1].semilogy(Kr, [recs[(K, 1e-3)][0] for K in Kr], color="#2a78d6", lw=2, marker="o", ms=4, label="momentos (fusão)")
ax[1].semilogy(Kr, [recs[(K, 1e-3)][2] for K in Kr], color="#eb6834", lw=2, marker="o", ms=4, label="janelas uniformes")
ax[1].semilogy(Kr, [recs[(K, 1e-3)][3] for K in Kr], color="#1baf7a", lw=2, marker="o", ms=4, label="janelas de energia igual")
ax[1].semilogy(Kr, [recs[(K, 0.0)][0] for K in Kr], color="#2a78d6", lw=1, ls=":", label="momentos sem ruído")
ax[1].set_xlabel("número de funcionais K")
ax[1].set_ylabel("erro máximo em m(t) / memória total")
ax[1].set_title("Reconstrução da memória (ruído 1e-3 por medida)", loc="left", fontsize=9)
ax[1].legend(frameon=False, fontsize=7.5)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "e36_janelas_momentos.png"), dpi=140)
