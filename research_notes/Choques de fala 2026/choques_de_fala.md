# Choques de fala, idade e saúde: teste com dados (2026-10-05)

## 0. Regra de seleção declarada ANTES de coletar eventos [método]

Escrita antes de qualquer busca de evento. Vale igual para os dois lados.

1. Ator: presidente/ex-presidente, candidato, cônjuge/familiar com exposição pública, ministro ou líder de partido aliado.
2. Uma fala/ato entra se: (a) foi coberta como manchete por pelo menos um veículo de cada campo
   (ex.: Folha/G1/Estadão/Valor/Reuters de um lado; Gazeta do Povo/Oeste/Brasil 247/CartaCapital de outro), OU
   (b) algum veículo financeiro (Valor, InfoMoney, Reuters, Bloomberg, Estadão Conteúdo) ligou explicitamente a fala ao
   dólar/juros/Bolsa, OU (c) é um marco institucional que a literatura/imprensa trata como de alto impacto.
3. Busca simétrica: os mesmos modelos de consulta para os dois lados ("dólar sobe após fala de X", "mercado reage a X",
   "gafe de X"), todos os resultados lidos, sem descartar evento por ter reação nula (eventos sem reação ENTRAM).
4. Janela: Lula/Janja/ministros 2023–26; Bolsonaro/Flávio/Eduardo/aliados 2019–26. Incluir obrigatoriamente os exemplos do usuário.
5. Evento com confusor maior no mesmo dia (pacote fiscal, Fed, dado, choque externo) é marcado "confundido"; não se atribui causa.
6. Controle de seleção: o mesmo cálculo é feito em TODOS os dias (placebo) para dar a distribuição-base do movimento anormal.
7. Limite declarado: não consigo contar itens de notícia de forma sistemática; a regra (a)/(b)/(c) é a aproximação operacional.
8. Como a regra foi aplicada (transparência da seleção) [fato do processo]. Os 34 eventos foram achados por buscas com os mesmos modelos de consulta para os dois lados e pela lista de exemplos do usuário (Janja/Musk, Trump/tarifas, meta zero, Faria Lima, 7/9/2021, embaixadores, Eduardo e o tarifaço, Flávio em 2026). Cada evento foi rotulado pelo critério pelo qual entrou: **(a)** cobertura nos dois campos sem ligação ao mercado na própria fonte (14 eventos) ou **(b)** ligação explícita a mercado em veículo financeiro/geral (20 eventos). O critério (b) é selecionado pelo resultado (só entra porque "mexeu"), por isso infla qualquer efeito; o grupo (a) é o menos enviesado. O tipo (fiscal, institucional, pessoal/diplomático, saúde, eleitoral, escândalo) foi atribuído pelo conteúdo, antes de olhar o movimento. A direção esperada (adversa ou tranquilizadora) também.

## 1. Resumo (leia primeiro)

1. **Falas e atos sobre política fiscal e instituições movem o câmbio de forma mensurável nos dois lados; falas pessoais/diplomáticas, não.** [cálculo próprio] Em 34 eventos (16 do lado Lula/Janja/ministros, 18 do lado Bolsonaro/Flávio/Eduardo/aliados), 7 tiveram movimento anormal do BRL no dia 0 acima de 1,65 desvio do placebo (|z|>1,65; esperado por acaso: 9,3% dos dias, ou 3,2 de 34). Todos os 7 são fiscais, institucionais, eleitorais ou escândalo; **nenhum dos 9 eventos pessoais/diplomáticos** (Janja/Musk, Gaza/Hitler, Xangai, Trump/tarifas, "gripezinha", Macron, Eduardo e o tarifaço) passou do limiar sozinho, e o movimento médio deles (0,73 pp em módulo) é praticamente o de um dia qualquer (0,63 pp).
2. **Os dois lados têm frequência e tamanho parecidos, com incerteza enorme.** [cálculo próprio] Eventos de alto impacto: Lula/ministros 3 em ~3,9 anos (0,77/ano; IC 95% de Poisson 0,16 a 2,25); Bolsonaro/aliados 4 em ~7,0 anos (0,57/ano; 0,16 a 1,46). Teste exato de taxas iguais: p = 0,71. Tamanho do movimento no dia 0: mediana ~2,8 pp (intervalo observado 2,5 a 4,5 pp) nos dois lados. Só 3 dos 7 não têm confusor documentado (Haddad/pacote de 27/11/2024, Bolsonaro 7/9/2021, indicação de Flávio em 5/12/2025). **Não há base para dizer que um lado seja sistematicamente mais "desestabilizador" que o outro; também não há base para dizer que sejam iguais** (n pequeno).
3. **Dez/2024 (dólar a R$ 6,26): foi o pacote fiscal, não a Janja.** [cálculo próprio] No dia 18/11 (primeiro pregão após a fala de 16/11) o BRL teve movimento anormal de -0,57 pp; nos 7 pregões seguintes o acumulado foi -0,3 pp. A depreciação anormal começa na noite de 27/11 (pronunciamento de Haddad às 20h30): +3,5 pp em 27-28/11. Até o recorde de 18/12 o acumulado anormal desde 18/11 foi +6,9 pp (bruto +8,2%), com mais +1,6 em 6/12, +1,3 em 16/12 e +2,4 em 18/12 (Fed duro + desidratação do pacote), e -2,65 em 19-20/12 (leilões do BC, vídeo de Lula com Galípolo, PEC). O R$ 6,26 é fechamento de 18/12, não PTAX (PTAX de 18/12: R$ 6,1624; -0,1% no dia).
4. **Persistência: nos eventos de alto impacto o efeito não "some" em 5 e 20 dias na mediana; some quando há reversão de política.** [cálculo próprio] Razão mediana (anormal em 5 dias / dia 0) = 0,83; em 20 dias = 1,06 (n = 7; janelas de 20 dias contaminadas por outros eventos). Casos de reversão: Dez/2024 18/12 (+2,5 no dia, -3,3 em 20 dias) e retratação de 9/9/2021 (-2,8, depois ~0). Atenção da mídia não foi medida: a tese "jogam debaixo da cadeira" sobre a **atenção** não foi testada; sobre o **preço**, o dado diz que não é regra.
5. **Idade/saúde (Parte B).** [cálculo próprio + estimativa] Homem brasileiro de 81,2 a 85,2 anos (mandato 2027-30): 29,0% de probabilidade de morrer no mandato pela tábua do IBGE 2024 (25,96% de 80,0 a 84,0). Com ajuste por acesso a cuidado (multiplicador de risco 0,6 a 0,9, hipótese): 18,5% a 26,5% (central 22,6%). Incapacidade sem morte: 2% a 8% (estimativa, base fraca). Flávio (45,4 anos): 2,0% de morte no mandato pela mesma tábua.
6. **Sucessão: Alckmin assume.** [fato constitucional, citado de memória] Pelo art. 79 da CF o vice sucede em caso de vaga. O mercado trata Alckmin como moderado/pró-empresa (imprensa; não é medição). O único evento de saúde observado (cirurgia de 10/12/2024) coincidiu com queda do dólar (ver L09; confundido por Copom/IPCA). Não há evidência aqui de "prêmio de risco de saúde".
7. **Gafe e idade:** [sem evidência] Não encontrei estudo que mostre aumento da frequência de gafes com a idade em políticos; a literatura de erros de fala em idosos é mista e a avaliação cognitiva de políticos quase não foi estudada. A tese é **hipótese não testada**, não fato nem refutada.
8. **Para os modelos (Parte C):** [estimativa/hipótese] choque de fala com taxa igual nos dois lados (central 0,5/ano cada, faixa 0,2 a 1,0; razão L/F de 0,5 a 2), tamanho mediano 3% no câmbio só para fala fiscal/institucional (zero para pessoal), meia-vida de semanas; e um termo de cauda de idade só para Lula (saída antecipada 20% a 37%, central ~26%). Efeito no índice das famílias: |ΔD| ≤ 0,1 ponto de índice; em P(Lula vence): < 0,2 pp pelo canal de saúde até a posse; o canal que importa é **quem governa**, não quem vence.

