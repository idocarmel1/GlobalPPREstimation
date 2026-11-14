"""Verify candidate registration and retained packages; inventory temporary cleanup."""
from pathlib import Path
import csv, hashlib, json, os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tools/skills/paper-to-ppr/scripts'))
from tools.project_core.registry.discovery import discover_models
from tools.project_core.workbooks.workbooks import read_book
from check_evidence import check
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p,base=ROOT):return os.path.relpath(p,base).replace('\\','/')
REGION=ROOT/'regions/LME/LME_002'
expected={'Aydin2007_Gulf_of_Alaska_1990-1994':'791a9011ea48ea2e3eb1a8907845452726ad1f7ebdd5ac7416aa5ba7bac4be36','Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49':'10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'}
models=discover_models(REGION)
assert set(models)==set(expected),list(models)
review=read(RUN/'qa/independent_numeric_review.json')
assert not review['mismatches']
assert review['result']=='pass_no_material_blockers'
protected=read(RUN/'qa/protected_workbook_hash.json')
assert sha(ROOT/protected['path'])==protected['sha256'],'Regional workbook changed'
registration=read(RUN/'qa/candidate_registration_report.json')
applied=registration['status']=='applied'
assert (applied and registration['cell_preservation_verified']) or registration['status']=='pending_project_write_lock'
book=read_book(ROOT/'Project.xlsx',sheets=['Models & coverage'])
header,rows=book['Models & coverage']['Models']
registered={r[header.index('model_id')]:dict(zip(header,r)) for r in rows if r[header.index('unit_id')]=='LME_002'}
if applied:
    assert set(registered)==set(expected)
    for mid,row in registered.items():
        assert row['selected'] in (False,None,0) and row['production_eligible'] in (False,None,0)
        assert row['researcher_review_status'] is None
        assert row['model_path']==rel(models[mid])
# Staged writer/converter representations and render/word caches are disposable;
# original source PDF and downloaded recovery sources are retained untouched.
targets=[RUN/'outputs']
for p in (RUN/'qa').iterdir():
    if p.is_file() and (p.suffix.lower()=='.png' or p.name.startswith(('page_','preference_page_','preference_upright_','root_page_','Project.before_candidate_registration.'))):targets.append(p)
if (RUN/'code/__pycache__').exists():targets.append(RUN/'code/__pycache__')
records=[]
for target in targets:
    assert target.resolve().is_relative_to(RUN.resolve()) and target.resolve()!=RUN.resolve()
    files=sorted(target.rglob('*')) if target.is_dir() else [target]
    for p in files:
        if p.is_file():records.append({'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size,'disposition':'remove temporary generated representation after canonical and evidence reconciliation','source_original':False})
dump(RUN/'qa/cleanup_plan.json',{'run':rel(RUN),'targets':[rel(p) for p in targets],'files':records,'source_originals_retained':True})
with (RUN/'qa/source_paths.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,['path','sha256','bytes','disposition','source_original']);w.writeheader();w.writerows(records)
summary={'canonical_models':{},'independent_source_checks':sum(review['checks'].values()),'registration_status':registration['status'],'unrelated_registry_cells_preserved':True,'regional_workbook_unchanged':True,'map_actions_performed':False,'selection_changes':False,'SPPR_or_annual_PPR_performed':False,'temporary_cleanup_planned_files':len(records)}
for mid,path in models.items():
    assert sha(path)==expected[mid]
    ev=path.parent/'extracted_tables/evidence'
    if mid.startswith('Aydin'):
        shutil.copy2(RUN/'qa/independent_numeric_review.json',ev/'independent_numeric_review.json')
        # Make report-local evidence links relative to the report itself.
        report=ev/'REPORT.md'
        report.write_text(report.read_text(encoding='utf-8').replace('(extracted_tables/evidence/','('),encoding='utf-8')
    for name in ['candidate_registration_report.json','protected_workbook_hash.json','source_paths.csv']:
        shutil.copy2(RUN/'qa'/name,ev/name)
    index_path=ev/'evidence_index.json';index=read(index_path)
    for artifact in index['artifacts']:
        if artifact.get('availability')=='present':artifact['sha256']=sha((ev/artifact['path']).resolve())
    tracked={a.get('path') for a in index['artifacts']}
    for p in [ev/'candidate_registration_report.json',ev/'protected_workbook_hash.json',ev/'source_paths.csv',ev/'independent_numeric_review.json']:
        if p.is_file() and rel(p,ev) not in tracked:index['artifacts'].append({'role':'handoff_verification','availability':'present','path':rel(p,ev),'sha256':sha(p)})
    dump(index_path,index)
    result=check(index_path);dump(ev/'completeness.json',result)
    assert not result['errors'],result['errors']
    assert result['missing_roles']==(['complete_final_diet'] if mid.startswith('Aydin') else [])
    summary['canonical_models'][mid]={'path':rel(path),'sha256':sha(path),'groups':len(read(path)['group']),'inventory_integrity_errors':result['errors'],'missing_required_roles':result['missing_roles']}
dump(RUN/'qa/final_verification.json',summary)
print(json.dumps(summary,indent=2))
