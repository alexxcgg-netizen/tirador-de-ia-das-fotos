"""Roda o modelo alternativo do 2º turno e grava ``resultados_alt_2t.json``.

    python modelo_alternativo/rodar_alt_2t.py            # 500 mil simulações
    python modelo_alternativo/rodar_alt_2t.py --rapido   # 50 mil (teste)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo_alt_2t as M  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO_PRINCIPAL = {"lula_media": 47.3, "p_lula": 0.15,
                    "fonte": "simulador principal, informado em 5/10/2026 (recalibração em curso)"}


def _hash(caminho):
    return hashlib.sha256(open(caminho, "rb").read()).hexdigest()[:16]


def _ufs(sh, reg):
    out = {}
    for j, uf in enumerate(reg):
        d = M.resumo_dist(sh[:, j], 1)
        out[uf] = dict(media=d["media"], p10=d["p10"], p90=d["p90"],
                       p_lula=round(float(np.mean(sh[:, j] > .5)), 3))
    return out


def _cenario(nac, sh, reg):
    return dict(nacional=M.resumo_dist(nac), p_lula=round(float(np.mean(nac > .5)), 4),
                p_margem_menor_2pp=round(float(np.mean(np.abs(nac - .5) < .01)), 4),
                ufs_lula_esperadas=round(float(np.mean(np.sum(sh > .5, axis=1))), 2),
                ufs=_ufs(sh, reg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    n = a.n or (50_000 if a.rapido else 500_000)
    n_bt = 20_000 if a.rapido else 100_000
    t0 = time.time()

    hist = M.carregar_historico()
    dados = M.carregar_1t_2026()

    # ---- principal (regressão empírica)
    r = M.prever_2026(n=n, hist=hist, dados=dados)
    princ = _cenario(r["nac"], r["sh"], r["reg"])
    real = M.avaliacao_1t()["real"]["nacional"]
    x_br = real["Lula"] / (real["Lula"] + real["Flavio"])

    # ---- backtest
    bt = M.backtest(hist, n=n_bt)
    br = hist[hist.uf == "BR"].set_index("ano")
    ingenuo = {int(a): round(100 * float(br.loc[a, "x"] - br.loc[a, "y"]), 2) for a in M.ANOS}
    e_ing = np.array([ingenuo[a] for a in M.ANOS if a >= 2006])

    # ---- sensibilidade da especificação
    sens = {}
    for spec in M.ESPECIFICACOES:
        rs = r if spec == "principal" else M.prever_2026(n=100_000, hist=hist, dados=dados, spec=spec)
        bts = bt if spec == "principal" else M.backtest(hist, n=20_000, spec=spec)
        sens[spec] = dict(lula_media=round(100 * float(np.mean(rs["nac"])), 2),
                          p_lula=round(float(np.mean(rs["nac"] > .5)), 3),
                          backtest=M.resumir_backtest(bts))

    # ---- variante: mistura com pesquisas corrigidas pelo erro do 1T
    pq = M.pesquisas_2t_corrigidas()
    bt_pq = M.backtest_pesquisas_hist(hist=hist)
    media_p = float(pq.lula_2p_corrigido.mean()) / 100
    rmse_hist = float(np.sqrt(np.mean([b["erro_corrigido"] ** 2 for b in bt_pq]))) / 100
    sd_p = max(rmse_hist, 0.02)
    nac_b, wp, m_b, s_b = M.misturar_pesquisas(r["nac"], media_p, sd_p)
    sh_b = M.ajustar_ufs_ao_nacional(r["sh"], r["nac"], nac_b)
    rng = np.random.default_rng(7)
    so_pq = rng.normal(media_p, sd_p, n)

    out = dict(
        meta=dict(
            gerado_em=time.strftime("%Y-%m-%d %H:%M:%S"), n_simulacoes=n,
            tempo_s=None,
            dados={os.path.relpath(p, M.RAIZ): _hash(p) for p in [
                M.ARQ_HIST, os.path.join(M.DIR_DADOS, "avaliacao_1t.json"),
                os.path.join(M.DIR_DADOS, "pesquisas_nacionais.csv"),
                os.path.join(M.DIR_DADOS, "backtest_pesquisas_nacionais.csv")]},
            apuracao_1t_pct=M.avaliacao_1t()["real"]["pst_nacional"],
            metodo=("logit(y)=b0+b1*logit(x)+b2*t por UF, 2002-2022, MQP sqrt(votos); "
                    "incerteza: resíduos LOO por eleição (efeito nacional + vetor estadual), "
                    "bootstrap suavizado; nacional ponderado por votos válidos esperados no 2T"),
        ),
        entrada_1t_2026=dict(lula_validos=real["Lula"], flavio_validos=real["Flavio"],
                             terceiros_validos=round(100 - real["Lula"] - real["Flavio"], 3),
                             lula_2p_1t=round(100 * x_br, 2)),
        coeficientes=dict(zip(["b0", "b1_logit_x", "b2_terceiros"],
                              [round(float(b), 4) for b in r["beta"]])),
        residuos_loo_nacionais_pp={int(k): round(100 * (v["pred_nac"] - v["real_nac"]), 2)
                                   for k, v in r["loo"].items()},
        principal_regressao=princ,
        variante_pesquisas=dict(
            descricao=("Média simples da última pesquisa de 2T (antes do 1T) de cada instituto, "
                       "corrigida pelo erro de margem do próprio instituto no 1T de 2026; "
                       "dp = RMSE do mesmo procedimento em 2018/2022 (piso 2 p.p.); "
                       "combinada com a regressão por inverso da variância"),
            institutos=pq.to_dict(orient="records"),
            media_corrigida=round(100 * media_p, 2),
            media_bruta=round(float(pq.lula_2p_bruto.mean()), 2),
            dp_pesquisas=round(100 * sd_p, 2),
            backtest_hist=bt_pq,
            so_pesquisas=dict(nacional=M.resumo_dist(so_pq),
                              p_lula=round(float(np.mean(so_pq > .5)), 4)),
            peso_pesquisas=round(float(wp), 3),
            mistura=_cenario(nac_b, sh_b, r["reg"]),
        ),
        sensibilidade_especificacao=sens,
        backtest=dict(por_ano=bt, resumo_2006_2022=M.resumir_backtest(bt),
                      resumo_2002_2022=M.resumir_backtest(bt, anos=tuple(M.ANOS)),
                      ingenuo_x_igual_y=dict(
                          erro_por_ano=ingenuo,
                          rmse_2006_2022=round(float(np.sqrt(np.mean(e_ing ** 2))), 2),
                          previsao_2026=round(100 * x_br, 2))),
        comparacao_modelo_principal=dict(
            principal=MODELO_PRINCIPAL,
            alt_regressao=dict(lula_media=princ["nacional"]["media"], p_lula=princ["p_lula"]),
            alt_mistura=dict(lula_media=round(100 * float(np.mean(nac_b)), 2),
                             p_lula=round(float(np.mean(nac_b > .5)), 4)),
        ),
    )
    out["meta"]["tempo_s"] = round(time.time() - t0, 1)
    with open(os.path.join(AQUI, "resultados_alt_2t.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)
    c = out["comparacao_modelo_principal"]
    print(json.dumps({k: out[k] for k in ["entrada_1t_2026", "coeficientes", "residuos_loo_nacionais_pp"]},
                     ensure_ascii=False))
    print("regressão:", princ["nacional"], "P(Lula)", princ["p_lula"])
    print("pesquisas:", out["variante_pesquisas"]["media_corrigida"], "dp", 100 * sd_p,
          "peso", round(wp, 3), "mistura", c["alt_mistura"],
          out["variante_pesquisas"]["mistura"]["nacional"])
    print("backtest:", out["backtest"]["resumo_2006_2022"], out["backtest"]["ingenuo_x_igual_y"])
    print("pesquisas hist:", bt_pq)
    print("sens:", {k: (v["lula_media"], v["p_lula"]) for k, v in sens.items()})
    print("tempo", out["meta"]["tempo_s"])


if __name__ == "__main__":
    main()
