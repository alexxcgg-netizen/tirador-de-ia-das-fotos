# Nordeste no 1º turno de 2026 x 2022: swing, comparecimento, terceiros e aritmética do 2º turno

Leitura de 05/10/2026, com o 1º turno (04/10) totalizado no arquivo municipal do repositório. Todos os números marcados
**[calc]** são cálculo próprio a partir dos arquivos abaixo. Não há juízo sobre candidatos. Os cenários são
exercícios aritméticos condicionais, não previsões.

**Fontes e reprodução.** Script: `nordeste_dados_1t.py` (nesta pasta). Ele só lê os dados do repositório e grava os CSVs daqui.
- Votos: `modelo_municipal/data/mun_2026_1t.csv` (TSE, 1º turno 2026; números 13 Lula, 22 Flávio, 55 Caiado,
  70 Cury, 30 Zema, 14 Renan Santos), `hist_2022.csv` e `hist_2018.csv` (TSE munzona), e
  `simulador/data/resultados_uf_2002_2022.csv` (1º e 2º turnos por UF, 2014/2018/2022).
- Covariáveis municipais (`covariaveis_mun_ne.csv`, 1.794 municípios do NE, baixadas em 05/10/2026):
  - Bolsa Família: MDS MiSocial, set/2026, pessoas beneficiárias por código IBGE. O indicador é "pessoas no PBF / moradores do Censo 2022", em %.
  - Evangélicos: % da população com 10 anos ou mais, IBGE SIDRA 9537 (Censo 2022).
  - Renda domiciliar per capita: IBGE SIDRA 10295, v13431 (Censo 2022).
  - De-para TSE→IBGE e capitais: `betafcc/Municipios-Brasileiros-TSE`.
  - O IDHM municipal só existe para 2010 (Atlas), então a renda do Censo 2022 entra como proxy. O casamento das bases não teve perdas: 1.794 de 1.794 municípios.
- Comparecimento por segmento: `simulador/data/abstencao_segmentos_uf.csv`, que só tem 2022.
- Unidade padrão: **swing** = % de Lula nos válidos no 1T 2026 menos % de Lula nos válidos no 1T 2022, em p.p.
  **Δmargem** = (Lula − Flávio) em 2026 menos (Lula − Bolsonaro) em 2022, em votos.
- CSVs:
  - `nordeste_swing_municipios.csv`: um registro por município.
  - `nordeste_swing_cortes.csv`: os cortes abaixo.
  - `nordeste_regressoes_swing.csv`
  - `nordeste_terceiros_uf.csv`
  - `nordeste_comparecimento_1t2t_hist.csv`
  - `nordeste_cenarios_2t.csv`

---

## 0. Resumo numérico

| Indicador [calc] | Valor |
|---|---|
| Diferença nacional no 1T (Flávio − Lula) | **2.259 mil votos** (56,09 mi x 53,83 mi) |
| Lula no NE, % dos válidos: 2022 1T → 2026 1T | 66,8% → 63,8% (**−3,0 p.p.**); fatia de 2 candidatos −3,9 p.p. |
| Votos de Lula no NE: 2022 → 2026 | 21,75 mi → 21,46 mi (−291 mil) |
| Votos do 2º colocado no NE: Bolsonaro 2022 → Flávio 2026 | 8,79 mi → 10,39 mi (**+1,61 mi**) |
| Δmargem de Lula no NE | **−1,90 mi**, ou 22,5% da piora nacional (−8,45 mi). O NE tem 27,4% do eleitorado. |
| Municípios do NE em que Lula caiu | 97,0% dos municípios (86,9% dos válidos) |
| Comparecimento no NE no 1T (comparecimento/aptos) | 80,5% → 81,5% (**+1,0 p.p.**; Brasil: 79,05% → 78,88%) |
| Abstenção no NE no 1T 2026 | 8,04 mi; brancos e nulos: 1,80 mi |
| Caiado + Cury + Renan + Zema no NE | **1,77 mi** (5,2% dos válidos do NE; 19,5% do total desses 4 no Brasil) |

A perda de Lula no NE veio pouco da queda dos seus votos absolutos (−0,29 mi). Veio sobretudo do crescimento do
candidato do PL (+1,61 mi) sobre um eleitorado e um comparecimento maiores (+1,14 mi aptos, +1,37 mi votantes).
Também caiu o voto em terceiros no NE (2,04 mi → 1,81 mi) [calc].

---

## 1. Onde Lula perdeu terreno no NE

### 1.1 Por UF [calc]

