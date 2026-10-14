"""Compare the actual upgraded engine with saved audited and floor experiments."""
from pathlib import Path
import argparse, copy, gzip, hashlib, inspect, json, sys, warnings
import numpy as np
import pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.scientific_helpers.sppr.method_coverage import ENGINE,_load,_constructor,_runtime,encode_lossless,method_settings
from tools.project_core.calculations.ee_floor_migration import target_flags
WORK=Path(__file__).resolve().parents[1]

def read(path):return json.loads(gzip.decompress(path.read_bytes()))
def frame(value):
    def cell(v):
        if isinstance(v,dict) and v.get('type')=='float':return {'nan':np.nan,'positive_infinity':np.inf,'negative_infinity':-np.inf}[v['value']]
        return v
    f=pd.DataFrame([[cell(v) for v in r] for r in value['data']],index=value['index'],columns=value['columns'])
    f.index.names=value['index_names'];f.columns.names=value['column_names']
    for c,d in zip(f.columns,value['dtypes']):f[c]=f[c].astype(d)
    return f
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(value,ensure_ascii=False,allow_nan=False).encode(),mtime=0))

def run(unit=None):
    sys.path.insert(0,str(ROOT/'regions/LME/LME_013/work/2026-10-14_175641_low_ee_sensitivity/code'))
    from test_low_ee import scenario
    models=json.loads((ROOT/'regions/LME/LME_013/work/2026-10-14_175641_low_ee_sensitivity/inputs/models.json').read_text())
    reports=[]
    for item in models:
        if unit and item['unit_id']!=unit:continue
        work=ROOT/item['work'];cfg=json.loads((work/'inputs/configuration.json').read_text(encoding='utf-8'))
        model=ROOT/cfg['model_path'];flags=cfg['flags'];frozen=read(work/'outputs/source_and_runtime.json.gz')
        code_hash=hashlib.sha256((ENGINE/'PPRCalculator.py').read_bytes()).hexdigest()
        original,source,_=_load(model,_constructor(flags,model),flags)
        original_runtime=_runtime(original)
        assert {k:original_runtime[k] for k in frozen['runtime']}==frozen['runtime'],item['unit_id']+' original runtime mismatch'
        assert source==frozen['source'],item['unit_id']+' source mismatch'
        off_flags=target_flags(flags,False,.1,code_hash);on_flags=target_flags(flags,True,.1,code_hash)
        off,_,_=_load(model,_constructor(off_flags,model),off_flags)
        on,_,_=_load(model,_constructor(on_flags,model),on_flags)
        off_runtime=_runtime(off)
        for k,v in frozen['runtime'].items():
            if k=='_groups_df':
                old=frame(v);pd.testing.assert_frame_equal(off.get_groups_df().loc[old.index,old.columns],old,check_exact=True)
            else:assert off_runtime[k]==v,item['unit_id']+' OFF runtime differs: '+k
        report={'unit':item['unit_id'],'canonical_source_exact':True,'OFF_original_runtime_exact':True,
                'settings':on_flags,'floor_info':encode_lossless(on.ee_floor_info),'actual_model_balance':bool(on.is_model_balanced()[0]),'methods':{}}
        living=[s for s in original.p.index if s not in original.get_DET_seq()+original.get_Import_seq() and original.p[s]>0]
        original_low=[s for s in living if original.EE[s]<.1]
        skipped=[s for s in original_low if not on.ee_floor_ledger.loc[s,'applied']]
        report['experiment_eligibility_differences']=[{'seq':int(s),'group':original.seq2name[s],
            'reason':on.ee_floor_ledger.loc[s,'reason'],'source_EE':encode_lossless(on.source_EE[s]),
            'audited_runtime_EE':float(original.EE[s])} for s in skipped]
        matching,_=scenario(original,living,on.external_mortality_export,True)
        for option,key in [('GE','new_GE'),('TE','new_TE_EEfix'),('With Egestion','new_WithEgestion')]:
            kwargs=method_settings(key,on_flags,model)['kwargs']
            kwargs={k:v for k,v in kwargs.items() if k in inspect.signature(on.SPPR_new).parameters}
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                off_matrix=copy.deepcopy(off).SPPR_new(**kwargs)[0]
                actual=copy.deepcopy(on);matrix=actual.SPPR_new(**kwargs)[0]
                replay=copy.deepcopy(matching).SPPR_new(**kwargs)[0]
            baseline=frame(read(work/'outputs/baseline'/option.replace(' ','_')/'full_return.json.gz')['SPPR'])
            expected=frame(read(work/'outputs/ee_floor_0p1'/option.replace(' ','_')/'full_return.json.gz')['SPPR'])
            np.testing.assert_allclose(off_matrix.reindex(index=baseline.index,columns=baseline.columns),baseline,rtol=1e-10,atol=1e-12,equal_nan=True)
            a=matrix.reindex(index=expected.index,columns=expected.columns).to_numpy(dtype=float);b=expected.to_numpy(dtype=float)
            match=bool(np.allclose(a,b,rtol=1e-10,atol=1e-12,equal_nan=True))
            np.testing.assert_allclose(matrix.reindex(index=replay.index,columns=replay.columns),replay,rtol=1e-10,atol=1e-12,equal_nan=True)
            balance=actual.is_sppr_balanced(matrix)
            report['methods'][key]={'OFF_baseline_matrix_matches':True,'ON_experiment_matrix_matches':match,
                'ON_same_valid_input_eligibility_replay_matches':True,
                'max_absolute_experiment_difference':float(np.nanmax(np.abs(a-b))),
                'actual_is_sppr_balanced':bool(balance[0]),'actual_sppr_inflow':float(balance[1]),'actual_sppr_outflow':float(balance[2])}
            assert match or skipped,item['unit_id']+' unexplained ON matrix differs: '+key
        write(model.parent/'results/diagnostics/ee_floor/experiment_reconciliation.json.gz',report)
        print(json.dumps({'unit':report['unit'],'affected':report['floor_info'].get('affected_groups'),'model_balanced':report['actual_model_balance'],'methods':report['methods']}),flush=True)
        reports.append(report)
    write(WORK/'qa/experiment_reconciliation.json.gz',reports)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit');a=p.parse_args();run(a.unit)
