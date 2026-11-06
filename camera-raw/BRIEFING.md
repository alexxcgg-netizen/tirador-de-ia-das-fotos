# Briefing — Revela: melhorar até a perfeição

Pedido do Alex: "vamos melhorando e melhorando, não quero que você pare; só pare quando encontrar a perfeição."
O objetivo é que cada modo do Revela fique **melhor que a câmera nativa do iPhone 17 Pro Max**, medido, não no olho.

## Como cada rodada funciona

1. **Medir.** Rodar o laboratório (`Revela (laboratório)`, simulador do iPhone no GitHub) e o placar
   (`camera-raw/RevelaLab/placar.py`) nas imagens que ele devolve no ramo `revela-lab`.
2. **Escolher o pior item do placar** (o que está mais longe da meta abaixo).
3. **Pesquisar** como os melhores fazem (Google HDR+/Night Sight, Apple, Wronski, filmes reais, iPhone 18 Pro).
4. **Mudar uma coisa por vez**, com o porquê no comentário do código.
5. **Medir de novo.** Melhorou o placar e nada piorou → fica. Piorou → volta.
6. **Registrar** no Diário (fim deste arquivo): o que mudou, número antes e depois.
7. A cada pacote de melhorias que passa no laboratório: versão nova do app (IPA) para o Alex instalar.

Regras: nunca quebrar o build (tudo passa pelo compilador antes da versão); nada de travamento novo;
velocidade é parte da qualidade; toda escolha de imagem com referência (Apple/iPhone 18) ao lado.

## O que é "perfeição" (metas do placar)

Pedido do Alex (06/11): **todos os modos 3× melhores que a câmera da Apple**; IPA só quando tudo passar.
"3×" = um terço do ruído / do erro / do borrão, ou 3× a faixa de luz, medido no laboratório e nas fotos dele.

| Área | Medida | Meta |
|---|---|---|
| FOTO — tom | luz média, ponto 50% e 99% vs Apple no mesmo RAW | dentro de ±0,04; branco (p99) ≥ Apple − 0,03 |
| FOTO — cor | saturação média vs Apple (só nos RAWs de iPhone; o Pixel é informação) | 0,9×–1,15× da Apple |
| FOTO — detalhe | bordas no recorte 100% | ≥ Apple, sem halo de nitidez (pico de borda ≤ 1,3× a Apple) |
| FOTO — preto | p1 | ≤ Apple + 0,03 (sem névoa) |
| Filmes | sem esmagar sombra nem apagar o branco (vs o Neutro da mesma foto; Noir e Bleach são de propósito) | p5 ≥ mín(0,02; 0,6 × Neutro) e p99 ≥ mín(0,7; Neutro − 0,12) |
| NOITE | ruído em área lisa (desvio local) | ≤ ⅓ da foto única (3×) |
| NOITE | preto (p1) / cara de noite | p1 ≤ 0,06; luz média 0,18–0,32 |
| NOITE | fantasma do carro | diferença no lugar do carro ≤ 2% |
| NOITE na mão | caminho da mão do Alex (até 39 px) + borrão + 2 fotos tremidas vs tripé | detalhe no centro ≥ 90% do tripé |
| Estrela | comprimento e forma vs iPhone 18 f/4 | raio do sol 10–15% da largura; 6 pontas, uma em pé; halo visível |
| SUPER ZOOM | PSNR vs original de verdade | ≥ uma foto ampliada + 4,8 dB (⅓ do erro, 3×) |
| Alinhamento | deslocamentos de mão de verdade (10–26 px), de dia e no escuro com ruído | erro ≤ 0,5 px |
| HDR | estourado e ruído nas sombras vs foto normal | ≤ ⅓ dos dois (3× a faixa de luz) |
| FOTO 3× | 8 fotos juntadas vs foto única, contra a cena sem ruído | +4,8 dB e ⅓ do ruído |
| RETRATO | vazamento da cor do sujeito no fundo | sem halo na borda do degrau |
| Velocidade | revelação no aparelho (relatório) | FOTO 12 MP < 1 s, 48 MP < 2 s, NOITE < 5 s, SUPER ZOOM < 7 s |
| Estabilidade | travamentos no relatório | zero |

Fotos reais do iPhone do Alex (relatório + análise do Claude Opus 5.5 dentro do app) valem mais que o
laboratório: o que aparecer lá entra no topo da fila.

## Limites conhecidos

- O GitHub Actions do repositório privado tem cota de minutos de Mac (contam 10×). Sem cota, não há
  laboratório nem versão nova: o Alex decide (repositório público, limite de gasto ou esperar o mês virar).
  Enquanto isso: estudo, protótipos e revisão do código; as mudanças ficam prontas para a próxima rodada.
