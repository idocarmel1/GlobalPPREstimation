# Shared global NPP inputs

The original monthly satellite rasters are global, shared inputs. Keep one copy
here; do not distribute them among overlapping EEZ, LME and high-seas folders.

| Location | Contents | Versioned in Git |
|---|---|---|
| `raw/copernicus/` | 288 original monthly NetCDF files | Git LFS |
| `raw/osu/` | 816 original monthly compressed HDF files | Git LFS |
| `raw/sau_*.geojson` | Six boundary files, including three full-region collections | Git LFS |
| `source_catalog.json` | Saved model/year/month source availability for offline planning | Yes |
| `source_manifest.json` | Portable paths, sizes, SHA-256 and monthly source URLs | Yes |
| `decoded/` | Regenerable decoded satellite rasters | No |
| `work/` | Regenerable coverage, masks and calculation intermediates | No |
| `output/` | New extraction runs, catalog, download records and provenance | No |

The complete local input inventory is 1,110 files: 1,104 monthly satellite files
and six geography files. On 2026-09-28 the monthly bytes were checked against the
preserved original download SHA-256 records before relocation. Every file was
hashed again after relocation. `source_manifest.json` records the verified bytes.
The 32 GB original collection is versioned using Git LFS. Git stores pointers and
GitHub LFS stores the original bytes. Run `git lfs install` and `git lfs pull` after
cloning, then run the verifier below. A checkout with LFS pointer text instead of
the original files will fail verification. Derived caches and new outputs remain
local and can be rebuilt from preserved inputs.

From the project root, verify all recorded source bytes without modifying them:

```powershell
python tools/verify_npp_sources.py
```

Current extraction code and setup instructions are in
[`../../tools/scientific_code/NPPExtraction/`](../../tools/scientific_code/NPPExtraction/).
The current annual entry point is `python tools/run_npp.py plan` or `run` using
the NPP environment. Review the plan before starting the expensive raster run.
Outputs from new runs go to `output/`; historical published results stay in
[`../../original_research_archive/research/npp_extraction_2026_09/`](../../original_research_archive/research/npp_extraction_2026_09/).
The original all-region expansion helper and its execution snapshots in that
archive are historical evidence, not the current entry point.

Annual regional results already exist in each `regions/<ID>/<ID>.xlsx`, on the
NPP sheet, and in `Project.xlsx` on Regional NPP. New extraction output does not
automatically replace those reviewed workbook values. Keep algorithm membership,
availability, gap-fill basis and provenance when adopting a new result, then
recalculate regional ratios and refresh the project with the current workflow.
Before adoption, retain the run's provenance, configuration, executed code and
source hashes in a versioned evidence folder and use portable workbook links to
that evidence. An adopted run's evidence is not disposable runtime output.

The three files in a region's `raw/` directory are catch inputs: the original
catch ZIP, exploited-organism reference JSON, and derived annual catch CSV.GZ.
They contain no satellite NPP. Regional NPP raster subsets, if produced later,
are derived products and do not replace these shared global originals.

Historical provenance may mention `NPPExtraction/data/raw/`. Map its suffix to
this directory's `raw/` and verify the recorded hash; do not rewrite frozen
provenance or reuse an old computation checkpoint as a new run.
