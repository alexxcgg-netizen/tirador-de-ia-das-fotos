# Mercados de previsão: eleição presidencial Brasil 2026 (1º turno em 4/out/2026)

**Coleta:** dados primários das APIs públicas, coletados em **3/out/2026, entre 19:14 e 19:17 UTC** (16:14–16:17 em Brasília):
- Polymarket Gamma: 19:14:38 UTC
- CLOB, histórico: ~19:15 UTC
- Kalshi: 19:15:35 UTC
- PredictIt: 19:16:38 UTC (o próprio arquivo da PredictIt tem carimbo de 15:15 UTC)
- Manifold: ~19:16 UTC

Nenhuma API foi bloqueada. A Kalshi devolveu "too_many_requests" em uma série; a consulta foi repetida e funcionou.

**Arquivos brutos** em `raw_mercados/` nesta pasta:
- `polymarket_events_snapshot.json`: JSON completo de 38 eventos.
- `polymarket_snapshot_clean.txt`: tabela de preços.
- `polymarket_historico_diario.csv`: histórico diário de 17 séries, de set/2025 a 3/out/2026.
- `kalshi_*.json`.
- `predictit_all.json`.
- `holders_*.json`: maiores detentores na Polymarket.
- `fetch.py`: script de coleta.

**Convenções:**
- "Preço" é o meio do intervalo entre a melhor oferta de compra e a de venda (bid/ask), ou o `outcomePrice` da Gamma, em US$ por contrato que paga US$ 1. Lê-se direto como probabilidade implícita.
- "Normalizado" significa dividir cada preço pela soma de todos os resultados, para remover o overround (a margem embutida que faz a soma passar de 100%).

---

## 1. Polymarket: todos os mercados da eleição de 2026, preços atuais, volume e liquidez

### Takeaway
No mercado principal "quem vence a eleição" (inclui o 2º turno; US$ 163,4 mi negociados, o maior mercado sobre o Brasil), Flávio Bolsonaro está em **59,4%** e Lula em **40,5%**. Normalizado, fica cerca de 58,8% contra 40,1%.

Os mercados do 1º turno apontam o contrário no curto prazo:
- Lula aparece em **72,5%** para terminar em 1º lugar no 1º turno.
- Há só **5,3%** de chance de alguém vencer já no 1º turno.
- Lula + Flávio no 2º turno: cerca de 98–99%.

Ou seja, o mercado espera que Lula lidere o 1º turno por pouco e que Flávio vença o 2º turno. O número "Flávio 57% / Lula 41,5%" do resumo anterior era próximo da realidade, mas desatualizado ou arredondado. O valor verificado é 59,4% / 40,5%.

### Cited Findings
**Mercado principal: "Brazil Presidential Election"** ([Gamma API](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election); [página](https://polymarket.com/event/brazil-presidential-election))
- Aberto em 18/set/2025. Encerramento previsto para 5/out/2026, mas o mercado inclui um eventual 2º turno.
- Volume total: **US$ 163.427.435**.
- Liquidez: **US$ 26,77 mi**.
- Contratos em aberto (open interest): **US$ 9,39 mi**.
- Volume em 24h: US$ 1,50 mi; em 7 dias: US$ 7,48 mi; em 30 dias: US$ 18,39 mi.
- 21.469 comentários.
- O evento está marcado como `restricted: true`.
- Preços:
  - Flávio: 0,5935 (bid 0,593 / ask 0,594).
  - Lula: 0,405 (bid 0,40 / ask 0,41).
  - Renan Santos e Alckmin: 0,15% cada.
  - Os demais (Tarcísio, Michelle, Jair, Haddad, Ratinho, Zema, Caiado etc.): 0,05% cada.
  - A soma dos "SIM" é 1,009.
- O volume acumulado por candidato mostra quanto dinheiro foi para nomes que não chegaram à disputa:

  | Candidato | Volume acumulado |
  |---|---|
  | Renan Santos | US$ 16,1 mi |
  | Tarcísio | US$ 14,6 mi |
  | Lula | US$ 14,3 mi |
  | Flávio | US$ 13,9 mi |
  | Ratinho Jr. | US$ 10,5 mi |
  | Eduardo Bolsonaro | US$ 10,5 mi |
  | Michelle | US$ 10,4 mi |

  [Gamma API](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election)

**Mercados do 1º turno** (todos via `https://gamma-api.polymarket.com/events?slug=<slug>`):
- **Vencedor do 1º turno** (`brazil-presidential-election-first-round-winner`; criado em 31/ago/2026):
  - Lula 72,5% (bid 0,72 / ask 0,73); Flávio 28,5%. Normalizado: 71,4% / 28,1%.
  - Volume US$ 1,04 mi; liquidez US$ 1,44 mi; 24h US$ 183 mil.
  - [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-winner)
- **"Algum candidato vence no 1º turno?"**: SIM **5,3%** (bid 0,052 / ask 0,054). Volume US$ 610 mil; liquidez US$ 112 mil. [Gamma](https://gamma-api.polymarket.com/events?slug=will-any-presidential-candidate-win-outright-in-the-first-round-of-the-brazil-election)
- **Quem vai ao 2º turno:** Flávio 98,8%, Lula 98,4%. Volume US$ 1,09 mi. [Gamma](https://gamma-api.polymarket.com/events?slug=which-candidates-will-advance-to-brazils-presidential-runoff)
- **2º lugar no 1º turno:** Flávio 71,5%, Lula 27,6%. Volume **US$ 9,05 mi**, o 2º maior mercado; liquidez US$ 3,07 mi. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-2nd-place)
- **3º lugar:** Renan Santos 52,5%, Augusto Cury 25,1%, Ronaldo Caiado 20,5%. Volume US$ 1,96 mi. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-3rd-place)
- **4º lugar:** Cury 39%, Caiado 28,5%, Renan 27,5%. Volume de apenas US$ 8 mil. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-4th-place)
- **Margem de vitória no 1º turno** (diferença em pontos percentuais de votos válidos entre 1º e 2º colocados):

  | Faixa | Probabilidade |
  |---|---|
  | Lula vence por menos de 5 pp | **57,5%** |
  | Lula vence por 5–10 pp | 17,0% |
  | Lula vence por 10–15 pp | 0,8% |
  | Flávio vence por menos de 5 pp | 22,2% |
  | Flávio vence por 5–10 pp | 4,4% |

  Volume US$ 970 mil. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-margin-of-victory)
