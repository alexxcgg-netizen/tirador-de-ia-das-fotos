## Skeptical review of the v2 scenario model, 2027–2034 (read-only)

**Scope.** I reviewed branch `briefing-eleicao-2026` at `b39459d`:
- `cenarios/` (`cenarios.py`, `premissas.py`, `dados.py`, `rodar.py`, `tests/`);
- `simulador/web/cenarios.html` and `cenarios.json`;
- the v1 review;
- the input notes (`salario_minimo_equilibrio_geral`, `macro_fiscal_dinamica`, `custos_ocultos_credito_subsidios`, `conta_completa_politicas`, `isencao_ir_incidencia`, `medido_vs_vivido`, `sanduiche_eleitoral`, `cenarios_economicos_insumos`, `checagem_promessas_discursos`).

I edited no model file. All experiments ran on copies in the scratchpad: n = 30,000 per winner, seed 2026, the same seed scheme as `rodar.py`.

Notation: "D" is the Lula-winner index minus the Flávio-winner index in 2030, in points of the 2026 = 100 index. Positive means higher under Lula.

---

## 0. Bottom line

1. **The top-line conclusion is honest and robust.** All 10 household types are inconclusive, and none is robustly better off under either winner. I reproduce it, and none of the problems below would overturn it. If anything, the problems show that the one near-result (formal 1 SM, D = +2.2, P = 0.82) is weaker than it looks.

2. **The central-set numbers below the headline are not neutral enough to publish as they stand.**
   - **Formal 1 SM.** The +2.2 points comes almost entirely from unsourced assumptions about how Flávio executes his plan, not from the economic mechanisms:
     - abono incidence and the composition of the fiscal adjustment: about 1.2–1.4 points;
     - Lula's intention to keep the minimum-wage rule set at 1.0, against 0.85 for Flávio: about 0.55 points;
     - PEC 12: about 0.36 points.
     
     With the same intention for both (0.9) and an abono cut that spares 1-SM workers, D falls to **+0.32 (P = 0.54)**.
   - **Top decile and "capital" cells.** These gain whenever the Selic is high, including in a credibility crisis. That sign is very likely wrong, because the model counts only interest income and never the fall in asset prices.

3. **Verdict: conditionally fit to publish as "scenarios, not forecasts".** Fix or prominently caveat C1, C2 and M1–M4 first (§2). The engine is in much better shape than v1:
   - the minimum-wage lag bug is fixed;
   - the Bolsa Família prior is symmetric in the central set;
   - the fiscal feedback loop is switched on;
   - cuts and financing have incidence;
   - "mediano" is gone;
   - tests pass and results reproduce.

   The remaining problems sit in the priors, in the assumption sets and in how the page presents them.

---

## 1. Were the v1 flaws fixed?

