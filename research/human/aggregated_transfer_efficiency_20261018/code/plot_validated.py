"""Plot the saved validated-seven comparison without executing the calculator."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

STUDY = Path(__file__).resolve().parents[1]
OUT = STUDY / 'results/validated7'


def main():
    source = OUT / 'comparison.json'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = json.loads(source.read_text(encoding='utf-8'))
    rows = result['summary']
    units = [p[0] for p in result['pairs']]
    variants = ['fixed_0.1', 'consumer_mean_Q', 'aggregated_II_IV']
    colors = ['#7b8793', '#007f86', '#b95127']
    labels = ['Fixed 10%', 'Consumer mean (Q weights)', 'Aggregated II–IV (geometric)']
    names = [next(r['label'] for r in rows if r['unit_id'] == unit) for unit in units]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.8), gridspec_kw={'width_ratios': [1, 1.05]})
    y = np.arange(len(units))
    for offset, variant, color, label in zip([-.23, 0, .23], variants, colors, labels):
        selected = [next(r for r in rows if r['unit_id'] == unit and r['variant'] == variant) for unit in units]
        axes[0].scatter([r['TE'] * 100 if r['TE'] is not None else np.nan for r in selected], y + offset,
                        s=48, color=color, label=label, zorder=3)
        if variant != 'fixed_0.1':
            axes[1].scatter([r['regional_ppr_ratio_to_fixed_0.1'] if r['regional_ppr_ratio_to_fixed_0.1'] is not None else np.nan for r in selected],
                            y + offset / 1.7, s=48, color=color, zorder=3)
    for ax in axes:
        ax.set_yticks(y, names)
        ax.invert_yaxis()
        ax.grid(axis='x', color='#dce1e4', linewidth=.7)
        ax.set_axisbelow(True)
    axes[0].set_xlabel('Scalar transfer efficiency (%)')
    axes[0].set_title('Transfer efficiencies', loc='left', weight='bold', pad=14)
    axes[0].set_xlim(left=0)
    axes[1].set_title('2019 regional PPR relative to fixed 10%', loc='left', weight='bold', pad=14)
    axes[1].set_xlabel('PPR ratio to fixed 10% TE (log scale)')
    axes[1].set_xscale('log')
    axes[1].axvline(1, color=colors[0], lw=1.2, ls='--')
    axes[1].tick_params(labelleft=False)
    fig.suptitle('Seven researcher-validated model–region pairs', x=.065, ha='left', fontsize=17, weight='bold', y=.98)
    handles, legends = axes[0].get_legend_handles_labels()
    fig.legend(handles, legends, loc='lower left', bbox_to_anchor=(.06, .075), ncol=3, frameon=False)
    fig.text(.065, .035, 'Same 2019 total-catch allocations and review exclusions. Existing provisional restrictions remain.\n'
             'Aggregated TE uses export-inclusive level flows; all options retain the same cycle-broken SPPR trophic levels.', fontsize=9, color='#454d53')
    fig.subplots_adjust(left=.19, right=.97, top=.86, bottom=.23, wspace=.16)
    fig.savefig(OUT / 'comparison.png', dpi=200, facecolor='white')
    fig.savefig(OUT / 'comparison.svg', facecolor='white')
    plt.close(fig)
    if hashlib.sha256(source.read_bytes()).hexdigest() != before:
        raise ValueError('Saved results changed while plotting')
    print(json.dumps({'source_sha256': before, 'models': len(units), 'plots': ['comparison.png', 'comparison.svg']}))


if __name__ == '__main__':
    main()
