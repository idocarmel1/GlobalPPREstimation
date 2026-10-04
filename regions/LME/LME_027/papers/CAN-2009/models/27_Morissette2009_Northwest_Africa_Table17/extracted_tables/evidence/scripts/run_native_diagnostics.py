"""Bounded direct diagnostics of official EcoBase118, retained within the candidate review."""
from pathlib import Path
import sys, json, hashlib, shutil, warnings, math, inspect, platform
import numpy as np
import pandas as pd

C=Path(__file__).resolve().parents[1]; ROOT=C.parents[3]
OUT=C/'diagnostics'; OUT.mkdir(exist_ok=True)
ENGINE=OUT/'engine'; ENGINE.mkdir(exist_ok=True)
for name in ('ModelData.py','PPRCalculator.py','utils.py'):
    shutil.copy2(ROOT/'tools/scientific_code/PPREstimation'/name,ENGINE/name)
sys.path.insert(0,str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator,DEFAULT_DIAGNOSTIC_THRESHOLDS
INPUT=C/'computational_inputs'/'official_EcoBase118.json'; INPUT.parent.mkdir(exist_ok=True)
native=json.loads((C/'evidence/identity/ecobase118_official_native.json').read_text(encoding='utf-8'))
selected=ROOT/'regions/LME_027/models/27_118_Northwest_Africa_(1987)/model.json'
canonical=json.loads(selected.read_text(encoding='utf-8'))
assert native['group_descr']['group']==canonical['group']
INPUT.write_text(json.dumps(native['group_descr'],ensure_ascii=False,indent=2),encoding='utf-8')
SETTINGS=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,
              weight_flow=1.,weight_guess=1.,normalize_DC=True,DC_tol=.001,
              balance_BA_after_DC_normalization=False)
OPTIONS=dict(det_collapse_mode='never',det_open_mode='none',det_theta=1.,det_external_sppr=0.)

