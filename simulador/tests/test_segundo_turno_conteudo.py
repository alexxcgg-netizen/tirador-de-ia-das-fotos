"""Testes do conteúdo do 2º turno pós-1T e da área Realidade × discurso (campanha do 2T e risco democrático):
gerador (simulador/gerar_segundo_turno_json.py), JSON publicado, seções do painel e neutralidade."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gerar_segundo_turno_json as G  # noqa: E402
import publicar  # noqa: E402

WEB = publicar.ORIG
HTML = (WEB / "index.html").read_text(encoding="utf-8")
JS = json.loads((WEB / "segundo_turno_conteudo.json").read_text(encoding="utf-8"))
NOVAS_SECOES = {
    "segundo-turno": ["st2-pesquisas", "st2-vies", "st2-mandato"],
    "campanha-2t": ["c2-intro", "c2-linha", "c2-apoios", "c2-justica", "c2-mercados", "c2-indireto", "c2-disputados"],
    "democracia": ["dm-intro", "dm-vereditos", "dm-evidencia", "dm-freios", "dm-indices", "dm-sinais", "dm-peso", "dm-nv"],
}


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _sem_data(d):
    d = json.loads(json.dumps(d))
    d["meta"].pop("gerado_em", None)
    return d


def test_json_publicado_em_dia_com_as_notas():
    """web/segundo_turno_conteudo.json tem de ser exatamente o que o gerador produz hoje a partir das notas."""
    assert _sem_data(G.gerar()) == _sem_data(JS)


def _textos(no, out):
    if isinstance(no, dict):
        if no.get("t") == "p":
            out.append(no["md"])
        if no.get("t") == "tab":
            out.extend(c for r in no["lin"] for c in r)
        for k, v in no.items():
            if k not in ("resumo", "resumo_aba"):
                _textos(v, out)
    elif isinstance(no, list):
        for v in no:
            _textos(v, out)
    return out


def test_nao_inventa_texto():
    """Todo parágrafo e toda célula de tabela extraídos existem literalmente numa das notas."""
    notas = _norm(G.NOTA_C.read_text(encoding="utf-8") + G.NOTA_D.read_text(encoding="utf-8") + G.NOTA_P.read_text(encoding="utf-8"))
    txt = _textos({k: JS[k] for k in ("campanha_2t", "risco_democratico", "pesquisas_pos_1t")}, [])
    assert len(txt) > 400
    for t in txt:
        assert _norm(t) in notas, t[:120]


def test_marcas_de_nao_verificado_preservadas():
    bruto = json.dumps(JS, ensure_ascii=False)
    for marca in ("[não verificado]", "[disputado]", "[reportado]"):
        assert marca in bruto, marca
    r4 = JS["campanha_2t"]["disputados"]["lista"]
    assert any("[não verificado]" in x for x in r4) and any("[disputado]" in x for x in r4)
    assert len(JS["risco_democratico"]["nao_verificado"]["lista"]) >= 10


def test_cury_apoia_flavio_na_tabela_de_apoios():
    tab = JS["campanha_2t"]["apoios"]["eliminados"]
    cury = [r for r in tab["lin"] if r[0].startswith("Augusto Cury")][0]
    posicao = cury[tab["cab"].index("Posição no 2T")]
    assert posicao.startswith("**Flávio**") and "08/10" in cury[tab["cab"].index("Data")]


def test_flavio_antes_de_lula_no_conteudo_novo():
    ind = JS["campanha_2t"]["indireto"]
    assert ind["placar"]["colunas"] == ["Flávio", "Lula"]
    cab = ind["vorcaro"]["tabela"]["cab"]
    assert max(i for i, c in enumerate(cab) if "Flávio" in c) < min(i for i, c in enumerate(cab) if "Lula" in c)
    for tb in (JS["risco_democratico"]["evidencia"]["sinais_tabela"], JS["risco_democratico"]["sinais"]["tabela"]):
        c = " ".join(tb["cab"])
        assert c.index("Flávio") < c.index("Lula")
    assert list(JS["risco_democratico"]["evidencia"])[:2] == ["flavio", "lula"]
    # placar com a mesma estrutura nos dois lados: um forte, cinco médias e uma fraca para cada (revisão de 12/10)
    n = {l["forca"]: (len(l["flavio"]), len(l["lula"])) for l in ind["placar"]["linhas"]}
    assert n == {"Forte": (1, 1), "Média": (5, 5), "Fraca": (1, 1)}
    assert all(cod in ind["casos"] for l in ind["placar"]["linhas"] for cod in l["flavio"] + l["lula"])


def test_cada_parte_tem_resumo_e_aba_tem_resumo_da_aba():
    C, R = JS["campanha_2t"], JS["risco_democratico"]
    for k in ("linha_tempo", "apoios", "justica", "mercados", "indireto", "disputados"):
        assert C[k]["resumo"] and all(x.strip() for x in C[k]["resumo"]), k
    for k in ("vereditos", "evidencia", "freios", "indices", "sinais", "peso", "nao_verificado"):
        assert R[k]["resumo"] and all(x.strip() for x in R[k]["resumo"]), k
    assert C["resumo_aba"] and R["resumo_aba"] and JS["pesquisas_pos_1t"]["resumo_aba"]
    for x in C["linha_tempo"]["resumo"] + R["vereditos"]["resumo"]:
        assert "**" not in x and "](" not in x          # texto puro nos quadros Resumo


def test_series_dos_indices():
    v = JS["risco_democratico"]["indices"]["vdem"]
    assert v["anos"][0] == 2014 and v["anos"][-1] == 2025
    assert v["series"]["Democracia liberal (LDI)"][v["anos"].index(2019)] == 0.528
    fh = JS["risco_democratico"]["indices"]["freedom_house"]
    assert dict(zip(fh["anos"], fh["valores"]))[2018] == 78


def test_pesquisas_pos_1t_batem_com_o_csv():
    P = JS["pesquisas_pos_1t"]
    nota = {r["instituto"]: r for r in P["tabela"]}
    primeira = {}                                   # a nota de 12/10 descreve a 1ª rodada pós-1T de cada instituto
    for r in sorted(P["csv"], key=lambda r: r["campo_fim"]):
        primeira.setdefault(r["instituto"], r)
    assert set(nota) == {"AtlasIntel", "Datafolha", "DataTrends", "Ipespe", "PoderData", "Vox Brasil"} and set(nota) <= set(primeira)
    for k in nota:
        assert float(nota[k]["flavio_total"].replace(",", ".")) == primeira[k]["t2_flavio"], k
        assert float(nota[k]["lula_total"].replace(",", ".")) == primeira[k]["t2_lula"], k
    assert primeira["Datafolha"]["campo_fim"] == "2026-10-07" and primeira["AtlasIntel"]["campo_inicio"] == "2026-10-03"
    assert "fonte primária" in P["verificacao"]["AtlasIntel"]["status"]


def test_secoes_novas_no_painel_terminam_com_resumo():
    for painel, secs in NOVAS_SECOES.items():
        corpo = HTML[HTML.index(f'data-painel="{painel}"'):]
        for s in secs:
            m = re.search(r'<section id="' + s + r'">([\s\S]*?)</section>', corpo)
            assert m, s
            ultima = m.group(1).rstrip().splitlines()[-1]
            assert f'<aside class="resumo" data-resumo="{s}" hidden></aside>' in ultima, s
            assert f'"{s}": function' in HTML, s
    for aba in ("campanha-2t", "democracia"):
        assert f'data-resumo-aba="{aba}"' in HTML and f'"{aba}": function' in HTML
    assert 'id="tab-campanha-2t" data-grupo="checagem"' in HTML and 'id="tab-democracia" data-grupo="checagem"' in HTML
    assert 'checagem: ["realidade", "indireto", "campanha-2t", "democracia"]' in HTML


def test_css_novo_sem_cores_proprias():
    """O CSS das seções novas usa só os tokens do painel (nenhuma cor nova, logo nenhuma cor de partido)."""
    ini = HTML.index("/* 2º turno pós-1T, campanha do 2º turno e risco democrático")
    css = HTML[ini:HTML.index("/* CMP:CSS:INICIO */")]
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", css)
    bloco = HTML[HTML.index("// ---------- 2º turno pós-1T (resultados_2t.json)"):HTML.index("// ---------- Indireto: o que cada um faz × diz (indireto.json)")]
    assert not re.search(r"#[0-9a-fA-F]{6}\b", bloco)
    cores = set(re.findall(r'css\("(--[a-z0-9-]+)"\)', bloco))
    assert cores <= {"--text", "--text-2", "--text-3", "--lula", "--flavio"}


def test_publicar_copia_o_conteudo_novo():
    src = (publicar.AQUI / "publicar.py").read_text(encoding="utf-8")
    assert '"segundo_turno_conteudo.json"' in src
    assert (publicar.DEST / "segundo_turno_conteudo.json").exists()
