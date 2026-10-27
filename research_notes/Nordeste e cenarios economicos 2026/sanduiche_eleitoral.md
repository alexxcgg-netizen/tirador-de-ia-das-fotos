# Efeito-sanduíche eleitoral: o meio da renda virou mais contra o governo?

Leitura de 05/10/2026, um dia depois do 1º turno. Nesta nota testamos com dados as etapas eleitorais da cadeia do
"efeito-sanduíche" (etapas 6, 7 e 8):

- (6) percepção de injustiça;
- (7) atribuição ao governo;
- (8) mudança de voto.

O texto é neutro: não julga candidatos. Cada número vem marcado assim:

- **[fato]**: número publicado, com fonte;
- **[calc]**: cálculo nosso;
- **[inf]**: inferência.

**Arquivos**

| Arquivo | Conteúdo |
|---|---|
| `simulador/data/renda_voto_aprovacao.csv` | Pesquisas por faixa de renda (voto e aprovação, 2022–2026). Uma linha por pesquisa × faixa × medida, com fonte, campo e n. |
| `sanduiche_eleitoral.py` (nesta pasta) | Reproduz todos os cálculos [calc]. Só lê arquivos do repositório. |
| `covariaveis_mun_br.csv` | Renda domiciliar per capita (Censo 2022, SIDRA 10295 v13431) e % de evangélicos (SIDRA 9537) dos 5.570 municípios, com o código TSE (de-para `betafcc/Municipios-Brasileiros-TSE`). Baixado em 05/10/2026. |
| `sanduiche_swing_decis_renda.csv` | Swing real do TSE (1º turno 2022 → 1º turno 2026) por decil de renda municipal. |

Nenhum arquivo do modelo de previsão foi alterado. As mudanças recomendadas estão na seção 7.

---

## Resumo

1. **A assinatura sanduíche não aparece na faixa de 2–5 SM.**
   - Em todas as comparações de pesquisa 2022 → 2026, a faixa de 2–5 SM foi a que **menos** se moveu contra Lula.
   - Medimos isso com o contraste S = swing(2–5) − média dos swings da base (até 2 SM) e do topo (mais de 5 SM). S < 0 seria o sanduíche.
   - S ficou entre **+1,2 e +8,6 p.p.** nos quatro pares de pesquisas. A média é **+5 p.p.** (EP ≈ 2–3; os pares não são independentes) [calc].
   - Os dados rejeitam a hipótese "o meio de 2–5 SM foi o que mais virou".
2. **O que os dados mostram é o gradiente de classe ficando mais íngreme no topo.**
   - A faixa de **mais de 5 SM** foi a que mais se moveu para Flávio.
   - Datafolha, 2º turno contra 2º turno: **−6,4 ± 4,1 p.p.** na fatia de Lula. Até 2 SM: −2,1 ± 2,3. 2–5 SM: +0,1 ± 2,7. Nacional: −0,9 [calc].
   - Quaest (com correção do 1º para o 2º turno): mais de 5 SM −11,3 ± 5,2 [calc].
   - Isso é mais compatível com **voto de classe** do que com sanduíche.
3. **A hipótese do sanduíche "deslocado para 5–10 SM" não pode ser testada no voto.**
   - Em 2026, Datafolha e Quaest publicam só "mais de 5 SM". Sem separar 5–10 de 10+, não há como ver o "pão de cima".
   - Há indícios fracos na aprovação. No Datafolha de dez/2025, ruim/péssimo foi de 31% (até 2), 39% (2–5), **53% (5–10)** e 40% (10+) [fato]. A faixa 10+ tem n ≈ 80 (margem de até 11 p.p.).
   - A AtlasIntel (online, faixas em R$) mostra Lula **vencendo** acima de R$ 10 mil (54 × 26) [fato]. Isso também indica um topo menos hostil que o meio-alto. A diferença de modo de coleta, porém, impede somar essa pesquisa às presenciais.
4. **No resultado real, analisado por município (ecológico), o swing contra Lula foi quase plano nos decis 1 a 8 de renda municipal** (−4,1 a −5,1 p.p. na fatia bipartidária) e **bem menor nos dois decis mais ricos** (−2,1) [calc].
   - Com controles (efeito fixo de UF, % de evangélicos, porte, capital e voto de 2022), sobra um "U" raso: os decis do meio ficam cerca de 1 p.p. abaixo das pontas.
   - Esse resultado depende da especificação. Só com efeito fixo de UF, a relação vira monotônica no sentido oposto. É inferência ecológica: município de renda média não é o mesmo que eleitor de renda média.
