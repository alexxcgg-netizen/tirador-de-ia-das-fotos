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
python simulador/gerar_segundo_turno_json.py    # notas do 2º turno e do risco democrático -> web/segundo_turno_conteudo.json
python simulador/publicar.py                    # cópia para artifact em web_publicar/ (+ resultados_alt.json)
python simulador/resultado_1t.py --rodar-tudo   # noite da apuração: TSE -> avaliação -> 2º turno -> publicar (~30 s)
python simulador/resultado_1t.py --ensaio-2022  # ensaio do pipeline com 2022 (+ validação 2014/2018) (~75 s)
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
  resultado_1t.py     noite da apuração: resultado TSE, avaliação (AVALIACAO_1T.md) e 2º turno condicionado
  transferencia_regional.py  2º turno: transferência dependente do lean da UF; comparecimento entre turnos
  vies_institutos.py  2º turno: erro de cada instituto no 1º turno (partial pooling) -> correção das pesquisas
                      de 2º turno; viés da indústria 1T -> 2T (backtest: --backtest-institutos)
  BACKTEST.md         relatório do backtest (tabelas)
  data/               pesquisas 2026 e históricas, resultados TSE, rejeição, eventos, segmentos
  web/                painel (index.html) + resultados.json
  tests/              pytest (modelo, backtest, segmentos)
  screenshots/        capturas do painel (desktop/celular, claro/escuro)
```

## Resultados (rodada de 3/10/2026, 500.000 simulações por visão, semente 20261004)

| Probabilidade | **Modelo calibrado** (principal) | Neutro (viés 0) | Viés histórico pleno | Polymarket (3/10) |
|---|---|---|---|---|
| Lula vence a eleição | **35,9%** | 45,7% | 30,5% | 40,1% |
| Flávio Bolsonaro vence a eleição | **64,1%** | 54,3% | 69,5% | 58,8% |
| Decidida no 1º turno | 21,4% (Lula 5,1; Flávio 16,3) | 16,4% (9,9; 6,5) | 32,9% (3,5; 29,3) | 5,3% |
| Lula em 1º no 1º turno | 34,5% | 56,5% | 23,6% | 71,4% |
| 1º turno Lula, % válidos (p10–p90) | 44,4 (40,3–48,6) | 46,1 (42,2–50,0) | 43,3 (38,9–47,8) | |
| 1º turno Flávio, % válidos (p10–p90) | 46,8 (42,6–51,1) | 45,2 (41,2–49,2) | 48,1 (43,6–52,7) | |
| 2º turno Lula, % válidos (p10–p90) | 48,7 (43,9–53,6) | 49,6 (44,9–54,4) | 48,2 (43,2–53,2) | |

Rodada refeita na madrugada de 4/10 com a pesquisa final da AtlasIntel (27/9–2/10, BR-00999/2026, publicada
em votos válidos: Lula 47,0, Flávio 44,1; 2º turno 50,1 x 49,9): mudanças ≤ 0,6 p.p. nas probabilidades.
Erro de Monte Carlo ≤ 0,07 p.p. UFs disputadas no calibrado (P(Lula vence o 2º turno na UF)):
PA 56%, AM 47%, TO 36%, MG 35%, AP 13%, RS 11%, SP 11%, RJ 7%, ES 7%, DF 5%, AL 78%;
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

## Noite da apuração: `resultado_1t.py`

```bash
python simulador/resultado_1t.py --rodar-tudo                 # repetir à vontade enquanto a apuração avança
python simulador/resultado_1t.py --rodar-tudo --n 100000      # mais rápido
python simulador/resultado_1t.py --rodar-tudo --fonte manual  # TSE fora do ar: data/resultado_1t_manual.csv
```

**a) Resultado oficial.** O código da eleição vem do arquivo público de configuração do TSE
(`https://resultados.tse.jus.br/oficial/comum/config/ele-c.json`): ciclo `ele2026`, eleição federal do 1º turno
**6257** (2º turno 6258). Presidente, Brasil/UF/exterior:
`https://resultados.tse.jus.br/oficial/ele2026/6257/dados/{uf}/{uf}-c0001-e006257-u.json` (formato "u", o mesmo
de 2024; na madrugada de 4/10 já publicado, com zeros). O padrão de 2022 (`dados-simplificados/...-r.json`)
devolve 404 hoje; o leitor entende os dois formatos. Lê % de seções totalizadas (`pst`), eleitorado,
comparecimento, abstenção, brancos, nulos, válidos e votos por candidato (por número: 13 Lula, 22 Flávio,
55 Caiado, 70 Cury, 30 Zema, 14 Renan; demais em "Outros"; votos anulados sub judice ficam fora dos válidos).
Fallbacks: última leitura gravada em `data/tse_1t_2026/` (fora do git) e CSV manual
(`uf,pst,eleitorado,comparecimento,abstencao,validos,brancos,nulos,lula,flavio,caiado,cury,zema,renan,outros`),
preenchido de qualquer fonte de apuração (G1, UOL etc.; não há JSON público estável desses portais que desse para
testar antes da eleição). UF sem nenhuma seção: previsão de véspera do modelo calibrado. Antes da 1ª parcial,
grava status "aguardando".

