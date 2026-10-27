"""Testes do modelo alternativo (rodar com: python -m pytest modelo_alternativo/tests)."""
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import modelo_alt as M  # noqa: E402


def _sintetico(seed=1, dias=120, casas=("A", "B", "C", "D"), efeitos=(0.08, -0.05, 0.0, -0.03)):
    rng = np.random.default_rng(seed)
    mu = np.cumsum(np.r_[0.1, rng.normal(0, 0.01, dias - 1)])
    t, y, s2, cs = [], [], [], []
    for d in range(0, dias, 2):
        for c, h in zip(casas, efeitos):
            if rng.random() < 0.5:
                v = 0.02 ** 2
                t.append(d); y.append(mu[d] + h + rng.normal(0, math.sqrt(v))); s2.append(v); cs.append(c)
    obs = M.Observacoes(t=np.array(t), y=np.array(y), s2=np.array(s2), casa=cs)
    return obs, mu, dict(zip(casas, efeitos))


def test_kalman_recupera_nivel_e_efeitos_soma_zero():
    obs, mu, ef = _sintetico()
    t_alvo = int(obs.t.max())
    ll, m, v, h, casas, vh = M.filtro_kalman(obs, t_alvo, 0.01, 0.005, 0.1, obs.y[0], 1.0)
    assert np.isfinite(ll)
    assert abs(h.sum()) < 1e-6                      # restrição de soma zero
    verdadeiro = np.array([ef[c] for c in casas]) - np.mean(list(ef.values()))
    assert np.max(np.abs(h - verdadeiro)) < 0.03
    # nível relativo à média das casas
    assert abs(m - (mu[t_alvo] + np.mean(list(ef.values())))) < 4 * math.sqrt(v) + 0.02
    assert np.all(vh >= 0)


def test_kalman_variancia_cresce_com_horizonte():
    obs, _, _ = _sintetico()
    t = int(obs.t.max())
    v0 = M.filtro_kalman(obs, t, 0.01, 0.005, 0.1, 0.0, 1.0)[2]
    v1 = M.filtro_kalman(obs, t + 21, 0.01, 0.005, 0.1, 0.0, 1.0)[2]
    assert v1 == pytest.approx(v0 + 21 * 0.01 ** 2)


def test_mcmc_componente_sintetico():
    obs, mu, ef = _sintetico(seed=3)
    aj = M.ajustar_componente(obs, int(obs.t.max()), n_iter=400, burn=150, seed=0)
    assert 0.05 < aj["aceitacao"] < 0.9
    assert len(aj["m"]) > 10 and np.all(aj["v"] > 0)
    alvo = mu[int(obs.t.max())] + np.mean(list(ef.values()))
    assert abs(np.mean(aj["m"]) - alvo) < 0.05


def test_dados_2026_razoes_invariantes_a_base():
    d = M.carregar_2026()
    assert d.alvo == pd.Timestamp("2026-10-03")
    p1 = d.p1
    # cenários com Tarcísio/Ratinho excluídos do 1º turno
    assert not p1["obs"].fillna("").str.lower().str.contains("cenario com").any()
    # a razão Lula/Flávio não depende da base (votos totais ou válidos): é a publicada
    def_ = p1["pt_v"].notna()
    assert def_.sum() > 40
    assert np.allclose((p1["pt_v"] / p1["opp_v"])[def_], (p1["lula"] / p1["flavio"])[def_])
    # uma linha publicada em válidos (bni = 0) fica igual; em totais, é reescalada
    valida = pd.DataFrame({"pt": [45.0], "opp": [42.0], "bni": [0.0], "m": [13.0]})
    pt, opp, dem, _ = M._validos_1t(valida["pt"], valida["opp"], valida["bni"], valida[["m"]], None)
    assert (pt[0], opp[0], dem[0]) == (45.0, 42.0, 13.0)
    total = pd.DataFrame({"pt": [42.0], "opp": [40.0], "bni": [7.0], "m": [11.0]})
    pt, opp, dem, _ = M._validos_1t(total["pt"], total["opp"], total["bni"], total[["m"]], None)
    assert pt[0] == pytest.approx(42 / 0.93) and pt[0] + opp[0] + dem[0] == pytest.approx(100)
    # fatias válidas somam 100 quando bni conhecido
    ok = p1["bni"].notna()
    assert np.allclose((p1["pt_v"] + p1["opp_v"] + p1["dem_v"])[ok], 100)
    assert len(d.comps["zq"]) > 50 and len(d.comps["z1"]) > 40


