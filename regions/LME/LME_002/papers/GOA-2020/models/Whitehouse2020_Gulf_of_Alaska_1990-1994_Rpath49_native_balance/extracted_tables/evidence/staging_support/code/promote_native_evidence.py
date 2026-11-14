"""Copy verified native-run evidence into the derived model; no scientific edits."""
from pathlib import Path
import hashlib,json,os,shutil,sys,datetime
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
PARENTS=ROOT/'regions/LME/LME_002/papers/GOA-2020/models'
PARENT=PARENTS/'Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
VARIANT=PARENTS/'Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
DEST=VARIANT/'extracted_tables/evidence/native_reproduction'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p,base=DEST):return os.path.relpath(p,base).replace('\\','/')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert (VARIANT/'model.json').is_file()
protected={p:sha(p) for p in [PARENT/'model.json',VARIANT/'model.json']}
assert protected[PARENT/'model.json']=='10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'
execution=read(RUN/'qa/native_execution.json')
assert execution['returncode']==0 and execution['all_source_bytes_unchanged']
review=read(RUN/'qa/independent_native_variant_review.json')
assert review['result']=='pass_no_material_mismatches' and not review['failures']
assert review['variant_sha256']==protected[VARIANT/'model.json']
DEST.mkdir(parents=True,exist_ok=True)
records=[]
def copy(source,dest,role):
    dest.parent.mkdir(parents=True,exist_ok=True)
    expected=sha(source);shutil.copy2(source,dest);assert sha(dest)==expected
    records.append({'path':rel(dest),'sha256':expected,'bytes':dest.stat().st_size,'role':role,'copied_from':rel(source,ROOT)})
native_files=sorted(p for p in (RUN/'outputs/native_balance').iterdir() if p.is_file())
assert len(native_files)==25,len(native_files)
for p in native_files:copy(p,DEST/p.name,'native_output')
for name in ['native_execution.json','native_execution.log','independent_native_variant_review.json','python_runtime.json']:
    copy(RUN/'qa'/name,DEST/'verification'/name,'execution_or_independent_verification')
for name in ['native_startup_failure.json','native_startup_failure.log','native_runtime_probe.log','native_runtime_probe_fixed.log','native_unpack_runtime.log']:
    copy(RUN/'qa'/name,DEST/'verification/setup'/name,'runtime_setup_history')
for name in ['native_balance.R','native_launch.py','native_handoff.py','native_acquire_runtime.py','native_acquire_dependencies.py','native_runtime_probe.py','check_native_independent.py']:
    copy(RUN/'code'/name,DEST/'code'/name,'execution_or_verification_script')
for name in ['runtime_acquisition.json','md5sum.R-4.5.1.txt','unpacker_release.json']:
    copy(RUN/'inputs/native_runtime_downloads'/name,DEST/'environment'/name,'runtime_acquisition_provenance')
for name,target in [('DESCRIPTION','data.table_DESCRIPTION.txt'),('MD5','data.table_MD5.txt')]:
    copy(RUN/'inputs/native_R_library/data.table'/name,DEST/'environment'/target,'runtime_dependency_identity')
source_references=[]
for name in ['Rpath_ecopath.R','Rpath_param.R','Rpath_unbalanced_data.R','Ecosense_GOA_base.csv','Ecosense_GOA_diet.csv','Ecosense_GOA_pedigree.csv','Ecosense.GOA.rda']:
    p=PARENT/'inputs/native'/name
    assert sha(p)==execution['source_hashes_before'][rel(p,ROOT)]
    source_references.append({'path':rel(p),'sha256':sha(p),'role':'unaltered_official_native_source','source_commit':execution['official_Rpath_commit']})
source_references.append({'path':rel(PARENT/'model.json'),'sha256':protected[PARENT/'model.json'],'role':'preserved_source_extraction'})
source_references.append({'path':rel(VARIANT/'model.json'),'sha256':protected[VARIANT/'model.json'],'role':'verified_derived_canonical_input'})
readme=f'''# Native Rpath reproduction evidence

This package belongs to the [derived canonical model]({rel(VARIANT/'model.json')}) and retains the native reproduction of the [unchanged source extraction]({rel(PARENT/'model.json')}). Original parameter CSVs, RDA and R code remain in the [source model's native-input folder]({rel(PARENT/'inputs/native')}/). They are linked and hashed in `native_manifest.json`, not copied into another active model representation.

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

`native_launch.py` expects the exact isolated R executable at `inputs/native_R_runtime/{{app}}/bin/x64/Rscript.exe` and the exact data.table binary under `inputs/native_R_library`; it sets the process locale above itself. It executes the following R command with absolute paths derived from the repository/work roots, then checks all original source bytes for change:

```powershell
$rscript = Join-Path $nativeRun 'inputs/native_R_runtime/{{app}}/bin/x64/Rscript.exe'
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
'''
(DEST/'README.md').write_text(readme,encoding='utf-8')
records.append({'path':'README.md','sha256':sha(DEST/'README.md'),'bytes':(DEST/'README.md').stat().st_size,'role':'reproduction_and_portability_guide','copied_from':None})
cleanup=['inputs/native_R_runtime','inputs/native_runtime_tools','inputs/native_R_library','inputs/native_runtime_downloads']
manifest={'schema_version':1,'run_id':RUN.name,'region_id':'LME_002','source_model_id':PARENT.name,'derived_model_id':VARIANT.name,'source_commit':execution['official_Rpath_commit'],'promoted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'verified_native_evidence_retained','native_output_file_count':25,'files':records,'source_references':source_references,'independent_verification':{'result':review['result'],'checks':sum(review['checks'].values()),'failures':len(review['failures']),'variant_sha256':review['variant_sha256']},'temporary_cleanup_candidates':[rel(RUN/p,ROOT) for p in cleanup],'cleanup_performed':False,'protected_model_hashes':{rel(p):h for p,h in protected.items()}}
dump(DEST/'native_manifest.json',manifest)
for item in records:
    p=DEST/item['path'];assert p.is_file() and sha(p)==item['sha256']
for item in source_references:
    p=(DEST/item['path']).resolve();assert p.is_file() and sha(p)==item['sha256']
assert all(sha(p)==h for p,h in protected.items())
dump(RUN/'qa/native_promotion_receipt.json',{'destination':rel(DEST,ROOT),'files_verified':len(records),'native_outputs':25,'external_sources_verified':len(source_references),'protected_models_unchanged':True,'manifest_sha256':sha(DEST/'native_manifest.json'),'cleanup_performed':False})
print(json.dumps({'destination':rel(DEST,ROOT),'files_verified':len(records),'native_outputs':25,'external_sources_verified':len(source_references),'protected_models_unchanged':True},indent=2))
