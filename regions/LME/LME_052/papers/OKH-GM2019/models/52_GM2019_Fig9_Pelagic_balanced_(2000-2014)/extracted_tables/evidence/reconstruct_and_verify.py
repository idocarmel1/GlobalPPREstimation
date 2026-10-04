"""Authorized, explicit carbon reconstruction; uses unmodified native engine.

Run from the project root with Miniconda Python. No central records are written.
All source files remain immutable. Mathematical closure is not source validation.
"""
from pathlib import Path
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import hashlib, io, json, math, sys, itertools

HERE = Path(__file__).resolve().parent
CAND = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p/'Project.xlsx').exists())
ENGINE = ROOT/'tools/scientific_code/PPREstimation'
sys.path.insert(0,str(ENGINE))
import numpy as np
import pandas as pd
from PPRCalculator import PPRCalculator
from ModelData import ModelData

MODEL_ID = '52_GM2019_Fig9_Pelagic_balanced_(2000-2014)'
AREA = 1544000.
SETTINGS = dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,
 default_gs=False,weight_flow=1.,weight_guess=1.,normalize_DC=False,
 balance_BA_after_DC_normalization=False)

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(x):
 if isinstance(x,pd.DataFrame):
  return {'index':[clean(v) for v in x.index], 'columns':[clean(v) for v in x.columns], 'data':clean(x.to_numpy().tolist())}
 if isinstance(x,pd.Series): return {'index':[clean(v) for v in x.index], 'data':clean(x.tolist()),'name':clean(x.name)}
 if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [clean(v) for v in x]
 if isinstance(x,(np.integer,np.floating,np.bool_)): x=x.item()
 if isinstance(x,float) and not math.isfinite(x): return None
 return x
