"""Adopt the researcher's five explicitly authorized diet-entry relocations."""
from pathlib import Path
from decimal import Decimal
from copy import deepcopy
from datetime import datetime
import csv
import hashlib
import io
import json
import os
import re

ROOT = Path(__file__).resolve().parents[11]
RUN = Path(__file__).resolve().parents[1]
MODEL_DIR = RUN.parents[2]
MODEL = MODEL_DIR / 'model.json'
ORIGINAL = MODEL_DIR / 'original_model.json'
OLD_REPORT = RUN / 'outputs/hypothesis_report.md'
REPORT = MODEL_DIR / 'misplaced_diet_entries_report.md'
NOTES = MODEL_DIR / 'model_notes.md'
LEDGER = ROOT / 'common_reference_data/provenance/source_paths.csv'
sha = lambda b: hashlib.sha256(b).hexdigest()
old_bytes = MODEL.read_bytes()
assert sha(old_bytes) == '9cc8a41414194be6f40f4fafd9d6ed23c38a1c5812acd55e6e39824e783c2998'
assert not ORIGINAL.exists() and not REPORT.exists()
for p in (MODEL, ORIGINAL, OLD_REPORT, REPORT, NOTES, LEDGER):
    assert p.resolve().is_relative_to(ROOT.resolve()), p

old = json.loads(old_bytes.decode('utf-8-sig'))
new = deepcopy(old)
groups = {int(g['group_seq']): g for g in new['group']}
moves = [(22, 11, 12, '0.022'), (32, 23, 22, '0.575'),
         (32, 25, 26, '0.121'), (32, 26, 27, '0.030'), (32, 28, 29, '0.070')]
entries = []
for prey, source, target, value in moves:
    diet = groups[source]['diet_descr']['diet']
    entry = next(e for e in diet if int(e['prey_seq']) == prey)
    assert entry['proportion'] == value
    entries.append(deepcopy(entry))
    diet.remove(entry)
for (prey, source, target, value), entry in zip(moves, entries):
    diet = groups[target]['diet_descr']['diet']
    assert not any(int(e['prey_seq']) == prey for e in diet)
    index = next((i for i, e in enumerate(diet) if int(e['prey_seq']) > prey), len(diet))
    diet.insert(index, entry)

def totals(data):
    return {int(g['group_seq']): Decimal(g['diet_imp']) + sum(
        (Decimal(e['proportion']) for e in g['diet_descr']['diet'] if Decimal(e['proportion']) >= 0), Decimal(0))
        for g in data['group'] if int(g['group_seq']) <= 36}

before, after = totals(old), totals(new)
affected = {11, 12, 22, 23, 25, 26, 27, 28, 29}
assert all(after[c] == Decimal(1) for c in affected)
assert all(after[c] == before[c] for c in set(before) - affected)
assert after[18] == Decimal('1.001')
assert {k: v for k, v in old.items() if k != 'group'} == {k: v for k, v in new.items() if k != 'group'}
changes = []
for a, b in zip(old['group'], new['group']):
    assert {k: v for k, v in a.items() if k != 'diet_descr'} == {k: v for k, v in b.items() if k != 'diet_descr'}
    assert {k: v for k, v in a['diet_descr'].items() if k != 'diet'} == {k: v for k, v in b['diet_descr'].items() if k != 'diet'}
    aa = {int(e['prey_seq']): e for e in a['diet_descr']['diet']}
    bb = {int(e['prey_seq']): e for e in b['diet_descr']['diet']}
    assert len(aa) == len(a['diet_descr']['diet']) and len(bb) == len(b['diet_descr']['diet'])
    for prey in aa.keys() | bb.keys():
        if aa.get(prey) != bb.get(prey):
            changes.append(dict(predator_id=int(a['group_seq']), predator_name=a['group_name'],
                                prey_id=prey, before=aa.get(prey), after=bb.get(prey)))
assert {(c['predator_id'], c['prey_id']) for c in changes} == {
    (11, 22), (12, 22), (23, 32), (22, 32), (25, 32), (26, 32), (27, 32), (28, 32), (29, 32)}
assert sorted(json.dumps(e, sort_keys=True) for g in old['group'] for e in g['diet_descr']['diet']) == sorted(
    json.dumps(e, sort_keys=True) for g in new['group'] for e in g['diet_descr']['diet'])
