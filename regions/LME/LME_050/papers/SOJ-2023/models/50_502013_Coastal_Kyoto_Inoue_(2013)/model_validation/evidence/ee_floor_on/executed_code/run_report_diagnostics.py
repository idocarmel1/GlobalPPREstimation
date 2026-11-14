"""Bounded current-engine GE/TE report diagnostics, conditional on baseline parity.

No workbook/publication or canonical input changes. No pinned-engine gate bypass:
this is a new current-engine execution, after separately verified initialization.
"""
from pathlib import Path
import gzip, hashlib, json, shutil, sys, os
import numpy as np
import pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as mc
MODEL=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parents[1]
EV=MODEL/'model_validation/evidence/ee_floor_on'
ARCH=MODEL/'model_validation/evidence/source_review/diet_reextraction_20261002/current_runtime_refresh'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
def readgz(p): return json.loads(gzip.decompress(p.read_bytes()))
def matrix_check(frame,method,names):
    a=np.asarray(frame['data'],dtype=float)
    negatives=[{'method':method,'source_id':frame['columns'][j],'source_name':names.get(str(frame['columns'][j]),str(frame['columns'][j])),'group_id':frame['index'][i],'group_name':names.get(str(frame['index'][i]),str(frame['index'][i])),'value':float(a[i,j])} for i,j in np.argwhere(np.isfinite(a)&(a<0))]
    return {'shape':list(a.shape),'row_ids':frame['index'],'source_ids':frame['columns'],'all_entries_finite':bool(np.isfinite(a).all()),'strict_negative_tolerance':0.0,'negative_pairs':negatives,'negative_source_count':len(set(str(x['source_id']) for x in negatives)),'matrix_minimum':float(a.min()),'matrix_maximum':float(a.max())}

