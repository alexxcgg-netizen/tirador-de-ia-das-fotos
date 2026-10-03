# Modelo alternativo: contraprova independente do simulador

Este é um segundo modelo de previsão da eleição presidencial de 2026 (1º turno em
4/10, 2º turno em 25/10; data de referência 3/10/2026). Ele existe para **conferir o
simulador principal** (`simulador/`). A metodologia é diferente de propósito: quando
os dois modelos concordam, o resultado não depende das escolhas de modelagem de um
deles; quando discordam, a diferença aponta qual premissa decide o resultado.

O modelo só **lê** `simulador/data/*.csv` e não altera nada no simulador. Os números
abaixo vêm de `resultados_alt.json`, rodado com o estado dos CSVs registrado em
`meta.dados` (hash SHA-256 dos arquivos), que inclui as pesquisas da véspera
(Datafolha, Quaest e Futura de 2–3/10).

```
python modelo_alternativo/rodar_alt.py            # 500 mil simulações por variante (~70 s)
python modelo_alternativo/rodar_alt.py --rapido   # versão curta para teste
python -m pytest modelo_alternativo/tests         # 13 testes (~6 s)
```

## Método

### 1. Agregação bayesiana dinâmica das pesquisas nacionais

Segue a linha de Linzer (2013) e do modelo da *Economist* (2020). Cada quantidade é
modelada em escala de log-razão. A intenção de voto latente `mu_t` segue um
**passeio aleatório diário**, e cada pesquisa a observa com o **efeito do instituto**
somado a um ruído:

```
y_j  = mu_{t_j} + h_{instituto(j)} + e_j,    e_j ~ N(0, s_j² + tau²)
mu_t = mu_{t-1} + eta_t,                     eta_t ~ N(0, omega²)
h    ~ N(0, sigma_h² (I − 11ᵀ/K))           (efeitos de instituto somam zero)
```

* `s_j²` é a variância amostral da log-razão, `(1/a + 1/b)/n`. `tau²` é o erro extra
  além do amostral, estimado.
* **Componentes**. No 1º turno são três:
  * `z1 = log(Lula/Flávio)`;
  * `z2 = log(demais/(Lula+Flávio))`, em que "demais" é tudo o que não vai para os dois
    primeiros, inclusive os candidatos não listados;
  * `log(c/Flávio)` para Renan, Cury, Caiado e Zema, usado apenas para dividir "demais"
    entre eles.

  No 2º turno o componente é `zq = log(Lula/Flávio)`.
* **A base não importa**. Como o modelo usa razões, tanto faz se a pesquisa foi
  publicada em votos totais ou em votos válidos. A linha do Datafolha de 3/10, que já
  esteve gravada em votos válidos, entraria sem precisar de conversão. Cenários de 1º
  turno com candidatos que não concorrem (Tarcísio, Ratinho, Ciro) ficam fora; o 2º
  turno dessas pesquisas é usado.
* **Ajuste**:
  * Um **filtro de Kalman** com estado aumentado `[mu, h_1..h_K]` dá a verossimilhança
    marginal exata.
  * Os hiperparâmetros `(omega, tau, sigma_h)` são amostrados por **MCMC**
    (Metropolis adaptativo; 4.000 iterações, 1.500 de aquecimento, priors meia-normais).
  * Para cada sorteio, o posterior de `mu` na véspera é uma normal. O posterior completo
    é uma mistura dessas normais, amostrada diretamente.

  Tudo roda em NumPy, sem dependências novas.
* **Soma zero dos efeitos de instituto**. O modelo assume que o instituto médio não
  tem viés. O viés da indústria como um todo não se identifica com as pesquisas; ele
  entra pelo erro histórico (item 2).

**Agregado na véspera** (média do posterior):

| Quantidade | Valor |
|---|---|
| Lula, % dos votos válidos no 1º turno | **45,1** |
| Flávio, % dos votos válidos no 1º turno | **43,8** |
| Demais (Renan 3,4; Cury 3,0; Caiado 3,0; Zema 1,1; não listados 0,7) | 11,1 |
| Fatia de Lula entre os dois primeiros no 1º turno | 50,7 |
| **Lula no 2º turno** | **49,5** (dp do posterior ≈ 0,5 p.p.) |

Efeitos de instituto no 2º turno, em p.p. aproximados (positivo = mais Lula que o
instituto médio):

