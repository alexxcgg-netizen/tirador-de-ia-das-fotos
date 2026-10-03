# Simulador Monte Carlo da eleição presidencial de 2026 (por UF)

Simulador estado a estado da eleição presidencial brasileira de 2026 (1º turno em
4/10/2026; eventual 2º turno em 25/10/2026), com 500.000 simulações por visão,
**backtest em 2014, 2018 e 2022** e um painel web estático.

Dados até **3/10/2026** (véspera do 1º turno, noite). Os números vêm das notas de
pesquisa em `research_notes/` e dos relatórios em `reports/`; cada linha dos CSVs
em `data/` traz fonte e data.

## Como rodar

```bash
pip install numpy pandas pytest                 # Python 3.10+
python simulador/backtest.py                    # grade + LOEO + BACKTEST.md + data/backtest_saida.json (~13 min)
python simulador/rodar.py                       # 500.000 simulações x 3 visões -> web/resultados.json (~45 s)
python simulador/publicar.py                    # cópia para artifact em web_publicar/ (+ resultados_alt.json)
python -m pytest simulador/tests -q             # testes (~25 s)
cd simulador/web && python -m http.server 8000  # abrir http://localhost:8000
```

`backtest.py --rapido` pula a grade e só avalia com os parâmetros de `premissas.json`.
O painel precisa de HTTP (o `fetch("resultados.json")` é relativo). Chart.js 4.4.1 vem do
cdnjs (versão fixa, com SRI) e cai para o jsDelivr se o cdnjs falhar; sem a biblioteca,
cartões, mapa e tabelas continuam funcionando.

**Tempo medido** (4 vCPUs, NumPy 2.4, float32, lotes de 100 mil): 38,6 s para 3 visões ×
500.000 simulações (1,5 milhão de eleições, 28 unidades × 7 candidatos) + 2,5 s de base e
priors; backtest completo (grade + LOEO aninhado) 745 s.

## Estrutura

```
simulador/
  premissas.json      parâmetros, cada um com origem (fonte / cálculo / backtest / inferência) e nota
  modelo.py           motor genérico: agregação, house effects hierárquicos, médias por UF, simulação
  backtest.py         roda o motor na véspera de 2014/2018/2022; métricas, grade, LOEO, BACKTEST.md
  rodar.py            2026: 3 visões -> web/resultados.json (inclui validação e segmentos)
  segmentos.py        prior demográfico por UF, ajuste de comparecimento, voto por segmento (SEGMENTOS.md)
  publicar.py         gera web_publicar/ (página sem <html>/<head>/<body>, para artifact)
  BACKTEST.md         relatório do backtest (tabelas)
  data/               pesquisas 2026 e históricas, resultados TSE, rejeição, eventos, segmentos
  web/                painel (index.html) + resultados.json
  tests/              pytest (modelo, backtest, segmentos)
  screenshots/        capturas do painel (desktop/celular, claro/escuro)
```

## Resultados (rodada de 3/10/2026, 500.000 simulações por visão, semente 20261004)

| Probabilidade | **Modelo calibrado** (principal) | Neutro (viés 0) | Viés histórico pleno | Polymarket (3/10) |
|---|---|---|---|---|
| Lula vence a eleição | **35,7%** | 45,5% | 30,4% | 40,1% |
| Flávio Bolsonaro vence a eleição | **64,3%** | 54,5% | 69,6% | 58,8% |
| Decidida no 1º turno | 20,8% (Lula 4,8; Flávio 16,0) | 15,7% (9,4; 6,3) | 32,0% (3,4; 28,6) | 5,3% |
| Lula em 1º no 1º turno | 34,1% | 56,3% | 23,5% | 71,4% |
| 1º turno Lula, % válidos (p10–p90) | 44,3 (40,1–48,5) | 46,0 (42,1–49,9) | 43,2 (38,8–47,7) | |
| 1º turno Flávio, % válidos (p10–p90) | 46,8 (42,5–51,0) | 45,1 (41,1–49,1) | 48,0 (43,5–52,6) | |
| 2º turno Lula, % válidos (p10–p90) | 48,7 (43,9–53,6) | 49,6 (44,9–54,3) | 48,2 (43,2–53,2) | |

Erro de Monte Carlo ≤ 0,07 p.p. UFs disputadas no calibrado (P(Lula vence o 2º turno na UF)):
PA 56%, AM 47%, TO 36%, MG 34%, AP 13%, RS 11%, SP 10%, RJ 7%, ES 7%, DF 5%, AL 78%;
demais UFs do Nordeste ≥ 98%; Sul/Centro-Oeste/RO/AC/RR ≤ 11%.

