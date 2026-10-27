# Arquivos de urna do 2º turno de 2026: Brusque e uma amostra nacional

Data da análise: 26/10/2026. Fonte: arquivos publicados pelo TSE em `resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/` (pleito 3221, eleição 6258).

## 1. Método

- **Seções**: a lista vem do `config/{uf}/{uf}-p003221-cs.json`. Ficaram de fora as seções agregadas (as que têm o campo `nsp`), porque não têm urna própria e o `aux.json` delas dá 404. Exemplo: Brusque 0086/0196 foi agregada à 0073. O universo das 27 UFs, sem o exterior, tem **497.897 urnas**.
- **BU** (`-bu.dat`): decodificado como `EntidadeEnvelopeGenerico`, e o `conteudo` como `EntidadeBoletimUrna`. Usei a especificação ASN.1 pública do TSE (`bu.asn1`, versão com `envelopeZeresimaImpressa` e `urnaEncerradaComEleitoresNaFila`, tirada de um espelho no GitHub). Ela decodificou 100% dos BUs sem erro. Só conto os votos do cargo `presidente`. Nos estados com 2º turno para governador o BU traz os dois cargos, e o governador também pode ter número 13 ou 22. Esse erro apareceu numa primeira passada e foi corrigido.
- **Log** (`-log.jez`): o arquivo é **ZIP**, não 7z, e contém `logd.dat` (texto em latin-1, separado por tabulação). Quando a urna foi substituída, o ZIP traz também o log da urna anterior, como `.jez` aninhado (também ZIP). Esse log aninhado foi lido e as linhas repetidas foram descartadas. Só uso as linhas de 25/10/2026. O voto conta na linha `O voto do eleitor foi computado`, a abertura em `Urna pronta para receber votos` e o encerramento em `Procedimento de encerramento confirmado`. Esse último horário bate com o `dataHoraEncerramento` do BU.
- **Fuso**: o relógio da urna marca a hora local. Comprovei isso na abertura do BU: AC abre às 06h, AM, MT, MS e RO abrem às 07h. Converti tudo para o horário de Brasília (AC −2 h; AM, RO, RR, MT e MS −1 h). Os cortes de "17h00" e "17h30" estão sempre no **horário de Brasília**.
- **Amostra** (semente 20261025): 150 urnas sorteadas com probabilidade igual entre as 497.897; 80 da BA (50 de Salvador, 15 de Feira de Santana e 15 de Lauro de Freitas); 80 da capital de SP. O plano está em `amostra_plano.json`.
- **Download**: um pedido por vez, com intervalo de pelo menos 0,3 s e espera crescente no 429 (houve alguns 429, todos resolvidos na nova tentativa). Python rodado com `-I`, fora da pasta dos dados. Depois do ajuste pedido, cada seção foi processada em fluxo e os arquivos brutos foram apagados. Não sobrou nenhum `.dat` nem `.jez`. Para a ampliação (biometria e eventos), os mesmos arquivos de Brusque e da amostra foram baixados **de novo**, porque os brutos já tinham sido apagados. Não entrou nenhuma seção nova. Volume total transferido: cerca de 0,3 GB.

## 2. Brusque (SC, código 80551, zonas 0005 e 0086)

São 283 urnas (284 seções, uma delas agregada). Todas com status `Totalizada`.

| Item | Soma dos BUs | Total oficial | Confere? |
|---|---|---|---|
| Flávio (22) | 65.171 | 65.171 | sim |
| Lula (13) | 19.202 | 19.202 | sim |
| Brancos | 857 | 857 | sim |
| Nulos | 1.345 | 1.345 | sim |
| Comparecimento | 86.575 | 86.575 | sim |
| Aptos | 101.579 | – | – |

