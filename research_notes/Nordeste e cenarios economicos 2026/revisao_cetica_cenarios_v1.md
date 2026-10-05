## Review of the 2027–2030 purchasing-power scenario model (read-only)

I edited and committed nothing. I read `cenarios/cenarios.py`, `cenarios/rodar.py`, `cenarios/tests/test_cenarios.py`, the visible text of `simulador/web/cenarios.html`, the full research note, and the results in `simulador/web/cenarios.json`. To size two of the findings I ran patched copies of the model in the scratchpad (`/tmp/claude-0/.../scratchpad/c_orig.py`, `c_fix.py`, `c_lag.py`).

**Current headline results (mean index in 2030, Lula − Flávio in index points, P(L>F)):**

| Household type | L − F | P(L>F) |
|---|---|---|
| Minimum-wage worker | +1.1 | 0.51 |
| Pensioner / BPC on the floor | +1.5 | 0.54 |
| Bolsa Família family | **+7.0** | **0.98** |
| "Median" worker | −0.6 | 0.16 |
| R$ 5–10k band | −1.25 | 0.09 |
| Indebted household | −0.9 | 0.17 |

**Bottom line:** apart from the Bolsa Família gap, every difference between the candidates is smaller than the model's own structural uncertainty. The Bolsa Família gap comes from an unsourced assumption, not from any mechanism.

---

## Top 15 problems, in priority order

Notation: "favours L" means the flaw pushes the L − F difference up for that household type; "favours F" pushes it down.

### 1. The Bolsa Família gap comes entirely from one assumption
- **What the model does now.** It applies past INPC plus a real raise (`cenarios.py:546`). The raise is L tri(0, 1, 3) and F tri(−2, 0, 1) (`:156`, `:174`). The family's income is the benefit alone (`:589`).
- **What drives the result.** The decomposition gives +6.83 of the +6.96 points to the "bolsa" group. In my scratch run, giving both candidates F's distribution shrinks the gap to **+0.11**.
- **Why it's wrong.**
  - Bolsa Família has no automatic indexation, so "INPC + real" is the wrong baseline for both candidates. To my knowledge the R$ 600 floor stayed nominal from 2023; please verify.
  - Real families mix informal earnings with the benefit.
  - A higher minimum wage can push families over the means test (the regra de proteção softens this).
  - The raises have a fiscal cost (Bolsa Família ≈ 1.2% of GDP), but none of it reaches the primary balance.
- **Bias.** Favours L for the Bolsa Família family by about 7 points, with a false 98% confidence.
- **Fix.**
  - Nominal benefit: B_t = B_{t−1}·(1 + J_t·a_t), where J_t ~ Bernoulli(p_adj,c) is a discrete readjustment and a_t is its size. Use p_adj in 0.3–0.9 for both candidates, from the track record.
  - Add 1.2% of GDP × cumulative real change to the primary balance.
  - Family income = informal labour + benefit; see item 8.
- **Data.** MDS benefit history 2019–2026 (VIS Data), PNADC income by source, Cadastro Único.

### 2. Minimum-wage rule bug, and the minimum wage treated as pure income
**The bug** (`cenarios.py:537`). `pibs[-1]` is GDP of t−1, but the rule uses t−2 (`pibs` starts as `[pib26]` and is appended after each year). In my scratch run, fixing only the lag moves L − F from +1.12 to **+1.82** for the minimum-wage worker and from +1.45 to **+2.16** for the pensioner. The rule also probably has a 0.6% real floor (Lei 15.077/2024, within the arcabouço band); verify, then use `clip(…, 0.6, 2.5)`.

**The mechanics** (`:536-546`, `:587-588`). A real minimum-wage gain becomes a 1:1 gain in purchasing power. E9 (employment) appears in the notes' table 7.3 but is never used. The model has:
- no price pass-through to minimum-wage-intensive services;
- no employment or informality response;
- no lighthouse effect (efeito farol) on informal wages;
- no spillover or compression up to about 2 minimum wages;
- no fiscal crowding under the arcabouço spending cap.

