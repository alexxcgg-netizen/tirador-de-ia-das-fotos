# Engenharia reversa — TCM Volvo XC40 2020 R-Design (T5 híbrido)

Projeto de estudo do **Transmission Control Module (TCM)** removido de um Volvo XC40
2020 R-Design, versão híbrida T5. O módulo foi substituído e a unidade antiga ficou
disponível para análise na bancada.

> **Escopo e legalidade.** Este é um estudo sobre hardware de propriedade do autor,
> feito para fins de aprendizado, reparo e entendimento do próprio veículo. A unidade
> está fora do carro, na bancada. Nada aqui se destina a burlar sistemas de terceiros,
> contornar antifurto/imobilizador de veículos que não sejam o próprio, nem a alterar
> parâmetros de emissões para uso em via pública.

---

## Objetivo

Entender, da camada mais acessível para a mais profunda, como o módulo funciona:

1. **Hardware** — identificar os componentes da placa.
2. **Barramento** — logar e mapear o tráfego CAN / diagnóstico (UDS).
3. **Firmware** — extrair o conteúdo da memória (quando possível).
4. **Análise** — desassemblar e documentar rotinas e mapas.

Cada camada tem uma pasta própria. Comece pela 1 e só avance quando a anterior
estiver documentada.

---

## Estrutura de pastas

```
tcm-volvo-xc40/
├── README.md          ← este arquivo
├── hardware/          ← fotos da placa, part numbers, datasheets, pinagem
├── can-logs/          ← capturas de tráfego CAN (.log, .csv, .asc)
├── firmware/          ← dumps de memória (NÃO comitar binários grandes sem Git LFS)
├── analise/           ← notas de desassembly, mapas identificados, scripts Ghidra
└── docs/              ← guias, checklists, referências
```

---

## Roteiro (passo a passo)

### Fase 1 — Hardware  🟢 viável em casa
- [ ] Fotografar a placa (frente e verso) em alta resolução → `hardware/`
- [ ] Ler e anotar o **part number** do módulo (etiqueta externa)
- [ ] Identificar o **microcontrolador** (provável Infineon TriCore ou Renesas)
- [ ] Identificar chips de **memória** (flash/EEPROM externas, se houver)
- [ ] Identificar os **transceivers CAN** (ex.: TJA1042, TLE6250)
- [ ] Localizar pads de **debug** (JTAG / BDM / DAP) e **pinos de alimentação**
- [ ] Baixar os datasheets dos chips → `hardware/datasheets/`

### Fase 2 — Barramento CAN  🟡 precisa de pouca ferramenta
- [ ] Montar bancada: fonte 12 V + conexão nos pinos de power e CAN-H/CAN-L
- [ ] Interface: adaptador CAN-USB **ou** Arduino + MCP2515 **ou** OBDLink
- [ ] Capturar tráfego "em repouso" e salvar → `can-logs/`
- [ ] Identificar IDs de mensagem recorrentes
- [ ] Testar sessão de diagnóstico **UDS (ISO 14229)** — ler DTCs, data identifiers
- [ ] Documentar o dicionário de mensagens → `docs/can-dictionary.md`

### Fase 3 — Extração de firmware  🟠 difícil
- [ ] Verificar se há leitura por diagnóstico (ReadMemoryByAddress / rotinas de upload)
- [ ] Avaliar bench/boot mode do MCU
- [ ] Último recurso: leitura direta do chip (programador compatível)
- [ ] ⚠️ Esperar proteção de leitura (read-out protection) — documentar o que achar

### Fase 4 — Análise do firmware  🔴 bem difícil
- [ ] Carregar o dump no **Ghidra** com o processador correto (TriCore/RH850 etc.)
- [ ] Identificar vetor de reset, tabela de interrupções, regiões de mapa
- [ ] Documentar funções e estruturas → `analise/`

---

## Ferramentas úteis

| Camada | Ferramenta | Custo |
|--------|-----------|-------|
| Hardware | Multímetro, câmera macro, lupa | baixo |
| CAN | Adaptador CAN-USB / Arduino+MCP2515 | baixo |
| CAN | `can-utils` (Linux: `candump`, `cansend`) | grátis |
| Diagnóstico | Wireshark + plugin CAN, SavvyCAN | grátis |
| Firmware | Programador de flash (conforme o chip) | médio |
| Análise | Ghidra | grátis |

---

## Status

**Fase 1 (hardware) — identificação externa concluída.** Módulo fotografado e
identificado: Volvo **32313196** / Bosch **F01R00DT75** / **TCU-053-19**, controlador
da dupla embreagem **7DCTH** do T5 híbrido. Ver [`hardware/IDENTIFICACAO.md`](hardware/IDENTIFICACAO.md)
e a pesquisa em [`docs/pesquisa-F01R00DT75.md`](docs/pesquisa-F01R00DT75.md).

**Pendências que destravam o resto:**
1. **Código de erro exato do VIDA** na gravação — o dado mais valioso.
2. **Chipset interno** (MCU/flash/EEPROM) — só visível abrindo a carcaça selada.
3. Provável necessidade de **clonagem de EEPROM** para o pareamento (ver pesquisa).
