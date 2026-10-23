"""Plot pooled no-floor level TE and compare matched floor-on/off observations.

Reads saved model-level flow tables only. The original floor-enabled study and
its histogram are unchanged. Negative observations remain separate records.
"""
from pathlib import Path
import hashlib
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

STUDY = Path(__file__).resolve().parents[1]
OUT = STUDY / 'results/full_collection_no_floor'
ON = STUDY / 'results/full_collection'
EVIDENCE = STUDY / 'evidence/full_collection_no_floor'
CLASSIC_MEAN_PERCENT = 10.13
KEY = ['model_id', 'trophic_level']


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statistics(values):
    values = np.asarray(values, dtype=float)
    return {
        'n': int(len(values)),
        'arithmetic_mean_percent': float(values.mean()) if len(values) else None,
        'sample_sd_percentage_points': float(values.std(ddof=1)) if len(values) > 1 else None,
        'min_percent': float(values.min()) if len(values) else None,
        'max_percent': float(values.max()) if len(values) else None,
    }


def validate_table(rows, summary):
    assert not rows.duplicated(KEY).any(), 'Duplicate model-level estimates'
    assert rows.groupby('model_id').trophic_level.apply(
        lambda values: set(values) == {2, 3, 4} and len(values) == 3).all()
    assert np.isfinite(rows.TE).all(), 'Undefined estimates must not be silently dropped'
    model_n = rows.model_id.nunique()
    aggregation_counts = summary['stage_counts'].get('aggregation_status', {})
    expected_models = aggregation_counts.get('ok', summary['stage_counts']['construction_status']['ok'])
    assert model_n == expected_models and len(rows) == model_n * 3
    components = rows[['predation', 'export', 'respiration', 'flow_to_detritus']]
    assert np.isfinite(components.to_numpy()).all(), 'Undefined flow components'
    assert (rows.throughput > 0).all()
    assert np.allclose(rows.throughput, components.sum(axis=1), rtol=1e-10, atol=1e-10)
    assert np.allclose(rows.TE, (rows.predation + rows['export']) / rows.throughput,
                       rtol=1e-10, atol=1e-12)
    return int(model_n)


def compare_moments(floor_on, no_floor):
    on_stats, off_stats = statistics(floor_on), statistics(no_floor)
    mu_on = on_stats['arithmetic_mean_percent']
    mu_off = off_stats['arithmetic_mean_percent']
    distances = {}
    for label, reference in [('classic_1995_mean', CLASSIC_MEAN_PERCENT), ('round_10_percent', 10.)]:
        on_distance = abs(mu_on - reference)
        off_distance = abs(mu_off - reference)
        distances[label] = {
            'reference_percent': reference,
            'floor_on_absolute_distance_percentage_points': on_distance,
            'no_floor_absolute_distance_percentage_points': off_distance,
            'distance_reduction_percentage_points': on_distance - off_distance,
            'no_floor_closer': bool(off_distance < on_distance),
        }
    return {'floor_on': on_stats, 'no_floor': off_stats,
            'no_floor_minus_floor_on_mean_percentage_points': mu_off - mu_on,
            'distance_to_reference': distances}


