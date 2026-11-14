"""Register the signed LME003 decision independently of numerical adoption."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
from unittest.mock import patch
import json, shutil, sys

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.workbooks.workbooks import sha
from tools.project_core.validation.researcher_review import read_report, _register_review, table_rows, approved_review, review_group_sequences
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews

UNIT='LME_003'
MID='CAL-2016_California_Current_2000-2014'
PROJECT=ROOT/'Project.xlsx'
BASE_SHA='9a3951c5e4342c3b8cc0ab2c0feccff9962aac3f91daf600e7a18a38e4c2e06b'
MODEL=resolve_model(region_directory(ROOT,UNIT),MID).parent
REGION=region_directory(ROOT,UNIT)/(UNIT+'.xlsx')
REPORT=MODEL/'model_validation/validation.docx'
PACKET=MODEL/'model_validation/work/2026-11-14_192900_signoff/outputs/proposed_registration.json'
PACKET_SHA='e8a47c8c9f4ab1090ba79ceab68fceebd442374e5b7617e243a46a947bee71c8'
BASELINE=RUN/'inputs/Project_before_batch_2_registration.xlsx'

def read(path):return json.loads(path.read_text('utf-8'))
def fingerprint(path):return sha(path) if path.is_file() else None
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def narrow_book():
    book={}
    with ZipFile(REGION) as archive:
        for sheet,table in [('Overview','Settings'),('Selected model groups','Groups')]:
            _,headers,_,rows=table_rows(archive,sheet,table)
            headers=list(rows[0][1]) if rows else headers
            book.setdefault(sheet,{})[table]=(headers,[[r.get(h) for h in headers] for _,r in rows])
    return book

def main():
    assert sha(PACKET)==PACKET_SHA,'Handoff changed'
    packet=read(PACKET)
    report_name,report_date,summary=read_report(ROOT,REPORT,MID)
    assert (report_name,report_date)==('Ido Carmel','2026-11-14')
    assert summary==packet['signed_summary']
    assert sha(REPORT)==packet['source_report_sha256']
    assert sha(MODEL/'model.json')==packet['canonical_model_sha256']
    verify_report(REPORT)
    index=ROOT/packet['reviewed_diagnostic_index']
    assert sha(index)==packet['reviewed_diagnostic_index_sha256']
    # Root's independent runtime audit must precede this shared registration.
    audit=read(RUN/'qa/LME_003_exclusion_audit.json')
    assert audit['passed'] and audit['packet_sha256']==PACKET_SHA
    for relative,digest in audit['authenticated_inputs'].items():
        candidate=(ROOT/relative).resolve()
        assert candidate.is_relative_to(ROOT)
        assert sha(candidate)==digest,relative
    book=narrow_book()
    settings=dict(book['Overview']['Settings'][1])
    assert settings['selected_model_id']==settings['results_model_id']==MID
    header,rows=book['Selected model groups']['Groups']
    ids=review_group_sequences(dict(zip(header,row)) for row in rows)
    excluded_seq=packet['excluded_seq']
    assert set(excluded_seq)==set(audit['excluded_seq']) and len(excluded_seq)==31
    excluded=[name for name,value in ids.items() if value in excluded_seq]
    assert excluded==packet['excluded_group_ids_in_workbook_order']
    protected=[REGION,REPORT,MODEL/'model.json',MODEL/'sppr_source.xlsx',
               MODEL/'results/regional_snapshot.xlsx',MODEL/'results/result_manifest.json',
               MODEL/'model_validation/taxon_mapping.xlsx',PACKET,index]
    protected=list(dict.fromkeys([*protected,*[(ROOT/path).resolve() for path in audit['authenticated_inputs']]]))
    before_sources={path:fingerprint(path) for path in protected}
    before_pages={name:sha(ROOT/'interactive_map'/name) for name in ['index.html','trends.html','sources.html']}
    with central_lock(ROOT):
        assert sha(PROJECT)==BASE_SHA,'Central baseline changed; inspect before registration'
        if BASELINE.exists():assert sha(BASELINE)==BASE_SHA
        else:shutil.copyfile(PROJECT,BASELINE)
        with patch('tools.project_core.calculations.coverage.ensure_validated_coverage',side_effect=AssertionError('Scientific inventory forbidden')):
            with publication_transaction(ROOT) as publication:
                _register_review(PROJECT,REPORT,UNIT,MID,excluded_seq)
                publication.checkpoint([PROJECT])
                _refresh_reviews(PROJECT,BASELINE,[UNIT],model_ids={UNIT:MID},publish=False)
                with ZipFile(PROJECT) as archive:
                    matches=[r for _,r in table_rows(archive,'Models & coverage','Models')[3]
                             if (r['unit_id'],r['model_id'])==(UNIT,MID)]
                assert len(matches)==1
                row=matches[0]
                approved=approved_review(ROOT,row,book)
                assert approved['status']=='Validated by researcher'
                assert approved['excluded_group_ids']==excluded
                assert approved['sections']==summary['sections']
                assert approved['report_sha256']==sha(REPORT)
                assert approved['model_sha256']==sha(MODEL/'model.json')
                for path,digest in before_sources.items():assert fingerprint(path)==digest,str(path)
                for name,digest in before_pages.items():assert sha(ROOT/'interactive_map'/name)==digest,name
                result={'schema_version':1,'passed':True,'unit_id':UNIT,'model_id':MID,
                    'registered_status':row['researcher_review_status'],
                    'researcher_name':report_name,'researcher_review_date':report_date,
                    'report_sha256':sha(REPORT),'canonical_sha256':sha(MODEL/'model.json'),
                    'excluded_seq':excluded_seq,'excluded_group_ids':excluded,
                    'project_before_sha256':BASE_SHA,'project_sha256':sha(PROJECT),
                    'pre_registration_snapshot':BASELINE.relative_to(ROOT).as_posix(),
                    'exact_review_replay_passed':True,'pages_unchanged':True,
                    'numerical_adoption_performed':False,'scientific_runs':0,
                    'numerical_scope_note':'Existing numerical workbooks are unchanged and still predate the signed ON0.1 run. Their adoption and page publication remain separate pending coordinator work.',
                    'authorization':{'source_chat':'01a1dac2-d77f-7690-808f-d3e65e801235','human_message_id':'01a1db16-0e8f-74b0-b45d-0ecf3e269f58'},
                    'source_handoff_sha256':PACKET_SHA,'timestamp_utc':datetime.now(timezone.utc).isoformat()}
        write(RUN/'qa/LME_003_registration.json',result)
        write(MODEL/'model_validation/evidence/source_review/researcher_registration_20261114.json',result)
    print(json.dumps({'registered':UNIT,'project_sha256':result['project_sha256'],'excluded_groups':len(excluded),'pages_updated':False,'scientific_runs':0}),flush=True)

if __name__=='__main__':main()