**Bias.** Favours L for the minimum-wage worker, especially in high-bite regions such as the Northeast. Favours F for informal workers, who are missing as a type and would gain from the lighthouse effect. It also misses that the cost squeezes discretionary spending.

**Fix.**
- Prices: π_j += s_L,j · b_j · g_MW, where b_j is the share of sector j's wage bill at or near the minimum wage. Calibrate the total to about 0.02–0.08 pp of IPCA per 1% real minimum wage (a suposição to check against BCB boxes).
- Spillover: g_w(m) = g_MW·max(0, 1 − (m−1)/(m*−1)), with m (wage in multiples of the minimum) up to m* ∈ [1.5, 2.5].
- Lighthouse: g_inf = λ·g_MW, with λ ∈ [0.2, 0.6].
- Formal employment: Δln E_r = ε·Kaitz_r/Kaitz_BR·g_MW, with ε ∈ [−0.1, 0].
- Fiscal: R$ 0.38–0.455 bn per R$ 1, net of 30–40% that returns as revenue. Under the cap this squeezes discretionary spending; see item 4.

**Data.** RAIS/CAGED (bite by sector and region), PNADC (Kaitz index by region, informal wage distribution), Engbom & Moser, Ipea TD 849.

### 3. The fiscal feedback loop is switched off by design
- **What the model does now.** The risk premium reacts only to debt surprises against the candidate's own expected path (`:485-487`, `rodar_cenario` `:609-617`).
- **Consequence.** The median 2030 debt gap (L 93.6% vs F 89.4% of GDP, 4.2 pp) produces **zero** premium. Any policy cost that is drawn with certainty never moves interest rates or the exchange rate. The decomposition swaps also re-estimate the expected path, so the fiscal channel of each group is netted out. In the non-persist state, L's exchange rate converges to consensus despite the higher debt.
- **Second gap.** GDP reacts only to "ajuste" (`:530`). Minimum-wage savings, the VAT cut, fuel subsidies and Bolsa Família changes reach the primary balance but have no demand effect.
- **Bias.** Favours L in rates and exchange rate for all types (debt path unpriced). Favours F on GDP and unemployment (its transfer cuts and tax cuts have no demand effect).
- **Fix.**
  - Back out the debt gap the market already prices from the bank shocks: Δd* ≈ ln(1+shock)/(λ_x·e8).
  - Price only the deviation from that: premium = e8·(d − d_cons − Δd*_cand).
  - Report the "market prices everything" and "market prices the path" variants side by side.
  - GDP: Δy = −Σ_k m_k·Δf_k, with multipliers m: transfers to the poor 0.8–1.5, investment 0.5–1.5, discretionary spending 0.3–0.8, consumption-tax cut 0.3–0.8, tax on high incomes or dividends 0.1–0.4.
- **Data.** IFI RAF (premium regressions), Tesouro debt projection report, multiplier literature (Ipea Comunicado 75 is contested, so use wide ranges).

### 4. Fiscal adjustment with no composition or incidence
- **What the model does now.** "ajuste" is one scalar (`:153`, `:170`, `:423-424`, `:557`). F's 1.5 pp of GDP in 18 months (about R$ 200 bn) coexists with p = 0.65 of keeping the minimum-wage rule, untouched pensions and flat Bolsa Família. The notes say this "não fecha sem despesa obrigatória" (doesn't close without cutting mandatory spending). Yet the minimum-wage rule is drawn independently of the adjustment size.
- **Lula's side.** Revenue measures fall on top incomes, and no household type carries them.
- **Bias.** Favours F for the poor types (cuts are invisible). Favours L for high incomes (no top-income type).
- **Fix.**
  - Split the adjustment by instrument: a = A·w_c, with a Dirichlet draw of w_c over: revenue from top incomes and tax expenditures; discretionary spending; mandatory spending (de-indexation, BPC, abono, health and education floors); privatisation (debt stock only).
  - Add an incidence matrix I[k, h]. For example, an abono salarial cut costs a minimum-wage worker about 1/12 of a year's income. Health and education cuts reduce in-kind income valued at cost.
  - Closing rule: if the cap minus mandatory spending falls below a floor for discretionary spending (shutdown risk), then either the minimum-wage rule drops (raise P(regra_sm drop) with the gap) or the rule breaks (premium jump).
