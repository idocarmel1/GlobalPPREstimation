from __future__ import annotations
import sys,json,pickle,hashlib,datetime,os,pprint
from pathlib import Path
import numpy as np,pandas as pd,openpyxl
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
MODEL=ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json';OLD=MODEL.parent/'sppr_source.xlsx'
SOURCE=ROOT/'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def decode(o):
    k=o['type']
    if k=='null':return None
    if k=='bool':return bool(o['value'])
    if k=='int':return int(o['value'])
    if k=='float':return float.fromhex(o['hex'])
    if k=='str':return o['value']
    if k=='dict':return {decode(x):decode(y) for x,y in o['entries']}
    if k in ['list','tuple']:return (list if k=='list' else tuple)(decode(v) for v in o['items'])
    if k=='Series':return pd.Series([decode(v) for v in o['data']],index=[decode(v) for v in o['index']],name=decode(o['name']),dtype=o['dtype'])
    if k=='DataFrame':
        f=pd.DataFrame([[decode(v) for v in row] for row in o['data']],index=[decode(v) for v in o['index']],columns=[decode(v) for v in o['columns']])
        for col,dtype in zip(f.columns,o['dtypes']):f[col]=f[col].astype(dtype)
        f.index.names=[decode(v) for v in o['index_names']];f.columns.names=[decode(v) for v in o['column_names']]
        return f
    if k=='ndarray':return np.array(decode(o['data']),dtype=o['dtype']).reshape(o['shape'])
    raise ValueError(k)
sys.stdout.reconfigure(encoding='utf-8')
summary=[];artifacts=[]
def add(role,path):artifacts.append({'role':role,'path':os.path.relpath(path,OUT).replace('\\','/'),
                                    'sha256':sha(path),'availability':'present'})
