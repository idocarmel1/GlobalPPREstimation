"""Read-only stage audit and portable aggregate inventory; never recalculate science."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, importlib.util, json, math, os, re, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
C = HERE.parents[1]
A = C / 'assumption_variants/adopted_balanced_20261003'
I = HERE.parent / 'integration'
REGION = ROOT / 'regions/LME_052'
E = REGION / 'validation_reports/52_GM2019_Fig9_Pelagic_(2000-2014)'
MODEL_ID = '52_GM2019_Fig9_Pelagic_balanced_(2000-2014)'
MODEL_HASH = '9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656'
NATIVE_INDEX_HASH = 'c22dbc130886699f67c1a0026a2cef97c7a971f80be91d2e821a144a16bd295f'
NATIVE_CHECK_HASH = '1f7ae77ddb6ea9b5ae4c10e4ae9b34d84075a4290b939be2b4cdc2316b33dac1'

def sha(p):
    assert Path(p).name.casefold() != 'notes for ai.txt'
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    assert Path(p).name.casefold() != 'notes for ai.txt'
    return json.loads(Path(p).read_text(encoding='utf-8'))

def optional(p):
    return read(p) if Path(p).is_file() else None

def rel(p):
    return Path(os.path.relpath(Path(p).resolve(), HERE)).as_posix()

def save(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def boolean_checks(obj, key='checks'):
    return bool(obj) and bool(obj.get(key)) and all(v is True for v in obj[key].values())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-proof', type=Path)
    args = parser.parse_args()
    artifacts, required, seen = [], set(), set()
    def add(role, p, must=True, expected=None):
        if must: required.add(role)
        key = (role, str(Path(p).resolve()))
        if key in seen: return
        seen.add(key)
        if Path(p).is_file():
            actual = sha(p)
            item = dict(role=role, availability='present', path=rel(p), sha256=actual,
                        size_bytes=Path(p).stat().st_size)
            if expected is not None: item['prior_expected_sha256'] = expected
            artifacts.append(item)
        else:
            artifacts.append(dict(role=role, availability='missing', path=rel(p),
                                  reason='Required stage output is not yet retained at inventory time.',
                                  acquisition_status='awaiting_final_stage_completion'))

    native_index = read(A / 'evidence_index.json')
    native_check = read(A / 'evidence_completeness.json')
    add('native.index', A / 'evidence_index.json')
    add('native.inventory_check', A / 'evidence_completeness.json')
    native_cohort_matches = True
    for item in native_index['artifacts']:
        p = (A / item['path']).resolve()
        native_cohort_matches &= p.is_file() and sha(p) == item['sha256']
        add('native.' + item['role'], p, must=item['role'] in native_index['required_roles'], expected=item['sha256'])
    for case in read(A / 'case_coverage.json'):
        case_path = A / case['path'].replace('\\','/')
        if case_path.suffix == '.json': case_path = case_path.parent
        add('native.case.' + case['case'] + '_F62_' + str(case['F62']).replace('.', 'p'),
            case_path / 'native_reload_result.json')

    role_data = read(ROOT / 'common_reference_data/paper_file_roles.json')
    target_roles = [r for r in role_data['files'] if r['path'].startswith('regions/LME_052/papers/OKH-GM2019/')]
    role_guard = len(target_roles) == 12 and len({r['path'] for r in target_roles}) == 12
    for record in target_roles:
        p = ROOT / record['path']
        role_guard &= p.is_file() and sha(p) == record['sha256']
        add('source.reviewed_file.' + p.name, p, expected=record['sha256'])
    for role, p in [
        ('source.file_roles', ROOT/'common_reference_data/paper_file_roles.json'),
        ('source.file_role_metadata_proof', HERE/'paper_file_role_metadata_proof.json'),
        ('source.file_role_registration_code', HERE/'register_paper_file_roles.py'),
        ('source.file_roles_after', HERE/'paper_file_roles.after_LME052.json'),
        ('regional.workbook', REGION/'LME_052.xlsx'),
        ('regional.taxon_appendix', REGION/(MODEL_ID+'_taxon_mapping_appendix.xlsx')),
        ('central.project', ROOT/'Project.xlsx'),
        ('central.registration', HERE/'registry_registration.json'),
        ('central.patch_spec', HERE/'registry_patch_spec.json'),
        ('central.independent_native_gate', HERE/'independent_final_gate.json'),
        ('central.payload_verification', HERE/'central_payload_verification.json'),
        ('central.classic_numeric_and_blank_row_exception', HERE/'independent_classic_verification.json'),
        ('central.six_unavailable_bound_rows_diagnostic', HERE/'annual_six_record_diagnostic.json'),
        ('map.build_execution', HERE/'map_build_execution.json'),
        ('map.numeric_verification_execution', HERE/'map_verification_execution.json'),
        ('map.source_metadata_regeneration_verification', HERE/'metadata_regeneration_verification.json'),
        ('map.final_layout_only_refresh', HERE/'final_layout_refresh.json'),
        ('map.caption_regression_verification', HERE/'trend_caption_regression_verification.json'),
        ('navigation.adoption_pointer_verification', HERE/'navigation_updates.json'),
        ('navigation.current_variant', C/'CURRENT_VARIANT.json'),
        ('navigation.master_models_index', REGION/'models/MASTER_INDEX.md'),
        ('navigation.report_index', REGION/'reports_index.md'),
        ('map.browser_observations', HERE/'browser_observations.json'),
        ('map.visible_map_screenshot', HERE/'browser_map.jpg'),
        ('map.visible_trends_screenshot', HERE/'browser_trends.jpg'),
        ('map.index_html', ROOT/'interactive_map/index.html'),
        ('map.trends_html', ROOT/'interactive_map/trends.html'),
        ('map.archive_html', ROOT/'interactive_map/archive/index.html'),
    ]: add(role,p)
    for p in HERE.glob('paper_file_roles.before_*.json'): add('source.file_roles_before',p)
    for p in HERE.glob('Project.before_registration_*.xlsx'): add('central.project_before',p)
    for p in HERE.glob('*.before_*'): add('navigation.previous_pointer_bytes',p,must=False)
    integration_roles = {
        'regional_adoption_verification.json':'regional.adoption',
        'carbon_unit_bridge.json':'regional.carbon_unit_bridge',
        'taxon_audit.json':'regional.exhaustive_taxon_audit',
        'taxonomy.csv':'regional.source_group_taxonomy',
        'mapping_verification.json':'regional.mapping_verification',
        'mapping_summary.json':'regional.mapping_summary',
        'matching_rows.json':'regional.exact_matching_rows',
        'allocation_ledger.json':'regional.allocation_assumptions',
        'allocation_search.json':'regional.allocation_source_search',
        'regional_science_verification.json':'regional.scientific_consequences',
        'source_link_fix_verification.json':'regional.source_link_regression_and_suite_limitations',
        'full_workflow_suite_20261003.log':'regional.broad_suite_log',
        'LME_052_before_GM2019_adoption.xlsx':'regional.before_adoption',
        'baseline_inventory.json':'regional.protected_baseline_inventory',
        'appendix_top_qa.png':'regional.appendix_top_visual_QA',
        'appendix_zero_and_unresolved_qa.png':'regional.appendix_zero_unresolved_visual_QA',
    }
    for name,role in integration_roles.items(): add(role,I/name)
    for p in I.glob('*.py'): add('regional.reproduction_code',p,must=False)
    for p in I.glob('*.log'):
        if p.name != 'full_workflow_suite_20261003.log': add('regional.retained_execution_log',p,must=False)
    for name in ['register_adopted_model.py','finalize_registry_spec.py','prepare_standard_project_update.py','verify_central_and_payload.py','independent_final_gate.py']:
        add('central.reproduction_code',HERE/name,must=False)
    add('map.final_layout_refresh_code',HERE/'refresh_final_layout.py')
    for name in ['original_atlas_data.py','build_html.py','verify_html.py','researcher_review.py','researcher_review.js']:
        add('map.current_production_code_identity',ROOT/'tools'/name)
    for name in ['project_update_execution.json','registry_before.json']:
        add('central.retained_execution_evidence',HERE/name,must=False)
    add('central.payload_verification_stdout',HERE/'central_payload_verification.stdout.log')
    for p in HERE.glob('*classic*.py'): add('central.classic_independent_reproduction_code',p,must=False)
    for p in HERE.glob('*caption*'):
        if p.is_file(): add('map.caption_regression_evidence',p,must=False)

    report_roles = {
        'report_inputs.json':'reports.inputs',
        'report_content_verification.json':'reports.complete_numeric_cell_verification',
        'document_structural_verification.json':'reports.manual_fields_and_relocated_link_verification',
        'inherited_manual_fields.json':'reports.inherited_manual_fields',
        'diagnostic_matrix_inspection.json':'reports.full_matrix_inspection',
        'visual_inspection.json':'reports.final_all_page_visual_QA',
        'map_alignment_confirmed.json':'reports.final_map_alignment',
        'evidence_index.json':'reports.final_package_inventory',
        'evidence_index_check.json':'reports.final_package_inventory_check',
        'geography/geography_assessment.json':'reports.source_geography_assessment',
        'geography/target_LME052_intended_whole_sea.png':'reports.target_geographic_figure',
        'geography/GM2019_Figure1_original_sampling.png':'reports.original_source_sampling_figure',
        'qa/validation/report.pdf':'reports.validation_final_rendered_PDF',
        'qa/departures/report.pdf':'reports.departures_final_rendered_PDF',
    }
    for name,role in report_roles.items(): add(role,E/name)
    for prefix in ['Model_validation','Article_departures']:
        add('reports.'+prefix+'_DOCX',REGION/(prefix+'_'+MODEL_ID+'.docx'))
    add('reports.original_researcher_document',REGION/'Model_validation_52_1_Sea_of_Okhotsk_NE_(1980).docx')
    add('reports.current_template',ROOT/'tools/templates/Model_validation_template.docx')
    add('reports.target_boundary',REGION/'validation_reports/52_1_Sea_of_Okhotsk_NE_(1980)/geography/target_LME052.geojson')
    for p in E.glob('*.py'): add('reports.reproduction_code',p,must=False)
    qa = optional(E/'visual_inspection.json')
    qa_fresh = bool(qa and qa.get('all_pages_inspected') is True)
    if qa:
        for report in qa.get('reports',[]):
            doc, pdf = ROOT/report['docx_path'], E/report['pdf_path']
            qa_fresh &= doc.is_file() and pdf.is_file() and sha(doc)==report['docx_sha256'] and sha(pdf)==report['pdf_sha256']
            pages=report['pages']
            qa_fresh &= [p['page'] for p in pages]==list(range(1,report['page_count']+1))
            for page in pages:
                p=E/page['image_path']
                add('reports.'+report['short_name']+'.reviewed_page_'+str(page['page']),p,expected=page['sha256'])
                qa_fresh &= p.is_file() and sha(p)==page['sha256'] and page.get('reviewed') is True
    report_package = optional(E/'evidence_index.json')
    report_cohort_matches = bool(report_package)
    if report_package:
        for item in report_package['artifacts']:
            if item['availability'] != 'present':
                report_cohort_matches = False
                continue
            p=(E/item['path']).resolve()
            report_cohort_matches &= p.is_file() and sha(p)==item['sha256']
            add('reports.package.'+item['role'],p,must=item['role'] in report_package['required_roles'],expected=item['sha256'])

    browser_path = args.browser_proof.resolve() if args.browser_proof else HERE/'browser_verification.json'
    add('map.final_visible_browser_verification',browser_path)
    browser=optional(browser_path)
    browser_ok=bool(browser and (browser.get('passed') is True or browser.get('all_checks_passed') is True)
                    and boolean_checks(browser) and browser.get('model_id')==MODEL_ID)
    if browser:
        browser_ok &= browser.get('project_sha256')==sha(ROOT/'Project.xlsx') and browser.get('regional_sha256')==sha(REGION/'LME_052.xlsx')
        browser_ok &= browser.get('map_sha256')==sha(ROOT/'interactive_map/index.html') and browser.get('trends_sha256')==sha(ROOT/'interactive_map/trends.html')

    checks = {}
    checks['exact_frozen_native_model'] = sha(A/'model.json')==MODEL_HASH
    checks['native_index_and_check_unchanged'] = sha(A/'evidence_index.json')==NATIVE_INDEX_HASH and sha(A/'evidence_completeness.json')==NATIVE_CHECK_HASH
    checks['all_152_native_artifacts_still_match_frozen_index'] = native_cohort_matches and len(native_index['artifacts'])==152
    checks['native_inventory_complete'] = native_check.get('complete') is True
    native_gate = read(A/'final_verification.json')
    checks['native_physical_gates_pass'] = native_gate.get('all_gates_pass') is True and boolean_checks(native_gate,'gates')
    checks['repeat_native_and_diagnostic_state_exactly_reproduced'] = read(A/'reload_consistency.json')['all_values_exactly_reproduced'] is True
    cases=read(A/'case_coverage.json')
    checks['all_eight_mandatory_cases_retained'] = len(cases)==8 and {c['F62'] for c in cases}=={.023,.025} and len({c['case'] for c in cases})==4
    case_checks=[]
    expected_cases={'figure_only':(False,False),'text_plus_figure_unrepaired':(True,False),
                    'reduced_figure_source_repairs':(True,True),'text_plus_figure_adopted':(True,True)}
    for case in cases:
        p=A/case['path'].replace('\\','/')
        result=read(p.parent/'native_reload_result.json')
        case_checks.append(p.is_file() and sha(p)==case['input_sha256'] and result['exact_input_sha256']==case['input_sha256']
                           and result['main_is_model_balanced']==case['main_balanced']
                           and (case['main_balanced'],case['physically_admissible'])==expected_cases[case['case']])
    checks['mandatory_case_identities_and_dispositions_reconcile'] = all(case_checks)
    checks['source_file_role_hash_guards_pass'] = role_guard and read(HERE/'paper_file_role_metadata_proof.json')['passed'] is True
    checks['native_full_matrix_reconciliations_pass'] = all(v is True for v in read(A/'diagnostics/reconciliation.json').values())
    with (A/'diagnostics/scoped_SPPR.csv').open(encoding='utf-8',newline='') as stream:
        scoped={(int(row['group_seq']),row['method']):row for row in csv.DictReader(stream)}
    scope_errors=[]
    matrix_checks=[]
    for method in ['GE','TE','With Egestion']:
        diagnostic=read(A/'diagnostics'/(method.replace(' ','_')+'_full_return.json'))
        matrix=diagnostic['SPPR'];columns=matrix['columns'];index=matrix['index']
        matrix_checks.append(diagnostic['model_sha256']==MODEL_HASH and len(index)==23 and len(set(index))==23
                             and columns==[23,22,1] and len(matrix['data'])==23
                             and all(len(row)==3 and all(math.isfinite(v) and v>=0 for v in row) for row in matrix['data']))
        for group,row in zip(index,matrix['data']):
            values=dict(zip(columns,row))
            for name,source_ids in [('all',[23,22,1]),('inner',[22,1]),('pp',[1])]:
                saved=float(scoped[group,method]['sppr_'+name]);recomputed=math.fsum(values[n] for n in source_ids)
                if abs(saved-recomputed)>1e-12+1e-15*abs(saved):
                    scope_errors.append(dict(group=group,method=method,scope=name,saved=saved,recomputed=recomputed))
    checks['actual_23_by_3_source_matrices_reopened_and_nonnegative'] = all(matrix_checks)
    checks['all_207_native_scope_sums_independently_reconcile'] = not scope_errors and len(scoped)==69
    bridge=read(I/'carbon_unit_bridge.json')
    bridge_errors=[]
    for row in bridge['rows']:
        factor=row['source_body_wet_per_carbon'];actual=row['regional_sppr_wet_equivalent_per_wet_catch']
        if factor is None:
            if actual is not None:bridge_errors.append(row)
        elif not math.isclose(actual,row['native_sppr_C_per_C_catch']*9/factor,rel_tol=1e-14,abs_tol=1e-12):bridge_errors.append(row)
        option={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}[row['method']]
        key='sppr_'+{'all':'all','inner':'inner','PP':'pp'}[row['scope']]
        if not math.isclose(row['native_sppr_C_per_C_catch'],float(scoped[row['group_id'],option][key]),rel_tol=1e-14,abs_tol=1e-12):
            bridge_errors.append({'reason':'native scoped coefficient mismatch','row':row})
    checks['all_207_carbon_unit_bridge_rows_recalculate'] = len(bridge['rows'])==23*3*3 and not bridge_errors and bridge['exact_model_sha256']==MODEL_HASH
    adoption=read(I/'regional_adoption_verification.json')
    checks['regional_adoption_gates_pass'] = boolean_checks(adoption)
    checks['regional_adopted_workbook_and_coefficients_current'] = sha(REGION/'LME_052.xlsx')==adoption['after_workbook_sha256'] and sha(A/'sppr_source.xlsx')==adoption['sppr_source_sha256']
    mapping=read(I/'mapping_verification.json')
    checks['regional_mapping_and_appendix_checks_pass'] = mapping['passed'] is True and boolean_checks(mapping)
    checks['regional_appendix_hash_current'] = sha(ROOT/mapping['appendix'])==mapping['appendix_sha256']
    source_link=read(I/'source_link_fix_verification.json')
    source_link_green=source_link['checks']['source_link_regression_green']
    source_link_red=source_link['checks']['source_link_regression_red']
    checks['targeted_source_link_regression_checks_pass'] = source_link_green['exit_code']==0 and not source_link_green['failures'] and source_link_red['exit_code']!=0 and source_link.get('protected_unchanged') is True
    checks['source_link_execution_code_and_protected_inputs_current'] = source_link['adapter_sha256']==sha(ROOT/'tools/original_atlas_data.py') and source_link['regression_fixture_sha256']==sha(ROOT/'tools/workflow_checks/test_model_source_paths.py') and all(sha(ROOT/p)==v for p,v in source_link['protected_after'].items())
    taxon_audit=read(I/'taxon_audit.json')
    checks['all_151_taxa_have_unique_exact_labels'] = len(taxon_audit)==151 and len({r['taxon'] for r in taxon_audit})==151
    suite_log=(I/'full_workflow_suite_20261003.log').read_text(encoding='utf-8')
    run=re.search(r'Ran (\d+) tests in ([\d.]+)s',suite_log);failure=re.search(r'FAILED \(failures=(\d+), errors=(\d+)\)',suite_log)
    checks['broad_suite_failure_limitation_honestly_retained'] = bool(run and failure)
    central=optional(HERE/'central_payload_verification.json')
    checks['central_and_map_identity_preservation_gates_pass'] = bool(central and central.get('passed') is True and boolean_checks(central))
    checks['central_and_regional_gate_hashes_current'] = bool(central and central['project_sha256']==sha(ROOT/'Project.xlsx') and central['regional_workbook_sha256']==sha(REGION/'LME_052.xlsx') and central['model_sha256']==MODEL_HASH)
    classic=optional(HERE/'independent_classic_verification.json')
    checks['central_classic_exception_independently_bounded'] = bool(classic and classic.get('passed') is True and boolean_checks(classic))
    checks['numeric_map_verification_executed_successfully'] = read(HERE/'map_verification_execution.json')['exit_code']==0
    independent=read(HERE/'independent_final_gate.json')
    checks['independent_actual_native_gate_passes'] = independent['all_checks_passed'] is True and independent['native_model_sha256']==MODEL_HASH
    # Reopen current embedded article metadata without invoking any calculator.
    sys.path.insert(0,str(ROOT/'tools'))
    from original_atlas_data import embedded
    mapdata,_=embedded(ROOT/'interactive_map/index.html','DB')
    article=next((a for a in mapdata['articles'] if a['article_id']=='OKH-GM2019__LME_052'),{})
    material={r['filename']:r for r in article.get('material_files',[])}
    checks['all_12_article_roles_applied_to_current_map_metadata'] = all(Path(r['path']).name in material and all(material[Path(r['path']).name].get(k)==r[k] for k in ['sha256','role','file_label']) for r in target_roles) and len(target_roles)==12
    checks['final_visible_browser_verification_passes'] = browser_ok
    metadata_regeneration=optional(HERE/'metadata_regeneration_verification.json')
    checks['source_metadata_regeneration_preserves_scientific_payload'] = bool(metadata_regeneration and metadata_regeneration.get('passed') is True and boolean_checks(metadata_regeneration))
    layout=optional(HERE/'final_layout_refresh.json')
    layout_ok=bool(layout and layout.get('passed') is True and boolean_checks(layout))
    if layout:
        layout_ok &= layout['protected_before']==layout['protected_after']
        layout_ok &= all(sha(ROOT/p)==value for p,value in layout['protected_after'].items())
        layout_ok &= layout['scientific_payload_hashes_before']==layout['scientific_payload_hashes_after']
        for name,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
            payload=embedded(ROOT/'interactive_map'/name,variable)[0]
            actual=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
            layout_ok &= actual==layout['scientific_payload_hashes_after'][name] and sha(ROOT/'interactive_map'/name)==layout['final_page_sha256'][name]
    checks['final_layout_refresh_preserves_all_scientific_payloads'] = layout_ok
    caption=optional(HERE/'trend_caption_regression_verification.json')
    checks['targeted_caption_regression_and_existing_checks_pass'] = bool(caption and caption.get('passed') is True and caption.get('regression_exit_code')==0
        and caption.get('frozen_templates_unchanged') is True and caption.get('science_workbooks_modified') is False
        and all(r['exit_code']==0 for r in caption['existing_checks']))
    navigation=optional(HERE/'navigation_updates.json')
    navigation_ok=bool(navigation and navigation.get('passed') is True and boolean_checks(navigation) and navigation.get('model_id')==MODEL_ID)
    if navigation:
        for record in navigation['files']:
            p=Path(record['path'])
            navigation_ok &= p.is_file() and p.resolve().is_relative_to(ROOT) and sha(p)==record['after_sha256'] and (HERE/record['backup']).is_file() and sha(HERE/record['backup'])==record['before_sha256']
    checks['navigation_pointers_and_before_bytes_reconcile'] = navigation_ok
    content=optional(E/'report_content_verification.json')
    content_ok=bool(content and content['exact_model_sha256']==MODEL_HASH and content['pending_map_alignment'] is False)
    if content:
        content_ok &= all(v is True for k,v in content.items() if k in ['all_448_native_input_changes_present_and_reconciled','all_74_food_components_present_and_reconciled','all_115_very_low_taxa_once','researcher_fields_undecided','same_input_all_three_retained_matrices'])
        content_ok &= all((REGION/name).is_file() and sha(REGION/name)==value for name,value in content['report_hashes'].items())
    checks['final_reports_content_and_hashes_reconcile'] = content_ok
    checks['every_final_report_page_visually_reviewed_and_hash_current'] = qa_fresh
    report_map=optional(E/'map_alignment_confirmed.json')
    checks['report_map_alignment_finalized'] = bool(report_map and report_map.get('alignment_passed') is True)
    report_index_check=optional(E/'evidence_index_check.json')
    checks['report_package_inventory_complete'] = bool(report_index_check and report_index_check.get('complete') is True and report_cohort_matches)

    stage_audit=dict(schema_version=1,timestamp_UTC=datetime.now(timezone.utc).isoformat(),model_id=MODEL_ID,
        native_model_sha256=MODEL_HASH,checks=checks,pending_or_failed_gates=[k for k,v in checks.items() if v is not True],
        broad_suite={'status':'FAILED', 'tests':int(run[1]) if run else None,'failures':int(failure[1]) if failure else None,'errors':int(failure[2]) if failure else None,
                    'evidence':rel(I/'full_workflow_suite_20261003.log'),'scope':'General workflow suite; not a scientific native run. The retained source-link regression evidence discusses failures; no blanket full-suite pass is claimed.'},
        unsupported_stages={'Monte_Carlo':'NOT_RUN: authorized adoption uses retained direct GE/TE/With Egestion only; no uncertainty ensemble is claimed.',
                            'global_PPR':'NOT_RUN: this regional workflow does not claim new global calculations.'},
        carbon_bridge={'rows':len(bridge['rows']),'formula':'regional = native carbon SPPR * 9 / body wet:C; wet catch * regional / 9 gives tC PPR','errors':bridge_errors},
        native_source_scope_arithmetic={'rows':207,'tolerance':'absolute 1e-12 + relative 1e-15','errors':scope_errors},
        scientific_limits={'researcher_validated':False,'production_eligible':False,'native_methods':'all WARN; zero model catch and terminal EE=0 retained',
                           'detritus':'374.4336835206025 million tC/year nonsteady residual under prescribed routing; not measured burial or validated stock trend',
                           'geography':'Source Figure1 is sampling stations, not an author GIS polygon; whole-sea proxy overlap is approximate',
                           'broad_suite':'6 failures and 15 errors retained, not falsely passed'},
        purpose='Overall handoff audit only; no model, workbook, map, frozen inventory or configuration was modified. Pending gates do not imply completion.')
    save(HERE/'overall_stage_audit.json',stage_audit)
    add('aggregate.stage_audit',HERE/'overall_stage_audit.json')
    add('aggregate.reproduction_code',Path(__file__))
    for role,reason in [('unrequested.Monte_Carlo','Direct-only authorized adoption; no Monte Carlo output claimed.'),('unrequested.global_calculation','Regional adoption; no new global calculation claimed.')]:
        artifacts.append(dict(role=role,availability='inapplicable',reason=reason,acquisition_status='not_run_outside_applicable_direct_regional_stages'))
    index=dict(schema_version=1,run_id='LME052-GM2019-BALANCED-COMPLETION-20261003',region_id='LME_052',model_id=MODEL_ID,variant_id='adopted_balanced_20261003',
        source_identity={'paper_id':'OKH-GM2019__LME_052',**native_index['source_identity']},
        computational_input_identity={'path':rel(A/'model.json'),'sha256':MODEL_HASH,'settings':rel(A/'runtime_settings.json'),'provenance':rel(A/'runtime_provenance.json')},
        methods=['Actual native LIM reload and physical checks','GE','TE','With Egestion','F62 .023/.025 mandatory cases','Eight EwE imports and actual admitted roundtrip','Taxon mapping and carbon-to-wet regional bridge','Central/map/trends adoption','Report numeric/manual-field/link/full-page checks'],
        required_roles=sorted(required),artifacts=artifacts,reconciliation=checks,
        limitations=stage_audit['scientific_limits'],stage_status=stage_audit['pending_or_failed_gates'],
        scope='Aggregate evidence integrity and declared stage reconciliation. This does not confer researcher approval, measured geographic overlap, ecological validation or a full broad-suite pass.')
    save(HERE/'overall_evidence_index.json',index)
    checker_path=ROOT/'tools/skills/original_skill_resources/combined-src/scripts/check_evidence.py'
    spec=importlib.util.spec_from_file_location('overall_evidence_checker',checker_path)
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result=checker.check(HERE/'overall_evidence_index.json')
    save(HERE/'overall_evidence_completeness.json',result)
    print(json.dumps({'complete':result['complete'],'verified_artifacts':len(result['verified_artifacts']),'missing_roles':result['missing_roles'],'errors':result['errors'],'pending_or_failed_gates':stage_audit['pending_or_failed_gates']},indent=2))
    raise SystemExit(0 if result['complete'] else 1)

if __name__=='__main__': main()