def test_historico_so_ate_vespera():
    for ano in M.ANOS_HIST:
        d = M.carregar_historico(ano)
        lim = pd.Timestamp(M.ELEICOES[ano]["t1"])
        assert (pd.to_datetime(d.p1["campo_fim"]) < lim).all()
        if len(d.p2):
            assert (pd.to_datetime(d.p2["campo_fim"]) < lim).all()
    assert len(M.carregar_historico(2014).p2) == 0     # não houve 2T pré-1T em 2014


def _pool_fake():
    erros = [
        {"ano": 2014, "erro": {"z1": -0.3, "z2": -0.2, "zq": None},
         "nucleo12": np.array([[0.1, 0.0], [-0.1, 0.05], [0.0, -0.05]]), "nucleoq": np.array([])},
        {"ano": 2018, "erro": {"z1": 0.05, "z2": -0.4, "zq": -0.1},
         "nucleo12": np.array([[0.2, 0.1], [-0.2, -0.1]]), "nucleoq": np.array([0.05, -0.05])},
        {"ano": 2022, "erro": {"z1": -0.02, "z2": -0.5, "zq": -0.2},
         "nucleo12": np.array([[0.1, -0.1], [-0.1, 0.1]]), "nucleoq": np.array([0.1, -0.1, 0.0])},
    ]
    return M.montar_pool(erros)


def test_bootstrap_neutro_simetrico_e_variancia_preservada():
    pool = _pool_fake()
    rng = np.random.default_rng(0)
    d1, d2, dq = M.sortear_erros(pool, 400_000, rng, "neutro")
    assert abs(d1.mean()) < 0.002 and abs(dq.mean()) < 0.002
    assert d1.std() == pytest.approx(pool.sigma["z1"], rel=0.02)
    assert dq.std() == pytest.approx(pool.sigma["zq"], rel=0.02)
    assert d2.mean() == pytest.approx(pool.mu["z2"], abs=0.003)     # contração preservada
    assert d2.std() == pytest.approx(pool.sigma["z2"], rel=0.03)


def test_bootstrap_historico_desloca_pela_media_com_sinal():
    pool = _pool_fake()
    rng = np.random.default_rng(1)
    d1, _, dq = M.sortear_erros(pool, 200_000, rng, "historico")
    assert d1.mean() == pytest.approx(pool.mu["z1"], abs=0.003)
    assert dq.mean() == pytest.approx(pool.mu["zq"], abs=0.003)
    with pytest.raises(ValueError):
        M.sortear_erros(pool, 10, rng, "outra")


def test_bootstrap_sem_suavizacao_so_valores_observados():
    pool = M.montar_pool(_pool_fake_erros(), suavizar=False)
    rng = np.random.default_rng(2)
    d1, _, _ = M.sortear_erros(pool, 5000, rng, "neutro")
    assert set(np.round(np.abs(d1), 6)) <= {0.3, 0.05, 0.02}


def _pool_fake_erros():
    return [
        {"ano": a, "erro": e, "nucleo12": np.array([[0.1, 0.1], [-0.1, -0.1]]),
         "nucleoq": np.array([0.1, -0.1])}
        for a, e in [(2014, {"z1": -0.3, "z2": -0.2, "zq": None}),
                     (2018, {"z1": 0.05, "z2": -0.4, "zq": -0.1}),
                     (2022, {"z1": -0.02, "z2": -0.5, "zq": -0.2})]
    ]


