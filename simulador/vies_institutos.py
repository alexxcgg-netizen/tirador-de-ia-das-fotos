"""Erro de cada instituto no 1º turno -> correção das pesquisas de 2º turno, e viés da indústria 1T -> 2T.

Lição do 1º turno de 2026: 11 dos 14 institutos com pesquisa na última semana erraram a favor de Lula; a média das
pesquisas errou a margem em ~+3 p.p. Duas perguntas, respondidas com dados (2014, 2018, 2022 e o 1º turno de 2026):

1. **Correção por instituto.** O erro do instituto p no 1º turno (fatia bipartidária PT/(PT+adversário) da(s)
   pesquisa(s) da última semana menos o resultado) é decomposto em média da indústria + desvio do instituto, com
   *partial pooling* (efeitos aleatórios, DerSimonian-Laird):

       e_p ~ N(theta_p, v_p),   theta_p ~ N(mu, tau²),   v_p = (amostral_p + dp_intra²) / k_p

   (k_p = pesquisas do instituto na janela; amostral pela fatia e pelo n dos que escolheram um dos dois). A média
   posterior theta_p = mu + B_p (e_p − mu), B_p = tau² / (tau² + v_p), com dp posterior. Variantes aplicadas às
   pesquisas de 2º turno do mesmo instituto (antes e depois do 1º turno): ``nenhuma``; ``relativa`` (só o desvio
   do instituto, B_p (e_p − mu): corrige quem errou mais ou menos que a indústria e deixa o nível da indústria para
   o termo de viés); ``industria`` (só mu, igual para todos); ``plena`` (mu + desvio). Instituto sem pesquisa de 1º
   turno na janela: desvio 0 (dp tau) e, nas variantes com nível, mu.

   ``backtest_correcao`` aplica cada variante em 2014, 2018 e 2022 (lean estimado só com o 1º turno do próprio ano,
   que é o que se sabe na noite da apuração) e mede o erro da média de pesquisas de 2º turno (o agregador do
   modelo, com house effects e recência) contra o 2º turno real, antes do 1º turno (pré-1T) e na véspera do 2º
   turno (pós-1T), além do erro de cada pesquisa da última semana.

2. **Viés da indústria 1T -> 2T.** ``vies_industria`` junta o erro do agregador no 1º turno (fatia bipartidária do
   PT) de 2014, 2018, 2022 e 2026, reestima a escala do viés persistente da indústria (tau0, máxima verossimilhança
   marginal) e a relação entre o erro do 1º turno e o erro da projeção do 2º turno de cada ano (regressão bayesiana
   com prior neutro, centrado em zero); devolve o termo de viés do 2º turno de 2026 condicionado ao erro do 1º turno
   de 2026.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

import modelo as M

PARAM_VI = {
    "janela_1t_dias": {"valor": 7, "origem": "inferencia",
                       "nota": "Pesquisas de 1º turno com fim de campo nos 7 dias antes da eleição (a mesma janela da "
                               "avaliação do 1º turno, AVALIACAO_1T.md)."},
    "so_ultima_1t": {"valor": True, "origem": "backtest",
                     "nota": "Só a última pesquisa de 1º turno de cada instituto na janela (pesquisas mais antigas da "
                             "janela misturam viés com movimento real da última semana, ex.: Aécio em 2014). "
                             "Alternativa (todas da janela, ponderadas por n) em backtest_correcao(so_ultima=False)."},
    "dp_intra_pp": {"valor": 1.0, "origem": "inferencia",
                    "nota": "Erro não amostral de uma pesquisa em torno do viés do próprio instituto (p.p. da fatia "
                            "bipartidária); soma-se à variância amostral."},
    "n_padrao": {"valor": 2000, "origem": "inferencia", "nota": "Amostra quando a fonte não informa n (como no agregador)."},
    "n_teto": {"valor": 5000, "origem": "inferencia", "nota": "Teto de n (como em house_effects_hier)."},
}


# ================================================================ 1) erro de cada instituto no 1º turno
def erros_1t(pesq: pd.DataFrame, real_pp: float, data_1t, janela: int | None = None,
             so_ultima: bool | None = None) -> pd.DataFrame:
    """pesq: instituto, campo_fim, n, a, b (intenções de voto do PT e do adversário no 1º turno, qualquer base).
    real_pp: fatia bipartidária real do PT no 1º turno (p.p.). Uma linha por instituto com pesquisa na janela:
    erro médio (ponderado por n), número de pesquisas, n total e variância do erro (p.p.²)."""
    janela = PARAM_VI["janela_1t_dias"]["valor"] if janela is None else janela
    t1 = pd.Timestamp(data_1t)
    x = pesq[(pesq.campo_fim < t1) & (pesq.campo_fim >= t1 - pd.Timedelta(days=janela))
             & pesq.a.notna() & pesq.b.notna()].copy()
    if (PARAM_VI["so_ultima_1t"]["valor"] if so_ultima is None else so_ultima):
        x = x.sort_values("campo_fim").groupby("instituto").tail(1)
    if x.empty:
        return pd.DataFrame(columns=["instituto", "erro_pp", "k", "n_total", "var_pp2", "fatia_pp", "campo_fim"])
    x["s"] = x.a / (x.a + x.b)
    n = x.n.fillna(PARAM_VI["n_padrao"]["valor"]).clip(upper=PARAM_VI["n_teto"]["valor"])
    # n efetivo: só quem escolheu um dos dois (a + b em % do total; linhas em válidos ~ 90%)
    x["n_ef"] = n * np.clip((x.a + x.b) / 100, 0.3, 1.0)
    x["samp"] = 1e4 * x.s * (1 - x.s) / x.n_ef
    x["e"] = 100 * x.s - real_pp
    s2 = PARAM_VI["dp_intra_pp"]["valor"] ** 2
    rows = []
    for ins, g in x.groupby("instituto"):
        w = g.n_ef.values
        k = len(g)
        rows.append({"instituto": ins, "erro_pp": float(np.sum(w * g.e) / w.sum()), "k": k, "n_total": float(n[g.index].sum()),
                     "var_pp2": float((g.samp.mean() + s2) / k), "fatia_pp": float(np.sum(w * 100 * g.s) / w.sum()),
                     "campo_fim": g.campo_fim.max().strftime("%Y-%m-%d")})
    return pd.DataFrame(rows).sort_values("erro_pp").reset_index(drop=True)


def pooling(err: pd.DataFrame) -> dict:
    """Partial pooling (DerSimonian-Laird) dos erros por instituto. Devolve {'_mu','_se_mu','_tau','_k', instituto:
    {'erro_pp','B','rel_pp','dp_rel_pp','plena_pp','dp_plena_pp'}}."""
    if err is None or len(err) == 0:
        return {"_mu": 0.0, "_se_mu": 0.0, "_tau": 0.0, "_k": 0}
    e = err.erro_pp.values.astype(float)
    v = err.var_pp2.values.astype(float)
    w = 1 / v
    k = len(e)
    mu_fe = float(np.sum(w * e) / w.sum())
    Q = float(np.sum(w * (e - mu_fe) ** 2))
    c = float(w.sum() - np.sum(w ** 2) / w.sum())
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (v + tau2)
    mu = float(np.sum(ws * e) / ws.sum())
    se_mu = float(math.sqrt(1 / ws.sum()))
    out = {"_mu": mu, "_se_mu": se_mu, "_tau": math.sqrt(tau2), "_k": k, "_Q": Q}
    for ins, ei, vi in zip(err.instituto, e, v):
        B = tau2 / (tau2 + vi) if tau2 > 0 else 0.0
        rel = B * (ei - mu)
        # dp posterior: parte própria (B v) + incerteza de mu propagada ((1-B)² se_mu² na plena; B² se_mu² na relativa)
        out[ins] = {"erro_pp": float(ei), "B": float(B), "rel_pp": float(rel),
                    "dp_rel_pp": float(math.sqrt(B * vi + B ** 2 * se_mu ** 2)),
                    "plena_pp": float(mu + rel), "dp_plena_pp": float(math.sqrt(B * vi + (1 - B) ** 2 * se_mu ** 2))}
    return out


def correcao(pool: dict, instituto: str, modo: str) -> tuple[float, float]:
    """(correção em p.p. da fatia bipartidária do PT a SUBTRAIR da pesquisa, dp) de um instituto."""
    if modo == "nenhuma" or not pool.get("_k"):
        return 0.0, 0.0
    mu, se, tau = pool["_mu"], pool["_se_mu"], pool["_tau"]
    r = pool.get(instituto)
    if modo == "industria":
        return mu, se
    if r is None:                                   # instituto sem pesquisa de 1º turno na janela
        return (0.0, 0.0) if modo == "relativa" else (mu, math.sqrt(se ** 2))
    if modo == "relativa":
        return r["rel_pp"], r["dp_rel_pp"]
    if modo == "plena":
        return r["plena_pp"], r["dp_plena_pp"]
    raise ValueError(modo)


def corrigir(df: pd.DataFrame, pool: dict, modo: str, col_a: str, col_b: str, mascara=None) -> pd.DataFrame:
    """Subtrai a correção do instituto da fatia bipartidária col_a/(col_a+col_b), mantendo col_a + col_b.
    mascara: linhas a corrigir (padrão: todas com col_a e col_b). Acrescenta 'correcao_pp' e 'correcao_dp_pp'."""
    out = df.copy()
    m = out[col_a].notna() & out[col_b].notna()
    if mascara is not None:
        m &= mascara
    cc = out["instituto"].map(lambda i: correcao(pool, i, modo))
    out["correcao_pp"] = np.where(m, [c[0] for c in cc], 0.0)
    out["correcao_dp_pp"] = np.where(m, [c[1] for c in cc], 0.0)
    tot = out[col_a] + out[col_b]
    q = np.clip(out[col_a] / tot - out["correcao_pp"] / 100, 0.01, 0.99)
    out.loc[m, col_a] = (q * tot)[m]
    out.loc[m, col_b] = (tot - q * tot)[m]
    return out


def dp_media_correcao(pool: dict, institutos, pesos, modo: str) -> float:
    """dp da correção média (pesos relativos dos institutos no agregador): parte própria independente + mu comum."""
    if modo == "nenhuma" or not pool.get("_k"):
        return 0.0
    w = np.asarray(pesos, float)
    w = w / w.sum()
    se = pool["_se_mu"]
    if modo == "industria":
        return se
    own, comum = 0.0, 0.0
    for i, wi in zip(institutos, w):
        r = pool.get(i)
        B = r["B"] if r else 0.0
        vi = (r["dp_rel_pp"] ** 2 - B ** 2 * se ** 2) if r else 0.0
        own += wi ** 2 * max(vi, 0.0)
        comum += wi * (B if modo == "relativa" else (1 - B))
    return float(math.sqrt(own + (comum * se) ** 2))


# ================================================================ dados históricos e de 2026
def _datas(ano):
    import resultado_1t as R
    return tuple(pd.Timestamp(x) for x in R.DATAS[ano])


def real_hist(ano: int) -> dict:
    h = pd.read_csv(M.DADOS / "resultados_uf_2002_2022.csv")
    br = h[h.uf == "BR"].set_index(["ano", "turno"])
    a1 = br.loc[(ano, 1)]
    return {"s1_pp": float(100 * a1.pt_pct_validos / (a1.pt_pct_validos + a1.oponente_pct_validos)),
            "q2_pp": float(br.loc[(ano, 2)].pt_pct_validos)}


def real_2026() -> dict:
    import json
    av = json.loads((M.DADOS / "avaliacao_1t.json").read_text(encoding="utf-8"))
    nac = av["real"]["nacional"]
    return {"s1_pp": 100 * nac["Lula"] / (nac["Lula"] + nac["Flavio"]), "pst": av["real"].get("pst_nacional")}


def pesquisas_hist(ano: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(1º turno: instituto, campo_fim, n, a, b), (2º turno: instituto, campo_inicio, campo_fim, n, a, b)."""
    d = pd.read_csv(M.DADOS / "backtest_pesquisas_nacionais.csv", parse_dates=["campo_inicio", "campo_fim"])
    d = d[d.ano == ano]
    p1 = d[d.turno_alvo == 1].rename(columns={"pt": "a", "opp": "b"})[["instituto", "campo_fim", "n", "a", "b"]]
    p2 = d[d.turno_alvo == 2].rename(columns={"pt": "a", "opp": "b"})[["instituto", "campo_inicio", "campo_fim", "n", "a", "b"]]
    return p1.reset_index(drop=True), p2.reset_index(drop=True)


