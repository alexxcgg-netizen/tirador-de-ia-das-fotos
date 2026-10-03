"""Backtest do simulador nas eleições de 2014, 2018 e 2022 ("na véspera").

Para cada eleição o motor de ``modelo.py`` roda como se fosse a véspera:

* ``v1`` = véspera do 1º turno: só pesquisas com campo encerrado até a véspera;
  prevê o 1º turno (nacional e UF) e o 2º turno (quando havia pesquisas de
  2º turno PT x adversário antes do 1º turno: 2018 e 2022);
* ``v2`` = véspera do 2º turno: o 1º turno já é conhecido (resultado oficial),
  pesquisas de 2º turno feitas depois do 1º turno.

Sem vazamento de informação futura:
  - o adversário é o 2º colocado na média das pesquisas da véspera (não o real);
  - o prior por UF usa o lean da eleição anterior; abstenção e brancos/nulos
    também da eleição anterior; eleitorado do próprio ano (publicado em julho);
  - a matriz de transferência vem das próprias pesquisas da véspera (pesquisas
    que perguntaram 1º e 2º turno ao mesmo tempo); na v2, é a que reproduz a
    média das pesquisas de 2º turno a partir do 1º turno real;
  - rejeição: só a publicada até a véspera (2018: Datafolha 6/10; 2022: nenhuma
    no conjunto de dados -> alocação proporcional);
  - o prior do viés da indústria para o ano A usa só os erros dos OUTROS anos
    (leave-one-election-out); a variante "temporal" usa só anos anteriores.

Saídas: BACKTEST.md, data/backtest_saida.json (lido por rodar.py e pelo painel).

Uso:
    python simulador/backtest.py            # grade + LOEO + avaliação final (~5-10 min)
    python simulador/backtest.py --rapido   # sem grade (usa premissas.json)
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import modelo as M  # noqa: E402

DADOS = AQUI / "data"
DATAS = {2014: ("2014-10-05", "2014-10-26"), 2018: ("2018-10-07", "2018-10-28"), 2022: ("2022-10-02", "2022-10-30")}
ANOS = (2014, 2018, 2022)
QS_COB = (0.5, 0.8, 0.95)
# 2ª preferência dos indecisos medida pela Quaest em 1/10/2022 (Pereira & Nunes 2024): publicada DEPOIS
# da eleição -> só na validação do método de indecisos, nunca na calibração.
PI_INDECISOS_2022_QUAEST = 1 - 0.525


# ---------------------------------------------------------------- dados históricos
def _ler():
    nac = pd.read_csv(DADOS / "backtest_pesquisas_nacionais.csv")
    for c in ("campo_inicio", "campo_fim"):
        nac[c] = pd.to_datetime(nac[c])
    puf = pd.read_csv(DADOS / "backtest_pesquisas_uf.csv")
    puf["campo_fim"] = pd.to_datetime(puf["campo_fim"])
    res = pd.read_csv(DADOS / "backtest_resultados.csv")
    hist = pd.read_csv(DADOS / "resultados_uf_2002_2022.csv")
    return nac, puf, res, hist


_CACHE = {}


def dados():
    if "d" not in _CACHE:
        _CACHE["d"] = _ler()
    return _CACHE["d"]


def candidatos(ano: int) -> tuple[list, dict]:
    nac = dados()[0]
    d = nac[(nac.ano == ano) & (nac.turno_alvo == 1)]
    nomes = [d.pt_cand.dropna().iloc[0], d.opp_cand.dropna().iloc[0]]
    slots = {}
    for s in ("c3", "c4", "c5", "c6"):
        nm = d[f"{s}_nome"].dropna()
        if len(nm):
            slots[s] = nm.iloc[0]
            nomes.append(nm.iloc[0])
    nomes.append("Outros")
    return nomes, slots


def adversario_vespera(ano: int, prem: dict) -> dict:
    """Confere que o 'adversário' do arquivo é o 2º colocado na média de véspera (regra do agregador:
    última pesquisa de cada instituto em 14 dias, peso sqrt(n) x recência), e não escolhido pelo resultado."""
    nomes, _ = candidatos(ano)
    st = _padronizar_nac(ano)
    ref = pd.Timestamp(DATAS[ano][0]) - pd.Timedelta(days=1)
    st = st[(st.campo_fim <= ref) & st.c1.notna()].copy()
    st["peso_extra"] = 1.0
    x = M._selecionar_recentes(st, "c1", ref, prem)
    med = {nomes[k]: float(np.sum(x.peso * x[f"c{k}"]) / np.sum(x.peso)) for k in range(1, len(nomes) - 1)}
    seg = max(med, key=med.get)
    return {"ano": ano, "medias_totais": med, "segundo_na_media": seg, "adversario_arquivo": nomes[1],
            "confere": seg == nomes[1]}


def _padronizar_nac(ano: int) -> pd.DataFrame:
    nac = dados()[0]
    nomes, slots = candidatos(ano)
    d1 = nac[(nac.ano == ano) & (nac.turno_alvo == 1)].copy()
    d2 = nac[(nac.ano == ano) & (nac.turno_alvo == 2)].copy()
    st = pd.DataFrame({"instituto": d1.instituto, "campo_fim": d1.campo_fim, "n": d1.n, "registro": d1.registro,
                       "base": "totais", "bni": d1.bni, "ind": d1.indecisos, "rej_pt": d1.rej_pt,
                       "rej_opp": d1.rej_opp})
    st["c0"] = d1.pt.values
    st["c1"] = d1.opp.values
    for k, s in enumerate(slots, start=2):
        st[f"c{k}"] = d1[s].values
    st[f"c{len(nomes) - 1}"] = d1.outros.values
    st["t2a"] = np.nan; st["t2b"] = np.nan; st["t2ind"] = np.nan
    st = st.reset_index(drop=True)
    extra = []
    for r in d2.itertuples():
        j = st.index[(st.instituto == r.instituto) & (st.campo_fim == r.campo_fim)]
        if len(j):
            st.loc[j[0], ["t2a", "t2b", "t2ind"]] = [r.pt, r.opp, r.indecisos]
            if pd.isna(st.loc[j[0], "rej_pt"]) and not pd.isna(r.rej_pt):
                st.loc[j[0], ["rej_pt", "rej_opp"]] = [r.rej_pt, r.rej_opp]
        else:
            extra.append({"instituto": r.instituto, "campo_fim": r.campo_fim, "n": r.n, "registro": r.registro,
                          "base": "totais", "bni": np.nan, "ind": np.nan, "t2a": r.pt, "t2b": r.opp,
                          "t2ind": r.indecisos, "rej_pt": r.rej_pt, "rej_opp": r.rej_opp})
    st = pd.concat([st, pd.DataFrame(extra)], ignore_index=True)
    for k in range(len(nomes)):
        if f"c{k}" not in st:
            st[f"c{k}"] = np.nan
    st["peso_extra"] = 1.0
    st, _ = M.deduplicar(st, ["c0", "c1", "t2a", "t2b"])
    return st.reset_index(drop=True)


def _lean(hist, ano, turno):
    a = hist[(hist.ano == ano) & (hist.turno == turno)].set_index("uf")
    col = "pt_2p_pct" if turno == 1 else "pt_pct_validos"
    return M.logit(a[col] / 100) - M.logit(a.loc["BR", col] / 100), a.loc["BR", col] / 100


def prior_estadual_hist(ano: int, turno: int) -> tuple[float, float]:
    """Inclinação do lean e dp do prior por UF para o ano, usando SÓ eleições anteriores:
    regressão (sem intercepto, 27 UFs) do lean de ano-4 no lean de ano-8 e RMSE dessa previsão
    fora do tempo, em p.p. no nível nacional de ano-4. Evita usar 0,85 e 7,0/4,5 p.p., que vêm de 2018->2022."""
    hist = dados()[3]
    la, _ = _lean(hist, ano - 8, turno)
    lb, nb = _lean(hist, ano - 4, turno)
    ufs = [u for u in la.index if u in lb.index and u not in ("BR", "ZZ", "VT")]
    x, y = la.loc[ufs].values, lb.loc[ufs].values
    f = float(np.sum(x * y) / np.sum(x * x))
    rmse_logit = float(np.sqrt(np.mean((f * x - y) ** 2)))
    return f, rmse_logit * 100 * nb * (1 - nb)


def _ufs_hist(ano: int, prem: dict) -> pd.DataFrame:
    _, _, res, hist = dados()
    r1 = res[(res.ano == ano) & (res.turno == 1) & (res.uf != "BR")].set_index("uf")
    ant = hist[hist.ano == ano - 4]
    a1 = ant[ant.turno == 1].set_index("uf")
    a2 = ant[ant.turno == 2].set_index("uf")
    f1, sd1 = prior_estadual_hist(ano, 1)
    f2, sd2 = prior_estadual_hist(ano, 2)
    l1 = M.logit(a1["pt_2p_pct"] / 100) - M.logit(a1.loc["BR", "pt_2p_pct"] / 100)
    l2 = M.logit(a2["pt_pct_validos"] / 100) - M.logit(a2.loc["BR", "pt_pct_validos"] / 100)
    ufs = list(r1.index)
    return pd.DataFrame({
        "uf": ufs, "nome": ufs, "regiao": r1.loc[ufs, "regiao"].values,
        "eleitores": r1.loc[ufs, "eleitorado"].values,
        "abst1": a1.loc[ufs, "abstencao_pct"].values,
        "bn1": (a1.loc[ufs, "branco_pct_comp"] + a1.loc[ufs, "nulo_pct_comp"]).values,
        "abst2": a2.loc[ufs, "abstencao_pct"].values,
        "bn2": (a2.loc[ufs, "branco_pct_comp"] + a2.loc[ufs, "nulo_pct_comp"]).values,
        "prior1": f1 * l1.loc[ufs].values, "prior2": f2 * l2.loc[ufs].values,
        "sdprior1": [prem["estados.dp_prior_exterior_pp"] if u == "ZZ" else sd1 for u in ufs],
        "sdprior2": [prem["estados.dp_prior_exterior_pp"] if u == "ZZ" else sd2 for u in ufs],
    })


def _padronizar_uf(ano: int, nomes: list) -> pd.DataFrame:
    puf = dados()[1]
    d = puf[puf.ano == ano].copy()
    # a mesma pesquisa às vezes aparece em totais e em válidos: fica a de válidos
    d["_pref"] = (d.base != "validos").astype(int)
    d = d.sort_values("_pref").drop_duplicates(["uf", "instituto", "campo_fim", "turno"])
    rows = []
    for r in d.itertuples():
        row = {"uf": r.uf, "instituto": r.instituto, "campo_fim": r.campo_fim, "n": r.n,
               "t2a": np.nan, "t2b": np.nan}
        for k in range(len(nomes)):
            row[f"c{k}"] = np.nan
        if r.turno == 1:
            row["c0"], row["c1"] = r.pt, r.opp
            nm = {r.c3_nome: r.c3, r.c4_nome: r.c4}
            mins = nomes[2:-1]
            if all(isinstance(x, str) for x in nm) and set(mins) <= set(nm) and len(mins) == 2:
                for k, c in enumerate(mins, start=2):
                    row[f"c{k}"] = nm[c]
                row[f"c{len(nomes) - 1}"] = r.outros if not pd.isna(r.outros) else 0.0
        else:
            row["t2a"], row["t2b"] = r.pt, r.opp
        rows.append(row)
    cols = ["uf", "instituto", "campo_fim", "n", "t2a", "t2b"] + [f"c{k}" for k in range(len(nomes))]
    return pd.DataFrame(rows, columns=cols)


def resultados(ano: int) -> dict:
    res = dados()[2]
    r1 = res[(res.ano == ano) & (res.turno == 1)].set_index("uf")
    r2 = res[(res.ano == ano) & (res.turno == 2)].set_index("uf")
    pt = r1.pt_pct_validos / 100
    op = r1.oponente_pct_validos / 100
    t3 = r1.terceiro1_pct_validos / 100
    out = {
        "pt1": pt, "opp1": op, "T": 1 - pt - op, "p2": pt / (pt + op), "margem": pt - op,
        "q": r2.pt_pct_validos / 100,
        "pt_1o_uf": (pt > op) & (pt > t3), "pt_vence_2t_uf": r2.pt_pct_validos > 50,
    }
    return out


def eleicao_hist(ano: int, horizonte: str, prem: dict, metodo_indecisos: str | None = None) -> M.Eleicao:
    nomes, _ = candidatos(ano)
    t1, t2 = (pd.Timestamp(x) for x in DATAS[ano])
    ref = (t1 if horizonte == "v1" else t2) - pd.Timedelta(days=1)
    st = _padronizar_nac(ano)
    st = st[st.campo_fim <= ref].copy()
    if horizonte == "v2":
        st = st[st.campo_fim >= t1].copy()           # 2º turno: só pesquisas feitas depois do 1º turno
        for k in range(len(nomes)):
            st[f"c{k}"] = np.nan
    ufs = _ufs_hist(ano, prem)
    puf = _padronizar_uf(ano, nomes)
    if horizonte == "v1":
        puf = puf[puf.campo_fim <= ref]
    else:
        puf = puf[(puf.campo_fim <= ref) & (puf.campo_fim >= t1)]
    # rejeição publicada até a véspera
    rj = st[st.rej_pt.notna()].sort_values("campo_fim")
    rejeicao = {"pt": float(rj.rej_pt.iloc[-1]), "opp": float(rj.rej_opp.iloc[-1])} if len(rj) else None
    M_ = len(nomes) - 2
    # transferência implícita: pesquisas da véspera com 1º e 2º turno
    if horizonte == "v1":
        par = st[st.c0.notna() & st.t2a.notna() & (st.campo_fim > ref - pd.Timedelta(days=14))]
        if len(par):
            dpt = (par.t2a - par.c0).clip(lower=0); dop = (par.t2b - par.c1).clip(lower=0)
            pool = (100 - par.c0 - par.c1)
            r = float(np.mean(dpt / (dpt + dop).where(dpt + dop > 0)))
            a = float(np.clip(np.mean(1 - (dpt + dop) / pool), 0.05, 0.6))
        else:
            r, a = 0.5, 0.3
        transf = np.tile([r * (1 - a), (1 - r) * (1 - a), a], (M_, 1))
        fixo = None
    else:
        a = 0.25
        transf = np.tile([0.5 * (1 - a), 0.5 * (1 - a), a], (M_, 1))   # ajustada depois (resolver_transf_v2)
        rr = resultados(ano)
        fixo = np.zeros((len(ufs), len(nomes)))
        for i, u in enumerate(ufs.uf):
            fixo[i, 0] = rr["pt1"][u]; fixo[i, 1] = rr["opp1"][u]; fixo[i, -1] = rr["T"][u]
    e = M.Eleicao(ano, nomes, ref, st, puf, ufs, transf, ref - pd.Timedelta(days=45),
                  rejeicao=rejeicao, exposicao={}, ajuste_comp=None, primeiro_turno_fixo=fixo,
                  horizonte_2t="vespera_2t" if horizonte == "v2" else "vespera_1t")
    return e


def construir_base_hist(ano, horizonte, prem, metodo_indecisos=None, pi_indecisos=None) -> M.Base:
    e = eleicao_hist(ano, horizonte, prem)
    if pi_indecisos is not None:
        e.pi_indecisos = pi_indecisos
    b = M.construir_base(e, prem, metodo_indecisos)
    if horizonte == "v2":
        # matriz que reproduz a média das pesquisas de 2º turno a partir do 1º turno real (nacional)
        w = (b.ufs.eleitores * (1 - b.ufs.abst1 / 100) * (1 - b.ufs.bn1 / 100)).values
        sh = (w[:, None] * e.primeiro_turno_fixo).sum(0) / w.sum()
        L, F, Mm = sh[0], sh[1], sh[2:].sum()
        a = e.transf[0, 2]
        r = float(np.clip((b.q_nat * (L + F + (1 - a) * Mm) - L) / ((1 - a) * Mm), 0, 1))
        e.transf = np.tile([r * (1 - a), (1 - r) * (1 - a), a], (e.M, 1))
    b.tem_2t = b.agg2 is not None and (horizonte == "v2" or ano != 2014)
    return b


# ---------------------------------------------------------------- erros históricos (centros determinísticos)
def centro_p2(b: M.Base, muT: float) -> float:
    """p2 nacional esperado depois da contração média da terceira via (sem erros)."""
    T = b.m_nat.sum()
    mc = b.m_nat * math.exp(muT)
    dlt = b.m_nat - mc
    r = b.e.transf[:, 0] / (b.e.transf[:, 0] + b.e.transf[:, 1])
    L = (1 - T) * b.p2_nat + np.sum(dlt * r)
    F = (1 - T) * (1 - b.p2_nat) + np.sum(dlt * (1 - r))
    return L / (L + F)


def erros_brutos(prem: dict, anos=ANOS, metodo_indecisos=None) -> dict:
    """Erros (pesquisa/centro − resultado) de cada ano: T (log), q v1 e q v2 (p.p.), e as bases."""
    out = {}
    for ano in anos:
        rr = resultados(ano)
        b1 = construir_base_hist(ano, "v1", prem, metodo_indecisos)
        b2 = construir_base_hist(ano, "v2", prem, metodo_indecisos)
        T_poll = float(b1.m_nat.sum())
        out[ano] = {
            "base_v1": b1, "base_v2": b2,
            "T_poll": T_poll, "T_real": float(rr["T"]["BR"]),
            "res_T_log": math.log(rr["T"]["BR"] / T_poll),
            "p2_poll": b1.p2_nat, "p2_real": float(rr["p2"]["BR"]),
            "q_v1_poll": b1.q_nat if b1.tem_2t else None, "q_real": float(rr["q"]["BR"]),
            "res_q_v1_pp": 100 * (b1.q_nat - rr["q"]["BR"]) if b1.tem_2t else None,
            "q_v2_poll": b2.q_nat, "res_q_v2_pp": 100 * (b2.q_nat - rr["q"]["BR"]),
        }
    return out


def priors_vies(err: dict, anos_prior, prem: dict, visao: str, correcao_comp=None) -> dict:
    """Prior do viés (b1, b2, muT) a partir dos erros dos anos em anos_prior.

    visao: 'neutro' (b = 0; muT encolhido), 'calibrado' (EB encolhido), 'pleno' (média sem encolhimento).
    correcao_comp: {'p2': pp, 'q': pp} descontado dos erros históricos (visão calibrada de 2026)."""
    anos_prior = [a for a in anos_prior if a in err]
    sT = prem["terceira_via.dp_ano_log"]
    tT = math.inf if visao == "pleno" else prem["terceira_via.tau0_log"]
    resT = [err[a]["res_T_log"] for a in anos_prior]
    muT = M.eb_vies(resT, sT, tT) if resT else (prem["terceira_via.mu_log"], 0.0)
    out = {"muT": muT}
    if visao == "neutro":
        out.update({"b1": (0.0, 0.0), "b2": (0.0, 0.0), "b2_v2": (0.0, 0.0)})
        return out
    c = correcao_comp or {"p2": 0.0, "q": 0.0}
    res_p2 = []
    for a in anos_prior:
        # centro de p2 do ano a com a contração estimada SEM o próprio ano a (sem vazamento)
        outros = [x for x in anos_prior if x != a]
        mu_a = M.eb_vies([err[x]["res_T_log"] for x in outros], sT, tT)[0] if outros else prem["terceira_via.mu_log"]
        res_p2.append(100 * (centro_p2(err[a]["base_v1"], mu_a) - err[a]["p2_real"]) - c["p2"])
    resq = [err[a]["res_q_v1_pp"] - c["q"] for a in anos_prior if err[a]["res_q_v1_pp"] is not None]
    resq2 = [err[a]["res_q_v2_pp"] - c["q"] for a in anos_prior]
    t1 = math.inf if visao == "pleno" else prem["vies.tau0_p2_pp"]
    tq = math.inf if visao == "pleno" else prem["vies.tau0_q_pp"]
    out["b1"] = M.eb_vies(res_p2, prem["vies.dp_ano_p2_pp"], t1)
    # viés do 2º turno = erro das pesquisas de 2º turno quando medem o mesmo que a urna (véspera do 2º turno);
    # a deriva entre a véspera do 1º turno e o 2º turno (+3,5/+4,7 em 2018/2022) é tratada como erro aleatório
    # simétrico (erro_2t.dp_q_pp_vespera_1t), não como viés persistente (2 casos só).
    out["b2"] = M.eb_vies(resq2, prem["vies.dp_ano_q_v2_pp"], tq)
    out["b2_v2"] = M.eb_vies(resq2, prem["vies.dp_ano_q_v2_pp"], tq)
    out["residuos"] = {"p2_pp": dict(zip(anos_prior, np.round(res_p2, 2))),
                       "q_v1_pp": {a: round(err[a]["res_q_v1_pp"] - c["q"], 2) for a in anos_prior
                                   if err[a]["res_q_v1_pp"] is not None},
                       "q_v2_pp": {a: round(err[a]["res_q_v2_pp"] - c["q"], 2) for a in anos_prior},
                       "T_log": dict(zip(anos_prior, np.round(resT, 3)))}
    return out


# ---------------------------------------------------------------- métricas
def crps(s: np.ndarray, y: float) -> float:
    s = np.sort(np.asarray(s, float))
    n = len(s)
    i = np.arange(1, n + 1)
    return float(np.mean(np.abs(s - y)) - np.sum((2 * i - n - 1) * s) / n ** 2)


def pit(s, y):
    s = np.asarray(s)
    return float(np.mean(s < y) + 0.5 * np.mean(s == y))


def _resumo_var(s, y, nome, nivel, ano, alvo, uf="BR"):
    q = np.quantile(s, [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975])
    p = pit(s, y)
    return {"ano": ano, "alvo": alvo, "nivel": nivel, "var": nome, "uf": uf, "real": 100 * y,
            "mediana": 100 * q[3], "erro_mediana": 100 * (q[3] - y), "p025": 100 * q[0], "p975": 100 * q[6],
            "p10": 100 * q[1], "p90": 100 * q[5], "p25": 100 * q[2], "p75": 100 * q[4],
            "pit": p, "crps": 100 * crps(s[:4000], y),
            **{f"cob{int(c * 100)}": bool(abs(p - 0.5) <= c / 2) for c in QS_COB}}


def _prob(p, y, nome, nivel, ano, alvo, uf="BR"):
    pc = min(max(p, 1e-3), 1 - 1e-3)
    return {"ano": ano, "alvo": alvo, "nivel": nivel, "evento": nome, "uf": uf, "p": p, "y": int(bool(y)),
            "brier": (p - y) ** 2, "logloss": -(y * math.log(pc) + (1 - y) * math.log(1 - pc))}


def avaliar_rodada(b: M.Base, r: dict, horizonte: str) -> tuple[list, list]:
    """Compara uma rodada simulada com o resultado oficial."""
    ano = b.e.ano
    rr = resultados(ano)
    ufs = list(b.ufs.uf)
    cont, prob = [], []
    if horizonte == "v1":
        n1 = r["nat1"]
        L, F = n1[:, 0], n1[:, 1]
        T = 1 - L - F
        for nome, s, y in (("pt1", L, rr["pt1"]["BR"]), ("opp1", F, rr["opp1"]["BR"]), ("T", T, rr["T"]["BR"]),
                           ("margem", L - F, rr["margem"]["BR"]), ("p2", L / (L + F), rr["p2"]["BR"])):
            cont.append(_resumo_var(s, y, nome, "nacional", ano, "1T"))
        prob.append(_prob(float(np.mean(r["primeiro"] == 0)), rr["pt1"]["BR"] > rr["opp1"]["BR"],
                          "PT 1º no 1º turno", "nacional", ano, "1T"))
        for i, u in enumerate(ufs):
            nv = "exterior" if u == "ZZ" else "uf"
            cont.append(_resumo_var(r["uf_L"][:, i], rr["pt1"][u], "pt1", nv, ano, "1T", u))
            cont.append(_resumo_var(r["uf_F"][:, i], rr["opp1"][u], "opp1", nv, ano, "1T", u))
            prob.append(_prob(float(np.mean(r["uf_top"][:, i] == 0)), rr["pt_1o_uf"][u], "PT 1º na UF (1T)",
                              nv, ano, "1T", u))
    if b.tem_2t:
        alvo = "2T (véspera do 1T)" if horizonte == "v1" else "2T (véspera do 2T)"
        cont.append(_resumo_var(r["Q"], rr["q"]["BR"], "q", "nacional", ano, alvo))
        if horizonte == "v1":
            prob.append(_prob(float(np.mean(r["vencedor"] == 0)), rr["q"]["BR"] > 0.5, "PT vence a eleição",
                              "nacional", ano, alvo))
        else:
            prob.append(_prob(float(np.mean(r["Q"] > 0.5)), rr["q"]["BR"] > 0.5, "PT vence o 2º turno",
                              "nacional", ano, alvo))
        for i, u in enumerate(ufs):
            nv = "exterior" if u == "ZZ" else "uf"
            cont.append(_resumo_var(r["uf_q"][:, i], rr["q"][u], "q", nv, ano, alvo, u))
            prob.append(_prob(float(np.mean(r["uf_q"][:, i] > 0.5)), rr["pt_vence_2t_uf"][u], "PT vence a UF (2T)",
                              nv, ano, alvo, u))
    return cont, prob


def vies_para_rodada(pri: dict, horizonte: str, visao: str) -> dict:
    v = {"muT": pri["muT"], "b1": pri["b1"], "b2": pri["b2"] if horizonte == "v1" else pri["b2_v2"]}
    if visao == "pleno":
        v["lambda1"] = v["lambda2"] = (1.0, 0.0)
    return v


# ---------------------------------------------------------------- execução
def com_params(prem: dict, **kw) -> dict:
    P = dict(prem)
    for k, v in kw.items():
        P[k.replace("__", ".")] = v
    return P


_BASES = {}


def base_cache(ano, horizonte, P, metodo=None, pi=None):
    chave = (ano, horizonte, metodo or P["indecisos.metodo"], pi, P["estados.dp_pesquisa_piso_1t_pp"],
             P["estados.dp_pesquisa_piso_2t_pp"], P["estados.dp_prior_1t_pp"], P["estados.dp_prior_2t_pp"])
    if chave not in _BASES:
        _BASES[chave] = construir_base_hist(ano, horizonte, P, metodo, pi)
    return _BASES[chave]


def rodar(P: dict, visao="calibrado", anos=ANOS, horizontes=("v1", "v2"), n=None, seed=7,
          modo_prior="loeo", err=None, metodo=None):
    """Roda os alvos e devolve (contínuas, probabilidades, priors usados)."""
    n = n or P["simulacao.n_backtest"]
    err = err or erros_brutos(P, metodo_indecisos=metodo)
    cont, prob, usados = [], [], {}
    for ano in anos:
        if modo_prior == "loeo":
            anos_prior = [a for a in ANOS if a != ano]
        else:                                     # temporal: só anos anteriores
            anos_prior = [a for a in ANOS if a < ano]
        pri = priors_vies(err, anos_prior, P, visao)
        usados[ano] = pri
        for h in horizontes:
            b = base_cache(ano, h, P, metodo)
            if h == "v2" and not b.tem_2t:
                continue
            rng = np.random.default_rng([seed, ano, 1 if h == "v1" else 2])
            r = M.simular_lote(b, vies_para_rodada(pri, h, visao), n, rng, P)
            c, p = avaliar_rodada(b, r, h)
            cont += c; prob += p
    return pd.DataFrame(cont), pd.DataFrame(prob), usados


def score(cont: pd.DataFrame, prob: pd.DataFrame | None = None) -> dict:
    """Resumo: CRPS médio (nacional e UF), cobertura, PIT."""
    out = {}
    for nivel in ("nacional", "uf"):
        c = cont[cont.nivel == nivel]
        if c.empty:
            continue
        out[f"crps_{nivel}"] = float(c.crps.mean())
        for q in QS_COB:
            out[f"cob{int(q * 100)}_{nivel}"] = float(c[f"cob{int(q * 100)}"].mean())
        out[f"mae_{nivel}"] = float(c.erro_mediana.abs().mean())
    if prob is not None and len(prob):
        for nivel in ("nacional", "uf"):
            p = prob[prob.nivel == nivel]
            if len(p):
                out[f"brier_{nivel}"] = float(p.brier.mean())
                out[f"logloss_{nivel}"] = float(p.logloss.mean())
    return out


# ---------------------------------------------------------------- calibração
GRADE_NAC1 = {"erro_nacional_1t.dp_p2_pp": [2.0, 3.0, 4.0, 5.0, 6.0], "erro_nacional_1t.gl_t": [3, 5, 10],
              "terceira_via.dp_log": [0.10, 0.20], "vies.tau0_p2_pp": [0.0, 1.0, 2.0, 4.0, math.inf]}
GRADE_NAC2 = {"erro_2t.dp_q_pp_vespera_1t": [2.0, 3.0, 4.5, 6.0, 8.0],
              "erro_2t.peso_pesquisas_vespera_1t": [0.1, 0.3, 0.5, 0.7],
              "vies.tau0_q_pp": [0.0, 1.0, 2.0, 4.0, math.inf]}
GRADE_NAC3 = {"erro_2t.dp_q_pp_vespera_2t": [0.5, 1.0, 1.5, 2.5, 3.5]}
# limites inferiores pelo conhecimento prévio: erro de pesquisa estadual de presidente com MAE 2,25-4,34 p.p.
# (Pindograma) -> piso >= 2 p.p.; erro idiossincrático da UF >= 3 p.p. (briefing)
GRADE_UF = {"estados.dp_uf_minimo_pp": [3.0, 4.5, 6.0], "estados.dp_pesquisa_piso_1t_pp": [2.0, 3.0, 5.0, 7.0],
            "estados.dp_pesquisa_piso_2t_pp": [2.0, 3.0, 4.5], "estados.dp_regional_pp": [1.5, 3.0, 4.5, 6.0]}


def _grade(P, grade, filtro, n, err, nivel, horizontes=("v1",), alvo_contem=None):
    """Roda a grade; devolve DataFrame com CRPS por ano para o filtro de variáveis."""
    linhas = []
    chaves = list(grade)
    for vals in itertools.product(*[grade[k] for k in chaves]):
        Pc = dict(P)
        Pc.update(dict(zip(chaves, vals)))
        cont, prob, _ = rodar(Pc, "calibrado", n=n, err=err, horizontes=horizontes)
        c = cont[(cont.nivel == nivel) & cont["var"].isin(filtro)]
        if alvo_contem:
            c = c[c.alvo.str.contains(alvo_contem, regex=False)]
        for ano, g in c.groupby("ano"):
            linhas.append({**dict(zip(chaves, vals)), "ano": ano, "crps": g.crps.mean(),
                           "cob80": g.cob80.mean(), "cob95": g.cob95.mean(), "n": len(g)})
    return pd.DataFrame(linhas), chaves


# Fixados por princípio (premissas.json), não otimizados: o encolhimento do viés e o peso das pesquisas de
# 2º turno (só 2 eleições informam esse peso; 0,5 = sem preferência entre as duas vias). Com 2-3 eleições do mesmo
# sinal, o CRPS sempre "prefere" menos encolhimento; a grade só mostra a sensibilidade (BACKTEST.md).
FIXOS = ("vies.tau0_p2_pp", "vies.tau0_q_pp", "erro_2t.peso_pesquisas_vespera_1t")
COB_MIN = (0.75, 0.90)


def _escolher(tab, chaves, anos, fixos=None):
    """Média do CRPS nos anos dados -> melhor combinação (empate: a mais simples/primeira)."""
    if fixos:
        for k, v in fixos.items():
            if k in tab:
                tab = tab[np.isclose(tab[k].astype(float), float(v)) | ((tab[k] == math.inf) & (v == math.inf))]
    x = tab[tab.ano.isin(anos)]
    x = x.assign(w=x["n"])
    t = x.groupby(chaves, dropna=False).apply(
        lambda g: pd.Series({"crps": g.crps.mean(), "cob80": np.average(g.cob80, weights=g.w),
                             "cob95": np.average(g.cob95, weights=g.w)}), include_groups=False).reset_index()
    # cobertura primeiro: só concorrem as combinações com intervalos não estreitos demais
    # (>= 75% dentro do intervalo de 80% e >= 90% dentro do de 95%); entre elas, menor CRPS.
    ok = t[(t.cob80 >= COB_MIN[0]) & (t.cob95 >= COB_MIN[1])]
    if ok.empty:
        ok = t[t.cob95 >= t.cob95.max() - 1e-9]
    ok = ok.sort_values("crps", kind="stable")
    return dict(ok.iloc[0][chaves]), float(ok.iloc[0].crps)


def calibrar(P: dict, n=8000, log=print) -> tuple[dict, dict]:
    """Calibração por blocos, com escolha in-sample e leave-one-election-out."""
    err = erros_brutos(P)
    rel = {}
    Pc = dict(P)
    blocos = [("nac1", GRADE_NAC1, ["pt1", "opp1", "T"], "nacional", ("v1",), "1T"),
              ("nac2", GRADE_NAC2, ["q"], "nacional", ("v1",), "véspera do 1T"),
              ("nac3", GRADE_NAC3, ["q"], "nacional", ("v2",), "véspera do 2T"),
              ("uf", GRADE_UF, ["pt1", "opp1", "q"], "uf", ("v1", "v2"), None)]
    for nome, grade, filtro, nivel, hs, alvo in blocos:
        t0 = time.perf_counter()
        tab, chaves = _grade(Pc, grade, filtro, n, err, nivel, hs, alvo)
        anos_bloco = sorted(tab.ano.unique())
        fx = {k: P[k] for k in FIXOS if k in chaves}
        melhor, sc = _escolher(tab, chaves, anos_bloco, fx)
        livre, sc_livre = _escolher(tab, chaves, anos_bloco)
        loeo = {}
        for a in anos_bloco:
            outros = [x for x in anos_bloco if x != a]
            m_a, _ = _escolher(tab, chaves, outros, fx)
            sel = np.all([tab[k].values == m_a[k] for k in chaves], axis=0) & (tab.ano.values == a)
            loeo[int(a)] = {"escolha": {k: _py(v) for k, v in m_a.items()},
                            "crps_fora": float(tab[sel].crps.iloc[0]),
                            "crps_insample": float(tab[(np.all([tab[k].values == melhor[k] for k in chaves], axis=0))
                                                       & (tab.ano.values == a)].crps.iloc[0])}
        rel[nome] = {"melhor": {k: _py(v) for k, v in melhor.items()}, "crps": sc, "anos": [int(a) for a in anos_bloco],
                     "sem_fixar_encolhimento": {"melhor": {k: _py(v) for k, v in livre.items()}, "crps": sc_livre},
                     "loeo": loeo, "grade": tab.replace([math.inf], 1e9).to_dict(orient="records"),
                     "tempo_s": round(time.perf_counter() - t0, 1)}
        log(f"[{nome}] melhor {rel[nome]['melhor']} CRPS {sc:.3f} ({rel[nome]['tempo_s']}s)")
        Pc.update(melhor)
    return Pc, rel


def _py(v):
    if isinstance(v, (np.floating, float)):
        return None if not math.isfinite(float(v)) else float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    return v


# ---------------------------------------------------------------- validação dos indecisos
def validar_indecisos(P: dict) -> list:
    """Erro da média de véspera em p2/q com indecisos proporcionais x por rejeição/2ª preferência."""
    out = []
    for ano in (2018, 2022):
        rr = resultados(ano)
        for h, var in (("v1", "p2"), ("v2", "q")):
            prop = construir_base_hist(ano, h, P, "proporcional")
            rej = construir_base_hist(ano, h, P, "rejeicao")
            real = rr["p2" if var == "p2" else "q"]["BR"]
            vp = prop.p2_nat if var == "p2" else prop.q_nat
            vr = rej.p2_nat if var == "p2" else rej.q_nat
            fonte = (f"rejeição {rej.e.rejeicao['pt']:.0f}/{rej.e.rejeicao['opp']:.0f} (Datafolha, até a véspera)"
                     if rej.e.rejeicao else "sem rejeição publicada no conjunto -> igual ao proporcional")
            out.append({"ano": ano, "turno": "1T" if var == "p2" else "2T", "var": var, "real": 100 * real,
                        "proporcional": 100 * vp, "rejeicao": 100 * vr, "erro_prop": 100 * (vp - real),
                        "erro_rej": 100 * (vr - real), "fonte": fonte})
            if ano == 2022 and h == "v1":
                pn = construir_base_hist(ano, h, P, "rejeicao", PI_INDECISOS_2022_QUAEST)
                out.append({"ano": ano, "turno": "1T", "var": var, "real": 100 * real, "proporcional": 100 * vp,
                            "rejeicao": 100 * pn.p2_nat, "erro_prop": 100 * (vp - real),
                            "erro_rej": 100 * (pn.p2_nat - real),
                            "fonte": "2ª preferência dos indecisos (Quaest 1/10/2022, publicada em 2024: só validação)"})
    return out


# ---------------------------------------------------------------- relatório
def _fmt(x, d=1):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "∞" if x == math.inf else "–"
    return f"{x:.{d}f}".replace(".", ",")


def tabela_md(df, cols, nomes=None, dec=None):
    nomes = nomes or cols
    dec = dec or {}
    linhas = ["| " + " | ".join(nomes) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cel = []
        for c in cols:
            v = r[c]
            if isinstance(v, (bool, np.bool_)):
                cel.append("sim" if v else "não")
            elif isinstance(v, (float, np.floating)):
                cel.append(_fmt(float(v), dec.get(c, 1)))
            else:
                cel.append(str(v))
        linhas.append("| " + " | ".join(cel) + " |")
    return "\n".join(linhas)


def pit_hist(cont, bins=10):
    h, _ = np.histogram(cont.pit.values, bins=bins, range=(0, 1))
    return h.tolist()


def avaliar_final(P: dict, n=40000, log=print, rel=None) -> dict:
    """Avaliação final com os parâmetros escolhidos: 3 visões, LOEO e temporal.
    Com rel (saída da grade), também a validação totalmente aninhada: para cada ano, os parâmetros de
    cada bloco são os escolhidos SEM aquele ano (e o prior de viés também sem ele)."""
    err = erros_brutos(P)
    saida = {"visoes": {}}
    if rel:
        cs, ps = [], []
        for ano in ANOS:
            Py = dict(P)
            for bloco in rel.values():
                esc = bloco["loeo"].get(int(ano))
                if esc:
                    Py.update({k: (math.inf if v is None else v) for k, v in esc["escolha"].items()})
            c, p, _ = rodar(Py, "calibrado", anos=(ano,), n=n, err=erros_brutos(Py))
            cs.append(c); ps.append(p)
        c, p = pd.concat(cs, ignore_index=True), pd.concat(ps, ignore_index=True)
        saida["aninhado"] = {"cont": c, "prob": p, "score": score(c, p)}
        log(f"[final aninhado] {saida['aninhado']['score']}")
    for visao in M.VISOES:
        cont, prob, pri = rodar(P, visao, n=n, err=err)
        saida["visoes"][visao] = {"cont": cont, "prob": prob, "priors": pri, "score": score(cont, prob)}
        log(f"[final {visao}] {score(cont, prob)}")
    cont, prob, pri = rodar(P, "calibrado", n=n, err=err, modo_prior="temporal")
    saida["temporal"] = {"cont": cont, "prob": prob, "priors": pri, "score": score(cont, prob)}
    saida["erros"] = {a: {k: v for k, v in d.items() if not k.startswith("base")} for a, d in err.items()}
    saida["indecisos"] = validar_indecisos(P)
    saida["adversarios"] = [adversario_vespera(a, P) for a in ANOS]
    return saida


def escrever(P: dict, rel: dict | None, fin: dict, tempo: float):
    vc = fin["visoes"]["calibrado"]
    cont, prob = vc["cont"], vc["prob"]
    L = []
    L.append("# Backtest do simulador: 2014, 2018 e 2022 (véspera)\n")
    L.append((f"Gerado por `backtest.py` em {pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M} UTC; "
              + (f"{P['simulacao.n_backtest']:,} simulações por alvo na grade e " if rel else "sem grade (--rapido); ")
              + f"40.000 na avaliação final; tempo total {tempo:.0f} s.\n").replace(",", "."))
    L.append("""## O que foi testado

