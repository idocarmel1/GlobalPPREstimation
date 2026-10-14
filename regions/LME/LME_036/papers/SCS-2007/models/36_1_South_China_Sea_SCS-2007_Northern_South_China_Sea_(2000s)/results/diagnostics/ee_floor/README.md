# EE-floor calculation evidence: LME_036

Model: `36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| EwE_TE_EE | 199.974495 | 197.055313 | -1.45977719% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| EwE_TE_noEE | 297.943777 | 294.870954 | -1.03134332% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| MC_new_GE | 50.8334539 | 51.0154586 | +0.358041167% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| MC_new_TE_EEfix | 458.76712 | 439.071233 | -4.29322113% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1986 | 72.654273 | 72.654273 | +0% | reused | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1995_TE0.1 | 185.590888 | 185.590888 | +0% | reused | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1995_TEmean | 500.08538 | 500.084221 | -0.000231776911% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1995_TEmean_catch | 42.67355 | 42.67355 | +0% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_2015 | 423.485432 | 418.907177 | -1.08108906% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| Ulanowicz_TE | 289.108328 | 286.106953 | -1.03814891% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| Ulanowicz_globalTEmean | 3641.52378 | 3641.50777 | -0.000439547992% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| Ulanowicz_globalTEmean_catch | 71.5900355 | 71.5900355 | +0% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_GE | 49.315844 | 49.3315102 | +0.0317670318% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_TE_EEfix | 423.485432 | 418.907177 | -1.08108906% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_TE_noEEfix | 423.485432 | 418.907177 | -1.08108906% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_WithEgestion | 25.3384651 | 25.3473537 | +0.0350792812% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_GE_asDC | 49.315844 | 49.3315102 | +0.0317670318% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_GE_asPP | 49.315844 | 49.3315102 | +0.0317670318% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_TE_asDC | 423.485432 | 418.907177 | -1.08108906% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_TE_asPP | 423.485432 | 418.907177 | -1.08108906% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_WithEgestion_asDC | 25.3384651 | 25.3473537 | +0.0350792812% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_WithEgestion_asPP | 25.3384651 | 25.3473537 | +0.0350792812% | ok | provisional: assumed size/stage allocations; see allocation ledger |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
