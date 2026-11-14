"""Final data/control acceptance for three negative decisions. No browser claim.
Read-only by default; --write-receipts writes ONLY exact model-local receipts.
Run after successful coordinator publication, never during a central write.
"""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime,timezone
import argparse,importlib.util,json,re,sys
SCRIPT=Path(__file__).resolve();RUN=SCRIPT.parents[1]
ROOT=next(p for p in SCRIPT.parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('negative_batch_sources',SCRIPT.with_name('register_negative_batch.py'));batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)
from tools.project_core.validation.researcher_review import sha,table_rows,read_report,approved_review,FIELDS
from tools.project_core.registry.discovery import region_directory,resolve_model
from tools.project_core.workbooks.workbooks import read_book,overview

def require(value,message):
    if not value:raise ValueError(message)

def rows(path):
    with ZipFile(path) as z:return {(r['unit_id'],r['model_id']):r for _,r in table_rows(z,'Models & coverage','Models')[3]}

def check(publication_receipt=None):
    reports,protected,_=batch.preflight();project=ROOT/'Project.xlsx';digest=sha(project);metadata=rows(project)
    if publication_receipt:
        receipt=json.loads(publication_receipt.read_text(encoding='utf-8-sig'));prior=publication_receipt.parent/'Project_before_registration.xlsx'
        require(sha(prior)==receipt['before_project'],'Transaction baseline changed')
        for path,wanted in receipt['protected'].items():require(sha(path)==wanted,'Protected transaction input changed: '+path)
        before=rows(prior)
        for key,row in before.items():
            require(key in metadata,'Existing model disappeared')
            fields=('selected','selection_rationale') if key in batch.PAIRS else (*FIELDS,'selected','selection_rationale')
            require({f:row.get(f) for f in fields}=={f:metadata[key].get(f) for f in fields},'Prior review/default changed: '+str(key))
    page_states={}
    for filename,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
        path=ROOT/'interactive_map'/filename;text=path.read_text(encoding='utf-8')
        require(f'<meta name="ppr-project-sha256" content="{digest}">' in text,'Page Project fingerprint differs')
        start=text.index('const '+var+'=')+len('const '+var+'=');payload,_=json.JSONDecoder().raw_decode(text,start)
        require('.researcher-disqualified-name' in text and '#b42318' in text,'Red disqualification style missing')
        require('Validated by researcher' in text,'Validated-only control absent')
        page_states[filename]={'sha256':sha(path),'variable':var,'units':payload['network']['units'] if var=='DB' else payload['units']}
    results=[]
    for (unit,model),report in zip(batch.PAIRS,reports):
        row=metadata[(unit,model)];book=read_book(region_directory(ROOT,unit)/(unit+'.xlsx'))
        name,date,source=read_report(ROOT,report,model);review=approved_review(ROOT,row,book)
        require(review is not None and review['status']=='Disqualified by researcher','Inactive negative decision')
        for field in ['verdict','reason','sections']:require(review[field]==source[field],'Source equality failed: '+field)
        require(review['verdict']=='MODEL DISQUALIFIED' and review['sections']==[] and review['excluded_group_ids']==[],'Rejection transferred positive sections/exclusions')
        require((review['researcher_name'],review['review_date'])==(name,date)==('Ido Carmel','2026-11-14'),'Signature mismatch')
        selected=overview(book)['selected_model_id'];page_proof={}
        for filename,page in page_states.items():
            value=page['units'][unit];default=value['models'][value['default_model']]['id'] if page['variable']=='DB' else value['default_model']
            require(default==selected,'Page default differs from preserved regional selection')
            matches=[m for m in value['models'] if m['id']==model];require(len(matches)==1,'Exact reviewed model missing/ambiguous')
            item=matches[0];require(item.get('researcher_review')==review,'Page review differs from fresh signed source')
            require(item.get('display_ppr_excluded_group_ids')==[] and not item.get('recorded_review_pending'),'Unexpected exclusions/pending review')
            if model==batch.PAIRS[-1][1]:
                require(item.get('verified') is False and item.get('scopes')=={},'Pooled candidate borrowed numerical readiness')
                require('values' not in item and 'workbook' not in item,'Pooled candidate borrowed default results')
                require(item.get('source')==row['model_path'],'Pooled candidate source differs')
                require(review.get('review_scope')=='model_source' and not row.get('reviewed_calculation_input_sha256'),'Pooled review borrowed calculation identity')
            page_proof[filename]={'sha256':page['sha256'],'review_exact':True,'selected_model_id':default,'negative_excluded_from_validated_status':review['status']!='Validated by researcher'}
        results.append({'unit_id':unit,'model_id':model,'project_sha256':digest,'report_sha256':sha(report),'canonical_sha256':sha(resolve_model(region_directory(ROOT,unit),model)),'review':review,'pages':page_proof,'data_and_control_checks_passed':True,'browser_UI_checked':False,'browser_limitation':'Browser verification was unavailable by coordinator policy; these are payload/style/control-source checks only.','transaction_preservation_receipt_checked':publication_receipt is not None})
    require(sha(project)==digest,'Project changed during acceptance')
    for filename,page in page_states.items():require(sha(ROOT/'interactive_map'/filename)==page['sha256'],'Page changed during acceptance')
    for path,wanted in protected.items():require(sha(path)==wanted,'Signed source changed during acceptance')
    return results

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--publication-receipt',type=Path);parser.add_argument('--write-receipts',action='store_true');args=parser.parse_args()
    require(not(ROOT/'.project-write.lock').exists(),'Central writer active; wait for publication completion')
    results=check(args.publication_receipt)
    if args.write_receipts:
        stamp=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')
        for result in results:
            model=resolve_model(region_directory(ROOT,result['unit_id']),result['model_id']).parent
            directory=model/'model_validation/work'/('2026-11-14_235500_publication_acceptance')/'outputs';directory.mkdir(parents=True,exist_ok=True)
            path=directory/('coordinator_acceptance_'+stamp+'.json');path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            result['receipt_path']=path.relative_to(ROOT).as_posix()
    print(json.dumps({'passed':True,'models':[{'unit_id':r['unit_id'],'model_id':r['model_id'],'receipt_path':r.get('receipt_path')} for r in results],'browser_UI_checked':False},indent=2))
if __name__=='__main__':main()
