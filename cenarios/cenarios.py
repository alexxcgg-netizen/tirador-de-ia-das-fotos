"""Cenários econômicos 2027–2030: poder de compra real das famílias sob cada vencedor
do 2º turno de 2026 (Lula x Flávio Bolsonaro). Monte Carlo anual, vetorizado.

Princípios
----------
* **Mesmas regras para os dois.** A função `simular` é uma só; o que muda entre os
  cenários é apenas o dicionário de parâmetros condicionais (`CANDIDATOS`), tirado
  da tabela 7.2 de `research_notes/Nordeste e cenarios economicos 2026/
  cenarios_economicos_insumos.md`. Nenhum parâmetro é escolhido para favorecer um lado.
* **Números aleatórios comuns.** Cada sorteio tem um fluxo próprio, semeado pelo
  nome (`_u`/`_z`). Os choques exógenos (alimentos, petróleo, IPCA de consenso, PIB,
  elasticidades...) são idênticos nos dois cenários: a diferença Lula − Flávio de uma
  simulação compara "o mesmo mundo com vencedores diferentes". Os sorteios de
  política (persistência do choque, regra do mínimo, IVA, 6x1...) usam fluxos
  próprios de cada candidato, independentes entre si.
* **Âncora no consenso.** O consenso (Focus/IFI) é tratado como média ponderada dos
  dois cenários; os choques do vencedor entram como desvios em relação a ele.
* **Rótulos.** Cada parâmetro tem fonte ou o rótulo `suposição` (sem fonte; entra
  na análise de sensibilidade). Ver `PARAMETROS`.

Unidades: taxas em % ao ano (p.p.), câmbio em R$/US$, dívida em % do PIB.
Ano-base 2026 = dezembro de 2026 (preços) e rendas vigentes em 2026.
"""
from __future__ import annotations

import zlib
from copy import deepcopy

import numpy as np
from scipy.special import ndtri

ANOS = [2027, 2028, 2029, 2030]
T = len(ANOS)

# ---------------------------------------------------------------------------
# Linha de base 2026 (fatos; seção 3.1 dos insumos)
# ---------------------------------------------------------------------------
BASE = {
    "cambio": 5.22,          # PTAX 02/10/2026 (BCB SGS 1)
    "selic_atual": 13.75,    # após o corte de set/2026
    "selic_fim_2026": 13.5,  # Focus 28/09/2026 (C7)
    "desemprego": 5.3,       # PNADC jun–ago/2026
    "renda_mediana": 3777.0, # renda real habitual PNADC jun–ago/2026 (usada como "trabalhador mediano")
    "renda_5_10k": 6500.0,   # [suposição] ponto representativo da faixa R$ 5–10 mil
    "salario_minimo": 1621.0,
    "bolsa_familia": 691.0,  # benefício médio 2026 (economia_fiscal.md)
    "cesta": 779.95,         # DIEESE/Conab, 27 capitais, jun/2026
    "divida": 82.5,          # IFI: DBGG fim de 2026 (82,9% em ago/2026, BC)
    "pib_nominal_tri": 13.4, # R$ tri, PIB nominal implícito (relatório de propostas) [calc]
    "juros_pf": 38.2,        # taxa média PF total, ago/2026 (BCB SGS 20716)
    "comprometimento": 28.7, # serviço da dívida/renda, jul/2026 (BCB SGS 29034)
    "horas_mes": 220.0,      # jornada legal usada pelo DIEESE
}
BASE["horas_cesta"] = BASE["cesta"] / BASE["salario_minimo"] * BASE["horas_mes"]
BASE["cestas_por_sm"] = BASE["salario_minimo"] / BASE["cesta"]

# Trajetórias de consenso (Focus 28/09/2026; 2030 = 2029 [suposição])
CONS = {
    "ipca": np.array([4.31, 3.80, 3.50, 3.50]),
    "selic_fim": np.array([12.0, 10.5, 10.0, 10.0]),
    "cambio": np.array([5.28, 5.30, 5.36, 5.36]),
    "cambio_2026": 5.20,
    "pib": np.array([1.5, 2.0, 2.0, 2.0]),
    "primario_sem_ajuste": np.array([-0.7, -0.6, -0.5, -0.4]),  # IFI 2027 = −0,7; depois [suposição]
}

# Pesos das cestas (IBGE/SIDRA ago/2026, tabelas 7060/7063). Componentes:
# A = alimentação no domicílio; G = combustíveis domésticos (gasolina + diesel + gás de
# botijão); S = serviços (peso [suposição] ~0,35, alvo do efeito da 6x1); R = resto.
PESOS = {
    "ipca": {"A": 0.1542, "G": 0.0514 + 0.0026 + 0.0124, "S": 0.35},
    "inpc": {"A": 0.1889, "G": 0.0482 + 0.0180, "S": 0.35},
    # Família do Bolsa Família: peso maior de alimentos [suposição, ordem de grandeza da POF]
    "bf": {"A": 0.30, "G": 0.07, "S": 0.30},
}
for _k in PESOS:
    PESOS[_k]["R"] = 1.0 - sum(PESOS[_k].values())
PESO_GASOLINA_EM_G = 0.0514 / PESOS["ipca"]["G"]

