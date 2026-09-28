# Why the WCP-2007 SPPR diagnostics fail

The reconstructed final model has one dominant problem: the published juvenile bigeye and juvenile yellowfin parameter rows do not support the catches and predation assigned to them. This is already present in the unnormalized source tables. All three SPPR budget gaps are completely explained by that same input imbalance, with different method-specific weights. No additional unexplained solver or detritus-budget discrepancy was found.

The paper describes the final model as balanced. This audit establishes a failure to reproduce that balance from the published tables under the current engine's group equations; it does not establish which value in the original native EwE model was different. Source values and production outputs were not changed.

## Direct source test

The paper gives the production equation on p6:

`B × PB × EE = landings + Σ(predator B × predator QB × diet fraction) + BA + net migration`.

Inputs below are from Table 6 (p19), final Table 4 columns (pp12-13), and Table 5 fleet landings (p14). All flows are tons/km2/year. Final tuna BA/B=0 is stated in the multi-stanza methods on p15. The source excludes living imports/exports (p7); the current loader sets unknown migration to zero.

| Term | Small BET (juvenile bigeye) | Small YFT (juvenile yellowfin) |
|---|---:|---:|
| Biomass B, tons/km2 | 0.00241 | 0.0128 |
| PB, year^-1 | 0.834 | 1.983 |
| Production B×PB | 0.00200994 | 0.0253824 |
| Published EE | 0.644 | 0.849 |
| Available used production B×PB×EE | 0.00129440136 | 0.0215496576 |
| Exact sum of fleet landings | 0.0013975 | 0.006973 |
| Predation from the exact published diet | 0.0012922586 | 0.021593107839 |
| Stated BA | 0 | 0 |
| Catch + predation minus available used production | +0.00139535724 | +0.007016450239 |
| Residual divided by total production | +69.4228% | +27.6430% |
| EE required by catch + predation | 1.3382283 | 1.1254297 |
| EE from predation alone | 0.6429339 | 0.8507118 |

The juvenile bigeye catch alone exceeds its published used-production budget: 0.0013975 > 0.00129440136, even before any predation is counted. This cannot be explained by a slight diet rounding discrepancy.

The printed EE values are close to the predation-only values for these two groups. That supports investigating a mismatch between final catches and the Table 6 state, or incomplete multi-stanza accounting. It does **not** establish that their catches should be zero. The positive fleet catches are explicit source data.

Table 5 uses the earlier 24-group roster and does not include newly added baby SKJ or split forage groups. Its caption does not identify it as exclusively initial or final. Tables 3-4 explicitly distinguish Initial and Final, whereas Table 6 explicitly gives final estimates. Therefore the combination is the published best-supported reconstruction, but the report does not establish that the displayed Table 5 is the exact catch state that generated Table 6. No catch redistribution among tuna stages is documented in the source.

## What was ruled out

- **Transcription/column shift:** the rotated diet pages were parsed by coordinates; Initial/Final headers, prey rows, predator columns, and all nonzero final cells were checked. Table 6, Table 5 and the critical diet cells were inspected in rendered pages. Canonical nonzero diet values equal the extraction exactly. Predator intake was multiplied by the corresponding prey fraction; the diet was not transposed.
- **Units or a second area division:** Tables 3/6 give biomass in tons/km2, Table 5 already gives tons/km2/year, and rates are year^-1. No absolute-to-area or carbon conversion was introduced.
- **Rounded catch totals:** the fleet figures were summed exactly, instead of using the highly rounded Total column. Small BET = 0.000504 + 0.0000525 + 0.000555 + 0.000286 = 0.0013975. Small YFT = 0.000763 + 0.00174 + 0.00217 + 0.0023 = 0.006973.
- **Diet normalization as the main cause:** normalizing the published consumer columns changes juvenile bigeye predation by -0.0000000362712 and juvenile yellowfin predation by -0.00000848504. The normalized production residuals remain +0.001395320969 and +0.007007965198. The maximal relative residual changes from 69.4228% to 69.4210%, essentially the same failure.
- **A new assimilation assumption:** consumer GS values follow Table 3, including final 0.35 for mesozooplankton and 0.4 for microzooplankton. These values do not create the catch/predation production discrepancy.
- **A separate consumption-equation failure:** the independent equation `Q = P + respiration + egestion` closes to 7.11e-15. The method `is_model_balanced()` instead puts *recomputed production* on the right side of its consumption check (PPRCalculator.py:687-690). Consequently its reported consumption residual is the same production residual divided by Q: the 2.2133% maximum is not another independent problem.
- **Divergence or negative coefficients:** all three solves converge; all report zero negative source columns. The GE living and recycling gains remain below one. TE and With Egestion have proximity warnings, but those warnings are not the reason all configurations have status FAIL.

## Why the three PP-budget gaps differ

For the exact completed model used by the diagnostics, define

