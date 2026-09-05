# PPR Ecopath Atlas

Open **index.html** for the interactive map, or **archive/index.html** for the searchable source archive. The map retains the supplied design and shows the exact 167 ecosystems in the source workbook's **Global Estimation** sheet: 66 LMEs, 84 EEZs and 17 High Seas regions.

## Using the map

- Choose a PPR year from 1950–2019. The ecosystem set stays fixed; ranks, shares, cumulative colors and totals update.
- Filter by ecosystem type, global selected-set rank, article quality, or local verified file availability.
- Select a region to inspect its studies. File buttons open the actual archived source materials.
- Red markers represent earlier, high-PPR ranks; green markers represent later cumulative shares. Gray markers indicate missing PPR, not zero catch.
- The polygon-color switch and article-footprint switch operate independently. Approximate study envelopes are dashed. A missing study boundary is stated explicitly and is not replaced by an invented polygon.

PPR uses the source calculation at TE=0.1. The 2019 selected-set sum is approximately 74.341 billion tonnes PP equivalent. It retains the workbook's whole-region overlap and missing-data limitations; it is not a verified spatially deduplicated global total. The map's article evidence does not establish PPR coverage.

## Evidence and files

All 84 selected EEZs have targeted public-literature search records in **data/eez_searches.csv**. The expanded search across all 66 LMEs is recorded in **data/lme_searches.csv**. This is an expanded, documented literature search, not a claim that every published model has been located. A documented gap means that this search did not locate a defensible model; it does not prove none exists. Whole-EEZ studies, subregional studies and basin proxies are distinguished. Conference abstracts and related theses remain explicitly described in their source notes.

All cataloged sources received real download attempts. **data/retrieval_summary.csv** provides one row per source and **data/download_attempts.csv** records individual requests and outcomes, including DOI, publisher, repository and Zotero routes. Zotero metadata and supplied attachment links were read through the connector; failed attachment requests are retained in the audit. Publisher and author copies were pursued independently of Zotero. **research/file_identity_review.json** records the review of newly retrieved main PDFs, including related theses and manuscript versions.

**data/articles.csv** contains article-to-region assignments; **data/files.csv** contains original filenames, source URLs, current validation status and SHA-256 hashes. Duplicate publications found in independent searches are reconciled by DOI. A source can support several regional assignments without counting as several distinct publications.

The original all-84 ZIP was read directly and its 540 files recovered to short generated paths. **inputs/zip_recovery.json** maps every original ZIP member to its recovered path. No Windows long-path setting was changed. Every verified PDF, supplement and model archive is copied into its article directory under **archive/regions/<ecosystem>/<article>/**. Short readable filenames avoid long-path errors. A deduplicated copy is retained in **archive/files/** for reproducibility; **data/article_files.csv** maps all article-folder copies.

One original East China Sea PDF was damaged. Its original bytes are retained and marked `validation_failed`; a newly retrieved, readable 15-page replacement is included. `downloaded_verified` means the local file passed format/structure validation, not that an Ecopath database successfully loaded. The public NOAA FTP archive supplied the Hawaii input/diet/output CSVs when its web download page failed.

## Quality interpretation

The inherited rubric is preserved: 55 points for model loadability, 20 for documentation, 15 for spatial fit, and 10 for recency/validation. New scores are provisional screening assessments. No model was load-tested in this project.

- No verified file: total score capped at 25.
- Readable main source, unaudited model completeness: loadability 20, documentation 10, total capped at 58.
- Verified parameter/diet tables (Hawaii and Tasman/Golden Bays): loadability 35, documentation 15, total capped at 72. Native EwE import and balance remain untested.
- Sources whose numerical basic parameters and diet tables were inspected receive loadability 35/55, documentation 18/20, and cap 76. The audit names the tables/pages. Presence of a native database is documented separately from successful loading.
- New spatial-fit values: whole EEZ 15, subregional 7, basin proxy 3. Recency is 7 for 2015 onward and 3 otherwise; this component does not assert independent model validation.

Original quality fields remain in the input snapshot. Geographic and bibliographic corrections are recorded explicitly, including Darwin/Wolf Islands, Kerguelen EEZ versus High Seas, the Pacific warm-pool study extent, and the Northwest Africa compilation. Confidential or unavailable model inputs remain stated as limitations.

## Rebuilding

Python 3.12 is recommended. From this project directory:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe build_atlas.py
.venv/Scripts/python.exe verify_atlas.py
.venv/Scripts/python.exe -m unittest discover -s tests
```

Rebuilding from the included input snapshots and research records requires no network. To attempt new or updated public source URLs, run `download_sources.py`; `download_noaa.py` retrieves the published Hawaii FTP dataset. Retrieval results are incremental and include unsuccessful attempts. No Zotero library was modified.

If local file navigation is restricted by a browser, serve the project locally:

```powershell
.venv/Scripts/python.exe -m http.server 8773 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8773`. The map uses Leaflet and OpenStreetMap tiles from public CDNs/services, so map rendering requires internet access; the archive index and local source files do not.

## Provenance and reproducibility

- Workbook snapshot: **inputs/PPR_global_summary.xlsx**, Global Estimation selected set and annual regional results.
- Original map, generator and summary workbook: **inputs/**, copied from article_map_version_1.
- Raw EEZ evidence: **research/eez_a.json**, **eez_b.json**, **eez_c.json**.
- File retrieval logs: **research/downloads/**.
- Validation results: **data/validation.json**.

The previous projects and the original ZIP remain unchanged. Research, file retrieval and review were performed on 2026-09-04.

## Expanded retrieval and remaining gaps

The supplied Cheung 2007 thesis and CMFRI Bulletin 51 were incorporated and audited. The Karnataka bulletin is dated 2008; its historical ARAB-2005 identifier is retained. The expanded search followed publisher, author, institutional repository and report/thesis routes after blocked downloads. Exact-DOI Figshare deposits provide supplements and supporting tables. Ordinary HTML landing pages, HTTP errors and authentication screens never count as recovered files. Some archived responses contain literal HTTP headers before a complete PDF; those headers are removed only after confirming the PDF payload, with raw response hashes and transformations recorded.

**data/unretrieved_main_sources.csv** lists sources whose main text remains unretrieved (even if supplements exist). **docs/lme-expansion-report.md** summarizes actual counts and limitations. **research/lme_*.json** records page/table audits and source identity reviews. Run **discover_supplements.py** and **discover_alternates.py** to refresh public discovery metadata, then **download_sources.py** to attempt the candidate routes and **build_atlas.py** to update the article folders and map.
