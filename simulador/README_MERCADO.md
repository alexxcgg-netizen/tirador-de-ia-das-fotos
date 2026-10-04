# Mercados de previsão ao vivo (apuração do 1º turno, 4/out/2026)

`simulador/mercado_ao_vivo.py` coleta os preços da Polymarket e da Kalshi e grava:

| Arquivo | Conteúdo |
|---|---|
| `simulador/data/mercado_ao_vivo.csv` | Uma linha por resultado e por coleta (só acrescenta). Colunas: `ts_utc, plataforma, evento, evento_rotulo, mercado_id, resultado, preco, normalizado, bid, ask, ultimo, volume, volume_24h, liquidez, status`. Resultados abaixo de 0,5% ficam de fora do CSV, mas entram na normalização. |
| `simulador/web/mercado_ao_vivo.json` | O retrato mais recente e as séries desde 2026-10-04 12:00 UTC (reescrito de forma atômica a cada coleta). |
| `simulador/data/mercado_ao_vivo_clob_cache.json` | Cache do histórico do CLOB, renovado no máximo a cada 240 s. |

## Uso

```bash
python simulador/mercado_ao_vivo.py                 # uma coleta (cerca de 6 s)
python simulador/mercado_ao_vivo.py --loop 60       # repete a cada 60 s; pare com Ctrl+C
python simulador/mercado_ao_vivo.py --loop 30 --historico-a-cada 600
python simulador/mercado_ao_vivo.py --sem-historico # não consulta o CLOB
python -m pytest simulador/tests/test_mercado_ao_vivo.py   # offline, usa o fixture gravado
```

Se uma API falhar, o erro é registrado no stderr e a coleta segue com o que respondeu. A Kalshi devolve `429` às vezes; nesse caso há uma nova tentativa com espera.

## Mercados cobertos (`evento`)

| evento | Polymarket (slug Gamma) | Kalshi (série) | Normaliza? |
|---|---|---|---|
| `vencedor` | `brazil-presidential-election` | `KXBRPRES` | sim |
| `vencedor_1t` | `brazil-presidential-election-first-round-winner` | `KXBRPRES1R` | sim |
| `decide_1t` | `will-any-presidential-candidate-win-outright-in-the-first-round-of-the-brazil-election` (resultado "Sim") | `KXBRAZILPRES1R` (resultado "Yes") | não (binário) |
| `margem_1t` | `brazil-presidential-election-first-round-margin-of-victory` | `KXBRPRES1MOV` | sim |
| `segundo_1t` | `brazil-presidential-election-first-round-2nd-place` | `KXBRPRESIDENT2` | sim |
| `vai_2t` | `which-candidates-will-advance-to-brazils-presidential-runoff` | `KXBRPRESADVANCE` | não |
| `uf_XX` | `brazil-presidential-election-first-round-1st-place-in-<estado>` para SP, MG, RJ, BA, PR, RS, GO, DF, PE, CE, PA, AM, SC, ES | n/d | sim |

Os nomes dos resultados vêm de cada plataforma. Eles não são uniformes: "Lula", "Luiz Inácio Lula da Silva", "Flavio Bolsonaro", "Flávio Bolsonaro". Para casar os nomes no painel, procure por substring (`/lula/i`, `/fl[aá]vio/i`).

Convenções:
- `preco` é o meio entre bid e ask quando o spread é de até 0,10. Se o spread for maior, usa o último negócio; se não houver negócio, usa o `outcomePrice`.
- `normalizado` é `preco` dividido pela soma do evento.
- Os placeholders negRisk inativos da Polymarket ("Person O", "Candidate A", "Other") são descartados.

## Estrutura do JSON