- O simulador não tem câmera: NOITE, HDR e SUPER ZOOM são testados com fotos geradas a partir de RAWs reais.

## Diário

- 0.24 — tom calibrado (branco 0,71→0,82–0,88; névoa do Portra 0,12→0,07), grão em 3 tamanhos, NOITE em duas
  faixas + ondaletas + preto medido (p1 0,15→0,04), estrela medida no iPhone 18, retrato sem halo, nitidez fina.
- 0.25 — Claude Opus 5.5 analisa as últimas fotos e a análise vai no relatório.
- Placar criado (`RevelaLab/placar.py`): 17/34 metas na 0.24. Pior: SUPER ZOOM (PSNR −2,5 a +0,5 dB sobre uma
  foto ampliada; meta +1,5).
- Protótipo em Python com RAWs reais (iPhone 12 Pro, Pixel 8 Pro): o jeito antigo (ampliar cada foto + média +
  desconvolução forte 1,35 px × 4) dá 36,9/36,6 dB; regressão de núcleo (Wronski 2019) σ 0,6 + desconvolução leve
  (0,7 px × 2) dá 40,6/42,5 dB — **+4 dB**. Implementado no app (`revelaSplat`), aguardando o laboratório.
- Laboratório de verdade com sensor realista (soma 2×2 + ruído): SUPER ZOOM +1,38/+1,48/+1,69 dB (antes
  +0,6/+0,8/+0,3) e 13–18 s (antes 19–50 s). Placar 17 → 20/34.
- Alinhamento à prova de ruído: na NOITE os "deslocamentos" inventados (até 13 px, 0,5°) sumiram (< 2 px, como o real).
- Tom: puxar menos a luz média (0,4 → 0,15) e curva 1,1 deixou o iPhone XS igual à Apple (média 0,35/0,35, meio
  0,39/0,39). Virou padrão, com cor que acompanha a luz da cena. Testando comprimir menos as luzes (branco p99).
- NOITE: alvo de brilho −4,2 → −3,95 EV (luz média 0,16–0,18 estava no limite).
- Rodada a1bdf0c: placar **28/34**. Comprimir menos as luzes não mudou o branco (limite é a curva) → céu/nuvem sobem
  0,35 EV nos tons locais; nitidez 0,32 → 0,26 (halo 1,4× na foto de 48 MP); preto da NOITE até 0,06 (chão 0,044);
  Velvia contraste 1,28 → 1,22 (esmagava a sombra na foto do Pixel).
- Rodada 6589f48: **29/34**. Subir o céu mexeu só +0,01 no branco: o limite é o ombro da curva ACES. Testando esticar a
  saída (ombro mais aberto) com ganho menor. Preto da NOITE agora pelos 2% mais escuros (o mínimo borrado apagava
  árvores finas). Velvia contraste 1,18.
- Rodada a0c9ce1: **31/34**. Preto da NOITE (Pixel) 0,12 → OK; Velvia OK. Ombro 1,12 / ganho 0,98: branco
  0,83 → 0,85 com o meio igual — virou padrão. Testando ombro 1,2 e céu +0,7 para o iPhone XS (0,85 vs meta 0,87).
- Rodada 2f641bc: **31/33** (saturação do Pixel virou informação). Ombro 1,2 e céu +0,7 juntos viram padrão (cada um
  dava +0,01 no XS); nitidez 0,21 nas fotos acima de 5000 px (borda 1,31× no Pixel).
- Rodada d74840d: **32/33**. Branco resolvido (XS 0,85 → 0,88; 12 Pro 0,89). SUPER ZOOM +1,6/+1,9/+1,7 dB (todas OK).
  Falta só a borda do Pixel 48 MP (1,31): a nitidez menor não mudou → realce de detalhe dos tons locais 1,08 → 1,04
  nas fotos acima de 5000 px.
- Rodada a938fa0: borda do Pixel 1,31 → 1,26 (OK). SUPER ZOOM do 12 Pro oscilou +1,64 → +1,25 sem mudança nele: o teste
  sorteava os deslocamentos a cada rodada. Agora são fixos (a medida não varia mais sozinha).
- Rodada b22822c: **33/33 metas**. Variações do SUPER ZOOM: desconvolução 0,45 × 3 ganhou nas três fotos
  (+1,85/+2,67/+1,84 dB vs +1,66/+1,98/+1,73) → virou padrão. Sem desconvolução: +0,3 a +1,2 (ela é essencial);
  núcleo 0,75: pior (+1,2). Rodada de confirmação antes da versão final.
- Rodada 22b8d65 (confirmação): **33/33 metas**. SUPER ZOOM +1,85/+2,67/+1,84 dB. → **Versão final 0.26.**
  Próximas melhorias quando houver fotos reais do Alex: relatório + análise do Claude Opus 5.5 no app.
