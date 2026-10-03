# Auditoria de equilíbrio do comparador (03/10/2026, revisão após a leitura dos planos)

Método: um script conta as palavras de cada campo (proposta, concreto, vago, custo, exige, evidência, histórico, quem ganha, quem perde, riscos) dos dados embutidos em `index.html`. As etiquetas como [fato] não entram na conta. O mesmo script conta as fontes, as promessas difíceis, as etiquetas de cautela ([alegação], [opinião], [inferência]) e, desde esta revisão, as etiquetas [declaração de campanha].

## O que mudou nesta revisão

Os seis planos registrados foram lidos diretamente (cópias do Poder360 e do Congresso em Foco; o TSE bloqueou acesso automatizado). Com isso:

- Uma nova etiqueta, **[declaração de campanha]**, marca propostas ditas fora do plano registrado. O mesmo critério vale para todos: Lula 2 (tarifa zero), Flávio 9 (R$ 190 bi, IVA de 20%, Estatuto do Desarmamento, porta de saída de 2 anos, cashback, PEC 12/2026, anistia/indulto, Jerusalém/BRICS/Mercosul), Caiado 2, Zema 3, Cury 2, Renan 0. A diferença reflete o que está ou não nos documentos, não um critério diferente.
- Lula: saiu a meta de “dívida abaixo de 80% do PIB até 2030”, que não está no plano. A promessa difícil correspondente virou “fechar a conta pelo crescimento, sem meta de dívida” (Lula recusou meta em 27/08; o PLOA 2027 projeta ~90% em 2029–30).
- Flávio: entram no plano, com página, 4% de crescimento, R$ 900 bi, 2,5 mi de moradias, ≥10 ministérios, dobrar o gasto federal em segurança, 5 presídios, maioridade 16/14 e 500 mil vagas. Entram o relato da CNN (25/09) sobre uma PEC de R$ 300 bi [alegação], o voto “Sim” na PEC 45/2023 e as ordens de grandeza [calc] de segurança e vagas.
- Goiás: “seguiu a tendência nacional” foi trocado pelo dado do FBSP (−58% contra −31,5%), com a letalidade policial (4,9 contra 3,1 por 100 mil; 29,6% das mortes violentas).
- Os dois favoritos ganharam o PDF do próprio plano como fonte e uma avaliação do FGV IBRE (21/07/2026). Lula ganhou a avaliação do OPEB sobre sua política externa, em paralelo à do OPEB sobre Flávio.
- CSS: corrigido um transbordo de 3 px a 400 px quando o painel “Ver base” estava aberto (já existia antes). O `<select>` dos critérios agora se ajusta à largura do cartão.

## Lula × Flávio Bolsonaro por área

| Área | Palavras Lula | Palavras Flávio | Diferença | Fontes L/F | Promessas difíceis L/F | Cautela L/F | Declaração L/F | Rótulos L (custo/PEC/evid.) | Rótulos F |
|---|---|---|---|---|---|---|---|---|---|
| Economia e fiscal | 362 | 390 | −7% | 12/12 | 5/5 | 4/7 | 1/2 | parcial / não depende / contra | parcial / em parte / contra |
| Segurança pública | 313 | 330 | −5% | 9/10 | 2/2 | 3/3 | 0/2 | não / em parte / mista | não / em parte / contra |
| Saúde | 194 | 193 | +1% | 4/4 | 1/1 | 3/3 | 0/0 | não / não depende / mista | não / não depende / sem base |
| Educação | 205 | 196 | +4% | 6/6 | 1/1 | 4/4 | 0/0 | parcial / não depende / mista | não / não depende / mista |
| Social, Previdência e trabalho | 279 | 286 | −2% | 10/10 | 2/2 | 4/4 | 0/3 | parcial / em parte / a favor | não / em parte / sem base |
| Instituições e corrupção | 215 | 237 | −9% | 8/8 | 1/1 | 3/3 | 0/1 | sem base / não depende / sem base | sem base / em parte / sem base |
| Política externa | 156 | 155 | +1% | 5/5 | 1/1 | 4/3 | 0/1 | sem base / não depende / sem base | sem base / não depende / sem base |
| Meio ambiente, agro, energia, infra | 248 | 226 | +9% | 7/7 | 1/1 | 3/5 | 0/1 | parcial / não depende / a favor | não / não depende / contra |
| **Total** | **1.972** | **2.013** | **−2,0%** | **61/62** | **14/14** | **28/32** | **2/10** | | |

(“Declaração” nesta tabela conta, nos campos da análise completa, as etiquetas [declaração de campanha] e as menções “fora do plano/programa” ou “não consta”; a contagem por candidato na seção anterior conta só as etiquetas, incluindo as promessas difíceis.)

