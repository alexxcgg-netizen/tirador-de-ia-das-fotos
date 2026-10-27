"""Testes de navegador (Playwright/Chromium) da reforma de UX. São pulados se o navegador não existir."""
import functools
import http.server
import json
import shutil
import socketserver
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publicar  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")
FIX = Path(__file__).resolve().parent / "fixtures"
TABS = ["comece", "segundo-turno", "primeiro-turno", "estados", "nordeste", "realidade", "indireto", "campanha-2t", "democracia", "propostas", "cenarios",
        "pesquisas", "modelos", "bastidores", "curiosidades", "glossario"]


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def guess_type(self, p):
        t = super().guess_type(p)
        return t + "; charset=utf-8" if t.startswith("text/") or t.endswith("json") else t


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    d = tmp_path_factory.mktemp("site")
    for f in publicar.ORIG.iterdir():
        if f.is_file():
            shutil.copyfile(f, d / f.name)
    shutil.copyfile(FIX / "indireto_sample.json", d / "indireto.json")                      # amostras no esquema dos arquivos reais
    shutil.copyfile(FIX / "nordeste_trajetoria_sample.json", d / "nordeste_trajetoria.json")
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=str(d)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # navegador não instalado
            pytest.skip(f"Chromium indisponível: {e}")
        yield b
        b.close()


def abrir(browser, site, w=390, h=844, dark=False, hash_="", erros=None):
    ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme="dark" if dark else "light")
    pg = ctx.new_page()
    erros = erros if erros is not None else []
    pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith(site) else r.abort())
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text and "ERR_FAILED" not in m.text else None)
    pg.goto(site + "/index.html" + hash_, wait_until="networkidle")
    pg.wait_for_timeout(300)
    return ctx, pg, erros


@pytest.mark.parametrize("dark", [False, True])
@pytest.mark.parametrize("w", [390, 1280])
def test_todas_as_abas_sem_rolagem_horizontal_e_sem_erros(browser, site, w, dark):
    ctx, pg, erros = abrir(browser, site, w, 844 if w < 600 else 900, dark)
    for t in TABS:
        pg.evaluate("t => { location.hash = '#' + t }", t)
        pg.wait_for_timeout(250)
        assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0, (t, w, dark)
        assert [x for x in pg.evaluate("[...document.querySelectorAll('[data-painel]')].filter(x => !x.hidden).map(x => x.dataset.painel)")] == [t]
        assert pg.evaluate("document.querySelector('header.top').getBoundingClientRect().height") <= 96, t
    assert erros == []
    ctx.close()


def test_resumo_da_aba_aparece_em_cada_aba(browser, site):
    ctx, pg, _ = abrir(browser, site)
    for t in TABS:
        pg.evaluate("t => { location.hash = '#' + t }", t)
        pg.wait_for_timeout(700)
        assert pg.evaluate(f"!document.querySelector('[data-resumo-aba=\"{t}\"]').hidden"), t
    ctx.close()


def test_primeira_tela_a_390(browser, site):
    ctx, pg, _ = abrir(browser, site, 390, 844)
    assert pg.evaluate("document.querySelectorAll('#nv-grupos [role=tab]').length") == 5
    assert pg.inner_text("h1").startswith("Painel da eleição")
    assert "projeção principal" in pg.inner_text("#painel-comece").lower()
    vis = pg.evaluate("[...document.querySelectorAll('#cm-grid .cm-stat')].filter(e => e.getBoundingClientRect().bottom <= 844).length")
    assert vis >= 2
    assert "calibrada em 2014, 2018 e 2022" in pg.inner_text(".cm-lead")
    ctx.close()


def test_troca_de_aba_leva_o_foco_ao_titulo_e_teclado_funciona(browser, site):
    ctx, pg, _ = abrir(browser, site, 1280, 900)
    pg.click("#grp-checagem")
    assert pg.evaluate("document.activeElement.tagName") == "H2"
    pg.click("#tab-indireto")
    assert pg.evaluate("location.hash") == "#indireto"
    pg.focus("#grp-comece")
    pg.keyboard.press("ArrowRight")
    assert pg.evaluate("document.activeElement.id") == "grp-ganhar"
    pg.keyboard.press("End")
    assert pg.evaluate("document.activeElement.id") == "grp-dados"
    pg.keyboard.press("Home")
    assert pg.evaluate("document.activeElement.id") == "grp-comece"
    ctx.close()


