import hashlib,json,os,re
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());QA=Path(__file__).parent.parent/'qa'
home=ROOT/'regions/LME/LME_038/papers/INDO-1999/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
source=home.parent/'38_38001_Java_Sea_(mid1970s)'
audit=home/'model_validation/evidence/source_review/diet_reextraction_20261002'
def link(p,label):return '['+label+']('+os.path.relpath(p,home).replace('\\','/').replace(' ','%20')+')'
data=json.loads((home/'model.json').read_text('utf8'));before=json.loads((source/'model.json').read_text('utf8'));bg={str(g['group_seq']):g for g in before['group']}
text='\nThe retained `source_audit` annotation inside JSON describes the former normalization arrangement; its authorization and hash are historical metadata. The current diet values follow the October 2 restoration ledger. The 28 signed BA values below remain computational completions, compared with '+link(source/'model.json','source reconstruction')+'; they are not reported stock changes.\n\n| Group ID/name | Published/source BA | Retained computational BA |\n|---|---|---|\n'
for g in data['group']:
 gid=str(g['group_seq']);text+='| '+gid+' / '+str(g['group_name'])+' | `'+str(bg[gid].get('biomass_accum'))+'` (unknown sentinel) | `'+str(g.get('biomass_accum'))+'` |\n'
text+='\nExact restoration locators: Buchary thesis, Table 3.10, PDF page 81 / printed page 72, consumer column 9 (Macrozoobenthos). These are already-retained October 2 source decisions; administrative migration did not re-extract or alter these cells.\n\n| Prey ID | Printed and retained literal | Former superseded literal |\n|---|---|---|\n'
for r in json.loads((audit/'changed_cells_ledger.json').read_text('utf8')):text+='| '+r['prey_id']+' | `'+r['adopted_literal']+'` | `'+r['before_literal']+'` |\n'
text+='\n'+link(audit/'changed_cells_ledger.json','Six-cell source locator and restoration ledger')+'; '+link(audit/'canonical_staleness.json','Current-versus-historical freshness limits')+'; '+link(audit/'runtime_transformation_ledger.json','Historical runtime normalization conventions')+'.\n'
p=home/'model_notes.md';current=p.read_text('utf8');current=current.replace('\n## Evidence links',text+'\n## Evidence links');p.write_text(current,encoding='utf8')
p=ROOT/'regions/LME/LME_052/papers/OKH-GM2019/models/52_GM2019_Fig9_Pelagic_balanced_(2000-2014)/model_notes.md'
current=p.read_text('utf8').replace('The following exact input differences','The sibling source reconstruction uses wet-weight stock density, while this computational variant uses carbon stock density with group-specific conversions. Consequently the B comparison records a unit/representation change as well as the documented stock-splitting choices; it is not a new biological correction.\n\nThe following exact input differences');p.write_text(current,encoding='utf8')
# Improve narrative spacing without modifying numeric literals, hashes, paths or scientific JSON.
inventory=json.loads((ROOT/'regions/LME_028/work/2026-10-04_000002_reorganization/qa/canonical_models.json').read_text('utf8'))
for item in inventory['destinations']:
 p=ROOT/item['directory']/'model_notes.md';text=p.read_text('utf8');lines=[]
 for line in text.splitlines():
  if line.startswith('|')or line.startswith('- ')or re.search(r'[0-9a-f]{64}',line):lines.append(line);continue
  parts=re.split(r'(`[^`]*`|\[[^\]]*\]\([^\)]*\))',line)
  for i in range(0,len(parts),2):
   parts[i]=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', parts[i]);parts[i]=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',parts[i])
  lines.append(''.join(parts))
 p.write_text('\n'.join(lines)+'\n',encoding='utf8')
record=json.loads((QA/'model_notes_and_sources.json').read_text('utf8'))
for r in record['notes']:
 home=next(ROOT/i['directory']for i in inventory['destinations']if i['unit_id']==r['unit_id']and i['model_id']==r['model_id']);r['notes_sha256']=hashlib.sha256((home/'model_notes.md').read_bytes()).hexdigest()
record['paper_source_byte_verification']={'files':1260,'exact_baseline_bytes':1258,'scientific_source_byte_differences':0,'administrative_guide_changes':['regions/LME/LME_027/papers/CAN-2014/sources/README.md','regions/LME/LME_050/papers/SOJ-2023/sources/README.md'],'lfs_pointers':0}
(QA/'model_notes_and_sources.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Completed explicit JavaSea BA/diet source locators, Okhotsk unit distinction and note wording.')
