from pathlib import Path
import hashlib,json
h=Path(__file__).resolve().parent;root=h.parents[4];src=Path('C:/Users/idoca/.agents/skills/ecopath-extraction');dest=root/'tools/skills/original_skill_resources/claude/ecopath-extraction';entries=[]
for rel in ['scripts/write_outputs.py','scripts/database_json.py','scripts/source_fidelity.py','references/output-formats.md','references/diet-source-runtime.md','references/published-companions.md']:
 p=dest/rel
 if p.exists() and not (h/'portable_before'/rel).exists():
  q=h/'portable_before'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 p.write_bytes((src/rel).read_bytes());entries.append({'file':str(p.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
p=dest/'SKILL.md';s=p.read_text(encoding='utf-8');title='## Current published-field companion support'
if title not in s:
 s+='\n'+title+'\n\nKeep the eight EwE import schemas unchanged. Preserve every additional published\nmodel field in separate purpose-specific evidence CSVs using\n[references/published-companions.md](references/published-companions.md).\nThe maintained writer/converter retain these in JSON and reconstruct numeric\nstandard sheets plus companion sheets with value/missing-mask verification.\nThese companion CSVs are not asserted to be directly importable by EwE.\nThis directory is the portable fallback when the current installed\n`ecopath-extraction` skill is unavailable; do not mix script versions within a run.\n'
 p.write_text(s,encoding='utf-8')
p=root/'tools/skills/original_skill_resources/combined-src/references/model-preparation.md';s=p.read_text(encoding='utf-8')
s=s.replace('Use the retained domain resources under `../../claude/ecopath-extraction/` for paper extraction and [group-taxonomy.md](group-taxonomy.md) for taxonomy.', 'For paper extraction, resolve the current `ecopath-extraction` skill from the available skill catalog and run its scripts from that resolved root. If unavailable, use the maintained portable fallback at `../../claude/ecopath-extraction/`, whose writer/converter support the same published-companion schema. Do not mix installed and fallback script versions within a run. Use [group-taxonomy.md](group-taxonomy.md) for taxonomy.')
s=s.replace('For a paper extraction, read `../../claude/ecopath-extraction/SKILL.md` and apply its scientific workflow:', 'For a paper extraction, read the resolved current extraction skill (or the maintained portable fallback above) and apply its scientific workflow:')
add='\nKeep the eight EwE import schemas unchanged. Preserve every additional published model field in separate purpose-specific evidence CSVs under the [published-companion contract](../../claude/ecopath-extraction/references/published-companions.md), retaining them in JSON and reconstructed sheets with numerical/missing-mask checks. These companions are not asserted to be directly importable by EwE.\n'
if 'under the [published-companion contract]' not in s:s=s.rstrip()+'\n'+add
p.write_text(s,encoding='utf-8')
(h/'portable_skill_sync.json').write_text(json.dumps(entries,indent=2),encoding='utf-8');print('Portable fallback and active preparation route synchronized')