5. **Etapas 6 e 7 (percepção e atribuição):** não encontramos, por faixa de renda, perguntas publicadas sobre "o governo favorece pobres ou ricos", "o governo ajuda pessoas como eu" ou de quem é a culpa.
   - O dado mais forte é sobre o efeito de um benefício direto. Depois da lei de isenção do IR até R$ 5 mil, o ruim/péssimo da faixa de 2–5 SM caiu de **47% para 39%** (Datafolha, dez/2025) [fato].
   - Ou seja, a atribuição (etapa 7) responde a benefício direto. A faixa de 2–5 SM deixou de ser um "meio sem benefício" em 2026.
6. **Parâmetro para o modelo** (detalhes na seção 7):
   - Swing adicional atribuível ao sanduíche em 2–5 SM: **0 p.p.** (faixa de 80%: −2 a +2), com confiança moderada de que não é grande e negativo.
   - Em 5–10 SM: **−1 p.p.** (faixa de 80%: −4 a +1), com **confiança baixa**. É "não identificável" com dados públicos.
   - **Recomendação:** não mexer na previsão calibrada. No máximo, criar uma alavanca de cenário desligada por padrão.
7. **Pesquisas de 2º turno de 2026:** até a manhã de 05/10 não encontramos nenhuma pesquisa de 2º turno publicada depois do 1º turno. O único 2º turno por faixa é o Datafolha de 15–17/09.

---

## 1. Hipótese e como medir

O efeito-sanduíche diz que o meio da distribuição de renda tem menos benefício direto e menos meios de se adaptar. Por isso ele perceberia mais injustiça (6), culparia o governo (7) e mudaria o voto (8).

**Variável.** Usamos o swing por faixa de renda b, de 2022 para 2026, na fatia bipartidária de Lula: `sw_b = p_b(2026) − p_b(2022)`. Nos dois anos, a fatia é Lula/(Lula + candidato bolsonarista), dentro da mesma faixa e do mesmo instituto.

**Assinatura testável.**
- **Sanduíche:** `S = sw_meio − ½(sw_base + sw_topo) < 0`. O meio anda mais para o adversário do que as duas pontas, numa curva em "U" ou em corcova.
- **Voto de classe:** `G = sw_topo − sw_base < 0`, com o meio entre os dois (monotônico).
- **Nulo:** swing uniforme, com S ≈ 0 e G ≈ 0.

**Erro-padrão.** `EP = √(p(1−p)/n_ef)`, com `n_ef = n_faixa × (fração com voto em um dos dois) / 1,5`. O 1,5 é o efeito de desenho suposto para amostras por cotas e pontos de fluxo. As faixas de 2026 do Quaest e do Datafolha de 03/10 têm n estimado; o CSV marca quais.

---

## 2. Pesquisas: swing 2022 → 2026 por faixa (etapa 8)

### 2.1 Níveis (fatia bipartidária de Lula, %)

| Pesquisa | Até 2 SM | 2–5 SM | 5–10 SM | 10+ SM | >5 SM | Total |
|---|---|---|---|---|---|---|
| Datafolha 2T 05–07/10/2022 (n = 2.884) | 59,3 | 44,1 | 46,4 | 54,7 | 49,1 | 52,7 |
| Datafolha 2T 28–29/10/2022 (n = 8.308; válidos) | 61 | 45 | 42 | 39 | 41,2 | 52 |
| Quaest 2T 23–25/10/2022 (n = 2.000) | 61,1 | 44,0 | – | – | 48,9 | 53,3 |
| Datafolha 2T 15–17/09/2026 (n = 2.001; situação A) | 58,9 | 45,1 | – | – | 34,8 | 51,1 |
| Datafolha 1T 15–17/09/2026 | 61,3 | 44,6 | – | – | 38,9 | 52,0 |
| Quaest 1T 24–27/09/2026 (n = 2.004) | 69,3 | 49,3 | – | – | 41,7 | 53,4 |
| Datafolha 1T 03/10/2026 (n = 4.006) | 61,0 | 42,7 | – | – | 41,7 | 51,2 |
| AtlasIntel 1T 11–16/09/2026 (online; faixas em R$) | R$ 2–3 mil: 43,1 | R$ 3–5 mil: 49,7 | R$ 5–10 mil: 51,1 | >R$ 10 mil: 67,3 | – | 51,4 |

Fontes: CSV. Os PDFs do Datafolha de 2022 (PO4117) e de 17/09/2026 (PO4290) estão nas tabelas do Poder360 [fato].

**Já em 2022 o nível era instável no topo.**
- Na rodada de 05–07/10/2022, o Datafolha tinha a faixa de 2–5 SM como a **mais** bolsonarista: 44, contra 46 em 5–10 e 54 em 10+. É um "U" em nível.
- Três semanas depois, o mesmo instituto mostrava gradiente monotônico (45 / 42 / 39).
- A Quaest de 23–25/10/2022 também tinha o meio abaixo do topo: 44 em 2–5 SM contra 49 em mais de 5.
- Com n de 100 a 900 nas faixas altas, o formato da curva no topo é ruído de ±3 a 6 p.p. **Por isso nenhuma conclusão deve vir de uma única pesquisa** [inf].

