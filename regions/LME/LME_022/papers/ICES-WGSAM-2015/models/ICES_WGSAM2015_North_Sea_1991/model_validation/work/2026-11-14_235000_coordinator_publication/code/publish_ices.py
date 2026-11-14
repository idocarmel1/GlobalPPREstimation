"""Coordinator ICES retained adoption. Default is isolated preflight; --publish
is the only live mutation route. No scientific inventory or fresh calculation.
"""
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as etree
import argparse, copy, importlib.util, json, re, shutil, sys, tempfile, time
sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve();RUN=SCRIPT.parents[1]
ROOT=next(p for p in SCRIPT.parents if (p/'Project.xlsx').is_file());sys.path.insert(0,str(ROOT))
from tools.project_core.validation.researcher_review import sha, table_rows, read_report, approved_review, review_group_sequences, _register_review, attach_payload_review, FIELDS
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.workbooks.workbooks import read_book, overview, records
from tools.project_core.workbooks.workbooks import digest_tables
from tools.project_core.maps.original_atlas_data import detail_from_book
UNIT='LME_022';MID='ICES_WGSAM2015_North_Sea_1991'
MODEL=ROOT/f'regions/LME/{UNIT}/papers/ICES-WGSAM-2015/models/{MID}'
REGION=ROOT/f'regions/LME/{UNIT}/{UNIT}.xlsx';REPORT=MODEL/'model_validation/validation.docx';PROJECT=ROOT/'Project.xlsx'
EXCLUDED=[1,2,3,4,65]
NAMES=['BaleenWhales','ToothedWhales','Seals','SurfaceFeedingSeabirds','DivingSeabirds']
STAGE=MODEL/'model_validation/work/2026-11-14_230000_retained_adoption'
PACKAGE=STAGE/'outputs/retained_package_v2';WRAPPER=STAGE/'code/adopt_retained.py'
CANONICAL_SHA='450e0f43822a34a02d4d26ad71358aeef32af8daaff7fcf07cd95ef2131cf97a'
REPORT_SHA='aa5516a7d20ddd25ac803b026ea96627a8fd51897b02c675d6aedbb2f1643b90'

def require(value,message):
    if not value:raise ValueError(message)

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=str,allow_nan=False)+'\n',encoding='utf-8')
def fingerprint(path):return sha(path) if Path(path).is_file() else None

def rows(project):
    with ZipFile(project) as archive:return {(r['unit_id'],r['model_id']):r for _,r in table_rows(archive,'Models & coverage','Models')[3]}

def pages(root):
    result={}
    for filename,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
        path=root/'interactive_map'/filename;text=path.read_text(encoding='utf-8')
        match=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',text)
        require(match,'Missing Project fingerprint: '+filename)
        start=text.index('const '+var+'=')+len('const '+var+'=');data,_=json.JSONDecoder().raw_decode(text,start)
        result[filename]={'sha256':sha(path),'project_sha256':match.group(1),'units':data['network']['units'] if var=='DB' else data['units'],'variable':var}
    return result

def default(page,unit):
    value=page['units'][unit];selected=value['default_model']
    return value['models'][selected]['id'] if page['variable']=='DB' else selected

def review_projection(page):
    return {unit:{'default':default(page,unit),'reviews':{m['id']:{k:copy.deepcopy(m[k]) for k in ('researcher_review','display_ppr_excluded_group_ids','recorded_review_pending') if k in m} for m in data['models']}} for unit,data in page['units'].items()}

AUTHORIZED_MAPPING={('Selected model groups','Groups'),('PPR','Matching'),('PPR','Allocation assumptions'),('PPR','Mapping review')}
AUTHORIZED_OUTPUTS={('Overview','Settings'),('Selected model groups','Group SPPR'),('PPR','Annual'),('PPR','Taxon SPPR'),('PPR','Taxon PPR inspected year'),('PPR–NPP','Ratios'),*[('Diagnostics',name) for name in ['model_health','EE floor','EE floor groups','Method coverage','Retained adoption']]}

def independent_inputs(book):
    return digest_tables([(sheet,name,data) for sheet,tables in book.items() for name,data in tables.items() if sheet in {'Catch','Classic PPR','NPP'}])

def mapping_identity(book):
    return digest_tables([(sheet,name,book[sheet][name]) for sheet,name in sorted(AUTHORIZED_MAPPING)])

def table_counts(book):
    return {sheet+'/'+name:len(records(book,sheet,name)) for sheet,name in sorted(AUTHORIZED_MAPPING)}

