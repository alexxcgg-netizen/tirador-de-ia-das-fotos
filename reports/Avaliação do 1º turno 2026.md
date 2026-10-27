# Avaliação do 1º turno de 2026: resultado, previsões e projeção do 2º turno

*Escrito em 5/10/2026, madrugada seguinte ao 1º turno (4/10). Base: **98,64% das seções totalizadas** (TSE, boletim
nacional de 21:03:24 de 4/10, horário de Brasília), com conferência nos arquivos por UF do TSE baixados às 21:06
(98,76%). Números provisórios: as UFs ainda parciais foram completadas pela projeção por município de
`simulador/resultado_1t.py`. Este texto não recomenda candidato.*

Convenções: votos válidos em %; p.p. = pontos percentuais; margem = Lula − Flávio; erro = previsto − real (positivo =
previsão acima do resultado). **[calc]** marca números calculados para este relatório a partir dos arquivos do TSE e
do repositório. Os demais vêm de `simulador/AVALIACAO_1T.md` e `simulador/data/avaliacao_1t.json` (avaliação gerada
automaticamente), `simulador/web/resultados_2t.json` (2º turno), `simulador/web/resultados.json` (previsão de véspera)
e `simulador/data/mercado_ao_vivo.csv` (mercados). Horários em Brasília (UTC−3).

## Em resumo

- **Haverá 2º turno entre Flávio Bolsonaro e Lula em 25/10.** Flávio terminou em 1º: 47,1% x 45,1% (projeção com
  98,6%), margem de 2,0 p.p. a favor de Flávio. Os outros quatro candidatos somaram 7,8%.
- **O nacional foi bem previsto pela visão calibrada do modelo principal** (erro na margem −0,5 p.p.; erro médio
  nos dois primeiros 0,5 p.p.). A média simples das pesquisas acertou Lula (+0,2) e subestimou Flávio (−3,2),
  porque superestimou os candidatos menores.
- **O erro foi regional.** O modelo subestimou a margem de Lula no Nordeste e no Norte e a superestimou no Sul: a
  polarização regional foi maior que a prevista. Ainda assim, todas as UFs ficaram dentro dos intervalos de 80% da
  visão calibrada para Lula, e 53 de 54 intervalos (Lula e Flávio) foram cumpridos.
- **Mercados erraram o 1º colocado** (davam ~71–72% para Lula em 1º) e acertaram que não haveria decisão no 1º
  turno (5%, melhor que os modelos).
- **A projeção do 2º turno, já com o 1º turno real, dá 14,5% para Lula e 85,5% para Flávio**, com Lula em 47,2%
  (80%: 43,8–50,7). Os mercados estão em 14–17% para Lula. A incerteza é grande: o modelo errou o 2º turno em ~2
  p.p. nas eleições passadas, e três semanas de campanha ainda vêm pela frente.

## 1. Resultado

### 1.1 Nacional

| Candidato | Válidos (%) | Votos (TSE, 98,76%) [calc] | 2022, 1º turno (%) |
|---|---|---|---|
| Flávio Bolsonaro (PL) | **47,07** | 55.658.655 | Bolsonaro 43,20 |
| Lula (PT) | **45,11** | 52.900.934 | Lula 48,43 |
| Augusto Cury | 2,89 | 3.417.328 | – |
| Renan Santos | 2,25 | 2.657.400 | – |
| Ronaldo Caiado | 2,18 | 2.588.129 | – |
| Romeu Zema | 0,27 | 324.249 | – |
| Outros (6 candidatos com votos no arquivo) | 0,22 | 258.772 [calc] | – |

Percentuais da primeira coluna: projeção com 98,64% (UFs parciais completadas por município). O arquivo nacional
do TSE com 98,76% dá 47,25% x 44,91% sem projeção. A diferença (~0,2 p.p. por candidato) existe porque faltam
sobretudo seções do Nordeste (BA 94,6%, AL 95,5% e CE 96,4% totalizadas). Com 98,76% apurado, Flávio está 2,76
milhões de votos à frente **[calc]**. Em relação ao 1º turno de 2022, o candidato do PT perdeu 3,3 p.p. e o
candidato do PL ganhou 3,9 p.p. **[calc]**.

### 1.2 Por região

Arquivos do TSE por UF com 97–100% totalizado em cada região. Não são projeções. **[calc]**

