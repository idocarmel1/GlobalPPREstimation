"""Publish the handed-off LME049 review and authenticated retained scenario."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
import importlib.util, json, re, shutil, sys, time

sys.stdout.reconfigure(encoding='utf-8')
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
RUN=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'Project.xlsx'
from tools.project_core.registry.discovery import region_directory,resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.validation.researcher_review import read_report,approved_review,table_rows
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews,_build
from tools.project_core.calculations.coverage import ensure_validated_coverage,_preserved_inputs
from tools.project_core.registry.update_project import _update
from tools.project_core.workbooks.workbooks import read_book,overview,sha

MIDS={u:'941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)' for u in ['HS_071','EEZ_598','EEZ_941']}
MIDS.update(LME_038='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)',
            LME_049='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)')
REGIONS={u:region_directory(ROOT,u)/(u+'.xlsx') for u in MIDS}
MODELS={u:resolve_model(REGIONS[u].parent,MIDS[u]).parent for u in MIDS}
MODEL=MODELS['LME_049'];REGION=REGIONS['LME_049']
HANDOFF=MODEL/'model_validation/evidence/source_review/researcher_registration_20261114.json'

def read(path):return json.loads(path.read_text('utf-8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')

def verify_final(expected_sources,protected,prior_regions):
    for path,digest in expected_sources.items():assert sha(path)==digest,str(path)+' changed'
    for unit,digest in prior_regions.items():assert sha(REGIONS[unit])==digest,unit+' previously published workbook changed'
    with ZipFile(PROJECT) as archive:
        central={(r['unit_id'],r['model_id']):r for _,r in table_rows(archive,'Models & coverage','Models')[3]}
    result={'project_sha256':sha(PROJECT),'units':{}}
    reviews={}
    for unit,mid in MIDS.items():
        book=read_book(REGIONS[unit]);settings=overview(book)
        assert settings['selected_model_id']==mid and settings['results_model_id']==mid
        if unit=='LME_049':
            assert _preserved_inputs(book)==protected
            assert settings.get('production_eligible') is None
            assert settings.get('production_eligibility_note'), 'Eligibility note missing from Overview Settings'
        report=MODELS[unit]/'model_validation/validation.docx'
        name,date,summary=read_report(ROOT,report,mid)
        row=central[(unit,mid)];review=approved_review(ROOT,row,book)
        assert row['researcher_review_status']=='Validated by researcher' and review
        assert (row['researcher_name'],row['researcher_review_date'])==(name,date)
        assert row['validation_report_sha256']==sha(report)
        assert row['reviewed_model_sha256']==sha(MODELS[unit]/'model.json')
        assert json.loads(row['researcher_review_summary'])['sections']==summary['sections']
        wanted=['Marine mammals'] if unit=='LME_038' else ['Toothed whales (all)'] if unit=='LME_049' else []
        assert review['excluded_group_ids']==wanted
        reviews[unit]=review
        manifest=read(MODELS[unit]/'results/result_manifest.json')
        assert len(manifest['method_coverage']['expected_methods'])==len(manifest['method_coverage']['methods'])==22
        if unit!='LME_038':
            assert manifest['effective_flags']['constructor']['use_ee_floor'] is True
            assert manifest['effective_flags']['constructor']['ee_floor']==.1
        if unit=='LME_049':
            marker=manifest['effective_flags']['runtime_initialization']
            assert marker and marker['reexecution_supported'] is False
        result['units'][unit]={'model_id':mid,'report_sha256':sha(report),'canonical_sha256':sha(MODELS[unit]/'model.json'),
            'researcher':name,'review_date':date,'exclusions':wanted,'method_outcomes':{k:v['status'] for k,v in manifest['method_coverage']['methods'].items()}}
    for filename,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
        page=(ROOT/'interactive_map'/filename).read_text('utf-8')
        marker=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',page)
        assert marker and marker.group(1)==sha(PROJECT)
        start=page.index('const '+variable+'=')+len('const '+variable+'=')
        payload,_=json.JSONDecoder().raw_decode(page,start)
        units=payload['network']['units'] if variable=='DB' else payload['units']
        for unit,mid in MIDS.items():
            data=units[unit];matching=[m for m in data['models'] if m['id']==mid]
            assert len(matching)==1
            model=matching[0]
            assert model.get('researcher_review')==reviews[unit],(filename,unit,'review')
            assert not model.get('recorded_review_pending'),(filename,unit,'pending')
            assert model.get('display_ppr_excluded_group_ids',[])==reviews[unit]['excluded_group_ids']
            default=data['models'][data['default_model']]['id'] if variable=='DB' else data['default_model']
            assert default==mid
            result['units'][unit][filename]='PASS'
        result[filename+'_sha256']=sha(ROOT/'interactive_map'/filename)
    return result

def main():
    started=time.time();handoff=read(HANDOFF)
    assert handoff['unit_id']=='LME_049' and handoff['model_id']==MIDS['LME_049']
    assert handoff['excluded_group_ids']==['Toothed whales (all)']
    previous=ROOT/handoff['project_before_path']
    assert sha(previous)==handoff['project_before_sha256']
    assert sha(PROJECT)==handoff['project_after_sha256'],'Project advanced after the registration handoff'
    assert sha(MODEL/'model.json')==handoff['canonical_sha256']
    assert sha(MODEL/'model_validation/validation.docx')==handoff['report_sha256']
    wrapper_path=RUN/'code/verified_lme049_package.py'
    spec=importlib.util.spec_from_file_location('verified_lme049_package',wrapper_path)
    package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
    expected={p:sha(p) for model in MODELS.values() for p in [model/'model.json',model/'model_validation/validation.docx',model/'model_validation/taxon_mapping.xlsx']}
    for model in MODELS.values():verify_report(model/'model_validation/validation.docx')
    protected=_preserved_inputs(read_book(REGION))
    prior_regions={u:sha(p) for u,p in REGIONS.items() if u!='LME_049'}
    print('Verifying authenticated retained LME049 package',flush=True)
    package.verify_package()
    with central_lock(ROOT),publication_transaction(ROOT,extra_region_paths=[REGION],extra_model_dirs=[MODEL]) as publication:
        assert sha(PROJECT)==handoff['project_after_sha256']
        before=RUN/'inputs/Project_before_LME049_publication.xlsx'
        if before.exists():assert sha(before)==sha(PROJECT)
        else:shutil.copyfile(PROJECT,before)
        _refresh_reviews(PROJECT,previous,['LME_049'],model_ids={'LME_049':MIDS['LME_049']},publish=False)
        print('LME049 bounded review gate PASS; adopting authenticated retained scenario',flush=True)
        adopted=package.apply(publication)
        publication.checkpoint(adopted['written_paths'],fingerprints=adopted.get('written_hashes'))
        print('LME049 adopted; checking complete validated-method inventories',flush=True)
        coverage=ensure_validated_coverage(ROOT,lock_held=True)
        publication.checkpoint(coverage.get('written_paths',coverage.get('written_region_paths',[])),fingerprints=coverage.get('written_hashes'))
        changed={'LME_049'}|set(coverage['changed_units'])
        _update(ROOT,[region_directory(ROOT,u)/(u+'.xlsx') for u in sorted(changed)],False)
        publication.checkpoint([PROJECT])
        print('Rebuilding map, trends and source views',flush=True)
        _build(PROJECT,only_units=changed)
        result=verify_final(expected,protected,prior_regions)
        result.update(passed=True,bounded_review_gate='PASS',handoff_sha256=sha(HANDOFF),
            adopted_package=adopted,coverage_preflight=coverage,changed_units=sorted(changed),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.time()-started)
        write(RUN/'qa/final_publication.json',result)
    print(json.dumps({'published':True,'project_sha256':sha(PROJECT),'verified_units':list(MIDS),'elapsed_seconds':time.time()-started}),flush=True)

if __name__=='__main__':main()
