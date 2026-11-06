# Busca por doador / arquivo de firmware (P/N 32313196)

Pesquisa feita em 06/11/2026, vários ângulos. Resumo honesto dos resultados.

## ✅ Hardware doador: EXISTE e está à venda

A busca pelo número exato **`32313196`** achou **módulo usado idêntico à venda**:
- Anúncio (eBay) de **"Volvo XC40 Gearbox ECU Control Unit 32313196, 1.5 Hybrid,
  193 kW, 2021"**, usado.
- **193 kW + 1.5 Hybrid = bate com o T5 Twin Engine.** É o par certo.

**Isso é o achado mais importante:** um módulo-doador idêntico é comprável no mercado
de usados. Ele serve para **duas coisas ao mesmo tempo**:
1. **Fonte do firmware** — lê-se a memória dele na bancada = arquivo de referência.
2. **Reserva** — pode virar o spare direto (após pareamento).

> Um único módulo usado resolve o "doador" e o "reserva" de uma vez.

## ❌ Arquivo de firmware pronto (grátis, na internet): NÃO circula aberto

- O número Bosch **`F01R00DT75`** não retorna nada indexado.
- As comunidades de arquivo de ECU/TCU (MHH Auto, Digital Kaos) cobrem
  principalmente **Mercedes/VW** — **nada do 7DCTH da Volvo**.
- O que aparece nessas comunidades costuma ser **pirataria** (dumps e ferramentas
  "cracked") → **risco de malware, problema legal, e qualidade duvidosa**.
  **Não é o caminho** — além de arriscado, nem tem o arquivo certo.

**Conclusão:** o firmware **não vem** de um download pronto. Ele vem de **ler um
módulo** — o teu próprio (na bancada) ou um doador comprado.

## Referência extra
- A Volvo tem SKUs de **"TCM reload"** (ex.: 31441211, 32138113) — são os códigos
  de serviço de regravação/recarga do próprio fabricante. Confirma que "recarregar
  o software" é um procedimento previsto.

## O que isso define para o projeto

O caminho fica **convergente e mais claro**:

1. **Fase A (bancada)** — lê o teu módulo. Descobre quanto está íntegro.
2. **Se precisar de referência** — compra um **doador usado `32313196`** (existe no
   mercado), lê ele, e usa como arquivo-base **e/ou** como reserva.
3. **Regravação** — com o arquivo certo em mãos, grava pela bancada ("porta dos
   fundos").

Ou seja: **não dependemos de achar um arquivo solto na internet.** Dependemos de
**ler hardware** — que a gente controla.

## Fontes
- [eBay — módulo usado XC40 Hybrid (P/N 32313196)](https://www.ebay.ph/b/Car-Truck-Transmission-Control-Modules/262259/bn_7117884171)
- [Guia TCM Volvo — precisa programação, não é plug-and-play](https://www.go-parts.com/garage/transmission-control-module-volvo-xc60-volvo-s60-volvo-v60-2016-2025)
- [Volvo parts — "TCM reload" (SKU de regravação)](https://usparts.volvocars.com/p/Volvo_2024_S90/TCM-reload-Automatic-Transmission-Transmission-Control-Module-TCM/65198578/31441211.html)
- [Data Transferring — serviço de clonagem de TCM Volvo (precisa P/N igual)](https://www.datatransferring.com/volvotcm)