new_bytes = (json.dumps(new, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
new_hash = sha(new_bytes)
run_rel = RUN.relative_to(MODEL_DIR).as_posix()

# Rebase the moved report's links and distinguish the earlier test from adoption.
report_before = OLD_REPORT.read_bytes()
report = report_before.decode('utf-8')
def rebase(match):
    label, reference = match.group(1), match.group(2)
    target = (OLD_REPORT.parent / reference).resolve()
    if target == MODEL:
        target = ORIGINAL
        label = 'preserved pre-correction model'
    return f'[{label}]({Path(os.path.relpath(target, MODEL_DIR)).as_posix()})'
report = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rebase, report)
report = report.replace('Date: 2026-10-08. Status: **unadopted hypothesis**.',
    'Date: 2026-10-08. Status: **five corrections adopted in model.json by explicit researcher instruction**.')
report = report.replace('No canonical model, validation DOCX, workbook, result, selection or map was edited.',
    'During the hypothesis-test stage, no canonical model, validation DOCX, workbook, result, selection or map was edited. The subsequent authorized adoption is recorded below.')
report = report.replace('## Candidate moves', '## Adopted moves')
report = report.replace('| Predator | Printed-entry total | Hypothesis total |', '| Predator | Pre-correction total | Corrected model total |')
report = report.replace('No loader, SPPR, ecological diagnostics or downstream calculation was run. These tests support review of a candidate table correction and do not adopt it.',
    'No loader, SPPR, ecological diagnostics or downstream calculation was run in the hypothesis-test stage. The CSV trial outputs retain that historical stage and its proposal labels.')
report += f'''\n\n## Researcher-authorized adoption — 2026-10-08\n\nThe researcher explicitly instructed: “change the current model.json to original_model.json” and “create a new model.json with these corrections”. The former canonical bytes are preserved as [original_model.json](original_model.json). The five moves above are now applied to [model.json](model.json) within the existing model folder and identity, as requested. Adoption records the researcher's decision; it does not establish author confirmation.\n\n- Preserved original SHA-256: `{sha(old_bytes)}`\n- Corrected model SHA-256: `{new_hash}`\n- All nine material totals are exactly 1.000. Albacore remains 1.001.\n- All non-diet fields, imports, unknown markers, group names/IDs and metadata were verified unchanged; the complete multiset of diet entries is preserved.\n- [Exact before/after cell ledger and verification]({run_rel}/qa/adoption_verification.json)\n\nThis report was moved to the model root at the researcher's request and its relative links were rebased. The existing Word validation, SPPR, diagnostics, regional results and map remain historical pre-correction artifacts. They have not been refreshed or certified equivalent to the corrected input.\n'''

notes = NOTES.read_text(encoding='utf-8')
notes = notes.replace('Regional application: `HS_077`. Canonical JSON SHA-256: `9cc8a41414194be6f40f4fafd9d6ed23c38a1c5812acd55e6e39824e783c2998`. The byte-preservation check compares this retained representation with the pre-relocation working state; it is not a fresh extraction or a new approval.',
    f'Regional application: `HS_077`. Current canonical JSON SHA-256: `{new_hash}`. The pre-correction canonical bytes are retained as [original_model.json](original_model.json), SHA-256 `{sha(old_bytes)}`, by explicit researcher instruction on 2026-10-08. This original file is the former working representation, not a claim of a pristine independent publication extraction.')
notes = notes.replace('Departures have not been independently re-extracted during this administrative task. No additional parameter correction is made. Selected canonical source retained; accepted historical transformed runtime constructed, GE and With Egestion direct OK, TE FAIL; provisional numerical display.',
    'On 2026-10-08 the researcher explicitly adopted five diet-entry relocations after the bounded source-placement tests. Exact values were preserved; only predator-column assignments changed. All nine material diet totals are now 1.000. Albacore remains 1.001, with no rounding adjustment. The corrected model retains the existing identity at the researcher\'s explicit request. Author intent remains unconfirmed.\n\n| Prey row / value | Former predator | Corrected predator | Publication locator |\n|---|---|---|---|\n| Small bigeye tuna (22), 0.022 | Large sailfish (11) | Large swordfish (12) | Table 3a, p. 158 / PDF 28, row 22 |\n| Mesopelagic fishes (32), 0.575 | Small marlins (23) | Small bigeye tuna (22) | Table 3a, p. 159 / PDF 29, row 32 |\n| Mesopelagic fishes (32), 0.121 | Small swordfish (25) | Small dorado (26) | Same row |\n| Mesopelagic fishes (32), 0.030 | Small dorado (26) | Small wahoo (27) | Same row |\n| Mesopelagic fishes (32), 0.070 | Small sharks (28) | Miscellaneous piscivores (29) | Same row |\n\nAll non-diet fields, diet imports, unknown markers and unrelated diets are unchanged. Source blanks at new destinations become the retained entries; original donor entries are absent after relocation. Dorado\'s 0.030 is moved out simultaneously with receiving 0.121. See the [misplaced diet entries report](misplaced_diet_entries_report.md) and its exact before/after ledger.\n\nExisting runtime/diagnostic evidence is historical: GE and With Egestion direct OK, TE FAIL; provisional numerical display. No downstream diagnostics, coefficients, regional calculations, Word validation or map refresh was performed after this correction, and equivalence to the corrected input has not been established.')
notes = notes.replace("The current validation document's Model extraction row records:",
    'The unchanged validation document still records the pre-correction input state quoted below; this passage is historical and superseded for the current canonical diet placements:')
notes = notes.replace('- [Canonical Ecopath representation](model.json)',
    '- [Corrected canonical Ecopath representation](model.json)\n- [Preserved pre-correction representation](original_model.json)\n- [Misplaced diet entries report](misplaced_diet_entries_report.md)')

# Complete preparation before renaming the canonical file.
assert MODEL.read_bytes() == old_bytes
assert OLD_REPORT.read_bytes() == report_before
MODEL.rename(ORIGINAL)
try:
    with MODEL.open('xb') as f:
        f.write(new_bytes)
except Exception:
    if MODEL.exists():
        MODEL.unlink()
    ORIGINAL.rename(MODEL)
    raise
OLD_REPORT.rename(REPORT)
REPORT.write_text(report, encoding='utf-8')
NOTES.write_text(notes, encoding='utf-8')

# Keep the bounded search reproducible against the preserved original.
script = RUN / 'code/test_hypotheses.py'
text = script.read_text(encoding='utf-8')
text = text.replace("PAPER = MODEL.parents[2]", "MODEL = MODEL.with_name('original_model.json') if MODEL.with_name('original_model.json').exists() else MODEL\nPAPER = MODEL.parents[2]")
script.write_text(text, encoding='utf-8')

# Append only the two authorized relocations to the portable source ledger.
ledger_before = LEDGER.read_bytes()
reader = csv.DictReader(io.StringIO(ledger_before.decode('utf-8-sig')))
fields = reader.fieldnames
assert fields is not None
buffer = io.StringIO(newline='')
writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator='\n')
for source, target, old_hash, new_hash_ledger, reason in [
    (MODEL, ORIGINAL, sha(old_bytes), sha(old_bytes), 'Researcher requested preservation of pre-correction model on 2026-10-08; corrected model.json created separately.'),
    (OLD_REPORT, REPORT, sha(report_before), sha(REPORT.read_bytes()), 'Researcher requested diet misplacement report at model root on 2026-10-08; links rebased and adoption recorded.')]:
    writer.writerow(dict(original_path=source.relative_to(ROOT).as_posix(), retained_path=target.relative_to(ROOT).as_posix(),
        sha256=old_hash, retained_sha256=new_hash_ledger, action='researcher_authorized_relocation', reason=reason,
        unit_id='HS_077', model_id=MODEL_DIR.name, extraction_run_id='2026-10-08_135441_diet_misplacement'))
