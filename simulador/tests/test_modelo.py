import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo as M  # noqa: E402
import rodar as R  # noqa: E402


@pytest.fixture(scope="module")
def prem():
    return M.carregar_premissas()


@pytest.fixture(scope="module")
def base(prem):
    return M.construir_base_2026(prem)


@pytest.fixture(scope="module")
def vieses(base, prem):
    return R.vieses_2026(base, prem)


@pytest.fixture(scope="module")
def lote(base, vieses):
    return {v: M.simular_lote(base, vieses[v], 20000, np.random.default_rng(7)) for v in M.VISOES}


# ------------------------------------------------------------------ somas e consistência
def test_shares_somam_um(lote):
    for r in lote.values():
        assert np.allclose(r["nat1"].sum(1), 1, atol=1e-4)
        assert ((r["uf_L"] > 0) & (r["uf_L"] < 1)).all() and ((r["uf_F"] > 0) & (r["uf_F"] < 1)).all()
        assert np.allclose(r["uf_L"] + r["uf_F"] + r["uf_T"], 1, atol=1e-4)
        assert (r["uf_T"] >= 0).all()
        assert ((r["uf_q"] > 0) & (r["uf_q"] < 1)).all()


def test_media_uf_calibrada_reproduz_nacional(base):
    u = base.ufs
    w = (u.eleitores * (1 - u.abst1 / 100) * (1 - u.bn1 / 100)).values
    T = 1 - base.m_uf.sum(1)
    assert abs(np.sum(w * T * base.p2_uf) / np.sum(w * T) - base.p2_nat) < 1e-6
    w2 = (u.eleitores * (1 - u.abst2 / 100) * (1 - u.bn2 / 100)).values
    assert abs(np.sum(w2 * base.q_uf) / np.sum(w2) - base.q_nat) < 1e-6
    agg_m = (w[:, None] * base.m_uf).sum(0) / w.sum()
    assert np.allclose(agg_m, base.m_nat, atol=1e-4)


def test_probabilidades_em_0_1_e_somam(prem, base, vieses):
    res, _, _ = R.executar(20000, 11, 10000, base=base, vieses=vieses, prem=prem)
    for vis in res.values():
        for k, v in vis["prob"].items():
            assert 0 <= v["p"] <= 1, k
        p = vis["prob"]
        assert abs(p["lula_vence"]["p"] + p["flavio_vence"]["p"] + p["outro_vence"]["p"] - 1) < 1e-9
        assert abs(p["decide_1t"]["p"] + p["segundo_turno_lula_flavio"]["p"] + p["segundo_turno_outro_par"]["p"] - 1) < 1e-9
        for u in vis["ufs"]:
            assert 0 <= u["p_lula_2t"] <= 1 and 0 <= u["p_lula_1o_1t"] + u["p_flavio_1o_1t"] <= 1 + 2e-4


def test_reprodutivel_com_semente(prem, base, vieses):
    a, _, _ = R.executar(5000, 123, 2500, base=base, vieses=vieses, prem=prem)
    b, _, _ = R.executar(5000, 123, 2500, base=base, vieses=vieses, prem=prem)
    c, _, _ = R.executar(5000, 124, 2500, base=base, vieses=vieses, prem=prem)
    assert a["calibrado"]["prob"] == b["calibrado"]["prob"]
    assert a["pleno"]["ufs"] == b["pleno"]["ufs"]
    assert a["calibrado"]["prob"] != c["calibrado"]["prob"]


def test_agregado_das_ufs_segue_sorteio_nacional(lote, base):
    r = lote["neutro"]
    impl = M.expit(M.logit(base.p2_nat) + r["e_p2"])
    agg = r["nat_p2_agregado"]
    assert np.corrcoef(impl, agg)[0, 1] > 0.95


def test_sanidade_geografia(lote, base):
    s = pd.Series(lote["neutro"]["uf_q"].mean(0), index=base.ufs.uf)
    for uf in ("BA", "PE", "CE", "PI", "MA"):
        assert s[uf] > 0.6
    for uf in ("SC", "PR", "MT", "RO", "RR", "AC"):
        assert s[uf] < 0.42


def test_ordem_das_visoes(lote):
    """O viés histórico tem sinal pró-PT; a visão pleno desloca mais que a calibrada, que desloca mais que a neutra."""
    n, c, p = (lote[v]["Q"].mean() for v in ("neutro", "calibrado", "pleno"))
    assert p < c < n
    assert lote["pleno"]["nat1"][:, 1].mean() > lote["neutro"]["nat1"][:, 1].mean()


def test_ufs_disputadas_nao_superconfiantes(prem, base, vieses):
    """SP não pode ficar com P(Lula) ~ 0 quando a disputa nacional é próxima (erro estadual calibrado)."""
    res, _, _ = R.executar(20000, 5, 20000, visoes=("neutro",), base=base, vieses=vieses, prem=prem)
    sp = [u for u in res["neutro"]["ufs"] if u["uf"] == "SP"][0]
    assert sp["p_lula_2t"] > 0.08
    q = sp["lula_2t_q"]
    assert q[2] - q[0] > 6       # intervalo de 80% com mais de 6 p.p.


