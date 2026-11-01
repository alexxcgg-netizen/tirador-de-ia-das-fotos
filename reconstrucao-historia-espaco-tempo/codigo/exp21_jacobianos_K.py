"""L03/L04, tarefa 2: quantos numeros independentes cada janela acrescenta? Jacobianos 4K x 6 (e 2K x 6, e com phi).

Sistema A (exp07), iota = 50 graus, D = 400 Mpc, NRHybSur3dq8_CCE, nivel A, deslocamento de janela.
Janelas [t_i(f_j), fim] com f_j = 10 Hz * (f_max/10 Hz)^(j/48), j = 0..48, M f_max = 0.012 (fim da inspiral);
o conjunto de K janelas e o subconjunto j = 0, 48/(K-1), ..., 48 (K = 1: so 10 Hz; K = 49: funcao de janela
continua amostrada).

Conjuntos de observaveis:
  T0: as quatro memorias, so m = 0 (6 parametros q, chi1, chi2, M, iota, D);
  O0: so deslocamento e spin (o que um interferometro mede), m = 0;
  T, O: idem com todos os m (7 parametros, com o azimute phi).
Saidas: ln|y| (precisao relativa); colunas escaladas como na revisao R4 (0.1 em q e chi, 1 Msol, 0.01 rad, 0.01 D,
0.01 rad em phi). Os jacobianos sao conferidos com passos h e h/2.

Parte 2: so as BANDAS da inspiral (m(f_j) - m(f_{j+1}), sem a ultima janela que contem a fusao), substituto contra o
modelo PN (exp20_pn_comum: H_20, H_40 de Cunningham et al. 2025 e spin pela primeira lei com beta ABFO), ordem por
ordem: mostra qual ordem PN acrescenta cada valor singular.

Saida: resultados/exp21_jacobianos_K.txt, .json, .npz; figura figuras/e21_valores_singulares.png
"""
import json
import os
import sys
import time

import numpy as np
import sympy as sp

import exp20_comum as C
from deteccao import MSUN_S, MPC_S
from harmonicos import sYlm

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
linhas = []
OUT = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


NJ = 48
KS = [1, 2, 3, 4, 5, 7, 9, 13, 25, 49]
NOMES6 = ("q", "c1", "c2", "M", "iota", "D")
NOMES7 = NOMES6 + ("phi",)
LIMIARES = (1e-2, 1e-3, 1e-4, 1e-5)


def grade(par, mf_max=0.012):
    fmax = mf_max / (par["M"] * MSUN_S)
    return [10.0 * (fmax / 10.0) ** (j / NJ) for j in range(NJ + 1)]


def sub_idx(K):
    if K == 1:
        return [0]
    return [int(round(j * NJ / (K - 1))) for j in range(K)]


def linhas_de(J, idx, ntip):
    """Seleciona as linhas das janelas idx num jacobiano (janela, tipo) achatado."""
    rows = []
    for j in idx:
        rows += list(range(j * ntip, (j + 1) * ntip))
    return J[rows]


def svd(J, par, nomes):
    s, Vt = C.svd_escalado(J, par, nomes)
    return s, Vt


