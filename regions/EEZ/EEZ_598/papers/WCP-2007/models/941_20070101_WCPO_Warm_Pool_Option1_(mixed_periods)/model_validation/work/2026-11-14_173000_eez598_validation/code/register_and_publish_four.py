"""Guarded combined pending-review publication using authenticated result packages."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, shutil, sys, time
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd().resolve();sys.path.insert(0,str(ROOT))
RUN=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'Project.xlsx'
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
ORDER=['EEZ_941','HS_071','LME_038','EEZ_598']
from tools.project_core.registry.discovery import region_directory,resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.validation.researcher_review import _register_review,read_report,approved_review,table_rows
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews,_build
from tools.project_core.calculations.coverage import ensure_validated_coverage,_preserved_inputs
from tools.project_core.registry.update_project import _update
from tools.project_core.workbooks.workbooks import read_book,overview,sha

MIDS={u:MID for u in ORDER};MIDS['LME_038']='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
REGIONS={u:region_directory(ROOT,u)/(u+'.xlsx') for u in ORDER}
MODELS={u:resolve_model(REGIONS[u].parent,MIDS[u]).parent for u in ORDER}
REPORTS={u:MODELS[u]/'model_validation/validation.docx' for u in ORDER}
BASELINE=MODELS['EEZ_941']/'model_validation/evidence/researcher_review_20261114/Project_before_registration.xlsx'
BASELINE_SHA='e387b01f895974bb7a11b5a13fd0c2a601ff089be74e0c13180f8d80d39c7b2b'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def read(path):return json.loads(path.read_text('utf-8'))
def write(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
def verify_published(expected_hashes,protected):
    result={'source_to_project_and_both_pages':{},'project_sha256':sha(PROJECT)}
    with ZipFile(PROJECT) as z:metadata={(r['unit_id'],r['model_id']):r for _,r in table_rows(z,'Models & coverage','Models')[3]}
    reviews={}
    for unit in ORDER:
        for path,digest in expected_hashes.items():assert sha(path)==digest, str(path)+' changed'
        book=read_book(REGIONS[unit]);assert _preserved_inputs(book)==protected[unit],unit+' protected inputs changed'
        assert overview(book)['selected_model_id']==MIDS[unit]
        row=metadata[(unit,MIDS[unit])];name,date,summary=read_report(ROOT,REPORTS[unit],MIDS[unit])
        assert row['researcher_review_status']=='Validated by researcher'
        assert (row['researcher_name'],row['researcher_review_date'])==(name,date)
        assert row['validation_report_sha256']==sha(REPORTS[unit])
        assert row['reviewed_model_sha256']==sha(MODELS[unit]/'model.json')
        assert json.loads(row['researcher_review_summary'])['sections']==summary['sections']
        reviews[unit]=approved_review(ROOT,row,book);assert reviews[unit],unit+' approval gate failed'
        manifest=read(MODELS[unit]/'results/result_manifest.json')
        outcomes=manifest['method_coverage']['methods']
        assert len(outcomes)==len(manifest['method_coverage']['expected_methods'])==22
        if unit!='LME_038':
            assert manifest['effective_flags']['constructor']['use_ee_floor'] is True
            assert manifest['effective_flags']['constructor']['ee_floor']==.1
        result['source_to_project_and_both_pages'][unit]={'reviewer':name,'date':date,'status':row['researcher_review_status'],
            'report_sha256':sha(REPORTS[unit]),'model_sha256':sha(MODELS[unit]/'model.json'),
            'method_statuses':{k:v['status'] for k,v in outcomes.items()},'protected_inputs_equal':True,
            'effective_flags':manifest['effective_flags'],'exclusions':reviews[unit]['excluded_group_ids']}
    for name,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
        page=(ROOT/'interactive_map'/name).read_text('utf-8')
        assert re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',page).group(1)==sha(PROJECT)
        mark='const '+var+'=';payload,_=json.JSONDecoder().raw_decode(page,page.index(mark)+len(mark))
        units=payload['network']['units'] if var=='DB' else payload['units']
        for u in ORDER:
            unit=units[u];matching=[m for m in unit['models'] if m['id']==MIDS[u]];assert len(matching)==1
            model=matching[0];assert model.get('researcher_review')==reviews[u],(name,u,'review mismatch')
            assert not model.get('recorded_review_pending'),(name,u,'pending')
            chosen=unit['models'][unit['default_model']]['id'] if var=='DB' else unit['default_model']
            assert chosen==MIDS[u],(name,u,'selection')
            assert model.get('display_ppr_excluded_group_ids',[])==(['Marine mammals'] if u=='LME_038' else [])
            result['source_to_project_and_both_pages'][u][name]='PASS'
    return result

def main():
    started=time.time();assert sha(BASELINE)==BASELINE_SHA
    wcpo=load('verified_floor_packages',MODELS['EEZ_598']/'model_validation/work/2026-11-14_160800_floor_adoption/code/verified_floor_packages.py')
    lme=load('adopt_current_diagnostics',MODELS['LME_038']/'model_validation/work/2026-11-14_152558_signoff/code/adopt_current_diagnostics.py')
    expected={p:sha(p) for u in ORDER for p in [REPORTS[u],MODELS[u]/'model.json',MODELS[u]/'model_validation/taxon_mapping.xlsx']}
    for u in ORDER:verify_report(REPORTS[u]);read_report(ROOT,REPORTS[u],MIDS[u])
    protected={u:_preserved_inputs(read_book(REGIONS[u])) for u in ORDER}
    print('Checking prepared packages and exact source identities',flush=True)
    lme.verify_package()
    for unit in ['HS_071','EEZ_598','EEZ_941']:wcpo.verify_package(unit)
    with central_lock(ROOT),publication_transaction(ROOT,extra_region_paths=list(REGIONS.values()),extra_model_dirs=list(MODELS.values())) as publication:
        before=RUN/'inputs/Project_before_combined_publication.xlsx'
        if before.exists():assert sha(before)==sha(PROJECT),'Existing rollback source differs'
        else:shutil.copyfile(PROJECT,before)
        _register_review(PROJECT,REPORTS['EEZ_598'],'EEZ_598',MID,[])
        publication.checkpoint([PROJECT])
        print('EEZ_598 registered; checking combined pending-review replay and old page fingerprints',flush=True)
        _refresh_reviews(PROJECT,BASELINE,ORDER,model_ids=MIDS,publish=False)
        print('Combined bounded review gate PASS; adopting authenticated numerical packages',flush=True)
        adopted={}
        adopted['LME_038']=lme.apply(publication)
        publication.checkpoint(adopted['LME_038']['written_paths'],fingerprints=adopted['LME_038'].get('written_hashes'))
        for unit in ['HS_071','EEZ_598','EEZ_941']:
            adopted[unit]=wcpo.apply(publication,unit)
            publication.checkpoint(adopted[unit]['written_paths'],fingerprints=adopted[unit].get('written_hashes'))
            print(unit+': adopted retained floor0.1 results and regional arithmetic',flush=True)
        print('Running mandatory full validated-model inventory preflight',flush=True)
        coverage=ensure_validated_coverage(ROOT,lock_held=True)
        publication.checkpoint(coverage.get('written_paths',coverage.get('written_region_paths',[])),fingerprints=coverage.get('written_hashes'))
        changed=set(ORDER)|set(coverage['changed_units'])
        _update(ROOT,[region_directory(ROOT,u)/(u+'.xlsx') for u in sorted(changed)],False)
        publication.checkpoint([PROJECT])
        print('Project consolidated; rebuilding map, trends and sources',flush=True)
        _build(PROJECT,only_units=changed)
        result=verify_published(expected,protected)
        result.update({'passed':True,'bounded_review_gate':'PASS','baseline_sha256':BASELINE_SHA,'project_before_sha256':sha(before),
            'coverage_preflight':coverage,'adopted_packages':adopted,'changed_units':sorted(changed),
            'timestamp_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.time()-started})
        write(RUN/'qa/combined_publication.json',result)
    print(json.dumps({'published':True,'project_sha256':sha(PROJECT),'regions':ORDER,'elapsed_seconds':time.time()-started}),flush=True)

if __name__=='__main__':main()
