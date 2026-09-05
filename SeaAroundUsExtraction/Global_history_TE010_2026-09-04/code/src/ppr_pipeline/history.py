"""Bounded-memory, resumable annual PPR from the frozen Sea Around Us archives.

Exact/genus assignments are time independent. Group fallback means are fitted
within each year and original release cohort (EEZ or LME+High Seas), never across
years. Whole-region estimates are not de-duplicated geographically.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .calculations import add_species_ppr, aggregate_groups, calculate_sppr
from .download import load_units_from_spatial_index
from .ingest import RAW_REQUIRED_COLUMNS, _catch_csv_name, read_exploited_organisms
from .matching import assign_trophic_levels
from .pipeline import load_trophic_reference


TAXON_KEYS = ['year', 'taxon', 'common_name', 'functional_group', 'commercial_group']
CATCH_COLUMNS = ['catch_tonnes', 'landings_tonnes', 'discards_tonnes',
                 'reported_tonnes', 'unreported_tonnes']
ANNUAL_COLUMNS = ['unit_id', 'region_name', 'region_type', 'year', 'total_catch_tonnes',
                  'matched_catch_tonnes', 'missing_tl_catch_tonnes', 'catch_tl_coverage_fraction',
                  'taxa_count', 'matched_taxa_count', 'ppr_species', 'ppr_commercial_correct',
                  'ppr_functional_correct', 'ppr_commercial_jensen', 'ppr_functional_jensen',
                  'source_data_status']
AUDIT_COLUMNS = ['year', 'raw_rows_selected', 'raw_filtered_tonnes', 'standardized_tonnes',
                 'difference_tonnes', 'reconciled']
REGION_TYPES = {'lme': 'LME', 'highseas': 'High Seas', 'eez': 'EEZ'}


def stream_standardized_archive(path: str | Path, *, chunksize: int = 250_000
                                ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read the CSV once, retaining year in every aggregate and raw catch audit."""
    path = Path(path)
    parts, audits = [], []
    observed_years: set[int] = set()
    with zipfile.ZipFile(path) as zf:
        member = _catch_csv_name(zf, path)
        if not zf.getinfo(member).file_size:
            return pd.DataFrame(columns=TAXON_KEYS + CATCH_COLUMNS), pd.DataFrame(columns=AUDIT_COLUMNS)
        with zf.open(member) as handle:
            for chunk in pd.read_csv(handle, usecols=sorted(RAW_REQUIRED_COLUMNS),
                                     chunksize=chunksize, low_memory=False):
                chunk['year'] = pd.to_numeric(chunk['year'], errors='raise').astype(int)
                observed_years.update(int(y) for y in chunk.year.unique())
                selected = chunk.loc[chunk.catch_type.isin(['Landings', 'Discards']) &
                                     chunk.reporting_status.isin(['Reported', 'Unreported'])].copy()
                selected['tonnes'] = pd.to_numeric(selected['tonnes'], errors='raise')
                if (selected.tonnes < 0).any() or not np.isfinite(selected.tonnes).all():
                    raise ValueError(f'Catch contains negative or non-finite tonnes: {path}')
                audits.append(selected.groupby('year').agg(raw_rows_selected=('tonnes', 'size'),
                                                          raw_filtered_tonnes=('tonnes', 'sum')))
                if selected.empty:
                    continue
                selected = selected.rename(columns={'scientific_name': 'taxon', 'tonnes': 'catch_tonnes'})
                for key in TAXON_KEYS[1:]:
                    selected[key] = selected[key].fillna('Unclassified').replace('', 'Unclassified')
                for source, label, target in [('catch_type', 'Landings', 'landings_tonnes'),
                                              ('catch_type', 'Discards', 'discards_tonnes'),
                                              ('reporting_status', 'Reported', 'reported_tonnes'),
                                              ('reporting_status', 'Unreported', 'unreported_tonnes')]:
                    selected[target] = np.where(selected[source] == label, selected.catch_tonnes, 0.0)
                parts.append(selected.groupby(TAXON_KEYS, sort=False, dropna=False)[CATCH_COLUMNS].sum())
                # Cap intermediate chunk aggregates, not just raw CSV chunk memory.
                if len(parts) >= 12:
                    parts = [pd.concat(parts).groupby(level=list(range(len(TAXON_KEYS))), sort=False).sum()]
    if parts:
        standardized = pd.concat(parts).groupby(level=list(range(len(TAXON_KEYS))), sort=False).sum().reset_index()
        standardized = standardized.sort_values(['year', 'catch_tonnes'], ascending=[True, False]).reset_index(drop=True)
    else:
        standardized = pd.DataFrame(columns=TAXON_KEYS + CATCH_COLUMNS)
    if not observed_years:
        return standardized, pd.DataFrame(columns=AUDIT_COLUMNS)
    audit = pd.concat(audits).groupby(level=0).sum().reindex(sorted(observed_years), fill_value=0)
    totals = standardized.groupby('year').catch_tonnes.sum()
    audit['standardized_tonnes'] = totals.reindex(audit.index, fill_value=0)
    audit['difference_tonnes'] = audit.standardized_tonnes - audit.raw_filtered_tonnes
    audit['reconciled'] = np.isclose(audit.standardized_tonnes, audit.raw_filtered_tonnes, atol=1e-8, rtol=1e-12)
    audit.index.name = 'year'
    if not audit.reconciled.all():
        raise ValueError(f'Annual catch reconciliation failed for {path}')
    return standardized, audit.reset_index()[AUDIT_COLUMNS]