**UF com apuração parcial: projeção por município** (antes: fatias das seções apuradas e válidos por
`válidos / pst`, o que supõe que o resto da UF vota como o que já foi apurado; em 2022 Bolsonaro liderou até
~67% porque o Centro-Sul totalizou antes). O TSE publica, por UF, a abrangência
`.../dados/{uf}/{uf}-e006257-ab.json` (eleitorado `te` e eleitorado das seções totalizadas `est` de cada
município; ~27 arquivos) e, por município, `.../dados/{uf}/{uf}{cdmun:05d}-c0001-e006257-u.json` (mesmo
formato "u" da UF, com votos por candidato). Códigos de município do TSE de 2026 = os de 2022 (5.751 de 5.757
casam; só um município novo no MT e 6 cidades do exterior não têm referência). Para cada município:
- votos válidos restantes = (`te` − `est`) × taxa de válidos por eleitor de 2022 no município × variação da
  taxa observada nos municípios já apurados (logaritmo, encolhida para a nacional);
- fatias do restante = as já apuradas no município (se parcial); senão a fatia do PT em 2022 no município
  deslocada (logito) pelo swing da UF, e a de Flávio entre os não-PT = a de Bolsonaro em 2022 deslocada do mesmo
  jeito; os menores dividem o resto como na UF apurada. Swing da UF = média dos municípios apurados ponderada
  por √válidos, encolhida para o swing nacional (k = 3 municípios efetivos), com inclinações no porte (log do
  eleitorado) e na fatia do PT em 2022 estimadas dentro das UFs com o país todo (ridge 0,5) e sem extrapolar
  para fora da faixa dos apurados;
- incerteza (dp da fatia do PT na UF, usada no lugar do ruído antigo na simulação do 2º turno): ruído municipal
  + erro comum do swing (piso 0,15 em logito) + extrapolação (municípios fora da faixa dos apurados); vai a zero
  com a apuração.
Só municípios com seções totalizadas e que mudaram desde a última leitura são baixados (24 em paralelo,
~35 arquivos/s; cache em `data/tse_1t_2026/municipios/`; prazo de 150 s). Falha em qualquer arquivo de uma UF,
ou soma dos municípios incoerente com o arquivo da UF (> 25%), põe a UF de volta no método antigo;
`--sem-municipios` desliga tudo. `resultados_2t.json` registra o método de cada UF, o swing e o nacional pelo
método antigo (`meta.projecao_parcial`). Referência: `data/municipios_2022.csv` (aptos, comparecimento,
válidos, votos de Lula e Bolsonaro por município, agregados de `votacao_candidato_munzona_2022` e
`detalhe_votacao_munzona_2022` do TSE; somas batem com o total nacional).

**Validação (replay de 2022, `--replay-2022`, `data/replay_projecao_2022.json`):** reapuração do 1º turno de
2022 com a zona eleitoral como unidade (`data/replay_munzona_2022.csv`), referência 2018 por município
(`data/municipios_2018.csv`, Haddad/Bolsonaro — um swing bem menos uniforme que o esperado entre 2022 e 2026),
cada UF num ritmo próprio e quatro ordens de totalização (5 sementes cada). Erro absoluto médio da fatia
nacional de Lula (p.p. de válidos), antigo → novo:

| Ordem | 10% | 25% | 50% | 75% |
|---|---|---|---|---|
| Bolsonaro na frente primeiro (como em 2022) | 8,9 → 1,4 | 7,0 → 1,4 | 4,7 → 1,1 | 2,5 → 0,5 |
| municípios grandes primeiro | 2,4 → 2,2 | 2,4 → 0,8 | 2,0 → 0,6 | 1,0 → 0,3 |
| municípios pequenos primeiro | 4,0 → 3,0 | 2,9 → 2,3 | 2,0 → 1,3 | 0,9 → 0,4 |
| aleatória | 0,3 → 0,1 | 0,2 → 0,1 | 0,1 → 0,1 | 0,1 → 0,1 |

