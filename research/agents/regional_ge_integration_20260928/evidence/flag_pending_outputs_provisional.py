import sys,json,pathlib,math
sys.path.insert(0,'tools')
from workbooks import *
from regional import recalculate,set_setting,result_hash
for rid in ['LME_013','LME_037']:
 p=pathlib.Path('regions')/rid/f'{rid}.xlsx';b=read_book(p);D=p.parent/'models/regional_ge_integration_20260928';before={tuple(r[:6]):r[7:] for r in rows(b,'PPR','Annual')}
 for r in rows(b,'PPR','Annual'):
  r[6]='provisional: '+r[2]+' WARN; '+('Patagonia-to-Humboldt geographic transfer; normalized diet and residual BA defaults' if rid=='LME_013' else 'Visayan locality; documented import/BA/GS/routing defaults; strict input and budget balance false')+'; scientific validation pending'
 recalculate(b,p)
 set_setting(b,'calculation_status','PROVISIONAL numeric supported-catch PPR displayed by user instruction; GE/TE/With Egestion WARN; scientific validation pending; full-region eligibility false')
 for r in rows(b,'PPR','Annual'):
  expected=before[tuple(r[:6])]
  for a,v in zip(r[7:],expected):assert a is None and v is None or isinstance(a,(int,float)) and isinstance(v,(int,float)) and math.isclose(a,v,rel_tol=1e-12,abs_tol=1e-5)
 write_book(p,b);c=read_book(p);validate_region(c,p);assert overview(c)['calculation_result_sha256']==result_hash(c)
 v=json.loads((D/'integration_verification.json').read_text());v['after_workbook_sha256']=sha(p);v['provisional_display_explicit']=True;v['numeric_values_preserved_when_flagged']=True;v['scientific_validation']='pending; not established by numerical verification';(D/'integration_verification.json').write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
 f=D/'INTEGRATION_REPORT.md';f.write_text(f.read_text(encoding='utf-8')+'\nAll Annual model output statuses now explicitly start provisional: and retain WARN and model-specific limitations. Numeric replay verification is not scientific validation. Validated common-catch comparisons exclude these provisional outputs.\n',encoding='utf-8')
 print(rid,'explicit provisional status verified')