def match_history_static(frame: pd.DataFrame, supplement: pd.DataFrame,
                         sau_reference: pd.DataFrame) -> pd.DataFrame:
    """Reuse the released exact-supplement, local-SAU and supplement-genus hierarchy."""
    keys = ['unit_id', 'taxon', 'commercial_group', 'functional_group']
    unique = frame[keys].drop_duplicates().copy()
    unique['catch_tonnes'] = 0.0
    matched = assign_trophic_levels(unique, supplement, sau_reference,
                                    allow_commercial_group_fallback=False,
                                    allow_functional_group_fallback=False)
    matched = matched.drop(columns='catch_tonnes')
    return frame.merge(matched, on=keys, how='left', validate='many_to_one')


def historical_group_means(frames: Iterable[pd.DataFrame]) -> dict[str, pd.Series]:
    """Match released means: average per taxon across units, then average taxa.

    Region-specific SAU TL may differ for the same taxon. Sum/count is retained
    before the taxon mean so duplicate labels have the same weight as the release.
    """
    parts: dict[str, list[pd.DataFrame]] = {'commercial': [], 'functional': []}
    for frame in frames:
        matched = frame.loc[frame.tl.notna()]
        for classification in parts:
            keys = ['cohort', 'year', f'{classification}_group', 'taxon_key']
            if matched.empty:
                continue
            part = matched.groupby(keys, sort=False).agg(tl_sum=('tl', 'sum'), tl_count=('tl', 'size'))
            parts[classification].append(part)
            if len(parts[classification]) >= 20:
                parts[classification] = [pd.concat(parts[classification]).groupby(level=[0, 1, 2, 3], sort=False).sum()]
    result = {}
    for classification, chunks in parts.items():
        if not chunks:
            result[classification] = pd.Series(dtype=float)
            continue
        sums = pd.concat(chunks).groupby(level=[0, 1, 2, 3], sort=False).sum()
        result[classification] = (sums.tl_sum / sums.tl_count).groupby(level=[0, 1, 2], sort=True).mean().rename('tl')
    return result