wb=openpyxl.load_workbook(OLD,read_only=True,data_only=True)
for key,option,method in [('GE','GE','new_GE'),('TE','TE','new_TE_EEfix'),('With_Egestion','With Egestion','new_WithEgestion')]:
    folder=OUT/key
    result=pickle.loads((folder/'full_return.pkl').read_bytes());report,sppr,A,L=result
    jresult=decode(json.loads((folder/'full_return.json').read_text(encoding='utf-8')))
    assert len(result)==len(jresult)==4
    for x,y in zip(result[1:],jresult[1:]):pd.testing.assert_frame_equal(x,y,check_exact=True)
    before=decode(json.loads((folder/'loaded_state_before.json').read_text(encoding='utf-8')))
    after=decode(json.loads((folder/'loaded_state_after.json').read_text(encoding='utf-8')))
    unchanged=all(before[k].equals(after[k]) for k in ['groups','DC','det_fate']) and all(before['vectors'][k].equals(after['vectors'][k]) for k in before['vectors'])
    comparisons=[]
    for scope,cols in [('all',list(sppr.columns)),('inner',[x for x in sppr.columns if x!=50]),('PP',[x for x in sppr.columns if x in [42,43,44,45]])]:
        rows=list(wb['sppr_'+scope].values);headers=list(rows[0]);column=headers.index(method)
        prior={int(r[0]):float(r[column]) for r in rows[1:] if r[0] is not None and r[column] is not None}
        for seq,value in sppr[cols].sum(axis=1,min_count=len(cols)).items():
            old=prior.get(int(seq));new=float(value);delta=None if old is None else new-old
            comparisons.append({'scope':scope,'seq':int(seq),'name':before['groups'].loc[seq,'group_name'],
                                'saved':old,'fresh':new,'difference':delta,'relative_difference':None if not old else delta/old,
                                'match_at_1e-10':old is not None and bool(np.isclose(new,old,rtol=1e-10,atol=1e-10))})
    dump(folder/'coefficient_comparison.json',comparisons)
    flat={}
    for section,body in report.items():
        if not isinstance(body,dict):flat['n_'+section if isinstance(body,(list,tuple)) else section]=len(body) if isinstance(body,(list,tuple)) else body;continue
        for field,value in body.items():
            name=f'{section}_{field}'
            if isinstance(value,dict):flat.update({f'{name}_{k}':v for k,v in value.items()})
            elif isinstance(value,(list,tuple)):flat[f'{section}_n_{field}']=len(value)
            else:flat[name]=value
    healthrows=list(wb['model_health'].values);healthkeys=healthrows[0]
    priorhealth=next(dict(zip(healthkeys,row)) for row in healthrows[1:] if row[0]==option)
    scalar=[]
    for field,new in flat.items():
        old=priorhealth.get(field)
        if isinstance(new,(float,int,np.floating,np.integer)) and not isinstance(new,(bool,np.bool_)):
            match=old is not None and bool(np.isclose(new,old,rtol=1e-10,atol=1e-10,equal_nan=True))
            delta=None if old is None else float(new)-float(old)
        else:match=old==new;delta=None
        scalar.append({'field':field,'saved':old,'fresh':new,'difference':delta,'match_at_1e-10':match})
    dump(folder/'saved_health_comparison.json',scalar)
    readable=pprint.pformat(report,sort_dicts=False,width=130)+'\n'
    for label,matrix in [('SPPR',sppr),('A',A),('L',L)]:readable+='\n'+label+'\n'+matrix.to_string(max_rows=None,max_cols=None,float_format=lambda x:repr(float(x)))+'\n'
    (folder/'full_return.txt').write_text(readable,encoding='utf-8')
    loaded=[];rows=list(wb['groups_df'].values);headers=list(rows[0]);oldgroups={int(r[0]):dict(zip(headers,r)) for r in rows[1:]}
    for seq,row in before['groups'].iterrows():
        for field in row.index:
            if field not in oldgroups[int(seq)]:continue
            old=oldgroups[int(seq)][field];new=row[field]
            if isinstance(new,(float,int,np.floating,np.integer)) and old is not None:
                loaded.append({'seq':int(seq),'field':field,'saved':float(old),'fresh':float(new),
                               'difference':float(new)-float(old),'match':bool(np.isclose(new,old,rtol=1e-10,atol=1e-10,equal_nan=True))})
    dump(folder/'loaded_groups_comparison.json',loaded)
    checks=[]
    for label,matrix in [('SPPR',sppr),('A',A),('L',L)]:
        arr=np.load(folder/f'{label}.npy',allow_pickle=False);masks=np.load(folder/f'{label}_masks.npz',allow_pickle=False)
        axes=json.loads((folder/f'{label}_axes.json').read_text(encoding='utf-8'))
        assert np.array_equal(arr,matrix.to_numpy(),equal_nan=True)
        assert axes['row_ids']==matrix.index.tolist() and axes['column_ids']==matrix.columns.tolist()
        assert axes['row_ids']==list(dict.fromkeys(axes['row_ids'])) and axes['column_ids']==list(dict.fromkeys(axes['column_ids']))
        for k,expected in [('nan',np.isnan(arr)),('positive_infinity',np.isposinf(arr)),('negative_infinity',np.isneginf(arr))]:assert np.array_equal(masks[k],expected)
        checks.append({'matrix':label,'shape':list(arr.shape),'axes_verified':True,'mask_counts':{k:int(masks[k].sum()) for k in masks.files},
                       'negative_count':int((arr<0).sum()),'npy_matches_lossless_json':True})
    dump(folder/'reopened_verification.json',{'full_json_equals_pickle_exact':True,'matrix_checks':checks,
      'scientific_state_unchanged':unchanged,'coefficient_tolerance':{'rtol':1e-10,'atol':1e-10},
      'all_coefficients_match':all(x['match_at_1e-10'] for x in comparisons),'all_loaded_numeric_groups_match':all(x['match'] for x in loaded)})
    metadata=json.loads((folder/'runtime_identity.json').read_text(encoding='utf-8'))
    metadata['execution_state']='RETURNED';metadata['returned_status']=report['status']
    if 'exception' in metadata:metadata['postprocessing_error']=metadata.pop('exception')
    if 'traceback' in metadata:metadata['postprocessing_error_traceback']=metadata.pop('traceback')
    metadata['postprocessing_recovered_from_same_return']=True
    metadata['executed_script_snapshot']='../direct_diagnostics_initial.py'
    assert metadata['runtime_hashes']['direct_diagnostics.py']==sha(OUT/'direct_diagnostics_initial.py')
    metadata['coefficient_max_absolute_difference']=max(abs(x['difference']) for x in comparisons)
    metadata['coefficient_max_relative_difference']=max(abs(x['relative_difference']) for x in comparisons if x['relative_difference'] is not None)
    metadata['coefficient_comparison_all_match']=all(x['match_at_1e-10'] for x in comparisons)
    metadata['scientific_state_unchanged_by_diagnostic']=unchanged
    metadata['runtime_warning_capture_availability']='not retained because original final postprocessing failed; complete diagnostic warnings are in exact returned report'
    dump(folder/'runtime_identity.json',metadata)
    summary.append({'option':option,'status':report['status'],'model_input_status':report['model_input']['status'],
       'model_input_strict_balanced':report['model_input']['is_model_balanced'],'balance_status':report['balance']['status'],
       'balance_strict_balanced':report['balance']['is_balanced'],'rho_living':report['divergence']['rho_living'],
       'b':report['divergence']['b'],'b_definition':'rho(diag(theta)B), TE b0 is formulation convention',
       'detritus':{'seq':49,'name':'Detritus','sppr':report['divergence']['sppr_det'][49]},
       'negative_SPPR_entries':int((sppr.to_numpy()<0).sum()),'nonfinite_SPPR_entries':int((~np.isfinite(sppr.to_numpy())).sum()),
       'max_coefficient_difference':metadata['coefficient_max_absolute_difference'],'coefficient_rows_compared':len(comparisons),
       'max_loaded_field_difference':max(abs(x['difference']) for x in loaded),'scientific_state_unchanged':unchanged,
       'seconds':metadata['total_seconds'],'warnings':report['warnings']})
    for p in folder.iterdir():
        if p.is_file():add(f'{key}_{p.stem}',p)
