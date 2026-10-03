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
python simulador/backtest.py                    # grade + LOEO + BACKTEST.md + data/backtest_saida.json (~10 min)
python simulador/rodar.py                       # 500.000 simulações x 3 visões -> web/resultados.json (~45 s)
python simulador/publicar.py                    # cópia para artifact em web_publicar/
python -m pytest simulador/tests -q             # testes (~25 s)
cd simulador/web && python -m http.server 8000  # abrir http://localhost:8000
```

`backtest.py --rapido` pula a grade e só avalia com os parâmetros de `premissas.json`.
O painel precisa de HTTP (o `fetch("resultados.json")` é relativo). Chart.js 4.4.1 vem do
cdnjs (versão fixa, com SRI) e cai para o jsDelivr se o cdnjs falhar; sem a biblioteca,
cartões, mapa e tabelas continuam funcionando.

**Tempo medido** (4 vCPUs, NumPy 2.4, float32, lotes de 100 mil): 40,6 s para 3 visões ×
500.000 simulações (1,5 milhão de eleições, 28 unidades × 7 candidatos) + 2,7 s de base e
priors; backtest completo 574 s.

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
| Lula vence a eleição | **21,5%** | 44,9% | 12,1% | 40,1% |
| Flávio Bolsonaro vence a eleição | **78,5%** | 55,1% | 87,9% | 58,8% |
| Decidida no 1º turno | 18,9% (Lula 5,2; Flávio 13,7) | 15,5% (10,1; 5,4) | 29,1% | 5,3% |
| Lula em 1º no 1º turno | 37,3% | 59,9% | 25,8% | 71,4% |
| 1º turno Lula, % válidos (p10–p90) | 44,5 (40,3–48,7) | 46,1 (42,3–50,0) | 43,4 (38,9–47,9) | |
| 1º turno Flávio, % válidos (p10–p90) | 46,4 (42,2–50,7) | 44,8 (40,8–48,8) | 47,7 (43,2–52,3) | |
| 2º turno Lula, % válidos (p10–p90) | 47,9 (44,4–51,4) | 49,7 (46,6–52,9) | 46,5 (42,7–50,4) | |

Erro de Monte Carlo ≤ 0,07 p.p. UFs disputadas no calibrado (P(Lula vence o 2º turno na UF)):
MG 25%, PA 44%, AM 40%, TO 30%, AP 15%, SP 5%, RS 9%, AL 76%; Nordeste ≥ 97% exceto AL;
Sul/Centro-Oeste/RO/AC/RR ≤ 5%.

**Leitura.** As pesquisas (média com efeitos de instituto) dão Lula 51,1% dos votos dos dois
primeiros no 1º turno e 49,6% no 2º turno: um empate. A diferença entre as visões é inteira
a premissa sobre o erro das pesquisas. Na véspera de 2014, 2018 e 2022 a média das pesquisas
(com o mesmo agregador) ficou mais favorável ao PT do que a urna: em p2, +6,4 / +4,0 / +0,8 p.p.
(depois da contração esperada da terceira via); no 2º turno projetado na véspera do 1º,
+4,0 (2018) e +4,7 (2022). O modelo calibrado encolhe essa média para zero (prior N(0, 2²)) e
chega a um viés de +1,5 ± 1,4 p.p. em p2 e +1,8 ± 1,4 p.p. no 2º turno, já descontado o efeito de
comparecimento e ponderado pela exposição dos institutos. A probabilidade é a média sobre a
incerteza desse viés. A regra é simétrica: erros históricos com sinal oposto produziriam
correção para o outro lado.

## Metodologia

### 1. Agregação nacional (`modelo.agregar`, `house_effects_hier`)
- Cada pesquisa vira **p2** = PT/(PT + adversário) no 1º turno, **m_k** = válidos de cada menor
  (só pesquisas com lista completa) e **q** = PT no 2º turno.
- **House effects hierárquicos:** `logito(y) = semana + h_instituto + e`, h ~ N(0, τ²), com τ e o
  ruído por pesquisa estimados por máxima verossimilhança restrita numa grade (2026: τ = 1,5 p.p.
  no 1º turno, 1,0 no 2º). h = média posterior com desvio-padrão; instituto com 1 pesquisa fica
  perto de zero. 1º turno (p.p. pró-Lula): MDA +2,8, Quaest +1,4, Indexa +1,0, Datafolha +0,5,
  Atlas +0,2, Vox −0,8, PoderData −1,2, Gerp −1,3, Palver −2,1, Futura −2,1.
- **Média final:** última pesquisa de cada instituto em 14 dias, peso √min(n, 3000) × e^(−dias/7),
  corrigida pelo house effect; a incerteza da própria média (dp posterior dos h) entra na simulação.
- **Higiene:** deduplicação por registro TSE e por instituto+data+números (nenhuma duplicata no
  arquivo atual; a suposta duplicata da AtlasIntel era a mesma rodada citada por dois veículos);
  Datafolha 3/10 entra em votos válidos (sem indecisos a alocar); **Gerp 30/9–2/10 sinalizada**
  (linha corrigida em 3/10; peso 0,5); pesquisas de véspera incluídas (Datafolha 3/10 n = 4.006,
  Palver 3/10, PoderData, MDA, Vox, IFP, Gerp).
- **Indecisos:** proporcionais. A divisão pelo "espaço" (100 − rejeição − intenção), na linha de
  Pereira & Nunes (2024), foi validada no backtest e **não melhorou** (2018 1T: erro +1,6 contra
  +0,5; 2022 2T: +0,3 contra +0,1); fica como sensibilidade (p2 51,0 contra 51,1). Nenhuma pesquisa
  de 2026 perguntou 2ª opção no 1º turno. A **rejeição** (Datafolha 45/45, sem misturar com a
  métrica da Quaest) é **teto suave** no 2º turno (ativo em ~1% das simulações).

### 2. Estados
- **Prior:** nacional + lean anterior em logito. Em 2026, prior misto de `segmentos.py`
  (1º turno: 0,8 × 0,85 × lean 2022 + 0,2 × demográfico; dp fora do tempo ~7,0 p.p.); no 2º turno
  o misto só em **AP e GO** (sem pesquisa de 2º turno; dp ~4,5 p.p.). Exterior: dp 15 p.p.
- **Pesquisas estaduais:** variância `1,5·p(1−p)/n + piso²` × (1 + dias/14), piso 3 p.p. (1º) e
  2 p.p. (2º) — escolhidos no backtest. Médias deslocadas para que o agregado das UFs reproduza o
  nacional (−1,6 p.p. no 1º turno, −1,3 no 2º).

### 3. Erro estruturado (por simulação)
1. **Margem PT x adversário:** t de Student (5 gl), dp 4,0 p.p. em p2 (backtest), + incerteza da média.
2. **Terceira via combinada:** erro em log com média −0,25 (contração de ~22%, prior empírico-bayesiano
   dos erros −0,09/−0,30/−0,43 de 2014/18/22) e dp 0,10 (t); os votos que saem vão para Lula/Flávio
   pela matriz de transferência (Quaest 24–27/9, Dirichlet α = 30).
3. **Resíduo por candidato menor:** log-normal nacional e por UF (dp 0,15), mexe na composição.
4. **Viés da indústria** (só calibrado/pleno): b ~ posterior empírico-bayesiana × exposição média dos
   institutos (Atlas 0,6 ± 0,2 por ponderar por voto passado; Quaest 0,9; demais 1,0 com dp 0,15–0,3;
   média ponderada 0,97). Correlação 0,6 entre o viés do 1º e do 2º turno.
5. **Subnacional:** eixo NE/N x S/CO (1,5 p.p.), região (4,5 p.p., backtest), UF (t, ≥ 3 p.p.),
   centrados para não alterar o agregado nacional.
6. **2º turno:** 0,3 × (pesquisas de 2º turno + erro t dp 2,0, ρ = 0,5 com o 1º turno + viés) +
   0,7 × (1º turno simulado + matriz de transferência), em logito (pesos escolhidos no backtest).
7. **Comparecimento:** abstenção e brancos/nulos de 2022 por UF + ruído; na visão calibrada, o
   **ajuste de comparecimento por segmento** (−0,37 p.p. em p2, −0,25 em q; `segmentos.py`). Para não
   contar duas vezes, os erros históricos usados no prior calibrado são descontados do efeito de
   comparecimento medido em 2022 (0,18 / 0,19 p.p.); a visão pleno não aplica o ajuste (o erro
   histórico já o contém).

### 4. Visões
- **Modelo calibrado (principal):** integra sobre a incerteza do viés (encolhido, com exposição por instituto).
- **Neutro:** viés 0 (mantém a contração usual da terceira via e todo o erro simétrico).
- **Viés histórico pleno:** média dos erros de 2014/18/22 sem encolhimento, exposição 1.

## Backtest (detalhes em BACKTEST.md)

Véspera de cada turno, só com pesquisas daquele momento; prior de viés **leave-one-election-out**.

| Visão | Cobertura 50/80/95% nacional | Cobertura 50/80/95% UF | CRPS nac / UF | Brier UF |
|---|---|---|---|---|
| Calibrado | 55 / 80 / 100 | 52 / 79 / 92 | 1,83 / 3,61 | 0,066 |
| Neutro | 30 / 70 / 95 | 47 / 78 / 91 | 2,12 / 3,71 | 0,069 |
| Viés pleno | 50 / 85 / 100 | 53 / 78 / 92 | 1,69 / 3,58 | 0,065 |
| Calibrado, prior só com anos anteriores | 45 / 70 / 100 | 51 / 77 / 92 | 2,16 / 3,73 | 0,069 |

- Parâmetros escolhidos por blocos (grade + restrição de cobertura ≥ 75%/90% + menor CRPS) e
  verificados fora da amostra (LOEO); o encolhimento do viés (τ0 = 2 p.p.) é fixo por princípio: a
  grade, com 2–3 eleições do mesmo sinal, sempre prefere encolher menos.
- Erro absoluto médio da mediana: 2,6 p.p. nacional, 5,0 p.p. por UF. O Brier das probabilidades
  nacionais de vitória é melhor no Neutro (0,005, contra 0,014 calibrado e 0,050 pleno), porque em
  2022 o viés não mudou o vencedor; com 8 eventos, essa diferença diz pouco.

## O que mudou em relação à versão anterior e por quê
- **Backtest** (antes inexistente) calibra σ nacional, σ estadual, gl, contração da terceira via e
  pesos do 2º turno; mostra que o modelo anterior era estreito demais nas UFs (cobertura 95% ~86%).
- **Erro estruturado** (margem + terceira via + resíduo) no lugar de erro i.i.d. por candidato.
- **Viés com incerteza** (posterior empírica, encolhida, por instituto) no lugar do cenário binário;
  as visões Neutro e Pleno ficam como sensibilidade. A "média 50/50" saiu.
- **House effects hierárquicos** (τ estimado) no lugar do ridge com dp fixo.
- **Estados:** piso de erro das pesquisas estaduais, fator regional (1,5 → 4,5 p.p.) e dp do prior
  (4 → 7,0/4,5 p.p.) calibrados; SP passa de ~4% para 5% (calibrado) / 11% (neutro).
- **Segmentos:** prior demográfico (AP, GO e 1º turno), ajuste de comparecimento sem dupla contagem,
  dados de segmento no painel.
- **2º turno:** transferência pesa mais (0,7) — no backtest, a via de transferência a partir do 1º
  turno errou menos que as pesquisas de 2º turno feitas antes do 1º turno.
- **Dados:** pesquisas de véspera incluídas, Datafolha 3/10 em válidos, Gerp sinalizada, deduplicação.

## Limitações
- **Poucas eleições:** 3 no 1º turno, 2 no 2º turno projetado na véspera do 1º. O prior de viés e
  as coberturas são estimativas grosseiras; os PITs das UFs de um mesmo ano são correlacionados.
- O erro de 2022 no 1º turno, medido pela média ampla (incluindo institutos que erraram para o outro
  lado), foi pequeno (+0,8 p.p. em p2); o viés calibrado depende muito de 2014 e 2018.
- **Decisão no 1º turno** (19% calibrado; 15% neutro) fica bem acima dos mercados (~5%): reflete
  as caudas t e o dp de 4 p.p. escolhido no backtest.
- Pesquisas estaduais: quase só uma rodada Quaest; AP sem n e sem 2º turno; GO sem 2º turno.
- Matriz de transferência de subamostras pequenas de uma pesquisa; no backtest usou-se a matriz
  implícita das pesquisas pareadas (sem a Quaest por candidato).
- Prior demográfico e ajuste de comparecimento não testados no backtest (seriam vazamento).
- O adversário de 2014 (Aécio) é o 2º na média final por instituto, mas Marina estava à frente na
  média simples da última semana: em disputas a três, a escolha do adversário é frágil.
- Quaest (2–3/10), AtlasIntel final, Futura e Veritá de véspera não estavam publicadas na coleta.
- O 2º turno é projetado em 3/10; fatos entre os turnos não estão no modelo.

## Neutralidade
O modelo usa apenas pesquisas registradas, resultados oficiais do TSE e parâmetros documentados
com origem. O viés calibrado sai de uma regra empírica aplicada a qualquer erro histórico, nos dois
sentidos. As três visões aparecem sempre lado a lado com os mercados. Os eventos da linha do tempo
são factuais, com fonte, auditados para equilíbrio (`data/auditoria_neutralidade.md`) e não mudam
nenhum número. As cores (violeta e verde-azulado) não são partidárias e foram validadas para
daltonismo e contraste.
