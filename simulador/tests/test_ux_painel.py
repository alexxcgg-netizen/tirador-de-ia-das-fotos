"""Testes da reforma de UX do painel: navegação em 2 níveis, comparador integrado, tokens, acessibilidade,
neutralidade e glossário. Os testes de navegador estão em test_ux_navegador.py."""
import json
import re
import subprocess
import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import publicar  # noqa: E402
from cores_util import contraste, delta_e, dist_rgb

WEB = publicar.ORIG
HTML = (WEB / "index.html").read_text(encoding="utf-8")
COMP = (publicar.AQUI.parent / "comparador" / "index.html").read_text(encoding="utf-8")
TABS_ANTIGAS = ["segundo-turno", "primeiro-turno", "estados", "nordeste", "realidade", "modelos", "pesquisas", "bastidores", "curiosidades"]
NOVAS = ["comece", "indireto", "campanha-2t", "democracia", "propostas", "cenarios", "glossario"]


def tokens(bloco):
    return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", bloco))


def blocos_tokens():
    claro = HTML[HTML.index(":root {"):HTML.index("@media (prefers-color-scheme: dark)")]
    escuro = HTML[HTML.index('@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {'):HTML.index(':root[data-theme="dark"] {')]
    return tokens(claro), tokens(escuro)


# ---------- navegação
def test_cinco_areas_no_nivel_1_e_todo_painel_mapeado():
    grupos = re.findall(r'<button role="tab" id="grp-([a-z]+)"', HTML)
    assert grupos == ["comece", "ganhar", "checagem", "propostas", "dados"]
    paineis = set(re.findall(r'data-painel="([a-z0-9-]+)"', HTML))
    assert paineis == set(TABS_ANTIGAS + NOVAS)
    mapa = re.search(r"var GRUPOS = \{(.*?)\};", HTML, re.S).group(1)
    for p in paineis:
        assert f'"{p}"' in mapa, p
    subs = re.findall(r'<button role="tab" id="tab-([a-z0-9-]+)" data-grupo="([a-z]+)"', HTML)
    assert {s for s, _ in subs} == paineis - {"comece"}


def test_areas_novas_e_subabas():
    assert 'id="tab-indireto" data-grupo="checagem"' in HTML and "Indireto: o que cada um faz × diz" in HTML
    assert 'id="tab-glossario" data-grupo="dados"' in HTML and "Glossário e regras" in HTML
    assert 'id="tab-propostas" data-grupo="propostas"' in HTML and 'id="tab-cenarios" data-grupo="propostas"' in HTML
    assert 'id="gl-lista"' in HTML and 'id="ne-trajetoria"' in HTML


def test_hashes_antigos_resolvem():
    corpo = HTML[HTML.index("function irPara"):]
    assert "TABS.indexOf(id) >= 0" in corpo
    for h in TABS_ANTIGAS:
        assert f'"{h}"' in re.search(r"var GRUPOS = \{(.*?)\};", HTML, re.S).group(1)
    assert "propostas-passo-" in corpo


def test_comparador_dentro_da_pagina_e_sem_link_externo():
    assert 'id="painel-propostas"' in HTML and "window.__cmp" in HTML and 'id="cmp-passo-3"' in HTML
    assert "↗" not in HTML
    for a in re.findall(r"<a\b[^>]*>", HTML):
        assert "comparador.html" not in a, a


def test_integracao_em_dia_com_a_fonte():
    """web/index.html tem de ser exatamente o resultado de integrar comparador/index.html (python simulador/publicar.py)."""
    assert publicar.integrar_comparador(HTML, COMP) == HTML


def test_css_do_comparador_nao_vaza():
    css = HTML[HTML.index("/* CMP:CSS:INICIO */"):HTML.index("/* CMP:CSS:FIM */")]
    seletores = []
    for cab in re.findall(r"(?m)^([^{}@/\n][^{}]*)\{", css):
        seletores += [s.strip() for s in cab.split(",")]
    assert len(seletores) > 100
    ruins = [s for s in seletores if not s.startswith("#painel-propostas")]
    assert not ruins, ruins[:5]


