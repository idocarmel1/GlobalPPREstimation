"""Bounded source/companion diagnostics; no global methods, Monte Carlo, or adoption.

All constructor behavior is recorded. Incomplete variant diets are never filled.
"""
from pathlib import Path
import argparse,copy,hashlib,inspect,json,math,pickle,platform,shutil,sys,traceback,warnings
from decimal import Decimal
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(HERE/'_deps'))
import numpy as np
import pandas as pd
ENGINE=HERE/'engine';ENGINE.mkdir(exist_ok=True)
for name in ('ModelData.py','PPRCalculator.py','utils.py'):
    src=ROOT/'tools/scientific_code/PPREstimation'/name
    dst=ENGINE/name
    if not dst.exists():shutil.copy2(src,dst)
sys.path.insert(0,str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator,DEFAULT_DIAGNOSTIC_THRESHOLDS

def encode(v):
    if isinstance(v,pd.DataFrame):
        a=v.to_numpy();out={'type':'DataFrame','index':encode(v.index.tolist()),'columns':encode(v.columns.tolist()),'index_name':v.index.name,'column_name':v.columns.name,'dtypes':[str(x) for x in v.dtypes],'data':encode(a.tolist()),'shape':list(a.shape)}
        out['null_mask']=[[x is None for x in row] for row in a.tolist()]
        if all(pd.api.types.is_numeric_dtype(t) for t in v.dtypes):
            f=a.astype(float);out.update(nan_mask=np.isnan(f).tolist(),positive_infinity_mask=np.isposinf(f).tolist(),negative_infinity_mask=np.isneginf(f).tolist())
        return out
    if isinstance(v,pd.Series):return {'type':'Series','index':encode(v.index.tolist()),'name':encode(v.name),'dtype':str(v.dtype),'data':encode(v.tolist())}
    if isinstance(v,np.ndarray):return {'type':'ndarray','shape':list(v.shape),'dtype':str(v.dtype),'data':encode(v.tolist())}
    if isinstance(v,dict):return {str(k):encode(x) for k,x in v.items()}
    if isinstance(v,tuple):return {'type':'tuple','items':[encode(x) for x in v]}
    if isinstance(v,list):return [encode(x) for x in v]
    if isinstance(v,np.generic):return encode(v.item())
    if isinstance(v,float) and not math.isfinite(v):return {'nonfinite':'NaN' if math.isnan(v) else ('+Infinity' if v>0 else '-Infinity')}
    if v is None or isinstance(v,(str,int,float,bool)):return v
    return {'type':type(v).__name__,'repr':repr(v)}

def save(out,name,obj):
    (out/name).write_text(json.dumps(encode(obj),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(c):return {k:copy.deepcopy(v) for k,v in vars(c).items() if k not in ('balanced_model','_model')}
def unknown(v):return v is None or str(v).strip() in ('','-9999','nan')
def diets(g):
    d=(g.get('diet_descr') or {}).get('diet',[])
    return [d] if isinstance(d,dict) else d
def compare_frames(a,b,layer):
    changes=[]
    for i in b.index:
        for field in b.columns:
            x=a.loc[i,field] if i in a.index and field in a.columns else None;y=b.loc[i,field]
            if encode(x)!=encode(y):changes.append({'layer':layer,'group_seq':int(i),'field':str(field),'before':x,'after':y})
    return changes

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--id',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--normalize',action='store_true');ap.add_argument('--derive-missing-pb',action='store_true');ap.add_argument('--source-blanks-zero',action='store_true');ap.add_argument('--block-reason');ap.add_argument('--interpretation',required=True)
    args=ap.parse_args();source=Path(args.input).resolve();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    canonical=json.loads(source.read_text(encoding='utf-8'));data=copy.deepcopy(canonical)
    transforms=[];missing_biology=[];missing_diet=[]
    for g in data['group']:
        seq=int(g['group_seq'])
        for field in ('biomass','pb','qb','ee'):
            if unknown(g.get(field)):missing_biology.append({'group_seq':seq,'group_name':g['group_name'],'field':field})
        for d in diets(g):
            if unknown(d.get('proportion')):missing_diet.append({'consumer_seq':seq,'prey_seq':int(d['prey_seq'])})
            if args.source_blanks_zero and unknown(d.get('proportion')) and (seq,int(d['prey_seq'])) in ((14,36),(15,36),(2,39),(15,39)):
                transforms.append({'layer':'explicit_runtime_input','group_seq':seq,'field':'diet:'+str(d['prey_seq']),'before':d['proportion'],'after':'0','interpretation':'Separate source-blank structural-zero convention; no deficit completion. Native689 demonstrates that at least birds/prey39 may be nonzero, so this is unverified.'});d['proportion']='0'
        if args.normalize and unknown(g.get('biomass_accum')) and not unknown(g.get('biomass_accum_rate')) and not unknown(g.get('biomass')):
            value=str(Decimal(g['biomass_accum_rate'])*Decimal(g['biomass']))
            transforms.append({'layer':'explicit_runtime_input','group_seq':seq,'field':'biomass_accum','before':g.get('biomass_accum'),'after':value,'formula':'Published BA rate × model-area biomass','interpretation':'Documented dimensional conversion, preserving known rate and sign; no balance-derived biological accumulation.'});g['biomass_accum']=value
        if args.derive_missing_pb and unknown(g.get('pb')) and str(g['pp'])=='0' and not unknown(g.get('ge')) and not unknown(g.get('qb')):
            value=float(g['ge'])*float(g['qb']);old=g.get('pb');g['pb']=str(value)
            transforms.append({'layer':'explicit_runtime_input','group_seq':seq,'field':'pb','before':old,'after':g['pb'],'formula':'Q/B × published P/Q','operands':{'qb':g['qb'],'pq':g['ge']},'interpretation':'Approximation from rounded source ratios; not a native multistanza reconstruction. Printed nonmissing P/B values preserved.'})
    computational=out/'computational_input.json';save(out,computational.name,data)
    settings=dict(underdetermined=False,zero_catch=False,zero_biomass_accum=False,default_gs=True,weight_flow=1.,weight_guess=1.,normalize_DC=args.normalize,DC_tol=.001,balance_BA_after_DC_normalization=False)
    options=dict(det_collapse_mode='never',det_open_mode='none',det_theta=1.,det_external_sppr=0.)
    evidence={'run_id':'BancArguin_20261003','assessment_id':args.id,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'source_relative_to_run':Path(__import__('os').path.relpath(source,out)).as_posix(),'source_sha256':sha(source),'computational_input_sha256':sha(computational),'constructor':settings,'diagnostic_options':options,'thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS,'diagnostic_signature':str(inspect.signature(PPRCalculator.diagnose_sppr)),'engine_hashes':{p.name:sha(p) for p in ENGINE.glob('*.py')},'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'interpretation':args.interpretation,'production_eligible':False,'missing_biology_before_runtime':missing_biology,'missing_diet_cells':missing_diet,'scopes':{'all':'All basal-source columns','inner':'Excludes synthetic external diet import','PP':'Primary producer columns only; excludes detritus and imported diet'},'matrix_orientation':'Recipient groups in rows, basal sources in columns; ordered native IDs stored on axes','units':'Wet-weight primary-production equivalent per unit consumer wet biomass; divide regional PPR by9 once for tonnes carbon'}
    reports={};solutions={};summary={};coefficients=[];negative=[];notices={};reconcile=[]
    methods=('GE','TE','With Egestion')
    if args.block_reason:
        for option in methods:reports[option]={'status':'NOT_RUN','reason':args.block_reason}
        summary=copy.deepcopy(reports);evidence['constructor_admission']='BLOCKED_BEFORE_MISSING_DIET_COERCION'
    else:
        try:
            m=ModelData(str(computational));save(out,'modeldata_loaded_state.json',snapshot(m))
            for g in data['group']:
                seq=int(g['group_seq'])
                for field,loaded in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ge','ge'),('gs','gs'),('ee','ee'),('export','catch'),('biomass_accum','biomass_accum'),('other_mort','M0b'),('tl','tl')]:
                    if loaded not in m.groups_data.columns:continue
                    a=g.get(field);b=m.groups_data.loc[seq,loaded]
                    if unknown(a):same=pd.isna(b)
                    else:
                        try:same=float(a)==b
                        except (TypeError,ValueError):same=a==b
                    if not same:transforms.append({'layer':'computational_input_to_ModelData','group_seq':seq,'field':field,'before':a,'after':b})
                for d in diets(g):
                    if unknown(d.get('proportion')):transforms.append({'layer':'computational_input_to_ModelData','group_seq':seq,'field':'diet:'+str(d['prey_seq']),'before':d.get('proportion'),'after':m.DC.loc[seq,int(d['prey_seq'])],'interpretation':'Loader unknown-to-zero behavior; missing source diet never validated by this conversion.'})
                fate=diets(g)
                for d in fate:
                    prey=int(d['prey_seq'])
                    if prey in m.det_fate.columns and unknown(d.get('detritus_fate')):transforms.append({'layer':'computational_input_to_ModelData','group_seq':seq,'field':'detritus_fate:'+str(prey),'before':d.get('detritus_fate'),'after':m.det_fate.loc[seq,prey],'interpretation':'Loader single-detritus closed-routing convention, not published evidence.'})
            with warnings.catch_warnings(record=True) as ww:
                warnings.simplefilter('always');c=PPRCalculator.from_modeldata(m,**settings)
            notices['constructor']=[str(x.message) for x in ww]
            save(out,'loaded_state_before.json',snapshot(c))
            with (out/'loaded_state_before.pkl').open('wb') as f:pickle.dump(snapshot(c),f,protocol=5)
            transforms+=compare_frames(m.groups_data,c._groups_df,'ModelData_to_calculator_groups')
            transforms+=compare_frames(m.DC,c._DC,'ModelData_to_calculator_diet')
            save(out,'modeldata_diet.json',m.DC);save(out,'runtime_diet.json',c._DC)
            sums=[]
            for seq in m.groups_data.index[m.groups_data.trophic_info=='Regular']:
                raw=float(m.DC.loc[seq].sum(skipna=False));rt=float(c._DC.loc[seq].sum(skipna=False))
                sums.append({'consumer_seq':int(seq),'consumer_name':c.seq2name[seq],'raw_loaded_sum':raw,'runtime_sum':rt,'factor':rt/raw if raw else None})
            save(out,'diet_normalization_sums.json',sums)
            # Expose vector-only defaults separately from DataFrame transformations.
            aliases={'p':'p','q':'q','catch':'catch','growth':'biomass_accum','GE':'ge','EE':'ee','GS':'gs','M0':'M0','predation':'predation','respiration':'respiration'}
            for attr,field in aliases.items():
                for seq in c._groups_df.index:
                    a=c._groups_df.loc[seq,field];b=getattr(c,attr).loc[seq]
                    if encode(a)!=encode(b):transforms.append({'layer':'calculator_table_to_vector','group_seq':int(seq),'field':attr,'before':a,'after':b})
            m2=ModelData(str(computational))
            with warnings.catch_warnings():
                warnings.simplefilter('ignore');c2=PPRCalculator.from_modeldata(m2,**settings)
            evidence['persisted_reload_state_equal']=encode(snapshot(c))==encode(snapshot(c2))
            assert evidence['persisted_reload_state_equal'],'Reload differs'
            before=encode(snapshot(c))
            for option in methods:
                with warnings.catch_warnings(record=True) as ww:
                    warnings.simplefilter('always')
                    try:
                        result=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**options)
                        with (out/(option.replace(' ','_')+'_return.pkl')).open('wb') as f:pickle.dump(result,f,protocol=5)
                        report,sppr,A,L=result;reports[option]=report;solutions[option]={'SPPR':sppr,'A':A,'L':L}
                        summary[option]={'status':report.get('status'),'divergence':report.get('divergence'),'model_input':report.get('model_input'),'matrix_available':isinstance(sppr,pd.DataFrame)}
                        if isinstance(sppr,pd.DataFrame):
                            assert sppr.index.is_unique and sppr.columns.is_unique
                            summary[option].update(shape=list(sppr.shape),all_finite=bool(np.isfinite(sppr.to_numpy()).all()),negative_entries=int((sppr<0).to_numpy().sum()))
                            for i in sppr.index:
                                for j in sppr.columns:
                                    if sppr.loc[i,j]<0:negative.append({'method':option,'source_id':int(j),'source_name':c.seq2name[j],'recipient_id':int(i),'recipient_name':c.seq2name[i],'value':float(sppr.loc[i,j]),'sign_tolerance':0})
                            for scope in ('all','inner','PP'):
                                cols=[j for j in sppr.columns if scope=='all' or (j not in c.get_Import_seq() and (scope!='PP' or j not in c.get_DET_seq()))]
                                totals=sppr[cols].sum(axis=1,skipna=False)
                                for i,v in totals.items():coefficients.append({'assessment_id':args.id,'group_seq':int(i),'group_name':c.seq2name[i],'scope':scope,'method':option,'sppr':float(v),'diagnostic_status':report.get('status'),'production_eligible':False})
                                direct=sppr[cols].to_numpy().sum(axis=1)
                                reconcile.append({'method':option,'scope':scope,'axis_unique':True,'scope_source_ids':[int(x) for x in cols],'sum_equal':bool(np.allclose(direct,totals.to_numpy(),rtol=1e-12,atol=1e-12,equal_nan=True))})
                    except Exception as ex:
                        reports[option]={'status':'EXCEPTION','exception':type(ex).__name__,'message':str(ex),'traceback':traceback.format_exc()};summary[option]=reports[option]
                notices[option]=[str(x.message) for x in ww]
            after=encode(snapshot(c))
            evidence['diagnostics_state_unchanged']=before==after
            changed_keys=[k for k in sorted(set(before)|set(after)) if before.get(k)!=after.get(k)]
            evidence['diagnostics_state_changed_attributes']=changed_keys
            evidence['scientific_state_unchanged']=all(k=='detritus_resolution_info' for k in changed_keys)
            save(out,'diagnostic_state_mutations.json',[{'attribute':k,'before':before.get(k),'after':after.get(k),'interpretation':'Diagnostic resolution metadata cache; no scientific vector/matrix change.' if k=='detritus_resolution_info' else 'Scientific state mutation requiring review.'} for k in changed_keys])
            assert evidence['scientific_state_unchanged'],'Diagnostic mutated scientific state'
            # Preserve every loaded biological/flow field as a directly inspectable table.
            c._groups_df.to_csv(out/'loaded_group_flows.csv',encoding='utf-8-sig',index=True)
            save(out,'loaded_state_after.json',snapshot(c))
            evidence['constructor_admission']='CONSTRUCTED'
        except Exception as ex:
            evidence['constructor_admission']='CONSTRUCTOR_EXCEPTION';evidence['exception']={'type':type(ex).__name__,'message':str(ex),'traceback':traceback.format_exc()}
            for option in methods:reports[option]={'status':'NOT_RUN','reason':'Constructor exception','exception':evidence['exception']}
            summary=copy.deepcopy(reports)
    evidence['warnings']=notices
    save(out,'direct_reports.json',reports);save(out,'direct_solutions.json',solutions);save(out,'summary.json',summary)
    save(out,'group_coefficients.json',coefficients);save(out,'negative_entries.json',negative);save(out,'transformation_ledger.json',transforms);save(out,'reconciliation.json',reconcile);save(out,'execution_evidence.json',evidence)
    (out/'DIRECT_DIAGNOSTICS.md').write_text('# Full direct diagnostic returns\n\n'+args.interpretation+'\n\n'+'\n\n'.join('## '+k+'\n\n```json\n'+json.dumps(encode(v),indent=2,ensure_ascii=False)+'\n```' for k,v in reports.items()),encoding='utf-8')
    print(json.dumps({'id':args.id,'admission':evidence['constructor_admission'],'methods':{k:v.get('status') for k,v in summary.items()},'coefficient_rows':len(coefficients)},ensure_ascii=False))

if __name__=='__main__':main()
