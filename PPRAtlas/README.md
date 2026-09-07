# PPR Ecopath Atlas

Open **index.html** for the interactive map, or **archive/index.html** for the searchable source archive. The map retains the supplied design and shows the exact 167 ecosystems in the source workbook's **Global Estimation** sheet: 66 LMEs, 84 EEZs and 17 High Seas regions.

Open **trends.html**, or choose **Time series** in the map header, for annual PPR and
PPR/NPP graphs. Every ecosystem's map details include a link to its own graph.

## Annual graphs

- All PPR masses displayed anywhere on the site use **tonnes carbon (t C)**:
  source wet-weight PPR is divided by 9 once. This applies to map values,
  tooltips, legends, method-ratio component masses, graph axes/readouts and
  plotted-data CSV downloads (`ppr_tonnes_carbon`). Source workbooks and the
  audited annual input JSON retain wet-weight values. Catch remains wet weight;
  recycling diagnostics and dimensionless method ratios are not converted.
- Choose PPR or PPR/NPP, a PPR method, source scope and NPP method. The simple
  trophic-chain option uses catch-taxon TL at TE=0.1; `SPPR_1995_TE0.1` uses model
  TL. Identical formulas can differ because these trophic-level inputs differ.
- **Change** opens the ecosystem picker: original global LME + High Seas set,
  selected pilot, LMEs, High Seas, all EEZs, atlas catalog, or a custom selection.
  All 366 known identities are selectable. The two Arctic units without catch
  remain missing. The map's ten-ecosystem coloring gate is unchanged.
- The curve sums the selected ecosystems that have a complete annual series for
  the chosen method. The same cohort is used for every plotted year. For model
  methods, choose a separate model version per ecosystem in the picker. Models
  are never averaged; failed and unverified estimates remain unavailable.
- NPP choices are Antoine–Morel, VGPM, Eppley, CbPM, CAFE and regional ensemble
  median. **The owner requested repeating the fixed 2019 NPP for all years for
  now.** This denominator is labeled on the graph. Annual NPP can later replace
  the scalar values with arrays aligned to the exported years.
- PPR/NPP (%) = `100 × sum(PPR tonnes carbon) / sum(NPP tonnes carbon)`.
  The PPR input has already been divided by 9; do not convert it again.
  Numerator and denominator use the same ecosystems, excluding those without
  positive NPP. The regional ensemble option sums the individual region medians;
  it is not the median of the global model totals or a mean of regional ratios.
- Hover over the curve or use the keyboard-accessible **Inspect year** slider.
  Set **First year** and **Last year** to compare a shorter period. Single-region
  links open the available catch span; missing years inside it remain gaps in
  the curve. Regional sums exclude incomplete series for the chosen period so
  changing coverage cannot create a false trend.
  **Download plotted data** includes exact values, catch coverage, included IDs,
  calculation choices, model overrides and resolved model IDs. Coverage and sources lists exclusions.
  Method coefficients and TLs are fixed across years; boundaries may overlap.

Refresh from the repository root after refreshing the network atlas:

```powershell
python -X utf8 tools/build_time_series.py
```

This verifies all source/workbook hashes and annual totals, then writes
`data/time_series.json`, the portable `trends.html`, and the audit at
`../data/time_series_validation.json`. Use `--check` to validate the saved export
without writing files. The graph page embeds its inputs and needs no network.

## Using the map

- Choose annual PPR, a ratio between methods, recycling `b`, or `rho living`.
- Switch between all sources, inner sources (no imports), and primary producers only.
- Select numerator/denominator methods for ratios. Both use identical available catch taxa;
  the details panel reports catch coverage. Missing values and zero denominators stay unavailable.
- Choose GE or TE for recycling. Values come from the upstream `diagnose_sppr()` output,
  with status and configuration. Both spectral radii must be below 1 for convergence;
  these conditions are necessary, not sufficient.
- Click an ecosystem to choose its model and open the actual SPPR/PPR workbooks. Models
  are kept separate. The year selector spans1950–2019; recycling is fixed for each model.
- Only the ten ecosystems in `../data/atlas_selection.json` may be colored. Candidate
  articles do not authorize new estimation coverage. Unselected and unavailable ecosystems
  stay gray. The isolated Saygu2025 validation does not color the North Sea.