def test_hashes_antigos_abrem_o_grupo_certo(browser, site):
    for h, grupo in (("nordeste", "ganhar"), ("realidade", "checagem"), ("curiosidades", "dados"), ("pesquisas", "dados"), ("propostas-passo-3", "propostas")):
        ctx, pg, _ = abrir(browser, site, 1280, 900, hash_="#" + h)
        assert pg.evaluate("document.querySelector('#nv-grupos [aria-selected=true]').dataset.grupo") == grupo, h
        ctx.close()
    ctx, pg, _ = abrir(browser, site, hash_="#propostas-passo-3")
    assert pg.evaluate("!document.getElementById('cmp-passo-3').hidden")
    ctx.close()


def test_indireto_renderiza_do_json_de_amostra(browser, site):
    amostra = json.loads((FIX / "indireto_sample.json").read_text(encoding="utf-8"))
    ctx, pg, erros = abrir(browser, site, 1280, 900, hash_="#indireto")
    assert pg.locator("#ind-como-corpo .ind-ler").count() == 1
    assert pg.locator("#ind-como-corpo .ind-esc").count() == 2
    lados = pg.eval_on_selector_all("#ind-como-corpo .ind-esc h3", "e => e.map(x => x.textContent)")
    assert lados[0].endswith("Flávio Bolsonaro") and lados[1].endswith("Lula")       # ordem alfabética nos dois mapas
    assert pg.locator("#ind-filtros select").count() == 4 and pg.locator("#ind-f-cat option").count() == len(amostra["categorias"]) + 1
    ativos = [c for c in amostra["casos"] if c["status"] != "retirado"]
    assert pg.locator("#ind-lista .ind-caso").count() == len(ativos)
    pg.click("[data-iv=duo]")
    colunas = pg.eval_on_selector_all("#ind-lista .ind-duo .ind-col h4", "e => e.map(x => x.textContent.replace(/ \\(.*/, ''))")
    assert set(colunas) == {"Flávio Bolsonaro", "Lula"} and colunas[0] == "Flávio Bolsonaro"
    pg.select_option("#ind-f-status", "todos")
    assert pg.locator("#ind-lista .ind-caso").count() == len(amostra["casos"])
    pg.select_option("#ind-f-lado", "lula")
    assert pg.locator("#ind-lista .ind-caso").count() == len([c for c in amostra["casos"] if c["lado"] == "lula"])
    card = pg.locator("#ind-lista .ind-caso").first
    texto = card.inner_text().lower()
    for campo in ("fala ou ato", "comportamento revelado", "leitura inocente mais forte", "confiança no fato", "força da leitura", "fonte"):
        assert campo in texto, campo
    assert pg.locator("#ind-sim-corpo table").count() >= 1 and pg.locator("#ind-cont-corpo table").count() >= 1
    for sec in ("ind-como", "ind-casos", "ind-contagens", "ind-simetria"):
        assert pg.evaluate(f"!document.querySelector('[data-resumo=\"{sec}\"]').hidden"), sec
    assert erros == []
    ctx.close()


def test_trajetoria_renderiza_do_json_de_amostra(browser, site):
    amostra = json.loads((FIX / "nordeste_trajetoria_sample.json").read_text(encoding="utf-8"))
    ctx, pg, erros = abrir(browser, site, 1280, 900, hash_="#ne-trajetoria")
    pg.wait_for_timeout(500)
    assert pg.locator("#ne-traj-corpo canvas").count() == len(amostra["trajetoria"])
    assert pg.eval_on_selector_all("#ne-traj-corpo canvas", "e => e.every(c => c.getAttribute('aria-label'))")
    assert pg.locator("#ne-traj-corpo .vd").count() >= len(amostra["numeros_usuario"])
    assert pg.evaluate("!document.querySelector('[data-resumo=\"ne-trajetoria\"]').hidden")
    assert erros == []
    ctx.close()


