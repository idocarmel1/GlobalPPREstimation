# Regional provisional PPR integration

Reviewed 366 regions: 23 have selected models. Updated 11 regional workbooks; 343 unselected regions were preserved. 22 selected regions have numerical 2019 GE PPR. Existing model selections and rationales were preserved.

The user explicitly requested numeric SPPR, taxon-to-group mappings and PPR display before later model validation. New results use explicit provisional statuses. Diagnostic FAIL/WARN, strict balance failures and unresolved source or regional applicability remain visible. Numerical output is not an assertion that the model is scientifically valid. Negative contributions from failed methods are retained rather than silently discarded. Provisional outputs are excluded from validated common-catch comparisons.

## Updated regions

2019, GE, all sources, total catch (landings plus discards), existing method treatment of unidentified taxa. PPR is in tonnes carbon; source wet-mass PPR is divided by 9 exactly once.

| Region | Selected model | PPR (tC) | Catch coverage | Mapped catch labels |
|---|---|---:|---:|---:|
| EEZ_598 — Papua New Guinea | 941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods) | 4,899,070.58 | 0.6796% | 2 |
| EEZ_941 — Kiribati (Gilbert Islands) | 941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods) | 7,274,368.63 | 0.9028% | 2 |
| HS_071 — Pacific, Western Central | 941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods) | 3,772,892.07 | 0.4913% | 2 |
| HS_077 — Pacific, Eastern Central | 077HS_1_Eastern_tropical_Pacific_(1993-1997) | 83,035,026.17 | 48.2954% | 4 |
| LME_013 — Humboldt Current | 13_1_Chilean_Patagonia_(1980) | 41,071,101.26 | 67.2820% | 9 |
| LME_022 — North Sea | 22_20251990_East_Coast_of_Scotland_(1991-1995) | 23,495,811.45 | 85.7899% | 72 |
| LME_024 — Celtic-Biscay Shelf | Hernvann_2020_Celtic_Sea_1985 | 17,635,031.28 | 74.8007% | 127 |
| LME_027 — Canary Current | 27_118_Northwest_Africa_(1987) | 11,094,298.21 | 74.2119% | 292 |
| LME_029 — Benguela Current | BEN2020_Southern_Benguela_1978 | 7,742,064.47 | 6.2898% | 34 |
| LME_037 — Sulu-Celebes Sea | Bacalso2026_Visayan_Sea_1997_baseline | 4,902,213.84 | 12.0595% | 31 |
| LME_049 — Kuroshio Current | 49_2019201301_Watari_Detritus_Pooled_Experiment_(2013) | 8,730,857.02 | 20.6518% | 7 |

Catch coverage = catch tonnage with a usable mapped coefficient / total catch tonnage for the same region, year and catch basis. It is not the fraction of species, model area, or scientific validity. For HS_077: 415,664.8921 / 860,671.2076 × 100 = 48.2954%. The supported labels are skipjack, albacore, Pacific bluefin and Carangidae.

Unsupported size splits remain unresolved. Mesh and gear selectivity do not justify a blanket adult-only allocation. See [size-allocation research](SIZE_ALLOCATION_RESEARCH.md) for online evidence, the HS_077 size thresholds and a proposed mass-weighted allocation approach.

## Diagnosis and applicability flags

### EEZ_598

PARTIAL GE: selected experimental WCPO option1; direct WARN and strict balance false retained. Only explicitly supported dorado/wahoo catch; tuna stage weights unavailable. Fixed mixed-period surrogate coefficients, not annual ecosystem reconstruction.

- GE: WARN
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: WARN
- TE: strict input balance false
- TE: strict SPPR balance false
- With Egestion: WARN
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false

### EEZ_941

PARTIAL GE: selected experimental WCPO option1; direct WARN and strict balance false retained. Only explicitly supported dorado/wahoo catch; tuna stage weights unavailable. Fixed mixed-period surrogate coefficients, not annual ecosystem reconstruction.

- GE: WARN
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: WARN
- TE: strict input balance false
- TE: strict SPPR balance false
- With Egestion: WARN
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false

### HS_071

PARTIAL GE: selected experimental WCPO option1; direct WARN and strict balance false retained. Only explicitly supported dorado/wahoo catch; tuna stage weights unavailable. Fixed mixed-period surrogate coefficients, not annual ecosystem reconstruction.

- GE: WARN
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: WARN
- TE: strict input balance false
- TE: strict SPPR balance false
- With Egestion: WARN
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false

### HS_077

PROVISIONAL partial GE: historical selected runtime normalizes inconsistent source diets and infers BA. GE direct OK; TE FAIL. Source/ecological validation pending; four mapped labels only, 48.2954% of 2019 catch.

- TE: FAIL
- TE: strict SPPR balance false

### LME_013

Conditional Chilean Patagonia 1980 coefficients applied to exact member catches in Humboldt LME. Geographic mismatch remains unquantified. Retained runtime normalizes Sea lions diet1.002, solves residual BA for unknown BA, defaults consumer GS0.2/migration0, detritus B1 and routing; these are computational assumptions, not recovered observations. All three direct configurations WARN, strict computational balance true. Historical ecosystem unchanged across catch years.

- GE: WARN
- TE: WARN
- With Egestion: WARN
- Whole-region scientific validation pending

### LME_022