| v1 item | Status in v2 | Evidence |
|---|---|---|
| R2: minimum-wage rule lag (`pibs[-1]` = t−1) | **Fixed** | `cenarios.py:443` uses `pibs[ano - 2]`, clipped to 0.6–2.5% until 2030 (`:444`). `test_regra_do_minimo_usa_pib_de_t_menos_2` checks the 2029 raise against 2027 GDP and confirms the old lag would differ. The 0.6% floor is still sourced only to Rádio Senado (SM note §11), as the page says. |
| R1: Bolsa Família prior (+7 points, P = 0.98) | **Fixed in the central and neutral sets.** **Reintroduced in the pro-Lula set** (M1) | Bernoulli raise event that restores the cumulative INPC, with U(0.3, 0.9) for both (`premissas.py:234,266`). But `aplicar_conjunto("pro_lula")` sets L U(0.6, 0.95) and F U(0.2, 0.6) (`:440-441`), with no mirror in pro-Flávio. |
| R3: fiscal feedback switched off | **Fixed** | Premium = regime + E8 × (d − d_consensus) (`cenarios.py:499-506`). P(crisis) rises with excess debt (`:396-398`). Demand multipliers apply by instrument (`:572-581`). Shapley turns channels off against a common reference, not a re-estimated path. Weak spot: M5. |
| R4: incidence of cuts and financing | **Implemented, but the parameters driving the results are invented** (C1, M3) | Dirichlet draw over composition (`:325`); abono (`:771-774`); in-kind services (`:881`); unfunded promises covered by debt or cuts (`:469-473`). |
| R8: "mediano" label | **Fixed** | `BASE` separates `renda_media_trabalho` (3,777) from `renda_mediana_trabalho` (2,300, from `kaitz_uf.csv`), and no type is called "median". `test_rotulo_media_nao_mediana` (`tests:58-61`) is vacuous, though: it checks that the key `"renda_mediana"` is absent, and it is absent only because the real key is `renda_mediana_trabalho`. |
| R5: 3-state regime, no Selic draw per candidate | Fixed | `premissas.py:205-207`; Taylor rule at `cenarios.py:517-522` |
| R6: exchange rate → income, Selic loadings by component | Partly fixed. The FX → income mapping is unsourced (m4) | `cenarios.py:67-68,697` |
| R7: interest by credit line, financial income | Credit lines fixed. Financial income added, but its sign is wrong in a crisis (C2) | `premissas.py:288-291`, `cenarios.py:815-824` |
| R9: binary unemployment risk by group | Fixed. It now dominates the variance (m1) | `cenarios.py:727-748` |
| R10: income-tax table correction as an event | Fixed. The prior is asymmetric and contradicts its own docstring (M2) | `premissas.py:236,269` vs `:11-12` |
| R12: fuels split into gasoline, diesel, LPG, bus fares | Fixed | `cenarios.py:541-553` |
| R13: error-correcting wages | Fixed | `cenarios.py:627-632` |
| R15: 6x1 with the same probability for both; hourly index; CE | Same probability: done. CE: done. **Hourly-wage index: not done** | `premissas.py:240,273` |

**Reproducibility.**
- `pytest cenarios/tests`: 36 passed (5.5 s).
- `rodar.py --n 20000 --n-shap 300 --n-sens 3000` writing to the scratchpad reproduces the published 2030 differences to within ±0.06 points for every type and set, with the same 10 × "inconclusivo". Examples:
  - formal 1 SM: 2.20 vs 2.21;
  - top decile: 0.90 vs 0.95;
  - pro-Flávio, formal 1 SM: −0.16 vs −0.18.
- A direct `rodar_par` run at n = 30,000 gives formal 1 SM +2.17 and top decile +0.94.

---

## 2. Ranked issues

### CRITICAL

#### C1. The only near-result (formal 1 SM, +2.2, P = 0.82) is driven by unsourced assumptions about Flávio's execution, but the page presents it as a channel effect

**Evidence.** The published Shapley split for formal 1 SM in 2030 is: fiscal +0.88; minimum wage direct +0.86; 6x1/PEC 12 +0.36; taxes +0.34; interest −0.29.

My counterfactual runs (central set, D for formal 1 SM in 2030):

| Change | D | P(L > F) |
|---|---|---|
| Published central | +2.17 | 0.82 |
| Abono share of mandatory cuts set to 0 (`obrig_abono`, `premissas.py:157`) | **+1.01** | |
| Flávio's adjustment composition set equal to Lula's (`premissas.py:226` vs `:258`) | **+0.79** | |
| Lula's intention to keep the rule 0.85, the same as Flávio's (`:233`) | +1.62 (pensioner on the floor: +0.93 → **+0.14**) | |
| PEC 12 switched off | +1.81 | |
| **Intention 0.9 for both + abono share 0** | **+0.32** | **0.54** |

**Why these assumptions are not defensible as central values.**

1. **Abono share U(0.1, 0.5) has no source.** It is marked `[suposição]` at `premissas.py:157`.
   - The only concrete signal about Flávio's mandatory cuts is the CNN report of 25/09 (`checagem_promessas_discursos.md:206`): he would remove the earmarked floors for health and education. Those cuts appear in the model only as in-kind income (`in_natura`), not in the index.
   - The only real precedent for cutting the abono is the Lula government's own 2024 package. It **restricts eligibility from the top**, so the ceiling shrinks towards 1.5 SM and 1-SM workers keep the benefit.
   - The incidence rule at `cenarios.py:772` (`corte_ab = ob_abono · x_obr / 0.22`, applied proportionally to every beneficiary) is the worst case for 1-SM workers.
