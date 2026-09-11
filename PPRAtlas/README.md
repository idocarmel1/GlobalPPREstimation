# PPR Ecopath Atlas

The map and linked graph offer three catch bases: **landings** (default),
**all catch**, and **discards only**. Each PPR numerator is calculated from that
basis at taxon resolution, including reported and unreported amounts. Switching
bases does not apply a region-wide retained/discarded percentage to an old PPR.

In the landings view, **Discard-routing sensitivity** can be shown or hidden.
Where a tested model, method, source scope and source hashes are compatible, the
range applies alternative routing coefficients to the same landed vector, at the
observed annual `D/(L+D)`. Only valid adjacent computed intervals are interpolated.
All-catch and discards-only views have no routing envelope. An unsupported case
says **not assessed**, never zero uncertainty. The range is not a confidence
interval; NPP model spread remains separate. See the
[study and methods](../research/discard_sensitivity_2026_09_10/README.md).

Source workbook downloads retain their original total-catch calculations and exact
final mappings. Use the plotted-data download for the selected catch-basis results.
URLs and downloads preserve catch basis, sensitivity visibility and the existing
year, method, source-scope, NPP and unidentified-taxon settings.

Open **index.html** for the interactive map, or **archive/index.html** for the searchable source archive. The map shows all **366 ecosystems: 66 LMEs, 282 EEZs and 18 High Seas regions**. The original **167-region Global Estimation** selection remains the curated article archive; displaying an additional ecosystem does not imply article extraction or model verification.

The map opens with **simple trophic chain**, calculated directly from each taxon's selected catch basis and reference trophic level at TE=0.1. It provides PPR and regional PPR/NPP independently of articles and models, in All-source scope. Model-specific methods retain their selected-model verification gates. The two no-catch identities, HS_018 and LME_064, remain visible with unavailable PPR. The All filter includes missing results; numeric Top filters include ranked results only. Scientific source polygons are preserved; only new display geometry is simplified.

Open **trends.html**, or choose **Time series** in the map header, for annual PPR and
PPR/NPP graphs. Every ecosystem's map details include a link to its own graph.

## Annual graphs

- All PPR masses displayed anywhere on the site use **tonnes carbon (t C)**:
  source wet-weight PPR is divided by 9 once. This applies to map values,
  tooltips, legends, method-ratio component masses, graph axes/readouts and
  plotted-data CSV downloads (`ppr_tonnes_carbon`). Source workbooks and the
  audited annual input JSON retain wet-weight values. Catch remains wet weight;
  recycling diagnostics and dimensionless method ratios are not converted.
- Choose PPR or PPR/NPP, one or more PPR methods, source scope and NPP method. The simple
  trophic-chain option uses catch-taxon TL at TE=0.1; `SPPR_1995_TE0.1` uses model
  TL. Identical formulas can differ because these trophic-level inputs differ.
- **PPR calculations** opens a checkbox picker. Each selected method has its own
  curve and inspected-year value; one selected method keeps the original teal
  curve and shaded area. Multiple curves use colors and, for larger selections,
  distinct line patterns. Unavailable methods are named with their reasons.
- **Divide by baseline** optionally divides every selected curve by another
  method for the same year, ecosystems, source scope and model choices. The
  baseline appears as a curve only when also selected. Relative values are
  dimensionless multiples (×); baseline/self is 1 where the baseline is positive.
  Missing or zero denominators remain gaps. Choosing **None** restores absolute
  PPR or PPR/NPP. In normalized PPR/NPP, the common NPP denominator cancels.
- **Change** opens the ecosystem picker: original global LME + High Seas set,
  selected pilot, LMEs, High Seas, all EEZs, atlas catalog, or a custom selection.
  All 366 known identities are selectable. The two Arctic units without catch
  remain missing for PPR. Simple-map coloring is independent of the ten selected model regions.
- The curve sums the selected ecosystems that have a complete annual series for
  the chosen method. The same cohort is used for every plotted year. For model
  methods, choose a separate model version per ecosystem in the picker. Models
  are never averaged; failed and unverified estimates remain unavailable.
  Comparisons use the intersection of ecosystems available to the usable curves
  and the baseline. A wholly unavailable selected method is disclosed without
  suppressing valid curves; an unavailable baseline makes relative values
  unavailable. Method totals can cover different catch taxa, so each curve
  reports its own catch coverage. Unlike the map's ratio calculation, these
  annual comparisons do not recompute totals over common catch taxa.
- NPP choices are Antoine–Morel, VGPM, Eppley, CbPM, CAFE and regional ensemble
  median. Inputs are year-specific, with unavailable years blank by default.
  All 366 identities have an ensemble estimate in every year from 1998–2019,
  including the two identities without catch. Per-model support remains explicit;
  an available ensemble does not imply full satellite-water coverage.
  **Missing historical NPP** optionally uses each ecosystem/method's earliest available
  value for earlier years only. These are labeled estimates, including source years
  in the inspector and CSV; internal gaps and later missing years remain blank.
  This option makes a constant-value proxy, not a historical satellite observation.
