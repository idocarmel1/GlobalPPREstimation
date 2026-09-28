# Regional NPP expansion — completed September 11, 2026

Final independent source-byte audit passed:1,104 monthly files and32,049,287,447
bytes directly SHA-256 hashed with zero mismatches. Reproduce with
`python -X utf8 tools/verify_regional_npp_sources.py`; the report binds all22
yearly provenance files, plan, annual CSV and publication proof. The frozen
executed helper has a metadata-based checksum cache that cannot detect a byte
replacement preserving size and timestamp. The audit validates current bytes,
not every historical validation boundary. Future extraction requires a versioned
helper with uncached checks and a fresh plan; retain this completed run unchanged.

The user authorized regional NPP for all 366 identities independently of article,
model and catch availability. **All 22 regional years completed at 02:53 Jerusalem;
checked publication completed at 02:54.** All 4,398 new numerical records passed
inspection. All 11,310 original rows were preserved exactly, and the shared reader
now returns 366 × 22 positive annual ensemble values, including the two retained
legacy 2019 cells. Evidence is in `data/regional_npp_numerical_review.json`,
`data/regional_npp_publication_review.json` and the expansion's
`publication_verification.json`. The canonical SHA-256 is
`961278ae7c39a898b4282fbb9b426ff2235eabca496553abe4b3330d34605dbe`.

Extraction started at 01:23 after full global verification. Launcher PID18268,
heavy worker PID16516 and watcher16904/session73151 have exited successfully.
Historical logs are
`tmp/regional_npp_20260910T213442Z_extracting_regional.stdout.log` and `.stderr.log`.
The first completed year,1998, and the complete final history passed independent
checks of finite estimates, exact ensemble arithmetic, full lineage and no
fabricated catch. No competing raster worker was launched.

## Historical finite watcher — replacement verified September 11, 2026, 00:35 Jerusalem

