# Histórico TSE 2002–2022 por UF: lean do PT, swings, correlação entre estados e transferência de votos no 2º turno

**Fonte primária de todos os números abaixo:** dados abertos do TSE, arquivos `votacao_candidato_munzona_AAAA.zip` e `detalhe_votacao_munzona_AAAA.zip` (2002, 2006, 2010, 2014, 2018, 2022), baixados de `https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/` e `https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/` em 03/10/2026. O download funcionou; **não foi preciso usar a Wikipedia como alternativa**. Os zips brutos (cerca de 1,9 GB) foram apagados depois da agregação.

Links das fontes (todos usam o mesmo padrão):
- [TSE – votacao_candidato_munzona_2022.zip](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip) (e os mesmos arquivos para _2002, _2006, _2010, _2014, _2018)
- [TSE – detalhe_votacao_munzona_2022.zip](https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2022.zip) (idem para os outros anos)
- [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br)

## Métodos

### Takeaway
Os votos para presidente (CD_CARGO = 1) foram agregados de município/zona para UF. Os totais nacionais conferem exatamente com o resultado oficial; por exemplo, em 2022 foram 118.229.719 votos válidos no 1º turno e 118.552.353 no 2º.

### Cited Findings
- **Arquivo usado.** Para presidente, só o arquivo `*_BR.csv` dentro de cada zip traz os dados (os arquivos por UF trazem só cargos estaduais). O `*_BRASIL.csv` reúne todos os cargos e foi ignorado para não contar votos em dobro — [TSE votacao_candidato_munzona](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip)
- **Variáveis de comparecimento.** Saíram do `detalhe_votacao_munzona`:
  - eleitorado (QT_APTOS), comparecimento e abstenções;
  - votos válidos (QT_TOTAL_VOTOS_VALIDOS) e brancos (QT_VOTOS_BRANCOS);
  - nulos = QT_TOTAL_VOTOS_NULOS + QT_TOTAL_VOTOS_ANULADOS (o segundo é zero para presidente em todos os anos).
  - Os votos em trânsito foram incluídos (somados) — [TSE detalhe_votacao_munzona](https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2022.zip)
- **Exterior.** O voto no exterior (SG_UF = "ZZ") entra no total nacional ("BR"), como no resultado oficial. Fica fora das análises entre as 27 UFs.
- **Definições usadas nas contas:**
  - abstenção % = abstenções ÷ eleitorado;
  - branco % e nulo % = sobre o comparecimento;
  - PT % e oponente % = sobre os votos válidos.
- **Candidatos.** Candidato do PT: número 13. Oponente principal: 2º colocado nacional (Serra 2002/2010, Alckmin 2006, Aécio 2014, Bolsonaro 2018/2022). Os dois terceiros colocados do 1º turno estão em colunas próprias.
- **Lean (inclinação partidária).** lean = PT% de válidos na UF − PT% nacional (com exterior), no mesmo turno. Também foi calculada a versão bipartidária (PT/(PT+oponente)), igual à anterior no 2º turno.
- **Swing relativo.** Swing = lean(t) − lean(t−1), ou seja, o swing da UF menos o swing nacional. Há 5 pares de eleições.
- **Matrizes de correlação 27×27.** Pearson entre UFs, calculada sobre:
  - (i) os 5 swings do 2º turno (arquivo principal);
  - (ii) 10 observações: swings de 1º e 2º turno;
  - (iii) 8 observações pós-2006 (1º e 2º turno, sem o par 2002→2006).
- **Transferência ecológica.**
  - Método: regressão de Goodman (MQO sem intercepto, ponderada pelo eleitorado) em cerca de 5.570 municípios, sem o exterior.
  - Variáveis explicativas: frações do eleitorado no 1º turno (PT, oponente, terceiros, branco+nulo, abstenção).
  - Variáveis explicadas: frações no 2º turno (PT, oponente, branco+nulo, abstenção).
  - Duas versões: MQO livre e MQO com coeficientes limitados a [0,1] (scipy `lsq_linear`), depois renormalizados para cada linha somar 100%.
  - Rodada para Brasil, Nordeste e fora do Nordeste.

