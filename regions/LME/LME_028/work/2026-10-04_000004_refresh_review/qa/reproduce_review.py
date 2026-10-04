"""Independent review reproductions; modifies temporary fixtures only."""
import copy,json,sys,tempfile
from pathlib import Path
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0,str(ROOT))
from tools.workflow_checks.selection.test_selection_refresh import SelectionTests
from tools.project_core.calculations.selection import refresh_region,execution_identity,central_lock
from tools.project_core.calculations.snapshots import save_snapshot
from tools.project_core.calculations.regional import set_setting,recalculate
from tools.project_core.workbooks.workbooks import read_book,update_book,overview,records,sha
from tools.project_core.registry.update_project import update

findings={}
def setup():
    f=SelectionTests();f.setUp();return f

f=setup()
try:
    b=read_book(f.path)
    h,r=b['PPR']['Matching'];r[:]=[['m','a','A',.5,'high','explicit_member','source'],['m','a','B',.5,'high','explicit_member','source'],['m','b','B',1.,'high','explicit_member','source']]
    recalculate(b,f.path);update_book(f.path,b)
    save_snapshot(f.path,f.models['m'],result_identity=execution_identity(f.root,f.models['m'],b,flags={'normalize_DC':True}))
    f.select('B');refresh_region(f.root,f.path,publisher=f.publish)
    b=read_book(f.path);b['Catch']['Catch'][1][0][-1]=200;update_book(f.path,b)
    f.select('m');result=refresh_region(f.root,f.path,publisher=f.publish);active=read_book(f.path)
    findings['incompatible_split_matching']={'result':result,'annual_rows':len(records(active,'PPR','Annual')),'matching_rows':len(records(active,'PPR','Matching')),'nonmissing_ppr_2019':[r[2019] for r in records(active,'PPR','Annual') if r['metric']=='ppr' and r[2019] is not None][:5]}
finally:f.tearDown()

f=setup()
try:
    save_snapshot(f.path,f.models['m'],result_identity=execution_identity(f.root,f.models['m'],f.book,flags={'normalize_DC':True}))
    f.select('B');refresh_region(f.root,f.path,publisher=f.publish)
    b=read_book(f.path);set_setting(b,'effective_loader_flags',json.dumps({'normalize_DC':False}));update_book(f.path,b)
    f.select('m');result=refresh_region(f.root,f.path,publisher=f.publish)
    manifest=json.loads((f.models['m']/'results/result_manifest.json').read_text(encoding='utf-8'))
    findings['flag_mismatch']={'result':result,'active_explicit_flags':overview(read_book(f.path)).get('effective_loader_flags'),'manifest_flags':manifest['effective_flags']}
finally:f.tearDown()

f=setup()
try:
    save_snapshot(f.path,f.models['m'],result_identity=execution_identity(f.root,f.models['m'],f.book,flags={'normalize_DC':True}))
    package=f.models['m']/'results';before={p.name:p.read_bytes() for p in package.iterdir()}
    f.select('B');before_active=f.path.read_bytes();before_central=(f.root/'Project.xlsx').read_bytes()
    def fail(*args):raise RuntimeError('injected failure')
    try:refresh_region(f.root,f.path,publisher=fail)
    except RuntimeError:pass
    findings['rollback']={'package_bytes_preserved':all((package/name).read_bytes()==value for name,value in before.items()),'active_bytes_preserved':f.path.read_bytes()==before_active,'central_bytes_preserved':(f.root/'Project.xlsx').read_bytes()==before_central}
finally:f.tearDown()

f=setup()
try:
    with central_lock(f.root):
        update(f.root,[f.path])
    findings['central_lock_bypass']={'updater_wrote_while_lock_held':True}
finally:f.tearDown()

f=setup()
try:
    w=openpyxl.load_workbook(f.path);w['Overview']['D3']='researcher note outside @table width';w.save(f.path);w.close()
    b=read_book(f.path);set_setting(b,'selection_rationale','updated rationale');update_book(f.path,b)
    w=openpyxl.load_workbook(f.path);findings['manual_cells']={'remaining_value':w['Overview']['D3'].value};w.close()
    update(f.root,[f.path]);w=openpyxl.load_workbook(f.root/'Project.xlsx')
    findings['native_table_columns']=[{'ref':t.ref,'header_width':openpyxl.utils.cell.range_boundaries(t.ref)[2],'table_column_count':len(t.tableColumns)} for s in w for t in s.tables.values()];w.close()
finally:f.tearDown()

out=Path(__file__).with_name('reproduction_results.json');out.write_text(json.dumps(findings,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(findings,ensure_ascii=False,indent=2))
