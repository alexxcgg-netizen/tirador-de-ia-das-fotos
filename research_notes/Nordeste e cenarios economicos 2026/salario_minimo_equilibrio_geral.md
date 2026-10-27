# Salário mínimo em equilíbrio geral: preços, efeito farol, cascata, emprego, fiscal e cestas por renda (insumos para o modelo de poder de compra)

> Notas de pesquisa (situação em 05/10/2026). Complementa `cenarios_economicos_insumos.md`, mesma pasta, e usa os mesmos códigos de parâmetros (C, L/F, E). Objetivo: dar ao modelo de cenários os **efeitos de segunda ordem** de um ganho real do salário mínimo (SM). Ele não sobe só a renda de quem ganha o piso. Também mexe em preços, em salários acima do piso, no emprego formal, nas contas públicas e no juro. A seção 7 dá a mesma profundidade aos canais das propostas do outro lado: câmbio, juros, corte de tributo sobre consumo, contrato por hora e corte de gasto.
>
> Etiquetas: **[fato]** dado oficial ou documento verificado; **[literatura]** resultado publicado (autor, ano, periódico); **[projeção]**; **[opinião]**; **[calc]** conta feita aqui; **[inferência]** leitura nossa dos dados; **[hipótese de modelagem]** escolha sem fonte direta. "Verificado" quer dizer que o resumo ou o texto do artigo foi lido nesta rodada (via WebFetch, ou PDF baixado e convertido). O que veio só de resumo de busca ou de imprensa secundária está marcado.

---

## 0. Resumo executivo

1. **Repasse a preços: pequeno no agregado, concentrado em serviços intensivos em trabalho.** Um aumento de 10% no SM nominal eleva a inflação de serviços em ~0,6 p.p. após um ano e o IPCA em ~0,3 p.p. (só efeito direto). É o que estima o boxe do BCB no Relatório de Inflação de mar/2013. No Brasil de 1982–2000, Lemos (2006, *Applied Economics*) achou +0,8% no nível de preços em 5 meses, efeito **maior nas regiões pobres** e menor com inflação baixa. A literatura internacional converge para repasse **pleno do custo** em setores de baixo salário (restaurantes, varejo alimentar), com elasticidade preço–SM de 0,04 a 0,11 no setor e ≤0,04 no índice geral [literatura, consenso amplo].
2. **Efeito farol e cascata são fortes no Brasil, mais do que nos EUA.** Engbom e Moser (2022, *AER*) mostram que o SM (alta real de 128% em 1996–2018) explica **45% da queda da desigualdade** de salários formais. O transbordamento vai até o P75–P90, mas é pequeno no meio: +6% no P50 e +2% no P75 para todo o aumento de 128%. Derenoncourt, Gérard, Lagos e Montialoux (2021, *working paper*) mostram que o SM dos anos 2000 **eliminou o hiato racial até o P10** nacional e até o **P30 no Nordeste**, sem migração para a informalidade [literatura, verificado].
3. **Emprego: consenso de efeito agregado pequeno; disputa sobre grupos e regiões de alta "mordida".** As estimativas nacionais giram entre −0,1 e 0 (elasticidade do emprego ao SM). Mas Saltiel e Urzúa (2022, *EDCC*) acham −0,35 no emprego formal em microrregiões menos expostas ao boom de commodities e −0,55 entre pessoas sem ensino médio. Jales (2018, *J. Applied Econometrics*) acha o setor informal **39% maior** do que seria sem o SM (2001–2009). Ponto crucial para 2027–2030: o SM já equivale a **~100% da renda mediana do trabalho em sete estados do Nordeste**, contra 65% no Brasil (IMDS, ago/2026). Isso fica **fora da faixa histórica** em que as estimativas de efeito nulo foram obtidas (Kaitz de 30% a 50% em 1999–2009) [fato/inferência].
4. **Fiscal: cada R$ 1 no SM custa R$ 413,2 milhões por ano** em despesa primária (Consultorias de Orçamento da Câmara e do Senado, PLOA 2027). Só na folha do INSS são R$ 380,5 milhões (DIEESE NT 289). Implicação [calc]: a massa de despesa indexada ao piso é de **~R$ 720 bilhões/ano, cerca de 25% da despesa primária** do PLOA 2027 (R$ 2,826 tri). Pela Lei 15.077/2024, o ganho real fica entre 0,6% e 2,5% em 2025–2030. Como esse é o mesmo intervalo do limite de gasto do arcabouço, a despesa vinculada cresce no teto e **comprime as discricionárias** (IFI: bloqueio de R$ 35,7 bi necessário em 2027).
5. **Cestas por renda (POF 2017–2018, conta própria a partir do SIDRA 6715/6972).** Excluído o aluguel imputado, a família com renda até R$ 1.908 (2 SM de 2018) gasta **22,9% em alimentação no domicílio**, contra 6,8% acima de R$ 23.850. No Nordeste a proporção é de 25,7%. Gás e energia somam 8,6% contra 2,1%; ônibus 2,8% contra 0,7%; remédios 5,5% contra 2,6%. A alimentação fora de casa pesa **igual** (~6–7%) em todas as faixas. Exemplo [calc]: um dólar 10% mais caro gera ~1,14% de inflação para a faixa mais pobre (1,19% no Nordeste) e ~0,84% para a mais rica.
6. **Os canais do outro lado também têm distribuição:** o corte de tributo sobre consumo é repassado de forma **assimétrica** (preços sobem com aumento de imposto cerca de duas vezes mais do que caem com corte: Benzarti et al., 2020, *JPE*). No contrato intermitente, a renda média foi de **58% do SM** em 2023 e **41% dos vínculos não geraram nenhum trabalho** no ano (DIEESE/RAIS). Nas famílias até 3 SM, **38,8% têm contas em atraso**, contra 14,9% acima de 10 SM (CNC Peic, jul/ago 2026).

---

## 1. Repasse do salário mínimo a preços

### 1.1 Evidência internacional (consenso: repasse quase pleno do custo, efeito agregado pequeno)

| Estudo | Contexto | Resultado | Status |
|---|---|---|---|
| **Aaronson (2001)**, "Price Pass-Through and the Minimum Wage", *Review of Economics and Statistics* 83(1):158–169 | Restaurantes, EUA e Canadá | Efeito acumulado de SM +1% sobre preços de restaurantes entre **0,04% e 0,08%**. As resenhas citam **0,56%–1,09% por SM +10%** em mercado competitivo e elasticidade de 0,037 para *fast food*. Efeito concentrado no trimestre do aumento | [literatura; números via resenhas, não lidos no original] |
| **Lemos (2008)**, "A Survey of the Effects of the Minimum Wage on Prices", *Journal of Economic Surveys* 22(1):187–212 | Resenha de ~30 estudos (pré-2005) | SM +10% → alimentos **até +4%**, índice geral **≤ +0,4%** | [literatura; número via citações secundárias consistentes] |
| **MaCurdy (2015)**, "How Effective Is the Minimum Wage at Supporting the Poor?", *Journal of Political Economy* 123(2):497–545 | EUA, modelo insumo-produto | O SM age como um **imposto sobre valor adicionado** nos preços. Esse "imposto" é **mais regressivo que um imposto estadual sobre vendas**, e os ganhos de renda se espalham de forma quase uniforme pela distribuição | [literatura, resumo verificado] |
| **Allegretto e Reich (2018)**, *ILR Review* 71(1):35–63 | San José (CA), SM +25%, 884 cardápios | Preços +1,45%; elasticidade **0,058** (0,044–0,109 conforme o tipo de restaurante); repasse quase pleno do custo | [literatura, resumo verificado] |
| **Harasztosi e Lindner (2019)**, "Who Pays for the Minimum Wage?", *American Economic Review* 109(8):2693–2727 | Hungria, aumento grande e persistente do SM em 2001 | **~75% do custo foi pago por consumidores** e 25% pelos donos das firmas. Elasticidade do emprego negativa mas pequena após 4 anos. Mais desemprego onde o repasse a preço é difícil (setores de bens comerciáveis) | [literatura, resumo verificado] |
| **Renkin, Montialoux e Siegenthaler (2022)**, *Review of Economics and Statistics* | Supermercados, dados de *scanner*, EUA 2001–2012 | SM +10% → preços **+0,36%**, repasse pleno do custo. Preços sobem nos **3 meses após a aprovação** da lei, não da vigência. O aumento atinge igualmente bens consumidos por ricos e pobres | [literatura, resumo verificado] |

