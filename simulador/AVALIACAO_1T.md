# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 21:25 UTC. Seções totalizadas no Brasil: 21,96% (TSE, 04/10/2026 18:19:31). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,44 | 47,67 | 2,18 | 2,89 | 0,29 | 2,30 | 0,23 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,6 | 45,2 | -2,5 | 4,1 | 2,1 | 0,29 | 0,79 | sim/sim | 0,83/1,11 |
| Modelo principal: calibrado | 44,4 | -0,0 | 46,8 | -0,8 | 0,8 | 0,4 | 0,50 | 0,60 | sim/sim | 0,64/0,77 |
| Modelo principal: viés pleno | 43,3 | -1,1 | 48,1 | 0,4 | -1,6 | 0,8 | 0,62 | 0,45 | sim/sim | 0,85/0,76 |
| Modelo alternativo: neutro | 46,6 | 2,1 | 45,3 | -2,4 | 4,5 | 2,3 | 0,28 | 0,71 | sim/sim | 1,29/1,29 |
| Modelo alternativo: historico | 43,8 | -0,7 | 48,1 | 0,4 | -1,1 | 0,5 | 0,55 | 0,44 | sim/sim | 1,01/1,07 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,8 | 43,8 | -3,9 | 4,7 | 2,3 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,8 | 41,6 | -6,1 | 8,9 | 4,4 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,2 | 49,4 | 1,7 | 4,5 | 3,9 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,0 | 46,6 | -1,1 | 10,1 | 5,0 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,3 | 41,5 | -6,2 | 7,5 | 3,7 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,6 | 45,9 | -1,8 | 2,3 | 1,2 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,3 | 42,1 | -5,6 | 8,9 | 4,4 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,2 | 43,6 | -4,1 | 4,3 | 2,1 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,5 | 40,5 | -7,2 | 6,6 | 3,9 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,3 | 46,2 | -1,4 | 1,1 | 0,9 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,5 | 44,1 | -3,6 | 6,1 | 3,1 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,0 | 47,5 | -0,2 | -0,8 | 0,6 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,5 | 43,7 | -4,0 | 5,5 | 2,8 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,2 | 43,5 | -4,2 | 5,4 | 2,7 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,8 | 44,7 | -2,9 | 1,1 | 2,4 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) -0,8; Gerp (30/09–02/10) 1,1; Futura (02/10–03/10) 1,1; Vox Brasil (29/09–01/10) 2,3; PoderData (30/09–02/10) 4,3; Ideia (25/09–28/09) 4,5; Datafolha (03/10–03/10) 5,4; Quaest (02/10–03/10) 5,5; AtlasIntel (27/09–02/10) 6,1; IFP (29/09–02/10) 6,6; Real Time Big Data (26/09–30/09) 7,5; Nexus (25/09–27/09) 8,9; CNT/MDA (29/09–02/10) 8,9; Indexa (27/09–29/09) 10,1.

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
| Modelo principal: neutro | 27 | 2,2 | 0,6 | 3,0 | -1,3 | 98% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 2,2 | -0,9 | 2,6 | 0,2 | 96% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 2,7 | -2,1 | 2,8 | 1,5 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 30,0 | 63,6 | parcial |
| AL | 55,0 | 40,2 | parcial |
| AM | 49,5 | 43,8 | parcial |
| AP | 48,3 | 43,5 | parcial |
| BA | 65,5 | 29,0 | parcial |
| CE | 61,4 | 32,8 | parcial |
| DF | 38,2 | 51,2 | parcial |
| ES | 36,5 | 55,9 | parcial |
| GO | 29,8 | 55,3 | parcial |
| MA | 65,0 | 30,0 | parcial |
| MG | 42,4 | 49,0 | parcial |
| MS | 33,3 | 59,9 | parcial |
| MT | 29,5 | 65,0 | parcial |
| PA | 49,0 | 45,3 | parcial |
| PB | 60,6 | 33,6 | parcial |
| PE | 63,3 | 31,2 | parcial |
| PI | 67,8 | 26,8 | parcial |
| PR | 30,6 | 60,5 | parcial |
| RJ | 38,3 | 54,1 | parcial |
| RN | 59,6 | 34,9 | parcial |
| RO | 25,8 | 67,5 | parcial |
| RR | 26,5 | 67,6 | parcial |
| RS | 35,5 | 55,8 | parcial |
| SC | 23,9 | 67,9 | parcial |
| SE | 61,5 | 31,9 | parcial |
| SP | 37,3 | 52,7 | parcial |
| TO | 43,0 | 50,8 | parcial |
| ZZ | 47,8 | 42,8 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
