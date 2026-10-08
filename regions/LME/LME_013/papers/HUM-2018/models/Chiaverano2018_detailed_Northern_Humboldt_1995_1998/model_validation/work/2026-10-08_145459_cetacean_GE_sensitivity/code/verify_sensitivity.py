from pathlib import Path
import json,hashlib,math,pickle,os,sys
import numpy as np
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists());OUT=RUN/'outputs'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def plain(x):
    if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,np.ndarray):return plain(x.tolist())
    if isinstance(x,np.bool_):return bool(x)
    if isinstance(x,np.integer):return int(x)
    if isinstance(x,(float,np.floating)):
        return float(x) if math.isfinite(x) else {'nonfinite':'NaN' if math.isnan(x) else '+Inf' if x>0 else '-Inf'}
    return x
comparison=load(OUT/'validated_cetacean_comparison.json');summary=load(OUT/'sensitivity_summary.json')
for label,cohort in comparison['cohorts'].items():
    rows=[r for r in comparison['groups'] if label!='strict_cetaceans' or r['strict_cetacean_membership']]
    assert cohort['approved_group_estimates']==0 and all(r['researcher_excluded'] for r in rows)
    assert cohort['mean_GE']==math.fsum(r['GE'] for r in rows)/len(rows)
    by_model={}
    for r in rows:by_model.setdefault(r['model_id'],[]).append(r)
    assert cohort['model_equal_mean_GE']==math.fsum(math.fsum(r['GE'] for r in rr)/len(rr) for rr in by_model.values())/len(by_model)
    for scope in ['all','inner','PP']:
        assert cohort['model_equal_mean_SPPR_GE'][scope]==math.fsum(math.fsum(r['SPPR_GE'][scope] for r in rr)/len(rr) for rr in by_model.values())/len(by_model)
count=0
for r in summary['results']:
    f=OUT/r['scenario']/r['configuration']
    # These pickles were produced by this task from known engine returns.
    report,sppr,A,L=pickle.loads((f/'full_return.pkl').read_bytes())
    assert plain(report)==load(f/'diagnostic_return.json')
    for name,frame in [('SPPR',sppr),('A',A),('L',L)]:
        axes=load(f/(name+'_axes.json'));arr=np.load(f/(name+'.npy'));masks=np.load(f/(name+'_masks.npz'))
        assert np.array_equal(arr,frame.to_numpy(dtype=float),equal_nan=True)
        assert len(axes['rows'])==len(frame.index) and len(axes['columns'])==len(frame.columns)
        assert [v['id'] for v in axes['rows']]==list(frame.index) and [v['id'] for v in axes['columns']]==list(frame.columns)
        assert all(mask.shape==arr.shape for mask in masks.values())
        assert np.array_equal(masks['nan'],np.isnan(arr))
        assert np.array_equal(masks['positive_infinity'],np.isposinf(arr))
        assert np.array_equal(masks['negative_infinity'],np.isneginf(arr))
    neg=load(f/'negative_matrix_entries.json')
    assert len(neg)==sum(int((x.to_numpy(dtype=float)<0).sum()) for x in [sppr,A,L])
    columns=load(f/'SPPR_axes.json')['columns']
    for scope in ['all','inner','PP']:
        cols=[v['id'] for v in columns if scope=='all' or (scope=='inner' and v['trophic_type']!='Import') or (scope=='PP' and v['trophic_type']=='PP')]
        assert math.isclose(r['cetacean_SPPR_GE'][scope],float(sppr.loc[33,cols].sum()),rel_tol=1e-12,abs_tol=1e-9)
    assert r['model_balanced'] and report['model_input']['is_model_balanced']
    assert r['overall_status']==report['status']=='FAIL'
    assert math.isclose(r['PB']/r['QB'],r['target_GE'],rel_tol=1e-12)
    if r['configuration']=='pooled':assert not (sppr.to_numpy(dtype=float)<0).any()
    count+=1
assert count==6
for path,digest in summary['protected_hashes'].items():assert sha(ROOT/path)==digest
for record in comparison['reviewed_models']:
    assert sha(ROOT/record['model_path'])==record['model_sha256']
    assert sha(ROOT/record['region_path'])==record['region_sha256']
assert sha(ROOT/'Project.xlsx')==comparison['project_sha256']
baseline=MODEL/'model_validation/work/2026-10-08_132433_balanced_validation/outputs/pooled/GE'
axes=load(baseline/'SPPR_axes.json');arr=np.load(baseline/'SPPR.npy')
row=next(i for i,v in enumerate(axes['rows']) if v['id']==33)
baseall=float(arr[row,:].sum());basepp=float(arr[row,[i for i,v in enumerate(axes['columns']) if v['trophic_type']=='PP']].sum())
main=next(r for r in summary['results'] if r['scenario']=='strict_model_mean' and r['configuration']=='pooled')
dump(RUN/'qa/verification.json',dict(status='PASS',cohort_means_verified=True,configuration_results_verified=count,
 full_return_matrix_axes_masks_negative_entries_scope_sums_verified=True,
 all_relevant_accepted_files_and_comparator_models_workbooks_unchanged=True,
 baseline_pooled_cetacean_all=baseall,baseline_cetacean_PP_only=basepp,
 main_scenario_pooled_cetacean_all=main['cetacean_SPPR_GE']['all'],
 percent_reduction=100*(1-main['cetacean_SPPR_GE']['all']/baseall),
 grade='All six GE sensitivity diagnostics retain overall FAIL; no scenario adopted.'))
index=OUT/'evidence_index.json'
artifacts=[dict(role='comparison',path='validated_cetacean_comparison.json',sha256=sha(OUT/'validated_cetacean_comparison.json'),availability='present'),
 dict(role='summary',path='sensitivity_summary.json',sha256=sha(OUT/'sensitivity_summary.json'),availability='present'),
 dict(role='verification',path='../qa/verification.json',sha256=sha(RUN/'qa/verification.json'),availability='present')]
for part in ['strict_model_mean','strict_group_mean','broad_model_mean']:
    for p in sorted((OUT/part).rglob('*')):
        if p.is_file():artifacts.append(dict(role='diagnostic_evidence',path=p.relative_to(OUT).as_posix(),sha256=sha(p),availability='present'))
for p in sorted((RUN/'code').rglob('*.py')):
    artifacts.append(dict(role='executed_code',path=os.path.relpath(p,OUT).replace('\\','/'),sha256=sha(p),availability='present'))
dump(index,dict(schema_version=1,run_id=RUN.name,region_id='LME_013',model_id=MODEL.name,
 variant_id='unadopted_cetacean_GE_sensitivity',source_identity=dict(canonical_sha256=summary['input_sha256']),
 computational_input_identity=dict(constructor=summary['constructor'],scenarios=[r['scenario'] for r in summary['results']],
 engine=summary['engine']),methods=['GE'],required_roles=['comparison','summary','verification','diagnostic_evidence','executed_code'],
 reconciliation=dict(cohort_means=True,matrices_masks_axes=True,scope_sums=True,source_preservation=True),artifacts=artifacts))
print('PASS: averages, six complete GE returns, scoped coefficients and unchanged accepted files verified.')