def pesquisas_2026() -> pd.DataFrame:
    df = M.carregar_pesquisas_nacionais_2026()[0]
    return df


def pool_hist(ano: int, janela: int | None = None, so_ultima: bool | None = None) -> dict:
    p1, _ = pesquisas_hist(ano)
    return pooling(erros_1t(p1, real_hist(ano)["s1_pp"], _datas(ano)[0], janela, so_ultima))


def pool_2026(janela: int | None = None, so_ultima: bool | None = None) -> tuple[dict, pd.DataFrame]:
    df = pesquisas_2026()
    p1 = pd.DataFrame({"instituto": df.instituto, "campo_fim": df.campo_fim, "n": df.n, "a": df.lula, "b": df.flavio})
    err = erros_1t(p1, real_2026()["s1_pp"], _datas(2026)[0], janela, so_ultima)
    return pooling(err), err


# ================================================================ backtest 2014/2018/2022
MODOS = ("nenhuma", "relativa", "industria", "plena")


def _q_agregador(e, prem) -> float | None:
    b = M.construir_base(e, prem)
    return float(b.q_nat) if b.agg2 is not None else None


def _eleicao_corrigida(ano, horizonte, prem, pool, modo):
    import backtest as BT
    e = BT.eleicao_hist(ano, horizonte, prem)
    e.nac = corrigir(e.nac, pool, modo, "t2a", "t2b")
    return e


