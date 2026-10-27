"""Premissas do modelo v2 (fatos, consenso, parâmetros incertos, programas, famílias-tipo e
conjuntos de hipóteses).

Regras de neutralidade
----------------------
* `COMUM` vale para os dois cenários: elasticidades, regimes de credibilidade, multiplicadores,
  incidência. Nada aqui tem rótulo de candidato.
* `CANDIDATOS["L"]` e `CANDIDATOS["F"]` têm **exatamente as mesmas chaves**. O que muda são os
  valores: o que cada um propôs ou declarou, e as probabilidades de execução. Promessas sem fonte de
  financiamento entram com probabilidade de execução, nunca pelo valor de face.
* Onde a pesquisa não discrimina entre os dois (persistência do choque cambial, reajuste do Bolsa
  Família, correção da tabela do IR, 6x1), o prior é o mesmo para os dois no conjunto central.
* Os conjuntos "pró-Lula" e "pró-Flávio" deslocam, dentro de faixas defensáveis, as hipóteses que
  cada campo costuma defender. Eles existem para mostrar onde a conclusão depende de hipótese.

Formatos de distribuição: número = fixo; ("tri", a, moda, b); ("U", a, b); ("N", média, dp, mín, máx);
("LN", mediana, sigma, mín, máx). Notas: M# = salario_minimo_equilibrio_geral.md (tabela §9);
MF# = macro_fiscal_dinamica.md (tabela §9); C/L/F/E# = cenarios_economicos_insumos.md (§7);
R# = item da revisão cética (revisao_cetica_cenarios_v1.md); V = medido_vs_vivido.md.
"""
from __future__ import annotations

from copy import deepcopy

import numpy as np

ANOS = list(range(2027, 2035))   # mandato 2027–2030 + 2031–2034 (custos diferidos)
ANOS_MANDATO = 4
T = len(ANOS)

BASE = {
    "cambio": 5.22,            # PTAX 02/10/2026
    "selic_fim_2026": 13.5,    # Focus 28/09/2026
    "selic_media_2026": 14.3,  # média de 2026 (15% até fev, cortes desde mar) [calc aproximado]
    "desemprego": 5.3,         # PNADC jun–ago/2026
    "renda_media_trabalho": 3777.0,  # PNADC: rendimento MÉDIO real habitual (não é mediana)
    "renda_mediana_trabalho": 2300.0,  # kaitz_uf.csv: mediana de todos os trabalhos (2T2026)
    "salario_minimo": 1621.0,
    "sm_2019": 998.0,
    "bolsa_familia_piso": 691.0,  # decreto de 17/09/2026 (+15,04% = INPC mar/23–ago/26)
    "bf_linha_pc": 218.0,      # linha de entrada do Bolsa Família (R$ per capita)
    "cesta": 779.95,           # DIEESE/Conab jun/2026 (27 capitais)
    "divida": 82.5,            # DBGG fim de 2026 (IFI)
    "pib_nominal_tri": 13.4,
    "horas_mes": 220.0,
    "linha_pobreza_pc": 700.0,   # R$/mês per capita de 2026 [suposição: ~US$ 6,85 PPC/dia, linha do IBGE SIS]
    "linha_extrema_pc": 230.0,   # ~US$ 2,15 PPC/dia [suposição]
    "alim_2019_2026": 1.763,     # V §3.1: alimentação no domicílio jan/2019–ago/2026 (+76,3%)
    "ipca_2019_2026": 1.497,     # V §3.1: IPCA jan/2019–ago/2026 (+49,7%)
}
BASE["horas_cesta"] = BASE["cesta"] / BASE["salario_minimo"] * BASE["horas_mes"]

CONS = {  # Focus 28/09/2026; IFI RAF 113/116; depois de 2029 = último ano [suposição]
    "ipca": np.array([4.31, 3.80, 3.50, 3.50, 3.50, 3.50, 3.50, 3.50]),
    "selic_fim": np.array([12.0, 10.5, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0]),
    "cambio": np.array([5.28, 5.30, 5.36, 5.36, 5.36, 5.36, 5.36, 5.36]),
    "pib": np.array([1.5, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]),
    "primario": np.array([-0.7, -0.8, -1.0, -1.1, -1.1, -1.1, -1.1, -1.1]),  # IFI base sem medidas novas (MF §1.3)
}
PARCELA_SELIC = 0.527   # MF13: DPF atrelada à Selic (Tesouro ago/2026)

# ---------------------------------------------------------------------------
# Mecanismos (canais) — usados como chaves liga/desliga na decomposição de Shapley
# ---------------------------------------------------------------------------
CANAIS = ["sm_direto", "repasse", "farol", "achatamento", "emprego", "juros", "cambio", "fiscal",
          "impostos", "trabalho", "credito", "longo_prazo"]
CANAL_NOME = {
    "sm_direto": "Salário mínimo (efeito direto na renda)",
    "repasse": "Repasse do mínimo a preços",
    "farol": "Efeito farol (informais)",
    "achatamento": "Cascata e achatamento (salários acima do piso)",
    "emprego": "Emprego (desemprego cíclico e efeito do mínimo)",
    "juros": "Juros, prêmio de risco e dívida das famílias",
    "cambio": "Câmbio",
    "fiscal": "Ajuste fiscal, cortes e transferências",
    "impostos": "Impostos e combustíveis",
    "trabalho": "6x1 e contrato por hora",
    "credito": "Crédito direcionado e ciclo da dívida das famílias",
    "longo_prazo": "Investimento e produto potencial (longo prazo)",
}

