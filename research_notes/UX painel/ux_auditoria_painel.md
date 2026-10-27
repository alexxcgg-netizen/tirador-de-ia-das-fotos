# Auditoria de UX/visual e SPEC de redesenho do painel (eleição 2026)

Data: 05/10/2026. Escopo: `simulador/web/index.html` (9 abas), `comparador.html` (fonte real: `comparador/index.html` na raiz do repositório, copiado por `publicar.py`) e `cenarios.html`. Nada foi editado; este arquivo é só diagnóstico e plano.
Pedido do usuário: "mais bonito, fácil de mexer e tudo mais; os gráficos estão legais, mas dá para melhorar; a aba de escolher o candidato, que te leva pra outro lugar, está muito confusa."

## 0. Método e evidências

- Servi `web_publicar/` com `http.server` (com charset utf-8; sem charset o texto sai com acentos quebrados, o que NÃO acontece no artifact publicado porque o invólucro injeta a meta charset) e usei Playwright/Chromium (Chart.js servido localmente, Google Fonts bloqueado, então a medição usa as fontes de reserva).
- 44 capturas: 9 abas + comparador + cenários, em 390 px e 1280 px, claro e escuro (guardadas no scratchpad da sessão, fora do repositório; aqui só cito o que mostram). Mais capturas dirigidas: menu aberto no celular, comparador no passo das áreas e no passo do resultado.
- Medições automáticas (todas as 44 páginas): **sem rolagem horizontal** (scrollWidth = clientWidth em todas), **sem erros de JS** (o único erro de console é o Google Fonts bloqueado pelo meu ambiente), carga+render de cada aba em torno de 0,6 a 0,9 s local.

| Página | Altura a 390 px | Altura a 1280 px |
|---|---|---|
| 2º turno | 13.642 px (~16 telas) | 7.082 px |
| 1º turno | 7.069 | 4.621 |
| Mapa e estados | 5.352 | 3.571 |
| Nordeste | 11.789 | 6.620 |
| **Realidade × discurso** | **56.526 px (~67 telas)** | 26.669 |
| Modelos e comparação | 3.347 | 2.380 |
| Pesquisas e mercado | 7.682 | 4.416 |
| Bastidores | 6.663 | 4.402 |
| Curiosidades | 6.561 | 3.226 |
| **Comparador** | **29.762 px (~35 telas)** | 15.291 |
| Cenários | 30.218 | 17.971 |

O painel já tem uma base boa: tokens de cor, modo claro/escuro (inclusive `data-theme`), `role=tablist/tab/tabpanel` com `aria-selected`, `aria-controls`, tabindex móvel e setas, "pular para o conteúdo", quadro Resumo em cada seção, hash por aba (`#nordeste`), aba lembrada em `localStorage`, `prefers-reduced-motion`. A auditoria abaixo é sobre o que atrapalha **por cima** dessa base. O plano preserva tudo isso.

## 1. Os 10 maiores problemas (resumo)

| # | Sev. | Problema | Evidência |
|---|---|---|---|
| 1 | Crítica | "Propostas dos candidatos" é um link de saída (↗) para outra página, com outro visual, sem a barra de abas; a volta é um link de texto | `index.html` L407; `publicar.py` `documento_comparador` injeta só "← Voltar ao painel da eleição"; capturas do comparador |
| 2 | Crítica | O fluxo do comparador não segue os 3 passos: abre com muro de texto (É / Não é + legenda de 7 etiquetas + contexto de 8 cartões), os "Passos 1 e 2" estão fundidos e o resultado fica 18.540 px abaixo no celular (22 telas) | medido: `#areas` em 3.516 px, `#resultado` em 18.540 px, 192 `select` e 11 sliders |
| 3 | Alta | No celular nenhuma aba fica visível: tudo está atrás de um botão "☰ 2º t…" com rótulo truncado; trocar de aba custa 2 toques. Meu próprio teste automático falhou ao clicar a aba a 390 px por ela estar oculta | capturas 390; `index.html` L270-282 |
| 4 | Alta | Navegação inchada e sem hierarquia: 9 abas + 2 links externos; no desktop o cabeçalho fixo ocupa **173 px** (19% de uma tela de 900) com "Curiosidades" sozinha na 2ª linha e os links numa 3ª | medido `header.top` = 173 px a 1280 |
| 5 | Alta | Não existe "Comece aqui": a primeira tela é a aba "2º turno", que abre direto em "Estimativa, não certeza" e números sem dizer o que é o painel, como ler P(Lula), intervalo de 80% ou Monte Carlo. Não há glossário | `grep` por glossário/`<details>` não acha glossário; `index.html` L396, L423 |
| 6 | Alta | Abas longas demais: Realidade × discurso tem 56.526 px a 390 px; 2º turno 13.642 px. Sem índice fixo, sem recolher seções | tabela acima |
| 7 | Média | Gráficos: 3 canvases sem `aria-label` (`ch-p1`, `ch-p2`, `ch-mk`); linhas verticais de eventos numeradas se amontoam e ficam ilegíveis à direita nos gráficos de pesquisas; histogramas com eixo "% das simulações" por barra de 0,25 p.p. (unidade difícil); texto de canvas em 10 px; sem rótulos diretos; sem faixa de incerteza desenhada no histograma | capturas `pesquisas-1280`, `segundo-turno-390`; `index.html` L1085-1090 |
| 8 | Média | Cores de candidato inconsistentes entre páginas: painel Lula roxo `#4a3aa7` / Flávio laranja `#b4531a`; comparador Flávio **azul** `#2f5fae`, Lula `#7d4aa8`, mais 4 matizes. Entidade com cor diferente por página quebra a regra "cor segue a entidade" | `comparador/index.html` L16-21 × `index.html` L12-13 |
| 9 | Média | Três "cascas" diferentes: painel (fundo quente `#f6f5f2`, texto preto), comparador (fundo frio `#f2f3f5`, azul-marinho `#23366e`, rótulos mono IBM Plex), cenários (cabeçalho próprio com botão "← Voltar ao painel" e tema). Parece três produtos | capturas |
| 10 | Média | Texto pequeno e contraste no limite: 303 elementos com fonte < 12 px; `--text-3` `#75736d` tem 4,62:1 sobre `--surface` mas **4,35:1 sobre `--bg`** (falha AA para texto pequeno); botões do cabeçalho com 34 px de altura; JSON sempre com `cache:no-store` + `?t=Date.now()` (≈1 MB a cada visita, sem cache) | medições e cálculo de contraste |