**Leitura para o Brasil** [inferência]: o mecanismo é "quem paga o SM" (consumidor ou lucro). Onde a demanda é local e pouco elástica (restaurante, cabeleireiro, serviço doméstico, construção residencial), o custo vai para o preço. Onde há concorrência externa (indústria, agro exportador), o custo sai do lucro ou do emprego.

### 1.2 Evidência brasileira

- **Lemos (2004)**, *The Effect of the Minimum Wage on Prices in Brazil*, IZA DP 1071, publicado como **Lemos (2006)**, "Anticipated Effects of the Minimum Wage on Prices", *Applied Economics* 38(3):325–337. Dados regionais mensais de 1982–2000. **SM +10% → preços +0,8% após 5 meses** e emprego −0,2%. A inflação resultante é "ligeiramente maior para os pobres no longo prazo, menor em períodos de inflação baixa e maior nas regiões mais pobres" [literatura, resumo verificado]. Cuidado: a amostra é dominada pela alta inflação e pela indexação dos anos 1980–1994, então é um **teto** para o período atual.
- **BCB, Relatório de Inflação de mar/2013, boxe "Algumas evidências sobre a relação entre salário e inflação no Brasil"** (PDF lido) [fato]:
  - **VAR** (2002T1–2012T4): o choque de 1% no salário médio real eleva o IPCA em 4 trimestres em **0,4 a 0,8 p.p.**, com pico em 1 ano. O SM entra como exógeno e sinaliza o salário médio (coeficiente de 0,52 na equação de salário, significativo).
  - **Modelo Samba** (DSGE): o pico vai de 0,5 a 1,1 p.p. com Selic endógena e de 0,6 a 1,5 p.p. com Selic constante (choque no salário médio, não no SM).
  - **Modelo desagregado, efeito direto do SM:** SM nominal +10% → **inflação de serviços +0,6 p.p.** no pico, 1 ano depois. O IPCA livre e o cheio sobem **cerca de metade disso (~0,3 p.p.)**. O BCB diz que o exercício "possivelmente subestima" o efeito, por excluir o canal da demanda e o fiscal (benefícios). Pela inércia dos serviços, o efeito é **persistente**.
- **BCB, RI de dez/2013, boxe de segmentação de serviços** (PDF lido) [fato]: os "serviços intensivos em trabalho" (mão de obra, médico, dentista, costureira, manicure, empregado doméstico etc.) eram 23,2% dos serviços do IPCA e têm "boa aderência à evolução do salário mínimo". O reajuste de 14,13% do SM em 2012 segurou essa inflação em alta até o fim de 2012.
- **Correlação anual recente (2012–2025)** [calc, descritivo e não causal, n = 14]: IPCA de dezembro (SIDRA 1419/7060) contra a variação nominal do SM.

| Item do IPCA (peso ago/2026) | Inclinação vs. SM nominal | Inclinação, ambos menos IPCA | Correlação | 12m até ago/2026 (SM: +6,79% em jan/2026) |
|---|---|---|---|---|
| Empregado doméstico (2,75%) | 0,81 | 0,87 | 0,69 | +6,42% |
| Serviços pessoais (6,35%) | 0,63 | 0,68 | 0,73 | +5,99% |
| Alimentação fora do domicílio (6,09%) | 0,50 | 0,40 | 0,64 | +5,40% |
| Mão de obra (reparos) (0,63%) | — | — | — | +8,60% |
| Cabeleireiro e barbeiro (1,12%) | — | — | — | +7,33% |
| Manicure (0,44%) | — | — | — | +7,80% |
| IPCA cheio | — | — | — | +4,22% |

