import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent
url=sys.argv[1];size=int(sys.argv[2]);target=base/sys.argv[3]
chunks=target.parent/(target.stem+'_chunks');chunks.mkdir(parents=True,exist_ok=True)
step=131072
def get(start):
 end=min(start+step,size)-1;p=chunks/f'{start:09d}.part';h=p.with_suffix('.headers')
 if p.exists() and p.stat().st_size==end-start+1:return p
 cmd=['curl.exe','-sS','-L','--connect-timeout','8','--max-time','150','-r',f'{start}-{end}',url,'-D',str(h),'-o',str(p)]
 r=subprocess.run(cmd,capture_output=True,text=True)
 valid=r.returncode==0 and p.stat().st_size==end-start+1 and f'content-range: bytes {start}-{end}/{size}' in h.read_text().lower()
 print(start,p.stat().st_size if p.exists() else 0,valid,flush=True)
 if not valid:raise RuntimeError(f'Invalid chunk{start} {r.stderr}')
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:parts=list(ex.map(get,range(0,size,step)))
data=b''.join(p.read_bytes() for p in parts)
assert len(data)==size
target.write_bytes(data)
print(json.dumps({'file':str(target),'size':size,'sha256':hashlib.sha256(data).hexdigest()}),flush=True)