## 2. Diagnóstico detalhado

### 2a. Navegação e arquitetura de informação

**O que um usuário novo vê.** Desktop: título, uma linha de metadados técnicos ("2º turno atualizado em 05/10 02:30 UTC · TSE 99,99% · 500.000 simulações"), 9 abas em 2 linhas, 2 links com ↗, depois "2º turno — 25/10: Lula x Flávio" com cinco âncoras e um aviso amarelo "Estimativa, não certeza". Os números grandes (47,9% × 52,1%; 23% × 77%) aparecem logo, o que é bom, mas sem uma frase do tipo "o que é isto" nem "como ler". Celular: título cortado ("Simulador presidenci…"), botão "☰ 2º t…" e `Tema`. Não se sabe que existem outras 8 áreas sem tocar no ☰.

**Por que 9 abas atrapalham.** Os nomes misturam três coisas: *o resultado* (2º turno, 1º turno, Mapa, Nordeste), *a checagem* (Realidade × discurso) e *os bastidores* (Modelos, Pesquisas e mercado, Bastidores e premissas, Curiosidades). Quem quer "quem vai ganhar" e quem quer "o que é verdade no discurso" têm o mesmo nível de menu que "Curiosidades". "Modelos e comparação" e "Bastidores e premissas" são vizinhos conceituais. A aba "Realidade × discurso" é o coração da regra nº 1 do projeto (separar realidade de mentira), mas está em 5º lugar.

**Nova arquitetura proposta (5 áreas + sub-abas, sem mudar os 9 painéis existentes)**

Nível 1 (barra fixa; 5 itens cabem no celular como barra rolável, ou como barra inferior):

1. **Comece aqui** (NOVA): o que é, 4 números grandes, "como ler", atalhos.
2. **Quem vai ganhar**: sub-abas `2º turno` · `1º turno` · `Estados` · `Nordeste`.
3. **Realidade × discurso**: aba atual, com índice fixo e seções recolhíveis.
4. **Propostas e cenários**: sub-abas `Comparar propostas` (o comparador, integrado, 3 passos) · `Cenários econômicos` (cenarios.html integrado ou, na 1ª fase, incorporado por iframe de mesma origem não é permitido pelo contrato; ver risco R3) · `Fatos verificados`.
5. **Dados e método**: sub-abas `Pesquisas e mercado` · `Modelos` · `Bastidores e premissas` · `Curiosidades` · `Glossário` (NOVO).

Ordem pelo que o eleitor pergunta: *o que é?* → *quem vai ganhar?* → *o que é verdade?* → *o que cada um propõe?* → *de onde vem isso?* A aba "2º turno" continua sendo a projeção principal (rótulo: "Projeção principal" no cartão de Comece aqui e no menu).

Esboço antes → depois (desktop):

```
ANTES
[Simulador presidencial 2026  meta técnica longa…                      Tema]
[2º turno][1º turno: resultado e avaliação][Mapa e estados][Nordeste][Realidade × discurso]
[Modelos e comparação][Pesquisas e mercado][Bastidores e premissas]
[Curiosidades]
| Propostas dos candidatos ↗   Cenários econômicos ↗          (altura total 173 px)

DEPOIS
[Painel da eleição 2026   Atualizado 05/10 02:30 · fonte: TSE 99,99%         Tema][?]
[Comece aqui][Quem vai ganhar][Realidade × discurso][Propostas e cenários][Dados e método]
   sub-abas (só do grupo ativo):  2º turno · 1º turno · Estados · Nordeste     (altura ≤ 96 px)
```

Esboço (celular, 390 px): título curto em uma linha, barra de 5 chips rolável com o ativo centralizado (`scrollIntoView({inline:'center'})`), sub-abas como segunda barra rolável. Sem hambúrguer. Altura fixa ≤ 96 px (hoje 50 px fechado e 360 px de menu aberto).

**"Comece aqui" (primeira tela, acima da dobra a 390 px).** Conteúdo, nesta ordem:
1. Uma frase: "Simulação da eleição presidencial de 2026 (2º turno em 25/10), calibrada em 2014, 2018 e 2022, com checagem do que é dito contra o que os dados mostram."
2. Cartões "números grandes" (mesmo componente `.stat`): Chance de vencer (Lula 23% · Flávio 77%), Fatia esperada dos votos válidos (47,9% × 52,1%), Faixa de 80% de cada um, Margem em milhões de votos. Cada um com "como ler" em uma linha. Mesma tipografia e mesmo tamanho para os dois candidatos.
3. Aviso de incerteza (o atual "Estimativa, não certeza") reduzido a duas linhas, com link "o que isso significa".
4. Três atalhos em cartões: "Ver a projeção principal", "Checar o que é dito × o que os dados mostram", "Comparar propostas com os meus pesos".
5. "Como ler este painel" em 4 itens + link para o Glossário.

### 2b. O fluxo do comparador (por que confunde, com evidência)

