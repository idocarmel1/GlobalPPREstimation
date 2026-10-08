from pathlib import Path
import sys,json,shutil,hashlib,zipfile,re,copy
root=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(root))
from tools.project_core.registry.discovery import region_directory,resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import read_report,table_rows,_register_review,FIELDS,approved_review
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews
run=Path(__file__).resolve().parent.parent
unit='LME_028';mid='28_646_Guinea_(1998)'
region=region_directory(root,unit);model=resolve_model(region,mid)
report=model.parent/'model_validation/validation.docx';project=root/'Project.xlsx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(file,var):
    text=file.read_text(encoding='utf-8');start=text.index('const '+var+'=')+len('const '+var+'=')
    data,_=json.JSONDecoder().raw_decode(text,start)
    fp=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',text).group(1)
    return data,fp
def units(data,var):return data['network']['units'] if var=='DB' else data['units']
def focal(data,var):return next(m for m in units(data,var)[unit]['models'] if m['id']==mid)
def rows(book):
    with zipfile.ZipFile(book) as z:return [r for _,r in table_rows(z,'Models & coverage','Models')[3]]
pre=json.loads((run/'qa/preflight.json').read_text(encoding='utf-8'))
assert sha(model)==pre['model_sha256']
assert sha(region/(unit+'.xlsx'))==pre['regional_workbook_sha256']
verify_report(report)
name,date,summary=read_report(root,report,mid)
assert (name,date)==('Ido Carmel','2026-10-08')
expected_groups={2:'Dauphins',4:'Oiseaux',1:'Baleines'}
with zipfile.ZipFile(region/(unit+'.xlsx')) as z:
    settings={r['field']:r['value'] for _,r in table_rows(z,'Overview','Settings')[3]}
    group_rows=[r for _,r in table_rows(z,'Selected model groups','Groups')[3]]
    book={'Overview':{'Settings':(['field','value'],[[k,v] for k,v in settings.items()])},'Selected model groups':{'Groups':(list(group_rows[0]),[[r[k] for k in group_rows[0]] for r in group_rows])}}
assert (settings.get('results_model_id') or settings.get('selected_model_id'))==mid
for seq,label in expected_groups.items():
    assert next(r['group_name'] for r in group_rows if int(float(r['seq']))==seq)==label
prior=run/'inputs/Project_before_registration.xlsx'
assert not prior.exists(),'Handoff already started; inspect saved evidence before retrying'
before_pages={}
# Own one canonical lock across snapshot, registration and refresh. Invoke the
# existing lock-body implementations to avoid acquiring a non-reentrant lock twice.
with central_lock(root):
    assert sha(project)==pre['project_sha256'],'Project changed after preflight'
    shutil.copyfile(project,prior)
    before_rows=rows(prior)
    for file,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
        path=root/'interactive_map'/file
        before_pages[file]=payload(path,var)
        assert before_pages[file][1]==sha(prior)
        shutil.copyfile(path,run/'inputs'/file)
    values=_register_review(project,report,unit,mid,list(expected_groups))
    _refresh_reviews(project,prior,[unit],model_ids={unit:mid})
    after_rows=rows(project)
    for old,new in zip(before_rows,after_rows):
        if (old.get('unit_id'),old.get('model_id'))==(unit,mid):
            assert {k:v for k,v in old.items() if k not in FIELDS}=={k:v for k,v in new.items() if k not in FIELDS}
        else:assert old==new,'Unrelated central model row changed'
    current=next(r for r in after_rows if (r['unit_id'],r['model_id'])==(unit,mid))
    review=approved_review(root,current,book)
    assert review['status']=='Validated by researcher'
    assert review['sections']==summary['sections']
    assert set(review['excluded_group_ids'])==set(expected_groups.values())
    checks={}
    for file,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
        data,fp=payload(root/'interactive_map'/file,var)
        assert fp==sha(project)
        target=focal(data,var)
        assert target['researcher_review']==review
        assert set(target['display_ppr_excluded_group_ids'])==set(expected_groups.values())
        assert not target.get('recorded_review_pending')
        stripped=copy.deepcopy(data);old_target=focal(before_pages[file][0],var);new_target=focal(stripped,var)
        for key in ['researcher_review','display_ppr_excluded_group_ids','recorded_review_pending']:
            new_target.pop(key,None)
            if key in old_target:new_target[key]=copy.deepcopy(old_target[key])
        assert stripped==before_pages[file][0],'Non-review payload changed'
        checks[file]={'source_review_equal':True,'all_other_embedded_data_preserved':True,'project_fingerprint':fp}
    assert sha(model)==pre['model_sha256']
    assert sha(region/(unit+'.xlsx'))==pre['regional_workbook_sha256']
    assert sha(report)==values['validation_report_sha256']
proof={'unit_id':unit,'model_id':mid,'reviewer':name,'date':date,'status':review['status'],'report_path':review['report_path'],'report_sha256':sha(report),'model_sha256':sha(model),'calculation_input_sha256':settings['calculation_input_sha256'],'regional_workbook_sha256':sha(region/(unit+'.xlsx')),'project_before_sha256':sha(prior),'project_after_sha256':sha(project),'display_exclusions':[{'English':'Dolphins','model_group':'Dauphins','seq':2},{'English':'Birds','model_group':'Oiseaux','seq':4},{'English':'Whales','model_group':'Baleines','seq':1}],'exclusion_provenance':'Exact French/English translations from researcher removal notes, resolved against actual selected model Groups.seq.','page_checks':checks,'central_other_rows_preserved':True,'canonical_model_and_regional_science_preserved':True,'report_rendered_pages_inspected':9}
(run/'qa/handoff.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False,indent=2))