def backtest_correcao(anos=(2014, 2018, 2022), janela: int | None = None, prem: dict | None = None,
                      log=print, so_ultima: bool | None = None) -> dict:
    """Erro (p.p., média das pesquisas − 2º turno real, fatia do PT) de cada variante, por ano e horizonte.
    pre_1t: agregador na véspera do 1º turno (pesquisas de 2º turno feitas antes do 1º turno);
    pos_1t: agregador na véspera do 2º turno (só pesquisas feitas depois do 1º turno);
    rmse_pesquisas_ult_semana: erro de cada pesquisa da última semana antes do 2º turno (uma por instituto)."""
    prem = prem or M.carregar_premissas()
    linhas, pools = [], {}
    for ano in anos:
        pool = pool_hist(ano, janela, so_ultima)
        pools[ano] = {k.lstrip("_"): v for k, v in pool.items() if k.startswith("_")}
        rr = real_hist(ano)
        _, p2 = pesquisas_hist(ano)
        t1, t2 = _datas(ano)
        ult = p2[(p2.campo_fim >= t2 - pd.Timedelta(days=7)) & (p2.campo_inicio >= t1)]
        ult = ult.sort_values("campo_fim").groupby("instituto").tail(1)
        pos_todas = p2[p2.campo_inicio >= t1]
        for modo in MODOS:
            row = {"ano": ano, "modo": modo, "mu_1t_pp": round(pool["_mu"], 3), "tau_1t_pp": round(pool["_tau"], 3),
                   "institutos_1t": pool["_k"]}
            for hz, nome in (("v1", "pre_1t"), ("v2", "pos_1t")):
                q = _q_agregador(_eleicao_corrigida(ano, hz, prem, pool, modo), prem)
                row[f"erro_{nome}_pp"] = None if q is None or (hz == "v1" and ano == 2014) else round(100 * q - rr["q2_pp"], 3)
            u = corrigir(ult, pool, modo, "a", "b")
            eu = 100 * u.a / (u.a + u.b) - rr["q2_pp"]
            row["rmse_pesquisas_ult_semana_pp"] = round(float(np.sqrt(np.mean(eu ** 2))), 3)
            row["vies_pesquisas_ult_semana_pp"] = round(float(np.mean(eu)), 3)
            ut = corrigir(pos_todas, pool, modo, "a", "b")
            et = 100 * ut.a / (ut.a + ut.b) - rr["q2_pp"]
            row["rmse_pesquisas_pos_1t_pp"] = round(float(np.sqrt(np.mean(et ** 2))), 3)
            row["n_pesquisas_ult_semana"] = int(len(u))
            linhas.append(row)
    t = pd.DataFrame(linhas)
    agg = {}
    for modo in MODOS:
        x = t[t.modo == modo]
        agg[modo] = {
            "rmse_pre_1t_pp": _rms(x.erro_pre_1t_pp), "rmse_pos_1t_pp": _rms(x.erro_pos_1t_pp),
            "mae_pre_1t_pp": _mae(x.erro_pre_1t_pp), "mae_pos_1t_pp": _mae(x.erro_pos_1t_pp),
            "rmse_pesquisas_ult_semana_pp": _rms(x.rmse_pesquisas_ult_semana_pp),
            "rmse_pesquisas_pos_1t_pp": _rms(x.rmse_pesquisas_pos_1t_pp)}
    # persistência do desvio de cada instituto: desvio no 1º turno x desvio da última pesquisa de 2º turno
    pers = persistencia_institutos(anos, janela, so_ultima)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        log(t.to_string())
        log(pd.DataFrame(agg).T.to_string())
        log(pers["tabela"].to_string())
    return {"tabela": t, "agregado": agg, "pools": pools, "persistencia": pers}


