from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def build_validation_notebook(output_path: str | Path) -> Path:
    """Create the executable pilot-validation research notebook."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    cells = [
        new_markdown_cell(
            r"""# PPR pilot validation

This notebook validates the five-region Sea Around Us pilot. It is a **pilot prioritization**, not a global estimate. Raw catch includes landings and discards, reported and unreported, for the latest year shared by every pilot archive.

Only the approved Pauly-Christensen trophic-chain calculation is used:

\[
SPPR = 10^{TL-1}
\]

\[
PPR = Catch_{tonnes} \times SPPR
\]

The paper's separate wet-weight-to-carbon divisor of 9 is intentionally omitted, so PPR is reported in tonnes of primary-production equivalent, not grams of carbon."""
        ),
        new_code_cell(
            """from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd()
if not (ROOT / 'output' / 'tables').exists():
    ROOT = ROOT.parent
TABLES = ROOT / 'output' / 'tables'
metadata = json.loads((TABLES / 'run_metadata.json').read_text())
print(f\"Pilot year: {metadata['year']} | TE: {metadata['transfer_efficiency']} | Unit: {metadata['ppr_unit']}\")"""
        ),
        new_markdown_cell("## Regional prioritization and catch totals"),
        new_code_cell(
            """summary = pd.read_csv(TABLES / 'pilot_summary.csv')
display(summary[['rank_pilot_ppr', 'unit_id', 'region_name', 'region_type', 'year',
                 'total_catch_tonnes', 'catch_tl_coverage_fraction', 'ppr_species',
                 'fraction_pilot_ppr']])

ax = summary.sort_values('ppr_species').plot.barh(
    x='region_name', y='ppr_species', legend=False, color='#147D92', figsize=(9, 4.8))
ax.set_title('Species-level PPR by pilot region (2019)')
ax.set_xlabel('tonnes primary-production equivalent')
ax.set_ylabel('')
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell("## Catch and aggregation reconciliation"),
        new_code_cell(
            """validation = pd.read_csv(TABLES / 'validation.csv')
key_checks = ['catch_reconciled', 'commercial_ppr_reconciled', 'functional_ppr_reconciled',
              'commercial_jensen_violations', 'functional_jensen_violations']
display(validation[validation['check'].isin(key_checks)].pivot(index='unit_id', columns='check', values='value'))

boolean_checks = validation[validation['check'].isin(
    ['catch_reconciled', 'commercial_ppr_reconciled', 'functional_ppr_reconciled'])]
assert boolean_checks['value'].astype(str).str.lower().isin(['true', '1', '1.0']).all()
violation_checks = validation[validation['check'].str.endswith('jensen_violations')]
assert pd.to_numeric(violation_checks['value']).eq(0).all()"""
        ),
        new_markdown_cell("## Trophic-level matching coverage"),
        new_code_cell(
            """coverage = pd.read_csv(TABLES / 'tl_coverage.csv')
display(coverage[['unit_id', 'match_method', 'tl_source', 'match_confidence',
                  'taxa_count', 'catch_tonnes', 'catch_fraction']])

coverage_pivot = coverage.pivot_table(index='unit_id', columns='match_method',
                                      values='catch_fraction', aggfunc='sum', fill_value=0)
coverage_pivot.plot.bar(stacked=True, figsize=(10, 4.8), colormap='viridis')
plt.title('Catch-weighted TL matching route by pilot region')
plt.ylabel('fraction of regional catch')
plt.xlabel('')
plt.legend(title='match method', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell(
            """## Correct aggregation versus intentional Jensen-error aggregation

For both commercial and functional groups, the correct method sums species PPR first. The comparison method deliberately averages TL by catch before exponentiating. Because the exponential is convex, the correct estimate is expected to be greater than or equal to the Jensen-error estimate, apart from floating-point noise."""
        ),
        new_code_cell(
            """jensen = pd.read_csv(TABLES / 'jensen_comparison.csv')
regional_bias = (jensen.groupby(['unit_id', 'region_name', 'classification'], as_index=False)
                 .agg(ppr_correct=('ppr_correct', 'sum'), ppr_jensen=('ppr_jensen', 'sum')))
regional_bias['underestimate_fraction'] = 1 - regional_bias['ppr_jensen'] / regional_bias['ppr_correct']
display(regional_bias)

pivot = regional_bias.pivot(index='region_name', columns='classification', values='underestimate_fraction')
pivot.plot.bar(figsize=(10, 4.8), color=['#147D92', '#E28A32'])
plt.title('Jensen shortcut underestimation by region and classification')
plt.ylabel('1 - PPR Jensen / PPR correct')
plt.xlabel('')
plt.axhline(0, color='#333333', linewidth=0.8)
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell("## Final validation gate"),
        new_code_cell(
            """assert summary['year'].nunique() == 1
positive_catch = summary['total_catch_tonnes'] > 0
assert summary.loc[positive_catch, 'catch_tl_coverage_fraction'].between(0, 1).all()
assert summary.loc[~positive_catch, 'catch_tl_coverage_fraction'].isna().all()
assert (summary['ppr_species'] - summary['ppr_commercial_correct']).abs().max() < 1e-5
assert (summary['ppr_species'] - summary['ppr_functional_correct']).abs().max() < 1e-5
assert summary['rank_pilot_ppr'].tolist() == list(range(1, len(summary) + 1))
print('All pilot validation gates passed.')"""
        ),
        new_markdown_cell(
            """## Sources and interpretation

- Sea Around Us catch and spatial data: https://www.seaaroundus.org/data/
- Sea Around Us tools/download guide: https://www.seaaroundus.org/tools-guide/
- Pauly, D. & Christensen, V. (1995), *Primary production required to sustain global fisheries*, Nature 374:255-257.
- Luong et al. (2020) supplementary workbook is used only for `MeanTL`; its alternative SPPR estimates are not used.

The ranking compares the five selected pilot regions only. It must not be interpreted as a global ranking until the same frozen workflow is run over every Sea Around Us LME and High Seas unit."""
        ),
    ]
    notebook = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nbformat.write(notebook, output)
    return output


def build_scope_validation_notebook(
    output_path: str | Path,
    *,
    scope_label: str,
    output_directory: str,
    unit_description: str,
) -> Path:
    """Create a compact, executable all-unit validation notebook."""
    if scope_label == "pilot":
        return build_validation_notebook(output_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    cells = [
        new_markdown_cell(
            rf"""# PPR {scope_label} validation

This notebook validates {unit_description} using the Sea Around Us definitions. Catch includes landings and discards, reported and unreported, for the latest year shared by every archive.

Only the approved Pauly-Christensen trophic-chain calculation is used:

\[
SPPR = 10^{{TL-1}}
\]

\[
PPR = Catch_{{tonnes}} \times SPPR
\]

The separate wet-weight-to-carbon divisor of 9 is intentionally omitted. PPR is reported in tonnes of primary-production equivalent."""
        ),
        new_code_cell(
            f"""from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd()
if not (ROOT / '{output_directory}' / 'tables').exists():
    ROOT = ROOT.parent
TABLES = ROOT / '{output_directory}' / 'tables'
metadata = json.loads((TABLES / 'run_metadata.json').read_text())
print(f"Scope: {{metadata['scope']}} | Units: {{metadata['unit_count']}} | Year: {{metadata['year']}} | TE: {{metadata['transfer_efficiency']}}")"""
        ),
        new_markdown_cell("## Global ranking and catch totals"),
        new_code_cell(
            f"""summary = pd.read_csv(TABLES / '{scope_label}_summary.csv')
display(summary[['rank_{scope_label}_ppr', 'unit_id', 'region_name', 'region_type', 'year',
                 'total_catch_tonnes', 'catch_tl_coverage_fraction', 'ppr_species',
                 'fraction_{scope_label}_ppr']].head(25))

top = summary.nsmallest(25, 'rank_{scope_label}_ppr').sort_values('ppr_species')
ax = top.plot.barh(x='region_name', y='ppr_species', legend=False,
                   color='#147D92', figsize=(10, 9))
ax.set_title(f"Top 25 PPR spatial units ({{metadata['year']}})")
ax.set_xlabel('tonnes primary-production equivalent')
ax.set_ylabel('')
plt.tight_layout()
plt.show()

display(summary.groupby('region_type', as_index=False).agg(
    units=('unit_id', 'size'), catch_tonnes=('total_catch_tonnes', 'sum'),
    ppr=('ppr_species', 'sum')))"""
        ),
        new_markdown_cell("## Catch and aggregation reconciliation"),
        new_code_cell(
            """validation = pd.read_csv(TABLES / 'validation.csv')
boolean_names = ['catch_reconciled', 'commercial_ppr_reconciled', 'functional_ppr_reconciled']
boolean_checks = validation[validation['check'].isin(boolean_names)].copy()
boolean_checks['passed'] = boolean_checks['value'].astype(str).str.lower().isin(['true', '1', '1.0'])
violation_checks = validation[validation['check'].str.endswith('jensen_violations')].copy()
violation_checks['value_numeric'] = pd.to_numeric(violation_checks['value'])
display(boolean_checks.groupby('check')['passed'].agg(['sum', 'count']))
display(violation_checks.groupby('check')['value_numeric'].agg(['sum', 'max']))
assert boolean_checks['passed'].all()
assert violation_checks['value_numeric'].eq(0).all()"""
        ),
        new_markdown_cell("## Trophic-level matching coverage"),
        new_code_cell(
            """coverage = pd.read_csv(TABLES / 'tl_coverage.csv')
route = coverage.groupby(['match_method', 'tl_source', 'match_confidence'], as_index=False).agg(
    taxa_rows=('taxa_count', 'sum'), catch_tonnes=('catch_tonnes', 'sum'))
route['catch_fraction_global'] = route['catch_tonnes'] / route['catch_tonnes'].sum()
display(route.sort_values('catch_tonnes', ascending=False))

low_coverage = summary.nsmallest(20, 'catch_tl_coverage_fraction')[
    ['unit_id', 'region_name', 'region_type', 'catch_tl_coverage_fraction',
     'missing_tl_catch_tonnes', 'taxa_count', 'matched_taxa_count']]
display(low_coverage)

route.set_index('match_method')['catch_fraction_global'].sort_values().plot.barh(
    color='#147D92', figsize=(8, 4.8))
plt.title('Global catch-weighted TL matching routes')
plt.xlabel('fraction of global catch')
plt.ylabel('')
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell(
            """## Correct aggregation versus intentional Jensen-error aggregation

The correct path sums taxon PPR before deriving group SPPR. The comparison path deliberately averages trophic level by catch before exponentiating. Convexity requires correct PPR to be at least the Jensen-error result, apart from numerical tolerance."""
        ),
        new_code_cell(
            """jensen = pd.read_csv(TABLES / 'jensen_comparison.csv')
global_bias = jensen.groupby('classification', as_index=False).agg(
    ppr_correct=('ppr_correct', 'sum'), ppr_jensen=('ppr_jensen', 'sum'))
global_bias['underestimate_fraction'] = 1 - global_bias['ppr_jensen'] / global_bias['ppr_correct']
display(global_bias)

regional_bias = jensen.groupby(['unit_id', 'region_name', 'classification'], as_index=False).agg(
    ppr_correct=('ppr_correct', 'sum'), ppr_jensen=('ppr_jensen', 'sum'))
regional_bias['underestimate_fraction'] = 1 - regional_bias['ppr_jensen'] / regional_bias['ppr_correct']
display(regional_bias.nlargest(25, 'underestimate_fraction'))"""
        ),
        new_markdown_cell("## Final validation gate"),
        new_code_cell(
            f"""assert len(summary) == metadata['unit_count'] == 84
assert summary['year'].nunique() == 1
positive_catch = summary['total_catch_tonnes'] > 0
assert summary.loc[positive_catch, 'catch_tl_coverage_fraction'].between(0, 1).all()
assert summary.loc[~positive_catch, 'catch_tl_coverage_fraction'].isna().all()
assert (summary['ppr_species'] - summary['ppr_commercial_correct']).abs().max() < 1e-4
assert (summary['ppr_species'] - summary['ppr_functional_correct']).abs().max() < 1e-4
assert summary['rank_{scope_label}_ppr'].tolist() == list(range(1, len(summary) + 1))
assert abs(summary['fraction_{scope_label}_ppr'].sum() - 1.0) < 1e-10
print('All {scope_label} validation gates passed.')"""
        ),
        new_markdown_cell(
            """## Sources

- Sea Around Us catch and spatial data: https://www.seaaroundus.org/data/
- Sea Around Us tools/download guide: https://www.seaaroundus.org/tools-guide/
- Pauly, D. & Christensen, V. (1995), *Primary production required to sustain global fisheries*, Nature 374:255-257.
- Luong et al. (2020) supplementary workbook is used only for `MeanTL`; its alternative SPPR estimates are not used."""
        ),
    ]
    notebook = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nbformat.write(notebook, output)
    return output
