"""Bind successful EEZ notebook execution to the exact current scientific outputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile

NOTEBOOK = 'PPR_EEZ_validation_executed.ipynb'
HTML = 'PPR_EEZ_validation_executed.html'
RECORD = 'eez_execution_record.json'


def fingerprint(output, *, include_notebooks=True):
    """Hash exact file membership and bytes; exclude the execution record itself.

    Bind all scientific tables and spatial sidecars recursively, every XLSX,
    and notebook/HTML artifacts. Unrelated previews/logs and the freshly rerun
    release-validation report are outside this execution fingerprint.
    """
    output=Path(output)
    files={}
    for path in sorted(output.rglob('*')):
        if not path.is_file():
            continue
        relative=path.relative_to(output)
        selected=relative.parts[0] in ('tables','spatial') or path.suffix.lower()=='.xlsx'
        selected=selected or (include_notebooks and path.suffix.lower() in ('.ipynb','.html'))
        if not selected or relative.as_posix()==RECORD:
            continue
        digest=hashlib.sha256()
        size=0
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):
                digest.update(chunk)
                size+=len(chunk)
        files[relative.as_posix()]={'sha256':digest.hexdigest(),'size_bytes':size}
    return files


def verify_notebook(path):
    notebook=json.loads(Path(path).read_text(encoding='utf8'))
    count=0
    for index,cell in enumerate(notebook.get('cells',[]),1):
        if cell.get('cell_type')!='code':
            continue
        if any(item.get('output_type')=='error' for item in cell.get('outputs',[])):
            raise ValueError(f'Notebook cell {index} contains an error')
        source=cell.get('source','')
        source=''.join(source) if isinstance(source,list) else source
        if source.strip():
            execution=cell.get('execution_count')
            if type(execution) is not int or execution<1:
                raise ValueError(f'Notebook cell {index} was not executed')
            count+=1
    if not count:
        raise ValueError('Notebook has no executed nonempty code cells')
    return count


def invalidate_execution(output):
    """Invalidate previous success before starting any notebook rerun."""
    (Path(output)/RECORD).unlink(missing_ok=True)


def record_execution(output):
    """Record only after successful execution and publication of notebook + HTML."""
    output=Path(output)
    invalidate_execution(output)
    count=verify_notebook(output/NOTEBOOK)
    if not (output/HTML).is_file() or not (output/HTML).stat().st_size:
        raise ValueError('Successful notebook HTML export is missing or empty')
    files=fingerprint(output)
    record={'schema_version':1,'status':'passed','executed_code_cells':count,
        'recorded_utc':datetime.now(timezone.utc).isoformat(),'files':files}
    # Avoid leaving a partially written record that looks like success.
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',suffix='.tmp',dir=output,delete=False) as stream:
        temporary=Path(stream.name)
        json.dump(record,stream,indent=2)
    try:
        temporary.replace(output/RECORD)
    finally:
        temporary.unlink(missing_ok=True)
    return record


def verify_execution(output):
    """Reject missing/failed execution, stale bytes, or changed file membership."""
    output=Path(output)
    record=json.loads((output/RECORD).read_text(encoding='utf8'))
    if record.get('schema_version')!=1 or record.get('status')!='passed':
        raise ValueError('No supported successful notebook execution record')
    count=verify_notebook(output/NOTEBOOK)
    if count!=record.get('executed_code_cells'):
        raise ValueError('Notebook execution count differs from recorded success')
    if not (output/HTML).is_file() or not (output/HTML).stat().st_size:
        raise ValueError('Successful notebook HTML export is missing or empty')
    if fingerprint(output)!=record.get('files'):
        raise ValueError('EEZ outputs differ from the successful notebook execution snapshot; rerun the notebook')
    return record