| Região | Peso nos válidos | Lula | Flávio | Margem 2026 | Margem 2022 (Lula − Bolsonaro, 1º turno) | Variação |
|---|---|---|---|---|---|---|
| Nordeste | 27,8% | 63,5 | 31,1 | +32,5 | +39,8 | −7,3 |
| Norte | 8,5% | 44,3 | 49,5 | −5,2 | +1,6 | −6,8 |
| Sudeste | 40,8% | 39,6 | 51,4 | −11,8 | −4,9 | −6,9 |
| Centro-Oeste | 7,7% | 32,6 | 56,5 | −23,9 | −15,9 | −8,0 |
| Sul | 14,9% | 31,3 | 60,1 | −28,8 | −17,8 | −11,0 |
| Exterior | 0,3% | 47,1 | 43,8 | +3,3 | +5,6 | −2,3 |

A margem caiu para o PT em todas as regiões, menos no Nordeste e mais no Sul. Como resultado, a distância entre
Nordeste e Sul passou de 57,6 para 61,3 p.p. **[calc]**.

### 1.3 UFs-chave

| UF | % totalizado | Lula | Flávio | Margem | Margem 2022 |
|---|---|---|---|---|---|
| SP | 99,7 | 38,2 | 51,9 | −13,7 | −6,8 |
| MG | 97,7 | 43,0 | 48,5 | −5,4 | +4,7 |
| RJ | 99,6 | 39,4 | 53,0 | −13,6 | −10,4 |
| BA | 94,6 | 65,8 | 28,9 | +36,9 | +45,4 |
| PR | 100,0 | 31,2 | 59,9 | −28,7 | −19,3 |
| RS | 100,0 | 35,7 | 55,6 | −19,9 | −6,6 |
| PE | 99,0 | 63,3 | 31,2 | +32,1 | +35,4 |
| CE | 96,4 | 62,9 | 31,6 | +31,4 | +40,5 |
| PA | 98,0 | 49,5 | 44,8 | +4,7 | +11,9 |
| AM | 98,0 | 47,8 | 45,4 | +2,3 | +6,8 |
| GO | 99,8 | 31,1 | 53,6 | −22,6 | −12,6 |

Fonte: arquivos `{uf}-c0001-e006257-u.json` do TSE, com 98,76% no nacional **[calc]**. **MG**, o maior colégio
eleitoral em disputa, foi para Flávio por 5,4 p.p. depois de ter dado vitória a Lula em 2022. No **Amapá**, com
100% apurado, Lula ficou à frente por 225 votos. Lula venceu em 12 UFs (as 9 do Nordeste, PA, AM e AP) e no
exterior. Flávio venceu nas outras 15 UFs. **[calc]**

### 1.4 Comparecimento, brancos e nulos x 2022

Calculado com os campos `e.est` (eleitores das seções totalizadas), `e.c`, `e.a`, `v.vb` e `v.tvn` dos arquivos do
TSE por UF. A base de 2022 é `simulador/data/resultados_uf_2002_2022.csv`. **[calc]**

| | Abstenção 2026 | Abstenção 2022 | Brancos 2026 (% comparec.) | Brancos 2022 | Nulos 2026 | Nulos 2022 |
|---|---|---|---|---|---|---|
| **Brasil** | **21,06%** | **20,95%** | **1,84%** | **1,59%** | **2,93%** | **2,82%** |
| Nordeste | 18,36% | 19,53% | 1,66% | 1,34% | 3,43% | 3,10% |
| Norte | 19,45% | 20,94% | 1,04% | 0,87% | 2,40% | 1,67% |
| Sudeste | 22,69% | 21,95% | 2,24% | 1,92% | 3,23% | 3,30% |
| Centro-Oeste | 21,70% | 21,34% | 1,20% | 1,21% | 2,12% | 1,94% |
| Sul | 20,45% | 19,34% | 1,87% | 1,68% | 1,89% | 2,01% |
| Exterior | 61,90% | 56,28% | 1,73% | 1,60% | 1,48% | 1,53% |

- No total, o comparecimento ficou praticamente igual ao de 2022 (+0,1 p.p. de abstenção). O modelo usava a
  abstenção e os brancos/nulos de 2022 por UF, com ruído, e essa premissa se confirmou no agregado.
