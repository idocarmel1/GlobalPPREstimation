"""Apply the authorized exact-pair negative review through the guarded APIs."""
import copy, hashlib, json, re, sys, zipfile
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import read_report, register_review, table_rows, FIELDS, sha
from tools.project_core.maps.build_html import refresh_reviews
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.maps.original_atlas_data import embedded

PAIR = ('LME_028', '28_646_Guinea_(1998)')
REASON = 'Reason – Amplified aggregated trophic pathways, uncertain catch allocations, and regional extrapolation undermine confidence in this model’s regional PPR application.'
MODEL = ROOT/'regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)'
PROJECT = ROOT/'Project.xlsx'
REPORT = MODEL/'model_validation/validation.docx'
BASE = json.loads((RUN/'qa/baseline.json').read_text(encoding='utf-8'))
PREVIOUS = Path(BASE['temporary_rollback'])/'Project.xlsx'

def metadata(path):
    with zipfile.ZipFile(path) as archive:
        return {(r['unit_id'], r['model_id']): r for _, r in table_rows(archive,'Models & coverage','Models')[3]}

def assert_source():
    name, date, summary = read_report(ROOT, REPORT, PAIR[1])
    assert (name,date)==('Ido Carmel','2026-10-18'), (name,date)
    assert summary['status']=='Disqualified by researcher'
    assert summary['verdict']=='MODEL DISQUALIFIED'
    assert summary['reason']==REASON, summary['reason']
    assert summary['sections']==[] and summary['note']==''
    return name,date,summary

def verify():
    name,date,source=assert_source()
    before=metadata(PREVIOUS); after=metadata(PROJECT)
    assert before.keys()==after.keys()
    changes={}
    for key,row in after.items():
        diff={k:[before[key].get(k),row.get(k)] for k in set(row)|set(before[key]) if before[key].get(k)!=row.get(k)}
        if diff:
            assert key==PAIR and set(diff)<=set(FIELDS), (key,list(diff))
            changes[str(key)]=diff
    row=after[PAIR];summary=json.loads(row['researcher_review_summary'])
    assert summary==dict(source,excluded_group_ids=[])
    assert row['researcher_name']==name and row['researcher_review_date']==date
    assert row['validation_report_sha256']==sha(REPORT)
    assert row['reviewed_model_sha256']==sha(MODEL/'model.json')
    assert row['reviewed_calculation_input_sha256']==before[PAIR]['reviewed_calculation_input_sha256']
    positive=sorted(k for k,r in after.items() if r.get('researcher_review_status')=='Validated by researcher')
    expected=sorted(tuple(p) for p in BASE['positive_pairs_before'] if tuple(p)!=PAIR)
    assert positive==expected and len(positive)==7
    pages={}
    for filename,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
        path=ROOT/'interactive_map'/filename
        payload,_=embedded(path,variable)
        old,_=embedded(Path(BASE['temporary_rollback'])/filename,variable)
        units=payload['network']['units'] if variable=='DB' else payload['units']
        oldunits=old['network']['units'] if variable=='DB' else old['units']
        target=next(m for m in units[PAIR[0]]['models'] if m['id']==PAIR[1])
        oldtarget=next(m for m in oldunits[PAIR[0]]['models'] if m['id']==PAIR[1])
        review=target['researcher_review']
        for key in ['status','verdict','reason','sections','note','excluded_group_ids']:
            assert review[key]==summary[key], (filename,key)
        assert review['researcher_name']==name and review['review_date']==date
        assert review['report_path']==row['validation_report_path']
        assert target.get('display_ppr_excluded_group_ids')==[]
        assert not target.get('recorded_review_pending')
        for field in ['researcher_review','display_ppr_excluded_group_ids','recorded_review_pending']:
            oldtarget.pop(field,None)
            if field in target:oldtarget[field]=copy.deepcopy(target[field])
        assert payload==old, filename+' changed beyond exact review/exclusion payload'
        text=path.read_text(encoding='utf-8')
        assert f'<meta name="ppr-project-sha256" content="{sha(PROJECT)}">' in text
        pages[filename]={'sha256':sha(path),'review':review,'default_model':units[PAIR[0]]['default_model'],
                         'all_other_embedded_data_equal':True}
    with zipfile.ZipFile(PREVIOUS) as a,zipfile.ZipFile(PROJECT) as b:
        assert a.namelist()==b.namelist()
        zipchanges=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    result={'target':PAIR,'signed_name':name,'signed_date':date,'reason':REASON,
            'registered_status':row['researcher_review_status'],'report_sha256':sha(REPORT),
            'project_sha256':sha(PROJECT),'changed_project_fields':list(changes[str(PAIR)]),
            'changed_project_parts':zipchanges,'positive_pairs':positive,'pages':pages}
    (RUN/'qa/registration_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['registered_status'],'positive_pairs':len(positive),
                      'exact_source_project_page_equality':True,'changed_project_parts':zipchanges},indent=2),flush=True)

if __name__=='__main__':
    if '--verify-only' not in sys.argv:
        assert_source()
        assert sha(PROJECT)==sha(PREVIOUS)==BASE['protected_sha256']['Project.xlsx'], 'Project changed since baseline'
        # The encompassing existing transaction also rolls registration back if
        # the guarded refresh rejects. It preserves concurrent-author changes.
        with publication_transaction(ROOT) as transaction:
            register_review(PROJECT,REPORT,*PAIR,[])
            transaction.checkpoint([PROJECT])
            refresh_reviews(PROJECT,PREVIOUS,[PAIR[0]],model_ids={PAIR[0]:PAIR[1]})
            verify()
    else:
        verify()
