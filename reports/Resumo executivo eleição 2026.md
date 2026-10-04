# Pesquisas empatadas, e o resultado depende da premissa sobre o erro delas

*Resumo executivo, 3–4/10/2026, véspera do 1º turno (4/10). Um eventual 2º turno será em 25/10. Este texto não recomenda candidato.*

## Entregáveis

| Documento | O que traz |
|---|---|
| [Briefing eleição presidencial 2026](Briefing%20elei%C3%A7%C3%A3o%20presidencial%202026.md) | Erros das pesquisas em 2018 e 2022, a corrida de 2026, o contexto (fatos, alegações e versões de todos os lados), a segmentação e as premissas do modelo |
| [Briefing eleição 2026 – complemento](Briefing%20elei%C3%A7%C3%A3o%202026%20complemento.md) | Pesquisas nas 27 UFs, mercados de previsão verificados na fonte, série do TSE de 2002 a 2022 (lean, swing e correlação), transferência de votos, efeitos de casa e parâmetros finais |
| [Propostas e viabilidade dos candidatos](Propostas%20e%20viabilidade%20dos%20candidatos.md) | O que cada plano registrado propõe, o que vem só de declarações de campanha, custos, dependências do Congresso e trade-offs |
| [Painel do simulador](https://claude.ai/artifact/2jH33uw8DKd8w5vbCEkwB6) | Três visões do modelo principal, o modelo alternativo e os mercados lado a lado; mapa por UF; backtest; linha do tempo de eventos auditada |
| [Comparador de propostas](https://claude.ai/artifact/Qmc7jGPBiikX9SgsBdghEC) | Comparação interativa das propostas por tema, separando o plano registrado das declarações |

Os dois briefings abrem com uma caixa "Atualização de 3–4/10/2026", que lista as correções feitas na noite de 3/10.

## Números-chave

**Pesquisas (fato e [calc]).** Na média simples da última pesquisa de cada um dos 14 institutos com campo encerrado entre 26/9 e 3/10, o 1º turno fica em **Lula 41,5% x Flávio Bolsonaro 39,9%** em votos totais, e o 2º turno em **45,5% x 46,1%**, ou 49,6% para Lula entre os dois. As rodadas da véspera variam por instituto. O Datafolha (3/10) dá Lula 42 x Flávio 40 e 47 x 46 no 2º turno. A Quaest (2–3/10) dá Lula 40 x Flávio 38 no 1º turno e Flávio 44 x Lula 42 no 2º. A Futura (2–3/10) dá Flávio 42,5 x Lula 40,5 e 48,0 x 45,1 no 2º turno. A margem do 2º turno vai de Lula +4 (MDA) a Flávio +5 (Gerp e Palver), o que é diferença entre institutos, não ruído de amostra. Os estados repetem o mapa do 2º turno de 2022, com swing mediano próximo de zero. SP e MG são os maiores colégios em disputa.

**Modelos e mercado** (500 mil simulações por visão; dados até 3/10):

| | Simulador calibrado (principal) | Simulador neutro | Simulador viés pleno | Alternativo neutro | Alternativo histórico | Polymarket (normalizado) |
|---|---|---|---|---|---|---|
| Lula vence | 35,7% | 45,5% | 30,4% | 49,4% | 18,9% | 40,1% |
| Flávio vence | 64,3% | 54,5% | 69,6% | 50,6% | 81,1% | 58,8% |
| Decidida no 1º turno | 20,8% | 15,7% | 32,0% | 36,4% | 39,8% | 5,3% |
| Lula em 1º no 1º turno | 34,1% | 56,3% | 23,5% | 58,0% | 27,4% | 71,4% |

Fontes: `simulador/web/resultados.json`, `modelo_alternativo/resultados_alt.json`, API da Polymarket às 19h14 UTC de 3/10. Kalshi, PredictIt e casas britânicas davam de 56% a 60% a Flávio.

**Backtest.** O simulador foi rodado na véspera de 2014, 2018 e 2022, só com as pesquisas daquele momento. Fora da amostra, os intervalos de 80% e 95% da visão calibrada contiveram 75% e 95% dos resultados nacionais e 81% e 93% dos estaduais. O erro absoluto médio foi de 2,8 p.p. no nacional e 4,8 p.p. por UF.

## Como ler os cenários

1. **Todas as colunas partem da mesma média de pesquisas**, que é um empate. Elas diferem numa única premissa: se as pesquisas de 2026 erram na mesma direção em que erraram na véspera de 2014, 2018 e 2022. Naqueles ciclos, a média ficou mais favorável ao PT do que a urna no 1º turno em +6,2, +2,7 e +0,6 p.p.
2. **A visão neutra** supõe erro sem direção. **A calibrada** aplica um viés estimado com esses três ciclos e encolhido para zero (+1,5 ± 1,4 p.p.), porque três eleições são pouca evidência. **A pleno** repete o erro médio sem encolhimento. A regra é simétrica: erros históricos de sinal oposto produziriam correção para o outro lado.
3. **O modelo alternativo** usa outro método: filtro de Kalman e bootstrap dos erros reais. Ele chega à mesma média e à mesma conclusão. Sem viés, a eleição fica perto de 50/50, com 45% a 49% para Lula. Com o viés histórico, Flávio passa a favorito.
4. **O mercado** fica entre a visão neutra e a calibrada no resultado final. No 1º turno, porém, ele está mais perto da leitura literal das pesquisas: Lula em 1º com 71% e decisão no 1º turno com 5%.
5. **Probabilidades não são votos.** Uma chance de 64% significa que o resultado oposto acontece em cerca de 1 de cada 3 cenários.

## Principais incertezas

- **Viés das pesquisas.** É a premissa que mais move o resultado. Passar da visão neutra à calibrada desloca cerca de 10 pontos de probabilidade. Os argumentos dos dois lados estão no briefing (§1.3 e Conclusão).
- **Amostra histórica mínima.** São 3 eleições no 1º turno e 2 no 2º. A chance de decisão no 1º turno (16–40% nos modelos, contra 5% no mercado) vem das caudas largas escolhidas no backtest. No modelo alternativo, ela depende quase toda do erro de 2014.
- **O 2º turno é projetado três semanas antes.** O modelo trata a deriva da campanha como erro simétrico largo. Fatos entre os turnos não estão nele: o reajuste do Bolsa Família pago em 19/10, uma eventual decisão do STF sobre a proibição das bets e o caso Master/STF.
- **Transferência de votos.** A matriz vem de subamostras pequenas de uma pesquisa (Quaest). Em 2022, Bolsonaro ficou com 70% do ganho líquido entre os turnos, e a matriz declarada de 2026 não reproduz essa assimetria.
- **Dados pendentes.** A AtlasIntel nacional final (válidos Lula 47 x Flávio 44,1; 2º turno 50,1 x 49,9) saiu depois da rodada final do modelo e ainda não está nos números acima. A Veritá nacional de 26/9–2/10 não tinha saído até cerca de 22h de 3/10. A ponderação da maioria dos institutos não foi verificada em documento primário.
- **Mercados.** Polymarket, Kalshi e PredictIt são arbitradas entre si e funcionam como um sinal só. A Polymarket é proibida no Brasil, e a calibração desses mercados em eleições brasileiras não pode ser medida.

## Neutralidade

Os modelos usam só pesquisas registradas, resultados do TSE e parâmetros com origem documentada (fonte, cálculo, backtest ou inferência). A linha do tempo do painel foi auditada para equilíbrio entre os lados (`simulador/data/auditoria_neutralidade.md`) e não altera nenhum número. Os briefings separam fato, alegação, versão e opinião. O relatório de propostas separa o plano registrado das declarações de campanha. Nenhum documento recomenda voto. O resultado do 1º turno em 4/10, sobretudo em SP e MG, deve ser o primeiro dado a atualizar a projeção do 2º turno.
