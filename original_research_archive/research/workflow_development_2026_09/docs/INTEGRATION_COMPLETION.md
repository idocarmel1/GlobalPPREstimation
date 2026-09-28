# PPR integration completion — updated 2026-09-11

This is the current handoff. It supersedes the open-work status in the original
`HANDOFF.md` and the first `CODEX_TAKEOVER.md` review, while preserving those files
as history. The requested scope, ratio, recycling, all-366 simple-chain map and
regional NPP expansion are implemented. Only expansion of extracted Ecopath models
and the additional conversion-factor literature review remain deferred. All final
builds and verification are complete; see the September11 evidence below.

The September 7 pilot results below remain historical evidence. The September 11
completion and deferred task list are recorded under **Current task status**.
Annual NPP supersedes the earlier fixed-2019 convention; the atlas now defaults
to landings and offers all catch and discards separately.

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

`data/atlas_selection.json` limits model-based results to the **ten selected
pilot ecosystems**. The default simple trophic chain independently uses catch and
catch-taxon trophic levels across all366 identities, with364 catch-bearing regions.
Article availability is not a simple-chain gate. The two no-catch identities retain
NPP without fabricated PPR. Curated archive membership remains an explicit167 subset.
Article areas are restricted to selected article IDs. Candidate articles remain
browsable as archived alternatives. Unmapped pilot ecosystems can show existing
diagnostics, but cannot show fabricated network PPR. At the model GE/All/2019
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
  **9:1 wet/carbon conversion**. The denominator now uses the corresponding annual NPP
  field, with unavailable years blank. This fixes a ninefold unit error without changing raw PPR or either
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

## Current task status — 2026-09-11

- [x] **Final follow-up skill refresh.** All three workflows in both Claude and
  Codex distributions were updated after implementation and extraction finished.
  All six packages reproduce their sources. Six independent forward scenarios
  passed, including no-article simple PPR, no-catch NPP, denominator geography,
  source lineage, fresh reproduction and mapping-only scope. The existing installed
  extraction skill was backed up and refreshed while preserving its interface.
- [x] **All-366 map and regional NPP.** Simple-chain PPR and regional ratios use
  catch/TL independently of article or model status. All366 identities are shown;
  364 have2019 catch-based PPR and ratios. NPP covers all366 over1998–2019.
- [x] **NPP through time and denominator scope.** NPP-only plotting is independent
  of PPR, catch and model availability. Ratios offer selected-ecosystem or fixed
  atlas-union denominators. The union is84 LME/high-seas identities with overlap
  removed, all22 years complete, and explicit annual physical support. Its ensemble
  is the median of union model totals, not a sum of regional medians. This is not
  total world-ocean NPP. Earlier gaps and optional proxies retain source years.
- [x] **Article reference/use log.** Root `external/ARTICLE_REFERENCE_USE_LOG.md`
  and JSON distinguish computed-model, selected-unverified, candidate, validation
  and methodological references. Unresolved citations remain explicit.
- [x] **Final generated-output verification.** All shared builds, independent
  arithmetic checks, actual browser scenarios and read-only full graph reproduction
  passed. The separately owned unfinished expanded discard experiment is excluded.
- [x] **Git delivery.** Integration commit 58f08539 was pushed successfully to main
  after all checks and skill updates. The repository history records the delivery.

- [x] **Task 1 — remove the search-status badge.** `expanded_search` is absent
  from ecosystem details; source-search metadata remains available in the archive.
- [x] **Task 2 — reproducible annual NPP and full integration.** The supplied ZIP
  is integrated as an installable, resumable project. All 22 supported years,
  1998–2019, cover all366 identities, including two without catch. The canonical
  grid contains25,211 rows:5,938 complete,2,112 partial and17,161 unsupported blank
  rows; zero failed or pending rows. All11,310 original rows are preserved exactly.
  The8,052 supported ensembles include two retained legacy2019 cells. Partial support
  means fewer available algorithms, not a completed five-model ensemble.
  All 364 central and ten mapped model workbooks, indexes, map and graph now
  use the completed canonical data. Earlier unavailable years remain blank;
  the optional constant earliest-year proxy applies only before a method starts,
  preserves its source year and never fills internal/later gaps.
  See [completed NPP handoff](ANNUAL_NPP_HANDOFF.md) and
  [reproduction instructions](../NPPExtraction/ANNUAL.md).
- [x] **Task 4 — final mappings in the central workbooks.** Both central LME and
  model downloads include `Final mappings`, with exact numerical weights,
  taxon/model/group identities, evidence and unresolved cases. All 4,042 rows
  match across eight central LME and ten model workbooks.
- [x] **Discard study and map integration.** All catch and discards-only views
  show their own PPR without a routing envelope. Landings remain the default,
  with a show/hide choice for supported discard-routing sensitivity. Each basis
  uses its own taxon catch vector. NPP, source scopes and unidentified-taxon
  choices remain consistent across map, graph and downloads. The study supports
  31 model/method/scope combinations in three models; other combinations are
  explicitly unassessed. Ranges describe scenarios, not confidence intervals.
  The [standalone report](../research/discard_sensitivity_2026_09_10/report.html)
  and [methods/findings](../research/discard_sensitivity_2026_09_10/METHODS_AND_FINDINGS.md)
  retain source limitations and invalid scenarios. Its data/runtime checks pass;
  actual report browser verification remains blocked by the browser's local-file
  navigation policy. Production map and graph browser checks passed separately.