### Inferences
- Pelo desenho dos dados, a correlação de swings relativos tende a ter média próxima de zero: se umas UFs sobem em relação ao nacional, outras têm de cair. Correlações negativas entre regiões são, em parte, um efeito mecânico.
- Com apenas 4 a 10 observações por par de UFs, cada correlação individual é muito ruidosa (o erro-padrão de r com n = 5 é cerca de 0,5). Para o simulador, use a estrutura por bloco regional, não a matriz bruta.

### Gaps
- Não usei dados por seção eleitoral nem modelos ecológicos mais robustos (King EI, Rosen/MCMC). A regressão de Goodman é sabidamente sensível a viés de agregação.

## Resultados nacionais e por UF (resultados_uf_2002_2022.csv)

### Takeaway
O PT venceu o 2º turno em 2002 (61,27%), 2006 (60,83%), 2010 (56,05%), 2014 (51,64%) e 2022 (50,90%), e perdeu em 2018 (44,87%). A abstenção nacional ficou entre 16,8% e 21,5%. Em 2022 o 2º turno teve **menos** abstenção que o 1º (20,58% contra 20,95%), o que não aconteceu em nenhuma outra eleição.

### Cited Findings
Tabela nacional (TSE, agregação própria):

| Ano | Turno | Eleitorado | Abst. % | Branco % comp. | Nulo % comp. | PT % válidos | Oponente % válidos | 3º / 4º colocado (1º turno) |
|---|---|---|---|---|---|---|---|---|
| 2002 | 1 | 115.253.816 | 17,74 | 3,03 | 7,36 | Lula 46,44 | Serra 23,20 | Garotinho 17,87 / Ciro 11,97 |
| 2002 | 2 | 115.253.816 | 20,47 | 1,88 | 4,12 | Lula 61,27 | Serra 38,73 | |
| 2006 | 1 | 125.913.235 | 16,75 | 2,73 | 5,67 | Lula 48,61 | Alckmin 41,64 | Heloísa Helena 6,85 / Cristovam 2,64 |
| 2006 | 2 | 125.913.235 | 18,99 | 1,32 | 4,70 | Lula 60,83 | Alckmin 39,17 | |
| 2010 | 1 | 135.804.433 | 18,12 | 3,13 | 5,51 | Dilma 46,91 | Serra 32,61 | Marina 19,33 / Plínio 0,87 |
| 2010 | 2 | 135.804.433 | 21,50 | 2,30 | 4,40 | Dilma 56,05 | Serra 43,95 | |
| 2014 | 1 | 142.822.046 | 19,39 | 3,84 | 5,80 | Dilma 41,59 | Aécio 33,55 | Marina 21,32 / Luciana Genro 1,55 |
| 2014 | 2 | 142.822.046 | 21,10 | 1,71 | 4,63 | Dilma 51,64 | Aécio 48,36 | |
| 2018 | 1 | 147.306.295 | 20,33 | 2,65 | 6,14 | Haddad 29,28 | Bolsonaro 46,03 | Ciro 12,47 / Alckmin 4,76 |
| 2018 | 2 | 147.306.294 | 21,30 | 2,14 | 7,43 | Haddad 44,87 | Bolsonaro 55,13 | |
| 2022 | 1 | 156.454.011 | 20,95 | 1,59 | 2,82 | Lula 48,43 | Bolsonaro 43,20 | Tebet 4,16 / Ciro 3,04 |
| 2022 | 2 | 156.454.011 | 20,58 | 1,42 | 3,16 | Lula 50,90 | Bolsonaro 49,10 | |

