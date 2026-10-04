# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 21:46 UTC. Seções totalizadas no Brasil: 36,60% (TSE, 04/10/2026 18:37:14). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,82 | 47,01 | 2,35 | 2,81 | 0,33 | 2,37 | 0,32 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,3 | 45,2 | -1,8 | 3,1 | 1,5 | 0,34 | 0,73 | sim/sim | 0,78/0,87 |
| Modelo principal: calibrado | 44,4 | -0,4 | 46,8 | -0,2 | -0,2 | 0,3 | 0,55 | 0,52 | sim/sim | 0,70/0,68 |
| Modelo principal: viés pleno | 43,3 | -1,5 | 48,1 | 1,1 | -2,6 | 1,3 | 0,67 | 0,38 | sim/sim | 0,90/0,86 |
| Modelo alternativo: neutro | 46,6 | 1,7 | 45,3 | -1,8 | 3,5 | 1,8 | 0,31 | 0,65 | sim/sim | 1,24/1,20 |
| Modelo alternativo: historico | 43,8 | -1,1 | 48,1 | 1,0 | -2,1 | 1,1 | 0,59 | 0,39 | sim/sim | 1,07/1,17 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,5 | 43,8 | -3,2 | 3,6 | 1,8 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,4 | 41,6 | -5,4 | 7,8 | 3,9 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 5,8 | 49,4 | 2,3 | 3,5 | 4,1 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 8,6 | 46,6 | -0,4 | 9,0 | 4,5 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 0,9 | 41,5 | -5,5 | 6,4 | 3,2 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,2 | 45,9 | -1,1 | 1,3 | 0,7 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 2,9 | 42,1 | -4,9 | 7,8 | 3,9 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | -0,1 | 43,6 | -3,4 | 3,3 | 1,8 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,9 | 40,5 | -6,5 | 5,6 | 3,7 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,7 | 46,2 | -0,8 | 0,0 | 0,8 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,1 | 44,1 | -3,0 | 5,1 | 2,5 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,4 | 47,5 | 0,5 | -1,8 | 0,9 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,2 | 43,7 | -3,3 | 4,5 | 2,2 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 0,8 | 43,5 | -3,5 | 4,4 | 2,2 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -2,2 | 44,7 | -2,3 | 0,1 | 2,2 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Gerp (30/09–02/10) 0,0; Futura (02/10–03/10) 0,1; Vox Brasil (29/09–01/10) 1,3; Palver (30/09–03/10) -1,8; PoderData (30/09–02/10) 3,3; Ideia (25/09–28/09) 3,5; Datafolha (03/10–03/10) 4,4; Quaest (02/10–03/10) 4,5; AtlasIntel (27/09–02/10) 5,1; IFP (29/09–02/10) 5,6; Real Time Big Data (26/09–30/09) 6,4; Nexus (25/09–27/09) 7,8; CNT/MDA (29/09–02/10) 7,8; Indexa (27/09–29/09) 9,0.

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
| Modelo principal: neutro | 27 | 1,9 | 0,8 | 2,8 | -1,4 | 100% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 1,9 | -0,8 | 2,3 | 0,2 | 98% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 2,5 | -1,9 | 2,5 | 1,5 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 28,8 | 64,4 | parcial |
| AL | 54,4 | 40,8 | parcial |
| AM | 48,9 | 44,3 | parcial |
| AP | 46,4 | 45,0 | parcial |
| BA | 65,1 | 29,4 | parcial |
| CE | 61,0 | 33,2 | parcial |
| DF | 38,2 | 51,2 | parcial |
| ES | 37,1 | 55,3 | parcial |
| GO | 30,3 | 54,5 | parcial |
| MA | 63,6 | 31,3 | parcial |
| MG | 42,6 | 48,8 | parcial |
| MS | 33,9 | 59,3 | parcial |
| MT | 29,0 | 65,4 | parcial |
| PA | 49,2 | 45,1 | parcial |
| PB | 60,9 | 33,4 | parcial |
| PE | 63,0 | 31,4 | parcial |
| PI | 69,2 | 25,6 | parcial |
| PR | 31,0 | 60,1 | parcial |
| RJ | 40,2 | 52,2 | parcial |
| RN | 58,6 | 35,9 | parcial |
| RO | 25,7 | 67,6 | parcial |
| RR | 22,6 | 71,2 | parcial |
| RS | 35,8 | 55,5 | parcial |
| SC | 24,8 | 66,9 | parcial |
| SE | 62,1 | 31,3 | parcial |
| SP | 38,3 | 50,4 | previsão |
| TO | 43,1 | 50,8 | parcial |
| ZZ | 43,9 | 48,3 | previsão |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
