# EE-floor calculation evidence: LME_035

Model: `35_412_Gulf_of_Thailande_(1963)`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| EwE_TE_EE | 29.1426184 | 29.1641462 | +0.0738705882% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| EwE_TE_noEE | 30.9848866 | 31.1947829 | +0.677415031% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| MC_new_GE | 21.7880047 | 22.6957431 | +4.16622978% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| MC_new_TE_EEfix | 98.4750593 | 89.4059781 | -9.20952096% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1986 | 25.6489891 | 25.6489891 | +0% | reused | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1995_TE0.1 | 56.9651294 | 56.9651294 | +0% | reused | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1995_TEmean | 20.050024 | 20.0133328 | -0.182998493% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_1995_TEmean_catch | 7.9840092 | 7.9840092 | +0% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| SPPR_2015 | 82.7128612 | 83.0035843 | +0.351484783% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| Ulanowicz_TE | 30.9795046 | 31.1947829 | +0.69490535% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| Ulanowicz_globalTEmean | 40.3523554 | 40.2490553 | -0.255995111% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| Ulanowicz_globalTEmean_catch | 11.7144754 | 11.7144754 | +0% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_GE | 20.9885199 | 20.927834 | -0.289138161% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_TE_EEfix | 87.4399215 | 83.0035843 | -5.0735832% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_TE_noEEfix | 82.7128612 | 83.0035843 | +0.351484783% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| new_WithEgestion | 10.5475363 | 10.5327193 | -0.140478554% | ok | provisional: assumed size/stage allocations; see allocation ledger |
| sym_GE_asDC | Unavailable / restricted | Unavailable / restricted | — | failed | did not resolve for any mapped group; refreshed diagnosis: did not resolve for any mapped group; refreshed diagnosis: unavailable: failed |
| sym_GE_asPP | Unavailable / restricted | Unavailable / restricted | — | failed | did not resolve for any mapped group; refreshed diagnosis: did not resolve for any mapped group; refreshed diagnosis: unavailable: failed |
| sym_TE_asDC | Unavailable / restricted | Unavailable / restricted | — | failed | did not resolve for any mapped group; refreshed diagnosis: did not resolve for any mapped group; refreshed diagnosis: unavailable: failed |
| sym_TE_asPP | Unavailable / restricted | Unavailable / restricted | — | failed | did not resolve for any mapped group; refreshed diagnosis: did not resolve for any mapped group; refreshed diagnosis: unavailable: failed |
| sym_WithEgestion_asDC | Unavailable / restricted | Unavailable / restricted | — | failed | did not resolve for any mapped group; refreshed diagnosis: did not resolve for any mapped group; refreshed diagnosis: unavailable: failed |
| sym_WithEgestion_asPP | Unavailable / restricted | Unavailable / restricted | — | failed | did not resolve for any mapped group; refreshed diagnosis: did not resolve for any mapped group; refreshed diagnosis: unavailable: failed |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
