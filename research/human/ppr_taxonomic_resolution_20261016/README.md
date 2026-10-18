# PPR at taxon resolution

Researcher-owned analysis requested on 16 October 2026, with agent assistance. This study explains in English how moving from Ecopath functional groups to catch taxa could change `SPPR_new` PPR under `TE_option='TE'`. It distinguishes an observed comparison, a conditional prediction, and the unresolved difference between either calculation and ecological reality.

The analysis extends the [SPPR and trophic-level experiment](../sppr_trophic_level_20261016/README.md) and the earlier [2019 aggregation decomposition](../../../regions/LME/LME_028/work/2026-10-16_202757_trophic_aggregation/outputs/decomposition.json). It uses saved coefficients and catch allocations. The original studies, canonical models, workbooks, researcher decisions, and diagnostic restrictions remain source evidence.

## Contents

- [English explanation and interpretation](report.md).
- [Analysis script](code/analyze.py) and [independent verifier](code/verify_independent.py).
- [Numerical summary](results/summary.json), [scenario table](results/scenario_totals.csv), and [regressions](results/regressions.json).
- [Conditional total PPR figure](results/conditional_totals.png) and [TL associations](results/tl_associations.png); SVG versions are in the same directory.
- [Source identity ledger](inputs/source_hashes.json).
- [Process record](evidence/process.md), [analysis verification](evidence/verification.json), and [independent verification](evidence/independent_verification.json).

## Main result

The same 2019 catch produces a reconstructed TE baseline of **8.039 billion tC**. Conditional taxon predictions give **11.355 billion tC** using a catch-weighted within-ecosystem slope, **12.562 billion tC** using the review-included slope, and **15.303 billion tC** using the all-consumer slope. These are respectively **1.412, 1.563, and 1.904 times baseline**. They include mean TL mismatch as well as Jensen curvature.

These values are sensitivity scenarios, not confidence bounds or identified expected true PPR. The projection assumes that a relationship measured between model groups also holds within those groups. It does not reconstruct taxon diets, efficiencies or feedback. The reconstructed baseline also retains the influence of finite coefficients whose saved annual results carry availability/implausibility restrictions.

## Reproduce

From the repository root, using Python 3.11+ with numpy and matplotlib:

```powershell
python research/human/ppr_taxonomic_resolution_20261016/code/analyze.py
python research/human/ppr_taxonomic_resolution_20261016/code/verify_independent.py
```

The analysis reads the saved experiment, current published catch-allocation payload and previous aggregation decomposition. It writes only this research package's derived outputs. The verifier independently reads the published coefficients, sums individual taxon allocations, and solves regression design matrices. Runtime identities and source hashes are recorded in `evidence/` and `inputs/`. No source models, scientific workbooks or published HTML are regenerated.

Numerical inputs must match the recorded source versions. If upstream data change, treat any verification failure as a reason to review and deliberately version the study; do not silently substitute a different cohort.

This is a research package, not a replacement for model-local scientific results. A regression over functional groups does not establish a species-level response, and a projected total does not confer scientific approval.