# ---------------------------------------------------------------------------
# Parâmetros comuns (distribuições). Formatos:
#   número = fixo; ("tri", a, moda, b); ("U", a, b); ("N", média, dp, mín, máx);
#   ("LN", mediana, sigma, mín, máx)
# ---------------------------------------------------------------------------
COMUM = {
    "ipca_2026": ("tri", 4.6, 5.0, 5.4),                 # C1 Focus/IFI
    "ipca_2027": ("tri", 3.6, 4.3, 5.0),                 # C2
    "ipca_2028_30_dp": 1.0,                              # C3 (normal ±1,0)
    "premio_alimentos": ("N", 0.9, 5.1, -7.8, 13.6),     # C4 IBGE 2003–2025 [calc]
    "pib_2026": ("tri", 1.6, 1.9, 2.4),                  # Focus 1,86; BM 1,9; IFI 2,0; FMI 2,4
    "pib_2027": ("tri", 0.2, 1.5, 2.5),                  # C5
    "pib_2028_30": ("tri", 1.0, 2.0, 2.5),               # C6
    "desemprego_2027": ("tri", 5.0, 6.0, 6.7),           # C10
    "renda_real_2027": ("tri", 0.0, 2.0, 3.5),           # C11
    "renda_real_2028_30": ("tri", -0.5, 1.5, 3.0),       # C12 [suposição ancorada]
    "salario_minimo_2027": ("tri", 1735.0, 1741.0, 1750.0),  # C17 PLOA
    "brent_2027": ("LN", 79.0, 0.20, 50.0, 150.0),       # C14 EIA 79; faixa 65–110
    "fracao_bomba": ("tri", 0.0, 0.25, 0.47),            # C15: +8 (0–15)% na bomba ÷ 32% de defasagem [suposição]
    "ruido_cambio_dp": 0.07,                             # ruído cambial anual não explicado [suposição]
    "ruido_selic_dp": 1.0,                               # C8 (faixa 8,5–14) [calc]
    # elasticidades (seção 7.3)
    "e1_12": ("tri", 0.03, 0.10, 0.25),                  # E1
    "e2_12": ("tri", 0.10, 0.26, 0.55),                  # E2
    "e3_12": ("tri", 0.05, 0.18, 0.35),                  # E3 administrados
    "assimetria": ("tri", 0.5, 0.75, 1.0),               # E5 [suposição]
    "selic_ipca": ("tri", 0.15, 0.27, 0.40),             # E6
    "selic_credito": ("U", 1.73 * 0.7, 1.73 * 1.3),      # E7 crédito pessoal ±30%
    "premio_divida": ("tri", 0.03, 0.112, 0.33),         # E8 IFI RAF 116
    "custo_sm_bi": ("U", 0.38, 0.455),                   # E10 R$ bi/ano por R$ 1 de mínimo
    # 6x1 (C13') e PEC 12
    "x6_precos_servicos": ("tri", 0.0, 1.0, 3.0),        # C13' Ipea/Abrasel [calc/opinião]
    "x6_pib_nivel": ("tri", -0.7, -0.2, 0.0),            # CNI −0,7 (opinião); Ipea "pequeno" [suposição na moda]
    "pec12_dp_renda": ("U", 0.03, 0.10),                 # [suposição] variabilidade de renda
    # IVA (F10/F11)
    "iva_leitura": ("U", 0.0, 1.0),                      # 0 = média efetiva (−1,6%; 1,1% PIB) ... 1 = referência (−6,25%; 4,2% PIB)
    "iva_repasse": ("U", 0.5, 1.0),                      # E12/F10 α
    "iva_alimentos": ("U", -0.5, 1.0),                   # fração do efeito que chega à cesta (negativa = cesta encarece) [suposição]
    "iva_fase": {2029: 0.2, 2030: 0.4},                  # transição linear 2029–2033 [suposição]
    # canais sem fonte direta [suposição] — todos na sensibilidade
    "conv_meses": ("U", 12.0, 18.0),                     # L3/F3: convergência em 12–18 meses
    "conv_pior": ("tri", 0.0, 0.0, 0.034),               # L3: "consenso ou pior" (até R$ 5,40); aplicado aos dois
    "acoplamento": 0.5,                                  # peso do estado de credibilidade nos sorteios de Selic e ajuste
    "selic_persistencia": ("U", 0.4, 0.8),               # persistência do desvio da Selic
    "selic_taylor": 0.5,                                 # reação da Selic à surpresa de inflação do ano anterior
    "premio_selic": ("U", 0.25, 0.75),                   # +1 p.p. de prêmio → Selic
    "premio_cambio": ("U", 0.05, 0.15),                  # +1 p.p. de prêmio → câmbio (Goldman: ~80 bps ≈ 8–12%) [calc]
    "pib_selic": ("U", 0.15, 0.45),                      # +1 p.p. Selic → PIB (p.p.)
    "multiplicador": ("U", 0.3, 0.8),                    # multiplicador fiscal do ajuste além do esperado
    "okun": ("U", 0.3, 0.5),                             # Okun
    "salario_pib": ("U", 0.3, 0.7),                      # PIB acima do consenso → salário real
    "indexacao_1": ("U", 0.3, 0.7),                      # repasse da surpresa de inflação ao salário no ano
    "indexacao_2": ("U", 0.2, 0.5),                      # recomposição no ano seguinte (do que faltou)
    "reposicao_desemprego": 0.5,                         # perda esperada de renda por p.p. de desemprego = (1 − 0,5)
    "credito_comprometimento": ("U", 0.1, 0.3),          # p.p. de renda por p.p. de Selic (insumos 5.5, sem fonte)
    "comprometimento_endividado": 0.30,                  # arquétipo 6 (definição: >30%)
    "comprometimento_5_10k": 0.15,                       # arquétipo 5 [suposição]
    "custo_comp_ir": 0.21,                               # R$ 25–31 bi ≈ 0,19–0,23% PIB [calc]
}

