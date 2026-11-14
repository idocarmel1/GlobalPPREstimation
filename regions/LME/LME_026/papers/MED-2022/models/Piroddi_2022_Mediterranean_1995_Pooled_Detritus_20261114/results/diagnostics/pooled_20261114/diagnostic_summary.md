# Pooled Mediterranean model: diagnostic findings

The requested variant was created and all three direct SPPR methods returned numerical results with **EE floor ON at 0.1**. **GE, TE and With Egestion all have overall FAIL grades.** Pooling resolved the missing-routing construction barrier under the explicitly authorized 100% routing assumption; it did not remove the retained input-budget inconsistencies.

The exact model is [Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114](../../../model.json), a separate 70-group variant of the original 71-group model. Original Discards (70) and Detritus (71) become **Pooled Discards and Detritus (70)**, with biomass **0.51582324 t/km²**. Groups 1–69 keep their source biology, source EE, fisheries and import shares. Their two detrital prey shares are summed without diet normalization. The runtime also contains synthetic diet-import group 71.

This is an interpretive summary. The complete direct returns, including all diagnostic fields and warning text, are retained separately and linked below. The engine's inherited short display label omits the scenario suffix; the canonical input hash and exact variant ID in [execution identity](outputs/run_identity.json) establish which model actually ran.

| Method | Overall | Input grade | Convergence grade | Recycling b | Living spectral radius | Pooled SPPR | PP-balance gap | PP-balance grade | Strict balanced flag |
|---|---|---|---|---:|---:|---:|---:|---|---|
| [GE](outputs/ge/diagnostic_report.json) | FAIL | FAIL | OK | 0.0293142743 | 0.412699240 | 1.385292244 | 0.0222165% | OK | false |
| [TE](outputs/te/diagnostic_report.json) | FAIL | FAIL | WARN | 0.0179918212 | 0.584593384 | 1.080632361 | 8.2443310% | FAIL | false |
| [With Egestion](outputs/with_egestion/diagnostic_report.json) | FAIL | FAIL | OK | 0.0271767451 | 0.330159392 | 1.440884838 | 0.7906302% | OK | false |

Each SPPR matrix has **71 recipient rows × 6 basal-source columns**. All contributions are finite; there are **zero negative entries** and **zero negative source columns** in every method. Both reported convergence conditions hold for every method (b < 1 and living spectral radius < 1). These facts do not override the overall FAIL grades. GE and With Egestion meet the diagnostic's coarse PP-gap grading threshold, but their stricter Boolean balance checks remain false.

The reported pooled SPPR is the pool's diagonal source contribution, `SPPR[70,70]`. Here it also equals the pool's all-source/inner row total because its other source contributions are zero; it is not its PP-only subtotal. Recycling b is the spectral radius of the resolved recycling matrix, and the living spectral radius applies to the consumer subnetwork.

TE flags near-zero efficiencies for **Tern (10), Gull&Cormorant (9), Fin whale (4), Common dolphin (3), and Bottlenose dolphin (1)**. Its nonzero recycling b is retained as returned: explicit internal fishery-discard recycling is present in this experiment.

## Remaining input-budget failures

All methods report maximum relative production residual **1.4776162288 (147.7616%)**, maximum relative consumption residual **0.0294506217 (2.94506%)**, and a failed strict model-balance check. The maximum production residual is Fin whale. Its retained discard removal is **0.0002808 t/km²/year**, while production is only **0.000190034526 t/km²/year**. With M0 and the external floor sink included, its production residual is **−0.000280798099655 t/km²/year**. No catch, production, living BA or source EE was repaired to hide that discrepancy.

The source diet rows also differ from one by up to **0.00043986418**. This is within the constructor's 0.001 admission tolerance but exceeds the stricter diagnostic threshold of 0.000001. Raw dietary shares were preserved.

The maximum consumption residual is **Loggerhead turtle (11), 2.94506%**. This diagnostic compares stored consumption with recomputed production plus egestion and respiration, so a production inconsistency can also appear in the consumption check.

These are findings for the stated translated runtime and its defaults; they are not proof that the author's native EwE model used the same unreported routing or initialization conventions.

## EE, M0 and pooled-flow checks

For all 69 living groups, effective **EE = 1 − M0/P** is verified to numerical tolerance. Here M0 is the production-derived non-predation mortality flow entering the pooled detritus after the floor diversion. Egestion and fleet discards are separate pool inflows. The identity does not by itself imply that all terms of the production budget balance.

| Group | Source EE | Effective EE |
|---|---:|---:|
| Bottlenose dolphin | 0.05 | 0.1 |
| Common dolphin | 0.01 | 0.1 |
| Fin whale | 0.00001 | 0.1 |
| Pelagic shark | 0.01941958 | 0.1 |

The total external mortality sink is **0.000670250768125 t/km²/year**. It stays outside the pool. Pooled input reconciles exactly as reduced M0 plus egestion plus fleet discards returned once:

- M0 plus egestion: **754.865418101701 t/km²/year**.
- Returned fishery discards: **0.0759254449376 t/km²/year**.
- Total pooled inflow: **754.941343546639 t/km²/year**.
- Consumption from the pool: **30.2059096649664 t/km²/year**.
- Remaining pool stock residual: **724.735433881673 t/km²/year**.

Total donor fishery removals remain **0.503896022935749 t/km²/year**; after returning discards internally, external fishery removal is **0.427970577998149 t/km²/year**. No fishery return was added twice.

The remaining stock residual is used by the engine to complete missing detritus biomass accumulation. It is **not an observed accumulation rate** and is not a newly invented external import. The canonical pooled EE remains unknown because the two source detrital EEs cannot be averaged meaningfully. The engine's effective detrital EE of 1 is a separately recorded runtime convention.

Other declared runtime assumptions are zero unlisted landings, zero missing living biomass accumulation/migration/detritus imports, and consumer GS = 0.2 (no small-zooplankton exception is present). Canonical missing values remain missing. No diet normalization, inverse-model repair, forced-balanced-state substitution or Monte Carlo run was performed.

## Review files and reproduction

- [Model departures and source links](../../../model_notes.md)
- [Plan](plan.md) and [aggregation ledger](aggregation_ledger.json)
- [Exact settings, environment and identities](outputs/run_identity.json)
- [EE and per-group flow reconciliation](outputs/living_ee_and_flow_reconciliation.csv)
- [Exactly-once routing reconciliation](outputs/flow_reconciliation.json)
- [Independent source-arithmetic check](independent_expected_flows.json)
- [Independent review](independent_review.json)
- [GE coefficients](outputs/ge/coefficients.csv), [TE coefficients](outputs/te/coefficients.csv), [With Egestion coefficients](outputs/with_egestion/coefficients.csv)
- [GE full return](outputs/ge/full_return.json), [TE full return](outputs/te/full_return.json), [With Egestion full return](outputs/with_egestion/full_return.json)
- [Reproduction entry point](code/run_diagnostics.py)

Two separately loaded initializations produced exactly equal tagged states; each diagnostic method was called once. The original model and the executed scientific files kept their checked hashes. The first bundled-Python launch failed before construction because SymPy was absent; the successful run used the existing Miniconda scientific environment, recorded in execution identity.

This variant is available for review as an **unselected, unpublished experiment**. No researcher decision was registered, and no regional workbook, Project.xlsx, map or trends were updated by this work. Numerical coefficients remain diagnostic evidence with FAIL restrictions.
