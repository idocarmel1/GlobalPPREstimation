"""Independently verify a committed coordinator registration; no shared writes."""
from pathlib import Path
from io import BytesIO
from xml.etree import ElementTree as E
import hashlib,json,math,sys,zipfile
run=Path(__file__).resolve().parents[1];v=run.parents[1];m=v.parent;root=Path(__file__).resolve().parents[11]
sys.path.insert(0,str(root));sys.stdout.reconfigure(encoding='utf-8')
from tools.project_core.validation.researcher_review import read_report,table_rows,STATUS,S,column_index
from tools.project_core.validation.validation_percentage_format import verify_report
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
packet=json.loads((run/'outputs/proposed_registration.json').read_text(encoding='utf-8'))
report=root/packet['source_report'];canonical=root/packet['canonical_model'];book=root/packet['regional_workbook'];project=root/'Project.xlsx'
assert sha(report)==packet['source_report_sha256'] and sha(canonical)==packet['canonical_model_sha256']
name,date,summary=read_report(root,report,m.name);verify_report(report)
summary['excluded_group_ids']=packet['excluded_group_ids_in_workbook_order']
raw=project.read_bytes();project_hash=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(BytesIO(raw)) as z:
    _,headers,_,rows=table_rows(z,'Models & coverage','Models')
    matched=[(r,d) for r,d in rows if d.get('unit_id')=='LME_003' and d.get('model_id')==m.name]
    assert len(matched)==1
    row,actual=matched[0];headers=list(actual)
    assert actual['researcher_review_status']==STATUS, 'Registration not committed yet'
    assert actual['researcher_name']==name and actual['researcher_review_date']==date
    assert actual['validation_report_path']==packet['source_report'] and actual['validation_report_sha256']==sha(report)
    assert actual['reviewed_model_sha256']==sha(canonical)
    assert json.loads(actual['researcher_review_summary'])==summary
    styles=E.fromstring(z.read('xl/styles.xml'));fonts=styles.find('{'+S+'}fonts');formats=styles.find('{'+S+'}cellXfs')
    for field in ['model_id','researcher_review_status']:
        cell=next(c for c in row if column_index(c.get('r'))==headers.index(field)+1)
        form=formats[int(cell.get('s','0'))];font=fonts[int(form.get('fontId','0'))]
        assert font.find('{'+S+'}color').get('rgb')=='FF187344' and font.find('{'+S+'}b') is not None
with zipfile.ZipFile(book) as z:
    _,_,_,settings_rows=table_rows(z,'Overview','Settings');settings={r['field']:r['value'] for _,r in settings_rows}
    _,_,_,groups=table_rows(z,'Selected model groups','Groups')
assert (settings.get('results_model_id') or settings.get('selected_model_id'))==m.name
current={int(float(r.get('group_seq',r.get('seq')))):r for _,r in groups}
for g in packet['excluded_groups']:
    assert current[g['seq']]['group_name']==g['group_name']
    assert math.isclose(float(current[g['seq']]['ge']),g['GE'],rel_tol=1e-12,abs_tol=1e-15)
assert project_hash==sha(project), 'Project changed during verification'
result={
 'schema_version':1,'unit_id':'LME_003','model_id':m.name,'researcher_review_status':STATUS,
 'researcher_name':name,'researcher_review_date':date,'source_report':packet['source_report'],
 'source_report_sha256':sha(report),'canonical_model_sha256':sha(canonical),
 'project_sha256_at_verification':project_hash,'project_row':int(row.get('r')),
 'excluded_seq':packet['excluded_seq'],'excluded_group_ids':summary['excluded_group_ids'],
 'exclusion_count':len(summary['excluded_group_ids']),
 'verification':{'signed_summary_exactly_matches':True,'source_signature_and_date_match':True,'percentage_format':True,'group_identifiers_names_GE_match':True,'model_and_status_green_bold':True,'source_DOCX_unchanged':True,'canonical_model_unchanged':True},
 'regional_workbook_sha256_at_verification':sha(book),
 'regional_workbook_matches_handoff':sha(book)==packet['regional_workbook_sha256'],
 'mutation_owner':'Shared resources coordinator; this verifier made no shared-file changes',
 'map_and_trends':'Delegated to Shared resources coordinator; not published by this chat',
 'new_scientific_solve_by_this_chat':False
}
out=v/'evidence/researcher_review_20261114/registration_verification.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':STATUS,'exclusion_count':result['exclusion_count'],'project_row':result['project_row'],'project_sha256':project_hash,'receipt':out.relative_to(root).as_posix()},indent=2))
