"""Fixed, overlap-free atlas NPP reference and a resumable cached-raster extractor.

The graph reads compact records without importing geospatial dependencies. Extraction
uses the existing NPP package on ONE dissolved LME/high-seas polygon union; it never
adds overlapping region totals or uses the changing global retrieval-mask products.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import sys
from pathlib import Path

from atomic_output import write_text_atomic

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'NPPExtraction/output/global_atlas_reference'
MODEL_IDS = ('antoinemorel', 'vgpm', 'eppley', 'cbpm', 'cafe')
METHOD_KEYS = [f'npp_{m}_tC_yr' for m in MODEL_IDS] + ['ens_median_tC_yr']
REFERENCE_ID = 'atlas_lme_high_seas_union_v1'
CONVENTION = {
    'id': 'median_of_union_model_totals',
    'label': 'Median of complete union-wide NPP model totals',
    'formula': 'median(NPP_model(fixed union)) over every model scheduled for that year',
    'note': 'Models are integrated over one dissolved polygon union, scaled to its gap-filled '
            'Antoine–Morel baseline using the existing NPP common-mask ratio method. This is '
            'not the sum of regional medians. All scheduled models must have finite union totals.',
}
GEOGRAPHY = ('Dissolved union of the fixed Global LME + High Seas set: 66 LMEs and 18 '
             'high-seas identities, including identities with no catch. Overlap is counted once. '
             'This is the geography represented by that atlas set, not total world-ocean NPP; '
             'EEZ waters outside this union are excluded.')
_VERIFIED_SOURCE_FILES = {}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    write_text_atomic(Path(path), json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n')


def _finite(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def guard_cached_inputs(path, inputs):
    """An unfinished numerical stage may only resume with identical frozen inputs."""
    path = Path(path)
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8')) != inputs:
            raise ValueError(f'Global NPP cache inputs changed: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, inputs)


def verify_source_files(root, downloads):
    root = Path(root).resolve()
    raw = (root / 'NPPExtraction/data/raw').resolve()
    result = []
    for item in downloads:
        recorded = str(item['path']).replace('\\', '/')
        marker = 'NPPExtraction/data/raw/'
        if marker not in recorded:
            raise ValueError(f'Unrecognized global NPP source path: {recorded}')
        path = (raw / recorded.split(marker, 1)[1]).resolve()
        if not path.is_relative_to(raw):
            raise ValueError('Global NPP source escapes raw-data directory')
        stat = path.stat()
        key = (str(path), stat.st_size, stat.st_mtime_ns, item['sha256'])
        if key not in _VERIFIED_SOURCE_FILES:
            if stat.st_size != item['bytes'] or sha256(path) != item['sha256']:
                raise ValueError(f'Global NPP source checksum mismatch: {path.name}')
            _VERIFIED_SOURCE_FILES[key] = True
        result.append({'path': path.relative_to(root).as_posix(), 'sha256': item['sha256'], 'bytes': stat.st_size})
    return sorted(result, key=lambda row: row['path'])


def code_hashes(root):
    root = Path(root)
    return {path.relative_to(root).as_posix(): sha256(path) for path in
            [root / 'tools/global_npp_reference.py', *sorted((root / 'NPPExtraction/npp').rglob('*.py'))]}


def complete_npz(path, required):
    """Interrupted writes are disposable caches; preserve them for diagnosis."""
    import numpy as np
    import zipfile
    import pickle
    path = Path(path)
    if not path.exists():
        return False
    try:
        # Own the file handle: NumPy can leak it when opening an interrupted ZIP
        # fails, which otherwise prevents renaming the file on Windows.
        with path.open('rb') as stream:
            with np.load(stream, allow_pickle=True) as data:
                if not set(required) <= set(data.files):
                    raise ValueError('Incomplete cache schema')
                for key in data.files:
                    data[key]  # Force CRC/array decoding before trusting the checkpoint.
        return True
    except (OSError, ValueError, EOFError, zipfile.BadZipFile, pickle.UnpicklingError):
        os.replace(path, path.with_suffix('.incomplete.npz'))
        return False


def reference_payload(years, records, geometry):
    """Export a fixed reference with explicit gaps; no selected-cohort argument exists."""
    years = [int(year) for year in years]
    if len(years) != len(set(years)):
        raise ValueError('Duplicate reference output year')
    lookup = {}
    for record in records:
        year = int(record['year'])
        if year in lookup:
            raise ValueError(f'Duplicate global NPP reference year: {year}')
        if record.get('geometry_sha256') != geometry.get('sha256'):
            raise ValueError(f'Global NPP geometry mismatch: {year}')
        for model, value in record.get('model_totals_tC_yr', {}).items():
            if model not in MODEL_IDS or (value is not None and not _finite(value)):
                raise ValueError(f'Invalid global NPP model total: {year}/{model}/{value}')
        lookup[year] = record
    annual, values = {}, {key: [] for key in METHOD_KEYS}
    for year in years:
        record = lookup.get(year)
        totals = {}
        if record is None:
            status = 'outside_source_coverage' if year < 1998 or year > 2019 else 'not_extracted'
            row = {'status': status, 'source_year': None, 'n_models': 0,
                   'reason': ('Annual satellite reference starts in 1998 and ends in 2019.'
                              if status == 'outside_source_coverage' else
                              'This year has no completed integration over the fixed atlas union.'),
                   'coverage_complete': False, 'geometry_complete': False,
                   'calculation_complete': False}
        else:
            row = dict(record)
            row['source_year'] = year
            computed = record.get('status') in ('complete', 'coverage_limited')
            totals = record.get('model_totals_tC_yr', {}) if computed else {}
            expected = record.get('expected_models', [])
            if not expected or len(expected) != len(set(expected)) or set(expected) - set(MODEL_IDS):
                raise ValueError(f'Invalid expected NPP models: {year}')
            support = [model for model in expected if _finite(totals.get(model))]
            row['n_models'] = len(support)
            row['available_models'] = support
            row['geometry_complete'] = computed
            # Completing the requested polygon computation does not make all its
            # water observed: source masks and excluded far fills remain explicit.
            row['coverage_complete'] = False
            row['coverage_limited'] = True
            row['coverage_status'] = 'source_water_mask_and_fill_limits'
            if row['geometry_complete'] and len(support) != len(expected):
                row['status'] = 'incomplete_model_support'
                row['reason'] = 'A scheduled NPP model lacks a complete union total; ensemble is unavailable.'
            row['ensemble_complete'] = row['geometry_complete'] and len(support) == len(expected)
            row['calculation_complete'] = row['ensemble_complete']
            row['model_support_complete'] = len(support) == len(expected)
            if row['calculation_complete']:
                row['status'] = 'coverage_limited'
            row['water_area_pct_of_polygon'] = record.get('coverage', {}).get('water_area_pct_of_polygon')
            row['reason'] = row.get('reason') or ('Fixed union calculation complete; coverage-limited source-method estimate. '
                'The source window water mask excludes never-retrieved cells, and central NPP excludes far nearest-neighbour fills.')
        median = (statistics.median([totals[m] for m in row['expected_models']])
                  if row.get('ensemble_complete') else None)
        for model in MODEL_IDS:
            values[f'npp_{model}_tC_yr'].append(totals.get(model))
        values['ens_median_tC_yr'].append(median)
        row['npp_denominator_tC_yr'] = median
        row['ensemble_convention'] = CONVENTION['id']
        row.update(complete=bool(row.get('ensemble_complete')), model_count=row['n_models'],
                   model_names=row.get('available_models', []),
                   available_ids=list(geometry['unit_ids']) if row.get('geometry_complete') else [],
                   missing_ids=[] if row.get('geometry_complete') else list(geometry['unit_ids']))
        annual[str(year)] = row
    return {'id': geometry.get('id', REFERENCE_ID), 'label': 'Global atlas NPP',
            'units': list(geometry['unit_ids']), 'unit_ids': list(geometry['unit_ids']),
            'years': years, 'npp': values, 'annual': annual, 'metadata': annual,
            'values': values['ens_median_tC_yr'],
            'units_label': 'tonnes carbon per year', 'default_method': 'ens_median_tC_yr',
            'geography': geometry.get('geography', GEOGRAPHY), 'reference_geography': geometry,
            'overlap_policy': 'Exact dissolved polygon union; both between-system and within-system overlap counted once.',
            'source': OUTPUT + '/reference.json',
            'ensemble_convention': CONVENTION['label'], 'ensemble_details': CONVENTION,
            'coverage_warning': 'Coverage-limited NPP estimate for the fixed atlas union. Source-window water masks '
                                'vary by year; never-retrieved cells and far nearest-neighbour fills are excluded. '
                                'This is not complete world-ocean NPP.',
            'missing_policy': 'Missing annual integrations stay blank. An explicitly selected earliest-year '
                              'proxy may fill only years before the first available reference year; '
                              'it must retain its source year and cannot fill internal or later gaps.',
            'provenance': [r.get('provenance') for r in records if r.get('provenance')]}


def build_global_npp_reference(root=ROOT, years=range(1950, 2020)):
    root = Path(root)
    directory = root / OUTPUT
    geometry_path = directory / 'geometry_manifest.json'
    if geometry_path.exists():
        geometry = json.loads(geometry_path.read_text(encoding='utf-8'))
        actual = root / geometry['path']
        if not actual.exists() or sha256(actual) != geometry['sha256']:
            raise ValueError('Fixed atlas NPP union geometry checksum mismatch')
    else:
        identities = json.loads((root / 'SeaAroundUsExtraction/global_output/tables/units.json').read_text(encoding='utf-8'))
        geometry = {'id': REFERENCE_ID, 'unit_ids': sorted(r['unit_id'] for r in identities),
                    'geography': GEOGRAPHY, 'sha256': None,
                    'status': 'union_integration_not_prepared'}
    records = []
    for path in sorted((directory / 'years').glob('*/record.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        provenance = root / record['provenance']
        if not provenance.exists() or sha256(provenance) != record['provenance_sha256']:
            raise ValueError(f'Global NPP provenance checksum mismatch: {path}')
        records.append(record)
    return reference_payload(years, records, geometry)


def dissolve_geometries(geometries):
    """Dissolve before fractional rasterization, including within-system overlaps."""
    from shapely import make_valid, union_all
    shapes = [make_valid(g) for g in geometries]
    if any(g.is_empty for g in shapes):
        raise ValueError('A fixed reference identity has empty geometry')
    union = make_valid(union_all(shapes))
    summed = sum(g.area for g in shapes)
    return union, {'summed_planar_area_degrees2': summed,
                   'union_planar_area_degrees2': union.area,
                   'overlap_planar_area_degrees2': max(0, summed - union.area),
                   'area_note': 'Planar degrees squared diagnose overlap only; physical area is computed by spherical raster-cell integration.'}


def prepare_geometry(root=ROOT):
    """Create a reproducible, fixed 84-identity union from cached full SAU layers."""
    from shapely.geometry import shape, mapping
    sys.path.insert(0, str(Path(root) / 'NPPExtraction'))
    from npp.regions import clean_geometry, build_coverage
    from npp.grids import get_grid
    root = Path(root)
    directory = root / OUTPUT
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / 'geometry_manifest.json'
    union_path = directory / 'atlas_lme_high_seas_union.geojson'
    identities = json.loads((root / 'SeaAroundUsExtraction/global_output/tables/units.json').read_text(encoding='utf-8'))
    expected = {row['unit_id'] for row in identities}
    if len(expected) != len(identities) or len(expected) != 84 or sum(unit.startswith('LME_') for unit in expected) != 66:
        raise ValueError('Global atlas reference membership changed; define a new versioned geography')
    sources, shapes, found = [], [], []
    for layer, prefix in [('lme', 'LME'), ('highseas', 'HS')]:
        path = root / f'NPPExtraction/data/raw/sau_{layer}_full.geojson'
        data = json.loads(path.read_text(encoding='utf-8'))
        sources.append({'path': path.relative_to(root).as_posix(), 'sha256': sha256(path),
                        'source_endpoint': f'https://api.seaaroundus.org/api/v1/{layer}/'})
        for feature in data['features']:
            unit = f"{prefix}_{int(feature['properties']['region_id']):03d}"
            if unit not in expected:
                continue
            cleaned = clean_geometry(shape(feature['geometry']))
            if cleaned is None:
                raise ValueError(f'Fixed atlas region has no usable geometry: {unit}')
            found.append(unit)
            shapes.append(cleaned)
    if len(found) != len(set(found)) or set(found) != expected:
        raise ValueError('Fixed atlas geometry identities are missing or duplicated')
    union, audit = dissolve_geometries(shapes)
    geojson = {'type': 'FeatureCollection', 'features': [{'type': 'Feature',
                'properties': {'region_id': 1, 'title': 'Fixed atlas LME + high-seas union'},
                'geometry': mapping(union)}]}
    serialized = json.dumps(geojson, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n'
    new_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding='utf-8'))
        if old['sha256'] != new_hash or old['sources'] != sources or old['unit_ids'] != sorted(expected):
            raise ValueError('Frozen atlas geometry or sources changed; require a new reference version')
    write_text_atomic(union_path, serialized)
    manifest = {'id': REFERENCE_ID, 'unit_ids': sorted(expected), 'regions': identities,
                'geography': GEOGRAPHY, 'path': union_path.relative_to(root).as_posix(),
                'sha256': new_hash, 'sources': sources, 'overlap_audit': audit,
                'overlap_handling': 'Exact geometric union after the existing antimeridian and topology repair; fractional cells integrated once.',
                'excluded_system': 'EEZs are not added. EEZ water outside the LME/high-seas union is outside this reference.',
                'source_evidence': 'NPPExtraction/METHODS.md sections 6.2, 6.3 and 7; npp/regions.py, aggregate.py, ensemble.py.'}
    write_json(manifest_path, manifest)
    cache = root / 'NPPExtraction/data/work/global_atlas_reference'
    cache.mkdir(parents=True, exist_ok=True)
    for name in ('4km', '12th'):
        path = cache / f'coverage_union_{name}_{new_hash[:12]}.npz'
        if not complete_npz(path, ['cid', 'cov', 'ridx', 'region_id', 'title']):
            temporary = cache / f'.coverage_union_{name}_{new_hash[:12]}.npz'
            build_coverage(union_path, get_grid(name), temporary)
            os.replace(temporary, path)
    return manifest


def extract_year(year, geometry, root=ROOT, execution_code=None):
    """Reuse source rasters, source-year settings and the original NPP implementation."""
    import datetime as dt
    import numpy as np
    root = Path(root)
    sys.path.insert(0, str(root / 'NPPExtraction'))
    from npp.config import Config
    from npp.aggregate import run_baseline
    from npp.ensemble import run_ensemble, scale_to_baseline
    from npp.report import baseline_table, ensemble_table
    from npp.grids import get_grid
    from npp.regions import Coverage
    from npp.fill import CATEGORIES
    from npp.solar import days_in_month
    matches = sorted((root / f'NPPExtraction/output/years/{year}').glob('*/provenance.json'))
    if len(matches) != 1:
        raise ValueError(f'Need one canonical source configuration for {year}; found {len(matches)}')
    source_path = matches[0]
    source = json.loads(source_path.read_text(encoding='utf-8'))
    execution_code = execution_code or code_hashes(root)
    if execution_code != code_hashes(root):
        raise ValueError('Global NPP extraction code changed during the running process')
    verified_sources = verify_source_files(root, source['downloads'])
    cfg = Config.load(**source['config'])
    cfg.raw_dir = root / 'NPPExtraction/data/raw'
    source_work = root / f"NPPExtraction/data/work/years/{year}/{source['config_key']}"
    directory = root / OUTPUT / 'years' / str(year)
    directory.mkdir(parents=True, exist_ok=True)
    record_path = directory / 'record.json'
    config_digest = sha256(source_path)
    inputs = {'geometry_sha256': geometry['sha256'], 'unit_ids': geometry['unit_ids'],
              'source_configuration_sha256': config_digest, 'source_files': verified_sources,
              'execution_code_sha256': execution_code}
    input_key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode('utf-8')).hexdigest()
    if record_path.exists():
        old = json.loads(record_path.read_text(encoding='utf-8'))
        if old.get('input_key') != input_key:
            raise ValueError(f'Completed global NPP source inputs changed: {year}')
        if sha256(root / old['provenance']) != old['provenance_sha256']:
            raise ValueError(f'Completed global NPP provenance checksum mismatch: {year}')
        return old
    cache = root / 'NPPExtraction/data/work/global_atlas_reference'
    cfg.work_dir = cache / str(year) / input_key[:16]
    cfg.out_dir = directory
    cfg.layers = ['lme']  # Driver slot only: the sole feature is the complete union.
    cfg.ensure_dirs()
    guard_cached_inputs(cfg.work_dir / 'inputs.json', inputs)
    for name in ('4km', '12th'):
        destination = cfg.coverage_path('lme', name)
        if not destination.exists():
            shutil.copyfile(cache / f"coverage_union_{name}_{geometry['sha256'][:12]}.npz", destination)
    water_source = source_work / cfg.watermask_path().name
    if not cfg.watermask_path().exists() and water_source.exists():
        shutil.copyfile(water_source, cfg.watermask_path())
    baseline_path = cfg.work_dir / f'baseline_{year}_4km.npz'
    if not complete_npz(baseline_path, ['lme_carbon_g', 'lme_area_m2']):
        run_baseline(cfg)
    base = baseline_table(cfg, baseline_path)
    ensemble_path = cfg.work_dir / f'ensemble_{year}_12th.npz'
    if not complete_npz(ensemble_path, ['lme_common_area', 'lme_region_id']):
        run_ensemble(cfg)
    ensemble = scale_to_baseline(cfg, base, ensemble_path)
    ensemble_table(cfg, ensemble)
    if len(base) != 1 or len(ensemble) != 1:
        raise ValueError('Union extraction must produce exactly one geographic region')
    br, er = base.iloc[0], ensemble.iloc[0]
    totals = {model: float(er[f'scaled_{model}_tC_yr']) if math.isfinite(er.get(f'scaled_{model}_tC_yr', float('nan'))) else None
              for model in MODEL_IDS}
    expected = list(cfg.ensemble.models)
    if any(totals[model] is None for model in expected):
        raise ValueError(f'Scheduled global NPP model has no complete union retrieval: {year}')
    small_grid = get_grid('12th')
    cov = Coverage(cfg.coverage_path('lme', '12th'), small_grid)
    polygon_area = float(br['polygon_area_km2'])
    water_area = float(br['water_area_km2'])
    z = np.load(ensemble_path, allow_pickle=True)
    own_area = {m: [float(x / 1e6) for x in z[f'lme_own_area_{m}'][:, 0]] for m in expected}
    common_area = [float(x / 1e6) for x in z['lme_common_area'][:, 0]]
    npz = np.load(baseline_path, allow_pickle=True)
    area_by_category = {cat: [float(x / 1e6) for x in npz['lme_area_m2'][:, 0, index]]
                        for index, cat in enumerate(CATEGORIES)}
    days = np.array([days_in_month(year, month) for month in range(1, 13)])
    central_area_days = sum(float(np.dot(days, area_by_category[cat])) for cat in cfg.fill.central_categories())
    water_area_days = water_area * float(days.sum())
    if execution_code != code_hashes(root):
        raise ValueError('Global NPP extraction code changed during the running process')
    provenance_path = directory / 'provenance.json'
    provenance = {'reference_id': REFERENCE_ID, 'geometry_sha256': geometry['sha256'],
                  'year': year, 'completed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                  'source_configuration': {'path': source_path.relative_to(root).as_posix(), 'sha256': config_digest},
                  'source_downloads': source['downloads'], 'verified_source_files': verified_sources,
                  'config': cfg.as_dict(), 'code_sha256': execution_code, 'input_key': input_key,
                  'ensemble_convention': CONVENTION, 'reference_geography': geometry['path'],
                  'outputs': [{'path': p.relative_to(root).as_posix(), 'sha256': sha256(p)}
                              for p in sorted(directory.glob('*.csv'))]}
    write_json(provenance_path, provenance)
    record = {'year': year, 'status': 'coverage_limited', 'geometry_sha256': geometry['sha256'],
              'input_key': input_key,
              'expected_models': expected, 'model_totals_tC_yr': totals,
              'calculation_complete': True, 'coverage_complete': False, 'coverage_limited': True,
              'ensemble_basis': str(er['ensemble_basis']),
              'ensemble_median_tC_yr': statistics.median(totals[m] for m in expected),
              'source_configuration': provenance['source_configuration'],
              'provenance': provenance_path.relative_to(root).as_posix(),
              'provenance_sha256': sha256(provenance_path),
              'source_year': year, 'window_years': list(cfg.window_years),
              'coverage': {'reference_regions': len(geometry['unit_ids']), 'geometry_complete': True,
                'polygon_area_km2': polygon_area, 'water_area_km2': water_area,
                'water_area_pct_of_polygon': 100 * water_area / polygon_area,
                'central_support_pct_of_water_pixel_days': 100 * central_area_days / water_area_days,
                'central_support_pct_of_polygon_pixel_days': 100 * central_area_days / (polygon_area * float(days.sum())),
                'excluded_far_pct_of_water_pixel_days': (0.0 if cfg.fill.nn_far_in_central else
                    100 * float(np.dot(days, area_by_category['nn_far'])) / water_area_days),
                'common_mask_area_km2_by_month': common_area,
                'own_mask_area_km2_by_model_month': own_area,
                'baseline_area_km2_by_category_month': area_by_category,
                'baseline_npp_tC_yr': float(br['npp_central_tC_yr']),
                'baseline_observed_tC_yr': float(br['npp_observed_tC_yr']),
                'baseline_all_fills_tC_yr': float(br['npp_all_fills_tC_yr']),
                'baseline_far_fill_in_central': cfg.fill.nn_far_in_central,
                'common_mask_threshold_pct': cfg.ensemble.min_common_mask_pct,
                'note': 'Complete fixed polygon union under the source method. Water mask is the source '
                        'window union of retrieved Antoine–Morel pixels; never-retrieved cells are outside '
                        'supported water, not observed zero. Far nearest-neighbour fills are excluded '
                        'from central NPP. Monthly areas expose satellite support and fill coverage.'}}
    write_json(record_path, record)
    for expanded in cfg.work_dir.glob('*.hdf'):
        expanded.unlink()
    print(f"Global atlas NPP {year}: {record['ensemble_median_tC_yr']:.9g} tC/yr; {len(expected)} models", flush=True)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract', action='store_true')
    parser.add_argument('--years', default='1998:2019')
    args = parser.parse_args(argv)
    if args.extract:
        start, end = [int(value) for value in args.years.split(':')]
        years = list(range(start, end + 1))
        if start < 1998 or end > 2019 or start > end:
            raise ValueError('Supported extraction years are 1998–2019')
        execution_code = code_hashes(ROOT)
        geometry = prepare_geometry()
        # Make a useful recent value available first, then complete chronological history.
        for year in sorted(years, key=lambda value: (value != 2019, value)):
            extract_year(year, geometry, execution_code=execution_code)
            write_json(ROOT / OUTPUT / 'reference.json', build_global_npp_reference())
    else:
        payload = build_global_npp_reference()
        print(json.dumps({'reference': payload['id'], 'complete_years': [int(y) for y, r in payload['annual'].items()
                           if r.get('ensemble_complete')], 'regions': len(payload['units'])}, indent=2))


if __name__ == '__main__':
    main()
