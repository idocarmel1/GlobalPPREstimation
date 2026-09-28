# North Sea conditional regional GE integration — 28 September 2026

**Superseding user instruction:** show traceable numeric SPPR as provisional PPR and flag diagnosis problems for later validation. All three direct methods now have explicit provisional Annual status; TE FAIL numbers are displayed as failed research previews, never relabeled valid. The earlier admission discussion below describes the initial integration before this instruction. `adopt_provisional.py` implements that later authorized display policy.
Selected model: `22_20251990_East_Coast_of_Scotland_(1991-1995)`. Overview selection and rationale are unchanged.

**2019, total catch (landings + discards), all sources, default unidentified treatment:** 23,495,811.450 tC/year (211,462,303.052 wet-weight-equivalent tonnes/year before division by nine). This is a supported-catch subtotal, not a whole-North-Sea estimate.

Mapping covers 72 of 384 catch labels and 2,331,134.612 of 2,717,260.698 total catch tonnes in 2019 (85.78988%). Unsupported coefficients remain blank. Full-region production_eligible remains false; method availability is based on reviewed direct diagnostic and numerical records.

## Source, computational state and admission

The canonical model.json hash is `5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691`. Canonical evidence and published values were not edited. `audit_runtime.py` verifies the retained executed-code hashes, loads an exact canonical copy with the recorded constructor, compares every loaded group field to the historical export, saves all calculator attributes to typed JSON, restores that saved state, and exactly reproduces full GE, TE and With Egestion diagnostic returns. Coefficients for each source scope agree with the retained export, joined by native group ID. The export helper uses a positional join that cannot safely consume a differently ordered direct return, so this integration explicitly reindexes direct coefficients by group ID. No engine change was made.

Constructor: normalize_DC=True, DC_tol=0.001, underdetermined=True, zero_biomass_accum=False; zero_catch=True, default_gs=True, flow/guess weights 1. Diagnostics: det_collapse_mode=never, det_external_sppr=0, det_open_mode=none, det_theta=1. These are the previously retained settings, not a newly introduced repair. Diet rounding is normalized, missing GS defaults to 0.2, unknown BA is completed from residual flows, and detritus EE/rates/defaults are engine transformations. The complete post-ModelData ledger and the earlier source-to-loader ledger remain distinguishable. All real living B/PB/QB/EE are published final values; no new living biomass placeholder was introduced. Computational BA is not measured biomass change. Source mass balance remains indeterminate for Turbot and Ling.

GE: OK, living spectral radius 0.2120896741, overall flow gap 0, zero returned warnings. With Egestion: OK. TE: FAIL, living spectral radius 1.1127784 and negative contributions including an unfished group. TE numeric coefficients and annual subtotals are retained as explicitly flagged provisional FAIL results under the superseding user instruction. No global or Monte Carlo run was performed.

## Mapping and geographic limits

The old mapping was reviewed against this exact selected model and the author XLSX Table S2, not accepted from its historical 99.597% coverage claim. That percentage included ecological analogues and unobserved composite weights. Sixty-nine exact source-member labels plus Argentina (source explicitly says Argentina sp.), common cockle and common whelk are retained. All accepted weights are 1 in a uniquely supported group. Representative Main Species lists support inclusion of named taxa but do not prove exhaustive composition. Other historical analogues, genus/family extensions and composite splits remain unresolved in this conservative result; this does not assert that every unlisted taxon is biologically excluded.

Cockle category identity: [WoRMS Cerastoderma edule](https://www.marinespecies.org/introduced/aphia.php?id=138998&p=taxdetails). Whelk category identity: [WoRMS Buccinum undatum](https://marinespecies.org/berms/aphia.php?id=138878&p=taxdetails). Source spelling Bussinum undatum is retained and not silently corrected in the model. Per-label accepted/rejected evidence and original assignments are in mapping_review.csv. Largest unsupported 2019 label is Marine fishes not identified, 318,308.913 tonnes; no composition weights are known.

The model describes East-coast Scotland shelf grounds, including Orkney/Shetland, rather than the whole North Sea. No validated overlap percentage is available. Catch mapping coverage is not geographic coverage. Fixed 1991–1995 coefficients across 1950–2019 catch do not reconstruct annual food webs. The source excludes discards; applying the coefficients to regional discards is an explicit removals-basis extrapolation and does not model discard recycling. No area scaling was applied.

## 2019 coverage by catch basis

| Basis | Supported tonnes | Total tonnes | Coverage |
|---|---:|---:|---:|
| landings | 2,207,345.770 | 2,573,903.418 | 85.759% |
| discards | 123,788.842 | 143,357.281 | 86.350% |
| catch | 2,331,134.612 | 2,717,260.698 | 85.790% |

## Verification and reproduction

Independent checks cover 3,456 weighted taxon coefficients, 17,010 annual cells across all methods/scopes/bases/unidentified treatments, and 34,020 PPR/NPP cells with division by nine exactly once. Total-catch PPR equals landings plus discards. Regional freshness validation passes. Catch, Classic PPR including historical sensitivity rows, NPP, selection and canonical JSON are preserved. The before workbook is retained.

Run `python regions/LME_022/models/regional_ge_integration_20260928/audit_runtime.py` to reproduce direct science and `python regions/LME_022/models/regional_ge_integration_20260928/verify_and_report.py` to verify the current regional workbook. `integrate.py` deliberately refuses to overwrite a newer workbook. Central/map verification is recorded in the project-wide integration report.

Files: runtime_verification.json; computational_state.json; direct_new_GE.json/.txt; direct_new_TE_EEfix.json/.txt; direct_new_WithEgestion.json/.txt; loader_transformations.json; mapping_review.csv; coverage_by_year_basis.csv; integration_verification.json.
