"""Recompute both annual catch bases from saved coefficient comparisons only."""
import json
import compare_engines as c


def material(scopes):
    return any(value['years_over_10_percent'] or value['years_with_sign_change']
               or value['years_with_availability_change'] for value in scopes.values())


inventory = c.driver.read(c.WORK/'inputs/validated_inventory.json')
summary = {
    'schema_version': 2,
    'comparison_basis': 'Pinned archived versus pinned current calculator on identical completed runtime; no constructor, normalization, balancing or EE floor is rerun for current comparator',
    'catch_bases': ['catch', 'landings'],
    'review_exclusions': 'Researcher group names/IDs applied to original taxon allocation shares; omitted shares not redistributed',
    'material_difference_rule': 'More than 10% annual PPR on common catch support, zero-to-nonzero/sign change, or execution/numerical availability/support change',
    'scope_limit': 'Only listed numerically_compared_methods were executed. Exact unchanged scientific AST call closures are reported separately. Changed, untested methods remain unassessed numerically.',
    'models': [],
}
for item in inventory['pairs']:
    output = c.ROOT/item['model_dir']/'results/diagnostics/engine_comparison_20261114'
    cache_path = output/'group_catch_weights.json'
    cache = c.driver.read(cache_path)
    if cache.get('schema_version') != 2 or set(cache['bases']) != {'catch', 'landings'}:
        raise ValueError('Corrected catch-weight capture missing: '+item['unit_id'])
    for basis, value in cache['bases'].items():
        for name in value['context']['excluded_group_names']:
            if any(value['weights'][name]):
                raise ValueError('Researcher exclusion retains allocated catch: '+item['unit_id']+'/'+name)
    weights = {basis: {name: c.np.asarray(values) for name, values in entry['weights'].items()}
               for basis, entry in cache['bases'].items()}
    methods = {}
    report_paths = []
    current_hashes = None
    for filename in ['comparison.json', 'additional_fast_comparison.json']:
        report_path = output/filename
        if not report_path.exists():
            continue
        report = c.driver.read(report_path)
        if c.sha(c.ROOT/item['model_dir']/'model.json') != report['model_sha256']:
            raise ValueError('Canonical model changed: '+item['unit_id'])
        current_hashes = report['current_engine_hashes']
        report['catch_bases'] = ['catch', 'landings']
        report['regional_weighting_by_basis'] = {
            basis: {**entry['context'], 'group_catch_weights_reference': cache_path.relative_to(c.ROOT).as_posix(),
                    'group_catch_weights_sha256': c.sha(cache_path)}
            for basis, entry in cache['bases'].items()}
        report['regional_weighting'] = report['regional_weighting_by_basis']['catch']
        for method, result in report['methods'].items():
            old = c.driver.read(output/(method+'_old.json.gz'))
            current = c.driver.read(output/(method+'_current.json.gz'))
            by_basis = {basis: c.annual_comparison(old, current, weighting) for basis, weighting in weights.items()}
            result['scopes'] = by_basis['catch']
            result['landings_scopes'] = by_basis['landings']
            result['materially_different_by_basis'] = {basis: material(scopes) for basis, scopes in by_basis.items()}
            result['materially_different'] = old['status'] != current['status'] or any(result['materially_different_by_basis'].values())
            methods[method] = {
                'old_status': old['status'], 'current_status': current['status'],
                'materially_different': result['materially_different'],
                'materially_different_by_basis': result['materially_different_by_basis'],
                'old_matches_saved_coefficients': result.get('old_matches_saved_coefficients', {}),
                'bases': {basis: {
                    'all_sources_2019': scopes['all']['year_2019'],
                    'max_relative_annual_all_sources': scopes['all']['max_relative_annual_change_common'],
                    'max_relative_coefficient_all_sources': scopes['all']['max_relative_coefficient_change'],
                    'max_absolute_coefficient_all_sources': scopes['all']['max_absolute_coefficient_change'],
                    'changed_coefficient_groups': scopes['all']['coefficient_changes_over_10_percent_or_sign'],
                } for basis, scopes in by_basis.items()},
            }
        report['materially_different'] = any(value['materially_different'] for value in report['methods'].values())
        report['canonical_model_unchanged_after_comparison'] = True
        report['weighting_correction'] = 'Researcher excluded_group_ids values resolve as recorded group names or numeric runtime IDs; both bases recomputed from immutable saved method returns.'
        c.save(report_path, report)
        report_paths.append(report_path.relative_to(c.ROOT).as_posix())
    ast_path = output/'scientific_ast_comparison.json'
    ast = c.driver.read(ast_path) if ast_path.exists() else {'methods': {}}
    for key, value in ast['methods'].items():
        if key in methods:
            value['numeric_comparison'] = 'completed'
            value['materially_different'] = methods[key]['materially_different']
            value['old_execution_status'] = methods[key]['old_status']
            value['current_execution_status'] = methods[key]['current_status']
            value['all_sources_2019_by_basis'] = {basis: data['all_sources_2019'] for basis, data in methods[key]['bases'].items()}
            value['all_sources_2019'] = methods[key]['bases']['catch']['all_sources_2019']
            value['max_relative_annual_all_sources'] = methods[key]['bases']['catch']['max_relative_annual_all_sources']
    if ast_path.exists():
        ast['materially_different_methods'] = [key for key, value in methods.items() if value['materially_different']]
        c.save(ast_path, ast)
    summary['current_engine_hashes'] = current_hashes
    summary['models'].append({
        'unit_id': item['unit_id'], 'model_id': item['model_id'],
        'report_paths': report_paths,
        'numerically_compared_methods': list(methods),
        'code_equivalent_methods': [key for key, value in ast['methods'].items() if value['transitive_scientific_ast_equal']],
        'changed_not_numerically_compared': [key for key, value in ast['methods'].items() if not value['transitive_scientific_ast_equal'] and key not in methods],
        'methods': methods,
        'materially_different': any(value['materially_different'] for value in methods.values()),
        'materially_different_methods': [key for key, value in methods.items() if value['materially_different']],
        'excluded_group_names': cache['bases']['landings']['context']['excluded_group_names'],
    })
    print(item['unit_id']+' both catch bases finalized: '+str(len(methods))+' methods', flush=True)
