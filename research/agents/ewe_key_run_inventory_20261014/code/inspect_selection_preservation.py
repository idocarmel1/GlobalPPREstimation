"""Diagnose source XML serialization differences against verified Git bytes."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import hashlib
import json
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_balanced_models import INDEPENDENT, STUDY, table_identity
from tools.project_core.validation.researcher_review import table_rows
before = json.loads((STUDY / 'evidence/balanced_selection_before.json').read_text(encoding='utf-8'))
for unit in ['LME_022', 'LME_023']:
    relative = 'regions/LME/' + unit + '/' + unit + '.xlsx'
    old_bytes = subprocess.run(['git', 'show', 'HEAD:' + relative], cwd=ROOT, capture_output=True, check=True).stdout
    assert hashlib.sha256(old_bytes).hexdigest() == before['region_hashes_before'][unit], 'Git does not match assessed starting workbook'
    changed = [k for k, v in table_identity(ROOT / relative).items() if v != before['targets'][unit]['independent_tables_before'][k]]
    print(unit, 'XML table digests changed:', changed)
    with ZipFile(BytesIO(old_bytes)) as old, ZipFile(ROOT / relative) as new:
        for sheet, table in INDEPENDENT:
            if sheet + '/' + table not in changed: continue
            oh, orows = table_rows(old, sheet, table)[1], [r for _, r in table_rows(old, sheet, table)[3]]
            nh, nrows = table_rows(new, sheet, table)[1], [r for _, r in table_rows(new, sheet, table)[3]]
            differences = []
            for i, (a, b) in enumerate(zip(orows, nrows)):
                for k in sorted(set(a) | set(b)):
                    if a.get(k) != b.get(k): differences.append({'row': i, 'field': k, 'old': a.get(k), 'new': b.get(k)})
            print(json.dumps({'table': sheet + '/' + table, 'headers_match': oh == nh, 'old_rows': len(orows), 'new_rows': len(nrows), 'differences': differences[:15]}, ensure_ascii=False))