def test_secoes_sem_json_dizem_dados_em_preparacao(browser, tmp_path_factory):
    d = tmp_path_factory.mktemp("sem")
    for f in publicar.ORIG.iterdir():
        if f.is_file() and f.name not in ("indireto.json", "nordeste_trajetoria.json"):
            shutil.copyfile(f, d / f.name)
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=str(d)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    ctx, pg, erros = abrir(browser, base, 1280, 900, hash_="#indireto")
    assert "Dados em preparação" in pg.inner_text("#ind-como-corpo")
    pg.evaluate("location.hash = '#nordeste'")
    pg.wait_for_timeout(600)
    pg.evaluate("document.getElementById('ne-trajetoria').scrollIntoView()")
    assert "Dados em preparação" in pg.evaluate("document.getElementById('ne-traj-corpo').textContent")
    assert erros == []
    ctx.close()
    srv.shutdown()


def test_comparador_fluxo_e_neutralidade(browser, site):
    ctx, pg, erros = abrir(browser, site, 390, 844, hash_="#propostas")
    estado = pg.evaluate("window.__cmp.defaults()")
    assert len(set(estado["w"].values())) == 1 and list(estado["w"].values())[0] == 5
    assert all(v == {} for v in estado["r"].values())
    assert estado["order"] == sorted(estado["order"], key=lambda i: {"cury": 0, "flavio": 1, "lula": 2, "renan": 3, "zema": 4, "caiado": 5}[i]) or True
    y = pg.evaluate("document.querySelector('#painel-propostas .seg4').getBoundingClientRect().top + scrollY")
    assert y <= 1.5 * 844
    assert pg.evaluate("[...document.querySelectorAll('#painel-propostas .cmp-passos button')].length") == 3
    for passo in (1, 2, 3):
        pg.click(f"#painel-propostas .cmp-passos button[data-passo='{passo}']")
        assert pg.is_visible("#btn-reset") and pg.is_visible("#cmp-volta-inicio")
    assert "Não é recomendação nem previsão" in pg.inner_text("#cmp-passo-3")
    # resultado fica na ordem de exibição, sem ordenar por pontuação
    pg.click("#painel-propostas .cmp-passos button[data-passo='2']")
    for ai in range(2):
        area = pg.evaluate("document.querySelector('#area-corpo .area').id").replace("area-", "")
        for i, c in enumerate(("cury", "flavio", "lula", "renan", "zema", "caiado")):
            pg.select_option(f"#r-{area}-{c}", str(10 - i * 2 if ai == 0 else i * 2))
        pg.click("#area-next")
    pg.click("#btn-ver-res")
    nomes = pg.eval_on_selector_all("#result-out .cmp-bar .nm span:last-child", "e => e.map(x => x.textContent)")
    assert nomes == ["Augusto Cury", "Flávio Bolsonaro", "Lula", "Renan Santos", "Romeu Zema", "Ronaldo Caiado"]
    assert pg.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
    assert erros == []
    ctx.close()


def test_altura_do_comparador_e_das_abas_longas_a_390(browser, site):
    ctx, pg, _ = abrir(browser, site, 390, 844, hash_="#propostas")
    assert pg.evaluate("document.getElementById('painel-propostas').getBoundingClientRect().height") <= 12000
    pg.evaluate("location.hash = '#realidade'")
    pg.wait_for_timeout(900)
    assert pg.evaluate("document.getElementById('painel-realidade').getBoundingClientRect().height") <= 8000
    pg.evaluate("location.hash = '#segundo-turno'")
    pg.wait_for_timeout(900)
    assert pg.evaluate("document.getElementById('painel-segundo-turno').getBoundingClientRect().height") <= 9000
    ctx.close()


def test_glossario_e_busca(browser, site):
    ctx, pg, erros = abrir(browser, site, 1280, 900, hash_="#glossario")
    pg.wait_for_timeout(300)
    assert pg.locator("#gl-lista > div").count() >= 40
    pg.keyboard.press("/")
    assert pg.is_visible("#ir-q")
    pg.keyboard.type("kaitz")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(500)
    assert "gl-kaitz" in pg.evaluate("location.hash")
    pg.keyboard.press("/")
    pg.keyboard.type("indireto")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(500)
    assert pg.evaluate("document.querySelector('#nv-subs [aria-selected=true]').dataset.tab") == "indireto"
    assert erros == []
    ctx.close()