- A distribuição regional mudou. A abstenção **caiu** no Nordeste (−1,2 p.p.) e no Norte (−1,5) e **subiu** no Sul
  (+1,1) e no Sudeste (+0,7). Nas UFs, RO (−2,9), MA (−2,5), PA (−2,1), AP (−2,1), AC (−2,0) e CE (−2,0) tiveram as maiores quedas, e RS
  (+1,6), MS (+1,8) e DF (+1,4) as maiores altas.
- Os brancos subiram em todas as regiões (+0,25 p.p. no país). Os nulos subiram pouco, com altas maiores em AL
  (+1,5), PA (+1,5) e CE (+0,9).
- Ressalva: as seções ainda não totalizadas (1,3% do eleitorado, quase todas no Nordeste e no exterior) costumam ter
  abstenção um pouco diferente da média. Os números podem mudar em alguns décimos.

## 2. Ranking dos previsores

### 2.1 Margem e erro médio (nacional)

Ordenado pelo erro absoluto na margem Lula − Flávio. MAE 2 = erro absoluto médio nos dois primeiros. MAE todos =
erro médio em todos os candidatos (7 categorias). Pesquisas: última de cada instituto, convertida para votos
válidos quando publicada em votos totais. Modelos: média das simulações.

| # | Previsor | Lula prev. | Flávio prev. | Erro na margem | MAE 2 | MAE todos |
|---|---|---|---|---|---|---|
| 1 | Futura (2–3/10) | 42,6 | 44,7 | −0,2 | 2,4 | 1,4 |
| 2 | Gerp (30/9–2/10) | 44,1 | 46,2 | −0,2 | 0,9 | 0,7 |
| 3 | **Modelo principal: calibrado** | 44,4 | 46,8 | −0,5 | **0,5** | **0,4** |
| 4 | Vox Brasil (29/9–1/10) | 45,0 | 45,9 | +1,1 | 0,7 | 1,0 |
| 5 | Palver (30/9–3/10) | 43,4 | 47,5 | −2,1 | 1,0 | 1,5 |
| 6 | Modelo alternativo: histórico | 43,8 | 48,1 | −2,3 | 1,2 | 1,2 |
| 7 | Modelo principal: viés pleno | 43,3 | 48,1 | −2,8 | 1,4 | 0,7 |
| 8 | Modelo principal: neutro | 46,1 | 45,2 | +2,8 | 1,4 | 0,7 |
| 9 | PoderData (30/9–2/10) | 44,7 | 43,6 | +3,0 | 1,9 | 1,0 |
| 10 | Ideia (25–28/9)\* | 50,6 | 49,4 | +3,2 | 3,9 | – |
| 11 | Modelo alternativo: neutro | 46,6 | 45,3 | +3,3 | 1,6 | 1,6 |
| 12 | Média das pesquisas (agregador, sem ajustes) | 45,3 | 43,8 | +3,4 | 1,7 | 0,9 |
| 13 | Datafolha (3/10) | 45,6 | 43,5 | +4,1 | 2,1 | 1,2 |
| 14 | Quaest (2–3/10) | 46,0 | 43,7 | +4,3 | 2,1 | 1,1 |
| 15 | AtlasIntel (27/9–2/10) | 47,0 | 44,1 | +4,8 | 2,4 | 1,4 |
| 16 | IFP (29/9–2/10) | 43,9 | 40,5 | +5,3 | 3,9 | 2,3 |
| 17 | Real Time Big Data (26–30/9) | 45,7 | 41,5 | +6,2 | 3,1 | 1,7 |
| 18 | Nexus (25–27/9) | 47,2 | 41,6 | +7,6 | 3,8 | 3,4 |
| 19 | CNT/MDA (29/9–2/10) | 47,7 | 42,1 | +7,6 | 3,8 | 1,7 |
| 20 | Indexa (27–29/9)\* | 53,4 | 46,6 | +8,8 | 4,4 | – |

\* Nas linhas de Ideia e Indexa, Lula e Flávio somam exatamente 100%. Isso indica que o dado registrado é a divisão
entre os dois, e não o 1º turno com todos os candidatos. A margem é comparável. O MAE dos níveis não é, porque
infla os dois primeiros. **[calc]**

Leitura:

- **Melhor no conjunto: visão calibrada do modelo principal.** Ficou em 3º na margem e em 1º no MAE dos dois
  primeiros e no MAE de todos os candidatos. Gerp e Vox Brasil ficaram logo atrás e foram os institutos mais
  equilibrados nas duas métricas. A Futura acertou a margem quase exatamente, mas subestimou o nível de Lula e o
  de Flávio em cerca de 2,4 p.p. cada, porque superestimou os candidatos menores.