Erro médio por UF (fatia de Lula, média das 4 ordens): 6,5 → 2,9 (10%), 5,4 → 2,1 (25%), 3,7 → 1,3 (50%),
1,9 → 0,5 (75%); cobertura do intervalo de 90% por UF 0,82–0,98. Ponto fraco: na **margem** Lula − 2º
colocado, com 10–25% apurado em ordem por porte, o método novo erra tanto quanto ou mais que o antigo (grandes
primeiro, 10%: 2,2 → 4,8 p.p.; pequenos primeiro, 10%: 6,0 → 6,6) — só capitais apuradas não dizem como o
interior variou; o intervalo se alarga nesse caso.

**b) Avaliação** (`data/avaliacao_1t.json`, `AVALIACAO_1T.md`): 3 visões do modelo, modelo alternativo, média das
pesquisas, última pesquisa nacional de cada instituto (últimos 7 dias, convertida para válidos) e mercados;
erros nacionais e por UF, PIT, cobertura dos intervalos, CRPS aproximado pelos quantis, Brier e log score dos
eventos (1º lugar, ida ao 2º turno, decisão no 1º turno) e ranking das pesquisas pelo erro na margem.

**c) 2º turno condicionado ao 1º turno real** (`web/resultados_2t.json`, seção "2º turno" do painel; 500 mil simulações):
- fatias reais por UF (UFs parciais projetadas por município, com o dp da projeção; no método antigo, ruído
  ∝ √(1 − pst)); se alguém passa de 50% com a apuração concluída, não há simulação;
- transferência dos eliminados (desde 5/10, uma onda só): Quaest 2–3/10 (BR-02197/2026) para todos os que ela mediu
  — Caiado 19/43/36, Renan 11/60/27, Cury 23/34/41 (% Lula/Flávio/branco-nulo-não vota, 2% de indecisos em cada) —
  e, para Zema (fora dessa onda), Quaest 24–27/9 (9/81/10) com Dirichlet α = 10 em vez de 30 (incerteza da escolha de
  onda: entre as duas ondas a fatia decidida de Lula caiu 0,04–0,17 nos outros três). Indecisos repartidos na
  proporção das três respostas em todas as linhas (antes: em "fora" para Caiado/Renan, linhas de premissas.json
  para Cury/Zema). Efeito (`segundo_turno.sensibilidade_matriz`): Lula −0,07 p.p. contra a mistura antiga; só a onda
  de 24–27/9 daria +0,37 p.p. Par diferente de Lula x Flávio: linha genérica e erro × 1,5;
- comparecimento: abstenção e brancos/nulos reais do 1º turno + variação média 1º→2º turno da UF em 2014/2018/2022;
- pesquisas de 2º turno: as de antes do 1º turno com peso 0,25 em logito (em 2018 e 2022 superestimaram o PT em
  3,5 e 4,7 p.p.), **corrigidas pelo erro do mesmo instituto no 1º turno** (ver abaixo), formam com a via de
  transferência a **projeção**; as feitas depois do 1º turno, quando entrarem em `pesquisas_nacionais.csv`, ficam
  fora da projeção e são combinadas com ela **por precisão** (peso = (1/dp_pos²)/(1/dp_pos² + 1/dp_projeção²);
  dp_pos = 1,5 p.p. + deriva de 3 p.p. por 21 dias até o 2º turno), **sem** correção por instituto (não passou no
  backtest) e **sem** termo de viés (a média da véspera do 2º turno errou +0,69 / −1,14 / +0,10 p.p. em
  2014/2018/2022). Antes de 5/10 elas entravam com peso fixo 0,5 e o viés era descontado do centro já misturado.
  Desde 12/10, a pesquisa cujo campo atravessa o 1º turno entra com peso pela fração de dias depois dele, e não há
  house effects (ver "Pesquisas pós-1T" abaixo);
