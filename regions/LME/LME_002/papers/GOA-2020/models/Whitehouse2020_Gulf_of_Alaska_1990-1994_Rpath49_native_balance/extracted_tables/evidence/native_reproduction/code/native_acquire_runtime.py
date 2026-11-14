"""Acquire official R and a portable unpacker; never run an installer."""
from pathlib import Path
import hashlib,json,urllib.request,sys
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
DEST=RUN/'inputs/native_runtime_downloads';DEST.mkdir(parents=True,exist_ok=True)
def get(url,name):
    path=DEST/name
    request=urllib.request.Request(url,headers={'User-Agent':'LME002-native-Rpath-reproduction'})
    with urllib.request.urlopen(request,timeout=120) as response,path.open('wb') as target:
        while chunk:=response.read(1024*1024):target.write(chunk)
    print(name,path.stat().st_size,flush=True)
    return path
base='https://cran.r-project.org/bin/windows/base/old/4.5.1/'
md5=get(base+'md5sum.R-4.5.1.txt','md5sum.R-4.5.1.txt')
r=get(base+'R-4.5.1-win.exe','R-4.5.1-win.exe')
expected=md5.read_text().split()[0]
assert hashlib.md5(r.read_bytes()).hexdigest()==expected
api=get('https://api.github.com/repos/jrathlev/InnoUnpacker-Windows-GUI/releases/tags/ui_2_2_13','unpacker_release.json')
release=json.loads(api.read_text(encoding='utf-8'))
print(json.dumps([{'name':a['name'],'url':a['browser_download_url'],'digest':a.get('digest')} for a in release['assets']],indent=2))
manifest={'R_version':'4.5.1','R_url':base+r.name,'R_md5_verified':True,'R_md5':expected,'R_sha256':hashlib.sha256(r.read_bytes()).hexdigest(),'unpacker_release_url':release['html_url'],'purpose':'Portable extraction only; installers not executed; temporary runtime will not modify global installation'}
(DEST/'runtime_acquisition.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
