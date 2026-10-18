# TE PPR at taxon resolution: current validated cohort

Researcher-owned successor analysis requested on 18 October 2026. It refits the TE taxon-resolution study for the 7 exact currently validated model-region pairs after withdrawal of Guinea 1998 validation. The [16 October study](../ppr_taxonomic_resolution_20261016/README.md) remains historical and unchanged.

The saved-coefficient baseline is **3.051529 billion tC**. Catch-weighted, review-included and all-consumer within-ecosystem projections are **6.208042**, **7.176716** and **9.525653 billion tC**. They are conditional scenarios, not uncertainty bounds or new scientific approvals.

- [Report and interpretation](report.md).
- [Exact cohort](inputs/cohort.json), [count expectations](inputs/sample_manifest.json), and [consumed source hashes](inputs/source_hashes.json).
- [Summary](results/summary.json), [all scenarios](results/scenarios.json), [regressions and LOMO fits](results/regressions.json), and [scenario CSV](results/scenario_totals.csv).
- [Conditional totals](results/conditional_totals.png) and [TL associations](results/tl_associations.png), with SVG companions.
- [Analysis verification](evidence/verification.json), [independent verification](evidence/independent_verification.json), [figure review](evidence/figure_review.json), and [process](evidence/process.md).

From the repository root, with the recorded scientific Python runtime:

```powershell
python research/human/ppr_taxonomic_resolution_20261018_validated7/code/analyze.py
python research/human/ppr_taxonomic_resolution_20261018_validated7/code/render_report.py
python research/human/ppr_taxonomic_resolution_20261018_validated7/code/verify_independent.py
```

Source versions must match the manifests. A changed cohort or dependency requires a deliberate successor or scoped rerun, not a silent fallback to historical results. These commands write only this study's derived outputs and never run the production model solver.
