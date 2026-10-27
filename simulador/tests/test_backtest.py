"""Testes do backtest: roda, mede cobertura, sem informação futura."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backtest as BT  # noqa: E402
import modelo as M  # noqa: E402


@pytest.fixture(scope="module")
def prem():
    return M.carregar_premissas()


@pytest.fixture(scope="module")
def err(prem):
    return BT.erros_brutos(prem)


def test_crps_normal():
    rng = np.random.default_rng(0)
    s = rng.standard_normal(200000)
    # CRPS de N(0,1) em y=0: 2*phi(0) - 1/sqrt(pi) ~ 0.2337
    assert abs(BT.crps(s[:20000], 0.0) - (2 / math.sqrt(2 * math.pi) - 1 / math.sqrt(math.pi))) < 0.01
    assert BT.pit(s, 0.0) == pytest.approx(0.5, abs=0.01)


def test_sem_pesquisas_do_futuro(prem):
    for ano in BT.ANOS:
        for h in ("v1", "v2"):
            e = BT.eleicao_hist(ano, h, prem)
            assert (e.nac.campo_fim <= e.ref).all()
            if len(e.puf):
                assert (e.puf.campo_fim <= e.ref).all()
            t1 = pd.Timestamp(BT.DATAS[ano][0])
            assert e.ref < (t1 if h == "v1" else pd.Timestamp(BT.DATAS[ano][1]))
            if h == "v2":
                assert (e.nac.campo_fim >= t1).all()


def test_adversario_e_o_segundo_na_media_de_vespera(prem, err):
    """O 'adversário' de cada ano é o 2º colocado nas pesquisas da véspera, não escolhido pelo resultado."""
    for ano in BT.ANOS:
        b = err[ano]["base_v1"]
        d = b.pesquisas
        # mesma regra do agregador: última pesquisa de cada instituto na janela, peso sqrt(n) x recência
        rec = M._selecionar_recentes(d[d.c1.notna()], "c1", b.e.ref, prem)
        media = lambda c: float(np.sum(rec.peso * rec[c]) / np.sum(rec.peso))
        for k in range(2, b.e.K - 1):          # candidatos nomeados (fora "Outros")
            assert media("c1") > media(f"c{k}")


def test_prior_loeo_exclui_o_proprio_ano(prem, err):
    _, _, usados = BT.rodar(prem, "calibrado", horizontes=("v1",), n=500, err=err)
    for ano, pri in usados.items():
        assert ano not in pri["residuos"]["p2_pp"]
        assert ano not in pri["residuos"]["q_v1_pp"]
    _, _, temp = BT.rodar(prem, "calibrado", horizontes=("v1",), n=500, err=err, modo_prior="temporal")
    assert temp[2014]["b1"] == (0.0, 0.0) or "residuos" not in temp[2014] or not temp[2014]["residuos"]["p2_pp"]
    assert set(temp[2022]["residuos"]["p2_pp"]) == {2014, 2018}


def test_prior_nao_depende_do_resultado_do_ano_avaliado(prem, err):
    import copy
    e2 = {a: dict(d) for a, d in err.items()}
    e2[2022]["p2_real"] = 0.2           # resultado de 2022 adulterado
    e2[2022]["res_T_log"] = -5.0
    a = BT.priors_vies(err, [2014, 2018], prem, "calibrado")
    b = BT.priors_vies(e2, [2014, 2018], prem, "calibrado")
    assert a["b1"] == b["b1"] and a["muT"] == b["muT"]


def test_v2_usa_primeiro_turno_real(prem):
    b = BT.construir_base_hist(2022, "v2", prem)
    rr = BT.resultados(2022)
    i = list(b.ufs.uf).index("SP")
    assert b.e.primeiro_turno_fixo[i, 0] == pytest.approx(rr["pt1"]["SP"])


def test_backtest_roda_e_mede_cobertura(prem, err):
    cont, prob, _ = BT.rodar(prem, "calibrado", n=3000, err=err)
    assert len(cont) > 100 and len(prob) > 50
    assert cont.pit.between(0, 1).all()
    s = BT.score(cont, prob)
    for k in ("cob50_nacional", "cob80_nacional", "cob95_nacional", "cob80_uf", "cob95_uf", "brier_uf", "crps_uf"):
        assert k in s and np.isfinite(s[k])
    assert 0 <= s["cob50_uf"] <= s["cob80_uf"] <= s["cob95_uf"] <= 1
    # alvos esperados: 1T dos 3 anos, 2T na véspera do 1T em 2018 e 2022, 2T na véspera do 2T nos 3
    alvos = set(map(tuple, cont[cont.nivel == "nacional"][["ano", "alvo"]].drop_duplicates().values))
    assert (2014, "1T") in alvos and (2018, "2T (véspera do 1T)") in alvos and (2022, "2T (véspera do 2T)") in alvos
    assert (2014, "2T (véspera do 1T)") not in alvos


def test_backtest_reprodutivel(prem, err):
    a, _, _ = BT.rodar(prem, "neutro", anos=(2018,), n=2000, err=err, seed=3)
    b, _, _ = BT.rodar(prem, "neutro", anos=(2018,), n=2000, err=err, seed=3)
    pd.testing.assert_frame_equal(a, b)


def test_cobertura_razoavel_saida_gravada():
    p = M.DADOS / "backtest_saida.json"
    if not p.exists():
        pytest.skip("backtest.py ainda não rodou")
    js = json.loads(p.read_text(encoding="utf-8"))
    s = js["scores"]["calibrado"]
    assert s["cob95_uf"] >= 0.8 and s["cob95_nacional"] >= 0.8
    assert len(js["pit_hist"]) == 10
