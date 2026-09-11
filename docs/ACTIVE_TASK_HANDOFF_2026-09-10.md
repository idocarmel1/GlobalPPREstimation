# Active task handoff — September 10, 2026

**Historical starting handoff:** the global and regional extractions described
below have since completed. Read `CONTINUATION_PROGRESS_2026-09-10.md` for the
latest state and active final-build sessions before acting on process instructions.

This is the compact continuation record for a fresh Codex task requested by the user to reduce context cost. Continue the existing saved checkout; substantial work is uncommitted and staged. Do not restart from Git HEAD or repeat completed scientific extraction. The prior implementation plan explicitly authorizes this checkout. Read other documents only as needed.

## Current user requirements and order

1. Make the map cover **all 366 ecosystem identities**, with the current 167 treated as a subset that can be filtered later. Simple trophic-chain **PPR and regional PPR/NPP must work independently of extracted articles or Ecopath models**. Obtain NPP for missing regions as necessary; this newly authorizes the wider regional extraction.
2. Finish the already-running 1998–2019 fixed global-atlas NPP reference and its graph integration. Preserve the completed NPP-only graph and selected/global denominator options.
3. Add a file in a root `external` directory containing every article reference used and an explanation of what it supports. `external` did not exist at handoff. Discover existing documented sources; verify references, do not invent bibliographic details. Maintain this log as new sources are used.
4. After every implementation/extraction agent finishes, update all affected project skills with the final knowledge and rebuild/check their distributions.
5. Complete verification, **commit and push**, as explicitly requested. No further approval needed for these authorized steps. Do not push partial results.

Earlier requested tasks are largely complete: remove `expanded_search` badge; runnable/fresh-clone NPP project and 22-year extraction for archived ecosystems; central workbook final mapping sheets; map/graph catch bases (all catch, discards, existing landings default) and optional discard-routing sensitivity. Keep wet-equivalent PPR to carbon conversion `/9` once. NPP is already carbon. Unsupported years remain blank, with an optional explicitly labeled earliest-year proxy only before coverage. The expanded literature review of the conversion factor and new Ecopath article/model extraction remain deferred.

## Safety, workspace, Git ownership

- Workspace is the current `GlobalPPREstimation` repository. Branch `main`, origin `https://github.com/idocarmel1/GlobalPPREstimation.git`. At the last fetch (20:17 UTC) HEAD equaled origin/main. Nothing committed/pushed yet.
- **Never run `PPREstimation/create_PPRS_excel.py`, including `--help`.** Use the documented builders below.
- Root owns the shared index: roughly 2,100 files already staged, including prior authorized scientific outputs. Preserve unrelated edits and staged work. Do not stash, reset, checkout, or bulk delete.
- Another Codex task, **Discards sensiticity**, id `01a08bd4-04dc-7641-bf69-e4d3eb4a6a43`, has an agent working exclusively under `research/discard_sensitivity_expanded_2026_09_10/`. Do not inspect partial outputs, edit, stage, commit, or auto-ingest that namespace. Its root acknowledged our exclusive Git/index ownership and no Git mutations until delivery. This is distinct from the completed original discard study.
- Use one owner for final generated workbook/map/graph writes. Preserve the live NPP worker. Full raster operations are RAM-heavy: one worker only; measured 2.36 GB working set/2.65 GB private memory. Do not start another heavy NPP raster worker concurrently without re-evaluating memory or serializing.
- New root `.gitattributes` intentionally preserves exact scientific bytes (`-text` scopes). Some staged source differences are CRLF-only so provenance survives fresh clones. Do not convert these files to LF. `skills/.gitattributes` has separate existing package rules.
- Ignored caches/venvs/downloads are reproducible and must not be committed. The small input/code ZIPs are intended source artifacts.

## Live processes / agent handoff

The global reference agent wrote **`docs/GLOBAL_NPP_WORKER_HANDOFF.md`** with its precise command and monitoring/checkpoint paths. Read this first. Python PID **16644**, launcher PID **18660**, tool session **76882** were confirmed alive. A fresh task may need OS/filesystem monitoring instead of the old session. At the latest checkpoint **6/22 years complete: 1998–2002 and 2019**; 2003 in progress, no errors. Do not terminate or restart merely because it is slow. **Do not edit its frozen NPP source code, canonical annual input CSV, or canonical provenance while it runs.** Plan the regional expansion independently, then write changed canonical inputs only after the worker finishes. The backend agent has finished its turn without stopping Python; 13 focused backend tests passed.

The map UI agent stopped at a coherent save point; no active process. Its saved changes are listed below. No simple-map exporter agent was started. Prior root's tiny HTTP preview is session 71455, port 8768, repository root; reuse if alive or start an owned hidden replacement. Temporary graph browser tab was closed. Other Python/test/export sessions have finished.

## New simple-map implementation: partly done

2019 inventory: 366 identities, 364 with catch/simple PPR; 167 current map identities, 166 with catch. Existing regional NPP has 168 identities including no-catch HS_018 and LME_064. Of the 199 identities outside the current map, 198 have catch but lack regional NPP; HS_018 has NPP and no catch. The user explicitly confirmed all 366 and authorized filling missing regional NPP. Missing catch must stay unavailable, not zero.

