# Chiaverano2018_detailed_Northern_Humboldt_1995_1998

## Source identity

HUM-2018__LME_013

Regional application: `LME_013`. Canonical JSON SHA-256: `c9ddb57d874926cd51a3dff19956ca57b197a1ab973cd96356c9bcc185a04bda`. The byte-preservation check compares this retained representation with the pre-relocation working state; it is not a fresh extraction or a new approval.

## Modeled period and area

Period: 1995–1998

Approximate A6–8%, B90–100%; reviewed source Figure 1 trace and reported-area discrepancy retained. Fixed model and allocations over 1950–2019 remain extrapolations.

## Departures from the publication

The native detailed supplement has 41 nodes: 39 stock/pool nodes plus two fleet nodes. This computational representation retains the 39 stocks and native biological values/diets, while recording habitat area=1, BA=0, migration=0 and external-detritus-import=0 as execution conventions. Source habitat fractions, numerical BA/migration/import remain unreported. Eggs group 36 is operationally a nonfeeding pool (`pp=2`), because its source rates are blank; the prose 25% egg-production statement is not an annual P/B input. Fleet landings/discards and export fates remain in companions because stock JSON cannot encode complete fleet ancestry.

Native Table A J14 supplies Sardine landings=5.6513425, whereas article PDF p.3/printed p.30 says 1.4 after balancing. The supplement branch is retained without a catch repair. Table B H4/H7/H8/H9/H39 sums to 1.045 for large jellyfish; this is an unresolved 4.5% excess. Small-gelatinous Table A C11/D11/E11/H11 values are B=0.009068332612514496, PB=0.5839999914169312, QB=2.919999837875366 and EE=0.949999988079071. Predation implies EE about 4409.97 under the retained arithmetic convention; no biomass magnitude correction was made.

The diagnostic loader separately normalizes 161 diet cells and replaces eight native pool-fate cells with identity routing. These are diagnostic transformations, not canonical source corrections. All direct methods remain FAIL; native missingness and source conflicts do not become scientific approval.
The following exact input differences compare this JSON with [retained source variant](../Chiaverano2018_detailed_Northern_Humboldt_1995_1998__source/model.json). The source representation is an evidence locator; it is not proof that every source field is a published measurement. `-9999` remains an unknown sentinel, and absent fields are shown as `None`. No difference was introduced by this reorganization.

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
