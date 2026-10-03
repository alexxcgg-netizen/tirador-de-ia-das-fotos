"""Roda o modelo alternativo: ajuste 2026, erros históricos, 500 mil simulações,
backtest 2018/2022 (deixa-uma-eleição-de-fora) e grava resultados_alt.json.

Uso:  python modelo_alternativo/rodar_alt.py [--sims 500000] [--iter 4000] [--rapido]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo_alt as M  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
SEMENTE = 20261004


def _limpo(x):
    """Converte para tipos JSON e remove chaves internas (prefixo _)."""
    if isinstance(x, dict):
        return {str(k): _limpo(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, (list, tuple)):
        return [_limpo(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if np.isnan(x) else round(float(x), 5)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, np.ndarray):
        return _limpo(x.tolist())
    return x


def renomear(sim, a="lula", b="flavio"):
    """Troca rótulos genéricos pt/opp pelos nomes de 2026."""
    def tr(s):
        return s.replace("pt_", a + "_").replace("opp_", b + "_").replace("_pt", "_" + a).replace("_opp", "_" + b)
    out = {"prob": {tr(k): v for k, v in sim["prob"].items()},
           "ep_mc": {tr(k): v for k, v in sim["ep_mc"].items()},
           "quantis_pct_validos": {tr(k): v for k, v in sim["quantis"].items()},
           "ufs": {u: {tr(k): v for k, v in d.items()} for u, d in sim["ufs"].items()}}
    return out


def resumo_agregado(dados, aj):
    est = {k: float(np.mean(a["m"])) for k, a in aj.items()}
    dem = M.expit(est["z2"])
    p2 = M.expit(est["z1"])
    lula, flavio = (1 - dem) * p2, (1 - dem) * (1 - p2)
    opp_ref, resid = M.composicao_ref(aj, dados.menores)
    men = {c: opp_ref * np.exp(est["m_" + c]) for c in dados.menores}
    casas = {}
    for comp, fator in [("z1", 25.0), ("zq", 25.0)]:
        a = aj[comp]
        casas[comp] = {c: {"pp": round(h * fator, 2), "dp_pp": round(s * fator, 2)}
                       for c, h, s in zip(a["casas"], a["h_media"], a["h_dp"])}
    tend = {}
    for comp in ["z1", "zq"]:
        dias, m, v = aj[comp]["tendencia"]
        datas = [dados.t0 + pd.Timedelta(days=int(d)) for d in dias]
        sel = list(range(0, len(dias), 7))
        if sel[-1] != len(dias) - 1:
            sel.append(len(dias) - 1)
        tend[comp] = [{"data": datas[i].strftime("%Y-%m-%d"),
                       "lula_pct": round(100 * float(M.expit(m[i])), 2),
                       "ic80": [round(100 * float(M.expit(m[i] - 1.2816 * np.sqrt(v[i]))), 2),
                                round(100 * float(M.expit(m[i] + 1.2816 * np.sqrt(v[i]))), 2)]}
                      for i in sel]
    return {
        "data_alvo": dados.alvo.strftime("%Y-%m-%d"),
        "n_pesquisas_1t": int(len(dados.comps["z1"])),
        "n_pesquisas_2t": int(len(dados.comps["zq"])),
        "lula_bipartidario_1t_pct": 100 * p2,
        "lula_validos_1t_pct": 100 * lula,
        "flavio_validos_1t_pct": 100 * flavio,
        "demais_validos_1t_pct": 100 * dem,
        "menores_validos_1t_pct": {c: 100 * v for c, v in men.items()},
        "nao_listados_validos_1t_pct": 100 * resid,
        "lula_2t_pct_validos": 100 * float(M.expit(est["zq"])),
        "dp_posterior_logit": {k: float(np.sqrt(np.mean(a["v"]) + np.var(a["m"]))) for k, a in aj.items()},
        "hiperparametros_mediana": {k: a["hiper_mediana"] for k, a in aj.items()},
        "taxa_aceitacao_mcmc": {k: a["aceitacao"] for k, a in aj.items()},
        "efeitos_instituto_pp_aprox": casas,
        "tendencia_semanal": tend,
    }


def instantaneo_dados():
    """Identifica a versão dos CSVs lidos (o simulador principal os atualiza)."""
    import hashlib
    out = {}
    for nome in ["pesquisas_nacionais.csv", "backtest_pesquisas_nacionais.csv",
                 "resultados_uf_2002_2022.csv"]:
        cam = os.path.join(M.DIR_DADOS, nome)
        with open(cam, "rb") as f:
            b = f.read()
        out[nome] = {"sha256_12": hashlib.sha256(b).hexdigest()[:12],
                     "linhas": b.count(b"\n") - 1}
    return out


def base_uf(ano_base):
    r = M.resultados_uf()
    return {1: r[(ano_base, 1)], 2: r[(ano_base, 2)]}


def comparar_principal():
    """Lê (sem alterar) o resultado do simulador principal, se existir."""
    cam = os.path.join(M.RAIZ, "simulador", "web", "resultados.json")
    try:
        with open(cam) as f:
            d = json.load(f)
        out = {"arquivo": "simulador/web/resultados.json", "gerado_em": d["meta"].get("gerado_em"),
               "visoes": {}}
        for nome, v in d.get("visoes", {}).items():
            p = v.get("prob", {})
            g = lambda k: (p.get(k) or {}).get("p")  # noqa: E731
            out["visoes"][nome] = {"lula_vence": g("lula_vence"), "flavio_vence": g("flavio_vence"),
                                   "decide_1t": g("decide_1t"),
                                   "segundo_turno_lula_flavio": g("segundo_turno_lula_flavio")}
        return out
    except Exception as exc:  # pragma: no cover - depende do outro módulo
        return {"erro": f"nao foi possivel ler: {exc}"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=500_000)
    ap.add_argument("--iter", type=int, default=4000)
    ap.add_argument("--burn", type=int, default=1500)
    ap.add_argument("--saida", default=os.path.join(AQUI, "resultados_alt.json"))
    ap.add_argument("--rapido", action="store_true", help="poucas iterações/simulações (teste)")
    a = ap.parse_args(argv)
    if a.rapido:
        a.sims, a.iter, a.burn = 20_000, 600, 200
    t_ini = time.time()

    # 1) ajustes (2026 e históricos, cada um só com pesquisas até a véspera do 1º turno)
    dados = {2026: M.carregar_2026()}
    for ano in M.ANOS_HIST:
        dados[ano] = M.carregar_historico(ano)
    ajustes = {ano: M.ajustar_eleicao(d, n_iter=a.iter, burn=a.burn, seed=SEMENTE + ano)
               for ano, d in dados.items()}
    t_aj = time.time() - t_ini

    # 2) erros históricos da média final do modelo
    erros = {ano: M.erros_eleicao(ano, dados[ano], ajustes[ano]) for ano in M.ANOS_HIST}
    pool = M.montar_pool([erros[ano] for ano in M.ANOS_HIST])

    # 3) 2026
    V1, p1 = M.desvios_estaduais(1)
    V2, p2 = M.desvios_estaduais(2)
    t_sim = time.time()
    cen = {}
    for i, var in enumerate(["neutro", "historico"]):
        sim = M.simular(dados[2026], ajustes[2026], pool, base_uf(2022), V1, V2,
                        n_sims=a.sims, variante=var, seed=SEMENTE + i)
        cen[var] = renomear(sim)
    t_sim = time.time() - t_sim

    # sensibilidade (neutro, 100 mil simulações): pool sem 2014; bootstrap sem suavização
    sens = {}
    for rot, pl in [("pool_sem_2014", M.montar_pool([erros[2018], erros[2022]])),
                    ("bootstrap_puro_sem_nucleo", M.montar_pool([erros[x] for x in M.ANOS_HIST],
                                                                suavizar=False))]:
        for var in ["neutro", "historico"]:
            sim = M.simular(dados[2026], ajustes[2026], pl, base_uf(2022), V1, V2,
                            n_sims=min(a.sims, 100_000), variante=var, seed=SEMENTE + 7)
            sens[f"{rot}/{var}"] = renomear(sim)["prob"]

    # 4) backtest 2018 e 2022 (erro deixa-uma-eleição-de-fora; desvios UF sem pares que tocam o ano)
    bt = {}
    t_bt = time.time()
    for ano in [2018, 2022]:
        pool_loo = M.montar_pool([erros[x] for x in M.ANOS_HIST if x != ano])
        V1b, _ = M.desvios_estaduais(1, excluir_anos={ano})
        V2b, _ = M.desvios_estaduais(2, excluir_anos={ano})
        bt[ano] = {}
        for i, var in enumerate(["neutro", "historico"]):
            sim = M.simular(dados[ano], ajustes[ano], pool_loo, base_uf(ano - 4), V1b, V2b,
                            n_sims=a.sims, variante=var, seed=SEMENTE + ano + i)
            bt[ano][var] = M.avaliar(sim, ano, M.resultados_uf())
            bt[ano][var]["pool_anos"] = pool_loo.anos
    resumo_bt = M.resumir_backtest(bt)
    t_bt = time.time() - t_bt

    saida = {
        "meta": {
            "modelo": "modelo_alternativo (passeio aleatório bayesiano + bootstrap empírico + swing uniforme)",
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "data_referencia": "2026-10-03",
            "eleicao_1t": M.ELEICOES[2026]["t1"], "eleicao_2t": M.ELEICOES[2026]["t2"],
            "n_simulacoes_por_variante": a.sims, "mcmc_iter": a.iter, "mcmc_burn": a.burn,
            "semente": SEMENTE,
            "tempo_s": {"ajustes_mcmc": round(t_aj, 1), "simulacao_2026": round(t_sim, 1),
                        "backtest": round(t_bt, 1), "total": round(time.time() - t_ini, 1)},
            "python": platform.python_version(), "numpy": np.__version__,
            "dados": instantaneo_dados(),
            "variante_principal": "neutro",
            "variantes": {
                "neutro": "erro partidário histórico com sinal sorteado (±): magnitude empírica, direção agnóstica",
                "historico": "erro com o sinal observado em 2014/2018/2022 (pesquisas superestimaram o PT)"},
        },
        "agregado_2026": resumo_agregado(dados[2026], ajustes[2026]),
        "erros_historicos": {
            str(ano): {"erro_logit": e["erro"], "resultado": e["resultado"],
                       "estimativa_modelo_vespera": {
                           "pt_bipartidario_1t_pct": 100 * float(M.expit(np.mean(ajustes[ano]["z1"]["m"]))),
                           "demais_1t_pct": 100 * float(M.expit(np.mean(ajustes[ano]["z2"]["m"]))),
                           "pt_2t_pct": (100 * float(M.expit(np.mean(ajustes[ano]["zq"]["m"])))
                                         if "zq" in ajustes[ano] else None)},
                       "n_institutos_nucleo": e["n_institutos_finais"]}
            for ano, e in erros.items()},
        "pool_erros": {"anos": pool.anos, "banda_h": pool.h, "dp_alvo_logit": pool.sigma,
                       "media_com_sinal_logit": pool.mu,
                       "n_nucleo_1t": int(len(pool.K12)), "n_nucleo_2t": int(len(pool.Kq)),
                       "pares_desvio_uf": p2},
        "cenarios_2026": cen,
        "sensibilidade_2026": sens,
        "backtest": {str(k): v for k, v in bt.items()},
        "backtest_resumo": resumo_bt,
        "comparacao_modelo_principal": comparar_principal(),
    }
    with open(a.saida, "w") as f:
        json.dump(_limpo(saida), f, ensure_ascii=False, indent=1)
    imprimir(saida)
    return saida


def imprimir(s):
    for var, c in s["cenarios_2026"].items():
        p = c["prob"]
        print(f"[{var}] Lula vence {p['lula_vence']:.3f} | Flavio vence {p['flavio_vence']:.3f} | "
              f"decide 1T {p['decide_1t']:.3f} | top2 Lula-Flavio {p['top2_lula_flavio']:.4f} | ha 2T L x F {p['ha_segundo_turno_lula_x_flavio']:.3f} | "
              f"Lula 1o no 1T {p['lula_1o_no_1t']:.3f}")
    for k, v in s["backtest_resumo"].items():
        print("backtest", k, v)
    print("tempo", s["meta"]["tempo_s"])


if __name__ == "__main__":
    main()
