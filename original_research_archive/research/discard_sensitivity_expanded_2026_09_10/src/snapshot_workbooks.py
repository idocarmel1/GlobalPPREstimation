"""Snapshot existing saved outputs after selection; workbook availability never selects a model."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1]
def run():
    selected=json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'));files=[]
    for row in selected:
        name=row['model_id']+'.xlsx';matches=list((PROJECT/'PPREstimation/output').rglob(name))
        if not matches:continue
        src=matches[0];dst=ROOT/'inputs/workbooks'/name
        if not dst.exists():shutil.copy2(src,dst)
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        assert sha(src)==sha(dst)
        files.append(dict(model_id=row['model_id'],source_path=str(src),snapshot_path=str(dst.relative_to(ROOT)),sha256=sha(dst),bytes=dst.stat().st_size))
    target=ROOT/'workbook_input_manifest.v2.json'
    if not target.exists():target.write_text(json.dumps(dict(files=files),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Snapshotted',len(files),'existing selected-model workbooks')
if __name__=='__main__':run()
