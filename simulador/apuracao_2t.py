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


def baixar_tse(fonte: str = "tse", pasta: Path | None = None) -> dict:
    out, erros = {}, []
    for uf in ["BR"] + R.UFS:
        try:
            if fonte == "diretorio":
                js = json.loads(next(Path(pasta).glob(f"{uf.lower()}-c0001-e*.json")).read_text(encoding="utf-8"))
            else:
                js = R._baixar(R.urls_presidente(CICLO, CD2T, uf)[0], timeout=15, tentativas=2)
            out[uf] = R.parse_tse(js, R.NUMEROS[2026])
        except Exception as ex:                                  # noqa: BLE001
            erros.append(f"{uf}: {ex}")
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


def projetar(tse: dict, modelo: dict, n: int = 40_000, seed: int = 25) -> dict:
    s = modelo["segundo_turno"]
    ufs = {u["uf"]: u for u in s["ufs"]}
    rng = np.random.default_rng(seed)
    linhas, obs_l, obs_v, d_num, d_den = [], 0.0, 0.0, 0.0, 0.0
    for uf, u in ufs.items():
        t = tse.get(uf)
        p = float(t["pst"]) if t and np.isfinite(t["pst"]) else 0.0
        vl = float(t["votos"].get("Lula", 0.0)) if t else 0.0
        vf = float(t["votos"].get("Flavio", 0.0)) if t else 0.0
        v = vl + vf
        prior = u["a_media"] / 100
        if p >= 10 and v > 0:                      # desvio nacional do modelo, medido onde já há apuração
            d_num += v * (vl / v - prior)
            d_den += v
        linhas.append({"uf": uf, "nome": u.get("nome", uf), "regiao": u["regiao"], "pst": p, "lula": vl, "flavio": vf,
                       "prior": prior, "esperado_validos": u["validos_2t_media"], "eleitores": u["eleitores"]})
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
        if p > 0 and v > 0:
            w = min(1.0, p / 30)
            total = w * v / (p / 100) + (1 - w) * r["esperado_validos"]
        else:
            total = r["esperado_validos"]
        resto = max(total - v, 0.0) if p < 100 else 0.0
        lam = p / (p + 10) if v > 0 else 0.0
        s_obs = r["lula"] / v if v > 0 else r["prior"]
        s_rest = lam * s_obs + (1 - lam) * (r["prior"] + desvio)
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
    antes = p_br < 0.5
    proj = {"p_lula": s["p_a_vence"] if antes else p_lula,
            "lula_pct": s["a_media"] if antes else float(100 * np.median(q)),
            "lula_p10": s["a_quantis"][1] if antes else float(100 * np.quantile(q, 0.1)),
            "lula_p90": s["a_quantis"][5] if antes else float(100 * np.quantile(q, 0.9)),
            "validos": float(np.median(tot_v)), "desvio_modelo_pp": 100 * desvio,
            "fonte": "modelo da véspera (sem apuração)" if antes else "parcial do TSE + modelo"}
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
                       "esperado_pct": round(100 * r["prior"], 2), "proj_pct": round(100 * r["lula_proj"], 2),
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
          f"proj Lula {js['projecao']['lula_pct']:.2f}% | P(Lula) {js['projecao']['p_lula']:.3f}")


if __name__ == "__main__":
    main()