# ---------------------------------------------------------------------------
# Parâmetros condicionais ao vencedor (tabela 7.2). Agrupados por canal: os grupos
# são trocados entre os cenários na decomposição "o que move a diferença".
# ---------------------------------------------------------------------------
CANDIDATOS = {
    "L": {
        "nome": "Lula",
        "credibilidade": {
            "choque": ("tri", 0.03, 0.08, 0.15),        # L1: +8% (+3 a +15) sobre R$ 5,22
            "p_persiste": 0.5,                          # L2 [suposição]
            "persistir_e_credivel": False,              # persistir = depreciação mantida (sem ajuste crível)
            "selic_2027": ("tri", 11.0, 12.5, 15.5),    # L4 [suposição de mapeamento]
            "ajuste": ("tri", 0.5, 1.7, 2.5),           # L16 p.p. do PIB até 2030
            "ajuste_meses": 48,
        },
        "minimo": {"p_regra": 1.0},                     # L6 regra INPC + PIB(t−2), teto 2,5
        "bolsa": {"real": ("tri", 0.0, 1.0, 3.0)},      # L7 [suposição]
        "ir": {"p_mantida": 1.0, "p_comp_revogada": 0.0},  # L8
        "iva": {"p": 0.0},
        "trabalho": {"p_6x1": 0.55, "p_pec12": 0.0},    # L12
        "combustivel": {"frac_2027": 0.5, "corte_trib": 0.0,
                        "custo_2027": ("tri", 0.05, 0.15, 0.30), "custo_perm": 0.0},  # L15
    },
    "F": {
        "nome": "Flávio Bolsonaro",
        "credibilidade": {
            "choque": ("tri", -0.14, -0.07, -0.04),     # F1: −7% (−14 a −4)
            "p_persiste": 0.5,                          # F2 [suposição]
            "persistir_e_credivel": True,               # persistir = entrega o ajuste antes/junto dos cortes
            "selic_2027": ("tri", 9.75, 11.0, 12.5),    # F4 [suposição de mapeamento]
            "ajuste": ("tri", 0.5, 1.5, 3.0),           # F16 p.p. do PIB em 18 meses
            "ajuste_meses": 18,
        },
        "minimo": {"p_regra": 0.65},                    # F6: P = 0,35 → só INPC a partir de 2028 [suposição]
        "bolsa": {"real": ("tri", -2.0, 0.0, 1.0)},     # F7 [suposição]
        "ir": {"p_mantida": 0.9, "p_comp_revogada": 0.3},  # F8 [suposição]
        "iva": {"p": 0.2},                              # F9 [suposição]
        "trabalho": {"p_6x1": 0.45, "p_pec12": 0.25},   # F12, F14 [suposição]
        "combustivel": {"frac_2027": 1.0, "corte_trib": ("tri", 4.8, 7.1, 9.5),  # R$ 0,3–0,6/l ÷ ~R$ 6,3/l [calc]
                        "custo_2027": 0.0, "custo_perm": ("tri", 0.2, 0.25, 0.3)},  # corte (0,1–0,2) + fim do imposto de exportação (~0,1) [suposição]
    },
}
GRUPOS = ["credibilidade", "minimo", "bolsa", "ir", "iva", "trabalho", "combustivel"]
GRUPO_NOME = {
    "credibilidade": "Câmbio, juros e ajuste fiscal (credibilidade)",
    "minimo": "Regra do salário mínimo",
    "bolsa": "Reajuste do Bolsa Família",
    "ir": "Isenção do IR e compensação",
    "iva": "IVA de 20%",
    "trabalho": "6x1 e contrato por hora",
    "combustivel": "Política de combustíveis",
}
# Eventos binários de cada cenário (definem as "células" usadas na reponderação no navegador)
EVENTOS = {"L": ["persiste", "x6"], "F": ["persiste", "regra_sm", "iva", "x6", "pec12"]}

ARQUETIPOS = {
    "sm": "Trabalhador formal com 1 salário mínimo",
    "aposentado": "Aposentado ou BPC no piso",
    "bf": "Família no Bolsa Família (renda = benefício)",
    "mediano": "Trabalhador mediano (R$ 3.777)",
    "faixa": "Renda de R$ 5–10 mil (R$ 6.500)",
    "endividado": "Família endividada (30% da renda em dívidas)",
}

# ---------------------------------------------------------------------------
# Sorteios com números aleatórios comuns
# ---------------------------------------------------------------------------
_EPS = 1e-12


def _seed(seed: int, nome: str):
    return np.random.default_rng(np.random.SeedSequence([seed, zlib.crc32(nome.encode())]))


def _u(seed, nome, n):
    return _seed(seed, nome).random(n)


def tri_ppf(u, a, m, b):
    u = np.asarray(u, dtype=float)
    if b - a < _EPS:
        return np.full_like(u, a)
    fc = (m - a) / (b - a)
    return np.where(u < fc, a + np.sqrt(u * (b - a) * (m - a)),
                    b - np.sqrt((1 - u) * (b - a) * (b - m)))


def amostrar(spec, u):
    """Transforma uniformes `u` segundo `spec` (ver formatos em COMUM)."""
    u = np.clip(np.asarray(u, dtype=float), 1e-9, 1 - 1e-9)
    if isinstance(spec, (int, float)):
        return np.full(u.shape, float(spec))
    kind = spec[0]
    if kind == "tri":
        return tri_ppf(u, *spec[1:])
    if kind == "U":
        return spec[1] + (spec[2] - spec[1]) * u
    if kind == "N":
        return np.clip(spec[1] + spec[2] * ndtri(u), spec[3], spec[4])
    if kind == "LN":
        return np.clip(spec[1] * np.exp(spec[2] * ndtri(u)), spec[3], spec[4])
    raise ValueError(spec)


def media_spec(spec):
    if isinstance(spec, (int, float)):
        return float(spec)
    k = spec[0]
    if k == "tri":
        return sum(spec[1:4]) / 3
    if k == "U":
        return (spec[1] + spec[2]) / 2
    return spec[1]


# ---------------------------------------------------------------------------
# Tributos (tabelas de 2026, nominais e congeladas [suposição: sem correção])
# ---------------------------------------------------------------------------
IR_FAIXAS = [(2428.80, 0.0, 0.0), (2826.65, 0.075, 182.16), (3751.05, 0.15, 394.16),
             (4664.68, 0.225, 675.49), (np.inf, 0.275, 908.73)]
IR_DESCONTO_SIMPLIFICADO = 607.20
INSS_FAIXAS = [(1621.00, 0.075), (2902.84, 0.09), (4354.27, 0.12), (8475.55, 0.14)]


def inss(renda, indice=1.0):
    """Contribuição do empregado (tabela progressiva 2026 [aproximação]), faixas
    corrigidas por `indice` (INPC acumulado)."""
    renda = np.asarray(renda, dtype=float)
    total = np.zeros_like(renda)
    piso = 0.0
    for teto, aliq in INSS_FAIXAS:
        teto_i = teto * indice
        total += np.clip(np.minimum(renda, teto_i) - piso, 0, None) * aliq
        piso = teto_i
    return total


def ir_mensal(renda, contrib, reducao=True):
    """IRPF mensal: tabela de mai/2025 + redução da Lei 15.270/2025 (isenção até
    R$ 5 mil; redução parcial de R$ 978,62 − 0,133145 × renda até R$ 7.350)."""
    renda = np.asarray(renda, dtype=float)
    base = renda - np.maximum(contrib, IR_DESCONTO_SIMPLIFICADO)
    imposto = np.zeros_like(renda)
    lim_inf = 0.0
    for teto, aliq, ded in IR_FAIXAS:
        faixa = (base > lim_inf) & (base <= teto)
        imposto = np.where(faixa, base * aliq - ded, imposto)
        lim_inf = teto
    imposto = np.maximum(imposto, 0.0)
    red = np.where(renda <= 5000.0, 312.89,
                   np.where(renda <= 7350.0, np.maximum(978.62 - 0.133145 * renda, 0.0), 0.0))
    red = np.where(reducao, red, 0.0)
    return np.maximum(imposto - red, 0.0)