**Leitura.** A média das pesquisas (efeitos de instituto, véspera incluída) dá Lula com 50,8% dos
votos dos dois primeiros no 1º turno e 49,6% no 2º turno: empate. Na véspera de 2014, 2018 e 2022 a
mesma média ficou mais favorável ao PT do que a urna no 1º turno (p2 depois da contração esperada da
terceira via: +6,2 / +2,7 / +0,6 p.p.); na véspera do 2º turno o erro foi pequeno e de sinal misto
(+0,5 / −1,3 / −0,1). O modelo calibrado encolhe o erro do 1º turno para zero (prior N(0, 2²)) e
chega a um viés de +1,5 ± 1,4 p.p. em p2, já descontado o efeito de comparecimento e ponderado pela
exposição dos institutos; no 2º turno o viés das pesquisas fica perto de zero (−0,3 ± 0,8), e o que
pesa é o 1º turno simulado (via de transferência) e a deriva de três semanas, tratada como erro
simétrico (dp 6 p.p. em q, escolhido no backtest). A regra é simétrica: erros históricos com sinal
oposto produziriam correção para o outro lado.

## Metodologia

### 1. Agregação nacional (`modelo.agregar`, `house_effects_hier`)
- Cada pesquisa vira **p2** = PT/(PT + adversário) no 1º turno, **m_k** = válidos de cada menor
  (só pesquisas com lista completa) e **q** = PT no 2º turno.
- **House effects hierárquicos:** `logito(y) = semana + h_instituto + e`, h ~ N(0, τ²), com τ e o
  ruído por pesquisa estimados por máxima verossimilhança restrita numa grade (2026: τ = 1,5 p.p.
  no 1º turno, 1,0 no 2º; o ruído ficou no limite inferior da grade, 0,5 p.p.). h = média posterior
  com dp; instituto com 1 pesquisa fica perto de zero. 1º turno (p.p. pró-Lula): MDA +2,9, Quaest
  +1,3, Indexa +1,1, Datafolha +0,6, Atlas +0,2, Vox −0,7, PoderData −1,1, Gerp −1,1, Veritá −1,4,
  Palver −1,9, Futura −1,9.
- **Média final:** última pesquisa de cada instituto em 14 dias, peso √min(n, 3000) × e^(−dias/7),
  corrigida pelo house effect; a incerteza da média (dp posterior dos h) entra na simulação.
- **Higiene:** deduplicação por registro TSE e por instituto+data+números (nenhuma duplicata no
  arquivo atual; a suposta duplicata da AtlasIntel era a mesma rodada citada por dois veículos);
  pesquisas de véspera incluídas (Datafolha 3/10 em votos totais, Quaest 2–3/10, Futura 2–3/10,
  Palver 3/10, Veritá consolidada 20–25/9, PoderData, MDA, Vox, IFP, Gerp) e 11 estaduais de véspera
  (Datafolha SP/MG/DF, AtlasIntel PA/PI/BA, Veritá AC/AL/AP/GO/DF); **Gerp 30/9–2/10 sinalizada**
  (linha corrigida em 3/10; peso 0,5).
- **Indecisos:** proporcionais. A divisão pelo "espaço" (100 − rejeição − intenção), na linha de
  Pereira & Nunes (2024), foi validada no backtest e **não melhorou** (2018 1T: erro +1,6 contra
  +0,5; 2022 2T: +0,3 contra +0,1); fica como sensibilidade (p2 50,75 contra 50,80). Nenhuma pesquisa
  de 2026 perguntou 2ª opção no 1º turno. A **rejeição** (Datafolha 45/45; a métrica da Quaest não é
  misturada) é **teto suave** no 2º turno (ativo em ~3–4% das simulações).

### 2. Estados
- **Prior:** nacional + 0,85 × lean de 2022 em logito; no 1º turno, misturado ao prior demográfico de
  `segmentos.py` (0,8 × simples + 0,2 × demográfico; dp fora do tempo ~7,0 p.p.; 2º turno ~4,5 p.p.).
  Como AP e GO passaram a ter pesquisa de 2º turno (Veritá), o prior demográfico do 2º turno não é
  mais necessário em nenhuma UF. Exterior: dp 15 p.p.
- **Pesquisas estaduais:** variância `1,5·p(1−p)/n + piso²` × (1 + dias/14), piso 3 p.p. (1º) e
  2 p.p. (2º), escolhidos no backtest. Médias deslocadas para que o agregado das UFs reproduza o
  nacional (−1,5 p.p. no 1º turno, −1,1 no 2º).

### 3. Erro estruturado (por simulação)
1. **Margem PT x adversário:** t de Student (5 gl), dp 4,0 p.p. em p2, + incerteza da média.
2. **Terceira via combinada:** erro em log com média −0,25 (contração de ~22%, prior empírico-bayesiano
   dos erros −0,09/−0,30/−0,43 de 2014/18/22) e dp 0,10 (t); os votos que saem vão para Lula/Flávio
   pela matriz de transferência (Quaest 24–27/9, Dirichlet α = 30); se os menores crescem, os votos
   saem de Lula/Flávio na proporção de cada um.
