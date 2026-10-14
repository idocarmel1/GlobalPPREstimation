# EE-floor calculation evidence: LME_013

Model: `Chiaverano2018_detailed_Northern_Humboldt_1995_1998`. The user authorized implementation, scientific reruns and adoption/publication of EE-floor calculations on 2026-10-14. The saved setting is `use_ee_floor=True`, `ee_floor=0.1`. Explicit OFF restores the audited baseline. This is a hypothetical calculation assumption, not a published parameter correction or a new researcher approval.

The floor is applied once after audited initialization. Source EE/M0 and completed pre-floor EE/M0 remain separate from effective EE/M0. The removed mortality is an explicit nonfishery external sink counted by production and both SPPR balance branches. Only reduced M0 plus unchanged egestion enter the existing detritus fate matrix. Catch, fishery weighting, living biological flows, migration and living biomass accumulation remain preserved. Negative detritus residuals and existing diagnostic restrictions remain limitations.

The audited loader dependencies, model-specific settings and recorded Monte Carlo policies remain recorded in [the result manifest](../../result_manifest.json). Humboldt retains `det_collapse_mode='auto'`. Compatible unaffected methods retain their actual earlier provenance; affected methods were executed with complete return evidence. An inventory outcome can be failed, timed out, restricted or unavailable while the model retains its historical researcher validation. Original signed Word documents and source diagnostics were preserved.

Before/after below: 2019 landings, all sources, all model groups, **million tonnes carbon equivalent**. The native regional Annual `ppr` values are wet-weight equivalent; existing regional ratio and view arithmetic divide by 9. Raw and converted values both remain in the machine-readable report. Researcher exclusions from displayed PPR remain separate and unchanged. Monte Carlo differences include new draws under the recorded unseeded policies where applicable; compatible unaffected Monte Carlo results were not redrawn.

| Method | Before (Mt C) | After (Mt C) | Change | Execution/retention | Scientific availability / restriction |
|---|---:|---:|---:|---|---|
| new_GE | 244.046986 | 227.510178 | -6.77607563% | ok | provisional: DIRECT GE overall FAIL; balanced model; det_collapse_mode=always; pending researcher review; production-ineligible; refreshed diagnosis: FAIL: configuration diagnostic |
| new_TE_EEfix | 835.805955 | 302.008898 | -63.8661466% | ok | provisional: DIRECT TE overall FAIL; balanced model; det_collapse_mode=always; pending researcher review; production-ineligible |
| new_WithEgestion | 98.0905962 | 95.7350406 | -2.40140821% | ok | provisional: DIRECT With Egestion overall FAIL; balanced model; det_collapse_mode=always; pending researcher review; production-ineligible; refreshed diagnosis: FAIL: configuration diagnostic |
| EwE_TE_EE | 120.933314 | 71.0477444 | -41.2504778% | ok | ok |
| EwE_TE_noEE | 592.633424 | 187.048136 | -68.4378018% | ok | ok |
| MC_new_GE | Unavailable / restricted | Unavailable / restricted | — | ok | unavailable: MC acceptance 3/100 below 80%; refreshed diagnosis: unavailable: MC acceptance 3/100 below 80%; refreshed diagnosis: unavailable: no finite coefficients |
| MC_new_TE_EEfix | 920.415232 | 337.587444 | -63.3222667% | ok | ok |
| SPPR_1986 | 78.8343165 | 78.8343165 | +0% | reused | ok |
| SPPR_1995_TE0.1 | 159.809496 | 159.809496 | +0% | reused | ok |
| SPPR_1995_TEmean | 18.5370082 | 18.4279216 | -0.588479991% | ok | ok |
| SPPR_1995_TEmean_catch | 160.351162 | 160.351162 | +0% | ok | ok |
| SPPR_2015 | 835.805955 | 302.008898 | -63.8661466% | ok | ok |
| Ulanowicz_TE | 587.048855 | 182.793709 | -68.8622664% | ok | ok |
| Ulanowicz_globalTEmean | 25.2225724 | 25.0387624 | -0.728751825% | ok | ok |
| Ulanowicz_globalTEmean_catch | 429.060048 | 429.060048 | +0% | ok | ok |
| new_TE_noEEfix | Unavailable / restricted | Unavailable / restricted | — | ok | FAIL: configuration diagnostic |
| sym_GE_asDC | Unavailable / restricted | Unavailable / restricted | — | failed | unavailable: failed; Method execution or evidence reconciliation failed: RecursionError: maximum recursion depth exceeded |
| sym_GE_asPP | 244.046986 | 227.510178 | -6.7760757% | ok | ok |
| sym_TE_asDC | Unavailable / restricted | Unavailable / restricted | — | failed | unavailable: failed; Method execution or evidence reconciliation failed: RecursionError: maximum recursion depth exceeded |
| sym_TE_asPP | 835.805955 | 302.008898 | -63.8661466% | ok | ok |
| sym_WithEgestion_asDC | Unavailable / restricted | Unavailable / restricted | — | failed | unavailable: failed; Method execution or evidence reconciliation failed: ValueError: matrices are not aligned |
| sym_WithEgestion_asPP | 98.0905962 | 95.7350406 | -2.4014082% | ok | ok |

Evidence:

- [Full 22-method manifest](../../result_manifest.json) and [actual method returns](../method_coverage/).
- [Source/completed/effective runtime ledger](runtime.json.gz); `*.baseline.json.gz` files retain lossless outgoing calculation packages and historical manifests without relabeling them as floor-enabled.
- [OFF and saved experiment reconciliation](experiment_reconciliation.json.gz). The Eastern Tropical Pacific experiment also floored a group with unknown source EE; the production setting excludes it. Replaying the experiment with the same valid-input eligibility agrees without changing source parameters or tolerances.
- [Input and result preservation](publication_verification.json.gz), [view/workbook equality](view_verification.json.gz), and [authenticated duplicate-removal receipts](execution_cache_cleanup.json.gz).

Supporting whole-project audit code, original preservation capture, native pre-publication Project.xlsx, test output, browser evidence and the eight-model index are retained under the Humboldt model's `results/diagnostics/ee_floor/verification/` directory. The broader legacy engine test suite remains blocked by absent historical engine-local ToyModels/Black Sea fixture paths; no scientific inputs were substituted. Root `structure.md` remains absent; the applicable structure guide is `explainers/structure.md`.
