# Dicionário CAN / UDS

Registro das mensagens observadas no barramento. Vá preenchendo à medida que
capturar o tráfego em `can-logs/`.

## Mensagens observadas

| CAN ID (hex) | Tamanho | Período | Interpretação | Confiança |
|--------------|---------|---------|---------------|-----------|
|              |         |         |               |           |

## Serviços UDS (ISO 14229) testados

| SID | Nome | Resposta | Notas |
|-----|------|----------|-------|
| 0x10 | DiagnosticSessionControl | | |
| 0x22 | ReadDataByIdentifier | | |
| 0x19 | ReadDTCInformation | | |
| 0x27 | SecurityAccess | | seed/key — anotar sem expor |
| 0x23 | ReadMemoryByAddress | | pode destravar extração de firmware |

## Observações
- Use `candump -L` (can-utils) para salvar com timestamp.
- Identifique primeiro o que é cíclico (telemetria) vs. sob demanda (diagnóstico).