### 2.2 Swing e contrastes [calc]

Comparações entre o 1º turno de 2026 e o 2º turno de 2022 recebem uma correção do 1º para o 2º turno por faixa. A correção vem do mesmo Datafolha de 15–17/09/2026, que mediu os dois turnos na mesma amostra:

| Faixa | Correção | Motivo |
|---|---|---|
| Até 2 SM | −2,4 | |
| 2–5 SM | +0,5 | |
| Mais de 5 SM | −4,1 | Os terceiros (Cury, Caiado, Renan, Zema) somam 23% nessa faixa e vão mais para Flávio |

A correção soma ±2 p.p. ao erro-padrão.

| Par 2022 → 2026 | sw até 2 | sw 2–5 | sw >5 | **S** (sanduíche se < 0) | **G** = topo − base | sw nacional |
|---|---|---|---|---|---|---|
| Datafolha 2T 28–29/10/22 → 2T 15–17/09/26 | −2,1 ± 2,3 | +0,1 ± 2,7 | **−6,4 ± 4,1** | **+4,3 ± 3,6** | −4,3 ± 4,7 | −0,9 |
| Datafolha 2T 05–07/10/22 → 2T 15–17/09/26 | −0,5 ± 2,6 | +1,0 ± 3,2 | −14,3 ± 5,0 | +8,4 ± 4,3 | −13,9 ± 5,7 | −1,9 |
| Datafolha 2T 28–29/10/22 → 1T 03/10/26 (corrigido) | −2,5 ± 2,7 | −1,9 ± 2,9 | −3,6 ± 3,9 | +1,2 ± 3,8 | −1,2 ± 4,7 | – |
| Quaest 2T 23–25/10/22 → 1T 24–27/09/26 (corrigido) | +5,8 ± 3,8 | +5,8 ± 4,0 | −11,3 ± 5,2 | +8,6 ± 5,1 | −17,1 ± 6,4 | – |

- **S é positivo nos quatro pares.** Combinado por variância inversa, dá +5,0 ± 2,0. Os pares partilham amostras de 2026, então o EP real é maior, de cerca de 3.
- **G é negativo nos quatro pares.** A faixa de cima andou mais para Flávio do que a de baixo. O formato é "o topo descolou", não corcova no meio.
- **Resultado:** a hipótese sanduíche na faixa de 2–5 SM é **rejeitada** nos dados disponíveis (S ≥ 0 em todos os pares, com a média cerca de 2 EP acima de zero). O padrão compatível é **voto de classe se aprofundando no topo**, e a faixa de 2–5 SM ficou perto do swing nacional.
- **Ressalva:** "mais de 5 SM" junta 5–10 SM (cerca de 10% da amostra) e 10+ (cerca de 3–4%). O swing desse bloco é dominado por 5–10 SM. Um sanduíche cujo "meio" fosse 5–10 SM, com 10+ estável, **produziria exatamente esse dado**. Por isso a seção 7 dá parâmetro separado para 5–10 SM, com confiança baixa.

### 2.3 Aprovação por faixa, 2024–2026 (etapa 7, por aproximação)

| Pesquisa (campo) | Medida | Até 2 | 2–5 | 5–10 | 10+ | >5 | Total |
|---|---|---|---|---|---|---|---|
| Quaest dez/2024 | aprova / desaprova | 63 / 34 | – | – | – | 39 / 59 | 52 / 47 |
| Datafolha fev/2025 | ótimo+bom | 29 | **17** | 18 | 18 | – | 24 |
| Quaest 27–31/03/2025 | aprova / desaprova | 52 / 45 | **36 / 61** | – | – | 34 / 64* | 41 / 56 |
| Datafolha 01–03/04/2025 | ótimo+bom | 30 | **26** | 31 | 31 | – | 29 |
| Datafolha 02–04/12/2025 | ótimo+bom / ruim+péssimo | 36 / 31 | 29 / 39 (era 47) | **24 / 53** | 27 / 40 | – | 32 / 37 |
| Quaest 08–11/05/2026 | aprova / desaprova | 54 / 40 | 43 / 52 | – | – | 39 / 58 | 46 / – |
| Datafolha 15–17/09/2026 | aprova / desaprova | 56 / 41 | 42 / 57 | – | – | **30 / 68** | 48 / 50 |
| Datafolha 15–17/09/2026 | ótimo+bom / ruim+péssimo | 41 / 33 | 27 / 48 | – | – | 20 / 61 | 34 / 42 |

