"""Termo sistemático da projeção 1º turno -> 2º turno (especificacao_vies_2t.py), sinal do viés, pesquisas pós-1T
e matriz de transferência de 2026 (resultado_1t.py)."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import especificacao_vies_2t as EV  # noqa: E402
import modelo as M  # noqa: E402
import resultado_1t as R  # noqa: E402
import vies_institutos as VI  # noqa: E402


def _c_fake(lula_frente: bool = False):
    rng = np.random.default_rng(3)
    U = len(R.UFS)
    L = rng.uniform(0.3, 0.6, U)
    F = (1 - L) * 0.9
    if not lula_frente:
        L, F = L * 0.85, F * 1.0
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


# ------------------------------------------------------------ sinal do termo de viés
def test_sinal_do_vies_pt_e_lider():
    assert R.vies_aplicado({"vies_pp": 1.0, "vies_sinal": "pt"}, 0.45, 0.47) == 1.0       # PT superestimado: tira de A
    assert R.vies_aplicado({"vies_pp": 1.0}, 0.45, 0.47) == 1.0                          # padrão = sinal do PT
    assert R.vies_aplicado({"vies_pp": 1.0, "vies_sinal": "lider"}, 0.45, 0.47) == -1.0  # A em 2º: soma a A
    assert R.vies_aplicado({"vies_pp": 1.0, "vies_sinal": "lider"}, 0.49, 0.43) == 1.0   # A líder: tira de A


def test_sinal_do_vies_na_simulacao():
    c = _c_fake(lula_frente=False)
    nat = (c["V1"][:, None] * c["S"]).sum(0)
    assert nat[0] < nat[1]                                       # Lula (A) atrás no 1º turno, como em 2026
    t = R.transf_para_par(("Lula", "Flavio"), 2026)
    s0 = R.simular_2t(c, ("Lula", "Flavio"), t, None, CAL0, _dc(), n=20_000)
    sp = R.simular_2t(c, ("Lula", "Flavio"), t, None, {**CAL0, "vies_pp": 1.0, "vies_sinal": "pt"}, _dc(), n=20_000)
    sl = R.simular_2t(c, ("Lula", "Flavio"), t, None, {**CAL0, "vies_pp": 1.0, "vies_sinal": "lider"}, _dc(), n=20_000)
    assert sp["centro"]["centro_a_pct"] == pytest.approx(s0["centro"]["centro_a_pct"] - 1.0, abs=0.02)
    assert sl["centro"]["centro_a_pct"] == pytest.approx(s0["centro"]["centro_a_pct"] + 1.0, abs=0.02)
    assert sl["centro"]["vies_historico_pp"] == -1.0 and sp["centro"]["vies_historico_pp"] == 1.0
    # par imprevisto: sem termo de viés
    sn = R.simular_2t(c, ("Lula", "Flavio"), t, None, {**CAL0, "vies_pp": 1.0}, _dc(), n=20_000, par_previsto=False)
    assert sn["centro"]["vies_historico_pp"] == 0.0


# ------------------------------------------------------------ pesquisas feitas depois do 1º turno
def test_pesquisas_pos_1t_combinadas_por_precisao_e_sem_vies():
    c = _c_fake()
    t = R.transf_para_par(("Lula", "Flavio"), 2026)
    pre = {"q": 0.48, "peso": 0.25, "dp_correcao_pp": 1.0}
    pos = {"q": 0.53, "dp_pp": 2.0, "dp_correcao_pp": 0.0}
    cal = {**CAL0, "vies_pp": 1.5, "vies_dp_pp": 0.8}
    a = R.simular_2t(c, ("Lula", "Flavio"), t, pre, cal, _dc(), n=20_000)
    b = R.simular_2t(c, ("Lula", "Flavio"), t, {**pre, "pos": pos}, cal, _dc(), n=20_000)
    sd_proj = math.sqrt(2.5 ** 2 + 0.8 ** 2 + (0.25 * 1.0) ** 2)
    assert a["erros"]["dp_nacional_pp"] == pytest.approx(sd_proj, abs=2e-3)
    assert b["erros"]["dp_projecao_pp"] == pytest.approx(sd_proj, abs=2e-3)
    w = (1 / 4) / (1 / 4 + 1 / sd_proj ** 2)
    assert b["centro"]["peso_pesquisas_pos_1t"] == pytest.approx(w, abs=1e-3)
    assert b["erros"]["dp_nacional_pp"] == pytest.approx(1 / math.sqrt(1 / sd_proj ** 2 + 1 / 4), abs=2e-3)
    # o viés só sai da projeção: centro = combinação da projeção já sem viés com as pesquisas pós-1T intactas
    proj = a["centro"]["projecao_a_pct"] / 100
    esperado = 100 * float(M.expit(w * M.logit(0.53) + (1 - w) * M.logit(proj)))
    assert b["centro"]["centro_a_pct"] == pytest.approx(esperado, abs=2e-3)
    assert b["centro"]["projecao_a_pct"] == a["centro"]["projecao_a_pct"]
    # com viés zero, o centro com pesquisas pós-1T sobe exatamente (1 − w) x viés (aprox. linear no logito)
    b0 = R.simular_2t(c, ("Lula", "Flavio"), t, {**pre, "pos": pos}, {**cal, "vies_pp": 0.0}, _dc(), n=20_000)
    assert b0["centro"]["centro_a_pct"] - b["centro"]["centro_a_pct"] == pytest.approx((1 - w) * 1.5, abs=0.03)
    # pesquisas pós-1T mais precisas pesam mais
    c2 = R.simular_2t(c, ("Lula", "Flavio"), t, {**pre, "pos": {**pos, "dp_pp": 1.0}}, cal, _dc(), n=20_000)
    assert c2["centro"]["peso_pesquisas_pos_1t"] > b["centro"]["peso_pesquisas_pos_1t"]


def test_pesquisas_2t_2026_com_pos_1t(monkeypatch):
    prem = M.carregar_premissas()
    base = M.carregar_pesquisas_nacionais_2026

    def fake():
        df, *resto = base()
        extra = pd.DataFrame([{"instituto": "Quaest", "campo_inicio": pd.Timestamp("2026-10-06"),
                               "campo_fim": pd.Timestamp("2026-10-08"), "n": 2000, "t2_lula": 46.0, "t2_flavio": 48.0}])
        return (pd.concat([df, extra], ignore_index=True), *resto)
    monkeypatch.setattr(M, "carregar_pesquisas_nacionais_2026", fake)
    hoje = pd.Timestamp("2026-10-10")
    q = R.pesquisas_2t_2026(("Lula", "Flavio"), prem, hoje)
    assert q["tipo"] == "pos_1t" and q["pos"]["n_pesquisas"] == 1
    assert q["pos"]["q"] == pytest.approx(46 / 94, abs=1e-6)                 # sem correção (PARAM_2T)
    assert q["peso"] == R.PARAM_2T["peso_pesquisas_pre_1t"]["valor"]         # a projeção mantém as pré-1T
    sp = math.sqrt(1.5 ** 2 + (3.0 * 15 / 21) ** 2)
    assert q["pos"]["dp_pp"] == pytest.approx(sp)
    qf = R.pesquisas_2t_2026(("Flavio", "Lula"), prem, hoje)
    assert qf["pos"]["q"] == pytest.approx(1 - q["pos"]["q"])


# ------------------------------------------------------------ especificações (backtest LOEO 2002-2022)
def test_terceiros_por_bloco_somam_os_menores():
    for a in EV.ANOS:
        b = EV.base_ano(a)
        assert np.allclose(b["TE"] + b["TN"], b["d"]["T"], atol=1e-9)
        assert (b["TE"] >= 0).all() and (b["TN"] >= 0).all()
    t = EV.tabela_terceiros()
    assert set(t.bloco) == {"esquerda", "nao_esquerda"} and t.fonte.str.contains("TSE").all()
    assert EV.base_ano(2002)["t_nesq_pp"] == pytest.approx(0, abs=1e-9)          # 2002: todos de esquerda
    assert EV.base_ano(2018)["t_esq_pp"] == pytest.approx(14.12, abs=0.1)        # = modelo_municipal (Ciro, Marina...)
    assert EV.base_ano(2022)["t_nesq_pp"] == pytest.approx(5.22, abs=0.1)
    assert not EV.base_ano(2018)["lider_pt"] and EV.base_ano(2022)["lider_pt"]
    assert set(EV.BLOCO_2026.values()) == {"nao_esquerda"}


def test_backtest_escolhe_pelo_rmse_loeo():
    bt = R.backtest_vies()
    assert bt["anos"] == [2002, 2006, 2010, 2014, 2018, 2022]
    rs = bt["resumo"]
    assert set(rs) == set(EV.ESPECIFICACOES)
    melhor = min(rs, key=lambda k: rs[k]["rmse_pp"])
    assert bt["escolha"]["espec"] == ("zero" if rs["zero"]["rmse_pp"] - rs[melhor]["rmse_pp"] < EV.EMPATE_PP else melhor)
    assert bt["escolha"]["espec"] == "zero"                    # com 2006 (5/10/2026)
    assert R.especificacao_escolhida() == "zero"
    # robustez: sem 2006 o líder vence (sensibilidade publicada)
    assert R.backtest_vies(tuple(a for a in EV.ANOS if a != 2006))["escolha"]["espec"] == "lider"
    # LOEO de verdade: o parâmetro de cada ano não usa o próprio ano
    t = bt["tabela"]
    v = t[(t.espec == "pt") & (t.ano == 2006)].vies_treino_pp.iloc[0]
    par = EV.ajustar("pt", [EV.base_ano(a) for a in EV.ANOS if a != 2006])
    assert v == pytest.approx(par["vies_pp"], abs=1e-3)


def test_escolha_empate_vai_para_zero():
    r = {"zero": {"rmse_pp": 2.0}, "pt": {"rmse_pp": 1.9}, "lider": {"rmse_pp": 2.5}, "ideologia": {"rmse_pp": 3.0}}
    assert EV.escolher(r)["espec"] == "zero" and EV.escolher(r)["empate"]
    r["lider"]["rmse_pp"] = 1.0
    assert EV.escolher(r)["espec"] == "lider"


def test_calibracao_2026_sem_dupla_contagem():
    cal = R.calibrar_2t_2026(None)
    assert cal["anos"] == [2002, 2006, 2010, 2014, 2018, 2022] and cal["vies_especificacao"] == "zero"
    assert cal["vies_pp"] == 0 and cal["vies_dp_pp"] == 0
    e = np.array(cal["erros_especificacao_pp"])
    assert cal["dp_nacional_pp"] == pytest.approx(math.sqrt((2 * 9 + np.sum(e ** 2)) / (2 + len(e))))
    # 'pt': dp nacional = resíduo em torno do viés (o viés e sua incerteza não entram duas vezes)
    cp = R.calibrar_2t_2026(None, espec="pt", vies_cond=False)
    r = np.array(cp["erros_especificacao_pp"]) - cp["vies_pp"]
    assert cp["dp_nacional_pp"] == pytest.approx(max(math.sqrt((18 + np.sum(r ** 2)) / 8), 2.0))
    cl = R.calibrar_2t_2026(None, espec="lider", vies_cond=False)
    assert cl["vies_sinal"] == "lider" and cp["vies_sinal"] == "pt"
    ci = R.calibrar_2t_2026(None, espec="ideologia")
    assert len(ci["p_blocos"]) == 2 and ci["vies_pp"] == 0


def test_transf_ideologia_mantem_participacao():
    t = R.transf_para_par(("Lula", "Flavio"), 2026)
    ti = R.transf_ideologia(t, (0.8, 0.4))
    for k, r in t.items():
        assert sum(ti[k]) == pytest.approx(sum(r)) and ti[k][2] == r[2]
    assert ti["Caiado"][0] / (ti["Caiado"][0] + ti["Caiado"][1]) == pytest.approx(0.4)
    assert ti["Outros"][0] / (ti["Outros"][0] + ti["Outros"][1]) > 0.7      # 'Outros' de 2026 quase todo de esquerda


# ------------------------------------------------------------ matriz de 2026 (uma onda; indecisos repartidos)
def test_matriz_2026_onda_unica_e_indecisos():
    m = R.matriz_2026("ultima")
    for k, r in m.items():
        assert sum(r) == pytest.approx(1, abs=1e-3)
    assert m["Caiado"] == R._linha_quaest(R.QUAEST_2T_2026["2026-10-03"]["Caiado"])
    assert m["Cury"] == R._linha_quaest(R.QUAEST_2T_2026["2026-10-03"]["Cury"])        # não mais a onda de 27/09
    assert m["Zema"] == R._linha_quaest(R.QUAEST_2T_2026["2026-09-27"]["Zema"])        # só existe na onda anterior
    assert R.onda_de("Zema") == "2026-09-27" and R.onda_de("Renan") == "2026-10-03"
    # indecisos repartidos na proporção: a razão Lula/Flávio não muda
    a, b, _, _ = R.QUAEST_2T_2026["2026-10-03"]["Renan"]
    assert m["Renan"][0] / m["Renan"][1] == pytest.approx(a / b, rel=1e-3)
    assert R.ALFA_TRANSF_2026["Zema"] < R.PARAM_2T["alfa_dirichlet"]["valor"]
    s = R.matriz_2026("2026-09-27")
    assert s["Caiado"] == R._linha_quaest(R.QUAEST_2T_2026["2026-09-27"]["Caiado"])


def test_alfa_por_linha_alarga_a_incerteza():
    c = _c_fake()
    t = R.transf_para_par(("Lula", "Flavio"), 2026)
    a = R.simular_2t(c, ("Lula", "Flavio"), t, None, CAL0, _dc(), n=20_000)
    b = R.simular_2t(c, ("Lula", "Flavio"), t, None, CAL0, _dc(), n=20_000,
                     alfa_linhas={k: 5.0 for k in t})
    assert b["erros"]["dp_nacional_da_matriz_pp"] > a["erros"]["dp_nacional_da_matriz_pp"]
    assert b["transferencia_alfa"]["Caiado"] == 5.0 and a["transferencia_alfa"]["Caiado"] == 30.0


# ------------------------------------------------------------ escala do viés e κ fora da amostra
def test_tau0_robusto_e_kappa_fora_da_amostra():
    e1 = {2014: 7.6, 2018: 0.5, 2022: 0.6, 2026: 1.8}
    assert VI.tau0_robusto(list(e1.values())) < VI.tau0_ml(list(e1.values()), float(np.std(list(e1.values()), ddof=1)))
    v = VI.vies_industria({2014: 2.7, 2018: -0.6, 2022: 2.1}, 2.6, e1=e1)
    assert v["tau0_estimador"] == "robusto" and set(v["tau0_sensibilidade_pp"]) >= {"ml_com_2026", "ml_sem_2014"}
    assert v["tau0_sensibilidade_pp"]["ml_sem_2014"] < v["tau0_sensibilidade_pp"]["ml_com_2026"]
    k = EV.backtest_kappa({2014: 2.7, 2018: -0.6, 2022: 2.1}, e1, 2.6)
    assert len(k["tabela"]) == 3 and k["rmse_com_kappa_pp"] > 0 and k["rmse_zero_pp"] > 0
