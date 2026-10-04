"""Publish saved direct returns in the existing workbook health schema; no solver calls."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE/'engine_snapshot'));sys.path.insert(0,str(ROOT/'tools'))
from PPRCalculator import PPRCalculator
from workbooks import *
from regional import result_hash
out=[]
for unit in ['HS_077','EEZ_941','EEZ_598','HS_071']:
    evidence=ROOT/'regions/HS_077/evidence/2026-09-28_integration_audit' if unit=='HS_077' else HERE
    reports=json.loads((evidence/'direct_diagnostics.json').read_text(encoding='utf-8'))
    flat=[{'TE_option':option,**PPRCalculator._flatten_diagnostics(report)} for option,report in reports.items()]
    header=list(dict.fromkeys(k for r in flat for k in r))
    path=ROOT/'regions'/unit/(unit+'.xlsx');book=read_book(path)
    before_input=input_hash(book);before_result=result_hash(book)
    book['Diagnostics']['model_health']=(header,[[clean(r.get(k)) for k in header] for r in flat])
    write_book(path,book);saved=read_book(path);validate_region(saved,path)
    assert input_hash(saved)==before_input and result_hash(saved)==before_result
    out.append({'region':unit,'diagnostic_rows':len(flat),'numeric_inputs_results_unchanged':True,'methods':{r['TE_option']:{'status':r['status'],'strict_model_balance':r['model_input_is_model_balanced'],'strict_PP_balance':r['balance_is_balanced'],'b':r['divergence_b'],'rho_living':r['divergence_rho_living']} for r in flat}})
(HERE/'health_table_verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
