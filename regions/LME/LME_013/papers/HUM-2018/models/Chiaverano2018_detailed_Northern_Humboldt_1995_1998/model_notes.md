# Chiaverano2018_detailed_Northern_Humboldt_1995_1998

## Source identity

HUM-2018__LME_013

Regional application: `LME_013`. Pre-correction relocation baseline SHA-256: `c9ddb57d874926cd51a3dff19956ca57b197a1ab973cd96356c9bcc185a04bda`. The historical byte-preservation check concerns relocation only. Current corrected canonical JSON SHA-256: `11cbf610b7d2514085bd0d079b385cf9419e15308493b3a35183673553c5adb7`.

## Modeled period and area

Period: 1995–1998

Approximate A6–8%, B90–100%; reviewed source Figure 1 trace and reported-area discrepancy retained. Fixed model and allocations over 1950–2019 remain extrapolations.

## Departures from the publication

The native detailed supplement has 41 nodes: 39 stock/pool nodes plus two fleet nodes. This computational representation retains the 39 stocks with the source-backed scientific corrections described below, while recording habitat area=1, BA=0, migration=0 and external-detritus-import=0 as execution conventions. Source habitat fractions, numerical BA/migration/import remain unreported. Eggs group 36 is operationally a nonfeeding pool (`pp=2`), because its source rates are blank; the prose 25% egg-production statement is not an annual P/B input. Fleet landings/discards and export fates remain in companions because stock JSON cannot encode complete fleet ancestry.

On 8 October 2026, the researcher authorized the primary source-backed corrections. Chrysaora plocamia (7) diet now uses Diatoms=0, Mesozooplankton=0.68, Macrozooplankton=0.17, Gelatinous zooplankton=0 and Anchovy eggs=0.15. The 68/17 fractions are reconstructed from author Supplementary Table H I14/J14 and Table E singleton identities; zero direct links occur at F14/K14 and the egg fraction retains Table B H39. This replaces the contradictory Table B row totaling 1.045; original source cells remain in the supplement and extraction evidence. Small-gelatinous biomass/PB/QB/EE remain unchanged. Sardine (9) landings follow article PDF3/printed30: 1.4 instead of Table A J14 5.6513425; reported discards remain 0.17462648325, so JSON export=1.57462648325. Sardine EE is recalculated as (normalized-diet predation + landings + discards)/production = 0.6872065402096068, replacing the model-estimated Table A H14 0.9700034856796265. B/PB/QB, BA and migration are unchanged. Article Table 1 and Scenario III still corroborate the older high-catch branch; author intention remains inconsistent. The adopted values are documented reconstructions and derived corrections, not newly printed source data.

Runtime diet normalization remains separate from canonical corrections and native pool-fate identity replacement remains an unsupported translation restriction. Fresh diagnostics for the corrected model are retained in the linked current validation run; numerical balance does not establish researcher approval.
The following table records baseline execution-convention differences from the [retained source variant](../Chiaverano2018_detailed_Northern_Humboldt_1995_1998__source/model.json); the accepted scientific corrections above are additional current differences. The source representation is an evidence locator; it is not proof that every source field is a published measurement. `-9999` remains an unknown sentinel. Relocation itself introduced no scientific difference.

| Group IDs | Field | Source representation | Retained representation |
|---|---|---|---|
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `habitat_area` | `-9999` | `1` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `biomass_accum` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `biomass_accum_rate` | `-9999` | `0` |
| 1, 2, 36, 37, 38, 39 | `gs` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `detritus_import` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `immigration` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `emigration` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 | `emigration_rate` | `-9999` | `0` |


## Evidence links

- [Canonical Ecopath representation](model.json)
- [provenance.json](inputs/provenance.json)
- [validation.docx](model_validation/validation.docx)
- [REPORT.md](extracted_tables/evidence/source/REPORT.md)
- [TRANSFORMATION_LEDGER.json](extracted_tables/evidence/TRANSFORMATION_LEDGER.json)
- [result_manifest.json](results/result_manifest.json)
- [Portable source dispositions](../../../../../../../common_reference_data/provenance/source_paths.csv)

## Removed extraction evidence

Superseded extraction packages and their unique old evidence are removed under the agreed latest-only policy; they are not merged into this package. Original paths, hashes and reasons are metadata in the linked disposition ledger. A link to this paragraph records an unavailable former payload, not replacement evidence or completed scientific verification.


Current correction and validation evidence: [adopted corrections](model_validation/work/2026-10-08_132433_balanced_validation/outputs/adopted_corrections.json), [validation run](model_validation/work/2026-10-08_132433_balanced_validation/outputs/). The researcher authorized map publication on 8 October 2026, conditional on auto detritus handling. Existing allocation proxies retain the published native source-model landings; the corrected sardine export does not silently change taxon allocation weights.

The [source correction rationale](model_validation/source_value_corrections.docx) cites only the article and author supplement. Fresh GE, TE and With Egestion diagnostics retain overall FAIL. Pooled GE and With Egestion remove negative coefficients and pass their SPPR budgets, but do not remove the unpooled convergence failure; TE remains unchanged by pooling and fails its SPPR budget. The corrected model passes living mass balance with both the exact notebook constructor and zero-BA-preserving validation settings. No current Monte Carlo uncertainty bounds are claimed. Ido Carmel signed MODEL VALIDATED on 8 October 2026; the human approval is conditional on auto detritus handling and does not change engine diagnostic grades.


Conditional researcher approval: every SPPR_new-related calculation must use `det_collapse_mode='auto'` (the user's stated `collapse_det_mode` condition). [Fresh auto diagnostic evidence](model_validation/work/2026-10-08_151840_auto_review_publication/outputs/auto/run_manifest.json) reproduces all prior pooled matrices and adopted coefficients exactly. The revised signed review includes Cetaceans and initially excludes Fishery offal, Pinnipeds, Seabirds and Chrysaora plocamia from displayed webpage PPR only; saved scientific groups, diets, catch, coefficients and allocation weights remain intact. Map users may override those initial display selections while the researcher-exclusion annotations retain the signed decisions. TE still fails its primary-production budget, and all three engine overall FAIL grades remain recorded.
