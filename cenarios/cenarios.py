"""Cenários 2027–2034, versão 2: poder de compra real das famílias sob cada vencedor do 2º turno
de 2026 (Lula x Flávio Bolsonaro). Monte Carlo anual, vetorizado (numpy).

O que mudou em relação à v1 (ver revisao_cetica_cenarios_v1.md)
---------------------------------------------------------------
* Regime de credibilidade em cadeia de Markov de 3 estados (crível / meio-termo / crise), com
  prior explícito por candidato e transição comum; a crise fica mais provável quando a dívida passa
  do consenso (realimentação fiscal ligada). Câmbio e prêmio dependem do regime, não do nome.
* Selic por regra de Taylor + prêmio (sem Selic sorteada por candidato); prêmio precifica o desvio
  da dívida em relação ao consenso (IFI); dívida com r − g.
* 11 setores de preço com repasse do mínimo (elasticidades por setor), câmbio, Selic, hiato,
  tributos, combustíveis represados e 6x1.
* Salário mínimo em equilíbrio geral: efeito direto, repasse a preços, farol (informais),
  cascata e achatamento, emprego (Kaitz regional) e custo fiscal. Regra com defasagem correta
  (PIB de t−2) e faixa 0,6–2,5% até 2030.
* Bloco fiscal: ajuste anunciado entregue conforme o regime, composição sorteada (topo, gasto
  tributário, discricionária, obrigatória), fechamento (corte acima do cortável força a quebra da
  regra do mínimo, para qualquer vencedor), promessas sem fonte com probabilidade de execução e
  financiamento (dívida ou cortes), multiplicadores por instrumento, incidência por família.
* Bolsa Família sem indexação automática: reajuste é um evento de Bernoulli com o mesmo prior.
* 10 famílias-tipo com cesta POF própria, dívida por linha de crédito, ativos financeiros,
  IR/INSS (tabelas corrigidas ou não por evento), risco de desemprego binário.
* Horizonte até 2034: o mandato (2027–2030) e os quatro anos seguintes, com regra comum de ajuste
  forçado quando a dívida passa do limiar, para mostrar o que é ganho que se sustenta e o que é
  ganho antecipado que se reverte.
* Camada "medido × vivido" (medido_vs_vivido.md), aplicada igualmente aos dois.

Neutralidade
------------
Uma única função `simular` para os dois vencedores. O programa entra só como dicionário (mesmas
chaves). Os sorteios de política usam o fluxo aleatório do *slot* ("1" ou "2"), não do candidato;
os choques exógenos são comuns aos dois (números aleatórios comuns). Os testes verificam que trocar
os programas de slot espelha exatamente o resultado.
"""
from __future__ import annotations

import zlib

import numpy as np
from scipy.special import ndtri

import dados as DD
from premissas import (ANOS, ANOS_MANDATO, BASE, CANAIS, CONS, COMUM, LINHAS, LINHA_REPASSE,
                       LINHA_REPRECIFICA, PARCELA_SELIC, SANDUICHE, T, TIPOS, TRANSICAO)

SETORES = DD.SETORES
NS = len(SETORES)
IX = {s: i for i, s in enumerate(SETORES)}


def _vet(d):
    return np.array([d.get(s, 0.0) for s in SETORES])


W_IPCA = _vet(DD.pesos_indice("ipca"))
W_INPC = _vet(DD.pesos_indice("inpc"))

# Repasse cambial por setor (12 e 24 meses; BCB RPM mar/2026, leitura por grupo), reescalado para
# que o IPCA tenha 0,10 em 12 meses; o sorteio comum 'repasse_cambio_ipca' escala todos juntos.
_FX12 = _vet({"A": .26, "I": .12, "SSM": .02, "SO": .02, "ALU": .05, "ENE": .05, "GLP": .40, "COMB": .25,
              "ONI": .05, "REM": .10})
_FX24 = _vet({"A": .33, "I": .22, "SSM": .03, "SO": .03, "ALU": .15, "ENE": .10, "GLP": .50, "COMB": .35,
              "ONI": .10, "REM": .20})
_esc = 0.10 / float(W_IPCA @ _FX12)
FX12, FX24 = _FX12 * _esc, _FX24 * _esc
# Carga da Selic por setor (R6: A 0,5; administrados 0; serviços 1,3; bens 1,1), normalizada
_SEL = _vet({"A": .5, "I": 1.1, "SSM": 1.3, "SO": 1.3, "ALU": .5})
SEL = _SEL / float(W_IPCA @ _SEL)
# Repasse do salário mínimo (M2–M6: serviços intensivos em SM, supermercado...), por 1% de ganho real
SMP = _vet({"A": .04, "I": .02, "SSM": .15, "SO": .03, "ONI": .05})
# Hiato → preços (por 1% de hiato)
GAP = _vet({"A": .05, "I": .10, "SSM": .20, "SO": .20, "ALU": .10})
# Setores tributados pelo IVA (fração da cesta do setor na alíquota cheia)
IVA_BASE = _vet({"A": .3, "I": 1, "SSM": 1, "SO": .7, "ENE": .5, "COMB": .5, "GLP": .5, "REM": .4, "PLA": .4})
IVA_REDUCOES = _vet({"A": 4.0, "REM": 3.0, "SO": 1.0, "PLA": 2.0})  # % de alta se acabarem as reduções (sistema pleno)
GASTO_TRIB = _vet({"I": 1, "SO": 1, "SSM": 1, "ENE": 1, "COMB": 1})  # onde cai o fim de renúncias
W_GT = float(W_IPCA @ np.array([{"I": 1, "SO": 1, "SSM": 1, "ENE": 1, "COMB": 1}.get(s, 0) for s in SETORES]))
FAIXAS_M = [0.6, 1.0, 1.25, 1.75, 2.5, 4.0, 7.0, 15.0]
IVA_FASE = {2028: 0.15, 2029: 0.30, 2030: 0.45, 2031: 0.6, 2032: 0.8, 2033: 1.0, 2034: 1.0}

PIB_BI = BASE["pib_nominal_tri"] * 1000.0
BF_PIB = 157.1 / PIB_BI * 100          # Bolsa Família ≈ 1,17% do PIB (PLOA 2027)
CUSTO_SM = DD.custo_sm()
SM_PP_POR_REAL = (CUSTO_SM["despesa_mi"] - CUSTO_SM["receita_mi"]) / 1000.0 / PIB_BI * 100  # p.p. do PIB por R$ 1
MASSA_PISO = DD.massa_salarial_perto_do_piso()
F_NE_PISO = DD.fracao_ne_no_piso_formal()
TOPO_POR_PP = 0.3 * PIB_BI / 1000 / 3.6 * 100 / 100   # % da renda do décimo do topo por p.p. do PIB de receita sobre o topo [suposição]
MASSA_SOBRE_PIB = 13.4 / 5.0                           # PIB / massa de rendimentos anual (~R$ 5 tri) [calc]

# ---------------------------------------------------------------------------
# Sorteios
# ---------------------------------------------------------------------------
_EPS = 1e-12


def _rng(seed, nome):
    return np.random.default_rng(np.random.SeedSequence([seed, zlib.crc32(nome.encode())]))


def _u(seed, nome, n):
    return _rng(seed, nome).random(n)


def tri_ppf(u, a, m, b):
    u = np.asarray(u, dtype=float)
    if b - a < _EPS:
        return np.full_like(u, a)
    fc = (m - a) / (b - a)
    return np.where(u < fc, a + np.sqrt(u * (b - a) * (m - a)), b - np.sqrt((1 - u) * (b - a) * (b - m)))


def amostrar(spec, u):
    u = np.clip(np.asarray(u, dtype=float), 1e-9, 1 - 1e-9)
    if isinstance(spec, (int, float)):
        return np.full(u.shape, float(spec))
    k = spec[0]
    if k == "tri":
        return tri_ppf(u, *spec[1:])
    if k == "U":
        return spec[1] + (spec[2] - spec[1]) * u
    if k == "N":
        return np.clip(spec[1] + spec[2] * ndtri(u), spec[3], spec[4])
    if k == "LN":
        return np.clip(spec[1] * np.exp(spec[2] * ndtri(u)), spec[3], spec[4])
    raise ValueError(spec)


