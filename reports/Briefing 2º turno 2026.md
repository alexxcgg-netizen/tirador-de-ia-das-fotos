# Briefing do 2º turno presidencial de 2026: Lula x Flávio Bolsonaro (25/10)

*Escrito na madrugada de 5/10/2026, por volta de 02:00 UTC (23:00 de 4/10 em Brasília), poucas horas depois da
apuração do 1º turno. O texto é neutro e não recomenda candidato. Os horários estão em Brasília (UTC−3), salvo
indicação.*

**Etiquetas.** **[FATO]** é dado oficial (TSE, Diário Oficial, nota de partido) ou declaração gravada e citada
literalmente. **[DECLARAÇÃO]** é o que um candidato ou partido disse sobre si mesmo, sem verificação. **[REPORTADO]**
é informação de imprensa sem documento primário, ou com divergência entre fontes. **[ALEGAÇÃO]** é acusação sem
decisão final. **[OPINIÃO]** é avaliação de analista, veículo ou campanha. **[calc]** é conta feita para este
texto. **[inferência]** é dedução do autor. Os veículos com alinhamento editorial conhecido estão sinalizados.
*Fontes internas:* `reports/Avaliação do 1º turno 2026.md`, `research_notes/Briefing eleição 2026
complemento/segundo_turno_inicio.md`, `simulador/web/resultados_2t.json`, `modelo_alternativo/resultados_alt_2t.json`,
`simulador/AVALIACAO_1T_LICOES.md` e `simulador/BACKTEST.md`.

---

## BLUF (o essencial)

- **Flávio Bolsonaro (PL) chega ao 2º turno à frente.** Teve 47,04% dos válidos, contra 45,15% de Lula (PT). A
  diferença é de **2,25 milhões de votos (1,88 p.p.)**, com 99,97% das seções totalizadas no TSE às 22:59 de 4/10
  **[FATO]**. A totalização ainda é parcial, mas a margem não deve mudar mais que alguns centésimos.
- **Os eliminados são poucos e estão, na maioria, à direita.** Cury, Renan Santos, Caiado, Zema e mais seis
  candidatos somaram 9,3 milhões de votos (7,81%). Desse total, 0,17 p.p. foram para candidatos de esquerda
  **[calc]**. **Se só esses votos mudassem de mãos, Lula precisaria de ~62% dos que continuarem válidos**
  **[calc]**. A matriz da Quaest (2–3/10) indica ~30% **[calc]**. Lula, portanto, também precisaria ganhar votos
  entre os 33,5 milhões de abstencionistas e os 6 milhões de brancos e nulos, ou tirar eleitores de Flávio.
- **Há três leituras de modelo, e elas discordam no centro e na largura:**
  - **Simulador principal:** Lula com **47,1%** (80%: 43,8–50,5), **P(Lula) = 13%**.
  - **Modelo alternativo, só com a história 1T→2T do TSE:** perto de **50/50**, com dp de ~6 p.p. (centro de 49,8
    a 52,1 conforme a especificação; P(Lula) de 44% a 58%).
  - **Modelo alternativo, misturado com as pesquisas corrigidas:** **48,0%**, P(Lula) = 19%.
  - **Mercados** (noite de 4/10): 14–17% para Lula.

  A diferença entre as leituras está quase toda na confiança dada às pesquisas de 2º turno e às matrizes de
  transferência, contra o padrão histórico 1T→2T.
- **Apoios até agora** **[FATO/DECLARAÇÃO]**:
  - Para Flávio: Zema (Novo), Tarcísio (SP) e Cleitinho (MG).
  - Neutros: o PSD de Kassab (nota que libera os diretórios) e Cury (Avante).
  - Contra os dois: Renan Santos (Missão), que libera os eleitores.
  - Sem posição: Caiado, que vai conversar com Kassab.
  - Nenhum eliminado nem partido de centro anunciou apoio a Lula até este horário.
  - A federação União Brasil–PP se reúne em 6/10 **[REPORTADO]**.
- **Calendário apertado e cheio de fatos fora do controle das campanhas:**
  - Fim das bets: sites saem do ar em 6/10. Uma decisão de Fux (STF) está pendente.
  - A PEC do fim da escala 6x1 está pautada no plenário do Senado para 6/10 **[REPORTADO]**.
  - Propaganda na TV de 9/10 a 23/10.
  - Debates: Record em 11/10 ou 18/10 (as fontes divergem). Nenhuma presença está confirmada.
  - **Bolsa Família com piso de R$ 691 a partir de 19/10.** Só os NIS de final 1 a 5 recebem antes da votação
    **[REPORTADO, calendário da Caixa]**.
- **O que olhar primeiro: as pesquisas de 2º turno feitas depois do 1º turno**, esperadas a partir de ~9–10/10
  **[inferência]**.
  - Na véspera do 2º turno, a média delas errou +0,7, −1,1 e +0,1 p.p. em 2014, 2018 e 2022.
  - As da primeira semana ficaram a −2,7, −1,6 e +2,1 p.p. do resultado **[calc]**. A distância de três semanas
    pesa.
  - Lula entre 46% e 48% dos válidos é compatível com o modelo principal. Acima de ~49–50%, com a leitura
    histórica.

---

## 1. O 1º turno em números

### 1.1 Nacional (TSE, 99,97% das seções, 22:59 de 4/10; totalização ainda marcada como parcial)

