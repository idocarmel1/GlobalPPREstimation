"""Read-only reproduction of the original LME037 execution-reference shape."""
import json
from pathlib import Path
import sys
import traceback

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
import adopt_completion as adopter
from tools.project_core.calculations import coverage
from tools.project_core.workbooks.workbooks import read_book


def main():
    item = next(item for item in adopter.read(WORK / 'inputs/validated_inventory.json')['pairs']
                if item['unit_id'] == 'LME_037')
    model_dir = ROOT / item['model_dir']
    manifest_path = model_dir / 'results/result_manifest.json'
    regional = ROOT / 'regions/LME/LME_037/LME_037.xlsx'
    manifest = adopter.read(manifest_path)
    record = manifest['method_coverage']['execution_evidence']
    proof = adopter.reference(model_dir / 'results/diagnostics', record)
    paths = [manifest_path, regional, proof, Path(coverage.__file__)]
    hashes = {path: adopter.sha(path) for path in paths}
    book = read_book(regional, sheets={'Selected model groups'})
    try:
        coverage._cached_methods(model_dir, manifest['method_coverage'],
            manifest['method_coverage'].get('context'), book, item['pending_non_mc_methods'])
    except AttributeError as error:
        assert str(error) == "'str' object has no attribute 'get'"
        trace = traceback.format_exc()
    else:
        raise AssertionError('Original execution-reference shape did not reproduce the failure')
    assert set(record) == {'path', 'sha256'}
    for path, digest in hashes.items():
        assert adopter.sha(path) == digest
    result = {'status': 'REPRODUCED_AUTHENTIC_LEGACY_SINGLE_REFERENCE',
        'execution_evidence': record, 'execution_evidence_value_types':
            {key: type(value).__name__ for key, value in record.items()},
        'proof_sha256_matches_original_reference': True, 'traceback': trace,
        'reason': 'The saved container is itself one valid reference; values() incorrectly treats path and SHA strings as individual references.',
        'proposed_fix': 'Read a legacy top-level path/SHA pair as one reference, alongside any later named reference objects; retain the original saved mapping verbatim and authenticate every reference.',
        'canonical_writes': False, 'scientific_solver_called': False,
        'unchanged_sha256': {path.relative_to(ROOT).as_posix(): digest for path, digest in hashes.items()}}
    output = WORK / 'qa/legacy_execution_reference_reproduction.json'
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