- **Data.** PLOA 2027, Tesouro "Resultado do Tesouro", IFI scenarios, Silveira-type in-kind incidence, POF.

### 5. The credibility regime has truncated tails, and the Selic mapping is asymmetric and unsourced
- **What the model does now.**
  - Two states only (`:418-447`).
  - Selic draws are L tri(11, 12.5, 15.5) and F tri(9.75, 11, 12.5). They assign Morgan Stanley's unconditional scenarios to candidates, labelled "suposição de mapeamento".
  - Neither candidate has a state worse than the initial shock. F has no failure mode, such as cutting taxes before adjusting (Inhasz; Macri in 2018). L's fiscal-dominance tail is capped.
  - Exchange-rate noise has a 7% standard deviation, against about 15% realised volatility for the real.
  - The persistence probability range in the tornado (0.3–0.7) is too narrow.
- **Bias.** Favours F in the tails. Understates L's downside too. The "credibilidade" group drives −0.95 points for the median worker.
- **Fix.**
  - A 3-state Markov regime per candidate: credible, muddle-through, crisis. Each state has its own exchange-rate level, premium and Selic, and a yearly transition matrix.
  - Crisis probability of 0.05–0.25 for both. For F it rises if the VAT or fuel cuts come before the adjustment. For L it rises with the primary gap.
  - Derive the Selic from a rule (item 14), not a per-candidate draw.
- **Data.** Brazil 2002, 2015 and 2024 episodes; Argentina 2018; bank scenarios; option-implied FX volatility.

### 6. The exchange rate affects households only through consumer prices
- **What the model does now.** The shock reaches prices only (`:437-447`, `:478-522`). Appreciation has no cost for agro, mining or export-manufacturing jobs and income, or for tourism, and there is no income loss from commodity prices measured in reais.
- **Second issue.** The Selic effect is spread equally over food, administered prices and services (`:507`, `:519-522`), but administered prices and food barely respond within a year.
- **Bias.** Favours F for workers in exporting regions (Midwest, South, western Bahia). For the urban Northeast poor, the price side dominates, so the direction is roughly right.
- **Fix.**
  - Sector income: Δln y_j = η_j·Δln FX, with η_agro ∈ [0.2, 0.6] and η_export-manufacturing ∈ [0.1, 0.3].
  - Selic loadings by component: (A, G, S, R) = (0.5, 0, 1.3, 1.1), normalised so that the IPCA elasticity stays at E6.
- **Data.** IBGE input-output tables (TRU), CEPEA agro GDP, Secex exports by state, BCB pass-through by group.

### 7. Interest-rate incidence is too crude
- **What the model does now** (`:583-592`, `:134-136`).
  - Fixed 30% and 15% debt-service shares; κ of 0.1–0.3 pp of income per Selic pp, with no source.
  - No split by credit line: consignado is fixed-rate, mortgages are TR-indexed, revolving credit and overdraft barely track the Selic.
  - No interest income for savers: the R$ 5–10k band and the top hold CDBs and poupança. A low-income type paying about 400% a year on revolving credit is unaffected by the Selic.