def _rms(s):
    s = pd.Series(s).dropna().astype(float)
    return round(float(np.sqrt(np.mean(s ** 2))), 3) if len(s) else None


def _mae(s):
    s = pd.Series(s).dropna().astype(float)
    return round(float(np.mean(np.abs(s))), 3) if len(s) else None


def persistencia_institutos(anos=(2014, 2018, 2022), janela: int | None = None, so_ultima: bool | None = None) -> dict:
    """Desvio de cada instituto em relação à média da indústria no 1º turno (erro bruto e encolhido) x desvio da
    sua última pesquisa de 2º turno (última semana) em relação à média das outras: correlação e inclinação por ano."""
    rows = []
    for ano in anos:
        p1, p2 = pesquisas_hist(ano)
        rr = real_hist(ano)
        t1, t2 = _datas(ano)
        err = erros_1t(p1, rr["s1_pp"], t1, janela, so_ultima)
        pool = pooling(err)
        ult = p2[(p2.campo_fim >= t2 - pd.Timedelta(days=7)) & (p2.campo_inicio >= t1)]
        ult = ult.sort_values("campo_fim").groupby("instituto").tail(1).copy()
        ult["e2"] = 100 * ult.a / (ult.a + ult.b) - rr["q2_pp"]
        m = err.merge(ult[["instituto", "e2"]], on="instituto")
        if len(m) < 3:
            continue
        d1 = m.erro_pp - m.erro_pp.mean()
        d2 = m.e2 - m.e2.mean()
        rel = m.instituto.map(lambda i: pool[i]["rel_pp"])
        rows.append({"ano": ano, "n_institutos": len(m), "corr_desvios": round(float(np.corrcoef(d1, d2)[0, 1]), 3),
                     "inclinacao_bruta": round(float(np.sum(d1 * d2) / np.sum(d1 ** 2)), 3),
                     "inclinacao_encolhida": round(float(np.sum(rel * d2) / max(np.sum(rel ** 2), 1e-9)), 3)
                     if np.sum(rel ** 2) > 1e-9 else None,
                     "media_e1_pp": round(float(m.erro_pp.mean()), 3), "media_e2_pp": round(float(m.e2.mean()), 3)})
    return {"tabela": pd.DataFrame(rows)}


