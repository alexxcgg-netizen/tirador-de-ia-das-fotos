# Auditoria de neutralidade: ressalvas assimétricas no painel e nos relatórios

> **Foto auditada:** 05/10/2026, 04:00–04:10 UTC (01:00 em Brasília), commit `1b27afc` ("Painel: aba Realidade × discurso").
> Arquivos lidos nessa versão: `simulador/web/index.html` (sha256 `663e1f6c…7763`), `simulador/web/realidade.json` (`e96fb9e3…f1e4`), `simulador/web/nordeste.json`, `reports/*.md` e, nesta pasta, `checagem_promessas_discursos.md` e `medido_vs_vivido.md`.
> Outro agente estava editando a aba "Realidade × discurso" durante a auditoria. Para repetir a auditoria na versão final, use a seção 8. O commit `44b2d71` (notas de conta das políticas), publicado depois da foto, não foi auditado.
> Esta auditoria é somente leitura: não altera o painel nem os relatórios.

## 1. Resposta curta

**Não há viés sistemático de amaciar só as críticas a Lula.** No painel, 58% das críticas ao governo Lula trazem alguma ressalva, e 59% das críticas a Flávio/PL/Bolsonaro também trazem. Nos dois lados, cerca de metade dessas ressalvas não vem com número.

**O padrão "os preços sobem, mas por outro lado…" existe e aparece nos pontos mais visíveis.** São quatro casos:

- o cartão de percepção de preços;
- os dois acertos de Flávio sobre o governo (carga tributária recorde e maior juro real do mundo);
- a explicação "custo de vida" no Nordeste;
- o card do IBGE.

Nesses casos, a ressalva a favor do governo:

- não tem número;
- ou usa um número que não sustenta a conclusão;
- ou deixa de fora um dado contrário que está nas notas de pesquisa.

**A maior assimetria é estrutural, não de redação.** A checagem testa 5 promessas de Flávio por "conta que feche" e nenhuma promessa de Lula para 2027–30. A tarifa zero, por exemplo, custaria R$ 100–110 bi por ano e não tem fonte de financiamento. Além disso, uma projeção do próprio governo (M6, PLOA 2027) e um ataque de veículo de oposição (M1, Revista Oeste) estão contados como "mercado".

**Também há assimetrias a favor de Flávio:**

- E7 usa o IVA de 20%, que a própria checagem classificou como "sem base", para defendê-lo;
- F12 e E5 omitem a PEC Kamikaze, as trocas na Petrobras e a LC 194/2022.

## 2. Escopo e método

1. **Extração.** O script da seção 8 percorre:
   - o texto visível do `index.html`;
   - os JSONs que o painel renderiza (`realidade.json`, `nordeste.json`, `curiosidades.json`);
   - os relatórios e as duas notas.

   Ele marca cada sentença com ressalva ("mas", "embora", "ainda assim", "por outro lado", "em parte", "contexto", "em sentido contrário", "atenua", "legítimo" etc.) dentro de uma unidade que cita um dos lados. Saíram 187 candidatas. O script também diz se há número depois do marcador.
2. **Classificação manual.** Cada afirmação avaliativa do painel foi classificada pelo **polo que ela atinge**:
   - Lula/PT/governo 2023–26;
   - Flávio/PL/governo Bolsonaro 2019–22.

   A polaridade é crítica, elogio/defesa ou fato neutro. Um veredito "falso" sobre uma frase de Flávio conta como crítica a Flávio, mesmo que funcione como defesa do governo. O mesmo vale para o outro lado.
3. **Ressalva com ou sem dado.** Conta como "com número" a ressalva que traz um número da fonte na própria unidade. Conta como "sem número" a ressalva qualitativa: "parte vem de…", "atenuam", "chama atenção, mas…".
4. **Relatórios.** O resumo executivo, as Propostas e o Briefing do 2º turno foram lidos inteiros. Os outros três relatórios foram triados pelo script e conferidos por amostragem.

## 3. Contagens

### 3.1 Painel (aba Realidade × discurso e aba Nordeste; matriz completa no apêndice)

| | Lula / PT / governo 2023–26 | Flávio / PL / Bolsonaro 2019–22 |
|---|---|---|
| **Críticas** | **36** | **22** |
| sem ressalva | 15 (42%) | 9 (41%) |
| com ressalva apoiada em número | 11 | 7 |
| com ressalva sem número | 10 | 6 |
| % das ressalvas sem número | 48% | 46% |
| **Elogios / defesas** | **11** | **2** |
| sem ressalva | 2 | 1 |
| com ressalva apoiada em número | 4 | 0 |
| com ressalva sem número | 5 | 1 |

**Recorte só da checagem (14 + 14 afirmações):**

