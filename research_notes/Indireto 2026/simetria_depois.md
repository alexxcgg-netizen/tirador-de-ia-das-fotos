# Simetria depois das revisões

Resultado de `auditoria_simetria.py` (reutilizável: lê `indireto_lula.csv` e `indireto_flavio.csv`) e interpretação. As classes de veículo (esquerda/centro/direita/oficial/checador) estão na tabela `SOURCE_CLASS` do script; são aproximações das revisões e podem ser contestadas editando a tabela.

## Antes e depois (o que as revisões mediram x o que o script mede agora)

| medida | antes (revisões, calculado por elas) | depois (script) |
|---|---|---|
| Tags com rótulo de conclusão | Lula 30 de 48; Flávio 0 de 56 | Lula 0; Flávio 0 (vocabulário `[fato]`/`[leitura]`/`[narrativa de X]`) |
| Casos com 2+ fontes | Lula 0 de 48; Flávio 12 de 56 | Lula 28 de 52 ativos; Flávio 27 de 54 |
| Casos com checador | Lula 0; Flávio 7 URLs | Lula 3 casos; Flávio 9 casos |
| Confiança 'alta' (uma coluna só) | Lula 8 de 48 (17%); Flávio 27 de 56 (48%) | `confianca_fato` alta: Lula 56%, Flávio 72% |
| Casos 'alta + indireto: sim' | Lula 6; Flávio 19 | `confianca_fato` alta + `forca_leitura_indireta` forte ou média: Lula 8; Flávio 16 (ver seção 4) |
| Casos ativos | Lula 48; Flávio 56 | Lula 52; Flávio 54 |
| Casos em escopo histórico | Lula 2 (L25, L33); Flávio 21 (2005 a 2022) | Lula 12 (PT 2003-22); Flávio 22 (4 pré-2019 + 18 de 2019-22) |

## Interpretação (curta, com as assimetrias que restam)

1. **O que ficou simétrico.** Mesmo vocabulário de tags (0 violações nos dois), mesmas colunas, mesma barra de evidência, mesma regra para os 10 mais fortes e os 5 mais fracos, mesmo número de linhas retiradas (12 e 12), períodos marcados nos dois lados, mesmo tratamento de fatos espelhados (Gonet x Aras, Prates x Castello Branco, mensagens de Vorcaro, anulação de Lula x rachadinha, perseguição, checagens de entrevistas). A fração de casos favoráveis ao ator ficou parecida (11 de 52, 21%; 8 de 54, 15%).
2. **Assimetria que resta: a força da leitura.** No mapa de Flávio há 5 casos `forte` e 17 elegíveis para o top 10; no de Lula, 1 `forte` e 9 elegíveis (por isso o top 10 de Lula tem 9 casos). Em `confianca_fato` não há caso 'baixa' ativo em nenhum dos dois: os de baixa foram retirados. Parte vem de fatos: os casos fortes de Flávio têm contradição literal documentada (FB33, FB34, FB44), atos oficiais de 2022 (FB12, FB13) e fonte primária; os casos de timing de Lula em 2026 perderam força quando a contra-evidência completa entrou (L09, L10, L07). Mas há duas fontes de incerteza que o script não elimina: (a) a rubrica de força é um juízo de quem revisou (a rubrica está nos mapas, mas a aplicação não foi auditada por terceiros) e (b) o histórico de Jair 2019-22 é maior e mais julgado que o do PT 2003-22 coberto aqui. Um apoiador de qualquer lado pode contestar casos concretos; as colunas permitem isso.
3. **Assimetria que resta: escopo histórico.** Flávio/Bolsonaro tem 22 casos históricos (4 pré-2019 + 18 de 2019-22); Lula/PT tem 12 (PT 2003-22), e o bloco do PT não é exaustivo (não há petrolão além do caso de Lula, nem Mariel/Cuba, nem política econômica de Lula 1 e 2). No recorte comparável de 2023-26, são 40 casos de Lula e 32 de Flávio/Jair/aliados, e a quantidade de 'média' é parecida (6 contra 5), mas Flávio tem 3 `forte` contra 0 de Lula em 2023-26.
4. **Assimetria que resta: fontes.** Os dois mapas ainda têm muitos casos de fonte única (Lula 24 com 1 veículo; Flávio 27); quem não passa na barra tem a força limitada a `fraca`. Mistura de classes: centro 60% (Lula) e 64% (Flávio); direita 11% e 5%; esquerda 5% e 6%; oficial 20% e 14%; checador 4% e 11%. O mapa de Flávio tem mais checadores (Aos Fatos e Lupa checaram mais as falas dele no JN do que as de Lula, que tem uma checagem da Record); o de Lula tem mais fonte oficial porque os casos de 2026 passaram por decretos e MPs. As páginas mais críticas ao governo (Poder360, Gazeta, Oeste) deram 403 em vários casos e a dureza dessa cobertura pode estar subrepresentada.
5. **Assimetria que resta: redação.** Hedges por 1000 palavras: Lula 7,3 contra 6,1 de Flávio; adjetivos: 1,5 contra 3,6. A contra-evidência do mapa de Lula é mais longa (392 contra 276 caracteres) porque as quatro maiores reescritas (L09, L10, L29, L47) trazem contexto completo. Isso pode refletir tanto cuidado maior com o lado que estava mais exposto na revisão anterior quanto uma tendência a amaciar com ressalvas (viés pró-governo da Regra 5); não é possível distinguir pelos números.
6. **Viés da própria revisão.** Este trabalho foi feito por um modelo de IA que não consegue auditar o próprio treinamento (Regra 5). O controle usado foi a mesma regra e o mesmo script para os dois lados, mais a verificação de fatos nas fontes; ele não substitui uma revisão independente das classificações, em especial de `forca_leitura_indireta` e das classes de veículo.

