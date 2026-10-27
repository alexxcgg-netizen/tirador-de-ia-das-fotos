"""Modelo alternativo do 2º turno de 2026 (Lula x Flávio Bolsonaro, 25/10/2026).

Método deliberadamente diferente do simulador principal (que parte de pesquisas
de 2º turno + matrizes de transferência): aqui o 2º turno é previsto **só a partir
do resultado real do 1º turno por UF**, por uma regressão empírica estimada nas
eleições presidenciais de 2002 a 2022 (TSE), com incerteza tirada dos resíduos
leave-one-election-out (LOO).

Regressão (por UF i, eleição e; 27 UFs, sem exterior/trânsito):

    logit(y_ie) = b0 + b1 * logit(x_ie) + b2 * t_ie + r_ie

    y = fatia do PT entre os dois no 2º turno (votos válidos)
    x = PT / (PT + principal oponente) no 1º turno
    t = 1 - PT - oponente  (fatia agregada dos demais candidatos no 1º turno)

ou seja, 1T PT, 1T oponente e 1T terceiros entram (as três somam 1, por isso
duas variáveis bastam). Mínimos quadrados ponderados por sqrt(votos válidos).

Incerteza: resíduo LOO r_ie = efeito nacional d_e (média ponderada por votos do
2º turno) + desvio estadual u_ie. Na simulação sorteia-se d de uma eleição e o
vetor u (inteiro, preserva correlação entre UFs) de outra, ambos com bootstrap
suavizado (Silverman, com correção de variância). O nacional é a soma por UF
ponderada pelos votos válidos esperados no 2º turno (votos válidos do 1º turno de
2026 x razão histórica 2T/1T da UF, com ruído histórico).

Variante (separada): mistura com as pesquisas de 2º turno feitas antes do 1º
turno, cada instituto corrigido pelo seu erro medido de margem no 1º turno de 2026
(``avaliacao_1t.json``). A incerteza das pesquisas vem do backtest 2018/2022 do
mesmo procedimento.
"""
from __future__ import annotations

import json
import os
import re

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DADOS = os.path.join(RAIZ, "simulador", "data")
ARQ_HIST = os.path.join(RAIZ, "research_notes", "Briefing eleição 2026 complemento",
                        "resultados_uf_2002_2022.csv")
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
       "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
       "SE", "SP", "TO"]
ANOS = [2002, 2006, 2010, 2014, 2018, 2022]
DATA_1T = {2014: "2014-10-05", 2018: "2018-10-07", 2022: "2022-10-02", 2026: "2026-10-04"}


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def expit(z):
    return 1.0 / (1.0 + np.exp(-np.asarray(z, dtype=float)))


# --------------------------------------------------------------------------- dados

def carregar_historico(caminho=ARQ_HIST) -> pd.DataFrame:
    """Uma linha por (ano, uf) com x, t, y e votos válidos do 1T e 2T."""
    d = pd.read_csv(caminho)
    a = d[d.turno == 1].set_index(["ano", "uf"])
    b = d[d.turno == 2].set_index(["ano", "uf"])
    m = a[["eleitorado", "votos_validos", "pt_pct_validos", "oponente_pct_validos"]].join(
        b[["votos_validos", "pt_2p_pct"]], rsuffix="_2t", how="inner").reset_index()
    m = m.rename(columns={"votos_validos": "vv1", "votos_validos_2t": "vv2"})
    p = m.pt_pct_validos / 100
    o = m.oponente_pct_validos / 100
    m["x"] = p / (p + o)
    m["t"] = 1 - p - o
    m["y"] = m.pt_2p_pct / 100
    m["razao_vv"] = m.vv2 / m.vv1
    return m