| | Lula/PT | Flávio/PL |
|---|---|---|
| Vereditos críticos | 11 | 12 |
| com ressalva | 4 (L4, L6 com número; L7, L12 sem) | 9 (F1, F2, F3, F4, F6, F13 com número; F8, F12, F14 sem) |
| Vereditos "correto" | 3 (L1, L3, L9) | 2 (F5, F7) |
| ressalva do "correto" | caveats contra o próprio Lula, 2 de 3 com número | caveats **a favor do governo**: F5 sem número, F7 com número que não sustenta a ressalva |

**Como ler:**

- Na checagem, as críticas a Flávio recebem *mais* ressalvas que as críticas a Lula. Em geral essas ressalvas são fatos contra o governo, por exemplo "sob Lula pioraram a inadimplência e o custo da dívida".
- O ponto fraco está nos dois "corretos" de Flávio. Quando a oposição acerta sobre um problema do governo, a frase seguinte tira o peso do problema e não traz conta.
- A diferença no número de elogios (11 contra 2) vem sobretudo do desenho: há um governo em exercício. Mesmo assim, o painel omite tanto os pontos positivos quanto os negativos do governo 2019–22 (seção 6).

### 3.2 Relatórios (triagem)

| Arquivo | Candidatas (com número / sem número) | Ressalvas sem respaldo confirmadas |
|---|---|---|
| Resumo executivo | 4 / 0 | 1 herdada (contagem "5 sem base", linha 85) |
| Propostas e viabilidade | 28 / 14 | 1 de escrutínio desigual (linha 138; ver H11) |
| Briefing 2º turno | 0 / 7 | 0. Em 366–381 há equilíbrio: "contradição registrada" aparece para os dois lados |
| Briefing presidencial | 10 / 11 | 1 (linha 30, "escândalos que atingem todos os lados") |
| Complemento e Avaliação 1º turno | 14 / 9 | 0. São ressalvas metodológicas, não avaliativas |
| `checagem_promessas_discursos.md` | 36 / 12 | é a fonte das reescritas abaixo e quase sempre tem o número que o painel cortou |
| `medido_vs_vivido.md` | 7 / 3 | 1 (linha 19, "isso explica boa parte do pessimismo", afirmação causal sem teste) |

## 4. Ressalvas sem respaldo e reescritas propostas

Os itens H1 a H8 suavizam críticas ao **governo Lula**. Os itens H9 a H12 suavizam críticas a **Flávio/Bolsonaro**. H13 e H14 são de importância baixa. Cada reescrita usa apenas dados que já estão nas notas.

**H1. `simulador/web/realidade.json:6` (meta.percepcao).**
- Texto atual: "…num trimestre em que o IPCA de alimentação e bebidas caiu… A memória ancora no nível de 2019 (+76% em comida), não na taxa do mês."
- Problema: a frase causal ("ancora em 2019") não tem teste para o Brasil. Ela também omite a alta atual de itens de compra frequente, que é a outra explicação documentada em `medido_vs_vivido.md:203`.
- Reescrita: "…num trimestre em que o IPCA de alimentação e bebidas caiu em junho, julho e agosto. Há duas explicações documentadas. A primeira é o nível acumulado: alimentação no domicílio +76,3% desde jan/2019, a maior parte em 2019–22. A segunda são itens de compra frequente que continuam subindo: feijão carioca +44,2% em 12 meses e café moído +45,9% desde jan/2023 (SIDRA). A percepção também é partidária: 77% dos eleitores de Flávio e 14% dos de Lula veem piora (Datafolha, mar/2026)."

**H2. `realidade.json:220` (F7, "maior juro real do mundo", correto).**
- Texto atual: "A Selic é do Copom autônomo (LC 179/2021). Em dez/2022 a Selic também estava em 13,75%."
- Problema: o número citado é a Selic nominal, não o juro real. A ressalva também tira da nota o trecho "hoje presidido por Galípolo, indicado de Lula" (`checagem_promessas_discursos.md:197`).
- Reescrita: "A Selic é decidida pelo Copom autônomo (LC 179/2021), hoje presidido por Galípolo, indicado de Lula. Ela subiu a 15% em jun/2025 e cai desde mar/2026. Em dez/2022 a Selic nominal também era de 13,75%."

**H3. `realidade.json:218` (F5, "recorde de carga tributária", correto).**
- Texto atual: "Parte vem de crescimento da base e formalização…"
- Problema: o tamanho dessa "parte" não foi medido.
- Reescrita: "Houve aumento de tributos (reoneração de combustíveis e da folha, IOF de 2025, fundos exclusivos e offshores; ver E2). Não foi medido quanto do +1,2 p.p. vem de alíquotas e quanto vem de base e formalização. A isenção do IR reduz a carga da renda média formal desde 2026, mas ainda não há dado realizado."