- The article-area switch shows explicitly selected catalog sources only. Archived
  alternatives remain readable in the details panel. Approximate envelopes are dashed.

Displayed PPR uses mapped catch × scoped SPPR ÷ 9 (tonnes carbon). Failed configurations and negative source-group SPPR
are excluded from map estimates; finite diagnostic values remain inspectable with FAIL
labels. Coefficients stay fixed across catch years. Geographic transfers and historical
identity conflicts are stated in the details; no spatially deduplicated global total is claimed.

## Evidence and files

All 84 selected EEZs have targeted public-literature search records in **data/eez_searches.csv**. The expanded search across all 66 LMEs is recorded in **data/lme_searches.csv**. This is an expanded, documented literature search, not a claim that every published model has been located. A documented gap means that this search did not locate a defensible model; it does not prove none exists. Whole-EEZ studies, subregional studies and basin proxies are distinguished. Conference abstracts and related theses remain explicitly described in their source notes.

All cataloged sources received real download attempts. **data/retrieval_summary.csv** provides one row per source and **data/download_attempts.csv** records individual requests and outcomes, including DOI, publisher, repository and Zotero routes. Zotero metadata and supplied attachment links were read through the connector; failed attachment requests are retained in the audit. Publisher and author copies were pursued independently of Zotero. **research/file_identity_review.json** records the review of newly retrieved main PDFs, including related theses and manuscript versions.

**data/articles.csv** contains article-to-region assignments; **data/files.csv** contains original filenames, source URLs, current validation status and SHA-256 hashes. Duplicate publications found in independent searches are reconciled by DOI. A source can support several regional assignments without counting as several distinct publications.

The original all-84 ZIP was read directly and its 540 files recovered to short generated paths. **inputs/zip_recovery.json** maps every original ZIP member to its recovered path. No Windows long-path setting was changed. Every verified PDF, supplement and model archive is copied into its article directory under **archive/regions/<ecosystem>/<article>/**. Short readable filenames avoid long-path errors. A deduplicated copy is retained in **archive/files/** for reproducibility; **data/article_files.csv** maps all article-folder copies.

One original East China Sea PDF was damaged. Its original bytes are retained and marked `validation_failed`; a newly retrieved, readable 15-page replacement is included. `downloaded_verified` means the local file passed format/structure validation, not that an Ecopath database successfully loaded. The public NOAA FTP archive supplied the Hawaii input/diet/output CSVs when its web download page failed.

## Quality interpretation

The inherited rubric is preserved: 55 points for model loadability, 20 for documentation, 15 for spatial fit, and 10 for recency/validation. New scores are provisional screening assessments. Pilot models have now been loaded and evaluated through the integration tools. The inherited catalog scores remain screening scores; numerical configuration health is reported separately.

- No verified file: total score capped at 25.
- Readable main source, unaudited model completeness: loadability 20, documentation 10, total capped at 58.
- Verified parameter/diet tables (Hawaii and Tasman/Golden Bays): loadability 35, documentation 15, total capped at 72. Native EwE import and balance remain untested.
- Sources whose numerical basic parameters and diet tables were inspected receive loadability 35/55, documentation 18/20, and cap 76. The audit names the tables/pages. Presence of a native database is documented separately from successful loading.
- New spatial-fit values: whole EEZ 15, subregional 7, basin proxy 3. Recency is 7 for 2015 onward and 3 otherwise; this component does not assert independent model validation.

Original quality fields remain in the input snapshot. Geographic and bibliographic corrections are recorded explicitly, including Darwin/Wolf Islands, Kerguelen EEZ versus High Seas, the Pacific warm-pool study extent, and the Northwest Africa compilation. Confidential or unavailable model inputs remain stated as limitations.

## Refreshing network results

From the repository root, after building and verifying model workbooks:

```powershell
python -X utf8 tools/build_network_atlas.py
```

This reads the existing catalog, writes `data/network_ppr.json` and renders `index.html`
without refetching articles or changing the selected ecosystem set. A full atlas rebuild
also includes this network file when present; refresh it after model/mapping changes.

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
