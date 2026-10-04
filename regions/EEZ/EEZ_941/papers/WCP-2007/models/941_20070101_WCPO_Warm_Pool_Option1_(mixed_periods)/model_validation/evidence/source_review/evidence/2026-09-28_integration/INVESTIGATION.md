# Selected WCPO option 1: limited regional GE integration

Saved direct returns are also flattened into each workbook's standard `Diagnostics / model_health` table by `normalize_health_tables.py`, without solving again. This preserves the full separate reports while exposing b, living-loop rho, overall/component grades and strict Boolean flags to the existing map adapter. `health_table_verification.json` checks that numeric inputs/results are unchanged by this metadata-only step. Run this normalization after replaying either integration script.

The user-selected experimental `941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)` is retained unchanged for Kiribati (Gilbert Islands), Papua New Guinea and Pacific Western Central high seas. This integration uses only two supported catch labels, **Coryphaena hippurus** and **Acanthocybium solandri**, both assigned with weight 1 to the source's `Piscivorous fish` group. It does not estimate a whole-region PPR total.

| Region | 2019 supported GE subtotal, all sources and total catch, tC | Supported catch, tonnes | Catch coverage |
|---|---:|---:|---:|
| EEZ_941 | 7,274,368.634222077 | 5,416.5260233694 | 0.9028103126% |
| EEZ_598 | 4,899,070.575850021 | 3,647.8689215140 | 0.6796044491% |
| HS_071 | 3,772,892.068520713 | 2,809.3115842887 | 0.4912948933% |

Regional workbooks hold annual 1950–2019 coefficients, supported-catch PPR, catch denominators and coverage numerators for all/inner/PP source scopes, landings/catch/discards and the existing unidentified treatments. Carbon above is wet-weight-equivalent PPR divided by nine once. Two labels are resolved among 63, 102 and 23 respectively. The remaining labels have explicit unresolved rows; unidentified treatment does not create source-supported matching. These are small partial subtotals and must not be presented as complete regional estimates.

## Why these two assignments

Allain et al. (2007), Table 1 (PDF p9), lists Coryphaenidae and explicitly names wahoo Acanthocybium solandri in Piscivorous fish. The retained taxonomy has all 31 canonical groups, exact source group identifiers, representative-list qualifiers and size definitions. [ITIS TSN 168791](https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=0168791), consulted 2026-09-28, places Coryphaena hippurus in Coryphaenidae. No separate source size pool for these named piscivores is specified.

BET and YFT have distinct adult/juvenile groups; SKJ has three stages. Billfish and sharks also have large/small groups. No region-year catch size allocation is supplied. Model biomass, its mixed-period catch proportions or equal weights do not establish regional-year allocation and were not used. Carangidae and Scombridae span source groups, while epipelagic families have separate larval/juvenile pools; benthic coastal catches do not automatically belong to a pelagic model. Broad labels and unverified memberships remain unresolved. Source example lists are not treated as exhaustive exclusions.

## Exact selected runtime and scientific admission

All three regional selected JSON files match SHA-256 `328330dc06ed3e96462995f1a04c1bdaa9747468af8bb4d9e4f57196b9cc1b03`, the previously tested D_fixed_M0 input. Original canonical source, extraction/import tables, balance evidence, scenario changes and selection provenance remain in each model directory and in EEZ_941's WCP-2007 source bundle. This selected variant is explicitly authorized in the existing selection rationale: juvenile BET and YFT P/B and EE were changed to preserve their original other-mortality flows. No new repair, pooling, selection or numerical tuning was introduced by this integration.

The historical constructor settings were reproduced exactly: underdetermined=True, zero_catch=True, zero_biomass_accum=False, default_gs=True, weight_flow=weight_guess=1, DC_tol=0.001, normalize_DC=True. Source rounded diets are normalized in this already adopted computation, unknown catches and migration become zero, missing BA becomes inferred residual accumulation, and detritus EE and routing have documented loader conventions. No real living group has biomass imputed in this final variant. The full before/after state and transformation ledger distinguish source and runtime quantities. Inferred BA does not become observed stock change, and this independent-group calculation does not verify native EwE multistanza equations.

Fresh direct diagnose_sppr returns for GE, TE and With Egestion all remain **WARN**, exactly as the selected scenario evidence states. The strict input mass-balance flag remains **false**; maximum production relative residual is 0.007279402209226768 (adult BET, 0.727940%). GE PP-budget component grade is OK, relative gap 0.0009785787909092304; its strict Boolean flag is separately preserved. Every biological GE source contribution was checked nonnegative, including unfished groups. Retained historical full coefficient matrices match the new calculations at rtol 1e-12 / atol 1e-10. A second load of the persisted input yields exactly equal group and diet tables. GE is admitted only as the explicitly selected, disclosed experimental-surrogate calculation. All annual method statuses start with provisional: so the map can display traceable numeric outputs without treating them as reviewed. GE, TE and With Egestion are all integrated with direct WARN retained. The user explicitly requested provisional display before later scientific validation.

The full direct return objects are in `direct_diagnostics.json` and `DIRECT_DIAGNOSTICS.md`; interpretation is confined to this file and workbook review blocks. There was no Monte Carlo or broad exporter run.

## Geography, time and preservation

The source is the broad pelagic WCPO warm pool (110–180°E, 15°N–15°S), with mixed observation/assessment periods. It is a surrogate for all three regions, not a region-specific native model or a reconstruction of annual ecosystem change. Region-specific geographic intersections already retained in SELECTION_AND_PROVENANCE.json were not changed or confused with catch-tonnage coverage.

`reproduce_and_integrate_wcpo.py` provides the bounded reproduction/adoption path. `engine_snapshot/`, saved exact input, direct matrices, loaded state and `runtime_verification.json` retain scientific execution evidence. Each region's `evidence/2026-09-28_integration/` contains its original workbook backup, exact taxonomy copy, full matching table and result summary. Before computing, inputs are persisted and re-read so calculated fingerprints refer to the Excel-stored precision. Existing Catch, Classic PPR and NPP blocks are verified identical; old classic ratio rows are retained. Model identity and selection rationale are unchanged. All three regional validation checks passed. No shared tool, Project.xlsx or map file was changed.
