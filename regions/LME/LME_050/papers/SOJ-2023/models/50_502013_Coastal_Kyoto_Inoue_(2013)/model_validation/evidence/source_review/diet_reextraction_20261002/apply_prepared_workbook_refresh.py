"""Validate persisted candidate, then hash-guard its coordinated adoption."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, validate_region, overview
OUT = Path(__file__).parent
PLAN = OUT / 'runtime_workbook_refresh_plan.json'
plan = json.loads(PLAN.read_text())
path = ROOT / 'regions/LME_050/LME_050.xlsx'
candidate = ROOT / plan['candidate_path']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(path) == plan['regional_before_sha256'], 'Concurrent workbook change'
assert sha(candidate) == plan['candidate_sha256'], 'Candidate changed'
source = ROOT / 'regions/LME_050/models/50_502013_Coastal_Kyoto_Inoue_(2013)/model.json'
source_hash = json.loads((OUT / 'current_runtime_refresh/refresh_receipt.json').read_text())['canonical_sha256']
assert sha(source) == source_hash, 'Concurrent source change'
verified = OUT / 'persisted_candidate_verification.json'
if not verified.exists() or json.loads(verified.read_text()).get('candidate_sha256') != sha(candidate):
    book = read_book(candidate)
    validate_region(book, path)
    assert overview(book)['calculation_input_sha256'] == plan['after_calculation_input_sha256']
    verified.write_text(json.dumps({'candidate_sha256': sha(candidate), 'source_sha256': source_hash,
                                   'persisted_regional_validation_passed': True}, indent=2))
    print('Persisted candidate validation passed', flush=True)
if '--apply' in sys.argv:
    assert sha(path) == plan['regional_before_sha256'] and sha(source) == source_hash
    backup = OUT / 'original_inputs' / sha(path) / path.name
    assert sha(backup) == sha(path), 'Original not archived'
    shutil.copyfile(candidate, path)
    assert sha(path) == plan['candidate_sha256']
    plan.update(applied=True, regional_after_sha256=sha(path), persisted_candidate_validated=True)
    (OUT / 'runtime_workbook_refresh_receipt.json').write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding='utf-8')
    receipt_path = OUT / 'root_receipt.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['current_shared_loader_requires_root_refresh_assessment'] = False
    receipt['runtime_refresh'] = {'direct_configurations_refreshed': ['GE', 'TE', 'With Egestion'],
       'all_coefficient_and_network_matrices_exactly_equal_to_history': True,
       'regional_workbook_refreshed': True, 'regional_sha256': sha(path),
       'selection_mapping_admission_preserved': True,
       'project_map_refresh_pending': True}
    receipt['evidence_paths'] += [(OUT / 'runtime_workbook_refresh_receipt.json').relative_to(ROOT).as_posix(),
                                 (OUT / 'current_runtime_refresh/refresh_receipt.json').relative_to(ROOT).as_posix()]
    receipt['precise_blockers'] = [v for v in receipt['precise_blockers'] if not v.startswith('Current shared runtime loader differs')]
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Applied runtime workbook refresh; selection and coefficients preserved', sha(path), flush=True)