- [x] **Final skill knowledge refresh, after the other agents finished.** Updated
  all three project skills and regenerated both Codex/Claude distributions and
  all six packages. Updated the existing installed extraction skill with a
  backup and preserved interface metadata. Independent retrieval checks cover
  the seven key procedures. See [refresh record](SKILL_KNOWLEDGE_REFRESH.md).
- [x] **Unidentified-catch sensitivity.** The selected method, zero contribution
  and reference-TL options preserve the selected catch basis, missing values,
  scope restrictions and audit labels. See [method and inventory](UNIDENTIFIED_CATCH.md).
- [x] **NPP denominator audit.** Canonical annual values are already regional
  tonnes carbon; legacy 2019 regional `scaled_*` fields are selected where needed.
  Bay of Bengal's median is 1,061,393,189.80 tC/year. PPR is divided by nine once.
- [ ] **Task 3 — carbon conversion literature review, deferred.** Use Perplexity
  for an expanded search of peer-reviewed and authoritative original publications
  on carbon, dry and wet weight, organism groups and trophic levels. Record
  uncertainty and evidence strength. Retain carbon:wet weight 1:9 if no significant
  differences between groups at different TLs are detected, per the owner's rule.
- [ ] **Coverage/model expansion, deferred.** Extend selected articles and models
  only with explicit geographic review and production approval. Existing local
  model-to-LME extrapolations and source-version limitations remain visible.

## Final verification — September 11

- Root Python suite:157 tests and two subtests passed. JavaScript suite:82 tests
  passed. These counts cover the explicit integration suites, not unrelated projects.
- All364 central and10 mapped model workbooks rebuilt; all10 model books verified.
  Annual audit:307,440 exported values,155,214 workbook NPP values and26,554 ratios.
- Simple map:230,580 annual PPR and230,580 ratio comparisons;1,094 source hashes.
  All364 catch-bearing regions have2019 simple PPR and regional ratios.
- All366 graph identities have NPP;50,308 base annual values,33,530 model annual
  values and26 model hashes checked. Full read-only rebuild matches exactly.
- Exact final mappings:4,042 rows. Unidentified controls:1,800 comparisons.
  Three catch bases and routing:16,200 comparisons;31 supported response combinations.
- Full global reference:22 years and176 graph checks, no missing supported years.
  Independent uncached source audit:1,104 files/32,049,287,447 bytes, no mismatches.
- All11,310 old regional rows remain field-for-field equal. Pilot/map and graph
  scientific data are preserved apart from the authorized NPP updates, removal of
  obsolete no-NPP notes and actual refreshed model-workbook hashes.
- Actual final map and graph browser checks passed, with no console warnings or
  errors. CSV/JSON controls and handlers are tested; a browser-saved download is
  not claimed. The old preview server was replaced for graph QA after an empty response.
- Six skill packages match their sources; six core forward scenarios and the
  additional checksum-cache scenario passed. Installed extraction resources match.
- Git audit:1,260 scoped scientific artifacts and197 frozen study inputs match
  exact staged bytes. Four previously normalized files were restaged from audited
  bytes. No raster caches, virtual environment or unfinished expanded study is staged.

Evidence is indexed by `data/integration_release_validation.json`. The frozen
regional helper's historical metadata-cache limitation is documented in the source
audit and reproduction guides; current monthly bytes independently match all hashes.

## Historical verification for the September 10 changes

- 107 root Python tests and two subtests; 49 JavaScript tests; 56 private study
  tests passed. The read-only time-series rebuild matches the delivered export.
- Annual NPP audit: 224,280 exported values, 155,124 workbook values and 26,554
  matching-year summary ratios checked across all 364 central and ten model books.
- Exact mapping audit: 4,042 rows; unidentified controls: 1,800 map/graph cases;
  three catch bases and routing sensitivity: 16,200 map/graph cases.
- All ten mapped model workbooks pass their independent verifier. The three
  unmapped alternative source models skipped by the builder are not failed
mapped targets and receive no invented mapping.
- Six skill packages reproduce their sources. Independent skill-only scenarios
  recover extraction/taxonomy, membership scope, mortality units, NPP reproduction,
  final weights, catch bases and routing validity rules.
- Browser checks cover the actual production map and graph, full-history NPP,
  early gaps/proxies, three catch bases, show/hide, workbook links and URL handoff.
  Download regressions verify that missing NPP retains carbon totals/bounds and
  an audit download even when every displayed ratio is unavailable.

Source workbook PPR remains a total-catch calculation in its original units.
The atlas headline changes legitimately with the selected catch basis. Mapping
decisions, production SPPR/Jensen algorithms, the 1:9 conversion and pilot
eligibility remain unchanged. Historical test counts above describe the prior
September 7 release and are not claims of newly rerunning unrelated suites.

The current publication and old-cell preservation proof is in
`NPPExtraction/output/regional_expansion/publication_verification.json`.
`NPPExtraction/output/extraction_coverage.json` and `workbook_refresh.json` describe
the preceding archived-subset release. Current cross-output audits are in
`data/annual_npp_validation.json`, `data/final_mappings_validation.json`,
`data/discard_views_validation.json` and `data/unidentified_validation.json`.

Do not execute `PPREstimation/create_PPRS_excel.py` directly, even with `--help`:
it runs a broad export. Use `tools/run_sppr.py` with explicit model IDs for future
authorized regeneration. Coordinate shared writers and build from stable inputs.
