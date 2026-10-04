"""Focused pre-export guard regressions; no canonical graph writes."""
import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools/knowledge_graph/provenance'))
from pipeline import assert_current_citations, assert_endpoints

checks = []
def rejected(name, function, *args):
    try: function(*args)
    except AssertionError:
        checks.append({'name': name, 'rejected': True})
    else: raise AssertionError('Guard accepted ' + name)

corpus = {'sha256': {'README.md': 'current', 'AGENTS.md': 'current2'}}
rejected('stale primary citation', assert_current_citations,
         [{'source_file': 'README.md', 'source_sha256': 'stale'}], corpus)
rejected('stale secondary citation', assert_current_citations,
         [{'source_file': 'README.md', 'source_sha256': 'current', 'source_evidence':
           [{'source_file': 'AGENTS.md', 'source_sha256': 'stale'}]}], corpus)
assert_current_citations([{'source_file': 'README.md', 'source_sha256': 'current', 'source_evidence':
                           [{'source_file': 'AGENTS.md', 'source_sha256': 'current2'}]}], corpus)
nodes = [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]
rejected('dangling edge', assert_endpoints, {'nodes': nodes, 'edges': [{'source': 'a', 'target': 'absent'}]})
rejected('dangling hyperedge', assert_endpoints, {'nodes': nodes, 'edges': [], 'hyperedges': [{'nodes': ['a', 'b', 'absent']}]})
rejected('short hyperedge', assert_endpoints, {'nodes': nodes, 'edges': [], 'hyperedges': [{'nodes': ['a', 'b', 'b']}]})
assert_endpoints({'nodes': nodes, 'edges': [{'source': 'a', 'target': 'b'}], 'hyperedges': [{'nodes': ['a', 'b', 'c']}]})
(RUN / 'qa/graph_guard_checks.json').write_text(json.dumps({'pass': True, 'negative_checks': checks,
        'valid_multi_source_and_hyperedge_cases': True, 'canonical_graph_writes': 0}, indent=2) + '\n', encoding='utf8')
print('Graph pre-export guards: 5 negative and 2 valid cases passed; no canonical writes.')
