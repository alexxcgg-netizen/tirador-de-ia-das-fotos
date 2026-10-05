# Backtest do simulador: 2014, 2018 e 2022 (véspera)

Gerado por `backtest.py` em 2026-10-04 02:13 UTC; 20.000 simulações por alvo na grade e 40.000 na avaliação final; tempo total 953 s.

## O que foi testado

O motor de `modelo.py` rodou como se fosse a véspera de cada turno, só com as pesquisas daquele momento
(`data/backtest_pesquisas_*.csv`), e foi comparado com o resultado oficial do TSE (`data/backtest_resultados.csv`).

* **v1 — véspera do 1º turno:** prevê o 1º turno (nacional e 27 UFs + exterior) e o 2º turno (2018 e 2022;
  em 2014 não havia pesquisa Dilma x Aécio antes do 1º turno no conjunto de dados).
* **v2 — véspera do 2º turno:** 1º turno real conhecido; pesquisas de 2º turno feitas depois do 1º turno.
* **Sem informação futura:** adversário = 2º colocado na média de véspera; prior das UFs = lean da eleição anterior;
  abstenção e brancos/nulos da eleição anterior; matriz de transferência das próprias pesquisas da véspera
  (perguntas de 1º e 2º turno na mesma pesquisa); rejeição só se publicada até a véspera; o prior do viés da
  indústria para o ano A usa só os erros dos **outros** anos (leave-one-election-out, LOEO). A variante
  **temporal** usa só anos anteriores (2014 sem prior; 2018 com 2014; 2022 com 2014 e 2018).
* **Limites do teste:** só 3 eleições (2 para o 2º turno projetado na véspera do 1º); pesquisas estaduais
  esparsas (2014 sem nenhuma; 2018 quase só Ibope; 2022 quase só Ipec). O prior demográfico e o ajuste de
  comparecimento de 2026 não entram no backtest (covariáveis de 2022–2026 e comparecimento real de 2022 seriam
  vazamento); a via de transferência usa a matriz implícita das pesquisas, não a matriz Quaest por candidato.

**Adversário de cada ano (conferido pela média de véspera, sem usar o resultado):** 2014: Aecio = não-PT mais votado na média (Aecio 23.7, Marina 21.1); 2018: Bolsonaro = não-PT mais votado na média (Bolsonaro 34.8, Ciro 10.9, Alckmin 6.6, Marina 3.2, Amoedo 2.6); 2022: Bolsonaro = não-PT mais votado na média (Bolsonaro 37.3, Ciro 4.7, Tebet 4.4). Em 2014 Aécio passou Marina só nos últimos dias; na média simples da última semana Marina ainda aparecia à frente, então a escolha do adversário numa disputa a três é frágil.

**Prior estadual sem dados futuros:** inclinação do lean e dp do prior de cada ano estimados só com eleições anteriores (2014: 0.91/5.8 p.p. (1T), 0.82/5.3 p.p. (2T); 2018: 0.97/11.5 p.p. (1T), 0.91/8.4 p.p. (2T); 2022: 0.95/8.6 p.p. (1T), 1.15/5.9 p.p. (2T)). Só os sinais das cargas do eixo NE/N x S/CO vêm de correlações 2002–2022 (parcialmente dentro da amostra).

## Erros das médias de véspera (insumo do prior de viés)

| Ano | T pesquisas | T real | erro T (log) | p2 pesquisas | p2 real | q pesq. véspera 1T | q pesq. véspera 2T | q real |
|---|---|---|---|---|---|---|---|---|
| 2014 | 27,2 | 24,9 | -0,09 | 63,0 | 55,4 | – | 52,3 | 51,6 |
| 2018 | 33,4 | 24,7 | -0,30 | 39,4 | 38,9 | 48,4 | 43,7 | 44,9 |
| 2022 | 12,9 | 8,4 | -0,43 | 53,5 | 52,9 | 55,6 | 51,0 | 50,9 |

T = soma dos candidatos fora os dois primeiros (votos válidos); p2 = PT/(PT+adversário); q = PT no 2º turno. Valores das médias do agregador (house effects hierárquicos, recência, indecisos pelo método escolhido). Erro positivo = pesquisas mais favoráveis ao PT.

Resíduos usados no prior (p.p.; p2 depois da contração média da terceira via estimada sem o próprio ano): {"p2_pp": {"2014": 6.41, "2018": 2.92, "2022": 0.77}, "q_v1_pp": {"2018": 3.52, "2022": 4.71}, "q_v2_pp": {"2014": 0.69, "2018": -1.14, "2022": 0.1}, "T_log": {"2014": -0.09, "2018": -0.302, "2022": -0.429}}

## Calibração: cobertura, erros e escores por visão

Nas três primeiras linhas, o prior de viés de cada ano exclui o próprio ano (LOEO), mas os demais parâmetros (dp, gl, pisos, pesos) foram escolhidos na grade com os três anos: é uma avaliação parcialmente dentro da amostra. A linha 'LOEO aninhado' refaz a escolha de todos os parâmetros sem o ano avaliado e é a medida honesta de desempenho fora da amostra. O exterior (ZZ) fica fora das métricas por UF (o voto no exterior mudou 20–40 p.p. entre eleições).