**H4. `simulador/web/nordeste.json:991` (explicação "Custo de vida", contra).**
- Texto atual: "…reajuste do Bolsa Família e salário mínimo atenuam."
- Problema: não há dado para "atenuam". O próprio painel mostra efeito nulo do reajuste (BTG/Nexus).
- Reescrita: "Aprovação no NE de 61% em setembro (Quaest), mas a desaprovação subiu de 29% para 35% entre julho e setembro. Entre beneficiários do Bolsa Família, Lula ficou em 64% antes e depois do reajuste (BTG/Nexus), sem efeito adicional medido."

**H5. `nordeste.json:1015` (explicação "Escândalos", contra).**
- Texto atual: "no NE o governo foi mais bem avaliado na resposta ao INSS."
- Problema: falta o número, que está em `nordeste_opiniao.md:142`.
- Reescrita: "…em 2025, 31% no NE acharam satisfatória a resposta do governo ao INSS, contra 16–18% no Sul e no Sudeste (Quaest, via busca, não verificado na fonte)."

**H6. `realidade.json:178` (card IBGE).**
- Texto atual: "…greve contra a gestão Pochmann, fundação IBGE+ considerada irregular pelo TCU, e, no governo anterior, o corte do orçamento do Censo em 2021."
- Problema: a comparação com o governo anterior não tem relação com a crise atual. A atribuição também é imprecisa: segundo a nota, quem cortou foi o Congresso.
- Reescrita: tirar o contraponto desta frase e, se for o caso, pôr em frase própria: "Crise anterior, de natureza orçamentária: em 2021 o Congresso cortou o orçamento do Censo de ~R$ 2 bi para R$ 71 mi, e a presidente do IBGE pediu demissão."

**H7. `realidade.json:137` (card emprego).**
- Texto atual: "Em sentido contrário: a maior parte dos 10,4 mi de ocupados a mais desde 2019 tem carteira."
- Problema: a base de 2019 cruza os dois governos e esconde o dado mais recente.
- Reescrita: "De 2019 a 2026, 5,7 dos 10,4 mi de ocupados a mais são empregados com carteira. Na divulgação da PNADC de jun–ago/2026, porém, 528 mil dos 774 mil novos ocupados eram informais (base de comparação não informada pela fonte; confirmar no IBGE antes de publicar)."

**H8. `realidade.json:265` (leitura 2019–22 x 2023–26).**
- Texto atual: "O investimento estrangeiro e o PIB foram melhores em 2023–25… Pandemia, juros globais, tarifas dos EUA e petróleo pesam nos dois períodos."
- Problema: a pandemia pesa num período só. O painel classifica L5 como enganoso por esse mesmo motivo, mas não aplica a mesma regra à própria comparação.
- Reescrita: "O PIB cresceu mais em 2023–25 (2,98% ao ano) que em 2019–22 (1,43%), período que inclui a recessão da pandemia (−3,28% em 2020). Como em L5, a diferença não mede só política econômica."

**H9. `realidade.json:273` (E7, "pró-empresa só para os ricos", exagerado).**
- Texto atual: "…mas o plano mantém programas sociais e um IVA menor reduz imposto sobre consumo…"
- Problema: a defesa se apoia numa promessa que o próprio painel classifica como "sem base" (F10). Também omite a desvinculação dos pisos e o detalhe do escritório (`checagem…md:336`).
- Reescrita: "Há sinal de viés para a alta renda: a emenda para isentar dividendos de sociedades de profissionais liberais beneficiaria o próprio escritório de Flávio e não entrou na lei. O plano promete manter os programas sociais, mas a equipe falou em desvincular os pisos de saúde e educação (CNN, 25/09), e o IVA menor não tem fonte de compensação (F10). 'Só para os ricos' não tem base. O efeito distributivo depende de cortes que não foram listados."

**H10. `realidade.json:225` (F12).**
- Texto atual: "Ainda assim, os déficits primários voltaram com Lula."
- Problema: a ressalva, a favor de Flávio, não tem número. Do lado de Bolsonaro, o texto também omite os valores.
- Reescrita: "O superávit de 2022 teve limitação de precatórios (EC 113 e 114/2021) e a PEC Kamikaze (R$ 41,2 bi). Ainda assim, o primário voltou a ser deficitário com Lula (−0,4% do PIB em 2024–25), e o nominal foi de 4,57% para 8,3%–8,8% do PIB."

**H11. `reports/Propostas e viabilidade dos candidatos.md:138`.**
- Texto atual: dá a taxa de promessas cumpridas de Bolsonaro (33% no G1, 15% na Lupa) e acrescenta que "os métodos diferem dos usados para Lula". Mas a taxa de Lula não aparece em nenhum ponto do relatório.
- Reescrita: acrescentar "Para Lula 3, o G1 conta 26 de 36 compromissos cumpridos (72%) até jun/2026. Um levantamento de meio de mandato deu 28%. Os recortes diferem, por isso as taxas não se comparam diretamente" (`research_notes/Propostas…/planos_governabilidade_historico.md:112–122`).

