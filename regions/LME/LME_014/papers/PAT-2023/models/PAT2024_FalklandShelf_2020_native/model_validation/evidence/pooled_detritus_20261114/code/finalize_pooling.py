"""Package the bounded pooling comparison and authenticate portable evidence."""
from pathlib import Path
import hashlib
import json
import os
import shutil

WORK=Path(__file__).resolve().parents[1]
MODEL=WORK.parents[2]
DEST=MODEL/'model_validation/evidence/pooled_detritus_20261114'
PREVIOUS=MODEL/'model_validation/evidence/discards_reconciliation_20261114'

def load(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

assert (WORK/'qa/display_name_correction.json').exists()
assert (WORK/'qa/independent_pooling_verification.json').exists()
assert not DEST.exists(), 'Do not overwrite a retained package.'
for folder in ['code','outputs','qa']:
    shutil.copytree(WORK/folder,DEST/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
comparison=load(DEST/'outputs/comparison.json')
summaries=comparison['summaries']
rows='\n'.join(f"| {s['method']} | {s['separate_ppr']:.10f} | {s['pooled_ppr']:.10f} | +{s['percent_change']:.6f}% | {s['status']} |" for s in summaries)
bird_rows=[]
for method in ['GE','TE']:
    record=load(DEST/f'outputs/{method}_pooled_full_return.json')
    frame=record['group_changes']
    for group,row in zip(frame['index'],frame['data']):
        item=dict(zip(frame['columns'],row))
        if item['name']=='Seabirds':
            bird_rows.append(f"| {method} | {item['separate_sppr']:.6f} | {item['pooled_sppr']:.6f} | +{item['sppr_percent_change']:.4f}% |")
assert len(bird_rows)==2
report=f'''# LME_014 pooled-detritus sensitivity

Pooling changes source-model total-catch PPR by only **+0.01846% (GE)** and **+0.00691% (TE)** relative to the source-reconciled separate-pool calculation. Both results remain **WARN**. EE floor is **ON at 0.1** in both configurations.

## Matched comparison

Discards (35) is already classified as DET, alongside Detritus (36). This experiment changes the existing calculator option from `det_collapse_mode=never` to `always`, retaining `det_open_mode=none`. It uses the exact prior effective state, including independently verified fishery returns to Detritus36, and the same pinned engine. The floor was not applied again. The two separate-pool results are reused; only the pooled GE and TE calls are new.

| Method | Separate pools | Pooled attribution | Change | Overall status |
|---|---:|---:|---:|---|
{rows}

These are source-model catch-weighted, all-source PPR values, not regional LME annual totals. Source mass is reported as tonnes per km² for 2020; wet versus dry mass is not explicit. No carbon conversion was made. PP-only PPR is unchanged: GE 20.8858634579 and TE 60.4869998045. [Full comparison](outputs/comparison.json)

## What pooling changes

The calculator sums the two detritus basis contributions, solves one scalar `a/(1-b)`, and applies it to both original source columns. It preserves group identities, consumer diets, physical flows and the A/L operators. This is pooled SPPR attribution, not a physical rewrite of the source Ecopath model.

| Method | Separate Discards SPPR | Separate Detritus SPPR | Shared pooled SPPR |
|---|---:|---:|---:|
| GE | 0 | 1.091558565747 | 1.091817694021 |
| TE | 0 | 0.941069101163 | 0.941071225662 |

Pooling therefore assigns a positive PPR origin to consumption through the Discards pathway. The effect is larger for some consumers than for total fishery PPR. For Seabirds:

| Method | Separate-pool SPPR | Pooled SPPR | Change |
|---|---:|---:|---:|
{chr(10).join(bird_rows)}

The actual pooled recycling coefficients are GE `collapse_b=0.0390868932624` and TE `collapse_b=0.00146962581595`. Diagnostic `divergence.b` deliberately retains the pre-pooling spectral radius; it should not be substituted for those pooled coefficients. Complete values and identities are retained in each full return.

## The stock residual remains a source question

The unchanged physical budgets sum to inflow **{comparison['aggregate_inflow']:.9f}**, consumption **{comparison['aggregate_consumption']:.9f}**, and net residual **+{comparison['aggregate_residual']:.9f} t/km²/year**. Aggregating those budgets would hide the individual Discards deficit inside the large Detritus surplus. It would not identify new fishery-discard or processing-offal supply.

The actual pooling option keeps Discards35's **−0.20750363203745528 t/km²/year** stock residual visible. Both methods retain this warning, pass strict weighted PPR balance with zero reported relative gap, and return finite SPPR matrices without negative entries. Their physical runtime state is unchanged. All non-detritus source columns, including PP and imports, are unchanged.

The original paper's heads-and-guts feeding mechanism does not establish that ordinary detritus is a substitute for fishery offal. Pooling is useful as a sensitivity assumption, showing that the total model-catch PPR is insensitive here. It does not resolve the missing source attribution or justify removing the warning. The earlier [Discards reconciliation](../discards_reconciliation_20261114/discards_reconciliation.md) retains the native model and paper evidence.

## Evidence and preservation

[GE full return](outputs/GE_pooled_full_return.json) · [TE full return](outputs/TE_pooled_full_return.json) · [Independent verification](qa/independent_pooling_verification.json) · [Execution provenance](outputs/provenance.json) · [Evidence index](evidence_index.json)

The model, source inputs, researcher DOCX, appendix, regional workbooks and retained baseline results were preserved. No Project.xlsx, map, trends or shared code writes were made. No decision was registered and no findings were sent to the coordinator. A summary-only group-name alignment issue was corrected by verified IDs before handoff; all numeric outputs and direct diagnostics were unchanged, with the correction and exact executed runner retained.
'''
(DEST/'pooled_detritus.md').write_text(report,encoding='utf-8')
artifacts=[]
for p in sorted(DEST.rglob('*')):
    if p.is_file():
        role={'outputs/GE_pooled_full_return.json':'GE_full_return','outputs/TE_pooled_full_return.json':'TE_full_return',
              'qa/independent_pooling_verification.json':'independent_verification','outputs/provenance.json':'execution_provenance',
              'pooled_detritus.md':'comparison_report'}.get(p.relative_to(DEST).as_posix(),p.relative_to(DEST).as_posix())
        artifacts.append({'role':role,'path':p.relative_to(DEST).as_posix(),'sha256':sha(p),'availability':'present'})
external=[('canonical_model',MODEL/'model.json'),('prior_evidence_index',PREVIOUS/'evidence_index.json'),
          ('effective_state',PREVIOUS/'outputs/diagnostics/source_exact_returns_to_36/effective_floor_on.json'),
          ('source_initialization',MODEL/'model_validation/evidence/ee_floor_on_review/initialization_and_floor.json'),
          ('source_return_ledger',PREVIOUS/'outputs/source/source_fisheries_ledger.json'),
          ('serialization_helpers',PREVIOUS/'code/run_discard_comparison.py')]
external += [(f'{m}_separate_full_return',PREVIOUS/f'outputs/diagnostics/source_exact_returns_to_36/{m}_full_return.json') for m in ['GE','TE']]
external += [(f'engine_{n}',PREVIOUS/'code/engine'/n) for n in ['PPRCalculator.py','ModelData.py','utils.py']]
for role,p in external:
    artifacts.append({'role':role,'path':Path(os.path.relpath(p,DEST)).as_posix(),'sha256':sha(p),'availability':'present'})
save(DEST/'evidence_index.json',{'schema_version':1,'run_id':WORK.name,'region_id':'LME_014','model_id':MODEL.name,
    'variant_id':'source_exact_returns_to_36_pooled_attribution_ee_floor_on',
    'source_identity':{'prior_evidence_index_sha256':sha(PREVIOUS/'evidence_index.json')},
    'computational_input_identity':{'canonical_sha256':sha(MODEL/'model.json'),'effective_state_sha256':sha(external[2][1])},
    'methods':['GE','TE'],'options':{'use_ee_floor':True,'ee_floor':.1,'det_collapse_mode':'always','det_open_mode':'none'},
    'required_roles':['GE_full_return','TE_full_return','independent_verification','execution_provenance','comparison_report','canonical_model','effective_state','GE_separate_full_return','TE_separate_full_return'],
    'artifacts':artifacts,'reconciliation':{'protected_files_unchanged':load(DEST/'qa/protected_files.json')['unchanged'],
        'all_direct_checks_pass':all(all(s['checks'].values()) for s in summaries)},
    'limits':'Focused SPPR attribution sensitivity, not physical source-model merge, regional recalculation or researcher adoption.'})
print(DEST.as_posix())
print(f'Indexed artifacts: {len(artifacts)}')