def carregar_1t_2026(dir_dados=DIR_DADOS) -> pd.DataFrame:
    """Resultado real do 1T de 2026 por UF (avaliacao_1t.json) + votos válidos do TSE."""
    av = json.load(open(os.path.join(dir_dados, "avaliacao_1t.json"), encoding="utf-8"))
    linhas = []
    for uf, r in av["real"]["ufs"].items():
        tot = sum(v for v in r.values())
        p, o = r["Lula"] / tot, r["Flavio"] / tot
        arq = os.path.join(dir_dados, "tse_1t_2026", f"{uf.lower()}-c0001-e006257-u.json")
        tse = json.load(open(arq, encoding="utf-8"))
        linhas.append(dict(uf=uf, p=p, o=o, x=p / (p + o), t=1 - p - o,
                           vv1=float(tse["v"]["vv"]), eleitorado=float(tse["e"]["te"]),
                           comparecimento=float(tse["e"]["c"]),
                           pst=float(tse["s"]["pstn"].replace(",", "."))))
    return pd.DataFrame(linhas).set_index("uf")


def avaliacao_1t(dir_dados=DIR_DADOS) -> dict:
    return json.load(open(os.path.join(dir_dados, "avaliacao_1t.json"), encoding="utf-8"))


# ---------------------------------------------------------------------- regressão

ESPECIFICACOES = {
    # principal: 1T PT, oponente e terceiros (via logit(x) e t)
    "principal": lambda lx, t: np.c_[np.ones(len(lx)), lx, t],
    # sensibilidade
    "interacao": lambda lx, t: np.c_[np.ones(len(lx)), lx, t, t * lx],
    "so_x": lambda lx, t: np.c_[np.ones(len(lx)), lx],
}


def matriz(df, spec="principal") -> np.ndarray:
    return ESPECIFICACOES[spec](logit(df.x.values), df.t.values)


def ajustar(df, spec="principal") -> np.ndarray:
    w = np.sqrt(np.sqrt(df.vv1.values))  # pesos sqrt(vv) => fator sqrt(w) nas linhas
    X = matriz(df, spec) * w[:, None]
    return np.linalg.lstsq(X, logit(df.y.values) * w, rcond=None)[0]


def prever_logit(beta, df, spec="principal") -> np.ndarray:
    return matriz(df, spec) @ beta


def nacional(share, pesos) -> float:
    return float(np.sum(share * pesos) / np.sum(pesos))


def residuos_loo(hist: pd.DataFrame, anos=None, excluir=(), spec="principal"):
    """Resíduos leave-one-election-out em logit para cada ano de ``anos``,
    ajustando sem esse ano e sem os de ``excluir``. Retorna dict ano -> dict."""
    uf = hist[hist.uf.isin(UFS)]
    anos = [a for a in (anos or ANOS) if a not in excluir]
    out = {}
    for e in anos:
        tr = uf[(uf.ano != e) & (~uf.ano.isin(excluir))]
        te = uf[uf.ano == e].set_index("uf").loc[UFS]
        beta = ajustar(tr, spec)
        z = prever_logit(beta, te, spec)
        r = logit(te.y.values) - z
        w = te.vv2.values
        d = nacional(r, w)
        out[e] = dict(beta=beta, z=z, r=r, d=d, u=r - d, y=te.y.values, w=w,
                      pred_nac=nacional(expit(z), w), real_nac=nacional(te.y.values, w))
    return out


# ------------------------------------------------------------------- bootstrap

def _suav(vals, idx, z, h_frac=None):
    """Bootstrap suavizado com correção de variância (Silverman & Young 1987);
    a variância resultante é a amostral com ddof=1 (com K = 5 ou 6 eleições, a
    variância populacional subestimaria a dispersão).

    vals: (K,) ou (K, U). idx: índices sorteados (n,). z: ruído N(0,1) com a forma de
    vals[idx]. h = 1,06 n^{-1/5} (regra de Silverman, em unidades de dp)."""
    vals = np.asarray(vals, dtype=float)
    K = vals.shape[0]
    h = 1.06 * K ** (-0.2) if h_frac is None else h_frac
    mu = vals.mean(axis=0)
    if K < 2:
        return np.broadcast_to(mu, z.shape).copy()
    sd = vals.std(axis=0, ddof=1)
    sd0 = vals.std(axis=0, ddof=0)
    # reescala os pontos para que a variância total seja a amostral sem viés (ddof=1)
    c = np.divide(sd, sd0, out=np.ones_like(np.asarray(sd, dtype=float)), where=sd0 > 0)
    return mu + (c * (vals[idx] - mu) + h * sd * z) / np.sqrt(1 + h ** 2)