def test_prefixar_css():
    out = publicar.prefixar_css(":scope { color: red; } :scope .a, p > b { x: y } @media (max-width: 5px) { :scope .c { z: 1 } }")
    assert "#painel-propostas {" in out and "#painel-propostas .a" in out and "#painel-propostas p > b" in out
    assert "@media (max-width: 5px) {\n#painel-propostas .c" in out


# ---------- tokens, contraste, paleta
def test_contraste_dos_textos_nos_dois_temas():
    claro, escuro = blocos_tokens()
    for nome, t in (("claro", claro), ("escuro", escuro)):
        for txt in ("text", "text-2", "text-3"):
            for sup in ("bg", "surface", "surface-2"):
                cor = t.get(txt) or claro[txt]
                fundo = t.get(sup) or claro[sup]
                assert contraste(cor, fundo) >= 4.5, (nome, txt, sup, round(contraste(cor, fundo), 2))


def test_cores_dos_candidatos_validadas_e_sem_cor_de_partido():
    claro, escuro = blocos_tokens()
    for nome, t, fundo in (("claro", claro, claro["surface"]), ("escuro", escuro, escuro["surface"])):
        a, b = t["cand-a"], t["cand-b"]
        assert contraste(a, fundo) >= 3 and contraste(b, fundo) >= 3, nome
        assert min(delta_e(a, b, "protan"), delta_e(a, b, "deutan")) >= 8, nome
        assert delta_e(a, b) >= 15, nome
    # nenhuma cor de partido conhecida (vermelho PT, azul PL, amarelo/verde) em nenhum token de cor do painel e do comparador
    partidos = ["#e30613", "#d60000", "#cc0000", "#ff0000", "#0033a0", "#0b3d91", "#0000ff", "#ffdf00", "#ffd700", "#009c3b", "#00a859"]
    cores = set()
    for t in blocos_tokens():
        cores |= {v for v in t.values()}
    for c in cores:
        for p in partidos:
            assert dist_rgb(c, p) > 60, (c, p)
    css_cmp = COMP[COMP.index("<style>"):COMP.index("</style>")]
    for lit in re.findall(r"#[0-9a-fA-F]{6}\b", css_cmp):
        for p in partidos:
            assert dist_rgb(lit, p) > 60, (lit, p)


def test_sem_fonte_menor_que_12px_no_css():
    estilos = re.findall(r"<style>(.*?)</style>", HTML, re.S)
    for css in estilos:
        for v in re.findall(r"font-size:\s*([0-9.]+)px", css):
            assert float(v) >= 12, v
    assert 'ctx.font = "12px "' in HTML


# ---------- acessibilidade
def test_canvas_com_rotulo_e_abas_com_aria():
    for tag in re.findall(r"<canvas\b[^>]*>", HTML):
        assert "aria-label=" in tag, tag
    for tag in re.findall(r'<button role="tab"[^>]*>', HTML):
        assert "aria-controls=" in tag and "aria-selected=" in tag, tag
    assert "cv.setAttribute(\"role\", \"img\")" in HTML       # todo gráfico recebe role=img ao ser criado
    assert "Ver como tabela" in HTML and "Como ler:" in HTML


def test_botoes_so_com_icone_tem_nome():
    for tag in re.findall(r"<button[^>]*>\s*<svg[^>]*>", HTML):
        assert "aria-label=" in tag, tag


def test_ids_unicos_no_html_estatico():
    ids = re.findall(r'\sid="([A-Za-z0-9_-]+)"', HTML[:HTML.index("<script")])
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, dup


