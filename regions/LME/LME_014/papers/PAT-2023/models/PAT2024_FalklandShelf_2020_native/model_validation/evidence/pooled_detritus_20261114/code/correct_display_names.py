"""Correct a summary-only positional label issue by verified group IDs; no solves."""
from pathlib import Path
import importlib.util
import json
import hashlib
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pool_runner',HERE/'code/run_pooling.py')
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
helper=runner.helper
changes=[]
for method in ['GE','TE']:
    path=HERE/f'outputs/{method}_pooled_full_return.json'
    record=runner.load(path)
    names=record['runtime_after']['seq2name']
    frame=record['group_changes']
    before=frame.drop(columns='name').copy()
    scientific_before=helper.encode({k:record[k] for k in ['diagnostic','SPPR','A','L','runtime_after','weighted_budget']})
    for group in frame.index:
        if frame.at[group,'name']!=names[group]:
            changes.append({'method':method,'group_id':int(group),'old_label':frame.at[group,'name'],'correct_label':names[group]})
        frame.at[group,'name']=names[group]
    assert frame.drop(columns='name').equals(before)
    assert scientific_before==helper.encode({k:record[k] for k in ['diagnostic','SPPR','A','L','runtime_after','weighted_budget']})
    helper.save(path,record)
comparison=runner.load(HERE/'outputs/comparison.json')
for summary in comparison['summaries']:
    corrected=runner.load(HERE/f"outputs/{summary['method']}_pooled_full_return.json")
    summary['top_catch_ppr_changes']=corrected['group_changes'].sort_values('catch_ppr_delta',ascending=False).head(8)
helper.save(HERE/'outputs/comparison.json',comparison)
provenance=runner.load(HERE/'outputs/provenance.json')
provenance['executed_runner']={'path':'code/run_pooling_executed.py','sha256':runner.sha(HERE/'code/run_pooling_executed.py')}
provenance['reproduction_runner']={'path':'code/run_pooling.py','sha256':runner.sha(HERE/'code/run_pooling.py'),'difference':'Explicit DataFrame index ensures names align with group IDs in group_changes presentation.'}
provenance['postprocessing']={'path':'code/correct_display_names.py','sha256':runner.sha(Path(__file__)),'solver_calls':0,'scientific_arrays_and_diagnostics_unchanged':True}
helper.save(HERE/'outputs/provenance.json',provenance)
helper.save(HERE/'qa/display_name_correction.json',{'reason':'Positional labels were combined with ID-indexed pandas Series without explicit DataFrame index. Only display names corrected by verified IDs; no numeric value or diagnostic changed.','changes':changes,'new_solver_calls':0,'scientific_arrays_and_diagnostics_unchanged':True})
print('Display names corrected; zero solver calls; all numeric outputs preserved.')
