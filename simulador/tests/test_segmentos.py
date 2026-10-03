"""Testes de sanidade do módulo segmentos.py (prior demográfico, comparecimento, decomposição)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import segmentos as S  # noqa: E402


@pytest.fixture(scope="module")
def cel():
    return S.carregar_abstencao_segmentos()


@pytest.fixture(scope="module")
def leans():
    return S.carregar_leans()


# ------------------------------------------------------------------ (a) prior demográfico
def test_covariaveis_completas():
    X = S.carregar_covariaveis()
    assert list(X.index) == S.UFS
    assert X.notna().all().all()
    assert set(X.columns) == set(S.COVARIAVEIS_PRIOR)


def test_leans_somam_aproximadamente_zero(leans):
    L, nac = leans
    el = pd.read_csv(S.DADOS / "eleitorado_uf_2026.csv").set_index("uf").loc[S.UFS, "eleitores_2026"].values
    for ano in (2018, 2022):
        p = S.expit(S.logit(nac[(ano, 2)]) + L[(ano, 2)].values)
        # média ponderada das UFs ~ nacional (exterior e pesos 2026 dão pequena diferença)
        assert abs(np.average(p, weights=el) - nac[(ano, 2)]) < 0.01
    assert abs(nac[(2022, 2)] - 0.509) < 0.001


def test_ridge_lambda_zero_igual_mqo():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 3))
    y = 1 + X @ np.array([0.5, -1.0, 2.0]) + rng.normal(0, 0.1, 40)
    b = S.ridge_ajustar(X, y, 0.0)
    b_ols, *_ = np.linalg.lstsq(np.c_[np.ones(40), X], y, rcond=None)
    assert np.allclose(b, b_ols)
    # penalização encolhe os coeficientes, não o intercepto
    b10 = S.ridge_ajustar(X, y, 100.0)
    assert np.linalg.norm(b10[1:]) < np.linalg.norm(b[1:])


@pytest.fixture(scope="module")
def validacao2():
    return S.validar_prior_demografico(2)


def test_validacao_prior_numeros_plausiveis(validacao2):
    v = validacao2
    # prior simples reproduz o RMSE documentado (~4 p.p. em 2018->2022)
    assert 3.0 < v["simples_2018->2022"] < 5.0
    # demografia explica boa parte do mapa (R2 LOO > 0,5), mas erra mais que o lean anterior
    assert v["r2_loo_2022"] > 0.5
    assert v["loo_demografico_2022"] > v["simples_2018->2022"]
    assert 0.5 <= v["peso_simples"] <= 1.0
    # o misto nunca é pior que o simples na média das duas transições (w = 1 está na grade)
    assert (v["misto_2014->2018"] + v["misto_2018->2022"]) <= (v["simples_2014->2018"] + v["simples_2018->2022"]) + 1e-9


def test_prior_por_uf(validacao2):
    df = S.prior_demografico_uf(2, validacao2)
    assert len(df) == 27 and df.uf.tolist() == S.UFS
    assert (df.dp_prior_logito > 0).all()
    assert np.allclose(df.prior_simples_logito, 0.85 * df.lean_2022_logito)
    # sinais estruturais: Nordeste acima, Sul/CO abaixo no prior demográfico
    d = df.set_index("uf").prior_demografico_pp
    assert d[["BA", "PI", "CE", "PE"]].min() > 5
    assert d[["SC", "PR", "RO", "MT"]].max() < -5
    # coeficientes com o sinal esperado (evangélicos -, Bolsa Família +)
    c = df.attrs["coeficientes_logito_por_dp"]
    assert c["pct_evangelicos"] < 0 and c["pbf_por_100_eleitores"] > 0


def test_arquivo_prior_coerente():
    df = pd.read_csv(S.DADOS / "prior_demografico_uf.csv")
    assert set(df.turno) == {1, 2}
    assert df.groupby("turno").size().eq(27).all()
    assert df[["prior_misto_logito", "dp_prior_logito"]].notna().all().all()


# ------------------------------------------------------------------ (b) comparecimento
def test_abstencao_bate_com_tse(cel):
    res = pd.read_csv(S.DADOS / "resultados_uf_2002_2022.csv")
    r = res[(res.ano == 2022)].set_index(["turno", "uf"])
    for t in (1, 2):
        g = cel[(cel.turno == t) & cel.uf.isin(S.UFS)].groupby("uf")[["aptos", "abstencao"]].sum()
        assert len(g) == 27  # inclui o DF (só existe no arquivo _BRASIL do zip)
        ab = 100 * g.abstencao / g.aptos
        diff = (ab - r.loc[t].loc[g.index, "abstencao_pct"]).abs()
        assert diff.max() < 0.2, diff.idxmax()
    assert set(cel.faixa_etaria) == set(S.FAIXAS)
    assert set(cel.escolaridade) == set(S.ESCOLARIDADES)


def test_padroes_de_abstencao(cel):
    a = S.abstencao_por_segmento(cel, ["faixa_etaria"]).set_index("faixa_etaria").abstencao_pct
    assert a["80+"] > 60 and a["70-79"] > a["60-69"] > a["45-59"]
    e = S.abstencao_por_segmento(cel, ["escolaridade"]).set_index("escolaridade").abstencao_pct
    assert e["analf_le"] > e["medio_comp"] > e["superior"]


def test_modelo_voto_reproduz_margens(cel, leans):
    c = S.montar_celulas(cel, 2)
    f = S.FONTES_VOTO["datafolha_2022_2t"]
    mv = S.ajustar_modelo_voto(c, f, leans[0][(2022, 2)])
    assert mv["convergiu"]
    # margem regional (alvo de nível) reproduzida exatamente
    for reg, (v, _) in f["margens"]["regiao"].items():
        m = (c.regiao == reg).values
        assert abs(np.average(mv["p"][m], weights=c.aptos[m]) - v / 100) < 1e-3
    # contrastes de gênero preservados (F - M = 5 p.p. +- 1)
    p = mv["p"]
    pf = np.average(p[(c.genero == "F").values], weights=c.aptos[c.genero == "F"])
    pm = np.average(p[(c.genero == "M").values], weights=c.aptos[c.genero == "M"])
    assert 0.04 < pf - pm < 0.06


def test_ajuste_sem_diferencial_de_comparecimento_e_zero(cel):
    c = S.montar_celulas(cel, 1)
    c = c.copy()
    c["comp_taxa"] = 0.8
    c["comparecimento"] = c["aptos"] * 0.8
    aj = S.ajuste_comparecimento(c, [S.FONTES_VOTO["datafolha_2022_2t"]], n_sorteios=5,
                                 kappa_intervalo=(1.0, 1.0), dp_logito_comparecimento=0.0)
    assert np.allclose(aj.ajuste_central_pp, 0, atol=1e-9)
    assert np.allclose(aj.ajuste_pp, 0, atol=1e-9)


def test_projecao_2026_bate_margens(cel):
    c = S.projetar_celulas_2026(S.montar_celulas(cel, 1))
    cov = pd.read_csv(S.DADOS / "covariaveis_uf.csv").set_index("uf")
    tot = c.groupby("uf").aptos.sum()
    assert np.allclose(tot.loc[S.UFS], cov.loc[S.UFS, "eleitores_2026_tse"], rtol=1e-6)
    v60 = c[c.faixa_etaria.isin(["60-69", "70-79", "80+"])].groupby("uf").aptos.sum() / tot * 100
    assert (v60.loc[S.UFS] - cov.loc[S.UFS, "pct_60mais_tse2026"]).abs().max() < 0.05


def test_arquivo_ajuste_plausivel():
    aj = pd.read_csv(S.DADOS / "ajuste_comparecimento_uf.csv")
    assert set(aj.turno) == {1, 2}
    assert aj.groupby("turno").size().eq(28).all()  # 27 UFs + BR
    # efeito pequeno (|ajuste| < 1,5 p.p.) e incerteza positiva
    assert aj.ajuste_pp.abs().max() < 1.5
    assert (aj.dp_ajuste_pp > 0).all()
    assert np.allclose(aj.ajuste_central_pp, (aj.p_votantes_central - aj.p_aptos_central) * 100, atol=1e-3)


def test_validacao_2022_move_para_o_resultado():
    v = S.validar_comparecimento_2022(n_sorteios=20)
    # o ajuste reduz o erro médio dos grandes institutos no 2º turno (que superestimaram Lula)
    t2 = v["turno_2"]
    assert t2["erro_medio_grandes_antes"] > 0
    assert abs(t2["erro_medio_grandes_depois"]) < abs(t2["erro_medio_grandes_antes"])


# ------------------------------------------------------------------ (c) decomposição
def test_decomposicao_json():
    j = json.loads((S.DADOS / "segmentos_voto.json").read_text(encoding="utf-8"))
    dims = {d["dimensao"]: d for d in j["dimensoes"]}
    assert {"genero", "idade", "escolaridade", "renda", "religiao", "regiao", "bolsa_familia"} <= set(dims)
    for chave in ("genero", "idade", "escolaridade"):
        s = sum(c["tamanho_pct"] for c in dims[chave]["categorias"])
        assert 99.0 < s < 100.5, chave
    for d in j["dimensoes"]:
        for c in d["categorias"]:
            if "voto_2022_2t" in c:
                assert c["voto_2022_2t"]["lula"] + c["voto_2022_2t"]["bolsonaro"] == 100
            if "voto_2026_1t" in c:
                assert 0 < c["voto_2026_1t"]["fatia_lula_2p"] < 100
    ev = next(c for c in dims["religiao"]["categorias"] if c["categoria"] == "Evangélicos")
    assert ev["voto_2026_1t"]["margem_lula"] < 0 and ev["voto_2022_2t"]["margem_lula"] < 0


def test_decomposicao_estrutura_em_memoria(cel):
    d = S.decomposicao_segmentos(cel)
    json.dumps(d, ensure_ascii=False)  # serializável
    idade = next(x for x in d["dimensoes"] if x["dimensao"] == "idade")
    sessenta = next(c for c in idade["categorias"] if c["categoria"] == "60+")
    assert sessenta["abstencao_2022_1t_pct"] > 25
