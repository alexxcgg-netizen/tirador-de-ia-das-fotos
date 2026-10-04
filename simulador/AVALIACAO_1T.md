# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 20:51 UTC. Seções totalizadas no Brasil: 7,59% (TSE, 04/10/2026 17:48:38). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,04 | 47,74 | 2,31 | 3,00 | 0,34 | 2,32 | 0,25 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 2,0 | 45,2 | -2,6 | 4,6 | 2,3 | 0,24 | 0,79 | sim/sim | 0,91/1,14 |
| Modelo principal: calibrado | 44,4 | 0,4 | 46,8 | -0,9 | 1,3 | 0,6 | 0,46 | 0,60 | sim/sim | 0,69/0,78 |
| Modelo principal: viés pleno | 43,3 | -0,7 | 48,1 | 0,4 | -1,1 | 0,5 | 0,58 | 0,46 | sim/sim | 0,79/0,76 |
| Modelo alternativo: neutro | 46,6 | 2,5 | 45,3 | -2,5 | 5,0 | 2,5 | 0,25 | 0,72 | sim/sim | 1,38/1,30 |
| Modelo alternativo: historico | 43,8 | -0,3 | 48,1 | 0,3 | -0,6 | 0,3 | 0,51 | 0,45 | sim/sim | 0,96/1,06 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 1,2 | 43,8 | -3,9 | 5,1 | 2,6 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 3,2 | 41,6 | -6,2 | 9,3 | 4,7 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,6 | 49,4 | 1,6 | 5,0 | 4,1 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,4 | 46,6 | -1,2 | 10,5 | 5,3 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,7 | 41,5 | -6,2 | 7,9 | 4,0 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 1,0 | 45,9 | -1,9 | 2,8 | 1,4 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,7 | 42,1 | -5,7 | 9,3 | 4,7 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,6 | 43,6 | -4,1 | 4,8 | 2,4 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,1 | 40,5 | -7,2 | 7,1 | 3,7 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | 0,1 | 46,2 | -1,5 | 1,5 | 0,8 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,9 | 44,1 | -3,7 | 6,6 | 3,3 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -0,6 | 47,5 | -0,3 | -0,3 | 0,4 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,9 | 43,7 | -4,1 | 6,0 | 3,0 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,6 | 43,5 | -4,3 | 5,9 | 2,9 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,4 | 44,7 | -3,0 | 1,6 | 2,2 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) -0,3; Gerp (30/09–02/10) 1,5; Futura (02/10–03/10) 1,6; Vox Brasil (29/09–01/10) 2,8; PoderData (30/09–02/10) 4,8; Ideia (25/09–28/09) 5,0; Datafolha (03/10–03/10) 5,9; Quaest (02/10–03/10) 6,0; AtlasIntel (27/09–02/10) 6,6; IFP (29/09–02/10) 7,1; Real Time Big Data (26/09–30/09) 7,9; Nexus (25/09–27/09) 9,3; CNT/MDA (29/09–02/10) 9,3; Indexa (27/09–29/09) 10,5.

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
| Modelo principal: neutro | 27 | 2,7 | 0,1 | 3,2 | -0,7 | 93% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 2,8 | -1,5 | 2,9 | 0,9 | 93% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 3,4 | -2,6 | 3,2 | 2,2 | 91% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 31,1 | 62,6 | parcial |
| AL | 54,5 | 40,6 | parcial |
| AM | 50,6 | 42,9 | parcial |
| AP | 55,0 | 37,7 | parcial |
| BA | 64,0 | 29,9 | parcial |
| CE | 61,3 | 32,9 | parcial |
| DF | 38,4 | 51,0 | parcial |
| ES | 37,5 | 53,6 | previsão |
| GO | 29,9 | 56,4 | parcial |
| MA | 67,5 | 28,1 | parcial |
| MG | 41,9 | 48,3 | parcial |
| MS | 33,5 | 59,0 | parcial |
| MT | 30,3 | 63,3 | parcial |
| PA | 47,9 | 45,0 | parcial |
| PB | 61,0 | 33,2 | parcial |
| PE | 62,0 | 32,4 | parcial |
| PI | 67,8 | 26,9 | parcial |
| PR | 31,1 | 59,4 | parcial |
| RJ | 38,2 | 54,4 | parcial |
| RN | 59,0 | 35,4 | parcial |
| RO | 27,5 | 66,2 | parcial |
| RR | 24,3 | 70,8 | parcial |
| RS | 31,9 | 59,7 | parcial |
| SC | 33,0 | 57,6 | parcial |
| SE | 61,9 | 31,9 | parcial |
| SP | 36,1 | 53,6 | parcial |
| TO | 44,1 | 49,7 | parcial |
| ZZ | 52,6 | 37,8 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
