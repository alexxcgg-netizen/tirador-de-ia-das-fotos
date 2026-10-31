# Ponte Revela ↔ Claude

Este ramo não tem código. É por onde o app Revela (no iPhone) e o Claude trocam dados.
O app lê e grava aqui com uma chave do GitHub guardada no Keychain do iPhone.

| Arquivo | Quem escreve | Para quê |
|---|---|---|
| `looks.json` | Claude e app | Filmes próprios (lista de `CustomLook`). O app junta pelo `id`. |
| `ajustes.json` | Claude | Ajustes que o app aplica quando o arquivo muda. |
| `recado.json` | Claude | `{"id": "...", "texto": "..."}`: aparece uma vez no app quando o `id` muda. |
| `estado.json` | app | Versão, validade da instalação e ajustes atuais (ao abrir, no máximo a cada 10 min). |
| `relatorios/*.md` | app | Relatório enviado pelo botão "Enviar ao Claude" (e sozinho depois de um fechamento). |

## `ajustes.json`

Só as chaves presentes são aplicadas:

```json
{
  "look": "Portra 400",
  "intensidade": 0.8,
  "grao": 1.2,
  "ettr": true,
  "protegerPele": true,
  "macroAutomatico": true,
  "visor60": false,
  "tresLooks": false,
  "looksExtras": ["Kodachrome", "Tri-X 400"],
  "estabilizacao": "Forte",
  "nivel": true,
  "grade": true,
  "modosEscondidos": ["DUPLA", "AÇÃO"],
  "ordemDosModos": ["FOTO", "RETRATO", "NOITE"]
}
```

`look` e `looksExtras` aceitam o nome de um filme pronto ou de um filme próprio.

## `looks.json`

Cada item tem `id` (UUID), `name`, `base` (nome de um filme pronto) e os ajustes: `exposure`, `contrast`,
`saturation`, `warmth`, `tint`, `fade`, `shadowColor`, `grain`, `grainSize`, `vignette`, `halation`,
`bloom`, `blackAndWhite`.
