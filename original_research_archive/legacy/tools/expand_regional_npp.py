"""Complete supported regional NPP independently of catch, preserving existing cells.

Plan is read-only with respect to canonical inputs. Extract is a serial raster job;
run only after the global worker exits. Publish refuses incomplete results and
preserves every existing CSV cell, including its exact string representation.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import shutil
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('NPPExtraction/output/regional_expansion')
MODELS = ('antoinemorel', 'vgpm', 'eppley', 'cbpm', 'cafe')
METHOD = 'gap-filled Antoine-Morel baseline; common-mask model ratios, own-coverage fallback'
VERIFIED = {}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.part')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def row_key(row):
    return row['unit_id'], int(row['year'])


def unique_rows(values):
    result = {}
    for row in values:
        key = row_key(row)
        if key in result:
            raise ValueError(f'duplicate regional NPP row: {key}')
        result[key] = row
    return result


def merge_rows(old, new):
    previous, additions = unique_rows(old), unique_rows(new)
    overlap = previous.keys() & additions.keys()
    if overlap:
        raise ValueError(f'cannot replace existing rows: {sorted(overlap)[:5]}')
    return [row for _, row in sorted({**previous, **additions}.items())]


def preservation_report(old, merged):
    previous, current = unique_rows(old), unique_rows(merged)
    for key, record in previous.items():
        if current.get(key) != record:
            raise ValueError(f'previous regional NPP row not preserved exactly: {key}')
    encoded = json.dumps([r for _, r in sorted(previous.items())], sort_keys=True, ensure_ascii=False).encode()
    return {'preserved_rows': len(previous), 'preserved_fields': sum(map(len, previous.values())),
            'preserved_rows_sha256': hashlib.sha256(encoded).hexdigest(), 'all_old_cells_exactly_equal': True}


def source_file(root, recorded):
    marker = 'NPPExtraction/data/raw/'
    recorded = str(recorded).replace('\\', '/')
    if marker not in recorded:
        raise ValueError(f'unrecognized source path: {recorded}')
    raw = (Path(root) / 'NPPExtraction/data/raw').resolve()
    path = (raw / recorded.split(marker, 1)[1]).resolve()
    if not path.is_relative_to(raw):
        raise ValueError('source path escapes raw directory')
    return path


def code_hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in
            [root / 'tools/expand_regional_npp.py', *sorted((root / 'NPPExtraction/npp').rglob('*.py'))]}


def verify_sources(root, manifest, checksums=True):
    result = []
    for record in manifest:
        path = source_file(root, record['path'])
        stat = path.stat()
        if stat.st_size != record['bytes']:
            raise ValueError(f'source byte count changed: {path.name}')
        key = str(path), stat.st_size, stat.st_mtime_ns, record['sha256']
        if checksums and key not in VERIFIED:
            if digest(path) != record['sha256']:
                raise ValueError(f'source checksum changed: {path.name}')
            VERIFIED[key] = True
        result.append({'path': path.relative_to(root).as_posix(), 'bytes': stat.st_size, 'sha256': record['sha256']})
    return result


def make_plan(root):
    output = root / OUTPUT
    output.mkdir(parents=True, exist_ok=True)
    canonical = root / 'NPPExtraction/output/annual_npp.csv'
    snapshot = output / 'annual_before.csv'
    if snapshot.exists():
        if digest(snapshot) != digest(canonical):
            raise ValueError('canonical annual input differs from existing expansion snapshot')
    else:
        shutil.copyfile(canonical, snapshot)
    old = rows(snapshot)
    present = {r['unit_id'] for r in old}
    units = sum([json.loads((root / f'SeaAroundUsExtraction/{folder}/tables/units.json').read_text(encoding='utf-8'))
                 for folder in ('global_output', 'eez_output')], [])
    missing = [r for r in units if r['unit_id'] not in present]
    grid, catch_sources, no_catch = [], [], []
    for unit in missing:
        uid = unit['unit_id']
        path = root / f'SeaAroundUsExtraction/data/catch_by_taxon_year/{uid}.csv.gz'
        if not path.exists():
            if uid not in ('HS_018', 'LME_064'):
                raise ValueError(f'unexpected missing catch identity: {uid}')
            no_catch.append(uid)
            # The original loader retains the supplied 2019 legacy cell verbatim.
            # These are NPP-only targets, never fabricated catch observations.
            grid.extend((uid, y) for y in range(1998, 2019))
            continue
        with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as handle:
            years = set()
            for record in csv.DictReader(handle):
                if record['unit_id'] != uid:
                    raise ValueError(f'catch identity mismatch: {uid}')
                years.add(int(record['year']))
        grid.extend((uid, y) for y in sorted(years))
        catch_sources.append({'path': path.relative_to(root).as_posix(), 'sha256': digest(path)})
    years = list(range(1998, 2020))
    grid = sorted(set(grid) | {(r['unit_id'], y) for r in missing for y in years
                              if not (r['unit_id'] in no_catch and y == 2019)})
    source_runs, files = {}, {}
    existing = set(unique_rows(old))
    reused, reused_sources = [], []
    for year in years:
        references = {r['provenance'] for r in old if int(r['year']) == year and r['provenance']}
        if len(references) != 1:
            raise ValueError(f'need one original canonical source run for {year}')
        path = root / references.pop()
        data = json.loads(path.read_text(encoding='utf-8'))
        inventory = verify_sources(root, data['downloads'], checksums=False)
        files.update({r['path']: r for r in inventory})
        source_runs[str(year)] = {'path': path.relative_to(root).as_posix(), 'sha256': digest(path),
                                 'config': data['config'], 'config_key': data['config_key'], 'downloads': data['downloads']}
        holes = {(u, year) for u in present if (u, year) not in existing}
        if holes:
            records_path = path.with_name('annual_records.json')
            computed = unique_rows(json.loads(records_path.read_text(encoding='utf-8')))
            if not holes.issubset(computed):
                raise ValueError(f'original supported NPP holes lack computed records: {holes - computed.keys()}')
            reused.extend(normalize_original_record(computed[key]) for key in sorted(holes))
            reused_sources.append({'path': records_path.relative_to(root).as_posix(), 'sha256': digest(records_path)})
    geometries = {}
    for layer, prefix in (('eez', 'EEZ'), ('highseas', 'HS'), ('lme', 'LME')):
        target_ids = {int(r['sau_region_id']) for r in missing if r['unit_id'].startswith(prefix + '_')}
        if not target_ids:
            continue
        geometry_source = root / f'NPPExtraction/data/raw/sau_{layer}_full.geojson'
        collection = json.loads(geometry_source.read_text(encoding='utf-8'))
        collection['features'] = [f for f in collection['features'] if int(f['properties']['region_id']) in target_ids]
        actual = {int(f['properties']['region_id']) for f in collection['features']}
        if actual != target_ids:
            raise ValueError(f'missing {layer} source geometries: {target_ids - actual}')
        geometry = output / f'{layer}_missing.geojson'
        atomic_json(geometry, collection)
        geometries[layer] = {'path': geometry.relative_to(root).as_posix(), 'sha256': digest(geometry),
                             'source_path': geometry_source.relative_to(root).as_posix(), 'source_sha256': digest(geometry_source)}
    legacy = root / 'NPPExtraction/NPP_2019_filled_SAU_regions.csv'
    plan = {'version': 1, 'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'before_path': snapshot.relative_to(root).as_posix(), 'before_sha256': digest(snapshot),
            'before_rows': len(old), 'before_unit_count': len(present), 'target_units': missing,
            'npp_only_units': no_catch, 'legacy_2019_preserved': {'path': legacy.relative_to(root).as_posix(), 'sha256': digest(legacy)},
            'reused_original_records': reused, 'reused_original_sources': reused_sources,
            'grid': grid, 'years': years, 'catch_sources': catch_sources, 'source_runs': source_runs,
            'source_files': list(files.values()), 'source_bytes': sum(r['bytes'] for r in files.values()),
            'missing_source_files': [], 'source_file_audit': 'existence and byte counts checked; SHA-256 checked before extraction',
            'geometries': geometries,
            'code_sha256': code_hashes(root), 'disk_free_bytes': shutil.disk_usage(root).free,
            'estimated_runtime_hours': [2.5, 3.5],
            'runtime_evidence': 'Original serial regional years1998–2018:155min over20 intervals; global recent years5.4–9min each. EEZ-only pilot pending.'}
    atomic_json(output / 'plan.json', plan)
    return plan


def finite(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def complete_checkpoint(path, kind, layers=(), models=(), grid=None):
    """Validate every array consumed downstream, including interrupted valid ZIPs."""
    import numpy as np
    try:
        with np.load(path, allow_pickle=True) as z:
            if kind == 'coverage':
                cid, cov, ridx = z['cid'], z['cov'], z['ridx']
                ids, title, dimensions = z['region_id'], z['title'], z['grid']
                n = len(ids)
                if not (n and ids.shape == title.shape == (n,) and cid.ndim == 1
                        and len(cid) and cid.shape == cov.shape == ridx.shape
                        and dimensions.shape == (3,) and str(dimensions[0]) == grid):
                    return False
                ny, nx = map(int, dimensions[1:])
                expected = {'4km': (4320, 8640), '12th': (2160, 4320)}[grid]
                return ((ny, nx) == expected and np.issubdtype(cid.dtype, np.integer)
                        and np.issubdtype(ridx.dtype, np.integer) and cid.min() >= 0
                        and cid.max() < ny * nx and ridx.min() >= 0 and ridx.max() < n
                        and np.isfinite(cov).all() and (cov > 0).all() and (cov <= 1).all())
            for layer in layers:
                ids, title = z[f'{layer}_region_id'], z[f'{layer}_title']
                n = len(ids)
                if not n or ids.shape != (n,) or title.shape != (n,):
                    return False
                if kind == 'baseline':
                    shapes = {'carbon_g': (12, n, 5), 'area_m2': (12, n, 5),
                              'mean_year_g': (12, n), 'anomaly_factor': (12, n),
                              'polygon_area_km2': (n,)}
                elif kind == 'ensemble':
                    shapes = {'common_area': (12, n), **{f'{prefix}_{m}': (12, n)
                              for m in models for prefix in ('common', 'own', 'own_area')}}
                else:
                    raise ValueError(f'unknown checkpoint kind: {kind}')
                if any(z[f'{layer}_{suffix}'].shape != shape for suffix, shape in shapes.items()):
                    return False
            return True
    except (OSError, ValueError, KeyError, TypeError, IndexError, EOFError, __import__('zipfile').BadZipFile):
        return False


def complete_watermask(path):
    import numpy as np
    try:
        mask = np.load(path, mmap_mode='r')
        return mask.shape == (4320, 8640) and mask.dtype == np.dtype(bool)
    except (OSError, ValueError, EOFError):
        return False


def code_key(plan):
    return hashlib.sha256(json.dumps(plan['code_sha256'], sort_keys=True).encode()).hexdigest()[:16]


def expected_year_identity(root, plan, year):
    source = plan['source_runs'][str(year)]
    sources = [{'path': source_file(root, r['path']).relative_to(root).as_posix(),
                'bytes': r['bytes'], 'sha256': r['sha256']} for r in source['downloads']]
    inputs = {'geometries': plan['geometries'], 'source_configuration_sha256': source['sha256'],
              'sources': sources, 'code_sha256': plan['code_sha256'],
              'target_rows': [[u, int(y)] for u, y in plan['grid'] if int(y) == year]}
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    return inputs, key


def expected_year_provenance(root, plan, year, key, inputs):
    source = plan['source_runs'][str(year)]
    config = {**source['config'], 'layers': list(plan['geometries']),
              'raw_dir': str(root / 'NPPExtraction/data/raw'),
              'work_dir': str(root / 'NPPExtraction/data/work/regional_expansion' / str(year) / key),
              'out_dir': str(root / OUTPUT / 'years' / str(year) / key)}
    return {'year': year, 'config_key': key, 'method': METHOD, 'config': config,
            'geometries': plan['geometries'], 'downloads': source['downloads'],
            'source_configuration': {'path': source['path'], 'sha256': source['sha256']},
            'verified_source_files': inputs['sources'], 'inputs': inputs,
            'runtime_code': {'sha256': plan['code_sha256'],
                             'snapshot_directory': (OUTPUT / 'execution_sources' / code_key(plan)).as_posix()}}


def completed_year_records(root, plan, year):
    """Accept only outputs belonging to the exact current inputs and execution."""
    inputs, key = expected_year_identity(root, plan, year)
    directory = root / OUTPUT / 'years' / str(year) / key
    done, provenance_path = directory / 'annual_records.json', directory / 'provenance.json'
    if not done.exists() or not provenance_path.exists():
        raise ValueError(f'incomplete current regional result for {year}; stale runs cannot substitute')
    provenance = json.loads(provenance_path.read_text(encoding='utf-8'))
    expected = expected_year_provenance(root, plan, year, key, inputs)
    for field, value in expected.items():
        if provenance.get(field) != value:
            raise ValueError(f'regional provenance identity mismatch: {year}/{field}')
    snapshot = root / expected['runtime_code']['snapshot_directory']
    for relative, checksum in plan['code_sha256'].items():
        if not (snapshot / relative).exists() or digest(snapshot / relative) != checksum:
            raise ValueError(f'regional execution snapshot mismatch: {year}/{relative}')
    required = {done.relative_to(root).as_posix(), *[(directory / f'npp_{year}_{name}.csv').relative_to(root).as_posix()
                for name in ('baseline_by_region', 'baseline_monthly', 'ensemble_by_region')]}
    outputs = provenance.get('outputs', [])
    if {item['path'] for item in outputs} != required or len(outputs) != len(required):
        raise ValueError(f'incomplete hashed regional output set: {year}')
    for item in outputs:
        path = (root / item['path']).resolve()
        if not path.is_relative_to(directory.resolve()) or digest(path) != item['sha256']:
            raise ValueError('completed regional output checksum changed')
    records = json.loads(done.read_text(encoding='utf-8'))
    validate_new_rows(records, inputs['target_rows'], [year])
    for record in records:
        if record.get('provenance') != provenance_path.relative_to(root).as_posix() or record.get('config_key') != key:
            raise ValueError(f'regional record provenance identity mismatch: {year}')
    return records


def annual_record(row, year, models, window, key, provenance):
    prefix = {'eez': 'EEZ', 'lme': 'LME', 'highseas': 'HS'}[row.get('layer', 'eez')]
    record = {'unit_id': f"{prefix}_{int(row['region_id']):03d}", 'year': year,
              'ensemble_basis': row['ensemble_basis'], 'method': METHOD,
              'window_years': ';'.join(map(str, window)), 'config_key': key, 'provenance': provenance,
              'water_area_km2': finite(row['water_area_km2'])}
    statuses = {}
    for model in MODELS:
        value = finite(row.get(f'scaled_{model}_tC_yr')) if record['water_area_km2'] else None
        record[f'npp_{model}_tC_yr'] = value
        statuses[model] = ('available' if value is not None else
                           'unsupported_year' if model not in models else 'no_regional_retrieval')
    values = [record[f'npp_{m}_tC_yr'] for m in MODELS if statuses[m] == 'available']
    record.update(status='complete' if len(values) == 5 else 'partial' if values else 'missing',
                  reason='; '.join(f'{m}: {s}' for m, s in statuses.items() if s != 'available'),
                  model_status=json.dumps(statuses, sort_keys=True), n_models=len(values),
                  available_models=';'.join(m for m in MODELS if statuses[m] == 'available'))
    for label, fn in (('median', statistics.median), ('min', min), ('max', max)):
        record[f'ens_{label}_tC_yr'] = fn(values) if values else None
    return record


def normalize_original_record(row):
    """Same ensemble summary as npp.annual.write_annual for never-published cells."""
    record = dict(row)
    values, models = [], []
    for model in MODELS:
        field = f'npp_{model}_tC_yr'
        record[field] = finite(record.get(field))
        if record[field] is not None:
            values.append(record[field])
            models.append(model)
    record['n_models'] = len(values)
    record['available_models'] = ';'.join(models)
    for label, fn in (('median', statistics.median), ('min', min), ('max', max)):
        record[f'ens_{label}_tC_yr'] = fn(values) if values else None
    record.setdefault('method', METHOD)
    return record


def validate_new_rows(records, grid, supported):
    lookup = unique_rows(records)
    expected = {(u, int(y)) for u, y in grid if int(y) in supported}
    if set(lookup) != expected:
        raise ValueError(f'incomplete regional extraction: expected{len(expected)}, found{len(lookup)}')
    for key, row in lookup.items():
        if row['status'] not in ('complete', 'partial', 'missing'):
            raise ValueError(f'failed or pending regional row: {key}')


def load_plan(root):
    plan = json.loads((root / OUTPUT / 'plan.json').read_text(encoding='utf-8'))
    if digest(root / plan['before_path']) != plan['before_sha256']:
        raise ValueError('original annual snapshot changed')
    for geometry in plan['geometries'].values():
        if digest(root / geometry['path']) != geometry['sha256']:
            raise ValueError('expansion geometry changed')
    return plan


def verify_frozen(root, plan):
    if code_hashes(root) != plan['code_sha256']:
        raise ValueError('regional numerical code changed; prepare a new explicitly versioned plan')
    for source in plan['source_runs'].values():
        if digest(root / source['path']) != source['sha256']:
            raise ValueError('original annual provenance changed')
    for geometry in plan['geometries'].values():
        if digest(root / geometry['source_path']) != geometry['source_sha256']:
            raise ValueError('original full geometry changed')
    legacy = plan['legacy_2019_preserved']
    if digest(root / legacy['path']) != legacy['sha256']:
        raise ValueError('original legacy2019 NPP changed')
    for source in plan['reused_original_sources']:
        if digest(root / source['path']) != source['sha256']:
            raise ValueError('original computed annual records changed')


def extract(root, years):
    plan = load_plan(root)
    verify_frozen(root, plan)
    sys.path.insert(0, str(root / 'NPPExtraction'))
    from npp.config import Config
    from npp.aggregate import run_baseline
    from npp.ensemble import run_ensemble, scale_to_baseline
    from npp.report import baseline_table, ensemble_table
    from npp.regions import build_coverage
    from npp.grids import get_grid
    output = root / OUTPUT
    cache = root / 'NPPExtraction/data/work/regional_expansion'
    cache.mkdir(parents=True, exist_ok=True)
    # Archive the exact executed helper and NPP code separately from frozen global outputs.
    for relative, expected in plan['code_sha256'].items():
        dest = output / 'execution_sources' / code_key(plan) / relative
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, dest)
        if digest(dest) != expected:
            raise ValueError('executed source snapshot differs from plan')
    geometries = plan['geometries']
    for layer, geometry in geometries.items():
        for grid in ('4km', '12th'):
            path = cache / f"coverage_{layer}_{grid}_{geometry['sha256'][:16]}_{code_key(plan)}.npz"
            if not complete_checkpoint(path, 'coverage', grid=grid):
                build_coverage(root / geometry['path'], get_grid(grid), path)
    for year in years:
        started = time.monotonic()
        verify_frozen(root, plan)
        if digest(root / 'NPPExtraction/output/annual_npp.csv') != plan['before_sha256']:
            raise ValueError('canonical CSV changed during extraction')
        source = plan['source_runs'][str(year)]
        verified = verify_sources(root, source['downloads'])
        inputs, key = expected_year_identity(root, plan, year)
        if verified != inputs['sources']:
            raise ValueError('verified sources differ from expected year identity')
        directory = output / 'years' / str(year) / key
        done = directory / 'annual_records.json'
        if done.exists() and (directory / 'provenance.json').exists():
            completed_year_records(root, plan, year)
            print(f'{year}: reusing verified complete extraction', flush=True)
            continue
        cfg = Config.load(**source['config'])
        cfg.layers = list(geometries)
        cfg.raw_dir = root / 'NPPExtraction/data/raw'
        cfg.work_dir = cache / str(year) / key
        cfg.out_dir = directory
        cfg.ensure_dirs()
        if shutil.disk_usage(root).free < 8 * 1024**3:
            raise RuntimeError('fewer than8GiB free')
        cache_inputs = cfg.work_dir / 'inputs.json'
        if cache_inputs.exists() and json.loads(cache_inputs.read_text(encoding='utf-8')) != inputs:
            raise ValueError('regional checkpoint identity changed')
        atomic_json(cache_inputs, inputs)
        for layer, geometry in geometries.items():
            for grid in ('4km', '12th'):
                dest = cfg.coverage_path(layer, grid)
                if not complete_checkpoint(dest, 'coverage', grid=grid):
                    shutil.copyfile(cache / f"coverage_{layer}_{grid}_{geometry['sha256'][:16]}_{code_key(plan)}.npz", dest)
        water_source = root / f"NPPExtraction/data/work/years/{year}/{source['config_key']}" / cfg.watermask_path().name
        if not complete_watermask(cfg.watermask_path()):
            cfg.watermask_path().unlink(missing_ok=True)
            if complete_watermask(water_source):
                shutil.copyfile(water_source, cfg.watermask_path())
        print(f'{year}: regional baseline for{len(plan["target_units"])} targets; models={cfg.ensemble.models}', flush=True)
        baseline = cfg.work_dir / f'baseline_{year}_4km.npz'
        if not complete_checkpoint(baseline, 'baseline', layers=cfg.layers):
            run_baseline(cfg)
        base = baseline_table(cfg, baseline)
        ensemble = cfg.work_dir / f'ensemble_{year}_12th.npz'
        if not complete_checkpoint(ensemble, 'ensemble', layers=cfg.layers, models=cfg.ensemble.models):
            run_ensemble(cfg)
        table = scale_to_baseline(cfg, base, ensemble)
        ensemble_table(cfg, table)
        provenance_path = (directory / 'provenance.json').relative_to(root).as_posix()
        records = [annual_record(r, year, cfg.ensemble.models, cfg.window_years, key, provenance_path)
                   for r in table.to_dict('records')]
        expected = [(u, y) for u, y in plan['grid'] if int(y) == year]
        wanted = {u for u, _ in expected}
        records = [r for r in records if r['unit_id'] in wanted]
        present = {r['unit_id'] for r in records}
        for unit in sorted(wanted - present):
            records.append({'unit_id': unit, 'year': year, 'status': 'missing',
                            'reason': 'no usable region geometry after repair', 'provenance': provenance_path,
                            'config_key': key, 'method': METHOD})
        validate_new_rows(records, expected, [year])
        verify_frozen(root, plan)
        verify_sources(root, source['downloads'])
        atomic_json(done, records)
        products = [done, *sorted(directory.glob('*.csv'))]
        expected_provenance = expected_year_provenance(root, plan, year, key, inputs)
        if cfg.as_dict() != expected_provenance['config']:
            raise ValueError('executed configuration differs from expected source configuration')
        atomic_json(directory / 'provenance.json', {
            **expected_provenance,
            'completed_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - started,
            'coverage_note': 'Coverage-limited water estimates; completed integration is not full source-water or pixel-day coverage.',
            'outputs': [{'path': p.relative_to(root).as_posix(), 'sha256': digest(p)} for p in products]})
        for disposable in cfg.work_dir.glob('*.hdf'):
            disposable.unlink()
        print(f'{year}: complete {len(records)} rows in {time.monotonic() - started:.1f}s', flush=True)


def publish(root):
    plan = load_plan(root)
    verify_frozen(root, plan)
    old = rows(root / plan['before_path'])
    canonical = root / 'NPPExtraction/output/annual_npp.csv'
    records = []
    for year in plan['years']:
        records.extend(completed_year_records(root, plan, year))
    validate_new_rows(records, plan['grid'], plan['years'])
    records.extend(plan['reused_original_records'])
    for unit, year in plan['grid']:
        if int(year) not in plan['years']:
            records.append({'unit_id': unit, 'year': year, 'status': 'unsupported',
                            'reason': 'reference source has no complete twelve-month year', 'n_models': 0, 'method': METHOD})
    fields = list(old[0])
    # CSV normalization applies only to additions; existing cells retain their strings.
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)
    buffer.seek(0)
    new = list(csv.DictReader(buffer))
    merged = merge_rows(old, new)
    proof = preservation_report(old, merged)
    previous = digest(canonical)
    if previous != plan['before_sha256']:
        if rows(canonical) == merged:
            return json.loads((root / OUTPUT / 'publication_verification.json').read_text(encoding='utf-8'))
        raise ValueError('canonical annual CSV changed before publication')
    candidate = root / OUTPUT / 'annual_expanded.csv'
    with candidate.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(merged)
    preservation_report(old, rows(candidate))
    temporary = canonical.with_suffix('.csv.part')
    shutil.copyfile(candidate, temporary)
    temporary.replace(canonical)
    proof.update(before_sha256=plan['before_sha256'], after_sha256=digest(canonical),
                 new_rows=len(new), total_rows=len(merged), new_units=len(plan['target_units']),
                 new_supported_rows=sum(int(r['year']) in plan['years'] for r in new),
                 reused_original_supported_cells=len(plan['reused_original_records']),
                 legacy_2019_preserved=plan['legacy_2019_preserved'], npp_only_units=plan['npp_only_units'],
                 statuses=dict(__import__('collections').Counter(r['status'] for r in new)),
                 years=plan['years'], published_at=dt.datetime.now(dt.timezone.utc).isoformat())
    atomic_json(root / OUTPUT / 'publication_verification.json', proof)
    return proof


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'extract', 'publish'))
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--years', default='1998:2019')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.action == 'plan':
        plan = make_plan(root)
        print(json.dumps({key: plan[key] for key in ('before_rows', 'source_bytes', 'missing_source_files', 'estimated_runtime_hours')}))
        print(f"Targets={len(plan['target_units'])}; catch-year rows={len(plan['grid'])}; source files={len(plan['source_files'])}")
    elif args.action == 'extract':
        years = (list(range(int(args.years.split(':')[0]), int(args.years.split(':')[1]) + 1))
                 if ':' in args.years else [int(x) for x in args.years.split(',')])
        extract(root, years)
    else:
        print(json.dumps(publish(root)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
