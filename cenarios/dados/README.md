# Dados de entrada – modelo de poder de compra das famílias

Coleta em 05/10/2026. Salário mínimo (SM) vigente: **R$ 1.621,00** (BCB SGS 1619).
Os scripts em `scripts/` reproduzem os CSVs. Foram escritos para rodar no scratchpad onde os
arquivos brutos foram baixados, então os caminhos precisam ser ajustados.

## 1. `distribuicao_salarios.csv`: renda do trabalho em múltiplos do SM
- **Fonte:** microdados da PNAD Contínua trimestral, **2º tri/2026** (`PNADC_022026.zip`, FTP IBGE
  `Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2026/`),
  com o dicionário `Dicionario_e_input_20221031.zip`. A estimativa usa o peso V1028.
- **Renda:** VD4019, o rendimento habitual de todos os trabalhos. Entram os ocupados (VD4002=1) com
  renda > 0, ou seja, 101,7 mi de 103,1 mi de ocupados.
- **Vínculo:** segue o conceito de informalidade do IBGE.
  - formal: VD4009 ∈ {01,03,05,06,07}, mais empregador e conta-própria com CNPJ (V4019=1).
  - informal: VD4009 ∈ {02,04,10}, mais empregador e conta-própria sem CNPJ.
  - Há também um recorte só de `empregado_privado_com_carteira` (VD4009=01).
- **Validação:** a taxa de informalidade calculada (37,4%) é igual à da SIDRA 8529 no 2T2026. A média
  habitual (R$ 3.738) é igual à da SIDRA 5436 no 2T2026.
- **Faixas:** `<1 SM` (<0,98), `~1 SM` (0,98–1,02), 1–1,5, 1,5–2, 2–3, 3–5, 5–10 e >10 SM.
  - Linhas extras: % que ganha *exatamente* R$ 1.621, % entre 0,95 e 1,05 SM, % até 1 SM (≤1,02) e a
    mediana em SM.
- **Cobertura:** Brasil e as 5 regiões.
- **Por que não SIDRA:** não há tabela SIDRA da PNADC por classes de SM. As tabelas 7536/7540
  (limites de percentis, PNADC anual) servem de alternativa para checar a distribuição.

## 2. `kaitz_uf.csv`: índice de Kaitz por UF e região (2T2026)
- **Fonte:** os mesmos microdados do item 1.
- **Medidas:** SM/mediana e SM/média, para VD4019 (todos os trabalhos) e VD4016 (trabalho principal).
  Há também SM/mediana para formais, empregados com carteira no setor privado e informais, além da
  % de informalidade e do n amostral.
- **Atenção:** a mediana é "grudada" em valores redondos e no próprio SM, por causa do amontoamento
  das respostas. Em todo o Nordeste e no PA a mediana é exatamente R$ 1.621 (Kaitz = 1,000). Para
  análises finas, é melhor usar a média ou as shares do item 1.

## 3. `cestas_consumo_pof.csv`: estrutura de gasto da POF 2017-2018
- **Fontes:**
  - SIDRA **6715**: despesa monetária e não monetária média mensal familiar por classes de rendimento
    total, variável 1201, classificações c339 × c12190.
  - SIDRA **6972**: alimentação no domicílio e fora dele.
  - SIDRA **6977**: número de famílias.
  - Valores em R$ de 15/01/2018.
- **Classes:** as 7 classes de rendimento familiar do IBGE. Elas equivalem a 2, 3, 6, 10, 15 e 25 SM
  de 2018 (SM de 2018 = R$ 954). A tabela não usa decis.
- **Medidas:** `pct_despesa_total` e `pct_despesa_consumo`. As categorias de consumo somam 100% da
  despesa de consumo (diferença de no máximo 0,02 p.p.).
- **Fora do consumo:**
  - Itens marcados com o prefixo `fin_`, `impostos`, `transferencias` e `aumento_ativo` são "outras
    despesas correntes", aumento do ativo ou diminuição do passivo. Para eles só há % da despesa total.
  - `fin_emprestimos_carne` corresponde à amortização de empréstimos e carnês (principal + juros).
- **Aluguel:** o aluguel não monetário (imputado a imóvel próprio ou cedido) entra no consumo da POF,
  mas não no IPCA. Ele aparece separado (`habitacao_aluguel_nao_monetario_imputado`).
