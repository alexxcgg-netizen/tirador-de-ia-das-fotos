# Pesquisas empatadas, e o resultado depende da premissa sobre o erro delas

> **Resultado do 1º turno: atualização de 5/10/2026, madrugada; 98,6% das seções totalizadas (TSE, 21:03 de
> 4/10), números provisórios**
>
> - **2º turno em 25/10 entre Flávio Bolsonaro e Lula.** Votos válidos: **Flávio 47,1%, Lula 45,1%**, Cury 2,9%,
>   Renan 2,3%, Caiado 2,2%, Zema 0,3% e outros 0,2%. A margem é de 2,0 p.p. para Flávio, ~2,8 milhões de votos.
>   Lula venceu em 12 UFs (Nordeste, PA, AM e AP) e Flávio em 15, incluindo SP, MG e RJ. A abstenção foi de 21,1%,
>   contra 21,0% em 2022 [calc].
> - **Melhores previsões do nacional:** a visão calibrada do simulador errou a margem em −0,5 p.p., com erro médio
>   de 0,5 p.p. nos dois primeiros, o menor entre todos os previsores. Gerp, Futura e Vox Brasil erraram a margem
>   em ≤ 1,1 p.p. A média simples das pesquisas errou +3,4 p.p. na margem a favor de Lula, porque superestimou os
>   candidatos menores. A visão neutra errou +2,8 e a pleno −2,8.
> - **Onde o modelo errou:** a margem de Lula foi subestimada no Nordeste (−4,6 p.p.) e no Norte (−3,5) e
>   superestimada no Sul (+6,0). Ainda assim, 53 de 54 intervalos estaduais de 80% contiveram o resultado. Os
>   mercados davam 71–72% para Lula em 1º e acertaram melhor que os modelos que não haveria decisão no 1º turno.
> - **Projeção do 2º turno com o 1º turno real:** **Flávio 85,5%, Lula 14,5%.** Lula aparece com 47,2% dos válidos
>   (80%: 43,8–50,7). A Polymarket dá 14% a Lula e a Kalshi 17%. Sem a correção de viés histórico, Lula teria
>   ~27% [calc]. O que pode mudar o quadro: a divisão dos 7,8% dos eliminados, o comparecimento por região, as
>   primeiras pesquisas pós-1º turno e os fatos da campanha.
> - Detalhes, ranking completo, desempenho da projeção ao vivo (com os problemas corrigidos durante a noite) e
>   limitações: [Avaliação do 1º turno 2026](Avalia%C3%A7%C3%A3o%20do%201%C2%BA%20turno%202026.md).
>   [Painel do simulador](https://claude.ai/artifact/2jH33uw8DKd8w5vbCEkwB6) (2º turno atualizado) ·
>   [Comparador de propostas](https://claude.ai/artifact/Qmc7jGPBiikX9SgsBdghEC).
>
> *O texto abaixo é a versão da véspera (3–4/10) e foi mantido como registro das previsões.*

*Resumo executivo, 3–4/10/2026, véspera do 1º turno (4/10). Um eventual 2º turno será em 25/10. Este texto não recomenda candidato.*

## Entregáveis

| Documento | O que traz |
|---|---|
| [Briefing eleição presidencial 2026](Briefing%20elei%C3%A7%C3%A3o%20presidencial%202026.md) | Erros das pesquisas em 2018 e 2022, a corrida de 2026, o contexto (fatos, alegações e versões de todos os lados), a segmentação e as premissas do modelo |
| [Briefing eleição 2026 – complemento](Briefing%20elei%C3%A7%C3%A3o%202026%20complemento.md) | Pesquisas nas 27 UFs, mercados de previsão verificados na fonte, série do TSE de 2002 a 2022 (lean, swing e correlação), transferência de votos, efeitos de casa e parâmetros finais |
| [Propostas e viabilidade dos candidatos](Propostas%20e%20viabilidade%20dos%20candidatos.md) | O que cada plano registrado propõe, o que vem só de declarações de campanha, custos, dependências do Congresso e trade-offs |
| [Avaliação do 1º turno 2026](Avalia%C3%A7%C3%A3o%20do%201%C2%BA%20turno%202026.md) | Resultado, ranking dos previsores, erros regionais, projeção ao vivo, mercados e projeção do 2º turno (5/10) |
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

## Realidade × discurso (atualização de 5/10/2026)

O painel ganhou a aba "Realidade × discurso", com os dados em `simulador/web/realidade.json`. Ela separa quatro tipos de distância entre número e discurso: (a) limite de medição, (b) enquadramento seletivo, (c) afirmação falsa e (d) manipulação de dados. A mesma régua vale para governo, oposição e mercado.

- **Nenhuma evidência de manipulação de dados do IBGE.** Há crise administrativa real (greve desde ago/2026, fundação IBGE+ considerada irregular pelo TCU), mas nenhuma denúncia técnica de interferência nos números. A alegação de que "o IBGE maquia o desemprego" é falsa pelo método da OIT, em uso desde 2012.
- **O maior descolamento entre número e vida real é taxa x nível, não erro de medição.** De jan/2019 a ago/2026, a alimentação no domicílio subiu 76,3%, e o IPCA, 49,7% (recalculado no SIDRA). A renda real do trabalho subiu 13,3% pelo deflator oficial e caiu 3,6% medida em comida. "Renda recorde" e "comida mais cara que antes da pandemia" são verdadeiras ao mesmo tempo.
- **Outros limites de medição:** o IPCA mede o litro, e com a gasolina E30 o custo por km sobe 1 a 2 p.p. a mais uma vez. O combustível está represado por subvenções (MPs 1.340, 1.363 e 1.391/2026). A deflação de agosto veio do bônus de Itaipu. O aluguel de quem muda de casa sobe cerca de 4 p.p. a mais por ano que o do IPCA, e os planos coletivos cerca de 5 p.p. a mais. O desemprego de 5,3% convive com subutilização de 13,1% e informalidade de 37,5%. O número de 3,78% de reduflação (IBPT) não tem método robusto.
- **Dívida:** o comprometimento da renda com o serviço da dívida foi de 28,72% em jul/2026 (BCB SGS 29034, com ajuste sazonal, máximo desde 2005), contra 22,75% em jan/2019. Os 29,3%–29,7% noticiados para fev–mar/2026 não aparecem em nenhuma das séries atuais. A série sem ajuste (29265) tem pico de 29,48% em mar/2026.
- **Checagem de 14 afirmações de cada campanha.** Lula/PT teve 3 corretas, 1 correta quando dita mas hoje exagerada, 5 corretas mas enganosas, 2 exageradas e 3 falsas. Flávio/PL teve 2 corretas, 3 corretas mas enganosas, 1 exagerada, 3 falsas e 5 sem base. O padrão descreve como cada lado erra e não serve de nota aos candidatos: os erros de Lula se concentram na comparação com o passado e na omissão do custo fiscal, e os de Flávio em promessas sem conta que feche (corte de R$ 190 bi, IVA de 20%, crescimento de 4% ao ano, juros caindo "na reunião seguinte"). A seleção não é aleatória, então a contagem não mede quem "mente mais".
- **Mercado:** ele acerta o diagnóstico fiscal, mas projeções condicionais circulam como promessa, como o "dólar a R$ 4,50 com Flávio". Errou para os dois lados no 1º ano de governos novos: pessimista com Lula em 2003 e 2023, otimista com a agenda liberal em 2019. Acertou a direção em 2014–16. O IDP de 2023–25 (média de US$ 74,8 bi por ano) foi maior que o de 2019–22 (US$ 57,3 bi), e a taxa de investimento ficou parada em cerca de 16,7%–16,9% do PIB nos dois períodos.

Itens que as notas citavam de memória foram conferidos em 5/10: a carta aberta do BC de 10/07/2025 sobre a meta descumprida e as Leis 14.754/2023, 14.789/2023, 14.871/2024 e 14.973/2024. A data da fala de Jair Bolsonaro sobre "contas esfaceladas" segue marcada como não confirmada. O relato de retórica de Lula contra a autonomia do BC em set/2026, que só tinha fonte de agregador, foi omitido.

## Neutralidade

Os modelos usam só pesquisas registradas, resultados do TSE e parâmetros com origem documentada (fonte, cálculo, backtest ou inferência). A linha do tempo do painel foi auditada para equilíbrio entre os lados (`simulador/data/auditoria_neutralidade.md`) e não altera nenhum número. Os briefings separam fato, alegação, versão e opinião. O relatório de propostas separa o plano registrado das declarações de campanha. Nenhum documento recomenda voto. O resultado do 1º turno em 4/10, sobretudo em SP e MG, deve ser o primeiro dado a atualizar a projeção do 2º turno.
