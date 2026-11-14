"""Record focused UI checks and unchanged live source evidence."""
import sys,json,hashlib,subprocess
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
root=Path.cwd();out=Path(__file__).resolve().parent
files={
'tools/project_core/maps/ee_floor.js':'ed27e376cc051ee39c8fed3862064c01f9e55fabd8366f02ba264fe991de2197',
'tools/project_core/maps/ee_floor_layout.py':'76dd0c67f1bf2c1fe1fcd60debd216e630c6ac5b228dc3ff395667bc06d18e07',
'tools/workflow_checks/maps/check_ee_floor_views.js':'96c0690557eb0bcf558d71bff124de2738f31dbcd71ec5cd92bfc71a70a2faec',
'tools/workflow_checks/maps/test_ee_floor_views.py':'923fb0ebe963aa3c6da0ce1d41f33539940bdafffaef5f3c9be200538bf708a2'}
actual={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}
assert actual==files,'Live inputs changed; regenerate patch before apply'
patch=out/'ee_floor_presentation_with_tests.patch'
checked=subprocess.run(['git','apply','--check',str(patch)],capture_output=True,text=True,encoding='utf-8')
assert checked.returncode==0,checked.stderr
green=json.loads((out/'ee_floor_source_green.json').read_text('utf-8'))
assert green['success'] and green['testsRun']==9 and green['skipped']==0
js=(root/'tools/project_core/maps/ee_floor.js').read_text('utf-8')
candidate=(out/'ee_floor_ui_candidate.js').read_text('utf-8')
assert js[js.index('    const diagnostics='):]==candidate[candidate.index('    const diagnostics='):]
layout=(root/'tools/project_core/maps/ee_floor_layout.py').read_text('utf-8')
layout_candidate=(out/'ee_floor_layout_candidate.py').read_text('utf-8')
assert layout.split('def source_provenance_layout')[0]==layout_candidate.split('def source_provenance_layout')[0]
record={'scope':'Staged presentation prose only; no payload, approval, numeric or production writes',
'production_sources_unchanged':True,'production_sha256':actual,
'git_apply_check':{'returncode':checked.returncode,'stderr':checked.stderr},
'red_evidence':['ee_floor_ui_red.json','ee_floor_source_red.json'],
'green_evidence':'ee_floor_source_green.json','tests_run':9,'failures':0,'errors':0,'skipped':0,
'checked_behavior':['ON/OFF distinction','known enabled zero affected groups','active/pending/unreviewed scope wording','original signed prose and disqualification preserved','current diagnostic restrictions preserved','source/effective group values preserved','exports and candidate/baseline settings unchanged','unknown historical settings not inferred','model and review payloads not mutated'],
'unchanged_code_regions':['JavaScript current diagnostics/restrictions/link output and all tooltips/exports','Python ee_floor_layout injection and export wiring'],
'patch':patch.name,'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'applied':False}
(out/'ee_floor_presentation_verification.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))