1. **Sai da página.** Item de menu com ↗ (convenção de "abre fora"), navegação completa para `comparador.html`. Some a barra de abas e o cabeçalho; sobra uma faixa "← Voltar ao painel da eleição". Voltar leva ao `index.html` (a aba lembrada vem do `localStorage`, mas o usuário perde a noção de onde estava).
2. **Outra cara.** Fundo `#f2f3f5` (frio) × `#f6f5f2` (quente); acento azul-marinho × quase preto; rótulos em IBM Plex Mono maiúsculo; títulos em Public Sans × system-ui; raio 6 px × 8-12 px. A página de cenários tem ainda um terceiro cabeçalho. Nada sinaliza "é o mesmo produto".
3. **Muro de leitura antes do primeiro controle.** Título, parágrafo, dois quadros "O que esta ferramenta é / não é", legenda com 7 etiquetas (fato, proposta, declaração de campanha, alegação, opinião, calc, inferência) e links; só então 8 cartões de contexto de 2027. O primeiro controle (peso da área) está em 3.516 px no celular (4 telas) e em 1.777 px no desktop.
4. **Passos mal numerados.** A tela diz "Passo 1 e 2" para a seção de áreas e "Passo 3" para o resultado. O usuário não sabe em qual passo está nem quantos faltam.
5. **Significado dos pesos não explicado onde se usa.** O controle é "Quanto esta área importa para você" 0-10, valor inicial 5 em todas (neutro: bom), mas a tela não diz que 5 é o padrão nem que o resultado só usa pesos e notas relativos ("esta área vale X% da conta"). Os 3 "critérios objetivos opcionais" aparecem só no passo 3, com outro eixo de peso (padrão 3), o que mistura duas ideias de peso.
6. **Esforço alto antes de qualquer retorno.** Resultado só aparece com todos os candidatos marcados avaliados em pelo menos 2 áreas: com 6 candidatos, são 12 notas (192 `select` na página, contando as bases ajustáveis). Enquanto isso o painel de resultado mostra uma mensagem longa ("Você ainda não avaliou áreas suficientes… Faltam notas em: Economia e fiscal (faltam 3); Segurança pública (faltam 6)…").
7. **O resultado está longe dos controles e começa por configuração.** O "Passo 3" abre com "Critérios objetivos opcionais" e "Quem entra na comparação" (configuração), depois a mensagem de vazio, depois o resultado. No celular o resultado está 22 telas abaixo da primeira nota. Não há mini-resumo fixo.
8. **A frase do resultado soa como placar.** "A maior pontuação é de X, N ponto(s) à frente do segundo." Está corretamente ressalvada ("não é uma recomendação"), mas a barra ordenada e o "à frente" criam leitura de ranking.
9. **Reiniciar e voltar escondidos.** "Apagar minhas respostas" está no fim do passo 3; sem botão de recomeçar no topo; a confirmação é boa (inline).
10. **"Embaralhar ordem" sem explicação.** É um recurso de neutralidade (viés de posição), mas o rótulo não diz por quê.

**Correção proposta: aba "Propostas e cenários → Comparar propostas", mesma casca, 3 passos.**

Estrutura única na página (sem sair, sem recarregar), com um indicador de passos fixo no topo da aba (`<ol class="passos" aria-label="Passos">`, cada passo é um botão; o ativo tem `aria-current="step"`):

```
[ 1 Escolha o que importa ] → [ 2 Veja o que cada plano propõe ] → [ 3 Resultado por critério ]
  Passo 1 de 3 · 8 áreas · 0 mudadas             [Recomeçar]   [Voltar ao início do painel]
```

- **Passo 1, "Escolha o que importa".** 8 áreas em lista compacta. Cada linha: nome da área, controle de peso com 4 posições rotuladas "Não importa · Importa pouco · Importa · Importa muito" (mapeadas a 0/3/6/10 internamente; o slider 0-10 vira opção avançada), texto "padrão: Importa (5)" até o usuário mexer, e à direita "vale 12% da sua conta" (peso ÷ soma). Todos começam no MESMO valor (hoje 5), sem pré-seleção que favoreça lado algum. Botão "Todas iguais" restaura. Os critérios objetivos opcionais (custo/fonte, PEC, evidência) vão aqui, em um bloco "Critérios extras (opcional)", e não no fim. Um parágrafo de 2 linhas: "Peso diz quanto a área pesa na conta. Nota, no passo 2, diz o quanto a proposta te convence. O resultado é a média ponderada das suas notas."
- **Passo 2, "Veja o que cada plano propõe".** Uma área por vez (navegação "Área 3 de 8 · Segurança pública ‹ ›"), com os candidatos lado a lado no desktop e empilhados no celular, **com a mesma ordem, a mesma ordem de campos e o mesmo estilo para todos**; "Quem entra na comparação" vem aqui, acima dos cartões. Cada cartão: Resumo (com etiqueta fato/proposta/…), Obstáculo principal, Fontes, e a nota "Quanto essa proposta te convence? 0-10" **vazia por padrão** ("sem nota"), como hoje. Faixa fixa no rodapé: "7 de 12 notas · [Ver resultado]". O resultado parcial aparece assim que há 2 áreas completas (regra atual preservada), mostrado em mini-formato na faixa fixa.
- **Passo 3, "Resultado por critério".** Primeiro a sentença neutra e a tabela (área | peso | nota de cada um), **em ordem fixa (a escolhida pelo usuário/alfabética), sem ordenar por pontuação**, com a mesma barra e a mesma cor-neutra por candidato; a pontuação aparece como número com faixa de sensibilidade ("muda se o peso de X for 0 ou 10"). Texto fixo acima: "Isto descreve as suas escolhas. Não é recomendação nem previsão." Em seguida a seção "Se você mudar o peso…", as incertezas e lacunas, e os botões **"Voltar ao passo 2"**, **"Recomeçar"** (com confirmação inline, já existente) e **"Copiar resultado como texto"** (o contrato do artifact bloqueia `window.print()` e downloads, então nada de botão Imprimir; copiar texto funciona dentro do clique, com fallback para selecionar).
- **Mover para fora da jornada:** "O que esta ferramenta é / não é" vira um `<details open>` de 3 linhas no topo do passo 1 (a primeira vez) e recolhido depois; as 7 etiquetas viram "Como ler as etiquetas" (`<details>`), que também alimenta o Glossário; "Contexto de 2027" e "Fatos verificados e contestados" viram sub-abas ou seções recolhidas da mesma aba ("Antes de decidir: contexto de 2027", "Depois: fatos verificados").
- **Neutralidade mantida:** pesos iniciais iguais para todas as áreas; notas vazias; mesmas palavras para todos ("Quanto essa proposta te convence?"); ordem alfabética por padrão com "Embaralhar ordem" explicado ("evita que quem aparece primeiro leve vantagem") ; **nenhuma cor de partido**: usar a cor-por-candidato do painel (ver 2c) ou monogramas neutros (cinza com sigla) em todas as páginas; nenhum candidato é "destacado" ou colocado por padrão à esquerda/em cima por ser favorito; os seis candidatos têm o mesmo tratamento, e a diferença de profundidade (Lula e Flávio completos, os demais resumidos, como no relatório) vem com uma nota visível "análise resumida" e não com tamanho de fonte ou cor.
- **Estado compartilhável:** o contrato do artifact só deixa passar `#token` simples; então `#propostas`, `#propostas-passo-2`, `#propostas-passo-3` abrem direto no passo. Pesos e notas continuam em `localStorage` (por viewer) com `try/catch`; o "copiar resultado" cobre o compartilhamento.

