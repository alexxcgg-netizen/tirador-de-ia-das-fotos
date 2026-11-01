"""Experimento 27b (L06): informacao mutua (KSG) e previsibilidade (R^2, validacao cruzada por binaria) dos
parametros a partir dos observaveis de memoria do conjunto do exp27_conjunto.

Informacao mutua I(alvo; vetor de observaveis) pelo estimador de Kraskov-Stoegbauer-Grassberger (algoritmo 1,
k = 5, norma do maximo), depois de transformar cada variavel em postos gaussianizados (invariante por mudancas
monotonas). Coeficiente informacional r_I = sqrt(1 - 2^(-2I)) (= |correlacao| no caso gaussiano).
R^2: HistGradientBoostingRegressor e regressao linear (referencia), GroupKFold (5 dobras) agrupando os sorteios
extrinsecos da mesma binaria intrinseca (sem vazamento).
Saidas: resultados/exp27_analise.txt e .json; figuras/e27_informacao.png
"""
import glob
import json
import os
import sys
import time

import numpy as np
from scipy.special import digamma
from scipy.spatial import cKDTree
from scipy.stats import norm, rankdata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
LINHAS = []


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


def gauss_postos(x):
    x = np.atleast_2d(x.T).T
    out = np.empty_like(x, dtype=float)
    for j in range(x.shape[1]):
        r = rankdata(x[:, j], method="ordinal")
        out[:, j] = norm.ppf(r / (len(x) + 1))
    return out


def ksg(x, y, k=5):
    """I(X;Y) em bits, KSG algoritmo 1 (norma do maximo), com transformacao gaussiana de postos."""
    X = gauss_postos(x)
    Y = gauss_postos(y)
    Z = np.hstack([X, Y])
    n = len(Z)
    tz = cKDTree(Z)
    d, _ = tz.query(Z, k=k + 1, p=np.inf)
    eps = d[:, -1]
    tx, ty = cKDTree(X), cKDTree(Y)
    nx = tx.query_ball_point(X, eps - 1e-12, p=np.inf, return_length=True) - 1
    ny = ty.query_ball_point(Y, eps - 1e-12, p=np.inf, return_length=True) - 1
    I = digamma(k) + digamma(n) - np.mean(digamma(nx + 1) + digamma(ny + 1))
    return max(I, 0.0) / np.log(2)


def r2_cv(X, y, grupos, modelo="hgb"):
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    pred = np.zeros_like(y)
    for tr, te in GroupKFold(n_splits=5).split(X, y, grupos):
        if modelo == "hgb":
            m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.06, max_leaf_nodes=31,
                                              min_samples_leaf=20, random_state=0)
        else:
            m = make_pipeline(StandardScaler(), LinearRegression())
        m.fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    return 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)


def sl(v):
    """log com sinal (observaveis de memoria cobrem ordens de grandeza e trocam de sinal)."""
    return np.sign(v) * np.log10(1 + np.abs(v) / np.median(np.abs(v)))