\* A matéria publica 64/34, uma inversão evidente; corrigimos.

**Leitura** [calc/inf]:
- **Em 2 das 3 rodadas do Datafolha com quatro faixas, a curva não é monotônica.**
  - Abr/2025: o fundo do ótimo+bom está em 2–5 SM (26 contra 30 e 31).
  - Dez/2025: o fundo está em 5–10 SM (ruim/péssimo 53, contra 39 em 2–5 e 40 em 10+).
  - O ponto mais baixo **se desloca para cima** depois da isenção do IR, que beneficia sobretudo a faixa de 2–5 SM.
  - É o que se espera se o "meio sem benefício" for definido pela política, e não por um corte fixo de renda.
  - **Mas:** a faixa 10+ tem n de 80 a 130 (EP de 5 a 7 p.p.), e o fundo foi escolhido depois de ver os dados. Isso é sugestivo, não é teste.
- **Na trajetória, quem mais caiu entre dez/2024 e o fundo de 2025 foi a base.**
  - Quaest, até 2 SM: −11 (63 → 52).
  - Datafolha, até 2 SM: −15 no ótimo+bom (44 em dez/2024 → 29 em fev/2025).
  - A recuperação de 2025–2026 também foi maior na base.
  - A faixa de 2–5 SM teve a pior marca relativa em fev–mar/2025 (17 de ótimo+bom; 61 de desaprovação) e se recuperou: 43/52 na Quaest de mai/2026; 42/57 no Datafolha de set/2026.
- **Em set/2026, o bloco de mais de 5 SM é o mais negativo:** 68% de desaprovação, contra 57% em 2–5 SM e 41% em até 2 SM. É o mesmo descolamento do topo visto no voto.

---

## 3. Resultado real (TSE), por município (etapa 8, sem pesquisa)

No Brasil não há boca de urna pública por renda. O único teste com voto real é **ecológico**: o swing municipal do 1º turno de 2022 para o 1º turno de 2026, na fatia Lula/(Lula + Bolsonaro ou Flávio), contra a renda domiciliar per capita do Censo 2022. São 5.570 municípios e 118,9 milhões de votos válidos [calc].

Para uma leitura aproximada, a renda familiar equivalente em SM é a renda per capita × 2,79 moradores ÷ R$ 1.212 (SM de 2022).

| Decil (ponderado por válidos) | Renda pc média (R$) | ≈ SM familiar | Lula 2022 | Lula 2026 | **swing bipartidário** | swing nos válidos |
|---|---|---|---|---|---|---|
| 1 | 642 | 1,5 | 77,2 | 72,4 | −4,9 | −3,9 |
| 2 | 820 | 1,9 | 71,1 | 66,3 | −4,8 | −4,2 |
| 3 | 1.050 | 2,4 | 58,4 | 53,9 | −4,4 | −4,2 |
| 4 | 1.271 | 2,9 | 50,1 | 45,6 | −4,5 | −4,2 |
| 5 | 1.457 | 3,4 | 45,2 | 40,1 | **−5,1** | −4,9 |
| 6 | 1.630 | 3,8 | 48,1 | 43,8 | −4,3 | −3,4 |
| 7 | 1.808 | 4,2 | 44,0 | 39,4 | −4,6 | −4,1 |
| 8 | 2.102 | 4,8 | 40,3 | 36,2 | −4,1 | −3,5 |
| 9 | 2.485 | 5,7 | 43,2 | 41,2 | −2,1 | −1,7 |
| 10 | 2.913 | 6,7 | 49,7 | 47,6 | −2,1 | −0,7 |

**Recortes (quintis de renda municipal):**

| Recorte | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| Nordeste | −5,0 | −5,0 | −4,4 | −3,4 | −1,8 |
| Fora do Nordeste | −5,0 | −5,0 | −4,9 | −4,2 | −1,9 |
| Evangélicos acima da média | −4,2 | −3,5 | −4,2 | −3,7 | −1,9 |
| Evangélicos abaixo da média | −5,0 | **−5,8** | **−5,7** | −4,8 | −2,1 |
| Fora do NE e evangélicos abaixo da média | −6,9 | −6,8 | −5,2 | −1,4 | −2,7 |

**Regressão WLS** (EP robusto; efeito de cada decil contra o decil 1, em p.p. do swing):

| Especificação | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
|---|---|---|---|---|---|---|---|---|---|
| Efeito fixo de UF | +0,2 | +1,1 | +1,5 | +1,9 | +2,8 | +2,7 | +3,7 | +4,4 | +5,0 |
| Efeito fixo de UF + evangélicos + porte + capital + Lula 2022 | −0,6 | −1,2 | −1,3 | **−1,3** | −1,1 | −1,3 | −0,9 | −0,6 | −1,0 (0,75) |