# ------------------------------------------------------------------ modelo PN das bandas (no observador)
def modelo_pn(ordem):
    """Funcao (par, freqs) -> matriz (K-1, 2) das bandas [f_j, f_{j+1}] de deslocamento e spin no observador (PN)."""
    import exp20_pn_comum as P
    from scipy.integrate import quad
    lead2, ser2 = P.chaves("H20")
    lead4, ser4 = P.chaves("H40")
    norm = P.expr("norm").subs(P.M, 1)
    e20 = -norm * lead2 * P.serie_em_v(ser2, ordem).subs(P.v, sp.sqrt(P.x))
    e40 = -norm * lead4 * P.serie_em_v(ser4, ordem).subs(P.v, sp.sqrt(P.x))
    Eb = P.E_lig_pos(7)
    dEb = sp.diff(P.nu * P.x / 2 * P.serie_em_v(sp.expand(Eb / (P.nu * P.x / 2)), ordem).subs(P.v, sp.sqrt(P.x)), P.x)
    MOD = tuple(k for k in P.MODOS_ABFO if k not in ((3, 1), (4, 2), (4, 1)))
    r = P.razao_serie(("spin", (3, 0)), MOD, 3, por="J", racionalizar=False)
    rb = sum(sp.expand(r).coeff(P.v, k) * P.v ** k for k in range(min(ordem, 3) + 1))
    syms = (P.nu, P.delta, P.s, P.sigma, P.chis, P.chia)
    f20 = sp.lambdify((P.x,) + syms, e20, "numpy")
    f40 = sp.lambdify((P.x,) + syms, e40, "numpy")
    fde = sp.lambdify((P.x,) + syms, dEb, "numpy")
    frb = sp.lambdify((P.v,) + syms, rb, "numpy")

    def F(par, freqs):
        sb = P.subs_num(par["q"], par["c1"], par["c2"])
        a = tuple(sb[k] for k in syms)
        Ms = par["M"] * MSUN_S
        Ds = par["D"] * MPC_S
        xs = [(np.pi * Ms * f) ** (2 / 3) for f in freqs]
        Y2 = sYlm(-2, 2, 0, par["iota"], 0.0).real
        Y4 = sYlm(-2, 4, 0, par["iota"], 0.0).real
        Y3 = sYlm(-2, 3, 0, par["iota"], 0.0).real
        out = []
        for xa, xb in zip(xs[:-1], xs[1:]):
            d = (f20(xa, *a) - f20(xb, *a)) * Y2 + (f40(xa, *a) - f40(xb, *a)) * Y4
            sp30 = quad(lambda xx: float(np.real(frb(np.sqrt(xx), *a))) * xx ** -1.5 * fde(xx, *a), xb, xa,
                        epsabs=0, epsrel=1e-13)[0]
            # convencao do codigo: banda = m(f_a) - m(f_b) = acumulado de f_a a f_b
            out.append([-d * Ms / Ds, sp30 * Y3 * Ms * Ms / Ds])
        return np.array(out)
    return F


def jac_pn(F, par, freqs, nomes=NOMES6):
    passos = dict(q=2e-3, c1=2e-3, c2=2e-3, M=5e-4 * par["M"], iota=1e-4, D=1e-3 * par["D"])
    y0 = np.log(np.abs(F(par, freqs).ravel()))
    cols = []
    for n in nomes:
        d = 0
        for k, c in zip((-2, -1, 1, 2), (1 / 12, -8 / 12, 8 / 12, -1 / 12)):
            p = dict(par)
            p[n] = par[n] + k * passos[n]
            d = d + c * np.log(np.abs(F(p, freqs).ravel()))
        cols.append(d / passos[n])
    return np.array(cols).T, y0


