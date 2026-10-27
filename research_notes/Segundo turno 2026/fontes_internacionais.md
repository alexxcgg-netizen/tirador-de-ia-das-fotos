# Fontes internacionais (em inglês) sobre a eleição de 2026: acerto no 1º turno e números atuais do 2º

Coleta feita em 18/10/2026, entre 20h e 20h40 UTC (17h a 17h40 em Brasília). O 2º turno é em 25/10.
Pergunta do usuário: "um site que sempre faz pesquisa com vários dados de todo mundo de eleição; ele errou o primeiro turno
por pouco; acho que é um site que fala inglês". O usuário confirmou depois que o site é o **Global Election Simulator**
(https://globalelectionsimulator.com/). Resultado oficial do 1º turno (TSE, válidos): **Flávio 47,03 × Lula 45,16**, ou seja,
margem Lula − Flávio de **−1,87**.

## 1. Global Election Simulator (o site que o usuário procurava)

### O que é e como funciona
- Simulador em inglês para eleições de mais de 70 países, com a lei eleitoral de cada um. Autor: Leo Chang. Publicado em
  maio de 2026, com código público no GitHub (`realleochang/globalelectionsimulator`; não consegui acesso de leitura nesta
  sessão). Conta no X: @globalelectsim.
- No Brasil, a base é o resultado oficial por estado e por município (5.571 municípios e 186 consulados). O usuário mexe nos
  controles e simula a apuração.
- **Em 2026 o site publicou uma projeção.** Antes do 1º turno, era uma média de pesquisas com duas correções. Para o 2º turno,
  é um modelo de transferência de votos rodado sobre a apuração real do 1º turno.
- **O próprio site diz duas coisas que não combinam.** Na página: "These are simulations. Nothing you generate here is a real
  or predicted election result". No X, a conta publicou em 2/10 uma "**2026 Final Brazilian General Election Projection**",
  com 1,27 milhão de visualizações. A Agência Lupa (3/10) classificou como "Falta contexto" um post que tratava esses números
  como pesquisa: os resultados podem ser alterados pelo usuário e a ferramenta não é pesquisa de intenção de voto
  ([Lupa](https://www.agencialupa.org/verificacao/2026/10/03/post-divulga-simulador-eleitoral-como-pesquisa-de-intencao-de-voto/)).
  É a mesma brecha da regra nº 1, do duplo sentido: a página tem a saída de "não é previsão", enquanto a rede social vende
  "Final Projection".

### Previsão do 1º turno e quanto errou
Há **duas versões**, e a diferença importa:

| Versão | Fonte | Flávio | Lula | Margem L−F | Erro de margem (real −1,87) | Líder |
|---|---|---|---|---|---|---|
| **A**: projeção de 2/10 (média de 17 pesquisas de 15 a 24/9 + consolidação de voto útil + 3 pontos de correção para o PL) | [post no X, 2/10, 21h09 UTC](https://x.com/globalelectsim/status/2106129522605146357); repetida na autoavaliação da página | **45,4** | **44,3** | −1,1 | **+0,77** | **certo (Flávio)** |
| **B**: "no dia da eleição" (correção do PL trocada pela margem implícita no mercado Kalshi, Lula +1,5) | texto da própria página: "So the map projects Lula 45.47 and Flávio Bolsonaro 43.97" | 43,97 | 45,47 | +1,5 | **+3,37** | errado (Lula) |

- **Versão A**: Flávio 1,63 abaixo do real, Lula 0,86 abaixo, Cury +0,71, Renan +0,66, Caiado +0,02 e Zema +0,43. Erro médio
  nos 6 maiores: **0,72**. É o menor erro de margem de todas as fontes deste arquivo e a única que pôs Flávio em 1º. Isso
  combina com o "errou por pouco" do usuário: acertou o líder e errou o tamanho por menos de 1 ponto.
  O 2º turno projetado em 2/10 era **Flávio 52,0 × Lula 48,0**.
- **Versão B**: a página diz que "until the morning of the vote" a correção era de 3 pontos para o PL e que, no dia da eleição,
  ela foi recalculada para acompanhar o mercado, o que pôs Lula na frente. A seção de autoavaliação ("How the projection did")
  compara com o resultado **só a versão A** ("had the right leader"). **Não verificado**: se a versão B chegou a ficar no ar
  como número principal no dia 4. O histórico de commits resolveria isso, mas não consegui acesso. Pela regra nº 1 (brecha 8,
  reescrita posterior), o registro precisa mostrar as duas versões.

### 2º turno: números atuais (página consultada em 18/10/2026)
- **Publicado: Flávio 53,50 × Lula 46,50** (válidos): 63.101.511 × 54.824.715 votos nos 27 estados, mais 326.101 no
  exterior. **Flávio vence em 17 dos 27 estados.** **O site não publica probabilidade nem intervalo.** O "±1,2%" de um post no
  X de 14/10 (53,3 × 46,7, citado por busca e não aberto) não é um intervalo do modelo.
- **Método**: parte da apuração real do 1º turno e estima o destino dos votos dos eliminados. As taxas são a média das
  transferências de 2018 e 2022 medidas município a município, misturadas com cruzamentos de pesquisa: Nexus e Datafolha
  antes do 1º turno e Datafolha de 6 a 8/10 depois. Retenção dos finalistas: PL 1,043, PT 1,015. O efeito de cada estado é
  reduzido em 29% (r = 0,644 entre 2018 e 2022). O comparecimento é a razão 2T/1T de cada estado (Brasil 0,9912). Para quem
  votou nos eliminados, o modelo usa: Cury 55,0 F / 29,1 L / 15,9 nenhum; Renan 64,5 / 24,5 / 11,0; Caiado 56,0 / 27,9 / 16,1;
  Zema 67,8 / 18,9 / 13,3.
- **O número publicado é um "nível escolhido pelo dono"**, nas palavras da página: "That national figure is a level the owner
  set". Na mesma base, há três números diferentes:
  - o modelo sem ajuste dá **Flávio 53,09** (Lula 46,91);
  - a média das 5 pesquisas de 2º turno que o site usa (Ipespe, PoderData, AtlasIntel, Datafolha e Vox, até cerca de 9/10)
    dá **Flávio 52,02** (Lula 47,98);
  - uma correção pela relação histórica entre o erro das pesquisas no 1º e no 2º turno, medida pelo próprio site, daria
    **Flávio 52,9**.

  **O número publicado (53,50) fica acima dos três.** A página registra que o pedido inicial era 54,2 e que esse valor foi
  recusado porque nada na conta chega a 54. Pela brecha 9 (seleção), o número principal do site é uma escolha editorial que
  favorece Flávio em 0,4 ponto em relação ao modelo do próprio site e em 1,5 ponto em relação às pesquisas. Teste do espelho:
  se um site pusesse Lula acima do próprio modelo e das pesquisas, isso também seria registrado como viés de seleção.
  O site merece crédito por **publicar** isso. O desvio, porém, continua lá.
- **Estados** (Flávio, % dos válidos; arquivo `data-brazil2026Runoff` do site):
  - mais apertados: PA 49,7 (Lula), AM 51,4, AP 53,1, MG 55,6, TO 55,7, AL 44,6 (Lula);
  - Lula: PI 28,0, BA 32,6, MA 34,6, PE 34,8, SE 35,3, CE 36,1, PB 37,1, RN 39,6;
  - Flávio: RJ 59,3, SP 60,1, DF 60,3, ES 61,2, RS 63,4, MS 64,9, GO 65,1, PR 67,7, MT 70,1, AC 72,8, RO 74,1, SC 74,2, RR 76,3;
  - exterior: 50,1 Flávio.
  Também existe uma projeção por município em `https://globalelectionsimulator.com/brazil-mun-2026-r2proj.json`.

### Comparação com o modelo deste projeto (P(Lula) 15,7%; Lula 48,4%; p10–p90 46,2–50,5)
| | Lula válidos | Diferença para o modelo |
|---|---|---|
| GES publicado (nível do dono) | 46,50 | **−1,9** |
| GES, modelo sem ajuste | 46,91 | −1,5 |
| GES, média das 5 pesquisas | 47,98 | −0,4 |
| Média pós-1T (Rio Times, 12 institutos, 18/10) | 48,8 | +0,4 |

- O número publicado pelo GES (46,5) fica **perto do p10 do modelo** (46,2). Em termos do modelo, é um cenário bom para Flávio,
  mas não extremo.
- A diferença vem de **transferência e retenção**, não de pesquisas. O GES dá a Flávio 55% a 68% dos votos dos eliminados e
  retenção maior para o PL (1,043 contra 1,015). As pesquisas pós-1T (média de 51 a 52 para Flávio) e o Datafolha de 6 a 8/10
  (59 × 41 entre os eleitores dos eliminados que escolhem um dos dois) indicam menos.
- O GES não dá probabilidade. Só como ordem de grandeza: com a largura de incerteza do nosso modelo (desvio de cerca de 1,7),
  um centro de 46,5 daria a Lula de 2% a 4% de chance. **Essa conta é nossa, não do site.**
- A regra nº 5 vale para os dois lados: o GES acertou o 1º turno (versão A) **porque** corrigiu o viés das pesquisas contra a
  direita. Isso dá peso ao método de correção, não ao "nível do dono" do 2º turno, que vai além da correção que o próprio site mede.

### Resumo (Global Election Simulator)
É um simulador em inglês de eleições de mais de 70 países. A projeção de 2/10 (Flávio 45,4 × Lula 44,3) acertou o líder e errou
a margem por 0,77 ponto, o melhor resultado entre as fontes deste arquivo. Uma revisão "no dia da eleição", descrita na própria
página, punha Lula à frente (43,97 × 45,47), e a autoavaliação não a menciona. Hoje o site publica **Flávio 53,5 × Lula 46,5**,
sem probabilidade e com 17 estados para Flávio. Esse número é um nível escolhido pelo dono, acima do próprio modelo (53,09), das
pesquisas que o site usa (52,02) e da correção que ele mesmo mede (52,9). Contra o nosso modelo, o GES tem Lula 1,9 ponto abaixo.

## 2. Outras fontes em inglês: quem publicou o quê antes do 1º turno e quanto errou

Critério: fonte em inglês (ou com versão em inglês) com número nacional publicado **antes** do resultado. Todos os valores estão
em **votos válidos**. Quando a fonte só publicou votos totais, brancos e indecisos foram retirados de forma proporcional
(marcado com *). "Erro de margem" é a margem prevista Lula − Flávio menos a real (−1,87). Valor positivo quer dizer que a
fonte superestimou Lula.

| # | Fonte | Idioma | Tipo | Data | Lula | Flávio | Margem L−F | **Erro de margem** | Erro médio, 6 maiores | Pôs Flávio em 1º? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Global Election Simulator (versão A)** | EN | média de pesquisas + correções | 2/10 | 44,3 | 45,4 | −1,1 | **+0,8** | 0,72 | **sim** |
| 2 | Plano Político, modelo v1.11 | PT + EN | modelo (152 pesquisas nacionais + 410 estaduais) | 3/10 | 44,9 | 44,3 | +0,6 | **+2,5** | 0,87 | não: P(Lula 1º) = 61% |
| — | *Modelo deste projeto (referência)* | PT | modelo | 3/10 | 46,07 | 45,18 | +0,89 | *+2,76* | *0,69* | *não: P(Lula 1º) = 57%* |
| 3 | Poll+Trend ("Globe Elections UN"), projeção final | EN | agregador ponderado | 4/10 | 45,45 | 44,51 | +0,94 | **+2,8** | 0,78 | não ("Extremely Close") |
| 4 | Kalshi (mercado de margem e de 1º colocado) | EN | mercado | 4/10, 17h38 UTC | — | — | ≈ +1,3 | **≈ +3,1** | — | não: P(Lula 1º) = 71% |
| 5 | Polymarket (idem) | EN | mercado | 4/10, 17h38 UTC | — | — | ≈ +1,4 | **≈ +3,3** | — | não: P(Lula 1º) = 70% |
| 6 | Global Election Simulator (versão B, "dia da eleição") | EN | média + margem do Kalshi | 4/10 | 45,47 | 43,97 | +1,5 | **+3,4** | — | não |
| 7 | BBC/PollingData (BBC News Brasil, em português) | PT | média de pesquisas | 4/10 | 45,5* | 43,7* | +1,9 | **≈ +3,7** | — | não |
| 8 | AtlasIntel (última pesquisa, campo de 27/9 a 2/10) | EN | pesquisa (n ≈ 5.000) | 3/10 | 47,0 | 44,1 | +2,9 | **+4,8** | — | não |
| 9 | The Economist, poll tracker | EN | média de pesquisas | 3/10 | 44,4* | 41,1* | +3,3 | **≈ +5,2** | — | não |

\* Economist 40 × 37 com 10% de indecisos; BBC/PollingData 41,8 × 40,1. Os dois vêm da tabela de agregadores da Wikipedia EN
(o site do Economist deu 403). A margem implícita nos mercados usa o ponto médio de cada faixa, então é aproximada.

Fontes da tabela: Plano Político, https://planopolitico.com.br/en/modelos-eleitorais/presidencial/primeiro-turno/ (arquivo de
3/10); Poll+Trend, https://pollplustrend.com/26brfpr1; mercados, `simulador/data/mercado_ao_vivo.csv` (4/10, 17h38 UTC,
durante a votação) e APIs Gamma/Kalshi; AtlasIntel, Gazeta do Povo e `avaliacao_1t.json` (erro 4,755); Economist e
BBC/PollingData, https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Brazilian_presidential_election.

Procurei e **não encontrei** previsão ou média do 1º turno de 2026 nestas fontes: Silver Bulletin, Race to the WH, Electionista,
Morning Consult, Europe Elects/America Elects (a America Elects só repassa pesquisas soltas), Bloomberg (é contratante da
AtlasIntel, sem modelo próprio), Rio Times (só tem média de 2º turno), AS/COA e electiontracker.eu (que só reproduz preços de
mercado). A Real Time Big Data é instituto brasileiro e teve erro de margem de +6,1. O logseleicoes.joaoraul.dev processa os
logs das urnas do TSE e não faz pesquisa nem previsão.

**Poll+Trend** (https://pollplustrend.com/, "Poll+Trend by Globe Elections UN"): blog em WordPress.com de um modelador individual,
Mingeun Lee. Não encontrei vínculo com a ONU. A página se põe em 1º lugar entre 36 previsores com "0.39% Average Error", mas
essa média divide o erro por 12 candidatos, 6 deles com menos de 0,2% dos votos (brecha 4: escolha do número). Na margem, o
Poll+Trend ficou atrás do Plano Político e muito atrás do GES.

### Resumo (acerto no 1º turno)
O GES, na versão de 2/10, foi o único que pôs Flávio em 1º e o que menos errou a margem (0,8). Depois vêm Plano Político (2,5),
o modelo deste projeto (2,76), Poll+Trend (2,8), Kalshi e Polymarket (cerca de 3,1 a 3,3), a versão do GES "do dia da
eleição" (3,4), BBC/PollingData (cerca de 3,7), AtlasIntel (4,8) e Economist (cerca de 5,2). Todas as fontes que não
corrigiram o viés das pesquisas superestimaram Lula.

## 3. Números atuais do 2º turno (18/10/2026)

| Fonte | Data | Método | P(Lula) | P(Flávio) | Lula válidos | Flávio válidos | Intervalo | URL |
|---|---|---|---|---|---|---|---|---|
| **Global Election Simulator** | página de 18/10 | transferência medida (2018/2022 + cruzamentos de pesquisa) sobre a apuração do 1T; nível nacional escolhido pelo dono | não publica | não publica | **46,50** | **53,50** | não publica | https://globalelectionsimulator.com/brazil/ |
| Plano Político v2.00 | 18/10 | simulações a partir do 1T oficial, transferência e 18 pesquisas pós-1T + 143 antes; calibração pelo erro histórico | **20%** | **80%** | **48,5** | **51,5** | IC 90%: Lula 45,4–51,7 | https://planopolitico.com.br/en/modelos-eleitorais/presidencial/ |
| Polymarket (API Gamma) | 18/10, 20h13 UTC | mercado; US$ 187 mi no evento | **20,4%** (0,205; bid/ask 0,20/0,21) | **79,6%** (0,7985) | — | — | — | https://gamma-api.polymarket.com/events?slug=brazil-presidential-election |
| Kalshi (API) | 18/10, 20h13 UTC | mercado; meio do bid/ask | **20,5%** (0,20/0,21) | **79,5%** (0,79/0,80) | — | — | — | https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXBRPRES |
| Poll+Trend, Polling Follower | 18/10 | média ponderada de 13 institutos (campo de 10 a 17/10) | — | — | 49,0 (bruto 46,71) | 51,0 (bruto 48,60) | — | https://pollplustrend.com/26brpf |
| Poll+Trend, projeção R2 | 10/10, atualizada em 14/10 | agregador | — | — | 49,61 | 50,39 | — | https://pollplustrend.com/26brfpr2 |
| AtlasIntel (última nacional) | campo de 3 a 8/10 | pesquisa online, n = 5.026 | — | — | 47,2 | 52,8 | ±1 | https://atlasintel.org/poll/brazil-national-2026-10-09 |
| The Economist | 13/10 | média (via Wikipedia) | — | — | 47,8 | 52,2 | — | https://www.economist.com/interactive/2026-brazil-election-tracker |
| BBC/PollingData | 15/10 | média (via Wikipedia) | — | — | 48,7 | 51,3 | — | https://flex.pollingdata.com.br/pdvoto/2026/presidente/br/t1_lula-flavio/ |
| Rio Times | 18/10 | média simples da última pesquisa de 12 institutos | — | — | 48,8 | 51,2 | — | https://www.riotimesonline.com/brazil-runoff-polls-2026/ |

Notas:
- **GES**: a janela de pesquisas do site parou em 5 pesquisas (até cerca de 9/10). A média de 12 institutos em 18/10 está
  mais perto de Lula (48,8).
- **Plano Político tirou a Vox Brasil em 18/10** (+1 ponto de P(Flávio)). A Vox é o único instituto com Lula à frente.
  A justificativa publicada é técnica (amostra com 83,9% até 2 salários mínimos; cruzamentos idênticos entre meses diferentes),
  sem decisão judicial. Fica registrado pela brecha 9 (seleção).
- **Poll+Trend R2**: a ficha de dados da página R2 repete a da R1 (campo de 26/9 a 3/10). Não está claro se a projeção usa as
  pesquisas de depois do 1º turno.
- **AtlasIntel**: não encontrei rodada nacional depois de 9/10.

### Resumo (números atuais)
O GES é a fonte mais favorável a Flávio (Lula 46,5) e o Poll+Trend a mais favorável a Lula (49,0 a 49,6). As médias simples
ficam entre 47,8 e 48,8. Plano Político e mercados dão cerca de 80 × 20 para Flávio.

## 4. Comparação com o modelo deste projeto e com a média das pesquisas

Referências: **modelo do projeto P(Lula) 15,7%, Lula 48,4% dos válidos, p10–p90 46,2–50,5**. Média das pesquisas pós-1T ≈
**Flávio 51 × Lula 49** (Rio Times 18/10: 51,2 × 48,8).

| Fonte | Lula válidos | Diferença para o modelo (48,4) | P(Lula) | Diferença para o modelo (15,7%) |
|---|---|---|---|---|
| **Global Election Simulator** | 46,5 | **−1,9** | não publica (cerca de 2% a 4% pela nossa largura) | — |
| AtlasIntel (9/10) | 47,2 | −1,2 | — | — |
| The Economist | 47,8 | −0,6 | — | — |
| Plano Político | 48,5 | +0,1 | 20% | +4,3 |
| BBC/PollingData | 48,7 | +0,3 | — | — |
| Rio Times (12 institutos) | 48,8 | +0,4 | — | — |
| Poll+Trend (18/10) | 49,0 | +0,6 | — | — |
| Polymarket / Kalshi | — | — | 20,4% / 20,5% | +4,7 / +4,8 |

O que dá para ler:
1. **O modelo está no meio.** O GES, que acertou melhor o 1º turno, põe Lula 1,9 ponto abaixo. Plano Político e médias
   simples ficam de 0,1 a 0,6 acima. A maior distância é para o GES, e ela vem sobretudo do "nível escolhido pelo dono" e de
   transferências mais favoráveis a Flávio. O modelo sem ajuste do próprio GES (46,9) fica 1,5 abaixo do nosso.
2. **O acerto do GES no 1º turno não se transfere automaticamente para o 2º.** No 1º turno, o acerto veio de corrigir as
   pesquisas. No 2º, o próprio site mede que essa correção vale cerca de 0,9 ponto (52,9 para Flávio), e o número publicado
   vai além disso.
3. **Na probabilidade, o modelo (15,7%) fica entre o GES (implícito de 2% a 4%, conta nossa) e Plano Político e mercados
   (cerca de 20%).** Contra Plano Político e mercados, o centro é o mesmo (48,4 contra 48,5) e a diferença vem da largura do
   intervalo. Isso continua como pendência de calibração (regra nº 5): ver se o intervalo do modelo está estreito demais.
4. Teste do espelho: as duas fontes que mais se afastam do modelo saem em sentidos opostos. O Poll+Trend não corrige o viés
   das pesquisas e já superestimou Lula em 2,8 no 1º turno. O GES põe um nível acima de tudo o que mede. Nenhuma das duas
   entra como "verdade". As duas ficam como balizas de sensibilidade.

### Resumo (comparação)
O GES (Lula 46,5) é a fonte mais pró-Flávio e fica perto do p10 do modelo (46,2). As médias e o Plano Político ficam no centro
do modelo ou um pouco acima. O melhor acerto do GES no 1º turno é argumento a favor de corrigir as pesquisas, o que o modelo já
faz. Não é argumento para adotar o nível de 53,5, que o próprio site diz ser escolha do dono.

## Resumo da aba
- **O site é o Global Election Simulator** (globalelectionsimulator.com), em inglês, com mais de 70 países. A projeção de 2/10
  (Flávio 45,4 × Lula 44,3) **acertou o líder e errou a margem por 0,8 ponto**, o melhor resultado entre as fontes avaliadas.
  Uma versão "do dia da eleição" descrita na página punha Lula à frente (erro de 3,4), e a autoavaliação do site não a menciona.
- **2º turno hoje (18/10)**: **Flávio 53,5 × Lula 46,5** (17 de 27 estados), **sem probabilidade**. É um nível escolhido pelo
  dono, acima do modelo do próprio site (53,09), das pesquisas que ele usa (52,02) e da correção que ele mede (52,9).
- **Contra o modelo** (Lula 48,4; P = 15,7%): o GES fica 1,9 ponto abaixo, perto do p10 do modelo. Plano Político (48,5; 20%) e
  mercados (cerca de 20%) concordam com o centro do modelo e dão um pouco mais de chance a Lula. As médias de pesquisas ficam
  em 48,7 a 49,0.
- Ranking pelo erro de margem no 1º turno: GES-A 0,8; Plano Político 2,5; modelo do projeto 2,76; Poll+Trend 2,8; Kalshi 3,1;
  Polymarket 3,3; GES-B 3,4; BBC/PollingData 3,7; AtlasIntel 4,8; Economist 5,2.
- Números de cada fonte em `simulador/data/benchmarks_2t.csv`.
