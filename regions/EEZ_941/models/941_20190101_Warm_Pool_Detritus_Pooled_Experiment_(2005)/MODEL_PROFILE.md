# Griffiths2019 pooled experiment versus WCP2007 option 1

**Pooling allows Griffiths2019 to run, but all three requested diagnostics return FAIL. WCP2007 option 1 (D_fixed_M0) remains WARN for all three.** Pooling therefore does not resolve the reason to prefer further examination of WCP option 1 over adopting this Griffiths reconstruction. Neither model has been selected.

| Direct method | Griffiths pooled overall | Griffiths PP budget; relative gap | WCP option 1 overall | WCP PP budget; relative gap |
|---|---|---|---|---|
| GE | **FAIL** | FAIL; 6.336529% | **WARN** | OK; 0.097858% |
| TE | **FAIL** | FAIL; 25.148312% | **WARN** | OK; 0.134701% |
| With Egestion | **FAIL** | OK; 0.159955% | **WARN** | OK; 0.024524% |

These are full direct `diagnose_sppr(TE_option=..., short=False, flat=False)` returns. No global method, annual PPR calculation, or model selection was performed. The original 46-group Griffiths model remains NOT_RUN_LOADER_BLOCKED because its two-pool routing is unknown. The table concerns only the separately authorized 45-group experiment. With Egestion's PP-budget status is OK under its threshold although its raw `is_balanced` flag is false; the overall model-input FAIL remains decisive.

## Why the pooled experiment still fails

The maximum production residual in the loaded normalized-diet experiment is **7128.367912%** of group production; the maximum consumption residual is **780.840301%**. All solves converge and produce zero negative source columns, but convergence does not validate the inputs. All three also warn about the living food-web amplification and near-zero seabird efficiency; GE and With Egestion warn about the recycling amplification.

The independent source-only equation already identifies the major contradiction: Pomfret production is 0.000294752 and production times EE is 0.0002800144 t/km²/year, while the exact final S3 diet implies predation 0.02128530003 before catch. Its source-equation residual is 7128.07195%. Large yellowfin consumption alone is about 19.92 times the printed Pomfret production. The small difference between this source residual and the diagnostic residual comes from documented runtime normalization; neither value was repaired. Source and loaded residuals should not be conflated.

Final S3 contains 46 prey by 42 consumers, with all 567 nonzero cells independently matching DOCX and rendered PDF coordinates. All 172 nonblank S4 fleet/total cells also match. Twenty-two printed totals disagree with their fleet components; exact components were retained, with total removals 0.033458867 t/km²/year. Main-paper ocean area is 11,543,000 km², while S1 catch derivations repeatedly use 12,086,900 km² and initial discard biomass uses 12,555,000 km². No density rescaling or catch repair was made. Initial diet S2 was excluded.

## What was authorized and what the loader did

The online routing review covered the publisher's sole Appendix S1–S4, author-posted appendix, primary institutional record, BMIS manuscript and EcoBase catalogue/native links. No recoverable exact-model numerical split was found in those available sources; this is a scoped finding, not proof of universal absence. Full URLs, findings and access limits are in `GRIFFITHS_ROUTING_SEARCH_20260928.md`.

Only source group45 Detritus and group46 Fishery discards were merged. Their known biomasses sum to **53.001775 t/km²**; each consumer's two prey proportions were summed exactly. All 42 original consumer diet sums and scalar biological/catch/taxonomy inputs are preserved in the experimental canonical, and both phytoplankton groups are unchanged. Pooled EE was left unknown, never averaged. The original 46-group canonical SHA256 remains `523cefaa423538f0609b96b75064594f426d87c8dca997a7973515792c1bafc3`.

The computational run uses the documented single-pool closed fate default, GS defaults, zero unspecified catches/imports, and normalized rounded diets, matching the benchmark's normalization convention. The first exact-diet runtime attempt is separately preserved: unknown synthetic import entries propagated NaN into basal-row detection and caused a KeyError before any return. The existing normalize_DC=True path resolves this without editing engine code. Every runtime diet change is recorded separately from source extraction.

The loader also sets detritus EE=1 and **replaces the source detritus BA=0 with derived accumulation**, approximately 416.710466 t/km²/year. Thus the successful run is a computational sensitivity model, not an exact steady-state reproduction. No source BA cell was changed. The pooled representation loses the separate suspended-discard pathway: routing applies natural other mortality plus egestion, and the engine does not separately return fleet discards to the pool. Catch export includes both retained and discarded removals. This limitation is not solved by pooling.

## Benchmark identity and regional choice

Option 1 is **D_fixed_M0**, not A_fixed_EE and not unchanged WCP2007. It preserves original juvenile other mortality while increasing juvenile production: small bigeye PB1.4129713563375232 / EE0.7898725981469387, small yellowfin PB2.5304972811160384 / EE0.8816702937266387. It remains an experimental correction without native multistanza validation. Its maximum production residual is approximately 0.727940% (adult bigeye); all PP-budget checks are OK. The exact saved direct returns were reused without rerunning WCP.

| Region | Griffiths source-domain target coverage | WCP2007 source-domain target coverage |
|---|---:|---:|
| HS_071 |29.09639%|57.57808%|
| EEZ_941 Kiribati Gilbert Islands |99.71577%|99.71577%|
| EEZ_598 Papua New Guinea |99.79181%|100.00000%|

These intersections use actual stored regional polygons and the stated study domains; evidence is in SPATIAL_OVERLAP.json. WCP-2007 already serves as a shared paper for EEZ_598. Later selection should review all three regions jointly. The EEZ_941 archive home is retained; it was chosen when comparing the first two regions, not as a claim that Papua New Guinea is less applicable. Only 9.07086% of Griffiths' reported ocean model area falls within EEZ_941 and 20.73849% within EEZ_598. These are broad pelagic proxies and do not establish coastal/reef representativeness.

For HS_071, WCP has substantially greater coverage, though neither spans the full target. For both EEZs, coverage is similarly high, and the present diagnostic evidence favors WCP option1 for further scrutiny. This is evidence for the user's later decision, not adoption. Do not rank the models by total PPR: their area, year, catch and group structure differ; Griffiths' returned footprints are outputs of a failed input model.

Allain2021 remains a separately archived 65-group, 2013 model. Its verified four-page report and associated context document lack the full numerical inputs required for reconstruction; it remains NOT_RUN, without substitution of older models. Its separately verified coverage is 74.48550% of HS_071 and 100% of EEZ_941; EEZ_598 applicability was not extrapolated.

## Reusable artifacts

Original Griffiths: `regions/EEZ_941/models/941_201901_Warm_Pool_(2005)` (46-group canonical, eight imports, taxonomy, cell evidence, source checks and original admission block).

Pooled experiment: `regions/EEZ_941/models/941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)` (45-group canonical, eight imports, taxonomy, canonical reconstruction, changes-only audit, full raw direct diagnostic JSON, frozen executed code, runtime transformations and preserved exception attempt).

The diagnostic JSON files contain only direct diagnostic output. Extraction, assumptions and comparison are separate. Previous blocked reports are preserved under `history_before_pooled_experiment`, alongside the pre-supplement history. No central workbook writes were made.
