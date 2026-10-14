# EE-floor calculation evidence: LME_028

Model: `28_646_Guinea_(1998)`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| EwE_TE_EE | 1036.97135 | 1036.97135 | +0% | reused | ok |
| EwE_TE_noEE | 1475.62794 | 1475.62794 | +0% | reused | ok |
| MC_new_GE | 950.099107 | 950.099107 | +0% | reused | ok |
| MC_new_TE_EEfix | Unavailable / restricted | Unavailable / restricted | — | reused | IMPLAUSIBLE - up to 34x the trophic-chain estimate; the solve is near-singular for this model |
| SPPR_1986 | 67.4907438 | 67.4907438 | +0% | reused | ok |
| SPPR_1995_TE0.1 | 192.792187 | 192.792187 | +0% | reused | ok |
| SPPR_1995_TEmean | 183.113849 | 183.113849 | +0% | reused | ok |
| SPPR_1995_TEmean_catch | 107.359105 | 107.359105 | +0% | reused | ok |
| SPPR_2015 | Unavailable / restricted | Unavailable / restricted | — | reused | IMPLAUSIBLE - up to 29x the trophic-chain estimate; the solve is near-singular for this model |
| Ulanowicz_TE | 1355.90502 | 1355.90502 | +0% | reused | ok |
| Ulanowicz_globalTEmean | 1398.18069 | 1398.18069 | +0% | reused | ok |
| Ulanowicz_globalTEmean_catch | 566.460515 | 566.460515 | +0% | reused | ok |
| new_GE | 850.39684 | 850.39684 | +0% | reused | ok |
| new_TE_EEfix | Unavailable / restricted | Unavailable / restricted | — | reused | IMPLAUSIBLE - up to 29x the trophic-chain estimate; the solve is near-singular for this model |
| new_TE_noEEfix | Unavailable / restricted | Unavailable / restricted | — | reused | IMPLAUSIBLE - up to 29x the trophic-chain estimate; the solve is near-singular for this model |
| new_WithEgestion | 270.860495 | 270.860495 | +0% | reused | ok |
| sym_GE_asDC | 850.918327 | 850.918327 | +0% | reused | ok |
| sym_GE_asPP | 850.39684 | 850.39684 | +0% | reused | ok |
| sym_TE_asDC | Unavailable / restricted | Unavailable / restricted | — | reused | DIVERGED: negative source-group SPPR |
| sym_TE_asPP | Unavailable / restricted | Unavailable / restricted | — | reused | IMPLAUSIBLE - up to 29x the trophic-chain estimate; the solve is near-singular for this model |
| sym_WithEgestion_asDC | Unavailable / restricted | Unavailable / restricted | — | reused | DIVERGED: negative source-group SPPR |
| sym_WithEgestion_asPP | 270.860495 | 270.860495 | +0% | reused | ok |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
