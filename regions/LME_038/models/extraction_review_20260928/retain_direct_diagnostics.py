"""Retain complete direct three-option reports through existing bounded health API."""
from pathlib import Path
import json,sys,tempfile,shutil,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_038';MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';dest=REG/'models'/MID
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
import create_PPRS_excel as cpe
def main():
 saved=json.loads((dest/'evidence/sppr_diagnostic_audit.json').read_text(encoding='utf8'))['health'];reports={}
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/(MID+'.json');shutil.copy2(dest/'model.json',p);model,_=cpe.load_model(str(p))
  with cpe._TaskRunner(180) as runner:
   runner.set_model(model)
   for te in ['GE','TE','With Egestion']:
    status,report,notes=runner.run(cpe.TASK_HEALTH,te,0);assert status=='ok',(te,status)
    flat=cpe.PPRCalculator._flatten_diagnostics(report);old=next(h for h in saved if h['TE_option']==te)
    for k,v in flat.items():
     if v is None:continue
     assert k in old,(te,k)
     if isinstance(v,(float,int)) and not isinstance(v,bool):assert math.isclose(v,old[k],rel_tol=1e-12,abs_tol=1e-12),(te,k,v,old[k])
     else:assert v==old[k],(te,k,v,old[k])
    reports[te]=report
 (dest/'evidence/DIAGNOSE_SPPR_DIRECT.json').write_text(json.dumps(reports,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),encoding='utf8')
 lines=['# SPPR diagnostics — selected Buchary model','']
 for te,report in reports.items():
  lines+=['## '+te,'']
  for section,values in report.items():
   lines+=['### '+section,'']
   if isinstance(values,dict):
    lines+=['| Field | Value |','|---|---|']
    for k,v in values.items():lines.append('| '+str(k)+' | '+str(v).replace('|','\\|').replace('\n','<br>')+' |')
   elif isinstance(values,list):lines.extend(['- '+str(v) for v in values] if values else ['[]'])
   else:lines.append(str(values))
   lines.append('')
 (dest/'SPPR_DIAGNOSTICS.md').write_text('\n'.join(lines),encoding='utf8')
 (dest/'evidence/DIRECT_DIAGNOSTIC_RETENTION.json').write_text(json.dumps({'retention':'Three direct diagnose_sppr reports through bounded existing health runner; no22-method orMC rerun','timeout_each_seconds':180,'saved_flattened_fields_match':True,'options':list(reports),'warnings':{k:r['warnings'] for k,r in reports.items()}},indent=2),encoding='utf8')
 print('Saved complete direct GE/TE/With Egestion reports; all flattened fields match selected run')
if __name__=='__main__':main()