| Visão | Cob. 50% nac | Cob. 80% nac | Cob. 95% nac | Cob. 50% UF | Cob. 80% UF | Cob. 95% UF | CRPS nac | CRPS UF | Brier nac | Brier UF | Log-loss UF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Neutro (viés 0) | 30,0 | 75,0 | 100,0 | 43,4 | 79,5 | 93,3 | 2,23 | 3,52 | 0,012 | 0,060 | 0,215 |
| Modelo calibrado | 45,0 | 80,0 | 100,0 | 46,8 | 81,1 | 93,6 | 1,94 | 3,44 | 0,017 | 0,057 | 0,204 |
| Viés histórico pleno | 50,0 | 85,0 | 100,0 | 48,5 | 80,5 | 93,6 | 1,76 | 3,39 | 0,041 | 0,053 | 0,191 |
| Calibrado, LOEO aninhado (parâmetros e prior sem o ano) | 40,0 | 75,0 | 95,0 | 51,5 | 80,5 | 92,9 | 2,08 | 3,55 | 0,027 | 0,058 | 0,212 |
| Calibrado, prior temporal | 40,0 | 70,0 | 100,0 | 46,8 | 79,8 | 92,9 | 2,27 | 3,59 | 0,017 | 0,059 | 0,210 |

Cobertura = % dos resultados reais dentro do intervalo central de 50/80/95% (ideal: 50/80/95). CRPS em p.p. (menor = melhor). Brier/log-loss das probabilidades de vitória (nacional: PT 1º no 1º turno e PT vence; UF: PT 1º na UF no 1º turno e PT vence a UF no 2º turno).

## Nacional, modelo calibrado (LOEO)

| Ano | Alvo | Variável | Real | Mediana | Erro | 80% | 95% | PIT | Em 80% | Em 95% |
|---|---|---|---|---|---|---|---|---|---|---|
| 2014 | 1T | pt1 | 41,6 | 48,5 | 6,9 | 43,7–52,9 | 40,7–55,4 | 0,04 | não | sim |
| 2014 | 1T | opp1 | 33,5 | 31,3 | -2,3 | 26,9–35,9 | 24,3–38,7 | 0,74 | sim | sim |
| 2014 | 1T | T | 24,9 | 19,9 | -5,0 | 15,5–25,6 | 13,5–29,3 | 0,87 | sim | sim |
| 2014 | 1T | margem | 8,0 | 17,2 | 9,1 | 9,7–24,4 | 4,4–28,9 | 0,07 | não | sim |
| 2014 | 1T | p2 | 55,4 | 60,8 | 5,4 | 56,0–65,3 | 52,7–68,2 | 0,08 | não | sim |
| 2014 | 2T (véspera do 2T) | q | 51,6 | 52,6 | 1,0 | 51,2–54,1 | 50,3–55,0 | 0,19 | sim | sim |
| 2018 | 1T | pt1 | 29,3 | 30,0 | 0,7 | 25,4–34,5 | 22,8–37,2 | 0,42 | sim | sim |
| 2018 | 1T | opp1 | 46,0 | 42,8 | -3,3 | 38,7–46,5 | 36,0–48,6 | 0,87 | sim | sim |
| 2018 | 1T | T | 24,7 | 27,1 | 2,4 | 22,0–33,1 | 19,7–37,2 | 0,28 | sim | sim |
| 2018 | 1T | margem | -16,8 | -12,8 | 4,0 | -18,8–-6,4 | -22,5–-2,1 | 0,19 | sim | sim |
| 2018 | 1T | p2 | 38,9 | 41,2 | 2,3 | 36,8–45,6 | 34,0–48,6 | 0,25 | sim | sim |
| 2018 | 2T (véspera do 1T) | q | 44,9 | 47,1 | 2,2 | 42,5–51,7 | 39,7–54,7 | 0,26 | sim | sim |
| 2018 | 2T (véspera do 2T) | q | 44,9 | 43,5 | -1,4 | 42,1–44,9 | 41,2–45,8 | 0,89 | sim | sim |
| 2022 | 1T | pt1 | 48,4 | 46,4 | -2,0 | 42,1–50,7 | 39,1–53,4 | 0,74 | sim | sim |
| 2022 | 1T | opp1 | 43,2 | 42,4 | -0,8 | 38,3–46,6 | 35,5–49,5 | 0,60 | sim | sim |
| 2022 | 1T | T | 8,4 | 11,0 | 2,6 | 8,9–13,6 | 7,9–15,4 | 0,05 | não | sim |
| 2022 | 1T | margem | 5,2 | 3,9 | -1,3 | -4,2–12,0 | -9,9–17,4 | 0,59 | sim | sim |
| 2022 | 1T | p2 | 52,9 | 52,2 | -0,6 | 47,6–56,8 | 44,4–59,8 | 0,58 | sim | sim |
| 2022 | 2T (véspera do 1T) | q | 50,9 | 54,4 | 3,5 | 49,6–59,1 | 46,5–62,1 | 0,17 | sim | sim |
| 2022 | 2T (véspera do 2T) | q | 50,9 | 51,1 | 0,2 | 49,8–52,5 | 48,9–53,4 | 0,41 | sim | sim |

pt1/opp1 = válidos do PT/adversário no 1º turno; T = terceira via; margem = PT − adversário; q = PT no 2º turno.

