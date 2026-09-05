"""Freeze provenance, manifest and versioned Desktop outputs without replacing earlier releases."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ppr_pipeline.download import load_units_from_spatial_index, regions_url
from ppr_pipeline.provenance import unit_source_urls


def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def record(path,relative_to):
    return {'path':path.relative_to(relative_to).as_posix(),'bytes':path.stat().st_size,'sha256':checksum(path)}


def release_targets(destination):
    destination = Path(destination).resolve()
    prefix = destination.parent/destination.name
    return {'directory':destination,
            'results_zip':prefix.with_name(prefix.name+'_results.zip'),
            'complete_zip':prefix.with_name(prefix.name+'_complete.zip'),
            'delivery_report':prefix.with_name(prefix.name+'_delivery.json')}


def preflight_targets(targets):
    for target in targets.values():
        if target.exists():
            raise FileExistsError(f'Refusing to replace an existing release target: {target}')


def ignored_release_names(directory,names):
    return {name for name in names if name in {'node_modules','__pycache__','.pytest_cache'} or name.endswith('.inspect.ndjson')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',required=True,type=Path)
    args = parser.parse_args()
    targets = release_targets(args.destination)
    preflight_targets(targets)
    destination = targets['directory']
    output = ROOT/'eez_output'
    from validate_eez_release import validate
    from eez_execution import verify_execution
    validation = validate(ROOT,workbooks=True)
    if validation.get('status')!='passed' or validation.get('workbook_count')!=283:
        raise ValueError('A full passing workbook/scientific validation is required before packaging')
    verify_execution(output)
    base = 'https://api.seaaroundus.org/api/v1'
    units = load_units_from_spatial_index(ROOT/'spatial/eez_units.csv') + load_units_from_spatial_index(ROOT/'spatial/spatial_units.csv')
    urls = unit_source_urls(base,units)
    for region in ('eez','lme','highseas'):
        urls[f'{region}_regions.json'] = regions_url(base,region,spatial=False)
        urls[f'{region}_regions_spatial.json'] = regions_url(base,region,spatial=True)
    sources = []
    for name,url in sorted(urls.items()):
        path = ROOT/'raw_data/SAU_downloads'/name
        item = record(path,ROOT)
        item['source_url'] = url
        item['local_file_modified_utc'] = datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()
        sources.append(item)
    provenance = {'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'notes':['Original downloaded bytes are retained. API dates may reflect server caching.',
                 'EEZ/LME/HS source units overlap; no unique world catch sum is asserted.'],
        'trophic_reference':record(ROOT/'input/trophic_levels_2020.csv',ROOT),'sources':sources}
    (ROOT/'input/eez_provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    shutil.copy2(ROOT/'EEZ_README.md',output/'README.md')
    manifest = {'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'validation':validation,'files':[record(p,output) for p in sorted(output.rglob('*')) if p.is_file() and p.name!='deliverable_manifest.json' and not p.name.endswith('.inspect.ndjson')]}
    (output/'deliverable_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    destination.mkdir(parents=True)
    allowed_dirs = ['src','tests','tools','config','input','raw_data','spatial','global_output','eez_output']
    if (ROOT/'eez_comparison_output').exists():
        allowed_dirs.append('eez_comparison_output')
    for name in allowed_dirs:
        shutil.copytree(ROOT/name,destination/name,ignore=ignored_release_names)
    for file in ROOT.iterdir():
        if file.is_file() and file.suffix in ('.py','.md','.txt'):
            shutil.copy2(file,destination/file.name)
    shutil.copy2(ROOT/'EEZ_README.md',destination/'README.md')
    # First create a convenient results-only archive; raw inputs are in the complete archive.
    results_zip = targets['results_zip']
    full_zip = targets['complete_zip']
    with zipfile.ZipFile(results_zip,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for file in sorted((destination/'eez_output').rglob('*')):
            if file.is_file():
                archive.write(file,file.relative_to(destination/'eez_output'))
    with zipfile.ZipFile(full_zip,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
        for file in sorted(destination.rglob('*')):
            if file.is_file():
                archive.write(file,Path(destination.name)/file.relative_to(destination),
                    compress_type=zipfile.ZIP_STORED if file.suffix.lower()=='.zip' else zipfile.ZIP_DEFLATED)
    delivery = {'directory':str(destination),'results_zip':record(results_zip,destination.parent),
        'complete_zip':record(full_zip,destination.parent),'validation':validation}
    report = targets['delivery_report']
    with report.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(delivery,indent=2))
    print(json.dumps(delivery,indent=2))


if __name__=='__main__':
    main()