### 2c. Gráficos

Inventário e auditoria (10 canvases no painel, 19 em Cenários, mais barras/mapa em HTML):

| Gráfico | Tipo atual | Adequação | Problemas | Melhoria específica |
|---|---|---|---|---|
| `ch-st-hist` (2º turno, distribuição) | barras de histograma, cor por lado dos 50% | Boa (distribuição de uma incerteza) | Eixo y "% das simulações" por barra de 0,25 p.p. é difícil de ler; "50%" em 10 px; sem marca de mediana e do intervalo de 80%; a legenda "Lula vence / Flávio vence" é boa, mas o rótulo direto na área seria melhor | Trocar o eixo y por "chance" (ou esconder o eixo e rotular a massa: "Lula vence em 23% das simulações" na área roxa, "Flávio vence em 77%" na outra); faixa de 80% sombreada sob a curva com rótulos "43,9%" e "51,8%"; mediana tracejada com rótulo "mediana 47,9%"; título que diz a conclusão |
| Faixas de margem (tabela com barras) | tabela + barra HTML | Boa | Barra na mesma cor do vencedor, sem eixo comum | Manter; alinhar a escala de 0-100%; colocar o total acumulado |
| `ch-1t` (1º turno, histogramas sobrepostos) | linha preenchida | Aceitável | Duas distribuições sobrepostas, sem rótulo direto | Rótulo direto "Lula" e "Flávio" no pico de cada curva; faixa de 80% marcada com um traço sob a curva; remover a legenda |
| `ch-2t` (margem) | barras | Boa | Mesmo caso do `ch-st-hist` | Mesmo tratamento; "Lula +x p.p." / "Flávio +x p.p." nas duas pontas do eixo |
| Mapa de quadrados por UF | tile map divergente | Boa (geografia aproximada) | Rótulo "F >99%" / "L 56%" depende da cor e de siglas; texto branco sobre tons médios pode ficar abaixo de 4,5:1 (verificar `txtOn`); sem legenda de quando é "empate" | Legenda com a escala e o ponto neutro "50%"; borda ou ícone no tile "incerto (45-55%)"; checar contraste do texto em cada passo da escala |
| `ch-p1` / `ch-p2` (pesquisas no tempo) | dispersão + média móvel + linhas verticais de eventos | Adequada, mas sobrecarregada | **Linhas de eventos numeradas se sobrepõem** (a partir de ~25 os números viram um borrão); sem `aria-label`; eixo y truncado (15-55 e 30-56) sem aviso; pontos laranja claros de baixo contraste; dois gráficos lado a lado com 560 px cada | Mover os eventos para uma faixa própria abaixo do eixo x (um marcador por evento, clicável, abrindo a lista), em vez de 39 linhas verticais; mostrar só os 5-8 eventos principais no gráfico; rótulo direto dos dois valores finais ("Lula 40,1% · Flávio 33,0%"); mensagem "eixo começa em 15%" no subtítulo; `aria-label` descrevendo a tendência |
| `ch-mk` / `ch-mv` (mercado) | linhas | Boa | Ticks de hora irregulares (09:00, 13:06, 15:53…); selo "desatualizado há 444 min" já existe (bom); duas codificações (cor e tracejado) já bem aplicadas | Ticks em horas cheias; rótulo direto "Flávio 83,1%" / "Lula 15,2%" no fim da linha; no `ch-mk` adicionar `aria-label` |
| `ch-cal` (calibração) | linhas + diagonal | Boa | Jargão ("cobertura nominal") | "Como ler" abaixo (já há texto); rótulo direto "ideal"; área em torno da diagonal |
| `ch-pit` | histograma cinza | Aceitável | "PIT" sem explicação; barras cinza sem referência além da linha tracejada | Glossário; faixa de aceitação (o que é "normal" para 10 barras); título que diz o veredito ("sem viés sistemático visível") |
| `ch-cur-serie` | linhas | Boa | Legenda com 2 itens | Rótulo direto nas pontas |
| Cenários (`c-traj`, `c-dif`, `c-hist`, `c-sand`, `c-faixas`, `c-reg-*`, `mc-*`, forest, barras) | misto | Em geral boa; pequenos múltiplos já existem em `mc-*` | 19 canvases por página; `tall` com 620 px a 390 px; texto e cores com mesma lógica da casca própria | Reaproveitar o componente de gráfico do painel (opções base, tooltip, cores); manter "inconclusivo" como estado visível |

**Princípios (dataviz) aplicados ao projeto:**
- **Paleta.** As duas cores do painel (`#4a3aa7` roxo e `#b4531a` laranja no claro; `#9085e9` e `#c86a2e` no escuro) **passam** `validate_palette.js` (ΔE de daltonismo 25,7 protan no claro; 21,0 tritan no escuro; contraste ≥ 3:1). Não são cores de partido (PT vermelho, PL azul), então a regra de neutralidade já é cumprida: **manter**. Ação: tornar essa dupla o único mapeamento em todas as páginas (comparador e cenários inclusive). Para a 3ª a 6ª candidaturas, usar uma sequência categórica fixa e validada (não reciclada) ou monograma cinza com sigla; nunca reutilizar roxo/laranja para outro candidato. Rodar o validador a cada mudança de token (teste automatizado, ver §5).
- **Rótulo direto no lugar de legenda** em todo gráfico de ≤ 4 séries; a legenda fica só como reforço para teclado/leitor de tela.
- **Valor-chave anotado**: mediana, faixa de 80%, valor final de cada série, ponto de virada (50%).
- **Incerteza visível e uniforme**: faixa de 80% sombreada e rotulada em todo gráfico de projeção; faixa de 95% mais clara quando existir; mesma convenção em todas as abas.
- **Pequenos múltiplos** para comparações de modelos (calibrado/neutro/viés pleno) em vez de 3 estilos de linha (sólida, tracejada, pontilhada) numa só área.
- **Formato numérico em português, único**: vírgula decimal, milhar com ponto, "milhões" abreviado como "mi" só quando houver espaço ("57,0 mi"; por extenso nos cartões grandes), percentuais com 1 casa (47,9%), intervalo com travessão (43,9–51,8%), pontos percentuais "p.p.". Hoje há `fmtMi`, `fmtVot`, `fmtN` espalhados: concentrar em um único objeto `FMT` usado por tooltip, eixo e texto.
- **Texto de canvas ≥ 12 px** (hoje 10 px na linha de referência) e ticks legíveis a 390 px (≤ 5 ticks no eixo x).
- **Modo escuro**: já existe um conjunto próprio de cores; revalidar contraste de eixos e grade (grade em `--grid` ok); conferir texto sobre os quadrados do mapa.
- **Alternativa em tabela**: botão "Ver como tabela" em cada gráfico, para leitor de tela e para quem quer o número exato.
- **Títulos que dizem a conclusão** + subtítulo de unidade, e uma linha "Como ler" recolhível por gráfico (§2e).