```jsonc
{
  "gerado_utc": "2026-10-04T17:38:47Z",
  "desde_utc": "2026-10-04T12:00:00Z",
  "destaques": {                         // números de manchete (normalizados)
    "Polymarket": {"vencedor_lula": 0.366, "vencedor_flavio": 0.616,
                   "1t_lula_primeiro": 0.693, "1t_flavio_primeiro": 0.295, "decide_no_1t": 0.0545},
    "Kalshi":     {...}
  },
  "ultimo": [                            // um grupo por plataforma+evento, resultados em ordem decrescente de preço
    {"plataforma": "Polymarket", "evento": "vencedor", "rotulo": "Vencedor da eleição", "soma_precos": 1.0,
     "resultados": [{"resultado": "Flávio Bolsonaro", "preco": 0.6265, "normalizado": 0.616,
                     "bid": 0.626, "ask": 0.627, "ultimo": 0.628, "volume": 1.45e7, "volume_24h": ...,
                     "liquidez": ..., "status": "ativo", "mercado_id": "0x..."}, ...]}
  ],
  "series_meta": {"Polymarket|vencedor|Flávio Bolsonaro": {"plataforma": "...", "evento": "...", "rotulo": "...", "resultado": "..."}},
  "series": {"Polymarket|vencedor|Flávio Bolsonaro": [[1791115200, 0.6305], ...]}   // [epoch_s, preço do SIM]
}
```

Detalhes das séries:
- Há no máximo um ponto por minuto, apenas para resultados com preço a partir de 2%.
- Na Polymarket, a base é o CLOB `prices-history`, com granularidade de 1 minuto em `vencedor`, `vencedor_1t`, `decide_1t` e `margem_1t`, e de 5 minutos nos demais. As coletas do CSV entram depois do último ponto do CLOB.
- Na Kalshi, a série vem só das coletas do CSV, ou seja, começa na primeira execução do script.
- As séries guardam o preço bruto, não o normalizado.

## Como ligar ao painel (`web/index.html`, sem editar aqui)

Quem cuida de `index.html` e `publicar.py` pode fazer o seguinte:

1. **Publicação.** Incluir `web/mercado_ao_vivo.json` na lista de arquivos que `publicar.py` copia e envia, ao lado de `resultados.json`.
2. **Busca periódica**, junto do polling que já existe:
   ```js
   async function carregarMercado() {
     const r = await fetch('mercado_ao_vivo.json?t=' + Date.now(), {cache: 'no-store'});
     if (!r.ok) return;                       // arquivo ausente: esconda o card
     const m = await r.json();
     const d = m.destaques.Polymarket, k = m.destaques.Kalshi;
     const pct = x => x == null ? '–' : (100 * x).toFixed(1) + '%';
     document.querySelector('#mercado-venc').textContent =
       `Flávio ${pct(d.vencedor_flavio)} · Lula ${pct(d.vencedor_lula)} (Kalshi: ${pct(k.vencedor_flavio)} / ${pct(k.vencedor_lula)})`;
     document.querySelector('#mercado-1t').textContent =
       `1º no 1º turno: Lula ${pct(d['1t_lula_primeiro'])} · decide no 1º turno: ${pct(d.decide_no_1t)}`;
     document.querySelector('#mercado-hora').textContent = m.gerado_utc;
     desenharSerie(m.series['Polymarket|vencedor|Flávio Bolsonaro'],
                   m.series['Polymarket|vencedor|Luiz Inácio Lula da Silva']);
   }
   carregarMercado(); setInterval(carregarMercado, 60_000);
   ```
3. **Gráfico.** Cada série é `[[epoch_s, p], ...]`. Para Chart.js ou SVG, mapeie `x = new Date(t*1000)`. Vale marcar uma linha vertical às 20:00 UTC (17:00 de Brasília), quando saem os primeiros boletins do TSE.
4. **Estados.** `m.ultimo.filter(g => g.evento.startsWith('uf_'))` dá o favorito por UF, que pode ser comparado com a projeção de `resultado_1t.py`.
5. **Defasagem.** Mostre `gerado_utc` no card. Se tiver passado mais de 5 minutos, marque o card como "desatualizado".
6. **Durante a apuração**, rode `python simulador/mercado_ao_vivo.py --loop 60` em paralelo ao loop do `resultado_1t.py`, antes do passo de publicação. Os dois escrevem arquivos diferentes, então não há conflito.