## 2. Dados, método e limites de medida

- **USD/BRL:** PTAX venda do BCB (SGS 1; coluna `ptax_*`) e, para o cálculo do anormal, cotação de fim de dia do Yahoo Finance (USDBRL=X). [fato] No Yahoo o "close" diário de câmbio é o preço de abertura (00:00 de Londres), então usei a cotação do dia útil seguinte como proxy do fechamento (cerca de 21h de Brasília). Erro de medida de ±0,3 a 0,5 pp por dia, igual para os dois lados.
- **PTAX é inadequada para fala à tarde:** é média de 4 janelas entre ~10h e ~13h. Exemplo: 18/12/2024, PTAX -0,1%, fechamento +3,0%. Por isso o anormal usa o fechamento proxy e a PTAX aparece só como dado bruto.
- **Controles:** cesta EM = média simples dos log-retornos de USDMXN, USDCLP, USDCOP, USDZAR (Yahoo); DXY (Yahoo); para o Ibovespa, EEM (Yahoo). Beta do BRL contra a cesta estimado por MQO em 250 pregões que terminam 21 pregões antes do evento. **Anormal = retorno do BRL - alfa - beta × cesta** (positivo = BRL enfraquece além do que a cesta explica). Variante com DXY na regressão nas colunas `cesta+dxy`. Robustez: mesma conta com FRED H.10 (BRL e índice do dólar EM, taxa do meio-dia de NY); correlação do anormal de 2 dias entre as duas bases = 0,80 e concordância de sinal de 67%: os eventos grandes concordam, os pequenos não são distinguíveis de ruído.
- **Placebo:** a mesma conta em todos os dias úteis de mar/2019 a out/2026 (n ≈ 1.970). Desvio-padrão do anormal: 0,85 pp (1 dia), 1,64 pp (5 dias), 2,93 pp (20 dias); P95 de |anormal| = 1,79 / 3,32 / 5,89 pp. Anualizado, o desvio idiossincrático do BRL é ~13,5% (0,85 × √252).
- **Eventos após o fechamento** (Haddad 27/11, Trump/Lula/Eduardo 9/7, Bolsonaro 24/3/2020, Petrobras 19/2/2021, secretários 21/10/2021, JN 28/8/2026, IOF 22/5/2025): janela de "1 dia" = 2 dias (noite anterior + dia 0), z ajustado por √2.
- **Indisponível:** vértice da curva DI (sem série diária gratuita acessível; o BCB SGS não publica DI) e **intradiário** (só fechamento diário). Consequência: efeitos que aparecem só em juros futuros (ex.: 27/10/2023, em que o InfoMoney relata alta de DIs e o BRL anormal foi -0,3 pp) **não** são captados.
- **Confundido:** marcado quando (i) há confusor documentado no mesmo dia (FOMC, CPI, pacote, o próprio tarifaço, covid), ou (ii) há choque global (|cesta| ou |DXY| > 0,95% no dia 0, que é ~1,5 desvio). "Limpo" significa **nenhum confusor documentado**, não ausência de confusor. Para janelas de 5 e 20 dias, outro evento da própria tabela dentro de 20 dias úteis marca a janela como contaminada.
- **Último dado:** 5/10/2026. As janelas de 5/20 dias dos eventos recentes são mais curtas; L16 (1/10/2026) não tem janela de câmbio (o fechamento de 2/10 exigiria a cotação de 5/10, que já contém a reação ao 1º turno de 4/10; PTAX 2/10: +0,31%).

## 3. Parte A: tabela-resumo dos 34 eventos

