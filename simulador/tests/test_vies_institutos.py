"""Correção das pesquisas de 2º turno pelo erro de cada instituto no 1º turno e viés da indústria 1T -> 2T
(vies_institutos.py) e sua integração no 2º turno de resultado_1t.py."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo as M  # noqa: E402
import resultado_1t as R  # noqa: E402
import vies_institutos as VI  # noqa: E402


def _err(e, v):
    return pd.DataFrame({"instituto": [f"I{i}" for i in range(len(e))], "erro_pp": e, "var_pp2": v})


def test_pooling_encolhe_para_a_media():
    p = VI.pooling(_err([0.0, 2.0, 4.0, 6.0, 8.0], [1.0, 1.0, 1.0, 1.0, 4.0]))
    assert p["_k"] == 5 and p["_tau"] > 0
    assert min(0.0, 6.0) < p["_mu"] < 8.0
    for i, e in enumerate([0.0, 2.0, 4.0, 6.0, 8.0]):
        r = p[f"I{i}"]
        assert 0 < r["B"] < 1
        assert r["plena_pp"] == pytest.approx(p["_mu"] + r["rel_pp"])
        assert abs(r["rel_pp"]) <= abs(e - p["_mu"]) + 1e-12          # encolhido, mesmo sinal
        assert r["rel_pp"] * (e - p["_mu"]) >= 0
    assert p["I4"]["B"] < p["I3"]["B"]                                # mais variância -> mais encolhimento
    # institutos homogêneos: tau = 0, sem desvio próprio; todos recebem a média
    h = VI.pooling(_err([1.0, 1.1, 0.9], [1.0, 1.0, 1.0]))
    assert h["_tau"] == 0 and all(h[f"I{i}"]["rel_pp"] == 0 for i in range(3))
    assert VI.correcao(h, "I0", "plena")[0] == pytest.approx(h["_mu"])
    assert VI.correcao(h, "desconhecido", "relativa") == (0.0, 0.0)
    assert VI.correcao(h, "desconhecido", "plena")[0] == pytest.approx(h["_mu"])
    assert VI.correcao(h, "I0", "nenhuma") == (0.0, 0.0)


def test_corrigir_mantem_total_e_desloca_fatia():
    p = VI.pooling(_err([2.0, 2.0], [1.0, 1.0]))
    df = pd.DataFrame({"instituto": ["I0", "I1", "X"], "a": [45.0, 50.0, np.nan], "b": [45.0, 40.0, 50.0]})
    out = VI.corrigir(df, p, "plena", "a", "b")
    assert np.allclose((out.a + out.b)[:2], (df.a + df.b)[:2])
    assert np.allclose(100 * out.a[:2] / (out.a + out.b)[:2], 100 * df.a[:2] / (df.a + df.b)[:2] - 2.0)
    assert np.isnan(out.a[2]) and out.b[2] == 50.0                     # sem 2º turno: intocado
    m = VI.corrigir(df, p, "plena", "a", "b", mascara=pd.Series([False, True, True]))
    assert m.a[0] == 45.0 and m.a[1] != 50.0


def test_erros_1t_usa_ultima_pesquisa_da_janela():
    p1 = pd.DataFrame({"instituto": ["A", "A", "B", "C"],
                       "campo_fim": pd.to_datetime(["2026-09-30", "2026-10-03", "2026-10-02", "2026-09-20"]),
                       "n": [2000, 2000, np.nan, 2000], "a": [40.0, 50.0, 45.0, 60.0], "b": [40.0, 50.0, 45.0, 20.0]})
    e = VI.erros_1t(p1, 49.0, "2026-10-04").set_index("instituto")
    assert set(e.index) == {"A", "B"}                                  # C fora da janela de 7 dias
    assert e.loc["A", "erro_pp"] == pytest.approx(1.0) and e.loc["A", "k"] == 1
    j = VI.erros_1t(p1, 49.0, "2026-10-04", so_ultima=False).set_index("instituto")
    assert j.loc["A", "k"] == 2 and j.loc["A", "var_pp2"] < e.loc["A", "var_pp2"]


def test_pool_2026_erro_da_industria():
    pool, err = VI.pool_2026()
    assert pool["_k"] == len(err) >= 12
    real = VI.real_2026()["s1_pp"]
    assert 48.5 < real < 49.5
    assert 1.0 < pool["_mu"] < 3.0                                     # pesquisas a favor de Lula no 1º turno
    assert (err.erro_pp > 0).sum() >= 10
    assert pool["Palver"]["rel_pp"] < 0 < pool["Datafolha"]["rel_pp"]


def test_backtest_sustenta_a_decisao():
    """Pré-1T corrigidas (plena) melhoram; pós-1T corrigidas pioram -> PARAM_2T reflete isso."""
    bt = VI.backtest_correcao(log=lambda *a: None)
    ag = bt["agregado"]
    assert ag["plena"]["rmse_pre_1t_pp"] < ag["nenhuma"]["rmse_pre_1t_pp"]
    for modo in ("relativa", "industria", "plena"):
        assert ag[modo]["rmse_pos_1t_pp"] > ag["nenhuma"]["rmse_pos_1t_pp"]
        assert ag[modo]["rmse_pesquisas_ult_semana_pp"] > ag["nenhuma"]["rmse_pesquisas_ult_semana_pp"]
    assert R.PARAM_2T["correcao_institutos_pre_1t"]["valor"] == "plena"
    assert R.PARAM_2T["correcao_institutos_pos_1t"]["valor"] == "nenhuma"


def test_vies_industria_regressao_neutra():
    e1 = {2014: 7.6, 2018: 0.5, 2022: 0.6, 2026: 1.8}
    v = VI.vies_industria({2014: 2.7, 2018: -0.6, 2022: 2.1}, 2.6, e1=e1)
    assert v["tau0_ml_com_2026_pp"] > 0 and v["tau0_usado_pp"] >= v["tau0_piso_pp"]
    assert abs(v["kappa_media"]) < 1 and v["kappa_dp"] < 0.5
    x = e1[2026] - v["media_e1_pp"]
    assert v["vies_2026_pp"] == pytest.approx(v["b_media_pp"] + v["kappa_media"] * x, abs=2e-3)
    # sem relação nos dados (erros 2T constantes; e1 de 2026 = média histórica) -> kappa ~ 0
    w = VI.vies_industria({2014: 1.0, 2018: 1.0, 2022: 1.0}, 2.6, e1={**e1, 2026: float(np.mean(list(e1.values())[:3]))})
    assert abs(w["kappa_media"]) < 0.05
    # tau0 por máxima verossimilhança marginal
    assert VI.tau0_ml([1.0, -1.0], 1.0) == 0.0
    assert VI.tau0_ml([3.0, 3.0, 3.0, 3.0], 2.0) == pytest.approx(math.sqrt(9 - 1))


def test_pesquisas_2t_2026_corrigidas():
    prem = M.carregar_premissas()
    hoje = pd.Timestamp("2026-10-05")
    q0 = R.pesquisas_2t_2026(("Lula", "Flavio"), prem, hoje, corr_pre="nenhuma")
    qp = R.pesquisas_2t_2026(("Lula", "Flavio"), prem, hoje, corr_pre="plena")
    qr = R.pesquisas_2t_2026(("Lula", "Flavio"), prem, hoje, corr_pre="relativa")
    assert q0["tipo"] == "pre_1t" and q0["q"] == q0["q_sem_correcao"] and q0["dp_correcao_pp"] == 0
    mu = qp["erro_1t_institutos"]["mu_pp"]
    assert 100 * (q0["q"] - qp["q"]) == pytest.approx(mu, abs=0.8)   # nível: ~ média da indústria
    assert abs(100 * (qr["q"] - q0["q"])) < 0.5                       # só desvios: quase neutro (house effects)
    assert qp["dp_correcao_pp"] > 0
    qf = R.pesquisas_2t_2026(("Flavio", "Lula"), prem, hoje, corr_pre="plena")
    assert qf["q"] == pytest.approx(1 - qp["q"])


def test_calibracao_com_correcao_e_vies_condicionado():
    cal0 = R.calibrar_2t_2026(None, corr="nenhuma", vies_cond=False)
    cal1 = R.calibrar_2t_2026(None, corr="plena", vies_cond=True)
    assert cal0["vies_metodo"] == "eb_tau0_fixo" and cal1["vies_metodo"] == "condicionado_1t_2026"
    assert cal1["erros_pp"][0] == pytest.approx(cal0["erros_pp"][0])          # 2014: sem pesquisas pré-1T
    assert cal1["erros_pp"][2] < cal0["erros_pp"][2]                          # 2022 corrigido
    assert cal1["vies_industria"]["erros_1t_pp"][2026] > 0
    assert abs(cal1["vies_pp"]) < max(abs(e) for e in cal1["erros_pp"])


def test_simular_2t_inclui_incerteza_da_correcao():
    U = len(R.UFS)
    rng = np.random.default_rng(3)
    L = rng.uniform(0.3, 0.6, U); F = (1 - L) * 0.9; r = 1 - L - F
    S = np.column_stack([L, F, r * 0.3, r * 0.3, r * 0.1, r * 0.2, r * 0.1])
    el = rng.uniform(5e5, 3e7, U)
    c = {"cands": list(M.CANDS), "S": S, "V1": el * 0.75, "eleitores": el, "abst1": np.full(U, 20.0),
         "bn1": np.full(U, 4.0), "pst": np.full(U, 100.0), "fonte_uf": ["TSE"] * U}
    cal = {"dp_nacional_pp": 2.5, "vies_pp": 0.5, "vies_dp_pp": 1.0, "dp_regional_pp": 1.0, "dp_uf_pp": 1.5}
    dc = pd.DataFrame({"d_abst": np.zeros(U), "d_bn": np.zeros(U)}, index=R.UFS)
    t = R.transf_para_par(("Lula", "Flavio"), 2026)
    a = R.simular_2t(c, ("Lula", "Flavio"), t, {"q": 0.48, "peso": 0.25}, cal, dc, n=20_000)
    b = R.simular_2t(c, ("Lula", "Flavio"), t, {"q": 0.48, "peso": 0.25, "dp_correcao_pp": 2.0}, cal, dc, n=20_000)
    assert b["erros"]["dp_nacional_pp"] == pytest.approx(math.sqrt(a["erros"]["dp_nacional_pp"] ** 2 + 0.25), abs=1e-3)
    assert b["centro"]["centro_a_pct"] == a["centro"]["centro_a_pct"]
