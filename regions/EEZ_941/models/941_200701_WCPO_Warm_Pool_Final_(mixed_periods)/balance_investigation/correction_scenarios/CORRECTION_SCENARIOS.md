# Experimental juvenile-tuna corrections — not adopted

The unmodified model already returns numerical PPR, but all three diagnoses are FAIL. Five isolated sensitivity scenarios remove the two large juvenile inconsistencies: every scenario returns WARN for GE, TE and With Egestion, and OK for the primary-production budget check. None makes the entire model exactly mass-balanced. No canonical/source file, selection, regional workbook or central workbook was changed.

## Most interpretable accounting hypothesis: D, preserve other mortality

Keep biomass, Q/B, diet, catch and the original other-mortality flow M0 unchanged. For each juvenile set Pnew = predation + catch + M0old, PBnew = Pnew/B, and EEnew = (predation + catch)/Pnew. Biomass accumulation remains the published zero. This closes the missing production with higher turnover without also inventing extra other mortality. It is an artificial independent-group sensitivity, not a recovered native model.

| Group | Published P/B | Experimental P/B | Change | Published EE | Experimental EE | New P/Q |
|---|---:|---:|---:|---:|---:|---:|
| Small BET | 0.834 | 1.412971356 | +69.42% | 0.644 | 0.789872598 | 0.05401 |
| Small YFT | 1.983 | 2.530497281 | +27.61% | 0.849 | 0.881670294 | 0.07451 |

P/Q remains below the available assimilated fraction (0.8), with positive juvenile respiration and no negative respiration anywhere. Direct Q = P + egestion + respiration still closes. The original other-mortality flows are 0.00071553864 and 0.0038327424 tons/km²/year. Seven pre-existing negative biomass-accumulation estimates in other groups remain loader completions, not published evidence. No new negative accumulation occurs in D.

D is close to simply adding fishing mortality catch/B to the printed P/B (1.413875519 for Small BET and 2.527765625 for Small YFT). This supports an omitted-fishing-turnover hypothesis as an interpretation worth investigating; it does not demonstrate that this is what happened in the original source.

The paper used multistanza tuna groups. The official [EwE input guide](https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/) identifies stanza P/B as total mortality Z and jointly derives non-leading stanza biomass and Q/B under age-structure assumptions. Holding B and Q/B fixed while editing P/B therefore does not establish native stanza consistency. Neither these values nor their biological plausibility can be validated without the native model or independently justified turnover estimates.

## Alternatives tested

| Scenario | Small BET P/B; EE | Small YFT P/B; EE | Assumption |
|---|---|---|---|
| D_fixed_M0 | 1.412971356; 0.789872598 | 2.530497281; 0.881670294 | Preserve original M0; increase production and recompute EE. |
| A_fixed_EE | 1.733023845; 0.644000000 | 2.627873123; 0.849000000 | Preserve printed EE: also increases M0 by 107.80% / 32.52%. |
| B_EE095 | 1.174807744; 0.950000000 | 2.348488717; 0.950000000 | Set both EE to an arbitrary 0.95: lower required production, much lower other mortality. |
| B_EE1_boundary | 1.116067356; 1.000000000 | 2.231064281; 1.000000000 | EE=1 lower bound: zero other mortality; mathematical boundary, not a preferred ecological case. |
| C_negative_BA | 0.834000000; 0.644000000 | 1.983000000; 0.849000000 | Keep PB/EE but fund catches through biomass decline; contradicts printed zero BA. |

Scenario C requires BA = -0.00139532096877 / -0.00700796519829 tons/km²/year: declines of 57.90% / 54.75% of standing biomass per year. Its catch footprints stay exactly at baseline because this closes the budget with a negative stock-change term. It is a contrast case, not a reasonable steady-state correction. EE-only edits cannot suffice: at original production the required EE is 1.33821 / 1.12510, above 1.

## Direct diagnostic comparison

