"""Nordeste: 1º turno 2026 x 2022 (swing, comparecimento, terceiros, cenários de 2º turno).

Somente leitura dos dados do repositório. Gera os CSVs desta pasta e imprime as tabelas usadas em
nordeste_dados_1t.md.  Uso:  python "research_notes/Nordeste e cenarios economicos 2026/nordeste_dados_1t.py"

Covariáveis municipais (covariaveis_mun_ne.csv, baixadas em 05/10/2026):
  * religião: IBGE SIDRA 9537 (Censo 2022, pessoas 10+), n6 nas UFs 21-29
  * renda domiciliar per capita: IBGE SIDRA 10295 v13431 (Censo 2022) e moradores (v13604)
  * Bolsa Família: MDS MiSocial, anomes 202609 (pessoas e famílias beneficiárias)
  * de-para TSE->IBGE e capitais: github.com/betafcc/Municipios-Brasileiros-TSE
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
NE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 40)


def md(df, fmt="{:,.1f}"):
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else fmt.format(v))
    d = d.astype(str).replace("nan", "")
    idx = [" / ".join(map(str, i)) if isinstance(i, tuple) else str(i) for i in d.index]
    head = "| " + " | ".join([""] + [str(c) for c in d.columns]) + " |"
    sep = "|" + "---|" * (len(d.columns) + 1)
    body = ["| " + " | ".join([i] + list(r)) + " |" for i, r in zip(idx, d.values)]
    return "\n".join([head, sep] + body)


def wavg(x, w):
    return float(np.sum(x * w) / np.sum(w))


# ---------------------------------------------------------------- dados
m26 = pd.read_csv(ROOT / "modelo_municipal/data/mun_2026_1t.csv")
m26 = m26.rename(columns={"c55": "caiado", "c70": "cury", "c30": "zema", "c14": "renan"})
h22 = pd.read_csv(ROOT / "modelo_municipal/data/hist_2022.csv")
h18 = pd.read_csv(ROOT / "modelo_municipal/data/hist_2018.csv")
cov = pd.read_csv(OUT / "covariaveis_mun_ne.csv").rename(columns={"pct_evangélicas": "pct_evang",
                                                                  "pct_católica_apostólica_": "pct_catol"})

d = m26[m26.uf.isin(NE)].merge(
    h22.drop(columns="uf"), on="cd_municipio_tse", how="left").merge(
    h18[["cd_municipio_tse", "t1_validos", "t1_pt", "t1_opp", "t1_aptos", "t1_comparecimento"]].add_prefix("h18_")
    .rename(columns={"h18_cd_municipio_tse": "cd_municipio_tse"}), on="cd_municipio_tse", how="left").merge(
    cov[["codigo_tse", "capital", "codigo_ibge", "pct_evang", "pct_catol", "renda_pc_c2022", "moradores_c2022",
         "pbf_pessoas_set2026", "pbf_familias_set2026", "pbf_pessoas_pct_pop"]],
    left_on="cd_municipio_tse", right_on="codigo_tse", how="left")
print("municípios NE 2026:", len(d), "sem 2022:", d.t1_validos.isna().sum(), "sem cov:", d.pct_evang.isna().sum())
d = d[d.t1_validos.notna()].copy()

# métricas
d["lula26"] = 100 * d.lula / d.validos
d["flav26"] = 100 * d.flavio / d.validos
d["terc26"] = 100 * (d.validos - d.lula - d.flavio) / d.validos
d["lula22"] = 100 * d.t1_pt / d.t1_validos
d["bols22"] = 100 * d.t1_opp / d.t1_validos
d["lula22_2t"] = 100 * d.t2_pt / d.t2_validos
d["swing"] = d.lula26 - d.lula22                                  # p.p. dos válidos, 1T x 1T
d["lula26_2p"] = 100 * d.lula / (d.lula + d.flavio)
d["lula22_2p"] = 100 * d.t1_pt / (d.t1_pt + d.t1_opp)
d["swing2p"] = d.lula26_2p - d.lula22_2p                           # p.p. bipartidário
d["marg26"] = d.lula - d.flavio
d["marg22"] = d.t1_pt - d.t1_opp
d["dmarg"] = d.marg26 - d.marg22                                   # votos líquidos
d["comp26"] = 100 * d.comparecimento / d.aptos
d["comp22"] = 100 * d.t1_comparecimento / d.t1_aptos
d["dcomp"] = d.comp26 - d.comp22
d["porte"] = pd.cut(d.aptos, [0, 10e3, 20e3, 50e3, 100e3, 200e3, 1e9],
                    labels=["<10 mil", "10-20 mil", "20-50 mil", "50-100 mil", "100-200 mil", ">200 mil"])
d["tipo"] = np.where(d.capital == 1, "Capital", "Interior")
for c, lab in [("pbf_pessoas_pct_pop", "q_pbf"), ("pct_evang", "q_evang"), ("renda_pc_c2022", "q_renda")]:
    d[lab] = pd.qcut(d[c], 5, labels=["Q1 (baixo)", "Q2", "Q3", "Q4", "Q5 (alto)"])


def resumo(g):
    v26, v22 = g.validos.sum(), g.t1_validos.sum()
    return pd.Series({
        "munic": len(g),
        "validos26_mil": v26 / 1e3,
        "lula22_%": 100 * g.t1_pt.sum() / v22,
        "lula26_%": 100 * g.lula.sum() / v26,
        "swing_pp": 100 * g.lula.sum() / v26 - 100 * g.t1_pt.sum() / v22,
        "bols22_%": 100 * g.t1_opp.sum() / v22,
        "flav26_%": 100 * g.flavio.sum() / v26,
        "terc26_%": 100 * (v26 - g.lula.sum() - g.flavio.sum()) / v26,
        "swing2p_pp": 100 * g.lula.sum() / (g.lula.sum() + g.flavio.sum())
                      - 100 * g.t1_pt.sum() / (g.t1_pt.sum() + g.t1_opp.sum()),
        "dvotos_lula_mil": (g.lula.sum() - g.t1_pt.sum()) / 1e3,
        "dmargem_mil": g.dmarg.sum() / 1e3,
        "comp22_%": 100 * g.t1_comparecimento.sum() / g.t1_aptos.sum(),
        "comp26_%": 100 * g.comparecimento.sum() / g.aptos.sum(),
        "dcomp_pp": 100 * g.comparecimento.sum() / g.aptos.sum()
                    - 100 * g.t1_comparecimento.sum() / g.t1_aptos.sum(),
    })


T = {}
T["uf"] = pd.concat([d.groupby("uf").apply(resumo, include_groups=False).loc[NE],
                     resumo(d).to_frame("NE").T])
T["tipo"] = d.groupby("tipo").apply(resumo, include_groups=False)
T["porte"] = d.groupby("porte", observed=True).apply(resumo, include_groups=False)
T["pbf"] = d.groupby("q_pbf", observed=True).apply(resumo, include_groups=False)
T["evang"] = d.groupby("q_evang", observed=True).apply(resumo, include_groups=False)
T["renda"] = d.groupby("q_renda", observed=True).apply(resumo, include_groups=False)
for k, lab, col in [("pbf", "q_pbf", "pbf_pessoas_pct_pop"), ("evang", "q_evang", "pct_evang"),
                    ("renda", "q_renda", "renda_pc_c2022")]:
    T[k].insert(1, "faixa", d.groupby(lab, observed=True)[col].agg(lambda s: f"{s.min():.0f}-{s.max():.0f}"))
cap = d[d.capital == 1].groupby("uf").apply(resumo, include_groups=False).loc[NE]
inte = d[d.capital == 0].groupby("uf").apply(resumo, include_groups=False).loc[NE]
T["cap_int_uf"] = pd.DataFrame({"swing_cap": cap.swing_pp, "swing_int": inte.swing_pp,
                                "dmarg_cap_mil": cap.dmargem_mil, "dmarg_int_mil": inte.dmargem_mil,
                                "dcomp_cap": cap.dcomp_pp, "dcomp_int": inte.dcomp_pp})

for k in ["uf", "tipo", "porte", "pbf", "evang", "renda", "cap_int_uf"]:
    print(f"\n### {k}\n" + md(T[k]))

# distribuição do swing (município)
q = d.swing.quantile([.05, .1, .25, .5, .75, .9, .95])
print("\n### distribuição do swing (p.p. válidos, município)\n", q.round(2).to_dict())
print("média ponderada por válidos:", round(wavg(d.swing, d.validos), 2), "| não ponderada", round(d.swing.mean(), 2))
print("% municípios com swing<0:", round(100 * (d.swing < 0).mean(), 1),
      "| % eleitorado (válidos):", round(100 * d.validos[d.swing < 0].sum() / d.validos.sum(), 1))
bins = [-100, -15, -10, -7.5, -5, -2.5, 0, 2.5, 5, 100]
hist = pd.cut(d.swing, bins).value_counts().sort_index()
hv = d.groupby(pd.cut(d.swing, bins), observed=False).validos.sum() / 1e3
T["hist"] = pd.DataFrame({"municipios": hist, "validos26_mil": hv})
print(md(T["hist"]))
T["hist_uf"] = d.groupby("uf").swing.describe(percentiles=[.1, .5, .9]).loc[NE][["10%", "50%", "90%", "min", "max"]]
print(md(T["hist_uf"]))

# regressões (WLS por válidos), com e sem EF de UF
def wls(y, X, w):
    Xc = np.column_stack([np.ones(len(X)), X])
    W = np.sqrt(w)
    b, *_ = np.linalg.lstsq(Xc * W[:, None], y * W, rcond=None)
    res = y - Xc @ b
    # erro-padrão robusto HC1 ponderado
    XtWX_inv = np.linalg.inv((Xc * w[:, None]).T @ Xc)
    meat = (Xc * (w * res)[:, None]).T @ (Xc * (w * res)[:, None])
    n, k = Xc.shape
    V = XtWX_inv @ meat @ XtWX_inv * n / (n - k)
    r2 = 1 - np.sum(w * res ** 2) / np.sum(w * (y - np.average(y, weights=w)) ** 2)
    return b, np.sqrt(np.diag(V)), r2


r = d.dropna(subset=["pct_evang", "renda_pc_c2022", "pbf_pessoas_pct_pop"]).copy()
r["log_aptos"] = np.log(r.aptos)
r["log_renda"] = np.log(r.renda_pc_c2022)
covs = ["lula22", "pbf_pessoas_pct_pop", "pct_evang", "log_renda", "log_aptos", "capital"]
z = {c: (r[c] - r[c].mean()) / r[c].std() if c != "capital" else r[c] for c in covs}
rows = []
for nome, X in [("simples_" + c, np.column_stack([z[c]])) for c in covs] + [
        ("multipla", np.column_stack([z[c] for c in covs])),
        ("multipla_EF_UF", np.column_stack([z[c] for c in covs] + [
            (r.uf == u).astype(float) for u in NE[1:]]))]:
    b, se, r2 = wls(r.swing.values, X, r.validos.values)
    names = ([nome.replace("simples_", "")] if nome.startswith("simples") else covs)
    for i, nm in enumerate(names):
        rows.append({"modelo": nome, "variavel": nm, "coef_pp_por_dp": b[i + 1], "ep_robusto": se[i + 1], "R2": r2})
T["reg"] = pd.DataFrame(rows).set_index(["modelo", "variavel"])
print("\n### regressões (swing p.p.; coef por 1 DP; capital = dummy)\n" + md(T["reg"], "{:.2f}"))
# correlações simples (ponderadas)
def wcorr(a, b, w):
    a, b = a - np.average(a, weights=w), b - np.average(b, weights=w)
    return np.sum(w * a * b) / np.sqrt(np.sum(w * a * a) * np.sum(w * b * b))
cor = {c: wcorr(r[c].values, r.swing.values, r.validos.values) for c in covs}
cor_comp = {c: wcorr(r[c].values, r.dcomp.values, r.validos.values) for c in covs + ["swing"]}
print("corr ponderada com swing:", {k: round(v, 2) for k, v in cor.items()})
print("corr ponderada com dcomp:", {k: round(v, 2) for k, v in cor_comp.items()})
T["corr"] = pd.DataFrame({"corr_swing": cor, "corr_dcomp": {c: cor_comp[c] for c in covs}})

# maiores perdas de margem
cols = ["uf", "municipio", "aptos", "lula22", "lula26", "swing", "dmarg", "dcomp", "pct_evang", "renda_pc_c2022"]
T["top_perda"] = d.sort_values("dmarg")[cols].head(20).set_index("municipio")
T["top_ganho"] = d.sort_values("dmarg", ascending=False)[cols].head(10).set_index("municipio")
T["top_swing_neg"] = d[d.aptos > 50e3].sort_values("swing")[cols].head(15).set_index("municipio")
for k in ["top_perda", "top_ganho", "top_swing_neg"]:
    print(f"\n### {k}\n" + md(T[k]))

# ---------------------------------------------------------------- comparecimento
# correlação do comparecimento com a fatia de Lula
print("\ncorr(comp26, lula26) pond.:", round(wcorr(d.comp26.values, d.lula26.values, d.aptos.values), 3),
      "| corr(dcomp, lula22):", round(wcorr(d.dcomp.values, d.lula22.values, d.aptos.values), 3),
      "| corr(dcomp, swing):", round(wcorr(d.dcomp.values, d.swing.values, d.aptos.values), 3))
d["q_lula22"] = pd.qcut(d.lula22, 5, labels=["Q1 (Lula fraco)", "Q2", "Q3", "Q4", "Q5 (Lula forte)"])
T["comp_lula"] = d.groupby("q_lula22", observed=True).apply(resumo, include_groups=False)[
    ["munic", "lula22_%", "lula26_%", "comp22_%", "comp26_%", "dcomp_pp", "swing_pp"]]
print(md(T["comp_lula"]))
abst = d.groupby("uf").apply(lambda g: pd.Series({
    "aptos26_mil": g.aptos.sum() / 1e3, "abst26_mil": (g.aptos - g.comparecimento).sum() / 1e3,
    "brnul26_mil": (g.brancos + g.nulos).sum() / 1e3,
    "lula2p_26": 100 * g.lula.sum() / (g.lula.sum() + g.flavio.sum())}), include_groups=False).loc[NE]
abst.loc["NE"] = abst.sum()
abst.loc["NE", "lula2p_26"] = 100 * d.lula.sum() / (d.lula.sum() + d.flavio.sum())
T["abst"] = abst

# histórico 1T->2T por UF (TSE agregado)
hist = pd.read_csv(ROOT / "simulador/data/resultados_uf_2002_2022.csv")
hist = hist[hist.uf.isin(NE) & hist.ano.isin([2014, 2018, 2022])]
p = hist.pivot_table(index=["ano", "uf"], columns="turno",
                     values=["eleitorado", "comparecimento", "votos_validos", "pt_votos", "oponente_votos"])
t12 = pd.DataFrame({
    "comp1_%": 100 * p[("comparecimento", 1)] / p[("eleitorado", 1)],
    "comp2_%": 100 * p[("comparecimento", 2)] / p[("eleitorado", 2)],
    "dcomp_mil": (p[("comparecimento", 2)] - p[("comparecimento", 1)]) / 1e3,
    "dvalidos_mil": (p[("votos_validos", 2)] - p[("votos_validos", 1)]) / 1e3,
    "dmargem_pt_mil": ((p[("pt_votos", 2)] - p[("oponente_votos", 2)])
                       - (p[("pt_votos", 1)] - p[("oponente_votos", 1)])) / 1e3,
})
t12["dcomp_pp"] = t12["comp2_%"] - t12["comp1_%"]
T["t12"] = t12
ne_t12 = p.groupby(level="ano").sum()
T["t12_ne"] = pd.DataFrame({
    "comp1_%": 100 * ne_t12[("comparecimento", 1)] / ne_t12[("eleitorado", 1)],
    "comp2_%": 100 * ne_t12[("comparecimento", 2)] / ne_t12[("eleitorado", 2)],
    "dcomp_mil": (ne_t12[("comparecimento", 2)] - ne_t12[("comparecimento", 1)]) / 1e3,
    "dvalidos_mil": (ne_t12[("votos_validos", 2)] - ne_t12[("votos_validos", 1)]) / 1e3,
    "pt_1t_mil": ne_t12[("pt_votos", 1)] / 1e3, "pt_2t_mil": ne_t12[("pt_votos", 2)] / 1e3,
    "opp_1t_mil": ne_t12[("oponente_votos", 1)] / 1e3, "opp_2t_mil": ne_t12[("oponente_votos", 2)] / 1e3,
    "dmargem_pt_mil": ((ne_t12[("pt_votos", 2)] - ne_t12[("oponente_votos", 2)])
                       - (ne_t12[("pt_votos", 1)] - ne_t12[("oponente_votos", 1)])) / 1e3,
})
T["t12_ne"]["dcomp_pp"] = T["t12_ne"]["comp2_%"] - T["t12_ne"]["comp1_%"]
print(md(T["abst"]))
print(md(T["t12"].unstack(0)["dcomp_pp"]))
print(md(T["t12_ne"]))
dc = T["t12"]["dcomp_pp"].unstack(0)

# ---------------------------------------------------------------- terceiros
ter = d.groupby("uf")[["caiado", "cury", "renan", "zema", "validos", "lula", "flavio"]].sum().loc[NE]
ter["outros"] = ter.validos - ter.lula - ter.flavio - ter[["caiado", "cury", "renan", "zema"]].sum(axis=1)
ter.loc["NE"] = ter.sum()
br = m26[["caiado", "cury", "renan", "zema", "validos", "lula", "flavio"]].sum()
ter4 = ter[["caiado", "cury", "renan", "zema"]].sum(axis=1)
T["terc"] = pd.DataFrame({
    "caiado_mil": ter.caiado / 1e3, "cury_mil": ter.cury / 1e3, "renan_mil": ter.renan / 1e3,
    "zema_mil": ter.zema / 1e3, "outros_mil": ter.outros / 1e3, "4_terc_mil": ter4 / 1e3,
    "4_terc_%val": 100 * ter4 / ter.validos,
    "caiado_%": 100 * ter.caiado / ter.validos, "cury_%": 100 * ter.cury / ter.validos,
    "renan_%": 100 * ter.renan / ter.validos, "zema_%": 100 * ter.zema / ter.validos})
T["terc_br"] = pd.DataFrame({"NE_mil": ter.loc["NE", ["caiado", "cury", "renan", "zema"]] / 1e3,
                             "BR_mil": br[["caiado", "cury", "renan", "zema"]] / 1e3})
T["terc_br"]["NE_%_do_BR"] = 100 * T["terc_br"].NE_mil / T["terc_br"].BR_mil
print(md(T["terc"]))
print(md(T["terc_br"]))
d["t4"] = d[["caiado", "cury", "renan", "zema"]].sum(axis=1)
tg = lambda g: pd.Series({"4_terc_mil": g.t4.sum() / 1e3, "4_terc_%": 100 * g.t4.sum() / g.validos.sum(),
                          "cury_%": 100 * g.cury.sum() / g.validos.sum(),
                          "renan_%": 100 * g.renan.sum() / g.validos.sum(),
                          "caiado_%": 100 * g.caiado.sum() / g.validos.sum()})
T["terc_tipo"] = d.groupby("tipo").apply(tg, include_groups=False)
T["terc_porte"] = d.groupby("porte", observed=True).apply(tg, include_groups=False)
T["terc_renda"] = d.groupby("q_renda", observed=True).apply(tg, include_groups=False)
T["terc_evang"] = d.groupby("q_evang", observed=True).apply(tg, include_groups=False)
T["terc_top"] = d.sort_values("t4", ascending=False)[["uf", "municipio", "validos", "t4", "cury", "renan",
                                                      "caiado", "zema"]].head(15).set_index("municipio")
T["terc_top"]["t4_%"] = 100 * T["terc_top"].t4 / T["terc_top"].validos
for k in ["terc_tipo", "terc_porte", "terc_renda", "terc_evang", "terc_top"]:
    print(f"\n### {k}\n" + md(T[k]))
print("capitais concentram % dos 4 terceiros NE:", round(100 * d.t4[d.capital == 1].sum() / d.t4.sum(), 1),
      "vs % dos válidos:", round(100 * d.validos[d.capital == 1].sum() / d.validos.sum(), 1))

# ---------------------------------------------------------------- cenários
# transferências (Lula / Flávio / fora) por candidato
TR = {
    "Quaest nacional": {"caiado": (19, 43), "renan": (11, 60), "cury": (28, 35), "zema": (10, 80), "outros": (30, 30)},
    "NE pró-Lula (+10 p.p. Lula/-10 Flávio)": {"caiado": (29, 33), "renan": (21, 50), "cury": (38, 25),
                                               "zema": (20, 70), "outros": (40, 20)},
    "NE pró-Flávio (2022 NE 'Outros/Tebet')": {"caiado": (10, 70), "renan": (8, 70), "cury": (15, 60),
                                                "zema": (5, 80), "outros": (10, 60)},
}
ne_ter = ter.loc["NE"]
transf = {}
for k, tr in TR.items():
    transf[k] = sum(ne_ter[c] * (tr[c][0] - tr[c][1]) / 100 for c in tr) / 1e3
print("\ntransferência líquida NE (mil, Lula - Flávio):", {k: round(v) for k, v in transf.items()})
# comparecimento: votos adicionais no 2T x margem líquida dos novos votantes
apt_ne, comp_ne = d.aptos.sum(), d.comparecimento.sum()
lula2p = d.lula.sum() / (d.lula.sum() + d.flavio.sum())
# margem por votante novo: se vierem com o perfil de cada UF (2p) ponderado
uf_2p = d.groupby("uf").apply(lambda g: g.lula.sum() / (g.lula.sum() + g.flavio.sum()), include_groups=False)
uf_apt = d.groupby("uf").aptos.sum()
val_rate = d.validos.sum() / d.comparecimento.sum()
def turnout_net(pp_by_uf, extra_lean=0.0):
    tot = 0
    for u in NE:
        novos = uf_apt[u] * pp_by_uf.get(u, 0) / 100 * val_rate
        tot += novos * (2 * min(uf_2p[u] + extra_lean, 1) - 1)
    return tot / 1e3, sum(uf_apt[u] * pp_by_uf.get(u, 0) / 100 for u in NE) / 1e3
sc_t = {
    "repete 2022 (NE +0,2 p.p.)": dc[2022].to_dict(),
    "repete 2018 (NE -1,1 p.p.)": dc[2018].to_dict(),
    "repete 2014 (NE -1,6 p.p.)": dc[2014].to_dict(),
    "estável (0)": {u: 0 for u in NE},
    "+1 p.p.": {u: 1 for u in NE},
    "+2 p.p.": {u: 2 for u in NE},
    "+3 p.p. (mobilização forte)": {u: 3 for u in NE},
}
tn = {k: turnout_net(v) for k, v in sc_t.items()}
tn_lean = {k: turnout_net(v, 0.10) for k, v in sc_t.items()}
T["sc_turnout"] = pd.DataFrame({"novos_votantes_mil": {k: v[1] for k, v in tn.items()},
                                "margem_liq_mil_perfil_UF": {k: v[0] for k, v in tn.items()},
                                "margem_liq_mil_perfil_UF+10pp": {k: v[0] for k, v in tn_lean.items()}})
print(md(T["sc_turnout"]))
# brancos e nulos: redução
bn = (d.brancos + d.nulos).sum()
T["bn"] = bn
print("brancos+nulos NE 1T 2026 (mil):", round(bn / 1e3), "| % comp:", round(100 * bn / comp_ne, 2))

GAP = (m26.flavio.sum() - m26.lula.sum()) / 1e3
T["gap"] = GAP
cen = []
def add(nome, tr, tu, bnred=0.0, bnlean=0.0):
    tnet = transf[tr]
    unet = tn_lean[tu][0] if "+10" in nome else tn[tu][0]
    bnet = bn * bnred * (2 * min(lula2p + bnlean, 1) - 1) / 1e3
    tot = tnet + unet + bnet
    cen.append({"cenario": nome, "transferencia_mil": tnet, "comparecimento_mil": unet, "brancos_nulos_mil": bnet,
                "total_NE_mil": tot, "%_do_gap": 100 * tot / GAP})
add("A. Pessimista: transf. pró-Flávio, comparecimento cai como 2018", "NE pró-Flávio (2022 NE 'Outros/Tebet')",
    "repete 2018 (NE -1,1 p.p.)")
add("A2. Histórico 2022: transf. Quaest, comparecimento como 2022", "Quaest nacional", "repete 2022 (NE +0,2 p.p.)")
add("B. Base: transf. Quaest, comparecimento estável", "Quaest nacional", "estável (0)")
add("C. Base + 1 p.p. comparecimento, -10% brancos/nulos", "Quaest nacional", "+1 p.p.", 0.10)
add("D. Otimista: transf. pró-Lula, +2 p.p. comparecimento, -15% B/N", "NE pró-Lula (+10 p.p. Lula/-10 Flávio)",
    "+2 p.p.", 0.15)
add("E. Teto: transf. pró-Lula, +3 p.p., novos +10 p.p. pró-Lula (+10), -20% B/N",
    "NE pró-Lula (+10 p.p. Lula/-10 Flávio)", "+3 p.p. (mobilização forte)", 0.20, 0.10)
T["cen"] = pd.DataFrame(cen).set_index("cenario")
print("\nGAP nacional (mil):", round(GAP))
print(md(T["cen"]))

# 2022 e 2018: quanto o PT ganhou de margem líquida no NE entre 1T e 2T (municipal)
for ano, h in [(2018, h18), (2022, h22)]:
    hh = h[h.uf.isin(NE)]
    dm = ((hh.t2_pt - hh.t2_opp) - (hh.t1_pt - hh.t1_opp)).sum() / 1e3
    dmb = ((h.t2_pt - h.t2_opp) - (h.t1_pt - h.t1_opp)).sum() / 1e3
    print(f"{ano}: Δmargem PT 1T->2T NE {dm:,.0f} mil; Brasil {dmb:,.0f} mil")

# contexto: NE no total nacional
nat = m26.merge(h22[["cd_municipio_tse", "t1_pt", "t1_opp", "t1_aptos", "t1_comparecimento", "t1_validos"]],
                on="cd_municipio_tse", how="left")
dm_br = (m26.lula.sum() - m26.flavio.sum()) - (h22.t1_pt.sum() - h22.t1_opp.sum())
print("\nΔmargem Lula 1T 2022->2026 Brasil (mil):", round(dm_br / 1e3), "| NE:", round(d.dmarg.sum() / 1e3),
      "| NE % da perda:", round(100 * d.dmarg.sum() / dm_br, 1))
print("swing BR (p.p. válidos):", round(100 * m26.lula.sum() / m26.validos.sum() - 100 * h22.t1_pt.sum() / h22.t1_validos.sum(), 2),
      "| comp BR 22->26:", round(100 * h22.t1_comparecimento.sum() / h22.t1_aptos.sum(), 2),
      round(100 * m26.comparecimento.sum() / m26.aptos.sum(), 2))
print("NE aptos 22->26 (mil):", round(d.t1_aptos.sum() / 1e3), round(d.aptos.sum() / 1e3),
      "| comparec.:", round(d.t1_comparecimento.sum() / 1e3), round(d.comparecimento.sum() / 1e3),
      "| válidos:", round(d.t1_validos.sum() / 1e3), round(d.validos.sum() / 1e3))
print("NE Lula 22->26 (mil):", round(d.t1_pt.sum() / 1e3), round(d.lula.sum() / 1e3),
      "| Bolsonaro->Flávio:", round(d.t1_opp.sum() / 1e3), round(d.flavio.sum() / 1e3),
      "| terceiros:", round((d.t1_validos - d.t1_pt - d.t1_opp).sum() / 1e3), round((d.validos - d.lula - d.flavio).sum() / 1e3))
print("NE % do eleitorado BR:", round(100 * d.aptos.sum() / m26.aptos.sum(), 1),
      "| NE % dos 4 terceiros BR:", round(100 * d.t4.sum() / m26[["caiado", "cury", "renan", "zema"]].sum().sum(), 1))
# aptos: variação por porte (indício de revisão cadastral)
print((d.groupby("porte", observed=True).apply(lambda g: 100 * (g.aptos.sum() / g.t1_aptos.sum() - 1), include_groups=False)).round(2).to_dict())

# ---------------------------------------------------------------- CSVs
mun_cols = ["cd_municipio_tse", "codigo_ibge", "uf", "municipio", "tipo", "porte", "aptos", "validos", "lula22",
            "lula26", "swing", "lula22_2p", "lula26_2p", "swing2p", "dmarg", "comp22", "comp26", "dcomp",
            "caiado", "cury", "renan", "zema", "pct_evang", "renda_pc_c2022", "pbf_pessoas_pct_pop"]
d[mun_cols].round(3).to_csv(OUT / "nordeste_swing_municipios.csv", index=False)
pd.concat({k: T[k] for k in ["uf", "tipo", "porte", "pbf", "evang", "renda"]}, names=["corte", "grupo"]) \
    .round(3).to_csv(OUT / "nordeste_swing_cortes.csv")
T["terc"].round(2).to_csv(OUT / "nordeste_terceiros_uf.csv")
T["t12"].round(3).to_csv(OUT / "nordeste_comparecimento_1t2t_hist.csv")
T["cen"].round(1).to_csv(OUT / "nordeste_cenarios_2t.csv")
T["reg"].round(3).to_csv(OUT / "nordeste_regressoes_swing.csv")
