# Simulador Monte Carlo da eleição presidencial de 2026 (por UF)

Simulador neutro, estado a estado, da eleição presidencial brasileira de 2026
(1º turno em 4/10/2026; eventual 2º turno em 25/10/2026), com 500.000
simulações por cenário e um painel web estático.

Dados até **3/10/2026** (véspera do 1º turno). Os números vêm das notas de
pesquisa em `research_notes/` e do relatório `reports/Briefing eleição presidencial 2026.md`;
cada linha dos CSVs em `data/` traz fonte e data.

## Como rodar

```bash
pip install numpy pandas pytest           # Python 3.10+
python simulador/rodar.py                 # 500.000 simulações x 2 cenários -> simulador/web/resultados.json
python simulador/rodar.py --n 50000 --seed 1   # rodada rápida / outra semente
python -m pytest simulador/tests -q       # testes
cd simulador/web && python -m http.server 8000   # abrir http://localhost:8000
```

O painel precisa ser servido por HTTP (o `fetch` de `resultados.json` não
funciona com `file://`). Ele usa Chart.js do cdnjs (com fallback para o
jsDelivr); sem a biblioteca, cartões, mapa e tabelas continuam funcionando.

Tempo medido neste ambiente (4 vCPUs, NumPy 2.4, float32, lotes de 100 mil):
**~30–33 s** para 2 cenários x 500.000 simulações (1 milhão de eleições
simuladas, 28 unidades x 7 candidatos), cerca de 0,4 s para a agregação.
A semente fixa (`premissas.json`, `simulacao.semente`) torna a rodada reprodutível.

## Estrutura

```
simulador/
  premissas.json        todos os parâmetros, com origem (fonte / cálculo / inferência) e nota
  modelo.py             agregação, médias por UF, simulação vetorizada
  rodar.py              roda N simulações por cenário e grava web/resultados.json
  data/
    pesquisas_nacionais.csv   89 pesquisas nacionais (dez/2025-2/10/2026), 1º e 2º turno, fonte por linha
    pesquisas_uf.csv          35 pesquisas estaduais (27 UFs), 1º e 2º turno, fonte por linha (números do G1 quando há conflito)
    eleitorado_uf_2026.csv    eleitorado apto 2026 por UF (TSE) + abstenção e brancos/nulos de 2022 por UF
    eventos_2026.csv          linha do tempo factual (só anotação no gráfico; NÃO entra no modelo)
    mercados_snapshot.csv     cotações de mercados de previsão em 3/10 (só comparação)
    polymarket_historico_diario.csv   série diária Polymarket (cópia de research_notes/.../raw_mercados)
    resultados_uf_2002_2022.csv, lean_swing_uf.csv, correlacao_swing_regioes.csv   cópias dos agregados TSE
  web/index.html        painel (HTML+CSS+JS inline, Chart.js via CDN)
  web/resultados.json   saída do modelo
  tests/test_modelo.py  testes pytest
  screenshots/          capturas do painel (desktop claro/escuro, celular)
```

## Metodologia

### 1. Média nacional das pesquisas
A participação dos candidatos é decomposta em três quantidades, todas em votos válidos:

- **p2** = Lula / (Lula + Flávio) no 1º turno — disponível em todas as pesquisas;
- **m_k** = válidos de cada candidato menor (Caiado, Cury, Zema, Renan Santos, "Outros" = 7 nanicos) — só nas pesquisas que publicam a lista completa;
- **q** = Lula / (Lula + Flávio) no 2º turno.

Votos válidos = votos totais / (100 − brancos, nulos e indecisos), ou seja,
indecisos alocados proporcionalmente (limitação: o briefing recomenda alocação por
2ª preferência, que não foi publicada em 2026).

**Efeitos de instituto (house effects).** Com as pesquisas da campanha (campo
a partir de 20/8), estima-se em logito `y = semana + h_instituto + e`, com
restrição Σh = 0 (o efeito é relativo ao consenso, não à verdade) e
encolhimento ridge (dp a priori 1,5 p.p.). Assim, um instituto com uma só
pesquisa fica perto de zero. Resultado (p.p. na fatia de Lula, positivo = mais
favorável a Lula que o consenso): 1º turno MDA +2,3, Quaest +1,3, Indexa +1,1,
Datafolha +0,1, Atlas 0,0, PoderData −1,5, Vox −1,3, Futura −2,1; 2º turno
Datafolha +1,3, MDA +1,6, Atlas +0,7, Futura −2,0, Gerp −1,5.

