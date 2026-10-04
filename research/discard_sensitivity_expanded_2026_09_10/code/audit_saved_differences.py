"""Diagnose saved-output differences by replaying one changed setting at a time."""
from pathlib import Path
import json,contextlib,io,warnings
import numpy as np,pandas as pd
from baseline import ROOT,ModelData,PPRCalculator,SETTINGS,METHODS,SCOPES,calculate,scoped
from summarize import saved_checks
from run_study import write_json

def run():
    output=[]
    selected={r['model_id']:ROOT/r['snapshot_path'] for r in json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))}
    selected.update({p.stem:p for p in (ROOT/'inputs/references').glob('*.json')})
    for path in sorted((ROOT/'results/models').glob('*/study.json')):
        study=saved_checks(json.loads(path.read_text(encoding='utf-8')));mid=study['models'][0]['model_id']
        failed=[c for c in study['baseline_checks'] if c.get('provenance')=='existing_saved_workbook' and c['passed'] is False]
        if not failed:continue
        with warnings.catch_warnings(),contextlib.redirect_stdout(io.StringIO()):
            warnings.simplefilter('ignore')
            model=ModelData(str(selected[mid]));calc=PPRCalculator.from_modeldata(model,**dict(SETTINGS,normalize_DC=False))
            frames={}
            for method in set(c['method'] for c in failed):
                try:frames[method]=calculate(calc,method)
                except Exception:frames[method]=None
        book=ROOT/'inputs/workbooks'/f'{mid}.xlsx';bookdata=pd.read_excel(book,sheet_name=None)
        checks=[]
        for check in failed:
            method=check['method'];scope=check['scope'];frame=frames.get(method)
            if frame is None:
                checks.append(dict(method=method,scope=scope,reproduced=False,error='Replay method unavailable'));continue
            fresh=scoped(calc,frame,scope);expected=bookdata['sppr_'+scope].set_index('seq')[method].reindex(fresh.index);mask=np.isfinite(fresh)&np.isfinite(expected)
            checks.append(dict(method=method,scope=scope,reproduced=bool(mask.any() and np.array_equal(np.isfinite(fresh),np.isfinite(expected)) and np.allclose(fresh[mask],expected[mask],rtol=2e-7,atol=1e-7)),
                max_absolute_error=float((fresh[mask]-expected[mask]).abs().max()),original_normalized_max_absolute_error=check['max_absolute_error']))
        row=dict(model_id=mid,experiment_settings=SETTINGS,replay_settings=dict(SETTINGS,normalize_DC=False),checks=checks,
            all_differences_reproduced=all(c['reproduced'] for c in checks),
            interpretation='The experiment preserves original-study normalize_DC=True. Each replayed comparison records whether existing saved values are reproduced with raw diet rows (normalize_DC=False); no tolerance is loosened or source model repaired.')
        output.append(row);print(mid,'raw-diet replay',row['all_differences_reproduced'],len(checks),flush=True)
    write_json(ROOT/'verification/saved_workbook_differences.json',output)
if __name__=='__main__':run()
