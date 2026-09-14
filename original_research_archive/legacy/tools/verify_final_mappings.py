"""Check exact assignment/weight parity between central and model workbooks."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import openpyxl

ROOT = Path(__file__).resolve().parents[1]


def mappings(path):
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(book['Final mappings'].values)
        start = next(i for i, row in enumerate(rows) if row[0] == 'unit_id')
        return [tuple(row[:13]) for row in rows[start + 1:] if row[0]]
    finally:
        book.close()


def canonical(rows):
    return json.dumps(sorted(rows, key=lambda row: json.dumps(row, ensure_ascii=False)),
                      ensure_ascii=False, allow_nan=False)


def verify(root=ROOT):
    report = dict(status='ok', central_workbooks=0, model_workbooks=0,
                  assignment_rows=0, models=[])
    for directory in sorted((root / 'data').glob('LME_*/models')):
        books = sorted(directory.glob('*.xlsx'))
        if not books:
            continue
        unit = directory.parent.name
        grouped = defaultdict(list)
        for row in mappings(directory.parent / f'{unit}.xlsx'):
            grouped[row[1]].append(row)
        if set(grouped) != {book.stem for book in books}:
            raise ValueError(f'{unit}: central and model workbook identities differ')
        report['central_workbooks'] += 1
        for book in books:
            rows = mappings(book)
            serialized = canonical(rows)
            if serialized != canonical(grouped[book.stem]):
                raise ValueError(f'{book}: final assignments/weights differ from central workbook')
            report['model_workbooks'] += 1
            report['assignment_rows'] += len(rows)
            report['models'].append(dict(unit=unit, model=book.stem, rows=len(rows),
                taxa=len({row[2] for row in rows}),
                mapping_sha256=hashlib.sha256(serialized.encode('utf-8')).hexdigest()))
    if not report['model_workbooks']:
        raise ValueError('No model workbooks were checked')
    return report


if __name__ == '__main__':
    report = verify()
    (ROOT / 'data/final_mappings_validation.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