| Candidato | Partido | Votos | % válidos |
|---|---|---|---|
| **Flávio Bolsonaro** | PL | **56.099.548** | **47,04** |
| **Lula** | PT | **53.852.447** | **45,15** |
| Augusto Cury | Avante | 3.448.112 | 2,89 |
| Renan Santos | Missão | 2.675.665 | 2,24 |
| Ronaldo Caiado | PSD | 2.604.877 | 2,18 |
| Romeu Zema | Novo | 326.470 | 0,27 |
| Samara (UP), Hertz Dias (PSTU), Edmilson Costa (PCB), Rui Costa Pimenta (PCO) | esquerda | 203.718 | 0,17 |
| Clariana Barão (DC), Wilson Grassi (Democrata) | direita | 56.917 | 0,05 |

Fonte: arquivo `br-c0001-e006257-u.json` do TSE, lido às ~02:00 UTC de 5/10 **[FATO]**. As somas por campo
ideológico são **[calc]**.

| Item | Valor |
|---|---|
| Eleitorado apto | 158.745.502 |
| Comparecimento | 125.241.177 (**78,92%**) |
| Abstenção | 33.461.357 (**21,08%**; era 20,95% em 2022) |
| Válidos | 119.267.754 (95,23%) |
| Brancos | 2.300.429 (1,84% do comparecimento) |
| Nulos | 3.672.994 (2,93%) |
| Margem Flávio − Lula | **2.247.101 votos (1,88 p.p.)** [calc] |

Em relação ao 1º turno de 2022, o candidato do PT perdeu 3,3 p.p. e o do PL ganhou 3,9 p.p. **[calc]**. Ainda não
há total oficial com 100% (situação "parcial" no arquivo do TSE). **Atenção:** um resumo da Wikipédia em português
lido na noite de 4/10 dizia que "Flávio venceu o segundo turno", o que é impossível e indica vandalismo. Não use a
Wikipédia como fonte nesta semana.

### 1.2 Mapa por região

Arquivos do TSE por UF com 97–100% totalizado em cada região; números de `Avaliação do 1º turno 2026.md` **[calc]**.

| Região | Peso nos válidos | Lula | Flávio | Margem (Lula − Flávio) | Margem no 1T de 2022 | Variação | Abstenção 2026 (2022) |
|---|---|---|---|---|---|---|---|
| Nordeste | 27,8% | 63,5 | 31,1 | **+32,5** | +39,8 | −7,3 | 18,4% (19,5%) |
| Norte | 8,5% | 44,3 | 49,5 | −5,2 | +1,6 | −6,8 | 19,5% (20,9%) |
| Sudeste | 40,8% | 39,6 | 51,4 | **−11,8** | −4,9 | −6,9 | 22,7% (22,0%) |
| Centro-Oeste | 7,7% | 32,6 | 56,5 | −23,9 | −15,9 | −8,0 | 21,7% (21,3%) |
| Sul | 14,9% | 31,3 | 60,1 | **−28,8** | −17,8 | −11,0 | 20,5% (19,3%) |

- **Lula venceu em 12 UFs** (as 9 do Nordeste, PA, AM e AP; no AP, por 225 votos) e no exterior. **Flávio venceu
  em 15**, entre elas SP (−13,7 na margem de Lula), MG (−5,4; Lula tinha vencido em 2022) e RJ (−13,6) **[calc]**.
- A polarização regional aumentou. A distância entre Nordeste e Sul passou de 57,6 para 61,3 p.p. **[calc]**.
- **O comparecimento mudou de lugar.** A abstenção caiu no Nordeste (−1,2 p.p.) e no Norte (−1,5) e subiu no Sul
  (+1,1) e no Sudeste (+0,7). No total ficou quase igual a 2022 **[calc]**.

---

## 2. A aritmética do 2º turno

### 2.1 Onde estão os votos em disputa

| Reservatório | Votos (milhões) | Observação |
|---|---|---|
| Eleitores dos eliminados | **9,32** | Cury 3,45; Renan 2,68; Caiado 2,60; Zema 0,33; demais 0,26 |
| Brancos + nulos | 5,97 | 4,77% do comparecimento |
| Abstenção | 33,46 | 21,08% do eleitorado |
| Eleitores de Flávio e de Lula que podem mudar de voto | – | Cada troca direta vale 2 votos na margem |

**O que cada lado precisa** **[calc]**. Com o mesmo número de válidos do 1º turno (119,3 milhões), a maioria
absoluta é de 59,63 milhões de votos:

- **Flávio precisa de +3,53 milhões.** Isso equivale a 38% dos 9,32 milhões dos eliminados, se todos eles votarem
  de novo.
- **Lula precisa de +5,78 milhões.** Isso equivale a 62% dos votos dos eliminados, ou a outra combinação de
  abstencionistas, brancos e nulos e eleitores de Flávio.
- **Regra geral:** se G for o ganho líquido total dos dois entre os turnos, Lula precisa de uma fração
  s ≥ (G + 2,25 mi)/(2G) desse ganho. Com G = 9,3 milhões, s é 62%. Com G = 12 milhões, por exemplo com
  abstenção menor, s cai para 59%.

### 2.2 Para onde vão os eliminados: o que dizem as pesquisas

Matriz da Quaest usada no simulador **[FATO sobre a pesquisa; subamostras pequenas]**: Caiado e Renan de 2–3/10,
Cury e Zema de 24–27/9.

| Eleitor de… | → Lula | → Flávio | → branco/nulo/abstenção |
|---|---|---|---|
| Cury (2,89%) | 28% | 35% | 37% |
| Renan Santos (2,24%) | 11% | 60% | 29% |
| Caiado (2,18%) | 19% | 43% | 38% |
| Zema (0,27%) | 10% | 80% | 10% |
| Demais (0,22%) | 30% | 30% | 40% (inferência neutra do modelo) |

Aplicada aos votos reais, a matriz dá **+1,87 milhão para Lula e +4,27 milhões para Flávio**. Lula chegaria a
~48,0% dos válidos e a margem a favor de Flávio subiria para ~4,6 milhões (`fluxo_eliminados` em
`resultados_2t.json`) **[calc]**. Entre os votos dos eliminados que continuam válidos, ~30% vão para Lula.

