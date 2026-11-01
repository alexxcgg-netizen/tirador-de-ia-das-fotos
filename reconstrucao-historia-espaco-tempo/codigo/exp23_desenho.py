"""L04, tarefa 4: desenho otimo das fronteiras das bandas (criterios D e E) para 4 fontes; o otimo e universal em M f?

Le resultados/exp23_prep_<fonte>.npz (exp23_preparar.py). K bandas: [10 Hz, c_1], [c_1, c_2], ..., [c_{K-1}, fim] com os
cortes c_k nas bordas da grade comum em M f. Medidas por banda: deslocamento (polarizacao +) e spin (x).
Parametros theta = (q, chi1, chi2, ln M, iota, ln D), branqueados pelas larguras a priori S = (2, 0.5, 0.5, 0.3, 0.5, 0.5).

Modelos de ruido (F = Fisher dos parametros; Ghat = Gram das bandas somando as elementares):
  'diag'  : cada banda medida com erro relativo 1/rho_b, rho_b = sqrt(Ghat_bb) (o modelo pedido: 1/SNR da memoria
            nula naquela banda): F = sum_b rho_b^2 g_b g_b^T, g_b = d ln V_b / d theta;
  'corr'  : bandas correlacionadas pelo detector: F = sum_bb' g_b Ghat_bb' g_b'^T (sinal = soma das bandas);
  'unif'  : erro relativo uniforme eps = 0.01 em todas as bandas (sem detector; testa a universalidade em M f).
Criterios no Fisher branqueado Ft = S F S: D = sum_i ln(1 + lambda_i) (ganho de informacao x2, em nats), E = lambda_min.
Busca exaustiva para K = 2..5 (cortes na grade); K = 6, 8 por descida coordenada com reinicios.

Saida: resultados/exp23_desenho.txt, .json; figuras/e23_desenho.png
"""
import itertools
import json
import os
import time

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = ("A", "q3", "M30", "M150")
ROT = {"A": "A (M=65, q=1,2)", "q3": "q=3, chi=(0,6;0)", "M30": "M=30", "M150": "M=150"}
SPRI = np.array([2.0, 0.5, 0.5, 0.3, 0.5, 0.5])
linhas = []
OUT = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


class Fonte:
    def __init__(self, nome, det="CE", inicio_mf=None):
        d = np.load(os.path.join(RAIZ, "resultados", "exp23_prep_%s.npz" % nome))
        self.nome = nome
        par = d["par"]                                   # q, c1, c2, M, iota, D
        self.M, self.D = par[3], par[5]
        self.mf = d["bordas_mf"].copy()
        self.hz = d["bordas_hz"].copy()
        V = d["Vb"].copy()                               # (n, 2) bandas elementares nitidas (desl, spin)
        dV = d["dVb"].copy()                             # (n, 2, 6) derivadas brutas em (q, c1, c2, M, iota, D)
        dV[:, :, 3] *= self.M                            # -> d/d ln M
        dV[:, :, 5] *= self.D                            # -> d/d ln D
        Gd, Gs = d["Gd_" + det].copy(), d["Gs_" + det].copy()
        i0 = 0
        if inicio_mf is not None:                        # descarta as bandas abaixo de inicio_mf (teste de universalidade)
            i0 = int(np.argmin(np.abs(self.mf - inicio_mf)))
        self.mf, self.hz = self.mf[i0:], self.hz[i0:]
        V, dV, Gd, Gs = V[i0:], dV[i0:], Gd[i0:, i0:], Gs[i0:, i0:]
        self.n = len(V)
        # somas acumuladas para bandas compostas
        self.cV = np.concatenate([np.zeros((1, 2)), np.cumsum(V, axis=0)])
        self.cdV = np.concatenate([np.zeros((1, 2, 6)), np.cumsum(dV, axis=0)])
        self.cG = {}
        for k, G in (("d", Gd), ("s", Gs)):
            c = np.zeros((self.n + 1, self.n + 1))
            c[1:, 1:] = np.cumsum(np.cumsum(G, axis=0), axis=1)
            self.cG[k] = c

    def bandas(self, cortes):
        b = [0] + list(cortes) + [self.n]
        V = np.array([self.cV[b[i + 1]] - self.cV[b[i]] for i in range(len(b) - 1)])          # (K, 2)
        dV = np.array([self.cdV[b[i + 1]] - self.cdV[b[i]] for i in range(len(b) - 1)])       # (K, 2, 6)
        Gh = {}
        for k in ("d", "s"):
            c = self.cG[k]
            Gh[k] = np.array([[c[b[i + 1], b[j + 1]] - c[b[i], b[j + 1]] - c[b[i + 1], b[j]] + c[b[i], b[j]]
                               for j in range(len(b) - 1)] for i in range(len(b) - 1)])
        return V, dV, Gh

    def fisher(self, cortes, modelo):
        V, dV, Gh = self.bandas(cortes)
        F = np.zeros((6, 6))
        for t, k in ((0, "d"), (1, "s")):
            g = dV[:, t, :] / V[:, t][:, None]                   # (K, 6) d ln V / d theta
            if modelo == "diag":
                F += (g.T * np.diag(Gh[k])) @ g
            elif modelo == "corr":
                F += g.T @ Gh[k] @ g
            elif modelo == "unif":
                F += g.T @ g / 0.01 ** 2
        return SPRI[:, None] * F * SPRI[None, :]


