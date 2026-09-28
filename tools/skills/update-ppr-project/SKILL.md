---
name: update-ppr-project
description: Use when consolidating regional selections or results into Project.xlsx, refreshing the interactive atlas, or preparing a verified project release.
---

Project.xlsx owns central paper and model metadata. Regional Overview owns selections and rationales. Numerical project tables are generated region-level outputs; do not insert taxa, catch matrices, or group coefficients into them.

Serialize central writes through one coordinator. Agents deliver patches validated against current headers and stable region/article/model keys, with portable evidence paths. Re-read/check the live workbook hash before applying a staged update. Preserve backups and unrelated records; compare by keys/content rather than row position because the updater sorts. Never overwrite a newer workbook from a stale snapshot.

For a regional path, resolve its containing project and run:

```
python tools/update_project.py --region regions/LME_028/LME_028.xlsx
python tools/build_html.py --workbook Project.xlsx --output interactive_map/index.html
```

For a full refresh use `--all` instead of `--region`. Commands are run from the project root; absolute paths and `--root` also work. The updater preserves central paper/model metadata and replaces the complete set of generated records for updated regions. The all-region build removes orphaned generated rows. Neither command executes SPPR or performs matching.

If a selected model is absent from Models & coverage, register it from its known source identity. Do not invent publication metadata. A first selection may have no results yet. If results belong to a previous model or input hashes changed, refresh the affected regional processing; never rewrite hashes merely to bypass a stale-result error. Use calculate-regional-ppr for that stage if requested. The HTML generator reads Project.xlsx, automatically locates regional workbooks for detailed views, and uses the preserved atlas source context inside the reorganized package. The output pages retain the original layouts and controls.

Selection and numerical eligibility are independent. Record authorized FAIL/NOT_RUN selections with exact restrictions and empty annual results. Use `prepare-selection` to archive/clear obsolete results. Preserve candidate history and alternative preferences; old "unselected" reports are dated evidence. Do not turn missing methods into zero or publish failed configurations just because the model is selected.

Verify one selected model per chosen region, matching IDs/paths/rationales, method restrictions, unchanged unrelated values and native tables/filters. Check atlas ranks against the documented 2019 total-catch reference, not the map's current display basis. For file-sharing errors, retain verified staging, retry transient atomic replacement within bounds, and report persistent blockers; do not force-close user applications.

For a requested knowledge-graph refresh, use Graphify on `tools/knowledge_graph`, preserving unchanged scientific evidence and indexing current source/decision reports and active skills. Verify scope, hashes, endpoints and retrieval examples. Do not parse all raw binaries or treat archived status as current authority. Verify generated map/trend fingerprints match Project.xlsx; distinguish automated payload/syntax checks from browser interaction checks.

The common-catch tables use anonymous cohort IDs to avoid transporting taxa into Project.xlsx. Paired method ratios must use their common-catch totals. Annual comparisons use a stable common region cohort and disclose per-method catch coverage. Preserve blanks, zero denominators, exact method health, source scopes, catch bases, unidentified treatments, and carbon conversion.

Verify updated regional totals, source links and missing states in Project.xlsx. Check the generated HTML, allowing its online Leaflet and font dependencies, including a region source panel, common-catch ratio, annual PPR/NPP, and unavailable data. Direct file opening must use bundled land geometry with no street-tile requests. `interactive_map/Open map.cmd` or `python tools/open_map.py` opens the map through a read-only loopback server for street detail with a real HTTP referrer. Keep the street layer below scientific overlays, use visible attribution, request only current-view tiles, and fall back to bundled land after a tile error without repeated retries. Preserve the simple-map choice. Preserve the original land source bytes and provenance under common_reference_data/geography; this display geometry must not replace scientific region boundaries or calculation inputs. Do not claim an online deployment: the local launcher is reachable only on the user's computer. Preserve alternative model and frozen experimental evidence outside production tables.

NPP source relocation or cache cleanup alone does not change regional scientific values and does not require regenerating Project.xlsx or the HTML. Shared global source files are versioned using Git LFS under `../../../common_reference_data/npp/raw/`; their source manifest and verification helper are versioned. The current extraction entry point is `../../run_npp.py`, with fresh outputs under `common_reference_data/npp/output/`. It does not automatically update workbooks. For newly adopted extraction results, first use calculate-regional-ppr to update regional NPP and its provenance and recalculate dependent ratios, then consolidate. Never replace missing NPP with zero or silently reuse the frozen archived expansion run.

Before publishing adopted NPP values, verify that their provenance links resolve to retained, versioned run evidence, including configuration, executed code and source hashes. Links only into ignored runtime output or absolute paths on one computer are insufficient for publication.

Read `../original_skill_resources/claude/ecopath-paper-to-ppr/references/integration-contract.md` for the original integration semantics, and `references/mortality-and-discards.md` relative to the same original skill when interpreting discard or mortality comparisons. Retain source-use distinctions, exact diagnostic configuration gates and experiment boundaries. Their historical repository commands are superseded by the two current scripts above. The project guide and dependency instructions are in `../../../README.md`.

Current runtime inputs are separate from historical studies: the NPP source catalog is `common_reference_data/npp/source_catalog.json`, and map source/model context is `common_reference_data/atlas_source_context/`. These paths are relative to the project root. The only directory under original_research_archive is research, containing named scientific baselines/studies. Resolve older provenance paths through `common_reference_data/provenance/archive_relocation.csv`; do not recreate legacy or reorganization_history directories or depend on deleted historical HTML pages.
