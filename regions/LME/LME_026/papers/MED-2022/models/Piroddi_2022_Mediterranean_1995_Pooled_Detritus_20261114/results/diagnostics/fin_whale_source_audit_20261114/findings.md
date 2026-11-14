# Fin-whale source check and pooled diagnostic interpretation

**Finding: no extraction error was identified in the fin-whale values.** The original spreadsheet, original canonical model, pooled canonical model and executed runtime agree on the reported biological parameters and fleet-discard quantities. No scientifically supported replacement value was found. Therefore the condition for correcting the pooled model and rerunning diagnostics was not met. This audit reuses the authenticated **EE floor ON at 0.1** returns from [the pooled experiment](../pooled_20261114/diagnostic_summary.md); it performs no new calculator construction or diagnostic solve.

## What the original sources contain

The [original XLSX supplement](../../../../../sources/41598_2022_18017_MOESM1_ESM-75e4d6d3.xlsx) identifies Fin whale as group 4. Its adjacent group names and identifiers confirm the row/column alignment.

| Quantity | Original source location | Retained value |
|---|---|---:|
| Biomass B | Basic input parameters!D8 | 0.008637933 t/km² |
| P/B | Basic input parameters!E8 | 0.022/year |
| Q/B | Basic input parameters!F8 | 7.249654/year |
| EE | Basic input parameters!G8 | 0.00001 |
| Fleet discards | Discards!F5:F41 | 0.0002808 summed |

The seven nonzero discard cells are F8, F18 and F27 = 0.0000144 each; F10, F20 and F29 = 0.000072 each; and F36 = 0.0000216. Other entries in F5:F41 are explicit zeros. They belong to seven distinct region-specific fleet rows, not duplicated rows introduced by extraction. The source has no fin-whale landings column; that missingness remains in both canonical models. The runtime explicitly assumes unlisted landings are zero and retains the reported discards once.

