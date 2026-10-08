"""Bounded HS_077 direct SPPR refresh using signed notebook constructor and method defaults.

Usage from repository root, with the existing NPP Python environment:
  python .../run_direct_candidate.py --input <audited computational JSON>
Candidate arithmetic is separate: calculate_candidate.py --mapping <mapping JSON>
reads retained matrices without invoking the scientific solver again.
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, inspect, json, math, os, pickle
import platform, shutil, sys, time, traceback, warnings
from datetime import datetime, timezone
from pathlib import Path

MODE = 'diagnostics'
HERE = Path(__file__).resolve().parents[1] / 'outputs' / MODE
MODEL = Path(__file__).resolve().parents[4]
ROOT = next(p for p in MODEL.parents if (p/'Project.xlsx').exists())
HERE.mkdir(parents=True,exist_ok=True)
sys.path.insert(0, str(HERE.parent / "diagnostics" / "vendor"))
sys.path.insert(0, str(ROOT / "tools/scientific_code/PPREstimation"))
import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator, DEFAULT_DIAGNOSTIC_THRESHOLDS

METHODS = ("GE", "TE", "With Egestion")
CONSTRUCTOR = dict(underdetermined=True, zero_catch=True,
                   zero_biomass_accum=False, default_gs=True,
                   weight_flow=1.0, weight_guess=1.0, normalize_DC=True,
                   DC_tol=0.001, balance_BA_after_DC_normalization=True)
SOLVER = {}  # Same defaults as the researcher's HS_077 notebook. Effective config retained in each diagnostic return.
TOL = dict(rtol=1e-10, atol=1e-12)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def encode(x):
    """Typed JSON preserves every returned field, axes, tuple and special value."""
    if x is None:
        return {"type": "null"}
    if x is pd.NA:
        return {"type": "pandas.NA"}
    if isinstance(x, (float, np.floating)):
        if math.isnan(x): return {"type": "float", "value": "NaN"}
        if math.isinf(x): return {"type": "float", "value": "+Inf" if x > 0 else "-Inf"}
        return {"type": "float", "value": float(x)}
    if isinstance(x, (bool, np.bool_)): return {"type": "bool", "value": bool(x)}
    if isinstance(x, (int, np.integer)): return {"type": "int", "value": int(x)}
    if isinstance(x, str): return {"type": "str", "value": x}
    if isinstance(x, pd.DataFrame):
        return {"type": "DataFrame", "index": encode(list(x.index)),
                "columns": encode(list(x.columns)), "index_name": encode(x.index.name),
                "columns_name": encode(x.columns.name), "dtypes": [str(d) for d in x.dtypes],
                "data": [[encode(v) for v in row] for row in x.to_numpy(dtype=object)]}
    if isinstance(x, pd.Series):
        return {"type": "Series", "index": encode(list(x.index)), "name": encode(x.name),
                "dtype": str(x.dtype), "data": [encode(v) for v in x.to_numpy(dtype=object)]}
    if isinstance(x, np.ndarray):
        return {"type": "ndarray", "shape": list(x.shape), "dtype": str(x.dtype),
                "data": encode(x.tolist())}
    if isinstance(x, dict): return {"type": "dict", "items": [[encode(k), encode(v)] for k,v in x.items()]}
    if isinstance(x, tuple): return {"type": "tuple", "items": [encode(v) for v in x]}
    if isinstance(x, list): return {"type": "list", "items": [encode(v) for v in x]}
    if isinstance(x, Path): return {"type": "Path", "value": str(x)}
    if isinstance(x, (ModelData, PPRCalculator)):
        return {"type": type(x).__name__, "attributes": encode(vars(x))}
    raise TypeError(f"Unsupported lossless serialization: {type(x).__name__}")

def plain(x):
    """Readable companion; lossless encoding above remains authoritative."""
    if isinstance(x, dict): return {str(k): plain(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [plain(v) for v in x]
    if isinstance(x, (np.bool_,)): return bool(x)
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (float,np.floating)):
        return float(x) if math.isfinite(x) else {"nonfinite": "NaN" if math.isnan(x) else ("+Inf" if x>0 else "-Inf")}
    if isinstance(x, np.ndarray): return plain(x.tolist())
    return x

def save(name, x, typed=False):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(encode(x) if typed else plain(x), ensure_ascii=False,
                            allow_nan=False, indent=2), encoding="utf-8")
    return p

def same(a,b): return encode(a) == encode(b)

def capture_matrix(folder, name, frame, names, trophic, orientation):
    folder.mkdir(parents=True, exist_ok=True)
    if frame is None:
        save(str(folder.relative_to(HERE) / f"{name}_unavailable.json"),
             {"availability":"unavailable", "reason":"Actual direct return is None"})
        return None
    arr = frame.to_numpy(dtype=float)
    obj = frame.to_numpy(dtype=object)
    null = np.array([[v is None or v is pd.NA for v in row] for row in obj], dtype=bool)
    masks = dict(null=null, nan=np.isnan(arr)&~null, positive_infinity=np.isposinf(arr),
                 negative_infinity=np.isneginf(arr))
    np.save(folder / f"{name}.npy", arr, allow_pickle=False)
    np.savez_compressed(folder / f"{name}_masks.npz", **masks)
    frame.to_csv(folder / f"{name}.csv", encoding="utf-8", float_format="%.17g")
    def axis(ids):
        return [{"id":int(i), "name":names.get(int(i),str(i)),
                 "trophic_type":trophic.get(int(i)),
                 "synthetic":trophic.get(int(i))=="Import"} for i in ids]
    axes = {"orientation":orientation, "units":"wet-weight-equivalent primary production per wet-weight unit" if name=="SPPR" else "dimensionless",
            "rows":axis(frame.index), "columns":axis(frame.columns),
            "shape":list(arr.shape), "null_count":int(null.sum()),
            "nan_count":int(masks['nan'].sum()),
            "positive_infinity_count":int(masks['positive_infinity'].sum()),
            "negative_infinity_count":int(masks['negative_infinity'].sum())}
    save(str(folder.relative_to(HERE)/f"{name}_axes.json"), axes)
    loaded=np.load(folder/f"{name}.npy",allow_pickle=False)
    masks_back=np.load(folder/f"{name}_masks.npz",allow_pickle=False)
    assert np.array_equal(loaded,arr,equal_nan=True)
    assert len(set(frame.index))==len(frame.index) and len(set(frame.columns))==len(frame.columns)
    assert all(np.array_equal(masks[k],masks_back[k]) for k in masks)
    return axes

def preflight(data):
    unknown=[]
    for g in data['group']:
        typ=int(float(g['pp']))
        fields=('biomass','pb','qb','ee','gs') if typ==0 else (('biomass','pb','ee') if typ==1 else ('biomass',))
        for f in fields:
            v=g.get(f)
            try: missing=v is None or float(v)==-9999 or not math.isfinite(float(v))
            except (TypeError,ValueError): missing=True
            if missing: unknown.append({'id':int(g['group_seq']),'name':g['group_name'],'field':f,'value':v})
    return unknown

def run(input_path):
    started=time.time()
    code_folder=HERE/'executed_code';code_folder.mkdir(exist_ok=True)
    for n in ['PPRCalculator.py','ModelData.py','utils.py']:
        shutil.copyfile(ROOT/'tools/scientific_code/PPREstimation'/n,code_folder/n)
    data=json.loads(input_path.read_text(encoding='utf-8-sig'))
    copied=input_path
    source_before=sha(input_path)
    environment={k:importlib.metadata.version(k) for k in ['numpy','pandas','scipy','sympy','igraph','tqdm','mpmath']}
    manifest={'schema_version':1,'run_id':'HS077_20261008_review_refresh',
              'region_id':'HS_077','model_id':'077HS_1_Eastern_tropical_Pacific_(1993-1997)',
              'timestamp_utc':datetime.now(timezone.utc).isoformat(),
              'input_path':os.path.relpath(input_path,HERE).replace('\\','/'),
              'input_sha256':source_before,'copied_input_sha256':sha(copied),
              'constructor':CONSTRUCTOR,'method_call':{'short':False,'flat':False,'return_sppr':True,**SOLVER},
              'thresholds':DEFAULT_DIAGNOSTIC_THRESHOLDS,'comparison_tolerances':TOL,
              'negative_entry_comparison':{'actual_negative_threshold':0.0,'material_threshold':-1e-12},
              'engine':{n:sha(ROOT/'tools/scientific_code/PPREstimation'/n) for n in ['PPRCalculator.py','ModelData.py','utils.py']},
              'script_sha256':sha(Path(__file__)),'python':sys.executable,'platform':platform.platform(),
              'packages':environment,'selection_adoption':'Researcher Ido Carmel signed MODEL VALIDATED on 08/10/2026; authorized corrected-source refresh and map handoff',
              'automatic_balanced_copy':'Constructor creates balanced_model; stored for provenance, never used for direct diagnosis or arithmetic.'}
    unknown=[v for v in preflight(data) if v['field'] in ('biomass','pb','qb') and int(float(next(g['pp'] for g in data['group'] if int(g['group_seq'])==v['id'])))!=2]  # Missing EE is explicitly admitted to LIM in the reviewed notebook.
    save('missing_biological_input_admission.json',{'missing':unknown,'admitted':not unknown})
    results={}
    if unknown:
        for option in METHODS:
            results[option]={'execution_status':'NOT_RUN','reason':'Missing source biological inputs; no placeholder biomass/default biology accepted','missing_inputs':unknown}
        save('methods_summary.json',results)
        save('run_manifest.json',{**manifest,'constructor_status':'NOT_RUN','duration_seconds':time.time()-started})
        return
    warning_records=[]
    try:
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            md=ModelData(str(copied))
            save('modeldata_exact.json',md,typed=True)
            md.groups_data.to_csv(HERE/'modeldata_groups.csv',encoding='utf-8',float_format='%.17g')
            md.DC.to_csv(HERE/'raw_loader_diet.csv',encoding='utf-8',float_format='%.17g')
            md.det_fate.to_csv(HERE/'loader_detritus_fate.csv',encoding='utf-8',float_format='%.17g')
            c=PPRCalculator.from_modeldata(md,**CONSTRUCTOR)
            warning_records.extend({'phase':'constructor','category':w.category.__name__,'message':str(w.message)} for w in ws)
    except Exception as e:
        exception={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
        save('constructor_exception.json',exception)
        for option in METHODS:
            results[option]={'execution_status':'NOT_RUN','reason':'Constructor exception','exception':exception}
        save('methods_summary.json',results)
        save('run_manifest.json',{**manifest,'constructor_status':'FAILED','duration_seconds':time.time()-started})
        return
    names={int(i):n for i,n in c.seq2name.items()}
    trophic={int(i):v for i,v in c._groups_df.trophic_info.items()}
    save('runtime_before_methods_lossless.json',vars(c),typed=True)
    with (HERE/'runtime_before_methods.pkl').open('wb') as f: pickle.dump(c,f,protocol=5)
    with (HERE/'runtime_before_methods.pkl').open('rb') as f:
        restored=pickle.load(f)
    assert encode(vars(c))==encode(vars(restored))
    manifest['persisted_runtime_reload_exact']=True
    manifest['runtime_before_sha256']=sha(HERE/'runtime_before_methods_lossless.json')
    c._groups_df.to_csv(HERE/'runtime_groups.csv',encoding='utf-8',float_format='%.17g')
    c._DC.to_csv(HERE/'runtime_diet.csv',encoding='utf-8',float_format='%.17g')
    ledger=[]
    for i in md.groups_data.index:
        for field in md.groups_data.columns:
            a=md.groups_data.loc[i,field]; b=c._groups_df.loc[i,field] if field in c._groups_df else None
            ledger.append({'id':int(i),'name':names[int(i)],'layer':'ModelData to calculator table','field':field,
                           'source':encode(a),'runtime':encode(b),'changed':not same(a,b)})
    vectors={'p':'p','q':'q','catch':'catch','predation':'predation','growth':'biomass_accum','M0':'M0',
             'respiration':'respiration','egestion':'egestion','EE':'ee','GE':'ge','GS':'gs','TL':'tl',
             'immigration':'immigration','emigration':'emigration','net_migration':'net_migration','det_export':'det_export'}
    for vector,field in vectors.items():
        for i,b in getattr(c,vector).items():
            a=c._groups_df.loc[i,field] if field in c._groups_df else None
            ledger.append({'id':int(i),'name':names[int(i)],'layer':'calculator table to effective vector','field':vector,
                           'source':encode(a),'runtime':encode(b),'changed':not same(a,b)})
    raw_field_map={'biomass':'biomass','pb':'pb','qb':'qb','ee':'ee','gs':'gs','ge':'ge','biomass_accum':'biomass_accum',
                   'immigration':'immigration','emigration':'emigration','export':'catch','respiration':'respiration'}
    json_to_loaded=[]
    for g in data['group']:
        i=int(g['group_seq'])
        for raw,a in g.items():
            loaded=raw_field_map.get(raw,raw if raw in md.groups_data.columns else None)
            if raw=='group_name': loaded='group_name'
            b=md.groups_data.loc[i,loaded] if loaded else None
            json_to_loaded.append({'id':i,'name':names[i],'source_field':raw,'raw_value':encode(a),
                'loader_field':loaded,'loaded_value':encode(b),'loader_status':'parsed or derived' if loaded else 'not exposed as scalar field; preserved in exact input',
                'note':'Diet, routing, trophic flag and synthetic group transformations retained separately in exact ModelData.'})
        for raw,loaded in raw_field_map.items():
            a=g.get(raw);b=md.groups_data.loc[i,loaded]
            ledger.append({'id':i,'name':names[i],'layer':'JSON to ModelData','field':raw,'loaded_field':loaded,
                           'source':encode(a),'runtime':encode(b),'changed':not same(a,b),
                           'comparison_note':'JSON stored strings become numeric; missing sentinel remains NaN.'})
    save('loader_field_ledger.json',ledger)
    save('full_input_field_ledger.json',json_to_loaded)
    strict,production,consumption=c.is_model_balanced()
    budget=pd.DataFrame({'group_name':c._groups_df.group_name,'trophic_type':c._groups_df.trophic_info,
                         'p':c.p,'production_rhs':production,'production_residual':production-c.p,
                         'q':c.q,'consumption_rhs':consumption,'consumption_residual':consumption-c.q,
                         'catch':c.catch,'predation':c.predation,'M0':c.M0,'egestion':c.egestion,
                         'BA_growth':c.growth,'net_migration':c.net_migration})
    budget.to_csv(HERE/'runtime_group_budget_residuals.csv',encoding='utf-8',float_format='%.17g')
    sums=[];cells=[]
    for i in md.DC.index:
        raw=float(md.DC.loc[i].sum(skipna=False));runtime=float(c._DC.loc[i].sum(skipna=False))
        sums.append({'recipient_consumer_id':int(i),'name':names[int(i)],'raw_sum':raw,'runtime_sum':runtime,
                     'factor':runtime/raw if raw else None,'synthetic':trophic[int(i)]=='Import',
                     'changed':not np.array_equal(md.DC.loc[i].to_numpy(),c._DC.loc[i].to_numpy(),equal_nan=True)})
        for j in md.DC.columns:
            a=md.DC.loc[i,j];b=c._DC.loc[i,j]
            if not same(a,b):
                cells.append({'consumer_id':int(i),'consumer_name':names[int(i)],'prey_id':int(j),'prey_name':names[int(j)],
                              'raw':float(a),'runtime':float(b),'delta':float(b-a),'factor':float(b/a) if a else None})
    save('runtime_normalization_rows.json',sums)
    save('runtime_normalization_changed_cells.json',cells)
    save('runtime_normalization_dependent_transformations.json',c.diet_normalization_balance_ledger,typed=True)
    save('source_scope_definitions.json',{'PP':c.get_PP_seq(),'inner':c.get_PP_seq()+c.get_DET_seq(),
         'all':c.get_PP_seq()+c.get_Import_seq()+c.get_DET_seq(),'names':names,
         'definitions':{'PP':'Primary producer basal columns only','inner':'All returned basal columns except imported diet',
                        'all':'Every basal column including imported diet; detritus counted as returned scaling'},
         'units':'wet weight equivalent per unit wet weight','synthetic_groups':c.get_Import_seq()})
    negative=[];coeff_rows=[];reconcile={}
    for option in METHODS:
        key=option.replace(' ','_');folder=HERE/key;folder.mkdir(exist_ok=True)
        method_start=time.time()
        try:
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('always')
                ret=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**SOLVER)
                warning_records.extend({'phase':option,'category':w.category.__name__,'message':str(w.message)} for w in ws)
            report,sppr,A,L=ret
            save(f'{key}/full_return_lossless.json',ret,typed=True)
            with (folder/'full_return.pkl').open('wb') as f: pickle.dump(ret,f,protocol=5)
            with (folder/'full_return.pkl').open('rb') as f: assert encode(pickle.load(f))==encode(ret)
            save(f'{key}/diagnostic_return.json',report)
            save(f'{key}/detritus_resolution_info_lossless.json',getattr(c,'detritus_resolution_info',None),typed=True)
            axes={}
            for name,frame in [('SPPR',sppr),('A',A),('L',L)]:
                axes[name]=capture_matrix(folder,name,frame,names,trophic,
                     'rows recipient groups; columns basal source groups' if name=='SPPR' else 'rows recipient groups; columns prey groups')
                if frame is not None:
                    for ri,cj in np.argwhere(frame.to_numpy(dtype=float)<0):
                        i=int(frame.index[ri]);j=int(frame.columns[cj]);value=float(frame.iloc[ri,cj])
                        negative.append({'method':option,'matrix':name,'source_column_id':j,'source_column_name':names[j],
                                         'recipient_group_id':i,'recipient_group_name':names[i],'value':value,
                                         'comparison_tolerance':0.0,'material_below_minus_1e12':value < -1e-12,
                                         'unfished_recipient':bool(c.catch.get(i,0)==0)})
            entry={'execution_status':'RETURNED','overall_status':report['status'],
                   'component_grades':{k:report[k]['status'] for k in ['model_input','divergence','balance']},
                   'strict_flags':{'is_model_balanced':report['model_input']['is_model_balanced'],
                                   'dc_rows_sum_to_1':report['model_input']['dc_rows_sum_to_1'],
                                   'b_converges':report['divergence'].get('b_converges'),
                                   'living_converges':report['divergence'].get('living_converges'),
                                   'is_sppr_balanced':report['balance'].get('is_balanced')},
                   'coefficients_available':sppr is not None,
                   'duration_seconds':time.time()-method_start,'production_eligible':False,
                   'eligibility_reason':'Source adopted and researcher reviewed; retained configuration FAIL remains ineligible' if report['status']=='FAIL' else 'Reviewed provisional source and mapping; no promotion to production eligibility'}
            if sppr is not None:
                scopes={'PP':[i for i in sppr.columns if i not in c.get_DET_seq()+c.get_Import_seq()],
                        'inner':[i for i in sppr.columns if i not in c.get_Import_seq()],
                        'all':list(sppr.columns)}
                for scope,cols in scopes.items():
                    scoped=sppr.loc[:,cols].sum(axis=1,skipna=False)
                    for i,v in scoped.items():
                        coeff_rows.append({'method':option,'scope':scope,'group_id':int(i),'group_name':names[int(i)],
                                           'trophic_type':trophic[int(i)],'synthetic':trophic[int(i)]=='Import',
                                           'source_ids':'|'.join(str(int(s)) for s in cols),'sppr_wet':float(v),
                                           'model_catch':float(c.catch.get(i,np.nan)),'unfished':bool(c.catch.get(i,0)==0),
                                           'overall_status':report['status'],'production_eligible':False})
                    observed=float((scoped*c.catch.reindex(scoped.index)).sum(skipna=False))
                    expected=report['footprint'][{'PP':'ppr_pp_only','inner':'ppr_inner','all':'ppr_all'}[scope]]
                    reconcile[f'{key}_{scope}_diagnostic_footprint']=bool(expected is not None and np.isclose(observed,expected,**TOL))
                    entry.setdefault('scope_model_catch_ppr',{})[scope]={'retained_matrix_sum':observed,'diagnostic_footprint':expected,
                                                                     'reconciles':reconcile[f'{key}_{scope}_diagnostic_footprint']}
                entry['all_coefficients_finite']=bool(np.isfinite(sppr.to_numpy(dtype=float)).all())
                entry['negative_sppr_entries']=int((sppr.to_numpy(dtype=float)<0).sum())
                entry['negative_sppr_sources']=int((sppr<0).any(axis=0).sum())
                entry['unfished_negative_sppr_entries']=sum(1 for n in negative if n['method']==option and n['matrix']=='SPPR' and n['unfished_recipient'])
                reconcile[f'{key}_negative_source_count']=entry['negative_sppr_sources']==report['divergence']['n_negative_sources']
            results[option]=entry
            print(option,entry['overall_status'],entry['strict_flags'],flush=True)
        except Exception as e:
            exception={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
            save(f'{key}/execution_exception.json',exception)
            results[option]={'execution_status':'EXCEPTION','overall_status':None,'exception':exception,
                             'production_eligible':False,'duration_seconds':time.time()-method_start}
    pd.DataFrame(negative,columns=['method','matrix','source_column_id','source_column_name','recipient_group_id',
        'recipient_group_name','value','comparison_tolerance','material_below_minus_1e12','unfished_recipient']).to_csv(HERE/'all_negative_matrix_entries.csv',index=False,encoding='utf-8',float_format='%.17g')
    pd.DataFrame(coeff_rows).to_csv(HERE/'group_scope_coefficients.csv',index=False,encoding='utf-8',float_format='%.17g')
    save('methods_summary.json',results)
    save('warnings.json',warning_records)
    save('runtime_after_methods_lossless.json',vars(c),typed=True)
    assert sha(input_path)==source_before
    manifest.update(constructor_status='CONSTRUCTED',source_input_unchanged=True,
                    runtime_after_sha256=sha(HERE/'runtime_after_methods_lossless.json'),
                    duration_seconds=time.time()-started,reconciliation=reconcile)
    save('run_manifest.json',manifest)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True)
    args=ap.parse_args();run(args.input)
