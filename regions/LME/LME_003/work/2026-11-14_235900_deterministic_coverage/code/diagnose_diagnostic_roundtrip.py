"""Reproduce retained diagnostic rounding only in disposable workbook copies."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.calculations.coverage import _restore_retained_numbers
from tools.project_core.workbooks.workbooks import read_book, records, table_dict, update_book
from tools.project_core.validation.researcher_review import S, column_index, table_rows
from tools.scientific_helpers.sppr import method_coverage as adapter

FIELD = 'model_input_p_max_rel_residual'
MODEL = ROOT / 'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native'
REGIONAL = ROOT / 'regions/LME/LME_014/LME_014.xlsx'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value):
    return {'value': value, 'repr': repr(value), 'hex': value.hex() if isinstance(value, float) else None}


def xml_target(path, option='GE'):
    with zipfile.ZipFile(path) as archive:
        _, _, _, values = table_rows(archive, 'Diagnostics', 'model_health')
        row, record = next((row, record) for row, record in values
                           if (record.get('TE_option') or record.get('config_TE_option')) == option)
        headers = list(record)
        cell = next(cell for cell in row if column_index(cell.get('r')) == headers.index(FIELD) + 1)
        return {'cell': cell.get('r'), 'value_text': cell.find(f'{{{S}}}v').text}


def health(book):
    return {r.get('TE_option') or r.get('config_TE_option'): r
            for r in records(book, 'Diagnostics', 'model_health')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expect-preserved', action='store_true')
    args = parser.parse_args()
    cache = MODEL / 'results/diagnostics/method_coverage/deterministic_completion_20261114/calculated/calculated.json'
    protected = {path: sha(path) for path in [REGIONAL, MODEL / 'sppr_source.xlsx', cache]}
    original = read_book(REGIONAL)
    original_health = health(original)
    protected_health = {key: value for key, value in original_health.items() if key in ('GE', 'TE')}
    outcome = json.loads(cache.read_bytes())['methods']['new_WithEgestion']
    # This is exactly the flattening/table-union branch in _apply_outcomes;
    # no scientific method or constructor is called.
    flat = adapter._engine()[2]._flatten_diagnostics(adapter.diagnostics_for_table(outcome['diagnostics']))
    expanded = copy.deepcopy(original)
    actual_health = copy.deepcopy(original_health)
    actual_health['With Egestion'] = {'TE_option': 'With Egestion', **flat}
    expanded['Diagnostics']['model_health'] = table_dict(actual_health.values())
    old_header = original['Diagnostics']['model_health'][0]
    new_header = expanded['Diagnostics']['model_health'][0]
    assert new_header != old_header
    for option, row in protected_health.items():
        assert all(health(expanded)[option][key] == value for key, value in row.items())
    report = {'status': 'READ_ONLY_TMP_REPRODUCTION', 'field': FIELD,
              'original': number(original_health['GE'][FIELD]), 'original_xml': xml_target(REGIONAL),
              'old_header_count': len(old_header), 'new_header_count': len(new_header),
              'added_headers': [key for key in new_header if key not in old_header],
              'removed_headers': [key for key in old_header if key not in new_header],
              'requested_original_diagnostics_exact': True, 'protected_options': ['GE', 'TE'], 'cases': {}}
    temporary_root = (WORK / 'tmp').resolve()
    assert temporary_root.is_relative_to(WORK.resolve())
    with tempfile.TemporaryDirectory(prefix='diagnostic-roundtrip-', dir=temporary_root) as directory:
        for label, requested in [('unchanged_header', copy.deepcopy(original)), ('actual_added_diagnostic_columns', expanded)]:
            candidate = Path(directory) / (label + '.xlsx')
            shutil.copyfile(REGIONAL, candidate)
            update_book(candidate, requested)
            written = read_book(candidate, sheets=['Diagnostics'])
            before_restore = {'number': number(health(written)['GE'][FIELD]), 'xml': xml_target(candidate)}
            restored = _restore_retained_numbers(candidate, requested, original)
            final = health(read_book(candidate, sheets=['Diagnostics']))
            differences = [{'option': option, 'field': key, 'before': number(value), 'after': number(final[option].get(key))}
                           for option, row in protected_health.items() for key, value in row.items()
                           if value != final[option].get(key)]
            report['cases'][label] = {'before_restore': before_restore, 'restorer_changed_workbook': restored,
                                     'after_restore': {'number': number(final['GE'][FIELD]), 'xml': xml_target(candidate)},
                                     'original_field_differences': differences}
    import openpyxl
    source = openpyxl.load_workbook(MODEL / 'sppr_source.xlsx', read_only=True, data_only=False)
    try:
        header, *rows = source['model_health'].values
        source_health = [dict(zip(header, row)) for row in rows]
        report['original_source_values'] = [{'option': row.get('TE_option') or row.get('config_TE_option'),
                                            **number(row.get(FIELD))} for row in source_health]
    finally:
        source.close()
    assert not report['cases']['unchanged_header']['original_field_differences']
    if args.expect_preserved:
        assert not report['cases']['actual_added_diagnostic_columns']['original_field_differences']
        report['status'] = 'PASS_TMP_POSTFIX_EXACT_PRESERVATION'
    else:
        assert report['cases']['actual_added_diagnostic_columns']['original_field_differences']
    for path, fingerprint in protected.items():
        assert sha(path) == fingerprint, str(path)
    report['source_hashes_unchanged'] = {p.relative_to(ROOT).as_posix(): h for p, h in protected.items()}
    report['helper_sha256'] = sha(__file__)
    report['coverage_sha256'] = sha(ROOT / 'tools/project_core/calculations/coverage.py')
    report['writer_sha256'] = sha(ROOT / 'tools/project_core/workbooks/workbooks.py')
    output = WORK / ('qa/diagnostic_roundtrip_postfix.json' if args.expect_preserved
                     else 'qa/diagnostic_roundtrip_reproduction.json')
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
