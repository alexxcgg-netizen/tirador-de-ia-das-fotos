# Insumos para cenários de poder de compra real 2027–2030: Lula (PT) x Flávio Bolsonaro (PL)

> Notas de pesquisa (situação em 05/10/2026, dia seguinte ao 1º turno). Objetivo: alimentar um modelo de cenários (Monte Carlo) sobre o que cada programa provavelmente significa para o **poder de compra real** das famílias, e não para a renda nominal. Exemplo do usuário: ganhar R$ 100 e pagar R$ 50 na carne é o mesmo que ganhar R$ 200 e pagar R$ 100; o que importa é quanto a renda compra.
>
> Etiquetas: **[fato]** dado oficial ou documento verificado; **[projeção]** previsão de instituição (mercado, IFI, FMI, Banco Mundial, governo); **[opinião]** avaliação de analista, entidade ou campanha; **[proposta]** está no plano registrado; **[declaração]** dito por candidato ou equipe fora do plano; **[calc]** conta feita aqui a partir de dados citados; **[hipótese de modelagem]** escolha nossa, sem fonte, que o modelo deve tratar como incerta. Nada foi inventado; o que não foi achado está em "Lacunas".
>
> Contexto de repositório já reunido (não repetido em detalhe): `research_notes/Propostas e viabilidade dos candidatos/economia_fiscal.md`, `custos_avaliacoes_independentes.md`, `lacunas_finais.md` e o relatório `reports/Propostas e viabilidade dos candidatos.md`. Resultado do 1º turno (TSE, 99,18% das seções, 04/10/2026 21h20): Flávio 47,18%, Lula 44,98% dos válidos; 2º turno em 25/10/2026 (`research_notes/Briefing eleição 2026 complemento/segundo_turno_inicio.md`).

---

## 0. Resumo executivo (o que os dados dizem)

1. **O histórico mostra que poder de compra real depende muito mais de choques externos e de inflação de alimentos do que de anúncios de campanha.** Nos dois mandatos de Lula (2003–2010), o mínimo teve ganho real acumulado de **53,7%** e a inflação de alimentos no domicílio (52,7%) ficou abaixo do IPCA (56,7%), com ajuda do boom de commodities e da apreciação do real (R$ 3,53 → R$ 1,67 por dólar). Em 2019–2022 a renda nominal até foi reposta, mas os alimentos subiram **56,2%** contra 26,9% do IPCA. Quem ganhava o mínimo perdeu: em São Paulo o mínimo comprava 2,04 cestas em 2019 e 1,59 em 2022 [fato, DIEESE].
2. **Linha de base 2026 favorável, com riscos acumulados para 2027.** A renda real habitual está em recorde (R$ 3.777, jun–ago/2026, +3,7% em 12 meses), o desemprego em 5,3% e o IPCA em 12 meses em 4,22% (alimentos no domicílio +2,80%). Por outro lado, o endividamento das famílias está em 49,9% da renda, o comprometimento com o serviço da dívida em 28,7% (recorde da série) e a inadimplência PF em 6,0%. Os combustíveis estão represados por subsídios: a defasagem do diesel é de 102% e a da gasolina de 32% (Abicom, 28/09), com Brent perto de US$ 100 por causa da guerra no Oriente Médio [fato].
3. **Consenso para 2027 (Focus, IFI, Banco Mundial):** PIB de 1,4%–2,0%, IPCA de 4,0%–4,3%, Selic em 12% no fim de 2027, dólar entre R$ 5,2 e R$ 5,3, dívida bruta em ~86% do PIB. Esse consenso é uma **média ponderada pelas probabilidades eleitorais**, não um cenário de um candidato [inferência].
4. **Os bancos projetam câmbio condicional ao vencedor, e quase nada além disso.** Para Flávio: R$ 4,50–5,00 (Goldman, Wells Fargo, JPMorgan e BTG). Para Lula: R$ 5,50–6,00 (JPMorgan R$ 5,50, BTG R$ 5,70–6,00, "vários bancos" R$ 5,80). Ponto de partida: R$ 5,22. O Goldman ressalva que as **políticas adotadas depois da eleição**, mais que o resultado, definem o câmbio. O Morgan Stanley dá Selic de 9,75% a 15,5% no fim de 2027, conforme a credibilidade fiscal, sem atribuir os cenários a candidatos [projeção/opinião].
5. **Canal mais forte do resultado eleitoral para o poder de compra no curto prazo: câmbio → alimentos.** O repasse cambial estimado pelo BC é de 0,10 para o IPCA em 12 meses (0,16 em 24) e de **0,26 para alimentação no domicílio** em 12 meses (0,33 em 24) (RPM mar/2026). Exemplo [calc]: dólar 10% mais caro (cenário Lula pelos bancos) dá +1,0 p.p. no IPCA e +2,6 p.p. nos alimentos em 12 meses. Dólar 7% mais barato (cenário Flávio) dá −0,7 p.p. e −1,8 p.p. A ressalva é que esses choques só persistem se a política fiscal confirmar a expectativa.
6. **Canal mais forte para a renda: salário mínimo e transferências.** A regra atual (INPC + PIB de t−2, com teto de 2,5% real) dá ~2%–2,5% de ganho real ao ano e atinge **61,9 milhões** de pessoas com renda referenciada no mínimo [fato, DIEESE]. Lula mantém a regra. Flávio declarou em 03/10 que não mexe na Previdência nem na valorização do mínimo, e Sachsida disse em 25/09 que a vinculação aos benefícios fica. Mas o plano é vago e o ajuste prometido (R$ 190 bi) não fecha sem despesa obrigatória. Por isso é **incerteza de modelagem** [declaração/inferência].
7. **Propostas com efeito sobre preços que dependem do Congresso e só valem depois de 2029:** o IVA de 20% de Flávio (o IBS só entra de 2029 a 2033) e o fim da escala 6x1 (PEC aprovada na Câmara, à espera do plenário do Senado). Pelo efeito direto, o IVA a 20% reduziria preços em 1,6% (se 20% for a alíquota média efetiva) a 6,25% (se for a alíquota de referência) nos bens tributados. O custo fiscal é de R$ 150 bi a R$ 560 bi por ano, o que pode anular o ganho via prêmio de risco e câmbio [calc].

---

## 1. Como medir "poder de compra real" no modelo

**Definição operacional** [hipótese de modelagem, padrão da literatura]:

- Poder de compra da família *f* no ano *t* = renda disponível nominal(*f*, *t*) ÷ índice de preços da cesta de consumo da família(*f*, *t*).
- Para famílias de baixa renda, usar a ponderação do **INPC** (1 a 5 SM), não a do IPCA. Os alimentos pesam mais nela.
- Métrica intuitiva (a do exemplo do usuário): **horas de trabalho, ganhando o mínimo, para comprar a cesta básica** = (custo da cesta ÷ salário mínimo) × 220 h. Confere com o DIEESE: R$ 779,95 ÷ R$ 1.621 × 220 = 105,85 h = 105h51 (jun/2026) [calc/fato].

**Pesos no índice (ago/2026, IBGE/SIDRA tabelas 7060 e 7063)** [fato]:

| Item | Peso IPCA (%) | Peso INPC (%) |
|---|---|---|
| Alimentação no domicílio | 15,42 | 18,89 |
| Carnes | 2,83 | 3,50 |
| Gasolina | 5,14 | 4,82 |
| Óleo diesel (direto) | 0,26 | — |
| Energia elétrica residencial | 4,30 | 5,29 |
| Gás de botijão | 1,24 | 1,80 |
| Ônibus urbano | 1,11 | 2,20 |