**Cautela:** são subamostras de poucas centenas de entrevistas, colhidas antes de os apoios serem anunciados. O
eleitor de **Cury é o menos definido**: 37% sem candidato e divisão quase igual entre os dois. Ele é o maior bloco
(3,45 milhões), e Cury declarou silêncio total.

### 2.3 O que aconteceu nos últimos três 2º turnos

`resultados_2t.json` (`historico_turnos`, `ecologico`), dados do TSE **[FATO; diferenças em calc]**.

| Ano | PT 1T → 2T (% válidos) | Adversário 1T → 2T | Ganho de votos PT / adversário | Fração do ganho líquido que foi ao PT | Quem eram os eliminados (e para onde foram os apoios) |
|---|---|---|---|---|---|
| 2014 | 41,6 → **51,6** | Aécio 33,6 → 48,4 | +11,2 mi / +16,1 mi | **41%** | Marina (21%), de centro-esquerda, apoiou Aécio |
| 2018 | 29,3 → 44,9 | Bolsonaro 46,0 → **55,1** | +15,7 mi / +8,5 mi | **65%** | Ciro (12,5%; "apoio crítico" do PDT a Haddad, sem campanha de Ciro), Alckmin (4,8%) e outros |
| 2022 | 48,4 → **50,9** | Bolsonaro 43,2 → 49,1 | +3,1 mi / +7,1 mi | **30%** | Tebet (4,2%) e Ciro (3,0%), de centro e centro-esquerda; Tebet apoiou Lula |

Leitura **[inferência]**:

- Em 2022 os eliminados eram de centro e centro-esquerda, e a principal deles declarou apoio ao PT. Mesmo assim, o
  adversário ficou com 70% do ganho líquido.
- Em 2026 os eliminados são de centro-direita e de direita, e nenhum apoiou Lula. A fração de que Lula precisa
  (~59–62%) só foi atingida em 2018, quando o PT estava 17 p.p. atrás e havia um grande bloco de centro-esquerda
  para captar.
- O ganho líquido mistura transferência, entrada e saída de abstencionistas e troca direta de voto. Não é uma
  medida pura de transferência.

### 2.4 Ideologia dos eliminados

Base: planos registrados e declarações (`Propostas e viabilidade dos candidatos.md`) **[FATO/DECLARAÇÃO]**.

- **Caiado** (PSD; vice Kassab): centro-direita e direita. Agenda penal dura (pena mínima de 45 anos para facção,
  maioridade aos 16 anos para crimes graves) e contenção fiscal. Antes do 1º turno disse: "em nenhuma hipótese,
  em nenhum cenário, em nenhum turno, estarei ao lado de Lula ou do PT" (15/8, [Metrópoles](https://www.metropoles.com/brasil/caiado-descarta-apoio-a-lula-no-2o-turno-apos-fala-de-kassab)).
  Também chamou votar em qualquer dos dois de "jogar caça-níquel" (23/9).
- **Zema** (Novo): direita liberal. Propõe privatizar todas as estatais e sair do BRICS. Já tinha liberado os
  candidatos do Novo para apoiar Flávio no 1º turno.
- **Renan Santos** (Missão, egresso do MBL): direita antissistema e contra os dois. Propõe desindexação,
  megapresídios e o fim do Bolsa Família como está. "Não votar em bandido" foi a frase com que negou apoio aos
  dois (28/9).
- **Cury** (Avante): centro difuso, sem eixo ideológico claro (semipresidencialismo, "gestão das emoções",
  crédito barato). É o eleitorado mais aberto.
- **Micropartidos:** a esquerda (UP, PSTU, PCB, PCO) somou 0,17%. A direita (DC, Democrata), 0,05% **[calc]**.

### 2.5 Comparecimento

Nas três últimas eleições, a abstenção variou −0,4 a +1,7 p.p. entre os turnos (2014: 19,4 → 21,1; 2018: 20,3 →
21,3; 2022: 20,95 → 20,6) **[FATO]**. O simulador projeta 21,9% para 2026 (80%: 20,5–23,2). Repetir no 2º turno a
alta de comparecimento do Nordeste e do Norte é o caminho mais citado para Lula. Uma mobilização maior no Sul e no
Sudeste joga a favor de Flávio. No backtest, o efeito partidário da variação de comparecimento foi pequeno: no
máximo 0,25 p.p. no nacional (`BACKTEST.md`).

---

## 3. As três leituras de modelo e por que divergem

| Leitura | Lula (% válidos) | Intervalo de 80% | P(Lula vence) | Base |
|---|---|---|---|---|
| **Simulador principal** (`simulador/web/resultados_2t.json`, 01:55 UTC de 5/10) | **47,14** | 43,8 – 50,5 | **13,0%** | 1º turno real + matriz Quaest regionalizada + pesquisas de 2º turno feitas antes do 1º turno, corrigidas pelo erro de cada instituto (peso 0,25) + viés histórico 1T→2T |
| **Alternativo: só regressão 1T→2T** (`modelo_alternativo/resultados_alt_2t.json`) | 52,1 (mediana 51,2); de 49,8 a 52,1 conforme a especificação | 44,5 – 61,0 | 44% a 58% | Só o mapa do 1º turno e a relação histórica 1T→2T por UF (2002–2022). Sem pesquisas |
| **Alternativo: regressão + pesquisas corrigidas** | **48,0** | 45,7 – 50,8 | **19%** | Mistura por inverso da variância; as pesquisas recebem peso 0,91 |
| (Alternativo: só pesquisas corrigidas) | 47,6 | 45,1 – 50,2 | 12% | 14 institutos; média bruta 49,6–50,0, corrigida 47,6 |
| (Ingênuo: 2T = fatia de Lula entre os dois no 1T) | 49,0 | – | – | Referência |
| Mercados (Polymarket / Kalshi, 21:05 de 4/10) | – | – | 14% / 17% | Arbitrados entre si: valem como um sinal só |

