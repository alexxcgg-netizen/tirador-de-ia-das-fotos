"""Testes do pipeline da noite da apuração (resultado_1t.py).

Fixtures em tests/fixtures/tse/:
  * ele-c.json            config pública do TSE (recorte), baixada em 4/10/2026
  * 2026/*.json           JSON de presidente 2026 (formato 'u') antes da apuração (zeros), baixados em 4/10/2026
  * 2024/rr-...-u.json    eleição suplementar de RR 2024 totalizada (formato 'u', com votos anulados sub judice)
  * 2022/*.json           1º turno de 2022 no formato 'dados-simplificados' (r), reconstruído dos dados abertos do TSE
                          (os JSON originais de 2022 não estão mais publicados)
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resultado_1t as R  # noqa: E402

FX = Path(__file__).resolve().parent / "fixtures" / "tse"


def _js(p):
    return json.loads((FX / p).read_text(encoding="utf-8"))


def test_descobre_codigo_2026():
    el = R.descobrir_eleicao(_js("ele-c.json"), 2026, 1)
    assert el["ciclo"] == "ele2026" and el["cd"] == "6257" and el["cdt2"] == "6258"
    assert R.descobrir_eleicao(_js("ele-c.json"), 2030, 1) is None
    u = R.urls_presidente("ele2026", "6257", "SP")
    assert u[0].endswith("/oficial/ele2026/6257/dados/sp/sp-c0001-e006257-u.json")
    assert u[1].endswith("/dados-simplificados/sp/sp-c0001-e006257-r.json")


def test_numero_br():
    assert R._num("48,43") == pytest.approx(48.43)
    assert R._num("57259504") == 57259504
    assert R._num("1.234,5") == pytest.approx(1234.5)
    assert np.isnan(R._num(""))


def test_parse_2026_antes_da_apuracao():
    r = R.parse_tse(_js("2026/br-c0001-e006257-u.json"), R.NUMEROS[2026])
    assert r["formato"] == "u" and r["pst"] == 0 and r["eleitorado"] == 158745502
    nomes = {c["n"] for c in r["candidatos"]}
    assert {"13", "22", "55", "70", "30", "14"} <= nomes            # todos os candidatos do modelo estão na cédula
    assert set(r["votos"]) == set(R.CANDS_ANO[2026])
    assert R.parse_tse(_js("2026/zz-c0001-e006257-u.json"), R.NUMEROS[2026])["abr"] == "ZZ"


def test_parse_u_totalizado_com_anulados():
    r = R.parse_tse(_js("2024/rr-c0003-e006278-u.json"))
    # o JSON é de governador (cargo 3): o leitor de presidente (cargo 1) não deve pegar candidatos
    assert r["candidatos"] == []
    js = _js("2024/rr-c0003-e006278-u.json")
    js["carg"][0]["cd"] = "1"
    r = R.parse_tse(js, {"10": "A", "13": "B"})
    assert r["pst"] == 100 and r["validos"] == 102845 and r["brancos"] == 3414 and r["nulos"] == 4295
    # candidato com votação anulada sub judice não entra nos válidos
    assert sum(r["votos"].values()) == 93897 + 8948


def test_parse_2022_fixture_bate_com_tse():
    r = R.parse_tse(_js("2022/br-c0001-e000544-r.json"), R.NUMEROS[2022])
    assert r["formato"] == "r" and r["pst"] == 100
    assert r["validos"] == 118229719
    assert r["votos"]["Lula"] / r["validos"] == pytest.approx(0.484307, abs=1e-5)
    assert r["votos"]["Bolsonaro"] / r["validos"] == pytest.approx(0.431976, abs=1e-5)
    assert sum(r["votos"].values()) == r["validos"]
    assert r["comparecimento"] + r["abstencao"] == pytest.approx(r["eleitorado"], rel=1e-5)  # agregação TSE difere em ~600


@pytest.fixture(scope="module")
def res2022():
    res = R.buscar_resultados(2022, "diretorio", FX / "2022", log=lambda *a: None)
    res.pop("_meta")
    return res


@pytest.fixture(scope="module")
def ufs_ref_2022():
    h = R._hist()
    r1 = h[(h.ano == 2022) & (h.turno == 1)].set_index("uf")
    return pd.DataFrame({"uf": R.UFS, "eleitores": r1.loc[R.UFS, "eleitorado"].values,
                         "abst1": r1.loc[R.UFS, "abstencao_pct"].values,
                         "bn1": (r1.loc[R.UFS, "branco_pct_comp"] + r1.loc[R.UFS, "nulo_pct_comp"]).values})


def test_consolidar_total(res2022, ufs_ref_2022):
    c = R.consolidar(res2022, 2022, ufs_ref_2022)
    assert R.status_apuracao(c) == "final"
    assert np.allclose(c["S"].sum(1), 1)
    assert c["nacional"][0] == pytest.approx(0.484307, abs=2e-4)       # soma das UFs = total nacional
    assert c["abst1"][R.UFS.index("SP")] == pytest.approx(20.68, abs=1.5)
    par, decidido, previsto = R.definir_par(c)
    assert par == ("Lula", "Bolsonaro") and not decidido and previsto


def test_consolidar_parcial_projeta(res2022, ufs_ref_2022):
    res = copy.deepcopy(res2022)
    for uf in ("SP", "BR"):
        for k in ("validos", "comparecimento", "abstencao", "brancos", "nulos"):
            res[uf][k] *= 0.4
        res[uf]["votos"] = {k: v * 0.4 for k, v in res[uf]["votos"].items()}
        res[uf]["pst"] = 40.0
    del res["AC"]                                                      # UF ainda sem nenhuma seção
    prev = {"AC": {"Lula": 0.3, "Bolsonaro": 0.6, "Ciro": 0.04, "Tebet": 0.04, "Outros": 0.02}}
    c = R.consolidar(res, 2022, ufs_ref_2022, prev)
    assert R.status_apuracao(c) == "parcial"
    i = R.UFS.index("SP")
    assert c["V1"][i] == pytest.approx(res2022["SP"]["validos"], rel=1e-9)   # projeção = apurado / pst
    assert c["fonte_uf"][R.UFS.index("AC")] == "previsão"
    sd = R._sd_proj(c)
    assert sd[i] > 0 and sd[R.UFS.index("RJ")] == 0 and sd[R.UFS.index("AC")] > sd[i]
    with pytest.raises(ValueError):
        R.consolidar(res, 2022, ufs_ref_2022, None)


def test_simular_2t_basico(res2022, ufs_ref_2022):
    c = R.consolidar(res2022, 2022, ufs_ref_2022)
    cal = {"dp_nacional_pp": 2.5, "dp_regional_pp": 1.0, "dp_uf_pp": 1.5, "vies_pp": 0.0, "vies_dp_pp": 0.0}
    d = R.delta_comparecimento((2014, 2018))
    linha = [0.32, 0.22, 0.46]
    s = R.simular_2t(c, ("Lula", "Bolsonaro"), R.transf_para_par(("Lula", "Bolsonaro"), 2022, linha), None, cal, d,
                     n=20000, seed=1)
    assert 0 < s["p_a_vence"] < 1 and s["p_a_vence"] + s["p_b_vence"] == pytest.approx(1)
    assert s["a_quantis"] == sorted(s["a_quantis"])
    assert len(s["ufs"]) == 28 and all(0 <= u["p_a"] <= 1 for u in s["ufs"])
    # centro = via de transferência (sem pesquisas, sem viés)
    assert s["a_media"] == pytest.approx(s["centro"]["via_transferencia_a_pct"], abs=0.5)
    # mais votos para A na matriz -> A sobe
    s2 = R.simular_2t(c, ("Lula", "Bolsonaro"), R.transf_para_par(("Lula", "Bolsonaro"), 2022, [0.6, 0.1, 0.3]), None,
                      cal, d, n=20000, seed=1)
    assert s2["a_media"] > s["a_media"]
    # pesquisas puxam o centro na direção delas
    s3 = R.simular_2t(c, ("Lula", "Bolsonaro"), R.transf_para_par(("Lula", "Bolsonaro"), 2022, linha),
                      {"q": 0.40, "peso": 0.5}, cal, d, n=20000, seed=1)
    assert s3["a_media"] < s["a_media"] - 2
    # determinístico com a mesma semente
    s4 = R.simular_2t(c, ("Lula", "Bolsonaro"), R.transf_para_par(("Lula", "Bolsonaro"), 2022, linha), None, cal, d,
                      n=20000, seed=1)
    assert s4["a_media"] == s["a_media"]


def test_par_imprevisto_e_decisao():
    cands = R.CANDS_ANO[2026]
    U = len(R.UFS)
    S = np.tile([0.30, 0.31, 0.32, 0.02, 0.02, 0.02, 0.01], (U, 1))   # Caiado em 1º, Flávio em 2º
    c = {"cands": cands, "S": S, "V1": np.ones(U), "nacional": S[0]}
    par, decidido, previsto = R.definir_par(c)
    assert par == ("Caiado", "Flavio") and not previsto and not decidido
    t = R.transf_para_par(par, 2026)
    assert set(t) == set(cands) - set(par) and t["Lula"] == R.LINHA_GENERICA
    S2 = np.tile([0.52, 0.40, 0.03, 0.02, 0.01, 0.01, 0.01], (U, 1))
    _, decidido, _ = R.definir_par({"cands": cands, "S": S2, "V1": np.ones(U), "nacional": S2[0]})
    assert decidido
    # par Lula x Flávio: matriz Quaest; com Flávio na frente, A continua sendo Lula (PT)
    S3 = np.tile([0.44, 0.46, 0.03, 0.03, 0.01, 0.02, 0.01], (U, 1))
    par, _, previsto = R.definir_par({"cands": cands, "S": S3, "V1": np.ones(U), "nacional": S3[0]})
    assert par == ("Lula", "Flavio") and previsto
    assert R.transf_para_par(par, 2026)["Zema"] == [0.10, 0.80, 0.10]


def test_calibracao_historica_sem_o_ano():
    cal = R.calibrar_2t((2014, 2018), 0.25)
    assert cal["anos"] == [2014, 2018] and len(cal["erros_pp"]) == 2
    assert cal["dp_nacional_pp"] >= R.PARAM_2T["dp_nacional_piso_pp"]["valor"]
    assert 0 < cal["dp_uf_pp"] < 6 and 0 <= cal["dp_regional_pp"] < 6
    assert abs(cal["vies_pp"]) < max(abs(e) for e in cal["erros_pp"])        # encolhido
    eco = R.ecologico(2022)
    assert 0 < eco["fracao_pt_dos_ganhos"] < 1


def test_avaliacao(res2022, ufs_ref_2022):
    c = R.consolidar(res2022, 2022, ufs_ref_2022)
    prev = [{"fonte": "teste", "tipo": "modelo", "nacional": {
        "Lula": {"media": 50.0, "quantis": {0.025: 45, 0.1: 47, 0.25: 48.5, 0.5: 50, 0.75: 51.5, 0.9: 53, 0.975: 55}},
        "Bolsonaro": {"media": 40.0, "quantis": {0.025: 35, 0.1: 37, 0.25: 38.5, 0.5: 40, 0.75: 41.5, 0.9: 43, 0.975: 45}}},
        "eventos": {"primeiro_lugar": {"Lula": 0.8, "Bolsonaro": 0.2}, "decidida_1t": 0.4,
                    "vai_ao_2t": {"Lula": 0.6, "Bolsonaro": 0.6}}, "ufs": {}},
        {"fonte": "Instituto X", "tipo": "pesquisa", "nacional": {"Lula": {"media": 51.0}, "Bolsonaro": {"media": 37.0}},
         "eventos": {}, "ufs": {}}]
    av = R.avaliar(c, prev)
    m = av["previsoes"][0]
    assert m["nacional"]["Lula"]["erro"] == pytest.approx(50 - 48.4307, abs=1e-2)
    assert m["nacional"]["Lula"]["em_80"] and not m["nacional"]["Bolsonaro"]["em_80"]
    assert m["eventos"]["Lula em 1º"]["ocorreu"] == 1 and m["eventos"]["Decidida no 1º turno"]["ocorreu"] == 0
    assert m["eventos"]["Decidida no 1º turno"]["brier"] == pytest.approx(0.16)
    assert av["ranking_pesquisas_margem"][0]["fonte"] == "Instituto X"
    md = R.escrever_avaliacao_md(av, "Teste")
    assert "| teste |" in md and "Brier" in md


def test_pesquisas_2026_finais_em_validos():
    ps = R.previsoes_pesquisas_2026()
    insts = {p["instituto"] for p in ps}
    assert {"Datafolha", "Quaest", "AtlasIntel"} <= insts
    for p in ps:
        tot = sum(v["media"] for v in p["nacional"].values())
        assert 60 < tot <= 100.5
    atlas = [p for p in ps if p["instituto"] == "AtlasIntel"][0]
    assert atlas["nacional"]["Lula"]["media"] == pytest.approx(47.0, abs=0.1)     # já publicada em válidos


def test_rodar_2026_aguardando(monkeypatch, tmp_path):
    """Antes da apuração (pst = 0) o pipeline grava status 'aguardando' sem simular."""
    def falso(ano, fonte="auto", diretorio=None, log=print):
        res = {"BR": R.parse_tse(_js("2026/br-c0001-e006257-u.json"), R.NUMEROS[2026]), "_meta": {"fonte": "teste"}}
        return res
    monkeypatch.setattr(R, "buscar_resultados", falso)
    monkeypatch.setattr(R, "WEB", tmp_path)
    (tmp_path / "resultados.json").write_text((Path(R.__file__).parent / "web" / "resultados.json").read_text(encoding="utf-8"),
                                              encoding="utf-8")
    out = R.rodar_2026(1000, 1, log=lambda *a: None)
    assert out["meta"]["status"] == "aguardando"
    assert json.loads((tmp_path / "resultados_2t.json").read_text())["meta"]["status"] == "aguardando"


def test_simular_2t_votos_faixas_virada(res2022, ufs_ref_2022):
    """Campos do painel '2º turno': votos absolutos, faixas de margem, UF de virada, fluxo dos eliminados."""
    c = R.consolidar(res2022, 2022, ufs_ref_2022)
    cal = {"dp_nacional_pp": 2.5, "dp_regional_pp": 1.0, "dp_uf_pp": 1.5, "vies_pp": 0.0, "vies_dp_pp": 0.0}
    d = R.delta_comparecimento((2014, 2018))
    s = R.simular_2t(c, ("Lula", "Bolsonaro"), R.transf_para_par(("Lula", "Bolsonaro"), 2022, [0.32, 0.22, 0.46]),
                     None, cal, d, n=20000, seed=1)
    v = s["votos"]
    assert sum(f["p"] for f in s["faixas_margem"]) == pytest.approx(1, abs=1e-4)
    assert sum(f["p"] for f in s["faixas_margem"] if f["de"] >= 0) == pytest.approx(s["p_a_vence"], abs=1e-4)
    assert v["a_quantis"] == sorted(v["a_quantis"]) and v["validos_quantis"] == sorted(v["validos_quantis"])
    assert v["a_media"] + v["b_media"] == pytest.approx(v["validos_media"], rel=1e-6)
    assert 100 * v["a_media"] / v["validos_media"] == pytest.approx(s["a_media"], abs=0.05)
    assert v["comparecimento_media"] < v["eleitores"] and v["validos_media"] < v["comparecimento_media"]
    assert v["primeiro_turno"]["por_candidato"]["Lula"] == pytest.approx(57_259_504, rel=1e-4)   # TSE 2022, 1º turno
    assert sum(v["primeiro_turno"]["por_candidato"].values()) == pytest.approx(v["primeiro_turno"]["validos"], rel=1e-6)
    elim = sum(v["primeiro_turno"]["por_candidato"][k] for k in ("Ciro", "Tebet", "Outros"))
    assert sum(sum(x) for x in v["fluxo_eliminados"].values()) == pytest.approx(elim, rel=1e-3)
    assert sum(s["uf_virada"]["freq"].values()) == pytest.approx(1, abs=1e-3)
    assert sum(u["validos_2t_media"] for u in s["ufs"]) == pytest.approx(v["validos_media"], rel=1e-4)


def test_historico_turnos():
    h = R.historico_turnos()
    assert [x["ano"] for x in h] == [2014, 2018, 2022]
    h22 = h[-1]
    assert h22["pt_2t_pct"] == pytest.approx(50.9, abs=0.1) and h22["pt_1t_pct"] == pytest.approx(48.4, abs=0.1)
    assert h22["abst_2t_pct"] > h22["abst_1t_pct"] - 1
