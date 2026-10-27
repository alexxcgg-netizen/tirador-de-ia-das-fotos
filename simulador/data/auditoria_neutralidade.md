# Auditoria de neutralidade de `eventos_2026.csv`

Data da auditoria: 03/10/2026, véspera do 1º turno.

Os eventos servem só de anotação no gráfico. Eles **não entram no modelo** (ver `rodar.py`, função que lê `eventos_2026.csv` apenas para o painel).

## Método

Classifiquei cada evento pelo lado a que ele é **desfavorável**, ou seja, o lado cujo candidato, partido, governo ou aliados aparecem como alvo, réu, derrotado ou alvo de crítica no fato descrito. A classificação ficou na nova coluna `lado_desfavorecido`.

| Valor | Significado |
|---|---|
| `governo_PT` | desfavorável ao governo Lula, ao PT ou a aliados diretos |
| `oposicao_PL` | desfavorável a Flávio ou Jair Bolsonaro, ao PL ou a aliados diretos (PP/Ciro Nogueira incluído) |
| `ambos` | atinge os dois polos (por exemplo, ausência conjunta em debates; CPMI com relatórios opostos) |
| `institucional_neutro` | fato de calendário, de instituição (STF, BC, TSE) ou de candidatura, sem alvo partidário direto |
| `outros` | atinge terceiros candidatos ou partidos (Ratinho, Caiado, Marçal, Zema) |
| `medida_governo` | ato ou medida do governo federal que pode favorecer o governo; a oposição contesta o uso eleitoral |
| `medida_oposicao` | ato de governo estadual da oposição com o mesmo perfil |

Os casos ambíguos foram resolvidos assim:

- **Caso Master:** os fatos que atingem o STF (contrato do escritório da esposa de Moraes, mensagens Vorcaro–Moraes, Toffoli, Mendonça × PF) são `institucional_neutro`. Os ministros envolvidos foram indicados por governos dos dois campos, e cada campo explora uma parte do caso.
- **Veto e derrubada do veto da Dosimetria:** o veto de Lula (8/1) conta como desfavorável à oposição. A derrubada pelo Congresso (30/4) conta como desfavorável ao governo, por ser uma derrota legislativa.
- **CPMI do INSS:** classificada como `ambos`. O relatório da oposição (Gaspar) pedia o indiciamento de Lupi e de Lulinha. O relatório governista apontava Jair Bolsonaro como "mentor" e pedia o indiciamento de Flávio. Nenhum dos dois foi aprovado. A descrição foi reescrita para registrar os dois relatórios; antes, ela só dizia que a CPMI terminou sem relatório.

## Balanço antes da auditoria (27 eventos)

| Lado desfavorecido | n |
|---|---|
| oposicao_PL | 5 (condenação de Bolsonaro, prisão de Bolsonaro, áudios Flávio–Vorcaro, inelegibilidade de Eduardo, inquérito Dark Horse) |
| governo_PT | 2 (derrubada do veto da Dosimetria, saída de Wagner da liderança) |
| ambos | 4 (CPMI do INSS, ausência no debate da Band, cancelamento dos debates da Record e da Globo) |
| medida_governo | 3 (isenção do IR, reajuste do Bolsa Família, MP das bets) |
| medida_oposicao | 0 |
| institucional_neutro | 8 |
| outros | 5 |

**Desequilíbrios encontrados:**

1. **Escândalos do lado do governo sub-representados.** A fraude do INSS só aparecia como "CPMI termina sem relatório". O início da investigação (Operação Sem Desconto, abr/2025) e os números da CGU não estavam na lista, e o salto dos descontos ocorreu em 2023–2024. A declaração de Lula de 1/10 sobre as bets ("eu não sabia") também faltava, assim como o socorro de R$ 20 bi aos Correios.
2. **Medidas de governos de oposição ausentes.** A lista trazia três medidas federais e nenhuma estadual, embora o registro tenha medidas comparáveis da oposição: Tarcísio sancionou reajuste de 10% às polícias cinco dias antes da vedação eleitoral.
3. **Caso Master contado só pelo lado de Flávio e de Wagner.** A busca contra Ciro Nogueira (PP), a delação do operador do filme Dark Horse, o contrato do escritório da esposa de Moraes e a saída de Toffoli da relatoria não apareciam.
4. **Dosimetria incompleta.** A lista registrava a derrubada do veto, mas não o veto (8/1) nem a suspensão da lei por Moraes (9/5). Sem a suspensão, o leitor poderia supor que a pena de Bolsonaro já tinha sido reduzida.

## Eventos acrescentados (12)

