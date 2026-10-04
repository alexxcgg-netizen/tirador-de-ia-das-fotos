# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 20:42 UTC. Seções totalizadas no Brasil: 4,58% (TSE, 04/10/2026 17:39:37). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 43,59 | 49,18 | 2,14 | 2,57 | 0,30 | 2,01 | 0,21 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 2,5 | 45,2 | -4,0 | 6,5 | 3,2 | 0,21 | 0,90 | sim/não | 1,11/1,77 |
| Modelo principal: calibrado | 44,4 | 0,8 | 46,8 | -2,4 | 3,2 | 1,6 | 0,40 | 0,76 | sim/sim | 0,76/1,04 |
| Modelo principal: viés pleno | 43,3 | -0,3 | 48,1 | -1,1 | 0,8 | 0,7 | 0,53 | 0,61 | sim/sim | 0,73/0,85 |
| Modelo alternativo: neutro | 46,6 | 3,0 | 45,3 | -3,9 | 6,9 | 3,5 | 0,23 | 0,80 | sim/sim | 1,57/1,83 |
| Modelo alternativo: historico | 43,8 | 0,2 | 48,1 | -1,1 | 1,3 | 0,7 | 0,47 | 0,58 | sim/sim | 1,00/1,10 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 1,7 | 43,8 | -5,4 | 7,0 | 3,5 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 3,6 | 41,6 | -7,6 | 11,2 | 5,6 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 7,1 | 49,4 | 0,2 | 6,9 | 3,6 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 9,8 | 46,6 | -2,6 | 12,4 | 6,2 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 2,2 | 41,5 | -7,7 | 9,8 | 4,9 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 1,4 | 45,9 | -3,3 | 4,7 | 2,4 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 4,1 | 42,1 | -7,1 | 11,2 | 5,6 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 1,1 | 43,6 | -5,6 | 6,7 | 3,3 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | 0,3 | 40,5 | -8,7 | 9,0 | 4,5 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | 0,5 | 46,2 | -2,9 | 3,4 | 1,7 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 3,4 | 44,1 | -5,1 | 8,5 | 4,2 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -0,2 | 47,5 | -1,7 | 1,6 | 0,9 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 2,4 | 43,7 | -5,5 | 7,9 | 3,9 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 2,1 | 43,5 | -5,7 | 7,8 | 3,9 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -1,0 | 44,7 | -4,4 | 3,5 | 2,7 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) 1,6; Gerp (30/09–02/10) 3,4; Futura (02/10–03/10) 3,5; Vox Brasil (29/09–01/10) 4,7; PoderData (30/09–02/10) 6,7; Ideia (25/09–28/09) 6,9; Datafolha (03/10–03/10) 7,8; Quaest (02/10–03/10) 7,9; AtlasIntel (27/09–02/10) 8,5; IFP (29/09–02/10) 9,0; Real Time Big Data (26/09–30/09) 9,8; Nexus (25/09–27/09) 11,2; CNT/MDA (29/09–02/10) 11,2; Indexa (27/09–29/09) 12,4.

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
| Modelo principal: neutro | 27 | 3,5 | 0,6 | 3,9 | -1,7 | 85% | 0,062 | 93% |
| Modelo principal: calibrado | 27 | 3,8 | -1,0 | 3,5 | -0,1 | 89% | 0,056 | 96% |
| Modelo principal: viés pleno | 27 | 4,2 | -2,1 | 3,7 | 1,2 | 87% | 0,058 | 93% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,063 | 85% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,054 | 96% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 31,2 | 62,8 | parcial |
| AL | 53,0 | 41,9 | parcial |
| AM | 41,4 | 50,6 | parcial |
| AP | 57,5 | 35,3 | parcial |
| BA | 66,5 | 28,3 | parcial |
| CE | 62,1 | 32,1 | parcial |
| DF | 38,4 | 51,0 | parcial |
| ES | 36,4 | 56,3 | parcial |
| GO | 30,8 | 55,8 | parcial |
| MA | 68,1 | 27,5 | parcial |
| MG | 45,1 | 46,9 | parcial |
| MS | 35,5 | 57,9 | parcial |
| MT | 32,1 | 62,5 | parcial |
| PA | 53,0 | 41,8 | parcial |
| PB | 61,2 | 33,1 | parcial |
| PE | 64,6 | 29,6 | parcial |
| PI | 67,4 | 27,5 | parcial |
| PR | 31,5 | 60,0 | parcial |
| RJ | 34,8 | 57,6 | parcial |
| RN | 58,5 | 36,0 | parcial |
| RO | 28,4 | 65,1 | parcial |
| RR | 24,7 | 70,5 | parcial |
| RS | 30,4 | 61,2 | parcial |
| SC | 23,9 | 68,3 | parcial |
| SE | 53,6 | 40,5 | parcial |
| SP | 31,9 | 59,9 | parcial |
| TO | 45,5 | 48,3 | parcial |
| ZZ | 52,6 | 37,8 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
