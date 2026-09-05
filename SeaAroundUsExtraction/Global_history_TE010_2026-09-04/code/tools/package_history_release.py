"""Copy verified new results into the new Desktop release and create its ZIP."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def copy_new(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if sha256(source)!=sha256(target):
            raise FileExistsError(f'Will not overwrite a different existing delivery file: {target}')
        return
    shutil.copy2(source,target)


def package_release(project_root,output_directory):
    root=Path(project_root).resolve()
    output=Path(output_directory).resolve()
    history=root/'history_output'
    historical=json.loads((history/'tables/historical_run_metadata.json').read_text(encoding='utf-8'))
    selection=json.loads((history/'tables/selection_metrics.json').read_text(encoding='utf-8'))
    saved=json.loads((output/'saved_workbook_validation.json').read_text(encoding='utf-8'))
    if not historical.get('all_checks_passed'):
        raise ValueError('Historical calculations have not passed verification')
    if selection.get('validation',{}).get('status')!='passed':
        raise ValueError('Spatial selection has not passed verification')
    if saved.get('status')!='passed':
        raise ValueError('Saved workbook has not passed verification')
    if not (output/'PPR_global_summary.xlsx').is_file():
        raise FileNotFoundError('Summary workbook is missing')
    if saved.get('output_workbook_sha256') != sha256(output/'PPR_global_summary.xlsx'):
        raise ValueError('Summary workbook changed after saved-file validation')
    skip={'static_species.csv.gz','completion.json','annual_regions.json'}
    for folder in ('tables','spatial'):
        for source in sorted((history/folder).rglob('*')):
            if source.is_file() and source.name not in skip:
                copy_new(source,output/source.relative_to(history))
    copy_new(root/'HISTORY_README.md',output/'README.md')
    for folder in ('src','tests'):
        source_dir=root/folder
        if source_dir.exists():
            for source in sorted(source_dir.rglob('*')):
                if source.is_file() and source.suffix in {'.py','.mjs'} and '__pycache__' not in source.parts:
                    copy_new(source,output/'code'/source.relative_to(root))
    names=['requirements.txt','run_history_pipeline.py','tools/select_regions.py','tools/history_workbook.mjs',
        'tools/build_history_workbook.mjs','tools/eez_workbook.mjs','tools/validate_history_workbook.py',
        'tools/plot_history_selection.py','tools/package_history_release.py']
    for name in names:
        if (root/name).is_file():
            copy_new(root/name,output/'code'/name)
    manifest={'files':{}}
    for file in sorted(output.rglob('*')):
        if file.is_file() and file.name!='deliverable_manifest.json' and not file.name.endswith('.inspect.ndjson'):
            manifest['files'][file.relative_to(output).as_posix()]={'bytes':file.stat().st_size,'sha256':sha256(file)}
    manifest_path=output/'deliverable_manifest.json'
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    archive_path=output.with_suffix('.zip')
    if archive_path.exists():
        raise FileExistsError(f'Archive already exists: {archive_path}')
    with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
        for file in sorted(output.rglob('*')):
            if file.is_file() and not file.name.endswith('.inspect.ndjson'):
                archive.write(file,file.relative_to(output).as_posix())
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError('Release ZIP failed its CRC check')
        entries=len(archive.infolist())
    for name,record in manifest['files'].items():
        if sha256(output/name)!=record['sha256']:
            raise ValueError(f'Delivered file changed during packaging: {name}')
    result={'directory':str(output),'zip_path':str(archive_path),'zip_bytes':archive_path.stat().st_size,
        'zip_sha256':sha256(archive_path),'zip_entries':entries,'verified_file_count':len(manifest['files'])}
    output.with_suffix('.delivery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('project_root',type=Path)
    parser.add_argument('output_directory',type=Path)
    args=parser.parse_args()
    print(json.dumps(package_release(args.project_root,args.output_directory),ensure_ascii=False,indent=2))