- **A maioria das pesquisas superestimou a margem de Lula.** 11 dos 14 institutos erraram nessa direção, e a média
  sem ajustes errou em +3,4 p.p. Lula veio quase igual à média (45,1 x 45,3). Quem ficou abaixo da média foi Flávio,
  e a diferença saiu dos menores. **[calc]**
- **A premissa sobre o viés decidiu o ranking entre as visões.** A calibrada aplicou uma correção de +1,5 p.p.
  encolhida, estimada em 2014, 2018 e 2022, e ficou a −0,5 p.p. da margem real. A neutra, sem correção, errou +2,8.
  A pleno, com o erro histórico inteiro, errou −2,8. O mesmo vale para o modelo alternativo (histórico −2,3; neutro
  +3,3). Isso é **uma única realização**. Ela não prova que a correção será adequada na próxima eleição, e um
  modelo bem calibrado erra fora do intervalo de 80% em 1 de cada 5 eleições.
- **Os institutos foram avaliados com uma única pesquisa e uma única eleição.** Isso diz pouco sobre a qualidade
  metodológica de cada um. Pesquisas com campo encerrado mais cedo (Nexus, Ideia, Indexa, de 25 a 29/9) também
  podem ter perdido movimentos da última semana.

### 2.2 Eventos probabilísticos (modelos e mercados)

Os mercados não publicam percentuais de voto, então são avaliados pelos eventos. Brier = (p − ocorreu)², em que
menor é melhor.

| Previsor | P(Lula em 1º) | Brier | P(decidida no 1º turno) | Brier |
|---|---|---|---|---|
| Modelo principal: viés pleno | 23,6% | **0,056** | 32,9% | 0,108 |
| Modelo alternativo: histórico | 27,4% | 0,075 | 39,8% | 0,158 |
| Modelo principal: calibrado | 34,5% | 0,119 | 21,4% | 0,046 |
| Modelo principal: neutro | 56,5% | 0,320 | 16,4% | 0,027 |
| Modelo alternativo: neutro | 58,0% | 0,336 | 36,4% | 0,133 |
| Polymarket | 71,4% | 0,510 | 5,3% | **0,003** |
| Kalshi | 72,0% | 0,518 | 4,6% | **0,002** |

Na véspera, os mercados de faixa de margem davam 28% (Kalshi) e 30% (Polymarket) para "Flávio à frente por 0–5
p.p.", que foi o resultado, e 54–55% para "Lula à frente por 0–5 p.p." (`mercado_ao_vivo.csv`, último registro
antes das 17h). **[calc]**

Leitura: os mercados ficaram perto da leitura literal das pesquisas e erraram o 1º colocado com 71–72% de
confiança. Acertaram melhor que todos os modelos a improbabilidade de decisão no 1º turno, em que os modelos tinham
caudas largas (16–40%) escolhidas no backtest para cobrir erros como o de 2014. Os mercados funcionam como um sinal
só, porque são arbitrados entre si.

## 3. Onde os modelos erraram e onde acertaram

### 3.1 Erros

**Polarização regional subestimada.** Erro na margem por região na previsão de véspera, ponderado pelo eleitorado
(previsto − real; negativo = margem de Lula subestimada). **[calc]**

| Visão | Nordeste | Norte | Sudeste | Centro-Oeste | Sul |
|---|---|---|---|---|---|
| Calibrada | **−4,6** | **−3,5** | +0,8 | +1,0 | **+6,0** |
| Neutra | −1,4 | −0,3 | +4,3 | +4,0 | +9,2 |
| Viés pleno | −7,0 | −6,1 | −1,5 | −1,4 | +3,7 |

- O padrão é o mesmo nas três visões: a diferença entre Sul e Nordeste fica perto de 10–11 p.p. em cada uma. Uma
  correção nacional de viés não remove isso. Os maiores erros da visão calibrada foram AP (−13,2 na margem), PI
  (−10,2), BA (−9,7), RS (+8,4), AL (−7,4), SE (−7,2) e AC (−5,8). **[calc]**
