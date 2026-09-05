"""Calculate every EEZ, with spatial selection rules used only as flags."""
import argparse
from pathlib import Path
import shutil
import sys
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from ppr_pipeline.pipeline import load_config, run_analysis, summarize_spatial_alternatives
from ppr_pipeline.eez_spatial import build_eez_spatial_outputs
from ppr_pipeline.download import load_units_from_spatial_index, catch_url
from ppr_pipeline.provenance import inspect_eez_archive
from ppr_pipeline.years import common_year_for_archives


def comparison_for_year(root, selected_year):
    """Reuse matching TE=0.1 results or recompute into a separate comparison release."""
    baseline_dir = root/'global_output/tables'
    metadata = json.loads((baseline_dir/'run_metadata.json').read_text(encoding='utf-8'))
    if metadata['year']==selected_year and metadata['transfer_efficiency']==0.1:
        return pd.read_csv(baseline_dir/'global_summary.csv'),'global_output'
    result = run_analysis(root,root/'config/global_eez_comparison.yml',requested_year=selected_year)
    return result['summary'],'eez_comparison_output'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=None)
    args = parser.parse_args()
    config = load_config(ROOT / 'config' / 'eez.yml')
    build_eez_spatial_outputs(ROOT, **config['spatial_flags'])
    units = load_units_from_spatial_index(ROOT / config['scope']['unit_index'])
    archive_audit = []
    for unit in units:
        archive_audit.append({'unit_id':unit['unit_id'],
            **inspect_eez_archive(ROOT / config['scope']['raw_directory'] / f"{unit['unit_id']}-catch.zip",
                unit['sau_region_id'], config['sea_around_us']['data_version_expected']),
            'source_url':catch_url(config['sea_around_us']['api_base_url'],'eez',unit['sau_region_id'])})
    pd.DataFrame(archive_audit).to_csv(ROOT / 'eez_output' / 'tables' / 'archive_audit.csv', index=False, encoding='utf-8-sig')
    comparison_units = load_units_from_spatial_index(ROOT / 'spatial/spatial_units.csv')
    selected_year,year_audit = common_year_for_archives(
        {u['unit_id']:ROOT/config['scope']['raw_directory']/f"{u['unit_id']}-catch.zip" for u in units+comparison_units},
        requested=args.year if args.year is not None else config['analysis'].get('year'),progress=print)
    (ROOT/'eez_output/tables/all_areas_year_audit.json').write_text(json.dumps(year_audit,indent=2),encoding='utf-8')
    result = run_analysis(ROOT, ROOT / 'config' / 'eez.yml', requested_year=selected_year)
    baseline,comparison_output = comparison_for_year(ROOT,selected_year)
    comparison = summarize_spatial_alternatives(pd.concat([result['summary'], baseline], ignore_index=True))
    comparison = comparison.drop(columns=[c for c in comparison if c.startswith(('fraction_global','rank_global','fraction_eez','rank_eez'))],errors='ignore')
    comparison.to_csv(ROOT / 'eez_output' / 'tables' / 'all_areas_summary.csv', index=False, encoding='utf-8-sig')
    metadata_path = ROOT/'eez_output/tables/run_metadata.json'
    metadata = json.loads(metadata_path.read_text())
    metadata['comparison_output_directory'] = comparison_output
    metadata['common_year_scope'] = 'All EEZ, LME and High Seas nonempty archives'
    metadata_path.write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    destination = ROOT / 'eez_output' / 'spatial'
    destination.mkdir(exist_ok=True)
    for name in ('EEZs.geojson', 'LMEs.geojson', 'HighSeas.geojson', 'eez_units.csv', 'spatial_units.csv'):
        shutil.copy2(ROOT / 'spatial' / name, destination / name)
    print(f'Completed {len(result["summary"])} EEZs for {result["year"]}.')


if __name__ == '__main__':
    main()
