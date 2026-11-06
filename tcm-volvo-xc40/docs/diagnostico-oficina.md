# Análise do diagnóstico de oficina (scanner Bosch ESI[tronic])

Dados extraídos de dois relatórios de scanner da oficina. **Dados pessoais
(VIN completo, placa, nome/endereço da oficina e técnicos) foram omitidos de
propósito** — este repositório é público.

## Veículo (confirmado pelo scanner)
- **Modelo:** Volvo XC40 T5 Twin Engine AWD
- **Motor:** **B3154T5** — 1.5 L, 3 cilindros, gasolina (132–192 kW)
- **Transmissão:** **7DCTH** — dupla embreagem, 7 marchas, versão híbrida ✅
- **Quilometragem no diagnóstico:** ~62.275 km
- **VIN:** YV1XZ••••••2058 (mascarado)

---

## Linha do tempo (3 momentos)

### 1) Scan de 23/12/2025 — problema presente, **módulo antigo ainda no carro**
Scanner Bosch ESI[tronic] 19.3. Resumo dos sistemas com falha:

| Sistema | Erros |
|---------|-------|
| Gerenciamento de motor DI B3154T 4.0 (ECM) | **4** |
| Alimentação de tensão / Alternador trifásico 4.0 | 1 |
| **Gerenciamento transmissão 7DCTH 4.0 (TCM)** | **"Sem ligação"** |
| Todos os demais | 0 |

**Memória de erros do ECM (motor):**
| DTC | Descrição | Detalhe |
|-----|-----------|---------|
| **U010100** | Comunicação com Unidade de comando da caixa de câmbio | **Comunicação perdida** |
| **U010187** | Comunicação com Unidade de comando da caixa de câmbio | **Falta mensagem** |
| P0A9068 | Alternador / Motor elétrico A | Informação após ocorrência |
| C007468 | Torque de acionamento solicitado | Erro no algoritmo |
| P061A00 | Módulo interno de regulagem do torque | Sinal não plausível / fora de margem |

### 2) 26/12/2025 — troca da bateria 12 V
- Bateria 12 V substituída (nova).
- Estado da bateria resetado no módulo central (ZE / "Bateria 12V: Repor").

### 3) Scan de 05/02/2026 — **após a troca do TCM**
Scanner Bosch ESI[tronic] 20.0. Resultado:

| Sistema | Erros |
|---------|-------|
| Gerenciamento de motor DI B3154T 4.0 | **0** |
| **Gerenciamento transmissão 7DCTH 4.0 (TCM)** | **0** ✅ (agora comunica) |
| Gerenc. elétr. energia Bateria HV 4.0 | 1 → `P0C7663` |
| Demais | 0 |

- `P0C7663` — "Sistema da bateria de AT (alta tensão): tempo de descarga muito
  longo" → coerente com a bateria híbrida ter ficado muito tempo descarregada.
  Erro apagado em seguida.

---

## Interpretação técnica

### A falha documentada do módulo antigo é PERDA DE COMUNICAÇÃO — não "não aceita gravação"
A evidência primária (tabelas do scanner) mostra:
- o TCM 7DCTH aparecia como **"Sem ligação"** (não respondia ao scanner), e
- o ECM registrava **U0101/U0100 = comunicação perdida com a caixa de câmbio**.

Ou seja: no dia do scan, o módulo estava **fora do barramento** (mudo), não apenas
"recusando atualização".

### ⚠️ Discrepância a esclarecer
O relato verbal anterior era: *"o VIDA comunicava, lia DTCs, mas não aceitava a
gravação"*. Já o scan Bosch mostra **"sem ligação"**. Possíveis explicações (todas
abertas até confirmar):
1. O scanner **aftermarket** (ESI[tronic]) pode ter cobertura limitada do 7DCTH
   híbrido → "sem ligação" seria limitação da ferramenta, não módulo morto.
2. O **VIDA (OEM)** alcançava o módulo, mas a gravação era rejeitada.
3. O módulo estava **intermitente** (às vezes no barramento, às vezes não).

→ **Isso é decisivo para a estratégia de recuperação** e precisa ser esclarecido.

### As 4 falhas do motor são CONSEQUÊNCIA, não causa
U0100, U0101, C007468 (erro de algoritmo de torque) e P061A00 são o que o ECM
registra **quando o TCM para de responder**. Provavelmente há **uma raiz** (TCM fora
do barramento) que cascateia nas demais. Não são 4 defeitos independentes.

### Sobre a hipótese "bateria corrompeu o firmware"
O scan **não prova** isso. Prova que houve **perda de comunicação** — que pode ser
hardware (alimentação, transceiver CAN, MCU) **ou** software. Mantém as duas abertas,
como combinado.

---

## O que isso define para a bancada

A pergunta nº 1 do teste de bancada passa a ser clara:

> **O módulo comunica no barramento quando energizado na bancada?**

- **Se sim** (responde em CAN / bootloader atende) → é mais provável ser problema de
  software/gravação → cenário mais recuperável.
- **Se não** (fica mudo) → diagnóstico de hardware: alimentação, massa, transceiver
  CAN, MCU. Aí a recuperação depende de achar e corrigir a falha física.

## Pendências
- [ ] Esclarecer a discrepância "sem ligação" (Bosch) × "comunicava mas não gravava" (VIDA)
- [ ] Teste de bancada: energizar e verificar se há comunicação
- [ ] Código/estado exato que o VIDA deu **na gravação** (se existir print/log)