| Instituto | Efeito |
|---|---|
| CNT/MDA | +2,8 |
| Datafolha | +0,9 |
| AtlasIntel | +0,9 |
| Quaest | +0,5 |
| PoderData | −0,3 |
| Vox | −1,3 |
| Palver | −1,3 |
| Gerp | −2,0 |
| Futura | −2,5 |

### 2. Erro do dia da eleição: bootstrap empírico de 2014, 2018 e 2022

O erro não vem de uma distribuição paramétrica. O mesmo agregador foi rodado em 2014,
2018 e 2022 com as pesquisas disponíveis até a véspera do 1º turno, e o erro de cada
eleição é **resultado menos a média final do modelo**:

| Eleição | Erro em z1 (PT/adv.) | Erro em z2 (demais) | Erro em zq (2º turno, medido na véspera do 1º) |
|---|---|---|---|
| 2014 | −0,36 (fatia PT bipartidária 64,0 → 55,4; Aécio subiu na reta final) | −0,18 | sem pesquisas de 2º turno antes do 1º |
| 2018 | +0,01 | −0,38 (demais 32,3 → 24,7) | −0,11 (47,7 → 44,9) |
| 2022 | −0,03 | −0,49 (13,0 → 8,4) | −0,18 (55,4 → 50,9) |

Como a simulação usa esses erros:

* **Sorteia uma eleição inteira**. O vetor `(z1, z2, zq)` sai junto, o que preserva a
  correlação entre o 1º e o 2º turno. Quando sai 2014, o erro do 2º turno vem de 2018
  ou 2022.
* **Suaviza com bootstrap** (Silverman & Young 1987, com correção de variância). O
  núcleo tem a **forma empírica** das discrepâncias entre institutos na véspera (27
  vetores no 1º turno, 20 no 2º). A largura de banda segue a regra de Silverman, e a
  correção faz o resultado manter a média e a variância do conjunto de erros
  observados. Sem suavização, só três valores seriam possíveis.
* **Variante `neutro`, a principal**. O sinal do erro partidário (z1 e zq) é sorteado:
  a magnitude é a histórica e a direção é agnóstica. O erro de "demais" (contração da
  terceira via, ou voto útil) não é partidário e mantém o sinal: houve contração nos
  três anos.
* **Variante `historico`**. É a `neutro` deslocada pela média dos erros com sinal. Nos
  três anos as pesquisas superestimaram o lado do PT, em média −0,12 em z1 e −0,15 em
  zq. Não é uma previsão de que isso vá se repetir; mostra o que acontece se se repetir.

### 3. Estados: swing uniforme a partir de 2022, sem pesquisas estaduais

* Para cada UF, a fatia bipartidária de 2022 recebe o mesmo swing nacional simulado,
  em p.p. (Lula × Bolsonaro no 2º turno; PT × adversário no 1º).
* Soma-se um **vetor de desvios estaduais** sorteado do histórico do TSE:
  `(UF_t − UF_{t−4}) − (BR_t − BR_{t−4})` para 2002→2006, …, 2018→2022.
* O vetor é sorteado inteiro, o que preserva a correlação espacial, por exemplo o
  realinhamento do Nordeste em 2006. Ele recebe a mesma suavização com correção de
  variância.
* No `neutro`, o sinal do vetor também é sorteado.
* A probabilidade por UF no 2º turno é condicional a um confronto Lula × Flávio.

### 4. Simulação

São **500.000 simulações por variante**, em lotes de 100 mil. Em cada simulação:

* sorteia-se o posterior do agregado e o erro empírico;
* calcula-se o 1º turno: alguém passa de 50% dos válidos? Quem são os dois primeiros?
* se não houver vencedor, calcula-se o 2º turno;
* calculam-se as UFs.

O erro de Monte Carlo das probabilidades é de no máximo 0,07 p.p.

## Resultados (3/10/2026)

| Probabilidade | **Neutro** | Histórico |
|---|---|---|
| **Lula vence a eleição** | **49,4%** | 18,9% |
| **Flávio Bolsonaro vence a eleição** | **50,6%** | 81,1% |
| Decide no 1º turno | 36,4% (Lula 20,9; Flávio 15,5) | 39,8% (Lula 9,0; Flávio 30,8) |
| Há 2º turno Lula × Flávio | 63,6% | 60,2% |
| Lula e Flávio são os dois primeiros | ≈100% | ≈100% |
| Lula em 1º no 1º turno | 58,0% | 27,4% |

Faixas de votos válidos (mediana, intervalo de 80%; no neutro também o de 90%):

