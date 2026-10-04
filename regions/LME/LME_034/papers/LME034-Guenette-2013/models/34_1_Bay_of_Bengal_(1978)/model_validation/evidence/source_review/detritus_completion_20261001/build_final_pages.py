"""Build final atlas pages with bounded retries for transient Windows file sharing."""
import json,os,shutil,sys,tempfile,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
sys.path.insert(0,str(ROOT/'tools'))
import build_html
from workbooks import sha

def atomic_with_sharing_retry(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(dir=path.parent,suffix=path.suffix);os.close(fd)
    staged=Path(temporary)
    try:
        staged.write_text(text,encoding='utf-8',newline='\n')
        for attempt in range(21):
            try:
                os.replace(staged,path)
                return
            except PermissionError:
                if attempt==20: raise
                if attempt==0:print('Waiting for transient file-sharing lock: '+str(path.relative_to(ROOT)),flush=True)
                time.sleep(.5)
    except BaseException:
        if staged.exists():
            retained=OUT/'release_staging'/path.relative_to(ROOT/'interactive_map')
            retained.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(staged,retained)
            print('Failed page retained at '+str(retained),flush=True)
        raise
    finally:
        if staged.exists():staged.unlink()

def main():
    expected=json.loads((OUT/'central_integration.json').read_text(encoding='utf-8'))['project_sha256']
    assert sha(ROOT/'Project.xlsx')==expected
    build_html.atomic_text=atomic_with_sharing_retry
    build_html.build(ROOT/'Project.xlsx',ROOT/'interactive_map/index.html')
    assert sha(ROOT/'Project.xlsx')==expected

if __name__=='__main__':main()
