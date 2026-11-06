# Descobrindo a pinagem do conector — TCM 32313196 (7DCTH)

> **Status:** pinagem exata **não encontrada publicamente** (06/11/2026).
> Este guia traz onde procurar + como deduzir com multímetro com segurança.

## ⚠️ Regra de ouro
**Não ligue 12 V em nada enquanto não tiver certeza dos pinos.** Ligar tensão no
pino errado é o único passo do projeto com risco real de matar o módulo.
Todos os testes abaixo são feitos **SEM energia**, só com multímetro.

---

## Método 1 — Procurar em bases de pinagem

Bases que catalogam pinagem de bancada de ECU/TCU (vale buscar pelo P/N,
pelo número Bosch, ou pelo tipo):
- **ecufiles-bg.com** — base com 334 controladores / 1011 variantes de conexão,
  separando **bench**, **OBD** e **boot**.
- **ecu.design** — fichas de pinagem Bosch/Volvo.
- **automatictuningfiles.com/docs/pinouts-ecu** — biblioteca gratuita de fotos de
  pinagem de bancada, inclui Volvo.
- **IO Terminal** — PDF "Volvo modules wiring diagrams".

Buscar por: `32313196`, `F01R00DT75`, `TCU-053-19`, `7DCTH`.

### Referência de PADRÃO (NÃO usar direto!)
Para o TCM **Aisin AW55** da Volvo existe pinagem de bancada publicada:
`12V = pinos 1, 11, 15` · `GND = pino 9` · `CAN-L = pino 6` · `CAN-H = pino 8`.
⚠️ **É outro módulo (automático Aisin, não DCT).** Serve só pra mostrar o *formato*
da coisa — **os pinos do nosso são diferentes**. Não ligar por esses números.

---

## Método 2 — Deduzir com multímetro (o módulo na bancada, SEM energia)

### Passo 1 — Achar o GND (massa)
- Multímetro em **continuidade/beep**.
- Uma ponta na **carcaça de alumínio**, outra em cada pino.
- Pinos que apitam (resistência quase zero) → candidatos a **GND**.

### Passo 2 — Achar CAN-H e CAN-L ⭐ (o truque mais confiável)
- Multímetro em **resistência (Ω)**.
- Medir entre **todos os pares de pinos** procurando **~120 Ω** (ou ~60 Ω).
- O par que der esse valor é **quase com certeza CAN-H / CAN-L** — é o resistor
  de terminação do barramento CAN.
- **Esse é o achado mais fácil e mais seguro de todos.** Comece por ele.

### Passo 3 — Achar o +12 V (alimentação)
- Pinos de alimentação costumam ser **mais grossos** ou **vários em paralelo**.
- No modo **diodo** do multímetro, de GND para um pino de alimentação costuma
  aparecer a queda de um diodo de proteção (~0,3-0,7 V).
- Medindo resistência de GND para o pino de alimentação, muitas vezes o valor
  **sobe devagar** (os capacitores internos carregando) — é um bom indício.

### Passo 4 — Confirmar antes de energizar
- Use fonte **com limite de corrente** (ajustar para ~0,5 A).
- Se ao ligar a fonte entrar em **limite de corrente / curto** → desligue na hora,
  a pinagem está errada.
- Consumo normal esperado: **corrente baixa** (dezenas a poucas centenas de mA).

---

## Método 3 — Ler a pinagem no próprio carro ⭐⭐ (o mais certeiro)

O carro do projeto **usa o mesmo conector** (agora com o módulo novo). Então o
**chicote do carro** entrega a resposta:

1. Com a **ignição desligada**, localizar o conector do TCM no carro.
2. **GND:** continuidade do pino até a carroceria.
3. **CAN:** procurar o **par de fios trançados** (CAN sempre é par trançado) —
   e/ou medir ~60 Ω entre eles com tudo desligado.
4. **+12 V:** com multímetro em tensão, achar o pino que dá ~12 V.
5. Anotar a posição e **transferir o mapa** para o módulo de bancada.

> Vantagem: é o **mesmo conector**, então o mapa é exatamente o certo.
> Cuidado: trabalhar com ignição desligada, não curto-circuitar pinos.

---

## Tabela para preencher

| Pino | Função confirmada | Como foi confirmado |
|------|-------------------|---------------------|
|      | GND               |                     |
|      | +12 V (VBAT)      |                     |
|      | +12 V (ignição)   |                     |
|      | CAN-H             |                     |
|      | CAN-L             |                     |

## Ordem recomendada
1. Método 1 (buscar nas bases) — grátis, rápido.
2. Método 2, Passo 2 (truque dos 120 Ω) — acha o CAN sem risco.
3. Método 3 (ler no carro) — confirma tudo com certeza.
4. Só então energizar, com fonte limitada em corrente.