**Média final.** Última pesquisa de cada instituto com campo encerrado nos 14
dias anteriores a 3/10, peso `sqrt(min(n, 3000)) * exp(−dias/7)`, valor
corrigido pelo house effect. Resultado: **p2 = 51,6%** (sem correção 51,5%),
**q = 49,8%** (sem correção 49,8%); menores somam 12,0% dos válidos
(Cury 3,5; Caiado 3,1; Renan 3,1; Outros 1,3; Zema 1,0). Para comparação, a
média simples das 13 pesquisas da última semana dá 45,5 x 45,6 no 2º turno.

### 2. Estados
- **Prior:** `logito(p_UF) = logito(p_nacional) + 0,85 × lean_2022(UF)` (lean em
  logito; 0,85 = inclinação do lean 2018→2022 no TSE), dp 4 p.p.
- **Pesquisas estaduais:** fatia bipartidária com variância
  `1,5·p(1−p)/n + 3²` (piso não amostral de 3 p.p.), inflada por `1 + dias/14`.
  Combinação por precisão com o prior. Os menores por UF usam o mesmo esquema
  (prior = composição nacional, dp 5 p.p.; Caiado tem 23% em GO).
- **Calibração:** as médias por UF são deslocadas por uma constante em logito
  para que a soma ponderada (eleitorado 2026 × comparecimento × válidos de 2022)
  reproduza a média nacional. O deslocamento foi de −1,0 p.p. no 1º turno e −0,9
  no 2º: as pesquisas estaduais (quase todas de uma rodada Quaest de 18–28/9)
  somadas dariam Lula ~1 ponto acima da média nacional.

### 3. Simulação (por sorteio)
1. **Erro nacional 1º turno:** t de Student (5 gl), dp 3,5 p.p. na fatia p2
   (≈ 3,1 p.p. por candidato em válidos; ≈ 6 p.p. na margem).
2. **Menores:** erro multiplicativo nacional (dp log 0,25) e por UF (0,2).
3. **Contração da terceira via (voto útil):** fração s ~ Beta(média 0,30, dp
   0,07) dos votos dos menores migra para os dois primeiros, dividida pela
   proporção Lula/(Lula+Flávio) da matriz de transferência Quaest (ex.: Zema
   10/80, Renan 25/50, Caiado 30/42, Cury 28/35).
4. **Estrutura entre UFs (logito):** fator "NE/N vs S/CO" (dp 1,5 p.p.; cargas
   NE +1, N +0,5, SE 0, CO −0,5, S −1, centradas pelo eleitorado), fator
   regional por região (dp 1,5) e erro idiossincrático da UF (t 5 gl, dp =
   máx(dp posterior da UF, 2,5 p.p.)). Esses três componentes são centrados em
   cada simulação, de modo que o agregado nacional segue o erro nacional
   sorteado (correlação 0,996 entre os dois no cenário neutro; teste automatizado).
5. **Comparecimento e brancos/nulos:** valores de 2022 por UF e turno + ruído
   nacional (1,0 e 0,8 p.p.) e por UF (1,5 e 0,5 p.p.). O resultado nacional é
   sempre a soma dos votos válidos simulados das 27 UFs + exterior.
6. **1º turno:** vencedor se alguém passa de 50% dos válidos nacionais; senão,
   os dois primeiros vão ao 2º turno.
7. **2º turno:** duas vias, combinadas em logito com pesos 0,7 / 0,3:
   - *pesquisas de 2º turno*: q da UF + erro nacional t (5 gl, dp 2,0 p.p.,
     correlação 0,4 com o erro do 1º turno) + erros subnacionais (correlação 0,6
     com os do 1º turno);
   - *transferência*: 1º turno simulado da UF + matriz Quaest sorteada por
     Dirichlet (α = 30) para cada candidato menor (Lula e Flávio retêm seus votos).
   Se o par do 2º turno não for Lula x Flávio (não ocorreu em nenhuma simulação),
   vence o 1º colocado do 1º turno.

