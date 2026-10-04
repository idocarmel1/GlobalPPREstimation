from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))
code=(BASE/'diagnostics/run_direct_candidate.py').read_text(encoding='utf-8')
code=code.replace('HERE / "vendor"','HERE.parent / "diagnostics" / "vendor"').replace('det_collapse_mode="never"','det_collapse_mode="auto"')
code=code.replace('HUM2018_20261003_detailed_source_candidate','HUM2018_20261003_auto_preflight').replace('not authorized; candidate evidence only','Conditional selection authorized after successful preflight; no researcher verdict authorized')
encoded=code.replace('\n','\r\n').encode('utf-8')
assert hashlib.sha256(encoded).hexdigest()==manifest['script_sha256'], 'Executed driver reconstruction does not match the recorded Windows file bytes'
(OUT/'executed_code/run_direct_auto.py').write_text(code,encoding='utf-8')
# The replay entry point retains its exact executed content and existing solver defaults.
(OUT/'run_direct_auto.py').write_text(code,encoding='utf-8')
shutil.copy2(BASE/'README.md',OUT/'baseline/candidate_README_before.md')
new='''# Selected Northern Humboldt model package

The audited detailed Chiaverano et al. (2018) Northern Humboldt baseline for 1995–1998 is selected for **provisional research review**. All three DIRECT methods retain overall **FAIL** and production eligibility is false. No researcher verdict is registered.

- [Current regional workbook](../../LME_013.xlsx) owns the selection and configuration.
- [Validation document](../../Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx) and [unchanged-confidence mapping appendix](../../LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx) remain beside that workbook.
- [Canonical source](source/resolved_native/model.json) preserves native values and missingness.
- [Actual audited computational input](source/computational/model.json) is the active input; there is no unrelated root-level historical JSON standing in for it.
- [Preserved never diagnostics](diagnostics/run_manifest.json) retain their original hashes, full returns and negative SPPR.
- [Distinct auto run](auto_run_20261003/run_manifest.json), [comparison](auto_run_20261003/comparison.md), [full returns](auto_run_20261003/full_direct_report.md), and [provisional arithmetic](auto_run_20261003/candidate_calculation_manifest.json) describe the newly selected configuration.
- [Existing mapping decisions](mapping/mapping_review.json), allocation evidence and geography are reused without numerical edits.
- `sppr_source.xlsx` contains only this exact auto configuration's retained groups, coefficients and diagnostic grades for the supported map workflow.
- `auto_run_20261003/baseline` snapshots the prior active workbooks, reports and generated pages. The Chilean Patagonia model/report remain intact.

The candidate package was relocated from `candidate_studies/HUM2018_20261003` into `models/Chiaverano2018_detailed_Northern_Humboldt_1995_1998` without changing scientific bytes. Its original canonical source folder was locked by another process and is retained; the selected package's canonical copy has the same source hash. The former candidate location contains a portable pointer and preserved source/runtime material, not an alternative selection.

The independent confidence denominator remains 277,099,551.4346593 t C for 2019 landings. Source production conflicts, unsupported native fleet-return ancestry, the four-pool TE EE=0 limitation, approximate 6–8% region coverage and fixed-period extrapolation remain unresolved.
'''
(BASE/'README.md').write_text(new,encoding='utf-8')
(OUT/'relocation.json').write_text(json.dumps({'old_package':'regions/LME_013/candidate_studies/HUM2018_20261003','selected_package':BASE.relative_to(ROOT).as_posix(),'canonical_sha256':sha(BASE/'source/resolved_native/model.json'),'computational_sha256':sha(BASE/'source/computational/model.json'),'original_locked_canonical_copy_retained':True,'scientific_content_changed':False,'reason':'User-authorized LME_013 directory organization after successful preflight'},indent=2),encoding='utf-8')
print('Executed driver hash verified; selected package index and relocation evidence saved.',flush=True)
