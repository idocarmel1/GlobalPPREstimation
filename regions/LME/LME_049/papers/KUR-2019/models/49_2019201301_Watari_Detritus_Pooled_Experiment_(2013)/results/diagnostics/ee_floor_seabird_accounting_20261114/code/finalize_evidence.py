"""Reopen and reconcile the scenario evidence without rerunning its science."""
from pathlib import Path
import json,hashlib,os,sys,math,gzip
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').exists())
MODEL=ROOT/'regions/LME/LME_049/papers/KUR-2019/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
OUT=HERE.parent/'outputs'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
settings=read(OUT/'settings.json')
snap=HERE/'engine';snap.mkdir(exist_ok=True)
for name,expected in settings['engine_hashes'].items():
 source=ROOT/'tools/scientific_code/PPREstimation'/name
 if not (snap/name).exists():
  assert sha(source)==expected
  (snap/name).write_bytes(source.read_bytes())
 assert sha(snap/name)==expected
sys.path.insert(0,str(snap))
sys.path.insert(1,str(ROOT/'research/agents/regional_ge_integration_20260928/evidence'))
from runtime_codec import decode,encode
from PPRCalculator import PPRCalculator
import numpy as np
state=decode(json.loads(gzip.decompress((OUT/'initial_runtime.json.gz').read_bytes())))
summary=read(OUT/'summary.json');checks=read(OUT/'verification.json')
previous=OUT.parent.parent/'ee_floor_seabird_export_20261114/outputs'
old_state=decode(json.loads(gzip.decompress((previous/'initial_runtime.json.gz').read_bytes())))
old_summary=read(previous/'summary.json')
metadata={};matrix_negatives=[];comparison={'methods':{},'BA_changes':[],
 'interpretation':'Only source-missing living BA is refreshed; final biological flows, source parameters and the earlier scenario coefficients are retained. Old diagnostics remain historical.'}
for attr in ['p','q','M0','egestion','respiration','predation','catch','net_migration','EE','_DC','_det_fate','external_mortality_export','det_export']:
 checks['prior_scenario_unchanged_'+attr]=encode(state[attr])==encode(old_state[attr])
source_ba=state['_model'].groups_data['biomass_accum']
for seq in state['growth'].index:
 before=float(old_state['growth'][seq]);after=float(state['growth'][seq])
 if before!=after:
  comparison['BA_changes'].append({'group_id':int(seq),'name':state['seq2name'][seq],
   'before':before,'after':after,'difference':after-before,
   'source_missing':bool(np.isnan(source_ba.loc[seq]))})
checks['only_source_missing_living_BA_changed']=all(row['source_missing'] and state['_groups_df'].loc[row['group_id'],'trophic_info'] in ['Regular','PP'] for row in comparison['BA_changes'])
known=source_ba[source_ba.notna()].index.intersection(state['growth'].index)
known=[s for s in known if state['_groups_df'].loc[s,'trophic_info'] in ['Regular','PP']]
checks['known_living_BA_preserved']=all(state['growth'][s]==old_state['growth'][s] for s in known)
for method in ['GE','TE','With Egestion']:
 key=method.replace(' ','_')
 report,S,A,L=decode(read(OUT/(key+'_full_return.json')))
 old_report,old_S,_,_=decode(read(previous/(key+'_full_return.json')))
 checks[key+'_coefficients_unchanged_from_prior_scenario']=encode(S)==encode(old_S)
 comparison['methods'][method]={'before_status':old_report['status'],'after_status':report['status'],
  'before_balance':old_report['balance'],'after_balance':report['balance'],
  'coefficients_exactly_unchanged':encode(S)==encode(old_S)}
 metadata[method]={'source_scopes':{'all':list(map(int,S.columns)),
  'inner':[int(s) for s in S.columns if state['_groups_df'].loc[s,'trophic_info']!='Import'],
  'PP':[int(s) for s in S.columns if state['_groups_df'].loc[s,'trophic_info']=='PP']},'matrices':{}}
 for matrix_name,m in [('source_coefficients',S),('A',A),('L',L)]:
  values=m.to_numpy(dtype=float)
  axes=lambda ids:[{'id':int(s),'name':state['seq2name'][s],
   'synthetic':state['_groups_df'].loc[s,'trophic_info']=='Import'} for s in ids]
  metadata[method]['matrices'][matrix_name]={'row_axis':axes(m.index),'column_axis':axes(m.columns),
   'orientation':'recipient group x basal source' if matrix_name=='source_coefficients' else 'recipient equation x group',
   'units':'PP equivalents per unit group production' if matrix_name=='source_coefficients' else 'dimensionless',
   'shape':list(m.shape),'masks':{'null':[], 'NaN':np.argwhere(np.isnan(values)).tolist(),
    'positive_infinity':np.argwhere(np.isposinf(values)).tolist(),'negative_infinity':np.argwhere(np.isneginf(values)).tolist()}}
  for i,j in np.argwhere(values<0):
   matrix_negatives.append({'method':method,'matrix':matrix_name,'recipient_id':int(m.index[i]),
    'recipient_name':state['seq2name'][m.index[i]],'source_id':int(m.columns[j]),
    'source_name':state['seq2name'][m.columns[j]],'value':float(values[i,j]),'comparison_tolerance':0.,
    'interpretation':'Negative contribution' if matrix_name=='source_coefficients' else 'Equation matrix sign; not a negative source contribution'})
 checks[key+'_matrix_axes_and_finiteness']=S.shape==(40,5) and A.shape==L.shape==(40,40) and all(m.index.is_unique and m.columns.is_unique and np.isfinite(m.to_numpy()).all() for m in (S,A,L))
 checks[key+'_scope_reconciliation']=math.isclose(float(S.mul(state['catch'],axis=0).sum().sum()),report['footprint']['ppr_all'],rel_tol=1e-12) and math.isclose(float(S[[36,37,38]].mul(state['catch'],axis=0).sum().sum()),report['footprint']['ppr_pp_only'],rel_tol=1e-12)
 checks[key+'_export_budget_decomposition']=abs(summary['results'][method]['additional_budget_audit']['difference'])<1e-9
 checks[key+'_no_negative_contributions']=bool((S.to_numpy()>=0).all())
 after=decode(json.loads(gzip.decompress((OUT/(key+'_runtime_after.json.gz')).read_bytes())))
 for attr in ['p','q','M0','egestion','growth','predation','catch','net_migration','EE','_DC','_det_fate','external_mortality_export','det_export']:
  checks[key+'_unchanged_'+attr]=encode(state[attr])==encode(after[attr])
