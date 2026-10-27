# Complemento ao briefing 2026: covariáveis demográficas por UF e reta final da campanha (25/09–03/10/2026)

*Notas coletadas em 03/10/2026, véspera do 1º turno (04/10/2026). Os dados de IBGE e MDS foram baixados direto das APIs e agregados por conta própria. Os demais itens vêm da imprensa e estão datados. Rótulos usados: **[FATO]** para fato verificável, **[ALEGAÇÃO]** para acusação ou investigação ainda não julgada e **[OPINIÃO]** para avaliação ou posição de ator político.*

## (A) Quais são as covariáveis demográficas de cada uma das 27 UFs (Bolsa Família, religião, raça, renda, urbanização, Gini, IDH)?

### Takeaway
A tabela completa das 27 UFs está montada e salva em `demografia_uf.csv`, com 23 colunas. O Bolsa Família de setembro/2026 chega a 19,3 milhões de famílias, o que dá 12,2 famílias para cada 100 eleitores no Brasil. Essa razão varia de 3,7 em SC a 22,6 no MA. O peso evangélico também varia muito: de 15,6% no PI a 44,4% no AC. O Norte é a região mais evangélica, e o Nordeste combina a maior cobertura do PBF com a maior proporção de católicos.

### Tabela por UF (ordenada pelo tamanho do eleitorado)
Definições das colunas:
- **Eleit. 2026**: eleitorado apto segundo o TSE em jul/2026, já usado no briefing anterior (`segmentacao_eleitorado.md`).
- **Fam. PBF set/26**: famílias beneficiárias do Bolsa Família em setembro/2026. É a soma dos municípios de cada UF na API MiSocial do MDS.
- **PBF/100 eleit.**: famílias do PBF para cada 100 eleitores. É uma razão de intensidade e não indica a fração de eleitores beneficiários, porque cada família tem em média cerca de 2,5 pessoas e várias delas votam.
- **PBF % domic.**: famílias do PBF divididas pelos domicílios particulares permanentes ocupados do Censo 2022. É uma aproximação, já que família do CadÚnico e domicílio não são a mesma coisa e o número de domicílios cresceu desde 2022.
- **Religião**: pessoas com 10 anos ou mais (Censo 2022).
- **Raça**: população residente (Censo 2022).
- **Renda pc**: rendimento médio mensal real domiciliar per capita da PNAD Contínua anual 2025, a preços médios do ano.
- **Gini**: rendimento domiciliar per capita da PNAD Contínua 2025.
- **IDHM 2024**: Radar IDHM do PNUD/Ipea/FJP.

O CSV traz também a renda e o Gini de 2024, o Gini do Censo 2022 e as proporções de indígenas e amarelos.