**H12. `reports/Briefing eleição presidencial 2026.md:30`.**
- Texto atual: "escândalos que atingem todos os lados (Banco Master, INSS)."
- Problema: "todos os lados" equipara os dois casos sem número.
- Reescrita: "o caso Master atinge políticos dos dois campos e do centro. A fraude do INSS se concentrou no governo Lula (62,5% dos descontos indevidos de 2019–24, segundo a CGU), que também a interrompeu e ressarciu mais de 4 milhões de aposentados."

**H13 (importância baixa). `realidade.json:96` e `:343` (bandeira verde).**
- Texto atual: "chama atenção pelo momento, mas segue regra paramétrica."
- Reescrita: acrescentar o número da justificativa: "a Aneel citou chuvas e a queda do custo marginal de operação no Norte, de R$ 1.866,74 para R$ 461,46/MWh (`medido_vs_vivido.md:74`)."

**H14 (importância baixa). `realidade.json:221` (F8).**
- Texto atual: "Os juros futuros podem cair se o mercado acreditar no ajuste."
- Reescrita: acrescentar a referência numérica: "o Morgan Stanley projeta Selic de 9,75% no cenário favorável".

## 5. A mesma régua vale para os dois lados?

| # | Assimetria | Onde | A favor de | Correção |
|---|---|---|---|---|
| S1 | **Promessas.** Cinco promessas de Flávio são testadas por "conta que feche" (F8–F11, F9). Nenhuma promessa de Lula para 2027–30 entra na checagem: tarifa zero (R$ 100–110 bi/ano), ampliação de BF, BPC e mínimo sem fonte de financiamento, e "o resultado fiscal virá da retomada do crescimento" (plano, p. 49). O relatório de Propostas trata desses pontos; o painel não. | `realidade.json` checagem | Lula | Incluir 2 ou 3 promessas de Lula com a mesma escala: tarifa zero e âncora "crescimento" sem meta de dívida. Ver também S2. |
| S2 | **Atribuição de lado.** M1 ("Lula quebrou o Brasil", Revista Oeste) está em "Mercado", mas a mesma revista aparece com Flávio/PL em F12. M6 (superávit do PLOA, MPO) é afirmação do **governo** e está em "Mercado". | `realidade.json:228`, `:233` | os dois (tira um "exagerado" de cada placar) | Mover M6 para Lula/PT. Mover M1 para Flávio/PL ou criar o lado "imprensa partidária". |
| S3 | **Categoria errada.** F13 ("50 milhões sob facções") é um número impreciso, não uma promessa, mas está marcado como "sem base", categoria definida para "promessas sem conta". Isso infla de 4 para 5 o "sem base" de Flávio, e o resumo executivo repete o 5 (linha 85). | `realidade.json:226`; Resumo:85 | Lula | Reclassificar como "exagerado". |
| S4 | **Verbo mais brando.** F14 diz que a regulamentação "coincidiu com a explosão do setor", mas a nota diz que ela "de fato abriu o mercado formal" (`checagem…md:55`). | `realidade.json:227` | Lula | Usar "abriu o mercado formal". |
| S5 | **Mesmo critério para comparar períodos.** Quando Lula compara 2019–22 com 2023–26, o painel marca enganoso (L5). Flávio também é marcado enganoso quando atribui ao governo atual uma alta de 2019–22 (F2, F3). Mas a comparação do próprio painel (PIB, IDP) não recebe a mesma ressalva. | `realidade.json:265` | Lula | H8. |
| S6 | **Ressalva nos "corretos".** Os acertos de Lula (L1, L3) recebem caveats contra o próprio Lula, com número. Os acertos de Flávio sobre o governo (F5, F7) recebem caveats que eximem o governo, sem número ou com número inadequado. | `:218`, `:220` | Lula | H2 e H3. |
| S7 | **Erros do mercado.** O veredito que favorece Lula em 2003 ("pessimismo excessivo") traz a ressalva "mas a renda real caiu 7,4%". O veredito contra o programa de Bolsonaro em 2019 ("otimismo excessivo") vem sem ressalva. | `realidade.json:288–289` | Bolsonaro, no 2003; contra Bolsonaro, no 2019 (direções opostas) | Usar o mesmo formato nos dois, ou tirar as duas ressalvas. |
| S8 | **"Mesma régua".** A aba diz aplicar "mesma régua para as medidas do governo e para as propostas da oposição", mas só o governo tem tabela de incidência. A oposição tem uma frase. | `index.html:653`, `realidade.json` empresas | indefinido | Dizer explicitamente que as propostas de Flávio não têm valores para montar a tabela, ou montar a tabela com as faixas de F9 e F10. |
| S9 | **Vocabulário.** "Erros" para Lula e "problemas" para Flávio (padrao[0] e [1]); "falso" e "exagerado" usados da mesma forma dos dois lados. Os dois lados têm 3 falsos, e o painel diz isso. | `realidade.json:193` | nenhum relevante | Opcional: usar "erros" nos dois. |
| S10 | **Fonte fraca.** A retórica de Lula contra a autonomia do BC em set/2026 foi retirada por ter só fonte de agregador (Resumo:88). F12 ficou com data não confirmada, mas a fala em si tem fonte. A regra é coerente. | Resumo:88 | nenhum | Nada a corrigir; manter o registro. |

