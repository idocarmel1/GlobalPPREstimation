"""Read-only source inventory and write-once private snapshots."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
OLD=PROJECT/'research/discard_sensitivity_2026_09_10'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        assert digest(src)==digest(dst),(src,dst)
    else: shutil.copy2(src,dst)
    return dict(source_path=str(src),snapshot_path=str(dst.relative_to(ROOT)),bytes=dst.stat().st_size,sha256=digest(dst))
def run():
    files=[]
    for src in sorted((PROJECT/'PPREstimation/real_models').rglob('*.json')):
        files.append(copy(src,ROOT/'inputs/corpus'/src.relative_to(PROJECT/'PPREstimation/real_models')))
    for src in (OLD/'inputs/PPREstimation/real_models/global_cover_jsons').glob('*.json'):
        files.append(copy(src,ROOT/'inputs/references'/src.name))
    for src in (OLD/'inputs/PPREstimation/output/top10').glob('*.xlsx'):
        files.append(copy(src,ROOT/'inputs/workbooks'/src.name))
    for src in (OLD/'src/experimental_engine').glob('*.py'):
        files.append(copy(src,ROOT/'inputs/frozen_engine'/src.name))
    for name in ['study.json','baseline_checks.json','source_evidence.json']:
        if (OLD/'results'/name).exists(): files.append(copy(OLD/'results'/name,ROOT/'inputs/original_results'/name))
    result=dict(schema_version=1,created_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),files=files)
    target=ROOT/'input_manifest.json'
    if not target.exists(): target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Verified',len(files),'snapshots;',sum(x['bytes'] for x in files),'bytes')
if __name__=='__main__':run()
