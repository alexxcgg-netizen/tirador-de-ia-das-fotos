"""Testes da fonte alternativa (g1) da apuração: fonte_alternativa.py.

Fixtures em tests/fixtures/g1/ (baixadas em 4/10/2026):
  * 2022/br-executivo.json         presidente Brasil 1º turno 2022 (s.glbimg.com/jo/el), fotos removidas
  * 2022/PRESIDENTE_{UF}.JSON      infográfico do g1 2022 por UF e ZZ, só 'atualizacao' e 'total'
  * 2026/br-executivo.json         presidente Brasil 2026 antes da apuração (zeros)
  * 2026/PRESIDENTE_CONSOLIDADO.JSON  presidente por UF 2026 antes da apuração (zeros)
  * 2026/sp-executivo.json         governador SP 2026 (só o eleitorado é usado)
"""
import copy
import csv
import json
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fonte_alternativa as A  # noqa: E402

FX = Path(__file__).resolve().parent / "fixtures"
G1 = FX / "g1"


def _js(p):
    return json.loads((G1 / p).read_text(encoding="utf-8"))


def _404(url):
    raise urllib.error.HTTPError(url, 404, "Not Found", None, None)


def baixar_2022(url):
    if url.endswith("/2022/apuracao/1-turno/br/executivo.json"):
        return _js("2022/br-executivo.json")
    if "/infografico-g1/2022/1-turno/PRESIDENTE_" in url:
        return _js("2022/" + url.rsplit("/", 1)[-1])
    _404(url)


def fake_2026(br, cons, ele_uf=None):
    ele_uf = ele_uf or {}
    sp = _js("2026/sp-executivo.json")

    def baixar(url):
        if url.endswith("/2026/apuracao/1-turno/br/executivo.json"):
            return br
        if url.endswith("/br/PRESIDENTE_CONSOLIDADO.JSON"):
            return cons
        if url.endswith("/executivo.json"):              # governador da UF: só eleitorado
            uf = url.rsplit("/", 2)[-2].upper()
            g = copy.deepcopy(sp)
            g["abrangencia"]["uf"] = uf
            g["abrangencia"]["eleitores"] = ele_uf.get(uf, 1_000_000)
            g["candidatos"] = [{"numero": "13", "votos": {"quantidade": 999999}, "destinacaoDosVotos": "Válido"}]
            return g
        _404(url)
    return baixar


def test_num():
    assert A.num("1.234.567") == 1234567
    assert A.num("390.750") == 390750
    assert A.num("48,43%") == 48.43
    assert A.num("100,00") == 100
    assert A.num("0.00") == 0
    assert A.num("45.67") == 45.67
    assert A.num("57259504") == 57259504
    assert A.num("") != A.num("")      # nan


def test_2022_g1_igual_ao_tse():
    """1º turno de 2022 pelo g1 = TSE (fixtures reconstruídas dos dados abertos) em todas as UFs, BR e ZZ."""
    alt = A.buscar_g1(2022, log=lambda *_: None, baixar=baixar_2022)
    assert alt["_meta"]["faltando"] == []
    br = alt["BR"]
    assert br["pst"] == 100 and br["votos"]["lula"] == 57259504 and br["votos"]["bolsonaro"] == 51072345
    assert br["validos"] == 118229719 and br["abstencao"] == 32770982
    assert alt["ZZ"]["votos"]["lula"] == 138933 and alt["ZZ"]["eleitorado"] == 304032 + 390750
    tse = A.buscar_tse(2022, FX / "tse" / "2022", log=lambda *_: None)
    assert len(tse) == 29
    rows = A.comparar(tse, alt, 2022, tol_pp=0.01)
    assert all(r["status"] == "ok" for r in rows), [r for r in rows if r["status"] != "ok"]
    assert max(r["d_max_pp"] for r in rows) < 0.001


