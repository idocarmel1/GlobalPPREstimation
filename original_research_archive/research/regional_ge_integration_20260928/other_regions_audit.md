# Other selected regions: GE integration and preservation audit

All current regional Overview selections inventoried; this worker excludes LME022,LME027,HS077. WCPO trio,LME024,LME029 delegated subsequently. No selection changes, source edits, global SPPR or Monte Carlo performed. Current regional snapshot; coordinating parent owns Project/map.

366 regional workbooks: 23 selected, 343 without a selected model. No new selections made.

2019, source_scope all, total catch landings+discards, unidentified treatment method; source wet-equivalent PPR divided by9 once. Provisional means numerical output pending scientific validation. Partial catch coverage is not geographic model coverage. Do not sum overlapping regions.

| Region | 2019 GE t carbon | Catch coverage | Numerical status / provenance |
|---|---:|---:|---|
| EEZ_598 | 4,899,070.576 | 0.68% | provisional: direct WARN; experimental surrogate; strict mass balance false; validation pending |
| EEZ_941 | 7,274,368.634 | 0.90% | provisional: direct WARN; experimental surrogate; strict mass balance false; validation pending |
| HS_071 | 3,772,892.069 | 0.49% | ok |
| LME_003 | 16,942,301.852 | 76.51% | ok |
| LME_013 | 41,071,101.257 | 67.28% | provisional: new_GE WARN; Patagonia-to-Humboldt geographic transfer; normalized diet and residual BA defaults; scientific validation pending |
| LME_014 | 6,490,048.075 | 65.31% | ok |
| LME_024 | unavailable | unavailable | no regional model output at this snapshot; see blocker/delegated work |
| LME_026 | unavailable | unavailable | no regional model output at this snapshot; see blocker/delegated work |
| LME_028 | 1,176,656,737.832 | 98.66% | ok |
| LME_029 | unavailable | unavailable | no regional model output at this snapshot; see blocker/delegated work |
| LME_032 | 264,764,335.903 | 98.81% | ok |
| LME_034 | 756,889,998.565 | 100.00% | ok |
| LME_035 | 22,572,463.866 | 99.98% | ok |
| LME_036 | 54,031,633.535 | 99.66% | ok |
| LME_037 | 4,902,213.843 | 12.06% | provisional: new_GE WARN; Visayan locality; documented import/BA/GS/routing defaults; strict input and budget balance false; scientific validation pending |
| LME_038 | 25,074,586.064 | 96.67% | ok |
| LME_047 | 26,990,183.867 | 100.00% | ok |
| LME_049 | 8,730,857.021 | 20.65% | provisional: GE overall OK; strict SPPR balance false; missing Seabirds B=1/PB=QB=0; scientific validation pending |
| LME_050 | 1,110,649.639 | 25.05% | ok |
| LME_052 | 1,151,857,971.590 | 98.05% | ok |

## Scientific limitations