- PPR/NPP (%) = `100 × sum(PPR tonnes carbon) / sum(NPP tonnes carbon)`.
  The PPR input has already been divided by 9; do not convert it again.
  Numerator and denominator use the same fixed PPR-valid ecosystems. A year is
  unavailable if any included ecosystem lacks positive NPP; changing NPP coverage
  cannot silently change the cohort. The regional ensemble option sums regional medians;
  it is not the median of the global model totals or a mean of regional ratios.
- Hover over the curve or use the keyboard-accessible **Inspect year** slider.
  Set **First year** and **Last year** to compare a shorter period. Single-region
  links open the available catch span; missing years inside it remain gaps in
  the curve. Regional sums exclude incomplete series for the chosen period so
  changing coverage cannot create a false trend.
  **Download plotted data** includes exact values, catch coverage, included IDs,
  calculation choices, model overrides and resolved model IDs. Coverage and sources lists exclusions.
  Multiple-method or baseline downloads use one row per method and year, with
  original carbon totals, denominator values, resolved baseline model IDs and
  reasons for unavailable values. Single-method downloads without a baseline
  use one row per year, including catch-basis and sensitivity fields. Shared URLs and ecosystem links preserve the
  selected methods and baseline; existing `method=` links still work.
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

- Choose annual PPR, PPR/NPP, a ratio between methods, recycling `b`, or `rho living`.
- NPP details follow the selected year and method. Model and central workbooks
  expose the final catch-taxon mappings, including exact numerical weights.
- Switch between all sources, inner sources (no imports), and primary producers only.
- Select numerator/denominator methods for ratios. Both use identical available catch taxa;
  the details panel reports catch coverage. Missing values and zero denominators stay unavailable.
- Choose GE or TE for recycling. Values come from the upstream `diagnose_sppr()` output,
  with status and configuration. Both spectral radii must be below 1 for convergence;
  these conditions are necessary, not sufficient.
- Click an ecosystem to choose its model and open the actual SPPR/PPR workbooks. Models
  are kept separate. The year selector spans1950–2019; recycling is fixed for each model.
- Model-based coloring requires a verified selected model in `../data/atlas_selection.json`.
  Independent simple-chain coloring uses catch and reference TL across all ecosystems.
  Candidate articles do not authorize model-based coverage; the isolated Saygu2025
  validation remains separate from production model selection.
- The article-area switch shows explicitly selected catalog sources only. Archived
  alternatives remain readable in the details panel. Approximate envelopes are dashed.

Displayed PPR uses the selected taxon catch basis × mapped scoped SPPR ÷ 9 (tonnes carbon). Failed configurations and negative source-group SPPR
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

Unidentified-catch sensitivity is available in both map and graph: selected-method SPPR (default), a zero-contribution assumption, or each affected taxon's reference-TL chain. The controls preserve catch tonnage and show the affected share; URLs and downloads record the choice. The reference chain is total-only and unavailable in inner/PP source scopes. See [the definition and methods](../docs/UNIDENTIFIED_CATCH.md) and [the exact affected taxa](../data/unidentified_taxa.json).

## NPP through time and denominator geography

The graph's **Measure** selector includes **NPP** in tonnes carbon per year.
This curve uses the chosen annual NPP calculation for the selected ecosystems,
independently of catch, Ecopath-model availability or PPR method. It appears once,
even if several PPR methods were previously selected. PPR-specific controls are
disabled without losing their selections. A missing required regional value
leaves a gap in the fixed selected sum; a genuine NPP zero remains zero.

For **PPR / NPP**, **NPP denominator** offers:

- **Selected ecosystems**: selected PPR divided by the sum of NPP for the same
  included PPR ecosystem cohort. This preserves the previous graph behavior.
  Choosing the regional ensemble sums regional medians; it is not the median of
  global model totals. Selected regional boundaries may overlap.
- **Global atlas NPP**: selected PPR divided by a separate, fixed atlas reference
  ensemble. PPR ecosystem/method selection and PPR exclusions cannot change this
  denominator. It uses a dissolved union of all 66 LME and 18 high-seas input
  polygons, including the two identities without catch. EEZs are not added.
  The existing NPP method is applied once to this union; the ensemble median is
  taken after computing each model's union-wide total. This is a coverage-limited
  atlas reference, not total world-ocean NPP. Satellite-supported water area,
  fill limits and algorithm support are recorded for each year. See
  [reference definition and reproduction](../docs/GLOBAL_ATLAS_NPP_REFERENCE.md).

Both discard-routing endpoints use exactly the same denominator as their central
PPR estimate. Normalized method comparisons remain dimensionless multiples and
have no routing envelope. NPP-only mode never normalizes a mass by a PPR method.
The map retains its own regional denominator behavior.

Annual missing values stay blank by default. The explicit earliest-year option
uses a constant earlier-year proxy, preserves source year and support, and cannot
fill internal/later gaps. For global scope the proxy uses the earliest computed
reference ensemble on the same fixed union, not separately filled regional sums.
Reference source coverage remains visible even when the value is a proxy.

URLs record `metric=npp` or `metric=ratio` and `npp_scope=selected|global`.
CSV and JSON downloads retain numeric NPP/denominator values, reference identities,
geography, overlap policy, ensemble convention, annual support, source/provenance
and substitutions. Downloads stay available for missing-value audit records.
