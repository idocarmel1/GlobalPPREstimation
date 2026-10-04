"""Read-only extended source/import/workbook verification; no model mutation."""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json
import openpyxl

R = Path(__file__).resolve().parent
N = R / 'resolved_native'
E = R / 'evidence'
snap = json.loads((E / 'supplement_cells.json').read_text(encoding='utf-8'))
sheet = {s['name']: s for s in snap['sheets']}
cells = {name: {c['address']: c for c in s['cells']} for name, s in sheet.items()}
x = json.loads((N / 'extraction.json').read_text(encoding='utf-8'))
m = json.loads((N / 'model.json').read_text(encoding='utf-8'))
prior = json.loads((N / 'ROUND_TRIP_CHECKS.json').read_text(encoding='utf-8'))
checks = {k: v for k, v in prior['exact_checks'].items() if not k.startswith('extended.')}

def check(label, ok):
    checks['extended.' + label] = bool(ok)

def num(a, b):
    if a is None or b is None:
        return a is None and b is None
    try:
        return Decimal(str(a)) == Decimal(str(b))
    except Exception:
        return False

def value(name, r, c):
    return sheet[name]['values'][r - 1][c - 1]

def loadcsv(name):
    return list(csv.reader((N / name).open(encoding='utf-8', newline='')))

A = 'Table A-resolved parameters'
B = 'Table B-resolved diet'
C = 'Table C-resolved detritus fate'
fields = [(3, 'biomass', 'biomass'), (4, 'pb', 'pb'), (5, 'qb', 'qb'),
          (6, 'pq', 'ge'), (7, 'ae', None), (8, 'ee', 'ee')]
land = loadcsv('Landings.csv')
discard = loadcsv('Discards.csv')
fate = loadcsv('Detritus_fate.csv')
wb = openpyxl.load_workbook(N / 'reconstructed.xlsx', data_only=False)
vector = list(csv.DictReader((N / 'GROUP_CATCH_BIOMASS.csv').open(encoding='utf-8', newline='')))
fleet_fate = json.loads((N / 'FLEET_DETRITUS_FATE.json').read_text(encoding='utf-8'))

for n in range(1, 40):
    g = x['groups'][n - 1]
    canonical = m['group'][n - 1]
    r = n + 5
    check(f'source.id.{n}', num(value(A, r, 1), n))
    check(f'source.name.{n}', value(A, r, 2) == g['name'] == canonical['group_name'])
    for c, field, native_field in fields:
        raw = value(A, r, c)
        check(f'source.parameter.{n}.{field}', num(raw, g[field]))
        if native_field:
            observed = canonical[native_field]
            check(f'source.canonical.{n}.{native_field}', observed == '-9999' if raw is None else num(raw, observed))
    ae = value(A, r, 7)
    gs = canonical['gs']
    check(f'source.GS_complement.{n}', gs == '-9999' if ae is None else Decimal(gs) == Decimal(1) - Decimal(str(ae)))
    for prey in range(1, 40):
        raw = value(B, prey + 3, n + 1)
        check(f'source.diet.{n}.{prey}', num(raw, x['diet'][str(n)][str(prey)]))
        check(f'source.diet_name.{n}.{prey}', value(B, prey + 3, 1) == x['groups'][prey - 1]['name'])
    imported = value(B, 43, n + 1)
    check(f'source.import.{n}', num(imported, x['diet'][str(n)]['import']) and num(imported, canonical['diet_imp']))
    for kind, rows, table, source_columns in [('landings', land, 'Catch', [9, 10]), ('discards', discard, 'Discards', [11, 12])]:
        check(f'{kind}.identity.{n}', rows[n][1] == g['name'] == wb[table].cell(n + 1, 2).value)
        vals = []
        for c, f in zip(source_columns, x['fleets']):
            raw = value(A, r, c)
            output_col = x['fleets'].index(f) + 2
            check(f'source.{kind}.{n}.{f}', num(raw, x[kind][str(n)][f]))
            check(f'CSV.{kind}.{n}.{f}', num(raw, rows[n][output_col]))
            check(f'workbook.{kind}.{n}.{f}', float(raw) == wb[table].cell(n + 1, output_col + 1).value)
            vals.append(Decimal(str(raw)))
        total = sum(vals)
        check(f'CSV.{kind}.total.{n}', num(total, rows[n][4]))
        check(f'workbook.{kind}.total.{n}', float(total) == wb[table].cell(n + 1, 5).value)
    total_catch = sum(Decimal(str(value(A, r, c))) for c in [9, 10, 11, 12])
    check(f'canonical.total_removals.{n}', num(total_catch, canonical['export']))
    check(f'vector.identity.{n}', vector[n - 1]['group_name'] == g['name'])
    for c, key in [(3, 'biomass_t_km2'), (9, 'landings_artisanal_t_km2_y'),
                   (10, 'landings_commercial_t_km2_y'), (11, 'discards_artisanal_t_km2_y'),
                   (12, 'discards_commercial_t_km2_y')]:
        raw = value(A, r, c)
        check(f'vector.source.{n}.{key}', vector[n - 1][key] == '' if raw is None else num(raw, vector[n - 1][key]))
    check(f'vector.total_removals.{n}', num(total_catch, vector[n - 1]['catch_total_t_km2_y']))
    for c, destination in enumerate(['Anchovy eggs', 'Fishery offal', 'Pelagic detritus', 'Benthic detritus', 'Export'], 3):
        raw = value(C, n + 3, c)
        check(f'source.fate.{n}.{destination}', num(raw, x['detritus_fate'][str(n)][destination]))
        check(f'CSV.fate.{n}.{destination}', num(raw, fate[n][c - 1]))
        check(f'workbook.fate.{n}.{destination}', float(raw) == wb['Fate'].cell(n + 1, c).value)