# ================================================================ 2) viés da indústria 1T -> 2T
def erros_industria_1t(prem: dict | None = None) -> dict:
    """Erro do agregador do modelo no 1º turno (fatia bipartidária do PT, p.p.) em 2014, 2018, 2022 e 2026."""
    import backtest as BT
    prem = prem or M.carregar_premissas()
    out = {}
    for ano in (2014, 2018, 2022):
        b = BT.construir_base_hist(ano, "v1", prem)
        out[ano] = round(100 * float(b.p2_nat) - real_hist(ano)["s1_pp"], 3)
    b = M.construir_base_2026(prem)
    out[2026] = round(100 * float(b.p2_nat) - real_2026()["s1_pp"], 3)
    return out


def tau0_ml(erros, sigma: float, grade=np.linspace(0.0, 6.0, 601)) -> float:
    """Escala do viés persistente (erro_ano = B + eta, B ~ N(0, tau0²), eta ~ N(0, sigma²)) por máxima
    verossimilhança marginal: média ~ N(0, tau0² + sigma²/n) -> tau0² = max(0, média² − sigma²/n)."""
    x = np.asarray(erros, float)
    n = len(x)
    return float(math.sqrt(max(0.0, x.mean() ** 2 - sigma ** 2 / n)))


def regressao_bayes(y, X, sigma: float, prior_dp) -> tuple[np.ndarray, np.ndarray]:
    """y = X b + e, e ~ N(0, sigma²), b ~ N(0, diag(prior_dp²)). Devolve (média, covariância) posterior."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    P0 = np.diag(1 / np.asarray(prior_dp, float) ** 2)
    S = np.linalg.inv(P0 + X.T @ X / sigma ** 2)
    return S @ X.T @ y / sigma ** 2, S


def vies_industria(erros_2t: dict, sigma_2t: float, e1: dict | None = None, tau0_atual: float = 2.0,
                   dp_kappa: float = 0.5, prem: dict | None = None) -> dict:
    """Termo de viés do 2º turno de 2026 a partir de (a) os erros históricos da projeção do 2º turno (erros_2t:
    {ano: p.p.}), (b) o erro do agregador no 1º turno em 2014-2026 (e1) e (c) a relação 1T -> 2T.

    Passos: (1) tau0 (escala do viés persistente da indústria na fatia do PT) reestimado por máxima verossimilhança
    marginal com os erros do 1º turno de 2014, 2018, 2022 e 2026 (com e sem 2026, para comparar); (2) modelo
    erro_2T_ano = b + kappa (e1_ano − média e1) + ruído (dp sigma_2t), b ~ N(0, tau0²), kappa ~ N(0, dp_kappa²)
    (prior neutro: sem relação); (3) viés de 2026 = b + kappa (e1_2026 − média e1), com dp posterior.
    Também devolve o método antigo (eb_vies com tau0 fixo) e o EB com o tau0 novo sem kappa."""
    e1 = e1 or erros_industria_1t(prem)
    anos = sorted(erros_2t)
    y = np.array([erros_2t[a] for a in anos], float)
    e1_hist = np.array([e1[a] for a in (2014, 2018, 2022)], float)
    e1_todos = np.array([e1[a] for a in sorted(e1)], float)
    sd1 = float(np.std(e1_todos, ddof=1))
    tau0_sem = tau0_ml(e1_hist, float(np.std(e1_hist, ddof=1)))
    tau0_com = tau0_ml(e1_todos, sd1)
    piso = 0.5
    tau0 = max(tau0_com, piso)
    ref = float(e1_todos.mean())
    X = np.column_stack([np.ones(len(anos)), [e1[a] - ref for a in anos]])
    b, S = regressao_bayes(y, X, sigma_2t, [tau0, dp_kappa])
    x26 = np.array([1.0, e1[2026] - ref])
    v26 = float(x26 @ b)
    dp26 = float(math.sqrt(x26 @ S @ x26))
    antigo = M.eb_vies(list(y), sigma_2t, tau0_atual)
    eb_novo = M.eb_vies(list(y), sigma_2t, tau0)
    return {"erros_1t_pp": e1, "erros_2t_pp": {a: round(float(erros_2t[a]), 3) for a in anos},
            "media_e1_pp": round(ref, 3), "dp_e1_pp": round(sd1, 3),
            "tau0_ml_sem_2026_pp": round(tau0_sem, 3), "tau0_ml_com_2026_pp": round(tau0_com, 3), "tau0_usado_pp": round(tau0, 3),
            "tau0_piso_pp": piso, "kappa_media": round(float(b[1]), 3), "kappa_dp": round(float(math.sqrt(S[1, 1])), 3),
            "b_media_pp": round(float(b[0]), 3), "b_dp_pp": round(float(math.sqrt(S[0, 0])), 3),
            "vies_2026_pp": v26, "vies_2026_dp_pp": dp26,
            "metodo_antigo": {"vies_pp": antigo[0], "vies_dp_pp": antigo[1], "tau0_pp": tau0_atual},
            "eb_tau0_novo_sem_kappa": {"vies_pp": eb_novo[0], "vies_dp_pp": eb_novo[1]}}
