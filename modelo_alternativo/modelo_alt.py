"""Modelo alternativo (independente) da eleição presidencial de 2026.

Serve de contraprova ao simulador principal (``simulador/``), com
metodologia propositalmente diferente:

1. **Agregação bayesiana dinâmica** (Linzer 2013; Economist 2020): para cada
   componente em escala log-razão, a intenção latente segue um passeio
   aleatório diário e cada pesquisa a observa com efeito de instituto
   (``house effect``, soma zero entre institutos) e ruído amostral + extra:

       y_j = mu_{t_j} + h_{k(j)} + e_j,   e_j ~ N(0, s_j^2 + tau^2)
       mu_t = mu_{t-1} + eta_t,           eta_t ~ N(0, omega^2)
       h ~ N(0, sigma_h^2 (I - 11'/K))    (soma zero)

   A verossimilhança marginal vem exata de um filtro de Kalman (estado
   aumentado [mu, h_1..h_K]); os hiperparâmetros (omega, tau, sigma_h) são
   amostrados por Metropolis com priors meia-normais. Dado cada sorteio dos
   hiperparâmetros o posterior de mu na data-alvo é normal (filtro), logo o
   posterior é uma mistura de normais — amostrada diretamente.

   Componentes: 1º turno z1 = log(PT/adversário), z2 = log(demais/(PT+adv.)),
   composição dos menores z_c = log(c/adversário); 2º turno zq = log(PT/adv.).
   Por serem razões, a base (votos totais ou válidos) é irrelevante — a linha
   do Datafolha de 3/10, publicada em votos válidos, entra sem conversão.

2. **Erro do dia da eleição empírico (bootstrap)**: erro = resultado - média
   final do próprio modelo em 2014/2018/2022, por eleição, no vetor
   conjunto (z1, z2, zq). Sorteia-se uma eleição inteira (preserva a
   correlação 1º/2º turno) e soma-se um núcleo de suavização (bootstrap
   suavizado, Silverman) cuja *forma* vem da dispersão empírica entre os
   institutos naquela véspera; nada de distribuição paramétrica para o erro.
   Variante ``neutro``: o sinal do erro partidário (z1, zq) é sorteado ±
   (troca de papéis entre os dois lados); ``historico``: sinal como ocorreu.

3. **UFs**: swing uniforme a partir de 2022 (em p.p. da fatia bipartidária)
   mais um vetor de desvios estaduais sorteado do histórico do TSE
   (2002→2006, ..., 2018→2022), também com suavização. Sem pesquisas
   estaduais.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DADOS = os.path.join(RAIZ, "simulador", "data")

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
       "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
       "SE", "SP", "TO"]

ELEICOES = {
    2014: {"t1": "2014-10-05", "t2": "2014-10-26"},
    2018: {"t1": "2018-10-07", "t2": "2018-10-28"},
    2022: {"t1": "2022-10-02", "t2": "2022-10-30"},
    2026: {"t1": "2026-10-04", "t2": "2026-10-25"},
}
ANOS_HIST = [2014, 2018, 2022]
N_PADRAO = 2000          # amostra assumida quando não informada
JANELA_NUCLEO_DIAS = 7   # pesquisas finais usadas para a forma do núcleo


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def logit(p):
    return np.log(p / (1.0 - p))


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

@dataclass
class Observacoes:
    """Observações de um componente: tempo (dia inteiro), y, var. amostral, instituto."""
    t: np.ndarray
    y: np.ndarray
    s2: np.ndarray
    casa: list

    def __len__(self):
        return len(self.y)


def _data_media(ini, fim):
    fim = pd.to_datetime(fim)
    ini = pd.to_datetime(ini) if isinstance(ini, str) and ini else fim
    if pd.isna(ini):
        ini = fim
    return ini + (fim - ini) / 2


def _obs_razao(df, num, den, n, t0):
    """Constrói observações de log(num/den) com var = (1/a + 1/b)/n_eff.

    ``num``/``den`` são séries em % da base válida (a e b como frações)."""
    ok = num.notna() & den.notna() & (num > 0) & (den > 0) & n.notna()
    a, b = num[ok] / 100.0, den[ok] / 100.0
    neff = n[ok].astype(float)
    y = np.log(a / b).to_numpy()
    s2 = ((1.0 / a + 1.0 / b) / neff).to_numpy()
    t = ((df.loc[ok, "data"] - t0).dt.days).to_numpy().astype(int)
    return Observacoes(t=t, y=y, s2=s2, casa=df.loc[ok, "instituto"].tolist())


def _validos_1t(pt, opp, bni, menores_df, outros):
    """Fatias em % dos válidos: PT, adversário e 'demais' (todo o resto).

    Se brancos/nulos/indecisos (bni) é conhecido, válidos = 100 - bni e
    demais = válidos - PT - adv. (inclui não listados). Caso contrário,
    demais = soma dos menores listados (só se todos foram informados)."""
    validos = 100.0 - bni
    demais = validos - pt - opp
    soma_men = menores_df.sum(axis=1, min_count=1)
    if outros is not None:
        soma_men = soma_men + outros.fillna(0)
    todos_men = menores_df.notna().all(axis=1)
    sem_bni = bni.isna()
    demais = demais.where(~sem_bni, soma_men.where(todos_men))
    validos = validos.where(~sem_bni, (pt + opp + demais))
    f = 100.0 / validos
    return pt * f, opp * f, demais * f, validos


@dataclass
class DadosEleicao:
    ano: int
    t0: pd.Timestamp
    alvo: pd.Timestamp            # data-alvo da agregação (véspera do 1º turno)
    p1: pd.DataFrame              # pesquisas de 1º turno (válidos)
    p2: pd.DataFrame              # pesquisas de 2º turno
    menores: list                 # nomes dos candidatos menores modelados
    comps: dict = field(default_factory=dict)   # nome -> Observacoes


def _montar(ano, p1, p2, menores, alvo):
    t0 = min(p1["data"].min() if len(p1) else alvo,
             p2["data"].min() if len(p2) else alvo)
    d = DadosEleicao(ano=ano, t0=t0, alvo=alvo, p1=p1, p2=p2, menores=menores)
    n1 = p1["n_validos"]
    # z1 usa as colunas brutas: a razão PT/adv. independe da base (totais ou válidos)
    d.comps["z1"] = _obs_razao(p1, p1["pt_bruto"], p1["opp_bruto"], n1, t0)
    d.comps["z2"] = _obs_razao(p1, p1["dem_v"], p1["pt_v"] + p1["opp_v"], n1, t0)
    for c in menores:
        d.comps["m_" + c] = _obs_razao(p1, p1[c + "_v"], p1["opp_v"], n1, t0)
    if len(p2):
        d.comps["zq"] = _obs_razao(p2, p2["q_pt"], p2["q_opp"], p2["n_q"], t0)
    return d


def carregar_2026(ate=None):
    """Pesquisas nacionais de 2026 (lado PT = Lula, adversário = Flávio)."""
    df = pd.read_csv(os.path.join(DIR_DADOS, "pesquisas_nacionais.csv"))
    df["data"] = [_data_media(i, f) for i, f in zip(df["campo_inicio"], df["campo_fim"])]
    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    alvo = pd.Timestamp(ELEICOES[2026]["t1"]) - pd.Timedelta(days=1)
    if ate is not None:
        alvo = pd.Timestamp(ate)
    df = df[pd.to_datetime(df["campo_fim"]) <= alvo].copy()
    df["n"] = df["n"].fillna(N_PADRAO)
    menores = ["renan", "cury", "caiado", "zema"]
    # 1º turno: exclui cenários com candidatos que não concorrem (Tarcísio, Ratinho, Ciro)
    obs = df["obs"].fillna("").str.lower()
    cen = obs.str.contains("cenario com")
    p1 = df[df["lula"].notna() & df["flavio"].notna() & ~cen].copy()
    pt, opp, dem, val = _validos_1t(p1["lula"], p1["flavio"], p1["bni"],
                                    p1[menores], p1["outros"])
    p1["pt_v"], p1["opp_v"], p1["dem_v"] = pt, opp, dem
    p1["pt_bruto"], p1["opp_bruto"] = p1["lula"], p1["flavio"]
    p1["n_validos"] = p1["n"] * (val / 100.0).fillna(0.9).clip(upper=1.0)
    f = 100.0 / val.fillna(p1[["lula", "flavio"] + menores].sum(axis=1) + 2.0)
    for c in menores:
        p1[c + "_v"] = p1[c] * f
    p2 = df[df["t2_lula"].notna() & df["t2_flavio"].notna()].copy()
    p2["q_pt"], p2["q_opp"] = p2["t2_lula"], p2["t2_flavio"]
    p2["n_q"] = p2["n"] * (p2["t2_lula"] + p2["t2_flavio"]) / 100.0
    return _montar(2026, p1.reset_index(drop=True), p2.reset_index(drop=True), menores, alvo)


def carregar_historico(ano):
    """Pesquisas de 2014/2018/2022 disponíveis até a véspera do 1º turno."""
    df = pd.read_csv(os.path.join(DIR_DADOS, "backtest_pesquisas_nacionais.csv"))
    df = df[df["ano"] == ano].copy()
    df["data"] = [_data_media(i, f) for i, f in zip(df["campo_inicio"], df["campo_fim"])]
    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    alvo = pd.Timestamp(ELEICOES[ano]["t1"]) - pd.Timedelta(days=1)
    df = df[pd.to_datetime(df["campo_fim"]) <= alvo]
    df["n"] = df["n"].fillna(N_PADRAO)
    p1 = df[df["turno_alvo"] == 1].copy()
    # nomes dos menores: colunas c3..c6 com nome
    nomes = []
    for k in ["c3", "c4", "c5", "c6"]:
        for nm in p1[k + "_nome"].dropna().unique():
            if nm not in nomes:
                nomes.append(nm)
    menores = [n.lower() for n in nomes]
    for nm in nomes:
        col = pd.Series(np.nan, index=p1.index)
        for k in ["c3", "c4", "c5", "c6"]:
            col = col.where(p1[k + "_nome"] != nm, p1[k])
        p1[nm.lower()] = col
    pt, opp, dem, val = _validos_1t(p1["pt"], p1["opp"], p1["bni"], p1[menores], p1["outros"])
    p1["pt_v"], p1["opp_v"], p1["dem_v"] = pt, opp, dem
    p1["pt_bruto"], p1["opp_bruto"] = p1["pt"], p1["opp"]
    p1["n_validos"] = p1["n"] * (val / 100.0).fillna(0.85)
    for c in menores:
        p1[c + "_v"] = p1[c] * 100.0 / val
    p2 = df[df["turno_alvo"] == 2].copy()
    p2["q_pt"], p2["q_opp"] = p2["pt"], p2["opp"]
    p2["n_q"] = p2["n"] * (p2["pt"] + p2["opp"]) / 100.0
    return _montar(ano, p1.reset_index(drop=True), p2.reset_index(drop=True), menores, alvo)


def resultado_nacional(ano):
    r = pd.read_csv(os.path.join(DIR_DADOS, "resultados_uf_2002_2022.csv"))
    r = r[r["uf"] == "BR"]
    t1 = r[(r["ano"] == ano) & (r["turno"] == 1)].iloc[0]
    t2 = r[(r["ano"] == ano) & (r["turno"] == 2)].iloc[0]
    pt, opp = float(t1["pt_pct_validos"]), float(t1["oponente_pct_validos"])
    return {"pt_1t": pt, "opp_1t": opp, "demais_1t": 100.0 - pt - opp,
            "q_2t": float(t2["pt_2p_pct"]),
            "terceiro_1t": float(t1["terceiro1_pct_validos"])}


def resultados_uf():
    r = pd.read_csv(os.path.join(DIR_DADOS, "resultados_uf_2002_2022.csv"))
    r = r[r["uf"].isin(UFS + ["BR"])]
    out = {}
    for (ano, turno), g in r.groupby(["ano", "turno"]):
        out[(int(ano), int(turno))] = g.set_index("uf")["pt_2p_pct"].astype(float)
    return out


# ---------------------------------------------------------------------------
# Filtro de Kalman com efeitos de instituto
# ---------------------------------------------------------------------------

def filtro_kalman(obs: Observacoes, t_alvo, omega, tau, sigma_h, mu0, v0,
                  casas=None, guardar=False):
    """Filtro de Kalman do passeio aleatório + efeitos de instituto (soma zero).

    Retorna (loglik, m_mu_alvo, v_mu_alvo, media_h, casas, var_h[, historico])."""
    if casas is None:
        casas = sorted(set(obs.casa))
    idx = {c: i for i, c in enumerate(casas)}
    K = len(casas)
    m = np.zeros(K + 1)
    m[0] = mu0
    P = np.zeros((K + 1, K + 1))
    P[0, 0] = v0
    if K > 1:
        P[1:, 1:] = sigma_h ** 2 * (np.eye(K) - np.ones((K, K)) / K)
    ordem = np.argsort(obs.t, kind="stable")
    t_cur = int(obs.t[ordem[0]]) if len(obs) else int(t_alvo)
    ll = 0.0
    w2, r_extra = omega ** 2, tau ** 2
    hist = []
    for j in ordem:
        tj = int(obs.t[j])
        if tj > t_cur:
            P[0, 0] += w2 * (tj - t_cur)
            t_cur = tj
        k = 1 + idx[obs.casa[j]]
        PH = P[:, 0] + P[:, k]
        S = PH[0] + PH[k] + obs.s2[j] + r_extra
        v = obs.y[j] - (m[0] + m[k])
        G = PH / S
        m = m + G * v
        P = P - np.outer(PH, G)
        ll += -0.5 * (math.log(2 * math.pi * S) + v * v / S)
        if guardar:
            hist.append((tj, m[0], P[0, 0]))
    if t_alvo > t_cur:
        P[0, 0] += w2 * (t_alvo - t_cur)
    saida = (ll, float(m[0]), float(P[0, 0]), m[1:].copy(), casas, np.diag(P)[1:].copy())
    if guardar:
        return saida + (hist,)
    return saida


def suavizar_tendencia(obs: Observacoes, h_media, casas, omega, tau, mu0, v0, t_fim):
    """Trajetória suavizada (RTS escalar) de mu, com efeitos de casa fixos na média."""
    idx = {c: i for i, c in enumerate(casas)}
    y = obs.y - np.array([h_media[idx[c]] for c in obs.casa])
    r = obs.s2 + tau ** 2
    t_ini = int(obs.t.min())
    dias = np.arange(t_ini, int(t_fim) + 1)
    mf = np.zeros(len(dias)); pf = np.zeros(len(dias))
    mp = np.zeros(len(dias)); pp = np.zeros(len(dias))
    m, p = mu0, v0
    for i, d in enumerate(dias):
        if i > 0:
            p = p + omega ** 2
        mp[i], pp[i] = m, p
        sel = obs.t == d
        for yy, rr in zip(y[sel], r[sel]):
            g = p / (p + rr)
            m = m + g * (yy - m)
            p = p * (1 - g)
        mf[i], pf[i] = m, p
    ms, ps = mf.copy(), pf.copy()
    for i in range(len(dias) - 2, -1, -1):
        c = pf[i] / pp[i + 1]
        ms[i] = mf[i] + c * (ms[i + 1] - mp[i + 1])
        ps[i] = pf[i] + c * c * (ps[i + 1] - pp[i + 1])
    return dias, ms, ps


PRIORS = {
    # escalas das meias-normais (omega por dia, tau, sigma_h), em unidades de log-razão
    "principal": (0.02, 0.10, 0.15),
    "menor": (0.05, 0.30, 0.50),
}


def ajustar_componente(obs: Observacoes, t_alvo, escala="principal", n_iter=3000,
                       burn=1000, thin=5, seed=0):
    """MCMC (Metropolis adaptativo) nos log-hiperparâmetros; verossimilhança via Kalman.

    Retorna dicionário com sorteios (m, v) do posterior de mu na data-alvo,
    médias dos efeitos de instituto e resumo dos hiperparâmetros."""
    rng = np.random.default_rng(seed)
    esc = np.array(PRIORS[escala])
    n0 = min(len(obs), 5)
    ordem = np.argsort(obs.t, kind="stable")[:n0]
    mu0, v0 = float(np.mean(obs.y[ordem])), 1.0
    casas = sorted(set(obs.casa))

    def logpost(th):
        x = np.exp(th)
        lp = float(np.sum(-0.5 * (x / esc) ** 2 + th))
        ll = filtro_kalman(obs, t_alvo, x[0], x[1], x[2], mu0, v0, casas)[0]
        return ll + lp

    th = np.log(esc * 0.5)
    lp = logpost(th)
    passo = np.full(3, 0.3)
    aceitos, guard = 0, []
    acc_janela = 0
    for it in range(n_iter):
        prop = th + passo * rng.standard_normal(3)
        lpp = logpost(prop)
        if math.log(rng.random()) < lpp - lp:
            th, lp = prop, lpp
            aceitos += 1
            acc_janela += 1
        if it < burn and (it + 1) % 100 == 0:   # adaptação só no aquecimento
            taxa = acc_janela / 100.0
            passo *= math.exp(taxa - 0.3)
            acc_janela = 0
        if it >= burn and (it - burn) % thin == 0:
            guard.append(th.copy())
    ths = np.array(guard)
    ms, vs, hs, hv = [], [], [], []
    for t in ths:
        x = np.exp(t)
        _, m, v, h, _, vh = filtro_kalman(obs, t_alvo, x[0], x[1], x[2], mu0, v0, casas)
        ms.append(m); vs.append(v); hs.append(h); hv.append(vh)
    xs = np.exp(ths)
    hmed = np.mean(hs, axis=0)
    xmed = np.median(xs, axis=0)
    dias, tend, tend_v = suavizar_tendencia(obs, hmed, casas, xmed[0], xmed[1], mu0, v0, t_alvo)
    return {
        "m": np.array(ms), "v": np.array(vs), "casas": casas, "h_media": hmed,
        "h_dp": np.sqrt(np.mean(hv, axis=0) + np.var(hs, axis=0)),
        "hiper_mediana": {"omega": float(xmed[0]), "tau": float(xmed[1]), "sigma_h": float(xmed[2])},
        "aceitacao": aceitos / n_iter, "n_obs": len(obs),
        "tendencia": (dias, tend, tend_v), "mu0": mu0,
    }


def sortear_posterior(aj, n, rng):
    i = rng.integers(0, len(aj["m"]), n)
    return aj["m"][i] + np.sqrt(aj["v"][i]) * rng.standard_normal(n)


def ajustar_eleicao(dados: DadosEleicao, n_iter=3000, burn=1000, seed=0):
    t_alvo = int((dados.alvo - dados.t0).days)
    out = {}
    for i, (nome, obs) in enumerate(dados.comps.items()):
        if len(obs) < 3:
            continue
        esc = "menor" if nome.startswith("m_") or nome == "z2" else "principal"
        out[nome] = ajustar_componente(obs, t_alvo, esc, n_iter=n_iter, burn=burn,
                                       seed=seed + 101 * i)
    return out


# ---------------------------------------------------------------------------
# Erros históricos (média final do modelo x resultado)
# ---------------------------------------------------------------------------

def erros_eleicao(ano, dados: DadosEleicao, ajuste):
    """Erro (resultado - média do modelo na véspera do 1º turno) em z1, z2, zq,
    e desvios dos institutos finais em torno da média (forma do núcleo)."""
    res = resultado_nacional(ano)
    a = {"z1": math.log(res["pt_1t"] / res["opp_1t"]),
         "z2": math.log(res["demais_1t"] / (res["pt_1t"] + res["opp_1t"])),
         "zq": logit(res["q_2t"] / 100.0)}
    err = {}
    nucleo = {}
    t_alvo = int((dados.alvo - dados.t0).days)
    for c in ["z1", "z2", "zq"]:
        if c not in ajuste:
            err[c] = None
            nucleo[c] = []
            continue
        est = float(np.mean(ajuste[c]["m"]))
        err[c] = a[c] - est
        obs = dados.comps[c]
        # última pesquisa de cada instituto na janela final
        ult = {}
        for t, y, casa in zip(obs.t, obs.y, obs.casa):
            if t >= t_alvo - JANELA_NUCLEO_DIAS and (casa not in ult or t >= ult[casa][0]):
                ult[casa] = (t, y)
        nucleo[c] = {casa: y - est for casa, (t, y) in ult.items()}
    # vetor conjunto (z1, z2) por instituto, centrado
    casas12 = sorted(set(nucleo["z1"]) & set(nucleo["z2"])) if nucleo["z1"] else []
    k12 = np.array([[nucleo["z1"][c], nucleo["z2"][c]] for c in casas12]) if casas12 else np.zeros((0, 2))
    if len(k12):
        k12 = k12 - k12.mean(axis=0)
    kq = np.array(list(nucleo["zq"].values())) if nucleo["zq"] else np.zeros(0)
    if len(kq):
        kq = kq - kq.mean()
    return {"ano": ano, "erro": err, "nucleo12": k12, "nucleoq": kq,
            "resultado": res, "n_institutos_finais": len(casas12)}


@dataclass
class PoolErros:
    anos: list
    A12: np.ndarray        # (E, 2) erros (z1, z2) por eleição
    Aq: np.ndarray         # (E,) erro zq (nan se indisponível)
    K12: np.ndarray        # núcleo padronizado (z1, z2): forma empírica entre institutos
    Kq: np.ndarray         # núcleo padronizado zq
    sigma: dict            # dispersão-alvo por componente (z1, zq: RMS; z2: dp)
    mu: dict               # média com sinal (z1, zq: viés histórico; z2: contração)
    h: dict                # larguras de banda (Silverman)


def _banda(sigma, n):
    """Regra de Silverman: h = 1,06 * sigma * n^(-1/5)."""
    return 1.06 * sigma * max(n, 1) ** (-0.2)


def montar_pool(erros: list, suavizar=True) -> PoolErros:
    A12 = np.array([[e["erro"]["z1"], e["erro"]["z2"]] for e in erros], dtype=float)
    Aq = np.array([np.nan if e["erro"]["zq"] is None else e["erro"]["zq"] for e in erros],
                  dtype=float)
    K12 = np.vstack([e["nucleo12"] for e in erros if len(e["nucleo12"])])
    Kq = np.concatenate([e["nucleoq"] for e in erros if len(e["nucleoq"])])
    K12 = K12 / K12.std(axis=0)
    Kq = Kq / Kq.std()
    aq = Aq[~np.isnan(Aq)]
    if len(aq) == 0:
        raise ValueError("pool sem erro de 2º turno")
    n = len(A12)
    # componentes partidárias: pool simetrizado {+A, -A} => média 0, dp = RMS
    sigma = {"z1": float(np.sqrt(np.mean(A12[:, 0] ** 2))),
             "zq": float(np.sqrt(np.mean(aq ** 2))),
             # 'demais' (contração da terceira via) não é partidária: dp em torno da média
             "z2": float(A12[:, 1].std()) if n > 1 else float(abs(A12[0, 1]))}
    mu = {"z1": float(A12[:, 0].mean()), "zq": float(aq.mean()), "z2": float(A12[:, 1].mean())}
    h = {"z1": _banda(sigma["z1"], n), "z2": _banda(sigma["z2"], n),
         "zq": _banda(sigma["zq"], len(aq))}
    if not suavizar:   # bootstrap puro (só os vetores de erro observados)
        h = {k: 0.0 for k in h}
    return PoolErros(anos=[e["ano"] for e in erros], A12=A12, Aq=Aq, K12=K12, Kq=Kq,
                     sigma=sigma, mu=mu, h=h)


def _suavizar(x, k, mu, sigma, h):
    """Bootstrap suavizado com correção de variância (Silverman & Young 1987):
    mu + (x - mu + h k) / sqrt(1 + h^2/sigma^2)  => preserva média e variância do pool."""
    if sigma <= 0:
        return x
    return mu + (x - mu + h * k) / math.sqrt(1.0 + (h / sigma) ** 2)


def sortear_erros(pool: PoolErros, n, rng, variante="neutro"):
    """Sorteia (d1, d2, dq): eleição inteira (vetor conjunto 1º/2º turno) com
    sinal partidário aleatório, suavizada por um núcleo de forma empírica.

    neutro:    d_partidario = s * A_e (+ núcleo), s = ±1  -> média 0
    historico: neutro + média com sinal dos erros históricos (viés pró-PT observado)
    """
    if variante not in ("neutro", "historico"):
        raise ValueError(variante)
    E = len(pool.A12)
    e = rng.integers(0, E, n)
    a1 = pool.A12[e, 0].copy()
    a2 = pool.A12[e, 1].copy()
    aq = pool.Aq[e].copy()
    com_q = np.where(~np.isnan(pool.Aq))[0]
    falta = np.isnan(aq)
    if falta.any():   # eleição sem pesquisas de 2º turno antes do 1º (2014)
        aq[falta] = pool.Aq[rng.choice(com_q, int(falta.sum()))]
    s = rng.choice([-1.0, 1.0], n)
    k = pool.K12[rng.integers(0, len(pool.K12), n)] * rng.choice([-1.0, 1.0], (n, 1))
    kq = pool.Kq[rng.integers(0, len(pool.Kq), n)] * rng.choice([-1.0, 1.0], n)
    d1 = _suavizar(s * a1, k[:, 0], 0.0, pool.sigma["z1"], pool.h["z1"])
    dq = _suavizar(s * aq, kq, 0.0, pool.sigma["zq"], pool.h["zq"])
    d2 = _suavizar(a2, k[:, 1], pool.mu["z2"], pool.sigma["z2"], pool.h["z2"])
    if variante == "historico":
        d1 = d1 + pool.mu["z1"]
        dq = dq + pool.mu["zq"]
    return d1, d2, dq


# ---------------------------------------------------------------------------
# Desvios estaduais (swing não uniforme) do histórico do TSE
# ---------------------------------------------------------------------------

def desvios_estaduais(turno, excluir_anos=(), ate=2022):
    """Vetores de desvio do swing uniforme por par de eleições consecutivas.

    desvio_uf = (fatia_uf[t] - fatia_uf[t-4]) - (fatia_BR[t] - fatia_BR[t-4]).
    ``excluir_anos``: descarta todo par que contenha um desses anos (evita
    vazamento do resultado do ano testado no backtest)."""
    res = resultados_uf()
    vecs, pares = [], []
    for a in range(2006, ate + 1, 4):
        if a in excluir_anos or (a - 4) in excluir_anos:
            continue
        cur, ant = res[(a, turno)], res[(a - 4, turno)]
        dv = (cur[UFS] - ant[UFS]) - (cur["BR"] - ant["BR"])
        vecs.append(dv.to_numpy())
        pares.append(f"{a-4}->{a}")
    return np.array(vecs), pares


def sortear_desvios_uf(V, n, rng, variante="neutro"):
    """Bootstrap suavizado (com correção de variância) de vetores inteiros de
    desvio estadual — preserva a correlação espacial de cada eleição.
    No neutro o sinal do vetor é sorteado (realinhamentos regionais em qualquer
    direção); no histórico, mantém-se o sinal observado."""
    m = len(V)
    a = rng.integers(0, m, n)
    b = rng.integers(0, m, n)
    h = _banda(1.0, m)
    sa = rng.choice([-1.0, 1.0], (n, 1)) if variante == "neutro" else 1.0
    sb = rng.choice([-1.0, 1.0], (n, 1))
    mu = 0.0 if variante == "neutro" else V.mean(axis=0)
    return mu + (V[a] * sa - mu + h * V[b] * sb) / math.sqrt(1.0 + h * h)


# ---------------------------------------------------------------------------
# Simulação
# ---------------------------------------------------------------------------

QUANTIS = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]


def composicao_ref(ajuste, menores):
    """(fatia do adversário de referência, resíduo não listado) em fração dos válidos."""
    dem = expit(np.mean(ajuste["z2"]["m"]))
    opp = (1 - dem) * (1 - expit(np.mean(ajuste["z1"]["m"])))
    nomeados = sum(opp * np.exp(np.mean(ajuste["m_" + c]["m"])) for c in menores)
    return opp, max(dem - nomeados, 0.0)


def simular(dados: DadosEleicao, ajuste, pool: PoolErros, base_uf, V1, V2,
            n_sims=500_000, variante="neutro", seed=0, lote=100_000,
            nomes=("pt", "opp")):
    """Simula 1º turno, 2º turno e UFs. base_uf: dict turno -> Series (fatia PT bipart., %)."""
    rng = np.random.default_rng(seed)
    menores = [c for c in dados.menores if "m_" + c in ajuste]
    cont = dict(pt_vence=0, opp_vence=0, outro_vence=0, decide_1t=0, pt_vence_1t=0,
                opp_vence_1t=0, top2_pt_opp=0, pt_lidera_1t=0, ha_2t_pt_opp=0)
    uf_pt2 = np.zeros(len(UFS)); uf_pt1 = np.zeros(len(UFS))
    amostras = {"pt_1t": [], "opp_1t": [], "demais_1t": [], "q_2t": [], "uf_q": []}
    for c in menores:
        amostras[c + "_1t"] = []
    restante = n_sims
    b1n, b2n = base_uf[1]["BR"], base_uf[2]["BR"]
    b1, b2 = base_uf[1][UFS].to_numpy(), base_uf[2][UFS].to_numpy()
    while restante > 0:
        n = min(lote, restante)
        restante -= n
        z1 = sortear_posterior(ajuste["z1"], n, rng)
        z2 = sortear_posterior(ajuste["z2"], n, rng)
        zq = sortear_posterior(ajuste["zq"], n, rng)
        d1, d2, dq = sortear_erros(pool, n, rng, variante)
        z1, z2, zq = z1 + d1, z2 + d2, zq + dq
        demais = expit(z2)                       # O/(O+T) = expit(log(O/T))
        p2 = expit(z1)
        pt = (1 - demais) * p2
        opp = (1 - demais) * (1 - p2)
        # composição dos menores (posterior) dentro de 'demais'
        if menores:
            # composição de 'demais' entre os menores (posterior de log(c/adv.))
            # e um resíduo não listado = demais_ref - soma dos menores_ref.
            zc = np.column_stack([sortear_posterior(ajuste["m_" + c], n, rng) for c in menores])
            frac = np.column_stack([composicao_ref(ajuste, menores)[0] * np.exp(zc),
                                    np.full(n, composicao_ref(ajuste, menores)[1])])
            frac = frac / frac.sum(axis=1, keepdims=True)
            men = frac[:, :-1] * demais[:, None]
            max_men = men.max(axis=1)
            for i, c in enumerate(menores):
                amostras[c + "_1t"].append(100 * men[:, i])
        else:
            max_men = demais * 0.6   # sem composição: maior menor ~ 60% do resto
        decide_pt = pt > 0.5
        decide_opp = opp > 0.5
        decide = decide_pt | decide_opp
        top2 = (np.minimum(pt, opp) > max_men)
        q = expit(zq)
        segundo_ok = ~decide & top2
        pt_v = decide_pt | (segundo_ok & (q > 0.5))
        opp_v = decide_opp | (segundo_ok & (q <= 0.5))
        outro = ~decide & ~top2
        # caso raríssimo: 2º turno sem um dos dois -> vence o líder do 1º turno
        lider_pt = pt >= np.maximum(opp, max_men)
        lider_opp = opp > np.maximum(pt, max_men)
        pt_v = pt_v | (outro & lider_pt)
        opp_v = opp_v | (outro & lider_opp)
        cont["pt_vence"] += int(pt_v.sum())
        cont["opp_vence"] += int(opp_v.sum())
        cont["outro_vence"] += int((~pt_v & ~opp_v).sum())
        cont["decide_1t"] += int(decide.sum())
        cont["pt_vence_1t"] += int(decide_pt.sum())
        cont["opp_vence_1t"] += int(decide_opp.sum())
        cont["top2_pt_opp"] += int(top2.sum())
        cont["ha_2t_pt_opp"] += int(segundo_ok.sum())
        cont["pt_lidera_1t"] += int(lider_pt.sum())
        # UFs: swing uniforme (p.p. da fatia bipartidária) + desvio histórico
        sw2 = 100 * q - b2n
        sw1 = 100 * p2 - b1n
        uq = b2[None, :] + sw2[:, None] + sortear_desvios_uf(V2, n, rng, variante)
        u1 = b1[None, :] + sw1[:, None] + sortear_desvios_uf(V1, n, rng, variante)
        uq = np.clip(uq, 0.5, 99.5)
        uf_pt2 += (uq > 50).sum(axis=0)
        uf_pt1 += (u1 > 50).sum(axis=0)
        amostras["pt_1t"].append(100 * pt)
        amostras["opp_1t"].append(100 * opp)
        amostras["demais_1t"].append(100 * demais)
        amostras["q_2t"].append(100 * q)
        amostras["uf_q"].append(uq[: min(n, 20000)].astype(np.float32))
    N = float(n_sims)
    a, b = nomes
    prob = {
        f"{a}_vence": cont["pt_vence"] / N, f"{b}_vence": cont["opp_vence"] / N,
        "outro_vence": cont["outro_vence"] / N,
        "decide_1t": cont["decide_1t"] / N, f"{a}_vence_1t": cont["pt_vence_1t"] / N,
        f"{b}_vence_1t": cont["opp_vence_1t"] / N,
        f"top2_{a}_{b}": cont["top2_pt_opp"] / N,                  # os dois são o top-2 do 1º turno
        f"ha_segundo_turno_{a}_x_{b}": cont["ha_2t_pt_opp"] / N,      # top-2 e ninguém decide no 1º turno
        f"{a}_1o_no_1t": cont["pt_lidera_1t"] / N,
    }
    ep = {k: math.sqrt(max(v * (1 - v), 0) / N) for k, v in prob.items()}
    amost = {k: np.concatenate(v) for k, v in amostras.items()}
    rot = {"pt_1t": f"{a}_1t", "opp_1t": f"{b}_1t", "demais_1t": "demais_1t", "q_2t": f"{a}_2t"}
    quant = {}
    for k, v in amost.items():
        if k == "uf_q":
            continue
        quant[rot.get(k, k)] = {f"p{int(qq*100)}": float(np.quantile(v, qq)) for qq in QUANTIS}
        quant[rot.get(k, k)]["media"] = float(np.mean(v))
    ufq = amost["uf_q"]
    ufs = {}
    for i, uf in enumerate(UFS):
        ufs[uf] = {f"p_{a}_vence_2t": uf_pt2[i] / N, f"p_{a}_a_frente_1t": uf_pt1[i] / N,
                   f"{a}_2t_p10": float(np.quantile(ufq[:, i], 0.10)),
                   f"{a}_2t_p50": float(np.quantile(ufq[:, i], 0.50)),
                   f"{a}_2t_p90": float(np.quantile(ufq[:, i], 0.90))}
    return {"prob": prob, "ep_mc": ep, "quantis": quant, "ufs": ufs,
            "_amostras": amost}


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

def _cobertura(amostra, verdade, niveis=(0.5, 0.8, 0.95)):
    out = {}
    for nv in niveis:
        lo, hi = np.quantile(amostra, [(1 - nv) / 2, 1 - (1 - nv) / 2], axis=0)
        out[nv] = (lo <= verdade) & (verdade <= hi)
    return out


def avaliar(sim, ano, dados_uf):
    """Métricas de um ano de backtest: cobertura (nacional e UF) e Brier."""
    res = resultado_nacional(ano)
    am = sim["_amostras"]
    nac = {"pt_1t": res["pt_1t"], "opp_1t": res["opp_1t"],
           "demais_1t": res["demais_1t"], "q_2t": res["q_2t"]}
    cob_nac = {k: {str(nv): bool(v) for nv, v in _cobertura(am[k], val).items()}
               for k, val in nac.items()}
    erro_mediana = {k: float(np.median(am[k]) - val) for k, val in nac.items()}
    real_uf2 = dados_uf[(ano, 2)][UFS].to_numpy()
    real_uf1 = dados_uf[(ano, 1)][UFS].to_numpy()
    cob_uf = {str(nv): float(v.mean()) for nv, v in _cobertura(am["uf_q"], real_uf2).items()}
    p = sim["prob"]
    eventos = {
        "pt_vence": (p["pt_vence"], res["q_2t"] > 50),
        "decide_1t": (p["decide_1t"], max(res["pt_1t"], res["opp_1t"]) > 50),
        "pt_1o_no_1t": (p["pt_1o_no_1t"], res["pt_1t"] > res["opp_1t"]),
        "top2_pt_opp": (p["top2_pt_opp"],
                                    min(res["pt_1t"], res["opp_1t"]) > res["terceiro_1t"]),
    }
    brier_nac = {k: (pp - float(o)) ** 2 for k, (pp, o) in eventos.items()}
    p2uf = np.array([sim["ufs"][u]["p_pt_vence_2t"] for u in UFS])
    p1uf = np.array([sim["ufs"][u]["p_pt_a_frente_1t"] for u in UFS])
    o2, o1 = (real_uf2 > 50).astype(float), (real_uf1 > 50).astype(float)
    return {
        "ano": ano,
        "previsao": {k: v for k, v in p.items()},
        "resultado": res,
        "erro_mediana_pp": erro_mediana,
        "cobertura_nacional": cob_nac,
        "cobertura_uf_2t": cob_uf,
        "brier_nacional": brier_nac,
        "brier_uf_2t": float(np.mean((p2uf - o2) ** 2)),
        "brier_uf_1t": float(np.mean((p1uf - o1) ** 2)),
        "acertos_uf_2t": int(((p2uf > 0.5) == (o2 > 0.5)).sum()),
        "acertos_uf_1t": int(((p1uf > 0.5) == (o1 > 0.5)).sum()),
        "_det_uf": {"p2": p2uf, "o2": o2, "p1": p1uf, "o1": o1},
    }


def resumir_backtest(bt):
    """Agrega 2018+2022 por variante: cobertura média e Brier."""
    out = {}
    variantes = next(iter(bt.values())).keys()
    for var in variantes:
        cob_nac = {nv: [] for nv in ("0.5", "0.8", "0.95")}
        cob_uf = {nv: [] for nv in ("0.5", "0.8", "0.95")}
        brier_nac, brier_sub, p2s, o2s, p1s, o1s = [], [], [], [], [], []
        for ano, d in bt.items():
            r = d[var]
            for q in r["cobertura_nacional"].values():
                for nv in cob_nac:
                    cob_nac[nv].append(q[nv])
            for nv in cob_uf:
                cob_uf[nv].append(r["cobertura_uf_2t"][nv])
            brier_nac += list(r["brier_nacional"].values())
            brier_sub += [r["brier_nacional"]["pt_vence"], r["brier_nacional"]["pt_1o_no_1t"]]
            p2s.append(r["_det_uf"]["p2"]); o2s.append(r["_det_uf"]["o2"])
            p1s.append(r["_det_uf"]["p1"]); o1s.append(r["_det_uf"]["o1"])
        p2, o2 = np.concatenate(p2s), np.concatenate(o2s)
        p1, o1 = np.concatenate(p1s), np.concatenate(o1s)
        eps = 1e-6
        out[var] = {
            "cobertura_nacional": {nv: float(np.mean(v)) for nv, v in cob_nac.items()},
            "n_quantidades_nacionais": len(cob_nac["0.5"]),
            "cobertura_uf_2t": {nv: float(np.mean(v)) for nv, v in cob_uf.items()},
            "n_uf": int(len(p2)),
            "brier_nacional_medio": float(np.mean(brier_nac)),
            "n_eventos_nacionais": len(brier_nac),
            # mesmos eventos do BACKTEST.md do simulador principal: PT vence; PT 1º no 1º turno
            "brier_nacional_pt_vence_e_pt_1o": float(np.mean(brier_sub)),
            "brier_uf_1t_e_2t": float(np.mean(np.r_[(p2 - o2) ** 2, (p1 - o1) ** 2])),
            "brier_uf_2t": float(np.mean((p2 - o2) ** 2)),
            "brier_uf_1t": float(np.mean((p1 - o1) ** 2)),
            "logloss_uf_2t": float(-np.mean(o2 * np.log(np.clip(p2, eps, 1)) +
                                            (1 - o2) * np.log(np.clip(1 - p2, eps, 1)))),
            "acerto_uf_2t": float(np.mean((p2 > 0.5) == (o2 > 0.5))),
            "referencia_brier_moeda": 0.25,
        }
    return out