O motor de `modelo.py` rodou como se fosse a véspera de cada turno, só com as pesquisas daquele momento
(`data/backtest_pesquisas_*.csv`), e foi comparado com o resultado oficial do TSE (`data/backtest_resultados.csv`).

* **v1 — véspera do 1º turno:** prevê o 1º turno (nacional e 27 UFs + exterior) e o 2º turno (2018 e 2022;
  em 2014 não havia pesquisa Dilma x Aécio antes do 1º turno no conjunto de dados).
* **v2 — véspera do 2º turno:** 1º turno real conhecido; pesquisas de 2º turno feitas depois do 1º turno.
* **Sem informação futura:** adversário = 2º colocado na média de véspera; prior das UFs = lean da eleição anterior;
  abstenção e brancos/nulos da eleição anterior; matriz de transferência das próprias pesquisas da véspera
  (perguntas de 1º e 2º turno na mesma pesquisa); rejeição só se publicada até a véspera; o prior do viés da
  indústria para o ano A usa só os erros dos **outros** anos (leave-one-election-out, LOEO). A variante
  **temporal** usa só anos anteriores (2014 sem prior; 2018 com 2014; 2022 com 2014 e 2018).
* **Limites do teste:** só 3 eleições (2 para o 2º turno projetado na véspera do 1º); pesquisas estaduais
  esparsas (2014 sem nenhuma; 2018 quase só Ibope; 2022 quase só Ipec). O prior demográfico e o ajuste de
  comparecimento de 2026 não entram no backtest (covariáveis de 2022–2026 e comparecimento real de 2022 seriam
  vazamento); a via de transferência usa a matriz implícita das pesquisas, não a matriz Quaest por candidato.