| Ano | Alvo | Evento | P(modelo) | Ocorreu | Brier |
|---|---|---|---|---|---|
| 2014 | 1T | PT 1º no 1º turno | 0,991 | 1 | 0,000 |
| 2014 | 2T (véspera do 2T) | PT vence o 2º turno | 0,983 | 1 | 0,000 |
| 2018 | 1T | PT 1º no 1º turno | 0,013 | 0 | 0,000 |
| 2018 | 2T (véspera do 1T) | PT vence a eleição | 0,199 | 0 | 0,040 |
| 2018 | 2T (véspera do 2T) | PT vence o 2º turno | 0,000 | 0 | 0,000 |
| 2022 | 1T | PT 1º no 1º turno | 0,743 | 1 | 0,066 |
| 2022 | 2T (véspera do 1T) | PT vence a eleição | 0,881 | 1 | 0,014 |
| 2022 | 2T (véspera do 2T) | PT vence o 2º turno | 0,861 | 1 | 0,019 |

## UFs, modelo calibrado (LOEO)

| Ano | Alvo | Var. | UFs | Erro abs. médio | Erro médio (viés) | Cob. 50% | Cob. 80% | Cob. 95% | CRPS |
|---|---|---|---|---|---|---|---|---|---|
| 2014 | 1T | opp1 | 27 | 6,4 | 0,3 | 37,0 | 70,4 | 88,9 | 4,53 |
| 2014 | 1T | pt1 | 27 | 7,6 | 3,6 | 37,0 | 55,6 | 81,5 | 5,61 |
| 2014 | 2T (véspera do 2T) | q | 27 | 4,0 | -1,1 | 37,0 | 74,1 | 85,2 | 2,93 |
| 2018 | 1T | opp1 | 27 | 6,0 | -4,0 | 40,7 | 66,7 | 85,2 | 4,46 |
| 2018 | 1T | pt1 | 27 | 5,8 | -1,2 | 44,4 | 74,1 | 88,9 | 4,18 |
| 2018 | 2T (véspera do 1T) | q | 27 | 5,9 | 2,5 | 51,9 | 85,2 | 100,0 | 4,04 |
| 2018 | 2T (véspera do 2T) | q | 27 | 3,1 | -1,2 | 44,4 | 81,5 | 100,0 | 2,16 |
| 2022 | 1T | opp1 | 27 | 3,3 | -1,9 | 74,1 | 96,3 | 100,0 | 2,27 |
| 2022 | 1T | pt1 | 27 | 2,6 | -1,8 | 70,4 | 100,0 | 100,0 | 2,16 |
| 2022 | 2T (véspera do 1T) | q | 27 | 5,4 | 5,2 | 29,6 | 92,6 | 100,0 | 3,67 |
| 2022 | 2T (véspera do 2T) | q | 27 | 2,6 | 0,6 | 48,1 | 96,3 | 100,0 | 1,78 |

| Ano | Alvo | Evento | UFs | Brier | Log-loss | % UFs com favorito certo |
|---|---|---|---|---|---|---|
| 2014 | 1T | PT 1º na UF (1T) | 27 | 0,194 | 0,626 | 63,0 |
| 2014 | 2T (véspera do 2T) | PT vence a UF (2T) | 27 | 0,016 | 0,097 | 100,0 |
| 2018 | 1T | PT 1º na UF (1T) | 27 | 0,069 | 0,237 | 92,6 |
| 2018 | 2T (véspera do 1T) | PT vence a UF (2T) | 27 | 0,063 | 0,231 | 92,6 |
| 2018 | 2T (véspera do 2T) | PT vence a UF (2T) | 27 | 0,018 | 0,073 | 100,0 |
| 2022 | 1T | PT 1º na UF (1T) | 27 | 0,021 | 0,111 | 100,0 |
| 2022 | 2T (véspera do 1T) | PT vence a UF (2T) | 27 | 0,041 | 0,155 | 96,3 |
| 2022 | 2T (véspera do 2T) | PT vence a UF (2T) | 27 | 0,033 | 0,100 | 96,3 |

Maiores erros por UF (mediana − real, p.p.):

| Ano | Alvo | Var. | UF | Real | Mediana | Erro | PIT | Em 95% |
|---|---|---|---|---|---|---|---|---|
| 2014 | 1T | pt1 | DF | 23,0 | 47,2 | 24,1 | 0,001 | não |
| 2014 | 1T | opp1 | AC | 29,1 | 49,4 | 20,3 | 0,003 | não |
| 2014 | 1T | pt1 | RJ | 35,6 | 53,2 | 17,6 | 0,006 | não |
| 2018 | 1T | opp1 | RJ | 59,8 | 43,1 | -16,6 | 0,992 | não |
| 2014 | 1T | pt1 | PE | 44,2 | 60,7 | 16,5 | 0,015 | não |
| 2018 | 2T (véspera do 1T) | q | RJ | 32,0 | 48,1 | 16,1 | 0,027 | sim |
| 2014 | 1T | pt1 | SP | 25,8 | 41,5 | 15,7 | 0,004 | não |
| 2018 | 1T | pt1 | RJ | 14,7 | 29,5 | 14,8 | 0,019 | não |
| 2018 | 1T | opp1 | AC | 62,2 | 47,6 | -14,6 | 0,986 | não |
| 2018 | 2T (véspera do 1T) | q | AC | 22,8 | 37,4 | 14,6 | 0,035 | sim |
| 2018 | 1T | opp1 | RO | 62,2 | 48,1 | -14,1 | 0,984 | não |
| 2018 | 1T | pt1 | MA | 61,3 | 47,6 | -13,7 | 0,993 | não |

