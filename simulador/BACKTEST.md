# Backtest do simulador: 2014, 2018 e 2022 (véspera)

Gerado por `backtest.py` em 2026-10-03 22:47 UTC; 20.000 simulações por alvo na grade e 40.000 na avaliação final; tempo total 574 s.

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

## Erros das médias de véspera (insumo do prior de viés)

| Ano | T pesquisas | T real | erro T (log) | p2 pesquisas | p2 real | q pesq. véspera 1T | q pesq. véspera 2T | q real |
|---|---|---|---|---|---|---|---|---|
| 2014 | 27,2 | 24,9 | -0,09 | 63,0 | 55,4 | – | 52,3 | 51,6 |
| 2018 | 33,4 | 24,7 | -0,30 | 39,4 | 38,9 | 48,4 | 43,7 | 44,9 |
| 2022 | 12,9 | 8,4 | -0,43 | 53,5 | 52,9 | 55,6 | 51,0 | 50,9 |

T = soma dos candidatos fora os dois primeiros (votos válidos); p2 = PT/(PT+adversário); q = PT no 2º turno. Valores das médias do agregador (house effects hierárquicos, recência, indecisos pelo método escolhido). Erro positivo = pesquisas mais favoráveis ao PT.

Resíduos usados no prior (p.p.; p2 depois da contração média da terceira via estimada sem o próprio ano): {"p2_pp": {"2014": 6.41, "2018": 2.92, "2022": 0.77}, "q_v1_pp": {"2018": 3.52, "2022": 4.71}, "q_v2_pp": {"2014": 0.69, "2018": -1.14, "2022": 0.1}, "T_log": {"2014": -0.09, "2018": -0.302, "2022": -0.429}}

## Calibração (LOEO): cobertura, erros e escores por visão

| Visão | Cob. 50% nac | Cob. 80% nac | Cob. 95% nac | Cob. 50% UF | Cob. 80% UF | Cob. 95% UF | CRPS nac | CRPS UF | Brier nac | Brier UF | Log-loss UF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Neutro (viés 0) | 30,0 | 70,0 | 95,0 | 47,4 | 77,6 | 91,2 | 2,12 | 3,71 | 0,005 | 0,069 | 0,233 |
| Modelo calibrado | 55,0 | 80,0 | 100,0 | 51,6 | 78,6 | 92,2 | 1,83 | 3,61 | 0,014 | 0,066 | 0,224 |
| Viés histórico pleno | 50,0 | 85,0 | 100,0 | 53,2 | 77,6 | 92,2 | 1,69 | 3,58 | 0,050 | 0,065 | 0,218 |
| Calibrado, prior temporal | 45,0 | 70,0 | 100,0 | 51,3 | 76,6 | 91,9 | 2,16 | 3,73 | 0,014 | 0,069 | 0,230 |

Cobertura = % dos resultados reais dentro do intervalo central de 50/80/95% (ideal: 50/80/95). CRPS em p.p. (menor = melhor). Brier/log-loss das probabilidades de vitória (nacional: PT 1º no 1º turno e PT vence; UF: PT 1º na UF no 1º turno e PT vence a UF no 2º turno).

## Nacional, modelo calibrado (LOEO)

