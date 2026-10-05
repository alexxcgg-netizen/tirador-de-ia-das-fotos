"""Gera a cópia para publicação como artifact (web_publicar/): mesma página, sem
<!doctype>, <html>, <head>, <body> e sem as metas charset/viewport (o invólucro
as adiciona), com o cabeçalho fixo respeitando a área segura do aparelho.

Uso: python simulador/publicar.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIG = AQUI / "web"
DEST = AQUI / "web_publicar"


def converter(html: str) -> str:
    out = html
    out = re.sub(r"<!doctype html>\s*", "", out, flags=re.I)
    out = re.sub(r"<html[^>]*>\s*", "", out, flags=re.I)
    out = re.sub(r"\s*</html>\s*", "\n", out, flags=re.I)
    out = re.sub(r"<head>\s*", "", out, flags=re.I)
    out = re.sub(r"\s*</head>\s*", "\n", out, flags=re.I)
    out = re.sub(r"<body[^>]*>\s*", "", out, flags=re.I)
    out = re.sub(r"\s*</body>\s*", "\n", out, flags=re.I)
    out = re.sub(r"<meta\s+charset=[^>]*>\s*", "", out, flags=re.I)
    out = re.sub(r"<meta\s+name=\"viewport\"[^>]*>\s*", "", out, flags=re.I)
    alvo = "header.top { position: sticky; top: 0;"
    assert alvo in out, "regra do cabeçalho fixo não encontrada"
    out = out.replace(alvo, "header.top { position: sticky; top: env(safe-area-inset-top, 0px);")
    return out.strip() + "\n"


def link_cenarios(html: str, existe: bool) -> str:
    """Mostra o item de menu "Cenários econômicos" só se a página cenarios.html for publicada junto."""
    alvo = 'id="link-cenarios" href="cenarios.html" hidden'
    return html.replace(alvo, 'id="link-cenarios" href="cenarios.html"') if existe else html


VOLTAR = """<style>
.voltar-painel { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 50; display: flex; justify-content: center;
  background: var(--surface); border-bottom: 1px solid var(--line); }
.voltar-painel a { display: inline-block; max-width: 1120px; width: 100%; padding: 10px 16px; color: var(--accent);
  font: 600 0.92rem var(--font-body); text-decoration: none; }
