from pathlib import Path
import gzip,hashlib,json,urllib.request,zipfile,sys
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1];D=RUN/'inputs/native_runtime_downloads'
def get(url,name):
 p=D/name
 if p.exists() and p.stat().st_size>0:return p
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'LME002-native-Rpath-reproduction'}),timeout=120) as r,p.open('wb') as f:
  while b:=r.read(1024*1024):f.write(b)
 print(name,p.stat().st_size,flush=True);return p
release=json.loads((D/'unpacker_release.json').read_text(encoding='utf-8'))
asset=next(a for a in release['assets'] if a['name']=='innounp-2.zip')
p=get(asset['browser_download_url'],asset['name'])
assert 'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()==asset['digest']
tools=RUN/'inputs/native_runtime_tools';tools.mkdir(exist_ok=True)
def unzip(p,target):
 with zipfile.ZipFile(p) as z:
  assert all((target/n).resolve().is_relative_to(target.resolve()) for n in z.namelist())
  z.extractall(target)
unzip(p,tools)
base='https://cran.r-project.org/bin/windows/contrib/4.5/'
idx=get(base+'PACKAGES.gz','PACKAGES.gz')
text=gzip.decompress(idx.read_bytes()).decode('utf-8')
block=next(x for x in text.split('\n\n') if x.startswith('Package: data.table\n'))
fields=dict(line.split(': ',1) for line in block.splitlines() if ': ' in line)
name='data.table_'+fields['Version']+'.zip';p=get(base+name,name)
if 'MD5sum' in fields:assert hashlib.md5(p.read_bytes()).hexdigest()==fields['MD5sum']
lib=RUN/'inputs/native_R_library';lib.mkdir(exist_ok=True);unzip(p,lib)
checked=0
for line in (lib/'data.table/MD5').read_text().splitlines():
 if not line.strip():continue
 digest,relative=line.split(maxsplit=1);target=lib/'data.table'/relative.lstrip('*')
 assert target.resolve().is_relative_to((lib/'data.table').resolve())
 assert hashlib.md5(target.read_bytes()).hexdigest()==digest,relative
 checked+=1
manifest=json.loads((D/'runtime_acquisition.json').read_text(encoding='utf-8'))
manifest.update({'unpacker':{'url':asset['browser_download_url'],'sha256':asset['digest'].split(':')[1]},'data.table':{'url':base+name,'version':fields['Version'],'archive_md5_supplied':'MD5sum' in fields,'internal_md5_files_verified':checked,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}})
(D/'runtime_acquisition.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('unpacker_candidates',[str(p.relative_to(RUN)) for p in tools.rglob('innounp.exe')])
