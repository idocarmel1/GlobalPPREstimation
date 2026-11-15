'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const target = path.join(__dirname, 'cleanup_after_acceptance.cjs');
const api = fs.existsSync(target) ? require(target) : {};
const H = 'a'.repeat(64), J = 'b'.repeat(64);
function guard() { assert.equal(typeof api.assertAcceptanceShape, 'function', 'Acceptance guard not implemented'); }
function fixture() {
  const units = Array.from({length:16}, (_, i) => 'UNIT_' + i);
  const sources = {'Project.xlsx':H, 'interactive_map/index.html':H, 'interactive_map/trends.html':H};
  return {
    units, current:sources, adoptionHash:J,
    status:{phase:'COMPLETED',exit_code:0}, publication:{project_sha256:H,scientific_execution_performed:false},
    final:{status:'PASS_FINAL_PUBLICATION',project_sha256:H,validated_pairs:16,researcher_exclusions:57,
      preservation_evidence:{adoption_sha256:J}, pages:Object.keys(sources).filter(p=>p.endsWith('.html')).map(p=>({path:p,sha256:H,project_sha256:H}))},
    browser:{status:'PASS',checks:Array.from({length:7},()=>({status:'PASS'})),page_errors:[],source_sha256_before:sources,source_sha256_after:sources},
    table:{passed:true,source_sha256:{'Project.xlsx':H,'interactive_map/trends.html':H},
      tables:Object.fromEntries(['landings','catch'].map(b=>[b,{rows:units.map(id=>({id,values:[{value:1},{value:2},{value:3}]}))}])),
      annual_checks:units.flatMap(unit_id=>['landings','catch'].map(catch_basis=>({unit_id,catch_basis,passed:true,years_with_control_results:70})))}
  };
}
test('accepts complete, consistently fingerprinted QA', () => { guard(); assert.doesNotThrow(()=>api.assertAcceptanceShape(fixture())); });
test('rejects running or failed adoption and unsuccessful QA', () => {
  guard(); for (const mutate of [x=>x.status.phase='RUNNING',x=>x.status.exit_code=1,x=>x.final.status='FAIL',x=>x.browser.status='FAIL',x=>x.table.passed=false]) {
    const x=fixture(); mutate(x); assert.throws(()=>api.assertAcceptanceShape(x));
  }
});
test('rejects stale Project, page, adoption certificate and table fingerprints', () => {
  guard(); for (const mutate of [x=>x.current['Project.xlsx']=J,x=>x.current['interactive_map/trends.html']=J,x=>x.final.preservation_evidence.adoption_sha256=H,x=>delete x.table.source_sha256,x=>x.table.source_sha256['Project.xlsx']=J]) {
    const x=fixture(); mutate(x); assert.throws(()=>api.assertAcceptanceShape(x));
  }
});
test('rejects partial or duplicate annual/table cohorts and browser errors', () => {
  guard(); for (const mutate of [x=>x.table.annual_checks.pop(),x=>x.table.annual_checks[0]=x.table.annual_checks[1],x=>x.table.tables.landings.rows.pop(),x=>x.browser.page_errors.push({message:'bad'})]) {
    const x=fixture(); mutate(x); assert.throws(()=>api.assertAcceptanceShape(x));
  }
});
test('rejects path escape, absolute paths, alternate streams and drive paths', () => {
  assert.equal(typeof api.safeRelative,'function','Path guard not implemented');
  for(const p of ['../Project.xlsx','a/../../x','C:/temp/x','C:\\temp\\x','/tmp/x','a/file:stream','a\u0000b','a/./b','a/.. /b','a/name./b']) assert.throws(()=>api.safeRelative(p));
  assert.equal(api.safeRelative('regions/LME/LME_003/work/cache.bin'),'regions/LME/LME_003/work/cache.bin');
});
test('CSV parser and encoder preserve quoted commas, newlines and Unicode', () => {
  assert.equal(typeof api.parseCsv,'function','CSV parser not implemented');
  assert.equal(typeof api.encodeCsvRows,'function','CSV encoder not implemented');
  const rows=[['path','reason'],['אישי/a,b','quote " and\nnewline']];
  assert.deepEqual(api.parseCsv(api.encodeCsvRows(rows)),rows);
  assert.throws(()=>api.parseCsv('a,"unterminated'));
});
test('candidate admission cannot target canonical scientific files or active locks', () => {
  assert.equal(typeof api.assertOwnedDeletion,'function','Deletion allowlist not implemented');
  const work='regions/LME/LME_003/work/2026-11-14_235900_deterministic_coverage';
  const hum='regions/LME/LME_013/papers/HUM-2018/models/Chiaverano2018_detailed_Northern_Humboldt_1995_1998/model_validation/work/2026-11-15_011000_ee_floor_docx';
  for(const p of ['Project.xlsx',work+'/tmp/adoption_supervisor.lock',work+'/outputs/final_cohort_audit.json','tools/scientific_code/PPREstimation/PPRCalculator.py',work+'/tmp/adoption_recovery_attempt3/objects/not-a-sha']) assert.throws(()=>api.assertOwnedDeletion(p,work,hum));
  for(const p of [work+'/code/__pycache__/x.pyc',hum+'/qa/final_render/page-1.png',work+'/tmp/adoption_recovery_attempt3/objects/'+H,work+'/tmp/adoption_recovery_attempt3/manifest.json',work+'/inputs/Project_before_humboldt_review.xlsx']) assert.doesNotThrow(()=>api.assertOwnedDeletion(p,work,hum));
});
