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

| Área | Medida | Meta |
|---|---|---|
| FOTO — tom | luz média, ponto 50% e 99% vs Apple no mesmo RAW | dentro de ±0,04; branco (p99) ≥ Apple − 0,03 |
| FOTO — cor | saturação média vs Apple (só nos RAWs de iPhone; o Pixel é informação) | 0,9×–1,15× da Apple |
| FOTO — detalhe | bordas no recorte 100% | ≥ Apple, sem halo de nitidez (pico de borda ≤ 1,3× a Apple) |
| FOTO — preto | p1 | ≤ Apple + 0,03 (sem névoa) |
| Filmes | sem esmagar sombra nem apagar o branco (vs o Neutro da mesma foto; Noir e Bleach são de propósito) | p5 ≥ mín(0,02; 0,6 × Neutro) e p99 ≥ mín(0,7; Neutro − 0,12) |
| NOITE | ruído em área lisa (desvio local) | ≤ 50% da foto única |
| NOITE | preto (p1) / cara de noite | p1 ≤ 0,06; luz média 0,18–0,32 |
| NOITE | fantasma do carro | diferença no lugar do carro ≤ 2% |
| Estrela | comprimento e forma vs iPhone 18 f/4 | raio do sol 10–15% da largura; 6 pontas, uma em pé; halo visível |
| SUPER ZOOM | PSNR vs original de verdade | ≥ uma foto ampliada + 1,5 dB |
| HDR | detalhe nas nuvens (p99 não estourado) e sombra | nuvem com textura; p1 ≤ 0,05 |
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
