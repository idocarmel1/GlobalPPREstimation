# Continuation ledger

Plan: `docs/ACTIVE_TASK_HANDOFF_2026-09-10.md`. User explicitly authorized this saved checkout, subagents, final commit and push. Existing staged and unstaged scientific work is preserved; root exclusively owns Git and final generated artifacts.

## Interface review and decisions

| Tasks | Shared interface | Decision |
| --- | --- | --- |
| Simple exporter / evaluator / UI | `network.simple_units` | Compact annual arrays; separate from selected model units; All-source PPR and PPR/NPP only. |
| Geography / graph export | All 366 versus curated 167 identities | Preserve archive membership explicitly; displaying geography does not imply an extracted article. |
| Global worker / regional expansion | Canonical NPP inputs and raster memory | Frozen until existing worker exits; one raster worker; preserve old regional cells when publishing expansion. |
| Regional expansion / final builders | Workbook, network, time-series writes | Root performs sequential builds after publication. |
| Skills / implementation agents | Final scientific guidance | Refresh skills after agents finish, then rebuild distributions. |
| Integration / separately owned research | Git index | Exclude `research/discard_sensitivity_expanded_2026_09_10/`; do not ingest unfinished research. |

## Active tasks

**Latest state — September11, ready for Git delivery:** all raster workers,
watchers, shared builders and checks have completed. Full graph rebuild82684 and
read-only check84341 passed with exact export equality. Root157tests+2subtests,
JS82, all independent output checks and final map/graph browser QA passed. Final
summary: `docs/INTEGRATION_COMPLETION.md`; evidence: `data/integration_release_validation.json`.

All6 skills rebuilt and checked after final findings;7 forward scenarios passed.
Installed extraction29resources and original interface match. Uncached raw audit
1104files/32,049,287,447bytes passed. Exact staging audit1260scientific artifacts
and197frozen inputs passed;4 normalized index files restaged from audited bytes.
All11,310original NPP rows and original PPR/mapping science are preserved.

The authorized allowlist is staged. Final commit and push main remain. Do not run
any extraction or builder again. All successful QA tabs closed; one failed preview
tab may remain. Root preview server8769/session87153 may be stopped after delivery;
the older server8768 is separately owned. Exclude unfinished expanded research.

The notes below are historical progress, not active workers or outstanding work.

- Simple export: `/root/simple_export` owns new helper, network builder and focused tests.
- Geography: `/root/map_geography` owns catalog, renderer and UI adjustments.
- Regional NPP: `/root/regional_npp` prepares separate expansion without modifying frozen worker inputs.
- Root evaluator: five new tests reproduced article gating, then passed; 26 focused simple/discard/unidentified tests passed together.
- Independent review: `/root/integration_review` found map/simple clean. Regional review found stale-plan publication and incomplete NPZ validation; both were fixed and independently re-reviewed with 19 tests and all 22 real source configurations passing.
- Source parity: exporter agent checked 679,158 annual cells against existing graph, exact equality; simple payload is 15,153,304 bytes. Root snapshot `tmp/simple_expansion_before.json` records staged pilot and graph non-NPP hashes before final rebuild.
- Geography complete: all366 with explicit curated167, safe catalog refresh integrated in network builder. Interim network build completed: 366 simple identities and the original 10 model units preserved exactly. No time-series rebuild yet.
- Article log complete: `external/ARTICLE_REFERENCE_USE_LOG.md` and JSON, generated from192 catalog assignments/155 source IDs and27 additional references. Rebuild/check its generator after final documentation changes.
- Global provenance compatibility: after worker exit, the two regressions reproduced and were fixed in `source_configuration_path`. Expansion references resolve through a checksummed original same-year parent; conflicting primary runs and invalid parents are rejected. All15 focused tests pass; independent review requested.
- Global reference: original worker PIDs16644/18660 exited normally after all22 records,1998–2019. Full unflagged verification passed in the watcher and again after the compatibility fix. No raster execution was duplicated.
- Sequential launcher: root persistent session73151 runs `tmp/watch_global_then_regional_npp.ps1`, watcher PID16904. It waits for global exit, requires all22 records and unflagged full global verification, then runs exactly one regional extractor. State: `tmp/regional_npp_watcher_state.json`; child logs are timestamped. Publication remains a separate root action. Earlier PID19908 failed on Windows PowerShell's null File.Replace backup binding; fixed with an explicit same-directory backup and repeated state-write checks before relaunch.
- Interim verification: 155 Python tests and two subtests passed, with only the two intentionally deferred global-lineage tests deselected; all 82 JavaScript tests passed. Simple-map verifier checked 230,580 annual PPR and 230,580 annual ratio results plus 1,094 source hashes. Atlas verifier passed all366/curated167/archive assertions.
- Interim browser QA: fresh default simple PPR has 364/366 values; Albania works without an article across landings/discards; HS_018 has honest missing PPR; pilot filter retains ten members and original model failures; Bay of Bengal regional ratio works. No console errors. Evidence: `data/simple_map_browser_validation.json`. Repeat relevant NPP scenarios after final expansion.
- Remaining: finish global and regional extraction; publish reviewed regional records; deferred global lineage fix; final scientific builds/parity and browser QA; skills refresh; reference-log regeneration; final review; stage-byte audit; commit/push.
- Release-byte preservation: `.gitattributes` now additionally protects `tools/expand_regional_npp.py` and the nine reference-log evidence paths not already covered. Final staging must include these explicit paths (including PPREstimation/README.md and SeaAroundUsExtraction input/documentation files outside the broad builder allowlist), preserve working bytes, then run the staged-byte audit.

