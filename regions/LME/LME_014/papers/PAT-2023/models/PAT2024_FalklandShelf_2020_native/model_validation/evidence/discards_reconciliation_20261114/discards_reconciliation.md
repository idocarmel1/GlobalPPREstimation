# LME_014 Discards reconciliation

The focused GE/TE checks are complete with EE floor **ON, 0.1**. Restoring the native fleet returns changes PPR slightly and leaves the Discards (35) deficit unchanged. The original Ecopath database already contains that deficit as a **negative calculated Export**; the reconstruction expresses it as negative detritus accumulation. Neither field establishes an observed external food supply.

## Native source and Ecopath verification

A fresh read-only query verified all 72 group/fleet catch records and their identifiers. The two fleets route **0.005859524956463247 t/km² during 2020** to **Detritus (36)** and zero to **Discards (35)**. All recorded discard mortality fractions are one. Natural mortality/egestion routing is a separate matrix. [Source ledger](outputs/source/source_fisheries_ledger.json) · [Independent source arithmetic](qa/independent/source_arithmetic_verification.json)

The installed EwE engine loaded and ran an isolated copy with all autosave components disabled. `RunEcopath` and `IsModelBalanced` both returned true. Its Discards output was:

| Native Discards term | t/km²/year |
|---|---:|
| Incoming flow (`InputToDet`) | 0 |
| Consumed (`DetEaten`) | 0.20750363171100616 |
| Calculated export (`Ex`) | −0.20750363171100616 |
| Biomass accumulation (`BA`) | 0 |
| Explicit detritus import | 0 |

The calculated export exactly matches the value stored in the original database. The official Ecopath calculation derives detritus export from incoming flow minus consumption, accumulation, onward transfer and respiration. Thus the negative export is a closure residual, not a newly documented import. Ecopath's balanced flag coexists with this unsupplied pool. [Native results](outputs/source/native_sdk_probe.json) · [Independent native verification](outputs/source/native_probe_verification.json) · [Official-source context](outputs/source/web_context.json)

The source was saved by EwE **6.6.8.18072**; the installed calculation assembly reports **6.7.0.18858** (installer label 6.7.0.18865). This is a later-version native reproduction, not an execution of the exact original binary. Both native detritus export outputs reproduce the source-stored values exactly. The original database hash remained unchanged. This native check used the original source settings; EE floor ON applies to the separate GE/TE comparisons below.

A related source clarification emerged: native Detritus has stored input EE=0, but its calculated EE is **0.04784027114510536**, which rounds to the paper's **0.05**. Comparing the stored input directly with the printed calculated output had overstated this as a source disagreement.

## What was lost in the reconstruction

Both retained JSON variants contain export=0 for the two detritus pools, so the source-stored native Export values were lost before the archived loader. That loader also clears detritus catch/export and derives accumulation from the residual. The old calculation omitted fleet-return supply as well. These are distinct transformations. [Native-to-canonical trace](qa/independent/native_export_trace.json)

The new controlled comparison restores only the independently verified donor-to-recipient fleet return matrix. It preserves accepted living biomass, production, consumption, diets, predation, catch and migration. No return was redirected to group 35, no additional offal/import was invented, and no detritus groups were pooled.

## Focused PPR results

The two scenarios use identical pinned calculation code and audited completed initialization. The no-return control reproduces the previously saved floor-ON SPPR, A and L matrices exactly. Each fresh restored scenario receives the floor once, followed by one GE and one TE diagnostic call, with `det_collapse_mode=never` and `det_open_mode=none`.

| Method | Model-catch PPR: control | Model-catch PPR: native returns | Change | Overall status |
|---|---:|---:|---:|---|
| GE | 35.6046647414 | 35.6114670127 | +0.0191% | WARN |
| TE | 89.3066575611 | 89.4135556062 | +0.1197% | WARN |

These are source-model catch-weighted, all-source PPR values in the engine's model-mass/area/year convention, not regional LME catch totals or carbon estimates. The source reports tonnes per km² for 2020 but does not explicitly establish wet versus dry mass; the project's assumed wet-weight convention is retained as a separate limitation.

All four calls pass their strict weighted balance checks and return finite SPPR matrices with no negative entries. All 37 recipient groups and five source columns were checked. Only the Detritus (36) source column changes; PP-only footprints remain unchanged. Discards (35) remains a zero source column and has an unexplained physical residual of **−0.20750363203745528 t/km²/year**. Returned catch is credited internally once and excluded from external removals; total-catch fishery PPR retains its original catch vector. [Comparison and complete diagnostics](outputs/diagnostics/comparison_summary.json) · [Independent matrix and budget verification](qa/independent/diagnostic_array_verification.json)

Native source BA=0, historical loader-derived pre-floor BA, and floor-effective residual are recorded separately. The floor intentionally recomputes effective detritus closure; this is not a source-parameter correction. The source-BA-zero comparisons are conditional arithmetic with unchanged coefficients, not an additional source-preserving solve or a diagnosis of the original native Ecopath model.

## Remaining scientific question

The reconstructed demand from Discards is **35.413 times** the recorded annual fisheries discards. Seabirds account for **86.6%** of that demand. Even a hypothetical redirection of all recorded discards to group 35 would leave about **0.2016441 t/km²/year** unexplained; that redirection was not run or adopted.

The main paper describes birds eating fish guts and heads. Its cited albatross study distinguishes unwanted fish from processing offal and uses fishery catches as a relative index of discard availability; it does not establish the annual offal amount missing here. The remaining question is whether the intended Discards pool includes processing waste absent from Table S4, or whether the final diet/routing specification requires clarification. A negative calculated export cannot supply the missing provenance. [Paper and related primary-source evidence](outputs/source/web_context.json)

The current reconstruction therefore remains **WARN with unresolved discard-source attribution**. The numerical omission of fleet returns has been isolated and quantified; the ecological supply discrepancy remains. The next evidence needed is the authors' intended final Discards inflow/routing and, if applicable, a quantified processing-offal ledger. A new import, changed diet or pooled-detritus scenario would require a separate justified scientific choice.

## Scope and preservation

This package is a model-local investigation for researcher review. The canonical model, accepted parameters, regional workbook, coefficient workbook, snapshots, taxon appendix and researcher DOCX were not overwritten. No decision was registered and this task performed no Project.xlsx, map, trends or sources-page writes. Shared code remained unchanged by this task; the coordinator confirmed the pinned engine identity and that floor-effective detritus closure is intentional. Concurrent shared-file changes by the coordinator, if any, are distinguished in the protection receipt.

[Evidence index](evidence_index.json) · [Execution provenance](outputs/diagnostics/run_provenance.json) · [Preservation receipt](qa/protected_final.json)
