# PPR time-series view implementation plan

**Goal:** Switch from the atlas to an annual PPR or PPR/NPP graph for a chosen set of ecosystems, with equivalent single-ecosystem links.

**Architecture:** A standalone `PPRAtlas/trends.html` shares the atlas palette and navigation. A compact annual export supplies all known ecosystem identities, original taxon-TL PPR, verified model-method PPR and the six existing NPP choices. Pure JavaScript aggregation is separate from accessible SVG rendering and controls. The map retains its pilot coloring gate.

**Constraints:** Preserve all PPREstimation algorithms and Jensen calculations. No missing value becomes zero. Model failures stay unavailable. Ratios use the same ecosystem cohort for numerator and denominator and convert wet PP to carbon at 9:1. Existing NPP is from 2019 only; label a fixed denominator explicitly unless an annual dataset is supplied. Regions may overlap: report selected-region sums and coverage rather than asserting unique global coverage.

**NPP decision:** The owner explicitly approved repeating fixed 2019 NPP for all years now, with annual values to be supplied later. The aggregator accepts either the current scalar baseline or future year-aligned arrays.

## Deliverables

1. Export `PPRAtlas/data/time_series.json` with years, named sets, units, original simple PPR, verified per-model/scope/method annual totals, included catch and NPP source values. Verify source hashes and comparison with persisted annual workbooks. Unit tests cover missingness, identity, method flags and scope preservation.
2. Implement a pure aggregation module. Tests cover weighted ratios, common and stable cohorts, true zeros, failures, unknown methods/years, empty selection, duplicate IDs and selected model overrides.
3. Build a spacious graph page with PPR/PPR-NPP controls, calculation-method selectors, source scope, searchable preset/custom ecosystem selection and model choices. Show a tooltip with year/value/coverage; provide CSV of plotted values. Add navigation in both views and a graph link for every map ecosystem.
4. Verify full export and representative numerical totals, browser interactions, empty states, deep links and responsive layout. Update usage documentation and project graph, then commit/push within the existing authorization.

## Annual export contract

`schema_version`, `years`, `npp_year`, `npp_methods[{id,label,note}]`, `ppr_methods[{id,label,kind,scopes}]`, `sets[{id,label,units,note}]`, and `units` keyed by unit ID.

Each unit has `name`, `type`, `pilot`, `note`, `npp` keyed by NPP field name, `simple:{ppr,catch,covered_catch}` arrays aligned to `years`, `models`, and `default_model` (model ID or null). Each model has `id,label,verified,source,workbook`, and `scopes[scope].methods[method]={status,ppr,covered_catch}`. Missing samples are null. NPP choices are the five `npp_*_tC_yr` columns and `ens_median_tC_yr`; the latter is labeled regional ensemble median, and aggregation sums regional medians explicitly. Model values must agree with verified atlas inputs and workbook annual totals.

Preset IDs: `global` (84 LME/High Seas input units), `pilot` (10 selected units), `lme`, `high_seas`, `eez` (all 282), `atlas` (167 catalog units), `all`. Include identities with no available values and explain exclusions; never fabricate their curves.

## Verification and final coverage behavior

The source audit covers 50,308 base annual catch/PPR cells, 33,530 usable model
annual totals and 26 upstream/model-workbook hashes. All 8,470 failed-status
annual values remain null. The export has 366 identities, 364 catch series,
84 NPP records, 16 model versions and 10 verified model workbooks.

Some catch series start late or contain gaps. The year-range control allows a
shorter comparison period. Regional sums retain a fixed complete cohort within
that period; single-ecosystem graphs use the available span and break the curve
at missing samples. For the full 1950–2019 global preset, 72 of 84 units have a
complete simple PPR series; NPP coverage can reduce this further by method.

Browser checks covered PPR/NPP and NPP method changes, preset/custom selection,
keyboard checkbox focus, separate South China Sea model choices, source scopes,
failed-method explanations, year inspection, and map links retaining
ecosystem/model/scope/year. An unselected Bouvet ecosystem link opens its
2004–2019 catch span. Exporter, aggregation and existing integration tests pass.