- **termo sistemático da projeção e erro nacional (desde 5/10; `especificacao_vies_2t.py`, `--backtest-vies`,
  `data/backtest_vies_2t.json`)**: a projeção (1º turno real + o que se sabia na véspera) errou, na fatia do PT,
  +1,5 (2002), −7,2 (2006), +1,6 (2010), +2,7 (2014), −0,6 (2018), +2,2 (2022) p.p. Quatro especificações para o
  termo sistemático, comparadas deixando uma eleição de fora (regra fixada antes: menor RMSE; empate < 0,25 p.p. →
  a mais simples):

  | Especificação | RMSE LOEO | MAE | cob. 80% | cob. 95% | log-dens. | termo em Lula 2026 | Lula 2026 (p10–p90) | P(Lula) |
  |---|---|---|---|---|---|---|---|---|
  | (a) viés com sinal do PT | 3,94 | 2,99 | 5/6 | 5/6 | −3,08 | −0,02 | 47,8 (43,7–52,0) | 24% |
  | (b) viés com sinal do líder do 1º turno | 3,95 | 2,91 | 5/6 | 5/6 | −3,07 | +0,14 | 48,0 (43,8–52,1) | 26% |
  | (c) transferência por ideologia dos terceiros | 3,79 | 3,06 | 5/6 | 5/6 | −3,02 | linhas por bloco | 49,1 (44,6–53,6) | 39% |
  | **(d) viés zero (escolhida)** | **3,41** | **2,63** | 5/6 | 5/6 | **−2,86** | 0 | **47,9 (43,9–51,8)** | **23%** |

  (Lula 2026 das sensibilidades com 100 mil simulações; a rodada oficial usa 500 mil.) Em (c) a fatia decidida que
  vai ao PT é p_esq para terceiros de esquerda/centro-esquerda e p_nesq para os demais (classificação por família
  partidária, com fonte, em `especificacao_vies_2t.TERCEIROS`); ajustada nas 6 eleições, p_esq = 0,46 e p_nesq =
  0,61 — o contrário da hipótese de que os terceiros de esquerda explicariam o erro (Garotinho, Marina 2010/2014 e
  Heloísa Helena não foram em bloco para o PT); aplicada a 2026 (todos de não-esquerda) contradiz a medida direta da
  Quaest (Caiado 0,31, Cury 0,40, Renan 0,16, Zema 0,10). **2006 entra**: Alckmin perder votos entre turnos é um
  erro real da projeção, do tipo que pode acontecer de novo; só fica fora da estimativa ecológica de β. **Robustez:
  sem 2006 o resultado muda** — o viés com sinal do líder vence (RMSE 0,94 contra 1,85 do zero, 1,38 PT e 2,09
  ideologia; o líder do 1º turno foi superestimado nas outras 5 eleições) e daria Lula 49,3% (46,5–52,0), P = 36%;
  PT sem 2006: 46,6%, P = 6%; zero sem 2006: 47,8%, P = 16%. Tudo em `segundo_turno.sensibilidade_vies`.
  Escolhida: **viés zero**, que vence em RMSE, MAE e log-densidade com as 6 eleições. dp nacional = √((2·3² +
  Σe²)/(2 + 6)) = **3,31 p.p.** (t5; antes 2,46 com 3 eleições + 1,21 do viés, que era contado duas vezes: o RMS
  dos erros já incluía o viés que se descontava do centro). dp regional 1,10 e estadual 1,94 p.p. (resíduos por UF
  das 6 eleições depois do ajuste nacional). A variância nacional que já vem da incerteza da matriz não é contada
  duas vezes. O termo condicionado ao 1º turno de 2026 (κ, abaixo) só vale na especificação (a); fora da amostra
  (2014/2018/2022) ele não ajudou: RMSE 2,09 com κ, 1,94 só com b, 2,02 com zero.
