# GE PPR at taxon resolution

Researcher-requested replication of the [TE taxon-resolution pipeline](../ppr_taxonomic_resolution_20261016/README.md), using `SPPR_new` with `TE_option='GE'` and the saved `new_GE` coefficients. The study was requested on 16 October 2026 and completed with agent assistance. Placement under `research/human` describes ownership, not scientific approval.

The comparison retains the same eight selected reviewed models, 2019 catch including discards, `all` source scope, unidentified treatment `method`, default review group exclusions, original taxon allocation shares, reference taxon TLs, and operative model TLs. GE coefficients and GE-fitted slopes replace the TE quantities. Model-specific saved configurations and diagnostic restrictions remain in force.

## Main findings

| Calculation | GE PPR, billion tC | Factor over GE baseline |
|---|---:|---:|
| Reconstructed group baseline | 2.026 | 1.000 |
| Unit slope `b=1` | 2.686 | 1.326 |
| Catch-weighted fit within ecosystems | 2.465 | 1.217 |
| Review-included fit within ecosystems | 2.629 | 1.297 |
| All-consumer fit within ecosystems | 2.907 | 1.435 |

The main within-ecosystem scenarios imply **22–43%** additional GE PPR, compared with **41–90%** under the corresponding TE scenarios. The review-included GE projection is **1.448 times grouped classic** and **0.830 times taxon simple chain**. All twelve scenarios, including pooled fits and PPR-weighted stress tests, are retained in the report and results. Scenario ranges are not confidence intervals for true PPR.

GE's lower total reflects different saved coefficients, different PPR contribution weights and lower fitted slopes. At the common fixed slope `b=1`, each group's TL correction is identical to TE's, but the aggregate GE correction is larger because its group weights differ. The lower fitted GE adjustments must not be interpreted as a universal inequality between the two methods.

The GE source has 261 positive consumer coefficients; the review-included sample remains 241 and the catch sample 200. Guinea GE is diagnostic OK, while Northern Humboldt retains a GE FAIL and production-ineligible provisional restriction. Numerical reconstruction does not remove those restrictions.

## Contents

- [Results and mathematical interpretation](report.md).
- [Analysis script](code/analyze.py) and [independent verifier](code/verify_independent.py).
- [Numerical summary](results/summary.json), [scenario table](results/scenario_totals.csv), and [regressions](results/regressions.json).
- [GE–TE comparison](results/ge_te_comparison.json) on identical catch and TL support.
- [Conditional totals](results/conditional_totals.png) and [TL associations](results/tl_associations.png), with SVG companions.
- [Source hashes](inputs/source_hashes.json).
- [Process record](evidence/process.md), [analysis verification](evidence/verification.json), and [independent verification](evidence/independent_verification.json).

## Reproduce

Run from the repository root with Python 3.11+, numpy and matplotlib:

```powershell
python research/human/ppr_taxonomic_resolution_GE_20261016/code/analyze.py
python research/human/ppr_taxonomic_resolution_GE_20261016/code/verify_independent.py
```

These scripts read existing saved results; they do not run the scientific calculator, modify model inputs or regenerate published views. The analysis writes derived outputs only inside this study. The verifier independently sums taxon allocations and fits regression design matrices. All totals are diagnostic reconstructions or conditional projections, not newly approved annual results or measured world totals.

The source experiment is [SPPR and trophic level](../sppr_trophic_level_20261016/README.md). The full interpretation of the anchored projection and its identification limits is retained in the TE report, and repeated for GE in this study's report.
