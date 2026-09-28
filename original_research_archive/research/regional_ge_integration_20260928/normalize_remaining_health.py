"""Publish retained diagnostics in the shared display schema, without solving models."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'regions/EEZ_941/evidence/2026-09-28_integration/engine_snapshot'))
sys.path.insert(0,str(ROOT/'tools'))
from PPRCalculator import PPRCalculator
from workbooks import *
from regional import result_hash
from original_atlas_data import review_flags

paths=[];checks=[]
for unit in ['LME_024','LME_027','LME_029']:
    source,=list((ROOT/'regions'/unit/'models').glob('*/integration_20260928/direct_reports.json'))
    reports=json.loads(source.read_text(encoding='utf-8'))
    flat=[{'TE_option':option,**PPRCalculator._flatten_diagnostics(value)} for option,value in reports.items()]
    header=list(dict.fromkeys(k for row in flat for k in row))
    path=ROOT/'regions'/unit/(unit+'.xlsx');book=read_book(path)
    before_input=input_hash(book);before_result=result_hash(book)
    untouched={s:digest_tables(list(t.items())) for s,t in book.items() if s!='Diagnostics'}
    book['Diagnostics']['model_health']=(header,[[clean(row.get(k)) for k in header] for row in flat])
    write_book(path,book);saved=read_book(path);validate_region(saved,path)
    assert input_hash(saved)==before_input and result_hash(saved)==before_result
    assert untouched=={s:digest_tables(list(t.items())) for s,t in saved.items() if s!='Diagnostics'}
    paths.append(path);checks.append({'unit_id':unit,'methods':[r['TE_option'] for r in flat],'review_flags':review_flags(saved),'workbook_sha256':sha(path),'retained_reports_sha256':sha(source),'all_non_diagnostic_tables_unchanged':True})
    print('Normalized saved health report',unit,flush=True)
(HERE/'health_schema_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('Retained diagnostics normalized; all numerical regional tables unchanged. Central consolidation remains separate.',flush=True)
