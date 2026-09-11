# Annual NPP completion — 2026-09-11

Both full-history extractions and checked regional publication are complete.
Regional NPP covers all 366 identities; the global reference uses the fixed
LME/high-seas union. The final skill refresh completed after extraction and all
implementation agents finished. All shared artifact rebuilds and final verification
passed; results are recorded in `CONTINUATION_PROGRESS_2026-09-10.md` and the validation reports.
The carbon conversion review and new Ecopath coverage expansion remain deferred.

## Delivered coverage

`NPPExtraction/output/annual_npp.csv` has SHA-256
`961278ae7c39a898b4282fbb9b426ff2235eabca496553abe4b3330d34605dbe`.

- All 366 identities × 22 years, 1998–2019: 8,052 annual ensemble values.
- 25,211 canonical rows over 1950–2019: 5,938 complete, 2,112 partial,
  17,161 unsupported blank; no pending, failed or source-error rows.
- Early 1998–2002 rows have one algorithm; some later regions have fewer than five.
  Per-year model counts, names, source files and hashes remain explicit.
- HS_018 and LME_064 have NPP without catch; their legacy 2019 cells and provenance
  are unchanged. The canonical CSV contains the other 8,050 supported rows.
- All 11,310 original rows remain identical in every field. Expansion computed
  4,398 supported records and reused 14 previously computed original cells.
- All 22 global-reference years pass full verification. Completing numerical
  integration does not imply full satellite-water or five-model coverage.

Preservation and numerical evidence:
`NPPExtraction/output/regional_expansion/publication_verification.json`,
`data/regional_npp_numerical_review.json` and
`data/regional_npp_publication_review.json`. The original
`NPPExtraction/output/extraction_coverage.json` is the archived-subset historical audit.

[ANNUAL.md](../NPPExtraction/ANNUAL.md) gives fresh-clone setup, source downloads,
resumable extraction and output definitions. Source downloads total approximately
32 GB, plus decoded caches. Caches are ignored and reproducible, not prerequisites
that must be copied from this computer. The 2019 reconciliation has 405 comparable
finite values with maximum relative difference 3.46e-8 against the supplied reference.

## Rebuild contract

Use one completed canonical input snapshot. Unset `PPR_ANNUAL_NPP_PATH` for the
canonical build; the earlier `output/snapshots/annual_npp_for_task14.csv` is a
historical intermediate snapshot and is no longer the delivered source.

From the repository root, with the documented dependencies installed:

```powershell
Remove-Item Env:PPR_ANNUAL_NPP_PATH -ErrorAction SilentlyContinue
python -X utf8 tools/build_ecosystem_data.py --force
python -X utf8 tools/build_model_workbook.py
python -X utf8 tools/build_network_atlas.py
python -X utf8 tools/build_time_series.py
python -X utf8 tools/verify_model_workbook.py
python -X utf8 tools/verify_annual_npp.py
python -X utf8 tools/verify_final_mappings.py
node tools/verify_unidentified.cjs
node tools/verify_discard_views.cjs
python -X utf8 tools/build_time_series.py --check
```

Run dependent writes sequentially and stop on errors. Workbook and atlas text
saves use same-directory temporary files followed by atomic replacement, avoiding
intermittent Windows failures opening an existing destination. This does not make
concurrent writers safe; assign one owner for final shared outputs.

## Units, missingness and verification

Canonical `npp_*_tC_yr` fields are already regional annual tonnes carbon. Legacy
2019 regional estimates use `scaled_*`; never apply the scaling twice. Source
workbook PPR remains total catch in wet-weight-equivalent units. Map/graph PPR
uses the selected taxon catch component and the existing `/9` conversion once.

Unsupported years stay blank. The optional earliest-year display proxy applies
only before each ecosystem/method's first available value and preserves source
year and estimated status. It does not fill internal/later gaps or replace zeros.
Ensemble spread is not a confidence interval and algorithms share inputs.

Current numerical counts are in `data/annual_npp_validation.json` and the other
`data/*_validation.json` reports, regenerated after the final shared builds.
The preceding archived-scope release checked 224,280 exported values, 155,124
workbook NPP values and 26,554 summary ratios; those counts are historical and do
not describe the expanded all-identity release. Mapping, catch-basis, unidentified
and simple-map parity checks remain independent release checks.
The obsolete `tmp/verify_task14.py` default-PPR comparison must not be used as a
release guard: the user's landings default legitimately changes the evaluation
vector, while the exporter separately verifies original total-catch workbook PPR.