def media_spec(spec):
    if isinstance(spec, (int, float)):
        return float(spec)
    if spec[0] == "tri":
        return sum(spec[1:4]) / 3
    if spec[0] == "U":
        return (spec[1] + spec[2]) / 2
    return spec[1]


def sorteado(spec):
    return not isinstance(spec, (int, float))


# ---------------------------------------------------------------------------
# Tributos (tabelas de 2026; correção por evento)
# ---------------------------------------------------------------------------
IR_FAIXAS = [(2428.80, 0.0, 0.0), (2826.65, 0.075, 182.16), (3751.05, 0.15, 394.16),
             (4664.68, 0.225, 675.49), (np.inf, 0.275, 908.73)]
IR_DESCONTO_SIMPLIFICADO = 607.20
INSS_FAIXAS = [(1621.00, 0.075), (2902.84, 0.09), (4354.27, 0.12), (8475.55, 0.14)]


def inss(renda, indice=1.0):
    renda = np.asarray(renda, dtype=float)
    total = np.zeros_like(renda)
    piso = 0.0
    for teto, aliq in INSS_FAIXAS:
        teto_i = teto * indice
        total = total + np.clip(np.minimum(renda, teto_i) - piso, 0, None) * aliq
        piso = teto_i
    return total


def ir_mensal(renda, contrib, reducao=True, corr=1.0):
    """IRPF mensal (tabela de mai/2025 + Lei 15.270/2025), limites multiplicados por `corr`
    (correção da tabela; 1 = congelada)."""
    renda = np.asarray(renda, dtype=float)
    corr = np.asarray(corr, dtype=float)
    base = renda - np.maximum(contrib, IR_DESCONTO_SIMPLIFICADO * corr)
    imposto = np.zeros_like(renda)
    lim_inf = 0.0
    for teto, aliq, ded in IR_FAIXAS:
        t = teto * corr
        faixa = (base > lim_inf) & (base <= t)
        imposto = np.where(faixa, base * aliq - ded * corr, imposto)
        lim_inf = t
    imposto = np.maximum(imposto, 0.0)
    red = np.where(renda <= 5000.0 * corr, 312.89 * corr,
                   np.where(renda <= 7350.0 * corr, np.maximum(978.62 * corr - 0.133145 * renda, 0.0), 0.0))
    red = np.where(reducao, red, 0.0)
    return np.maximum(imposto - red, 0.0)


# ---------------------------------------------------------------------------
# Dívida de consenso (âncora do prêmio): taxa implícita calibrada para 86,4% em 2027 (IFI)
# ---------------------------------------------------------------------------
def _sel_media_cons(t):
    ant = BASE["selic_fim_2026"] if t == 0 else CONS["selic_fim"][t - 1]
    return (CONS["selic_fim"][t] + ant) / 2


def _calibrar_k():
    pi, g = CONS["ipca"][0] / 100, CONS["pib"][0] / 100
    gn = (1 + g) * (1 + pi) - 1
    alvo = 86.4 + CONS["primario"][0]
    i = alvo / BASE["divida"] * (1 + gn) - 1
    return (i - PARCELA_SELIC * _sel_media_cons(0) / 100) / (1 - PARCELA_SELIC) - pi


K_JURO_REAL = _calibrar_k()


def _divida_consenso():
    d, out = BASE["divida"], []
    for t in range(T):
        pi, g = CONS["ipca"][t] / 100, CONS["pib"][t] / 100
        i = PARCELA_SELIC * _sel_media_cons(t) / 100 + (1 - PARCELA_SELIC) * (pi + K_JURO_REAL)
        d = d * (1 + i) / ((1 + g) * (1 + pi)) - CONS["primario"][t]
        out.append(d)
    return np.array(out)


DIVIDA_CONS = _divida_consenso()


def _spill(m, p50, p2a3):
    """Elasticidade do salário de quem ganha m SM ao ganho real do mínimo (cascata, M12–M13)."""
    xs = np.array([1.0, 1.25, 1.5, 2.5, 3.5])
    ys = np.stack([np.ones_like(p50), (1 + p50) / 2, p50, p2a3, np.zeros_like(p50)], 0)
    if m >= 3.5:
        return np.zeros_like(p50)
    j = int(np.searchsorted(xs, m, side="right")) - 1
    j = min(j, len(xs) - 2)
    w = (m - xs[j]) / (xs[j + 1] - xs[j])
    return ys[j] * (1 - w) + ys[j + 1] * w


