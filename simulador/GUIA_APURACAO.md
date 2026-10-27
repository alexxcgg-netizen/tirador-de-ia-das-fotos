# Guia para hoje à noite: como ler a apuração do 1º turno (4/10/2026)

Urnas fecham às 17h de Brasília (20h UTC). Os números abaixo são **% dos votos válidos** e vêm da rodada
pré-eleitoral do simulador (`web/resultados.json`, 3–4/10). Tabelas completas: `data/benchmarks_uf.csv` e
`web/benchmarks.json` (gerados por `python simulador/benchmarks.py`). Histórico da ordem de apuração:
`APURACAO_2022_ORDEM.md`.

## 1. Cinco regras para não se enganar

1. **Não leia a margem nacional parcial.** Em 2022 Bolsonaro liderou até ~67% apurado e Lula terminou
   5,2 p.p. à frente. O Sul/Sudeste/Centro-Oeste é totalizado antes do Norte/Nordeste. Pela ordem de 2022, com
   10–20% apurado o esperado hoje é **Flávio ~8 a 12 p.p. à frente nas duas visões do modelo**; isso não é
   notícia.
2. **Leia UFs quase fechadas (≥ 95% apurado) contra o benchmark da própria UF**, não contra o total nacional.
3. **Uma UF isolada quase não distingue as visões.** Calibrado e neutro diferem ~1,6 p.p. em cada UF; o erro
   de uma UF é de 4–5 p.p. O sinal está no **padrão**: quantas UFs grandes caem de cada lado da linha de
   indiferença, ponderadas por eleitores.
4. **As duas visões podem errar juntas, para qualquer lado.** Lula acima de ~48 nacional é mais pró-Lula que as
   duas visões (as pesquisas teriam subestimado Lula); Lula abaixo de ~42 é mais pró-Flávio que o calibrado (e
   perto da visão "viés histórico pleno", Lula 43,3 / Flávio 48,1). Não force o resultado em uma das duas.
5. **Compare com 2022 só como referência de geografia.** O modelo espera Lula abaixo de 2022 em quase todas as
   UFs (−4,0 p.p. nacional no calibrado, −2,4 no neutro); "Lula perde votos frente a 2022 no Nordeste" é o
   esperado, não surpresa. A pergunta é: perde mais ou menos que o esperado?

## 2. Benchmarks nacionais

| | Calibrado (principal) | Neutro (viés 0) | Linha de indiferença | 3:1 a favor do calibrado | 3:1 a favor do neutro | 2022 (1º turno) |
|---|---|---|---|---|---|---|
| Lula | 44,4 (p10–p90 40,3–48,6) | 46,1 (42,2–50,0) | **45,2** | ≤ 38,7 | ≥ 51,8 | 48,4 |
| Flávio | 46,8 (42,6–51,1) | 45,2 (41,2–49,1) | **46,0** | ≥ 52,8 | ≤ 39,2 | 43,2 (Bolsonaro) |
| Margem Lula − Flávio | −2,4 (−10,6 a +5,8) | +0,9 (−6,8 a +8,6) | **−0,8** | ≤ −13,5 | ≥ +12,0 | +5,2 |

Como ler: **resultado final de Lula abaixo de 45,2 (ou margem abaixo de −0,8) deixa o calibrado mais provável
que o neutro; acima, o neutro.** As duas visões estão próximas (diferença de 1,7 p.p. contra dp ~3,2), então
mesmo o resultado final só dá razão de 3:1 longe do centro. O que se aprende de verdade é **o tamanho e o sinal
do erro das pesquisas**: a média das pesquisas (neutro) dava Lula 46,1; o calibrado espera Lula 1,6 p.p. abaixo
disso, como nos 1º turnos de 2014/18/22.

## 3. UFs a observar (decididas no 1º turno do mapa e grandes colégios)

Lula e Flávio: média (p10–p90). Linha = valor final na UF em que calibrado e neutro empatam; abaixo dela para
Lula (acima para Flávio) favorece o calibrado.