| UF | munic. | válidos 2026 (mil) | Lula 22 % | Lula 26 % | swing p.p. | Bolsonaro 22 % | Flávio 26 % | terceiros 26 % | swing 2 cand. p.p. | Δ votos Lula (mil) | Δmargem (mil) | comp. 22 % | comp. 26 % | Δcomp. p.p. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MA | 217 | 4.005 | 68,8 | 64,0 | **−4,9** | 26,0 | 30,9 | 5,1 | −5,2 | −42 | −297 | 77,8 | 80,2 | +2,4 |
| PI | 224 | 2.143 | 74,3 | 71,0 | −3,3 | 19,9 | 24,1 | 4,9 | −4,2 | +3 | −107 | 82,3 | 82,7 | +0,4 |
| CE | 184 | 5.615 | 65,9 | 63,3 | −2,6 | 25,4 | 31,3 | 5,4 | **−5,3** | −26 | −404 | 82,5 | 84,4 | +1,9 |
| RN | 167 | 2.072 | 63,0 | 59,8 | −3,2 | 31,0 | 34,8 | 5,5 | −3,8 | −26 | −124 | 81,8 | 81,6 | −0,2 |
| PB | 223 | 2.513 | 64,2 | 61,3 | −2,9 | 29,6 | 33,1 | 5,6 | −3,5 | −14 | −128 | 82,7 | 82,6 | −0,1 |
| PE | 185 | 5.601 | 65,3 | 63,5 | −1,8 | 29,9 | 31,0 | 5,5 | −1,4 | −4 | −112 | 81,8 | 81,8 | 0,0 |
| AL | 102 | 1.819 | 56,5 | 54,7 | −1,8 | 36,0 | 40,4 | 4,8 | −3,5 | +21 | −93 | 77,6 | 79,4 | +1,7 |
| SE | 75 | 1.364 | 63,8 | 62,7 | −1,1 | 29,2 | 30,6 | 6,6 | −1,4 | +27 | −12 | 81,7 | 82,7 | +1,0 |
| BA | 417 | 8.533 | 69,7 | 66,1 | −3,6 | 24,3 | 28,6 | 5,3 | −4,3 | −230 | **−621** | 78,7 | 79,8 | +1,1 |
| **NE** | 1.794 | 33.665 | 66,8 | 63,8 | **−3,0** | 27,0 | 30,9 | 5,4 | −3,9 | −291 | **−1.897** | 80,5 | 81,5 | +1,0 |

- Em votos líquidos, a perda se concentra na **BA (−621 mil)**, no **CE (−404 mil)** e no **MA (−297 mil)**. Juntos são 70% da Δmargem do NE [calc].
- PE e SE tiveram os menores swings, puxados por Recife e Aracaju, onde Lula subiu.
- No CE, o swing nos válidos (−2,6) é menor que o de 2 candidatos (−5,3). Isso indica que parte do voto de terceiros de 2022 (Ciro) migrou para Flávio [calc; inferência ecológica não feita].

### 1.2 Capital x interior [calc]

| | munic. | válidos 26 (mil) | Lula 22 % | Lula 26 % | swing p.p. | swing 2 cand. | Δmargem (mil) | Δcomp. p.p. |
|---|---|---|---|---|---|---|---|---|
| Capitais (9) | 9 | 6.763 | 55,8 | 55,3 | **−0,6** | −1,9 | −223 | 0,0 |
| Interior | 1.785 | 26.902 | 69,7 | 65,9 | **−3,8** | −4,4 | **−1.674** | +1,3 |

Por UF, o swing no interior é sempre pior que o da capital:

| UF | swing capital | swing interior | Δmargem capital (mil) | Δmargem interior (mil) | Δcomp. capital | Δcomp. interior |
|---|---|---|---|---|---|---|
| MA (São Luís) | −2,0 | −5,5 | −27 | −270 | +0,2 | +2,7 |
| PI (Teresina) | −1,2 | −4,1 | −19 | −88 | +0,3 | +0,5 |
| CE (Fortaleza) | +0,3 | −4,0 | −61 | −343 | +3,5 | +1,4 |
| RN (Natal) | −1,2 | −4,1 | −16 | −108 | −0,4 | −0,2 |
| PB (João Pessoa) | −0,9 | −3,4 | −9 | −118 | −1,1 | +0,1 |
| PE (Recife) | +1,3 | −2,6 | +19 | −130 | −1,8 | +0,4 |
| AL (Maceió) | +0,7 | −2,9 | −12 | −81 | +0,3 | +2,3 |
| SE (Aracaju) | +1,5 | −2,2 | +4 | −16 | +0,2 | +1,3 |
| BA (Salvador) | −1,7 | −4,0 | −102 | −519 | −2,2 | +1,8 |

