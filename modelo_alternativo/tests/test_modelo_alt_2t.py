"""Testes do modelo alternativo do 2º turno (python -m pytest modelo_alternativo/tests)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import modelo_alt_2t as M  # noqa: E402


@pytest.fixture(scope="module")
def hist():
    return M.carregar_historico()


def _sintetico(beta=(0.1, 0.8, -0.6), seed=0):
    rng = np.random.default_rng(seed)
    linhas = []
    for ano in M.ANOS:
        d = rng.normal(0, 0.05)
        for uf in M.UFS:
            x = rng.uniform(.25, .75)
            t = rng.uniform(.02, .3)
            z = beta[0] + beta[1] * M.logit(x) + beta[2] * t + d + rng.normal(0, .03)
            vv = rng.uniform(3e5, 2e7)
            linhas.append(dict(ano=ano, uf=uf, x=x, t=t, y=float(M.expit(z)), vv1=vv,
                               vv2=vv * 1.02, razao_vv=1.02))
    return pd.DataFrame(linhas)


def test_historico_consistente(hist):
    br = hist[hist.uf == "BR"].set_index("ano")
    assert list(br.index) == M.ANOS
    assert abs(br.loc[2022, "y"] - 0.509) < 1e-3
    assert abs(br.loc[2018, "x"] - 29.2778 / (29.2778 + 46.0314)) < 1e-6
    assert ((hist.t >= 0) & (hist.t < 1)).all()


def test_regressao_recupera_coeficientes():
    df = _sintetico()
    b = M.ajustar(df)
    assert np.allclose(b, [0.1, 0.8, -0.6], atol=0.06)


def test_loo_sem_vazamento(hist):
    """A previsão de um ano não depende do resultado de 2º turno desse ano."""
    base = M.residuos_loo(hist, anos=[2014])[2014]
    h2 = hist.copy()
    h2.loc[h2.ano == 2014, "y"] = 0.2
    alt = M.residuos_loo(h2, anos=[2014])[2014]
    assert np.allclose(base["z"], alt["z"])
    assert not np.allclose(base["r"], alt["r"])


def test_backtest_sem_vazamento(hist):
    a = M.backtest(hist, n=2000, anos=[2018])[0]
    h2 = hist.copy()
    h2.loc[h2.ano == 2018, "y"] = 0.9
    b = M.backtest(h2, n=2000, anos=[2018])[0]
    assert a["previsto"] == b["previsto"]
    assert a["real"] != b["real"]


def test_decomposicao_residuo(hist):
    for v in M.residuos_loo(hist).values():
        assert abs(np.sum(v["u"] * v["w"]) / np.sum(v["w"])) < 1e-12
        assert np.allclose(v["d"] + v["u"], v["r"])


def test_bootstrap_suavizado_preserva_media_e_variancia():
    rng = np.random.default_rng(3)
    vals = np.array([-0.3, 0.1, 0.2, -0.1, 0.35, -0.25])
    n = 400_000
    s = M._suav(vals, rng.integers(0, len(vals), n), rng.standard_normal(n))
    assert abs(s.mean() - vals.mean()) < 0.003
    # variância da distribuição suavizada = variância amostral (ddof=1) dos valores
    assert abs(s.var() - vals.var(ddof=1)) / vals.var(ddof=1) < 0.03


def test_dados_2026():
    d = M.carregar_1t_2026()
    assert set(M.UFS) <= set(d.index)
    assert ((d.x > 0) & (d.x < 1)).all()
    x_nac = np.sum(d.p * d.vv1) / np.sum((d.p + d.o) * d.vv1)
    assert abs(x_nac - 45.158 / (45.158 + 47.032)) < 0.003


def test_correcao_pesquisas_sinal():
    pq = M.pesquisas_2t_corrigidas()
    assert len(pq) >= 10
    dif = pq.lula_2p_corrigido - pq.lula_2p_bruto
    assert (np.sign(dif) == -np.sign(pq.erro_margem_1t)).all()


def test_mistura():
    rng = np.random.default_rng(0)
    nac = rng.normal(0.52, 0.06, 200_000)
    nb, wp, m_b, s_b = M.misturar_pesquisas(nac, 0.476, 0.02)
    assert 0.476 < m_b < 0.52 and s_b < 0.02 and 0.5 < wp < 1
    assert abs(nb.std() - s_b) < 1e-3 and abs(nb.mean() - m_b) < 1e-3
    sh = np.c_[nac, nac]
    sh2 = M.ajustar_ufs_ao_nacional(sh, nac, nb)
    assert np.allclose(sh2[:, 0], nb)


def test_previsao_2026_coerente():
    r = M.prever_2026(n=20_000, seed=1)
    assert r["sh"].shape == (20_000, len(r["reg"]))
    assert np.all(r["nac"] >= r["sh"].min(axis=1)) and np.all(r["nac"] <= r["sh"].max(axis=1))
    p = np.mean(r["nac"] > .5)
    assert 0 < p < 1
    i_ba, i_sc = r["reg"].index("BA"), r["reg"].index("SC")
    assert np.mean(r["sh"][:, i_ba] > .5) > 0.95 and np.mean(r["sh"][:, i_sc] > .5) < 0.05