Anormal do BRL em pontos percentuais (pp) no dia 0 (ou 2 dias, se após o fechamento), 5 dias e 20 dias; PTAX bruta em % no dia 0 / 5 / 20 dias; z = anormal do dia 0 dividido pelo desvio do placebo. Critério: (a) cobertura nos dois campos; (b) ligação a mercado. Fonte, texto literal, Ibovespa, DXY, cesta, robustez FRED e confusores estão no CSV `eventos_choques.csv`.

| id | data | ator | tipo | crit. | anorm. 1d | anorm. 5d | anorm. 20d | PTAX 1d/5d/20d % | z 1d | status |
|---|---|---|---|---|---|---|---|---|---|---|
| L01 | 2022-11-10 | Lula | fiscal | b | +4.5 | +4.9 | +3.5 | +2.8 / +5.9 / +0.9 | +5.3 | confundido |
| L02 | 2022-11-17 | Lula | fiscal | b | -0.1 | +0.1 | +0.7 | +2.7 / +1.4 / +0.4 | -0.2 | limpo |
| L03 | 2023-04-13 | Lula | pess/dipl | a | +0.8 | +3.2 | +0.3 | -0.8 / +2.0 / -0.5 | +1.0 | confundido |
| L04 | 2023-10-27 | Lula | fiscal | b | -0.3 | +0.8 | +0.1 | -1.1 / -2.3 / -2.2 | -0.3 | limpo |
| L05 | 2024-02-18 | Lula | pess/dipl | a | -0.6 | +0.0 | +0.9 | -0.4 / +0.2 / +0.4 | -0.7 | limpo |
| L06 | 2024-06-26 | Lula | fiscal | b | +0.9 | +3.4 | +2.0 | +1.5 / +4.4 / +2.8 | +1.1 | confundido |
| L07 | 2024-11-16 | Janja | pess/dipl | a | -0.6 | +0.3 | +4.3 | -0.5 / +0.2 / +4.5 | -0.7 | limpo |
| L08 | 2024-11-27 | Haddad | fiscal | b | +3.5 | +4.0 | +5.0 | +2.7 / +3.9 / +5.8 | +2.9 | limpo |
| L09 | 2024-12-10 | Lula | saúde | b | -0.5 | +1.0 | -1.7 | -0.1 / -0.1 / +1.2 | -0.6 | confundido |
| L10 | 2024-12-18 | Haddad | fiscal | b | +2.5 | +0.4 | -3.3 | -0.1 / -0.2 / -2.2 | +2.9 | confundido |
| L11 | 2024-12-20 | Lula | fiscal | b | -0.6 | -0.5 | -2.7 | -1.7 / +0.2 / -2.2 | -0.7 | confundido |
| L12 | 2025-01-30 | Lula | pess/dipl | a | +0.2 | -1.1 | -1.5 | +0.7 / -1.0 / -1.4 | +0.2 | limpo |
| L13 | 2025-05-22 | Haddad | fiscal | b | +0.2 | +0.8 | -3.1 | +1.0 / +0.3 / -2.5 | +0.2 | confundido |
| L14 | 2025-07-09 | Lula | pess/dipl | a | +1.6 | +1.5 | +0.4 | +1.5 / +2.0 / +0.3 | +1.3 | confundido |
| L15 | 2025-09-23 | Lula | pess/dipl | b | -0.9 | -0.4 | +0.9 | -0.7 / -0.4 / +0.6 | -1.0 | limpo |
| L16 | 2026-10-01 | Lula | inst. | a | — | — | — | +0.3 / +— / +— | +— | confundido |
| B01 | 2019-10-31 | Eduardo Bolsonaro | inst. | a | +0.1 | +3.1 | +1.4 | -0.6 / +2.2 / +5.5 | +0.1 | limpo |
| B02 | 2020-02-12 | Paulo Guedes | fiscal | a | +0.7 | +0.9 | +0.3 | +0.5 / +0.7 / +13.2 | +0.8 | limpo |
| B03 | 2020-03-24 | Jair Bolsonaro | pess/dipl | a | +0.1 | +2.3 | +3.7 | -0.0 / +2.5 / +7.4 | +0.1 | confundido |
| B04 | 2020-05-22 | Jair Bolsonaro | inst. | b | -0.4 | -2.4 | -4.5 | -0.4 / -4.7 / -4.6 | -0.5 | confundido |
| B05 | 2020-09-15 | Jair Bolsonaro | fiscal | b | +0.2 | +1.3 | +2.0 | -0.5 / +2.7 / +5.4 | +0.3 | limpo |
| B06 | 2021-02-19 | Jair Bolsonaro | fiscal | b | -0.2 | -0.2 | +0.1 | +2.1 / +2.6 / +2.1 | -0.1 | limpo |
| B07 | 2021-09-07 | Jair Bolsonaro | inst. | b | +2.7 | +1.0 | +2.9 | +1.5 / +0.9 / +5.5 | +3.2 | limpo |
| B08 | 2021-09-09 | Jair Bolsonaro | inst. | b | -2.8 | -1.8 | +0.4 | +0.6 / +0.1 / +4.9 | -3.3 | confundido |
| B09 | 2021-10-21 | Governo Bolsonaro | fiscal | b | +0.2 | -2.0 | -4.9 | +1.2 / -0.5 / -1.0 | +0.2 | limpo |
| B10 | 2022-07-18 | Jair Bolsonaro | inst. | a | +0.7 | +3.6 | +0.9 | -0.6 / +0.9 / -5.5 | +0.8 | limpo |
| B11 | 2022-11-01 | Jair Bolsonaro | inst. | a | -0.7 | +0.7 | +7.4 | -2.0 / -1.6 / +0.7 | -0.9 | limpo no dia 0; janela de 20d contaminada (L01/L02) |
| B12 | 2025-07-09 | Eduardo Bolsonaro | pess/dipl | a | +1.6 | +1.5 | +0.4 | +1.5 / +2.0 / +0.3 | +1.3 | confundido |
| B13 | 2025-12-05 | Jair Bolsonaro / Flávio | eleit. | b | +2.5 | +2.1 | +3.1 | +0.9 / +2.4 / +2.6 | +3.0 | limpo |
| B14 | 2025-12-07 | Flávio Bolsonaro | eleit. | b | -0.5 | -0.0 | +0.0 | +1.6 / +1.1 / +0.7 | -0.6 | confundido |
| B15 | 2026-05-13 | Flávio Bolsonaro | escând. | b | +3.0 | +2.8 | +6.7 | +0.3 / +2.9 / +5.7 | +3.5 | confundido |
| B16 | 2026-08-27 | Flávio Bolsonaro | fiscal | b | -0.1 | -1.3 | -2.8 | +0.7 / -1.3 / +0.7 | -0.1 | confundido |
| B17 | 2026-08-28 | Flávio Bolsonaro | fiscal | a | -0.3 | -1.3 | -2.8 | -0.4 / -1.4 / +0.2 | -0.2 | confundido |
| B18 | 2019-08-24 | Jair Bolsonaro | pess/dipl | a | -0.2 | -0.4 | +1.2 | +1.3 / +1.3 / +2.0 | -0.3 | confundido |

