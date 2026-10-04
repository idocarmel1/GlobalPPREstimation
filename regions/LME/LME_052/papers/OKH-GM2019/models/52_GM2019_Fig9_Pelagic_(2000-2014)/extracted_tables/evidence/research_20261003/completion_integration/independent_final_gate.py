"""Independent real constructor reload of the exact persisted adopted input."""
import contextlib
import hashlib
import io
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
FINAL = HERE.parents[1] / 'assumption_variants/adopted_balanced_20261003'
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(ENGINE))
import numpy as np
from PPRCalculator import PPRCalculator


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run():
    path = FINAL / 'model.json'
    identity = sha(path)
    code_before = {p.name:sha(p) for p in [ENGINE/'PPRCalculator.py',ENGINE/'ModelData.py',ENGINE/'utils.py']}
    source = json.loads(path.read_text(encoding='utf-8'))
    settings = json.loads((FINAL/'runtime_settings.json').read_text(encoding='utf-8'))
    log = io.StringIO()
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        calc = PPRCalculator(str(path), **settings)
        actual = calc.is_model_balanced()
    (HERE/'independent_native_reload.log').write_text(log.getvalue(),encoding='utf-8')
    frame = calc.get_groups_df()
    rows = []
    for n in frame.index:
        rows.append({'id':int(n),'name':calc.seq2name[n], 'kind':str(frame.loc[n,'trophic_info']),
            **{k:float(v[n]) for k,v in {'P':calc.p,'Q':calc.q,'D':calc.predation,'BA':calc.growth,
                'M0':calc.M0,'R':calc.respiration,'U':calc.egestion,'GS':calc.GS,'EE':calc.EE,
                'catch':calc.catch,'immigration':calc.immigration,'emigration':calc.emigration,
                'detritus_export':calc.det_export}.items()}})
    living = [r for r in rows if r['id'] <= 21]
    consumers = [r for r in living if r['id'] >= 2]
    tolerance = 1e-8
    checks = {
        'actual_main_balance_return':bool(actual[0]),
        'native_22_biological_ids':sorted(int(g['group_seq']) for g in source['group']) == list(range(1,23)),
        'runtime_23_ids_with_native_import':sorted(r['id'] for r in rows) == list(range(1,24)),
        'all_vectors_finite':all(math.isfinite(v) for r in rows for k,v in r.items() if isinstance(v,float)),
        'physical_production_consumption':all(r['P'] >= -tolerance and r['Q'] >= -tolerance for r in rows),
        'physical_living_flows':all(r[k] >= -tolerance for r in living for k in ['D','M0','R','U','BA']),
        'GS_standard_bounds':all(.1-tolerance <= r['GS'] <= .35+tolerance for r in consumers),
        'EE_physical_and_standard_bounds':all(-tolerance <= r['EE'] <= .95+tolerance for r in consumers),
        'all_21_living_BA_zero':all(abs(r['BA']) <= tolerance for r in living),
        'detritus_BA_nonnegative':next(r['BA'] for r in rows if r['id']==22) >= -tolerance,
        'catch_and_all_migration_zero':all(abs(r[k]) <= tolerance for r in rows for k in ['catch','immigration','emigration']),
        'detritus_export_zero':all(abs(r['detritus_export']) <= tolerance for r in rows),
        'source_detritus_import_zero':all(float(g.get('detritus_import',0)) == 0 for g in source['group']),
        'GS_unsupplied_for_every_consumer':all(float(g['gs']) == -9999 for g in source['group'] if 2<=int(g['group_seq'])<=21),
        'detritus_fate_all_living_100percent':all(
            sum(float(p['detritus_fate']) for p in g['diet_descr']['diet']) == 1 and
            all(float(p['detritus_fate']) == (1 if int(p['prey_seq'])==22 else 0) for p in g['diet_descr']['diet'])
            for g in source['group'] if int(g['group_seq'])<=21),
        'no_unsolved_native_parameters':bool(frame.loc[list(range(1,24)),['p','q','M0','respiration','egestion','biomass_accum','gs','ee']].notna().all().all()),
        'normalization_disabled':settings.get('normalize_DC') is False,
        'input_unchanged_during_reload':sha(path)==identity,
        'executed_engine_unchanged_during_reload':code_before == {p.name:sha(p) for p in [ENGINE/'PPRCalculator.py',ENGINE/'ModelData.py',ENGINE/'utils.py']},
    }
    result = {'schema_version':1, 'model_id':source.get('model_id'), 'native_model_sha256':identity,
        'runtime_settings':settings, 'engine_sha256':code_before, 'tolerance':tolerance,
        'actual_returned_main_balanced':bool(actual[0]),
        'max_abs_production_residual':float(np.max(np.abs(actual[1]-calc.p))),
        'max_abs_consumption_residual':float(np.max(np.abs(actual[2]-calc.q))),
        'checks':checks,'all_checks_passed':all(checks.values()),'rows':rows,
        'synthetic_import_is_not_biological':True,
        'balanced_legacy_copy_used':False, 'calculator_vectors_modified':False}
    (HERE/'independent_final_gate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in {'rows','runtime_settings','engine_sha256'}},ensure_ascii=False,indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    run()