# ---------- neutralidade do comparador
def test_comparador_neutro_por_construcao():
    assert "var PESO_PADRAO = 5;" in COMP and "s.w[a.id] = PESO_PADRAO; s.r[a.id] = {};" in COMP     # pesos iguais, notas vazias
    assert "order: ALPHA.slice()" in COMP and re.search(r"ALPHA = CANDS\.map", COMP)
    bloco = COMP[COMP.index("var CANDS"):COMP.index("var ALPHA")]
    ids = re.findall(r'\{ id: "([a-z]+)",\s+nome: "([^"]+)"', bloco)
    assert len(ids) == 6
    assert [n for _, n in ids] == sorted((n for _, n in ids), key=lambda s: s.lower())      # ordem alfabética
    assert "Quanto essa proposta te convence?" in COMP and COMP.count("Quanto essa proposta te convence?") == 1   # mesma pergunta para todos
    res = COMP[COMP.index("function renderResult"):COMP.index("function textoResultado")]
    assert res.count(".sort(") == 1 and "var scores = r.inc.map" in res        # o único sort é no vetor de notas (para a diferença); candidatos ficam na ordem de exibição
    assert "r.inc.map(function (c)" in res and "state.order.filter" in COMP
    assert "Não é recomendação nem previsão." in COMP and "Recomeçar" in COMP and "Voltar ao passo 2" in COMP and "Voltar ao início do painel" in COMP
    assert "à frente do segundo" not in COMP          # sem linguagem de placar
    assert 'class="mono' in COMP or "mono c-" in COMP


def test_cores_do_comparador_sao_as_do_painel():
    assert "--c-lula: var(--cand-a)" in COMP and "--c-flavio: var(--cand-b)" in COMP
    assert "#2f5fae" not in COMP and "#7d4aa8" not in COMP


def test_ordem_alfabetica_documentada():
    assert "alfabética pelo primeiro nome" in HTML and "Flávio Bolsonaro, depois Lula" in HTML
    assert 'id="gl-regras"' in HTML


# ---------- glossário
def test_glossario_termos_e_tamanho():
    g = json.loads((WEB / "glossario.json").read_text(encoding="utf-8"))
    ids = {t["id"] for t in g["termos"]}
    for obrigatorio in ("monte-carlo", "intervalo-80", "p-lula", "pit", "calibrado", "neutro", "vies-pleno", "house-effect", "kaitz", "efeito-farol", "efeito-sanduiche", "backtest", "votos-validos", "brier", "p-p"):
        assert obrigatorio in ids, obrigatorio
    for t in g["termos"]:
        assert len(t["definicao"].split()) <= 30, t["id"]
    assert len(g["termos"]) >= 40


# ---------- formatação em português (módulo FMT, executado em node)
@pytest.mark.skipif(shutil.which("node") is None, reason="node não instalado")
def test_formatacao_ptbr():
    ini, fim = HTML.index("/* FMT:INICIO"), HTML.index("/* FMT:FIM */")
    codigo = HTML[ini:fim]
    codigo = codigo[:codigo.rindex("var fmtPct")] if "var fmtPct" in codigo else codigo
    prog = codigo + """
const casos = [FMT.n(1234.5,1), FMT.n(0,1), FMT.n(-3.04,1), FMT.n(null), FMT.n(undefined), FMT.pct(0.479), FMT.pct(null), FMT.sinal(4.3), FMT.sinal(-4.3), FMT.sinal(0), FMT.pp(-2.55,1), FMT.mi(57000292), FMT.mi(12345678901,0), FMT.vot(15000000), FMT.vot(5100000), FMT.vot(450000), FMT.vot(null), FMT.faixa(43.93,51.79), FMT.pc(47.857)];
console.log(JSON.stringify(casos));
"""
    out = subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout
    got = json.loads(out)
    nbsp = " "
    assert got[0] == "1.234,5" and got[1] == "0,0" and got[2].replace("−", "-") == "-3,0"
    assert got[3] == "–" and got[4] == "–"
    assert got[5] == "47,9%" and got[6] == "–"
    assert got[7] == "+4,3" and got[8].replace("−", "-") == "-4,3" and got[9] == "0,0"
    assert got[10].replace("−", "-").replace(nbsp, " ") in ("-2,5 p.p.", "-2,6 p.p.")
    assert got[11] == "57,0 mi" and got[12] == "12.346 mi"
    assert got[13] == "15,0 mi" and got[14] == "5,10 mi" and got[15] == "450 mil" and got[16] == "–"
    assert got[17] == "43,9–51,8%" and got[18] == "47,9%"
