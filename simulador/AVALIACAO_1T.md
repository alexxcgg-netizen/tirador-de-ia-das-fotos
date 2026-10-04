# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 20:32 UTC. Seções totalizadas no Brasil: 2,39% (TSE, 04/10/2026 17:30:44). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,22 | 48,78 | 2,29 | 2,43 | 0,26 | 1,85 | 0,19 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,9 | 45,2 | -3,6 | 5,5 | 2,7 | 0,26 | 0,87 | sim/sim | 0,86/1,58 |
| Modelo principal: calibrado | 44,4 | 0,2 | 46,8 | -1,9 | 2,2 | 1,1 | 0,48 | 0,72 | sim/sim | 0,67/0,93 |
| Modelo principal: viés pleno | 43,3 | -0,9 | 48,1 | -0,7 | -0,2 | 0,8 | 0,60 | 0,57 | sim/sim | 0,82/0,79 |
| Modelo alternativo: neutro | 46,6 | 2,4 | 45,3 | -3,5 | 5,9 | 2,9 | 0,26 | 0,78 | sim/sim | 1,32/1,65 |
| Modelo alternativo: historico | 43,8 | -0,5 | 48,1 | -0,7 | 0,3 | 0,6 | 0,53 | 0,55 | sim/sim | 0,98/1,04 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 1,1 | 43,8 | -5,0 | 6,0 | 3,0 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 3,0 | 41,6 | -7,2 | 10,2 | 5,1 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,4 | 49,4 | 0,6 | 5,8 | 3,5 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,2 | 46,6 | -2,2 | 11,4 | 5,7 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,5 | 41,5 | -7,3 | 8,8 | 4,4 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,8 | 45,9 | -2,9 | 3,7 | 1,8 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,5 | 42,1 | -6,7 | 10,2 | 5,1 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,5 | 43,6 | -5,2 | 5,6 | 2,8 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,3 | 40,5 | -8,3 | 8,0 | 4,3 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,1 | 46,2 | -2,5 | 2,4 | 1,3 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,7 | 44,1 | -4,7 | 7,5 | 3,7 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -0,8 | 47,5 | -1,3 | 0,5 | 1,0 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,8 | 43,7 | -5,1 | 6,9 | 3,4 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,4 | 43,5 | -5,3 | 6,7 | 3,4 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,6 | 44,7 | -4,0 | 2,5 | 2,8 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) 0,5; Gerp (30/09–02/10) 2,4; Futura (02/10–03/10) 2,5; Vox Brasil (29/09–01/10) 3,7; PoderData (30/09–02/10) 5,6; Ideia (25/09–28/09) 5,8; Datafolha (03/10–03/10) 6,7; Quaest (02/10–03/10) 6,9; AtlasIntel (27/09–02/10) 7,5; IFP (29/09–02/10) 8,0; Real Time Big Data (26/09–30/09) 8,8; Nexus (25/09–27/09) 10,2; CNT/MDA (29/09–02/10) 10,2; Indexa (27/09–29/09) 11,4.

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
| Modelo principal: neutro | 27 | 4,2 | -1,3 | 4,3 | 0,1 | 80% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 4,8 | -2,9 | 4,4 | 1,6 | 82% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 5,5 | -4,0 | 4,9 | 2,9 | 78% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 33,0 | 62,1 | parcial |
| AL | 55,3 | 39,4 | parcial |
| AM | 50,9 | 42,5 | parcial |
| AP | 59,8 | 33,5 | parcial |
| BA | 61,9 | 31,3 | parcial |
| CE | 64,8 | 29,1 | parcial |
| DF | 38,5 | 51,1 | parcial |
| ES | 38,3 | 54,9 | parcial |
| GO | 31,7 | 55,2 | parcial |
| MA | 68,6 | 27,3 | parcial |
| MG | 45,5 | 46,9 | parcial |
| MS | 37,1 | 57,0 | parcial |
| MT | 33,8 | 60,9 | parcial |
| PA | 52,9 | 41,9 | parcial |
| PB | 64,5 | 30,1 | parcial |
| PE | 64,7 | 30,2 | parcial |
| PI | 67,4 | 27,3 | parcial |
| PR | 31,8 | 60,0 | parcial |
| RJ | 29,3 | 64,8 | parcial |
| RN | 58,7 | 35,8 | parcial |
| RO | 31,9 | 59,4 | parcial |
| RR | 41,8 | 54,7 | parcial |
| RS | 33,7 | 57,6 | parcial |
| SC | 24,1 | 68,5 | parcial |
| SE | 59,7 | 34,8 | previsão |
| SP | 34,0 | 58,6 | parcial |
| TO | 46,2 | 47,7 | parcial |
| ZZ | 52,8 | 37,6 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