Fonte: [IBGE SIDRA, tabelas 1419 e 7060](https://servicodados.ibge.gov.br/api/v3/agregados/7060), conta própria. As inclinações misturam causalidade com fatores comuns (alimentos e demanda). O valor de alimentação fora do domicílio é dominado pelo custo do alimento. O empregado doméstico ficou bem abaixo do SM em 2020–2024 (pandemia e informalização) e voltou a acompanhar o piso em 2025–2026.

### 1.3 Por setor (síntese para o modelo)

| Setor | Elasticidade preço–SM (central; faixa) | Base |
|---|---|---|
| Serviço doméstico (é praticamente um salário) | 0,8 (0,4–1,0) | correlação acima; o efeito farol se aplica (seção 2) [calc/inferência] |
| Serviços pessoais (cabeleireiro, manicure) | 0,3 (0,1–0,6) | BCB 2013 (aderência); Kosonen (2015) sobre a incidência nesses serviços [inferência] |
| Alimentação fora do domicílio | 0,10 (0,04–0,30) | Aaronson; Allegretto e Reich; o teto reflete a maior participação de trabalhadores no piso no Brasil [literatura/hipótese] |
| Construção e reparos (mão de obra) | 0,3 (0,1–0,6) | item "mão de obra" do IPCA; sem estudo brasileiro específico [hipótese] |
| Varejo alimentar (supermercado) | 0,04 (0,02–0,08) | Renkin et al. (2022) [literatura] |
| Serviços (IPCA) | 0,06 (0,03–0,10) | BCB RI mar/2013 [fato] |
| IPCA cheio | 0,03 (0,01–0,08) | BCB 2013 (0,03, direto); Lemos 2006 (0,08, teto com alta inflação) [fato/literatura] |
| Núcleos | entre serviços e cheio, ~0,04 | [inferência] |

**Timing**: o pico ocorre em ~4 trimestres e o efeito é persistente pela inércia dos serviços (BCB 2013). Nos EUA os preços se antecipam à vigência (Renkin et al.). No Brasil o reajuste é anual, em janeiro, e conhecido em agosto (PLOA). Hipótese de modelagem: 60% do efeito no ano t e 40% em t+1.

**Regra de uso no modelo** [hipótese de modelagem]: aplique as elasticidades **só ao ganho real adicional** entre cenários. A reposição do INPC é endógena à inflação e não deve ser recontada.

---

## 2. Efeito farol (*lighthouse effect*)

- **Souza e Baltar (1979)**, "Salário mínimo e taxa de salários no Brasil", *Pesquisa e Planejamento Econômico* 9(3): cunham o conceito. O SM "guia" a fixação de salários além da cobertura legal [literatura; citação confirmada via OIT].
- **Neri, Gonzaga e Camargo (2001)**, "Salário mínimo, 'efeito-farol' e pobreza", *Revista de Economia Política* 21(2):263–276. Com a PNAD de 1996 (jornada padronizada em 40 h), **~14% dos empregados sem carteira ganhavam exatamente 1 SM**, apesar de 27% de descumprimento. O vínculo é mais fraco entre os conta-própria [literatura; números via resumo da OIT].
- **Fajnzylber (2001)**, CEDEPLAR TD 151 (PME 1982–1997, painel de 541 mil pessoas): "efeitos significativos do SM em toda a distribuição de salários, **tanto no setor formal quanto no informal**". As elasticidades de emprego são de ~−0,1 para formais na base e de **−0,25 a −0,35** para informais e conta-própria de baixo salário [literatura, resumo verificado].
- **Lemos (2009)**, "Minimum Wage Effects in a Developing Country", *Labour Economics* 16(2):224–237: o SM aumenta salários sem efeitos negativos significativos sobre o emprego, com efeito farol, inclusive sobre conta-própria [literatura, via resumo de busca].
- **Boeri, Garibaldi e Ribeiro (2011)**, "The Lighthouse Effect and Beyond", *Review of Income and Wealth* 57(s1):S54–S78. O salário informal sobe após o SM também por **seleção e composição**: **pelo menos 1/3** da alta do salário médio informal vem da triagem entre os setores, não de sinalização, e essa contribuição cresce com o tempo [literatura, resumo verificado]. **Implicação**: só parte da alta informal é ganho de quem já estava lá.
- **Maloney e Núñez Mendez (2004)**, em Heckman e Pagés (orgs.), *Law and Employment* (NBER/U. Chicago Press): densidades de Kernel mostram aglomeração (*bunching*) no SM também no setor informal da América Latina, Brasil incluso [literatura; de memória, não reverificado nesta rodada].
- **Derenoncourt, Gérard, Lagos e Montialoux (2021)**, "Racial Inequality, Minimum Wage Spillovers, and the Informal Sector" (*working paper*, 15/05/2021): o SM é **de facto vinculante no setor informal**, exceto na agricultura, no trabalho doméstico e entre conta-própria. Não há realocação significativa do formal para o informal [literatura, resumo verificado].

**Magnitude para o modelo** [inferência/hipótese]: para empregados sem carteira na faixa de 0,8 a 1,2 SM, elasticidade salário–SM de 0,5 (0,3–0,8). Para conta-própria, 0,2 (0–0,4). Para trabalhadores domésticos informais, 0,5 (0,2–0,8). Os limites inferiores refletem a parte de composição (Boeri et al.) e o descumprimento.

---

## 3. Transbordamento (cascata), compressão e prêmio de escolaridade

### 3.1 Engbom e Moser (2022), *AER* 112(12):3803–3847 (PDF lido)

- **Dados**: RAIS 1996–2018 com PNAD e PME. Alta real do SM de **128%** (58,6 pontos log ajustados por produtividade).
- **Forma reduzida**: entre estados, há efeitos marginais monotônicos e significativos **até o P90**. Em testes de robustez, o transbordamento "alcança o P75 ou acima" (nos EUA, até o P20 em Autor et al., 2016, e até a mediana em Lee, 1999). A semielasticidade do desvio-padrão do log salário ao SM é de **~−0,20**. A queda prevista é de 11,7 pontos log, contra 19,3 observados.
- **Modelo de equilíbrio (busca com firmas heterogêneas)**: o SM reduz a variância do log salário em 12 pontos log, ou **45% da queda observada**. O ganho salarial é de **+6% no P50 e +2% no P75** para todo o aumento de 128%. Isso dá elasticidades de **~0,07 no P50 e ~0,025 no P75** [calc: 6/82 e 2/82, com ln(2,28) = 0,82].
- **Regiões**: a variância caiu "mais da metade" nos três estados mais pobres em 1996 e "menos de um quinto" nos três mais ricos. Nos estados pobres, o P50/P10 caiu 50% e o P50/P25 caiu 40%. A compressão da cauda superior (P90/P50) só ocorreu nos estados pobres.
- **Emprego**: PNAD com efeitos nulos, "precisamente estimados", sobre participação, emprego e participação formal. No modelo, o emprego agregado cai **0,7%** e o produto **sobe 1%** (realocação para firmas mais produtivas). Ressalva: entre os **trabalhadores de menor habilidade, o emprego cai mais de 15%** (nota 48).
- **Por que o transbordamento vai tão alto no Brasil**: o SM é mais vinculante, a força de trabalho tem baixa escolaridade (diplomas de ensino médio ou superior só se concentram do P75 ao P90) e muitos trabalhadores "já passaram" pelo SM (degrau de entrada).

### 3.2 Outros estudos

- **Derenoncourt et al. (2021)**: a razão SM/mediana passou de **30% em 1999 para mais de 50% em 2009**. O hiato racial de salários caiu de 40 para 28 pontos log entre 1999 e 2009 e o SM o **apagou até o P10 nacional e até o P30 no Nordeste**. Não houve substituição branco–não branco nem desemprego significativo [literatura, verificado].
- **Derenoncourt e Montialoux (2021)**, "Minimum Wages and Racial Inequality", *Quarterly Journal of Economics* 136(1): nos EUA, a extensão do SM em 1966/67 explica **mais de 20%** da queda do hiato racial de rendimentos entre 1965 e 1980 [literatura, verificado via resumo]. Serve de referência internacional, não brasileira.
- **Komatsu e Menezes-Filho (2015)**, "Salário mínimo e desigualdade salarial: um estudo com densidades contrafactuais nas regiões metropolitanas brasileiras", *Pesquisa e Planejamento Econômico* 45(3). Com a PME de 2004–2014 e o método DFL, o SM reduziu a dispersão "especialmente entre as mulheres e no estrato mais baixo". Na parte alta, pesaram as condições de oferta e demanda [literatura, verificado].
- **Ferreira, Firpo e Messina (2022)**, "Labor Market Experience and Falling Earnings Inequality in Brazil: 1995–2012", *World Bank Economic Review* 36(1):37–67. O Gini do trabalho caiu de 0,50 para 0,41 e o 90/10 caiu ~40%. O fator principal foi a **queda do retorno à experiência potencial**. Hiatos de gênero, raça, informalidade e rural–urbano também contribuíram. Agiram em sentido contrário a maior dispersão de prêmios setoriais e o "paradoxo do progresso" (retorno convexo à escolaridade) [literatura, verificado via resumo]. **Disputa**: o peso do SM contra a oferta de escolaridade na compressão do prêmio. Engbom e Moser atribuem ao SM 45% da queda; a decomposição de FFM enfatiza retornos e composição. As abordagens não são diretamente comparáveis.
- **Corseuil, Foguel e Hecksher (2015)**, "Efeitos dos pisos salariais estaduais sobre o mercado de trabalho: uma nova abordagem empírica", *Economia Aplicada* 19(1):131–169. Controle sintético para os pisos de PR e SP: em um grupo ocupacional por estado, o piso **elevou a remuneração sem reduzir o emprego nem aumentar a informalidade**. Nos demais grupos não houve efeito [literatura, verificado].

### 3.3 Parâmetros de cascata (salário em múltiplos do SM)

| Faixa (Brasil, 2026) | Posição aproximada | Elasticidade do salário ao SM: central (faixa) | Base |
|---|---|---|---|
| 1,0–1,2 SM (formal) | P10–P30 | 0,9 (0,7–1,0) | piso legal com aglomeração [fato/inferência] |
| ~1,5 SM | ~P50 nacional (mediana ≈ R$ 2.494 = 1.621 ÷ 0,65) | 0,10 (0,05–0,25) | modelo de E&M 0,07; forma reduzida maior [calc/literatura] |
| 2–3 SM | ~P70–P85 | 0,03 (0,0–0,10) | E&M P75 ≈ 0,025 [calc] |
| > 3 SM | > P85 | ~0 | [inferência] |
| **Nordeste**: mediana ≈ 1 SM em 7 estados | P50 ≈ SM | 0,6 a 1,0 até o P50 | IMDS 2026 + DGLM (efeito até o P30 no NE) [inferência] |

Retorno à educação [inferência]: cada ponto de ganho real do SM comprime o prêmio do ensino médio sobre o fundamental, porque os dois grupos estão na faixa de 1–1,5 SM. O prêmio do superior quase não se move, pois esse grupo está acima do P75–P90.

---

## 4. Emprego e informalidade

### 4.1 "Mordida" (índice de Kaitz = SM ÷ mediana)

| Recorte | Kaitz | Fonte |
|---|---|---|
| Brasil, 1999 | ~30% | Derenoncourt et al. (2021), Fig. 1 [literatura] |
| Brasil, 2009 | > 50% | idem |
| **Brasil, 2026** | **65%** (6º entre 34 países; EUA 25%) | IMDS, ago/2026, PNADC, renda do trabalho [fato, via imprensa: Times Brasil, ICL, Folha] |
| **AL, BA, CE, MA, PB, PI, RN** | **~100%** | idem |
| SP / SC / DF | 57% / 52% / 49% | idem |

A mediana implícita do Brasil é de ~R$ 2.494 [calc]. A IMDS (Fernando Veloso) alerta para efeitos sobre informalidade e fiscal. Paulo Tafner diz que a política tem eficácia decrescente contra a pobreza. Segundo a imprensa, a IMDS também calculou que só 9% dos aposentados que recebem o piso estão entre os 30% mais pobres [opinião/fato, via [ICL Notícias](https://iclnoticias.com.br/economia/renda-trabalhador-salario-nordeste/); dado não lido no original]. **Lacuna**: a nota técnica original da IMDS não foi localizada, então não está claro se o Kaitz usa a renda de todos os trabalhos ou só a do principal, nem qual trimestre.

### 4.2 Estudos de emprego no Brasil

| Estudo | Período e dados | Resultado |
|---|---|---|
| **Fajnzylber (2001)**, CEDEPLAR TD 151 | PME 1982–1997 | Elasticidade de ~−0,1 para formais na base; de −0,25 a −0,35 para informais e conta-própria; maior entre jovens [verificado] |
| **Carneiro (2004)**, *Empirica* 31(4):295–306 | Séries de tempo, 1982–2002 | Testa se o SM empurra para a informalidade. Saltiel e Urzúa (2022) resumem Carneiro (2001) como "efeitos modestos de desemprego" [conclusão do artigo de 2004 **não lida**; resumo indisponível] |
| **Neumark, Cunningham e Siga (2006)** | 1996–2001 | Elasticidade de −0,07 (citado em Saltiel e Urzúa) [literatura, secundária] |
| **Jales (2018)**, *J. Applied Econometrics* 33(1):29–51 | PNAD 2001–2009, descontinuidade da densidade | Setor informal **~39% maior** do que sem o SM (desemprego formal e migração formal→informal) [verificado] |
| **Saltiel e Urzúa (2022)**, *Economic Development and Cultural Change* 70(4):1403–1437 | RAIS 2003–2012 (SM real +62%) | Pisos estaduais: nulo (descarta < −0,15). SM nacional: −0,2 nos estados e −0,09 com Kaitz pela mediana, não significativos. Em restaurantes e hotéis, −0,5 (sig.) a −0,39. Sem ensino médio, ≤ −0,18. **Microrregiões menos expostas ao boom de commodities: −0,35 no emprego formal e −0,55 entre sem ensino médio**, contra −0,1 nas mais expostas. Os autores alertam que os efeitos "podem ter crescido" na recessão [PDF lido] |
| **Engbom e Moser (2022)** | 1996–2018 | Forma reduzida nula; modelo −0,7% para +128% real; −15% entre os de menor habilidade [lido] |
| **Derenoncourt et al. (2021)** | 1999–2009 | Sem desemprego significativo nem realocação para o informal [verificado] |
| **Corseuil, Foguel e Hecksher (2015)** | Pisos de PR e SP | Sem efeito em emprego e informalidade [verificado] |

**Consenso**: no Brasil de 1996–2012, com o boom de commodities, um Kaitz de 30%–55% e um mercado formal em expansão, o efeito agregado de emprego foi **pequeno ou nulo**, e a renda subiu na base e no meio da distribuição.
**Disputa**: (i) a migração para o informal (Jales: sim, grande; DGLM e E&M: não); (ii) a heterogeneidade regional e por grupo (Saltiel e Urzúa: efeitos relevantes onde não houve boom; E&M: −15% entre os de menor habilidade no modelo); (iii) a **validade externa** para 2027–2030, com Kaitz de ~100% no Nordeste e sem boom de commodities garantido.

### 4.3 Evidência recente (2023–2026)

- O SM teve ganho real a cada janeiro: +2,49% em 2026 e cerca de 2,5% em 2025 (DIEESE NT 289). O desemprego está em 5,3%, mínimo da série, e a renda real habitual em recorde (`cenarios_economicos_insumos.md`) [fato]. Correlação agregada não é efeito causal.
- Nota do Ipea (Pateo e Lobo, 2025, citada pela imprensa): com desemprego mínimo em 2024 (6,6%), a informalidade chegou a 31,77% ("crescimento sem formalização"), atribuída à capacidade fiscalizatória [opinião técnica, via [Outras Palavras](https://outraspalavras.net/trabalhoeprecariado/o-paradoxo-no-mercado-de-trabalho-brasileiro/); não lida no original].
- O Ipea (Pateo, mar/2026) equipara o aumento do custo da hora no fim da escala 6x1 a uma política de aumento real do SM [via [Brasil de Fato](https://www.brasildefato.com.br/2026/03/09/estudo-do-ipea-equipara-reducao-de-jornada-de-trabalho-a-valorizacao-do-salario-minimo/)]. Relevante porque os **dois choques se somam** em serviços intensivos em trabalho.
- **Lacuna**: não foi encontrado estudo causal publicado sobre o efeito no emprego dos reajustes de 2023–2026.

**Parâmetros de emprego** [hipótese de modelagem ancorada na literatura]: a elasticidade do emprego formal ao SM real é **−0,05** no Brasil (faixa −0,20 a 0) e **−0,15** no Nordeste e outras áreas de Kaitz ~100% (faixa −0,40 a 0, distribuição assimétrica para a esquerda). Para jovens e quem não tem ensino médio, use 2 a 3 vezes esses valores. A migração formal→informal fica entre 0 e 50% dos postos formais perdidos.

---

## 5. Canal fiscal

| Item | Valor | Fonte |
|---|---|---|
| Custo de R$ 1 no SM, despesa primária total | **R$ 413,2 mi/ano** | Consultorias de Orçamento da Câmara e do Senado, PLDO/PLOA 2027 ([CNN Brasil, 26/08/2026](https://www.cnnbrasil.com.br/economia/money/macroeconomia/proposta-do-minimo-de-2027-pode-elevar-despesas-do-governo-em-r-496-bi/)) [fato] |
| Idem, PLOA 2026 | ~R$ 400 mi/ano | Consultoria de Orçamentos do Senado (via resumo de busca) [fato, secundário] |
| Só a folha do INSS | **R$ 380,5 mi/ano** | [DIEESE NT 289, dez/2025](https://www.dieese.org.br/notatecnica/2025/notaTec289salarioMinimo.pdf) [fato] |
| SM 2027 (PLOA): R$ 1.741 (+R$ 120) | +R$ 49,6 bi | idem CNN [fato] |
| Beneficiários do INSS no piso | **70,8%** dos beneficiários e **46,0%** do valor (BEPS set/2025); 69,1% dos benefícios (BEPS mai/2026, via imprensa) | DIEESE NT 289; [meutudo](https://meutudo.com.br/blog/noticias/2026/07/23/por-que-o-valor-do-salario-minimo-pesa-tanto-nos-beneficios-pagos-pelo-inss-entenda/) [fato] |
| Pessoas com renda referenciada no SM | 61,9 mi: INSS 29,3 mi; empregados 17,7 mi; conta-própria 10,8 mi; domésticos 3,9 mi; empregadores 0,4 mi | DIEESE NT 289, Tabela 1 [fato] |
| Renda adicional na economia (reajuste de 2026) | R$ 81,8 bi | idem |
| Despesa de 2027 (PLOA) | Previdência R$ 1,169 tri; BPC R$ 145–153 bi; abono e seguro-desemprego R$ 104,7 bi; Bolsa Família R$ 157,1 bi (sem reajuste) | imprensa sobre o PLOA (NC News, CNN, Vero Notícias) [fato, secundário] |
| Regra | INPC + PIB de t−2 (Lei 14.663/2023), com ganho real entre **0,6% e 2,5%** de 2025 a 2030 (Lei 15.077/2024) | [Rádio Senado, 02/01/2025](https://www12.senado.leg.br/radio/1/noticia/2025/01/02/governo-reajusta-salario-minimo-com-novo-limite-de-ganho-real); texto no Planalto fora do ar nesta rodada [fato] |

**Contas** [calc]:
- **Massa indexada ao piso** ≈ R$ 413,2 mi × 1.741 ≈ **R$ 719 bi/ano**, ou **~25% da despesa primária** do PLOA 2027 (R$ 2,826 tri). É uma aproximação: o custo por real vezes o nível do SM.
- **Cada 1 p.p. a mais de ganho real** em 2027 custa R$ 17,4 × R$ 413,2 mi ≈ **R$ 7,2 bi/ano**, de forma permanente. Com +1 p.p./ano em 2027–2030, o custo chega a ~R$ 29 bi/ano em 2030 e soma **~R$ 73 bi** (em reais de 2027) no período, sem juros. Com PIB nominal de ~R$ 14 tri [hipótese], seriam ~0,5% do PIB em dívida adicional até 2030. Pela regra atual, isso só ocorre se o PIB de t−2 crescer acima do teto, o que não acontece. Portanto o "+1 p.p." equivale a **mudar a lei**. Na direção oposta, "só INPC" (cenário F6 com P = 0,35) **economiza** ~R$ 7–18 bi/ano por ano de congelamento real (ganho de 1 a 2,5 p.p.).
- **Interação com o arcabouço** (LC 200/2023) [inferência]: o limite da despesa total cresce de 0,6% a 2,5% real ao ano. Pela Lei 15.077, o SM tem ganho real no mesmo intervalo. Mas a despesa indexada também cresce com o **número** de beneficiários (crescimento vegetativo do INSS e do BPC). Assim, a fatia vinculada cresce **acima** do limite e espreme as discricionárias. A IFI projeta déficit de R$ 86,1 bi em 2027, contra superávit de R$ 18,6 bi no PLOA, e bloqueio de **R$ 35,7 bi** em discricionárias ([CNN Brasil sobre o RAF](https://www.cnnbrasil.com.br/economia/money/macroeconomia/ifi-do-senado-ve-risco-a-meta-de-2027-e-necessidade-de-contingenciamento/)) [projeção].
- **Retorno via arrecadação**: o DIEESE afirma que "parte relevante" volta pelo consumo, sem número [opinião]. A contribuição ao INSS sobre a folha no piso também sobe. **Lacuna**: não há estimativa oficial do custo líquido de arrecadação.
- **Dívida e juros** [inferência]: o efeito direto é pequeno por ano (0,05% do PIB por p.p.). O canal que importa é o **prêmio de risco**, se o mercado ler o gasto indexado como insustentável. A elasticidade E8 de `cenarios_economicos_insumos.md` (DBGG +1 p.p. do PIB → prêmio de 5 anos +0,03 p.p.; 0,03–0,33 recente) dá a ordem de grandeza.

---

## 6. Cestas de consumo por renda (POF 2017–2018) e dívida das famílias

### 6.1 Participação no consumo, sem aluguel imputado (%) [calc a partir de IBGE, SIDRA 6715 e 6972]

Classes de renda familiar total mensal (valores de 2018; SM de 2018 = R$ 954).

**Brasil**

| Item | ≤ R$ 1.908 (≤2 SM) | 2–3 SM | 3–6 SM | 6–10 SM | 10–15 SM | 15–25 SM | > 25 SM | Total |
|---|---|---|---|---|---|---|---|---|
| Alimentação no domicílio | **22,9** | 19,2 | 16,6 | 12,6 | 11,5 | 9,3 | **6,8** | 14,0 |
| Alimentação fora do domicílio | 6,0 | 6,6 | 7,1 | 7,0 | 6,9 | 6,8 | 6,7 | 6,8 |
| Energia elétrica | 5,7 | 5,1 | 4,4 | 3,4 | 3,0 | 2,3 | 1,7 | 3,7 |
| Gás doméstico | 2,9 | 2,1 | 1,5 | 0,9 | 0,7 | 0,5 | 0,4 | 1,2 |
| Gasolina e álcool (veículo próprio) | 3,3 | 3,9 | 5,4 | 5,9 | 5,9 | 5,2 | 4,3 | 5,1 |
| Transporte urbano | 2,8 | 2,8 | 2,5 | 1,9 | 1,4 | 1,1 | 0,7 | 1,9 |
| Aquisição de veículos | 3,1 | 4,5 | 6,4 | 9,4 | 9,2 | 11,3 | 13,1 | 8,2 |
| Aluguel monetário | 5,6 | 4,6 | 3,2 | 2,7 | 2,3 | 2,3 | 1,1 | 3,0 |
| Remédios | 5,5 | 5,9 | 5,0 | 4,1 | 3,6 | 3,1 | 2,6 | 4,3 |
| Plano de saúde | 0,5 | 1,0 | 1,8 | 3,2 | 4,6 | 5,1 | 5,3 | 3,0 |
| Educação | 2,5 | 3,2 | 4,3 | 5,9 | 6,6 | 7,4 | 9,1 | 5,6 |
| Serviços pessoais | 1,3 | 1,4 | 1,6 | 1,6 | 1,7 | 1,6 | 1,5 | 1,5 |

**Nordeste**

| Item | ≤2 SM | 2–3 | 3–6 | 6–10 | 10–15 | 15–25 | > 25 | Total |
|---|---|---|---|---|---|---|---|---|
| Alimentação no domicílio | **25,7** | 22,7 | 17,4 | 12,7 | 10,4 | 8,5 | 7,8 | 17,1 |
| Alimentação fora do domicílio | 7,4 | 8,4 | 9,4 | 8,6 | 6,5 | 6,8 | 7,5 | 8,2 |
| Energia elétrica | 4,6 | 4,1 | 3,4 | 3,0 | 2,9 | 2,2 | 2,1 | 3,5 |
| Gás doméstico | 3,2 | 2,5 | 1,6 | 1,0 | 0,7 | 0,4 | 0,3 | 1,7 |
| Gasolina e álcool | 3,4 | 3,5 | 4,4 | 5,5 | 6,3 | 4,4 | 5,4 | 4,5 |
| Transporte urbano | 3,0 | 3,1 | 2,7 | 2,0 | 1,3 | 1,1 | 0,4 | 2,3 |
| Remédios | 5,1 | 5,5 | 4,5 | 3,9 | 3,4 | 3,1 | 2,9 | 4,4 |
| Plano de saúde | 0,3 | 0,7 | 1,6 | 4,0 | 4,8 | 5,8 | 6,0 | 2,5 |
| Educação | 3,1 | 3,9 | 5,5 | 6,1 | 7,2 | 8,0 | 7,3 | 5,4 |

**Na despesa total, com aluguel imputado (IBGE, Brasil)** [fato]: até 2 SM, alimentação 22,0% e habitação 39,0% (61,2% juntas, como no [release do IBGE](https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/25598-pof-2017-2018-familias-com-ate-r-1-9-mil-destinam-61-2-de-seus-gastos-a-alimentacao-e-habitacao)); acima de 25 SM, 7,6% e 22,7%. Impostos diretos: 1,3% contra 10,3%. **Empréstimo e carnê: 1,9% contra 1,8%** (2,3%–2,8% nas faixas médias). **Serviços bancários**: 0,5% contra 1,5%.

**Leituras para o modelo** [inferência]:
- O choque de **alimentos e câmbio** pesa 3,4 vezes mais na base (22,9 contra 6,8).
- O choque de **energia, gás e ônibus** (administrados) pesa ~4 vezes mais na base (11,4 contra 2,8).
- O choque de **SM sobre preços**, via alimentação fora de casa e serviços pessoais, é ~neutro por renda (7,3 contra 8,2). Gastos intensivos em SM de quem está no topo (empregado doméstico, peso de 2,75% no IPCA; reparos) **não estão separados** nesta tabela. Pela lógica, concentram-se no topo, o que torna o efeito-preço do SM **menos regressivo no Brasil** do que MaCurdy (2015) acha nos EUA [inferência; não quantificado].
- Gasolina e compra de veículos (canal do câmbio e do IVA sobre bens duráveis) pesam mais no meio e no topo.
- Ressalva: a POF é de 2017–2018. Os pesos de 2026 do INPC e do IPCA já estão em `cenarios_economicos_insumos.md` (C16).

### 6.2 Dívida e serviço da dívida por renda

| Indicador | Base | Topo | Fonte |
|---|---|---|---|
| Famílias endividadas (jul/2026) | ≤3 SM: 84,9% | >10 SM: 72,0% | CNC Peic ([Agência Brasil, 06/08/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-08/cnc-endividamento-das-familias-sobe-para-82-mas-inadimplencia-cai)) [fato] |
| Contas em atraso (jul → ago/2026) | ≤3 SM: 38,5% → 38,8% | >10 SM: 15,1% → 14,9% | idem; agosto via [Sou Brasília](https://soubrasilia.com/peic-cnc-agosto-2026-endividamento-82-inadimplencia-baixa-renda/) [fato, secundário] |
| Sem condições de pagar (ago/2026) | ≤3 SM: 18,3% | 5–10 SM: 7,8% | idem [secundário] |
| Comprometimento médio da renda (Peic) | 29,5% (total); 19,2% das famílias comprometem mais de 50% | — | idem |
| Cartão de crédito como dívida principal | > 85% dos endividados | — | idem |
| Comprometimento de renda dos tomadores (BCB, 2017) | ≤1 SM: **25,2%**, maior inadimplência | 1–2 SM: 17,5% | [BCB, Relatório de Cidadania Financeira, cap. 2](https://www.bcb.gov.br/nor/relcidfin/cap02.html) [fato, dado antigo] |
| Modalidades (BCB, 2017) | ≤1 SM: **rotativo do cartão é a 2ª modalidade** mais comum; cheque especial é a 6ª | demais faixas: rotativo e cheque especial entre as 4 primeiras | idem |
| CRI agregado (BCB, SGS 29034) | 28,7% (recorde) | — | `cenarios_economicos_insumos.md` |
| Tendência (REF mai/2026) | o comprometimento individual cresceu no 2º semestre de 2025, "com maior impacto nos tomadores de menor renda" | — | [BCB REF mai/2026](https://www.bcb.gov.br/content/publicacoes/ref/202605/RELESTAB202605-refPub.pdf) [fato] |

**Lacuna**: não há série pública e recente do BCB com o comprometimento por faixa de SM; o último dado localizado é de 2017. Para o modelo, use a Peic na incidência e o CRI do BCB no nível.

---

## 7. Mesma profundidade para os canais das outras políticas

### 7.1 Câmbio (apreciação ou depreciação) por renda

- Repasse (BCB RPM mar/2026): 0,10 para o IPCA e **0,26 para alimentação no domicílio** em 12 meses (E1 e E2 em `cenarios_economicos_insumos.md`).
- **Inflação por faixa com dólar +10%** [calc]: alimentação no domicílio +2,6%; resto da cesta ≈ +0,71% (o que fecha o IPCA em +1,0% com peso de 15,4%).
  - Até 2 SM (Brasil): 0,229 × 2,6 + 0,771 × 0,71 ≈ **+1,14%**
  - Até 2 SM (Nordeste): ≈ **+1,19%**
  - Média: ≈ +0,97%
  - Acima de 25 SM: ≈ **+0,84%**
  - Pelo mesmo cálculo, uma apreciação de 10% beneficia mais a base (com o desconto de assimetria E5).
- **Lado da renda (o que a apreciação tira)** [literatura/inferência]: Saltiel e Urzúa (2022) mostram que regiões mais expostas ao boom de commodities **absorveram melhor** o SM, com efeito de −0,1 no emprego formal contra −0,35 nas menos expostas. Câmbio forte e commodities fracas no agro do interior tendem a reduzir essa proteção. Dix-Carneiro e Kovak (2017, *AER* 107(10):2908–46) mostram que choques de comércio em mercados locais brasileiros têm efeitos sobre emprego formal e salários **que se ampliam por 20 anos** (o efeito em 20 anos é três vezes o de 10 anos), com baixa mobilidade entre regiões [literatura, verificado via resumo]. Choques ao setor de bens comerciáveis no interior não se dissipam rápido.
- Parâmetro sugerido [hipótese]: emprego formal em microrregiões agro e de indústria comerciável, elasticidade ao câmbio real de 0,05 a 0,15 (apreciação de 10% → −0,5% a −1,5% do emprego local em 2 anos). Não há estimativa brasileira direta verificada nesta rodada.

### 7.2 Juros por renda

- O repasse da Selic às taxas é de +4,43 p.p. no cheque especial e +1,73 p.p. no crédito pessoal por 1 p.p. de Selic (E7, BCB EE 118/2022). O rotativo do cartão estava em **440,5% a.a.** em nov/2025 (Agência Brasil, dez/2025, via resumo de busca) [fato, secundário].
- **Incidência** [inferência a partir de 6.2]: a base tem maior proporção de endividados e de atrasos e usa o rotativo como 2ª modalidade. O topo tem dívida mais barata (imobiliário, consignado, veículos) e **ativos que rendem a Selic**. Selic menor ajuda a base pelo custo da dívida e reduz a renda financeira do topo.
- Parâmetro sugerido [hipótese]: Selic −1 p.p. → serviço da dívida −0,3 a −0,6% da renda na faixa até 3 SM endividada (comprometimento ~30% × peso de 20% a 40% de modalidades pós-fixadas ou rotativas × variação da taxa). A calibração fica para o SGS (lacuna já registrada).

### 7.3 Corte de tributo sobre consumo (IBS/CBS, ICMS, IPI, PIS/Cofins)

| Evidência | Resultado | Status |
|---|---|---|
| **Benzarti, Carloni, Harju e Kosonen (2020)**, "What Goes Up May Not Come Down", *JPE* 128(12):4438–4474 | Os preços respondem **cerca de duas vezes mais a aumentos** de IVA do que a cortes. A assimetria persiste por anos; maior em firmas de margem baixa; vale para todas as mudanças de IVA na UE em 1996–2015 | [literatura, verificado] |
| **Kosonen (2015)**, *J. Public Economics* 131:87–100 | Corte de IVA em cabeleireiros (Finlândia): repasse de **~43%–52%** | [literatura, via resumo de busca] |
| **Desoneração da cesta básica de 2013** (PIS/Cofins, Lei 12.839/2013) | Avaliação do CMAP citada na imprensa: repasse de **5,4%** (queda efetiva de 0,5%) e gasto tributário apropriado sobretudo pelo topo | [**não verificado** no documento primário: o PDF do CMAP não baixou] |
| **Banco Mundial (out/2023)**, isenção da cesta na reforma tributária | Isenção ampla da cesta beneficia mais quem tem renda alta. Alíquota padrão com devolução (*cashback*) para os 10% mais pobres zera a carga deles | [literatura, resumo verificado] |
| **Combustíveis, energia e telecom, 2022** (LC 194/2022 e desoneração federal) | A alíquota da gasolina caiu de ~27% para 18% (DIEESE NT 270). IBGE: sem as quedas da gasolina e da energia, o IPCA de 2022 teria sido **9,56% e não 5,79%**. A conta inclui também cortes de preço da Petrobras; não é só repasse de tributo. O BCB (RI jun/2022) avaliou que as medidas "reduzem sensivelmente a inflação no ano corrente, embora elevem, em menor magnitude, a inflação no horizonte relevante" | [fato; o IBGE via CNN Brasil] |
| **IPI de automóveis, 2009 e 2012** | Estudos (ANPEC 2017; UFSC 2014) medem vendas e excedente, sem coeficiente de repasse claro | [lacuna] |

**Parâmetro sugerido**: repasse de corte de tributo ao preço de **0,5** (0,05–1,0). Combustíveis com preço monitorado ficam perto de 1, porque o corte vai direto para a bomba. Alimentos e serviços com cadeias longas ficam em 0,05–0,5. Uma alta futura de tributo é repassada com ~1,0 (assimetria). **Incidência por renda**: o efeito de preço de um IVA menor é proporcional à cesta tributada. A cesta básica já tem alíquota reduzida ou zero na EC 132/LC 214, então o ganho relativo vai para quem consome bens e serviços de alíquota cheia (meio e topo) [inferência].

### 7.4 Contrato por hora (intermitente) desde a Reforma de 2017

| Indicador | Valor | Fonte |
|---|---|---|
| Vínculos intermitentes no setor privado, fim de 2023 | 417 mil (0,94% do estoque formal) | DIEESE, Boletim Emprego em Pauta 28 (2024), RAIS 2023 [fato, via imprensa e resumo] |
| Remuneração mensal média | **R$ 762 = 58% do SM**; mulheres e jovens R$ 661 (~50%) | idem |
| Vínculos sem nenhum trabalho no ano | **41%** | idem |
| Vínculos com renda mensal abaixo de 1 SM ou nula | **76%** | idem |
| Duração média (vínculos encerrados) | 4,5 meses; houve pagamento em **44% dos meses** contratados | idem |
| Ipea TD 2898 (jul/2023) | Remuneração média em 2021: R$ 1.485 para intermitentes contra R$ 2.925 para os demais (medida diferente, provavelmente nos meses com renda). Perfil: mais jovens, sem superior, não brancos. A expansão reduziria a massa salarial e aumentaria a desigualdade | [Ipea](https://repositorio.ipea.gov.br/bitstream/11058/12192/1/TD_2898_Web.pdf) [fato/projeção] |

**Leitura para o modelo** [inferência]: o contrato por hora muda pouco a renda **média** agregada (é <1% do emprego formal), mas aumenta muito a **variância** da renda individual. Mal desenhado, empurra a renda para baixo do piso mensal: em 2023, 76% dos vínculos não alcançaram 1 SM. Parâmetro do arquétipo "intermitente": renda média de 0,58 SM (0,45–0,75) e coeficiente de variação mensal alto (meses sem trabalho ~56%).

### 7.5 Corte de gasto: o que é cortável e quem é afetado

- PLOA 2027: despesa primária de R$ 2,826 tri, **~90% obrigatória**; sobram R$ 283,2 bi discricionários, dos quais R$ 61,2 bi são emendas e outros Poderes. Emendas impositivas: R$ 44,8 bi (até R$ 57,7 bi com as de comissão) [fato, via imprensa sobre o levantamento do PLOA; SpaceMoney bloqueado].
- Previdência (R$ 1,169 tri), BPC (R$ 145–153 bi), abono e seguro-desemprego (R$ 104,7 bi) e Bolsa Família (R$ 157,1 bi) **são o grosso** [fato, secundário].
- **Incidência** [inferência]:
  - Corte de discricionária atinge investimento, custeio de saúde e educação acima dos pisos constitucionais e programas como Farmácia Popular e Pé-de-Meia. Quem depende do SUS e da escola pública são as faixas baixas: na POF, plano de saúde é 0,5% do consumo até 2 SM, contra 5,3% no topo, e educação é 2,5% contra 9,1%.
  - Mudar a regra do SM ou a vinculação do piso previdenciário atinge **29,3 milhões** de beneficiários e 61,9 milhões com renda referenciada. Segundo a IMDS, só uma parte pequena dos aposentados no piso está entre os 30% mais pobres, o que é o argumento de focalização [opinião].
  - Mudanças no abono salarial (quem ganha até ~2 SM) e no seguro-desemprego atingem o formal de baixa renda.
- Parâmetro sugerido [hipótese]: um ajuste de 1 p.p. do PIB feito só em discricionárias equivale a cortar ~R$ 140 bi, cerca de metade das discricionárias, o que é inviável. Um ajuste crível exige mexer em regras de despesa obrigatória: SM, vinculações, abono, BPC e pisos.

---

## 8. Como juntar no modelo: equilíbrio geral do SM por arquétipo [hipótese de modelagem]

Para um ganho real adicional g (p.p.) no SM em relação ao cenário base:

1. **Renda nominal**:
   - Piso formal e INSS/BPC: +g.
   - Empregado informal perto do piso: +0,5g (efeito farol).
   - Conta-própria: +0,2g.
   - Trabalhador mediano: +0,10g no Brasil e +0,6 a 1,0g no Nordeste.
   - 2–3 SM: +0,03g.
   - Acima de 3 SM: 0.
2. **Emprego**: probabilidade de perder o emprego formal = |ε| × g, com ε = −0,05 no Brasil e −0,15 no Nordeste (jovens e sem ensino médio ×2–3). Quem perde vai para o informal com renda de ~0,7 do salário anterior (fração de 0 a 50%) [hipótese].
3. **Preços** (com peso de cada família):
   - Serviços pessoais: +0,3g.
   - Doméstico: +0,8g.
   - Alimentação fora do domicílio: +0,10g.
   - Mão de obra: +0,3g.
   - Supermercado: +0,04g.
   - Isso dá ≈ +0,03g a +0,08g no IPCA (checagem de consistência). 60% no ano e 40% em t+1.
4. **Fiscal**: custo de g × SM × R$ 413,2 mi por ano, acumulado. O prêmio de risco entra via E8, e com ele a Selic e o câmbio.
5. **Resultado líquido típico** (g = 1 p.p.) [calc]:
   - Quem ganha o piso ou o benefício no piso: ≈ +0,95% de poder de compra.
   - Mediano no Sudeste: ≈ +0,05%.
   - Mediano no Nordeste: ≈ +0,6% a +0,9%.
   - Quem está acima de 3 SM: ≈ −0,03% a −0,08%, antes do canal fiscal e dos juros.
   - No Nordeste, a cauda de risco é a perda de emprego formal (de 0,15% a 0,4% dos empregos por p.p.).

---

## 9. Tabela final de parâmetros

| # | Parâmetro | Central | Faixa | Fonte |
|---|---|---|---|---|
| M1 | Elasticidade do IPCA ao SM nominal (efeito direto, pico em ~4 tri) | 0,03 | 0,01–0,08 | BCB RI mar/2013 (0,03); Lemos 2006 (0,08, alta inflação); Lemos 2008 (≤0,04) |
| M2 | Elasticidade do IPCA serviços ao SM | 0,06 | 0,03–0,10 | BCB RI mar/2013 |
| M3 | Elasticidade do preço de empregado doméstico ao SM | 0,8 | 0,4–1,0 | IPCA × SM 2012–2025 [calc, descritivo] |
| M4 | Elasticidade de serviços pessoais e mão de obra ao SM | 0,3 | 0,1–0,6 | BCB RI dez/2013; correlação [calc]; [hipótese] |
| M5 | Elasticidade da alimentação fora do domicílio ao SM | 0,10 | 0,04–0,30 | Aaronson 2001; Allegretto e Reich 2018 (0,044–0,109); [hipótese] para o teto no Brasil |
| M6 | Elasticidade do varejo alimentar ao SM | 0,04 | 0,02–0,08 | Renkin, Montialoux e Siegenthaler 2022 |
| M7 | Fração do custo do SM paga por consumidores | 0,75 | 0,5–1,0 | Harasztosi e Lindner 2019 |
| M8 | Defasagem do repasse a preços (fração no ano t) | 0,6 | 0,4–0,9 | BCB 2013 (pico em 1 ano); Renkin et al. (antecipação) [hipótese] |
| M9 | Efeito-preço do SM maior em regiões pobres (multiplicador para o NE) | 1,3 | 1,0–1,6 | Lemos 2006 (direção); magnitude [hipótese] |
| M10 | Efeito farol: elasticidade salarial de empregados sem carteira perto do piso | 0,5 | 0,3–0,8 | Neri, Gonzaga e Camargo 2001; Fajnzylber 2001; Boeri et al. 2011 (≥1/3 é composição); DGLM 2021 |
| M11 | Efeito farol: conta-própria | 0,2 | 0–0,4 | Fajnzylber 2001; Neri et al. 2001 (vínculo fraco); Lemos 2009 |
| M12 | Transbordamento no P50 nacional (~1,5 SM) | 0,10 | 0,05–0,25 | Engbom e Moser 2022 (modelo 0,07; forma reduzida maior) [calc] |
| M13 | Transbordamento a 2–3 SM (~P75–P85) | 0,03 | 0–0,10 | Engbom e Moser 2022 (P75 ≈ 0,025) [calc] |
| M14 | Transbordamento no P50 do Nordeste (mediana ≈ SM) | 0,8 | 0,6–1,0 | IMDS 2026; DGLM 2021 (até o P30 no NE) [inferência] |
| M15 | Parcela da queda da desigualdade salarial atribuída ao SM (1996–2018) | 45% | 33%–60% | Engbom e Moser 2022 (45%; NBER: "um terço" da queda de 25,9 pontos log) |
| M16 | Elasticidade do emprego formal ao SM, Brasil | −0,05 | −0,20 a 0 | Saltiel e Urzúa 2022; Engbom e Moser 2022; NCS 2006 (−0,07); Fajnzylber 2001 (−0,1) |
| M17 | Elasticidade do emprego formal ao SM, Nordeste e Kaitz ~100% | −0,15 | −0,40 a 0 | Saltiel e Urzúa 2022 (−0,35 sem boom); validade externa incerta [hipótese] |
| M18 | Multiplicador para jovens e sem ensino médio | 2,5 | 1,5–4 | Saltiel e Urzúa (−0,55 contra −0,35); Fajnzylber; E&M (−15% no modelo) |
| M19 | Fração dos empregos formais perdidos que vai para o informal | 0,3 | 0–0,5 | Jales 2018 (alta) contra DGLM 2021 e E&M (≈0) [disputado] |
| M20 | Kaitz (SM/mediana): Brasil / NE (7 UFs) / SP / SC / DF | 65% / ~100% / 57% / 52% / 49% | — | IMDS ago/2026 (via imprensa) |
| M21 | Custo fiscal por R$ 1 de SM (despesa primária) | R$ 413,2 mi/ano | R$ 380,5–420 mi | Consultorias de Orçamento (PLOA 2027); DIEESE NT 289 (só o INSS) |
| M22 | Massa de despesa indexada ao piso | R$ 719 bi (~25% da primária) | R$ 670–730 bi | [calc] M21 × SM |
| M23 | Custo de +1 p.p. de ganho real (2027) | R$ 7,2 bi/ano, permanente | R$ 6,6–7,3 bi | [calc] |
| M24 | Beneficiários do INSS no piso: fração de pessoas / do valor | 70,8% / 46,0% | 69%–71% / — | BEPS set/2025 (DIEESE); BEPS mai/2026 (69,1%) |
| M25 | Ganho real do SM permitido por lei, 2025–2030 | INPC + PIB t−2 | 0,6%–2,5% | Lei 14.663/2023; Lei 15.077/2024 |
| M26 | Peso da alimentação no domicílio na cesta (sem aluguel imputado): ≤2 SM / total / >25 SM (BR) | 22,9 / 14,0 / 6,8% | NE: 25,7 / 17,1 / 7,8% | POF 2017–18, SIDRA 6715/6972 [calc] |
| M27 | Peso de energia, gás e ônibus: ≤2 SM / >25 SM (BR) | 11,4 / 2,8% | NE: 10,8 / 2,8% | idem [calc] |
| M28 | Peso de alimentação fora do domicílio e serviços pessoais: ≤2 SM / >25 SM | 7,3 / 8,2% | NE: 8,6 / 8,9% | idem [calc] |
| M29 | Inflação por faixa com dólar +10% (12m): ≤2 SM / média / >25 SM | 1,14 / 0,97 / 0,84% | NE ≤2 SM: 1,19% | E1, E2 × M26 [calc] |
| M30 | Inadimplência (contas em atraso): ≤3 SM / >10 SM | 38,8% / 14,9% | jul–ago/2026 | CNC Peic |
| M31 | Comprometimento de renda dos tomadores ≤1 SM | 25,2% | dado de 2017 | BCB, Relatório de Cidadania Financeira |
| M32 | Repasse de corte de tributo sobre consumo ao preço | 0,5 | 0,05–1,0 (combustíveis ~1; cesta ~0,05–0,5) | Benzarti et al. 2020; Kosonen 2015; cesta de 2013 (5,4%, não verificado) |
| M33 | Repasse de alta de tributo (assimetria) | 1,0 | 0,8–1,0 | Benzarti et al. 2020 (~2× o do corte) |
| M34 | Contrato intermitente: renda média / fração de vínculos sem trabalho no ano | 0,58 SM / 41% | 0,45–0,75 SM | DIEESE (RAIS 2023) |
| M35 | Emprego formal em microrregiões agro e comerciáveis: elasticidade ao câmbio real | 0,10 | 0,05–0,15 | [hipótese]; direção de Saltiel e Urzúa 2022 e Dix-Carneiro e Kovak 2017 |
| M36 | Selic −1 p.p. → serviço da dívida da faixa ≤3 SM endividada (% da renda) | −0,4 | −0,3 a −0,6 | E7 + Peic [hipótese] |

---

## 10. Consenso contra disputa (síntese)

**Consenso (literatura ampla e convergente):**
- O SM é repassado a preços em setores de baixo salário com demanda local, com efeito pequeno no índice geral.
- No Brasil, o SM comprimiu fortemente a base da distribuição e reduziu hiatos raciais, regionais e de gênero.
- Nos anos 2000, o efeito agregado sobre emprego foi pequeno ou nulo.
- O custo fiscal por real é de ~R$ 0,4 bi/ano e a vinculação domina a dinâmica da despesa.

**Disputado:**
- Até onde vai o transbordamento: P75–P90 (Engbom e Moser) ou só a cauda baixa (estudos dos EUA). No Brasil, a disputa recai sobre o tamanho no meio da distribuição.
- A migração para a informalidade (Jales: +39% contra DGLM: nada).
- A validade externa com Kaitz de ~100% no Nordeste e sem boom de commodities.
- A focalização: o SM como instrumento contra a pobreza (IMDS e Tafner) ou como política de renda ampla (DIEESE).
- A magnitude do repasse de cortes de tributo no Brasil (cesta de 2013 contra combustíveis em 2022).

## 11. Lacunas

- **Nota técnica original da IMDS** (Kaitz por UF): não localizada; os números vêm de reportagens convergentes (Times Brasil, ICL, Folha, Jornal de Brasília).
- **Carneiro (2004)**: conclusão não lida (sem resumo disponível).
- **Lemos (2008)**: os números (+4% em alimentos, ≤0,4% no geral) vêm de citações secundárias consistentes, sem leitura do original.
- **CMAP, cesta básica**: o número de repasse de 5,4% não foi verificado no PDF (o *link* retornou HTML).
- **Planalto fora do ar** (03–05/10): o texto da Lei 15.077 não foi lido; o intervalo de 0,6%–2,5% vem da Rádio Senado.
- **Comprometimento de renda por faixa de SM**: o BCB só tem o dado de 2017; não há série recente pública.
- **Efeito causal dos reajustes de 2023–2026 sobre o emprego**: não há estudo.
- **Gasto das famílias com empregado doméstico na POF por faixa**: não extraído (é necessário para quantificar a progressividade do efeito-preço do SM).
- **Câmbio → emprego regional (agro e comerciáveis)**: não há elasticidade brasileira direta verificada; M35 é hipótese.

## Fontes principais (links)

- Engbom e Moser (2022), *AER*: [AEA](https://www.aeaweb.org/articles?id=10.1257%2Faer.20181506); [NBER w28831](https://www.nber.org/papers/w28831)
- Derenoncourt, Gérard, Lagos e Montialoux (2021): [PDF](http://www.clairemontialoux.com/files/DGLM2021.pdf); Derenoncourt e Montialoux (2021), *QJE*: [PDF](https://www.clairemontialoux.com/files/DM_QJE_2021.pdf)
- Saltiel e Urzúa (2022), *EDCC*: [DOI](https://dx.doi.org/10.1086/714114); [PDF](http://econweb.umd.edu/~urzua/PaperSU_2020.pdf)
- Jales (2018), *JAE*: [RePEc](https://ideas.repec.org/a/wly/japmet/v33y2018i1p29-51.html)
- Harasztosi e Lindner (2019), *AER*: [AEA](https://pubs.aeaweb.org/doi/10.1257/aer.20171445)
- Aaronson (2001), *REStat*: [ResearchGate](https://www.researchgate.net/publication/24095681_Price_Pass-Through_and_the_Minimum_Wage)
- MaCurdy (2015), *JPE*: [UChicago](https://www.journals.uchicago.edu/doi/abs/10.1086/679626)
- Lemos (2006/2004): [IZA DP 1071](https://www.iza.org/publications/dp/1071/the-effect-of-the-minimum-wage-on-prices-in-brazil); Lemos (2008): [EconPapers](https://econpapers.repec.org/article/blajecsur/v_3a22_3ay_3a2008_3ai_3a1_3ap_3a187-212.htm)
- Allegretto e Reich (2018): [IRLE](https://irle.berkeley.edu/are-local-minimum-wages-absorbed-by-price-increases); Renkin, Montialoux e Siegenthaler: [Berkeley GSPP](https://gspp.berkeley.edu/research-and-impact/publications/the-pass-through-of-minimum-wages-into-us-retail-prices-evidence-from-supermarket-scanner-data)
- BCB, RI mar/2013, boxe: [PDF](https://www.bcb.gov.br/content/ri/relatorioinflacao/201303/RELINF201303-ri201303b8p.pdf); RI dez/2013: [PDF](https://www.bcb.gov.br/htms/relinf/port/2013/12/ri201312p.pdf); RI jun/2022: [PDF](https://www.bcb.gov.br/content/ri/relatorioinflacao/202206/ri202206c2p.pdf)
- Neri, Gonzaga e Camargo (2001), *REP*: [OIT, resumo](https://www.ilo.org/resource/minimum-wage-%E2%80%9Clighthouse-effect%E2%80%9D-brazil)
- Boeri, Garibaldi e Ribeiro (2011), *RIW*: [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1475-4991.2011.00455.x)
- Fajnzylber (2001): [RePEc](https://ideas.repec.org/p/cdp/texdis/td151.html); Carneiro (2004): [RePEc](https://ideas.repec.org/a/kap/empiri/v31y2004i4p295-306.html); Lemos (2009): [ResearchGate](https://www.researchgate.net/publication/222406280_Minimum_Wage_Effects_in_a_Developing_Country)
- Komatsu e Menezes-Filho (2015), *PPE*: [Ipea](https://ipea.gov.br/portal/publicacao-item?id=a0d397b9-7354-4ce6-ab61-60d97549d935); Corseuil, Foguel e Hecksher (2015): [USP](https://revistas.usp.br/ecoa/article/view/106029); Ferreira, Firpo e Messina (2022): [RePEc](https://ideas.repec.org/a/oup/wbecrv/v36y2022i1p37-67..html)
- Dix-Carneiro e Kovak (2017), *AER*: [AEA](https://www.aeaweb.org/articles?id=10.1257%2Faer.20161214)
- Benzarti et al. (2020), *JPE*: [NBER](https://www.nber.org/papers/w23849); Kosonen (2015): [RePEc](https://ideas.repec.org/a/eee/pubeco/v131y2015icp87-100.html)
- IMDS (ago/2026), via [Times Brasil](https://timesbrasil.com.br/brasil/salario-minimo-ganha-peso-e-chega-perto-da-renda-mediana-em-sete-estados-nordestinos/) e [ICL Notícias](https://iclnoticias.com.br/economia/renda-trabalhador-salario-nordeste/)
- DIEESE: [NT 289](https://www.dieese.org.br/notatecnica/2025/notaTec289salarioMinimo.pdf); [Emprego em Pauta 28 (intermitente)](https://www.dieese.org.br/boletimempregoempauta/2024/boletimEmpregoPauta28.pdf); [NT 270 (ICMS)](https://www.dieese.org.br/notatecnica/2022/notaTec270ICMS.pdf)
- IBGE POF 2017–2018: [SIDRA/API, tabelas 6715 e 6972](https://servicodados.ibge.gov.br/api/v3/agregados/6715); IPCA: tabelas 1419 e 7060
- CNC Peic: [Agência Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2026-08/cnc-endividamento-das-familias-sobe-para-82-mas-inadimplencia-cai); BCB [REF mai/2026](https://www.bcb.gov.br/content/publicacoes/ref/202605/RELESTAB202605-refPub.pdf); [Cidadania Financeira](https://www.bcb.gov.br/nor/relcidfin/cap02.html)
- Banco Mundial (2023), cesta básica: [link](https://www.worldbank.org/pt/country/brazil/publication/brasil-impactos-distributivos-reforma-tributaria-isencao-cesta-basica)
- Ipea TD 2898 (intermitente): [PDF](https://repositorio.ipea.gov.br/bitstream/11058/12192/1/TD_2898_Web.pdf)
