# Ensaio: avaliação das previsões do 1º turno de 2022

Gerado por `resultado_1t.py` em 2026-10-04 02:06 UTC. Seções totalizadas no Brasil: 100,00% (TSE, 02/10/2022 23:59:59). Ensaio do pipeline com dados históricos (resultado oficial do TSE).

## Resultado (votos válidos, %)

| Lula | Bolsonaro | Ciro | Tebet | Outros |
|---|---|---|---|---|
| 48,43 | 43,20 | 3,04 | 4,16 | 1,17 |

Decidida no 1º turno: não. Ordem: Lula, Bolsonaro, Tebet.

## Previsões nacionais x resultado

Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, 'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); CRPS aproximado pelos quantis publicados (menor = melhor).

| Fonte | Lula prev. | erro | Bolsonaro prev. | erro | Erro na margem | MAE 2 primeiros | PIT Lula | PIT Bolsonaro | Em 80% (Lula/Bolsonaro) | CRPS Lula/Bolsonaro |
|---|---|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 47,6 | -0,8 | 41,2 | -2,0 | 1,2 | 1,4 | 0,60 | 0,76 | sim/sim | 0,71/0,89 |
| Modelo principal: calibrado | 46,4 | -2,1 | 42,5 | -0,7 | -1,3 | 1,4 | 0,74 | 0,59 | sim/sim | 0,94/0,74 |
| Modelo principal: viés pleno | 44,6 | -3,9 | 44,5 | 1,3 | -5,2 | 2,6 | 0,84 | 0,36 | sim/sim | 1,68/0,90 |
| Média das pesquisas (agregador, sem ajustes) | 46,6 | -1,8 | 40,5 | -2,7 | 0,8 | 2,2 | – | – | – | –/– |
| FSB (23/09–25/09) | 47,9 | -0,6 | 37,2 | -6,0 | 5,4 | 3,3 | – | – | – | –/– |
| PoderData (25/09–27/09) | 47,4 | -1,1 | 37,9 | -5,3 | 4,2 | 3,2 | – | – | – | –/– |
| Futura (26/09–28/09) | 43,6 | -4,8 | 40,5 | -2,7 | -2,1 | 3,8 | – | – | – | –/– |
| Ideia (23/09–28/09) | 49,0 | 0,5 | 38,5 | -4,7 | 5,2 | 2,6 | – | – | – | –/– |
| Brasmarket (26/09–28/09) | 34,7 | -13,8 | 51,0 | 7,8 | -21,5 | 10,8 | – | – | – | –/– |
| Parana Pesquisas (27/09–29/09) | 49,8 | 1,4 | 42,3 | -0,9 | 2,3 | 1,1 | – | – | – | –/– |
| Verita (24/09–29/09) | 42,6 | -5,8 | 45,7 | 2,5 | -8,3 | 4,2 | – | – | – | –/– |
| AtlasIntel (28/09–30/09) | 50,3 | 1,9 | 41,1 | -2,1 | 4,0 | 2,0 | – | – | – | –/– |
| CNT/MDA (28/09–30/09) | 48,3 | -0,1 | 39,7 | -3,5 | 3,4 | 1,8 | – | – | – | –/– |
| Ipespe (30/09–30/09) | 47,9 | -0,5 | 34,4 | -8,8 | 8,3 | 4,7 | – | – | – | –/– |
| Ipec (25/09–01/10) | 50,5 | 2,1 | 36,6 | -6,6 | 8,7 | 4,4 | – | – | – | –/– |
| Datafolha (30/09–01/10) | 50,5 | 2,1 | 35,8 | -7,4 | 9,5 | 4,8 | – | – | – | –/– |
| Quaest (30/09–01/10) | 49,1 | 0,7 | 37,8 | -5,4 | 6,1 | 3,0 | – | – | – | –/– |

**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** Futura (26/09–28/09) -2,1; Parana Pesquisas (27/09–29/09) 2,3; CNT/MDA (28/09–30/09) 3,4; AtlasIntel (28/09–30/09) 4,0; PoderData (25/09–27/09) 4,2; Ideia (23/09–28/09) 5,2; FSB (23/09–25/09) 5,4; Quaest (30/09–01/10) 6,1; Ipespe (30/09–30/09) 8,3; Verita (24/09–29/09) -8,3; Ipec (25/09–01/10) 8,7; Datafolha (30/09–01/10) 9,5; Brasmarket (26/09–28/09) -21,5.

## Eventos (Brier e log score)

