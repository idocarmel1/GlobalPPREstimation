"""Matched actual full/selective/session reads on unchanged real workbook bytes."""
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, sha
from tools.project_core.workbooks.read_session import ReadSession

RUN = Path(__file__).resolve().parent.parent
path = ROOT / 'regions/LME/LME_038/LME_038.xlsx'
before = sha(path)
events = []
active = False

def audit(event, args):
    if active and event == 'open' and isinstance(args[0], (str, bytes)):
        try:
            if Path(args[0]).resolve() == path: events.append(event)
        except (TypeError, ValueError): pass

sys.addaudithook(audit)
expected = read_book(path)['Overview']
results = []
for repetition in range(5):
    for variant in (['full', 'selective', 'session'] if repetition % 2 == 0 else ['session', 'selective', 'full']):
        events.clear(); active = True; start = time.perf_counter()
        session = ReadSession() if variant == 'session' else None
        values = []
        for _ in range(3):
            book = session.read(path, sheets=['Overview']) if session else read_book(path, sheets=['Overview'] if variant == 'selective' else None)
            values.append(book['Overview'])
        if session: session.assert_unchanged()
        elapsed = time.perf_counter() - start; active = False
        assert all(value == expected for value in values)
        results.append({'repeat': repetition, 'variant': variant, 'elapsed_seconds': elapsed,
                        'logical_reads': 3, 'workbook_parses': session.parse_count if session else 3,
                        'observed_workbook_file_opens': len(events), 'engine_calls': 0,
                        'render_calls': 0, 'project_writes': 0, 'exact_table_equality': True})
assert sha(path) == before
output = {'input': path.relative_to(ROOT).as_posix(), 'sha256': before,
          'runtime': sys.version, 'context': 'new operation per sample; OS cache uncontrolled; same process, alternating order',
          'token_telemetry': None, 'input_unchanged': True, 'samples': results}
(RUN / 'qa/workbook_read_benchmark.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf8')
for variant in ['full', 'selective', 'session']:
    samples = [r for r in results if r['variant'] == variant]
    print(variant, 'mean_seconds', sum(r['elapsed_seconds'] for r in samples) / len(samples),
          'parses', samples[0]['workbook_parses'], 'file_opens', samples[0]['observed_workbook_file_opens'])
