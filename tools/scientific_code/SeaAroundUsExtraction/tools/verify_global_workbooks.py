"""Independently compare the global XLSX cached values to current CSVs and arithmetic."""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from validate_eez_release import workbook_cells, check_table_cells, check_groups

ROOT = Path(__file__).resolve().parents[1]


def csv_frame(path):
    frame = pd.read_csv(path)
    # A heterogeneous validation value column is text in pandas; the workbook
    # deliberately imports its numeric and boolean entries as typed cells.
    if 'value' in frame:
        def typed(v):
            if isinstance(v, str):
                if v.lower() in ('true', 'false'):
                    return v.lower() == 'true'
                try:
                    return float(v)
                except ValueError:
                    pass
            return v
        frame['value'] = frame['value'].map(typed)
    return frame


def main():
    output = ROOT / 'global_output'
    tables = output / 'tables'
    units = json.loads((tables / 'units.json').read_text(encoding='utf-8'))
    books = list((output / 'regional_calculations').glob('*.xlsx'))
    assert len(books) == len(units)
    expected = {u['unit_id'] for u in units}
    assert {'_'.join(p.stem.split('_')[:2]) for p in books} == expected
    formula_count = 0
    for path in books:
        unit = '_'.join(path.stem.split('_')[:2])
        sheets, count = workbook_cells(path)
        formula_count += count
        source = pd.read_csv(tables / 'regions' / unit / 'species.csv')
        for sheet, csv_name in [('Species','species'),('Commercial','commercial'),('Functional','functional'),('Missing TL','missing_tl'),('Validation','validation')]:
            frame = csv_frame(tables / 'regions' / unit / f'{csv_name}.csv')
            check_table_cells(sheets[sheet], frame)
        assert sheets['Metadata']['B5'] == .1
        for kind in ('commercial','functional'):
            check_groups(source, pd.read_csv(tables / 'regions' / unit / f'{kind}.csv'), kind)
        for i, r in enumerate(source.itertuples(index=False), 2):
            if pd.notna(r.tl):
                assert np.isclose(sheets['Species'][f'U{i}'], r.catch_tonnes * 10 ** (r.tl - 1), rtol=1e-11, atol=1e-6)
    sheets, count = workbook_cells(output / 'PPR_global_summary.xlsx')
    formula_count += count
    assert 'Jensen Comparison' not in sheets
    for sheet, csv_name in [('Summary','global_summary'),('Validation','validation'),('TL Coverage','tl_coverage'),('Ingestion Audit','ingestion_audit')]:
        check_table_cells(sheets[sheet], csv_frame(tables / f'{csv_name}.csv'))
    report = {'workbooks_verified': len(books) + 1, 'formula_count': formula_count,
              'cached_values_match_current_csv': True, 'independent_group_arithmetic': True,
              'formula_errors': 0}
    (output / 'numeric_workbook_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
