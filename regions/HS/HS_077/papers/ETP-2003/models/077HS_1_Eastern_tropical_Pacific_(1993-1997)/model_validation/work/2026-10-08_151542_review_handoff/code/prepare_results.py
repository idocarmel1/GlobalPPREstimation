from pathlib import Path
import hashlib,json,pickle,shutil,sys
import pandas as pd
W=Path(__file__).resolve().parents[1];M=W.parents[2];ROOT=next(p for p in M.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
import create_PPRS_excel as cpe
from PPRCalculator import PPRCalculator
from tools.project_core.workbooks.workbooks import read_book,update_book,rows,records,overview
from tools.project_core.calculations.regional import recalculate,set_setting,set_result_hash
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
D=W/'outputs/diagnostics';manifest=json.loads((D/'run_manifest.json').read_text(encoding='utf-8'))
assert manifest['source_input_unchanged'] and sha(M/'model.json')==manifest['input_sha256']
for n,digest in manifest['engine'].items():assert sha(ROOT/'tools/scientific_code/PPREstimation'/n)==digest
with (D/'runtime_before_methods.pkl').open('rb') as f:c=pickle.load(f)
keys={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}
results={};reports={}
for key,option in keys.items():
 with (D/option.replace(' ','_')/'full_return.pkl').open('rb') as f:ret=pickle.load(f)
 reports[option]=ret[0];results[key]=ret[1]
 assert ret[1] is not None
health=pd.DataFrame.from_dict({option:PPRCalculator._flatten_diagnostics(report) for option,report in reports.items()},orient='index');health.index.name='TE_option'
tables=cpe.build_sppr_tables(c,results,list(keys))
notes=cpe.build_notes_table(list(keys),{k:'ok' for k in keys})
notes.loc['bounded review refresh']=['Only GE, TE and With Egestion executed. No Monte Carlo or global run. Researcher exclusions affect displayed PPR only.','reviewed provisional']
mt=cpe.ModelTables(M.name,str(M/'model.json'),cpe.build_groups_table(c),tables['pp'],tables['inner'],tables['all'],health,cpe.build_footprint_table(c,results,list(keys)),pd.DataFrame({'status':['NOT_RUN'],'reason':['Monte Carlo outside authorized bounded refresh']},index=pd.Index(['Monte Carlo'],name='method')),notes)
export=Path(cpe.write_tables_excel(mt,str(M.with_suffix('.json')),str(W/'outputs/coefficients')))
coefficient=W/'outputs/sppr_source.xlsx';shutil.copy2(export,coefficient)
regional=ROOT/'regions/HS/HS_077/HS_077.xlsx';regional_sha=sha(regional);book=read_book(regional)
assert overview(book)['selected_model_id']==M.name
manual={(s,t):book[s][t] for s,t in [('Catch','Catch'),('Classic PPR','Taxa'),('PPR','Matching'),('NPP','NPP'),('NPP','Provenance')]}
g=mt.groups.reset_index();book['Selected model groups']['Groups']=(list(g.columns),g.where(pd.notnull(g),None).values.tolist())
group_rows=[]
for scope,table in [('all',tables['all']),('inner',tables['inner']),('PP',tables['pp'])]:
 for seq,r in table.iterrows():
  for key in keys:group_rows.append([M.name,r['group_name'],scope,key,float(r[key])])
book['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],group_rows)
for sheet,table in [('model_health',health),('mc_diagnostics',mt.mc_diagnostics),('run_notes',notes)]:
 frame=table.reset_index();book.setdefault('Diagnostics',{})[sheet]=(list(frame.columns),frame.where(pd.notnull(frame),None).values.tolist())
from tools.project_core.calculations.regional import ANNUAL_HEADER
annual=[]
for scope in ['all','inner','PP']:
 for key,option in keys.items():
  report=reports[option];status='provisional: diagnostic '+report['status']
  if not report['balance'].get('is_balanced'):status+='; strict SPPR balance check failed'
  annual.append([M.name,scope,key,'landings','method','ppr',status,*[None]*70])
book['PPR']['Annual']=(ANNUAL_HEADER,annual)
set_setting(book,'results_model_id',M.name);set_setting(book,'results_model_sha256',manifest['input_sha256'])
set_setting(book,'production_eligible',False)
for field,value in {'det_collapse_mode':reports['GE']['config'].get('det_collapse_mode','auto'),'sppr_configuration':json.dumps({k:r['config'] for k,r in reports.items()},sort_keys=True),'sppr_constructor':json.dumps(manifest['constructor'],sort_keys=True),'computational_input_sha256':manifest['input_sha256'],'canonical_source_sha256':manifest['input_sha256'],'sppr_engine_hashes':json.dumps(manifest['engine'],sort_keys=True),'diagnostic_manifest':(D/'run_manifest.json').relative_to(ROOT).as_posix(),'missing_value_policy':'Reviewed notebook: LIM estimates missing EE/flows; zero_catch=True; zero_biomass_accum=False; default_gs=True; source detritus convention retained'}.items():set_setting(book,field,value)
set_setting(book,'selection_rationale','Selected pilot model; researcher adopted five source diet-table corrections and validated on 08/10/2026. Existing full regional taxon mapping retained.')
recalculate(book,regional)
set_setting(book,'calculation_status','provisional: corrected source and reviewed LIM settings refreshed; GE/TE/With Egestion diagnostic WARN retained; TE strict SPPR balance fails; existing regional mapping retained; historical sensitivity bounds invalidated')
set_result_hash(book)
for (s,t),v in manual.items():assert book[s][t]==v,(s,t)
stage=W/'outputs/regional/HS_077.xlsx';stage.parent.mkdir(exist_ok=True);shutil.copy2(regional,stage);update_book(stage,book)
check=read_book(stage)
for (s,t),v in manual.items():assert check[s][t]==v,(s,t)
assert sha(regional)==regional_sha
assert overview(check)['results_model_sha256']==sha(M/'model.json')
assert len(rows(check,'Selected model groups','Group SPPR'))==len(c._groups_df)*9
assert all(r['production_eligible'] is False for r in [overview(check)])
evidence={'regional_before_sha256':regional_sha,'regional_staged_sha256':sha(stage),'canonical_model_sha256':sha(M/'model.json'),'coefficient_source_sha256':sha(coefficient),'manual_tables_preserved':[list(k) for k in manual],'methods':{k:{'status':r['status'],'strict_sppr_balance':r['balance'].get('is_balanced')} for k,r in reports.items()},'calculation_input_sha256':overview(check)['calculation_input_sha256'],'calculation_result_sha256':overview(check)['calculation_result_sha256'],'source_model_unchanged':True,'display_exclusions_not_applied_to_saved_science':True}
(W/'qa/prepared_results.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8');print(json.dumps(evidence,indent=2))
