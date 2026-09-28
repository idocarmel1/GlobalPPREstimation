# Selected 2013 model: regional pipeline report

**Selection saved:** `50_502013_Coastal_Kyoto_Inoue_(2013)`, because the user prefers the newer model. **1985 remains a good comparison model.** This is not a finding that 2013 is numerically superior.

The regional Overview records the exact selection and rationale. Previous results were archived before `prepare_selection`; the original source models, comparison reports and evidence remain intact. The independently verified [GE group comparison](ge_year_comparison/GE_SPPR_GROUP_COMPARISON.md) is complete.

## Completed and verified

- Three bounded direct `diagnose_sppr()` calls: GE, TE, With Egestion only, with full returns. Each exactly reproduces its previous audited return; all remain WARN, with nonnegative finite source coefficients and convergent calculations. No global option, Monte Carlo or broad method suite was run.
- The loaded groups, diet and detritus fate match the original audit exactly. Canonical 2013 SHA256 remains `a3b008c0add95db106f9e10cf90907cc7f1f9d2ab1425cbf615745142e27330e`.
- Regional Selected model groups now contains all 40 source groups plus diet import, with 369 coefficients covering 3 methods×3 scopes×41 groups.
- 19 of 253 catch taxa have exact Table S3 membership or verified synonym evidence. All 234 remaining taxa retain explicit unresolved rows. Source and mapping spellings were not silently repaired; no invented proxy groups or coarse weights were used.
- Supported-catch annual PPR and available PPR/NPP ratios were calculated through the current regional calculation contract. Catch, NPP and Classic PPR taxon inputs are unchanged. Prior annual/sensitivity results remain in the archived workbook; current calculation invalidates old sensitivity bounds as required.

## Coverage is the remaining scientific limit

|2019 basis|Confirmed mapped tonnes|All recorded tonnes|Coverage|
|---|---:|---:|---:|
|Total catch|648,029.94|2,586,941.84|25.0500%|
|Landings|640,137.59|2,258,481.01|28.3437%|
|Discards|7,892.36|328,460.82|2.4028%|

The source is coastal Kyoto, not the whole Sea of Japan. It supplies no supported pollock, cod, saury or Pacific herring group. Major unresolved 2019 catches include Alaska pollock 494,220.49 t, unidentified marine fish 315,222.27 t, Pacific herring 109,934.89 t, Scomber 106,955.52 t, Pectinidae 86,406.07 t and Pacific cod 80,661.51 t. Some coarse taxa may become resolvable with better group definitions; others lie outside the source model. Neither case justifies an invented mapping.

**Complete regional model PPR remains pending additional membership or explicitly reviewed proxy evidence. Production eligibility remains false.** Current annual values are confirmed mapped-catch subtotals, not full-LME totals; unresolved taxa are not assumed to require zero production. The standard zero/simple unidentified-treatment views remain separate from the method-treatment coverage shown here.

## Supported 2019 catch subtotal, all-source coefficients

These values apply 2013 coefficients to the 19 supported taxon series. They are separate from the paper's own modeled-area catch footprint. Carbon conversion divides wet-weight equivalent production by 9 once. The ratio denominator is existing regional ensemble-median NPP, while the numerator remains a partial catch subtotal.

|Method|Direct diagnostic|PPR wet-weight tonnes|PPR tonnes carbon|Subset PPR / existing regional NPP|
|---|---|---:|---:|---:|
| GE | WARN | 9,995,846.75 | 1,110,649.64 | 0.5203% |
| TE | WARN | 50,570,682.26 | 5,618,964.70 | 2.6321% |
| With Egestion | WARN | 6,514,850.98 | 723,872.33 | 0.3391% |

## Caveats preserved

The paper describes different diets between 1985 and 2013 but supplies only one complete matrix. Source admission is still unresolved. Loader diet normalization, missingGS/catch/migration/routing defaults and solved biomass accumulation are unchanged and remain separately audited. Numerical balance does not establish recovery of the original year-specific source model. The WARN statuses include EE=0 consequences; selection does not erase them.

The three synonym links were independently retrieved from the WoRMS API and retained with hashes: [Sardinops melanostictus → Sardinops sagax](https://www.marinespecies.org/rest/AphiaRecordByAphiaID/309913), [Crassostrea gigas → Magallana gigas](https://www.marinespecies.org/rest/AphiaRecordByAphiaID/140656), and [Dasyatis akajei → Hemitrygon akajei](https://www.marinespecies.org/rest/AphiaRecordsByName/Dasyatis%20akajei?like=false&marine_only=true). These resolve taxonomy; they do not establish whole-LME spatial representativeness.

## Validation and handoff

Independent checks passed for 3780 annual mapped-subset cells and 7056 supported ratio cells.26964 unsupported ratio cells remain blank. Catch=landings+discards holds within 7.5×10⁻¹⁰t. The current regional engine rounds taxon coefficients to 6 decimals; the largest resulting annual difference from unrounded group coefficients is 0.22871 wet-weight tonnes, retained in the audit. Regional selection/input/result fingerprints validate.

Evidence and full-precision outputs are under `../50_502013_Coastal_Kyoto_Inoue_(2013)/selected_pipeline/`: `VALIDATION.json`, `MAPPING_REVIEW.json`, all direct returns, source coefficients, membership/coverage tables, annual subtotals, ratios, code snapshots and provenance. Regional workbookSHA256: `156a5ab454860c617e4228a6c298119ee48fa73899b3d30174563a9d2724cdc7`.

Central registration is queued in [SELECTED_CENTRAL_REGISTRATION_PROPOSAL.json](SELECTED_CENTRAL_REGISTRATION_PROPOSAL.json). The proposal updates the existing paper record, appends the two absent local models, derives the 2013 selection from Overview, retains 1985 comparison status, and preserves scores/ranks/other regions. No central workbook or map writes were performed by this selected-model run.
