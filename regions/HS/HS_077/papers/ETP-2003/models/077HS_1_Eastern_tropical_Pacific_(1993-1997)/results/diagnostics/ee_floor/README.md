# EE-floor calculation evidence: HS_077

Model: `077HS_1_Eastern_tropical_Pacific_(1993-1997)`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| EwE_TE_EE | 488.109611 | 487.188148 | -0.188782099% | ok | ok |
| EwE_TE_noEE | 1010.66275 | 1008.7995 | -0.184359127% | ok | ok |
| MC_new_GE | 321.734474 | 320.584231 | -0.357513002% | ok | ok |
| MC_new_TE_EEfix | 2833.79243 | 2799.75557 | -1.20110624% | ok | ok |
| SPPR_1986 | 335.699948 | 335.699948 | +0% | reused | ok |
| SPPR_1995_TE0.1 | 380.718957 | 380.718957 | +0% | reused | ok |
| SPPR_1995_TEmean | 19.0024209 | 19.0024022 | -9.81988045e-05% | ok | ok |
| SPPR_1995_TEmean_catch | 4252.37116 | 4246.90457 | -0.128553905% | ok | ok |
| SPPR_2015 | 2456.22865 | 2449.8058 | -0.261492083% | ok | ok |
| Ulanowicz_TE | 980.122634 | 978.976193 | -0.116969118% | ok | ok |
| Ulanowicz_globalTEmean | 34.9994608 | 34.9994179 | -0.000122723558% | ok | ok |
| Ulanowicz_globalTEmean_catch | 54024.3854 | 53921.547 | -0.190355507% | ok | ok |
| new_GE | 291.916533 | 291.916533 | +0% | ok | provisional: diagnostic WARN |
| new_TE_EEfix | 2456.22865 | 2449.8058 | -0.261492083% | ok | provisional: diagnostic WARN; strict SPPR balance check failed |
| new_TE_noEEfix | Unavailable / restricted | Unavailable / restricted | — | ok | FAIL: configuration diagnostic |
| new_WithEgestion | 29.0644556 | 29.0644556 | +0% | ok | provisional: diagnostic WARN |
| sym_GE_asDC | Unavailable / restricted | Unavailable / restricted | — | ok | DIVERGED: negative source-group SPPR |
| sym_GE_asPP | 291.916533 | 291.916533 | +0% | ok | ok |
| sym_TE_asDC | 2463.64704 | 2457.14411 | -0.263955231% | ok | ok |
| sym_TE_asPP | 2456.22865 | 2449.8058 | -0.261492083% | ok | ok |
| sym_WithEgestion_asDC | Unavailable / restricted | Unavailable / restricted | — | ok | DIVERGED: negative source-group SPPR |
| sym_WithEgestion_asPP | 29.0644556 | 29.0644556 | +0% | ok | ok |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
