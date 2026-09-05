"""Render the selected whole-region map from the delivered polygon layers."""
import argparse
import json
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

parser = argparse.ArgumentParser()
parser.add_argument('history_directory', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
metrics = json.loads((args.history_directory / 'tables/selection_metrics.json').read_text(encoding='utf-8'))
regions = gpd.read_file(args.history_directory / 'spatial/selected_regions.geojson')
gaps = gpd.read_file(args.history_directory / 'spatial/gaps.geojson')
overlaps = gpd.read_file(args.history_directory / 'spatial/overlaps.geojson')
colors = {'LME':'#237B83', 'EEZ':'#E3A458', 'HS':'#A9C7DF', 'High Seas':'#A9C7DF'}
fig, ax = plt.subplots(figsize=(15, 8), facecolor='white')
for kind, part in regions.groupby('region_type'):
    part.plot(ax=ax, color=colors[kind], edgecolor='white', linewidth=.15)
if not gaps.empty:
    gaps.plot(ax=ax, color='#CF4860', edgecolor='none', alpha=.9)
if not overlaps.empty:
    overlaps.plot(ax=ax, color='#754B9E', edgecolor='none', alpha=.7)
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Selected Sea Around Us regions', loc='left', fontsize=17, fontweight='bold', pad=34)
ax.text(0, 1.025, f"{metrics['selected_count']} regions   |   {metrics['coverage_fraction']:.2%} mapped-area coverage   |   "
        f"{metrics['twice_covered_fraction_of_union']:.2%} of selected area overlaps", transform=ax.transAxes, fontsize=11)
ax.legend(handles=[Patch(facecolor=colors['LME'],label='LME'),Patch(facecolor=colors['EEZ'],label='EEZ'),
    Patch(facecolor=colors['HS'],label='High Seas'),Patch(facecolor='#754B9E',label='Overlap'),
    Patch(facecolor='#CF4860',label='Gap within source polygons')], loc='lower center', bbox_to_anchor=(.5,-.17), ncol=5, frameon=False)
ax.grid(alpha=.14, linewidth=.5)
fig.text(.09,.02,'Areas measured on WGS84; map shown in longitude/latitude. Geographic coverage is not PPR coverage.\n'
    'Whole-region PPR retains unknown duplication in overlaps. Blank background is outside the available polygon union.',fontsize=9,color='#555555')
fig.subplots_adjust(top=.84,bottom=.2,left=.08,right=.99)
args.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(args.output,dpi=160,bbox_inches='tight')
plt.close(fig)
print(args.output)
