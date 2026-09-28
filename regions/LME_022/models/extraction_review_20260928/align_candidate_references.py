"""Update references after native folder moves; preserve numerical/source/log bytes."""
from pathlib import Path
import json,hashlib
review=Path(__file__).parent;models=review.parent
mapping={'NS-2025_ECS-1890-1895':'22_20251890_East_Coast_of_Scotland_(1890-1895)','NS-2025_ECS-1991-1995':'22_20251990_East_Coast_of_Scotland_(1991-1995)','Mackinson-2007_NS-1991':'22_20071991_North_Sea_report_Table_3.3_(1991)','EcoBase-457_NS-1991':'457_457_North_Sea_(1991)'}
before={name:hashlib.sha256((models/name/'model.json').read_bytes()).hexdigest() for name in mapping.values()}
changed=[]
for folder in [review,*[models/n for n in mapping.values()]]:
 for p in folder.rglob('*'):
  if not p.is_file() or p==Path(__file__) or p.suffix not in ['.py','.json','.md','.csv'] or 'diagnostic_code' in p.parts:continue
  text=p.read_text(encoding='utf-8-sig');new=text
  for old,name in mapping.items():new=new.replace(old,name)
  if p.name=='extract_candidates.py':new=new.replace("mid='NS-2025_ECS-'+period","mid=f'22_2025{suffix}_East_Coast_of_Scotland_({period})'")
  if p.name=='finish_evidence.py':new=new.replace("folder.startswith('NS-2025')","folder.startswith('22_2025')")
  if new!=text:p.write_text(new,encoding='utf8');changed.append(str(p.relative_to(models)))
for name,h in before.items():assert hashlib.sha256((models/name/'model.json').read_bytes()).hexdigest()==h
(review/'candidate_folder_relocation.json').write_text(json.dumps({'mapping':mapping,'canonical_sha256_unchanged':before,'updated_references':changed,'historical_logs':'Raw logs and executed code snapshots retained byte-for-byte. Historical path strings resolve through this relocation manifest.'},indent=2),encoding='utf8')
print('Aligned references; canonical model bytes unchanged.')