- A causa provável, documentada em `simulador/AVALIACAO_1T_LICOES.md`, é o prior estadual
  `nacional + 0,85 × lean de 2022`. Com fator menor que 1, o modelo puxa as UFs para o centro. Em 2026 o lean se
  manteve ou aumentou, e as pesquisas estaduais eram esparsas demais para corrigir. A recomendação registrada é
  um fator de ~0,95–1,0 e menos encolhimento das pesquisas estaduais, a ser validada em backtest com 2014–2026
  antes de qualquer mudança.
- Por UF, a visão calibrada indicou o vencedor certo em 25 de 27 UFs (93%). Errou AM, onde dava 45% para Lula em
  1º e Lula venceu por ~2,5 p.p., e AP, onde dava 11% para Lula e Lula ficou à frente por 225 votos. **[calc]**

**Candidatos menores superestimados, como em 2014, 2018 e 2022.** Na véspera, a média das pesquisas dava 10,9%
aos menores (Caiado 2,9, Cury 3,1, Zema 0,5, Renan 3,6, outros 0,8). Eles tiveram 7,8%. O modelo já aplicava uma
contração e previu 8,7%, mas ainda ficou 0,9 p.p. acima. **[calc]** Por candidato, na visão calibrada: Renan
+0,6, Outros +0,4 (fora do intervalo de 95%), Caiado +0,2, Zema +0,16 (fora do intervalo de 95%) e Cury −0,4 (o
único que veio acima do previsto).

### 3.2 Acertos

- **Margem nacional.** Visão calibrada: −0,5 p.p. na margem, −0,7 em Lula e −0,2 em Flávio. É bem menos que o
  erro médio de 2,8 p.p. do backtest no nacional. Os PITs ficaram perto do centro (0,58 Lula, 0,53 Flávio).
- **Cobertura dos intervalos.** No nacional, Lula e Flávio ficaram dentro do intervalo de 80% nas cinco visões
  dos dois modelos. Nas UFs, a cobertura de 80% foi de 98% na calibrada, 100% na neutra e 96% na pleno. Ou seja,
  os intervalos estaduais estavam largos o bastante para absorver o erro regional. A ressalva é que, com 98%, eles
  podem estar um pouco largos demais.
- **Comparecimento.** A premissa de abstenção e brancos/nulos iguais a 2022 por UF errou o total nacional em
  ~0,1 p.p. de abstenção e ~0,35 p.p. de brancos+nulos. **[calc]**
- **Par do 2º turno.** Todas as visões e os mercados davam ≥98% para Lula x Flávio.

## 4. A projeção ao vivo durante a apuração

O `resultado_1t.py` leu o TSE a cada 5–10 minutos. Ele completava as UFs parciais com o swing por município sobre
2022 e recalculava a projeção do 2º turno. Trajetória reconstruída do histórico de commits de
`simulador/data/avaliacao_1t.json` e `simulador/web/resultados_2t.json`. **[calc]**

| Hora da leitura | % apurado (TSE) | Margem parcial do TSE | Margem projetada | P(Lula vence 2º turno) | Observação |
|---|---|---|---|---|---|
| 17:24 | 1,2 | −6,4 | −5,1 | 7% | 18 UFs no método antigo, 3 com a previsão de véspera |
| 17:42 | 4,6 | −9,0 | −5,6 | 7% | 5 UFs no método antigo |
| 17:51 | 7,6 | −9,7 | −3,7 | 12% | 12 UFs no método antigo, ES com a previsão (timeout TLS) |
| 18:07 | 12,5 | −10,4 | −5,6 | 7% | 7 UFs no método antigo, AP com a previsão |
| 18:21 | 19,5 | −10,5 | −6,1 | 7% | 13 UFs no método antigo |
| *18:20* | | | | | *Correção publicada (commit 820c665)* |
| 18:25 | 22,0 | −10,3 | −3,2 | 11% | 28 UFs pelo método municipal |
| 18:39 | 31,9 | −9,6 | −2,8 | 12% | |
| 18:47 | 36,6 | −9,4 | −2,2 | 17% | SP e exterior com a previsão de véspera (HTTP 429) |
| 18:50 | 41,6 | −9,0 | −2,8 | 12% | |
| 18:56–19:13 | 47,3 (parado) | −8,6 | −2,7 a −2,5 | 12–13% | Arquivo nacional parado |
| 19:21–20:04 | 64,8 (parado) | −7,3 | −2,4 a −2,2 | 13% | Arquivo nacional parado (~45 min) |
| 20:11 | 85,0 | −5,0 | −2,2 | 13% | |
| 20:45 | 92,8 | −3,6 | −2,1 | 14% | |
| 21:05 | 98,6 | −2,4 | −2,0 | 14,5% | |

