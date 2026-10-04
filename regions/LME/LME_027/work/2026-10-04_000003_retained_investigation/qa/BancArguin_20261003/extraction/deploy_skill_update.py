from pathlib import Path
import json,hashlib
here=Path(__file__).resolve().parent;target=Path('C:/Users/idoca/.agents/skills/ecopath-extraction');stage=here/'skill_update'
hashes=json.loads((here/'skill_update_original_hashes.json').read_text(encoding='utf-8'))
for rel,old in hashes.items():
 actual=hashlib.sha256((target/rel).read_bytes()).hexdigest()
 if actual!=old:raise RuntimeError('Concurrent skill edit detected; do not overwrite: '+rel)
installed=[]
for source in stage.rglob('*'):
 if not source.is_file() or '__pycache__' in source.parts:continue
 rel=source.relative_to(stage);dest=target/rel
 if str(rel).replace('\\','/') not in hashes and dest.exists():raise RuntimeError('Unexpected existing new target '+str(dest))
 if dest.exists():
  backup=here/'skill_before'/rel;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(dest.read_bytes())
 dest.parent.mkdir(exist_ok=True);dest.write_bytes(source.read_bytes());installed.append({'path':str(dest),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
(here/'installed_skill_update.json').write_text(json.dumps(installed,indent=2),encoding='utf-8');print(json.dumps(installed,indent=2))