""")
    # erros históricos
    L.append("**Adversário de cada ano (conferido pela média de véspera, sem usar o resultado):** "
             + "; ".join(f"{d['ano']}: {d['adversario_arquivo']} "
                         + ("= não-PT mais votado na média" if d["confere"] else "≠ não-PT mais votado (" + d["segundo_na_media"] + ")")
                         + " (" + ", ".join(f"{k} {v:.1f}" for k, v in d['medias_totais'].items()) + ")"
                         for d in fin["adversarios"])
             + ". Em 2014 Aécio passou Marina só nos últimos dias; na média simples da última semana Marina ainda "
               "aparecia à frente, então a escolha do adversário numa disputa a três é frágil.\n")
    L.append("**Prior estadual sem dados futuros:** inclinação do lean e dp do prior de cada ano estimados só com "
             "eleições anteriores (" + "; ".join(f"{a}: {prior_estadual_hist(a, 1)[0]:.2f}/{prior_estadual_hist(a, 1)[1]:.1f} p.p. "
                                                   f"(1T), {prior_estadual_hist(a, 2)[0]:.2f}/{prior_estadual_hist(a, 2)[1]:.1f} p.p. (2T)"
                                                   for a in ANOS)
             + "). Só os sinais das cargas do eixo NE/N x S/CO vêm de correlações 2002–2022 (parcialmente dentro da amostra).\n")
    L.append("## Erros das médias de véspera (insumo do prior de viés)\n")
    er = []
    for a, d in fin["erros"].items():
        er.append({"Ano": str(a), "T pesquisas": 100 * d["T_poll"], "T real": 100 * d["T_real"],
                   "erro T (log)": d["res_T_log"], "p2 pesquisas": 100 * d["p2_poll"], "p2 real": 100 * d["p2_real"],
                   "q pesq. véspera 1T": (100 * d["q_v1_poll"]) if d["q_v1_poll"] else float("nan"),
                   "q pesq. véspera 2T": 100 * d["q_v2_poll"], "q real": 100 * d["q_real"]})
    L.append(tabela_md(pd.DataFrame(er), list(er[0].keys()), dec={"erro T (log)": 2}))
    L.append("\nT = soma dos candidatos fora os dois primeiros (votos válidos); p2 = PT/(PT+adversário); "
             "q = PT no 2º turno. Valores das médias do agregador (house effects hierárquicos, recência, "
             "indecisos pelo método escolhido). Erro positivo = pesquisas mais favoráveis ao PT.\n")
    pri22 = fin["visoes"]["calibrado"]["priors"][2022]
    L.append("Resíduos usados no prior (p.p.; p2 depois da contração média da terceira via estimada sem o próprio ano): "
             + json.dumps(priors_vies(fin["_err_obj"], list(ANOS), P, "calibrado")["residuos"], ensure_ascii=False)
             .replace("NaN", "–") + "\n")
    # resumo por visão
    L.append("## Calibração: cobertura, erros e escores por visão\n")
    L.append("Nas três primeiras linhas, o prior de viés de cada ano exclui o próprio ano (LOEO), mas os demais "
             "parâmetros (dp, gl, pisos, pesos) foram escolhidos na grade com os três anos: é uma avaliação "
             "parcialmente dentro da amostra. A linha 'LOEO aninhado' refaz a escolha de todos os parâmetros sem o "
             "ano avaliado e é a medida honesta de desempenho fora da amostra. O exterior (ZZ) fica fora das "
             "métricas por UF (o voto no exterior mudou 20–40 p.p. entre eleições).\n")
    rows = []
    for v in M.VISOES:
        s = fin["visoes"][v]["score"]
        rows.append({"Visão": {"neutro": "Neutro (viés 0)", "calibrado": "Modelo calibrado",
                               "pleno": "Viés histórico pleno"}[v],
                     "Cob. 50% nac": s.get("cob50_nacional"), "Cob. 80% nac": s.get("cob80_nacional"),
                     "Cob. 95% nac": s.get("cob95_nacional"), "Cob. 50% UF": s.get("cob50_uf"),
                     "Cob. 80% UF": s.get("cob80_uf"), "Cob. 95% UF": s.get("cob95_uf"),
                     "CRPS nac": s.get("crps_nacional"), "CRPS UF": s.get("crps_uf"),
                     "Brier nac": s.get("brier_nacional"), "Brier UF": s.get("brier_uf"),
                     "Log-loss UF": s.get("logloss_uf")})
    if "aninhado" in fin:
        sa = fin["aninhado"]["score"]
        rows.append({"Visão": "Calibrado, LOEO aninhado (parâmetros e prior sem o ano)",
                     "Cob. 50% nac": sa.get("cob50_nacional"), "Cob. 80% nac": sa.get("cob80_nacional"),
                     "Cob. 95% nac": sa.get("cob95_nacional"), "Cob. 50% UF": sa.get("cob50_uf"),
                     "Cob. 80% UF": sa.get("cob80_uf"), "Cob. 95% UF": sa.get("cob95_uf"),
                     "CRPS nac": sa.get("crps_nacional"), "CRPS UF": sa.get("crps_uf"),
                     "Brier nac": sa.get("brier_nacional"), "Brier UF": sa.get("brier_uf"),
                     "Log-loss UF": sa.get("logloss_uf")})
    st = fin["temporal"]["score"]
    rows.append({"Visão": "Calibrado, prior temporal", "Cob. 50% nac": st.get("cob50_nacional"),
                 "Cob. 80% nac": st.get("cob80_nacional"), "Cob. 95% nac": st.get("cob95_nacional"),
                 "Cob. 50% UF": st.get("cob50_uf"), "Cob. 80% UF": st.get("cob80_uf"), "Cob. 95% UF": st.get("cob95_uf"),
                 "CRPS nac": st.get("crps_nacional"), "CRPS UF": st.get("crps_uf"), "Brier nac": st.get("brier_nacional"),
                 "Brier UF": st.get("brier_uf"), "Log-loss UF": st.get("logloss_uf")})
    df = pd.DataFrame(rows)
    for c in df.columns:
        if c.startswith("Cob"):
            df[c] = df[c] * 100
    L.append(tabela_md(df, list(df.columns), dec={"CRPS nac": 2, "CRPS UF": 2, "Brier nac": 3, "Brier UF": 3,
                                                  "Log-loss UF": 3}))
    L.append("\nCobertura = % dos resultados reais dentro do intervalo central de 50/80/95% (ideal: 50/80/95). "
             "CRPS em p.p. (menor = melhor). Brier/log-loss das probabilidades de vitória (nacional: PT 1º no "
             "1º turno e PT vence; UF: PT 1º na UF no 1º turno e PT vence a UF no 2º turno).\n")
    # nacional detalhado
    L.append("## Nacional, modelo calibrado (LOEO)\n")
    nac = cont[cont.nivel == "nacional"].copy()
    nac["Intervalo 80%"] = nac.apply(lambda r: f"{_fmt(r.p10)}–{_fmt(r.p90)}", axis=1)
    nac["Intervalo 95%"] = nac.apply(lambda r: f"{_fmt(r.p025)}–{_fmt(r.p975)}", axis=1)
    L.append(tabela_md(nac, ["ano", "alvo", "var", "real", "mediana", "erro_mediana", "Intervalo 80%", "Intervalo 95%",
                             "pit", "cob80", "cob95"],
                       ["Ano", "Alvo", "Variável", "Real", "Mediana", "Erro", "80%", "95%", "PIT", "Em 80%", "Em 95%"],
                       {"pit": 2}))
    L.append("\npt1/opp1 = válidos do PT/adversário no 1º turno; T = terceira via; margem = PT − adversário; "
             "q = PT no 2º turno.\n")
    pn = prob[prob.nivel == "nacional"]
    L.append(tabela_md(pn, ["ano", "alvo", "evento", "p", "y", "brier"], ["Ano", "Alvo", "Evento", "P(modelo)", "Ocorreu",
                                                                           "Brier"], {"p": 3, "brier": 3}))
    # por UF
    L.append("\n## UFs, modelo calibrado (LOEO)\n")
    uf = cont[cont.nivel == "uf"]
    g = uf.groupby(["ano", "alvo", "var"]).agg(n=("crps", "size"), mae=("erro_mediana", lambda x: x.abs().mean()),
                                               vies=("erro_mediana", "mean"), cob50=("cob50", "mean"),
                                               cob80=("cob80", "mean"), cob95=("cob95", "mean"),
                                               crps=("crps", "mean")).reset_index()
    for c in ("cob50", "cob80", "cob95"):
        g[c] *= 100
    L.append(tabela_md(g, list(g.columns), ["Ano", "Alvo", "Var.", "UFs", "Erro abs. médio", "Erro médio (viés)",
                                            "Cob. 50%", "Cob. 80%", "Cob. 95%", "CRPS"], {"crps": 2}))
    pu = prob[prob.nivel == "uf"].groupby(["ano", "alvo", "evento"]).agg(
        n=("brier", "size"), brier=("brier", "mean"), logloss=("logloss", "mean"),
        acertos=("p", lambda x: 0)).reset_index()
    acc = prob[prob.nivel == "uf"].assign(ac=lambda d: ((d.p > 0.5) == (d.y == 1)).astype(float)) \
        .groupby(["ano", "alvo", "evento"]).ac.mean().values
    pu["acertos"] = acc * 100
    L.append("\n" + tabela_md(pu, list(pu.columns), ["Ano", "Alvo", "Evento", "UFs", "Brier", "Log-loss",
                                                       "% UFs com favorito certo"], {"brier": 3, "logloss": 3}))
    # piores UFs
    w = uf.reindex(uf.erro_mediana.abs().sort_values(ascending=False).index).head(12)
    L.append("\nMaiores erros por UF (mediana − real, p.p.):\n")
    L.append(tabela_md(w, ["ano", "alvo", "var", "uf", "real", "mediana", "erro_mediana", "pit", "cob95"],
                       ["Ano", "Alvo", "Var.", "UF", "Real", "Mediana", "Erro", "PIT", "Em 95%"], {"pit": 3}))
    # PIT
    L.append("\n## Histograma PIT (todas as variáveis, nacional + UF, modelo calibrado)\n")
    h = pit_hist(cont)
    L.append("| Faixa | " + " | ".join(f"{i / 10:.1f}–{(i + 1) / 10:.1f}" for i in range(10)) + " |")
    L.append("|---|" + "---|" * 10)
    L.append("| n | " + " | ".join(str(x) for x in h) + " |")
    L.append("\nUm modelo calibrado tem PIT uniforme (barras iguais). Barras altas nas pontas = intervalos estreitos; "
             "acúmulo num lado = viés. Os PITs das UFs de um mesmo ano são fortemente correlacionados (o erro "
             "nacional é comum), então o histograma tem muito menos informação independente do que o número de "
             "pontos sugere.\n")
    # LOEO da grade
    if rel:
        L.append("## Escolha dos parâmetros (grade + leave-one-election-out)\n")
        L.append("Peso das pesquisas de 2º turno (0,5) e encolhimento do viés (tau0 = 2 p.p.) fixos por princípio: só 2–3 eleições os informam. Limites inferiores dos pisos estaduais pelo conhecimento prévio (Pindograma: MAE de 2,25–4,34 p.p.). Escolha por blocos: entre as combinações cuja cobertura média é de pelo menos 75% no intervalo de 80% e 90% no de 95% (evita intervalos estreitos demais), a de menor CRPS médio; cada bloco usa os parâmetros já escolhidos dos "
                 "anteriores. 'Fora da amostra' = CRPS do ano deixado de fora com os parâmetros escolhidos nos "
                 "outros anos; 'na amostra' = com os parâmetros escolhidos em todos os anos.\n")
        for nome, d in rel.items():
            L.append(f"**Bloco {nome}** — escolhido: `{json.dumps(d['melhor'])}` (CRPS médio {_fmt(d['crps'], 3)}).")
            if any(k in FIXOS for k in d["melhor"]):
                L.append(f"Sem fixar o encolhimento, a grade escolheria `{json.dumps(d['sem_fixar_encolhimento']['melhor'])}` "
                         f"(CRPS {_fmt(d['sem_fixar_encolhimento']['crps'], 3)}); o encolhimento fica fixo por princípio "
                         "(ver abaixo).")
            L.append("")
            t = pd.DataFrame([{"Ano deixado de fora": a, "Escolha sem ele": json.dumps(v["escolha"]),
                               "CRPS fora": v["crps_fora"], "CRPS na amostra": v["crps_insample"]}
                              for a, v in d["loeo"].items()])
            L.append(tabela_md(t, list(t.columns), dec={"CRPS fora": 3, "CRPS na amostra": 3}) + "\n")
    # tau0 sensibilidade
    if rel and "nac1" in rel:
        gr = pd.DataFrame(rel["nac1"]["grade"])
        m = rel["nac1"]["melhor"]
        sel = gr
        for k in ("erro_nacional_1t.dp_p2_pp", "erro_nacional_1t.gl_t", "terceira_via.dp_log"):
            sel = sel[sel[k] == m[k]]
        s = sel.groupby("vies.tau0_p2_pp").crps.mean().reset_index()
        s["vies.tau0_p2_pp"] = s["vies.tau0_p2_pp"].map(lambda x: "∞ (sem encolhimento)" if x > 1e8 else _fmt(x))
        L.append("Sensibilidade ao encolhimento do viés do 1º turno (tau0, p.p.; LOEO, demais parâmetros fixos):\n")
        L.append(tabela_md(s, ["vies.tau0_p2_pp", "crps"], ["tau0 p2", "CRPS nacional 1T"], {"crps": 3}) + "\n")
    if rel and "nac2" in rel:
        gr = pd.DataFrame(rel["nac2"]["grade"])
        m = rel["nac2"]["melhor"]
        sel = gr[(gr["erro_2t.dp_q_pp_vespera_1t"] == m["erro_2t.dp_q_pp_vespera_1t"]) &
                 (gr["erro_2t.peso_pesquisas_vespera_1t"] == m["erro_2t.peso_pesquisas_vespera_1t"])]
        s = sel.groupby("vies.tau0_q_pp").crps.mean().reset_index()
        s["vies.tau0_q_pp"] = s["vies.tau0_q_pp"].map(lambda x: "∞ (sem encolhimento)" if x > 1e8 else _fmt(x))
        L.append("Sensibilidade ao encolhimento do viés do 2º turno projetado na véspera do 1º (tau0, p.p.):\n")
        L.append(tabela_md(s, ["vies.tau0_q_pp", "crps"], ["tau0 q", "CRPS nacional 2T"], {"crps": 3}) + "\n")
    # indecisos
    L.append("## Indecisos: rejeição/2ª preferência x proporcional\n")
    ti = pd.DataFrame(fin["indecisos"])
    L.append(tabela_md(ti, ["ano", "turno", "real", "proporcional", "rejeicao", "erro_prop", "erro_rej", "fonte"],
                       ["Ano", "Turno", "Real (p2 ou q)", "Proporcional", "Rejeição/2ª pref.", "Erro prop.",
                        "Erro rej.", "Informação usada"], {}))
    L.append("""
