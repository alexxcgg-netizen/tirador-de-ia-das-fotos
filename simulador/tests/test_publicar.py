"""publicar.py: cópia opcional dos JSON ao vivo (mercado e benchmarks) e conversão do HTML."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publicar  # noqa: E402


def test_copiar_opcional_ausente_nao_falha(tmp_path):
    assert publicar.copiar_opcional(tmp_path / "nao_existe.json", tmp_path / "dest.json") is False
    assert not (tmp_path / "dest.json").exists()


def test_copiar_opcional_copia(tmp_path):
    src = tmp_path / "mercado_ao_vivo.json"
    src.write_text(json.dumps({"gerado_utc": "2026-10-04T17:00:00Z"}), encoding="utf-8")
    dst = tmp_path / "out" / "mercado_ao_vivo.json"
    dst.parent.mkdir()
    assert publicar.copiar_opcional(src, dst) is True
    assert json.loads(dst.read_text(encoding="utf-8"))["gerado_utc"] == "2026-10-04T17:00:00Z"
    assert not (dst.parent / "mercado_ao_vivo.json.tmp").exists()


def test_index_tem_paineis_ao_vivo():
    html = (publicar.ORIG / "index.html").read_text(encoding="utf-8")
    out = publicar.converter(html)
    for alvo in ('id="sec-mercado"', 'id="sec-apur"', "mercado_ao_vivo.json", "benchmarks.json"):
        assert alvo in out
    assert "<html" not in out.lower() and "<body" not in out.lower()


def test_index_tem_secao_segundo_turno():
    html = (publicar.ORIG / "index.html").read_text(encoding="utf-8")
    out = publicar.converter(html)
    for alvo in ('id="segundo-turno"', 'href="#segundo-turno"', "resultados_alt_2t.json", 'id="c-transf"', 'id="st-uf"'):
        assert alvo in out
    # a seção do 2º turno vem antes das demais seções do painel
    assert out.index('id="segundo-turno"') < out.index('id="cards"')


def test_documento_comparador_tem_esqueleto_e_volta():
    frag = "<title>Comparador</title>\n<style>:root{--bg:#fff}</style>\n<link rel=\"stylesheet\" href=\"x.css\">\n<div class=\"wrap\">oi</div>\n"
    doc = publicar.documento_comparador(frag)
    assert doc.startswith("<!doctype html>") and "<body>" in doc and doc.rstrip().endswith("</html>")
    assert "viewport-fit=cover" in doc and 'charset="utf-8"' in doc
    assert 'href="index.html"' in doc and '<div class="wrap">oi</div>' in doc
    head = doc.split("</head>")[0]
    assert "<title>Comparador</title>" in head and 'href="x.css"' in head


def test_link_cenarios_so_se_existir():
    html = '<a class="tab-link" id="link-cenarios" href="cenarios.html" hidden>Cenários</a>'
    assert "hidden" in publicar.link_cenarios(html, False)
    assert "hidden" not in publicar.link_cenarios(html, True)
    idx = (publicar.ORIG / "index.html").read_text(encoding="utf-8")
    assert 'id="link-cenarios" href="cenarios.html" hidden' in idx and 'href="comparador.html"' in idx


def test_documento_cenarios_injeta_volta_so_se_faltar():
    doc = "<!doctype html>\n<html><head><title>C</title></head><body class=\"x\">\n<main>oi</main>\n</body></html>\n"
    out = publicar.documento_cenarios(doc)
    assert out.startswith("<!doctype html>") and out.count('href="index.html"') == 1
    assert out.index('<body class="x">') < out.index('href="index.html"') < out.index("<main>")
    ja = doc.replace("<main>", '<a href="index.html">voltar</a><main>')
    assert publicar.documento_cenarios(ja) == ja


def test_publicar_cenarios(tmp_path):
    orig, dest = tmp_path / "web", tmp_path / "pub"
    orig.mkdir(); dest.mkdir()
    assert publicar.publicar_cenarios(orig, dest) is False and not (dest / "cenarios.html").exists()
    (orig / "cenarios.html").write_text("<!doctype html><html><body><p>x</p></body></html>", encoding="utf-8")
    (orig / "cenarios.json").write_text("{}", encoding="utf-8")
    assert publicar.publicar_cenarios(orig, dest) is True
    assert 'href="index.html"' in (dest / "cenarios.html").read_text(encoding="utf-8")
    assert (dest / "cenarios.json").exists() and not (dest / "cenarios.html.tmp").exists()


def test_index_tem_abas_nordeste_e_curiosidades():
    out = publicar.converter((publicar.ORIG / "index.html").read_text(encoding="utf-8"))
    for alvo in ('id="tab-nordeste"', 'id="painel-nordeste"', "nordeste.json", 'id="ne-cen"',
                 'id="tab-curiosidades"', 'id="painel-curiosidades"', "curiosidades.json", 'id="cur-cards"'):
        assert alvo in out
    assert '"nordeste"' in out and '"curiosidades"' in out


def test_curiosidades_json_usa_placar_final():
    cu = json.loads((publicar.ORIG / "curiosidades.json").read_text(encoding="utf-8"))
    real = json.loads((publicar.AQUI / "data" / "avaliacao_1t.json").read_text(encoding="utf-8"))["real"]["nacional"]
    fl = f"{real['Flavio']:.2f}".replace(".", ",")
    card = next(c for c in cu["cards"] if c["titulo"].startswith("A menor diferença"))
    assert fl in card["texto"] and "44,98" not in card["texto"]
    assert "NÃO VERIFICADO" not in json.dumps([cu["cards"], cu["explicador"]], ensure_ascii=False)
    assert all(c.get("fonte_url") for c in cu["cards"])


def test_index_tem_aba_realidade():
    out = publicar.converter((publicar.ORIG / "index.html").read_text(encoding="utf-8"))
    for alvo in ('id="tab-realidade"', 'id="painel-realidade"', "realidade.json", 'id="rd-cards"',
                 'id="rd-claims"', 'id="rd-tally"', 'id="rd-empresas"', 'id="rd-ler"'):
        assert alvo in out
    assert '"realidade"' in out and "Realidade × discurso" in out


def test_realidade_json_contagem_e_fontes():
    rd = json.loads((publicar.ORIG / "realidade.json").read_text(encoding="utf-8"))
    itens = rd["checagem"]["itens"]
    conta = lambda lado, v: sum(1 for i in itens if i["lado"] == lado and i["v"] == v)
    # balanço da nota de checagem (seção 0.4): mesma régua para os dois lados
    # revisado após a auditoria de neutralidade (05/10/2026): promessas de Lula na mesma escala "conta que feche",
    # PLOA 2027 (governo) e Revista Oeste fora de "mercado", F13 reclassificado e duas falas novas de cada lado
    assert [conta("lula", v) for v in ("correto", "hoje_exagerado", "enganoso", "exagerado", "falso", "sem_base")] == [3, 1, 6, 5, 3, 3]
    assert [conta("flavio", v) for v in ("correto", "hoje_exagerado", "enganoso", "exagerado", "falso", "sem_base")] == [2, 0, 5, 3, 3, 4]
    assert sum(1 for i in itens if i["lado"] == "mercado") == 4
    assert not any(i["lado"] == "mercado" and ("MPO" in i["quem"] or "Oeste" in i["quem"]) for i in itens)
    assert any(i["lado"] == "lula" and i["v"] == "sem_base" and "tarifa zero" in i["afirmacao"].lower() for i in itens)
    escala = {e[0] for e in rd["checagem"]["escala"]}
    assert all(i["v"] in escala and i["fontes"] and all(f[1].startswith("https://") for f in i["fontes"]) for i in itens)
    assert all(c["fontes"] and c["tipo"] and set(c["tipo"]) <= {"a", "b", "c", "d"} for c in rd["indicadores"])
    txt = json.dumps(rd, ensure_ascii=False)
    assert "antes de publicar" not in txt and "de memória" not in txt
    # nenhuma alegação de manipulação do IBGE sem evidência: o único cartão (d) diz "sem evidência"
    d = [c for c in rd["indicadores"] if "d" in c["tipo"]]
    assert len(d) == 1 and "Sem evidência" in d[0]["gap"]
    divida = next(c for c in rd["indicadores"] if c["id"] == "divida")
    assert "28,72%" in divida["gap_det"] and "29034" in divida["gap_det"] and "29265" in divida["verif"]


def test_realidade_conta_completa():
    rd = json.loads((publicar.ORIG / "realidade.json").read_text(encoding="utf-8"))
    cc = rd["conta_completa"]
    assert {g["gov"].split()[0] for g in cc["veredito"]} == {"Lula", "Bolsonaro", "Flávio"}
    assert all(len(l) == 5 for g in cc["veredito"] for l in g["linhas"])
    assert "não má-fé" in cc["engana"]
    assert {p["gov"] for p in cc["politicas"]} == {"Lula", "Bolsonaro", "Flávio"}
    assert all(p["visivel"] and p["paga"] and p["quando"] and p["P"] and p["M"] and p["T"] for p in cc["politicas"])
    assert len(cc["divida"]["linhas"]) == 2 and cc["excecoes"]["linhas"]
    assert "meia-entrada" in cc["credito"]["titulo"] and len(cc["credito"]["blocos"]) == 5
    assert any("ICMS" in l[0] for l in cc["divergencias"]["linhas"])
    txt = json.dumps(cc, ensure_ascii=False)
    assert "~R$ 25 bi" not in txt and "26,6" in txt  # outorga da Eletrobras conferida
    assert "não reverificado" not in txt and "de memória" not in txt


def test_cada_aba_termina_com_resumo():
    """Toda seção ("assunto") de toda aba termina com um quadro Resumo, e toda aba com "Resumo da aba"."""
    import re
    html = (publicar.ORIG / "index.html").read_text(encoding="utf-8")
    paineis = re.findall(r'<div role="tabpanel"[^>]*data-painel="([^"]+)"[^>]*>([\s\S]*?)(?=\n  <div role="tabpanel"|\n  <footer)', html)
    assert len(paineis) == 9
    chaves_js = set(re.findall(r'^    "([a-z0-9-]+)": function', html, re.M))
    for nome, corpo in paineis:
        corpo = corpo.rstrip()
        assert corpo.endswith("</div>")
        ultimo = corpo[:-len("</div>")].rstrip().splitlines()[-1]
        assert f'data-resumo-aba="{nome}"' in ultimo, nome
        assert f'"{nome}": function' in html, nome
        for sec in re.findall(r"<section[\s\S]*?</section>", corpo):
            if 'id="segundo-turno"' in sec:   # seção única: cada parte (h3) tem o seu resumo
                partes = re.findall(r'data-resumo="(st-[a-z]+)"', sec)
                assert partes == ["st-hero", "st-dist", "st-virada", "st-fluxo", "st-calc", "st-bast"]
                assert all(p in chaves_js for p in partes)
                continue
            fim = sec[:-len("</section>")].rstrip().splitlines()[-1]
            m = re.search(r'<aside class="resumo" data-resumo="([^"]+)"', fim)
            assert m, (nome, sec[:80])
            assert m.group(1) in chaves_js, m.group(1)
    assert ".resumo {" in html and ".resumo.aba" in html