`r_i = catch_i + predation_i + growth_i + net_migration_i + M0_i - P_i`.

The audit found, for each requested option,

`PP outflow - PP inflow = Σ_i (SPPR_i × r_i)`.

The equality is verified within 1.5e-12 primary-production-equivalent tons/km2/year. Thus all the global budget error is accounted for by the input residuals. Different transfer-efficiency and detritus accounting choices give different SPPR weights for the same residuals; there is no unexplained remaining global accounting error in this run.

| Option | Small YFT weighted residual | Small BET weighted residual | All other groups combined | Total excess outflow | Relative PP gap |
|---|---:|---:|---:|---:|---:|
| GE | 159.363129 | 52.950560 | -1.250125 | 211.063564 | 19.2233% |
| TE | 81.772938 | 39.001827 | -1.617902 | 119.156863 | 10.8526% |
| With Egestion | 37.309913 | 11.212599 | -0.287835 | 48.234678 | 4.3931% |

The source-model PP inflow is 1097.9547 for every option. The two juvenile groups contribute slightly more than 100% of each net positive gap, because small negative residuals in other tuna groups partly offset them. With Egestion's PP gap is graded WARN by the method, but its common input residual remains FAIL, so its overall status is also FAIL.

The current engine uses GE = P/Q; TE = (P/Q)×EE; With Egestion = P/(Q-egestion) (PPRCalculator.py, get_TE). GE and With Egestion use different detritus-recycling equations; TE uses direct primary-producer/import supply to detritus. These are the documented choices under audit, not newly changed formulas. Full per-group SPPR weights and weighted catch/growth/export terms are in the three `budget_decomposition_*.csv` files.

## Loader effects kept separate from source facts

Strict source loading without diet normalization rejects the rounded columns at tolerance 0.001. The standard bounded pipeline normalizes them, fills unknown catch and migration with zeros, derives respiration and unknown BA, and completes detritus flows. These are computational assumptions, recorded separately in the extraction report and `diagnostics/LOADER_TRANSFORMATIONS.json`.

In particular, the loader completes unknown BA for 24 source groups and treats the detritus surplus as growth/BA of about 208.048. The paper describes unused detritus as sedimentation export. The seven explicitly zero tuna BA values are preserved, so the loader cannot absorb their source discrepancies into unknown BA. This explains why the surviving production residuals are concentrated in the seven tuna stages. Missing BA for other groups is not independent proof that those groups are balanced in the original model.

The symbolic SPPR solve and the completed detritus convention do not add an unexplained gap: their PP-budget difference still equals the weighted input residual exactly. This algebraic agreement is a numerical consistency finding; it does not validate the loader-imputed flows as source evidence.

## What remains unresolved and possible next steps

Verified: the displayed final parameter/diet tables plus displayed landings and stated tuna BA=0 do not reproduce the paper's claimed balance. The dominant juvenile discrepancy is source-level, not a parsing or normalization artifact.

Unresolved: whether Table 5 includes catches not present in the final native model, whether a final table contains a reporting error, or whether native multi-stanza transfers/definitions supply missing accounting information. The report explicitly uses multi-stanza links (p15) but does not provide a native database or an exchange-flow table. The current standalone-group JSON does not encode those links. The audit cannot decide among these explanations.

The strongest next step is to obtain the exact 2007 final native EwE file or an author-confirmed correction, then compare juvenile fleet catches, stanza links, B/PB/EE and movement terms. Any confirmed correction should be preserved as a new source-supported variant. Without such evidence, retain the extraction as a failed candidate and consider a separately documented later model. Removing catches, changing published EE, or inserting balancing BA would be an experimental scenario rather than a source correction and requires a separate decision. No such scenario was run here.

## Reproduction and preservation

- `audit_balance_causes.py` loads the frozen canonical input and frozen engine code from `diagnostics/executed_code/`, using the same loader settings as the original three calls.
- It repeats only the three diagnostics with `return_sppr=True`, verifies the returned reports equal the saved original reports, and retains the SPPR vectors needed for the residual decomposition. No Monte Carlo or broad exporter is run.
- `CAUSE_AUDIT.json` records exact arithmetic, settings, hashes, source/loaded residuals and method decompositions. `source_equation_audit.csv` retains all source groups with calculable production; `loaded_equation_audit.csv` retains every engine group, including unfished groups and the synthetic import.
- `juvenile_tuna_predation_cells.json` lists every contributing predator, B, QB and source diet fraction for both juvenile tuna groups.
- Canonical model SHA-256 before/after: `d21f8703b0461c1a390021684ab291fdfa9c15f254babc77fa6a6e2176333155`. The source PDF SHA-256 remains `0adcf55ef7760865786bc2774b1fb147a6461a6fe0b128a943c8fce27c23f52f`. No original source, canonical model, shared scientific code, central workbook, regional selection or regional PPR result was modified by the investigation.