**88% da perda líquida do NE ocorreu no interior** [calc]. Fortaleza é exceção no swing (+0,3), mas o comparecimento
maior gerou Δmargem negativa (−61 mil), porque Flávio cresceu mais em votos absolutos.

### 1.3 Por porte do município (aptos 2026) [calc]

| Porte | munic. | válidos 26 (mil) | Lula 22 % | Lula 26 % | swing | swing 2 cand. | Δmargem (mil) | Δcomp. |
|---|---|---|---|---|---|---|---|---|
| <10 mil | 750 | 3.616 | 76,3 | 71,9 | −4,4 | −5,2 | −237 | +1,7 |
| 10–20 mil | 573 | 6.249 | 74,5 | 70,3 | −4,3 | −5,0 | −423 | +2,5 |
| 20–50 mil | 349 | 7.904 | 72,3 | 68,2 | −4,1 | −4,8 | −519 | +1,9 |
| 50–100 mil | 77 | 3.946 | 65,7 | 61,7 | −4,0 | −4,5 | −262 | +0,3 |
| 100–200 mil | 25 | 2.671 | 58,4 | 56,0 | −2,4 | −3,3 | −130 | +0,3 |
| >200 mil | 20 | 9.279 | 56,5 | 55,5 | **−1,0** | −2,0 | −326 | −0,4 |

Gradiente monotônico: quanto menor o município, maior a queda. Abaixo de 100 mil aptos o swing é de cerca de −4 a −4,4 p.p.

### 1.4 Por intensidade de Bolsa Família (pessoas no PBF / moradores; quintis de municípios) [calc]

| Quintil | faixa % | válidos 26 (mil) | Lula 22 % | Lula 26 % | swing | swing 2 cand. | Δmargem (mil) | Δcomp. |
|---|---|---|---|---|---|---|---|---|
| Q1 (baixo) | 9–42 | 17.946 | 60,3 | 58,1 | −2,2 | −3,1 | −894 | +0,1 |
| Q2 | 42–48 | 4.901 | 71,0 | 67,0 | −4,0 | −4,8 | −326 | +1,6 |
| Q3 | 48–53 | 3.829 | 75,0 | 71,0 | −4,0 | −4,7 | −243 | +2,0 |
| Q4 | 53–58 | 3.662 | 75,5 | 71,0 | −4,6 | −5,2 | −247 | +2,4 |
| Q5 (alto) | 58–87 | 3.327 | 77,2 | 72,9 | −4,3 | −5,0 | −187 | +2,6 |

Os municípios com mais PBF tiveram queda maior em p.p. (≈ −4 a −4,6 contra −2,2 no Q1). Mas o Q1 reúne as capitais e
as cidades grandes. Controlando porte, capital e UF (seção 1.7), o efeito do PBF desaparece (coef. ≈ 0). Nos
quintis altos de PBF, o comparecimento subiu mais (+2,4 a +2,6 p.p.), e mesmo assim Lula perdeu fatia.

### 1.5 Por % de evangélicos (Censo 2022; quintis de municípios) [calc]

| Quintil | faixa % | válidos 26 (mil) | Lula 22 % | Lula 26 % | swing | swing 2 cand. | Δmargem (mil) | Δcomp. |
|---|---|---|---|---|---|---|---|---|
| Q1 (baixo) | 3–11 | 3.126 | 78,4 | 74,2 | −4,2 | −5,2 | −197 | +1,7 |
| Q2 | 11–14 | 3.817 | 77,2 | 72,9 | −4,3 | −5,1 | −251 | +2,1 |
| Q3 | 14–18 | 4.607 | 74,2 | 70,1 | −4,1 | −5,1 | −315 | +1,7 |
| Q4 | 18–24 | 6.136 | 69,0 | 65,4 | −3,6 | −4,4 | −383 | +1,6 |
| Q5 (alto) | 24–59 | 15.979 | 59,2 | 57,0 | **−2,1** | −2,9 | −751 | +0,3 |

Lula perdeu **menos** onde há mais evangélicos, de forma contraintuitiva. Esses municípios já davam votação alta a
Bolsonaro em 2022, e a nova perda de 2026 se concentrou no eleitorado católico do interior, que era majoritariamente
lulista. Com efeitos fixos de UF e controles, o coeficiente de evangélicos continua positivo (+0,45 p.p. por DP) [calc].

### 1.6 Por renda domiciliar per capita (Censo 2022; quintis de municípios) [calc]

