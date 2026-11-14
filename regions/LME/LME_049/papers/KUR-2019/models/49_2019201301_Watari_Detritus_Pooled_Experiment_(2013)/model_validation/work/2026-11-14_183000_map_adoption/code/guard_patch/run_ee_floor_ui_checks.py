"""Run existing generated-page checks against production or staged UI without writes."""
import sys, json, subprocess, hashlib
from pathlib import Path
from unittest.mock import patch
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd()
sys.path.insert(0,str(ROOT))
OUT=Path(__file__).resolve().parent
from tools.project_core.maps.build_html import linked_layout
mode=sys.argv[1]
candidate=OUT/'ee_floor_ui_candidate.js'
native=ROOT/'tools/project_core/maps/ee_floor.js'
original_read=Path.read_text
def read_text(path,*args,**kwargs):
    if mode=='green' and path.resolve()==native.resolve():
        return original_read(candidate,*args,**kwargs)
    return original_read(path,*args,**kwargs)
pages=[]
with patch.object(Path,'read_text',read_text):
    for name in ['index.html','trends.html']:
        page=OUT/'ee_floor_ui_checks'/mode/name
        page.parent.mkdir(parents=True,exist_ok=True)
        page.write_text(linked_layout(original_read(ROOT/'tools/project_core/maps/original_html_layout'/name,encoding='utf-8')),encoding='utf-8')
        pages.append(str(page))
node=Path('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
result=subprocess.run([str(node),str(OUT/'check_ee_floor_views_candidate.js'),*pages],capture_output=True,text=True,encoding='utf-8')
record={'mode':mode,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'production_js_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'pages':pages}
(OUT/f'ee_floor_ui_{mode}.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
sys.exit(result.returncode)

