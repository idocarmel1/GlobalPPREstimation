import hashlib,json
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());QA=Path(__file__).parent.parent/'qa'
findings=json.loads((QA/'retained_file_findings.json').read_text('utf8'));out=[]
current=[p for p in(ROOT/'tools/workflow_checks').rglob('*')if p.is_file()and p.suffix in{'.py','.js'}and '__pycache__'not in p.parts]
for r in findings['findings'].get('missing',[]):
 matches=[p for p in current if p.name==Path(r['original_path']).name]
 if len(matches)!=1:out.append(dict(r,status='unresolved',candidates=[p.relative_to(ROOT).as_posix()for p in matches]));continue
 p=matches[0];out.append(dict(r,status='resolved_later_responsibility_move',actual_retained_path=p.relative_to(ROOT).as_posix(),actual_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reason='Checks/tools subsequently organized into their approved responsibility package; implementation imports updated.'))
(QA/'late_move_reconciliation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Late responsibility moves resolved',sum(r['status']=='resolved_later_responsibility_move'for r in out),'of',len(out))
# This obsolete model-dependent workbook is intentionally not relabeled as a current variant.
q=json.loads((QA/'previous_results_fast_review.json').read_text('utf8'))
r=next(x for x in q if x.get('results_model_id')=='27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991)')
r.update(disposition='obsolete_extraction_dependent_output_removed',reason='No retained canonical representation has the recorded historical input hash; no reviewed identity equivalence or scientific authorization supports relabeling its coefficients under published Base, approximation or native EcoBase689.',retained_historical_study_input='research/discard_sensitivity_expanded_2026_09_10/inputs/corpus/global_cover_jsons/27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991).json',retained_historical_input_role='Frozen input of the substantive discard-sensitivity study, explicitly historical; it is not a canonical current extraction or current result authority.',coefficient_reuse='not permitted; actual recorded model hash differs and Matching/Annual are absent')
(QA/'obsolete_previous_result_disposition.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