Current architectural restriction: `tools/build_network_atlas.py` exports `network.units` only for 10 pilot model selections, and `network_metrics.js` gates on units/verified models before the simple method. The graph already has independently calculated simple PPR for all 364 catch-bearing identities. Do not extract papers to fix simple PPR availability.

**Saved UI changes**, not yet rebuilt into artifacts:
- `PPRAtlas/atlas/network_view.js`
- `PPRAtlas/atlas/network_controls.html`
- new `tests/test_simple_map_view.cjs`

The UI now forwards `simple_unit: network.simple_units?.[id]` to `PPRMetrics.evaluate`, offers independent `simple trophic chain` in All scope for PPR/PPR-NPP, supports nonpilot details/coloring/counts/central workbook/CSV, and keeps pilot membership in `network.units`. No hard-coded region counts in new logic; pilot/all selection found by option label. CSV preserves precision and `source_files`. 4 focused UI + 10 existing discard-view tests passed; JS syntax passed. Remaining UI work includes any changes revealed by actual browser QA and all-366 renderer rank handling.

**Planned exporter contract (not implemented):** add `network.simple_units`, keyed by all 366 identities, separate from unchanged `network.units`. Each record `{years,name,type,simple,unidentified,catch_accounting,sources}`. `simple` uses the exact graph simple shape: wet-equivalent `ppr`, `covered_catch`, `catch` arrays; `catch_bases`; `unidentified_zero` and `unidentified_simple` variants. Aggregate per-year values, not enormous full-taxon matrices.

Suggested new helper `tools/simple_atlas_data.py`:
- Read identities from `SeaAroundUsExtraction/{global_output,eez_output}/tables/units.json`.
- Reuse `tools/discard_data.py:read_catch_components(root, unit)` for full-precision bases and provenance.
- Read trophic levels through the existing shared reader (`bmw.mio.read_trophic_levels(root,unit)`); avoid helpers that accidentally use a global ROOT in fixtures.
- Reuse `tools/build_time_series.py:simple_basis_values(components, years, trophic_levels, metadata, treatment)` and unidentified metadata helpers. This module does not import the network builder, so a carefully scoped import can avoid a cycle.
- Include raw catch/species paths and hashes and central workbook path when present. Preserve two no-catch identities without fabricated years/zeroes.

**Root evaluator work (not implemented):** in `network_metrics.js`, branch before model gates only for `state.method === 'simple trophic chain'`, `state.mode` in `ppr`/`npp_ratio`, and supplied `state.simple_unit`. All scope only. Select basis/treatment arrays, look up exact year, divide wet-equivalent PPR by 9 once. Return existing result shape with independent source/provenance, catches, missingness and unassessed fixed-TL uncertainty. For ratios reuse annual regional NPP resolution, requiring a positive denominator. Preserve model-based gates for method-comparison mode `ratio` and model-specific scopes. Do not let selected model coefficients affect independent simple results. Add meaningful tests (no model, unverified model, basis/treatment, zero vs missing TL, NPP, All-only).

**All-366 geography:** `PPRAtlas/atlas/catalog.py` currently reads curated 167 inputs/selected polygons. Extend display coverage without falsely marking new regions as curated article archive/pilot selections. Raw local geometries exist under `SeaAroundUsExtraction/spatial/{LMEs,HighSeas,EEZs}.geojson`, and corresponding global/EEZ output spatial directories. Inspect their properties and simplify only display geometry; preserve scientific input geometries. `render.py` has All-rank logic requiring adjustment. Keep subset identity explicit for future filtering.

## Existing global-NPP graph work to preserve

- New `PPRAtlas/atlas/time_series_npp.js`; integration in `time_series_metrics.js`, controls/view, and renderer. NPP-only is exactly one curve independent of models/catch/method/baseline. Selected/global denominator preference and disabled controls are preserved when switching measures. CSV/JSON include denominator, reference and annual support.
- Global reference is the exact dissolved **66 LME + 18 High Seas union**, no EEZ double counting and no claim of entire world-ocean coverage. Median is taken after each model's union total. Fixed geography 294,673,087.34 km², union SHA `716d96ccf2f814231bfe94e583ced4bffd4606841fcff3467b1f7dbcb0e3f124`.
- `tools/global_npp_reference.py`, `tools/verify_global_npp_reference.py`, associated tests and `docs/GLOBAL_ATLAS_NPP_REFERENCE.md` belong to that backend. Follow its handoff before changing anything while worker runs.
- Completed calculations remain **coverage-limited** water estimates. Calculation complete != full source-water/pixel support. In 2019 median is 42,068,251,754.19618 tC/year; water 97.7159% polygon, central 93.8518% water / 91.7081% polygon pixel-days. Early years use one available algorithm, later years five.
- Canonical-provenance lookup chooses source run from annual CSV, not arbitrary directories. Changed inputs must create a new cache; never silently resume with different code/sources.
- `PPRAtlas/data/time_series.json` currently includes only the earlier 1998/2019 global snapshot. Refresh final all-22 reference after worker completion. `tmp/refresh_global_graph.py` can replace only `global_npp`, check unit preservation and render trends. A full time-series rebuild takes ~17 minutes and should be reserved for actual source/export changes, including the new network changes.
- `tools/verify_npp_graph.cjs` defaults to requiring all22; `--allow-partial-reference` was used only for interim QA. Final must pass without that flag.

