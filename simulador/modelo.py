"""Modelo Monte Carlo por UF da eleição presidencial brasileira (motor genérico).

O mesmo motor roda 2026 (``eleicao_2026``) e as eleições de 2014, 2018 e 2022
no backtest (``backtest.py``), sempre "na véspera" e só com as pesquisas
disponíveis naquela data. Detalhes, fontes e números em README.md,
BACKTEST.md e premissas.json.

Estrutura
---------
1. **Agregação nacional.** Cada pesquisa é decomposta em
     - p2 = PT / (PT + principal adversário) no 1º turno (indecisos alocados
       pela rejeição/2ª preferência ou proporcionalmente);
     - m_k = votos válidos de cada candidato menor ("terceira via");
     - q  = fatia do PT no 2º turno PT x adversário.
   Efeitos de instituto (house effects) por modelo hierárquico (efeitos
   aleatórios com variância estimada por máxima verossimilhança), média
   ponderada por recência e sqrt(n), uma pesquisa por instituto.
2. **UFs.** Prior (nacional + lean anterior em logito; em 2026, prior
   demográfico misto de segmentos.py) combinado com pesquisas estaduais;
   médias deslocadas para que o agregado reproduza o nacional.
3. **Erro estruturado** (por simulação):
     a) erro na margem PT x adversário (logito de p2), t de Student;
     b) erro na fatia combinada da terceira via (log), com média negativa
        (contração/voto útil) estimada dos erros de 2014/2018/2022;
     c) resíduo pequeno por candidato menor (nacional e por UF);
     d) viés da indústria (beta) com prior empírico-bayesiano dos erros
        históricos, encolhido para zero, ponderado pela exposição de cada
        instituto (lambda) — só nas visões "calibrado" e "pleno";
     e) fatores subnacionais: eixo NE/N x S/CO, região, UF (t);
     f) 2º turno: erro próprio correlacionado com o do 1º turno + via de
        transferência a partir do 1º turno simulado; teto suave pela rejeição.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"

CANDS = ["Lula", "Flavio", "Caiado", "Cury", "Zema", "Renan", "Outros"]
MENORES = ["Caiado", "Cury", "Zema", "Renan", "Outros"]
COL = {"Lula": "lula", "Flavio": "flavio", "Caiado": "caiado", "Cury": "cury",
       "Zema": "zema", "Renan": "renan", "Outros": "outros"}
REGIOES = ["N", "NE", "CO", "SE", "S"]
VISOES = ("neutro", "calibrado", "pleno")


# ---------------------------------------------------------------- utilidades
def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def pp_para_logito(pp, p):
    """Converte p.p. de uma fatia p (0-1) para logito (derivada local)."""
    return pp / (100.0 * p * (1 - p))


def carregar_premissas(caminho: Path | str = AQUI / "premissas.json") -> dict:
    """Lê premissas.json e devolve um dicionário plano {secao.param: valor}."""
    bruto = json.loads(Path(caminho).read_text(encoding="utf-8"))
    plano = {"_bruto": bruto}

    def walk(d, prefixo=""):
        for k, v in d.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict) and "valor" in v:
                plano[prefixo + k] = v["valor"]
            elif isinstance(v, dict):
                walk(v, prefixo + k + ".")
    walk(bruto)
    return plano


def t_unit(rng, shape, df):
    """t de Student com variância 1 (df > 2)."""
    z = rng.standard_normal(shape, dtype=np.float32)
    g = rng.chisquare(df, size=shape).astype(np.float32) / df
    return z / np.sqrt(g) * np.float32(math.sqrt((df - 2) / df))


def eb_vies(erros, sigma_eta, tau0):
    """Prior empírico-bayesiano do viés da indústria.

    erros: erros históricos (pesquisa − resultado) na mesma unidade de sigma_eta.
    Modelo: erro_ano = B + eta_ano, eta ~ N(0, sigma_eta²), B ~ N(0, tau0²).
    Devolve (média, dp) da posterior de B. tau0 = inf -> sem encolhimento
    (média simples, dp = sigma/sqrt(n)); tau0 = 0 -> B = 0.
    """
    x = np.asarray([e for e in erros if e is not None and np.isfinite(e)], float)
    n = len(x)
    if n == 0 or tau0 == 0:
        return 0.0, 0.0
    if not np.isfinite(tau0):
        return float(x.mean()), float(sigma_eta / math.sqrt(n))
    prec = 1 / tau0 ** 2 + n / sigma_eta ** 2
    return float(x.sum() / sigma_eta ** 2 / prec), float(math.sqrt(1 / prec))


# ---------------------------------------------------------------- especificação genérica
@dataclass
class Eleicao:
    """Tudo o que o motor precisa saber de uma eleição, na data de referência.

    nac: pesquisas nacionais padronizadas (uma linha por pesquisa), colunas
         instituto, campo_fim, n, registro, c0..c{K-1} (votos totais, ou
         válidos se base == 'validos'), bni, ind, base, t2a, t2b, peso_extra.
    puf: pesquisas estaduais padronizadas: uf, instituto, campo_fim, n,
         c0..c{K-1} (pode faltar), t2a, t2b.
    ufs: uf, nome, regiao, eleitores, abst1, bn1, abst2, bn2,
         prior1 / prior2 (lean em logito), sdprior1 / sdprior2 (p.p.).
    transf: (M, 3) linhas [PT, adversário, branco/nulo/abstenção] do 2º turno
         por candidato menor (média do Dirichlet).
    """
    ano: int
    cands: list
    ref: pd.Timestamp
    nac: pd.DataFrame
    puf: pd.DataFrame
    ufs: pd.DataFrame
    transf: np.ndarray
    inicio_house: pd.Timestamp
    rejeicao: dict | None = None            # {'pt': %, 'opp': %} métrica "não votaria de jeito nenhum"
    pi_indecisos: float | None = None       # fração dos indecisos (entre os 2) que vai ao PT, se medida
    exposicao: dict = field(default_factory=dict)   # instituto -> (lambda, dp)
    ajuste_comp: dict | None = None         # {'a1','a2': arrays (U,) logito; 'dp1','dp2': p.p.}
    primeiro_turno_fixo: np.ndarray | None = None   # (U, K) válidos reais do 1º turno (backtest do 2º turno na véspera do 2º)
    horizonte_2t: str = "vespera_1t"        # 'vespera_1t' ou 'vespera_2t'
    notas: list = field(default_factory=list)

    @property
    def K(self):
        return len(self.cands)

    @property
    def M(self):
        return len(self.cands) - 2


# ---------------------------------------------------------------- pesquisas: limpeza e indecisos
def deduplicar(df: pd.DataFrame, cols_valor: list) -> tuple[pd.DataFrame, list]:
    """Remove pesquisas repetidas: mesmo registro TSE ou mesmo instituto+data+números."""
    log = []
    d = df.copy()
    d["_ordem"] = np.arange(len(d))
    chave = pd.Series(["|".join(str(v) for v in row) for row in
                       d[["instituto", "campo_fim"] + cols_valor].itertuples(index=False)], index=d.index)
    dup = chave.duplicated(keep="last")
    for r in d[dup].itertuples():
        log.append(f"duplicata removida: {r.instituto} {pd.Timestamp(r.campo_fim).date()} (mesmos números)")
    d = d[~dup]
    if "registro" in d:
        reg = d["registro"].astype(str).str.extract(r"([A-Z]{2}-\d{5}/\d{4})")[0]
        tem = reg.notna()
        dup2 = tem & reg.duplicated(keep="last")
        for r in d[dup2].itertuples():
            log.append(f"duplicata removida: {r.instituto} {pd.Timestamp(r.campo_fim).date()} (registro repetido)")
        d = d[~dup2]
    return d.sort_values("_ordem").drop(columns="_ordem"), log


def pi_rejeicao(s_pt, s_opp, rej):
    """Fração dos indecisos (que escolhem entre os 2 primeiros) que vai ao PT,
    proporcional ao 'espaço' de cada um: 100 − rejeição − intenção atual."""
    room_pt = np.maximum(100 - rej["pt"] - s_pt, 1.0)
    room_op = np.maximum(100 - rej["opp"] - s_opp, 1.0)
    return room_pt / (room_pt + room_op)


def preparar_pesquisas(e: Eleicao, prem: dict, metodo_indecisos: str | None = None) -> pd.DataFrame:
    """Calcula p2, q, válidos dos menores e T (terceira via) de cada pesquisa nacional."""
    metodo = metodo_indecisos or prem["indecisos.metodo"]
    d = e.nac.copy()
    K = e.K
    cs = [f"c{k}" for k in range(K)]
    named = d[cs].sum(axis=1, skipna=True)
    completo = d[cs[2:]].notna().all(axis=1) & d["bni"].notna()
    validos = d["base"].eq("validos") | ((d["bni"].fillna(-1) == 0) & (named >= 98))
    d["base_validos"] = validos
    # indecisos (fração de bni que é indeciso) -> alocados; brancos/nulos -> excluídos
    f1 = prem["indecisos.fracao_bni_1t"]
    u = d["ind"].where(d["ind"].notna(), f1 * d["bni"].fillna(0))
    u = u.where(~validos, 0.0)
    s_pt, s_op = d["c0"], d["c1"]
    top = s_pt + s_op
    u_top = u * top / named.where(named > 0)          # parte dos indecisos que fica com os 2 primeiros
    if metodo == "rejeicao" and (e.rejeicao is not None or e.pi_indecisos is not None):
        pi = (np.full(len(d), e.pi_indecisos) if e.pi_indecisos is not None
              else pi_rejeicao(s_pt.values, s_op.values, e.rejeicao))
    else:
        pi = (s_pt / top).values
    d["p2_prop"] = s_pt / top
    d["p2"] = (s_pt + u_top * pi) / (top + u_top)
    d["indecisos_alocados"] = u
    # menores em válidos (só pesquisas com a lista completa)
    for k in range(2, K):
        d[f"m{k}"] = np.where(completo, d[f"c{k}"] / named.where(named > 0), np.nan)
    d["T"] = np.where(completo, d[[f"m{k}" for k in range(2, K)]].sum(axis=1), np.nan)
    # 2º turno
    f2 = prem["indecisos.fracao_resto_2t"]
    resto2 = (100 - d["t2a"] - d["t2b"]).clip(lower=0)
    u2 = d["t2ind"].where(d["t2ind"].notna(), f2 * resto2) if "t2ind" in d else f2 * resto2
    top2 = d["t2a"] + d["t2b"]
    if metodo == "rejeicao" and e.rejeicao is not None:
        pi2 = pi_rejeicao(d["t2a"].values, d["t2b"].values, e.rejeicao)
    else:
        pi2 = (d["t2a"] / top2).values
    d["q_prop"] = d["t2a"] / top2
    d["q"] = (d["t2a"] + u2 * pi2) / (top2 + u2)
    return d


# ---------------------------------------------------------------- house effects hierárquicos
def house_effects_hier(d: pd.DataFrame, coluna: str, inicio, ref, grade_tau=None, grade_se=None) -> dict:
    """Efeitos de instituto como efeitos aleatórios (partial pooling).

    y_i = mu_semana + h_inst + e_i,   h ~ N(0, tau²),  e_i ~ N(0, s_e² + amostral_i)
    tau e s_e por máxima verossimilhança (perfilada) numa grade; h = média
    posterior (BLUP), com dp posterior. Institutos com poucas pesquisas ficam
    perto de zero automaticamente.
    """
    x = d[(d.campo_fim >= inicio) & (d.campo_fim <= ref) & d[coluna].notna()].copy()
    if len(x) < 3:
        return {"_tau_pp": None, "_se_pp": None}
    p = x[coluna].values
    y = logit(p)
    n = x["n"].fillna(2000).clip(upper=5000).values
    samp = 1.0 / (n * p * (1 - p))                       # variância amostral em logito
    sem = ((x.campo_fim - inicio).dt.days // 7).values
    semanas = sorted(set(sem))
    insts = sorted(x["instituto"].unique())
    X = np.zeros((len(x), len(semanas)))
    Z = np.zeros((len(x), len(insts)))
    for i, (s, ins) in enumerate(zip(sem, x["instituto"])):
        X[i, semanas.index(s)] = 1
        Z[i, insts.index(ins)] = 1
    escala = 100 * np.mean(p) * (1 - np.mean(p))          # logito -> p.p.
    grade_tau = grade_tau or [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
    grade_se = grade_se or [0.5, 0.75, 1.0, 1.5, 2.0, 2.5]
    melhor = None
    for tpp in grade_tau:
        for spp in grade_se:
            t2, s2 = (tpp / escala) ** 2, (spp / escala) ** 2
            V = np.diag(s2 + samp) + t2 * Z @ Z.T
            Vi = np.linalg.inv(V)
            A = X.T @ Vi @ X
            mu = np.linalg.solve(A, X.T @ Vi @ y)
            r = y - X @ mu
            _, logdet = np.linalg.slogdet(V)
            _, logdetA = np.linalg.slogdet(A)
            ll = -0.5 * (logdet + logdetA + r @ Vi @ r)    # REML
            if melhor is None or ll > melhor[0]:
                melhor = (ll, tpp, spp, t2, s2, Vi, r)
    _, tpp, spp, t2, s2, Vi, r = melhor
    h = t2 * Z.T @ Vi @ r
    cov = t2 * np.eye(len(insts)) - t2 ** 2 * Z.T @ Vi @ Z
    cont = x.groupby("instituto").size()
    out = {ins: {"h_logito": float(h[j]), "h_pp": float(h[j] * escala),
                 "dp_pp": float(math.sqrt(max(cov[j, j], 0)) * escala), "n_pesquisas": int(cont[ins])}
           for j, ins in enumerate(insts)}
    out["_tau_pp"] = tpp
    out["_se_pp"] = spp
    return out


def _selecionar_recentes(d, coluna, ref, prem):
    jan = prem["agregacao.janela_dias"]
    x = d[d[coluna].notna() & (d.campo_fim <= ref) & (d.campo_fim > ref - pd.Timedelta(days=jan))].copy()
    x = x.sort_values("campo_fim").groupby("instituto").tail(1)
    dias = (ref - x.campo_fim).dt.days.clip(lower=0)
    n = x["n"].fillna(2000).clip(upper=prem["agregacao.n_teto"])
    x["peso"] = np.sqrt(n) * np.exp(-dias / prem["agregacao.tau_recencia_dias"]) * x["peso_extra"].fillna(1.0)
    x["dias"] = dias
    return x


def agregar(d, coluna, house, ref, prem, exposicao=None):
    """Média ponderada (logito) das últimas pesquisas de cada instituto, corrigidas pelo house effect.

    Devolve dict com media, media_bruta, dp_consenso_pp, lambda_medio, dp_lambda, tabela."""
    x = _selecionar_recentes(d, coluna, ref, prem)
    if x.empty:
        return None
    h = x["instituto"].map(lambda i: house.get(i, {}).get("h_logito", 0.0)).values
    hsd = x["instituto"].map(lambda i: house.get(i, {}).get("dp_pp", house.get("_tau_pp") or 1.5)).values
    y = logit(x[coluna].values) - h
    w = x["peso"].values / x["peso"].sum()
    media = float(expit(np.sum(w * y)))
    bruta = float(expit(np.sum(w * logit(x[coluna].values))))
    se = house.get("_se_pp") or 1.2
    dp_cons = float(math.sqrt(np.sum(w ** 2 * (hsd ** 2 + se ** 2))))
    exposicao = exposicao or {}
    padrao = exposicao.get("_padrao", (1.0, 0.0))
    lam = np.array([exposicao.get(i, padrao)[0] for i in x["instituto"]])
    lsd = np.array([exposicao.get(i, padrao)[1] for i in x["instituto"]])
    tabela = [{"instituto": r.instituto, "campo_fim": r.campo_fim.strftime("%Y-%m-%d"),
               "n": None if pd.isna(r.n) else int(r.n), "valor": round(float(getattr(r, coluna)) * 100, 2),
               "house_pp": round(house.get(r.instituto, {}).get("h_pp", 0.0), 2),
               "house_dp_pp": round(house.get(r.instituto, {}).get("dp_pp", 0.0), 2),
               "exposicao_vies": round(float(exposicao.get(r.instituto, padrao)[0]), 2),
               "peso_extra": float(r.peso_extra) if not pd.isna(r.peso_extra) else 1.0,
               "peso_rel": round(float(r.peso / x["peso"].sum()), 3)}
              for r in x.itertuples()]
    return {"media": media, "media_bruta": bruta, "dp_consenso_pp": dp_cons,
            "lambda_medio": float(np.sum(w * lam)), "dp_lambda": float(math.sqrt(np.sum((w * lsd) ** 2))),
            "tabela": tabela}


def menores_nacionais(d, e: Eleicao, ref, prem):
    """Votos válidos médios de cada candidato menor (pesquisas recentes com a lista completa)."""
    out = []
    for k in range(2, e.K):
        x = _selecionar_recentes(d, f"m{k}", ref, prem)
        if x.empty:
            out.append(np.nan)
            continue
        out.append(float(np.sum(x["peso"] * x[f"m{k}"]) / np.sum(x["peso"])))
    return np.array(out)


# ---------------------------------------------------------------- base (médias nacionais e por UF)
def combinar(prior, sd_prior, obs, sd_obs):
    prec = 1 / sd_prior ** 2 + np.sum(1 / np.asarray(sd_obs, float) ** 2)
    media = (prior / sd_prior ** 2 + np.sum(np.asarray(obs, float) / np.asarray(sd_obs, float) ** 2)) / prec
    return media, math.sqrt(1 / prec)


def _resolver_desloc(p, w, alvo):
    lo, hi = -3.0, 3.0
    for _ in range(80):
        mid = (lo + hi) / 2
        v = np.sum(w * expit(logit(p) + mid)) / np.sum(w)
        if v < alvo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


@dataclass
class Base:
    e: Eleicao
    prem: dict
    ufs: pd.DataFrame
    p2_nat: float
    q_nat: float
    m_nat: np.ndarray
    p2_uf: np.ndarray
    q_uf: np.ndarray
    m_uf: np.ndarray
    sd_p2_uf: np.ndarray
    sd_q_uf: np.ndarray
    agg1: dict
    agg2: dict | None
    house1: dict
    house2: dict
    detalhe_uf: list = field(default_factory=list)
    desloc: dict = field(default_factory=dict)
    pesquisas: pd.DataFrame | None = None


def construir_base(e: Eleicao, prem: dict, metodo_indecisos: str | None = None) -> Base:
    d = preparar_pesquisas(e, prem, metodo_indecisos)
    ref = e.ref
    house1 = house_effects_hier(d, "p2", e.inicio_house, ref)
    house2 = house_effects_hier(d, "q", e.inicio_house, ref)
    agg1 = agregar(d, "p2", house1, ref, prem, e.exposicao)
    agg2 = agregar(d, "q", house2, ref, prem, e.exposicao)
    m_nat = menores_nacionais(d, e, ref, prem)
    if agg1 is None and e.primeiro_turno_fixo is not None:
        # véspera do 2º turno (backtest): o 1º turno é o resultado oficial
        u = e.ufs
        w = (u.eleitores * (1 - u.abst1 / 100) * (1 - u.bn1 / 100)).values
        sh = (w[:, None] * e.primeiro_turno_fixo).sum(0) / w.sum()
        agg1 = {"media": float(sh[0] / (sh[0] + sh[1])), "media_bruta": float(sh[0] / (sh[0] + sh[1])),
                "dp_consenso_pp": 0.0, "lambda_medio": 1.0, "dp_lambda": 0.0, "tabela": []}
        m_nat = np.maximum(sh[2:], 1e-4)
    p2_nat = agg1["media"]
    q_nat = agg2["media"] if agg2 else np.nan

    ufs = e.ufs.reset_index(drop=True)
    U, M = len(ufs), e.M
    deff = prem["estados.efeito_desenho"]
    piso1 = prem["estados.dp_pesquisa_piso_1t_pp"] / 100
    piso2 = prem["estados.dp_pesquisa_piso_2t_pp"] / 100
    tau = prem["estados.tau_recencia_uf_dias"]
    sdpm = prem["estados.dp_prior_menores_pp"] / 100
    pisom = prem["estados.dp_pesquisa_menores_piso_pp"] / 100
    puf = e.puf
    p2_uf = np.zeros(U); q_uf = np.zeros(U); sd1 = np.zeros(U); sd2 = np.zeros(U)
    m_uf = np.zeros((U, M))
    detalhe = []
    q_ref = q_nat if np.isfinite(q_nat) else p2_nat
    for i, r in ufs.iterrows():
        pr1 = float(expit(logit(p2_nat) + r.prior1))
        pr2 = float(expit(logit(q_ref) + r.prior2))
        sdp1 = r.sdprior1 / 100
        sdp2 = r.sdprior2 / 100
        pol = puf[(puf.uf == r.uf) & (puf.campo_fim <= ref)] if len(puf) else puf
        o1, s1, o2, s2 = [], [], [], []
        for p in pol.itertuples():
            dias = max((ref - p.campo_fim).days, 0)
            infl = 1 + dias / tau
            nn = p.n if not pd.isna(p.n) else prem["estados.n_padrao_sem_amostra"]
            if not pd.isna(p.c0) and not pd.isna(p.c1) and (p.c0 + p.c1) > 0:
                v = p.c0 / (p.c0 + p.c1)
                n_top = nn * (p.c0 + p.c1) / 100
                o1.append(v); s1.append(math.sqrt((deff * v * (1 - v) / n_top + piso1 ** 2) * infl))
            if not pd.isna(p.t2a) and not pd.isna(p.t2b) and (p.t2a + p.t2b) > 0:
                v = p.t2a / (p.t2a + p.t2b)
                n_top = nn * (p.t2a + p.t2b) / 100
                o2.append(v); s2.append(math.sqrt((deff * v * (1 - v) / n_top + piso2 ** 2) * infl))
        p2_uf[i], sd1[i] = combinar(pr1, sdp1, o1, s1)
        q_uf[i], sd2[i] = combinar(pr2, sdp2, o2, s2)
        for k in range(M):
            obs, sds = [], []
            for p in pol.itertuples():
                x = getattr(p, f"c{k + 2}", np.nan)
                cs = [getattr(p, f"c{j}", np.nan) for j in range(e.K)]
                if pd.isna(x) or any(pd.isna(c) for c in cs):
                    continue
                tot = float(np.nansum(cs))
                if tot <= 0:
                    continue
                v = x / tot
                nn = p.n if not pd.isna(p.n) else prem["estados.n_padrao_sem_amostra"]
                var = deff * max(v, 0.005) * (1 - v) / nn + pisom ** 2
                obs.append(v); sds.append(math.sqrt(var * (1 + max((ref - p.campo_fim).days, 0) / tau)))
            m_uf[i, k], _ = combinar(m_nat[k], sdpm, obs, sds)
        m_uf[i] = np.clip(m_uf[i], 0.001, None)
        detalhe.append({"uf": r.uf, "prior_p2": pr1, "prior_q": pr2, "dp_prior_p2_pp": r.sdprior1,
                        "dp_prior_q_pp": r.sdprior2, "pesquisas_1t": len(o1), "pesquisas_2t": len(o2)})

    # ---- calibração: agregado ponderado das UFs = média nacional
    w1 = (ufs.eleitores * (1 - ufs.abst1 / 100) * (1 - ufs.bn1 / 100)).values
    w2 = (ufs.eleitores * (1 - ufs.abst2 / 100) * (1 - ufs.bn2 / 100)).values
    for _ in range(50):
        agg_m = (w1[:, None] * m_uf).sum(0) / w1.sum()
        m_uf = m_uf * (m_nat / agg_m)[None, :]
    m_uf = np.clip(m_uf, 0.0005, None)
    T = 1 - m_uf.sum(1)
    d1 = _resolver_desloc(p2_uf, w1 * T, p2_nat)
    p2_cal = expit(logit(p2_uf) + d1)
    d2 = _resolver_desloc(q_uf, w2, q_ref)
    q_cal = expit(logit(q_uf) + d2)
    for i, dd in enumerate(detalhe):
        dd.update({"p2_pesquisas_prior": float(p2_uf[i]), "q_pesquisas_prior": float(q_uf[i]),
                   "p2_calibrado": float(p2_cal[i]), "q_calibrado": float(q_cal[i]),
                   "dp_p2_pp": float(sd1[i] * 100), "dp_q_pp": float(sd2[i] * 100)})
    b = Base(e, prem, ufs, p2_nat, q_ref, m_nat, p2_cal, q_cal, m_uf, sd1 * 100, sd2 * 100,
             agg1, agg2, house1, house2, detalhe, pesquisas=d)
    b.desloc = {"p2_logito": float(d1), "q_logito": float(d2),
                "p2_pp_aprox": float(d1 * 100 * p2_nat * (1 - p2_nat)),
                "q_pp_aprox": float(d2 * 100 * q_ref * (1 - q_ref))}
    return b


# ---------------------------------------------------------------- simulação
def _beta_params(m, s):
    k = m * (1 - m) / s ** 2 - 1
    return m * k, (1 - m) * k


def simular_lote(base: Base, vies: dict, B: int, rng: np.random.Generator, P: dict | None = None) -> dict:
    """Simula B eleições.

    vies: {'b1': (média, dp) p.p. de p2, 'b2': (média, dp) p.p. de q, 'muT': (média, dp) log,
           'lambda1'/'lambda2': (média, dp) exposição, 'ajuste_comp': bool}
    Devolve arrays nacionais (B, ...) e por UF (B, U).
    """
    P = P or base.prem
    e = base.e
    ufs = base.ufs
    U, K, M = len(ufs), e.K, e.M
    f32 = np.float32
    reg_idx = np.array([REGIOES.index(r) if r in REGIOES else -1 for r in ufs.regiao])
    cargas = P["estados.cargas_eixo"]
    load = np.array([cargas.get(r, 0.0) for r in ufs.regiao], dtype=f32)
    w_ele = ufs.eleitores.values.astype(f32)
    load = load - np.sum(w_ele * load) / np.sum(w_ele)
    df_n = P["erro_nacional_1t.gl_t"]
    df_uf = P["estados.gl_t_uf"]
    sd_ax = P["estados.dp_eixo_pp"]
    sd_rg = P["estados.dp_regional_pp"]
    sd_min = P["estados.dp_uf_minimo_pp"]

    def sub_erros(p_uf, sd_post, ww):
        """Eixo + regional + UF (logito), centrados para não mexer no agregado nacional."""
        conv = 1 / (100 * p_uf * (1 - p_uf))
        ax = rng.standard_normal(B, dtype=f32)[:, None] * f32(sd_ax) * load[None, :]
        rgd = rng.standard_normal((B, len(REGIOES)), dtype=f32) * f32(sd_rg)
        rg = np.where(reg_idx[None, :] >= 0, rgd[:, np.clip(reg_idx, 0, None)], 0).astype(f32)
        sd_id = np.maximum(sd_post, sd_min)
        s = (ax + rg + t_unit(rng, (B, U), df_uf) * sd_id[None, :].astype(f32)) * conv[None, :].astype(f32)
        wc = ww * p_uf * (1 - p_uf)
        return s - (s @ (wc / wc.sum()).astype(f32))[:, None]

    # ---------- viés da indústria (correlacionado entre turnos)
    rho_b = P["vies.rho_1t_2t"]
    zb1 = rng.standard_normal(B)
    zb2 = rho_b * zb1 + math.sqrt(1 - rho_b ** 2) * rng.standard_normal(B)
    mu1, sd1b = vies.get("b1", (0.0, 0.0)); mu2, sd2b = vies.get("b2", (0.0, 0.0))
    lm1, ls1 = vies.get("lambda1", (1.0, 0.0)); lm2, ls2 = vies.get("lambda2", (1.0, 0.0))
    lam1 = np.clip(lm1 + ls1 * rng.standard_normal(B), 0, 1.2)
    lam2 = np.clip(lm2 + ls2 * rng.standard_normal(B), 0, 1.2)
    b1 = ((mu1 + sd1b * zb1) * lam1).astype(f32)          # p.p. de p2, positivo = pesquisas pró-PT
    b2 = ((mu2 + sd2b * zb2) * lam2).astype(f32)          # p.p. de q

    ajuste = vies.get("ajuste_comp", False) and e.ajuste_comp is not None
    t1 = t_unit(rng, B, df_n)

    if e.primeiro_turno_fixo is None:
        # ---------- 1º turno
        p_c = base.p2_uf
        sd_cons1 = base.agg1["dp_consenso_pp"]
        e_pp = t1 * f32(P["erro_nacional_1t.dp_p2_pp"]) + rng.standard_normal(B).astype(f32) * f32(sd_cons1) - b1
        e_p2 = pp_para_logito(e_pp, base.p2_nat).astype(f32)
        lp = logit(p_c)[None, :].astype(f32) + e_p2[:, None]
        if ajuste:
            a1 = e.ajuste_comp["a1"][None, :] + rng.normal(0, 1, (B, 1)) * pp_para_logito(e.ajuste_comp["dp1"], base.p2_nat)
            lp = lp + a1.astype(f32)
        sub1 = sub_erros(p_c, base.sd_p2_uf, w_ele * (1 - base.m_uf.sum(1)))
        p2 = expit(lp + sub1).astype(f32)

        # terceira via: erro combinado (log) + resíduo por candidato
        muT, sdT = vies.get("muT", (P["terceira_via.mu_log"], 0.0))
        dT = (muT + sdT * rng.standard_normal(B) + P["terceira_via.dp_log"] * t_unit(rng, B, df_n)).astype(f32)
        zk = rng.standard_normal((B, 1, M), dtype=f32) * f32(P["terceira_via.dp_log_residuo_nacional"])
        zuk = rng.standard_normal((B, U, M), dtype=f32) * f32(P["terceira_via.dp_log_residuo_uf"])
        m0 = base.m_uf[None, :, :].astype(f32)
        m1 = m0 * np.exp(dT[:, None, None] + zk + zuk)
        tot = m1.sum(2, keepdims=True)
        m1 = np.where(tot > 0.6, m1 * (0.6 / tot), m1)
        alfa = P["transferencia.alfa_dirichlet"]
        TM = np.stack([rng.dirichlet(alfa * np.asarray(e.transf[k]) + 1e-3, B) for k in range(M)], axis=1).astype(f32)
        r_l = TM[:, :, 0] / (TM[:, :, 0] + TM[:, :, 1])          # (B, M)
        top0 = 1 - m0.sum(2)
        mov = m0 - m1                                             # votos que saem (ou entram, se < 0) dos menores
        L = top0 * p2 + (mov * r_l[:, None, :]).sum(2)
        F = top0 * (1 - p2) + (mov * (1 - r_l[:, None, :])).sum(2)
        L = np.maximum(L, 0.002); F = np.maximum(F, 0.002)
        s_ = L + F + m1.sum(2)
        L, F, m1 = L / s_, F / s_, m1 / s_[:, :, None]
        shares = np.concatenate([L[:, :, None], F[:, :, None], m1], axis=2)     # (B,U,K)
    else:
        sh = np.asarray(e.primeiro_turno_fixo, dtype=f32)
        shares = np.broadcast_to(sh[None], (B, U, K)).copy()
        L, F, m1 = shares[:, :, 0], shares[:, :, 1], shares[:, :, 2:]
        TM = np.broadcast_to(np.asarray(e.transf, f32)[None], (B, M, 3)).copy()
        sub1 = np.zeros((B, U), f32)
        e_p2 = np.zeros(B, f32)

    C = P
    def valid_w(abst, bn):
        an = rng.standard_normal((B, 1), dtype=f32) * f32(C["comparecimento.dp_abst_nacional_pp"])
        au = rng.standard_normal((B, U), dtype=f32) * f32(C["comparecimento.dp_abst_uf_pp"])
        bnn = rng.standard_normal((B, 1), dtype=f32) * f32(C["comparecimento.dp_bn_nacional_pp"])
        bnu = rng.standard_normal((B, U), dtype=f32) * f32(C["comparecimento.dp_bn_uf_pp"])
        ab = np.clip(abst.astype(f32)[None, :] + an + au, 5, 75) * f32(0.01)
        bb = np.clip(bn.astype(f32)[None, :] + bnn + bnu, 0.5, 25) * f32(0.01)
        return w_ele[None, :] * (1 - ab) * (1 - bb)
    wv1 = valid_w(ufs.abst1.values, ufs.bn1.values)
    nat1 = np.einsum("bu,buk->bk", wv1, shares) / wv1.sum(1, keepdims=True)

    # ---------- 2º turno
    h2 = "vespera_2t" if e.horizonte_2t == "vespera_2t" else "vespera_1t"
    sdq = P[f"erro_2t.dp_q_pp_{h2}"]
    rho = P["erro_2t.rho_com_1t"] if e.primeiro_turno_fixo is None else 0.0
    t2 = (rho * t1 + math.sqrt(1 - rho ** 2) * t_unit(rng, B, P["erro_2t.gl_t"])).astype(f32)
    q_u = base.q_uf
    sd_cons2 = base.agg2["dp_consenso_pp"] if base.agg2 else 1.0
    eq_pp = t2 * f32(sdq) + rng.standard_normal(B).astype(f32) * f32(sd_cons2) - b2
    e_q = pp_para_logito(eq_pp, base.q_nat).astype(f32)
    ru = P["erro_2t.rho_uf_1t_2t"] if e.primeiro_turno_fixo is None else 0.0
    ind2 = sub_erros(q_u, base.sd_q_uf, w_ele)
    sub2 = f32(ru) * sub1 + f32(math.sqrt(1 - ru ** 2)) * ind2
    lq = logit(q_u)[None, :].astype(f32) + e_q[:, None] + sub2
    if ajuste:
        a2 = e.ajuste_comp["a2"][None, :] + rng.normal(0, 1, (B, 1)) * pp_para_logito(e.ajuste_comp["dp2"], base.q_nat)
        lq = lq + a2.astype(f32)
    q_poll = expit(lq).astype(f32)
    num = L + (m1 * TM[:, None, :, 0]).sum(2)
    den = L + F + (m1 * (TM[:, None, :, 0] + TM[:, None, :, 1])).sum(2)
    q_tr = (num / den).astype(f32)
    wq = P[f"erro_2t.peso_pesquisas_{h2}"]
    q = expit(wq * logit(q_poll) + (1 - wq) * logit(q_tr)).astype(f32)
    wv2 = valid_w(ufs.abst2.values, ufs.bn2.values)
    Wn = wv2.sum(1)
    # teto suave pela rejeição nacional (métrica Datafolha, em válidos): se a fatia
    # nacional passa do teto, todas as UFs são deslocadas pelo mesmo valor em logito
    teto_ativo = np.zeros(B, bool)
    if e.rejeicao is not None and P["rejeicao.teto_ativo"]:
        folga = P["rejeicao.folga_pp"] / 100
        bn2 = P["rejeicao.bn_2t_pct"] / 100
        capL = min((1 - e.rejeicao["pt"] / 100) / (1 - bn2) + folga, 0.99)
        capF = min((1 - e.rejeicao["opp"] / 100) / (1 - bn2) + folga, 0.99)
        k = P["rejeicao.suavidade_pp"] / 100

        def soft(x, cap):
            y = cap - k + k * np.tanh((x - cap + k) / k)
            return np.where(x > cap - k, y, x)
        Qr = (wv2 * q).sum(1) / Wn
        Qn = 1 - soft(1 - soft(Qr, capL), capF)
        teto_ativo = np.abs(Qn - Qr) > 1e-5
        if teto_ativo.any():
            idx = np.where(teto_ativo)[0]
            qa, wa, alvo = q[idx], wv2[idx], Qn[idx]
            for _ in range(4):                     # Newton: desloca em logito até o agregado bater no teto
                Qa = (wa * qa).sum(1) / Wn[idx]
                deriv = (wa * qa * (1 - qa)).sum(1) / Wn[idx]
                qa = expit(logit(qa) + ((alvo - Qa) / np.maximum(deriv, 1e-6))[:, None]).astype(f32)
            q = q.copy()
            q[idx] = qa
    Q = (wv2 * q).sum(1) / Wn
    Qp = (wv2 * q_poll).sum(1) / Wn
    Qt = (wv2 * q_tr).sum(1) / Wn

    # ---------- desfecho
    ordem = np.argsort(-nat1, axis=1)
    primeiro, segundo = ordem[:, 0], ordem[:, 1]
    venceu_1t = nat1.max(1) > 0.5
    par = ((primeiro == 0) & (segundo == 1)) | ((primeiro == 1) & (segundo == 0))
    vencedor = np.where(venceu_1t, primeiro, np.where(par, np.where(Q > 0.5, 0, 1), primeiro)).astype(np.int8)
    if e.primeiro_turno_fixo is not None:
        vencedor = np.where(Q > 0.5, 0, 1).astype(np.int8)
    nat_p2_agregado = nat1[:, 0] / (nat1[:, 0] + nat1[:, 1])
    return {
        "nat1": nat1.astype(f32), "Q": Q.astype(f32), "Q_pesquisas": Qp.astype(f32), "Q_transf": Qt.astype(f32),
        "primeiro": primeiro.astype(np.int8), "segundo": segundo.astype(np.int8),
        "venceu_1t": venceu_1t, "par_lf": par, "vencedor": vencedor,
        "uf_L": shares[:, :, 0], "uf_F": shares[:, :, 1], "uf_T": shares[:, :, 2:].sum(2),
        "uf_top": np.argmax(shares, 2).astype(np.int8),
        "uf_q": q, "e_p2": e_p2, "nat_p2_agregado": nat_p2_agregado.astype(f32),
        "b1": b1, "b2": b2, "teto_rejeicao": teto_ativo,
    }


# ---------------------------------------------------------------- 2026
def carregar_pesquisas_nacionais_2026() -> tuple[pd.DataFrame, list]:
    df = pd.read_csv(DADOS / "pesquisas_nacionais.csv")
    df["campo_fim"] = pd.to_datetime(df["campo_fim"])
    df["campo_inicio"] = pd.to_datetime(df["campo_inicio"])
    df, log = deduplicar(df, ["lula", "flavio", "t2_lula", "t2_flavio"])
    return df.reset_index(drop=True), log


def _ufs_2026(prem: dict) -> pd.DataFrame:
    el = pd.read_csv(DADOS / "eleitorado_uf_2026.csv")
    res = pd.read_csv(DADOS / "resultados_uf_2002_2022.csv")
    r22 = res[res.ano == 2022]
    t1 = r22[r22.turno == 1].set_index("uf")
    t2 = r22[r22.turno == 2].set_index("uf")
    el = el.set_index("uf")
    el["pt2p_1t_2022"] = t1["pt_2p_pct"] / 100
    el["pt_2t_2022"] = t2["pt_pct_validos"] / 100
    br1 = t1.loc["BR", "pt_2p_pct"] / 100
    br2 = t2.loc["BR", "pt_pct_validos"] / 100
    lean1 = logit(el["pt2p_1t_2022"].values) - logit(br1)
    lean2 = logit(el["pt_2t_2022"].values) - logit(br2)
    f = prem["estados.fator_lean"]
    out = pd.DataFrame({
        "uf": el.index, "nome": el["nome"].values, "regiao": el["regiao"].values,
        "eleitores": el["eleitores_2026"].values, "abst1": el["abst_1t_2022"].values,
        "bn1": el["bn_1t_2022_pct_comp"].values, "abst2": el["abst_2t_2022"].values,
        "bn2": el["bn_2t_2022_pct_comp"].values,
        "prior1": f * lean1, "prior2": f * lean2,
        "sdprior1": np.where(el.index == "ZZ", prem["estados.dp_prior_exterior_pp"], prem["estados.dp_prior_1t_pp"]),
        "sdprior2": np.where(el.index == "ZZ", prem["estados.dp_prior_exterior_pp"], prem["estados.dp_prior_2t_pp"]),
        "pt2p_1t_2022": el["pt2p_1t_2022"].values, "pt_2t_2022": el["pt_2t_2022"].values,
    })
    # prior demográfico misto (segmentos.py): 1º turno em todas as UFs; 2º turno só nas UFs sem pesquisa de 2º turno
    if prem["estados.usar_prior_demografico"]:
        pri = pd.read_csv(DADOS / "prior_demografico_uf.csv").set_index(["turno", "uf"])
        puf = pd.read_csv(DADOS / "pesquisas_uf.csv")
        sem2t = set(puf.uf) - set(puf[puf.t2_lula.notna()].uf) | (set(out.uf) - set(puf.uf) - {"ZZ"})
        w2 = prem["estados.peso_simples_2t_sem_pesquisa"]
        for i, u in enumerate(out.uf):
            if (1, u) in pri.index:
                out.loc[i, "prior1"] = pri.loc[(1, u), "prior_misto_logito"]
                out.loc[i, "sdprior1"] = pri.loc[(1, u), "dp_prior_recente_pp"]
            if (2, u) in pri.index:
                out.loc[i, "sdprior2"] = pri.loc[(2, u), "dp_prior_recente_pp"]
                if u in sem2t:
                    out.loc[i, "prior2"] = (w2 * pri.loc[(2, u), "prior_simples_logito"]
                                            + (1 - w2) * pri.loc[(2, u), "prior_demografico_logito"])
        out.attrs["ufs_prior_demografico_2t"] = sorted(sem2t & set(out.uf))
    return out


def eleicao_2026(prem: dict) -> Eleicao:
    nac, log = carregar_pesquisas_nacionais_2026()
    st = pd.DataFrame({
        "instituto": nac["instituto"], "campo_fim": nac["campo_fim"], "n": nac["n"],
        "registro": nac["registro"], "base": "totais", "bni": nac["bni"], "ind": np.nan,
        "t2a": nac["t2_lula"], "t2b": nac["t2_flavio"], "obs": nac["obs"].fillna(""),
    })
    for k, c in enumerate(CANDS):
        st[f"c{k}"] = nac[COL[c]]
    nomeados = ["lula", "flavio", "caiado", "cury", "zema", "renan"]
    completo = nac[nomeados].notna().all(axis=1) & nac["bni"].notna()
    outros = (100 - nac[nomeados].sum(axis=1) - nac["bni"]).clip(lower=0)
    st.loc[completo & nac["outros"].isna(), "c6"] = outros[completo & nac["outros"].isna()]
    # base em válidos declarada na observação (ex.: Datafolha 3/10)
    st.loc[st.obs.str.contains("VOTOS VALIDOS", case=False), "base"] = "validos"
    pesos = prem["agregacao.peso_extra_instituto"]
    st["peso_extra"] = st["instituto"].map(lambda i: pesos.get(i, 1.0))
    ex = prem["vies.exposicao_instituto"]
    exposicao = {k: (v["lambda"], v["dp"]) for k, v in ex.items()}

    puf = pd.read_csv(DADOS / "pesquisas_uf.csv")
    for c in ("campo_inicio", "campo_fim", "publicacao"):
        puf[c] = pd.to_datetime(puf[c])
    puf["campo_fim"] = puf["campo_fim"].fillna(puf["publicacao"] - pd.Timedelta(days=1))
    pst = pd.DataFrame({"uf": puf.uf, "instituto": puf.instituto, "campo_fim": puf.campo_fim, "n": puf.n,
                        "t2a": puf.t2_lula, "t2b": puf.t2_flavio})
    for k, c in enumerate(CANDS):
        pst[f"c{k}"] = puf[COL[c]]
    # na UF, "lista completa" = todos os candidatos nomeados; outros vazio -> 0
    pst.loc[pst[["c2", "c3", "c4", "c5"]].notna().all(axis=1) & pst.c6.isna(), "c6"] = 0.0

    ufs = _ufs_2026(prem)
    transf = np.array([prem[f"matriz_transferencia_2t.{c}"] for c in MENORES], float)
    rej = prem["rejeicao.valores_2026"]
    aj = None
    if prem["comparecimento.ajuste_segmentos"]:
        a = pd.read_csv(DADOS / "ajuste_comparecimento_uf.csv").set_index(["turno", "uf"])
        a1 = np.array([a["ajuste_logito"].get((1, u), a.loc[(1, "BR"), "ajuste_logito"]) for u in ufs.uf])
        a2 = np.array([a["ajuste_logito"].get((2, u), a.loc[(2, "BR"), "ajuste_logito"]) for u in ufs.uf])
        aj = {"a1": a1, "a2": a2, "dp1": float(a.loc[(1, "BR"), "dp_ajuste_pp"]),
              "dp2": float(a.loc[(2, "BR"), "dp_ajuste_pp"]),
              "br1_pp": float(a.loc[(1, "BR"), "ajuste_pp"]), "br2_pp": float(a.loc[(2, "BR"), "ajuste_pp"])}
    ref = pd.Timestamp(prem["data_referencia"])
    e = Eleicao(2026, CANDS, ref, st, pst, ufs, transf, pd.Timestamp(prem["agregacao.house_effect_inicio"]),
                rejeicao={"pt": rej["Lula"], "opp": rej["Flavio"]}, exposicao=exposicao, ajuste_comp=aj,
                notas=log)
    return e


def construir_base_2026(prem: dict | None = None, metodo_indecisos: str | None = None) -> Base:
    prem = prem or carregar_premissas()
    return construir_base(eleicao_2026(prem), prem, metodo_indecisos)
