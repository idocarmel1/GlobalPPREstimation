"""Stage retained ICES evidence and arithmetic; CLI never adopts or solves."""
from __future__ import annotations
import argparse, copy, gzip, hashlib, json, math, os, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT=Path(__file__).resolve(); RUN=SCRIPT.parents[1]; MODEL=RUN.parents[2]
ROOT=next(p for p in MODEL.parents if (p/'tools/project_core').is_dir())
REGION=ROOT/'regions/LME/LME_022/LME_022.xlsx'; PACKAGE=RUN/'outputs/retained_package_v2'
PRIMARY=MODEL/'results/diagnostics/2026-11-14_loader_repair'
AUDIT=MODEL/'model_validation/work/2026-11-14_200000_ices_full_review/qa/coordinator_retained_adoption_audit_20261114.json'
MAPPING=MODEL/'model_validation/evidence/mapping/mapping_decisions.json'
INDEX=MODEL/'model_validation/evidence/evidence_index.json'
KEYS=['new_GE','new_TE_EEfix','new_WithEgestion']; OPTIONS=dict(zip(KEYS,['GE','TE','With Egestion']))
PREFIX='retained_adoption_20261114'; EXCLUDED=[1,2,3,4,65]
sys.path.insert(0,str(ROOT))
from tools.project_core.calculations import coverage
from tools.project_core.calculations.regional import set_setting,result_hash
from tools.project_core.calculations.snapshots import dependencies
from tools.project_core.workbooks.workbooks import read_book,records,overview,table_dict,input_hash,YEARS,finite,digest_tables

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fingerprint(p):return sha(p) if Path(p).is_file() else None
def rel(p,base=ROOT):return Path(p).resolve().relative_to(Path(base).resolve()).as_posix()
def read(p):
    p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text(encoding='utf-8-sig'))
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def require(x,message):
    if not x:raise ValueError(message)
def check_inputs(values):
    for name,value in values.items():
        p=(ROOT/name).resolve();require(p.is_relative_to(ROOT) and fingerprint(p)==value,'Changed input: '+name)
def scalar(x):
    if isinstance(x,dict) and x.get('type')=='float':
        require(x['value']=='nan','Unexpected nonfinite');return None
    return x
def frame(x):return {i:{k:scalar(v) for k,v in zip(x['columns'],r)} for i,r in zip(x['index'],x['data'])}
def flatten(x):
    out={}
    def visit(path,v):
        if isinstance(v,dict):
            for k,w in v.items():visit(path+[k],w)
        elif isinstance(v,list):out['_'.join(path)]=json.dumps(v,ensure_ascii=False)
        else:out['_'.join(path)]=v
    visit([],x);return out
