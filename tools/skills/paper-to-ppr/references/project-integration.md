# Project registry, map and knowledge graph

Apply the [evidence, execution and adoption contract](evidence-handoff.md) to this stage: explain fresh runs and honor existing scoped authorization, retain the applicable portable evidence, and verify completeness before handoff.

Paths in this reference are relative to this file unless stated as project-root paths. Domain references resolve from their current resource directory. Historical release evidence is explicitly scoped; current commands below govern publication.

Project.xlsx owns central paper and model metadata. Regional Overview owns selections and rationales. Numerical project tables are generated region-level outputs; do not insert taxa, catch matrices, or group coefficients into them.

Source metadata handoffs must include a material-availability check: current descriptor, exact retained source identity/hash, proposed correction if needed, and remaining limitations. Reconcile stale missing-file claims against verified material. Keep historical retrieval counts as history unless independently re-audited; file presence alone establishes neither scientific fidelity nor model approval.

Resolve the recorded `article_dir` as well as the publication-ID folder through the repository relocation ledger. A retained folder alias can differ from the paper ID, as in the Java Sea thesis. Keep paths inside the repository and preserve a specific current loadability assessment when discovering files; an old missing-file phrase in historical scoring must not erase that assessment.

Serialize central writes through one coordinator. Agents deliver patches validated against current headers and stable region/article/model keys, with portable evidence paths. Re-read/check the live workbook hash before applying a staged update. Preserve backups and unrelated records; compare by keys/content rather than row position because the updater sorts. Never overwrite a newer workbook from a stale snapshot.

The updater checks Project.xlsx and every supplied regional workbook again immediately before saving. If any changed during integration, it rejects the write; read the newer state, reconcile the keyed handoff and retry. Do not bypass this guard by restoring an older workbook or rewriting its freshness hashes.

Reconcile article geometry separately from coverage text. Papers/Models metadata edits do not update `Map geography` or its `article:<article_id>` payload. Compare the displayed polygon with the reviewed source footprint; retain an adequate explicitly approximate boundary, replace a conflicting polygon with an evidenced reconstruction, or clear a misleading placeholder when no defensible replacement exists. Preserve historical geometry as provenance. Use keyed old-geometry/content hashes and source-file hashes, label reconstructed boundaries and their uncertainty, and verify the actual overlay after rebuilding. The calculation region boundary and accepted scientific inputs remain unchanged.

For every saved model-selection change, update the affected region in Project.xlsx and rebuild the web pages as part of completing that selection; no separate refresh request is needed unless the user explicitly defers it. This covers first selections, replacements and cleared selections, including blocked or NOT_RUN models. Use the actual readiness status and preserve unavailable results. The same commands apply to an independently requested registry/map refresh.

Resolve the regional path and its containing project:

```
python tools/cli/region.py refresh --region regions/LME/LME_028
```

After a selection change, always rebuild the map, time-series and source pages. For registry-only changes unrelated to selection, rebuild when requested:

```
python -m tools.project_core.maps.build_html --workbook Project.xlsx --output interactive_map/index.html
```

Verify the generated pages against the saved workbook:

```
python -m tools.workflow_checks.maps.verify_html --workbook Project.xlsx --html interactive_map/index.html
```

Then check the affected region in the refreshed browser view: model dropdown, result or explicit unavailable status, diagnosis flags, and its time-series view must agree with the new selection. Generated defaults alone are insufficient: the map remembers browser model choices and URL overrides, which can keep an old model selected after a rebuild. If a remembered choice still points to the former project selection, switch that region to the newly selected model through the visible controls and verify the result; preserve unrelated browser preferences. Distinguish this saved project-selection workflow from a temporary exploratory dropdown choice, which does not change regional Overview or require rebuilding the files. Record the selection change, refresh and verification outcome in the existing selection evidence or handoff.

For a separately authorized all-region central update use `python tools/cli/project.py --all`, followed by the map builder above. The single-selection refresh command has no --all mode. Central discovery uses only canonical `regions/<type>/<unit>/<unit>.xlsx` files; adjacent review appendices are not regional calculation inputs. Commands are run from the project root or use absolute script/input paths. `--root` is an option of update_project.py; build_html.py uses `--workbook` and `--output`. The updater preserves central paper/model metadata and replaces the complete set of generated records for updated regions. The all-region build removes orphaned generated rows. Neither command executes SPPR or performs matching.

If a selected model is absent from Models & coverage, register it from its known source identity. Do not invent publication metadata. A first selection may have no results yet. If results belong to a previous model or input hashes changed, refresh the affected regional processing; never rewrite hashes merely to bypass a stale-result error. Follow regional-calculation.md for that stage if requested. The HTML generator reads Project.xlsx, automatically locates regional workbooks for detailed views, and uses the preserved atlas source context inside the reorganized package. The output pages retain the original layouts and controls.

