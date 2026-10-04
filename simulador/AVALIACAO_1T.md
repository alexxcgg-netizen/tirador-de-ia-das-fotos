# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 20:23 UTC. Seções totalizadas no Brasil: 1,23% (TSE, 04/10/2026 17:21:47). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 43,85 | 48,91 | 2,36 | 2,45 | 0,32 | 1,91 | 0,21 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 2,2 | 45,2 | -3,7 | 5,9 | 3,0 | 0,23 | 0,88 | sim/sim | 0,99/1,64 |
| Modelo principal: calibrado | 44,4 | 0,6 | 46,8 | -2,1 | 2,6 | 1,3 | 0,43 | 0,74 | sim/sim | 0,72/0,95 |
| Modelo principal: viés pleno | 43,3 | -0,5 | 48,1 | -0,8 | 0,3 | 0,7 | 0,56 | 0,58 | sim/sim | 0,76/0,81 |
| Modelo alternativo: neutro | 46,6 | 2,7 | 45,3 | -3,7 | 6,4 | 3,2 | 0,24 | 0,79 | sim/sim | 1,46/1,71 |
| Modelo alternativo: historico | 43,8 | -0,1 | 48,1 | -0,8 | 0,8 | 0,5 | 0,49 | 0,56 | sim/sim | 0,96/1,06 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 1,4 | 43,8 | -5,1 | 6,5 | 3,3 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 3,3 | 41,6 | -7,3 | 10,7 | 5,3 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,8 | 49,4 | 0,5 | 6,3 | 3,6 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,6 | 46,6 | -2,3 | 11,9 | 5,9 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,9 | 41,5 | -7,4 | 9,3 | 4,7 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 1,1 | 45,9 | -3,0 | 4,2 | 2,1 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,9 | 42,1 | -6,8 | 10,7 | 5,4 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,8 | 43,6 | -5,3 | 6,1 | 3,1 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | 0,0 | 40,5 | -8,4 | 8,4 | 4,2 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | 0,2 | 46,2 | -2,7 | 2,9 | 1,5 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 3,1 | 44,1 | -4,8 | 7,9 | 4,0 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -0,4 | 47,5 | -1,4 | 1,0 | 0,9 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 2,1 | 43,7 | -5,2 | 7,4 | 3,7 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,8 | 43,5 | -5,4 | 7,2 | 3,6 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,2 | 44,7 | -4,2 | 2,9 | 2,7 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) 1,0; Gerp (30/09–02/10) 2,9; Futura (02/10–03/10) 2,9; Vox Brasil (29/09–01/10) 4,2; PoderData (30/09–02/10) 6,1; Ideia (25/09–28/09) 6,3; Datafolha (03/10–03/10) 7,2; Quaest (02/10–03/10) 7,4; AtlasIntel (27/09–02/10) 7,9; IFP (29/09–02/10) 8,4; Real Time Big Data (26/09–30/09) 9,3; Nexus (25/09–27/09) 10,7; CNT/MDA (29/09–02/10) 10,7; Indexa (27/09–29/09) 11,9.

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
| Modelo principal: neutro | 27 | 5,6 | -0,9 | 5,4 | -0,3 | 76% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 5,9 | -2,5 | 5,4 | 1,3 | 72% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 6,5 | -3,6 | 5,9 | 2,6 | 68% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 30,1 | 63,6 | parcial |
| AL | 50,6 | 43,9 | previsão |
| AM | 52,3 | 41,2 | parcial |
| AP | 66,0 | 28,4 | parcial |
| BA | 60,7 | 33,2 | previsão |
| CE | 58,9 | 35,1 | parcial |
| DF | 38,5 | 51,1 | parcial |
| ES | 40,0 | 54,2 | parcial |
| GO | 26,9 | 57,0 | parcial |
| MA | 69,5 | 27,1 | parcial |
| MG | 43,0 | 49,0 | parcial |
| MS | 36,2 | 57,0 | parcial |
| MT | 35,7 | 58,7 | parcial |
| PA | 53,2 | 42,0 | parcial |
| PB | 66,6 | 28,3 | parcial |
| PE | 65,9 | 28,8 | parcial |
| PI | 73,7 | 21,5 | parcial |
| PR | 30,3 | 58,5 | parcial |
| RJ | 19,7 | 75,4 | parcial |
| RN | 64,7 | 30,9 | parcial |
| RO | 30,2 | 63,9 | parcial |
| RR | 34,3 | 60,7 | parcial |
| RS | 27,0 | 65,0 | parcial |
| SC | 35,8 | 55,5 | parcial |
| SE | 59,7 | 34,8 | previsão |
| SP | 35,8 | 57,0 | parcial |
| TO | 43,5 | 50,0 | parcial |
| ZZ | 52,8 | 37,6 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