| Quintil | faixa R$ | válidos 26 (mil) | Lula 22 % | Lula 26 % | swing | swing 2 cand. | Δmargem (mil) | Δcomp. |
|---|---|---|---|---|---|---|---|---|
| Q1 (baixo) | 359–644 | 3.395 | 78,3 | 74,0 | −4,3 | −5,2 | −201 | +2,8 |
| Q2 | 644–703 | 3.579 | 75,8 | 71,7 | −4,1 | −4,9 | −222 | +2,2 |
| Q3 | 703–759 | 3.891 | 74,0 | 69,9 | −4,1 | −5,0 | −264 | +2,1 |
| Q4 | 759–840 | 4.412 | 70,7 | 66,5 | −4,2 | −4,9 | −306 | +1,7 |
| Q5 (alto) | 840–2.566 | 18.388 | 60,6 | 58,4 | −2,2 | −3,1 | −903 | +0,1 |

O padrão é o mesmo nos quatro primeiros quintis, com queda quase uniforme de cerca de −4 a −4,3 p.p. em todo o
interior pobre, e queda menor no Q5, que é urbano.

### 1.7 Distribuição do swing e regressões [calc]

**Distribuição municipal do swing (p.p.):**
- Percentis: p5 −8,7; p10 −7,3; p25 −5,6; **mediana −4,0**; p75 −2,7; p90 −1,5; p95 −0,7.
- Média simples: −4,2. Média ponderada por válidos: −3,1.

| Faixa de swing (p.p.) | municípios | válidos 26 (mil) |
|---|---|---|
| ≤ −15 | 1 | 9 |
| −15 a −10 | 35 | 333 |
| −10 a −7,5 | 118 | 1.306 |
| −7,5 a −5 | 418 | 5.392 |
| −5 a −2,5 | 829 | 12.903 |
| −2,5 a 0 | 339 | 9.308 |
| 0 a +2,5 | 46 | 4.260 |
| +2,5 a +5 | 5 | 139 |
| > +5 | 3 | 15 |

**Swing por UF (percentis municipais):**

| UF | p10 | mediana | p90 | mín. | máx. |
|---|---|---|---|---|---|
| MA | −9,2 | −5,6 | −2,9 | −14,4 | −0,8 |
| PI | −7,6 | −4,1 | −1,6 | −15,2 | +7,8 |
| CE | −6,9 | −4,1 | −1,7 | −11,3 | +4,2 |
| RN | −6,5 | −4,1 | −2,2 | −13,1 | +1,2 |
| PB | −6,6 | −3,6 | −1,7 | −10,9 | +2,0 |
| PE | −5,7 | −3,3 | −0,8 | −9,9 | +1,3 |
| AL | −5,4 | −2,8 | −0,7 | −7,6 | +1,1 |
| SE | −4,3 | −2,7 | +0,1 | −5,9 | +1,7 |
| BA | −7,3 | −4,3 | −1,4 | −12,2 | +5,5 |

**Regressões.** Variável dependente: swing em p.p.; WLS ponderado por válidos; n = 1.794. Coeficiente em p.p. por
1 desvio-padrão da covariável (capital é dummy). Erro-padrão robusto HC1 entre parênteses.

| Variável | simples | múltipla | múltipla + EF de UF |
|---|---|---|---|
| Lula % 2022 | −0,92 (0,13), R² 0,22 | −0,35 (0,15) | −0,03 (0,16) |
| PBF % moradores | −0,94 (0,14), R² 0,21 | −0,07 (0,11) | +0,01 (0,10) |
| % evangélicos | +0,76 (0,13), R² 0,10 | +0,10 (0,13) | **+0,45 (0,12)** |
| log renda pc | +0,68 (0,08), R² 0,27 | −0,12 (0,15) | −0,15 (0,11) |
| log aptos (porte) | +0,73 (0,09), R² 0,31 | +0,31 (0,13) | **+0,37 (0,11)** |
| Capital (dummy) | +3,39 (0,46), R² 0,28 | +1,90 (0,59) | **+2,09 (0,48)** |
| R² do modelo | — | 0,35 | 0,46 |

Correlações ponderadas com o swing: porte +0,56, capital +0,53, renda +0,52, Lula 2022 −0,46, PBF −0,46,
evangélicos +0,31.

**Leitura** [calc]: as variáveis socioeconômicas são muito colineares no NE. Dentro de cada UF, o que segue
explicando a queda é **urbanização/porte**: capitais têm swing 2 p.p. melhor para Lula, e cidades maiores também.
PBF e renda, depois dos controles, não acrescentam poder explicativo. Os efeitos fixos de UF somam cerca de 11 p.p. de
R². O MA, o PI e a BA têm queda própria maior, o que pode refletir dinâmicas estaduais (alianças, candidaturas a
governador), sem verificação aqui.

### 1.8 Mapa-tabela: maiores perdas de margem (votos líquidos) [calc]