## 6. Omissões: fatos críticos que estão nas notas e faltam no painel ou nos relatórios

**Contra o governo Lula (faltam no painel):**

1. Feijão carioca +44,2% em 12 meses e café +45,9% desde 2023 (`checagem…md:113`, tabela da seção 4). É o dado mais direto para "os preços estão subindo" e não aparece em nenhum ponto do painel (C03, C20).
2. Copom presidido por Galípolo, indicado de Lula (`checagem…md:48, :197`). Ausente de F7.
3. Negativados de 69,4 mi (dez/22) para 83,9 mi (ago/26), ou +14,5 mi, contra +3,5 mi entre abr/20 e dez/22 (`checagem…md:181`). F3 diz que "o salto do estoque foi em 2020–22", o que só vale para a razão endividamento/renda.
4. Na divulgação da PNADC de jun–ago/2026, 528 mil dos 774 mil novos ocupados eram informais (Propostas:34; a base de comparação deve ser confirmada no IBGE). O painel só traz a comparação com 2019.
5. O Gini subiu em 2025, de 0,504 para 0,511 (`medido_vs_vivido.md:187`). A confiança do consumidor (FGV ICC) ficou em 84,2, a menor desde nov/2022 (`:198`).
6. Troca de Jean Paul Prates na Petrobras (mai/2024): verificada em `meta.verificacao`, mas não usada em E1.
7. L12: a IFI vê contingenciamento necessário de R$ 35,7 bi. Pestana: "não adianta… bypassar o arcabouço" (`checagem…md:153`).
8. L11: letalidade policial em alta (6.602 mortes) e 7 estados com alta de MVI (`checagem…md:149`).
9. L2: 6,03 mi dos "10,1 mi de empregos" estão em administração pública, educação e saúde (`checagem…md:24`).
10. Frases de Lula checadas em `medido_vs_vivido.md:235–237` que ficaram fora da checagem: "criamos 20 milhões de empregos" (exagerado) e "inflação de Bolsonaro 6,2%, a nossa 4,5%" (falta contexto).
11. Custo de R$ 22 bi do reajuste do Bolsa Família em 2027, ausente de L10 (está nas Propostas).

**Contra Flávio/Bolsonaro (faltam no painel):**

1. PEC Kamikaze (R$ 41,2 bi) e EC 113 e 114 de precatórios em F12. O painel só diz "precatórios adiados e receitas extraordinárias".
2. Governo Bolsonaro trocou 4 presidentes da Petrobras e impôs teto de ICMS (LC 194/2022). A fala de Flávio de que Eduardo "nunca pediu tarifas" foi classificada pelo Aos Fatos como parcialmente enganosa. Os três itens estão em `checagem…md:334` e faltam em E5.
3. Vídeo de supermercado de Flávio com imagens de out/2021, do governo Bolsonaro (Lupa; `medido_vs_vivido.md:226`).
4. Emenda de Flávio que isentaria dividendos do próprio escritório (`checagem…md:336`). Falta no painel e nas Propostas.
5. Bets sem regulamentação entre 2019 e 2022 (`checagem…md:233`). Ausente de F14.
6. "Lula defende traficantes": a frase existiu, mas citá-la sem a retratação é correto mas enganoso (`checagem…md:229`).

**A favor de cada lado e também omitidos (para equilíbrio):**

- A dívida bruta caiu de 86,9% para 71,7% do PIB entre 2020 e 2022, "com ajuda da inflação" (a favor de Bolsonaro).
- Lei de Liberdade Econômica (2019) e autonomia do BC (2021) (a favor de Bolsonaro, E5).
- Lula proibiu os sites de apostas em set/2026 (a favor de Lula, F14).
- O Focus errou o IPCA de 2025 por ~1,4 p.p. para cima (a favor do governo, erros do mercado).

## 7. As 10 correções prioritárias