**Desempenho.** Desde a primeira leitura, com 1,2% apurado, a projeção mostrava Flávio à frente e o 2º turno
favorável a ele. A margem parcial do TSE chegou a −10,5 p.p. com 20% apurado. A projeção ficou sempre mais perto
do resultado final (−2,0) que o parcial bruto. Até a correção, porém, ela **oscilou entre −3,2 e −6,1**, com erro
médio absoluto de 2,7 p.p. contra o número final. **[calc]** Depois da correção, ficou estável e convergiu de
forma monotônica: −3,2 com 22%, −2,8 com 32–42%, −2,2 com 65% e −2,0 com 98,6%.

**Viés residual.** A convergência não foi aleatória. Depois da correção, a projeção subestimou Lula de forma
sistemática: ~1,3 p.p. na margem com 22–28% apurado, ~0,5–0,8 com 42–47% e ~0,2–0,4 com 65%. **[calc]** Os municípios
apurados cedo foram, mesmo depois do ajuste por porte e inclinação política, mais favoráveis a Flávio que os
restantes. O ajuste por município reduziu muito o efeito da ordem regional de totalização descrito em
`simulador/APURACAO_2022_ORDEM.md`, mas não o eliminou. Os intervalos da projeção deveriam ter um viés esperado
dependente do % apurado, e não só um erro simétrico.

**Problemas encontrados e corrigidos durante a noite:**

1. **Fallbacks do download municipal e cache defasado (corrigido às 18:20, commit 820c665).** O cache gravava a
   versão do arquivo da UF mesmo quando o arquivo do município no CDN ainda trazia um `est` menor. Esse município
   ficava defasado para sempre. Além disso, a checagem de consistência comparava **totais** de votos: os municípios
   somavam ~18% menos que a UF em MG, pela defasagem normal do CDN. Isso mandava UFs inteiras de volta ao método
   antigo, que usa as fatias parciais sem ajuste municipal. De 5 a 18 UFs por leitura caíam no método antigo, e é
   isso que explica as oscilações de 2–3 p.p. da primeira hora. A correção passou a usar o `est` de cada arquivo,
   baixar de novo os arquivos defasados, comparar taxas (válidos por eleitor totalizado) em vez de totais, fazer 3
   tentativas por arquivo (timeouts de TLS) e contar como não apurados os municípios sem arquivo (até 10% do
   eleitorado totalizado da UF). Depois disso, as 28 UFs ficaram no método municipal em todas as leituras.
2. **SP com a previsão de véspera em uma leitura (18:47).** O TSE respondeu HTTP 429 (excesso de requisições) para
   os arquivos de SP e do exterior. Essas duas unidades entraram com a previsão de véspera em vez da apuração. A
   margem projetada pulou de −2,8 para −2,2 e a probabilidade de Lula no 2º turno de 12% para 17%, e as duas
   voltaram na leitura seguinte. Uma UF desse tamanho não deveria cair para a previsão de véspera quando havia um
   arquivo de poucos minutos antes no cache. Isso ficou como melhoria pendente, sem mudança nesta noite.
3. **Arquivo nacional do TSE parado.** O arquivo `br` ficou com o mesmo carimbo de horário (18:48:59, 47,3%) em
   três leituras e depois (19:14:08, 64,8%) por ~45 minutos, entre 19:21 e 20:04. Nesse período os arquivos por UF e
   por município continuaram mudando, e a projeção também (−2,4 para −2,2). Só o "% apurado" e o parcial nacional
   exibidos ficaram defasados. Às 20:11 o arquivo saltou para 85,0%. Não sabemos se o atraso foi do TSE ou do CDN.
4. **Sem efeito no resultado publicado da véspera.** Nenhuma correção alterou `web/resultados.json` nem o motor do
   modelo. As mudanças afetaram só a projeção ao vivo e o 2º turno condicionado.

## 5. Reação dos mercados durante a apuração

`simulador/data/mercado_ao_vivo.csv`, com registros a cada ~2 minutos entre 14:38 de 4/10 e 21:08. "Normalizado" =
preço dividido pela soma dos preços do evento. **[calc]**