def encode(v):
    if isinstance(v,pd.DataFrame):
        a=v.to_numpy(); result={'type':'DataFrame','index':encode(v.index.tolist()),'columns':encode(v.columns.tolist()),
                  'dtypes':[str(x) for x in v.dtypes],'data':encode(a.tolist()),'shape':list(a.shape)}
        if all(pd.api.types.is_numeric_dtype(t) for t in v.dtypes):
            f=a.astype(float)
            result.update(nan_mask=np.isnan(f).tolist(),positive_infinity_mask=np.isposinf(f).tolist(),negative_infinity_mask=np.isneginf(f).tolist())
        return result
    if isinstance(v,pd.Series): return {'type':'Series','index':encode(v.index.tolist()),'name':encode(v.name),'dtype':str(v.dtype),'data':encode(v.tolist())}
    if isinstance(v,np.ndarray): return {'type':'ndarray','shape':list(v.shape),'dtype':str(v.dtype),'data':encode(v.tolist())}
    if isinstance(v,dict): return {str(k):encode(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [encode(x) for x in v]
    if isinstance(v,np.generic):return encode(v.item())
    if isinstance(v,float) and not math.isfinite(v):return {'nonfinite':'nan' if math.isnan(v) else ('+inf' if v>0 else '-inf')}
    if v is None or isinstance(v,(str,int,float,bool)):return v
    raise TypeError(type(v).__name__)
def save(name,v): (OUT/name).write_text(json.dumps(encode(v),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def state(c):return {k:encode(v) for k,v in vars(c).items() if isinstance(v,(pd.DataFrame,pd.Series))}
def load():
    m=ModelData(str(INPUT))
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter('always'); c=PPRCalculator.from_modeldata(m,**SETTINGS)
    return m,c,[str(w.message) for w in notices]
m,c,notices=load(); m2,c2,notices2=load()
before=state(c); assert before==state(c2),'Persisted input reload changed calculator state'
save('loaded_state.json',before)
ledger=[]
for i in m.groups_data.index:
    for field in m.groups_data.columns.intersection(c._groups_df.columns):
        a=encode(m.groups_data.loc[i,field]); b=encode(c._groups_df.loc[i,field])
        if a!=b:ledger.append({'group_seq':int(i),'group_name':c.seq2name[i],'field':field,'source_loaded':a,'runtime':b})
for i in m.DC.index:
    for j in m.DC.columns:
        a=m.DC.loc[i,j]; b=c._DC.loc[i,j]
        if a!=b:ledger.append({'group_seq':int(i),'group_name':c.seq2name[i],'field':'diet:'+str(j),'source_loaded':a,'runtime':b})
save('transformation_ledger.json',ledger)
reports={}; solutions={}; warning_log={}; negatives=[]; summary={}; coefficients=[]
for option in ('GE','TE','With Egestion'):
    with warnings.catch_warnings(record=True) as ww:
        warnings.simplefilter('always')
        try:
            report,sppr,A,L=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**OPTIONS)
            reports[option]=report;solutions[option]={'SPPR':sppr,'A':A,'L':L}
            summary[option]={'status':report['status'],'divergence':report['divergence'],
                             'model_input':report['model_input'],'matrix_shape':list(sppr.shape),
                             'all_finite':bool(np.isfinite(sppr.to_numpy()).all()),'negative_entries':int((sppr<0).to_numpy().sum())}
            for i in sppr.index:
                for j in sppr.columns:
                    if sppr.loc[i,j]<0:negatives.append({'method':option,'source_id':int(j),'source_name':c.seq2name[j],
                         'recipient_id':int(i),'recipient_name':c.seq2name[i],'value':float(sppr.loc[i,j]),'sign_tolerance':0})
            for scope in ('all','inner','PP'):
                cols=[j for j in sppr.columns if scope=='all' or (j not in c.get_Import_seq() and (scope!='PP' or j not in c.get_DET_seq()))]
                totals=sppr[cols].sum(axis=1,min_count=1)
                for i,v in totals.items(): coefficients.append({'group_seq':int(i),'group_name':c.seq2name[i],'scope':scope,'method':option,'sppr':float(v)})
        except Exception as ex:
            reports[option]={'status':'EXCEPTION','exception':type(ex).__name__,'message':str(ex)}
            summary[option]=reports[option]
        warning_log[option]=[str(w.message) for w in ww]
assert before==state(c),'Diagnostic mutated calculator state'
save('direct_reports.json',reports);save('direct_solutions.json',solutions);save('summary.json',summary)
save('negative_entries.json',negatives);save('group_coefficients.json',coefficients)
save('execution_evidence.json',{'variant':'official_EcoBase118_same_model_source_audited','input':'../computational_inputs/official_EcoBase118.json',
     'input_sha256':sha(INPUT),'native_source_sha256':sha(C/'evidence/identity/ecobase118_official_input.xml'),
     'constructor':SETTINGS,'diagnostic_options':OPTIONS,'effective_diagnostic_signature':str(inspect.signature(c.diagnose_sppr)),
     'thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS,'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
     'engine_hashes':{p.name:sha(p) for p in ENGINE.glob('*.py')},'constructor_warnings':notices,'diagnostic_warnings':warning_log,
     'reload_state_equal':True,'state_unchanged_by_diagnostics':True,'native_groups_equal_selected_canonical':True,
     'BA_normalization_compensation':'Disabled explicitly to preserve the previously accepted constructor behavior; no new biological BA repair.',
     'matrix_semantics':'SPPR rows are recipient native group IDs, columns basal source IDs. Ratios are PP equivalent per biomass, wet-weight; source27 Detritus,28 synthetic Import,24 Benthic producers,26 Phytoplankton.',
     'canonical_source_separation':'Paper-only model.json remains incomplete and is not the computational input. Native supplementation does not establish an independent replacement model.'})
save('source_only_admission.json',{'status':'NOT_RUN','variant':'paper_only_Table17_Table18',
     'reason':'Published Table18 omits consumer25 Zooplankton; paper lacks a complete model-time catch/BA/GS/detritus-routing specification. No silent unknown-to-zero or donor diet completion.',
     'methods':{x:'NOT_RUN' for x in ('GE','TE','With Egestion')},
     'native_companion':'Official EcoBase118 supplies a complete computational representation of the same model; separate fresh native diagnostics retained.'})
(OUT/'DIRECT_DIAGNOSTICS.md').write_text('# Direct diagnostics of the official native companion\n\nThis is EcoBase118, source-audited against Table17, not a distinct replacement. The paper-only reconstruction remains NOT_RUN.\n\n'+
    '\n\n'.join('## '+k+'\n\n```json\n'+json.dumps(encode(v),indent=2,ensure_ascii=False)+'\n```' for k,v in reports.items()),encoding='utf-8')
print(json.dumps({k:{'status':v['status'],'rho':v.get('divergence',{}).get('rho_living'),'b':v.get('divergence',{}).get('b'),'negatives':v.get('negative_entries')} for k,v in summary.items()}))