## Saída do script (gerada por `python auditoria_simetria.py`, em 2026-10-05, depois das revisões)

Lados: Lula/PT, Flávio/Bolsonaro. Contagens sobre TODAS as linhas do CSV (inclui status retirado) onde indicado; a maioria das tabelas usa so os casos ativos (status 'indireto' ou 'não indireto').

## 0. Linhas por status

| status | Lula/PT | Flávio/Bolsonaro | total |
|---|---|---|---|
| indireto | 34 | 40 | 74 |
| não indireto | 18 | 14 | 32 |
| retirado | 12 | 12 | 24 |
| TOTAL de linhas | 64 | 66 | 130 |

Casos favoraveis ao ator (a_favor_do_ator sim/misto), entre os ativos: Lula/PT: 10 sim + 1 misto; Flávio/Bolsonaro: 6 sim + 2 misto
Casos marcados 'disputado': Lula/PT: 2; Flávio/Bolsonaro: 1

## 1. Casos ativos por categoria

| categoria | Lula/PT | Flávio/Bolsonaro |
|---|---|---|
| 1 porta-vozes | 2 | 2 |
| 2 atos sem palavras | 9 | 9 |
| 3 timing | 7 | 6 |
| 4 escolha do número | 5 | 4 |
| 5 palavras com dono | 2 | 1 |
| 6 mensagens diferentes por público | 1 | 4 |
| 7 imagens/símbolos/memes | 2 | 0 |
| 8 reescrita posterior | 5 | 6 |
| 9 silêncios | 4 | 4 |
| 10 aliados e proteção | 8 | 10 |
| 11 linguagem de ameaça/combate | 3 | 4 |
| 12 narrativa de vítima/inimigo | 4 | 4 |
| TOTAL | 52 | 54 |

## 2. Casos ativos por periodo

| periodo | Lula/PT | Flávio/Bolsonaro |
|---|---|---|
| PT 2003-22 (histórico) | 12 | 0 |
| governo Bolsonaro 2019-22 | 0 | 18 |
| governo Lula 2023-26 | 40 | 0 |
| oposição 2023-26 (Jair, Flávio e aliados) | 0 | 32 |
| pré-2019 (histórico) | 0 | 4 |

## 3. Vocabulario de tags (casos ativos)

- Lula/PT: {'[fato]': 50, '[leitura]': 28, '[narrativa de X]': 5}; violacoes do vocabulario: nenhuma
- Flávio/Bolsonaro: {'[fato]': 47, '[leitura]': 7, '[narrativa de X]': 5}; violacoes do vocabulario: nenhuma

## 4. confianca_fato e forca_leitura_indireta (casos ativos)

**confianca_fato**

| confianca_fato | Lula/PT (n) | Flávio/Bolsonaro (n) | Lula/PT (%) | Flávio/Bolsonaro (%) |
|---|---|---|---|---|
| alta | 29 | 39 | 56% | 72% |
| média | 23 | 15 | 44% | 28% |
| baixa | 0 | 0 | 0% | 0% |

**forca_leitura_indireta**

| forca_leitura_indireta | Lula/PT (n) | Flávio/Bolsonaro (n) | Lula/PT (%) | Flávio/Bolsonaro (%) |
|---|---|---|---|---|
| forte | 1 | 5 | 2% | 9% |
| média | 8 | 12 | 15% | 22% |
| fraca | 34 | 29 | 65% | 54% |
| não conclusivo | 9 | 8 | 17% | 15% |

Cruzamento (alta confianca no fato x forca da leitura), so 'indireto':

| lado | alta+forte | alta+média | alta+fraca | alta+nc |
|---|---|---|---|---|
| Lula/PT | 1 | 7 | 7 | 6 |
| Flávio/Bolsonaro | 5 | 11 | 10 | 3 |

