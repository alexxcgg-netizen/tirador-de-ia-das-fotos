"""Verificacao D3 (L06): de onde vem o R^2 ~ 0.5 de ln M a partir do MOPED com ruido em CE (exp27_analise)?

Testes: (i) reproduz o R^2 do HGB com GroupKFold; (ii) outro aprendiz (k-NN em postos e floresta aleatoria);
(iii) so a componente de amplitude do MOPED (a de ln D, = -(s_A|x)) e so o SNR verdadeiro (rho_+, rho_x sem
ruido): quanto de ln M vem da correlacao amplitude-massa dos priors (M em [40,120], D ~ D^2 em [200,1000]);
(iv) controle nulo: alvos embaralhados entre binarias.
"""
import glob
import os

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "..", "resultados")


def r2_cv(X, y, g, modelo):
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.model_selection import GroupKFold
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.preprocessing import QuantileTransformer
    from sklearn.pipeline import make_pipeline
    pred = np.zeros_like(y)
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        if modelo == "hgb":
            m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.06, max_leaf_nodes=31, random_state=0)
        elif modelo == "rf":
            m = RandomForestRegressor(n_estimators=200, min_samples_leaf=10, random_state=0, n_jobs=1)
        else:
            m = make_pipeline(QuantileTransformer(n_quantiles=200, output_distribution="normal"),
                              KNeighborsRegressor(n_neighbors=40))
        m.fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    return 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)


def main():
    arqs = sorted(glob.glob(os.path.join(RES, "exp27_conjunto_*.npz")))
    Ds = [dict(np.load(a)) for a in arqs]
    ch = [k for k in Ds[0] if Ds[0][k].ndim >= 1 and Ds[0][k].shape[0] == Ds[0]["M"].shape[0]]
    d = {k: np.concatenate([D[k] for D in Ds]) for k in ch}
    g = d["i"].astype(int)
    y = np.log(d["M"])
    eta = d["eta"]
    alvos = {"ln M": y, "ln M_chirp": np.log(d["M"] * eta ** 0.6), "ln M_f": np.log(d["Mf"])}
    X8 = d["CE_moped_n"]
    print("n = %d, binarias %d" % (len(y), len(np.unique(g))))
    conj = {"MOPED 8 com ruido (CE)": X8, "so componente lnD do MOPED (amplitude)": X8[:, [4]],
            "MOPED sem a componente lnM": np.delete(X8, 0, axis=1), "so componente lnM do MOPED": X8[:, [0]],
            "componentes lnM + lnD": X8[:, [0, 4]],
            "SNR verdadeiro (rho+, rhox, sem ruido)": d["CE_rho"]}
    for nome, X in conj.items():
        lin = []
        for an, yy in alvos.items():
            vals = [r2_cv(X, yy, g, m) for m in ("hgb", "rf", "knn")]
            lin.append("%s: hgb %.3f rf %.3f knn %.3f" % (an, *vals))
        print("%-42s | %s" % (nome, " | ".join(lin)), flush=True)
    rng = np.random.default_rng(3)
    perm = rng.permutation(np.unique(g))
    mapa = dict(zip(np.unique(g), perm))
    idx_bin = {b: np.where(g == b)[0] for b in np.unique(g)}
    y_emb = y.copy()
    for b in np.unique(g):
        src = idx_bin[mapa[b]]
        y_emb[idx_bin[b]] = y[src[0]]
    print("controle nulo (ln M embaralhado entre binarias), MOPED 8: hgb %.3f" % r2_cv(X8, y_emb, g, "hgb"))


if __name__ == "__main__":
    main()