def test_csv_formato(tmp_path):
    alt = A.buscar_g1(2022, log=lambda *_: None, baixar=baixar_2022)
    p = A.gravar_csv(alt, 2022, tmp_path / "m.csv")
    with open(p, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert list(linhas[0].keys()) == ["uf", "pst", "eleitorado", "comparecimento", "abstencao", "validos", "brancos",
                                      "nulos", "lula", "bolsonaro", "ciro", "tebet", "outros"]
    assert [r["uf"] for r in linhas] == ["BR"] + A.UFS
    sp = next(r for r in linhas if r["uf"] == "SP")
    assert sp["bolsonaro"] == "12239989" and sp["pst"] == "100.00" and sp["validos"] == "25656334"


def test_csv_lido_pelo_resultado_1t(tmp_path):
    R = pytest.importorskip("resultado_1t")
    alt = A.buscar_g1(2022, log=lambda *_: None, baixar=baixar_2022)
    res = R.ler_manual(A.gravar_csv(alt, 2022, tmp_path / "m.csv"), R.CANDS_ANO[2022])
    assert set(res) == {"BR", *R.UFS}
    assert res["SP"]["votos"]["Lula"] == 10490032 and res["ZZ"]["pst"] == 100


def test_2026_zeros_antes_da_apuracao(tmp_path):
    br, cons = _js("2026/br-executivo.json"), _js("2026/PRESIDENTE_CONSOLIDADO.JSON")
    ufs = A.parse_g1_consolidado(cons, 2026)
    assert sorted(ufs) == sorted(A.UFS27)
    assert set(ufs["SP"]["votos"]) == {"lula", "flavio", "caiado", "cury", "zema", "renan", "outros"}
    alt = A.buscar_g1(2026, log=lambda *_: None, baixar=fake_2026(br, cons))
    assert alt["_meta"]["faltando"] == [] and alt["_meta"]["exterior"].startswith("derivado")
    assert alt["BR"]["eleitorado"] == 158745463
    assert alt["ZZ"]["pst"] == 0 and alt["ZZ"]["eleitorado"] == 158745463 - 27 * 1_000_000
    # votos do governador (executivo.json da UF) não entram
    assert alt["SP"]["votos"]["lula"] == 0
    p = A.gravar_csv(alt, 2026, tmp_path / "m.csv")
    txt = p.read_text().splitlines()
    assert txt[0] == "uf,pst,eleitorado,comparecimento,abstencao,validos,brancos,nulos,lula,flavio,caiado,cury,zema,renan,outros"
    assert len(txt) == 30


def _parcial_2026(exterior_ok=True):
    """Consolidado e Brasil com apuração parcial sintética: cada UF com 1000 votos (600 Lula, 400 Flávio)."""
    br, cons = copy.deepcopy(_js("2026/br-executivo.json")), copy.deepcopy(_js("2026/PRESIDENTE_CONSOLIDADO.JSON"))
    for reg in cons["presidente_consolidado"]["regiao"]:
        for e in reg["estado"]:
            e.update(qtd_urnas="50.00", comp_abs="1100", abst_abs="400", votos_validos_abs="1000",
                     votos_brancos_abs="40", votos_nulos_abs="60")
            for c in e["candidato"]:
                c["votos_cand_abs"] = {"13": "600", "22": "400"}.get(c["numero"], "0")
    ext = 50 if exterior_ok else -50                        # exterior: 50 votos de Lula
    a = br["abrangencia"]
    a.update(andamento="50,00", eleitoradoApurado=27 * 1500 + 100)
    a["eleitores"] = 27 * 3000 + 200
    a["votos"]["comparecimento"] = 27 * 1100 + 60
    a["votos"]["abstencao"]["quantidade"] = 27 * 400 + 40
    a["votos"]["validos"]["quantidade"] = 27 * 1000 + ext
    a["votos"]["brancos"]["quantidade"] = 27 * 40 + 5
    a["votos"]["nulos"]["quantidade"] = 27 * 60 + 5
    for c in br["candidatos"]:
        c["votos"]["quantidade"] = {"13": 27 * 600 + ext, "22": 27 * 400}.get(c["numero"], 0)
    return br, cons


def test_2026_parcial_e_exterior_derivado():
    br, cons = _parcial_2026()
    alt = A.buscar_g1(2026, log=lambda *_: None, baixar=fake_2026(br, cons, {u: 3000 for u in A.UFS27}))
    sp = alt["SP"]
    assert sp["pst"] == 50 and sp["votos"]["lula"] == 600 and sp["votos"]["flavio"] == 400 and sp["eleitorado"] == 3000
    zz = alt["ZZ"]
    assert zz["votos"]["lula"] == 50 and zz["votos"]["flavio"] == 0 and zz["validos"] == 50
    assert zz["comparecimento"] == 60 and zz["abstencao"] == 40 and zz["eleitorado"] == 200
    assert zz["pst"] == pytest.approx(50.0)          # (60 + 40) / 200


def test_exterior_inconsistente_vira_zero():
    br, cons = _parcial_2026(exterior_ok=False)
    alt = A.buscar_g1(2026, log=lambda *_: None, baixar=fake_2026(br, cons, {u: 3000 for u in A.UFS27}))
    assert alt["ZZ"]["pst"] == 0 and alt["ZZ"]["validos"] == 0


def test_comparar_aponta_divergencia():
    tse = A.buscar_tse(2022, FX / "tse" / "2022", log=lambda *_: None)
    alt = copy.deepcopy(tse)
    alt["SP"]["votos"]["lula"] += 300_000                  # +1,1 p.p. em SP
    alt["MG"]["pst"] = 80.0                                # momento diferente: não alerta
    alt["MG"]["votos"]["lula"] += 300_000
    rows = {r["uf"]: r for r in A.comparar(tse, alt, 2022)}
    assert rows["SP"]["status"].startswith("DIVERGENTE") and rows["SP"]["d_lula"] > 0.5
    assert rows["MG"]["status"] == "momentos diferentes"
    assert rows["RJ"]["status"] == "ok"
    assert "1 UF(s) divergente(s)" in A.imprimir_comparacao(list(rows.values()), 2022)


def test_tse_formato_u_2026():
    tse = A.buscar_tse(2026, FX / "tse" / "2026", log=lambda *_: None)
    assert {"BR", "SP", "ZZ"} <= set(tse)
    assert tse["ZZ"]["eleitorado"] == 916534 and tse["BR"]["pst"] == 0