Notas: L = lado Lula/Janja/ministros (16); B = lado Bolsonaro/Flávio/Eduardo/aliados (18). L14 e B12 são **o mesmo evento de mercado** (carta de Trump de 9/7/2025) visto pelos dois lados: não somar como independentes. B16 e B17 têm janelas sobrepostas. B08 é a reversão de B07. Textos não citados literalmente na fonte estão marcados como [paráfrase], [tradução] ou [ato].

### 3.1 Frequência por ano e lado

Eventos documentados (qualquer movimento): 2019: B2; 2020: B4; 2021: B4; 2022: L2 B2; 2023: L2; 2024: L7; 2025: L4 B3; 2026: L1 B3. **Isto não é uma taxa**: depende de onde busquei e de quando a imprensa cobriu (2024 concentra a crise fiscal e a Janja). Eventos de alto impacto (|z1|>1,65): 2021: B2 (7/9 e retratação 9/9); 2022: L1 (10/11); 2024: L2 (27/11 e 18/12); 2025: B1 (5/12); 2026: B1 (13/5). Dos 7, 3 não têm confusor documentado: L08, B07, B13. Taxa de alto impacto, [cálculo próprio] Lula/ministros 0,77/ano (IC 0,16 a 2,25), Bolsonaro/aliados 0,57/ano (0,16 a 1,46); só os "limpos": 0,26/ano (0,01 a 1,43) e 0,29/ano (0,03 a 1,03). As taxas **não são distinguíveis** (p = 0,71) e podem ser iguais.

### 3.2 Distribuição dos movimentos anormais

[cálculo próprio] Dia 0, 33 eventos com dado: média do módulo 1,06 pp (placebo: 0,63); 7 de 33 com |z|>1,65 (placebo: 9,3%, ou 3,1 esperados; P(≥7 de 33 | p=0,093) ≈ 0,03 pela binomial, **sem corrigir seleção**). Por critério de seleção: grupo (a) (14 eventos, sem ligação a mercado na fonte): módulo médio 0,63 pp (igual ao placebo), 0 eventos com |z1|>1,65; grupo (b) (20): módulo médio 1,33 pp, 7 eventos com |z1|>1,65. O excesso do grupo (b) é em grande parte o próprio critério de seleção, **não prova** que falas "em geral" movam o dólar.

Médias com sinal (positivo = na direção esperada pelo conteúdo), pp, com IC 90% por bootstrap:

| grupo | n | dia 0 | 5 dias | 20 dias |
|---|---|---|---|---|
| todos | 34 | +0,78 [0,41; 1,17] | +1,02 [0,55; 1,52] | +0,77 [-0,05; 1,63] |
| lado Lula/ministros | 16 | +0,91 [0,32; 1,55] | +1,34 [0,68; 2,08] | +0,62 [-0,43; 1,64] |
| lado Bolsonaro/aliados | 18 | +0,67 [0,22; 1,16] | +0,75 [0,07; 1,42] | +0,90 [-0,35; 2,13] |
| sem confusor no dia 0 | 16 | +0,56 [0,07; 1,12] | +0,78 [0,14; 1,49] | +1,10 [-0,06; 2,31] |
| só critério (a) | 14 | +0,27 | +1,10 | +1,29 |
| só critério (b) | 20 | +1,11 | +0,97 | +0,44 |

Teste de permutação Lula x Bolsonaro (diferença de médias, p): dia 0 +0,24 (p=0,62), 5 dias +0,59 (p=0,33), 20 dias -0,28 (p=0,79); só limpos: -0,21 (0,77), -0,23 (0,79), +0,21 (0,90). **Nenhuma diferença entre lados é distinguível de zero.**

### 3.3 Persistência em 5 e 20 dias

[cálculo próprio] Os 7 eventos com |z1|>1,65, tomados na direção do dia 0: média 3,08 pp (dia 0), 2,44 (5 dias), 2,51 (20 dias); razões individuais 5d/dia0 = 1,09; 1,12; 0,18; 0,36; 0,65; 0,83; 0,96; 20d/dia0 = 0,79; 1,41; -1,31; 1,06; -0,14; 1,21; 2,25. Leitura: **o efeito não decai a zero na mediana**, mas (i) as janelas de 20 dias incluem outros eventos (L01 tem a fala "paciência" de 17/11, L08 tem a erosão do pacote e a crise de dezembro, B15 tem toda a sequência de revelações de maio a setembro) e (ii) o mercado de câmbio não é um objeto isolado: quando o governo reverte (BC vendeu dólar em 19-20/12/2024; Bolsonaro recuou em 9/9/2021) o efeito some. No placebo, o anormal de 20 dias tem desvio de 2,9 pp: um efeito de 2,5 pp em 20 dias **não é distinguível** de ruído para um único evento. Efeito intradiário que reverte até o fechamento aparece no L02 (17/11/2022): dólar +1,79% às 10h20 e PTAX +2,7%, mas fechamento anormal ~0.