def simular(z_base, w_base, pool_d, pool_u, n, rng, sd_razao=None):
    """Simula UFs (n, U) e nacional (n,) em fatia de Lula (0-1).

    z_base: logit previsto por UF; w_base: votos válidos esperados no 2T por UF;
    pool_d: (K,) efeitos nacionais LOO; pool_u: (K, U) desvios estaduais LOO."""
    U = len(z_base)
    K = len(pool_d)
    d = _suav(pool_d, rng.integers(0, K, n), rng.standard_normal(n))
    u = _suav(pool_u, rng.integers(0, K, n), rng.standard_normal((n, U)))
    sh = expit(z_base[None, :] + d[:, None] + u)
    w = np.broadcast_to(w_base, (n, U))
    if sd_razao is not None:
        w = w * np.exp(rng.standard_normal((n, U)) * sd_razao[None, :])
    nac = np.sum(sh * w, axis=1) / np.sum(w, axis=1)
    return sh, nac


# ---------------------------------------------------------------------- backtest

def backtest(hist: pd.DataFrame, n=100_000, seed=1, anos=ANOS, spec="principal"):
    """Para cada eleição alvo: ajusta sem ela; o pool de erros vem de LOO aninhado
    (cada outra eleição prevista por um ajuste que também exclui o alvo), de modo que
    o ano-alvo nunca entra nem nos coeficientes nem na incerteza."""
    rng = np.random.default_rng(seed)
    uf = hist[hist.uf.isin(UFS)]
    res = []
    for e in anos:
        outer = residuos_loo(hist, anos=[e], spec=spec)[e]
        inner = residuos_loo(hist, excluir=(e,), spec=spec)
        pool_d = np.array([v["d"] for v in inner.values()])
        pool_u = np.array([v["u"] for v in inner.values()])
        te = uf[uf.ano == e].set_index("uf").loc[UFS]
        tr = uf[uf.ano != e]
        razao = tr.groupby("uf").razao_vv.mean().loc[UFS].values
        sdr = tr.groupby("uf").razao_vv.apply(lambda s: np.log(s).std()).loc[UFS].values
        w_prev = te.vv1.values * razao
        sh, nac = simular(outer["z"], w_prev, pool_d, pool_u, n, rng, sdr)
        real = outer["real_nac"]
        prev = nacional(expit(outer["z"]), w_prev)
        q = lambda a, p: np.quantile(a, p, axis=0)
        cov = lambda lo, hi, v: (lo <= v) & (v <= hi)
        res.append(dict(
            ano=int(e), previsto=round(100 * prev, 2), real=round(100 * real, 2),
            erro_nacional=round(100 * (prev - real), 2),
            mae_uf=round(100 * float(np.mean(np.abs(expit(outer["z"]) - te.y.values))), 2),
            pit_nacional=round(float(np.mean(nac <= real)), 3),
            nac_em_80=bool(cov(q(nac, .1), q(nac, .9), real)),
            nac_em_95=bool(cov(q(nac, .025), q(nac, .975), real)),
            cobertura_uf_80=round(float(np.mean(cov(q(sh, .1), q(sh, .9), te.y.values))), 3),
            cobertura_uf_95=round(float(np.mean(cov(q(sh, .025), q(sh, .975), te.y.values))), 3),
            acerto_vencedor_uf=round(float(np.mean((expit(outer["z"]) > .5) == (te.y.values > .5))), 3),
            p_pt=round(float(np.mean(nac > .5)), 3), pt_venceu=bool(real > .5),
        ))
    return res


