# LME022 extraction and SPPR assessment — 28 September 2026

Four candidate JSONs are now available from the two requested sources: two published East-coast Scotland period models, the printed 1991 North Sea model, and a separately attributed EcoBase457 numerical variant of the latter. **User preference recorded on 28 September 2026:** `22_20251990_East_Coast_of_Scotland_(1991-1995)`, with the user's rationale, "least SPPR failures". GE and WithEgestion are OK; TE remains FAIL. This records candidate preference, not production adoption or scientific validity across all configurations. The earlier preference for the Mackinson/Daskalov paper, based on perceived spatial fit and documentation detail, is retained as history and superseded by this exact-model preference. Production Overview remains unselected.

**Later debugging requested by the user on 28 September 2026:** `457_457_North_Sea_(1991)` failed standard engine input/flow checks despite passing independent source mass balance. Discards group 68 has stored P=0.2981897135 versus recomputed P=-99.7018102865; the original source has detritus_import=100 and immigration=100. GE, TE and WithEgestion overall relative balance gaps are 2.9109828, 0.12447885 and 2.8741747. Cause remains unresolved: source representation, loader handling and computation have not been disentangled. The model is flagged for later review. No debugging experiments, source repairs or engine changes were performed for this preference update.

The North Sea report independently supports a basin-scale ICES IV domain of approximately 570,000 km². The Saygu models describe East-coast Scotland shelf fishing grounds, including Orkney/Shetland, within the North Sea. No defensible overlap percentage was calculated from a bounding box; the inherited central paper value 0.1 has not been validated. Source presence, spatial suitability, numerical validity and model adoption are distinct.

## Source preservation and interpretation

Source PDFs, XLSX/DOCX supplements, the original repository JSON and retrieved EcoBase records remain under `regions/LME_022/papers/`. The source manifest hashes their bytes. Each paper extraction includes all eight required import artifacts, source JSON, taxonomy, coordinate/page evidence, mass-balance findings and a database round-trip workbook. Source B, PB, QB, EE, GS and explicit diet entries were compared to canonical JSON; source catches were compared to JSON export totals. Group taxonomy preserves source spelling and the scope of principal-species lists; it is not an exhaustive modern nomenclature reconciliation.

The legacy converter silently normalizes diets. Its compatibility output is retained separately, and the canonical JSON was restored to exact published diet proportions, with every changed cell recorded. Both Saygu matrices have small rounding deviations; the report has large inconsistencies. The canonical import tables and JSON are not repaired models. Converter conventions (blank habitat=1, blank diet/import/catch represented as 0) are explicitly distinguished from original blanks. Published final B/PB/QB/EE values include Ecopath estimates rather than four independent inputs; no new source-supported values were inferred. Numeric biomass accumulation is unreported for all groups in each paper extraction and remains unknown. Any loader-derived value appears only in diagnostic outputs and `LOADER_TRANSFORMATIONS.csv`.

The calculation engine loads with `normalize_DC=True`, `DC_tol=0.001`, `underdetermined=True`, `zero_biomass_accum=False`. Consequently, wrapper results are **conditional computational diagnostics after loader normalization/defaults/flow completion**, not validation of a fully source-specified model. In particular, the printed North Sea input fails strict source diet admission and cannot be accepted merely because the loader computes numbers. Missing fate fractions can become external export in this representation; this is not source evidence of export.

## Exact diagnostic configuration

Each candidate was run through the existing regional SPPR wrapper using a fresh isolated candidate workbook in its own model directory. The live LME022 workbook was not selected or cleared. Runs request 22 methods (20 deterministic, 2 Monte Carlo), with 180 seconds per method/health row and 100 samples for MC. Health uses `det_collapse_mode=never`, `det_external_sppr=0`, `det_open_mode=none`, `det_theta=1`; theta is inert for this closed configuration. MC uses 10% uncertainty, 20% cut, and excludes divergent draws. Monte Carlo realizations are not seeded here and are retained exactly; earlier converter-normalized Saygu realizations are separately archived and are not the current results. A timeout is computational unavailability, never zero, and does not itself prove scientific failure. Health status applies to its exact configuration; an algorithm returning finite values does not establish scientific admissibility. Negative-group screening includes unfished groups.