### 2d. Acabamento visual

- **Tipografia.** O painel usa `system-ui` (fonte de reserva vira DejaVu no Linux, que aparece larga e desigual nas capturas); o comparador carrega Public Sans e IBM Plex Mono do Google Fonts. Proposta: um par só para todas as páginas, carregado do Google Fonts com `display=swap` e pilha de reserva (`"Public Sans", system-ui, …` para texto e títulos; `"IBM Plex Mono"` apenas para dados/legendas), com escala fixa: 12 (apoio), 14 (corpo), 16 (corpo em celular), 20, 24, 32, 48 (número grande). `font-variant-numeric: tabular-nums` nos números.
- **Hierarquia.** Hoje quase tudo é cartão com a mesma borda e raio; os blocos de Resumo, avisos, cartões de número e seções têm peso visual parecido. Proposta: cartão com borda só para objetos (números grandes, gráficos); seções sem borda, separadas por espaço e título; Resumo mantém a barra lateral (é a identidade do projeto, e os testes dependem dele).
- **Espaçamento.** Gutters de 16 px já respeitados (sem rolagem horizontal em 44/44 páginas). Padronizar `gap` 8/12/16/24 em tokens `--s-1..--s-5`.
- **Estados de carga.** Hoje "carregando…" no cabeçalho e seções ocultas por `display:none` até o JSON chegar; gráficos aparecem vazios. Proposta: esqueleto (blocos cinza com altura final) nos cartões e gráficos, para evitar salto de layout; mensagem de erro com ação ("Tentar de novo") em vez do texto técnico "abra via servidor estático".
- **Estados vazios.** Já há alguns (mercado "desatualizado"); padronizar o componente "ainda não há dados: o que será mostrado e quando".
- **Microinterações úteis (só estas):** troca de aba sem salto (rolar ao topo do painel com `scroll-margin`), foco no título do painel ao trocar de aba (acessibilidade), realce de 150 ms no número que muda quando o usuário troca a "Visão" (calibrado/neutro/viés pleno), tooltip em toque ("tocar para ver"), `prefers-reduced-motion` respeitado. Sem animação decorativa.
- **Desempenho.** O painel baixa ~1 MB de JSON por visita (`resultados.json` 298 KB, `mercado_ao_vivo.json` 358 KB, `realidade.json` 110 KB, `resultados_2t.json` 77 KB, `benchmarks.json` 50 KB, outros < 40 KB; `cenarios.json` 766 KB só na página de cenários), com `cache:"no-store"` e `?t=Date.now()` em todos. Propostas: (i) cache normal para os JSONs estáticos e `no-store` só para `mercado_ao_vivo.json`; (ii) `mercado_ao_vivo.json` só com as últimas 24 h na carga inicial; (iii) criar os gráficos de uma aba quando ela abre pela primeira vez (hoje as 10 instâncias são criadas de uma vez em painéis ocultos); (iv) carregar `cenarios.json` só ao abrir a sub-aba; (v) `Chart.js` com `defer`.

### 2e. Facilidade de uso

- **Glossário.** Termos sem explicação na interface: Monte Carlo, intervalo de 80%, P(Lula), p.p., PIT, calibração, backtest, viés pleno/neutro/calibrado, válidos, Brier. Proposta: aba "Glossário" (em Dados e método) + definição curta ao toque/foco em cada termo (`<abbr>`/botão com `aria-describedby`, não só `title`, que não funciona no toque). Exemplo: "P(Lula) = em quantas das 500.000 simulações Lula vence; 23% quer dizer cerca de 1 em 4, não que ele terá 23% dos votos."
- **"Como ler" por gráfico.** Uma linha visível sob o título ("Cada barra é uma fatia de 0,25 p.p.; quanto mais alta, mais simulações caíram ali") e um `<details>` com o detalhe; a mesma estrutura em todos os gráficos.
- **Estado compartilhável.** Pelo contrato do artifact só `#token` simples chega à página; então: `#aba` e `#aba-secao` (âncora) funcionam e devem ser o padrão (`#propostas-passo-3`, `#realidade-conta`). Filtros (visão do modelo, métrica do mapa, ordenação da tabela) ficam em `localStorage` (por viewer, com try/catch) e **não** na URL. Para partilhar um resultado do comparador: botão "Copiar resultado como texto".
- **Imprimir/exportar.** `window.print()` e downloads são bloqueados no artifact: oferecer "Copiar resumo" (texto) e uma folha de estilo `@media print` limpa (para quem abre fora do artifact), sem botão de imprimir.
- **Busca/atalhos.** Campo "Ir para…" (atalho `/`), que lista abas, seções e termos do glossário (≈ 60 entradas), no cabeçalho; no celular, um botão de lupa. Substitui o hambúrguer como forma de achar conteúdo. Índice fixo "Nesta aba" (âncoras) já existe em 2º turno e Realidade (`st-nav`); generalizar para todas.
- **Acessibilidade.** Mantém-se o que já está certo (papéis, `aria-selected`, tabindex móvel, "pular", reduced-motion). A corrigir: (i) `--text-3` ≥ 4,5:1 sobre **todas** as superfícies (clarear/escurecer o token: por ex. `#6b6963` sobre `#f6f5f2` dá ≥ 4,9:1; recalcular com script); (ii) texto < 12 px (303 elementos) subir para ≥ 12 px; (iii) alvos de toque ≥ 44 px no cabeçalho (hoje 34 px) e nos botões de segmento; (iv) `aria-label` nos 3 canvases sem rótulo e `role="img"` em todos; (v) mover o foco para o título do painel ao trocar de aba; (vi) anel de foco visível em todos os controles (conferir `:focus-visible` nas sub-abas novas); (vii) ao trocar de aba, anunciar via `aria-live` ("Aba Estados aberta"); (viii) o rótulo do botão de menu não pode ser truncado.
- **Neutralidade na interface (regra nº 1, item 9 do CLAUDE.md: seleção é fala indireta).** A ordem das abas, o cartão "números grandes" e o que aparece na primeira tela são escolhas editoriais. Documentar no próprio "Comece aqui" que a primeira tela mostra a projeção principal e os dois candidatos com o mesmo tamanho e a mesma ordem fixa (alfabética: Flávio antes de Lula? Decidir e manter a mesma ordem em todas as páginas; hoje o painel põe Lula primeiro e o comparador alfabético, o que é outra inconsistência a registrar). Passar o texto novo pelo teste do espelho e pela auditoria (`auditoria_neutralidade.md`).

