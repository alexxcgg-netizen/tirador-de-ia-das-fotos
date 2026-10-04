"""Transferência regionalizada no 2º turno (transferencia_regional.py) e sua integração em resultado_1t.py."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo as M  # noqa: E402
import resultado_1t as R  # noqa: E402
import transferencia_regional as TR  # noqa: E402


def _c_fake():
    rng = np.random.default_rng(1)
    U = len(R.UFS)
    L = rng.uniform(0.25, 0.70, U)
    F = (1 - L) * rng.uniform(0.80, 0.92, U)
    resto = 1 - L - F
    S = np.column_stack([L, F, resto * 0.3, resto * 0.35, resto * 0.05, resto * 0.25, resto * 0.05])
    el = rng.uniform(5e5, 3e7, U)
    return {"cands": list(M.CANDS), "S": S, "V1": el * 0.75, "eleitores": el, "abst1": np.full(U, 20.0),
            "bn1": np.full(U, 4.0), "pst": np.full(U, 100.0), "fonte_uf": ["TSE"] * U}


def test_lean_z_sinal_e_centro():
    L = np.array([0.6, 0.4, 0.5]); F = np.array([0.3, 0.5, 0.4]); w = np.array([1.0, 1.0, 1.0])
    z = TR.lean_z(L, F, w)
    assert z[0] > 0 > z[1]
    assert abs(np.sum(w * (L + F) * M.expit(M.logit(L / (L + F)))) / np.sum(w * (L + F)) - np.sum(w * L) / np.sum(w * (L + F))) < 1e-12


def test_linhas_uf_preservam_nacional_e_beta_zero():
    c = _c_fake()
    rows = np.array([R.TRANSF_LF_2026[k] for k in ["Caiado", "Cury", "Zema", "Renan", "Outros"]])
    elim = [2, 3, 4, 5, 6]
    r0, _ = TR.linhas_uf(rows, c["S"], 0, 1, elim, c["V1"], 0.0)
    assert np.allclose(r0, rows[None])
    r1, z = TR.linhas_uf(rows, c["S"], 0, 1, elim, c["V1"], 0.6)
    for j, k in enumerate(elim):
        w = c["V1"] * c["S"][:, k]
        p_nac = rows[j, 0] / (rows[j, 0] + rows[j, 1])
        p_uf = r1[:, j, 0] / (r1[:, j, 0] + r1[:, j, 1])
        assert np.sum(w * p_uf) / w.sum() == pytest.approx(p_nac, abs=1e-6)      # nacional da matriz mantido
        assert np.allclose(r1[:, j, 0] + r1[:, j, 1], rows[j, 0] + rows[j, 1])   # participação mantida
        assert np.allclose(r1[:, j, 2], rows[j, 2])
        assert np.corrcoef(p_uf, z)[0, 1] > 0.99                                  # UF mais petista -> mais para o PT


def test_estimar_beta_hierarquico():
    eb = TR.estimar_beta()
    assert set(eb["por_ano"]) == set(TR.ANOS_BETA) and 2006 not in eb["por_ano"]
    assert 0.2 < eb["mu"] < 0.8                     # efeito de contexto positivo nas eleições usadas
    assert eb["dp_preditivo"] >= eb["tau"] >= TR.PARAM_REG["beta_tau_min"]["valor"]
    sem = TR.estimar_beta(tuple(a for a in TR.ANOS_BETA if a != 2018))
    assert 2018 not in sem["por_ano"]


def test_simular_2t_regional_com_beta_zero_igual_ao_nacional():
    c = _c_fake()
    cal = {"dp_nacional_pp": 2.5, "vies_pp": 0.0, "vies_dp_pp": 0.0, "dp_regional_pp": 1.0, "dp_uf_pp": 1.5}
    d_comp = R.delta_comparecimento()
    tr = R.transf_para_par(("Lula", "Flavio"), 2026)
    a = R.simular_2t(c, ("Lula", "Flavio"), tr, None, cal, d_comp, n=20_000, seed=3)
    b = R.simular_2t(c, ("Lula", "Flavio"), tr, None, cal, d_comp, n=20_000, seed=3, regional={"mu": 0.0, "dp": 0.0})
    assert a["centro"]["via_transferencia_a_pct"] == pytest.approx(b["centro"]["via_transferencia_a_pct"], abs=1e-6)
    assert [u["transferencia_central"] for u in a["ufs"]] == [u["transferencia_central"] for u in b["ufs"]]
    g = R.simular_2t(c, ("Lula", "Flavio"), tr, None, cal, d_comp, n=20_000, seed=3, regional={"mu": 0.5, "dp": 0.3})
    assert g["transferencia_regional"]["beta_media"] == 0.5
    # o centro nacional da via de transferência quase não muda (recentragem por candidato)
    assert g["centro"]["via_transferencia_a_pct"] == pytest.approx(a["centro"]["via_transferencia_a_pct"], abs=0.15)
    z = np.array([g["transferencia_regional"]["lean_logito_uf"][u] for u in R.UFS])
    dq = np.array([gu["transferencia_central"] - au["transferencia_central"] for gu, au in zip(g["ufs"], a["ufs"])])
    assert np.corrcoef(z, dq)[0, 1] > 0.9


def test_backtest_regional_2018_2022_melhora():
    t = TR.backtest_regional(anos=(2018, 2022), log=lambda *a: None)
    for ano in (2018, 2022):
        x = t[t.ano == ano].set_index("variante")
        assert x.loc["beta", "uf_mae_pp"] < x.loc["nacional", "uf_mae_pp"]
        # nacional da via de transferência inalterado (a regionalização só redistribui entre UFs)
        assert x.loc["beta", "nacional_transferencia_erro_pp"] == pytest.approx(
            x.loc["nacional", "nacional_transferencia_erro_pp"], abs=0.1)


def test_backtest_comparecimento_formato():
    o = TR.backtest_comparecimento(log=lambda *a: None)
    assert {"media_uf", "encolhida_k1", "so_nacional", "sem_variacao"} <= set(o["resumo"].index)
    assert (o["resumo"]["efeito_pt_nacional_pp"] < 0.5).all()      # reponderação das UFs mexe pouco no PT nacional


def test_cli_ensaio_a_seco_tem_opcoes():
    import inspect
    sig = inspect.signature(R.rodar_2026)
    assert "saida_dir" in sig.parameters and "regional" in sig.parameters
    assert R.PARAM_2T["transferencia_regional"]["valor"] in (True, False)


def test_backtest_2t_pipeline_smoke():
    t = R.backtest_2t(anos=(2018, 2022), n=20_000, log=lambda *a: None)
    assert set(t.variante) == {"nacional", "regionalizada"} and set(t.ano) == {2018, 2022}
    x = t.set_index(["ano", "variante"])
    for ano in (2018, 2022):     # nacional praticamente igual; UF não piora
        assert abs(x.loc[(ano, "regionalizada"), "erro_nacional_pp"] - x.loc[(ano, "nacional"), "erro_nacional_pp"]) < 0.3
        assert x.loc[(ano, "regionalizada"), "uf_mae_pp"] <= x.loc[(ano, "nacional"), "uf_mae_pp"] + 0.05
