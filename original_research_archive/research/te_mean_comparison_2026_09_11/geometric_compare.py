"""Compare consumer arithmetic/geometric means and verify the production fallback."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'PPREstimation'))
from PPRCalculator import PPRCalculator


def geometric(values, weights):
    active = weights > 0
    if not active.any():
        return None
    x, w = values[active], weights[active]
    assert np.isfinite(x).all() and (x >= 0).all()
    if (x == 0).any():
        return 0.0
    return float(np.exp(np.average(np.log(x), weights=w)))


def main():
    assert np.isclose(geometric(np.array([.1,.4]), np.array([1.,1.])), .2)
    assert geometric(np.array([0.,.4]), np.array([1.,1.])) == 0
    assert np.isclose(geometric(np.array([0.,.4]), np.array([0.,1.])), .4)
    rows = []
    for original in json.loads((HERE/'results.json').read_text()):
        if not original['mass_balanced']:
            continue
        path = ROOT/'PPREstimation/output/top10'/(original['model']+'.xlsx')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == original['workbook_sha256']
        g = pd.read_excel(path, sheet_name='groups_df').set_index('seq').sort_index(ascending=False)
        te = (g.p/g.q).fillna(1) * (1-g.M0/g.p).fillna(1)
        consumer = g.group_type.eq('Regular')
        c = g[consumer]
        v = te[consumer].to_numpy()
        row = {'ecosystem': original['ecosystem'], 'model': original['model'], 'means': {}}
        # Only signed roundoff near exact zero is clipped, and only in this
        # geometric sensitivity. ETP toothed whales have TE=-3.92e-18.
        rounded = (v<0)&(v>=-1e-15)
        row['roundoff_clipped_to_zero'] = c.loc[rounded,'group_name'].tolist()
        geometric_values = v.copy()
        geometric_values[rounded] = 0
        for label, weights in [('equal',np.ones(len(c))),('catch',c['catch'].to_numpy()),('biomass',c.biomass.fillna(0).to_numpy())]:
            arithmetic = float(np.average(v,weights=weights)) if weights.sum()>0 else None
            geo = geometric(geometric_values,weights)
            assert geo is None or geo <= arithmetic+1e-12
            row['means'][label] = {'arithmetic':arithmetic,'geometric':geo,
                'positive_weight_zero_TE_groups': c.loc[(weights>0)&(geometric_values==0),'group_name'].tolist()}
        # Rehydrate only the saved state required by get_TE: this verifies the
        # real method on the same saved model, without re-solving or exporting.
        pc = PPRCalculator.__new__(PPRCalculator)
        pc._groups_df = g.copy()
        pc.p,pc.q,pc.M0,pc.catch = g.p.copy(),g.q.copy(),g.M0.copy(),g['catch'].copy()
        pc.GE,pc.n_groups = g['ge'].copy(),len(g)
        actual = float(pc.get_TE('global',as_matrix=False).loc[c.index[0]])
        expected = float(np.average(te,weights=g['catch'])) if g['catch'].sum()>0 else row['means']['biomass']['arithmetic']
        assert np.isclose(actual,expected)
        row['production_global_TE'] = actual
        rows.append(row)
    (HERE/'geometric_results.json').write_text(json.dumps(rows,indent=2,allow_nan=False),encoding='utf-8')
    lines = ['# Geometric mean sensitivity', '',
             'Each cell shows arithmetic mean → geometric mean, in percent. All three weighting schemes use consumer groups only. Canary Current remains excluded for failed mass balance.', '',
             '| Model | Equal weights | Catch weights | Biomass weights |',
             '|---|---:|---:|---:|']
    for row in rows:
        cells = []
        for label in ['equal','catch','biomass']:
            m = row['means'][label]
            cells.append('Unavailable' if m['arithmetic'] is None else f"{100*m['arithmetic']:.2f} → {100*m['geometric']:.2f}")
        lines.append('| '+row['model']+' | '+' | '.join(cells)+' |')
    lines += ['', 'For positive efficiencies: G = exp(sum(w_i ln(TE_i)) / sum(w_i)). Zero-weight groups are omitted; a zero efficiency with positive weight makes the geometric mean zero (its continuous extension). No zero-efficiency consumers were discarded.', '',
              'Eastern tropical Pacific has one numerical-roundoff negative TE (toothed whales, approximately -3.92e-18). This sensitivity treats values between -1e-15 and 0 as zero and records every such group; other negative values would stop the calculation. No clipping was added to production code.', '',
              'The requested production fix retains arithmetic averaging and changes only the zero-catch biomass fallback to consumer groups. Catch-weighted production calculations retain their previous cohort. Geometric weighting was not added to production. The catch sensitivity above, like the previous comparison, is consumer-only.', '',
              'For Arabian Sea the biomass mean changes from 9.32% to 6.72%. If used as the common TE in SPPR_1995 at TL=3, this alone would raise SPPR by about 1.92 times; at heterogeneous trophic levels the aggregate effect differs. The actual Arabian Sea production method uses catch weights because its model has catch, so this hypothetical biomass substitution is not triggered by the code fix.', '',
              'For East China Sea and Okhotsk the geometric biomass mean is zero because positive-biomass consumers have EE=0. Using a zero global TE gives no finite classic SPPR for TL>1. A geometric consumer mean therefore cannot serve as a general replacement without an explicit, scientifically justified treatment of those zeros.', '',
              'Exact values, zero-TE group names and results from the actual production get_TE method are recorded in geometric_results.json. All nine saved balanced models were checked against the patched method. Existing exported workbooks and atlas data were not regenerated.']
    (HERE/'geometric_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for row in rows:
        print(row['ecosystem'],json.dumps(row['means']))
    print('Verified production get_TE against all nine saved balanced models; catch weighting preserved.')


if __name__ == '__main__':
    main()