def criterios(Ft):
    lam = np.linalg.eigvalsh(0.5 * (Ft + Ft.T))
    lam = np.clip(lam, 0, None)
    return float(np.sum(np.log1p(lam))), float(lam[0]), lam


def otimizar(fo, K, modelo, crit):
    """Cortes otimos (indices) para K bandas; crit 'D' ou 'E'."""
    j = 0 if crit == "D" else 1
    melhor = None
    cand = range(1, fo.n)
    if K == 1:
        Ft = fo.fisher([], modelo)
        return [], criterios(Ft)
    if K <= 5:
        for c in itertools.combinations(cand, K - 1):
            v = criterios(fo.fisher(list(c), modelo))
            if melhor is None or v[j] > melhor[1][j]:
                melhor = (list(c), v)
        return melhor
    rng = np.random.default_rng(K)
    for rep in range(8):
        c = sorted(rng.choice(list(cand), K - 1, replace=False).tolist())
        v = criterios(fo.fisher(c, modelo))
        mud = True
        while mud:
            mud = False
            for i in range(K - 1):
                lo = c[i - 1] + 1 if i > 0 else 1
                hi = c[i + 1] - 1 if i < K - 2 else fo.n - 1
                for nv in range(lo, hi + 1):
                    c2 = list(c)
                    c2[i] = nv
                    v2 = criterios(fo.fisher(c2, modelo))
                    if v2[j] > v[j] + 1e-12:
                        c, v, mud = c2, v2, True
        if melhor is None or v[j] > melhor[1][j]:
            melhor = (c, v)
    return melhor


def geom(fo, K):
    """Cortes geometricamente espacados em M f entre a primeira borda e a ultima da grade (referencia ingenua)."""
    if K == 1:
        return []
    alvo = np.geomspace(fo.mf[0], fo.mf[-1], K + 1)[1:-1]
    c = sorted(set(int(np.argmin(np.abs(fo.mf - a))) for a in alvo))
    return [x for x in c if 0 < x < fo.n]