3. **Resíduo por candidato menor:** log-normal nacional e por UF (dp 0,15), mexe na composição.
4. **Viés da indústria** (calibrado/pleno): posterior empírico-bayesiana × exposição média dos
   institutos (AtlasIntel 0,6 ± 0,2 por ponderar por voto passado, documento primário; demais 1,0 com
   dp 0,15–0,3; média ponderada 0,98). Correlação 0,6 entre o viés dos dois turnos.
5. **Subnacional:** eixo NE/N x S/CO (1,5 p.p.), região (3 p.p.), UF (t, ≥ 3 p.p.), centrados (pesos de
   votos válidos) para não alterar o agregado nacional.
6. **2º turno:** 0,5 × (pesquisas de 2º turno + erro t dp 6 p.p., ρ = 0,5 com o 1º turno + viés) +
   0,5 × (1º turno simulado + matriz de transferência), em logito.
7. **Comparecimento:** abstenção e brancos/nulos de 2022 por UF + ruído; na visão calibrada, o **ajuste
   de comparecimento por segmento** (−0,37 p.p. em p2, −0,25 em q; `segmentos.py`), somado depois da
   calibração nacional (se somado antes, a calibração o anularia). Para não contar duas vezes, os erros
   históricos usados no prior calibrado são descontados do efeito de comparecimento medido em 2022
   (0,18/0,19 p.p.) antes do encolhimento: o efeito de comparecimento é tratado como medido (TSE), não
   encolhido; o resto do erro histórico é encolhido. A visão pleno não aplica o ajuste.

### 4. Visões
- **Modelo calibrado (principal):** integra sobre a incerteza do viés (encolhido, com exposição por instituto).
- **Neutro:** viés 0 (mantém a contração usual da terceira via e todo o erro simétrico).
- **Viés histórico pleno:** média dos erros de 2014/18/22 sem encolhimento, exposição 1.

## Backtest (detalhes em BACKTEST.md)

Véspera de cada turno, só com pesquisas daquele momento; prior de viés **leave-one-election-out**;
inclinação e dp do prior estadual de cada ano estimados só com eleições anteriores; exterior fora das
métricas por UF.

| Visão | Cobertura 50/80/95% nacional | Cobertura 50/80/95% UF | CRPS nac / UF | Brier UF |
|---|---|---|---|---|
| **Calibrado, LOEO aninhado** (parâmetros e prior sem o ano) | 40 / 75 / 95 | 52 / 81 / 93 | 2,08 / 3,55 | 0,058 |
| Calibrado (parâmetros com os 3 anos) | 45 / 80 / 100 | 47 / 81 / 94 | 1,94 / 3,44 | 0,057 |
| Neutro | 30 / 75 / 100 | 43 / 80 / 93 | 2,23 / 3,52 | 0,060 |
| Viés pleno | 50 / 85 / 100 | 49 / 81 / 94 | 1,76 / 3,39 | 0,053 |
| Calibrado, prior só com anos anteriores | 40 / 70 / 100 | 47 / 80 / 93 | 2,27 / 3,59 | 0,059 |

- 20 quantidades nacionais e ~300 por UF; os pontos de um mesmo ano são correlacionados.
- Parâmetros por blocos (grade com restrição de cobertura ≥ 75%/90% + menor CRPS). Fixos por
  princípio: encolhimento do viés (τ0 = 2 p.p.; a grade sempre prefere encolher menos com 2–3 eleições
  do mesmo sinal) e peso 0,5 entre as duas vias do 2º turno (a grade, com 2 eleições, escolheria 0,1–0,3).
- Erro absoluto médio da mediana: 2,8 p.p. nacional, 4,8 p.p. por UF. Brier das probabilidades
  nacionais: neutro 0,012, calibrado 0,017, pleno 0,041 (8 eventos; diz pouco).
- Validação dos indecisos e da escolha do adversário (2014: Aécio era o não-PT mais votado na média de
  véspera por instituto, mas não na média simples da última semana) em BACKTEST.md.

## Comparação com o modelo alternativo (`modelo_alternativo/`)
Modelo independente (filtro de Kalman, bootstrap dos erros reais de 2014/18/22, swing uniforme sem
pesquisas estaduais). Médias de pesquisas quase idênticas (p2 50,7–50,8; q 49,5–49,6). Neutros: 45,5%
(principal) x 49,4% (alternativo) para Lula; viés pleno/histórico: 30,4% x 18,9%. A maior diferença é a
decisão no 1º turno (principal 16–21%, alternativo 36–40%): o bootstrap repete o erro de margem de
2014 (~10 p.p.) como ele foi; sem 2014 o alternativo dá ~0%. No 2º turno, o histórico do alternativo
aplica o erro médio de 2º turno visto na véspera do 1º (que inclui a deriva de 2018 e 2022); o principal
trata essa deriva como erro simétrico. Por UF, as maiores diferenças vêm das pesquisas estaduais
(RJ, AP, AL, TO, SP), que o principal usa e o alternativo não. O painel mostra os dois lado a lado.