## 3. Especificação do redesenho

### 3.1 Tokens (um só conjunto para as 3 páginas)

Manter o conjunto do painel (já tem claro/escuro e `data-theme`) como fonte de verdade e ADICIONAR:
`--s-1:4px; --s-2:8px; --s-3:12px; --s-4:16px; --s-5:24px; --s-6:32px`; `--r-1:6px; --r-2:10px`; `--fs-1:12px; --fs-2:14px; --fs-3:16px; --fs-4:20px; --fs-5:24px; --fs-6:32px; --fs-num:44px`; `--focus: 2px solid var(--accent)`; `--cand-a`/`--cand-b` (as duas cores atuais, renomeadas de `--lula/--flavio` APENAS no CSS novo para a ideia de "entidade fixa"; os nomes antigos permanecem como alias para não quebrar os testes e o JS) e `--cand-3..6` validados; `--text-3` corrigido.
O comparador passa a importar esses tokens e abandona `--ink/--muted/--line/--accent` próprios (alias temporário para não reescrever o CSS de uma vez).

### 3.2 Componentes

`.nav-grupos` (5 chips), `.nav-sub` (sub-abas), `.passos` (indicador de 3 passos), `.stat` (número grande, já existe), `.chart-card` (título que diz a conclusão + unidade + gráfico + "Como ler" + "Ver como tabela" + Resumo), `.termo` (glossário em linha), `.skeleton`, `.vazio`, `.busca` ("Ir para…").

## 4. Plano de implementação (ordem, arquivos, critérios de aceitação)

Regra geral para todos os passos: não quebrar `publicar.py` (`converter` exige a string `header.top { position: sticky; top: 0;` em `index.html`; `documento_comparador` exige fragmento com `<title>`, `</style>` e injeta "← Voltar"; `link_cenarios` procura `id="link-cenarios" href="cenarios.html" hidden`), manter as 5 regras de neutralidade, rodar `pytest simulador/tests/test_publicar.py` e a auditoria a cada passo.

**Passo 1. Corrigir o que é pequeno e vale muito (1 PR).** Arquivos: `simulador/web/index.html` (CSS `:root` e dark, L12-60; `.btn-ghost`, `#menu-btn` L246-282; canvases L805, L809, L828), `comparador/index.html` (tokens).
- `--text-3` com contraste ≥ 4,5:1 sobre `--bg`, `--surface` e `--surface-2`, nos dois temas.
- Fonte mínima 12 px (CSS e canvas: `ctx.font` do plugin `vline` L1087, `Chart.defaults.font.size`).
- `aria-label` + `role="img"` nos 3 canvases sem rótulo; rótulo do botão de menu sem truncar.
- Alvos de toque ≥ 44 px (`.btn-ghost`, `.seg button`).
- Cores dos candidatos do comparador iguais às do painel.
Aceitação: contraste ≥ 4,5:1 (script); 0 elementos de texto < 12 px; 10/10 canvases com `aria-label`; 44/44 capturas sem rolagem horizontal; 0 erros de JS.

**Passo 2. Nova navegação em 2 níveis + "Comece aqui".** Arquivos: `index.html` (nav L394-409; JS `ativarAba`/`irPara` L2331-2379; novo painel `painel-comece`; nova estrutura de grupos que **reaproveita os 9 painéis atuais** apenas movendo o mapeamento aba→grupo em JS, sem mover DOM). `publicar.py`: sem mudança (a string `header.top { position: sticky; top: 0;` fica).
- 5 chips no nível 1 + sub-abas; sem hambúrguer no celular; barra rolável com ativo centralizado; cabeçalho fixo ≤ 96 px em 1280 e ≤ 96 px em 390 (com sub-abas).
- Hashes antigos (`#segundo-turno`, `#nordeste`, …) continuam funcionando e abrem o grupo certo; aba inicial = "Comece aqui" na primeira visita e a última aba depois (como hoje).
- "Comece aqui" com 4 números grandes lidos de `resultados_2t.json`, 3 atalhos, "Como ler".
Aceitação: número de abas de nível 1 = 5 (≤ 6); primeira tela a 390 px (viewport 390×844) mostra, sem rolar, título, frase "o que é", pelo menos 2 números grandes e o rótulo "projeção principal"; troca para qualquer um dos 9 painéis em ≤ 2 toques e 0 rolagem horizontal; setas/Home/End funcionam; foco vai ao título do painel; todos os hashes antigos resolvem.

