"""Promote the completed physical-merge experiment into model-local evidence."""
from pathlib import Path
import hashlib
import json
import os
import shutil

WORK=Path(__file__).resolve().parents[1]
MODEL=WORK.parents[2]
DEST=MODEL/'model_validation/evidence/physical_detritus_merge_20261114'
PREVIOUS=MODEL/'model_validation/evidence/discards_reconciliation_20261114'
POOLED=MODEL/'model_validation/evidence/pooled_detritus_20261114'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def series(d):
    f=d['frame']
    return {i:r[0] for i,r in zip(f['index'],f['data'])}

qa=load(WORK/'qa/independent_physical_merge_verification.json')
assert qa['passed']
assert not DEST.exists(), 'Retained package must not be overwritten.'
for folder in ['inputs','outputs','code','qa']:
    shutil.copytree(WORK/folder,DEST/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
c=load(DEST/'outputs/comparison.json')
provenance=load(DEST/'outputs/provenance.json')
table=[];birds=[];coefs=[]
for s in c['summaries']:
    table.append(f"| {s['method']} | {s['separate_ppr']:.10f} | {s['physical_merge_ppr']:.10f} | +{s['percent_change_vs_separate']:.6f}% | {s['separate_status']} → {s['status']} |")
    b=series(s['seabirds'])
    assert b['name']=='Seabirds'
    birds.append(f"| {s['method']} | {b['separate_sppr']:.6f} | {b['physical_merge_sppr']:.6f} | +{b['sppr_percent_change']:.4f}% |")
    r=load(DEST/f"outputs/{s['method']}_physical_merge_full_return.json")
    d=r['diagnostic']
    info=r['detritus_resolution_info']
    coefs.append(f"- {s['method']}: merged-pool SPPR **{info['x_vec'][0]:.12f}**, recycling b **{info['rho_B']:.12f}**, strict weighted relative gap **{d['balance']['rel_gap']:.3g}**, overall **{d['status']}**.")
max_sppr_difference=max(load(DEST/f"outputs/{m}_physical_merge_full_return.json")['maximum_abs_SPPR_difference_from_attribution_pooling'] for m in ['GE','TE'])
report=f'''# LME_014 physical Discards–Detritus merge

The isolated physical-merge scenario is complete with **EE floor ON at 0.1**. Discards35 and Detritus36 were replaced by one physical pool, retained as group36 and named **Detritus including Discards**. The canonical model was not changed.

## GE/TE comparison

| Method | Separate physical pools | Physically merged pool | Change | Diagnostic status |
|---|---:|---:|---:|---|
{chr(10).join(table)}

Values are source-model total-catch, all-source PPR, not regional LME annual totals. Source units are tonnes per km² for 2020; wet versus dry mass is not explicitly established. No carbon conversion was made. PP-only PPR remains GE **20.8858634579** and TE **60.4869998045**.

The physical merge reproduces the prior attribution-pooling result within numerical tolerance. Maximum absolute SPPR difference after the correct source-column crosswalk is **{max_sppr_difference:.3g}**. For retained recipients, merged source36 equals the previous pooled columns35+36. The two detritus recipient rows are not added together, because each represented a coefficient per unit material.

{chr(10).join(coefs)}

All returned SPPR values are finite and nonnegative at the recorded tolerance. Both strict weighted balance checks pass. Full matrices retain every recipient, including unfished groups. The matrix has 36 runtime recipients and four basal-source columns; only one detritus group remains.

For Seabirds25, the coefficients change more than the fishery total:

| Method | Separate-pool SPPR | Physical-merge SPPR | Change |
|---|---:|---:|---:|
{chr(10).join(birds)}

## What was physically merged

The run restored the audited, source-reconciled **pre-floor** state. It summed the two inherited stocks and extensive flows, summed their prey fractions for every consumer, and combined both natural-detritus-fate and fleet-return recipient columns. The two detritus consumer rows were both zero. After recipient aggregation, both original detritus fate rows were exactly one into the merged pool, so there was no undefined donor-weighting choice. All living biological quantities and total diet consumption were preserved.

Merged runtime biomass is **{c['merged_stock_biomass']:.12f}** in the inherited model's stock units. This is the sum of retained runtime values, not a newly observed stock. PB/QB and GE/GS were derived from the summed flows; source EE was not averaged. Original component source values and missingness remain in the [merge specification](inputs/merge_specification.json).

The floor was then applied exactly once. The affected living groups and hypothetical external mortality sink (**{c['floor_sink_total']:.12f} t/km²/year**) match the separate-pool reference. Recorded fisheries returns (**{c['total_fishery_returns']:.15f} t/km²/year**) enter the merged pool once; total fishery catch and external-removal accounting are preserved. No additional offal or import was introduced.

## Why the negative-stock warning disappears

The merged physical budget after the floor is:

| Term | t/km²/year |
|---|---:|
| Incoming material | {c['merged_inflow']:.12f} |
| Consumption | {c['merged_consumption']:.12f} |
| Calculated stock residual | +{c['merged_stock_residual']:.12f} |

The source model's two reported BA inputs sum to zero; the positive runtime residual remains the reconstruction's calculated closure. It is not a measured accumulation. The former Discards deficit of **−0.20750363203745528** is absorbed into the larger Detritus surplus when their physical budgets are combined. There is no separately represented Discards stock left for the diagnostic to flag.

This is a numerical outcome under the **complete-mixing assumption**. It does not establish that ordinary detritus and fishery heads/guts are interchangeable food or identify the missing source-specific offal supply. The [original Discards reconciliation](../discards_reconciliation_20261114/discards_reconciliation.md) and its source warning remain unchanged. An improved scenario diagnostic does not validate or approve the original model.

## Execution and preservation

Only two fresh diagnostics were run: GE and TE on the physically merged state, using `det_collapse_mode=never` and `det_open_mode=none`. There was no additional attribution-pooling operation. This is a PPR-calculator scenario based on the audited reconstruction; no merged native EwE database run was performed. The separate-pool and [attribution-pooled](../pooled_detritus_20261114/pooled_detritus.md) baselines were reused with their exact code/input identities. The merged pre-floor and effective states were retained; the effective state was reopened and authenticated before the calls.

[GE full return](outputs/GE_physical_merge_full_return.json) · [TE full return](outputs/TE_physical_merge_full_return.json) · [Merge and floor states](outputs/merge_and_floor.json) · [Independent verification](qa/independent_physical_merge_verification.json) · [Comparison data](outputs/comparison.json) · [Execution provenance](outputs/provenance.json) · [Evidence index](evidence_index.json)

No canonical model, source input, researcher DOCX, appendix, regional workbook, Project.xlsx, map, trends or shared code was changed by this task. No scenario was adopted, decision registered, or findings sent to the coordinator.
'''
(DEST/'physical_detritus_merge.md').write_text(report,encoding='utf-8')
artifacts=[]
roles={'outputs/GE_physical_merge_full_return.json':'GE_full_return','outputs/TE_physical_merge_full_return.json':'TE_full_return',
    'outputs/merge_and_floor.json':'merge_and_floor_states','inputs/merge_specification.json':'merge_specification',
    'qa/independent_physical_merge_verification.json':'independent_verification','outputs/provenance.json':'execution_provenance',
    'physical_detritus_merge.md':'comparison_report'}
for p in sorted(DEST.rglob('*')):
    if p.is_file():
        relative=p.relative_to(DEST).as_posix()
        artifacts.append({'role':roles.get(relative,relative),'path':relative,'sha256':sha(p),'availability':'present'})
external=[('canonical_model',MODEL/'model.json'),('source_evidence_index',PREVIOUS/'evidence_index.json'),
    ('pre_floor_reference',PREVIOUS/'outputs/diagnostics/source_exact_returns_to_36/post_returns_before_floor.json'),
    ('separate_effective_reference',PREVIOUS/'outputs/diagnostics/source_exact_returns_to_36/effective_floor_on.json'),
    ('source_initialization',MODEL/'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json'),
    ('source_return_ledger',PREVIOUS/'outputs/source/source_fisheries_ledger.json'),
    ('serialization_helpers',PREVIOUS/'code/run_discard_comparison.py')]
external += [(f'engine_{name}',PREVIOUS/'code/engine'/name) for name in ['PPRCalculator.py','ModelData.py','utils.py']]
for m in ['GE','TE']:
    external.extend([(f'{m}_separate_reference',PREVIOUS/f'outputs/diagnostics/source_exact_returns_to_36/{m}_full_return.json'),
                     (f'{m}_attribution_pooling_reference',POOLED/f'outputs/{m}_pooled_full_return.json')])
for role,p in external:
    artifacts.append({'role':role,'path':Path(os.path.relpath(p,DEST)).as_posix(),'sha256':sha(p),'availability':'present'})
save(DEST/'evidence_index.json',{'schema_version':1,'run_id':WORK.name,'region_id':'LME_014','model_id':MODEL.name,'variant_id':c['variant_id'],
    'source_identity':provenance['inputs'],'computational_input_identity':{'effective_runtime_sha256':provenance['effective_state_sha256']},
    'methods':['GE','TE'],'options':provenance['options'],'artifacts':artifacts,
    'required_roles':['canonical_model','pre_floor_reference','merge_specification','merge_and_floor_states','GE_full_return','TE_full_return','independent_verification','execution_provenance','comparison_report'],
    'reconciliation':{'independent_qa_passed':qa['passed'],'merge_checks_pass':all(c['merge_checks'].values()),
        'floor_checks_pass':all(c['floor_checks'].values()),'direct_checks_pass':all(all(s['checks'].values()) for s in c['summaries']),
        'protected_files_unchanged':load(DEST/'qa/protected_files.json')['all_protected_unchanged']},
    'limits':'Physical-merge scenario, not canonical adoption or regional recalculation. Numerical status does not resolve original source attribution.'})
print(DEST.as_posix())
print('Artifacts:',len(artifacts))