| Hora | % apurado | Polymarket: Lula vence a eleição | Kalshi: Lula vence | Polymarket: Lula em 1º no 1º turno | Polymarket: decidida no 1º turno |
|---|---|---|---|---|---|
| 16:58 (antes das 17h) | – | 35,6% | 34,9% | 66% | 6% |
| 17:32 | 2,4 | 31% | 28% | 54% (17:38) | 3% |
| 17:48 | 7,6 | 21% | 20% | 24% (17:52) | 9% |
| 18:04 | 12,5 | 15% | 15% | 11% | 13% (18:00) |
| 18:36 | 32 | 13–15% | 15% | 10% | 3% |
| 19:31 | 65 | 14% | 17% | <1% | <1% |
| 21:05 | 98,6 | 14,4% | 16,8% | <1% | <1% |

- **Os mercados reagiram rápido.** Em 1h, entre 2% e 12% apurado, a chance de Lula vencer a eleição caiu de ~35%
  para ~15%, e a de Lula terminar em 1º caiu de 66% para 11%. A queda veio antes de o parcial nacional dar
  informação forte por si só, porque Flávio à frente por ~10 p.p. com 10–20% apurado era esperado nas duas visões
  do modelo (`APURACAO_2022_ORDEM.md`). Ela coincidiu com o que a projeção por município mostrava (7–12%).
- **A probabilidade de decisão no 1º turno subiu brevemente** para 9–13% entre 17:48 e 18:12, quando o parcial
  nacional de Flávio estava em ~51% dos válidos. Depois caiu para menos de 1%.
- **A situação no fim da noite está alinhada:** 14–17% para Lula nos mercados e 14,5% no modelo. Antes da
  apuração, os mercados (35–36%) e a visão calibrada do modelo (35,9%) também estavam próximos.
- O mercado de faixa de margem fechou com ~95–98% em "Flávio à frente por 0–5 p.p.".

## 6. Projeção do 2º turno (25/10)

Fonte: `simulador/web/resultados_2t.json`, gerado às 21:04 de 4/10 com 98,64% apurado e 500 mil simulações, com
transferência de votos regionalizada pelo lean da UF.

| | Lula | Flávio |
|---|---|---|
| **Probabilidade de vitória** | **14,5%** | **85,5%** |
| Votos válidos, média | 47,2% | 52,8% |
| Intervalo de 80% (Lula) | 43,8 – 50,7 | |
| Intervalo de 95% (Lula) | 41,4 – 53,1 | |
| Margem mediana (Lula − Flávio) | −5,6 p.p. (80%: −12,4 a +1,3) | |

**Como o centro é formado:**

1. **Transferência dos votos dos eliminados.** A matriz vem da Quaest (Caiado e Renan: 2–3/10; Cury e Zema:
   24–27/9). Do eleitor de cada candidato, a fração que vai para Lula / Flávio / branco, nulo ou abstenção é:
   Caiado 19/43/38, Cury 28/35/37, Renan 11/60/29, Zema 10/80/10. Entre os votos dos menores que permanecem
   válidos, ~30% vão para Lula **[calc]**. O resultado é Lula 47,9%.
2. **Pesquisas de 2º turno feitas antes do 1º turno** (média: Lula 49,6%), com peso de 25%. O peso é baixo porque
   em 2018 e 2022 essas pesquisas superestimaram o PT em 3,5 e 4,7 p.p. Resultado: 48,4%.
3. **Correção de viés histórico** de −1,1 p.p. Esse método errou +2,7, −0,3 e +2,8 p.p. em 2014, 2018 e 2022, e o
   erro médio foi encolhido para zero. Centro final: **47,2%**.

**Sensibilidade.**

- Com a matriz nacional única, sem regionalizar, Lula tem 14,2%.
- Sem a correção de viés do passo 3, o centro seria 48,4% e a chance de Lula subiria para cerca de 27%
  (aproximação normal com o mesmo desvio, **[calc]**).
- Em um cenário só com os eliminados, para Lula chegar a 50% dos válidos sem mudar a abstenção, ele precisaria de
  ~62% dos votos que os menores tiveram no 1º turno (4,9 de 7,8 p.p.). A matriz da Quaest dá ~20%. **[calc]**
- O backtest do pipeline do 2º turno (LOEO) teve erro nacional de +2,0, −1,6 e +2,2 p.p. em 2014, 2018 e 2022.