- **EEZ_598**: WCPO Option1 mixed-period selected experiment: regional/provisional mapping handled by separate worker. Evidence class: retained recent selected evidence audited; no new model rerun.
- **EEZ_941**: WCPO Option1 mixed-period selected experiment: regional/provisional mapping handled by separate worker. Evidence class: retained recent selected evidence audited; no new model rerun.
- **HS_071**: WCPO Option1 mixed-period selected experiment: regional/provisional mapping handled by separate worker. Evidence class: retained recent selected evidence audited; no new model rerun.
- **LME_003**: Existing separately verified conditional author-equation reconstruction; retained GS/routing defaults, low-confidence unidentified demersal pooling and unknown geographic overlap. Partial mapped catch, not annual ecosystem reconstruction. Evidence class: retained recent selected evidence audited; no new model rerun.
- **LME_013**: Conditional Chilean Patagonia 1980 coefficients applied to exact member catches in Humboldt LME. Geographic mismatch remains unquantified. Retained runtime normalizes Sea lions diet1.002, solves residual BA for unknown BA, defaults consumer GS0.2/migration0, detritus B1 and routing; these are computational assumptions, not recovered observations. All three direct configurations WARN, strict computational balance true. Historical ecosystem unchanged across catch years. Evidence class: new exact-runtime replay and supported/provisional integration.
- **LME_014**: Existing selected native Falkland shelf2020 model; three direct configurations WARN and geographically local model. Partial mapped catch and fixed model over history; preserved rather than rerun. Evidence class: retained recent selected evidence audited; no new model rerun.
- **LME_024**: Selected configuration originally FAIL with explicit routed experimental numeric outputs; delegated provisional mapping/integration handled by separate worker. Evidence class: no regional model output at this snapshot; see blocker/delegated work.
- **LME_026**: Source construction NOT_RUN; no numerical coefficient may be invented. Selected identity retained, unavailable until source/constructor block resolved. Evidence class: no regional model output at this snapshot; see blocker/delegated work.
- **LME_028**: Geographic transfer from country Guinea111932km2 to Guinea Current LME;13 B/EE printed-source discrepancies retained. Low-confidence coarse allocation and source-supported synonyms remain assumptions. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.
- **LME_029**: Selected configuration FAIL; traceable numeric provisional integration delegated to separate worker. Evidence class: no regional model output at this snapshot; see blocker/delegated work.
- **LME_032**: Karnataka shelf27000km2 transferred to Arabian Sea LME. Mapping sources rederived previously, with estimated coarse-catch allocations, not published composition. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.
- **LME_034**: Whole-LME catch allocated across model geographical subregions2/3 using biomass/shelf-area proxies. Maldives region1 excluded.100% label assignment is not100% geographic/scientific validation. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.
- **LME_035**: MATERIAL IDENTITY WARNING: selected filename/year1963 actually contains1980 parameters (11/11 printed biomass values agree1980;10 differ1963).10-50m shelf to full LME transfer; no complete printed parameter table. Preserve identity warning. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.
- **LME_036**: Northern Chinese shelf(<200m) transferred to full South China Sea LME. Printed source numerical conflicts unresolved; coarse catch and stage selectivity proxies retained. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.
- **LME_037**: Conditional Visayan Sea1997 baseline applied to supported LME037 catch. Geographic fraction is unknown. Exact documented zero-import input and loader defaults retained: unknown diet imports0, living BA0, GS0.2, migration0, single-detritus routing, detritus EE0.44->1, detritus BA682.68614643. Diet unnormalized with DC_tol0.0021. GE/TE/Egestion WARN with strict input/budget balance false; TE Seabirds near-singular. These are conditional mapped-catch subtotals, not whole-region or source-balanced ecosystem claims. Evidence class: new exact-runtime replay and supported/provisional integration.
- **LME_038**: Explicitly user-authorized normalized/BA-completed Java Sea variant. Macrozoobenthos diet divided0.660,28 signed BA values computational not measured. Local area471000km2 transferred to LME; inherited stage/biomass proxies. Historical Monte Carlo exists but none run in this task. Evidence class: retained recent selected evidence audited; no new model rerun.
- **LME_047**: 2018 source membership feeding-guild model with coarse catch-composition allocations. Whole-LME coverage historically assumed without verified model area; no new scientific approval here. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.
- **LME_049**: PROVISIONAL UNVALIDATED: user authorized numeric display before scientific validation. Exact selected39-group detritus-pooled Watari2013 experiment and retained runtime reproduced. Seabirds missing living biomass defaults B=1 and PB/QB=0; GS/default completion, rounded-diet normalization, assumed common detritus routing, and residual-solved BA remain material. GE/Egestion overall OK are threshold grades only, strict SPPR balance false. TE overall FAIL: negative basal-source coefficients in unfished Seabirds and near singularity remain; negative group contributions are retained, not repaired or hidden. Only seven exact source members mapped; all others unresolved. Whole-region spatial suitability and species proportions are not validated. Evidence class: new exact-runtime replay and supported/provisional integration.
- **LME_050**: Prior direct/source review and exact/synonym-only mapping preserved; Kyoto coastal model yields25.05%2019 catch subtotal. Most whole-LME stocks unsupported; production_eligible false. Evidence class: retained recent selected evidence audited; no new model rerun.
- **LME_052**: Sea of Okhotsk NE is model identifier, not northeastern subregion. Printed consumer inputs agree; detritus biomass and full diet not independently source-verified. Pollock stages use model-biomass weights because model catch zero; composition proxy, not observed catch split. Evidence class: retained migrated results; current bytes/fingerprints audited, no new scientific revalidation.

## Checks and preservation

Every assigned selected workbook initially passed freshness validation and result fingerprint checks. Original Openpyxl Overview-only inventory is all_region_overview_inventory.json; fast independent XML inventory agreed selected identities. Existing high mapping coverage does not revalidate ecological assumptions. New integration evidence is within each changed regional models/regional_ge_integration_20260928 folder: backups, exact runtime state, source bytes, full direct returns, health grades, transformations, coefficients, all taxon decisions and verification. No Project.xlsx or map writes by this worker.

Unselected regions (343) remain explicitly categorized in JSON; no selection research was started.