def resumir_backtest(bt, anos=(2006, 2010, 2014, 2018, 2022)):
    s = [b for b in bt if b["ano"] in anos]
    e = np.array([b["erro_nacional"] for b in s])
    return dict(
        anos=list(anos),
        rmse_nacional=round(float(np.sqrt(np.mean(e ** 2))), 2),
        mae_nacional=round(float(np.mean(np.abs(e))), 2),
        vies_nacional=round(float(np.mean(e)), 2),
        mae_uf=round(float(np.mean([b["mae_uf"] for b in s])), 2),
        cobertura_nac_80=f"{sum(b['nac_em_80'] for b in s)}/{len(s)}",
        cobertura_nac_95=f"{sum(b['nac_em_95'] for b in s)}/{len(s)}",
        cobertura_uf_80=round(float(np.mean([b["cobertura_uf_80"] for b in s])), 3),
        cobertura_uf_95=round(float(np.mean([b["cobertura_uf_95"] for b in s])), 3),
        brier_vencedor=round(float(np.mean([(b["p_pt"] - b["pt_venceu"]) ** 2 for b in s])), 3),
    )


# ------------------------------------------------------------------- pesquisas

def _nome_inst(fonte):
    return re.sub(r"\s*\(.*$", "", fonte).strip()


def pesquisas_2t_corrigidas(dir_dados=DIR_DADOS, ate="2026-10-03"):
    """Última pesquisa de 2º turno de cada instituto antes do 1T, corrigida pelo erro
    de margem do próprio instituto no 1T de 2026 (positivo = superestimou Lula).

    Correção em fatia bipartidária: erro_margem / (2 * (Lula+Flávio reais no 1T))."""
    av = avaliacao_1t(dir_dados)
    err = {_nome_inst(r["fonte"]): r["erro_margem"] for r in av["ranking_pesquisas_margem"]}
    real = av["real"]["nacional"]
    top2 = (real["Lula"] + real["Flavio"]) / 100
    p = pd.read_csv(os.path.join(dir_dados, "pesquisas_nacionais.csv"))
    p = p[(p.campo_fim <= ate) & p.t2_lula.notna() & p.t2_flavio.notna()]
    p = p.sort_values("campo_fim").groupby("instituto").tail(1)
    linhas = []
    for _, r in p.iterrows():
        if r.instituto not in err:
            continue
        bruto = r.t2_lula / (r.t2_lula + r.t2_flavio)
        corr = bruto - err[r.instituto] / 100 / (2 * top2)
        linhas.append(dict(instituto=r.instituto, campo_fim=r.campo_fim,
                           lula_2p_bruto=round(100 * bruto, 2),
                           erro_margem_1t=err[r.instituto],
                           lula_2p_corrigido=round(100 * corr, 2)))
    return pd.DataFrame(linhas)


def backtest_pesquisas_hist(dir_dados=DIR_DADOS, hist=None):
    """Mesmo procedimento em 2018 e 2022 (únicos anos com pesquisas de 2T antes do
    1T): erro da média corrigida (e da bruta) frente ao 2T real, em p.p."""
    hist = carregar_historico() if hist is None else hist
    d = pd.read_csv(os.path.join(dir_dados, "backtest_pesquisas_nacionais.csv"))
    out = []
    for ano in (2018, 2022):
        br1 = hist[(hist.ano == ano) & (hist.uf == "BR")].iloc[0]
        real_m = (br1.x * (1 - br1.t)) - (1 - br1.x) * (1 - br1.t)  # margem 1T (válidos)
        top2 = 1 - br1.t
        t1 = d[(d.ano == ano) & (d.turno_alvo == 1) & (d.campo_fim < DATA_1T[ano])]
        t2 = d[(d.ano == ano) & (d.turno_alvo == 2) & (d.campo_fim < DATA_1T[ano])]
        t1 = t1.sort_values("campo_fim").groupby("instituto").tail(1).set_index("instituto")
        t2 = t2.sort_values("campo_fim").groupby("instituto").tail(1).set_index("instituto")
        brutos, corrs = [], []
        for inst in t2.index.intersection(t1.index):
            a = t1.loc[inst]
            if pd.isna(a.bni):
                continue
            em = (a.pt - a.opp) / (100 - a.bni) - real_m
            b = t2.loc[inst]
            bruto = b.pt / (b.pt + b.opp)
            brutos.append(bruto)
            corrs.append(bruto - em / (2 * top2))
        real2 = float(br1.y)
        out.append(dict(ano=ano, n_institutos=len(corrs),
                        erro_bruto=round(100 * (np.mean(brutos) - real2), 2),
                        erro_corrigido=round(100 * (np.mean(corrs) - real2), 2),
                        dp_entre_institutos=round(100 * float(np.std(corrs, ddof=1)), 2)))
    return out