def renda_liquida(renda, indice=1.0, reducao=True):
    c = inss(renda, indice)
    return renda - c - ir_mensal(renda, c, reducao)


# ---------------------------------------------------------------------------
# Calibração da taxa implícita da dívida: reproduz a DBGG de 86,4% em 2027 (IFI)
# no cenário de consenso sem ajuste novo.
# ---------------------------------------------------------------------------
PARCELA_SELIC = 0.464  # títulos atrelados à Selic na DPF (IFI RAF 116)


def _calibrar_k():
    s_avg = (BASE["selic_fim_2026"] + CONS["selic_fim"][0]) / 2
    pi, g = CONS["ipca"][0] / 100, CONS["pib"][0] / 100
    gn = (1 + g) * (1 + pi) - 1
    alvo = 86.4 + CONS["primario_sem_ajuste"][0]  # d27 + pb = d26 (1+i)/(1+gn)
    i = alvo / BASE["divida"] * (1 + gn) - 1
    return (i - PARCELA_SELIC * s_avg / 100) / (1 - PARCELA_SELIC) - pi


K_JURO_REAL = _calibrar_k()

# Ajuste fiscal "esperado" pelo consenso: média das trajetórias modais declaradas [calc]


def _traj_ajuste(total, meses):
    frac = np.minimum(1.0, 12.0 * np.arange(1, T + 1) / meses)
    return np.multiply.outer(np.asarray(total, dtype=float), frac)


AJUSTE_REF = 0.5 * (_traj_ajuste(1.7, 48) + _traj_ajuste(1.5, 18))


# ---------------------------------------------------------------------------
# Simulação
# ---------------------------------------------------------------------------
def montar_spec(base: str, trocas: dict | None = None) -> dict:
    """Cópia da especificação do candidato `base` com grupos trocados (decomposição)."""
    spec = deepcopy(CANDIDATOS[base])
    for grupo, origem in (trocas or {}).items():
        spec[grupo] = deepcopy(CANDIDATOS[origem][grupo])
    return spec


