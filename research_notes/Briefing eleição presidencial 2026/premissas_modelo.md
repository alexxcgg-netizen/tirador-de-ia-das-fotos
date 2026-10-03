# Premissas e parâmetros para um modelo Monte Carlo (≈500 mil simulações) da eleição presidencial brasileira de 2026, por estado

> Observação de contexto: hoje é 03/10/2026, véspera do 1º turno (04/10/2026). Os parâmetros abaixo valem para um nowcast de véspera e para a projeção do 2º turno (25/10/2026). Todos os números vêm de fontes citadas; cálculos feitos por mim a partir dessas fontes aparecem em "Inferências".

## 1. Magnitude e viés do erro das pesquisas finais no Brasil (presidente, 1º/2º turno, por estado, por instituto)

### Takeaway
No 1º turno, o erro em candidatos individuais nas pesquisas de véspera é grande e **sistemático numa só direção desde 2014**: o candidato anti-PT mais competitivo ficou subestimado em 5 a 8 p.p. de votos válidos (Aécio em 2014, Bolsonaro em 2018 e 2022). No 2º turno o erro é bem menor (1 a 3 p.p.). O erro absoluto médio por candidato (medida do Pindograma) fica em torno de 2,5 p.p. para presidente e 3,5 p.p. para governador, mas a média esconde caudas: há erros de margem de 15 a 20 p.p. em disputas estaduais.

