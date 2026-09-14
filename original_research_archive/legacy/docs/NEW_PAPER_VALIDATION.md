# New paper to PPR validation

Completed 2026-09-07 for **Saygu et al. (2025), East Coast of Scotland, 1991-1995**. The archived paper was newly extracted in this pass; it had no production model JSON or SPPR workbook. The pipeline now has a reproducible extraction, taxonomy, SPPR, catch mapping and independently verified PPR result in a separate validation directory.

This completes the **computational integration test**. It does not establish a production-quality North Sea estimate: the paper covers part of the LME, its source parameters are rounded, two raw mass-balance checks remain ambiguous, and 15.9% of mapped catch rests on low-confidence inference. The validation model is absent from the shared top10 folder, model selection, atlas data and production ecosystem index.

## Deliverables

All paths below are relative to [`data/LME_022/validation/NS-2025_ECS-1990s/`](../data/LME_022/validation/NS-2025_ECS-1990s/).

| Artifact | Path |
|---|---|
| Final PPR workbook, 13 sheets | `evaluation/data/LME_022/models/22_20251990_East_Coast_of_Scotland_(1991-1995).xlsx` |
| SPPR workbook and run report | `sppr/` |
| Eight EwE import files, extraction/database JSON, round-trip workbook, Taxonomy.xlsx, report | `extraction/20251990_East_Coast_of_Scotland_1991-1995/` |
| Taxon mapping, source members, group dictionary, taxonomy, notes, fixed weights | `evaluation/data/LME_022/mapping/` |
| Source hashes and cell audit | `SOURCE_INVENTORY.json`, `VALIDATION_RESULT.json` |
| Independently checked scope calculations | `SCOPES_VERIFICATION.json` |
| Software-derived BA, GS and detritus flows | `LOADER_TRANSFORMATIONS.csv` |
| Reproduction and stage logs | `reproduce/run.py`, `logs/` |
| Regression evidence before health propagation | `baseline_before_health_fix/` |

The author supplies no EcoBase accession here. Model number `20251990` is explicitly an extraction-local identifier, formed from publication year and historical period; it is not a claimed catalogue accession.

## Source extraction