assert LEDGER.read_bytes() == ledger_before
LEDGER.write_bytes(ledger_before + (b'' if ledger_before.endswith(b'\n') else b'\n') + buffer.getvalue().encode('utf-8'))

# Verify persisted bytes, semantics and all rebased links.
assert ORIGINAL.read_bytes() == old_bytes
assert MODEL.read_bytes() == new_bytes
assert json.loads(MODEL.read_text(encoding='utf-8')) == new
assert not OLD_REPORT.exists()
for ref in re.findall(r'\]\(([^)]+)\)', REPORT.read_text(encoding='utf-8')):
    if (MODEL_DIR / ref).resolve() != (RUN / 'qa/adoption_verification.json').resolve():
        assert (MODEL_DIR / ref).resolve().is_file(), ref
verification = dict(timestamp=datetime.now().astimezone().isoformat(),
    authorization='Researcher explicitly requested original_model.json preservation, corrected model.json and model-root report.',
    original_model_sha256=sha(ORIGINAL.read_bytes()), corrected_model_sha256=sha(MODEL.read_bytes()),
    original_bytes_preserved=True, only_authorized_diet_cells_changed=True,
    all_non_diet_fields_unchanged=True, full_diet_entry_multiset_unchanged=True,
    all_nine_material_totals_exactly_one=True, other_consumer_totals_unchanged=True,
    albacore_total='1.001', all_report_links_valid=True, report_moved=True,
    adopted_moves=[dict(prey_id=r, from_predator_id=s, to_predator_id=t, proportion=v) for r,s,t,v in moves],
    exact_changed_cells=changes, totals=[dict(predator_id=c, before=str(before[c]), after=str(after[c])) for c in sorted(before)],
    downstream_refresh='not performed; historical outputs preserved')
(RUN / 'qa/adoption_verification.json').write_text(json.dumps(verification, indent=2, ensure_ascii=False), encoding='utf-8')
for ref in re.findall(r'\]\(([^)]+)\)', REPORT.read_text(encoding='utf-8')):
    assert (MODEL_DIR / ref).resolve().is_file(), ref
print(json.dumps({k:v for k,v in verification.items() if k not in ('exact_changed_cells','totals')}, indent=2, ensure_ascii=False))
