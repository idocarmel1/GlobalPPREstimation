"""2019 total-catch simple-chain ranks within the curated atlas ensemble."""
import gzip
import json
from pathlib import Path

from tools.project_core.workbooks.workbooks import SIMPLE, finite, records

RANK_COLUMN = 'atlas_region_rank'
RANK_TABLES = [('Regions & status', 'Regions'), ('Papers', 'Papers'), ('Models & coverage', 'Models')]


def ensemble_ids(root):
    path = Path(root) / 'common_reference_data/atlas_source_context/catalog.json.gz'
    with gzip.open(path, 'rt', encoding='utf-8') as source:
        return set(json.load(source)['curated_region_ids'])


def apply_atlas_ranks(book, members):
    values = {}
    for row in records(book, 'Regional PPR', 'Annual'):
        unit = row.get('unit_id')
        if unit not in members or row.get('model_id') or any(row.get(k) != v for k, v in
                [('scope', 'all'), ('method', SIMPLE), ('catch_basis', 'catch'),
                 ('unidentified', 'method'), ('metric', 'ppr')]):
            continue
        if unit in values:
            raise ValueError(f'Duplicate 2019 atlas ranking input: {unit}')
        value = row.get(2019)
        values[unit] = value if row.get('status') == 'ok' and finite(value) and value >= 0 else None
    ordered = sorted(((unit, value) for unit, value in values.items() if value is not None),
                     key=lambda item: (-item[1], item[0]))
    ranks = {}; previous = None; rank = None
    for position, (unit, value) in enumerate(ordered, 1):
        if value != previous:
            rank = position
        ranks[unit] = rank
        previous = value
    for sheet, table in RANK_TABLES:
        if table not in book.get(sheet, {}):
            continue
        header, data = book[sheet][table]
        if RANK_COLUMN not in header:
            header.append(RANK_COLUMN)
        column = header.index(RANK_COLUMN); unit_column = header.index('unit_id')
        for row in data:
            row.extend([None] * (len(header) - len(row)))
            row[column] = ranks.get(row[unit_column])
    return ranks