| UF | % eleit. | Lula calibrado | Lula neutro | Linha Lula | Flávio calibrado | Flávio neutro | Linha Flávio | 2022 Lula / Bolsonaro |
|---|---|---|---|---|---|---|---|---|
| SP | 21,5 | 38,3 (32,8–43,9) | 40,0 (34,6–45,4) | 39,2 | 50,4 (44,8–56,0) | 48,7 (43,2–54,2) | 49,6 | 40,9 / 47,7 |
| MG | 10,3 | 43,2 (37,3–49,1) | 45,0 (39,3–50,7) | 44,1 | 47,1 (41,1–53,1) | 45,3 (39,5–51,1) | 46,2 | 48,3 / 43,6 |
| RJ | 8,1 | 38,5 (32,6–44,6) | 40,4 (34,5–46,2) | 39,5 | 53,7 (47,6–59,7) | 51,9 (46,0–57,7) | 52,8 | 40,7 / 51,1 |
| BA | 7,1 | 60,7 (54,1–67,0) | 62,3 (56,0–68,3) | 61,5 | 33,2 (26,9–39,8) | 31,6 (25,6–37,9) | 32,4 | 69,7 / 24,3 |
| RS | 5,4 | 40,2 (33,4–47,0) | 42,0 (35,3–48,7) | 41,0 | 51,7 (44,8–58,5) | 49,9 (43,1–56,6) | 50,8 | 42,3 / 48,9 |
| PR | 5,4 | 32,3 (25,5–39,3) | 33,8 (27,0–40,8) | 33,0 | 56,5 (49,4–63,5) | 55,0 (47,8–61,9) | 55,8 | 36,0 / 55,3 |
| PE | 4,6 | 62,8 (56,2–69,1) | 64,4 (58,1–70,4) | 63,6 | 31,4 (25,1–38,0) | 29,9 (23,8–36,1) | 30,6 | 65,3 / 29,9 |
| PA | 3,9 | 46,9 (40,0–53,7) | 48,5 (41,9–55,2) | 47,7 | 45,5 (38,6–52,4) | 43,8 (37,1–50,4) | 44,6 | 52,2 / 40,3 |
| GO | 3,2 | 33,5 (27,2–39,9) | 35,0 (28,8–41,3) | 34,2 | 53,8 (47,2–60,3) | 52,3 (45,8–58,7) | 53,1 | 39,5 / 52,2 |
| ES | 1,9 | 37,5 (30,9–44,1) | 39,2 (32,7–45,7) | 38,3 | 53,6 (46,9–60,3) | 51,9 (45,3–58,5) | 52,8 | 40,4 / 52,2 |
| AM | 1,8 | 45,4 (37,9–52,9) | 47,1 (39,8–54,4) | 46,3 | 46,9 (39,4–54,4) | 45,2 (37,9–52,6) | 46,1 | 49,6 / 42,8 |
| AL | 1,5 | 50,6 (43,8–57,4) | 52,5 (45,9–59,0) | 51,6 | 43,9 (37,2–50,8) | 42,1 (35,5–48,7) | 43,0 | 56,5 / 36,0 |
| DF | 1,4 | 36,7 (30,2–43,5) | 38,2 (31,7–44,8) | 37,5 | 53,8 (47,0–60,5) | 52,3 (45,6–58,9) | 53,1 | 36,9 / 51,6 |
| TO | 0,7 | 42,5 (35,2–49,8) | 44,0 (36,9–51,2) | 43,3 | 47,0 (39,7–54,4) | 45,5 (38,3–52,7) | 46,3 | 50,4 / 44,0 |
| AP | 0,4 | 40,2 (33,4–47,2) | 41,8 (35,0–48,6) | 41,0 | 53,3 (46,3–60,2) | 51,8 (44,9–58,5) | 52,5 | 45,7 / 43,4 |

Demais UFs (incluindo exterior, ZZ) no CSV. Disputadas no 1º lugar do 1º turno segundo o modelo: **PA, AM, TO,
MG, AL** (e, com menor chance, AP).

