"""Download every official EEZ; resumable, with bounded concurrent requests."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from ppr_pipeline.download import (
    _download, _session_with_retries, download_unit_inputs,
    eez_units_from_catalog, regions_url,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=3, choices=range(1, 5))
    args = parser.parse_args()
    raw = ROOT / 'raw_data' / 'SAU_downloads'
    base = 'https://api.seaaroundus.org/api/v1'
    with _session_with_retries() as session:
        for spatial in (False, True):
            name = 'eez_regions_spatial.json' if spatial else 'eez_regions.json'
            _download(session, regions_url(base, 'eez', spatial=spatial), raw / name, overwrite=False)
    units = eez_units_from_catalog(json.loads((raw / 'eez_regions.json').read_text(encoding='utf-8')))
    features = json.loads((raw / 'eez_regions_spatial.json').read_text(encoding='utf-8'))['data']['features']
    if {u['sau_region_id'] for u in units} != {f['properties']['region_id'] for f in features}:
        raise ValueError('EEZ catalog and polygon IDs disagree')
    errors = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_unit_inputs, [u], base, raw, progress=None): u for u in units}
        for i, future in enumerate(as_completed(futures), 1):
            u = futures[future]
            try:
                future.result()
                print(f'[{i}/{len(units)}] {u["unit_id"]} {u["name"]}: ready', flush=True)
            except Exception as exc:
                errors.append({'unit_id': u['unit_id'], 'error': str(exc)})
                print(f'[{i}/{len(units)}] {u["unit_id"]}: ERROR {exc}', flush=True)
    (raw / 'eez_download_status.json').write_text(json.dumps({'units': len(units), 'errors': errors}, indent=2), encoding='utf-8')
    if errors:
        raise RuntimeError(f'{len(errors)} EEZ downloads failed; rerun to retry missing inputs')


if __name__ == '__main__':
    main()