Partial results only. East-coast Scotland 1991–1995 coefficients applied to North Sea 1950–2019 catch, including discards although source model excludes them. Not a whole-region ecosystem reconstruction. Canonical source preserved; runtime diet normalization, GS defaults and residual BA completion documented. Unsupported catch stays missing.

- TE: FAIL
- Whole-region scientific validation pending

### LME_024

PROVISIONAL arithmetic for user-selected model; scientific validation deferred. source model balance FAIL; GE/With Egestion PP balance FAIL; authorized routing experiment; partial LME and stage coverage. Canonical model untouched; runtime evidence in models/Hernvann_2020_Celtic_Sea_1985/integration_20260928. Unmapped catch omitted; model-period coefficients over historical catch are not yearly ecosystem reconstructions.

- GE: FAIL
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: FAIL
- TE: strict input balance false
- With Egestion: FAIL
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false
- Whole-region scientific validation pending

### LME_027

Partial supported-catch GE subtotal; source composition comes from recovered 2008 precursor Table 1, not verified final 2009 inventory. EcoBase 118 source differs in period/version; no numerical source values replaced. Geography is broader offshore Northwest Africa, not exact LME boundary. Canonical source unchanged; selected loader bookkeeping documented separately.

- GE: WARN
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: WARN
- TE: strict input balance false
- TE: strict SPPR balance false
- With Egestion: WARN
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false
- Whole-region scientific validation pending

### LME_029

PROVISIONAL arithmetic for user-selected model; scientific validation deferred. source model balance FAIL; incomplete native stanza/BA representation; defaulted inputs; partial southern LME and stage coverage. Canonical model untouched; runtime evidence in models/BEN2020_Southern_Benguela_1978/integration_20260928. Unmapped catch omitted; model-period coefficients over historical catch are not yearly ecosystem reconstructions.

- GE: FAIL
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: FAIL
- TE: strict input balance false
- TE: strict SPPR balance false
- With Egestion: FAIL
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false
- Whole-region scientific validation pending

### LME_037

Conditional Visayan Sea1997 baseline applied to supported LME037 catch. Geographic fraction is unknown. Exact documented zero-import input and loader defaults retained: unknown diet imports0, living BA0, GS0.2, migration0, single-detritus routing, detritus EE0.44->1, detritus BA682.68614643. Diet unnormalized with DC_tol0.0021. GE/TE/Egestion WARN with strict input/budget balance false; TE Seabirds near-singular. These are conditional mapped-catch subtotals, not whole-region or source-balanced ecosystem claims.

- GE: WARN
- GE: strict input balance false
- GE: strict SPPR balance false
- TE: WARN
- TE: strict input balance false
- TE: strict SPPR balance false
- With Egestion: WARN
- With Egestion: strict input balance false
- With Egestion: strict SPPR balance false
- Whole-region scientific validation pending

### LME_049

PROVISIONAL UNVALIDATED: user authorized numeric display before scientific validation. Exact selected39-group detritus-pooled Watari2013 experiment and retained runtime reproduced. Seabirds missing living biomass defaults B=1 and PB/QB=0; GS/default completion, rounded-diet normalization, assumed common detritus routing, and residual-solved BA remain material. GE/Egestion overall OK are threshold grades only, strict SPPR balance false. TE overall FAIL: negative basal-source coefficients in unfished Seabirds and near singularity remain; negative group contributions are retained, not repaired or hidden. Only seven exact source members mapped; all others unresolved. Whole-region spatial suitability and species proportions are not validated.

- GE: strict SPPR balance false
- TE: FAIL
- TE: strict SPPR balance false
- With Egestion: strict SPPR balance false
- Whole-region scientific validation pending

## Remaining unavailable

- LME_026: unavailable. Selection retained; no numerical PPR invented.

## Verification

- 37 workflow tests passed, including signed provisional results, warning retention, missing-data gates, method-specific diagnostic schema and exports.
- All updated regional workbooks passed input/result freshness checks. Separate regional evidence retains exact runtime reproduction, matching reviews and independent annual arithmetic.
- Central paper/model metadata, unrelated regional records, selected IDs and rationales were preserved. Updated regional annual tables match the combined workbook.
- Generated map and trend evaluators independently match all 11 updated regions’ 2019 GE values and coverage, with one carbon conversion and visible provisional/diagnostic metadata.
- Full generated-page annual/NPP and fingerprint verification is recorded in html_verification.txt. Browser inspection is recorded separately in browser_verification.json.
- Representative regional workbook Overview rendering: LME022_overview.png. Original workbook backups and complete per-region evidence are retained.

## Evidence

- FINAL_INTEGRATION_VERIFICATION.json: central preservation, selected-region inventory, hashes and flags.
- generated_regions_verification.json: generated map/trend calculations.
- health_schema_verification.json: metadata-only diagnostic normalization.
- Other regions: other_regions_audit.md / .json; each changed LME has models/.../integration_20260928 or models/regional_ge_integration_20260928.
- HS_077 and WCPO: regional evidence folders; HS_077 PROVISIONAL_INTEGRATION.md supersedes earlier withholding notes while retaining their original audit findings.
- LME_022: models/regional_ge_integration_20260928/INTEGRATION_REPORT.md.

Final Project.xlsx SHA-256: `1d13e2bb422a5b63201dfff18121e3f5fd0ddc2c3c15a8dc63006bf767d67310`