if __name__ == "__main__":
    t0 = time.time()
    res = {}
    log("Desenho otimo de bandas: cortes c_k (Hz | M f), criterios D = sum ln(1+lambda) e E = lambda_min do Fisher branqueado")
    log("larguras a priori (q, chi1, chi2, ln M, iota, ln D) = %s" % SPRI.tolist())
    for det in ("CE", "ET"):
        for modelo in ("diag", "corr"):
            log()
            log("=== detector %s, ruido '%s' ===" % (det, modelo))
            for nome in FONTES:
                fo = Fonte(nome, det)
                for K in (1, 2, 3, 4, 5, 6):
                    if det == "ET" and K > 4:
                        continue
                    for crit in ("D", "E"):
                        c, (Dv, Ev, lam) = otimizar(fo, K, modelo, crit)
                        cg = geom(fo, K)
                        Dg, Eg, _ = criterios(fo.fisher(cg, modelo))
                        Fpost = np.linalg.inv(fo.fisher(c, modelo) + np.eye(6))
                        red = np.sqrt(np.diag(Fpost))                      # desvio a posteriori / a priori
                        log("  %-5s K=%d %s-otimo: cortes %s Hz | Mf %s ; D %.3f E %.2e (geometrico: D %.3f E %.2e) ; "
                            "sigma_post/sigma_prior %s"
                            % (nome, K, crit, ",".join("%.1f" % fo.hz[i] for i in c),
                               ",".join("%.4f" % fo.mf[i] for i in c), Dv, Ev, Dg, Eg,
                               " ".join("%.2f" % z for z in red)))
                        res["%s|%s|%s|K%d|%s" % (det, modelo, nome, K, crit)] = dict(
                            cortes_hz=[float(fo.hz[i]) for i in c], cortes_mf=[float(fo.mf[i]) for i in c], D=Dv, E=Ev,
                            D_geom=Dg, E_geom=Eg, lam=lam.tolist(), red=red.tolist())
    # universalidade: erro relativo uniforme, inicio comum em M f
    log()
    log("=== universalidade em M f: ruido 'unif' (erro relativo 1% por banda), todas as fontes desde M f = 0.0074 ===")
    for nome in FONTES:
        fo = Fonte(nome, "CE", inicio_mf=0.0074)
        for K in (2, 3, 4):
            for crit in ("D", "E"):
                c, (Dv, Ev, lam) = otimizar(fo, K, "unif", crit)
                log("  %-5s K=%d %s-otimo: cortes Mf %s (Hz %s) ; D %.4f E %.4e"
                    % (nome, K, crit, ",".join("%.4f" % fo.mf[i] for i in c), ",".join("%.1f" % fo.hz[i] for i in c), Dv, Ev))
                res["unif|%s|K%d|%s" % (nome, K, crit)] = dict(cortes_mf=[float(fo.mf[i]) for i in c], D=Dv, E=Ev)
    # o mesmo com CE e inicio comum (isola o efeito da curva de ruido)
    log()
    log("=== mesmo inicio M f = 0.0074, ruido CE 'corr' (o que muda e so a curva de ruido em Hz) ===")
    for nome in FONTES:
        fo = Fonte(nome, "CE", inicio_mf=0.0074)
        for K in (2, 3):
            c, (Dv, Ev, lam) = otimizar(fo, K, "corr", "D")
            log("  %-5s K=%d D-otimo: cortes Mf %s (Hz %s) ; D %.4f" % (nome, K, ",".join("%.4f" % fo.mf[i] for i in c),
                                                                       ",".join("%.1f" % fo.hz[i] for i in c), Dv))
            res["CEcomum|%s|K%d|D" % (nome, K)] = dict(cortes_mf=[float(fo.mf[i]) for i in c], D=Dv)
    OUT["res"] = res
    # paisagem K = 2 para a figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"axes.facecolor": "#fcfcfb", "figure.facecolor": "#fcfcfb", "axes.edgecolor": "#52514e",
                         "text.color": "#52514e", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e", "grid.color": "#e6e5e0", "font.size": 9})
    cores = {"A": "#2a78d6", "q3": "#eb6834", "M30": "#1baf7a", "M150": "#52514e"}
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
    pais = {}
    for nome in FONTES:
        for i, (modelo, ini, tit) in enumerate((("corr", None, "CE, bandas correlacionadas"),
                                                ("diag", None, "CE, erro 1/SNR por banda (diagonal)"),
                                                ("unif", 0.0074, "erro relativo uniforme, início M f = 0,0074"))):
            fo = Fonte(nome, "CE", inicio_mf=ini)
            vals = [criterios(fo.fisher([c], modelo))[0] for c in range(1, fo.n)]
            base = criterios(fo.fisher([], modelo))[0]
            ax[i].semilogx(fo.mf[1:], np.array(vals) - base, "-", color=cores[nome], label=ROT[nome])
            pais["%s|%s" % (nome, modelo)] = dict(mf=fo.mf[1:].tolist(), ganho=(np.array(vals) - base).tolist())
            ax[i].set_title(tit, fontsize=9)
            ax[i].set_xlabel("corte $Mf$ (K = 2)")
            ax[i].set_ylabel("ganho em D sobre uma banda (nats x2)")
            ax[i].grid(True, which="both")
    ax[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e23_desenho.png"), dpi=150)
    OUT["paisagem_K2"] = pais
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RAIZ, "resultados", "exp23_desenho.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(os.path.join(RAIZ, "resultados", "exp23_desenho.json"), "w") as fh:
        json.dump(OUT, fh, indent=1, default=float)
