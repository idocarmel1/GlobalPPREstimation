"""Adopt the successful auto preflight through the region workbook contract."""
from pathlib import Path
import sys,json,csv,math,copy,shutil,hashlib
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3];REGION=ROOT/'regions/LME_013'
MODEL='Chiaverano2018_detailed_Northern_Humboldt_1995_1998'
METHOD={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,set_result_hash,result_hash
from run_region import prepare_selection
assert BASE==REGION/'models'/MODEL,'Relocate the evidence package first'
assert json.loads((OUT/'preflight_result.json').read_text())['passed']
path=REGION/'LME_013.xlsx';before_hash=sha(path);b=read_book(path);original=copy.deepcopy(b)
snapshot=json.loads((BASE/'mapping/regional_arithmetic_snapshot.json').read_text(encoding='utf-8'))
for sheet,table,key in [('Catch','Catch','catch'),('Classic PPR','Taxa','classic_taxa'),('NPP','NPP','npp')]:
    current=records(b,sheet,table)
    stored=snapshot[key]
    assert [{str(k):v for k,v in r.items()} for r in current]==stored,f'{key} differs from candidate input snapshot'
mapping=json.loads((BASE/'mapping/mapping_review.json').read_text(encoding='utf-8'))
manifest=json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))
model_path=(BASE/'source/computational/model.json').relative_to(REGION).as_posix()
set_setting(b,'selected_model_id',MODEL)
set_setting(b,'model_path',model_path)
rationale='User authorized the audited Northern Humboldt 1995–1998 detailed supplement after isolated auto preflight: all DIRECT GE/TE/With Egestion SPPR entries finite and nonnegative. Actual overall FAIL grades remain; selected for provisional research review, production-ineligible, not researcher-validated.'
set_setting(b,'selection_rationale',rationale)
prepare_selection(b,path)

def read_csv(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def value(x):
    if x=='':return None
    if x in ['True','False']:return x=='True'
    try:
        v=float(x);return v if math.isfinite(v) else None
    except (ValueError,TypeError):return x
runtime=read_csv('runtime_groups.csv')
groups=[{'seq':int(r['group_seq']),**{k:value(v) for k,v in r.items() if k!='group_seq'}} for r in runtime]
b['Selected model groups']['Groups']=table_dict(groups)
group_coeff=read_csv('group_scope_coefficients.csv')
b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],
    [[MODEL,r['group_name'],r['scope'],METHOD[r['method']],float(r['sppr_wet'])] for r in group_coeff])
matching=[];review=[];assumptions=[]
for r in mapping['taxa']:
    for c in r['candidates']:
        matching.append([MODEL,r['taxon'],c['group_name'],c['weight'],r['overall_confidence'],
                         'models/'+MODEL+'/mapping/mapping_review.json; sources: '+', '.join(r.get('sources',[])),r['reason']])
        if r['assumed_allocation']:
            assumptions.append({'model_id':MODEL,'taxon':r['taxon'],'group':c['group_name'],'seq':c['group_id'],'weight':c['weight'],
                'rule':r['allocation_rule'],'confidence':r['allocation_confidence'],'source_landings':c.get('source_landings'),
                'source_catch':c.get('source_catch'),'source_biomass':c.get('source_biomass'),
                'limitations':r['allocation_reason'],'years_applied':'1950–2019','catch_bases_applied':'landings; catch; discards',
                'evidence':(BASE/'mapping/allocation_ledger.json').relative_to(REGION).as_posix(),'eligibility':'assumed composition; not researcher validation'})
    review.append({'model_id':MODEL,**{k:r.get(k) for k in ['taxon','membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','assumed_membership','assumed_allocation','reason']},
                   'evidence':(BASE/'mapping/mapping_review.json').relative_to(REGION).as_posix()})
b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],matching)
b['PPR']['Mapping review']=table_dict(review)
b['PPR']['Allocation assumptions']=table_dict(assumptions)
reports={m:json.loads((OUT/m.replace(' ','_')/'diagnostic_return.json').read_text(encoding='utf-8')) for m in METHOD}
def flatten(x,prefix='',out=None):
    out={} if out is None else out
    for k,v in x.items():
        key=prefix+k
        if isinstance(v,dict):flatten(v,key+'_',out)
        elif isinstance(v,list):out[key]=json.dumps(v,ensure_ascii=False)
        else:out[key]=v
    return out
