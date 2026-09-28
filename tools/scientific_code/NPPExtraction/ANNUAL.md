# Annual NPP extraction in the current repository

The active implementation is `tools/scientific_code/NPPExtraction`. Run it through
`tools/run_npp.py` or install this package and use `python -m npp.annual`.
Both entry points resolve the repository independently of the working directory.

The annual workflow reads region identities from `regions/<unit_id>/` and actual
catch years from `regions/<unit_id>/raw/<unit_id>.csv.gz`. For each selected complete
source year, it includes every current region, including regions without catch.
It does not invent catch values. The current repository contains 366 identities.

## Runtime locations

All paths below are relative to the repository root:

| Location | Purpose |
|---|---|
| `common_reference_data/npp/raw/` | Original monthly downloads and source geometry, versioned with Git LFS |
| `common_reference_data/npp/decoded/` | Rebuildable exact float32 Copernicus raster cache |
| `common_reference_data/npp/work/` | Rebuildable coverage, masks, annual accumulators and selected geometry |
| `common_reference_data/npp/output/` | New annual CSV, download manifests, source catalog and provenance |
| `common_reference_data/npp/output/single_year/` | Standalone `npp.cli` CSVs and workbook |

The decoder already derives its cache as `raw_dir.parent / decoded`; the new raw
location therefore places it in the shared NPP runtime tree automatically. Generated
annual geometry selections go under `work/geometry`, preserving raw geometry bytes.
No runtime output is written into the historical archive.

The original source files are included in Git through Git LFS, not replaced with
download URLs. After cloning, install Git LFS and run `git lfs pull` from the repository
root before verification or extraction. `tools/verify_npp_sources.py` checks the local
payloads against the source manifest; LFS pointer text is not usable scientific data.
Only decoded, work and runtime output directories are ignored and rebuildable.

The published September 2026 annual CSV and its original helper, snapshots and audit
records remain frozen under
[`original_research_archive/research/npp_extraction_2026_09`](../../../original_research_archive/research/npp_extraction_2026_09/).
The current runner creates a separate extraction. It does not replace that published
release, copy its values into a new run, refresh regional workbooks or publish results.
The historical expansion helper remains an archived reproduction artifact; the current
runner directly includes all region identities and does not require that helper.

## Installation

From the repository root, using Python 3.13 (the tested Windows environment):

```powershell
python -m venv tools/scientific_code/NPPExtraction/.venv
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe -m pip install -r tools/scientific_code/NPPExtraction/requirements-lock.txt
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe -m pip install -e tools/scientific_code/NPPExtraction --no-deps
```

On Linux/macOS, use `.venv/bin/python` for the interpreter path. For a compatible
unlocked environment with Python 3.11 or newer, install the package with its test extra
instead: `python -m pip install -e "tools/scientific_code/NPPExtraction[test]"`.
The locked NumPy/SciPy versions require Python 3.12 or newer. HDF4 support is supplied
by the tested Windows `pyhdf` wheel; other platforms may need the HDF4 system library.
Unicode repository paths are supported by the native-reader workarounds.

## Plan, verify and run

Commands below run from the repository root. An absolute path to `tools/run_npp.py`
works from another directory with the same default data locations.

```powershell
# Offline plan using a saved source catalog; writes a separate runtime plan and CSV.
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe tools/run_npp.py plan --years 1998:2019

# Verify shared original source bytes before a recomputation.
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe tools/verify_npp_sources.py

# Full extraction: substantial disk, memory and runtime required.
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe -u tools/run_npp.py run --years 1998:2019
```

`plan` uses `common_reference_data/npp/output/source_catalog.json`, falling back to
the frozen shared source catalog if the runtime copy is absent. It does not contact
source servers unless `--refresh-sources` is explicitly supplied. If neither catalog
exists, it requests a source probe instead of silently downloading metadata.
`probe` explicitly discovers source availability and writes the runtime catalog:

```powershell
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe tools/run_npp.py probe
```

