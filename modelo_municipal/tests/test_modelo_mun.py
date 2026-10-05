"""Testes do modelo municipal do 2º turno (dados sintéticos + checagens dos arquivos gerados)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))

from modelo_mun import CATS, CATS6, ModeloEI, ModeloLogit, _completar, agregar, avaliar, simular  # noqa: E402


def _sintetico(n=600, semente=0, beta_pt=(1, 0, .8, .2, .3, 0), beta_op=(0, 1, .15, .7, .1, .03), ruido=0.0):
    rng = np.random.default_rng(semente)
    ufs = np.array(["BA", "SP", "RS", "PE", "MG", "PA"])
    x = rng.dirichlet([6, 6, 1, 2, 1, 4], n)
    aptos = rng.integers(2_000, 300_000, n).astype(float)
    d = pd.DataFrame({"cd_municipio_tse": np.arange(n), "uf": ufs[np.arange(n) % len(ufs)], "aptos": aptos})
    d["pt1"], d["opp1"] = x[:, 0] * aptos, x[:, 1] * aptos
    d["terc_esq"], d["terc1"] = x[:, 2] * aptos, (x[:, 2] + x[:, 3]) * aptos
    d["brancos"], d["nulos"] = x[:, 4] * aptos / 2, x[:, 4] * aptos / 2
    d["comparecimento"] = (1 - x[:, 5]) * aptos
    ypt = x @ np.array(beta_pt) + ruido * rng.normal(size=n)
    yop = x @ np.array(beta_op) + ruido * rng.normal(size=n)
    d["pt2"], d["opp2"] = ypt * aptos, yop * aptos
    return _completar(d)


def test_fracoes_somam_um():
    d = _sintetico()
    assert np.allclose(d[CATS].sum(axis=1), 1)
    assert np.allclose(d[CATS6].sum(axis=1), 1)


def test_ei_recupera_coeficientes():
    d = _sintetico()
    m = ModeloEI(niveis=[], lam=0, cats=CATS6).ajustar(d)
    assert np.allclose(m.coefs[("nac", "nac")]["pt"], [1, 0, .8, .2, .3, 0], atol=1e-3)
    assert np.allclose(m.coefs[("nac", "nac")]["opp"], [0, 1, .15, .7, .1, .03], atol=1e-3)


def test_ei_respeita_limites_e_hierarquia():
    d = _sintetico(ruido=0.02)
    m = ModeloEI(niveis=["uf"], lam=10, cats=CATS6).ajustar(d)
    for b in m.coefs.values():
        for k in ("pt", "opp"):
            assert (b[k] >= -1e-9).all() and (b[k] <= 1 + 1e-9).all()
    p = m.prever(d)
    assert (p.fatia_pt_prev.between(0, 1)).all()
    # grupo desconhecido cai no nível nacional
    d2 = d.head(3).copy()
    d2["uf"] = "XX"
    assert np.allclose(m.prever(d2).pt2_prev, ModeloEI(niveis=[], lam=0, cats=CATS6).ajustar(d).prever(d2).pt2_prev)


def test_avaliacao_zero_quando_previsao_perfeita():
    d = _sintetico()
    r = avaliar(ModeloEI(niveis=["uf"], lam=10, cats=CATS6).ajustar(d).prever(d), d)
    assert abs(r["erro_nacional_pp"]) < 1e-3 and r["rmse_mun_pp"] < 1e-2


def test_logit_roda_e_preve_fatias_validas():
    d = _sintetico(ruido=0.01)
    p = ModeloLogit(efeito="uf").ajustar(d).prever(d)
    assert p.fatia_pt_prev.between(0, 1).all()
    assert abs(agregar(p).iloc[0].fatia_pt_prev - (d.pt2.sum() / (d.pt2 + d.opp2).sum())) < 0.02


def test_simulacao_agregada_coerente():
    d = _sintetico()
    p = ModeloEI(niveis=[], lam=0, cats=CATS6).ajustar(d).prever(d)
    s = simular(p, 2.0, 1.0, 0.5, 1.0, n=200_000, semente=1)
    assert abs(s["media_pct"] - s["base_pct"]) < 0.05
    esperado = np.sqrt(2.0 ** 2 + 0.6 ** 2)  # nacional domina; regional/UF diluídos entre grupos
    assert 2.0 <= s["dp_pct"] <= esperado + 0.3
    z = (50 - s["base_pct"]) / s["dp_pct"]
    from scipy.stats import norm
    assert abs(s["p_lula"] - (1 - norm.cdf(z))) < 0.02


ARQ = AQUI / "resultados_municipal_2t.json"


@pytest.mark.skipif(not ARQ.exists(), reason="rode rodar_mun.py antes")
def test_saidas_publicadas():
    r = json.loads(ARQ.read_text(encoding="utf-8"))
    n = r["nacional"]
    assert 0 <= n["p_lula"] <= 1 and n["n_sim"] == 500_000
    q = n["lula_pct_quantis"]
    assert q["2.5"] < q["50"] < q["97.5"]
    assert 100 < n["validos_mi"] < n["comparecimento_mi"] < r["primeiro_turno_2026"]["aptos_mi"]
    assert len(r["uf"]) >= 27
    csv = pd.read_csv(AQUI / "projecao_municipios_2t.csv")
    assert len(csv) > 5500
    assert abs(100 * csv.lula_2t_votos.sum() / csv.validos_2t.sum() - n["lula_pct_projetado"]) < 0.05
    # validação: o modelo principal erra o país em menos de 5 p.p. nos dois sentidos
    for v in r["validacao"][r["meta"]["modelo_principal"]].values():
        assert abs(v["erro_nacional_pp"]) < 5