No production catch matching, annual regional PPR, PPR–NPP comparison or map rebuild was performed. Model-internal footprint numbers in the diagnostic exports are not regional annual results. Continue the integration pipeline only after the user chooses an exact model and any material source/engine issues are resolved or explicitly scoped.


## 22_20251890_East_Coast_of_Scotland_(1890-1895)

Published 1890–1895 East-coast Scotland model: 25 groups, 23 consumers, 1 phytoplankton and 1 detritus group. Parameters: paper Table 1/PDF 6; diets: supplementary Table S3; three-fleet landings: Table S1; taxonomy: Table S2. Methods DOCX was inspected. GS, BA, detritus routing/import and habitat shares are not numerically documented. Discards are explicitly excluded by the paper. Printed seal biomass 0.00 remains 0.00; it was not replaced with an inferred small positive biomass. Source validation: 0 errors, 27 warnings; source mass-balance check BALANCED with 0 errors, 0 indeterminate and 3 endotherm P/Q warnings, conditional on its treatment of unknowns. This does not certify exact source completeness. GE/WithEgestion WARN involve the zero-biomass/EE historical seal case. TE diverges and has negative Seabirds SPPR despite zero catch.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | WARN | 0.21226276 | 0 |
| TE | FAIL | 1.1116113 | 1.2720206e-15 |
| With Egestion | WARN | 0.16981021 | 4.2400685e-16 |

MC_new_GE: 100/100 accepted; 0 divergent rejections and 0 negative rejections (not necessarily additive). MC_new_TE_EEfix: 21/100 accepted; 79 divergent rejections and 0 negative rejections (not necessarily additive).

SPPR_2015: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. new_TE_noEEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. new_TE_EEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. sym_TE_asPP: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. sym_TE_asDC: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258.

Unavailable methods: none.

97 printed core values matched database JSON; 232 source diet slots including zeros/import matched without normalization; All group names, source BA unknowns and taxonomy carried through; All database exports equal retained fleet landings plus discards; Eight import tables and database round-trip workbook retained. Round-trip basic/diet cells independently verified: 775.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: ad7cae363be6214a700845fcf15f5584b20de4c20c05e3ebf251fa03c89f1692.

## 22_20251990_East_Coast_of_Scotland_(1991-1995)

Published 1991–1995 East-coast Scotland model: 25 groups, same topology and source locations as the1890–1895 version. Period-specific parameters and landings are retained separately. Source validation: 0 errors, 27 warnings; source mass balance INDETERMINATE, 0 errors, 2 indeterminate groups (Turbot and Ling),3 endotherm P/Q warnings. Unknown BA could reconcile the discrepancy, but no checker-suggested BA was inserted. GE/WithEgestion are OK for the completed engine model; TE still diverges with negative unfished Seabirds. These results do not remove the source BA uncertainty.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | OK | 0.21208967 | 0 |
| TE | FAIL | 1.1127784 | 2.1200343e-16 |
| With Egestion | OK | 0.16967174 | 0 |

MC_new_GE: 100/100 accepted; 0 divergent rejections and 0 negative rejections (not necessarily additive). MC_new_TE_EEfix: 13/100 accepted; 87 divergent rejections and 0 negative rejections (not necessarily additive).

SPPR_2015: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. new_TE_noEEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. new_TE_EEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. sym_TE_asPP: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. sym_TE_asDC: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512.

Unavailable methods: none.

97 printed core values matched database JSON; 232 source diet slots including zeros/import matched without normalization; All group names, source BA unknowns and taxonomy carried through; All database exports equal retained fleet landings plus discards; Eight import tables and database round-trip workbook retained. Round-trip basic/diet cells independently verified: 775.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: 5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691.