Fonte: [IBGE SIDRA, tabela 7060 (IPCA) e 7063 (INPC), variáveis 66/45, ago/2026](https://apisidra.ibge.gov.br/).

**Arquétipos sugeridos para o modelo** [hipótese de modelagem]:
1. Trabalhador formal que ganha 1 SM (cesta INPC, renda = SM).
2. Aposentado ou BPC no piso (renda = SM, sem IR).
3. Família no Bolsa Família (benefício médio citado de R$ 691 em 2026, ver `economia_fiscal.md`; cesta INPC com peso maior de alimentos).
4. Trabalhador mediano (renda habitual ~R$ 3.777; ganha com a isenção do IR até R$ 5 mil, cesta IPCA).
5. Trabalhador de R$ 5–10 mil (isenção parcial até R$ 7.350, mais exposto a crédito e juros).
6. Endividado (comprometimento de renda acima de 30%), sensível à Selic.

---

## 2. Histórico: poder de compra real por período de governo

### 2.1 Tabela-síntese

| Indicador | 2003–2010 (Lula 1–2) | 2011–2016 (Dilma*) | 2016–2018 (Temer) | 2019–2022 (Bolsonaro) | 2023–2026 (Lula 3) |
|---|---|---|---|---|---|
| Ganho real acumulado do salário mínimo (reajustes de abr/03 a jan/10; jan/11–jan/16; jan/17–jan/18; jan/19–jan/22; jan/23–jan/26) | **+53,7%** | **+15,3%** | **−0,3%** | **+1,2%** | **+11,5%** |
| IPCA acumulado | 56,7% (5,8% a.a.) | 49,4% (6,9% a.a.) | 6,8% (2017–18; 3,3% a.a.) | 26,9% (6,1% a.a.) | 14,3% em 2023–25 (4,6% a.a.); 2026 até ago: 3,11% |
| Alimentação no domicílio acumulada | 52,7% (5,4% a.a.) | 65,2% (8,7% a.a.) | −0,5% (2017–18) | **56,2% (11,8% a.a.)** | 9,2% em 2023–25 (3,0% a.a.); 2026 até ago: 3,44% |
| Alimentos − IPCA (p.p. a.a.) | −0,4 | +1,8 | −3,6 | **+5,7** | −1,6 |
| Renda real habitual (PNADC, out–dez, R$ a preços recentes) | n.d. (PNADC começa em 2012) | 3.189 (2012) → 3.348 (2014) → 3.260 (2016) | 3.260 → 3.351 (2018) | 3.351 → 3.068 (2021) → 3.317 (2022): **−1,0%** | 3.317 → 3.742 (2025) → 3.777 (jun–ago/26): **+13,9%** |
| Desemprego PNADC (out–dez) | n.d. (PME metropolitana, não comparável; ver Lacunas) | 6,9% (2012), 6,2% (2013, mínima), 6,6% (2014) → 12,1% (2016) | 12,1% → 11,7% (2018) | 11,1% (2019) → 14,2% (2020) → 7,9% (2022); pico de 14,8% no tri fev–abr/2021 | 7,4% (2023) → 5,1% (2025) → 5,3% (jun–ago/26) |
| Cesta básica em horas de trabalho no SM (DIEESE, média das capitais) | ~144h (2003) → ~98h (2010) [ver nota] | 88h21 (mai/2012) | n.d. | 124h08 (abr/2022, pico); 120h52 (mai/2022) | 105h43 (abr/2025) → 100h52 (abr/2026) → 105h51 (jun/2026) |
| Cestas básicas compradas pelo SM em São Paulo (média anual) | n.d. | n.d. | n.d. | 2,04 (2019) → 1,88 → 1,68 → **1,59 (2022)** | 1,71 (2023) → 1,75 (2024) → 1,75 (2025) → **1,93 (jan/26)** |
| Endividamento das famílias com o SFN / renda 12m (BC, SGS 29037) | 16,5% (jan/2005) → 34,0% (dez/2010) | 39,2% (dez/2014) | 38,1% (dez/2016) → 39,0% (dez/2018) | 41,5% (dez/2019) → 49,1% (dez/2022) | 49,7% (dez/2025) → **49,9% (jul/2026)** |
| Comprometimento de renda com o serviço da dívida (SGS 29034) | 17,0% (mar/2005) → 24,0% (dez/2010) | 23,5% (2014) | 23,2% (2016) → 22,6% (2018) | 22,7% (2019) → 27,6% (2022) | 28,1% (2025) → **28,7% (jul/2026)** |
| Inadimplência PF, carteira total (SGS 21084)** | n.d. | 3,7% (dez/2014) | 4,0% (dez/2016) → 3,3% (dez/2018) | 3,9% (dez/2022) | 5,1% (dez/2025) → **6,0% (ago/2026)** |
| Pobreza / extrema pobreza (IBGE SIS, linhas do Banco Mundial) | n.d. nesta rodada | 34,7% / 6,6% (2012) | n.d. | **36,8% / 9,0% (2021, pico da série)** → 31,6% / 5,9% (2022) | 27,3% / 4,4% (2023) → **23,1% / 3,5% (2024, mínimo da série)** |
| Selic no fim do período | 25,0% (dez/02) → 10,75% (dez/10) | 11,75% (dez/14) → 14,25% (mai/16) | 6,50% (dez/18) | 13,75% (dez/22) | 15,0% (dez/25) → 13,75% (out/26) |
| Dólar no fim do período (PTAX) | R$ 3,53 (dez/02) → R$ 1,67 (dez/10) | R$ 2,66 (dez/14) → R$ 3,49 (mai/16) | R$ 3,87 (dez/18) | R$ 5,22 (dez/22) | R$ 5,50 (dez/25) → R$ 5,22 (02/10/26) |

\* Dilma governou até mai/2016; o mínimo de jan/2016 e a inflação de 2016 entram na coluna dela por convenção de ano-calendário. O reajuste de jan/2019 (+1,14% real) foi decretado por Bolsonaro com a regra da Lei 13.152/2015 e está na coluna dele.
\*\* A identificação das séries do SGS (21084 = inadimplência PF total; 20716 = taxa média PF total; 20740 = PF recursos livres) é nossa e convém confirmar no SGS antes de publicar.

**Fontes da tabela:**
- Salário mínimo: [DIEESE, Nota Técnica 289, 22/12/2025](https://www.dieese.org.br/notatecnica/2025/notaTec289salarioMinimo.pdf), Tabela 1 (reajustes reais por data, INPC). Acumulados por período [calc] a partir da tabela. Total de abr/2002 a jan/2026: nominal +710,5%, INPC +306,7%, real +99,3% [fato].
- IPCA e alimentação no domicílio: [IBGE SIDRA, tabelas 1737, 655, 2938, 1419 e 7060](https://apisidra.ibge.gov.br/). Acumulados [calc]. 2025: IPCA 4,26%, alimentação no domicílio 1,43%. 12 meses até ago/2026: IPCA 4,22%, alimentação e bebidas 3,53%, alimentação no domicílio 2,80% [fato]. Atenção: um agregador citou "alimentação e bebidas 7,42% em 12 meses", o que **não confere** com o SIDRA.
- Renda e desemprego: [IBGE SIDRA, tabelas 6390 (v5933) e 6381 (v4099)](https://apisidra.ibge.gov.br/). 2025 em média anual: renda real de R$ 3.560 (+5,7%) e desemprego de 5,6%, mínima da série ([IBGE, release 2025 anual](https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/45759-pnad-continua-em-2025-taxa-anual-de-desocupacao-foi-de-5-6-enquanto-taxa-de-subutilizacao-foi-14-5), via resumo de busca). Jun–ago/2026: R$ 3.777, massa real recorde de R$ 385,6 bi, 103,5 milhões de ocupados, informalidade de 37,5% ([Diario de Pernambuco, 29/09/2026](https://www.diariodepernambuco.com.br/economia/2026/09/11725242-desemprego-fica-em-53-ate-agosto-e-populacao-ocupada-atinge-recorde-aponta-ibge.html)).
- Cesta em horas: mai/2012 e abr–mai/2022 ([Money Times, 11/07/2022, dados do DIEESE](https://www.moneytimes.com.br/tempo-de-trabalho-para-comprar-cesta-basica-com-salario-minimo-aumentou-36-e-10-anos/)); abr/2025, abr/2026 e jun/2026 ([CNN Brasil, jul/2026, Conab/DIEESE](https://www.cnnbrasil.com.br/economia/money/macroeconomia/cesta-basica-exige-105-horas-de-trabalho-e-consome-52-do-salario-minimo/); [DIEESE, abr/2026](https://www.dieese.org.br/analisecestabasica/2026/202604cestabasica/index.html?page=3)). **Nota sobre 2003 e 2010:** um trabalho acadêmico (Unilasalle) dá a cesta em 65,65% do SM em 2003 e 44,50% em 2010, sem a cidade identificada (provavelmente Porto Alegre). Convertido pela fórmula de 220 h, isso dá ~144h e ~98h [calc]. Usar só como ordem de grandeza ([PDF Unilasalle](https://www.unilasalle.edu.br/uploads/files/c724b7ef85e0e9a9854ab06b0a585c87.pdf), não aberto: 503). **Quebra de série:** desde ago/2025 a pesquisa cobre 27 capitais (antes eram 17), em parceria com a Conab ([Agência Gov, ago/2025](https://agenciagov.ebc.com.br/noticias/202508/parceria-garante-monitoramento-de-precos-da-cesta-basica-de-alimentos)).
- Cestas por SM em São Paulo: DIEESE NT 289, Gráfico 2 (médias anuais de 2019 a 2025, estimativa para jan/26).
- Endividamento, comprometimento, inadimplência, Selic e câmbio: [BCB SGS, séries 29037, 29034, 21084, 432 e 1](https://api.bcb.gov.br/).
- Pobreza: [IBGE SIS 2025, divulgada em 03/12/2025](https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/45344-8-6-milhoes-de-pessoas-sairam-da-pobreza-entre-2023-e-2024); [IBGE, 2021 recorde](https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/35687-em-2021-pobreza-tem-aumento-recorde-e-atinge-62-5-milhoes-de-pessoas-maior-nivel-desde-2012) (via resumos de busca). Sem os programas sociais, a extrema pobreza de 2024 seria de 10,0% e não de 3,5%, e a pobreza de 28,7% e não de 23,1% [fato, SIS].

### 2.2 Fatores que confundem a atribuição a governos (importante para não "dar crédito" errado)

- **2003–2010:** superciclo de commodities, termos de troca favoráveis e apreciação forte do real (de R$ 3,53 para R$ 1,67). Isso barateou alimentos e importados. A alimentação no domicílio subiu 6,72% em 2003 e quase nada de 2004 a 2006 (2,57%; 0,59%; −0,16%), depois saltou em 2007–08 (12,4%; 10,7%) com o pico das commodities agrícolas. A crise global de 2008–09 foi breve no Brasil. Bônus demográfico [contexto conhecido; a atribuição ao ciclo é consenso na literatura, não reverificada aqui].
- **2011–2016:** fim do superciclo (2011–2014), "Nova Matriz" (controle de preços administrados como combustíveis e energia em 2012–14), seguida do **tarifaço de 2015** (IPCA de 10,67%, alimentos +12,9%) e da recessão de 2015–16. Seca e choques de oferta de alimentos (2012–13, 2015–16).
- **2016–2018:** recessão e desemprego alto puxam a inflação para baixo. Safra recorde de 2017 (alimentos −4,85%). Teto de gastos.
- **2019–2022:** **pandemia** (renda média de 2020 inflada por efeito composição: os informais de baixa renda saíram da ocupação), auxílio emergencial em 2020, **inflação global** de 2021–22 (energia, fertilizantes, guerra na Ucrânia a partir de fev/2022), dólar acima de R$ 5, cortes de ICMS e tributos de combustíveis em 2022. O DIEESE registra **alta de 44,3% dos alimentos de 2020 a 2022** e o fim do ganho real do mínimo ([NT 289](https://www.dieese.org.br/notatecnica/2025/notaTec289salarioMinimo.pdf)).
- **2023–2026:** mercado de trabalho apertado, transferências maiores (Bolsa Família), safra grande e queda de alimentos em 2023 e 2025, real apreciado em 2025–26, isenção do IR até R$ 5 mil (2026). Ao mesmo tempo, **choque do petróleo de 2026** (guerra no Oriente Médio, Brent perto de US$ 100–108) amortecido por subsídios e cortes de tributos de R$ 37,5 bi de mar. a set/2026. Selic de 15% de jun/2025 a fev/2026.
- **Percepção x dado:** a Eurasia (Christopher Garman, 18/08/2026) cita pesquisa com **62% dizendo ter perdido poder de compra**, apesar de renda real crescendo 4%–6% ([Bloomberg Línea, 18/08/2026](https://www.bloomberglinea.com.br/brasil/mercado-exagera-no-grau-de-favoritismo-de-lula-na-eleicao-diz-eurasia/)). Explicações plausíveis [inferência]: memória do **nível** de preços dos alimentos (ainda bem acima de 2019 em horas de trabalho) e o serviço da dívida, que come 28,7% da renda. O modelo deve reportar o **nível** (horas por cesta, cestas por SM) e não só a variação.

---

## 3. Linha de base 2026 e consenso 2027–2030

### 3.1 Situação atual (fatos)

| Variável | Valor | Data / fonte |
|---|---|---|
| IPCA 12 meses | 4,22% | ago/2026, IBGE (SIDRA) |
| IPCA acumulado no ano | 3,11% | jan–ago/2026, IBGE |
| Alimentação no domicílio, 12 meses | 2,80% | ago/2026, IBGE |
| Selic | 13,75% | após o corte de set/2026 ([Bloomberg Línea/Goldman, 01/10/2026](https://www.bloomberglinea.com.br/mercados/dolar-pode-ir-de-r-450-a-r-580-apos-eleicao-e-depende-do-fiscal-segundo-o-goldman/)); o ciclo de cortes começou em mar/2026, a partir de 15% ([Banco Mundial MPO](https://thedocs.worldbank.org/en/doc/e408a7e21ba62d843bdd90dc37e61b57-0500032021/related/mpo-bra.pdf)) |
| Dólar (PTAX) | R$ 5,2238 | 02/10/2026, BCB SGS 1 |
| Desemprego | 5,3% | jun–ago/2026, PNADC |
| Renda real habitual | R$ 3.777 (+3,7% a/a) | jun–ago/2026, PNADC |
| Salário mínimo | R$ 1.621 (+6,79%; real +2,49%) | jan/2026, DIEESE NT 289 |
| Mínimo previsto para 2027 | R$ 1.741 (+7,4%) | PLOA, [Agência Brasil, ago/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-08/salario-minimo-devera-subir-para-r-1741-em-2027) |
| Cesta básica (27 capitais) | R$ 779,95; 105h51; 52,02% do SM líquido | jun/2026, DIEESE/Conab |
| Endividamento / comprometimento de renda | 49,86% / 28,72% | jul/2026, BCB |
| Juros médios PF (total) / PF recursos livres | 38,2% / 61,7% a.a. | ago/2026, BCB SGS 20716 / 20740 |
| Spread bancário | 20,9 p.p. | jul/2026, BC via [IFI RAF 116](https://www12.senado.leg.br/ifi/ultimas-publicacoes/relatorio-de-acompanhamento-fiscal-set-2026) |
| Dívida bruta (DBGG, metodologia BC) | 82,9% do PIB | ago/2026 (ver `economia_fiscal.md`) |
| Títulos indexados à Selic na DPF | 46,4% (contra 35,7% em dez/2023) | jul/2026, IFI RAF 116 |
| Brent | ~US$ 101–108 | 09–16/09/2026 ([Agência Brasil, 09/09/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-09/novas-medidas-para-combustiveis-terao-impacto-de-r-7-bilhoes-por-mes); [InfoMoney, 16/09/2026](https://www.infomoney.com.br/mercados/risco-de-restricao-pontual-de-diesel-volta-ao-radar-diante-de-defasagem-da-petrobras/)) |
| Defasagem de combustíveis (Abicom) | diesel 102% (R$ 3,34/l); gasolina 32% (R$ 0,95/l) | 28/09/2026 ([BM&C](https://bmcnews.com.br/petroleo-e-energia/defasagem-da-petrobras-chega-a-102-no-diesel/), via resumo de busca) |
| Medidas para combustíveis | subvenção do diesel de R$ 1,12 + R$ 1,00/l (total de R$ 2,12/l, prorrogada por 30 dias em 28/09); PIS/Cofins da gasolina reduzido em R$ 0,63/l; etanol zerado (R$ 0,19/l); R$ 7 bi/mês; R$ 37,5 bi de mar. a set/2026 | [Agência Brasil, 09/09/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-09/novas-medidas-para-combustiveis-terao-impacto-de-r-7-bilhoes-por-mes); [Mix Vale, 28/09/2026](https://www.mixvale.com.br/2026/09/28/governo-federal-prorroga-subvencao-ao-oleo-diesel-por-30-dias/) |
| Isenção do IR até R$ 5 mil (Lei 15.270/2025) | redução de até R$ 312,89/mês; isenção parcial até R$ 7.350; >10 mi de beneficiários (até ~16 mi isentos); renúncia de ~R$ 25–31 bi/ano, compensada por 10% retido na fonte sobre dividendos acima de R$ 50 mil/mês e imposto mínimo para renda acima de R$ 600 mil/ano | [Fecomércio-RS](https://fecomercio-rs.org.br/noticiadetalhe/2025/12/01/Lei-n-15-270-2025-Ampliacao-da-isencao-do-Imposto-de-Renda/cec96f0a-abba-464e-936f-6b3c65752264); [CRC-MA](https://crcma.org.br/noticias/isencao-do-ir-ate-r-5-mil-pode-injetar-r-17-bi-no-consumo-de-bens-e-de-servicos-mas-gera-preocupacoes-fiscais-em-medio-prazo) (via resumo de busca) |
| Acordo Mercosul–UE | aplicação provisória desde 01/05/2026; >80% das exportações brasileiras à UE com tarifa zero | [Agência Brasil/CNI, abr/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-04/cni-acordo-mercosul-ue-zera-tarifas-de-80-das-exportacoes-europa); [Comissão Europeia](https://commission.europa.eu/topics/trade/eu-mercosur-trade-agreement_pt) |

### 3.2 Projeções de consenso (não condicionais)

| Variável | 2026 | 2027 | 2028 | 2029 | 2030 | Fonte |
|---|---|---|---|---|---|---|
| IPCA (%) — Focus | 4,99 | 4,31 | 3,80 | 3,50 | n.d. | [Focus de 28/09/2026 via Eu Quero Investir](https://euqueroinvestir.com/economia/boletim-focus-mercado-projeta-queda-da-selic-so-para-2028) |
| Selic, fim do ano (%) — Focus | 13,50 | 12,00 | 10,50 | 10,00 | n.d. | idem |
| PIB (%) — Focus | 1,86 | 1,36 | 1,83 | 2,00 | n.d. | idem |
| Dólar, fim do ano — Focus | 5,20 | 5,28 | 5,30 | 5,36 | n.d. | idem |
| PIB / IPCA / Selic / dólar — IFI (RAF 116, cenário de set/2026) | 2,0 / 5,0 / 14,0 / 5,2 | 1,8 / 4,0 / 12,0 / 5,2 | — | — | — | [IFI RAF 116, 17/09/2026](https://www12.senado.leg.br/ifi/ultimas-publicacoes/relatorio-de-acompanhamento-fiscal-set-2026), p. 57 |
| Juro real ex-ante (IFI) | 7,5 | 5,5 | — | — | — | idem |
| Massa salarial, crescimento (IFI)* | 5,1 | 3,4 | — | — | — | idem |
| Ocupação, crescimento (IFI) | 1,1 | 0,7 | — | — | — | idem |
| Primário consolidado (% PIB, IFI) | −0,5 | −0,7 | — | — | — | idem |
| Dívida bruta (% PIB, IFI) | 82,5 | 86,4 | — | >100% em 2032 | — | idem; [Agência Senado, 25/06/2026](https://www12.senado.leg.br/noticias/materias/2026/06/25/ifi-proximo-presidente-da-republica-tera-de-enfrentar-decisoes-fiscais-dificeis) |
| PIB / IPCA / Selic / dólar / Brent — governo (PLOA 2027, grade SPE de jul/2026) | — | 2,5 / 3,6 / 12,0 / 5,3 / **US$ 71** | — | — | — | IFI RAF 116, Tabela 1 |
| Brent — EIA/DoE (mai/2026) | US$ 95 | US$ 79 | — | — | — | [eixos, 12/05/2026](https://eixos.com.br/petroleo-e-gas/nos-eua-doe-corta-projecao-do-brent-para-2026-a-us-95-e-sobe-preco-medio-para-us-79-em-2027/) |
| PIB — Banco Mundial (GEP, jun/2026) | 1,9 | 2,0 | 2,2 | — | — | [GEP jun/2026](https://thedocs.worldbank.org/en/doc/2b672b3b0415d6b66c45b66579db4ef5-0050012026/original/GEP-Jun-2026.pdf); o MPO de abr/2026 dava 1,6 / 1,8 / 2,2 ([MPO Brasil](https://thedocs.worldbank.org/en/doc/e408a7e21ba62d843bdd90dc37e61b57-0500032021/related/mpo-bra.pdf)) |
| PIB — FMI (WEO, atualização de jul/2026) | 2,4 | 2,2 | — | — | ~2,5 no médio prazo | [Rio Times](https://www.riotimesonline.com/imf-brazil-gdp-forecast-2026-2027-slowdown-weo-2026/), [Global Times](https://www.globaltimes.cn/page/202607/1365729.shtml) (via resumo de busca); Artigo IV de 01/06/2026: inflação na meta de 3% até meados de 2028 e crescimento de médio prazo de ~2,5% ([FMI](https://www.imf.org/pt/news/articles/2026/06/01/pr26179-brazil-imf-staff-completes-2026-article-iv)) |
| Dívida bruta (metodologia FMI) | ~96,5–97,8 | ~100 | — | — | estabiliza em ~106% por volta de 2035 sem ajuste | via imprensa (ver `economia_fiscal.md`) |

\* A IFI não diz na tabela se a massa salarial é real ou nominal. Pelo contexto (2,7%–5,1%, com IPCA de 4%–5%), parece real [inferência; confirmar]. Se for real, a renda real média por ocupado cresceria ~2,7% em 2027 (3,4% − 0,7%) [calc].

**Leitura** [inferência]: o Focus de 28/09/2026 foi coletado com o mercado em ~50/50 entre os candidatos ([Money Times](https://www.moneytimes.com.br/50-50-entre-lula-e-flavio-bolsonaro-por-que-o-mercado-mudou-de-aposta-e-o-que-isso-significa-para-bolsa-e-dolar-lils/)). Portanto, é aproximadamente a **média dos dois cenários**. No Monte Carlo, o consenso deve ser a âncora, e os choques condicionais devem ser aplicados de forma que a média ponderada pelas probabilidades volte perto do consenso.

### 3.3 Cenários não condicionais do Morgan Stanley (30/08/2026)

| Cenário | Selic fim de 2027 | IPCA 2027 | Dólar | PIB 2027 | Desemprego 2027 | Premissa |
|---|---|---|---|---|---|---|
| Base | 11,0% | 4,0% | n.d. | 1,2% | 6,7% (5,6% hoje) | ajuste fiscal moderado, insuficiente para mudar o humor dos investidores |
| Negativo | 15,5% | 5,0% | R$ 6,00 | 0,2% | n.d. | novo governo sem plano crível de estabilização da dívida |
| Otimista | 9,75% | 3,8% | R$ 4,50 | 1,5% | 6,5% | "choque de gradualismo": programa fiscal de longo prazo ganha credibilidade imediata |

Fonte: [Seu Dinheiro, 30/08/2026](https://www.seudinheiro.com/2026/economia/a-selic-pode-terminar-2027-em-975-ao-ano-ou-subir-para-155-e-o-que-vai-definir-a-taxa-nao-e-a-economia-mlim/) [projeção]. O MS não atribui probabilidades nem candidatos aos cenários. A conclusão citada é que "a variável que vai decidir o futuro dos juros é a eleição de 2026 e a credibilidade fiscal do próximo governo".

---

## 4. Projeções condicionais aos candidatos

### 4.1 Bancos e casas de análise (câmbio, juros, bolsa)

| Instituição | Data | Flávio vence | Lula vence | Premissas declaradas | Tipo |
|---|---|---|---|---|---|
| JPMorgan | ~28/09–03/10/2026 | dólar a R$ 4,90 (em outra citação, R$ 4,80); Selic poderia ir ao neutro (~6% real / ~10% nominal) com agenda de reformas; MSCI Brasil +21% a +41% (P/L de 8,6 para até 13,3) | dólar a R$ 5,50 | referência à reforma da Previdência de 2019 (bolsa +130% no período) | projeção ([Times Brasil](https://timesbrasil.com.br/eleicoes-2026/eleicao-wall-street-lula-flavio-bolsonaro-bolsa-cambio/); [Mix Vale, 28/09/2026](https://www.mixvale.com.br/2026/09/28/jpmorgan-projeta-dolar-entre-r-490-e-r-550-apos-as-eleicoes/)) |
| Goldman Sachs (Teresa Alves) | 01/10/2026 | otimista: R$ 4,50–4,80; "valor justo" de R$ 4,80 sem prêmio fiscal residual; caso extremo de R$ 4,35 (precedente da Colômbia, "improvável") | moderado: R$ 5,40 (prêmio fiscal de set/2024); pessimista: R$ 5,80 (prêmio volta à máxima de dez/2024, depreciação de ~14%) | "mudanças nas políticas depois das eleições, mais do que o resultado em si, podem levar o real a diferentes níveis"; ~80 bps de prêmio nos DI de 2 a 10 anos que podem ser eliminados num resultado favorável ao mercado | projeção/opinião ([Bloomberg Línea, 01/10/2026](https://www.bloomberglinea.com.br/mercados/dolar-pode-ir-de-r-450-a-r-580-apos-eleicao-e-depende-do-fiscal-segundo-o-goldman/); [Money Times, 02/10/2026](https://www.moneytimes.com.br/eleicao-pode-virar-o-jogo-do-dolar-o-que-esperar-de-cambio-e-juros-apos-o-1o-turno/)) |
| Wells Fargo | ~out/2026 | dólar a R$ 4,75 | (R$ 5,80, atribuído a "bancos americanos") | — | projeção (Money Times, 02/10/2026) |
| BTG Pactual | 01/10/2026 | real +5% (~R$ 5,00); Ibovespa +11% a +20% (até +32% a +45% num cenário de 1 desvio-padrão) | real −10% a −15% (R$ 5,70–6,00); Ibovespa ~170 mil (−10%) | com Flávio, "medidas mais decisivas para enfrentar desequilíbrios fiscais urgentes" | projeção ([Exame, 01/10/2026](https://exame.com/invest/mercados/com-eleicao-no-radar-btg-trava-carteira-de-acoes-e-aponta-potenciais-campeas/)) |
| Citi (Leonardo Porto) | 03/10/2026 | posicionado para apreciação do real via opções | — | ajuste necessário de 3% a 3,5% do PIB, estrutural, não por venda de ativos | opinião ([Times Brasil](https://timesbrasil.com.br/eleicoes-2026/eleicao-wall-street-lula-flavio-bolsonaro-bolsa-cambio/)) |
| XP (Caio Megale) | 2026 (antes do 1º turno) | — | — | Selic de 13,75% no fim de 2026 e de 11,5% no fim de 2027, "condicionada à continuidade do aperto e ao avanço do ajuste fiscal"; dólar a R$ 5,00 no fim de 2026; Sbardelotto (31/08): mantido o crescimento real da despesa de 2,5%, o ajuste terá de vir pela receita | projeção não condicional ([BPMoney](https://bpmoney.com.br/brasil/xp-eleva-projecao-para-selic-no-fim-de-2026-para-1375-e-ve-dolar-a-r-5/); ver `lacunas_finais.md`) |
| Eurasia (Garman) | 18/08 e set/2026 | — | — | probabilidade de Lula: 60% (ago) e 55% (set); "o mercado exagera" o favoritismo | opinião ([Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/mercado-exagera-no-grau-de-favoritismo-de-lula-na-eleicao-diz-eurasia/); [Money Times](https://www.moneytimes.com.br/sem-50-50-eurasia-ve-55-de-chance-de-vitoria-de-lula-mas-margem-e-apertada-diz-cientista-politico-apsa/)) |
| Itaú, Bradesco, Santander, Tendências, LCA, 4intelligence | — | **não encontrado** projeção condicional por candidato | — | Itaú (Mesquita, fim de 2025): ajuste necessário de 4% do PIB; Bradesco Asset (Funchal, 29/09): espera algum pacote qualquer que seja o vencedor | ver `lacunas_finais.md` |
| Análise sem autoria confirmada (Money Times) | set/2026 | política mais austera, mas efeito nos juros só a partir do 2º tri de 2028 | continuidade não muda o quadro fiscal no curto prazo | — | opinião (via resumo de busca) |

**Síntese para o modelo** [calc, a partir de R$ 5,22]:
- Flávio: dólar de R$ 4,50 a R$ 5,00, ou **−4% a −14%**. Moda em ~R$ 4,80–4,90 (−6% a −8%).
- Lula: dólar de R$ 5,40 a R$ 6,00, ou **+3% a +15%**. Moda em ~R$ 5,50–5,80 (+5% a +11%).
- Diferença entre os cenários: ~R$ 0,60–1,30, ou **~12%–25%** no câmbio.
- Os números são **choques de impacto** (semanas ou meses após o 2º turno). A persistência depende do que o vencedor fizer (Goldman). Nenhum banco publicou IPCA, PIB ou salário real condicionais ao candidato. O efeito sobre preços tem de ser **derivado** com os repasses da seção 6.

### 4.2 Visões heterodoxas, sindicais e de centro-esquerda

- **Economistas heterodoxos na CartaCapital (01/10/2026)** [opinião]: Marcelo Manzano (Unicamp) diz que, com cenário externo benigno e PIB de 3,5%–4% num governo Lula, haveria "estabilização da relação dívida pública-PIB, equacionando o problema de forma virtuosa"; para ele, Flávio representaria a "destruição definitiva" das políticas de inclusão de 1988. Saulo Abouchedid (Facamp): "haverá mais espaço para a queda de juros no Lula 4"; com o bolsonarismo, "o espelho do Brasil amanhã [...] é a Argentina hoje". José Augusto Gaspar Ruas: "Não acredito que reste muito mais fôlego para continuar com o crescimento puxado por um consumo". Passos Santos: "ampliar a base fiscal" ([CartaCapital](https://www.cartacapital.com.br/carta-capital/sobe-e-desce/); veículo de esquerda).
- **DIEESE** [opinião sindical, com dados]: a valorização do mínimo é "uma das políticas mais relevantes de combate à pobreza"; parte do custo volta como arrecadação. Sem ganho real (2019–22), houve perda frente aos alimentos ([NT 289](https://www.dieese.org.br/notatecnica/2025/notaTec289salarioMinimo.pdf)). Sobre a **PEC 12/2026** (contrato por hora, apoiada pela campanha de Flávio): a renda média dos intermitentes é **58% do salário mínimo**; a PEC "transfere aos trabalhadores os riscos das flutuações" e aumenta a variabilidade da renda ([Condsef, jun/2026](https://www.condsef.org.br/noticias/dieese-aponta-impactos-pec-12-2026-sobre-jornada-trabalho-direitos-trabalhistas); [Hora do Povo](https://horadopovo.com.br/pec-apoiada-por-bolsonaristas-reduz-direitos-e-seguranca-da-renda-afirma-dieese/)).
- **Fundação Perseu Abramo** (ligada ao PT, 08/09/2026) [opinião partidária]: a desvinculação das aposentadorias do mínimo atribuída "à oposição" economizaria R$ 1,1 tri em dez anos e "condena milhões de idosos [...] a uma perda contínua de poder de compra". A campanha de Flávio negou em 25/09 ([FPA](https://fpabramo.org.br/plano-da-oposicao-preve-desvincular-aposentadorias-do-minimo-para-cortar-r-11-tri-economistas-alertam-para-explosao-da-pobreza/)).
- **OPEB (25/09/2026)** [opinião crítica]: compara o plano de Flávio ao de Milei (inflação controlada e superávit, mas desemprego de 7,9%, informalidade de 45% e 31 mil empresas fechadas) ([OPEB](https://opeb.org/2026/09/25/entre-a-teoria-e-a-pratica-o-plano-flavio-bolsonaro-sob-a-sombra-da-argentina-de-milei/)).
- **Ipea** (órgão do governo; fev/2026): o fim da 6x1 eleva o custo médio do trabalho celetista em 7,84%, com impacto abaixo de 1% do custo operacional em indústria e comércio ([Poder360](https://www.poder360.com.br/poder-economia/fim-da-escala-6-x-1-elevaria-custo-do-trabalho-em-784-diz-ipea/)).
- **Não encontrados:** Belluzzo, Laura Carvalho e Nelson Barbosa sobre os planos de 2026 (ver `lacunas_finais.md`).

### 4.3 Visões pró-mercado e liberais

- **Instituto Millenium** (Antonio Vladika, 24/06/2026) [opinião]: critica renúncias, subsídios, crédito direcionado e renegociações, com "custo estimado de R$ 140 bilhões", e diz que a população é "obrigada a financiar, com perda de poder de compra" via inflação e juros ([Millenium](https://institutomillenium.org.br/a-politica-que-consome-o-futuro/)). Não analisa o plano de Flávio.
- **CLP:** sem análise dos planos de 2026 localizada. Há uma nota de 2025 com 25 medidas prioritárias ([PDF via Poder360](https://static.poder360.com.br/2025/02/CLP-nota-tecnica-medias-governo-economia-2025-2026.pdf)).
- **Armínio Fraga** (~24/07/2026): "Não descarto uma recessão em 2027" (sobre o governo Lula). **Felipe Salto** (03/10/2026): propor redução de carga tributária é "desconhecimento do Orçamento", o que atinge a promessa do IVA. **Juliana Inhasz (Insper, 24/09)** sobre Flávio: "o problema nesse caso é a ordem dos fatores", cortar imposto antes da compensação. **TAG (André Leite, 29/09):** espera ajuste mais profundo com Flávio; Lula é "um grande ponto de interrogação". Detalhes e links em `lacunas_finais.md`.
- **FGV IBRE (Fernando de Holanda Barbosa Filho):** com o fim da 6x1, o valor adicionado cairia pelo menos 3,9% no cenário favorável (já com ganho de produtividade de 2,5%) e mais de 10% no pior ([Forbes, 02/09/2026](https://forbes.com.br/forbes-money/2026/09/fim-escala-6x1-impactos/)). **CNI:** PIB −0,7% (R$ 76 bi) com 40h ([JB, abr/2026](https://www.jb.com.br/economia/2026/04/1059439-fim-da-escala-6x1-estudos-divergem-sobre-impactos-no-pib-e-inflacao.html)). **Abrasel:** preços em bares e restaurantes +~7%. **Gabriel Barros (ARX):** "risco real de inflação de custos" (Forbes).

---

## 5. Mecanismos: do programa ao poder de compra

Cada item traz: o que cada candidato propõe; o canal; a magnitude disponível; quem ganha e quem perde.

### 5.1 Salário mínimo (renda de 61,9 milhões de pessoas)
- **Regra atual (Lei 14.663/2023 + LC 200/2023):** INPC de 12 meses até novembro + crescimento real do PIB de dois anos antes, **limitado a 2,5%** de ganho real. Em 2026: 4,18% + 2,5% = 6,79%. Sem o teto, o mínimo de 2026 seria R$ 1.636 (+R$ 15) [fato, NT 289]. *Lacuna:* não reverificamos se a Lei 15.077/2024 também fixa um piso de 0,6% para o ganho real. Tratar como incerto.
- **Lula** [proposta]: mantém a valorização real. Ganho real projetado ≈ min(PIB de t−2; 2,5%): 2027 ≈ 2,3% (PIB de 2025); 2028 ≈ 1,9–2,4% (PIB de 2026); 2029 ≈ 1,4–1,8% (PIB de 2027); 2030 ≈ 1,8–2,2% (PIB de 2028) [calc com Focus, IFI e Banco Mundial].
- **Flávio** [declarações]: em 03/10/2026, disse que fará o ajuste "sem mexer na Previdência nem na política de valorização do salário mínimo". Sachsida (25/09): a vinculação mínimo–benefícios será mantida, mas sem esclarecer se o ganho real continua. O plano não trata do tema. Mansueto (BTG) e o Itaú defendem rever a regra para viabilizar o ajuste [opinião] (ver `lacunas_finais.md`).
- **Custo fiscal:** cada R$ 1 no mínimo custa R$ 380,5 mi/ano na folha do INSS (DIEESE) ou ~R$ 455 mi/ano em INSS + BPC ([SpaceMoney](https://www.spacemoney.com.br/economia/macroeconomia/salario-minimo-1741-impacto-inss-bpc-2027/), cálculo em `custos_avaliacoes_independentes.md`). O mínimo de 2027 custa +R$ 54,6 bi.
- **Efeitos colaterais (literatura)** [opinião acadêmica]: Engbom e Moser (2022) atribuem à alta real de 128% do mínimo entre 1996 e 2018 **~45% da queda da desigualdade salarial, sem efeito negativo relevante em emprego ou informalidade** (realocação para firmas mais produtivas) ([resumo em Mínimos Quadrados](https://minimosquadrados.substack.com/p/minimos-quadrados-03-salario-minimo)). Ipea (TD 849, Foguel/Ramos/Carneiro): efeitos agregados negativos sobre emprego e formalidade, "porém as magnitudes reportadas [...] não são expressivas" ([Ipea](https://repositorio.ipea.gov.br/entities/publication/c0d72dcc-c594-4c74-8019-54645681d82b)). O "efeito farol" puxa também os rendimentos informais.

### 5.2 Imposto de renda (isenção até R$ 5 mil, em vigor desde 2026)
- **Lula:** "consolidar" a isenção compensada por tributação de alta renda [proposta].
- **Flávio:** o plano promete "reverter impostos criados ou elevados no governo Lula" [proposta, ver `economia_fiscal.md`]. **Não encontramos** se isso incluiria a retenção de 10% sobre dividendos ou o imposto mínimo da Lei 15.270. Revogar a compensação sem revogar a isenção abriria um buraco de ~R$ 25–31 bi/ano [calc]. Revogar a isenção parece politicamente improvável [hipótese de modelagem].
- **Efeito na renda:** até R$ 312,89/mês (≈R$ 4 mil/ano com o 13º) para quem ganha até R$ 5 mil. Isso equivale a ~8%–10% de aumento da renda líquida de quem ganha R$ 3,5–5 mil [calc aproximado]. Estimativas de consumo: ~54,5% de R$ 31,2 bi (R$ 17 bi) vão para o consumo, e o efeito no PIB é de ~0,2% (CRC-MA, autoria do estudo não identificada).

### 5.3 IVA (IBS/CBS) — a promessa de 20% de Flávio
- **Fatos:** a alíquota de referência estimada é de **28%–28,5%** e a média ponderada efetiva de **~22%**. O IVA deve arrecadar 12,5% do PIB (média de 2012–2021 dos tributos substituídos) ([Bráulio Borges, Blog do IBRE, 27/01/2026](https://blogdoibre.fgv.br/posts/reforma-da-tributacao-indireta-no-brasil-transformacao-historica-que-tem-inicio-em-2026)). Calendário: CBS plena em 2027; IBS cresce de 2029 a 2033 [fato].
- **Flávio** [declaração de 22/06/2026; o plano fala em "reduzir o IVA"]: 20%. Especialistas (KPMG, Simões Pires): estimativa "sem base de dados", "enorme perda de arrecadação", essenciais poderiam encarecer se a redução vier da eliminação de alíquotas reduzidas ([reformatributaria.com](https://www.reformatributaria.com/reforma-tributaria-nas-eleicoes/proposta-de-flavio-bolsonaro-para-iva-de-20-pode-encarecer-produtos-essenciais-dizem-especialistas/)).
- **Efeito direto nos preços** [calc]: preço com imposto ∝ (1 + t). De 28% para 20%: 1,20/1,28 − 1 = **−6,25%** nos bens à alíquota cheia. De 22% (média efetiva) para 20%: **−1,6%** no consumo tributado. Com repasse α. **Atenção ao efeito distributivo:** se o caminho for eliminar exceções (cesta básica zerada, saúde e educação com redução de 60%), a cesta básica pode **subir**. Para o arquétipo de baixa renda, o sinal é ambíguo.
- **Repasse de cortes de IVA (literatura):** assimétrico e incompleto em vários estudos europeus (Benzarti et al.: reduções repassam menos que aumentos). Mas o corte temporário do IVA de alimentos em Portugal (2023) teve repasse **pleno e simétrico** ([J. Public Econ. 2025](https://www.sciencedirect.com/science/article/abs/pii/S0047272725001148); [Observador](https://observador.pt/especiais/apesar-dos-receios-de-medina-supermercados-fizeram-mesmo-o-iva-zero-chegar-as-familias/)). No Brasil (ICMS sobre alimentos), cada 1 p.p. de alíquota mexe ~0,13% no preço, em ~4 meses ([ANPEC 2024](https://www.anpec.org.br/encontro/2024/submissao/files_I/i5-a503da6b13f84b2aeb5f0650f4e7d51e.pdf), via resumo de busca).
- **Custo fiscal:** R$ 150 bi/ano (leitura de média efetiva) a R$ 480–560 bi/ano (leitura de referência, 3,6%–4,2% do PIB), quando o sistema estiver completo [calc, `lacunas_finais.md`]. Pelo canal do prêmio de risco (5.5), isso pode **anular** o ganho de preço.

### 5.4 Combustíveis e Petrobras (fator comum aos dois, mas com custo fiscal diferente)
- **Situação:** preços represados (diesel 102% abaixo da paridade, gasolina 32% abaixo) e subsídios mensais renováveis (R$ 7 bi/mês). Brent esperado de US$ 79 em 2027 (EIA) contra US$ 71 no PLOA [fato/projeção].
- **Lula:** a Petrobras abandonou a paridade de importação em mai/2023 [fato]. A linha de 2026 é de suavização com subsídio e corte de tributo, financiada em parte por imposto de exportação de petróleo de 12% (MP 1.340/2026) [fato, `lacunas_finais.md`].
- **Flávio:** promete "reduzir impostos sobre energia elétrica e combustíveis" [proposta] e revogar o imposto de exportação de petróleo [declaração de 20/03/2026]. Não tem posição explícita sobre a política de preços da Petrobras. Fala em "possivelmente" desinvestir em segmentos da Petrobras [declaração].
- **Choque potencial** [calc]: realinhar a gasolina com +5% a +15% na bomba (depende da fração da refinaria no preço final, não verificada aqui) daria **+0,26 a +0,77 p.p. no IPCA** (peso de 5,14%). O diesel tem peso direto de 0,26%, mas entra no frete e nos alimentos (efeito indireto não quantificado). Se o petróleo cair para ~US$ 79 em 2027, a defasagem se fecha sozinha em parte.

### 5.5 Credibilidade fiscal → câmbio → preços; prêmio de risco → juros → crédito
- **Prêmio de risco (IFI, RAF 116, 17/09/2026)** [fato/estimativa]: a dívida bruta contribui com **3,16 p.p.** para o prêmio da taxa de 5 anos nos 12 meses até ago/2026 (contra 2,10 p.p. em 2011–13), acima da crise de 2014–16. Coeficiente de amostra completa (2007–2026): **+0,03 p.p. de prêmio por +1 p.p. de dívida/PIB**. Janelas móveis de 5 anos: mediana de 0,112 no vértice de 5 anos; nas janelas de 2025–26, **~0,33** (5 e 10 anos). Ou seja, a sensibilidade **cresceu**. Mais títulos atrelados à Selic (46,4% da DPF) aumentam a transmissão.
- **Câmbio → preços:** ver 6.1. É o canal pelo qual "o mercado gostar ou não" do vencedor chega ao prato de comida.
- **Selic → crédito** (BC, Estudo Especial 118/2022): repasse de 1 p.p. da Selic, em 12 meses, para as taxas: cheque especial **+4,43 p.p.**; crédito pessoal **+1,73**; aquisição de outros bens **+1,64**; veículos +0,75; imobiliário +0,43; rural +0,41–0,55. A maior parte vem no primeiro trimestre ([BCB EE 118](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE118_Repasse_da_taxa_Selic_para_o_mercado_de_credito_bancario.pdf)).
- **Selic → inflação** (BC, RI jun/2024, boxe): +1 p.p. na Selic por 4 trimestres dá **−0,27 p.p. no IPCA acumulado em 4 trimestres** no efeito máximo, com pico em ~5 trimestres ([BCB RI jun/2024](https://www.bcb.gov.br/content/ri/relatorioinflacao/202406/ri202406b12p.pdf), via resumo de busca).
- **Endividado:** com comprometimento de 28,7% da renda, 1 p.p. a mais de Selic nas linhas de crédito pessoal e cartão encarece o serviço da dívida. O efeito sobre renda livre depende do prazo médio e da parcela pós-fixada [hipótese de modelagem: elasticidade do comprometimento ≈ 0,1–0,3 p.p. de renda por 1 p.p. de Selic em 12 meses, **sem fonte**; calibrar].

### 5.6 Bolsa Família e transferências
- **Lula:** manter e ampliar Bolsa Família (benefício médio de R$ 691 em 2026, após os R$ 600) e o Auxílio Gás [proposta, `economia_fiscal.md`].
- **Flávio:** Bolsa Família como "ponte para o emprego", sem cortes anunciados, com retorno imediato ao benefício após o seguro-desemprego [proposta]. O ministro José Guimarães diz que o "cardápio de cortes" mira a área social [opinião partidária].
- **Peso no poder de compra dos pobres:** os programas sociais tiram ~6,5 p.p. de população da extrema pobreza (10,0% → 3,5% em 2024) [fato, SIS]. No modelo, a indexação do benefício importa: o Bolsa Família **não tem regra automática de reajuste** [conhecimento geral, não reverificado]. Sem reajuste discricionário, perde para a inflação de alimentos.

### 5.7 Trabalho: fim da 6x1 x contrato por hora (PEC 12/2026)
- **6x1** [fato]: a PEC 221/19 foi aprovada na Câmara em 2 turnos (472 e 461 votos, mai/2026) e na CCJ do Senado (02/09/2026); o plenário deve votar depois do 1º turno (possível esforço concentrado na 2ª semana de outubro). Prevê 40h em 5 dias, sem redução de salário, com transição; dois dias de descanso valem dois meses após a promulgação ([Câmara](https://www.camara.leg.br/noticias/1277141-camara-aprova-em-dois-turnos-fim-da-escala-6x1-com-jornada-maxima-de-40-horas-semanais/); [Estado de Minas, set/2026](https://www.em.com.br/politica/2026/09/7504982-pec-do-fim-da-escala-6x1-aguarda-votacao-final-no-senado-entenda-a-tramitacao-em-setembro-de-2026.html)). Lula apoia. A campanha de Flávio apoia a PEC 12/2026 (de Rogério Marinho, PL-RN), que condiciona menos horas a menos renda.
- **Efeito no poder de compra** [calc/inferência]: para o celetista em 6x1, o **salário-hora** sobe ~10% (44h → 40h com o mesmo salário), mas a renda mensal fica igual. O efeito em preços está concentrado em serviços intensivos em trabalho: Ipea +7,84% no custo do trabalho; Abrasel ~+7% nos preços de bares e restaurantes. Risco de informalização (crítica patronal) contra ganho de produtividade (defensores). A magnitude no IPCA não foi publicada por ninguém que tenhamos achado.
- **Contrato por hora (Flávio):** pode ampliar a ocupação formal [opinião dos defensores], mas reduz a previsibilidade da renda (intermitentes ganham 58% do SM, segundo o DIEESE).

### 5.8 Comércio exterior (tarifas EUA, China, Mercosul–UE)
- O acordo Mercosul–UE vigora provisoriamente desde 01/05/2026 [fato]. Flávio quer "libertar das amarras do Mercosul", ingressar na OCDE, aliar-se aos EUA e abrir a economia gradualmente; o plano não cita BRICS nem Mercosul [proposta/declaração, `custos_avaliacoes_independentes.md`]. Lula mantém Mercosul e BRICS.
- **Tarifas dos EUA ao Brasil em 2026:** situação **não verificada** nesta rodada (as buscas não trouxeram o status). Para o modelo: abertura comercial tende a baratear bens industriais (repasse cambial de 0,12–0,22 nos bens industriais), mas a magnitude por candidato não tem fonte.

---

## 6. Elasticidades e regras de bolso (com fonte)

### 6.1 Repasse cambial (BC, RPM mar/2026, boxe "Repasse cambial: estimativas por projeções locais"; amostra de jul/2006 a dez/2025, controlando por commodities)
- IPCA cheio: **0,10 em 12 meses; 0,16 em 24 meses** (10% de depreciação dá +1,0 p.p. em 12 meses e +1,6 p.p. em 24).
- Modelo semiestrutural do BC: 0,10 no IPCA em 4 trimestres; **administrados 0,18; livres 0,07**.
- **Alimentação no domicílio: 0,26 em 12 meses; 0,33 em 24** ("intenso e bastante rápido"; IC amplo).
- Bens industriais: ~0,12 em 12 meses e ~0,22 em 24 (leitura dos rótulos do gráfico; conferir).
- Serviços: ~0,01–0,03 (estatisticamente ≈ 0).
- Os intervalos de confiança são "bastante amplos": usar distribuição larga.
- Fonte: [BCB, RPM mar/2026, boxe](https://www.bcb.gov.br/content/ri/relatorioinflacao/202603/rpm202603b8p.pdf).
- **Assimetria:** a literatura brasileira sugere repasse maior em depreciações do que em apreciações e dependente do ciclo ([PUC-Rio TD 462](https://www.econ.puc-rio.br/api/uploads/adm/trabalhos/files/td462.pdf); [Ensaios FEE](https://revistas.planejamento.rs.gov.br/index.php/ensaios/article/download/4062/3944/25114)). Magnitude não extraída [hipótese: repasse na apreciação = 50%–100% do repasse na depreciação].

### 6.2 Juros
- Selic → IPCA: −0,27 p.p. no máximo, em 4 trimestres, por +1 p.p. de Selic mantido por 4 trimestres; pico em ~5 trimestres (BC, RI jun/2024).
- Selic → taxas de crédito PF em 12 meses: crédito pessoal 1,73; outros bens 1,64; cheque especial 4,43; veículos 0,75; imobiliário 0,43 (BC EE 118/2022).
- Spread bancário de 20,9 p.p. (jul/2026); taxa PF total de 38,2% a.a. (ago/2026).

### 6.3 Prêmio de risco fiscal
- +1 p.p. de DBGG/PIB → +0,03 p.p. no prêmio de 5 anos (amostra completa); mediana móvel de 0,112; janelas de 2025–26 com ~0,33 (IFI RAF 116, tabelas 10–11 e seção 4).
- A contribuição da dívida ao prêmio é de 3,16 p.p. (12 meses até ago/2026).

### 6.4 Salário mínimo
- Emprego e informalidade: efeito ≈ 0 (Engbom e Moser, 1996–2018) a levemente negativo (Ipea TD 849).
- Fiscal: R$ 380–455 mi por R$ 1 (seção 5.1).
- Massa de renda: +R$ 81,7 bi em 2026 com +R$ 103 (DIEESE).

### 6.5 Choques específicos
- Alimentos − IPCA (2003–2025, anual): média de **+0,87 p.p.**, desvio-padrão de **5,1 p.p.**, mínimo de −7,8 (2017) e máximo de +13,6 (2020) [calc, IBGE]. É a principal fonte de ruído no poder de compra da baixa renda.
- Combustível: 10% na gasolina → ~+0,5 p.p. no IPCA (peso de 5,14%) [calc].
- IVA: −1,6% a −6,25% nos preços dos bens tributados por alíquota, × repasse de 0,5–1,0 [calc].

---

## 7. Tabela de parâmetros para o Monte Carlo

Convenções: "Valor" é a moda ou mediana sugerida; "Faixa" deve virar uma distribuição triangular ou normal truncada (sugestão na coluna "Dist."). L = cenário Lula; F = cenário Flávio; C = comum aos dois. Tudo que é **[hipótese de modelagem]** deve entrar em análise de sensibilidade.

### 7.1 Linha de base (comum)

| # | Parâmetro | Valor | Faixa | Dist. | Fonte / tipo |
|---|---|---|---|---|---|
| C1 | IPCA 2026 (%) | 5,0 | 4,6–5,4 | tri | Focus 28/09 (4,99); IFI (5,0) [projeção] |
| C2 | IPCA 2027 (%), consenso | 4,3 | 3,6–5,0 | tri | Focus (4,31); IFI (4,0); PLOA (3,6); MS (3,8–5,0) [projeção] |
| C3 | IPCA 2028 / 2029 / 2030 (%) | 3,8 / 3,5 / 3,5 | ±1,0 | normal | Focus; 2030 = 2029 [hipótese] |
| C4 | Alimentação no domicílio − IPCA (p.p. a.a.) | +0,9 | DP 5,1; mín −7,8; máx +13,6 | normal ou bootstrap 2003–2025 | IBGE [calc] |
| C5 | PIB 2027 (%) | 1,5 | 0,2–2,5 | tri | Focus 1,36; IFI 1,8; BM 2,0; FMI 2,2; PLOA 2,5; MS 0,2–1,5 [projeção] |
| C6 | PIB 2028–2030 (%) | 2,0 | 1,0–2,5 | tri | Focus 1,8–2,0; BM 2,2; FMI ~2,5 [projeção] |
| C7 | Selic fim de 2026 / 2027 (%) | 13,5 / 12,0 | 2027: 9,75–15,5 | tri | Focus; IFI (14,0 / 12,0); MS [projeção] |
| C8 | Selic 2028 / 2029 (%) | 10,5 / 10,0 | 8,5–14 | tri | Focus [projeção] |
| C9 | Dólar fim de 2026 / 2027 (R$) | 5,20 / 5,28 | 4,50–6,00 | ver L1/F1 | Focus; IFI 5,2 [projeção] |
| C10 | Desemprego 2026 → 2027 (%) | 5,3 → 6,0 | 5,0–6,7 | tri | PNADC; MS base 6,7 [fato/projeção]; moda [hipótese] |
| C11 | Renda real média por ocupado 2027 (%) | +2,0 | 0–3,5 | tri | IFI massa 3,4 − ocupação 0,7 [calc]; desaceleração MS [hipótese] |
| C12 | Renda real 2028–2030 (% a.a.) | +1,5 | −0,5 a +3,0 | tri | [hipótese ancorada no PIB per capita e na produtividade] |
| C13 | Dívida bruta 2027 (% PIB, BC) | 86,4 | 84–90 | tri | IFI [projeção] |
| C14 | Brent 2027 (US$) | 79 | 65–110 | lognormal | EIA (79); PLOA (71); hoje ~100 [projeção] |
| C15 | Realinhamento da gasolina na bomba quando o subsídio acabar (%) | +8 | 0–15 | tri | defasagem de 32% na refinaria (Abicom); fração na bomba [hipótese] |
| C16 | Peso da gasolina / alimentos no domicílio (IPCA; INPC) | 5,14 / 15,42; 4,82 / 18,89 | — | fixo | IBGE ago/2026 [fato] |
| C17 | Salário mínimo 2027 (R$) | 1.741 | 1.735–1.750 | tri | PLOA [fato/projeção] |

### 7.2 Choques condicionais ao vencedor

| # | Parâmetro | Lula (L) | Flávio (F) | Dist. | Fonte / tipo |
|---|---|---|---|---|---|
| L1/F1 | Choque cambial de impacto (% sobre R$ 5,22, nas 4–8 semanas após 25/10) | +8 (faixa de +3 a +15) | −7 (faixa de −14 a −4) | tri | JPM, GS, WF, BTG [projeção] |
| L2/F2 | Probabilidade de o choque **persistir** 12 meses (o vencedor entrega a política que o mercado espera) | 0,5 (0,3–0,7)¹ | 0,5 (0,3–0,7)² | beta | Goldman: "as políticas, mais que o resultado"; Inhasz e Salto sobre a ordem dos fatores em Flávio; Eurasia: "mercado exagera" [opinião]; valores [hipótese de modelagem] |
| L3/F3 | Se não persistir: o câmbio converge para | consenso C9 ou pior (GS moderado R$ 5,40; pessimista R$ 5,80) | consenso C9 (R$ 5,2–5,3) | — | [hipótese] |
| L4/F4 | Selic fim de 2027 (%) | 12,5 (11–15,5) | 11,0 (9,75–12,5) | tri | MS (9,75 / 11 / 15,5) e JPM (neutro de 10% com reformas); mapeamento por candidato [hipótese, sem fonte direta] |
| L5/F5 | Defasagem do efeito fiscal nos juros | já no preço; sem melhora até um ajuste | efeito só a partir do 2º tri de 2028 (citado) | — | Money Times, autoria não confirmada [opinião] |
| L6/F6 | Ganho real do mínimo, 2027–2030 (% a.a.) | min(PIB de t−2; 2,5) ≈ 1,4–2,5 | P = 0,65: igual a L (declaração de 03/10); P = 0,35: 0% a partir de 2028 (só INPC) | mistura | Lei 14.663/LC 200 [fato]; Flávio e Sachsida [declaração]; Mansueto e Itaú [opinião]; P [hipótese] |
| L7/F7 | Bolsa Família: reajuste real (% a.a.) | 0 a +3 (moda +1) | −2 a +1 (moda 0; "ponte", sem correção) | tri | propostas [proposta]; valores [hipótese] |
| L8/F8 | Isenção de IR até R$ 5 mil mantida | P = 1,0 | P = 0,9 (compensação revogada com P = 0,3) | Bernoulli | Lei 15.270 [fato]; Flávio vago [hipótese] |
| F9 | IVA a 20% aprovado até 2030 | — | P = 0,2 (0,05–0,4) | beta | precisa de LC/PEC e acordo federativo; crítica técnica [opinião]; P [hipótese] |
| F10 | Efeito de preço do IVA a 20% se aprovado (% nos bens tributados, a partir de 2029, gradual até 2033) | — | −1,6 (média efetiva) a −6,25 (referência) × repasse α | tri; α ~ U(0,5; 1,0) | Borges [fato]; [calc]; Benzarti e Portugal [literatura] |
| F11 | Custo fiscal do IVA a 20% (% PIB/ano, sistema pleno) | — | 1,1 a 4,2 | tri | [calc, `lacunas_finais.md`] |
| L12/F12 | Fim da 6x1 promulgado (probabilidade; votação no Senado em out/2026, antes da posse) | P = 0,55 | P = 0,45 | beta | quórum de PEC incerto [hipótese]; Câmara 461–472 votos [fato] |
| C13' | Se a 6x1 passar: efeito no nível de preços de serviços em 2 anos (%) | +1,0 (0 a +3) | igual | tri | Ipea 7,84% custo × parcela do trabalho; Abrasel ~7% no setor [calc/opinião] |
| F14 | PEC 12/2026 (contrato por hora) aprovada | — | P = 0,25 | beta | [hipótese]; DIEESE: renda média de intermitentes = 58% do SM [fato/opinião] |
| L15/F15 | Política de combustíveis em 2027 | suavização com subsídio: realinhamento C15 × 0,5 em 2027 e restante em 2028 | corte de tributos (gasolina −R$ 0,3 a −0,6/l) + fim do imposto de exportação; realinhamento C15 em 2027 | — | MP 1.340, medidas de set/2026 [fato]; plano de Flávio [proposta]; timing [hipótese] |
| L16/F16 | Ajuste primário até 2030 (p.p. do PIB) | +1,7 (0,5–2,5) | +1,5 em 18 meses (0,5–3,0) menos o custo de F11 se o IVA passar | tri | Forbes (fonte petista anônima / assessores de Flávio) [declaração]; necessário: IFI 2,5, Citi 3–3,5, Itaú 4 [opinião] |
| L17/F17 | Probabilidade de vitória (peso dos cenários) | ~0,40–0,55 | ~0,45–0,60 | — | 1º turno Flávio 47,2 x Lula 45,0 [fato]; Kalshi 60/39 (03/10) [mercado]; Eurasia 55% Lula (set) [opinião]; usar o modelo de 2º turno do repo |

¹ L2: probabilidade de Lula surpreender com ajuste crível (o que reverteria a depreciação) = 1 − L2.
² F2: probabilidade de Flávio entregar o ajuste crível antes ou junto dos cortes de impostos.

### 7.3 Elasticidades (comuns)

| # | Elasticidade | Valor | Faixa | Fonte |
|---|---|---|---|---|
| E1 | Repasse câmbio → IPCA, 12m / 24m | 0,10 / 0,16 | 0,03–0,25 (IC 90% amplo) | BCB RPM mar/2026 |
| E2 | Repasse câmbio → alimentação no domicílio, 12m / 24m | 0,26 / 0,33 | 0,10–0,55 | idem |
| E3 | Repasse câmbio → administrados (4 tri) / livres | 0,18 / 0,07 | 0,05–0,35 | idem (modelo semiestrutural) |
| E4 | Repasse câmbio → bens industriais, 12m / 24m | ~0,12 / ~0,22 | 0,0–0,40 | idem (leitura de gráfico) |
| E5 | Assimetria (repasse na apreciação ÷ na depreciação) | 0,75 | 0,5–1,0 | [hipótese]; literatura PUC-Rio/FEE |
| E6 | Selic +1 p.p. (4 tri) → IPCA | −0,27 p.p. (pico em ~5 tri) | −0,15 a −0,40 | BCB RI jun/2024 |
| E7 | Selic +1 p.p. → taxa de crédito pessoal / outros bens / cheque especial (12m) | +1,73 / +1,64 / +4,43 p.p. | ±30% | BCB EE 118/2022 |
| E8 | DBGG +1 p.p. PIB → prêmio de 5 anos | +0,03 p.p. | 0,03–0,33 (recente) | IFI RAF 116 |
| E9 | Salário mínimo real +1% → emprego formal | ≈ 0 | −0,1% a 0 | Engbom e Moser; Ipea TD 849 [literatura] |
| E10 | Custo fiscal por R$ 1 de mínimo | R$ 0,38–0,455 bi/ano | — | DIEESE; SpaceMoney [fato/calc] |
| E11 | Isenção de IR → consumo | 54,5% da renúncia | 40%–80% | CRC-MA (estudo sem autoria clara) |
| E12 | Repasse de corte de IVA ao preço | 0,75 | 0,5–1,0 | Benzarti (parcial); Portugal 2023 (pleno) |
| E13 | Programas sociais → extrema pobreza | −6,5 p.p. (2024) | — | IBGE SIS [fato] |

### 7.4 Esqueleto sugerido do modelo [hipótese de modelagem]

Para cada simulação *s*, vencedor *w* ∈ {L, F} sorteado com L17/F17, e ano *t* = 2027…2030:
1. Câmbio: e(t) = e₀ × (1 + choque L1/F1) com persistência L2/F2; senão, convergência a C9/L3/F3 em 12–18 meses; mais ruído de commodities (C14).
2. Inflação geral: π(t) = C2/C3 + E1 × Δe(t, 12m) + E1' × Δe(t−1, 24m residual) + E6 × (Selic(t−1) − consenso) + combustíveis (C15 × peso C16) + IVA (F9 × F10 × peso, a partir de 2029) + 6x1 (L12 × C13' × peso dos serviços).
3. Alimentos: π_alim(t) = π(t) + C4 + (E2 − E1) × Δe.
4. Índice da família *f* = pesos INPC ou IPCA (C16) aplicados a alimentos, combustíveis e o restante.
5. Renda nominal: mínimo (C17, L6/F6), benefício (L7/F7), salário médio (C11–C12 + π), IR (L8/F8), contrato por hora (F14) para a variância da renda.
6. Serviço da dívida: Selic (L4/F4) × E7 × saldo médio do arquétipo endividado.
7. Saídas: poder de compra real por arquétipo (índice 2026 = 100), **horas de trabalho no SM por cesta** (custo da cesta ÷ SM × 220) e cestas por SM. Reportar mediana, P10–P90 e a diferença L − F, com destaque para quanto da diferença vem de **hipóteses** (L2/F2, L6/F6, F9) e não de fontes.

---

## 8. Lacunas e cuidados

- **Nenhuma projeção publicada de IPCA, PIB, desemprego ou salário real condicional ao candidato** foi encontrada (só câmbio, Selic e bolsa). Tudo além disso no modelo é derivado das elasticidades e das hipóteses acima.
- Itaú, Bradesco, Santander, Tendências, LCA, 4intelligence e XP: **sem cenário condicional por candidato** localizado. O Morgan Stanley tem cenários fiscais não atribuídos a candidatos.
- Tesouro (Relatório de Projeções da Dívida 2026) e o RAF da IFI com trajetória até 2030: não lidos. A IFI de set/2026 só traz 2026–2027 na tabela de curto prazo; a trajetória longa (dívida >100% em 2032) é do RAF de jun/2026.
- Renda real e desemprego de 2003–2011 (PME, seis regiões metropolitanas): não extraídos. A PME não é comparável com a PNADC. Pobreza de 2003–2014: não reverificada.
- Horas de cesta de 2003 e 2010: fonte acadêmica com cidade não identificada (PDF fora do ar). Série nacional comparável: só desde 2012 nesta rodada. Quebra de amostra em ago/2025 (17 → 27 capitais).
- Fração do preço de refinaria na bomba (para C15): não verificada. Tarifas dos EUA ao Brasil em 2026: status não verificado.
- Se a Lei 15.077/2024 fixa piso de 0,6% para o ganho real do mínimo: não reverificado.
- Posição de Flávio sobre a Lei 15.270 (dividendos, imposto mínimo): não encontrada.
- Elasticidade do comprometimento de renda à Selic: sem fonte. Calibrar com o SGS (29034 contra a Selic, com defasagens).
- Identificação das séries do SGS 21084, 20716 e 20740: confirmar no portal do BC.
- O número do FMI sobre a dívida (metodologia FMI) diverge entre matérias (ver `economia_fiscal.md`).
- Agregadores bloqueados (Poder360, Mix Vale, SpaceMoney, O Cafezinho): parte do conteúdo veio de resumos de busca, como indicado.