# ---------------------------------------------------------------------------
# Parâmetros comuns (incertos). Cada um vira um sorteio por simulação, igual nos dois cenários.
# ---------------------------------------------------------------------------
COMUM = {
    # consenso e choques externos
    "ipca_2027": ("tri", 3.6, 4.3, 5.0),             # C2
    "ipca_dp": 1.0,                                   # C3
    "ipca_2026": ("tri", 4.6, 5.0, 5.4),             # C1 (INPC 2026 ≈ IPCA 2026 [suposição])
    "premio_alimentos": ("N", 0.9, 5.1, -7.8, 13.6), # C4 IBGE 2003–2025
    "pib_2026": ("tri", 1.6, 1.9, 2.4),
    "pib_2027": ("tri", 0.2, 1.5, 2.5),              # C5
    "pib_2028_30": ("tri", 1.0, 2.0, 2.5),           # C6
    "desemprego_2027": ("tri", 5.0, 6.0, 6.7),       # C10
    "desemprego_dp": 0.4,                             # passeio comum anual [suposição]
    "renda_real_2027": ("tri", 0.0, 2.0, 3.5),       # C11
    "renda_real_2028_30": ("tri", -0.5, 1.5, 3.0),   # C12
    "sm_2027": ("tri", 1735.0, 1741.0, 1750.0),      # C17 PLOA
    "brent_2027": ("LN", 72.0, 0.20, 45.0, 140.0),   # MF37
    "brent_dp": 0.15,
    "fracao_bomba_gasolina": ("tri", 0.0, 0.25, 0.47),  # C15
    "fracao_bomba_diesel": ("tri", 0.05, 0.25, 0.45),   # [suposição]
    "diesel_alimentos": 0.05, "diesel_onibus": 0.25,    # parcela do diesel no custo [suposição/TRU]
    "fx_ruido_dp": 0.10,                                 # R5: ~12–15% de volatilidade; parte já nos regimes
    "selic_ruido_dp": 0.75,
    # repasse cambial (E1–E4) e assimetria (E5); comonotônicos com fator comum de escala
    "repasse_cambio_ipca": ("tri", 0.03, 0.10, 0.25),
    "assimetria": ("tri", 0.5, 0.75, 1.0),
    "selic_ipca": ("tri", 0.15, 0.27, 0.40),         # E6
    # Taylor (R14): candidato só entra via prêmio e expectativas
    "taylor_rho": ("U", 0.3, 0.6),
    "taylor_pi": ("U", 0.6, 1.3),
    "taylor_gap": ("U", 0.3, 0.7),
    "premio_selic": ("U", 0.25, 0.75),               # +1 p.p. de prêmio → Selic
    "premio_cambio": ("U", 0.03, 0.10),              # +1 p.p. de prêmio (dívida) → câmbio (log)
    "premio_divida": ("tri", 0.03, 0.112, 0.33),     # E8/IFI
    "fx_divida": 0.07,                               # MF11: +1% de câmbio → +0,07 p.p. DBGG
    # hiato, Okun, salários
    "is_juro": ("U", 0.15, 0.45),                    # MF16 (convertido para anual) [suposição]
    "hiato_rho": ("U", 0.4, 0.7),
    "okun_neg": ("U", 0.4, 0.6), "okun_pos": ("U", 0.2, 0.3),  # MF17
    "receita_ciclica": 0.25,                         # primário por 1% de hiato [suposição]
    "indexacao": ("U", 0.3, 0.7),                    # R13: repasse da surpresa de inflação no ano
    "correcao_erro": ("U", 0.3, 0.7),                # R13: κ
    "salario_desemprego": ("U", 0.3, 0.8),           # w* cai φ% por p.p. de desemprego acima do consenso
    # multiplicadores (MF21–26; R3)
    "mult_transferencia": ("tri", 0.8, 1.5, 1.8),       # MF22 1,5 (0,8–1,8); C30 1,78
    "mult_beneficio_sm": ("tri", 0.4, 0.7, 1.2),
    "mult_discricionaria": ("tri", 0.2, 0.5, 1.0),
    "mult_imposto_consumo": ("tri", 0.1, 0.25, 0.4),   # MF26 0,25 (0,1–0,4)
    "mult_imposto_topo": ("tri", 0.05, 0.2, 0.4),
    "mult_subsidio": ("tri", 0.0, 0.1, 0.3),
    # salário mínimo em equilíbrio geral (salario_minimo_equilibrio_geral.md §9)
    "sm_repasse_escala": ("tri", 0.4, 0.75, 2.0),    # M1: IPCA 0,016–0,08 por 1% (0,03 central)
    "sm_repasse_defasagem": ("U", 0.4, 0.9),         # M8 (fração no ano)
    "sm_repasse_ne": ("U", 1.0, 1.6),                # M9
    "farol_informal": ("tri", 0.3, 0.5, 0.8),        # M10
    "farol_autonomo": ("tri", 0.0, 0.2, 0.4),        # M11
    "cascata_p50": ("tri", 0.05, 0.10, 0.25),        # M12 (~1,5 SM)
    "cascata_2a3": ("tri", 0.0, 0.03, 0.10),         # M13
    "cascata_ne": ("tri", 0.6, 0.8, 1.0),            # M14: transbordamento até a mediana do Nordeste (≈ 1 SM)
    "consumidor_paga": ("U", 0.5, 1.0),              # M7
    "achatamento_psi": ("U", 0.0, 0.5),              # fração do custo não repassado que sai dos salários acima [suposição]
    "emprego_sm_br": ("tri", -0.20, -0.05, 0.0),     # M16
    "emprego_sm_ne": ("tri", -0.40, -0.15, 0.0),     # M17
    "emprego_pouca_qualif": ("tri", 1.5, 2.5, 4.0),   # M18 2,5 (1,5–4)
    "formal_para_informal": ("U", 0.0, 0.5),         # M19
    "beta_desemprego_baixa": ("U", 1.5, 2.0),        # R9
    "beta_desemprego_alta": ("U", 0.4, 0.7),
    # fiscal: execução por regime, fechamento, incidência
    "entrega_credivel": ("U", 0.75, 1.0),
    "entrega_meio": ("U", 0.25, 0.65),
    "entrega_crise": ("U", 0.0, 0.3),
    "discricionaria_cortavel": ("U", 0.4, 0.8),      # p.p. do PIB cortáveis sem paralisar (R$ 222 bi ≈ 1,6%) [suposição]
    "fechamento_k": ("U", 0.15, 0.5),               # P/ano de o fechamento "estourar" por p.p. de excesso [suposição]
    "fechamento_sm": ("U", 0.3, 0.7),               # se estourar: P(sai pela regra do mínimo); senão, rompe o arcabouço (+crise) [suposição]
    "vegetativo": 0.10,                              # crescimento vegetativo da obrigatória acima do teto (p.p./ano) [suposição]
    "financiado_divida": ("U", 0.5, 0.9),
    "obrig_abono": ("U", 0.0, 0.3),                  # fração do corte de obrigatórias que cai no abono salarial (R$ 30 bi ≈ 0,22% PIB) [suposição]            # parte de promessa sem fonte que vira dívida (resto: cortes)
    "incidencia_lucro_salario": ("U", 0.3, 0.5),     # MF30
    "incidencia_fase": ("U", 0.25, 0.75),            # quanto da incidência de longo prazo aparece até 2030
    "repasse_banco_spread": ("U", 0.4, 1.0),         # MF31
    "repasse_corte_tributo": ("tri", 0.05, 0.5, 1.0),  # M32
    "repasse_alta_tributo": ("U", 0.8, 1.0),         # M33
    # IVA (F10/F11) e combustíveis
    "iva_leitura": ("U", 0.0, 1.0),
    "iva_rota_uniforme": 0.5,                        # P(rota "corte uniforme"); senão "remove reduções" [suposição]
    "corte_gasolina_bomba": ("tri", 4.8, 7.1, 9.5),  # R$ 0,3–0,6/l ÷ R$ 6,3/l [calc]
    # 6x1 e PEC 12 (R15)
    "x6_precos_servicos": ("tri", 0.0, 1.0, 3.0),
    "x6_pib_nivel": ("tri", -0.7, -0.2, 0.0),
    "x6_informalizacao": ("tri", 0.0, 0.5, 1.5),     # p.p. de risco de perder o emprego formal no piso
    "pec12_parcela": ("U", 0.02, 0.10),
    "pec12_horas": ("U", 0.6, 0.9),
    "pec12_formaliza": ("U", 0.0, 0.05),
    # câmbio → renda (R6, M35) e regime
    "cambio_renda": ("U", 0.0, 0.10),                # M35 (agro e comerciáveis), escalado pela exposição da família [suposição]
    "topo_decil_parcela": ("U", 0.1, 0.4),           # parte da receita nova sobre altas rendas paga pelo décimo do topo (o resto é 1%/0,1%) [suposição]
    "duracao_titulos": ("U", 4.0, 6.0),              # C2 da revisão v2: marcação a mercado de prefixados e IPCA+
    "beta_acoes_premio": ("U", 0.05, 0.10),          # Ibovespa −5 a −10% por +1 p.p. de prêmio (2015, 2024)
    "crise_aperto_p": ("U", 0.3, 0.6),               # M5 da revisão: P(pacote de emergência num ano de crise), qualquer vencedor
    "crise_aperto_tam": ("U", 0.5, 1.0),             # tamanho do pacote (p.p. do PIB)
    "rolagem_premio": 0.2,
    # canal de longo prazo (macro_fiscal_dinamica.md §6: potencial 1,2–3,0%; FBCF 16%; PTF ~0,3%/ano):
    # juro real longo (Selic real + prêmio) abaixo do consenso → mais investimento → capital → potencial e salários,
    # com defasagem de 3+ anos; na crise, o contrário. Mesmo mapa para os dois [suposição, faixa larga]
    "invest_juro": ("U", 0.2, 1.0),                  # p.p. de FBCF/PIB por p.p. de juro real longo
    "invest_defasagem": 3,                           # anos até o capital novo virar produto
    "elasticidade_capital": 0.35, "capital_produto": 3.0,
    "eficiencia_iva_sem_excecoes": ("U", 0.0, 0.5),  # % do PIB (nível) até 2034 se o IVA vier pela rota "menos exceções" (Ferreira et al.: 6 p.p. em 15 anos)                           # fração da dívida não-Selic que rola por ano ao juro com prêmio
    "conv_meses": ("U", 12.0, 18.0),
    "fx_credivel": ("tri", -0.14, -0.08, -0.03),     # Goldman R$ 4,50–4,80; JPM 4,80–4,90
    "fx_meio": ("tri", -0.02, 0.02, 0.06),           # Goldman moderado R$ 5,40
    "fx_crise": ("tri", 0.10, 0.18, 0.35),           # Goldman R$ 5,80+; 2015 e 2002 muito acima
    "premio_credivel": ("tri", -1.2, -0.8, -0.3),    # Goldman: ~80 bps eliminados
    "premio_crise": ("tri", 1.0, 2.0, 4.0),          # 2015, dez/2024
    "crise_por_divida": ("U", 0.05, 0.20),           # +P(crise)/ano por 10 p.p. de dívida acima do consenso [suposição]
    # crédito e custos ocultos (custos_ocultos_credito_subsidios.md, C1–C33)
    "direcionado_selic": ("U", 0.02, 0.07),          # C7: +p.p. de Selic por +1 p.p. de fatia do direcionado (C6 ~1,1 p.p. no nível; Castro 2019 ~0)
    "credito_impulso": ("U", 0.2, 0.5),              # p.p. de hiato no ano por p.p. do PIB de crédito novo [suposição]
    "credito_ressaca": ("tri", 0.15, 0.34, 0.45),    # C22: −p.p. de PIB acumulado em 3 anos (defasado) por p.p. de dívida/PIB
    "fgts_valor": 0.5,
    "fgts_rend_base": 6.9,                            # C12: rendimento total do FGTS em 2025 (TR + 3% + lucro), com desconto de 1,9 p.p.
    "antecipacao_receita": ("U", 0.2, 0.6),          # fração da receita única que é antecipação (royalties, dívida ativa) e falta em 2031–34
    "lacuna_compensacao_ir": ("tri", 0.0, 0.06, 0.12),  # IR16: buraco de R$ 15–21 bi em 2026; ajuste do IRPFM em 2027 (IR14) e regime pleno (IR15) o fecham até 2029 — comum, lei vigente             # valor, para o trabalhador, de R$ 1 depositado no FGTS (iliquidez) [suposição]
    # famílias
    "crra": 1.5,
    # depois do mandato (2031–2034): quem governa é desconhecido; vale uma regra comum de "a conta chega"
    "ajuste_forcado_limiar": ("U", 3.0, 8.0),       # p.p. de dívida acima do consenso que dispara ajuste forçado
    "ajuste_forcado_passo": ("U", 0.3, 0.8),        # p.p. do PIB por ano de ajuste forçado (até 2,5)                                     # R15: ρ ∈ [1, 2]
    "encolhimento": ("U", 0.1, 0.5),                 # V §1: reduflação em alimentos e higiene (p.p./ano)
    "aluguel_mudanca": ("U", 3.0, 5.0),              # V §3.3: novos contratos +~4 p.p./ano
    "plano_coletivo": ("U", 3.0, 7.0),               # V §3.4: coletivos ~+5 p.p./ano
    "taxa_mudanca": 0.2,                             # fração de inquilinos que muda por ano [suposição]
}