def main():
    t0 = time.time()
    arqs = sorted(glob.glob(os.path.join(RES, "exp27_conjunto_*.npz")))
    Ds = [dict(np.load(a)) for a in arqs]
    chaves = [k for k in Ds[0] if Ds[0][k].ndim >= 1 and Ds[0][k].shape[0] == Ds[0]["M"].shape[0]]
    d = {k: np.concatenate([D[k] for D in Ds]) for k in chaves}
    yA, rA_CE, rA_ET = Ds[0]["yA"], Ds[0]["rhoA_CE"], Ds[0]["rhoA_ET"]
    n = len(d["M"])
    grupos = d["i"].astype(int)
    log("Experimento 27b: %d amostras (%d binarias intrinsecas x sorteios extrinsecos), arquivos %d" %
        (n, len(np.unique(grupos)), len(arqs)))
    rng = np.random.default_rng(7)
    # controle do estimador KSG: gaussianas com I conhecida (y = a.x + ruido, x em 1, 4 e 9 dimensoes)
    for dim in (1, 4, 9):
        xg = rng.standard_normal((n, dim))
        for rr in (0.3, 0.9):
            yg = rr * xg.sum(1) / np.sqrt(dim) + np.sqrt(1 - rr * rr) * rng.standard_normal(n)
            log("controle KSG: dim %d, correlacao %.1f: I estimada %.3f bits, exata %.3f bits"
                % (dim, rr, ksg(xg, yg), -0.5 * np.log2(1 - rr * rr)))
    q, M, eta = d["q"], d["M"], d["eta"]
    m1, m2 = q / (1 + q), 1 / (1 + q)
    alvos = {
        "ln M": np.log(M), "q": q, "chi1": d["c1"], "chi2": d["c2"], "ln D": np.log(d["D"]), "cos iota": d["cosi"],
        "|cos iota|": np.abs(d["cosi"]), "ln M_f": np.log(d["Mf"]), "ln M_chirp": np.log(M * eta ** 0.6),
        "chi_eff": m1 * d["c1"] + m2 * d["c2"], "ln(M/D)": np.log(M / d["D"]), "ln(eta M/D)": np.log(eta * M / d["D"]),
    }
    integ = d["integ"]
    obs = {}
    obs["(a) 4 integradas, sem ruido"] = np.column_stack([sl(integ[:, j]) for j in range(4)])
    obs["(a) 4 integradas, so m=0, sem ruido"] = np.column_stack([sl(d["integ_m0"][:, j]) for j in range(4)])
    obs["(b) desl.+spin, sem ruido"] = np.column_stack([sl(integ[:, j]) for j in range(2)])
    for p, rA in (("CE", rA_CE), ("ET", rA_ET)):
        sig_id = np.abs(yA) / rA[0]
        integ_n = integ + rng.standard_normal(integ.shape) * sig_id[None, :]
        obs["(a) 4 integradas, erro ideal 1/rho+ (%s)" % p] = integ_n
        sig_b = np.array([abs(yA[0]) / rA[0], abs(yA[1]) / rA[1]])
        obs["(b) desl.+spin, ruido real (%s)" % p] = integ[:, :2] + rng.standard_normal((n, 2)) * sig_b[None, :]
        obs["(c1) MOPED 8, sem ruido (%s)" % p] = d[p + "_moped_0"]
        obs["(c1) MOPED 8, com ruido (%s)" % p] = d[p + "_moped_n"]
        obs["(c2) banco 9, sem ruido (%s)" % p] = d[p + "_banco_0"]
        obs["(c2) banco 9, com ruido (%s)" % p] = d[p + "_banco_n"]
        obs["(c3) bandas 9, com ruido (%s)" % p] = d[p + "_bandas_n"]
        obs["(c) c1+c2+c3, com ruido (%s)" % p] = np.hstack([d[p + "_moped_n"], d[p + "_banco_n"], d[p + "_bandas_n"]])
    log("SNR da memoria nula no conjunto (rede, h+): CE mediana %.2f (10%%-90%%: %.2f-%.2f) ; ET mediana %.2f (%.2f-%.2f)"
        % (np.median(d["CE_rho"][:, 0]), *np.percentile(d["CE_rho"][:, 0], [10, 90]),
           np.median(d["ET_rho"][:, 0]), *np.percentile(d["ET_rho"][:, 0], [10, 90])))
    log("Controle: degrau da serie nula contra deslocamento integrado so m = 0: max |dif rel| = %.1e"
        % np.max(np.abs(d["degrau_serie"] / d["integ_m0"][:, 0] - 1)))
    res = {"alvos": list(alvos), "obs": list(obs), "R2": {}, "R2lin": {}, "I": {}}
    log("")
    log("R^2 (HGB, validacao cruzada agrupada) | R^2 linear | I (bits, KSG k=5):")
    log("%-44s " % "observaveis \\ alvo" + " ".join("%-12s" % a for a in alvos))
    for nome, X in obs.items():
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X[:, None]
        r2, r2l, I = [], [], []
        for a, y in alvos.items():
            r2.append(r2_cv(X, y, grupos))
            r2l.append(r2_cv(X, y, grupos, "lin"))
            I.append(ksg(X, y))
        res["R2"][nome], res["R2lin"][nome], res["I"][nome] = r2, r2l, I
        log("%-44s " % nome + " ".join("%5.2f|%4.2f|%4.2f" % (a, b, c) for a, b, c in zip(r2, r2l, I)))
    log("")
    log("tempo %.0f s" % (time.time() - t0))
    with open(os.path.join(RES, "exp27_analise.json"), "w") as fh:
        json.dump(res, fh, default=float)
    with open(os.path.join(RES, "exp27_analise.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")
    # figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import exp24_comum as C
    C.estilo(plt)
    sel_obs = ["(a) 4 integradas, sem ruido", "(b) desl.+spin, sem ruido", "(b) desl.+spin, ruido real (CE)",
               "(c1) MOPED 8, com ruido (CE)", "(c) c1+c2+c3, com ruido (CE)", "(c) c1+c2+c3, com ruido (ET)"]
    R = np.array([res["R2"][o] for o in sel_obs])
    fig, ax = plt.subplots(figsize=(10, 3.8))
    im = ax.imshow(np.clip(R, 0, 1), cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(alvos)))
    ax.set_xticklabels(list(alvos), rotation=35, ha="right")
    ax.set_yticks(range(len(sel_obs)))
    ax.set_yticklabels(sel_obs)
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            ax.text(j, i, "%.2f" % R[i, j], ha="center", va="center", fontsize=7,
                    color="white" if R[i, j] > 0.6 else C.COR["texto"])
    ax.grid(False)
    ax.set_title("R² (validação cruzada agrupada por binária) dos parâmetros a partir de observáveis de memória")
    fig.colorbar(im, ax=ax, fraction=0.025)
    fig.tight_layout()
    fig.savefig(os.path.join(AQUI, "..", "figuras", "e27_informacao.png"), dpi=150)


if __name__ == "__main__":
    main()