def test_desvios_estaduais_loo_sem_vazamento():
    V, pares = M.desvios_estaduais(2)
    assert pares == ["2002->2006", "2006->2010", "2010->2014", "2014->2018", "2018->2022"]
    assert V.shape == (5, 27)
    _, p18 = M.desvios_estaduais(2, excluir_anos={2018})
    assert all("2018" not in p for p in p18) and len(p18) == 3
    # desvios ponderados por eleitores somam ~0 (definição relativa ao nacional)
    r = pd.read_csv(os.path.join(M.DIR_DADOS, "resultados_uf_2002_2022.csv"))
    w = r[(r.ano == 2022) & (r.turno == 2)].set_index("uf").loc[M.UFS, "votos_validos"].to_numpy()
    assert abs(np.average(V[-1], weights=w)) < 1.0


def test_desvios_uf_neutro_media_zero():
    V, _ = M.desvios_estaduais(2)
    D = M.sortear_desvios_uf(V, 200_000, np.random.default_rng(0), "neutro")
    assert np.abs(D.mean(axis=0)).max() < 0.1
    # variância preservada (média dos quadrados dos vetores observados)
    assert D.var(axis=0).mean() == pytest.approx((V ** 2).mean(), rel=0.05)


@pytest.fixture(scope="module")
def simulacao_rapida():
    d = M.carregar_2026()
    aj = M.ajustar_eleicao(d, n_iter=300, burn=100)
    pool = _pool_fake()
    V1, _ = M.desvios_estaduais(1)
    V2, _ = M.desvios_estaduais(2)
    r = M.resultados_uf()
    base = {1: r[(2022, 1)], 2: r[(2022, 2)]}
    return M.simular(d, aj, pool, base, V1, V2, n_sims=30_000, variante="neutro", seed=0, lote=10_000)


def test_simulacao_probabilidades_coerentes(simulacao_rapida):
    p = simulacao_rapida["prob"]
    assert p["pt_vence"] + p["opp_vence"] + p["outro_vence"] == pytest.approx(1.0)
    assert p["decide_1t"] == pytest.approx(p["pt_vence_1t"] + p["opp_vence_1t"])
    assert 0 <= p["top2_pt_opp"] <= 1
    q = simulacao_rapida["quantis"]
    assert q["pt_1t"]["p5"] <= q["pt_1t"]["p50"] <= q["pt_1t"]["p95"]
    # fatias de 1º turno somam 100 (média)
    soma = q["pt_1t"]["media"] + q["opp_1t"]["media"] + q["demais_1t"]["media"]
    assert soma == pytest.approx(100, abs=1e-6)
    assert set(simulacao_rapida["ufs"]) == set(M.UFS)
    for u in M.UFS:
        assert 0 <= simulacao_rapida["ufs"][u]["p_pt_vence_2t"] <= 1


def test_swing_uniforme_preserva_ordem_regional(simulacao_rapida):
    u = simulacao_rapida["ufs"]
    # sem pesquisas estaduais, a ordem vem de 2022: PI (Lula 77%) > SP > SC (Lula 31%)
    assert u["PI"]["p_pt_vence_2t"] > u["SP"]["p_pt_vence_2t"] > u["SC"]["p_pt_vence_2t"]


def test_avaliar_e_resumo_backtest():
    d = M.carregar_historico(2022)
    aj = M.ajustar_eleicao(d, n_iter=300, burn=100)
    pool = _pool_fake()
    V1, _ = M.desvios_estaduais(1, excluir_anos={2022})
    V2, _ = M.desvios_estaduais(2, excluir_anos={2022})
    r = M.resultados_uf()
    sim = M.simular(d, aj, pool, {1: r[(2018, 1)], 2: r[(2018, 2)]}, V1, V2,
                    n_sims=20_000, seed=0, lote=10_000)
    av = M.avaliar(sim, 2022, r)
    assert 0 <= av["brier_uf_2t"] <= 1
    assert set(av["cobertura_nacional"]) == {"pt_1t", "opp_1t", "demais_1t", "q_2t"}
    res = M.resumir_backtest({2022: {"neutro": av}})
    assert res["neutro"]["n_uf"] == 27
    assert 0 <= res["neutro"]["cobertura_uf_2t"]["0.8"] <= 1
