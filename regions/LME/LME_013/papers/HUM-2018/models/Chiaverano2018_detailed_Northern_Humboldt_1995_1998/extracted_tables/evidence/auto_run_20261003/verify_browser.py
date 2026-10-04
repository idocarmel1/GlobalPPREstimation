from pathlib import Path
from decimal import Decimal
from urllib.parse import unquote
import json,csv,math,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent.parents[3]
historical=json.loads((OUT/'qa/browser_observations.json').read_text(encoding='utf-8'))
observed=json.loads((OUT/'qa/browser_current_snapshot.json').read_text(encoding='utf-8'))
methods={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}
def csvdata(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
annual={(r['method'],r['scope'],r['catch_basis'],r['unidentified_treatment'],int(r['year'])):r for r in csvdata('candidate_annual_totals.csv')}
ratios={(r['method'],r['scope'],r['catch_basis'],r['unidentified_treatment'],int(r['year']),r['npp_method']):r for r in csvdata('candidate_annual_npp_ratios.csv')}
results=[]
for row in historical['observations']+observed['observations']:
    key=(methods[row['method']],row['scope'],row['basis'],row['treatment'],row['year'])
    value=annual[key]['ppr_tC'] if row['metric']=='ppr' else ratios[*key,observed['npp_method']]['ppr_npp_ratio']
    value=None if value=='' else float(value)*(100 if row['metric']=='npp_ratio' else 1)
    expected='Unavailable' if value is None else format(Decimal(format(value,'.4g')),',f')+(' t C' if row['metric']=='ppr' else '%')
    assert row['modelLabel']=='Chiaverano2018 detailed Northern Humboldt 1995 1998'
    displayed=row['visibleText'].split(row['modelLabel']+'\n',1)[1].split('\n',1)[0]
    assert displayed==expected,(row['name'],displayed,expected,value)
    assert 'Model not yet validated by researcher' in row['visibleText']
    assert 'det_collapse_mode=auto · Production-ineligible' in row['visibleText']
    assert all(s in row['visibleText'] for s in ['GE overall FAIL; input FAIL; convergence FAIL; SPPR balance FAIL','TE overall FAIL; input FAIL; convergence WARN; SPPR balance FAIL','With Egestion overall FAIL; input FAIL; convergence FAIL; SPPR balance WARN'])
    results.append({'case':row['name'],'expected_full_precision':value,'expected_display':expected,'actual_display':displayed,'passed':True,'dimensions':{k:row[k] for k in ['method','scope','basis','treatment','metric','year']}})
for link in observed['links']:
    path=(ROOT/'interactive_map'/unquote(link['href'])).resolve()
    assert path.is_relative_to(ROOT) and path.is_file(),link
current=hashlib.sha256((ROOT/'Project.xlsx').read_bytes()).hexdigest()
assert current==observed['project_fingerprint'],'Project changed after browser inspection'
result={'passed':True,'model_id':OUT.parent.name,'project_sha256':current,'display_precision':'four significant digits; underlying saved values reconciled separately','npp_method':observed['npp_method'],'missing_npp_policy':observed['missing_npp_policy'],'cases':results,'portable_links':observed['links'],'scientific_eligibility':False,'researcher_verdict':None,'limits':'Browser checks cover representative dimensions; all saved annual dimensions are exhaustively reconciled in integration_verification.json.'}
result['historical_cases_before_concurrent_LME052_rebuild']=len(historical['observations'])
result['current_cases_after_shared_rebuild']=len(observed['observations'])
result['current_origin']='http://localhost:8877'
result['persistence']=json.loads((OUT/'qa/browser_persistence.json').read_text(encoding='utf-8'))
assert result['persistence']['reload_retained'] and result['persistence']['method_changes_retained']
(OUT/'qa/browser_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Browser dimensions, values, missingness, actual grades and portable links reconciled in '+str(len(results))+' cases.')