# ------------------------------------------------------------------------ 2026

def prever_2026(n=500_000, seed=2026, hist=None, dados=None, spec="principal"):
    hist = carregar_historico() if hist is None else hist
    dados = carregar_1t_2026() if dados is None else dados
    rng = np.random.default_rng(seed)
    uf = hist[hist.uf.isin(UFS)]
    beta = ajustar(uf, spec)
    loo = residuos_loo(hist, spec=spec)
    pool_d = np.array([loo[a]["d"] for a in ANOS])
    pool_u = np.array([loo[a]["u"] for a in ANOS])

    # Exterior (ZZ): mesma regressão, sem desvio estadual próprio (u = 0).
    reg = UFS + (["ZZ"] if "ZZ" in dados.index else [])
    D = dados.loc[reg]
    z = prever_logit(beta, D, spec)
    hr = hist[hist.ano >= 2006]
    razao = hr.groupby("uf").razao_vv.mean()
    sdr = hr.groupby("uf").razao_vv.apply(lambda s: np.log(s).std())
    w = D.vv1.values * razao.reindex(reg).fillna(razao.loc[UFS].mean()).values
    sd_r = sdr.reindex(reg).fillna(sdr.loc[UFS].mean()).values
    pu = np.c_[pool_u, np.zeros(len(ANOS))] if "ZZ" in reg else pool_u
    sh, nac = simular(z, w, pool_d, pu, n, rng, sd_r)
    return dict(beta=beta, loo=loo, reg=reg, z=z, w=w, sh=sh, nac=nac, dados=D)


def misturar_pesquisas(nac_reg, media_p, sd_p, rng=None):
    """Combina (inverso da variância) a distribuição nacional da regressão com
    N(media_p, sd_p) das pesquisas corrigidas; devolve sorteios nacionais e peso."""
    m_r, s_r = float(np.mean(nac_reg)), float(np.std(nac_reg))
    wp = (1 / sd_p ** 2) / (1 / sd_p ** 2 + 1 / s_r ** 2)
    m_b = wp * media_p + (1 - wp) * m_r
    s_b = 1 / np.sqrt(1 / sd_p ** 2 + 1 / s_r ** 2)
    return m_b + (nac_reg - m_r) * (s_b / s_r), wp, m_b, s_b


def ajustar_ufs_ao_nacional(sh, nac_old, nac_new):
    """Desloca todas as UFs em logit pela diferença nacional (aproximação de 1ª ordem)."""
    dz = logit(nac_new) - logit(nac_old)
    return expit(logit(sh) + dz[:, None])


def resumo_dist(a, casas=2):
    a = 100 * np.asarray(a)
    q = np.quantile(a, [.025, .1, .5, .9, .975])
    return dict(media=round(float(a.mean()), casas), mediana=round(float(q[2]), casas),
                p10=round(float(q[1]), casas), p90=round(float(q[3]), casas),
                p2_5=round(float(q[0]), casas), p97_5=round(float(q[4]), casas),
                dp=round(float(a.std()), casas))