Brier = (p − ocorreu)²; log score = log da probabilidade dada ao que aconteceu (mais perto de 0 = melhor).

| Fonte | Evento | P prevista | Ocorreu | Brier | Log score |
|---|---|---|---|---|---|
| Modelo principal: neutro | Lula em 1º | 0,875 | sim | 0,016 | -0,134 |
| Modelo principal: neutro | Bolsonaro em 1º | 0,126 | não | 0,016 | -0,134 |
| Modelo principal: neutro | Ciro em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: neutro | Tebet em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: neutro | Outros em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: neutro | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: neutro | Bolsonaro no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: neutro | Ciro no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: neutro | Tebet no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: neutro | Outros no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: neutro | Decidida no 1º turno | 0,218 | não | 0,048 | -0,246 |
| Modelo principal: calibrado | Lula em 1º | 0,743 | sim | 0,066 | -0,297 |
| Modelo principal: calibrado | Bolsonaro em 1º | 0,257 | não | 0,066 | -0,297 |
| Modelo principal: calibrado | Ciro em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: calibrado | Tebet em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: calibrado | Outros em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: calibrado | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: calibrado | Bolsonaro no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: calibrado | Ciro no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: calibrado | Tebet no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: calibrado | Outros no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: calibrado | Decidida no 1º turno | 0,152 | não | 0,023 | -0,165 |
| Modelo principal: viés pleno | Lula em 1º | 0,505 | sim | 0,245 | -0,683 |
| Modelo principal: viés pleno | Bolsonaro em 1º | 0,495 | não | 0,245 | -0,683 |
| Modelo principal: viés pleno | Ciro em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: viés pleno | Tebet em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: viés pleno | Outros em 1º | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: viés pleno | Lula no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: viés pleno | Bolsonaro no 2º turno | 1,000 | sim | 0,000 | -0,001 |
| Modelo principal: viés pleno | Ciro no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: viés pleno | Tebet no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: viés pleno | Outros no 2º turno | 0,000 | não | 0,000 | -0,001 |
| Modelo principal: viés pleno | Decidida no 1º turno | 0,139 | não | 0,019 | -0,150 |

## UFs

| Fonte | UFs | MAE Lula | Viés Lula | MAE Bolsonaro | Viés Bolsonaro | Cobertura 80% | Brier 'Lula 1º na UF' | Acerto do favorito |
|---|---|---|---|---|---|---|---|---|
| Modelo principal: neutro | 27 | 2,5 | -0,6 | 3,6 | -3,1 | 98% | 0,024 | 100% |
| Modelo principal: calibrado | 27 | 2,7 | -1,8 | 3,2 | -1,8 | 98% | 0,021 | 100% |
| Modelo principal: viés pleno | 27 | 3,8 | -3,6 | 2,7 | 0,1 | 93% | 0,029 | 100% |

Exterior fora das métricas por UF. Viés positivo = previsão acima do resultado.

## Resultado por UF (votos válidos, %)

| UF | Lula | Bolsonaro | Situação |
|---|---|---|---|
| AC | 29,3 | 62,5 | apurado |
| AL | 56,5 | 36,0 | apurado |
| AM | 49,6 | 42,8 | apurado |
| AP | 45,7 | 43,4 | apurado |
| BA | 69,7 | 24,3 | apurado |
| CE | 65,9 | 25,4 | apurado |
| DF | 36,9 | 51,6 | apurado |
| ES | 40,4 | 52,2 | apurado |
| GO | 39,5 | 52,2 | apurado |
| MA | 68,8 | 26,0 | apurado |
| MG | 48,3 | 43,6 | apurado |
| MS | 39,0 | 52,7 | apurado |
| MT | 34,4 | 59,8 | apurado |
| PA | 52,2 | 40,3 | apurado |
| PB | 64,2 | 29,6 | apurado |
| PE | 65,3 | 29,9 | apurado |
| PI | 74,2 | 19,9 | apurado |
| PR | 36,0 | 55,3 | apurado |
| RJ | 40,7 | 51,1 | apurado |
| RN | 63,0 | 31,0 | apurado |
| RO | 29,0 | 64,4 | apurado |
| RR | 23,1 | 69,6 | apurado |
| RS | 42,3 | 48,9 | apurado |
| SC | 29,5 | 62,2 | apurado |
| SE | 63,8 | 29,2 | apurado |
| SP | 40,9 | 47,7 | apurado |
| TO | 50,4 | 44,0 | apurado |
| ZZ | 47,2 | 41,6 | apurado |

Leitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em 1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade metodológica de cada um.
