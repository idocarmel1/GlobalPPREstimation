# Native Rpath reproduction evidence

This package belongs to the [derived canonical model](../../../model.json) and retains the native reproduction of the [unchanged source extraction](../../../../Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model.json). Original parameter CSVs, RDA and R code remain in the [source model's native-input folder](../../../../Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/inputs/native/). They are linked and hashed in `native_manifest.json`, not copied into another active model representation.

The numerical reproduction is summarized in [NATIVE_BALANCE_REPORT.md](NATIVE_BALANCE_REPORT.md) and [native_summary.json](native_summary.json). All 25 native outputs are retained at this directory's top level. [native_balanced.rds](native_balanced.rds) is the exact native R object; its identical-object reload was checked. CSVs use 17 significant digits and retain source names, order, units and matrix orientation described in the summary. These native outputs are evidence, not another canonical model JSON.

## Executed versions and settings

- Official Rpath source commit: `fe63f6d370d942ff1786f4d649e432fbfb85f81b`; the pinned `read.rpath.params` and `rpath` functions were sourced unchanged.
- R 4.5.1 (2025-06-13, UCRT Windows x64), data.table 1.18.6.1, MASS 7.3-65; one data.table thread. Full [R session information](session_info.txt) and [runtime acquisition receipt](environment/runtime_acquisition.json) are retained.
- Child-process locale: `LC_ALL=English_United States.utf8`, `LANG=en_US.UTF-8`. Inherited Linux `C.UTF-8` was unavailable in Windows R and prevented Hebrew-path lookup. The failed startup and successful probe are retained under [verification/setup](verification/setup/). No global environment settings or R equations were changed.
- Python 3.11.9 with NumPy 2.3.4 was used for the independent check; its full environment is recorded in [python_runtime.json](verification/python_runtime.json). Python 3.12.14 ran the thin acquisition/launch/handoff wrappers; those wrappers perform no native balance calculations.
- The data.table binary reported it was built under R 4.5.3. The run used R 4.5.1 and native balance emitted no warnings. Independent R and Python calculations reconcile as reported; no dependency-version equivalence beyond this run is claimed.

## Reproduction commands

Run from the repository root. Create a fresh regional work run with `inputs`, `outputs`, `code` and `qa` subdirectories; copy the retained scripts from [code](code/) into its `code` directory. The following uses the original run identity so the paths match the execution receipt; use a new run identity for a new experiment. Existing evidence should not be overwritten.

```powershell
$nativeRun = Join-Path (Get-Location).Path 'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
$wrapperPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$qaPython = Join-Path $env:USERPROFILE 'AppData/Local/Programs/Python/Python311/python.exe'
& $wrapperPython "$nativeRun/code/native_launch.py"
& $wrapperPython "$nativeRun/code/native_handoff.py"
& $qaPython "$nativeRun/code/check_native_independent.py"
```

`native_launch.py` expects the exact isolated R executable at `inputs/native_R_runtime/{app}/bin/x64/Rscript.exe` and the exact data.table binary under `inputs/native_R_library`; it sets the process locale above itself. It executes the following R command with absolute paths derived from the repository/work roots, then checks all original source bytes for change:

```powershell
$rscript = Join-Path $nativeRun 'inputs/native_R_runtime/{app}/bin/x64/Rscript.exe'
$sourceNative = Join-Path (Get-Location).Path 'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/inputs/native'
# In the actual run these variables were supplied only to the child environment.
$env:LC_ALL = 'English_United States.utf8'
$env:LANG = 'en_US.UTF-8'
& $rscript --vanilla "$nativeRun/code/native_balance.R" $sourceNative "$nativeRun/outputs/native_balance" "$nativeRun/inputs/native_R_library"
```

The independent checker defaults to the retained derived canonical model and also checks its eight import tables. It accepts `--native-output <directory>` and `--variant <model-directory>` for explicit paths. [Its receipt](verification/independent_native_variant_review.json) records the exact hashes and the earlier native-only review as well as the final variant comparison.

The runtime was obtained by extracting (not installing) the [official R 4.5.1 installer](https://cran.r-project.org/bin/windows/base/old/4.5.1/R-4.5.1-win.exe), whose official MD5 was verified, using the hash-verified portable unpacker identified in the acquisition receipt. The optional acquisition helpers are retained in `code/`. They document acquisition mechanics; before a replay, require the exact package versions and hashes in `environment/runtime_acquisition.json`. The CRAN package-index helper can discover newer package versions and must not be mistaken for a frozen dependency lock. The package DESCRIPTION and internal MD5 manifest are also retained. Verify the source hashes in `native_manifest.json` before rerunning; source files at another version do not reproduce this pinned execution.

## Retention and limits

All evidence links are relative to this directory. Historical run-relative paths inside execution receipts identify where execution occurred; `native_manifest.json` maps copied artifacts to their current retained location through `copied_from` and `path`.

The living equations are full rank, the native budgets reconcile, and EE lies within [0,1]. That establishes the reported native balance, not PPR diagnostic validity, catch mapping, modern temporal applicability, geographic coverage or researcher approval. Native source NA-to-zero conventions and solved values are explicit in the ledgers. No source parameters were fitted or normalized. The pinned Rpath code includes post-2020 changes; this is not a claim to reproduce the unavailable exact historical software environment of the article.

Temporary runtime/download/tool/library trees and duplicate work outputs may be removed after the coordinator verifies retained hashes and completes the overall task. No original paper/model native inputs or pre-existing system Python installation may be removed. This promotion performed no cleanup and changed no model JSON, model notes, registry, map or top-level evidence index.
