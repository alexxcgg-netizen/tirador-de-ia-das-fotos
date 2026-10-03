"""Modelo Monte Carlo por UF da eleição presidencial brasileira de 2026.

Estrutura (detalhes e fontes em README.md e premissas.json):

1. Agregação nacional das pesquisas (house effects relativos ao consenso,
   peso por recência e sqrt(n)), decomposta em:
     - p2  = fatia de Lula entre os dois primeiros no 1º turno (Lula/(Lula+Flávio));
     - m_k = votos válidos de cada candidato menor (Caiado, Cury, Zema, Renan, Outros);
     - q   = fatia de Lula no 2º turno Lula x Flávio.
2. Médias por UF: prior (nacional + 0,85 x lean de 2022, em logito) combinado com
   as pesquisas estaduais por precisão; depois calibradas para que o agregado
   ponderado pelo eleitorado reproduza a média nacional.
3. Simulação: erro nacional t de Student, fator NE/N x S/CO, fatores regionais,
   erro idiossincrático da UF, contração da terceira via, comparecimento e
   brancos/nulos por UF, 2º turno por pesquisas + matriz de transferência.
   Cenários: 'neutro' (sem viés) e 'historico' (viés anti-PT de 2014/18/22).

Tudo vetorizado em NumPy, float32, em lotes.
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


# ---------------------------------------------------------------- utilidades
def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


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


# ---------------------------------------------------------------- dados
def carregar_pesquisas_nacionais() -> pd.DataFrame:
    df = pd.read_csv(DADOS / "pesquisas_nacionais.csv")
    df["campo_fim"] = pd.to_datetime(df["campo_fim"])
    df["campo_inicio"] = pd.to_datetime(df["campo_inicio"])
    nomeados = ["lula", "flavio", "caiado", "cury", "zema", "renan"]
    completo = df[nomeados].notna().all(axis=1) & df["bni"].notna()
    # 'Outros' (nanicos) = 100 - candidatos listados - BNI  [cálculo]
    df.loc[completo, "outros"] = (100 - df.loc[completo, nomeados].sum(axis=1)
                                  - df.loc[completo, "bni"]).clip(lower=0)
    # denominador de válidos: 100 - BNI (indecisos alocados proporcionalmente)
    df["denom_validos"] = 100 - df["bni"]
    df["p2"] = df["lula"] / (df["lula"] + df["flavio"])
    df["q"] = df["t2_lula"] / (df["t2_lula"] + df["t2_flavio"])
    return df


def carregar_pesquisas_uf(prem: dict) -> pd.DataFrame:
    df = pd.read_csv(DADOS / "pesquisas_uf.csv")
    for c in ("campo_inicio", "campo_fim", "publicacao"):
        df[c] = pd.to_datetime(df[c])
    df["data_ref"] = df["campo_fim"].fillna(df["publicacao"] - pd.Timedelta(days=1))
    df["n"] = df["n"].fillna(prem["estados.n_padrao_sem_amostra"])
    cols = [COL[c] for c in CANDS]
    df["denom_validos"] = df[cols].sum(axis=1, skipna=True)
    df["p2"] = df["lula"] / (df["lula"] + df["flavio"])
    df["q"] = df["t2_lula"] / (df["t2_lula"] + df["t2_flavio"])
    return df


def carregar_ufs() -> pd.DataFrame:
    el = pd.read_csv(DADOS / "eleitorado_uf_2026.csv")
    res = pd.read_csv(DADOS / "resultados_uf_2002_2022.csv")
    r22 = res[res.ano == 2022]
    t1 = r22[r22.turno == 1].set_index("uf")
    t2 = r22[r22.turno == 2].set_index("uf")
    el = el.set_index("uf")
    # fatia bipartidária do PT em 2022 (1º turno: PT/(PT+Bolsonaro); 2º turno: PT % válidos)
    el["pt2p_1t_2022"] = t1["pt_2p_pct"] / 100
    el["pt_2t_2022"] = t2["pt_pct_validos"] / 100
    br_1t = t1.loc["BR", "pt_2p_pct"] / 100
    br_2t = t2.loc["BR", "pt_pct_validos"] / 100
    el["lean1_logit"] = logit(el["pt2p_1t_2022"].values) - logit(br_1t)
    el["lean2_logit"] = logit(el["pt_2t_2022"].values) - logit(br_2t)
    return el.reset_index()


# ---------------------------------------------------------------- agregação nacional
def estimar_house_effects(df: pd.DataFrame, coluna: str, prem: dict) -> dict:
    """Efeito de instituto em logito: y = mu_semana + h_inst + e, soma(h)=0, ridge em h."""
    inicio = pd.Timestamp(prem["agregacao.house_effect_inicio"])
    ref = pd.Timestamp(prem["data_referencia"])
    d = df[(df.campo_fim >= inicio) & (df.campo_fim <= ref) & df[coluna].notna()].copy()
    if d.empty:
        return {}
    d["y"] = logit(d[coluna].values)
    d["sem"] = ((d.campo_fim - inicio).dt.days // 7).clip(upper=5)
    semanas = sorted(d["sem"].unique())
    insts = sorted(d["instituto"].unique())
    W, J = len(semanas), len(insts)
    X = np.zeros((len(d), W + J))
    for i, (s, ins) in enumerate(zip(d["sem"], d["instituto"])):
        X[i, semanas.index(s)] = 1
        X[i, W + insts.index(ins)] = 1
    y = d["y"].values
    sd_resid = 1.2 / 25          # ~1,2 p.p. de ruído por pesquisa (inferência)
    sd_prior = prem["agregacao.house_effect_prior_sd_pp"] / 25
    lam = (sd_resid / sd_prior) ** 2
    R = np.zeros((J, W + J))
    R[:, W:] = np.sqrt(lam) * np.eye(J)
    C = np.zeros((1, W + J))
    C[0, W:] = 1000.0          # restrição soma(h) = 0
    A = np.vstack([X, R, C])
    b = np.concatenate([y, np.zeros(J), [0.0]])
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    h = sol[W:]
    cont = d.groupby("instituto").size()
    return {ins: {"h_logito": float(h[j]), "h_pp": float(h[j] * 25), "n_pesquisas": int(cont[ins])}
            for j, ins in enumerate(insts)}


def _selecionar_recentes(df, coluna, prem):
    ref = pd.Timestamp(prem["data_referencia"])
    jan = prem["agregacao.janela_dias"]
    d = df[df[coluna].notna() & (df.campo_fim <= ref) &
           (df.campo_fim > ref - pd.Timedelta(days=jan))].copy()
    d = d.sort_values("campo_fim").groupby("instituto").tail(1)
    dias = (ref - d.campo_fim).dt.days.clip(lower=0)
    n = d["n"].fillna(2000).clip(upper=prem["agregacao.n_teto"])
    d["peso"] = np.sqrt(n) * np.exp(-dias / prem["agregacao.tau_recencia_dias"])
    d["dias"] = dias
    return d


def media_nacional(df, coluna, house, prem):
    d = _selecionar_recentes(df, coluna, prem)
    h = d["instituto"].map(lambda i: house.get(i, {}).get("h_logito", 0.0))
    y = logit(d[coluna].values) - h.values
    w = d["peso"].values
    media = float(expit(np.sum(w * y) / np.sum(w)))
    media_bruta = float(expit(np.sum(w * logit(d[coluna].values)) / np.sum(w)))
    tabela = [{"instituto": r.instituto, "campo_fim": r.campo_fim.strftime("%Y-%m-%d"),
               "n": None if pd.isna(r.n) else int(r.n), "valor": round(float(getattr(r, coluna)) * 100, 2),
               "house_pp": round(house.get(r.instituto, {}).get("h_pp", 0.0), 2),
               "peso_rel": round(float(r.peso / d["peso"].sum()), 3)}
              for r in d.itertuples()]
    return media, media_bruta, tabela


def menores_nacionais(df, prem):
    """Votos válidos médios de cada candidato menor (pesquisas recentes com o dado)."""
    out = {}
    for c in MENORES:
        col = COL[c]
        d = df[df["denom_validos"].notna()].copy()
        d = _selecionar_recentes(d, col, prem)
        v = d[col] / d["denom_validos"]
        out[c] = float(np.sum(d["peso"] * v) / np.sum(d["peso"]))
    return out


# ---------------------------------------------------------------- médias por UF
def combinar(prior, sd_prior, obs, sd_obs):
    prec = 1 / sd_prior ** 2 + np.sum(1 / np.asarray(sd_obs) ** 2)
    media = (prior / sd_prior ** 2 + np.sum(np.asarray(obs) / np.asarray(sd_obs) ** 2)) / prec
    return media, math.sqrt(1 / prec)


@dataclass
class Base:
    prem: dict
    ufs: pd.DataFrame
    p2_nat: float
    q_nat: float
    menores_nat: dict
    p2_uf: np.ndarray
    q_uf: np.ndarray
    m_uf: np.ndarray            # (U, 5) votos válidos dos menores
    sd_p2_uf: np.ndarray        # dp posterior (p.p.)
    sd_q_uf: np.ndarray
    house_1t: dict
    house_2t: dict
    tabela_1t: list
    tabela_2t: list
    p2_bruta: float
    q_bruta: float
    detalhe_uf: list = field(default_factory=list)


def construir_base(prem: dict | None = None) -> Base:
    prem = prem or carregar_premissas()
    nac = carregar_pesquisas_nacionais()
    puf = carregar_pesquisas_uf(prem)
    ufs = carregar_ufs()
    ref = pd.Timestamp(prem["data_referencia"])

    house1 = estimar_house_effects(nac, "p2", prem)
    house2 = estimar_house_effects(nac, "q", prem)
    p2_nat, p2_bruta, tab1 = media_nacional(nac, "p2", house1, prem)
    q_nat, q_bruta, tab2 = media_nacional(nac, "q", house2, prem)
    mnat = menores_nacionais(nac, prem)

    f = prem["estados.fator_lean"]
    sdp = prem["estados.dp_prior_pp"] / 100
    piso = prem["estados.dp_pesquisa_piso_pp"] / 100
    deff = prem["estados.efeito_desenho"]
    tau = prem["estados.tau_recencia_uf_dias"]
    sdpm = prem["estados.dp_prior_menores_pp"] / 100
    pisom = prem["estados.dp_pesquisa_menores_piso_pp"] / 100

    U = len(ufs)
    p2_uf = np.zeros(U); q_uf = np.zeros(U); sd1 = np.zeros(U); sd2 = np.zeros(U)
    m_uf = np.zeros((U, len(MENORES)))
    detalhe = []
    for i, r in ufs.iterrows():
        pr1 = float(expit(logit(p2_nat) + f * r.lean1_logit))
        pr2 = float(expit(logit(q_nat) + f * r.lean2_logit))
        pol = puf[puf.uf == r.uf]
        o1, s1, o2, s2 = [], [], [], []
        for p in pol.itertuples():
            dias = max((ref - p.data_ref).days, 0)
            infl = 1 + dias / tau
            if not np.isnan(p.p2):
                n_top = p.n * (p.lula + p.flavio) / 100
                v = deff * p.p2 * (1 - p.p2) / n_top + piso ** 2
                o1.append(p.p2); s1.append(math.sqrt(v * infl))
            if not np.isnan(p.q):
                n_top = p.n * (p.t2_lula + p.t2_flavio) / 100
                v = deff * p.q * (1 - p.q) / n_top + piso ** 2
                o2.append(p.q); s2.append(math.sqrt(v * infl))
        p2_uf[i], sd1[i] = combinar(pr1, sdp, o1, s1)
        q_uf[i], sd2[i] = combinar(pr2, sdp, o2, s2)
        for k, c in enumerate(MENORES):
            obs, sds = [], []
            for p in pol.itertuples():
                x = getattr(p, COL[c])
                if not np.isnan(x) and p.denom_validos > 0 and not np.isnan(p.p2):
                    # só usa se a pesquisa lista os menores (denominador = soma dos candidatos)
                    if pd.isna(p.caiado):
                        continue
                    v = x / p.denom_validos
                    var = deff * max(v, 0.005) * (1 - v) / p.n + pisom ** 2
                    obs.append(v); sds.append(math.sqrt(var * (1 + max((ref - p.data_ref).days, 0) / tau)))
            m_uf[i, k], _ = combinar(mnat[c], sdpm, obs, sds)
        m_uf[i] = np.clip(m_uf[i], 0.001, None)
        detalhe.append({"uf": r.uf, "prior_p2": pr1, "prior_q": pr2,
                        "pesquisas_1t": len(o1), "pesquisas_2t": len(o2)})

    # ---- calibração: agregado ponderado das UFs = média nacional
    w1 = (ufs.eleitores_2026 * (1 - ufs.abst_1t_2022 / 100) * (1 - ufs.bn_1t_2022_pct_comp / 100)).values
    w2 = (ufs.eleitores_2026 * (1 - ufs.abst_2t_2022 / 100) * (1 - ufs.bn_2t_2022_pct_comp / 100)).values
    alvo_m = np.array([mnat[c] for c in MENORES])
    for _ in range(50):
        agg_m = (w1[:, None] * m_uf).sum(0) / w1.sum()
        m_uf = m_uf * (alvo_m / agg_m)[None, :]
    T = 1 - m_uf.sum(1)
    d1 = _resolver_desloc(p2_uf, w1 * T, p2_nat)
    p2_cal = expit(logit(p2_uf) + d1)
    d2 = _resolver_desloc(q_uf, w2, q_nat)
    q_cal = expit(logit(q_uf) + d2)
    for i, dd in enumerate(detalhe):
        dd.update({"p2_pesquisas_prior": float(p2_uf[i]), "q_pesquisas_prior": float(q_uf[i]),
                   "p2_calibrado": float(p2_cal[i]), "q_calibrado": float(q_cal[i])})
    base = Base(prem, ufs, p2_nat, q_nat, mnat, p2_cal, q_cal, m_uf,
                sd1 * 100, sd2 * 100, house1, house2, tab1, tab2, p2_bruta, q_bruta, detalhe)
    base.desloc_calibracao = {"p2_logito": float(d1), "q_logito": float(d2),
                              "p2_pp_aprox": float(d1 * 25), "q_pp_aprox": float(d2 * 25)}
    return base


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


# ---------------------------------------------------------------- simulação
def _t_unit(rng, shape, df):
    """t de Student com variância 1."""
    z = rng.standard_normal(shape, dtype=np.float32)
    g = rng.chisquare(df, size=shape).astype(np.float32) / df
    return z / np.sqrt(g) * np.float32(math.sqrt((df - 2) / df))


def _beta_params(m, s):
    k = m * (1 - m) / s ** 2 - 1
    return m * k, (1 - m) * k


def simular_lote(base: Base, cenario: str, B: int, rng: np.random.Generator) -> dict:
    """Simula B eleições. Devolve arrays nacionais (B,...) e por UF (B,U)."""
    P = base.prem
    ufs = base.ufs
    U = len(ufs)
    f32 = np.float32
    reg_idx = np.array([REGIOES.index(r) if r in REGIOES else -1 for r in ufs.regiao])
    cargas = P["estados.cargas_eixo"]
    load = np.array([cargas.get(r, 0.0) for r in ufs.regiao], dtype=f32)
    w_ele = ufs.eleitores_2026.values.astype(f32)
    load = load - np.sum(w_ele * load) / np.sum(w_ele)

    # ---------- 1º turno: erros nacionais
    df1 = P["erro_nacional_1t.gl_t"]
    z1 = rng.standard_normal(B, dtype=np.float32)
    g1 = rng.chisquare(df1, B).astype(f32) / df1
    sc1 = f32(math.sqrt((df1 - 2) / df1))
    e_p2 = (z1 / np.sqrt(g1) * sc1) * f32(P["erro_nacional_1t.dp_p2_pp"] / 25)
    eta = rng.standard_normal((B, 1, len(MENORES)), dtype=np.float32) * f32(P["erro_nacional_1t.dp_log_menores"])

    # subnacional 1T (logito)
    sd_ax = P["estados.dp_eixo_pp"] / 25
    sd_rg = P["estados.dp_regional_pp"] / 25
    ax = rng.standard_normal(B, dtype=np.float32)[:, None] * f32(sd_ax) * load[None, :]
    rg_draw = rng.standard_normal((B, len(REGIOES)), dtype=np.float32) * f32(sd_rg)
    rg = np.where(reg_idx[None, :] >= 0, rg_draw[:, np.clip(reg_idx, 0, None)], 0).astype(f32)
    p_uf = base.p2_uf
    sd_id = np.maximum(base.sd_p2_uf, P["estados.dp_uf_minimo_pp"]) / 100 / (p_uf * (1 - p_uf))
    tid = _t_unit(rng, (B, U), 5)
    sub1 = ax + rg + tid * sd_id[None, :].astype(f32)

    T_med = 1 - base.m_uf.sum(1)
    w_cent = w_ele * T_med * p_uf * (1 - p_uf)
    sub1 = sub1 - (sub1 @ (w_cent / w_cent.sum()).astype(f32))[:, None]

    p2 = expit(logit(base.p2_uf)[None, :].astype(f32) + e_p2[:, None] + sub1).astype(f32)

    eta_uf = rng.standard_normal((B, U, len(MENORES)), dtype=np.float32) * f32(P["estados.dp_log_menores_uf"])
    m = base.m_uf[None, :, :].astype(f32) * np.exp(eta + eta_uf)
    tot = m.sum(2, keepdims=True)
    m = np.where(tot > 0.6, m * (0.6 / tot), m)
    top = 1 - m.sum(2)

    # contração da terceira via
    a, b = _beta_params(P["terceira_via.contracao_media"], P["terceira_via.contracao_dp"])
    s = rng.beta(a, b, B).astype(f32)
    alfa = P["matriz_transferencia_2t.alfa_dirichlet"]
    TM = np.stack([rng.dirichlet(alfa * np.array(P[f"matriz_transferencia_2t.{c}"]), B) for c in MENORES],
                  axis=1).astype(f32)                         # (B,5,3)
    r_l = TM[:, :, 0] / (TM[:, :, 0] + TM[:, :, 1])           # (B,5)
    movido = s[:, None, None] * m
    m = m - movido
    L = top * p2 + (movido * r_l[:, None, :]).sum(2)
    F = top * (1 - p2) + (movido * (1 - r_l[:, None, :])).sum(2)

    b1 = np.zeros(B, dtype=f32)
    b2 = np.zeros(B, dtype=f32)
    if cenario == "historico":
        b1 = np.maximum(rng.normal(P["vies_historico.vies_1t_flavio_media_pp"],
                                   P["vies_historico.vies_1t_flavio_dp_pp"], B), 0).astype(f32) / 100
        b2 = rng.normal(P["vies_historico.vies_2t_lula_media_pp"],
                        P["vies_historico.vies_2t_lula_dp_pp"], B).astype(f32) / 100
        fl = P["vies_historico.vies_1t_fracao_de_lula"]
        M_nat = float(sum(base.menores_nat.values()) * (1 - P["terceira_via.contracao_media"]))
        L_nat = float((1 - sum(base.menores_nat.values())) * base.p2_nat)
        g = np.clip(b1 * (1 - fl) / M_nat, 0, 0.9)
        h = np.clip(b1 * fl / L_nat, 0, 0.5)
        m = m * (1 - g)[:, None, None]
        L = L * (1 - h)[:, None]
        F = 1 - L - m.sum(2)

    shares = np.concatenate([L[:, :, None], F[:, :, None], m], axis=2)     # (B,U,7)

    # comparecimento e brancos/nulos
    C = P
    def valid_w(abst, bn):
        an = rng.normal(0, C["comparecimento.dp_abst_nacional_pp"], (B, 1))
        au = rng.normal(0, C["comparecimento.dp_abst_uf_pp"], (B, U))
        bnn = rng.normal(0, C["comparecimento.dp_bn_nacional_pp"], (B, 1))
        bnu = rng.normal(0, C["comparecimento.dp_bn_uf_pp"], (B, U))
        ab = np.clip(abst[None, :] + an + au, 5, 70) / 100
        bb = np.clip(bn[None, :] + bnn + bnu, 0.5, 25) / 100
        return (w_ele[None, :] * (1 - ab) * (1 - bb)).astype(f32), ab.astype(f32)
    wv1, ab1 = valid_w(ufs.abst_1t_2022.values, ufs.bn_1t_2022_pct_comp.values)
    nat1 = np.einsum("bu,buk->bk", wv1, shares) / wv1.sum(1, keepdims=True)

    # ---------- 2º turno
    df2 = P["erro_2t.gl_t"]
    rho = P["erro_2t.rho_com_1t"]
    z2 = rho * z1 + math.sqrt(1 - rho ** 2) * rng.standard_normal(B, dtype=np.float32)
    g2 = rng.chisquare(df2, B).astype(f32) / df2
    e_q = z2 / np.sqrt(g2) * f32(math.sqrt((df2 - 2) / df2)) * f32(P["erro_2t.dp_q_pp"] / 25)
    q_u = base.q_uf
    sd_id2 = np.maximum(base.sd_q_uf, P["estados.dp_uf_minimo_pp"]) / 100 / (q_u * (1 - q_u))
    ru = P["erro_2t.rho_uf_1t_2t"]
    ax2 = rng.standard_normal(B, dtype=np.float32)[:, None] * f32(sd_ax) * load[None, :]
    rg2d = rng.standard_normal((B, len(REGIOES)), dtype=np.float32) * f32(sd_rg)
    rg2 = np.where(reg_idx[None, :] >= 0, rg2d[:, np.clip(reg_idx, 0, None)], 0).astype(f32)
    tid2 = _t_unit(rng, (B, U), 5)
    ind2 = ax2 + rg2 + tid2 * sd_id2[None, :].astype(f32)
    sub2 = f32(ru) * sub1 * (sd_id2 / sd_id)[None, :].astype(f32) + f32(math.sqrt(1 - ru ** 2)) * ind2
    w_c2 = w_ele * q_u * (1 - q_u)
    sub2 = sub2 - (sub2 @ (w_c2 / w_c2.sum()).astype(f32))[:, None]
    q_poll = expit(logit(q_u)[None, :].astype(f32) + e_q[:, None] + sub2 - (b2 / 0.25)[:, None])

    num = L + (m * TM[:, None, :, 0]).sum(2)
    den = L + F + (m * (TM[:, None, :, 0] + TM[:, None, :, 1])).sum(2)
    q_tr = num / den
    wq = P["erro_2t.peso_pesquisas_vs_transferencia"]
    q = expit(wq * logit(q_poll) + (1 - wq) * logit(q_tr)).astype(f32)
    wv2, ab2 = valid_w(ufs.abst_2t_2022.values, ufs.bn_2t_2022_pct_comp.values)
    Wn = wv2.sum(1)
    Q = (wv2 * q).sum(1) / Wn
    Qp = (wv2 * q_poll).sum(1) / Wn
    Qt = (wv2 * q_tr).sum(1) / Wn

    # ---------- desfecho
    ordem = np.argsort(-nat1, axis=1)
    primeiro, segundo = ordem[:, 0], ordem[:, 1]
    venceu_1t = nat1.max(1) > 0.5
    par_lf = ((primeiro == 0) & (segundo == 1)) | ((primeiro == 1) & (segundo == 0))
    vencedor = np.where(venceu_1t, primeiro,
                        np.where(par_lf, np.where(Q > 0.5, 0, 1), primeiro)).astype(np.int8)

    # nacional "implícito" pelo erro nacional (para teste de consistência)
    nat_p2_agregado = nat1[:, 0] / (nat1[:, 0] + nat1[:, 1])

    return {
        "nat1": nat1.astype(f32), "Q": Q.astype(f32), "Q_pesquisas": Qp.astype(f32), "Q_transf": Qt.astype(f32),
        "primeiro": primeiro.astype(np.int8), "segundo": segundo.astype(np.int8),
        "venceu_1t": venceu_1t, "par_lf": par_lf, "vencedor": vencedor,
        "uf_L": shares[:, :, 0], "uf_F": shares[:, :, 1], "uf_top": np.argmax(shares, 2).astype(np.int8),
        "uf_q": q, "e_p2": e_p2, "nat_p2_agregado": nat_p2_agregado.astype(f32),
        "b1": b1, "b2": b2,
    }