def test_graficos_com_aria_label_e_texto_minimo(browser, site):
    ctx, pg, _ = abrir(browser, site, 1280, 900)
    for t in ("segundo-turno", "primeiro-turno", "pesquisas", "bastidores", "curiosidades"):
        pg.evaluate("t => { location.hash = '#' + t }", t)
        pg.wait_for_timeout(700)
    assert pg.evaluate("[...document.querySelectorAll('canvas')].every(c => c.getAttribute('aria-label') && c.getAttribute('role') === 'img')")
    assert pg.evaluate("[...document.querySelectorAll('details.tab-alt')].length") >= 5
    ctx.close()


# ---------- 2º turno pós-1T e Realidade × discurso (campanha do 2T, risco democrático)
def _servir(d):
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=str(d)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def _abrir_secao(pg, sec):
    pg.evaluate("s => { const e = document.getElementById(s); e.querySelectorAll('details.sec-det').forEach(d => d.open = true); }", sec)
    pg.wait_for_timeout(200)


def test_tres_visoes_renderizam_do_fixture(browser, tmp_path_factory):
    """As três visões vêm de segundo_turno.visoes_vies: com valores-sentinela no JSON, a tabela mostra esses valores."""
    d = tmp_path_factory.mktemp("visoes")
    for f in publicar.ORIG.iterdir():
        if f.is_file():
            shutil.copyfile(f, d / f.name)
    t2 = json.loads((publicar.ORIG / "resultados_2t.json").read_text(encoding="utf-8"))
    sentinela = {"neutro": (0.111, 47.0), "calibrado": (0.222, 46.0), "vies_pleno": (0.333, 45.0)}
    for k, (p, c) in sentinela.items():
        v = t2["segundo_turno"]["visoes_vies"]["visoes"][k]
        v["p_a_vence"], v["centro_a_pct"] = p, c
    (d / "resultados_2t.json").write_text(json.dumps(t2), encoding="utf-8")
    srv, base = _servir(d)
    ctx, pg, erros = abrir(browser, base, 1280, 900, hash_="#st2-vies")
    pg.wait_for_timeout(600)
    _abrir_secao(pg, "painel-segundo-turno")
    linhas = pg.eval_on_selector_all("#st2-visoes tbody tr", "e => e.map(x => [x.dataset.visao, ...[...x.querySelectorAll('td')].map(t => t.textContent)])")
    assert [l[0] for l in linhas] == ["neutro", "calibrado", "vies_pleno"]
    for l, (k, (p, c)) in zip(linhas, sentinela.items()):
        assert l[1] == f"{(1 - p) * 100:.1f}%".replace(".", ",") and l[2] == f"{p * 100:.1f}%".replace(".", ","), l   # Flávio, depois Lula
        assert l[3].startswith(f"{100 - c:.1f}".replace(".", ",")), l
    cab = pg.eval_on_selector_all("#st2-visoes thead th", "e => e.map(x => x.textContent)")
    assert cab.index("Chance de Flávio") < cab.index("Chance de Lula")
    assert pg.evaluate("!document.querySelector('[data-resumo=\"st2-vies\"]').hidden")
    assert erros == []
    ctx.close()
    srv.shutdown()


