# Pesquisas da véspera (3/10/2026): complemento

Levantamento feito na noite de 3/10/2026, por volta de 22h BRT. O arquivo `pesquisas_vespera_extra.csv` usa as mesmas colunas de `simulador/data/pesquisas_nacionais.csv`. As linhas estaduais trazem `instituto` com o sufixo `(UF=XX)` e começam o campo `obs` com "ESTADUAL". O `obs` de cada linha diz se os números estão em **votos totais** ou em **votos válidos**. Nas linhas em válidos, `bni=0` por construção.

## Nacionais divulgadas em 3/10 (números novos)

| Instituto | Campo | n | 1T totais (Lula / Flávio / outros) | 2T totais (Lula x Flávio) | Rejeição | Fonte primária |
|---|---|---|---|---|---|---|
| Quaest (BR-02197/2026) | 2–3/10 | 3.702 | 40 / 38; Caiado 3, Cury 3, Renan 3, Zema 0; BN 10, indecisos 3 (válidos 46/45) | 42 x **44** (BN 13, indecisos 1) | não publicada | G1 quaest-presidente-3-outubro; SBT News; Brasil 247 |
| Datafolha (BR-01708/2026) | 3/10 | 4.006 | 42 / 40; Caiado 4, Cury 3, Renan 3, Zema 0; BN 4, indecisos 3 (válidos 45/42) | 47 x 46 (BN 6, indecisos 2) | não publicada (1/10: 45 x 45) | G1 datafolha-presidente-3-outubro; O Tempo |
| Futura/100% Cidades (BR-02431/2026) | 2–3/10 (PDF) | 2.000 | 40,5 / 42,5; Cury 3,9, Caiado 3,7, Renan 2,6, Zema 0,8; BN 2,6, NS 2,4 (válidos 42,6/44,8) | 45,1 x 48,0 (BN 5,7, NS 1,2); Caiado 44,7 x Lula 44,0 | Lula 46,9; Flávio 43,1; Renan 15,7; Zema 13,7; Caiado 12,7; Cury 10,7 | PDF no admin.cnnbrasil.com.br; CNN; Money Times |

Também incluí a Veritá **nacional consolidada de 20–25/9** (n=40.500, divulgada em 1/10), que não estava no CSV principal. Em votos totais: Flávio 44,3 / Lula 43,8 / Cury 4,2 / Renan 2,3 / Caiado 2,1 / Zema 0,5; NS/NR mais branco/nulo somam 1,9. Em válidos: 45,14 x 44,65. O relatório não traz 2º turno.

## Estaduais (presidente) divulgadas em 3/10

- **Datafolha SP** (BR-05815, n=2.520): totais Flávio 42 x Lula 36; válidos 45 x 39.
- **Datafolha DF** (BR-09812, n=1.620): totais 47 x 35; 2º turno 55 x 38.
- **Datafolha MG** (BR-07919, n=2.003): o título do G1 dá 41 x 41 em válidos, mas o corpo da matéria repete os números de SP. Está marcado como não confiável.
- **AtlasIntel**, em votos válidos, campo 27/9–2/10:
  - PA: 51,4 x 41,3.
  - PI: 67,9 x 27,5; 2º turno 70,6 x 29,4.
  - BA: 60,5 x 29,8; 2º turno 64,6 x 35,4.
- **Veritá**, campo 26/9–1/10, com PDFs no site do instituto (Supabase público). Totais:
  - AC: Flávio 66,6 x Lula 25,9.
  - AL: Lula 51,2 x Flávio 39,8.
  - AP: Flávio 49,2 x Lula 40,3.
  - GO: Flávio 50,6 x Lula 32,8 (Caiado 10,1).
  - DF: Flávio 51,0 x Lula 39,6.
  - Os relatórios de MS, PA, MA, MT, TO, BA, CE, PE, SC, RN, RR, RO, RS e SP publicados em 3/10 não têm pergunta presidencial extraível em texto.
- Vi apenas como legenda de foto no G1, sem conferir (não estão no CSV): "Quaest no Pará: Lula 40, Flávio 35, Cury 7" e "Quaest em RO: Flávio 53, Lula 19".

## Conflitos encontrados

1. **Quaest, 2º turno:** a lista da Gazeta do Povo traz "Lula 44 / Flávio 42", mas o texto da própria matéria, o G1 e o Brasil 247 dão **Flávio 44 x Lula 42**. Fiquei com Flávio 44.
2. **Datafolha 3/10:** a Wikipedia PT registra "1–3 Out, n=2.002" e Zema com 1%. G1 e O Tempo dizem campo apenas em 3/10, n=4.006 e Zema 0 nos votos totais (1 nos válidos).
3. **Futura, datas:** o registro, a Exame e a Wikipedia anunciavam campo de 29/9 a 3/10. O PDF e a Money Times dizem 2–3/10. Uma das matérias da CNN diz 25–29/9, o que parece cópia da rodada anterior. A manchete da CNN chama de "válidos" um 2º turno que, pela soma, está em totais.
4. **AtlasIntel BA, 2º turno:** a CNN dá 64,6 x 35,4 em válidos. A manchete do Poder360 dá 61,6 x 34,3, provavelmente em totais.
5. **Gerp:** a pesquisa divulgada em 3/10 é a **BR-00509/2026** (campo 30/9–2/10), já corrigida no CSV principal. A BR-08168/2026 (campo 1–3/10) não foi divulgada.