### 3.4 Tipo de fala

| tipo | n | mód. médio dia 0 (pp) | com sinal dia 0 | com sinal 5d | eventos com \|z1\|>1,65 |
|---|---|---|---|---|---|
| fiscal | 14 | 1,02 | +0,87 | +0,88 | 3 |
| institucional | 7 | 1,25 | +0,85 | +1,31 | 2 |
| eleitoral/escândalo | 3 | 2,0 | +1,7 | +1,6 | 2 |
| pessoal/diplomático | 9 | 0,73 | +0,43 | +0,85 | 0 |
| saúde | 1 | 0,52 | -0,52 | +0,98 | 0 |

Diferença fiscal+institucional versus resto (permutação): módulo dia 0 +0,08 pp (p=0,87), 5 dias +0,44 (p=0,33). **A diferença por tipo existe nos casos grandes (7 de 7 são fiscal/institucional/eleitoral), mas não é estatisticamente separável com n=34**, e todos os grandes entraram pelo critério (b). No grupo (a), os eventos institucionais (n=4: Eduardo/AI-5, embaixadores, 1/11/2022, L16) não mexeram no dia 0 (módulo 0,51) e tiveram +2,5 pp médios em 5 dias (B01 +3,1; B10 +3,6; B11 +0,7), com janelas contaminadas: sinal sugestivo, **não atribuível**. Resultado honesto: **efeito pequeno ou nulo de falas pessoais/diplomáticas; efeito grande e relevante de decisões e falas fiscais/institucionais de quem tem poder sobre elas, com quase tudo no dia 0 do ato (pacote, indicação, ruptura) e pouco em "gafe"**.

### 3.5 Episódio de dez/2024 em detalhe [cálculo próprio]

Fechamento proxy (USD/BRL) e anormal diário do BRL vs cesta (beta 0,57 estimado antes de 18/11):

| data | evento do dia | fechamento | anormal (pp) | acumulado desde 18/11 |
|---|---|---|---|---|
| 18/11 | 1º pregão após Janja (16/11) | 5,746 | -0,57 | -0,57 |
| 19 a 26/11 | sem evento relevante | 5,77 a 5,81 | soma -0,3 | -0,31 |
| 27/11 | Haddad, TV 20h30 (quarta) | 5,937 | +2,24 | +1,93 |
| 28/11 | 1º pregão após o pacote | 6,014 | +1,30 | +3,24 |
| 6/12 | (sem evento da tabela) | 6,088 | +1,57 | +4,89 |
| 10 a 11/12 | cirurgia de Lula, IPCA, Copom (alta de 1 p.p.) | 6,045; 5,953 | -0,52; -1,36 | +2,68 |
| 16/12 | (sem evento da tabela) | 6,147 | +1,32 | +5,57 |
| 18/12 | Haddad "especulação" 13h, FOMC, pacote desidratado | 6,289 | +2,36 | +6,89 |
| 19 a 20/12 | leilões do BC, vídeo de Lula, PEC | 6,152; 6,084 | -2,25; -0,40 | +4,23 |

Os valores brutos de fechamento do proxy diferem das cotações oficiais de fechamento (ex.: 18/12: oficial R$ 6,2657 a R$ 6,2672; proxy 6,289) por causa do horário. [fato] Fontes do recorde: dgabc.com.br/Noticia/4182800 e oliberal.com/economia (dólar fecha a R$ 6,26). Conclusão: do aumento anormal acumulado de 18/11 a 18/12 (+6,9 pp), a fala da Janja contribui com zero ou negativo; o pacote fiscal (27-28/11) explica ~3,5 pp (mais da metade), e o resto veio da erosão fiscal, Fed e dias sem evento tabelado. Se a fala da Janja tivesse efeito grande, deveria aparecer em 18-26/11; não aparece. **Isso não prova que a Janja não possa ter efeito em outro contexto** (poucos eventos pessoais, n=9).

## 4. Parte B: idade e saúde

### 4.1 Probabilidades atuariais [cálculo próprio]

Fonte: IBGE, Tábua Completa de Mortalidade 2024, homens (ftp.ibge.gov.br/Tabuas_Completas_de_Mortalidade/Tabuas_Completas_de_Mortalidade_2024/xlsx/homens.xlsx). q(80) = 62,28 por mil; e(80) = 8,28 anos; e(81) = 7,80. Idade de Lula: 80,94 em 5/10/2026 (nasceu em 27/10/1945; completou 80 em 27/10/2025, CNN Brasil), 81,18 em 1/1/2027, 85,18 em 1/1/2031. A tábua de 2023 dá resultados idênticos a 0,1 pp.

| janela | idade | morte, tábua IBGE 2024 | com multiplicador de risco 0,9 / 0,75 / 0,6 [hipótese] |
|---|---|---|---|
| 5/10 a 25/10/2026 (2º turno) | 80,9 | 0,35% | 0,3 / 0,3 / 0,2% |
| 5/10 a 1/1/2027 (posse) | 80,9 a 81,2 | 1,65% | 1,5 / 1,2 / 1,0% |
| mandato 1/1/2027 a 31/12/2030 | 81,2 a 85,2 | **28,95%** | 26,5 / 22,6 / 18,5% |
| 4 anos a partir de 80,0 (cenário "80 anos" do pedido) | 80,0 a 84,0 | 25,96% | n/d |
| por ano do mandato | | 6,9; 7,7; 8,6; 9,6% | |