### 3.1 Como se forma o centro do simulador principal [calc, do JSON]

1. **Transferência:** 1º turno real + matriz da Quaest, regionalizada pelo lean da UF. Resultado: **47,98%**.
2. **Pesquisas de 2º turno feitas antes do 1º turno:** a média bruta de 49,59% cai para **47,67%** depois de
   corrigir cada instituto pelo próprio erro no 1º turno. Na média, a indústria superestimou a fatia de Lula em
   +1,95 p.p.
3. **Mistura com peso 0,25** para as pesquisas: 47,91%.
4. **Viés histórico do método** (média de 2014–2022, encolhida, condicionada ao erro do 1º turno de 2026):
   −0,78 p.p. Centro final: **47,13%**.

**Sensibilidade:**
- Sem a correção por instituto, o centro seria 47,26% (P = 14,6%).
- Com a correção relativa, 47,50% (P = 16,3%).
- Com uma matriz nacional única no lugar da regionalizada, P = 12,8%.
- Erros do mesmo pipeline no backtest leave-one-election-out: +2,3, −1,9 e +1,6 p.p. em 2014, 2018 e 2022.

### 3.2 Por que a regressão histórica dá ~50/50

- A regressão por UF (`logit y = 0,173 + 0,794·logit x − 0,771·t`) diz que o 2º turno puxa as UFs para 50% e que
  terceiros grandes historicamente prejudicaram o PT. Em 2026 os terceiros somam só 7,8%, então quase todo o
  intercepto positivo entra. Esse intercepto se apoia muito em 2006.
- **A regressão não enxerga ideologia.** Na série histórica, os terceiros relevantes eram de centro-esquerda
  (Marina, Ciro, Heloísa Helena, Tebet). Em 2026 são de centro-direita e de direita. Isso provavelmente favorece
  Lula indevidamente nessa leitura (README do modelo alternativo).
- **Desempenho fraco no backtest.** O RMSE nacional fora da amostra foi de 5,9 p.p. em 2006–2022, pior que o
  ingênuo (4,7). Só 2 de 5 anos ficaram dentro do intervalo de 80%. A transição 1T→2T no Brasil variou de −5 a
  +7 p.p. para o PT.

### 3.3 Onde está a discordância

**[inferência, apoiada nos dois READMEs]**

- **A vantagem de Flávio não vem do mapa do 1º turno.** Uma liderança de 1,9 p.p. já se reverteu e já se ampliou
  no histórico. Ela vem das **pesquisas de 2º turno**, mesmo corrigidas, e da **matriz de transferência**.
- **Quem confia nas pesquisas corrigidas e na Quaest fica com ~47–48% e P de 12–19%.** Quem confia só na relação
  histórica fica perto de 50/50, com incerteza muito maior.
- **Argumentos a favor da leitura com pesquisas:** a correção por instituto reduziu o erro das pesquisas de 2º
  turno feitas antes do 1º turno de +3,5/+4,7 para +2,0/+2,0 p.p. em 2018 e 2022. A ideologia dos eliminados também
  aponta para Flávio.
- **Argumentos contra:** são só dois anos de teste. Mesmo corrigida, a média ainda superestimou o PT nesses dois
  anos. A matriz vem de uma pesquisa só. E faltam três semanas de campanha, com uma deriva entre turnos que o
  histórico mostra ser grande (2014: Aécio à frente na primeira semana e Dilma vencendo).
- **Erro do 1º turno de 2026:** a visão calibrada do modelo principal errou a margem em −0,5 p.p., e a média
  simples das pesquisas errou em +3,4 p.p. a favor de Lula. Isso é uma única realização e não prova que a correção
  acerta no 2º turno.

---

## 4. Calendário até 25/10

