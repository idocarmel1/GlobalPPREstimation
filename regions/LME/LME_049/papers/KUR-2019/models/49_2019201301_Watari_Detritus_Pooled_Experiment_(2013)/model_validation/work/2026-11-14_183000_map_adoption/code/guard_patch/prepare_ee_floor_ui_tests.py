"""Stage copy-only UI regression tests; do not change production sources."""
import sys, hashlib, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'tools/workflow_checks/maps/check_ee_floor_views.js'
original=SOURCE.read_text('utf-8')
def replace_once(text, old, new):
    assert text.count(old)==1, old
    return text.replace(old,new,1)
updated=replace_once(original, "  assert.match(panel.textContent,/does not approve/i);",
"""  assert.match(panel.textContent,/The signed researcher review applies to the model, diagnostics and calculation conditions recorded in its report\\. Other method results retain their own diagnostic status\\./);
  assert.doesNotMatch(panel.textContent,/does not approve this changed/);
  assert.match(panel.textContent,/1 affected groups\\./);
  assert.match(panel.textContent,/External mortality export: 1\\.5/);""")
updated=replace_once(updated,
"""  assert.match(unsignedPanel.textContent,/require separate researcher review/);
  assert.doesNotMatch(unsignedPanel.textContent,/The signed researcher review retains/,'An unreviewed model must not gain a claimed signature');""",
"""  assert.match(unsignedPanel.textContent,/No verified researcher review is recorded for this model\\./);
  assert.doesNotMatch(unsignedPanel.textContent,/The signed researcher review applies/,'An unreviewed model must not gain a claimed signature');
  const pending={...unsigned,recorded_review_pending:{recorded_status:'Validated by researcher',researcher_name:'R',review_date:'2026-09-01',reason:'The source report changed'}};
  const pendingBefore=JSON.stringify(pending),pendingPanel=new Element('div');reviewView.append(pendingPanel,pending);
  assert.match(pendingPanel.textContent,/The recorded researcher review is awaiting current verification\\./);
  assert.doesNotMatch(pendingPanel.textContent,/The signed researcher review applies|No verified researcher review is recorded/);
  assert.equal(JSON.stringify(pending),pendingBefore,'Pending status and recorded review remain unchanged');
  const rejected={...model,researcher_review:{...review,status:'Disqualified by researcher',verdict:'Disqualified',reason:'Retained scientific limitation'}};
  const rejectedBefore=JSON.stringify(rejected),rejectedPanel=new Element('div');reviewView.append(rejectedPanel,rejected);
  assert.equal(reviewView.isValidated(rejected),false);
  assert.match(rejectedPanel.textContent,/Disqualified.*Retained scientific limitation/);
  assert.equal(JSON.stringify(rejected),rejectedBefore,'Presentation cannot reverse a disqualification');""")
updated=replace_once(updated,
"  const offPanel=new Element('div');reviewView.append(offPanel,off);assert.match(offPanel.textContent,/EE floor OFF/);",
"""  const offBefore=JSON.stringify(off),offPanel=new Element('div');reviewView.append(offPanel,off);assert.match(offPanel.textContent,/EE floor OFF/);
  assert.match(offPanel.textContent,/No EE floor is applied in this saved calculation\\./);
  assert.doesNotMatch(offPanel.textContent,/hypothetical external nonfishery mortality sink|affected groups|External mortality export:/i);
  assert.equal(JSON.stringify(off),offBefore,'Floor-off display leaves saved fields and review unchanged');""")
updated=replace_once(updated,
"  const noAffectedPanel=new Element('div');reviewView.append(noAffectedPanel,noAffected);assert.match(noAffectedPanel.textContent,/EE floor ON \\(0\\.1\\)/);",
"""  const noAffectedPanel=new Element('div');reviewView.append(noAffectedPanel,noAffected);assert.match(noAffectedPanel.textContent,/EE floor ON \\(0\\.1\\)/);
  assert.match(noAffectedPanel.textContent,/hypothetical external nonfishery mortality sink/i);
  assert.match(noAffectedPanel.textContent,/0 affected groups\\./);
  assert.match(noAffectedPanel.textContent,/External mortality export: 0 /);""")
(OUT/'check_ee_floor_views_candidate.js').write_text(updated,encoding='utf-8',newline='\n')
record={'base_js_sha256':hashlib.sha256((ROOT/'tools/project_core/maps/ee_floor.js').read_bytes()).hexdigest(),'base_test_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
(OUT/'ee_floor_ui_baseline.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'staged_test':str(OUT/'check_ee_floor_views_candidate.js'),**record},ensure_ascii=False))