**Passo 3. Integrar o comparador como sub-aba, com os 3 passos.** Arquivos: `comparador/index.html` (fonte), `index.html` (novo painel `painel-propostas` que recebe o fragmento), `publicar.py` (`documento_comparador` deixa de ser necessário para a navegação; manter a função e a página `comparador.html` como compatibilidade/redirect por uma versão, e o link antigo `comparador.html` mostra "Esta página mudou para o painel" com link a `index.html#propostas`).
Opções de integração, pela ordem de preferência: (A) gerar o painel no build: `publicar.py` incorpora o miolo do comparador em `index.html` (menos risco de CSS global vazando: prefixar o CSS com `#painel-propostas`); (B) manter o arquivo separado e carregá-lo com `fetch` num `<div>` (o contrato do artifact permite `fetch` de arquivos publicados junto), injetando o HTML e o CSS prefixado. Preferir A por simplicidade e por funcionar offline.
- Indicador de passos, passo 1 (pesos em 4 posições + % da conta), passo 2 (uma área por vez, mesma ordem de campos, notas vazias), passo 3 (tabela em ordem fixa, sensibilidade, copiar resultado, voltar, recomeçar), rodapé fixo "n de m notas".
- Remover da jornada: bloco É/Não é (vira `<details>`), legenda das 7 etiquetas (vira `<details>`), contexto 2027 e fatos (seções recolhíveis ou sub-abas).
- `localStorage` com a chave atual (`comparador-propostas-2026:v1`) e migração do formato antigo (pesos 0-10 intactos).
Aceitação: o primeiro controle de peso aparece dentro da 1ª tela a 1280 px e a ≤ 1,5 telas a 390 px (hoje 1.777 px e 3.516 px); o link "Propostas" não tem ↗ e não sai da página; voltar/recomeçar visíveis em todos os passos; pesos iniciais idênticos entre áreas e nenhuma nota preenchida; ordem de candidatos alfabética por padrão; resultado com a mesma barra/cor-neutra para todos e **sem** ordenação por pontuação; nenhuma cor de partido; a aba tem Resumo da aba; 0 rolagem horizontal; 0 erros de JS; altura total da aba a 390 px ≤ 12.000 px (hoje 29.762).

**Passo 4. Gráficos.** Arquivos: `index.html` (`baseOpts` L1070-1080, `vline` L1085-1090, `renderHist` L1105+, `ch-st-hist` L1459, `ch-p1/p2` L2398-2418, `ch-mk` L2439, `ch-mv` L2524, `ch-cal/pit` L1229-1240, `ch-cur-serie` L1975); `cenarios.html` (opções L616-625).
- Plugin `rotuloDireto` (rótulo no fim de cada série) e `faixa80` (sombra + rótulos); remover legendas HTML duplicadas quando houver rótulo direto (manter para teclado se necessário).
- `ch-st-hist`/`ch-2t`: eixo y trocado, mediana, faixa de 80%, títulos com conclusão.
- `ch-p1/p2`: eventos em faixa própria; ≤ 8 marcadores; rótulo dos valores finais; aviso de eixo truncado.
- Botão "Ver como tabela" e `aria-label` em todos.
- Módulo `FMT` único (ver 2c) usado em tooltips, eixos e textos; teste de formatação.
- Lazy render por aba (IntersectionObserver ou na ativação).
Aceitação: 100% dos gráficos com `aria-label`/`role=img`; texto de gráfico ≥ 12 px; 0 sobreposição de rótulos a 390 px (verificar por captura); todo gráfico de projeção com a faixa de 80% desenhada e rotulada; paleta validada (`validate_palette.js` PASS em claro e escuro); número em português em 100% dos tooltips (vírgula decimal, "mi", "%", "p.p."); tempo de render da aba ≤ 800 ms local (hoje 0,6-0,9 s com 10 instâncias criadas de uma vez).

**Passo 5. Glossário, "como ler" e busca.** Arquivos: `index.html` (novo painel `painel-glossario` em "Dados e método"; componente `.termo`; campo "Ir para…"). Dados do glossário num `glossario.json` (≈ 40 termos) copiado por `publicar.py` com `copiar_opcional`.
Aceitação: cada termo da lista (Monte Carlo, intervalo de 80%, P(Lula), p.p., PIT, calibração, backtest, válidos, Brier, viés calibrado/neutro/pleno) tem definição ≤ 30 palavras; todo gráfico tem "Como ler" de 1 linha; a busca acha qualquer aba/seção em ≤ 2 teclas além do termo; funciona só com teclado.

**Passo 6. Abas longas.** `index.html`, aba Realidade (L661-760) e Nordeste (L597-655): índice fixo "Nesta aba", seções em `<details>` recolhidas por padrão exceto a primeira, cada uma com Resumo visível mesmo recolhida (o teste exige o Resumo no fim de cada `<section>`; manter o `<aside class="resumo">` fora do `<details>` ou dentro de um `<details open>` marcado).
Aceitação: altura inicial (todas as seções recolhidas) de Realidade a 390 px ≤ 8.000 px (hoje 56.526); 2º turno ≤ 9.000 px; "Expandir tudo" disponível e lembrado em `localStorage`.

**Passo 7. Acabamento e desempenho.** `index.html`/`publicar.py`: esqueletos de carga, estado de erro com "Tentar de novo", tipografia única, cache dos JSONs estáticos (remover `?t=Date.now()` exceto mercado), `mercado_ao_vivo.json` com janela de 24 h (em `mercado_ao_vivo.py`), `cenarios.json` sob demanda; folha `@media print`.
Aceitação: bytes baixados na 1ª visita ≤ 600 KB sem `cenarios.json` (hoje ≈ 1 MB) e ≤ 150 KB na 2ª visita (cache); sem salto de layout visível (CLS < 0,1 em 3 execuções); página (HTML) ≤ 16 MB e cada JSON ≤ 16 MB (limites do artifact).

**Passo 8. Cenários na mesma casca.** `cenarios.html`: trocar cabeçalho próprio pelo cabeçalho do painel; depois integrar como sub-aba (mesma opção A/B do passo 3; `cenarios.json` sob demanda). Manter `link_cenarios` enquanto a página separada existir.
Aceitação: mesmo cabeçalho, tokens e tipografia do painel; sub-aba "Cenários econômicos" sem ↗; gráficos usando os mesmos módulos; 0 rolagem horizontal.