| Data | Evento | Lado desfavorecido |
|---|---|---|
| 23/04/2025 | Operação Sem Desconto (PF/CGU) sobre o INSS; números da CGU (R$ 706 mi em 2022 → R$ 3,3 bi em 2024; inserções desde 2016) | governo_PT |
| 09/12/2025 | O Globo revela o contrato de R$ 129 mi do escritório de Viviane Barci de Moraes com o Master | institucional_neutro |
| 09/12/2025 | Decreto dá garantia da União a empréstimo de R$ 20 bi aos Correios | governo_PT |
| 08/01/2026 | Lula veta integralmente o PL da Dosimetria | oposicao_PL |
| 12/02/2026 | Toffoli deixa a relatoria do caso Master | institucional_neutro |
| 24/03/2026 | Moraes concede prisão domiciliar humanitária a Bolsonaro | institucional_neutro |
| 02/04/2026 | Tarcísio sanciona reajuste de 10% às polícias de SP antes da vedação eleitoral | medida_oposicao |
| 07/05/2026 | Compliance Zero (5ª fase): busca contra Ciro Nogueira (PP) | oposicao_PL |
| 09/05/2026 | Moraes suspende a aplicação da Lei da Dosimetria às execuções penais | oposicao_PL |
| 27/05/2026 | Câmara aprova a PEC do fim da escala 6x1 (PL e Novo votam contra; Senado obstruído em 2/9) | medida_governo |
| 03/09/2026 | PGR fecha a delação do "Mineiro" (repasses de Vorcaro para o Dark Horse) | oposicao_PL |
| 01/10/2026 | Lula: "Por que que eu não fiz antes? Ah, porque eu não sabia" (bets) | governo_PT |

**Eventos reescritos (3):**

- **CPMI do INSS:** a descrição agora registra os dois relatórios.
- **Bolsa Família:** passa a informar 15,04% pelo INPC, R$ 600 → R$ 691, pagamento em 19/10 (antes do 2º turno), custo de R$ 5,8 bi e a defesa do governo.
- **MP das bets:** acrescenta o Desenrola 3.0 no mesmo dia, a crítica do PL ("eleitoral") e os recursos do setor ao STF.

## Balanço depois da auditoria (39 eventos)

| Lado desfavorecido | n |
|---|---|
| oposicao_PL | 9 |
| governo_PT | 5 |
| ambos | 4 |
| medida_governo | 4 |
| medida_oposicao | 1 |
| institucional_neutro | 11 |
| outros | 5 |

O total de `oposicao_PL` continua maior. A diferença vem de **decisões judiciais e legislativas contra Bolsonaro e sua família**: condenação, prisão, inelegibilidade de Eduardo, veto e suspensão da Dosimetria e inquérito do Dark Horse. Esses são os fatos registrados no período.

Separando só **escândalos e controvérsias** (categoria `escandalo` e a declaração sobre as bets):

| Lado | Eventos |
|---|---|
| governo_PT | Operação Sem Desconto, saída de Wagner, Correios, "eu não sabia" (4) |
| oposicao_PL | áudios Flávio–Vorcaro, busca contra Ciro Nogueira, delação do "Mineiro" (3). Somado ao inquérito do Dark Horse (categoria `judiciario`), o total também é 4 |
| ambos | CPMI do INSS |
| institucional (STF/BC) | liquidação do Master, contrato Barci de Moraes, Toffoli, relatório Moraes–Vorcaro, Mendonça × PF |

As medidas federais (4) superam as estaduais da oposição (1). Isso reflete a diferença de instrumentos entre governo federal e governos estaduais. Não encontrei com fonte e data outras medidas estaduais de governadores de oposição.

## O que ficou de fora e por quê

- **Pagamentos do Master a Mantega, Lewandowski, Temer, ACM Neto, Rueda, Wajngarten e Frias:** são documentados, mas não encontrei data exata de divulgação para cada caso. A Folha publicou o caso Mantega em 14/08/2026, segundo um resumo de busca que não verifiquei. Se for incluído, deve vir junto com os pagamentos aos demais partidos.
- **Gilmar × Nunes Marques (mensagens de 8/9):** fica coberto pelo evento de 8/9 (crise no STF).
- **TSE e os posts sobre Nossa Senhora Aparecida (plenário 7 × 0 diz que é falso que Flávio propôs a medida):** a data exata da sessão não foi confirmada; a matéria do Brasil de Fato é de 1/10.
- **Prorrogação da subvenção ao diesel até 26/10 (um dia após o 2º turno):** a data da portaria não foi confirmada.
- **Rejeição do recurso de Eduardo (18/9) e nova fase da Sem Desconto:** redundantes com eventos já listados.

## Regras de redação aplicadas

- Cada linha traz só fatos com fonte: decisão, documento, votação, declaração entre aspas ou valor oficial. As alegações aparecem como alegações ("PF alega", "apura suspeita... não provada").
- Quando a fonte é parcial, a linha traz também a resposta ou o contraponto: Flávio nega; Wagner nega; governo diz que cabe nas regras orçamentárias; Lula nega caráter eleitoral; Toffoli fala em "ilações".
- Termos valorativos ficam só dentro de aspas atribuídas ("eleitoral", "mentor", "ilações").
- O painel não mostra a coluna `lado_desfavorecido`. Ela existe para auditoria.
