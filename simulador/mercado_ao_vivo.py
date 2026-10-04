"""Rastreador ao vivo dos mercados de previsão (Polymarket + Kalshi) na apuração do 1º turno.

Uma chamada:
  1. busca os preços atuais (Polymarket Gamma; Kalshi trade-api v2);
  2. acrescenta uma linha por resultado em data/mercado_ao_vivo.csv;
  3. (re)baixa o histórico do CLOB da Polymarket desde --desde (padrão 2026-10-04 12:00 UTC),
     fidelidade de 1 min nos mercados-chave e 5 min nos demais, com cache em disco;
  4. escreve web/mercado_ao_vivo.json com o retrato mais recente + as séries.

Uso:
  python simulador/mercado_ao_vivo.py              # uma coleta
  python simulador/mercado_ao_vivo.py --loop 60    # repete a cada 60 s (Ctrl+C para parar)
  python simulador/mercado_ao_vivo.py --sem-historico   # não consulta o CLOB

Convenções (mesmas de research_notes/.../mercados_de_previsao.md):
  preco       = meio do bid/ask quando o spread <= 0,10; senão último negócio; senão outcomePrice.
  normalizado = preco / soma dos precos do evento (apenas em eventos mutuamente exclusivos).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CSV_PADRAO = AQUI / "data" / "mercado_ao_vivo.csv"
JSON_PADRAO = AQUI / "web" / "mercado_ao_vivo.json"
CACHE_CLOB = AQUI / "data" / "mercado_ao_vivo_clob_cache.json"
DESDE_PADRAO = "2026-10-04T12:00:00Z"

GAMMA = "https://gamma-api.polymarket.com/events"
CLOB_HIST = "https://clob.polymarket.com/prices-history"
KALSHI = "https://api.elections.kalshi.com/trade-api/v2/markets"

# (chave, slug, rótulo, mutuamente_exclusivo, chave_para_historico_1min)
POLY_EVENTOS = [
    ("vencedor", "brazil-presidential-election", "Vencedor da eleição", True, True),
    ("vencedor_1t", "brazil-presidential-election-first-round-winner", "1º colocado no 1º turno", True, True),
    ("decide_1t", "will-any-presidential-candidate-win-outright-in-the-first-round-of-the-brazil-election",
     "Alguém vence no 1º turno", False, True),
    ("margem_1t", "brazil-presidential-election-first-round-margin-of-victory", "Margem no 1º turno", True, True),
    ("segundo_1t", "brazil-presidential-election-first-round-2nd-place", "2º colocado no 1º turno", True, False),
    ("vai_2t", "which-candidates-will-advance-to-brazils-presidential-runoff", "Vai ao 2º turno", False, False),
]
UFS_POLY = [
    ("SP", "sao-paulo"), ("MG", "minas-gerais"), ("RJ", "rio-de-janeiro"), ("BA", "bahia"),
    ("PR", "parana"), ("RS", "rio-grande-do-sul"), ("GO", "goias"), ("DF", "federal-district"),
    ("PE", "pernambuco"), ("CE", "ceara"), ("PA", "para"), ("AM", "amazonas"),
    ("SC", "santa-catarina"), ("ES", "espirito-santo"),
]
for _uf, _s in UFS_POLY:
    POLY_EVENTOS.append((f"uf_{_uf}", f"brazil-presidential-election-first-round-1st-place-in-{_s}",
                         f"1º colocado no 1º turno em {_uf}", True, False))

# (chave, série, rótulo, mutuamente_exclusivo)
KALSHI_SERIES = [
    ("vencedor", "KXBRPRES", "Vencedor da eleição", True),
    ("vencedor_1t", "KXBRPRES1R", "1º colocado no 1º turno", True),
    ("decide_1t", "KXBRAZILPRES1R", "Alguém vence no 1º turno", False),
    ("margem_1t", "KXBRPRES1MOV", "Margem no 1º turno", True),
    ("segundo_1t", "KXBRPRESIDENT2", "2º colocado no 1º turno", True),
    ("vai_2t", "KXBRPRESADVANCE", "Vai ao 2º turno", False),
]

CAMPOS = ["ts_utc", "plataforma", "evento", "evento_rotulo", "mercado_id", "resultado",
          "preco", "normalizado", "bid", "ask", "ultimo", "volume", "volume_24h", "liquidez", "status"]

MAX_PARALELO = 8
LIMIAR_SERIE = 0.02  # só guarda série/histórico de resultados com preço >= 2%
LIMIAR_CSV = 0.005  # o CSV omite resultados abaixo de 0,5% (a normalização usa todos)


# --------------------------------------------------------------------------- HTTP
def http_get_json(url: str, params: dict | None = None, tentativas: int = 3):
    import requests  # import tardio: os testes injetam um fake

    for i in range(tentativas):
        try:
            r = requests.get(url, params=params, timeout=20, headers={"User-Agent": "simulador-eleicao/1.0"})
            if r.status_code == 429:
                time.sleep(1.5 * (i + 1))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as ex:  # noqa: BLE001
            if i == tentativas - 1:
                raise
            print(f"  aviso: {url} falhou ({ex}); tentando de novo", file=sys.stderr)
            time.sleep(1.0 * (i + 1))
    raise RuntimeError(f"sem resposta de {url}")


# --------------------------------------------------------------------------- utilidades
def _f(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def preco_justo(bid, ask, ultimo, fallback=None):
    """Meio do bid/ask se o spread for apertado; senão último negócio; senão fallback."""
    if bid is not None and ask is not None and ask > 0 and ask >= bid and (ask - bid) <= 0.10:
        return round((bid + ask) / 2, 4)
    if ultimo is not None and ultimo > 0:
        return round(ultimo, 4)
    if fallback is not None:
        return round(fallback, 4)
    return None


def normalizar(linhas: list[dict], exclusivo: bool):
    soma = sum(l["preco"] for l in linhas if l["preco"])
    for l in linhas:
        if l["preco"] is None:
            l["normalizado"] = None
        elif exclusivo and soma > 0:
            l["normalizado"] = round(l["preco"] / soma, 4)
        else:
            l["normalizado"] = l["preco"]
    return soma


def iso(ts: float | datetime) -> str:
    if isinstance(ts, (int, float)):
        ts = datetime.fromtimestamp(ts, tz=timezone.utc)
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# --------------------------------------------------------------------------- Polymarket
def _paralelo(fn, itens):
    with ThreadPoolExecutor(max_workers=MAX_PARALELO) as ex:
        return list(ex.map(fn, itens))


def _tentar(get, url, params, rotulo):
    try:
        return get(url, params)
    except Exception as ex:  # noqa: BLE001
        print(f"  {rotulo}: falhou ({ex})", file=sys.stderr)
        return None


def coletar_polymarket(get, ts: str):
    linhas, tokens = [], {}
    respostas = _paralelo(lambda e: _tentar(get, GAMMA, {"slug": e[1]}, f"Polymarket {e[1]}"), POLY_EVENTOS)
    for (chave, slug, rotulo, excl, chave_1min), dados in zip(POLY_EVENTOS, respostas):
        if not dados:
            continue
        ev = dados[0]
        grupo = []
        for m in ev.get("markets", []):
            if not m.get("active", True) and not m.get("closed"):
                continue  # placeholder negRisk ("Person O", "Candidate A"): sem livro
            try:
                outp = json.loads(m.get("outcomePrices") or "[]")
            except (TypeError, ValueError):
                outp = []
            fallback = _f(outp[0]) if outp else None
            bid, ask, ult = _f(m.get("bestBid")), _f(m.get("bestAsk")), _f(m.get("lastTradePrice"))
            p = preco_justo(bid, ask, ult, fallback)
            if m.get("closed") and fallback is not None:
                p = fallback  # mercado resolvido: outcomePrice é o resultado
            nome = m.get("groupItemTitle") or m.get("question") or "?"
            if not excl and len(ev.get("markets", [])) == 1:
                nome = "Sim"
            status = "fechado" if m.get("closed") else ("ativo" if m.get("active", True) else "inativo")
            grupo.append({
                "ts_utc": ts, "plataforma": "Polymarket", "evento": chave, "evento_rotulo": rotulo,
                "mercado_id": m.get("conditionId") or m.get("slug"), "resultado": nome,
                "preco": p, "normalizado": None, "bid": bid, "ask": ask, "ultimo": ult,
                "volume": _f(m.get("volume")), "volume_24h": _f(m.get("volume24hr")),
                "liquidez": _f(m.get("liquidity")), "status": status,
            })
            try:
                tok = json.loads(m.get("clobTokenIds") or "[]")
            except (TypeError, ValueError):
                tok = []
            if tok:
                tokens[serie_id("Polymarket", chave, nome)] = (tok[0], 1 if chave_1min else 5)
        grupo = [g for g in grupo if g["preco"] is not None]
        normalizar(grupo, excl)
        linhas.extend(grupo)
    return linhas, tokens


def backfill_clob(get, tokens: dict, linhas_atuais: list[dict], desde: datetime, cache: dict | None = None):
    """Histórico do CLOB (preço do SIM) desde `desde`, para resultados relevantes."""
    cache = dict(cache or {})
    relevantes = {serie_id(l["plataforma"], l["evento"], l["resultado"])
                  for l in linhas_atuais if l["plataforma"] == "Polymarket" and (l["preco"] or 0) >= LIMIAR_SERIE}
    start = int(desde.timestamp())
    alvo = sorted((sid, tf) for sid, tf in tokens.items() if sid in relevantes)
    resps = _paralelo(lambda it: _tentar(get, CLOB_HIST, {"market": it[1][0], "startTs": start,
                                                           "fidelity": it[1][1]}, f"CLOB {it[0]}"), alvo)
    for (sid, (tok, fid)), h in zip(alvo, resps):
        if not h:
            continue
        pts = [[int(x["t"]), round(float(x["p"]), 4)] for x in h.get("history", []) if int(x["t"]) >= start]
        cache[sid] = {"fidelidade_min": fid, "pontos": pts}
    return cache


# --------------------------------------------------------------------------- Kalshi
def coletar_kalshi(get, ts: str):
    linhas = []
    for chave, serie, rotulo, excl in KALSHI_SERIES:  # sequencial: a Kalshi limita a taxa
        dados = _tentar(get, KALSHI, {"series_ticker": serie, "limit": 200}, f"Kalshi {serie}")
        if not dados:
            continue
        ms = [m for m in dados.get("markets", []) if m.get("status") not in ("finalized", "settled")] \
            or dados.get("markets", [])
        # se a série tiver vários eventos, fica com o mais recente
        evs = sorted({m.get("event_ticker") for m in ms})
        if len(evs) > 1:
            ms = [m for m in ms if m.get("event_ticker") == evs[-1]]
        grupo = []
        for m in ms:
            bid, ask = _f(m.get("yes_bid_dollars")), _f(m.get("yes_ask_dollars"))
            ult = _f(m.get("last_price_dollars"))
            p = preco_justo(bid, ask, ult)
            if m.get("result") in ("yes", "no"):
                p = 1.0 if m["result"] == "yes" else 0.0
            if p is None:
                continue
            grupo.append({
                "ts_utc": ts, "plataforma": "Kalshi", "evento": chave, "evento_rotulo": rotulo,
                "mercado_id": m.get("ticker"), "resultado": m.get("yes_sub_title") or m.get("ticker"),
                "preco": p, "normalizado": None, "bid": bid, "ask": ask, "ultimo": ult,
                "volume": _f(m.get("volume_fp")), "volume_24h": _f(m.get("volume_24h_fp")),
                "liquidez": _f(m.get("open_interest_fp")), "status": m.get("status"),
            })
        normalizar(grupo, excl)
        linhas.extend(grupo)
    return linhas


# --------------------------------------------------------------------------- saída
def serie_id(plataforma, evento, resultado):
    return f"{plataforma}|{evento}|{resultado}"


def anexar_csv(linhas: list[dict], caminho: Path):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    novo = not caminho.exists() or caminho.stat().st_size == 0
    with caminho.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS, extrasaction="ignore")
        if novo:
            w.writeheader()
        for l in linhas:
            if (l.get("preco") or 0) < LIMIAR_CSV and l.get("status") not in ("fechado", "finalized", "settled"):
                continue
            w.writerow({k: ("" if l.get(k) is None else l.get(k)) for k in CAMPOS})


def ler_csv(caminho: Path, desde: datetime):
    if not caminho.exists():
        return []
    out = []
    with caminho.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                if parse_iso(r["ts_utc"]) < desde:
                    continue
            except (KeyError, ValueError):
                continue
            out.append(r)
    return out


def montar_series(csv_rows: list[dict], clob: dict, desde: datetime):
    """{serie_id: [[epoch_s, preco], ...]} combinando CLOB (Polymarket) e as coletas do CSV.

    Para Polymarket, o CLOB é a base; pontos do CSV posteriores ao último ponto do CLOB são acrescentados.
    """
    series: dict[str, list] = {}
    t0 = desde.timestamp()
    for sid, d in clob.items():
        series[sid] = [p for p in d.get("pontos", []) if p[0] >= t0]
    ultimos_csv: dict[str, list] = {}
    for r in csv_rows:
        p = _f(r.get("preco"))
        if p is None:
            continue
        sid = serie_id(r["plataforma"], r["evento"], r["resultado"])
        ultimos_csv.setdefault(sid, []).append([int(parse_iso(r["ts_utc"]).timestamp()), p])
    for sid, pts in ultimos_csv.items():
        if max(x[1] for x in pts) < LIMIAR_SERIE and sid not in series:
            continue
        base = series.setdefault(sid, [])
        corte = base[-1][0] if base else 0
        base.extend(x for x in pts if x[0] > corte)
    for sid in series:
        # ordena, remove duplicatas de timestamp e reduz a no máximo 1 ponto/minuto
        dedup: dict[int, float] = {}
        for t, p in sorted(series[sid]):
            dedup[t // 60 * 60] = p
        series[sid] = [[t, p] for t, p in sorted(dedup.items())]
    return series


def resumo(linhas: list[dict]):
    """Estrutura do retrato mais recente, agrupada por plataforma/evento e ordenada por preço."""
    grupos: dict[tuple, dict] = {}
    for l in linhas:
        k = (l["plataforma"], l["evento"])
        g = grupos.setdefault(k, {"plataforma": l["plataforma"], "evento": l["evento"],
                                  "rotulo": l["evento_rotulo"], "resultados": []})
        g["resultados"].append({kk: l[kk] for kk in
                                ("resultado", "preco", "normalizado", "bid", "ask", "ultimo",
                                 "volume", "volume_24h", "liquidez", "status", "mercado_id")})
    for g in grupos.values():
        g["resultados"].sort(key=lambda r: -(r["preco"] or 0))
        g["soma_precos"] = round(sum(r["preco"] or 0 for r in g["resultados"]), 4)
    return list(grupos.values())


def destaques(linhas: list[dict]):
    """Números de manchete para o painel (normalizados)."""
    def achar(plat, ev, termo):
        for l in linhas:
            if l["plataforma"] == plat and l["evento"] == ev and termo.lower() in l["resultado"].lower():
                return l["normalizado"]
        return None

    d = {}
    for plat in ("Polymarket", "Kalshi"):
        d[plat] = {
            "vencedor_lula": achar(plat, "vencedor", "Lula"),
            "vencedor_flavio": achar(plat, "vencedor", "Flávio") or achar(plat, "vencedor", "Flavio"),
            "1t_lula_primeiro": achar(plat, "vencedor_1t", "Lula"),
            "1t_flavio_primeiro": achar(plat, "vencedor_1t", "Flávio") or achar(plat, "vencedor_1t", "Flavio"),
            "decide_no_1t": next((l["preco"] for l in linhas if l["plataforma"] == plat
                                  and l["evento"] == "decide_1t"), None),
        }
    return d


def escrever_json(caminho: Path, ts: str, linhas: list[dict], series: dict, desde: datetime):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    meta = {}
    for l in linhas:
        meta[serie_id(l["plataforma"], l["evento"], l["resultado"])] = {
            "plataforma": l["plataforma"], "evento": l["evento"], "rotulo": l["evento_rotulo"],
            "resultado": l["resultado"]}
    doc = {
        "gerado_utc": ts,
        "desde_utc": iso(desde),
        "convencoes": {
            "preco": "meio do bid/ask se spread<=0,10; senão último negócio; senão outcomePrice (US$ por contrato de US$ 1)",
            "normalizado": "preco / soma do evento (só eventos mutuamente exclusivos)",
            "series": "[epoch_s, preco do SIM] — 1 ponto/min no máximo; Polymarket = CLOB prices-history + coletas",
        },
        "destaques": destaques(linhas),
        "ultimo": resumo(linhas),
        "series_meta": {k: meta.get(k, dict(zip(("plataforma", "evento", "resultado"), k.split("|"))))
                        for k in series},
        "series": series,
    }
    tmp = caminho.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, caminho)
    return doc


# --------------------------------------------------------------------------- orquestração
def coletar_uma_vez(get=http_get_json, csv_path=CSV_PADRAO, json_path=JSON_PADRAO, cache_path=CACHE_CLOB,
                    desde=DESDE_PADRAO, historico=True, agora=None, idade_max_cache=240):
    desde_dt = parse_iso(desde) if isinstance(desde, str) else desde
    agora = agora or datetime.now(timezone.utc)
    ts = iso(agora)
    poly, tokens = coletar_polymarket(get, ts)
    kal = coletar_kalshi(get, ts)
    linhas = poly + kal
    anexar_csv(linhas, Path(csv_path))

    cache = {}
    cache_path = Path(cache_path) if cache_path else None
    if cache_path and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
    if historico:
        idade = agora.timestamp() - cache.get("_atualizado", 0)
        if idade >= idade_max_cache or cache.get("_desde") != iso(desde_dt):
            novo = backfill_clob(get, tokens, linhas, desde_dt,
                                 {k: v for k, v in cache.items() if not k.startswith("_")})
            cache = {"_atualizado": agora.timestamp(), "_desde": iso(desde_dt), **novo}
            if cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(cache), encoding="utf-8")
    clob = {k: v for k, v in cache.items() if not k.startswith("_")}
    series = montar_series(ler_csv(Path(csv_path), desde_dt), clob, desde_dt)
    doc = escrever_json(Path(json_path), ts, linhas, series, desde_dt)
    return doc


def imprimir(doc):
    print(f"Coleta {doc['gerado_utc']}  ({sum(len(g['resultados']) for g in doc['ultimo'])} resultados, "
          f"{len(doc['series'])} séries)")
    for g in doc["ultimo"]:
        if g["evento"].startswith("uf_"):
            continue
        top = ", ".join(f"{r['resultado']} {100 * (r['normalizado'] or 0):.1f}%"
                        for r in g["resultados"][:4] if (r["preco"] or 0) >= 0.01)
        print(f"  {g['plataforma']:10s} {g['rotulo']:28s} {top}")
    ufs = [g for g in doc["ultimo"] if g["evento"].startswith("uf_")]
    if ufs:
        print("  Polymarket UFs: " + "; ".join(
            f"{g['evento'][3:]} {g['resultados'][0]['resultado'].split()[0]} {100 * (g['resultados'][0]['normalizado'] or 0):.0f}%"
            for g in ufs if g["resultados"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--loop", type=float, default=0, help="repete a cada N segundos (0 = uma vez)")
    ap.add_argument("--csv", default=str(CSV_PADRAO))
    ap.add_argument("--json", default=str(JSON_PADRAO))
    ap.add_argument("--desde", default=DESDE_PADRAO, help="início das séries (UTC ISO)")
    ap.add_argument("--sem-historico", action="store_true", help="não baixa o histórico do CLOB")
    ap.add_argument("--historico-a-cada", type=float, default=240,
                    help="segundos entre re-downloads do histórico do CLOB (padrão 240)")
    a = ap.parse_args(argv)
    while True:
        t = time.time()
        try:
            doc = coletar_uma_vez(csv_path=a.csv, json_path=a.json, desde=a.desde,
                                  historico=not a.sem_historico, idade_max_cache=a.historico_a_cada)
            imprimir(doc)
        except Exception as ex:  # noqa: BLE001
            print(f"coleta falhou: {ex}", file=sys.stderr)
            if not a.loop:
                raise
        if not a.loop:
            break
        time.sleep(max(1.0, a.loop - (time.time() - t)))


if __name__ == "__main__":
    main()