1. **Checar promessas de Lula** com a mesma escala usada para Flávio (S1): tarifa zero e "crescimento como âncora" sem meta de dívida. Mover M6 para Lula/PT (S2).
2. **Cartão de percepção (H1):** acrescentar feijão +44% e café +46% e tratar o "ancora em 2019" como uma de duas explicações, não como causa.
3. **F7 (H2):** acrescentar "hoje presidido por Galípolo, indicado de Lula" e não usar a Selic nominal para responder a uma frase sobre juro real.
4. **F5 (H3):** trocar "parte vem da base" pela lista de aumentos de tributos e dizer que a divisão entre alíquota e base não foi medida.
5. **NE "custo de vida" (H4):** tirar o "atenuam" e pôr o dado BTG/Nexus (efeito nulo) e a alta da desaprovação.
6. **Comparação 2019–22 x 2023–26 (H8):** aplicar ao próprio painel a ressalva da pandemia usada contra Lula em L5.
7. **E7 (H9):** não defender Flávio com uma promessa classificada como "sem base". Incluir a desvinculação dos pisos e a emenda do escritório.
8. **F12 e E5 (H10 e omissões):** incluir PEC Kamikaze, EC 113 e 114, trocas na Petrobras e LC 194 do lado Bolsonaro, e o déficit primário em números do lado Lula. Em E1, incluir Prates.
9. **F13 e F14 (S3, S4):** reclassificar F13 como "exagerado", atualizar o resumo executivo (linha 85: Flávio passa a ter 4 "sem base") e trocar "coincidiu" por "abriu o mercado formal".
10. **Emprego, IBGE e escândalos (H5, H6, H7, H12):**
    - emprego: acrescentar à base de 2019 o dado mais recente (528 de 774 mil novos ocupados informais, base a confirmar);
    - IBGE: tirar o "governo anterior" do card;
    - escândalos: pôr os números do INSS no painel e no Briefing presidencial:30.

## 8. Como repetir a auditoria na versão final

Salve os dois blocos abaixo como `audit.py` e `checks.py` em qualquer pasta e rode a partir da raiz do repositório:

```
python3 audit.py . > candidatas.tsv   # triagem: sentenças com ressalva, lado e se há número
python3 checks.py .                   # 20 verificações das correções acima (PENDENTE / ok)
```

Na foto de 05/10/2026 04:00 UTC, o `audit.py` deu 187 candidatas e o `checks.py` deu **20 de 20 pendentes**. Depois que o outro agente terminar a aba, rode os dois de novo:

- os itens "ok" indicam correções aplicadas;
- "n/d" indica que o JSON mudou de estrutura e o item precisa de conferência manual;
- a contagem da seção 3.1 deve ser refeita com a matriz do apêndice, porque a classificação de polaridade é manual.

```python
#!/usr/bin/env python3
"""audit.py: triagem reprodutível de ressalvas (candidatas para revisão manual).
Saída TSV: arquivo, linha ou caminho JSON, lado, marcadores, número depois do marcador (s/n), trecho."""
import json, re, sys, html, glob, os
R = sys.argv[1] if len(sys.argv) > 1 else "."
LULA = re.compile(r"\bLula\b|\bPT\b|petista|Haddad|Durigan|governo atual|gest[aã]o atual|Lula 3|2023[–-]2?6|2023[–-]25|desde 2023|desde jan/2023|sob Lula|com Lula", re.I)
FLAV = re.compile(r"Fl[aá]vio|\bPL\b|Bolsonaro|bolsonaris|Guedes|Daniella|Sachsida|Marinho|2019[–-]2?2|governo anterior|gest[aã]o anterior|oposi[cç][aã]o", re.I)
HEDGE = re.compile(r"por outro lado|em sentido contr[aá]rio|\bmas\b|\bembora\b|ainda assim|mesmo assim|em parte|\bparte\b|contexto|\bporém\b|no entanto|atenua|ressalva|apesar|tamb[eé]m|legítim", re.I)
NUM = re.compile(r"\d")
def sentences(text):
    return [s for s in re.split(r"(?<=[.!?;])\s+(?=[A-ZÁÉÍÓÚ“\"(])", text) if s.strip()]
def emit(src, loc, text):
    l, f = bool(LULA.search(text)), bool(FLAV.search(text))
    if not (l or f): return
    lado = "ambos" if l and f else ("lula" if l else "flavio")
    for s in sentences(text):
        hs = [m.group(0).lower() for m in HEDGE.finditer(s)]
        if not hs: continue
        m = HEDGE.search(s); num_after = bool(NUM.search(s[m.start():]))
        print("\t".join([src, str(loc), lado, ",".join(sorted(set(hs))), "s" if num_after else "n", s.strip().replace("\t", " ")[:600]]))
def walk(x, p, src):
    if isinstance(x, dict):
        if all(isinstance(v, (str, list)) and not (isinstance(v, list) and v and isinstance(v[0], dict)) for v in x.values()):
            emit(src, p, " ".join(v if isinstance(v, str) else " ".join(map(str, v)) for k, v in x.items() if "fonte" not in k and k != "url")); return
        for k, v in x.items():
            if "fonte" in k or k == "url": continue
            walk(v, p + "." + k, src)
    elif isinstance(x, list):
        if all(isinstance(i, str) for i in x): emit(src, p, " | ".join(i for i in x if not i.startswith("http"))); return
        for i, v in enumerate(x): walk(v, "%s[%d]" % (p, i), src)
    elif isinstance(x, str) and not x.startswith("http"):
        emit(src, p, x)
print("arquivo\tlocal\tlado\tressalvas\tnum_na_ressalva\ttrecho")
h = open(os.path.join(R, "simulador/web/index.html"), encoding="utf-8").read()
h = re.sub(r"<style>.*?</style>", lambda m: "\n" * m.group(0).count("\n"), h, flags=re.S)
for i, line in enumerate(h.split("\n"), 1):
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", line))).strip()
    if len(t) > 30: emit("simulador/web/index.html", i, t)
for j in ["realidade.json", "nordeste.json", "curiosidades.json"]:
    pth = os.path.join(R, "simulador/web", j)
    if os.path.exists(pth): walk(json.load(open(pth, encoding="utf-8")), "$", "simulador/web/" + j)
for f in sorted(glob.glob(os.path.join(R, "reports/*.md"))) + [os.path.join(R, "research_notes/Nordeste e cenarios economicos 2026", n) for n in ("checagem_promessas_discursos.md", "medido_vs_vivido.md")]:
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        if line.strip(): emit(os.path.relpath(f, R), i, line.strip())
```

