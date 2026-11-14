"""Bounded signed-review replay and retained-only publication; never run science."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
from unittest.mock import patch
import argparse, importlib.util, json, os, re, shutil, sys, tempfile, time

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')
RUN = Path(__file__).resolve().parents[1]
PROJECT = ROOT/'Project.xlsx'
MID = '941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
ORDER = ['EEZ_941', 'HS_071', 'LME_038', 'LME_049', 'LME_050', 'EEZ_598']
MIDS = {u: MID for u in ['EEZ_941', 'HS_071', 'EEZ_598']}
MIDS.update(LME_038='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)',
            LME_049='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)',
            LME_050='50_502013_Coastal_Kyoto_Inoue_(2013)')
ADOPT = [u for u in ORDER if u != 'LME_050']
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.validation.researcher_review import _register_review, read_report, approved_review, table_rows
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews, _build
from tools.project_core.calculations.coverage import _preserved_inputs
from tools.project_core.registry.update_project import _update
from tools.project_core.workbooks.workbooks import read_book, overview, sha

REGIONS = {u: region_directory(ROOT,u)/(u+'.xlsx') for u in ORDER}
MODELS = {u: resolve_model(REGIONS[u].parent,MIDS[u]).parent for u in ORDER}
REPORTS = {u: MODELS[u]/'model_validation/validation.docx' for u in ORDER}
BASELINE = MODELS['EEZ_941']/'model_validation/evidence/researcher_review_20261114/Project_before_registration.xlsx'
BASELINE_SHA = 'e387b01f895974bb7a11b5a13fd0c2a601ff089be74e0c13180f8d80d39c7b2b'

def read(path):
    return json.loads(path.read_text('utf-8'))

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def sources():
    expected={p:sha(p) for u in ORDER for p in [REPORTS[u],MODELS[u]/'model.json',MODELS[u]/'model_validation/taxon_mapping.xlsx']}
    for u in ORDER:
        _,_,summary=read_report(ROOT,REPORTS[u],MIDS[u])
        assert summary.get('status','Validated by researcher') == ('Disqualified by researcher' if u=='LME_050' else 'Validated by researcher'),u
        if u!='LME_050': verify_report(REPORTS[u])
    assert sha(BASELINE)==BASELINE_SHA
    return expected

def bounded_gate_copy():
    """Prove the replay on an isolated copy before mutating the central workbook."""
    before=sha(PROJECT)
    fd,temporary=tempfile.mkstemp(prefix='.coordinator-gate-',suffix='.xlsx',dir=ROOT);os.close(fd)
    try:
        temporary=Path(temporary);shutil.copyfile(PROJECT,temporary)
        _register_review(temporary,REPORTS['EEZ_598'],'EEZ_598',MID,[])
        _refresh_reviews(temporary,BASELINE,ORDER,model_ids=MIDS,publish=False)
        assert sha(PROJECT)==before,'Project changed during preflight'
    finally:
        temporary.unlink(missing_ok=True)
    return {'passed':True,'live_project_sha256':before,'baseline_sha256':BASELINE_SHA,'replay_order':ORDER}

def verify(expected,protected,unchanged_region):
    for path,digest in expected.items(): assert sha(path)==digest,str(path)+' source changed'
    assert sha(REGIONS['LME_050'])==unchanged_region,'LME_050 scientific workbook changed'
    with ZipFile(PROJECT) as archive:
        central={(r['unit_id'],r['model_id']):r for _,r in table_rows(archive,'Models & coverage','Models')[3]}
    result={'project_sha256':sha(PROJECT),'units':{},'scientific_runs':0}
    reviews={}
    for u in ORDER:
        book=read_book(REGIONS[u]);settings=overview(book)
        assert _preserved_inputs(book)==protected[u],u+' protected tables changed'
        assert settings['selected_model_id']==MIDS[u]
        name,date,summary=read_report(ROOT,REPORTS[u],MIDS[u]);row=central[(u,MIDS[u])]
        assert (row['researcher_name'],row['researcher_review_date'])==(name,date)
        assert row['validation_report_sha256']==sha(REPORTS[u])
        assert row['reviewed_model_sha256']==sha(MODELS[u]/'model.json')
        saved=json.loads(row['researcher_review_summary'])
        assert saved['sections']==summary['sections']
        assert saved.get('reason')==summary.get('reason')
        review=approved_review(ROOT,row,book); assert review,u+' decision gate failed'
        wanted=['Marine mammals'] if u=='LME_038' else ['Toothed whales (all)'] if u=='LME_049' else []
        assert review['excluded_group_ids']==wanted
        reviews[u]=review
        result['units'][u]={'model_id':MIDS[u],'status':row['researcher_review_status'],'reviewer':name,'date':date,
                           'report_sha256':sha(REPORTS[u]),'exclusions':wanted,'protected_inputs_equal':True}
        if u in ADOPT:
            manifest=read(MODELS[u]/'results/result_manifest.json')
            outcomes=manifest['method_coverage']['methods']
            assert len(outcomes)==len(manifest['method_coverage']['expected_methods'])==22
            flags=manifest['effective_flags']
            if u=='LME_038':
                # The authenticated pre-floor engine has no floor kwargs.
                # Its executed evidence establishes OFF; absence alone does not.
                relative='results/diagnostics/validation_20261114/execution_evidence.json'
                evidence=next(e for e in flags['configuration_evidence'] if e['relative_path']==relative)
                executed=MODELS[u]/relative
                assert sha(executed)==evidence['sha256']
                assert read(executed)['ee_floor']['applied'] is False
                assert 'use_ee_floor' not in flags['constructor']
                assert 'ee_floor' not in flags['constructor']
            else:
                assert flags['constructor']['use_ee_floor'] is True
                assert flags['constructor']['ee_floor']==.1
            if u=='LME_049':
                assert flags['runtime_initialization']['reexecution_supported'] is False
                assert settings.get('production_eligible') is None
                assert settings.get('production_eligibility_note')
            result['units'][u]['method_outcomes']={k:v['status'] for k,v in outcomes.items()}
    for filename,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
        page=(ROOT/'interactive_map'/filename).read_text('utf-8')
        assert re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',page).group(1)==sha(PROJECT)
        mark='const '+variable+'=';payload,_=json.JSONDecoder().raw_decode(page,page.index(mark)+len(mark))
        units=payload['network']['units'] if variable=='DB' else payload['units']
        for u in ORDER:
            unit=units[u];matches=[m for m in unit['models'] if m['id']==MIDS[u]];assert len(matches)==1
            model=matches[0]
            assert model.get('researcher_review')==reviews[u],(filename,u,'source review mismatch')
            assert not model.get('recorded_review_pending'),(filename,u,'pending')
            assert model.get('display_ppr_excluded_group_ids',[])==reviews[u]['excluded_group_ids']
            default=unit['models'][unit['default_model']]['id'] if variable=='DB' else unit['default_model']
            assert default==MIDS[u],(filename,u,'selection changed')
            result['units'][u][filename]='PASS'
        result[filename+'_sha256']=sha(ROOT/'interactive_map'/filename)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    started=time.time();expected=sources()
    with central_lock(ROOT):
        if not args.publish:
            gate=bounded_gate_copy();write(RUN/'qa/bounded_replay_preflight.json',gate)
            print('Exact six-review replay and old page fingerprint gate PASS',flush=True)
            return
        gate={'baseline_sha256':BASELINE_SHA,'live_project_sha256':sha(PROJECT),'replay_order':ORDER}
        # Package wrapper is prepared and independently authenticated separately.
        package=load('coordinator_retained_packages',RUN/'code/retained_packages.py')
        package.verify_all()
        protected={u:_preserved_inputs(read_book(REGIONS[u])) for u in ORDER}
        unchanged_region=sha(REGIONS['LME_050'])
        before=RUN/'inputs/Project_before_combined_publication.xlsx'
        if before.exists():assert sha(before)==sha(PROJECT),'Prior transaction snapshot differs'
        else:shutil.copyfile(PROJECT,before)
        # Tripwire: publication is retained-data-only even if a caller regresses.
        with patch('tools.project_core.calculations.coverage.ensure_validated_coverage',side_effect=AssertionError('Scientific inventory forbidden in retained-only publication')):
            with publication_transaction(ROOT,extra_region_paths=list(REGIONS.values()),extra_model_dirs=[MODELS[u] for u in ADOPT]) as publication:
                _register_review(PROJECT,REPORTS['EEZ_598'],'EEZ_598',MID,[]);publication.checkpoint([PROJECT])
                _refresh_reviews(PROJECT,BASELINE,ORDER,model_ids=MIDS,publish=False)
                gate['passed']=True
                print('Live six-review replay and old page fingerprint gate PASS',flush=True)
                adopted=package.apply_all(publication)
                print('All five authenticated retained packages adopted; consolidating saved results',flush=True)
                _update(ROOT,[REGIONS[u] for u in ADOPT],False);publication.checkpoint([PROJECT])
                _build(PROJECT,only_units=set(ORDER))
                result=verify(expected,protected,unchanged_region)
                result.update(passed=True,bounded_gate=gate,adopted=adopted,project_before_sha256=sha(before),
                              timestamp_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.time()-started)
                write(RUN/'qa/combined_publication.json',result)
        print(json.dumps({'published':True,'project_sha256':sha(PROJECT),'units':ORDER,'scientific_runs':0}),flush=True)

if __name__=='__main__':main()
