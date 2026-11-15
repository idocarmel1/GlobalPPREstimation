"""Conservative method-call AST audit and bounded extra numerical comparisons."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_engines as comparison

ROOT, WORK, adapter = comparison.ROOT, comparison.WORK, comparison.adapter
EXCLUDED_NUMERICAL = {'EwE_TE_EE', 'EwE_TE_noEE', 'sym_TE_asPP', 'sym_TE_asDC', 'sym_GE_asPP',
                      'sym_GE_asDC', 'sym_WithEgestion_asPP', 'sym_WithEgestion_asDC'}


class StripDocstrings(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body = node.body[1:]
        return node


def graph(path):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    calculator = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'PPRCalculator')
    methods = {node.name: node for node in calculator.body if isinstance(node, ast.FunctionDef)}
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    nodes = {**{'method:'+name: node for name, node in methods.items()},
             **{'function:'+name: node for name, node in functions.items()}}
    result = {}
    for name, node in nodes.items():
        children = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute) and child.func.attr in methods:
                    children.add('method:'+child.func.attr)
                if isinstance(child.func, ast.Name) and child.func.id in functions:
                    children.add('function:'+child.func.id)
        normalized = ast.dump(StripDocstrings().visit(deepcopy(node)), include_attributes=False)
        result[name] = {'sha256': hashlib.sha256(normalized.encode()).hexdigest(), 'calls': children}
    return result


def closure(graph_, target):
    found, pending = set(), ['method:'+target]
    while pending:
        node = pending.pop()
        if node in found: continue
        found.add(node)
        pending.extend(graph_.get(node, {}).get('calls', []))
    return found


def main():
    inventory = comparison.driver.read(WORK/'inputs/validated_inventory.json')
    current, current_hashes, snapshot = comparison.pin_current_engine()
    current_graph = graph(snapshot/'PPRCalculator.py')
    project = comparison.comparison_table(ROOT/'Project.xlsx', 'Models & coverage', 'Models')
    reviews = {(row['unit_id'], row['model_id']): json.loads(row.get('researcher_review_summary') or '{}')
               for row in comparison.records(project, 'Models & coverage', 'Models')}
    summary = {'method_scope': inventory['canonical_non_mc_methods'], 'current_engine_hashes': current_hashes,
               'code_equivalence_scope': 'Exact normalized AST equality of conservative transitive class/global-function call closure, same utils bytes and same retained runtime. Constructor is outside this comparison.',
               'not_numerically_compared_by_this_extension': sorted(EXCLUDED_NUMERICAL), 'models': []}
    for item in inventory['pairs']:
        root = ROOT/item['model_dir']; output = root/'results/diagnostics/engine_comparison_20261114'
        try:
            flags = comparison.driver.replay_flags(item)
            path = adapter._calculation_engine_path(flags, root/'model.json')
            if path is None: path = adapter._engine_paths(flags, root/'model.json')['PPRCalculator.py']
            old_graph = graph(path)
            utils_equal = flags['engine_source_hashes']['utils.py'] == current_hashes['utils.py']
            evidence = {'unit_id': item['unit_id'], 'model_id': item['model_id'],
                        'old_calculator_path': path.relative_to(ROOT).as_posix(), 'old_calculator_sha256': comparison.sha(path),
                        'current_calculator_sha256': current_hashes['PPRCalculator.py'],
                        'utils_bytes_equal': utils_equal, 'methods': {}}
            pending = []
            for key in inventory['canonical_non_mc_methods']:
                settings = adapter.method_settings(key, flags, root/'model.json')
                relevant = closure(old_graph, settings['target']) | closure(current_graph, settings['target'])
                changes = [{'function': name, 'old_sha256': old_graph.get(name, {}).get('sha256'),
                            'current_sha256': current_graph.get(name, {}).get('sha256')}
                           for name in sorted(relevant) if old_graph.get(name, {}).get('sha256') != current_graph.get(name, {}).get('sha256')]
                same = not changes and utils_equal
                evidence['methods'][key] = {'target': settings['target'], 'settings': settings,
                                            'transitive_scientific_ast_equal': same,
                                            'conservative_call_closure': sorted(relevant), 'changed_functions': changes,
                                            'numeric_comparison': 'completed in base comparison' if key in comparison.METHODS else 'not executed'}
                if key not in comparison.METHODS and key not in EXCLUDED_NUMERICAL and not same:
                    pending.append(key)
            comparison.save(output/'scientific_ast_comparison.json', evidence)
            numeric_path = output/'additional_fast_comparison.json'
            numeric = comparison.driver.read(numeric_path) if numeric_path.exists() else {'methods': {}}
            if numeric.get('current_engine_hashes', current_hashes) != current_hashes:
                raise ValueError('Existing extra comparison uses different current engine')
            remaining = [key for key in pending if key not in numeric['methods']]
            if remaining:
                fresh = comparison.compare_pair(item, current, current_hashes, snapshot,
                                                  reviews[(item['unit_id'], item['model_id'])],
                                                  report_filename='additional_fast_remaining.json', methods=remaining)
                numeric = {**fresh, 'methods': {**numeric['methods'], **fresh['methods']}}
                numeric['method_scope'] = list(numeric['methods'])
                comparison.save(numeric_path, numeric)
            if numeric['methods']:
                for key, value in numeric['methods'].items():
                    evidence['methods'][key]['numeric_comparison'] = 'completed'
                    evidence['methods'][key]['materially_different'] = value['materially_different']
                    evidence['methods'][key]['old_execution_status'] = value['old_execution_status']
                    evidence['methods'][key]['current_execution_status'] = value['current_execution_status']
                    evidence['methods'][key]['all_sources_2019'] = value['scopes']['all']['year_2019']
                    evidence['methods'][key]['max_relative_annual_all_sources'] = value['scopes']['all']['max_relative_annual_change_common']
                comparison.save(output/'scientific_ast_comparison.json', evidence)
            evidence['materially_different_methods'] = [key for key, value in evidence['methods'].items() if value.get('materially_different')]
            summary['models'].append({'unit_id': item['unit_id'], 'model_id': item['model_id'],
                                      'materially_different_methods': evidence['materially_different_methods'],
                                      'additional_numerically_compared_methods': pending,
                                      'code_equivalent_methods': [key for key, value in evidence['methods'].items() if value['transitive_scientific_ast_equal']],
                                      'changed_not_numerically_compared': [key for key, value in evidence['methods'].items() if not value['transitive_scientific_ast_equal'] and value['numeric_comparison'] == 'not executed'],
                                      'evidence': (output/'scientific_ast_comparison.json').relative_to(ROOT).as_posix()})
            print(item['unit_id']+' AST+fast extension complete; material='+str(evidence['materially_different_methods']), flush=True)
        except Exception as exc:
            import traceback
            error = {'unit_id': item['unit_id'], 'model_id': item['model_id'], 'error': str(exc), 'traceback': traceback.format_exc()}
            comparison.save(output/'additional_comparison_error.json', error)
            summary['models'].append(error)
            print(item['unit_id']+' EXTENSION ERROR '+str(exc), flush=True)
        comparison.save(WORK/'outputs/engine_comparison_additional_summary.json', summary)


if __name__ == '__main__': main()
