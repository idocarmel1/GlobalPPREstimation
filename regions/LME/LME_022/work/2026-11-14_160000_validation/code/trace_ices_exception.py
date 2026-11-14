"""Retain locals from the unchanged engine's failed GE call, without repairing state."""
from pathlib import Path
import sys, json, gzip, hashlib, warnings
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as mc
from run_ices_diagnostics import MODEL, OUT, FLAGS

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    constructor=mc._constructor(FLAGS,MODEL)
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter('always')
        model,source,loader_notices=mc._load(MODEL,constructor,FLAGS)
        before=mc._runtime(model)
        original=json.loads(gzip.decompress((OUT/'constructor.json.gz').read_bytes()))['constructor_outcome']['runtime']
        trace={'purpose':'One unchanged GE repeat solely to capture failure-frame matrices; no source/engine/state repair.',
            'runtime_matches_original_run':mc._json_bytes(before)==mc._json_bytes(original),
            'model_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),
            'flags':FLAGS,'expected_basal_ids':model.get_PP_seq()+model.get_Import_seq()+model.get_DET_seq()}
        try:
            model.diagnose_sppr(**mc.method_settings('new_GE',FLAGS,MODEL)['kwargs'])
            trace['unexpected_success']=True
        except Exception as exc:
            trace['exception']={'type':type(exc).__name__,'message':str(exc)}
            tb=exc.__traceback__
            while tb:
                if tb.tb_frame.f_code.co_name=='SPPR_new':
                    local=tb.tb_frame.f_locals
                    trace['engine_line']=tb.tb_lineno
                    trace['frames']={key:mc.encode_lossless(local[key]) for key in ['SPPR','A','L','DC','GE','new_index','new_columns','basis'] if key in local}
                    trace['observations']={'SPPR_columns':local['SPPR'].columns.tolist(),
                        'SPPR_shape':list(local['SPPR'].shape),'nullspace_dimension':len(local['ns']),
                        'expected_detritus_ids':model.get_DET_seq(),
                        'DC_row_sums':{str(i):float(v) for i,v in local['DC'].sum(axis=1).items()},
                        'GE_row_nonfinite_counts':{str(i):int(v) for i,v in local['GE'].isna().sum(axis=1).items()}}
                tb=tb.tb_next
        trace['warnings']=[str(w.message) for w in notices]
    trace=mc.encode_lossless(trace)
    raw=mc._json_bytes(trace);p=OUT/'failure_frame_GE.json.gz';p.write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in trace.items() if k!='frames'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