# Matriz de transição anual do regime (comum; linhas = de, colunas = para). MF29: reversão
# depois de sinal crível ~0,6; R5: P(crise) 0,05–0,25.
TRANSICAO = np.array([[0.80, 0.15, 0.05],
                      [0.15, 0.70, 0.15],
                      [0.10, 0.40, 0.50]])
REGIMES = ["credível", "meio-termo", "crise de credibilidade"]

# ---------------------------------------------------------------------------
# Programas (mesmas chaves para os dois)
# ---------------------------------------------------------------------------
CANDIDATOS = {
    "L": {
        "nome": "Lula",
        "regime": {
            "pi0": [0.50, 0.35, 0.15],                  # L2: P(depreciação persiste) 0,5 → P(crível) 0,5
            "transicao": None,                          # None = TRANSICAO comum
            "impacto_cambio": ("tri", 0.03, 0.08, 0.15),  # L1 (bancos): mercado precifica
        },
        "fiscal": {
            "ajuste_total": ("tri", 0.5, 1.7, 2.5),     # L16 (p.p. do PIB até 2030)
            "ajuste_meses": 48,
            # composição do ajuste (média da Dirichlet): receita sobre topo, corte de gasto
            # tributário, discricionária, obrigatória [suposição a partir do histórico e do plano]
            "composicao": [0.45, 0.15, 0.30, 0.10],
            "concentracao": 20.0,
            "privatizacao": 0.0,                        # p.p. do PIB de redução de estoque
            # parte do ajuste que é receita única/extraordinária (não corta ninguém, some depois de 2028):
            # receitas não recorrentes e deduções da meta (IFI; conta_completa_politicas.md §4.1, CC24–25) [suposição]
            "receita_unica": ("tri", 0.05, 0.15, 0.30),
        },
        # C1 da revisão v2: o próprio governo Lula mudou a regra em dez/2024 (teto de 2,5%); Flávio declarou manter (03/10)
        # e a nota F6 dá 0,65 → mesmo prior para os dois
        "minimo": {"p_intencao": ("U", 0.8, 1.0), "ganho_extra": 0.0},
        "bolsa": {"p_reajuste": ("U", 0.3, 0.9), "real_extra": 0.0},  # R1: mesmo prior
        # IR25: política de correção (art. 6º da Lei 15.270) com P ~0,3 até 2027; correções parciais em 2023–25
        "ir": {"p_correcao": ("U", 0.05, 0.40), "p_reverte_topo": 0.0, "p_reverte_bancos": 0.0},
        "iva": {"p": 0.0},
        "combustivel": {"frac_2027": 0.5, "subsidio_2027": ("tri", 0.15, 0.35, 0.6),  # CC17: R$ 7 bi/mês ≈ 0,6% PIB anualizado; Brent de 2027 menor reduz
                        "p_corte_trib": 0.0, "custo_corte": 0.0},
        "trabalho": {"p_6x1": 0.5, "p_pec12": 0.0},     # R15: 6x1 votada antes da posse → mesmo P
        "credito": {  # custos_ocultos_credito_subsidios.md — sem números nos planos: tratado como cenário [suposição]
            "direcionado_dfatia": ("tri", 0.0, 1.0, 2.0),  # p.p./ano na fatia do direcionado (ritmo de 2024–26 continua)
            "expansao_credito": ("tri", 0.0, 0.5, 1.0),    # p.p. do PIB/ano de crédito PF acima do consenso (pacote parafiscal C28)
            "fgts_desconto": ("tri", 1.4, 1.9, 2.2),       # C15: descontos do MCMV custam ao cotista ~1,9 p.p. de rendimento
            "diferidos": [0.0] * 8},    # custo diferido que cai no primário (p.p. do PIB)
    },
    "F": {
        "nome": "Flávio Bolsonaro",
        "regime": {
            "pi0": [0.50, 0.35, 0.15],                  # F2: P(apreciação persiste) 0,5 → P(crível) 0,5
            "transicao": None,
            "impacto_cambio": ("tri", -0.14, -0.07, -0.04),  # F1 (bancos)
        },
        "fiscal": {
            "ajuste_total": ("tri", 0.5, 1.5, 3.0),     # F16: 1,5 p.p. (R$ 190 bi) em 18 meses
            "ajuste_meses": 18,
            # checagem F9: R$ 190 bi contra R$ 222 bi de discricionárias; sem lista de cortes
            "composicao": [0.05, 0.20, 0.45, 0.30],
            "concentracao": 20.0,
            "privatizacao": ("tri", 0.0, 0.5, 2.0),     # securitização/imóveis/estatais: só estoque
            # "Tesouraço": fontes citadas são securitização da dívida ativa, royalties antecipados, venda de
            # ativos (CC43, CC45; conta_completa_politicas.md §5) [suposição sobre a fração]
            "receita_unica": ("tri", 0.30, 0.50, 0.70),
        },
        "minimo": {"p_intencao": ("U", 0.8, 1.0), "ganho_extra": 0.0},
        "bolsa": {"p_reajuste": ("U", 0.3, 0.9), "real_extra": 0.0},
        # isencao_ir_incidencia.md §3.3: nenhuma proposta de correção da tabela inteira; Bolsonaro não corrigiu em
        # 2019–22; IR28: revogar a compensação e manter a isenção, P = 0,3 (0,1–0,5)
        "ir": {"p_correcao": ("U", 0.05, 0.40), "p_reverte_topo": 0.30, "p_reverte_bancos": 0.30},
        "iva": {"p": 0.2},                              # F9: sem fonte de compensação
        "combustivel": {"frac_2027": 1.0, "subsidio_2027": 0.0,
                        "p_corte_trib": 0.7, "custo_corte": ("tri", 0.2, 0.25, 0.35)},
        "trabalho": {"p_6x1": 0.5, "p_pec12": 0.25},
        "credito": {  # mesma régua: Casa Verde e Amarela "à menor taxa" sobe o direcionado; menos BNDES o reduz
            "direcionado_dfatia": ("tri", -1.5, -0.25, 1.0),
            "expansao_credito": ("tri", 0.0, 0.4, 1.0),
            "fgts_desconto": ("tri", 1.4, 1.9, 2.2),
            "diferidos": [0.0] * 8},    # custo diferido que cai no primário (p.p. do PIB)
    },
}

