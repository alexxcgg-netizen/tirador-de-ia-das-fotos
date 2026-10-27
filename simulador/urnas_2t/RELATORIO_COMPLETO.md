# Todas as urnas do 2º turno 2026 (leitura direta do boletim de urna)

Fonte: arquivos de urna públicos do TSE (pleito 3221, 2º turno; pleito 3220 para o 1º turno). Lidos o BU de cada seção, sem passar pelo totalizador. Leitura concluída em 27/10/2026, ~07h UTC.

## 1. Cobertura e soma
- 499.178 BUs lidos de 499.248 seções oficiais. As 70 restantes: 41 "não instaladas" e 29 do exterior marcadas "Totalizada" cujo BU não aparece na listagem pública (não consegui lê-las).
- Soma dos BUs: Lula 64.255.787, Flávio 59.825.688. Oficial agora: Lula 64.256.232, Flávio 59.826.041. Diferença: 445 e 353 votos (≈800 votos, 0,0006%), compatível com as 29 seções do exterior sem BU. Comparecimento: 128.235.243 contra 128.236.074.
- Em todas as 5.571 cidades brasileiras lidas por inteiro, votos, comparecimento, brancos e nulos dos BUs batem com o total municipal oficial (0 diferenças; 11 cidades pareciam diferir só porque o arquivo oficial que eu tinha era antigo, e bateram depois de baixar de novo). 187 cidades diferem apenas em "aptos" (soma −26.744: o oficial tem mais eleitores aptos que a soma das seções), concentradas em capitais (DF −14.819, Manaus −2.436, Natal −2.328, Palmas −1.204, Vitória −1.185).
- Em nenhuma seção a soma dos votos de presidente difere do comparecimento.

## 2. O que apareceu de estranho (e o que se sabe)
- 148 seções com comparecimento maior que aptos (DF, ES, RN, AM). 157 seções nas amostras com comparecimento ≥ aptos tinham mediana de 107,5% de comparecimento já no 1º turno → o padrão não nasceu no 2º turno. Coincide com as capitais em que o oficial tem mais aptos que a soma das seções. Hipótese: eleitores em trânsito votando em seções de capital [não verificado na fonte primária].
- Seções quase unânimes (≥99% dos votos válidos, ≥100 votos): Lula 151 (AM 67, MA 26, PA 17, MT 12, RR 8…), Flávio 4 (RS 2, PA 1, PR 1). Entre as 1.482 seções com Lula ≥95% no 2T, a mediana de Lula já era 96,1% no 1T; entre as 30 com Flávio ≥95%, 3% no 1T para Lula. Ou seja, já eram assim no 1º turno. Muitas ficam em áreas indígenas e ribeirinhas [localização das seções: amostra, não verificada seção a seção].
- Último dígito dos votos: aptos e comparecimento são uniformes (≈10% cada dígito); os votos de Lula e de Flávio têm a mesma leve queda (10,5% no 0 para 9,6% no 9). Os dois candidatos do mesmo jeito indica efeito de contagens com densidade decrescente, não marca de um candidato; o desvio máximo é 0,24 ponto.
- Comparecimento × voto: correlação entre comparecimento e % de Lula nas cidades ≈ −0,04; entre "compareceram sem biometria" e % de Lula ≈ −0,01. Nenhuma relação relevante.

## 3. 1º turno × 2º turno, urna por urna (15.632 seções pareadas)
- Amostra aleatória de 13.963 seções + 1.669 sinalizadas (extremas ou com comparecimento ≥ aptos).
- Amostra: parcela de Lula entre Lula+Flávio mediana de 46,7% no 1T para 50,2% no 2T (média +2,95 pontos). O número nacional pelo município dá +2,8: bate.
- O deslocamento é suave e previsível: +3,8 pontos onde Lula tinha 20–40% no 1T, +0,6 onde tinha >80% (voto dos outros candidatos do 1T e teto). Nenhuma seção da amostra se desvia do padrão por mais de ~3,6 desvios (0 acima de 5). Comparecimento mediano subiu de 79,7% para 81,5%.

## 4. O que estes testes NÃO pegam
- Se os BUs e a soma oficial fossem alterados juntos e de forma coerente, estes testes não veriam. Eles pegam divergência entre urna e totalização, seção que foge do padrão do 1T, impressão digital de números inventados. Não pegam fraude que preserve esses padrões.
- Amostra de 1T cobre 14 mil seções (2,8%), não todas.
- 29 seções do exterior (~800 votos) sem BU lido.
- Anomalia estatística ≠ fraude; ausência de anomalia ≠ prova de integridade.
