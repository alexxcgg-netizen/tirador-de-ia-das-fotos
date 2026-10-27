# Segmentação do eleitorado brasileiro e comportamento de voto por segmento (2018–2026) — insumos para simulador presidencial por UF

Notas de pesquisa compiladas em 03/10/2026 (véspera do 1º turno de 04/10/2026). Fonte primária central para o perfil 2026: microdados oficiais do TSE "perfil_eleitorado_2026" (arquivo gerado em 14/07/2026, publicado no CDN do TSE em 17/07/2026), que eu baixei e agreguei diretamente — os totais batem exatamente com os divulgados pelo TSE (158.745.463). URL do arquivo: https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip

---

## 1. Perfil do eleitorado 2026 (TSE): total, UF, idade, gênero, escolaridade, exterior

### Takeaway
O eleitorado apto de 2026 é de 158.745.463 (+2.291.452 ou +1,46% vs 2022), 52,84% feminino, cada vez mais velho (60+ = 23,60%, vs 21,02% em 2022) e com escolaridade concentrada em médio completo (27,9%) e fundamental incompleto (21,2%); o Sudeste (SP+MG+RJ+ES) soma 41,8% e o Nordeste 27,4% do eleitorado.

### Cited Findings

**Totais (TSE, julho/2026)**
- Total apto 1º turno 04/10/2026: 158.745.463; crescimento de 2.291.452 (1,46%) vs 2022 (156.454.011) — [TSE](https://www.tse.jus.br/comunicacao/noticias/2026/Julho/mais-de-158-milhoes-de-eleitores-estao-aptos-votar-nas-eleicoes-2026); [Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/eleicoes-2026-mais-de-1587-milhoes-de-pessoas-estao-aptas-a-votar-no-brasil-neste-ano/)
- Voto obrigatório: 136.541.551; voto facultativo: 22.203.912 — [Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/eleicoes-2026-mais-de-1587-milhoes-de-pessoas-estao-aptas-a-votar-no-brasil-neste-ano/)
- Gênero: feminino 83.877.126 (52,84%); masculino 74.845.001 (47,15%); não informado 23.336 — [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip) (agregação própria)
- Eleitores no exterior (UF "ZZ"): 918.876 (0,58%), +31,82% vs 697.078 em 2022; 57,4% mulheres; 38,5% com superior completo — [Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/eleicoes-2026-mais-de-1587-milhoes-de-pessoas-estao-aptas-a-votar-no-brasil-neste-ano/); [Agência Brasil, 09/2026](https://agenciabrasil.ebc.com.br/politica/noticia/2026-09/quase-1-milhao-de-brasileiros-no-exterior-poderao-votar-nas-eleicoes); [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip)

**Faixas etárias 2026 (agregação própria dos microdados TSE; % do total de 158,7 mi)**
| Faixa | Eleitores | % |
|---|---|---|
| 16–17 (facultativo) | 1.634.244 (16a: 606.603; 17a: 1.027.641) | 1,03 |
| 18–24 | 17.588.253 | 11,08 |
| 25–34 | 30.168.463 | 19,00 |
| 35–44 | 31.257.206 | 19,69 |
| 45–59 | 40.638.548 | 25,60 |
| 60–69 | 20.205.622 | 12,73 |
| 70+ (facultativo) | 17.251.915 | 10,87 |
| 60+ (total) | 37.457.537 | 23,60 |
— [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip)
- 60+ passou de 32.891.438 (21,02%) em 2022 para 37.457.537 (23,60%) em 2026 (+4.566.099); faixa 21–34 caiu de 43.819.788 para 41.037.601; maior faixa quinquenal é 40–44 (15.994.391; 10,08%) — [Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/eleicoes-2026-mais-de-1587-milhoes-de-pessoas-estao-aptas-a-votar-no-brasil-neste-ano/); [Ric.com.br](https://ric.com.br/politica/eleicoes/total-de-leitores-aptos-votar-brasil-eleicoes-2026-tse/)
- ATENÇÃO (conflito): Bloomberg Línea cita "16–17 anos: 3.571.159 (2,25%)". Nos microdados, 3.571.159 = 16+17+18 anos (606.603+1.027.641+1.936.915). O número correto para 16–17 é 1.634.244 (1,03%) — [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip) vs [Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/eleicoes-2026-mais-de-1587-milhoes-de-pessoas-estao-aptas-a-votar-no-brasil-neste-ano/)

**Escolaridade 2026 (declarada no cadastro eleitoral; agregação própria)**
| Grau | Eleitores | % |
|---|---|---|
| Analfabeto | 5.519.686 | 3,48 |
| Lê e escreve | 9.623.112 | 6,06 |
| Fundamental incompleto | 33.604.061 | 21,17 |
| Fundamental completo | 9.723.908 | 6,13 |
| Médio incompleto | 28.891.452 | 18,20 |
| Médio completo | 44.292.209 | 27,90 |
| Superior incompleto | 9.033.880 | 5,69 |
| Superior completo | 18.037.161 | 11,36 |
| Não informado | 19.994 | 0,01 |
— [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip); totais arredondados confirmados por [TSE "Faltam 30 dias"](https://www.tse.jus.br/comunicacao/noticias/2026/Setembro/faltam-30-dias-brasil-tem-mais-de-158-milhoes-de-eleitoras-e-eleitores-aptos-a-votar) (médio completo 44,2 mi; fund. incompleto 33,6 mi; médio incompleto 28,8 mi; superior completo 18 mi)
- Pela primeira vez, eleitores com superior (completo) superam analfabetos (manchete Valor reproduzida pelo PT; página não acessível — 403) — [pt.org.br/Valor](https://pt.org.br/do-valor-pela-1a-vez-eleitores-com-ensino-superior-ultrapassam-analfabetos/). Nos microdados: superior completo 18,0 mi vs analfabetos 5,5 mi (ou 15,1 mi somando "lê e escreve").
- Raça/cor no cadastro eleitoral: 79,38% "não informado" (campo recém-coletado), portanto inútil para ponderação — [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip)

**Eleitorado 2026 por UF (todas as 27 UFs + exterior), com perfil (agregação própria dos microdados TSE)**
Colunas: eleitores; % do Brasil; % mulheres; % 16–17; % 60+; % 70+; % analfabeto+"lê e escreve"; % até fundamental incompleto (analf.+lê/escreve+fund. inc.); % superior completo.
| UF | Eleitores | % BR | %Fem | %16–17 | %60+ | %70+ | %Analf+LE | %≤Fund.inc | %Sup.compl |
|---|---|---|---|---|---|---|---|---|---|
| SP | 34.104.226 | 21,48 | 53,2 | 0,53 | 24,8 | 11,2 | 4,5 | 22,1 | 15,1 |
| MG | 16.377.659 | 10,32 | 52,5 | 0,81 | 26,2 | 12,4 | 10,5 | 34,4 | 10,2 |
| RJ | 12.857.000 | 8,10 | 54,0 | 0,53 | 27,6 | 13,5 | 6,7 | 29,0 | 9,5 |
| BA | 11.321.005 | 7,13 | 52,8 | 1,22 | 21,5 | 9,5 | 16,5 | 38,4 | 7,9 |
| PR | 8.609.026 | 5,42 | 52,8 | 0,90 | 24,9 | 11,0 | 5,6 | 26,7 | 14,3 |
| RS | 8.526.233 | 5,37 | 52,9 | 0,64 | 29,6 | 14,3 | 4,3 | 31,0 | 11,2 |
| PE | 7.225.744 | 4,55 | 53,6 | 1,33 | 21,7 | 9,9 | 15,2 | 37,6 | 8,3 |
| CE | 6.998.494 | 4,41 | 52,8 | 1,71 | 21,1 | 9,6 | 15,9 | 35,4 | 8,4 |
| PA | 6.265.355 | 3,95 | 50,8 | 1,71 | 17,4 | 7,8 | 12,3 | 37,3 | 7,5 |
| SC | 5.725.753 | 3,61 | 52,3 | 0,79 | 23,9 | 10,2 | 3,8 | 24,8 | 14,8 |
| MA | 5.186.562 | 3,27 | 51,9 | 2,14 | 18,8 | 8,7 | 18,3 | 38,8 | 6,1 |
| GO | 5.080.755 | 3,20 | 53,0 | 0,98 | 21,7 | 9,6 | 7,9 | 28,5 | 11,7 |
| PB | 3.247.397 | 2,05 | 52,9 | 1,63 | 22,3 | 10,5 | 18,9 | 41,9 | 8,5 |
| ES | 2.990.490 | 1,88 | 52,8 | 0,68 | 24,6 | 11,1 | 8,6 | 31,8 | 11,2 |
| AM | 2.801.182 | 1,76 | 51,4 | 1,83 | 15,1 | 6,1 | 8,9 | 27,2 | 8,8 |
| PI | 2.708.160 | 1,71 | 51,7 | 2,02 | 22,0 | 10,5 | 20,4 | 42,6 | 7,5 |
| RN | 2.660.565 | 1,68 | 52,8 | 1,40 | 22,4 | 10,3 | 14,5 | 38,7 | 8,9 |
| MT | 2.638.230 | 1,66 | 51,4 | 1,58 | 19,5 | 8,0 | 8,8 | 28,7 | 13,8 |
| AL | 2.441.794 | 1,54 | 53,5 | 1,66 | 19,7 | 8,7 | 20,5 | 44,3 | 6,2 |
| DF | 2.253.132 | 1,42 | 54,1 | 0,85 | 20,4 | 9,0 | 3,6 | 15,6 | 23,3 |
| MS | 2.024.884 | 1,28 | 52,8 | 1,12 | 22,6 | 9,9 | 8,5 | 32,1 | 14,1 |
| SE | 1.740.124 | 1,10 | 53,2 | 1,33 | 20,1 | 9,0 | 13,9 | 41,6 | 7,6 |
| RO | 1.267.105 | 0,80 | 51,6 | 1,90 | 19,6 | 8,1 | 10,8 | 35,1 | 9,9 |
| TO | 1.182.307 | 0,74 | 50,9 | 1,99 | 19,2 | 8,8 | 12,0 | 31,2 | 11,0 |
| AC | 614.375 | 0,39 | 51,6 | 2,29 | 15,9 | 7,1 | 16,2 | 35,4 | 9,5 |
| AP | 577.534 | 0,36 | 51,4 | 2,50 | 14,7 | 6,3 | 7,6 | 27,4 | 10,1 |
| RR | 401.496 | 0,25 | 50,9 | 2,88 | 15,5 | 6,5 | 7,7 | 24,6 | 10,7 |
| Exterior (ZZ) | 918.876 | 0,58 | 57,4 | 0,26 | 14,0 | 4,1 | 1,2 | 4,5 | 38,5 |
| **Brasil** | **158.745.463** | 100 | 52,84 | 1,03 | 23,60 | 10,87 | 9,54 | 30,71 | 11,36 |
— [TSE microdados 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip). Valores de SP, MG, RJ, BA, PR, RS confirmados por [TRE-SP](https://www.tre-sp.jus.br/comunicacao/noticias/2026/Julho/eleicoes-2026-sp-tem-21-4-do-eleitorado-nacional-e-soma-34-1-milhoes-de-aptos-a-votar-em-outubro), [TRE-PR](https://www.tre-pr.jus.br/comunicacao/noticias/2026/Julho/parana-tem-8-609-026-eleitores-aptos-a-votar-nas-eleicoes-2026), [Gazeta do Paraná](https://gazetadoparana.com.br/publico/parana-alcanca-5%C2%BA-maior-eleitorado-do-brasil-veja-numeros), [Portal Salvador FM](https://www.portalsalvadorfm.com.br/bahia/bahia-tem-4o-maior-eleitorado-do-brasil-nas-eleicoes-2026/)
- Paraná passou o RS e é, pela primeira vez, o 5º maior colégio eleitoral (8.609.026 vs 8.526.233) — [TRE-PR](https://www.tre-pr.jus.br/comunicacao/noticias/2026/Julho/parana-tem-8-609-026-eleitores-aptos-a-votar-nas-eleicoes-2026)
- Somas regionais (cálculo próprio a partir da tabela): Sudeste 66.329.375 (41,78%); Nordeste 43.529.845 (27,42%); Sul 22.861.012 (14,40%); Norte 13.109.354 (8,26%); Centro-Oeste 11.997.001 (7,56%); exterior 0,58%.

### Inferences
- O envelhecimento (+2,6 p.p. de 60+ em 4 anos) e a concentração de 70+ no Sul/Sudeste (RS 14,3%, RJ 13,5%, MG 12,4%) importam para o simulador porque 70+ é voto facultativo com abstenção alta — o eleitorado "apto" superestima o peso efetivo desses estados mais velhos.
- Os estados com maior parcela de baixa escolaridade (AL 44%, PI 43%, PB 42%, SE 42% até fundamental incompleto) coincidem com os de maior voto petista em 2018/2022 (ver seção 4), útil como covariável de UF.

### Gaps
- Não obtive a série TSE 2022 por UF com o mesmo detalhamento para calcular variação por UF 2022→2026 (só nacional).
- Raça/cor do cadastro eleitoral é inútil (79% não informado); usar Censo 2022.

---

## 2. Composição socioeconômica (Censo 2022 / PNAD) e Bolsa Família

### Takeaway
Censo 2022: católicos 56,7% e evangélicos 26,9% da população (vs 65,1% / 21,6% em 2010), com evangélicos mais fortes no Norte (36,8%) e Centro-Oeste (31,4%) e católicos no Nordeste (63,9%) e Sul (62,4%); pardos 45,3%, brancos 43,5%, pretos 10,2%. Bolsa Família atendia 19,29 mi de famílias em set/2026, com o Nordeste concentrando ~47% dos beneficiários.

### Cited Findings
**Religião (Censo 2022, divulgado em jun/2025; população 10+ anos)**
- Católicos: 65,1% (2010) → 56,7% (2022); evangélicos: 21,6% (35 mi, 2010) → 26,9% (47,4 mi, 2022) — [Brasil 61](https://brasil61.com/n/censo-2022-numero-de-catolicos-cai-enquanto-evangelicos-avancam-bras2514093); [Agência Gov](https://agenciagov.ebc.com.br/noticias/202506/censo-2022-catolicos-seguem-em-queda-evangelicos-e-sem-religiao-crescem-no-pais)
- Por região: católicos — Nordeste 63,9%, Sul 62,4%; evangélicos — Norte 36,8%, Centro-Oeste 31,4% — [Brasil 61](https://brasil61.com/n/censo-2022-numero-de-catolicos-cai-enquanto-evangelicos-avancam-bras2514093)
- Por UF (extremos): Piauí maior proporção de católicos (77,4%) e menor de evangélicos (15,6%); menores proporções de católicos em Roraima (37,89%), Rio de Janeiro (38,92%) e Acre (38,93%); maior proporção de evangélicos no Acre (44,4%); Acre e Rondônia são os únicos estados com evangélicos à frente de católicos — [Brasil 61](https://brasil61.com/n/censo-2022-numero-de-catolicos-cai-enquanto-evangelicos-avancam-bras2514093); [CNN Brasil](https://www.cnnbrasil.com.br/nacional/brasil/brasil-tem-recorde-de-evangelicos-e-menor-numero-de-catolicos-da-historia/)

**Raça/cor (Censo 2022, divulgado dez/2023)**
- Pardos 92,1 mi (45,3%) — superam brancos pela 1ª vez desde 1991; brancos 88,2 mi (43,5%); pretos 10,2% (eram 7,6% em 2010; +42,3%); indígenas 0,8%; amarelos 0,4% — [Agência Gov](https://agenciagov.ebc.com.br/noticias/202312/censo-2022-mostra-que-45-da-populacao-brasileira-e-pardos-e-43-5-branca)

**Bolsa Família (MDS, 2026)**
- Setembro/2026: 19,29 milhões de famílias, benefício médio R$ 678,18 (outras fontes citam R$ 691) — [Agência Brasil, 09/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-09/beneficiarios-com-nis-de-final-8-recebem-bolsa-familia-de-setembro); [Mix Vale](https://www.mixvale.com.br/2026/09/22/mds-libera-bolsa-familia-com-valor-medio-de-r-691-em-setembro/)
- Fevereiro/2026: 18,84 milhões de famílias — [Secom](https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/02/bolsa-familia-chega-a-18-84-milhoes-de-beneficiarios-do-pais-a-partir-desta-quinta-12); abril/2026: 18,9 milhões — [Secom](https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/04/bolsa-familia-chega-a-18-9-milhoes-de-beneficiarios-em-todo-o-brasil-a-partir-desta-quinta-16). Referência histórica: 21,18 mi em nov/2023 — [Agência Gov](https://agenciagov.ebc.com.br/noticias/202311/bolsa-familia-chega-a-21-18-milhoes-de-familias-a-partir-desta-sexta)
- Por UF (abr/2026): Bahia 2,36 mi famílias; São Paulo 2,22 mi; Pernambuco 1,48 mi; Nordeste 8,79 mi (fev/2026) e 8,86 mi (mar/2026) — [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/106275/bahia-e-sao-paulo-lideram-em-beneficiarios-do-bolsa-familia-veja-mapa); [Jornal Grande Bahia](https://jornalgrandebahia.com.br/2026/03/bolsa-familia-atende-mais-de-23-milhoes-de-familias-na-bahia-e-injeta-r-15-bilhao-na-economia-estadual-em-marco-de-2026/)
- Em pesquisa: em 2022, 23% da amostra Datafolha (28–29/10/2022) declarava receber Auxílio Brasil (38% no Nordeste; 39% entre renda até 2 SM; 13% no Sul) — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf)

### Inferences
- Razão famílias BF/eleitores (cálculo próprio, ordem de grandeza): Bahia ~2,36 mi famílias / 11,32 mi eleitores ≈ 0,21; São Paulo 2,22/34,10 ≈ 0,065; Pernambuco 1,48/7,23 ≈ 0,20; Nordeste 8,86/43,53 ≈ 0,20; Brasil 19,29/158,7 ≈ 0,12 famílias por eleitor. Como cada família tem em média >1 eleitor, a parcela de eleitores em domicílios beneficiários é maior — consistente com os ~23% de autodeclarados no Datafolha 2022.

### Gaps
- Tabela completa de famílias BF por UF (27 UFs) em 2026 não foi recuperada — consultar MDS VIS Data (https://aplicacoes.cidadania.gov.br/vis/data3/).
- Percentuais evangélico/católico para todas as 27 UFs (Censo 2022) não foram obtidos — só extremos e regiões; tabela completa no SIDRA (tabela de religião do Censo 2022).
- Renda/classe (distribuição de rendimento domiciliar per capita por UF; PNAD Contínua) e urbano/rural não foram levantados nesta rodada. "Sem religião" do Censo 2022 não verificado aqui.

---

## 3. Voto por segmento: 2022 (Datafolha final) e 2026 (Datafolha, Quaest, AtlasIntel)

### Takeaway
Os clivagens são estáveis entre 2022 e 2026: Lula lidera entre baixa renda (até 2 SM), baixa escolaridade, mulheres, católicos, Nordeste e beneficiários do BF; o candidato bolsonarista (Jair em 2022; Flávio em 2026) lidera entre renda 2 SM+, evangélicos (~2:1), homens, Sul e Centro-Oeste. Em 2026 a diferença de gênero aparece ampliada na AtlasIntel e o voto jovem (16–24) pró-Lula se mantém no Datafolha.

### Cited Findings

**2022 — Datafolha véspera do 2º turno (28–29/10/2022; 8.308 entrevistas; 253 municípios; ±2 p.p.; BR-08297/2022). Resultado nacional: Lula 52% x Bolsonaro 48% válidos (total: 49% x 45%; branco/nulo 4%; não sabe 2%)** — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf)

Votos válidos por segmento (Lula / Bolsonaro):
| Segmento | Lula | Bolsonaro | Peso na amostra (%) |
|---|---|---|---|
| Homens | 50 | 50 | 48 |
| Mulheres | 55 | 45 | 52 |
| 16–24 | 57 | 43 | 14 |
| 25–34 | 51 | 49 | 20* |
| 35–44 | 50 | 50 | 21* |
| 45–59 | 53 | 47 | 25* |
| 60+ | 52 | 48 | 20 |
| Fundamental | 61 | 39 | 28 |
| Médio | 49 | 51 | 46* |
| Superior | 49 | 51 | 26 |
| Renda até 2 SM | 61 | 39 | 46 |
| 2–5 SM | 45 | 55 | 36* |
| 5–10 SM | 42 | 58 | 11* |
| 10+ SM | 39 | 61 | 4* |
| Sudeste | 48 | 52 | 43 |
| Sul | 40 | 60 | 14 |
| Nordeste | 71 | 29 | 27 |
| Centro-Oeste | 39 | 61 | 7* |
| Norte | 48 | 52 | 8 |
| SP | 49 | 51 | — |
| RJ | 43 | 57 | — |
| MG | 53 | 47 | — |
| Católicos | 59 | 41 | 55 |
| Evangélicos | 31 | 69 | 25 |
| Espíritas | 59 | 41 | ~3 |
| Região metropolitana | 52 | 48 | — |
| Interior | 52 | 48 | — |
| Empresários | 23 | 77 | — |
| Desempregados (procuram) | 67 | 33 | — |
| Estudantes | 67 | 33 | — |
(*pesos derivados das bases ponderadas do próprio relatório: 25–34 = 1.661/8.308; médio = 3.813/8.308; 2–5 SM = 3.020; 5–10 SM = 884; 10+ SM = 323; Centro-Oeste = 616.) — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf)
- Mesmo relatório: sem religião = 9% da amostra (19% entre 16–24); evangélicos 25% (pentecostais 12%); 23% recebiam Auxílio Brasil — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf)
- Transferência 1º→2º turno 2022: Lula herdava 59% dos válidos de Tebet (41% Bolsonaro) e 56% dos de Ciro (44% Bolsonaro); 21% dos eleitores de Tebet e 18% dos de Ciro iam votar branco/nulo — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf)
- Estimativa derivada (José Eustáquio Diniz Alves) a partir do Datafolha: Lula ~11,7 mi votos evangélicos vs Bolsonaro ~26,1 mi; argumenta que o eleitorado sem religião foi decisivo — [EcoDebate, 31/10/2022](https://www.ecodebate.com.br/2022/10/31/o-eleitorado-sem-religiao-foi-o-fiel-da-balanca-da-vitoria-de-lula/)

**2026 — Datafolha 15–17/09/2026 (2.002 entrevistas; 125 municípios; ±2 p.p.; BR-04029/2026)**
- 1º turno nacional: Lula 39%, Flávio Bolsonaro 36%, Augusto Cury 6%, Ronaldo Caiado 4%, Renan Santos 3%, Romeu Zema 2%, Samara Martins 1%, Rui Costa Pimenta 1%; branco/nulo 6%; não sabe 3%. 2º turno: Lula 46% x Flávio 44% (rejeição 47% cada). 76% totalmente decididos — [NC News](https://ncnews.com.br/2026/09/18/datafolha-revela-onde-lula-e-flavio-bolsonaro-concentram-forca-veja-os-recortes-por-idade-renda-religiao-e-regiao/)

1º turno por segmento (% total de votos):
| Segmento | Lula | Flávio |
|---|---|---|
| Até 2 SM | 46 | 29 |
| 2–5 SM | 33 | 41 |
| Mais de 5 SM | 28 | 44 |
| Beneficiários Bolsa Família | 53 | 28 |
| Não beneficiários | 36 | 37 |
| Católicos | 43 | 32 |
| Evangélicos | 26 | 48 |
| Mulheres | 41 | 32 |
| Homens | 37 | 39 |
| 16–24 | 39 | 29 |
| 25–34 | 37 | 39 |
| 35–44 | 41 | 35 |
| 45–59 | 35 | 39 |
| 60+ | 43 | 33 |
| Fundamental | 47 | 30 |
| Médio | 36 | 38 |
| Superior | 36 | 37 |
| Nordeste | 56 | 26 |
| Sudeste | 34 | 37 |
| Sul | 27 | 45 |
| Centro-Oeste/Norte | 35 | 41 |
— [NC News (Datafolha 15–17/09/2026)](https://ncnews.com.br/2026/09/18/datafolha-revela-onde-lula-e-flavio-bolsonaro-concentram-forca-veja-os-recortes-por-idade-renda-religiao-e-regiao/); [Tribuna de Jundiaí](https://tribunadejundiai.com.br/politica/eleicoes-2026/datafolha-lula-flavio-bolsonaro-perfil-eleitor-renda-religiao/)
- Tendência no Datafolha: Flávio cresceu entre evangélicos e renda 2–5 SM; Lula cresceu entre 60+, Sudeste e católicos — [Tribuna de Jundiaí](https://tribunadejundiai.com.br/politica/eleicoes-2026/datafolha-lula-flavio-bolsonaro-perfil-eleitor-renda-religiao/)
- Observação: o artigo da NC News não informa a margem por segmento de beneficiários, nem o 2º turno por segmento.

**2026 — Quaest/Globo 24–27/09/2026 (2.004 entrevistas; BR-06520/2026; margem 3 p.p. católicos, 4 p.p. evangélicos)**
- Católicos, 1º turno: Lula 48% (era 43% na rodada anterior), Flávio 29% (27%). 2º turno: Lula 50% (46%), Flávio 37% (=); branco/nulo 10%
- Evangélicos, 1º turno: Lula 27% (23%), Flávio 46% (49%). 2º turno: Flávio 54% (58%), Lula 30% (28%); branco/nulo 13%
— [Estado de Minas](https://www.em.com.br/politica/2026/09/7509823-quaest-lula-avanca-entre-catolicos-e-evangelicos-apos-polemica.html); [Terra](https://www.terra.com.br/noticias/eleicoes/pesquisas/lula-avanca-entre-catolicos-e-evangelicos-em-meio-a-fake-news-sobre-nossa-senhora-mostra-pesquisa-quaest,c82f35c1b5cdca7a0be4a9e1723c74aeazy1o2bp.html)
- Contexto: rodada coincidiu com circulação de conteúdo falso sobre Flávio e o título de padroeira de N. Sra. Aparecida; diretor da Quaest atribui a recuperação de Lula a mulheres, baixa renda e Bolsa Família — [Terra](https://www.terra.com.br/noticias/eleicoes/pesquisas/lula-avanca-entre-catolicos-e-evangelicos-em-meio-a-fake-news-sobre-nossa-senhora-mostra-pesquisa-quaest,c82f35c1b5cdca7a0be4a9e1723c74aeazy1o2bp.html)

**2026 — AtlasIntel/Bloomberg 23–28/09/2026 (5.005 entrevistas, online)**
- 1º turno: Lula 46,2% x Flávio 43,1% (outra divulgação: 45% x 42%); 2º turno: empate 50% x 50% dos válidos — [Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/atlasintel-presidente-setembro-2026-4/); [Brasil de Fato](https://www.brasildefato.com.br/2026/09/29/pesquisa-atlas-lula-tem-45-contra-42-de-flavio-bolsonaro-no-1o-turno-2o-turno-esta-empatado/)
- Mulheres (1º turno): Lula 57,4% x Flávio 32,9%; homens: Flávio 52,4%; evangélicos: Flávio 62,7% x Lula 20,8% — [Gazeta do Povo / busca](https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/atlasintel-presidente-setembro-2026-4/)

### Inferences
- Para o simulador, os "swings" relativos são mais estáveis que os níveis: renda até 2 SM ≈ +20 p.p. de margem pró-Lula em 2022 (61–39) e +17 p.p. no 1º turno do Datafolha 2026 (46–29); evangélicos ≈ −38 p.p. (31–69) em 2022 vs −22 p.p. (Datafolha 1º turno) / −24 p.p. (Quaest 2º turno) / −42 p.p. (Atlas 1º turno) em 2026 — a dispersão entre institutos é grande para evangélicos.
- O gap de gênero no Datafolha 2022 era de 10 p.p. de margem (M: 0; F: +10 Lula); em 2026 o Datafolha mostra ~11 p.p. (H −2, M +9), enquanto a AtlasIntel indica gap muito maior (~25 p.p. de margem entre mulheres), o que sugere diferença metodológica (online vs presencial) — tratar como incerteza.
- Juventude: em 2022 16–24 era o grupo mais pró-Lula por idade (57% válidos); em 2026 (Datafolha) 16–24 segue pró-Lula (39–29) e 60+ ficou também pró-Lula (43–33), com 25–34 e 45–59 levemente pró-Flávio.
- Ensino superior: em 2022 empate técnico com vantagem a Bolsonaro (49–51); em 2026 empate (36–37). O voto de escolaridade é não-monotônico — o clivagem real é fundamental vs resto.

### Gaps
- Não obtive crosstabs de 2º turno por renda/escolaridade/idade de 2026 (Datafolha/Quaest) nem raça/cor em nenhuma pesquisa.
- Não obtive Quaest final de 2022 por segmento; nem voto por beneficiário de Auxílio Brasil em 2022 (o PDF Datafolha traz a proporção mas não o cruzamento de voto nas tabelas extraídas).
- Não obtive dados de 2018 por segmento (Datafolha/Ibope 2018); estudos de Nicolau não consultados nesta rodada.

---

## 4. Resultados por UF: 2º turno 2018 e 2022 (e 1º turno 2022) + abstenção

### Takeaway
Lula venceu 2022 com 50,90% x 49,10% (13 UFs para Lula, 14 incl. DF para Bolsonaro); Bolsonaro venceu 2018 com 55,13% x 44,87%. Entre 2018 e 2022 o PT ganhou terreno em praticamente todas as UFs, sobretudo no Sudeste (SP +12,7 p.p., MG +8,4) e Centro-Oeste/DF, mas perdeu ligeiramente em AC, PE, CE, RR e RO.

### Cited Findings
**2º turno — % dos votos válidos do candidato do PT (Haddad 2018 / Lula 2022); Bolsonaro = 100 − valor. Coluna Δ = cálculo próprio.**
| UF | Haddad 2018 | Lula 2022 | Δ PT (p.p.) | 1º T 2022 Lula | 1º T 2022 Bolsonaro | Abst. 1º T 2022 |
|---|---|---|---|---|---|---|
| AC | 22,78 | 29,70 | +6,9 | 29,26 | 62,50 | 22,43 |
| AL | 59,92 | 58,68 | −1,2 | 56,50 | 36,05 | 22,37 |
| AP | 49,80 | 48,64 | −1,2 | 45,67 | 43,41 | 19,51 |
| AM | 49,73 | 51,10 | +1,4 | 49,58 | 42,80 | 20,14 |
| BA | 72,69 | 72,12 | −0,6 | 69,73 | 24,31 | 21,35 |
| CE | 71,11 | 69,97 | −1,1 | 65,91 | 25,38 | 17,45 |
| DF | 30,01 | 41,19 | +11,2 | 36,85 | 51,65 | 17,54 |
| ES | 36,94 | 41,96 | +5,0 | 40,40 | 52,23 | 20,75 |
| GO | 34,48 | 41,29 | +6,8 | 39,51 | 52,16 | 21,72 |
| MA | 73,26 | 71,14 | −2,1 | 68,84 | 26,02 | 22,20 |
| MT | 33,58 | 34,92 | +1,3 | 34,39 | 59,84 | 23,38 |
| MS | 34,78 | 40,51 | +5,7 | 39,04 | 52,70 | 22,08 |
| MG | 41,81 | 50,20 | +8,4 | 48,29 | 43,60 | 22,28 |
| PA | 54,81 | 54,75 | −0,1 | 52,22 | 40,27 | 21,22 |
| PB | 64,98 | 66,62 | +1,6 | 64,21 | 29,62 | 17,29 |
| PR | 31,57 | 37,60 | +6,0 | 35,99 | 55,26 | 19,48 |
| PE | 66,50 | 66,93 | +0,4 | 65,27 | 29,91 | 18,20 |
| PI | 77,05 | 76,86 | −0,2 | 74,25 | 19,90 | 17,69 |
| RJ | 32,05 | 43,47 | +11,4 | 40,68 | 51,09 | 22,74 |
| RN | 63,41 | 65,10 | +1,7 | 62,98 | 31,02 | 18,17 |
| RS | 36,76 | 43,65 | +6,9 | 42,28 | 48,89 | 19,78 |
| RO | 27,82 | 29,34 | +1,5 | 28,98 | 64,36 | 24,65 |
| RR | 28,45 | 23,92 | −4,5 | 23,05 | 69,57 | 16,70 |
| SC | 24,08 | 30,73 | +6,7 | 29,54 | 62,21 | 18,43 |
| SP | 32,03 | 44,76 | +12,7 | 40,89 | 47,71 | 21,61 |
| SE | 67,54 | 67,21 | −0,3 | 63,82 | 29,16 | 18,35 |
| TO | 51,02 | 51,36 | +0,3 | 50,40 | 44,00 | 18,54 |
| **Brasil** | **44,87** | **50,90** | **+6,0** | 48,43* | 43,20* | 20,95 |
— 2018: [Wikipédia PT — Resultados 2018](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018); 2022: [Wikipédia PT — Resultados 2022](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2022); confirmados parcialmente por [CNN Brasil](https://www.cnnbrasil.com.br/politica/veja-estados-em-que-lula-ganhou-e-perdeu-no-segundo-turno/) e [ND Mais](https://ndmais.com.br/politica/estados-que-mais-votaram-em-lula-e-bolsonaro-em-2022-veja-os-maiores-percentuais/) (PI 76,83% / BA 72,11% / MA 70,93% — pequenas divergências de 0,01–0,2 p.p. com a Wikipédia; SP 44,76/55,24; RJ 43,47/56,53; SC 69,27 Bolsonaro). *Totais nacionais do 1º turno 2022 (48,43/43,20) são do meu conhecimento prévio do TSE, não verificados nesta rodada.
- A coluna "1º T 2022" da Wikipédia mistura % de válidos por candidato; os 4 candidatos principais (Lula, Bolsonaro, Tebet, Ciro) estão disponíveis na mesma fonte (ex.: SP Tebet 6,34%, Ciro 5,07%; CE Ciro 7,49%) — [Wikipédia PT — Resultados 2022](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2022)
- 2018 nacional: 1º turno Bolsonaro 46,03%, Haddad 29,28%, Ciro 12,47%; 2º turno Bolsonaro 57.797.847 (55,13%) x Haddad 47.040.906 (44,87%) — [Wikipedia EN 2018](https://en.wikipedia.org/wiki/2018_Brazilian_presidential_election); [Wikipédia PT 2018](https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018)

### Inferences
- Swing uniforme 2018→2022 de +6,0 p.p. pró-PT foi muito heterogêneo: forte no Sudeste/Sul/CO urbano (SP +12,7, RJ +11,4, DF +11,2, MG +8,4), nulo ou levemente negativo no Nordeste (já saturado, ~65–77%) e no Norte (RR −4,5). Para o simulador, modelar swing proporcional/logit por UF em vez de uniforme.
- MG (50,20%) e AM, TO, AP (~49–51%) foram os "estados-pêndulo" de 2022.

### Gaps
- Abstenção por UF no 2º turno de 2022 completa (só extremos) e abstenção por UF em 2018 não foram tabuladas.

---

## 5. Comparecimento/abstenção por segmento e entre turnos (2018, 2022)

### Takeaway
Abstenção nacional 2018: ~20,3% (1º T) → ~21,3% (2º T); 2022: 20,95% → 20,59% — a primeira vez na história em que a abstenção caiu no 2º turno. Abstenção é muito maior entre 60+ (34,5% em 2022) e menor no Nordeste (19,3%) que na média.

### Cited Findings
- 2022: abstenção 20,95% no 1º turno (32,77 mi) e 20,59% no 2º turno (~32,2 mi); inédito o 2º turno ter menos abstenção que o 1º; o 2º turno teve ~570 mil votos válidos a mais que o 1º — [CNN Brasil](https://www.cnnbrasil.com.br/politica/em-cenario-inedito-no-pais-abstencao-no-2o-turno-e-menor-do-que-no-1o/); [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2022-10/segundo-turno-teve-570-mil-votos-validos-mais-do-que-primeiro-turno); [CNN Brasil ranking UF](https://www.cnnbrasil.com.br/politica/acre-teve-maior-abstencao-no-2o-turno-e-o-df-a-menor-veja-ranking-de-estados/)
- 2º turno 2022 por UF (extremos): maior abstenção Acre 28,41%, Amapá 27,17%, Rondônia 24,68%; menor DF 16,72%, Paraíba 16,74%, Ceará 17,14% — [CNN Brasil](https://www.cnnbrasil.com.br/politica/acre-teve-maior-abstencao-no-2o-turno-e-o-df-a-menor-veja-ranking-de-estados/)
- Notar: Acre e Amapá subiram de abstenção do 1º (22,4% / 19,5%) para o 2º turno (28,4% / 27,2%) — cálculo comparando [Wikipédia PT 2022](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2022) e [CNN Brasil](https://www.cnnbrasil.com.br/politica/acre-teve-maior-abstencao-no-2o-turno-e-o-df-a-menor-veja-ranking-de-estados/)
- 60+: abstenção 37,1% (2014) → 36,4% (2018) → 34,5% (2022); Nordeste: média de 25,5% em 1998 → 19,2%/19,3% em 2022 (abaixo da média nacional; Sudeste lidera abstenção) — [Gazeta do Povo](https://gazetadopovo.com.br/economia/abstencao-atinge-niveis-de-1998-lideranca-e-do-sudeste)
- 2018: comparecimento 79,67% (1º T) e 78,70% (2º T); 117.364.654 e 115.933.451 votantes — [Wikipedia EN 2018](https://en.wikipedia.org/wiki/2018_Brazilian_presidential_election); [Wikipédia PT 2018](https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018)
- Escolaridade e abstenção: análise local (RN, 2022) aponta relação entre baixa escolaridade e abstenção — [MQD Lab](https://mqdlab.substack.com/p/a-abstencao-nas-eleicoes-de-2022-e-o-fator-escolaridade-no-rn) (não lido na íntegra)

### Inferences
- Como 60+ (23,6% do eleitorado 2026, sendo 10,9% com 70+) tem abstenção ~1,7x a média, o peso efetivo dos idosos no comparecimento é bem menor que no cadastro; RS, RJ, MG (mais velhos) terão comparecimento relativo menor, o Nordeste maior. A queda de abstenção no 2º turno de 2022 (com transporte gratuito em vários municípios) beneficiou mobilização em ambos os lados — não há dado aqui que permita atribuir a quem.

### Gaps
- Abstenção por faixa etária/escolaridade/gênero para 2018 e 2022 (TSE "comparecimento e abstenção" por perfil) não tabulada; a tabela completa de 27 UFs no 2º turno 2022 e em 2018 também não.

---

## 6. Padrões estruturais e mudanças em 2026: gênero, jovens, evangélicos, Nordeste vs Sul/Sudeste

### Takeaway
A polarização regional persiste: Nordeste segue ~2:1 pró-Lula (71–29 em 2022; 56–26 no 1º turno Datafolha 2026), Sul é o reduto oposto (40–60 em 2022; 27–45 em 2026). Evangélicos permanecem o segmento mais pró-Bolsonaro, mas com sinais de oscilação em setembro/2026; o gap de gênero continua com Lula à frente entre mulheres.

### Cited Findings
- Nordeste 2022 (Datafolha válidos): Lula 71 x 29; Sul 40 x 60; Centro-Oeste 39 x 61; Sudeste 48 x 52; Norte 48 x 52 — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf)
- Nordeste 2026 (Datafolha 1º T, set/26): Lula 56 x Flávio 26; Sul 27 x 45; Sudeste 34 x 37; CO/Norte 35 x 41 — [NC News](https://ncnews.com.br/2026/09/18/datafolha-revela-onde-lula-e-flavio-bolsonaro-concentram-forca-veja-os-recortes-por-idade-renda-religiao-e-regiao/)
- Evangélicos: 2022 31 x 69 (Datafolha válidos) → 2026 Quaest 2º T 30 x 54 (24–27/09; antes 28 x 58); Datafolha 1º T 26 x 48; AtlasIntel 1º T 20,8 x 62,7 — fontes nas seções acima
- Mulheres: 2022 55 x 45 (Datafolha válidos) → 2026 Datafolha 1º T 41 x 32; AtlasIntel 1º T 57,4 x 32,9 — fontes nas seções acima
- Evangélicos são ~25–27% do eleitorado nas amostras (Datafolha 2022: 25%; Datafolha 2022 também citado com 27% em análise de Diniz Alves) — [Datafolha via Poder360, PDF](https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf); [EcoDebate](https://www.ecodebate.com.br/2022/10/31/o-eleitorado-sem-religiao-foi-o-fiel-da-balanca-da-vitoria-de-lula/)

### Inferences
- Polarização Nordeste x Sul em 2026 no 1º turno (margem +30 vs −18 p.p.) é da mesma ordem que em 2022 (+42 vs −20 em válidos de 2º turno), sugerindo que a geografia de 2022 é um bom prior para 2026 por UF.
- Mudança mais visível para 2026: Lula mais competitivo entre 60+ e católicos (Datafolha/Quaest) e Flávio mais forte em renda 2–5 SM e evangélicos (Datafolha) — tendências de curto prazo, sujeitas a ruído.

### Gaps
- Não encontrei estudos acadêmicos de 2026 sobre mudança de padrões; análises de Nicolau (voto por segmento 2018/2022) não consultadas.
- Pesquisas estaduais por UF (2026) não fazem parte deste escopo e não foram coletadas.