def lossless(x):
 if isinstance(x,pd.DataFrame):
  values=x.to_numpy().tolist()
  return {'python_type':'pandas.DataFrame','index':[lossless(v) for v in x.index],
   'index_name':lossless(x.index.name),'columns':[lossless(v) for v in x.columns],
   'columns_name':lossless(x.columns.name),'dtypes':[str(v) for v in x.dtypes], 'data':lossless(values)}
 if isinstance(x,pd.Series):return {'python_type':'pandas.Series','index':[lossless(v) for v in x.index], 'name':lossless(x.name),'dtype':str(x.dtype),'data':lossless(x.tolist())}
 if isinstance(x,np.ndarray):return {'python_type':'numpy.ndarray','dtype':str(x.dtype),'shape':list(x.shape),'data':lossless(x.tolist())}
 if isinstance(x,dict):return {str(k):lossless(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [lossless(v) for v in x]
 if isinstance(x,(np.integer,np.floating,np.bool_)):x=x.item()
 if isinstance(x,float) and not math.isfinite(x):return {'python_type':'float','nonfinite':'NaN' if math.isnan(x) else ('+Infinity' if x>0 else '-Infinity')}
 return x
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(clean(x),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sval(v): return '-9999' if v is None else format(float(v),'.17g')

SRC=CAND/'assumption_variants/researcher_readings_20261003'
SOURCE=read(SRC/'model.json')
CARBON=read(SRC/'carbon_reconstruction.json')
TABLE=read(CAND/'audit/table3_source_readings.json')
FACTORS=read(SRC/'conversion_factors.json')
factor={r['group_id']:float(r['wet_per_carbon']) if r['wet_per_carbon'] is not None else None for r in FACTORS}
factor[3]=10.
table={r['figure_group_id']:r for r in TABLE if r['figure_group_id'] is not None}
names={int(g['group_seq']):g['group_name'] for g in SOURCE['group']}
P={g['n']:float(g['figure_production_carbon_million_t_per_year']) for g in CARBON['groups'] if g['n']!=22}
B={n:float(r['biomass_wet_million_t'])/factor[n] for n,r in table.items()}
B.update({2:P[2]/20.,3:P[3]/20.,22:310./20.})
CORRECTIONS={'F41':.00685,'F42':.0139,'F71':.02,'F52':.0057,'F57':.0024,
 'F53':.00114,'F65':.0057,'F66':.00588,'F70':.0042,'F44':.0114,'F64':.0057,'F75':.011}

def figure_flows(f62=.023,repairs=False):
 z={n:{p:0. for p in range(1,24)} for n in range(2,22)}
 for f in CARBON['flows']:
  v=float(f['adopted_carbon_flow'])
  if f['flow_id']=='F62': v=f62
  if repairs: v=CORRECTIONS.get(f['flow_id'],v)
  z[f['consumer_id']][f['prey_id']]+=v
 return z

def replace_source_diets(z,complete_text=False):
 """All absolute food values are million wet tonnes/year before prey conversion."""
 detailed=[]
 def diet(n,rows):
  z[n]={p:0. for p in range(1,24)}
  for label,prey,wet,f,basis in rows:
   carbon=wet/f
   z[n][prey]+=carbon
   detailed.append(dict(consumer=n,prey=prey,category=label,wet_million_t=wet,
    wet_per_carbon=f,carbon_million_t=carbon,basis=basis,
    status='source quantity with explicit representation/conversion assumption'))
 # The source's unallocated Other is retained in full. A 40/50/10 split is a
 # transparent source-informed assumption, not a recovered measured diet.
 rem=95.8-.283*10.6
 diet(6,[('Copepods',4,56.7,14.,'2019 p153 and dissertation Table4.11'),
  ('Euphausiids',5,.283*10.6,10.6,'Clear Figure F13 nested inside source Other'),
  ('Other: chaetognaths',7,rem*.4,20.,'Assumed40% of residual; qualitative feeding evidence'),
  ('Other: absent larval crustaceans and tunicates',23,rem*.5,13.3,'Assumed50%; primary Table3 Other plankton factor'),
  ('Other: gelatinous food',14,rem*.1,285.2,'Assumed10%; jellyfish primary factor')])
 # Complete residence-integrated source salmon leaf totals. No365day expansion.
 # Fish leaves are assigned to smelt, the only Figure fish prey of this group.
 # Squid uses source stocks (equal0.5millionwet) for50/50 stage allocation.
 diet(8,[('Euphausiids',5,.4719,10.6,'Dissertation Table4.52'),
  ('Amphipods represented as hyperiids',6,.8678,14.5,'Table4.52; taxonomic lump assumption'),
  ('Copepods',4,.0513,14.,'Table4.52 directspecies sums; conflictingTable4.54 rejected'),
  ('Chaetognaths',7,.0605,20.,'Table4.52'),
  ('Pteropods',23,.0768,17.79,'Table4.52 wet; Table7.1 warmseason factor'),
  ('Decapods',23,.0191,13.3,'Table4.52; Other planktonfactor proxy'),
  ('Oikopleura',23,.0612,20.97,'Table4.52; Table7.1 warmseason factor'),
  ('Gelatinous organisms',14,.0448,285.2,'Table4.52; jellyfish lump assumption'),
  ('Squid III',9,.0469*.5,11.9,'Table4.52; equalwetstock stage split'),
  ('Squid IV',16,.0469*.5,11.94,'Table4.52; equalwetstock stage split'),
  ('Fish represented as smelt',11,.0965,8.7,'Table4.52; FigureF36 prey analogue assumption'),
  ('Rounded total-minus-leaf discrepancy',23,.00014,13.3,'1.79694 total minus1.7968 leafsum retained')])
 jelly=read(CAND/'research_20261003/source_feeding_repairs/jellyfish_text_diet/aggregated_source_prey_categories.json')
 rows=[]
 for r in jelly:
  label=r['prey']; wet=float(r['annual_wet_thousand_t'])/1000.
  mapping={'Euphausiids':(5,10.6),'Copepods':(4,14.),'Amphipods':(6,14.5),
   'Chaetognaths':(7,20.),'Pteropods':(23,None),'Mysids':(23,None),
   'Decapod larvae':(23,13.3),'Jellyfish':(14,285.2),'Fish eggs':(23,10.02),
   'Fish larvae':(23,10.02),'Meroplankton':(23,13.3),'Other':(23,13.3)}
  prey,f=mapping[label]
  if f is None: f=wet/float(r['mixed_2019_anchor_carbon_Q_million_tC_per_year'])
  rows.append((label,prey,wet,f,'Dissertation Tables4.15/4.16; primarypreyfactor or declared externalproxy'))
 diet(14,rows)
 if not complete_text: return detailed
 # Other primary prose diets: known fractions retained, missing food imported;
 # the Figure only sets the within-category split, not the reported total.
 for n,total,phy,pooled,source in [(4,2945.,.768,.215,'2019 p153 copepods'),(5,1445.6,.789,.194,'2019 p153 euphausiids')]:
  b=z[n][2]*9.4; proto=z[n][3]*10.; split=(2./3. if n==4 else b/(b+proto))
  diet(n,[('Phytoplankton',1,total*phy,20.,source),
   ('Bacteria part of pooled microheterotrophs',2,total*pooled*split,9.4,source+('; assumed2/3 pooledwet share; Figure2:1carbon prior andEEheadroom' if n==4 else '; Figurewet-relative split')),
   ('Protozoa part of pooled microheterotrophs',3,total*pooled*(1-split),10.,source+('; assumed1/3 pooledwet share; Figure2:1carbon prior andEEheadroom' if n==4 else '; Figurewet-relative split')),
   ('Unallocated source1.7% other food',23,total*(1-phy-pooled),13.3,source+'; explicitOtherplankton import')])
 diet(7,[('Copepods',4,281.4,14.,'2019p153 directannualamount; avoids rounded87.9% conflict'),
  ('Euphausiids',5,.566*10.6,10.6,'Retain clearFigureF16; not source2.2% ambiguous denominator'),
  ('Unallocated other food',23,320.-281.4-.566*10.6,13.3,'2019total320 minusknown food; importedsourceunknown')])
 diet(11,[('Copepods',4,10.29*.407,14.,'2019p155'),('Euphausiids',5,10.29*.461,10.6,'2019p155'),
  ('Hyperiids',6,.0085*14.5,14.5,'RetainFigureF32 inside13.2% remainder'),
  ('Chaetognaths',7,.005*20.,20.,'RetainFigureF33 inside13.2% remainder'),
  ('Unallocated other food',23,10.29*.132-.0085*14.5-.005*20.,13.3,'Explicit remainder; absentprey import')])
 for n,total,zoo_share,source in [(10,36.9,.973,'2019p155 herring'),(13,14.74,.979,'2019p156 capelin'),(12,16.5,.989,'2019p156 smallpollock')]:
  represented=[p for p in range(4,8) if z[n][p]>0]
  knownwet=sum(z[n][p]*factor[p] for p in represented)
  desired=total*zoo_share
  scale=min(1.,desired/knownwet)
  rows=[(names[p],p,z[n][p]*factor[p]*scale,factor[p],source+'; Figurewithin-zooplankton split'+(' scaled0.2% toprinted subtotal' if scale!=1 else '')) for p in represented]
  if desired-knownwet*scale>1e-12: rows.append(('Other zooplankton',23,desired-knownwet*scale,13.3,source+'; preservedunallocated zooplankton'))
  # Retain represented nonplankton cells when they fit the printed remainder.
  foodfish=total*(1-zoo_share); internal=[p for p in range(8,22) if z[n][p]>0]
  knownfish=sum(z[n][p]*factor[p] for p in internal)
  fishscale=min(1.,foodfish/knownfish) if knownfish else 1.
  rows.extend((names[p],p,z[n][p]*factor[p]*fishscale,factor[p],source+'; representednonplankton') for p in internal)
  if foodfish-knownfish*fishscale>1e-12: rows.append(('Absent nekton food',23,foodfish-knownfish*fishscale,10.02,source+'; primaryOthernekton factor proxy'))
  diet(n,rows)
 # Squid aggregate total/category proportions are source; stage split is assumed.
 # III retains plankton-heavy Figure paths; IV receives80% of unknown nekton.
 plankwet=sum(z[n][p]*factor[p] for n in [9,16] for p in [4,5,6,7,14])
 extra_plank=32.4*.64-plankwet
 assert extra_plank>=0
 known_nekton={n:sum(z[n][p]*factor[p] for p in range(8,22) if p!=14) for n in [9,16]}
 unknown_nekton=32.4*.36-sum(known_nekton.values())
 assert unknown_nekton>=0
 for n in [9,16]:
  rows=[]
  for p in range(1,22):
   if z[n][p]>0: rows.append((names[p],p,z[n][p]*factor[p],factor[p],'RetainedFigurepath afterexplicitdecimal scenario'))
  rows.extend([('Absent other plankton',23,extra_plank*(.9 if n==9 else .1),13.3,'2019aggregate64%;90/10 residualstage allocation'),
   ('Absent nekton prey',23,unknown_nekton*(.2 if n==9 else .8),10.02,'2019aggregate36%;20/80 residualstage allocation; IIIplanktivory/IVnektonfeeding prose')])
  diet(n,rows)
 return detailed

def native_model(z,status):
 native=deepcopy(SOURCE)
 native['model_id']=MODEL_ID
 native['model_name']='Sea of Okhotsk pelagic balanced assumption reconstruction'
 native['model_number']='GM2019-Fig9-balanced'
 native['model_year']='2000-2014'
 native['_reconstruction']=dict(model_id=MODEL_ID,currency='tonnes carbon per km2; annual rates',
  status=status,area_km2=AREA,source_preserved=True,source_model='../../researcher_readings_20261003/model.json',
  article_doi='10.26428/1606-9919-2019-198-143-163',period='2000-2014',scope='Whole Sea epipelagic0-200m',
  area_basis='Implied Table3 whole-Sea denominator, not a geographic coverage measurement',
  source_pdf_sha256=CARBON['source_pdf_sha256'],source_model_sha256=sha(SRC/'model.json'),
  variant='adopted_balanced_20261003',unknown_sentinel='-9999',
  source_preservation='Original article/extraction and human accepted Figure variant retained unchanged',
  external_food='Full quantitative source remainder and absent prey categories retained as native diet imports',
  wet_carbon_factor_unknown_ids=[22],Protozoa_wet_per_carbon=10.,Protozoa_factor_assumed=True,
  source_number_corrections='12 low-confidence decimal hypotheses, NOT demonstrated article typographical errors',
  limitations='Mathematical balance does not validate generalized source Figure, stage allocation, proxy factors, missing food, microbial split, or mixed jellyfish period.',
  assumed_microbe_PB=20.,microbe_split='Bacteria101.1/20 andProtozoa35.1/20 milliontC',
  detritus_inventory='Assumed310/20=15.5milliontC; 18.25dayfeeding-inventory turnover, no observedstock',
  catch=0,migration=0,living_BA=0,GS='Unknown, standardLIM .10-.35',detritus_import_export=0,
  source_to_final_ledger='source_to_final_ledger.json',runtime_settings='runtime_settings.json')
 native['_reconstruction']['source_model']='../researcher_readings_20261003/model.json'
 for g in native['group']:
  n=int(g['group_seq'])
  g['biomass']=sval(B[n]*1e6/AREA);g['biomass_habitat_area']=g['biomass']
  g['pb']=sval(P[n]/B[n]) if n!=22 else '-9999'
  q=sum(z[n].values()) if n in z else None
  g['qb']=sval(q/B[n]) if q is not None else '-9999'
  g['ee']='-9999';g['other_mort']='-9999';g['gs']='-9999' if n in z else '0'
  g['respiration']='-9999';g['ge']='-9999'
  g['biomass_accum']='0' if n!=22 else '-9999';g['biomass_accum_rate']='0' if n!=22 else '-9999'
  for key in ['export','immigration','emigration','emigration_rate','detritus_import']: g[key]='0'
  g['diet_imp']=sval(z[n][23]/q) if n in z else '0'
  g['diet_descr']={'diet':[dict(prey_seq=str(p),proportion=sval(z[n][p]/q) if n in z else '0',detritus_fate='1' if p==22 else '0') for p in range(1,23)]}
  g['b_hab_area_input']='true';g['pb_input']='true' if n!=22 else 'false';g['qb_input']='true' if n in z else 'false';g['ee_input']='false';g['ge_input']='false'
 return native

def snapshot(calc):
 balanced,prod,cons=calc.is_model_balanced()
 df=calc.get_groups_df();raw=calc.get_model().groups_data
 rows=[]
 for n in sorted(df.index):
  rows.append(dict(group_id=int(n),group=calc.seq2name[n],trophic_info=df.loc[n,'trophic_info'],
   biomass=df.loc[n,'biomass'],P=calc.p[n],Q=calc.q[n],PB=df.loc[n,'pb'],QB=df.loc[n,'qb'],
   EE=calc.EE[n],GS=calc.GS[n],GE=calc.GE[n],BA=calc.growth[n],D=calc.predation[n],
   M0=calc.M0[n],R=calc.respiration[n],U=calc.egestion[n],catch=calc.catch[n],
   immigration=calc.immigration[n],emigration=calc.emigration[n],net_migration=calc.net_migration[n],
   detritus_export=calc.det_export[n],production_residual=prod[n]-calc.p[n],consumption_residual=cons[n]-calc.q[n],
   unsolved_fields=[k for k in ['p','q','M0','respiration','egestion','biomass_accum','gs','ee'] if pd.isna(df.loc[n,k])]))
 return clean(dict(main_is_model_balanced=bool(balanced),rows=rows,returned_production=prod,returned_consumption=cons,
  raw_constructor_groups=raw,final_groups=df,DC=calc.get_DC(DET_as_PP=True),Z=calc.get_Z(DET_as_PP=True),
  detritus_fate=calc.get_det_fate(),TL=calc.TL,normalization=calc.diet_normalization_rows,
  catch_zero=bool((calc.catch==0).all()),migration_zero=bool((calc.immigration==0).all() and (calc.emigration==0).all()),
  detritus_export_zero=bool((calc.det_export==0).all()),biological_groups=22,runtime_groups=len(df)))

def execute(path):
 log=io.StringIO()
 with redirect_stdout(log),redirect_stderr(log): calc=PPRCalculator(str(path),**SETTINGS)
 (path.parent/'native_reload.log').write_text(log.getvalue(),encoding='utf-8')
 result=snapshot(calc);result.update(exact_input_sha256=sha(path),settings=SETTINGS,
  engine_sha256={p.name:sha(p) for p in [ENGINE/'PPRCalculator.py',ENGINE/'ModelData.py',ENGINE/'utils.py']})
 save(path.parent/'native_reload_result.json',result)
 return calc,result

def main():
 protected=[SRC/'model.json',SRC/'carbon_reconstruction.json',CAND/'model.json',ROOT/'Project.xlsx']
 before={str(p.relative_to(ROOT)):sha(p) for p in protected}
 save(HERE/'runtime_settings.json',SETTINGS)
 outcomes=[]
 for case,text,repair in [('figure_only',False,False),('text_plus_figure_unrepaired',True,False),('reduced_figure_source_repairs',False,True),('text_plus_figure_adopted',True,True)]:
  for f62 in [.023,.025]:
   dest=HERE/'cases'/f'{case}_F62_{str(f62).replace(".","p")}'
   z=figure_flows(f62,repair)
   details=replace_source_diets(z,complete_text=text) if case!='figure_only' else []
   native=native_model(z,case)
   save(dest/'model.json',native);save(dest/'food_component_ledger.json',details)
   calc,result=execute(dest/'model.json')
   violations=[]
   for row in result['rows']:
    n=row['group_id']
    if n<=21:
     for key in ['M0','R','U','BA']:
      if row[key] is None or row[key]<-1e-8:violations.append(dict(group=n,field=key,value=row[key]))
     if row['EE'] is None or not -1e-8<=row['EE']<=.95+1e-8:violations.append(dict(group=n,field='EE',value=row['EE']))
     if n>=2 and (row['GS'] is None or not .1-1e-8<=row['GS']<=.35+1e-8):violations.append(dict(group=n,field='GS',value=row['GS']))
   outcomes.append(dict(case=case,F62=f62,main_balanced=result['main_is_model_balanced'],
    physically_admissible=not violations,physical_violations=violations,
    input_sha256=result['exact_input_sha256'],path=str((dest/'model.json').relative_to(HERE)),
    unsolved_groups=[r['group_id'] for r in result['rows'] if r['unsolved_fields']],
    negative_BA=[r['group_id'] for r in result['rows'] if r['BA']< -1e-10]))
   print(outcomes[-1],flush=True)
   if case=='text_plus_figure_adopted' and f62==.023:
    save(HERE/'model.json',native);save(HERE/'food_component_ledger.json',details);save(HERE/'carbon_food_flows.json',z)
 save(HERE/'case_coverage.json',outcomes)
 calc,result=execute(HERE/'model.json')
 assert result['main_is_model_balanced'], 'Exact adopted native reload failed'
 living=[r for r in result['rows'] if r['group_id']<=21]
 assert all(not r['unsolved_fields'] for r in result['rows'])
 assert all(r['BA']>=-1e-10 and r['M0']>=-1e-10 and r['R']>=-1e-10 and r['U']>=-1e-10 for r in living)
 assert all(-1e-8<=r['EE']<=.95+1e-8 for r in living)
 assert all(.1-1e-8<=r['GS']<=.35+1e-8 for r in living if r['group_id']>=2)
 assert result['catch_zero'] and result['migration_zero'] and result['detritus_export_zero']
 # Persist every cell difference, including structural additions and unchanged
 # source baselines; final runtime values are recorded separately from suppliedGS.
 final=read(HERE/'model.json');changes=[]
 for old,new in zip(SOURCE['group'],final['group']):
  n=int(new['group_seq'])
  for key in sorted(set(old)|set(new)):
   if key=='diet_descr': continue
   if old.get(key)!=new.get(key): changes.append(dict(group=n,group_name=names[n],field=key,before=old.get(key),after=new.get(key),
    basis='Native carbon conversion / explicitly authorized reconstruction; see group_parameters andfood_component_ledger'))
  oldcells={int(c['prey_seq']):c for c in (old.get('diet_descr') or {}).get('diet',[])}
  for cell in new['diet_descr']['diet']:
   p=int(cell['prey_seq']);prev=oldcells.get(p,{})
   for key in ['proportion','detritus_fate']:
    if prev.get(key)!=cell[key]:changes.append(dict(group=n,group_name=names[n],field='diet.'+key,prey=p,before=prev.get(key),after=cell[key],basis='Sourcefood / declareddecimal or allocation assumption / carbonprey conversion'))
 group_parameters=[]
 for r in result['rows']:
  n=r['group_id']
  if n>22: continue
  group_parameters.append(dict(group_id=n,group=names[n],body_wet_per_carbon=factor[n],
   source_table=table.get(n),source_figure_production=P.get(n),adopted_B_million_tC=B[n],
   adopted_P_million_tC=P.get(n),adopted_Q_million_tC=sum(read(HERE/'carbon_food_flows.json').get(str(n),{}).values()),
   final_native_parameters=r,basis='SourceTable3wetstock/preybodyfactor; FigureP preserved; PB derived P/B. Microbes sharePB20, production-proportionalB. Detstock assumption.'))
 ledger=dict(model_id=MODEL_ID,source_model_sha256=sha(SRC/'model.json'),exact_final_sha256=sha(HERE/'model.json'),
  input_cell_changes=changes,group_parameters=group_parameters,
  article_arrow_changes=[dict(flow_id=f['flow_id'],prey=f['prey_id'],consumer=f['consumer_id'],before=float(f['adopted_carbon_flow']),after=CORRECTIONS[f['flow_id']],source_literal=f['source_literal'],routing_status=f['routing_status'],status='Low-confidence scientific decimal hypothesis, NOT proven source error',confidence='Very low',reason='Production-availability closure withzeroBA/catch/migration; verifiedsourceproduction preserved') for f in CARBON['flows'] if f['flow_id'] in CORRECTIONS],
  accepted_unchanged={'F62':.023,'F62_sensitivity':.025,'F67':.05,'F77_prey':15},
  stock_and_rate_policy='Preserve Table3 wetstock/bodyfactor; preserveFigureP exactly; adjustPB for rounded source inconsistency. MicrobePB20 pooledsourceassumption.',
  GS_policy='Unknown in all20consumer JSON rows; solved byactualstandardLIM, notfixed0.2',
  EE_BA_policy='LivingBAzero explicit best-guess sustainable stock; EEderived frompredation/production and bounded/admissibility checked',
  food_policy='Source totals/fractions preserved; unknown foodexplicit imports; no normalization ofpartialdiets',
  detritus_policy='AllM0andU tosolepool; import/exportzero; BAresidual; detstockassumed',
  case_coverage=outcomes,uncertainty='GeneralizedFigure is not authorEcopath input. Decimalhypotheses, absentfood allocation, microbialsplit, mixed2018/2019jellyscope, stageaggregation andbodyfactor proxies preventclaims ofsourcevalidation.')
 save(HERE/'source_to_final_ledger.json',ledger)
 # Retain every direct diagnostic full return, coefficients andmatrix axes.
 summaries={}
 for option in ['GE','TE','With Egestion']:
  tag=option.replace(' ','_');log=io.StringIO()
  try:
   with redirect_stdout(log),redirect_stderr(log): ret=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
   report,sppr,A,L=ret
   save(HERE/'diagnostics'/f'{tag}_lossless_return.json',lossless(dict(actual_return=ret,TE=calc.get_TE(option),model_sha256=sha(HERE/'model.json'),settings=SETTINGS)))
   save(HERE/'diagnostics'/f'{tag}_full_return.json',dict(report=report,SPPR=sppr,A=A,L=L,TE=calc.get_TE(option),model_sha256=sha(HERE/'model.json'),settings=SETTINGS))
   sppr.to_csv(HERE/'diagnostics'/f'{tag}_SPPR.csv',encoding='utf-8')
   summaries[option]=dict(report=report,coefficients_finite=bool(np.isfinite(sppr.to_numpy()).all()))
  except Exception as exc:
   summaries[option]=dict(status='EXCEPTION',exception_type=type(exc).__name__,exception=str(exc))
   save(HERE/'diagnostics'/f'{tag}_full_return.json',summaries[option])
  (HERE/'diagnostics'/f'{tag}.log').write_text(log.getvalue(),encoding='utf-8')
  print('DIAGNOSTIC',option,clean(summaries[option]),flush=True)
 save(HERE/'diagnostics'/'summary.json',summaries)
 save(HERE/'protected_source_hashes.json',dict(before=before,after={str(p.relative_to(ROOT)):sha(p) for p in protected},all_unchanged=all(before[str(p.relative_to(ROOT))]==sha(p) for p in protected)))
 print('FINAL_NATIVE_MODEL_BALANCED',sha(HERE/'model.json'),flush=True)

if __name__=='__main__': main()