2. **Composition** (F 30% mandatory against L 10%) is also `[suposição]` (`premissas.py:224-226, 257-258`). The note's argument is that discretionary spending of R$ 222 bn cannot fund R$ 190 bn, which is correct. But it does not imply that the mandatory part falls on 1-SM workers.
3. **Rule-keeping intention.**
   - L = 1.0 ignores that the Lula government itself changed the rule in Dec/2024 (Lei 15.077, cap of 2.5%) under fiscal pressure.
   - F = 0.85 departs from the input note's own F6 = 0.65 (`cenarios_economicos_insumos.md`, table 7.2). The central value is therefore sourced on neither side.

**Fix.**
- Abono incidence: model abono cuts as eligibility restriction from the top. For formal 1 SM, use `corte_ab` = 0 unless the mandatory cut exceeds ~0.15% of GDP. Put `obrig_abono` U(0, 0.3) in the tornado for both sides.
- Rule-keeping intention: a common prior for both, e.g. U(0.8, 1.0) (L: 2024 precedent; F: 03/10 statement). Move the asymmetry to the pro-Lula and pro-Flávio sets.
- On the page: tag the "fiscal" and "minimum wage direct" Shapley bars for formal 1 SM and the floor pensioner as **"depende de suposição sobre a execução"** (depends on an assumption about execution). Show the "intention 0.9 for both + abono 0" counterfactual next to the central value.

#### C2. Top decile and capital incomes rise in a credibility crisis (flow-only accounting of wealth)

**Evidence.**
- Financial income is computed as `ret = 0.6·(Selic·0.85 − IPCA) + 0.4·((IPCA + 5.5)·0.85 − IPCA)` (`cenarios.py:820`). Capital cells use the same formula (`:803`).
- The IPCA+ leg has a **fixed** real yield of 5.5% in every regime. There is no mark-to-market on fixed-rate or IPCA+ bonds, and no equity or real-estate revaluation (the page admits "sem patrimônio (bolsa, imóveis)").
- Results:
  - **Top decile by regime, 2030, Lula winner:** credible 101.05, middle 102.67, **crisis 102.83** (Selic 9.1 / 10.3 / 12.7). It is the same for Flávio.
  - In the **pro-Flávio set**, where Lula has more crises, the top decile does **better under Lula** (D = +2.59).
  - Removing the Selic → financial-income link cuts the top decile's central D from **+0.94 to +0.18**.
  - Sanduíche capital cells: the level falls by 11–26 points for both winners. This is the real Selic normalising from ~7.2% to ~5% on a ratio `ret/ret0`. D between winners reaches **+10 points** in 2029–30 (`sanduiche.celulas.s_*_capital`).
- The page text endorses the logic: "Selic alta … rende para quem tem aplicação" (`cenarios.html:357`).

**Fix.**
- Add a wealth block: Δwealth = −duration × Δyield on fixed-rate and IPCA+ bonds (duration ~4–6), plus an equity beta to the premium (Ibovespa −5 to −10% per +1 pp of premium, from 2015 and 2024).
- Report an income + revaluation measure for the top decile and the capital cells.
- Until that exists, mark the "Topo 10%" row and the capital column as **"sinal não confiável: não inclui perda de patrimônio"** (sign not reliable: excludes wealth losses) and drop the capital column from the sanduíche test.

### MAJOR

#### M1. The four assumption sets do not bracket symmetrically, and the tornado probes Flávio's assumptions more than Lula's

**Asymmetries between the sets** (`premissas.py:433-462`):

| Item | Pro-Lula set | Pro-Flávio set |
|---|---|---|
| Bolsa Família prior | Makes it **asymmetric** (L 0.6–0.95, F 0.2–0.6) | Does not touch it (no mirror) |
| F's one-off revenue share (50%, the biggest F-specific fiscal assumption) | — | Not lowered |
| L's rule-keeping intention (1.0) | — | Not lowered |
| L's directed-credit expansion | — | Not raised |
| L's fuel subsidy | — | Not raised |
| F's composition | Pushed to 50% mandatory | — |

