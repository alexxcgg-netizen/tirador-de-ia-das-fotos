"""Testes dos JSONs de indireto e de trajetoria do Nordeste (esquema, ids, contagens, tags, tamanho)."""
import importlib.util
import json
import os
import re

import pytest

AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.dirname(AQUI)
WEB = os.path.join(SIM, "web")
FIX = os.path.join(AQUI, "fixtures")
RAIZ = os.path.dirname(SIM)
NOTAS_OK = os.path.isdir(os.path.join(RAIZ, "research_notes", "Indireto 2026"))


def _mod(nome):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(SIM, nome + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


gi = _mod("gerar_indireto_json")
gn = _mod("gerar_nordeste_trajetoria_json")
TAG_OK = re.compile(r"^\[(fato|leitura|narrativa de [^\[\]]+)\]( \+ \[(fato|leitura|narrativa de [^\[\]]+)\])*$")


def carrega(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def ind():
    return carrega(os.path.join(WEB, "indireto.json"))


@pytest.fixture(scope="module")
def ne():
    return carrega(os.path.join(WEB, "nordeste_trajetoria.json"))


# ---------- indireto: arquivo real e amostra ----------
@pytest.mark.parametrize("caminho", [os.path.join(WEB, "indireto.json"), os.path.join(FIX, "indireto_sample.json")])
def test_indireto_esquema_ids_contagens(caminho):
    d = carrega(caminho)
    for k in gi.TOPO:
        assert k in d
    for k in ("gerado_em", "escopo", "regra", "avisos"):
        assert k in d["meta"]
    assert set(d["meta"]["escopo"]) == {"lula", "flavio"}
    gi.validar(d)  # ids unicos, top_* existentes, contagens batem com os casos, tags, resumos


def test_indireto_campos_iguais_nos_dois_lados(ind):
    por = {l: {tuple(sorted(c)) for c in ind["casos"] if c["lado"] == l} for l in ("lula", "flavio")}
    assert por["lula"] == por["flavio"] and len(por["lula"]) == 1
    assert set(next(iter(por["lula"]))) == set(gi.CAMPOS_CASO)


def test_indireto_tags_so_vocabulario_comum(ind):
    for c in ind["casos"]:
        assert TAG_OK.match(c["tag"].strip()), (c["id"], c["tag"])


def test_indireto_mantem_retirados_e_valores(ind):
    ret = [c for c in ind["casos"] if c["status"] == "retirado"]
    assert {c["lado"] for c in ret} == {"lula", "flavio"}
    assert {c["status"] for c in ind["casos"]} <= set(gi.STATUS_OK)
    assert {c["confianca_fato"] for c in ind["casos"]} <= {"alta", "média", "baixa"}
    assert {c["forca_leitura"] for c in ind["casos"]} <= {"forte", "média", "fraca", "não conclusivo"}
    assert all(c["fonte_url"].startswith("http") and " | " not in c["fonte_url"] for c in ind["casos"])


def test_indireto_avisos_e_categorias(ind):
    av = " ".join(ind["meta"]["avisos"]).lower()
    for trecho in ("não é recomendação de voto", "dependem da seleção", "juízos dos autores", "não verificados"):
        assert trecho in av
    assert [c["id"] for c in ind["categorias"]] == list(range(1, 13))
    assert all(c["nome"] and c["descricao"] for c in ind["categorias"])
    assert ind["resumos"][-1]["secao"] == "Resumo da aba"
    assert ind["simetria"]["assimetrias_restantes"] and ind["simetria"]["tabela"]


def test_indireto_tops_respeitam_regra(ind):
    por_id = {c["id"]: c for c in ind["casos"]}
    for l, ids in ind["top_fortes"].items():
        assert len(ids) <= 10
        assert all(por_id[i]["forca_leitura"] in ("forte", "média") and not por_id[i]["disputado"] for i in ids)
    for l, ids in ind["top_fracos"].items():
        assert len(ids) <= 5
        assert all(por_id[i]["forca_leitura"] in ("fraca", "não conclusivo") for i in ids)


def test_indireto_tamanho(ind):
    t = os.path.getsize(os.path.join(WEB, "indireto.json"))
    assert 50_000 < t < 1_000_000


def test_indireto_sample_pequena():
    assert os.path.getsize(os.path.join(FIX, "indireto_sample.json")) < 60_000


@pytest.mark.skipif(not NOTAS_OK, reason="research_notes ausente")
def test_indireto_gerador_reproduz_arquivo(ind):
    novo = gi.construir()
    novo["meta"]["gerado_em"] = ind["meta"]["gerado_em"]
    assert novo == ind, "indireto.json desatualizado: rode python simulador/gerar_indireto_json.py"


# ---------- nordeste ----------
@pytest.mark.parametrize("caminho", [os.path.join(WEB, "nordeste_trajetoria.json"), os.path.join(FIX, "nordeste_trajetoria_sample.json")])
def test_nordeste_esquema(caminho):
    d = carrega(caminho)
    for k in gn.TOPO:
        assert k in d
    assert {"uf", "anos_PT", "anos_aliados_esquerda", "anos_outros", "mandatos"} <= set(d["partidos"][0])
    assert {"item", "valor_citado", "valor_verificado", "veredito", "fonte_url"} <= set(d["numeros_usuario"][0])
    assert {"indicador", "unidade", "series"} <= set(d["trajetoria"][0])
    assert {"grupo", "anos", "valores"} == set(d["trajetoria"][0]["series"][0])
    assert {"indicador", "resultado", "nota"} <= set(d["comparacao_pt"][0])
    assert {"grupo", "indicador", "resultado"} <= set(d["espelho"][0])
    assert d["eleitoral"]["tabela"] and d["limites"] and d["resumo"]


def test_nordeste_conteudo(ne):
    gn.validar(ne)
    v = [n["veredito"] for n in ne["numeros_usuario"]]
    assert v.count("confirmado") == 7 and set(v) <= {"confirmado", "diferente", "parcial"}
    pi = next(p for p in ne["partidos"] if p["uf"] == "PI")
    se = next(p for p in ne["partidos"] if p["uf"] == "SE")
    assert any(m["partido"] == "PT" and m["inicio"].endswith("2003") for m in pi["mandatos"])
    assert any(m["partido"] == "PT" and m["inicio"].endswith("2007") for m in se["mandatos"])
    assert "Piauí" in ne["meta"]["correcao"] and "Sergipe" in ne["meta"]["correcao"]
    assert len(ne["trajetoria"]) == 8
    for t in ne["trajetoria"]:
        assert len(t["series"]) == 4
        assert all(len(s["anos"]) == len(s["valores"]) and s["anos"] == sorted(s["anos"]) for s in t["series"])
    txt = json.dumps(ne["comparacao_pt"], ensure_ascii=False)
    assert "Homicídios" in txt and "Ceará e Piauí" in txt
    assert any("significativ" in c["resultado"] for c in ne["comparacao_pt"])


def test_nordeste_tamanho(ne):
    t = os.path.getsize(os.path.join(WEB, "nordeste_trajetoria.json"))
    assert 10_000 < t < 400_000


def test_nordeste_sample_pequena():
    assert os.path.getsize(os.path.join(FIX, "nordeste_trajetoria_sample.json")) < 30_000


@pytest.mark.skipif(not NOTAS_OK, reason="research_notes ausente")
def test_nordeste_gerador_reproduz_arquivo(ne):
    novo = gn.construir()
    novo["meta"]["gerado_em"] = ne["meta"]["gerado_em"]
    assert novo == ne, "nordeste_trajetoria.json desatualizado: rode python simulador/gerar_nordeste_trajetoria_json.py"
