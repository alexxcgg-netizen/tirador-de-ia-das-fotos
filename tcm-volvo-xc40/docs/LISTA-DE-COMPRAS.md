# Lista de compras — bancada Fase A (leitura/diagnóstico)

> ⚠️ Preços são **estimativas** (BRL, 2026), não verificadas. Confira nas lojas.
> Objetivo da Fase A: energizar o módulo na bancada e conversar com ele por CAN.
> Custo total estimado do kit básico: **~R$ 250 a R$ 700**, dependendo do que você já tem.

## Essenciais

| Item | Para quê | Estimativa | O que procurar |
|------|----------|-----------|----------------|
| **Multímetro** | Achar GND, CAN (120 Ω) e +12 V sem energia | R$ 80–200 | Com **continuidade (beep)**, **resistência (Ω)** e **modo diodo** |
| **Fonte 12 V com limite de corrente** | Energizar o módulo com segurança | R$ 250–500 | Fonte de bancada 0–30 V / 0–5 A com **ajuste de corrente (CC)** |
| **Adaptador CAN** | Traduz CAN ↔ USB para o PC | R$ 60–300 | Veja opções abaixo |
| **Fios/jumpers** | Ligar fonte e CAN no conector | R$ 20–50 | Jumpers Dupont fêmea + fio 18–20 AWG |

### Opções de adaptador CAN
- **Arduino + módulo MCP2515** (~R$ 60–100): barato, ensina muito, mas dá mais trabalho (firmware tipo SLCAN).
- **Adaptador USB-CAN pronto** tipo CANable / compatível (~R$ 150–300): plugar e usar, funciona com SavvyCAN e `python-can`.
- Qualquer opção: confirmar que tem **transceiver CAN** (ex.: TJA1050/1051) e velocidade **500 kbit/s** (típico, a confirmar).

## Muito recomendados

| Item | Para quê | Estimativa |
|------|----------|-----------|
| **Chicote usado** (ferro-velho/desmanche) | Plug fêmea do TCM com ~20 cm de fio: conecta sem forçar os pinos | R$ 50–150 |
| **Pontas de prova finas / agulhas** | Medir pinos sem deformar | R$ 20–40 |
| **Lupa ou câmera macro** | Ler/fotografar o conector e a placa | R$ 30–80 |
| **Resistor 120 Ω** | Terminação do lado do adaptador (muitos módulos MCP2515 já têm jumper) | R$ 1–5 |

## Não precisa agora
- ❌ Programador de flash / ferramenta de bancada (só na Fase 3, e só se a leitura mostrar necessidade).
- ❌ Doador (módulo usado idêntico): decidido que **não** será comprado.
- ❌ Estação de solda / abertura da carcaça: o módulo é selado e não precisa abrir agora.

## Ordem de compra sugerida
1. **Multímetro** (e já dá pra fazer o truque dos 120 Ω + ler a pinagem no carro).
2. **Fonte com limite de corrente.**
3. **Adaptador CAN.**
4. Chicote/jumpers conforme a pinagem confirmada.

## Segurança
- Fonte **sempre com limite de corrente** (~0,5 A no começo).
- **Nunca** energizar antes de confirmar os pinos (ver `hardware/PINAGEM.md`).
- Bancada sem objetos metálicos soltos em cima do módulo.