- **Recalibração com o 1º turno de 2026 (5/10/2026; `vies_institutos.py`, `--backtest-institutos`).**
  *(1) Correção por instituto.* Erro de cada instituto no 1º turno = fatia bipartidária Lula/(Lula+Flávio) da sua
  última pesquisa da semana final menos o real (48,98%). *Partial pooling* (efeitos aleatórios, DerSimonian-Laird;
  variância = amostral pelo n dos que escolheram um dos dois + 1 p.p.² não amostral): média da indústria
  **μ = +1,95 p.p.** (ep 0,48; 14 institutos, 11 acima de zero), τ entre institutos 1,0 p.p.; correção de cada um =
  μ + B·(erro − μ), B = 0,27–0,39 (de +0,7 p.p. para Palver a +2,6 para Indexa). Backtest 2014/2018/2022 (lean só
  com o 1º turno do próprio ano): nas **pesquisas pré-1T** a correção plena reduz o erro da média de 2º turno de
  +3,5/+4,7 para +2,0/+2,0 p.p. (RMS 4,2 → 2,0; só o desvio relativo: 3,0) — são as mesmas entrevistas que erraram
  o 1º turno; nas **pesquisas pós-1T** toda correção piora (média da véspera RMS 0,77 → 1,06 relativa, 4,3 plena;
  erro por pesquisa 2,3 → 2,9–5,0), e o desvio do instituto não persiste (correlação −0,30 em 2018, +0,91 em 2022).
  Adotado: correção plena só nas pré-1T (Lula nas pesquisas pré-1T 49,6% → 47,7%, dp da correção 0,4 p.p. somado à
  incerteza); pós-1T sem correção (`PARAM_2T["correcao_institutos_pos_1t"] = "nenhuma"`; código pronto para as
  variantes). No pipeline LOEO completo o erro nacional fica igual (RMS 1,96 → 1,95; 2022 melhora, 2014 e 2018
  pioram um pouco), UF MAE 2,25 → 2,19, cobertura de 80% nas UFs 0,94 → 0,90.
  *(2) Viés da indústria 1T → 2T com 2026 (desde a tarde de 5/10, só sensibilidade: especificação (a)).* Erro do
  agregador no 1º turno (fatia do PT): +7,6 (2014), +0,5 (2018),
  +0,6 (2022), **+1,8 (2026)**. τ0 (escala do viés persistente) por máxima verossimilhança marginal: 1,7 sem 2026,
  2,0 com 2026 — mas puxado por 2014 (sem 2014: 0,88); desde 5/10 o estimador é robusto (mediana e MAD): **1,13**
  (todas as variantes em `vies_industria.tau0_sensibilidade_pp`). Relação 1º → 2º turno: erro da projeção = b + κ·(e1 − média e1),
  κ ~ N(0; 0,5²) (prior neutro) → **κ = 0,17 ± 0,32** (fraca; 2014 domina). Como 2026 errou menos que a média
  histórica no 1º turno, o viés condicionado cai: termo de viés do 2º turno **−1,13 → −0,78 p.p.** (−0,93 só pela
  calibração com pesquisas corrigidas; −0,15 pelo κ).
  *Sensibilidade* (`segundo_turno.sensibilidade_recalibracao`, 100 mil simulações, TSE 99,94%): método antigo
  P(Lula) 14,6%, Lula 47,26% (p10–p90 43,9–50,7); só correção 11,7%, 46,98%; só viés 1T→2T 15,6%, 47,37%; **novo
  12,9%, 47,13% (43,8–50,4)**; alternativa com correção só relativa 16,3%, 47,50%. Rodada publicada (`--rodar-tudo`, 500 mil):
  P(Lula) 13,0%, Lula 47,14% (p10–p90 43,82–50,45); antes desta recalibração, 14,7% e 47,27% (TSE 99,89%).
  **Revisão da tarde de 5/10** (termo sistemático por LOEO 2002–2022, dp sem dupla contagem, uma onda da Quaest,
  pesquisas pós-1T por precisão; ensaio a seco, TSE 99,99%, 500 mil): **Lula 47,86% (p10–p90 43,93–51,79),
  P(Lula) 23,1%**. Decomposição: viés removido +0,78 p.p.; matriz de uma onda −0,06 p.p.; dp nacional 2,74 → 3,31
  (P sobe ~10 p.p. pelos dois). O método da manhã com as linhas novas e τ0 robusto daria 47,39% e 12,6%
  (`sensibilidade_recalibracao`).
- Estimativas ecológicas TSE (fração do PT nos votos ganhos entre turnos): 2014 0,40; 2018 0,63; 2022 0,30 —
  mostram quanto a transferência real varia de uma eleição para outra (reportadas em `resultados_2t.json`).
