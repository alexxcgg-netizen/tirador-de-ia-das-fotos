"""Fonte alternativa de apuração (presidente, 1º turno): g1 / Globo, independente do TSE.

Uso na noite da apuração (TSE fora do ar, lento ou com 403/429):

    python simulador/fonte_alternativa.py                      # grava data/resultado_1t_manual.csv
    python simulador/fonte_alternativa.py --intervalo 60       # idem, de minuto em minuto (Ctrl+C para parar)
    python simulador/resultado_1t.py --rodar-tudo --fonte manual
    python simulador/fonte_alternativa.py --comparar           # TSE x g1, por UF (não grava o CSV)
    python simulador/fonte_alternativa.py --ano 2022 --saida /tmp/r22.csv   # ensaio com 2022 (arquivo do g1)

Fontes (JSON públicos que alimentam as páginas de apuração do g1, CDN da Globo, cache de 10 s):

* Brasil (presidente): ``https://s.glbimg.com/jo/el/{ano}/apuracao/1-turno/br/executivo.json``
  (abrangencia: andamento = % de seções totalizadas, eleitores, eleitoradoApurado, votos.{abstencao, brancos,
  nulos, validos}.quantidade, comparecimento; candidatos[].numero / votos.quantidade / destinacaoDosVotos).
* UFs (presidente por UF), 2026: ``.../{ano}/apuracao/1-turno/br/PRESIDENTE_CONSOLIDADO.JSON``
  (presidente_consolidado.regiao[].estado[]: qtd_urnas = % de urnas apuradas, comp_abs, abst_abs,
  votos_{validos,brancos,nulos}_abs, candidato[].numero / votos_cand_abs / processo). Usado pelo mapa de apuração
  do g1 de 2026. Não traz eleitorado: vem de ``.../{uf}/executivo.json`` (página de governador da UF; o
  eleitorado é o mesmo, a menos de poucos milhares de eleitores).
* UFs, formato de 2022 (infográfico do g1, ainda publicado):
  ``https://s3.glbimg.com/v1/AUTH_fa32656b5fa140c0b66ae29bf6742b13/infografico-g1/{ano}/1-turno/PRESIDENTE_{UF}.JSON``
  (inclui ZZ = exterior). Em 2026 ainda devolve 404 antes da apuração; é tentado se o consolidado falhar.
* Exterior (ZZ) em 2026: o consolidado não tem ZZ, então ZZ = Brasil − soma das 27 UFs (votos, abstenção,
  brancos, nulos, eleitorado); % apurado = eleitorado apurado / eleitorado. Como os dois arquivos podem estar
  em momentos diferentes da apuração, a diferença é aproximada; se der negativa, ZZ sai com pst = 0 (o
  resultado_1t.py usa a previsão de véspera para o exterior).

O ``executivo.json`` de cada UF é de GOVERNADOR (não usar os votos dele para presidente).
UOL, Poder360, CNN e o espelho de simulação do TSE respondem 403 (Akamai) a partir deste ambiente.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
MANUAL_CSV = DADOS / "resultado_1t_manual.csv"

G1_HOST = "https://s.glbimg.com/jo/el"
G1_INFOGRAFICO = "https://s3.glbimg.com/v1/AUTH_fa32656b5fa140c0b66ae29bf6742b13/infografico-g1"
TSE_HOST = "https://resultados.tse.jus.br"
TSE_ELEICAO = {2026: ("ele2026", "6257"), 2022: ("ele2022", "544")}

UFS27 = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
         "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
UFS = UFS27 + ["ZZ"]
# número na urna -> coluna do CSV (demais -> "outros"); mesmos números do resultado_1t.py
NUMEROS = {
    2026: {"13": "lula", "22": "flavio", "55": "caiado", "70": "cury", "30": "zema", "14": "renan"},
    2022: {"13": "lula", "22": "bolsonaro", "12": "ciro", "15": "tebet"},
}
CAND_COLS = {2026: ["lula", "flavio", "caiado", "cury", "zema", "renan", "outros"],
             2022: ["lula", "bolsonaro", "ciro", "tebet", "outros"]}
BASE_COLS = ["uf", "pst", "eleitorado", "comparecimento", "abstencao", "validos", "brancos", "nulos"]
CAMPOS_NUM = ["eleitorado", "comparecimento", "abstencao", "validos", "brancos", "nulos"]


# ------------------------------------------------------------------ util
def num(x) -> float:
    """'1.234.567' / '48,43' / '48,43%' / '0.00' / 123 -> float (nan se vazio)."""
    if x is None:
        return float("nan")
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().rstrip("%").strip()
    if not s:
        return float("nan")
    if "," in s:                       # formato brasileiro: ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3 and len(s.split(".")[0]) <= 3
                              and not s.startswith("0")):
        s = s.replace(".", "")          # '390.750' = milhar
    try:
        return float(s)
    except ValueError:
        return float("nan")


def baixar_json(url: str, timeout: float = 20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (simulador-eleicao-2026)",
                                               "Accept": "application/json", "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8-sig"))


def _agrega_cands(cands: list, ano: int) -> dict:
    """[(numero, votos, valido?)] -> {coluna: votos}; só votos válidos (fora anulados/sub judice)."""
    mapa = NUMEROS[ano]
    out = {c: 0.0 for c in CAND_COLS[ano]}
    for n, v, ok in cands:
        if not ok:
            continue
        col = mapa.get(str(n).lstrip("0") or "0", "outros")
        out[col] += 0.0 if math.isnan(v) else v
    return out


def _valido(s) -> bool:
    s = str(s or "").strip().lower()
    return s == "" or s.startswith("v")


# ------------------------------------------------------------------ parsers
def parse_g1_executivo(js: dict, ano: int) -> dict:
    """``{uf|br}/executivo.json`` do g1. Para 'br' é presidente; para UFs é governador (só eleitorado/seções)."""
    a = js["abrangencia"]
    v = a.get("votos", {})
    q = lambda k: num((v.get(k) or {}).get("quantidade")) if isinstance(v.get(k), dict) else num(v.get(k))  # noqa: E731
    cands = [(c.get("numero"), num((c.get("votos") or {}).get("quantidade")), _valido(c.get("destinacaoDosVotos")))
             for c in js.get("candidatos", [])]
    votos = _agrega_cands(cands, ano)
    comp = num(v.get("comparecimento"))
    validos = q("validos")
    if not (validos > 0):
        validos = sum(votos.values())
    return {"pst": num(a.get("andamento")), "eleitorado": num(a.get("eleitores")),
            "eleitorado_apurado": num(a.get("eleitoradoApurado")), "secoes": num(a.get("secoes")),
            "secoes_totalizadas": num(a.get("secoesTotalizadas")),
            "comparecimento": comp, "abstencao": q("abstencao"), "validos": validos,
            "brancos": q("brancos"), "nulos": q("nulos"), "votos": votos,
            "atualizado": js.get("dataHora", "")}


def parse_g1_consolidado(js: dict, ano: int) -> dict:
    """``br/PRESIDENTE_CONSOLIDADO.JSON`` (2026) -> {UF: registro} (sem eleitorado)."""
    p = js["presidente_consolidado"]
    out = {}
    for reg in p.get("regiao", []):
        for e in reg.get("estado", []):
            uf = str(e.get("uf", "")).upper()
            cands = [(c.get("numero"), num(c.get("votos_cand_abs")), _valido(c.get("processo")))
                     for c in e.get("candidato", [])]
            votos = _agrega_cands(cands, ano)
            validos = num(e.get("votos_validos_abs"))
            if not (validos > 0):
                validos = sum(votos.values())
            out[uf] = {"pst": num(e.get("qtd_urnas")), "eleitorado": float("nan"),
                       "comparecimento": num(e.get("comp_abs")), "abstencao": num(e.get("abst_abs")),
                       "validos": validos, "brancos": num(e.get("votos_brancos_abs")),
                       "nulos": num(e.get("votos_nulos_abs")), "votos": votos,
                       "atualizado": f"{e.get('data', '')} {e.get('hora', '')}".strip(), "status": e.get("status", "")}
    return out


def parse_g1_infografico(js: dict, ano: int) -> dict:
    """``infografico-g1/{ano}/1-turno/PRESIDENTE_{UF}.JSON`` (formato 2022)."""
    at, t = js.get("atualizacao", {}), js["total"]
    cands = [(c.get("id_candidato"), num(c.get("total_votos_validos")), True) for c in t.get("candidatos", [])]
    votos = _agrega_cands(cands, ano)
    comp, abst, pst = num(t.get("total")), num(t.get("abstencao")), num(at.get("apuracao_total"))
    # eleitorado só é conhecido com a UF totalizada (comparecimento + abstenção); antes disso o buscar_g1 completa
    ele = comp + abst if comp >= 0 and abst >= 0 and pst >= 99.995 else float("nan")
    return {"pst": pst, "eleitorado": ele,
            "comparecimento": comp, "abstencao": abst, "validos": sum(votos.values()),
            "brancos": num(t.get("brancos")), "nulos": num(t.get("nulos")), "votos": votos,
            "atualizado": f"{at.get('data', '')} {at.get('hora', '')}".strip()}


def derivar_exterior(br: dict, ufs: dict, ano: int) -> dict:
    """ZZ = Brasil − Σ 27 UFs. pst = eleitorado apurado do exterior / eleitorado do exterior."""
    cols = CAND_COLS[ano]
    falt = [u for u in UFS27 if u not in ufs]
    if falt:
        raise ValueError(f"faltam UFs para derivar o exterior: {falt}")
    d = {k: br[k] - sum(ufs[u][k] for u in UFS27) for k in ["comparecimento", "abstencao", "validos", "brancos", "nulos"]}
    d["votos"] = {c: br["votos"][c] - sum(ufs[u]["votos"][c] for u in UFS27) for c in cols}
    ele_ufs = sum(ufs[u]["eleitorado"] for u in UFS27)
    d["eleitorado"] = br["eleitorado"] - ele_ufs if math.isfinite(ele_ufs) else float("nan")
    apur = d["comparecimento"] + d["abstencao"]
    ok = all(math.isfinite(x) and x >= 0 for x in [d["comparecimento"], d["abstencao"], d["validos"], d["brancos"],
                                                     d["nulos"], *d["votos"].values()])
    if ok and apur > 0 and d["eleitorado"] > 0:
        d["pst"] = min(100.0, 100.0 * apur / d["eleitorado"])
    else:                                            # inconsistente (arquivos em momentos diferentes) -> sem exterior
        d = {k: 0.0 for k in ["comparecimento", "abstencao", "validos", "brancos", "nulos"]}
        d["votos"] = {c: 0.0 for c in cols}
        d["eleitorado"] = max(br["eleitorado"] - ele_ufs, 0.0) if math.isfinite(ele_ufs) else 0.0
        d["pst"] = 0.0
    d["atualizado"] = br.get("atualizado", "")
    d["derivado"] = True
    return d


# ------------------------------------------------------------------ busca
def buscar_g1(ano: int = 2026, turno: int = 1, log=print, baixar=baixar_json) -> dict:
    """{'BR': reg, 'AC': reg, ..., 'ZZ': reg, '_meta': {...}}; reg = dict com os campos do CSV + 'votos'."""
    base = f"{G1_HOST}/{ano}/apuracao/{turno}-turno"
    meta = {"fonte": "g1", "urls": [], "erros": [], "baixado_em": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    res = {}
    url = f"{base}/br/executivo.json"
    res["BR"] = parse_g1_executivo(baixar(url), ano)
    meta["urls"].append(url)
    # 1) consolidado (2026)
    ufs = {}
    try:
        url = f"{base}/br/PRESIDENTE_CONSOLIDADO.JSON"
        ufs = parse_g1_consolidado(baixar(url), ano)
        meta["urls"].append(url)
        meta["fonte_uf"] = "consolidado"
    except Exception as ex:  # noqa: BLE001
        meta["erros"].append(f"consolidado: {ex}")
    # 2) infográfico por UF (formato 2022), para o que faltar (inclui ZZ)
    falt = [u for u in UFS if u not in ufs]
    if falt and len(falt) > 1:   # só ZZ faltando é o normal do consolidado: não vale 28 requisições
        for uf in falt:
            url = f"{G1_INFOGRAFICO}/{ano}/{turno}-turno/PRESIDENTE_{uf}.JSON"
            try:
                ufs[uf] = parse_g1_infografico(baixar(url), ano)
                meta["urls"].append(url)
                meta.setdefault("fonte_uf", "infografico")
            except Exception as ex:  # noqa: BLE001
                meta["erros"].append(f"{uf} infografico: {ex}")
    elif falt == ["ZZ"]:
        url = f"{G1_INFOGRAFICO}/{ano}/{turno}-turno/PRESIDENTE_ZZ.JSON"
        try:
            ufs["ZZ"] = parse_g1_infografico(baixar(url), ano)
            meta["urls"].append(url)
        except Exception as ex:  # noqa: BLE001
            meta["erros"].append(f"ZZ infografico: {ex}")
    # eleitorado das UFs sem eleitorado (consolidado): executivo.json da UF (governador)
    for uf in UFS27:
        r = ufs.get(uf)
        pst_ok = 0 <= r["pst"] <= 100 if r is not None else True
        if r is None or (math.isfinite(r["eleitorado"]) and r["eleitorado"] > 0 and pst_ok):
            continue
        try:
            g = parse_g1_executivo(baixar(f"{base}/{uf.lower()}/executivo.json"), ano)
            r["eleitorado"] = g["eleitorado"]
            if not pst_ok and 0 <= g["pst"] <= 100:    # qtd_urnas fora de 0-100: usa o andamento da UF
                meta["erros"].append(f"{uf}: pst do consolidado {r['pst']} inválido; usando andamento {g['pst']}")
                r["pst"] = g["pst"]
        except Exception as ex:  # noqa: BLE001
            meta["erros"].append(f"{uf} eleitorado: {ex}")
            p = r["pst"] / 100 if r["pst"] > 0 else float("nan")
            r["eleitorado"] = (r["comparecimento"] + r["abstencao"]) / p if p == p else float("nan")
    zz = ufs.get("ZZ")
    if zz is not None and not (zz["eleitorado"] > 0):     # infográfico parcial: estima pelo % apurado
        zz["eleitorado"] = (zz["comparecimento"] + zz["abstencao"]) * 100 / zz["pst"] if zz["pst"] > 0 else 0.0
    if "ZZ" not in ufs and all(u in ufs for u in UFS27):
        ufs["ZZ"] = derivar_exterior(res["BR"], ufs, ano)
        meta["exterior"] = "derivado (Brasil − 27 UFs)"
    res.update(ufs)
    meta["faltando"] = [u for u in UFS if u not in res]
    res["_meta"] = meta
    for e in meta["erros"]:
        log(f"  aviso: {e}")
    return res


# ------------------------------------------------------------------ CSV
def _fmt(x, dec=0):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "0"
    return f"{x:.{dec}f}" if dec else str(int(round(x)))


def linhas_csv(res: dict, ano: int) -> list[dict]:
    cols = CAND_COLS[ano]
    out = []
    for uf in ["BR"] + UFS:
        r = res.get(uf)
        if r is None:
            continue
        d = {"uf": uf, "pst": _fmt(r["pst"] if r["pst"] == r["pst"] else 0.0, 2)}
        for k in CAMPOS_NUM:
            d[k] = _fmt(r[k])
        for c in cols:
            d[c] = _fmt(r["votos"].get(c, 0.0))
        out.append(d)
    return out


def gravar_csv(res: dict, ano: int, caminho: Path) -> Path:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=BASE_COLS + CAND_COLS[ano], lineterminator="\n")
        w.writeheader()
        w.writerows(linhas_csv(res, ano))
    tmp.replace(caminho)
    return caminho


# ------------------------------------------------------------------ TSE e comparação
def _parse_tse(js: dict, ano: int) -> dict:
    """Leitor mínimo do JSON do TSE (formato 'u' de 2024+ e 'r' de 2022), independente do resultado_1t.py."""
    if "carg" in js:
        s, e, v = js.get("s", {}), js.get("e", {}), js.get("v", {})
        cands = [(c.get("n"), num(c.get("vap")), _valido(c.get("dvt")))
                 for car in js["carg"] if str(car.get("cd")) == "1"
                 for agr in car.get("agr", []) for par in agr.get("par", []) for c in par.get("cand", [])]
        r = {"pst": num(s.get("pst")), "eleitorado": num(e.get("te")), "comparecimento": num(e.get("c")),
             "abstencao": num(e.get("a")), "validos": num(v.get("vv")), "brancos": num(v.get("vb")),
             "nulos": num(v.get("tvn"))}
    elif "cand" in js:
        cands = [(c.get("n"), num(c.get("vap")), _valido(c.get("dvt"))) for c in js["cand"]]
        r = {k2: num(js.get(k1)) for k1, k2 in [("pst", "pst"), ("e", "eleitorado"), ("c", "comparecimento"),
                                                  ("a", "abstencao"), ("vv", "validos"), ("vb", "brancos"),
                                                  ("tvn", "nulos")]}
    else:
        raise ValueError("JSON do TSE em formato desconhecido")
    r["votos"] = _agrega_cands(cands, ano)
    if not (r["validos"] > 0):
        r["validos"] = sum(r["votos"].values())
    r["atualizado"] = f"{js.get('dg', '')} {js.get('hg', '')}".strip()
    return r


def buscar_tse(ano: int = 2026, diretorio: Path | None = None, log=print, baixar=baixar_json) -> dict:
    """TSE por UF (28 + BR). diretorio: lê JSONs locais ({uf}-c0001-e*.json) em vez de baixar."""
    res = {}
    for uf in ["BR"] + UFS:
        try:
            if diretorio is not None:
                ps = sorted(Path(diretorio).glob(f"{uf.lower()}-c0001-e*.json"))
                if not ps:
                    continue
                js = json.loads(ps[0].read_text(encoding="utf-8"))
            else:
                ciclo, cd = TSE_ELEICAO[ano]
                u = uf.lower()
                js = baixar(f"{TSE_HOST}/oficial/{ciclo}/{cd}/dados/{u}/{u}-c0001-e{int(cd):06d}-u.json")
            res[uf] = _parse_tse(js, ano)
        except Exception as ex:  # noqa: BLE001
            log(f"  TSE {uf}: {ex}")
    return res


def comparar(a: dict, b: dict, ano: int, tol_pp: float = 0.3, tol_pst: float = 1.0) -> list[dict]:
    """Compara duas leituras (a = TSE, b = alternativa) por UF.

    Para cada UF: Δpst (p.p.), Δ de cada candidato em % dos válidos (p.p.), Δ de abstenção e brancos+nulos em %
    do comparecimento, Δ relativo dos válidos. 'alerta' quando as duas estão no mesmo ponto da apuração
    (|Δpst| <= tol_pst) e algum Δ de fatia passa de tol_pp, ou quando com pst = 100 os votos diferem."""
    cols = CAND_COLS[ano]
    out = []
    for uf in ["BR"] + UFS:
        ra, rb = a.get(uf), b.get(uf)
        if ra is None or rb is None:
            out.append({"uf": uf, "status": "ausente em " + ("TSE" if ra is None else "alternativa")})
            continue
        d = {"uf": uf, "pst_a": ra["pst"], "pst_b": rb["pst"], "d_pst": rb["pst"] - ra["pst"]}
        va, vb = ra["validos"], rb["validos"]
        if not (va > 0 and vb > 0):
            d["status"] = "sem votos" if not (va > 0 or vb > 0) else "votos só em " + ("TSE" if va > 0 else "alternativa")
            out.append(d)
            continue
        dmax = 0.0
        for c in cols:
            x = 100 * (rb["votos"].get(c, 0) / vb - ra["votos"].get(c, 0) / va)
            d[f"d_{c}"] = x
            dmax = max(dmax, abs(x))
        d["d_validos_rel"] = 100 * (vb / va - 1)
        ca, cb = ra["comparecimento"], rb["comparecimento"]
        if ca > 0 and cb > 0:
            d["d_bn"] = 100 * ((rb["brancos"] + rb["nulos"]) / cb - (ra["brancos"] + ra["nulos"]) / ca)
            d["d_abst"] = 100 * (rb["abstencao"] / (cb + rb["abstencao"]) - ra["abstencao"] / (ca + ra["abstencao"]))
        d["d_max_pp"] = dmax
        mesmo_ponto = abs(d["d_pst"]) <= tol_pst
        if mesmo_ponto and dmax > tol_pp:
            d["status"] = "DIVERGENTE"
        elif ra["pst"] >= 99.99 and rb["pst"] >= 99.99 and abs(d["d_validos_rel"]) > 0.01:
            d["status"] = "DIVERGENTE (totalizado)"
        elif not mesmo_ponto:
            d["status"] = "momentos diferentes"
        else:
            d["status"] = "ok"
        out.append(d)
    return out


def imprimir_comparacao(rows: list[dict], ano: int, nome_a="TSE", nome_b="g1") -> str:
    cols = CAND_COLS[ano]
    cab = f"{'UF':<3} {'pst ' + nome_a:>9} {'pst ' + nome_b:>8} " + " ".join(f"{c[:6]:>7}" for c in cols) + \
          f" {'bn':>6} {'abst':>6} {'válid%':>7}  status"
    linhas = [f"Diferenças {nome_b} − {nome_a} (p.p. dos válidos; bn/abst em p.p.; válidos em % relativo)", cab]
    for d in rows:
        if "d_max_pp" not in d:
            pa = f"{d['pst_a']:9.2f} {d['pst_b']:8.2f}" if "pst_a" in d else f"{'':9} {'':8}"
            linhas.append(f"{d['uf']:<3} {pa} {d['status']}")
            continue
        linhas.append(f"{d['uf']:<3} {d['pst_a']:9.2f} {d['pst_b']:8.2f} "
                      + " ".join(f"{d[f'd_{c}']:+7.2f}" for c in cols)
                      + f" {d.get('d_bn', float('nan')):+6.2f} {d.get('d_abst', float('nan')):+6.2f}"
                      + f" {d['d_validos_rel']:+7.2f}  {d['status']}")
    n_div = sum(1 for d in rows if str(d.get("status", "")).startswith("DIVERGENTE"))
    linhas.append(f"{n_div} UF(s) divergente(s).")
    return "\n".join(linhas)


def resumo(res: dict, ano: int) -> str:
    br = res.get("BR")
    if not br:
        return "sem Brasil"
    v = br["validos"]
    fat = ", ".join(f"{c} {100 * br['votos'][c] / v:.2f}%" for c in CAND_COLS[ano]) if v > 0 else "sem votos"
    n_ap = sum(1 for u in UFS if u in res and res[u]["pst"] > 0)
    return (f"Brasil: {br['pst']:.2f}% das seções ({br.get('atualizado', '')}); {fat}. "
            f"UFs com apuração: {n_ap}/28; faltando: {res.get('_meta', {}).get('faltando', [])}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ano", type=int, default=2026, choices=sorted(CAND_COLS))
    ap.add_argument("--saida", type=Path, default=None, help="CSV de saída (padrão: data/resultado_1t_manual.csv)")
    ap.add_argument("--comparar", action="store_true", help="compara TSE x g1 por UF (não grava CSV)")
    ap.add_argument("--tse-dir", type=Path, default=None, help="com --comparar: JSONs do TSE locais em vez de baixar")
    ap.add_argument("--tol", type=float, default=0.3, help="tolerância em p.p. para alertar divergência")
    ap.add_argument("--intervalo", type=int, default=0, help="repete a cada N segundos (0 = uma vez)")
    a = ap.parse_args(argv)
    saida = a.saida or MANUAL_CSV
    if a.ano != 2026 and a.saida is None and not a.comparar:
        ap.error("--ano diferente de 2026 exige --saida (não sobrescrever o CSV manual de 2026)")
    while True:
        try:
            alt = buscar_g1(a.ano)
            print(resumo(alt, a.ano))
            if a.comparar:
                tse = buscar_tse(a.ano, a.tse_dir)
                print(imprimir_comparacao(comparar(tse, alt, a.ano, a.tol), a.ano))
            else:
                p = gravar_csv(alt, a.ano, saida)
                print(f"gravado {p} ({len(linhas_csv(alt, a.ano))} linhas)")
        except Exception as ex:  # noqa: BLE001
            print(f"ERRO: {type(ex).__name__}: {ex}", file=sys.stderr)
            if not a.intervalo:
                return 1
        if not a.intervalo:
            return 0
        time.sleep(a.intervalo)


if __name__ == "__main__":
    raise SystemExit(main())
