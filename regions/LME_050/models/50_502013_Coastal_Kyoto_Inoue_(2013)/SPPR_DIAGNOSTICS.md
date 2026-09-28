# Direct SPPR diagnostics — Coastal Kyoto 2013

Calls: `PPRCalculator.diagnose_sppr(short=False, flat=False, return_sppr=False)`, with GE, TE, and With Egestion. Complete values below are returned diagnostics; displayed floats are abbreviated to 10 significant digits. JSON retains full precision. Footprints are model-internal quantities, not regional annual PPR.

| Returned field | GE | TE | With Egestion |
|---|---:|---:|---:|
| status | WARN | WARN | WARN |
| model_input.status | WARN | WARN | WARN |
| model_input.is_model_balanced | True | True | True |
| model_input.p_max_rel_residual | 1.199787134e-16 | 1.199787134e-16 | 1.199787134e-16 |
| model_input.q_max_rel_residual | 2.114710523e-16 | 2.114710523e-16 | 2.114710523e-16 |
| model_input.dc_rows_sum_to_1 | True | True | True |
| model_input.dc_max_deviation | 2.220446049e-16 | 2.220446049e-16 | 2.220446049e-16 |
| model_input.n_negative_catch | 0 | 0 | 0 |
| model_input.n_zero_catch | 13 | 13 | 13 |
| model_input.total_catch | 3.999627 | 3.999627 | 3.999627 |
| model_input.has_catch | True | True | True |
| model_input.has_ee_issues | True | True | True |
| model_input.n_ee0 | 1 | 1 | 1 |
| model_input.n_ee_marginal | 0 | 0 | 0 |
| model_input.n_ee_gt_1 | 0 | 0 | 0 |
| model_input.ee0_groups | [30] | [30] | [30] |
| model_input.ee_marginal_groups | [] | [] | [] |
| divergence.status | OK | OK | OK |
| divergence.solve_error | None | None | None |
| divergence.b | 0.03129442747 | 0 | 0.03179448901 |
| divergence.b_converges | True | True | True |
| divergence.rho_living | 0.1060445413 | 0.2461420247 | 0.08483563303 |
| divergence.living_converges | True | True | True |
| divergence.sppr_det.40 | 1.361092011 | 0.675780055 | 1.38712794 |
| divergence.max_sppr_det | 1.361092011 | 0.675780055 | 1.38712794 |
| divergence.max_sppr_group.seq | 11 | 8 | 11 |
| divergence.max_sppr_group.tl | 2.977351155 | 2.720233759 | 2.977351155 |
| divergence.max_sppr_group.sppr | 88.47169207 | 2531.64821 | 50.98205693 |
| divergence.max_sppr_group.inv_te | 12.84615385 | 30.14403292 | 10.27692308 |
| divergence.max_tl_group.seq | 12 | 12 | 12 |
| divergence.max_tl_group.tl | 3.208475248 | 3.208475248 | 3.208475248 |
| divergence.max_tl_group.sppr | 23.89734068 | 141.2506497 | 13.87083751 |
| divergence.max_tl_group.inv_te | 4.035714286 | 5.310150376 | 3.228571429 |
| divergence.n_negative_sources | 0 | 0 | 0 |
| divergence.expect_negatives | False | False | False |
| divergence.near_singular_te | [] | [] | [] |
| balance.status | OK | OK | OK |
| balance.is_balanced | True | True | True |
| balance.inflow | 1844.312981 | 1844.312981 | 1844.312981 |
| balance.outflow | 1844.312981 | 1844.312981 | 1844.312981 |
| balance.rel_gap | 1.232836714e-16 | 1.232836714e-16 | 2.465673427e-16 |
| footprint.ppr_all | 83.09784055 | 969.7225065 | 49.1481273 |
| footprint.ppr_inner | 67.8619438 | 927.587962 | 38.29651095 |
| footprint.ppr_pp_only | 65.10526629 | 902.1084941 | 36.38765515 |
| footprint.npp | 1801.7326 | 1801.7326 | 1801.7326 |
| footprint.ppr2npp | 0.0376648254 | 0.514831092 | 0.02125537993 |
| footprint.ppr2npp_pp_only | 0.03613481062 | 0.5006894442 | 0.02019592427 |
| config.TE_option | GE | TE | With Egestion |
| config.det_open_mode | none | none | none |
| config.det_theta | 1 | 1 | 1 |
| config.det_external_sppr | 0 | 0 | 0 |
| config.det_collapse_mode | never | never | never |
| config.explicit_TE | False | False | False |
| config.method | single_detritus | None | single_detritus |
| config.would_pool | False | False | False |
| config.model | Coastal_Kyoto_Inoue (2013) | Coastal_Kyoto_Inoue (2013) | Coastal_Kyoto_Inoue (2013) |
| warnings | ["1 group(s) with EE=0 (all production is non-predatory death): 30 (Tongue sole). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"] | ["1 group(s) with EE=0 (all production is non-predatory death): 30 (Tongue sole). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed", "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)"] | ["1 group(s) with EE=0 (all production is non-predatory death): 30 (Tongue sole). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"] |

Raw JSON: [GE](evidence/diagnose_sppr_GE.json), [TE](evidence/diagnose_sppr_TE.json), [With Egestion](evidence/diagnose_sppr_With_Egestion.json).
