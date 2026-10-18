# Execution and evidence scope

The 18 October TE successor adapts the historical analyzer into a new package. Historical results, reports and scripts are not overwritten. The successor consumes the new seven-pair cohort manifest, current published catch allocations and new upstream aggregation/SPPR studies after active review publication.

All pooled, within, between, per-model and leave-one-model-out regressions are refitted. Twelve conditional scenarios are recalculated from original allocation weights and saved coefficients. Sample counts are derived from upstream evidence and checked by a separate direct allocation enumeration. The independent verifier uses least-squares design matrices rather than the analyzer's demeaning formulas and verifies all refit classes and transported totals.

The report and figures are regenerated from these outputs. [Runtime and analysis checks](verification.json), [independent checks](independent_verification.json), [stdout](run_stdout.json) and [figure review](figure_review.json) record completed verification. The [cohort](../inputs/cohort.json) and [source ledger](../inputs/source_hashes.json) identify exact inputs. No production scientific engine call, input repair, model selection change, or mutation of a historical study is part of this package.

Scope remains 2019 catch including discards, all sources, unidentified treatment method, and the cohort's signed-review default exclusions. Numerical restrictions survive. These are conditional reconstructions and calibration sensitivities, not a claim of taxon-level model validation or measured global PPR.