The workbook's discard caption specifies t/km² and the 1990s, without a separate annual suffix or area-weighting rule. The [DOCX supplement](../../../../../sources/41598_2022_18017_MOESM2_ESM-7d26163a.docx), S5, defines total catch as landings plus discards in t/km²/year, supporting the annual removal interpretation used in the run. The [paper's Methods](https://www.nature.com/articles/s41598-022-18017-x) describes a single whole-Mediterranean 1995 baseline with fleets divided among Western, Adriatic, Ionian and Eastern regions. That supports treating these as distinct fleet partitions, not four copies of the same whole-basin total. No documented alternative area conversion or fin-whale BA/migration value was found that authorizes a correction. Zero missing BA/migration remain explicit runtime assumptions, not recovered measurements. The DOCX supplies source-method references for fin whale, including by-catch, but does not establish a replacement value that resolves this discrepancy.

This conclusion distinguishes faithful extraction from compatibility of the published tables with the translated calculator. It does not establish that the author's native EwE model used the same unreported initialization, spatial conversions or flow conventions.

## Why fin whale fails the production budget

In the executed annual/common-area interpretation:

```text
P = B × P/B = 0.008637933 × 0.022 = 0.000190034526
Reported discards D = 0.0002808
D / P = 1.4776262288253872
```

Thus the reported discard quantity alone is **47.7626% greater than production**, before any natural mortality is added.

With the authorized floor:

```text
EE_effective = 0.1
M0_to_pooled_detritus = P × (1 − 0.1) = 0.0001710310734
External floor sink = 0.00001900155225474
M0_to_pooled_detritus + sink = original M0 = 0.00019003262565474
P − discards − M0_to_pooled_detritus − sink = −0.00028079809965474
```

Flows are t/km²/year under that runtime interpretation. The relative production residual is **147.7616%**, exceeding the engine's **10% FAIL threshold**. The formula **EE = 1 − M0/P holds**; it is not the failing check. The floor partitions the same original mortality between detritus and an external sink, so it cannot remove the existing catch/production mismatch. The return of fishery discards to detritus also does not undo mortality in the donor group.

## What fails or warns

All three methods return overall **FAIL**, because all inherit the same input-budget failure. Six groups exceed the 10% production-residual threshold:

| Group | Absolute relative production residual |
|---|---:|
| Fin whale | 147.7616% |
| Common dolphin | 84.2472% |
| Green turtle | 34.8729% |
| Loggerhead turtle | 27.4592% |
| Striped dolphin | 15.1402% |
| Bottlenose dolphin | 15.0747% |

Correcting fin whale alone, if a correction were justified later, would therefore not establish a passing model.

The maximum consumption residual is Loggerhead turtle, **2.94506%**. That contributes a warning under the component thresholds, not a separate >10% failure. The diagnostic recomputes consumption from recomputed production, egestion and respiration, so production discrepancies can propagate into it.

Diet sums deviate from one by up to **0.00043986418**. This passes the constructor's 0.001 admission tolerance but exceeds the diagnostic's 0.000001 criterion and adds a warning. Diets were not normalized.

TE also has a separate **8.244331% PP-budget gap**, above the 5% FAIL threshold. Its near-zero efficiencies in Bottlenose dolphin, Common dolphin, Fin whale, Gull&Cormorant and Tern add a warning; they are not evidence that recycling failed to converge. In the saved GE and TE formulations, the global budget gap can be reconstructed as production residuals weighted by each group's all-source SPPR. TE strongly amplifies the dolphin residuals. This simple decomposition does not reproduce With Egestion's gap and is not generalized to that method.

## What passes

| Check | GE | TE | With Egestion |
|---|---|---|---|
| Method returns a full numerical result | PASS | PASS | PASS |
| Finite SPPR contributions; no negative entries | PASS | PASS | PASS |
| Living network convergence (ρ < 1) | 0.412699 | 0.584593 | 0.330159 |
| Recycling convergence (b < 1) | 0.0293143 | 0.0179918 | 0.0271767 |
| PP-budget gap | 0.0222165% | 8.244331% | 0.7906302% |
| Coarse PP-budget grade | OK | FAIL | OK |
| Strict budget balanced flag | false | false | false |

The coarse PP-budget grade is OK up to 1%, WARN above 1%, and FAIL above 5%. The separate strict numerical balance test is tighter; therefore a coarse OK is not exact balance or an overall pass.

Other verified passes are:

- All 69 living groups satisfy effective EE = 1 − M0/P, with M0 delivered to the pooled detritus.
- The effective runtime has no EE outside [0,1] or near-zero EE issues.
- The floor's external mortality sink remains outside detritus.
- Fishery discards are removed from donors and returned to the single pool exactly once.
- Every method retains complete 71 × 6 SPPR matrices, 71 × 71 A/L matrices, masks, coefficients and diagnostic returns; saved coefficients reconcile to their source contributions.
- The original and pooled canonical inputs remain unchanged, and the source-cell and execution hashes match their retained evidence.

The positive pooled stock residual of **724.735433881673 t/km²/year** remains calculated detritus biomass accumulation, not a measured stock trend. These numerical and accounting passes do not establish ecological plausibility or researcher approval.

## Evidence and disposition

- [Exact source-cell comparison](source_cells.json)
- [Paper and DOCX context](paper_context.json)
- [Diagnostic thresholds, residuals and passing checks](diagnostic_checks.json)
- [Original pooled execution and full returns](../pooled_20261114/diagnostic_summary.md)

No model value, original report, selection, Project.xlsx entry, map, trend, or researcher decision was changed. No rerun was made because no extraction error was demonstrated. Resolving the remaining discrepancy requires authoritative clarification of the native model's fin-whale removals and unreported flow/initialization conventions, or a separately authorized parameter scenario; an arbitrary catch reduction, EE repair or invented balancing flow would not be an extraction correction.