- **A soma das seções bateu exatamente com o total oficial nos cinco itens.**
- Votos contados no log: **86.575**, igual ao comparecimento do BU. A conta só fecha incluindo o log aninhado da urna substituída na seção 0005/0220 (22 votos).
- Horários: 280 urnas abriram às 08:00:01 e 3 entre 08:01 e 08:03. O primeiro voto saiu às 08:01 (mediana) e no máximo às 08:07. Todas as urnas encerraram entre 17:00 e 17:06.
- **Votos depois das 17h00: 5 (0,006%)**, um em cada uma de 5 urnas, todos até 17:00:35. Depois das 17h30: **0**.
- Habilitação (BU): 80.043 por biometria (92,5%), 5.162 por dados biográficos depois de falha da digital e 1.370 de eleitores sem biometria cadastrada. O log não traz nenhum tipo de habilitação além de `[biométrica]`.
- Eventos:
  - **0005/0220**: urna de contingência. A urna original (02002003) recebeu 22 votos até 08:24. A urna 02022292 foi ligada às 08:28, a contingência foi cancelada uma vez pelo operador e refeita às 08:33. O log da memória externa da urna original foi marcado como "corrompido", mas foi lido e tem os 22 votos. O total, 306 + 22 = 328, bate com o BU. O BU diz `contingenciaSecao`.
  - 0086/0069: o BU diz `contingenciaSecao`, mas a substituição foi no 1º turno (o log aninhado é de 04/10). No dia 25/10 a urna funcionou normalmente.
  - 6 urnas foram religadas durante a votação. Em 4 delas o log registra o erro "Falha na captura da digital. Desligue e ligue a urna". A 0005/0135 foi desligada pela chave às 11:57 e voltou às 12:02.
  - `ERRO: Problema ao desmontar a MR` aparece em 282 das 283 urnas, na inicialização. É sistemático e não tem relação com votos.

## 3. Efeito da prorrogação (amostra)

| Grupo | Urnas | Votos no log | Votos ≥ 17h00 | % | Votos ≥ 17h30 | Urnas com voto ≥ 17h00 | Urnas encerradas ≥ 18h |
|---|---|---|---|---|---|---|---|
| Nacional (aleatória) | 150 | 38.002 | 15 | 0,039% | 0 | 14 | 1 |
| Salvador, Feira e Lauro (BA) | 80 | 26.225 | 18 | 0,069% | 2 | 13 | 8 |
| Capital de SP | 80 | 21.983 | 21 | 0,096% | 4 | 13 | 5 |

- **Estimativa nacional de votos dados depois das 17h** (Brasília): **0,039%**, com IC 95% de **0,021% a 0,061%**. É uma estimativa de razão com bootstrap de 20.000 reamostragens das 150 urnas. Depois das 17h30, nenhum voto nas 150 urnas. Como limite superior aproximado (regra do 3), no máximo ~2% das urnas teriam algum voto depois das 17h30. Nas capitais da amostra, a fração depois das 17h30 foi de 0,008% (BA) e 0,018% (SP).
- Para dar escala, sem afirmar nenhuma relação causal: 0,04% do comparecimento equivale a algumas dezenas de milhares de votos no país. A diferença entre os candidatos foi de 3,54 pontos percentuais, ou seja, milhões de votos.
- Quase todo voto depois das 17h00 aconteceu nos primeiros minutos (fila). Os casos mais tardios estão em Salvador 0007/0177 (último voto às 18:33, 2 depois das 17h), SP 0381/0648 (6 votos depois das 17h, último às 18:12) e SP 0006/0310 (último às 18:10).
- **Urnas abertas até ~19h sem votar**: das 8 urnas da BA encerradas depois das 18h, **6 não tiveram nenhum voto depois das 17h**. O último voto foi entre 16:33 e 16:58, e elas encerraram entre 19:01 e 19:04. Em SP isso aconteceu em 2 de 5 (0350/0754, encerrada às 18:03, e 0002/0352, às 19:00). Pela regra descrita no pedido (prorrogação para as seções abertas às 17h), essas urnas não tinham sido encerradas às 17h. Ficaram abertas, mas não houve votos. É um fato do log. Não tenho o despacho para comparar a seção com a lista de seções abrangidas.
- Na amostra nacional, só 1 urna encerrou depois das 18h (Salvador 0003/0574, às 19:00, com 1 voto depois das 17h). Outra (Grajaú/MA 0015/0382) encerrou às 17:33, com o último voto às 16:42.

## 4. Anomalias objetivas na amostra (310 urnas)

