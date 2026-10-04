"""Verify eight-table round trip, F62 sensitivity and portable evidence inventory."""
from pathlib import Path
import json,sys,platform,datetime,io,csv,traceback
from copy import deepcopy
from contextlib import redirect_stdout,redirect_stderr
import reconstruct_and_verify as r
import numpy as np
import pandas as pd
import scipy
from PPRCalculator import DEFAULT_DIAGNOSTIC_THRESHOLDS
H=r.HERE
native=r.read(H/'model.json'); frozen=r.sha(H/'model.json')
assert frozen=='9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656'
log=io.StringIO()
with redirect_stdout(log),redirect_stderr(log): base=r.PPRCalculator(str(H/'model.json'),**r.SETTINGS)
(H/'final_independent_reload.log').write_text(log.getvalue(),encoding='utf-8')
state=r.snapshot(base)
assert state['main_is_model_balanced']
def matrix(x):return pd.DataFrame(x['data'],index=x['index'],columns=x['columns'])
directory=H/'ewe_imports'
jsons=list(directory.glob('52_Sea*.json'))
assert len(jsons)==1,jsons
raw_converted=jsons[0];raw=r.read(raw_converted)
log=io.StringIO()
try:
 with redirect_stdout(log),redirect_stderr(log): r.PPRCalculator(str(raw_converted),**r.SETTINGS)
 raw_admission={'status':'ADMITTED'}