| Ano | Alvo | Variável | Real | Mediana | Erro | 80% | 95% | PIT | Em 80% | Em 95% |
|---|---|---|---|---|---|---|---|---|---|---|
| 2014 | 1T | pt1 | 41,6 | 48,4 | 6,8 | 43,7–52,8 | 40,7–55,4 | 0,04 | não | sim |
| 2014 | 1T | opp1 | 33,5 | 31,4 | -2,2 | 26,8–36,0 | 24,2–38,8 | 0,74 | sim | sim |
| 2014 | 1T | T | 24,9 | 19,9 | -5,0 | 15,5–25,6 | 13,5–29,3 | 0,87 | sim | sim |
| 2014 | 1T | margem | 8,0 | 17,1 | 9,0 | 9,5–24,3 | 4,2–28,9 | 0,07 | não | sim |
| 2014 | 1T | p2 | 55,4 | 60,7 | 5,4 | 55,9–65,3 | 52,6–68,3 | 0,08 | não | sim |
| 2014 | 2T (véspera do 2T) | q | 51,6 | 52,6 | 1,0 | 51,2–54,1 | 50,3–55,0 | 0,19 | sim | sim |
| 2018 | 1T | pt1 | 29,3 | 29,6 | 0,4 | 24,6–34,3 | 21,4–37,0 | 0,46 | sim | sim |
| 2018 | 1T | opp1 | 46,0 | 43,1 | -2,9 | 39,3–46,7 | 36,9–48,9 | 0,85 | sim | sim |
| 2018 | 1T | T | 24,7 | 27,1 | 2,4 | 22,0–33,1 | 19,7–37,2 | 0,28 | sim | sim |
| 2018 | 1T | margem | -16,8 | -13,6 | 3,1 | -20,0–-7,0 | -23,9–-2,6 | 0,26 | sim | sim |
| 2018 | 1T | p2 | 38,9 | 40,6 | 1,7 | 35,8–45,3 | 32,6–48,3 | 0,31 | sim | sim |
| 2018 | 2T (véspera do 1T) | q | 44,9 | 45,9 | 1,0 | 42,7–49,2 | 40,8–51,3 | 0,34 | sim | sim |
| 2018 | 2T (véspera do 2T) | q | 44,9 | 43,5 | -1,3 | 42,2–45,0 | 41,3–45,9 | 0,88 | sim | sim |
| 2022 | 1T | pt1 | 48,4 | 46,4 | -2,1 | 41,9–50,7 | 38,9–53,4 | 0,74 | sim | sim |
| 2022 | 1T | opp1 | 43,2 | 42,5 | -0,7 | 38,3–46,7 | 35,5–49,6 | 0,59 | sim | sim |
| 2022 | 1T | T | 8,4 | 11,0 | 2,6 | 8,9–13,6 | 7,9–15,4 | 0,05 | não | sim |
| 2022 | 1T | margem | 5,2 | 3,8 | -1,4 | -4,4–12,0 | -10,2–17,4 | 0,59 | sim | sim |
| 2022 | 1T | p2 | 52,9 | 52,2 | -0,7 | 47,5–56,7 | 44,2–59,8 | 0,58 | sim | sim |
| 2022 | 2T (véspera do 1T) | q | 50,9 | 53,3 | 2,4 | 49,6–56,9 | 47,2–59,2 | 0,19 | sim | sim |
| 2022 | 2T (véspera do 2T) | q | 50,9 | 51,2 | 0,2 | 49,8–52,6 | 48,9–53,4 | 0,41 | sim | sim |

pt1/opp1 = válidos do PT/adversário no 1º turno; T = terceira via; margem = PT − adversário; q = PT no 2º turno.

| Ano | Alvo | Evento | P(modelo) | Ocorreu | Brier |
|---|---|---|---|---|---|
| 2014 | 1T | PT 1º no 1º turno | 0,991 | 1 | 0,000 |
| 2014 | 2T (véspera do 2T) | PT vence o 2º turno | 0,983 | 1 | 0,000 |
| 2018 | 1T | PT 1º no 1º turno | 0,011 | 0 | 0,000 |
| 2018 | 2T (véspera do 1T) | PT vence a eleição | 0,060 | 0 | 0,004 |
| 2018 | 2T (véspera do 2T) | PT vence o 2º turno | 0,000 | 0 | 0,000 |
| 2022 | 1T | PT 1º no 1º turno | 0,733 | 1 | 0,071 |
| 2022 | 2T (véspera do 1T) | PT vence a eleição | 0,878 | 1 | 0,015 |
| 2022 | 2T (véspera do 2T) | PT vence o 2º turno | 0,856 | 1 | 0,021 |

## UFs, modelo calibrado (LOEO)

| Ano | Alvo | Var. | UFs | Erro abs. médio | Erro médio (viés) | Cob. 50% | Cob. 80% | Cob. 95% | CRPS |
|---|---|---|---|---|---|---|---|---|---|
| 2014 | 1T | opp1 | 28 | 6,6 | -0,1 | 35,7 | 75,0 | 92,9 | 4,65 |
| 2014 | 1T | pt1 | 28 | 8,3 | 4,3 | 39,3 | 64,3 | 82,1 | 6,04 |
| 2014 | 2T (véspera do 2T) | q | 28 | 4,3 | -0,5 | 50,0 | 71,4 | 89,3 | 3,12 |
| 2018 | 1T | opp1 | 28 | 6,1 | -3,4 | 32,1 | 60,7 | 78,6 | 4,51 |
| 2018 | 1T | pt1 | 28 | 6,1 | -1,3 | 46,4 | 71,4 | 85,7 | 4,44 |
| 2018 | 2T (véspera do 1T) | q | 28 | 6,2 | 0,9 | 35,7 | 64,3 | 89,3 | 4,38 |
| 2018 | 2T (véspera do 2T) | q | 28 | 3,5 | -1,3 | 42,9 | 78,6 | 96,4 | 2,41 |
| 2022 | 1T | opp1 | 28 | 3,8 | -0,9 | 82,1 | 92,9 | 100,0 | 2,81 |
| 2022 | 1T | pt1 | 28 | 3,5 | -2,7 | 67,9 | 96,4 | 100,0 | 2,76 |
| 2022 | 2T (véspera do 1T) | q | 28 | 4,3 | 2,7 | 57,1 | 92,9 | 100,0 | 3,01 |
| 2022 | 2T (véspera do 2T) | q | 28 | 1,8 | 0,2 | 78,6 | 96,4 | 100,0 | 1,55 |

