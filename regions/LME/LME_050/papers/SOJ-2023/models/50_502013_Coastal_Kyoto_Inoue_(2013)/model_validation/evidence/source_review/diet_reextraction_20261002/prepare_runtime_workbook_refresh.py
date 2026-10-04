"""Prepare the affected selected runtime/workbook refresh without changing selection."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import pandas as pd
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, write_book, overview, records, validate_region
from regional import recalculate, set_setting, set_result_hash
OUT = Path(__file__).parent
REFRESH = OUT / 'current_runtime_refresh'
PATH = ROOT / 'regions/LME_050/LME_050.xlsx'
MID = '50_502013_Coastal_Kyoto_Inoue_(2013)'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
before_sha = sha(PATH)
book = read_book(PATH)
old = copy.deepcopy(book)
baseline = copy.deepcopy(book)
recalculate(baseline, PATH)
settings = overview(book)
assert settings['selected_model_id'] == MID
receipt = json.loads((REFRESH / 'refresh_receipt.json').read_text())
assert all(o.get('status') == 'WARN' and all(v['equivalent_at_absolute_1e_12'] for v in o['matrix_comparison'].values()) for o in receipt['outcomes'])
groups = pd.read_csv(REFRESH / 'loaded_groups.csv').fillna('')
assert list(groups.columns) == book['Selected model groups']['Groups'][0]
book['Selected model groups']['Groups'] = (list(groups.columns), groups.values.tolist())
health = []
for option in ('GE', 'TE', 'With Egestion'):
    report_path = REFRESH / ('diagnose_sppr_' + option.replace(' ', '_') + '.json')
    report = json.loads(report_path.read_text())['direct_diagnose_sppr_return']
    health.append([MID, option, report['status'], json.dumps(report, ensure_ascii=False), report_path.relative_to(PATH.parent).as_posix()])
book['Diagnostics']['direct_diagnose_sppr'] = (['model_id','TE_option','status','complete_return_json','evidence_path'], health)
recalculate(book, PATH)
# The rate correction changed neither coefficients nor dependent numeric output.
# Keep the existing production/admission decision and selection rationale.
for key in ('production_eligible', 'calculation_status', 'source_note'):
    set_setting(book, key, settings.get(key))
set_result_hash(book)
for sheet in ('Catch', 'NPP'):
    assert book[sheet] == old[sheet], sheet
assert book['Classic PPR']['Taxa'] == old['Classic PPR']['Taxa']
assert book['PPR']['Matching'] == old['PPR']['Matching']
assert book['Selected model groups']['Group SPPR'] == old['Selected model groups']['Group SPPR']
for sheet, tables in (('Classic PPR', ['Annual']), ('PPR', ['Annual', 'Taxon SPPR']), ('PPR–NPP', ['Ratios'])):
    for table in tables:
        assert book[sheet][table] == baseline[sheet][table], (sheet, table, 'Runtime rate correction changed calculated outputs')
assert overview(book)['selected_model_id'] == settings['selected_model_id']
assert overview(book)['model_path'] == settings['model_path']
assert overview(book)['selection_rationale'] == settings['selection_rationale']
validate_region(book, PATH)
candidate = OUT / 'LME_050_runtime_refresh_candidate.xlsx'
write_book(candidate, book)
assert sha(PATH) == before_sha, 'Concurrent regional workbook change'
backup = OUT / 'original_inputs' / before_sha / PATH.name
backup.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(PATH, backup)
assert sha(backup) == before_sha
plan = {'region': 'LME_050', 'regional_before_sha256': before_sha,
        'candidate_sha256': sha(candidate), 'candidate_path': candidate.relative_to(ROOT).as_posix(),
        'before_calculation_input_sha256': settings['calculation_input_sha256'],
        'after_calculation_input_sha256': overview(book)['calculation_input_sha256'],
        'numeric_coefficients_unchanged': True,
        'fresh_before_and_after_annual_and_ratios_exactly_equal': True,
        'storage_precision_note': 'Recalculation from the stored workbook may change Excel 16-significant-digit rounding tails; same fresh before/after calculations are exactly equal.',
        'selection_mapping_source_decisions_preserved': True, 'candidate_validated': True,
        'applied': False}
dump(OUT / 'runtime_workbook_refresh_plan.json', plan)
print(json.dumps(plan), flush=True)
if '--apply' in sys.argv:
    assert sha(PATH) == before_sha
    shutil.copyfile(candidate, PATH)
    assert sha(PATH) == plan['candidate_sha256']
    plan.update(applied=True, regional_after_sha256=sha(PATH))
    dump(OUT / 'runtime_workbook_refresh_receipt.json', plan)
    print('Applied validated affected runtime workbook refresh', flush=True)
