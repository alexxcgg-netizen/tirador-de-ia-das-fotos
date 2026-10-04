# Estados repetem 2022, e o mercado precifica Flávio

> ### Atualização de 3–4/10/2026
>
> Esta versão incorpora as pesquisas nacionais e estaduais da véspera, os números finais do simulador e do modelo alternativo, o backtest de 2014–2022 e correções a este próprio documento. As conclusões não mudam: estados, pesquisas e mercado seguem concordando no mapa e no 1º turno e divergindo por cerca de 1 ponto de margem no 2º turno. Os trechos alterados trazem a marca *(corrigido em 3/10)* ou *(atualizado em 3/10)*. O [briefing principal](Briefing%20elei%C3%A7%C3%A3o%20presidencial%202026.md) traz a mesma caixa com a tabela completa das pesquisas, e o [resumo executivo](Resumo%20executivo%20elei%C3%A7%C3%A3o%202026.md) reúne todos os entregáveis.
>
> **1. Pesquisas da véspera (fato).** Nacionais: Datafolha 3/10 **Lula 42 x Flávio 40** (válidos 45 x 42), 2º turno **47 x 46**; Quaest 2–3/10 **Lula 40 x Flávio 38** (válidos 46 x 45), 2º turno **Flávio 44 x Lula 42**; Futura 2–3/10 **Flávio 42,5 x Lula 40,5**, 2º turno **Flávio 48,0 x Lula 45,1**; Palver 30/9–3/10 Flávio 47 x Lula 43, 2º turno 49 x 44; Gerp 30/9–2/10 (corrigida) Flávio 43 x Lula 41, 2º turno 49 x 44; Veritá consolidada 20–25/9 Flávio 44,3 x Lula 43,8. A AtlasIntel nacional final (BR-00999/2026, 27/9–2/10, n = 4.945) saiu mais tarde na noite de 3/10, só em votos válidos: **Lula 47 x Flávio 44,1**; 2º turno **50,1 x 49,9** ([CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/atlas-lula-tem-47-dos-votos-validos-no-1o-turno-flavio-441/); [Exame](https://exame.com/brasil/pesquisa-para-presidente-atlasintel-lula-tem-47-e-flavio-bolsonaro-441-dos-votos-validos/)). Ela foi registrada no arquivo de pesquisas depois da rodada final do modelo, então **não entra** nas médias nem nas probabilidades abaixo. Na média simples, a AtlasIntel aparece com a rodada de 23–28/9. Média simples dos 14 institutos com campo entre 26/9 e 3/10 [calc]: 1º turno **41,5 x 39,9** (margem +1,6; mediana +2,0; dp 2,9); 2º turno **45,5 x 46,1** (margem −0,7; mediana ≈ 0; dp 2,6), ou **49,6% bipartidário para Lula**. Estaduais: Datafolha SP 3/10 Flávio 42 x Lula 36; Datafolha DF Flávio 47 x Lula 35 (2º turno 55 x 38); AtlasIntel 27/9–2/10 em válidos: BA Lula 60,5 x 29,8 (2º turno 64,6 x 35,4), PI 67,9 x 27,5, PA 51,4 x 41,3; Veritá 26/9–1/10 em totais: AC Flávio 66,6 x 25,9, AL Lula 51,2 x 39,8, AP Flávio 49,2 x 40,3 (2º turno 52,9 x 43,2), GO Flávio 50,6 x 32,8 (2º turno 57,7 x 37,1), DF Flávio 51,0 x 39,6. O título do G1 para o Datafolha de MG (41 x 41) não bate com o corpo da matéria e não foi usado como confirmado (`research_notes/.../pesquisas_vespera_extra.md`).
>
> **2. Modelo final.**
>
> | Probabilidade (500 mil simulações por visão) | **Simulador calibrado** (visão principal) | Simulador neutro (viés 0) | Simulador viés histórico pleno | Alternativo neutro | Alternativo histórico | Polymarket 3/10, 19h14 UTC (normalizado) |
> |---|---|---|---|---|---|---|
> | Lula vence a eleição | **35,7%** | 45,5% | 30,4% | 49,4% | 18,9% | 40,1% |
> | Flávio Bolsonaro vence a eleição | **64,3%** | 54,5% | 69,6% | 50,6% | 81,1% | 58,8% |
> | Decidida no 1º turno | 20,8% | 15,7% | 32,0% | 36,4% | 39,8% | 5,3% |
> | Lula em 1º no 1º turno | 34,1% | 56,3% | 23,5% | 58,0% | 27,4% | 71,4% |
> | Lula, 1º turno, % válidos (mediana; p10–p90) | 44,3 (40,1–48,5) | 46,0 (42,1–49,9) | 43,2 (38,8–47,7) | 46,8 (40,0–52,5) | 44,0 (37,2–49,7) | – |
> | Lula, 2º turno, % válidos (mediana; p10–p90) | 48,7 (43,9–53,6) | 49,6 (44,9–54,3) | 48,2 (43,2–53,2) | 49,5 (44,6–54,5) | 45,9 (41,0–50,8) | – |
>
> Fontes: `simulador/web/resultados.json` (gerado em 3/10 às 23h26 UTC, semente 20261004), `modelo_alternativo/resultados_alt.json` (22h57 UTC) e `simulador/data/mercados_snapshot.csv` ([Gamma API](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election)). Erro de Monte Carlo ≤ 0,07 p.p. em cada probabilidade. A tabela de comparação dentro de `modelo_alternativo/README.md` usa um instantâneo anterior do simulador (22h51 UTC, antes da rodada final) e não deve ser citada; valem os números acima.
>
> **Como ler as visões.** As cinco colunas de modelo usam praticamente a mesma média de pesquisas: Lula com 50,8% dos votos dos dois primeiros no 1º turno (alternativo: 50,7%) e 49,6% no 2º turno (alternativo: 49,5%). O que muda entre elas é **uma única premissa: se as pesquisas de 2026 erram como erraram na véspera de 2014, 2018 e 2022**. A visão *neutra* supõe erro sem direção. A *calibrada* aplica um viés estimado com os três ciclos e encolhido para zero (+1,5 ± 1,4 p.p. na fatia de Lula entre os dois primeiros no 1º turno, cerca de 3 p.p. de margem; no 2º turno, −0,3 ± 0,8). A *pleno* repete o erro médio histórico sem encolhimento (≈ +3,4 p.p.). A regra é simétrica: erros históricos com o sinal oposto produziriam correção para o outro lado. No 2º turno, o mercado (58,8% para Flávio) fica entre a visão neutra e a calibrada. No 1º turno, o mercado (Lula em 1º com 71%; decisão no 1º turno com 5%) fica mais perto da leitura literal das pesquisas do que qualquer visão de modelo. Os modelos dão de 16% a 40% de chance de decisão no 1º turno porque usam caudas largas (t de Student com dp de 4 p.p., escolhido no backtest) ou repetem o erro de 2014; sem 2014, o alternativo dá cerca de 0% [calc]. Nenhuma dessas colunas é recomendação: elas mostram quanto o resultado depende da premissa de viés.
>
> **3. Backtest (véspera de 2014, 2018 e 2022).** O simulador foi rodado como se fosse a véspera de cada eleição, só com as pesquisas daquele momento, e comparado com o TSE (`simulador/BACKTEST.md`). Na avaliação honesta fora da amostra (todos os parâmetros e o prior de viés escolhidos sem o ano testado), a visão calibrada cobriu **40/75/95%** dos resultados nacionais nos intervalos de 50/80/95% e **52/81/93%** dos resultados por UF; o ideal é 50/80/95. O CRPS foi de 2,08 p.p. no nacional e 3,55 por UF, e o erro absoluto médio da mediana, de 2,8 p.p. no nacional e 4,8 por UF. Na véspera do 1º turno, a média das pesquisas ficou mais favorável ao PT do que a urna nos três ciclos (fatia PT/adversário, depois da contração esperada da terceira via: +6,2 / +2,7 / +0,6 p.p.); na véspera do 2º turno, o erro foi pequeno e de sinal misto (+0,5 / −1,3 / −0,1). São 3 eleições no 1º turno e 2 no 2º turno projetado, e o viés calibrado depende muito de 2014 e 2018. O modelo alternativo, com outro método, teve cobertura por UF de 46/83/93% em 2018 e 2022.
>
> **4. Correções neste documento.** (a) **Gerp:** este documento dizia que a rodada final dava "Lula 46 x 44 no 1º turno" e que o instituto "mudou de direção". A linha estava com os nomes trocados. O correto é Flávio 46 x Lula 44 em válidos (43 x 41 em totais), e a Gerp segue do lado pró-Flávio (§1 e §6). (b) Médias nacionais refeitas: 1º turno 41,8 x 39,3 → **41,5 x 39,9**; 2º turno 45,5 x 45,9 → **45,5 x 46,1**; bipartidário 49,8% → **49,6%** (lead, §1, §3.2 e §9). (c) Datafolha nos válidos: 45 x 40 → **45 x 42** na véspera (§2.1). (d) AP e GO deixam de estar sem 2º turno: a Veritá publicou os dois (§3.1). (e) AtlasIntel "final": não houve dupla contagem. Os números iguais eram a mesma rodada de 23–28/9 citada por dois veículos, e a rodada BR-00999/2026 não tinha sido publicada até cerca de 22h de 3/10 (§1 e §10). (f) Tabela de parâmetros (§9) com os valores finais do simulador e lacunas (§10) atualizadas. (g) A conclusão ganhou nota: o modelo final não usou um parâmetro separado de retenção diferencial.

Os dados novos mostram um quadro coerente. As **pesquisas estaduais reproduzem quase exatamente o mapa do 2º turno de 2022**: a mediana do swing de Lula sobre 2022, nas 25 UFs com 2º turno pesquisado, é de **0,0 ponto**. Agregadas pelo comparecimento, essas pesquisas dão **Lula com 50,8% a 51,1% dos votos bipartidários** no 2º turno [calc]. As 14 pesquisas nacionais finais davam **49,8%** [calc]; com as rodadas da véspera e a linha da Gerp corrigida, dão **49,6%** *(atualizado em 3/10)*. Os mercados de previsão, agora verificados direto nas APIs em 3/10 às 16h15 (horário de Brasília), dão **Flávio 59,4% contra Lula 40,5% na Polymarket** ([Gamma API](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election)), com Kalshi, PredictIt e casas britânicas entre 56% e 60% para Flávio. No 1º turno, porém, **mercado e pesquisas concordam**: Lula termina em primeiro com cerca de 72%, e há apenas 5% de chance de decisão no 1º turno. A divergência está só no 2º turno, e é menor do que o briefing anterior sugeria. Com erro de margem de σ ≈ 4–6 p.p., 59% equivale a um deslocamento de apenas **0,9 a 1,4 p.p. de margem pró-Flávio** sobre a média das pesquisas [calc], e não de 2 a 3 p.p. A série oficial do TSE de 2002–2022, agregada nesta rodada, dá ao simulador o que faltava: um lean estadual muito estável (correlação de 0,97 entre 2018 e 2022), um swing relativo pós-2006 de cerca de 6 p.p. dividido entre um fator regional e um fator próprio da UF, e uma estrutura de correlação em blocos (NE+N contra S+CO). Ela também traz um alerta: em 2022, **Bolsonaro ficou com 70% do ganho líquido de votos entre os turnos**. As matrizes de transferência da Quaest de 2026 apontam na mesma direção, mas com 23% a 38% de branco/nulo entre eleitores de terceiros.

> **Convenções.** "Válidos" exclui brancos e nulos. "Totais" inclui brancos, nulos e indecisos. "Bipartidário" é Lula ÷ (Lula + Flávio). "Margem" é Lula − Flávio; valor positivo é pró-Lula. **[calc]** marca cálculo próprio a partir das fontes citadas. **[inferência]** marca premissa ou leitura não publicada por fonte. Em temas contestados, o texto separa **Fato** (documento, decisão, dado oficial), **Alegação** (acusação ou investigação não julgada) e **Opinião/Versão** (posição de ator). Este documento complementa o "Briefing eleição presidencial 2026"; a §1 lista o que ele corrige.

---

## 1. Sete números do briefing anterior mudam com os dados novos

O briefing anterior usava, para várias UFs, margens da Quaest tiradas de um resumo secundário (SpaceMoney) com data de campo não confirmada. As matérias do G1 (contratante: Globo) trazem números diferentes em quase todas elas. **A origem das margens antigas é incerta**, e RS e GO em especial não aparecem em nenhuma Quaest publicada. Os números do G1 devem substituí-las ([G1 SP](https://g1.globo.com/sp/sao-paulo/eleicoes/2026/noticia/2026/09/29/quaest-sp-presidente-29-setembro.ghtml); [G1 Sudeste](https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/03/maior-regiao-eleitoral-do-pais-sudeste-tem-disputa-apertada-entre-lula-e-flavio-bolsonaro.ghtml); [G1 BA](https://g1.globo.com/ba/bahia/eleicoes/2026/noticia/2026/09/24/quaest-bahia-presidente-24-setembro.ghtml); [G1 CE](https://g1.globo.com/ce/ceara/eleicoes/2026/noticia/2026/09/23/quaest-ce-presidente-23-setembro.ghtml); [G1 PE](https://g1.globo.com/pe/pernambuco/eleicoes/2026/noticia/2026/09/23/quaest-pe-presidente-23-de-setembro.ghtml); [G1 RJ](https://g1.globo.com/rj/rio-de-janeiro/eleicoes/2026/noticia/2026/09/29/quaest-rj-presidente-29-setembro.ghtml); [G1 GO](https://g1.globo.com/go/goias/eleicoes/2026/noticia/2026/09/24/quaest-em-go-presidente-24-setembro.ghtml); [G1 PR](https://g1.globo.com/pr/parana/eleicoes/2026/noticia/2026/09/24/quaest-parana-presidente-24-setembro.ghtml)).

| Item | Briefing anterior | Valor corrigido | Fonte da correção |
|---|---|---|---|
| Quaest SP, margem 2T | Flávio +12 | **Flávio +8** (35 x 43, 25–28/9); F+6 em 23/9 | G1 SP / G1 Sudeste |
| Quaest RJ, margem 2T | Flávio +13 | **Flávio +10** (34 x 44, 29/9); F+8 em 23/9 | G1 RJ |
| Quaest GO, margem 2T | Flávio +13 | **2T não divulgado**; 1T Flávio 33 x Lula 27, Caiado 23 (F+6) | G1 GO |
| Quaest BA / PE / CE, margem 2T | Lula +33 / +34 / +28 | **Lula +35 / +33 / +32** | G1 BA, PE, CE |
| Quaest PR, margem 2T | Flávio +20 | Flávio +20 (31 x 51): **confere** | G1 PR |
| Polymarket, vitória na eleição | 57% x 41,5% (resumo da KuCoin, não verificado) | **59,4% x 40,5%** (bid/ask 0,593/0,594 e 0,40/0,41), verificado na API em 3/10 às 19h14 UTC | [Gamma API](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election) |
| Viés que o mercado "embute" | "2–3 p.p. de margem pró-Flávio", ligado na tabela de sensibilidade a P ≈ 69% | **≈ 1 p.p.** (0,9 com σ = 4; 1,4 com σ = 6) [calc]; 69% exigiria mercado a 69%, não a 59% | Inversão normal: z(0,59) = 0,23 |

O briefing anterior também deixava pendências que agora se resolvem. Os valores de **AC e RO no 1º turno de 2018 são de fato quase idênticos** no TSE (62,238% e 62,240% para Bolsonaro, em válidos), então não há erro de transcrição. O PI de 2022 no 2º turno é 76,86%, não 76,83%. A abstenção de 2014 é de 19,39% no 1º turno e 21,10% no 2º ([TSE, dados abertos](https://dadosabertos.tse.jus.br)) [calc]. A **CPI das Bets** terminou em 12/6/2025, com o relatório de Soraya Thronicke rejeitado por 4 x 3 ([Rádio Senado](https://www12.senado.leg.br/radio/1/noticia/2025/06/12/cpi-das-bets-rejeita-relatorio-final)). A **Lei da Dosimetria** (Lei 15.402/2026) foi promulgada em 8/5, e em 9/5 Moraes suspendeu sua aplicação às execuções penais até decisão do plenário. Por isso, ela não reduziu a pena de Jair Bolsonaro ([STF Notícias](https://noticias.stf.jus.br/postsnoticias/relator-suspende-aplicacao-da-lei-da-dosimetria-a-execucoes-penais-no-stf/)). Há ainda dois ajustes menores. A CNT/MDA final dá 2º turno de **47,3 x 43,1**, e não 47 x 43. Duas pesquisas novas entram na média nacional: **Gerp** (Flávio 43 x Lula 41 no 1º turno, em totais, ou 46 x 44 em válidos; Flávio 49 x 44 no 2º) *(corrigido em 3/10: esta frase dizia "46 x 44" com Lula à frente, porque a linha original trazia os nomes trocados)* e **IFP** (40,62 x 37,49; 45,88 x 45,01) ([Wikipedia PT](https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026); [Poder360 – Gerp](https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-49-contra-44-de-lula-no-2o-turno-diz-gerp/); [Poder360 – IFP](https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-4588-contra-4501-de-flavio-no-2o-turno-diz-pesquisa/)). Com a última pesquisa de cada um dos 14 institutos com campo entre 26/9 e 3/10, incluídas as rodadas da véspera e a Gerp corrigida, a média do 1º turno fica em **Lula 41,5 x Flávio 39,9** (margem média +1,6; mediana +2,0; desvio-padrão 2,9). A do 2º turno fica em **45,5 x 46,1** (margem média −0,7; mediana ≈ 0; desvio-padrão 2,6) [calc] *(corrigido em 3/10; antes 41,8 x 39,3 e 45,5 x 45,9, com a Gerp invertida e sem as rodadas da véspera)*.

Duas datas seguem com divergência entre fontes. A MP das bets é de **25/9** segundo a Agência Senado e o Correio Braziliense, e de 26/9 segundo a Pública. A rodada "final" da AtlasIntel (27/9–2/10, BR-00999/2026) é citada com números **idênticos** aos da rodada de 23–28/9 (45,3 x 42,2; 2º turno 47,6 x 47,7), o que sugere que as fontes confundiram as rodadas ([Bloomberg Línea](https://www.bloomberglinea.com.br/brasil/nova-pesquisa-atlasintel-mostra-lula-e-flavio-empatados-na-reta-final-da-eleicao/)). *(Atualizado em 3/10: a conferência do simulador confirmou que era a mesma rodada de 23–28/9, BR-04391/2026, citada por dois veículos, e que a BR-00999/2026 ainda não tinha sido divulgada por volta das 22h de 3/10. Não há dupla contagem. Mais tarde, a BR-00999/2026 saiu com números diferentes, em válidos: Lula 47 x Flávio 44,1, e 2º turno 50,1 x 49,9. Ela não entrou na rodada final do modelo.)* Às 16h de 3/10, **Datafolha (BR-01708/2026, 4.006 entrevistas num único dia), Quaest (BR-02197/2026), Futura, Palver e Veritá ainda não tinham divulgado** as rodadas de véspera ([Exame](https://exame.com/brasil/pesquisas-para-presidente-hoje-veja-os-levantamentos-que-serao-divulgados-neste-sabado/)). O modelo deve ser reestimado quando elas saírem. *(Atualizado em 3/10: Datafolha, Quaest, Futura e Palver saíram na noite de 3/10 e entraram no modelo final; ver a caixa de atualização. A Veritá divulgou só estaduais e uma consolidação nacional de 20–25/9.)*

---

## 2. Mercados concordam com as pesquisas no 1º turno e divergem por um ponto no 2º

### 2.1 Preços verificados em 3/10: Flávio entre 56% e 61%, e Lula favorito para liderar o 1º turno

Os preços foram coletados direto das APIs públicas entre 19h14 e 19h17 UTC de 3/10, e os arquivos brutos estão em `raw_mercados/`. O mercado principal da Polymarket ("quem vence a eleição", incluindo o 2º turno) é o maior mercado já aberto sobre o Brasil: **US$ 163,4 milhões negociados**, US$ 26,8 milhões de liquidez e US$ 9,39 milhões em contratos abertos. É cerca de **490 vezes** o volume do mercado equivalente de 2022, que movimentou US$ 0,33 milhão ([Gamma API 2026](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election); [Gamma API 2022](https://gamma-api.polymarket.com/events?slug=who-will-win-the-2022-brazilian-presidential-election)) [calc]. As plataformas convergem: a Kalshi dá Flávio 0,61 e Lula 0,40 (meio do intervalo normalizado ≈ 60/39) ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBRPRES&status=open)). A PredictIt dá 0,62/0,43, que normalizado fica em 58,5/40,6 ([PredictIt API](https://www.predictit.org/api/marketdata/all/)). As casas britânicas agregadas pela Oddschecker pagam 1,67 por Flávio e 2,10–2,20 por Lula, o que normalizado dá **55,7–56,9% para Flávio** ([Oddschecker](https://www.oddschecker.com/politics/world-politics/brazil-presidential-election/winner)). A Manifold, com dinheiro fictício e só 58 apostadores, dá 57/42,4 ([Manifold API](https://api.manifold.markets/v0/slug/2026-brazil-presidential-election-w)).

| Mercado (3/10, ~19h15 UTC) | Polymarket | Kalshi | PredictIt | Casas britânicas | Manifold |
|---|---|---|---|---|---|
| Flávio vence a eleição | 58,8% (bruto 59,35) | ≈ 60% | 58,5% | 55,7–56,9% | 57% |
| Lula vence a eleição | 40,1% (bruto 40,5) | ≈ 39% | 40,6% | 43,1–44,3% | 42,4% |
| Lula em 1º no 1º turno | 71,4% (bruto 72,5) | ≈ 72% | – | – | – |
| Alguém vence no 1º turno | 5,3% | 4,6% | – | – | – |
| Margem do 1º turno: Lula por menos de 5 p.p. | 57,5% | 59% | – | – | – |
| Lula ≥ 44% dos válidos | 69,5% | 64,5% | – | – | – |
| Flávio ≥ 39% dos válidos | 91,5% | ≈ 90,5% | – | – | – |

Fontes: APIs citadas acima; normalização = preço ÷ soma dos preços de todos os resultados. Os mercados de faixa e de margem da Polymarket têm volume de US$ 2 mil a US$ 1 milhão ([Gamma – margem](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-margin-of-victory); [Gamma – 1º lugar](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-winner)).

As faixas de votos válidos põem o centro do 1º turno em **Lula ≈ 45–46% e Flávio ≈ 42–43%** [calc]. Isso cai em cima das pesquisas. Datafolha dá 45 x 40 nos válidos (**45 x 42 na rodada da véspera**, *atualizado em 3/10*), MDA 47,8 x 42,1 e Atlas cerca de 46,3 x 43,1 [calc]. O agregado bayesiano do modelo alternativo, com todas as pesquisas da véspera, dá **Lula 45,1 x Flávio 43,8** nos válidos, praticamente o centro implícito no mercado. **No 1º turno, portanto, o mercado não aposta em erro das pesquisas.** A distribuição da margem do 1º turno dá cerca de 27% de chance de Flávio terminar em primeiro (22,2% "por menos de 5" mais 4,4% "por 5–10") ([Gamma](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-margin-of-victory)). O briefing anterior chamava esse cenário de "não desprezível"; o mercado dá a ele cerca de 1 em 4. Os mercados de comparecimento apontam para o padrão de 2022. Na Kalshi, "pelo menos 124 milhões de votantes" sai a 65–67% e "pelo menos 126 milhões" a 24–30% ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBRAZILTURNOUT&status=open)). Isso equivale a um comparecimento mediano de cerca de 78,5–79% sobre 158,7 milhões de aptos, ou **abstenção de cerca de 21%** [calc].

**Os mercados estaduais divergem das pesquisas em SP.** A Polymarket dá Flávio com 97% de chance de vencer o 1º turno em SP, mas o Datafolha de 28–30/9 mostra Flávio 41 x 40 nos válidos (na rodada da véspera, 2–3/10, **Flávio 45 x 39**, o que reduz a distância; *atualizado em 3/10*; [G1 SP](https://g1.globo.com/sp/sao-paulo/eleicoes/2026/noticia/2026/10/03/datafolha-sp-presidente-3-outubro.ghtml)) ([G1 SP](https://g1.globo.com/sp/sao-paulo/eleicoes/2026/noticia/2026/10/02/datafolha-em-sp-flavio-bolsonaro-39percent-lula-38percent-cury-5percent-caiado-4percent-renan-4percent-zema-1percent.ghtml)). Em MG, o estado mais disputado no mercado, Lula tem 72% e Flávio 23,3%. No AM, Lula tem 80,5% ([Gamma – MG](https://gamma-api.polymarket.com/events?slug=brazil-presidential-election-first-round-1st-place-in-minas-gerais)). Os mercados estaduais movimentaram só US$ 12 mil a US$ 93 mil cada. A confiança extrema em SP pode refletir a memória dos erros de 2018 e 2022 naquele estado (−12 p.p. para Bolsonaro em 2018 no Ibope; cerca de +16 p.p. de erro de margem pró-Lula no Ipec em 2022) ou apenas liquidez rasa [inferência].

### 2.2 A trajetória teve dois choques datados e uma virada gradual em setembro

O histórico diário da Polymarket, reconstruído pela API de preços do CLOB, mostra cinco fases ([CLOB prices-history](https://clob.polymarket.com/prices-history?market=%3CtokenId%3E&interval=max&fidelity=1440); CSV em `raw_mercados/polymarket_historico_diario.csv`). Lula abriu como favorito em set/2025 (59%), com Tarcísio como principal adversário (48%). Em **6/12/2025**, Flávio saltou de 1,7% para 13,7% e Tarcísio caiu 14,5 p.p., na data do lançamento da pré-candidatura de Flávio. Em mar–mai/2026, Flávio empatou e chegou a 45,1% em 8/5. Em **14/5/2026**, ele caiu 10,7 p.p. num único dia (de 43% para 32,4%) e chegou a 24,9% em 22/5, um dia depois dos áudios com Vorcaro publicados pelo Intercept. Lula chegou a **64,5% em 7/8**. A virada começou em 28/8, data em que Lula perdeu 5 p.p. Os maiores movimentos foram em 9/9 e em **11/9, quando Flávio passou à frente** (+6,1 p.p., para 52,5%), sem perder a liderança depois. O pico foi de 61,2% em 1/10 ([Brazil Journal](https://braziljournal.com/flavio-sera-presidente-pelo-menos-segundo-a-kalshi-e-polymarket)). A Kalshi atribuiu a virada às investigações sobre "Lulinha" no caso INSS ([Kalshi News](https://news.kalshi.com/p/brazil-2026-election-odds-bolsonaro-favored-over-lula)). Essa atribuição é **opinião da plataforma**, sem teste causal. Pela data, a virada também coincide com a AtlasIntel/Bloomberg de 10/9, que mostrava empate no 2º turno (46,4 x 46,2), e com o início da crise Moraes/Vorcaro, em 1/9 [inferência].

O mercado reagiu pouco à MP das bets: Flávio passou de 58,2% para 56,1% em 25/9, dentro do ruído diário. A reação ao **Datafolha de 2/10** foi mensurável: de 62,2% na tarde de 1/10 para 55,6% logo depois da divulgação, e depois uma recuperação para 59,4% ([NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)). Em cerca de 48 horas, o preço de Flávio oscilou **6,6 p.p.**, o que dá a medida da incerteza do próprio mercado.

| Data | Flávio | Lula | Alguém vence no 1º turno |
|---|---|---|---|
| 19/9/2025 | – | 59% | 20,5% |
| 5/12/2025 | 1,7% | 47,5% | 15,5% |
| 23/1/2026 | 27,3% | 52,5% | 14,5% |
| 8/5/2026 | 45,1% | 37,5% | 12% |
| 22/5/2026 | 24,9% | 45,5% | 14,5% |
| 7/8/2026 | 26,9% | 64,5% | 7% |
| 11/9/2026 | 52,5% | 45,5% | 6,9% |
| 1/10/2026 | 61,2% | 38,5% | 4,6% |
| 3/10/2026 | 59,4% | 40,5% | 5,4% |

Fonte: [CLOB prices-history](https://clob.polymarket.com/prices-history?market=%3CtokenId%3E&interval=max&fidelity=1440), pontos diários em UTC.

### 2.3 Quem opera, o que a lei diz e por que o sinal deve ser descontado

**Fato:** a Polymarket está proibida de oferecer serviços no Brasil desde abril/maio de 2026. A data varia entre fontes: 24/4 para a Pública, 4/5 para a Rio Times. Mesmo assim, a plataforma continua promovendo os mercados. A Meta bloqueou o Instagram da Polymarket no Brasil em setembro, a pedido da Secretaria de Prêmios e Apostas, e o evento aparece marcado como `restricted` na API ([Pública](https://apublica.org/2026/09/apesar-de-proibicao-polymarket-promove-apostas-sobre-eleicoes-brasileiras/); [SBT News](https://sbtnews.sbt.com.br/noticia/economia/perfil-de-apostas-eleitorais-e-bloqueado-a-pedido-da-fazenda)). **Fato:** pelo menos 10 candidatos, entre eles Flávio, divulgaram cotações como se fossem indicador de vantagem. Especialistas ouvidos pela Pública apontam possível violação da regra que só permite divulgar pesquisas registradas, o que é **opinião jurídica**, sem decisão ([Pública](https://apublica.org/2026/09/flavio-bolsonaro-e-aliados-divulgam-apostas-do-polymarket-como-pesquisa-eleitoral/)). A concentração é relevante: o maior detentor de "Lula SIM" tem **1,02 milhão de contratos**, e os 20 maiores somam 3,64 milhões. Do lado de Flávio, as posições são mais pulverizadas: o maior detentor tem 374 mil contratos e os 20 maiores somam 2,62 milhões ([data-api holders](https://data-api.polymarket.com/holders?market=%3CconditionId%3E&limit=20)). Não há dado público sobre a nacionalidade dos operadores ([Rio Times](https://www.riotimesonline.com/brazil-election-prediction-markets-vs-polls-2026/)).

Os argumentos a favor de dar peso ao mercado são concretos. As pesquisas subestimaram a direita no 1º turno em 2018 e 2022, e os mercados acertaram em 2024 nos EUA, quando a Polymarket dava Trump 58,6% com as médias de pesquisa empatadas ([NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)). Os argumentos contra também. Polymarket, Kalshi e PredictIt estão arbitradas entre si, e por isso funcionam como **um sinal só, não três**. A base provável de operadores é estrangeira, cripto-nativa e mais à direita [inferência, sem dado direto]. Brasileiros estão formalmente excluídos. As cotações viraram peça de campanha, o que cria incentivo para movê-las. E as estatísticas de acerto citadas na imprensa (87% em 15 eleições segundo a XP; 90,6% sete dias antes segundo a própria Kalshi) medem acerto do favorito, não calibração, e vêm de partes interessadas ([Brazil Journal](https://braziljournal.com/flavio-sera-presidente-pelo-menos-segundo-a-kalshi-e-polymarket)). Não há série de preços de 2022 na API (o histórico veio vazio), então **a calibração do mercado em eleições brasileiras não pode ser medida**.

**Leitura para o modelo [calc + inferência].** O mercado pode ser decomposto. Aplicando a matriz de transferência da Quaest (§5) ao centro de válidos implícito no mercado (Lula 45,5; Flávio 42,5; outros 12), o 2º turno daria Lula ≈ 50,4% bipartidário. Para chegar a 59% de Flávio, o mercado precisa acrescentar algo além da transferência declarada: viés residual das pesquisas, abstenção diferencial ou retenção mais fraca de Lula. O tamanho desse "algo" é de cerca de 1 p.p. de margem. Isso é compatível com o erro médio de 2º turno de 2018 e 2022 (de 1 a 3 p.p., pró-PT nos institutos tradicionais) e muito menor que o erro de 1º turno daqueles anos.

---

## 3. As pesquisas das 27 UFs desenham o mapa de 2022 com swing quase nulo

### 3.1 Todas as UFs têm pesquisa recente, e a âncora uniforme é a rodada Quaest de 18–28/9

Nenhuma UF ficou sem pesquisa presidencial em setembro. A rodada Quaest/Globo cobriu 26 UFs (todas menos o PI), com entrevistas presenciais domiciliares e calibração MrP, ou seja, regressão multinível com pós-estratificação ([Band](https://www.band.com.br/politica/eleicoes/lula-x-flavio-veja-como-estao-intencoes-de-voto-para-presidente-por-estado)). O PI tem AtlasIntel. SP, RJ, MG, PE e DF têm ainda Datafolha de 28/9–1/10, e MG e RS têm Real Time Big Data. As lacunas eram o **AP**, com só o 1º turno Lula 32 x Flávio 36, sem n, registro nem 2º turno, e o **GO**, sem 2º turno publicado. *(Atualizado em 3/10: a Veritá, por URA, publicou 2º turno nas duas UFs, com campo de 26/9 a 1/10. No AP, Flávio 52,9 x Lula 43,2; em GO, Flávio 57,7 x Lula 37,1, em votos totais. Com isso, o simulador não precisa mais de prior demográfico de 2º turno em nenhuma UF.)*

| UF | Pesquisa (campo) | 1T Lula | 1T Flávio | Outros relevantes | 2T Lula x Flávio | Bipartidário Lula 2T [calc] | 2T 2022 Lula (TSE) | Swing [calc] |
|---|---|---|---|---|---|---|---|---|
| SP | Datafolha (28–30/9) / Quaest (25–28/9) | 38 / 30 | 39 / 36 | Cury 5, Caiado 4, Renan 4 | 45 x 48 / 35 x 43 | 48,4 / 44,9 | 44,76 | +1,9 |
| MG | Datafolha / RTBD / Quaest | 42 / 42 / 35 | 36 / 40 / 31 | Zema 4 | 48 x 44 / 46 x 46 / 41 x 40 | 52,2 / 50,0 / 50,6 | 50,20 | +0,7 |
| RJ | Datafolha / Quaest | 38 / 31 | 45 / 38 | – | 42 x 51 / 34 x 44 | 45,2 / 43,6 | 43,47 | +0,9 |
| BA | Quaest (20–23/9) / Atlas (24–28/9) | 58 / 57,6 | 23 / 27,8 | – | 62 x 27 / 61,3 x 31,4 | 69,7 / 66,1 | 72,12 | −4,2 |
| PR | Quaest (20–23/9) | 26 | 40 | – | 31 x 51 | 37,8 | 37,60 | +0,2 |
| RS | RTBD (24–28/9) / Quaest | 41 / 31 | 44 / 35 | – | 43 x 53 / 35 x 46 | 44,8 / 43,2 | 43,65 | +0,4 |
| PE | Datafolha / Quaest (19–22/9) | 61 / 54 | 25 / 21 | – | 65 x 29 / 58 x 25 | 69,1 / 69,9 | 66,93 | +2,6 |
| CE | Quaest | 55 | 23 | – | 59 x 27 | 68,6 | 69,97 | −1,4 |
| PA | Quaest (22–25/9) | 40 | 35 | Cury 7 | 44 x 40 | 52,4 | 54,75 | −2,4 |
| SC | Quaest | 23 | 50 | – | 24 x 60 | 28,6 | 30,73 | −2,2 |
| MA | Quaest | 59 | 22 | – | 63 x 26 | 70,8 | 71,14 | −0,3 |
| GO | Quaest (20–23/9) | 27 | 33 | **Caiado 23** | não divulgado | – | 41,29 | – |
| PB | Quaest (18–21/9) | 54 | 23 | – | 60 x 26 | 69,8 | 66,62 | +3,1 |
| ES | Quaest | 31 | 37 | – | 37 x 46 | 44,6 | 41,96 | +2,6 |
| AM | Quaest (20–23/9) | 38 | 32 | – | 45 x 40 | 52,9 | 51,10 | +1,8 |
| PI | AtlasIntel (23–28/9) | 68,5 | 24,6 | – | 70 x 26 | 72,9 | 76,86 | −3,9 |
| RN | Quaest | 52 | 25 | – | 56 x 30 | 65,1 | 65,10 | 0,0 |
| MT | Quaest | 25 | 50 | – | 30 x 56 | 34,9 | 34,92 | 0,0 |
| AL | Quaest | 44 | 32 | – | 48 x 34 | 58,5 | 58,68 | −0,1 |
| DF | Datafolha (28–30/9) / Quaest | 35 / 32 | 44 / 38 | Caiado 9 / 8 | 39 x 51 / 37 x 48 | 43,3 / 43,5 | 41,19 | +2,2 |
| MS | Quaest | 27 | 42 | – | 31 x 51 | 37,8 | 40,51 | −2,7 |
| SE | Quaest | 54 | 26 | – | 56 x 30 | 65,1 | 67,21 | −2,1 |
| RO | Quaest | 19 | 53 | – | 23 x 62 | 27,1 | 29,34 | −2,3 |
| TO | Quaest (19–22/9) | 37 | 35 | Caiado 7 | 44 x 44 | 50,0 | 51,36 | −1,4 |
| AC | Quaest (21–24/9) | 24 | 50 | – | 25 x 59 | 29,8 | 29,70 | +0,1 |
| AP | Quaest (2ª quinzena/9) | 32 | 36 | – | não testado | – | 48,64 | – |
| RR | Quaest | 20 | 59 | – | 22 x 67 | 24,7 | 23,92 | +0,8 |

Fontes: matérias do G1 de cada UF listadas nas notas ([G1 – índice de pesquisas](https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/)); BA Atlas ([O Cafezinho](https://www.ocafezinho.com/2026/09/30/pesquisa-a-tarde-aponta-lula-30-pontos-a-frente-de-flavio-bolsonaro-na-bahia)); PI ([Brasil 247](https://www.brasil247.com/nordeste/atlas-lula-tem-685-e-flavio-bolsonaro-246-no-piaui/)); RS RTBD ([CartaCapital](https://www.cartacapital.com.br/politica/pesquisa-real-time-flavio-bolsonaro-empata-com-lula-no-1o-turno-e-vence-no-2o-no-rs/)); MG RTBD ([Estado de Minas](https://www.em.com.br/politica/2026/10/7513774-real-time-big-data-lula-tem-42-e-flavio-40-em-minas.html)); AP e 2T do PA ([Band](https://www.band.com.br/politica/eleicoes/lula-x-flavio-veja-como-estao-intencoes-de-voto-para-presidente-por-estado)); 2022 de [TSE dados abertos](https://dadosabertos.tse.jus.br). Ordem por tamanho do eleitorado. O swing usa a média simples das pesquisas da UF. Há dois registros duplicados no G1 a conferir: BR-05155/2026 aparece para Quaest-SP e Quaest-MG, e BR-02676/2026 para Datafolha-SP e Datafolha-PE.

*(Atualizado em 3/10.)* Rodadas estaduais da véspera, que não estão na tabela acima mas entram no simulador (`simulador/data/pesquisas_uf.csv`): **Datafolha SP** (2–3/10) Flávio 42 x Lula 36; **Datafolha DF** (2–3/10) Flávio 47 x Lula 35, 2º turno 55 x 38; **AtlasIntel** (27/9–2/10, válidos) BA Lula 60,5 x 29,8 (2º turno 64,6 x 35,4), PI 67,9 x 27,5 (2º turno 70,6 x 29,4), PA 51,4 x 41,3; **Veritá** (26/9–1/10, totais) AC Flávio 66,6 x 25,9, AL Lula 51,2 x 39,8 (2º turno 52,4 x 41,7), AP, GO e DF (Flávio 51,0 x 39,6; 2º turno 55,3 x 41,4). O padrão de mapa de 2022 se mantém. No modelo calibrado, as UFs mais disputadas no 2º turno são PA (P(Lula) = 56%), AM (47%), TO (36%) e MG (34%); SP fica em 10% e RJ em 7% [`simulador/web/resultados.json`].

### 3.2 O que a tabela diz: mapa congelado, leve ganho de Lula no Sudeste e perda no Nordeste profundo

O resultado mais importante é estrutural. **A mediana do swing sobre 2022 é 0,0, e só 4 de 25 UFs se afastam mais de 3 p.p.** [calc]. São elas BA (−4,2), PI (−3,9), PB (+3,1) e, no limite, MS (−2,7) e PE/ES (+2,6). O sinal regional é suave: Lula ganha de 1 a 2 p.p. em SP, RJ, ES, DF e MG e perde de 2 a 4 em BA, PI, PA, SE, MS, RO e SC. Isso continua a convergência de 2018→2022 no Sudeste, mas não repete a queda do lean nordestino daquele ciclo (−4 a −8 p.p.) (§4). Ponderando as UFs pelos votos válidos do 2º turno de 2022, ajustados ao eleitorado de 2026, e imputando AP e GO com swing zero, **as pesquisas estaduais dão Lula 51,1% bipartidário (só Quaest: 50,8%)** [calc]. As nacionais davam 49,8% (49,6% com as rodadas da véspera, *atualizado em 3/10*). O mesmo cálculo aplicado ao resultado real de 2022 reproduz 50,97% (oficial: 50,90%), o que valida a ponderação. A própria Quaest nacional de 24–27/9 dá 50,0% (42 x 42), contra 50,8% na sua rodada estadual. A diferença de cerca de 1 p.p. pode vir do campo mais antigo das estaduais (18–25/9, antes de parte do movimento para Flávio), da MrP ou de ruído [inferência]. **Para o simulador, os estados devem ser ancorados nas pesquisas estaduais e recentrados no nível nacional**, e não somados como se fossem independentes. *(Atualizado em 3/10: o simulador final faz esse recentramento. As médias estaduais são deslocadas em −1,5 p.p. no 1º turno e −1,1 p.p. no 2º, para que o agregado das UFs reproduza o nacional.)*

O 1º turno mostra outro padrão. Lula lidera folgado no Nordeste. Flávio lidera folgado no Sul, no Centro-Oeste e em AC, RO e RR. **SP, MG, AM, PA, TO e AP estão apertados.** O DF também tem Flávio à frente (Datafolha 46 x 36 nos válidos) ([G1 DF](https://g1.globo.com/df/distrito-federal/eleicoes/2026/noticia/2026/10/02/datafolha-df-presidente-2-outubro.ghtml)). **GO é a única UF em que um terceiro disputa**: Caiado tinha 32% em agosto e 23% em setembro na Quaest, e o DF vem depois, com 8–9% ([G1 GO](https://g1.globo.com/go/goias/eleicoes/2026/noticia/2026/09/24/quaest-em-go-presidente-24-setembro.ghtml)). Entre agosto e setembro, Flávio ganhou de 6 a 9 p.p. no 1º turno no Norte, Centro-Oeste e Sul (AC +8, MS +9, RO +8, MT +7, GO +6), e Lula ganhou 8 na BA ([Brasil de Fato](https://www.brasildefato.com.br/2026/08/26/onde-lula-e-flavio-bolsonaro-lideram-disputa-para-presidente-veja-os-numeros-da-quaest-em-17-estados-e-no-df/)) [calc].

Há um **efeito de casa forte entre Datafolha e Quaest** nas cinco UFs em que os dois pesquisaram. O Datafolha deixa cerca de 6% em branco/nulo/indeciso. A Quaest deixa de 15% a 25%. Por isso, no Datafolha, Lula e Flávio aparecem de 5 a 8 pontos mais altos. Comparadas em votos bipartidários, as duas casas ficam a até 3,5 p.p. uma da outra em SP (48,4 contra 44,9) e a menos de 1,6 nas demais [calc]. A Quaest em SP é o ponto mais pró-Flávio entre as fontes. Nos válidos do 1º turno, o Datafolha dá **SP Flávio 41 x 40, RJ 48 x 40, MG Lula 45 x 38 e DF Flávio 46 x 36** ([G1 MG](https://g1.globo.com/mg/minas-gerais/eleicoes/2026/noticia/2026/10/02/datafolha-mg-presidente-2-outubro.ghtml); [G1 RJ](https://g1.globo.com/rj/rio-de-janeiro/eleicoes/2026/noticia/2026/10/02/datafolha-no-rj-presidencia-2-outubro.ghtml)). Não foram encontradas pesquisas presidenciais estaduais de Ipec, Futura, Vox ou Paraná Pesquisas no período. A Paraná Pesquisas publicou só governador e Senado ([Gazeta do Povo – índice](https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/)).

**Imputação [inferência].** Para o AP, o 1º turno com Flávio +4, o 2º turno de 2022 (Lula 48,6) e o AM vizinho (Lula +5) sugerem um 2º turno perto do empate, com leve vantagem de Flávio. Para o GO, sem 2º turno, o prior adequado é o 2º turno de 2022 (Lula 41,3) mais o swing do Centro-Oeste (≈ 0 a −1). A imputação deve levar em conta que os 23% de Caiado se dividem, na Quaest nacional, em 42% para Flávio, 30% para Lula e 28% para branco/nulo.

---

## 4. Vinte anos de TSE fixam o lean, o swing e a correlação entre estados

### 4.1 O lean do PT é estável desde 2006, e 2026 parte do lean de 2022 encolhido

Os votos para presidente de 2002 a 2022 foram agregados de município/zona para UF a partir dos arquivos `votacao_candidato_munzona` e `detalhe_votacao_munzona`. Os totais batem com o oficial: em 2022, 118.229.719 votos válidos no 1º turno e 118.552.353 no 2º ([TSE votacao_candidato_munzona_2022](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip); [TSE detalhe_votacao_munzona_2022](https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2022.zip)). O lean de cada UF (PT na UF menos PT nacional, no mesmo turno) é muito persistente desde o realinhamento de 2006. **A correlação do lean do 2º turno entre eleições consecutivas vai de 0,86 a 0,97, e foi de 0,97 em 2018→2022**, com inclinação de 0,84 e erro residual de 3,5 p.p. A única ruptura é 2002→2006, com correlação de 0,32 ([TSE dados abertos](https://dadosabertos.tse.jus.br)) [calc]. A dispersão entre UFs atingiu o máximo em 2018 (desvio-padrão de 17,5 p.p.) e recuou para 15,1 em 2022 [calc].

| Período (2º turno) | Correlação do lean | Inclinação | RMSE do resíduo (p.p.) |
|---|---|---|---|
| 2002→2006 | 0,32 | 0,59 | 12,8 |
| 2006→2010 | 0,93 | 0,89 | 4,9 |
| 2010→2014 | 0,86 | 0,93 | 7,0 |
| 2014→2018 | 0,96 | 1,19 | 5,1 |
| 2018→2022 | 0,97 | 0,84 | 3,5 |

Fonte: [TSE dados abertos](https://dadosabertos.tse.jus.br), cálculo próprio.

O lean de 2022 no 2º turno vai de **+26,0 no PI a −27,0 em RR**. Entre os grandes colégios, fica em SP −6,1, MG −0,7, RJ −7,4, BA +21,2, PR −13,3, RS −7,3, PE +16,0 e CE +19,1 [calc]. **MG é o pêndulo estrutural**: o lean ficou entre −3,1 e +5,2 em todas as seis eleições, e o swing relativo tem RMS de 2,6 p.p. desde 2006, o menor entre os grandes colégios. O PR (0,7) e o GO (1,4) são ainda mais estáveis. AC (10,6), SE (10,2), RJ (8,8), RR (8,5) e RN (8,2) são os mais voláteis [calc]. A regra empírica é **lean2026 ≈ 0,85 × lean2022 ± 3,5–5 p.p.** [inferência a partir da inclinação de 2018→2022]. A comparação com a §3 mostra que as pesquisas estaduais de 2026 estão dentro dessa faixa em todas as UFs, o que reforça a validade de ambos.

### 4.2 Swing pós-2006 de 6 p.p., dividido quase meio a meio entre região e UF

O swing relativo típico de uma UF no 2º turno, medido pelo RMS, é de **8,15 p.p. contando 2002→2006 e 6,18 p.p. desde 2006**. A decomposição pós-2006 dá um componente regional (média da região) de **4,55 p.p.** e um componente próprio da UF de **4,18 p.p.** O 1º turno é mais volátil (RMS de 9,57 com 2002), porque terceiros candidatos com base regional mexem no mapa: Ciro no CE, Marina no AC, Tebet no MS ([TSE dados abertos](https://dadosabertos.tse.jus.br)) [calc]. Em 2018→2022, o Nordeste perdeu de 4 a 8 p.p. de lean em todas as UFs, e SP (+6,7), RJ (+5,4), DF (+5,1) e MG (+2,4) ganharam. Esses valores são para **eleição contra eleição**. Num modelo que já usa pesquisas estaduais, eles servem como prior para UFs sem pesquisa, e não como erro da pesquisa estadual, que é menor (σ de 3 a 4 p.p. na margem, pelo briefing anterior).

### 4.3 A correlação tem blocos claros, e a matriz 27×27 bruta não deve ir para o simulador

As matrizes de correlação 27×27 do swing relativo, salvas em `correlacao_swing_uf*.csv`, mostram estrutura em blocos. **O Sul anda junto (r médio de 0,91; 0,80 pós-2006), o Nordeste anda junto (0,76; 0,40 pós-2006), e os dois andam em sentidos opostos (−0,72; −0,25 pós-2006).** O Norte acompanha o Nordeste (+0,39/+0,40), o Centro-Oeste acompanha o Sul (+0,57/+0,45), e **o Sudeste não forma bloco** (correlação interna de 0,14) ([TSE dados abertos](https://dadosabertos.tse.jus.br)) [calc]. Boa parte da força dessas correlações vem do realinhamento de 2002→2006 (NE +15,6; S −12,8). Sem ele, a correlação dentro do Nordeste cai de 0,76 para 0,40.

| Base | N–N | NE–NE | CO–CO | SE–SE | S–S | NE–S | NE–N | CO–S | NE–CO | SE–NE |
|---|---|---|---|---|---|---|---|---|---|---|
| 2º turno, 5 pares (2002–2022) | 0,24 | 0,76 | 0,27 | 0,14 | 0,91 | −0,72 | 0,39 | 0,57 | −0,55 | −0,25 |
| 1º+2º turno, 10 obs. | 0,34 | 0,57 | 0,29 | 0,01 | 0,89 | −0,60 | 0,39 | 0,61 | −0,41 | −0,16 |
| Pós-2006, 1º+2º turno, 8 obs. | 0,49 | 0,40 | 0,04 | 0,14 | 0,80 | −0,25 | 0,40 | 0,45 | −0,16 | −0,21 |

Fonte: [TSE dados abertos](https://dadosabertos.tse.jus.br), cálculo próprio (média das correlações entre pares de UFs dentro de cada bloco).

Três ressalvas definem o uso. Primeira: com 5 a 10 observações por par, o erro-padrão de cada r é de cerca de 0,5, e a matriz bruta nem é bem condicionada. Segunda: swings *relativos* somam zero por construção, então parte das correlações negativas entre regiões é mecânica. Terceira: isso mede a covariância de **swings eleitorais**, não de **erros de pesquisa**, que não puderam ser estimados por falta de um histórico de pesquisas estaduais [inferência]. A estrutura recomendada é **fatorial**: erro nacional, mais um fator "lulismo" com carga positiva em NE e N e negativa em S e CO, mais um fator regional, mais ruído da UF. Uma alternativa é encolher a matriz em direção às médias de bloco pós-2006. A correlação *total* entre UFs no simulador continua alta e positiva, porque o erro nacional domina.

### 4.4 A abstenção caiu entre turnos pela primeira vez em 2022

Até 2018, a abstenção sempre subiu do 1º para o 2º turno, com mediana por UF de +1,4 a +3,8 p.p. **Em 2022 ela caiu** de 20,95% para 20,58%, com mediana de −0,36 p.p. Caiu em SP, MG, GO, SC, PE, BA, PR, RS, RJ, CE e DF. Subiu muito no AP (19,5 → 27,2), AC (22,4 → 28,4) e RR (16,7 → 21,9), três UFs sem 2º turno para governador ([TSE dados abertos](https://dadosabertos.tse.jus.br)) [calc]. A leitura para 2026 é que a abstenção do 2º turno depende de haver 2º turno estadual e de quanto a disputa está apertada. O simulador não deve somar mecanicamente +2 p.p. em todas as UFs [inferência].

---

## 5. A transferência de 2022 foi de 70% para Bolsonaro, e a de 2026 se inclina para Flávio com muito branco/nulo

### 5.1 A contabilidade nacional de 2022 é a evidência mais robusta

Entre o 1º e o 2º turno de 2022, **Lula ganhou 3,09 milhões de votos e Bolsonaro, 7,13 milhões**. O PT ficou com só 30% do ganho líquido dos finalistas, apesar de ter terminado o 1º turno à frente. Em 2010 e 2014, essa fatia foi de 41% a 43%. Em 2018, Haddad ficou com 65%, puxado pelo voto de Ciro no Nordeste ([TSE dados abertos](https://dadosabertos.tse.jus.br)) [calc]. Em 2022, a fatia do PT por UF foi de 48% em SE e 47% no CE até **5% no AC e em RO**, 9% no MT, 14% em SC e 16% no RS [calc]. Esse número não depende de modelo, mas também não separa transferência de mudança no comparecimento.

| Ano | Ganho do PT | Ganho do oponente | Fatia do PT no ganho líquido |
|---|---|---|---|
| 2002 | +13,34 mi | +13,67 mi | 49% |
| 2006 | +11,63 mi | −2,43 mi | 126% (Alckmin perdeu votos) |
| 2010 | +8,10 mi | +10,58 mi | 43% |
| 2014 | +11,23 mi | +16,14 mi | 41% |
| 2018 | +15,70 mi | +8,52 mi | 65% |
| 2022 | +3,09 mi | +7,13 mi | 30% |

Fonte: [TSE dados abertos](https://dadosabertos.tse.jus.br), cálculo próprio.

### 5.2 A regressão ecológica e a pesquisa individual divergem, e a pesquisa deve ancorar

A regressão de Goodman sobre cerca de 5.570 municípios, ponderada pelo eleitorado e com coeficientes restritos a [0,1], dá para 2022 **Ciro → 71% Lula e 26% Bolsonaro, Tebet → 87% Bolsonaro e 13% branco/nulo**. Para 2018, dá Ciro → 85,5% Haddad ([TSE dados abertos](https://dadosabertos.tse.jus.br)) [calc]. O Datafolha de 5–7/10/2022 media coisa bem diferente: eleitores de Tebet com 31% Lula, 29% Bolsonaro e 28% branco/nulo ([Diario de Pernambuco](https://www.diariodepernambuco.com.br/noticia/politica/2022/10/bolsonaro-herda-mais-votos-de-ciro-do-que-lula-e-os-de-tebet-se-divide.html)). Os números divulgados para Ciro somam 106%, o que indica erro de transcrição ([Seu Dinheiro](https://www.seudinheiro.com/2022/politica/bolsonaro-lula-pesquisa-datafolha-segundo-turno-voto-eleicoes-ccgg/)). A divergência tem explicação conhecida. Ciro concentrou votos onde Lula já era forte (CE), e Tebet onde Bolsonaro era forte (MS, agro). A regressão de Goodman confunde esse contexto com a transferência individual e infla Ciro → Lula e Tebet → Bolsonaro [inferência]. O resultado agregado de 70% para Bolsonaro é mais compatível com Ciro dividido ou pendendo à direita do que com a taxa ecológica. **As taxas de Goodman não devem ser usadas como ponto central.** Servem só como teste de plausibilidade, por exemplo para verificar que o simulador reproduz a fatia de 30% a 45% do PT nos ciclos com centro-direita forte.

### 5.3 A matriz de 2026 segundo a Quaest e o Datafolha

A Quaest de 24–27/9 (BR-06520/2026) cruza o voto do 1º turno com o do 2º. **Zema: 81% Flávio x 9% Lula. Renan Santos: 48% x 23%. Caiado: 42% x 30%. Cury: 34% x 27%, com 38% em branco/nulo** ([Perfil Brasil](https://brasil.perfil.com/politica/quaest-flavio-bolsonaro-votos-zema-caiado-renan.phtml); [O Povo](https://www.opovo.com.br/noticias/politica/2026/09/28/quaest-1-dos-eleitores-de-cury-estao-indecisos-no-2-turno-indice-e-de-6-entre-os-de-renan.html)). O Datafolha, citado pela NextPredict, dá Caiado 50 x 33, Renan 54 x 14 e Cury 35 x 33, com 30% em branco/nulo ([NextPredict](https://nextpredict.io/market-news/politics/brazil-election-tests-prediction-markets-edge/)). Na Quaest de 3–6/9, Cury ia 46 x 24 para Flávio. A queda para 34 x 27 coincide com o encolhimento do eleitorado de Cury de cerca de 10% para 3–4%. A leitura plausível é que **os eleitores de Cury com preferência por Flávio já migraram no 1º turno** ([Revista Oeste](https://revistaoeste.com/politica/maioria-dos-eleitores-de-cury-renan-caiado-e-zema-votaria-em-flavio-no-2o-turno/)) [inferência]. As subamostras têm de 20 a 100 entrevistas. *(Atualizado em 3/10.)* A Quaest da véspera (2–3/10) traz novos cruzamentos: eleitores de Caiado vão 43% para Flávio e 19% para Lula, e os de Renan, 60% e 11% ([G1](https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/03/quaest-presidente-3-outubro.ghtml)). Os números são mais pró-Flávio que os de 24–27/9. O simulador final manteve a matriz de 24–27/9, que tem as quatro linhas completas.

| Eleitor no 1º turno | Lula | Flávio | Branco/nulo/abstenção | Fonte |
|---|---|---|---|---|
| Zema | 0,10 | 0,80 | 0,10 | Quaest 24–27/9 |
| Renan Santos | 0,25 (Datafolha 0,14) | 0,50 (Datafolha 0,54) | 0,25 | Quaest; Datafolha via NextPredict |
| Caiado | 0,30 (Datafolha 0,33) | 0,42 (Datafolha 0,50) | 0,28 | idem |
| Cury | 0,28 | 0,35 | 0,37 | idem |

**Teste de consistência [calc].** Aplicando a matriz da Quaest aos válidos do Datafolha (Lula 45, Flávio 40, Cury 4, Caiado 3, Renan 3, Zema 1), e supondo retenção total dos eleitores de Lula e de Flávio, o resultado é **Lula 47,9 x Flávio 45,0, ou 51,6% bipartidário**, igual ao 2º turno declarado pelo próprio Datafolha (48 x 45). A matriz explica, portanto, o 2º turno das pesquisas. Ela *não* explica o 59% do mercado nem a assimetria de 2022. Por isso, o simulador precisa de um parâmetro separado de **retenção diferencial e abstenção diferencial entre turnos**, com prior que inclua o caso de 2022.

---

## 6. Institutos: só a AtlasIntel documenta a ponderação, e os efeitos de casa chegam a ±5 p.p.

A AtlasIntel é o único instituto cuja metodologia de 2026 está confirmada em documento primário. Ela usa **recrutamento digital aleatório (Atlas RDR) online e pós-estratificação por sexo, idade, escolaridade, renda, região e comportamento eleitoral anterior** ([PDF Atlas/Bloomberg, jul/2026](https://static.poder360.com.br/uploads/2026/07/AtlasIntel-nacional-29jul2026.pdf)). Ponderar pelo voto passado empurra a amostra para o equilíbrio de 2022, o que é coerente com a Atlas mostrar 47,6 x 47,7 no 2º turno, enquanto os presenciais sem esse ajuste mostram Lula +3 a +4 [inferência]. Em 2022, a Atlas foi das mais próximas de Bolsonaro no 1º turno (41% dos válidos contra 43,2% reais). O Datafolha é presencial, e a rodada de véspera ouviu 4.006 pessoas num único dia ([Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-2/)). A Quaest é presencial domiciliar ([Perfil Brasil](https://brasil.perfil.com/politica/quaest-flavio-bolsonaro-votos-zema-caiado-renan.phtml)). Duas afirmações circulam só em fontes secundárias e **não foram confirmadas em documento dos institutos**: que o Datafolha não pondera formalmente por religião ([Gospel Mais](https://gospelmais.com/noticias/especialista-evangelicos-erro-datafolha-pesquisas-188660)) e que a Quaest estima os evangélicos em 31% a 36% por "correção algorítmica" ([Gazeta do Povo](https://www.gazetadopovo.com.br/vida-e-cidadania/eleitorado-evangelicos-barra-chances-esquerda-eleicoes-2026/)). Nenhum PDF do PesqEle de 2026 foi lido. A ponderação por Censo 2022, por voto de 2022 e por religião segue sem verificação para quase todos os institutos.

Os efeitos de casa foram estimados [calc] comparando cada pesquisa com campo encerrado entre 1/9 e 2/10 com a média dos *outros institutos* em ±7 dias. O cálculo usa as séries da [Wikipedia EN](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Brazilian_presidential_election). Resíduo positivo é pró-Lula.

| Instituto | Efeito 1T (p.p. de margem, totais) | n | Efeito 2T (p.p. de margem) | n | Erro de margem 2T em 2022 (briefing anterior) |
|---|---|---|---|---|---|
| CNT/MDA | +4,7 | 2 | +4,5 | 1 | +0,4 |
| Datafolha | −0,2 | 5 | **+3,2** | 5 | +2,5 |
| Nexus | +2,8 | 1 | +2,5 | 1 | – |
| Indexa | +2,8 | 1 | +1,3 | 1 | – |
| AtlasIntel | −0,4 | 4 | +0,9 | 4 | +5,0 |
| Ideia | −1,6 | 1 | +0,8 | 1 | +2,4 |
| Quaest | +1,0 | 5 | −0,4 | 5 | +1,6 |
| Real Time Big Data | +1,7 | 2 | −0,8 | 1 | – |
| PoderData | −2,9 | 5 | −0,9 | 5 | +3,6 |
| Palver | −2,7 | 1 | −2,7 | 3 | – |
| Vox | −3,6 | 1 | −3,1 | 1 | – |
| Futura | **−5,8** | 1 | **−4,8** | 3 | −2,4 |

*(Atualizado em 3/10.)* No simulador final, os efeitos de casa são estimados por um modelo hierárquico (τ = 1,5 p.p. no 1º turno), com as rodadas da véspera. Na fatia de Lula entre os dois primeiros no 1º turno: MDA +2,9; Quaest +1,3; Indexa +1,1; Datafolha +0,6; AtlasIntel +0,2; Vox −0,7; PoderData −1,1; Gerp −1,1; Veritá −1,4; Palver −1,9; Futura −1,9 (`simulador/README.md`). O modelo alternativo, com filtro de Kalman, estima no 2º turno MDA +2,8, Datafolha +0,9, AtlasIntel +0,9, Quaest +0,5, PoderData −0,3, Vox −1,3, Palver −1,3, Gerp −2,0 e Futura −2,5. Os dois métodos concordam no sinal.

Leituras com n = 1 são frágeis. O padrão robusto é a **Futura consistentemente pró-Flávio** (já em janeiro dava Flávio 48,1 x 41,9) e o **Datafolha pró-Lula no 2º turno**, cerca de +3, depois de errar +2,5 na margem do 2º turno de 2022. A Gerp **não** mudou de direção *(corrigido em 3/10)*. Esta frase dizia que a rodada final dava Lula 46 x 44 no 1º turno, mas a linha original tinha os nomes trocados. O correto é Flávio 46 x Lula 44 em válidos (43 x 41 em totais), em linha com as rodadas de dez/2025 e mar/2026 ([Exame – Gerp](https://exame.com/brasil/pesquisa-gerp-flavio-bolsonaro-tem-46-e-lula-44-dos-votos-validos-no-1o-turno/)). O simulador dá peso 0,5 a essa rodada por causa da correção. Como no briefing anterior, a correlação entre o erro de 2022 e o efeito de casa de 2026 não autoriza "corrigir" cada instituto pelo erro passado. A AtlasIntel, por exemplo, errou +5,0 na margem do 2º turno de 2022 e hoje está perto da média. A rejeição está empatada: Datafolha 45/45 (era 46/45 em março) e Quaest 54/56, na métrica "conhece e não votaria", que fica cerca de 10 p.p. acima ([Vero Notícias](https://veronoticias.com/politica/datafolha-lula-e-flavio-mantem-maior-rejeicao-com-45-cada/); [O Povo](https://www.opovo.com.br/noticias/politica/2026/09/28/rejeicao-a-lula-oscila-de-55-para-54-mostra-quaest-flavio-bolsonaro-se-mantem-em-56.html)). Na espontânea do Datafolha (Lula 39, Flávio 31, 13% de indecisos), a distância até a estimulada é de 3 pontos para Lula e de 7 para Flávio. **Flávio tem mais voto "só estimulado"**, menos cristalizado ou vindo de terceiros recentes ([Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-2/)) [inferência].

---

## 7. Bolsa Família e religião explicam quase 80% do mapa estadual

As covariáveis das 27 UFs foram baixadas direto das APIs do MDS e do IBGE e estão salvas em `demografia_uf.csv`. **Em setembro de 2026, o Bolsa Família atendia 19.295.378 famílias, com R$ 13,04 bilhões repassados e benefício médio de cerca de R$ 676** ([MDS API MiSocial](https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&wt=json&fq=anomes_s:202609&rows=6000&fl=sigla_uf,qtd_familias_beneficiarias_bolsa_familia,valor_repassado_bolsa_familia_f)). São 12,2 famílias para cada 100 eleitores no país, com variação de **3,7 em SC a 22,6 no MA** [calc]. Pelo Censo 2022, os evangélicos vão de **15,6% no PI a 44,4% no AC** ([IBGE SIDRA 9537](https://apisidra.ibge.gov.br/values/t/9537/n3/all/v/1000140/p/2022/c133/95263,95277,2836/c2/6794/c58/95253)). A renda domiciliar per capita de 2025 vai de R$ 1.231 no MA a R$ 4.401 no DF ([IBGE SIDRA 7531](https://apisidra.ibge.gov.br/values/t/7531/n3/all/v/10824/p/2024,2025/c1019/49243)). O IDHM 2024 vai de 0,745 no MA a 0,866 no DF ([PNUD Radar IDHM](https://www.undp.org/pt/brazil/publications/radar-idhm-evolucao-do-idhm-e-de-seus-componentes-periodo-de-2012-2024)).

| UF | Famílias PBF por 100 eleitores | % evangélicos | % católicos | % brancos | Renda pc 2025 (R$) | IDHM 2024 | Lean 2T 2022 |
|---|---|---|---|---|---|---|---|
| SP | 6,8 | 27,3 | 52,2 | 57,8 | 2.862 | 0,838 | −6,1 |
| MG | 8,9 | 24,8 | 63,5 | 41,1 | 2.289 | 0,809 | −0,7 |
| RJ | 11,0 | 32,0 | 38,9 | 42,0 | 2.732 | 0,819 | −7,4 |
| BA | 21,1 | 23,4 | 57,0 | 19,6 | 1.452 | 0,759 | +21,2 |
| PR | 6,6 | 26,1 | 62,9 | 64,6 | 2.687 | 0,822 | −13,3 |
| RS | 6,4 | 21,4 | 60,6 | 78,4 | 2.772 | 0,818 | −7,3 |
| PE | 20,8 | 25,2 | 58,8 | 33,6 | 1.568 | 0,754* | +16,0 |
| CE | 19,7 | 20,8 | 70,4 | 27,9 | 1.379 | 0,773 | +19,1 |
| PA | 20,4 | 35,3 | 54,4 | 19,3 | 1.435 | 0,758 | +3,8 |
| SC | 3,7 | 23,4 | 64,3 | 76,3 | 2.752 | 0,833 | −20,2 |
| MA | 22,6 | 25,4 | 64,4 | 20,1 | 1.231 | 0,745 | +20,2 |
| GO | 9,0 | 32,6 | 51,9 | 36,2 | 2.378 | 0,815 | −9,6 |
| PB | 19,4 | 20,8 | 69,0 | 35,7 | 1.542 | 0,760 | +15,7 |
| ES | 9,4 | 35,4 | 47,8 | 38,6 | 2.209 | 0,804 | −8,9 |
| AM | 22,1 | 39,4 | 47,4 | 18,4 | 1.450 | 0,767 | +0,2 |
| PI | 20,2 | 15,6 | 77,4 | 22,6 | 1.534 | 0,764 | +26,0 |
| RN | 17,9 | 21,4 | 67,0 | 39,5 | 1.779 | 0,778 | +14,2 |
| MT | 8,2 | 30,0 | 56,7 | 32,3 | 2.297 | 0,812 | −16,0 |
| AL | 20,9 | 22,9 | 64,2 | 29,3 | 1.401 | 0,746 | +7,8 |
| DF | 7,3 | 29,2 | 49,7 | 40,0 | 4.401 | 0,866 | −9,7 |
| MS | 9,4 | 32,5 | 51,9 | 42,4 | 2.369 | 0,797 | −10,4 |
| SE | 20,9 | 18,3 | 67,8 | 25,2 | 1.688 | 0,761 | +16,3 |
| RO | 10,0 | 41,1 | 40,9 | 30,7 | 1.970 | 0,786 | −21,6 |
| TO | 12,0 | 31,0 | 58,7 | 23,2 | 1.979 | 0,789* | +0,5 |
| AC | 20,7 | 44,4 | 38,9 | 21,4 | 1.372 | 0,754 | −21,2 |
| AP | 20,0 | 36,4 | 51,0 | 21,4 | 1.675 | 0,767* | −2,3 |
| RR | 19,3 | 34,4 | 37,9 | 20,6 | 1.870 | 0,780 | −27,0 |

Fontes: MDS e SIDRA citados acima; raça em [SIDRA 9605](https://apisidra.ibge.gov.br/values/t/9605/n3/all/v/1000093/p/2022/c86/2776,2777,2779,2778,2780); lean do [TSE](https://dadosabertos.tse.jus.br) [calc]. *IDHM ambíguo na fonte secundária (o de PE pode ser de 2023). A razão PBF/eleitores mede intensidade, não a fração de eleitores beneficiários.

**Regressão entre UFs [calc].** O lean de 2022 no 2º turno tem correlação de **+0,72 com a proporção de católicos, +0,62 com a cobertura do PBF, −0,66 com a de evangélicos**, −0,57 com o IDHM e −0,51 com a renda. Só a cobertura do PBF e a proporção de evangélicos explicam **R² = 0,78** do lean entre as 27 UFs (lean ≈ 15,8 + 1,39 × PBF − 1,29 × %evangélicos; RMSE 7,0 p.p.). Acrescentar a proporção de brancos leva o R² a 0,80. O maior resíduo é **RR, −25 p.p.** (o modelo prevê −1,8 e o real é −27,0). Seguem SC (−10,8), AC (−8,4), TO (+8,1) e ES (+8,0). A leitura para o simulador [inferência]: PBF e renda são quase colineares, então convém usar só uma das duas. **A religião é a covariável que separa o Norte pobre e evangélico (AC, RO, RR, AM) do Nordeste pobre e católico (PI, CE, PB, SE)**, e por isso deve carregar a correlação entre UFs dentro do fator "lulismo". O eixo explica também por que Norte e Nordeste se correlacionam só +0,39 apesar de PBF parecido. Essas são correlações ecológicas entre estados, não efeitos individuais do benefício ou da religião sobre o voto.

---

## 8. A reta final não teve debate, adiou as decisões judiciais e manteve todos os candidatos

**Debates (fato).** Não houve nenhum debate na TV aberta com os dois líderes antes do 1º turno. O pool SBT/CNN caiu no início de setembro. A Record cancelou em 23/9 o debate de 27/9 porque Lula e Flávio não iriam, e anunciou um debate de 2º turno para 11/10 ([O Tempo](https://www.otempo.com.br/eleicoes/2026/presidentes/2026/9/23/tv-record-cancela-debate-presidencial-apos-desistencia-de-lula-e-flavio-bolsonaro)). O debate da Globo de 1/10 caiu numa sequência de decisões. Em 30/9, Lula avisou que daria entrevista ao Flow Podcast no horário. A ministra Estela Aranha, do TSE, proibiu o púlpito vazio e perguntas dirigidas ao ausente. Por volta das 19h de 1/10, Flávio desistiu, alegando "censura imposta pelo TSE" (**versão** do candidato). Gilmar Mendes, do STF, mandou incluir Renan Santos. A Globo então cancelou, alegando que as intimações mudavam as regras acordadas ([CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/tv-globo-cancela-debate-presidencial/); [Correio Braziliense](https://www.correiobraziliense.com.br/mundo/2026/10/7512880-globo-cancela-debate-e-cita-decisoes-de-gilmar-mendes-do-stf-e-estela-aranha-do-tse-o-que-dizem-juristas.html)). Caiado, Cury e Zema tinham confirmado presença. "Interferência indevida" é **opinião** da Globo. A consultoria AP Exata, citada pela CNN, mediu desgaste dos dois líderes nas redes depois do cancelamento; trata-se de estudo privado sem metodologia publicada ([CNN Brasil](https://www.cnnbrasil.com.br/blogs/caio-junqueira/eleicoes/cancelamento-de-debate-afeta-imagem-de-lula-e-flavio-diz-estudo/)). O briefing anterior dizia que o TSE "suspendeu a regra do púlpito vazio". O detalhe correto é que a decisão foi de uma ministra (Estela Aranha) e que a decisão de Gilmar sobre Renan veio depois da desistência de Flávio. O horário eleitoral foi de 28/8 a 1/10 ([TSE](https://www.tse.jus.br/comunicacao/radio/2026/Setembro/calendario-eleitoral-ultimo-dia-da-propaganda-eleitoral-gratuita-e-dos-comicios)).

**Apoios e desistências (fato).** Ninguém desistiu. Em 26/9, Zema descartou a desistência ("Em hipótese alguma", disse o vice Eduardo Girão), mas **liberou os candidatos do Novo para apoiar Flávio já no 1º turno** ([CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/zema-descarta-desistencia-e-libera-candidatos-do-novo-para-apoiar-flavio/)). A Revista Oeste tinha publicado que ele estava "prestes a desistir", relato contrariado pela CNN e pelo O Antagonista ([O Antagonista](https://oantagonista.com.br/brasil/zema-descarta-desistir-e-mantem-candidatura-ao-planalto/)). Não foi encontrado apoio formal de Caiado, Cury ou Renan entre 25/9 e 3/10. Para o modelo, o voto útil à direita acontece "por baixo": a parcela de Zema deve ser parcialmente transferida, mas não zerada [inferência].

**Bets (fato e versões).** A MP 1.394/2026, de 25/9, proíbe apostas e cassinos online com vigência imediata. Os saques vão até 5/10, os sites saem do ar em 6/10 e os saldos são devolvidos de 9 a 14/10. O PL 5.477/2026 criminaliza a exploração ([Agência Senado](https://www12.senado.leg.br/noticias/materias/2026/09/28/mp-proibe-bets-e-determina-encerramento-das-operacoes-em-30-dias)). As associações do setor foram ao STF (ADI 8024, entre outras). Em 2/10, Fux deu 72 horas para AGU e governo se manifestarem, o que empurra a liminar para depois do 1º turno ([O Tempo](https://www.otempo.com.br/politica/judiciario/2026/10/2/fux-da-72-horas-ao-governo-antes-de-decidir-pedido-para-liberar-bets)). Os líderes do Congresso só tratarão a MP depois da eleição e preveem mudanças ([Metrópoles](https://www.metropoles.com/brasil/fim-das-bets-futuro-da-mp-divide-congresso-que-aguarda-passar-as-eleicoes)). Para o PL, a MP é "eleitoral" (**opinião**). Os clubes são contra; o presidente do Flamengo fala em perda de R$ 400 milhões (**versão**). Segundo a Pública, 75% dos brasileiros apoiam a proibição ([Pública](https://apublica.org/2026/09/de-apostas-predicoes-e-eleicoes/)). A pesquisa de origem desse número não foi identificada. A Polymarket mal reagiu à MP (§2.2).

**Master, Vorcaro e STF.** **Fato:** em 1/9, Mendonça retirou o sigilo de um relatório da PF com 52 mensagens que a PF atribui a uma conversa entre Vorcaro e Moraes ([Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121852/mendonca-retira-sigilo-de-apuracao-sobre-mensagens-de-vorcaro-e-moraes)). **Versão:** em ofício a Fachin, Moraes questionou se as mensagens existem ([Poder360](https://www.poder360.com.br/poder-justica/stf-aceitou-vaza-jato-mas-rejeita-chats-de-vorcaro-contra-moraes/)). **Fato:** Fachin unificou as apurações e as adiou para 22/9. Mendonça liberou o caso para o plenário, sem data marcada. Até 3/10 não havia decisão ([Terra/Estadão](https://www.terra.com.br/noticias/brasil/politica/mendonca-libera-para-julgamento-em-plenario-caso-sobre-mensagens-entre-moraes-e-vorcaro,d9c47723ddab5fd56a5074db9e55e208u5ior1i2.html)). A delação de Vorcaro, entregue em maio, não foi homologada ([Agência Brasil](https://agenciabrasil.ebc.com.br/justica/noticia/2026-05/defesa-de-vorcaro-entrega-proposta-de-delacao-pgr-e-pf)). **Fato e alegação:** em 3/9, a PGR fechou delação com Antonio Carlos Freixo Júnior, o "Mineiro", que relata repasses a pedido de Vorcaro para o filme "Dark Horse". Se parte do dinheiro foi para Eduardo Bolsonaro é **suspeita não provada** ([CNN Brasil](https://www.cnnbrasil.com.br/politica/dark-horse-pgr-fecha-delacao-com-empresario-ligado-a-fundo-nos-eua/)). Entre 25/9 e 3/10 não surgiu fato novo de peso. O risco de choque está numa decisão durante o 2º turno [inferência].

**Bolsonaro.** **Fato:** o inquérito do cartão de vacina foi arquivado a pedido da PGR em março de 2025 e pode ser reaberto. No caso das joias há indiciamento pela PF, sem denúncia nova no período ([InfoMoney](https://www.infomoney.com.br/politica/bolsonaro-soma-tres-inqueritos-abertos-na-pf-caso-do-cartao-de-vacina-foi-arquivado/)). **Projeção da imprensa:** se a Lei da Dosimetria for aplicada, a pena cai para cerca de 19 anos e 7 meses ([Metrópoles](https://www.metropoles.com/brasil/o-que-muda-com-a-lei-da-dosimetria-e-como-bolsonaro-pode-se-beneficiar)).

**Logística e ambiente (fato).** O presidente do TSE, Nunes Marques, mandou os 27 TREs acompanharem o transporte público gratuito em 4/10 e 25/10, com base na ADPF 1.013 e com frequência equivalente à de dia útil ([CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/tse-cobra-tres-sobre-transporte-publico-gratuito-nas-eleicoes/)). Em 2022, o passe livre não teve efeito significativo sobre o comparecimento, segundo o Ipea, como registrou o briefing anterior. A Lei Seca vale em todo o estado em AC, AP, AM, CE, MA, PA, PI e RR, e em parte de BA, GO, RO, SE e TO. As fontes divergem sobre o MT ([Metrópoles](https://www.metropoles.com/brasil/lei-seca-1oturno-eleicoes-2026-estados)). A Agência Pública contou 11 casos de violência política relatados por candidatos entre 12 e 28/9, um a cada 37 horas. O TSE registra 62 denúncias de violência política de gênero ([Agência Pública](https://apublica.org/2026/10/levantamento-aponta-um-caso-de-violencia-politica-a-cada-37-horas-durante-campanha-de-2026)). Não foram encontrados incidentes graves com presidenciáveis.

**Gasto digital (fato, com recortes divergentes).** No recorte do Correio Braziliense de setembro, Lula concentrou **R$ 5,2 milhões dos R$ 6,3 milhões (82,5%)** gastos em anúncios na Meta pelos presidenciáveis. Flávio gastou R$ 702 mil e Caiado R$ 222 mil ([Correio Braziliense](https://www.correiobraziliense.com.br/politica/2026/09/7509241-presidenciaveis-destinam-rs-63-milhoes-em-anuncios-nas-redes-82-sao-de-lula.html)). A Lupa classificou como irregulares, por propaganda negativa ou desinformação, R$ 460 mil (10%) dos anúncios de Lula e mais de R$ 170 mil dos de Flávio, e nenhum de Zema ou Renan. **A classificação é da Lupa** ([Agência Lupa](https://www.agencialupa.org/eleicoes/2026/10/02/candidatos-a-presidencia-gastam-mais-de-r-740-mil-em-anuncios-na-meta-que-contrariam-regras-eleitorais/)).

| Tema da reta final | Fato | Alegação | Opinião/versão |
|---|---|---|---|
| Debate Globo | Cancelado em 1/10 depois de decisões de Estela Aranha (TSE) e Gilmar Mendes (STF) e da ausência dos dois líderes | – | "Censura" (Flávio); "interferência indevida" (Globo) |
| MP das bets | Editada em 25/9; liminar e Congresso ficam para depois do 1º turno | – | "Eleitoral" (PL); "saúde pública" (governo) |
| Master/Moraes | 52 mensagens em relatório da PF; plenário sem data; delação não homologada | Conteúdo e autoria das mensagens; desvio ao fundo de Eduardo | Moraes questiona a existência das mensagens |
| Zema | Mantém a candidatura e libera o Novo para apoiar Flávio | – | "Prestes a desistir" (Revista Oeste, desmentido) |
| Mercados | Proibidos no Brasil desde abr/mai; usados por candidatos | Possível violação da lei eleitoral | Mercado como "pesquisa" (campanhas) |

---

## 9. Parâmetros atualizados para o simulador

A tabela substitui ou complementa a §5.1 do briefing anterior. "Fonte" indica número publicado ou medido diretamente; "[calc]" indica cálculo próprio sobre dados primários; "[inferência]" indica escolha do modelador. *(Atualizado em 3/10.)* A coluna "Valor final" traz o que o simulador usa na rodada de 3/10 (`simulador/premissas.json`). **Backtest** marca valor escolhido pela grade com validação deixa-uma-eleição-de-fora em 2014, 2018 e 2022 (`simulador/BACKTEST.md`).

| Parâmetro | Valor sugerido (2–3/10) | Valor final no simulador (3/10) | Origem | Base empírica |
|---|---|---|---|---|
| Média nacional 1T (totais) | Lula 41,8; Flávio 39,3; margem +2,5 | *(Corrigido em 3/10)* 14 institutos com véspera: **41,5 x 39,9**, margem +1,6. No modelo, a fatia de Lula entre os dois primeiros, com efeitos de casa, é **50,8%** | [calc] | `pesquisas_nacionais.csv`; Wikipedia PT/EN; G1 |
| Média nacional 2T | 45,5 x 45,9; bipartidário 49,8% | *(Corrigido em 3/10)* **45,5 x 46,1; 49,6%**; no modelo, **49,6%** (alternativo 49,5%) | [calc] | Idem |
| Âncora estadual 2T | Bipartidário por UF da §3, recentrado no nível nacional | Pesquisas estaduais com piso não amostral de 3 p.p. (1T) e 2 p.p. (2T), recentradas (−1,5 / −1,1 p.p.) | [calc] + **backtest** (pisos) | §3; `BACKTEST.md` |
| Prior para UFs sem 2T (AP, GO) | 2T 2022 + swing regional; AP ≈ 47–49, GO ≈ 40–42 | Desnecessário: a Veritá publicou 2º turno nas duas UFs (AP 43,2 x 52,9; GO 37,1 x 57,7) | Fonte | `pesquisas_uf.csv` |
| Lean prior (sem pesquisa) | lean2026 = 0,85 × lean2022, σ = 3,5–5 | 0,85 × lean2022 em logito, misturado ao prior demográfico no 1T (0,8/0,2); dp 7,0 p.p. (1T) e 4,5 (2T) | [calc] | TSE; `SEGMENTOS.md` |
| Swing relativo da UF | Regional N(0; 4,5) + UF N(0; 4,2) | Usado como referência do prior; na simulação, eixo 1,5 + região 3,0 + UF ≥ 3,0 p.p. | [calc] + **backtest** | §4.2 |
| Erro de pesquisa estadual (margem) | σ = 3–4 p.p., t com ν ≈ 4; ×1,5 em AP, GO e PI | Variância 1,5·p(1−p)/n + piso² (3 p.p. no 1T, 2 no 2T) × (1 + dias/14); erro da UF t (5 gl), mínimo 3 p.p. | **Backtest** | `BACKTEST.md` |
| Estrutura de correlação | Fatorial: nacional + "lulismo" + regional + UF | Igual: nacional + eixo NE/N x S/CO (dp 1,5; cargas NE 1, N 0,5, SE 0, CO −0,5, S −1) + região (dp 3,0) + UF, centrada | [calc] + **backtest** (região) | §4.3 |
| Covariáveis da correlação | %evangélicos e PBF/100 eleitores | Entram no prior demográfico por UF (`segmentos.py`), não na matriz de erros | [calc] | §7 |
| Efeitos de casa (2T) | Futura −4,8 … MDA +4,5; encolher conforme n | Hierárquicos com τ estimado (1,0 p.p. no 2T); 1º turno de MDA +2,9 a Futura −1,9 (§6) | [calc] | `simulador/README.md` |
| Viés comum da indústria, 1T | Cenário A: 0; Cenário B: anti-PT +2 a +4 p.p. | Calibrado: **+1,5 ± 1,4 p.p.** na fatia PT/adversário (prior empírico-bayesiano, τ0 = 2), × exposição por instituto (AtlasIntel 0,6); neutro 0; pleno +3,4 | **Backtest** + [inferência] | Erros de véspera +6,2 / +2,7 / +0,6 (2014/18/22) |
| Viés comum da indústria, 2T (margem) | "Pesquisas": 0; "mercado": ≈ +1 p.p. pró-Flávio | Viés das pesquisas de 2º turno −0,3 ± 0,8 p.p. (erros na véspera do 2T); a deriva até 25/10 entra como erro simétrico de dp **6,0 p.p.** na fatia de Lula | **Backtest** | `BACKTEST.md` |
| Transferência de terceiros | Zema 0,10/0,80/0,10; Renan 0,22/0,52/0,26; Caiado 0,31/0,46/0,23; Cury 0,28/0,35/0,37; α ≈ 20 | Matriz Quaest 24–27/9: Zema 0,10/0,80/0,10; Renan 0,25/0,50/0,25; Caiado 0,30/0,42/0,28; Cury 0,28/0,35/0,37; **α = 30** | Fonte + [inferência] | §5.3 |
| Retenção e abstenção diferenciais entre turnos | Parâmetro próprio; centro 0, cauda até ≈ 2 p.p. pró-Flávio | **Não implementado** como parâmetro separado. O 2º turno é 0,5 × pesquisas + 0,5 × (1º turno simulado + transferência); o comparecimento por segmento ajusta −0,25 p.p. em q na visão calibrada | [inferência] | `simulador/README.md` |
| Checagem de transferência | Fatia do PT no ganho líquido entre 30% e 45% | Mantida como checagem | [calc] | TSE 2010–2022 |
| Abstenção 1T | 20,5–21,5% nacional; por UF = 1T 2022 ± 2 | 2022 por UF e turno + ruído (dp 1,0 nacional; 1,5 por UF) | Fonte + [inferência] | TSE 2022; Kalshi ≈ 21% |
| Variação da abstenção 1T→2T | −1 a +1; AC, AP, RR +3 a +8 | Usa a abstenção do 2º turno de 2022 por UF, que já contém esse padrão | Fonte | TSE 2018 e 2022 |
| Contração da terceira via | (não estava nesta tabela) | Erro em log com média −0,25 (≈ 22%), dp 0,10 | **Backtest** | Erros −0,09 / −0,30 / −0,43 |
| Erro nacional 1T | (não estava nesta tabela) | dp 4,0 p.p. na fatia PT/adversário, t com 5 gl | **Backtest** | `BACKTEST.md` |
| P(decisão no 1º turno) – âncora externa | ≈ 5% | Modelo: 15,7% (neutro), 20,8% (calibrado), 32,0% (pleno); alternativo 36–40% | Fonte (mercado) | APIs, 3/10 |
| P(Flávio 1º no 1º turno) – âncora externa | ≈ 27–28% | Modelo: 43,7% (neutro), 65,9% (calibrado), 76,5% (pleno) | Fonte (mercado) | Polymarket e Kalshi |
| P(Flávio vence) – âncora externa | 56–60% (normalizado) | Modelo: 54,5% (neutro), **64,3% (calibrado)**, 69,6% (pleno); alternativo 50,6% / 81,1% | Fonte (mercado) | Polymarket, Kalshi, PredictIt, casas britânicas |
| Eleitorado 2026 | 157.826.587 nas 27 UFs; 158.745.463 com exterior | Igual | Fonte | [TSE perfil do eleitorado 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip) |

Para o painel, a mudança principal está nos cenários do 2º turno. O briefing anterior tratava o cenário "mercado" como +2 p.p. pró-Flávio. O valor verificado fica perto de **+1 p.p.** Com σ = 4, isso dá **P(Flávio) ≈ 60%**, e o cenário "erro igual ao do 1º turno de 2022" passa a ser uma cauda que nem o mercado precifica [calc]. *(Atualizado em 3/10.)* O simulador final não usa um cenário "mercado". Ele integra o viés do 1º turno com incerteza, e a visão calibrada (64,3% para Flávio) acabou acima do mercado (58,8%), enquanto a neutra (54,5%) ficou abaixo. Os mercados aparecem no [painel](https://claude.ai/artifact/2jH33uw8DKd8w5vbCEkwB6) só como referência externa, sem entrar no cálculo.

---

## 10. Lacunas que ainda limitam o modelo

*(Atualizada em 3/10.)* As lacunas resolvidas foram retiradas da tabela e estão listadas abaixo dela.

| Lacuna | Impacto no modelo | Onde resolver |
|---|---|---|
| AtlasIntel nacional final (BR-00999/2026: válidos Lula 47 x Flávio 44,1; 2º turno 50,1 x 49,9) publicada depois da rodada final do modelo; Veritá nacional de 26/9–2/10 e Gerp BR-08168/2026 (1–3/10) não divulgadas até cerca de 22h de 3/10 | O modelo ainda não incorpora a última AtlasIntel | Nova rodada do simulador; sites dos institutos |
| Datafolha MG de 3/10: título do G1 (41 x 41) não bate com o corpo da matéria | Uma UF-pêndulo com dado da véspera não confirmado | Relatório BR-07919/2026 |
| AP sem n na Quaest; AP e GO com 2º turno só pela Veritá (URA); PI só com AtlasIntel; 2º turno do PA só pela Band (a AtlasIntel de 27/9–2/10 trouxe só o 1º turno) | σ maior nessas UFs | G1 AP/GO; PesqEle |
| Registros duplicados no G1 (BR-05155 em SP/MG; BR-02676 em SP/PE) | Risco de deduplicação errada (a deduplicação do simulador não encontrou duplicatas no arquivo, mas o registro de SP segue marcado "conferir") | PesqEle/TSE |
| Ponderação dos institutos em 2026 (Censo 2022, voto de 2022, religião) não verificada, exceto AtlasIntel | Os efeitos de casa ficam sem explicação mecânica; a exposição ao viés só é diferente de 1 na Atlas | PDFs do PesqEle |
| Histórico de pesquisas estaduais × resultado ainda esparso (2014 sem nenhuma; 2018 quase só Ibope; 2022 quase só Ipec) | Os pisos estaduais vêm do backtest, mas com poucos institutos; a correlação de *erros* entre UFs segue como escolha do modelador | Banco do Pindograma; PesqEle 2018 e 2022 |
| Matriz 27×27 estimada com 5 a 10 observações | Por isso o simulador usa estrutura fatorial | Dados municipais ou por seção |
| Transferência ecológica só por Goodman (viés de agregação); Datafolha 2022 para Ciro soma 106% | A taxa de 2022 por candidato segue incerta | EI de King/Rosen por seção; relatório original do Datafolha |
| Não há pergunta de 2ª opção no 1º turno em 2026 | Contração da 3ª via calibrada só por 2014, 2018 e 2022 | Relatórios completos de Datafolha e Quaest |
| Não há matriz de transferência completa da AtlasIntel nem do Datafolha em 2026; Quaest da véspera só com Caiado e Renan | A matriz central depende da Quaest de 24–27/9 | Relatórios dos institutos |
| Só 3 eleições no backtest (2 no 2º turno projetado na véspera do 1º) | O viés calibrado depende muito de 2014 e 2018; a decisão no 1º turno (16–40% nos modelos, contra 5% no mercado) é sensível a uma única eleição | Não há como ampliar a amostra antes de 4/10 |
| Calibração dos mercados em eleições brasileiras (CLOB sem histórico de 2022; Betfair 403) | O peso do mercado no painel é arbitrário; ele aparece só como referência | Betfair Exchange; ElectionBettingOdds |
| Nacionalidade e identidade dos operadores | Não dá para separar informação de viés de base | Não há fonte pública |
| Mercados estaduais com volume de US$ 12 mil a US$ 93 mil | SP 97% Flávio pode ser liquidez rasa | Atualizar perto do fechamento |
| IDHM ambíguo em PE, TO e AP; PBF por UF somado a partir dos municípios | Covariáveis com pequeno erro | Painel do PNUD; release do MDS |
| Pessoas (não famílias) do PBF por idade | Exposição ao PBF por eleitor fica aproximada | CadÚnico |
| Efeito de ter 2º turno estadual sobre a abstenção não estimado | Abstenção do 2º turno por UF fica aproximada | TSE 2014–2022 com indicador de 2º turno de governador |
| Biometria, direitos de resposta da última semana, gastos no Google, conteúdo do último HGPE | Contexto | TSE; Google Ad Transparency |
| Origem do dado "75% apoiam a proibição das bets" (Pública) | Contexto | Pesquisa de origem |

**Resolvidas em 3/10:**

- **Rodadas da véspera** de Datafolha, Quaest, Futura e Palver divulgadas e incorporadas.
- **AtlasIntel "final" com números idênticos:** era a mesma rodada de 23–28/9 citada por dois veículos, e não há dupla contagem.
- **GO e AP sem 2º turno:** a Veritá publicou os dois.
- **Linha da Gerp corrigida** (nomes trocados).

---

## Conclusão

A nova evidência mostra que o ponto de discórdia é mais estreito do que parecia. Pesquisas, mercados e o histórico do TSE concordam no mapa (2022 com swing quase zero), no 1º turno (Lula à frente por 2 a 4 pontos de válidos, com cerca de 95% de chance de 2º turno) e na estrutura regional. *(Atualizado em 3/10: com as rodadas da véspera, a vantagem média de Lula no 1º turno caiu para cerca de 1,6 ponto em votos totais, e o Datafolha da véspera dá 3 pontos em válidos, 45 x 42.)* Divergem sobre cerca de **1 ponto de margem no 2º turno**. Esse ponto tem uma origem empírica identificável: a assimetria de 2022, quando Bolsonaro ficou com 70% do ganho líquido entre os turnos. A matriz de transferência declarada em 2026 não reproduz essa assimetria. O mercado, sim, a embute. Por isso, no simulador, o parâmetro que mais pesa no resultado deixa de ser o viés das pesquisas no 1º turno e passa a ser a retenção e a abstenção diferenciais entre os turnos. É uma variável que pesquisa nenhuma mede antes de 4/10 e que deve ser reestimada com os dados do 1º turno. *(Atualizado em 3/10: o simulador final não incluiu esse parâmetro separado. A deriva entre os turnos entrou como erro simétrico de dp 6 p.p., escolhido no backtest, e metade do 2º turno vem do 1º turno simulado com a matriz de transferência. Com isso, o parâmetro que mais separa as visões voltou a ser o viés do 1º turno: a visão neutra dá 54,5% a Flávio, a calibrada 64,3% e a pleno 69,6%. A recomendação de reestimar o 2º turno com o resultado do 1º continua válida.)*

Dois achados mudam o desenho do modelo. Primeiro, as pesquisas estaduais agregadas ficam cerca de 1 p.p. mais pró-Lula que as nacionais. Ou o simulador as recentra no nível nacional, ou herdará um viés que não vem de lugar nenhum. Segundo, Bolsa Família e religião explicam quase 80% do lean, e a religião distingue Norte e Nordeste. A correlação entre estados deve, portanto, ser construída sobre esses fatores, e não sobre a matriz bruta de cinco eleições. A noite de domingo testará diretamente o que nenhuma fonte resolve hoje: se a cauda de SP que o mercado precifica a 97% para Flávio é informação ou liquidez rasa. O resultado de SP no 1º turno deve ser o primeiro dado a atualizar o modelo do 2º turno.