def _aggregate_history_groups(species: pd.DataFrame, column: str, te: float) -> pd.DataFrame:
    """Vectorized annual form of aggregate_groups; tested against that implementation."""
    schema = list(aggregate_groups(species.iloc[:0], column, te=te).columns)
    if species.empty:
        return pd.DataFrame(columns=['year'] + schema)
    work = species.copy()
    work[column] = work[column].fillna('Unclassified').replace('', 'Unclassified')
    work['matched'] = work.tl.notna()
    work['matched_catch'] = work.catch_tonnes.where(work.matched, 0.0)
    work['weighted_tl'] = (work.catch_tonnes * work.tl).fillna(0.0)
    group = work.groupby(['year', column], sort=True).agg(
        taxon_count_total=('catch_tonnes', 'size'), taxon_count_matched=('matched', 'sum'),
        catch_tonnes_total=('catch_tonnes', 'sum'), catch_tonnes_matched=('matched_catch', 'sum'),
        ppr_correct=('ppr', 'sum'), weighted_tl=('weighted_tl', 'sum'))
    group.loc[group.taxon_count_matched == 0, 'ppr_correct'] = np.nan
    group['catch_tonnes_missing_tl'] = group.catch_tonnes_total - group.catch_tonnes_matched
    group['catch_coverage_fraction'] = group.catch_tonnes_matched / group.catch_tonnes_total.replace(0, np.nan)
    denominator = group.catch_tonnes_matched.replace(0, np.nan)
    group['sppr_correct'] = group.ppr_correct / denominator
    group['tl_weighted_jensen'] = group.weighted_tl / denominator
    group['sppr_jensen'] = calculate_sppr(group.tl_weighted_jensen, te=te)
    group['ppr_jensen'] = group.catch_tonnes_matched * group.sppr_jensen
    group['jensen_difference'] = group.ppr_correct - group.ppr_jensen
    group['jensen_ratio_correct_to_error'] = group.ppr_correct / group.ppr_jensen.replace(0, np.nan)
    group['jensen_percent_difference'] = group.jensen_difference / group.ppr_jensen.replace(0, np.nan)
    return group.reset_index()[['year'] + schema]