The source is [Saygu et al. (2025)](https://doi.org/10.3389/fmars.2025.1646031), archived under `PPRAtlas/archive/regions/LME_022/NS-2025/`. The main PDF, author XLSX supplement and DOCX formula supplement are present and hashed. There were no inaccessible listed supplements. The alternate Gan et al. (2025) Kuroshio-Oyashio bundle was inspected; its diet matrix uses many `+` values meaning <0.01, making it less suitable for an exact-value test.

The North Sea extraction preserves 25 functional groups, 23 consumers, 232 explicit diet cells and three fleets. PDF Table 1 on p. 6 was visually inspected at 220 dpi and extracted by bounding-box coordinates, using the right-hand 1990s parameter subcolumns. XLSX Table S1 supplies fleet landings, S2 group membership and S3 the diet matrix. A separate audit compared **650 spreadsheet slots**, including blanks, with the extraction. Source diet sums of **0.9996-1.0005** are retained in the import files.

All eight required EwE files exist. Structural validation reports **0 errors and 27 warnings**, because the paper does not report numerical GS, BA or detritus fate. The source database preserves `GS=-9999` and `BA=-9999`. All 25 taxonomy definitions reached `groups_df`; the exporter adds one external import group.

Two distinctions are preserved in the report:

- The existing database converter normalizes ten diet columns. The existing SPPR loader supplies biological defaults and solves missing BA while balancing rounded inputs. The audit lists these transformations; they are not attributed to the author.
- Standalone `massbalance_check.py` reports **1 error (Ling EE=1.003), 5 warnings and 24 notes**. The database converter's newer unknown-BA check reports **0 errors, 2 indeterminate groups and 3 warnings**. Turbot and Ling would reconcile within the rounding intervals of their printed B, but neither an adjusted B nor a suggested BA was inserted. The raw source remains unchanged.

## Catch mapping and coverage

The mapping uses the actual `LME_022` Sea Around Us catch archive: **384 taxa over 1950-2019**, totaling **208.301 million tonnes**. The member list was transcribed before mapping; it has 124 printed taxon names. The validator confirms **96 taxa and 81.2% of catch tonnage** against it, with **zero contradictions**.

| Confidence | Taxa | Share of catch |
|---|---:|---:|
| High | 113 | 81.8% |
| Medium | 138 | 1.9% |
| Low | 71 | 15.9% |
| Unresolved | 62 | 0.4% |

Total tonnage mapped is **99.597%**. Fourteen composites carry 15.7% of catch, using fixed catch-composition weights calculated from identified catch. The largest uncertainty is unidentified demersal catch allocated to the multi-species Flatfishes, Monkfish and Large Dem. fish pools. That wide candidate choice is marked low confidence; coverage is not evidence that its true composition is known. Deep-water fishes, tuna/billfish, freshwater/diadromous fish and other organisms lacking an appropriate source compartment remain unresolved. Important unresolved examples are roundnose grenadier, European eel and Atlantic bluefin tuna.

## SPPR, health and PPR verification

The safe `tools/run_sppr.py` wrapper generated **1/1 workbook**, with **20/20 methods returning**. `PPREstimation/create_PPRS_excel.py` was never executed from the shell, and no algorithm or Jensen code was changed.

| Diagnostic configuration | Status | Living-network spectral radius |
|---|---|---:|
| GE | OK | 0.212090 |
| TE | FAIL | 1.112778 |
| With Egestion | OK | 0.169672 |

The new-paper case exposed an integration defect: negative TE SPPR occurred in unfished source groups, so catch aggregation hid the problem and the first workbook selected `new_TE_EEfix` as its headline. The corrected shared builder now flags negative results in any source group and carries the matching upstream configuration diagnostic into method status. The raw pre-fix workbook is retained as regression evidence. The final workbook flags five affected methods; its automatic headline is **Ulanowicz_TE**, while the explicitly tested **new_GE** and **new_WithEgestion** configurations remain OK. The TE diagnostic is not asserted to grade other solver configurations or the accepted Monte Carlo draw subset.

The final workbook includes all, internal and primary-producer-only SPPR/PPR, plus a Recycling sheet. The repository verifier reports **1/1 workbook verified**. A second audit, which does not use the builder or its weight resolver, independently reconstructed fixed composite weights and compared:

- **23,040 taxon × method × scope cells** to upstream SPPR: maximum difference **0** at the saved six-decimal precision.
- **4,200 annual method × scope totals** across all 70 years to catch × scoped SPPR.
- All-source deterministic PPR and the Jensen comparison rows against the pre-fix baseline: unchanged. Monte Carlo values may vary on a fresh SPPR run.

The final isolated run also includes the corrected live Excel missing-value formulas. A small artifact-tool calculation workbook, `visual_checks/missing_formula.xlsx`, confirms that missing SPPR stays blank, a genuine zero stays zero, and an all-missing method total stays blank. Its rendered sheet was visually checked. The final North Sea Summary's **140 PPR/NPP cells** were independently checked against the 9:1 wet-weight/carbon conversion. The complete `--skip-sppr` pipeline was rerun after these formula changes; both source and scope audits passed with the comparison counts above unchanged.

For a computational example, the 2019 **new_GE** result is **257.586 million tonnes wet-weight-equivalent PP** for all/internal sources and **180.424 million tonnes** for primary-producer-only sources. These quantities use the whole-LME catch and the partial-area historical model. They are test outputs, not a scientifically adopted North Sea estimate. The simple unpartitioned 1995 method correctly stays unavailable in the PP-only model columns. NPP ratios use the existing 9:1 wet-weight/carbon conversion and identify the fixed 2019 denominator; the spatial and temporal applicability limitation still remains.

## Reproduce

From the checkout, run:

```powershell
python -X utf8 "data/LME_022/validation/NS-2025_ECS-1990s/reproduce/run.py"
```

This re-extracts the sources, generates the eight files and JSON, runs the one named SPPR model, prepares an isolated evaluation root, maps real catch, builds the PPR workbook and runs both verifiers. Stage logs and exact commands are saved in `logs/`. It expects and records the single known raw-source Ling mass-balance error; a different error fails the reproduction. `--skip-sppr` reuses the already generated SPPR workbook and was used to verify the final launcher and all downstream stages without drawing a new Monte Carlo sample.

The evaluation root contains copies of the small inputs and integration helpers it reads. `EVALUATION_INPUT_HASHES.json` identifies their versions. No result is copied into production selections or the colored pilot by this command.
