# Discards divided by ten: pooled model sensitivity

**Result: all three methods still return overall FAIL.** Five of the six flagged groups remain above the 10% production-residual threshold. This is a user-authorized hypothesis, not a source correction.

Only discards for groups 1, 2, 3, 4, 11 and 12 were divided by ten. Their donor catch and single-pool returns were reduced together. All living biological parameters, diets, 100% pooled routing, EE floor ON at 0.1 and the external mortality sink were retained. The original and pooled canonical models were not changed.

## Production-budget changes

| Group | Baseline absolute discrepancy | Discards / 10 | New direction |
|---|---:|---:|---|
| Bottlenose dolphin | 15.0747% | 2.9925% | outflow deficit |
| Striped dolphin | 15.1402% | 56.1064% | outflow deficit |
| Common dolphin | 84.2472% | 24.0773% | outflow excess |
| Fin whale | 147.7616% | 14.7753% | outflow excess |
| Loggerhead turtle | 27.4592% | 88.2459% | outflow deficit |
| Green turtle | 34.8729% | 92.5873% | outflow deficit |

Bottlenose dolphin falls below the 10% failure threshold, but remains above the warning threshold. Fin whale and Common dolphin improve but still fail. Striped dolphin and both turtles worsen because their total production outflows were already too small; reducing discards increases that deficit. No other living group exceeds 10%.

Fin-whale discards after scaling are 0.00002808 t/km²/year, below production of 0.000190034526. However, its retained M0 plus floor sink already consumes almost all production, so the remaining catch still produces a 14.7753% discrepancy. EE = 1 - M0/P continues to hold; it does not force the rest of the production budget to close.

## SPPR diagnostic changes

| Method | PP-budget gap: baseline → sensitivity | PP-budget grade: baseline → sensitivity | Overall |
|---|---:|---|---|
| GE | 0.0222% → 0.8595% | OK → OK | FAIL |
| TE | 8.2443% → 4.5093% | FAIL → WARN | FAIL |
| With Egestion | 0.7906% → 1.0935% | OK → WARN | FAIL |

All strict budget-balance flags remain false. The largest consumption residual rises from 2.9451% to 9.4646%, still below the 10% failure threshold. The small diet-sum warning is unchanged. TE retains its near-zero-efficiency warning.

## Model-catch PPR and coefficient changes

These are all-source PPR values for the model’s own catch density, in the model mass basis per km²/year. They are diagnostic footprints, not recalculated regional catch time series or eligible published estimates.

| Method | Baseline PPR | Sensitivity PPR | Relative change | Largest living-group SPPR coefficient change across all/inner/PP |
|---|---:|---:|---:|---:|
| GE | 107.474617 | 97.786622 | -9.0142% | -0.925472% |
| TE | 554.267469 | 411.342098 | -25.7864% | -16.747684% |
| With Egestion | 40.005891 | 36.677443 | -8.3199% | -0.307809% |

The catch-weighted PPR decrease combines lower discards with altered all-source SPPR coefficients; the two effects should not be conflated. PP-only SPPR coefficients are exactly unchanged for every group and method. The largest living all/inner coefficient decrease occurs in Mobile benthos (group 61). Complete group/scope coefficient comparisons are in [comparison.json](comparison.json).

## Accounting, evidence and limits

- All three methods returned full numerical results using the same five pinned engine/serialization files as the baseline.
- SPPR contributions remain finite and nonnegative; all returned matrices remain finite and recycling converges. These are numerical checks, not ecological validation.
- All living effective EE values, M0 and external mortality sink amounts are unchanged; EE = 1 - M0/P is preserved.
- Total discard returns fall from 0.0759254449376 to 0.0752188642616 t/km²/year. Total catch falls from 0.5038960229357493 to 0.5031894422597494; external landings remain 0.4279705779981493.
- The floor sink remains 0.000670250768124695 t/km²/year. The calculated pool stock residual decreases with the discard reduction; it remains a runtime balance quantity, not an observed biomass trend.
- No model, workbook, DOCX, selection, Project.xlsx, map/trends or researcher decision was updated.

[Scenario plan](plan.md) · [Exact comparison](comparison.json) · [Independent numerical audit](independent_review.json) · [Execution summary](outputs/summary.json) · [Evidence index](evidence_index.json) · [Completeness](completeness.json)

[Baseline diagnostics](../pooled_20261114/diagnostic_summary.md) · [Original source check](../fin_whale_source_audit_20261114/findings.md)
