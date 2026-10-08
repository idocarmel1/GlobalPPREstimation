"""Read-only sensitivity excluding zero-TE consumers from each weighted mean."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def summarize(te, weights):
    assert np.isfinite(te).all() and (te >= 0).all()
    assert np.isfinite(weights).all() and (weights >= 0).all()
    retained = (te > 0) & (weights > 0)
    total = float(weights.sum())
    retained_weight = float(weights[retained].sum())
    return {
        'arithmetic': float(np.average(te[retained], weights=weights[retained])) if retained_weight else None,
        'geometric': float(np.exp(np.average(np.log(te[retained]), weights=weights[retained]))) if retained_weight else None,
        'excluded_weight_fraction': float(weights[te == 0].sum()/total) if total else None,
        'retained_weight': retained_weight,
    }


def main():
    # An omitted zero must affect neither numerator nor denominator.
    example = summarize(np.array([0., .1, .4]), np.array([100., 1., 1.]))
    assert np.isclose(example['geometric'], .2)
    assert np.isclose(example['arithmetic'], .25)
    assert summarize(np.array([0.]), np.array([1.]))['geometric'] is None
    assert summarize(np.array([.2]), np.array([0.]))['geometric'] is None
    previous = {r['ecosystem']: r for r in json.loads((HERE/'geometric_results.json').read_text())}
    results = []
    for original in json.loads((HERE/'results.json').read_text()):
        if not original['mass_balanced']:
            continue
        path = ROOT/'PPREstimation/output/top10'/(original['model']+'.xlsx')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == original['workbook_sha256']
        g = pd.read_excel(path, sheet_name='groups_df')
        g = g[g.group_type.eq('Regular')].copy()
        te = ((g.p/g.q).fillna(1)*(1-g.M0/g.p).fillna(1)).to_numpy()
        rounded = (te < 0) & (te >= -1e-15)
        te[rounded] = 0  # Same documented ETP signed-roundoff handling as prior analysis.
        row = {'ecosystem':original['ecosystem'], 'model':original['model'],
               'consumer_groups':len(g), 'excluded_groups':g.loc[te==0,'group_name'].tolist(),
               'roundoff_clipped_groups':g.loc[rounded,'group_name'].tolist(), 'means':{}}
        for label, weights in [('equal',np.ones(len(g))), ('catch',g['catch'].to_numpy()),
                               ('biomass',g.biomass.fillna(0).to_numpy())]:
            result = summarize(te, weights)
            result['previous_including_zero'] = previous[row['ecosystem']]['means'][label]
            if result['geometric'] is not None:
                assert result['geometric'] <= result['arithmetic']+1e-12
                if result['excluded_weight_fraction'] == 0:
                    assert np.isclose(result['geometric'],result['previous_including_zero']['geometric'])
            row['means'][label] = result
        results.append(row)
    (HERE/'positive_te_results.json').write_text(json.dumps(results,indent=2,allow_nan=False),encoding='utf-8')
    lines = ['# Consumer means excluding TE = 0', '',
             'Read-only sensitivity: consumer groups with TE > 0 only, with weights renormalized after exclusion. Canary Current remains excluded for failed mass balance. Existing source-diet caveats apply. Values below are percentages.', '',
             '| Model | Equal geometric | Catch geometric | Biomass geometric | Excluded consumer groups | Excluded biomass (%) | Excluded catch (%) |',
             '|---|---:|---:|---:|---:|---:|---:|']
    fmt = lambda v: 'Unavailable' if v is None else f'{100*v:.2f}'
    for row in results:
        means = row['means']
        cells = [fmt(means[k]['geometric']) for k in ['equal','catch','biomass']]
        cells += [f"{len(row['excluded_groups'])}/{row['consumer_groups']}",
                  fmt(means['biomass']['excluded_weight_fraction']),fmt(means['catch']['excluded_weight_fraction'])]
        lines.append('| '+row['model']+' | '+' | '.join(cells)+' |')
        print(row['ecosystem'],json.dumps({k:{a:b for a,b in v.items() if a!='previous_including_zero'} for k,v in means.items()}),row['excluded_groups'])
    lines += ['', 'Formula: G = exp(sum_{TE_i>0}(w_i ln TE_i) / sum_{TE_i>0}(w_i)). If no positive weight remains, the mean is unavailable. Positive efficiencies arbitrarily close to zero are retained; no positive cutoff is imposed.', '',
              'The single ETP toothed-whale TE of approximately -3.92e-18 is treated as zero under the same -1e-15 to 0 signed-roundoff rule as the preceding sensitivity. Other negative values cause an error. This rule does not modify production code.', '',
              'These are means conditional on positive transfer efficiency, not means over the entire consumer community. TE=0 can reflect EE=0 rather than missing data, so dropping such consumers changes the scientific quantity. Exact excluded names, weight fractions, corresponding arithmetic means and previous inclusive means are in positive_te_results.json.', '',
              'No production code, workbook or atlas output was changed. Verified renormalization on a known example, zero remaining weight, geometric <= arithmetic, and unchanged values whenever excluded groups carry zero weight.']
    (HERE/'positive_te_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
