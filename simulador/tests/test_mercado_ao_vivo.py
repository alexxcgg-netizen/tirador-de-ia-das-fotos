"""Testes do rastreador de mercados ao vivo, com respostas reais gravadas em 4/out/2026 17:37 UTC."""
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mercado_ao_vivo as MV  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "mercado" / "respostas_2026-10-04T1737Z.json"
AGORA = datetime(2026, 10, 4, 17, 37, 8, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def respostas():
    return json.loads(FIX.read_text(encoding="utf-8"))


@pytest.fixture
def fake_get(respostas):
    chamadas = []

    def get(url, params=None):
        chamadas.append((url, dict(params or {})))
        if url == MV.GAMMA:
            if params["slug"] in respostas["gamma"]:
                return respostas["gamma"][params["slug"]]
            raise RuntimeError("404 (fora do fixture)")
        if url == MV.KALSHI:
            if params["series_ticker"] in respostas["kalshi"]:
                return respostas["kalshi"][params["series_ticker"]]
            raise RuntimeError("429")
        if url == MV.CLOB_HIST:
            return respostas["clob"].get(params["market"], {"history": []})
        raise AssertionError(url)

    get.chamadas = chamadas
    return get


def rodar(tmp_path, get, agora=AGORA, **kw):
    return MV.coletar_uma_vez(get=get, csv_path=tmp_path / "m.csv", json_path=tmp_path / "m.json",
                              cache_path=tmp_path / "cache.json", agora=agora, **kw)


def test_preco_justo():
    assert MV.preco_justo(0.37, 0.38, 0.38) == 0.375
    assert MV.preco_justo(0.0, 1.0, 0.0, 0.5) == 0.5  # spread largo, sem negócio -> fallback
    assert MV.preco_justo(0.10, 0.40, 0.31) == 0.31  # spread largo -> último negócio
    assert MV.preco_justo(0.0, 1.0, 0.0) is None


def test_coleta_e_normalizacao(tmp_path, fake_get):
    doc = rodar(tmp_path, fake_get)
    grupos = {(g["plataforma"], g["evento"]): g for g in doc["ultimo"]}
    venc = grupos[("Polymarket", "vencedor")]
    nomes = [r["resultado"] for r in venc["resultados"]]
    assert not any(n.startswith("Person") for n in nomes)  # placeholders descartados
    nomes1t = [r["resultado"] for r in grupos[("Polymarket", "vencedor_1t")]["resultados"]]
    assert not any(n.startswith(("Candidate", "Other")) for n in nomes1t)
    assert nomes[0] == "Flávio Bolsonaro"
    assert abs(sum(r["normalizado"] for r in venc["resultados"]) - 1) < 1e-3
    assert 0.55 < venc["resultados"][0]["normalizado"] < 0.70
    # binário: normalizado == preço
    dec = grupos[("Polymarket", "decide_1t")]["resultados"]
    assert len(dec) == 1 and dec[0]["resultado"] == "Sim" and dec[0]["normalizado"] == dec[0]["preco"]
    # Kalshi
    kv = grupos[("Kalshi", "vencedor")]["resultados"]
    assert abs(sum(r["normalizado"] for r in kv) - 1) < 1e-3
    assert doc["destaques"]["Kalshi"]["vencedor_flavio"] > doc["destaques"]["Kalshi"]["vencedor_lula"]
    assert doc["destaques"]["Polymarket"]["1t_lula_primeiro"] > 0.5
    # UF presente
    assert ("Polymarket", "uf_SP") in grupos
    # séries: backfill do CLOB, todas a partir de 12:00 UTC
    sid = "Polymarket|vencedor|Flávio Bolsonaro"
    assert sid in doc["series"] and len(doc["series"][sid]) > 10
    t0 = datetime(2026, 10, 4, 12, tzinfo=timezone.utc).timestamp()
    assert all(p[0] >= t0 for s in doc["series"].values() for p in s)
    assert doc["series_meta"][sid]["rotulo"] == "Vencedor da eleição"
    # fidelidade 1 min nos mercados-chave
    fids = {p.get("fidelity") for u, p in fake_get.chamadas if u == MV.CLOB_HIST}
    assert fids <= {1, 5} and 1 in fids


def test_csv_acumula_e_json_valido(tmp_path, fake_get):
    rodar(tmp_path, fake_get)
    doc = rodar(tmp_path, fake_get, agora=AGORA + timedelta(minutes=2))
    rows = list(csv.DictReader((tmp_path / "m.csv").open(encoding="utf-8")))
    assert set(rows[0]) == set(MV.CAMPOS)
    ts = {r["ts_utc"] for r in rows}
    assert ts == {"2026-10-04T17:37:08Z", "2026-10-04T17:39:08Z"}
    # cache do CLOB reaproveitado na 2ª coleta (idade < 240 s)
    n_clob = sum(1 for u, _ in fake_get.chamadas if u == MV.CLOB_HIST)
    assert n_clob == len(json.loads((tmp_path / "cache.json").read_text())) - 2
    # série da Kalshi vem do CSV (2 pontos)
    k = [s for sid, s in doc["series"].items() if sid.startswith("Kalshi|vencedor|")]
    assert k and max(len(s) for s in k) == 2
    json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))


def test_falhas_parciais_nao_derrubam(tmp_path, respostas):
    def get(url, params=None):
        if url == MV.GAMMA and params["slug"] == "brazil-presidential-election":
            return respostas["gamma"][params["slug"]]
        raise RuntimeError("fora do ar")

    doc = rodar(tmp_path, get)
    assert [g["evento"] for g in doc["ultimo"]] == ["vencedor"]
    assert doc["series"]  # cai para os pontos do CSV


def test_sem_historico(tmp_path, fake_get):
    doc = rodar(tmp_path, fake_get, historico=False)
    assert not any(u == MV.CLOB_HIST for u, _ in fake_get.chamadas)
    assert all(len(s) == 1 for s in doc["series"].values())
