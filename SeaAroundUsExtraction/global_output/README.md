# Sea Around Us PPR pipeline

This project estimates the primary production required (PPR) to sustain Sea
Around Us reconstructed marine catches. It includes both the validated
five-region pilot and the completed global-scale run over every Sea Around
Us-defined Large Marine Ecosystem (LME) and High Seas unit.

Only the approved Pauly-Christensen (1995) trophic-chain method is used, with
transfer efficiency fixed at `TE = 0.1`:

```text
SPPR = (1 / TE)^(TL - 1) = 10^(TL - 1)
PPR  = catch tonnes × SPPR
```

The original paper's separate wet-weight-to-carbon divisor of 9 is deliberately
not applied. PPR is therefore labelled in tonnes of primary-production
equivalent, not tonnes of carbon.

## Completed scope and result

The global run contains 84 spatial units: 66 LMEs and 18 High Seas units. The
latest year shared by every non-empty catch archive is **2019**. Two official
units (`HS_018`, Arctic Sea, and `LME_064`, Central Arctic Ocean) have valid Sea
Around Us ZIP files containing zero-byte CSVs; they are retained with zero catch
and zero PPR and are explicitly flagged in the year and ingestion audits.

For the frozen 2019 inputs:

| Metric | Result |
|---|---:|
| Total catch | 99,115,685.26 tonnes |
| Total PPR | 65,252,683,993.89 tonnes primary-production equivalent |
| LME PPR | 57,876,694,349.93 |
| High Seas PPR | 7,375,989,643.96 |
| Catch-weighted TL coverage | 100% of positive catch |
| Catch reconciliation failures | 0 |
| Group/species PPR reconciliation failures | 0 |
| Jensen-inequality violations | 0 |

The largest regional PPR estimate is the South China Sea (`LME_036`) at
8,070,990,713.09 tonnes primary-production equivalent (12.37% of the 84-unit
total).

## Catch and trophic-level scope

Catch includes landings plus discards, reported plus unreported, across all
fishing entities, sectors, gears, and end uses in the downloaded Sea Around Us
files. Many Sea Around Us rows are species, while some are broader reported
taxa; the detailed files therefore use “species/taxon” where appropriate.

Trophic levels are assigned in this auditable order:

1. exact scientific-name match to `MeanTL` in the supplied 2020 supplement;
2. exact taxon match to the same Sea Around Us unit's exploited-organisms table;
3. mean of at least two supplement species in the same genus;
4. catch-independent mean of unique matched taxa in the commercial group;
5. catch-independent mean of unique matched taxa in the functional group;
6. unmatched, retained with missing TL and PPR.

Every regional species/taxon table records `match_method`, `tl_source`,
`match_confidence`, and `reference_taxon`. In the completed run, 46.69% of
positive catch matched the 2020 supplement exactly and 53.31% matched the
unit-specific Sea Around Us table exactly. No fallback or missing-TL assignment
was required.

## Correct and intentional Jensen-error calculations

Species/taxon PPR is calculated first. Commercial and functional outputs then
contain two parallel paths:

- **Correct:** sum member-taxon PPR, then derive group SPPR as
  `PPR_correct / matched catch`.
- **Intentional Jensen error:** calculate catch-weighted mean TL, transform it
  to `SPPR_jensen`, then multiply by matched catch.

Across all units, the Jensen shortcut underestimates correct PPR by 22.93% for
commercial groups and 16.48% for functional groups. Each group file reports the
difference, ratio, and percentage.

## Run or reproduce

Use Python 3.11 or newer from this directory:

```powershell
python -m pip install -r requirements.txt
python download_global_data.py
python run_global_pipeline.py
python build_global_notebook.py
node tools/build_workbooks.mjs --global
node tools/verify_workbooks.mjs --global
```

Downloads are resumable and frozen files are reused by default. To request a
specific year that is present in every non-empty archive:

```powershell
python run_global_pipeline.py --year 2018
python build_global_notebook.py
```

The original five-region pilot remains reproducible with:

```powershell
python download_data.py
python run_pipeline.py
python build_notebook.py
node tools/build_workbooks.mjs
```

## Global outputs

```text
global_output/
  PPR_global_summary.xlsx
  workbook_verification.json
  spatial/
    LMEs.geojson
    HighSeas.geojson
    spatial_units.csv
  regional_calculations/
    <84 regional .xlsx files>
  tables/
    global_summary.csv
    validation.csv
    tl_coverage.csv
    jensen_comparison.csv
    ingestion_audit.csv
    year_availability.csv
    run_metadata.json
    units.json
    regions/<unit_id>/
      species.csv
      commercial.csv
      functional.csv
      missing_tl.csv
      validation.csv
```

The Excel species SPPR/PPR columns and both group aggregation paths contain live
formulas. The corresponding CSV values are machine-readable. The executed
`notebooks/global_validation.ipynb` report contains the ranking, catch
reconciliation, matching coverage, Jensen comparisons, figures, and final
assertions.

The complete polygon layers inside `global_output/spatial/` are GeoPandas-ready
GeoJSON in EPSG:4326. They contain 66 valid LME geometries and 18 valid High Seas
geometries. The normalized unit index links each geometry to the API region ID.

## Validation gates

The workflow validates:

- archive structure and common-year availability;
- raw filtered catch against standardized taxon catch;
- species PPR against correct commercial and functional aggregation;
- the Jensen inequality for every group;
- TL matching route, confidence, catch coverage, and missing taxa;
- workbook formulas after reopening all 85 exported files;
- polygon feature counts, CRS, and geometry validity.

The current automated suite contains 47 passing tests. All six code cells in the
executed global notebook completed without errors, and all 85 workbook formula
error scans are clear.

## Provenance and reuse

`input/provenance.json` records source URLs, byte sizes, and SHA-256 checksums
for every frozen Sea Around Us input and inspected reference. Source materials
under the parent project's `sources/` directory remain read-only and are not
modified. Follow current Sea Around Us citation and licensing requirements when
redistributing data or publishing results.