## 5. Testes a adicionar

Em `simulador/tests/` (arquivos novos ou ampliando `test_publicar.py`):
1. `test_ux_navegacao.py`: `index.html` tem exatamente 5 itens de nível 1; todo `data-painel` está mapeado a um grupo; hashes antigos (lista fixa) resolvem; nenhum `<a>` externo (`↗`) para o comparador.
2. `test_ux_tokens.py`: contraste calculado de `--text`, `--text-2`, `--text-3` sobre `--bg`/`--surface`/`--surface-2` nos dois temas ≥ 4,5:1; contraste de `--cand-a/--cand-b` sobre superfície ≥ 3:1; roda a lógica do `validate_palette` para as cores de candidato (ΔE de daltonismo ≥ 8) e falha se cor de partido conhecida entrar nos tokens (lista: vermelho/azul/amarelo exatos de PT/PL, por distância de cor).
3. `test_ux_acessibilidade.py`: todo `<canvas>` tem `aria-label`/`role="img"`; todo `role=tab` tem `aria-controls` e `aria-selected`; todo `button`/`a` com ícone tem nome acessível; nenhum `font-size` < 12px no CSS (regex).
4. `test_ux_comparador.py` (neutralidade): pesos iniciais iguais para todas as áreas; nenhuma nota preenchida em `defaults()`; ordem alfabética por padrão; mesmos rótulos para todos os candidatos; sem cores de partido; resultado não ordena por pontuação; presença de "Recomeçar", "Voltar" e da frase "não é recomendação".
5. Teste de navegador (Playwright, opcional/marcado `@pytest.mark.browser`, pulado se não houver Chromium): para 390 px e 1280 px, claro e escuro, cada aba e cada sub-aba: `scrollWidth == clientWidth`, 0 erros de console (ignorando fontes), cabeçalho ≤ 96 px, primeiro número grande visível sem rolar, controle de peso do comparador visível em ≤ 1,5 telas.
6. `test_ux_formato.py`: função de formatação em português (vírgula decimal, "mi", "%", "p.p.") com casos de borda (0, valores negativos, > 1e7, nulo "–").
7. Atualizar `test_cada_aba_termina_com_resumo` (hoje `assert len(paineis) == 9`): passa para 11 painéis (9 atuais + `comece` + `propostas`; `glossario` também exige Resumo da aba), mantendo a exigência de Resumo por seção. Atualizar `test_documento_comparador_tem_esqueleto_e_volta` se `comparador.html` virar redirecionamento.
8. Teste de `publicar.py`: `converter` continua achando `header.top { position: sticky; top: 0;` após o novo CSS (já há `assert` interno); `copiar_opcional` para `glossario.json`.

## 6. Riscos e como mitigar

- **R1. Quebrar `publicar.py`.** Ele troca uma string exata do CSS do cabeçalho e remove tags do documento. Mitigação: manter a regra `header.top { position: sticky; top: 0;` literal; rodar `python simulador/publicar.py` e `pytest simulador/tests/test_publicar.py` em cada passo; publicar um artifact de teste privado antes do definitivo.
- **R2. Neutralidade.** Navegação, ordem, destaque e redação são escolhas editoriais (regra nº 1, brecha 9). Mitigação: mesmos tamanhos/ordem/estilo para os dois candidatos, pesos iniciais iguais, notas vazias, teste do espelho nos textos novos ("Comece aqui", comparador, glossário), advogado do diabo duplo e `auditoria_neutralidade.md` (audit.py, checks.py) antes de publicar; nenhum "recomendado/favorito" no comparador; cores validadas e sem cor de partido.
- **R3. Contrato do artifact.** Só `#token` simples chega à página (sem `#chave=valor` nem `?query`); `window.print()` e downloads não funcionam; `iframe` de outras origens não é permitido. Mitigação: estado compartilhável só por `#aba`/`#aba-secao`; "copiar resultado como texto"; integrar por incorporação de HTML, não por iframe.
- **R4. CSS vazando ao integrar o comparador.** Mitigação: prefixar tudo com `#painel-propostas`, ou namespace por classe; revisão por captura antes/depois nas 4 combinações (390/1280 × claro/escuro).
- **R5. Conflito com outros agentes editando as mesmas páginas.** Mitigação: fazer cada passo em PR curto, depois de `git pull --rebase`; mudanças de estrutura (passos 2, 3, 6) em arquivo dedicado quando possível (CSS/JS novos em blocos delimitados por comentários).
- **R6. Regressão de dados/gráficos.** Mitigação: comparar números exibidos antes/depois (capturas e `grep` de valores-chave: 47,9%, 52,1%, 23%, 77%); nenhum cálculo muda neste plano, só apresentação.
- **R7. Desempenho em celulares fracos.** Mitigação: render preguiçoso por aba, esqueletos, `mercado_ao_vivo.json` com janela de 24 h.
- **R8. Viés da própria IA no redesenho** (regra nº 5): premissas padrão do painel (visão "Calibrado" como padrão, o que aparece primeiro) já são uma fala indireta; deixar explícito em "Comece aqui" e permitir trocar a visão de qualquer tela.

## 7. Critérios de aceitação globais (resumo)

- 0 rolagem horizontal a 390 px e 1280 px, claro e escuro, em todas as abas/sub-abas e no comparador integrado.
- 0 erros de JS no console (excluindo bloqueio de fontes por rede).
- Contraste de texto ≥ 4,5:1 (tokens) e de marcas de gráfico ≥ 3:1; paleta de candidatos validada.
- Navegação: 5 itens no nível 1; qualquer painel em ≤ 2 toques; cabeçalho fixo ≤ 96 px.
- Primeira tela (390×844): título, "o que é", ≥ 2 números grandes, "projeção principal".
- Comparador: primeiro controle na 1ª tela a 1280 px e ≤ 1,5 telas a 390 px; 3 passos nomeados; recomeçar e voltar visíveis; altura ≤ 12.000 px a 390 px.
- Todo gráfico: `aria-label`, "Como ler", tabela alternativa, texto ≥ 12 px, formatação em português.
- Testes de neutralidade e `test_publicar.py` verdes; `publicar.py` gera `web_publicar/` sem erro.