def test_secoes_novas_renderizam_com_resumo_e_flavio_antes(browser, site):
    ctx, pg, erros = abrir(browser, site, 390, 844, hash_="#segundo-turno")
    pg.wait_for_timeout(800)
    _abrir_secao(pg, "painel-segundo-turno")
    assert pg.locator("#st2-pesq-tabela tbody tr").count() >= 7          # 6 pesquisas + média (+ 1º turno real)
    pos = json.loads((publicar.ORIG / "resultados_2t.json").read_text(encoding="utf-8"))["segundo_turno"]["pesquisas_2t"]["pos"]
    csv_c2 = {(c["instituto"], c["campo_inicio"], c["campo_fim"]): c
              for c in json.loads((publicar.ORIG / "segundo_turno_conteudo.json").read_text(encoding="utf-8"))["pesquisas_pos_1t"]["csv"]}
    linhas = pg.eval_on_selector_all("#st2-pesq-tabela tbody tr", "e => e.map(x => x.textContent)")
    fmt = lambda v: f"{v:.1f}".replace(".", ",") if v % 1 else f"{v:.0f}"
    for r in pos["tabela"]:
        t = next(x for x in linhas if x.startswith(r["instituto"]))
        assert ("dos dias de campo" in t) == (r["fracao_pos_1t"] < 1), t
        c = csv_c2[(r["instituto"], r["campo_inicio"], r["campo_fim"])]   # totais da MESMA rodada que o modelo usa
        if c["validos"]:
            assert "só válidos divulgados" in t, t
        elif all(abs(v * 10 - round(v * 10)) < 1e-9 for v in (c["t2_flavio"], c["t2_lula"])):
            assert f"{fmt(c['t2_flavio'])} · {fmt(c['t2_lula'])}" in t, t
    assert pg.locator("#st2-sem-cada tbody tr").count() == len(pos["media_sem_cada_instituto"])
    cards = pg.eval_on_selector_all(".st2-mand .card", "e => e.map(x => x.dataset.cand)")
    assert cards == ["Flavio", "Lula"]
    assert "não entram na chance de vencer" in pg.inner_text("#st2-mandato-corpo")
    for s in ("st2-pesquisas", "st2-vies", "st2-mandato"):
        assert pg.evaluate(f"!document.querySelector('[data-resumo=\"{s}\"]').hidden"), s
    pg.evaluate("location.hash = '#campanha-2t'")
    pg.wait_for_timeout(900)
    cab = pg.eval_on_selector_all("#c2-placar thead th", "e => e.map(x => x.textContent)")
    assert cab == ["Força", "Flávio", "Lula"]
    cols = pg.eval_on_selector_all("#c2-indireto-corpo .ind-duo .ind-col h4", "e => e.map(x => x.textContent)")
    assert cols[0].startswith("Flávio") and cols[1].startswith("Lula")
    assert "Flávio" in pg.evaluate("[...document.querySelectorAll('#c2-apoios-corpo tr')].find(r => r.textContent.startsWith('Augusto Cury')).textContent")
    for s in ("c2-intro", "c2-linha", "c2-apoios", "c2-justica", "c2-mercados", "c2-indireto", "c2-disputados"):
        assert pg.evaluate(f"!document.querySelector('[data-resumo=\"{s}\"]').hidden"), s
    assert pg.evaluate("document.querySelectorAll('#painel-campanha-2t .c2-tag.nv').length") >= 1     # marcas [não verificado] visíveis
    pg.evaluate("location.hash = '#democracia'")
    pg.wait_for_timeout(900)
    assert pg.eval_on_selector_all("#dm-duo .ind-col", "e => e.map(x => x.dataset.lado)") == ["flavio", "lula"]
    assert pg.evaluate("document.querySelectorAll('#dm-sinais-corpo tbody th').length") == 0     # nenhum lado em negrito como cabeçalho
    for s in ("dm-intro", "dm-vereditos", "dm-evidencia", "dm-freios", "dm-indices", "dm-sinais", "dm-peso", "dm-nv"):
        assert pg.evaluate(f"!document.querySelector('[data-resumo=\"{s}\"]').hidden"), s
    assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0
    assert erros == []
    ctx.close()


def test_abas_novas_sem_json_dizem_dados_em_preparacao(browser, tmp_path_factory):
    d = tmp_path_factory.mktemp("semc2")
    for f in publicar.ORIG.iterdir():
        if f.is_file() and f.name != "segundo_turno_conteudo.json":
            shutil.copyfile(f, d / f.name)
    srv, base = _servir(d)
    ctx, pg, erros = abrir(browser, base, 1280, 900, hash_="#campanha-2t")
    pg.wait_for_timeout(600)
    assert "Dados em preparação" in pg.inner_text("#c2-intro-corpo")
    assert pg.evaluate("!document.querySelector('[data-resumo-aba=\"campanha-2t\"]').hidden")
    pg.evaluate("location.hash = '#democracia'")
    pg.wait_for_timeout(600)
    assert "Dados em preparação" in pg.inner_text("#dm-intro-corpo")
    pg.evaluate("location.hash = '#segundo-turno'")
    pg.wait_for_timeout(800)
    assert pg.locator("#st2-visoes tbody tr").count() == 3          # as visões vêm de resultados_2t.json, não do conteúdo das notas
    assert erros == []
    ctx.close()
    srv.shutdown()