# ---------------------------------------------------------------------------
# Famílias-tipo (arquétipos [suposição], ancorados nas faixas da PNADC, POF e SCR)
#   m_*: renda em múltiplos do SM de 2026; tam: pessoas; pof: classe de cesta; ne: cesta do NE
#   divida: estoque/renda anual, serviço/renda, mistura de linhas (SCR por faixa de renda)
#   in_kind: valor dos serviços públicos usados (SUS, escola) em % da renda monetária [suposição]
# ---------------------------------------------------------------------------
LINHAS = ["cartao", "cheque", "pessoal", "consignado", "veiculo", "habitacional"]
# repasse da Selic à taxa (E7/EE 118; rotativo quase insensível, R7) e fração repactuada por ano
LINHA_REPASSE = {"cartao": 0.3, "cheque": 1.5, "pessoal": 1.73, "consignado": 0.8, "veiculo": 0.75, "habitacional": 0.43}
LINHA_REPRECIFICA = {"cartao": 1.0, "cheque": 1.0, "pessoal": 0.6, "consignado": 0.3, "veiculo": 0.35, "habitacional": 0.05}

TIPOS = {
    "formal_sm": dict(
        nome="Trabalhador formal com 1 salário mínimo", curto="Formal 1 SM",
        formal=1.0, tam=2, pof="47558", ne=False, regiao_emprego="piso_formal",
        u0=0.06, beta="baixa", rr=0.45, abono=True, x6=True, pec12=True, in_kind=0.20,
        divida=dict(estoque=0.45, servico=0.22, mix=dict(cartao=0.26, cheque=0.04, pessoal=0.15, consignado=0.38, veiculo=0.05, habitacional=0.12)),
        exposto_cambio=0.05),
    "informal_sm": dict(
        nome="Trabalhador informal perto de 1 SM", curto="Informal ~1 SM",
        informal=1.0, tam=2, pof="47558", ne=False, u0=0.09, beta="baixa", rr=0.25, in_kind=0.22,
        divida=dict(estoque=0.25, servico=0.15, mix=dict(cartao=0.45, cheque=0.05, pessoal=0.35, consignado=0.0, veiculo=0.10, habitacional=0.05)),
        exposto_cambio=0.03, pec12_formaliza=True),
    "autonomo": dict(
        nome="Conta própria (inclui aplicativo), 1,3 SM", curto="Conta própria",
        autonomo=1.3, tam=2, pof="47558", ne=False, u0=0.07, beta="baixa", rr=0.3, in_kind=0.18,
        aplicativo=0.3,
        divida=dict(estoque=0.35, servico=0.18, mix=dict(cartao=0.30, cheque=0.05, pessoal=0.20, consignado=0.10, veiculo=0.20, habitacional=0.15)),
        exposto_cambio=0.03),
    "bf_ne": dict(
        nome="Família no Bolsa Família, Nordeste (4 pessoas)", curto="Bolsa Família NE",
        informal=0.40, bf=900.0, tam=4, pof="47558", ne=True, u0=0.15, beta="baixa", rr=0.2, in_kind=0.40,
        divida=dict(estoque=0.15, servico=0.10, mix=dict(cartao=0.6, cheque=0.0, pessoal=0.4, consignado=0.0, veiculo=0.0, habitacional=0.0)),
        exposto_cambio=0.05),
    "bf_resto": dict(
        nome="Família no Bolsa Família, resto do Brasil (4 pessoas)", curto="Bolsa Família resto",
        informal=0.45, bf=900.0, tam=4, pof="47558", ne=False, u0=0.13, beta="baixa", rr=0.2, in_kind=0.35,
        divida=dict(estoque=0.15, servico=0.10, mix=dict(cartao=0.6, cheque=0.0, pessoal=0.4, consignado=0.0, veiculo=0.0, habitacional=0.0)),
        exposto_cambio=0.05),
    "aposentado_piso": dict(
        nome="Aposentado no piso (1 SM)", curto="Aposentado piso",
        aposentadoria_piso=1.0, tam=1.5, pof="47558", ne=False, in_kind=0.15,
        divida=dict(estoque=0.50, servico=0.25, mix=dict(cartao=0.15, cheque=0.0, pessoal=0.10, consignado=0.75, veiculo=0.0, habitacional=0.0))),
    "aposentado_acima": dict(
        nome="Aposentado acima do piso (2,2 SM, corrigido pelo INPC)", curto="Aposentado > piso",
        aposentadoria_inpc=2.2, tam=2, pof="47559", ne=False, in_kind=0.10, ir=True,
        divida=dict(estoque=0.50, servico=0.22, mix=dict(cartao=0.20, cheque=0.0, pessoal=0.10, consignado=0.60, veiculo=0.05, habitacional=0.05))),
    "classe_media": dict(
        nome="Trabalhador formal de 2,5 SM (classe média; achatamento)", curto="Formal 2,5 SM",
        formal=2.5, tam=3, pof="47560", ne=False, u0=0.04, beta="media", rr=0.5, x6=True, in_kind=0.08, ir=True,
        plano_coletivo=True, inquilino=True, financeiro=0.3,
        divida=dict(estoque=0.80, servico=0.25, mix=dict(cartao=0.16, cheque=0.03, pessoal=0.07, consignado=0.19, veiculo=0.09, habitacional=0.46)),
        exposto_cambio=0.05),
    "endividado": dict(
        nome="Família endividada no rotativo (formal 1,8 SM)", curto="Endividado (rotativo)",
        formal=1.8, tam=3, pof="47559", ne=False, u0=0.06, beta="baixa", rr=0.45, x6=True, in_kind=0.15, inquilino=True,
        divida=dict(estoque=0.90, servico=0.40, mix=dict(cartao=0.45, cheque=0.15, pessoal=0.25, consignado=0.10, veiculo=0.05, habitacional=0.0)),
        exposto_cambio=0.05),
    "topo": dict(
        nome="Décimo mais rico com aplicações (15 SM + ativos)", curto="Topo 10%",
        formal=15.0, tam=3, pof="47563", ne=False, u0=0.025, beta="alta", rr=0.6, in_kind=0.01, ir=True,
        plano_coletivo=True, financeiro=4.0, reverte_topo=0.003,
        divida=dict(estoque=1.2, servico=0.15, mix=dict(cartao=0.15, cheque=0.02, pessoal=0.03, consignado=0.05, veiculo=0.15, habitacional=0.60)),
        exposto_cambio=0.03),
}