- **Transferência regionalizada (desde a noite de 4/10/2026; `transferencia_regional.py`).** A matriz Quaest continua
  sendo o âncora nacional, mas a fatia "decidida" que cada eliminado dá ao PT, p = a/(a+b), passa a depender do lean
  da UF no 1º turno: logito p_UF = logito p + β·z_UF + c(β), com z_UF = logito(Lula/(Lula+Flávio)) da UF menos o
  nacional e c(β) recentrando cada linha para que a média nacional (ponderada pelos votos do eliminado em cada UF)
  continue igual à da Quaest — redistribui entre UFs, não muda o nacional. β é o efeito de contexto ecológico (o
  eleitor de terceira via num estado onde o PT é fraco vai mais para o adversário do PT), estimado por MQ não linear
  com os resultados por UF do TSE (1º → 2º turno) de 2002, 2010, 2014, 2018 e 2022 (β por ano 1,31 / 0,46 / 0,12 /
  0,57 / 0,38; 2006 fora: Alckmin perdeu votos entre turnos) e combinado hierarquicamente (prior N(0; 0,5²),
  variação entre eleições pelo método dos momentos): **β = 0,46, dp preditivo 0,44**, sorteado em cada simulação
  junto com a Dirichlet da matriz. A calibração do erro regional/estadual passa a medir os resíduos com o mesmo
  método. Um efeito regional fixo adicional (N/NE/CO/SE/S) foi testado e **não** entrou (piorou 2014 e 2022).
  Desliga com `PARAM_2T["transferencia_regional"]` ou `--transf-regional nao`; o outro método sai sempre como
  sensibilidade em `segundo_turno.sensibilidade_regional`.
  *Backtest* (leave-one-election-out, detalhes em BACKTEST.md): pipeline completo 2014/2018/2022 — nacional
  inalterado (erro +2,0/−1,6/+2,2 p.p. nos dois métodos), erro médio por UF 2,45→2,87 (2014), 2,19→1,80 (2018),
  2,11→2,10 (2022), média 2,25 nos dois; cobertura das UFs no intervalo de 80% 0,91→0,94 e no de 95% 0,975→0,988.
  Melhora 2018 e 2022 (a validação pedida) e 4 de 5 eleições na distribuição entre UFs isolada; piora 2014
  (Marina, cujo voto não seguiu o lean). Efeito em 2026 (cópia a seco com o TSE a 91,8% apurado): nacional igual (Lula
  47,2% nos dois; P(Lula) 13,9% → 14,0%), UFs ±0,36 p.p. (NE sobe até +0,36 no PI; S/CO/RO/RR/AC caem até −0,35 em SC).
- **Comparecimento entre turnos (checado em 2014/2018/2022, LOEO).** A variação média da abstenção por UF (método
  atual) teve o menor erro (1,29 p.p. por UF; encolhida para o nacional 1,35; só nacional 1,80; sem variação 1,92).
  Brancos+nulos: média por UF 2,35, sem variação 1,92 (só 2022 favorece "sem variação"; mantido). Efeito partidário
  pequeno: a variação da abstenção quase não se correlaciona com o lean (r = −0,04, −0,04, −0,20) e a reponderação
  das UFs muda o PT nacional em ≤ 0,25 p.p.; os erros nacionais da abstenção (−1,0, −0,5, +1,5 p.p.) batem com o
  dp de 1 p.p. usado. Nada mudou.
