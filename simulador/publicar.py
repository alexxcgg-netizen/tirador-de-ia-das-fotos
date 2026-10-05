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


ESCOPO_CMP = "#painel-propostas"


def _prefixar_seletor(sel: str, escopo: str) -> str:
    sel = sel.strip()
    return escopo + sel[len(":scope"):] if sel.startswith(":scope") else escopo + " " + sel


def prefixar_css(css: str, escopo: str = ESCOPO_CMP) -> str:
    """Prefixa todos os seletores com o escopo (":scope" vira o próprio escopo), para o CSS do comparador não vazar
    para o resto do painel. Trata @media/@supports recursivamente; outras @-regras passam sem prefixo."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)

    def bloco(txt: str) -> str:
        out, i, n = [], 0, len(txt)
        while i < n:
            j = txt.find("{", i)
            if j < 0:
                break
            cab, depth, k = txt[i:j].strip(), 1, j + 1
            while k < n and depth:
                depth += (txt[k] == "{") - (txt[k] == "}")
                k += 1
            corpo = txt[j + 1:k - 1]
            if cab.startswith(("@media", "@supports")):
                out.append(cab + " {\n" + bloco(corpo) + "}\n")
            elif cab.startswith("@"):
                out.append(cab + " {" + corpo + "}\n")
            else:
                out.append(",\n".join(_prefixar_seletor(x, escopo) for x in cab.split(",")) + " {" + corpo + "}\n")
            i = k
        return "".join(out)

    return bloco(css)


def partes_comparador(frag: str) -> tuple[str, str, str]:
    """Separa comparador/index.html em (css, html, js): o primeiro <style>, o último <script> e o resto
    (sem <title> nem <link>, que o painel já tem)."""
    f = re.sub(r"<title>.*?</title>\s*", "", frag.strip(), flags=re.S)
    f = re.sub(r"\s*<link[^>]*>", "", f)
    m_css = re.search(r"<style>(.*?)</style>", f, flags=re.S)
    m_js = list(re.finditer(r"<script>(.*?)</script>", f, flags=re.S))
    assert m_css and m_js, "comparador/index.html precisa de <style> e <script>"
    js = m_js[-1]
    html = (f[:m_css.start()] + f[m_css.end():js.start()]).strip()
    return m_css.group(1), html, js.group(1)


def _troca(txt: str, ini: str, fim: str, novo: str) -> str:
    a, b = txt.index(ini), txt.index(fim)
    return txt[:a + len(ini)] + "\n" + novo.rstrip("\n") + "\n" + txt[b:]


def integrar_comparador(index_html: str, frag: str) -> str:
    """Injeta o comparador (CSS prefixado, painel e JS) nos marcadores CMP:* de simulador/web/index.html."""
    css, html, js = partes_comparador(frag)
    out = _troca(index_html, "/* CMP:CSS:INICIO */", "/* CMP:CSS:FIM */", prefixar_css(css))
    corpo = "\n".join(("  " + l) if l.strip() else l for l in html.split("\n"))
    out = _troca(out, "<!-- CMP:HTML:INICIO -->", "<!-- CMP:HTML:FIM -->", corpo)
    return _troca(out, "<!-- CMP:JS:INICIO -->", "<!-- CMP:JS:FIM -->", "<script>" + js.rstrip() + "\n</script>")


AVISO_COMPARADOR = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Comparar propostas mudou de lugar</title>
<style>
:root { color-scheme: light dark; --bg: #f6f5f2; --fg: #0b0b0b; --fg2: #52514e; --ac: #2b2a27; --line: #dedcd5; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #121211; --fg: #ffffff; --fg2: #c3c2b7; --ac: #e9e8e2; --line: #34332f; } }
:root[data-theme="dark"] { --bg: #121211; --fg: #ffffff; --fg2: #c3c2b7; --ac: #e9e8e2; --line: #34332f; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }
main { max-width: 560px; margin: 0 auto; padding: 48px 16px; display: grid; gap: 16px; }
h1 { font-size: 1.4rem; margin: 0; }
p { margin: 0; color: var(--fg2); }
a.btn { display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border: 1px solid var(--ac); border-radius: 6px; color: var(--ac); font-weight: 600; text-decoration: none; justify-self: start; }
a.btn:focus-visible { outline: 2px solid var(--ac); outline-offset: 2px; }
</style>
</head>
<body>
<main>
<h1>Comparar propostas mudou de lugar</h1>
<p>O comparador agora faz parte do painel da eleição, na área “Propostas e cenários”, com o mesmo visual e em 3 passos. Suas notas e pesos continuam salvos neste navegador.</p>
<a class="btn" href="index.html#propostas">Abrir Comparar propostas</a>
</main>
</body>
</html>
"""


def documento_comparador(_fragmento: str = "") -> str:
    """comparador.html virou um aviso curto com link para o painel (o comparador foi integrado como sub-aba)."""
    return AVISO_COMPARADOR


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
    comp = AQUI.parent / "comparador" / "index.html"
    if comp.exists():                     # "Comparar propostas": fonte em comparador/index.html, integrada como sub-aba do painel
        novo_html = integrar_comparador(html, comp.read_text(encoding="utf-8"))
        if novo_html != html:
            (ORIG / "index.html").write_text(novo_html, encoding="utf-8")
        html = novo_html
    else:
        print("ausente (pulado): comparador/index.html")
    publicar_cenarios(ORIG, DEST)          # "Cenários econômicos": página extra, o botão só aparece se ela existir
    (DEST / "index.html").write_text(link_cenarios(converter(html), (DEST / "cenarios.html").exists()), encoding="utf-8")
    for d in (ORIG, DEST):                 # comparador.html (endereço antigo): aviso curto com link para o painel
        (d / "comparador.html").write_text(documento_comparador(), encoding="utf-8")
    shutil.copyfile(ORIG / "resultados.json", DEST / "resultados.json")
    if (ORIG / "resultados_2t.json").exists():     # 2º turno com o 1º turno apurado (resultado_1t.py)
        shutil.copyfile(ORIG / "resultados_2t.json", DEST / "resultados_2t.json")
    for nome in ("mercado_ao_vivo.json", "benchmarks.json",    # painéis "Mercado ao vivo" e "Apuração ao vivo"
                 "nordeste.json", "curiosidades.json",         # abas "Nordeste" e "Curiosidades"
                 "realidade.json",                             # aba "Realidade × discurso"
                 "indireto.json",                              # sub-aba "Indireto" (gerado por outro processo; ausente = "dados em preparação")
                 "nordeste_trajetoria.json",                   # seção "Trajetória por governo" da aba Nordeste (idem)
                 "glossario.json"):                            # "Glossário e regras"
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
