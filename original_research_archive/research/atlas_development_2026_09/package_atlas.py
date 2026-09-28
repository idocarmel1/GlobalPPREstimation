"""Package reproducible outputs with short member paths and a SHA-256 manifest."""
from pathlib import Path
import hashlib, json, zipfile

ROOT=Path(__file__).resolve().parent
EXCLUDED={'.venv','__pycache__','.git'}

def main():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not EXCLUDED.intersection(p.relative_to(ROOT).parts) and p.name!='delivery_manifest.json')
    manifest=[]
    for p in files:
        with p.open('rb') as stream: digest=hashlib.file_digest(stream,'sha256').hexdigest()
        manifest.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest})
    manifest_path=ROOT/'delivery_manifest.json'
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    target=ROOT.parent/'PPR_Ecopath_Atlas.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files+[manifest_path]:z.write(p,(Path(ROOT.name)/p.relative_to(ROOT)).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)+1
        longest=max(len(n) for n in z.namelist())
    print(json.dumps({'archive':str(target),'files':len(files)+1,'megabytes':round(target.stat().st_size/1e6,2),'longest_member_path':longest,'crc_verified':True}))

if __name__=='__main__':main()