**Effects:**
- Without the Bolsa Família override, pro-Lula D for the Bolsa Família family (rest of Brazil) falls from **+5.65 to +0.51**, and for the Northeast family from **+3.07 to +1.00**.
- Giving Flávio Lula's one-off share in the pro-Flávio set moves formal 1 SM from −0.18 to **+0.28**, which changes its sign. Lowering the one-off share means more real cuts, so more abono is cut.

**Tornado** (`rodar.py:305-328`):
- It has F-only bars: F intention, "Bolsa Família only for Lula high", F VAT, F reversal.
- It has **no L-side bars**: L composition, L one-off share, L directed credit (+1 pp/yr), L subsidy, L intention.
- It has no mirror bar "Bolsa Família only for Flávio high".

**Fix.**
- Make each pro set a mirror of the other: the same list of parameters moved by the same quantile distance.
- Drop the Bolsa Família asymmetry, or mirror it.
- Add the missing L-side and F-side items.
- Add a test that the two override lists move the same keys symmetrically.

#### M2. The income-tax correction prior is asymmetric, contradicts the model's own rule, and misreads its source

**Evidence.**
- The docstring (`premissas.py:11-12`) says the IR table correction gets **the same prior for both** "where research does not discriminate".
- The code uses L U(0.15, 0.55) and F U(0.05, 0.40) **per year** (`:236, :269`).
- The source IR25 is "P = 0.3 that the art. 6 *policy* is approved by 2027". That is a one-off probability, not a yearly one.
- The note says explicitly: "nenhum dos dois lados propôs indexar as faixas acima de R$ 7.350" (neither side proposed indexing the brackets above R$ 7,350) (`isencao_ir_incidencia.md` §3.3). It also says Guedes's PL 2.337/2021 *did* correct all brackets.
- Neither has corrected the full table since 2015.

**Effect.** Small: formal 2.5 SM moves −0.14 → −0.22, top decile +0.94 → +0.83. But it is a direct breach of the stated rule, and the page repeats it as "prior por posição declarada" (prior by stated position).

**Fix.** U(0.05, 0.4) per year for both in the central set. Keep the asymmetry only in the pro sets.

#### M3. The fiscal closure counts announced mandatory cuts both as infeasible and as delivered

**Evidence.**
- `excesso_corte = max(0, xd + vegetative − cutable) + xo_alvo` (`cenarios.py:425`). Every point of announced mandatory cuts counts as "excess" that can blow up, at 15–50% a year per pp.
- When it blows up, either the minimum-wage rule breaks or the arcabouço breaks, which adds +0.15 to P(crisis) the following year (`:398, :431-436`). Yet the mandatory cut is **still applied** to the abono (`x_obr = xo_alvo − sm_econ`, `:474`).
- Result: the side with more mandatory cuts in its composition is penalised twice, through the abono and through the rule break or crisis:
  - P(rule kept in 2030): L 0.955, F 0.773;
  - P(arcabouço broken): L 0.046, F 0.108.
- F's rule-keeping gap is 0.18 (0.955 vs 0.773). About 0.14 of it comes from intention (1.0 vs 0.85) and about 0.04 from the higher closure blow-up rate (about 9% vs 4.5% of draws).

**Fix.** A blow-up should **replace** the planned mandatory cut, either by the rule break or by the cut not happening (debt rises), not add to it.

#### M4. Multipliers labelled "fonte" deviate from their sources

**Evidence** (`premissas.py:126-131` vs the notes):

| Multiplier | Model | Source |
|---|---|---|
| Transfers | tri(0.5, **0.9**, 1.5) | MF22 central **1.5** (0.8–1.8); C30 1.78 |
| Consumption taxes | tri(0.2, **0.4**, 0.8) | MF26 **0.25** (0.1–0.4) |

The page catalogue labels both "fonte" (`PARAMETROS`, line 505). A lower benefit multiplier makes mandatory-cut adjustments less contractionary. A higher consumption-tax multiplier makes VAT and fuel tax cuts more stimulative. Both lean slightly towards F, but the magnitude is small: in the tornado, the transfer multiplier moves formal 1 SM by only 0.05.

**Fix.** Use the note values, or relabel them "calc/suposição (hiato positivo, MF25)" and explain why.

#### M5. The debt loop is under-powered, and crisis and adjustment move in one direction only