- **Pesquisas pós-1T, visões de viés, apoios e mandato (12/10/2026; `--backtest-pos-1t`,
  `data/backtest_pos_1t_2t.json`, BACKTEST.md).** O backtest roda o pipeline completo em datas entre os turnos de
  2014/2018/2022 (4, 8, 12, 16 e 20 dias depois do 1º turno e véspera; só pesquisas com fim de campo até a data − 1
  dia) e mede o CRPS do nacional.
  (1) Pesquisa cujo campo atravessa o 1º turno (AtlasIntel 3–8/10, n = 5.026) entra com peso igual à fração dos dias
  de campo depois do dia da eleição (4/6; `PARAM_2T["pesquisas_atravessando_1t"] = "fracao"`; antes: excluída). Não há
  caso histórico, então o backtest não muda; efeito em 2026: centro 47,91 → 47,84, P(Lula) 13,7% → 12,9%.
  (2) House effects pós-1T (*partial pooling* em relação à média entre institutos, com ou sem prior do erro do 1º
  turno): CRPS médio 0,999 → 0,964 / 0,945, mas cada variante só melhora 1 das 3 eleições. Com dados insuficientes,
  ficam como sensibilidade (`house_effects_pos_1t = "nenhum"`). Indecisos: razão dos válidos a/(a + b) para todos os
  institutos (Vox 50,86%).
  (3) Três visões do 2º turno: neutro, calibrado (padrão) e viés pleno. O viés pleno é o pior no backtest (CRPS 2,22).
  (4) Apoios declarados a Flávio: sem pesquisa nova de 2ª opção, a matriz não muda. Sensibilidade k ~ U(0; 0,30) da
  coluna "fora" de Caiado/Zema/Cury indo a Flávio: −0,04 p.p. (k = 0,30: −0,07).
  (5) Saída antecipada do mandato 2027–2030 (informativo, mesmo método para os dois).
  Rodada de 12/10 (TSE 100%, 500 mil): **P(Lula) 12,9%, Lula 47,85% (p10–p90 45,38–50,33), centro 47,84**. Visões:
  neutro 14,7% (48,01), viés pleno 4,7% (46,61).

  **Chaves novas em `resultados_2t.json`** (todas em `segundo_turno`, só quando o par é Lula x Flávio; o painel as mostra
  em "Quem vai ganhar → 2º turno": seções "Pesquisas depois do 1º turno", "Quanto a premissa de viés muda" e
  "Quem completa o mandato"):
  - `visoes_vies.visoes.{neutro,calibrado,vies_pleno}`: `p_a_vence`, `a_media`, `centro_a_pct`, `a_p10`, `a_p90`,
    `correcao_pre_1t`, `correcao_pos_1t`, `pesquisas_pre_1t_a_pct`, `pesquisas_pos_1t_a_pct`, `projecao_a_pct`,
    `peso_pesquisas_pos_1t`, `dp_nacional_pp`, `n`, `descricao` e `backtest` (`rmse_centro_pp`, `crps_medio_pp`,
    `cob80`, `cob95`, `pit_medio`); `visoes_vies.par` e `visoes_vies.nota`. `calibrado` = a rodada principal.
  - `sensibilidade_pos_1t`: lista com `variante`, `atravessa`, `house`, `n_pesquisas_pos`, `institutos`,
    `pesquisas_pos_1t_a_pct`, `peso_pesquisas_pos_1t`, `centro_a_pct`, `a_media`, `a_p10`, `a_p90`, `p_a_vence`.
  - `sensibilidade_endosso`: `candidatos`, `para`, `k_centro`, `k_meia_amplitude`, `nota` e `tabela` (`variante`,
    `via_transferencia_a_pct`, `projecao_a_pct`, `centro_a_pct`, `a_media`, `a_p10`, `a_p90`, `p_a_vence`, `endosso`).
  - `backtest_pos_1t`: `resumo` e `resumo_horizontes_4_8` (por variante: `rmse_centro_pp`, `mae_centro_pp`,
    `crps_medio_pp`, `cob80`, `cob95`, `pit_medio`, `brier`, `rmse_media_pos_pp`, `casos`), `decisao` (por variante:
    `d_crps_pp`, `d_rmse_centro_pp`, `d_crps_por_ano_pp`, `passa_media`, `passa_consistencia_2_de_3`, `passa`),
    `calibracao_dp_pesquisas_pos`, `pesquisas_atravessando_1t`, `horizontes`, `n`, `gerado_em`.
  - `mandato_2027_2030` (informativo, **não** entra em P(vencer)): `por_candidato.{Lula,Flavio}` com `vice`,
    `idade_na_posse`, `morte_no_mandato_tabua_pct`, `incapacidade_pct`, `p_saida_antecipada_pct`,
    `p_completa_se_eleito_pct`, `p_vencer_pct`, `p_eleito_e_completa_pct`, `p_eleito_e_vice_assume_pct` (cada um com
    `baixo`/`central`/`alto` = menor/maior risco de saída) e `fonte`; `p_vencedor_completa_pct`, `p_vice_assume_pct`,
    `metodo`, `multiplicadores`, `dias_ate_posse`, `nota`.
  - `pesquisas_2t.pos` ganhou `tabela` (por instituto: `campo_inicio`, `campo_fim`, `n`, `fracao_pos_1t`,
    `fatia_a_validos_pct`, `fatia_a_usada_pct`, `house_pp`, `peso_rel`), `atravessa`, `house`, `house_effects`,
    `q_sem_house`, `dp_house_pp`, `dp_correcao_institutos_pp`, `media_sem_cada_instituto` e `dias_ate_2t`.
  - `endosso` (em cada simulação; `null` no padrão).
- **Ensaio a seco:** `--saida PASTA` grava `resultados_2t.json`, `avaliacao_1t.json` e `AVALIACAO_1T.md` na pasta e
  não roda `publicar.py`; `--fonte cache` lê só a última leitura gravada (sem rede); `--backtest-2t` imprime os
  backtests acima (e grava o das pesquisas pós-1T); `--backtest-vies` refaz a escolha do termo sistemático
  (`data/backtest_vies_2t.json`); `--backtest-pos-1t` refaz só o das pesquisas pós-1T (`data/backtest_pos_1t_2t.json`).