health=[flatten(reports[m])|{'config_DET_TE_vals':1,'config_fix_EE_0_cases':True,'production_eligible':False} for m in METHOD]
b['Diagnostics']['model_health']=table_dict(health)
b['Diagnostics']['run_notes']=(['topic','note','status'],[
    ['run identity',manifest['run_id']+'; '+(OUT/'run_manifest.json').relative_to(REGION).as_posix(),'actual auto run'],
    ['constructor',json.dumps(manifest['constructor']), 'audited; unchanged'],
    ['solver settings',json.dumps(manifest['method_call']),'det_collapse_mode explicitly auto'],
    ['source limitations','Native fleet discard-return ancestry unsupported; source production conflicts and multi-pool TE EE=0 limitations remain.','FAIL retained'],
    ['researcher decision','No researcher verdict registered. Manual fields preserved.','pending researcher review']])
b['Diagnostics']['Taxon mapping validation']=table_dict(review)
b['Diagnostics']['selection_review']=(['model_id','GE','TE','With Egestion','evidence','note'],[[MODEL,'FAIL','FAIL','FAIL',(OUT/'comparison.md').relative_to(REGION).as_posix(),rationale]])
set_setting(b,'results_model_id',MODEL);set_setting(b,'results_model_sha256',sha(BASE/'source/computational/model.json'))
status={m:f"provisional: DIRECT {m} overall FAIL; input {reports[m]['model_input']['status']}; convergence {reports[m]['divergence']['status']}; SPPR balance {reports[m]['balance']['status']}; det_collapse_mode=auto; production-ineligible; pending researcher review" for m in METHOD}
b['PPR']['Annual']=(ANNUAL_HEADER,[[MODEL,s,METHOD[m],'landings','method','ppr',status[m],*[None]*70] for s in ['all','inner','PP'] for m in METHOD])
recalculate(b,path)
# Integrate full-precision audited arithmetic and its explicit unknown masks.
# The general wrapper rounds taxon coefficients; the source-specific run retains
# the exact allocation products and genuine-zero/unknown contribution policy.
tc=json.loads((OUT/'taxon_scope_coefficients.json').read_text(encoding='utf-8'))
b['PPR']['Taxon SPPR']=(['model_id','taxon','scope','method','sppr'],[[MODEL,r['taxon'],r['scope'],METHOD[r['method']],r['sppr_wet']] for r in tc])
annual=read_csv('candidate_annual_totals.csv');keyed={}
for r in annual:
    key=(r['scope'],METHOD[r['method']],r['catch_basis'],r['unidentified_treatment'])
    if key not in keyed:keyed[key]={metric:[None]*70 for metric in ['ppr','catch','covered_catch']}
    y=int(r['year'])-1950
    keyed[key]['ppr'][y]=None if r['ppr_tC']=='' else float(r['ppr_tC'])*9
    keyed[key]['catch'][y]=value(r['catch_t_wet'])
    keyed[key]['covered_catch'][y]=value(r['covered_catch_t_wet']) if r['contribution_complete']=='True' else None
rows_out=[]
reverse={v:k for k,v in METHOD.items()}
for (s,m,basis,treatment),metrics in keyed.items():
    st='unavailable: simple reference has no source decomposition' if s!='all' and treatment=='simple' else status[reverse[m]]
    for metric,values in metrics.items():rows_out.append([MODEL,s,m,basis,treatment,metric,st,*values])
b['PPR']['Annual']=(ANNUAL_HEADER,rows_out)
b['Classic PPR']=original['Classic PPR']
ratios={}
for r in read_csv('candidate_annual_npp_ratios.csv'):
    key=(MODEL,r['scope'],METHOD[r['method']],r['catch_basis'],r['unidentified_treatment'],r['npp_method'])
    ratios.setdefault(key,[None]*70)[int(r['year'])-1950]=None if r['ppr_npp_ratio']=='' else 100*float(r['ppr_npp_ratio'])
ratio_header=['model_id','scope','method','catch_basis','unidentified','npp_method',*YEARS]
classic_ratios=[r for r in rows(original,'PPR–NPP','Ratios') if not r[0]]
b['PPR–NPP']['Ratios']=(ratio_header,classic_ratios+[[*k,*v] for k,v in ratios.items()])
ref=[r for r in read_csv('candidate_reference_2019_taxa.csv') if int(r['year'])==2019 and r['catch_basis']==overview(original)['catch_basis'] and r['unidentified_treatment']=='method']
b['PPR']['Taxon PPR inspected year']=(['model_id','taxon','scope','method','year','catch_basis','catch_tonnes','sppr','ppr_wet_tonnes'],
    [[MODEL,r['taxon'],r['scope'],METHOD[r['method']],2019,r['catch_basis'],value(r['catch_t_wet']),value(r['coefficient_wet']),value(r['ppr_t_wet_equivalent'])] for r in ref])