def main():
    parity=json.loads((WORK/'outputs/initialization_parity.json').read_text(encoding='utf8'))
    assert parity['all_core_parity'], 'Current initialization differs from audited base'
    assert parity['stored_baseline_parity'] is True, 'Cannot match retained baseline'
    assert sha(MODEL/'model.json')==parity['canonical_sha256']
    assert {n:sha(mc.ENGINE/n) for n in mc.ENGINE_FILES}==parity['current_code_hashes']
    if EV.exists() and any(EV.iterdir()): raise RuntimeError('Refuse to overwrite existing EE-floor evidence')
    EV.mkdir(parents=True,exist_ok=True)
    code=EV/'executed_code'; code.mkdir()
    for n in (*mc.ENGINE_FILES,'create_PPRS_excel.py'): shutil.copy2(mc.ENGINE/n,code/n)
    shutil.copy2(Path(mc.__file__),code/'method_coverage.py')
    shutil.copy2(__file__,code/Path(__file__).name)
    shutil.copy2(WORK/'outputs/initialization_parity.json',EV/'initialization_parity.json')
    flags={'constructor':{**parity['audited_constructor'],'use_ee_floor':True,'ee_floor':.1,'ee_threshold':.1,'refresh_missing_biomass_accum':False},'diagnostics':{'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.,'det_external_sppr':0.},'method_timeout_seconds':180.}
    answer=mc.compute_methods(MODEL/'model.json',flags,['new_GE','new_TE_EEfix'],EV,method_timeout=180.)
    dump(EV/'execution_summary.json',answer)
    initial=readgz(EV/'constructor.json.gz')['constructor_outcome']
    names={str(x['id']):x['name'] for x in answer['groups']}
    summaries={}; original={}
    for key,label in [('new_GE','GE'),('new_TE_EEfix','TE')]:
        doc=readgz(EV/f'{key}.json.gz')
        diagnostic=mc.diagnostics_for_table(doc.get('diagnostics'))
        summary={'execution_status':doc['status'],'reason':doc.get('reason'),'diagnostic':diagnostic,'evidence':f'{key}.json.gz'}
        if doc.get('source_matrix'):
            checked=matrix_check(doc['source_matrix'],label,names)
            checked['negative_source_count_agrees_with_diagnostic']=checked['negative_source_count']==diagnostic['divergence']['n_negative_sources']
            summary['matrix_check']=checked
            for i,name in enumerate(['SPPR','A','L'],start=1):
                encoded=doc['return']['items'][i]
                dump(EV/f'{name}_{label}.json',encoded)
                pd.DataFrame(encoded['data'],index=encoded['index'],columns=encoded['columns']).to_csv(EV/f'{name}_{label}.csv')
            summary['detritus_sppr_named']=[{'id':str(i),'name':names.get(str(i),str(i)),'sppr':v} for i,v in diagnostic['divergence'].get('sppr_det',{}).items()]
            summary['negative_pairs']=checked['negative_pairs']
        summaries[label]=summary
        baseline=pd.read_csv(ARCH/f'SPPR_{label}.csv',index_col=0)
        baseline.columns=[int(c) for c in baseline.columns]
        bdiag=json.loads((ARCH/f'diagnose_sppr_{label}.json').read_text(encoding='utf8'))['direct_diagnose_sppr_return']
        original[label]={'diagnostic':bdiag,'matrix_check':matrix_check(mc.encode_lossless(baseline),label,names),'matrix_sha256':sha(ARCH/f'SPPR_{label}.csv')}
    floor_info=initial.get('runtime',{}).get('ee_floor_info')
    ledger=initial.get('runtime',{}).get('ee_floor_ledger')
    if ledger:
        dump(EV/'ee_floor_ledger.json',ledger)
        pd.DataFrame(ledger['data'],index=ledger['index'],columns=ledger['columns']).to_csv(EV/'ee_floor_ledger.csv')
    report={'model_id':MODEL.name,'canonical_sha256':sha(MODEL/'model.json'),'source':str((MODEL/'model.json').relative_to(ROOT)).replace('\\','/'),'new_evidence':str(EV.relative_to(ROOT)).replace('\\','/'),'execution_description':'Fresh current-engine direct GE/TE diagnostics after verified OFF initialization parity; not an ee_floor_v1 pinned-engine upgrade or proof of algorithm equivalence','historical_ee_floor_provenance':'not recorded; archived engine predates floor support','current_ee_floor_v1_compatibility':parity['current_ee_floor_v1_compatible'],'initialization_parity':parity,'flags':flags,'engine_hashes':answer['engine_hashes'],'floor_info':floor_info,'floor_ledger':ledger,'methods':summaries,'historical_methods':original,'source_scopes':{'all':'All basal-source contributions','inner':'All except synthetic Import','PP':'All except synthetic Import and detritus'},'adoption':'Report evidence only; no workbook, map, trends, selection or researcher review registration changes'}
    dump(WORK/'outputs/diagnostic_audit.json',report)
    dump(EV/'diagnostic_summary.json',{k:v for k,v in report.items() if k not in ['initialization_parity','historical_methods','floor_ledger']})
    assert sha(MODEL/'model.json')==parity['canonical_sha256']
    assert {n:sha(mc.ENGINE/n) for n in mc.ENGINE_FILES}==parity['current_code_hashes']
    artifacts=[]
    for p in sorted(EV.rglob('*')):
        if p.is_file(): artifacts.append({'role':p.relative_to(EV).as_posix(),'path':p.relative_to(EV).as_posix(),'sha256':sha(p),'availability':'present'})
    artifacts.append({'role':'canonical_model','path':os.path.relpath(MODEL/'model.json',EV).replace('\\','/'),'sha256':sha(MODEL/'model.json'),'availability':'present'})
    index={'schema_version':1,'run_id':'2026-11-14_validation_lme050','region_id':'LME_050','model_id':MODEL.name,'variant_id':'same canonical model; EE floor ON 0.1, current engine','source_identity':{'canonical_sha256':parity['canonical_sha256']},'computational_input_identity':{'flags':flags,'engine_hashes':answer['engine_hashes']},'methods':['GE','TE'],'required_roles':['canonical_model','constructor.json.gz','new_GE.json.gz','new_TE_EEfix.json.gz','ee_floor_ledger.json','initialization_parity.json'],'artifacts':artifacts,'reconciliation':{'baseline_initialization_matches':parity['all_core_parity'],'all_matrices_complete':all(v.get('matrix_check',{}).get('all_entries_finite',False) for v in summaries.values()),'negative_counts_agree':all(v.get('matrix_check',{}).get('negative_source_count_agrees_with_diagnostic',False) for v in summaries.values())}}
    dump(EV/'evidence_index.json',index)
    print(json.dumps({'methods':{k:{'execution':v['execution_status'],'diagnostic_status':v['diagnostic']['status'],'divergence':v['diagnostic']['divergence'],'balance':v['diagnostic']['balance']} for k,v in summaries.items()},'floor_info':floor_info},ensure_ascii=False))
if __name__=='__main__': main()
