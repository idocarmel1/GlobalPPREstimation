# HS_071: selected WCP-2007 option 1

USER SELECTED 2026-09-28: WCP-2007 option 1 (D_fixed_M0) for HS_071, EEZ_941 and EEZ_598. Explicit experimental variant preserves juvenile other-mortality flows and changes Small BET P/B to 1.4129713563375232, EE to 0.7898725981469387; Small YFT P/B to 2.5304972811160384, EE to 0.8816702937266387. GE, TE and With Egestion all WARN; PP-budget checks OK, but strict mass balance remains false (adult BET residual 0.727940%). This is an adopted surrogate, not an author-confirmed correction or a region-specific native EwE model. Original source remains preserved. Griffiths 2019 source and pooled variant are retained for later investigation of failures, not selected.

Exact selected model: `941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)`. Its JSON bytes match the tested D_fixed_M0 experiment (SHA-256 `328330dc06ed3e96462995f1a04c1bdaa9747468af8bb4d9e4f57196b9cc1b03`).

Existing diagnostic returns are retained in diagnostic_evidence/. No diagnostic rerun or additional biological correction was performed to record this selection. Previous regional results are archived and model-dependent tables are cleared pending calculations for this selection.

USER REQUEST 2026-09-28: retain Griffiths et al. (2019) for later investigation across HS_071, EEZ_941 and EEZ_598. Understand why it fails before considering adoption. Original 46-group extraction is blocked by unknown two-pool routing. The authorized 45-group pooled experiment loads but GE, TE and With Egestion all FAIL. Investigate the Pomfret production/predation inconsistency, 22 printed catch-total versus fleet-sum conflicts, and routing/fishery-return and loader effects separately. No further parameter repair is authorized by this note.