def simular(spec: dict, n: int, seed: int, tag: str, comum: dict | None = None,
            divida_esperada=None, fixos: dict | None = None) -> dict:
    """Simula `n` trajetórias 2027–2030 para um vencedor.

    spec: parâmetros condicionais (ver CANDIDATOS); tag: fluxo aleatório dos sorteios
    de política ("L" ou "F"); comum: substituições em COMUM (sensibilidade);
    divida_esperada: trajetória (T,) que o mercado espera para este vencedor — o
    prêmio de risco reage só a surpresas em relação a ela (None = sem realimentação);
    fixos: força eventos binários (ex.: {"iva": 1}).
    """
    P = dict(COMUM)
    P.update(comum or {})
    fixos = fixos or {}
    cr = spec["credibilidade"]

    def d(nome, spec_):
        return amostrar(spec_, _u(seed, nome, n))

    def evento(nome, p):
        if nome in fixos:
            return np.full(n, bool(fixos[nome]))
        return _u(seed, f"{tag}:{nome}", n) < p

    # ---- sorteios exógenos (comuns aos dois cenários)
    ipca26 = d("ipca_2026", P["ipca_2026"])
    pib26 = d("pib_2026", P["pib_2026"])
    ipca_c = np.empty((n, T))
    ipca_c[:, 0] = d("ipca_2027", P["ipca_2027"])
    for t in range(1, T):
        ipca_c[:, t] = amostrar(("N", CONS["ipca"][t], P["ipca_2028_30_dp"], 1.0, 8.0),
                                _u(seed, f"ipca_{ANOS[t]}", n))
    premio = np.stack([d(f"premio_alimentos_{a}", P["premio_alimentos"]) for a in ANOS], 1)
    pib_c = np.stack([d("pib_2027", P["pib_2027"])] +
                     [d(f"pib_{a}", P["pib_2028_30"]) for a in ANOS[1:]], 1)
    renda_real = np.stack([d("renda_real_2027", P["renda_real_2027"])] +
                          [d(f"renda_real_{a}", P["renda_real_2028_30"]) for a in ANOS[1:]], 1)
    u27 = d("desemprego_2027", P["desemprego_2027"])
    sm27 = d("salario_minimo_2027", P["salario_minimo_2027"])
    brent = d("brent_2027", P["brent_2027"])
    fbomba = d("fracao_bomba", P["fracao_bomba"])
    ruido_fx = np.stack([amostrar(("N", 0.0, P["ruido_cambio_dp"], -1, 1), _u(seed, f"fx_{a}", n))
                         for a in ANOS], 1)
    ruido_sel = np.stack([amostrar(("N", 0.0, P["ruido_selic_dp"], -5, 5), _u(seed, f"sel_{a}", n))
                          for a in ANOS], 1)
    ue = _u(seed, "elasticidades", n)  # repasses comonotônicos [suposição]
    e1 = amostrar(P["e1_12"], ue)
    e2 = amostrar(P["e2_12"], ue)
    e3 = amostrar(P["e3_12"], ue)
    r24_1, r24_2 = 0.16 / 0.10, 0.33 / 0.26
    assim = d("assimetria", P["assimetria"])
    e6 = d("selic_ipca", P["selic_ipca"])
    e7 = d("selic_credito", P["selic_credito"])
    e8 = d("premio_divida", P["premio_divida"])
    custo_sm = d("custo_sm_bi", P["custo_sm_bi"])
    x6_p = d("x6_precos_servicos", P["x6_precos_servicos"])
    x6_g = d("x6_pib_nivel", P["x6_pib_nivel"])
    pec_dp = d("pec12_dp_renda", P["pec12_dp_renda"])
    pec_z = ndtri(np.clip(_u(seed, "pec12_z", n), 1e-9, 1 - 1e-9))
    iva_l = d("iva_leitura", P["iva_leitura"])
    iva_mag = -(1.6 + (6.25 - 1.6) * iva_l)      # % nos bens tributados (sistema pleno)
    iva_custo = 1.1 + (4.2 - 1.1) * iva_l        # % do PIB/ano (sistema pleno), comonotônico
    iva_rep = d("iva_repasse", P["iva_repasse"])
    iva_alim = d("iva_alimentos", P["iva_alimentos"])
    conv = d("conv_meses", P["conv_meses"])
    conv_pior = d("conv_pior", P["conv_pior"])
    rho_s = d("selic_persistencia", P["selic_persistencia"])
    lam_s = d("premio_selic", P["premio_selic"])
    lam_x = d("premio_cambio", P["premio_cambio"])
    beta = d("pib_selic", P["pib_selic"])
    mult = d("multiplicador", P["multiplicador"])
    okun = d("okun", P["okun"])
    gam = d("salario_pib", P["salario_pib"])
    th1 = d("indexacao_1", P["indexacao_1"])
    th2 = d("indexacao_2", P["indexacao_2"])
    kap = d("credito_comprometimento", P["credito_comprometimento"])
    acop = float(P["acoplamento"])

    # ---- sorteios de política (fluxo próprio do candidato)
    persiste = evento("persiste", cr["p_persiste"])
    credivel = persiste if cr["persistir_e_credivel"] else ~persiste
    choque = amostrar(cr["choque"], _u(seed, f"{tag}:choque", n))
    u_sel = acop * (~credivel) + (1 - acop) * _u(seed, f"{tag}:selic", n)
    selic27 = amostrar(cr["selic_2027"], u_sel)
    u_aj = acop * credivel + (1 - acop) * _u(seed, f"{tag}:ajuste", n)
    ajuste = _traj_ajuste(amostrar(cr["ajuste"], u_aj), cr["ajuste_meses"])
    regra_sm = evento("regra_sm", spec["minimo"]["p_regra"])
    bf_real = amostrar(spec["bolsa"]["real"], _u(seed, f"{tag}:bf", n))
    ir_mantida = evento("ir_mantida", spec["ir"]["p_mantida"])
    comp_rev = evento("comp_revogada", spec["ir"]["p_comp_revogada"])
    iva = evento("iva", spec["iva"]["p"])
    x6 = evento("x6", spec["trabalho"]["p_6x1"])
    pec12 = evento("pec12", spec["trabalho"]["p_pec12"])
    cb = spec["combustivel"]
    corte_trib = amostrar(cb["corte_trib"], _u(seed, f"{tag}:corte_trib", n))
    custo_comb27 = amostrar(cb["custo_2027"], _u(seed, f"{tag}:custo_comb27", n))
    custo_comb = amostrar(cb["custo_perm"], _u(seed, f"{tag}:custo_comb", n))

    # ---- câmbio: desvio log em relação ao consenso (média do ano)
    x_ini = np.log(BASE["cambio"] * (1 + choque) / CONS["cambio"][0])
    x_alvo = np.log1p(conv_pior)
    rest27 = 1 - 6.0 / conv                      # fração média do choque que resta em 2027
    rest28 = (conv - 12.0) ** 2 / (24.0 * conv)  # idem em 2028
    xc = np.empty((n, T))
    pers_dir = persiste  # "persistir" = choque de impacto mantido
    xc[:, 0] = np.where(pers_dir, x_ini, x_alvo + (x_ini - x_alvo) * rest27)
    xc[:, 1] = np.where(pers_dir, x_ini, x_alvo + (x_ini - x_alvo) * rest28)
    xc[:, 2] = np.where(pers_dir, x_ini, x_alvo)
    xc[:, 3] = xc[:, 2]

    # ---- estados
    w = {k: PESOS[k] for k in PESOS}
    wI = w["ipca"]
    sel_fim = np.empty((n, T)); sel_avg = np.empty((n, T))
    x = np.empty((n, T)); fx = np.empty((n, T))
    infl = {k: np.empty((n, T)) for k in ("A", "G", "S", "R", "ipca", "inpc", "bf")}
    pib = np.empty((n, T)); desemp = np.empty((n, T)); divida = np.empty((n, T))
    primario = np.empty((n, T)); sm = np.empty((n, T)); sm_regra = np.empty((n, T))
    bfb = np.empty((n, T)); salario = np.empty((n, T)); juros_pf = np.empty((n, T))
    premio_risco = np.zeros((n, T))
    surpresa_prev = np.zeros(n)
    dev_fim_prev = np.zeros(n); dev_avg_prev = np.zeros(n)
    dx_prev = np.zeros(n); x_prev = np.zeros(n)
    fb = np.zeros(n)            # realimentação cambial acumulada
    rw = np.zeros(n)            # passeio aleatório cambial comum
    d_prev = np.full(n, BASE["divida"])
    u_prev = np.full(n, BASE["desemprego"])
    sm_prev = np.full(n, BASE["salario_minimo"]); smr_prev = sm_prev.copy()
    bf_prev = np.full(n, BASE["bolsa_familia"])
    sal_prev = np.full(n, BASE["renda_mediana"])
    inpc_prev = ipca26.copy()   # INPC 2026 ≈ IPCA 2026 [suposição]
    pibs = [pib26]              # PIB de t−2 para a regra do mínimo
    pibn_prev = BASE["pib_nominal_tri"]
    aj_prev = np.zeros(n); ref_prev = 0.0
    gap_need = None
    e_r = lambda ea, eg: np.maximum(0.0, (ea - wI["A"] * eg[0] - wI["G"] * eg[1] - wI["S"] * 0.02) / wI["R"])
    e_r12 = e_r(e1, (e2, e3))
    e_r24 = e_r(e1 * r24_1, (e2 * r24_2, e3 * r24_1))

    def repasse(e12, e24, dx_t, dx_p):
        a_t = np.where(dx_t < 0, assim, 1.0)
        a_p = np.where(dx_p < 0, assim, 1.0)
        return 100 * (e12 * a_t * dx_t + (e24 - e12) * a_p * dx_p)

    for t, ano in enumerate(ANOS):
        # 1. prêmio de risco: surpresa da dívida do ano anterior
        if divida_esperada is not None and t > 0:
            premio_risco[:, t] = e8 * (d_prev - divida_esperada[t - 1])
        pr = premio_risco[:, t]
        # 2. Selic
        if t == 0:
            sel_fim[:, t] = selic27
        else:
            sel_fim[:, t] = (CONS["selic_fim"][t] + rho_s * dev_fim_prev + lam_s * pr
                             + P["selic_taylor"] * surpresa_prev + ruido_sel[:, t])
        sel_fim[:, t] = np.clip(sel_fim[:, t], 5.0, 22.0)
        dev_fim = sel_fim[:, t] - CONS["selic_fim"][t]
        sel_avg[:, t] = (sel_fim[:, t] + (BASE["selic_fim_2026"] if t == 0 else sel_fim[:, t - 1])) / 2
        cons_avg = (CONS["selic_fim"][t] + (BASE["selic_fim_2026"] if t == 0 else CONS["selic_fim"][t - 1])) / 2
        dev_avg = sel_avg[:, t] - cons_avg
        # 3. câmbio
        rw = rw + ruido_fx[:, t]
        fb = fb + lam_x * pr
        x[:, t] = xc[:, t] + rw + fb
        fx[:, t] = CONS["cambio"][t] * np.exp(x[:, t])
        dx = x[:, t] - x_prev
        # 4. inflação por componente
        c = ipca_c[:, t] - wI["A"] * media_spec(P["premio_alimentos"])
        sel_ef = -e6 * (0.4 * dev_avg + 0.6 * dev_avg_prev)
        # combustíveis: realinhamento (comum) com calendário do vencedor
        if t == 0:
            gap = 1.32 * (brent / 100) * (fx[:, 0] / BASE["cambio"]) - 1
            gap_need = 100 * fbomba * np.maximum(gap, 0.0)
        frac = cb["frac_2027"] if t == 0 else (1 - cb["frac_2027"] if t == 1 else 0.0)
        comb = frac * gap_need - (PESO_GASOLINA_EM_G * corte_trib if t == 0 else 0.0)
        # IVA
        fase = P["iva_fase"].get(ano, 0.0) - P["iva_fase"].get(ano - 1, 0.0)
        iva_ef = np.where(iva, fase * iva_mag * iva_rep, 0.0)
        # 6x1: metade em 2027, metade em 2028
        x6_ef = np.where(x6, x6_p * 0.5, 0.0) if t < 2 else np.zeros(n)
        infl["A"][:, t] = c + premio[:, t] + repasse(e2, e2 * r24_2, dx, dx_prev) + sel_ef + iva_alim * iva_ef
        infl["G"][:, t] = c + repasse(e3, e3 * r24_1, dx, dx_prev) + sel_ef + comb
        infl["S"][:, t] = c + repasse(0.02, 0.03, dx, dx_prev) + sel_ef + x6_ef + iva_ef
        infl["R"][:, t] = c + repasse(e_r12, e_r24, dx, dx_prev) + sel_ef + iva_ef
        for cesta in ("ipca", "inpc", "bf"):
            infl[cesta][:, t] = sum(w[cesta][k] * infl[k][:, t] for k in "AGSR")
        surpresa = infl["ipca"][:, t] - CONS["ipca"][t]
        # 5. PIB e desemprego
        ref_t = AJUSTE_REF[t]
        dajuste = (ajuste[:, t] - aj_prev) - (ref_t - ref_prev)
        x6_pib = np.where(x6, x6_g * 0.5, 0.0) if t < 2 else 0.0
        pib[:, t] = pib_c[:, t] - beta * (0.3 * dev_avg + 0.7 * dev_avg_prev) - mult * dajuste + x6_pib
        if t == 0:
            desemp[:, t] = u27 - okun * (pib[:, t] - pib_c[:, t])
        else:
            desemp[:, t] = u_prev - okun * (pib[:, t] - 2.0)
        desemp[:, t] = np.clip(desemp[:, t], 3.0, 20.0)
        # 6. salário mínimo (regra: INPC(t−1) + PIB(t−2), teto 2,5, sem ganho negativo)
        ganho = np.clip(pibs[-1] if t > 0 else 0.0, 0.0, 2.5)
        if t == 0:
            sm[:, t] = sm27; sm_regra[:, t] = sm27
        else:
            smr = smr_prev * (1 + inpc_prev / 100) * (1 + ganho / 100)
            sm[:, t] = np.where(regra_sm, sm_prev * (1 + inpc_prev / 100) * (1 + ganho / 100),
                                sm_prev * (1 + inpc_prev / 100))
            sm_regra[:, t] = smr
        # 7. Bolsa Família: INPC passado + reajuste real
        bfb[:, t] = bf_prev * (1 + inpc_prev / 100) * (1 + bf_real / 100)
        # 8. salário mediano: inflação esperada + repasse parcial da surpresa + ganho real
        cresc = (CONS["ipca"][t] + th1 * surpresa + th2 * (1 - th1) * surpresa_prev
                 + renda_real[:, t] + gam * (pib[:, t] - pib_c[:, t]))
        salario[:, t] = sal_prev * (1 + cresc / 100)
        # 9. fiscal e dívida
        pibn = pibn_prev * (1 + pib[:, t] / 100) * (1 + infl["ipca"][:, t] / 100)
        economia_sm = (sm_regra[:, t] - sm[:, t]) * custo_sm / (pibn * 1000) * 100
        custo_iva = np.where(iva, P["iva_fase"].get(ano, 0.0) * iva_custo, 0.0)
        custo_ir = (np.where(comp_rev, P["custo_comp_ir"], 0.0) - np.where(~ir_mantida, P["custo_comp_ir"], 0.0)) if t > 0 else 0.0
        custo_c = (custo_comb27 if t == 0 else 0.0) + custo_comb
        primario[:, t] = (CONS["primario_sem_ajuste"][t] + ajuste[:, t] - custo_iva - custo_ir
                          - custo_c + economia_sm)
        i_ef = PARCELA_SELIC * sel_avg[:, t] / 100 + (1 - PARCELA_SELIC) * (infl["ipca"][:, t] / 100 + K_JURO_REAL)
        gn = (1 + pib[:, t] / 100) * (1 + infl["ipca"][:, t] / 100) - 1
        divida[:, t] = d_prev * (1 + i_ef) / (1 + gn) - primario[:, t]
        juros_pf[:, t] = BASE["juros_pf"] + e7 * (sel_avg[:, t] - BASE["selic_atual"])
        # avança
        d_prev = divida[:, t]; u_prev = desemp[:, t]; sm_prev = sm[:, t]; smr_prev = sm_regra[:, t]
        bf_prev = bfb[:, t]; sal_prev = salario[:, t]; inpc_prev = infl["inpc"][:, t]
        pibs.append(pib[:, t]); pibn_prev = pibn; aj_prev = ajuste[:, t]; ref_prev = ref_t
        surpresa_prev = surpresa; dev_fim_prev = dev_fim; dev_avg_prev = dev_avg
        dx_prev = dx; x_prev = x[:, t]

    # ---- índices de preço e poder de compra (2026 = 100)
    preco = {k: np.cumprod(1 + infl[k] / 100, axis=1) for k in ("A", "ipca", "inpc", "bf")}
    cesta = BASE["cesta"] * preco["A"]
    idx_inss = np.cumprod(1 + np.column_stack([ipca26, infl["inpc"][:, :-1]]) / 100, axis=1)
    ir_red = np.column_stack([np.ones(n, bool)] + [ir_mantida] * (T - 1))
    fu = 1 - (1 - P["reposicao_desemprego"]) * (desemp - BASE["desemprego"]) / 100
    pec_fator = np.where(pec12[:, None] & (np.arange(T) >= 1)[None, :],
                         np.exp(pec_dp[:, None] * pec_z[:, None] - 0.5 * pec_dp[:, None] ** 2), 1.0)
    fator_sal = salario / BASE["renda_mediana"]
    liq0_med = renda_liquida(BASE["renda_mediana"])
    liq0_faixa = renda_liquida(BASE["renda_5_10k"])
    liq_med = renda_liquida(salario, idx_inss, ir_red)
    liq_faixa = renda_liquida(BASE["renda_5_10k"] * fator_sal, idx_inss, ir_red)
    dsel = sel_avg - BASE["selic_atual"]
    ds_end = P["comprometimento_endividado"] + kap[:, None] * dsel / 100
    ds_faixa = P["comprometimento_5_10k"] + 0.5 * kap[:, None] * dsel / 100
    pp = {
        "sm": 100 * (sm / BASE["salario_minimo"]) * fu * pec_fator / preco["inpc"],
        "aposentado": 100 * (sm / BASE["salario_minimo"]) / preco["inpc"],
        "bf": 100 * (bfb / BASE["bolsa_familia"]) / preco["bf"],
        "mediano": 100 * (liq_med / liq0_med) * fu / preco["ipca"],
        "faixa": 100 * (liq_faixa / liq0_faixa) * fu * (1 - ds_faixa) / (1 - P["comprometimento_5_10k"]) / preco["ipca"],
        "endividado": 100 * (liq_med / liq0_med) * fu * (1 - ds_end) / (1 - P["comprometimento_endividado"]) / preco["ipca"],
    }
    return {
        "pp": pp,
        "horas_cesta": cesta / sm * BASE["horas_mes"],
        "cestas_sm": sm / cesta,
        "macro": {
            "ipca": infl["ipca"], "alimentos": infl["A"], "inpc": infl["inpc"],
            "selic": sel_fim, "cambio": fx, "divida": divida, "desemprego": desemp,
            "pib": pib, "sm_real": 100 * (sm / BASE["salario_minimo"]) / preco["inpc"],
            "juros_pf": juros_pf, "primario": primario, "premio": premio_risco,
        },
        "eventos": {"persiste": persiste, "x6": x6, "regra_sm": regra_sm, "iva": iva,
                    "pec12": pec12, "ir_mantida": ir_mantida, "comp_revogada": comp_rev},
    }