O EP dos decis 2 a 8 fica entre 0,16 e 0,45.

**Leitura** [inf]:
- **Sem controles, ou só com UF, a renda municipal "protege" Lula de forma monotônica.** Os lugares ricos (capitais e metrópoles) perderam menos, e os mais pobres perderam mais. Isso não é sanduíche: é a base, e não o meio, que se moveu mais em termos absolutos. O mesmo padrão aparece no Nordeste (nota `nordeste_dados_1t.md`, seção 1.6).
- **Com controles, sobra um U raso.**
  - Os decis 3 a 7 ficam cerca de 1,2–1,3 p.p. pior que o decil 1, e os decis 9 e 10 ficam cerca de 0,6–1,0 pior.
  - O contraste ecológico S ≈ −1,3 − ½(0 − 0,8) ≈ **−0,9 p.p.** (EP ≈ 0,5).
  - O sinal é de sanduíche, mas o tamanho é pequeno, e o resultado depende de incluir o controle "Lula 2022" (regressão à média) e o porte.
- **A falácia ecológica pesa muito aqui.** Um município de renda média (R$ 1.300–1.800 per capita) é uma mistura de pobres, classe média e ricos. Ele também difere em urbanização, setor (agro × serviços) e mídia.
- **Teste melhor, não feito:** voto por seção eleitoral cruzado com a renda do setor censitário, dentro das capitais.

---

## 4. Percepção e atribuição (etapas 6 e 7)

| Item pedido | O que existe por faixa | Leitura |
|---|---|---|
| "Economia piorou" | Só nacional: 49–50% piorou (Quaest abr e set/2026); 71% dizem que o poder de compra caiu (abr/2026) [fato] | Sem recorte de renda publicado |
| Preço dos alimentos e custo de vida | Quaest (2024, classes pelo Critério Brasil): 79–80% em **todas** as classes viram os alimentos subirem; contas de água e luz, 64–66% [fato] | **A percepção do custo de vida não distingue o meio:** é transversal |
| Imposto e isenção do IR | Quaest abr/2026: 31% dizem ter sido beneficiados pela isenção até R$ 5 mil, 66% não; entre os beneficiados, 49% não viram diferença [fato]. Datafolha dez/2025: ruim/péssimo em 2–5 SM caiu de 47 para 39 após a lei [fato]. Apoio à isenção: 79% (Quaest out/2025) [fato] | O benefício é **creditado** ao governo (etapa 7 funciona), e a faixa de 2–5 SM deixou de ser "sem benefício" |
| "Governo favorece pobres ou ricos" / "ajuda pessoas como eu" | **Não encontrado** por faixa nas pesquisas públicas de 2023–2026 | Lacuna principal da cadeia |
| De quem é a culpa (governo, Congresso, mercado, estados) | **Não encontrado** por faixa | Lacuna |
| Identidade política por classe | Quaest (2024): lulista 28 / 16 / 12% (pobres / classe média / ricos); direita (com bolsonarista) 23 / 34 / 43% [fato] | Monotônico: o meio fica entre a base e o topo, sem "corcova" |
| Aperto financeiro objetivo | CNC Peic jul–ago/2026: inadimplência 38,8% (≤3 SM) contra 14,9% (>10 SM); "sem condições de pagar" 18,3% (≤3 SM) contra 7,8% (5–10 SM) [fato; via `salario_minimo_equilibrio_geral.md`] | O aperto de dívida medido é **maior na base**, não no meio |
| Ônus tributário objetivo | O imposto implícito do FGTS cresce até 10 SM (0,9% → 3,6% da renda) [calc; `custos_ocultos_credito_subsidios.md`]. A alíquota efetiva do IR cai no topo (Gobetti e Orair, Ipea TD 2190, 2016) [fato] | Há um "sanduíche fiscal" objetivo entre 5 e 40 SM. Não há medida de que ele seja **percebido** |

**Conclusão das etapas 6 e 7:**
- Os dados públicos **não permitem medir** a percepção de injustiça nem a culpa por faixa.
- O que se mede (custo de vida e identidade política) é transversal ou monotônico.
- O único efeito causal aproximado, o da isenção do IR, mostra que benefício direto melhora a avaliação na faixa beneficiada. Isso é coerente com a cadeia do sanduíche: o canal "falta de benefício leva à insatisfação" existe. Mas, depois da reforma, o canal tiraria a faixa de 2–5 SM do recheio [inf].

---

## 5. Explicações alternativas