All calls use the same frozen engine and original loader settings, all source groups, short=False and flat=False; return_sppr=True additionally retains the coefficients. There are no global, Monte Carlo or regional annual-PPR runs. Total source catch remains 0.0540203 tons/km²/year. Footprints below are source-model catch primary-production equivalents in tons/km²/year; they are not annual EEZ totals.

| Scenario | Method | Overall | PP budget gap | Catch footprint | Change vs baseline |
|---|---|---|---:|---:|---:|
| baseline | GE | FAIL | 19.223340% | 695.357922 | +0.000% |
| baseline | TE | FAIL | 10.852621% | 1114.780553 | +0.000% |
| baseline | With Egestion | FAIL | 4.393139% | 172.498147 | +0.000% |
| A_fixed_EE | GE | WARN | 0.097954% | 553.386188 | -20.417% |
| A_fixed_EE | TE | WARN | 0.134701% | 1000.813711 | -10.223% |
| A_fixed_EE | With Egestion | WARN | 0.024429% | 149.737657 | -13.195% |
| B_EE095 | GE | WARN | 0.097931% | 571.489106 | -17.814% |
| B_EE095 | TE | WARN | 0.134701% | 1000.814652 | -10.223% |
| B_EE095 | With Egestion | WARN | 0.024728% | 156.071272 | -9.523% |
| B_EE1_boundary | GE | WARN | 0.098109% | 578.217297 | -16.846% |
| B_EE1_boundary | TE | WARN | 0.134701% | 1000.814967 | -10.223% |
| B_EE1_boundary | With Egestion | WARN | 0.024878% | 158.478072 | -8.128% |
| C_negative_BA | GE | WARN | 0.113859% | 695.357922 | +0.000% |
| C_negative_BA | TE | WARN | 0.147356% | 1114.780553 | +0.000% |
| C_negative_BA | With Egestion | WARN | 0.026216% | 172.498147 | +0.000% |
| D_fixed_M0 | GE | WARN | 0.097858% | 560.259005 | -19.429% |
| D_fixed_M0 | TE | WARN | 0.134701% | 1000.814097 | -10.223% |
| D_fixed_M0 | With Egestion | WARN | 0.024524% | 152.119420 | -11.814% |

Every experimental PP budget is OK and every solver converges with zero negative SPPR sources. Overall WARN remains because the maximum production residual is 0.727940% (adult BET), compared with 69.421026% at baseline. Diagnostic consumption residual falls from 2.213278% to 0.046103%. Remaining residuals also occur in adult YFT, SKJ, Small SKJ and baby SKJ. These unchanged discrepancies are consistent with source precision/input mismatches; they were not repaired. Exact is_model_balanced remains false.

TE retains its original warning that mortality-derived SPPR is written off, and its spectral-radius proximity warning. With Egestion retains a detritus-recycling proximity warning. These method warnings are separate from the removed juvenile imbalance.

| Method | Small BET baseline → D SPPR | Small YFT baseline → D SPPR |
|---|---:|---:|
| GE | 37948.659136 → 18742.832270 | 22740.285445 → 16179.501241 |
| TE | 27951.867568 → 12113.146275 | 11668.570791 → 8805.134342 |
| With Egestion | 8035.856375 → 4343.886779 | 5323.929613 → 4068.481875 |

## Published versus computational diet

Source values were never normalized or overwritten. The existing computational loader normalizes rounded diet rows. Formula results using the raw published diet are separately retained in RESULTS.json. For D, raw-diet P/B and EE would be 1.412986407 / 0.789874836 (Small BET) and 2.531160175 / 0.881701283 (Small YFT). The runs above use the normalized computational predation, so the intended juvenile equation closes under the actual engine.

Each scenario folder contains an isolated engine-compatible input, full raw diagnose_GE.json / diagnose_TE.json / diagnose_With_Egestion.json, SPPR matrices, loaded groups and per-group flow audit. RESULTS.json includes all coefficient comparisons and exact alternative formula targets. PROVENANCE.json records settings, code hashes and the unchanged canonical hash. The baseline raw diagnoses were verified equal to the prior diagnoses after JSON key serialization. artifact_manifest.json covers the final outputs. No scenario was adopted.
