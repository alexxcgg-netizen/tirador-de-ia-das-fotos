"""Pesquisas de 2º turno feitas depois do 1º turno (fração pós-1T, razão dos válidos, house effects), visões de viés,
efeito de apoio declarado e saída antecipada do mandato (resultado_1t.py)."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo as M  # noqa: E402
import resultado_1t as R  # noqa: E402

T1, T2 = pd.Timestamp("2026-10-04"), pd.Timestamp("2026-10-25")


def _p2(linhas):
    d = pd.DataFrame(linhas, columns=["instituto", "campo_inicio", "campo_fim", "n", "a", "b"])
    d["campo_inicio"] = pd.to_datetime(d.campo_inicio)
    d["campo_fim"] = pd.to_datetime(d.campo_fim)
    return d


def _c_fake():
    rng = np.random.default_rng(3)
    U = len(R.UFS)
    L = rng.uniform(0.3, 0.6, U) * 0.85
    F = (1 - L) * 0.9
    r = 1 - L - F
    S = np.column_stack([L, F, r * 0.3, r * 0.3, r * 0.1, r * 0.2, r * 0.1])
    S = S / S.sum(1, keepdims=True)
    el = rng.uniform(5e5, 3e7, U)
    return {"cands": list(M.CANDS), "S": S, "V1": el * 0.75, "eleitores": el, "abst1": np.full(U, 20.0),
            "bn1": np.full(U, 4.0), "pst": np.full(U, 100.0), "fonte_uf": ["TSE"] * U}


def _dc():
    U = len(R.UFS)
    return pd.DataFrame({"d_abst": np.zeros(U), "d_bn": np.zeros(U)}, index=R.UFS)


CAL0 = {"dp_nacional_pp": 2.5, "vies_pp": 0.0, "vies_dp_pp": 0.0, "dp_regional_pp": 1.0, "dp_uf_pp": 1.5}


# ------------------------------------------------------------ 1) pesquisas que atravessam o 1º turno
def test_fracao_pos_1t():
    f = R.fracao_pos_1t(["2026-10-03", "2026-10-05", "2026-10-01", None, "2026-10-04"],
                        ["2026-10-08", "2026-10-07", "2026-10-04", "2026-10-06", "2026-10-05"], T1)
    assert f[0] == pytest.approx(4 / 6)          # AtlasIntel 3-8/10: 5, 6, 7 e 8/10 depois do dia da eleição
    assert f[1] == 1.0                            # campo todo depois
    assert f[2] == 0.0                            # termina no dia da eleição
    assert f[3] == 1.0                            # sem início: um dia só
    assert f[4] == pytest.approx(0.5)             # 4-5/10: o dia da eleição conta como antes


def test_media_pos_1t_peso_pela_fracao_e_excluir():
    p2 = _p2([["A", "2026-10-03", "2026-10-08", 3000, 45.0, 51.0],
              ["B", "2026-10-06", "2026-10-08", 3000, 47.0, 47.0]])
    hoje = pd.Timestamp("2026-10-08")
    fr = R.media_pos_1t(p2, T1, hoje, T2, atravessa="fracao", house="nenhum")
    ex = R.media_pos_1t(p2, T1, hoje, T2, atravessa="excluir", house="nenhum")
    assert fr["n_pesquisas"] == 2 and ex["n_pesquisas"] == 1 and ex["institutos"] == ["B"]
    pesos = {r["instituto"]: r["peso_rel"] for r in fr["tabela"]}
    assert pesos["A"] / pesos["B"] == pytest.approx(4 / 6, abs=1e-3)
    qa, qb = 45 / 96, 0.5
    esperado = float(M.expit((4 / 6 * M.logit(qa) + M.logit(qb)) / (1 + 4 / 6)))
    assert fr["q"] == pytest.approx(esperado, abs=1e-6)
    assert ex["q"] == pytest.approx(0.5)
    # deriva: 17 dias até o 2º turno
    assert fr["dp_pp"] == pytest.approx(math.sqrt(1.5 ** 2 + (3.0 * 17 / 21) ** 2))


def test_media_pos_1t_indecisos_pela_razao_dos_validos():
    # mesma razão a/(a+b) com 9,7% de indecisos (como a Vox de 2026) ou sem indecisos: mesma fatia
    p_alto = _p2([["Vox", "2026-10-05", "2026-10-07", 2100, 44.2, 42.7]])
    p_baixo = _p2([["Vox", "2026-10-05", "2026-10-07", 2100, 44.2 / 86.9 * 100, 42.7 / 86.9 * 100]])
    a = R.media_pos_1t(p_alto, T1, pd.Timestamp("2026-10-09"), T2, house="nenhum")
    b = R.media_pos_1t(p_baixo, T1, pd.Timestamp("2026-10-09"), T2, house="nenhum")
    assert a["q"] == pytest.approx(44.2 / 86.9, abs=1e-9) and b["q"] == pytest.approx(a["q"], abs=1e-9)


def test_media_pos_1t_defasagem_de_divulgacao():
    p2 = _p2([["A", "2026-10-05", "2026-10-07", 2000, 45.0, 50.0], ["B", "2026-10-06", "2026-10-08", 2000, 48.0, 48.0]])
    x = R.media_pos_1t(p2, T1, pd.Timestamp("2026-10-08"), T2, house="nenhum", defasagem_dias=1)
    assert x["institutos"] == ["A"]


# ------------------------------------------------------------ 2) house effects nas pesquisas pós-1T
def test_house_pooling_encolhe_para_zero_e_aproxima_do_consenso():
    rng = np.random.default_rng(1)
    linhas = []
    for k, dia in enumerate(range(5, 20, 2)):
        d0 = pd.Timestamp("2026-10-04") + pd.Timedelta(days=dia)
        for ins, off, nn in (("Alto", 3.0, 3000), ("M1", 0.0, 400), ("M2", 0.0, 400), ("M3", 0.0, 400)):
            q = 47.0 + off + rng.normal(0, 0.5)
            linhas.append([ins, d0 - pd.Timedelta(days=1), d0, nn, q, 100 - q])
    p2 = _p2(linhas)
    hoje = pd.Timestamp("2026-10-20")
    sem = R.media_pos_1t(p2, T1, hoje, T2, house="nenhum")
    com = R.media_pos_1t(p2, T1, hoje, T2, house="pooling")
    h = com["house_effects"]["institutos"]
    assert 0 < h["Alto"]["house_pp"] < 3.0 + 0.5            # positivo e encolhido
    assert all(abs(h[i]["house_pp"]) < h["Alto"]["house_pp"] for i in ("M1", "M2", "M3"))
    # com pesos iguais o desvio relativo à média não move a média; aqui o instituto "Alto" pesa mais (n maior),
    # então tirar o seu efeito aproxima a média do consenso dos outros
    assert abs(100 * com["q"] - 47.0) < abs(100 * sem["q"] - 47.0) - 0.2
    assert com["dp_house_pp"] > 0 and com["dp_correcao_pp"] >= com["dp_house_pp"]


def test_house_prior_1t_centra_no_desvio_do_1t():
    p2 = _p2([["A", "2026-10-05", "2026-10-07", 2000, 47.0, 53.0], ["B", "2026-10-05", "2026-10-07", 2000, 47.0, 53.0],
              ["C", "2026-10-05", "2026-10-07", 2000, 47.0, 53.0]])
    pool = {"_k": 3, "_mu": 1.0, "_se_mu": 0.3, "_tau": 1.0,
            "A": {"rel_pp": 2.0, "B": 0.5}, "B": {"rel_pp": 0.0, "B": 0.5}, "C": {"rel_pp": 0.0, "B": 0.5}}
    x = R.media_pos_1t(p2, T1, pd.Timestamp("2026-10-09"), T2, pool=pool, house="pooling_prior_1t")
    h = x["house_effects"]["institutos"]
    assert h["A"]["prior_1t_pp"] == pytest.approx(2.0, abs=1e-6)
    assert h["A"]["house_pp"] > h["B"]["house_pp"]
    assert x["q"] < 0.47                                    # tira o desvio de A da média
    with pytest.raises(ValueError):
        R.media_pos_1t(p2, T1, pd.Timestamp("2026-10-09"), T2, house="outro")


def test_pesquisas_2t_2026_atlasintel_entra_pela_fracao():
    prem = M.carregar_premissas()
    hoje = pd.Timestamp("2026-10-12")
    fr = R.pesquisas_2t_2026(("Lula", "Flavio"), prem, hoje, atravessa="fracao")["pos"]
    ex = R.pesquisas_2t_2026(("Lula", "Flavio"), prem, hoje, atravessa="excluir")["pos"]
    atlas = [r for r in fr["tabela"] if r["instituto"] == "AtlasIntel"]
    assert atlas and atlas[0]["fracao_pos_1t"] == pytest.approx(4 / 6, abs=1e-4)
    assert atlas[0]["campo_inicio"] == "2026-10-03" and atlas[0]["campo_fim"] == "2026-10-08"
    assert "AtlasIntel" not in ex["institutos"] and fr["n_pesquisas"] == ex["n_pesquisas"] + 1
    assert R.PARAM_2T["pesquisas_atravessando_1t"]["valor"] == "fracao"
    flip = R.pesquisas_2t_2026(("Flavio", "Lula"), prem, hoje)["pos"]
    assert flip["q"] == pytest.approx(1 - fr["q"])
    for k, v in fr["media_sem_cada_instituto"].items():
        assert flip["media_sem_cada_instituto"][k] == pytest.approx(1 - v)


# ------------------------------------------------------------ backtest das pesquisas pós-1T
def test_crps_amostra_bate_com_normal():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(200_000)
    y = 0.7
    z = y
    pdf = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    exato = z * (2 * cdf - 1) + 2 * pdf - 1 / math.sqrt(math.pi)
    assert R._crps_amostra(x, y) == pytest.approx(exato, abs=0.01)


def test_backtest_pos_1t_estrutura():
    v = {k: R.VARIANTES_POS_1T[k] for k in ("so_projecao", "padrao_sem_house", "house_pooling")}
    r = R.backtest_pos_1t(anos=(2018, 2022), horizontes=(8,), n=5000, variantes=v, log=lambda *a: None)
    t = pd.DataFrame(r["tabela"])
    assert set(t.variante) == set(v) and set(t.ano) == {2018, 2022}
    assert r["pesquisas_atravessando_1t"] == {"2018": 0, "2022": 0}
    t = t[t.ano == 2022]
    sp = t[t.variante == "so_projecao"].iloc[0]
    pd_ = t[t.variante == "padrao_sem_house"].iloc[0]
    assert sp.n_pesquisas_pos == 0 and pd_.n_pesquisas_pos > 0 and pd_.peso_pos > 0
    # sem informação futura: só pesquisas com fim de campo até a data − defasagem
    p2 = R.VI.pesquisas_hist(2022)[1]
    corte = pd.Timestamp("2022-10-10") - pd.Timedelta(days=R.PARAM_2T["defasagem_publicacao_backtest_dias"]["valor"])
    disp = p2[(p2.campo_fim > pd.Timestamp("2022-10-02")) & (p2.campo_fim <= corte)].instituto.nunique()
    assert pd_.n_pesquisas_pos == disp
    assert "house_pooling" in r["decisao"] and "passa_consistencia_2_de_3" in r["decisao"]["house_pooling"]


def test_decisao_do_backtest_gravado_sustenta_o_padrao():
    import json
    p = R.DADOS / "backtest_pos_1t_2t.json"
    if not p.exists():
        pytest.skip("backtest_pos_1t_2t.json ainda não gerado")
    r = json.loads(p.read_text(encoding="utf-8"))
    dec = r["decisao"]
    adotar = [k for k in ("house_pooling", "house_pooling_prior_1t") if dec[k]["passa"]]
    hs = R.PARAM_2T["house_effects_pos_1t"]["valor"]
    assert (hs == "nenhum") == (not adotar)
    assert not dec["vies_pleno"]["passa"]                    # viés pleno nas pós-1T piora o backtest
    assert R.PARAM_2T["correcao_institutos_pos_1t"]["valor"] == "nenhuma"


# ------------------------------------------------------------ 4) efeito de apoio declarado (sensibilidade)
def test_endosso_desligado_nao_muda_nada_e_k_move_so_quem_apoiou():
    c = _c_fake()
    par = ("Lula", "Flavio")
    t = R.transf_para_par(par, 2026)
    a = R.simular_2t(c, par, t, None, CAL0, _dc(), n=20_000)
    b = R.simular_2t(c, par, t, None, CAL0, _dc(), n=20_000, endosso=None)
    assert a["p_a_vence"] == b["p_a_vence"] and a["a_media"] == b["a_media"] and a["endosso"] is None
    z = R.simular_2t(c, par, t, None, CAL0, _dc(), n=20_000,
                     endosso={"cands": ["Caiado"], "para": "Flavio", "k_centro": 0.0, "k_meia": 0.0})
    assert z["centro"]["via_transferencia_a_pct"] == pytest.approx(a["centro"]["via_transferencia_a_pct"], abs=1e-9)
    e = R.simular_2t(c, par, t, None, CAL0, _dc(), n=20_000,
                     endosso={"cands": ["Caiado", "Zema", "Cury"], "para": "Flavio", "k_centro": 0.15, "k_meia": 0.15})
    assert e["centro"]["via_transferencia_a_pct"] < a["centro"]["via_transferencia_a_pct"]
    assert e["a_media"] < a["a_media"]
    lc = e["endosso"]["linhas_centrais"]
    assert lc["Renan"] == pytest.approx(t["Renan"], abs=1e-4)                       # Renan não apoiou
    assert lc["Caiado"][1] == pytest.approx(t["Caiado"][1] + 0.15 * t["Caiado"][2], abs=1e-4)
    assert lc["Caiado"][0] == pytest.approx(t["Caiado"][0], abs=1e-4)
    assert sum(lc["Caiado"]) == pytest.approx(1.0, abs=1e-4)
    assert e["endosso"]["k_faixa"] == [0.0, 0.3]
    assert R.PARAM_2T["efeito_endosso"]["valor"] is False


# ------------------------------------------------------------ 5) saída antecipada do mandato (informativo)
def test_mandato_mesmo_metodo_para_os_dois():
    m = R.mandato_2027_2030(("Lula", "Flavio"), 0.2)
    L, F = m["por_candidato"]["Lula"], m["por_candidato"]["Flavio"]
    assert L["morte_no_mandato_tabua_pct"] == pytest.approx(28.95, abs=0.1)     # taxas anuais arredondadas na nota
    assert F["morte_no_mandato_tabua_pct"] == pytest.approx(1.98, abs=0.01)
    assert 24 < L["p_saida_antecipada_pct"]["central"] < 28                     # nota: ~26%
    assert 19 < L["p_saida_antecipada_pct"]["baixo"] < 22 and 33 < L["p_saida_antecipada_pct"]["alto"] < 38
    assert 1.2 < F["p_saida_antecipada_pct"]["central"] < 2.5                    # nota: ~2%
    for k in ("baixo", "central", "alto"):
        assert L["p_completa_se_eleito_pct"][k] + L["p_saida_antecipada_pct"][k] == pytest.approx(100, abs=0.02)
        tot = 0.2 * L["p_completa_se_eleito_pct"][k] + 0.8 * F["p_completa_se_eleito_pct"][k]
        assert m["p_vencedor_completa_pct"][k] == pytest.approx(tot, abs=0.02)
        assert m["p_vice_assume_pct"][k] == pytest.approx(100 - tot, abs=0.02)
    assert L["vice"].startswith("Geraldo Alckmin") and F["vice"].startswith("Alfredo Gaspar")
    # P(vencer) entra só como peso: com o par invertido o resultado é o mesmo
    m2 = R.mandato_2027_2030(("Flavio", "Lula"), 0.8)
    assert m2["p_vencedor_completa_pct"] == m["p_vencedor_completa_pct"]
    assert R.mandato_2027_2030(("Lula", "Caiado"), 0.5) is None


# ------------------------------------------------------------ 3) três visões de viés do 2º turno
def test_visoes_vies_2t():
    c = _c_fake()
    par = ("Lula", "Flavio")
    prem = M.carregar_premissas()
    hoje = pd.Timestamp("2026-10-12")
    cal = R.calibrar_2t_2026(None)
    qp = R.pesquisas_2t_2026(par, prem, hoje)
    sim = R.simular_2t(c, par, R.transf_2026(par, cal), qp, cal, _dc(), n=10_000, alfa_linhas=R.alfa_2026(par))
    v = R.visoes_vies_2t(c, par, True, None, False, _dc(), prem, hoje, 10_000, 1, sim)["visoes"]
    assert set(v) == {"neutro", "calibrado", "vies_pleno"}
    assert v["calibrado"]["p_a_vence"] == sim["p_a_vence"]
    assert v["calibrado"]["correcao_pos_1t"] == "nenhuma" and v["vies_pleno"]["correcao_pos_1t"] == "plena"
    # a indústria superestimou Lula no 1º turno de 2026: o viés pleno puxa as pesquisas pós-1T para baixo
    assert v["vies_pleno"]["pesquisas_pos_1t_a_pct"] < v["calibrado"]["pesquisas_pos_1t_a_pct"]
    assert v["neutro"]["pesquisas_pos_1t_a_pct"] == v["calibrado"]["pesquisas_pos_1t_a_pct"]
    assert v["neutro"]["pesquisas_pre_1t_a_pct"] > v["calibrado"]["pesquisas_pre_1t_a_pct"]
    for x in v.values():
        assert 0 <= x["p_a_vence"] <= 1 and x["a_p10"] < x["a_media"] < x["a_p90"]
