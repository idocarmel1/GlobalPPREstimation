from pathlib import Path
import hashlib,json
run=Path(__file__).resolve().parents[1]
s=(run/'code/test_atomic_replace_retry.py').read_text(encoding='utf-8-sig')
a=s.index('RUN=Path(__file__)');b=s.index('from tools.project_core.registry.publication',a)
s=s[:a]+"sys.path.insert(0,str(ROOT))\nfrom tools.project_core.maps import build_html as build\n"+s[b:]
s=s.replace("tempfile.TemporaryDirectory(dir=RUN/'qa')","tempfile.TemporaryDirectory()")
compile(s,'installed atomic retry tests','exec');(run/'outputs/test_atomic_replace_retry.installable.py').write_text(s,encoding='utf-8')
qa={'shared_writes':False,'focused_tests_passed':5,'focused_seconds':.674,'red_before_fix':{'failures':1,'errors':2,'passed':2},'max_attempts':6,'delays_seconds':[.2,.4,.8,1.6,3.2],'total_wait_seconds':6.2,'retry_windows_error_codes':[5,32,33],'hashes':{p:hashlib.sha256((run/p).read_bytes()).hexdigest() for p in ['outputs/atomic_replace_retry.patch','outputs/build_html.atomic_retry.proposed.py','outputs/build_html.combined.patch','outputs/test_atomic_replace_retry.installable.py']}}
(run/'qa/atomic_retry_verification.json').write_text(json.dumps(qa,indent=2),encoding='utf-8');print(json.dumps(qa,indent=2))
