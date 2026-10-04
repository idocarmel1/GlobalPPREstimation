"""Freeze exactly the Banc evidence being superseded; never archive unrelated models."""
from pathlib import Path
import hashlib,json,zipfile,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REGION=ROOT/'regions/LME_027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old_dirs=[p for p in (REGION/'models').iterdir() if p.is_dir() and 'Banc_d_Arguin' in p.name]
old_dirs.append(REGION/'papers/CAN-2014/extracted')
baseline=HERE/'baseline';baseline.mkdir(exist_ok=True)
archive=baseline/'superseded_Banc_evidence.zip'
manifest=[]
if archive.exists():
    raise RuntimeError('Baseline already exists; do not silently replace it')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for directory in old_dirs:
        for p in sorted(directory.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(ROOT).as_posix()
            z.write(p,rel)
            manifest.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
with zipfile.ZipFile(archive) as z:
    for item in manifest:
        b=z.read(item['path'])
        assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
protected=[REGION/'LME_027.xlsx',REGION/'Model_validation_27_118_Northwest_Africa_(1987).docx']
protected += list((REGION/'models/27_118_Northwest_Africa_(1987)').rglob('*'))
protected += list((REGION/'models/27_Morissette2009_Northwest_Africa_Table17').rglob('*'))
protected += [p for p in (REGION/'papers/CAN-2014').iterdir() if p.is_file()]
receipt=dict(run_id='BancArguin_20261003',archive=archive.name,archive_sha256=sha(archive),
    archived_files=manifest,all_archived_bytes_verified=True,
    protected_files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in protected if p.is_file()],
    cleanup_authorized=True,cleanup_performed=False)
(baseline/'manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(archived_files=len(manifest),archive_bytes=archive.stat().st_size,protected_files=len(receipt['protected_files']))))