| Município | UF | aptos | Lula 22 % | Lula 26 % | swing | Δmargem | Δcomp. | evang. % | renda pc |
|---|---|---|---|---|---|---|---|---|---|
| Salvador | BA | 1.955.479 | 67,0 | 65,3 | −1,7 | −102.106 | −2,2 | 24,3 | 1.770 |
| Fortaleza | CE | 1.795.713 | 53,2 | 53,5 | +0,3 | −61.096 | +3,5 | 26,3 | 1.669 |
| Feira de Santana | BA | 435.631 | 61,7 | 57,1 | −4,6 | −31.997 | −2,1 | 31,7 | 1.210 |
| São Luís | MA | 761.443 | 56,5 | 54,5 | −2,0 | −26.638 | +0,2 | 30,4 | 1.596 |
| Teresina | PI | 592.974 | 62,4 | 61,2 | −1,2 | −19.149 | +0,3 | 19,4 | 1.560 |
| Natal | RN | 573.148 | 50,1 | 49,0 | −1,2 | −15.536 | −0,4 | 24,6 | 2.049 |
| Petrolina | PE | 249.120 | 65,3 | 60,2 | −5,1 | −14.664 | −1,1 | 22,2 | 1.290 |
| Balsas | MA | 71.213 | 51,6 | 38,4 | −13,3 | −13.599 | +1,4 | 21,8 | 1.167 |
| Imperatriz | MA | 195.325 | 43,3 | 39,0 | −4,2 | −13.070 | +0,3 | 37,2 | 1.324 |
| Juazeiro do Norte | CE | 200.346 | 72,5 | 67,1 | −5,5 | −12.997 | +0,2 | 11,5 | 1.022 |
| Vitória da Conquista | BA | 265.595 | 55,4 | 52,8 | −2,6 | −12.989 | −2,6 | 29,7 | 1.311 |
| Caucaia | CE | 249.622 | 58,5 | 56,0 | −2,6 | −12.977 | 0,0 | 32,6 | 948 |
| Barreiras | BA | 109.227 | 58,1 | 50,7 | −7,4 | −11.715 | −0,8 | 25,7 | 1.340 |
| Maceió | AL | 646.463 | 40,4 | 41,1 | +0,7 | −11.579 | +0,3 | 29,9 | 1.606 |
| Luís Eduardo Magalhães | BA | 81.123 | 41,4 | 32,5 | −8,9 | −11.577 | −0,1 | 32,7 | 1.645 |

Swings mais negativos entre municípios com mais de 50 mil aptos [calc]:
- Polos do agronegócio do Matopiba: Balsas −13,3, Grajaú −9,0, Luís Eduardo Magalhães −8,9, Barreiras −7,4 e Açailândia −6,2.
- Polos do interior do CE e de PE: Morada Nova −7,8, Tianguá −7,4, Serra Talhada −6,3, Santa Cruz do Capibaribe −6,0 e Araripina −5,7.
- Em sentido oposto, os maiores ganhos de margem foram em Recife (+18,6 mil), Aracaju (+4,1 mil), Cabo de Santo Agostinho, N. S. do Socorro e Olinda.

---

## 2. Comparecimento no NE

### 2.1 1º turno 2026 x 2022 [calc]

- O comparecimento no NE **subiu** de 80,5% para 81,5% (+1,0 p.p.), enquanto no Brasil caiu de 79,05% para 78,88%.
- Em números absolutos foram +1,37 mi de votantes no NE. Os aptos passaram de 42,37 mi para 43,51 mi (+2,7%).
- As maiores altas foram no MA (+2,4), no CE (+1,9) e em AL (+1,7). RN e PB ficaram estáveis (−0,2 e −0,1), assim como PE (0,0).
- O comparecimento subiu no interior (+1,3) e ficou estável nas capitais (0,0; com queda em Salvador −2,2 e Recife −1,8).
  Subiu mais nos municípios pequenos e de PBF alto (+2,4 a +2,6) e nos de renda baixa (+2,8 no Q1).

Correlação com a fatia de Lula, ponderada por aptos [calc]:
- corr(comparecimento 2026, % Lula 2026) = **−0,32**. Nível: Lula é mais forte onde o comparecimento é mais baixo, um padrão estrutural.
- corr(Δcomparecimento, % Lula 2022) = **+0,21**. O comparecimento cresceu mais onde Lula era mais forte.
- corr(Δcomparecimento, swing) = **−0,16**. Onde o comparecimento subiu, Lula **não** ganhou fatia, e até perdeu um pouco mais.