# ---------------------------------------------------------------------------
# Matriz "sanduíche": 6 faixas de renda × 3 tipos de renda (CLT / PJ-lucros / capital). Células
# representativas [suposição], ancoradas em PNADC, POF, SCR e Lei 15.270/2025; atualizar com
# isencao_ir_incidencia.md e sanduiche_eleitoral.md quando publicadas.
#   m: renda em SM; pof: cesta; in_kind: serviços públicos usados (% da renda); adapt: capacidade de
#   adaptação (fração de um custo tributário que pode ser reclassificada, adiada ou repassada);
#   l15270: carga adicional estatutária do imposto mínimo e da retenção de dividendos (% da renda);
#   topo_peso: % da renda pago por p.p. do PIB de receita nova sobre altas rendas.
# ---------------------------------------------------------------------------
FAIXAS_SANDUICHE = [
    # id, rótulo, m, POF, in_kind, serviço, estoque, cartão/pessoal vs habitacional, u0, exposição câmbio
    ("ate2", "até 2 SM", 1.5, "47558", 0.30, 0.25, 0.50, 0.70, 0.07, 0.10),
    ("2a5", "2–5 SM", 3.5, "47560", 0.15, 0.25, 0.70, 0.45, 0.045, 0.15),
    ("5a10", "5–10 SM", 7.5, "47561", 0.07, 0.22, 0.80, 0.35, 0.035, 0.20),
    ("10a20", "10–20 SM", 15.0, "47562", 0.04, 0.18, 0.90, 0.30, 0.03, 0.25),
    ("20a50", "20–50 SM", 35.0, "47563", 0.02, 0.12, 0.90, 0.25, 0.025, 0.30),
    ("50mais", "50+ SM", 80.0, "47564", 0.01, 0.08, 0.80, 0.20, 0.02, 0.35),
]
TIPOS_RENDA = {"clt": "Salário (CLT)", "pj": "Empresa, PJ e lucros", "capital": "Patrimônio e capital"}
# IR26 (isencao_ir_incidencia.md, DIRPF 2025): índice de adaptação por faixa 12 / 9 / 13 / 21 / 34 / 52–68 (0–100);
# por tipo de renda [suposição]: CLT 0,3×, PJ 1,3×, capital 1,5× (teto 0,85)
_IDX_ADAPT = [0.12, 0.09, 0.13, 0.21, 0.34, 0.60]
ADAPT = {"clt": [round(0.3 * v, 3) for v in _IDX_ADAPT], "pj": [round(min(0.85, 1.3 * v), 3) for v in _IDX_ADAPT],
         "capital": [round(min(0.85, 1.5 * v), 3) for v in _IDX_ADAPT]}