1. **Região (o Nordeste concentra a base).** Calculamos o swing esperado por faixa só pela composição regional: as participações de região dentro de cada faixa (Datafolha 28–29/10/2022) vezes o swing regional do 2º turno (Datafolha 2022 → 15–17/09/2026: SE −0,3; S −4,0; NE −4,3; CO/N +0,4) [calc]. O resultado:
   - até 2 SM −2,1, 2–5 SM −1,6, mais de 5 SM −1,3;
   - S esperado pela região: **≈ 0**;
   - o observado é −2,1, +0,1 e −6,4, e o resíduo, 0, +1,7 e **−5,1**.
   - **A região não explica** nem a estabilidade do meio nem a queda do topo.
2. **Escolaridade.** No 2º turno do Datafolha (2022 → set/2026), o swing foi fundamental −1,2, médio −1,2, superior −1,7 [calc]. É quase uniforme.
   - A faixa de mais de 5 SM tem 64–76% com ensino superior. Se o deslocamento dela viesse da escolaridade, o grupo com superior teria caído cerca de 6 p.p., e não caiu.
   - Logo, o deslocamento no topo vem de pessoas de renda alta **sem** diploma, como pequenos empresários, autônomos e comerciantes [inf]. Isso é compatível com o perfil "pequeno negócio" da hipótese, mas na faixa acima de 5 SM.
3. **Religião.** Evangélicos: 2T 2022, 31% Lula; set/2026: 34,8% no Datafolha e 35,7% na Quaest [calc], ou seja, um leve movimento **para** Lula. Católicos: 59 → 56,7.
   - A participação evangélica é igual em até 2 e em 2–5 SM (26%) e menor no topo (18–23%).
   - Por isso a religião não cria corcova no meio nem explica a queda do topo.
4. **Idade.** No 2º turno de set/2026, 60+ e 16–24 estão mais pró-Lula (49 contra 40, e 49 contra 39). A distribuição etária é quase igual entre as faixas de renda (média de 41 a 44 anos em todas, Datafolha 2022). Sem efeito de composição relevante.
5. **Mudança dos cortes de renda.**
   - O SM subiu de R$ 1.212 (2022) para R$ 1.621 (2026), +34% nominal e cerca de +10–12% real.
   - O corte de "5 SM" de 2026 é uma renda real mais alta, e a faixa de mais de 5 SM ficou mais seleta (15% da amostra em 2022 contra 13% em 2026).
   - Uma faixa de topo mais rica tende a parecer mais à direita mesmo sem mudança individual. Isso explica parte do −6 p.p. Estimamos 1–2 p.p., pelo gradiente 5–10 contra 10+ de 2022 [inf].
6. **Terceiros candidatos no 1º turno.** Cury, Caiado, Renan e Zema somam 23% na faixa de mais de 5 SM, contra cerca de 10% em até 2 SM. Por isso a fatia bipartidária do 1º turno superestima Lula no topo. Corrigimos isso nos pares com 1º turno (seção 2.2).
7. **Não resposta diferencial e erro das pesquisas.**
   - No 1º turno de 2026, as pesquisas subestimaram Flávio em cerca de 3 p.p. na média (AVALIACAO_1T.md).
   - Se a não resposta for maior no meio, as pesquisas por faixa escondem um sanduíche.
   - O teste ecológico (seção 3) não mostra erro concentrado no meio: o swing real é quase plano nos decis 1 a 8. Mas um teste direto exigiria a previsão implícita por município.
8. **Modo de coleta.** A AtlasIntel (online) mostra o gradiente invertido no topo: Lula 54% acima de R$ 10 mil. Painéis online recrutam no topo mais pessoas escolarizadas e metropolitanas. Não misturamos com as pesquisas presenciais.

---

## 6. Literatura

**Brasil: "nova classe média", lulismo e virada de 2013–2018**
- **Singer** (2009, "Raízes sociais e ideológicas do lulismo", *Novos Estudos* 85; 2012, *Os sentidos do lulismo*) mostra o realinhamento de 2006: o lulismo passou a se apoiar no subproletariado (cerca de 2 SM ou menos), e a classe média se afastou do PT.
- **Singer** (2013, "Brasil, junho de 2013: classes e ideologias cruzadas", *Novos Estudos* 97) analisa a classe média e a "nova classe trabalhadora" nas ruas.
- **Singer** (2018, *O lulismo em crise*) liga a ruptura de 2013–2016 à perda do centro.
- **Hunter e Power** (2007, *LAPS* 49(1)) e **Zucco** (2008, *JLAS* 40(1)) documentam a mudança da base petista para o Nordeste e os pobres, com o Bolsa Família.
- **Neri** (FGV, 2008–2010, "nova classe média"), **Souza** (2010, *Os batalhadores brasileiros*) e **Pochmann** (2012, *Nova classe média?*) debatem se a faixa C ascendente é "classe média" ou trabalhadora. O ponto relevante aqui: a faixa de 2–5 SM é, em boa parte, a classe C que ascendeu nos anos 2000.
- **Gethin e Morgan** (2018, *WID Issue Brief* 2018/3, "Brazil Divided") são a formulação mais próxima do sanduíche.
  - Entre 2001 e 2015, a renda real dos 50% mais pobres cresceu 29,9%, a dos 10% mais ricos 21,0% e a dos **40% do meio só 9,2%**.
  - Ao mesmo tempo, o voto no PT foi se concentrando na metade de baixo.
  - Os autores leem 2018 como reação do meio, que ficou de fora dos ganhos de baixo e de cima.
  - Ver também Gethin, Martínez-Toledano e Piketty (2022, *QJE* 137(1), "Brahmin Left versus Merchant Right").
