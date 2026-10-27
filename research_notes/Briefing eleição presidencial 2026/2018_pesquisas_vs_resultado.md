# Eleição presidencial de 2018: últimas pesquisas vs. resultado oficial (TSE), por candidato e por UF, e por que as pesquisas erraram

Notas de pesquisa para calibrar o erro de um simulador Monte Carlo. Convenção: "válidos" = excluindo brancos, nulos e indecisos (o mesmo critério do TSE). "Erro" = pesquisa − resultado, em pontos percentuais (p.p.). Erro negativo = candidato subestimado.

## 1. Últimas pesquisas nacionais vs. TSE (1º e 2º turno)

### Takeaway
No 1º turno, Datafolha e Ibope (véspera, 5 e 6/out) **subestimaram os dois primeiros colocados ao mesmo tempo** (Bolsonaro −5 a −6 p.p., Haddad cerca de −4,3 p.p.) e **superestimaram os candidatos menores** (Alckmin +3,2, Marina +2, Ciro +0,5 a +2,5). A **margem** Bolsonaro−Haddad, porém, saiu quase certa (15–16 p.p. projetados contra 16,75 reais). O padrão combina com concentração tardia de votos (voto útil) nos dois candidatos que lideravam. No 2º turno as duas pesquisas acertaram dentro da margem: Datafolha 55/45 contra 55,13/44,87.