— [TSE dados abertos](https://dadosabertos.tse.jus.br)

- Os totais conferem com o resultado oficial. Por exemplo, Lula teve 57.259.504 votos no 1º turno de 2022 e 60.345.999 no 2º; Bolsonaro, 51.072.345 e 58.206.354 — [TSE votacao_candidato_munzona_2022](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip)

### Inferences
- O CSV tem 29 "UFs" por ano e turno: as 27 UFs, mais ZZ (exterior) e BR (nacional). São 348 linhas, prontas para alimentar o simulador como prior histórico.

### Gaps
- Este arquivo não traz dados municipais. Eles existem em formato intermediário, mas não foram salvos na pasta para manter os arquivos pequenos.

## (a) Lean do PT por UF por eleição (lean_swing_uf.csv)

### Takeaway
Desde 2006 o mapa ficou estável: o Nordeste está de +15 a +30 pp acima da média nacional do PT, e o Sul, o Centro-Oeste, SP, AC, RO e RR estão de −6 a −27 pp abaixo. 2002 foi a exceção: antes do realinhamento, o voto do PT era quase uniforme no país.

### Cited Findings
Lean do 2º turno, em pp (PT na UF − PT nacional):

| UF | 2002 | 2006 | 2010 | 2014 | 2018 | 2022 |
|---|---|---|---|---|---|---|
| AC | −1,3 | −8,5 | −25,7 | −15,3 | −22,1 | −21,2 |
| AM | 8,6 | 26,0 | 24,5 | 13,4 | 4,9 | 0,2 |
| AP | 14,2 | 9,6 | 6,6 | 9,8 | 4,9 | −2,3 |
| PA | −8,6 | −0,7 | −2,9 | 5,8 | 9,9 | 3,8 |
| RO | −5,7 | −5,5 | −8,7 | −6,5 | −17,0 | −21,6 |
| RR | 4,3 | −22,3 | −22,6 | −10,6 | −16,4 | −27,0 |
| TO | −7,2 | 9,4 | 2,8 | 7,8 | 6,2 | 0,5 |
| AL | −17,7 | 0,6 | −2,4 | 10,5 | 15,0 | 7,8 |
| BA | 4,4 | 17,3 | 14,8 | 18,5 | 27,8 | 21,2 |
| CE | 10,5 | 21,6 | 21,3 | 25,1 | 26,2 | 19,1 |
| MA | −2,8 | 23,8 | 23,0 | 27,1 | 28,4 | 20,2 |
| PB | −4,3 | 14,2 | 5,5 | 12,6 | 20,1 | 15,7 |
| PE | −4,2 | 17,7 | 19,6 | 18,6 | 21,6 | 16,0 |
| PI | −0,5 | 16,5 | 13,9 | 26,6 | 32,2 | 26,0 |
| RN | −2,6 | 8,9 | 3,5 | 18,3 | 18,5 | 14,2 |
| SE | −3,8 | −0,7 | −2,5 | 15,4 | 22,7 | 16,3 |
| DF | 1,0 | −3,9 | −3,2 | −13,5 | −14,9 | −9,7 |
| GO | −4,2 | −6,0 | −6,8 | −8,8 | −10,4 | −9,6 |
| MS | −6,1 | −15,8 | −11,2 | −8,0 | −10,1 | −10,4 |
| MT | −6,8 | −11,1 | −7,2 | −6,3 | −11,3 | −16,0 |
| ES | −1,9 | 4,7 | −6,9 | −5,5 | −7,9 | −8,9 |
| MG | 5,2 | 4,4 | 2,4 | 0,8 | −3,1 | −0,7 |
| RJ | 17,7 | 8,9 | 4,4 | 3,3 | −12,8 | −7,4 |
| SP | −5,9 | −13,1 | −10,1 | −16,0 | −12,8 | −6,1 |
| PR | −2,0 | −11,6 | −11,5 | −12,6 | −13,3 | −13,3 |
| RS | −5,4 | −16,2 | −7,0 | −5,2 | −8,1 | −7,3 |
| SC | 2,9 | −15,4 | −12,7 | −16,2 | −20,8 | −20,2 |

— [TSE dados abertos](https://dadosabertos.tse.jus.br) (agregação própria)

- **Dispersão.** O desvio-padrão do lean entre UFs no 2º turno foi de 7,5 pp em 2002, 13,7 (2006), 13,1 (2010), 14,1 (2014), 17,5 (2018) e 15,1 (2022). A polarização regional chegou ao máximo em 2018 e recuou um pouco em 2022 (estabilidade_lean.csv) — [TSE](https://dadosabertos.tse.jus.br)
- **MG como estado-pêndulo.** O lean de MG ficou entre −3,1 e +5,2 em todas as eleições, e seu swing relativo tem o menor RMS entre os grandes colégios (2,3 pp). — [TSE](https://dadosabertos.tse.jus.br)

### Inferences
- Para 2026, o ponto de partida natural é o lean de 2022, ou uma média de 2018 e 2022. Há sinais de regressão parcial à média: AM, AP, RJ e SP se aproximaram do centro em 2022, e o Nordeste perdeu de 5 a 8 pp de lean, ainda muito alto.

### Gaps
- Não ajustei o lean por candidato ("efeito casa": Ciro no CE em 2002/2018, Marina no AC, Tebet no MS, Alckmin em SP em 2006).

## (b) Variação do lean entre eleições (swing relativo)

### Takeaway
O swing relativo típico de uma UF entre eleições é de cerca de 8 pp no 2º turno contando 2002→2006. **Desde 2006 é de cerca de 6 pp.** Quase metade dessa variância é regional, comum à região toda; o restante é próprio de cada UF.

### Cited Findings
Swing relativo do 2º turno (pp) — médias simples por região:

| Região | 02→06 | 06→10 | 10→14 | 14→18 | 18→22 |
|---|---|---|---|---|---|
| N | +0,5 | −4,9 | +4,3 | −4,9 | −5,4 |
| NE | +15,6 | −2,6 | +8,4 | +4,4 | −6,2 |
| CO | −5,2 | +2,1 | −2,1 | −2,5 | +0,2 |
| SE | −2,6 | −3,8 | −1,8 | −4,8 | +3,4 |
| S | −12,8 | +4,0 | −1,0 | −2,7 | +0,5 |

— [TSE](https://dadosabertos.tse.jus.br)

- **Decomposição do swing do 2º turno, com 2002→2006.** RMS total 8,15 pp; componente regional (média da região) 6,12 pp; componente idiossincrático da UF 5,38 pp. — [TSE](https://dadosabertos.tse.jus.br)
- **Mesma decomposição pós-2006 (4 pares).** RMS total 6,18 pp; regional 4,55 pp; idiossincrático 4,18 pp. — [TSE](https://dadosabertos.tse.jus.br)
- **No 1º turno, com 2002→2006.** RMS total 9,57 pp; regional 6,79; idiossincrático 6,75. O 1º turno é mais volátil por causa de terceiros candidatos com base regional. — [TSE](https://dadosabertos.tse.jus.br)
- **RMS do swing do 2º turno pós-2006 por UF:**
  - menores: PR 0,7, GO 1,4, MG 2,6, MS 3,0, SC 3,2, PE 3,4;
  - maiores: AC 10,6, SE 10,2, RJ 8,8, RR 8,5, RN 8,2, AL 7,9, PI 7,7.
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)
- **2018→2022.** O Nordeste perdeu entre 4 e 8 pp de lean em todas as UFs. SP (+6,7), RJ (+5,4), DF (+5,1) e MG (+2,4) ganharam. É um movimento de convergência ao nacional. — [TSE](https://dadosabertos.tse.jus.br)

### Inferences
- **Sugestão para o simulador:** swing relativo da UF ~ fator regional N(0, cerca de 4,5 pp) + ruído próprio da UF N(0, cerca de 4 pp), pela calibração pós-2006. Use desvios menores (cerca de 2–3 pp) para UFs historicamente estáveis (MG, GO, PR) e maiores (cerca de 8–10 pp) para UFs pequenas do Norte e Nordeste. Esse swing se soma ao erro nacional.

### Gaps
- Com só 4 a 5 pares, o desvio-padrão por UF é estimado com muita incerteza (intervalo de confiança aproximado de ±35–50%).

## (c) Correlação dos swings entre UFs (correlacao_swing_uf*.csv, correlacao_swing_regioes.csv)

### Takeaway
Há uma estrutura em blocos clara: **NE com NE** (r médio de 0,76 no 2º turno; 0,40 pós-2006) e **Sul com Sul** (0,91; 0,80 pós-2006) são muito correlacionados. NE e Sul andam em sentidos opostos (−0,72; −0,25 pós-2006). O Norte acompanha o NE (+0,39/+0,40). O CO acompanha o Sul (+0,57/+0,45). O Sudeste é heterogêneo: correlação interna de apenas 0,14.

### Cited Findings
Correlação média dentro e entre blocos regionais (média dos pares de UFs; diagonal = pares dentro da região):

| Base | N–N | NE–NE | CO–CO | SE–SE | S–S | NE–S | NE–N | CO–S | NE–CO | SE–NE |
|---|---|---|---|---|---|---|---|---|---|---|
| 2º turno, 5 pares (2002–2022) | 0,24 | 0,76 | 0,27 | 0,14 | 0,91 | −0,72 | 0,39 | 0,57 | −0,55 | −0,25 |
| 1º+2º turno, 10 obs. | 0,34 | 0,57 | 0,29 | 0,01 | 0,89 | −0,60 | 0,39 | 0,61 | −0,41 | −0,16 |
| Pós-2006, 1º+2º turno, 8 obs. | 0,49 | 0,40 | 0,04 | 0,14 | 0,80 | −0,25 | 0,40 | 0,45 | −0,16 | −0,21 |

— [TSE](https://dadosabertos.tse.jus.br) (cálculo próprio)

- **Média das correlações fora da diagonal.** 0,03 na matriz principal (2º turno, 5 pares); 0,08 na pós-2006. Na principal, 29% dos pares têm r > 0,5 e 28% têm r < −0,5. — [TSE](https://dadosabertos.tse.jus.br)
- **Pares mais positivos.**
  - Matriz principal: AL–PI 1,00, MA–PE 0,97, PA–PI 0,97, PR–SC 0,96, MS–RS 0,96.
  - Pós-2006: PI–SE 0,99, MS–MT 0,97, PA–PI 0,95.
  - Pares mais negativos na principal: MA–PR −0,96, AL–SP −0,96, TO–SC −0,95.
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)
- **Peso do par 2002→2006.** Esse par (realinhamento lulista: NE +15,6, S −12,8) responde por boa parte das correlações altas da matriz principal. Sem ele, a correlação dentro do NE cai de 0,76 para 0,40. — [TSE](https://dadosabertos.tse.jus.br)

### Inferences
- **Recomendação:** não use a matriz 27×27 bruta no Monte Carlo, porque com n = 5 ela nem é bem condicionada. Use um modelo fatorial:
  - erro nacional;
  - um fator "NE+N contra S+CO" (o eixo lulismo/antilulismo), com carga positiva no NE e no N e negativa no S e no CO;
  - um fator regional;
  - ruído da UF.
- Uma alternativa é encolher a matriz em direção às médias por bloco da tabela acima, de preferência a versão pós-2006.
- A correlação entre UFs **dentro do mesmo resultado** (incluindo o erro nacional) será alta e positiva. Esta análise mede só a covariância do desvio regional em relação ao nacional.

### Gaps
- A correlação dos *erros de pesquisa* por UF (diferente da correlação dos swings eleitorais) não foi estimada. Seria preciso ter as pesquisas estaduais históricas.

## (d) Estabilidade do lean entre eleições consecutivas (estabilidade_lean.csv)

### Takeaway
Desde 2006 o lean é muito estável. A correlação entre eleições consecutivas no 2º turno é de 0,86 a 0,97, e chegou a 0,97 em 2018→2022. A exceção é 2002→2006, com correlação de 0,32 no 2º turno e −0,02 no 1º: foi o realinhamento.

### Cited Findings
| Par | Correlação do lean no 2º turno | Inclinação | RMSE do resíduo (pp) | Correlação do lean no 1º turno |
|---|---|---|---|---|
| 2002→2006 | 0,32 | 0,59 | 12,8 | −0,02 |
| 2006→2010 | 0,93 | 0,89 | 4,9 | 0,87 |
| 2010→2014 | 0,86 | 0,93 | 7,0 | 0,89 |
| 2014→2018 | 0,96 | 1,19 | 5,1 | 0,87 |
| 2018→2022 | 0,97 | 0,84 | 3,5 | 0,91 |

— [TSE](https://dadosabertos.tse.jus.br)

- Correlação do lean do 2º turno de 2022 com eleições anteriores: 0,97 com 2018, 0,92 com 2014, 0,80 com 2010, 0,78 com 2006 e −0,02 com 2002. — [TSE](https://dadosabertos.tse.jus.br)

### Inferences
- Um prior razoável para o lean de 2026 é lean2026 ≈ 0,85 × lean2022 (encolhimento de cerca de 15% em direção a zero, como em 2018→2022), com erro de 3,5 a 5 pp por UF.

### Gaps
- Não ajustei o lean por mudanças demográficas, como o crescimento evangélico ou a migração.

## Abstenção: 1º contra 2º turno por UF (primeiro_segundo_turno_uf.csv)

### Takeaway
Até 2018, a abstenção sempre subiu do 1º para o 2º turno; a alta mediana por UF foi de +1,4 a +3,8 pp. **Em 2022 ela caiu** (mediana −0,4 pp; nacional de 20,95% para 20,58%), algo inédito, embora com fortes exceções no Norte.

### Cited Findings
- **Variação da abstenção do 1º para o 2º turno, por ano** (média / mediana entre as 27 UFs + ZZ + BR, em pp):
  - 2002: +4,0 / +3,4
  - 2006: +3,5 / +2,7
  - 2010: +4,0 / +3,8
  - 2014: +2,2 / +1,7
  - 2018: +1,9 / +1,4
  - 2022: +0,55 / −0,36
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)
- **2022 por UF.**
  - A abstenção caiu em SP (21,6 → 21,1), MG (22,3 → 21,0), GO (21,7 → 20,7), SC (18,4 → 17,4), PE (18,2 → 17,3), BA (21,3 → 20,5), PR, RS, RJ, CE e DF.
  - Subiu muito no AP (19,5 → 27,2), AC (22,4 → 28,4) e RR (16,7 → 21,9), e também em TO, AM e PA.
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)
- **2018.** A abstenção subiu em todas as UFs, com destaque para AC (+8,1), AP (+6,2) e RR (+5,0). — [TSE](https://dadosabertos.tse.jus.br)

### Inferences
- Em disputas apertadas, a mobilização do 2º turno pode reduzir a abstenção, sobretudo no Sudeste e no Sul. O simulador não deve presumir mecanicamente que a abstenção sobe no 2º turno.
- No Norte, há uma alta estrutural de abstenção no 2º turno. Ela foi maior em 2022 porque AP, AC e RR não tiveram 2º turno para governador.

### Gaps
- Não separei o efeito de haver 2º turno estadual na UF. Seria uma variável útil para o simulador.

## Transferência do 1º para o 2º turno: contabilidade nacional e regressão por UF

### Takeaway
Em 2022, do "bolo" líquido de votos novos no 2º turno, o PT ficou com só **30%**: Lula ganhou 3,09 milhões de votos e Bolsonaro, 7,13 milhões. Em 2018, Haddad ficou com 65% do ganho líquido. Em 2010 e 2014, o PT ficou com 41–43%, abaixo da sua fatia do 1º turno.

### Cited Findings
- **Contabilidade nacional, 1º para 2º turno** (TSE, cálculo próprio):

| Ano | Ganho do PT | Ganho do oponente | Votos de terceiros no 1º turno | Variação da abstenção | Variação de brancos e nulos | Fatia do PT no ganho líquido |
|---|---|---|---|---|---|---|
| 2002 | +13,34 mi | +13,67 mi | 25,79 mi | +3,14 mi | −4,35 mi | 49% |
| 2006 | +11,63 mi | −2,43 mi | 9,37 mi | — | — | 126% (Alckmin perdeu votos) |
| 2010 | +8,10 mi | +10,58 mi | — | — | — | 43% |
| 2014 | +11,23 mi | +16,14 mi | — | — | — | 41% |
| 2018 | +15,70 mi | +8,52 mi | 26,43 mi | — | — | 65% |
| 2022 | +3,09 mi | +7,13 mi | 9,90 mi | −0,57 mi | +0,25 mi | 30% |

  — [TSE](https://dadosabertos.tse.jus.br)
- **2022 por UF.** A fatia do PT no ganho dos dois finalistas foi maior em SE (48%), CE (47%), MA e PI (45%), BA (40%). Foi menor em AC (5%), RO (5%), MT (9%), RR (12%), SC (14%) e RS (16%). — [TSE](https://dadosabertos.tse.jus.br)
- **2018 por UF.** Haddad subiu +38,0 pp no CE (Ciro teve 41,0% lá no 1º turno). Nas outras UFs, a alta foi de +7,5 (RO) a +22,2 (RN). — [TSE](https://dadosabertos.tse.jus.br)
- **Regressão entre as 27 UFs** do ganho do PT (pp de válidos) contra o voto dos terceiros no 1º turno (pp):
  - 2018: Ciro 0,85, Alckmin cerca de 0; correlação do ganho do PT com o total de terceiros = 0,86.
  - 2022: Tebet 0,14, Ciro 0,83; correlação = 0,46.
  - 2014: Marina 0,42.
  - 2010: Marina 0,58.
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)

### Inferences
- Em 2022, o voto de terceiros mais o voto do 2º turno foram, no saldo, desproporcionalmente para Bolsonaro. É um sinal de que, numa disputa Lula × candidato de direita, o "bolo" de terceiros e de quem volta a votar tende a pesar contra o PT.

### Gaps
- A contabilidade líquida não separa o que foi transferência de votos do que foi mudança de quem compareceu.

## Regressão ecológica municipal 2022 (e 2018): taxas de transferência de Tebet e Ciro (transferencia_2022.csv, transferencia_2t_ecologica.csv)

### Takeaway
A regressão de Goodman municipal sugere:
- Ciro em 2022: cerca de 71% para Lula e 26% para Bolsonaro.
- Tebet em 2022: com restrição [0,1], cerca de 87% para Bolsonaro e 13% para branco/nulo. Em MQO livre: 13% Lula, 24% Bolsonaro, 18% branco/nulo e 45% abstenção, um resultado instável.
- Ciro em 2018: cerca de 85% para Haddad.

**Essas estimativas divergem muito do Datafolha** e devem ser tratadas com bastante cautela, por causa do viés de agregação.

### Cited Findings
- **2022, Brasil, MQO restrito a [0,1]** (taxas em %; cada linha mostra para onde foi o eleitor do 1º turno):

| Origem no 1º turno | Lula | Bolsonaro | Branco/nulo | Abstenção |
|---|---|---|---|---|
| Lula | 97,5 | 0 | 0,8 | 1,7 |
| Bolsonaro | 0 | 100 | 0 | 0 |
| Tebet | 0 | 86,8 | 13,2 | 0 |
| Ciro | 70,8 | 25,9 | 3,3 | 0 |
| Outros | 22,5 | 77,5 | 0 | 0 |
| Branco/nulo | 24,6 | 10,4 | 65,0 | 0 |
| Abstenção | 0 | 2,5 | 0 | 97,5 |

  — [TSE](https://dadosabertos.tse.jus.br) (cálculo próprio, 5.570 municípios)
- **Robustez por região (2022, MQO restrito).**
  - Nordeste: Tebet 0 / 77 / 23 / 0 e Ciro 57 / 43 / 0 / 0.
  - Fora do Nordeste: Tebet 7 / 57 / 36 / 0 e Ciro 86 / 7 / 8 / 0.
  - Ordem dos números: Lula / Bolsonaro / branco-nulo / abstenção.
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)
- **2018, Brasil, MQO restrito.**
  - Ciro: 85,5% Haddad, 8,7% Bolsonaro, 5,8% branco/nulo.
  - Alckmin: 0% Haddad, 61,7% Bolsonaro, 35,4% branco/nulo, 2,9% abstenção.
  - Amoêdo: 0 / 57,9 / 42,1.
  - O MQO livre dá resultado parecido para Ciro (83,7% Haddad).
  - Fonte: [TSE](https://dadosabertos.tse.jus.br)
- **2014, Marina (restrito):** 43,8% Dilma, 50,4% Aécio. Fora do Nordeste: 28,9 / 62,9. — [TSE](https://dadosabertos.tse.jus.br)
- **2010, Marina (restrito):** 41,4% Dilma, 41,6% Serra, 12,2% branco/nulo. — [TSE](https://dadosabertos.tse.jus.br)
- **Regressão em diferenças municipal (2022).** Ganho do Lula em pp de válidos = −1,21 + 0,315 × Tebet% + 0,786 × Ciro% + 0,067 × Outros%. — [TSE](https://dadosabertos.tse.jus.br)
- **Contraste com pesquisa individual.**
  - Datafolha de 5 a 7/10/2022: eleitores de Tebet com 31% Lula, 29% Bolsonaro, 28% branco/nulo e 12% indecisos.
  - Eleitores de Ciro, segundo os relatos da imprensa: 42% Bolsonaro, 31% Lula, 28% branco/nulo e 5% indecisos. Esses números somam 106%, o que indica erro de transcrição na matéria. Convém confirmar no relatório original do Datafolha.
  - Fontes: [Diario de Pernambuco](https://www.diariodepernambuco.com.br/noticia/politica/2022/10/bolsonaro-herda-mais-votos-de-ciro-do-que-lula-e-os-de-tebet-se-divide.html); [Seu Dinheiro](https://www.seudinheiro.com/2022/politica/bolsonaro-lula-pesquisa-datafolha-segundo-turno-voto-eleicoes-ccgg/)

### Inferences
- **Por que a regressão ecológica e a pesquisa divergem.**
  - Em 2022, o voto em Ciro se concentrou onde Lula já era forte, como o CE. O voto em Tebet se concentrou onde Bolsonaro era forte (MS e o agro do Centro-Oeste, Sul e interior de SP).
  - A regressão de Goodman confunde esse efeito de contexto com a transferência individual. Por isso superestima Ciro → Lula e Tebet → Bolsonaro.
- **O resultado agregado é robusto e independe do modelo.** Bolsonaro ficou com cerca de 70% do ganho líquido. Isso só fecha se a soma Tebet + Ciro + outros + brancos e nulos que voltaram a votar pendeu para Bolsonaro, o que é mais compatível com o Datafolha (Ciro mais para Bolsonaro) do que com a regressão ecológica de Ciro.
- **Recomendação para o simulador.** Parametrize a transferência de terceiros com distribuições amplas, ancoradas nas pesquisas individuais, e use a contabilidade nacional (PT com cerca de 30–45% do ganho líquido nos ciclos com centro-direita forte) como checagem. Não use as taxas de Goodman como ponto central.
- **Ciro em 2018.** A estimativa de que cerca de 85% foi para Haddad é mais plausível, porque o padrão bate com a alta de +38 pp do PT no CE. Ainda assim, também está sujeita a viés de contexto.

### Gaps
- Não estimei modelos ecológicos hierárquicos (EI de King ou Rosen et al.) nem usei dados por seção, que têm menos viés de agregação. Também não há painel individual público entre o 1º e o 2º turno de 2022.

## Arquivos gerados (nesta pasta)
- `resultados_uf_2002_2022.csv`: ano × turno × UF (27 UFs, mais ZZ e BR). Traz eleitorado, comparecimento, abstenção, brancos, nulos, válidos, votos e % do PT, do oponente e dos dois terceiros colocados, lean e versão bipartidária.
- `lean_swing_uf.csv`: lean do 1º e do 2º turno por eleição, swings relativos, desvio-padrão e RMS do swing por UF, incluindo o RMS pós-2006.
- `correlacao_swing_uf.csv`: matriz principal 27×27 (swings do 2º turno, 5 pares).
- `correlacao_swing_uf_1t2t.csv`: matriz com 10 observações (1º e 2º turno).
- `correlacao_swing_uf_pos2006.csv`: matriz com 8 observações pós-2006.
- `correlacao_swing_regioes.csv`: médias por bloco regional nas três bases.
- `estabilidade_lean.csv`: correlação, inclinação e RMSE do lean entre eleições consecutivas.
- `primeiro_segundo_turno_uf.csv`: comparação entre o 1º e o 2º turno por UF (variação do PT, variação da abstenção, % de terceiros e fatia do PT no ganho).
- `transferencia_2022.csv` e `transferencia_2t_ecologica.csv` (2010–2022): taxas de Goodman nas versões MQO livre e restrita, para Brasil, Nordeste e fora do Nordeste.
