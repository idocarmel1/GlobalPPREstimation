from __future__ import annotations
import sys, os, json, hashlib, platform, time, traceback, warnings, pickle, subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
ENGINE=ROOT/'tools/scientific_code/PPREstimation'
MODEL=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
OLD=MODEL.parent/'sppr_source.xlsx'
OPTIONS=['GE','TE','With Egestion']
CONSTRUCTOR={'underdetermined':True,'zero_catch':True,'zero_biomass_accum':False,'default_gs':True,
             'weight_flow':1.0,'weight_guess':1.0,'normalize_DC':True,'DC_tol':0.001}
METHOD={'short':False,'flat':False,'return_sppr':True,'det_collapse_mode':'never','det_open_mode':'none',
        'det_theta':1.0,'det_external_sppr':0.0,'DET_TE_vals':1.0,'fix_EE_0_cases':True}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run_worker(option):
    import numpy as np, pandas as pd, scipy, sympy, igraph, openpyxl
    from copy import deepcopy
    sys.path.insert(0,str(ENGINE))
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS
    key=option.replace(' ','_');folder=OUT/key;folder.mkdir(exist_ok=True)
    def val(x):
        if x is None: return {'type':'null'}
        if isinstance(x,(bool,np.bool_)):return {'type':'bool','value':bool(x)}
        if isinstance(x,(int,np.integer)):return {'type':'int','value':str(int(x))}
        if isinstance(x,(float,np.floating)):
            f=float(x)
            return {'type':'float','hex':f.hex(),'value':None if not np.isfinite(f) else f,
                    'nan':bool(np.isnan(f)),'positive_infinity':bool(np.isposinf(f)),
                    'negative_infinity':bool(np.isneginf(f))}
        if isinstance(x,str):return {'type':'str','value':x}
        if isinstance(x,pd.DataFrame):return frame(x)
        if isinstance(x,pd.Series):return {'type':'Series','dtype':str(x.dtype),'index':[val(y) for y in x.index],
                                           'name':val(x.name),'data':[val(y) for y in x.tolist()]}
        if isinstance(x,dict):return {'type':'dict','entries':[[val(k),val(v)] for k,v in x.items()]}
        if isinstance(x,(list,tuple)):return {'type':type(x).__name__,'items':[val(v) for v in x]}
        if isinstance(x,np.ndarray):return {'type':'ndarray','dtype':str(x.dtype),'shape':list(x.shape),'data':val(x.tolist())}
        raise TypeError(f'Unsupported serialization type {type(x)}')
    def plain(x):
        if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [plain(v) for v in x]
        if isinstance(x,np.generic):return plain(x.item())
        if isinstance(x,float) and not np.isfinite(x):return str(x)
        return x
    def frame(df):
        cells=[[val(y) for y in row] for row in df.to_numpy().tolist()]
        return {'type':'DataFrame','shape':list(df.shape),'dtypes':[str(x) for x in df.dtypes],
                'index':[val(y) for y in df.index],'columns':[val(y) for y in df.columns],
                'index_names':[val(y) for y in df.index.names],'column_names':[val(y) for y in df.columns.names],
                'data':cells}
    def dump(name,obj): (folder/name).write_text(json.dumps(plain(obj),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    def state(c):
        return {'groups':c._groups_df.copy(),'DC':c._DC.copy(),'det_fate':c._det_fate.copy(),
                'vectors':{k:deepcopy(getattr(c,k)) for k in ['p','q','catch','predation','growth','immigration',
                  'emigration','net_migration','M0','respiration','egestion','det_export','EE','GE','GS','TL']}}
    start=datetime.now(timezone.utc).isoformat();t=time.perf_counter()
    metadata={'model_id':'34_1_Bay_of_Bengal_(1978)','model_sha256':sha(MODEL),
      'saved_export_sha256':sha(OLD),'started_utc':start,'constructor':CONSTRUCTOR,'method':dict(METHOD,TE_option=option),
      'thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS,'python_executable':sys.executable,'python_version':sys.version,
      'platform':platform.platform(),'package_versions':{m.__name__:m.__version__ for m in [np,pd,scipy,sympy,igraph,openpyxl]},
      'runtime_hashes':{p.name:sha(p) for p in [ENGINE/'ModelData.py',ENGINE/'PPRCalculator.py',ENGINE/'utils.py',
                                                ENGINE/'create_PPRS_excel.py',Path(__file__)]}}
    captured=[]
    try:
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            md=ModelData(str(MODEL));md_state={'groups':md.groups_data.copy(),'DC':md.DC.copy(),'det_fate':md.det_fate.copy()}
            c=PPRCalculator.from_modeldata(md,**CONSTRUCTOR)
            before=state(c)
            metadata['construction_seconds']=time.perf_counter()-t
            dump('loaded_state_before.json',val(before));dump('modeldata_state.json',val(md_state))
            raw=json.loads(MODEL.read_text(encoding='utf-8'));ledger=[]
            for g in raw['group']:
                seq=int(g['group_seq']);row=c._groups_df.loc[seq]
                for original,field in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('gs','gs'),
                                       ('biomass_accum','biomass_accum'),('immigration','immigration'),
                                       ('emigration','emigration'),('export','catch')]:
                    a=float(g[original]);b=float(row[field]);missing=a==-9999
                    if missing or not np.isclose(a,b,rtol=0,atol=1e-14,equal_nan=True):
                        ledger.append({'seq':seq,'name':g['group_name'],'field':field,'canonical':None if missing else a,
                                       'canonical_raw':g[original],'loaded':plain(b),'source_missing':missing,
                                       'reason':'derived production closure BA' if field=='biomass_accum' else
                                          'detritus computational EE forced to1' if seq==49 and field=='ee' else
                                          'basal bookkeeping q=p' if field=='qb' and seq in [42,43,44,45,49] else
                                          'loader zero default for missing migration' if field in ['immigration','emigration'] else 'constructor transformation'})
            ledger.append({'seq':50,'name':'diet_import','field':'biomass','canonical':'inapplicable synthetic import',
                           'loaded':float(c._groups_df.loc[50,'biomass']),'reason':'loader missing-biomass placeholder1 for synthetic group only'})
            ledger.append({'field':'detritus_fate','reason':'canonical routing allzero; loader fills single-pool closed routing for all non-import biological groups',
                           'loaded_row_sums':{str(i):float(x) for i,x in c._det_fate.sum(axis=1).items()}})
            ledger.append({'field':'diet','reason':'constructor normalize_DC=True; canonical already source-normalized',
                           'max_abs_constructor_change':float((c._DC-md_state['DC']).abs().to_numpy().max())})
            dump('transformation_ledger.json',ledger)
            tdiag=time.perf_counter()
            result=c.diagnose_sppr(TE_option=option,**METHOD)
            report,sppr,A,L=result
            metadata['diagnostic_seconds']=time.perf_counter()-tdiag
            metadata['total_seconds']=time.perf_counter()-t
            dump('full_return.json',val(result));dump('diagnostic_report.json',plain(report))
            with (folder/'full_return.pkl').open('wb') as f:pickle.dump(result,f,protocol=5)
            dump('loaded_state_after.json',val(state(c)))
            numeric_before={k:v for k,v in before.items()};after=state(c)
            unchanged=all(before[k].equals(after[k]) for k in ['groups','DC','det_fate']) and all(before['vectors'][k].equals(after['vectors'][k]) for k in before['vectors'])
            metadata['scientific_state_unchanged_by_diagnostic']=unchanged
            names=c.seq2name; matrices={};negative=[]
            for label,df in [('SPPR',sppr),('A',A),('L',L)]:
                if df is None:matrices[label]={'availability':'missing','reason':'returned None'};continue
                arr=df.to_numpy(dtype=float);np.save(folder/f'{label}.npy',arr,allow_pickle=False)
                mask={'null':np.array([[v is None for v in r] for r in df.to_numpy()],dtype=bool),'nan':np.isnan(arr),
                      'positive_infinity':np.isposinf(arr),'negative_infinity':np.isneginf(arr)}
                np.savez_compressed(folder/f'{label}_masks.npz',**mask)
                axes={'orientation':'recipient group rows × basal-source columns' if label=='SPPR' else 'consumer group rows × prey group columns',
                  'units':'t wet-weight primary-production equivalents per t wet-weight group' if label=='SPPR' else 'dimensionless',
                  'row_ids':[int(i) for i in df.index],'row_names':[names[int(i)] for i in df.index],
                  'column_ids':[int(i) for i in df.columns],'column_names':[names[int(i)] for i in df.columns],
                  'synthetic_row_flags':[int(i)==50 for i in df.index],'synthetic_column_flags':[int(i)==50 for i in df.columns],
                  'source_scopes':{'all':[int(i) for i in df.columns],
                    'inner':[int(i) for i in df.columns if int(i)!=50],
                    'PP':[int(i) for i in df.columns if int(i) in [42,43,44,45]]} if label=='SPPR' else None,
                  'shape':list(arr.shape),'mask_counts':{k:int(v.sum()) for k,v in mask.items()}}
                dump(f'{label}_axes.json',axes); matrices[label]=axes
                reopened=np.load(folder/f'{label}.npy',allow_pickle=False)
                assert np.array_equal(reopened,arr,equal_nan=True)
                assert df.index.is_unique and df.columns.is_unique
                if label=='SPPR':
                    for i,j in zip(*np.where(arr<0)):
                        negative.append({'method':option,'matrix':'SPPR','source_seq':int(df.columns[j]),
                         'source_name':names[int(df.columns[j])],'recipient_seq':int(df.index[i]),
                         'recipient_name':names[int(df.index[i])],'value':float(arr[i,j]),'comparison_tolerance':0.0})
            dump('matrix_inventory.json',matrices);dump('negative_entries.json',negative)
            comparisons=[];wb=openpyxl.load_workbook(OLD,read_only=True,data_only=True)
            colname={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}[option]
            if sppr is not None:
                for scope,columns in [('all',list(sppr.columns)),('inner',[x for x in sppr.columns if x!=50]),
                                      ('PP',[x for x in sppr.columns if x in [42,43,44,45]])]:
                    rows=list(wb['sppr_'+scope].values); headers=list(rows[0]);col=headers.index(colname)
                    old={int(r[0]):float(r[col]) for r in rows[1:] if r[0] is not None and r[col] is not None}
                    new=sppr[columns].sum(axis=1,min_count=len(columns))
                    for seq,value in new.items():
                        prior=old.get(int(seq));delta=None if prior is None else float(value)-prior
                        comparisons.append({'scope':scope,'seq':int(seq),'group':names[int(seq)],'saved':prior,
                        'fresh':plain(float(value)),'difference':delta,'match':prior is not None and np.isclose(value,prior,rtol=1e-10,atol=1e-10)})
                dump('coefficient_comparison.json',comparisons)
            wb.close()
            captured=[{'category':w.category.__name__,'message':str(w.message),'filename':str(w.filename),'lineno':w.lineno} for w in ws]
            dump('captured_runtime_warnings.json',captured)
            metadata['returned_status']=report['status'];metadata['negative_entries']=len(negative)
            metadata['coefficient_max_absolute_difference']=max((abs(x['difference']) for x in comparisons if x['difference'] is not None),default=None)
            metadata['coefficient_comparison_all_match']=all(x['match'] for x in comparisons)
            metadata['finished_utc']=datetime.now(timezone.utc).isoformat();dump('runtime_identity.json',metadata)
            print(json.dumps({'option':option,'status':report['status'],'seconds':metadata['total_seconds'],
                 'rho_living':report['divergence'].get('rho_living'),'b':report['divergence'].get('b'),
                 'sppr_det':report['divergence'].get('sppr_det'),'negative_entries':len(negative),
                 'max_coefficient_difference':metadata['coefficient_max_absolute_difference'],
                 'comparison_all_match':metadata['coefficient_comparison_all_match']},default=str),flush=True)
    except Exception as ex:
        metadata['execution_state']='EXCEPTION';metadata['exception']=repr(ex);metadata['traceback']=traceback.format_exc()
        dump('runtime_identity.json',metadata); print(json.dumps({'option':option,'error':repr(ex)}),flush=True);raise

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    if len(sys.argv)>1:run_worker(sys.argv[1])
    else:
        states=[]
        for option in OPTIONS:
            t=time.perf_counter()
            try:
                proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),option],capture_output=True,text=True,
                                    encoding='utf-8',timeout=180,cwd=ROOT)
                status={'option':option,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'seconds':time.perf_counter()-t}
                print(proc.stdout,flush=True)
            except subprocess.TimeoutExpired as ex:
                status={'option':option,'execution_state':'TIMEOUT','seconds':time.perf_counter()-t,'reason':'180s constructor+diagnostic wall-clock bound'}
                print(json.dumps(status),flush=True)
            states.append(status)
            (OUT/'execution_status.json').write_text(json.dumps(states,ensure_ascii=False,indent=2),encoding='utf-8')
