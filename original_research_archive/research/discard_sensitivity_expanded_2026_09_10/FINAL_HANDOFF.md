# Verified expansion handoff

Exactly 20 additional source-valid existing marine Ecopath JSONs, representing 18 named ecosystems, have been evaluated at all 27 solved fractions. The four original references are separate and use the same dense grid. Okhotsk remains a zero-harvest null control. All writes stayed in this research namespace; no Git/index/branch operation, production export, NPP edit or shared-engine mutation was performed.

## Verification

- 62,784 final scenario records and 999,500 group-coefficient rows.
- All eight required methods and applicable all/inner/PP scopes are retained. SC/SM/SE use every grid point; unsupported added-model SR and chain source scopes stay unavailable. The 52,320 added-model records contain 25,621 valid, 26,120 unavailable, 531 failed method-conservation checks and 48 other invalid cases; nothing is replaced with zero. Detailed support is in method_scenario_coverage.csv.
- 304,690 independent output checks, zero failures; 34 focused tests pass.
- All 3,936 overlapping original records match coefficients, PPR and validity masks.
- 551 baseline comparisons: 486 strict matches, 16 unavailable, 49 strict saved-workbook differences. All 49 reproduce under raw-diet replay. The experiment preserves normalized diets within the recorded source-rounding tolerance.
- Actual in-app browser checks cover controls, dense fractions, original versus added models, source scopes, retained landings, invalid methods, source-compatible PP ratios, aggregate support, screening/hashes and screenshots. Browser-displayed values match the numerical CSV. The same embedded JavaScript passes nine runtime/export cases and full compact-JSON equality.
- CSV/JSON Save file links completed the browser's supported downloadMedia action without error; the API returns no destination path. The initial native-download-event probe timed out, so persistent explicit save links were added and verified. Export lengths and contents match the independently checked numerical payloads.

## Main findings

At 20% SM discard on the same original H, the new_GE median coefficient increase is +0.9628% (20/20; range +0.0001% to +20.9640%). With egestion it is +0.2522% (20/20); TE_EEfix is +24.9853% (18/20), and Ulanowicz_TE is +18.8469% (20/20). The retained-landings GE median is -19.2298%, showing why coefficient and numerator effects must remain separate. Prince William Sound's TEmean case has +68.6679% coefficients and +34.9343% retained-landings PPR at 20% discard.

The fixed standard is above new_GE in 5 of 20 cases and below it in 15 at 20% SM. Against WithEgestion, signs split 12 above and 8 below. There is no universal standard overestimation. SC is invariant; SC and SE agree below the zero-catch endpoint. There are no validity transitions inside the 0–20% grid. The largest low-range second difference is 0.180611 response percentage points near 19% for Prince William Sound / TEmean; no unsolved point is presented as solved.

At 100%, method support can fall sharply: GE and WithEgestion retain 17/20, TE_EEfix 4/20, and Ulanowicz 14/20 for SM/all-source paired changes. SPPR_1986 is undefined at zero catch; TEmean uses biomass weights. Some finite flow-method endpoint coefficients are extremely large and sensitive to source rounding as remaining removal approaches zero. They are stress diagnostics, not robust ecological forecasts. Invalid cases remain missing.

## Source and inference limits

All 252 corpus files are inventoried; 20 qualify after the first 52 queued candidates. The original ordering was fixed before sensitivity results. A documented source-fidelity amendment, following input review of provisional runs, replaced Santa Pola Bay (marine fish farm), Western Channel, Moreton Bay and Western Bering Sea. The first two erase nonzero documented onward routes; the latter two need unobserved detritus stock draw. Their completed exploratory results remain in results/excluded_provisional_models and enter no valid aggregates. All four replacements follow the unchanged candidate queue.

Nineteen final models change zero DET fate rows to identity, a disclosed representation change with zero DET M0/egestion; one is unchanged. No nonzero documented detritus onward fate is overwritten in the final cohort. Dependent detritus accumulation remains the original accounting convention, not an observed dynamics claim. Central and North Atlantic each have two dependent time observations. Native currency is WetWeight; unknown mass/area/time normalization stays unknown, and absolute native totals are not pooled. Scenario spread is a sensitivity range, not a confidence interval or global model-validity estimate.

## Artifacts and proposed interface

- Report: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/report.html
- Scientific methods/findings: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/METHODS_AND_FINDINGS.md
- Source catalog/screening: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/results/selected_models.json and candidate_screening.json
- Numerical outputs: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/results/ecosystem_ppr.csv, group_sppr.csv, effect_decomposition.csv, scenario_envelopes.csv, aggregate_distributions.csv, method_scenario_coverage.csv
- Verification: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/verification/output_checks.json and browser_checks.json
- Response data: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/results/discard_responses.v2.json
- Consumer contract: C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/research/discard_sensitivity_expanded_2026_09_10/RESPONSE_INTERFACE.md

The versioned response file is a proposal for later ownership-coordinated integration. It requires an exact source hash/group identity, unchanged retained-landings support, valid baseline/endpoints, explicit scope and /9 convention, fixed annual selected/global NPP denominator across compared endpoints, and preserved missing-data masks. It does not authorize a global donor proxy, new mappings, yearly Ecopath reconstruction, interpolation across invalid points/weight changes, or installation into the live atlas. Parent task coordinates handoff to Complete all-ecosystem PPR and NPP integration (01a08d18-5b20-7b80-8ba3-5dfac3b22cac).