## O que mudou em relação à versão anterior e por quê
- **Backtest** (antes inexistente) calibra σ nacional, σ estadual, gl e contração da terceira via;
  mostrou que o modelo anterior era estreito demais nas UFs (cobertura 95% ~86%; agora 93%).
- **Erro estruturado** (margem + terceira via + resíduo) no lugar de erro i.i.d. por candidato.
- **Viés com incerteza** (posterior empírica, encolhida, por instituto) no lugar do cenário binário;
  Neutro e Pleno ficam como sensibilidade. A "média 50/50" saiu.
- **House effects hierárquicos** (τ estimado) no lugar do ridge com dp fixo.
- **Estados:** pisos, fator regional (1,5 → 3 p.p.) e dp do prior (4 → 7,0/4,5 p.p.) calibrados;
  SP passa de 3,8% para 10–14% para Lula.
- **2º turno:** erro de 2,0 → 6,0 p.p. na projeção feita na véspera do 1º turno (deriva de 3 semanas),
  pesos 0,5/0,5 entre pesquisas e transferência.
- **Segmentos:** prior demográfico, ajuste de comparecimento sem dupla contagem, dados no painel.
- **Dados:** pesquisas de véspera nacionais e estaduais, Gerp sinalizada, deduplicação.
- **Cores:** Flávio passou de verde para laranja-queimado (verde lembra a campanha bolsonarista).

## Revisão independente (red team) e correções
Uma sessão revisora independente apontou, entre outros: (1) prior estadual do backtest com inclinação
0,85 e dp tirados de 2018→2022 (vazamento) → agora estimados por ano só com eleições anteriores;
(2) tabela "LOEO" parcialmente dentro da amostra → adicionada a validação aninhada e o texto corrigido;
(3) adversário de 2014 vindo do arquivo → conferido pela média de véspera, fragilidade documentada;
(4) viés do 2º turno estimado com a deriva entre turnos (2 casos) → viés do 2º turno agora vem dos
erros da véspera do 2º turno, e a deriva entra como erro simétrico; (5) parâmetros na borda da grade →
grades ampliadas, limites inferiores dos pisos estaduais pela literatura, peso do 2º turno fixo;
(6) exposição de Quaest 0,9 com fonte não confirmada → 1,0; (7) README desatualizado → reescrito;
(8) `lula_vence_2t_se_houver` não condicional → corrigido; (9) contração "negativa" e centragem dos
erros estaduais → corrigidas; (10) exterior nas métricas por UF → separado; (11) verde para Flávio e
selos coloridos → paleta e selos neutros. Mantido, com justificativa: o ajuste de comparecimento é
aplicado por inteiro (medido nos dados do TSE), e só o restante do erro histórico é encolhido.

## Limitações
- **Poucas eleições:** 3 no 1º turno, 2 no 2º turno projetado na véspera do 1º. O prior de viés e as
  coberturas são estimativas grosseiras.
- O erro de 2022 no 1º turno, medido pela média ampla (incluindo institutos que erraram para o outro
  lado), foi pequeno (+0,6 p.p. em p2); o viés calibrado depende muito de 2014 e 2018.
- **Decisão no 1º turno** (21% calibrado; 16% neutro) fica bem acima dos mercados (~5%): caudas t com
  dp de 4 p.p. escolhido no backtest; o modelo alternativo dá ainda mais (36%).
- Pesquisas estaduais: poucas rodadas por UF; AP sem n na Quaest.
- Matriz de transferência de subamostras pequenas de uma pesquisa; no backtest usou-se a matriz
  implícita das pesquisas pareadas.
- Prior demográfico e ajuste de comparecimento não testados no backtest (seriam vazamento).
- AtlasIntel final, Veritá 26/9–2/10 e Gerp 1–3/10 não estavam publicadas na coleta.
- O 2º turno é projetado em 3/10; fatos entre os turnos não estão no modelo.

## Neutralidade
O modelo usa apenas pesquisas registradas, resultados oficiais do TSE e parâmetros documentados
com origem. O viés calibrado sai de uma regra empírica aplicada a qualquer erro histórico, nos dois
sentidos. As três visões aparecem sempre lado a lado com os mercados. Os eventos da linha do tempo
são factuais, com fonte, auditados para equilíbrio (`data/auditoria_neutralidade.md`) e não mudam
nenhum número. As cores (violeta e laranja-queimado) foram escolhidas para não lembrar as dos
partidos ou das campanhas e foram validadas para daltonismo e contraste.