wb.close();dump(OUT/'direct_summary.json',summary)
for role,path in [('source_pdf',SOURCE),('canonical_model',MODEL),('saved_export',OLD),('source_audit',OUT/'source_audit.json'),
                  ('executed_entry_point',OUT/'direct_diagnostics_initial.py'),('reproduction_entry_point',OUT/'direct_diagnostics.py'),
                  ('postprocessing',Path(__file__)),('diagnostic_summary',OUT/'direct_summary.json')]:add(role,path)
for p in OUT.iterdir():
    if p.is_file() and (p.name.startswith('source_page_') or p.name.startswith('source_table') or p.name in ['native_recovery_search.json','recovery_http_attempts.json','ecobase_catalogue_20260930.html','direct_reports.txt','audit_source.py','source_findings.txt','source_audit_summary.txt','execution_status.json','execution_status_initial_postprocessing_errors.json']):add(p.stem,p)
required=['source_pdf','canonical_model','saved_export','source_audit','executed_entry_point','diagnostic_summary']
for key in ['GE','TE','With_Egestion']:required.extend([f'{key}_{x}' for x in ['full_return','SPPR','SPPR_axes','SPPR_masks','runtime_identity','transformation_ledger','reopened_verification','coefficient_comparison']])
index={'schema_version':1,'run_id':'LME034_34_1_direct_20260930','region_id':'LME_034','model_id':'34_1_Bay_of_Bengal_(1978)',
       'variant_id':'existing_source_normalized_constructor_derived_BA','source_identity':{'sha256':sha(SOURCE)},
       'computational_input_identity':{'sha256':sha(MODEL)},'methods':['GE','TE','With Egestion'],
       'artifacts':artifacts,'required_roles':required,
       'reconciliation':{'full_matrices_reopened':True,'negative_entries_checked_all_groups_sources':True,
                        'coefficients_match_saved_at_1e_10':all(x['max_coefficient_difference']<1e-8 for x in summary),
                        'diagnostics_preserve_scientific_loaded_state':all(x['scientific_state_unchanged'] for x in summary)},
       'scientific_source_fidelity_complete':False,
       'scientific_limitation':'Material Table17 diet omissions/existing normalization and non-source BA; native author balanced model unavailable',
       'constructor_runtime_warnings_retained':False}
index['artifacts'].append({'role':'constructor_runtime_warning_capture','availability':'missing','reason':'Original postprocessing failed after full returns were retained; diagnostic warnings are retained exactly but external constructor warning capture was lost','acquisition_status':'not retried; no additional science execution needed for full returned diagnostic evidence'})
dump(OUT/'diagnostic_evidence_index.json',index)
full=dict(index);full['required_roles']=list(index['required_roles'])+['author_native_balanced_model']
full['artifacts']=list(index['artifacts'])+[{'role':'author_native_balanced_model','availability':'missing','reason':'Malformed Table17/AppendixA3.2 published diets prevent source-faithful reconstruction; bounded primary recovery did not obtain native database','acquisition_status':'searched primary official BOBLME/workshop/EcoBase routes and local archive; source host fails DNS, Google site sign-in, focal EcoBase accession not found'}]
dump(OUT/'evidence_index.json',full);print(json.dumps(summary))
