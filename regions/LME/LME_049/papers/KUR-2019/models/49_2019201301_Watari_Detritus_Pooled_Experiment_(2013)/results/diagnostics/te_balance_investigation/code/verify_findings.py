"""Independent arithmetic checks on exact diagnostic returns; no scientific rerun."""
from pathlib import Path
import json, math, hashlib, sys, os
sys.dont_write_bytecode=True
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
MODEL=ROOT/'regions/LME/LME_049/papers/KUR-2019/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
EV=MODEL/'extracted_tables/evidence'
OUT=Path(__file__).resolve().parent.parent/'outputs'
sys.path.insert(0,str(EV/'diagnostic_code/PPREstimation'))
sys.path.insert(1,str(ROOT/'research/agents/regional_ge_integration_20260928/evidence'))
from runtime_codec import decode
import numpy as np
import pandas as pd
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(OUT/'summary.json')
reconstruction=read(OUT/'reconstruction.json')
reconstruction['initial_unsuccessful_attempt']={'exception':'ValueError: Could not extract year from filename: model','stage':'Archived ModelData filename parsing, before construction','resolution':'Use a temporary byte-identical copy named with the exact model ID; delete that alias after use. Canonical model.json stays unchanged.'}
save('reconstruction.json',reconstruction)
state_path=MODEL/'model_validation/evidence/source_review/diet_reextraction_20261002/reloaded_runtime_state.json'
state=decode(read(state_path))
DC=state['_DC']
bird=s['seabird_runtime']
checks={}
checks['canonical_hash_matches']=sha(MODEL/'model.json')=='ce1c22a1e20e2a5de8a8ac75e6ddb00c3f0db619849354df9f1527277e36d15c'
checks['replayed_reports_equal_saved']=all(v['report_equal_saved'] for v in s['methods'].values())
checks['input_runtime_unchanged']=s['input_state_unchanged']
checks['all_flow_mismatch_is_seabird_feeding']=s['predation_delta_equals_seabird_consumption']
checks['source_seabird_EE_is_zero']=s['seabird_source']['ee']=='0.00'
checks['source_biomass_is_missing']=s['seabird_source']['biomass']=='-9999'
checks['seabird_has_no_predators']=bool((DC[3]==0).all())
checks['seabird_has_no_self_feeding']=DC.loc[3,3]==0
checks['seabird_TE_negative_roundoff']=(-1e-14<bird['TE']<0)
findings={}
for method,v in s['methods'].items():
    key=method.replace(' ','_')
    ret=decode(read(OUT/(key+'_full_return.json')))
    report,S,A,L=ret
    checks[key+'_matrix_axes_unique']=all(m.index.is_unique and m.columns.is_unique for m in (S,A,L))
    checks[key+'_matrix_shape']=S.shape==(40,5) and A.shape==L.shape==(40,40)
    checks[key+'_finite_matrices']=all(bool(np.isfinite(m.to_numpy()).all()) for m in (S,A,L))
    total=S.sum(axis=1)
    gap=v['balance']['outflow']-v['balance']['inflow']
    flow_gap=v['predation_mismatch_weighted_sum']
    if method!='TE':checks[key+'_gap_explained_by_predation']=math.isclose(gap,flow_gap,rel_tol=0,abs_tol=1e-10)
    else:
        independent_bird=(DC.loc[3].reindex(total.index)@total)/bird['TE']
        checks['TE_bird_row_independently_reproduced']=math.isclose(independent_bird,float(total[3]),rel_tol=1e-13)
        checks['TE_gap_equals_seabird_BA_times_SPPR']=math.isclose(gap,bird['BA']*float(total[3]),rel_tol=0,abs_tol=1e-10)
        checks['TE_other_group_exports_equal_PP_input']=math.isclose(float(((state['catch']+state['growth']+state['net_migration'])*total).drop(3).sum()),v['balance']['inflow'],rel_tol=0,abs_tol=1e-10)
    # Reconcile scopes directly from the complete source contribution matrix.
    pp=[36,37,38]
    ppr_all=float((S.mul(state['catch'],axis=0)).sum().sum())
    ppr_pp=float((S[pp].mul(state['catch'],axis=0)).sum().sum())
    checks[key+'_scope_reconciliation']=math.isclose(ppr_all,report['footprint']['ppr_all'],rel_tol=1e-13) and math.isclose(ppr_pp,report['footprint']['ppr_pp_only'],rel_tol=1e-13)
    findings[method]={'inflow':v['balance']['inflow'],'outflow':v['balance']['outflow'],'absolute_gap':gap,'gap_percent':100*v['balance']['rel_gap'],'strict_pass':v['balance']['is_balanced'],'diagnostic_grade':v['status'],'balance_grade':v['balance']['status'],'weighted_missing_predation':flow_gap,'seabird_BA_weighted':v['seabird']['BA_weighted']}
