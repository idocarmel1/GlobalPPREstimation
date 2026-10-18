# Process and decisions

## Request

On 16 October 2026, the researcher requested an English replacement for the earlier explanation, a clearer and potentially more detailed derivation, inspection of `research/human/sppr_trophic_level_20261016`, emphasis on the total change in the desired true PPR rather than Jensen's inequality alone, and a dedicated record under `research/human`.

## Analysis design

1. Read the project README, current agent contract, research index, and referenced experiment. Use the canonical knowledge graph as a navigation aid only; its older snapshot does not certify the new experiment.
2. Inspect the source experiment's code, figures, definitions, coefficients, restrictions, and source identities. Its 261 consumer groups include unfished groups; 260 have positive TE coefficients suitable for a logarithmic fit. The original analysis describes a relationship but does not estimate a transport slope.
3. Retain the prior clean 2019 comparison: the same eight default selected, registered models, total catch, all source scope, unidentified treatment `method`, and signed-review default group exclusions.
4. Join the experiment to the 200 catch-bearing groups by ecosystem and group identity. Use the trophic level inverted from the actual saved fixed-10% coefficient; the ordinary displayed TL can follow a different cycle convention.
5. Estimate descriptive log-SPPR versus TL slopes with explicit sample and weighting choices. Separate pooled association from variation within ecosystems, and evaluate sensitivity to the ecosystem used for calibration.
6. Apply conditional taxon predictions anchored to each group's saved coefficient. Separate mean-TL displacement, within-group convexity, and the unresolved change in network properties. Do not interpret the regression association as an experimentally identified species-level slope.
7. Compare resulting total PPR to the current new-method total, the grouped classical total, and the taxon simple-chain total. Examine contributions and influential groups, preserving finite values and their diagnostic restrictions.
8. Independently reconcile arithmetic, check source hashes, inspect figures, and review the explanation for unsupported claims about true or global PPR.

## Independent preliminary check

Before the expanded analysis, the coordinator recomputed the fixed-slope scenario directly from the previous per-group results. With base-10 slope `b=1`, the mean-shift-only factor is 0.963230753405054, the incremental within-group Jensen factor is 1.313821819506947, and their product is 1.2655135810436755. Baseline PPR is 8,038,956,733.758991 tC and the projected PPR is 10,173,408,923.99451 tC. These are conditional calculations over the selected cohort, not new model solves or global estimates.

The mean-shift factor is below one under new-method PPR weights, despite the classical centering factor being above one. This demonstrates why a single factor from a different method cannot simply be multiplied into the new-method total.

## Scope of interpretation

All calculations retain `TE_option='TE'`, the saved floor-enabled configurations and their other recorded assumptions. Selection and researcher registration are separate from the validity of a transformed method result. A greater SPPR coefficient is not evidence that an estimate is closer to truth.

The estimate sought is the PPR of the same catch under a defensible finer-resolution food web and the same accounting convention. Unknown within-group diets, efficiencies, flows, selectivity, and network feedback are not filled in as facts. No inference about the world is made solely from the eight-model cohort.

## Completed calculations

The source experiment's 200 catch-bearing groups matched the allocation study exactly. The evaluation contains 2,018 region–taxon records, 3,089 allocated taxon–group rows, and 44,153,491.4524133 tonnes of catch. No positive-catch coefficient was missing. Fifteen descriptive regressions, twelve conditional total scenarios and eighty leave-one-ecosystem-out calculations were saved.

The current group-coefficient reconstruction is 8.038956734 billion tC. The all-consumer within-ecosystem slope is 1.374115 and gives 15.303431738 billion tC, a factor of 1.903659. Applying review exclusions to the calibration sample gives slope 1.216247 and 12.561549372 billion tC, a factor of 1.562585. The catch-weighted within-ecosystem slope is 1.121099 and gives 11.354870653 billion tC, a factor of 1.412481. These all evaluate the same catch; the calibration choices differ.

The PPR-weighted regression is retained as a clearly labeled stress test. It gives factor 4.904359, illustrating strong sensitivity to outcome-based weights and extreme coefficients. It is not selected as the best estimate. Leave-one-model-out ranges are explicitly sensitivity checks, not confidence intervals or validation of taxon-scale transport.

Guinea contributes 62.04% of the reconstructed TE baseline. Its deep large shark/ray group alone contributes 38.70%. The report makes the saved annual implausibility restriction explicit: numerical reconstruction from finite group coefficients does not make an unavailable annual TE result valid or approved.

## Independent verification and review

The main analysis checks its direct per-taxon sums against the group mean-shift × Jensen decomposition. A separate [verification implementation](../code/verify_independent.py) independently parses the current published HTML coefficients and allocations. It does not import the analysis module or reuse its transported group outputs. It also fits the ten pooled/within-ecosystem regression slopes using weighted design matrices and `numpy.linalg.lstsq`, rather than the main analysis's centering formulas.

All **62 numerical checks** passed. The largest relative disagreement was **4.93 × 10^-15**. All **38 input-source hashes** matched the ledger. The independent verifier also checks local links in the README, report and process record. Its first run reached the link check and found that the README referenced the verification record before it had been written; the verifier now recognizes its own pending output. This bookkeeping correction did not affect numerical results.

Both scientific figures were visually inspected for label overlap, clipping, legibility and correspondence to their numerical tables. The review-included scenario is visible in the totals figure. The PPR-weighted stress test has a separate grey hatched style. The baseline is labeled as a reconstruction so that the figure does not imply approval of a saved annual TE result.

An independent mathematical review checked the derivation, examples, sequential total factors, availability wording and interpretation of true PPR. It prompted one clarification in two places: the anchored prediction retains the group's multiplicative departure from the TL relationship; it does not construct a disaggregated network or enforce flow balance. No further scientific corrections were identified.

The analysis used the existing `FishEstimation` Python environment for numpy/matplotlib; the independent numerical verifier used the bundled Python runtime. No packages were installed. No scientific solver was run. Writes were confined to this dedicated research package and its entry in the research index; pre-existing workspace edits were preserved.