| Quantidade | Neutro | Histórico |
|---|---|---|
| Lula, 1º turno | 46,8 (40,0–52,5; 90%: 38,3–53,9) | 44,0 (37,2–49,7) |
| Flávio, 1º turno | 45,5 (38,4–51,3; 90%: 37,0–52,9) | 48,3 (41,2–54,0) |
| Demais, 1º turno | 8,1 (6,8–9,7) | 8,1 (6,8–9,7) |
| Renan / Cury / Caiado / Zema | 2,4 / 2,2 / 2,2 / 0,8 | idem |
| **Lula, 2º turno** | **49,5 (44,6–54,5; 90%: 43,2–55,9)** | 45,9 (41,0–50,8) |

### UFs: P(Lula vence a UF no 2º turno)

| UF | Neutro | Lula 2º turno, mediana (p10–p90) | Lula à frente no 1º turno (neutro) | Histórico |
|---|---|---|---|---|
| CE | 100% | 68,6 (59,3–78,0) | 100% | 99% |
| BA | 99% | 70,8 (59,2–82,4) | 99% | 100% |
| PI | 99% | 75,5 (61,2–90,0) | 98% | 100% |
| SE | 94% | 65,9 (53,1–78,8) | 91% | 96% |
| MA | 92% | 69,8 (51,9–87,8) | 97% | 96% |
| RN | 92% | 63,8 (51,1–76,6) | 92% | 93% |
| PB | 91% | 65,3 (50,8–79,8) | 90% | 93% |
| PE | 91% | 65,6 (51,0–80,2) | 85% | 95% |
| AL | 73% | 57,3 (42,4–72,5) | 75% | 78% |
| PA | 67% | 53,4 (43,7–63,2) | 66% | 62% |
| TO | 50% | 50,0 (37,7–62,3) | 55% | 38% |
| AM | 49% | 49,7 (35,3–64,0) | 54% | 28% |
| MG | 40% | 48,8 (43,0–54,7) | 53% | 9% |
| AP | 34% | 47,3 (39,2–55,4) | 46% | 5% |
| RJ | 21% | 42,1 (29,7–54,6) | 26% | 3% |
| SP | 17% | 43,4 (34,6–52,2) | 25% | 6% |
| RS | 16% | 42,3 (32,4–52,3) | 25% | 6% |
| ES | 10% | 40,6 (31,3–50,0) | 14% | 2% |
| DF | 7% | 39,8 (31,0–48,5) | 21% | 0% |
| MS | 5% | 39,1 (31,0–47,4) | 7% | 0% |
| RR | 3% | 22,6 (3,6–41,6) | 8% | 0% |
| AC | 2% | 28,5 (14,2–42,5) | 11% | 0% |
| SC | 2% | 29,3 (17,1–41,6) | 4% | 0% |
| PR | 1% | 36,3 (29,0–43,5) | 4% | 0% |
| GO | 0% | 39,9 (34,6–45,3) | 7% | 0% |
| RO | 0% | 28,0 (19,5–36,5) | 0% | 0% |
| MT | 0% | 33,6 (26,2–40,9) | 1% | 0% |

As faixas por UF são largas porque os desvios estaduais históricos são grandes: o
realinhamento de 2006 chega a mais de 10 p.p. em algumas UFs. Este modelo não usa
pesquisas estaduais.

### Sensibilidade (neutro; 100 mil simulações)

| Variação | Lula vence | Decide no 1º turno | Lula em 1º no 1º turno |
|---|---|---|---|
| Base (2014 + 2018 + 2022, com suavização) | 49,4% | 36,4% | 58,0% |
| Erros só de 2018 e 2022 | 46,4% | **0,0%** | 84,8% |
| Bootstrap puro, sem suavização | 50,0% | 33,3% | 72,4% |

A probabilidade de decisão no 1º turno **depende inteiramente de 2014**. O erro de
cerca de 12 p.p. na margem PT × adversário naquele ano, com a arrancada de Aécio sobre
Marina na véspera, é o único da amostra grande o bastante para levar alguém a 50%. Com
só três eleições, essa é a principal fragilidade de um erro empírico. O número precisa
ser lido junto com essa tabela.

## Backtest 2018 e 2022

Regras do backtest:

* O agregado de cada ano usa **só pesquisas com campo encerrado antes do 1º turno**.
* O erro do dia da eleição é **deixa-uma-eleição-de-fora**: para 2018, vem de 2014 e
  2022; para 2022, de 2014 e 2018.