- **Votos válidos de Lula no 1º turno:**
  - Faixas baixas: 44% ou mais = 69,5%; 41–44% = 24%; 38–41% = 5,7%; abaixo de 38% = cerca de 2,8%. Volume de US$ 46 mil.
  - Faixas altas (criadas em 2/out): 44–47% = 53%; abaixo de 44% = 30,5%; 47–50% = 16,5%; 50% ou mais = cerca de 4,7%. Volume de apenas US$ 1,7 mil.
  - A regra de resolução usa votos válidos.
  - [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-lula-da-silva-vote-share); [Gamma faixas altas](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-lula-da-silva-vote-share-higher-strikes-20261002141337150)
- **Votos válidos de Flávio:**
  - 39% ou mais = 91,5% (US$ 232 mil negociados).
  - Faixas altas: 42–45% = 39%; 39–42% = 34%; 45–48% = 15%; abaixo de 39% = 8,5%; 48% ou mais = cerca de 6,6%.
  - [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-flavio-bolsonaro-vote-share); [Gamma faixas altas](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-flavio-bolsonaro-vote-share-higher-strikes)
- **Votos válidos de Renan Santos:** 2–4% = 54,5%; 4–6% = 26,5%; abaixo de 2% = 8,2%; 6–8% = 7,8%; 8% ou mais = 6,7%. Volume US$ 281 mil, dos quais US$ 180 mil na faixa de 8% ou mais. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-renan-santos-vote-share)
- **Votos válidos de Augusto Cury:** 2–4% = 41,5%; 4–6% = 35,5%; 6% ou mais = 10,5%; 1–2% = 10,5%. Volume US$ 22 mil. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-augusto-cury-vote-share)
- **Comparecimento** (votos/eleitorado, conforme TSE): 78–80% = 40%; 76–78% = 38,5%; abaixo de 76% = 15,5%; 80–82% = 11,5%; 82% ou mais = 2,2%. A soma dá 1,077, um overround alto. Volume ínfimo, US$ 3,8 mil. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-turnout)
- **Participação em debate antes do 1º turno** (Flávio e Lula): o preço do SIM é cerca de 0 para ambos, ou seja, o mercado precifica que nenhum dos dois participou de debate televisionado até 3/out. Volumes de US$ 71 mil e US$ 62 mil. Isso é preço de mercado, não um fato verificado. [Gamma Flávio](https://gamma-api.polymarket.com/events?slug=flavio-bolsonaro-participates-in-debate-before-first-round); [Gamma Lula](https://gamma-api.polymarket.com/events?slug=lula-participates-in-debate-before-first-round)
- **"Lula vira sobre Flávio até 15/out":** 35%. Volume US$ 24 mil. [Gamma](https://gamma-api.polymarket.com/events?slug=lula-flips-bolsonaro-for-brazil-president-by)
- **"Trump vai endossar quem?":** Flávio 27,5%. [Gamma](https://gamma-api.polymarket.com/events?slug=who-will-trump-endorse-for-president-of-brazil-20260803210809)

**Vencedor do 1º turno por estado** (criados em 17/ago/2026). A liquidez gira em torno de US$ 200–440 mil cada, mas o volume é baixo, de US$ 12–93 mil. Fonte: [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-1st-place-in-minas-gerais), mesmo padrão de slug para os demais estados.

| Estado | Preço implícito |
|---|---|
| SP | Flávio 97% |
| RJ | Flávio 98,3% |
| MG | **Lula 72% / Flávio 23,3%**, o estado mais disputado (US$ 74 mil negociados) |
| BA | Lula 99,1% |
| PE | Lula 99,3% |
| CE | Lula 99,6% |
| PA | Lula 96,2% |
| AM | Lula 80,5% / Flávio 24% |
| PR | Flávio 99,1% |
| RS | Flávio 97,9% |
| SC | Flávio 98,6% |
| GO | Flávio 94,8% / Caiado 4,6% |
| DF | Flávio 97% |
| ES | Flávio 97,6% |

**Mercados correlatos:**
- Senado, partido com mais cadeiras conquistadas: PL 95,8%.
- Câmara, maior bancada: PL 70,5%, UPB 25,2%.
- Governo de SP: Tarcísio 99,6%.
- Governo do RJ: Eduardo Paes 77%, Douglas Ruas 22,8%. Volume US$ 593 mil.
- [Gamma senado](https://gamma-api.polymarket.com/events?slug=next-brazil-senate-election-most-seats-won); [Gamma câmara](https://gamma-api.polymarket.com/events?slug=brazil-chamber-of-deputies-election-winner)

**Busca completa** por "brazil", "brasil", "lula", "flavio bolsonaro", "tarcisio" e "brazil election" ([public-search](https://gamma-api.polymarket.com/public-search?q=brazil)). Também aparecem estes mercados:
- Já resolvidos: "Will the Workers' Party nominate Lula by Aug 15", "Flavio Bolsonaro VP Candidate", "Flávio Bolsonaro charged or arrested by Sept 30" e "Will Jair Bolsonaro be arrested by Aug 31, 2025".
- Ainda abertos: "Alexandre de Moraes out as STF justice?" e "Any STF justice removed by impeachment before 2027?".

### Inferences
- Os preços da Polymarket são internamente coerentes, com uma ressalva:
  - Lula em 1º no 1º turno: cerca de 72–75% (somando o mercado de vencedor do 1º turno com as faixas de margem favoráveis a Lula, que dão 75,3%).
  - Flávio vence o 2º turno: cerca de 59%.
  - Juntos, esses preços implicam que o mercado vê **transferência de votos do 3º colocado em diante** (Renan, Caiado, Cury, Zema), ou abstenção diferencial, favorecendo Flávio no 2º turno.
  - A ressalva é que o centro implícito dos votos válidos de Lula, cerca de 45–46%, contra cerca de 42–43% de Flávio, deixa por volta de 11–13% para os demais. Isso é coerente com as faixas de Renan, Cury e Caiado.
- Tirando o mercado principal (US$ 163 mi) e o de 2º lugar (US$ 9 mi), os mercados derivados têm volume baixo, de dezenas a centenas de milhares de dólares. Os preços de faixas e de estados são, portanto, sinais fracos e fáceis de mover.

### Gaps
- Não encontrei mercado da Polymarket de vitória de Lula por estado no 2º turno, nem de margem do 2º turno.
- Não há dados oficiais da Polymarket sobre a nacionalidade dos operadores.

---

## 2. Histórico de preços (set/2025 a out/2026) e grandes movimentos

### Takeaway
A trajetória da Polymarket teve cinco fases:
1. **Set–nov/2025:** Lula como favorito (50–60%) e Tarcísio como principal adversário (20–48%).
2. **Dez/2025–jan/2026:** Flávio entra (de 1–2% para 12–27%) e Tarcísio desaba.
3. **Mar–mai/2026:** Flávio empata com Lula e chega a liderar (pico de cerca de 45% em 8/mai).
4. **14/mai/2026:** queda abrupta de Flávio (-10,7 pp), coincidindo com a data dos áudios de Vorcaro. Até ago/2026, Lula se recupera e chega a 60–65%.
5. **Fim de ago a out/2026:** reversão forte. Flávio passa Lula em **11/set/2026** (+6,1 pp naquele dia) e chega ao pico de cerca de 61% em 1º/out.

### Cited Findings
Fonte de toda a série: [CLOB prices-history](https://clob.polymarket.com/prices-history?market=<tokenId>&interval=max&fidelity=1440), com os tokens obtidos na [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election). CSV completo em `raw_mercados/polymarket_historico_diario.csv`. Os valores são o ponto diário (UTC) do contrato SIM.

**Pontos semanais selecionados** (mercado principal, colunas Flávio / Lula / Tarcísio / "alguém vence no 1º turno"):

| Data | Flávio | Lula | Tarcísio | Vence no 1º turno |
|---|---|---|---|---|
| 19/set/2025 (início) | n/d | 59% | 48% | 20,5% |
| 3/out/2025 | n/d | 42,5% | 37% | 15,5% |
| 7/nov/2025 | n/d | 57% | 29,5% | 13,5% |
| 5/dez/2025 | 1,7% | 47,5% | 35,5% | 15,5% |
| 19/dez/2025 | 17,8% | 46,5% | 19% | 13,5% |
| 23/jan/2026 | 27,3% | 52,5% | 5,1% | 14,5% |
| 27/fev/2026 | 34,1% | 48,5% | 2,8% | 10,5% |
| 27/mar/2026 | 41,8% | 41,5% | 1,3% | 15% |
| 8/mai/2026 | 45,1% | 37,5% | 0,2% | 12% |
| 22/mai/2026 | 24,9% | 45,5% | n/d | 14,5% |
| 26/jun/2026 | 22,1% | 56,5% | n/d | 15,5% |
| 7/ago/2026 | 26,9% | 64,5% | n/d | 7% |
| 28/ago/2026 | 35,9% | 57,5% | n/d | 9,5% |
| 4/set/2026 | 44% | 54,5% | n/d | 5,3% |
| 11/set/2026 | 52,5% | 45,5% | n/d | 6,9% |
| 25/set/2026 | 56,1% | 43,5% | n/d | 4,9% |
| 1º/out/2026 | **61,2%** | 38,5% | n/d | 4,6% |
| 3/out/2026 | 59,4% | 40,5% | n/d | 5,4% |

Em set/2025, o mercado também precificava Haddad em 39,5%, Jair Bolsonaro em 21,5% e Michelle em 10,5%. Esses preços iniciais tinham pouca liquidez.

**Maiores variações diárias da Polymarket e eventos que coincidem com elas.** A correspondência com os eventos é inferência por data; não estabeleço causalidade.
- **6/dez/2025:** Flávio sobe de 1,7% para 13,7% (+12 pp) e Tarcísio cai de 35,5% para 21% (-14,5 pp). Data compatível com o lançamento da pré-candidatura de Flávio no início de dez/2025.
- **17/dez/2025:** Flávio +5,9 pp, de 11,3% para 17,2%.
- **23/jan/2026:** Flávio +8 pp (de 19,3% para 27,3%) e Tarcísio -7,5 pp (de 12,6% para 5,1%). A CNN Brasil noticiou que Tarcísio descartou a candidatura e disse que buscaria a reelegição em SP; a data exata da declaração não foi confirmada. [CNN Brasil](https://www.cnnbrasil.com.br/politica/tarcisio-descarta-disputar-presidencia-em-2026-e-aposta-em-reeleicao/)
- **30/abr/2026:** Flávio +4,2 pp, chegando a 43%.
- **14/mai/2026:** **Flávio -10,7 pp**, de 43% para 32,4%, e Lula +3 pp. Continuou caindo até 28,4% em 16/mai e 24,9% em 22/mai. A data coincide com os áudios de Vorcaro de 13/mai/2026, citados no briefing.
- **3–4/jun/2026:** Flávio +4,7 pp e depois -7,9 pp, chegando a 25,4%.
- **2/jul/2026:** Lula +5 pp, para 60,5%.
- **28/ago/2026:** Lula -5 pp, de 62,5% para 57,5%. Começa a reversão.
- **9/set/2026:** Flávio +5,5 pp (para 45,4%) e Lula -6 pp (para 52,5%).
- **11/set/2026:** **Flávio +6,1 pp (para 52,5%) e Lula -7 pp (para 45,5%). Primeira liderança de Flávio.**
- 19–22/set/2026: Flávio passa de 56,5% para 60,6%.
- **25/set/2026:** Flávio cai de 58,2% para 56,1%. Data da medida provisória (MP) das bets.
- 1º/out: Flávio no pico de 61,2%.
- 2–3/out: recua para 59,4% depois do Datafolha.

**Imprensa sobre a virada de setembro:**
- Na Polymarket, Lula liderou até 10/set/2026 (52% contra 47,7%); Flávio passou à frente em 11/set e não perdeu mais a liderança. [Brazil Journal, 1/out/2026](https://braziljournal.com/flavio-sera-presidente-pelo-menos-segundo-a-kalshi-e-polymarket)
- A Kalshi atribuiu a virada às investigações sobre Fábio Luís "Lulinha" no caso de fraude no INSS. O texto também cita acusações de que o governo Trump estaria tentando influenciar a eleição (tarifas, designação de facções como organizações terroristas). [Kalshi News, 15/set/2026](https://news.kalshi.com/p/brazil-2026-election-odds-bolsonaro-favored-over-lula)
  - Kalshi naquela data: Flávio 55%, Lula 44%.
  - Pesquisa AtlasIntel/Bloomberg citada pela Kalshi: 2º turno com Flávio 46,4% e Lula 46,2%.

**Movimentos intradiários ao redor da MP das bets e do Datafolha:**
- 25/set, 20h: Flávio 57,4%, Lula 43%.
- Quinta-feira, 1º/out, à tarde: Flávio 62,2%, Lula 38%.
- Depois do Datafolha de 2/out (às 8h21): Flávio 55,6%, Lula 44%.
- [NextPredict, 2/out/2026](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)

**Outras séries:**
- **Vencedor do 1º turno** (desde 31/ago/2026): Lula começou em 91,5%; caiu para 87% em 4/set, 79,5% em 11/set e 68% em 21–22/set; está em 72,5% em 3/out.
- **2º lugar no 1º turno:** Flávio passou de 62,5% (fev) para 87,5% (7/ago) e caiu para 71,5% (3/out). A queda reflete a chance crescente de Flávio terminar em 1º.
- **"Alguém vence no 1º turno":** caiu de cerca de 20% (set/2025) para cerca de 5% (out/2026).

### Inferences
- Há dois movimentos claros e sustentados ligados a fatos datados: a entrada de Flávio em dez/2025 e o choque de 14/mai/2026. A virada de setembro foi gradual, de 28/ago a 22/set, com picos em 9 e 11/set. Pela data, coincide com a pesquisa AtlasIntel de empate no 2º turno e com o noticiário sobre Lulinha/INSS.
- O mercado reagiu pouco à MP das bets (25/set), algo entre -2 e +5 pp de ruído, e reagiu de forma mensurável ao Datafolha de 2/out: Flávio caiu de cerca de 62% para cerca de 56–59%.

### Gaps
- O CLOB não devolveu histórico do mercado de 2022 (0 pontos), então não foi possível reconstruir a curva da Polymarket em 2022.
- Não encontrei datas confirmadas por fonte primária para a "crise do STF" de setembro/2026 nem para os debates. A correspondência com esses eventos fica para quem cruzar com a cronologia do briefing.

---

## 3. Kalshi, PredictIt, Manifold, casas de apostas (Betfair, Smarkets e outras)

### Takeaway
Todas as plataformas convergem: Flávio entre **57% e 60%** e Lula entre **40% e 44%** para vencer a eleição. As casas de apostas tradicionais são um pouco menos favoráveis a Flávio (cerca de 56–57% normalizado). A Kalshi espelha a Polymarket nos mercados de 1º turno: Lula 74% para vencer o 1º turno e 4,4% de chance de vitória no 1º turno.

### Cited Findings
**Kalshi** ([API de mercados](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBRPRES&status=open), coletado em 3/out 19:15 UTC):

| Mercado | Preço / probabilidade | Volume (contratos) |
|---|---|---|
| KXBRPRES (vencedor) | Flávio 0,61 (bid 0,60 / ask 0,61; open interest 663 mil); Lula 0,40 (bid 0,39 / ask 0,40; open interest 680 mil); Renan 0,4%; Cury 1% | Flávio 1,44 mi; Lula 1,34 mi; Renan 1,16 mi. Normalizado (meio do intervalo): Flávio ≈ 60%, Lula ≈ 39% |
| KXBRPRES1R (vencedor do 1º turno) | Lula 0,74 (bid 0,74 / ask 0,75); Flávio 0,29 | Lula 126 mil; Flávio 181 mil |
| KXBRAZILPRES1R (alguém vence no 1º turno) | SIM 4,4% (bid 0,043 / ask 0,049) | 82,8 mil |
| KXBRPRESIDENT2 (2º lugar) | Flávio 74%, Lula 26% | n/d |
| KXBRPRES1MOV (margem do 1º turno) | Lula 0–5 pp 59%; Lula 5–10 pp 14%; Lula 10–15 pp 1%; Flávio 0–5 pp 23% (bid 0,20 / ask 0,21); Flávio 5–10 pp 5% (bid 0,03 / ask 0,04); Flávio 10–15 pp 6% (último negócio; bid 0 / ask 0,04) | n/d |
| KXBRPRESADVANCE (vai ao 2º turno) | Lula 99%, Flávio 99% | n/d |

**KXVOTEBR1** (faixas do tipo "pelo menos X%"):
- Lula: ≥40% = 0,82–0,86; ≥42% = 0,65–0,67; **≥44% = 0,64–0,65**; ≥45% = 0,25–0,38; ≥46% = 0,09–0,19; ≥50% = 0,03–0,08.
- Flávio: ≥39% = 0,88–0,93; ≥42% = 0,52–0,60; ≥47% = 0,16–0,19.
- Renan: ≥4% = 0,43; ≥7% = cerca de 0,2.
- Caiado: ≥4% = 0,38–0,48.
- Cury: ≥4% = 0,52–0,57.

**KXBRAZILTURNOUT** (comparecimento em número de eleitores):
- ≥122 mi = 97%; **≥124 mi = 65–67%**; ≥126 mi = 24–30%; ≥128 mi = 11–12%.
- [API Kalshi](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBRAZILTURNOUT&status=open)

**Volume total da Kalshi segundo a imprensa** (a API dá volume em contratos, não em US$):
- US$ 3,12 mi em 13/ago/2026. [Oddschecker](https://www.oddschecker.com/us/insight/specials/politics/20260813-brazil-election-odds-lula-da-silva-regains-advantage-over-flavio-bolsonaro-ahead-of-october-election)
- Cerca de US$ 4,5 mi em 21/set/2026. [Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)
- US$ 6,49 mi em 2/out/2026. [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)

**Kalshi em 13/ago/2026:** Lula 65%, Flávio 28%, Renan 6%. [Oddschecker](https://www.oddschecker.com/us/insight/specials/politics/20260813-brazil-election-odds-lula-da-silva-regains-advantage-over-flavio-bolsonaro-ahead-of-october-election)

**PredictIt**, mercado 8544 ([API](https://www.predictit.org/api/marketdata/all/); [página](https://www.predictit.org/markets/detail/8544/Who-will-win-the-2026-Brazilian-presidential-election); carimbo de 3/out 15:15 UTC):
- Flávio: último 0,62 (comprar SIM 0,63 / vender 0,60).
- Lula: último 0,43 (comprar 0,42 / vender 0,40).
- Zema: 0,01.
- Os últimos negócios somam 1,06. Normalizado: **Flávio ≈ 58,5%, Lula ≈ 40,6%**.

**Manifold**, dinheiro fictício ("mana"), mercado "2026 Brazil Presidential Election Winner?" ([API](https://api.manifold.markets/v0/slug/2026-brazil-presidential-election-w)):
- Flávio 57%, Lula 42,4%.
- Volume de 47.684 mana e só **58 apostadores**. É um sinal de baixíssimo peso.

**Casas de apostas no Reino Unido** (agregado da Oddschecker, consultado em 3/out/2026) ([Oddschecker](https://www.oddschecker.com/politics/world-politics/brazil-presidential-election/winner)):
- Flávio: odd decimal 1,67 (4/6); implícito 59,9%.
- Lula: 2,10 (11/10), implícito 47,6%; algumas casas pagam 2,20 (6/5), implícito 45,5%.
- Overround: 7,5% com 2,10, ou 5,3% com 2,20.
- **Normalizado: Flávio ≈ 55,7–56,9%; Lula ≈ 43,1–44,3%.**
- Casas listadas: bet365, William Hill, Unibet, Betfred, Betfair Sportsbook, Ladbrokes, BetVictor e BetMGM UK.

**Comparativo em 21/set/2026** ([Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)):

| Plataforma | Flávio | Lula |
|---|---|---|
| Polymarket | 58,7% | 40,5% |
| Kalshi | 61% | 41–42% |
| PredictIt | 59% | 43% |
| Smarkets | 56,8–59,5% | 40–42,4% |
| Manifold | 59% | 40% |
| Casas de apostas (Oddschecker) | 52% | 50% |

### Inferences
- A dispersão entre plataformas é pequena: cerca de 4 pp no preço do Flávio. Isso indica arbitragem ativa entre Polymarket, Kalshi e PredictIt, que não devem ser tratadas como sinais independentes.
- As casas tradicionais, cujo preço reflete exposição da banca e não só a opinião de apostadores, ficam um pouco mais perto de 50/50.

### Gaps
- **Betfair Exchange:** não obtive o preço da bolsa nem o volume casado. A página da Betfair devolveu 403 e a Oddschecker só mostra a Betfair Sportsbook.
- **Smarkets:** só tenho o dado de 21/set (via Rio Times), sem coleta própria.
- **Casas brasileiras:** não encontrei odds de casas brasileiras para a eleição. A Pública/Rio Times citam proibição de contratos eleitorais desde abr/mai de 2026, então não deve haver oferta legal. Não verificado diretamente.

---

## 4. Quem opera esses mercados, concentração e status legal no Brasil

### Takeaway
Não há dado público sobre a divisão entre brasileiros e estrangeiros. Formalmente, o acesso de brasileiros a esses mercados é proibido desde abr/mai de 2026, e a própria Polymarket marca o evento como "restricted". A concentração é relevante: um único operador detém cerca de 1,02 milhão de contratos SIM em Lula. Os candidatos, sobretudo do campo de Flávio, usaram as cotações como se fossem pesquisa.

### Cited Findings
**Maiores detentores na Polymarket**, mercado principal ([data-api holders](https://data-api.polymarket.com/holders?market=<conditionId>&limit=20); arquivos `raw_mercados/holders_*.json`):
- **Lula SIM:** o maior detentor ("unknwnfnd") tem 1.020.439 contratos. Os 20 maiores somam 3,64 mi de contratos. Os seguintes têm 576 mil, 575 mil, 259 mil e 245 mil.
- **Flávio SIM:** posições mais pulverizadas; os 20 maiores somam 2,62 mi. O maior tem 374 mil ("SuperavitFiscal") e há nomes como "RenanPresidente." (334 mil) e "LulaVaiPerder" (182 mil).
- Nos lados "NÃO" aparece um endereço sem nome com 4,69 mi de contratos em ambos. Provavelmente é o adaptador/contrato de risco negativo (neg-risk) da plataforma, não um apostador; isso não foi verificado.
- Para comparação, o open interest total do evento é de US$ 9,39 mi. [Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election)

**Proibição e status legal:**
- A Polymarket está proibida de oferecer e anunciar serviços no Brasil desde 24/abr/2026, mas continua fazendo isso. A AGU pediu informações à Fazenda, e a Meta bloqueou o Instagram da Polymarket no Brasil em setembro, a pedido da Secretaria de Prêmios e Apostas (SPA) do Ministério da Fazenda. [Pública](https://apublica.org/2026/09/apesar-de-proibicao-polymarket-promove-apostas-sobre-eleicoes-brasileiras/); [SBT News](https://sbtnews.sbt.com.br/noticia/economia/perfil-de-apostas-eleitorais-e-bloqueado-a-pedido-da-fazenda)
- Há divergência sobre a data da proibição: a Rio Times dá 4/mai/2026, a NextPredict diz que o Brasil bloqueou Polymarket, Kalshi e outras em abril de 2026, e a Pública diz 24/abr. [Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/); [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)
- A Rio Times afirma que não há dado público de como as posições se dividem entre operadores brasileiros e estrangeiros. [Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)
- **MP das bets:** a Pública dá sexta-feira, **26/set/2026**; a NextPredict dá "25/set". Segundo a Pública, os anúncios saem do ar em 5/out e 75% dos brasileiros apoiam a proibição. A Pública também diz que a Polymarket contratou representantes para fazer lobby no Brasil e que Donald Trump Jr. é consultor da plataforma. [Pública, 28/set/2026](https://apublica.org/2026/09/de-apostas-predicoes-e-eleicoes/)
- Pelo menos 10 candidatos, entre eles Flávio Bolsonaro, divulgaram cotações de mercados de previsão como indicador de vantagem. Elon Musk ampliou o alcance dessas postagens. Especialistas veem possível violação da lei eleitoral, que proíbe divulgar dados que não sejam de pesquisas registradas. [Pública](https://apublica.org/2026/09/flavio-bolsonaro-e-aliados-divulgam-apostas-do-polymarket-como-pesquisa-eleitoral/); [Pública](https://apublica.org/2026/09/de-apostas-predicoes-e-eleicoes/)
- A imprensa alinhada à direita noticia as cotações da Polymarket de forma recorrente, como em "A 3 dias da eleição, chance de Flávio vencer vai a 62%". [Revista Oeste](https://revistaoeste.com/politica/a-3-dias-da-eleicao-chance-de-flavio-vencer-vai-a-62-no-polymarket/)

### Inferences
- A combinação de proibição formal no Brasil, liquidação em cripto e mercados dominados por grandes posições sugere uma base de operadores majoritariamente estrangeira ou cripto-nativa, mais alguns brasileiros via VPN. Isso é inferência, sem dado direto.
- O fato de candidatos usarem as cotações como propaganda cria incentivo para mover o preço como sinal político. Com US$ 26,8 mi de liquidez, mover o mercado principal custa caro, mas os mercados derivados, de US$ 2 a 300 mil, são baratos de mover.

### Gaps
- Não há dado de nacionalidade nem de geolocalização dos operadores.
- Não consegui identificar os donos das carteiras.

---

## 5. Comparação com pesquisas e vieses conhecidos dos mercados

### Takeaway
As pesquisas mostram Lula à frente no 1º turno por 2 a 7 pp e o 2º turno empatado tecnicamente (Lula de 0 a +3 pp). Os mercados concordam com o 1º turno, mas dão cerca de 59–60% a Flávio no 2º turno.

Essa diferença tem duas leituras possíveis:
- Os mercados podem estar precificando um viés pró-direita nas pesquisas brasileiras, como em 2022, quando Bolsonaro foi subestimado em 4 a 7 pp no 1º turno, e transferências de votos favoráveis a Flávio.
- Ou podem estar refletindo o viés da base de operadores, como em 2024 nos EUA, onde acertaram.

O histórico é misto: em 2022, o favorito dos mercados (Lula) venceu, mas o mercado tinha volume pequeno.

### Cited Findings
**Pesquisas recentes, segundo a imprensa.** Há números conflitantes entre fontes para os mesmos institutos, provavelmente por diferenças entre votos totais e válidos, ou entre rodadas.
- **Datafolha 2/out/2026:** 1º turno Lula 42% × Flávio 38%; 2º turno Lula 48% × Flávio 45%, empate técnico. [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)
- **Datafolha 24/set:** 1º turno 40% × 36%; 2º turno 47% × 45%. [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)
- **Quaest (semana da eleição):** 1º turno Lula 39% × Flávio 34%; 2º turno 42% × 42%. [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)
- **Rio Times (21/set, atualizado em 29/set)** lista outros números como "1º turno":
  - Datafolha (15–17/set): 46 × 44.
  - AtlasIntel (11–16/set): 46,8 × 47,2.
  - Quaest (14/set): 40 × 42.
  - BTG/Nexus (28/set): 47 × 46.
  - CNT/MDA: 47,3 × 40.
  - Indexa: 43 × 42.
  - Média de cerca de 1,5 pp de vantagem para Lula no 2º turno.
  - Esses números parecem misturar cenários de 2º turno. Tratar com cautela. [Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)
- **AtlasIntel/Bloomberg (10/set):** 2º turno Flávio 46,4% × Lula 46,2%. [Kalshi News](https://news.kalshi.com/p/brazil-2026-election-odds-bolsonaro-favored-over-lula)
- **CNT/MDA (ago/2026):** 1º turno Lula 42,4% × Flávio 28,7%; 2º turno 48,0% × 39,1%. [Oddschecker](https://www.oddschecker.com/us/insight/specials/politics/20260813-brazil-election-odds-lula-da-silva-regains-advantage-over-flavio-bolsonaro-ahead-of-october-election)
- **Transferência de votos no Datafolha, 2º turno:**
  - Eleitores de Caiado: 50% Flávio × 33% Lula.
  - Eleitores de Renan: 54% × 14%.
  - Eleitores de Cury: 35% × 33%, com 30% em branco/nulo.
  - [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)

**Histórico de 2022:**
- Pesquisas finais do 1º turno para Bolsonaro, em votos válidos, contra o resultado de 43,20%:
  - Datafolha: 36% (erro de 7,2 pp).
  - Ipec: 37%.
  - AtlasIntel: 41,1%.
  - [Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)
- No 2º turno, o Datafolha deu 52% a Lula; o resultado foi 50,9%. [Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)
- O mercado de 2022 da Polymarket movimentou só cerca de US$ 334 mil (US$ 264 mil no contrato de Lula e US$ 64 mil no de Bolsonaro). [Gamma 2022](https://gamma-api.polymarket.com/events?slug=who-will-win-the-2022-brazilian-presidential-election)
- A Betfair movimentou US$ 23,6 mi, de US$ 27,3 mi no total agregado. [ElectionBettingOdds](https://www.electionbettingodds.com/Brazil2022_week.html)
- Antes do 2º turno de 2022, a Betfair Exchange tinha Lula a 1,55 (cerca de 65%) e Bolsonaro a 2,76 (cerca de 36%), segundo o snippet da busca. A página original devolveu 403 e não foi verificada. [Betfair (snippet)](https://betting.betfair.com/politics/general-politics-betting/brazilian-election-odds-lula-odds-on-to-beat-bolsonaro-in-sundays-vote-251022-204.html)
- A France24 relata que as pesquisas previam vantagem de cerca de 15 pp para Lula no 1º turno, contra uma diferença real de cerca de 5 pp. [France24](https://www.france24.com/en/americas/20221003-against-the-odds-brazil-s-bolsonaro-defies-polls-to-force-challenger-lula-into-presidential-run-off)

**EUA 2024:** na véspera, a média do RCP mostrava Trump e Harris empatados em 48,5%; a Polymarket dava Trump 58,6% × Harris 41,4% (às 19h de 4/nov). Trump venceu com 312 votos no Colégio Eleitoral e também no voto popular. [NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)

**Estudos de acurácia citados pela imprensa:**
- A XP, olhando 15 eleições globais, aponta 87% de acerto da Polymarket no dia da eleição, mas ressalta a amostra limitada. [Brazil Journal](https://braziljournal.com/flavio-sera-presidente-pelo-menos-segundo-a-kalshi-e-polymarket)
- Um estudo da Kalshi com 2,2 milhões de contratos desde 2021 aponta 90,6% de acerto 7 dias antes da eleição. [Brazil Journal](https://braziljournal.com/flavio-sera-presidente-pelo-menos-segundo-a-kalshi-e-polymarket)
- Os dois estudos medem acerto do favorito, não calibração. São estudos das próprias plataformas ou de corretoras.

### Inferences
**Comparação direta das faixas de 1º turno com as pesquisas.**
- O centro implícito dos votos válidos de Lula no mercado é de cerca de 45–46%: P(≥44%) ≈ 65–70% e P(≥47%) ≈ 20%.
- Para Flávio, o centro é de cerca de 42–43%: P(≥42%) ≈ 55–60% e P(≥45%) ≈ 20–25%.
- No Datafolha de 2/out (42 × 38 em votos totais), a conversão aproximada para votos válidos dá algo como 46 × 42, assumindo de 8 a 10% de brancos, nulos e indecisos.
- Logo, **no 1º turno, mercado e pesquisas estão muito próximos**. A divergência está só na leitura do 2º turno: a média das pesquisas dá Lula +0 a +3, enquanto o mercado dá cerca de 59–60% para Flávio.

**Vieses a considerar, de forma neutra:**
- **A favor do mercado:** em 2022 as pesquisas subestimaram Bolsonaro no 1º turno, e em 2024 os mercados acertaram nos EUA enquanto as pesquisas indicavam empate. A transferência de votos de Renan e Caiado favorece Flávio no Datafolha.
- **Contra o mercado:**
  - Há indício de viés de base de operadores (cripto, estrangeiros, maior proximidade com a direita), sem dado direto.
  - Brasileiros estão formalmente impedidos de operar, o que reduz a informação local.
  - Há uso político das cotações como propaganda.
  - A arbitragem entre plataformas faz com que três "fontes" sejam, na prática, uma só.
  - O histórico de 2022 é de baixa liquidez.
  - Um preço de 59% ainda implica cerca de 41% de chance de Lula: não é previsão "de certeza".

### Gaps
- Não obtive série histórica de preços da Polymarket/Betfair para 2022 (a API devolveu histórico vazio). Assim, não dá para medir a calibração do mercado naquele ano.
- Não encontrei estudo acadêmico independente sobre a acurácia de mercados de previsão em eleições brasileiras.
- Os números de pesquisa vieram da imprensa (NextPredict, Rio Times, Kalshi News, Oddschecker), não dos relatórios dos institutos. As fontes divergem, como mostra a lista da Rio Times.

---

## 6. Probabilidades implícitas consolidadas, normalizadas (3/out/2026, cerca de 19:15 UTC)

### Takeaway
O consenso dos mercados líquidos, normalizado, dá **Flávio cerca de 59% e Lula cerca de 40%** para vencer a eleição. Para o 1º turno: **Lula 1º colocado cerca de 72–74%**, **2º turno quase certo (cerca de 95%)** e margem de Lula no 1º turno abaixo de 5 pp como cenário modal (57–59%).

### Cited Findings

| Mercado | Polymarket (meio do intervalo, normalizado) | Kalshi (meio do intervalo) | PredictIt (último negócio, normalizado) | Casas no Reino Unido (normalizado) | Manifold |
|---|---|---|---|---|---|
| Flávio vence a eleição | 58,8% (bruto 59,35%) | ≈ 60% (bruto 0,605) | 58,5% (bruto 0,62) | 55,7–56,9% (odd 1,67) | 57% |
| Lula vence a eleição | 40,1% (bruto 40,5%) | ≈ 39% (bruto 0,395) | 40,6% (bruto 0,43) | 43,1–44,3% (odd 2,10–2,20) | 42,4% |
| Lula 1º no 1º turno | 71,4% (bruto 72,5%) | ≈ 72% (bruto Lula 0,745 / Flávio 0,285) | n/d | n/d | n/d |
| Alguém vence no 1º turno | 5,3% | 4,6% (meio do intervalo) | n/d | n/d | n/d |
| Lula ≥44% dos válidos | 69,5% (faixa baixa) / 69,5% (faixas altas: 1 − 30,5%) | 64,5% | n/d | n/d | n/d |
| Flávio ≥39% dos válidos | 91,5% | ≈ 90,5% | n/d | n/d | n/d |
| Margem: Lula < 5 pp | 56,0% (normalizado sobre a soma de 1,026) | 58,5% | n/d | n/d | n/d |

Fontes: [Polymarket Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election); [Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBRPRES&status=open); [PredictIt API](https://www.predictit.org/api/marketdata/all/); [Oddschecker](https://www.oddschecker.com/politics/world-politics/brazil-presidential-election/winner); [Manifold API](https://api.manifold.markets/v0/slug/2026-brazil-presidential-election-w)

**Volumes de referência:**
- Polymarket, mercado principal: US$ 163,4 mi (liquidez de US$ 26,8 mi).
- Kalshi, total: cerca de US$ 6,5 mi (NextPredict, 2/out).
- Polymarket, mercado de 2022: US$ 0,33 mi.
- Betfair 2022: US$ 23,6 mi.

### Inferences
- Pelo volume, o mercado da Polymarket sobre a eleição brasileira de 2026 é cerca de 490 vezes maior que o de 2022, e é de longe o principal sinal de mercado.
- O sinal de 59/40 deve ser lido como "leve favoritismo de Flávio no 2º turno". Não é margem ampla.

### Gaps
- Os preços mudam rapidamente na véspera. A Polymarket registrou um intervalo de 55,6% a 62,2% para Flávio entre 1º e 3/out. Atualize perto do fechamento das urnas, se possível.
