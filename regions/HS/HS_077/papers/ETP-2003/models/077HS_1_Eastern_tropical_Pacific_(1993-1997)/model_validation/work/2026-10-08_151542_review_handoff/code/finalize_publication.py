from pathlib import Path
HERE=Path(__file__).resolve().parent
helper=(HERE/'publish_review.py').read_text(encoding='utf-8')
exec(helper[:helper.index('\nprepared=')])
prepared=json.loads((W/'qa/prepared_results.json').read_text(encoding='utf-8'))
project=ROOT/'Project.xlsx';regional=ROOT/'regions/HS/HS_077/HS_077.xlsx';report=M/'model_validation/validation.docx';pages=ROOT/'interactive_map'
report_sha=sha(report);name,date,summary=read_report(ROOT,report,M.name)
expected=['Grazing birds','Pursuit birds','Toothed whales','Spotted dolphin','Mesopelagic dolphins','Large sharks','Small sharks'];seq=[2,1,4,5,6,15,28]
original=W/'inputs/publication_before/Project.xlsx';before_rows=model_rows(original);before_project=sha(original)
with wait_lock():
 print('Final verification lock acquired; adopted science remains unchanged.',flush=True)
 with zipfile.ZipFile(project) as z:assert z.testzip() is None
 assert sha(regional)==prepared['regional_staged_sha256']
 assert sha(M/'sppr_source.xlsx')==prepared['coefficient_source_sha256']
 assert sha(M/'model.json')==prepared['canonical_model_sha256']
 assert sha(M/'results/regional_snapshot.xlsx')==sha(regional)
 current_rows=model_rows(project);current={(r['unit_id'],r['model_id']):r for r in current_rows};empty=[]
 fields=['researcher_review_status','researcher_name','researcher_review_date','validation_report_path','validation_report_sha256','reviewed_model_sha256','reviewed_calculation_input_sha256','researcher_review_summary']
 for r in before_rows:
  if (r['unit_id'],r['model_id'])==('HS_077',M.name):continue
  a=current[r['unit_id'],r['model_id']]
  for field in fields:
   assert (a.get(field) or '')==(r.get(field) or ''),(r['unit_id'],field)
   if a.get(field)!=r.get(field):empty.append({'unit_id':r['unit_id'],'model_id':r['model_id'],'field':field,'old':r.get(field),'new':a.get(field),'meaning':'Equivalent empty cell; no review/source identity lost'})
 (W/'qa/unrelated_review_preservation.json').write_text(json.dumps({'all_nonempty_review_values_unchanged':True,'equivalent_empty_cell_serializations':empty},indent=2),encoding='utf-8')
 current_fingerprint=sha(project)
 assert all(f'<meta name="ppr-project-sha256" content="{current_fingerprint}">' in (pages/n).read_text(encoding='utf-8') for n in ['index.html','trends.html'])
 latest_dir=W/'inputs/final_metadata_before';latest_dir.mkdir(exist_ok=True);shutil.copy2(project,latest_dir/'Project.xlsx')
 for n in ['index.html','trends.html','sources.html']:shutil.copy2(pages/n,latest_dir/n)
 before_map,_=embedded(pages/'index.html','DB');before_series,_=embedded(pages/'trends.html','SERIES_DB')
 values={'loadability_class':'Current working model state (ungraded): researcher-adopted corrected source loads with reviewed LIM settings; fresh GE, TE and With Egestion diagnostics WARN.','full_model_loadable':'Corrected working model constructed with reviewed LIM settings; original representation preserved separately.','quality_rationale':'Historical numeric scores retained without regrading. The researcher adopted five exact diet-entry relocations and signed MODEL VALIDATED on 08/10/2026. Fresh GE, TE and With Egestion returns are WARN; TE fails strict SPPR balance. Approximately 47% target coverage and low geographic confidence remain unchanged. Researcher validation is separate from production eligibility.','recommendation':'Selected ETP7 model was validated by Ido Carmel on 08/10/2026 after adopting five diet-entry relocations. Retain provisional numerical display and diagnostic restrictions; seven reviewed groups are excluded only from displayed PPR. The source remains a partial geographic proxy for HS_077.','loadability_evidence':'Fresh corrected model execution on 2026-10-08 uses the signed notebook LIM constructor and default GE/TE/With Egestion configurations. Canonical source, executed engine, runtime transformations and complete returned matrices/scopes are retained in '+(W/'outputs/diagnostics/run_manifest.json').relative_to(ROOT).as_posix()+'. All three grades WARN; GE and With Egestion pass strict SPPR balance, TE fails it. Source biomass accumulation and detritus routing remain undocumented; no author-native EwE file recovered.'}
 try:
  patch_metadata(project,values,sheet_name='Papers',table_name='Papers',identity_field='article_id',identity='ETP-2003__HS_077')
  build(project,only_units=['HS_077'])
 except BaseException:
  temp=project.with_name('.hs077-final-metadata-rollback.xlsx');shutil.copy2(latest_dir/'Project.xlsx',temp);os.replace(temp,project)
  for n in ['index.html','trends.html','sources.html']:
   temp=(pages/n).with_name('.hs077-final-rollback-'+n);shutil.copy2(latest_dir/n,temp);os.replace(temp,pages/n)
  raise
 after_index={(r['unit_id'],r['model_id']):r for r in model_rows(project)}
 for r in current_rows:
  assert after_index[r['unit_id'],r['model_id']]==r
 row=after_index['HS_077',M.name];registered=json.loads(row['researcher_review_summary'])
 assert registered['sections']==summary['sections'] and set(registered['excluded_group_ids'])==set(expected)
 assert row['validation_report_sha256']==sha(report)==report_sha
 assert row['reviewed_model_sha256']==sha(M/'model.json')
 assert row['reviewed_calculation_input_sha256']==prepared['calculation_input_sha256']
 catalog,_=embedded(pages/'index.html','DB');series,_=embedded(pages/'trends.html','SERIES_DB')
 cm=next(m for m in catalog['network']['units']['HS_077']['models'] if m['id']==M.name)
 sm=next(m for m in series['units']['HS_077']['models'] if m['id']==M.name)
 assert cm['researcher_review']==sm['researcher_review']
 assert cm['researcher_review']['sections']==summary['sections']
 assert cm['display_ppr_excluded_group_ids']==sm['display_ppr_excluded_group_ids']==registered['excluded_group_ids']
 assert cm['workbook_sha256']==sm['workbook_sha256']==sha(regional)
 for unit,payload in before_map['network']['units'].items():assert catalog['network']['units'][unit]==payload,unit
 for unit,payload in before_series['units'].items():assert series['units'][unit]==payload,unit
 fingerprint=sha(project)
 for n in ['index.html','trends.html']:assert f'<meta name="ppr-project-sha256" content="{fingerprint}">' in (pages/n).read_text(encoding='utf-8')
 note=M/'model_notes.md';text=note.read_text(encoding='utf-8')
 old='Existing runtime/diagnostic evidence is historical: GE and With Egestion direct OK, TE FAIL; provisional numerical display. No downstream diagnostics, coefficients, regional calculations, Word validation or map refresh was performed after this correction, and equivalence to the corrected input has not been established.'
 new='On 2026-10-08, the corrected canonical model and reviewed notebook constructor/default method settings were executed directly for GE, TE and With Egestion. All three current diagnostic grades are WARN; GE and With Egestion pass strict SPPR balance, TE fails that strict check. Current coefficients and regional arithmetic were refreshed and their exact source, engine, runtime and full returns retained in [review refresh evidence](model_validation/work/2026-10-08_151542_review_handoff/outputs/diagnostics/run_manifest.json). Production eligibility remains false; provisional numerical display is retained. Catch, NPP, taxon mappings and the independent classic coefficients are unchanged. Historical sensitivity bounds were invalidated. Ido Carmel signed MODEL VALIDATED on 08/10/2026; the seven named exclusions apply only to displayed PPR, and are registered in Project and the map. The signed Word retains researcher-written historical source/diagnostic descriptions; current scientific discrepancies are recorded here rather than rewriting the signed review.'
 assert old in text;text=text.replace(old,new).replace('The unchanged validation document still records the pre-correction input state quoted below;','The signed validation document still records the pre-correction input state quoted below;');note.write_text(text,encoding='utf-8')
 proof={'project_before_sha256':before_project,'project_after_sha256':fingerprint,'regional_sha256':sha(regional),'report_sha256':report_sha,'reviewer':name,'signed_date':date,'model_id':M.name,'excluded_group_seq':seq,'excluded_group_names':expected,'scoped_refresh_from_latest_matching_pages':True,'unrelated_central_reviews_preserved':True,'unrelated_page_payloads_preserved':True,'canonical_source_unchanged':sha(M/'model.json')==prepared['canonical_model_sha256'],'all_six_word_pages_visually_verified':True,'current_diagnostic_grades':prepared['methods'],'empty_cell_serialization_equivalence_audit':'unrelated_review_preservation.json'}
 (W/'qa/publication_verified.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof,indent=2),flush=True)
print('HS_077 scientific and signed review publication verified; shared lock released.',flush=True)
