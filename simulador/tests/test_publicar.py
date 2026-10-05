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
