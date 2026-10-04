from pathlib import Path
import json,csv,hashlib,sys,shutil,pickle
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE/'diagnostics/vendor'))
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
import numpy as np
from run_direct_auto import encode
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((BASE/'diagnostics/run_manifest.json').read_text(encoding='utf-8'))
new=json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))
assert old['constructor']==new['constructor']
assert {k:v for k,v in old['method_call'].items() if k!='det_collapse_mode'}=={k:v for k,v in new['method_call'].items() if k!='det_collapse_mode'}
assert old['input_sha256']==new['input_sha256'] and old['engine']==new['engine'] and old['packages']==new['packages']
assert old['runtime_before_sha256']==new['runtime_before_sha256']
comparison={};checks={};negative=[]
for m in ['GE','TE','With Egestion']:
    k=m.replace(' ','_');folder=OUT/k
    with (folder/'full_return.pkl').open('rb') as f: ret=pickle.load(f)
    assert encode(ret)==json.loads((folder/'full_return_lossless.json').read_text(encoding='utf-8'))
    report,sppr,A,L=ret
    previous=json.loads((BASE/'diagnostics'/k/'diagnostic_return.json').read_text(encoding='utf-8'))
    assert report['config']['det_collapse_mode']=='auto'
    assert report['divergence']['solve_error'] is None
    mats={}
    for name,frame in [('SPPR',sppr),('A',A),('L',L)]:
        assert frame is not None,f'{m} {name} unavailable'
        arr=np.load(folder/f'{name}.npy',allow_pickle=False)
        axes=json.loads((folder/f'{name}_axes.json').read_text(encoding='utf-8'))
        assert np.array_equal(arr,frame.to_numpy(dtype=float),equal_nan=True)
        assert list(frame.index)==[a['id'] for a in axes['rows']]
        assert list(frame.columns)==[a['id'] for a in axes['columns']]
        masks=np.load(folder/f'{name}_masks.npz',allow_pickle=False)
        assert not any(masks[x].any() for x in masks.files),f'{m} {name} unavailable/nonfinite'
        assert np.isfinite(arr).all(),f'{m} {name} nonfinite'
        before=np.load(BASE/'diagnostics'/k/f'{name}.npy',allow_pickle=False)
        mats[name]={'shape':list(arr.shape),'entries_checked':int(arr.size),'finite':True,
                    'negative_entries_never':int((before<0).sum()),'negative_entries_auto':int((arr<0).sum()),
                    'exact_equal_never':bool(np.array_equal(arr,before)),
                    'maximum_absolute_change':float(np.max(np.abs(arr-before)))}
        if name=='SPPR':assert not (arr<0).any(),f'{m} negative SPPR'
    info=json.loads((folder/'detritus_resolution_info_lossless.json').read_text(encoding='utf-8'))
    def decode(x):
        if x['type']=='dict':return {decode(k):decode(v) for k,v in x['items']}
        if x['type'] in ['list','tuple']:return [decode(v) for v in x['items']]
        if x['type']=='null':return None
        return x.get('value')
    decoded=decode(info)
    comparison[m]={'never':{'overall':previous['status'],'components':{k:previous[k]['status'] for k in ['model_input','divergence','balance']},'pp_gap':previous['balance']['rel_gap']},
                   'auto':{'overall':report['status'],'components':{k:report[k]['status'] for k in ['model_input','divergence','balance']},'pp_gap':report['balance']['rel_gap']},
                   'matrices':mats,'detritus_resolution_info':decoded,
                   'pooling_applicability':'TE has no detritus recycling scaling; retained calculator attribute is inherited from GE and is not a TE pooling decision' if m=='TE' else 'actual successful scaling',
                   'production_eligible':False}
    checks[m]=True
(OUT/'never_vs_auto_comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'preflight_result.json').write_text(json.dumps({'passed':all(checks.values()),'hypothesis_held':True,'controlled_settings_equal_except_mode':True,'runtime_before_identical':True,'methods':checks,'no_scientific_validation':True},indent=2),encoding='utf-8')
lines=['# Northern Humboldt never versus auto comparison','',
       'The numerical preflight passed for every returned SPPR, A and L matrix. All source–recipient entries, including unfished recipients, were inspected after reopening. No SPPR value was clipped or replaced. Scientific FAIL grades remain.','',
       '| Method | Negative SPPR never | Negative SPPR auto | Auto input / convergence / balance | Auto PP gap | Pooling |','|---|---:|---:|---|---:|---|']
for m,d in comparison.items():
    lines.append(f"| {m} | {d['matrices']['SPPR']['negative_entries_never']} | {d['matrices']['SPPR']['negative_entries_auto']} | {' / '.join(d['auto']['components'].values())} | {d['auto']['pp_gap']*100:.6f}% | {'Not applicable' if m=='TE' else d['detritus_resolution_info']['method']} |")
lines+=['','[Exact comparison and pooling details](never_vs_auto_comparison.json) · [Auto settings and hashes](run_manifest.json) · [Preserved never run](../diagnostics/run_manifest.json)','',
        'All methods retain overall FAIL and false production eligibility. Selection is authorized for provisional research review; it is not researcher validation.']
(OUT/'comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
shutil.copy2(OUT/'run_direct_auto.py',OUT/'executed_code/run_direct_auto.py')
print(json.dumps(comparison,indent=2,ensure_ascii=False),flush=True)
