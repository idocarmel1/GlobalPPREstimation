"""Create a portable current evidence inventory with explicit source-fidelity limits."""
import importlib.util,json,os,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import sha

def main():
    config=json.loads((OUT/'refresh_configuration.json').read_text(encoding='utf-8'))
    artifacts=[]
    def add(role,path):
        path=Path(path);assert path.is_file(),path
        artifacts.append({'role':role,'availability':'present','path':os.path.relpath(path,OUT).replace('\\','/'),'sha256':sha(path)})
    add('source_pdf',ROOT/'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf')
    add('canonical_raw_model',ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json')
    add('sppr_export',ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/sppr_source.xlsx')
    add('regional_workbook',ROOT/'regions/LME_034/LME_034.xlsx')
    add('central_workbook',ROOT/'Project.xlsx')
    for name in ['table17_source_ledger.json','current_source_verification.json','source_runtime_separation.json',
                 'meiobenthos_source_justification.json','missing_diet_source_sweep.json','initial_diet_appendix_sweep.json','refresh_configuration.json','constructor_warnings.json',
                 'direct_current_export_reconciliation.json','regional_adoption.json','central_integration.json','html_verification.txt','README.md']:
        add(name.rsplit('.',1)[0],OUT/name)
    for page in [25,26,27]:add(f'Table17_page_{page}',OUT/f'Table17_p{page}_200dpi.png')
    for folder in ['GE','TE','With_Egestion']:
        for path in sorted((OUT/'direct_diagnostics'/folder).iterdir()):
            if path.is_file():add(folder+'_'+path.name.replace('.','_'),path)
    for name in ['restore_table17.py','refresh_outputs.py','adopt_regional_outputs.py','finish_source_evidence.py','verify_current_source.py','missing_diet_source_sweep.py','integrate_central.py','index_current_evidence.py']:
        add('reproduction_'+name[:-3],OUT/name)
    for filename in ['source_audit.json','source_findings.txt','audit_source.py']:
        add('source_audit_'+filename.replace('.','_'),OUT.parent/'source_diagnostics'/filename)
    for filename in ['ModelData.py','PPRCalculator.py','utils.py','create_PPRS_excel.py']:
        path=ROOT/'tools/scientific_code/PPREstimation'/filename
        assert sha(path)==config['engine_hashes'][filename],filename
        add('engine_'+filename[:-3],path)
    for filename in ['index.html','trends.html','archive/index.html']:
        add('generated_'+filename.replace('/','_').replace('.','_'),ROOT/'interactive_map'/filename)
    assert sha(ROOT/'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json')==config['canonical_model_sha256']
    data={'schema_version':1,'run_id':config['run_id'],'region_id':'LME_034','model_id':'34_1_Bay_of_Bengal_(1978)',
        'variant_id':'printed_raw_diets_with_researcher_meiobenthos_override_runtime_normalization',
        'source_identity':{'pdf_sha256':artifacts[0]['sha256'],'diet_pages':[25,26,27],'known_cells':2155,'unknown_cells':45},
        'computational_input_identity':{'canonical_sha256':config['canonical_model_sha256'],'normalization':'calculator copy only','researcher_override':'group40 Detritus1','constructor':config['constructor']},
        'methods':config['methods'],'required_roles':[a['role'] for a in artifacts], 'artifacts':artifacts,
        'reconciliation':{'printed_source_matches_except_authorized_override':True,'raw_source_sums_observable':True,
            'loader_warning_observed':True,'direct_matrices_match_current_export':True,'protected_regional_tables_preserved':True,
            'other_central_units_preserved':True,'generated_pages_match_current_project':True},
        'scientific_limits':{'native_author_source_available':False,'production_eligible':False,
            'missing_diet_cells_recovered':False,'researcher_override_is_literal_group40_source_value':False,
            'negative_symbolic_results':'Existing unstable as_DC formulations remain flagged; current negative values retained',
            'monte_carlo':'Retained75-draw settings; native spawned-worker seed unspecified; fresh run-specific stochastic estimates'}}
    spec=importlib.util.spec_from_file_location('check_current_evidence',ROOT/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    path=OUT/'operational_evidence_index.json';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result=checker.check(path);assert result['complete'],result
    (OUT/'operational_evidence_completeness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    data['required_roles'].append('author_native_balanced_model')
    data['artifacts'].append({'role':'author_native_balanced_model','availability':'missing',
        'reason':'No author-native balanced database recovered; printed diet omissions and explicit researcher reconstruction remain',
        'acquisition_status':'Bounded previous local/source recovery recorded in source diagnostics; no additional acquisition attempted in this restoration'})
    path=OUT/'evidence_index.json';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result=checker.check(path);assert not result['complete'] and result['missing_roles']==['author_native_balanced_model'] and result['errors']==[],result
    (OUT/'evidence_completeness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'operational_evidence_complete':True,'scientific_source_fidelity_complete':False,'missing_roles':result['missing_roles'],'artifacts_verified':len(result['verified_artifacts'])}))

if __name__=='__main__':main()