- **Samuels e Zucco** (2018, *Partisans, Antipartisans, and Nonpartisans*) mostram que o antipetismo é mais forte entre renda e escolaridade mais altas. **Nicolau** (2020, *O Brasil dobrou à direita*) mostra que Bolsonaro, em 2018, foi mais forte de 2 a 10 SM e acima. Em 2018, o Datafolha do 2º turno dava Bolsonaro com 62% em 5–10 SM ou mais (nota `2018_pesquisas_vs_resultado.md`).
- **Kerche** (com Marona, 2022, *A política no banco dos réus*) trata da Lava Jato e das instituições, não de classe. É útil como contexto da virada de 2014–2018, mas não testa o mecanismo de renda.
- **Costa** (2022, Mecila WP 45, "Unequal and Divided: The Middle Classes in Contemporary Brazil") faz uma revisão sobre fragmentação da classe média.

**Internacional ("squeezed middle")**
- **OECD** (2019, *Under Pressure: The Squeezed Middle Class*): custos de moradia, saúde e educação subiram mais que a renda do meio.
- **Milanovic** (2016): a "curva do elefante" mostra a classe média baixa dos países ricos estagnada.
- **Kurer** (2020, *Comparative Political Studies* 53(10–11), "The Declining Middle"): o meio em declínio vota na direita populista, mas por **status e expectativa**, mais do que por renda corrente.
- **Gidron e Hall** (2017, *BJS*): status social subjetivo.
- **Engler e Weisstanner** (2021, *JEPP* 28(2)): a ameaça de queda social amplia o voto na direita radical.
- **Burgoon et al.** (2019, *Economic Policy* 34(97)): privação posicional, isto é, crescer menos que os outros grupos.
- **Lição para a medida:** o mecanismo aparece em **trajetória relativa** e status percebido, não em nível de renda. A faixa de SM é uma aproximação fraca disso.

**Já está documentado?** Sim. O afastamento da classe média do PT desde 2006 e a ruptura de 2013–2018 estão bem documentados (Singer; Gethin e Morgan; Samuels e Zucco; Nicolau).
- **O incremento de 2026 sobre 2022:** na faixa de 2–5 SM ele é **≈ 0** (ou levemente pró-Lula, depois do IR). Na faixa de mais de 5 SM ele é **negativo, de cerca de −5 p.p.** (com 1–2 p.p. vindos da mudança dos cortes).
- 2022 já era o patamar "pós-virada". O que 2026 acrescenta é um **topo mais à direita**, não um meio mais espremido.

---

## 7. Parâmetro para o modelo e integração (sem alterar a previsão)

**Parâmetro:** swing adicional atribuível ao mecanismo sanduíche, em p.p. da fatia bipartidária de Lula no 2º turno, **além do que as pesquisas por faixa já medem**.

| Faixa (parte do eleitorado*) | Central | Faixa de 80% | Confiança | Base |
|---|---|---|---|---|
| Até 2 SM (46%) | 0 | – | – | Referência |
| **2–5 SM** (36%) | **0** | −2 a +2 | Moderada (o sinal observado é o oposto do sanduíche: S = +5 ± 3) | Seções 2.2 e 3 |
| **5–10 SM** (11%) | **−1** | −4 a +1 | **Baixa: não identificável** com dados públicos (5–10 não é separado em 2026; só há indícios na aprovação de dez/2025 e no U ecológico de cerca de −1) | Seções 2.3 e 3 |
| 10+ SM (4%) | 0 | −3 a +3 | Baixa | – |

\* Participação na amostra do Datafolha de 2022 (renda familiar), como em `segmentos_voto.json`.

**Efeito nacional do valor central:** 0,11 × (−1) ≈ **−0,1 p.p.** Na prática é zero, e por isso não há motivo para mudar a previsão calibrada.