### 4. Cenários
- **Neutro:** sem viés sistemático (só o erro simétrico acima).
- **Viés histórico:** em 2014, 2018 e 2022 as pesquisas de véspera subestimaram
  o candidato anti-PT mais competitivo em 5–8 p.p. de válidos no 1º turno e
  superestimaram o PT em ~0,5–1,1 p.p. no 2º turno. Por simulação: Flávio
  +b p.p. no 1º turno, b ~ N(3, 1) truncada em 0 (1/3 retirado de Lula, 2/3 dos
  menores; somado à contração da terceira via, o deslocamento total de Flávio em
  relação às pesquisas fica em ~5 p.p., na faixa histórica); no 2º turno, Lula
  −N(0,8; 0,6) p.p. na via das pesquisas.
- O painel mostra os dois lado a lado e a média 50/50 (mistura exata).

## Resultados (rodada de 3/10/2026, 500.000 simulações por cenário, semente 20261004)

| Probabilidade | Neutro | Viés histórico | Média 50/50 |
|---|---|---|---|
| Lula vence a eleição | 48,2% | 24,4% | 36,3% |
| Flávio Bolsonaro vence a eleição | 51,8% | 75,6% | 63,7% |
| Decide no 1º turno | 13,3% (Lula 9,8; Flávio 3,4) | 25,5% (Lula 5,3; Flávio 20,2) | 19,4% |
| 2º turno Lula x Flávio | 86,7% | 74,5% | 80,6% |
| Lula 1º colocado no 1º turno | 65,6% | 32,5% | 49,1% |
| 1º turno Lula, % válidos (p10–p90) | 46,5 (43,1–50,0) | 45,5 (42,1–48,9) | |
| 1º turno Flávio, % válidos (p10–p90) | 44,6 (41,2–48,1) | 47,8 (44,2–51,3) | |
| 2º turno Lula, % válidos (p10–p90) | 49,9 (47,7–52,1) | 48,8 (46,6–51,1) | |

Erro de Monte Carlo (e.p.) dessas probabilidades: ≤ 0,07 p.p.

UFs (P(Lula vence o 2º turno na UF), neutro / histórico): Nordeste ≥ 95%
em todas as UFs (AL 95/92; demais ~100); Sul, Centro-Oeste, RO, AC e RR ≤ 4%;
SP 3,8/1,7; RJ 1,6/0,8; **MG 41/27**; **AM 55/43**; **PA 71/59**; **TO 43/30**;
AP 23/16.

Mercados de previsão em 3/10 (normalizados): Flávio vence 56–60%, Lula 40–44%;
alguém vence no 1º turno 4,6–5,3%; Lula em 1º no 1º turno ~72%.

### Leituras e surpresas
- **2º turno nacional neutro ≈ cara ou coroa (48/52)**, coerente com a média de
  45,5 x 45,6. A leve vantagem de Flávio vem da média de 2º turno corrigida por
  instituto (49,8% para Lula): P(Lula > 50% no 2º turno) = 47,8%.
- **Via de transferência dá Lula 50,1%, via de pesquisas 49,8%.** A matriz
  Quaest aplicada ao 1º turno não capta a migração líquida de indecisos para
  Flávio que as próprias pesquisas mostram (Quaest: Lula 39→42, Flávio 34→42
  com menores de só 12 pontos). Por isso o peso da via de transferência é 0,3.
- **P(decisão no 1º turno) de 13% (neutro) é bem maior que nos mercados
  (~5%).** Decorre do dp de 3,1 p.p. por candidato (faixa de 3–4 sugerida pelo
  briefing) com caudas t e da contração da terceira via, que leva Lula a 46,5%
  em média. No cenário histórico, 20% são vitórias de Flávio no 1º turno — um
  erro do tamanho de 2022 aplicado às pesquisas de 2026.
- **SP com só ~4% para Lula no 2º turno**, embora o Datafolha-SP dê 45 x 48
  (48,4% bipartidário): a Quaest-SP dá 35 x 43 (44,9%), o prior de 2022 é 44,8%
  e a calibração nacional tira ~1 ponto. É a premissa estadual mais sensível.
- **Cenário histórico ≈ 76% Flávio**, acima dos mercados (~59%): os mercados
  ficam entre os dois cenários, perto da média 50/50 (64%).

## Premissas (resumo; lista completa em `premissas.json` e no painel)