**Evidence.**
1. The implicit interest rate is `i = 0.527·Selic + 0.473·(IPCA + K)` with K fixed (`cenarios.py:601`). The risk premium never reaches the 47% of debt that is fixed-rate or IPCA+, and there is no rollover at higher yields. That understates the cost of a higher debt path for both sides, a little more for the higher-debt side (L, +2.9 pp of GDP in 2030).
2. Delivery of the adjustment falls to 0–30% in a crisis (`premissas.py:151`). Forced adjustment exists only after 2030 (`cenarios.py:409-411`). So within the mandate a crisis only ever *reduces* adjustment. That is the reverse of 2015 (Levy) and of most EM episodes, where crises force tightening.
3. Both sides have 38% P(crisis in some year by 2030), and P(crisis) drifts to 27–29% by 2034. The page should say plainly that this is a large common level assumption: stationary P(crisis) of 0.17 from `TRANSICAO`, plus debt drift.

**Fix.**
- Apply the premium to the non-Selic share with a rollover of ~20%/yr.
- Allow a forced-tightening branch in a crisis during the mandate, for example P = 0.3–0.6 of a +0.5–1 pp of GDP emergency package under any winner.

#### M6. Page framing can imply a winner, or a narrative, from noise-level differences

1. **Sanduíche text.** The bold "**O meio fica abaixo das duas pontas.**" (the middle falls below both ends) appears for Lula and not for Flávio (`cenarios.html:741`). The underlying CLT numbers in 2027–28 are: middle +1.40, up to 2 SM +1.51, 50+ SM +2.22 (L), against +1.93 / +1.29 / +2.62 (F). The boolean flips on a 0.1-point gap, while the card's own caveat says gaps under 1 point are inside the uncertainty. **Fix:** say "sim/não" only when the squeeze exceeds 1 point, otherwise "indistinguível" (indistinguishable).
2. **Sustentabilidade.** "Vantagem inicial devolvida: toda, e inverte" (initial advantage given back: all of it, and reverses; `:699`) is shown for Flávio on 5 types. There, the early lead is the FX-appreciation price effect that markets priced, not a front-loaded giveaway. The section was built to show "ganho antecipado que se reverte" (early gains that reverse), so a lay reader will read it as "Flávio's gains are fake". **Fix:** split the reversal by source, for example "efeito de câmbio que se dissipa" (exchange-rate effect that fades) vs "conta adiada" (deferred bill: one-off revenue, credit hangover), or relabel it neutrally as "diferença dos anos 1–2 vs 5–8" (difference in years 1–2 vs 5–8).
3. **Shapley text.** "A favor do cenário Lula: Ajuste fiscal, cortes e transferências (+0,88)" (in Lula's favour: fiscal adjustment, cuts and transfers) reads as a finding, but it is C1's assumption. The Shapley total (+2.05, n = 4,000) also differs from the headline (+2.21, n = 200,000) for the same quantity. Either explain it or rescale.
4. **Sanduíche "Aperto econômico" card.** It says the IR correction prior is set "por posição declarada" (by stated position), which conflicts with M2.

#### M7. Mobile layout and reading order bury the conclusion

At 390 px (Playwright, Chromium):
- **What works:** no horizontal page scroll (`scrollWidth` = 390); no JS errors once Chart.js loads.
  - In the sandbox the CDN failed TLS until I set `ignoreHTTPSErrors`. That is an environment issue, not a page bug.
  - Toggling the pro-Flávio set and moving a prior slider keeps width at 390.
- **What doesn't:**
  - The **"pode / não pode concluir" box starts at 1,963 px**, about 2.3 screens down. The **robustness forest starts at 3,799 px**, about 4.5 screens down. The changelog `<details open>` (`:229`) sits in between.
  - The page is 28,664 px long.
  - The sticky header wraps to about 155 px, roughly 18% of the viewport.
  - The events and sustainability tables need sideways scrolling, with no hint, and the "Flávio vence" column is off-screen.
  - Nothing above the fold says "todas as 10 famílias: inconclusivo" (all 10 families: inconclusive).

**Fix:**
- A one-sentence verdict line under the lead.
- Close the changelog by default and move the can/cannot box above it.
- Make the header non-sticky on narrow screens.
- On mobile, show the tables as stacked cards or add a scroll cue.

### MINOR

- **m1. Variance dominated by idiosyncratic unemployment.**
  - Var(D) for formal 1 SM is **49** (sd ≈ 7) against a mean of 2.2.
  - Sobol first-order indices sum to under 0.06 (top: Flávio's intention, 0.018). They are dominated by unemployment-status flips and are uninformative as an attribution.
  - Level bands such as "Informal: [29.7; 117.4]" are mostly the unemployment lottery (75% income loss), which a lay reader will take for macro uncertainty.
  - **Fix:** compute Sobol on E[D | policy and macro draws], averaging out the household unemployment draw, and show bands both with and without job loss.
- **m2. Unsourced constants that move results.**
  - `TOPO_POR_PP = 0.3·13.4/3.6` (`cenarios.py:87`): its units are unclear. 1 pp of GDP ≈ 5% of the top decile's income, not 1.1%.
  - The "other programmes" item is a flat R$ 100/month for every type, including the top decile (`:792`).
  - `cambio_renda` gives urban formal workers and the top decile FX-linked wage gains (exposure 0.15–0.30, `:697`), while the source M35 concerns agro and tradable microregions.
  - `achatamento_psi` and `fechamento_k`/`fechamento_sm` are all `[suposição]`.
  - Put them all in the tornado.
- **m3. Note values not used or narrowed.**
  - M14 (spillover at the Northeast median, 0.8) is unused: Northeast wage bands get the national spillover.
  - M18 (low-skill multiplier 2.5, range 1.5–4) is implemented as U(1, 2.5).
  - L's 2027 fuel subsidy, tri(0.1, 0.3, 0.6) for one year, is below the CC17 run-rate of 0.6% of GDP.
  - `diferidos` = 0 for both, with a stale comment saying the notes are unpublished (`premissas.py:183-184, 245, 278`).
- **m4. Anchor drift.** The mean 2027 IPCA across winners is 4.6 against Focus 4.31, because the full fuel realignment is added on top of Focus, which likely already prices part of it. It is common to both, so it biases levels, not D.
- **m5. Taylor and IS rules.**
  - φπ ∈ [0.6, 1.3] on the nominal deviation, so the rule is passive for about 57% of draws on impact. The long-run response φπ/(1−ρ) ≈ 1.7 is fine.
  - The IS curve uses the nominal, not the real, Selic deviation (`cenarios.py:585`).
  - The Taylor surprise term includes only last year's realised surprise and the FX pass-through, not current fuel, VAT or minimum-wage price shocks.
- **m6. "Regime, not name" gives a credible Lula the same −8% FX level as a credible Flávio.** Goldman's R$ 4.50–4.80 was quoted for the Flávio scenario. This is defensible as neutrality, but the page should state it.
- **m7. The hourly-wage index (v1 R15) is not shown.** The 6x1 and PEC 12 reach the index only through monthly income, so the leisure and hours effects are invisible.
- **m8. Tests.**
  - The mirror test and "cada canal pode favorecer qualquer um" (each channel can favour either side) prove the **code** is label-free. The second is implied by the first.
  - Neither tests **parameter** neutrality.
  - The Bolsa Família regression test compares two identical blocks.
  - **Add:**
    - a lint that every L ≠ F value in `CANDIDATOS` carries a source tag;
    - a test that the pro-Lula and pro-Flávio override lists are mirrors;
    - a test that the central set's asymmetric keys are exactly the documented list.
- **m9. Lay units.** The page uses "pontos do índice", "p.p.", "SM", "P(L > F)", "equivalente-certeza", "CRRA ρ = 1,5", Shapley and Sobol without translation. Add "≈ R$ X por mês" next to each D. For example, +2.2 points for formal 1 SM ≈ R$ 38/month in 2026 reais.

---

## 3. Parameter spot-check (27 items)

**Status key:**
- ✓ = faithful to the source.
- ≈ = within range, but with a different central value or a narrower range.
- ✗ = deviates from the source or is unsourced, and moves results.

| Parameter (model) | Model | Source | Status |
|---|---|---|---|
| Minimum wage → IPCA (M1), `SMP`·`sm_repasse_escala` | 0.031 mode (0.016–0.082) | 0.03 (0.01–0.08) | ✓ |
| Share paid by consumers (M7) | U(0.5, 1.0) | 0.75 (0.5–1.0) | ✓ |
| Price lag (M8) | U(0.4, 0.9) | 0.6 (0.4–0.9) | ✓ |
| Northeast price multiplier (M9) | U(1.0, 1.6) | 1.3 (1.0–1.6) | ✓ |
| Lighthouse effect, informal (M10) | tri(0.3, 0.5, 0.8) | 0.5 (0.3–0.8) | ✓ |
| Lighthouse effect, own-account (M11) | tri(0, 0.2, 0.4) | 0.2 (0–0.4) | ✓ |
| Spillover at 1.5 SM / 2–3 SM (M12–13) | 0.10 / 0.03 | 0.10 / 0.03 | ✓ |
| Spillover at the Northeast median (M14) | not used | 0.8 | ✗ (m3) |
| Formal employment elasticity, Brazil / Northeast (M16–17) | −0.05 / −0.15 | −0.05 / −0.15 | ✓ (sign correct) |
| Low-skill multiplier (M18) | U(1, 2.5) | 2.5 (1.5–4) | ≈, lower |
| Formal → informal (M19) | U(0, 0.5) | 0.3 (0–0.5) | ✓ |
| Cost per R$ 1 of minimum wage (M21) | R$ 413.2 mn | R$ 413.2 mn | ✓ |
| Rule (M25) | INPC + GDP(t−2), 0.6–2.5% | same | ✓ |
| Selic → debt service of indebted ≤3 SM (M36) | ~0.59% of income per pp | 0.3–0.6 | ≈ (upper edge) |
| Selic share of public debt (MF13) | 0.527 | 52.7% | ✓ |
| FX → gross debt (MF11) | 0.07 | 0.07 | ✓ |
| Selic → IPCA (E6/MF15) | tri(0.15, 0.27, 0.40) | −0.27 (−0.15 to −0.40) | ✓ (sign correct) |
| Okun (MF17) | 0.4–0.6 / 0.2–0.3 | 0.5 / 0.25 | ✓ |
| Transfer multiplier (MF22, C30) | 0.9 central | 1.5 / 1.78 | ✗ (M4) |
| Tax multiplier (MF26) | 0.4 | 0.25 | ✗ (M4) |
| Profit tax → wages (MF30) | U(0.3, 0.5) | 0.4 (0.3–0.5) | ✓ |
| Debt → premium (E8) | tri(0.03, 0.112, 0.33) | full sample 0.03; rolling median 0.112; 2025–26 at 0.33 | ✓ |
| FX pass-through: IPCA / food (E1/E2) | 0.10 / 0.25 | 0.10 / 0.26 | ✓ |
| Appreciation asymmetry (E5) | tri(0.5, 0.75, 1.0) | 0.75 | ✓ |
| FX impact shock (L1/F1) | +8% (3–15) / −7% (−14 to −4) | same | ✓ |
| Flávio keeps the minimum-wage rule (F6) | 0.85 | **0.65** | ✗ (C1) |
| 6x1 (L12/F12) | 0.5 / 0.5 | 0.55 / 0.45, equalised per R15 | ✓ |
| VAT (F9–F11) | P 0.2; −1.6 to −6.25; 1.1–4.2% of GDP | same | ✓ (pass-through 0.5 vs E12 0.75: ≈) |
| Directed-credit share → Selic (C7) | U(0.02, 0.07) | 0.04 (0.02–0.07) | ✓ |
| Household credit hangover (C22) | tri(0.15, 0.34, 0.45) | −0.34 (−0.15 to −0.45) | ✓ |
| FGTS/MCMV discount (C15) | tri(1.4, 1.9, 2.2) | 1.9 (1.6–2.0) | ≈, wider |
| Table correction (IR25) | per year: L 0.15–0.55, F 0.05–0.40 | P 0.3 *by 2027*; "neither side proposed" | ✗ (M2) |
| Reversal of top-income taxes (IR28) | P 0.3 | 0.3 (0.1–0.5) | ✓ |
| Adaptation index (IR26) | 12/9/13/21/34/60 × CLT 0.3, PJ 1.3, capital 1.5 | 12/9/13/21/34/52–68; multipliers are an assumption | ≈ |
| Kaitz index, Brazil / Northeast (M20, `kaitz_uf.csv`) | 0.705 / 1.0 | 65% / ~100% | ✓ |
| Lived-experience layer (V: shrinkflation, rent, collective health plans) | 0.1–0.5; 3–5; 3–7 | same | ✓ |

**Assumptions the builder admits, and how much they drive:**
- **Composition and abono:** about 1.2–1.4 points for formal 1 SM, which is most of its D. Critical.
- **One-off revenue share:** setting F = L moves formal 1 SM +2.17 → +3.34 and floor pensioner +0.93 → +1.23. A lower one-off share means more real cuts, so more abono. In pro-Flávio it flips formal 1 SM's sign. Major.
- **Credibility priors:** about ±0.2 points for workers in the tornado. They are large only for the top decile (0.35 ↔ 1.57), which is C2's artefact.
- **Adaptation index:** it only touches the PJ and capital sanduíche cells. Small next to C2.

---

## 4. Economics checklist (task item 4)

- **Debt / r − g / premium loop.** Sensible in direction and calibrated to the IFI (consensus gross debt 96.4% in 2030 vs IFI 95.7%). It is under-powered on the non-Selic debt, and the crisis feedback runs one way within the mandate (M5).
- **Taylor rule.** Sensible structure; the candidate enters only through the premium and expectations. φπ is passive on impact for most draws (m5).
- **Pass-through magnitudes.** Consistent with the BCB and with the minimum-wage literature (§3).
- **Lighthouse effect on informal workers.** Correct sign and magnitude. It applies only to *deviations from the rule*, which is right for D. It reaches the Bolsa Família families through their informal earnings.
- **Employment loss in high-bite Northeast regions.** Present: `eps_ne` weighted by `F_NE_PISO` = 0.41 for formal 1 SM, and in the wage bands. Like every minimum-wage effect, it applies only to deviations from the rule. No Northeast *formal* household type exists, so the Northeast bite shows up only in the wage-band chart.
- **2031–34 forced-adjustment rule.**
  - **Symmetric in code:** a common threshold, a common step and a 50/50 split between discretionary and mandatory spending.
  - **Symmetric in effect:** P = 0.545 for L vs 0.514 for F, consistent with L's slightly higher debt. Through the common abono share it then also hits formal 1 SM.
- **"Top 10% gains from a high Selic".** Not sound as modelled (C2).

---

## 5. Neutrality tests: do they test anything?

- **What they establish:** the simulation code contains no candidate label, swapping programmes mirrors the results exactly, and identical programmes give D = 0.
- **What they don't:** they say nothing about whether the **inputs** are neutral. That is where every remaining bias in this review lives: C1, M1, M2, M3.
- **What would make them meaningful:** the tests listed in m8. Also make it a hard rule that every L ≠ F entry in the central set points to a line in a note, and that `[suposição]` values are equal across candidates unless a note discriminates.

---

## 6. Overall verdict

**Fit to publish as "cenários, não previsões": yes, conditionally.**

**What already holds:**
- The page leads with the right disclaimer and labels every type "INCONCLUSIVO" prominently.
- It explains that the probabilities hold only within the assumptions.
- The engine is mechanically neutral and reproducible.

**What must be fixed or labelled first** (each is a few hours' work):
1. **C1:** common rule-keeping intention for both, abono incidence that spares 1-SM workers, and assumption tags on the Shapley bars.
2. **C2:** caveat the top decile and capital column, or add revaluation of assets.
3. **M1:** make the pro sets true mirrors and add the L-side tornado bars.
4. **M2:** the same IR prior for both.
5. **M6:** the sanduíche boolean threshold and neutral labels in the sustentabilidade table.
6. **M7:** a verdict line above the fold on mobile.

Once those are done, the central-set numbers will rest on the evidence rather than on unsourced execution assumptions. As expected, the honest summary is unchanged: four years of plausible policy differences move household purchasing power by less than the model's structural uncertainty, for every household type.
