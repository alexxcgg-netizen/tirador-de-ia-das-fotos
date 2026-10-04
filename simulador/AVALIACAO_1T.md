# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 21:50 UTC. Seções totalizadas no Brasil: 41,57% (TSE, 04/10/2026 18:43:29). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 44,65 | 47,41 | 2,20 | 2,91 | 0,29 | 2,29 | 0,23 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,4 | 45,2 | -2,2 | 3,7 | 1,8 | 0,32 | 0,77 | sim/sim | 0,80/1,00 |
| Modelo principal: calibrado | 44,4 | -0,2 | 46,8 | -0,6 | 0,4 | 0,4 | 0,53 | 0,57 | sim/sim | 0,67/0,73 |
| Modelo principal: viés pleno | 43,3 | -1,3 | 48,1 | 0,7 | -2,0 | 1,0 | 0,65 | 0,42 | sim/sim | 0,88/0,80 |
| Modelo alternativo: neutro | 46,6 | 1,9 | 45,3 | -2,2 | 4,1 | 2,0 | 0,30 | 0,69 | sim/sim | 1,26/1,26 |
| Modelo alternativo: historico | 43,8 | -0,9 | 48,1 | 0,6 | -1,5 | 0,8 | 0,57 | 0,42 | sim/sim | 1,05/1,11 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,6 | 43,8 | -3,6 | 4,2 | 2,1 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,5 | 41,6 | -5,8 | 8,4 | 4,2 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 6,0 | 49,4 | 1,9 | 4,0 | 4,0 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 8,8 | 46,6 | -0,8 | 9,6 | 4,8 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 1,1 | 41,5 | -5,9 | 7,0 | 3,5 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 0,3 | 45,9 | -1,5 | 1,9 | 0,9 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 3,1 | 42,1 | -5,3 | 8,4 | 4,2 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 0,0 | 43,6 | -3,8 | 3,8 | 1,9 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -0,8 | 40,5 | -6,9 | 6,2 | 3,8 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,6 | 46,2 | -1,2 | 0,6 | 0,9 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 2,3 | 44,1 | -3,4 | 5,7 | 2,8 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,2 | 47,5 | 0,1 | -1,3 | 0,6 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,3 | 43,7 | -3,7 | 5,1 | 2,5 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 1,0 | 43,5 | -3,9 | 4,9 | 2,5 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -2,0 | 44,7 | -2,7 | 0,7 | 2,3 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Gerp (30/09–02/10) 0,6; Futura (02/10–03/10) 0,7; Palver (30/09–03/10) -1,3; Vox Brasil (29/09–01/10) 1,9; PoderData (30/09–02/10) 3,8; Ideia (25/09–28/09) 4,0; Datafolha (03/10–03/10) 4,9; Quaest (02/10–03/10) 5,1; AtlasIntel (27/09–02/10) 5,7; IFP (29/09–02/10) 6,2; Real Time Big Data (26/09–30/09) 7,0; Nexus (25/09–27/09) 8,4; CNT/MDA (29/09–02/10) 8,4; Indexa (27/09–29/09) 9,6.

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
| Modelo principal: viés pleno | 27 | 2,5 | -1,9 | 2,4 | 1,5 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 28,7 | 64,5 | parcial |
| AL | 54,2 | 41,0 | parcial |
| AM | 48,6 | 44,6 | parcial |
| AP | 46,3 | 45,1 | parcial |
| BA | 65,3 | 29,2 | parcial |
| CE | 61,0 | 33,1 | parcial |
| DF | 38,2 | 51,2 | parcial |
| ES | 37,3 | 55,2 | parcial |
| GO | 30,5 | 54,4 | parcial |
| MA | 63,5 | 31,4 | parcial |
| MG | 42,7 | 48,8 | parcial |
| MS | 34,0 | 59,2 | parcial |
| MT | 29,0 | 65,3 | parcial |
| PA | 49,3 | 45,0 | parcial |
| PB | 61,0 | 33,3 | parcial |
| PE | 63,1 | 31,3 | parcial |
| PI | 69,3 | 25,5 | parcial |
| PR | 31,0 | 60,1 | parcial |
| RJ | 40,3 | 52,1 | parcial |
| RN | 58,7 | 35,8 | parcial |
| RO | 25,7 | 67,6 | parcial |
| RR | 22,4 | 71,3 | parcial |
| RS | 35,8 | 55,5 | parcial |
| SC | 24,7 | 66,9 | parcial |
| SE | 62,0 | 31,3 | parcial |
| SP | 37,6 | 52,3 | parcial |
| TO | 43,3 | 50,5 | parcial |
| ZZ | 47,9 | 42,7 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