# ---------------------------------------------------------------------------
# Simulação
# ---------------------------------------------------------------------------
def simular(spec: dict, n: int, seed: int, slot: str, comum: dict | None = None,
            canais: dict | None = None, fixos: dict | None = None, tipos=None) -> dict:
    """Simula `n` trajetórias 2027–2034 para um programa `spec`.

    slot: fluxo aleatório dos sorteios de política ("1" ou "2"); comum: substituições em COMUM;
    canais: {canal: bool} (desligar = mesma referência neutra para qualquer programa);
    fixos: força sorteios (testes): {"s0": int, "regra": bool, "bf": bool, "iva": bool, ...}.
    """
    P = dict(COMUM)
    P.update(comum or {})
    on = {c: True for c in CANAIS}
    on.update(canais or {})
    fixos = fixos or {}
    tipos = list(tipos or TIPOS)

    amostras = {}

    def c(nome):
        v = amostrar(P[nome], _u(seed, "c:" + nome, n))
        if sorteado(P[nome]):
            amostras[nome] = v
        return v

    def pol_u(nome, k=n):
        return _u(seed, f"{slot}:{nome}", k)

    def evento(nome, p):
        if nome in fixos:
            return np.full(n, bool(fixos[nome]))
        return pol_u(nome) < p

    # ---------------- choques comuns
    ipca26 = c("ipca_2026")
    pib26 = c("pib_2026")
    ipca_c = np.empty((n, T))
    ipca_c[:, 0] = c("ipca_2027")
    for t in range(1, T):
        ipca_c[:, t] = amostrar(("N", CONS["ipca"][t], P["ipca_dp"], 0.5, 9.0), _u(seed, f"ipca_{ANOS[t]}", n))
    premA = np.stack([amostrar(P["premio_alimentos"], _u(seed, f"premA_{a}", n)) for a in ANOS], 1)
    pib_c = np.stack([c("pib_2027")] + [amostrar(P["pib_2028_30"], _u(seed, f"pib_{a}", n)) for a in ANOS[1:]], 1)
    rr_c = np.stack([c("renda_real_2027")] + [amostrar(P["renda_real_2028_30"], _u(seed, f"rr_{a}", n)) for a in ANOS[1:]], 1)
    u_c = c("desemprego_2027")[:, None] + np.cumsum(np.column_stack(
        [np.zeros(n)] + [amostrar(("N", 0, P["desemprego_dp"], -2, 2), _u(seed, f"udp_{a}", n)) for a in ANOS[1:]]), 1)
    sm27 = c("sm_2027")
    brent = c("brent_2027")
    fbg, fbd = c("fracao_bomba_gasolina"), c("fracao_bomba_diesel")
    rw = np.cumsum(np.stack([amostrar(("N", 0, P["fx_ruido_dp"], -0.5, 0.5), _u(seed, f"fx_{a}", n)) for a in ANOS], 1), 1)
    sel_noise = np.stack([amostrar(("N", 0, P["selic_ruido_dp"], -3, 3), _u(seed, f"sel_{a}", n)) for a in ANOS], 1)
    e1 = c("repasse_cambio_ipca") / 0.10
    assim = c("assimetria")
    e6 = c("selic_ipca")
    rho_s, phi_pi, phi_y = c("taylor_rho"), c("taylor_pi"), c("taylor_gap")
    lam_s, lam_x, e8 = c("premio_selic"), c("premio_cambio"), c("premio_divida")
    beta_r, rho_g = c("is_juro"), c("hiato_rho")
    ok_neg, ok_pos = c("okun_neg"), c("okun_pos")
    theta, kappa, phi_u = c("indexacao"), c("correcao_erro"), c("salario_desemprego")
    m_tr, m_bs, m_di = c("mult_transferencia"), c("mult_beneficio_sm"), c("mult_discricionaria")
    m_ic, m_it, m_su = c("mult_imposto_consumo"), c("mult_imposto_topo"), c("mult_subsidio")
    smp_esc, smp_lag, smp_ne = c("sm_repasse_escala"), c("sm_repasse_defasagem"), c("sm_repasse_ne")
    far_i, far_a = c("farol_informal"), c("farol_autonomo")
    cas50, cas23 = c("cascata_p50"), c("cascata_2a3")
    cons_paga, psi = c("consumidor_paga"), c("achatamento_psi")
    eps_br, eps_ne, qualif, f2i = c("emprego_sm_br"), c("emprego_sm_ne"), c("emprego_pouca_qualif"), c("formal_para_informal")
    b_baixa, b_alta = c("beta_desemprego_baixa"), c("beta_desemprego_alta")
    ent = np.stack([c("entrega_credivel"), c("entrega_meio"), c("entrega_crise")], 1)
    cortavel, fech_k, phi_debt = c("discricionaria_cortavel"), c("fechamento_k"), c("financiado_divida")
    fech_sm = c("fechamento_sm")
    ob_abono = c("obrig_abono")
    inc_ls, inc_fase, rep_banco = c("incidencia_lucro_salario"), c("incidencia_fase"), c("repasse_banco_spread")
    rep_corte, rep_alta = c("repasse_corte_tributo"), c("repasse_alta_tributo")
    iva_l = c("iva_leitura")
    corte_gas = c("corte_gasolina_bomba")
    x6_p, x6_g, x6_inf = c("x6_precos_servicos"), c("x6_pib_nivel"), c("x6_informalizacao")
    pec_s, pec_h, pec_f = c("pec12_parcela"), c("pec12_horas"), c("pec12_formaliza")
    fx_renda, conv = c("cambio_renda"), c("conv_meses")
    fx_reg = np.stack([c("fx_credivel"), c("fx_meio"), c("fx_crise")], 1)
    pr_reg = np.stack([c("premio_credivel"), np.zeros(n), c("premio_crise")], 1)
    crise_div = c("crise_por_divida")
    encolh, alu_mud, plano_col = c("encolhimento"), c("aluguel_mudanca"), c("plano_coletivo")
    af_lim, af_passo = c("ajuste_forcado_limiar"), c("ajuste_forcado_passo")
    dir_sel, cr_imp, cr_res = c("direcionado_selic"), c("credito_impulso"), c("credito_ressaca")

    # ---------------- sorteios de política (fluxo do slot)
    rg = spec["regime"]
    pi0 = np.asarray(rg["pi0"], float)
    u0 = pol_u("regime_0")
    s = np.empty((n, T), dtype=np.int8)
    s0 = (u0 > pi0[0]).astype(np.int8) + (u0 > pi0[0] + pi0[1]).astype(np.int8)
    if "s0" in fixos:
        s0 = np.full(n, int(fixos["s0"]), np.int8)
    amostras["regime_ini"] = s0.astype(float)
    trans = np.asarray(rg["transicao"] if rg.get("transicao") is not None else TRANSICAO, float)
    impacto = amostrar(rg["impacto_cambio"], pol_u("impacto"))
    fs = spec["fiscal"]
    ajuste_total = amostrar(fs["ajuste_total"], pol_u("ajuste_total"))
    comp_media = np.asarray(fs["composicao"], float)
    comp = _rng(seed, f"{slot}:comp").dirichlet(comp_media * fs["concentracao"] + 1e-6, n)
    w_topo, w_te, w_disc, w_obr = comp[:, 0], comp[:, 1], comp[:, 2], comp[:, 3]
    privat = amostrar(fs["privatizacao"], pol_u("privat"))
    r_unica = amostrar(fs["receita_unica"], pol_u("receita_unica"))
    amostras["receita_unica"] = r_unica
    antecip = c("antecipacao_receita")
    lacuna_ir = c("lacuna_compensacao_ir")
    unica_acum = np.zeros(n)
    intencao = evento("regra_intencao", spec["minimo"]["p_intencao"])
    p_bf = amostrar(spec["bolsa"]["p_reajuste"], pol_u("p_bf"))
    p_ir = amostrar(spec["ir"]["p_correcao"], pol_u("p_ir"))
    rev_topo = evento("reverte_topo", spec["ir"]["p_reverte_topo"])
    rev_banco = evento("reverte_bancos", spec["ir"]["p_reverte_bancos"]) | (rev_topo & (pol_u("rb_corr") < 0.5) & (spec["ir"]["p_reverte_bancos"] > 0))
    iva = evento("iva", spec["iva"]["p"])
    iva_unif = pol_u("iva_rota") < float(P["iva_rota_uniforme"])
    cb = spec["combustivel"]
    subsid27 = amostrar(cb["subsidio_2027"], pol_u("subsidio"))
    corte_comb = evento("corte_comb", cb["p_corte_trib"])
    custo_corte = amostrar(cb["custo_corte"], pol_u("custo_corte"))
    x6 = evento("x6", spec["trabalho"]["p_6x1"])
    pec12 = evento("pec12", spec["trabalho"]["p_pec12"])
    cr = spec["credito"]
    dfatia = amostrar(cr["direcionado_dfatia"], pol_u("dfatia"))
    expcr = amostrar(cr["expansao_credito"], pol_u("expcr"))
    fgts_desc = amostrar(cr["fgts_desconto"], pol_u("fgts_desc"))
    difer = np.asarray(cr["diferidos"], float)
    fatia_cum = np.zeros(n); cred_hist = []
    u_bf = np.stack([pol_u(f"bf_{a}") for a in ANOS], 1)
    u_ir = np.stack([pol_u(f"ir_{a}") for a in ANOS], 1)
    u_fech = np.stack([pol_u(f"fech_{a}") for a in ANOS], 1)
    u_fech2 = np.stack([pol_u(f"fech2_{a}") for a in ANOS], 1)
    u_reg = np.stack([pol_u(f"reg_{a}") for a in ANOS], 1)
    for k, v in (("iva", iva), ("x6", x6), ("pec12", pec12), ("reverte_topo", rev_topo), ("corte_comb", corte_comb),
                 ("intencao_regra", intencao)):
        amostras[k] = v.astype(float)
    amostras["comp_obrigatoria"] = w_obr
    amostras["ajuste_total"] = ajuste_total

    # ---------------- estados
    Z = lambda: np.zeros((n, T))
    x = Z(); fx = Z(); prem = Z(); sel = Z(); sel_avg = Z(); dev = Z()
    infl = np.zeros((n, T, NS)); ipca = Z(); inpc = Z(); infl_ssm_ne = Z()
    gap = Z(); gap_c = Z(); pib = Z(); des = Z(); divida = Z(); prim = Z()
    sm = Z(); smr = Z(); dg = Z(); bf = Z(); bf_linha = Z(); ir_corr = Z()
    entregue = Z(); x_disc = Z(); x_obr = Z(); r_topo = Z(); te = Z(); forcado = Z()
    custo_iva_t = Z(); fiscal_tr = Z(); regra = np.zeros((n, T), bool); quebra_forcada = np.zeros(n, bool)
    spread_livre = Z(); cred_cum = Z(); crise_ate = np.zeros(n, bool); arcab_rompido = np.zeros(n, bool)
    rompe_prev_bump = np.zeros(n, bool)

    on_f, on_i = on["fiscal"], on["impostos"]
    x_prev = np.log(BASE["cambio"] / BASE["cambio"])  # 0
    core_prev = np.log(BASE["cambio"] * (1 + impacto) / CONS["cambio"][0]) if on["cambio"] else np.zeros(n)
    dev_prev = np.zeros(n); dev_avg_prev = np.zeros(n); surp_prev = np.zeros(n)
    gap_prev = np.zeros(n); gapc_prev = np.zeros(n); d_prev = np.full(n, BASE["divida"])
    sm_prev = np.full(n, BASE["salario_minimo"]); smr_prev = sm_prev.copy(); sel_prev = np.full(n, BASE["selic_fim_2026"])
    inpc_prev = ipca26.copy(); pibs = {2026: pib26}
    pibn_prev = np.full(n, PIB_BI)
    bf_val = np.full(n, 1.0); bf_acc = 1 + 0.25 * ipca26 / 100; bf_lin = np.full(n, BASE["bf_linha_pc"])
    ir_c = np.ones(n); ir_acc = 1 + ipca26 / 100
    dx_prev = np.zeros(n); contr_prev = {k: np.zeros(n) for k in ("tr", "bs", "di", "ob", "ic", "it", "su")}
    regra_ok = intencao.copy(); s_prev = s0
    x6_level_prev = np.zeros(n); dg_prev = np.zeros(n)
    rest0 = 1 - 6.0 / conv
    forc_prev = np.zeros(n)

    for t, ano in enumerate(ANOS):
        mandato = t < ANOS_MANDATO
        # 1. regime
        if t == 0:
            st = s0
        else:
            excesso = np.maximum(0.0, d_prev - DIVIDA_CONS[t - 1]) / 10.0 if on_f else np.zeros(n)
            row = trans[s_prev]
            pc = np.minimum(row[:, 2] + crise_div * excesso + 0.15 * rompe_prev_bump, 0.95)
            resto = row[:, 0] + row[:, 1]
            p_cred = row[:, 0] / np.maximum(resto, 1e-9) * (1 - pc)
            st = (u_reg[:, t] > p_cred).astype(np.int8) + (u_reg[:, t] > 1 - pc).astype(np.int8)
        s[:, t] = st
        crise_ate |= (st == 2) & mandato
        # 2. ajuste anunciado e entregue (o alvo se mantém depois de atingido)
        alvo = ajuste_total * min(1.0, 12.0 * (t + 1) / fs["ajuste_meses"])
        delta = np.take_along_axis(ent, st[:, None].astype(int), 1)[:, 0]
        ent_t = alvo * delta if on_f else np.zeros(n)
        # ajuste forçado depois do mandato (regra comum: quem governar)
        if not mandato and on_f:
            gatilho = (d_prev - DIVIDA_CONS[t - 1] > af_lim) | (s_prev == 2)
            forc = np.where(gatilho, np.minimum(forc_prev + af_passo, 2.5), forc_prev)
        else:
            forc = forc_prev
        forcado[:, t] = forc
        entregue[:, t] = ent_t
        # receita única: entra no primário só em 2027–28 e não corta ninguém; o resto é ajuste recorrente
        unica_t = ent_t * r_unica if t < 2 else np.zeros(n)
        unica_acum = unica_acum + unica_t
        rec_t = ent_t * (1 - r_unica)
        xd = rec_t * w_disc + 0.5 * forc
        xo_alvo = rec_t * w_obr + 0.5 * forc
        rt = rec_t * w_topo
        tet = rec_t * w_te
        # 3. regra do mínimo e fechamento (comum: corte acima do cortável força a quebra)
        excesso_corte = np.maximum(0.0, xd + P["vegetativo"] * (t + 1) - cortavel) + xo_alvo
        rompe = np.zeros(n, bool)
        if t >= 1:
            p_estouro = np.clip(fech_k * excesso_corte, 0, 0.9)
            estoura = u_fech[:, t] < p_estouro
            pela_regra = estoura & (u_fech2[:, t] < fech_sm) & regra_ok
            rompe = estoura & ~pela_regra
            arcab_rompido |= rompe & mandato
            if "regra" not in fixos:
                quebra_forcada |= pela_regra
                regra_ok = regra_ok & ~pela_regra
        rompe_prev_bump = rompe
        if "regra" in fixos:
            regra_ok = np.full(n, bool(fixos["regra"]))
        regra[:, t] = regra_ok
        if t == 0:
            sm_t = sm27.copy(); smr_t = sm27.copy()
        else:
            g2 = pibs[ano - 2]
            lo, hi = (0.6, 2.5) if ano <= 2030 else (0.0, 2.5)
            ganho_ref = np.clip(g2, lo, hi)
            ganho = np.where(regra_ok, ganho_ref + spec["minimo"]["ganho_extra"], 0.0)
            sm_t = sm_prev * (1 + inpc_prev / 100) * (1 + ganho / 100)
            smr_t = smr_prev * (1 + inpc_prev / 100) * (1 + ganho_ref / 100)
        dg_t = 100 * np.log((sm_t / sm_prev) / (smr_t / smr_prev))
        sm[:, t], smr[:, t], dg[:, t] = sm_t, smr_t, dg_t
        # 4. Bolsa Família (evento de reajuste que repõe o INPC acumulado) e IR (correção da tabela)
        j_bf = (u_bf[:, t] < p_bf) if "bf" not in fixos else np.full(n, bool(fixos["bf"]))
        fat = np.where(j_bf, bf_acc * (1 + spec["bolsa"]["real_extra"] / 100), 1.0)
        bf_val = bf_val * fat; bf_lin = bf_lin * np.where(j_bf, bf_acc, 1.0); bf_acc = np.where(j_bf, 1.0, bf_acc)
        bf[:, t] = bf_val; bf_linha[:, t] = bf_lin
        j_ir = u_ir[:, t] < p_ir
        ir_c = np.where(j_ir & on_i, ir_c * ir_acc, ir_c); ir_acc = np.where(j_ir & on_i, 1.0, ir_acc)
        ir_corr[:, t] = ir_c
        # 5. custos e economias de medidas (p.p. do PIB) — PIB nominal estimado do ano
        pibn_est = pibn_prev * (1 + CONS["pib"][t] / 100) * (1 + CONS["ipca"][t] / 100)
        sm_custo = (sm_t - smr_t) * SM_PP_POR_REAL * PIB_BI / pibn_est
        sm_econ = np.maximum(-sm_custo, 0.0)
        bf_custo = BF_PIB * (bf_val - 1.0)
        ir_custo = 2.5 * (ir_c - 1.0)                      # ~0,025 p.p. por 1% de correção [calc aproximado]
        fase = IVA_FASE.get(ano, 0.0)
        iva_custo = np.where(iva & on_i, fase * (1.1 + 3.1 * iva_l) * np.where(iva_unif, 1.0, 0.4), 0.0)
        comb_custo = (np.where(t == 0, subsid27, 0.0) + np.where(corte_comb, custo_corte, 0.0)) if on_i else np.zeros(n)
        rev_custo = (np.where(rev_topo & (ano >= 2028), 0.2, 0.0) + np.where(rev_banco & (ano >= 2028), 0.2, 0.0)) if on_i else np.zeros(n)
        sem_fonte = iva_custo + np.where(corte_comb & on_i, custo_corte, 0.0) + rev_custo
        cobre = (1 - phi_debt) * sem_fonte
        sp = np.maximum(w_disc + w_obr, 1e-6)
        xd = xd + cobre * w_disc / sp
        xo_alvo = xo_alvo + cobre * w_obr / sp
        xo_res = np.maximum(0.0, xo_alvo - sm_econ)
        x_disc[:, t], x_obr[:, t] = xd, xo_res
        r_eff = (rt - np.where(rev_topo & (ano >= 2028), 0.2, 0.0)) if on_i else np.zeros(n)
        r_topo[:, t] = r_eff
        te[:, t] = tet if on_i else 0.0
        custo_iva_t[:, t] = iva_custo
        dif_t = difer[t] if on["credito"] else 0.0
        # conta adiada: antecipação de receitas (royalties, dívida ativa) falta em 2031–34
        dif_t = dif_t + (antecip * unica_acum / 4.0 if not mandato else 0.0)
        subs_t = (subsid27 if (t == 0 and on_i) else np.zeros(n))
        if on_f:
            # ajuste entregue + forçado; economia do mínimo além da meta de obrigatórias; custos de medidas;
            # promessas sem fonte: parte vira dívida (phi), parte é coberta por cortes (já em xd/xo)
            prim_med = (rec_t + unica_t - (lacuna_ir if ano <= 2028 else 0.0) + forc + np.maximum(0.0, sm_econ - xo_alvo) - np.maximum(sm_custo, 0.0) - bf_custo
                        - ir_custo - phi_debt * sem_fonte - subs_t - dif_t)
        else:
            prim_med = np.zeros(n)
        # 6. câmbio: núcleo converge para o nível do regime; ruído comum; realimentação do prêmio
        if on["cambio"]:
            lvl = np.take_along_axis(fx_reg, st[:, None].astype(int), 1)[:, 0]
            q = rest0 if t == 0 else 0.35
            core = lvl + (core_prev - lvl) * q
        else:
            core = np.zeros(n)
        # 7. prêmio: regime + desvio da dívida em relação ao consenso (realimentação fiscal)
        if on["juros"]:
            pr = np.take_along_axis(pr_reg, st[:, None].astype(int), 1)[:, 0]
            if t > 0:
                pr = pr + np.clip(e8 * (d_prev - DIVIDA_CONS[t - 1]), -3.0, 6.0)
        else:
            pr = np.zeros(n)
        prem[:, t] = pr
        pr_div = np.clip(e8 * (d_prev - DIVIDA_CONS[t - 1]), -3.0, 6.0) if (on["juros"] and t > 0) else np.zeros(n)
        fb = lam_x * pr_div if on["cambio"] else 0.0
        x_t = np.clip(core + rw[:, t] + fb, -0.6, 1.0)
        x[:, t] = x_t
        fx[:, t] = CONS["cambio"][t] * np.exp(x_t)
        dx = x_t - x_prev
        # 8. Selic (Taylor + prêmio; o candidato só entra pelo prêmio e pelas expectativas)
        surp_esp = 0.5 * surp_prev + 0.5 * e1 * 0.10 * dx * 100
        if on["credito"] and mandato:
            fatia_cum = fatia_cum + dfatia
        dsel_dir = dir_sel * fatia_cum if on["credito"] else 0.0
        if on["juros"]:
            dv = rho_s * dev_prev + phi_pi * surp_esp + phi_y * (gap_prev + gapc_prev) + lam_s * pr + sel_noise[:, t] + dsel_dir
        else:
            dv = sel_noise[:, t].copy()
        sel_t = np.clip(CONS["selic_fim"][t] + dv, 4.0, 26.0)
        dv = sel_t - CONS["selic_fim"][t]
        sel[:, t], dev[:, t] = sel_t, dv
        sa = (sel_t + sel_prev) / 2
        sel_avg[:, t] = sa
        dev_avg = sa - _sel_media_cons(t)
        # 9. inflação por setor
        a_t = np.where(dx < 0, assim, 1.0); a_p = np.where(dx_prev < 0, assim, 1.0)
        cbase = ipca_c[:, t] - W_IPCA[IX["A"]] * media_spec(P["premio_alimentos"])
        pi_s = np.repeat(cbase[:, None], NS, 1)
        pi_s[:, IX["A"]] += premA[:, t]
        pi_s += 100 * e1[:, None] * (FX12[None] * (a_t * dx)[:, None] + (FX24 - FX12)[None] * (a_p * dx_prev)[:, None])
        pi_s -= e6[:, None] * SEL[None] * (0.4 * dev_avg + 0.6 * dev_avg_prev)[:, None]
        pi_s += GAP[None] * (gap_prev + gapc_prev)[:, None]
        if on["repasse"]:
            smx = smp_esc * (smp_lag * dg_t + (1 - smp_lag) * dg_prev)
            pi_s += SMP[None] * smx[:, None]
        else:
            smx = np.zeros(n)
        # combustíveis represados (comum: chega a quem vencer) e política de cada um
        if t == 0:
            gap_g = 1.32 * (brent / 100) * (fx[:, 0] / BASE["cambio"]) - 1
            gap_d = 2.02 * (brent / 100) * (fx[:, 0] / BASE["cambio"]) - 1
            need_g = 100 * fbg * np.maximum(gap_g, 0.0)
            need_d = 100 * fbd * np.maximum(gap_d, 0.0)
        frac27 = cb["frac_2027"] if on_i else 1.0
        frac = frac27 if t == 0 else (1 - frac27 if t == 1 else 0.0)
        pi_s[:, IX["COMB"]] += frac * need_g
        pi_s[:, IX["GLP"]] += 0.5 * frac * need_g
        pi_s[:, IX["A"]] += P["diesel_alimentos"] * frac * need_d
        pi_s[:, IX["ONI"]] += P["diesel_onibus"] * frac * need_d
        if on_i and t == 0:
            pi_s[:, IX["COMB"]] -= np.where(corte_comb, corte_gas, 0.0)
        if on_i:
            dfase = fase - IVA_FASE.get(ano - 1, 0.0)
            mag = (1.6 + 4.65 * iva_l) * rep_corte
            unif = -mag[:, None] * IVA_BASE[None]
            remo = -0.6 * mag[:, None] * IVA_BASE[None] * (IVA_REDUCOES[None] == 0) + rep_alta[:, None] * IVA_REDUCOES[None]
            pi_s += np.where(iva[:, None], dfase * np.where(iva_unif[:, None], unif, remo), 0.0)
            # fim de renúncias: receita / (consumo tributado ≈ R$ 8 tri × peso) → alta de preço, repasse de alta
            dte = tet - (te[:, t - 1] if t > 0 else 0.0)
            pi_s += (dte * PIB_BI / (8000.0 * W_GT) * rep_alta)[:, None] * GASTO_TRIB[None]
        if on["trabalho"] and t < 2:
            x6e = np.where(x6, x6_p * 0.5, 0.0)
            pi_s[:, IX["SSM"]] += x6e; pi_s[:, IX["SO"]] += 0.5 * x6e
        infl[:, t] = pi_s
        infl_ssm_ne[:, t] = pi_s[:, IX["SSM"]] + (smp_ne - 1) * SMP[IX["SSM"]] * smx
        ipca[:, t] = pi_s @ W_IPCA
        inpc[:, t] = pi_s @ W_INPC
        surp = ipca[:, t] - ipca_c[:, t]
        # 10. hiato (política) + hiato comum; PIB; desemprego
        contr = {
            "tr": -bf_custo, "bs": -np.maximum(sm_custo, 0) + sm_econ, "di": xd + 0.5 * forc, "ob": xo_res,
            "ic": tet - iva_custo - np.where(corte_comb & on_i, custo_corte, 0.0), "it": r_eff,
            "su": -subs_t,
        }
        if on_f:
            imp = (m_tr * (contr["tr"] - contr_prev["tr"]) + m_bs * (contr["bs"] - contr_prev["bs"])
                   + m_di * (contr["di"] - contr_prev["di"]) + m_bs * (contr["ob"] - contr_prev["ob"])
                   + m_ic * (contr["ic"] - contr_prev["ic"]) + m_it * (contr["it"] - contr_prev["it"])
                   + m_su * (contr["su"] - contr_prev["su"]))
        else:
            imp = np.zeros(n)
        x6g = np.where(x6, x6_g * 0.5, 0.0) * (t < 2) if on["trabalho"] else 0.0
        juro_g = beta_r * (0.5 * dev_avg + 0.5 * dev_avg_prev) if on["juros"] else 0.0
        # crédito às famílias: impulso no ano, ressaca defasada (1–3 anos depois)
        cr_t = expcr if (on["credito"] and mandato) else np.zeros(n)
        ressaca = sum(cred_hist[-k] for k in (1, 2, 3) if len(cred_hist) >= k) if cred_hist else 0.0
        g_t = rho_g * gap_prev - juro_g - imp + x6g + cr_imp * cr_t - cr_res / 3.0 * ressaca
        cred_hist.append(cr_t)
        cred_cum[:, t] = (cred_cum[:, t - 1] if t > 0 else 0.0) + cr_t
        gc_t = 0.5 * gapc_prev + (pib_c[:, t] - CONS["pib"][t])
        gap[:, t], gap_c[:, t] = g_t, gc_t
        pib[:, t] = pib_c[:, t] + (g_t - gap_prev)
        tot_gap = g_t + gc_t
        ok = np.where(tot_gap < 0, ok_neg, ok_pos)
        des[:, t] = np.clip(u_c[:, t] - ok * ((g_t if on["emprego"] else 0.0) + gc_t), 2.5, 25.0)
        # 11. dívida
        pibn = pibn_prev * (1 + pib[:, t] / 100) * (1 + ipca[:, t] / 100)
        prim_t = CONS["primario"][t] + prim_med + P["receita_ciclica"] * tot_gap
        i_ef = PARCELA_SELIC * sa / 100 + (1 - PARCELA_SELIC) * (ipca[:, t] / 100 + K_JURO_REAL)
        gn = pibn / pibn_prev - 1
        d_t = d_prev * (1 + i_ef) / (1 + gn) - prim_t + P["fx_divida"] * 100 * dx * (1 if on["cambio"] else 0)
        if t == 0 and on_f:
            d_t = d_t - privat
        divida[:, t], prim[:, t] = d_t, prim_t
        spread_livre[:, t] = 0.0
        # avança
        pibs[ano] = pib[:, t]
        d_prev, s_prev, x_prev, core_prev = d_t, st, x_t, core
        dev_prev, dev_avg_prev, surp_prev, dx_prev = dv, dev_avg, surp, dx
        gap_prev, gapc_prev, sm_prev, smr_prev, sel_prev = g_t, gc_t, sm_t, smr_t, sel_t
        inpc_prev, pibn_prev, dg_prev, forc_prev = inpc[:, t], pibn, dg_t, forc
        contr_prev = contr
        bf_acc = bf_acc * (1 + inpc[:, t] / 100)
        ir_acc = ir_acc * (1 + inpc[:, t] / 100)

    # ---------------- índices de preço (2026 = 1)
    nivel_set = np.cumprod(1 + infl / 100, axis=1)            # (n, T, NS)
    nivel_ipca = np.cumprod(1 + ipca / 100, axis=1)
    nivel_inpc = np.cumprod(1 + inpc / 100, axis=1)
    nivel_ssm_ne = np.cumprod(1 + infl_ssm_ne / 100, axis=1)
    cum_dg = np.cumsum(dg, axis=1)                             # log-% de desvio do mínimo
    idx_inss = np.cumprod(1 + np.column_stack([ipca26, inpc[:, :-1]]) / 100, axis=1)

    # salário de mercado (real-alvo com correção de erro) — comum a todos os salários fora do piso
    lw_star = np.cumsum(rr_c - phi_u[:, None] * (des - u_c) * (1 if on["emprego"] else 0), axis=1) / 100
    z = np.zeros(n); zs = Z()
    for t in range(T):
        z = (1 - kappa) * z - (1 - theta) * (ipca[:, t] - CONS["ipca"][t]) / 100
        zs[:, t] = z
    w_merc = np.exp(lw_star + zs) * nivel_ipca                 # índice nominal (2026 = 1)
    if on["impostos"]:
        # só a parte de tributo sobre lucro das empresas (~20%) chega aos salários; o IRPFM é pessoal (IR18/IR21)
        w_merc = w_merc * (1 - inc_ls[:, None] * inc_fase[:, None] * 0.2 * MASSA_SOBRE_PIB * r_topo / 100)
    sm_dir = sm if on["sm_direto"] else smr
    cdg = cum_dg if on["farol"] else np.zeros_like(cum_dg)

    # ---------------- renda do trabalho por faixa de SM (Nordeste x resto; formal x informal), real pelo INPC,
    # já descontado o risco esperado de perder o emprego por causa do mínimo (sem desemprego cíclico)
    faixas = {}
    rr_f = 0.45
    for reg in ("NE", "resto"):
        eps = eps_ne if reg == "NE" else eps_br
        defl = nivel_inpc + (W_INPC[IX["SSM"]] * (nivel_ssm_ne - nivel_set[:, :, IX["SSM"]]) if reg == "NE" else 0.0)
        for m in FAIXAS_M:
            # formal
            if m <= 1.0:
                wf = sm_dir * m
            else:
                sp = _spill(m, cas50, cas23)[:, None] if on["achatamento"] else 0.0
                comp = (psi * (1 - cons_paga) * MASSA_PISO)[:, None] * cum_dg if (on["achatamento"] and m > 1.5) else 0.0
                wf = m * BASE["salario_minimo"] * w_merc * np.exp((sp * cum_dg - comp) / 100)
            if m <= 2.0 and on["emprego"]:
                e_ = eps * (qualif if m <= 1.0 else 1.0)
                psm = np.clip(-e_[:, None] * (1.0 if m <= 1.0 else 0.3) * cum_dg / 100, -0.05, 0.3)
                wf = wf * (1 - psm * (1 - (f2i[:, None] * 0.7 + (1 - f2i[:, None]) * rr_f)))
            lam = (far_i if m <= 1.25 else (0.5 * far_i if m <= 1.75 else 0.0 * far_i))[:, None] if on["farol"] else 0.0
            wi = m * BASE["salario_minimo"] * w_merc * np.exp(lam * cum_dg / 100)
            faixas[f"{reg}|formal|{m:g}"] = 100 * wf / defl / (m * BASE["salario_minimo"])
            faixas[f"{reg}|informal|{m:g}"] = 100 * wi / defl / (m * BASE["salario_minimo"])

    # ---------------- famílias
    res = {}
    for h in tipos:
        tp = TIPOS[h] if h in TIPOS else SANDUICHE[h]
        res[h] = _familia(h, tp, n, seed, P, on, sm_dir, sm, w_merc, cum_dg, cdg, far_i, far_a, cas50, cas23, psi,
                          cons_paga, des, b_baixa, b_alta, eps_br, eps_ne, qualif, f2i, x6, x6_inf, pec12, pec_s,
                          pec_h, pec_f, bf, bf_linha, nivel_set, nivel_ssm_ne, ir_corr, idx_inss, sel_avg, ipca,
                          rev_banco, rep_banco, spread_livre, x, fx_renda, x_disc, x_obr, r_topo, rev_topo, cred_cum,
                          fgts_desc, ob_abono, encolh, alu_mud, plano_col, nivel_ipca, ipca26)
    cesta = BASE["cesta"] * nivel_set[:, :, IX["A"]]
    regimes_p = np.stack([(s == k).mean(0) for k in range(3)], 0)
    return {
        "familias": res,
        "macro": {"ipca": ipca, "alimentos": infl[:, :, IX["A"]], "servicos_sm": infl[:, :, IX["SSM"]], "inpc": inpc,
                  "selic": sel, "cambio": fx, "divida": divida, "desemprego": des, "pib": pib, "primario": prim,
                  "premio": prem, "sm_real": 100 * sm / BASE["salario_minimo"] / nivel_inpc,
                  "horas_cesta": cesta / sm * BASE["horas_mes"], "ajuste_entregue": entregue,
                  "ajuste_forcado": forcado, "corte_discricionaria": x_disc, "corte_obrigatoria": x_obr},
        "regime": s, "regime_ini": s0, "regimes_p": regimes_p,
        "eventos": {"regra_sm_2030": regra[:, ANOS_MANDATO - 1], "regra_sm_2034": regra[:, -1],
                    "quebra_forcada": quebra_forcada, "crise_ate_2030": crise_ate, "arcabouco_rompido_2030": arcab_rompido,
                    "ajuste_forcado_pos": forcado[:, -1] > 0, "iva": iva, "x6": x6, "pec12": pec12,
                    "reverte_topo": rev_topo, "bf_reajustes": (np.diff(np.column_stack([np.ones(n), bf]), axis=1) > 1e-9).sum(1)},
        "amostras": amostras,
        "faixas": faixas,
    }