O multiplicador de risco é **suposição de ajuste** (acesso a médicos, exames, perfil socioeconômico). A tábua é a média masculina brasileira; presidentes com acesso a cuidado de ponta costumam ter mortalidade menor, mas não encontrei estimativa brasileira citável para o fator, então a faixa 0,6 a 0,9 é minha. Histórico documentado de Lula: queda e hemorragia/hematoma intracraniano com cirurgia em 10/12/2024; exames para catarata em jan/2026; check-up com resultados normais em mar/2026 (plantaobrasil.net/news.asp?nID=153445); retirada de carcinoma basocelular no couro cabeludo e infiltração no punho em abr/2026 (otempo.com.br, 26/4/2026). Esses itens não estão no cálculo; apontam para acompanhamento frequente e não para risco calculável.

**Incapacidade (sem morte).** [estimativa, base fraca] Incidência de AVC aos 80 a 85 anos: 17,2 por mil pessoas-ano (revisão sistemática, PMC3161203); incidência de demência em homens de 80 a 84: 6,7 por mil pessoas-ano (estudo Monzino 80+, Itália, Alzheimer's & Dementia 2020); prevalência de demência de 80 a 84 anos no Brasil: 13% a 41% entre estudos (revisão sistemática PMC10865913; o valor de 21,2% de um consenso de especialistas de 2019 vem de resumo de busca, fonte primária não conferida, estudos de alta qualidade, todos em São Paulo, população urbana). Em 4 anos: AVC ≈ 6,7%, demência ≈ 2,6%. Só uma fração deles impede governar (suposição: 1/3 a 1/2), e Lula está em atividade plena hoje (seleção positiva). Resultado: 2% a 8% de incapacidade grave no mandato, central 4% [hipótese]. **Não achei base brasileira para risco de incapacidade presidencial.**

**Comparação (mesma régua).** Flávio Bolsonaro, 45,4 anos (nasceu em 25/4/1981): morte no mandato 1,98% pela mesma tábua (1,5% com multiplicador 0,75). Saúde documentada: procedimento oftalmológico em 4-5/3/2026, sem restrição declarada (ncnews.com.br, 5/3/2026). **Cauda não médica documentada:** inquérito no STF (PF, aberto em julho/2026 pelo ministro André Mendonça, com parecer favorável da PGR citando "indícios consistentes de condutas ilícitas") sobre o financiamento do filme Dark Horse; documentos divulgados em setembro mostram negociação de US$ 24 milhões com Daniel Vorcaro (CNN Brasil/Gustavo Uribe e Brasil de Fato, 3/10/2026). Não estimo probabilidade de condenação, inelegibilidade ou saída por esse caminho (sem base). Para Lula, caudas jurídicas/políticas semelhantes (Master e contrato do escritório da mulher de Moraes) são **disputadas** (ver CLAUDE.md); idem sem probabilidade.

### 4.2 Sucessão e mercado

- [fato constitucional, citado de memória; a consulta ao Planalto falhou com 503 e não conferi o texto] Art. 79 da CF: o vice substitui o presidente em impedimento e lhe sucede em caso de vaga. Art. 80: na falta do vice, presidente da Câmara, do Senado e do STF. Art. 81: eleição só quando vagam presidente **e** vice. Art. 77, §4º: se morte, desistência ou impedimento de candidato ocorrer antes do 2º turno, convoca-se, entre os remanescentes, o de maior votação. [leitura, não verificada] O Brasil não tem rito formal para declarar incapacidade presidencial além de "impedimento".
- Alckmin foi confirmado vice na chapa de 2026 (poder360.com.br, "Alckmin é confirmado como vice"). A imprensa descreve-o como centrista pró-empresa e fator de estabilidade para o mercado [leitura da imprensa, não medida]. Há reportagem (Brasil 247, com fonte não nomeada na página) de que Lula avalia Alckmin na Fazenda num segundo mandato: **não verificado**.
- **Única observação de mercado com saúde de Lula:** cirurgia de 10/12/2024: o dólar caiu e a Bolsa subiu (Poder360: "Dólar fecha abaixo de R$ 6 após anúncio de operação"; JB: "ativos se valorizam quando presidente está na UTI"; InvestNews: "excêntrica reação do mercado"). Anormal do BRL: -0,52 pp (dia 0), -1,36 pp (11/12), mas com IPCA e Copom no mesmo intervalo: **confundido**. [hipótese] O mercado reage a quem substitui, não à idade; com Alckmin como sucessor, a reação a um evento de saúde pode ser neutra ou até positiva. Isso não está provado por um único caso.
- **Biden 2024** [fato, imprensa]: após o debate de 27/6/2024, 67% a 74% dos americanos diziam que Biden era velho demais (Gallup/NYT-Siena, via reportagens) contra 37% a 43% para Trump; os mercados reagiram em 28/6 com alta de juros longos e do dólar ("Trump trade"), ou seja, **precificaram a chance de o outro vencer**, não a idade em si; Biden desistiu em 21/7. O gatilho foi um **evento visível**, não a idade.
- **Pesquisas brasileiras sobre idade de Lula:** PoderData (campo 18-20/7/2026, 2.500 entrevistas, ±2 pp): 50% dizem que a idade não é problema para a reeleição, 43% dizem que é, 7% sem opinião; homens e jovens de 16 a 24 anos preocupam-se mais, mulheres e idosos menos; Nordeste 60% "não é problema", Sul 50% "é problema" (cnnbrasil.com.br/eleicoes/poderdata-para-50-idade-de-lula-nao-e-problema-para-43-e-problema). A mesma pesquisa mostrava +24 pp de "não é problema" em relação a julho/2025 segundo o Poder360 (não conferi a série). Genial/Quaest de outubro/2025: 56% diziam que Lula não deveria se candidatar (a pergunta não é de idade). Não encontrei Datafolha específico de idade nesta rodada.

### 4.3 "A frequência de gafes sobe com a idade?"

[sem evidência] Não encontrei estudo quantitativo de gafes políticas por idade. A literatura achada: erros de fala em adultos mais velhos não diferem muito dos jovens em condições normais (4,7 vs 3,9 por 100 palavras em fala lenta, estudo geral de linguagem); declínio executivo e liderança política é discutido em ensaios (Cambridge, "Cognitive decline and political leadership", 2024; Karger "Aging heads of state") sem medir gafes; especialistas ouvidos por imprensa advertem que gafes não diagnosticam declínio cognitivo. Nos meus dados: eventos do lado Lula de 2023 a 2026 (idade 77 a 80) têm 1 evento de alto impacto limpo (Haddad, fiscal) e nenhum em 2023, 2025, 2026, sem tendência crescente; **n é pequeno demais para concluir**, e não coletei os mandatos 2003-10 para comparar a mesma pessoa mais jovem.

## 5. Parte C: parâmetros simétricos propostos

### 5.1 Choque de fala (cenarios e simulador)

| parâmetro | central | faixa plausível | base |
|---|---|---|---|
| taxa λ de eventos de alto impacto, por lado | 0,5/ano | 0,2 a 1,0 | Parte A: 0,77 (Lula) e 0,57 (Bolsonaro) por ano, IC 0,16 a 2,25; limpos 0,26 e 0,29 [estimativa] |
| razão λ_Lula/λ_Flávio | **1,0** | 0,5 a 2,0 | taxas indistinguíveis, p = 0,71; igualdade é possível e é o padrão |
| tamanho no dia 0 (log USD/BRL, só fala fiscal/institucional/ato) | mediana 3% (lognormal, dispersão 0,3) | mediana 2% a 4% | 7 casos: 2,5 a 4,5 pp, mediana 2,8 [cálculo próprio] |
| tamanho para fala pessoal/diplomática | 0 a 0,5 pp | 0 a 1 pp | 0 de 9 acima de 1,65σ; módulo 0,73 vs 0,63 do acaso |
| fração adversa | 80% | 60% a 90% | 6 de 7 eventos grandes adversos [estimativa] |
| persistência após 5 dias | 0,8 | 0,2 a 1,1 | mediana 0,83 [cálculo próprio] |
| persistência após 20 dias | 0,6 | 0,2 a 1,0 | observado 0,8 a 1,0, mas contaminado; reduzido por reversões [hipótese] |

Como implementar sem viés: (i) o choque vem do **ocupante** do cargo no cenário: no caminho "Lula governa" sorteia-se o processo do lado Lula (presidente, Fazenda, Janja), no caminho "Flávio governa" o do lado Flávio (presidente, Fazenda, família); mesmos parâmetros por padrão; (ii) o sorteio dos dois processos é **independente**, então a diferença pareada ganha variância, não média; (iii) quando λ e tamanho são iguais, o efeito esperado em D é zero; (iv) o `fx_ruido_dp = 0,10` de `cenarios/premissas.py` (R5: "12 a 15% de volatilidade; parte já nos regimes") já é maior que a variância total de choques de fala estimada (2 lados × 0,5/ano × 3%² = 0,0009, desvio ~3%/ano), então o termo é em grande parte **redundante** com o ruído existente; recomendo acrescentá-lo só como componente identificável do ruído, sem aumentar o total. No simulador eleitoral o choque de fala é erro simétrico na margem; esta rodada **não** mediu efeito de fala em pesquisa (sem event study de pesquisas), então não proponho valor para o voto, só a sensibilidade abaixo.

### 5.2 Termo de cauda idade/saúde (só Lula; Flávio com a mesma regra, 2% de morte)

| parâmetro | central | faixa | base |
|---|---|---|---|
| morte no mandato (1/2027 a 12/2030) | 22,6% | 18,5% a 29,0% | IBGE 2024 e multiplicador 0,6 a 0,9 [cálculo + hipótese] |
| incapacidade grave sem morte | 4% | 2% a 8% | [estimativa, base fraca] |
| saída antecipada total | ~26% | 20% a 37% | soma aproximada |
| momento da saída | risco crescente (6,9; 7,7; 8,6; 9,6% por ano); metade do mandato em média | | tábua |
| sucessão | Alckmin assume até 2030 (art. 79) | | CF |
| regime do sucessor (hipótese a ser fixada pelo usuário) | (S1) igual ao de Lula; (S2) mais crível fiscalmente (regime de Flávio); (S3) S1 mais prêmio de transição de 1 a 3% no câmbio por poucos meses | | sem evidência no 2024 de prêmio de saúde |
| ocorrência antes do 2º turno | 0,35% (0,2 a 0,35%) | | art. 77 §4 se verificado |

### 5.3 Sensibilidade (rodada rápida, não altera os arquivos publicados) [cálculo próprio]

**Household (cenarios, conjunto "central", 20.000 trajetórias por vencedor, semente 11, 10 famílias; D = índice de Lula menos índice de Flávio, média 2027-2030; erro de Monte Carlo ≈ 0,3 pp em P):**

| experimento | ΔD médio (pontos de índice; faixa entre famílias) | ΔP(L > F em 2030) (média; faixa) |
|---|---|---|
| choque simétrico, λ total 1,1/ano, 3% (ruído cambial 0,100 → 0,105) | +0,001 (-0,003 a +0,006) | 0,0 pp |
| choque simétrico, λ total 3,6/ano, 4% (ruído 0,100 → 0,126) | +0,002 (-0,007 a +0,020) | +0,2 pp (0,0 a 0,3) |
| choque assimétrico: câmbio do cenário Lula +2 pp (persistente no regime) | -0,023 (-0,042 a +0,028) | +0,6 pp (0,3 a 1,2) |
| choque assimétrico: câmbio do cenário Lula +5 pp | -0,058 (-0,110 a +0,063) | +1,4 pp (0,7 a 2,8) |
| sucessão com 10% das trajetórias de Lula passando ao regime de Flávio (limite superior) | +0,018 (-0,031 a +0,040) | -0,7 pp (-1,2 a -0,3) |
| idem 20% | +0,032 (-0,056 a +0,069) | -1,2 pp (-2,2 a -0,6) |
| idem 28% | +0,047 (-0,082 a +0,103) | -1,8 pp (-3,3 a -1,0) |

Leituras: (1) choque de fala simétrico não muda nada; (2) mesmo assimétrico, o efeito médio é |ΔD| ≤ 0,06 ponto de um índice de base 100 e o sinal varia por família (quem tem renda exposta ao câmbio ganha com dólar alto no modelo); (3) a sucessão, mesmo no limite superior (sucessor com o regime de Flávio por todo o mandato), move D em ≤ 0,05 ponto na média e P(L>F) em ≤ 2 pp. **O modelo já embute um efeito candidato-específico muito maior que qualquer termo de fala:** `impacto_cambio` central de +8% para Lula e -7% para Flávio ("mercado precifica", bancos), com decaimento de 35% ao ano. Dados desta rodada que dão ordem de grandeza (não incluídos na tabela): indicação de Flávio em 5/12/2025 teve +2,5 pp anormal; a cotação ao vivo de 5/10/2026 às 16h32 era R$ 4,985 contra PTAX de 5,2238 em 2/10 (-4,6%, dado parcial, após o 1º turno de 4/10 com Flávio 47,03% x Lula 45,16% dos válidos segundo a imprensa). **Identidade do vencedor move o câmbio mais que fala.**

**Simulador eleitoral (calibrado, referência 3/10/2026, antes do 1º turno; P(Lula vence) = 35,9%, margem 2T com média -2,5 pp e desvio ~7,3 pp):** [cálculo próprio] Densidade da margem em zero ≈ 0,052 por pp, então **cada 1 pp de deslocamento persistente na margem vale ~5,2 pp em P(Lula)**; um choque simétrico de desvio 0,5 pp adiciona variância desprezível (< 0,05 pp em P). Pelo canal de saúde até 25/10: -0,35% × P ≈ -0,13 pp; até a posse, o vice-eleito assume e a chapa continua. O efeito relevante é em P(**Lula governa o mandato inteiro**) ≈ 0,359 × (1 - 0,26) ≈ 26,6% (para saída de 20% a 37%: 28,7% a 22,6%). Esse P está desatualizado pelo 1º turno e serve só de ordem de grandeza.

## 6. Limites e o que não consegui verificar

- Seleção: 34 eventos achados por busca em motor de busca com resumos; a lista pode omitir eventos sem cobertura de mercado. Critério (b) infla efeitos. Sem verificação sistemática de contagem de notícias nos dois campos.
- Citações: várias estão em tradução da fonte ou paráfrase (marcado no CSV); o original em português de L03, L11, L14, B01, B05, B08, B10, B11, B14 não foi verificado.
- DI e intradiário indisponíveis; PTAX não serve para falas à tarde; o "fechamento" é um proxy (~21h) com erro de 0,3 a 0,5 pp; FRED confirma só os eventos grandes.
- A classificação "confundido" depende de confusores que conheço ou que a fonte cita; alguns (ex.: FOMC de 15-16/9/2020, Powell em 23/9/2025, PCE em 27/10/2023, escalada EUA-China em ago/2019) são de conhecimento geral, **não checados**.
- Horário exato da fala/divulgação não verificado em L09, L12, L16, B15; mudanças de dia 0 mudam o resultado desses casos.
- Atenção da mídia não medida; efeito em pesquisas não medido; efeito de eventos de saúde no mercado só com 1 observação confundida.
- Constituição (arts. 77, 79 a 81) citada de memória: o Planalto devolveu 503. O texto foi lido em memória e deve ser conferido.
- Os parâmetros da Parte C são faixas e hipóteses; a faixa do multiplicador de risco (0,6 a 0,9) e a de incapacidade (2% a 8%) não têm fonte brasileira.
- Os dados de mercado de 2026 vêm de Yahoo/imprensa e o último dia (5/10/2026) é cotação ao vivo parcial.
- Sobre o viés do próprio painel (CLAUDE.md, Regra 1, brecha 9): a seleção, a ordem e o fato de o lado Lula ter 16 eventos e o lado Bolsonaro 18 são decisões minhas; o critério e o CSV completo estão abertos para auditoria.

## 7. Resumo da aba

1. Falas e atos fiscais/institucionais movem o BRL em ~3 pp no dia do ato, nos dois lados, com frequência indistinguível (0,5 a 0,8 por ano de alto impacto por lado) e quase sempre com confusor; falas pessoais/diplomáticas (Janja/Musk incluída) não se distinguem de um dia qualquer em 9 casos.
2. O dólar a R$ 6,26 em dez/2024 é pacote fiscal (+3,5 pp em 27-28/11), Fed e desidratação do pacote; a Janja teve efeito nulo ou negativo nos pregões seguintes.
3. Idade: 29% de morte no mandato pela tábua do IBGE (22,6% com ajuste hipotético), mais 2% a 8% de incapacidade; Alckmin assume; o mercado não mostrou prêmio de saúde no único caso observado (confundido).
4. Nos modelos, choque de fala com taxa igual nos dois lados não altera D nem P; o termo de cauda de idade altera, no limite superior, D em ≤ 0,05 ponto e P(L>F) em ≤ 2 pp, e muda sobretudo P(Lula governa o mandato inteiro) (~26%).
5. A tese do usuário está **parcialmente apoiada** (fala fiscal/institucional importa; custo persiste na mediana; idade eleva a cauda de saída) e **parcialmente não apoiada** (gafe pessoal sem efeito detectável; sem prova de efeito maior de um lado; sem evidência de gafe crescente com idade).
