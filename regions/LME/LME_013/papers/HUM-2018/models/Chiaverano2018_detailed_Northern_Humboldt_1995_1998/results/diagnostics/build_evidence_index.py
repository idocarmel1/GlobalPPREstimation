"""Inventory scientific evidence and hashes; never invokes a calculator."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
manifest=load(HERE/'run_manifest.json')
calculation=load(HERE/'candidate_calculation_manifest.json')
verification=load(HERE/'candidate_arithmetic_verification.json')
matrix=load(HERE/'retained_matrix_verification.json')
source=HERE.parent/'source/resolved_native/model.json'
input_path=HERE/'computational_input_exact.json'
artifacts=[]
required=['native_source_documents','native_source_model','computational_input','constructor_and_engine_identity','runtime_field_ledger',
          'full_direct_returns','all_returned_matrices','coefficient_scope_table','negative_entry_table',
          'runtime_normalization_cell_ledger','retained_matrix_verification','candidate_mapping',
          'regional_catch_classic_npp_context','taxon_annual_candidate_arithmetic','annual_candidate_totals',
          'annual_candidate_npp_ratios','candidate_arithmetic_verification','reproduction_entry_point']
role_paths={
    '../source/resolved_native/model.json':'native_source_model',
    'computational_input_exact.json':'computational_input',
    'run_manifest.json':'constructor_and_engine_identity',
    'loader_field_ledger.json':'runtime_field_ledger',
    'full_direct_report.json':'full_direct_returns',
    'group_scope_coefficients.csv':'coefficient_scope_table',
    'all_negative_matrix_entries.csv':'negative_entry_table',
    'runtime_normalization_changed_cells.json':'runtime_normalization_cell_ledger',
    'retained_matrix_verification.json':'retained_matrix_verification',
    '../mapping/mapping_review.json':'candidate_mapping',
    '../mapping/regional_arithmetic_snapshot.json':'regional_catch_classic_npp_context',
    'candidate_taxon_annual.csv.gz':'taxon_annual_candidate_arithmetic',
    'candidate_annual_totals.csv':'annual_candidate_totals',
    'candidate_annual_npp_ratios.csv':'annual_candidate_npp_ratios',
    'candidate_arithmetic_verification.json':'candidate_arithmetic_verification',
    'run_direct_candidate.py':'reproduction_entry_point'}
paths=[]
for p in HERE.rglob('*'):
    if p.is_file() and not any(v in p.relative_to(HERE).parts for v in ['vendor','__pycache__']):
        rel=p.relative_to(HERE).as_posix()
        if rel in ['diagnostics_evidence_index.json','diagnostics_completeness.json'] or rel=='.gitignore': continue
        paths.append(rel)
paths+=['../source/resolved_native/model.json','../source/computational/model.json',
        '../source/computational/TRANSFORMATION_LEDGER.json','../source/resolved_native/FLEET_DETRITUS_FATE.json',
        '../source/resolved_native/SOURCE_BUDGET_ARITHMETIC.json','../source/resolved_native/GROUP_IDENTITY.json',
        '../source/resolved_native/SOURCE_CELLS.json','../source/evidence/original_sources.json',
        '../mapping/mapping_review.json','../mapping/regional_arithmetic_snapshot.json','../mapping/catch_universe.json',
        '../../../papers/HUM-2018/1-s2.0-S0079661117303312-main.pdf',
        '../../../papers/HUM-2018/Supplementary material revised and final.xls',
        '../../../papers/HUM-2018/Peru paper figures and tables II.docx']
for rel in sorted(set(paths)):
    p=(HERE/rel).resolve()
    role=role_paths.get(rel,'native_source_documents' if rel.startswith('../../../papers/') else
                       ('all_returned_matrices' if p.suffix=='.npy' else 'supporting_evidence'))
    artifacts.append({'role':role,'path':rel,'sha256':sha(p),'availability':'present'})
artifacts.extend([
    {'role':'native_fishery_discard_return_ancestry','availability':'inapplicable',
     'reason':'The exact source records quantities and fleet routing, but the current SPPR engine recycling equations do not implement donor-resolved fishery return ancestry. No synthetic external import substituted.',
     'acquisition_status':'Native evidence retained; unsupported engine representation remains explicit.'},
    {'role':'TE_EE0_detritus_recredit','availability':'inapplicable',
     'reason':'Engine fix_EE_0_cases is requested but supports only a single detritus pool; four-pool translation emits an explicit warning and applies no correction.',
     'acquisition_status':'Actual direct TE warning/return retained.'},
    {'role':'adoption_or_published_regional_PPR','availability':'inapplicable',
     'reason':'The task authorizes isolated candidate evidence only; every method returns FAIL and every annual model result remains production-ineligible.',
     'acquisition_status':'No active model, workbook, Project, map, graph or approval write performed.'}])
reconciliation={**manifest['reconciliation'],
    'retained_matrix_masks_axes_and_scope_sums':matrix['status']=='PASS',
    'retained_candidate_arithmetic':verification['status']=='PASS',
    'no_biological_method_mutations':load(HERE/'method_runtime_state_ledger.json')['biological_fields_changed']==[],
    'source_computational_input_identity_matches_copy':sha(HERE.parent/'source/computational/model.json')==manifest['input_sha256']==sha(input_path),
    'candidate_mapping_hash_matches_arithmetic':sha((HERE/calculation['mapping_path']).resolve())==calculation['mapping_sha256'],
    'all_candidate_results_ineligible':verification['all_rows_production_ineligible']}
index={'schema_version':1,'run_id':manifest['run_id'],'region_id':'LME_013',
       'model_id':manifest['model_id'],'variant_id':'native_supplement_runtime_DC_normalized_no_BA_compensation',
       'source_identity':{'path':'../source/resolved_native/model.json','sha256':sha(source),
                          'citation':'Chiaverano et al. 2018, Progress in Oceanography164,28–36',
                          'DOI':'10.1016/j.pocean.2018.04.009','model_period':'1995–1998',
                          'native_supplement_sha256':sha(HERE/'../../../papers/HUM-2018/Supplementary material revised and final.xls')},
       'computational_input_identity':{'path':'computational_input_exact.json','sha256':sha(input_path)},
       'methods':['GE','TE','With Egestion'],'required_roles':required,
       'artifacts':artifacts,'reconciliation':reconciliation,
       'scope':'Candidate diagnostics and arithmetic evidence only; no configuration authority or adoption state is assigned.'}
(HERE/'diagnostics_evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'artifacts':len(artifacts),'required_roles':len(required),'all_reconciliations_passed':all(reconciliation.values())}))