if __name__ == "__main__":
    t0 = time.time()
    A = C.PAR_A
    fr = grade(A)
    log("Sistema A, iota = 50 graus, D = 400 Mpc; grade de %d janelas de %.2f a %.2f Hz (M f de %.4f a %.4f)"
        % (len(fr), fr[0], fr[-1], fr[0] * A["M"] * MSUN_S, fr[-1] * A["M"] * MSUN_S))
    J = {}
    arq = os.path.join(RAIZ, "resultados", "exp21_jacobianos_K.npz")
    if "--reusar" in sys.argv and os.path.exists(arq):
        d = np.load(arq)
        for nome, nomes in (("T0", NOMES6), ("T", NOMES7)):
            J[nome] = (d[nome + "_J"], d[nome + "_J2"], d[nome + "_y0"], nomes)
            errc = np.linalg.norm(J[nome][0] - J[nome][1], axis=0) / np.linalg.norm(J[nome][0], axis=0)
            log("  jacobiano %s (%d x %d) relido de exp21_jacobianos_K.npz ; |J(h)-J(h/2)|/|J| por coluna: %s"
                % (nome, J[nome][0].shape[0], J[nome][0].shape[1], " ".join("%.1e" % e for e in errc)))
    for nome, todos_m, nomes in (("T0", False, NOMES6), ("T", True, NOMES7)):
        if nome in J:
            continue
        t1 = time.time()
        Jh, y0 = C.jacobiano(A, fr, nomes=nomes, todos_m=todos_m)
        p2 = dict(q=1e-3, c1=1e-3, c2=1e-3, M=2.5e-4 * A["M"], iota=5e-5, D=5e-4 * A["D"], phi=5e-5)
        Jh2, _ = C.jacobiano(A, fr, nomes=nomes, todos_m=todos_m, passos=p2)
        errc = np.linalg.norm(Jh - Jh2, axis=0) / np.linalg.norm(Jh, axis=0)
        log("  jacobiano %s (%d x %d): %.0f s ; |J(h)-J(h/2)|/|J| por coluna: %s"
            % (nome, Jh.shape[0], Jh.shape[1], time.time() - t1, " ".join("%.1e" % e for e in errc)))
        J[nome] = (Jh, Jh2, y0, nomes)
    np.savez(arq,
             **{k + "_J": v[0] for k, v in J.items()}, **{k + "_J2": v[1] for k, v in J.items()},
             **{k + "_y0": v[2] for k, v in J.items()}, freqs=np.array(fr))

    log()
    log("1) JANELAS ATE O FIM (fusao incluida): valores singulares (escalas R4) em funcao de K")
    tab = {}
    for conj, base, tipos_idx in (("T0", "T0", [0, 1, 2, 3]), ("O0", "T0", [0, 1]), ("T", "T", [0, 1, 2, 3]),
                                  ("O", "T", [0, 1])):
        Jh, Jh2, y0, nomes = J[base]
        Jt = Jh.reshape(len(fr), 4, -1)[:, tipos_idx, :].reshape(len(fr) * len(tipos_idx), -1)
        Jt2 = Jh2.reshape(len(fr), 4, -1)[:, tipos_idx, :].reshape(len(fr) * len(tipos_idx), -1)
        log("  conjunto %s (%s; %d parametros)" % (conj, "+".join(C.TIPOS[i][:4] for i in tipos_idx), len(nomes)))
        tab[conj] = {}
        for K in KS:
            idx = sub_idx(K)
            Jk = linhas_de(Jt, idx, len(tipos_idx))
            Jk2 = linhas_de(Jt2, idx, len(tipos_idx))
            s, Vt = svd(Jk, A, nomes)
            s2, _ = svd(Jk2, A, nomes)
            dif = np.max(np.abs(s2 / s - 1)[: min(len(s), len(s2))])
            kmin = {lim: int(np.sum(s > lim)) for lim in LIMIARES}
            log("    K=%2d: %s | /sqrt(K): min %.2e | h vs h/2 %.0e | #(sigma>1e-2,1e-3,1e-4,1e-5) = %s"
                % (K, " ".join("%.3e" % x for x in s), s[-1] / np.sqrt(K), dif,
                   ",".join(str(kmin[l]) for l in LIMIARES)))
            tab[conj][K] = dict(s=s.tolist(), dif=dif, v_fraca=Vt[-1].tolist())
        # K minimo para posto completo acima de cada limiar
        npar = len(nomes)
        for lim in LIMIARES:
            ks = [K for K in KS if len(tab[conj][K]["s"]) >= npar and tab[conj][K]["s"][npar - 1] > lim]
            log("    K minimo com %d valores singulares > %.0e: %s" % (npar, lim, ks[0] if ks else "nenhum K <= 49"))
        Vf = np.array(tab[conj][KS[-1]]["v_fraca"])
        log("    direcao mais fraca em K=49 (unidades das escalas, %s): %s" % (",".join(nomes), " ".join("%+.3f" % z for z in Vf)))
    OUT["janelas"] = tab

    log()
    log("2) SO AS BANDAS DA INSPIRAL (sem a janela final), deslocamento + spin, m = 0: substituto contra PN")
    Jh = J["T0"][0].reshape(len(fr), 4, -1)
    y0 = J["T0"][2].reshape(len(fr), 4)                   # valores brutos (nao logaritmos)
    # jacobiano das bandas a partir dos de janelas: d ln|m_a - m_b| = (m_a dln m_a - m_b dln m_b)/(m_a - m_b)
    tabb = {}
    for K in [3, 4, 5, 7, 9, 13, 25, 49]:
        idx = sub_idx(K)
        rows = []
        for ja, jb in zip(idx[:-1], idx[1:]):
            for ti in (0, 1):
                ma, mb = y0[ja, ti], y0[jb, ti]
                rows.append((ma * Jh[ja, ti] - mb * Jh[jb, ti]) / (ma - mb))
        Jb = np.array(rows)
        s, _ = svd(Jb, A, NOMES6)
        tabb[K] = dict(sub=s.tolist())
    # PN
    for ordem in (0, 2, 3, 4, 5, 6, 7):
        t1 = time.time()
        F = modelo_pn(ordem)
        for K in [3, 4, 5, 7, 9, 13, 25, 49]:
            idx = sub_idx(K)
            Jp, yp = jac_pn(F, A, [fr[j] for j in idx])
            s, _ = svd(Jp, A, NOMES6)
            tabb[K]["pn%d" % ordem] = s.tolist()
            if K == 9:
                # comparar valores: bandas PN contra substituto
                sub_b = []
                for ja, jb in zip(idx[:-1], idx[1:]):
                    sub_b.append([y0[ja, 0] - y0[jb, 0], y0[ja, 1] - y0[jb, 1]])
                sub_b = np.array(sub_b)
                sinal = np.sign(F(A, [fr[j] for j in idx]))
                yv = F(A, [fr[j] for j in idx])
                tabb[K]["erro_pn%d" % ordem] = (np.abs(yv) / np.abs(sub_b) - 1).tolist()
        log("  modelo PN ordem v^%d pronto (%.0f s)" % (ordem, time.time() - t1))
    for K in [3, 5, 9, 25, 49]:
        log("  K=%2d (%d bandas, %d linhas):" % (K, K - 1, 2 * (K - 1)))
        log("     substituto: " + " ".join("%.3e" % x for x in tabb[K]["sub"]))
        for ordem in (0, 2, 3, 4, 5, 6, 7):
            log("     PN v^%d    : " % ordem + " ".join("%.3e" % x for x in tabb[K]["pn%d" % ordem]))
    log("  erro relativo das bandas PN (|PN|/|sub| - 1), K=9, deslocamento e spin, por ordem:")
    for ordem in (0, 2, 3, 4, 5, 6, 7):
        e = np.array(tabb[9]["erro_pn%d" % ordem])
        log("     v^%d: desl %s | spin %s" % (ordem, " ".join("%+.1e" % z for z in e[:, 0]), " ".join("%+.1e" % z for z in e[:, 1])))
    OUT["bandas"] = {str(k): v for k, v in tabb.items()}

    # figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"axes.facecolor": "#fcfcfb", "figure.facecolor": "#fcfcfb", "axes.edgecolor": "#52514e",
                         "text.color": "#52514e", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e", "grid.color": "#e6e5e0", "font.size": 9})
    cores = ["#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#9b59b6", "#c0392b", "#7f8c8d"]
    fig, ax = plt.subplots(1, 3, figsize=(13, 4))
    for i, conj in enumerate(("T0", "O0")):
        for k in range(7 if conj.startswith("T") and conj == "T" else 6):
            ys = [tab[conj][K]["s"][k] if len(tab[conj][K]["s"]) > k else np.nan for K in KS]
            ax[i].loglog(KS, ys, "o-", color=cores[k % 7], ms=3, label="$\\sigma_%d$" % (k + 1))
        for lim in LIMIARES[:3]:
            ax[i].axhline(lim, color="#52514e", lw=0.6, ls=":")
        ax[i].set_xlabel("número de janelas K")
        ax[i].set_ylabel("valor singular (escalas R4)")
        ax[i].set_title({"T0": "quatro memórias (m=0)", "O0": "deslocamento + spin (m=0)"}[conj], fontsize=9)
        ax[i].grid(True, which="both")
    ax[0].legend(fontsize=7, ncol=2)
    for k in range(6):
        ax[2].semilogy(range(7), [tabb[25]["pn%d" % o][k] for o in (0, 2, 3, 4, 5, 6, 7)], "o-", color=cores[k], ms=3,
                       label="$\\sigma_%d$" % (k + 1))
        ax[2].axhline(tabb[25]["sub"][k], color=cores[k], lw=0.8, ls="--")
    ax[2].set_xticks(range(7))
    ax[2].set_xticklabels(["N", "1PN", "1,5PN", "2PN", "2,5PN", "3PN", "3,5PN"])
    ax[2].set_title("bandas da inspiral (K=25): PN (pontos) e substituto (tracejado)", fontsize=9)
    ax[2].set_ylabel("valor singular")
    ax[2].grid(True)
    ax[2].legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e21_valores_singulares.png"), dpi=150)
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RAIZ, "resultados", "exp21_jacobianos_K.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(os.path.join(RAIZ, "resultados", "exp21_jacobianos_K.json"), "w") as fh:
        json.dump(OUT, fh, indent=1, default=float)