| Data | Evento | Status |
|---|---|---|
| **Seg 5/10** | Campanhas recomeçam ("a partir de amanhã a gente começa uma nova campanha", Lula). B3 e câmbio abrem: **primeira reação do mercado ao resultado**. Último dia para sacar saldos das bets (23:59). Prazo de 72h da AGU para responder a Fux (pedido de 2/10) vence por volta desta data | [FATO] saque e prazo ([Agência Brasil, 2/10](https://agenciabrasil.ebc.com.br/justica/noticia/2026-10/fux-pede-manifestacao-da-agu-sobre-pedido-para-liberar-bets)) |
| **Ter 6/10** | Sites e aplicativos de bets saem do ar (MP 1.394). **Plenário do Senado: PEC 221/2019 (fim da escala 6x1)**, que precisa de 49 votos em dois turnos. Reunião da federação União Brasil–PP sobre o apoio no 2º turno | [REPORTADO] Senado ([Imirante, 2/10](https://m.imirante.com/noticias/brasil/2026/10/02/ipolitica-presidente-do-senado-marca-votacao-do-fim-da-escala-6x1); outra fonte fala em votação em 5/10). Federação ([ParaíbaOnline citando a Folha, 27/9](https://paraibaonline.com.br/eleicoes/2026/09/27/pp-e-uniao-brasil-impoem-condicao-para-apoiar-flavio-bolsonaro-no-2o-turno/)) |
| 7–8/10 | Operadoras de bets informam os saldos remanescentes por CPF | [REPORTADO] |
| a definir | Decisão de Fux sobre a suspensão da MP das bets (ANJL/IBJR) | [FATO] pendente |
| **Sex 9/10** | Começo do horário eleitoral gratuito do 2º turno (regra: "sexta-feira seguinte ao 1º turno" até a antevéspera) | [FATO] Lei 9.504/97, art. 49; datas [calc] |
| ~9–10/10 em diante | Primeiras pesquisas nacionais de 2º turno feitas depois do 1º turno (registro no TSE 5 dias antes da divulgação) | [inferência]; nenhuma registrada foi localizada até 5/10 de madrugada |
| **Dom 11/10** ou **Dom 18/10** | Debate da Record. O Tempo e a Gazeta do Povo (23/9) falam em 11/10; Ranking dos Políticos (22/8) e Congresso em Foco (10/8) falam em 18/10 | [REPORTADO, divergente]; presença não confirmada |
| 12/10 | Feriado de N. Sra. Aparecida. No 1º turno houve conteúdo falso sobre Flávio e a padroeira, cuja remoção o TSE confirmou por 7 x 0 | [FATO] |
| 12/10 ou 19/10 | Debate do consórcio CNN/SBT/RedeTV! e outras emissoras | [REPORTADO, 10/8] |
| a definir | Debate Band/Cultura (parceria renovada para o 2º turno) e Globo (limite: sexta 23/10) | [REPORTADO] / [NÃO ENCONTRADO] |
| **Seg 19/10** | **Bolsa Família com piso de R$ 691 (+15,04%)**: NIS final 1 recebe em 19/10, final 2 em 20/10 e assim por diante até o final 5 em 23/10. Finais 6 a 0 recebem a partir de 26/10, depois da votação | [REPORTADO] calendário divulgado ([NSC Total](https://www.nsctotal.com.br/economia/bolsa-familia-novo-piso-691-outubro-2026-datas); [Mixvale, 4/10](https://www.mixvale.com.br/2026/10/04/caixa-libera-repasse-do-bolsa-familia-de-r-691-a-partir-do-dia-19/)) |
| 20/10 | A partir desta data, eleitores não podem ser presos, salvo em flagrante (5 dias antes) | [FATO] Código Eleitoral, art. 236 |
| 22/10 | Começa a quarentena de conteúdo sintético (72h antes da votação), pela Res. TSE 23.755/2026 | [FATO] |
| **Sex 23/10** | Último dia de horário eleitoral e de debates | [FATO] regra; [calc] data |
| **Dom 25/10** | **2º turno**, também para governador em AC, AM, DF, ES, RJ, RN e TO | [FATO] |
| 26/10 | Termina a subvenção ao diesel, estendida por portaria (segundo a Gazeta do Povo, veículo crítico ao governo) | [REPORTADO] |

---

## 5. O que cada campanha diz que vai enfatizar

As frases entre aspas são das próprias campanhas **[DECLARAÇÃO]**. As descrições de estratégia sem aspas são da
imprensa **[REPORTADO]**.

### Lula (PT)

- **Discurso de 4/10, ~22h** ([Revista Fórum, à esquerda](https://revistaforum.com.br/politica/lula-discurso-1o-turno/);
  [O Tempo](https://www.otempo.com.br/eleicoes/2026/presidentes/2026/10/4/lula-diz-que-esperava-vitoria-no-1-turno-mas-que-agora-comeca-nova-campanha);
  [NC News](https://ncnews.com.br/2026/10/04/flavio-fim-era-pt-lula-nova-campanha-segundo-turno-2026/)):
  - Sobre o resultado: "Eu confesso que estava convencido de que eu ia ganhar as eleições no primeiro turno."
  - Sobre o 2º turno: "A partir de amanhã a gente começa uma nova campanha. A gente vai poder mostrar a diferença
    entre as propostas." "Sou muito bom no mata-mata."
  - Ataque ao adversário: "É uma biografia tenebrosa. Com ligações tenebrosas, com suspeitas gravíssimas, com
    relação com os milicianos e o crime organizado", "com a participação na criação do Banco Master". Isso é
    **[ALEGAÇÃO]**. Não há condenação de Flávio. Há inquérito no STF sobre o financiamento do filme "Dark Horse"
    (ver §6).
  - Mobilização: "o voto é necessário para definir o futuro do país."
- **Estratégia descrita pela imprensa** ([O Tempo, 4/10, 21:07](https://www.otempo.com.br/eleicoes/2026/presidentes/2026/10/4/lula-tentara-desconstruir-flavio-no-segundo-turno-senador-buscara-apoios-na-direita)):
  - "desconstrução" de Flávio;
  - desmobilizar os eleitores dos eliminados que tendem a votar nele;
  - ampliar propostas em **segurança pública** e uma **reforma do Judiciário**, temas de centro.
- **Agenda já em curso:** a imprensa também aponta comparação com o governo Bolsonaro, justiça tributária (isenção
  do IR até R$ 5 mil) e fim da escala 6x1 **[REPORTADO; data da matéria não verificada]**. No plano registrado
  estão a 6x1, a ampliação do Bolsa Família, o ganho real do mínimo e o arcabouço fiscal.

### Flávio Bolsonaro (PL)

- **Declaração de 4/10** ([NC News, 22:07](https://ncnews.com.br/2026/10/04/flavio-fim-era-pt-lula-nova-campanha-segundo-turno-2026/)):
  disse estar "muito feliz", vê uma "possibilidade real" de vitória e chamou o resultado de "fim da era do PT".
  Repetiu a proposta de **acabar com a reeleição**.
- **Estratégia descrita pela imprensa** (O Tempo, 4/10): primeiro, reunir os apoios à direita (Caiado, Cury, Zema)
  para captar a maior parte do voto desses candidatos. Ele também negociou com Ciro Nogueira (PP) e Antônio Rueda
  (União) **[REPORTADO]**. Segundo a Folha, citada pela ParaíbaOnline, as condições da federação seriam espaço no
  governo e a permanência de Davi Alcolumbre na presidência do Senado.
- **Temas já usados na campanha:**
  - o STF: "Quem vota em Lula está votando em Alexandre de Moraes", ato de 7/9, citado pela
    [Gazeta do Povo, centro-direita](https://www.gazetadopovo.com.br/eleicoes/2026/lula-sai-atras-de-flavio-e-sem-apoios-expressivos-na-disputa-de-segundo-turno/);
  - a "censura" do TSE, motivo alegado para desistir do debate da Globo em 1/10;
  - o INSS e Lulinha;
  - segurança dura e o "tesouraço" fiscal (plano registrado).
- **Aliados:**
  - Tarcísio (SP, reeleito com 62,65%): "Agora São Paulo vai ser decisivo para eleger Flávio Bolsonaro no segundo
    turno". Diz que fará campanha fora de SP ([CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/tarcisio-agradece-bolsonaro-e-diz-que-sp-sera-decisivo-para-flavio/)).
  - Cleitinho (MG): "Eu já ia apoiar o Flávio" ([O Tempo](https://www.otempo.com.br/eleicoes/2026/governadores/2026/10/4/apos-eleicao-para-governo-de-minas-cleitinho-declara-apoio-a-flavio-bolsonaro-no-2-turno)).

### Quadro de apoios (até ~02:00 UTC de 5/10)

| Ator | Posição | Status |
|---|---|---|
| Zema / Novo | Apoia Flávio ("Onde estiver PT, nós estaremos contra") | [FATO] declaração ([O Tempo, 4/10](https://www.otempo.com.br/eleicoes/2026/presidentes/2026/10/4/zema-indica-apoio-a-flavio-bolsonaro-no-segundo-turno-da-eleicao-presidencial)); nota formal do Novo não localizada |
| PSD (Kassab) | **Neutro**; libera diretórios, parlamentares e filiados | [FATO] nota ([Metrópoles, 4/10](https://www.metropoles.com/brasil/psd-declara-neutralidade-no-2o-turno-das-eleicoes-presidenciais); [CNN Brasil](https://www.cnnbrasil.com.br/politica/psd-mantem-neutralidade-e-libera-diretorios-para-apoio-em-disputa-presidencial/)) |
| Caiado | Ainda sem posição: "jamais vou me pronunciar sem antes estar reunido com o presidente do meu partido". Antes do 1º turno, havia descartado Lula "em nenhum cenário" | [REPORTADO] ([Transmissão Política, 4/10](https://transmissaopolitica.com.br/politica-nacional/2026/10/04/psd-segundo-turno-kassab-caiado/)) |
| Cury / Avante | Neutro ("Eu me silencio completamente"). Proíbe o uso do seu nome e diz que vai deixar a política | [FATO] declaração ([CNN Brasil, 4/10](https://www.cnnbrasil.com.br/eleicoes/cury-diz-que-nao-vai-apoiar-ninguem-no-2-turno-me-silencio/)) |
| Renan Santos / Missão | Não apoia nenhum dos dois ("façam o que quiserem"). O boato de apoio a Lula foi desmentido | [REPORTADO] ([BP Money](https://bpmoney.com.br/noticias/renan-santos-descarta-apoio-a-lula-e-flavio-apos-1o-turno-facam-o-que-quiserem/); [Boatos.org](https://www.boatos.org/politica/renan-santos-declarou-apoio-a-lula-no-2o-turno-das-eleicoes-de-2026.html)) |
| União Brasil + PP (federação) | Neutros no 1º turno. Decisão marcada para 6/10. A Revista Oeste (à direita) noticiou que o União "decidiu apoiar Flávio" | [REPORTADO]; página da Oeste inacessível (403) |
| MDB, Republicanos | Neutros no 1º turno. Posição no 2º turno não localizada (Tarcísio e Cleitinho, do Republicanos, apoiam Flávio individualmente) | [NÃO ENCONTRADO] |
| Renan Calheiros (MDB-AL) | Antes do 1º turno, disse esperar Lula "fortalecido". Nenhuma declaração depois do 1º turno foi localizada | [REPORTADO] ([GazetaWeb](https://www.gazetaweb.com/noticias/eleicoes/renan-calheiros-espera-lula-como-o-mais-votado-e-fortalecido-para-o-segundo-turno-940075)) |
| Governadores do PT (BA, CE, PI) e do PL (PR, RS, SC, RO, RR) | Alinhamento partidário presumido; sem declaração depois do 1º turno | [NÃO ENCONTRADO] |
| Raquel Lyra (PE, PSD), Eduardo Leite (RS, PSD), Gladson Cameli (AC, PP) | Sem sinalização | [REPORTADO] ([Poder360](https://www.poder360.com.br/poder-eleicoes/lula-tem-mais-apoio-de-governadores-no-1o-turno-flavio-vira-no-2o/)) |

Panorama do Poder360 **[REPORTADO]**: no 1º turno, Lula tinha 12 governadores, com 53 milhões de eleitores, e
Flávio 5, com 57,3 milhões. No 2º turno, Flávio tende a chegar a 13. Antes do 1º turno, Kassab chegou a ser citado
dizendo que o Centrão estava com Lula, e depois negou ter falado em apoio a Lula
([CNN Brasil](https://www.cnnbrasil.com.br/eleicoes/kassab-afirma-que-nunca-falou-de-apoio-a-lula-em-eventual-2o-turno-2/)).
A versão é contestada.

---

## 6. Riscos e coringas

A mesma régua vale para os dois lados. Nenhum item tem efeito medido. A direção e o tamanho são incertos
**[inferência]**, salvo indicação.

### 6.1 Fatores que podem pesar contra Lula

| Fator | Natureza | Observação |
|---|---|---|
| Distância de 2,25 milhões de votos e uma matriz de transferência desfavorável (~30% dos eliminados que continuam válidos) | [FATO] / [calc] | Exige uma virada fora do padrão de 2014 e 2022 |
| Perda de palanques estaduais: SP (Tarcísio), MG (Cleitinho), PR, SC e RS com governadores do PL; PSD neutro | [FATO] | Lula venceu MG em 2022 e perdeu por 5,4 p.p. em 2026 |
| **Bets:** se Fux suspender a MP, a medida-símbolo cai. A frase "eu não sabia" (Flow, 1/10) contrasta com a lei sancionada pelo próprio governo em 2023 | [FATO] registro / [OPINIÃO] crítica de oportunismo eleitoral | A primeira Quaest depois do anúncio não mostrou efeito: rejeição de 55% para 54% |
| **INSS / Lulinha:** a PF informou ao STF que vai investigar a relação de Fábio Luís com o "Careca do INSS". O inquérito trata de tráfico de influência, não de autoria da fraude | [ALEGAÇÃO]; não há denúncia | A investigação está travada por falta de efetivo, segundo a Gazeta do Povo. A defesa pede arquivamento (CartaCapital) |
| **Reajuste do Bolsa Família às vésperas do pleito:** a crítica de uso eleitoral e uma ação contra o reajuste continuam pendentes | [FATO] calendário / [OPINIÃO] crítica | O desfecho judicial não foi localizado |
| **PEC da 6x1 no Senado:** se for derrotada ou adiada, perde força uma bandeira da campanha | [REPORTADO] pauta de 6/10 | Precisa de 49 votos. Em setembro a base contava 53–54 |
| Rejeição alta: Lula com 54% (Quaest, fim de setembro) | [FATO] pesquisa | Flávio tinha 56% na mesma rodada |
| Polarização regional maior que a prevista, com o Sul e o Sudeste mais anti-PT | [FATO] 1T | O Sudeste tem 40,8% dos válidos |

### 6.2 Fatores que podem pesar contra Flávio

| Fator | Natureza | Observação |
|---|---|---|
| **Banco Master / "Dark Horse":** a PF apura financiamento de ~R$ 61 mi de Vorcaro para o filme sobre Jair. Mendonça autorizou inquérito em 23/7. Flávio negou "categoricamente" qualquer contato e depois admitiu a negociação ("dinheiro privado para um projeto privado") | [ALEGAÇÃO] investigação; [FATO] contradição registrada | Lula já usa o tema. Vorcaro **desistiu da delação** e foca em pedir liberdade ([Gazeta do Povo, 2/10](https://www.gazetadopovo.com.br/republica/daniel-vorcaro-desiste-de-delacao-premiada-e-foca-estrategia-na-liberdade/)), mas os autos continuam saindo do sigilo |
| Negociação com o Centrão sob condições (cargos, presidência do Senado) | [REPORTADO] | Pode gerar atrito com a ala antissistema. Renan Santos chama os dois de "bandido" |
| Rejeição alta (56% na Quaest do fim de setembro) e eleitor de Renan e Caiado com 29–38% em branco, nulo ou abstenção | [FATO] pesquisa | Apoio formal não garante transferência |
| Debates: os dois faltaram a todos no 1º turno. Aceitar ou recusar os do 2º turno tem custo para qualquer um | [FATO] histórico | – |
| **Crise do STF/Master:** o relatório da PF sobre contatos de Vorcaro com Moraes não conclui que houve crime. Mensagens também citam Mendonça e Nunes Marques, indicados por Bolsonaro | [FATO] relatório / [ALEGAÇÃO] conteúdo | O tema mobiliza a base de Flávio, mas os desdobramentos atingem atores dos dois campos |
| Comparecimento: a queda da abstenção no Nordeste e no Norte pode se repetir ou aumentar | [FATO] 1T | Cada 1 p.p. a menos de abstenção no Nordeste são ~0,43 milhão de eleitores. Com a divisão do 1º turno (63,5 x 31,1), isso dá um ganho líquido de ~0,13 milhão para Lula [calc aproximado] |
| Bolsa Família de R$ 691 pago a metade dos beneficiários antes de 25/10 | [REPORTADO] calendário | Não há estimativa causal do efeito no voto |

### 6.3 Fatores sem direção clara

- **Decisão de Fux sobre as bets e votação da 6x1:** cada resultado favorece narrativas diferentes.
- **Conteúdo sintético e desinformação:** a quarentena começa em 22/10. Houve remoções de conteúdo nos dois sentidos
  no 1º turno.
- **Novas revelações em casos abertos:** Master atinge políticos dos dois campos e do centro. INSS: nenhum fato
  novo localizado depois do 1º turno.
- **Mercados:** a última sessão antes da eleição (sex 2/10) fechou com o Ibovespa em +2,63%, a 192.114 pontos, e o
  dólar a R$ 5,216 ([CNN Brasil](https://www.cnnbrasil.com.br/economia/money/mercado/mercado-financeiro-ibovespa-dolar-2-outubro-2026/)).
  Parte da imprensa associou a alta à percepção de mais chances de Flávio **[OPINIÃO de analistas]**. **A reação ao
  resultado ainda não existe:** a B3 abre às 10h de 5/10, depois deste texto. A CNN atribuiu a alta de 2/10 também
  a dados fracos do mercado de trabalho dos EUA.

---

## 7. O que observar nas primeiras pesquisas de 2º turno

### 7.1 Como elas se saíram no passado

As referências vêm de `simulador/data/backtest_pesquisas_nacionais.csv` e `BACKTEST.md`. A métrica é a fatia de
votos válidos do PT **[calc]**.

| Ano | Resultado | Média da 1ª semana pós-1T | Erro da 1ª semana | Erro da média da véspera do 2T (agregador) |
|---|---|---|---|---|
| 2014 | 51,6 | 48,9 (Ibope, Datafolha, 7–9/10) | **−2,7** | +0,7 |
| 2018 | 44,9 | 43,3 (Ipespe, Datafolha, Ideia, 8–10/10) | **−1,6** | −1,1 |
| 2022 | 50,9 | 53,0 (Futura, Ipec, PoderData, Quaest, Datafolha, 3–7/10) | **+2,1** | +0,1 |

- **Na véspera do 2º turno, as pesquisas acertaram com erro de 1 a 2 p.p.** Na primeira semana, ficaram a 2–3 p.p.
  do resultado e erraram nos dois sentidos. Esse erro mistura erro de medida com movimento real da campanha.
- **No 1º turno de 2026, 11 de 14 institutos superestimaram a fatia de Lula.** A média ficou +1,8 p.p. acima
  (`AVALIACAO_1T_LICOES.md`). Mesmo assim, no backtest de 2014, 2018 e 2022, corrigir as pesquisas pós-1T pelo
  erro do 1º turno **piorou** a precisão (RMS de 0,77 para 1,06–4,3 p.p.), e o desvio de cada instituto não
  persistiu (correlação de −0,30 em 2018). Por isso o simulador usa essas pesquisas como publicadas.
- **Dois argumentos opostos, os dois legítimos:**
  - O erro de 2026 a favor do PT pode persistir, como em 2014 no 1º turno.
  - O histórico mostra que, depois do 1º turno, os institutos se recalibram.

### 7.2 Referências para cada leitura de modelo

A tabela usa a média das pesquisas pós-1T na fatia de Lula entre os dois. Em votos totais, basta dividir Lula por
(Lula + Flávio).

| Média das primeiras pesquisas (Lula, % válidos) | Compatível com… | Leitura **[inferência]** |
|---|---|---|
| **≤ 45** | Cauda baixa do principal (p25 = 45,5) | Flávio amplia a vantagem sobre o 1º turno, como Bolsonaro em 2022 (70% do ganho líquido) |
| **45 – 47** | Centro do principal (47,1) e "só pesquisas corrigidas" (47,6) | Transferência próxima da matriz da Quaest |
| **47 – 49** | Mistura do alternativo (48,0) e o ingênuo (49,0) | Lula retém a fatia que tinha entre os dois no 1º turno |
| **49 – 51** | Regressão histórica (49,8–52,1) | Exigiria uma virada no padrão de transferência e de comparecimento. O modelo principal subiria bastante: ele dá às pesquisas pós-1T um dp de 1,5 p.p. mais uma deriva de 3 p.p. por 21 dias |
| **≥ 51** | Cauda alta de todas as leituras (p90 do principal = 50,5) | Mudança de quadro. Lembrar que em 2022 a primeira semana superestimou o PT em 2,1 p.p. |

**Como ler:**
- Compare **cada instituto com ele mesmo**, de antes do 1º turno para depois, além da média. A Quaest tinha Flávio
  44 x Lula 42 em votos totais (2–3/10). O Datafolha, Lula 47 x Flávio 46 (3/10). A AtlasIntel, 50,1 x 49,9.
- Os institutos mais próximos do resultado no 1º turno foram Gerp, Futura, Vox e Palver, e os mais distantes,
  MDA, Nexus, RTBD e Indexa. **Não há evidência de que essa ordem se mantenha no 2º turno.**
- Também vale olhar o cruzamento do voto no 1º turno com o voto no 2º, sobretudo o **eleitor de Cury**; a
  rejeição de cada candidato; e a intenção por região (Sudeste e Nordeste).

---

## 8. Lacunas

- **Totais oficiais finais:** o TSE ainda marca a totalização como parcial (99,97%). Os números podem mudar alguns
  milhares de votos.
- **Pesquisas pós-1T:** nenhuma foi localizada até ~02:00 UTC de 5/10. O PesqEle/TSE bloqueou o acesso automatizado
  (403).
- **Mercado financeiro:** sem reação ao resultado até a abertura de 5/10.
- **Apoios formais:** faltam as notas de Novo, Avante e Missão, a decisão de União Brasil–PP (6/10), o MDB, o
  Republicanos e a posição de Caiado.
- **Debates:** as datas divergem (Record em 11/10 ou 18/10) e não há confirmação de presença.
- **Matriz de transferência:** vem de uma pesquisa só, com subamostras pequenas. Cury e Zema foram medidos em
  24–27/9, antes do resultado e dos apoios.
- **Decisões pendentes:** Fux (bets), plenário do Senado (6x1) e o desfecho da ação contra o reajuste do Bolsa
  Família.
- **Casos Master e INSS:** nenhum fato processual novo foi localizado depois do 1º turno. A data de um novo
  depoimento de Vorcaro (citado como "dia 15" pela Times Brasil) não foi confirmada.
- **Modelos:** os três têm de 3 a 6 eleições de calibração. O simulador trata a deriva da campanha como erro
  simétrico. A regressão histórica não enxerga a ideologia dos eliminados e perde para o ingênuo no backtest.
- **Fontes com resumo automático:** algumas páginas foram lidas por resumo (WebFetch). As citações literais vêm das
  páginas indicadas, mas convém conferir no original antes de republicar.

---

*Atualizar este briefing quando saírem a 1ª rodada de pesquisas pós-1T, a decisão de União Brasil–PP, a posição de
Caiado e a votação da 6x1. O painel do simulador ([link](https://claude.ai/artifact/2jH33uw8DKd8w5vbCEkwB6)) traz a
projeção do 2º turno por UF.*