## Ainda não publicadas (até ~22h de 3/10)

- **AtlasIntel nacional BR-00999/2026** (27/9–2/10, n≈5.000, divulgação prevista para as 14h). Não encontrei números em Bloomberg Línea, CNN, Terra, UOL, Gazeta ou Poder360, e a Wikipedia PT (revisão das 22:12 UTC) ainda marca "não divulgado". A Atlas divulgou só rodadas estaduais (PA, PI, BA, RJ, PR, SC, ES, PE, MT).
- **Veritá nacional BR-04522/2026** (26/9–2/10, n=40.500). Saíram 19 relatórios estaduais, mas nenhuma consolidação nacional.
- **Gerp BR-08168/2026** (1–3/10).
- **Real Time Big Data e Paraná Pesquisas:** nenhuma pesquisa presidencial nacional nova em 3/10. A última RTBD é de 26–30/9 e já está no CSV.

## Fontes

- G1 Quaest: https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/03/quaest-presidente-3-outubro.ghtml
- SBT News Quaest: https://sbtnews.sbt.com.br/noticia/politica/quaest-lula-46-x-45-flavio-no-1-turno-em-votos-validos
- Brasil 247, Quaest 2º turno: https://brasil247.com/poder/lula-e-flavio-bolsonaro-estao-empatados-no-2o-turno-diz-quaest
- Gazeta do Povo Quaest: https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-outubro-2026/
- G1 Datafolha: https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/03/datafolha-presidente-3-outubro.ghtml
- O Tempo Datafolha: https://www.otempo.com.br/eleicoes/2026/pesquisas/2026/10/3/lula-tem-45-e-flavio-bolsonaro-42-no-primeiro-turno-em-votos-validos-aponta-pesquisa
- Futura, PDF: https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Relatorio_Tracking_Nacional_1_Turno_Final_Votos_Validos-3.pdf
- Futura, CNN 1º turno: https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-448-das-intencoes-de-voto-no-1o-turno-lula-426/
- Futura, CNN 2º turno: https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-48-dos-votos-validos-no-2o-turno-lula-451/
- Futura, Money Times: https://www.moneytimes.com.br/pesquisa-futura-flavio-bolsonaro-tem-425-e-lula-405-no-primeiro-turno-gaep/
- Veritá nacional, PDF: https://lgjdbpskgjfbmlffbntx.supabase.co/storage/v1/object/public/pesquisas/pdfs/1790855512625_Relatorio_Nacional_Verita_Imprensa_27_UFs_20_a_25_Setembro_2026.pdf
- Veritá nacional, Revista Oeste: https://revistaoeste.com/politica/verita-flavio-lula-1-turno/
- Veritá estaduais: PDFs listados na tabela pública `pesquisas` do site eleicoes26.institutoverita.com.br. As URLs estão no CSV.
- Datafolha SP: https://g1.globo.com/sp/sao-paulo/eleicoes/2026/noticia/2026/10/03/datafolha-sp-presidente-3-outubro.ghtml
- Datafolha MG: https://g1.globo.com/mg/minas-gerais/eleicoes/2026/noticia/2026/10/03/datafolha-mg-presidente-3-outubro.ghtml
- Datafolha DF: https://g1.globo.com/df/distrito-federal/eleicoes/2026/noticia/2026/10/03/datafolha-df-presidente-3-outubro.ghtml
- Atlas PA: https://www.cnnbrasil.com.br/eleicoes/atlas-lula-tem-514-dos-votos-validos-no-1o-turno-no-para-flavio-413/
- Atlas PI: https://www.cnnbrasil.com.br/eleicoes/atlas-no-pi-lula-tem-679-dos-votos-validos-no-1o-turno-flavio-275/
- Atlas BA: https://www.cnnbrasil.com.br/eleicoes/atlas-na-ba-lula-tem-605-dos-votos-validos-no-1o-turno-flavio-298/
- Agenda de divulgação com os registros: https://exame.com/brasil/pesquisas-para-presidente-hoje-veja-os-levantamentos-que-serao-divulgados-neste-sabado/
- Gerp BR-00509: https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/gerp-presidente-outubro-2026-vespera-1-turno/
- Wikipedia PT (raw): https://pt.wikipedia.org/w/index.php?title=Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026&action=raw