```python
#!/usr/bin/env python3
"""checks.py: verificações de regressão das correções propostas nesta auditoria."""
import json, re, sys, os
R = sys.argv[1] if len(sys.argv) > 1 else "."
rd = json.load(open(os.path.join(R, "simulador/web/realidade.json"), encoding="utf-8"))
ne = json.load(open(os.path.join(R, "simulador/web/nordeste.json"), encoding="utf-8"))
I = {i["id"]: i for i in rd["checagem"]["itens"]}
ind = {c["id"]: c for c in rd["indicadores"]}
V = {v[0]: v for v in rd["empresas"]["vereditos"]}
EX = {e["exp"]: e for e in ne["explicacoes"]}
txt = lambda d: " ".join(str(x) for x in (d.values() if isinstance(d, dict) else d))
def g(f):
    try: return f()
    except Exception: return None
C = [
 ("C01 F7 omite que o Copom é dirigido por indicados de Lula", lambda: not re.search(r"Gal[ií]polo|indicad", I["F7"]["fora"])),
 ("C02 F5: ressalva 'parte vem da base' sem número", lambda: "Parte" in I["F5"]["fora"] and not re.search(r"\d", I["F5"]["fora"])),
 ("C03 percepção: 'memória ancora em 2019' sem itens que subiram em 12m (feijão/café)", lambda: "ancora" in rd["meta"]["percepcao"] and not re.search(r"feij|caf[eé]", rd["meta"]["percepcao"])),
 ("C04 F13 classificado como 'sem base' (categoria de promessa)", lambda: I["F13"]["v"] == "sem_base"),
 ("C05 M1 (Revista Oeste) contado como 'mercado'", lambda: I["M1"]["lado"] == "mercado" and "Oeste" in I["M1"]["quem"]),
 ("C06 M6 (projeção do governo/MPO) contado como 'mercado'", lambda: I["M6"]["lado"] == "mercado" and "MPO" in I["M6"]["quem"]),
 ("C07 nenhuma promessa de Lula 2027–30 checada (tarifa zero, 6x1, mínimo)", lambda: not any(i["lado"] == "lula" and re.search(r"tarifa zero|6x1|promet|vamos|2027", i["afirmacao"], re.I) for i in rd["checagem"]["itens"])),
 ("C08 NE custo de vida: 'atenuam' sem dado (BTG/Nexus mostra efeito nulo)", lambda: "atenua" in EX["Custo de vida e alimentos"]["contra"]),
 ("C09 NE escândalos: 'mais bem avaliado' sem número", lambda: "avaliado" in txt(EX[[k for k in EX if "INSS" in k][0]]) and not re.search(r"\d", EX[[k for k in EX if "INSS" in k][0]]["contra"])),
 ("C10 'pandemia pesa nos dois períodos' na leitura 2019–22 x 2023–26", lambda: re.search(r"[Pp]andemia.*dois per[ií]odos", rd["empresas"]["resultados_leitura"]) is not None),
 ("C11 card IBGE contrapõe crise atual com 'governo anterior'", lambda: "governo anterior" in ind["ibge"]["gap_det"]),
 ("C12 emprego: contraponto 'desde 2019 tem carteira' sem o dado de 12 meses", lambda: "desde 2019" in ind["emprego"]["gap_det"] and not re.search(r"12 meses|528", ind["emprego"]["gap_det"])),
 ("C13 F14: 'coincidiu' (nota diz 'de fato abriu o mercado formal')", lambda: "coincidiu" in I["F14"]["fora"]),
 ("C14 E7 defende Flávio com IVA menor (promessa F10 'sem base')", lambda: "IVA menor" in V["E7"][4]),
 ("C15 E1 omite a troca na Petrobras (Prates), já verificada", lambda: "Prates" not in V["E1"][4]),
 ("C16 E5 omite trocas na Petrobras e LC 194/2022 do governo Bolsonaro", lambda: not re.search(r"Petrobras|194", V["E5"][4])),
 ("C17 F3 omite negativados 69,4→83,9 mi (dez/22→ago/26)", lambda: not re.search(r"83,9|negativad", txt(I["F3"]))),
 ("C18 F12 omite PEC Kamikaze/precatórios com valores", lambda: not re.search(r"Kamikaze|113", txt(I["F12"]))),
 ("C19 bandeira verde: 'regra paramétrica' sem o número do CMO", lambda: "paramétrica" in ind["itaipu"]["gap_det"] and not re.search(r"MWh", ind["itaipu"]["gap_det"])),
 ("C20 L5 omite feijão +44% e café +46% em 12m/desde 2023", lambda: not re.search(r"feij|caf[eé]", txt(I["L5"]))),
]
pend = 0
for nome, f in C:
    r = g(f)
    estado = "PENDENTE" if r else ("ok" if r is False else "n/d (estrutura mudou)")
    pend += bool(r); print(f"{estado:10s} {nome}")
print(f"\n{pend} de {len(C)} pendentes")
```