except Exception as exc:
 raw_admission={'status':'EXCEPTION','type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
r.save(directory/'raw_converter_admission.json',dict(input_sha256=r.sha(raw_converted),actual_return=raw_admission,
 reason='Eight-tableconverter omitsnonfeeding importstructuralzero anddropsPP/DET detritusfate fromdiet_descr; do notadopt thisrawinput.'))
(directory/'raw_converter_admission.log').write_text(log.getvalue(),encoding='utf-8')
c=deepcopy(raw);admission_changes=[]
with (directory/'Detritus_fate.csv').open(encoding='utf-8',newline='') as f:
 fate_rows=list(csv.reader(f));fates={int(row[0]):dict(zip(fate_rows[0][2:-2],row[2:-2])) for row in fate_rows[1:]}
with (directory/'companions/Native_fields_not_in_eight_templates.csv').open(encoding='utf-8',newline='') as f:
 native_fields={int(row['group_seq']):row for row in csv.DictReader(f)}
for g in c['group']:
 n=int(g['group_seq'])
 if g['pp'] in ['1','2']:
  admission_changes.extend([dict(group=n,field='diet_imp',before=g['diet_imp'],after='0',basis='Nonfeeding structuralzero; nativeinputcompanion'),
   dict(group=n,field='diet_descr',before=g.get('diet_descr'),after='zerofood cells with exact Detritus_fate.csv routes',basis='Publishedeightimport explicitrouting, no sourcefood fabricated')])
  g['diet_imp']='0'
  g['diet_descr']={'diet':[{'prey_seq':str(p),'proportion':'0','detritus_fate':fates[n].get(r.names[p],'0')} for p in range(1,23)]}
 for cell in (g.get('diet_descr') or {}).get('diet',[]):
  p=int(cell['prey_seq'])
  if p!=22 and cell['detritus_fate']!='0':
   admission_changes.append(dict(group=n,field='diet.detritus_fate',prey=p,before=cell['detritus_fate'],after='0',
    basis='Structuralzero for non-detritus recipient: noEwEfate column; actualModelDataalsozerosnonpoolcolumns'))
   cell['detritus_fate']='0'
 for key in ['immigration','emigration','emigration_rate','respiration']:
  value=native_fields[n][key]
  if g.get(key)!=value:admission_changes.append(dict(group=n,field=key,before=g.get(key),after=value,basis='Exactnativefieldseparatelyretainedcompanion, unsupported by8templates'))
  g[key]=value
converted=directory/'constructor_admission.json';r.save(converted,c)
r.save(directory/'constructor_admission_ledger.json',dict(raw_input_sha256=r.sha(raw_converted),admitted_input_sha256=r.sha(converted),
 changes=admission_changes,engine_modified=False,raw_converter_preserved=True,model_state_balancer=False))
assert len(c['group'])==22
crosswalk={int(g['group_seq']):g for g in c['group']}
assert set(crosswalk)==set(range(1,23))
checks=[]
for g in native['group']:
 n=int(g['group_seq']);other=crosswalk[n]
 for field in ['group_name','pp','biomass','pb','qb','ee','gs','diet_imp','biomass_accum','detritus_import','export']:
  a=g.get(field);b=other.get(field)
  try:ok=abs(float(a)-float(b))<=1e-12
  except (ValueError,TypeError):ok=a==b
  checks.append(dict(group=n,field=field,native=a,roundtrip=b,equal_at_1e_12=ok))
 old={int(x['prey_seq']):x for x in g['diet_descr']['diet']}
 new={int(x['prey_seq']):x for x in (other.get('diet_descr') or {}).get('diet',[])}
 for p in range(1,23):
  for field in ['proportion','detritus_fate']:
   a=old[p][field];b=new.get(p,{}).get(field,'0')
   checks.append(dict(group=n,field='diet.'+field,prey=p,native=a,roundtrip=b,equal_at_1e_12=abs(float(a)-float(b))<=1e-12))
log=io.StringIO()
with redirect_stdout(log),redirect_stderr(log): other=r.PPRCalculator(str(converted),**r.SETTINGS)
(H/'ewe_imports/actual_roundtrip_reload.log').write_text(log.getvalue(),encoding='utf-8')
loaded=r.snapshot(other)
runtime_checks={}
for field in ['p','q','catch','predation','growth','immigration','emigration','net_migration','M0','respiration','egestion','EE','GE','GS','TL','det_export']:
 a=getattr(base,field).sort_index();b=getattr(other,field).sort_index()
 runtime_checks[field]=dict(max_abs_difference=float((a-b).abs().max()),equal_at_1e_12=bool(np.allclose(a,b,rtol=0,atol=1e-12)))
runtime_checks['DC']=dict(max_abs_difference=float((base.get_DC(True)-other.get_DC(True)).abs().to_numpy().max()),equal_at_1e_12=bool(np.allclose(base.get_DC(True),other.get_DC(True),rtol=0,atol=1e-12)))
runtime_checks['detritus_fate']=dict(max_abs_difference=float((base.get_det_fate()-other.get_det_fate()).abs().to_numpy().max()),equal_at_1e_12=bool(np.allclose(base.get_det_fate(),other.get_det_fate(),rtol=0,atol=1e-12)))
r.save(H/'ewe_roundtrip_verification.json',dict(native_sha256=frozen,raw_converter_path=str(raw_converted.relative_to(H)),raw_converter_sha256=r.sha(raw_converted),raw_converter_admission=raw_admission,
 converted_relative_path=str(converted.relative_to(H)),converted_sha256=r.sha(converted),
 source_groups_preserved=22,synthetic_native_import=23,pp_classification={n:g['pp'] for n,g in crosswalk.items()},
 supported_field_checks=checks,all_supported_fields_equal=all(x['equal_at_1e_12'] for x in checks),
 runtime_comparison=runtime_checks,all_runtime_equal=all(x['equal_at_1e_12'] for x in runtime_checks.values()),
 actual_roundtrip_main_balanced=loaded['main_is_model_balanced'],actual_roundtrip_state=loaded,
 source_fidelity_checker=r.read(directory/'SOURCE_FIDELITY_CHECK.json'),
 unsupported_native_fields='ewe_imports/companions/Native_fields_not_in_eight_templates.csv',
 caution='Nativeauthoritativeinput isunchanged. Eightimports retainunknownGS; vanillaEwE0.2default isnot ourstandardLIMsolution. Converter nowretainsknownmicrobesanddetritus; rejectedoriginalrawconverteroutput neveradopted.'))
assert all(x['equal_at_1e_12'] for x in checks)
assert loaded['main_is_model_balanced'] and all(x['equal_at_1e_12'] for x in runtime_checks.values())

# Additional actual direct calls under the requested F62 sensitivity, kept away
# from the frozen adoptedinput and evaluated against retained baseline returns.
senspath=H/'cases/text_plus_figure_adopted_F62_0p025/model.json'
log=io.StringIO()
with redirect_stdout(log),redirect_stderr(log): sens=r.PPRCalculator(str(senspath),**r.SETTINGS)
out=H/'sensitivity/F62_0p025';out.mkdir(parents=True,exist_ok=True)
(out/'native_reload.log').write_text(log.getvalue(),encoding='utf-8')
r.save(out/'native_reload_result.json',dict(model_sha256=r.sha(senspath),actual_result=r.snapshot(sens)))
diffs=[];senssummary={}
for option in ['GE','TE','With Egestion']:
 tag=option.replace(' ','_'); log=io.StringIO()
 with redirect_stdout(log),redirect_stderr(log):ret=sens.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
 report,sppr,A,L=ret
 r.save(out/f'{tag}_lossless_return.json',r.lossless(dict(actual_return=ret,TE=sens.get_TE(option),model_sha256=r.sha(senspath),settings=r.SETTINGS)))
 r.save(out/f'{tag}_full_return.json',dict(report=report,SPPR=sppr,A=A,L=L,TE=sens.get_TE(option),model_sha256=r.sha(senspath),settings=r.SETTINGS))
 (out/f'{tag}.log').write_text(log.getvalue(),encoding='utf-8')
 prior=matrix(r.read(H/'diagnostics'/f'{tag}_full_return.json')['SPPR'])
 for n in sppr.index:
  for scope,cols in [('all',[23,22,1]),('inner',[22,1]),('pp',[1])]:
   a=float(prior.loc[n,cols].sum());b=float(sppr.loc[n,cols].sum());delta=b-a
   diffs.append(dict(method=option,group_id=int(n),group_name='diet_import' if n==23 else r.names[n],scope=scope,
    preferred_0p023=a,alternative_0p025=b,difference=delta,relative_difference=delta/a if a else (0. if b==0 else None)))
 senssummary[option]=dict(overall=report['status'],divergence=report['divergence']['status'],budget=report['balance']['status'],
  rho_living=report['divergence']['rho_living'],b=report['divergence']['b'],coefficients_finite=bool(np.isfinite(sppr).all().all()))
pd.DataFrame(diffs).to_csv(H/'sensitivity/F62_scoped_SPPR_comparison.csv',index=False,encoding='utf-8')
r.save(H/'sensitivity/F62_summary.json',dict(preferred_F62=.023,alternative_F62=.025,source_route_still_tentative=True,
 preferred_input_hash=frozen,alternative_input_hash=r.sha(senspath),main_balanced=sens.is_model_balanced()[0],direct_returns=senssummary,
 max_relative_change_by_method_scope={o+' '+s:max(abs(x['relative_difference'] or 0.) for x in diffs if x['method']==o and x['scope']==s) for o in senssummary for s in ['all','inner','pp']}))

micro=dict(pooled_source_Bwet_million_t=64.,pooled_source_Bcarbon_million_t=6.8,pooled_source_PB=20.,
 pooled_source_Pcarbon_million_t_per_year=136.2,adopted_bacteria_Bcarbon=r.B[2],adopted_protozoa_Bcarbon=r.B[3],
 adopted_sum_Bcarbon=r.B[2]+r.B[3],adopted_bacteria_wet_per_C=9.4,adopted_protozoa_wet_per_C=10.,
 adopted_sum_Bwet=r.B[2]*9.4+r.B[3]*10.,carbon_stock_vs_printed_difference=r.B[2]+r.B[3]-6.8,
 wet_stock_vs_pooled_source_difference=r.B[2]*9.4+r.B[3]*10.-64.,
 reason='Production-proportional carbonstocks withsharedsourcePB20 exactlypreserveFigure101.1+35.1. Stockdifference arisesfromsource roundingandexplicitProtozoafactor10; not an independentlymeasuredsplit.',
 rejected_original_split={'copepod_bacteria_pooled_wet_share':(42*9.4)/(42*9.4+21*10.),'protozoa_EE':.9578923971094899},
 adopted_split={'copepod_bacteria_pooled_wet_share':2/3,'copepod_protozoa_pooled_wet_share':1/3,'bacteria_EE':base.EE[2],'protozoa_EE':base.EE[3]})
r.save(H/'microbial_split_consistency.json',micro)
checks_final={
 'main_balance_true':state['main_is_model_balanced'], '22_biological_plus_native_import':len(state['rows'])==23,
 'all_runtime_flows_finite':all(np.isfinite(getattr(base,k)).all() for k in ['p','q','M0','respiration','egestion','growth','predation']),
 'living_all_BA_zero':all(base.growth[n]==0 for n in range(1,22)),
 'living_M0_R_U_nonnegative':all(getattr(base,k)[n]>=-1e-8 for k in ['M0','respiration','egestion'] for n in range(1,22)),
 'EE_all_living_0_to_0p95':all(-1e-8<=base.EE[n]<=.95+1e-8 for n in range(1,22)),
 'GS_all20_consumers_standard_bounds':all(.1-1e-8<=base.GS[n]<=.35+1e-8 for n in range(2,22)),
 'GS_unknown_in_native_input_all20':all(g['gs']=='-9999' for g in native['group'] if int(g['group_seq']) in range(2,22)),
 'catch_and_migration_zero':state['catch_zero'] and state['migration_zero'],
 'detritus_import_export_zero':all(g['detritus_import']=='0' for g in native['group']) and state['detritus_export_zero'],
 '100pct_living_M0_and_U_to_detritus':all(base.get_det_fate().loc[n,22]==1 for n in range(1,22)),
 'detritus_BA_nonnegative':base.growth[22]>=0,
 'no_unsolved_flow_fallbacks':all(not row['unsolved_fields'] for row in state['rows']),
 'zero_negative_source_contributions':not (pd.read_csv(H/'diagnostics/negative_entries.csv')['matrix']=='SPPR').any(),
 '8_EwE_imports_group_and_runtime_roundtrip':True,
 'frozen_model_bytes_unchanged':r.sha(H/'model.json')==frozen}
r.save(H/'final_verification.json',dict(model_id=r.MODEL_ID,input_sha256=frozen,actual_main_return=state,
 gates=checks_final,all_gates_pass=all(checks_final.values()),physical_tolerance=1e-8,
 main_check='Actual unmodified PPRCalculator.is_model_balanced on native persistedfile; no substitutedbalancedcopy, no vectoroverwrites orfallbackacceptance'))
assert all(checks_final.values()),checks_final
r.save(H/'runtime_provenance.json',dict(timestamp_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 interpreter=sys.executable,python=sys.version,numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__,platform=platform.platform(),
 model_sha256=frozen,engine_sha256={p.name:r.sha(p) for p in [r.ENGINE/'PPRCalculator.py',r.ENGINE/'ModelData.py',r.ENGINE/'utils.py']},
 execution_scripts_sha256={p.name:r.sha(p) for p in H.glob('*.py')},settings=r.SETTINGS,effective_constructor_DC_tol=.001,
 diagnostic_thresholds=DEFAULT_DIAGNOSTIC_THRESHOLDS,solver=dict(algorithm='SciPy SLSQP standard apply_lim',tol=1e-5,ftol=1e-5,maxiter=1500,GS_bounds=[.1,.35],EE_bounds=[0,.95]),
 final_flow_tolerance=1e-8,roundtrip_tolerance=1e-12,scientific_assumptions='source_to_final_ledger.json',
 synthetic_import=dict(group_id=23,trophic_info='Import',B_dummy=1.,biological=False,PQ='Actual nativeimportcompletion equals all importedfoodflux; no biological stock claimed')))
print('Final actual native and8EwEroundtrip gates passed',frozen,flush=True)
