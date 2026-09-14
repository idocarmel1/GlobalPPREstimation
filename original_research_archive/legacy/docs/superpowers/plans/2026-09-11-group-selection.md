# Model group selection implementation plan

**Goal:** Select and sort model groups by name, TE, TL, SPPR_all, SPPR_inner and catch-related PPR, consistently across the map and annual graphs in standalone HTML files.

**Architecture:** Embed group inputs alongside the existing data. Share pure group calculations and one dialog component between views. Save named group selections by ecosystem/model, carry them through navigation URLs, and persist browser settings. No external data requests or server.

**Approved design:** User's group-filter proposal and explicit implementation request in this conversation. Preserve model food webs, existing quality gates, catch allocations and NPP denominators. All groups selected must return the existing numbers exactly.

## Interfaces

`model.group_data`: `{groups:[{id,name,te,tl}], methods:[methodId], scopes:{all:groupByMethodMatrix,inner:matrix,PP:matrix}, mappings:taxonArrayOfGroupIndexWeightPairs}`. IDs are authoritative group names, not row numbers. TE is the upstream group's GE × EE; expose its definition in the UI. Source SPPR is not recomputed.

Annual units also receive `group_inputs`: years, taxa, full_precision_catch, landings, discards, catch, and baseline taxon SPPR scopes/model metadata needed for selected-group calculations. Avoid copying catch arrays per model. Map units already contain these inputs.

Shared selection state: `group_selections` maps `unitId + '::' + modelId` to an array of selected group names; omitted key means all, empty array means none. Model overrides remain keyed by ecosystem. One selection is reused for every method. Table filters select rows explicitly and never silently change when the inspected method/year changes.

## Work

- [x] Export group metadata, exact final mapping weights and source-scope SPPR; test identity, missingness and precision. Add verified MC counts to map models as well.
- [x] Implement pure group selection/calculation helpers and integrate map and annual metrics. Test all-selected identity, partial multi-group mappings without renormalization, no groups, all catch bases, method ratios, simple-chain allocation, NPP invariance and MC gate precedence. Invalidate precomputed discard envelopes when a subset is selected.
- [x] Add a shared accessible dialog with model chooser, reference method, name and numeric filters, sortable columns, row checkboxes, Select all, Select matching and Clear all. Preserve the existing visual style.
- [x] Add local persistence, URL transfer and CSV/JSON selection provenance. Verify direct local-file reopening and cross-view navigation in a real browser.
- [x] Rebuild both standalone pages, check source hashes and numerical regression suites, inspect the actual UI, and report actual file sizes.

## Verification commands

`node --test tests/*.cjs`

`C:/Users/idoca/miniconda3/python.exe -m pytest tests/test_group_export.py tests/test_time_series_export.py tests/test_ppr_scopes.py -q`

Build the network export first, then the time-series export. Preserve all unrelated research work and earlier map changes; do not commit or alter source workbooks.