for key,val in {
    'selected_paper_ids':'HUM-2018__LME_013','production_eligible':False,
    'source_note':'PROVISIONAL Northern Humboldt detailed 1995–1998 supplement; all 218 reviewed mappings retained. Auto eliminates negative SPPR but all methods retain overall FAIL. Source, spatial and temporal limits remain; no researcher validation.',
    'calculation_status':'selected; auto preflight passed; provisional full DIRECT GE/TE/With Egestion integrated; all overall FAIL; production-ineligible; pending researcher review',
    'det_collapse_mode':'auto','sppr_configuration':json.dumps(manifest['method_call']),
    'sppr_constructor':json.dumps(manifest['constructor']),
    'computational_runtime_evidence':(OUT/'run_manifest.json').relative_to(REGION).as_posix(),
    'computational_state_sha256':manifest['runtime_before_sha256'],
    'computational_input_sha256':manifest['input_sha256'],
    'canonical_source_path':(BASE/'source/resolved_native/model.json').relative_to(REGION).as_posix(),
    'canonical_source_sha256':sha(BASE/'source/resolved_native/model.json'),
    'sppr_engine_hashes':json.dumps(manifest['engine']),
    'validation_document':'Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx',
    'diagnostic_manifest':(OUT/'run_manifest.json').relative_to(REGION).as_posix(),
    'source_note_reference':(OUT/'comparison.md').relative_to(REGION).as_posix(),
    'previous_selection_model_id':overview(original)['selected_model_id'],
    'taxon_coefficient_precision':'full-precision candidate allocation products; no rounding',
    'missing_value_policy':'Unknown remains blank; genuine recorded zero catch gives zero annual contribution; unsupported simple PP/inner stays unavailable'
}.items():set_setting(b,key,val)
set_setting(b,'calculation_input_sha256',input_hash(b));set_result_hash(b)
assert b['Catch']==original['Catch'] and b['Classic PPR']==original['Classic PPR'] and b['NPP']==original['NPP']
validate_region(b,path)
assert sha(path)==before_hash,'Regional workbook changed during integration'
write_book(path,b)
# Retain standard coefficient workbook in the selected model folder so supported
# map source links identify this exact configuration, rather than historical JSON.
w=openpyxl.Workbook();w.remove(w.active)
for name,headers,rr in [('groups_df',*b['Selected model groups']['Groups']),('model_health',*b['Diagnostics']['model_health'])]:
    s=w.create_sheet(name);s.append(headers)
    for row in rr:s.append([clean(v) for v in row])
for scope in ['all','inner','PP']:
    s=w.create_sheet('sppr_'+scope);s.append(['seq','group_name',*METHOD.values()])
    lookup={(r['group_name'],r['method']):float(r['sppr_wet']) for r in group_coeff if r['scope']==scope}
    for g in groups:s.append([g['seq'],g['group_name'],*[lookup[(g['group_name'],m)] for m in METHOD]])
for s in w:s.freeze_panes='C2';s.auto_filter.ref=s.dimensions;s.column_dimensions['B'].width=32
w.save(BASE/'sppr_source.xlsx');w.close()
loaded=read_book(path)
assert digest_tables([loaded['Catch'],loaded['Classic PPR'],loaded['NPP']])==digest_tables([original['Catch'],original['Classic PPR'],original['NPP']])
validate_region(loaded,path)
(OUT/'regional_integration.json').write_text(json.dumps({'selected_model_id':MODEL,'actual_input_path':model_path,'input_sha256':manifest['input_sha256'],'workbook_sha256':sha(path),'independent_inputs_and_classic_preserved':True,'mapping_sha256':sha(BASE/'mapping/mapping_review.json'),'production_eligible':False,'annual_rows':len(rows_out),'taxon_coefficients':len(tc),'config':'auto'},indent=2),encoding='utf-8')
print('Selected model workbook integrated and reopened; independent catch/classic/NPP preserved.',flush=True)