L15270 = {"clt": [0, 0, 0, 0, 0, 0], "pj": [0, 0, 0, 0, 0.02, 0.07], "capital": [0, 0, 0, 0, 0.01, 0.05]}
TOPO_PESO = [0.0, 0.0, 0.0, 0.2, 1.0, 2.5]
TRIB_PJ = [0.08, 0.10, 0.11, 0.13, 0.15, 0.15]   # carga efetiva sobre a renda de PJ/Simples/presumido [suposição]


def _celulas_sanduiche():
    out = {}
    for i, (fid, rot, m, pof, ink, serv, est, livre, u0, fx) in enumerate(FAIXAS_SANDUICHE):
        mix = dict(cartao=livre * 0.45, cheque=livre * 0.1, pessoal=livre * 0.45 * 0.6 + 0.0, consignado=livre * 0.45 * 0.4,
                   veiculo=0.1 * (1 - livre), habitacional=0.9 * (1 - livre))
        for tr, nome_tr in TIPOS_RENDA.items():
            d = dict(nome=f"{rot} · {nome_tr}", curto=f"{rot} {tr.upper()}", tam=1.0, pof=pof, ne=False, in_kind=ink,
                     faixa=fid, tipo_renda=tr, adapt=ADAPT[tr][i], l15270=L15270[tr][i], topo_peso=TOPO_PESO[i],
                     exposto_cambio=fx * (0.3 if tr == "clt" else 0.5),
                     divida=dict(estoque=est * (1.0 if tr == "clt" else 0.7), servico=serv * (1.0 if tr == "clt" else 0.7), mix=mix))
            if tr == "clt":
                d.update(formal=m, u0=u0, beta="baixa" if m <= 2 else ("media" if m <= 10 else "alta"), rr=0.45 if m <= 2 else 0.5,
                         ir=True, abono=m <= 2, plano_coletivo=m >= 5)
            elif tr == "pj":
                d.update(pj=m, trib_pj=TRIB_PJ[i], u0=u0 + 0.01, beta="media" if m <= 10 else "alta", rr=0.4, plano_coletivo=m >= 5)
            else:
                d.update(capital=m, pos_fixado=0.6 if m <= 10 else 0.45)
            out[f"s_{fid}_{tr}"] = d
    return out


SANDUICHE = _celulas_sanduiche()

# ---------------------------------------------------------------------------
# Conjuntos de hipóteses (mesma régua: cada um mexe em parâmetros comuns e/ou nos dois programas)
# ---------------------------------------------------------------------------
CONJUNTOS = {
    "central": {"nome": "Literatura (central)",
                "descricao": "Valores centrais das notas de pesquisa. Prior de credibilidade igual para os dois "
                             "(P(crível) = 0,5, a persistência ~50/50 do choque); choque cambial de impacto dos bancos."},
    "neutro": {"nome": "Neutro (mesma régua de execução)",
               "descricao": "Ignora o choque de impacto precificado pelos bancos e toma as declarações pelo valor "
                            "(Flávio mantém a regra do mínimo, salvo fechamento fiscal). Priors de regime iguais."},
    "pro_lula": {"nome": "Hipóteses favoráveis a Lula",
                 "descricao": "Lula alcança credibilidade com mais chance; Flávio corta impostos antes de ajustar "
                              "(Macri 2018) e o ajuste cai em gasto social; mínimo sem perda de emprego; farol forte; "
                              "repasse a preços baixo; multiplicador de transferências alto; mercado pouco sensível à dívida."},
    "pro_flavio": {"nome": "Hipóteses favoráveis a Flávio",
                   "descricao": "Flávio entrega o ajuste e o real se valoriza de forma duradoura; Lula entra em crise com "
                                "mais chance; mínimo com perda de emprego forte no Nordeste; repasse a preços alto; farol "
                                "fraco; multiplicadores baixos; prêmio muito sensível à dívida."},
}


# M1 da revisão v2: os conjuntos pró-Lula e pró-Flávio são espelhos exatos.
# (a) parâmetros comuns disputados: cada conjunto leva o parâmetro a uma ponta da própria faixa
#     ("lo"/"hi" = ponta que costuma ser defendida por quem apoia Lula);
COMUNS_DISPUTADOS = [
    ("emprego_sm_br", "hi"), ("emprego_sm_ne", "hi"), ("farol_informal", "hi"), ("farol_autonomo", "hi"),
    ("sm_repasse_escala", "lo"), ("mult_transferencia", "hi"), ("mult_beneficio_sm", "hi"),
    ("mult_discricionaria", "hi"), ("premio_divida", "lo"), ("conv_meses", "lo"), ("consumidor_paga", "lo"),
    ("cascata_p50", "hi"), ("cascata_2a3", "hi"), ("incidencia_lucro_salario", "lo"),
]
# (b) hipóteses de execução de cada programa: (caminho, valor favorável ao próprio, valor desfavorável).
#     No conjunto pró-X, X recebe o favorável e o outro o desfavorável.
EXECUCAO_DISPUTADA = [
    ("regime.pi0", [0.65, 0.30, 0.05], [0.35, 0.40, 0.25]),
    ("minimo.p_intencao", ("U", 0.9, 1.0), ("U", 0.6, 0.8)),
    ("bolsa.p_reajuste", ("U", 0.6, 0.95), ("U", 0.2, 0.6)),
    ("ir.p_correcao", ("U", 0.4, 0.8), ("U", 0.0, 0.3)),
    ("fiscal.composicao", [0.35, 0.30, 0.30, 0.05], [0.0, 0.10, 0.40, 0.50]),
    ("fiscal.receita_unica", ("tri", 0.05, 0.1, 0.2), ("tri", 0.5, 0.7, 0.9)),
    ("credito.direcionado_dfatia", ("tri", -1.0, -0.5, 0.0), ("tri", 1.0, 2.0, 3.0)),
]
# Assimetrias do conjunto central (L ≠ F), cada uma com a nota que a sustenta. Um teste garante que
# não há outra diferença entre os programas além destas.
ASSIMETRIAS_CENTRAIS = {
    "regime.impacto_cambio": "cenarios_economicos_insumos.md L1/F1 (bancos)",
    "fiscal.ajuste_total": "L16/F16 (declarações)",
    "fiscal.ajuste_meses": "L16/F16",
    "fiscal.composicao": "planos + checagem F9 (R$ 190 bi x R$ 222 bi) [suposição sinalizada]",
    "fiscal.privatizacao": "plano de Flávio (PND, securitização)",
    "fiscal.receita_unica": "conta_completa_politicas.md §4.1 e §5 (CC43–45) [suposição sinalizada]",
    "ir.p_reverte_topo": "plano de Flávio ('reverter impostos'); IR28",
    "ir.p_reverte_bancos": "plano de Flávio",
    "iva.p": "F9",
    "combustivel.frac_2027": "L15/F15",
    "combustivel.subsidio_2027": "MP 1.340; CC17",
    "combustivel.p_corte_trib": "plano de Flávio",
    "combustivel.custo_corte": "plano de Flávio",
    "trabalho.p_pec12": "F14 (PEC 12 apoiada pela campanha de Flávio)",
    "credito.direcionado_dfatia": "custos_ocultos_credito_subsidios.md (NIB/BNDES x CVA) [cenário]",
    "credito.expansao_credito": "C28 (pacote parafiscal) [cenário]",
}