User preference (explicit instruction, 2026-09-28): this exact model is preferred because it has the "least SPPR failures". GE and WithEgestion are OK, but TE remains FAIL. This does not change production Overview or adopt computed results.

## 22_20071991_North_Sea_report_Table_3.3_(1991)

Printed1991 model: 68 groups (64 consumers, 1 phytoplankton, 3 detritus pools), final balanced Table 3.3 printed27–28/PDF 29–30, diets Table 3.4 printed29–40/PDF 31–42. Bracketed initial estimates are preserved as evidence and not substituted for the final table. Table 3.5 eight-fleet landings and unallocated total discards were converted from tonnes using 570000 km². Dashes remain unknown. Summary catches differ from detailed12-fleet Tables14.7/14.8; both are retained separately, not silently mixed. Prose documents only limited fate routing (PP30% DOM/70% POM; DOM→POM; POM→export); the remaining source fate fractions stay unknown. Taxonomy combines the report's group descriptions with 107 principal benthic contributors from Table 11.8, not an exhaustive census.

**Severe printed-source defects:**19 consumer diet sums differ from 1 by more than 0.01;33 exceed the engine0.001 admission tolerance. Examples: juvenile Cod0.562, juvenile Saithe0.403, adult Saithe1.530, Hake1.539, Blue whiting0.387 and Large crabs1.468. Continuation-page values appear repeated in some columns; source coordinates and page images preserve the evidence. The Import row is included (adult Whiting includes0.324). Gelatinous zooplankton PB 2.858 and QB 0.18 imply P/Q 15.8778, as actually printed; the prose separately claims P/Q 0.45. None was repaired. Strict raw diet admission FAILS. Import validation records19 errors/67 warnings. Source mass balance is NOT BALANCED: 1 error, 19 indeterminate, 4 warnings, including nonpositive gelatinous respiration. Loader normalization/completion yields low identity residuals but does not cure this source failure. All three main health configurations FAIL; GE and TE diverge, and WithEgestion fails overall flow balance. Many negative SPPR values remain, including unfished groups.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | FAIL | 1.0077335 | 10.172396 |
| TE | FAIL | 1.1912864 | 0.93872104 |
| With Egestion | FAIL | 0.8061868 | 2.0459071 |

Both 100-sample Monte Carlo methods timed out at 180 seconds; acceptance/rejection counts are unavailable.

sym_WithEgestion_asPP: 67 negative aggregate groups, including 19 unfished groups; minimum SPPR -952039.9801. sym_WithEgestion_asDC: 67 negative aggregate groups, including 19 unfished groups; minimum SPPR -937970.8671. new_GE: 48 negative aggregate groups, including 8 unfished groups; minimum SPPR -5038070.626. sym_GE_asPP: 48 negative aggregate groups, including 8 unfished groups; minimum SPPR -5056549.12. SPPR_2015: 37 negative aggregate groups, including 3 unfished groups; minimum SPPR -581458.1653. new_TE_noEEfix: 37 negative aggregate groups, including 3 unfished groups; minimum SPPR -581458.1653. new_TE_EEfix: 37 negative aggregate groups, including 3 unfished groups; minimum SPPR -581458.1653. sym_TE_asPP: 37 negative aggregate groups, including 3 unfished groups; minimum SPPR -581458.1653.

Unavailable methods: EwE_TE_noEE: timeout; EwE_TE_EE: timeout; sym_TE_asDC: failed; sym_GE_asDC: failed; MC_new_GE: timeout; MC_new_TE_EEfix: timeout.

329 printed core values matched database JSON; 908 source diet slots including zeros/import matched without normalization; All group names, source BA unknowns and taxonomy carried through; All database exports equal retained fleet landings plus discards; Eight import tables and database round-trip workbook retained. Round-trip basic/diet cells independently verified: 5032.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: 946bac733f0a74ce2a8428ed5dadff548ad6ee5d7c3a30328c03dcf9e8d09934.

