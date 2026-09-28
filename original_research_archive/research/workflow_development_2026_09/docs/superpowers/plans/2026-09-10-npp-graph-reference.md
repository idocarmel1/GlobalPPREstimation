# NPP graph and fixed atlas denominator implementation plan

> Use subagent-driven development for independent geography and UI work; root owns numerical integration and the final export.

**Goal:** Plot annual NPP independently of PPR availability and offer selected-cohort or fixed global-atlas NPP denominators for PPR/NPP.

**Architecture:** Extend the existing pure graph aggregation with a dedicated NPP lookup/coverage helper. Export a versioned, fixed-geography global reference with explicit ensemble and support metadata. Keep the map's regional denominator unchanged. Source NPP, catch, mapping and production SPPR algorithms remain unchanged.

**Specification:** The September 10 delegated request in this task is the controlling specification. It explicitly authorizes implementation and verification without another approval checkpoint. Work in the current checkout to preserve its completed, uncommitted integration inputs. The user's subsequent instruction authorizes committing and pushing after all work, verification and the final skill refresh are complete.

**Scope extension:** The user's subsequent all-366 request supersedes map-hash preservation and the original regional-input freeze after the running global worker exits. Display all 366 identities, export simple catch/TL PPR independently of articles, and expand regional NPP to missing EEZs while preserving every existing regional value. Curated archive and selected-model membership remain explicit subsets. Add the root `external` article reference/use log. The active continuation record and ownership are in `../../ACTIVE_TASK_HANDOFF_2026-09-10.md` and `../../CONTINUATION_PROGRESS_2026-09-10.md`.

## Numerical contract

- `state.mode`: `ppr`, `ratio`, or `npp`; `state.npp_scope`: `selected` (default) or `global`.
- NPP mode ignores PPR methods, catch, models, source scope, baseline and discards; it produces exactly one selected-NPP curve. Preserve control preferences when switching back.
- Selected NPP is a fixed selected region sum. Missing required annual values leave a gap and identify missing regions. No implicit changing subtotal. Existing selected-ratio cohort rules remain unchanged.
- Global reference is a separate exported `global_npp` record, independent of numerator selection: fixed region IDs/geography, overlap policy, ensemble convention, source hashes, annual values and support metadata. Do not treat EEZ+LME sums as unique ocean geography. Require the complete fixed polygon union and scheduled model pool; missing computation yields a gap. A successfully computed source-water estimate remains explicitly coverage-limited, with annual physical support metadata, and is never described as complete world-ocean coverage.
- Global ratio uses the reference ensemble, not a sum controlled by the chosen PPR method or filtered PPR cohort. Reference values and denominator provenance survive even when PPR is unavailable. Divide central carbon PPR and both compatible routing bounds by the same reference.
- Earliest-year substitution remains explicit and only fills earlier missing years. For the global reference it uses the earliest complete fixed-reference ensemble value, preserving source-year support; no internal/later gap filling.
- Normalized method comparisons retain matched-cohort/denominator semantics and show dimensionless multiples. NPP masses use tonnes carbon/year, never percentages.
- CSV/JSON include mode, denominator scope/value, reference geography/IDs, ensemble convention, annual support, missing regions, source/provenance and substitutions.

## Tasks

- [x] Geography/reference: inspect LME+High Seas membership, available global products and polygon overlap. Implement `tools/global_npp_reference.py`, audit documentation and meaningful synthetic tests for ensemble order, fixed support, missingness and overlap gates. Root wires it into `tools/build_time_series.py` after reviewing its contract.
- [x] Pure aggregation: add `PPRAtlas/atlas/time_series_npp.js`; integrate it in `time_series_metrics.js` and `render.py`. Test NPP-only without models/catch, selected sums, zero/missing values, fixed global denominator, central/band units, earliest proxies and JSON/CSV values. Ten focused numerical tests and independent review pass.
- [x] Graph UI: extend `time_series.html`, `time_series_view.js` and necessary CSS. Add measure/scope selectors and JSON download; disable irrelevant controls, retain URL/preferences, explain reference/support in readouts, tooltips and coverage. Eleven actual-view tests pass, including no-catch NPP notes and complete missing-reference details.
- [x] Rebuild/verify: after all source edits settle, rebuild time-series JSON/HTML once; independently verify actual annual reference and graph arithmetic, run affected Python/JavaScript checks and actual browser scenarios. Preserve all original regional NPP cells and existing PPR/mapping calculations; map/graph output hashes change for the authorized all-366 expansion and new workbook hashes.
- [x] Documentation/skills: record implemented convention, geography limits and missing years; update graph instructions and affected project integration skill references, then rebuild/check distributions. Mark this plan and current task list complete only after evidence is available.
- [x] Commit/push: after the agents finish, verification passes and skills are refreshed, commit the completed project work and push the current branch. Exclude temporary caches and the separately owned, unfinished expanded discard experiment.

## Required regression fixture

Use stored wet-equivalent PPR 900 and 2700 (carbon PPR 100 and 300), regional NPP
1000 and 3000, and fixed global NPP 10000. Both regions give 10% selected / 4%
global; the first alone gives 10% selected / 1% global. A second PPR method or a
missing model must not change the global denominator. Test matched sensitivity
endpoints using the same division, and missing global years as gaps.

## Ownership

The NPP extraction and prior agents are finished. The reference agent owns only
its new backend/tests/geography documentation; the UI agent owns graph controls,
view and UI tests. Root owns aggregation, renderer, exporter and final generated
outputs. No concurrent workbook, map or time-series writers are allowed.