Fresh clones reuse original monthly files through the tracked
`common_reference_data/npp/source_manifest.json`; ignored runtime download manifests
are not required. Each reuse checks the catalog URL and freshly hashes the raw bytes.
Size and modification time cannot bypass this check. An existing manifest-listed
original with a different hash or URL is preserved and the run fails explicitly;
restore the Git LFS original or use a separate source release/workspace. A missing
original may be downloaded at its recorded URL, but its SHA-256 must match before it
is placed at the original path. New files outside the original manifest retain the
existing download/resume behavior.

Historical `downloads_<year>.json` records under
`original_research_archive/research/npp_extraction_2026_09/output/` may optionally be
copied into runtime output. The versioned default catalog is
`common_reference_data/npp/source_catalog.json`.
Keep the archive unchanged and do not copy its annual CSV. Runtime and original
metadata with conflicting hashes for the same URL cause an explicit error.
Do not run a second raster worker concurrently against the same runtime directories.

Without `--years`, selected years are the union of actual catch years. Unsupported
catch years retain blank NPP rows; each selected supported year adds every identity.
Use `--years start:end` or comma-separated years for an explicit range, especially for
NPP beyond the catch record. Previously extracted runtime NPP-only years are retained
when planning or running another range. `--root` selects a different repository-shaped
workspace, placing all new annual runtime outputs under that root.

`--config path.yaml` changes scientific settings. The annual runner enforces the native
Antoine-Morel 4 km reference baseline, available model membership and complete source
years. Its centered five-year source window is clipped at source boundaries. There is
no extrapolation to an unsupported target year. YAML directory paths are relative to
the YAML file; absolute paths remain absolute. Annual runtime paths are set by `--root`.
Standalone CLI path overrides remain relative to the caller's working directory.

## Scientific output contract

`common_reference_data/npp/output/annual_npp.csv` contains actual catch-year rows plus
selected supported identity/year rows, with five `npp_<model>_tC_yr` fields and the
median/minimum/maximum of finite models. Values are annual tonnes of carbon. The
scientific aggregation, gap filling, polar-night handling and model-ratio algorithms
are unchanged; see [`METHODS.md`](METHODS.md).

Each model estimate scales the gap-filled Antoine-Morel baseline by the model ratio
on common coverage, with the existing own-coverage fallback when common coverage is
sparse. Neighboring years fill missing pixels within a supported target year; they do
not create observations outside the satellite record. The minimum-maximum range is
model spread, not a statistical confidence interval. A one-model median is that model,
not a five-model ensemble.

`n_models`, `available_models`, `ensemble_basis`, `model_status`, `window_years` and
`method` expose coverage and ensemble membership. Missing numeric cells are blank,
never zero. Status distinguishes `unsupported`, `pending`, `source_error`, `failed`,
`partial`, `missing` and `complete`. Complete means five usable algorithm estimates,
not complete satellite-water coverage. Regions absent after geometry repair receive
explicit missing records. `archive_without_catch.json` retains the historical filename
but now reports current region identities lacking catch rows.

Annual checkpoints are stored under `output/years/<year>/<configuration-key>/`;
records point to the actual runtime provenance path. The key includes scientific
configuration, geometry, code, source metadata, URL and content hashes. Relocation
therefore invalidates old derived checkpoints intentionally. Raw source files remain
reusable after validation. Expanded HDF copies are removed after a completed year.

A historical extraction needs tens of GB for source files, several GB of RAM and
substantial computation. The full decoded cache can need roughly 45-50 GB more.
`--workers` controls concurrent downloads only; annual raster calculations are serial.

## Verification

```powershell
tools/scientific_code/NPPExtraction/.venv/Scripts/python.exe -m pytest tools/scientific_code/NPPExtraction/tests -q
```

The suite includes current-layout paths, offline planning, NPP-only identity membership,
raw geometry preservation, source-reader checks, synthetic annual integration and exact
numeric accumulator parity with the frozen supplied ZIP. The 23 published-2019 numerical
checks need a completed full-region single-year extraction; set `NPP_OUT_DIR` to it.
Without those outputs, they skip. Planning and tests do not establish that a full raster
recomputation has completed or that newly generated results reproduce the frozen release.