d=read(OUT/'fresh_state_differences.json')
checks['fresh_initialization_no_numeric_differences']=not any(isinstance(x['saved'],(float,int)) or isinstance(x['fresh'],(float,int)) for x in d)
checks['fresh_state_differences_only_taxonomy_encoding']=all(isinstance(x['saved'],str) and isinstance(x['fresh'],str) and x['saved'].replace('ג€“','–')==x['fresh'] for x in d)
negative=read(OUT/'negative_entries.json')
checks['exactly_four_negative_entries_all_TE_seabirds']=len(negative)==4 and all(x['method']=='TE' and x['recipient_id']==3 for x in negative)
protected=read(OUT/'protected_before.json')
changed=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
checks['all_preexisting_regional_files_unchanged']=not changed
checks={k:bool(v) for k,v in checks.items()}
save('findings.json',{'scope':'Historical selected 39-group Watari configuration. No input, code, workbook, selection or review change; no result adoption.', 'causes':{'TE':'Source seabird EE=0 became runtime -4.6629367034256575e-15 during underdetermined optimization. TE=-4.66293666959761e-16 bypasses exact-zero handling and amplifies positive prey requirements into negative coefficients. Seabirds are a terminal consumer, so this need not inflate living spectral radius.','strict_GE_and_egestion':'Archived loader computed predation while seabird Q was missing (treated as zero), solved Q=0.5000000014803441 later, and never refreshed prey predation. Weighted omitted seabird feeding equals both budget gaps. Ordinary group balance uses stale stored predation and therefore passes.','strict_TE':'Seabird BA=-2.4079145675966143e-16 multiplied by total SPPR=-2.0990122553775226e17 gives +50.54242187287362, equal to the entire TE budget excess. The other groups sum to PP input.','MC_interpretation':'No new MC draws. Archived sampler pins nonpositive TE at its deterministic value. Its diverged category includes any FAIL divergence grade, including negative source coefficients; it does not prove spectral radius exceeds one.','secondary_near_zero_TE':'Toothed whales have source EE=0.01 and TE=0.00009803921568627349 (inverse 10200), causing large positive coefficients; this does not explain the four negative seabird entries.','current_engine':'Current apply_lim already refreshes predation, snaps abs(EE)<1e-10 to zero with consistent M0, and refreshes PB/QB. No current-engine scientific run or adoption was performed; these code differences do not establish current-model validity.'},'budget':findings,'verification':checks,'fresh_initialization':{'numeric_differences':0,'taxonomy_encoding_differences':len(d),'full_state_identical':False},'source_limitations_retained':['Seabird source biomass censored; missing biomass and flows completed conditionally.','Detritus pooling/routing assumption and solved BA remain unvalidated source assumptions.','This investigation establishes the implementation causes of the archived symptoms, not scientific approval.'],'protected_files_checked':len(protected),'changed_files':changed})
save('verification.json',{'passed':all(checks.values()),'checks':checks,'failed':[k for k,v in checks.items() if not v]})
print(json.dumps({'checks':len(checks),'passed':all(checks.values()),'failed':[k for k,v in checks.items() if not v],'budget':findings},indent=2))
assert all(checks.values())
# Hash every evidence artifact and referenced source, using paths relative to the index.
paths=[(p,'investigation evidence') for p in OUT.iterdir() if p.is_file() and p.name not in ('evidence_index.json','completeness.json')]
paths += [(p,'reproduction code') for p in Path(__file__).parent.glob('*.py')]
paths += [(MODEL/'model.json','canonical input'),(state_path,'historical audited runtime'),(EV/'diagnostic_settings.json','historical constructor settings')]
paths += [(EV/'diagnostic_code/PPREstimation'/n,'historical executed engine') for n in ('ModelData.py','PPRCalculator.py','utils.py')]
paths += [(ROOT/'tools/scientific_code/PPREstimation/PPRCalculator.py','current engine read-only comparison'),(ROOT/'research/agents/regional_ge_integration_20260928/evidence/runtime_codec.py','runtime decoder')]
items=[{'role':role,'path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':sha(p),'availability':'present'} for p,role in paths]
save('evidence_index.json',{'schema_version':1,'run_id':'2026-11-14_144037_te_balance','region_id':'LME_049','model_id':MODEL.name,'source_identity':sha(MODEL/'model.json'),'computational_input_identity':sha(state_path),'methods':['GE','TE','With Egestion'],'artifacts':items,'unperformed':[{'role':'new Monte Carlo draws','availability':'inapplicable','reason':'Archived sampler code and diagnostics explain rejection; no fresh stochastic run needed.'},{'role':'current engine scientific rerun','availability':'inapplicable','reason':'Investigation targets recorded failures, without adopting changed runtime conventions.'}]})
assert all(sha(OUT/x['path'])==x['sha256'] for x in read(OUT/'evidence_index.json')['artifacts'])
save('completeness.json',{'all_present_artifacts_reopened_and_hash_verified':True,'artifact_count':len(items),'required_missing_roles':[],'arithmetic_checks_passed':all(checks.values()),'adoption_performed':False})
