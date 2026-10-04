"""Check documentation destinations and unchanged scientific bytes."""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[6]
QA = Path(__file__).resolve().parent.parent / 'qa'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    files = [ROOT / 'README.md', ROOT / 'AGENTS.md'] + list((ROOT / 'explainers').rglob('*.md'))
    files += [ROOT / p for p in [
        'tools/skills/paper-to-ppr/SKILL.md', 'tools/skills/ecopath-model-validation/SKILL.md',
        'tools/skills/paper-to-ppr/resources/mapping/references/output-format.md',
        'tools/skills/paper-to-ppr/resources/extraction/procedure.md', 'tools/templates/instructions.md']]
    broken = []; obsolete = []; checked = 0
    for path in files:
        text = path.read_text('utf8')
        for name in ['project_reorganization_plan.md', 'skill_efficiency_ideas.md', 'skill_efficiency_implementation_plan.md']:
            if name in text: obsolete.append({'source': path.relative_to(ROOT).as_posix(), 'obsolete': name})
        for match in re.finditer(r'\[[^\]]*\]\(([^\n)]+)\)', text):
            ref = match.group(1).split(' "')[0].strip('<>')
            target = ref.split('#')[0]
            if not target or re.match(r'^[a-zA-Z]+:', target): continue
            checked += 1
            resolved = path.parent / unquote(target)
            if not resolved.exists(): broken.append({'source': path.relative_to(ROOT).as_posix(), 'target': ref})
    assert not broken, broken
    assert not obsolete, obsolete
    assert not (ROOT / 'explainers/plans').exists()
    dispositions = json.loads((QA / 'documentation_dispositions.json').read_text('utf8'))
    kept = dispositions['existing_human_guides_preserved_byte_for_byte']
    assert all(sha(ROOT / 'explainers' / name) == dispositions['baseline_sha256']['explainers/' + name] for name in kept)
    labeled = dispositions['existing_human_guides_preserved_except_documented_replacements']
    for name in labeled:
        rel = 'explainers/' + name
        before = subprocess.check_output(['git', 'show', '768dffbe:' + rel], cwd=ROOT)
        expected = before.replace(b'[structure contract]', b'[project layout]')
        if name == 'PPREstimation/USER_GUIDE.md':
            changes = json.loads((QA / 'engine_guide_example_changes.json').read_text('utf8'))['changes']
            for change in changes:
                expected = expected.replace(change['before'].encode('utf8'), change['after'].encode('utf8'))
        assert (ROOT / rel).read_bytes() == expected, rel
    oldqa = ROOT / 'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency/qa'
    hashes = json.loads((oldqa / 'live_protected_hashes.json').read_text('utf8'))
    changed = [name for name, expected in hashes.items() if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    assert not changed, changed
    value = {'checked_at': datetime.now(timezone.utc).isoformat(), 'pass': True,
             'documentation_files_checked': len(files), 'local_link_destinations_checked': checked,
             'broken_links': broken, 'obsolete_plan_references': obsolete,
             'plans_directory_absent': True, 'preserved_human_guides': kept,
             'human_scientific_guides_exact_bytes_except_documented_replacements': labeled,
             'engine_guide_example_changes': 'engine_guide_example_changes.json',
             'scientific_artifact_files_checked': len(hashes), 'scientific_bytes_unchanged': not changed,
             'scope': 'All current human/agent guides and affected skill/resource entries; path existence checks, five full-byte guide checks,461 protected scientific/workbook/report/page files. No scientific execution.'}
    (QA / 'documentation_verification.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'links': checked, 'preserved_guides': len(kept), 'scientific_files_unchanged': len(hashes)}))

if __name__ == '__main__': main()
