from pathlib import Path
import json,hashlib,os,subprocess,sys
h=Path(__file__).resolve().parent;root=h.parents[4];installed=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=load(h/'skill_regression_baseline/result.json');own=load(h/'skill_regression_installed_final/result.json');indpath=h.parent/'mapping/skill_independent_test/independent_results.json';ind=load(indpath)
actual={f:sha(installed/f) for f in ['source_fidelity.py','database_json.py','write_outputs.py']}
assert actual==ind['tested_revision_sha256']
result={'baseline':{'checks':len(base),'passed':sum(base.values()),'failed':sum(not x for x in base.values())},'installed_regression':{'checks':len(own),'passed':sum(own.values()),'all_passed':all(own.values())},'independent_regression':{'checks':len(ind['results']),'passed':sum(x['passed'] for x in ind['results']),'all_passed':all(x['passed'] for x in ind['results']),'path':os.path.relpath(indpath,h).replace('\\','/')},'quick_validate':'Skill is valid! (executed with task-local PyYAML 6.0.3)','tested_script_sha256':actual,'limits':'EwE compatibility verified against exact existing eight schemas; no EwE GUI import attempted. Biological validity remains a separate assessment.'}
p=h/'SKILL_VALIDATION.json';p.write_text(json.dumps(result,indent=2),encoding='utf-8')
index=load(h/'evidence_index.json')
for role,path in [('skill_validation',p),('independent_skill_regression',indpath),('installed_skill_regression',h/'skill_regression_installed_final/result.json')]:
 index['required_roles'].append(role);index['artifacts'].append({'role':role,'path':os.path.relpath(path,h).replace('\\','/'),'sha256':sha(path),'availability':'present'})
(h/'evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
checker=root/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py'
done=subprocess.run([sys.executable,str(checker),str(h/'evidence_index.json'),'--output',str(h/'completeness.json')],capture_output=True,text=True,encoding='utf-8');assert done.returncode==0,done.stdout[-1500:]
print(json.dumps(result,indent=2))
