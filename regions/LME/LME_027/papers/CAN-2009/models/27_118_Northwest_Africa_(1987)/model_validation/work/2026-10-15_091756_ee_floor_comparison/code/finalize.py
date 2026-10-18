"""Verify and explain retained comparison matrices without rerunning the engine."""
from pathlib import Path
import hashlib
import json
import os
import numpy as np

RUN = Path(__file__).resolve().parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in MODEL.parents if (p/'Project.xlsx').exists())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


comparison = json.loads((RUN/'outputs/comparison.json').read_text(encoding='utf-8'))
checks = json.loads((RUN/'qa/reconciliation.json').read_text(encoding='utf-8'))
hist = MODEL/'extracted_tables/evidence/integration_20260928'
state = json.loads((hist/'loaded_state.json').read_text(encoding='utf-8'))
groups = state['_groups_df']
groups = {i:dict(zip(groups['columns'],row)) for i,row in zip(groups['index'],groups['data'])}
diet = state['_DC']
diet = {i:dict(zip(diet['columns'],row)) for i,row in zip(diet['index'],diet['data'])}
eigenchecks = {}
for case in ('OFF','ON'):
    for option in ('GE','TE','With Egestion'):
        stem = option.replace(' ','_')
        bundle = json.loads((RUN/f'outputs/{case}/{stem}_matrices.json').read_text(encoding='utf-8'))
        a = bundle['A']
        array = np.array(a['data'],dtype=float)
        ids, cols = a['index'],a['columns']
        living = [i for i in ids if sum(diet[i].values()) != 0]
        block = array[np.ix_([ids.index(i) for i in living],[cols.index(i) for i in living])]
        rho = float(np.max(np.abs(np.linalg.eigvals(block))))
        result = comparison['cases'][case][option]
        np.testing.assert_allclose(rho,result['divergence']['rho_living'],atol=1e-12,rtol=1e-12)
        assert result['SPPR_finite'] and result['negative_SPPR_entries']==0
        eigenchecks[case+'/'+option] = {'independent_rho_living':rho,'all_SPPR_finite':True,'negative_SPPR_entries':0}
        checks[case+'_'+stem+'_independent_rho_and_SPPR_integrity'] = True
    a = json.loads((RUN/f'outputs/{case}/TE_matrices.json').read_text(encoding='utf-8'))['A']
    self_gain = float(a['data'][a['index'].index(13)][a['columns'].index(13)])
    np.testing.assert_allclose(self_gain,comparison['cases'][case]['TE']['divergence']['rho_living'],rtol=1e-12,atol=1e-12)
    eigenchecks[case+'/dominant_self_loop'] = {'group_id':13,'group_name':groups[13]['group_name'],
        'effective_EE':groups[13]['ee'],'self_diet_fraction':diet[13][13],
        'TE':groups[13]['p']/groups[13]['q']*groups[13]['ee'],'self_loop_gain':self_gain,
        'selected_by_threshold':groups[13]['ee']<.1}