## Histograma PIT (todas as variáveis, nacional + UF, modelo calibrado)

| Faixa | 0.0–0.1 | 0.1–0.2 | 0.2–0.3 | 0.3–0.4 | 0.4–0.5 | 0.5–0.6 | 0.6–0.7 | 0.7–0.8 | 0.8–0.9 | 0.9–1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| n | 36 | 36 | 32 | 22 | 44 | 30 | 23 | 37 | 40 | 31 |

Um modelo calibrado tem PIT uniforme (barras iguais). Barras altas nas pontas = intervalos estreitos; acúmulo num lado = viés. Os PITs das UFs de um mesmo ano são fortemente correlacionados (o erro nacional é comum), então o histograma tem muito menos informação independente do que o número de pontos sugere.

## Escolha dos parâmetros (grade + leave-one-election-out)

Peso das pesquisas de 2º turno (0,5) e encolhimento do viés (tau0 = 2 p.p.) fixos por princípio: só 2–3 eleições os informam. Limites inferiores dos pisos estaduais pelo conhecimento prévio (Pindograma: MAE de 2,25–4,34 p.p.). Escolha por blocos: entre as combinações cuja cobertura média é de pelo menos 75% no intervalo de 80% e 90% no de 95% (evita intervalos estreitos demais), a de menor CRPS médio; cada bloco usa os parâmetros já escolhidos dos anteriores. 'Fora da amostra' = CRPS do ano deixado de fora com os parâmetros escolhidos nos outros anos; 'na amostra' = com os parâmetros escolhidos em todos os anos.

**Bloco nac1** — escolhido: `{"erro_nacional_1t.dp_p2_pp": 4.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 2.0}` (CRPS médio 1,958).
Sem fixar o encolhimento, a grade escolheria `{"erro_nacional_1t.dp_p2_pp": 3.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": null}` (CRPS 1,883); o encolhimento fica fixo por princípio (ver abaixo).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2014 | {"erro_nacional_1t.dp_p2_pp": 3.0, "erro_nacional_1t.gl_t": 10.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 2.0} | 3,172 | 3,102 |
| 2018 | {"erro_nacional_1t.dp_p2_pp": 3.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.2, "vies.tau0_p2_pp": 2.0} | 1,641 | 1,495 |
| 2022 | {"erro_nacional_1t.dp_p2_pp": 6.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 2.0} | 1,407 | 1,277 |

**Bloco nac2** — escolhido: `{"erro_2t.dp_q_pp_vespera_1t": 6.0, "erro_2t.peso_pesquisas_vespera_1t": 0.5, "vies.tau0_q_pp": 2.0}` (CRPS médio 1,705).
Sem fixar o encolhimento, a grade escolheria `{"erro_2t.dp_q_pp_vespera_1t": 2.0, "erro_2t.peso_pesquisas_vespera_1t": 0.1, "vies.tau0_q_pp": null}` (CRPS 1,102); o encolhimento fica fixo por princípio (ver abaixo).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2018 | {"erro_2t.dp_q_pp_vespera_1t": 8.0, "erro_2t.peso_pesquisas_vespera_1t": 0.5, "vies.tau0_q_pp": 2.0} | 1,452 | 1,373 |
| 2022 | {"erro_2t.dp_q_pp_vespera_1t": 3.0, "erro_2t.peso_pesquisas_vespera_1t": 0.5, "vies.tau0_q_pp": 2.0} | 2,181 | 2,037 |

**Bloco nac3** — escolhido: `{"erro_2t.dp_q_pp_vespera_2t": 1.5}` (CRPS médio 0,575).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2014 | {"erro_2t.dp_q_pp_vespera_2t": 1.5} | 0,601 | 0,601 |
| 2018 | {"erro_2t.dp_q_pp_vespera_2t": 1.0} | 0,896 | 0,847 |
| 2022 | {"erro_2t.dp_q_pp_vespera_2t": 2.5} | 0,377 | 0,276 |

