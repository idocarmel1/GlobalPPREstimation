"""Extend the original consumer TE comparison with total-consumption weights."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    rows = json.loads((HERE / 'results.json').read_text())
    for row in rows:
        if not row['mass_balanced']:
            continue
        path = ROOT / 'PPREstimation/output/top10' / (row['model'] + '.xlsx')
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['workbook_sha256']
        g = pd.read_excel(path, sheet_name='groups_df')
        c = g[g.group_type.eq('Regular')]
        te = (c.p / c.q).fillna(1) * (1 - c.M0 / c.p).fillna(1)
        assert np.isfinite(te).all() and np.isfinite(c.q).all() and (c.q > 0).all()
        # Preserve the original consumer cohort, including TE=0 and signed
        # numerical roundoff; this is not the positive-TE geometric sensitivity.
        row['consumption_weight'] = float(np.average(te, weights=c.q))
        row['consumer_total_consumption'] = float(c.q.sum())
        ratio = float((c.p * c.ee).sum() / c.q.sum())
        assert np.isclose(row['consumption_weight'], ratio, rtol=1e-12, atol=1e-14)
        assert np.isclose(row['consumption_weight'], (c.p-c.M0).sum()/c.q.sum())
        assert np.isclose(row['equal_weight'], te.mean())
        assert np.isclose(row['biomass_weight'], np.average(te, weights=c.biomass.fillna(0)))
        if c['catch'].sum() > 0:
            assert np.isclose(row['catch_weight'], np.average(te, weights=c['catch']))
        else:
            assert row['catch_weight'] is None
        print(row['ecosystem'], f"consumption TE = {100*row['consumption_weight']:.4f}%")
    (HERE / 'consumption_results.json').write_text(json.dumps(rows, indent=2, allow_nan=False), encoding='utf-8')
    lines = ['# Original comparison with consumption weights', '',
             'Consumer-only arithmetic means, including zero-TE consumers. Q is total consumption (biomass × Q/B), not Q/B alone. Consumption-weighted TE = sum(Q_i TE_i)/sum(Q_i) = sum(P_i EE_i)/sum(Q_i). Input hashes and the original three means were verified against the saved workbooks.', '',
             '| Model | Equal | Catch | Biomass | Consumption | Trophic: cycles removed | Trophic: cycles retained |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        if not row['mass_balanced']:
            lines.append('| '+row['model']+' | '+' | '.join(['Excluded']*6)+' |')
            continue
        values = [row[k] for k in ['equal_weight','catch_weight','biomass_weight','consumption_weight']]
        values += [row['trophic_project_cycle_removal_sensitivity']['geometric'], row['trophic_EwE_cycles_off']['geometric']]
        lines.append('| '+row['model']+' | '+' | '.join('Unavailable' if v is None else f'{100*v:.2f}' for v in values)+' |')
    lines += ['', 'All table entries are percentages. The trophic columns are unchanged geometric summaries of level-II–IV flow efficiencies, with the cycle conventions documented in methodology.md. They are different statistics from consumer-weighted means.', '',
              'Canary Current remains excluded for failed underlying model mass balance. All original source/model caveats apply, especially substantial source-diet normalization in Eastern tropical Pacific. Missing catch means no catch in the available model input. Thailand is the 1980 payload despite its inherited 1963 filename.', '',
              'This is a read-only analysis. No production code, model workbook, or atlas output was changed.']
    (HERE / 'consumption_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