save('matrix_metadata_and_masks.json',metadata)
save('all_matrix_negative_entries.json',matrix_negatives)
save('previous_scenario_comparison.json',comparison)
protected=read(OUT/'protected_before.json')
checks['all_preexisting_regional_files_still_unchanged']=all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in protected.items())
checks={k:bool(v) for k,v in checks.items()}
save('final_verification.json',{'passed':all(checks.values()),'checks':checks,'failed':[k for k,v in checks.items() if not v]})
assert all(checks.values())
roles={
 'settings.json':'settings and provenance','summary.json':'scenario summary',
 'initial_runtime.json.gz':'initial runtime','ee_floor_ledger.json':'EE floor transformation ledger',
 'negative_entries.json':'negative contribution inventory','flow_residuals.csv':'group balance residuals',
 'missing_biomass_accum_ledger.json':'missing BA finalization ledger',
 'matrix_metadata_and_masks.json':'matrix axes scopes units and nonfinite masks',
 'all_matrix_negative_entries.json':'all returned matrix negative entries',
 'previous_scenario_comparison.json':'previous scenario comparison',
 'final_verification.json':'reconciliation','protected_before.json':'protected inputs',
}
for method in ['GE','TE','With Egestion']:
 key=method.replace(' ','_')
 roles[key+'_full_return.json']=method+' full diagnostic and matrices'
 roles[key+'_runtime_after.json.gz']=method+' post-diagnostic runtime'
paths=[p for p in OUT.iterdir() if p.is_file() and p.name not in ['evidence_index.json','completeness.json','handoff_check.json']]
paths+=list(HERE.glob('*.py'))+list(snap.glob('*.py'))+[MODEL/'model.json',ROOT/'research/agents/regional_ge_integration_20260928/evidence/runtime_codec.py']
artifacts=[]
for p in paths:
 role=roles.get(p.name,'supporting evidence') if p.parent==OUT else 'canonical input' if p==MODEL/'model.json' else 'executed code'
 artifacts.append({'role':role,'path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p),'availability':'present'})
save('evidence_index.json',{'schema_version':1,'run_id':'2026-11-14_final_flow_accounting','region_id':'LME_049','model_id':MODEL.name,'variant_id':'runtime_ee_floor_0.1_seabird_external_export_final_accounting','source_identity':sha(MODEL/'model.json'),'computational_input_identity':{'canonical_sha256':sha(MODEL/'model.json'),'settings_sha256':sha(OUT/'settings.json'),'runtime_sha256':sha(OUT/'initial_runtime.json.gz')},'methods':['GE','TE','With Egestion'],'required_roles':list(roles.values())+['canonical input','executed code'],'artifacts':artifacts,'reconciliation':checks,'scope':'diagnostic scenario; unchanged canonical inputs; no adoption or Monte Carlo run in this package'})
assert all(sha(OUT/x['path'])==x['sha256'] for x in artifacts)
save('completeness.json',{'all_artifacts_reopened_hash_verified':True,'artifact_count':len(artifacts),'checks_passed':len(checks),'scientific_balance_pass':all(r['balance']['is_balanced'] for r in summary['results'].values()),'adopted':False})
print(json.dumps({'checks':len(checks),'passed':all(checks.values()),'artifacts':len(artifacts),'model_files_unchanged':len(protected)}))
