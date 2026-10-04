# Provisional Southern Benguela SPPR-to-catch integration, 2026-09-28

Numeric SPPR-to-catch mapping and display were requested before later scientific validation. Annual statuses explicitly remain **provisional**, all direct diagnostics remain **FAIL**, and full-region `production_eligible` remains false.

2019, all sources, total catch (landings plus discards), unidentified treatment `method`:

| Numeric method | Supported-catch subtotal, tC |
|---|---:|
| GE | 7,742,064.465583207 |
| TE | 16,298,034.09218465 |
| With Egestion | 2,539,142.800910817 |

Only **100,165.7790733005 of 1,592,518.0818040827 wet tonnes (6.289773423472076%)** are mapped. There are 34 mapped labels among 247 historical labels. These low-coverage subtotals must not be read as estimates for all Benguela catch. Unmapped catch is omitted, not assigned a zero coefficient. The dominant unresolved labels include unidentified marine fish, Trachurus capensis, Merluccius, Sardinella and Engraulis capensis. Fixed 1978 coefficients applied across historical catches do not reconstruct annual ecosystems. The calculation converts wet-weight-equivalent PPR to carbon by division by nine exactly once.

## Exact numerical configuration

The canonical selected model remains unchanged. The calculation uses the already retained `diagnostics/29_20201978_Southern_Benguela_PQ_completed_(1978).json` copied byte-for-byte here. This is a separate computational completion: two missing deep-water-hake P/B values are derived from published P/Q × Q/B (2.00375 and 0.799). It is not a new parameter adjustment, a substitution of Z for P/B, or a claim that canonical unknowns are now published inputs.

Constructor settings reproduce the preceding extraction review exactly: `underdetermined=False`, `zero_catch=False`, `zero_biomass_accum=True`, `default_gs=True`, `normalize_DC=False`, `DC_tol=0.001`. Both default weights are 1. LME metadata is explicitly set to 29 as in the retained run. The existing defaults fill unknown BA, 40 unknown consumer GS values, migration/import values and one-pool routing; printed sardine and rock-lobster BA, the five source-supported GS=.35 values and diet sums 1.0001/1.0002 are retained. Detritus EE is forced to one and residual detritus BA is derived by the existing loader. No new repair, pooling or source-value change occurs here.

`reproduce_direct.py` uses the retained three-file engine snapshot and the persisted computational copy. Two independent reloads have exactly equal captured state, flows and all direct returns. The new GE, TE and With Egestion returned objects also exactly equal the earlier `diagnostics/*_direct_return.json` objects; the loaded group table reproduces the earlier `loaded_groups.csv`. Source-decomposed solutions and identity-aligned coefficients are retained for all three methods. No global, broad inventory or Monte Carlo was run.

All three overall and model-input grades are FAIL. The maximum production relative residual is **0.23960893055555557**; maximum consumption residual is **0.023242318055667854**. All direct coefficient matrices have zero negative source columns. GE divergence grade is OK and PP-balance grade OK, but the strict Boolean is false and relative gap is **0.0004852725961139777**. TE's PP-balance relative gap is **0.09618197517629808**; With Egestion's is **0.0004254579512667005**. Small PP gaps do not override the source mass-balance failure. Native multistanza/sardine stock-accumulation interpretation remains unresolved; these diagnostics do not prove that the author's native EwE model is invalid.

## Taxonomy, life stages and location

The selected source extraction already crosswalked main Table 1 to the numeric Table 2/S4 order and retained supplement S2's named examples. This integration uses those explicit members, not an inference that the example lists are exhaustive. Specific species take precedence over a generic genus example. Agulhas sole goes to its dedicated group, following the documented main-table priority over the overlapping S2 example.

Two transparent orthographic crosswalks are retained in each relevant matching explanation: source `Etrumeus whiteheadii` to accepted `Etrumeus whiteheadi` (ITIS TSN 551211; FAO https://www.fao.org/4/ac482e/ac482e08.pdf), and source `Trichuiurus lepturus` to `Trichiurus lepturus` (WoRMS AphiaID 127089, https://www.marinespecies.org/CaRMS/aphia.php?id=127089&p=taxdetails). Source spelling is not overwritten. The distinct Panulirus homarus/Palinurus gilchristi conflict for South Coast rock lobster is not treated as synonymy and remains unresolved.

Anchovy, sardine, horse mackerel and hake have juvenile/adult groups. No regional size/age allocation weights were supplied. These catches remain unresolved; native model stage biomass/catch proportions are not imposed on the full LME across years. Genus labels that span documented groups likewise remain unresolved. The full mapping, explanations and yearly catch coverage are retained in the workbook and `matching_review.csv`.

The model represents 220,000 km² of the **southern** Benguela, from Orange River to East London. The whole-LME catches include the northern system. No 50% rectangle-based coverage claim or spatial correction is applied. Large unmapped northern catches are therefore a model-scope limitation as well as a taxonomy limitation.

## Preservation and validation

`LME_029_before_integration.xlsx` preserves the original workbook. Catch, Classic PPR, NPP, existing classic ratios, selection/rationale and canonical bytes are verified unchanged. The standard regional calculation generates provisional annual values, taxon coefficients and ratios; its normal freshness hashes describe the saved state. `integration_verification.json` records values, hashes, preserved blocks, coverage and unresolved catch, with successful regional validation. `reproduce_direct.py` followed by `integrate.py` reproduces the work. Shared tools, Project.xlsx and the map are outside these scripts' write scope.
