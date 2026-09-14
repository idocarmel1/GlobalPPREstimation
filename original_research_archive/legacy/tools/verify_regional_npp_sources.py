"""Independent post-extraction source-byte audit; no metadata cache or raster work."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from atomic_output import write_text_atomic

def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

started = time.monotonic()
plan_path = ROOT / 'NPPExtraction/output/regional_expansion/plan.json'
plan = json.loads(plan_path.read_text(encoding='utf-8'))
plan_hash = digest(plan_path)
canonical = ROOT / 'NPPExtraction/output/annual_npp.csv'
canonical_hash = digest(canonical)
sources = {}
raw = (ROOT / 'NPPExtraction/data/raw').resolve()
for year, source in plan['source_runs'].items():
    for item in source['downloads']:
        recorded = item['path'].replace('\\', '/')
        marker = 'NPPExtraction/data/raw/'
        if marker not in recorded:
            raise ValueError(f'Unrecognized source path: {recorded}')
        path = (raw / recorded.split(marker, 1)[1]).resolve()
        if not path.is_relative_to(raw):
            raise ValueError('Source escapes raw directory')
        relative = path.relative_to(ROOT).as_posix()
        expected = (item['bytes'], item['sha256'])
        if relative in sources and sources[relative]['expected'] != expected:
            raise ValueError(f'Conflicting planned source identity: {relative}')
        entry = sources.setdefault(relative, {'expected': expected, 'years': []})
        entry['years'].append(int(year))

results, failures = [], []
for index, (relative, item) in enumerate(sorted(sources.items()), 1):
    path = ROOT / relative
    before = path.stat()
    checksum = digest(path)
    after = path.stat()
    expected_bytes, expected_hash = item['expected']
    stable = before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns
    valid = stable and after.st_size == expected_bytes and checksum == expected_hash
    row = {'path': relative, 'bytes': after.st_size, 'sha256': checksum,
           'expected_sha256': expected_hash, 'expected_bytes': expected_bytes,
           'years': sorted(set(item['years'])), 'status': 'passed' if valid else 'failed'}
    results.append(row)
    if not valid:
        failures.append(relative)
    if index % 100 == 0:
        print(f'Hashed {index}/{len(sources)} source files', flush=True)

bindings = []
for year in plan['years']:
    paths = list((ROOT / 'NPPExtraction/output/regional_expansion/years' / str(year)).glob('*/provenance.json'))
    if len(paths) != 1:
        raise ValueError(f'Ambiguous completed regional provenance: {year}')
    provenance_path = paths[0]
    provenance = json.loads(provenance_path.read_text(encoding='utf-8'))
    expected_source = plan['source_runs'][str(year)]
    if provenance['source_configuration'] != {k: expected_source[k] for k in ('path', 'sha256')}:
        raise ValueError(f'Completed regional lineage differs from plan: {year}')
    for source in provenance['verified_source_files']:
        item = sources[source['path']]
        if item['expected'] != (source['bytes'], source['sha256']):
            raise ValueError(f'Completed source identity differs from plan: {year}')
    bindings.append({'year': year, 'path': provenance_path.relative_to(ROOT).as_posix(),
                     'sha256': digest(provenance_path)})
if digest(plan_path) != plan_hash or digest(canonical) != canonical_hash:
    raise ValueError('Completed plan or annual table changed during audit')
report = {
    'status': 'passed' if not failures else 'failed',
    'audit_type': 'Independent uncached SHA-256 of actual monthly source bytes after completed extraction',
    'completed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
    'elapsed_seconds': time.monotonic() - started,
    'plan': {'path': plan_path.relative_to(ROOT).as_posix(), 'sha256': plan_hash},
    'annual': {'path': canonical.relative_to(ROOT).as_posix(), 'sha256': canonical_hash},
    'publication_verification': {'path': 'NPPExtraction/output/regional_expansion/publication_verification.json',
        'sha256': digest(ROOT / 'NPPExtraction/output/regional_expansion/publication_verification.json')},
    'completed_regional_provenance': bindings,
    'unique_monthly_files': len(results), 'bytes_read_and_hashed': sum(row['bytes'] for row in results),
    'failed_sources': failures,
    'historical_validation_limitation': 'The executed frozen regional helper reused successful checksum checks while path, size, modification time and expected hash matched. Such metadata can remain unchanged after a byte replacement. This post-extraction audit independently checks all current source bytes; it does not retroactively establish uncached validation at every historical extraction boundary.',
    'future_extraction_requirement': 'Use an explicitly versioned hardened helper and fresh plan/cache identity that hash actual source bytes at every validation boundary. Preserve this completed run\'s helper, plan and execution snapshots as historical evidence.',
    'sources': results,
}
destination = ROOT / 'data/regional_npp_source_bytes_validation.json'
write_text_atomic(destination, json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('status', 'unique_monthly_files', 'bytes_read_and_hashed', 'elapsed_seconds', 'failed_sources')}), flush=True)
if failures:
    raise SystemExit(1)