**Checklist manual (o que o script não pega):**

- [ ] Toda ressalva depois de uma crítica a um dos lados traz número da fonte?
- [ ] O mesmo tipo de comparação (períodos desiguais, base escolhida) recebe o mesmo veredito quando é feita pelo governo, pela oposição e pelo próprio painel?
- [ ] As promessas dos dois candidatos são testadas por custo e fonte?
- [ ] Cada fonte fica no mesmo "lado" em todos os itens?
- [ ] As categorias da escala são usadas só para o que definem ("sem base" = promessa sem conta)?
- [ ] Os fatos críticos de `checagem_promessas_discursos.md` e `medido_vs_vivido.md` cortados na passagem para o painel foram cortados nos dois lados?

## Apêndice: matriz de classificação do painel (foto de 05/10/2026)

**Legenda:**

- Alvo: L = Lula/PT/governo 2023–26; F = Flávio/PL/Bolsonaro 2019–22.
- Polaridade: − = crítica; + = elogio ou defesa.
- Ressalva: 0 = sem ressalva; N = com ressalva apoiada em número; S = com ressalva sem número.

| Unidade (`realidade.json` salvo indicação) | Alvo | Polaridade | Ressalva |
|---|---|---|---|
| L2, L5, L8, L10, L11, L13, L14 | L | − | 0 |
| L4 (correto quando dito), L6 (crescimento 2023–24 real) | L | − | N |
| L7 (qualidade do superávit 2022), L12 (meta cumprida com deduções) | L | − | S |
| F5 (carga recorde, confirmada) | L | − | S |
| F7 (juro real, confirmado) | L | − | N (número inadequado) |
| M5, M6, E2 | L | − | 0 |
| E4 (concessões recordes, sem número) | L | − | S |
| indicadores alimentos:45, emprego:137, meta.percepcao:6 | L | − | N |
| indicadores combustível:86; leitura (confiança):265; como_ler governo a, b, c | L | − | 0 |
| indicadores itaipu:96, ibge:178; padrao[0] | L | − | S |
| `nordeste.json` explicações: custo de vida, evangélicos, ascensão, fragmentação, política local | L | − | N |
| `nordeste.json` explicações: segurança, escândalos, desgaste | L | − | S |
| L1, L3 | L | + | N |
| L9; M4; E1; E3; como_ler governo d (:343) | L | + | S |
| M1 ("quebrou" exagerado); erros 2003 (:288) | L | + | N |
| leitura IDP e PIB (:265); erros 2023 | L | + | 0 |
| F9, F10, F11; erros 2019; ibge (Censo 2021); como_ler oposição a–d | F | − | 0 |
| F1, F2, F3, F4, F6, F13; L5 contexto (2019–22: pandemia, câmbio > R$ 5) | F | − | N |
| F8, F12, F14; E5, E6; padrao[1] | F | − | S |
| E7 (defesa com IVA menor) | F | + | S |
| E8 | F | + | 0 |
