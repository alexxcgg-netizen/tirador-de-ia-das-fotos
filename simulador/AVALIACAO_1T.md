# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 21:31 UTC. Seções totalizadas no Brasil: 27,88% (TSE, 04/10/2026 18:26:58). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,38 | 47,71 | 2,19 | 2,90 | 0,29 | 2,30 | 0,23 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,7 | 45,2 | -2,5 | 4,2 | 2,1 | 0,28 | 0,79 | sim/sim | 0,84/1,12 |
| Modelo principal: calibrado | 44,4 | 0,0 | 46,8 | -0,9 | 0,9 | 0,5 | 0,49 | 0,60 | sim/sim | 0,65/0,78 |
| Modelo principal: viés pleno | 43,3 | -1,1 | 48,1 | 0,4 | -1,5 | 0,7 | 0,62 | 0,46 | sim/sim | 0,84/0,76 |
| Modelo alternativo: neutro | 46,6 | 2,2 | 45,3 | -2,5 | 4,6 | 2,3 | 0,27 | 0,71 | sim/sim | 1,30/1,30 |
| Modelo alternativo: historico | 43,8 | -0,6 | 48,1 | 0,4 | -1,0 | 0,5 | 0,54 | 0,45 | sim/sim | 1,01/1,06 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,9 | 43,8 | -3,9 | 4,8 | 2,4 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,8 | 41,6 | -6,1 | 8,9 | 4,5 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,3 | 49,4 | 1,7 | 4,6 | 4,0 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,0 | 46,6 | -1,1 | 10,2 | 5,1 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,4 | 41,5 | -6,2 | 7,6 | 3,8 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,6 | 45,9 | -1,8 | 2,4 | 1,2 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,3 | 42,1 | -5,6 | 9,0 | 4,5 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,3 | 43,6 | -4,1 | 4,4 | 2,2 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,5 | 40,5 | -7,2 | 6,7 | 3,8 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,3 | 46,2 | -1,5 | 1,2 | 0,9 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,6 | 44,1 | -3,6 | 6,2 | 3,1 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,0 | 47,5 | -0,2 | -0,7 | 0,6 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,6 | 43,7 | -4,0 | 5,6 | 2,8 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,3 | 43,5 | -4,2 | 5,5 | 2,7 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,8 | 44,7 | -3,0 | 1,2 | 2,4 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) -0,7; Gerp (30/09–02/10) 1,2; Futura (02/10–03/10) 1,2; Vox Brasil (29/09–01/10) 2,4; PoderData (30/09–02/10) 4,4; Ideia (25/09–28/09) 4,6; Datafolha (03/10–03/10) 5,5; Quaest (02/10–03/10) 5,6; AtlasIntel (27/09–02/10) 6,2; IFP (29/09–02/10) 6,7; Real Time Big Data (26/09–30/09) 7,6; Nexus (25/09–27/09) 8,9; CNT/MDA (29/09–02/10) 9,0; Indexa (27/09–29/09) 10,2.

## Eventos (Brier e log score)

Brier = (p − ocorreu)²; log score = log da probabilidade dada ao que aconteceu (mais perto de 0 = melhor).