- Todas as áreas ficam dentro de ±10%. Segurança chegou a −24% depois das correções, porque separar “no plano” de “fora do plano” e incluir as 500 mil vagas alongou o texto de Flávio. O texto dele foi enxugado e o de Lula recebeu os itens do plano conferidos por página (FNSP p. 28, controle de armas p. 28, condição da PEC p. 30) e a mesma base de gasto federal (FBSP). Instituições chegou a −15% e foi enxugada da mesma forma.
- Fontes: 61 contra 62. A diferença de uma fonte vem da segurança, onde Flávio cita também a votação da PEC 45/2023 (Conjur).
- Promessas que soam fáceis mas não são: 14 itens para cada um (391 palavras para Lula, 352 para Flávio), com a mesma contagem por área de antes. Mudou o item de dívida de Lula (ver acima). Os itens de Flávio sobre R$ 190 bi, IVA de 20%, anistia e porta de saída levam a etiqueta [declaração de campanha]; o de tarifa zero de Lula também. As 500 mil vagas e o dobro do gasto em segurança de Flávio estão na linha correspondente da seção 5 do relatório; no comparador aparecem no campo “Custo” da segurança, com o [calc], para manter a paridade por área.
- Etiquetas de cautela: Lula 28, Flávio 32. A diferença vem do [alegação] sobre o relato da CNN e do [opinião] do FGV IBRE em Economia, e de [inferência] em Ambiente.
- Os dois recebem o mesmo escrutínio sobre passivos: INSS, Master e Gonet para Lula; Dark Horse, rachadinhas e Aras para Flávio. Os dois têm a ressalva de que não há condenação nem denúncia vigente.

## Rótulos objetivos alterados por esta revisão (base visível na página)

| Área / candidato | Critério | Antes | Agora | Base |
|---|---|---|---|---|
| Economia / Caiado | Depende de PEC | depende | depende em parte | A “PEC emergencial” é declaração (17/09), fora do plano; o plano prevê compensação de despesas por lei |
| Economia / Cury | Custo e fonte | não | parcial | O plano indica a fonte do crédito subsidiado (dividendos de estatais, p. 98), sem estimar o custo |
| Economia / Flávio | Custo e fonte | parcial | parcial (mantido) | Base reescrita: o plano não dá valor; o total (R$ 190 bi) e receitas pontuais foram declarados pela coordenadora; a CNN relata R$ 300 bi |
| Economia / Flávio | Depende de PEC | em parte | em parte (mantido) | Base reescrita: reformular o arcabouço exige LC; corte crível, PEC; relato de PEC com desvinculação [alegação] |
| Social / Flávio | Depende de PEC | em parte | em parte (mantido) | A PEC 12/2026 é defendida fora do plano; os itens do plano dependem de lei |
| Segurança / Flávio | Custo e fonte | não | não (mantido) | A campanha não estima custo; as ordens de grandeza são [calc] do relatório |
| Segurança / Caiado | Evidência | mista | mista (mantido) | Base trocada para o FBSP: −58% contra −31,5%, com letalidade policial alta |

## Candidatos menores (resumo + obstáculo, todas as áreas)

Caiado 335, Zema 322, Cury 232, Renan Santos 359 palavras (antes: 311, 282, 205, 325). Cresceram com os itens conferidos nos planos (autonomia do BC e redução de danos de Caiado; internação involuntária e porte rural de Zema; fonte do crédito de Cury; custo da desfavelização de Renan) e com a marcação das falas fora dos planos. Para Caiado, Cury e Renan, a política externa segue “não encontrada”.

## Neutralidade de apresentação

- Ordem fixa alfabética (Augusto Cury, Flávio Bolsonaro, Lula, Renan Santos, Romeu Zema, Ronaldo Caiado), com botão para embaralhar. O resultado segue a ordem de exibição, não a ordem por pontuação.
- Cores: ciano, azul, violeta, índigo, magenta e grafite, além de um monograma. Não há vermelho, verde nem amarelo. A etiqueta [declaração de campanha] usa a cor de destaque neutra, com borda tracejada.
- As notas começam vazias. O peso de cada área começa em 5 para todas.
- Rótulos objetivos: a evidência segue a coluna “Evidência” das tabelas-síntese do relatório. Os outros rótulos seguem as seções de viabilidade e custo. A base de cada rótulo aparece na página e pode ser trocada pelo usuário. Onde o relatório não dá base, o rótulo fica “sem base” e não entra na conta.

## Verificação

Playwright (Chromium 1194), página envolvida num esqueleto mínimo, Google Fonts bloqueado, 1366 px e 400 px, claro e escuro: nenhum erro de console, nenhuma rolagem horizontal (também com todos os painéis abertos), cálculo, persistência e “apagar” funcionando. Capturas em `screenshots/`.

## Assimetrias que permanecem (vêm do relatório)

- Evidência em Ambiente: “a favor” para Lula (queda de 50,6% do desmatamento, sem atribuição causal) e “contra” para Flávio. O rótulo de Flávio vem do histórico do campo (2019–22), não de uma avaliação da proposta. As duas bases estão explícitas.
- Evidência em Segurança: “mista” para Lula e “contra” para Flávio (armas, contestada), como no relatório.
- Custo: Lula tem “parcial” em 4 áreas e Flávio em 1. Isso reflete custos conhecidos de programas que já existem, não um plano de financiamento.
- Declarações fora do plano: 10 em Flávio contra 2 em Lula na análise completa. É o resultado da leitura dos documentos: o plano de Flávio deixa fora vários números que a campanha divulgou, e o de Lula deixa fora a tarifa zero e qualquer meta de dívida.
