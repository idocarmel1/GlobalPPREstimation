"""Build and execute the EEZ validation notebook, also exporting readable HTML."""
from pathlib import Path
import json
import sys
import tempfile
import nbformat
from nbformat.v4 import new_notebook, new_code_cell as code, new_markdown_cell as md
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from eez_execution import fingerprint, invalidate_execution, record_execution, verify_execution, verify_notebook


def build_notebook(root=ROOT):
    thresholds=json.loads((Path(root)/'eez_output/tables/spatial_validation.json').read_text(encoding='utf8'))['thresholds']
    # Retain configurable precision while displaying ratios with at least two decimals.
    def ratio(value):
        text=f'{value:.12f}'.rstrip('0').rstrip('.')
        whole,_,fraction=text.partition('.')
        return whole+'.'+fraction.ljust(2,'0')
    cells = [
        md('''# All Sea Around Us EEZs — PPR validation (TE = 0.1)

Every official EEZ unit is retained. Earlier spatial selection rules are **flags only**, not filters or replacements. EEZ, LME and High Seas are overlapping analysis systems and their totals must not be added together.

The approved 1995 trophic-chain calculation is `SPPR = 10**(TL-1)` and `PPR = catch tonnes × SPPR`. No alternative 2020 regression is used; the 2020 supplement supplies MeanTL only. The separate /9 carbon conversion remains off. Commercial and functional outputs include both correct aggregation and the intentional catch-weighted-TL Jensen shortcut.'''),
        code('''from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT = Path.cwd()
if not (ROOT/'eez_output/tables').exists():
    ROOT = ROOT.parent
TABLES = ROOT/'eez_output/tables'
metadata = json.loads((TABLES/'run_metadata.json').read_text())
summary = pd.read_csv(TABLES/'eez_summary.csv')
print(f"{metadata['unit_count']} EEZs | year {metadata['year']} | TE={metadata['transfer_efficiency']}")
assert metadata['transfer_efficiency'] == 0.1
display(summary[['unit_id','region_name','total_catch_tonnes','ppr_species','fraction_eez_ppr']].head(20))'''),
        md('## Common year, empty archives and catch reconciliation'),
        code('''years = pd.read_csv(TABLES/'year_availability.csv')
display(years.groupby(['first_year','last_year','source_data_status'],dropna=False).size().rename('units').reset_index())
assert years.loc[years.constrains_common_year,'contains_selected_year'].all()
audit = pd.read_csv(TABLES/'ingestion_audit.csv')
assert audit.reconciled.all()
print('Largest catch reconciliation difference (tonnes):',audit.difference_tonnes.abs().max())
display(summary.loc[summary.total_catch_tonnes==0,['unit_id','region_name']])
print('Empty official source archives are retained and do not constrain common year; zero-catch TL coverage is undefined.')'''),
        md('## Trophic-level matching coverage'),
        code('''coverage = pd.read_csv(TABLES/'tl_coverage.csv')
routes = coverage.groupby(['match_method','tl_source','match_confidence'],as_index=False).agg(catch_tonnes=('catch_tonnes','sum'),taxa_rows=('taxa_count','sum'))
routes['catch_fraction_eez'] = routes.catch_tonnes / summary.total_catch_tonnes.sum()
display(routes)
display(summary.nsmallest(15,'catch_tl_coverage_fraction')[['unit_id','region_name','catch_tl_coverage_fraction','missing_tl_catch_tonnes']])
print('Overall matched catch fraction:',summary.matched_catch_tonnes.sum()/summary.total_catch_tonnes.sum())'''),
        md('## Correct versus intentional Jensen aggregation'),
        code('''jensen = pd.read_csv(TABLES/'jensen_comparison.csv')
valid = jensen.dropna(subset=['ppr_jensen'])
assert (valid.ppr_correct+1e-6 >= valid.ppr_jensen).all()
bias = jensen.groupby('classification',as_index=False).agg(ppr_correct=('ppr_correct','sum'),ppr_jensen=('ppr_jensen','sum'))
bias['underestimate_fraction'] = 1-bias.ppr_jensen/bias.ppr_correct
display(bias)
top = summary.head(20).sort_values('ppr_species')
ax = top.plot.barh(x='region_name',y='ppr_species',legend=False,figsize=(10,8),color='#147D92')
ax.set_xlabel('tonnes primary-production equivalent'); ax.set_ylabel('')
ax.set_title(f"Top 20 EEZs, {metadata['year']}, TE=0.1")
plt.tight_layout(); plt.show()'''),
        md(f'''## Advisory spatial rules

- Addition: intersection with the **union of LMEs** is strictly below {thresholds['low_overlap_threshold']*100:.12g}% of the EEZ area.
- Preference candidate: at least {thresholds['containment_threshold']*100:.12g}% of the LME lies in the EEZ, and EEZ/LME area ratio is at least {ratio(thresholds['prefer_ratio'])}.
- Review flag: the same containment condition, with area ratio at least {ratio(thresholds['review_ratio'])} and below {ratio(thresholds['prefer_ratio'])}.

The configured containment interpretation is provisional. These values describe this run, not fixed defaults. All exact pairwise fractions are provided. Different pairs can trigger both preference and review flags for one EEZ. Small geographic overlap does not imply small catch overlap.'''),
        code('''spatial = json.loads((TABLES/'spatial_validation.json').read_text())
flags = pd.read_csv(TABLES/'eez_selection_flags.csv')
pairs = pd.read_csv(TABLES/'eez_lme_intersections.csv')
print('Thresholds:',spatial['thresholds'])
print('Counts:',spatial['flag_counts'])
print('Area method:',spatial['area_method'])
print('Newly repaired EEZ geometries:',spatial['new_eez_repair_count'])
print('EEZ sum minus union area (km²):',spatial['eez_sum_minus_union_area_km2'])
display(pairs.loc[pairs.flag_prefer_eez_candidate | pairs.flag_review_110_120])
display(flags.loc[flags.flag_add_low_lme_overlap].head(20))'''),
        md('## Separate spatial-system summaries — not additive'),
        code('''all_areas = pd.read_csv(TABLES/'all_areas_summary.csv')
display(all_areas.groupby('region_type').agg(units=('unit_id','size'),catch_tonnes=('total_catch_tonnes','sum'),ppr=('ppr_species','sum')))
assert all_areas.year.nunique()==1
assert np.allclose(all_areas.groupby('region_type').fraction_type_ppr.sum(),1)
print('All Areas Summary ranks and fractions are within each spatial system. There is no mixed EEZ+LME+HS world total.')'''),
        md('## Independent final verification'),
        code('''sys.path.insert(0,str(ROOT/'tools'))
from validate_eez_release import validate
report = validate(ROOT,workbooks=True)
print(json.dumps(report,indent=2))
assert report['status']=='passed'
print('All scientific, spatial and exported workbook checks passed.')'''),
        md('''## Sources and scope limits

- [Sea Around Us definitions](https://www.seaaroundus.org/sea-around-us-area-parameters-and-definitions/): analytical EEZs may be divided by ocean-facing coast or territory; mapped boundaries are not legal authority.
- [Catch reconstruction and allocation](https://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/): catches are not uniformly distributed by area. No area-based catch subtraction is performed here.
- [Sea Around Us downloads](https://www.seaaroundus.org/tools-guide/).
- Pauly & Christensen (1995), *Nature* 374, 255–257; supplied 2020 supplement MeanTL.

Source ZIPs retain all available years. Tables and workbooks calculate the configurable common analysis year. Geometry repairs, normalized dateline layers, input hashes and source URLs are included in the release. This run gathers all data for later selection; it does not construct a disjoint final world partition.'''),
    ]
    return new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})