| Ano | Alvo | Evento | UFs | Brier | Log-loss | % UFs com favorito certo |
|---|---|---|---|---|---|---|
| 2014 | 1T | PT 1º na UF (1T) | 28 | 0,199 | 0,608 | 60,7 |
| 2014 | 2T (véspera do 2T) | PT vence a UF (2T) | 28 | 0,016 | 0,099 | 100,0 |
| 2018 | 1T | PT 1º na UF (1T) | 28 | 0,075 | 0,241 | 89,3 |
| 2018 | 2T (véspera do 1T) | PT vence a UF (2T) | 28 | 0,043 | 0,165 | 96,4 |
| 2018 | 2T (véspera do 2T) | PT vence a UF (2T) | 28 | 0,021 | 0,076 | 100,0 |
| 2022 | 1T | PT 1º na UF (1T) | 28 | 0,054 | 0,214 | 96,4 |
| 2022 | 2T (véspera do 1T) | PT vence a UF (2T) | 28 | 0,065 | 0,224 | 92,9 |
| 2022 | 2T (véspera do 2T) | PT vence a UF (2T) | 28 | 0,056 | 0,164 | 92,9 |

Maiores erros por UF (mediana − real, p.p.):

| Ano | Alvo | Var. | UF | Real | Mediana | Erro | PIT | Em 95% |
|---|---|---|---|---|---|---|---|---|
| 2022 | 1T | pt1 | ZZ | 47,2 | 21,4 | -25,8 | 0,953 | sim |
| 2022 | 1T | opp1 | ZZ | 41,6 | 66,2 | 24,6 | 0,053 | sim |
| 2014 | 1T | pt1 | DF | 23,0 | 47,2 | 24,2 | 0,002 | não |
| 2014 | 1T | pt1 | ZZ | 18,3 | 41,9 | 23,6 | 0,018 | não |
| 2022 | 2T (véspera do 1T) | q | ZZ | 51,3 | 30,7 | -20,6 | 0,918 | sim |
| 2014 | 1T | opp1 | AC | 29,1 | 48,3 | 19,3 | 0,009 | não |
| 2014 | 1T | pt1 | RJ | 35,6 | 52,9 | 17,3 | 0,012 | não |
| 2014 | 1T | pt1 | SP | 25,8 | 41,9 | 16,1 | 0,007 | não |
| 2018 | 1T | opp1 | RJ | 59,8 | 43,7 | -16,1 | 0,998 | não |
| 2018 | 1T | pt1 | PI | 63,4 | 47,4 | -16,0 | 0,995 | não |
| 2014 | 1T | pt1 | PE | 44,2 | 60,1 | 15,9 | 0,030 | sim |
| 2018 | 2T (véspera do 1T) | q | AC | 22,8 | 38,4 | 15,6 | 0,003 | não |

## Histograma PIT (todas as variáveis, nacional + UF, modelo calibrado)

| Faixa | 0.0–0.1 | 0.1–0.2 | 0.2–0.3 | 0.3–0.4 | 0.4–0.5 | 0.5–0.6 | 0.6–0.7 | 0.7–0.8 | 0.8–0.9 | 0.9–1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| n | 35 | 20 | 36 | 34 | 44 | 36 | 19 | 30 | 39 | 35 |

Um modelo calibrado tem PIT uniforme (barras iguais). Barras altas nas pontas = intervalos estreitos; acúmulo num lado = viés. Os PITs das UFs de um mesmo ano são fortemente correlacionados (o erro nacional é comum), então o histograma tem muito menos informação independente do que o número de pontos sugere.