- **Mapeamento IPCA:** a coluna `grupo_ipca` indica o grupo ou subitem do IPCA.
  - `codigo_ipca_c315` é a categoria da SIDRA 7060/7063.
  - Pesos de **ago/2026**: IPCA vem da SIDRA 7060, v66; INPC vem da SIDRA 7063, v45.
  - Mapeamento manual. "Celular e acessórios" (recreação na POF) foi para Comunicação.

## 4. `beneficios_piso_inss.csv`: benefícios no piso e custo de +R$ 1 no SM
- **Fonte:** **BEPS – Boletim Estatístico da Previdência Social, vol. 32 nº 08, ago/2026**
  (`gov.br/previdencia/.../boletins-da-previdencia-social/2026/beps082026_final.pdf`).
  - Quadro 16 (emitidos por faixa de valor), Quadro 17 (urbano/rural), Quadro 18 (UF/região) e
    Quadro 20 (espécies 87/88 = BPC, RMV).
  - Benefícios no piso: **29,49 mi (69,1%)** do total de 42,66 mi emitidos.
  - RGPS: 22,90 mi de 36,04 mi (63,5%).
  - BPC: 6,56 mi (3,81 mi PcD e 2,75 mi idosos).
- **Custo fiscal:** PLDO 2027, Anexo V (Riscos Fiscais), Tabela 10, reproduzida na Nota Técnica
  Conjunta CONOF/CONORF nº 3/2026 (mai/2026).
  - +R$ 1 no SM = **R$ 413,2 mi/ano** de despesa: RGPS 308,4; BPC 74,0; RMV 0,5; abono 20,0;
    seguro-desemprego 10,2.
  - O mesmo +R$ 1 gera +R$ 8,2 mi de receita.
  - SM projetado para 2027: R$ 1.717 no PLDO (abr/2026) e R$ 1.741 no PLOA 2027 (ago/2026). O valor
    do PLOA veio da imprensa (CNN e Poder360), sem conferência no documento original.

## 5. `endividamento_por_renda.csv`: endividamento e inadimplência
Formato longo: fonte, referência, faixa, indicador, valor, unidade.
- **BCB SGS (agregado):**
  - 29034, 29035, 29036, 29264, 29265: comprometimento de renda com o serviço da dívida, jul/2026
    (28,7% dessazonalizado).
  - 29037 e 29038: endividamento sobre a renda de 12 meses (49,9%).
  - 21084: inadimplência PF total, ago/2026 (6,03%).
  - 21112: inadimplência PF com recursos livres (8,01%).
- **BCB SCR.data:**
  - Arquivo `planilha_202607.csv`, de `bcb.gov.br/pda/desig/planilha_2026.zip`, data-base 31/07/2026,
    filtrado em cliente = PF.
  - Faixas de **renda do tomador em SM** (sem rendimento, ≤1, 1–2, 2–3, 3–5, 5–10, 10–20, >20).
  - Medidas: carteira ativa, % vencido >15 dias, % inadimplida >90 dias (carteira inadimplida
    arrastada) e ativo problemático. Também há o recorte por modalidade (cartão, consignado, pessoal,
    veículos, habitacional etc.).
  - Inadimplência de 9,9% para quem ganha ≤1 SM, contra 5,7% para quem ganha >20 SM.
- **CNC Peic:**
  - Ago/2026, divulgada em 10/09/2026 no Portal do Comércio.
  - % de famílias endividadas, com contas em atraso e sem condições de pagar, por faixa de renda
    (≤3, 3–5, 5–10, >10 SM).
  - Renda comprometida média de 29,5%. Algumas células por faixa não foram divulgadas.
- **Serasa:** 83,9 mi de negativados em ago/2026. A fonte é secundária (imprensa) e não há recorte
  por renda.

## Lacunas
- **Comprometimento por faixa de renda:** não há série oficial do comprometimento de renda (serviço
  da dívida / renda) por faixa de renda. O BCB publica só o agregado e a Peic só a média geral.
- **Desatualização da POF:** a POF é de 2017-18. A POF 2024-25 ainda não está na SIDRA. Os itens
  "comunicação", "serviços pessoais" e "despesas financeiras" seguem a classificação da POF, que não
  coincide 1:1 com a do IPCA.
- **CAGED e RAIS:** não foram usados, porque a PNADC já cobre formais e informais. A RAIS 2024
  poderia refinar a fração de vínculos formais exatamente no SM.
- **Revisão de pesos:** os pesos do IPCA e do INPC são de ago/2026. O IBGE os atualiza com a POF.