def _get(d, path):
    for k in path.split("."):
        d = d[k]
    return d


def _set(d, path, v):
    ks = path.split(".")
    for k in ks[:-1]:
        d = d[k]
    d[ks[-1]] = deepcopy(v)


def _ponta(spec, lado):
    if isinstance(spec, (int, float)):
        return spec
    if spec[0] in ("tri", "U"):
        return spec[1] if lado == "lo" else spec[-1]
    return spec[3] if lado == "lo" else spec[4]


def aplicar_conjunto(nome: str):
    """Retorna (comum_override, specs) para o conjunto."""
    specs = {k: deepcopy(v) for k, v in CANDIDATOS.items()}
    com = {}
    if nome == "central":
        pass
    elif nome == "neutro":
        for k in specs:
            specs[k]["regime"]["impacto_cambio"] = 0.0
            specs[k]["regime"]["pi0"] = [0.45, 0.40, 0.15]
            specs[k]["fiscal"]["receita_unica"] = ("tri", 0.1, 0.3, 0.5)
            specs[k]["fiscal"]["composicao"] = [0.25, 0.20, 0.35, 0.20]
    elif nome in ("pro_lula", "pro_flavio"):
        favorecido, outro = ("L", "F") if nome == "pro_lula" else ("F", "L")
        for path, fav, desf in EXECUCAO_DISPUTADA:
            _set(specs[favorecido], path, fav)
            _set(specs[outro], path, desf)
        for k, lado_lula in COMUNS_DISPUTADOS:
            lado = lado_lula if nome == "pro_lula" else ("lo" if lado_lula == "hi" else "hi")
            com[k] = _ponta(COMUM[k], lado)
    else:
        raise KeyError(nome)
    return com, specs