PROGRESS={'stages':[],'started_utc':datetime.now(timezone.utc).isoformat()}
def step(name,action):
    item={'stage':name,'started_utc':datetime.now(timezone.utc).isoformat(),'status':'running'}
    PROGRESS['stages'].append(item);write(RUN/'qa/progress.json',PROGRESS)
    print('['+item['started_utc']+'] '+name,flush=True);started=time.monotonic()
    try:
        result=action();item['status']='passed';return result
    except Exception as error:
        item.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        item['elapsed_seconds']=round(time.monotonic()-started,3);write(RUN/'qa/progress.json',PROGRESS)

def authenticate_package():
    pins=read(RUN/'inputs/package_pin.json')
    require(sha(WRAPPER)==pins['wrapper_sha256'] and sha(PACKAGE/'preparation.json')==pins['preparation_sha256'],'Frozen ICES package changed')
    spec=importlib.util.spec_from_file_location('ices_retained_coordinator',WRAPPER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    plan=module.verify_package(PACKAGE)
    require(plan['ready_for_apply'] and plan['unit_id']==UNIT and plan['model_id']==MID,'ICES preparation incomplete or wrong identity')
    promotions=[]
    for item in plan['promotions']:
        source=(PACKAGE/item['source']).resolve();target=(ROOT/item['target']).resolve()
        require(source.is_relative_to(PACKAGE) and (target==REGION or target.is_relative_to(MODEL)),'Promotion outside exact ICES scope')
        require(sha(source)==item['sha256'],'Staged promotion changed')
        promotions.append((source,target,item['sha256']))
    require(len(promotions)==8 and len({t for _,t,_ in promotions})==8,'Expected eight unique promotions')
    return {'module':module,'plan':plan,'promotions':promotions,'pins':pins}

def package_unchanged(package,installed=False):
    require(sha(WRAPPER)==package['pins']['wrapper_sha256'] and sha(PACKAGE/'preparation.json')==package['pins']['preparation_sha256'],'Package changed')
    targets={t for _,t,_ in package['promotions']}
    for source,target,digest in package['promotions']:
        require(sha(source)==digest,'Staged bytes changed')
        if installed:require(sha(target)==digest,'Installed promotion differs: '+str(target))
    for relative,digest in package['plan']['consumed_inputs'].items():
        path=ROOT/relative
        if installed and path in targets:continue
        require(fingerprint(path)==digest,'Consumed input changed: '+relative)

def initialize(package):
    require(sha(REPORT)==REPORT_SHA and sha(MODEL/'model.json')==CANONICAL_SHA,'Signed/canonical ICES source changed')
    name,date,summary=read_report(ROOT,REPORT,MID)
    require((name,date)==('Ido Carmel','2026-11-14') and summary.get('status','Validated by researcher')=='Validated by researcher','Signed ICES decision changed')
    verify_report(REPORT)
    current=read_book(REGION);settings=overview(current)
    require(settings['selected_model_id']==MID,'ICES regional selection changed')
    staged=next(s for s,t,_ in package['promotions'] if t==REGION);book=read_book(staged)
    require(overview(book).get('results_model_id')==MID,'Staged calculation belongs to another model')
    identities=review_group_sequences(records(book,'Selected model groups','Groups'))
    require([identities.get(name) for name in NAMES]==EXCLUDED,'Staged signed group IDs differ')
    require(len(identities)==70 and len(records(book,'Selected model groups','Group SPPR'))==630,'Staged groups or coefficients incomplete')
    require(independent_inputs(current)==independent_inputs(book),'Staging changed protected independent inputs')
    selected_fields=('selected_model_id','selection_rationale','model_path')
    require({k:settings.get(k) for k in selected_fields}=={k:overview(book).get(k) for k in selected_fields},'Staging changed selection/rationale')
    current_pages=pages(ROOT);project_sha=sha(PROJECT)
    require(all(p['project_sha256']==project_sha for p in current_pages.values()),'Current pages do not match current Project; finish prior publication first')
    central=rows(PROJECT);require((UNIT,MID) in central,'Register ICES model metadata first')
    source_paths=[REPORT,MODEL/'model.json',MODEL/'model_notes.md',MODEL/'model_validation/taxon_mapping.xlsx',SCRIPT]
    source_paths += [ROOT/'tools/project_core'/p for p in ['validation/researcher_review.py','maps/build_html.py','maps/original_atlas_data.py','registry/update_project.py','registry/publication.py','registry/writes.py']]
    return {'book':book,'staged':staged,'pages':current_pages,'central':central,'project_sha256':project_sha,'selection':{k:settings.get(k) for k in selected_fields},'protected':independent_inputs(current),'staged_mapping_identity':mapping_identity(book),'old_table_counts':table_counts(current),'staged_table_counts':table_counts(book),'sources':{str(p):sha(p) for p in source_paths}}

def check_sources(state):
    for path,digest in state['sources'].items():require(sha(path)==digest,'Protected source changed: '+path)

def candidate(root,project,book):
    row=rows(project)[(UNIT,MID)];review=approved_review(root,row,book)
    name,date,summary=read_report(root,root/REPORT.relative_to(ROOT),MID)
    require(review and review['sections']==summary['sections'] and (review['researcher_name'],review['review_date'])==(name,date),'Signed source/registered review differ')
    require(len(review['excluded_group_ids'])==5 and set(review['excluded_group_ids'])==set(NAMES),'Signed five-group exclusions differ')
    _,model=detail_from_book(book,UNIT,MID);attach_payload_review(root,row,book,model,review)
    require(not model.get('recorded_review_pending'),'Staged review pending')
    for method in ['GE','TE','With Egestion']:require(model['health'][method]['status']=='WARN','Retained warning changed: '+method)
    provenance=model.get('calculation_provenance',{})
    require(provenance.get('use_ee_floor') is True and provenance.get('ee_floor')==.1,'Retained floor provenance differs')
    require(overview(book).get('production_eligible') is False,'Production restriction changed')
    return model

def copy_report_dependencies(root):
    """Mirror actual local DOCX hyperlinks before installing staged promotions."""
    word='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    with ZipFile(REPORT) as archive:
        document=etree.fromstring(archive.read('word/document.xml'))
        relationships={r.get('Id'):r.get('Target') for r in etree.fromstring(archive.read('word/_rels/document.xml.rels'))}
    dependencies={}
    for link in document.iter('{'+word+'}hyperlink'):
        target=relationships.get(link.get('{'+rel+'}id'),'')
        if not target or urlsplit(target).scheme:continue
        local_target=target.partition('#')[0]
        if not local_target:continue  # Internal Word anchor has no file dependency.
        source=(REPORT.parent/unquote(local_target)).resolve()
        require(source.is_relative_to(ROOT) and source.is_file(),'Review dependency is missing or outside the repository: '+target)
        dependencies.setdefault(source,[]).append(target)
    evidence=[]
    for source,links in sorted(dependencies.items()):
        relative=source.relative_to(ROOT);out=root/relative;digest=sha(source)
        out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,out)
        require(sha(out)==digest==sha(source),'Fixture review dependency copy differs: '+relative.as_posix())
        evidence.append({'path':relative.as_posix(),'sha256':digest,'links':sorted(set(links))})
    return evidence

