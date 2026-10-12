# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-12 17:14 UTC. Seções totalizadas no Brasil: 100,00% (TSE, 05/10/2026 02:59:31). Fonte do resultado: cache local (ensaio a seco).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 45,16 | 47,03 | 2,18 | 2,89 | 0,27 | 2,24 | 0,22 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 0,9 | 45,2 | -1,8 | 2,8 | 1,4 | 0,38 | 0,73 | sim/sim | 0,73/0,87 |
| Modelo principal: calibrado | 44,4 | -0,7 | 46,8 | -0,2 | -0,5 | 0,5 | 0,59 | 0,52 | sim/sim | 0,75/0,68 |
| Modelo principal: viés pleno | 43,3 | -1,8 | 48,1 | 1,1 | -2,9 | 1,5 | 0,70 | 0,38 | sim/sim | 0,95/0,86 |
| Modelo alternativo: neutro | 46,6 | 1,4 | 45,3 | -1,8 | 3,2 | 1,6 | 0,34 | 0,65 | sim/sim | 1,19/1,20 |
| Modelo alternativo: historico | 43,8 | -1,4 | 48,1 | 1,0 | -2,4 | 1,2 | 0,62 | 0,39 | sim/sim | 1,12/1,16 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,1 | 43,8 | -3,2 | 3,3 | 1,7 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,0 | 41,6 | -5,5 | 7,5 | 3,7 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 5,5 | 49,4 | 2,3 | 3,1 | 3,9 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 8,3 | 46,6 | -0,4 | 8,7 | 4,4 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 0,6 | 41,5 | -5,5 | 6,1 | 3,1 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | -0,2 | 45,9 | -1,1 | 1,0 | 0,7 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 2,6 | 42,1 | -4,9 | 7,5 | 3,8 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | -0,5 | 43,6 | -3,4 | 2,9 | 1,9 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -1,3 | 40,5 | -6,5 | 5,3 | 3,9 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -1,1 | 46,2 | -0,8 | -0,3 | 0,9 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 1,8 | 44,1 | -3,0 | 4,8 | 2,4 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,7 | 47,5 | 0,4 | -2,2 | 1,1 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 0,8 | 43,7 | -3,3 | 4,2 | 2,1 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 0,5 | 43,5 | -3,5 | 4,0 | 2,0 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -2,5 | 44,7 | -2,3 | -0,2 | 2,4 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Futura (02/10–03/10) -0,2; Gerp (30/09–02/10) -0,3; Vox Brasil (29/09–01/10) 1,0; Palver (30/09–03/10) -2,2; PoderData (30/09–02/10) 2,9; Ideia (25/09–28/09) 3,1; Datafolha (03/10–03/10) 4,0; Quaest (02/10–03/10) 4,2; AtlasIntel (27/09–02/10) 4,8; IFP (29/09–02/10) 5,3; Real Time Big Data (26/09–30/09) 6,1; Nexus (25/09–27/09) 7,5; CNT/MDA (29/09–02/10) 7,5; Indexa (27/09–29/09) 8,7.

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
| Modelo principal: neutro | 27 | 1,8 | 0,3 | 2,6 | -1,1 | 100% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 2,1 | -1,2 | 2,2 | 0,5 | 98% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 2,8 | -2,4 | 2,6 | 1,8 | 96% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 28,7 | 64,6 | apurado |
| AL | 54,7 | 40,5 | apurado |
| AM | 48,2 | 45,0 | apurado |
| AP | 45,7 | 45,7 | apurado |
| BA | 66,2 | 28,5 | apurado |
| CE | 63,3 | 31,3 | apurado |
| DF | 38,1 | 51,3 | apurado |
| ES | 37,8 | 54,8 | apurado |
| GO | 31,1 | 53,6 | apurado |
| MA | 64,0 | 30,9 | apurado |
| MG | 43,3 | 48,2 | apurado |
| MS | 34,7 | 58,6 | apurado |
| MT | 29,2 | 65,2 | apurado |
| PA | 49,9 | 44,5 | apurado |
| PB | 61,3 | 33,1 | apurado |
| PE | 63,5 | 31,0 | apurado |
| PI | 71,0 | 24,1 | apurado |
| PR | 31,2 | 59,9 | apurado |
| RJ | 39,4 | 53,0 | apurado |
| RN | 59,8 | 34,8 | apurado |
| RO | 25,9 | 67,5 | apurado |
| RR | 22,9 | 71,1 | apurado |
| RS | 35,7 | 55,6 | apurado |
| SC | 25,0 | 66,7 | apurado |
| SE | 62,8 | 30,6 | apurado |
| SP | 38,2 | 51,9 | apurado |
| TO | 43,4 | 50,4 | apurado |
| ZZ | 47,6 | 43,5 | apurado |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