def main():
    paths = [OUT / 'level_flows.csv', OUT / 'summary.json',
             ON / 'level_flows.csv', ON / 'summary.json',
             EVIDENCE / 'manifest.json', EVIDENCE / 'verification.json',
             STUDY / 'evidence/full_collection_manifest.json',
             STUDY / 'evidence/full_collection_verification.json']
    source_hashes = {p.relative_to(STUDY).as_posix(): sha256(p) for p in paths}
    off = pd.read_csv(paths[0], encoding='utf-8')
    off_summary = json.loads(paths[1].read_text(encoding='utf-8'))
    on = pd.read_csv(paths[2], encoding='utf-8')
    on_summary = json.loads(paths[3].read_text(encoding='utf-8'))
    off_manifest, off_receipt, on_manifest, on_receipt = [
        json.loads(path.read_text(encoding='utf-8')) for path in paths[4:]]
    assert off_manifest['source_hashes'] == on_manifest['source_hashes']
    assert off_manifest['flag_changes_from_baseline'] == {
        'use_ee_floor': {'baseline': True, 'new': False}}
    assert off_summary['initialization_flags'] == off_manifest['initialization_flags']
    assert on_manifest['initialization_flags']['use_ee_floor'] is True
    for key, digest in on_manifest['code_hashes'].items():
        assert off_manifest['code_hashes'][key] == digest, 'Calculation code changed across runs'
    for manifest, receipt, data_paths in [(off_manifest, off_receipt, paths[:2]),
                                          (on_manifest, on_receipt, paths[2:4])]:
        assert receipt['original_calculation_started_utc'] == manifest['started_utc']
        assert receipt['source_bytes_unchanged'] and receipt['code_bytes_unchanged']
        for path in data_paths:
            key = path.relative_to(STUDY).as_posix()
            assert receipt['output_sha256'][key] == source_hashes[key], 'Changed saved result: ' + key
    # The producing runner records its actual constructor flags in the summary.
    assert off_summary['initialization_flags']['use_ee_floor'] is False
    model_n = validate_table(off, off_summary)
    on_model_n = validate_table(on, on_summary)
    nonnegative = off.loc[off.TE >= 0].copy()
    negative = off.loc[off.TE < 0].copy()
    negative['TE_percent'] = negative.TE * 100
    negative['predation_plus_export'] = negative.predation + negative['export']
    on_nonnegative = on.loc[on.TE >= 0]
    assert len(nonnegative) > 1 and len(on_nonnegative) > 1
    values = nonnegative.TE.to_numpy() * 100
    stats = statistics(values)
    own_populations = compare_moments(on_nonnegative.TE.to_numpy() * 100, values)

    paired = on[KEY + ['TE']].merge(off[KEY + ['TE']], on=KEY, how='outer',
                                  suffixes=('_floor_on', '_no_floor'), indicator=True,
                                  validate='one_to_one')
    shared = paired.loc[paired['_merge'] == 'both'].copy()
    common = shared.loc[(shared.TE_floor_on >= 0) & (shared.TE_no_floor >= 0)].copy()
    assert len(common) > 1
    common['TE_floor_on_percent'] = common.TE_floor_on * 100
    common['TE_no_floor_percent'] = common.TE_no_floor * 100
    common['no_floor_minus_floor_on_percentage_points'] = (
        common['TE_no_floor_percent'] - common['TE_floor_on_percent'])
    matched = compare_moments(common['TE_floor_on_percent'], common['TE_no_floor_percent'])
    delta = common['no_floor_minus_floor_on_percentage_points'].to_numpy()
    matched.update({
        'common_nonnegative_row_n': len(common), 'models_represented': int(common.model_id.nunique()),
        'mean_paired_delta_percentage_points': float(delta.mean()),
        'sample_sd_paired_delta_percentage_points': float(delta.std(ddof=1)),
        'lower_no_floor_n': int((delta < 0).sum()),
        'unchanged_n': int((delta == 0).sum()), 'higher_no_floor_n': int((delta > 0).sum()),
    })
    assert math.isclose(matched['mean_paired_delta_percentage_points'],
                        matched['no_floor_minus_floor_on_mean_percentage_points'],
                        rel_tol=1e-10, abs_tol=1e-12)
    pairing_counts = {
        'floor_on_only_n': int((paired['_merge'] == 'left_only').sum()),
        'no_floor_only_n': int((paired['_merge'] == 'right_only').sum()),
        'shared_finite_rows_n': len(shared), 'common_nonnegative_n': len(common),
        'both_negative_n': int(((shared.TE_floor_on < 0) & (shared.TE_no_floor < 0)).sum()),
        'negative_only_floor_on_n': int(((shared.TE_floor_on < 0) & (shared.TE_no_floor >= 0)).sum()),
        'negative_only_no_floor_n': int(((shared.TE_floor_on >= 0) & (shared.TE_no_floor < 0)).sum()),
    }
    assert (pairing_counts['common_nonnegative_n'] + pairing_counts['both_negative_n']
            + pairing_counts['negative_only_floor_on_n'] + pairing_counts['negative_only_no_floor_n']
            == len(shared))

    width = 4.
    upper_edge = max(40., (math.floor(float(values.max()) / width) + 1) * width)
    bins = np.arange(0., upper_edge + width / 2, width)
    counts, edges = np.histogram(values, bins=bins)
    assert counts.sum() == len(nonnegative)
    assert len(nonnegative) + len(negative) == len(off)
    mu, sd = stats['arithmetic_mean_percent'], stats['sample_sd_percentage_points']
    assert sd > 0
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'svg.fonttype': 'none', 'hatch.linewidth': .35,
    })
    fig, ax = plt.subplots(figsize=(11.4, 7.1))
    fig.subplots_adjust(left=.10, right=.97, top=.77, bottom=.24)
    heights, _, _ = ax.hist(values, bins=bins, color='#eeeeee', edgecolor='#262626',
                            linewidth=1.2, hatch='...', zorder=2)
    assert np.array_equal(heights.astype(int), counts)
    x = np.linspace(0., upper_edge, 600)
    curve = (len(values) * width / (sd * np.sqrt(2 * np.pi))
             * np.exp(-.5 * ((x - mu) / sd) ** 2))
    ax.plot(x, curve, color='#202020', lw=2.,
            label='Normal reference (same mean and SD)', zorder=3)
    ax.axvline(CLASSIC_MEAN_PERCENT, color='#27658b', lw=1.8, ls='--', zorder=4,
               label='Classic 1995 pooled mean: 10.13%')
    ax.set(xlim=(0., upper_edge), ylim=(0., max(heights.max(), curve.max()) * 1.12),
           xlabel='Transfer efficiency (%)', ylabel='Number of level estimates')
    ax.set_xticks(bins)
    ax.grid(axis='y', color='#e5e5e5', linewidth=.6, zorder=0)
    ax.set_axisbelow(True)
    ax.text(.97, .95, f'Mean = {mu:.2f}%\nSD = {sd:.2f} percentage points\nn = {len(values):,}',
            transform=ax.transAxes, va='top', ha='right', fontsize=12, linespacing=1.5,
            bbox={'facecolor': 'white', 'edgecolor': '#555555', 'pad': 10})
    ax.legend(loc='lower left', bbox_to_anchor=(0., 1.02), borderaxespad=0,
              ncol=2, frameon=False, fontsize=9)
    fig.text(.10, .94, 'Pooled transfer efficiencies with the EE floor disabled',
             ha='left', fontsize=18, weight='bold')
    fig.text(.10, .885, f'Levels II–IV · {model_n} calculable models · {len(off):,} finite estimates · '
             f'{len(negative)} negative estimates retained separately', fontsize=11, color='#4c4c4c')
    fig.text(.10, .10,
             f'All {len(nonnegative):,} nonnegative estimates; bin width = 4 percentage points; sample SD uses n − 1.\n'
             f'Floor-on mean = {own_populations["floor_on"]["arithmetic_mean_percent"]:.2f}%; '
             f'no-floor mean = {mu:.2f}%. Common nonnegative support: '
             f'{matched["floor_on"]["arithmetic_mean_percent"]:.2f}% → '
             f'{matched["no_floor"]["arithmetic_mean_percent"]:.2f}% (n = {len(common):,}).\n'
             'Levels within a model are dependent. The classic reference comes from a different model sample and accounting.',
             fontsize=9, color='#4c4c4c', linespacing=1.6)
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    negative_path = OUT / 'negative_level_estimates.csv'
    negative.to_csv(negative_path, index=False, encoding='utf-8')
    common_path = OUT / 'paired_nonnegative_level_estimates.csv'
    common.drop(columns='_merge').to_csv(common_path, index=False, encoding='utf-8')
    outputs = [negative_path, common_path]
    for suffix in ('png', 'svg'):
        path = OUT / f'pooled_te_histogram.{suffix}'
        fig.savefig(path, dpi=200, facecolor='white')
        outputs.append(path)
    plt.close(fig)
    for relative, expected in source_hashes.items():
        assert sha256(STUDY / relative) == expected, f'Input changed: {relative}'
    report = {
        'source_sha256': source_hashes, 'script_sha256': sha256(Path(__file__)),
        'initialization_flags': off_summary['initialization_flags'],
        'inventory_n': off_summary['inventory_count'],
        'loadable_n': off_summary['stage_counts']['load_status']['ok'],
        'calculable_n': model_n, 'floor_on_calculable_n': on_model_n, 'levels': [2, 3, 4],
        'weighting': 'Each model-level estimate has unit weight; no consumption or flow weighting.',
        'nonnegative_histogram': stats,
        'all_finite_including_negative': statistics(off.TE.to_numpy() * 100),
        'negative': statistics(negative.TE.to_numpy() * 100),
        'negative_records': negative.to_dict(orient='records'),
        'zero_n': int((off.TE == 0).sum()), 'above_100_percent_n': int((off.TE > 1).sum()),
        'bins_percent': edges.tolist(), 'bin_counts': counts.tolist(),
        'normal_curve': 'Descriptive reference scaled by n times bin width; not a normality test.',
        'classic_reference': {'mean_percent': CLASSIC_MEAN_PERCENT, 'n_estimates': 140,
            'n_models': 48, 'comparable_population': False,
            'source': 'https://www.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf'},
        'floor_comparison': {'each_nonnegative_population': own_populations,
                            'common_nonnegative_row_support': matched,
                            'pairing_counts': pairing_counts},
        'checks': {'EE_floor_disabled': True, 'exact_model_level_keys': True,
                   'all_estimates_finite': True, 'stored_throughput_and_TE_recomputed': True,
                   'histogram_and_signed_counts_reconcile': True,
                   'common_nonnegative_support_reconciled': True,
                   'original_output_receipts_match': True,
                   'source_inputs_and_calculation_code_match_between_runs': True,
                   'only_EE_floor_flag_changed': True,
                   'paired_delta_equals_difference_of_means': True,
                   'source_hashes_unchanged': True},
        'output_sha256': {p.relative_to(STUDY).as_posix(): sha256(p) for p in outputs},
    }
    (EVIDENCE / 'pooled_te_histogram.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('calculable_n', 'nonnegative_histogram',
                     'negative', 'floor_comparison', 'checks')}, indent=2))


if __name__ == '__main__':
    main()