| Fonte | Evento | P prevista | Ocorreu | Brier | Log score |
|---|---|---|---|---|---|
| Modelo principal: neutro | Lula em 1º | 0,565 | não | 0,320 | -0,833 |
| Modelo principal: neutro | Flavio em 1º | 0,435 | sim | 0,320 | -0,833 |
| Modelo principal: neutro | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: neutro | Flavio no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: neutro | Decidida no 1º turno | 0,164 | não | 0,027 | -0,179 |
| Modelo principal: calibrado | Lula em 1º | 0,345 | não | 0,119 | -0,423 |
| Modelo principal: calibrado | Flavio em 1º | 0,655 | sim | 0,119 | -0,423 |
| Modelo principal: calibrado | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: calibrado | Flavio no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: calibrado | Decidida no 1º turno | 0,214 | não | 0,046 | -0,241 |
| Modelo principal: viés pleno | Lula em 1º | 0,236 | não | 0,056 | -0,270 |
| Modelo principal: viés pleno | Flavio em 1º | 0,764 | sim | 0,056 | -0,270 |
| Modelo principal: viés pleno | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: viés pleno | Flavio no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: viés pleno | Decidida no 1º turno | 0,329 | não | 0,108 | -0,399 |
| Modelo alternativo: neutro | Lula em 1º | 0,580 | não | 0,336 | -0,867 |
| Modelo alternativo: neutro | Flavio em 1º | 0,420 | sim | 0,336 | -0,867 |
| Modelo alternativo: neutro | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo alternativo: neutro | Flavio no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo alternativo: neutro | Decidida no 1º turno | 0,364 | não | 0,133 | -0,453 |
| Modelo alternativo: historico | Lula em 1º | 0,274 | não | 0,075 | -0,320 |
| Modelo alternativo: historico | Flavio em 1º | 0,726 | sim | 0,075 | -0,320 |
| Modelo alternativo: historico | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo alternativo: historico | Flavio no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo alternativo: historico | Decidida no 1º turno | 0,398 | não | 0,158 | -0,507 |
| Mercado: Kalshi | Lula em 1º | 0,720 | não | 0,518 | -1,273 |
| Mercado: Kalshi | Flavio em 1º | 0,280 | sim | 0,518 | -1,273 |
| Mercado: Kalshi | Decidida no 1º turno | 0,046 | não | 0,002 | -0,047 |
| Mercado: Polymarket | Lula em 1º | 0,714 | não | 0,510 | -1,252 |
| Mercado: Polymarket | Flavio em 1º | 0,286 | sim | 0,510 | -1,252 |
| Mercado: Polymarket | Flavio no 2º turno | 0,988 | sim | 0,000 | -0,012 |
| Mercado: Polymarket | Lula no 2º turno | 0,984 | sim | 0,000 | -0,016 |
| Mercado: Polymarket | Decidida no 1º turno | 0,053 | não | 0,003 | -0,054 |

## UFs

| Fonte | UFs | MAE Lula | Viés Lula | MAE Flavio | Viés Flavio | Cobertura 80% | Brier 'Lula 1º na UF' | Acerto do favorito |
|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 27 | 2,1 | 0,8 | 3,0 | -1,5 | 98% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 2,0 | -0,8 | 2,5 | 0,1 | 96% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 2,5 | -1,9 | 2,6 | 1,4 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 29,0 | 64,3 | parcial |
| AL | 54,4 | 40,8 | parcial |
| AM | 49,6 | 43,7 | parcial |
| AP | 47,6 | 44,2 | parcial |
| BA | 65,4 | 29,2 | parcial |
| CE | 60,7 | 33,3 | parcial |
| DF | 38,1 | 51,2 | parcial |
| ES | 36,7 | 55,7 | parcial |
| GO | 29,9 | 55,2 | parcial |
| MA | 64,8 | 30,2 | parcial |
| MG | 42,1 | 49,2 | parcial |
| MS | 33,3 | 59,9 | parcial |
| MT | 29,1 | 65,4 | parcial |
| PA | 48,9 | 45,4 | parcial |
| PB | 60,8 | 33,5 | parcial |
| PE | 63,4 | 31,1 | parcial |
| PI | 68,5 | 26,2 | parcial |
| PR | 30,6 | 60,6 | parcial |
| RJ | 38,5 | 53,9 | parcial |
| RN | 58,9 | 35,5 | parcial |
| RO | 25,8 | 67,5 | parcial |
| RR | 24,7 | 69,0 | parcial |
| RS | 35,6 | 55,7 | parcial |
| SC | 24,4 | 67,4 | parcial |
| SE | 61,5 | 31,8 | parcial |
| SP | 37,6 | 52,4 | parcial |
| TO | 42,8 | 51,0 | parcial |
| ZZ | 47,9 | 42,8 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
