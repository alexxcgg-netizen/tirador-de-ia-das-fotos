"""Transferência regionalizada no 2º turno e variação do comparecimento entre turnos por UF.

Lição do 1º turno de 2026: os erros por UF do modelo de véspera foram regionalmente estruturados (PT subestimado
no NE/N, superestimado no S). O 2º turno condicionado ao 1º turno real já parte das fatias reais de cada UF, mas
aplicava UMA matriz de transferência nacional (Quaest) a todos os estados. Aqui a fatia "decidida" que cada
eliminado transfere ao PT, p_k = a_k / (a_k + b_k), passa a depender da inclinação partidária da UF no 1º turno:

    logito p_{k,u} = logito p_k + beta * z_u + c_k(beta),     z_u = logito(L_u/(L_u+F_u)) − logito(L_BR/(L_BR+F_BR))

* p_k e a participação a_k + b_k vêm da matriz nacional (Quaest), que continua sendo o âncora;
* c_k(beta) recentra cada linha para que a média nacional (ponderada pelos votos do eliminado em cada UF) volte a
  ser exatamente p_k — a regionalização redistribui entre UFs, não muda o nacional da matriz;
* beta (efeito de contexto: um eleitor de terceira via num estado muito antipetista vai mais para o antipetista)
  é estimado de forma ecológica com os resultados por UF do TSE (1º -> 2º turno) de 2002, 2010, 2014, 2018 e 2022,
  e combinado hierarquicamente (média entre eleições, variância entre eleições pelo método dos momentos); na
  simulação beta ~ N(mu, dp²) por sorteio, além da Dirichlet da matriz;
* efeito regional adicional (N, NE, CO, SE, S) nos resíduos depois de beta: média entre eleições encolhida
  (empírico-bayesiano) — só entra se o backtest fora da amostra melhorar.

2006 fica fora da estimativa: Alckmin perdeu votos entre turnos (a transferência não é identificável).
Validação: ``backtest_regional()`` (leave-one-election-out em 2014, 2018 e 2022 com o que se sabia na véspera).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

import modelo as M

REGIOES = ["N", "NE", "CO", "SE", "S", "EXT"]
ANOS_BETA = (2002, 2010, 2014, 2018, 2022)
PART_HIST = 0.65            # participação (a + b) da linha usada só para estimar beta nos anos históricos

PARAM_REG = {
    "beta_prior_media": {"valor": 0.0, "origem": "inferencia",
                         "nota": "Prior de beta centrado em zero (= matriz nacional uniforme)."},
    "beta_prior_dp": {"valor": 0.5, "origem": "inferencia",
                      "nota": "Prior fraco de beta (logito por logito de lean)."},
    "beta_tau_min": {"valor": 0.15, "origem": "inferencia",
                     "nota": "Piso da variação de beta entre eleições (só 4-5 eleições)."},
    "usar_efeito_regional": {"valor": False, "origem": "backtest",
                             "nota": "Efeito regional fixo além de beta: piorou ou não mudou o backtest (ver BACKTEST.md)."},
    "encolhimento_comparecimento_k": {"valor": 1.0, "origem": "backtest",
                                      "nota": "Variação da abstenção 1º->2º turno por UF = nacional do ano + desvio "
                                              "médio da UF encolhido n/(n+k) (n = eleições anteriores)."},
}


def lean_z(L, F, w) -> np.ndarray:
    """Lean bipartidário em logito: logito(L/(L+F)) na UF menos o nacional (ponderado por w)."""
    L, F, w = np.asarray(L, float), np.asarray(F, float), np.asarray(w, float)
    pn = np.sum(w * L) / np.sum(w * (L + F))
    return M.logit(L / (L + F)) - M.logit(pn)


def _ajuste_ano(d: dict, part: float = PART_HIST) -> dict:
    """(logito p, beta, ep de beta) de um ano por MQ não linear ponderado nas 27 UFs."""
    from scipy.optimize import least_squares
    m = np.array([u != "ZZ" for u in d["ufs"]])
    L, F, T, q, w = d["L"][m], d["F"][m], d["T"][m], d["q"][m], d["V1"][m]
    z = lean_z(L, F, w)
    sw = np.sqrt(w / w.mean())

    def f(th):
        pu = M.expit(th[0] + th[1] * z)
        return (L + T * part * pu) / (L + F + T * part)
    r = least_squares(lambda th: (f(th) - q) * sw, [0.0, 0.0])
    J = r.jac
    s2 = float(np.sum(r.fun ** 2) / max(len(q) - 2, 1))
    try:
        cov = np.linalg.inv(J.T @ J) * s2
        ep = float(math.sqrt(max(cov[1, 1], 0)))
    except np.linalg.LinAlgError:
        ep = float("nan")
    return {"logit_p": float(r.x[0]), "beta": float(r.x[1]), "ep_beta": ep}


_CACHE = {}


def estimar_beta(anos: tuple = ANOS_BETA) -> dict:
    """Combinação hierárquica de beta entre eleições: beta_ano ~ N(mu, tau² + ep²), prior mu ~ N(0, 0,5²)."""
    chave = tuple(anos)
    if chave in _CACHE:
        return _CACHE[chave]
    import resultado_1t as R
    por_ano = {a: _ajuste_ano(R.historico_ano(a)) for a in anos}
    b = np.array([v["beta"] for v in por_ano.values()])
    e = np.array([v["ep_beta"] if np.isfinite(v["ep_beta"]) else 0.5 for v in por_ano.values()])
    tau_min = PARAM_REG["beta_tau_min"]["valor"]
    tau2 = max(float(np.var(b, ddof=1) - np.mean(e ** 2)) if len(b) > 1 else 0.0, tau_min ** 2)
    m0, s0 = PARAM_REG["beta_prior_media"]["valor"], PARAM_REG["beta_prior_dp"]["valor"]
    wts = 1 / (tau2 + e ** 2)
    prec = 1 / s0 ** 2 + wts.sum()
    mu = float((m0 / s0 ** 2 + np.sum(wts * b)) / prec)
    sd_mu = math.sqrt(1 / prec)
    out = {"anos": list(anos), "mu": mu, "dp_mu": sd_mu, "tau": math.sqrt(tau2),
           "dp_preditivo": math.sqrt(tau2 + sd_mu ** 2),
           "por_ano": {int(a): {k: round(v, 4) for k, v in x.items()} for a, x in por_ano.items()}}
    _CACHE[chave] = out
    return out


def _recentrar(p0: float, z: np.ndarray, peso: np.ndarray, beta: float) -> float:
    """c tal que sum(peso * expit(logito p0 + beta z + c)) / sum(peso) = p0."""
    if beta == 0 or peso.sum() <= 0:
        return 0.0
    return M._resolver_desloc(np.clip(M.expit(M.logit(p0) + beta * z), 1e-4, 1 - 1e-4), peso, p0)


def linhas_uf(rows: np.ndarray, S: np.ndarray, A: int, B: int, elim: list, V: np.ndarray, beta: float,
              efeito_reg: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Linhas de transferência por UF (U, E, 3) a partir das linhas nacionais (E, 3).

    S: fatias do 1º turno (U, K); V: votos válidos do 1º turno por UF (U,). Mantém a participação a+b de cada
    linha e o p_k nacional (ponderado pelos votos do eliminado). Devolve (linhas, z)."""
    rows = np.asarray(rows, float)
    z = lean_z(S[:, A], S[:, B], V)
    U, E = S.shape[0], len(elim)
    out = np.empty((U, E, 3))
    for j, k in enumerate(elim):
        a, b, c = rows[j]
        part = a + b
        p0 = a / part if part > 0 else 0.5
        peso = V * S[:, k]
        cc = _recentrar(p0, z, peso, beta)
        pu = M.expit(M.logit(p0) + beta * z + cc + (0 if efeito_reg is None else efeito_reg))
        out[:, j, 0] = part * pu
        out[:, j, 1] = part * (1 - pu)
        out[:, j, 2] = c
    return out, z