- **BU contra o log**: em todas as 310 urnas, (a) os votos de presidente somados (13 + 22 + brancos + nulos) são iguais ao comparecimento do BU e (b) o número de "voto computado" no log é igual ao comparecimento. Não houve nenhum BU que não batesse.
- **Voto fora do horário**: nenhum voto antes das 08h nem depois das 19h30 (Brasília).
- **Substituição ou contingência**: 4 urnas com `contingenciaSecao` no BU. Em 1 delas (Ananindeua/PA 0107/0310) a troca foi no próprio dia 25/10, depois de 4 erros "ERROR opening the biometric reader": duas urnas aparecem no log e a abertura ficou para 08:15.
- **Religada durante a votação**: 13 urnas (10 uma vez, 2 duas vezes, 1 cinco vezes). Suspensão de votação: 9 urnas.
- **Itacarambi/MG 0148/0376**: 5 registros de `ERRO: Erro inesperado durante a votação | O voto do eleitor NÃO foi registrado`, junto com 5 reinícios e 1 suspensão. Mesmo assim, BU e log batem (111 votos computados = 111 comparecimentos). Pelo log, a interrupção aconteceu antes do registro. Não dá para dizer se esses eleitores voltaram a votar.
- Erros sistemáticos: `Problema ao desmontar a MR` aparece em 309 das 310 urnas. Erros pontuais de leitor biométrico, LED e LCD do terminal do mesário.
- **Status no `aux.json`**: 79 seções da amostra estavam como `Recebida` (47 delas na capital de SP), e não `Totalizada`, no momento do download. O BU dessas seções existe e decodifica normalmente.
- Nada disso, sozinho, indica fraude. São eventos operacionais registrados pela própria urna.

## 5. Limites

- A amostra nacional tem 150 urnas e o intervalo de confiança é largo em termos relativos. Depois das 17h30 só existe limite superior. As cidades foram escolhidas pelo pedido, não por sorteio, e não representam o país.
- "Voto depois das 17h" inclui o eleitor que já estava na fila às 17h, o que a lei permite com ou sem prorrogação. Com os logs não dá para separar o efeito da prorrogação do efeito da fila.
- O fuso foi aplicado por UF. Municípios com fuso diferente do resto da UF (por exemplo, Fernando de Noronha) não foram tratados, e nenhum caiu na amostra.
- O `bu.asn1` veio de um espelho público, não do site do TSE. A validação exata contra o total oficial de Brusque sustenta a decodificação.
- O processo não verifica assinaturas digitais nem a cadeia de hashes.

## Arquivos (todos neste diretório)

- `brusque_secoes.csv`: 1 linha por urna de Brusque, com votos, horários, flags e eventos (biometria, religamentos, contingência, erros).
- `amostra_secoes.csv`: 1 linha por urna da amostra.
- `eventos_urna.csv`: 593 linhas (Brusque e amostra). Abertura, primeiro e último voto, encerramento, habilitação (BU e log), reinícios, suspensões, contingência e erros. Os dígitos das mensagens foram mascarados e não há dado de eleitor.
- `votos_hora.csv`: votos computados por urna e por minuto (horário de Brasília).
- `eventos_log_agregados.json`: contagem de cada tipo de mensagem relevante (ALERTA, ERRO, contingência), com dígitos mascarados.
- `amostra_plano.json`: as seções sorteadas.

## Resumo

- A soma dos BUs de Brusque bate exatamente com o total oficial: Flávio 65.171, Lula 19.202, brancos 857, nulos 1.345, comparecimento 86.575. Os logs têm o mesmo número de votos.
- Em Brusque, 5 votos (0,006%) foram dados depois das 17h e nenhum depois das 17h30.
- No país, a estimativa é de 0,039% dos votos depois das 17h (IC 95% de 0,021% a 0,061%) e nenhum voto depois das 17h30 na amostra. Em Salvador, Feira e Lauro a fração foi de 0,069%, e na capital de SP de 0,096%.
- Várias urnas de Salvador e de SP ficaram abertas até ~19h sem nenhum voto depois das 17h.
- Não houve BU que não batesse com o log. As anomalias encontradas são operacionais: contingências, reinícios, erros de biometria e 5 erros "voto NÃO registrado" em uma urna de MG, onde mesmo assim BU e log fecham.