| Quintil de % Lula 2022 | Lula 22 % | Lula 26 % | comp. 22 % | comp. 26 % | Δcomp. | swing |
|---|---|---|---|---|---|---|
| Q1 (Lula mais fraco) | 57,8 | 55,7 | 82,3 | 82,5 | +0,2 | −2,1 |
| Q2 | 70,7 | 66,6 | 79,9 | 81,3 | +1,4 | −4,1 |
| Q3 | 75,5 | 71,1 | 78,3 | 80,5 | +2,2 | −4,4 |
| Q4 | 79,6 | 75,2 | 78,1 | 80,1 | +2,0 | −4,3 |
| Q5 (Lula mais forte) | 84,4 | 80,2 | 77,5 | 79,6 | +2,1 | −4,1 |

Ressalva: os aptos cresceram mais nos municípios pequenos (+3,9% em <10 mil) e médios (+5,4% em 50–100 mil) do que
nas cidades com mais de 200 mil aptos (+0,8%) [calc]. A variação do denominador (revisões e transferências de título)
pode afetar a taxa de comparecimento. Por isso, a alta de comparecimento não deve ser lida automaticamente como
mobilização.

### 2.2 Estoque de não votantes no 1T 2026 [calc]

| UF | aptos (mil) | abstenção (mil) | brancos+nulos (mil) | Lula % dos 2 cand. |
|---|---|---|---|---|
| MA | 5.183 | 1.029 | 150 | 67,4 |
| PI | 2.705 | 467 | 94 | 74,6 |
| CE | 6.997 | 1.089 | 293 | 66,9 |
| RN | 2.660 | 489 | 99 | 63,2 |
| PB | 3.249 | 565 | 170 | 65,0 |
| PE | 7.223 | 1.312 | 310 | 67,2 |
| AL | 2.442 | 504 | 120 | 57,5 |
| SE | 1.740 | 301 | 75 | 67,2 |
| BA | 11.313 | 2.288 | 492 | 69,8 |
| **NE** | 43.511 | **8.045** | **1.802** | 67,4 |

Perfil da abstenção no NE no 1T 2022, último dado por segmento:
- Dos cerca de 8,3 mi abstencionistas, **2,08 mi tinham 70 anos ou mais**, faixa em que o voto é facultativo e que comparece 55% (70–79) e 21% (80+).
- **2,69 mi** se declaravam analfabetos ou "lê e escreve".
- No 2T de 2022, o comparecimento do NE subiu nesses grupos (70–79 +4,6 p.p.; 80+ +3,6; analfabetos +2,2) e caiu entre os jovens (18–24 −1,2; 25–34 −0,7).

### 2.3 Histórico 1T→2T no NE (TSE agregado por UF) [calc]

Δ comparecimento/aptos, 2T − 1T, em p.p.:

| UF | 2014 | 2018 | 2022 |
|---|---|---|---|
| MA | −3,7 | −2,8 | −1,3 |
| PI | −2,4 | −2,1 | −1,0 |
| CE | −1,6 | −1,4 | +0,3 |
| RN | −0,8 | −1,0 | +0,7 |
| PB | −0,4 | −1,0 | +0,6 |
| PE | −1,2 | −0,2 | +0,9 |
| AL | −0,4 | −2,2 | −0,9 |
| SE | −1,2 | −1,0 | −0,5 |
| BA | −1,6 | −0,4 | +0,9 |

| NE | comp. 1T % | comp. 2T % | Δ p.p. | Δ votantes (mil) | Δ válidos (mil) | PT 1T→2T (mil) | adversário 1T→2T (mil) | Δmargem PT (mil) |
|---|---|---|---|---|---|---|---|---|
| 2014 | 80,0 | 78,3 | −1,6 | −626 | +668 | 16.403 → 20.180 | 4.230 → 7.974 | +34 |
| 2018 | 81,2 | 80,1 | −1,1 | −436 | +291 | 14.583 → 20.290 | 7.453 → 8.825 | +4.335 |
| 2022 | 80,5 | 80,7 | +0,2 | +92 | −84 | 21.753 → 22.535 | 8.787 → 9.963 | **−394** |

- **Em nenhum dos três ciclos o comparecimento do NE subiu mais de 0,2 p.p. entre os turnos.** Em 2014 e 2018 caiu de 1 a 1,6 p.p.
- O ganho de margem do PT entre os turnos depende da composição dos terceiros. Em 2018, o voto em Ciro no NE (1T) foi em grande parte para Haddad: +4,3 mi. Em 2014 (Marina) e em 2022 (Ciro/Tebet), a margem ficou estável ou piorou.
- Em 2022, no NE, Bolsonaro ganhou 1,18 mi votos entre os turnos e Lula, 0,78 mi.

---

## 3. Terceiros no NE (Caiado, Cury, Renan Santos, Zema) [calc]

