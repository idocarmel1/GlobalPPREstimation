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
for method in ['GE','TE','With Egestion']:
 key=method.replace(' ','_')
 report,S,A,L=decode(read(OUT/(key+'_full_return.json')))
 checks[key+'_matrix_axes_and_finiteness']=S.shape==(40,5) and A.shape==L.shape==(40,40) and all(m.index.is_unique and m.columns.is_unique and np.isfinite(m.to_numpy()).all() for m in (S,A,L))
 checks[key+'_scope_reconciliation']=math.isclose(float(S.mul(state['catch'],axis=0).sum().sum()),report['footprint']['ppr_all'],rel_tol=1e-12) and math.isclose(float(S[[36,37,38]].mul(state['catch'],axis=0).sum().sum()),report['footprint']['ppr_pp_only'],rel_tol=1e-12)
 checks[key+'_export_budget_decomposition']=abs(summary['results'][method]['additional_budget_audit']['difference'])<1e-9
 checks[key+'_no_negative_contributions']=bool((S.to_numpy()>=0).all())
 after=decode(json.loads(gzip.decompress((OUT/(key+'_runtime_after.json.gz')).read_bytes())))
 for attr in ['p','q','M0','egestion','growth','predation','catch','net_migration','EE','_DC','_det_fate','external_mortality_export','det_export']:
  checks[key+'_unchanged_'+attr]=encode(state[attr])==encode(after[attr])
protected=read(OUT/'protected_before.json')
checks['all_preexisting_regional_files_still_unchanged']=all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in protected.items())
checks={k:bool(v) for k,v in checks.items()}
save('final_verification.json',{'passed':all(checks.values()),'checks':checks,'failed':[k for k,v in checks.items() if not v]})
assert all(checks.values())
roles={
 'settings.json':'settings and provenance','summary.json':'scenario summary',
 'initial_runtime.json.gz':'initial runtime','ee_floor_ledger.json':'EE floor transformation ledger',
 'negative_entries.json':'negative contribution inventory','flow_residuals.csv':'group balance residuals',
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
save('evidence_index.json',{'schema_version':1,'run_id':'2026-11-14_145409_floor_seabird_export','region_id':'LME_049','model_id':MODEL.name,'variant_id':'runtime_ee_floor_0.1_seabird_external_export','source_identity':sha(MODEL/'model.json'),'computational_input_identity':{'canonical_sha256':sha(MODEL/'model.json'),'settings_sha256':sha(OUT/'settings.json'),'runtime_sha256':sha(OUT/'initial_runtime.json.gz')},'methods':['GE','TE','With Egestion'],'required_roles':list(roles.values())+['canonical input','executed code'],'artifacts':artifacts,'reconciliation':checks,'scope':'diagnostic scenario; unchanged canonical inputs; no adoption or Monte Carlo run'})
assert all(sha(OUT/x['path'])==x['sha256'] for x in artifacts)
save('completeness.json',{'all_artifacts_reopened_hash_verified':True,'artifact_count':len(artifacts),'checks_passed':len(checks),'scientific_balance_pass':False,'adopted':False})
print(json.dumps({'checks':len(checks),'passed':all(checks.values()),'artifacts':len(artifacts),'model_files_unchanged':len(protected)}))
