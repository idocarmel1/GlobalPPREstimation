# Reproduce annual NPP for all atlas ecosystems

The supplied `ppr-npp.zip` was imported into this directory without changing its two
original 2019 reference CSVs. The archive workflow supplies the original base;
the separate regional expansion supplies every missing supported identity/year.
NPP availability is independent of catch and articles. NPP-only rows do not create
invented catch values.

## Completed extraction — September 11, 2026

All **366 identities have annual ensemble NPP for 1998–2019**: 8,052 values,
including the retained legacy 2019 cells for no-catch HS_018 and LME_064. The
canonical CSV contains **25,211** rows spanning 1950–2019: **5,938 complete**,
**2,112 partial**, and **17,161 unsupported** rows with blank NPP. There are no
pending, failed, source-error or missing ensemble rows. Its SHA-256 is
`961278ae7c39a898b4282fbb9b426ff2235eabca496553abe4b3330d34605dbe`.

The [publication proof](output/regional_expansion/publication_verification.json)
checks all 11,310 original rows field-for-field. Expansion added 4,398 newly
computed supported records and reused 14 already computed original cells.
The [independent publication review](../data/regional_npp_publication_review.json)
checks all 366 × 22 positive annual ensembles. The older
[archive coverage audit](output/extraction_coverage.json) and
[workbook refresh audit](output/workbook_refresh.json) retain the preceding
archived-subset release as historical evidence. Current cross-output comparisons
are in `data/annual_npp_validation.json` at the repository root.

Early 1998–2002 estimates use one model; some later regions have fewer than five
usable model estimates. Preserve annual counts, identities and ensemble basis.
The cache contains 1,104 distinct monthly source files totaling 32.05 GB, including
neighboring-year inputs. Annual provenance links to exact code and full-geometry
snapshots. Completing calculation does not establish full satellite-water coverage.
The separately verified [fixed atlas-union reference](../docs/GLOBAL_ATLAS_NPP_REFERENCE.md)
also covers all 22 years and uses a different ensemble aggregation convention.

The fresh 2019 extraction was also compared with all 82 overlapping legacy regions.
The 405 finite model pairs across 81 regions agree with the legacy `scaled_*` values
to a maximum relative difference of `3.46e-8`. The Black Sea's previously blank
scaled entries now use the supplied algorithm's own-coverage fallback; its
three-model median is 62,028,266.28 tC/year. See
[the reconciliation](output/reconciliation_2019.json). The older common-mask
headline values are a different quantity and must not be mixed with these totals.

## Fresh checkout setup