Leitura: a alocação por "espaço" (100 − rejeição − intenção) ou por 2ª preferência leva os indecisos para quem
tem menos rejeição relativa à intenção atual. A linha de 2022 com a 2ª preferência da Quaest usa informação
publicada depois da eleição e serve só para validar o método (não entra na calibração).
""")
    return "\n".join(L)


def exportar_json(P, rel, fin, caminho=DADOS / "backtest_saida.json"):
    vc = fin["visoes"]["calibrado"]
    cont = vc["cont"]
    js = {
        "gerado_em": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
        "parametros": {k: _py(P[k]) for k in sorted(set().union(*[set(g) for g in (GRADE_NAC1, GRADE_NAC2, GRADE_NAC3,
                                                                                     GRADE_UF)]))},
        "scores": {v: fin["visoes"][v]["score"] for v in M.VISOES} | {"calibrado_temporal": fin["temporal"]["score"]}
        | ({"calibrado_aninhado": fin["aninhado"]["score"]} if "aninhado" in fin else {}),
        "nacional": cont[cont.nivel == "nacional"].round(3).to_dict(orient="records"),
        "prob_nacional": vc["prob"][vc["prob"].nivel == "nacional"].round(4).to_dict(orient="records"),
        "uf_resumo": cont[cont.nivel == "uf"].groupby(["ano", "alvo", "var"]).agg(
            mae=("erro_mediana", lambda x: float(x.abs().mean())), vies=("erro_mediana", "mean"),
            cob50=("cob50", "mean"), cob80=("cob80", "mean"), cob95=("cob95", "mean"),
            n=("crps", "size")).reset_index().round(3).to_dict(orient="records"),
        "uf_pontos": cont[cont.nivel == "uf"][["ano", "alvo", "var", "uf", "real", "mediana", "p10", "p90", "pit"]]
        .round(2).to_dict(orient="records"),
        "pit_hist": pit_hist(cont),
        "cobertura_curva": [{"nominal": q, **{v: float(np.mean(np.abs(fin["visoes"][v]["cont"].pit - 0.5) <= q / 2))
                                              for v in M.VISOES}}
                            for q in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)],
        "erros_historicos": {int(a): {k: (None if v is None else float(v)) for k, v in d.items()}
                             for a, d in fin["erros"].items()},
        "indecisos": fin["indecisos"],
        "loeo": {k: {"melhor": v["melhor"], "loeo": v["loeo"]} for k, v in (rel or {}).items()},
    }
    caminho.write_text(json.dumps(js, ensure_ascii=False, default=_py, allow_nan=False), encoding="utf-8")
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="pula a grade; usa premissas.json")
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    t0 = time.perf_counter()
    P = M.carregar_premissas()
    rel = None
    if not a.rapido:
        Pc, rel = calibrar(P, n=a.n or P["simulacao.n_backtest"])
        mud = {k: (P[k], Pc[k]) for k in Pc if not k.startswith("_") and Pc[k] != P[k]}
        print("parâmetros escolhidos (premissas -> backtest):", mud)
        P = Pc
    fin = avaliar_final(P, n=40000, rel=rel)
    fin["_err_obj"] = erros_brutos(P)
    tempo = time.perf_counter() - t0
    (AQUI / "BACKTEST.md").write_text(escrever(P, rel, fin, tempo), encoding="utf-8")
    exportar_json(P, rel, fin)
    print(f"BACKTEST.md e data/backtest_saida.json gravados ({tempo:.0f} s)")


if __name__ == "__main__":
    main()
