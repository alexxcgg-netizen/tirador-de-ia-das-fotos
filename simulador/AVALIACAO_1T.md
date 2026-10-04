# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 20:59 UTC. Seções totalizadas no Brasil: 10,92% (TSE, 04/10/2026 17:57:12). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,40 | 47,61 | 2,24 | 2,91 | 0,33 | 2,27 | 0,24 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,7 | 45,2 | -2,4 | 4,1 | 2,0 | 0,28 | 0,78 | sim/sim | 0,83/1,08 |
| Modelo principal: calibrado | 44,4 | 0,0 | 46,8 | -0,8 | 0,8 | 0,4 | 0,50 | 0,59 | sim/sim | 0,64/0,76 |
| Modelo principal: viés pleno | 43,3 | -1,1 | 48,1 | 0,5 | -1,6 | 0,8 | 0,62 | 0,44 | sim/sim | 0,84/0,77 |
| Modelo alternativo: neutro | 46,6 | 2,2 | 45,3 | -2,4 | 4,5 | 2,3 | 0,27 | 0,71 | sim/sim | 1,29/1,28 |
| Modelo alternativo: historico | 43,8 | -0,6 | 48,1 | 0,4 | -1,1 | 0,5 | 0,55 | 0,44 | sim/sim | 1,01/1,08 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,9 | 43,8 | -3,8 | 4,7 | 2,3 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,8 | 41,6 | -6,0 | 8,8 | 4,4 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,2 | 49,4 | 1,7 | 4,5 | 4,0 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,0 | 46,6 | -1,0 | 10,0 | 5,0 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,3 | 41,5 | -6,1 | 7,5 | 3,7 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,6 | 45,9 | -1,7 | 2,3 | 1,2 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,3 | 42,1 | -5,5 | 8,9 | 4,4 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,3 | 43,6 | -4,0 | 4,3 | 2,1 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,5 | 40,5 | -7,1 | 6,6 | 3,8 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,3 | 46,2 | -1,4 | 1,1 | 0,8 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,5 | 44,1 | -3,6 | 6,1 | 3,0 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,0 | 47,5 | -0,1 | -0,8 | 0,6 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,6 | 43,7 | -3,9 | 5,5 | 2,8 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,2 | 43,5 | -4,1 | 5,4 | 2,7 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,8 | 44,7 | -2,9 | 1,1 | 2,3 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) -0,8; Gerp (30/09–02/10) 1,1; Futura (02/10–03/10) 1,1; Vox Brasil (29/09–01/10) 2,3; PoderData (30/09–02/10) 4,3; Ideia (25/09–28/09) 4,5; Datafolha (03/10–03/10) 5,4; Quaest (02/10–03/10) 5,5; AtlasIntel (27/09–02/10) 6,1; IFP (29/09–02/10) 6,6; Real Time Big Data (26/09–30/09) 7,5; Nexus (25/09–27/09) 8,8; CNT/MDA (29/09–02/10) 8,9; Indexa (27/09–29/09) 10,0.

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
| Modelo principal: neutro | 27 | 2,6 | 0,3 | 3,0 | -1,1 | 94% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 2,7 | -1,3 | 2,8 | 0,5 | 96% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 3,2 | -2,4 | 3,0 | 1,8 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 30,5 | 63,2 | parcial |
| AL | 54,2 | 40,9 | parcial |
| AM | 50,6 | 42,7 | parcial |
| AP | 52,4 | 39,8 | parcial |
| BA | 65,3 | 29,4 | parcial |
| CE | 61,6 | 32,7 | parcial |
| DF | 38,3 | 51,1 | parcial |
| ES | 36,6 | 55,8 | parcial |
| GO | 29,6 | 56,4 | parcial |
| MA | 67,2 | 28,1 | parcial |
| MG | 41,6 | 48,8 | parcial |
| MS | 32,7 | 59,9 | parcial |
| MT | 31,4 | 63,3 | parcial |
| PA | 52,1 | 42,5 | parcial |
| PB | 60,4 | 33,7 | parcial |
| PE | 63,8 | 30,9 | parcial |
| PI | 67,7 | 26,9 | parcial |
| PR | 31,0 | 59,7 | parcial |
| RJ | 37,5 | 55,0 | parcial |
| RN | 59,6 | 34,9 | parcial |
| RO | 26,9 | 66,7 | parcial |
| RR | 24,5 | 70,6 | parcial |
| RS | 34,8 | 56,4 | parcial |
| SC | 23,9 | 68,1 | parcial |
| SE | 61,4 | 32,2 | parcial |
| SP | 36,9 | 52,9 | parcial |
| TO | 43,7 | 50,1 | parcial |
| ZZ | 52,5 | 37,9 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
