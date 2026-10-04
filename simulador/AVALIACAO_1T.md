# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 21:07 UTC. Seções totalizadas no Brasil: 12,45% (TSE, 04/10/2026 18:00:33). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 43,34 | 48,95 | 2,19 | 2,82 | 0,31 | 2,17 | 0,23 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 2,7 | 45,2 | -3,8 | 6,5 | 3,3 | 0,19 | 0,89 | sim/sim | 1,21/1,66 |
| Modelo principal: calibrado | 44,4 | 1,1 | 46,8 | -2,1 | 3,2 | 1,6 | 0,37 | 0,74 | sim/sim | 0,80/0,95 |
| Modelo principal: viés pleno | 43,3 | -0,0 | 48,1 | -0,8 | 0,8 | 0,4 | 0,50 | 0,59 | sim/sim | 0,69/0,82 |
| Modelo alternativo: neutro | 46,6 | 3,2 | 45,3 | -3,7 | 6,9 | 3,5 | 0,22 | 0,79 | sim/sim | 1,68/1,73 |
| Modelo alternativo: historico | 43,8 | 0,4 | 48,1 | -0,9 | 1,3 | 0,7 | 0,44 | 0,56 | sim/sim | 1,03/1,07 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 1,9 | 43,8 | -5,1 | 7,1 | 3,5 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 3,9 | 41,6 | -7,4 | 11,2 | 5,6 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 7,3 | 49,4 | 0,4 | 6,9 | 3,9 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 10,1 | 46,6 | -2,4 | 12,5 | 6,2 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 2,4 | 41,5 | -7,5 | 9,9 | 4,9 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 1,7 | 45,9 | -3,1 | 4,7 | 2,4 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 4,4 | 42,1 | -6,9 | 11,3 | 5,6 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 1,3 | 43,6 | -5,3 | 6,7 | 3,3 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | 0,6 | 40,5 | -8,4 | 9,0 | 4,5 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | 0,8 | 46,2 | -2,7 | 3,5 | 1,7 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 3,6 | 44,1 | -4,9 | 8,5 | 4,3 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | 0,1 | 47,5 | -1,5 | 1,6 | 0,8 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 2,6 | 43,7 | -5,3 | 7,9 | 4,0 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 2,3 | 43,5 | -5,5 | 7,8 | 3,9 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -0,7 | 44,7 | -4,2 | 3,5 | 2,5 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) 1,6; Gerp (30/09–02/10) 3,5; Futura (02/10–03/10) 3,5; Vox Brasil (29/09–01/10) 4,7; PoderData (30/09–02/10) 6,7; Ideia (25/09–28/09) 6,9; Datafolha (03/10–03/10) 7,8; Quaest (02/10–03/10) 7,9; AtlasIntel (27/09–02/10) 8,5; IFP (29/09–02/10) 9,0; Real Time Big Data (26/09–30/09) 9,9; Nexus (25/09–27/09) 11,2; CNT/MDA (29/09–02/10) 11,3; Indexa (27/09–29/09) 12,5.

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
| Modelo principal: neutro | 27 | 2,5 | 1,0 | 3,1 | -1,7 | 94% | 0,032 | 100% |
| Modelo principal: calibrado | 27 | 2,4 | -0,6 | 2,7 | -0,1 | 96% | 0,031 | 96% |
| Modelo principal: viés pleno | 27 | 2,9 | -1,7 | 3,0 | 1,2 | 96% | 0,037 | 93% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,056 | 93% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,038 | 96% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 29,9 | 63,7 | parcial |
| AL | 53,9 | 41,3 | parcial |
| AM | 50,4 | 43,0 | parcial |
| AP | 40,2 | 53,3 | previsão |
| BA | 65,2 | 29,4 | parcial |
| CE | 61,6 | 32,5 | parcial |
| DF | 38,2 | 51,1 | parcial |
| ES | 36,1 | 56,4 | parcial |
| GO | 29,3 | 56,4 | parcial |
| MA | 66,9 | 28,4 | parcial |
| MG | 41,6 | 48,9 | parcial |
| MS | 32,7 | 60,3 | parcial |
| MT | 31,0 | 63,5 | parcial |
| PA | 47,5 | 45,5 | parcial |
| PB | 60,6 | 33,5 | parcial |
| PE | 63,6 | 31,1 | parcial |
| PI | 67,2 | 27,3 | parcial |
| PR | 30,6 | 60,6 | parcial |
| RJ | 38,5 | 54,0 | parcial |
| RN | 59,6 | 34,8 | parcial |
| RO | 29,9 | 62,1 | parcial |
| RR | 27,1 | 66,0 | parcial |
| RS | 35,1 | 56,1 | parcial |
| SC | 24,1 | 67,8 | parcial |
| SE | 60,9 | 32,7 | parcial |
| SP | 31,8 | 59,6 | parcial |
| TO | 43,3 | 50,5 | parcial |
| ZZ | 52,5 | 37,9 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