.voltar-painel a:hover { text-decoration: underline; }
.voltar-painel a:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
</style>
<nav class="voltar-painel" aria-label="Voltar"><a href="index.html">← Voltar ao painel da eleição</a></nav>
"""


def documento_comparador(fragmento: str) -> str:
    """comparador/index.html é um fragmento (sem doctype/html/head/body); como página extra do artifact ele precisa
    do próprio esqueleto. Injeta só o link de volta ao painel; o conteúdo do comparador não muda."""
    frag = fragmento.strip()
    m = re.search(r"<title>.*?</title>", frag, flags=re.S)
    titulo = m.group(0) if m else "<title>Comparador de propostas 2026</title>"
    if m:
        frag = frag[:m.start()] + frag[m.end():]
    corte = frag.find("</style>")
    cab, corpo = (frag[:corte + len("</style>")], frag[corte + len("</style>"):]) if corte >= 0 else ("", frag)
    links = re.findall(r"\s*<link[^>]*>", corpo)
    for l in links:
        corpo = corpo.replace(l, "", 1)
    return ("<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            + titulo + "\n" + cab + "".join(links) + "\n</head>\n<body>\n" + VOLTAR + corpo.strip() + "\n</body>\n</html>\n")


VOLTAR_CENARIOS = """<nav class="voltar-painel" aria-label="Voltar" style="padding:10px 16px;font:600 0.92rem system-ui,sans-serif">\
<a href="index.html" style="color:inherit">← Voltar ao painel</a></nav>
"""


def documento_cenarios(html: str) -> str:
    """cenarios.html já é um documento completo; só injeta o link de volta ao painel, se ainda não houver um."""
    if re.search(r"""href=["'](?:\./)?index\.html(?:#[^"']*)?["']""", html):
        return html
    m = re.search(r"<body[^>]*>", html, flags=re.I)
    if not m:
        return VOLTAR_CENARIOS + html
    return html[:m.end()] + "\n" + VOLTAR_CENARIOS + html[m.end():]


def publicar_cenarios(orig: Path, dest: Path) -> bool:
    """Copia cenarios.html (com o link de volta) e cenarios.json, se existirem. Retorna se a página foi publicada."""
    pag = orig / "cenarios.html"
    if not pag.exists():
        print("ausente (pulado): cenarios.html")
        return False
    tmp = dest / "cenarios.html.tmp"
    tmp.write_text(documento_cenarios(pag.read_text(encoding="utf-8")), encoding="utf-8")
    tmp.replace(dest / "cenarios.html")
    copiar_opcional(orig / "cenarios.json", dest / "cenarios.json")
    return True


def copiar_opcional(origem: Path, destino: Path) -> bool:
    """Copia se existir; arquivo ausente ou ilegível não interrompe a publicação (o painel esconde o card).
    Escreve num temporário e renomeia, para não publicar um JSON pela metade se outro processo estiver
    regravando a origem."""
    if not origem.exists():
        print("ausente (pulado):", origem.name)
        return False
    tmp = destino.with_name(destino.name + ".tmp")
    try:
        shutil.copyfile(origem, tmp)
        tmp.replace(destino)
    except OSError as ex:
        print(f"falha ao copiar {origem.name} (pulado): {ex}")
        tmp.unlink(missing_ok=True)
        return False
    return True


def main():
    DEST.mkdir(exist_ok=True)
    html = (ORIG / "index.html").read_text(encoding="utf-8")
    publicar_cenarios(ORIG, DEST)          # "Cenários econômicos": página extra, menu só aparece se ela existir
    (DEST / "index.html").write_text(link_cenarios(converter(html), (DEST / "cenarios.html").exists()), encoding="utf-8")
    comp = AQUI.parent / "comparador" / "index.html"
    if comp.exists():                     # "Propostas dos candidatos": página extra do mesmo artifact
        doc = documento_comparador(comp.read_text(encoding="utf-8"))
        for d in (ORIG, DEST):
            (d / "comparador.html").write_text(doc, encoding="utf-8")
    else:
        print("ausente (pulado): comparador/index.html")
    shutil.copyfile(ORIG / "resultados.json", DEST / "resultados.json")
    if (ORIG / "resultados_2t.json").exists():     # 2º turno com o 1º turno apurado (resultado_1t.py)
        shutil.copyfile(ORIG / "resultados_2t.json", DEST / "resultados_2t.json")
    for nome in ("mercado_ao_vivo.json", "benchmarks.json",    # painéis "Mercado ao vivo" e "Apuração ao vivo"
                 "nordeste.json", "curiosidades.json",         # abas "Nordeste" e "Curiosidades"
                 "realidade.json"):                            # aba "Realidade × discurso"
        copiar_opcional(ORIG / nome, DEST / nome)
    alt = AQUI.parent / "modelo_alternativo" / "resultados_alt.json"
    if alt.exists():                      # comparação com o modelo alternativo (lida relativamente pelo painel)
        shutil.copyfile(alt, ORIG / "resultados_alt.json")
        shutil.copyfile(alt, DEST / "resultados_alt.json")
    # 2º turno do modelo alternativo (comparação na seção "2º turno — 25/10"; ausente = linha omitida)
    alt2 = AQUI.parent / "modelo_alternativo" / "resultados_alt_2t.json"
    if copiar_opcional(alt2, ORIG / "resultados_alt_2t.json"):
        copiar_opcional(ORIG / "resultados_alt_2t.json", DEST / "resultados_alt_2t.json")
    # modelo municipal do 2º turno (aba "Modelos e comparação"; ausente = linha omitida)
    mun = AQUI.parent / "modelo_municipal" / "resultados_municipal_2t.json"
    if copiar_opcional(mun, ORIG / "resultados_municipal_2t.json"):
        copiar_opcional(ORIG / "resultados_municipal_2t.json", DEST / "resultados_municipal_2t.json")
    print("gravado:", DEST)


if __name__ == "__main__":
    main()
