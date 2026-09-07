# Pilot PPR integration completion — 2026-09-07

This is the current handoff. It supersedes the open-work status in the original
`HANDOFF.md` and the first `CODEX_TAKEOVER.md` review, while preserving those files
as history. Remaining integration tasks **1–5 are complete**, including the requested
scope, ratio and recycling views. Task 6's expansion beyond the selected pilot has
not been started. The knowledge graph is refreshed separately from coverage expansion.

## Research and mapping work

| Ecosystem/model | Taxa | Catch mapped, 1950–2019 | GE / TE / egestion diagnostics |
|---|---:|---:|---|
| Northern Humboldt, 1995–1998 | 218 | 98.1854% | FAIL / FAIL / FAIL |
| Guinea, 1998 | 375 | 98.5802% | OK / WARN / OK |
| Arabian Sea off Karnataka, 2000 | 430 | 98.7301% | OK / WARN / OK |
| Gulf of Thailand, 1980 payload | 247 | 99.9846% | WARN / WARN / WARN |
| Northern South China Sea, 2000s | 374 | 99.7884% | WARN / WARN / OK |
| Northern South China Sea, 1970s | 374 | 99.7884% | WARN / WARN / OK |
| Sea of Okhotsk, 1980 NE | 151 | 97.3335% | WARN / FAIL / WARN |

These seven mappings were completed or rechecked against their source tables,
with source notes, group dictionaries, taxonomy, explicit members where available,
confidence, unresolved taxa, fixed composite weights and validation records. The
Arabian review replaced inherited tail assignments using the published member
table. South China Sea weights remain period-specific. Only the usable northern
Humboldt model was mapped; other versions were not silently substituted.

All seven named upstream SPPR exports were regenerated after applying taxonomy.
Every deterministic SPPR value reproduces the prior numerical result within
`1e-9`; source JSON changes are limited to `taxon_descr`. Monte Carlo estimates
vary between runs and their comparisons are recorded in the model sidecars.
Guinea needed a 600-second retry, which completed in 449.6 seconds and recovered
the previously timed-out Monte Carlo method. No finite cells were lost.

The independent [Guinea combined-skill comparison](../data/LME_028/validation/combined-skill-comparison/README.md)
uses a separately run combined-skill mapping and preserves both CSVs. Group sets
agree on 96.4% of catch tonnage. Combined coverage is 99.6652%, versus 98.5802% for
the separate production arm, with more low-confidence assignments. The production
mapping is retained. This is neither a fully blinded experiment nor proof of
scientific accuracy or statistical non-inferiority.

## New paper through the complete pipeline

[Saygu et al. (2025), East Coast of Scotland 1991–1995](NEW_PAPER_VALIDATION.md)
was newly extracted through source tables, eight EwE import files, taxonomy,
model JSON, SPPR, mapping and PPR in an isolated validation directory. It contains
25 source groups, 232 explicit diet cells, 384 catch taxa and 99.597% catch coverage.
An independent audit checked 23,040 taxon/method/scope values and 4,200 annual
totals with zero numerical differences.

The raw source's Ling EE=1.003 and Turbot/BA uncertainty remain documented; printed
values were not repaired in the source extraction. GE and egestion converge; TE
fails with rho living 1.11278. The existing loader's normalization and defaults
are recorded separately. This completes a computational integration test, not a
production North Sea estimate. The model is absent from pilot selection, production
top10 exports and atlas coloring.

## Workbooks and map

All **364 base ecosystem workbooks** now include `sppr_all`, `sppr_inner`,
`sppr_PP` and `Recycling`, in addition to their original five sheets. Group rows
identify each model explicitly. The **10 mapped model workbooks in eight ecosystems**
retain `SPPR` for all sources and add taxon-level `sppr_inner`, `sppr_PP`, annual
`PPR inner`/`PPR PP`, and diagnostics. Multiple models stay separate.

- **All:** imported food, internal detritus and primary-producer sources.
- **Inner:** internal sources, excluding imports.
- **PP:** primary-producer sources, excluding detritus and imports.

Unavailable source partitions remain blank. Scalar methods without a decomposition
are not copied into the PP partition. The simple trophic chain is labeled as an
unpartitioned reference in workbooks and is available only under All in the map.

The [atlas](../PPRAtlas/index.html) reads verified model workbooks through
`tools/build_network_atlas.py`. Its controls select catch year, model, scope,
method, a ratio numerator/denominator, or recycling **b / rho living** under
**GE / TE**. Ratios use exactly the common catch taxa with finite results for
both methods; zero/missing denominators are unavailable. Annual coverage is shown.
Recycling values are model diagnostics, not annual estimates, and show the original
status and calculation configuration. Finite diagnostic values remain inspectable
even when the configuration fails.

