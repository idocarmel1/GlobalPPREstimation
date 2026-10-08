"""Compare source-backed correction proposals; never write accepted model inputs.

Run with the project's scientific Python environment. xlrd is needed to read the
original supplement; an optional --xlrd-path supplies a temporary reader location.
All experimental values exist only in independent ModelData instances.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import warnings

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--xlrd-path')
args = parser.parse_args()
if args.xlrd_path:
    sys.path.insert(0, args.xlrd_path)
import xlrd

RUN = Path(__file__).resolve().parents[1]
MODEL = Path(__file__).resolve().parents[4]
REPO = next(p for p in MODEL.parents if (p / 'Project.xlsx').exists())
SOURCES = MODEL.parents[1] / 'sources'
sys.path.insert(0, str(REPO / 'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator

OUT = RUN / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

protected = [MODEL / 'model.json', MODEL / 'model_notes.md',
             MODEL / 'model_validation/validation.docx',
             MODEL / 'model_validation/human_validation_tests.ipynb',
             SOURCES / 'Supplementary material revised and final.xls',
             SOURCES / '1-s2.0-S0079661117303312-main.pdf']
before = {str(p.relative_to(REPO)): sha(p) for p in protected}
book = xlrd.open_workbook(SOURCES / 'Supplementary material revised and final.xls',
                          formatting_info=True)
A, B, C, H = [book.sheet_by_index(i) for i in [1, 2, 3, 8]]
P = np.array([A.cell_value(r, 2) * A.cell_value(r, 3) for r in range(5, 40)])
Q = np.array([A.cell_value(r, 2) * A.cell_value(r, 4)
              if isinstance(A.cell_value(r, 4), (float, int)) else 0.
              for r in range(5, 40)])
EE = np.array([A.cell_value(r, 7) for r in range(5, 44)])
GS = np.array([1 - A.cell_value(r, 6)
               if isinstance(A.cell_value(r, 6), (float, int)) else 0.
               for r in range(5, 40)])
landings = np.array([sum(A.cell_value(r, c) or 0. for c in [8, 9])
                     for r in range(5, 40)])
discards = np.array([sum(A.cell_value(r, c) or 0. for c in [10, 11])
                     for r in range(5, 40)])
dc = np.array([[B.cell_value(r, c) or 0. for r in range(3, 42)]
               for c in range(1, 40)])
imports = np.array([B.cell_value(42, c) or 0. for c in range(1, 40)])
fate = np.array([[C.cell_value(r, c) or 0. for c in range(2, 6)]
                 for r in range(3, 42)])
q_all = np.r_[Q, np.zeros(4)]
def normalized(d):
    sums = d.sum(axis=1) + imports
    return d / np.where(sums == 0., 1., sums)[:, None]

old_diet = dc.copy()
old_diet[6, :] = 0.
old_diet[6, [3, 4, 35]] = [.68, .17, .15]
reconstruction = []
for code, group in [(4, 1), (7, 4), (8, 5), (9, 6)]:
    col = next(c for c in range(2, H.ncols) if H.cell_value(3, c) == code)
    coefficient = H.cell_value(13, col)
    reconstruction.append({'source_cell': f'{xlrd.formula.colname(col)}14',
        'producer_code': code, 'prey_group_seq': group,
        'Acp': coefficient, 'Q_prey': Q[group-1], 'Q_jellyfish': Q[6],
        'diet_from_Acp_times_Qprey_over_Qjellyfish':
            coefficient * Q[group-1] / Q[6] if Q[group-1] else None,
        'interpretation': 'Zero direct link' if coefficient == 0 else
            'Singleton living consumer-prey link including physiological partitioning'})

settings = dict(underdetermined=True, zero_catch=True, zero_biomass_accum=False,
                default_gs=True, weight_flow=1., weight_guess=1.,
                normalize_DC=True, DC_tol=.001)
scenarios = [
    ('original', False, None, False, False),
    ('article_landings_only_fixed_discards', False, 1.4, False, False),
    ('article_landings_only_scaled_discards', False, 1.4, True, False),
    ('production_matrix_diet_only', True, None, False, False),
    ('matrix_diet_article_landings_fixed_discards', True, 1.4, False, False),
    ('matrix_diet_article_landings_scaled_discards', True, 1.4, True, False),
    ('matrix_diet_article_landings_fixed_discards_reestimate_EE', True, 1.4, False, True),
    ('matrix_diet_article_landings_scaled_discards_reestimate_EE', True, 1.4, True, True),
]
results, residual_rows = [], []
for label, use_old, new_landing, scale_discard, reestimate in scenarios:
    d = old_diet.copy() if use_old else dc.copy()
    L, D, efficiencies = landings.copy(), discards.copy(), EE.copy()
    if new_landing is not None:
        if scale_discard:
            D[8] *= new_landing / L[8]
        L[8] = new_landing
    predation = normalized(d).T @ q_all
    if reestimate:
        efficiencies[8] = (predation[8] + L[8] + D[8]) / P[8]
    native_rows = []
    # Source pool equations: consumption = EE * inflow; unused material
    # follows Table C; discard returns enter offal through fleet routing.
    living_to_pools = (P * (1-efficiencies[:35]) + Q*GS) @ fate[:35]
    living_to_pools[1] += D.sum()
    pool_inflow = np.linalg.solve(np.eye(4) - fate[35:].T @
                                 np.diag(1-efficiencies[35:]), living_to_pools)
    steady_inflow = np.linalg.solve(np.eye(4) - fate[35:].T,
                                   living_to_pools - fate[35:].T @ predation[35:])
    steady_pool_rows = [{'group_seq':j+36, 'inflow':float(steady_inflow[j]),
        'predation':float(predation[j+35]),
        'reestimated_EE':float(predation[j+35]/steady_inflow[j]),
        'unutilized_flow':float(steady_inflow[j]-predation[j+35])}
        for j in range(4)]
    for j in range(4):
        native_rows.append({'group_seq': j+36, 'inflow': float(pool_inflow[j]),
            'predation': float(predation[j+35]), 'source_EE': float(efficiencies[j+35]),
            'EE_implied_by_inflow_and_predation': float(predation[j+35]/pool_inflow[j]),
            'utilization_residual': float(predation[j+35]-pool_inflow[j]*efficiencies[j+35])})
    for compensate in [True, False]:
        m = ModelData(str(MODEL/'model.json'))
        if use_old:
            m.DC.loc[7, :] = 0.
            m.DC.loc[7, [4, 5, 36]] = [.68, .17, .15]
        m.groups_data.loc[9, 'catch'] = L[8] + D[8]
        if reestimate:
            m.groups_data.loc[9, 'ee'] = efficiencies[8]
            m.groups_data.loc[9, 'M0'] = P[8] * (1-efficiencies[8])
        with warnings.catch_warnings(record=True) as notices:
            calc = PPRCalculator.from_modeldata(m, **settings,
                balance_BA_after_DC_normalization=compensate)
        balanced, production, consumption = calc.is_model_balanced()
        living = m.groups_data.index[m.groups_data.trophic_info.isin(['Regular', 'PP'])]
        failures = [int(i) for i in production.index
                    if not np.isclose(production[i], calc.p[i])]
        rec = {'scenario': label, 'runtime_BA_compensation': compensate,
            'balanced': bool(balanced), 'failing_group_seqs': failures,
            'sardine_landings': float(L[8]), 'sardine_discards': float(D[8]),
            'sardine_total_removals': float(L[8]+D[8]),
            'sardine_EE': float(efficiencies[8]),
            'living_max_abs_BA': float(calc.growth.loc[living].abs().max()),
            'warnings': [str(w.message) for w in notices],
            'native_pool_budget_with_source_EE': native_rows,
            'native_pool_budget_with_reestimated_EE_zero_BA': steady_pool_rows,
            'sardine_M0': float(calc.M0[9]),
            'direct_Q_identity_max_residual': float((calc.q-calc.p-calc.egestion-calc.respiration).abs().max())}
        results.append(rec)
        for i in living:
            residual_rows.append({'scenario': label, 'runtime_BA_compensation': compensate,
                'group_seq': int(i), 'group_name': calc.seq2name[i],
                'production': float(calc.p[i]), 'predation': float(calc.predation[i]),
                'M0': float(calc.M0[i]), 'catch': float(calc.catch[i]),
                'BA': float(calc.growth[i]), 'residual': float(production[i]-calc.p[i]),
                'percent_residual': float(100*(production[i]-calc.p[i])/calc.p[i])})
    print(label, 'EE=',efficiencies[8], 'removals=',L[8]+D[8],
          'balanced/no BA compensation=',results[-1]['balanced'],
          'failures=',results[-1]['failing_group_seqs'])

after = {str(p.relative_to(REPO)): sha(p) for p in protected}
assert before == after, 'Protected inputs changed during analysis.'
report = {'scope': 'Unadopted correction proposals; no SPPR calculation or source edits.',
          'settings': settings, 'protected_input_hashes': before,
          'protected_inputs_unchanged': True,
          'matrix_diet_reconstruction': reconstruction,
          'source_sardine_discard_to_landings_ratio': float(discards[8]/landings[8]),
          'scenarios': results}
(OUT/'correction_scenarios.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
with (OUT/'living_group_residuals.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(residual_rows[0]));writer.writeheader();writer.writerows(residual_rows)
print('Saved', OUT/'correction_scenarios.json')
