"""Prepare signed-source evidence only; never register or publish shared files."""
from pathlib import Path
import csv,hashlib,json,math,shutil,sys,zipfile
from xml.etree import ElementTree as E

run=Path(__file__).resolve().parents[1]; v=run.parents[1]; m=v.parent
root=Path(__file__).resolve().parents[11]
sys.path.insert(0,str(root));sys.stdout.reconfigure(encoding='utf-8')
from tools.project_core.validation.researcher_review import read_report,table_rows,STATUS
from tools.project_core.validation.validation_percentage_format import verify_report
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=v/'validation.docx'; book=root/'regions/LME/LME_003/LME_003.xlsx'
diag=m/'results/diagnostics/ee_floor_review_20261114'
expected={report:'64d7df9a743268bf9808c988144c8e5a7d0005b4297b8f017b2710e5b0062c3c',
          book:'1bcb76f49df4812616141075000a022d4a4d2465b28357c03d18cef9c3617957',
          m/'model.json':'18ed0ba93eb9c95ce305fc03fc36cc189b4cd365d9482fd8be30f398c2508925',
          diag/'outputs/effective_groups.csv':'7822b2b4c7cd5e84f432cfc69981e1b0049e58b6f7003ccf669350a8fb3249b1',
          diag/'inventory/evidence_index.json':'ea6b4a364f4b31634a6c9562e7e268f0a1187d2f399c77c96de721ac438d826f'}
assert all(sha(p)==h for p,h in expected.items())
name,date,summary=read_report(root,report,m.name)
assert (name,date,summary.get('status',STATUS))==('Ido Carmel','2026-11-14',STATUS)
verify_report(report)
assert summary['sections'][2]['rows'][0]['text']=='Removed groups from calculation:\nAll groups that have GE<0.01'
with zipfile.ZipFile(book) as z:
    _,_,_,settings_rows=table_rows(z,'Overview','Settings')
    settings={r['field']:r['value'] for _,r in settings_rows}
    _,headers,_,groups=table_rows(z,'Selected model groups','Groups')
    headers=list(groups[0][1]) if groups else (headers or [])
assert settings.get('results_model_id')==settings.get('selected_model_id')==m.name
assert 'group_seq' in headers and 'seq' not in headers
with (diag/'outputs/effective_groups.csv').open(newline='',encoding='utf-8') as f:runtime=list(csv.DictReader(f))
def ge(r):
    value=r.get('ge')
    return None if value in (None,'') else float(value)
selected=[r for r in runtime if ge(r) is not None and math.isfinite(ge(r)) and ge(r)<0.01]
ids=sorted(int(r['group_seq']) for r in selected)
assert ids==list(range(60,80))+list(range(82,93))
assert all(r['trophic_info']=='Regular' and float(r['catch'])==0 for r in selected)
byid={int(r['group_seq']):r for r in runtime}
book_byid={int(float(r['group_seq'])):r for _,r in groups}
for seq in ids:
    assert byid[seq]['group_name']==book_byid[seq]['group_name']
    assert math.isclose(ge(byid[seq]),ge(book_byid[seq]),rel_tol=1e-12,abs_tol=1e-15)
expected_names=[r['group_name'] for _,r in groups if int(float(r['group_seq'])) in ids]
assert len(expected_names)==len(set(expected_names))==31
# Verify the introductory confidence paragraphs at their actual body positions.
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';n={'w':W}
with zipfile.ZipFile(report) as z:document=E.fromstring(z.read('word/document.xml'))
text=lambda e:''.join(t.text or '' for t in e.findall('.//w:t',n))
body=list(document.find('w:body',n));start=next(i for i,x in enumerate(body) if x.tag=='{'+W+'}p' and text(x)=='Taxon mapping and coverage')
boundary=next(i for i in range(start+1,len(body)) if body[i].tag=='{'+W+'}tbl')
actual_intro=[text(x) for x in body[start+1:boundary] if x.tag=='{'+W+'}p' and text(x)]
confidence=summary['sections'][-1]
assert actual_intro[:len(confidence['reference'])]==confidence['reference']
assert text(body[boundary].find('w:tr/w:tc',n))=='Overall confidence'
assert len(actual_intro)==len(confidence['reference'])+1
assert len(body[boundary].findall('w:tr',n))==6

