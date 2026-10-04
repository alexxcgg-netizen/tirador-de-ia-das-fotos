# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 21:21 UTC. Seções totalizadas no Brasil: 19,54% (TSE, 04/10/2026 18:16:13). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 43,09 | 49,18 | 2,19 | 2,84 | 0,30 | 2,19 | 0,22 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 3,0 | 45,2 | -4,0 | 7,0 | 3,5 | 0,17 | 0,90 | sim/não | 1,32/1,76 |
| Modelo principal: calibrado | 44,4 | 1,3 | 46,8 | -2,3 | 3,7 | 1,8 | 0,34 | 0,76 | sim/sim | 0,83/1,04 |
| Modelo principal: viés pleno | 43,3 | 0,2 | 48,1 | -1,1 | 1,3 | 0,6 | 0,48 | 0,61 | sim/sim | 0,72/0,85 |
| Modelo alternativo: neutro | 46,6 | 3,5 | 45,3 | -3,9 | 7,4 | 3,7 | 0,21 | 0,80 | sim/sim | 1,78/1,83 |
| Modelo alternativo: historico | 43,8 | 0,7 | 48,1 | -1,1 | 1,8 | 0,9 | 0,42 | 0,58 | sim/sim | 1,07/1,10 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 2,2 | 43,8 | -5,4 | 7,5 | 3,8 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 4,1 | 41,6 | -7,6 | 11,7 | 5,9 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 7,5 | 49,4 | 0,2 | 7,4 | 3,9 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 10,3 | 46,6 | -2,6 | 12,9 | 6,5 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 2,6 | 41,5 | -7,7 | 10,3 | 5,2 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | 1,9 | 45,9 | -3,3 | 5,2 | 2,6 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 4,6 | 42,1 | -7,1 | 11,7 | 5,9 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | 1,6 | 43,6 | -5,6 | 7,1 | 3,6 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | 0,8 | 40,5 | -8,7 | 9,5 | 4,7 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | 1,0 | 46,2 | -2,9 | 3,9 | 2,0 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 3,9 | 44,1 | -5,1 | 9,0 | 4,5 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | 0,3 | 47,5 | -1,7 | 2,0 | 1,0 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 2,9 | 43,7 | -5,5 | 8,4 | 4,2 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 2,6 | 43,5 | -5,7 | 8,3 | 4,1 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -0,5 | 44,7 | -4,4 | 4,0 | 2,5 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Palver (30/09–03/10) 2,0; Gerp (30/09–02/10) 3,9; Futura (02/10–03/10) 4,0; Vox Brasil (29/09–01/10) 5,2; PoderData (30/09–02/10) 7,1; Ideia (25/09–28/09) 7,4; Datafolha (03/10–03/10) 8,3; Quaest (02/10–03/10) 8,4; AtlasIntel (27/09–02/10) 9,0; IFP (29/09–02/10) 9,5; Real Time Big Data (26/09–30/09) 10,3; Nexus (25/09–27/09) 11,7; CNT/MDA (29/09–02/10) 11,7; Indexa (27/09–29/09) 12,9.

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
| Modelo principal: neutro | 27 | 2,8 | 1,0 | 3,5 | -1,7 | 87% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 2,6 | -0,6 | 3,2 | -0,1 | 94% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 3,1 | -1,7 | 3,3 | 1,2 | 93% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 30,4 | 63,0 | parcial |
| AL | 56,6 | 38,9 | parcial |
| AM | 49,8 | 43,5 | parcial |
| AP | 49,4 | 42,5 | parcial |
| BA | 64,8 | 29,8 | parcial |
| CE | 61,2 | 32,9 | parcial |
| DF | 38,2 | 51,2 | parcial |
| ES | 36,2 | 56,2 | parcial |
| GO | 28,3 | 56,9 | parcial |
| MA | 60,4 | 34,1 | parcial |
| MG | 41,8 | 49,1 | parcial |
| MS | 32,7 | 60,1 | parcial |
| MT | 29,4 | 65,1 | parcial |
| PA | 49,4 | 44,9 | parcial |
| PB | 60,6 | 33,6 | parcial |
| PE | 63,1 | 31,3 | parcial |
| PI | 67,4 | 27,1 | parcial |
| PR | 30,7 | 60,2 | parcial |
| RJ | 38,7 | 53,8 | parcial |
| RN | 60,6 | 33,9 | parcial |
| RO | 26,3 | 67,2 | parcial |
| RR | 26,8 | 67,0 | parcial |
| RS | 33,8 | 57,6 | parcial |
| SC | 24,4 | 67,5 | parcial |
| SE | 61,1 | 32,4 | parcial |
| SP | 32,8 | 58,3 | parcial |
| TO | 43,2 | 50,6 | parcial |
| ZZ | 52,3 | 38,1 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
