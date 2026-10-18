# SPPR and trophic level: seven validated pairs, 18 October 2026

This researcher-owned successor analysis uses the seven registered researcher-validated model-region pairs after the signed withdrawal of approval for `(LME_028, 28_646_Guinea_(1998))`. The [16 October eight-model study](../sppr_trophic_level_20261016/README.md) remains unchanged historical evidence. This package recomputes its descriptions and figures from retained saved coefficients; it does not run the scientific engine or change model inputs, workbooks, signed decisions or diagnostic eligibility.

The [cohort manifest](inputs/cohort.json) binds exact model identities to the current Project workbook and signed report hashes. It includes HS_077, LME_013, LME_032, LME_034, LME_035, LME_036 and LME_047. All 219 consumer groups remain in the data, including unfished groups and zero coefficients. Review-specific exclusions are applied by the downstream catch analysis, not by this all-consumer description. LME_027 remains a separate reference overlay and is not a member of the validated cohort.

## Results

- [GE and TE comparison](results/sppr_ge_te_side_by_side.png), with [SVG](results/sppr_ge_te_side_by_side.svg).
- [Four-method comparison](results/sppr_methods_side_by_side.png), with [SVG](results/sppr_methods_side_by_side.svg).
- [TE against trophic level](results/sppr_vs_tl.png).
- [All GE/TE/With Egestion group records](results/group_records.json), [model descriptions and LME_027 decomposition](results/comparison.json), and [four-panel values and restrictions](results/method_panel_data.json).

GE has 219 positive coefficients. TE has 218 positive coefficients and one zero, which remains in the data and is omitted only from logarithmic plots. EwE with final EE multiplication has 174 positive values, one zero and 44 unavailable Bay of Bengal values after the saved timeout. EwE without final EE multiplication has 219 positive values. No missing coefficient is imputed.

All plots retain `all` basal sources and the saved floor-enabled configurations with floor 0.1. Trophic level is `1 + log10(SPPR_1995_TE0.1)`, matching the saved cycle-broken, detritus-basal convention. The dashed fixed-10% chain is a comparison curve, not an ecological acceptance boundary. WARN, FAIL, provisional and other saved restrictions remain in the records; researcher validation does not approve transformed calculations. The LME_027 overlays and their feedback decomposition are unchanged diagnostic references.

## Evidence and reproduction

[Source hashes](inputs/source_hashes.json) identify current consumed bytes; [code derivation](inputs/code_derivation.json) records the unchanged predecessor scripts from which this successor was adapted. [Calculation verification](evidence/verification.json), [method-panel verification](evidence/method_panel_verification.json), [independent retained-row checks](evidence/source_subset_verification.json) and [visual inspection](evidence/figure_review.json) describe their separate verification scopes.

The independent check confirmed all 657 method/group records and 876 four-panel rows equal their retained historical counterparts, and all 165 newly recomputed catch-allocation group rows and seven regional rows agree individually. It checked 95 source hashes. These comparisons do not generate totals by subtracting an old aggregate. Five cohort-guard tests reject duplicate, missing, old eight-model and wrong-model identities.

From the repository root, with Python 3.11+, NumPy, SciPy and Matplotlib:

```powershell
python research/human/sppr_trophic_level_20261018_validated7/code/test_cohort.py
python research/human/sppr_trophic_level_20261018_validated7/code/analyze.py
python research/human/sppr_trophic_level_20261018_validated7/code/plot_method_panels.py
python research/human/sppr_trophic_level_20261018_validated7/code/plot_ge_te.py
```

Then reproduce the [new aggregation analysis](../../../regions/LME/LME_028/work/2026-10-18_121535_trophic_aggregation_validated7/README.md) before running `python research/human/sppr_trophic_level_20261018_validated7/code/verify_saved_subset.py`. The scripts reject a different exact review cohort and stale consumed sources. Deliberately changing sources requires a new study decision and fresh evidence; these commands overwrite only this successor's derived files. The retained 16 October package is never rewritten.
