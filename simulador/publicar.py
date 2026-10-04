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
    (DEST / "index.html").write_text(converter(html), encoding="utf-8")
    shutil.copyfile(ORIG / "resultados.json", DEST / "resultados.json")
    if (ORIG / "resultados_2t.json").exists():     # 2º turno com o 1º turno apurado (resultado_1t.py)
        shutil.copyfile(ORIG / "resultados_2t.json", DEST / "resultados_2t.json")
    for nome in ("mercado_ao_vivo.json", "benchmarks.json"):   # painéis "Mercado ao vivo" e "Apuração ao vivo"
        copiar_opcional(ORIG / nome, DEST / nome)
    alt = AQUI.parent / "modelo_alternativo" / "resultados_alt.json"
    if alt.exists():                      # comparação com o modelo alternativo (lida relativamente pelo painel)
        shutil.copyfile(alt, ORIG / "resultados_alt.json")
        shutil.copyfile(alt, DEST / "resultados_alt.json")
    print("gravado:", DEST)


if __name__ == "__main__":
    main()
