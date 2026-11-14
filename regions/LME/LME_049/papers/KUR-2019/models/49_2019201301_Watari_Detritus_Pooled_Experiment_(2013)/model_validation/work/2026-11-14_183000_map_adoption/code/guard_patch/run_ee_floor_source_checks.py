"""Use existing Python/UI tests with staged modules only; no production writes."""
import sys, os, json, importlib.util, unittest, io, subprocess, tempfile, hashlib
from pathlib import Path
from unittest.mock import patch
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd();sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
mode=sys.argv[1]
node=Path('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
os.environ['PATH']=str(node.parent)+os.pathsep+os.environ.get('PATH','')
temp=OUT/'ee_floor_ui_checks'/('source_'+mode);temp.mkdir(parents=True,exist_ok=True);tempfile.tempdir=str(temp)
native_test=ROOT/'tools/workflow_checks/maps/test_ee_floor_views.py'
spec=importlib.util.spec_from_file_location('test_staged_ee_floor_views',native_test)
tests=importlib.util.module_from_spec(spec)
exec(compile((OUT/'test_ee_floor_views_candidate.py').read_text('utf-8'),str(native_test),'exec'),tests.__dict__)
native_source=ROOT/'tools/project_core/maps/ee_floor_layout.py'
if mode=='green':
    spec=importlib.util.spec_from_file_location('staged_floor_layout',OUT/'ee_floor_layout_candidate.py')
    staged=importlib.util.module_from_spec(spec);spec.loader.exec_module(staged)
    tests.source_provenance_layout=staged.source_provenance_layout
native_js=ROOT/'tools/project_core/maps/ee_floor.js'
original_read=Path.read_text;original_run=subprocess.run
def read_text(path,*args,**kwargs):
    if mode=='green' and path.resolve()==native_js.resolve():
        return original_read(OUT/'ee_floor_ui_candidate.js',*args,**kwargs)
    return original_read(path,*args,**kwargs)
def run(args,*pargs,**kwargs):
    args=list(args)
    if len(args)>1 and Path(args[1]).name=='check_ee_floor_views.js':
        args[1]=str(OUT/'check_ee_floor_views_candidate.js')
    return original_run(args,*pargs,**kwargs)
suite=unittest.TestLoader().loadTestsFromModule(tests) if mode=='green' else unittest.TestSuite([tests.EeFloorViewsTests('test_source_view_distinguishes_floor_and_review_states_without_mutation')])
stream=io.StringIO()
with patch.object(Path,'read_text',read_text),patch.object(subprocess,'run',run):
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
record={'mode':mode,'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'success':result.wasSuccessful(),'output':stream.getvalue(),
        'production_source_sha256':hashlib.sha256(native_source.read_bytes()).hexdigest(),'production_js_sha256':hashlib.sha256(native_js.read_bytes()).hexdigest()}
(OUT/f'ee_floor_source_{mode}.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False));sys.exit(0 if result.wasSuccessful() else 1)

