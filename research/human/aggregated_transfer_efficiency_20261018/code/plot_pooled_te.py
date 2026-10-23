"""Pool saved level II-IV efficiencies; preserve negative observations separately.

This script reads the completed collection study, without rerunning or changing
the calculator, model inputs, or the original execution evidence.
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
OUT = STUDY / 'results/full_collection'
EVIDENCE = STUDY / 'evidence'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statistics(values):
    """Values and reported moments use percent / percentage-point units."""
    return {
        'n': int(len(values)),
        'arithmetic_mean_percent': float(np.mean(values)),
        'sample_sd_percentage_points': float(np.std(values, ddof=1)),
        'min_percent': float(np.min(values)),
        'max_percent': float(np.max(values)),
    }


def main():
    source = OUT / 'level_flows.csv'
    summary_source = OUT / 'summary.json'
    source_hashes = {str(p.relative_to(STUDY)): sha256(p)
                     for p in (source, summary_source)}
    rows = pd.read_csv(source, encoding='utf-8')
    summary = json.loads(summary_source.read_text(encoding='utf-8'))
    assert not rows.duplicated(['model_id', 'trophic_level']).any()
    assert rows.groupby('model_id').trophic_level.apply(
        lambda values: set(values) == {2, 3, 4} and len(values) == 3).all()
    assert np.isfinite(rows.TE).all(), 'Do not silently drop undefined estimates'
    model_n = rows.model_id.nunique()
    assert model_n == summary['stage_counts']['construction_status']['ok']
    assert len(rows) == model_n * 3
    # Independently check that the stored quantities are the published ratio.
    component_sum = rows[['predation', 'export', 'respiration',
                          'flow_to_detritus']].sum(axis=1)
    assert np.allclose(rows.throughput, component_sum, rtol=1e-10, atol=1e-10)
    assert (rows.throughput > 0).all()
    assert np.allclose(rows.TE, (rows.predation + rows['export']) / rows.throughput,
                       rtol=1e-10, atol=1e-12)

    nonnegative = rows.loc[rows.TE >= 0].copy()
    negative = rows.loc[rows.TE < 0].copy()
    negative['TE_percent'] = negative.TE * 100
    negative['predation_plus_export'] = negative.predation + negative['export']
    negative_path = OUT / 'negative_level_estimates.csv'
    negative.to_csv(negative_path, index=False, encoding='utf-8')
    values = nonnegative.TE.to_numpy() * 100
    stats = statistics(values)
    all_stats = statistics(rows.TE.to_numpy() * 100)
    bin_width = 4.
    upper_edge = max(40., (math.floor(float(values.max()) / bin_width) + 1) * bin_width)
    bins = np.arange(0., upper_edge + bin_width / 2., bin_width)
    counts, edges = np.histogram(values, bins=bins)
    assert counts.sum() == len(nonnegative)
    assert len(nonnegative) + len(negative) == len(rows)

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'svg.fonttype': 'none', 'hatch.linewidth': .35,
    })
    fig, ax = plt.subplots(figsize=(10.6, 6.6))
    fig.subplots_adjust(left=.10, right=.97, top=.80, bottom=.22)
    heights, _, _ = ax.hist(values, bins=bins, color='#eeeeee', edgecolor='#262626',
                            linewidth=1.2, hatch='...', zorder=2)
    assert np.array_equal(heights.astype(int), counts)
    mu = stats['arithmetic_mean_percent']
    sd = stats['sample_sd_percentage_points']
    x = np.linspace(0, upper_edge, 600)
    normal_counts = (len(values) * bin_width / (sd * np.sqrt(2 * np.pi))
                     * np.exp(-.5 * ((x - mu) / sd) ** 2))
    ax.plot(x, normal_counts, color='#202020', lw=2.,
            label='Normal reference (same mean and SD)', zorder=3)
    ax.set(xlim=(0, upper_edge), ylim=(0, max(heights.max(), normal_counts.max()) * 1.12),
           xlabel='Transfer efficiency (%)', ylabel='Number of level estimates')
    ax.set_xticks(bins)
    ax.grid(axis='y', color='#e5e5e5', linewidth=.6, zorder=0)
    ax.set_axisbelow(True)
    ax.text(.97, .95, f'Mean = {mu:.2f}%\nSD = {sd:.2f} percentage points\nn = {len(values):,}',
            transform=ax.transAxes, va='top', ha='right', fontsize=12,
            linespacing=1.5, bbox={'facecolor': 'white', 'edgecolor': '#555555', 'pad': 10})
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.02), borderaxespad=0,
              frameon=False, fontsize=9)
    fig.text(.10, .94, 'Pooled transfer efficiencies at trophic levels II–IV',
             ha='left', fontsize=18, weight='bold')
    fig.text(.10, .885, f'{model_n} calculable models · {len(rows):,} finite estimates · '
             f'{len(negative)} negative estimates reported separately', fontsize=11, color='#4c4c4c')
    fig.text(.10, .065, f'Bars include all {len(nonnegative):,} nonnegative estimates; bin width = 4 percentage points. '
             'SD uses n − 1.\n'
             'Levels within a model are dependent. Current study settings include EE floor = 0.1; '
             'this is not the 1995 model sample.', fontsize=9, color='#4c4c4c', linespacing=1.6)
    outputs = [negative_path]
    for suffix in ('png', 'svg'):
        path = OUT / f'pooled_te_histogram.{suffix}'
        fig.savefig(path, dpi=200, facecolor='white')
        outputs.append(path)
    plt.close(fig)

    for relative, before in source_hashes.items():
        assert sha256(STUDY / relative) == before, f'Input changed: {relative}'
    report = {
        'source_sha256': source_hashes,
        'script_sha256': sha256(Path(__file__)),
        'inventory_n': summary['inventory_count'],
        'loadable_n': summary['stage_counts']['load_status']['ok'],
        'calculable_n': int(model_n),
        'levels': [2, 3, 4],
        'weighting': 'Each model-level estimate has unit weight; no flow or consumption weighting.',
        'nonnegative_histogram': stats,
        'all_finite_including_negative': all_stats,
        'negative': statistics(negative.TE.to_numpy() * 100) if len(negative) else {'n': 0},
        'negative_records': negative.to_dict(orient='records'),
        'zero_n': int((rows.TE == 0).sum()),
        'above_100_percent_n': int((rows.TE > 1).sum()),
        'bins_percent': edges.tolist(),
        'bin_counts': counts.tolist(),
        'normal_curve': 'Descriptive reference scaled by n times bin width; not a test of normality.',
        'checks': {
            'exactly_one_estimate_per_model_per_level': True,
            'all_estimates_finite': True,
            'stored_throughput_and_TE_recomputed': True,
            'histogram_and_negative_counts_reconcile': True,
            'source_hashes_unchanged': True,
        },
        'output_sha256': {str(p.relative_to(STUDY)): sha256(p) for p in outputs},
    }
    (EVIDENCE / 'pooled_te_histogram.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('calculable_n', 'nonnegative_histogram',
                       'all_finite_including_negative', 'negative', 'checks')}, indent=2))


if __name__ == '__main__':
    main()
