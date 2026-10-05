"""Baixa o 1º turno 2026 (Presidente) por município dos arquivos do TSE e grava um CSV compacto.

Reaproveita o cache local (JSONs brutos em RAW_DIR e os arquivos por UF em simulador/data/tse_1t_2026/), baixa só
o que falta, com no máximo 8 conexões simultâneas e retentativas com backoff exponencial (o TSE responde 429).

Saída: modelo_municipal/data/mun_2026_1t.csv
  cd_municipio_tse, uf, aptos, comparecimento, brancos, nulos, validos, lula, flavio, outros_<n>..., terceiros
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
CACHE_SIMULADOR = RAIZ / "simulador" / "data" / "tse_1t_2026"
RAW_DIR = Path(os.environ.get("RAW_2026", AQUI / "data" / "_raw_2026"))  # não versionado
SAIDA = AQUI / "data" / "mun_2026_1t.csv"
BASE = "https://resultados.tse.jus.br/oficial/ele2026/6257/dados"
UFS = ("ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to zz").split()
LULA, FLAVIO = "13", "22"
WORKERS = 8


def _num(x) -> float:
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return float("nan")


def baixar(url: str, destino: Path, tentativas: int = 8) -> dict | None:
    if destino.exists() and destino.stat().st_size > 100:
        try:
            return json.loads(destino.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    espera = 1.0
    for _ in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "modelo-municipal/1.0 (pesquisa)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                corpo = r.read()
            js = json.loads(corpo)
            destino.write_bytes(corpo)
            return js
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                ra = e.headers.get("Retry-After")
                espera = max(espera, float(ra) if ra and ra.isdigit() else espera)
        except Exception:  # timeouts / TLS / JSON truncado
            pass
        time.sleep(espera + random.random())
        espera = min(espera * 2, 60)
    return None


def parse_u(js: dict) -> dict:
    """Arquivo 'u' (município): votos por candidato, brancos, nulos, comparecimento, eleitorado."""
    e, v = js.get("e", {}), js.get("v", {})
    out = {"aptos": _num(e.get("te")), "comparecimento": _num(e.get("c")), "abstencao": _num(e.get("a")),
           "validos": _num(v.get("vv")), "brancos": _num(v.get("vb")), "nulos": _num(v.get("tvn")),
           "pst": _num(js.get("s", {}).get("pst"))}
    cands = {}
    for c in js.get("carg", []):
        for a in c.get("agr", []):
            for p in a.get("par", []):
                for k in p.get("cand", []):
                    cands[str(k["n"])] = _num(k.get("vap"))
    out["lula"] = cands.get(LULA, 0.0)
    out["flavio"] = cands.get(FLAVIO, 0.0)
    for n, x in cands.items():
        out[f"c{n}"] = x
    return out


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    tarefas = []
    for uf in UFS:
        ab = baixar(f"{BASE}/{uf}/{uf}-e006257-ab.json", RAW_DIR / f"{uf}-ab.json")
        if ab is None:
            print("sem abrangência", uf, file=sys.stderr)
            continue
        for a in ab.get("abr", []):
            if str(a.get("tpabr", "")).lower() in ("mun", "mu"):
                cd = int(a["cdabr"])
                tarefas.append((uf, cd))
    print(f"{len(tarefas)} municípios", file=sys.stderr)
    linhas, falhas = [], []
    with ThreadPoolExecutor(WORKERS) as ex:
        fut = {ex.submit(baixar, f"{BASE}/{uf}/{uf}{cd:05d}-c0001-e006257-u.json", RAW_DIR / f"{uf}{cd:05d}.json"): (uf, cd)
               for uf, cd in tarefas}
        for i, f in enumerate(as_completed(fut)):
            uf, cd = fut[f]
            js = f.result()
            if js is None:
                falhas.append((uf, cd))
                continue
            linhas.append({"cd_municipio_tse": cd, "uf": uf.upper(), **parse_u(js)})
            if i % 500 == 0:
                print(i, file=sys.stderr)
    df = pd.DataFrame(linhas).fillna(0.0)
    cand_cols = [c for c in df.columns if c.startswith("c") and c[1:].isdigit()]
    df["terceiros"] = df[cand_cols].sum(axis=1) - df["lula"] - df["flavio"]
    df = df.sort_values(["uf", "cd_municipio_tse"])
    df.to_csv(SAIDA, index=False)
    print(f"ok {len(df)} municípios; falhas: {falhas}", file=sys.stderr)
    if falhas:
        sys.exit(2)


if __name__ == "__main__":
    main()