def deslocamentos_beta(rows, S, A, B, elim, V, grade=np.linspace(-1.5, 2.5, 81)) -> tuple[np.ndarray, np.ndarray]:
    """c_k(beta) numa grade (para interpolar nas simulações sem resolver a bisseção a cada sorteio)."""
    z = lean_z(S[:, A], S[:, B], V)
    C = np.zeros((len(grade), len(elim)))
    for j, k in enumerate(elim):
        a, b, _ = rows[j]
        p0 = a / (a + b) if a + b > 0 else 0.5
        for i, bt in enumerate(grade):
            C[i, j] = _recentrar(p0, z, V * S[:, k], bt)
    return grade, C


# ============================================================ backtest (LOEO) 2014/2018/2022
def _qtr(L, F, T, linha, z=None, beta=0.0, V=None):
    """2º turno PT pela via de transferência com uma linha [PT, adv, fora] e, opcionalmente, beta."""
    a, b, _ = linha
    part = a + b
    p0 = a / part
    if beta and z is not None:
        cc = _recentrar(p0, z, V * T, beta)
        p = M.expit(M.logit(p0) + beta * z + cc)
    else:
        p = np.full_like(L, p0)
    return (L + T * part * p) / (L + F + T * part)


def _linha_vespera(ano: int) -> list:
    """Linha de transferência implícita nas pesquisas da véspera (2014+); antes disso, a linha genérica."""
    import resultado_1t as R
    if ano >= 2014:
        return R.preditores_hist(ano)["linha"]
    return list(R.LINHA_GENERICA)