### Cited Findings
**Erro médio agregado (Pindograma, média do erro absoluto por candidato em votos válidos, só pesquisas da última semana):**
- Presidente (nacional): 3,17 p.p. (2014), 2,46 (2018), 2,53 (2022). Presidente (pesquisas estaduais): 4,34 (2014), 2,25 (2018), 2,53 (2022). Governador: 3,07 (2014), 3,65 (2018), 3,53 (2022). — [Pindograma, "Quatro lições que tiramos do desempenho das pesquisas em 2022"](https://pindograma.com.br/2022/09/05/desempenho-pesquisas-22.html) (atenção: o slug da URL tem data de 05/09/2022, mas o texto analisa resultados de 2022. A data de publicação real não está clara.)
- Ipec/Ibope/Datafolha contra os concorrentes: presidente 2014, 2,36 contra 3,71 (vantagem de 1,35 p.p.); presidente 2022, 2,37 contra 2,56 (0,19 p.p.); governador 2022, 3,31 contra 3,50 (0,19 p.p.). É a menor diferença da série histórica. — [Pindograma](https://pindograma.com.br/2022/09/05/desempenho-pesquisas-22.html)
- A correlação entre a nota histórica do ranking (2012–2020) e o desempenho em 2022 foi de **0,03**. Os agregadores superaram os institutos individuais. — [Pindograma](https://pindograma.com.br/2022/09/05/desempenho-pesquisas-22.html)
- O desempenho de um instituto em 2012/2014 "não está correlacionado" com o de 2016/2018. Ponderar o agregado pela nota histórica melhorou a precisão em apenas **0,1 p.p.** — [Pindograma, metodologia do ranking](https://pindograma.com.br/2020/09/07/ranking.html). Entre os institutos A/B+ é difícil prever quem acerta mais. A correlação só aparece entre as notas ruins ("quanto pior a nota, pior parece ser o desempenho futuro"). — [Pindograma, mudanças 2022](https://pindograma.com.br/2022/06/24/rankingat.html)

**2022, 1º turno (resultado em válidos: Lula 48,43%, Bolsonaro 43,20%, Tebet 4,2%, Ciro 3,0%; em totais: Lula 46,3%, Bolsonaro 41,3%, brancos e nulos 4,4%):**
- Pesquisas finais (votos totais): Datafolha 30/09–01/10 (n=12.800) Lula 48, Bolsonaro 34, Tebet 6, Ciro 5, brancos e nulos 5. Ipec 29/09–01/10 (n=3.008) 47/34/5/5, brancos e nulos 7. Abrapel/Ipespe 46/33. AtlasIntel 28–30/09 (n=4.500) 49,8/40,7/2,6/3,9, brancos e nulos 1. — [Wikipedia, Opinion polling 2022](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2022_Brazilian_presidential_election)
- Em votos válidos: Datafolha Lula 50 × Bolsonaro 36; Ipec Bolsonaro 37; AtlasIntel Bolsonaro 41,1, o mais próximo e o único 100% via web. — [CNN Brasil](https://www.cnnbrasil.com.br/politica/resultados-das-urnas-divergem-de-pesquisas-eleitorais/); [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121840/veja-previsoes-eleitorais-de-pesquisas-que-acertaram-resultado-em-2022)
- Quaest de 01/10 (votos totais): Bolsonaro 33,5 (resultado 41,3, erro −7,8), Lula 43,5 (46,3, erro −2,8), outros 11,6 (8,0, erro +3,6), indecisos 8,3, brancos e nulos 3,1 (4,4). Tomando o agregador do Estadão como média, as pesquisas subestimaram Bolsonaro em ~8 p.p. dos votos totais. — [Pereira & Nunes, Opinião Pública v.30, 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)

**2022, 2º turno (resultado em válidos: Lula 50,9%, Bolsonaro 49,1%):**
- Datafolha 28–29/10 (n=8.308) Lula 49, Bolsonaro 45, brancos e nulos 7. Ipec 27–29/10 50/43/7. Paraná Pesquisas 47,1/46,3/6,6. AtlasIntel 52,4/45,7/1,9 (votos totais, conforme a tabela da Wikipedia). — [Wikipedia](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2022_Brazilian_presidential_election)
- O agregador do Estadão indicou Lula com 52% dos válidos, erro de 1,1 p.p. Os institutos não mudaram a metodologia de coleta entre os turnos (registros do PesqEle). — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)

**2018:**
- 1º turno, véspera (06/10), votos válidos: Datafolha Bolsonaro 40, Haddad 25. Ibope 41 e 25. Resultado: 46 e 29. Erro de 5 a 6 p.p. em Bolsonaro e ~4 p.p. em Haddad. Boca de urna Ibope: 45 e 28. — [Aos Fatos](https://www.aosfatos.org/noticias/postagens-distorcem-resultados-para-dizer-que-ibope-e-datafolha-erraram-em-2018/)
- Votos totais 03–04/10: Datafolha (n=19.552) Bolsonaro 36, Haddad 22, Ciro 13, Alckmin 7, indecisos 10. DataPoder360 30/25/15. Paraná Pesquisas 34,9/21,8. RealTime Big Data 34/24. Resultado em válidos: Bolsonaro 46,0, Haddad 29,3, Ciro 12,5, Alckmin 4,8. — [Wikipedia, Opinion polling 2018](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2018_Brazilian_presidential_election)
- 2º turno, finais em válidos: Ibope Bolsonaro 54 × 46, Datafolha 55 × 45. Resultado: 55,1 × 44,9. — [Poder360](https://www.poder360.com.br/eleicoes/ibope-bolsonaro-54-x-46-haddad-datafolha-bolsonaro-55-x-45-haddad/)

**2014:**
- Aécio Neves: Ibope 27%, Datafolha 26% nas finais, contra 33,5% no resultado (subestimado em 6,5 a 7,5 p.p.). — [Blog do Dina](https://blogdodina.com/pesquisas-eleitorais-erram-mesmo-lado-flavio-polymarket/) (fonte secundária. Não confirmei se os números das pesquisas estão em válidos ou totais.)
- Sensus de véspera: Dilma 37,3, Marina 22,5, Aécio 20,6. Resultado: Dilma ~41,6, Aécio ~33,6, Marina ~21,3 (válidos, apuração parcial de 93,5%: 41,0/34,2/21,1). — [Diario de Cuyo](https://diariodecuyo.com.ar/mundo/Dilma-y-Neves-se-disputaran-la-presidencia-de-Brasil-en-el-ballotage-20141005-0002.html)

**2010:**
- 1º turno, finais em votos totais: Datafolha 01–02/10 Dilma 47, Serra 29, Marina 16. Ibope igual. Vox Populi 47/26/14. Resultado em válidos: Dilma 46,91, Serra 32,61, Marina 19,33. 2º turno: Datafolha 27–30/10 Dilma 52, Serra 40, contra 56,05 e 43,95 em válidos. — [Wikipedia, Opinion polling 2010](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2010_Brazilian_presidential_election)

**Erros estaduais (governador 2022, exemplos de cauda):**
- SP: Ipec Haddad 41 × Tarcísio 31, Datafolha 39 × 31, contra 35,7 × 42,3 no resultado (erro de margem ~15,6 p.p.). RJ: Ipec Castro 48 × Freixo 33, contra 58,7 × 27,4 (~17 p.p.). BA: Ipec ACM Neto 51 × Jerônimo 40, contra 40,8 × 49,5 (20,65 p.p., com inversão de ordem). RS: Ipec Leite 40 × Onyx 30, contra 26,8 × 37,5 (20,69 p.p.). — [Seu Dinheiro](https://www.seudinheiro.com/2022/politica/eleicoes-2022-lula-bolsonaro-pesquisas-do-ipec-e-datafolha-erraram-resultados-das-urnas-em-ate-20-pontos-percentuais-nos-estados-lils/) (a matéria mistura bases de votos totais e válidos. Os números de "erro" são de margem entre os dois primeiros.)

### Inferências
- Erros de **margem** (1º contra 2º colocado, em válidos) que calculei com os dados acima. 2022 1ºT: Datafolha ~14 p.p. projetado contra 5,2 real (erro ≈ 8,8). Ipec ≈ 8,8. Atlas ≈ 9,2 contra 5,2 (erro ≈ 4,0). 2018 1ºT: Datafolha/Ibope 15–16 contra 16,7 (margem quase certa, mas ambos os candidatos subestimados porque os "outros" foram superestimados). 2022 2ºT: Datafolha válidos ≈ 52,1 × 47,9 (Lula +1,2). Ipec ≈ 53,8 × 46,2 (+2,9). Paraná ≈ 50,4 × 49,6 (−0,5). 2018 2ºT: erro ≤ 1 p.p. 2010 2ºT: Datafolha em válidos ≈ 56,5 × 43,5 contra 56,05 (≈ +0,5). 2010 1ºT: Datafolha em válidos ≈ Dilma 51,1, Serra 31,5, Marina 17,4, ou seja, Dilma superestimada em ~4 p.p. e um 2º turno não antecipado.
- **Parâmetros sugeridos para o simulador (calibração):**
  - 1º turno, erro sistemático nacional por candidato: desvio padrão de ~3 a 4 p.p. em válidos, com cauda pesada (t de Student com ν ≈ 4–6). Some um **viés estrutural opcional** a favor do candidato anti-PT mais competitivo de +2 a +4 p.p., ou trate o viés como desconhecido com média 0 e σ maior. Três eleições seguidas (2014, 2018, 2022) com o mesmo sinal é evidência forte, mas N=3. Recomendo rodar com e sem o viés e mostrar os dois cenários.
  - Os "outros"/terceira via são sistematicamente superestimados no 1º turno (voto útil). Modele uma contração (shrink) da 3ª via de ~20–40% nas pesquisas finais, redistribuída aos dois primeiros. Em 2022, Quaest mostrava "outros" com 11,6 e o resultado foi 8,0.
  - 2º turno: σ nacional da margem ≈ 2–3 p.p. (meia-margem ≈ 1–1,5 p.p.), t com ν ≈ 5.
  - Componente estadual (para presidente, em pesquisas estaduais): erro absoluto médio de ~2,3–4,3 p.p. por candidato e caudas de 15–20 p.p. de margem em governador. Sugiro σ estadual idiossincrático de ~3–4 p.p. na margem para presidente, com ν baixo (3–5).
- Ponderação por "rating" do instituto quase não tem valor preditivo no Brasil (r=0,03; ganho de 0,1 p.p.). Use **penalidade só para institutos claramente ruins** e trate o resto igualmente. Estimar house effects em tempo real é mais útil que notas históricas.

### Gaps
- Não obtive séries de pesquisas finais de **2006** (Lula chegou a 48,6% e houve 2º turno contra Alckmin, que as pesquisas tenderam a subestimar). Também faltou 2014 em votos válidos por instituto de fonte primária. Verificar na Wikipedia PT ou no acervo Datafolha.
- Não encontrei o ranking atualizado do Pindograma (2024/2026) com notas por instituto (Quaest, AtlasIntel, Paraná Pesquisas, PoderData, Real Time Big Data). Ver https://pindograma.com.br/ranking.html.
- Os números da Atlas no 2º turno de 2022 na Wikipedia (52,4/45,7) parecem inconsistentes com outras reportagens. Conferir na fonte original.
- Não encontrei estudo acadêmico com a distribuição completa de erros estaduais para presidente por UF de 2006 a 2022. O banco do Pindograma no GitHub (citado como aberto) é a melhor fonte para estimar isso.

## 2. Estrutura estatística recomendada (agregação, house effects, caudas, correlação entre estados)

### Takeaway
O padrão-ouro é um modelo bayesiano dinâmico (Linzer 2013, depois Heidemanns, Gelman & Morris 2020) com: random walk por estado e nacional, house effects por instituto, um termo de erro não amostral comum a todos os institutos, priors de "fundamentos", e erros correlacionados entre estados. No Brasil, a seleção de pesquisas segue os critérios do Pindograma (janela final de 3 semanas no 1ºT e 2 semanas no 2ºT, lista completa de candidatos, pesquisa estimulada).

### Cited Findings
- O modelo da Economist (Heidemanns, Gelman & Morris, HDSR 2020) estende o modelo bayesiano dinâmico de Linzer (2013). Ele combina por partial pooling uma previsão por fundamentos (renda, aprovação, incumbência) com pesquisas nacionais e estaduais num modelo de série temporal da opinião por estado. Cada pesquisa é tratada como estimativa do apoio daquele dia, com viés e variância modelados. O modelo inclui **house effects por instituto** e **erros compartilhados por todos os institutos**, e foi ajustado em R/Stan com atualização diária. — [Heidemanns, Gelman & Morris, HDSR 2020](https://sites.stat.columbia.edu/gelman/research/published/hdsr_forecasting.pdf); [resumo em HDSR](https://sites.stat.columbia.edu/gelman/research/published/Harvard_Data_Science_Review.pdf)
- Reflexão de 2024 sobre a incerteza dos modelos: [Grappling with uncertainty in forecasting the 2024 U.S. presidential election (HDSR 6.4)](https://hdsr.mitpress.mit.edu/pub/yoa73r1m/release/1); [blog de Gelman](https://statmodeling.stat.columbia.edu/2024/07/03/grappling-with-uncertainty-in-forecasting-the-2024-u-s-presidential-election/)
- Crítica sobre sucesso e fracasso de pesquisas e previsões: [Statistics and Public Policy, 2021](https://www.tandfonline.com/doi/full/10.1080/2330443X.2021.1971126)
- Metodologia do Pindograma (inspirada no FiveThirtyEight). O erro é calculado por candidato contra os votos válidos (em 2022 a métrica mudou do desvio padrão das diferenças com sinal para a média das diferenças absolutas). Uma regressão estima o erro esperado dado o tipo de disputa (presidente nacional, presidente estadual, governador, prefeito), o turno, os dias até a eleição, o tamanho da amostra, a UF e o % de brancos e nulos. O índice II combina comparações dentro da mesma eleição: `(n(x−m) + 3·índice1)/(n+3)`. O ranking aplica regressão à média com pesquisas "neutras" (30 até 2020, 15 a partir de 2022), com prior melhor para institutos filiados à ABEP/CONRE (−0,07 contra 0,74). Critérios de inclusão: até 3 semanas antes do 1ºT ou 2 semanas antes do 2ºT, candidatos listados somando ≥90% dos votos, pesquisa estimulada. Base de 6.062 pesquisas (2012–2018). — [Pindograma, metodologia](https://pindograma.com.br/2020/09/07/ranking.html); [Pindograma 2022](https://pindograma.com.br/2022/06/24/rankingat.html)
- Agregadores brasileiros existentes: Estadão (agregador de pesquisas, usado como referência por Pereira & Nunes) — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf); PollingData/PDVoto, com agregação por UF e cargo — [flex.pollingdata.com.br](https://flex.pollingdata.com.br/pdvoto/2022/governador/se/t1/); "PollsterGraph", citado pelo Pindograma como melhor que institutos individuais — [Pindograma](https://pindograma.com.br/2022/09/05/desempenho-pesquisas-22.html)

### Inferências
Proposta de arquitetura em dois estágios, ambos factíveis em NumPy:
1. **Estágio de agregação (média de pesquisas por estado e nacional):**
   - Use o log-ratio aditivo (ALR) das participações em válidos como espaço de modelagem, para respeitar a soma 1 em múltiplos candidatos.
   - Peso de cada pesquisa: `w = (n_eff)^(1/2) · exp(−Δdias/τ) · q_instituto`, com τ ≈ 7–10 dias na reta final, n_eff limitado (por exemplo, a 2.000–3.000) para que pesquisas gigantes (Datafolha com 12–19 mil entrevistas) não dominem, já que o erro dominante não é amostral, e q = 1 para todos, exceto institutos com histórico ruim ou sem registro no TSE.
   - House effect: estime por modelo misto (`y_ij = μ_estado,t + h_instituto + ε`) com a restrição Σh = 0 (ou média dos institutos "de referência"). Assim o house effect é relativo ao consenso, e o viés do consenso fica por conta do erro sistemático do estágio 2.
   - Se houver tempo: Kalman/DLM (random walk com σ_dia ≈ 0,2–0,4 p.p.) por estado, com partial pooling para o nacional (como Linzer/Economist).
2. **Estágio de simulação (incerteza do dia da eleição):** `margem_s = média_s + e_nacional + e_regional(r(s)) + e_estado(s) + e_viés_específico_candidato`. Cada componente vem de uma t multivariada (ν≈5). Ordem de grandeza: σ_nac ≈ 3 p.p. por candidato no 1ºT (≈2 no 2ºT), σ_reg ≈ 1,5–2, σ_est ≈ 2,5–3,5 (maior em UFs com poucas pesquisas e inflado por 1/√(número de pesquisas)).
   - **Covariância entre estados:** estime a correlação a partir dos desvios estaduais (swing da UF menos swing nacional) do voto petista em 2006, 2010, 2014, 2018 e 2022 (dados do TSE por UF/município), mais similaridade demográfica do Censo 2022 (% evangélicos, renda, escolaridade, % Bolsa Família, região). Use shrinkage (Ledoit-Wolf) para uma matriz positiva definida, porque 5 eleições não bastam para uma covariância 27×27. Regiões naturais: N, NE, CO, SE, S, e talvez SP separado.
   - Para estados sem pesquisas: prior = resultado de 2022 na UF + swing nacional estimado × elasticidade da UF (elasticidades históricas do TSE).
- Como o rating histórico prediz pouco, o maior ganho vem de: (a) **erro sistemático comum** grande e de cauda pesada; (b) **ajuste para voto útil e indecisos** (seção 3); (c) house effects estimados no próprio ciclo.

### Gaps
- Não acessei diretamente as páginas de metodologia do FiveThirtyEight/Silver Bulletin (uso de distribuição t, "uncertainty index", ajustes de likely voter, house effects) nem a do modelo da Economist para 2024. Os detalhes acima sobre t de Student são recomendação baseada na prática conhecida, sem citação direta nesta nota.
- Não localizei metodologias publicadas de JOTA, Atlas, Poder360 (agregador) ou Estadão Dados para 2026, nem modelos acadêmicos brasileiros de previsão probabilística por UF.

## 3. Votos válidos, indecisos, brancos/nulos e abstenção

### Takeaway
O resultado oficial é em **votos válidos**, sem brancos e nulos. Converter os votos totais da pesquisa exige retirar brancos, nulos e indecisos. Distribuir os indecisos proporcionalmente é enviesado no Brasil: a evidência de 2022 mostra alinhamento tardio desproporcional dos indecisos e voto útil a favor do candidato anti-PT mais competitivo. A abstenção (~20–21%) não entra no cálculo de válidos, mas importa para o comparecimento diferencial por perfil.

### Cited Findings
- 2022: abstenção de 20,95% no 1ºT e 20,59% no 2ºT. — [CUT](https://www.cut.org.br/noticias/total-de-abstencoes-caiu-de-20-95-para-20-59-entre-o-1-e-o-2-turno-da-eleicao-1f2f). No 2ºT, abstenção de 32.200.558 eleitores (20,59%), brancos 1,43% e nulos 3,16% dos votos. — [Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2022/abstencao-votos-brancos-e-nulos-no-segundo-turno-da-eleicao-presidencial-de-2022/); [TSE](https://www.tse.jus.br/comunicacao/noticias/2022/Outubro/100-das-secoes-totalizadas-confira-como-ficou-o-quadro-eleitoral-apos-o-2o-turno)
- Brancos e nulos no 1ºT 2022: 4,4% dos votos totais (contra 3,1% na Quaest de véspera). — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)
- Os indecisos caíram de 8,3% no sábado antes do 1ºT para 5% no sábado antes do 2ºT, ou seja, boa parte resolve a ambivalência no 1ºT. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)
- Mudança tardia (Quaest, painel antes e depois): entre quem se informa pela internet (~40% do eleitorado), a vantagem de Bolsonaro em válidos passou de ~6 p.p. (intenção em 26–27/09) para mais de 13 p.p. (voto reportado em 3–4/10). Entre evangélicos (~28%), de 27 para 39 p.p. Cada efeito equivale a mais de 3 p.p. no agregado. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)
- Realocação: entre os indecisos, Bolsonaro estava à frente de Lula no ordenamento de 52,5%. Lula era o mais rejeitado por 39,9% dos indecisos e 39,1% da terceira via. Bolsonaro, por 32,1% e 26,8%. Realocar o voto útil (por rejeição) e os indecisos (pela 2ª preferência) levou Bolsonaro de 33,5 para 40,1–41,1 (real 41,3) e Lula de 43,5 para 48,0–48,5 (real 46,3). A margem projetada foi de 7,4–7,9 contra 5,0 real, quando a pesquisa bruta dava 10. A **alocação proporcional dos indecisos ignora as propensões e funciona pior**. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)
- A literatura internacional (Kennedy et al. 2018 e outros) documenta mudança tardia como fonte de erro. No Brasil, voto obrigatório com abstenção possível amplia o alinhamento dos indecisos. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)

### Inferências
- Pipeline sugerido por pesquisa:
  1. Partir dos votos totais estimulados.
  2. Retirar brancos e nulos (simular a taxa final de brancos e nulos como ~3,5–5% no 1ºT, com prior pelo histórico da UF).
  3. Alocar indecisos por 2ª preferência ou rejeição quando houver microdados, senão por uma regra "anti-rejeição": os indecisos vão menos para o candidato mais rejeitado. Parametrize com um Dirichlet cujo vetor de concentração vem dos dados de 2ª preferência.
  4. Aplicar o voto útil: transferência de uma fração π ~ Beta (média 0,25–0,35) da 3ª via para os dois primeiros, na proporção inversa da rejeição.
  5. Normalizar para válidos.
- Abstenção: use-a para pesar o comparecimento diferencial (cortes de renda e escolaridade com abstenção maior). Se as pesquisas não filtram "eleitor provável", o viés pode correr para o lado do eleitorado de menor comparecimento. Simule a abstenção por UF como ~20% ± 2 p.p. (base 2022), mas a métrica de vitória continua sendo os válidos, então o efeito é de segunda ordem.
- Para pesos amostrais, prefira institutos que já usam o Censo 2022 em vez do Censo 2010 ou da PNAD. Diferenças de composição religiosa (evangélicos) e etária afetam diretamente o voto Lula × anti-PT.

### Gaps
- Não obtive a abstenção e os brancos/nulos oficiais do 1ºT 2018 nem a série de 2006–2014 por UF. Usar o portal de dados abertos do TSE (dadosabertos.tse.jus.br, "Resultados", detalhe da votação por município e zona).
- Sem estudo específico sobre o "likely voter model" no Brasil.

## 4. Modelagem do 2º turno: matriz de transferência e rejeição como teto

### Takeaway
Os erros de 2º turno são historicamente pequenos (≤1–3 p.p.), então cenários diretos de 2º turno nas pesquisas finais, ajustados por house effect, são a melhor base. A matriz de transferência dos eliminados deve vir dos cenários de 2º turno cruzados com o voto de 1º turno e da rejeição (quem rejeita X não migra para X). A rejeição funciona como teto aproximado: o teto de X ≈ 100% − rejeição de X, em válidos.

### Cited Findings
- 2018 2ºT: finais Datafolha 55 × 45, Ibope 54 × 46, resultado 55,1 × 44,9. — [Poder360](https://www.poder360.com.br/eleicoes/ibope-bolsonaro-54-x-46-haddad-datafolha-bolsonaro-55-x-45-haddad/)
- 2022 2ºT: agregador Estadão Lula 52 contra 50,9 real. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)
- 2022: a rejeição de Lula era maior que a de Bolsonaro entre indecisos (39,9% contra 32,1%) e na terceira via (39,1% contra 26,8%), o que explica a transferência desproporcional para Bolsonaro. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)
- Na amostra experimental de terceira via e indecisos de 2022: 29% Ciro, 24% Tebet, 5% outros, 12% branco ou nulo, 23% indecisos, 7% abstenção. — [Pereira & Nunes 2024](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf)

### Inferências
- Matriz T (k eliminados × {A, B, branco/nulo/abstenção}): cada linha ~ Dirichlet(α·p̂). p̂ vem dos cruzamentos de 1ºT × 2ºT das pesquisas. A concentração α ≈ 20–50 reflete a incerteza. Calibração com 2022 (inferência a partir do resultado agregado: Lula foi de 48,4 para 50,9 e Bolsonaro de 43,2 para 49,1 em válidos): os votos de Tebet, Ciro e outros (~8,4 p.p.) se dividiram com vantagem para Bolsonaro, junto com mudanças de comparecimento. Não é um caso de transferência "à esquerda".
- Simulação conjunta: cada simulação gera os resultados de 1ºT, define os dois primeiros (o par pode variar entre simulações), aplica T e soma o erro nacional do 2ºT (σ menor e correlacionado com o erro do 1ºT, ρ ≈ 0,3–0,5, já que o viés anti-PT foi persistente no 1ºT mas não no 2ºT).
- Teto pela rejeição: truncar ou penalizar as simulações em que um candidato supere 100 − rejeição (em válidos, ajustada pela rejeição a ambos), com folga de ~2–3 p.p. A rejeição medida também carrega house effect.

### Gaps
- Não encontrei uma matriz de transferência 2018 (Ciro → Haddad/Bolsonaro) publicada de forma citável. Pode ser estimada com inferência ecológica por município (pacotes `eiPack`/`ei` em R ou o método de King) com os dados do TSE de 1ºT e 2ºT.

## 5. Implementação computacional, fontes de dados, apresentação e armadilhas

### Takeaway
500 mil simulações × 27 UFs × ~5 candidatos cabem em memória com NumPy vetorizado (~67 milhões de floats, ~0,5 GB em float64, menos em float32 ou em lotes). As fontes primárias são os dados abertos do TSE (resultados por UF e município), o PesqEle (registro de pesquisas) e o banco de pesquisas do Poder360. As principais armadilhas: excesso de confiança (ignorar o viés comum), contar duas vezes pesquisas do mesmo instituto, herding, pesos de pesquisa desatualizados, e tratar votos totais e válidos como iguais.

### Cited Findings
- O PesqEle (TSE) disponibiliza o registro das pesquisas e mostra que os institutos não mudaram a metodologia entre os turnos de 2022. — [Pereira & Nunes 2024, nota 7](https://www.scielo.br/j/op/a/PTRgFK6cD9yfxPzFsssNFZh/?lang=pt&format=pdf) (https://pesqele-divulgacao.tse.jus.br/app/pesquisa/listar.xhtml)
- O banco do Poder360 forneceu 871 das 6.062 pesquisas do Pindograma. Código e dados do Pindograma são abertos no GitHub. — [Pindograma](https://pindograma.com.br/2020/09/07/ranking.html); [Pindograma 2022](https://pindograma.com.br/2022/06/24/rankingat.html)
- Resultados oficiais por UF: [TSE resultados](https://resultados.tse.jus.br/oficial/app/index.html) (citado por Pereira & Nunes).
- Herding e dispersão: a vantagem dos três grandes caiu para 0,19 p.p., o que mostra convergência de desempenho mas não independência dos erros. Em 2022 todos erraram na mesma direção. — [Pindograma](https://pindograma.com.br/2022/09/05/desempenho-pesquisas-22.html); [CNN Brasil](https://www.cnnbrasil.com.br/politica/resultados-das-urnas-divergem-de-pesquisas-eleitorais/)

### Inferências
- **Código (esqueleto):**
  - `rng = np.random.default_rng(seed)`.
  - Erros nacionais t-multivariados: `Z = rng.standard_normal((N, k)) @ L_nac.T`, `g = rng.chisquare(ν, (N,1))/ν`, `e = Z/np.sqrt(g)`.
  - Erro estadual: `Z_s = rng.standard_normal((N, 27)) @ L_estados.T`, com L de Cholesky da matriz de covariância com shrinkage.
  - Por candidato, use tensor (N, 27, k) em float32 e processe em lotes de 50–100 mil.
  - Converta de ALR para participações por softmax.
  - Vencedor do 1ºT: soma ponderada por eleitorado de válidos esperado de cada UF (comparecimento × (1 − brancos/nulos) × aptos, com aptos do TSE 2026). Calcule a probabilidade de vitória no 1ºT (válidos > 50%), as probabilidades de cada par no 2ºT e o 2ºT via matriz T.
  - Tudo vetorizado: `np.argmax`, `np.sort` no eixo de candidatos.
  - Erro de Monte Carlo com 500 mil simulações: para p=0,5, SE ≈ 0,07 p.p., bem mais que suficiente.
- **Apresentação:** probabilidade de vitória (e de decisão no 1ºT) arredondada (por exemplo, "7 em 10"); histograma ou densidade do % de válidos nacional com o intervalo de 80/95%; mapa coroplético por UF com P(vencer na UF) e margem mediana; gráfico de "caminhos" (par do 2ºT); tabela de cenários com e sem o viés anti-PT histórico.
- **Armadilhas:**
  1. Excesso de confiança: o erro amostral (±2 p.p. com n=2.000) é pequeno perto do erro não amostral (5–8 p.p. no candidato no 1ºT). Calibre a cobertura com backtest 2014–2022: os intervalos de 90% precisam conter os resultados reais.
  2. Contagem dupla: a mesma pesquisa divulgada por vários veículos, ou cortes regionais/UF da mesma amostra nacional. Deduplique pelo número de registro no TSE (BR-xxxxx/ano e UF-xxxxx/ano).
  3. Herding: institutos convergindo na véspera. Não trate as pesquisas como independentes e inclua o erro comum.
  4. Pesos amostrais com base no Censo 2010 ou na PNAD antiga contra o Censo 2022: diferença de composição religiosa e etária.
  5. Misturar votos totais e válidos. Exemplo: "Datafolha 36% contra 43,2%" compara bases diferentes, e em válidos o Datafolha de 2022 deu 36 contra o real 43,2. Em 2018, "36% total" equivalia a "40% válido".
  6. Pesquisas estaduais de presidente vêm de institutos menores, com amostras pequenas e possíveis vieses regionais fortes. Infle σ_estado.
  7. Ponderação por rating histórico: quase não ajuda no Brasil (r=0,03).
  8. Comunicação: deixar claro que 80% não é certeza, e mostrar o cenário "pesquisas erram como em 2014/2018/2022".

### Gaps
- Não verifiquei a API atual do Poder360 (agregador/banco de pesquisas 2026) nem o formato do CSV de 2026 do PesqEle e do dadosabertos.tse.jus.br.
- Sem dados de eleitorado apto 2026 por UF nesta nota (ver estatísticas do eleitorado no TSE).
- Não pesquisei pesquisas de 2026 nem house effects observados no ciclo de 2026. Os resultados de busca mencionaram pesquisas AtlasIntel e Paraná Pesquisas de governador na BA em 2026 ([JGB](https://jornalgrandebahia.com.br/2026/10/atlasintel-que-antecipou-lideranca-de-jeronimo-em-2022-registra-515-dos-votos-validos-nas-eleicoes-2026-parana-aponta-503-para-acm-neto)), mas isso está fora do escopo desta nota.