def finish_history(static: pd.DataFrame, means: dict[str, pd.Series], *, te: float = 0.1
                   ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    species = static.copy()
    for classification in ['commercial', 'functional']:
        column = f'{classification}_group'
        if species.empty or means[classification].empty:
            continue
        indexes = pd.MultiIndex.from_frame(species[['cohort', 'year', column]])
        fallback = pd.Series(means[classification].reindex(indexes).to_numpy(), index=species.index)
        mask = species.tl.isna() & fallback.notna()
        species.loc[mask, 'tl'] = fallback.loc[mask]
        species.loc[mask, 'match_method'] = f'{classification}_group_mean'
        species.loc[mask, 'tl_source'] = f'Exact/genus matched-taxa {classification}-group mean'
        species.loc[mask, 'match_confidence'] = 'low'
        species.loc[mask, 'reference_taxon'] = species.loc[mask, column]
    species = add_species_ppr(species, te=te)
    return (species, _aggregate_history_groups(species, 'commercial_group', te),
            _aggregate_history_groups(species, 'functional_group', te))


def summarize_history(unit: dict, years: Iterable[int], species: pd.DataFrame,
                      commercial: pd.DataFrame, functional: pd.DataFrame,
                      available_years: set[int]) -> pd.DataFrame:
    rows = []
    grouped_species = {int(y): p for y, p in species.groupby('year')}
    commercial_totals = commercial.groupby('year')[['ppr_correct', 'ppr_jensen']].sum()
    functional_totals = functional.groupby('year')[['ppr_correct', 'ppr_jensen']].sum()
    for year in years:
        row = {'unit_id': unit['unit_id'], 'region_name': unit['name'],
               'region_type': REGION_TYPES[unit['sau_region']], 'year': int(year)}
        if year not in available_years:
            row.update({column: np.nan for column in ANNUAL_COLUMNS[4:-1]})
            row['source_data_status'] = 'missing_year' if available_years else 'empty_catch_archive'
        else:
            part = grouped_species.get(int(year), species.iloc[:0])
            total = float(part.catch_tonnes.sum())
            matched = float(part.loc[part.tl.notna(), 'catch_tonnes'].sum())
            row.update(total_catch_tonnes=total, matched_catch_tonnes=matched,
                       missing_tl_catch_tonnes=total - matched,
                       catch_tl_coverage_fraction=matched / total if total else np.nan,
                       taxa_count=len(part), matched_taxa_count=int(part.tl.notna().sum()),
                       ppr_species=float(part.ppr.sum()), source_data_status='available')
            for classification, group_totals in [('commercial', commercial_totals), ('functional', functional_totals)]:
                for calculation in ['correct', 'jensen']:
                    row[f'ppr_{classification}_{calculation}'] = (
                        float(group_totals.loc[year, f'ppr_{calculation}']) if year in group_totals.index else 0.0)
        rows.append(row)
    return pd.DataFrame(rows, columns=ANNUAL_COLUMNS)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(path.name + '.tmp')
    frame.to_csv(temporary, index=False, encoding='utf-8-sig',
                 compression={'method': 'gzip', 'compresslevel': 1, 'mtime': 0} if path.name.endswith('.gz') else None)
    temporary.replace(path)


def _fingerprint(path: Path) -> dict:
    stat = path.stat()
    result = {'name': path.name, 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
    if path.suffix == '.zip':
        with zipfile.ZipFile(path) as zf:
            result['members'] = [{'name': i.filename, 'crc32': i.CRC, 'size': i.file_size} for i in zf.infolist()]
    else:
        result['sha256'] = _sha(path)
    return result


def _validate_annual(unit_id: str, annual: pd.DataFrame, audit: pd.DataFrame,
                     species: pd.DataFrame, commercial: pd.DataFrame,
                     functional: pd.DataFrame) -> pd.DataFrame:
    rows = []
    values = annual.set_index('year')
    for _, ingestion in audit.iterrows():
        year = int(ingestion.year)
        row = values.loc[year]
        part = species.loc[species.year == year]
        checks = {
            'catch_reconciliation': np.isclose(row.total_catch_tonnes, ingestion.raw_filtered_tonnes, atol=1e-8, rtol=1e-12),
            'landings_plus_discards': np.isclose(part.landings_tonnes.sum() + part.discards_tonnes.sum(), row.total_catch_tonnes, atol=1e-8, rtol=1e-12),
            'reported_plus_unreported': np.isclose(part.reported_tonnes.sum() + part.unreported_tonnes.sum(), row.total_catch_tonnes, atol=1e-8, rtol=1e-12),
        }
        for classification, groups in [('commercial', commercial), ('functional', functional)]:
            group = groups.loc[groups.year == year]
            checks[f'{classification}_ppr_equals_species'] = np.isclose(row.ppr_species, row[f'ppr_{classification}_correct'], atol=1e-7, rtol=1e-12)
            valid = group.loc[group.ppr_correct.notna() & group.ppr_jensen.notna()]
            checks[f'{classification}_jensen_inequality'] = bool((valid.ppr_correct + np.maximum(1e-7, valid.ppr_correct.abs() * 1e-12) >= valid.ppr_jensen).all())
        rows.extend({'unit_id': unit_id, 'year': year, 'check': key, 'passed': bool(value)} for key, value in checks.items())
    return pd.DataFrame(rows, columns=['unit_id', 'year', 'check', 'passed'])


def _compare_reference(summary: pd.DataFrame, reference_path: Path) -> pd.DataFrame:
    columns = ['unit_id', 'year', 'metric', 'reference', 'historical', 'difference', 'comparison_status', 'passed']
    if not reference_path.exists():
        return pd.DataFrame(columns=columns)
    reference = pd.read_csv(reference_path)
    rows = []
    actual = summary.set_index(['unit_id', 'year'])
    for _, expected in reference.iterrows():
        key = (expected.unit_id, int(expected.year))
        if key not in actual.index:
            rows.append(dict(unit_id=key[0], year=key[1], metric='region_year', comparison_status='absent_row', passed=False))
            continue
        row = actual.loc[key]
        for metric in ANNUAL_COLUMNS[4:-1]:
            left, right = float(expected[metric]), float(row[metric])
            empty_legacy = row.source_data_status == 'empty_catch_archive' and (left == 0 or np.isnan(left)) and np.isnan(right)
            passed = bool(empty_legacy or np.isclose(left, right, equal_nan=True, atol=1e-7, rtol=1e-10))
            rows.append(dict(unit_id=key[0], year=key[1], metric=metric, reference=left,
                             historical=right, difference=right-left,
                             comparison_status='legacy_empty_zero_to_missing' if empty_legacy else 'numeric_reproduction', passed=passed))
    return pd.DataFrame(rows, columns=columns)


def run_history_pipeline(project_root: str | Path, *, output_root: str | Path | None = None,
                         chunksize: int = 250_000, progress=print) -> dict:
    """Calculate every observed year, keeping originals and release tables read-only."""
    root = Path(project_root).resolve()
    output = Path(output_root).resolve() if output_root else root / 'history_output'
    tables = output / 'tables'
    tables.mkdir(parents=True, exist_ok=True)
    units = (load_units_from_spatial_index(root / 'spatial/spatial_units.csv') +
             load_units_from_spatial_index(root / 'spatial/eez_units.csv'))
    units = sorted(units, key=lambda unit: unit['unit_id'])
    if len({unit['unit_id'] for unit in units}) != len(units):
        raise ValueError('Duplicate region identifiers in spatial indexes')
    raw = root / 'raw_data/SAU_downloads'
    supplement_path = root / 'input/trophic_levels_2020.csv'
    supplement = load_trophic_reference(supplement_path)
    source_code = {name: _sha(Path(__file__).parent / name) for name in ['history.py', 'matching.py', 'calculations.py', 'ingest.py']}
    manifests = []
    audits = []
    all_years: set[int] = set()
    for index, unit in enumerate(units, 1):
        unit_id = unit['unit_id']
        directory = tables / 'regions' / unit_id
        directory.mkdir(parents=True, exist_ok=True)
        manifest_path = directory / 'static_manifest.json'
        static_path, audit_path = directory / 'static_species.csv.gz', directory / 'ingestion_audit.csv'
        archive, exploited = raw / f'{unit_id}-catch.zip', raw / f'{unit_id}-exploited.json'
        inputs = {'unit': unit, 'archive': _fingerprint(archive), 'exploited': _fingerprint(exploited),
                  'supplement_sha256': _sha(supplement_path), 'source_code_sha256': source_code}
        signature = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
        previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
        resumed = (previous.get('signature') == signature and static_path.exists() and audit_path.exists())
        if resumed:
            audit = pd.read_csv(audit_path)
            manifest = previous
        else:
            frame, audit = stream_standardized_archive(archive, chunksize=chunksize)
            frame.insert(0, 'unit_id', unit_id)
            frame.insert(1, 'region_name', unit['name'])
            frame.insert(2, 'region_type', REGION_TYPES[unit['sau_region']])
            frame['cohort'] = 'eez' if unit['sau_region'] == 'eez' else 'lme_highseas'
            sau = read_exploited_organisms(exploited)
            sau['unit_id'] = unit_id
            static = match_history_static(frame, supplement, sau)
            _write_csv(static, static_path)
            _write_csv(audit, audit_path)
            manifest = {'signature': signature, 'inputs': inputs,
                        'years': [int(y) for y in audit.year], 'taxon_year_rows': len(static)}
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        manifests.append(manifest)
        audit = audit.assign(unit_id=unit_id)
        audits.append(audit)
        all_years.update(manifest['years'])
        if progress:
            progress(f'Archive [{index}/{len(units)}] {unit_id}: {len(manifest["years"])} years, {manifest["taxon_year_rows"]} taxon-years' + (' (resumed)' if resumed else ''), flush=True)
    years = sorted(all_years)
    if not years:
        raise ValueError('No observed years across the archive collection')
    final_signature = hashlib.sha256(json.dumps({'signatures': [m['signature'] for m in manifests], 'years': years, 'te': 0.1}, sort_keys=True).encode()).hexdigest()
    if progress:
        progress(f'Fitting year-specific cohort fallback means for {years[0]}–{years[-1]} ({len(years)} years).', flush=True)
    def static_frames():
        for unit in units:
            yield pd.read_csv(tables / 'regions' / unit['unit_id'] / 'static_species.csv.gz', keep_default_na=False,
                              na_values={'tl': [''], 'catch_tonnes': ['']})
    means = historical_group_means(static_frames())
    for classification, values in means.items():
        _write_csv(values.rename('tl').reset_index() if len(values) else pd.DataFrame(columns=['cohort', 'year', f'{classification}_group', 'tl']),
                   tables / f'{classification}_fallback_means.csv')
    annual_parts, validation_parts, missing_parts, coverage_parts = [], [], [], []
    resumed_units = 0
    for index, (unit, manifest, audit) in enumerate(zip(units, manifests, audits), 1):
        directory = tables / 'regions' / unit['unit_id']
        marker = directory / 'completion.json'
        previous = json.loads(marker.read_text(encoding='utf-8')) if marker.exists() else {}
        filenames = ['species.csv.gz', 'commercial.csv.gz', 'functional.csv.gz', 'annual.csv', 'validation.csv', 'missing_tl.csv.gz', 'tl_coverage.csv']
        if previous.get('signature') == final_signature and all((directory / name).exists() for name in filenames):
            resumed_units += 1
            annual = pd.read_csv(directory / 'annual.csv')
            validation = pd.read_csv(directory / 'validation.csv')
            missing = pd.read_csv(directory / 'missing_tl.csv.gz')
            coverage = pd.read_csv(directory / 'tl_coverage.csv')
        else:
            static = pd.read_csv(directory / 'static_species.csv.gz', keep_default_na=False, na_values={'tl': [''], 'catch_tonnes': ['']})
            species, commercial, functional = finish_history(static, means)
            annual = summarize_history(unit, years, species, commercial, functional, set(manifest['years']))
            validation = _validate_annual(unit['unit_id'], annual, audit, species, commercial, functional)
            missing = species.loc[species.tl.isna()]
            coverage = species.groupby(['unit_id', 'year', 'match_method', 'tl_source', 'match_confidence'], dropna=False).agg(taxa_count=('taxon', 'size'), catch_tonnes=('catch_tonnes', 'sum')).reset_index()
            if not validation.passed.all():
                raise ValueError(f'Historical validation failed for {unit["unit_id"]}: {validation.loc[~validation.passed].to_dict("records")}')
            for filename, frame in zip(filenames, [species, commercial, functional, annual, validation, missing, coverage]):
                _write_csv(frame, directory / filename)
            marker.write_text(json.dumps({'signature': final_signature}), encoding='utf-8')
        annual_parts.append(annual)
        validation_parts.append(validation)
        if len(missing):
            missing_parts.append(missing)
        coverage_parts.append(coverage)
        if progress:
            progress(f'PPR [{index}/{len(units)}] {unit["unit_id"]}: {len(annual)} annual rows', flush=True)
    summary = pd.concat(annual_parts, ignore_index=True).sort_values(['unit_id', 'year']).reset_index(drop=True)
    validation = pd.concat(validation_parts, ignore_index=True)
    ingestion = pd.concat(audits, ignore_index=True)
    reference_path = root / 'eez_output/tables/all_areas_summary.csv'
    reproduction = _compare_reference(summary, reference_path)
    missing = pd.concat(missing_parts, ignore_index=True) if missing_parts else pd.DataFrame(columns=['unit_id', 'year', 'taxon', 'catch_tonnes', 'tl'])
    for name, frame in [('annual_regions.csv', summary), ('historical_validation.csv', validation),
                        ('historical_ingestion_audit.csv', ingestion), ('historical_2019_reproduction.csv', reproduction),
                        ('historical_missing_tl.csv.gz', missing), ('historical_tl_coverage.csv', pd.concat(coverage_parts, ignore_index=True))]:
        _write_csv(frame, tables / name)
    # pandas JSON encodes undefined numeric estimates as JSON null, never NaN.
    (tables / 'annual_regions.json').write_text(summary.to_json(orient='records', double_precision=15, force_ascii=False), encoding='utf-8')
    availability = pd.DataFrame([{'unit_id': unit['unit_id'], 'region_name': unit['name'],
                                  'region_type': REGION_TYPES[unit['sau_region']],
                                  'first_year': min(m['years']) if m['years'] else None,
                                  'last_year': max(m['years']) if m['years'] else None,
                                  'year_count': len(m['years']),
                                  'source_data_status': 'available' if m['years'] else 'empty_catch_archive'}
                                 for unit, m in zip(units, manifests)])
    _write_csv(availability, tables / 'historical_year_availability.csv')
    metadata = {'created_utc': datetime.now(timezone.utc).isoformat(), 'unit_count': len(units),
                'year_count': len(years), 'first_year': years[0], 'last_year': years[-1], 'years': years,
                'annual_row_count': len(summary), 'taxon_year_rows': sum(m['taxon_year_rows'] for m in manifests),
                'available_rows': int((summary.source_data_status == 'available').sum()),
                'missing_year_rows': int((summary.source_data_status == 'missing_year').sum()),
                'empty_archive_rows': int((summary.source_data_status == 'empty_catch_archive').sum()),
                'empty_archive_units': availability.loc[availability.year_count == 0, 'unit_id'].tolist(),
                'transfer_efficiency': 0.1, 'apply_wet_weight_to_carbon_divisor': False,
                'ppr_unit': 'tonnes_primary_production_equivalent',
                'matching_cohorts': {'eez': 'all EEZs within each year', 'lme_highseas': 'all LMEs and High Seas within each year'},
                'group_fallback': 'Original exact/genus-matched taxon mean within commercial group, then functional group; taxa deduplicated across the annual cohort.',
                'unavailable_values': 'Blank/null estimates for missing years and empty archives; observed zero catches remain numeric zero.',
                'geographic_scope': 'All overlapping whole-region alternatives; sums are not a deduplicated global census.',
                'missing_tl_taxon_year_rows': len(missing), 'missing_tl_catch_tonnes_sum_over_overlapping_region_years': float(missing.catch_tonnes.sum()),
                'reference_validation_performed': reference_path.exists(), 'reference_comparisons': len(reproduction),
                'legacy_empty_encoding_comparisons': int((reproduction.comparison_status == 'legacy_empty_zero_to_missing').sum()),
                'validation_count': len(validation), 'validation_failures': int((~validation.passed.astype(bool)).sum()),
                'reference_failures': int((~reproduction.passed.astype(bool)).sum()),
                'resumed_units': resumed_units, 'signature': final_signature, 'source_code_sha256': source_code,
                'all_checks_passed': bool(validation.passed.all() and reproduction.passed.all())}
    (tables / 'historical_run_metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    if not metadata['all_checks_passed']:
        raise ValueError(f'Historical output failed validation: {metadata["validation_failures"]} annual checks, {metadata["reference_failures"]} reference checks')
    return {'summary': summary, 'validation': validation, 'metadata': metadata}