| UF | Caiado (mil) | Cury (mil) | Renan (mil) | Zema (mil) | outros (mil) | 4 terceiros (mil) | % válidos | Caiado % | Cury % | Renan % | Zema % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MA | 50,1 | 84,8 | 60,4 | 4,6 | 5,1 | 199,8 | 5,0 | 1,3 | 2,1 | 1,5 | 0,1 |
| PI | 21,6 | 47,6 | 32,2 | 1,4 | 2,7 | 102,8 | 4,8 | 1,0 | 2,2 | 1,5 | 0,1 |
| CE | 45,6 | 140,5 | 107,6 | 4,3 | 7,7 | 297,9 | 5,3 | 0,8 | 2,5 | 1,9 | 0,1 |
| RN | 16,4 | 57,4 | 35,3 | 1,5 | 2,9 | 110,6 | 5,3 | 0,8 | 2,8 | 1,7 | 0,1 |
| PB | 19,5 | 73,8 | 42,2 | 2,0 | 3,7 | 137,6 | 5,5 | 0,8 | 2,9 | 1,7 | 0,1 |
| PE | 73,2 | 138,0 | 85,9 | 6,1 | 5,9 | 303,1 | 5,4 | 1,3 | 2,5 | 1,5 | 0,1 |
| AL | 14,2 | 42,4 | 26,8 | 1,2 | 3,0 | 84,6 | 4,7 | 0,8 | 2,3 | 1,5 | 0,1 |
| SE | 26,7 | 38,9 | 21,4 | 1,2 | 2,2 | 88,1 | 6,5 | 2,0 | 2,9 | 1,6 | 0,1 |
| BA | 122,5 | 194,9 | 117,3 | 6,5 | 10,7 | 441,2 | 5,2 | 1,4 | 2,3 | 1,4 | 0,1 |
| **NE** | **389,7** | **818,3** | **529,1** | **28,6** | 44,0 | **1.765,7** | 5,2 | 1,2 | 2,4 | 1,6 | 0,1 |

| Candidato | NE (mil) | Brasil (mil) | NE % do total |
|---|---|---|---|
| Cury | 818 | 3.448 | 23,7 |
| Renan Santos | 529 | 2.675 | 19,8 |
| Caiado | 390 | 2.605 | 15,0 |
| Zema | 29 | 326 | 8,8 |

**Concentração:**
- Os terceiros ficam sub-representados no NE (19,5% dos votos dos 4 contra 27,4% do eleitorado). Cury é o mais nordestino deles.
- Dentro do NE, os votos dos terceiros se concentram nas cidades grandes, de maior renda e mais evangélicas.
- As 9 capitais têm 27,2% desses votos contra 20,1% dos válidos. Salvador (108 mil), Fortaleza (104 mil), Recife (61 mil) e São Luís (50 mil) lideram.

| Corte | 4 terceiros (mil) | % válidos | Cury % | Renan % | Caiado % |
|---|---|---|---|---|---|
| Capitais | 481 | 7,1 | 3,0 | 2,2 | 1,7 |
| Interior | 1.285 | 4,8 | 2,3 | 1,4 | 1,0 |
| <10 mil aptos | 142 | 3,9 | 2,0 | 1,1 | 0,8 |
| >200 mil aptos | 646 | 7,0 | 3,0 | 2,1 | 1,7 |
| Renda Q1 | 124 | 3,7 | 1,7 | 1,0 | 0,8 |
| Renda Q5 | 1.138 | 6,2 | 2,8 | 1,9 | 1,4 |
| Evangélicos Q1 | 129 | 4,1 | 2,0 | 1,3 | 0,8 |
| Evangélicos Q5 | 974 | 6,1 | 2,7 | 1,8 | 1,4 |

---

## 4. Aritmética: quanto do gap de cerca de 2,26 mi pode vir do NE?

O gap é a diferença do 1T (Flávio − Lula = 2.259 mil). Para virar, Lula precisa de ganho líquido de margem acima de
2,26 mi **somando todas as regiões**. A tabela abaixo isola apenas a contribuição líquida do NE (Lula − Flávio, em
mil votos) por três canais [calc]:

1. **Transferência** dos 1,77 mi votos de terceiros do NE (mais 44 mil de "outros"). Três matrizes (Lula/Flávio em %):
   - *Quaest nacional* (2–3/10 e 24–27/9): Caiado 19/43, Renan 11/60, Cury 28/35, Zema 10/80, outros 30/30.
   - *NE pró-Lula*: cada uma com +10 p.p. para Lula e −10 p.p. para Flávio.
   - *NE pró-Flávio*: Caiado 10/70, Renan 8/70, Cury 15/60, Zema 5/80, outros 10/60. Inspirada na inferência ecológica de 2022 no NE (Tebet 0/77 e "Outros" 8/71, OLS restrito, `transferencia_2t_ecologica.csv`).