**Bloco uf** — escolhido: `{"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 3.0}` (CRPS médio 3,497).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2014 | {"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 1.5} | 4,365 | 4,338 |
| 2018 | {"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 3.0} | 3,706 | 3,706 |
| 2022 | {"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 7.0, "estados.dp_pesquisa_piso_2t_pp": 3.0, "estados.dp_regional_pp": 4.5} | 2,626 | 2,446 |

Sensibilidade ao encolhimento do viés do 1º turno (tau0, p.p.; LOEO, demais parâmetros fixos):

| tau0 p2 | CRPS nacional 1T |
|---|---|
| 0,0 | 2,149 |
| 1,0 | 2,069 |
| 2,0 | 1,958 |
| 4,0 | 1,886 |
| ∞ (sem encolhimento) | 1,883 |

Sensibilidade ao encolhimento do viés do 2º turno projetado na véspera do 1º (tau0, p.p.):

| tau0 q | CRPS nacional 2T |
|---|---|
| 0,0 | 1,716 |
| 1,0 | 1,708 |
| 2,0 | 1,705 |
| 4,0 | 1,704 |
| ∞ (sem encolhimento) | 1,703 |

## Decisão no 1º turno: diagnóstico

Nenhuma das três eleições do backtest foi decidida no 1º turno (líder com 41,6% em 2014, 46,0% em 2018 e 48,4% em 2022). O evento entra agora nas probabilidades nacionais ('Decidida no 1º turno') e a fatia do líder ('lider1') nas contínuas, fora das médias de cobertura e CRPS usadas na grade.

**Decomposição em 2026** (200 mil simulações, um componente desligado de cada vez; p.p. de votos válidos):

| Visão | Componente alterado | P(decidida) % | Lula vence no 1T % | Flávio vence no 1T % | Lula méd. | Flávio méd. | 3ª via méd. |
|---|---|---|---|---|---|---|---|
| calibrado | modelo como está | 21,3 | 5,1 | 16,2 | 44,4 | 46,8 | 8,7 |
| calibrado | erro nacional de margem: dp 4,0 -> 3,0 | 14,0 | 2,4 | 11,6 | 44,4 | 46,8 | 8,7 |
| calibrado | erro nacional de margem: dp 4,0 -> 2,0 | 7,3 | 0,7 | 6,6 | 44,4 | 46,8 | 8,7 |
| calibrado | erro nacional de margem desligado | 1,3 | 0,0 | 1,3 | 44,4 | 46,8 | 8,7 |
| calibrado | caudas: t5 -> t30 (quase normal) | 24,3 | 5,8 | 18,6 | 44,4 | 46,8 | 8,7 |
| calibrado | sem contração da 3ª via (média e incerteza 0) | 11,2 | 3,0 | 8,2 | 43,4 | 45,4 | 11,2 |
| calibrado | sem erro aleatório da 3ª via | 21,1 | 5,1 | 16,0 | 44,5 | 46,9 | 8,7 |
| calibrado | sem ajuste de comparecimento | 19,7 | 6,1 | 13,7 | 44,8 | 46,4 | 8,7 |
| calibrado | viés sem incerteza (dp 0) | 18,9 | 4,3 | 14,6 | 44,4 | 46,8 | 8,7 |
| calibrado | viés do 1º turno = 0 | 16,1 | 8,2 | 7,9 | 45,7 | 45,6 | 8,7 |
| neutro | modelo como está | 16,4 | 9,9 | 6,5 | 46,1 | 45,2 | 8,7 |
| neutro | erro nacional de margem: dp 4,0 -> 3,0 | 8,5 | 5,3 | 3,2 | 46,1 | 45,2 | 8,7 |
| neutro | erro nacional de margem: dp 4,0 -> 2,0 | 2,5 | 1,7 | 0,9 | 46,1 | 45,2 | 8,7 |
| neutro | erro nacional de margem desligado | 0,0 | 0,0 | 0,0 | 46,1 | 45,2 | 8,7 |
| neutro | caudas: t5 -> t30 (quase normal) | 19,8 | 12,0 | 7,8 | 46,1 | 45,2 | 8,7 |
| neutro | sem contração da 3ª via (média e incerteza 0) | 8,9 | 5,7 | 3,2 | 45,0 | 43,8 | 11,2 |
| neutro | sem erro aleatório da 3ª via | 16,1 | 9,8 | 6,3 | 46,1 | 45,2 | 8,7 |

**Validação aninhada por variante** (para cada ano, dp/gl/dp_log escolhidos sem o ano, com a regra da grade; prior de viés sem o ano; 20 mil simulações):

| Variante | P dec. 2014 | P dec. 2018 | P dec. 2022 | Brier dec. | Log-loss dec. | CRPS nac 1T | Cob. 80% | Cob. 95% | CRPS líder | PIT líder 14/18/22 |
|---|---|---|---|---|---|---|---|---|---|---|
| atual | 31,2 | 0,8 | 26,0 | 0,055 | 0,227 | 2,41 | 73,3 | 93,3 | 2,67 | 0.02/0.87/0.58 |
| contração da 3ª via mais encolhida (tau0_log 0,15) | 26,1 | 1,7 | 23,7 | 0,042 | 0,197 | 2,44 | 73,3 | 100,0 | 2,48 | 0.07/0.86/0.61 |
| sem contração da 3ª via (tau0_log 0) | 11,5 | 1,0 | 20,6 | 0,019 | 0,121 | 3,02 | 60,0 | 100,0 | 2,43 | 0.24/0.92/0.67 |
| contração sem mexer em p2 (proporcional) | 42,3 | 11,5 | 20,4 | 0,078 | 0,300 | 2,46 | 73,3 | 86,7 | 2,63 | 0.02/0.63/0.64 |

Leitura:
* O componente que mais pesa é o **erro nacional de margem** (dp 4,0 p.p. em p2, ~7 p.p. na margem): desligado, a
  probabilidade cai para perto de zero; com dp 3,0 ela cai cerca de um terço. O segundo é a **contração da
  terceira via** (os votos que saem dos menores vão sobretudo para os dois primeiros e aproximam o líder de 50%).
  O viés calibrado muda **quem** vence no 1º turno (desloca de Lula para Flávio) mais do que o total; caudas t5
  não são a causa (com t30 a probabilidade sobe um pouco, porque a mesma variância fica mais concentrada perto de
  ±1–1,5 dp); comparecimento e erros estaduais quase não contam.
* **O backtest não sustenta reduzir o dp nacional:** com dp 3,0 ou 2,0 a cobertura de 80% cai para 67% e a de 95%
  para 93%/80% (abaixo da restrição); a escolha aninhada continua entre 3 e 6. A probabilidade de decisão na
  véspera de 2014 (~31%) e de 2022 (~16–26%) foi alta e nenhuma das duas foi decidida, o que aponta na mesma
  direção dos mercados, mas são 3 eventos (2 informativos) e o Brier com 3 'não' sempre premia estreitar.
* **Sem contração** a decisão no 1º turno fica mais bem calibrada (Brier menor), mas o CRPS nacional piora muito e a
  cobertura de 80% cai para 60%: os menores perderam votos na urna nas três eleições. **Contração mais encolhida**
  (tau0_log 0,15) melhora um pouco o Brier da decisão e o CRPS do líder, com CRPS nacional praticamente igual
  (diferença dentro do ruído de 20 mil simulações): não há evidência suficiente para trocar.
* Decisão: **parâmetros mantidos**. A probabilidade de decisão no 1º turno é a parte menos confiável do modelo
  (cauda de um erro estimado com 3 eleições) e é apresentada com essa ressalva no README (Limitações).

## Indecisos: rejeição/2ª preferência x proporcional

| Ano | Turno | Real (p2 ou q) | Proporcional | Rejeição/2ª pref. | Erro prop. | Erro rej. | Informação usada |
|---|---|---|---|---|---|---|---|
| 2018 | 1T | 38,9 | 39,4 | 40,5 | 0,5 | 1,6 | rejeição 41/44 (Datafolha, até a véspera) |
| 2018 | 2T | 44,9 | 43,7 | 43,7 | -1,1 | -1,1 | rejeição 54/41 (Datafolha, até a véspera) |
| 2022 | 1T | 52,9 | 53,5 | 53,5 | 0,6 | 0,6 | sem rejeição publicada no conjunto -> igual ao proporcional |
| 2022 | 1T | 52,9 | 53,5 | 53,3 | 0,6 | 0,5 | 2ª preferência dos indecisos (Quaest 1/10/2022, publicada em 2024: só validação) |
| 2022 | 2T | 50,9 | 51,0 | 51,2 | 0,1 | 0,3 | rejeição 46/50 (Datafolha, até a véspera) |

Leitura: a alocação por "espaço" (100 − rejeição − intenção) ou por 2ª preferência leva os indecisos para quem
tem menos rejeição relativa à intenção atual. A linha de 2022 com a 2ª preferência da Quaest usa informação
publicada depois da eleição e serve só para validar o método (não entra na calibração).

## 2º turno condicionado ao 1º turno real: matriz nacional única x transferência regionalizada

*Seção escrita à mão em 4/10/2026 (noite do 1º turno), fora do `backtest.py`; refazer com
`python simulador/resultado_1t.py --backtest-2t` (não grava arquivos). Se `backtest.py` regenerar este arquivo,
recolar esta seção.*

**Método novo** (`transferencia_regional.py`): logito da fatia decidida do eliminado para o PT na UF =
nacional + β·lean da UF (logito, 1º turno) + recentragem que mantém o nacional da matriz. β por eleição (MQ não
linear em 27 UFs, participação 0,65): 2002 1,31 (ep 0,26); 2010 0,46 (0,15); 2014 0,12 (0,09); 2018 0,57 (0,17);
2022 0,38 (0,27); 2006 excluído (oponente perdeu votos). Combinação hierárquica: μ = 0,46, τ entre eleições 0,40,
dp preditivo 0,44. Nos testes abaixo β é sempre estimado **sem** o ano avaliado.

**(1) Distribuição entre UFs isolada** — linha nacional da véspera (pesquisas pareadas; 2002/2010: linha genérica),
nacional ajustado ao real (só a distribuição entre UFs conta). Erro médio absoluto por UF (p.p. do PT no 2º turno):

| Ano | β (LOEO) | Matriz única | Regionalizada | + efeito regional fixo |
|---|---|---|---|---|
| 2002 | 0,33 | 3,05 | 2,83 | 2,72 |
| 2010 | 0,45 | 1,33 | 1,19 | 1,02 |
| 2014 | 0,56 | 1,39 | **2,29** | 2,02 |
| 2018 | 0,42 | 1,86 | 1,68 | 1,55 |
| 2022 | 0,46 | 0,53 | 0,40 | 0,94 |
| Média (MAE / RMSE) | | 1,63 / 2,25 | 1,68 / 2,19 | 1,65 / 2,14 |

Correlação erro x lean com a matriz única: −0,32, −0,52, −0,15, −0,44, −0,67 (UFs petistas subestimadas, antipetistas
superestimadas) — o padrão que β corrige; com β: −0,04, +0,19, +0,58, −0,01, −0,30. 2014 é a exceção: o voto de
Marina não seguiu o lean (β do ano 0,12) e β = 0,56 corrige demais. O efeito regional fixo melhora 2002/2010/2018,
mas piora 2022 (0,40→0,94) e não entrou.

**(2) Pipeline completo** (`simular_2t`, 100 mil simulações, LOEO para β, calibração e comparecimento; 1º turno real
do CSV do TSE; pesquisas de 2º turno da véspera do 1º turno com peso 0,25):

| Ano | Variante | Erro nacional | PIT | UF MAE | UF RMSE | Cob. 80% UF | Cob. 95% UF | Acerto UF | Brier UF |
|---|---|---|---|---|---|---|---|---|---|
| 2014 | matriz única | +1,99 | 0,24 | 2,45 | 3,32 | 0,89 | 0,96 | 0,96 | 0,027 |
| 2014 | regionalizada | +2,04 | 0,23 | 2,87 | 3,88 | 0,89 | 0,96 | 1,00 | 0,020 |
| 2018 | matriz única | −1,61 | 0,70 | 2,19 | 3,00 | 0,85 | 0,96 | 0,96 | 0,025 |
| 2018 | regionalizada | −1,59 | 0,70 | 1,80 | 2,51 | 0,93 | 1,00 | 0,93 | 0,027 |
| 2022 | matriz única | +2,20 | 0,20 | 2,11 | 2,24 | 1,00 | 1,00 | 0,96 | 0,024 |
| 2022 | regionalizada | +2,20 | 0,21 | 2,10 | 2,18 | 1,00 | 1,00 | 0,96 | 0,024 |
| Média | matriz única | 1,94 | | 2,25 | 2,85 | 0,91 | 0,975 | | 0,025 |
| Média | regionalizada | 1,94 | | 2,25 | 2,86 | 0,94 | 0,988 | | 0,024 |

Viés médio por região (previsto − real, p.p.), 2018: NE −3,7 → −2,3, S +0,3 → −0,3; 2022: NE +1,3 → +1,6,
S +3,0 → +2,7 (o erro nacional de +2,2 domina).

**Decisão: adotada** (`PARAM_2T["transferencia_regional"] = True`). Regra: nacional neutro e UF melhor na validação
2018/2022 — nacional igual (por construção), UF MAE 2,19→1,80 e 2,11→2,10, cobertura melhor. Ressalva: com 2014 a
média do MAE fica empatada (2,25) e, na distribuição isolada, a média 2014–2022 piora (1,26→1,46) por causa de 2014;
o ganho esperado é pequeno e concentrado em eleições em que os eliminados são do campo antipetista (2018, 2022,
2026). O método antigo é publicado como sensibilidade em `resultados_2t.json`.

**Comparecimento 1º→2º turno por UF (LOEO 2014/2018/2022).** Erro médio absoluto da abstenção do 2º turno por UF
(p.p.): média da variação por UF (atual) 1,29; encolhida para o nacional (k = 1) 1,35; (k = 3) 1,51; só nacional
1,80; sem variação 1,92. Brancos+nulos: 2,35 / 2,30 / 2,31 / 2,43 / 1,92. Viés nacional da abstenção prevista:
−1,0 (2014), −0,5 (2018), +1,5 (2022) — compatível com o dp nacional de 1 p.p. Efeito partidário: correlação da
variação da abstenção com o lean −0,04, −0,04, −0,20 (2022: UFs petistas compareceram relativamente mais, −0,7
p.p. por unidade de logito); a reponderação das UFs mexe ≤ 0,25 p.p. no PT nacional. Mantido o método atual.

## 2º turno: correção das pesquisas pelo erro de cada instituto no 1º turno e viés 1T → 2T (5/10/2026)

*Seção escrita à mão em 5/10/2026 (1º turno com 99,9% apurado), fora do `backtest.py`; refazer com
`python simulador/resultado_1t.py --backtest-institutos` (grava `data/backtest_correcao_institutos.json`). Se
`backtest.py` regenerar este arquivo, recolar esta seção.*

**Método** (`vies_institutos.py`). Erro do instituto no 1º turno = fatia bipartidária do PT na sua última pesquisa
dos 7 dias finais menos o real. Efeitos aleatórios (DerSimonian-Laird): e_p ~ N(θ_p, v_p), θ_p ~ N(μ, τ²), v_p =
amostral (n dos que escolheram PT ou adversário; n ausente = 2000) + 1 p.p.² não amostral. Lean encolhido θ_p = μ +
B_p(e_p − μ), B_p = τ²/(τ² + v_p). Variantes aplicadas às pesquisas de 2º turno do mesmo instituto: **nenhuma**;
**relativa** (só B_p(e_p − μ)); **indústria** (só μ); **plena** (μ + desvio). Em cada ano o lean usa só o 1º turno
do próprio ano (é o que se sabe na noite da apuração). Média de 2º turno = o agregador do modelo (house effects
hierárquicos, recência), refeito com as pesquisas corrigidas.

Pooling do 1º turno: 2014 μ = +7,6 (4 institutos, τ = 0 — movimento de Aécio na última semana); 2018 μ = +0,7
(τ = 4,0; Veritá −7,7, PoderData +6,6); 2022 μ = +1,3 (τ = 4,4; Brasmarket −12,4); **2026 μ = +1,95 (ep 0,48),
τ = 1,0, 14 institutos**.

**Erro da média de pesquisas de 2º turno vs 2º turno real (p.p., fatia do PT):**

| Ano | Variante | Pré-1T (véspera do 1º turno) | Pós-1T (véspera do 2º turno) | RMSE por pesquisa, última semana |
|---|---|---|---|---|
| 2014 | nenhuma | — | +0,69 | 1,74 |
| 2014 | relativa | — | +0,69 | 1,74 |
| 2014 | indústria | — | −6,95 | 7,18 |
| 2014 | plena | — | −6,95 | 7,18 |
| 2018 | nenhuma | +3,52 | −1,14 | 2,97 |
| 2018 | relativa | +2,69 | −1,68 | 3,71 |
| 2018 | indústria | +2,86 | −1,80 | 3,29 |
| 2018 | plena | +2,03 | −2,35 | 3,97 |
| 2022 | nenhuma | +4,71 | +0,10 | 2,08 |
| 2022 | relativa | +3,28 | +0,27 | 2,79 |
| 2022 | indústria | +3,42 | −1,18 | 2,43 |
| 2022 | plena | +1,99 | −1,02 | 2,95 |
| **RMS** | nenhuma | 4,16 | 0,77 | 2,32 |
| **RMS** | relativa | 3,00 | 1,06 | 2,86 |
| **RMS** | indústria | 3,15 | 4,20 | 4,77 |
| **RMS** | plena | **2,01** | 4,28 | 5,03 |

Usando todas as pesquisas de 1º turno da janela (ponderadas por n) em vez da última: pré-1T plena 1,79, pós-1T
pior ainda (RMSE por pesquisa pós-1T 7,0) — mantida a última pesquisa (as anteriores misturam viés com movimento).

Persistência do desvio do instituto (1º turno → última pesquisa de 2º turno, em relação à média de cada turno):
correlação +0,41 (2014, 4 institutos), **−0,30 (2018, 7)**, +0,91 (2022, 11); inclinação −0,38 a +1,02. O
nível da indústria também não passa: 2014 errou +7,6 no 1º turno e +0,6 na última semana do 2º.

**Projeção 1º turno real → 2º turno** (transferência + pré-1T com peso 0,25; `calibrar_2t`): erros
nenhuma +2,68 / −0,26 / +2,83 (RMS 2,25); relativa +2,68 / −0,46 / +2,47 (2,12); indústria +2,68 / −0,42 / +2,50
(2,13); plena +2,68 / −0,62 / +2,15 (**2,01**). Pipeline completo LOEO (`--backtest-2t`, 100 mil simulações,
variante "regionalizada+correcao"): erro nacional +2,31 / −1,85 / +1,63 (antes +2,04 / −1,59 / +2,20; RMS 1,96 →
1,95), UF MAE 2,25 → 2,19, UF RMSE 2,86 → 2,78, Brier UF 0,024 → 0,023, cobertura 80% nas UFs 0,94 → 0,90, 95%
0,99 → 0,975. Neutro no nacional (melhora 2022, piora 2014 — onde só o viés calibrado muda — e 2018).

**Decisão.** Pré-1T: **correção plena adotada** (`PARAM_2T["correcao_institutos_pre_1t"] = "plena"`): melhora a
média pré-1T nos dois anos testáveis (o mecanismo é direto: são as mesmas entrevistas, com a mesma amostra e
ponderação, que erraram o 1º turno) e é neutra no pipeline; a calibração histórica do 2º turno passa a usar as
pesquisas corrigidas do mesmo jeito, para o viés não ser descontado duas vezes. Pós-1T: **não adotada**
(`"nenhuma"`): toda variante piorou a média da véspera do 2º turno e o erro de cada pesquisa em 2014, 2018 e 2022.

**Viés da indústria 1T → 2T com 2026** (`vies_institutos.vies_industria`). Erro do agregador no 1º turno (fatia
do PT): +7,62 (2014), +0,48 (2018), +0,63 (2022), +1,83 (2026). τ0 por máxima verossimilhança marginal
(τ0² = max(0, ē² − s²/n)): 1,71 sem 2026, 2,03 com 2026. Regressão bayesiana do erro da projeção do 2º turno no
erro do 1º turno: erro_2T = b + κ(e1 − 2,64) + ruído (dp 2,5), b ~ N(0; 2,03²), κ ~ N(0; 0,5²): b = +0,91 ± 1,17,
**κ = +0,17 ± 0,32** (sem correção: +0,12 ± 0,33). Viés de 2026 = b + κ(1,83 − 2,64) = **+0,78 ± 1,21 p.p.**
(EB antigo com τ0 = 2: +1,13 sem correção, +0,93 com correção). Com 3 pares (e o de 2014 dominado pela
transferência genérica, não pelas pesquisas), κ é praticamente o prior; o efeito em 2026 é −0,15 p.p.

**Efeito em 2026** (100 mil simulações, TSE 99,94%):

| Variante | Pesquisas pré-1T (Lula) | Viés | P(Lula) | Lula % | p10–p90 |
|---|---|---|---|---|---|
| Antigo | 49,59 | −1,13 | 14,6% | 47,26 | 43,85–50,67 |
| Só correção por instituto | 47,67 | −0,93 | 11,7% | 46,98 | 43,70–50,25 |
| Só viés 1T→2T com 2026 | 49,59 | −1,02 | 15,6% | 47,37 | 43,93–50,80 |
| **Novo (ambos)** | 47,67 | −0,78 | **12,9%** | **47,13** | 43,83–50,43 |
| Alternativa: correção relativa + viés | 49,63 | −0,89 | 16,3% | 47,50 | 44,14–50,86 |
