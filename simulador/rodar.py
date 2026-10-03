"""Roda o simulador e grava web/resultados.json.

Uso:
    python simulador/rodar.py                 # 500.000 simulações por cenário (premissas.json)
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

CENARIOS = {"neutro": "Neutro (pesquisas sem viés sistemático)",
            "historico": "Viés histórico (erro anti-PT de 2014/2018/2022)"}
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


def executar(n: int, seed: int, lote: int, cenarios=("neutro", "historico"), base=None, guardar_brutos=False):
    base = base or M.construir_base()
    U = len(base.ufs)
    saida = {}
    brutos = {}
    for ci, cen in enumerate(cenarios):
        rng = np.random.default_rng([seed, ci])
        acc = {k: [] for k in ("nat1", "Q", "Q_pesquisas", "Q_transf", "primeiro", "segundo",
                               "venceu_1t", "par_lf", "vencedor", "e_p2", "nat_p2_agregado")}
        hL = np.zeros((U, NB), np.int64); hF = np.zeros((U, NB), np.int64); hq = np.zeros((U, NB), np.int64)
        topL = np.zeros(U); topF = np.zeros(U); winq = np.zeros(U)
        sL = np.zeros(U); sF = np.zeros(U); sq = np.zeros(U)
        feito = 0
        while feito < n:
            B = min(lote, n - feito)
            r = M.simular_lote(base, cen, B, rng)
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
            brutos[cen] = A
        nat1 = A["nat1"]
        res = {"descricao": CENARIOS.get(cen, cen), "n": n}
        # probabilidades
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
            "lula_vence_2t_se_houver": _p((A["Q"] > 0.5).mean(), n),
        }
        res["prob_top2"] = {c: _p(((A["primeiro"] == k) | (A["segundo"] == k)).mean(), n)
                            for k, c in enumerate(M.CANDS)}
        res["prob_1o_lugar"] = {c: _p((A["primeiro"] == k).mean(), n) for k, c in enumerate(M.CANDS)}
        # distribuições nacionais
        res["primeiro_turno"] = {c: {"media": round(float(nat1[:, k].mean() * 100), 3),
                                     "quantis": [round(float(x) * 100, 2) for x in np.quantile(nat1[:, k], QS)]}
                                 for k, c in enumerate(M.CANDS)}
        res["primeiro_turno"]["margem_lula_flavio"] = {
            "media": round(float((nat1[:, 0] - nat1[:, 1]).mean() * 100), 3),
            "quantis": [round(float(x) * 100, 2) for x in np.quantile(nat1[:, 0] - nat1[:, 1], QS)]}
        res["hist_1t"] = {c: _hist(nat1[:, k] * 100, 20, 65, 0.25) for k, c in enumerate(M.CANDS[:2])}
        res["hist_1t"]["Menores"] = _hist((1 - nat1[:, 0] - nat1[:, 1]) * 100, 0, 25, 0.25)
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
        }
        res["hist_margem_2t"] = _hist(marg2, -25, 25, 0.5)
        res["consistencia"] = {
            "corr_erro_nacional_vs_agregado_ufs": round(float(np.corrcoef(A["e_p2"], M.logit(A["nat_p2_agregado"]))[0, 1]), 4)}
        # UFs
        ufl = []
        for u, r in base.ufs.iterrows():
            ufl.append({
                "uf": r.uf, "nome": r.nome, "regiao": r.regiao, "eleitores": int(r.eleitores_2026),
                "lula_1t_media": round(sL[u] / n * 100, 2), "flavio_1t_media": round(sF[u] / n * 100, 2),
                "lula_1t_q": _q_hist(hL[u], [0.1, 0.5, 0.9]), "flavio_1t_q": _q_hist(hF[u], [0.1, 0.5, 0.9]),
                "p_lula_1o_1t": round(topL[u] / n, 4), "p_flavio_1o_1t": round(topF[u] / n, 4),
                "lula_2t_media": round(sq[u] / n * 100, 2), "lula_2t_q": _q_hist(hq[u], [0.1, 0.5, 0.9]),
                "p_lula_2t": round(winq[u] / n, 4),
                "ep_mc_p_lula_2t": round(math.sqrt(max(winq[u] / n * (1 - winq[u] / n), 1e-12) / n), 5),
                "lula_2t_2022": round(float(r.pt_2t_2022) * 100, 2),
            })
        res["ufs"] = ufl
        saida[cen] = res
    return saida, base, brutos


def series_pesquisas(prem):
    df = M.carregar_pesquisas_nacionais()
    ev = pd.read_csv(M.DADOS / "eventos_2026.csv")
    d = df[df.campo_fim >= "2025-12-01"].sort_values("campo_fim")
    pontos = []
    for r in d.itertuples():
        pontos.append({"instituto": r.instituto, "data": r.campo_fim.strftime("%Y-%m-%d"),
                       "n": None if pd.isna(r.n) else int(r.n),
                       "lula": None if pd.isna(r.lula) else float(r.lula),
                       "flavio": None if pd.isna(r.flavio) else float(r.flavio),
                       "t2_lula": None if pd.isna(r.t2_lula) else float(r.t2_lula),
                       "t2_flavio": None if pd.isna(r.t2_flavio) else float(r.t2_flavio),
                       "fonte": r.fonte_url})
    # média móvel: últimas pesquisas de cada instituto em 14 dias, peso sqrt(n)*exp(-dias/7)
    media = []
    for dia in pd.date_range("2026-01-15", prem["data_referencia"], freq="3D").append(
            pd.DatetimeIndex([pd.Timestamp(prem["data_referencia"])])):
        lin = {"data": dia.strftime("%Y-%m-%d")}
        for col in ("lula", "flavio", "t2_lula", "t2_flavio"):
            j = d[(d.campo_fim <= dia) & (d.campo_fim > dia - pd.Timedelta(days=21)) & d[col].notna()]
            j = j.groupby("instituto").tail(1)
            if len(j) < 2:
                lin[col] = None
                continue
            w = np.sqrt(j["n"].fillna(2000).clip(upper=3000)) * np.exp(-(dia - j.campo_fim).dt.days / 7)
            lin[col] = round(float(np.sum(w * j[col]) / np.sum(w)), 2)
        media.append(lin)
    eventos = ev.to_dict(orient="records")
    return {"pontos": pontos, "media": media, "eventos": eventos}


def _limpo(x):
    """Troca NaN/inf por None (JSON válido)."""
    if isinstance(x, dict):
        return {k: _limpo(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_limpo(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, np.integer):
        return int(x)
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


def main():
    ap = argparse.ArgumentParser()
    prem = M.carregar_premissas()
    ap.add_argument("--n", type=int, default=prem["simulacao.n_simulacoes"])
    ap.add_argument("--seed", type=int, default=prem["simulacao.semente"])
    ap.add_argument("--lote", type=int, default=prem["simulacao.lote"])
    ap.add_argument("--saida", default=str(AQUI / "web" / "resultados.json"))
    a = ap.parse_args()

    t0 = time.perf_counter()
    base = M.construir_base(prem)
    t1 = time.perf_counter()
    res, base, _ = executar(a.n, a.seed, a.lote, base=base)
    t2 = time.perf_counter()

    # mistura 50/50 dos cenários (exata para probabilidades)
    mist = {k: round((res["neutro"]["prob"][k]["p"] + res["historico"]["prob"][k]["p"]) / 2, 5)
            for k in res["neutro"]["prob"]}

    meta = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_referencia": prem["data_referencia"],
        "n_simulacoes_por_cenario": a.n, "semente": a.seed, "lote": a.lote,
        "tempo_base_s": round(t1 - t0, 2), "tempo_simulacao_s": round(t2 - t1, 2),
        "python": platform.python_version(), "numpy": np.__version__,
        "candidatos": M.CANDS,
    }
    entradas = {
        "p2_nacional": round(base.p2_nat * 100, 3), "p2_nacional_sem_house": round(base.p2_bruta * 100, 3),
        "q_nacional": round(base.q_nat * 100, 3), "q_nacional_sem_house": round(base.q_bruta * 100, 3),
        "menores_nacional_validos": {k: round(v * 100, 2) for k, v in base.menores_nat.items()},
        "pesquisas_media_1t": base.tabela_1t, "pesquisas_media_2t": base.tabela_2t,
        "house_effects_1t_pp": {k: round(v["h_pp"], 2) for k, v in base.house_1t.items()},
        "house_effects_2t_pp": {k: round(v["h_pp"], 2) for k, v in base.house_2t.items()},
        "calibracao_ufs": base.desloc_calibracao,
        "detalhe_uf": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()} for d in base.detalhe_uf],
    }
    out = {"meta": meta, "entradas": entradas, "cenarios": res, "mistura_50_50": mist,
           "pesquisas": series_pesquisas(prem), "mercados": mercados(),
           "premissas": premissas_lista(prem)}
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.saida).write_text(json.dumps(_limpo(out), ensure_ascii=False, default=str, allow_nan=False), encoding="utf-8")

    print(f"N={a.n:,} por cenário | seed={a.seed} | base {t1 - t0:.2f}s | simulação {t2 - t1:.1f}s")
    for c, r in res.items():
        p = r["prob"]
        print(f"[{c}] Lula {p['lula_vence']['p']:.3f} | Flávio {p['flavio_vence']['p']:.3f} | "
              f"decide 1T {p['decide_1t']['p']:.3f} | 2T L x F {p['segundo_turno_lula_flavio']['p']:.3f} | "
              f"1T Lula {r['primeiro_turno']['Lula']['media']:.1f} Flávio {r['primeiro_turno']['Flavio']['media']:.1f} | "
              f"2T Lula {r['segundo_turno']['lula_media']:.1f} (pesq {r['segundo_turno']['via_pesquisas_lula_media']:.1f}, "
              f"transf {r['segundo_turno']['via_transferencia_lula_media']:.1f})")
    print("gravado:", a.saida)


if __name__ == "__main__":
    main()
