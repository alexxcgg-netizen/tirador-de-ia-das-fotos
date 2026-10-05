"""Erro sistemático da projeção "1º turno real -> 2º turno": qual especificação os dados de 2002-2022 sustentam.

A projeção do 2º turno parte do 1º turno real por UF e transfere os votos dos eliminados com uma linha
[PT, adversário, fora] (a implícita nas pesquisas pareadas da véspera quando existe: 2018 e 2022; senão a linha
genérica [0,35; 0,35; 0,30]) e mistura, com peso 0,25, a média das pesquisas de 2º turno feitas antes do 1º turno
(corrigidas por instituto; só 2018 e 2022 têm). O erro dessa projeção (previsto − real, p.p. da fatia do PT nos
válidos) foi, de 2002 a 2022: +1,5, −7,2, +1,6, +2,7, −0,6, +2,2.

Quatro especificações para o termo sistemático, comparadas por validação deixando uma eleição de fora (LOEO):

  (a) viés com sinal do PT: erro = b_PT + ruído (o PT é superestimado/subestimado em toda eleição);
  (b) viés com sinal do líder do 1º turno: erro_PT = s · b_L + ruído, s = +1 se o PT liderou o 1º turno, −1 se não
      (o líder é superestimado); em 2026 o líder é Flávio, então o termo favorece Lula;
  (c) sem viés de sinal, mas a fatia "decidida" que vai ao PT depende da ideologia do terceiro: p_esq para os
      terceiros de esquerda/centro-esquerda, p_nesq para os demais (TERCEIROS, com fonte); a participação (1 − fora)
      continua a da linha da véspera;
  (d) viés zero.

Os viéses de (a) e (b) são encolhidos para zero (empírico-bayesiano, prior N(0, tau0²), como no simulador).
(c) estima p_esq e p_nesq por mínimos quadrados no erro nacional das eleições de treino (prior fraco em logito).
Métricas: RMSE e MAE nacional fora da amostra, cobertura dos intervalos de 80% e 95% (t de Student, 5 g.l., dp
preditivo com o mesmo prior qui-quadrado inverso do simulador) e log-verossimilhança preditiva média.
Regra de escolha (fixada antes de rodar): menor RMSE LOEO; se a diferença para a especificação mais simples (zero)
for menor que EMPATE_PP, fica a mais simples e a incerteza é alargada (as outras viram sensibilidade).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

import modelo as M

ANOS = (2002, 2006, 2010, 2014, 2018, 2022)
ESPECIFICACOES = ("pt", "lider", "ideologia", "zero")
NOMES = {"pt": "(a) viés com sinal do PT", "lider": "(b) viés com sinal do líder do 1º turno",
         "ideologia": "(c) transferência por ideologia dos terceiros (esquerda x não-esquerda), sem viés de sinal",
         "zero": "(d) viés zero"}
EMPATE_PP = 0.25            # diferença de RMSE LOEO abaixo da qual as especificações são tratadas como empatadas
PRIOR_LOGITO_DP = 1.0       # prior fraco de logito(p) por bloco em (c): N(0, 1²)
ESCALA_PRIOR_PP = 2.0       # escala (p.p.) que converte o prior em resíduo comparável aos erros nacionais

# Terceiros colocados (1º turno, % dos válidos, TSE) e classificação ideológica. Regra fixa, por família partidária:
# 'esquerda' = partidos de esquerda/centro-esquerda (PSB, PPS-2002, PDT, PSOL, PSTU, PCB, PCO, UP, PV, Rede, PPL);
# 'nao_esquerda' = todos os demais (centro, centro-direita, direita). Mesma regra do modelo_municipal/ para 2018/2022.
# coluna: onde o candidato está em data/resultados_uf_2002_2022.csv (terceiro1, terceiro2 ou dentro de 'outros',
# que é repartido entre os blocos pela proporção nacional desta tabela em todas as UFs).
_F = "TSE, resultado oficial do 1º turno (dados abertos, votacao_candidato_munzona_{ano}); classificação: {c}"
TERCEIROS = [
    # 2002
    (2002, "Anthony Garotinho", "PSB", 17.87, "esquerda", "terceiro1", "centro-esquerda; apoiou Lula no 2º turno"),
    (2002, "Ciro Gomes", "PPS", 11.97, "esquerda", "terceiro2", "centro-esquerda; apoiou Lula no 2º turno"),
    (2002, "Zé Maria", "PSTU", 0.47, "esquerda", "outros", "esquerda"),
    (2002, "Rui Costa Pimenta", "PCO", 0.04, "esquerda", "outros", "esquerda"),
    # 2006
    (2006, "Heloísa Helena", "PSOL", 6.85, "esquerda", "terceiro1", "esquerda; neutra no 2º turno (PSOL: voto nulo)"),
    (2006, "Cristovam Buarque", "PDT", 2.64, "esquerda", "terceiro2", "centro-esquerda; neutro no 2º turno"),
    (2006, "Ana Maria Rangel", "PRP", 0.13, "nao_esquerda", "outros", "centro-direita"),
    (2006, "José Maria Eymael", "PSDC", 0.07, "nao_esquerda", "outros", "centro-direita"),
    (2006, "Luciano Bivar", "PSL", 0.06, "nao_esquerda", "outros", "direita"),
    # 2010
    (2010, "Marina Silva", "PV", 19.33, "esquerda", "terceiro1", "centro-esquerda; neutra no 2º turno"),
    (2010, "Plínio de Arruda Sampaio", "PSOL", 0.87, "esquerda", "terceiro2", "esquerda"),
    (2010, "José Maria Eymael", "PSDC", 0.09, "nao_esquerda", "outros", "centro-direita"),
    (2010, "Zé Maria", "PSTU", 0.08, "esquerda", "outros", "esquerda"),
    (2010, "Levy Fidelix", "PRTB", 0.06, "nao_esquerda", "outros", "direita"),
    (2010, "Ivan Pinheiro", "PCB", 0.04, "esquerda", "outros", "esquerda"),
    (2010, "Rui Costa Pimenta", "PCO", 0.01, "esquerda", "outros", "esquerda"),
    # 2014
    (2014, "Marina Silva", "PSB", 21.32, "esquerda", "terceiro1",
     "centro-esquerda pela regra do partido; apoiou Aécio no 2º turno (ver sensibilidade marina_2014)"),
    (2014, "Luciana Genro", "PSOL", 1.55, "esquerda", "terceiro2", "esquerda"),
    (2014, "Pastor Everaldo", "PSC", 0.75, "nao_esquerda", "outros", "direita"),
    (2014, "Eduardo Jorge", "PV", 0.61, "esquerda", "outros", "centro-esquerda"),
    (2014, "Levy Fidelix", "PRTB", 0.43, "nao_esquerda", "outros", "direita"),
    (2014, "Zé Maria", "PSTU", 0.09, "esquerda", "outros", "esquerda"),
    (2014, "José Maria Eymael", "PSDC", 0.06, "nao_esquerda", "outros", "centro-direita"),
    (2014, "Mauro Iasi", "PCB", 0.05, "esquerda", "outros", "esquerda"),
    (2014, "Rui Costa Pimenta", "PCO", 0.01, "esquerda", "outros", "esquerda"),
    # 2018
    (2018, "Ciro Gomes", "PDT", 12.47, "esquerda", "terceiro1", "centro-esquerda; 'apoio crítico' do PDT a Haddad"),
    (2018, "Geraldo Alckmin", "PSDB", 4.76, "nao_esquerda", "terceiro2", "centro-direita; neutro"),
    (2018, "João Amoêdo", "Novo", 2.50, "nao_esquerda", "outros", "direita"),
    (2018, "Cabo Daciolo", "Patriota", 1.26, "nao_esquerda", "outros", "direita"),
    (2018, "Henrique Meirelles", "MDB", 1.20, "nao_esquerda", "outros", "centro"),
    (2018, "Marina Silva", "Rede", 1.00, "esquerda", "outros", "centro-esquerda"),
    (2018, "Alvaro Dias", "Podemos", 0.80, "nao_esquerda", "outros", "centro-direita"),
    (2018, "Guilherme Boulos", "PSOL", 0.58, "esquerda", "outros", "esquerda"),
    (2018, "Vera Lúcia", "PSTU", 0.05, "esquerda", "outros", "esquerda"),
    (2018, "José Maria Eymael", "DC", 0.04, "nao_esquerda", "outros", "centro-direita"),
    (2018, "João Goulart Filho", "PPL", 0.03, "esquerda", "outros", "esquerda"),
    # 2022
    (2022, "Simone Tebet", "MDB", 4.16, "nao_esquerda", "terceiro1", "centro; apoiou Lula no 2º turno"),
    (2022, "Ciro Gomes", "PDT", 3.04, "esquerda", "terceiro2", "centro-esquerda; PDT apoiou Lula no 2º turno"),
    (2022, "Soraya Thronicke", "União", 0.51, "nao_esquerda", "outros", "centro-direita"),
    (2022, "Felipe d'Avila", "Novo", 0.47, "nao_esquerda", "outros", "direita"),
    (2022, "Padre Kelmon", "PTB", 0.07, "nao_esquerda", "outros", "direita"),
    (2022, "Léo Péricles", "UP", 0.05, "esquerda", "outros", "esquerda"),
    (2022, "Sofia Manzano", "PCB", 0.04, "esquerda", "outros", "esquerda"),
    (2022, "Vera Lúcia", "PSTU", 0.01, "esquerda", "outros", "esquerda"),
    (2022, "José Maria Eymael", "DC", 0.01, "nao_esquerda", "outros", "centro-direita"),
]
# 2026: todos os eliminados relevantes são de não-esquerda; em 'Outros' (0,22%), 0,17 p.p. são PSTU, PCB, PCO e UP
# (modelo_municipal/README.md, contagem por número de urna).
BLOCO_2026 = {"Caiado": "nao_esquerda", "Cury": "nao_esquerda", "Zema": "nao_esquerda", "Renan": "nao_esquerda"}
OUTROS_2026_FRAC_ESQUERDA = 0.17 / 0.218


def tabela_terceiros(marina_2014: str = "esquerda") -> pd.DataFrame:
    t = pd.DataFrame(TERCEIROS, columns=["ano", "candidato", "partido", "pct_validos_1t", "bloco", "coluna", "rotulo"])
    if marina_2014 != "esquerda":
        t.loc[(t.ano == 2014) & (t.candidato == "Marina Silva"), "bloco"] = marina_2014
    t["fonte"] = [_F.format(ano=a, c="regra por família partidária (docstring)") for a in t.ano]
    return t


def fatias_blocos(ano: int, d: dict, marina_2014: str = "esquerda") -> tuple[np.ndarray, np.ndarray]:
    """(T_esq, T_nesq) por UF (frações dos válidos), na ordem de d['ufs']; somam d['T']."""
    import resultado_1t as R
    t = tabela_terceiros(marina_2014)
    t = t[t.ano == ano]
    h = R._hist()
    r1 = h[(h.ano == ano) & (h.turno == 1)].drop_duplicates("uf").set_index("uf").loc[d["ufs"]]
    te = np.zeros(len(d["ufs"])); tn = np.zeros(len(d["ufs"]))
    for col in ("terceiro1", "terceiro2"):
        x = t[t.coluna == col]
        v = r1[f"{col}_pct_validos"].fillna(0).values / 100
        if len(x) and x.bloco.iloc[0] == "esquerda":
            te += v
        else:
            tn += v
    o = t[t.coluna == "outros"]
    fe = float(o[o.bloco == "esquerda"].pct_validos_1t.sum() / o.pct_validos_1t.sum()) if len(o) else 0.0
    resto = np.clip(d["T"] - te - tn, 0, None)
    return te + fe * resto, tn + (1 - fe) * resto


_BASES = {}


def base_ano(ano: int, marina_2014: str = "esquerda", P: dict | None = None) -> dict:
    """O que a projeção de `ano` usa: 1º/2º turno reais por UF, linha da véspera, pesquisas pré-1T (corrigidas)."""
    chave = (ano, marina_2014)
    if chave in _BASES:
        return _BASES[chave]
    import resultado_1t as R
    d = R.historico_ano(ano)
    if ano >= 2014:
        pre = R.preditores_hist(ano, P, R.PARAM_2T["correcao_institutos_pre_1t"]["valor"])
    else:
        pre = {"linha": list(R.LINHA_GENERICA), "q_pesquisas": None}
    te, tn = fatias_blocos(ano, d, marina_2014)
    V = d["V1"]
    out = {"ano": ano, "d": d, "linha": [float(x) for x in pre["linha"]], "q_pesquisas": pre["q_pesquisas"],
           "TE": te, "TN": tn, "lider_pt": bool(np.sum(V * d["L"]) > np.sum(V * d["F"])),
           "real_pp": 100 * float(d["q_br"]),
           "t_esq_pp": 100 * float(np.sum(V * te) / V.sum()), "t_nesq_pp": 100 * float(np.sum(V * tn) / V.sum())}
    _BASES[chave] = out
    return out


def projecao(b: dict, p_blocos: tuple[float, float] | None = None, w_pre: float | None = None) -> float:
    """Fatia nacional do PT (fração) projetada: transferência por UF (votos agregados) + pesquisas pré-1T (peso w).
    p_blocos = (p_esq, p_nesq): fatia decidida ao PT por bloco, com a participação da linha da véspera."""
    import resultado_1t as R
    w_pre = R.PARAM_2T["peso_pesquisas_pre_1t"]["valor"] if w_pre is None else w_pre
    d, r = b["d"], b["linha"]
    V, L, F = d["V1"], d["L"], d["F"]
    part = r[0] + r[1]
    if p_blocos is None:
        num = L + d["T"] * r[0]
    else:
        num = L + part * (b["TE"] * p_blocos[0] + b["TN"] * p_blocos[1])
    den = L + F + d["T"] * part
    qt = float(np.sum(V * num) / np.sum(V * den))
    if b["q_pesquisas"] is None:
        return qt
    return float(M.expit(w_pre * M.logit(b["q_pesquisas"]) + (1 - w_pre) * M.logit(qt)))


def ajustar_blocos(bases: list) -> tuple[float, float]:
    """(p_esq, p_nesq) que minimizam o erro nacional nas eleições `bases` (prior fraco N(0, 1²) em logito)."""
    from scipy.optimize import least_squares

    def res(th):
        p = M.expit(np.asarray(th))
        e = [100 * (projecao(b, (p[0], p[1])) - b["d"]["q_br"]) for b in bases]
        return np.r_[e, ESCALA_PRIOR_PP * np.asarray(th) / PRIOR_LOGITO_DP]
    r = least_squares(res, [0.0, 0.0])
    p = M.expit(r.x)
    return float(p[0]), float(p[1])


def dp_preditivo(residuos, k: int = 0) -> float:
    """dp nacional com o prior do simulador: sqrt((nu0 s0² + soma r²) / (nu0 + n − k)), com piso."""
    import resultado_1t as R
    s0, nu0 = R.PARAM_2T["dp_nacional_prior_pp"]["valor"], R.PARAM_2T["gl_prior_dp"]["valor"]
    piso = R.PARAM_2T["dp_nacional_piso_pp"]["valor"]
    r = np.asarray(residuos, float)
    return max(math.sqrt((nu0 * s0 ** 2 + float(np.sum(r ** 2))) / max(nu0 + len(r) - k, 1)), piso)


def ajustar(espec: str, bases: list) -> dict:
    """Parâmetros da especificação com as eleições `bases`: viés (sinal PT), dp do viés, dp residual, p por bloco."""
    import resultado_1t as R
    tau0 = R.PARAM_2T["tau0_vies_pp"]["valor"]
    e = np.array([100 * (projecao(b) - b["d"]["q_br"]) for b in bases])
    s = np.array([1.0 if (espec == "pt" or b["lider_pt"]) else -1.0 for b in bases])
    if espec in ("pt", "lider"):
        y = s * e                                                    # erro no sinal da especificação
        sd0 = dp_preditivo(y - y.mean(), 1)
        v, vdp = M.eb_vies(list(y), sd0, tau0)
        sd = dp_preditivo(y - v)
        return {"espec": espec, "vies_pp": float(v), "vies_dp_pp": float(vdp), "dp_residual_pp": sd,
                "erros_pp": e.tolist(), "anos": [b["ano"] for b in bases]}
    if espec == "ideologia":
        p = ajustar_blocos(bases)
        r = np.array([100 * (projecao(b, p) - b["d"]["q_br"]) for b in bases])
        return {"espec": espec, "vies_pp": 0.0, "vies_dp_pp": 0.0, "p_esq": p[0], "p_nesq": p[1],
                "dp_residual_pp": dp_preditivo(r, 2), "erros_pp": r.tolist(), "anos": [b["ano"] for b in bases]}
    return {"espec": "zero", "vies_pp": 0.0, "vies_dp_pp": 0.0, "dp_residual_pp": dp_preditivo(e),
            "erros_pp": e.tolist(), "anos": [b["ano"] for b in bases]}


def prever(espec: str, par: dict, b: dict) -> tuple[float, float]:
    """(centro p.p. da fatia do PT, dp preditivo p.p.) da eleição b com os parâmetros `par`."""
    if espec == "ideologia":
        q = 100 * projecao(b, (par["p_esq"], par["p_nesq"]))
    else:
        s = 1.0 if (espec == "pt" or b["lider_pt"]) else -1.0
        q = 100 * projecao(b) - (s * par["vies_pp"] if espec in ("pt", "lider") else 0.0)
    return q, math.sqrt(par["dp_residual_pp"] ** 2 + par["vies_dp_pp"] ** 2)


def _t_quantil(p: float, gl: int) -> float:
    from scipy import stats
    return float(stats.t.ppf(p, gl) * math.sqrt((gl - 2) / gl))     # t de variância 1, como M.t_unit


def _t_logpdf(x: float, sd: float, gl: int) -> float:
    from scipy import stats
    esc = sd * math.sqrt((gl - 2) / gl)
    return float(stats.t.logpdf(x / esc, gl) - math.log(esc))


def backtest(anos=ANOS, marina_2014: str = "esquerda", P: dict | None = None) -> dict:
    """LOEO das quatro especificações. Devolve tabela por ano e resumo por especificação."""
    import resultado_1t as R
    gl = R.PARAM_2T["gl_t"]["valor"]
    z80, z95 = _t_quantil(0.9, gl), _t_quantil(0.975, gl)
    bases = {a: base_ano(a, marina_2014, P) for a in anos}
    linhas = []
    for espec in ESPECIFICACOES:
        for a in anos:
            par = ajustar(espec, [bases[x] for x in anos if x != a])
            q, sd = prever(espec, par, bases[a])
            e = q - bases[a]["real_pp"]
            linhas.append({"espec": espec, "ano": a, "previsto_pp": round(q, 3), "real_pp": round(bases[a]["real_pp"], 3),
                           "erro_pp": round(e, 3), "dp_pred_pp": round(sd, 3), "em_80": bool(abs(e) <= z80 * sd),
                           "em_95": bool(abs(e) <= z95 * sd), "logdens": round(_t_logpdf(e, sd, gl), 4),
                           "vies_treino_pp": round(par["vies_pp"], 3),
                           "p_esq": round(par.get("p_esq", float("nan")), 3), "p_nesq": round(par.get("p_nesq", float("nan")), 3)})
    t = pd.DataFrame(linhas)
    resumo = {}
    for espec, g in t.groupby("espec", sort=False):
        completo = ajustar(espec, list(bases.values()))
        resumo[espec] = {"nome": NOMES[espec], "rmse_pp": round(float(np.sqrt(np.mean(g.erro_pp ** 2))), 3),
                         "mae_pp": round(float(np.mean(np.abs(g.erro_pp))), 3),
                         "erro_medio_pp": round(float(g.erro_pp.mean()), 3),
                         "cobertura_80": round(float(g.em_80.mean()), 3), "cobertura_95": round(float(g.em_95.mean()), 3),
                         "logdens_media": round(float(g.logdens.mean()), 4),
                         "erros_loeo_pp": dict(zip(g.ano.astype(int), g.erro_pp)),
                         "parametros_todas": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in completo.items()
                                              if k != "erros_pp"},
                         "erros_ajustados_todas_pp": [round(x, 3) for x in completo["erros_pp"]]}
    return {"anos": list(anos), "marina_2014": marina_2014, "tabela": t, "resumo": resumo,
            "escolha": escolher(resumo),
            "terceiros_pp": {a: {"esquerda": round(bases[a]["t_esq_pp"], 2), "nao_esquerda": round(bases[a]["t_nesq_pp"], 2),
                                 "pt_liderou_1t": bases[a]["lider_pt"]} for a in anos}}


def escolher(resumo: dict) -> dict:
    """Menor RMSE LOEO; empate (< EMPATE_PP da mais simples, 'zero') -> 'zero' com incerteza alargada."""
    melhor = min(resumo, key=lambda k: resumo[k]["rmse_pp"])
    dz = resumo["zero"]["rmse_pp"] - resumo[melhor]["rmse_pp"]
    if melhor == "zero" or dz < EMPATE_PP:
        return {"espec": "zero", "empate": melhor != "zero", "melhor_rmse": melhor, "dif_para_zero_pp": round(dz, 3),
                "motivo": ("viés zero tem o menor RMSE fora da amostra" if melhor == "zero" else
                           f"'{melhor}' melhora o RMSE em só {dz:.2f} p.p. (< {EMPATE_PP}): empate -> a mais simples "
                           "(viés zero), com a incerteza alargada pela dispersão entre especificações")}
    return {"espec": melhor, "empate": False, "melhor_rmse": melhor, "dif_para_zero_pp": round(dz, 3),
            "motivo": f"menor RMSE fora da amostra ({resumo[melhor]['rmse_pp']:.2f} contra "
                      f"{resumo['zero']['rmse_pp']:.2f} p.p. do viés zero)"}


# ============================================================ κ (1º turno -> 2º turno) fora da amostra
def backtest_kappa(erros_2t: dict, e1: dict, sigma: float, tau0: float = 2.0, dp_kappa: float = 0.5) -> dict:
    """LOEO de erro_2T = b + κ (e1 − média e1) contra erro_2T = b (EB), nos anos com e1 (2014, 2018, 2022)."""
    import vies_institutos as VI
    anos = sorted(a for a in erros_2t if a in e1)
    out = []
    for a in anos:
        tr = [x for x in anos if x != a]
        y = np.array([erros_2t[x] for x in tr]); x1 = np.array([e1[x] for x in tr])
        ref = float(np.mean(x1))
        bk, _ = VI.regressao_bayes(y, np.column_stack([np.ones(len(tr)), x1 - ref]), sigma, [tau0, dp_kappa])
        b0, _ = M.eb_vies(list(y), sigma, tau0)
        out.append({"ano": a, "erro_real_pp": round(erros_2t[a], 3),
                    "pred_com_kappa_pp": round(float(bk[0] + bk[1] * (e1[a] - ref)), 3), "kappa_treino": round(float(bk[1]), 3),
                    "pred_sem_kappa_pp": round(float(b0), 3)})
    t = pd.DataFrame(out)
    return {"tabela": t.to_dict(orient="records"),
            "rmse_com_kappa_pp": round(float(np.sqrt(np.mean((t.pred_com_kappa_pp - t.erro_real_pp) ** 2))), 3),
            "rmse_sem_kappa_pp": round(float(np.sqrt(np.mean((t.pred_sem_kappa_pp - t.erro_real_pp) ** 2))), 3),
            "rmse_zero_pp": round(float(np.sqrt(np.mean(t.erro_real_pp ** 2))), 3)}
