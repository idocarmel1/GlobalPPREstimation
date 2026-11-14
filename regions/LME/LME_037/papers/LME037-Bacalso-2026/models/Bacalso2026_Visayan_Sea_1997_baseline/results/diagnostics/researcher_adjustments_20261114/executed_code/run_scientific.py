"""Authorized LME037 runtime adjustment; stage evidence only, without adoption."""
from pathlib import Path
import copy, gzip, hashlib, importlib.util, json, math, os, platform, sys, traceback, warnings
from datetime import datetime, timezone

sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
MODEL=RUN.parents[2]
ROOT=MODEL.parents[6]
ENGINE=ROOT/'tools/scientific_code/PPREstimation'
OUT=RUN/'outputs/scientific'
OUT.mkdir(parents=True,exist_ok=True)
QA=RUN/'qa'
QA.mkdir(exist_ok=True)
MID='Bacalso2026_Visayan_Sea_1997_baseline'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fsha(path):return sha(Path(path).read_bytes())
def rawjson(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
canonical_before=fsha(MODEL/'model.json')
assert canonical_before=='a361c3dbf6abef5cedb0d0d480492e55907efde57b573278c5a7db2b7dbaf270'
workbook=ROOT/'regions/LME/LME_037/LME_037.xlsx'
workbook_before=fsha(workbook)
protected={str(p.relative_to(ROOT)).replace('\\','/'):fsha(p) for p in [MODEL/'model.json',workbook,*[p for p in (MODEL/'extracted_tables').iterdir() if p.is_file()]]}
code_bytes={n:(ENGINE/n).read_bytes() for n in ['PPRCalculator.py','ModelData.py','utils.py']}
code_hashes={n:sha(v) for n,v in code_bytes.items()}
code_out=OUT/'executed_code'
code_out.mkdir(exist_ok=True)
for name,raw in code_bytes.items():(code_out/name).write_bytes(raw)
sys.path.insert(0,str(ENGINE))
import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator,DEFAULT_DIAGNOSTIC_THRESHOLDS
assert all(fsha(ENGINE/n)==h for n,h in code_hashes.items()),'Engine changed during import'
codec_source=ROOT/'research/agents/regional_ge_integration_20260928/evidence/runtime_codec.py'
spec=importlib.util.spec_from_file_location('review_runtime_codec',codec_source)
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
encode,decode=codec.encode,codec.decode
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,records

ARTIFACTS=[]
def save(name,value,role,typed=False):
    path=OUT/name
    raw=rawjson(encode(value) if typed else value)
    if name.endswith('.gz'):raw=gzip.compress(raw,mtime=0)
    path.write_bytes(raw)
    ARTIFACTS.append({'role':role,'path':name,'sha256':sha(raw),'availability':'present'})
    return {'path':str(path.relative_to(RUN)).replace('\\','/'),'sha256':sha(raw)}
def finite_json(x):
    if isinstance(x,np.generic):x=x.item()
    if isinstance(x,float) and not math.isfinite(x):return None
    if isinstance(x,dict):return {str(k):finite_json(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [finite_json(v) for v in x]
    return x
if (OUT/'configuration.json').exists() and not (QA/'constructor_attempt1.json').exists():
    (QA/'constructor_attempt1.json').write_bytes(rawjson({'outcome':'constructor blocked; GE/TE/With Egestion NOT_RUN','error_type':'ValueError','message':'det_fate contains missing or nonfinite source routing fractions; supply the unknown fractions before calculation.','scientific_solver_called':False,'configuration':json.loads((OUT/'configuration.json').read_text(encoding='utf-8')),'resolution':'Explicitly replay only the authenticated historical single-detritus routing assumption; retain canonical source missingness.'}))
def science_state(c):
    keys=['_groups_df','_DC','_det_fate','p','q','catch','predation','growth','immigration','emigration','net_migration','M0','respiration','egestion','det_export','EE','GE','GS','TL','external_mortality_export','source_EE','source_M0','EE_before_floor','M0_before_floor']
    return {k:getattr(c,k) for k in keys}
flags={'underdetermined':False,'zero_catch':True,'zero_biomass_accum':False,'default_gs':True,
       'normalize_DC':True,'DC_tol':0.0021,'balance_BA_after_DC_normalization':False,
       'refresh_missing_biomass_accum':True,'use_ee_floor':True,'ee_threshold':0.1,'ee_floor':1.0}
method_flags={'det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'det_collapse_mode':'never','thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS}
model_data=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
canonical_names={int(g['group_seq']):g['group_name'] for g in model_data['group']}
import_default_ledger=[{'group_id':int(g['group_seq']),'group_name':g['group_name'],'field':'diet_imp','source':g['diet_imp'],'runtime':0.0,'basis':'Historical audited zero-import assumption retained'} for g in model_data['group']]
assert all(x['source']=='-9999' for x in import_default_ledger)
routing_path=MODEL/'results/diagnostics/routing_completed_by_loader.csv'
routing=pd.read_csv(routing_path,index_col=0)
routing.index=routing.index.astype(int);routing.columns=routing.columns.astype(int)
assert list(routing.index)==list(range(34,0,-1)) and list(routing.columns)==[33]
assert routing.loc[34,33]==0 and (routing.loc[list(range(1,34)),33]==1).all()
config={'unit_id':'LME_037','model_id':MID,'canonical_model_sha256':canonical_before,'constructor':flags,'diagnostics':method_flags,'input_transformations':{'diet_imp_unknown_to_zero_group_ids':list(canonical_names),'single_detritus_routing':{'source_path':'results/diagnostics/routing_completed_by_loader.csv','source_sha256':fsha(routing_path),'historical_state_sha256':'496736db6d7b56078a3e99cdb0b6586a864c6fb39e9c35ca13f5005c85d19c2b','historical_Git_commit':'7cce584ef32f0f7d31e6b5712cdd909eafd3f139','verified_equal_to_historical_state':True,'recipient_detritus_id':33,'source_group_fractions':{str(i):float(routing.loc[i,33]) for i in routing.index}},'source_canonical_unchanged':True},'engine_hashes':code_hashes,'method_keys':['new_GE','new_TE_EEfix','new_WithEgestion'],'execution_scope':'Authorized runtime adjustment and three existing methods only; unadopted staged results','stock_adapter_reconstructible':False,'researcher_exclusion':'Seabirds (1) remains in ecological equations and full diagnostic matrices; requested removal is a report/display exclusion.'}
config['computational_input_identity']=sha(rawjson(config))
save('configuration.json',config,'configuration')
save('input_assumptions.json',import_default_ledger,'input_transformations')
save('audited_single_detritus_routing.json.gz',routing,'routing_initialization',typed=True)

def construct():
    md=ModelData(str(MODEL/'model.json'),model_name='Visayan_Sea_Bacalso_baseline',model_year='1997')
    import_id=next(k for k,v in md.seq2name.items() if v=='diet_import')
    assert import_id==34
    md.DC.loc[:,import_id]=0.0
    md.det_fate=routing.copy()
    print('Constructing current configured runtime',flush=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        c=PPRCalculator.from_modeldata(md,**flags)
    return c,[str(w.message) for w in caught]

calc,constructor_warnings=construct()
assert calc.seq2name=={**canonical_names,34:'diet_import'}
assert calc.ee_floor_info['affected_groups']==[1],calc.ee_floor_info
assert calc.EE[1]==1 and calc.M0[1]==0
assert math.isclose(calc.external_mortality_export[1],0.000784,rel_tol=1e-12,abs_tol=1e-15)
assert all(calc.external_mortality_export[k]==0 for k in calc.external_mortality_export.index if k!=1)
feeders=calc._groups_df.index[calc._groups_df.trophic_info.eq('Regular')]
assert np.allclose(calc._DC.loc[feeders].sum(axis=1),1,rtol=0,atol=1e-12)
nonfeeders=calc._groups_df.index[~calc._groups_df.trophic_info.eq('Regular')]
assert (calc._DC.loc[nonfeeders].sum(axis=1)==0).all()
assert calc.is_model_balanced()[0],'Requested BA closure did not reach strict model balance'
state_before=copy.deepcopy(science_state(calc))
state_digest=sha(rawjson(encode(state_before)))
runtime_ref=save('runtime_before.json.gz',vars(calc),'runtime_before',typed=True)
save('normalization_rows.json.gz',calc.diet_normalization_rows,'normalization_rows',typed=True)
save('normalization_balance_ledger.json.gz',calc.diet_normalization_balance_ledger,'normalization_balance',typed=True)
save('missing_ba_ledger.json.gz',calc.missing_biomass_accum_ledger,'ba_completion',typed=True)
save('mortality_sink_ledger.json.gz',calc.ee_floor_ledger,'mortality_sink',typed=True)
save('mortality_sink_info.json',finite_json(calc.ee_floor_info),'mortality_sink_info')
changed_cells=[]
raw_DC=calc._model.DC
for recipient in calc._DC.index:
    for prey in calc._DC.columns:
        old,new=float(raw_DC.loc[recipient,prey]),float(calc._DC.loc[recipient,prey])
        if old!=new and not (math.isnan(old) and math.isnan(new)):
            changed_cells.append({'consumer_id':int(recipient),'prey_id':int(prey),'old':finite_json(old),'new':finite_json(new),'old_missing':not math.isfinite(old),'new_missing':not math.isfinite(new)})
save('normalized_diet_changed_cells.json',changed_cells,'normalized_diet_cells')

# Reload the serialized complete runtime without invoking a solver; also independently
# rebuild initialization from current canonical bytes and the same explicit settings.
reloaded_attrs=decode(json.loads(gzip.decompress((OUT/'runtime_before.json.gz').read_bytes())))
restored=PPRCalculator.__new__(PPRCalculator);restored.__dict__.update(reloaded_attrs)
assert sha(rawjson(encode(science_state(restored))))==state_digest
independent,independent_warnings=construct()
assert sha(rawjson(encode(science_state(independent))))==state_digest
save('reload_verification.json',{'serialized_runtime_science_exact':True,'fresh_constructor_science_exact':True,'source_reloaded':True,'scientific_state_sha256':state_digest,'method_resolve_repeated':False,'constructor_warnings':constructor_warnings,'independent_constructor_warnings':independent_warnings},'reload_verification')

groups_df=calc.get_groups_df()
group_rows=[]
for seq,row in groups_df.iterrows():
    r={'seq':int(seq),**row.to_dict()};r['group_type']=r['trophic_info']
    group_rows.append(finite_json(r))
save('groups.json',group_rows,'groups')
oldbook=read_book(workbook,sheets=['Selected model groups'])
oldgroups={int(r['seq']):r for r in records(oldbook,'Selected model groups','Groups')}
oldcoeff={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(oldbook,'Selected model groups','Group SPPR')}
assert {k[2] for k in oldcoeff}==set(config['method_keys'])
biological_checks=[]
for r in group_rows:
    if r['seq']>32:continue
    for field in ['biomass','pb','qb','catch','p','q','gs','egestion','respiration','immigration','emigration','net_migration']:
        a,b=r[field],oldgroups[r['seq']][field]
        if not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12):biological_checks.append({'seq':r['seq'],'field':field,'old':b,'new':a})
assert not biological_checks,biological_checks
oldnew_ba=[{'seq':r['seq'],'group':r['group_name'],'source_ba':next((g['biomass_accum'] for g in model_data['group'] if int(g['group_seq'])==r['seq']),None),'old_runtime_ba':oldgroups[r['seq']]['biomass_accum'],'new_runtime_ba':r['biomass_accum']} for r in group_rows]
save('ba_before_after.json',oldnew_ba,'ba_comparison')

methods=[];coeff_rows=[];matrix_inspections=[]
for option,key,stem in [('GE','new_GE','GE'),('TE','new_TE_EEfix','TE'),('With Egestion','new_WithEgestion','With_Egestion')]:
    print('Running',option,flush=True)
    method_calc=copy.deepcopy(restored)
    before=sha(rawjson(encode(science_state(method_calc))))
    started=datetime.now(timezone.utc).isoformat()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            returned=method_calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**method_flags)
        after=sha(rawjson(encode(science_state(method_calc))))
        assert before==after,'Diagnostic changed scientific runtime'
        report,sppr,A,L=returned
        assert list(sppr.index)==list(range(34,0,-1)) and list(sppr.columns)==[34,33,32,31]
        ret_ref=save('full_return_'+stem+'.json.gz',returned,key+'_full_return',typed=True)
        report_ref=save('diagnostic_'+stem+'.json',finite_json(report),key+'_diagnostic')
        scope_ids={'all':[34,33,32,31],'inner':[33,32,31],'PP':[31,32]}
        discrepancies=[]
        for scope,ids in scope_ids.items():
            summed=sppr.loc[:,ids].sum(axis=1,skipna=False)
            for gid,v in summed.items():
                coeff_rows.append({'model_id':MID,'group':calc.seq2name[gid],'scope':scope,'method':key,'sppr':float(v) if math.isfinite(v) else None})
                old=oldcoeff[(calc.seq2name[gid],scope,key)]
                discrepancies.append({'group_id':int(gid),'group':calc.seq2name[gid],'scope':scope,'old':old,'new':float(v),'delta':float(v-old)})
        save('coefficient_comparison_'+stem+'.json',discrepancies,key+'_coefficient_comparison')
        per_matrices=[]
        for label,matrix in [('SPPR',sppr),('A',A),('L',L)]:
            assert matrix.index.is_unique and matrix.columns.is_unique
            negative=[];nulls=[];nan=[];posinf=[];neginf=[]
            for row_id in matrix.index:
                for col_id in matrix.columns:
                    v=matrix.loc[row_id,col_id]
                    record={'row_id':int(row_id),'row_name':calc.seq2name[row_id],'column_id':int(col_id),'column_name':calc.seq2name[col_id]}
                    if v is None:nulls.append(record)
                    elif math.isnan(v):nan.append(record)
                    elif math.isinf(v):(posinf if v>0 else neginf).append(record)
                    elif v<0:negative.append({**record,'value':float(v)})
            per_matrices.append({'matrix':label,'shape':list(matrix.shape),'ordered_rows':[{'id':int(i),'name':calc.seq2name[i]} for i in matrix.index],'ordered_columns':[{'id':int(i),'name':calc.seq2name[i]} for i in matrix.columns],'negative_entries':negative,'null':nulls,'nan':nan,'positive_infinity':posinf,'negative_infinity':neginf,'sign_comparison_tolerance':0,'role':'Recipient group × basal source contribution' if label=='SPPR' else 'Transfer matrix' if label=='A' else 'Equation coefficient matrix; negative diagonals expected'})
        assert not any(per_matrices[0][k] for k in ['negative_entries','null','nan','positive_infinity','negative_infinity'])
        assert report['divergence']['n_negative_sources']==0
        matrix_inspections.append({'method':option,'matrices':per_matrices,'unfished_recipients_included':True,'scope_ids':scope_ids})
        methods.append({'option':option,'method_key':key,'started':started,'completed':datetime.now(timezone.utc).isoformat(),'outcome':'returned','status':report['status'],'diagnostic':finite_json(report),'full_return':ret_ref,'diagnostic_file':report_ref,'scientific_runtime_unchanged':True,'warnings':[str(w.message) for w in caught]})
        print('Completed',option,report['status'],'strict_input',report['model_input']['is_model_balanced'],'strict_global',report['balance']['is_balanced'],flush=True)
    except Exception as error:
        failure={'option':option,'method_key':key,'outcome':'EXCEPTION','type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        save('failure_'+stem+'.json',failure,key+'_failure');methods.append(failure)

save('matrix_inspections.json',matrix_inspections,'matrix_inspections')
save('group_sppr.json',coeff_rows,'group_sppr')
save('runtime_after.json.gz',vars(calc),'runtime_after',typed=True)
assert all(fsha(ENGINE/n)==h for n,h in code_hashes.items()),'Engine source changed during execution'
changed_protected={p:{'before':h,'after':fsha(ROOT/p)} for p,h in protected.items() if fsha(ROOT/p)!=h}
assert not changed_protected,changed_protected
summary={'schema_version':1,'unit_id':'LME_037','model_id':MID,'run_id':RUN.name,'timestamp':datetime.now(timezone.utc).isoformat(),'scientific_execution_performed':True,'adopted':False,'canonical_sha256':canonical_before,'source_workbook_sha256':workbook_before,'computational_input_identity':config['computational_input_identity'],'scientific_runtime_sha256':state_digest,'runtime_file':runtime_ref,'engine_hashes':code_hashes,'runtime_codec_sha256':fsha(codec_source),'configuration':config,'constructor_warnings':constructor_warnings,'source_and_workbook_preserved':True,'engine_bytes_unchanged':True,'living_parameters_preserved':True,'biological_parameter_differences':biological_checks,'methods':methods,'sink':finite_json(calc.ee_floor_info),'source_missing_ba_applied_groups':[int(i) for i in calc.missing_biomass_accum_ledger.index[calc.missing_biomass_accum_ledger.applied]],'normalization_changed_cell_count':len(changed_cells),'runtime_rows':34,'source_groups':33,'coefficient_rows':len(coeff_rows),'groups_path':'outputs/scientific/groups.json','group_sppr_path':'outputs/scientific/group_sppr.json','state_reload_exact':True,'fresh_constructor_exact':True,'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__},'interpretation':['Derived BA is a closure residual, not observed stock change.','Canonical published diets/EE/unknowns remain unchanged; runtime diet rows are normalized.','Only Seabirds mortality is routed to the explicit hypothetical external sink; its egestion remains routed to detritus.','Seabirds is retained in ecological equations and every matrix; researcher removal applies to displayed fishery PPR/group selection.','Statuses below describe this current configured execution; historical diagnostics remain unchanged.']}
summary_path=RUN/'outputs/scientific_summary.json';summary_path.write_bytes(rawjson(summary))
required=['configuration','input_transformations','runtime_before','runtime_after','normalization_rows','ba_completion','mortality_sink','matrix_inspections','reload_verification','group_sppr','groups']+[key+'_full_return' for key in config['method_keys']]
for name in code_bytes:ARTIFACTS.append({'role':'executed_code','path':'executed_code/'+name,'sha256':code_hashes[name],'availability':'present'})
ARTIFACTS.append({'role':'source_model','path':os.path.relpath(MODEL/'model.json',OUT).replace('\\','/'),'sha256':canonical_before,'availability':'present'})
required.extend(['source_model','executed_code'])
index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_037','model_id':MID,'variant_id':'normalized_DC_derived_missing_BA_seabirds_external_M0','source_identity':canonical_before,'computational_input_identity':config['computational_input_identity'],'methods':config['method_keys'],'required_roles':required,'artifacts':ARTIFACTS,'reconciliation':{'source_unchanged':not changed_protected,'only_seabirds_sink':calc.ee_floor_info['affected_groups']==[1],'source_group_identity':calc.seq2name=={**canonical_names,34:'diet_import'},'all_three_returns':all(m['outcome']=='returned' for m in methods),'runtime_reload':True,'fresh_constructor':True,'all_306_coefficients':len(coeff_rows)==306,'engine_unchanged':True}}
(OUT/'evidence_index.json').write_bytes(rawjson(index))
(QA/'scientific_protected_input_checks.json').write_bytes(rawjson({'before':protected,'changed':changed_protected,'engine_hashes':code_hashes}))
print('STAGED',summary_path,flush=True)
