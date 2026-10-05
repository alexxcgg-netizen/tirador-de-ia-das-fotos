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
