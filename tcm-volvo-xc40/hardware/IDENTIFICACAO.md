# Identificação do hardware — TCM Volvo XC40 T5 Hybrid 2020

> Status: **identificação externa confirmada por fotos** (06/11/2026).
> Interior ainda selado — chips internos pendentes de abertura/teardown.

## Fotos
Ver pasta [`fotos/`](fotos/):
- `01-etiqueta-principal.jpg` — etiqueta Volvo/Bosch
- `02-tampa-respiro-AMF300200.jpg` — respiro de compensação de pressão (NÃO é chip)
- `03-verso-tracelabel.jpg` — verso com trace label
- `04-conector-geral.jpg` / `05-conector-pinos.jpg` — conector
- `06-modulo-completo.jpg` — visão geral

## Etiqueta do módulo (CONFIRMADO)

| Campo | Valor |
|-------|-------|
| **Volvo P/N** | **32313196** |
| **Fabricante** | Bosch |
| **Bosch P/N** | **F01R00DT75** |
| **Designação de tipo** | **TCU-053-19** (Transmission Control Unit) |
| **Código de data** | `191120` → 20/11/2019 |
| **Campos auxiliares** | `210044` (V210044), `0376` / `T191120A0376` |
| **Origem** | China |
| **Trace label (verso)** | 5012209625 |
| **Marcação tampa/respiro** | AMF300200 — nº `190709231231` |

## Interpretação

- Confirmado que é o **TCM/TCU** (etiqueta diz "TCU" explicitamente).
- Pela arquitetura (carcaça de alumínio aletada, selada, com **respiro de compensação
  de pressão**, conector único grande), é um **controlador de transmissão de dupla
  embreagem (DCT) montado externamente** — coerente com a caixa **7DCTH** do T5 híbrido.
- Isso o diferencia dos TCMs das versões **2.0L** (T4/T5 mild-hybrid), que usam
  transmissão automática Aisin de 8 marchas (conversor de torque) e módulos diferentes.
  **→ Por isso as referências de anúncio não batem (ver nota de compatibilidade abaixo).**

## Nota de compatibilidade (IMPORTANTE)

| Referência | Situação |
|-----------|----------|
| **32313196** | ✅ A real, lida na etiqueta do módulo físico |
| 31686384 | ❌ Visto em anúncio — é TCM de XC40, mas superseded por 31461858 e com faixa de chassi específica; **não confirmado pro híbrido** |
| 36010492 | ❌ Apareceu em busca anterior — **não confirmado, não corresponde** |
| 31380617 → 32249308 | ❌ TCM de XC40 **2.0L** (T4/T5 gasolina) — provavelmente é o da Aisin 8 marchas, **não** o da DCT híbrida |

## Microcontrolador (INFERÊNCIA — não confirmado)

Não dá pra ver o chip (módulo selado). Mas, por contexto:
- Datasheet de TCU da Bosch descreve arquitetura **multicore lockstep, AUTOSAR 4.0,
  ISO 26262 ASIL D**.
- A família **Infineon AURIX (TriCore)** é a típica para DCT nesse período.
- **Hipótese mais provável:** MCU Infineon AURIX **TC2xx** (ex.: TC27x/TC29x),
  fabricação 2019. ⚠️ **A confirmar** só abrindo o módulo ou com datasheet do F01R00DT75.

## Memória
- Flash e EEPROM: **pendente** (ver só abrindo). A nota de mercado de "EEPROM cloning"
  sugere que há uma EEPROM externa relevante para o pareamento. A confirmar.

## Debug / programação
- Pads JTAG/DAP/BDM: **pendente** (interior selado).

## Pinagem do conector
_(a mapear com multímetro — continuidade até os chips, após abrir)_

| Pino | Função provável | Confirmado |
|------|----------------|------------|
|      |                 |            |