def patch_source_numbers(path,book):
    """Avoid openpyxl's sixteen-digit rounding of retained source values."""
    from tools.project_core.validation.researcher_review import sheet_xml,S
    from openpyxl.utils import get_column_letter
    import openpyxl
    w=openpyxl.load_workbook(path,read_only=True); wanted={}
    for s in w:
        wanted[s.title]={get_column_letter(j)+str(i):v for i,row in enumerate(s.values,1) for j,v in enumerate(row,1) if finite(v)}
    w.close()
    coeff={(r['scope'],r['group'],r['method']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')}
    w=openpyxl.load_workbook(path,read_only=True)
    for scope in ['all','inner','PP']:
        data=list(w['sppr_'+scope].values);header=data[0]
        for i,row in enumerate(data[1:],2):
            for j,key in enumerate(header,1):
                if key in KEYS:wanted['sppr_'+scope][get_column_letter(j)+str(i)]=coeff[scope,row[header.index('group_name')],key]
    for sheet,table in [('groups_df',('Selected model groups','Groups')),('model_health',('Diagnostics','model_health'))]:
        header,rows=book[table[0]][table[1]]
        wanted[sheet]={get_column_letter(j)+str(i):v for i,row in enumerate(rows,2) for j,v in enumerate(row,1) if finite(v)}
    w.close();replacements={}
    with zipfile.ZipFile(path) as z:
        for name,values in wanted.items():
            member,sheet=sheet_xml(z,name)
            for c in sheet.iter('{'+S+'}c'):
                if c.get('r') in values:
                    v=c.find('{'+S+'}v');require(v is not None,'Numeric cell absent');v.text=repr(values[c.get('r')])
            replacements[member]=ET.tostring(sheet,encoding='utf-8')
        parts=[(i,replacements.get(i.filename,z.read(i.filename))) for i in z.infolist()]
    with zipfile.ZipFile(path,'w') as z:
        for i,b in parts:z.writestr(i,b)

def prepare(package_path=None):
    package=Path(package_path or PACKAGE).resolve();require(package.is_relative_to(RUN/'outputs'),'Outside owned outputs')
    if (package/'preparation.json').exists():return verify_package(package)
    a=read(AUDIT);require(sha(AUDIT)=='1c47e1a9293a7a500003c8a797043cffcd214208c84bbfa98a76225bd62b08ec','Audit changed')
    guards={rel(AUDIT):sha(AUDIT),rel(SCRIPT):sha(SCRIPT),rel(ROOT/'README.md'):sha(ROOT/'README.md')}
    def consume(p,expected=None):
        p=Path(p);v=sha(p);require(expected is None or v==expected,'Audited input changed '+str(p));guards[rel(p)]=v;return p
    consume(REGION,a['pins']['regional_workbook']['sha256']);consume(MODEL/'model.json',a['pins']['canonical_model_sha256'])
    consume(MODEL/'model_validation/validation.docx',a['pins']['signed_DOCX_sha256']);consume(MAPPING,a['pins']['mapping_decisions_sha256'])
    consume(MODEL/'model_validation/taxon_mapping.xlsx',a['pins']['taxon_appendix_sha256'])
    consume(PRIMARY/'evidence_index.json',a['pins']['primary_evidence_index_sha256'])
    for r in read(PRIMARY/'evidence_index.json')['artifacts']:consume((PRIMARY/r['path']).resolve(),r['sha256'])
    consume(INDEX)
    for r in read(INDEX)['artifacts']:
        if r.get('availability')=='present' and r.get('sha256') and r.get('role')!='report':consume((INDEX.parent/r['path']).resolve(),r['sha256'])
    mapping=read(MAPPING)
    for p,d in mapping['input_sha256'].items():consume(ROOT/p,d)
    original=read_book(REGION);require(overview(original)['selected_model_id']==MODEL.name,'Selection changed')
    backup=RUN/'inputs/pre_adoption';backup.mkdir(parents=True,exist_ok=True)
    for p in [REGION,INDEX]:
        target=backup/p.name
        require(not target.exists() or sha(target)==sha(p),'Historical backup differs')
        if not target.exists():shutil.copyfile(p,target)
        consume(target)
    source_names=['sppr_source.xlsx','results/regional_snapshot.xlsx','results/result_manifest.json']
    for name in source_names:require(not (MODEL/name).exists(),'Unexpected existing result '+name);guards[rel(MODEL/name)]=None
    pins=RUN/'inputs/executed_engine';pins.mkdir(parents=True,exist_ok=True)
    for name,digest in a['actual_engine']['hashes'].items():
        data=subprocess.check_output(['git','show',a['actual_engine']['git_commit']+':tools/scientific_code/PPREstimation/'+name],cwd=ROOT)
        require(hashlib.sha256(data).hexdigest()==digest,'Git engine mismatch');target=pins/name
        require(not target.exists() or sha(target)==digest,'Engine pin differs');target.write_bytes(data);consume(target,digest)
    for name in coverage._arithmetic_identity():consume(ROOT/'tools/project_core'/name)
    for name in ['tools/scientific_helpers/sppr/configuration.py','tools/scientific_helpers/sppr/method_coverage.py']:consume(ROOT/name)
    run=read(PRIMARY/'run_manifest.json'); runtime=read(PRIMARY/'constructor.json.gz')['constructor_outcome']['runtime']
    groups=frame(runtime['_groups_df']);book=copy.deepcopy(original)
    group_rows=[{'seq':i,'group_type':r['trophic_info'],**r} for i,r in groups.items()]
    book['Selected model groups']['Groups']=table_dict(group_rows)
    matches=[];reviews=[];allocations=[]
    for r in mapping['rows']:
        evidence=rel(MAPPING,MODEL)+' | '+r['membership_locator']+' | '+r['allocation_source']
        reviews.append({'model_id':MODEL.name,'taxon':r['taxon'],**{k:r.get(k) for k in ['membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence']},'assumed_membership':r['assumptions']['membership_inferred'],'assumed_allocation':r['assumptions']['allocation_assumed'],'evidence':evidence})
        for g in r['groups']:
            matches.append({'model_id':MODEL.name,'taxon':r['taxon'],'group':g['group_name'],'weight':g['weight'],'confidence':r['overall_confidence'],'evidence':evidence,'explanation':r['reason']})
            allocations.append({'model_id':MODEL.name,'taxon':r['taxon'],'group':g['group_name'],'seq':g['group_id'],'weight':g['weight'],'rule':r['allocation_rule'],'confidence':r['allocation_confidence'],'source_catch':g['source_catch_t_km2_year'],'loaded_catch':None,'source_biomass':g['source_biomass_t_km2'],'limitations':r['allocation_rationale']+' Fixed across 1950–2019 and all catch bases; extrapolation not verified.','years_applied':'1950–2019','catch_bases_applied':'landings, catch, discards','evidence':evidence})
    for name,rr in [('Matching',matches),('Mapping review',reviews),('Allocation assumptions',allocations)]:book['PPR'][name]=table_dict(rr)
    flags={'constructor':a['primary_scope']['constructor'],'diagnostics':a['primary_scope']['method_options'],
        'engine_source_hashes':a['actual_engine']['hashes'],'engine_sources':{n:rel(pins/n,MODEL) for n in a['actual_engine']['hashes'] if n!='create_PPRS_excel.py'},
        'configuration_evidence':[{'relative_path':rel(PRIMARY/'run_manifest.json',MODEL),'sha256':sha(PRIMARY/'run_manifest.json'),'original_source_hash':sha(MODEL/'model.json')}],
        'runtime_initialization':{'kind':'retained_scenario','configuration_id':'ICES_1991_separate_detritus_Git38cb75d_floor_0.1','reexecution_supported':False,'stock_adapter_reconstructible':False,'description':'Saved completed repaired-loader runtime; exact source and effective state retained in constructor.json.gz; this package does not claim stock reconstruction equivalence','runtime':{'relative_path':rel(PRIMARY/'constructor.json.gz',MODEL),'sha256':sha(PRIMARY/'constructor.json.gz')},'git_commit':a['actual_engine']['git_commit']}}
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    flags=resolve_audited_configuration(MODEL,original,{'canonical_model_sha256':sha(MODEL/'model.json'),'effective_flags':flags})
    from tools.scientific_helpers.sppr import method_coverage as adapter
    for call in [lambda:adapter._constructor(flags,MODEL/'model.json'),lambda:adapter._load(MODEL/'model.json',{},flags)]:
        try:call()
        except ValueError as e:require('Unsupported retained runtime initialization' in str(e),'Unexpected engine guard')
        else:raise ValueError('Retained runtime reached scientific loader')
    outcomes={};stage_model=package/'model';stage_region=package/'regional/LME_022.xlsx'
    stage_region.parent.mkdir(parents=True,exist_ok=True);stage_model.mkdir(parents=True,exist_ok=True);shutil.copyfile(REGION,stage_region)
    status='retained ICES GE/TE/With Egestion WARN; source/model and mapping extrapolation restrictions retained; EE floor ON 0.1'
    for key in KEYS:
        v=run['answer']['methods'][key];require(v['diagnostics']['status']=='WARN','Diagnosis changed')
        cert={'method':key,'source':{'relative_path':rel(PRIMARY/(key+'.json.gz'),MODEL),'sha256':sha(PRIMARY/(key+'.json.gz'))},'audit':{'relative_path':rel(AUDIT,MODEL),'sha256':sha(AUDIT)},'effective_flags':flags,'diagnostic_status':'WARN','original_execution_annual_status':v['annual_status'],'scientific_execution_performed':False,'new_MC_draws':False,'full_inventory_claim':False,'reviewed_exclusions_display_only':EXCLUDED,
              'status_policy':'Preserve exact retained execution annual_status=ok for the three finite nonnegative WARN methods. WARN is retained in diagnostic tables and evidence; ok is arithmetic eligibility, not absence of scientific warnings or renewed approval. Existing production_eligible=False is preserved separately. LME014 inherited provisional statuses; ICES has no prior annual status to inherit.'}
        cp=stage_model/'results/diagnostics'/PREFIX/(key+'.json');write(cp,cert)
        outcomes[key]={'status':'reused','reason':'Authenticated retained execution; WARN; no new solve or MC','scopes':v['scopes'],'annual_status':copy.deepcopy(v['annual_status']),'execution_annual_status':v['annual_status'],'retained_diagnostics_flat':{'TE_option':OPTIONS[key],**flatten(v['diagnostics'])},'evidence':{'path':PREFIX+'/'+key+'.json','sha256':sha(cp),'availability':'present'},'evidence_kind':'authenticated_retained_runtime_adoption'}
    coverage._apply_outcomes(book,MODEL.name,outcomes,KEYS)
    info=runtime['ee_floor_info'];book['Diagnostics']['EE floor']=table_dict([{'field':k,'value':v} for k,v in info.items()])
    book['Diagnostics']['EE floor groups']=table_dict([{'group_seq':i,**r} for i,r in frame(runtime['ee_floor_ledger']).items()])
    book['Diagnostics']['Retained adoption']=table_dict([{'topic':'scientific provenance','detail':'Git38cb75d; separate DOM67/POM68/Discards69; 70 effective runtime groups (69 source + synthetic import). Runtime values are not source-parameter corrections.'},{'topic':'mapping','detail':'Exact retained reviewed 384-taxon/715-assignment decision set, including 88 zero weights; no reallocation or taxonomy review.'},{'topic':'historical source note','detail':overview(original)['source_note']},{'topic':'display exclusions','detail':'1,2,3,4,65; network and weights unchanged. Cetorhinus maximus → BaleenWhales retains positive historical catch over 62 years.'},{'topic':'annual status policy','detail':cert['status_policy']}])
    coverage._arithmetic(book,REGION,MODEL/'model.json',flags,original,invalidated_methods=KEYS)
    set_setting(book,'source_note','ICES WGSAM2015 North Sea 1991 retained Rpath port; separate DOM67/POM68/Discards69, floor ON 0.1; all three direct diagnostics WARN. Fixed 1991 coefficients/mapping applied to 1950–2019 LME catch; source/area/period limitations retained. Previous Scotland note is historical in Diagnostics and pre-adoption workbook.')
    set_setting(book,'production_eligible',False);set_setting(book,'calculation_status',status+'; dependent arithmetic only; no scientific rerun')
    set_setting(book,'sppr_engine_hashes',json.dumps(a['actual_engine']['hashes'],sort_keys=True))
    import pandas as pd
    coverage._update_source(stage_model/'sppr_source.xlsx',book,outcomes,effective_groups=pd.DataFrame(group_rows).set_index('seq'))
    # Keep the exact regional/source group column order for source preservation.
    import openpyxl
    w=openpyxl.load_workbook(stage_model/'sppr_source.xlsx');s=w['groups_df'];w.remove(s);s=w.create_sheet('groups_df');h,rr=book['Selected model groups']['Groups'];s.append(h)
    for r in rr:s.append(r)
    w.save(stage_model/'sppr_source.xlsx');w.close();patch_source_numbers(stage_model/'sppr_source.xlsx',book)
    set_setting(book,'results_source_sha256',sha(stage_model/'sppr_source.xlsx'))
    saved=coverage._save_calculation(stage_region,book,MODEL/'model.json',flags,copy.deepcopy(book),invalidated_methods=KEYS)
    # Independently owned input sheets retain their exact XML including human formatting.
    from tools.project_core.validation.researcher_review import sheet_xml
    with zipfile.ZipFile(REGION) as src,zipfile.ZipFile(stage_region) as dst:
        replacements={sheet_xml(dst,s)[0]:src.read(sheet_xml(src,s)[0]) for s in ['Catch','Classic PPR','NPP']}
        parts=[(i,replacements.get(i.filename,dst.read(i.filename))) for i in dst.infolist()]
    with zipfile.ZipFile(stage_region,'w') as dst:
        for i,data in parts:dst.writestr(i,data)
    saved=read_book(stage_region);require(overview(saved)['calculation_input_sha256']==input_hash(saved),'Independent XML restore invalidated inputs')
    snapshot=stage_model/'results/regional_snapshot.xlsx';shutil.copyfile(stage_region,snapshot)
    for key,digest in coverage._method_rows(saved)[1].items():outcomes[key]['group_rows_sha256']=digest
    context=coverage._context(ROOT,MODEL/'model.json',flags)
    manifest={'schema_version':1,'unit_id':'LME_022','model_id':MODEL.name,'snapshot_selected_model_id':MODEL.name,'timestamp':datetime.now(timezone.utc).isoformat(),'snapshot_sha256':sha(snapshot),'canonical_model_sha256':sha(MODEL/'model.json'),'present_canonical_model_sha256':sha(MODEL/'model.json'),'coefficient_source_sha256':sha(stage_model/'sppr_source.xlsx'),'effective_flags':flags,'code_identity':a['actual_engine']['hashes'],'provenance_status':'Authenticated retained Git38cb75d separate-detritus execution; no new science; WARN preserved','dependencies':dependencies(saved),'artifacts':{'snapshot':'regional_snapshot.xlsx','model':'../model.json','coefficients':'../sppr_source.xlsx'},'retained_adoption':{'audit':{'relative_path':rel(AUDIT,MODEL),'sha256':sha(AUDIT)},'original_regional_workbook':{'relative_path':rel(backup/'LME_022.xlsx',MODEL),'sha256':sha(backup/'LME_022.xlsx')},'actual_execution':{'relative_path':rel(PRIMARY/'run_manifest.json',MODEL),'sha256':sha(PRIMARY/'run_manifest.json')},'scientific_execution_performed':False,'new_MC_draws':False,'full_inventory_claim':False,'stock_engine_equivalence_claim':False,'group_metadata_role':'Exact saved effective runtime, not canonical extraction','historical_exclusion_caveat':a['mapping']['historical_exclusion_caveat'],'context_roles':{'method_coverage.context':'Current retained-evidence verification/arithmetic environment, not a new scientific execution'}},'method_coverage':{'schema_version':1,'scope':'Three retained direct methods only','expected_methods':KEYS,'context':context,'methods':outcomes,'execution_evidence':{},'arithmetic_code_identity':coverage._arithmetic_identity(),'protected_inputs_sha256':coverage._preserved_inputs(saved)}}
    write(stage_model/'results/result_manifest.json',manifest)
    index=read(INDEX);reports=[r for r in index['artifacts'] if r['role']=='report'];require(len(reports)==1,'Ambiguous report index')
    previous=reports[0]['sha256'];reports[0]['sha256']=sha(MODEL/'model_validation/validation.docx')
    index['signed_report_binding']={'previous_generated_draft_sha256':previous,'signed_report_sha256':reports[0]['sha256'],'bound_at':datetime.now(timezone.utc).isoformat(),'reason':'Explicit retained-adoption authorization accepts current signed source; draft render/verification records remain historical and are not claimed as renewed signed-report QA','source_authorization':a['authorization']}
    write(stage_model/'model_validation/evidence/evidence_index.json',index)
    promotions=[{'source':rel(stage_region,package),'target':rel(REGION),'sha256':sha(stage_region)}]
    for p in sorted(x for x in stage_model.rglob('*') if x.is_file()):
        target=MODEL/p.relative_to(stage_model);promotions.append({'source':rel(p,package),'target':rel(target),'sha256':sha(p)});guards.setdefault(rel(target),fingerprint(target))
    check_inputs(guards)
    plan={'schema_version':1,'package':rel(package),'unit_id':'LME_022','model_id':MODEL.name,'consumed_inputs':guards,'promotions':promotions,'context':context,'expected_methods':KEYS,'ready_for_apply':False,'numerical_adoption_performed':False,'counts':{'groups':70,'coefficients':630,'taxa':384,'assignments':715,'zero_weights':88},'status_policy':cert['status_policy']}
    write(package/'preparation.json',plan);verify_package(package);plan['ready_for_apply']=True;write(package/'preparation.json',plan);return plan

def verify_package(package_path=None,*,check_consumed=True):
    package=Path(package_path or PACKAGE).resolve();require(package.is_relative_to(RUN/'outputs'),'Outside owned package');plan=read(package/'preparation.json')
    if check_consumed:check_inputs(plan['consumed_inputs'])
    for p in plan['promotions']:
        source=(package/p['source']).resolve();target=(ROOT/p['target']).resolve()
        require(source.is_relative_to(package) and sha(source)==p['sha256'],'Promotion changed')
        require(target==REGION or target.is_relative_to(MODEL/'results') or target in [MODEL/'sppr_source.xlsx',INDEX],'Unexpected promotion target')
    original=read_book(RUN/'inputs/pre_adoption/LME_022.xlsx');book=read_book(package/'regional/LME_022.xlsx');manifest=read(package/'model/results/result_manifest.json');mapping=read(MAPPING);run=read(PRIMARY/'run_manifest.json')
    for s in ['Catch','Classic PPR','NPP']:require(book[s]==original[s],'Independent input changed '+s)
    for k in ['selected_model_id','selection_rationale','catch_basis','taxon_detail_year','production_eligible']:require(overview(book)[k]==overview(original)[k],'Setting changed '+k)
    for t,d in original['Diagnostics'].items():
        if t not in ['model_health','EE floor','EE floor groups','Method coverage']:require(book['Diagnostics'][t]==d,'Unrelated diagnostic changed '+t)
    require(overview(book)['calculation_input_sha256']==input_hash(book) and overview(book)['calculation_result_sha256']==result_hash(book),'Stale arithmetic')
    require(manifest['snapshot_sha256']==sha(package/'regional/LME_022.xlsx')==sha(package/'model/results/regional_snapshot.xlsx'),'Snapshot mismatch')
    expected={(k,s,g):v for k in KEYS for s,gg in run['answer']['methods'][k]['scopes'].items() for g,v in gg.items()}
    actual={(r['method'],r['scope'],r['group']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')};require(len(actual)==630 and actual==expected,'Coefficients not exact')
    want={(r['taxon'],g['group_name']):(g['weight'],r['overall_confidence'],r['reason']) for r in mapping['rows'] for g in r['groups']}
    got={(r['taxon'],r['group']):(r['weight'],r['confidence'],r['explanation']) for r in records(book,'PPR','Matching')};require(got==want and len(got)==715,'Mapping changed')
    groups=records(book,'Selected model groups','Groups');require(len(groups)==70,'Wrong group inventory')
    require(coverage._source_matches(package/'model',book,KEYS),'Source coherence failed')
    require(manifest['method_coverage']['arithmetic_code_identity']==coverage._arithmetic_identity(),'Arithmetic implementation changed')
    require(coverage._package_cache_valid(package/'model',package/'regional/LME_022.xlsx',manifest,plan['context'],KEYS),'Three-method retained cache invalid')
    runtime=read(PRIMARY/'constructor.json.gz')['constructor_outcome']['runtime']
    expected_groups=[{'seq':i,'group_type':r['trophic_info'],**r} for i,r in frame(runtime['_groups_df']).items()]
    require(groups==expected_groups,'Runtime Groups values or missingness changed')
    # Independent direct multiplication checks every generated PPR annual cell,
    # including all bases/treatments, missingness, 6-place taxon rounding and ratios.
    taxon={r['taxon']:r for r in mapping['rows']};simple={r['taxon']:r['sppr'] for r in records(original,'Classic PPR','Taxa')}
    catches=records(original,'Catch','Catch');coeff={(t,s,k):round(math.fsum(g['weight']*expected[k,s,g['group_name']] for g in r['groups']),6) for t,r in taxon.items() for k in KEYS for s in ['all','inner','PP']}
    checks=0;max_error=0
    for r in records(book,'PPR','Annual'):
        if r['metric']!='ppr':continue
        eligible=not (r['unidentified']=='simple' and r['scope']!='all')
        require((r['status']=='ok') if eligible else str(r['status']).startswith('unavailable:'),'Eligibility mismatch')
        for y in YEARS:
            vals=[]
            for c in catches:
                if c['catch_basis']!=r['catch_basis']:continue
                v=coeff[c['taxon'],r['scope'],r['method']]
                if c['unidentified'] and r['unidentified']=='zero':v=0
                if c['unidentified'] and r['unidentified']=='simple':v=simple.get(c['taxon'])
                if finite(c[y]) and finite(v):vals.append(c[y]*v)
            want_value=math.fsum(vals) if vals and eligible else None
            if want_value is None:require(r[y] is None,'Missing annual became numeric')
            else:
                err=abs(want_value-r[y]);max_error=max(max_error,err);require(math.isclose(want_value,r[y],rel_tol=1e-13,abs_tol=1e-8),'Annual arithmetic mismatch')
            checks+=1
    annual={(r['model_id'] or '',r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for s in ['PPR','Classic PPR'] for r in records(book,s,'Annual') if r['metric']=='ppr'}
    npp={r['method']:r for r in records(book,'NPP','NPP')};ratio_checks=0
    for r in records(book,'PPR–NPP','Ratios'):
        p=annual[r['model_id'] or '',r['scope'],r['method'],r['catch_basis'],r['unidentified']];n=npp[r['npp_method']]
        for y in YEARS:
            v=100*p[y]/9/n[y] if finite(p[y]) and finite(n[y]) and n[y]>0 else None
            require(r[y] is None if v is None else math.isclose(r[y],v,rel_tol=1e-13,abs_tol=1e-12),'Ratio/missingness mismatch');ratio_checks+=1
    excluded_names={r['group_name'] for r in groups if r['seq'] in EXCLUDED};excluded=[(t,g['group_name'],g['weight']) for t,r in taxon.items() for g in r['groups'] if g['group_name'] in excluded_names and g['weight']>0]
    require(excluded==[('Cetorhinus maximus','BaleenWhales',1.0)],'Excluded mapping support changed')
    catch=next(r for r in catches if r['taxon']=='Cetorhinus maximus' and r['catch_basis']=='catch');positive=[y for y in YEARS if catch[y]>0]
    require(len(positive)==62 and positive[0]==1950 and positive[-1]==2012 and catch[2019]==0,'Historical exclusions differ')
    exclusion_effect={k:{s:{str(y):catch[y]*expected[k,s,'BaleenWhales']/9 for y in YEARS} for s in ['all','inner','PP']} for k in KEYS}
    write(RUN/'qa/historical_display_exclusions.json',{'excluded_ids':EXCLUDED,'allocation_weights_unchanged':True,'taxon':'Cetorhinus maximus','catch_removed_tonnes':{str(y):catch[y] for y in YEARS},'positive_years':len(positive),'sum_catch':math.fsum(catch[y] for y in YEARS),'removed_PPR_tC_exact_group_contributions':exclusion_effect,'rounding_note':'Display group contributions use exact retained group coefficients; regional annual coefficients are rounded to six decimals; no renormalization of retained shares.'})
    require(ratio_checks==37800,'Expected 540 ratio rows / 37800 cells')
    write(RUN/'qa/verification.json',{'passed':True,'counts':plan['counts'],'annual_cells_independently_checked':checks,'ratio_cells_independently_checked':ratio_checks,'max_annual_roundtrip_absolute_error':max_error,'catch_classic_npp_exact':True,'selection_rationale_exact':True,'all_coefficients_and_weights_exact':True,'scientific_solve_performed':False,'new_MC_draws':False,'runtime_stock_reconstruction_blocked':True,'snapshot_exact':True,'historical_exclusion_positive_years':62,'scope':'Retained import and dependent arithmetic, not renewed scientific audit'})
    return plan

def apply(publication,package_path=None):
    from tools.project_core.registry.publication import _ACTIVE,publication_write
    from tools.project_core.calculations.coverage import _write_bytes
    package=Path(package_path or PACKAGE).resolve()
    require(publication in _ACTIVE.get() and publication.root==ROOT,'Active caller publication required')
    lock=ROOT/'.project-write.lock';require(lock.is_file() and lock.read_text().strip()==str(os.getpid()),'Caller writer lock required')
    plan=verify_package(package,check_consumed=False);require(plan['ready_for_apply'],'Preparation incomplete');targets={p['target'] for p in plan['promotions']}
    check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
    if all(fingerprint(ROOT/p['target'])==p['sha256'] for p in plan['promotions']):return {'status':'already_applied','changed_units':['LME_022'],'written_paths':[]}
    check_inputs(plan['consumed_inputs']);written=[]
    for p in plan['promotions']:
        target=ROOT/p['target'];data=(package/p['source']).read_bytes();require(hashlib.sha256(data).hexdigest()==p['sha256'],'Promotion changed before write')
        with publication_write(target,fingerprint=p['sha256']):_write_bytes(target,data,expected_sha256=plan['consumed_inputs'][p['target']])
        written.append(str(target))
    check_inputs({k:v for k,v in plan['consumed_inputs'].items() if k not in targets})
    return {'status':'applied','changed_units':['LME_022'],'written_paths':written,'written_hashes':{str(ROOT/p['target']):p['sha256'] for p in plan['promotions']}}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','verify']);parser.add_argument('--package',type=Path);args=parser.parse_args()
    p=prepare(args.package) if args.command=='prepare' else verify_package(args.package)
    print(json.dumps({'package':p['package'],'promotions':len(p['promotions']),'consumed':len(p['consumed_inputs']),'ready':p['ready_for_apply'],'counts':p['counts']}))
