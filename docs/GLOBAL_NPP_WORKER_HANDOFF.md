# Global NPP worker — completed continuation record

**Completed 11 September 2026, 01:23 Jerusalem:** all 22 records for 1998–2019
passed full verification; original PIDs 16644/18660 have exited. The regional
expansion now runs separately under the watcher documented in
`REGIONAL_NPP_EXPANSION_HANDOFF.md`. The instructions below record the original
worker handoff and its reproducible extraction procedure; they are not a request
to start another global worker.

## Original handoff (historical)

The user requested continuation in a new task. **The independent Python worker is
still running; do not restart or duplicate it.** Its monitoring-only tool cell was
stopped, and the actual worker was then confirmed alive.

## Process and current progress

- Workspace: `C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation`
- Worker PID **16644**; Python launcher PID **18660**; parent shell PID **11812**.
- Original tool session: **76882**. This may not be available in the new task;
  process and filesystem monitoring below do not depend on it.
- Command, from repository root:

```powershell
NPPExtraction/.venv/Scripts/python.exe -u -X utf8 tools/global_npp_reference.py --extract --years 1998:2018
```

- Completed: **1998, 1999, 2000, 2001, 2002, 2019** (6 of 22 years).
- In progress at handoff: **2003**; remaining through 2018 runs sequentially.
- 2019 was computed first in a preceding worker and is already published.
- There have been no failed years. Keep **one raster worker**: measured peak working
  set was 2.36 GB / peak private memory 2.65 GB, leaving insufficient comfortable
  headroom for two simultaneous baseline peaks on this 16 GB machine.

Inspect the process without depending on the previous agent or tool session:

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*tools/global_npp_reference.py*' -and $_.Name -like '*python*' } | Select-Object ProcessId,ParentProcessId,CommandLine
Get-Process -Id 16644 | Select-Object Id,CPU,WorkingSet64,StartTime
Get-ChildItem -LiteralPath NPPExtraction/output/global_atlas_reference/years -Filter record.json -Recurse | Select-Object FullName,LastWriteTime
```

The stdout log is attached to session 76882; **there is no persistent stdout log
file**. Do not redirect or relaunch the live worker merely to add logging. Published
records and checkpoint files provide reliable cross-task progress:

- `NPPExtraction/output/global_atlas_reference/years/YYYY/record.json`: authoritative
  completed year, written only after successful numerical calculation and provenance.
- Same directory: baseline and ensemble CSV ledgers, then `provenance.json`.
- `NPPExtraction/output/global_atlas_reference/reference.json`: compact reference,
  refreshed atomically after each completed year.
- `NPPExtraction/data/work/global_atlas_reference/YYYY/<input-key>/`: ignored checkpoints.
  `inputs.json` is written first, followed by water/coverage caches, the complete
  `baseline_YYYY_4km.npz`, and `ensemble_YYYY_12th.npz`. Monthly calculation is not
  individually checkpointed; avoid interrupting a partial year.

## Do not invalidate the live worker

Until it finishes, do **not edit** `tools/global_npp_reference.py` or any
`NPPExtraction/npp/*.py` source: the worker verifies their hashes before/after each
year and will stop if they change. Do not mutate its raw source files, canonical
annual CSV, source-year provenance, fixed geometry, or reference output directories.
Its input keys and source-byte checks prevent stale checkpoint reuse.

The new request to supply NPP for **all 366 ecosystems**, including the currently
missing **198** regional identities, is separate from this fixed-union calculation.
Plan that work now, but coordinate its raster run and canonical output publication
after this worker finishes. If implementation can proceed independently, use new
tools outside `NPPExtraction/npp/` and separate outputs; do not run `npp.annual plan`
over the live canonical inputs. Full source geometry files and monthly rasters are
already cached, so fresh downloads should generally be unnecessary.

If the worker exits before all years are complete, inspect the latest record and
checkpoint state. Only after confirming it has exited, rerun the command above to
resume with the current frozen source. Matching completed inputs are reused; an
interrupted NPZ is detected. Changed inputs are recomputed in a new keyed cache.

## Final steps after completion

1. Confirm 22 completed records, 1998–2019, and that the worker has exited.
2. Run `python -X utf8 tools/verify_global_npp_reference.py`. It requires all 22 years
   and writes `NPPExtraction/output/global_atlas_reference/verification.json`.
   The verifier currently passes for the two endpoint years using `--allow-partial`;
   the final run must omit that flag.
3. Run `python -X utf8 -m pytest -q tests/test_global_npp_reference.py` (13 focused
   tests passed before handoff).
4. Refresh the graph's global reference using the root task's established export
   workflow. The root completed graph implementation, full tests and browser QA on
   the endpoint data; preserve all existing PPR arrays and map behavior while
   refreshing annual reference inputs.
5. Complete the newly requested 366-ecosystem regional coverage work, final skill
   knowledge refresh, remaining verification, and the user-authorized commit/push.
   Coordinate their exact order with the new task's broader handoff.

The reference's fixed boundary is one dissolved union of 66 LMEs and 18 high-seas
identities, including no-catch LME_064 and HS_018; EEZs are not added. Its default is
the median of union-wide model estimates, not a sum of regional medians. Values are
coverage-limited tonnes carbon/year; calculation completion does not mean full
spatial satellite coverage or total world-ocean NPP.

Useful checked values: 1998 = **41,688,186,668.48225 tC/year** (one model);
2019 = **42,068,251,754.19618 tC/year** (five models). See
`docs/GLOBAL_ATLAS_NPP_REFERENCE.md` for scientific details and coverage definitions.

Exact executed helper snapshots are retained under
`NPPExtraction/output/global_atlas_reference/execution_sources/`. The 2019 helper
hash is `7374d1e565593fba831dca072e8a95cde854664b38688803cb0a85b31485ecf7`;
the current worker uses
`96cd3ae6cf66ad9821c7384f84e6bba64b817ea562280a0fd67b42f06330e464`.
The difference is the bounded canonical-provenance selection/resumption improvement;
the underlying NPP numerical code is identical and checked by the final verifier.
