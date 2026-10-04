# Direct SPPR diagnostics — Coastal Kyoto 1985

Calls: `PPRCalculator.diagnose_sppr(short=False, flat=False, return_sppr=False)`, with GE, TE, and With Egestion. Complete values below are returned diagnostics; displayed floats are abbreviated to 10 significant digits. JSON retains full precision. Footprints are model-internal quantities, not regional annual PPR.

| Returned field | GE | TE | With Egestion |
|---|---:|---:|---:|
| status | WARN | WARN | WARN |
| model_input.status | WARN | WARN | WARN |
| model_input.is_model_balanced | True | True | True |
| model_input.p_max_rel_residual | 6.632156658e-16 | 6.632156658e-16 | 6.632156658e-16 |
| model_input.q_max_rel_residual | 1.983249419e-16 | 1.983249419e-16 | 1.983249419e-16 |
| model_input.dc_rows_sum_to_1 | True | True | True |
| model_input.dc_max_deviation | 2.220446049e-16 | 2.220446049e-16 | 2.220446049e-16 |
| model_input.n_negative_catch | 0 | 0 | 0 |
| model_input.n_zero_catch | 14 | 14 | 14 |
| model_input.total_catch | 21.46681 | 21.46681 | 21.46681 |
| model_input.has_catch | True | True | True |
| model_input.has_ee_issues | True | True | True |
| model_input.n_ee0 | 2 | 2 | 2 |
| model_input.n_ee_marginal | 0 | 0 | 0 |
| model_input.n_ee_gt_1 | 0 | 0 | 0 |
| model_input.ee0_groups | [34, 23] | [34, 23] | [34, 23] |
| model_input.ee_marginal_groups | [] | [] | [] |
| divergence.status | OK | OK | OK |
| divergence.solve_error | None | None | None |
| divergence.b | 0.01918493651 | 0 | 0.01945577343 |
| divergence.b_converges | True | True | True |
| divergence.rho_living | 0.1060445413 | 0.2441561799 | 0.08483563303 |
| divergence.living_converges | True | True | True |
| divergence.sppr_det.40 | 1.191347653 | 0.7282538903 | 1.333771975 |
| divergence.max_sppr_det | 1.191347653 | 0.7282538903 | 1.333771975 |
| divergence.max_sppr_group.seq | 11 | 30 | 11 |
| divergence.max_sppr_group.tl | 2.977566853 | 2.71 | 2.977566853 |
| divergence.max_sppr_group.sppr | 80.82391369 | 6359.418977 | 48.62429897 |
| divergence.max_sppr_group.inv_te | 12.84615385 | 475.6756757 | 10.27692308 |
| divergence.max_tl_group.seq | 12 | 12 | 12 |
| divergence.max_tl_group.tl | 3.208475248 | 3.208475248 | 3.208475248 |
| divergence.max_tl_group.sppr | 24.10700707 | 125.5439509 | 14.21861586 |
| divergence.max_tl_group.inv_te | 4.035714286 | 5.765306122 | 3.228571429 |
| divergence.n_negative_sources | 0 | 0 | 0 |
| divergence.expect_negatives | False | False | False |
| divergence.near_singular_te | [] | [] | [] |
| balance.status | OK | OK | OK |
| balance.is_balanced | True | True | True |
| balance.inflow | 4473.954582 | 4473.954582 | 4473.954582 |
| balance.outflow | 4473.954582 | 4473.954582 | 4473.954582 |
| balance.rel_gap | 2.032865299e-16 | 2.032865299e-16 | 2.032865299e-16 |
| footprint.ppr_all | 433.7914973 | 1159.386035 | 282.5250026 |
| footprint.ppr_inner | 362.4739531 | 999.9641435 | 226.8486321 |
| footprint.ppr_pp_only | 360.0268911 | 958.5378519 | 224.8925905 |
| footprint.npp | 4162.7343 | 4162.7343 | 4162.7343 |
| footprint.ppr2npp | 0.08707592821 | 0.2402181046 | 0.05449510244 |
| footprint.ppr2npp_pp_only | 0.08648807854 | 0.2302664025 | 0.05402520898 |
| config.TE_option | GE | TE | With Egestion |
| config.det_open_mode | none | none | none |
| config.det_theta | 1 | 1 | 1 |
| config.det_external_sppr | 0 | 0 | 0 |
| config.det_collapse_mode | never | never | never |
| config.explicit_TE | False | False | False |
| config.method | single_detritus | None | single_detritus |
| config.would_pool | False | False | False |
| config.model | Coastal_Kyoto_Inoue (1985) | Coastal_Kyoto_Inoue (1985) | Coastal_Kyoto_Inoue (1985) |
| warnings | ["2 group(s) with EE=0 (all production is non-predatory death): 34 (Brittle star), 23 (Ivory shell). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"] | ["2 group(s) with EE=0 (all production is non-predatory death): 34 (Brittle star), 23 (Ivory shell). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed", "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)"] | ["2 group(s) with EE=0 (all production is non-predatory death): 34 (Brittle star), 23 (Ivory shell). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"] |

Raw JSON: [GE](evidence/diagnose_sppr_GE.json), [TE](evidence/diagnose_sppr_TE.json), [With Egestion](evidence/diagnose_sppr_With_Egestion.json).
