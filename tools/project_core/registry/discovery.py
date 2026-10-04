"""Canonical identities; work files and Windows shortcuts are never discovery inputs."""
from pathlib import Path

def project_root(path):
    path=Path(path).resolve()
    for candidate in [path,*path.parents]:
        if (candidate/'Project.xlsx').is_file():return candidate
    raise ValueError(f'Cannot locate Project.xlsx above {path}')

def region_directory(root, unit_id):
    if not isinstance(unit_id,str) or '/' in unit_id or '\\' in unit_id or unit_id.split('_')[0] not in {'LME','EEZ','HS'}:
        raise ValueError(f'Invalid region identity: {unit_id}')
    return Path(root)/'regions'/unit_id.split('_')[0]/unit_id

def discover_regions(root):
    result={}
    for kind in ['LME','EEZ','HS']:
        for region in sorted((Path(root)/'regions'/kind).glob('*')):
            if region.is_symlink() or not region.is_dir():continue
            unit=region.name
            if not unit.startswith(kind+'_'):raise ValueError(f'Region identity disagrees with grouping: {region}')
            workbook=region/(unit+'.xlsx')
            if not workbook.is_file():raise ValueError(f'Canonical regional workbook missing: {workbook}')
            if unit in result:raise ValueError(f'Duplicate region identity: {unit}')
            result[unit]=workbook
    return result

def discover_models(region_dir):
    region=Path(region_dir).resolve();result={}
    for pattern in ['papers/*/models/*/model.json','ecobase/*/model.json']:
        for model in sorted(region.glob(pattern)):
            resolved=model.resolve()
            if not resolved.is_relative_to(region) or any(p.is_symlink() for p in [model,*model.parents] if p.is_relative_to(region)):
                raise ValueError(f'Model path escapes canonical region: {model}')
            identity=model.parent.name
            if identity in result:raise ValueError(f'Duplicate model identity {identity}: {result[identity]}, {model}')
            result[identity]=model
    # Unexpected immediate model representations are errors, not additional models.
    for pattern in ['model.json','models/*/model.json','papers/*/model.json','ecobase/model.json']:
        unexpected=next(region.glob(pattern),None)
        if unexpected:raise ValueError(f'Unexpected canonical model location: {unexpected}')
    return result

def resolve_model(region_dir, model_id):
    if not isinstance(model_id,str) or not model_id or any(x in model_id for x in ['/', '\\', '..']):
        raise ValueError(f'Invalid model identity: {model_id}')
    models=discover_models(region_dir)
    if model_id not in models:raise ValueError(f'Unknown regional model {model_id} in {region_dir}')
    return models[model_id]