**Ensaio com 2022** (1º turno de 2022 como se fosse a noite de hoje; resultado lido de JSON no formato do TSE de
2022, reconstruídos dos dados abertos em `tests/fixtures/tse/2022/`; regerado em 5/10 com o método atual: calibração
com 2002–2018, especificação do termo sistemático escolhida por LOEO sem 2022 — deu viés zero):
2º turno previsto Lula 53,1% (p10–p90 49,0–57,2; P(Lula vence) 84%); real 50,9% (PIT 0,24, dentro do intervalo
de 80%); 26 de 27 UFs com o vencedor certo, erro médio absoluto por UF 2,1 p.p., todas as UFs no intervalo de 80%.
Na véspera do 1º turno, o modelo principal dava 54,3% para Lula no 2º turno. Ensaios 2014/2018 (mesma regra, sem o
próprio ano): Dilma 54,4 (real 51,6; PIT 0,20), Haddad 44,3 (real 44,9; PIT 0,57); nos três, resultado nacional
dentro do intervalo de 80% (erro médio absoluto 1,8 p.p.), UFs 94% no de 80% e 99% no de 95% (antes 91% e 98%).
Saídas em `data/ensaio_2022/` (`resumo.json` vai para `resultados_2t.json`, bloco `ensaio_2022`).

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
- **Decisão no 1º turno** (21% calibrado; 16% neutro) fica bem acima dos mercados (~5%). Decomposição
  (BACKTEST.md, "Decisão no 1º turno"): o que pesa é o dp do erro nacional de margem (4,0 p.p. em p2; desligado,
  a probabilidade cai a ~1%; com dp 3,0, a 14%) e, em segundo lugar, a contração da terceira via (sem ela, 11%);
  o viés calibrado muda sobretudo *quem* venceria no 1º turno; caudas t5, comparecimento e erros estaduais quase
  não contam. Na validação aninhada (parâmetros e prior sem o ano), a véspera de 2014 e de 2022 teve P(decisão)
  de 31% e 26%, e nenhuma das duas foi decidida: indício de que esta cauda é larga, como dizem os mercados. Mas
  reduzir o dp derruba a cobertura de 80% para 67% (abaixo da restrição); tirar a contração piora muito o CRPS
  (2,41 → 3,02) e a cobertura (73% → 60%); encolher mais a contração (tau0_log 0,15) melhora um pouco o Brier da
  decisão (0,055 → 0,042) com CRPS praticamente igual (2,41 → 2,44), diferença compatível com ruído em 3
  eleições. **Parâmetros mantidos**; esta probabilidade é a parte menos confiável do modelo. O modelo
  alternativo dá ainda mais (36%).
- Pesquisas estaduais: poucas rodadas por UF; AP sem n na Quaest.
- Matriz de transferência de subamostras pequenas de uma pesquisa; no backtest usou-se a matriz
  implícita das pesquisas pareadas.
- Prior demográfico e ajuste de comparecimento não testados no backtest (seriam vazamento).
- AtlasIntel final (27/9–2/10) incluída na madrugada de 4/10. Não localizadas com fonte verificável até
  4/10 ~02h UTC: consolidação nacional da Veritá 26/9–2/10 (BR-04522/2026; só relatórios estaduais citados no
  site do instituto) e Gerp 1–3/10 (BR-08168/2026).
- **Pipeline da noite da apuração** (`resultado_1t.py`): a projeção de UFs com apuração parcial é por
  município (swing sobre 2022), validada só com um replay de 2022 (referência 2018) em ordens simuladas; os
  arquivos por município do TSE de 2026 foram testados só antes da apuração (com zeros); dentro de um município
  parcial supõe-se que o resto vote como o apurado; o erro do 2º turno foi calibrado com 3 eleições (prior de dp 3 p.p.);
  a matriz de transferência vem de subamostras pequenas da Quaest; o endpoint do TSE de 2026 foi testado só antes
  da apuração (com zeros) e o formato de 2022 só com arquivos reconstruídos (os JSON originais saíram do ar).
- O 2º turno é projetado em 3/10; fatos entre os turnos não estão no modelo.

## Neutralidade
O modelo usa apenas pesquisas registradas, resultados oficiais do TSE e parâmetros documentados
com origem. O viés calibrado sai de uma regra empírica aplicada a qualquer erro histórico, nos dois
sentidos. As três visões aparecem sempre lado a lado com os mercados. Os eventos da linha do tempo
são factuais, com fonte, auditados para equilíbrio (`data/auditoria_neutralidade.md`) e não mudam
nenhum número. As cores (violeta e laranja-queimado) foram escolhidas para não lembrar as dos
partidos ou das campanhas e foram validadas para daltonismo e contraste.