* Os desvios estaduais excluem todo par de eleições que contenha o ano testado, para
  evitar vazamento.
* A base estadual é a eleição anterior: 2014 para 2018 e 2018 para 2022.
* São 500 mil simulações por ano e variante.

| Métrica (2018 + 2022) | Neutro | Histórico | Ideal |
|---|---|---|---|
| Cobertura nacional: intervalo de 50% / 80% / 95% (8 quantidades: PT, adversário e demais no 1º turno; PT no 2º turno) | 75% / 75% / 100% | 62% / 88% / 100% | 50 / 80 / 95 |
| Cobertura por UF no 2º turno: 50% / 80% / 95% (54 casos) | 46% / 83% / 93% | 59% / 76% / 96% | 50 / 80 / 95 |
| Brier nacional (PT vence; PT 1º no 1º turno) | 0,044 | 0,107 | 0 (moeda = 0,25) |
| Brier nacional (8 eventos, inclui "decide no 1º turno" e top-2) | 0,049 | 0,099 | |
| Brier por UF no 2º turno / 1º turno | 0,075 / 0,048 | 0,050 / 0,041 | |
| Log-loss por UF no 2º turno | 0,29 | 0,16 | |
| UFs com favorito certo no 2º turno | 50/54 (93%) | 50/54 | |

Probabilidades atribuídas na véspera do 1º turno, no neutro:

| Ano | PT vence | Decide no 1º turno | PT em 1º no 1º turno | Resultado |
|---|---|---|---|---|
| 2018 | 28,9% | 17,1% | 3,4% | Haddad perdeu; houve 2º turno; Bolsonaro em 1º |
| 2022 | 90,8% | 43,0% | 71,1% | Lula venceu; houve 2º turno; Lula em 1º |

Leitura:

* **No geral a calibração é razoável.** A cobertura por UF fica perto da nominal e o
  intervalo de 95% contém o resultado nacional nos 8 casos.
* **O ponto fraco é a decisão no 1º turno.** Em 2022 o modelo deu 43% de chance de não
  haver 2º turno. É a mesma fragilidade do erro de 2014 apontada na sensibilidade.
* **O histórico tem Brier por UF melhor e Brier nacional pior.** Nos dois anos testados,
  o viés pró-PT das pesquisas de fato ocorreu nos estados. Em 2022, porém, a variante
  deu só 44% a Lula em 1º no 1º turno, e ele terminou em 1º.
* **São só dois anos de teste.** As métricas têm variância alta e servem como checagem
  de sanidade, não como prova de calibração.

## Comparação com o simulador principal

`resultados_alt.json → comparacao_modelo_principal` lê `simulador/web/resultados.json`
no momento da execução, sem alterá-lo. O instantâneo de 22h51 UTC de 3/10:

| | Alternativo neutro | Principal neutro | Alternativo histórico | Principal calibrado / pleno |
|---|---|---|---|---|
| Lula vence | 49,4% | 43,1% | 18,9% | 20,4% / 11,4% |
| Decide no 1º turno | 36,4% | 15,7% | 39,8% | 20,6% / 31,9% |
| Há 2º turno Lula × Flávio | 63,6% | 84,3% | 60,2% | 79,4% / 68,1% |
| Lula em 1º no 1º turno | 58,0% | 56,6% | 27,4% | 34,5% / 23,7% |

**Onde os modelos concordam**:

* O agregado é praticamente o mesmo. No principal, a fatia de Lula entre os dois
  primeiros no 1º turno é 51,0% e no 2º turno é 49,6%; aqui, 50,7% e 49,5%. São
  métodos de agregação totalmente diferentes (média ponderada com efeitos aleatórios
  contra passeio aleatório com filtro de Kalman), e mesmo assim os efeitos de
  instituto também batem em sinal: CNT/MDA e Datafolha puxam para Lula; Futura, Gerp e
  Palver puxam para Flávio.
* **Sem viés, a eleição está perto de 50/50**: 43–49% para Lula.
* **Com o viés histórico, Flávio é favorito**: cerca de 80% (19–20% para Lula).

O ponto central é o mesmo nos dois modelos: a distância entre o cenário neutro e o
histórico é bem maior que a incerteza do agregado.

**Onde e por que discordam**:

1. **Decisão no 1º turno: 36% aqui contra 16% no principal.**
   * O principal usa erro paramétrico (t de Student, dp de cerca de 4 p.p. na fatia
     bipartidária).
   * Este modelo usa o erro empírico, dominado por 2014. Sem 2014, cai a 0%.
   * Os mercados davam cerca de 5% (`simulador/README.md`).
   * A verdade provavelmente está entre os dois modelos. O número é muito sensível a
     uma única observação.
2. **Lula vence no neutro: 49% contra 43%.** Aqui, o mesmo erro sorteado move o 1º e o
   2º turno juntos (vetor conjunto). Como Lula tem chance maior de passar de 50% no 1º
   turno, esse ganho compensa o 2º turno levemente desfavorável. No principal, o 2º
   turno tem erro próprio e menos 1º turnos decididos.
3. **UFs.**
   * O principal combina um prior demográfico com pesquisas estaduais.
   * Este usa só swing uniforme mais desvios históricos, daí faixas por UF mais largas.
   * Exemplo: em SP, P(Lula) é 17% aqui e cerca de 4% no principal (pela leitura do
     README dele). MG também fica mais incerta.

Resumo das diferenças de método:

| | Simulador principal | Modelo alternativo |
|---|---|---|
| Agregação | média ponderada por recência e √n, uma pesquisa por instituto, efeitos de instituto por máxima verossimilhança | passeio aleatório latente, todas as pesquisas, filtro de Kalman + MCMC nos hiperparâmetros |
| 1º turno | p2 (PT × adversário) e menores, com indecisos alocados por rejeição e 2ª opção | log-razões z1 e z2, indecisos ignorados (razões) |
| Erro do dia | t de Student paramétrico, viés da indústria com prior empírico-bayesiano encolhido | bootstrap dos vetores de erro observados, suavizado com núcleo empírico |
| Estados | prior demográfico + pesquisas estaduais + fatores regionais | swing uniforme de 2022 + vetores de desvio do TSE (2002–2022) |
| Correlação 1º/2º turno | erro do 2º turno correlacionado parametricamente | mesma eleição histórica sorteada para os dois turnos |

## Limitações

* **Só há três eleições com pesquisas no conjunto de dados**, e para o erro do 2º
  turno medido na véspera do 1º, só duas. Qualquer erro "empírico" com essa amostra é
  frágil; a suavização apenas evita que ele fique restrito a três pontos.
* **A soma zero dos efeitos de instituto depende de quais institutos publicaram.** Em
  2026 há vários institutos com poucas pesquisas e efeito pró-Flávio (Futura, Gerp,
  Palver, Vox).
* **A composição dos menores** vem só do posterior das pesquisas. O erro histórico
  "demais" é aplicado ao conjunto, sem erro individual por candidato menor.
* **O swing uniforme** ignora pesquisas estaduais e mudanças de composição do
  eleitorado entre 2022 e 2026.
* **Abstenção e brancos/nulos não são modelados.** Tudo é em votos válidos.
* **Como a base é usada.** A razão Lula/Flávio usa todas as pesquisas. "Demais" só
  entra quando há brancos, nulos e indecisos informados, ou quando todos os menores
  foram publicados.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `modelo_alt.py` | dados, filtro de Kalman, MCMC, erros históricos, bootstrap, swing estadual, simulação e métricas |
| `rodar_alt.py` | execução completa e geração de `resultados_alt.json` |
| `resultados_alt.json` | metadados (tempo, hash dos dados), agregado, erros, cenários `neutro` e `historico`, sensibilidade, backtest, comparação |
| `tests/test_modelo_alt.py` | testes: recuperação de parâmetros sintéticos no filtro e no MCMC, invariância à base, ausência de vazamento no backtest, simetria e preservação de variância do bootstrap, coerência das probabilidades |

Tempo de execução (Python 3.11 / NumPy 2.4, 1 núcleo): **cerca de 70 s no total**.
São cerca de 56 s de MCMC (4 anos × até 7 componentes), cerca de 4,5 s para as
1 milhão de simulações de 2026 e cerca de 8 s de backtest, com 4 milhões de
simulações.

Referências:

* Linzer, D. (2013). Dynamic Bayesian forecasting of presidential elections in the
  states. *JASA* 108(501).
* Heidemanns, Gelman & Morris (2020). An updated dynamic Bayesian forecasting model
  for the US presidential election. *HDSR*.
* Silverman, B. & Young, G. (1987). The bootstrap: to smooth or not to smooth?
  *Biometrika* 74(3).
