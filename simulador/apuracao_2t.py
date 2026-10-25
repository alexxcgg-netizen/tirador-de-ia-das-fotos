"""Noite da apuração do 2º turno (25/10/2026): parcial do TSE por UF -> projeção do resultado final.

Para cada UF: votos já apurados (Lula e Flávio) + votos que faltam, estimados pela mistura do total implícito
na parcial (válidos / % de seções) com os válidos esperados pelo modelo (web/resultados_2t.json). A fatia de Lula
nos votos que faltam mistura a fatia já apurada na UF com a expectativa do modelo deslocada pelo desvio nacional
observado (UFs com mais apuração dizem quanto o modelo errou). Incerteza: choque nacional comum, choque comum da
ordem de apuração dentro das UFs (as primeiras seções podem não representar o resto) e choque por UF, todos encolhendo à medida que a apuração avança. Antes da 1ª parcial, a projeção é a do modelo da véspera.

Também grava a margem parcial esperada pela ordem de totalização de 2022 (Sul/Sudeste primeiro) e a linha de
empate: com X% apurado, se Flávio está à frente por menos que a linha, a parcial aponta Lula vencendo.

Uso: python simulador/apuracao_2t.py --saida pasta/apuracao_2t.json [--fonte tse|diretorio --dir pasta_json]
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import resultado_1t as R

AQUI = Path(__file__).resolve().parent
MODELO = AQUI / "web" / "resultados_2t.json"
HIST = AQUI / "data" / "resultados_uf_2002_2022.csv"
CICLO, CD2T = "ele2026", "6258"
# 2º turno de 2022 (Agência Brasil): % de seções totalizadas -> margem parcial Lula − Bolsonaro (p.p. dos válidos)
PONTOS_2022 = [(32.41, -1.82), (51.96, -0.52), (67.76, 0.02), (100.0, 1.80)]
FINAL_2022 = 1.80
NNE = {"N", "NE"}


CACHE_UF = Path(__file__).resolve().parent / "data" / "tse_2t_2026_ultimo.json"
MUN_1T = Path(__file__).resolve().parent / "data" / "municipios_1t_2026.csv"   # TSE, votacao_candidato_munzona_2026


def carregar_mun() -> dict:
    """1º turno por município (Lula e Flávio): {uf: (códigos TSE, votos Lula, votos Flávio)}."""
    import csv
    m = {}
    for r in csv.DictReader(open(MUN_1T, encoding="utf-8")):
        l, f = int(r["lula"]), int(r["flavio"])
        if l + f:
            m.setdefault(r["uf"], []).append((int(r["cd_municipio"]), l, f))
    return {uf: (np.array([x[0] for x in v]), np.array([x[1] for x in v], float), np.array([x[2] for x in v], float))
            for uf, v in m.items()}


def composicao(ab: list, mun: tuple, prior_uf: float):
    """Fração apurada de cada município (eleitorado totalizado / eleitorado, do arquivo de abrangência), peso
    (votos dos dois no 1º turno) e fatia de Lula esperada no município: a do 1º turno deslocada, em logito, pelo
    quanto o modelo espera que a UF mude do 1º para o 2º turno."""
    cds, L, F = mun
    a = {int(c): (te, est) for c, te, est in ab}
    te = np.array([a.get(int(c), (0.0, 0.0))[0] for c in cds], float)
    est = np.array([a.get(int(c), (0.0, 0.0))[1] for c in cds], float)
    frac = np.clip(np.where(te > 0, est / np.where(te > 0, te, 1), 0.0), 0, 1)
    V = L + F
    t = np.clip(L / V, 0.01, 0.99)
    t_uf = L.sum() / V.sum()
    b = R.M.expit(R.M.logit(t) + R.M.logit(prior_uf) - R.M.logit(t_uf))
    return frac, V, b


def baixar_tse(fonte: str = "tse", pasta: Path | None = None) -> dict:
    """Uma tentativa por UF, com pausa entre pedidos (o TSE devolve 429 a quem pede rápido demais). UF que falhar
    fica com a última leitura boa (cache local), para a projeção não perder o estado inteiro."""
    import time
    cache = json.loads(CACHE_UF.read_text(encoding="utf-8")) if CACHE_UF.exists() else {}
    out, erros = {}, []
    for uf in ["BR"] + R.UFS:
        try:
            if fonte == "diretorio":
                js = json.loads(next(Path(pasta).glob(f"{uf.lower()}-c0001-e*.json")).read_text(encoding="utf-8"))
            else:
                js = None
                for t in range(4):                       # 429 é intermitente: espera e tenta de novo
                    try:
                        js = R._baixar(R.urls_presidente(CICLO, CD2T, uf)[0], timeout=15, tentativas=1)
                        break
                    except Exception as ex2:             # noqa: BLE001
                        if t == 3 or "429" not in str(ex2):
                            raise
                        time.sleep(2 + 2 * t)
                time.sleep(0.4)
            out[uf] = R.parse_tse(js, R.NUMEROS[2026])
            cache[uf] = js
        except Exception as ex:                                  # noqa: BLE001
            erros.append(f"{uf}: {ex}")
            if uf in cache:
                out[uf] = R.parse_tse(cache[uf], R.NUMEROS[2026])
    out["_ab"] = {}
    idade_ab = time.time() - cache.get("_ab_em", 0)
    if fonte != "diretorio":                             # abrangência: quais municípios já foram apurados
        for uf in (R.UFS if idade_ab > 240 else []):     # muda devagar: renova a cada ~4 min, senão usa o cache
            cache["_ab_em"] = time.time()
            if uf == "ZZ":
                continue
            try:
                js = None
                for t in range(3):
                    try:
                        js = R._baixar(R.url_ab(CICLO, CD2T, uf), timeout=15, tentativas=1)
                        break
                    except Exception as ex2:             # noqa: BLE001
                        if t == 2 or "429" not in str(ex2):
                            raise
                        time.sleep(2 + 2 * t)
                time.sleep(0.4)
                cache["ab_" + uf] = js
            except Exception as ex:                      # noqa: BLE001
                erros.append(f"ab {uf}: {ex}")
                js = cache.get("ab_" + uf)
        for uf in R.UFS:
            js = cache.get("ab_" + uf)
            if js and uf != "ZZ":
                d = R.parse_ab(js)
                out["_ab"][uf] = list(zip(d.cd, d.te.fillna(0), d.est.fillna(0)))
        CACHE_UF.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    out["_erros"] = erros
    return out


def fator_k(ufs: list) -> float:
    """Razão entre o gap regional esperado em 2026 e o do 2º turno de 2022 (margem N+NE menos S+SE+CO)."""
    import csv

    def gap(rows):
        def m(nne):
            r = [x for x in rows if (x[0] in NNE) == nne]
            return sum(a * w for _, a, w in r) / sum(w for _, _, w in r)
        return m(True) - m(False)
    g26 = gap([(u["regiao"], 2 * u["a_media"] - 100, u["validos_2t_media"]) for u in ufs if u["uf"] != "ZZ"])
    h = [r for r in csv.DictReader(open(HIST, encoding="utf-8")) if r["ano"] == "2022" and r["turno"] == "2"
         and r["uf"] not in ("BR", "ZZ")]
    g22 = gap([(r["regiao"], float(r["pt_pct_validos"]) - float(r["oponente_pct_validos"]), float(r["votos_validos"]))
               for r in h])
    return g26 / g22


def trajetoria(final_esperado: float, k: float) -> list:
    return [{"pst": x, "margem_2022": m, "esperada": round(final_esperado + k * (m - FINAL_2022), 2),
             "linha_empate": round(k * (m - FINAL_2022), 2)} for x, m in PONTOS_2022]


def interp(traj: list, pst: float, chave: str) -> float:
    xs, ys = [t["pst"] for t in traj], [t[chave] for t in traj]
    return float(np.interp(pst, xs, ys))          # antes de 32% fica no valor de 32% (2022 não tem pontos antes)


def projetar(tse: dict, modelo: dict, n: int = 40_000, seed: int = 25, mun: dict | None = None) -> dict:
    s = modelo["segundo_turno"]
    ufs = {u["uf"]: u for u in s["ufs"]}
    rng = np.random.default_rng(seed)
    ab = tse.get("_ab", {})
    mun = carregar_mun() if mun is None and MUN_1T.exists() else (mun or {})
    linhas, obs_l, obs_v, d_num, d_den = [], 0.0, 0.0, 0.0, 0.0
    for uf, u in ufs.items():
        t = tse.get(uf)
        p = float(t["pst"]) if t and np.isfinite(t["pst"]) else 0.0
        vl = float(t["votos"].get("Lula", 0.0)) if t else 0.0
        vf = float(t["votos"].get("Flavio", 0.0)) if t else 0.0
        v = vl + vf
        prior = u["a_media"] / 100
        r = {"uf": uf, "nome": u.get("nome", uf), "regiao": u["regiao"], "pst": p, "lula": vl, "flavio": vf, "prior": prior,
             "lula_1t": round(100 * u["a_1t"] / (u["a_1t"] + u["b_1t"]), 2), "esperado_validos": u["validos_2t_media"],
             "eleitores": u["eleitores"], "comp": None, "esperado_apurado": None}
        if uf in ab and uf in mun and v > 0:
            frac, V, b = composicao(ab[uf], mun[uf], prior)
            te_ab = sum(float(x[1]) for x in ab[uf])
            p_ab = sum(float(x[2]) for x in ab[uf]) / te_ab if te_ab else 0.0
            if p_ab > 0 and abs(p / 100 - p_ab) > 0.005:
                # abrangência mais velha que a parcial da UF (renovada a cada ~4 min ou com 429): reescala a fração
                # apurada de cada município para bater com a % da UF, senão os votos que faltam saem inflados
                frac = np.clip(frac * (p / 100) / p_ab, 0, 1)
            cv = float((frac * V).sum())
            if cv > 0.002 * V.sum():
                r["comp"] = (frac, V, b, cv)
                r["esperado_apurado"] = float((frac * V * b).sum() / cv)   # o que o modelo esperava NAS seções já apuradas
        base = r["esperado_apurado"] if r["esperado_apurado"] is not None else prior
        if v > 0 and uf != "ZZ" and (p >= 10 or (r["comp"] is not None and p >= 3)):
            d_num += v * (vl / v - base)         # desvio do modelo descontada a composição do que já foi apurado
            d_den += v
        linhas.append(r)
        obs_l += vl
        obs_v += v
    br = tse.get("BR")
    p_br = float(br["pst"]) if br and np.isfinite(br["pst"]) else 0.0
    desvio = (d_num / d_den) * min(1.0, p_br / 20) if d_den else 0.0
    sig_n = 0.015 * max(0.12, 1 - p_br / 100)
    # choque comum da ordem de apuração dentro das UFs (capital/interior, urbano/rural): não some com o desvio
    # nacional medido, porque afeta igualmente as seções já apuradas que usamos para medi-lo
    sig_ordem = 0.03 * (1 - min(p_br, 100) / 100) ** 0.5
    choque_n = rng.normal(0, sig_n, n) + rng.normal(0, sig_ordem, n)
    tot_l = np.full(n, obs_l)
    tot_v = np.full(n, obs_v)
    for r in linhas:
        p, v = r["pst"], r["lula"] + r["flavio"]
        s_obs = r["lula"] / v if v > 0 else r["prior"]
        if r["comp"] is not None:
            # método municipal: votos que faltam = votos do 1º turno nos municípios (fração não apurada) x razão
            # 2º/1º turno observada; fatia = esperada em cada município deslocada pelo swing da UF já medido
            frac, V, b, cv = r["comp"]
            razao = float(np.clip(v / cv, 0.7, 1.3))
            resto = razao * float(((1 - frac) * V).sum()) if p < 100 else 0.0
            sw_uf = float(R.M.logit(np.clip(s_obs, 0.01, 0.99)) - R.M.logit(np.clip(r["esperado_apurado"], 0.01, 0.99)))
            sw_nac = desvio / max(r["prior"] * (1 - r["prior"]), 0.05)
            w = p / (p + 3)
            sw = w * sw_uf + (1 - w) * sw_nac
            rest_w = (1 - frac) * V
            s_rest = float((rest_w * R.M.expit(R.M.logit(b) + sw)).sum() / rest_w.sum()) if rest_w.sum() > 0 else s_obs
            r["metodo"] = "municipal"
        else:
            if p > 0 and v > 0:
                w = min(1.0, p / 30)
                total = w * v / (p / 100) + (1 - w) * r["esperado_validos"]
            else:
                total = r["esperado_validos"]
            resto = max(total - v, 0.0) if p < 100 else 0.0
            lam = p / (p + 25) if v > 0 else 0.0     # primeiras seções (capitais) podem não representar a UF
            s_rest = lam * s_obs + (1 - lam) * (r["prior"] + desvio)
            r["metodo"] = "uf"
        r.update({"faltam_validos": resto, "lula_resto": s_rest,
                  "lula_proj": (r["lula"] + resto * s_rest) / (v + resto) if v + resto > 0 else r["prior"]})
        if resto > 0:
            sim = np.clip(s_rest + choque_n + rng.normal(0, 0.03 * math.sqrt(1 - p / 100), n), 0, 1)
            tot_l += resto * sim
            tot_v += resto
    q = tot_l / tot_v
    p_lula = float((q > 0.5).mean())
    k = fator_k(list(ufs.values()))
    final_modelo = 2 * s["a_media"] - 100
    traj = trajetoria(final_modelo, k)
    parcial = {"pst": p_br, "lula": float(br["votos"].get("Lula", 0)) if br else 0.0,
               "flavio": float(br["votos"].get("Flavio", 0)) if br else 0.0,
               "atualizado_tse": br.get("atualizado") if br else None,
               "comparecimento": br.get("comparecimento") if br else None, "eleitorado": br.get("eleitorado") if br else None}
    vb = parcial["lula"] + parcial["flavio"]
    parcial["lula_pct"] = 100 * parcial["lula"] / vb if vb else None
    parcial["margem"] = (2 * parcial["lula_pct"] - 100) if vb else None
    antes = p_br < 3       # abaixo de 3% a parcial é ruído de ordem de apuração: mostra o modelo
    proj = {"p_lula": s["p_a_vence"] if antes else p_lula,
            "lula_pct": s["a_media"] if antes else float(100 * np.median(q)),
            "lula_p10": s["a_quantis"][1] if antes else float(100 * np.quantile(q, 0.1)),
            "lula_p90": s["a_quantis"][5] if antes else float(100 * np.quantile(q, 0.9)),
            "validos": float(np.median(tot_v)), "desvio_modelo_pp": 100 * desvio,
            "fonte": "modelo da véspera (com menos de 3% apurado a parcial ainda não diz nada)" if antes else "parcial do TSE + modelo"}
    if not antes:
        proj["margem_votos_p50"] = float(np.median(2 * tot_l - tot_v))
        proj["margem_votos_p10"] = float(np.quantile(2 * tot_l - tot_v, 0.1))
        proj["margem_votos_p90"] = float(np.quantile(2 * tot_l - tot_v, 0.9))
    else:
        v = s["votos"]
        proj.update({"margem_votos_p50": v["margem_quantis"][3], "margem_votos_p10": v["margem_quantis"][1],
                     "margem_votos_p90": v["margem_quantis"][5]})
    bench = None
    if vb:
        bench = {"esperada": round(interp(traj, p_br, "esperada"), 2), "linha_empate": round(interp(traj, p_br, "linha_empate"), 2)}
    ufs_out = sorted([{"uf": r["uf"], "nome": r["nome"], "regiao": r["regiao"], "pst": round(r["pst"], 2),
                       "lula_pct": round(100 * r["lula"] / (r["lula"] + r["flavio"]), 2) if r["lula"] + r["flavio"] else None,
                       "esperado_pct": round(100 * r["prior"], 2),
                       "esperado_apurado_pct": None if r["esperado_apurado"] is None else round(100 * r["esperado_apurado"], 2),
                       "metodo": r["metodo"], "lula_1t_pct": r["lula_1t"], "proj_pct": round(100 * r["lula_proj"], 2),
                       "eleitores": r["eleitores"]} for r in linhas], key=lambda x: -x["eleitores"])
    return {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "parcial": parcial, "projecao": proj,
            "benchmark": bench, "trajetoria": traj, "k": round(k, 3),
            "modelo": {"p_lula": s["p_a_vence"], "lula_pct": s["a_media"], "p10": s["a_quantis"][1], "p90": s["a_quantis"][5],
                       "gerado_em": modelo["meta"]["gerado_em"]},
            "ufs": ufs_out}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--saida", required=True)
    ap.add_argument("--fonte", default="tse", choices=["tse", "diretorio"])
    ap.add_argument("--dir", default=None)
    a = ap.parse_args()
    saida = Path(a.saida)
    tse = baixar_tse(a.fonte, a.dir)
    erros = tse.pop("_erros")
    if "BR" not in tse:
        print("TSE indisponível:", erros[:3])
        return
    js = projetar(tse, json.loads(MODELO.read_text(encoding="utf-8")))
    js["erros_download"] = erros[:10]
    hist = []
    if saida.exists():
        hist = json.loads(saida.read_text(encoding="utf-8")).get("historico", [])
    p = js["parcial"]
    ponto = {"hora": js["gerado_em"], "pst": p["pst"], "margem_parcial": p["margem"], "lula_proj": js["projecao"]["lula_pct"],
             "p_lula": js["projecao"]["p_lula"], "atualizado_tse": p["atualizado_tse"]}
    if not hist or hist[-1]["pst"] != ponto["pst"] or hist[-1]["atualizado_tse"] != ponto["atualizado_tse"]:
        hist.append(ponto)
    js["historico"] = hist
    saida.write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"pst {p['pst']:.2f}% | Lula parcial {p['lula_pct'] if p['lula_pct'] is None else round(p['lula_pct'], 2)} | "
          f"proj Lula {js['projecao']['lula_pct']:.2f}% | P(Lula) {js['projecao']['p_lula']:.3f} | falhas {len(erros)} | TSE {p['atualizado_tse']}")


if __name__ == "__main__":
    main()