def efeitos_regionais(anos: tuple, beta: float) -> dict:
    """Média por região dos resíduos (p.p.) depois do deslocamento nacional, encolhida (EB) entre anos."""
    import resultado_1t as R
    rows = []
    for a in anos:
        d = R.historico_ano(a)
        linha = _linha_vespera(a)
        m = np.array([u != "ZZ" for u in d["ufs"]])
        L, F, T, q, w = d["L"][m], d["F"][m], d["T"][m], d["q"][m], d["V1"][m]
        z = lean_z(L, F, w)
        qt = _qtr(L, F, T, linha, z, beta, w)
        dd = M._resolver_desloc(np.clip(qt, 1e-4, 1 - 1e-4), w, d["q_br"])
        r = 100 * (q - M.expit(M.logit(qt) + dd))
        for u, x in zip(np.array(d["ufs"])[m], r):
            rows.append({"ano": a, "regiao": R.REGIAO[u], "res": x})
    t = pd.DataFrame(rows)
    g = t.groupby(["regiao", "ano"]).res.mean().unstack()
    n = g.shape[1]
    media = g.mean(axis=1)
    var_entre = float(np.var(g.values, ddof=1)) if n > 1 else 1.0
    var_media = (g.var(axis=1, ddof=1) / n).fillna(var_entre / n)
    tau2 = max(float(np.var(media.values, ddof=1) - var_media.mean()), 0.0) if len(media) > 1 else 0.0
    k = tau2 / (tau2 + var_media)
    return {r: float(media[r] * k[r]) for r in media.index}


def backtest_regional(anos=(2002, 2010, 2014, 2018, 2022), log=print) -> pd.DataFrame:
    """UF MAE / viés regional, LOEO: para cada ano, beta (e efeitos regionais) estimados sem o ano; linha nacional =
    a implícita nas pesquisas da véspera (como no ensaio); centro nacional = real (isola a distribuição entre UFs) e
    = projeção (como no pipeline). Compara 'nacional' (matriz única) x 'beta' x 'beta+regiao'."""
    import resultado_1t as R
    out = []
    for a in anos:
        d = R.historico_ano(a)
        linha_v = _linha_vespera(a)
        m = np.array([u != "ZZ" for u in d["ufs"]])
        L, F, T, q, w = d["L"][m], d["F"][m], d["T"][m], d["q"][m], d["V1"][m]
        ufs = np.array(d["ufs"])[m]
        reg = np.array([R.REGIAO[u] for u in ufs])
        z = lean_z(L, F, w)
        eb = estimar_beta(tuple(x for x in ANOS_BETA if x != a))
        ef = efeitos_regionais(tuple(x for x in ANOS_BETA if x != a), eb["mu"])
        variantes = {"nacional": _qtr(L, F, T, linha_v),
                     "beta": _qtr(L, F, T, linha_v, z, eb["mu"], w)}
        vb = variantes["beta"]
        efu = np.array([ef.get(g, 0.0) for g in reg]) / (100 * vb * (1 - vb))
        variantes["beta+regiao"] = M.expit(M.logit(vb) + efu)
        for nome, qt in variantes.items():
            dd = M._resolver_desloc(np.clip(qt, 1e-4, 1 - 1e-4), w, d["q_br"])
            qa = M.expit(M.logit(qt) + dd)
            e = 100 * (qa - q)
            qbr = float(np.sum(w * qt) / w.sum())
            linha = {"ano": a, "variante": nome, "beta": eb["mu"] if nome != "nacional" else 0.0,
                     "uf_mae_pp": float(np.mean(np.abs(e))), "uf_rmse_pp": float(np.sqrt(np.mean(e ** 2))),
                     "nacional_transferencia_erro_pp": 100 * (qbr - d["q_br"]),
                     "corr_erro_lean": float(np.corrcoef(e, z)[0, 1])}
            for g in ["N", "NE", "CO", "SE", "S"]:
                linha[f"vies_{g}"] = float(np.mean(e[reg == g]))
            out.append(linha)
    t = pd.DataFrame(out)
    log(t.round(3).to_string())
    return t


