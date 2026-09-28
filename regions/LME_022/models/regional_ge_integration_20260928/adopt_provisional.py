"""Apply the user's later authorization for flagged numerical research previews."""
from pathlib import Path
import sys,json,csv,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,set_result_hash
p=HERE.parent.parent/'LME_022.xlsx';b=read_book(p);old=copy.deepcopy(b);model=overview(b)['selected_model_id']
coeff=[]
for scope,f in [('all','all'),('inner','inner'),('PP','pp')]:
    for r in csv.DictReader((HERE/f'group_sppr_{f}.csv').open(encoding='utf-8')):
        for m in ['new_GE','new_TE_EEfix','new_WithEgestion']:coeff.append([model,r['group_name'],scope,m,float(r[m])])
b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],coeff)
for r in rows(b,'PPR','Annual'):
    if r[5]=='ppr':r[6]='provisional: '+('TE FAIL; divergent living network and negative source contributions' if r[2]=='new_TE_EEfix' else ('GE OK' if r[2]=='new_GE' else 'With Egestion OK'))+'; normalized/completed runtime; Scotland spatial transfer; partial mapping; scientific validation pending'
recalculate(b,p)
b['Classic PPR']=old['Classic PPR'];h,rr=b['PPR–NPP']['Ratios'];b['PPR–NPP']['Ratios']=(h,[r for r in rr if r[0]]+[r for r in rows(old,'PPR–NPP','Ratios') if not r[0]])
set_setting(b,'calculation_status','Provisional supported-catch PPR displayed by user request; GE/Egestion OK, TE FAIL flagged; 85.79% of 2019 total catch; scientific validation pending')
b['Diagnostics']['provisional_display_authorization']=table_dict([{'date':'2026-09-28','instruction':'User requests taxon mapping and PPR display for selected models with numeric SPPR, to validate every model later; flag diagnosis problems.','scope':'Exact retained runtime, numeric research previews only; no new ecological repair; missing mappings/coefficients remain blank.'}])
set_result_hash(b);write_book(p,b);saved=read_book(p);validate_region(saved,p)
for s in ['Catch','Classic PPR','NPP']:assert saved[s]==old[s]
summary=json.loads((HERE/'integration_verification.json').read_text(encoding='utf-8'));summary['workbook_sha256']=sha(p);summary['display_state']='provisional, per later explicit user instruction; full TE FAIL values also displayed with flags';(HERE/'integration_verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('North Sea three traceable direct methods adopted as explicitly flagged provisional results; source and independent results preserved.')
