# Arquivos de urna do 2º turno 2026 (TSE) e análise da virada

Programas usados na noite e no dia seguinte ao 2º turno (25-26/10/2026). Os caminhos de trabalho apontam para a
pasta temporária da sessão (`SCRATCH` / caminhos absolutos no topo de cada script): troque pela pasta local antes de rodar.

- `crawl_bu.py`: lê o boletim de urna (BU) de cada seção em resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221
  (um pedido por vez, espera no 429, retoma de onde parou, apaga o bruto). Saída: uma linha por seção.
- `bweb_watch.py`: vigia o Portal de Dados Abertos e, quando o `bweb` do 2º turno sair, lê Presidente de todas as seções.
- `validar_secoes.py`: confere a soma por município com o total oficial do TSE.
- `bu2026.asn1`: especificação ASN.1 do BU (cópia pública; a soma de Brusque bate exatamente com o oficial).
- `parse.py`, `process.py`, `run_*.py`, `build_*.py`, `dl.py`: leitura de BU e log (Brusque e amostra nacional).
- `baixar_mun_2t.py`: resultado do 2º turno por município (arquivos de resultado do TSE).
- `analise_virada.py`: 1º turno (dados abertos, todos os candidatos) x 2º turno por município; regressão ecológica.
- `RELATORIO_AMOSTRA.md`, `brusque_secoes.csv`, `amostra_secoes.csv`, `eventos_urna.csv`: resultados da leitura de
  Brusque (283 urnas) e da amostra de 310 urnas (votos depois das 17h, biometria, eventos). Só contagens por seção.

Uso: `python3 -I <script>` de fora das pastas com arquivos baixados (dados não confiáveis).
