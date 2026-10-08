"""Freeze the bounded current graph corpus and prepare native extraction tasks."""
import hashlib
import json
import math
import os
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
STAGE = BASE / 'work/graph_prepare/final_refresh'
STAGE.mkdir(parents=True, exist_ok=True)
os.environ['GRAPHIFY_OUT'] = str(STAGE)
from graphify.detect import classify_file, count_words
from graphify.cache import check_semantic_cache


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (STAGE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    plan_path = BASE / 'verification/knowledge_graph_refresh_plan.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    baseline = json.loads((ROOT / 'tools/knowledge_graph/source_hashes.json').read_text(encoding='utf-8-sig'))
    names = ['graph_evidence_merge.py', 'verify_integrated_regional_tables.py', 'verify_final_browser_observations.py',
             'verify_final_trends_outputs.js', 'verify_final_page_relocation.py', 'finalize_review_coordination.py']
    extras = [(BASE / n).relative_to(ROOT).as_posix() for n in names] + ['tools/original_html_layout/archive_layout.py']
    plan['proposed_new_sources'] = sorted(set(plan['proposed_new_sources']) | (set(extras) - set(baseline)))
    scope = sorted(set(baseline) | set(plan['proposed_new_sources']))
    missing = [s for s in scope if not (ROOT / s).is_file()]
    assert not missing, missing
    files = {}
    for rel in scope:
        kind = classify_file(ROOT / rel)
        assert kind is not None, rel
        files.setdefault(kind.value, []).append(str(ROOT / rel))
    words = sum(count_words(ROOT / f) for f in scope)
    assert len(scope) <= 500 and words <= 2_000_000
    hashes = {f: sha(ROOT / f) for f in scope}
    changed = [f for f in scope if baseline.get(f) != hashes[f]]
    new_files = {k: [f for f in fs if Path(f).relative_to(ROOT).as_posix() in changed] for k,fs in files.items()}
    for src, dest in [('graph.json','baseline.graph.json'),('source_hashes.json','baseline.source_hashes.json')]:
        shutil.copyfile(ROOT / 'tools/knowledge_graph' / src, STAGE / dest)
    save('frozen.source_hashes.json', hashes)
    save('detection.json', {'files':files,'new_files':new_files,'total_files':len(scope),'total_words':words,'changed_sources':changed,'deleted_sources':[]})
    noncode = [f for k, fs in new_files.items() if k != 'code' for f in fs]
    nodes, edges, hypers, uncached = check_semantic_cache(noncode, root=ROOT)
    # No exact-byte acceptance companion exists for this first final refresh.
    # Even a cache hit cannot establish YAML-frontmatter freshness on its own.
    save('cache_check.json', {'checked_files':len(noncode),'reported_uncached':len(uncached),
         'reported_cached_nodes':len(nodes),'reported_cached_edges':len(edges),'reported_cached_hyperedges':len(hypers),
         'exact_byte_accepted_hits':0,'disposition':'All changed non-code sources require extraction because no matching full-byte provenance acceptance ledger exists.'})
    count = math.ceil(len(noncode) / 23)
    chunks = [noncode[i*23:(i+1)*23] for i in range(count)]
    for i, paths in enumerate(chunks, 1):
        save(f'chunk_{i:02d}_sources.json', [{'path':Path(p).relative_to(ROOT).as_posix(),'sha256':hashes[Path(p).relative_to(ROOT).as_posix()]} for p in paths])
    # Literal allowlist, with parent traversal re-enabled only where needed.
    dirs = set()
    for f in scope:
        p = Path(f).parent
        while str(p) != '.':
            dirs.add(p.as_posix())
            p = p.parent
    lines = ['# Current architecture, scientific evidence and all23 review records.', '# Exact corpus: tools/knowledge_graph/source_hashes.json', '/*']
    for d in sorted(dirs, key=lambda s:(s.count('/'), s)):
        lines += ['!/' + d + '/', '/' + d + '/*']
    lines += ['!/' + f for f in scope]
    (ROOT / '.graphifyignore').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    plan['status'] = 'Final source bytes frozen; AST and native semantic extraction pending.'
    plan['final_source_count'] = len(scope)
    plan['final_word_count'] = words
    plan['current_changed_sources'] = changed
    plan['current_missing_sources'] = []
    plan_path.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    save('freeze_identity.json', {'baseline_graph_sha256':sha(STAGE/'baseline.graph.json'),'baseline_sources_sha256':sha(STAGE/'baseline.source_hashes.json'),'frozen_sources_sha256':sha(STAGE/'frozen.source_hashes.json'),'scope_count':len(scope),'word_count':words,'changed_count':len(changed),'semantic_files':len(noncode),'chunks':len(chunks),'token_usage':None,'cost':None})
    print(json.dumps({'files':len(scope),'words':words,'changed':len(changed),'kinds':{k:len(v) for k,v in files.items()},'changed_kinds':{k:len(v) for k,v in new_files.items()},'semantic_chunks':[len(c) for c in chunks]}))


if __name__ == '__main__':
    main()
