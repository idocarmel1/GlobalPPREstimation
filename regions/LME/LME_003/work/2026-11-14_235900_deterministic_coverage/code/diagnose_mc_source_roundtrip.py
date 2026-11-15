"""Inspect MC-sheet serialization through the real merge in a private copy."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as etree

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
import adopt_completion as adoption
from tools.project_core.calculations.coverage import _update_source
from tools.project_core.validation.researcher_review import S, sheet_xml
from tools.project_core.workbooks.workbooks import read_book


def inspect(path, retained):
    with zipfile.ZipFile(path) as archive:
        member, sheet = sheet_xml(archive, 'mc_diagnostics')
        raw = archive.read(member)
    return {'protected_rows': adoption.source_state(path, retained)['mc_diagnostics'],
            'dimension': sheet.find(f'{{{S}}}dimension').get('ref'),
            'xml_rows': [{'r': row.get('r'), 'cell_count': len(row)}
                         for row in sheet.findall(f'{{{S}}}sheetData/{{{S}}}row')],
            'worksheet_member': member, 'worksheet_sha256': hashlib.sha256(raw).hexdigest(),
            'worksheet_xml': raw.decode()}


def main():
    model = ROOT / 'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native'
    source = model / 'sppr_source.xlsx'
    regional = ROOT / 'regions/LME/LME_014/LME_014.xlsx'
    original_hashes = {p: adoption.sha(p) for p in (source, regional)}
    book = read_book(regional)
    retained = set(adoption.protected_book(book)['retained_methods'])
    before = inspect(source, retained)
    with tempfile.TemporaryDirectory(prefix='mc-source-roundtrip-', dir=WORK / 'tmp') as directory:
        candidate = Path(directory) / 'sppr_source.xlsx'
        shutil.copyfile(source, candidate)
        # No new scientific result is needed: even a merge with no outcomes
        # exercises the same load/save of the untouched MC sheet.
        _update_source(candidate, book, {})
        after = inspect(candidate, retained)
        try:
            adoption.unchanged_projection(adoption.source_state(source, retained),
                                          adoption.source_state(candidate, retained), 'source')
        except ValueError as error:
            guard_error = str(error)
        else:
            guard_error = None
    for p, fingerprint in original_hashes.items():
        assert adoption.sha(p) == fingerprint, str(p)
    assert len(before['protected_rows']) == 2 and len(after['protected_rows']) == 1
    assert all(value is None for value in before['protected_rows'][1])
    assert before['protected_rows'][0] == after['protected_rows'][0]
    assert guard_error == 'Protected row count changed: source/mc_diagnostics'
    report = {'status': 'REPRODUCED_EMPTY_MC_ROW_REMOVAL', 'before': before, 'after': after,
              'strict_guard_error': guard_error, 'new_mc_method_requested': False,
              'scientific_solver_called': False, 'canonical_writes': False,
              'source_hashes_unchanged': {p.relative_to(ROOT).as_posix(): h for p, h in original_hashes.items()},
              'coverage_sha256': adoption.sha(ROOT / 'tools/project_core/calculations/coverage.py'),
              'helper_sha256': adoption.sha(__file__)}
    out = WORK / 'qa/mc_source_roundtrip_reproduction.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