def rodar_cenario(spec: dict, n: int, seed: int, tag: str, comum: dict | None = None,
                  fixos: dict | None = None) -> dict:
    """Duas passagens: (1) sem realimentação, para obter a dívida que o mercado
    espera deste vencedor (média); (2) com o prêmio reagindo a surpresas de dívida."""
    r1 = simular(spec, n, seed, tag, comum, None, fixos)
    esperada = r1["macro"]["divida"].mean(axis=0)
    r2 = simular(spec, n, seed, tag, comum, esperada, fixos)
    r2["divida_esperada"] = esperada
    return r2


def rodar_par(n: int, seed: int, comum: dict | None = None, specs: dict | None = None) -> dict:
    specs = specs or {"L": CANDIDATOS["L"], "F": CANDIDATOS["F"]}
    return {k: rodar_cenario(specs[k], n, seed, k, comum) for k in ("L", "F")}


# ---------------------------------------------------------------------------
# Catálogo de premissas (vai para o JSON e para a página)
# ---------------------------------------------------------------------------
PARAMETROS = [
    # id, nome, Lula, Flávio (ou comum), fonte, tipo
    ("C1–C3", "IPCA de consenso 2026/2027/2028–30", "5,0 / 4,3 (3,6–5,0) / 3,8–3,5 ±1,0", "comum", "Focus 28/09/2026; IFI RAF 116", "projeção"),
    ("C4", "Alimentação no domicílio − IPCA (p.p./ano)", "+0,9, dp 5,1, entre −7,8 e +13,6", "comum", "IBGE 2003–2025 [calc]", "fonte"),
    ("C5–C6", "PIB 2027 / 2028–30 (%)", "1,5 (0,2–2,5) / 2,0 (1,0–2,5)", "comum", "Focus, IFI, Banco Mundial, FMI, MS", "projeção"),
    ("C7–C8", "Selic de consenso (fim de ano)", "13,5 / 12,0 / 10,5 / 10,0 / 10,0; ruído dp 1,0", "comum", "Focus; 2030 = 2029 [suposição]", "projeção"),
    ("C9", "Dólar de consenso", "5,28 / 5,30 / 5,36 / 5,36", "comum", "Focus; 2030 = 2029 [suposição]", "projeção"),
    ("C10", "Desemprego 2027 (%)", "6,0 (5,0–6,7)", "comum", "PNADC; MS; moda [suposição]", "projeção"),
    ("C11–C12", "Renda real por ocupado 2027 / 2028–30 (%)", "+2,0 (0–3,5) / +1,5 (−0,5–3,0)", "comum", "IFI [calc]; 2028–30 [suposição]", "suposição"),
    ("C13", "Dívida bruta 2027 (% PIB)", "86,4 (calibra a taxa implícita)", "comum", "IFI RAF 116", "projeção"),
    ("C14", "Brent 2027 (US$)", "79 (lognormal, 65–110)", "comum", "EIA; PLOA", "projeção"),
    ("C15", "Fração da defasagem da refinaria que chega à bomba", "0,25 (0–0,47)", "comum", "Abicom 32%; fração [suposição]", "suposição"),
    ("C17", "Salário mínimo 2027 (R$)", "1.741 (1.735–1.750)", "comum", "PLOA 2027", "fonte"),
    ("L1/F1", "Choque cambial de impacto (sobre R$ 5,22)", "+8% (+3 a +15)", "−7% (−14 a −4)", "JPMorgan, Goldman, Wells Fargo, BTG", "projeção"),
    ("L2/F2", "P(choque cambial persiste 12 meses)", "0,5", "0,5", "valores sem fonte; Goldman: 'as políticas, mais que o resultado'", "suposição"),
    ("L3/F3", "Se não persistir: converge para", "consenso até +3,4% (R$ 5,40), em 12–18 meses", "idem (mesma regra)", "Goldman (R$ 5,40); aplicar aos dois [suposição]", "suposição"),
    ("L4/F4", "Selic fim de 2027 (%)", "12,5 (11–15,5)", "11,0 (9,75–12,5)", "Morgan Stanley, JPMorgan; mapeamento por candidato [suposição]", "suposição"),
    ("L6/F6", "Ganho real do mínimo", "regra (PIB t−2, teto 2,5%)", "regra com P = 0,65; só INPC a partir de 2028 com P = 0,35", "Lei 14.663; declarações; P [suposição]", "suposição"),
    ("L7/F7", "Bolsa Família: reajuste real (%/ano)", "+1 (0 a +3)", "0 (−2 a +1)", "propostas; valores [suposição]", "suposição"),
    ("L8/F8", "Isenção do IR até R$ 5 mil mantida", "P = 1", "P = 0,9 (compensação revogada P = 0,3)", "Lei 15.270; P [suposição]", "suposição"),
    ("F9", "IVA de 20% aprovado até 2030", "—", "P = 0,2", "[suposição]", "suposição"),
    ("F10–F11", "Efeito do IVA (sistema pleno) e custo fiscal", "—", "−1,6% a −6,25% × repasse 0,5–1,0; 1,1–4,2% do PIB; 20% em 2029, 40% em 2030", "Borges/IBRE; Benzarti; Portugal 2023; fase [suposição]", "calc"),
    ("L12/F12", "Fim da 6x1 promulgado", "P = 0,55", "P = 0,45", "[suposição]", "suposição"),
    ("C13'", "6x1: preços de serviços em 2 anos / PIB (nível)", "+1% (0–3) / −0,2% (−0,7–0)", "idem", "Ipea, Abrasel, CNI [calc/opinião]", "suposição"),
    ("F14", "PEC 12/2026 (contrato por hora) aprovada", "—", "P = 0,25; renda do trabalhador de 1 SM ganha ruído de dp 3–10%", "DIEESE (58% do SM); P e dp [suposição]", "suposição"),
    ("L15/F15", "Combustíveis", "realinhamento 50% em 2027 e 50% em 2028, com subsídio (0,05–0,3% PIB em 2027)", "realinhamento em 2027; corte de tributos de 4,8–9,5% na gasolina; custo 0,2–0,3% PIB/ano", "MP 1.340; plano; calendário e custos [suposição]", "suposição"),
    ("L16/F16", "Ajuste primário (p.p. do PIB)", "+1,7 (0,5–2,5) até 2030", "+1,5 (0,5–3,0) em 18 meses, menos o custo do IVA se aprovado", "Forbes (declarações de campanha)", "projeção"),
    ("E1–E4", "Repasse cambial (12m): IPCA / alimentos / administrados", "0,10 / 0,26 / 0,18 (24m: 0,16 / 0,33)", "comum", "BCB RPM mar/2026", "fonte"),
    ("E5", "Assimetria (apreciação ÷ depreciação)", "0,75 (0,5–1,0)", "comum", "[suposição]; PUC-Rio, FEE", "suposição"),
    ("E6", "Selic +1 p.p. → IPCA", "−0,27 p.p. (−0,15 a −0,40)", "comum", "BCB RI jun/2024", "fonte"),
    ("E7", "Selic → taxa de crédito pessoal", "1,73 (±30%)", "comum", "BCB EE 118/2022", "fonte"),
    ("E8", "Dívida +1 p.p. PIB → prêmio", "0,112 (0,03–0,33)", "comum", "IFI RAF 116", "fonte"),
    ("E10", "Custo fiscal por R$ 1 de mínimo", "R$ 0,38–0,455 bi/ano", "comum", "DIEESE; SpaceMoney", "fonte"),
    ("M1", "Prêmio → câmbio / → Selic", "5–15% / 0,25–0,75 por p.p.", "comum", "ordem de grandeza do Goldman [calc]; [suposição]", "suposição"),
    ("M2", "Acoplamento credibilidade ↔ Selic e ajuste", "0,5", "comum", "[suposição]", "suposição"),
    ("M3", "Persistência do desvio da Selic; reação à inflação", "0,4–0,8; 0,5", "comum", "[suposição]", "suposição"),
    ("M4", "Selic → PIB; multiplicador fiscal; Okun", "0,15–0,45; 0,3–0,8; 0,3–0,5", "comum", "[suposição]", "suposição"),
    ("M5", "Repasse da surpresa de inflação aos salários (ano / seguinte)", "0,3–0,7 / 0,2–0,5", "comum", "[suposição]", "suposição"),
    ("M6", "Comprometimento de renda: Selic +1 p.p.", "+0,1 a +0,3 p.p. de renda", "comum", "insumos 5.5, sem fonte", "suposição"),
    ("M7", "Pesos: serviços 0,35; Bolsa Família com 30% em alimentos", "—", "comum", "[suposição]", "suposição"),
    ("M8", "Tabelas de IR nominais congeladas; INSS corrigido pelo INPC", "—", "comum", "Lei 15.270; [suposição]", "suposição"),
]