Selection and numerical eligibility are independent. Normally record authorized FAIL/NOT_RUN selections with exact restrictions and empty annual results. When the user explicitly authorizes provisional research display of existing numeric coefficients, retain their diagnosis flags, label annual/map/trend outputs provisional and keep production eligibility false; missing coefficients remain unavailable. Selection alone does not authorize this exception. Use `python tools/cli/region.py refresh --region <canonical-region>` to save full model-local snapshots, restore compatible results or clear outgoing values as pending. Preserve candidate history and alternative preferences; old "unselected" reports are dated evidence. Do not turn missing methods into zero or present failed configurations as validated. See [size-stage-allocations.md](size-stage-allocations.md) for assumption-dependent coverage and recording.

Mapping availability is separate from coefficient availability. An accepted source-group inventory and adopted allocation may enable group controls and group-filtered independent simple-chain estimates even when Ecopath calculations are NOT_RUN. Keep the Ecopath methods unavailable, preserve diagnostic flags, and do not describe available mapping controls as model approval. Verify both the mapped subset calculation and an unavailable Ecopath method in the rendered view.

Verify one selected model per chosen region, matching IDs/paths/rationales, method restrictions, unchanged unrelated values and native tables/filters. Check atlas ranks against the documented 2019 total-catch reference, not the map's current display basis. For file-sharing errors, retain verified staging, retry transient atomic replacement within bounds, and report persistent blockers; do not force-close user applications.

For a requested knowledge-graph refresh, use Graphify on `tools/knowledge_graph`, preserving unchanged scientific evidence and indexing current source/decision reports and active skills. Verify scope, hashes, endpoints and retrieval examples. Do not parse all raw binaries or treat archived status as current authority. Verify generated map/trend fingerprints match Project.xlsx; distinguish automated payload/syntax checks from browser interaction checks.

The common-catch tables use anonymous cohort IDs to avoid transporting taxa into Project.xlsx. Paired method ratios must use their common-catch totals. Annual comparisons use a stable common region cohort and disclose per-method catch coverage. Preserve blanks, zero denominators, exact method health, source scopes, catch bases, unidentified treatments, and carbon conversion.

Verify updated regional totals, source links and missing states in Project.xlsx. Check the generated HTML, allowing its online Leaflet and font dependencies, including a region source panel, common-catch ratio, annual PPR/NPP, and unavailable data. Direct file opening must use bundled land geometry with no street-tile requests. `interactive_map/Open map.cmd` or `python tools/cli/map.py` opens the map through a read-only loopback server for street detail with a real HTTP referrer. Keep the street layer below scientific overlays, use visible attribution, request only current-view tiles, and fall back to bundled land after a tile error without repeated retries. Preserve the simple-map choice. Preserve the original land source bytes and provenance under common_reference_data/geography; this display geometry must not replace scientific region boundaries or calculation inputs. Do not claim an online deployment: the local launcher is reachable only on the user's computer. Preserve alternative model and frozen experimental evidence outside production tables.

NPP source relocation or cache cleanup alone does not change regional scientific values and does not require regenerating Project.xlsx or the HTML. Shared global source files are versioned using Git LFS under project-root `common_reference_data/npp/raw/<product>/<year>/`; their source manifest and verification helper are versioned. The current extraction entry point is `python tools/cli/npp.py`, with fresh outputs under `common_reference_data/npp/output/`. It does not automatically update workbooks. For newly adopted extraction results, first follow regional-calculation.md to update regional NPP and its provenance and recalculate dependent ratios, then consolidate. Never replace missing NPP with zero or silently reuse the frozen archived expansion run.

Before publishing adopted NPP values, verify that their provenance links resolve to retained, versioned run evidence, including configuration, executed code and source hashes. Links only into ignored runtime output or absolute paths on one computer are insufficient for publication.

Read [the retained integration semantics](../resources/mapping/references/integration-contract.md) for the original integration semantics, and [mortality and discards](../resources/extraction/references/mortality-and-discards.md) when interpreting discard or mortality comparisons. Retain source-use distinctions, exact diagnostic configuration gates and experiment boundaries. Historical release counts and study findings remain historical; current publication uses the commands above. The project guide and dependency instructions are in [README](../../../../README.md).

Current runtime inputs are separate from historical studies: the NPP source catalog is `common_reference_data/npp/source_catalog.json`, and map source/model context is `common_reference_data/atlas_source_context/`. These paths are relative to the project root. Named substantive scientific baselines/studies live under `research/{human,agents}/<study_id>/`; no obsolete archive tree is retained. Resolve older provenance paths through `common_reference_data/provenance/source_paths.csv`; do not recreate legacy or reorganization_history directories or depend on deleted historical HTML pages.