def main(root=ROOT):
    root=Path(root)
    output=root/'eez_output'
    invalidate_execution(output)
    before=fingerprint(output,include_notebooks=False)
    notebook=build_notebook(root)
    NotebookClient(notebook,timeout=1200,kernel_name='python3',resources={'metadata':{'path':str(root)}}).execute()
    html,_ = HTMLExporter().from_notebook_node(notebook)
    if before!=fingerprint(output,include_notebooks=False):
        raise ValueError('Scientific outputs changed during notebook execution; rerun on a stable snapshot')
    path=output/'PPR_EEZ_validation_executed.ipynb'
    # Stage both artifacts before publication. A failed rerun preserves old files,
    # but cannot be packaged: its former success record was already invalidated.
    with tempfile.TemporaryDirectory(prefix='eez-notebook-',dir=output.parent) as directory:
        staging=Path(directory)
        notebook_path=staging/path.name
        html_path=notebook_path.with_suffix('.html')
        nbformat.write(notebook,notebook_path)
        html_path.write_text(html,encoding='utf-8')
        verify_notebook(notebook_path)
        if not html_path.stat().st_size:
            raise ValueError('Notebook HTML export is empty')
        notebook_path.replace(path)
        html_path.replace(path.with_suffix('.html'))
    record_execution(output)
    print(path)


if __name__ == '__main__':
    main()