**Historical watcher PID16904**, launched by root in persistent execution
**session73151** with
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File tmp/watch_global_then_regional_npp.ps1`.
It started September10 at21:34:42 UTC. Three successive atomic status timestamps
were observed:21:34:44.5779005,21:35:14.92307 and21:35:45.1483022 UTC. This verifies
two full30-second cycles after the correction. The watcher remained alive and
held its exclusive lock (probe exit12), with11/22 global years completed and no
regional child yet launched. That root-owned session subsequently completed and exited.

Watcher console output was captured in session73151. Each verifier/regional
child received separate timestamped persistent stdout/stderr logs; exact
paths and child PIDs were written into the status JSON when its stage started.
`tmp/regional_npp_watcher_launch.json` describes that launch and the
successful cycle/lock verification. The failed initial launch metadata is retained
as `tmp/regional_npp_watcher_failed_launch_19908.json`.

### Initial launch and correction history

- Initial hidden watcher PID **19908**, started September 10 at21:31:45 UTC,
  **exited on its second state update**. The error and fix are recorded below;
  consult the status/launch metadata for the replacement watcher.
- Script: `tmp/watch_global_then_regional_npp.ps1`.
- Atomic stage/PID status: `tmp/regional_npp_watcher_state.json`.
- Launch metadata: `tmp/regional_npp_watcher_launch.json`.
- Exclusive process-held lock: `tmp/regional_npp_watcher.lock`. Its continued file
  existence alone does not indicate a live lock; the OS handle is authoritative.
- Watcher stdout: `tmp/regional_npp_watcher_20260910T213140Z.stdout.log`.
- Watcher stderr: `tmp/regional_npp_watcher_20260910T213140Z.stderr.log`.

The first verified state was `waiting_for_global_exit`: global PIDs18660/16644
remained alive,11 of22 records completed (1998–2007 and2019), and no regional
worker was running. A duplicate check returned exit12 because the existing watcher
held the exclusive lock; no second watcher or raster job was launched. A separate
lightweight child-process test confirmed that a nonzero child exit7 is preserved,
so a failed global verifier cannot be mistaken for success.

The initial watcher then failed because Windows PowerShell passed the null
`File.Replace` backup argument as an invalid empty path. No regional job started.
The script now supplies an explicit same-directory `.previous` backup. A real
Windows PowerShell probe verified three consecutive atomic state writes, the
previous-state backup and exact child failure-code propagation. Preserve the
initial stderr above as diagnostic evidence. The replacement launch and multiple
successful30-second cycles are recorded above.

The finite watcher checks every30 seconds, without terminating existing workers.
After every detected global/NPP raster process exits, it requires22 parseable
records for1998–2019 with matching year and `calculation_complete=true`. It then
runs `tools/verify_global_npp_reference.py` **without any partial flag**, records
the exact exit code, and refuses to proceed on failure. It rechecks that no raster
worker exists before launching one regional `extract --years1998:2019` process.
The actual command includes a space between `--years` and `1998:2019`.

Each child has timestamped stdout/stderr files under `tmp/`; current child command,
PID and log paths appear in the status JSON. Successful global verification also
retains `verifier_stdout` and `verifier_stderr` when the regional child starts.
The watcher ends as `regional_complete` or an explicit failure state. It never
runs canonical publication. If interrupted or failed, inspect its stage/logs and
existing Python processes before deciding whether to restart; never duplicate a
live regional worker. No active agent polling is required for this finite chain.

## Prepared files and measured inventory

- `tools/expand_regional_npp.py`: separate plan, extraction and publication actions.
- `tests/test_regional_npp_expansion.py`: nineteen tests pass, including a real temporary
  CSV publication, exact old-field preservation, refusal of collisions/incomplete
  publication, no-catch identities, true zero versus missing retrieval, original
  record reuse, truncated/incomplete checkpoint rejection and idempotent publication.
  Independent review reproduced stale-result publication in a temporary fixture;
  the regression now passes, as do six separate provenance-alignment cases.
- `NPPExtraction/output/regional_expansion/plan.json`: completed read-only source
  audit, original configurations, input hashes, target rows and geometry identity.
- `NPPExtraction/output/regional_expansion/annual_before.csv`: exact immutable
  original canonical CSV, SHA-256
  `37a92d512619485f5a759fc23f75877294674abd7313418e433246a91762d254`.
- Separate full scientific geometry subsets: 198 EEZs, HS_018, LME_064. Original
  raw geometry files and canonical source files are unchanged.

All 1,104 required monthly files exist with the expected sizes: 32,049,287,447
bytes (29.85 GiB). No missing monthly sources or target polygons were found.
Each file's SHA-256 is checked before its extraction year, with in-process reuse
only while its path, size, modification time and expected hash remain identical.
Available algorithms are inherited exactly from each original annual source run:
one in 1998–2002, five scheduled in 2003–2019, with regional retrieval absence
remaining explicit. Original per-year water-mask windows are retained, including
2019's 2017–2021 window. No new source discovery or downloads are needed.

The plan contains 200 geographic targets and 13,887 new target rows: 4,398
supported NPP rows, plus 9,489 unsupported historical rows where catch reporting
requires them. HS_018 and LME_064 receive 1998–2018 NPP-only rows; their original
legacy 2019 cells and provenance remain unchanged and continue to be merged by
the existing NPP reader. EEZ_252's 1998 NPP is computed despite no catch that year.

Fourteen other supported NPP cells already exist in original extraction records
but were omitted by the former catch-year grid. These are copied with their
original model values and original provenance: EEZ_037/2003; EEZ_074/1998–2003;
HS_067/2008,2009,2012,2013,2015,2017,2018. Existing canonical cells are not replaced.
Successful publication contains 25,211 canonical rows, including 8,050
supported rows; the two preserved legacy 2019 cells complete 366 × 22 coverage.
Calculation coverage does not imply positive retrieval for every region/model.

## Historical execution and resumption contract

The exited watcher was the authorized launcher for this frozen run. The command
below records its extraction procedure. For fresh reproduction, follow
`NPPExtraction/ANNUAL.md` in an isolated workspace and prepare a fresh plan from
the original archive base. The published canonical CSV intentionally differs from
this completed run's frozen extraction baseline.

```powershell
NPPExtraction/.venv/Scripts/python.exe -u -X utf8 tools/expand_regional_npp.py extract --years 1998:2019
```

The watcher launched this command using `Start-Process -WindowStyle Hidden`, a
resolved Python executable, the repository as working directory, and distinct
stdout/stderr files under `tmp/`. It recorded each child PID and exact log paths.
Timestamped log names on a subsequent controlled launch preserve diagnostics.
Before publication, the command could resume its unchanged frozen inputs; a single
year could be requested with `--years 2019` for
a pilot. The full command reuses completed verified years.

The one-time scientific fractional geometry coverage uses the existing exact
coverage builder at native 4km and comparison 1/12-degree resolutions. All years
reuse it. Existing same-window water masks are copied into separate caches. The
original NPP numerical engine computes the missing regions with unchanged
settings. Union-wide annual totals cannot be reused as regional totals: the
climatology anomaly factor is specific to each region and month. Baseline and
ensemble NPZs checkpoint each completed stage; truncated or incomplete NPZs are
recomputed. Validation checks every downstream array and its dimensions, including
coverage titles/grid/triples, all baseline accounting arrays, and all scheduled
ensemble model arrays. Water-mask shape and Boolean type are checked before reuse.

Outputs are isolated under `NPPExtraction/output/regional_expansion/years/`;
ignored caches under `NPPExtraction/data/work/regional_expansion/`. Exact helper
and NPP Python source snapshots are saved in `execution_sources/<code-key>/`. Each completed
year has `annual_records.json`, baseline monthly/regional tables, ensemble table,
and `provenance.json` with hashes of final outputs, source files, original source
configuration, geometry, executed code and measured elapsed seconds.

The cache key binds the exact helper/core source, original provenance, input
raster hashes, supported target rows and all geometry hashes. Shared coverage caches
also carry the code key, so changing the coverage implementation cannot reuse an
old matrix under the same geometry hash. The runner checks frozen sources before
and after each year. Do not edit `tools/expand_regional_npp.py`, `NPPExtraction/npp`
or original annual provenance during extraction. The global helper may be changed
after its own worker exits; this regional worker does not import it.

This regional run took approximately **90 minutes**, including initial geometry
coverage. The earlier planning estimate was 2.5–3.5 hours; timings depend on source
caches, hardware and memory. The first year's numerical stages took195.7 seconds;
later five-model years took approximately225–326 seconds.
The old baseline worker measured about 2.36 GB working set / 2.65 GB private
memory. Allow additional memory for the new sparse EEZ coverage; a new peak has
not yet been measured. One raster worker only. Approximately 274 GiB disk was
free at planning; the helper refuses to start a year with under 8 GiB free.

## Publication and integration

Only after all 22 years complete:

```powershell
NPPExtraction/.venv/Scripts/python.exe -X utf8 tools/expand_regional_npp.py publish
NPPExtraction/.venv/Scripts/python.exe -m pytest -q tests/test_regional_npp_expansion.py
```

Publication and resume share the same expected per-year input identity. They accept
only its exact output directory, validate complete executed configuration,
original source-configuration lineage, geometry, raw manifest and execution
snapshot bytes, require all four hashed output files, and check every record's
provenance/key. A sole stale directory cannot substitute for a current result.
Publication also checks every expected supported target row and all frozen
source-code/configuration identities. It builds a separate expanded
CSV, verifies all 11,310 original rows field-for-field, and replaces the canonical
CSV atomically. New rows are additions only. Unsupported years remain blank;
no-catch regions never acquire catch rows or manufactured catch values. The proof
is `publication_verification.json`, including before/after CSV hashes, exact
preserved-row hash/count, added rows, statuses and original-record reuse.

Root owns all final central-workbook, model-workbook, map and graph builds.
After the global worker exited, root adapted
`global_npp_reference.source_configuration_path` to resolve canonical expansion
provenance through its explicit `source_configuration` path and SHA-256. The
original same-year source configuration remains unique. All15 focused tests and
independent conflicting/foreign-year fixtures passed, and the full global verifier
passed against the expanded canonical CSV.

Update current coverage documentation and skills only after extraction and all
implementation agents finish, as the user requested. Do not stage or commit
caches, logs or another task's expanded discard-sensitivity workspace.