# Fleet biology and diet are unavailable, not numeric zero or imputed stock data.
for n in [40, 41]:
    r = n + 5
    check(f'fleet.id.{n}', num(value(A, r, 1), n))
    check(f'fleet.name.{n}', value(A, r, 2) == fleet_fate['source_fleet_nodes'][str(n)])
    for c in range(3, 13):
        check(f'fleet.native_blank.{n}.{c}', value(A, r, c) is None)
    for c, destination in enumerate(['Anchovy eggs', 'Fishery offal', 'Pelagic detritus', 'Benthic detritus', 'Export'], 3):
        check(f'fleet.fate.{n}.{destination}', num(value(C, n + 3, c), fleet_fate['fate'][str(n)][destination]))
check('detailed_diet_39_named_predators', [v for v in sheet[B]['values'][2][1:] if v is not None] == [g['name'] for g in x['groups']])
check('detailed_diet_no_fleet_columns', all(value(B, r, c) is None for r in range(3, 44) for c in [41, 42, 43]))

# Verify provenance values, formats and estimation flags directly against the read snapshot.
for i, record in enumerate(json.loads((N / 'SOURCE_CELLS.json').read_text(encoding='utf-8'))):
    src = cells[record['sheet']][record['cell']]
    check(f'ledger.value.{i}', src['value'] == record['native_value'])
    check(f'ledger.hash.{i}', record['source_sha256'] == snap['source_sha256'])
    if 'number_format' in record:
        check(f'ledger.format.{i}', src['number_format'] == record['number_format'])
    if 'estimated_by_model' in record:
        check(f'ledger.estimated.{i}', src['bold'] == record['estimated_by_model'])

agg = json.loads((R / 'aggregated_alternative_source.json').read_text(encoding='utf-8'))
for name, retained in agg.items():
    check(f'aggregate.full_snapshot.{name}', retained == sheet[name])
    for i, cell in enumerate(retained['cells']):
        check(f'aggregate.cell.{name}.{i}', cell == cells[name][cell['address']])
check('aggregate_diet_no_fleet_columns', all(v is None for row in sheet['Table F-aggregated diet']['values'][2:] for v in row[25:]))

tl = openpyxl.load_workbook(N / 'TL.xlsx', data_only=False).active
for n in range(1, 40):
    check(f'TL.identity.{n}', tl.cell(n + 1, 1).value == n and tl.cell(n + 1, 2).value == x['groups'][n - 1]['name'])
metadata = openpyxl.load_workbook(N / 'Metadata.xlsx', data_only=False).active
for i, key in enumerate(['LME', 'model_number', 'model_name', 'model_year'], 1):
    check(f'Metadata.{key}', metadata.cell(i, 1).value == key and metadata.cell(i, 2).value == x['metadata'][key])
diet_wb = wb['Diet']
for col, n in enumerate(x['consumers'], 3):
    check(f'workbook.diet.import.{n}', diet_wb.cell(41, col).value == float(x['diet'][str(n)]['import']))

failures = [k for k, passed in checks.items() if not passed]
result = dict(prior, passed=not failures, checks=len(checks), failures=failures, exact_checks=checks,
              extra_coverage=['source snapshot direct parameter/diet/import/catch/fate comparisons',
                              'full source provenance value/format/bold checks',
                              'fleet source blanks, identities and discard fate',
                              'absent fleet diet columns explicitly verified',
                              'all aggregated raw cells and metadata',
                              'catch/discard/fate workbook sheets and diet imports'],
              identity_guarantee='Source and computational model JSON were read only. No normalization or biological repair.')
(N / 'ROUND_TRIP_CHECKS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
availability = {
    'detailed_fleet_diet': {'status': 'not supplied', 'evidence': 'Table B row 3 names 39 stock predators; AO:AQ and rows 3–43 are blank', 'invented': False},
    'aggregate_fleet_diet': {'status': 'not supplied', 'evidence': 'Table F row 3 names 24 stock predators; Z:AQ are blank', 'invented': False},
    'fleet_biology': {'status': 'blank source cells', 'evidence': 'Table A C45:L46', 'invented': False},
    'fleet_removals': {'status': 'explicit per-stock landings and discards', 'evidence': 'Table A I6:L44'},
    'fleet_discard_fate': {'status': 'explicit, entire return to Offal 37', 'evidence': 'Table C C43:G44'},
    'ECOTRAN_fisheries_production_node': {'status': 'retained raw matrix evidence', 'evidence': 'Table H-agg. production matrix', 'interpretation': 'Not interchangeable with a supplied Ecopath fleet diet column'}
}
(N / 'FIELD_AVAILABILITY.json').write_text(json.dumps(availability, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failures': failures[:20]}, ensure_ascii=False))
raise SystemExit(0 if not failures else 1)
