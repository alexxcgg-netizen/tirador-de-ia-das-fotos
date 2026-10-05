# Lições do 1º turno de 2026 (noite de 4/10/2026, ~90% das seções apuradas; adendo de 5/10 no fim)

Notas para a próxima versão do modelo. **Os resultados publicados do modelo de véspera não foram alterados**
(`web/resultados.json`, `premissas.json` e o motor de `modelo.py` ficaram como estavam); a avaliação completa é a de
`AVALIACAO_1T.md` / `data/avaliacao_1t.json`, regerada a cada leitura do TSE.

## O que aconteceu

* **Nacional quase exato.** Visão calibrada: erro na margem Lula − Flávio de −0,3 p.p.; erro médio nos dois
  primeiros 0,45 p.p. (com ~91% apurado). As 28 UFs ficaram dentro dos intervalos de 80%.
* **Erros por UF com estrutura regional.** Margem de Lula subestimada no NE (−3,9 p.p. em média) e no N (−3,6),
  superestimada no S (+5,8); SE e CO perto de zero. Ou seja: a polarização regional foi **maior** que a do prior.
* **Menores superestimados.** Renan (+0,6 p.p.), Zema (+0,16; PIT 0,03) e "outros" (+0,4; PIT 0,01) ficaram abaixo
  da previsão, como em 2014, 2018 e 2022 (erro log da terceira via −0,09, −0,30, −0,43). Cury veio acima (−0,4).

## Leitura

1. **Polarização regional subestimada / encolhimento para o nacional forte demais.** O prior estadual é
   `nacional + 0,85 × lean de 2022` (`estados.fator_lean`, inclinação 2018→2022). Um erro NE/N negativo e S positivo
   é exatamente o que se espera de um fator menor que 1 num ano em que o lean se manteve ou aumentou. As pesquisas
   estaduais (esparsas) não compensaram, e o peso delas contra o prior também encolhe para o nacional.
2. **O erro foi regional, não estadual.** Erros parecidos dentro da região indicam que o componente regional
   (`estados.dp_regional_pp` = 3,0) tem a escala certa para a cobertura, mas o **centro** do prior ficou deslocado
   ao longo do eixo NE/N x S, que é previsível pelo lean.
3. **Menores: a contração da terceira via ainda foi pouca.** A posterior empírico-bayesiana da contração (prior
   `terceira_via.tau0_log` 0,3) encolhe para zero um erro que teve o mesmo sinal em quatro eleições seguidas.

## Mudanças de parâmetros que os dados sustentam (para a próxima eleição; não aplicadas agora)

| Parâmetro | Hoje | Sustentado | Por quê |
|---|---|---|---|
| `estados.fator_lean` | 0,85 | ~0,95–1,0 (ou estimar com 2014–2026) | erro NE/N −, S +; 2022→2026 manteve o lean |
| encolhimento das pesquisas estaduais para o prior | — | menor, quando o lean é estável | o prior puxou NE e S para o centro |
| `terceira_via.tau0_log` | 0,3 | ~0,5 (menos encolhimento da contração) | 4 eleições com menores abaixo das pesquisas |
| `terceira_via.mu_log` (sem prior) | −0,27 | −0,3 a −0,35 | média 2014–2026 |
| `estados.dp_regional_pp` | 3,0 | manter | 28/28 UFs no intervalo de 80%: incerteza adequada |

Antes de mudar, refazer o backtest LOEO (2014/2018/2022 + 2026) com `backtest.py`: com 4 eleições o ganho tem de
aparecer fora da amostra, não só em 2026.

## O que já mudou hoje (só no 2º turno condicionado ao 1º turno real)

* **Transferência regionalizada** (`transferencia_regional.py`): a mesma lição — o contexto partidário da UF importa —
  aplicada aos votos dos eliminados. O eleitor de Caiado/Cury/Zema/Renan num estado muito antipetista vai mais para
  Flávio que a matriz nacional da Quaest diz; num estado petista, menos. β = 0,46 (dp 0,44), estimado nos resultados
  por UF do TSE 2002–2022 e recentrado para não mudar o nacional. Backtest e decisão em BACKTEST.md (seção do 2º
  turno). Efeito em 2026: nacional igual; UFs ±0,35 p.p.
* **Comparecimento entre turnos**: checado em 2014/2018/2022; o método atual (variação média por UF) é o melhor dos
  testados e o efeito partidário é pequeno (≤ 0,25 p.p. no nacional). Sem mudança.

## Recalibração do 2º turno com os erros do 1º turno (5/10/2026, 99,9% apurado)

O 1º turno mostrou um erro de indústria a favor de Lula: na fatia bipartidária Lula/(Lula+Flávio), o agregador
errou +1,8 p.p. e as últimas pesquisas de 11 dos 14 institutos ficaram acima do real (μ encolhido +1,95 p.p.; de
−1,2 na Palver a +4,4 na Indexa). O que isso diz sobre as pesquisas de 2º turno foi testado em 2014, 2018 e 2022
(`vies_institutos.py`, BACKTEST.md, seção final) antes de mudar qualquer coisa:

* **Pesquisas de 2º turno feitas antes do 1º turno** (mesmas entrevistas que erraram o 1º turno): corrigir cada
  instituto pelo seu erro de 1º turno (média da indústria + desvio encolhido) reduz o erro da média de 2º turno de
  +3,5/+4,7 para +2,0/+2,0 p.p. em 2018/2022. **Adotado**; a calibração histórica do 2º turno foi refeita com as
  pesquisas corrigidas do mesmo jeito (sem descontar o viés duas vezes). Em 2026: pesquisas pré-1T 49,6% → 47,7%
  para Lula (peso 0,25 no centro).
* **Pesquisas feitas depois do 1º turno** (entram nesta semana): a mesma correção **piorou** a média da véspera do
  2º turno nos três anos (RMS 0,77 → 1,06 só com desvios, 4,3 com o nível da indústria); o desvio do instituto
  não persistiu (2018: correlação −0,30). **Não adotado** — as pesquisas pós-1T entram como publicadas. Se o erro
  de 2026 persistir no 2º turno, o histórico não permite saber isso de antemão.
* **Viés da indústria 1T → 2T**: com 2026 a escala do viés persistente (τ0) estimada pelos dados é 2,0 p.p. (o
  valor usado); a relação entre o erro do 1º turno de um ano e o erro da projeção do 2º turno é fraca (κ = 0,17 ±
  0,32, prior neutro). Termo de viés do 2º turno: −1,13 → −0,78 p.p.
* **Resultado:** P(Lula) 14,7% → 13,0%; Lula 47,27% → 47,14% (p10–p90 43,8–50,5). Cada mudança isolada: correção
  das pré-1T −0,29 p.p. / −2,9 p.p. em P; viés condicionado +0,11 p.p. / +1,1 p.p. em P (BACKTEST.md).

Ressalvas: 2 anos para a correção pré-1T e 3 para a pós-1T; no pipeline completo LOEO a correção é neutra no
nacional (RMS 1,96 → 1,95) e a cobertura de 80% nas UFs cai de 0,94 para 0,90. O que mais pesa nesta semana são as
pesquisas pós-1T e a deriva entre turnos, que esta recalibração não muda.