| UF | Eleit. 2026 | Fam. PBF set/26 | PBF/100 eleit. | PBF % domic. | % Evang. | % Catól. | % Sem rel. | % Branca | % Parda | % Preta | % Urbana | Renda pc 2025 (R$) | Gini 2025 | IDHM 2024 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SP | 34.104.226 | 2.321.827 | 6.8 | 14.3 | 27.33 | 52.24 | 10.46 | 57.78 | 32.96 | 7.99 | 96.82 | 2862 | 0.491 | 0.838 |
| MG | 16.377.659 | 1.459.921 | 8.9 | 19.4 | 24.78 | 63.48 | 5.72 | 41.08 | 46.76 | 11.84 | 88.23 | 2289 | 0.473 | 0.809 |
| RJ | 12.857.000 | 1.419.748 | 11.0 | 23.1 | 32.00 | 38.92 | 16.89 | 41.98 | 41.62 | 16.16 | 97.90 | 2732 | 0.543 | 0.819 |
| BA | 11.321.005 | 2.388.140 | 21.1 | 46.9 | 23.35 | 56.98 | 12.91 | 19.61 | 57.31 | 22.38 | 76.72 | 1452 | 0.466 | 0.759 |
| PR | 8.609.026 | 567.235 | 6.6 | 13.5 | 26.06 | 62.85 | 6.03 | 64.57 | 30.06 | 4.24 | 88.95 | 2687 | 0.470 | 0.822 |
| RS | 8.526.233 | 542.284 | 6.4 | 12.7 | 21.35 | 60.63 | 8.82 | 78.42 | 14.67 | 6.52 | 87.50 | 2772 | 0.468 | 0.818 |
| PE | 7.225.744 | 1.504.146 | 20.8 | 47.2 | 25.18 | 58.82 | 10.39 | 33.60 | 55.27 | 10.04 | 83.89 | 1568 | 0.520 | 0.754* |
| CE | 6.998.494 | 1.380.598 | 19.7 | 45.7 | 20.75 | 70.40 | 5.27 | 27.93 | 64.71 | 6.77 | 76.89 | 1379 | 0.506 | 0.773 |
| PA | 6.265.355 | 1.279.470 | 20.4 | 52.3 | 35.27 | 54.35 | 7.06 | 19.34 | 69.87 | 9.77 | 75.07 | 1435 | 0.492 | 0.758 |
| SC | 5.725.753 | 213.505 | 3.7 | 7.6 | 23.40 | 64.29 | 6.32 | 76.28 | 19.22 | 4.07 | 88.36 | 2752 | 0.425 | 0.833 |
| MA | 5.186.562 | 1.173.467 | 22.6 | 56.1 | 25.37 | 64.36 | 7.10 | 20.10 | 66.39 | 12.61 | 70.93 | 1231 | 0.491 | 0.745 |
| GO | 5.080.755 | 458.522 | 9.0 | 17.8 | 32.57 | 51.92 | 8.40 | 36.24 | 54.18 | 9.19 | 93.19 | 2378 | 0.479 | 0.815 |
| PB | 3.247.397 | 629.343 | 19.4 | 45.9 | 20.77 | 68.96 | 6.15 | 35.72 | 55.55 | 7.96 | 79.57 | 1542 | 0.507 | 0.760 |
| ES | 2.990.490 | 281.991 | 9.4 | 19.7 | 35.40 | 47.82 | 11.54 | 38.59 | 49.79 | 11.21 | 85.90 | 2209 | 0.480 | 0.804 |
| AM | 2.801.182 | 620.384 | 22.1 | 57.4 | 39.37 | 47.39 | 7.38 | 18.39 | 68.79 | 4.91 | 82.83 | 1450 | 0.488 | 0.767 |
| PI | 2.708.160 | 547.041 | 20.2 | 51.1 | 15.56 | 77.43 | 4.30 | 22.63 | 64.83 | 12.25 | 69.44 | 1534 | 0.508 | 0.764 |
| RN | 2.660.565 | 475.300 | 17.9 | 41.6 | 21.40 | 67.01 | 7.42 | 39.49 | 50.90 | 9.17 | 81.98 | 1779 | 0.540 | 0.778 |
| MT | 2.638.230 | 215.226 | 8.2 | 16.8 | 29.99 | 56.73 | 8.14 | 32.30 | 56.00 | 9.86 | 86.28 | 2297 | 0.439 | 0.812 |
| AL | 2.441.794 | 509.551 | 20.9 | 48.9 | 22.88 | 64.16 | 9.31 | 29.27 | 60.36 | 9.55 | 80.57 | 1401 | 0.512 | 0.746 |
| DF | 2.253.132 | 165.080 | 7.3 | 16.7 | 29.21 | 49.74 | 11.27 | 39.98 | 48.66 | 10.71 | 96.48 | 4401 | 0.570 | 0.866 |
| MS | 2.024.884 | 190.938 | 9.4 | 19.5 | 32.47 | 51.90 | 8.96 | 42.38 | 46.93 | 6.50 | 88.13 | 2369 | 0.457 | 0.797 |
| SE | 1.740.124 | 363.180 | 20.9 | 46.4 | 18.27 | 67.76 | 9.11 | 25.20 | 61.61 | 12.85 | 79.95 | 1688 | 0.532 | 0.761 |
| RO | 1.267.105 | 126.771 | 10.0 | 22.8 | 41.08 | 40.87 | 12.93 | 30.74 | 59.24 | 8.65 | 78.53 | 1970 | 0.458 | 0.786 |
| TO | 1.182.307 | 141.802 | 12.0 | 27.6 | 31.00 | 58.67 | 6.45 | 23.20 | 62.14 | 13.19 | 82.89 | 1979 | 0.472 | 0.789* |
| AC | 614.375 | 126.918 | 20.7 | 48.6 | 44.38 | 38.93 | 11.20 | 21.44 | 66.25 | 8.56 | 74.45 | 1372 | 0.509 | 0.754 |
| AP | 577.534 | 115.676 | 20.0 | 57.5 | 36.37 | 51.04 | 7.63 | 21.40 | 65.28 | 11.81 | 88.76 | 1675 | 0.496 | 0.767* |
| RR | 401.496 | 77.314 | 19.3 | 43.6 | 34.35 | 37.89 | 16.94 | 20.62 | 57.25 | 7.73 | 78.18 | 1870 | 0.506 | 0.780 |
| BR | 157.826.587 | 19.295.378 | 12.2 | 26.6 | | | | | | | | | | 0.805 |