**UFs mais disputadas no 2º turno:** AM, com Lula a 50,0% e chance de 50%; PA, 51,2% e 65%; AP, 48,3% e 30%; MG,
45,6% e 9%; TO, 45,0% e 7%. SP fica em 40,7% e 1%. A projeção de MG vem do 1º turno real (43,0 x 48,5) mais a
transferência.

**O que pode mudar a projeção.** A lista é neutra. Cada fator pode mover o resultado para os dois lados.

| Fator | Poderia favorecer Lula se… | Poderia favorecer Flávio se… |
|---|---|---|
| Eleitores de Caiado, Cury, Renan e Zema (7,8% dos válidos) | dividirem-se de modo mais equilibrado que a matriz da Quaest, que vem de subamostras pequenas; o voto de Cury e "outros" é o menos definido | seguirem a matriz ou se concentrarem ainda mais em Flávio, como sugere a regionalização (estados antipetistas transferem mais para ele) |
| Comparecimento | a queda da abstenção no Nordeste e no Norte se repetir ou aumentar | a abstenção voltar a subir no Nordeste ou cair no Sul e no Sudeste |
| Pesquisas pós-1º turno (primeiras nesta semana) | mostrarem Lula acima de 47–48%, o que reduziria a correção histórica | confirmarem a vantagem de Flávio. Na véspera do 2º turno, o erro histórico das pesquisas foi pequeno (+0,7, −1,1 e +0,1 p.p.) |
| Brancos e nulos | eleitores dos menores que hoje dizem que anulariam votarem em Lula | esses eleitores votarem em Flávio ou se absterem menos que o previsto |
| Campanha e fatos até 25/10 | debates, apoios e fatos da campanha | debates, apoios e fatos da campanha |
| Fatos fora do modelo | reajuste do Bolsa Família pago em 19/10, decisão do STF sobre as bets, caso Master/STF: o efeito de cada um é incerto em direção e tamanho | idem |
| Erro do próprio modelo | o viés histórico (3 eleições) não se repetir | o viés de 2014/2022 se repetir sem encolhimento |

Os apoios dos candidatos eliminados não estão listados porque não há posição pública verificada no momento em que
este texto foi escrito.

## 7. Limitações

- **A apuração não está completa.** O texto usa 98,64–98,76% das seções. Faltam sobretudo BA, AL, CE e o exterior.
  A projeção completa essas UFs, e a margem deve mudar no máximo alguns décimos, mais provavelmente a favor de
  Lula, já que as seções que faltam são do Nordeste.
- **Uma eleição é uma única realização.** O ranking de previsores, a vantagem da visão calibrada e a cobertura dos
  intervalos valem para 2026 e não demonstram, sozinhos, superioridade de método.
- **Dados de pesquisas.** A conversão para votos válidos exclui brancos, nulos e indecisos de forma proporcional,
  o que pode penalizar institutos que publicam em votos totais. As linhas de Ideia e Indexa parecem registrar só a
  divisão entre os dois primeiros (ver §2.1). As datas de campo variam de 25/9 a 3/10.
- **Mercados.** Polymarket e Kalshi são arbitradas entre si e equivalem a um sinal só. A Polymarket é proibida no
  Brasil, e o volume não garante calibração.
- **Projeção ao vivo.** As métricas da §4 comparam com o número de 98,6%, não com o final. O viés residual da
  projeção ainda não foi incorporado aos intervalos.
- **2º turno.** O modelo tem 3 eleições de calibração para a transferência e trata a deriva da campanha como erro
  simétrico. A matriz de transferência vem de uma pesquisa só.
- **Comparecimento.** As taxas são das seções já totalizadas. O exterior tem abstenção estruturalmente alta e
  apuração incompleta (88,6%).

## Links

- [Painel do simulador](https://claude.ai/artifact/2jH33uw8DKd8w5vbCEkwB6): 2º turno condicionado, mapa, mercados
  ao vivo
- [Comparador de propostas](https://claude.ai/artifact/Qmc7jGPBiikX9SgsBdghEC)
- [Resumo executivo](Resumo%20executivo%20elei%C3%A7%C3%A3o%202026.md)
- Avaliação automática completa: `simulador/AVALIACAO_1T.md`. Lições para o modelo:
  `simulador/AVALIACAO_1T_LICOES.md`. Backtest: `simulador/BACKTEST.md`.