**Por que não entra no cenário central:**
1. As pesquisas por faixa já incorporam o comportamento de cada faixa. Somar um delta seria contar duas vezes.
2. A evidência para 2–5 SM vai na direção contrária.
3. Para 5–10 SM, a evidência é pequena e depende de n de 80 a 200.

**Como alavanca de cenário em `segmentos.py`** (sugestão para quem integra; não implementada):

```python
# premissas.json -> "cenarios": {"sanduiche": {"ativo": false, "delta_pp": {"2a5": 0.0, "5a10": 0.0},
#     "origem": "research_notes/.../sanduiche_eleitoral.md"}}
# Participação da faixa em cada região (perfil Datafolha 28-29/10/2022: 2-3 SM + 3-5 SM; 5-10 SM):
PESO_FAIXA_REGIAO = {   # (2-5 SM, 5-10 SM), fração do eleitorado da região
    "Sudeste": (0.42, 0.12), "Sul": (0.46, 0.16), "Nordeste": (0.24, 0.05),
    "Centro-Oeste": (0.40, 0.18), "Norte": (0.28, 0.09)}

def alavanca_sanduiche(regiao_uf: pd.Series, delta_pp: dict, q_nat: float) -> pd.Series:
    """Deslocamento em logito por UF, para somar a q_cal (2º turno), vindo de um swing extra por faixa de renda.
    regiao_uf: série uf -> região. delta_pp: {"2a5": δ, "5a10": δ} em p.p. da fatia de Lula."""
    d_pp = regiao_uf.map(lambda r: PESO_FAIXA_REGIAO[r][0] * delta_pp.get("2a5", 0.0)
                                   + PESO_FAIXA_REGIAO[r][1] * delta_pp.get("5a10", 0.0))
    # converte p.p. em logito em torno da fatia nacional (aproximação de primeira ordem)
    return d_pp / 100 / (q_nat * (1 - q_nat))
```

**Cenários sugeridos:**

| Cenário | δ 2–5 SM | δ 5–10 SM | Efeito no Brasil | Efeito por região |
|---|---|---|---|---|
| Neutro (padrão) | 0 | 0 | 0 | – |
| Sanduíche plausível | 0 | −1 | ≈ −0,1 p.p. | – |
| Sanduíche forte (estresse; não sustentado pelos dados) | −2 | −4 | ≈ −1,2 p.p. | SE −1,3; S −1,6; CO −1,5; N −0,9; NE −0,7 |

**Regras de uso:**
- Aplicar **só** como cenário, nunca na visão calibrada.
- Não somar ao cenário "viés histórico", porque o erro histórico já contém qualquer efeito de não resposta da classe média.

**Outras mudanças recomendadas** (não feitas, porque são arquivos do modelo):
1. **`segmentos.py` / `SEGMENTOS.md`:** a documentação diz que "não há cruzamentos de 2º turno de 2026". Agora há: Datafolha 15–17/09/2026, situação A.
   - Renda: 53/37, 41/50, 32/60.
   - Escolaridade: 55/37, 43/47, 43/48.
   - Católicos 51/39; evangélicos 32/60.
   - Região: SE 42/46; S 32/57; NE 62/31; CO/N 41/52.
   - Fonte: PDF do Poder360, `static.poder360.com.br/uploads/2026/09/pesquisa-datafolha-17set2026.pdf`.
   - Esses números poderiam substituir a mistura 50/50 com 2022 em `FONTES_VOTO` para o 2º turno.
2. **`segmentos_voto.json`:** a faixa "Mais de 5 SM" de 2026 deveria levar o aviso de que o corte em SM de 2026 é uma renda real cerca de 10% mais alta que em 2022.

---

## 8. Limitações e próximos dados

**Limitações**
- Os n por faixa são pequenos no topo, e as faixas de 2026 da Quaest e do Datafolha de 03/10 têm n estimado.
- As matérias secundárias têm erros: a Quaest de mar/2025 inverteu os números da faixa de mais de 5 SM; corrigimos.
- Algumas datas de campo de 2025 vêm de memória ou das matérias e estão marcadas no CSV.
- A linha "2–5 SM 43/52" da Quaest tem rodada incerta (ago/2025 ou mai/2026).
- Não obtivemos o Datafolha da véspera do 1º turno de 2022 por faixa, nem nenhuma pesquisa de 2023 por faixa.

**Para fechar as lacunas:**
- tabelas completas do Datafolha de 1–3/10/2026, que podem ter 5–10 e 10+;
- ESEB 2022 e, quando sair, ESEB 2026, com renda individual e perguntas de justiça e atribuição;
- relatórios completos da Quaest, com aprovação por faixa desde fev/2023;
- teste dentro das cidades: voto por seção × renda do setor censitário do Censo 2022, nas capitais;
- previsão implícita por município × erro, para testar a não resposta da classe média.
