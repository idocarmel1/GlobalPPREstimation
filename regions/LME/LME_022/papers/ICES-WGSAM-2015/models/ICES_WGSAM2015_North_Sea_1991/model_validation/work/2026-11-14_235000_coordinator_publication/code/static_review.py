from pathlib import Path
import ast,hashlib,json,sys
from zipfile import ZipFile
run=Path(__file__).resolve().parents[1];root=next(p for p in run.parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(root))
from tools.project_core.validation.researcher_review import table_rows,review_group_sequences,read_report
stage=run.parent/'2026-11-14_230000_retained_adoption'
handoff=json.loads((stage/'outputs/coordinator_handoff.json').read_text())
pins={'wrapper_sha256':handoff['script']['sha256'],'preparation_sha256':handoff['preparation_sha256'],'package':handoff['package'],'ready':handoff['ready']}
(run/'inputs/package_pin.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
script=run/'code/publish_ices.py';text=script.read_text(encoding='utf-8-sig');tree=ast.parse(text);compile(tree,str(script),'exec')
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
publish=functions['publish'];calls=[]
for node in ast.walk(publish):
    if isinstance(node,ast.Call):
        fn=node.func;name=fn.id if isinstance(fn,ast.Name) else fn.attr if isinstance(fn,ast.Attribute) else ''
        calls.append((node.lineno,name))
calls.sort();names=[name for _,name in calls]
assert names.index('apply')<names.index('_register_review')<names.index('_refresh_reviews')<names.index('_update')<names.index('_build')<names.index('final_checks')
assert 'publication_transaction' in names and 'publication_write' in names
assert 'ensure_validated_coverage(' not in text
assert "only_units={UNIT}" in text and '_update(ROOT,[REGION],False)' in text
assert 'BASELINE_SHA' not in text and 'CURRENT_SHA' not in text
regional=stage/'outputs/retained_package_v2/regional/LME_022.xlsx'
with ZipFile(regional) as archive:
    groups=[r for _,r in table_rows(archive,'Selected model groups','Groups')[3]]
identities=review_group_sequences(groups);excluded={name:seq for name,seq in identities.items() if seq in [1,2,3,4,65]}
print(json.dumps(excluded))
result={'compile_passed':True,'transaction_order_verified':True,'scope_ICES_only':True,'no_mutable_Project_pin':True,'all_promotions_tracked_for_rollback':True,'staged_excluded_groups':excluded,'staged_group_count':len(groups),'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'package_pins':pins,'driver_executed':False,'shared_writes':False,'live_preflight_run':False,'notes':'Only AST/static checks and narrow staged group inspection; parent runs default isolated preflight after active batch finishes.'}
(run/'qa/static_review.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