# ------------------------------------------------------------------ viés e house effects
def test_eb_vies_encolhe():
    x = [6.0, 4.0, 1.0]
    assert M.eb_vies(x, 3.0, 0) == (0.0, 0.0)
    m_inf, s_inf = M.eb_vies(x, 3.0, math.inf)
    assert abs(m_inf - np.mean(x)) < 1e-12 and abs(s_inf - 3 / math.sqrt(3)) < 1e-12
    m2, s2 = M.eb_vies(x, 3.0, 2.0)
    assert 0 < m2 < m_inf and s2 < s_inf
    m_neg, _ = M.eb_vies([-v for v in x], 3.0, 2.0)
    assert abs(m_neg + m2) < 1e-12     # simétrico: sinal oposto -> correção oposta


def test_house_effects_hierarquicos(base):
    h = base.house1
    um = [v for k, v in h.items() if not k.startswith("_") and v["n_pesquisas"] == 1]
    varios = [v for k, v in h.items() if not k.startswith("_") and v["n_pesquisas"] >= 5]
    assert um and varios
    assert np.mean([v["dp_pp"] for v in um]) > np.mean([v["dp_pp"] for v in varios])
    assert all(v["dp_pp"] > 0 for v in um + varios)
    assert h["_tau_pp"] > 0


def test_exposicao_reduz_vies(base):
    assert 0.5 < base.agg1["lambda_medio"] <= 1.0
    tab = {r["instituto"]: r for r in base.agg1["tabela"]}
    if "AtlasIntel" in tab:
        assert tab["AtlasIntel"]["exposicao_vies"] < 1


def test_ajuste_comparecimento_so_no_calibrado(vieses):
    assert vieses["calibrado"]["ajuste_comp"] is True
    assert vieses["neutro"]["ajuste_comp"] is False and vieses["pleno"]["ajuste_comp"] is False
    assert vieses["neutro"]["b1"] == (0.0, 0.0)


def test_vies_calibrado_desconta_comparecimento(prem):
    """Sem dupla contagem: o prior calibrado usa erros históricos descontados do efeito de comparecimento."""
    import backtest as BT
    err = BT.erros_brutos(prem)
    a = BT.priors_vies(err, list(BT.ANOS), prem, "calibrado")
    b = BT.priors_vies(err, list(BT.ANOS), prem, "calibrado", correcao_comp=prem["vies.ajuste_comparecimento_historico_pp"])
    assert b["b1"][0] < a["b1"][0] and b["b2"][0] < a["b2"][0]


def test_teto_rejeicao(base, vieses, prem):
    r = M.simular_lote(base, vieses["neutro"], 20000, np.random.default_rng(3))
    bn2 = prem["rejeicao.bn_2t_pct"] / 100
    capL = (1 - base.e.rejeicao["pt"] / 100) / (1 - bn2) + prem["rejeicao.folga_pp"] / 100
    capF = (1 - base.e.rejeicao["opp"] / 100) / (1 - bn2) + prem["rejeicao.folga_pp"] / 100
    assert r["Q"].max() <= capL + 0.005
    assert (1 - r["Q"]).max() <= capF + 0.005


# ------------------------------------------------------------------ dados
def test_sem_pesquisas_duplicadas():
    df, _ = M.carregar_pesquisas_nacionais_2026()
    reg = df["registro"].dropna().astype(str).str.extract(r"([A-Z]{2}-\d{5}/\d{4})")[0].dropna()
    assert not reg.duplicated().any()
    assert not df.duplicated(["instituto", "campo_fim", "lula", "flavio", "t2_lula", "t2_flavio"]).any()


def test_deduplicar_remove_repetida():
    df, _ = M.carregar_pesquisas_nacionais_2026()
    dup = pd.concat([df, df.iloc[[5]]], ignore_index=True)
    limpo, log = M.deduplicar(dup, ["lula", "flavio", "t2_lula", "t2_flavio"])
    assert len(limpo) == len(df) and len(log) == 1


def test_pesquisa_em_validos_e_sinalizada(base):
    d = base.pesquisas
    # linhas em válidos (ou sem brancos/nulos/indecisos) não recebem alocação de indecisos
    assert (d.loc[d.base_validos, "indecisos_alocados"] == 0).all()
    # Datafolha 3/10 agora em votos totais (bni = 7): não é tratada como válidos
    df3 = d[(d.instituto == "Datafolha") & (d.campo_fim == "2026-10-03")]
    assert len(df3) == 1 and not bool(df3.base_validos.iloc[0])
    tab = {r["instituto"]: r for r in base.agg1["tabela"]}
    if "Gerp" in tab:
        assert tab["Gerp"]["peso_extra"] == 0.5


def test_indecisos_por_rejeicao_muda_pouco(prem):
    a = M.construir_base_2026(prem, "proporcional")
    b = M.construir_base_2026(prem, "rejeicao")
    assert abs(a.p2_nat - b.p2_nat) < 0.01
    assert abs(a.q_nat - b.q_nat) < 0.01
