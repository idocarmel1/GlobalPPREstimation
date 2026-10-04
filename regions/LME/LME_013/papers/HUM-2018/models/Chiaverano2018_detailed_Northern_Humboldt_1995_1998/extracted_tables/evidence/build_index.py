"""Seal candidate evidence inventory without re-executing scientific methods."""
from pathlib import Path
import os,json,hashlib
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=read(BASE/'diagnostics/run_manifest.json');qa=read(BASE/'qa/final_verification.json')
roles={
 'README.md':'review_guide',
 'source/evidence_index.json':'source_stage_inventory',
 'source/resolved_native/model.json':'canonical_source',
 'source/computational/model.json':'computational_input',
 'source/resolved_native/ROUND_TRIP_CHECKS.json':'source_round_trip',
 'source/SOURCE_CONFLICTS.json':'source_conflicts',
 'source/resolved_native/Taxonomy.xlsx':'taxonomy',
 'source/aggregated_alternative_source.json':'alternative_assessment',
 'mapping/evidence_index.json':'mapping_stage_inventory',
 'mapping/mapping_review.json':'complete_mapping',
 'mapping/allocation_ledger.json':'allocation_quantities',
 'mapping/search_records.json':'composition_searches',
 'mapping/regional_arithmetic_snapshot.json':'regional_inputs',
 'diagnostics/diagnostics_evidence_index.json':'diagnostics_stage_inventory',
 'diagnostics/run_manifest.json':'diagnostic_settings_and_identities',
 'diagnostics/full_direct_report.json':'full_direct_returns',
 'diagnostics/all_negative_matrix_entries.csv':'all_negative_pairs',
 'diagnostics/loader_matrix_field_ledger.json':'loader_matrix_transforms',
 'diagnostics/runtime_normalization_changed_cells.json':'runtime_normalization',
 'diagnostics/candidate_calculation_manifest.json':'candidate_calculations',
 'diagnostics/candidate_taxon_annual.csv.gz':'taxon_year_contributions',
 'diagnostics/candidate_annual_totals.csv':'annual_candidate_totals',
 'diagnostics/candidate_annual_npp_ratios.csv':'candidate_npp_ratios',
 'diagnostics/candidate_arithmetic_verification.json':'arithmetic_verification',
 'geography/geographic_assessment.json':'geographic_assessment',
 '../../Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx':'validation_docx',
 '../../LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx':'linked_excel_appendix',
 'qa/candidate_validation.pdf':'rendered_validation',
 'qa/final_verification.json':'final_acceptance_and_preservation',
 'protected_baseline.json':'protected_baseline'}
imports=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']
for name in imports:roles['source/resolved_native/'+name]='EwE_import_'+name
for method in ['GE','TE','With_Egestion']:
 for matrix in ['SPPR','A','L']:roles[f'diagnostics/{method}/{matrix}.npy']=f'{method}_{matrix}'
files=set(roles)
for folder in ['source','mapping','diagnostics','geography']:
 for current,dirs,names in os.walk(BASE/folder,followlinks=False):
  dirs[:]=[d for d in dirs if d not in ['vendor','node_modules','__pycache__','.venv']]
  for name in names:
   if name.lower()=='notes for ai.txt' or name=='.gitignore':continue
   files.add((Path(current)/name).relative_to(BASE).as_posix())
for p in BASE.glob('*.py'):files.add(p.name)
for p in BASE.glob('*.mjs'):files.add(p.name)
files.add('context.json')
for i in range(1,8):files.add(f'qa/candidate_validation_page_{i:02d}.png')
for name in ['top','middle','bottom','sources','saved_sources','saved_longest_reason','artifact_verification.json']:files.add('qa/appendix/'+name+('' if name.endswith('.json') else '.png'))
files.add('qa/document_fidelity.json');files.add('qa/appendix_links.json');files.add('qa/artifact.md')
artifacts=[{'role':roles.get(rel,'supporting_evidence'),'path':rel,'availability':'present','sha256':sha((BASE/rel).resolve())} for rel in sorted(files)]
for name in ['source/evidence_index.json','mapping/evidence_index.json','diagnostics/diagnostics_evidence_index.json']:
 for a in read(BASE/name)['artifacts']:
  if a['availability']!='present':artifacts.append(a)
reconciliations={'source_stage_complete':read(BASE/'source/completeness.json')['complete'],
 'mapping_stage_complete':read(BASE/'mapping/evidence_completeness.json')['complete'],
 'diagnostic_stage_complete':read(BASE/'diagnostics/diagnostics_completeness.json')['complete'],
 'final_delivery_checks':qa['status']=='PASS',
 'all_protected_files_unchanged':not qa['changed_protected_files'],
 'mapping_hash_matches_final_arithmetic':qa['mapping_sha256']==read(BASE/'diagnostics/candidate_calculation_manifest.json')['mapping_sha256'],
 'source_round_trip':read(BASE/'source/resolved_native/ROUND_TRIP_CHECKS.json')['passed']}
index={'schema_version':1,'run_id':'HUM2018_20261003_complete_candidate_review','region_id':'LME_013',
 'model_id':'HUM2018_resolved_native','variant_id':'native_supplement_unrepaired_separate_runtime_normalization',
 'source_identity':{'doi':'10.1016/j.pocean.2018.04.009','canonical_sha256':sha(BASE/'source/resolved_native/model.json')},
 'computational_input_identity':{'path':'source/computational/model.json','sha256':sha(BASE/'source/computational/model.json'),'direct_run_id':run['run_id']},
 'methods':['GE','TE','With Egestion'],'required_roles':sorted(set(roles.values())),
 'artifacts':artifacts,'reconciliation':reconciliations,'production_eligible':False,
 'limits':'Inventory completion is distinct from scientific validity. Three direct methods returned FAIL; native-flow translation is incomplete; candidate arithmetic remains ineligible. Researcher approval and active adoption are outside this task.'}
(BASE/'evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'artifacts':len(artifacts),'required_roles':len(index['required_roles']),'reconciliations':reconciliations}))