# ============================================================ comparecimento 1º -> 2º turno
def delta_comparecimento_eb(anos: tuple, k: float | None = None) -> pd.DataFrame:
    """d_abst/d_bn por UF = média nacional dos anos + desvio médio da UF encolhido n/(n + k)."""
    import resultado_1t as R
    k = PARAM_REG["encolhimento_comparecimento_k"]["valor"] if k is None else k
    rows = []
    for a in anos:
        d = R.historico_ano(a)
        da, db = d["abst2"] - d["abst1"], d["bn2"] - d["bn1"]
        w = d["eleitores"]
        mna, mnb = np.sum(w * da) / w.sum(), np.sum(w * db) / w.sum()
        for i, u in enumerate(d["ufs"]):
            rows.append({"ano": a, "uf": u, "d_abst": da[i], "d_bn": db[i], "dev_a": da[i] - mna, "dev_b": db[i] - mnb,
                         "nac_a": mna, "nac_b": mnb})
    t = pd.DataFrame(rows)
    n = len(anos)
    f = n / (n + k)
    nac = t.groupby("ano")[["nac_a", "nac_b"]].first().mean()
    g = t.groupby("uf")[["dev_a", "dev_b"]].mean()
    res = pd.DataFrame({"d_abst": nac["nac_a"] + f * g["dev_a"], "d_bn": nac["nac_b"] + f * g["dev_b"]})
    return res.reindex(R.UFS).fillna({"d_abst": nac["nac_a"], "d_bn": nac["nac_b"]})


def backtest_comparecimento(anos=(2014, 2018, 2022), log=print) -> dict:
    """LOEO: erro da abstenção do 2º turno por UF (p.p.) com média simples por UF (atual) x encolhida; efeito
    partidário: correlação da variação da abstenção com o lean e efeito da reponderação das UFs no PT nacional."""
    import resultado_1t as R
    linhas, part = [], []
    for a in anos:
        d = R.historico_ano(a)
        outros = tuple(x for x in anos if x != a)
        m = np.array([u != "ZZ" for u in d["ufs"]])
        real = d["abst2"]
        for nome, dc in {"media_uf": R.delta_comparecimento(outros), "encolhida_k1": delta_comparecimento_eb(outros, 1.0),
                         "encolhida_k3": delta_comparecimento_eb(outros, 3.0),
                         "so_nacional": delta_comparecimento_eb(outros, 1e9),
                         "sem_variacao": pd.DataFrame({"d_abst": 0.0, "d_bn": 0.0}, index=R.UFS)}.items():
            pa = d["abst1"] + dc.reindex(d["ufs"])["d_abst"].values
            pb = d["bn1"] + dc.reindex(d["ufs"])["d_bn"].values
            e = (pa - real)[m]
            # efeito no PT nacional (2º turno real por UF, pesos = válidos previstos x válidos reais)
            W_pred = d["eleitores"] * (1 - pa / 100) * (1 - pb / 100)
            W_real = d["V2"]
            q_pred = float(np.sum(W_pred * d["q"]) / W_pred.sum())
            q_real_w = float(np.sum(W_real * d["q"]) / W_real.sum())
            linhas.append({"ano": a, "metodo": nome, "mae_abst_uf_pp": float(np.mean(np.abs(e))),
                           "vies_abst_pp": float(np.mean(e)), "mae_bn_uf_pp": float(np.mean(np.abs((pb - d["bn2"])[m]))),
                           "efeito_pt_nacional_pp": 100 * (q_pred - q_real_w)})
        z = lean_z(d["L"][m], d["F"][m], d["V1"][m])
        da = (d["abst2"] - d["abst1"])[m]
        part.append({"ano": a, "corr_dabst_lean": float(np.corrcoef(da, z)[0, 1]),
                     "inclinacao_pp_por_logito": float(np.polyfit(z, da, 1)[0]),
                     "d_abst_nacional_pp": float(np.sum(d["eleitores"] * (d["abst2"] - d["abst1"])) / d["eleitores"].sum())})
    t = pd.DataFrame(linhas)
    resumo = t.groupby("metodo")[["mae_abst_uf_pp", "mae_bn_uf_pp", "efeito_pt_nacional_pp"]].agg(
        lambda x: float(np.mean(np.abs(x))))
    log(t.round(3).to_string())
    log(resumo.round(3).to_string())
    log(pd.DataFrame(part).round(3).to_string())
    return {"tabela": t, "resumo": resumo, "partidario": pd.DataFrame(part)}