Valores do Brasil: 56,75% católicos, 26,85% evangélicos e 9,28% sem religião ([SIDRA 9537](https://apisidra.ibge.gov.br/values/t/9537/n1/all/v/1000140/p/2022/c133/95263,95277,2836/c2/6794/c58/95253)). Renda per capita de R$ 2.264 em 2025 ([SIDRA 7531](https://apisidra.ibge.gov.br/values/t/7531/n1/all/v/10824/p/2025/c1019/49243)). Gini de 0,511 em 2025 ([SIDRA 7435](https://apisidra.ibge.gov.br/values/t/7435/n1/all/v/10681/p/2025)). O asterisco (*) marca os três IDHM ambíguos explicados na lista de lacunas desta seção.

*A tabela usa ponto como separador decimal para manter o mesmo formato do CSV.*

### Cited Findings
- **[FATO]** Bolsa Família em setembro/2026 (`anomes_s=202609`, o mês mais recente disponível em 03/10/2026). A API devolveu 5.571 registros municipais com 19.295.378 famílias beneficiárias e R$ 13,04 bilhões repassados no mês, o que dá um benefício médio de cerca de R$ 676. SP (2,32 milhões) e BA (2,39 milhões) são as UFs com mais famílias atendidas. — [MDS VIS Data / API MiSocial (consulta direta)](https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&wt=json&fq=anomes_s:202609&rows=6000&fl=sigla_uf,qtd_familias_beneficiarias_bolsa_familia,valor_repassado_bolsa_familia_f)
- **[FATO]** Religião no Censo 2022, pessoas com 10 anos ou mais (tabela 9537). Os maiores percentuais de evangélicos estão no AC (44,4%), em RO (41,1%) e no AM (39,4%). Os menores estão no PI (15,6%), em SE (18,3%) e no CE (20,8%). Os maiores percentuais de católicos estão no PI (77,4%) e no CE (70,4%). Os maiores percentuais de pessoas sem religião estão em RR (16,9%) e no RJ (16,9%). — [IBGE SIDRA 9537](https://apisidra.ibge.gov.br/values/t/9537/n3/all/v/1000140/p/2022/c133/95263,95277,2836/c2/6794/c58/95253)
- **[FATO]** Cor ou raça no Censo 2022 (tabela 9605, percentual da população residente). As maiores proporções de brancos estão no RS (78,4%) e em SC (76,3%). A maior proporção de pretos está na BA (22,4%). As maiores proporções de pardos estão no PA (69,9%) e no AM (68,8%). — [IBGE SIDRA 9605](https://apisidra.ibge.gov.br/values/t/9605/n3/all/v/1000093/p/2022/c86/2776,2777,2779,2778,2780)
- **[FATO]** Situação do domicílio no Censo 2022 (tabela 10211, percentual de população urbana). A urbanização vai de 69,4% no PI e 70,9% no MA até 97,9% no RJ. — [IBGE SIDRA 10211](https://apisidra.ibge.gov.br/values/t/10211/n3/all/v/1000093/p/2022/c2661/32776/c1/1)
- **[FATO]** Renda domiciliar per capita da PNAD Contínua anual 2025 (tabela 7531). O DF tem a maior (R$ 4.401) e o MA a menor (R$ 1.231). Entre 2024 e 2025 a renda subiu em todas as UFs. — [IBGE SIDRA 7531](https://apisidra.ibge.gov.br/values/t/7531/n3/all/v/10824/p/2024,2025/c1019/49243)
- **[FATO]** Gini do rendimento domiciliar per capita da PNAD Contínua 2025 (tabela 7435). O DF tem o maior (0,570) e SC o menor (0,425). O Gini do Censo 2022 (tabela 10301) está no CSV e tem nível mais alto porque a fonte é outra. — [IBGE SIDRA 7435](https://apisidra.ibge.gov.br/values/t/7435/n3/all/v/10681/p/2024,2025); [IBGE SIDRA 10301](https://apisidra.ibge.gov.br/values/t/10301/n3/all/v/13418/p/2022)
- **[FATO]** Domicílios particulares permanentes ocupados no Censo 2022 (tabela 4712), usados como denominador da coluna "PBF % domic.". — [IBGE SIDRA 4712](https://apisidra.ibge.gov.br/values/t/4712/n3/all/v/381/p/2022)
- **[FATO]** IDHM 2024 do Radar IDHM (PNUD, publicado em 08/05/2026). O Brasil tem 0,805. O DF tem o maior valor (0,866) e o MA o menor (0,745). — [Wikipedia, que cita o PNUD Radar IDHM 2012–2024](https://pt.wikipedia.org/wiki/Lista_de_unidades_federativas_do_Brasil_por_%C3%8Dndice_de_Desenvolvimento_Humano); [PNUD Radar IDHM](https://www.undp.org/pt/brazil/publications/radar-idhm-evolucao-do-idhm-e-de-seus-componentes-periodo-de-2012-2024)
- **[FATO]** Eleitorado apto por UF em 2026. A soma das 27 UFs é 157.826.587, ou 158.745.463 com o exterior. — [TSE perfil do eleitorado 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip) (agregação feita no briefing anterior)

### Inferences
- O PBF tem relação inversa com renda e IDHM. As UFs com 20 ou mais famílias do PBF para cada 100 eleitores são MA, AM, BA, AL, SE, PE, AC, PA, PI e AP. Todas estão no Norte ou no Nordeste e têm renda per capita abaixo de R$ 1.700. No modelo, a cobertura do PBF e a renda vão ser quase colineares, então convém usar uma só ou ortogonalizar uma em relação à outra.
- Religião é a covariável que separa estados com renda parecida. O Norte combina PBF alto com muitos evangélicos (AC, RO, AM, AP e RR acima de 34%). O Nordeste interior combina PBF alto com muitos católicos (PI, CE, PB, SE, RN e AL com 64% ou mais de católicos). Isso é útil para distinguir o eleitorado de baixa renda do Norte do eleitorado de baixa renda do Nordeste.
- O DF é um caso à parte, com a maior renda e o maior Gini. RJ e RO têm alto percentual de pessoas sem religião ou de evangélicos combinado com renda média.

### Gaps
- **IDHM ambíguo em PE, TO e AP.** Na fonte secundária, essas três UFs aparecem com um valor só, sem a coluna de comparação. O valor de PE (0,754) está fora da ordem do ranking, que o coloca em 18º lugar, e por isso pode ser o número de 2023. É preciso conferir no painel Power BI ou no PDF do PNUD. O IDHM não é comparável ao IDH global.
- Não encontrei os números de famílias do PBF por UF publicados oficialmente pelo MDS em release. Os totais por UF foram somados por mim a partir dos dados municipais. Os registros de setembro/2026 parecem completos (5.571 municípios), mas a fonte não diz se são uma prévia.
- **Ressalva ecológica sobre o PBF.** Família beneficiária não é eleitor. Para estimar quantos eleitores vivem em famílias do PBF, é preciso usar o número de pessoas beneficiárias e a idade delas, que estão no CadÚnico e não foram baixados.
- O Censo 2022 divulgou religião apenas para pessoas com 10 anos ou mais. Não existe série anual por UF depois de 2022.

## (B) O que aconteceu na reta final da campanha (25/09 a 03/10/2026) e o que ainda está pendente?

### Takeaway
A reta final teve três fatos principais. O primeiro foi o colapso dos debates na TV aberta: a Record cancelou o seu debate em 23/09 e a Globo cancelou o dela em 01/10, menos de uma hora antes do horário, depois de decisões do TSE e do STF. Com isso, não houve nenhum debate na TV aberta com os dois líderes. O segundo foi a MP que proíbe as bets, de 25/09, cuja análise ficou para depois da eleição tanto no Congresso quanto no STF, com Fux. O terceiro foi o caso Master/Vorcaro, que segue sem desfecho: a delação de Vorcaro não foi homologada e o plenário do STF não marcou data para julgar o caso das mensagens com Moraes. Nenhum dos candidatos relevantes desistiu. Zema se manteve candidato, mas liberou os candidatos do Novo para apoiar Flávio.

### Cited Findings

**Debates**
- **[FATO] Início de set/2026.** O debate do pool SBT/CNN Brasil foi cancelado depois que Lula e Flávio confirmaram que não iriam. — [O Tempo, 23/09](https://www.otempo.com.br/eleicoes/2026/presidentes/2026/9/23/tv-record-cancela-debate-presidencial-apos-desistencia-de-lula-e-flavio-bolsonaro)
- **[FATO] 23/09.** A Record cancelou o debate de 27/09 porque Lula e Flávio não iriam participar. Segundo a emissora, os dois somam cerca de 70% das intenções de voto. A Record informou que, se houver 2º turno, fará um debate em 11/10. — [O Tempo](https://www.otempo.com.br/eleicoes/2026/presidentes/2026/9/23/tv-record-cancela-debate-presidencial-apos-desistencia-de-lula-e-flavio-bolsonaro); [Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2026/record-cancela-debate-presidencial-apos-desistencia-de-lula-e-flavio/); [Correio Braziliense](https://www.correiobraziliense.com.br/politica/2026/09/7506699-record-cancela-debate-apos-ausencia-de-lula-e-flavio-bolsonaro.html)
- **[FATO] 25/09.** A Globo marcou seu debate para 01/10 às 21h20. Foram convidados apenas os candidatos de partidos com cinco ou mais parlamentares eleitos em 2022: Lula (PT), Flávio Bolsonaro (PL), Augusto Cury (Avante) e Ronaldo Caiado (PSD). Zema (Novo) e Renan Santos (Missão) ficaram de fora por esse critério. — [Correio Braziliense, 25/09](https://www.correiobraziliense.com.br/politica/2026/09/7508901-confira-detalhes-do-debate-presidencial-da-tv-globo.html)
  - Há uma divergência: a CNN diz que Zema estava confirmado no dia do debate. Isso sugere que o critério da Globo mudou ou que outra decisão incluiu Zema. Não confirmei qual foi o caso.
- **[FATO] 30/09 e 01/10.** Esta é a sequência de eventos do debate da Globo:
  1. Em 30/09, Lula avisou que não iria ao debate e que daria entrevista ao Flow Podcast no mesmo horário.
  2. A ministra Estela Aranha, do TSE, proibiu a Globo de manter um púlpito vazio com o nome de Lula e proibiu perguntas dirigidas ao candidato ausente.
  3. Por volta das 19h de 01/10, Flávio anunciou que não iria, citando "censura imposta pelo TSE".
  4. Depois disso, o ministro Gilmar Mendes, do STF, mandou a Globo incluir Renan Santos (Missão).
  5. A Globo cancelou o debate, dizendo que as intimações alteravam as regras já acordadas.
  
  Caiado, Cury e Zema tinham confirmado presença. — [CNN Brasil, 01–02/10](https://www.cnnbrasil.com.br/eleicoes/tv-globo-cancela-debate-presidencial/); [Correio Braziliense, 10/2026](https://www.correiobraziliense.com.br/mundo/2026/10/7512880-globo-cancela-debate-e-cita-decisoes-de-gilmar-mendes-do-stf-e-estela-aranha-do-tse-o-que-dizem-juristas.html)
- **[OPINIÃO]** A Globo classificou as decisões como "interferência indevida" na liberdade de imprensa. — [Correio Braziliense / BBC](https://www.correiobraziliense.com.br/mundo/2026/10/7512880-globo-cancela-debate-e-cita-decisoes-de-gilmar-mendes-do-stf-e-estela-aranha-do-tse-o-que-dizem-juristas.html)
- **[ALEGAÇÃO/estudo]** Segundo levantamento da consultoria AP Exata obtido pela CNN, Lula e Flávio sofreram desgaste nas redes sociais depois do cancelamento. — [CNN Brasil, blog Caio Junqueira](https://www.cnnbrasil.com.br/blogs/caio-junqueira/eleicoes/cancelamento-de-debate-afeta-imagem-de-lula-e-flavio-diz-estudo/)

**Propaganda e calendário**
- **[FATO]** O horário eleitoral gratuito no rádio e na TV foi de 28/08 a 01/10, num total de 35 dias. Debates e propaganda na imprensa escrita eram permitidos até 02/10. Caminhadas e carreatas eram permitidas até as 22h de 03/10. — [TSE](https://www.tse.jus.br/comunicacao/radio/2026/Setembro/calendario-eleitoral-ultimo-dia-da-propaganda-eleitoral-gratuita-e-dos-comicios); [Mix Vale, 01/10](https://mixvale.com.br/2026/10/01/horario-eleitoral-do-1oturno-das-eleicoes-2026-termina-hoje-entenda)
- **Gap:** não encontrei descrição do conteúdo dos últimos programas de TV de cada campanha.

**Desistências e apoios**
- **[FATO] 26/09.** Zema (Novo) disse que não vai desistir. O vice dele, Eduardo Girão, declarou: "Em hipótese alguma vamos desistir". Zema liberou os candidatos do Novo para apoiar Flávio já no 1º turno. Marina Helena, candidata a deputada federal por SP, declarou apoio a Flávio, e Sebastião Coelho, candidato ao Senado pelo DF, já apoiava. — [CNN Brasil, 26/09](https://www.cnnbrasil.com.br/eleicoes/zema-descarta-desistencia-e-libera-candidatos-do-novo-para-apoiar-flavio/)
- **[OPINIÃO/relato]** A Revista Oeste publicou que Zema estava "prestes a desistir". Esse relato foi contrariado pela CNN e pelo O Antagonista. — [Revista Oeste](https://revistaoeste.com/no-ponto/zema-esta-prestes-a-desistir-da-candidatura-para-apoiar-flavio/); [O Antagonista](https://oantagonista.com.br/brasil/zema-descarta-desistir-e-mantem-candidatura-ao-planalto/)
- **[FATO]** A candidatura de Pablo Marçal foi indeferida por unanimidade em 11/09. — [Wikipedia, Eleição presidencial no Brasil em 2026](https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026)
- **Gap:** não achei registro de desistência ou de apoio formal de Caiado, Cury ou Renan Santos entre 25/09 e 03/10.

**Banco Master, Vorcaro e Moraes**
- **[FATO] 01/09.** O ministro André Mendonça retirou o sigilo de um relatório da PF com 52 mensagens que a PF atribui a uma conversa entre Moraes e Vorcaro. — [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121852/mendonca-retira-sigilo-de-apuracao-sobre-mensagens-de-vorcaro-e-moraes); [Poder360](https://www.poder360.com.br/poder-justica/fachin-atrasa-casos-que-envolvem-moraes-e-vorcaro-ate-22-de-setembro/)
- **[ALEGAÇÃO]** Em ofício ao presidente do STF, Edson Fachin, Moraes questionou se as mensagens identificadas pela PF realmente existem. Ele já tinha negado ter recebido mensagens em março/2026. — [Poder360](https://www.poder360.com.br/poder-justica/stf-aceitou-vaza-jato-mas-rejeita-chats-de-vorcaro-contra-moraes/)
- **[FATO]** Fachin juntou as apurações num único procedimento e adiou os casos para 22/09. A Poder360 diz que a tendência era deixar a decisão para depois da eleição. Mendonça liberou o caso para julgamento no plenário, mas a data não foi marcada. Até 03/10 não encontrei nenhuma decisão de plenário. — [Poder360](https://www.poder360.com.br/poder-justica/fachin-atrasa-casos-que-envolvem-moraes-e-vorcaro-ate-22-de-setembro/); [Terra/Estadão](https://www.terra.com.br/noticias/brasil/politica/mendonca-libera-para-julgamento-em-plenario-caso-sobre-mensagens-entre-moraes-e-vorcaro,d9c47723ddab5fd56a5074db9e55e208u5ior1i2.html)
- **[FATO]** A delação de Vorcaro não foi homologada. A proposta foi entregue à PGR e à PF em maio/2026 e, segundo a Correio/Blog da Denise, ficou "congelada" por causa da crise envolvendo o STF. — [Agência Brasil](https://agenciabrasil.ebc.com.br/justica/noticia/2026-05/defesa-de-vorcaro-entrega-proposta-de-delacao-pgr-e-pf); [Correio Braziliense, Blog da Denise](https://blogs.correiobraziliense.com.br/denise/com-stf-na-roda-vorcaro-fica-sem-delacao/)
- **[FATO e ALEGAÇÃO] 03/09.** No caso "Dark Horse", a PGR fechou delação com Antonio Carlos Freixo Júnior, o "Mineiro", que relata repasses feitos a pedido de Vorcaro para financiar o filme sobre Bolsonaro. A delação foi enviada a Mendonça. A investigação apura se parte do dinheiro foi desviada para Eduardo Bolsonaro, o que é uma suspeita e não está provado. A imprensa diz que Flávio negociou os pagamentos. — [Brasil de Fato, 03/09](https://www.brasildefato.com.br/2026/09/03/dark-horse-pgr-fecha-delacao-com-operador-de-repasses-para-filme-sobre-bolsonaro/); [CNN Brasil](https://www.cnnbrasil.com.br/politica/dark-horse-pgr-fecha-delacao-com-empresario-ligado-a-fundo-nos-eua/); [Poder360](https://www.poder360.com.br/poder-justica/delacao-relata-malas-de-dinheiro-e-remessas-de-vorcaro/)

**Bolsonaro: dosimetria, joias e cartão de vacina**
- **[FATO]** A Lei da Dosimetria (Lei 15.402/2026) foi promulgada em 08/05/2026. Em 09/05, Moraes, relator das ADIs da ABI e da federação PSOL-Rede, suspendeu a aplicação da lei às execuções penais até o plenário decidir. Não há data para o julgamento. Por isso, a redução não foi aplicada a Bolsonaro, cuja pena é de 27 anos e 3 meses. — [STF Notícias](https://noticias.stf.jus.br/postsnoticias/relator-suspende-aplicacao-da-lei-da-dosimetria-a-execucoes-penais-no-stf/); [Conjur, 09/05](https://conjur.com.br/2026-mai-09/alexandre-suspende-efeitos-da-lei-da-dosimetria-ate-analise-no-stf-2/); [Revista Oeste](https://revistaoeste.com/politica/moraes-suspende-aplicacao-da-lei-da-dosimetria-ate-stf-analisar-acoes/)
- **[ALEGAÇÃO/projeção]** Segundo estimativas da imprensa, se a lei for aplicada a pena cairia para cerca de 19 anos e 7 meses. — [Metrópoles](https://www.metropoles.com/brasil/o-que-muda-com-a-lei-da-dosimetria-e-como-bolsonaro-pode-se-beneficiar); [CNN Brasil](https://www.cnnbrasil.com.br/blogs/jussara-soares/politica/defesa-de-bolsonaro-prepara-pedido-para-reduzir-pena-com-base-na-dosimetria/)
- **[FATO]** O inquérito do cartão de vacina foi arquivado a pedido da PGR em março/2025. A PGR considerou que a prova se apoiava só na delação de Mauro Cid, e o caso pode ser reaberto. No caso das joias, Bolsonaro foi indiciado pela PF (associação criminosa, lavagem e peculato/apropriação). Não encontrei denúncia nem decisão nova entre 25/09 e 03/10/2026. — [InfoMoney](https://www.infomoney.com.br/politica/bolsonaro-soma-tres-inqueritos-abertos-na-pf-caso-do-cartao-de-vacina-foi-arquivado/); [ISTOÉ](https://istoe.com.br/joias-sauditas-e-fraude-em-cartao-de-vacina-como-estao-outros-indiciamentos-da-pf-contra-bolsonaro)

**MP das bets e CPI das Bets**
- **[FATO] 25/09.** O governo editou a MP 1.394/2026, que proíbe as bets e cassinos online, com vigência imediata. A MP vale por 60 dias, prorrogáveis por mais 60.
  - Cronograma da MP: não são aceitas novas apostas desde a edição. Os saques podem ser feitos até 05/10. Sites e apps saem do ar em 06/10. Os saldos serão devolvidos entre 09 e 14/10.
  - Também chegou ao Congresso o PL 5.477/2026, que torna crime explorar e anunciar bets.
  
  — [Agência Senado, 28/09](https://www12.senado.leg.br/noticias/materias/2026/09/28/mp-proibe-bets-e-determina-encerramento-das-operacoes-em-30-dias); [Metrópoles](https://www.metropoles.com/brasil/fim-das-bets-futuro-da-mp-divide-congresso-que-aguarda-passar-as-eleicoes); [Revista Oeste](https://revistaoeste.com/politica/fim-das-ibets-i-ainda-depende-do-congresso-para-se-tornar-definitivo/)
- **[FATO]** Os líderes do Congresso só vão discutir a MP depois da eleição e preveem mudanças no texto. — [Metrópoles](https://www.metropoles.com/brasil/fim-das-bets-futuro-da-mp-divide-congresso-que-aguarda-passar-as-eleicoes); [Brasil em Folhas, 29/09](https://www.brasilemfolhas.com.br/2026/09/lideres-do-congresso-preveem-mudancas-na-mp-que-proibe-bets/)
- **[OPINIÃO]** O PL chama a MP de "eleitoral". Clubes de futebol são contra; o presidente do Flamengo fala em perda de R$ 400 milhões. — [Metrópoles](https://www.metropoles.com/brasil/fim-das-bets-futuro-da-mp-divide-congresso-que-aguarda-passar-as-eleicoes)
- **[FATO] 28/09 a 02/10.** A ANJL e o Instituto Brasileiro de Jogo Responsável entraram no STF contra a MP (ADI 8024, entre outras). Fux assumiu a relatoria e, em 02/10, deu 72 horas para AGU e governo se manifestarem. Na prática, a análise da liminar fica para depois do 1º turno. — [O Tempo, 02/10](https://www.otempo.com.br/politica/judiciario/2026/10/2/fux-da-72-horas-ao-governo-antes-de-decidir-pedido-para-liberar-bets); [iGaming Brazil, 02/10](https://igamingbrazil.com/legislacao/2026/10/02/ministro-luiz-fux-assume-relatoria-de-acoes-contra-proibicao-das-bets-no-stf/); [Jornal de Brasília](https://jornaldebrasilia.com.br/noticias/politica-e-poder/luiz-fux-da-72-horas-para-governo-prestar-informacoes-sobre-mp-que-proibe-bets/)
- **[FATO]** A CPI das Bets do Senado encerrou os trabalhos em 12/06/2025 rejeitando, por 4 votos a 3, o relatório de Soraya Thronicke. O relatório pedia o indiciamento de 16 pessoas, entre elas Virgínia Fonseca e Deolane Bezerra. Soraya enviou as provas à PF, à PGR e ao STF. Não houve outra CPI das Bets em 2026 que eu tenha encontrado. — [Rádio Senado, 12/06/2025](https://www12.senado.leg.br/radio/1/noticia/2025/06/12/cpi-das-bets-rejeita-relatorio-final); [CNN Brasil](https://www.cnnbrasil.com.br/politica/relatorio-da-cpi-das-bets-e-rejeitado-por-4-votos-a-3/)

**TSE e logística do dia da eleição**
- **[FATO]** O presidente do TSE, Kassio Nunes Marques, mandou os 27 TREs acompanharem a oferta de transporte público gratuito em 04/10 e no eventual 2º turno em 25/10. A base é a ADPF 1.013 do STF, que declarou inconstitucional a omissão do poder público. No meio urbano, a frequência deve ser equivalente à de dia útil. — [CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/tse-cobra-tres-sobre-transporte-publico-gratuito-nas-eleicoes/); [TRE-SC, out/2026](https://www.tre-sc.jus.br/comunicacao/noticias/2026/Outubro/entenda-como-funcionara-o-transporte-publico-gratuito-no-dia-das-eleicoes-em-santa-catarina)
- **[FATO]** Lei Seca em 04/10:
  - Restrição em todo o estado: AC, AP, AM, CE, MA, MT, PA, PI e RR, com horários diferentes em cada um. Exemplos: CE das 8h às 18h; PI das 18h de sábado às 18h de domingo.
  - Restrição em apenas algumas localidades: BA, GO, RO, SE e TO.
  - As fontes divergem sobre o MT: aparece tanto como restrição total quanto parcial.
  
  — [Metrópoles](https://www.metropoles.com/brasil/lei-seca-1oturno-eleicoes-2026-estados); [Correio Braziliense, 10/2026](https://www.correiobraziliense.com.br/brasil/2026/10/7513034-veja-em-quais-estados-a-venda-de-bebidas-esta-proibida-nas-eleicoes.html)
- **Gap:** não encontrei dados sobre biometria em 2026, como o percentual do eleitorado com biometria ou eventual flexibilização. É preciso consultar o TSE.

**Violência e incidentes**
- **[FATO]** A Agência Pública contou 11 casos de violência política relatados por candidatos entre 12 e 28/09, o que dá um a cada 37 horas. O TSE registrou 62 denúncias de violência política de gênero desde a pré-campanha. Dois exemplos:
  - Em 27/09, em Itajaí (SC), a casa da mãe do candidato ao Senado Décio Lima (PT) foi apedrejada.
  - A deputada Isolda Dantas (PT-RN) denunciou ameaças de morte.
  
  — [Agência Pública, 10/2026](https://apublica.org/2026/10/levantamento-aponta-um-caso-de-violencia-politica-a-cada-37-horas-durante-campanha-de-2026); [CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/tse-registrou-62-casos-de-violencia-politica-de-genero-desde-a-pre-campanha/)
- **Gap:** não encontrei incidentes graves envolvendo os candidatos à presidência nesse período.

**Mídia e campanha digital**
- **[FATO]** Pela Biblioteca de Anúncios, a Meta recebeu R$ 236 milhões em anúncios eleitorais de 2026, 82% mais que em toda a eleição de 2022. — [Poder360](https://www.poder360.com.br/poder-eleicoes-2026/meta-ja-recebeu-r-236-milhoes-por-anuncios-eleitorais-em-2026/)
  - A página da Poder360 deu erro 403 quando tentei abrir. O número veio do resumo da busca.
- **[FATO]** Gastos dos presidenciáveis em anúncios na Meta, no recorte do Correio Braziliense de set/2026 (R$ 6,3 milhões no total):
  - Lula: R$ 5,2 milhões em 1.045 anúncios, ou 82,5% do total.
  - Flávio: R$ 702 mil em 128 anúncios.
  - Caiado: R$ 222 mil em 373 anúncios.
  
  — [Correio Braziliense](https://www.correiobraziliense.com.br/politica/2026/09/7509241-presidenciaveis-destinam-rs-63-milhoes-em-anuncios-nas-redes-82-sao-de-lula.html); [InfoMoney](https://www.infomoney.com.br/politica/em-um-mes-presidenciaveis-ja-gastaram-mais-de-r-55-milhoes-em-propaganda-digital/)
- **[FATO/análise] 02/10.** A Lupa analisou os anúncios na Meta entre 16/08 e 25/09:
  - Quatro dos seis principais candidatos gastaram R$ 5,6 milhões.
  - Cerca de R$ 738 mil (13%) foram para anúncios que a Lupa considera irregulares, com propaganda negativa ou desinformação.
  - Lula: R$ 4,6 milhões no total, dos quais R$ 460 mil (10%) em anúncios irregulares.
  - Flávio: mais de R$ 170 mil em anúncios irregulares.
  - Zema e Renan: nenhum anúncio irregular.
  
  A classificação de "irregular" é da própria Lupa. — [Agência Lupa, 02/10](https://www.agencialupa.org/eleicoes/2026/10/02/candidatos-a-presidencia-gastam-mais-de-r-740-mil-em-anuncios-na-meta-que-contrariam-regras-eleitorais/)
- **[FATO]** Últimas pesquisas, apenas como contexto (as séries estão em outra nota):
  - Datafolha de 01/10: Lula 42% e Flávio 38% no 1º turno; Lula 48% e Flávio 45% no 2º turno.
  - Datafolha final: 4.006 entrevistas em 03/10, divulgação às 18h45 de 03/10.
  
  — [CartaCapital](https://www.cartacapital.com.br/cartaexpressa/os-detalhes-da-ultima-pesquisa-datafolha-sobre-lula-x-flavio-bolsonaro-no-1o-turno/)

### Inferences
- Na prática, não houve nenhum debate na TV aberta com Lula e Flávio antes do 1º turno. O simulador não deve incluir choque de debate no 1º turno. O debate da Record previsto para 11/10, se houver 2º turno, é o próximo ponto de possível choque.
- A MP das bets tira os sites do ar em 06/10, dois dias depois do 1º turno. Fux e o Congresso deixaram a decisão para depois da eleição. O efeito eleitoral, se existir, vem do anúncio e não da execução da medida.
- Na direita, o voto útil está sendo feito por baixo, com candidatos do Novo apoiando Flávio, e não pela retirada de Zema. Para o modelo, o caminho é transferir parte do voto de Zema para Flávio, e não zerar Zema.
- No caso Master/Vorcaro, o STF e a PGR não produziram fato novo de peso entre 25/09 e 03/10. O risco é que alguma decisão saia depois do 1º turno, durante o 2º.

### Gaps
- Não encontrei perguntas de Quaest ou Datafolha sobre percepção de viés da mídia ou sobre o meio usado para se informar em 2026. A busca não trouxe resultados.
- Não encontrei dados de monitoramento digital de Palver, Bites ou Quaest com volume de menções por candidato na reta final.
- Os valores da Biblioteca de Anúncios da Meta mudam conforme o recorte de datas usado por cada veículo: o Correio fala em R$ 6,3 milhões e a Lupa em R$ 5,6 milhões. Não há um total oficial consolidado até 03/10.
- Também não encontrei:
  - os gastos com anúncios no Google;
  - decisões específicas do TSE sobre biometria e sobre direitos de resposta na última semana;
  - o conteúdo dos últimos programas de TV de cada campanha.