# ---------------------------------------------------------------------------
# Catálogo para a página (id, nome, Lula, Flávio/comum, fonte, tipo)
# ---------------------------------------------------------------------------
PARAMETROS = [
    ("R5/L2/F2", "Regime de credibilidade: P inicial (crível / meio-termo / crise) — prior comum", "0,50 / 0,35 / 0,15", "0,50 / 0,35 / 0,15",
     "persistência ~50/50 do choque para os dois (insumos L2/F2; MF §8.4); P(crise) 0,05–0,25 (revisão R5)", "suposição"),
    ("R5", "Transição anual do regime (crível→crível, meio→meio, crise→crise)", "0,80 / 0,70 / 0,50", "comum",
     "MF29 (reversão ≤12 meses ~0,6); crise sobe com a dívida acima do consenso", "suposição"),
    ("L1/F1", "Choque cambial de impacto (mercado)", "+8% (+3 a +15)", "−7% (−14 a −4)", "JPMorgan, Goldman, BTG, Wells Fargo", "projeção"),
    ("R5", "Câmbio por regime (desvio do consenso)", "crível −8%; meio +2%; crise +18%", "comum", "Goldman R$ 4,50–5,80; 2015, 2024", "projeção"),
    ("R5", "Prêmio por regime (p.p.)", "crível −0,8; meio 0; crise +2", "comum", "Goldman (80 bps); episódios MF §2", "calc"),
    ("R14", "Selic por regra de Taylor + prêmio", "ρ 0,3–0,6; φπ 0,6–1,3; φy 0,3–0,7; prêmio 0,25–0,75", "comum", "revisão R14; sem Selic sorteada por candidato", "suposição"),
    ("E8/R3", "Prêmio por p.p. de dívida acima do consenso", "0,112 (0,03–0,33)", "comum", "IFI RAF 116; dívida de consenso = IFI base", "fonte"),
    ("L16/F16", "Ajuste primário anunciado (p.p. do PIB)", "1,7 (0,5–2,5) até 2030", "1,5 (0,5–3,0) em 18 meses", "declarações (Forbes, GloboNews)", "projeção"),
    ("R4", "Entrega do ajuste por regime", "crível 75–100%; meio 25–65%; crise 0–30%", "comum", "promessa sem lista de cortes não entra pelo valor de face", "suposição"),
    ("R4", "Composição do ajuste: topo / gasto tributário / discricionária / obrigatória", "45 / 15 / 30 / 10%", "5 / 20 / 45 / 30%", "planos; checagem F9 (R$ 190 bi x R$ 222 bi discricionárias)", "suposição"),
    ("C1", "Abono no corte de obrigatórias; corte por restrição a partir do topo (precedente de 2024)", "0–30%", "comum", "pacote de dez/2024; sem fonte para a fração", "suposição"),
    ("C2", "Marcação a mercado da riqueza: duração 4–6 de prefixados/IPCA+; ações −5 a −10% por p.p. de prêmio", "—", "comum", "episódios de 2015 e 2024", "suposição"),
    ("M5", "Prêmio chega à dívida não-Selic (rolagem de 20%/ano); pacote de emergência na crise (P 0,3–0,6; 0,5–1 p.p.)", "—", "comum", "revisão v2; 2003, 2015", "suposição"),
    ("R4", "Fechamento: P(quebrar a regra do mínimo) por p.p. de corte de gasto acima do cortável", "0,3–0,8 por p.p.", "comum", "IFI (contingenciamento R$ 35,7 bi); M22", "suposição"),
    ("C1/F6", "Intenção de manter a regra do mínimo (mesmo prior)", "U(0,8; 1,0)", "U(0,8; 1,0)", "Lula mudou a regra em dez/2024 (Lei 15.077); Flávio declarou manter (03/10); nota F6 = 0,65", "suposição"),
    ("M25", "Regra do mínimo", "INPC(t−1) + PIB(t−2), entre 0,6% e 2,5%", "idem", "Lei 14.663/2023; Lei 15.077/2024 (piso 0,6% a verificar)", "fonte"),
    ("R1", "Bolsa Família: P(reajuste no ano) — repõe o INPC acumulado", "U(0,3; 0,9)", "U(0,3; 0,9)", "histórico 2019–2026 (sem indexação automática; reajuste de 15,04% em set/2026)", "suposição"),
    ("F8", "Reverter impostos de Lula sobre o topo (IRPFM/dividendos) e bancos", "—", "P = 0,35", "plano: 'reverter impostos criados'", "suposição"),
    ("F9–F11", "IVA de 20%", "—", "P = 0,2; −1,6% a −6,25%; 1,1–4,2% do PIB (pleno)", "Borges/IBRE; M32/M33", "calc"),
    ("L15/F15", "Combustíveis", "realinha 50% em 2027 com subsídio 0,1–0,6% PIB", "realinha em 2027; corte de tributo (P 0,7) 0,2–0,35% PIB/ano", "MP 1.340; plano", "suposição"),
    ("CC43–45", "Parte do ajuste que é receita única (não corta gasto; some depois de 2028; parte é antecipação que falta em 2031–34)", "15% (5–30%)", "50% (30–70%)",
     "conta_completa_politicas.md: deduções e receitas extraordinárias (Lula); securitização e royalties antecipados (Flávio)", "suposição"),
    ("CC06–07", "Lacuna da compensação da isenção do IR (comum: lei vigente)", "0–0,13% do PIB/ano", "comum",
     "Receita via CNN: R$ 10,5 bi arrecadados x R$ 28 bi de renúncia em 2026 (confiança baixa; muda com a declaração de 2027)", "calc"),
    ("R10/IR25", "Correção da tabela inteira do IR (P por ano); sem ela, arrasto de faixa (R$ 10 mil: 15,7% → ~17,2% em 2030)", "U(0,05; 0,40)", "U(0,05; 0,40)",
     "isencao_ir_incidencia.md §3.3: nenhum dos dois propôs indexar as faixas acima de R$ 7.350; mesmo prior (assimetria só nos conjuntos pró)", "suposição"),
    ("IR26", "Índice de adaptação por faixa (≤2 / 2–5 / 5–10 / 10–20 / 20–50 / 50+ SM)", "12 / 9 / 13 / 21 / 34 / 52–68", "comum", "DIRPF 2025 [calc]", "calc"),
    ("IR18/IR21", "Imposto mínimo: repasse a preços ~0 (≤0,03 p.p. de IPCA); efeito em salários 0 a −0,5%", "—", "comum", "isencao_ir_incidencia.md §4", "calc"),
    ("R15", "Fim da 6x1 / PEC 12", "P 0,5 / —", "P 0,5 / P 0,25", "Senado vota antes da posse; DIEESE (intermitentes)", "suposição"),
    ("M1–M9", "Repasse do mínimo a preços (serviços intensivos em SM 0,25; IPCA ≈ 0,03)", "escala 0,4–2,0", "comum", "BCB RI mar/2013; Lemos; Harasztosi e Lindner", "fonte"),
    ("M10–M11", "Efeito farol: informal / conta própria", "0,5 (0,3–0,8) / 0,2 (0–0,4)", "comum", "Neri et al.; Fajnzylber; Boeri et al.", "fonte"),
    ("M12–M13", "Cascata: 1,5 SM / 2–3 SM", "0,10 / 0,03", "comum", "Engbom e Moser (2022)", "fonte"),
    ("M16–M19", "Emprego formal ao mínimo: Brasil / NE; pouca qualificação ×2,5 (1,5–4); migração ao informal", "−0,05 / −0,15; 0–50%", "comum", "Saltiel e Urzúa; Jales; E&M", "fonte"),
    ("M14", "Cascata até a mediana do Nordeste (≈ 1 SM)", "0,8 (0,6–1,0)", "comum", "IMDS 2026; DGLM 2021", "fonte"),
    ("M21", "Custo de R$ 1 no mínimo", "R$ 413,2 mi/ano (−R$ 8,2 mi de receita)", "comum", "PLDO 2027, Anexo V", "fonte"),
    ("MF21–26", "Multiplicadores: transferência / benefício do piso / discricionária / imposto de consumo / topo / subsídio", "1,5 / 0,7 / 0,5 / 0,25 / 0,2 / 0,1", "comum", "Orair et al.; Sanches; Matheson e Pereira; transferência MF22 = 1,5 (0,8–1,8); imposto de consumo MF26 = 0,25 (0,1–0,4)", "fonte"),
    ("MF30–31", "Incidência: tributo sobre lucro → salários; tributo bancário → spread", "0,3–0,5; 0,4–1,0", "comum", "Fuest et al.; Suárez Serrato e Zidar; BC (spread)", "fonte"),
    ("R7", "Selic → serviço da dívida por linha (repasse; repactuação/ano)", "cartão 0,3; cheque 1,5; pessoal 1,73; consignado 0,8; veículo 0,75; imobiliário 0,43", "comum", "BC EE 118; rotativo quase insensível", "fonte"),
    ("R9", "Ciclicidade do desemprego: baixa / alta renda", "1,5–2,0 / 0,4–0,7", "comum", "revisão R9; PNADC", "suposição"),
    ("C1–C8", "Crédito direcionado: variação da fatia (p.p./ano) → Selic (+0,02–0,07 por p.p.)", "+1,0 (0 a +2)", "−0,25 (−1,5 a +1)",
     "custos_ocultos_credito_subsidios.md (C6–C7: prêmio ~1,1 p.p., confiança baixa; Castro 2019 ~0); planos sem números", "suposição"),
    ("C20–C23", "Expansão do crédito às famílias: impulso agora, ressaca depois (−0,34 p.p. de PIB em 3 anos por p.p.)", "+0,5 p.p. PIB/ano (0–1)", "+0,4 (0–1)",
     "Mian-Sufi-Verner; Drehmann-Juselius-Korinek; pacote parafiscal de 2026 (C28)", "suposição"),
    ("C13–C16", "FGTS: tributo implícito contra o CDI (camada vivida), desconto do MCMV", "1,9 p.p.", "1,9 p.p.", "C15–C16 (saldo médio suposto ±50%)", "calc"),
    ("MF §6", "Longo prazo: juro real longo → FBCF (0,2–1,0 p.p. do PIB por p.p.) → capital (α 0,35; K/Y 3) → potencial e salários, defasagem de 3 anos; IVA sem exceções +0–0,5% do PIB", "—", "comum",
     "macro_fiscal_dinamica.md §6 (potencial 1,2–3,0%; FBCF 16%; reforma tributária +2,4% a +20% do PIB em 15 anos)", "suposição"),
    ("V", "Camada medido × vivido: reduflação; aluguel de quem muda; plano coletivo; dívida", "0,1–0,5 p.p.; +3–5 p.p.; +3–7 p.p.; serviço total", "comum", "medido_vs_vivido.md §1, §3.3, §3.4, §5.1", "calc"),
]