`data/atlas_selection.json` explicitly limits colored results to the **ten selected
pilot ecosystems**. Others remain gray, including the new-paper validation region.
Article areas are restricted to selected article IDs. Candidate articles remain
browsable as archived alternatives. Unmapped pilot ecosystems can show existing
diagnostics, but cannot show fabricated network PPR. At the default GE/All/2019
view, seven ecosystems have valid PPR values; ten selected ecosystems is an
eligibility count, not a claim of ten available results.

## Integration defects corrected

- A failed diagnostic is attached only to the exact SPPR configuration it tested:
  `new_GE`, `new_TE_EEfix`, or `new_WithEgestion`. Any negative source-group SPPR
  flags that method, including negative groups with no mapped catch. Failed methods
  remain visible in workbooks with status but are excluded from map estimates.
- Excel `INDEX` can turn a referenced blank into zero. Taxon formulas now guard
  with `ISNUMBER`; all-missing totals remain blank with a `COUNT` guard. Genuine
  numeric zero remains zero.
- PPR/NPP compares wet-weight-equivalent PPR with carbon NPP using the existing
  **9:1 wet/carbon conversion**. The denominator is explicitly the fixed 2019 NPP
  field. This fixes a ninefold unit error without changing raw PPR or either
  Jensen calculation.
- Partial ecosystem builds preserve unrelated rows in the ecosystem index.
  Taxonomy sidecars are excluded from mapping-file discovery.
- The safe named-model SPPR wrapper forces UTF-8 for workers on Windows, preserving
  functional-group names such as `≤` through JSON and XLSX. It reports failed or
  incomplete exports through its exit code.
- The upstream summary rank formula now breaks ties in source-table order,
  including zero-catch ties. Its scientific PPR formulas are unchanged.

All **368 upstream workbooks** were regenerated: 85 global and 283 EEZ workbooks.
Their cached cells match current source CSV tables and independent group arithmetic,
covering **105,124 formulas with zero formula errors**. A Windows runtime wrapper
at `tools/run_workbook_exports.ps1` makes the existing artifact-tool export usable
with the bundled dependencies and paths containing spaces and Hebrew text.

## Source limitations that affect interpretation

- **Thailand:** Ecobase 412 is the **1980 overexploited model**. All 11 comparable
  published biomass values match 1980; ten contradict 1963. The inherited filename
  remains for stable joins, but map labels and notes identify the conflict. The
  original article supplies membership and biomass comparisons, not a complete
  independently verified PB/QB/diet package.
- **Okhotsk:** “NE” means the new detailed Ecopath model of the **whole Sea**, not
  northeastern Okhotsk. The source lacks a full species inventory. TE is unsafe.
- **Guinea:** the paper models **111,932 km² off the country Guinea**, not the whole
  Guinea Current LME. Thirteen printed B/EE comparisons and the bird TL differ
  from the inherited payload; this source-version uncertainty is retained.
- **Geography:** applying local/coastal models to whole-LME catches remains an
  extrapolation, including Karnataka, northern Humboldt and the South China Sea.
- **Validation:** member checking uses literal taxa/synonyms and can accept a
  composite with only one overlapping candidate. Manual source review remains
  necessary. High catch coverage is not evidence of complete ecological accuracy.

## Skills and verification

`skills/claude/` and `skills/codex/` contain the same three skills: extraction,
species-to-group mapping, and the combined paper-to-PPR workflow. Corresponding
scripts, templates, examples and domain references are identical; entry points
fit each agent. All six archives pass the deterministic distribution check.

Final integration regression checks: **52 root tests and 193 Sea Around Us/atlas
Python tests passed**, plus map-metric and spreadsheet JavaScript checks. All ten
production model workbooks pass the independent workbook verifier. Browser checks
covered scopes, both recycling options, method ratios, year/model switches,
Thailand's identity note, unavailable failed estimates and unselected gray regions.
Representative scope sheets and missing-value formulas were rendered and inspected.

The PPREstimation algorithm files and both Jensen calculations were preserved.
Its separate pre-existing test issues (missing fixture arguments and a stale method
count expectation) were outside this integration; the passing checks above do not
claim that unrelated suite was repaired.

## Next work

Task 6 may now extend selected article/model coverage, with explicit geographic
review and production approval of any new model. Keep the source limitations and
mapping uncertainty visible. `graphify-out/GRAPH_REPORT.md` records the refreshed
architecture and research context; its corpus excludes generated table contents
and raw archive duplicates. Do not execute `PPREstimation/create_PPRS_excel.py`
directly, even with `--help`: it runs a broad export. Use `tools/run_sppr.py` with
explicit model IDs for future regeneration.