**Indicador simples para a noite:** para cada UF com ≥ 95% apurado, calcule `Lula real − Linha Lula` e faça a
média ponderada por eleitores (coluna `pct_eleitorado`). Média negativa e consistente entre regiões → calibrado;
positiva → neutro; muito além de ±2–3 p.p. → as pesquisas erraram mais que as duas visões supõem. Cuidado: as
primeiras UFs fechadas são do Sul/Sudeste/CO; espere pelo menos uma grande do Nordeste (BA, PE, CE) antes de
concluir, porque o erro tem componente regional (eixo NE/N x S/CO no modelo).

## 4. Bellwethers (2006–2022)

UFs cuja fatia do PT nos dois primeiros ficou mais perto da nacional (desvio absoluto médio em 10 disputas,
1º e 2º turnos de 2006 a 2022; TSE, `data/resultados_uf_2002_2022.csv`):

| UF | Desvio médio (p.p.) | Lean médio | Lean 1º turno 2022 | Acertou 1º colocado (1T) | Acertou vencedor (2T) |
|---|---|---|---|---|---|
| **MG** | **2,0** | +0,1 | −0,3 | 5/5 | 5/5 |
| PA | 5,6 | +4,3 | +3,6 | 4/5 | 4/5 |
| TO | 5,8 | +5,8 | +0,5 | 5/5 | 4/5 |
| AP | 7,1 | +6,3 | −1,6 | 5/5 | 4/5 |
| ES | 7,1 | −5,2 | −9,2 | 3/5 | 2/5 |
| AL | 7,8 | +7,2 | +8,2 | 4/5 | 4/5 |

**Minas Gerais é o termômetro:** quem venceu em MG venceu o Brasil em todas as eleições de 2006 a 2022, e a
fatia do PT nos dois primeiros em MG ficou em média +0,1 p.p. da nacional (desvio absoluto médio de 2,0 p.p.). O modelo espera MG um pouco menos
pró-Lula que o país neste ano (Lula 43,2 em MG x 44,4 nacional no calibrado), então o MG final é um bom
estimador do nacional com ~1 p.p. de folga. Atenção: MG costuma fechar antes do Nordeste.

Municípios grandes (≥ 100 mil válidos) mais próximos do nacional, PT x Bolsonaro no 1º turno de **2018 e 2022**
(o repositório não tem dados municipais de 2006–2014): Montes Claros (MG, desvio 1,8), Ananindeua (PA, 2,3),
Castanhal (PA, 2,5), Guarapuava (PR, 2,6), Ribeirão das Neves (MG, 2,8), Itaquaquecetuba (SP, 2,9), Belém (PA,
3,1), Natal (RN, 3,3). Dois pontos por município são pouco; use como curiosidade, não como sinal.

## 5. Ordem de apuração: o que esperar no relógio

Pela ordem de 2022 escalada para o gap regional esperado em 2026 (detalhes em `APURACAO_2022_ORDEM.md`), margem
parcial Lula − Flávio esperada:

| % apurado | Calibrado | Neutro | Linha de indiferença |
|---|---|---|---|
| 10% | −11,7 | −8,3 | −10,0 |
| 35% | −10,0 | −6,6 | −8,3 |
| 52% | −8,2 | −4,9 | −6,5 |
| 70% | −6,7 | −3,4 | −5,1 |
| 97% | −3,3 | 0,0 | −1,7 |
| 100% | −2,4 | +0,9 | −0,8 |

Ou seja: Flávio à frente durante quase toda a noite é compatível com as duas visões; uma margem parcial
**acima** da coluna "neutro" no mesmo % apurado sugere um resultado melhor para Lula que a média das pesquisas;
**abaixo** da coluna "calibrado", melhor para Flávio que o calibrado. É ilustrativo (a ordem de 2026 pode
mudar); prefira as UFs fechadas e a projeção por UF de `resultado_1t.py --rodar-tudo`, que completa as UFs
parciais com a previsão.

## 6. Decisão no 1º turno

Para vencer no 1º turno é preciso mais de 50% dos válidos. Probabilidades pré-eleitorais: calibrado 21% (Lula 5,
Flávio 16), neutro 16% (Lula 10, Flávio 7). Com a terceira via somando ~9% no modelo, 50% exige o líder ~9 p.p.
à frente do segundo no resultado final. No parcial, por causa da ordem de apuração, Flávio acima de 50% com
menos de ~70% apurado **não** indica decisão no 1º turno.
