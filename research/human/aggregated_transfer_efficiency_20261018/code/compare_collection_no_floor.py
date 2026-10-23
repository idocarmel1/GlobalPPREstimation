"""Repeat the collection's level-flow calculation with only the EE floor disabled.

Reuse the existing loader, worker and timeout machinery. Do not recalculate
unrequested SPPR methods, modify baseline results, or change scientific inputs.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
from queue import Queue
import subprocess
import sys
import threading

import compare_collection as base

STUDY = base.STUDY
OUT = STUDY / 'results/full_collection_no_floor'
EVIDENCE = STUDY / 'evidence/full_collection_no_floor'
base.OUT = OUT
base.FLAGS = {**base.FLAGS, 'use_ee_floor': False}
base.METHODS = ()  # Only the level-flow estimates are requested in this follow-up.


class NoFloorServer(base.ModelServer):
    """Launch this entry point so every child receives the no-floor settings."""
    def __init__(self):
        environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                           MKL_NUM_THREADS='1', PYTHONIOENCODING='utf-8')
        self.process = subprocess.Popen(
            [sys.executable, '-u', str(Path(__file__).resolve()), '--server'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', env=environment,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.lines = Queue()
        threading.Thread(target=self._read_lines, daemon=True).start()
        base.SERVERS.append(self)
        self.wait_for('SERVER_READY', 90.)


base.ModelServer = NoFloorServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=60.)
    args = parser.parse_args()
    if args.server:
        base.server()
        return

    baseline_path = STUDY / 'evidence/full_collection_manifest.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    sources = sorted(base.CORPUS.glob('*.json'), key=lambda path: path.name)
    hashes = {path.relative_to(base.ROOT).as_posix(): base.sha(path) for path in sources}
    if hashes != baseline['source_hashes']:
        raise ValueError('Input inventory/bytes changed since the floor-enabled baseline.')
    for relative, expected in baseline['code_hashes'].items():
        if base.sha(base.ROOT / relative) != expected:
            raise ValueError('Baseline calculation code changed: ' + relative)
    changes = {key: {'baseline': baseline['initialization_flags'].get(key), 'new': value}
               for key, value in base.FLAGS.items()
               if value != baseline['initialization_flags'].get(key)}
    assert changes == {'use_ee_floor': {'baseline': True, 'new': False}}, changes
    code_hashes = {**baseline['code_hashes'],
                   Path(__file__).relative_to(base.ROOT).as_posix(): base.sha(Path(__file__))}
    baseline_results = STUDY / 'results/full_collection/level_flows.csv'
    reference_hashes = {str(path.relative_to(STUDY)): base.sha(path)
                        for path in (baseline_path, baseline_results)}
    manifest = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'discovery': baseline['discovery'], 'source_count': len(sources),
        'source_hashes': hashes, 'code_hashes': code_hashes,
        'initialization_flags': base.FLAGS, 'flag_changes_from_baseline': changes,
        'baseline_reference_sha256': reference_hashes,
        'python_executable': sys.executable, 'timeout_seconds': args.timeout,
        'workers': max(1, min(3, args.workers)),
        'scope': 'Fresh construction and get_aggregated_TE for all canonical JSONs; no SPPR rerun.',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    base.save_json(EVIDENCE / 'manifest.json', manifest)
    records = []
    try:
        with ThreadPoolExecutor(max_workers=manifest['workers']) as pool:
            futures = {pool.submit(base.run_one, path, args.timeout): path for path in sources}
            for future in as_completed(futures):
                records.append(future.result())
                if len(records) % 10 == 0 or len(records) == len(sources):
                    constructed = sum(r.get('construction_status') == 'ok' for r in records)
                    print(f'{len(records)}/{len(sources)} processed; constructed={constructed}', flush=True)
    finally:
        for server in base.SERVERS:
            server.close()
    records.sort(key=lambda record: record['source'])
    base.verify_calculation_identity(manifest, records)
    for relative, digest in reference_hashes.items():
        assert base.sha(STUDY / relative) == digest, relative
    flows = [{'model_id': record['model_id'], **flow} for record in records
             for flow in record.get('aggregated_flows', [])]
    base.save_csv(OUT / 'level_flows.csv', flows)
    summary = {
        'inventory_count': len(records), 'initialization_flags': base.FLAGS,
        'flag_changes_from_baseline': changes,
        'stage_counts': {key: dict(Counter(record.get(key, 'not_run') for record in records))
                         for key in ('json_status', 'load_status', 'construction_status',
                                     'aggregation_status', 'run_status')},
        'level_estimate_count': len(flows),
        'balance_counts_constructed': dict(Counter(
            str(record['model_balance_status']) for record in records
            if record.get('construction_status') == 'ok')),
        'failures': [{key: record.get(key) for key in (
            'model_id', 'stage', 'run_status', 'error', 'aggregation_error',
            'subprocess_error', 'timeout_stage')}
            for record in records if record.get('run_status') != 'complete'
            or record.get('aggregation_status') == 'error'],
        'interpretation': 'Loadability, construction, balance and scientific validity remain separate.'
    }
    base.save_json(OUT / 'summary.json', summary)
    verification = {
        'completed_utc': datetime.now(timezone.utc).isoformat(),
        'original_calculation_started_utc': manifest['started_utc'],
        'source_count': len(sources), 'output_record_count': len(records),
        'unique_sources': len({record['source'] for record in records}),
        'source_bytes_unchanged': True, 'code_bytes_unchanged': True,
        'baseline_reference_bytes_unchanged': True,
        'every_record_has_no_floor_flags': all(record['flags'] == base.FLAGS for record in records),
        'output_sha256': {path.relative_to(STUDY).as_posix(): base.sha(path)
                          for path in sorted(OUT.rglob('*')) if path.is_file()},
        'summary': summary,
    }
    base.save_json(EVIDENCE / 'verification.json', verification)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