2. **Comparecimento**: Δ p.p. de comparecimento/aptos por UF. Os novos votantes votam como a divisão Lula/Flávio do
   1T na UF, ou, na variante "+10", com 10 p.p. a mais para Lula. 94,9% dos novos votantes viram válidos.
3. **Brancos/nulos**: uma fração dos 1,80 mi brancos e nulos passa a votar válido, com a divisão Lula/Flávio do NE
   (67,4%/32,6%), ou com 10 p.p. a mais para Lula no cenário E.

Sensibilidade do canal de comparecimento:

| Δ comparecimento no NE (1T→2T) | novos votantes (mil) | margem líquida, perfil da UF (mil) | perfil +10 p.p. Lula (mil) |
|---|---|---|---|
| repete 2014 (−1,6 p.p.) | −711 | −246 | −381 |
| repete 2018 (−1,1 p.p.) | −489 | −156 | −249 |
| estável | 0 | 0 | 0 |
| repete 2022 (+0,2 p.p.) | +94 | +33 | +51 |
| +1 p.p. | +435 | +143 | +226 |
| +2 p.p. | +870 | +287 | +452 |
| +3 p.p. (sem precedente recente) | +1.305 | +430 | +678 |

Regra de bolso [calc]: **cada 1 p.p. de comparecimento no NE vale cerca de 435 mil votantes e de 140 a 225 mil votos
líquidos para Lula**. Cada 10% dos brancos e nulos que passam a votar válido vale cerca de 63 mil votos líquidos. A
transferência dos 4 terceiros do NE só fica positiva para Lula se ele tiver mais desses eleitores do que Flávio. Na
matriz Quaest, ela custa −430 mil.

**Cenários (contribuição líquida do NE, em mil votos Lula − Flávio)** [calc]:

| Cenário | transferência | comparecimento | brancos/nulos | **total NE** | % do gap de 2.259 |
|---|---|---|---|---|---|
| A. Pessimista: transf. pró-Flávio, comparecimento cai como em 2018 | −974 | −156 | 0 | **−1.130** | −50% |
| A2. "Como 2022": transf. Quaest, comparecimento +0,2 | −430 | +33 | 0 | **−397** | −18% |
| B. Base: transf. Quaest, comparecimento estável | −430 | 0 | 0 | **−430** | −19% |
| C. Base, +1 p.p. de comparecimento, −10% de brancos/nulos | −430 | +143 | +63 | **−224** | −10% |
| D. Otimista: transf. pró-Lula, +2 p.p., −15% de brancos/nulos | −68 | +287 | +94 | **+313** | +14% |
| E. Teto: transf. pró-Lula, +3 p.p. com novos votantes +10 p.p. pró-Lula, −20% de brancos/nulos (+10 p.p.) | −68 | +678 | +197 | **+807** | +36% |

**Leitura** [calc]:
- Nas hipóteses históricas (A, A2, B), o NE **amplia** a diferença a favor de Flávio no 2T, em 0,4 a 1,1 mi. Os 1,77 mi de terceiros do NE são majoritariamente de candidatos cujo eleitorado declara preferir Flávio, e o comparecimento do NE não costuma subir entre os turnos.
- Para o NE fechar mais de 10% do gap, é preciso combinar transferência bem melhor que a nacional com uma alta de comparecimento de 2 p.p. ou mais. Isso não ocorreu no NE em 2014, 2018 nem 2022.
- Mesmo no teto (E), o NE cobre cerca de um terço do gap (cerca de 0,8 mi). O restante teria de vir do Sudeste/Sul/Centro-Oeste, onde estão cerca de 80% dos votos dos 4 terceiros.
- Referência histórica: o único caso recente de grande ganho do PT no NE entre os turnos (2018, +4,3 mi) dependeu de um terceiro de centro-esquerda forte no NE (Ciro). Esse perfil não existe em 2026: os terceiros de esquerda somam 0,17% dos válidos no país.

**Limitações:**
- O 1T está totalizado no arquivo, com cerca de 1,2% do eleitorado nacional extrapolado por `pst`.
- As matrizes de transferência são nacionais (pesquisas) ou ecológicas de 2022. Não há pesquisa de 2026 por região com segunda opção dos terceiros.
- Os novos votantes do 2T podem ter perfil diferente do perfil médio da UF. A variante "+10" tenta cobrir o caso de mobilização em reduto lulista.
- O comparecimento de 2026 tem denominador (aptos) que mudou de forma desigual por porte.
- Os cortes por PBF, religião e renda são ecológicos (município), não individuais.