## Regional extraction live — 11 September, 01:23 Jerusalem

Watcher16904/session73151 passed full global verification and launched regional Python18268/16516 at22:23:36 UTC. Stage is `extracting_regional`. Logs: `tmp/regional_npp_20260910T213442Z_extracting_regional.stdout.log` and `.stderr.log`. First1998 coverage caches completed for198 EEZs plus two no-catch identities; monthly baseline is progressing. Do not edit regional helper, NPP core, original source provenance or canonical annual CSV while it runs. Root alone publishes after all22 regional years are complete and reviewed.

The full22-year global graph refresh completed in session60748; all unit data was preserved exactly (canonical SHA055d7f3b9ec51f5afb3be7a16d25c1a1986580c2bb7a65198dc348015dfeea7a). The unflagged graph verifier passed176 checks with no missing reference years. Independent lineage review is clean:15 focused tests, additional fixtures for conflicting/foreign-year parents, and all22 real canonical paths passed. Full time-series rebuild remains due after regional publication.

Mid-run numerical inspection checked11 completed regional years/2,200 rows with no missing ensemble estimates, valid arithmetic and full lineage. Some later-year regions have fewer than five usable model estimates; retain their partial support. Final independent inspection: `python -X utf8 tmp/summarize_regional_npp.py`; on all22 years this writes `data/regional_npp_numerical_review.json` and requires4,398 newly computed supported rows. Final documentation must distinguish the original archived-scope audit `NPPExtraction/output/extraction_coverage.json` (historical11,310-row hash) from the new `regional_expansion/publication_verification.json`, current annual validation and numerical review. Do not present old archived-scope counts as current all366 coverage; NPPExtraction/README.md and ANNUAL.md also need final updates.

Regional scope ruling: include 1998–2018 NPP-only rows for HS_018 and LME_064 as well as the 198 missing catch-bearing EEZs; retain the two no-catch regions' legacy 2019 values/provenance. Catch remains absent. Reuse decoded sources/water masks with region-specific integration; union totals cannot supply individual EEZ estimates. Prior regional timings imply several hours for the additional 22-year extraction.

## Deferred scope

Do not run `PPREstimation/create_PPRS_excel.py`. New Ecopath extraction and the expanded wet-weight/carbon conversion literature review remain deferred.

## Final verification notes

Final atlas verification passes366 identities/curated167 and317 archive copies.
Final mappings passes4,042 assignments across8 central and10 model books.
An accidentally unscoped pytest command30655 entered the separately owned expanded
study during test discovery and failed collection. No results were used, no study
source was edited or staged; subsequent checks use explicit authorized directories.

Final root suite157+2subtests passed; all10modelbooks,4042mappings and atlas checks pass.
Uncached source audit passed1104files/32,049,287,447bytes. Finalmapbrowserreport passed.
Read-only full time-series check84341 is running beside writer82684 against stable inputs;
it compares only at completion. All6skillpackages rebuilt after new cache guidance;
independent seventh forward scenario passed. No index changes yet.