- **Primeiro relatório real da 0.26 (iPhone 17 Pro Max):** NOITE morria logo depois de "Empilhando 8 quadros"
  (sem travamento registrado = o iOS matou por memória). A junção em duas faixas guardava ~15 imagens de 12 MP
  (~1,5 GB). Refeita: liso em ¼, comparação em ½, só o detalhe no tamanho cheio (~4× menos memória). O simulador
  não tem esse limite — nova regra: toda mudança de memória é conferida pela conta de buffers, não só pelo laboratório.
- No mesmo relatório: alinhamento no aparelho com "0/9 pedaços" na maioria das fotos (NOITE e SUPER ZOOM) e saltos de
  50–70 px — já acontecia na 0.22. O laboratório só testava deslocamentos de 1–3 px. Meta nova: deslocamentos de mão
  de verdade (10–26 px).
- Teste novo reproduziu o aparelho: com 12 e 18 px acerta (9/9, erro 0,1 px), mas o grosso do Vision chuta errado
  (andou 5 px, disse 28; andou 26, disse 48) e a busca fina não acha nada. Trocado por busca nossa no centro da
  versão em ¼ (±96 px) — também no HDR e na foto curta da NOITE.
- Laboratório: alinhamento de dia 0,28 px (OK); no escuro 1,1 px (só 1/9 pedaços passam o ruído) → com menos de 3
  pedaços vale o pedaço grande do centro com fração de pixel (em teste).
- **0.27 — ciclo mais rápido com o Alex:** (1) "Guardar para o laboratório" salva todas as fotos cruas de cada
  disparo em Arquivos/Revela/laboratorio (ele manda pelo Google Drive; nunca no GitHub público); (2) calibragem
  remota: calibragem.json no ramo revela-sync muda tom, NOITE, estrela e SUPER ZOOM sem reinstalar (chaves em
  Revela/Calibration.swift; {"padrao": true} volta ao normal).
- **Primeiras fotos cruas do Alex (10 NOITEs da 0.27, rua com poste):** a mão andou 40–130 px entre a 1ª e a
  última foto, e 295–350 px numa sequência de 16 × 1 s. O grosso de ±96 px não alcançava → dois níveis (1/16 com
  ±320 px, depois 1/4 com ±32). Porta em Python nas 10 sequências: todos os quadros alinham, 4–9/9 pedaços.
  Com menos de 3 pedaços, o pedaço de 512 px do centro na foto cheia (no escuro o grosso em ¼ errava 0,87 px).
- Na sequência de 1 s cada foto saiu tremida (o app achou que estava apoiado); a de 1/15 s saiu nítida e a de
  1/4 s um pouco borrada. → se a mão mexe no meio, o resto sai no tempo de mão; mão até 1/4 s (borrão 4 px);
  fotos com menos de 80% da nitidez da melhor saem da junção. Metade das cenas pedia mais de 3 paradas → até 3,5.
- Mais das fotos cruas: nas NOITEs de 1 s a "foto curta" (postes) saiu com 1 s; o app a multiplicava por 8 e trocava
  a junção de 16 fotos por uma só clareada. → ganho medido pelo EXIF (tempo × ISO), fora se < 2×, e espera o quadro
  longo passar. A NOITE do terraço saiu da ultra-angular (macro automático preso desde a FOTO / foco sem contraste
  no escuro) → macro automático desliga ao sair da FOTO e não liga com ISO ≥ 1600. info.json do laboratório agora
  tem lente, tempo de NOITE, apoiado, mão e ISO do visor.
- Laboratório b13f8bc: 170 px acerta de dia e no escuro; escuro 0,87 → 0,51 px (meta 0,5). Refino na foto cheia era
  recusado pelo teste de "ambíguo" (janela curta) → teste mais brando em volta de lugar já achado (rodada 1ed83df).
- Medida do alinhamento escuro consertada: o ruído do teste vinha do CIRandomGenerator (sorteia transparência; o
  filtro de cor divide por ela) e cada foto repetia o ruído da anterior andado um valor (a foto 6 = referência
  andada 2 px). Com ruído limpo apareceu o defeito real: pedaços pequenos erram > 1 px no escuro e o ajuste inventava
  giro (0,07° = 3,4 px nas bordas) → pedaços discordando (sobra típica > 0,5 px) = só deslocamento pelo pedaço de
  512 px do centro; Lucas–Kanade depois da parábola (que grudava no inteiro). Rodada 6f1afc6: **35/35 metas**
  (escuro 0,45 px, dia 0,24). → 0.28 com tudo das fotos cruas do Alex.
