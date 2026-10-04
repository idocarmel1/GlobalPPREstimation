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

No production model selected. Exact diagnostic configurations and source/loader distinctions are described in the extraction-set report.