## 5. Numero de fontes (veiculos distintos) por caso ativo

| lado | 1 fonte | 2+ fontes | com fonte oficial | com checador | passa a barra | nao passa |
|---|---|---|---|---|---|---|
| Lula/PT | 24 | 28 | 15 | 3 | 33 | 19 |
| Flávio/Bolsonaro | 27 | 27 | 11 | 9 | 37 | 17 |

Barra de evidencia: fonte oficial/primaria, OU checador, OU 2+ veiculos distintos. Casos que nao passam tem forca limitada a 'fraca' e nao entram nos 10 mais fortes.

## 6. Mistura de veiculos (URLs distintas por dominio, casos ativos)

| classe | Lula/PT (n) | Flávio/Bolsonaro (n) | Lula/PT (%) | Flávio/Bolsonaro (%) |
|---|---|---|---|---|
| esquerda | 6 | 6 | 5% | 6% |
| centro | 66 | 61 | 60% | 64% |
| direita | 12 | 5 | 11% | 5% |
| oficial | 22 | 13 | 20% | 14% |
| checador | 4 | 10 | 4% | 11% |
| (sem classe) | 0 | 0 | 0% | 0% |
| TOTAL de citacoes | 110 | 95 |  |  |

Principais dominios por lado:

- Lula/PT: cnnbrasil.com.br (12), gazetadopovo.com.br (10), agenciabrasil.ebc.com.br (8), otempo.com.br (7), poder360.com.br (6), www12.senado.leg.br (5), gov.br (4), conjur.com.br (4)
- Flávio/Bolsonaro: cnnbrasil.com.br (12), poder360.com.br (7), jornaldebrasilia.com.br (5), aosfatos.org (5), agencialupa.org (5), infomoney.com.br (4), gazetadopovo.com.br (4), agenciabrasil.ebc.com.br (4)

## 7. Redacao (campos comportamento_revelado + contra_evidencia, casos ativos)

| lado | palavras | hedges | hedges/1000 | adjetivos | adjetivos/1000 | tam. medio contra-evid. (car.) | contra-evid. com numero |
|---|---|---|---|---|---|---|---|
| Lula/PT | 4663 | 34 | 7.3 | 7 | 1.5 | 392 | 83% |
| Flávio/Bolsonaro | 3595 | 22 | 6.1 | 13 | 3.6 | 276 | 85% |

Listas usadas: HEDGES e ADJETIVOS no topo do script (aproximacao por prefixo de palavra; serve para comparar os lados, nao para medir tom).

## 8. Rankings pela mesma regra

**Regra dos 10 mais fortes.** 10 mais fortes = casos com status 'indireto' (a leitura indireta e o que esta em teste), que passam a barra de evidencia (fonte primaria/oficial, OU checador com metodo publicado, OU 2+ veiculos distintos), que NAO estao marcados 'disputado' e cuja forca_leitura_indireta e 'forte' ou 'media'. Ordem: forca_leitura_indireta, depois confianca_fato, depois numero de veiculos distintos, depois numero de classes de veiculo diferentes; empate final pelo SHA-1 do id (arbitrario, sem relacao com lado, data ou tema). Casos favoraveis ao ator, 'nao indireto' e retirados nao entram.

**Regra dos 5 mais fracos.** 5 mais fracos = casos com status 'indireto' (a acusacao de indireto que menos se sustenta). Ordem crescente: forca_leitura_indireta (nao conclusivo < fraca), depois confianca_fato (baixa < media < alta), depois numero de veiculos distintos (menos primeiro), depois SHA-1 do id. Casos 'nao indireto' (controles explicitos) e retirados ficam em listas proprias.

### Lula/PT

Mais fortes: LP06 (forte/alta), L37 (média/alta), L51 (média/alta), L18 (média/alta), LP05 (média/alta), LP01 (média/alta), L03 (média/alta), L28 (média/alta), L49 (média/média)
(elegiveis: 9)
Mais fracos: L11 (não conclusivo/média), L48 (não conclusivo/média), L38 (não conclusivo/média), LP04 (não conclusivo/alta), L39 (não conclusivo/alta)

### Flávio/Bolsonaro

Mais fortes: FB44 (forte/alta), FB12 (forte/alta), FB33 (forte/alta), FB34 (forte/alta), FB13 (forte/alta), FB35 (média/alta), FB08 (média/alta), FB62 (média/alta), FB58 (média/alta), FB60 (média/alta)
(elegiveis: 17)
Mais fracos: FB15 (não conclusivo/média), FB07 (não conclusivo/média), FB43 (não conclusivo/média), FB40 (não conclusivo/média), FB66 (não conclusivo/alta)

