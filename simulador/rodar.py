"""Roda o simulador de 2026 e grava web/resultados.json.

Três visões, sempre lado a lado:
  * calibrado (principal): viés da indústria com prior empírico-bayesiano dos
    erros de 2014/2018/2022, encolhido para zero, ponderado pela exposição de
    cada instituto; ajuste de comparecimento por segmento; integra sobre a
    incerteza do viés (a probabilidade é a média sobre os sorteios do viés);
  * neutro: viés 0 (pesquisas como estão, com a contração usual da terceira via);
  * pleno: viés médio histórico sem encolhimento, exposição 1.

Uso:
    python simulador/rodar.py                 # 500.000 simulações por visão
    python simulador/rodar.py --n 50000 --seed 1
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import modelo as M  # noqa: E402
import backtest as BT  # noqa: E402

VISAO_DESC = {"calibrado": "Modelo calibrado (viés com incerteza, encolhido; principal)",
              "neutro": "Neutro (pesquisas sem viés sistemático)",
              "pleno": "Viés histórico pleno (erro médio de 2014/2018/2022, sem encolhimento)"}
QS = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]
NB = 1001  # histogramas por UF: 0,0..100,0 em passos de 0,1 p.p.


def _q_hist(h, qs=QS):
    c = np.cumsum(h) / h.sum()
    return [round(float(np.searchsorted(c, q) / 10), 2) for q in qs]


def _hist(x, lo, hi, passo):
    bordas = np.arange(lo, hi + passo / 2, passo)
    h, _ = np.histogram(np.clip(x, lo, hi - 1e-6), bordas)
    return {"inicio": lo, "passo": passo, "contagens": h.astype(int).tolist()}


def _p(x, n):
    p = float(x)
    return {"p": round(p, 5), "ep_mc": round(math.sqrt(max(p * (1 - p), 1e-12) / n), 5)}


def vieses_2026(base: M.Base, prem: dict, err: dict | None = None) -> dict:
    """Prior do viés por visão, a partir dos erros históricos (todos os 3 anos)."""
    err = err or BT.erros_brutos(prem)
    corr = prem["vies.ajuste_comparecimento_historico_pp"]
    out = {}
    for v in M.VISOES:
        pri = BT.priors_vies(err, list(BT.ANOS), prem, v, correcao_comp=corr if v == "calibrado" else None)
        d = {"muT": pri["muT"], "b1": pri["b1"], "b2": pri["b2"]}
        if v == "calibrado":
            d["lambda1"] = (base.agg1["lambda_medio"], base.agg1["dp_lambda"])
            d["lambda2"] = (base.agg2["lambda_medio"], base.agg2["dp_lambda"])
            d["ajuste_comp"] = True
        else:
            d["lambda1"] = d["lambda2"] = (1.0, 0.0)
            d["ajuste_comp"] = False
        d["residuos"] = pri.get("residuos")
        out[v] = d
    return out


def executar(n: int, seed: int, lote: int, visoes=M.VISOES, base=None, vieses=None, prem=None,
             guardar_brutos=False):
    prem = prem or M.carregar_premissas()
    base = base or M.construir_base_2026(prem)
    vieses = vieses or vieses_2026(base, prem)
    U = len(base.ufs)
    K = base.e.K
    saida, brutos = {}, {}
    for ci, vis in enumerate(visoes):
        rng = np.random.default_rng([seed, ci])
        acc = {k: [] for k in ("nat1", "Q", "Q_pesquisas", "Q_transf", "primeiro", "segundo", "venceu_1t",
                               "par_lf", "vencedor", "e_p2", "nat_p2_agregado", "b1", "b2", "teto_rejeicao")}
        hL = np.zeros((U, NB), np.int64); hF = np.zeros((U, NB), np.int64); hq = np.zeros((U, NB), np.int64)
        topL = np.zeros(U); topF = np.zeros(U); winq = np.zeros(U)
        sL = np.zeros(U); sF = np.zeros(U); sq = np.zeros(U)
        feito = 0
        while feito < n:
            B = min(lote, n - feito)
            r = M.simular_lote(base, vieses[vis], B, rng)
            for k in acc:
                acc[k].append(r[k])
            for arr, h, s in ((r["uf_L"], hL, sL), (r["uf_F"], hF, sF), (r["uf_q"], hq, sq)):
                idx = np.clip(np.rint(arr * 1000).astype(np.int32), 0, NB - 1)
                for u in range(U):
                    h[u] += np.bincount(idx[:, u], minlength=NB)
                s += arr.sum(0)
            topL += (r["uf_top"] == 0).sum(0); topF += (r["uf_top"] == 1).sum(0)
            winq += (r["uf_q"] > 0.5).sum(0)
            feito += B
        A = {k: np.concatenate(v) for k, v in acc.items()}
        if guardar_brutos:
            brutos[vis] = A
        nat1 = A["nat1"]
        res = {"descricao": VISAO_DESC[vis], "n": n,
               "vies_usado": {k: (list(v) if isinstance(v, tuple) else v) for k, v in vieses[vis].items()
                              if k != "residuos"}}
        venc = A["vencedor"]
        res["prob"] = {
            "lula_vence": _p((venc == 0).mean(), n),
            "flavio_vence": _p((venc == 1).mean(), n),
            "outro_vence": _p((venc > 1).mean(), n),
            "decide_1t": _p(A["venceu_1t"].mean(), n),
            "lula_vence_1t": _p((A["venceu_1t"] & (A["primeiro"] == 0)).mean(), n),
            "flavio_vence_1t": _p((A["venceu_1t"] & (A["primeiro"] == 1)).mean(), n),
            "segundo_turno_lula_flavio": _p((~A["venceu_1t"] & A["par_lf"]).mean(), n),
            "segundo_turno_outro_par": _p((~A["venceu_1t"] & ~A["par_lf"]).mean(), n),
            "lula_1o_no_1t": _p((A["primeiro"] == 0).mean(), n),
            "flavio_1o_no_1t": _p((A["primeiro"] == 1).mean(), n),
            "lula_vence_2t_se_houver": _p(((A["Q"] > 0.5) & ~A["venceu_1t"] & A["par_lf"]).sum()
                                          / max((~A["venceu_1t"] & A["par_lf"]).sum(), 1), n),
        }
        res["prob_top2"] = {c: _p(((A["primeiro"] == k) | (A["segundo"] == k)).mean(), n) for k, c in enumerate(M.CANDS)}
        res["prob_1o_lugar"] = {c: _p((A["primeiro"] == k).mean(), n) for k, c in enumerate(M.CANDS)}
        res["primeiro_turno"] = {c: {"media": round(float(nat1[:, k].mean() * 100), 3),
                                     "quantis": [round(float(x) * 100, 2) for x in np.quantile(nat1[:, k], QS)]}
                                 for k, c in enumerate(M.CANDS)}
        tv = 1 - nat1[:, 0] - nat1[:, 1]
        res["primeiro_turno"]["terceira_via"] = {"media": round(float(tv.mean() * 100), 3),
                                                 "quantis": [round(float(x) * 100, 2) for x in np.quantile(tv, QS)]}
        res["primeiro_turno"]["margem_lula_flavio"] = {
            "media": round(float((nat1[:, 0] - nat1[:, 1]).mean() * 100), 3),
            "quantis": [round(float(x) * 100, 2) for x in np.quantile(nat1[:, 0] - nat1[:, 1], QS)]}
        res["hist_1t"] = {c: _hist(nat1[:, k] * 100, 20, 65, 0.25) for k, c in enumerate(M.CANDS[:2])}
        res["hist_1t"]["Menores"] = _hist(tv * 100, 0, 25, 0.25)
        marg2 = (2 * A["Q"] - 1) * 100
        res["segundo_turno"] = {
            "lula_media": round(float(A["Q"].mean() * 100), 3),
            "lula_quantis": [round(float(x) * 100, 2) for x in np.quantile(A["Q"], QS)],
            "margem_media": round(float(marg2.mean()), 3),
            "margem_quantis": [round(float(x), 2) for x in np.quantile(marg2, QS)],
            "via_pesquisas_lula_media": round(float(A["Q_pesquisas"].mean() * 100), 3),
            "via_transferencia_lula_media": round(float(A["Q_transf"].mean() * 100), 3),
            "p_lula_via_pesquisas": round(float((A["Q_pesquisas"] > 0.5).mean()), 4),
            "p_lula_via_transferencia": round(float((A["Q_transf"] > 0.5).mean()), 4),
            "teto_rejeicao_ativo": round(float(A["teto_rejeicao"].mean()), 4),
        }
        res["hist_margem_2t"] = _hist(marg2, -25, 25, 0.5)
        res["vies_sorteado"] = {"b1_media_pp": round(float(A["b1"].mean()), 3), "b1_dp_pp": round(float(A["b1"].std()), 3),
                                "b2_media_pp": round(float(A["b2"].mean()), 3), "b2_dp_pp": round(float(A["b2"].std()), 3)}
        res["consistencia"] = {
            "corr_erro_nacional_vs_agregado_ufs": round(float(np.corrcoef(A["e_p2"], M.logit(A["nat_p2_agregado"]))[0, 1]), 4)}
        ufl = []
        for u, r in base.ufs.iterrows():
            ufl.append({
                "uf": r.uf, "nome": r.nome, "regiao": r.regiao, "eleitores": int(r.eleitores),
                "lula_1t_media": round(sL[u] / n * 100, 2), "flavio_1t_media": round(sF[u] / n * 100, 2),
                "lula_1t_q": _q_hist(hL[u], [0.1, 0.5, 0.9]), "flavio_1t_q": _q_hist(hF[u], [0.1, 0.5, 0.9]),
                "p_lula_1o_1t": round(topL[u] / n, 4), "p_flavio_1o_1t": round(topF[u] / n, 4),
                "lula_2t_media": round(sq[u] / n * 100, 2), "lula_2t_q": _q_hist(hq[u], [0.1, 0.5, 0.9]),
                "lula_2t_q95": _q_hist(hq[u], [0.025, 0.975]),
                "p_lula_2t": round(winq[u] / n, 4),
                "ep_mc_p_lula_2t": round(math.sqrt(max(winq[u] / n * (1 - winq[u] / n), 1e-12) / n), 5),
                "lula_2t_2022": round(float(r.pt_2t_2022) * 100, 2),
            })
        res["ufs"] = ufl
        saida[vis] = res
    return saida, base, brutos


def series_pesquisas(prem, base: M.Base):
    df = M.carregar_pesquisas_nacionais_2026()[0]
    ev = pd.read_csv(M.DADOS / "eventos_2026.csv")
    d = df[df.campo_fim >= "2025-12-01"].sort_values("campo_fim").copy()
    validos = d["obs"].fillna("").str.contains("VOTOS VALIDOS", case=False)
    pesos = prem["agregacao.peso_extra_instituto"]
    pontos = []
    for r, val in zip(d.itertuples(), validos):
        pontos.append({"instituto": r.instituto, "data": r.campo_fim.strftime("%Y-%m-%d"),
                       "n": None if pd.isna(r.n) else int(r.n),
                       "lula": None if pd.isna(r.lula) else float(r.lula),
                       "flavio": None if pd.isna(r.flavio) else float(r.flavio),
                       "t2_lula": None if pd.isna(r.t2_lula) else float(r.t2_lula),
                       "t2_flavio": None if pd.isna(r.t2_flavio) else float(r.t2_flavio),
                       "base_1t": "validos" if val else "totais",
                       "sinalizada": r.instituto in pesos,
                       "fonte": r.fonte_url})
    # média móvel (votos totais): últimas pesquisas de cada instituto em 21 dias; linhas em válidos ficam fora do 1º turno
    media = []
    d1 = d[~validos]
    for dia in pd.date_range("2026-01-15", prem["data_referencia"], freq="3D").append(
            pd.DatetimeIndex([pd.Timestamp(prem["data_referencia"])])):
        lin = {"data": dia.strftime("%Y-%m-%d")}
        for col in ("lula", "flavio", "t2_lula", "t2_flavio"):
            src = d1 if col in ("lula", "flavio") else d
            j = src[(src.campo_fim <= dia) & (src.campo_fim > dia - pd.Timedelta(days=21)) & src[col].notna()]
            j = j.groupby("instituto").tail(1)
            if len(j) < 2:
                lin[col] = None
                continue
            w = np.sqrt(j["n"].fillna(2000).clip(upper=3000)) * np.exp(-(dia - j.campo_fim).dt.days / 7)
            lin[col] = round(float(np.sum(w * j[col]) / np.sum(w)), 2)
        media.append(lin)
    eventos = ev.fillna("").to_dict(orient="records")
    return {"pontos": pontos, "media": media, "eventos": eventos}


def _limpo(x):
    if isinstance(x, dict):
        return {str(k): _limpo(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_limpo(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def mercados():
    pm = pd.read_csv(M.DADOS / "polymarket_historico_diario.csv")
    pm = pm[pm.data >= "2025-12-01"]
    hist = [{"data": r["data"], "lula": r["election|Luiz Inácio Lula da Silva"],
             "flavio": r["election|Flávio Bolsonaro"],
             "decide_1t": r["election|YES"] if not pd.isna(r["election|YES"]) else None}
            for _, r in pm.iterrows()]
    snap = pd.read_csv(M.DADOS / "mercados_snapshot.csv").fillna("").to_dict(orient="records")
    return {"polymarket_historico": hist, "snapshot": snap,
            "fonte_historico": "https://clob.polymarket.com/prices-history (coleta 3/10/2026, research_notes/.../raw_mercados)"}


def premissas_lista(prem):
    out = []

    def walk(d, pref=""):
        for k, v in d.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict) and "valor" in v:
                out.append({"parametro": pref + k, "valor": v["valor"], "origem": v.get("origem", ""),
                            "nota": v.get("nota", ""), "fonte_url": v.get("fonte_url", "")})
            elif isinstance(v, dict):
                walk(v, pref + k + ".")
    walk(prem["_bruto"])
    return out


def validacao_json():
    p = M.DADOS / "backtest_saida.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def segmentos_json():
    p = M.DADOS / "segmentos_voto.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def institutos_tabela(base: M.Base, prem: dict):
    ex = prem["vies.exposicao_instituto"]
    pad = ex["_padrao"]
    insts = sorted(set(k for k in base.house1 if not k.startswith("_")) | set(k for k in base.house2 if not k.startswith("_")))
    pesos = prem["agregacao.peso_extra_instituto"]
    out = []
    for i in insts:
        h1 = base.house1.get(i, {}); h2 = base.house2.get(i, {})
        e = ex.get(i, pad)
        out.append({"instituto": i, "house_1t_pp": h1.get("h_pp"), "house_1t_dp_pp": h1.get("dp_pp"),
                    "house_2t_pp": h2.get("h_pp"), "house_2t_dp_pp": h2.get("dp_pp"),
                    "n_pesquisas": h1.get("n_pesquisas", h2.get("n_pesquisas")),
                    "exposicao": e["lambda"], "exposicao_dp": e["dp"], "metodo": e["metodo"],
                    "peso_extra": pesos.get(i, 1.0)})
    return out


def main():
    ap = argparse.ArgumentParser()
    prem = M.carregar_premissas()
    ap.add_argument("--n", type=int, default=prem["simulacao.n_simulacoes"])
    ap.add_argument("--seed", type=int, default=prem["simulacao.semente"])
    ap.add_argument("--lote", type=int, default=prem["simulacao.lote"])
    ap.add_argument("--saida", default=str(AQUI / "web" / "resultados.json"))
    a = ap.parse_args()

    t0 = time.perf_counter()
    base = M.construir_base_2026(prem)
    err = BT.erros_brutos(prem)
    vieses = vieses_2026(base, prem, err)
    base_alt = M.construir_base_2026(prem, "rejeicao")
    t1 = time.perf_counter()
    res, base, _ = executar(a.n, a.seed, a.lote, base=base, vieses=vieses, prem=prem)
    t2 = time.perf_counter()

    aj = base.e.ajuste_comp or {}
    meta = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_referencia": prem["data_referencia"],
        "n_simulacoes_por_visao": a.n, "n_simulacoes_por_cenario": a.n, "semente": a.seed, "lote": a.lote,
        "visoes": list(M.VISOES), "visao_principal": "calibrado",
        "tempo_base_s": round(t1 - t0, 2), "tempo_simulacao_s": round(t2 - t1, 2),
        "python": platform.python_version(), "numpy": np.__version__, "candidatos": M.CANDS,
    }
    entradas = {
        "p2_nacional": round(base.p2_nat * 100, 3), "p2_nacional_sem_house": round(base.agg1["media_bruta"] * 100, 3),
        "p2_nacional_indecisos_rejeicao": round(base_alt.p2_nat * 100, 3),
        "q_nacional": round(base.q_nat * 100, 3), "q_nacional_sem_house": round(base.agg2["media_bruta"] * 100, 3),
        "q_nacional_indecisos_rejeicao": round(base_alt.q_nat * 100, 3),
        "dp_consenso_pp": {"p2": round(base.agg1["dp_consenso_pp"], 3), "q": round(base.agg2["dp_consenso_pp"], 3)},
        "exposicao_media": {"p2": [round(base.agg1["lambda_medio"], 3), round(base.agg1["dp_lambda"], 3)],
                            "q": [round(base.agg2["lambda_medio"], 3), round(base.agg2["dp_lambda"], 3)]},
        "menores_nacional_validos": {c: round(float(v) * 100, 2) for c, v in zip(M.MENORES, base.m_nat)},
        "pesquisas_media_1t": base.agg1["tabela"], "pesquisas_media_2t": base.agg2["tabela"],
        "house_effects_1t_pp": {k: round(v["h_pp"], 2) for k, v in base.house1.items() if not k.startswith("_")},
        "house_effects_2t_pp": {k: round(v["h_pp"], 2) for k, v in base.house2.items() if not k.startswith("_")},
        "house_hiper": {"tau_1t_pp": base.house1["_tau_pp"], "ruido_1t_pp": base.house1["_se_pp"],
                        "tau_2t_pp": base.house2["_tau_pp"], "ruido_2t_pp": base.house2["_se_pp"]},
        "institutos": institutos_tabela(base, prem),
        "calibracao_ufs": base.desloc,
        "ajuste_comparecimento": {"br_1t_pp": aj.get("br1_pp"), "br_2t_pp": aj.get("br2_pp"),
                                  "dp_1t_pp": aj.get("dp1"), "dp_2t_pp": aj.get("dp2"),
                                  "aplicado_em": "visão calibrada"},
        "ufs_prior_demografico_2t": base.ufs.attrs.get("ufs_prior_demografico_2t", []),
        "detalhe_uf": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()} for d in base.detalhe_uf],
        "higiene": {"duplicatas_removidas": base.e.notas,
                    "linhas_sem_indecisos_a_alocar": [f"{r.instituto} {r.campo_fim:%Y-%m-%d}" for r in
                                          base.pesquisas[base.pesquisas.base_validos].itertuples()],
                    "sinalizadas": prem["agregacao.peso_extra_instituto"]},
        "vies": {v: {"b1_pp": list(vieses[v]["b1"]), "b2_pp": list(vieses[v]["b2"]), "muT_log": list(vieses[v]["muT"]),
                     "residuos": vieses[v]["residuos"]} for v in M.VISOES},
        "erros_historicos": {int(k): {kk: (None if vv is None else round(float(vv), 4)) for kk, vv in d.items()
                                      if not kk.startswith("base")} for k, d in err.items()},
    }
    sens = [{"visao": v, "rotulo": VISAO_DESC[v], "lula_vence": res[v]["prob"]["lula_vence"]["p"],
             "flavio_vence": res[v]["prob"]["flavio_vence"]["p"], "decide_1t": res[v]["prob"]["decide_1t"]["p"],
             "lula_1o_no_1t": res[v]["prob"]["lula_1o_no_1t"]["p"],
             "lula_2t_media": res[v]["segundo_turno"]["lula_media"]} for v in M.VISOES]
    out = {"meta": meta, "entradas": entradas, "visoes": res, "cenarios": res, "sensibilidade": sens,
           "pesquisas": series_pesquisas(prem, base), "mercados": mercados(),
           "validacao": validacao_json(), "segmentos": segmentos_json(),
           "premissas": premissas_lista(prem)}
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.saida).write_text(json.dumps(_limpo(out), ensure_ascii=False, default=str, allow_nan=False), encoding="utf-8")

    print(f"N={a.n:,} por visão | seed={a.seed} | base+priors {t1 - t0:.2f}s | simulação {t2 - t1:.1f}s")
    for v in M.VISOES:
        print(f"  viés {v}: b1={vieses[v]['b1']} b2={vieses[v]['b2']} muT={vieses[v]['muT']}")
    for c, r in res.items():
        p = r["prob"]
        print(f"[{c}] Lula {p['lula_vence']['p']:.3f} | Flávio {p['flavio_vence']['p']:.3f} | "
              f"decide 1T {p['decide_1t']['p']:.3f} | Lula 1º no 1T {p['lula_1o_no_1t']['p']:.3f} | "
              f"1T Lula {r['primeiro_turno']['Lula']['media']:.1f} Flávio {r['primeiro_turno']['Flavio']['media']:.1f} "
              f"3ª via {r['primeiro_turno']['terceira_via']['media']:.1f} | "
              f"2T Lula {r['segundo_turno']['lula_media']:.1f} (pesq {r['segundo_turno']['via_pesquisas_lula_media']:.1f}, "
              f"transf {r['segundo_turno']['via_transferencia_lula_media']:.1f})")
    print("gravado:", a.saida)


if __name__ == "__main__":
    main()
