"""Read-only source comparison; algebraic counterfactuals are not candidate models."""
from pathlib import Path
import json,sys,shutil,hashlib,subprocess
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').exists())
MODELS=ROOT/'regions/LME_050/models'
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False,default=lambda a:a.item() if hasattr(a,'item') else str(a)),encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv)>1:
 year=int(sys.argv[1]);mid=f'50_50{year}_Coastal_Kyoto_Inoue_({year})';src=MODELS/mid;out=HERE/str(year);out.mkdir(exist_ok=True)
 p=out/(mid+'.json');shutil.copy2(src/'model.json',p)
 sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
 from ModelData import ModelData
 from PPRCalculator import PPRCalculator
 m=PPRCalculator.from_modeldata(ModelData(str(p)),underdetermined=True,zero_biomass_accum=False,DC_tol=.001,normalize_DC=True)
 config=dict(TE_option='GE',short=False,flat=False,return_sppr=True,thresholds=None,det_collapse_mode='never',det_open_mode='none',det_theta=1.,det_external_sppr=0.)
 report,s,a,l=m.diagnose_sppr(**config)
 old=json.loads((src/'evidence/diagnose_sppr_GE.json').read_text(encoding='utf8'))['direct_diagnose_sppr_return']
 dump(out/'direct_diagnose_sppr_GE.json',dict(configuration=config,direct_diagnose_sppr_return=report))
 assert json.loads(json.dumps(report))==old,'Direct report changed from original evidence'
 s.to_csv(out/'SPPR.csv');a.to_csv(out/'A.csv');l.to_csv(out/'L.csv');m._groups_df.to_csv(out/'groups.csv')
 det=m.get_DET_seq()[0];basis=s.copy();factor=float(s.loc[det,det]);basis[det]/=factor
 basis.to_csv(out/'unscaled_basal_basis.csv')
 nd=basis.drop(columns=det).sum(axis=1);fr=m._det_fate[det].reindex(m.M0.index).fillna(0);effective=m.M0*fr/m.q[det]
 flow=pd.DataFrame({'name':pd.Series(m.seq2name),'M0':m.M0,'q':m.q,'egestion':m.egestion,'detritus_fraction':fr,'m_eff':effective,'non_det_basis':nd,'det_basis':basis[det]})
 flow['c_contribution']=effective*nd;flow['b_contribution']=effective*basis[det];flow.to_csv(out/'detritus_flow_decomposition.csv')
 b=float(flow.b_contribution.sum());c=float(flow.c_contribution.sum());assert np.isclose(factor,c/(1-b))
 dump(out/'provenance.json',dict(source_sha256=sha(src/'model.json'),source_path=str(src/'model.json'),unchanged_report=True,detritus_factor=factor,detritus_b=b,detritus_c=c,detritus_q=float(m.q[det]),code_sha256={n:sha(ROOT/'tools/scientific_code/PPREstimation'/n) for n in ['PPRCalculator.py','ModelData.py','utils.py']}))
else:
 for year in [1985,2013]:
  r=subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).resolve()),str(year)],capture_output=True,text=True,encoding='utf8',timeout=180)
  (HERE/f'run_{year}.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf8');assert r.returncode==0,r.stderr
 ds={}
 for year in [1985,2013]:
  out=HERE/str(year);g=pd.read_csv(out/'groups.csv',index_col=0).sort_index();s=pd.read_csv(out/'SPPR.csv',index_col=0).sort_index();s.columns=s.columns.astype(int)
  basis=pd.read_csv(out/'unscaled_basal_basis.csv',index_col=0).sort_index();basis.columns=basis.columns.astype(int)
  ds[year]=dict(g=g,s=s,basis=basis,prov=json.loads((out/'provenance.json').read_text()),report=json.loads((out/'direct_diagnose_sppr_GE.json').read_text())['direct_diagnose_sppr_return'])
 comp=pd.DataFrame({'name':ds[1985]['g'].group_name})
 for y,d in ds.items():
  for field in ['catch','biomass','pb','qb','ee','gs','biomass_accum','M0','q','p','net_migration']:comp[f'{field}_{y}']=d['g'][field]
  comp[f'GE_{y}']=d['g'].p/d['g'].q
  comp[f'SPPR_all_{y}']=d['s'].sum(axis=1)
  for seq,name in [(39,'PP'),(40,'DET'),(41,'Import')]:
   comp[f'SPPR_{name}_{y}']=d['s'][seq];comp[f'PPR_{name}_{y}']=d['g']['catch']*d['s'][seq]
  comp[f'PPR_all_{y}']=comp[f'catch_{y}']*comp[f'SPPR_all_{y}']
 comp['PPR_difference_1985_minus_2013']=comp.PPR_all_1985-comp.PPR_all_2013
 comp['SPPR_ratio_1985_to_2013']=comp.SPPR_all_1985/comp.SPPR_all_2013
 comp['catch_effect_symmetric']=(comp.catch_1985-comp.catch_2013)*(comp.SPPR_all_1985+comp.SPPR_all_2013)/2
 comp['coefficient_effect_symmetric']=(comp.SPPR_all_1985-comp.SPPR_all_2013)*(comp.catch_1985+comp.catch_2013)/2
 assert np.allclose(comp.PPR_difference_1985_minus_2013,comp.catch_effect_symmetric+comp.coefficient_effect_symmetric)
 comp.to_csv(HERE/'all_groups_comparison.csv');comp.sort_values('PPR_difference_1985_minus_2013',ascending=False).to_csv(HERE/'ranked_ppr_contributions.csv')
 cross={f'catch_{cy}_coefficients_{sy}':float((comp[f'catch_{cy}']*comp[f'SPPR_all_{sy}']).sum()) for cy in ds for sy in ds}
 # Hybrid basal-basis / detritus-multiplier calculations: algebra only, not new models.
 hybrid={}
 for cy in ds:
  for by in ds:
   for fy in ds:
    mat=ds[by]['basis'].copy();mat[40]*=ds[fy]['prov']['detritus_factor']
    hybrid[f'catch_{cy}_basis_{by}_detritus_factor_{fy}']=float((ds[cy]['g']['catch']*mat.sum(axis=1)).sum())
 summary=dict(scope='GE only; algebraic counterfactuals are explanatory diagnostics, not revised or adopted source models',cross_catch_coefficients=cross,hybrid_basal_basis_detritus_multiplier=hybrid,catch_effect_symmetric=float(comp.catch_effect_symmetric.sum()),coefficient_effect_symmetric=float(comp.coefficient_effect_symmetric.sum()),years={str(y):d['prov']|{'catch':float(d['g']['catch'].sum()),'footprint':d['report']['footprint']} for y,d in ds.items()})
 dump(HERE/'COMPARISON.json',summary)
 print(json.dumps(summary,indent=2));print(comp.sort_values('PPR_difference_1985_minus_2013',ascending=False)[['name','catch_1985','catch_2013','SPPR_all_1985','SPPR_all_2013','PPR_all_1985','PPR_all_2013','PPR_difference_1985_minus_2013']].head(14).to_string())