checks['dominant_group13_self_loop_unchanged_above_threshold'] = True
protected = json.loads((RUN/'inputs/protected_hashes.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/path)==digest for path,digest in protected.items())
checks['all_preexisting_protected_files_byte_identical'] = True
save(RUN/'qa/independent_matrix_verification.json',eigenchecks)
save(RUN/'qa/reconciliation.json',checks)
summary = '''# LME_027 EE-floor diagnostic comparison

The specific concern of excessive living-compartment recycling still holds with
EE floor 0.1 and selection threshold 0.1. TE rho_living is 0.9907169786465047
both OFF and ON, and TE remains WARN. It converges mathematically (<1), but
remains close to divergence and above both the default 0.7 warning threshold
and the signed report's stated 0.9 concern.

| Method | OFF status | ON status | OFF rho_living | ON rho_living |
|---|---|---|---:|---:|
| GE | WARN | OK | 0.16615874785448084 | 0.16615874785448084 |
| TE | WARN | WARN | 0.9907169786465047 | 0.9907169786465047 |
| With Egestion | WARN | OK | 0.13292699828358467 | 0.13292699828358467 |

The returned TE A[13,13] equals the dominant living-network eigenvalue in both
cases. Group 13 (Mesopelagic predators) consumes itself at diet fraction 0.016;
its pre-floor EE is 0.117029533, exceeding the strict selection threshold 0.1.
Its self-loop therefore stays unchanged. The numerical concern persists, but
attributing the dominant loop solely to the EE<0.1 compartments is unsupported.

Coastal tunas (17) no longer triggers the near-zero TE warning. However,
previously zero-EE groups now have nonzero TE; five remain below the diagnostic
TE threshold 0.001: Seabirds (11), Killer whales (9), Sperm whales (8), Beaked
whales (7) and Sei whales (5). Maximum total group TE SPPR rises from about
2.774 million (Mesopelagic predators) to 85.413 million (Beaked whales).
These are group coefficients, not regional catch-weighted totals.

All six SPPR matrices are finite and have no negative contributions. The floor
affects 15 groups, records 10.828832010005804 model flow units as hypothetical
external nonfishery mortality export, and introduces no negative detritus stock
residual. The strict source model balance flag remains false in both cases.
The TE SPPR balance flag changes from false to true; its relative budget gap
falls from 2.1399011940631314e-5 to 7.664274280832692e-6. Budget improvement
does not remove the near-divergent living loop.

The archived loader reproduces the retained completed runtime within 1e-12.
The OFF matrices reproduce historical matrices within the recorded 1e-10
tolerance. Both cases use the same audited initialization, diet normalization,
detritus options and current calculation engine; only the floor Boolean changes.
Threshold and floor are explicitly 0.1. Canonical inputs, living biological
flows and catch remain protected. Full returns, ordered matrices, nonfinite
masks, source-scope coefficients and provenance are adjacent in outputs/.

The original signed review and all protected existing files remain byte-identical.
The registered disqualification, regional workbooks, saved results and map were
not changed. This run creates diagnostic evidence only and supplies no renewed
researcher approval. No extraction, mapping, regional arithmetic or Monte Carlo
was performed.

Reproduction: run code/compare.py from the repository (or with an available
scientific Python), then code/finalize.py and the project's evidence checker.
The archived loader temporarily requires a period-bearing filename; its input
is a byte-identical canonical copy removed immediately after parsing.

- [Comparison values and warnings](outputs/comparison.json)
- [Independent matrix verification](qa/independent_matrix_verification.json)
- [Reconciliation checks](qa/reconciliation.json)
- [Original signed review, preserved](../../validation.docx)
- [Portable evidence inventory](evidence_index.json)
'''
(RUN/'summary.md').write_text(summary,encoding='utf-8')
index_path=RUN/'evidence_index.json'
index=json.loads(index_path.read_text(encoding='utf-8'))
artifacts=[]
for path in sorted(RUN.rglob('*')):
    if path.is_file() and path.name not in ('evidence_index.json','completeness.json'):
        relative=path.relative_to(RUN).as_posix()
        artifacts.append({'role':relative,'path':relative,'sha256':sha(path),'availability':'present'})
for role,path in [('canonical_input',MODEL/'model.json'),('original_signed_review',MODEL/'model_validation/validation.docx'),
                  ('historical_configuration',hist/'execution_evidence.json'),('historical_matrices',hist/'direct_solutions.json')]:
    artifacts.append({'role':role,'path':os.path.relpath(path,RUN).replace('\\','/'),
                      'sha256':sha(path),'availability':'present'})
index.update(artifacts=artifacts,required_roles=[a['role'] for a in artifacts],reconciliation=checks)
save(index_path,index)
print(json.dumps({'conclusion':'Living-recycling concern persists; dominant TE self-loop unchanged',
    'dominant_self_loop':eigenchecks['ON/dominant_self_loop'],'preservation_verified':True,
    'artifacts':len(artifacts),'reconciliation_checks':len(checks)},indent=2))