- **Bias.** Overstates the harm of a high Selic for the R$ 5–10k band (favours F). May understate it for heavily indebted households (favours L).
- **Fix.**
  - Δservice_h = (D/Y)_h · Σ_l w_h,l · pass_l · repr_l(t) · ΔSelic, using E7 by line (1.73 personal, 4.43 overdraft, 0.75 vehicle, 0.43 mortgage) and repricing of about 40–60% per year.
  - Financial income: Δy_h = (A/Y)_h · s_post-fixed · ΔSelic · (1 − tax).
- **Data.** BCB SCR and REF by income band, SGS 29034 regressed on the Selic, POF financial assets.

### 8. The household types are wrong or incomplete
- **"Mediano" is mislabelled.** R$ 3,777 is the PNADC **mean** habitual income ("rendimento médio") of all workers, informal included; the median is much lower. The model applies CLT INSS and income tax to it (`:43`, `:199`). C11/C12 is mean income per worker, which carries composition effects.
- **Missing types:**
  - informal worker (37.5% of employment);
  - pensioner above the floor (INPC only, no minimum-wage gain);
  - top decile and asset holders (Ibovespa +11% to +41% under F; affected by L's dividend tax);
  - households rather than individuals;
  - Northeast vs Southeast;
  - a pensioner price basket (IPCA-3i-like, heavier on health).
- **Bias.** The model can't show who loses under each candidate: informal workers and above-floor pensioners under L's priorities, top incomes under L's financing, the poor under F's cuts.
- **Fix.** About 10 household types defined on PNADC: region × decile × formal/informal/pensioner/Bolsa Família, with POF baskets by decile and region.

### 9. The unemployment effect is an expected-value scalar that is the same for everyone
- **What the model does now.** fu = 1 − 0.5·(u − 5.3)/100 for every worker type (`:575`). The 0.5 replacement rate is fixed. The trend in Okun's law is hard-coded at 2.0 (`:534`).
- **What it misses.** Low-wage, young, Northeast and informal workers are 1.5–2× more cyclical. Job loss is a binary, fat-tailed event, and the poverty-risk tail is never shown.
- **Bias.** Understates the cost of slowdowns for the poor in both scenarios: L's higher Selic, and F's 2027 front-loading (median GDP 2027: F 1.17 vs L 1.47).
- **Fix.**
  - u_h = u_0h + β_h·(u − u_0), with β_low ∈ [1.5, 2], β_high ∈ [0.4, 0.7].
  - Income loss = Δu_h·(1 − rr_h·dur_h/12), with rr = 0 for informal workers.
  - Report P(below the poverty line).
- **Data.** PNADC flows by group, seguro-desemprego rules.

### 10. Income-tax brackets frozen for four years
- **What the model does now.** It freezes both the IR table and the Lei 15.270 thresholds (R$ 5,000 / R$ 7,350) in nominal terms (`:256-298`, `:573-582`, M8).
- **Effect.** The R$ 5–10k type (R$ 6,500 rising to about R$ 8,000 nominal by 2030) falls out of the partial-exemption zone in both scenarios, which is why its index sits at about 99–100. The higher-inflation scenario (L, cumulative IPCA 17.3% vs 16.3%) gets more bracket creep. The table was corrected in 2023, 2024 and 2025, plus the 2026 exemption, so a freeze is a policy choice in its own right.
- **Bias.** A slight bias against L for the median and R$ 5–10k types, and a downward bias in levels for both.
- **Fix.** A yearly correction event with candidate-specific probability (wide: 0.3–0.8 for both). Correct thresholds by realised INPC, and put the cost in the primary balance.

### 11. The VAT cut
- **What the model does now** (`:113-118`, `:398-402`, `:515-522`, `:554`).
  - A uniform price cut on services and other goods only from 2029. The CBS is fully in force from 2027, so a cut could start earlier.
  - Food gets a U(−0.5, 1) fraction of the cut.
  - The cost reaches the risk premium only as a surprise. No demand effect.
  - No modelling of cashback for Cadastro Único households or of zero-rating of the cesta básica nacional.
  - No financing closure (up to 4.2% of GDP when fully phased in).
- **Bias.** Small in the current results (−0.09 points). Its sign for the poor is ambiguous, but it is presented as a price gain.
- **Fix.**
  - Model tax wedges by good (standard, reduced 60%, zero rate, per LC 214/2025).
  - Two routes to 20%: a uniform cut, or removing the reductions.
  - Distribute through POF shares, and require financing (debt, other taxes or cuts, each with its incidence).
  - On the page, say plainly that the effect is negligible before 2030.

### 12. Fuel pricing and who pays for it
- **What the model does now** (`:160-179`, `:509-513`, `:71-78`).
  - The gasoline tax cut is applied to every basket's fuel component using the IPCA gasoline share. For Bolsa Família families that component is mostly bottled gas (LPG), so the cut is over-credited to the poor.
  - Diesel (102% below import parity; about R$ 7 bn a month of subsidy, or about 0.6% of GDP annualised) is missing, along with its pass-through to freight, food and bus fares (bus fares weigh 2.2% in the INPC).
  - L's 2027 cost of 0.05–0.30% of GDP looks low against the current run-rate.
  - The fuel shock is one-off, with no path for Brent.
- **Bias.** Favours F for Bolsa Família families. Understates L's subsidy cost (favours L on fiscal).
- **Fix.**
  - Separate gasoline, diesel, LPG, electricity and bus fares.
  - Diesel → food through the freight share in the input-output table.
  - Cost = subsidy per litre × volume.
  - Candidate pricing rules over a stochastic path for Brent.
- **Data.** ANP volumes, Abicom, IBGE input-output tables, POF fuel shares by decile (gasoline rises with income).

### 13. Partial wage indexation makes inflation losses permanent
- **What the model does now** (`:548-550`). Wage growth recovers only θ1 + θ2(1 − θ1) of an inflation surprise, typically about 0.6–0.7. The rest is lost for good.
- **Why it's wrong.** Over four years, real wages are set by productivity and labour-market tightness. The legitimate permanent part is the real-exchange-rate effect on tradables, which item 6 handles.
- **Bias.** Penalises the higher-inflation scenario (L) for wage earners.
- **Fix.** Error correction: g_w = π^e + θ1·surprise + κ·(w*_t − w_{t−1}), with w* = productivity + φ·(u* − u) and κ ∈ [0.3, 0.7].

### 14. Double counting, and correlated events treated as independent
- **The Selic is counted three times.** The 2027 Selic per candidate (which already includes the market's FX and inflation expectation) is followed by a Taylor reaction to the FX-driven surprise (`:492`) and by persistence ρ. On top, premium → FX and premium → Selic are applied, though the bank FX shock already contains the premium.
- **Events are treated as independent.** The page's re-weighting (`rodar.py:103-108`) allows incoherent combinations, such as a big adjustment plus the minimum-wage rule kept, the VAT cut and a low Selic.
- **The elasticities E1, E2 and E3 are comonotonic** (`:384`), an untested assumption.
- **Bias.** Likely favours F through a double Selic penalty on L.
- **Fix.**
  - Selic from a rule: i = r* + π^e + 1.5(π − π*) + 0.5·gap + premium. The candidate enters only through the premium and expectations.
  - The Taylor term acts only on unexpected inflation.
  - Use a Gaussian copula over the events (correlation of about 0.5 between adjustment size and dropping the minimum-wage rule).

### 15. Labour-law changes: PEC 12 hourly contracts and the end of the 6x1 schedule
- **PEC 12** (`:576-577`). It is modelled as mean-preserving noise, so its mean effect is zero by construction. Fix:
  - a share s ∈ [0.02, 0.10] of low-wage formal workers moves to hourly contracts, with hours drawn from Beta(mean 0.6–0.9);
  - a share f ∈ [0, 0.05] of informal workers formalises (gains INSS, FGTS and income);
  - report the certainty equivalent, CE = (E[y^(1−ρ)])^(1/(1−ρ)) with ρ ∈ [1, 2], so the variance is priced.
- **6x1** (`:518`, `:529`).
  - Its probability depends on the winner (0.55 vs 0.45) although the Senate votes before the inauguration.
  - The roughly 10% rise in hourly wages and the extra leisure are not shown.
  - Informalisation is missing.
  - Fix: make the probability the same for both candidates, and show an hourly-wage index next to the monthly one.
- **Bias.** Small now (−0.03 points). The direction is ambiguous.

### Also missing (lower priority)
- **Privatisations.** Not modelled. Treat proceeds as a reduction in the debt stock with no primary-balance effect. Markets weight structural measures more (Citi). Tariff effects are ambiguous, so show them only as a range.
- **Income-tax-exemption financing (L).** The dividend withholding and minimum tax have no household type to fall on, and no behavioural response (dividend timing).

---

## Internal-consistency checklist

- **Same world in both scenarios: yes.** Common random numbers are implemented correctly, and the neutrality test (`tests:43-50`) holds. The model is mechanically neutral, but the parameter choices are not neutral in their consequences (items 1, 5, 14).
- **Consensus anchor.** It assumes the Focus survey is a 50/50 average of the two scenarios. If markets priced about 60% F, L's deviations should be larger and F's smaller, so that p·L + (1−p)·F = consensus. The anchor test's 0.6 pp tolerance (`tests:68-72`) is loose.
- **Nominal vs real.** Deflation is correct. The problems are the bracket freeze (item 10), the assumed automatic Bolsa Família indexation (item 1), and minimum-wage cost per R$ held fixed in nominal terms.
- **Price weights.** Services at 0.35 is used for all baskets (`:71-75`, a suposição). The Bolsa Família basket (A 0.30) is a guess. Pensioners use the INPC.
- **Unemployment.** See item 9. Bolsa Família and pensioner types have no labour-market exposure at all.
- **Regions.** None, although the research folder is about the Northeast. The Northeast has a higher minimum-wage bite, about half of Bolsa Família families, informality above 50%, a higher food share, lower credit exposure, and municipal payrolls tied to the minimum wage.
- **Horizon and lags.** An annual model ending in 2030 truncates the long-run effects of both programmes (debt sustainability for L; reform productivity and social investment for both). The 2027 minimum wage is fixed by the budget bill (PLOA). The VAT starts in 2029. Lagged responses mostly fall after 2028.
- **[suposição] ranges are too narrow** for:
  - persistence probability (0.3–0.7; should be about 0.1–0.9);
  - F keeping the minimum-wage rule (0.4–0.9);
  - Bolsa Família raises;
  - κ;
  - exchange-rate noise (7%);
  - fixed values for acoplamento 0.5, selic_taylor 0.5, reposicao 0.5 and PESOS.
  
  The one-at-a-time tornado misses interactions. Use Sobol indices, or named "assumption sets" (pro-L reading, pro-F reading, neutral).
- **Decomposition** (`rodar.py:261-274`). Swaps re-estimate the expected debt path, which removes the fiscal channel of each group (item 3).

---

## What a credible model of this kind can and cannot conclude

**It can:**
- Show conditional arithmetic: "if the real ends 10% weaker, food inflation is about 2.5–3 pp higher in 12 months"; "each 1 pp of real minimum-wage gain is worth X to floor pensioners and costs Y of GDP".
- Rank which channels matter for which households: exchange rate and food for the poor's prices; the minimum wage for the 1-minimum-wage worker and floor pensioners; Bolsa Família rules for transfer families; the Selic for indebted households.
- Show that external shocks (food premium SD 5.1 pp a year, Brent) dominate the spread of outcomes for each winner.
- State which of its conclusions hang on unsourced assumptions.

**It cannot:**
- Say which winner leaves a given household better off with a stated probability. P(L>F) is internal to the model and conditional on the assumptions; structural uncertainty is not sampled.
- Distinguish differences of 1–2 index points over four years from zero.
- Forecast regime outcomes. Execution is the dominant uncertainty, and it is a political judgement.
- Capture welfare beyond purchasing power: leisure, risk, in-kind public services, long-run growth.

**What the page should do:**
- Show the "is this outcome robust across assumption sets?" view first.
- Replace "P(L>F) = 0.98" with "under these assumptions".
- Flag the Bolsa Família gap as assumption-driven.

---

## Proposed v2 architecture (numpy, vectorised, roughly 4–6 hours)

1. **`regime.py`**: a 3-state Markov chain per candidate (credible / muddle / crisis) with a yearly transition matrix. Each state sets the premium level and the probability of the exchange-rate and inflation-expectation shock. Event copula over: minimum-wage rule, Bolsa Família readjustment, VAT, PEC 12, IR correction, adjustment size.

2. **Macro core** (annual, with semiannual optional):
   - Output gap: gap_t = ρ·gap_{t−1} − β(r − r*) − Σ m_k·Δf_k + ε.
   - Unemployment: Okun's law plus a group-specific β_h.
   - Selic: Taylor rule plus premium.
   - Exchange rate: ln FX = consensus + premium/λ + regime level + noise (SD 12–15%).
   - Debt: accumulation as now, plus privatisation as a stock adjustment.

3. **Sectors (5):** agro/food; tradable industry; commerce and personal services (high minimum-wage bite); other services; administered prices (fuel, energy, transport split out).
   - Price equation: π_j = π^e + a_j·gap + ε_j·Δln FX + s_L,j·(g_wage,j − prod) + Δτ_j + admin_j.
   - Sector incomes respond to the exchange rate through η_j.

4. **Wage distribution:** 20 quantile bins × 2 regions (Northeast vs Southeast/South/Midwest) × formal/informal, from PNADC.
   - Minimum-wage spillover function, lighthouse effect for informal workers, employment elasticity scaled by regional Kaitz index.
   - Error-correcting real wages.

5. **Fiscal block:** a list of measures, each with a cost path (% of GDP), a multiplier and an incidence vector over household types:
   - minimum-wage rule and RGPS/BPC indexation;
   - Bolsa Família;
   - abono salarial;
   - IR exemption, compensation and table correction;
   - VAT (two routes);
   - fuel taxes and subsidies (diesel, gasoline, LPG);
   - discretionary cuts, health/education floors, privatisation.

   An arcabouço spending cap with a discretionary floor leads either to a rule break (premium jump) or to dropping the minimum-wage rule.

6. **Household block:** about 10 types:
   - Northeast/Southeast × {informal + Bolsa Família, 1-minimum-wage formal, floor pensioner, above-floor pensioner, median formal, R$ 5–10k, top decile with assets, indebted}.
   - Income components: formal labour, informal labour, pension, BPC, Bolsa Família, financial income, debt service by credit line, INSS and IR.
   - POF 2017–18 baskets by decile and region, with about 9 groups (food at home, food away, housing/energy, fuel, public transport, health, education, other goods, other services).
   - Output: real disposable income / basket Laspeyres index, certainty equivalent, and P(poverty).

7. **Outputs:**
   - Distribution and paired difference by household type.
   - Shapley decomposition over channels (with 7 groups, 2^7 runs at n = 10k is fine).
   - Sobol or assumption-set robustness table.
   - Results by regime.

**Data:** POF 2017–18 (SIDRA, by decile and region), PNADC (wage distribution, informality, cyclicality), RAIS/CAGED (minimum-wage bite by sector and region), IBGE input-output tables 2019, BCB SCR/REF (debt by income band) and SGS, Tesouro/PLOA (RGPS, BPC, Bolsa Família, abono costs), regional IPCA weights and IPCA-3i, ANP fuel volumes, Secex exports by state, IFI premium estimates.