def isolated_preflight(state,package):
    # A real isolated root, with exact same relative identities, avoids mocking
    # live workbook reads or accidentally registering against empty live Groups.
    from tools.project_core.maps.build_html import _refresh_reviews
    with tempfile.TemporaryDirectory(prefix='ices-preflight-',dir=RUN/'qa') as tmp:
        root=Path(tmp);project=root/'Project.xlsx';prior=root/'before.xlsx'
        shutil.copyfile(PROJECT,project);shutil.copyfile(PROJECT,prior)
        require(sha(prior)==state['project_sha256'],'Project changed before preflight copy')
        for source in [MODEL/'model.json',REPORT,MODEL/'model_notes.md',MODEL/'model_validation/taxon_mapping.xlsx']:
            target=root/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        dependencies=copy_report_dependencies(root)
        write(RUN/'qa/report_link_dependencies.json',{'report_sha256':sha(REPORT),'copied_before_staged_promotions':True,'dependencies':dependencies})
        for source,target,digest in package['promotions']:
            out=root/target.relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,out);require(sha(out)==digest,'Fixture promotion copy differs')
        (root/'interactive_map').mkdir()
        for filename,page in state['pages'].items():
            target=root/'interactive_map'/filename;shutil.copyfile(ROOT/'interactive_map'/filename,target);require(sha(target)==page['sha256'],'Page changed before fixture copy')
        _register_review(project,root/REPORT.relative_to(ROOT),UNIT,MID,EXCLUDED)
        _refresh_reviews(project,prior,[UNIT],model_ids={UNIT:MID},publish=False)
        result=candidate(root,project,state['book'])
    check_sources(state);package_unchanged(package)
    require(sha(PROJECT)==state['project_sha256'],'Live Project changed during preflight')
    require(all(sha(ROOT/'interactive_map'/n)==p['sha256'] for n,p in state['pages'].items()),'Live page changed during preflight')
    return result

