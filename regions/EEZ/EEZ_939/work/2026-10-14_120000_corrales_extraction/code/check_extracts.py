from pathlib import Path
import json,csv,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[6];WORK=Path(__file__).resolve().parents[1]
RESOURCE=ROOT/'tools/skills/paper-to-ppr/resources/extraction'
for period in ['1990_1994','2008_2012']:
 state=json.loads((WORK/f'outputs/stage_{period}.json').read_text(encoding='utf-8'));stage=Path(state['path'])
 m=json.loads((stage/'model.json').read_text(encoding='utf-8'))
 cross=m['companions']['Source_group_crosswalk.csv']['rows']
 tax=WORK/f'inputs/taxonomy_{period}.csv'
 with tax.open('w',encoding='utf-8',newline='') as f:
  writer=csv.writer(f);writer.writerow(['seq','group_name','taxon_descr'])
  for row in cross[1:]:writer.writerow([row[1],row[2],row[3]])
 subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/skills/paper-to-ppr/scripts/write_taxonomy.py'),str(tax),str(stage/'Taxonomy.xlsx')],check=True)
 outcomes=[]
 for name,args in [('validate',['validate.py',str(stage)]),('massbalance',['massbalance_check.py',str(stage)]),('conversion',['database_json.py','-d',str(stage),'--update-report'])]:
  command=[sys.executable,'-X','utf8',str(RESOURCE/'scripts'/args[0])]+args[1:]
  r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');(WORK/f'qa/{period}_{name}.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
  outcomes.append({'check':name,'exit_code':r.returncode,'log':f'{period}_{name}.log'});print(period,name,r.returncode,flush=True)
 (WORK/f'qa/{period}_check_outcomes.json').write_text(json.dumps(outcomes,indent=2),encoding='utf-8')