Run from `NPPExtraction` using Python 3.11–3.13 (Python 3.13 tested on Windows):

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[test]"
.venv/Scripts/python.exe -m pytest tests -q
```

On Linux/macOS use `.venv/bin/python` in place of `.venv/Scripts/python.exe`.
`requirements-lock.txt` records the versions tested in this Windows Python 3.13 run;
install it with `python -m pip install -r requirements-lock.txt` and then
`python -m pip install -e . --no-deps` to reproduce that dependency set.
Use Python 3.13 for the tested environment. The locked NumPy/SciPy versions require
Python 3.12 or newer; on Python 3.11, the editable install above resolves compatible
earlier dependency versions instead of using this lock file.
Current Windows Python 3.13 wheels include the HDF4 library through `pyhdf`; a separate
Conda environment is unnecessary. On platforms lacking a wheel, install the platform's
HDF4 development package before installing `pyhdf`. HTTPS certificate verification
uses the system trust store plus Certifi roots and is never disabled.
The NetCDF4/HDF4 native readers on Windows can reject existing files in Unicode paths.
The package handles this through NetCDF4's in-memory API and temporary ASCII HDF4
paths; the Hebrew repository path was tested using actual downloaded files.

### Requested full recomputation

Before a new regional extraction, use a versioned helper with uncached source-byte
validation and a fresh plan/cache identity. The completed regional helper retains
its historical metadata cache so that the executed code remains reproducible;
size and modification time alone cannot prove unchanged content. The independent
post-extraction check `python -X utf8 tools/verify_regional_npp_sources.py` (from the
repository root) directly hashed all1,104 planned monthly files/32,049,287,447 bytes
with zero mismatches. Its report is `data/regional_npp_source_bytes_validation.json`.
This validates current source bytes without claiming every past boundary was
checked uncached. Preserve the completed helper, plan and execution snapshots.

Validate shipped results before choosing to recompute them. Use an isolated
checkout or separate output workspace for a full recomputation. The archive-only
writer replaces its canonical CSV; **do not run it over an expanded all-366 release**.
In the reproduction workspace, create the original archive/catch base first:

```powershell
.venv/Scripts/python.exe -m npp.annual plan --refresh-sources
.venv/Scripts/python.exe -m npp.annual run
```

Then, from the repository root, prepare a fresh regional expansion plan and run
its extraction and checked publication:

```powershell
NPPExtraction/.venv/Scripts/python.exe -X utf8 tools/expand_regional_npp.py plan
NPPExtraction/.venv/Scripts/python.exe -u -X utf8 tools/expand_regional_npp.py extract --years 1998:2019
NPPExtraction/.venv/Scripts/python.exe -X utf8 tools/expand_regional_npp.py publish
```

Review complete annual records before publication. The plan freezes the original
CSV, source configurations, raw-file hashes, scientific geometry and executed code.
Resumption requires their exact identity and complete validated checkpoints; after
publication, the canonical CSV intentionally differs from the extraction baseline.
Do not start a competing raster worker or mutate frozen inputs. For the separate
fixed-union run, follow its linked reproduction guide and serialize raster work.
See [regional execution and preservation details](../docs/REGIONAL_NPP_EXPANSION_HANDOFF.md).

Use `--refresh-sources` to discover a new source release. Use `--config path.yaml` for
fill settings; annual source windows are clipped to available complete years.
The default is the supplied five-year centered window (two neighboring years each
side), shortened at the source boundaries. There is no extrapolation to earlier target
years. The optional atlas earliest-available-year display is a downstream estimate and
is never written into the canonical extraction file.

## Scientific meaning

`output/annual_npp.csv` retains actual catch-year rows and all supported NPP-only
identity/year rows, with five
`npp_<model>_tC_yr` fields and median/minimum/maximum across the finite models. Values
are annual tonnes of carbon. The canonical annual fields correspond to the ZIP's
`scaled_<model>_tC_yr`: gap-filled Antoine–Morel baseline multiplied by the model ratio
on common coverage; sparse common coverage uses the original own-coverage fallback.
The original CSV `npp_*` and `scaled_*` fields differ, so those 2019 CSVs remain
references and are not silently seeded into the annual product.

`n_models`, `available_models`, `ensemble_basis`, `model_status`, `window_years`, and
`method` disclose changing ensemble membership and gap-fill context. A one-model
median equals that model and is not a five-model ensemble. The neighboring-year fill
estimates missing satellite pixels within a supported target year; it does not create
annual data before the satellite record. Existing spatial fill and polar-night methods
are retained; see `METHODS.md`.
The minimum–maximum range is the spread across available algorithms, not a statistical
confidence interval; a one-model range cannot represent total NPP uncertainty.

All missing numeric cells are blank, including unsupported early years, failed downloads,
and models without regional retrievals. `status` distinguishes `unsupported`, `pending`,
`source_error`, `failed`, `partial`, `missing`, and `complete`. `complete` means all five
algorithms yielded a value for that region, not that all pixels were observed directly.

## Availability, checkpoints, and resource needs

The live September 10, 2026 native listings show complete Copernicus years 1998–2024.
The four OSU MODIS algorithms have different missing months: VGPM/Eppley list complete
2003–2021 and 2023 (April 2022 is absent); CbPM lists complete 2003–2021; CAFE lists
complete 2003–2023. Partial 1997/2002/2024 series are not annualized. Always consult
`output/source_catalog.json` for the exact model/year/month URLs and discovery time;
the source catalog is the availability authority, rather than the ranges in this text.

2019 requires approximately 3.9 GB Copernicus data for the 2017–2021 window plus four
OSU model years. The Copernicus native sample is ~780 MB/year; OSU sample is ~17 MB
per model/month. A full historical run needs tens of GB and substantial computation.
The native 4 km baseline can require several GB of RAM; the four-worker setting applies
only to downloads, while raster computations run one year at a time.
Exact float32 decoded Copernicus rasters are cached as read-only memory maps under
`data/decoded/`, outside the original source cache. This preserves every value and NaN
while avoiding repeated decompression across overlapping five-year windows; allow about
45–50 GB extra disk for the full history. File size and modification time bind these
derived files to sources, whose URL and SHA-256 are verified by the annual runner.

Raw monthly files and coverage caches are under ignored `data/`. Download files are
atomic and content length checked. `output/downloads_<year>.json` records URLs, sizes,
SHA-256 hashes, and failures. Resume reuses completed source files and only recomputes
when scientific configuration, code, relevant input file metadata, or source hashes/URLs change. Completed
annual stage outputs live under `output/years/<year>/<configuration-key>/`; the record's
`provenance` points to the exact configuration and source hashes. `failed_jobs.json`
records failures from the latest run. Expanded HDF files are removed after a successful
year; the compressed originals remain reusable. On resume, existing sources must match
the saved URL and SHA-256; changed releases or corrupted local files are downloaded again.

`output/archive_without_catch.json` documents archived identities without catch rows.
The supplied numerical 2019 regression tests skip until pointed at a complete original
366-region extraction; the annual archive subset intentionally has fewer regions.

Sources: [Copernicus product](https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/services),
[OSU Ocean Productivity](https://orca.science.oregonstate.edu/).