## 457_457_North_Sea_(1991)

EcoBase accession 457: 68 groups, registry period1991–1992 and local archive filename1991. The live record explicitly cites the Mackinson/Daskalov technical report. The original JSON bytes are archived; every original numerical field was preserved, with source-based taxonomy attached by group_seq only. It is a separate repository numerical variant, not an interchangeable paper extraction: the parameter comparison records 205 unequal fields including precision, BA unknown→0, catches and substantial changes (e.g. gelatinous QB 6.35111141 instead of printed0.18). The database export aggregates catch and does not preserve the12-fleet ledger. Its JSON-only route is retained with a reconstructed workbook; original repository bytes remain the authority.

Strict source diet admission PASS; independent source mass-balance checker BALANCED with 0 errors/0 indeterminate and 4 endotherm warnings. Nevertheless, all standard engine configurations FAIL. A fresh independent engine load reproduces the worst identity residual at Discards group 68: stored production0.2981897135 versus recomputed−99.7018102865. The source supplies both detritus_import 100 and immigration 100, unchanged; the engine's handling of this detritus/migration representation requires investigation. Do not describe this alone as proof that the repository living food web is grossly unbalanced. Separate overall balance gaps remain substantial. No negative aggregate group SPPR occurs in completed methods, but convergence/nonnegativity does not make the diagnostic model valid. Both MC methods and both EwE path methods timed out; six symbolic methods failed. No source or engine repair was attempted.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | FAIL | 0.33263683 | 2.9109828 |
| TE | FAIL | 0.58371892 | 0.12447885 |
| With Egestion | FAIL | 0.26610946 | 2.8741747 |

Both 100-sample Monte Carlo methods timed out at 180 seconds; acceptance/rejection counts are unavailable.

No negative aggregate group SPPR in completed methods; unavailable methods were not treated as passing.

Unavailable methods: EwE_TE_noEE: timeout; EwE_TE_EE: timeout; sym_TE_asPP: failed; sym_TE_asDC: failed; sym_GE_asPP: failed; sym_GE_asDC: failed; sym_WithEgestion_asPP: failed; sym_WithEgestion_asDC: failed; MC_new_GE: timeout; MC_new_TE_EEfix: timeout.

All original repository numerical fields unchanged; only taxon_descr attached by exact group_seq. Round-trip basic/diet cells independently verified: JSON-only repository route; reconstruction retained.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: f6a8a64ecd52fca40117afe76503db2ea29db002a87bc789959dd75c31dbcfbc.

User-requested deferred review (2026-09-28): investigate why this model fails flow balancing despite passing the independent source check. The verified Discards/import/migration discrepancy above is evidence, not an established cause. No debugging experiment or repair was performed in this preference update.

## Unavailable 1973 version and sources

The report discusses a fitted1973 model. No complete separate static parameter/diet/fishery set was found in the requested source bundle. EcoBase628 advertises a1973 model but its retrieved record exposes zero groups/fleets. It is documented as unavailable, not reconstructed from 1991 values and not counted among the four extracted candidates.

- Saygu et al. (2025), doi 10.3389/fmars.2025.1646031: https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1646031/full
- Mackinson and Daskalov (requested citation2007; copyright2008), Cefas Technical Report142: https://www.cefas.co.uk/publications/techrep/tech142.pdf
- EcoBase457 and 628 records: archived HTML and retrieval hashes in the report paper folder. The457 record gives the source linkage and numerical-variant identity; the628 record supports the present availability limitation.

Central metadata changes are defined in `central_metadata_proposal.json`, coordinated by the parent task; `CENTRAL_REGISTRATION_VERIFICATION.json` records application and preservation checks. The exact model preference and deferred EcoBase457 review are now recorded. Existing regional selection/results and prior validation evidence are preserved. Production execution remains pending further instruction.