(run/'inputs').mkdir(parents=True,exist_ok=True);(run/'outputs').mkdir(parents=True,exist_ok=True)
signed_copy=run/'inputs/signed_validation.docx'
if signed_copy.exists():assert sha(signed_copy)==sha(report)
else:shutil.copyfile(report,signed_copy)
packet={
    'schema_version':1,'unit_id':'LME_003','model_id':m.name,
    'status':'Prepared for coordinator registration; not a registration receipt',
    'user_authorization':'Read/register edited validated DOCX and update Project.xlsx. Exclude all GE<0.01 groups. Coordinate first; map and trends are delegated to Shared resources coordinator.',
    'coordinator_thread_id':'01a1daa4-cbff-7830-8cb0-b8342b49ec5d',
    'researcher_name':name,'researcher_review_date':date,'researcher_review_status':STATUS,
    'source_report':report.relative_to(root).as_posix(),'source_report_sha256':sha(report),
    'signed_source_copy':'../inputs/signed_validation.docx','signed_source_copy_sha256':sha(signed_copy),
    'canonical_model':(m/'model.json').relative_to(root).as_posix(),'canonical_model_sha256':sha(m/'model.json'),
    'regional_workbook':book.relative_to(root).as_posix(),'regional_workbook_sha256':sha(book),
    'settings_identity':{k:settings.get(k) for k in ['selected_model_id','results_model_id','results_model_sha256','calculation_input_sha256']},
    'group_identifier_header':'group_seq','excluded_seq':ids,'excluded_group_ids_in_workbook_order':expected_names,
    'exclusion_rule':{'field':'ge','operator':'<','threshold':0.01,'missing_values':'not classified as less than threshold','scope':'Initial webpage displayed PPR group selection; preserve full scientific network, matrices, coefficients, denominator and allocation weights'},
    'excluded_groups':[{'seq':seq,'group_name':byid[seq]['group_name'],'GE':ge(byid[seq]),'source_catch':float(byid[seq]['catch']),'trophic_info':byid[seq]['trophic_info']} for seq in ids],
    'boundary_checks':{'retained_80_GE':ge(byid[80]),'retained_81_GE':ge(byid[81]),'phytoplankton_1_GE':ge(byid[1]),'diet_import_94_GE':ge(byid[94]),'detritus_93_GE':ge(byid[93]),'exact_threshold_groups':[int(r['group_seq']) for r in runtime if ge(r)==0.01]},
    'reviewed_diagnostic_configuration':{'use_ee_floor':True,'ee_floor':0.1},
    'reviewed_diagnostic_index':(diag/'inventory/evidence_index.json').relative_to(root).as_posix(),
    'reviewed_diagnostic_index_sha256':sha(diag/'inventory/evidence_index.json'),
    'diagnostic_status':{'GE':'WARN','TE':'WARN'},
    'numerical_adoption_boundary':'This registration does not adopt new regional coefficients. Existing regional GE/TE coefficients predate EE floor; they must not be described as matching the signed ON0.1 diagnostic configuration. Appendix shares are independent simple-chain PPR.',
    'signed_summary':summary,
    'checks':{'signed_source_parser':True,'percentage_format':True,'confidence_intro_document_order':True,'confidence_five_rows':True,'exact31_unique_id_name_crosswalk':True,'regional_and_effective_GE_agree':True,'all_excluded_source_catch_zero':True,'independent_agent_matching_check':'No current Matching row targets any of the31 excluded groups; unchanged mapped-catch PPR totals expected.'},
    'coordinator_work_required':['Resolve seq/group_seq compatibility without editing the regional workbook','Snapshot current Project.xlsx immediately before serialized registration','Register this exact signed source with excluded_seq above','Verify bounded central row change and signed-source equality','Own any map/trends update and verify initial Groups included in PPR selections']
}
out=run/'outputs/proposed_registration.json';out.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert all(sha(p)==h for p,h in expected.items())
print(json.dumps({'packet':out.relative_to(root).as_posix(),'sha256':sha(out),'excluded_count':len(ids),'registered':False},indent=2))