def _familia(h, tp, n, seed, P, on, sm_dir, sm, w_merc, cum_dg, cdg, far_i, far_a, cas50, cas23, psi, cons_paga,
             des, b_baixa, b_alta, eps_br, eps_ne, qualif, f2i, x6, x6_inf, pec12, pec_s, pec_h, pec_f, bf, bf_linha,
             nivel_set, nivel_ssm_ne, ir_corr, idx_inss, sel_avg, ipca, rev_banco, rep_banco, spread_livre, x, fx_renda,
             x_disc, x_obr, r_topo, rev_topo, cred_cum, fgts_desc, ob_abono, encolh, alu_mud, plano_col, nivel_ipca, ipca26):
    SM0 = BASE["salario_minimo"]
    Tn = sm.shape[1]
    cexp = np.exp(fx_renda[:, None] * tp.get("exposto_cambio", 0.0) * x) if on["cambio"] else 1.0
    ach = on["achatamento"]
    renda_trab = np.zeros((n, Tn)); renda0_trab = 0.0
    formal_w = np.zeros((n, Tn)); formal0 = 0.0
    eh_trab = any(k in tp for k in ("formal", "informal", "autonomo", "pj"))
    # --- trabalho
    if "formal" in tp:
        m = tp["formal"]
        if m <= 1.0:
            w = sm_dir * m
        else:
            sp = _spill(m, cas50, cas23)[:, None] if ach else 0.0
            comp = (psi * (1 - cons_paga) * MASSA_PISO)[:, None] * cum_dg if (ach and m > 1.5) else 0.0
            w = m * SM0 * w_merc * np.exp((sp * cum_dg - comp) / 100)
        w = w * cexp
        formal_w = w; formal0 = m * SM0
    if "informal" in tp:
        m = tp["informal"]
        lam = far_i[:, None] if on["farol"] else 0.0
        w = m * SM0 * w_merc * np.exp(lam * cum_dg / 100) * cexp
        renda_trab = renda_trab + w; renda0_trab += m * SM0
    if "autonomo" in tp:
        m = tp["autonomo"]
        lam = far_a[:, None] if on["farol"] else 0.0
        w = m * SM0 * w_merc * np.exp(lam * cum_dg / 100) * cexp
        renda_trab = renda_trab + w; renda0_trab += m * SM0
    if "pj" in tp:
        m = tp["pj"]
        w = m * SM0 * w_merc * cexp * (1 - tp["trib_pj"])
        renda_trab = renda_trab + w; renda0_trab += m * SM0 * (1 - tp["trib_pj"])
    # --- emprego (risco binário com uniforme comum aos dois cenários)
    status_desemp = np.zeros((n, Tn), bool)
    if eh_trab:
        beta = {"baixa": b_baixa, "media": np.full(n, 1.0), "alta": b_alta}[tp["beta"]][:, None]
        p_cic = tp["u0"] + (beta * (des - BASE["desemprego"]) / 100 if on["emprego"] else 0.0)
        p_sm = np.zeros((n, Tn))
        if "formal" in tp and tp["formal"] <= 2.0 and on["emprego"]:
            eps = (eps_br * (1 - F_NE_PISO) + eps_ne * F_NE_PISO)
            if tp["formal"] <= 1.0:
                eps = eps * qualif
            frac_piso = 1.0 if tp["formal"] <= 1.0 else 0.3
            p_sm = -eps[:, None] * frac_piso * cum_dg / 100
        if tp.get("x6") and on["trabalho"]:
            p_sm = p_sm + np.where(x6, x6_inf / 100, 0.0)[:, None] * (np.arange(Tn) >= 1)[None] * (1.0 if tp.get("formal", 9) <= 2 else 0.3)
        p = np.clip(p_cic + p_sm, 0.002, 0.8)
        U = np.stack([_u(seed, f"emp:{h}:{a}", n) for a in range(Tn)], 1)
        status_desemp = U < p
        frac_sm = np.clip(np.where(p > 0, np.maximum(p_sm, 0) / p, 0), 0, 1)
        rr = tp["rr"]
        perda = np.where(status_desemp, 1 - (frac_sm * (f2i[:, None] * 0.7 + (1 - f2i[:, None]) * rr) + (1 - frac_sm) * rr), 0.0)
    else:
        perda = np.zeros((n, Tn))
    base_emp = (1 - tp.get("u0", 0.0) * (1 - tp.get("rr", 1.0))) if eh_trab else 1.0
    # PEC 12: parte dos formais de baixa renda vai para contrato por hora; parte dos informais formaliza
    fator_pec = 1.0
    if on["trabalho"] and tp.get("pec12"):
        Up = _u(seed, f"pec:{h}", n)
        hr = np.clip(pec_h + 0.15 * ndtri(np.clip(_u(seed, f"pech:{h}", n), 1e-9, 1 - 1e-9)), 0.2, 1.0)
        fator_pec = np.where((pec12 & (Up < pec_s))[:, None] & (np.arange(Tn) >= 1)[None], hr[:, None], 1.0)
    form_inf = np.zeros((n, Tn), bool)
    if on["trabalho"] and tp.get("pec12_formaliza"):
        form_inf = (pec12 & (_u(seed, f"pecf:{h}", n) < pec_f))[:, None] & (np.arange(Tn) >= 1)[None]
    formal_w = formal_w * fator_pec
    bruto_trab = (formal_w + np.where(form_inf, sm_dir, renda_trab)) * (1 - perda)
    # --- tributos sobre o trabalho formal
    liq_formal = formal_w * (1 - perda)
    inss_c = inss(liq_formal, idx_inss) if "formal" in tp else 0.0
    ir_f = ir_mensal(liq_formal, inss_c, True, ir_corr) if (tp.get("ir") and "formal" in tp) else 0.0
    liq0_formal = formal0 - (float(inss(np.array([formal0]))[0]) if "formal" in tp else 0.0)
    if tp.get("ir") and "formal" in tp:
        liq0_formal -= float(ir_mensal(np.array([formal0]), inss(np.array([formal0])))[0])
    renda = bruto_trab - formal_w * (1 - perda) + (liq_formal - inss_c - ir_f)
    renda0 = (renda0_trab + liq0_formal) * base_emp
    # abono salarial (formal até 2 SM): 1 SM/ano
    if tp.get("abono"):
        corte_ab = np.clip(ob_abono[:, None] * x_obr / 0.22, 0, 1) if on["fiscal"] else 0.0
        renda = renda + sm_dir / 12 * (1 - corte_ab) * (1 - perda)
        renda0 += SM0 / 12 * base_emp
    # --- aposentadorias
    if "aposentadoria_piso" in tp:
        renda = renda + tp["aposentadoria_piso"] * sm_dir
        renda0 += tp["aposentadoria_piso"] * SM0
    if "aposentadoria_inpc" in tp:
        v0 = tp["aposentadoria_inpc"] * SM0
        renda = renda + v0 * idx_inss
        renda0 += v0
    # --- Bolsa Família (com regra de proteção: renda do trabalho per capita acima da linha → 50%)
    if "bf" in tp:
        bfv = tp["bf"] * (bf if on["fiscal"] else 1.0)
        pc = bruto_trab / tp["tam"]
        lin = bf_linha if on["fiscal"] else BASE["bf_linha_pc"]
        bfv = np.where(pc > lin, 0.5 * bfv, bfv)
        renda = renda + bfv
        renda0 += tp["bf"]
        # outros programas (Gás do Povo, Pé-de-Meia, Farmácia Popular) cortados com a discricionária
        prog = 100.0 * nivel_ipca * (1 - (np.clip(0.5 * x_disc / 1.6, 0, 1) if on["fiscal"] else 0.0))
        renda = renda + prog
        renda0 += 100.0
    # --- topo: perde com receita sobre o topo; ganha se a reversão vier
    if tp.get("reverte_topo") is not None and on["impostos"]:
        topo_perda = TOPO_POR_PP * np.maximum(r_topo, 0) / 100
        renda = renda * (1 - topo_perda) * (1 + tp["reverte_topo"] * rev_topo.astype(float)[:, None] * (np.arange(Tn) >= 1)[None])
    # --- célula de capital: a renda é o retorno real das aplicações (pós-fixado + resto), depois do IR
    if "capital" in tp:
        sa_c = sel_avg if on["juros"] else (np.array([[(CONS["selic_fim"][t] + (BASE["selic_fim_2026"] if t == 0 else CONS["selic_fim"][t - 1])) / 2 for t in range(Tn)]]) + 0 * sel_avg)
        sp_ = tp["pos_fixado"]
        ret_c = sp_ * (sa_c * 0.85 - ipca) + (1 - sp_) * ((ipca + 5.5) * 0.85 - ipca)
        ret_c0 = sp_ * (BASE["selic_media_2026"] * 0.85 - 5.0) + (1 - sp_) * ((5.0 + 5.5) * 0.85 - 5.0)
        renda = renda + tp["capital"] * SM0 * nivel_ipca * ret_c / ret_c0 * cexp
        renda0 += tp["capital"] * SM0
    # --- Lei 15.270 (imposto mínimo e retenção de dividendos): vigente para os dois; a carga efetiva é a
    # estatutária vezes (1 − adaptação); se a reversão vier (programa), a carga some a partir de 2028
    if tp.get("l15270") and on["impostos"]:
        carga = tp["l15270"] * (1 - tp["adapt"])
        ganho = np.where(rev_topo[:, None] & (np.arange(Tn) >= 1)[None], carga / (1 - carga), 0.0)
        renda = renda * (1 + ganho)
    if tp.get("topo_peso") and on["impostos"]:
        renda = renda * (1 - tp["topo_peso"] * (1 - tp["adapt"]) * np.maximum(r_topo, 0) / 100)
    # --- renda financeira (real, depois do IR de 15%)
    fin_r = 0.0
    if tp.get("financeiro"):
        ativos = tp["financeiro"] * 12 * (renda0 if renda0 > 0 else 1.0)
        sa = sel_avg if on["juros"] else (np.array([[(CONS["selic_fim"][t] + (BASE["selic_fim_2026"] if t == 0 else CONS["selic_fim"][t - 1])) / 2 for t in range(Tn)]]) + 0 * sel_avg)
        ret = 0.6 * (sa * 0.85 - ipca) + 0.4 * ((ipca + 5.5) * 0.85 - ipca)
        ret0 = 0.6 * (BASE["selic_media_2026"] * 0.85 - 5.0) + 0.4 * ((5.0 + 5.5) * 0.85 - 5.0)
        fin_r = ativos * nivel_ipca * ret / 100 / 12
        renda = renda + fin_r
        renda0 += ativos * ret0 / 100 / 12
    # --- serviço da dívida: variação por Selic, spread e repactuação
    dv = tp["divida"]
    t_ix = np.arange(Tn)[None]
    dsel = (sel_avg - BASE["selic_media_2026"]) if on["juros"] else (sel_avg * 0 + np.array([[(CONS["selic_fim"][t] + (BASE["selic_fim_2026"] if t == 0 else CONS["selic_fim"][t - 1])) / 2 for t in range(Tn)]]) - BASE["selic_media_2026"])
    soma = np.zeros((n, Tn))
    for l in LINHAS:
        w = dv["mix"].get(l, 0.0)
        if w == 0:
            continue
        rep = np.minimum(1.0, LINHA_REPRECIFICA[l] * (t_ix + 1))
        dtax = LINHA_REPASSE[l] * dsel * rep
        if l in ("cartao", "cheque", "pessoal", "veiculo"):
            if on["impostos"]:
                dtax = dtax - 0.4 * rep_banco[:, None] * rev_banco[:, None] * (t_ix >= 1)
            dtax = dtax + spread_livre * rep
        soma += w * dtax
    estoque = dv["estoque"]
    renda_bruta_nom = np.maximum(renda, 1.0)
    dserv = estoque * soma / 100 * renda_bruta_nom
    # crédito novo às famílias (p.p. do PIB; crédito PF = 35% do PIB, C24) eleva o serviço proporcionalmente
    serv_base = dv["servico"] * renda_bruta_nom * (1 + (cred_cum / 35.0 if on["credito"] else 0.0))
    disp = renda - dserv
    # --- deflatores
    cst = DD.cesta(tp["pof"], tp.get("ne", False))
    wv = np.array([cst[s_] for s_ in SETORES])
    P_of = nivel_set @ wv
    if tp.get("ne"):
        P_of = P_of + wv[IX["SSM"]] * (nivel_ssm_ne - nivel_set[:, :, IX["SSM"]])
    # vivido: reduflação (alimentos e higiene), aluguel de quem muda, plano coletivo — só esses setores mudam
    t1 = np.arange(1, Tn + 1)[None]
    extra = {"A": encolh[:, None], "I": 0.15 * encolh[:, None]}
    if tp.get("inquilino"):
        extra["ALU"] = P["taxa_mudanca"] * alu_mud[:, None]
    if tp.get("plano_coletivo"):
        extra["PLA"] = plano_col[:, None]
    P_viv = P_of.copy()
    for s_, e_ in extra.items():
        P_viv = P_viv + wv[IX[s_]] * nivel_set[:, :, IX[s_]] * ((1 + e_ / 100) ** t1 - 1)
    real = disp / P_of
    idx = 100 * real / renda0
    # vivido: renda livre depois de TODO o serviço da dívida; FGTS valorado (qualidade do emprego)
    fgts = 0.08 * formal_w * (1 - perda) * P["fgts_valor"] if "formal" in tp else 0.0
    fgts0 = 0.08 * formal0 * P["fgts_valor"] * base_emp if "formal" in tp else 0.0
    if "formal" in tp:
        # tributo implícito do FGTS contra o CDI (C13–C16): saldo/renda anual cresce com a renda
        saldo = float(np.interp(np.log(tp["formal"]), np.log([1.0, 1.5, 2.0, 5.0, 10.0, 20.0]), [0.10, 0.12, 0.16, 0.32, 0.49, 0.6]))
        rend = np.maximum(ipca, P["fgts_rend_base"] + 1.9 - (fgts_desc[:, None] if on["credito"] else 1.9))
        rend0 = P["fgts_rend_base"]
        fgts = fgts - saldo * formal_w * (1 - perda) * np.maximum(0.0, sel_avg * 0.85 - rend) / 100
        fgts0 = fgts0 - saldo * formal0 * base_emp * max(0.0, BASE["selic_media_2026"] * 0.85 - rend0) / 100
    livre = disp - serv_base + fgts
    livre0 = renda0 * (1 - dv["servico"]) + fgts0
    idx_viv = 100 * (livre / P_viv) / livre0
    # pobreza: renda per capita real em R$ de 2026
    pc_real = real / tp["tam"]
    # serviços públicos (in natura): perda por cortes em saúde e educação (% da renda)
    inkind = tp.get("in_kind", 0.0) * 100 * (0.5 * x_disc + 0.4 * x_obr) / 2.5 if on["fiscal"] else np.zeros((n, Tn))
    # nível × taxa: renda em "comida de 2019" (só para quem tem renda atrelada ao mínimo)
    comida2019 = None
    if ("aposentadoria_piso" in tp) or (tp.get("formal") == 1.0):
        comida2019 = 100 * (sm_dir / BASE["sm_2019"]) / (BASE["alim_2019_2026"] * nivel_set[:, :, IX["A"]])
    return {"idx": idx, "idx_vivido": idx_viv, "pc_real": pc_real, "inkind": inkind, "renda0": renda0,
            "comida2019": comida2019}