| Parâmetro | Valor | Origem |
|---|---|---|
| Janela / recência / teto de n | 14 dias, τ = 7 dias, n ≤ 3.000 | inferência (briefing) |
| House effects | Σh = 0, ridge dp 1,5 p.p. | inferência apoiada em fonte (Pindograma r = 0,03 para ratings) |
| Contração da 3ª via | Beta(0,30; dp 0,07) | inferência (2018, 2022) |
| Matriz de transferência | Quaest 24–27/9, Dirichlet α = 30 | fonte (Outros: inferência) |
| Erro nacional 1º turno | t5, dp 3,5 p.p. na fatia p2 | inferência (Pindograma MAE 2,5–3,2; erros 2018/2022) |
| Viés histórico 1º turno | Flávio +N(3, 1) p.p. | inferência (2014/18/22, N = 3) |
| Erro nacional 2º turno | t5, dp 2,0 p.p.; ρ = 0,4 com 1º turno | inferência |
| Viés histórico 2º turno | Lula −N(0,8; 0,6) p.p. | cálculo (2010, 2018, 2022) |
| Peso pesquisas x transferência no 2º turno | 0,7 / 0,3 | inferência |
| Prior estadual | 0,85 × lean 2022, dp 4 p.p. | cálculo (TSE) |
| Piso de erro de pesquisa estadual | 3 p.p.; deff 1,5 | inferência (Pindograma 2,25–4,34) |
| Fator NE/N x S/CO; regional; UF | 1,5; 1,5; ≥ 2,5 p.p. | sinais de correlação: cálculo (TSE); tamanhos: inferência |
| Abstenção e brancos/nulos | 2022 por UF + ruído | fonte (TSE) + inferência |
| Eleitorado | 158.745.463 aptos por UF | fonte (TSE 2026) |

## Limitações
- **Mais simulações não reduzem a incerteza das premissas.** Com 500 mil
  simulações o erro de Monte Carlo é < 0,1 p.p.; mudar o viés suposto em 2
  pontos de margem muda a probabilidade de vitória em ~20 pontos.
- Viés histórico com N = 3 eleições; pode não se repetir (Censo 2022 nas
  ponderações; vários institutos já mostram disputa mais apertada).
- **Pesquisas de véspera não incluídas:** Datafolha (3/10, n = 4.006), Quaest
  (2–3/10, n = 3.702) e AtlasIntel final (27/9–2/10, n = 5.000) não tinham
  números publicados localizáveis com fonte verificável no momento da rodada
  (uma busca rápida retornou só resumos que repetem a rodada anterior). Foram
  usadas as rodadas anteriores. Para incluí-las, acrescente linhas em
  `data/pesquisas_nacionais.csv` e rode de novo.
- Pesquisas estaduais: quase só uma rodada Quaest; AP sem n, sem menores e sem
  2º turno (n = 600 assumido); GO sem 2º turno; conflitos de números entre
  veículos (AL, RS) resolvidos pelo G1/veículo contratante.
- Indecisos alocados proporcionalmente; sem teto por rejeição; sem modelo de
  eleitor provável; matriz de transferência de subamostras pequenas.
- Correlação entre UFs por fatores com tamanhos escolhidos (não estimados de
  erros históricos de pesquisas estaduais, que não estão disponíveis).
- Sem backtest de cobertura 2014–2022.
- O 2º turno é projetado em 3/10; fatos entre turnos não estão no modelo.
- Gerp final (44 x 49 no 2º turno) tem nota de checagem na fonte; entra com o
  mesmo peso dos demais (house effect encolhido).

## Neutralidade
O modelo não escolhe lado. Usa apenas pesquisas registradas, resultados
oficiais do TSE e parâmetros documentados com sua origem. Os dois cenários de
erro das pesquisas — "pesquisas como estão" e "pesquisas erram como em
2014/2018/2022" — são sempre mostrados lado a lado; nenhum é apresentado como
o correto. Os eventos da linha do tempo são descritos de forma factual, com
fonte, servem só de anotação e não alteram nenhum número. As cores do painel
(violeta e verde-azulado) foram escolhidas para não coincidir com as cores
partidárias e foram validadas para daltonismo e contraste. Os mercados de
previsão aparecem apenas como comparação.
