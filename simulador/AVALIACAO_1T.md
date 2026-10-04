# Avaliação das previsões do 1º turno de 2026

Gerado por `resultado_1t.py` em 2026-10-04 23:16 UTC. Seções totalizadas no Brasil: 89,58% (TSE, 04/10/2026 20:14:34). **Apuração parcial: números provisórios; UFs não totalizadas projetadas.** Fonte do resultado: TSE (https://resultados.tse.jus.br/oficial/ele2026/6257/dados/...).

## Resultado (votos válidos, %)

| Lula | Flavio | Caiado | Cury | Zema | Renan | Outros |
|---|---|---|---|---|---|---|
| 45,00 | 47,16 | 2,19 | 2,90 | 0,28 | 2,26 | 0,22 |

Decidida no 1º turno: não. Ordem: Flavio, Lula, Cury.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Flavio prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Flavio | Em 80% (Lula/Flavio) | CRPS Lula/Flavio |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 46,1 | 1,1 | 45,2 | -2,0 | 3,0 | 1,5 | 0,36 | 0,75 | sim/sim | 0,75/0,89 |
| Modelo principal: calibrado | 44,4 | -0,6 | 46,8 | -0,3 | -0,3 | 0,4 | 0,57 | 0,54 | sim/sim | 0,72/0,70 |
| Modelo principal: viés pleno | 43,3 | -1,7 | 48,1 | 1,0 | -2,6 | 1,3 | 0,69 | 0,40 | sim/sim | 0,93/0,84 |
| Modelo alternativo: neutro | 46,6 | 1,6 | 45,3 | -1,9 | 3,5 | 1,7 | 0,33 | 0,66 | sim/sim | 1,21/1,22 |
| Modelo alternativo: historico | 43,8 | -1,2 | 48,1 | 0,9 | -2,1 | 1,1 | 0,60 | 0,40 | sim/sim | 1,10/1,14 |
| Média das pesquisas (agregador, sem ajustes) | 45,3 | 0,3 | 43,8 | -3,3 | 3,6 | 1,8 | – | – | – | –/– |
| Nexus (25/09–27/09) | 47,2 | 2,2 | 41,6 | -5,6 | 7,8 | 3,9 | – | – | – | –/– |
| Ideia (25/09–28/09) | 50,6 | 5,6 | 49,4 | 2,2 | 3,4 | 3,9 | – | – | – | –/– |
| Indexa (27/09–29/09) | 53,4 | 8,4 | 46,6 | -0,6 | 9,0 | 4,5 | – | – | – | –/– |
| Real Time Big Data (26/09–30/09) | 45,7 | 0,7 | 41,5 | -5,7 | 6,4 | 3,2 | – | – | – | –/– |
| Vox Brasil (29/09–01/10) | 45,0 | -0,0 | 45,9 | -1,3 | 1,3 | 0,6 | – | – | – | –/– |
| CNT/MDA (29/09–02/10) | 47,7 | 2,7 | 42,1 | -5,1 | 7,8 | 3,9 | – | – | – | –/– |
| PoderData (30/09–02/10) | 44,7 | -0,3 | 43,6 | -3,5 | 3,2 | 1,9 | – | – | – | –/– |
| IFP (29/09–02/10) | 43,9 | -1,1 | 40,5 | -6,7 | 5,5 | 3,9 | – | – | – | –/– |
| Gerp (30/09–02/10) | 44,1 | -0,9 | 46,2 | -0,9 | 0,0 | 0,9 | – | – | – | –/– |
| AtlasIntel (27/09–02/10) | 47,0 | 1,9 | 44,1 | -3,1 | 5,0 | 2,5 | – | – | – | –/– |
| Palver (30/09–03/10) | 43,4 | -1,6 | 47,5 | 0,3 | -1,9 | 0,9 | – | – | – | –/– |
| Quaest (02/10–03/10) | 46,0 | 1,0 | 43,7 | -3,5 | 4,5 | 2,2 | – | – | – | –/– |
| Datafolha (03/10–03/10) | 45,6 | 0,6 | 43,5 | -3,7 | 4,3 | 2,2 | – | – | – | –/– |
| Futura (02/10–03/10) | 42,6 | -2,4 | 44,7 | -2,4 | 0,0 | 2,4 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Gerp (30/09–02/10) 0,0; Futura (02/10–03/10) 0,0; Vox Brasil (29/09–01/10) 1,3; Palver (30/09–03/10) -1,9; PoderData (30/09–02/10) 3,2; Ideia (25/09–28/09) 3,4; Datafolha (03/10–03/10) 4,3; Quaest (02/10–03/10) 4,5; AtlasIntel (27/09–02/10) 5,0; IFP (29/09–02/10) 5,5; Real Time Big Data (26/09–30/09) 6,4; Nexus (25/09–27/09) 7,8; CNT/MDA (29/09–02/10) 7,8; Indexa (27/09–29/09) 9,0.

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
| Modelo principal: neutro | 27 | 1,7 | 0,5 | 2,6 | -1,2 | 100% | 0,057 | 96% |
| Modelo principal: calibrado | 27 | 1,9 | -1,1 | 2,1 | 0,4 | 98% | 0,060 | 93% |
| Modelo principal: viés pleno | 27 | 2,6 | -2,2 | 2,5 | 1,7 | 98% | 0,068 | 89% |
| Modelo alternativo: neutro | – | – | – | – | – | –% | 0,060 | 89% |
| Modelo alternativo: historico | – | – | – | – | – | –% | 0,065 | 93% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Flavio | Situação |
|---|---|---|---|
| AC | 28,8 | 64,5 | parcial |
| AL | 54,2 | 41,0 | parcial |
| AM | 47,8 | 45,4 | parcial |
| AP | 45,7 | 45,6 | parcial |
| BA | 65,1 | 29,4 | parcial |
| CE | 62,5 | 31,9 | parcial |
| DF | 38,1 | 51,3 | apurado |
| ES | 37,7 | 54,8 | parcial |
| GO | 31,0 | 53,7 | parcial |
| MA | 63,4 | 31,4 | parcial |
| MG | 43,2 | 48,3 | parcial |
| MS | 34,6 | 58,6 | parcial |
| MT | 29,2 | 65,1 | parcial |
| PA | 49,5 | 44,9 | parcial |
| PB | 61,3 | 33,1 | parcial |
| PE | 63,3 | 31,2 | parcial |
| PI | 70,5 | 24,5 | parcial |
| PR | 31,2 | 59,9 | parcial |
| RJ | 39,8 | 52,6 | parcial |
| RN | 59,5 | 34,9 | parcial |
| RO | 25,9 | 67,5 | parcial |
| RR | 22,8 | 71,2 | parcial |
| RS | 35,7 | 55,6 | parcial |
| SC | 25,1 | 66,6 | parcial |
| SE | 62,6 | 30,7 | parcial |
| SP | 38,2 | 52,0 | parcial |
| TO | 43,4 | 50,4 | parcial |
| ZZ | 46,9 | 43,8 | parcial |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
