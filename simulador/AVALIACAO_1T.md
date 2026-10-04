# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 22:04 UTC. Seções totalizadas no Brasil: 47,26% (TSE, 04/10/2026 18:48:59). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,80 | 47,30 | 2,21 | 2,90 | 0,29 | 2,27 | 0,22 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,3 | 45,2 | -2,1 | 3,4 | 1,7 | 0,34 | 0,76 | sim/sim | 0,78/0,95 |
| Modelo principal: calibrado | 44,4 | -0,4 | 46,8 | -0,5 | 0,1 | 0,4 | 0,55 | 0,55 | sim/sim | 0,69/0,72 |
| Modelo principal: viés pleno | 43,3 | -1,5 | 48,1 | 0,8 | -2,3 | 1,1 | 0,66 | 0,41 | sim/sim | 0,90/0,82 |
| Modelo alternativo: neutro | 46,6 | 1,8 | 45,3 | -2,0 | 3,8 | 1,9 | 0,31 | 0,68 | sim/sim | 1,24/1,24 |
| Modelo alternativo: historico | 43,8 | -1,0 | 48,1 | 0,8 | -1,8 | 0,9 | 0,58 | 0,41 | sim/sim | 1,07/1,12 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,5 | 43,8 | -3,5 | 4,0 | 2,0 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,4 | 41,6 | -5,7 | 8,1 | 4,1 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 5,8 | 49,4 | 2,1 | 3,8 | 4,0 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 8,6 | 46,6 | -0,7 | 9,3 | 4,7 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 0,9 | 41,5 | -5,8 | 6,8 | 3,4 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,2 | 45,9 | -1,4 | 1,6 | 0,8 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 2,9 | 42,1 | -5,2 | 8,2 | 4,1 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | -0,1 | 43,6 | -3,7 | 3,6 | 1,9 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,9 | 40,5 | -6,8 | 5,9 | 3,9 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,7 | 46,2 | -1,1 | 0,4 | 0,9 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,2 | 44,1 | -3,2 | 5,4 | 2,7 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,4 | 47,5 | 0,2 | -1,5 | 0,8 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,2 | 43,7 | -3,6 | 4,8 | 2,4 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 0,9 | 43,5 | -3,8 | 4,7 | 2,3 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -2,2 | 44,7 | -2,6 | 0,4 | 2,4 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Gerp (30/09–02/10) 0,4; Futura (02/10–03/10) 0,4; Palver (30/09–03/10) -1,5; Vox Brasil (29/09–01/10) 1,6; PoderData (30/09–02/10) 3,6; Ideia (25/09–28/09) 3,8; Datafolha (03/10–03/10) 4,7; Quaest (02/10–03/10) 4,8; AtlasIntel (27/09–02/10) 5,4; IFP (29/09–02/10) 5,9; Real Time Big Data (26/09–30/09) 6,8; Nexus (25/09–27/09) 8,1; CNT/MDA (29/09–02/10) 8,2; Indexa (27/09–29/09) 9,3.

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
| Modelo principal: neutro | 27 | 1,8 | 0,7 | 2,7 | -1,4 | 98% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 1,8 | -0,9 | 2,2 | 0,2 | 98% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 2,5 | -2,0 | 2,4 | 1,5 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 28,6 | 64,6 | parcial |
| AL | 54,0 | 41,1 | parcial |
| AM | 48,4 | 44,8 | parcial |
| AP | 46,6 | 44,8 | parcial |
| BA | 65,2 | 29,3 | parcial |
| CE | 61,2 | 33,0 | parcial |
| DF | 38,2 | 51,2 | parcial |
| ES | 37,4 | 55,2 | parcial |
| GO | 30,6 | 54,2 | parcial |
| MA | 63,1 | 31,7 | parcial |
| MG | 43,0 | 48,4 | parcial |
| MS | 34,0 | 59,2 | parcial |
| MT | 29,0 | 65,3 | parcial |
| PA | 49,0 | 45,2 | parcial |
| PB | 61,1 | 33,2 | parcial |
| PE | 63,0 | 31,4 | parcial |
| PI | 69,5 | 25,3 | parcial |
| PR | 31,1 | 60,0 | parcial |
| RJ | 40,2 | 52,2 | parcial |
| RN | 59,0 | 35,4 | parcial |
| RO | 26,0 | 67,3 | parcial |
| RR | 22,7 | 71,2 | parcial |
| RS | 35,8 | 55,6 | parcial |
| SC | 24,9 | 66,8 | parcial |
| SE | 61,9 | 31,4 | parcial |
| SP | 37,9 | 52,2 | parcial |
| TO | 43,3 | 50,6 | parcial |
| ZZ | 47,9 | 42,7 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
