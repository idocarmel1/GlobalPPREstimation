# EE-floor calculation evidence: LME_047

Model: `47_2_East_China_Sea_(2018)`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| EwE_TE_EE | 65.9412802 | 65.9606614 | +0.0293915892% | ok | ok |
| EwE_TE_noEE | 114.322088 | 114.512872 | +0.166882527% | ok | ok |
| MC_new_GE | 25.8258292 | 24.7385867 | -4.20990362% | ok | ok |
| MC_new_TE_EEfix | 149.082102 | 143.259826 | -3.90541548% | ok | ok |
| SPPR_1986 | Unavailable / restricted | Unavailable / restricted | — | reused | returned zero for every mapped group - check the method upstream |
| SPPR_1995_TE0.1 | 108.134195 | 108.134195 | +0% | reused | ok |
| SPPR_1995_TEmean | 169.6348 | 169.633748 | -0.000619867485% | ok | ok |
| SPPR_1995_TEmean_catch | 54.1418115 | 54.1381524 | -0.006758396% | ok | ok |
| SPPR_2015 | 137.547883 | 137.782311 | +0.170434034% | ok | ok |
| Ulanowicz_TE | 112.215087 | 112.402528 | +0.16703706% | ok | ok |
| Ulanowicz_globalTEmean | 418.509292 | 418.505687 | -0.000861390513% | ok | ok |
| Ulanowicz_globalTEmean_catch | 91.4109769 | 91.4030794 | -0.00863963336% | ok | ok |
| new_GE | 24.2957882 | 24.2935868 | -0.009060817% | ok | ok |
| new_TE_EEfix | 138.080451 | 137.782311 | -0.215917363% | ok | ok |
| new_TE_noEEfix | 137.547883 | 137.782311 | +0.170434034% | ok | ok |
| new_WithEgestion | 13.2657983 | 13.265281 | -0.00389936271% | ok | ok |
| sym_GE_asDC | 24.2957882 | 24.2935868 | -0.009060817% | ok | ok |
| sym_GE_asPP | 24.2957882 | 24.2935868 | -0.009060817% | ok | ok |
| sym_TE_asDC | 137.547883 | 137.782311 | +0.170434034% | ok | ok |
| sym_TE_asPP | 138.080451 | 137.782311 | -0.215917363% | ok | ok |
| sym_WithEgestion_asDC | 13.2657983 | 13.265281 | -0.00389936271% | ok | ok |
| sym_WithEgestion_asPP | 13.2657983 | 13.265281 | -0.00389936271% | ok | ok |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