## Completed evidence / intentional changes to guards

Before the new simple-map request: **121 Python tests + 2 subtests and 70 JavaScript tests passed**. Full time-series export: 366 units, 70 years, 364 catch/simple, 168 NPP, 16 models/10 verified; 50,308 simple source comparisons, 33,530 model annual comparisons, 26 hashes checked. Previous annual/workbook/mapping audits are recorded in `docs/ANNUAL_NPP_HANDOFF.md` and `docs/INTEGRATION_COMPLETION.md`; do not repeat unnecessarily unless changed inputs require them.

Actual graph browser QA passed: HS_018 NPP without catch/model; selected/global Bay ratios; global missing 1950 reason; earliest 1998 proxy/support; normalized methods and return to single NPP curve; no console errors. Browser CSV save event timed out, so do not claim a browser-saved download; actual handler/numerical CSV/JSON tests passed. `data/npp_graph_browser_validation.json` and graph validation still correctly say reference history in progress.

Original canonical annual CSV SHA is `37a92d512619485f5a759fc23f75877294674abd7313418e433246a91762d254`. **The new all-366 request now intentionally expands it**; preserve all prior per-region/year values and document the new hash rather than requiring old full-file identity. Similarly prior map-hash preservation in `tmp/npp_graph_before.json` / the earlier plan is superseded by the user's requested map expansion. Preserve scientific values for already-covered regions and existing model methods.

Prior graph complete-unit JSON canonical SHA was `055d7f3b9ec51f5afb3be7a16d25c1a1986580c2bb7a65198dc348015dfeea7a` using Python sorted JSON/ensure_ascii=False/default spaces. With new NPP coverage, compare unchanged fields and old NPP cells rather than enforcing this whole-record hash blindly.

Completed original private study: `research/discard_sensitivity_2026_09_10/`, 197 frozen inputs, current manifest SHA `0a37309f22ba887bbb6ff90a6cbba7329910c6c0108ba76ecb979e9224d71047`. Historical `verification/input_hashes.json` refers to its earlier manifest; current summary is authoritative. Do not rewrite frozen bytes. A prior browser policy blocked that local research report; do not retry via HTTP/indirect routes. Actual production atlas HTTP QA is allowed.

## Skills refresh, final build and delivery

Authoritative sources: `skills/claude/ecopath-extraction/`, `skills/claude/ewe-species-to-group-mapper/`, `skills/combined-src/`, `skills/codex-src/`. Do not directly edit generated combined/Codex distributions. Build with `python skills/build_combined_skill.py`, then `--check`. Six packages. Installed extraction skill at `C:/Users/idoca/.agents/skills/ecopath-extraction` was previously refreshed with backup/provenance in `data/installed_skill_refresh.json`; update with a new backup only if necessary and preserve `agents/openai.yaml`. No new global installs requested.

Pre-refresh retrieval audit found missing skill guidance for NPP-only/no-catch mode; fixed-union denominator/ensemble; annual physical-support limits; canonical run/cache selection; Git exact-byte provenance. Add the new all-366 independent simple method, expanded regional NPP and article-use log knowledge too. Apply appropriate skill-writing instructions, then independently verify guidance can be retrieved. Do this after all agents finish, per user.

Update current tasks in `docs/INTEGRATION_COMPLETION.md`, `docs/SKILL_KNOWLEDGE_REFRESH.md`, earlier plan, and relevant READMEs; do not leave old 167-only delivery claims as current scope.

Final shared writes are sequential: central workbook build if NPP changed; model workbook refresh; network build; time-series build; relevant annual/mapping/model/discard/simple parity checks, Python/JS tests, and actual map browser QA. See `docs/ANNUAL_NPP_HANDOFF.md` for commands. Add an independent all-366 simple map/graph parity check across bases/treatments, confirming no article/model gate and honest absence for two no-catch regions.

Existing staging allowlist was `.gitignore .gitattributes README.md PPRAtlas data docs skills tests tools NPPExtraction` excluding unfinished `NPPExtraction/output/global_atlas_reference/**`, plus only the original completed `research/discard_sensitivity_2026_09_10` study. Also scoped renormalization of the 17 root -text patterns. After completion restage latest files, new `external`, and finished global outputs; never include expanded research namespace or caches.

`tmp/verify_staged_provenance.py` independently compares staged Git blob bytes to working scientific artifacts using actual Git attributes and checks all197 frozen inputs. Last passed 977 exact artifacts. Run after final staging, then stage its `data/git_provenance_validation.json`. Verify no staged file exceeds GitHub size limits (existing time-series artifacts ~49 MB; new map payload should be compact), inspect final scope, commit, push main, verify remote hash, stop owned preview and close temporary tabs. Report completion and any real remaining source-data coverage limits concisely.