def final_checks(state,package,expected):
    check_sources(state);package_unchanged(package,True)
    book=read_book(REGION);settings=overview(book)
    require(independent_inputs(book)==state['protected'],'Protected independent/manual tables changed')
    require(mapping_identity(book)==state['staged_mapping_identity'],'Authorized staged Groups/mapping tables changed')
    require({k:settings.get(k) for k in state['selection']}==state['selection'],'Selection/rationale changed')
    actual_candidate=candidate(ROOT,PROJECT,book)
    central=rows(PROJECT)
    require(set(central)==set(state['central']),'Central model identities changed')
    for key,old in state['central'].items():
        if key==(UNIT,MID):continue
        fields=FIELDS if key[0]==UNIT else (*FIELDS,'selected','selection_rationale')
        require({f:central[key].get(f) for f in fields}=={f:old.get(f) for f in fields},'Prior central review/default changed: '+str(key))
    current_pages=pages(ROOT)
    for filename,page in current_pages.items():
        require(page['project_sha256']==sha(PROJECT),'Published fingerprint differs')
        before=review_projection(state['pages'][filename]);after=review_projection(page)
        for unit,prior in before.items():
            if unit!=UNIT:require(after.get(unit)==prior,'Prior page review/default changed: '+unit)
        for model,prior in before.get(UNIT,{}).get('reviews',{}).items():
            if model!=MID:require(after[UNIT]['reviews'].get(model)==prior,'Other ICES-region candidate review changed')
        require(default(page,UNIT)==MID,'ICES is not published default')
        matches=[m for m in page['units'][UNIT]['models'] if m['id']==MID];require(len(matches)==1,'Ambiguous ICES payload')
        actual=matches[0]
        for field in ['researcher_review','display_ppr_excluded_group_ids','health','calculation_provenance']:
            require(actual.get(field)==expected.get(field)==actual_candidate.get(field),'Published staged semantics differ: '+field)
        require(not actual.get('recorded_review_pending'),'Published review pending')
        for field in ['methods','scopes']:require(actual['group_data'][field]==expected['group_data'][field],'Coefficient/missingness matrix differs')
        require([g['id'] for g in actual['group_data']['groups']]==[g['id'] for g in expected['group_data']['groups']],'Ecological groups changed')
        scopes=actual['scopes'] if filename=='index.html' else actual['taxon_scopes']
        require(scopes==expected['scopes'],'Taxon coefficients/statuses differ')
    return {'project_sha256':sha(PROJECT),'pages':{n:p['sha256'] for n,p in current_pages.items()},'promotions_verified':8,'all_prior_reviews_and_defaults_preserved':True}

def publish(state,package):
    from tools.project_core.registry.publication import publication_transaction,publication_write
    from tools.project_core.maps.build_html import _refresh_reviews,_build
    from tools.project_core.registry.update_project import _update
    run=RUN/'outputs'/datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S');run.mkdir()
    prior=run/'Project_before_ICES_registration.xlsx';shutil.copyfile(PROJECT,prior)
    require(sha(prior)==state['project_sha256'],'Project changed before transaction')
    # Track ALL promotions, including evidence_index and new diagnostic files,
    # not only the standard snapshot/result-manifest artifact list.
    targets=[target for _,target,_ in package['promotions']]
    with publication_transaction(ROOT,extra_region_paths=targets,extra_model_dirs=[MODEL]) as publication:
        package_unchanged(package);check_sources(state)
        step('adopt authenticated ICES retained package',lambda:package['module'].apply(publication,PACKAGE))
        package_unchanged(package,True)
        # Critical order: installed Groups must precede signed registration.
        with publication_write(PROJECT):step('register signed ICES review',lambda:_register_review(PROJECT,REPORT,UNIT,MID,EXCLUDED))
        step('verify exact bounded review replay',lambda:_refresh_reviews(PROJECT,prior,[UNIT],model_ids={UNIT:MID},publish=False))
        expected=step('verify installed candidate review and diagnostics',lambda:candidate(ROOT,PROJECT,read_book(REGION)))
        step('consolidate only LME022',lambda:_update(ROOT,[REGION],False));publication.checkpoint([PROJECT])
        step('build saved-data pages only LME022',lambda:_build(PROJECT,only_units={UNIT}))
        result=step('final installed bytes sources reviews defaults and diagnostics',lambda:final_checks(state,package,expected))
        write(run/'publication_receipt.json',result)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--publish',action='store_true');parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
    require(not(args.publish and args.preflight),'Choose one mode')
    from tools.project_core.registry.writes import central_lock
    with central_lock(ROOT),patch('tools.project_core.calculations.coverage.ensure_validated_coverage',side_effect=AssertionError('Scientific inventory forbidden in retained ICES publication')):
        package=step('authenticate and verify frozen retained package',authenticate_package);state=step('check current baseline and staged independent inputs',lambda:initialize(package))
        write(RUN/'qa/input_preservation.json',{k:state[k] for k in ['protected','staged_mapping_identity','old_table_counts','staged_table_counts']})
        if args.publish:result=publish(state,package)
        else:
            step('isolated staged registration replay and candidate preflight',lambda:isolated_preflight(state,package));result={'passed':True,'isolated_registration_and_gate':True,'live_mutations':False,'project_sha256':state['project_sha256']}
        write(RUN/'qa'/('publication.json' if args.publish else 'preflight.json'),result)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()



