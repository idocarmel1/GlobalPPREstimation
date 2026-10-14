# EE-floor calculation evidence: LME_032

Model: `32_1_Arabian_Sea_off_Karnataka_(2000)`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| EwE_TE_EE | 250.100251 | 250.100251 | +0% | ok | ok |
| EwE_TE_noEE | 283.763065 | 283.763065 | +0% | ok | ok |
| MC_new_GE | 273.817106 | 287.748187 | +5.0877319% | ok | ok |
| MC_new_TE_EEfix | 509.979944 | 517.173856 | +1.41062651% | ok | ok |
| SPPR_1986 | 61.733978 | 61.733978 | +0% | reused | ok |
| SPPR_1995_TE0.1 | 344.429994 | 344.429994 | +0% | reused | ok |
| SPPR_1995_TEmean | 82.8576326 | 82.85758 | -6.34642847e-05% | ok | ok |
| SPPR_1995_TEmean_catch | 40.5213227 | 40.5213227 | +0% | ok | ok |
| SPPR_2015 | 475.633964 | 475.633968 | +8.00053246e-07% | ok | ok |
| Ulanowicz_TE | 271.383867 | 271.383867 | +0% | ok | ok |
| Ulanowicz_globalTEmean | 431.555344 | 431.55488 | -0.000107528502% | ok | ok |
| Ulanowicz_globalTEmean_catch | 133.793944 | 133.793944 | +0% | ok | ok |
| new_GE | 259.045341 | 259.022775 | -0.00871106203% | ok | ok |
| new_TE_EEfix | 475.633964 | 475.633968 | +8.00053246e-07% | ok | ok |
| new_TE_noEEfix | 475.633964 | 475.633968 | +8.00053246e-07% | ok | ok |
| new_WithEgestion | 88.1931837 | 88.1900533 | -0.00354941311% | ok | ok |
| sym_GE_asDC | 259.045341 | 259.022775 | -0.00871106203% | ok | ok |
| sym_GE_asPP | 259.045341 | 259.022775 | -0.00871106203% | ok | ok |
| sym_TE_asDC | 475.633964 | 475.633968 | +8.00053246e-07% | ok | ok |
| sym_TE_asPP | 475.633964 | 475.633968 | +8.00053246e-07% | ok | ok |
| sym_WithEgestion_asDC | 88.1931837 | 88.1900533 | -0.00354941311% | ok | ok |
| sym_WithEgestion_asPP | 88.1931837 | 88.1900533 | -0.00354941311% | ok | ok |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
