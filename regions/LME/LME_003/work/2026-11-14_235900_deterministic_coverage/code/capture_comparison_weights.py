"""Freeze original allocation weights for both comparison catch bases."""
import json
from types import SimpleNamespace
import compare_engines as c

inventory = c.driver.read(c.WORK/'inputs/validated_inventory.json')
project = c.comparison_table(c.ROOT/'Project.xlsx', 'Models & coverage', 'Models')
reviews = {(row['unit_id'], row['model_id']): json.loads(row.get('researcher_review_summary') or '{}')
           for row in c.records(project, 'Models & coverage', 'Models')}
for item in inventory['pairs']:
    root = c.ROOT/item['model_dir']
    old = c.driver.read(root/'results/diagnostics/engine_comparison_20261114/new_GE_old.json.gz')
    canonical = c.driver.read(root/'model.json')
    names = {int(group['group_seq']): group['group_name'] for group in canonical['group']}
    all_names = dict.fromkeys(old['scopes']['all'])
    model = SimpleNamespace(seq2name=names,
                            name2seq={name: next((seq for seq, value in names.items() if value == name), None)
                                      for name in all_names})
    for basis in ['landings', 'catch']:
        c.catch_context(item, model, reviews[(item['unit_id'], item['model_id'])], basis)
    print(item['unit_id']+' both catch-weight bases captured', flush=True)