### Cited Findings
**Resultado oficial do 1º turno (7/out/2018), % dos válidos** — [Wikipedia: 2018 Brazilian general election](https://en.wikipedia.org/wiki/2018_Brazilian_general_election)
- Bolsonaro 46,03 (49.277.010 votos); Haddad 29,28 (31.342.051); Ciro 12,47; Alckmin 4,76; Amoêdo 2,50; Cabo Daciolo 1,26; Meirelles 1,20; Marina 1,00; Alvaro Dias 0,80; Boulos 0,58; Vera 0,05; Eymael 0,04; Goulart Filho 0,03.
- Votos válidos: 107.050.749. Brancos e nulos: 10.313.159 (8,79% dos votos). Comparecimento: 79,67%, logo abstenção de cerca de 20,3%.

**Resultado oficial do 2º turno (28/out/2018)** — [Wikipedia](https://en.wikipedia.org/wiki/2018_Brazilian_general_election)
- Bolsonaro 55,13% (57.797.847); Haddad 44,87% (47.040.906). Brancos e nulos: 9,57%. Comparecimento: 78,70%.

**Datafolha da véspera do 1º turno** (5–6/out, n=19.552, 382 municípios, margem de ±2) — [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2018-10/pesquisa-datafolha-para-presidente)
- Válidos: Bolsonaro 40, Haddad 25, Ciro 15, Alckmin 8, Marina 3, Amoêdo 3, Alvaro Dias 2, Meirelles 2, Boulos 1, Daciolo 1.
- Totais: Bolsonaro 36, Haddad 22, Ciro 13, Alckmin 7, Marina 3, Amoêdo 3, Dias 2, Meirelles 2. Brancos e nulos 6, indecisos 4.
- Simulações de 2º turno: Bolsonaro 45 x Haddad 43; Ciro 47 x Bolsonaro 43; Bolsonaro 43 x Alckmin 41.

**Ibope da véspera do 1º turno** (5–6/out, n=3.010, ±2; TV Globo e Estadão) — [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2018-10/pesquisa-ibope-para-presidente-da-republica)
- Válidos: Bolsonaro 41, Haddad 25, Ciro 13, Alckmin 8, Marina 3, Amoêdo 3, Meirelles 2, Daciolo 2, Dias 2, Boulos 1.
- Totais: Bolsonaro 36, Haddad 22, Ciro 11, Alckmin 7, Marina 3; brancos e nulos 7; indecisos 5.
- Simulação de 2º turno: Bolsonaro 45 x Haddad 41; Ciro 45 x Bolsonaro 41.

**Boca de urna do Ibope (7/out)**: Bolsonaro 45, Haddad 28 (válidos, ±2). Ficou dentro da margem do resultado (46/29) — [Aos Fatos](https://www.aosfatos.org/noticias/postagens-distorcem-resultados-para-dizer-que-ibope-e-datafolha-erraram-em-2018/)

**Erros calculados (pesquisa de véspera, válidos, menos o TSE):**

| Candidato | TSE | Datafolha | Erro DF | Ibope | Erro Ibope |
|---|---|---|---|---|---|
| Bolsonaro | 46,03 | 40 | −6,0 | 41 | −5,0 |
| Haddad | 29,28 | 25 | −4,3 | 25 | −4,3 |
| Ciro | 12,47 | 15 | +2,5 | 13 | +0,5 |
| Alckmin | 4,76 | 8 | +3,2 | 8 | +3,2 |
| Marina | 1,00 | 3 | +2,0 | 3 | +2,0 |
| Amoêdo | 2,50 | 3 | +0,5 | 3 | +0,5 |
| Meirelles | 1,20 | 2 | +0,8 | 2 | +0,8 |
| A. Dias | 0,80 | 2 | +1,2 | 2 | +1,2 |
| Daciolo | 1,26 | 1 | −0,3 | 2 | +0,7 |
| Boulos | 0,58 | 1 | +0,4 | 1 | +0,4 |
| Margem B−H | 16,75 | 15 | −1,75 | 16 | −0,75 |

- Erro absoluto médio nos 5 principais candidatos: Datafolha cerca de 3,6 p.p.; Ibope cerca de 3,0 p.p. Nos 10 candidatos: Datafolha cerca de 2,1; Ibope cerca de 1,9. Cálculos próprios a partir das fontes acima.
- O Aos Fatos resume o desvio como "5 a 6 pontos" para Bolsonaro e cerca de 4 para Haddad — [Aos Fatos](https://www.aosfatos.org/noticias/postagens-distorcem-resultados-para-dizer-que-ibope-e-datafolha-erraram-em-2018/)

**Outros institutos, última semana do 1º turno (votos TOTAIS, não válidos)** — [Wikipedia: Opinion polling 2018](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2018_Brazilian_presidential_election)
- Instituto Veritá (2–5/out, n=5.208): Bolsonaro 41,5; Haddad 18,8; Ciro 8,4; Alckmin 4,2; Marina 1,4. Foi o único com Bolsonaro acima de 40% nos totais, o que é compatível com mais de 45% dos válidos.
- CNT/MDA (4–5/out, n=2.002): Bolsonaro 36,7; Haddad 24,0; Ciro 9,9; Alckmin 5,8; Marina 2,2.
- DataPoder360 (3–4/out, n=4.000): Bolsonaro 30; Haddad 25; Ciro 15; Alckmin 7; Marina 2. Foi o que mais subestimou Bolsonaro.
- XP/Ipespe (3–4/out, n=2.000): Bolsonaro 36; Haddad 22; Ciro 11; Alckmin 8; Marina 4.
- Datafolha (3–4/out) 36/22/13/7/3; Ibope (1–2/out) 36/22/11/7/3.

**2º turno: pesquisas da véspera**
- Datafolha (26–27/out, n=18.371, 340 municípios, ±2): Bolsonaro 55 x Haddad 45 nos válidos. Erro de −0,1/+0,1 — [Poder360 (título)](https://www.poder360.com.br/eleicoes/ibope-bolsonaro-54-x-46-haddad-datafolha-bolsonaro-55-x-45-haddad/); [O Povo](https://www.opovo.com.br/noticias/politica/2018/10/pesquisa-presidente-2-turno-haddad-bolsonaro-sabado-27-outubro-27-10.html)
- Ibope (26–27/out, n=3.010, ±2): Bolsonaro 54 x Haddad 46 nos válidos. Erro de −1,1/+1,1 — [Seu Dinheiro](https://www.seudinheiro.com/2018/politica/ibope-bolsonaro-tem-54-dos-votos-validos-e-haddad-46/)
- Trajetória do Datafolha no 2º turno: a primeira pesquisa (cerca de 10/out) deu 58 x 42, e a margem caiu até 55 x 45 na véspera — [Metrópoles](https://www.metropoles.com/brasil/eleicoes-2018/datafolha-no-2o-turno-bolsonaro-tem-58-e-haddad-42)

### Inferences
- Para calibrar o simulador: em 2018 o erro de 1º turno foi **correlacionado e estrutural**, não ruído de amostragem. Com n=19.552, a margem do Datafolha seria de cerca de ±0,7 p.p. por candidato, e o erro em Bolsonaro foi cerca de 8 vezes maior. A soma dos erros dos dois líderes (cerca de −10 p.p.) foi compensada pelos menores (+10 p.p.). Isso sugere modelar um choque de "concentração nos líderes", com a margem entre eles preservada.
- O erro foi bem menor no 2º turno (|erro| ≤ 1,1 p.p.), quando há menos espaço para voto útil.
- A mesma direção se repetiu em 2022 (Bolsonaro subestimado em cerca de 8 p.p. nos totais segundo o agregador do Estadão), o que indica viés persistente ou mecanismo recorrente — [Pereira & Nunes, Opinião Pública 2024](https://www.redalyc.org/journal/329/32977806001/32977806001.pdf)

### Gaps
- Não encontrei os números em votos válidos das últimas pesquisas de Paraná Pesquisas, Vox Populi, Ideia Big Data e MDA para o 1º turno, nem as finais desses institutos para o 2º turno. A fonte da Wikipedia só traz totais. A página do Poder360 retornou 403.

## 2. Pesquisas estaduais vs. resultado (presidente, governador, Senado)

### Takeaway
O erro estadual foi muito maior que o nacional e se concentrou no Sudeste. Em SP, o Ibope da véspera deu Bolsonaro com 41% dos válidos, e ele teve 53% (−12 p.p.). Nos governos, candidatos "outsiders" alinhados a Bolsonaro saltaram do 3º lugar nas pesquisas para o 1º lugar: Witzel no RJ, de 12% para 41%, e Zema em MG. Nomes do PT que lideravam as pesquisas para o Senado ficaram fora: Dilma em MG terminou em 4º, e Suplicy em SP terminou em 3º.

### Cited Findings
**Presidente em SP, Ibope de 4–6/out (n=2.002, ±2), válidos**: Bolsonaro 41, Haddad 19, Alckmin 14, Ciro 11, Amoêdo 5, Marina 3, Daciolo 2, Meirelles 2. Totais: Bolsonaro 35, Haddad 16, Alckmin 12, Ciro 9 — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2018/10/06/interna_politica,994856/ibope-em-sp-bolsonaro-tem-41-haddad-19-ciro-11.shtml)
- Resultado em SP: Bolsonaro 53,00; Haddad 16,42; Ciro 11,35 — [Wikipedia PT: Resultados por estado](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018). Erros calculados: Bolsonaro −12,0; Haddad +2,6; Ciro −0,35. O valor de Alckmin em SP não aparece na fonte.

**Presidente em MG, 2º turno**: o Ibope de 15–17/out dava Bolsonaro com 62% dos válidos — [Gazeta do Povo](https://especiais.gazetadopovo.com.br/eleicoes/2018/pesquisas-eleitorais/ibope/ibope-bolsonaro-tem-62-dos-votos-validos-em-minas-gerais/). O resultado foi 58,19% ([Wikipedia PT](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018)). A pesquisa foi feita cerca de 11 dias antes, então a diferença não equivale a erro de véspera.

**Governador do RJ**
- Ibope da véspera, válidos: Paes 32, Romário 20, Witzel 12. Resultado do 1º turno: Witzel 41,28 (erro de cerca de −29 p.p.) — [Wikipedia, via busca](https://en.wikipedia.org/wiki/2018_Rio_de_Janeiro_gubernatorial_election). Outra versão da mesma página cita Ibope com Paes 26, Romário 19, Witzel 7, provavelmente votos totais ou uma rodada anterior. **Divergência entre fontes.**
- A boca de urna deu Witzel com 39%, e no Ibope de 6/out ele estava empatado em 3º com 12% — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/26/interna_politica,1398068/pesquisas-eleitorais-erraram-tudo-em-2018-como-diz-bolsonaro.shtml)
- 2º turno: Ibope Witzel 45 x Paes 38 e Datafolha 44 x 40, provavelmente em votos totais. Resultado: Witzel 59,87 x Paes 40,13 — [Wikipedia](https://en.wikipedia.org/wiki/2018_Rio_de_Janeiro_gubernatorial_election). Outra fonte traz um Ibope de 2º turno com Witzel 60 x Paes 40 nos válidos — [Gazeta do Povo](https://especiais.gazetadopovo.com.br/eleicoes/2018/pesquisas-eleitorais/ibope/ibope-pesquisa-governo-rj-segundo-turno-rio-de-janeiro/)

**Governador de MG**: Zema aparecia em 3º nas pesquisas finais — [Estado de Minas, 2022](https://www.em.com.br/app/noticia/politica/2022/09/29/interna_politica,1399802/por-que-pesquisas-nao-previram-surpresas-em-2018-como-dilma-witzel-e-zema.shtml). Resultado do 1º turno: Zema 42,73; Anastasia 29,06; Pimentel 23,12. No 2º turno, Zema teve 71,80 x Anastasia 28,20 — [Wikipedia](https://en.wikipedia.org/wiki/2018_Minas_Gerais_gubernatorial_election)

**Senado em MG, pesquisas de 4–6/out**: Ibope com Dilma 26, Viana 19, Pacheco 18, Dinis 16; Datafolha com Dilma 28, Pacheco 19, Viana 17, Dinis 15. A fonte também lista uma série menor: Ibope 20/14/14/12 e Datafolha 23/15/14/12. Os rótulos "válidos" e "totais" parecem trocados na fonte, porque cada eleitor tinha 2 votos para o Senado — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2018/10/06/interna_politica,994841/confira-pesquisas-ibope-e-datafolha-para-o-senado-em-minas.shtml). Dilma liderou durante toda a campanha e terminou em 4º. Pacheco e Viana foram eleitos — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/29/interna_politica,1399802/por-que-pesquisas-nao-previram-surpresas-em-2018-como-dilma-witzel-e-zema.shtml)
- Uma pesquisa do Ibope em MG registrava 31% de indecisos para o Senado — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/26/interna_politica,1398068/pesquisas-eleitorais-erraram-tudo-em-2018-como-diz-bolsonaro.shtml)

**Senado em SP**: Eduardo Suplicy (PT) liderou as pesquisas e terminou em 3º — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/29/interna_politica,1399802/por-que-pesquisas-nao-previram-surpresas-em-2018-como-dilma-witzel-e-zema.shtml)

**Resultado presidencial por UF (válidos, TSE via Wikipedia PT)** — [Wikipedia PT](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018)

| UF | 1T Bolsonaro | 1T Haddad | 1T Ciro | 2T Bolsonaro | 2T Haddad | Abst. 1T | Abst. 2T |
|---|---|---|---|---|---|---|---|
| AC | 62,24 | 18,53 | 5,17 | 77,22 | 22,78 | 18,99 | 27,11 |
| AL | 34,40 | 44,75 | 10,12 | 40,08 | 59,92 | 22,60 | 24,83 |
| AP | 40,74 | 32,77 | 12,34 | 50,20 | 49,80 | 16,70 | 22,88 |
| AM | 43,48 | 40,30 | 7,50 | 50,27 | 49,73 | 19,35 | 21,39 |
| BA | 23,41 | 60,28 | 9,41 | 27,31 | 72,69 | 20,74 | 21,09 |
| CE | 21,74 | 33,12 | 40,95 | 28,89 | 71,11 | 17,33 | 18,69 |
| DF | 58,37 | 11,87 | 16,60 | 69,99 | 30,01 | 18,70 | 18,92 |
| ES | 54,76 | 24,20 | 9,54 | 63,06 | 36,94 | 19,26 | 20,91 |
| GO | 57,24 | 21,86 | 8,60 | 65,52 | 34,48 | 20,19 | 21,61 |
| MA | 24,28 | 61,26 | 8,39 | 26,74 | 73,26 | 20,54 | 23,35 |
| MT | 60,04 | 24,76 | 5,59 | 66,42 | 33,58 | 24,55 | 26,23 |
| MS | 55,06 | 23,87 | 8,04 | 65,22 | 34,78 | 21,22 | 22,78 |
| MG | 48,31 | 27,65 | 11,64 | 58,19 | 41,81 | 22,19 | 23,13 |
| PA | 36,19 | 41,39 | 10,03 | 45,19 | 54,81 | 19,95 | 23,29 |
| PB | 31,30 | 45,46 | 16,75 | 35,02 | 64,98 | 15,03 | 16,07 |
| PE | 30,57 | 48,87 | 13,56 | 33,50 | 66,50 | 17,90 | 18,14 |
| PR | 56,89 | 19,70 | 8,31 | 68,43 | 31,57 | 16,96 | 17,26 |
| PI | 18,76 | 63,40 | 11,42 | 22,95 | 77,05 | 15,71 | 17,86 |
| RJ | 59,79 | 14,69 | 15,22 | 67,95 | 32,05 | 23,59 | 24,06 |
| RN | 30,21 | 41,19 | 22,31 | 36,59 | 63,41 | 17,11 | 18,14 |
| RS | 52,63 | 22,81 | 11,37 | 63,24 | 36,76 | 18,14 | 18,87 |
| RO | 62,24 | 20,36 | 6,03 | 72,18 | 27,82 | 22,31 | 24,96 |
| RR | 62,97 | 17,85 | 5,36 | 71,55 | 28,45 | 13,92 | 18,86 |
| SC | 65,82 | 15,13 | 6,68 | 75,92 | 24,08 | 16,30 | 16,87 |
| SP | 53,00 | 16,42 | 11,35 | 67,97 | 32,03 | 21,52 | 21,78 |
| SE | 27,21 | 50,09 | 13,02 | 32,46 | 67,54 | 18,82 | 19,81 |
| TO | 44,64 | 41,12 | 7,17 | 48,98 | 51,02 | 19,98 | 24,84 |

Regiões, na ordem 1T Bolsonaro/Haddad/Ciro e depois 2T Bolsonaro/Haddad: Norte 43,4/36,8/8,6 e 51,9/48,1; Nordeste 25,9/50,6/17,0 e 30,3/69,7; Centro-Oeste 57,7/20,8/9,5 e 66,6/33,5; Sudeste 53,2/19,2/12,1 e 65,4/34,6; Sul 57,4/19,8/9,1 e 68,3/31,7 — [Wikipedia PT](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018). Observação: o CE foi a única UF vencida por Ciro no 1T (40,95). Na fonte, os percentuais do 1T por UF podem estar em base de válidos; a fonte não deixa explícito.

### Inferences
- O erro nacional de cerca de −5,5 em Bolsonaro parece ter sido puxado pelo Sudeste (SP −12 no Ibope estadual), onde Alckmin e outros candidatos de centro-direita tinham mais votos para perder. Para o simulador, faz sentido usar variância de erro maior por UF e choque regional correlacionado, com SP/RJ/MG mais expostos a migração tardia da centro-direita.
- Disputas estaduais tinham muito mais indecisos que a presidencial. Em 2022, por exemplo, a certeza de voto ficava em 50–69% para governador contra 79–83% para presidente, segundo Ipec/Quaest — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/29/interna_politica,1399802/por-que-pesquisas-nao-previram-surpresas-em-2018-como-dilma-witzel-e-zema.shtml). Isso torna os erros de governador e Senado tipicamente 2 a 5 vezes maiores.

### Gaps
- Não obtive as pesquisas finais Ibope/Datafolha de presidente nas 27 UFs, então não é possível montar a tabela completa de erro por estado. Recomendo buscar no arquivo da Gazeta do Povo, que tem uma página por UF por instituto (por exemplo, [SP](https://especiais.gazetadopovo.com.br/eleicoes/2018/pesquisas-eleitorais/ibope/ibope-presidente-sp-sao-paulo/) e [RJ](https://especiais.gazetadopovo.com.br/eleicoes/2018/pesquisas-eleitorais/rj)).
- Faltam os percentuais oficiais do Senado em MG e SP (Pacheco, Viana, Dinis, Dilma; Major Olímpio, Mara Gabrilli, Suplicy) com fonte verificada.
- O ranking do Pindograma (2012–2018) explica a metodologia, com erro medido pelo desvio-padrão das diferenças com sinal, mas a página não trouxe o erro médio por instituto nem por ano. O exemplo citado é uma disputa de governador em MG com erro ajustado de 12,7 p.p. — [Pindograma](https://pindograma.com.br/2020/09/07/ranking.html)

## 3. Explicações para os erros (concorrentes, algumas contestadas)

### Takeaway
A explicação mais documentada é a de **mudança tardia de voto**: voto útil de eleitores de Alckmin, Marina e Ciro e alinhamento de indecisos nas últimas 24–48h, além de uma "onda" antipolítica que levou junto candidatos alinhados a Bolsonaro nos estados. A boca de urna acertando, enquanto a pesquisa de véspera errava, é consistente com essa tese. Explicações técnicas (cotas desatualizadas pelo Censo 2010, abstenção diferencial, recusas e "voto envergonhado") são citadas na literatura, mas com evidência mais fraca para 2018. O debate segue em aberto.

### Cited Findings
- Na véspera, Ibope e Datafolha erraram 5 a 6 p.p. em Bolsonaro, mas a boca de urna do Ibope acertou (45/28 contra 46/29). Isso indica mudança entre sábado e domingo, ou erro de pesquisa domiciliar que a boca de urna não tem — [Aos Fatos](https://www.aosfatos.org/noticias/postagens-distorcem-resultados-para-dizer-que-ibope-e-datafolha-erraram-em-2018/)
- Especialistas citados pelo Estado de Minas atribuem as surpresas a uma onda bolsonarista e antipolítica forte nas últimas 24–48h, que beneficiou desconhecidos alinhados a Bolsonaro, e à alta indecisão nas disputas estaduais — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/26/interna_politica,1398068/pesquisas-eleitorais-erraram-tudo-em-2018-como-diz-bolsonaro.shtml); [Terra](https://www.terra.com.br/noticias/brasil/dilma-witzel-e-zema-por-que-pesquisas-nao-previram-surpresas-nas-urnas-em-2018,a630f88d4fe8c7f959e2383c27ceb079eljqoen5.html)
- Raphael Nishimura (Univ. de Michigan): pesquisas captam "o momento em que foram coletadas". Emerson Cervi (UFPR): para governador e Senado, o eleitor decide "na última hora" — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/29/interna_politica,1399802/por-que-pesquisas-nao-previram-surpresas-em-2018-como-dilma-witzel-e-zema.shtml)
- Pereira & Nunes (Opinião Pública, v.30, 2024) afirmam que em 2014 e 2018 as pesquisas da última semana também divergiram do resultado. Segundo eles, o voto estratégico e o alinhamento de indecisos são mecanismos plausíveis. Citando Plutowski, Weitz-Shapiro & Winters (2021), registram que "nas eleições de 2018, o tipo mais comum de voto estratégico foi o deslocamento de votos dos candidatos menos competitivos para os mais competitivos". Os autores também listam as explicações técnicas rivais (vieses de amostragem, recusas, captação inadequada da abstenção) e as tratam como alternativa debatida — [Pereira & Nunes 2024](https://www.redalyc.org/journal/329/32977806001/32977806001.pdf)
- A crítica de que as pesquisas "erraram tudo" em 2018, feita por Bolsonaro e apoiadores em 2022, em parte compara votos totais das pesquisas com votos válidos do TSE. Segundo checagem do Aos Fatos, isso infla o erro aparente — [Aos Fatos](https://www.aosfatos.org/noticias/postagens-distorcem-resultados-para-dizer-que-ibope-e-datafolha-erraram-em-2018/). As simulações de 2º turno feitas no 1º turno (Bolsonaro 45 x Haddad 43 no Datafolha, contra 55 x 45 depois) são hipotéticas segundo os institutos, mas são citadas pelos críticos como erro — [Estado de Minas](https://www.em.com.br/app/noticia/politica/2022/09/26/interna_politica,1398068/pesquisas-eleitorais-erraram-tudo-em-2018-como-diz-bolsonaro.shtml)

### Inferences
- O padrão "líderes subestimados, nanicos superestimados, margem correta" é a assinatura esperada de voto útil tardio. Um erro de cobertura amostral contra eleitores de Bolsonaro tenderia a afetar só ele, e não Haddad também. Isso favorece a tese de mudança tardia para 2018, mas não exclui viés de amostragem. A repetição em 2022 reabriu o debate.
- Quanto a WhatsApp e desinformação, "voto envergonhado", cotas pelo Censo 2010/PNAD e a facada de 6/set como causa do erro final: não encontrei, nesta rodada, estudo quantitativo que meça o efeito específico de cada fator sobre o erro de 2018. São hipóteses circulantes, não quantificadas aqui.

### Gaps
- Não localizei entrevistas de 2018 de Mauro Paulino (Datafolha) ou Márcia Cavallari (Ibope) explicando o erro, nem documentação sobre a defasagem de cotas pelo Censo 2010 aplicada a 2018. É preciso buscar no acervo da Folha e do Estadão (paywall).
- Não há aqui evidência sobre pesquisas telefônicas/IVR contra presenciais em 2018. O Veritá, que chegou mais perto em Bolsonaro, usa metodologia própria pouco documentada.

## 4. Evolução das pesquisas em 2018

### Takeaway
Com Lula no cenário, ele liderava com cerca de 30–31% contra cerca de 15–17% de Bolsonaro. Sem Lula, Bolsonaro liderava com 17–19% e Marina vinha em 2º com cerca de 15%. Depois da facada (6/set) e da troca de Lula por Haddad (11/set), Bolsonaro subiu para cerca de 26–28% e Haddad saiu de cerca de 6% para 22–25% em três semanas, com Marina desabando.

### Cited Findings
Todos os números são votos totais, de acordo com a [Wikipedia: Opinion polling 2018](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2018_Brazilian_presidential_election).
- Datafolha de 9–13/abr (após a prisão de Lula, n=4.260). Com Lula: Lula 31, Bolsonaro 15, Marina 10, Alckmin 6, Ciro 5. Sem Lula: Bolsonaro 17, Marina 15, Ciro 9, Alckmin 7, Haddad 2.
- Datafolha de 6–7/jun (n=2.824). Com Lula: Lula 30, Bolsonaro 17, Marina 10, Ciro 6, Alckmin 6. Sem Lula: Bolsonaro 19, Marina 15, Ciro 10, Alckmin 7, Haddad 1.
- FSB de 1–2/set: Bolsonaro 26, Ciro 12, Marina 11, Alckmin 8, Haddad 6. A pesquisa foi feita antes da facada, apesar do rótulo "post-stabbing" no resumo da fonte.
- Datafolha de 13–14/set (logo após Haddad substituir Lula): Bolsonaro 26, Haddad 13, Ciro 13, Alckmin 9, Marina 8.
- Na semana final (1–4/out): Bolsonaro 36, Haddad 22, Ciro 11–13, Alckmin 7, Marina 3 (Datafolha e Ibope).

### Inferences
- A transferência de votos de Lula para Haddad foi rápida, de cerca de 6 para 22 em 3 semanas. A queda de Marina (de cerca de 15 para 1 no resultado) e de Alckmin (de cerca de 9 para 4,8) foi contínua e continuou depois da última pesquisa. Isso é compatível com a migração final que as pesquisas não captaram.

### Gaps
- Não coletei a série de rejeição (o "não votaria de jeito nenhum") nem o efeito medido do #EleNão (29/set). Pelo que lembro sem fonte nesta rodada, a rejeição de Bolsonaro e a de Haddad estavam ambas em torno de 40–45% no fim de setembro e início de outubro; esse número precisa ser verificado.

## 5. Abstenção, brancos e nulos: 2018 vs. 2014

### Takeaway
A abstenção subiu: cerca de 20,3% no 1T de 2018 e 21,3% no 2T, a maior desde 1998. Brancos e nulos também cresceram (9,6% no 2T de 2018 contra 6,3% no 2T de 2014).

### Cited Findings
- 2T de 2018: abstenção de 21,3% (31,37 milhões); brancos 2,14%; nulos 7,43% — [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2018-10/taxa-de-abstencao-na-eleicao-presidencial-e-maior-desde-1998). Abstenção histórica: 1994 29,3; 1998 21,5; 2002 17,7; 2006 16,8; 2010 18,1; 2014 19,4; 2018 21,3 (mesma fonte).
- 2T de 2014: brancos 1,71% (1,92 milhão) e nulos 4,63% (5,21 milhões). Mais de 42 milhões de eleitores (cerca de 30%) se abstiveram, anularam ou votaram em branco no 2T de 2018 — [Conjur](https://www.conjur.com.br/2018-out-29/31-milhoes-eleitores-nao-votaram-segundo-turno/)
- 1T de 2018: comparecimento de 79,67% (abstenção de cerca de 20,3%); brancos e nulos somaram 8,79% — [Wikipedia](https://en.wikipedia.org/wiki/2018_Brazilian_general_election)
- Creomar de Souza atribui a alta à polarização: "uma eleição muito polarizada expulsa os moderados" — [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2018-10/taxa-de-abstencao-na-eleicao-presidencial-e-maior-desde-1998)
- Abstenção por UF no 2T: máxima no AC (27,1%) e no MT (26,2%), mínima na PB (16,1%) e em SC (16,9%) — [Wikipedia PT](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018)

### Inferences
- A abstenção cresceu no Norte entre os turnos (AC de 19,0 para 27,1; TO de 20,0 para 24,8; AP de 16,7 para 22,9). Para o simulador, isso indica que modelar o comparecimento por UF e por turno tem impacto não trivial.

### Gaps
- O valor de 19,4% atribuído a 2014 pela Agência Brasil confere com a abstenção do 1T de 2014. Pelo que lembro, a do 2T de 2014 foi de cerca de 21,1%, o que deixaria a comparação de 2T inconsistente na fonte. Convém verificar no TSE.
- Não encontrei estudo que quantifique a abstenção diferencial por perfil de eleitor (renda, idade) como causa do erro das pesquisas em 2018.

## 6. Voto por região e por perfil demográfico

### Takeaway
Em 2018, Bolsonaro dominou Sul, Centro-Oeste e Sudeste (65–68% no 2T), e Haddad venceu o Nordeste com cerca de 70%. Segundo o Datafolha do 2T, Bolsonaro ia melhor entre homens, eleitores de maior renda e escolaridade e evangélicos. Haddad ia melhor entre os mais pobres e de menor escolaridade.

### Cited Findings
- Primeira pesquisa Datafolha do 2T (cerca de 10/out; total geral 58 x 42 nos válidos) — [Metrópoles](https://www.metropoles.com/brasil/eleicoes-2018/datafolha-no-2o-turno-bolsonaro-tem-58-e-haddad-42):
  - Gênero: Bolsonaro com 42% dos votos totais entre mulheres e 57% entre homens.
  - Renda e escolaridade: Bolsonaro com 62% na faixa de 5 a 10 salários mínimos ou mais e 58% entre quem tem ensino superior. Haddad com 44% entre quem tem até o ensino fundamental e 44% entre quem ganha até 2 salários mínimos.
  - Religião: entre evangélicos, Bolsonaro 60 x Haddad 26.
- Regiões no 2T: Sul 68,3, Centro-Oeste 66,6, Sudeste 65,4, Norte 51,9 e Nordeste 30,3 para Bolsonaro — [Wikipedia PT](https://pt.wikipedia.org/wiki/Resultados_da_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018)

### Inferences
- Evangélicos (cerca de 30% do eleitorado, número não verificado nesta rodada) com margem de cerca de 34 p.p. a favor de Bolsonaro foram um dos maiores diferenciais segmentares. A clivagem Nordeste contra o resto (cerca de 40 p.p. de diferença) é o principal eixo geográfico.

### Gaps
- Não obtive a abertura demográfica da pesquisa de véspera nem de boca de urna (Ibope, 28/out), nem dados por cor/raça e idade. Também faltam os números de católicos.
