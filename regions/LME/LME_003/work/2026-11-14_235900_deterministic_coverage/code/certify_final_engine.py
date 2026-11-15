"""Certify unchanged compared method call closures against final canonical bytes."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
WORK = Path(__file__).resolve().parents[1]
ENGINE = ROOT/'tools/scientific_code/PPREstimation'
PINNED = WORK/'inputs/current_engine_comparison'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


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
    nodes = {**{'method:'+name: node for name, node in methods.items()}, **{'function:'+name: node for name, node in functions.items()}}
    result = {}
    for name, node in nodes.items():
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute) and child.func.attr in methods: calls.add('method:'+child.func.attr)
                if isinstance(child.func, ast.Name) and child.func.id in functions: calls.add('function:'+child.func.id)
        result[name] = {'sha256': hashlib.sha256(ast.dump(StripDocstrings().visit(deepcopy(node)), include_attributes=False).encode()).hexdigest(), 'calls': calls}
    class StripBodies(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.body = [ast.Pass()]
            return node
    context = ast.dump(StripBodies().visit(tree), include_attributes=False)
    return result, hashlib.sha256(context.encode()).hexdigest()


def closure(graph_, target):
    found, pending = set(), ['method:'+target]
    while pending:
        node = pending.pop()
        if node in found: continue
        found.add(node)
        pending.extend(graph_.get(node, {}).get('calls', []))
    return found


inventory = read(WORK/'inputs/validated_inventory.json')
filenames = ['PPRCalculator.py', 'ModelData.py', 'utils.py']
final_bytes = {name: (ENGINE/name).read_bytes() for name in filenames}
hashes = {name: hashlib.sha256(data).hexdigest() for name, data in final_bytes.items()}
old, old_context = graph(PINNED/'PPRCalculator.py')
new, new_context = graph(ENGINE/'PPRCalculator.py')
dependencies_equal = all(sha(PINNED/name) == hashes[name] for name in filenames if name != 'PPRCalculator.py')
common = {'pinned_executed_engine_hashes': {name: sha(PINNED/name) for name in filenames},
          'final_canonical_engine_hashes': hashes,
          'nonfunction_module_context_equal': old_context == new_context,
          'supporting_module_bytes_equal': dependencies_equal,
          'interpretation': 'Exact normalized conservative transitive function/method AST comparison. An unchanged closure plus identical module context and dependencies extends the pinned numerical comparison to these final method bytes; it does not test a new constructor or untested changed methods.'}
summary = {**common, 'models': []}
for item in inventory['pairs']:
    output = ROOT/item['model_dir']/'results/diagnostics/engine_comparison_20261114'
    methods = {}
    for filename in ['comparison.json', 'additional_fast_comparison.json']:
        if (output/filename).exists(): methods.update(read(output/filename)['methods'])
    report = {**common, 'unit_id': item['unit_id'], 'model_id': item['model_id'], 'methods': {}}
    for key, result in methods.items():
        relevant = closure(old, result['settings']['target']) | closure(new, result['settings']['target'])
        changes = [node for node in sorted(relevant) if old.get(node, {}).get('sha256') != new.get(node, {}).get('sha256')]
        report['methods'][key] = {'unchanged_for_final_engine': not changes and old_context == new_context and dependencies_equal,
                                  'changed_reachable_functions': changes,
                                  'conservative_call_closure': sorted(relevant)}
    report['all_numerically_compared_methods_unchanged'] = all(row['unchanged_for_final_engine'] for row in report['methods'].values())
    for name, data in final_bytes.items():
        target = output/'final_engine_confirmation'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    save(output/'final_engine_call_closure_certification.json', report)
    summary['models'].append({'unit_id': item['unit_id'], 'model_id': item['model_id'],
                              'all_numerically_compared_methods_unchanged': report['all_numerically_compared_methods_unchanged'],
                              'method_count': len(methods),
                              'unverified_methods': [key for key, row in report['methods'].items() if not row['unchanged_for_final_engine']]})
if any(sha(ENGINE/name) != value for name, value in hashes.items()):
    raise ValueError('Canonical source changed during certification')
save(WORK/'outputs/engine_comparison_final_engine_certification.json', summary)
print(json.dumps({'final_engine_hashes': hashes, 'models': summary['models']}))