## Escolha dos parâmetros (grade + leave-one-election-out)

Escolha por blocos: entre as combinações cuja cobertura média é de pelo menos 75% no intervalo de 80% e 90% no de 95% (evita intervalos estreitos demais), a de menor CRPS médio; cada bloco usa os parâmetros já escolhidos dos anteriores. 'Fora da amostra' = CRPS do ano deixado de fora com os parâmetros escolhidos nos outros anos; 'na amostra' = com os parâmetros escolhidos em todos os anos.

**Bloco nac1** — escolhido: `{"erro_nacional_1t.dp_p2_pp": 4.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 2.0}` (CRPS médio 1,922).
Sem fixar o encolhimento, a grade escolheria `{"erro_nacional_1t.dp_p2_pp": 3.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 4.0}` (CRPS 1,860); o encolhimento fica fixo por princípio (ver abaixo).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2014 | {"erro_nacional_1t.dp_p2_pp": 3.0, "erro_nacional_1t.gl_t": 10.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 2.0} | 3,150 | 3,078 |
| 2018 | {"erro_nacional_1t.dp_p2_pp": 3.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.2, "vies.tau0_p2_pp": 2.0} | 1,562 | 1,406 |
| 2022 | {"erro_nacional_1t.dp_p2_pp": 5.0, "erro_nacional_1t.gl_t": 5.0, "terceira_via.dp_log": 0.1, "vies.tau0_p2_pp": 2.0} | 1,344 | 1,282 |

**Bloco nac2** — escolhido: `{"erro_2t.dp_q_pp_vespera_1t": 2.0, "erro_2t.peso_pesquisas_vespera_1t": 0.3, "vies.tau0_q_pp": 2.0}` (CRPS médio 1,083).
Sem fixar o encolhimento, a grade escolheria `{"erro_2t.dp_q_pp_vespera_1t": 2.0, "erro_2t.peso_pesquisas_vespera_1t": 0.5, "vies.tau0_q_pp": null}` (CRPS 0,813); o encolhimento fica fixo por princípio (ver abaixo).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2018 | {"erro_2t.dp_q_pp_vespera_1t": 3.0, "erro_2t.peso_pesquisas_vespera_1t": 0.3, "vies.tau0_q_pp": 2.0} | 0,800 | 0,774 |
| 2022 | {"erro_2t.dp_q_pp_vespera_1t": 2.0, "erro_2t.peso_pesquisas_vespera_1t": 0.3, "vies.tau0_q_pp": 2.0} | 1,392 | 1,392 |

**Bloco nac3** — escolhido: `{"erro_2t.dp_q_pp_vespera_2t": 1.5}` (CRPS médio 0,569).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2014 | {"erro_2t.dp_q_pp_vespera_2t": 1.5} | 0,600 | 0,600 |
| 2018 | {"erro_2t.dp_q_pp_vespera_2t": 1.0} | 0,873 | 0,827 |
| 2022 | {"erro_2t.dp_q_pp_vespera_2t": 2.5} | 0,384 | 0,281 |

**Bloco uf** — escolhido: `{"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 4.5}` (CRPS médio 3,676).

| Ano deixado de fora | Escolha sem ele | CRPS fora | CRPS na amostra |
|---|---|---|---|
| 2014 | {"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 1.5} | 4,627 | 4,573 |
| 2018 | {"estados.dp_uf_minimo_pp": 3.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 1.5} | 3,985 | 3,928 |
| 2022 | {"estados.dp_uf_minimo_pp": 8.0, "estados.dp_pesquisa_piso_1t_pp": 3.0, "estados.dp_pesquisa_piso_2t_pp": 2.0, "estados.dp_regional_pp": 4.5} | 2,795 | 2,527 |

Sensibilidade ao encolhimento do viés do 1º turno (tau0, p.p.; LOEO, demais parâmetros fixos):

| tau0 p2 | CRPS nacional 1T |
|---|---|
| 0,0 | 2,102 |
| 1,0 | 2,025 |
| 2,0 | 1,922 |
| 4,0 | 1,863 |
| ∞ (sem encolhimento) | 1,873 |

Sensibilidade ao encolhimento do viés do 2º turno projetado na véspera do 1º (tau0, p.p.):

| tau0 q | CRPS nacional 2T |
|---|---|
| 0,0 | 1,264 |
| 1,0 | 1,198 |
| 2,0 | 1,083 |
| 4,0 | 0,938 |
| ∞ (sem encolhimento) | 0,833 |

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