# ---------------------------------------------------------------------------
# Pares e lotes
# ---------------------------------------------------------------------------
def rodar_par(n: int, seed: int, specs: dict, comum: dict | None = None, canais: dict | None = None,
              lote: int = 50_000, tipos=None, fixos: dict | None = None, slots=("1", "2")) -> dict:
    """Roda L (slot "1") e F (slot "2") com os mesmos choques comuns, em lotes de `lote`.
    `slots` iguais = mesmos sorteios de política (experimentos controlados)."""
    out = {"L": [], "F": []}
    k = 0
    while k * lote < n:
        m = min(lote, n - k * lote)
        sd = seed * 1000 + k
        out["L"].append(simular(specs["L"], m, sd, slots[0], comum, canais, fixos, tipos))
        out["F"].append(simular(specs["F"], m, sd, slots[1], comum, canais, fixos, tipos))
        k += 1
    return {c: _juntar(v) for c, v in out.items()}


def _juntar(rs):
    if len(rs) == 1:
        return rs[0]

    def j(objs):
        a = objs[0]
        if isinstance(a, dict):
            return {kk: j([o[kk] for o in objs]) for kk in a}
        if a is None:
            return None
        if isinstance(a, np.ndarray):
            return np.concatenate(objs, axis=0)
        return a
    pesos = [x["regime"].shape[0] for x in rs]
    rp = sum(x["regimes_p"] * w for x, w in zip(rs, pesos)) / sum(pesos)
    for x in rs:
        x["_rp"] = x.pop("regimes_p")
    r = j(rs)
    r.pop("_rp", None)
    r["regimes_p"] = rp
    return r