summary['expected_pairs'] = len(inventory['pairs'])
summary['completed_pairs'] = len(summary['models'])
summary['total_numerical_method_pairs'] = sum(len(model['methods']) for model in summary['models'])
summary['materially_different_pairs'] = [model['unit_id'] for model in summary['models'] if model['materially_different']]
symbolic_path = c.WORK/'outputs/engine_comparison_symbolic_availability.json'
if symbolic_path.exists():
    symbolic = c.driver.read(symbolic_path)
    summary['symbolic_availability_evidence'] = symbolic_path.relative_to(c.ROOT).as_posix()
    summary['observed_symbolic_availability_repairs'] = [
        {'unit_id': model['unit_id'], 'model_id': model['model_id'],
         'methods': {key: {'exact_runtime_and_settings_equal': row.get('exact_encoded_runtime_before_equal') and row.get('exact_method_target_and_kwargs_equal'),
                           'annual_status': row.get('new_annual_status')}
                     for key, row in model['methods'].items() if row.get('numerical_output_became_available')}}
        for model in symbolic['models'] if model['availability_repaired_methods']]
    summary['other_symbolic_execution_failures'] = [
        {'unit_id': model['unit_id'], 'method': key, 'current_status': row['new_status'], 'current_reason': row.get('new_reason')}
        for model in symbolic['models'] for key, row in model['methods'].items() if row['new_status'] != 'ok']
    summary['flagged_pairs_including_observed_availability_repairs'] = sorted(set(summary['materially_different_pairs']) | {
        model['unit_id'] for model in symbolic['models'] if model['availability_repaired_methods']})
certificate_path = c.WORK/'outputs/engine_comparison_final_engine_certification.json'
if certificate_path.exists():
    summary['final_engine_certification_reference'] = certificate_path.relative_to(c.ROOT).as_posix()
stage_path = c.WORK/'outputs/engine_comparison_additional_summary.json'
if stage_path.exists():
    stage = c.driver.read(stage_path)
    for model in stage['models']:
        final = next(row for row in summary['models'] if row['unit_id'] == model['unit_id'] and row['model_id'] == model['model_id'])
        model['additional_numerically_compared_methods'] = [key for key in final['numerically_compared_methods'] if key not in c.METHODS]
        model['materially_different_methods'] = final['materially_different_methods']
    stage['finalized_both_bases_with_researcher_exclusions'] = True
    stage['authoritative_combined_summary'] = (c.WORK/'outputs/engine_comparison_summary.json').relative_to(c.ROOT).as_posix()
    c.save(stage_path, stage)
c.save(c.WORK/'outputs/engine_comparison_summary.json', summary)
print(json.dumps({key: summary[key] for key in ['completed_pairs', 'total_numerical_method_pairs', 'materially_different_pairs']}))
