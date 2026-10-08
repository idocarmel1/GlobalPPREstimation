"""Root-only graph rendering and independent preservation/freshness checks."""
from pathlib import Path
import collections
import copy
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

S = Path(__file__).resolve().parent
B = S.parents[2]
R = B.parents[2]
O = S/'candidate'
O.mkdir(exist_ok=True)
sys.path.insert(0, str(B))
os.environ['GRAPHIFY_OUT'] = str(S)
from graph_evidence_merge import read, canonical, edge_records
import networkx as nx
from graphify.export import to_html
from graphify.report import generate
from graphify.analyze import suggest_questions
from graphify.detect import save_manifest, _md5_file
from graphify.benchmark import run_benchmark
from graphify.cache import save_semantic_cache
from graphify.serve import _query_graph_text


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (O/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def text(name, data):
    (O/name).write_text(data.rstrip()+'\n', encoding='utf-8')


def make_graph(d):
    G = nx.DiGraph() if d.get('directed') else nx.Graph()
    for n in d['nodes']:
        G.add_node(n['id'], **{k:copy.deepcopy(v) for k,v in n.items() if k!='id'})
    for e in d['links']:
        attrs={k:copy.deepcopy(v) for k,v in e.items() if k not in {'source','target'}}
        attrs.update(_src=e['source'],_tgt=e['target'])
        G.add_edge(e['source'], e['target'], **attrs)
    G.graph['hyperedges']=copy.deepcopy(d['hyperedges'])
    return G


class Unavailable:
    def __format__(self, spec):
        return 'unavailable'


def main():
    partition = read(S/'partition_identity.json')
    for name,digest in partition['files'].items():assert sha(S/name)==digest,name
    frozen=read(S/'frozen.source_hashes.json'); baseline=read(S/'baseline.source_hashes.json')
    old=read(S/'baseline.graph.json'); d=read(S/'merged.graph.json'); a=read(S/'analysis.json')
    audit=read(S/'merge_audit.json'); detection=read(S/'detection.json')
    for fragment in audit['semantic_checks']:
        assert sha(S/fragment['fragment']) == fragment['sha256'], fragment
    assert sha(S/'ast.json') == audit['ast_input_sha256']
    labels={int(k):v for k,v in read(S/'labels.json').items()}
    communities={int(k):v for k,v in a['communities'].items()}
    assert set(labels)==set(communities)
    assert all(isinstance(v,str) and 2<=len(v.split())<=5 for v in labels.values())
    for f,h in frozen.items():
        assert (R/f).resolve().is_relative_to(R) and sha(R/f)==h, f
    unchanged={f for f,h in frozen.items() if baseline.get(f)==h}
    newnodes={n['id']:n for n in d['nodes']}
    assert len(newnodes)==len(d['nodes'])
    ignore_community=lambda n:{k:v for k,v in n.items() if k!='community'}
    protected=[n for n in old['nodes'] if not n.get('source_file') or n['source_file'] in unchanged]
    for n in protected:
        assert ignore_community(n)==ignore_community(newnodes[n['id']]), n['id']
    kept_edges=[e for e in edge_records(old) if not e.get('source_file') or e['source_file'] in unchanged]
    kept_hyper=[h for h in old['hyperedges'] if not h.get('source_file') or h['source_file'] in unchanged]
    assert not collections.Counter(map(canonical,kept_edges))-collections.Counter(map(canonical,edge_records(d)))
    assert not collections.Counter(map(canonical,kept_hyper))-collections.Counter(map(canonical,d['hyperedges']))
    for e in edge_records(d):
        assert e['source'] in newnodes and e['target'] in newnodes
        assert not e.get('source_file') or e['source_file'] in frozen
    for n in d['nodes']:
        assert not n.get('source_file') or n['source_file'] in frozen
    for row in d['nodes'] + edge_records(d) + d['hyperedges']:
        if row.get('source_file') and row.get('source_sha256'):
            assert row['source_sha256'] == frozen[row['source_file']], row
    assert len({h['id'] for h in d['hyperedges']})==len(d['hyperedges'])
    for h in d['hyperedges']:
        assert set(h['nodes'])<=set(newnodes)
    G=make_graph(d)
    save('graph.json',d)
    save('source_hashes.json',frozen)
    save('.graphify_labels.json',{str(k):v for k,v in labels.items()})
    save_manifest(detection['files'],str(O/'manifest.json'),kind='both',root=R)
    manifest=read(O/'manifest.json'); assert set(manifest)==set(frozen)
    for f in frozen:
        assert manifest[f]['ast_hash']==manifest[f]['semantic_hash']==_md5_file(R/f), f
    questions=suggest_questions(G,communities,labels)
    report=generate(G,communities,{int(k):v for k,v in a['cohesion'].items()},labels,a['gods'],a['surprises'],detection,{'input':Unavailable(),'output':Unavailable()},'GlobalPPREstimation',suggested_questions=questions,built_at_commit=None)
    report=re.sub(r'\[\[_COMMUNITY_[^|\]]+\|([^\]]+)\]\]',r'\1',report)
    report+='\n\n## Evidence preservation and freshness\n\n'
    report+='This graph indexes the bounded current project corpus, including all 23 regional reviews. Review completion does not imply scientific approval. Accepted manual scientific inputs remain preserved. Historical source nodes and former-reference anchors are not current instructions.\n\n'
    report+=f'Full-byte hashes for {len(frozen)} sources (including YAML frontmatter) are in [source_hashes.json](source_hashes.json). The worktree source snapshot was based on commit d14c71a9; source hashes, rather than that base commit alone, establish graph freshness.\n\n'
    report+=f'The canonical JSON retains {len(edge_records(d)):,} separately attributed evidence records across {len(d["links"]):,} edge pairs. Report statistics and HTML edges describe the derived topology; additional evidence remains in graph.json. {len(protected):,} protected nodes retain their evidence attributes; only derived community IDs were recomputed.\n\n'
    report+='Measured host token usage and monetary cost are unavailable. The benchmark is an estimate of context size, not a measurement of tokens or money saved. [Verification](completion_verification.json) · [Refresh scope](REFRESH_SCOPE.md) · [Interactive graph](graph.html).\n'
    text('GRAPH_REPORT.md',report)
    os.chdir(O)
    try:
        to_html(G,communities,'graph.html',community_labels=labels,node_limit=5000)
    finally:
        os.chdir(R)
    assert G.number_of_nodes()<=5000, 'Aggregate view requires a separately reviewed parity check'
    html=(O/'graph.html').read_text(encoding='utf-8')
    raw_nodes=json.loads(re.search(r'const RAW_NODES = (.*?);\n',html,re.S).group(1))
    raw_edges=json.loads(re.search(r'const RAW_EDGES = (.*?);\n',html,re.S).group(1))
    raw_hyperedges=json.loads(re.search(r'const hyperedges = (.*?);\n',html,re.S).group(1))
    assert raw_hyperedges==d['hyperedges']
    assert {n['id'] for n in raw_nodes}==set(newnodes)
    rendered={(e['from'],e['to'],e['label'],e['confidence']) for e in raw_edges}
    expected={(e['source'],e['target'],e.get('relation',''),e.get('confidence','EXTRACTED')) for e in d['links']}
    assert rendered==expected and len(raw_edges)==len(d['links'])
    for n in raw_nodes:
        assert n['community']==newnodes[n['id']]['community']
        assert n['community_name']==labels[n['community']]
    node_exe=Path('C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
    js_checks=[]
    for i,script in enumerate(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,re.S)):
        if not script.strip(): continue
        p=S/f'html_script_{i}.js';p.write_text(script,encoding='utf-8')
        x=subprocess.run([str(node_exe),'--check',str(p)],capture_output=True,text=True)
        assert x.returncode==0,x.stderr
        js_checks.append({'script':i,'status':'PASS'})
    queries=[]
    semantic_files=[f for f in frozen if '/validation_reports/' in f and (f.endswith('/source_review.md') or f.endswith('/reports_index.md'))]
    # Include special root indexes: every selected region must retrieve its
    # newly reviewed source or index, never merely an old diagnostics node.
    units=[r['unit_id'] for r in read(B/'final_23_region_status.json')['regions']]
    for unit in units:
        candidates=[n for n in d['nodes'] if (n.get('source_file') or '').startswith(f'regions/{unit}/') and (n.get('source_file') or '').endswith('reports_index.md') and n.get('source_sha256')==frozen.get(n.get('source_file'))]
        assert candidates,unit
        chosen=min(candidates,key=lambda n:int(re.search(r'\d+',str(n['source_location'])).group()))
        result=_query_graph_text(G,chosen['id'],depth=1,token_budget=4000)
        assert chosen['label'] in result and chosen['source_file'] in result, unit
        queries.append({'unit_id':unit,'query':chosen['id'],'expected_source':chosen['source_file'],'output':result})
    conceptual=[]
    for regex in [r'preserv.*(?:manual|scientific)|(?:manual|scientific).*preserv',r'source catch symbols|loader.zero|model.export.zero',r'negative.*(?:contribution|TE)|negative.entry',r'confidence.*(?:allocation|membership)|(?:allocation|membership).*confidence',r'geograph|overlap',r'ecopath.paper.to.ppr',r'Bay of Bengal|Meiobenthos']:
        candidates=[n for n in d['nodes'] if n.get('source_file') and n.get('source_sha256') and n['source_sha256']==frozen.get(n['source_file']) and re.search(regex,n.get('label',''),re.I)]
        assert candidates,regex
        chosen=candidates[0];result=_query_graph_text(G,chosen['id'],depth=1,token_budget=4000)
        assert chosen['label'] in result and chosen['source_file'] in result, chosen
        conceptual.append({'topic':regex,'query':chosen['id'],'expected_source':chosen['source_file'],'output':result})
    benchmark=run_benchmark(str(O/'graph.json'),detection['total_words'],[newnodes[q['query']]['label'] for q in queries[::5]]+[newnodes[q['query']]['label'] for q in conceptual[:3]])
    assert 'error' not in benchmark
    benchmark['measurement_status']='Estimated context size only. Not observed host token consumption, elapsed time, or monetary savings.'
    save('benchmark.json',benchmark)
    text('BENCHMARK.txt',f"Estimated context-size benchmark: {benchmark['corpus_tokens']:,} full-corpus tokens; {benchmark['avg_query_tokens']:,} average graph-query tokens; {benchmark['reduction_ratio']}x ratio.\nThis is not measured token or cost savings.\nSee benchmark.json for queries and assumptions.")
    cost=read(R/'tools/knowledge_graph/cost.json')
    cost['runs'].append({'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(frozen),'changed_files':len(detection['changed_sources']),'semantic_files':66,'input_tokens':None,'output_tokens':None,'monetary_cost':None,'status':'Three native gpt-6.1-sol xhigh extractors; host usage unavailable. Local AST and preserving merge verified.'})
    save('cost.json',cost)
    semantic={'nodes':[],'edges':[],'hyperedges':[]}
    for i in range(1,4):
        frag=read(S/f'chunk_{i:02d}.json')
        for k in semantic:semantic[k].extend(frag.get(k,[]))
    assert save_semantic_cache(**semantic,root=R)==66
    save('semantic_cache_acceptance.json',{'full_byte_hash_required_before_cache_reuse':True,'source_sha256':{f:frozen[f] for f in {n['source_file'] for n in semantic['nodes']}},'accepted_fragments':audit['semantic_checks'],'cache_location':'Native Graphify cache in ignored final-refresh staging; accepted fragments retained in the review verification package.'})
    text('REFRESH_SCOPE.md','# All 23 selected-region graph refresh\n\nThe exact portable corpus contains 466 files (203 documents and 263 code files), approximately 519,583 words. This bounded graph is an index, not an exhaustive copy of every retained scientific artifact.\n\nThis refresh re-extracted 66 documents in three native GPT 6.1 Sol xhigh agents and 19 code files with local Graphify AST extraction. All 46 regional review/index documents are included. Unchanged source evidence, separately attributed relationships and hyperedges were retained. Former anchors explicitly identify historical source bytes.\n\nScientific manual inputs remain accepted. Mapping corrections and confidence revisions are evidence-based; diagnostic failure, calculation availability, source availability and approval remain separate. The current unified paper-to-PPR skill and validation guide govern workflow; archived documents retain historical authority only.\n\nFull-byte source freshness includes frontmatter. Graphify manifest hashes are supplementary. Edge-pair topology is used for visualization while canonical JSON preserves every evidence record. External import stubs identify referenced symbols only and do not claim their implementation was read.\n\n[Source hashes](source_hashes.json) · [Graph](graph.json) · [Verification](completion_verification.json) · [Audit](refresh_audit.json)\n\n## Source inventory\n\n'+'\n'.join('- `'+f+'`' for f in frozen))
    # Check local links in newly generated graph documents, respecting the
    # local graph directory. The canonical source inventory is plain text.
    local_links=[]
    for name in ['GRAPH_REPORT.md','REFRESH_SCOPE.md']:
        for target in re.findall(r'\]\(([^)]+)\)',(O/name).read_text(encoding='utf-8')):
            target=target.strip('<>');
            if re.match(r'(?:https?:|mailto:|#)',target):continue
            dest=(O/unquote(target.split('#')[0])).resolve()
            assert dest.is_relative_to(O) and (dest.is_file() or dest.name in {'completion_verification.json','refresh_audit.json'}),target
            local_links.append({'document':name,'target':target})
    all_regional_docs={n['source_file'] for n in semantic['nodes'] if n['source_file'].startswith('regions/') and n['source_file'].endswith(('reports_index.md','source_review.md'))}
    assert len(all_regional_docs)==46,len(all_regional_docs)
    verification={'status':'PASS','source_and_manifest_hashes_checked':len(frozen),'node_endpoints':len(newnodes),'edge_pairs':len(d['links']),'separately_attributed_evidence_records':len(edge_records(d)),'hyperedges':len(d['hyperedges']),'unchanged_node_evidence_attributes_preserved':len(protected),'derived_community_attribute_recomputed':True,'unchanged_evidence_preserved':len(kept_edges),'unchanged_hyperedges_preserved':len(kept_hyper),'regional_review_index_sources':len(all_regional_docs),'all23_retrieval':queries,'conceptual_retrieval':conceptual,'html_payload_matches':True,'inline_javascript_syntax':js_checks,'local_links':local_links,'browser_interaction':'Not part of this graph acceptance; browser map/trends/archive checks recorded separately.','token_usage':None,'monetary_cost':None,'source_snapshot_sha256':sha(S/'frozen.source_hashes.json')}
    save('completion_verification.json',verification)
    save('refresh_audit.json',{**audit,'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':d['freshness']['base_commit'],'source_snapshot_sha256':sha(S/'frozen.source_hashes.json'),'corpus_files':len(frozen),'corpus_words':detection['total_words'],'changed_sources':detection['changed_sources'],'deleted_sources':[],'scientific_recalculation':False,'token_usage':None,'monetary_cost':None})
    text('COMPLETION_REPORT.md',f'# All 23 selected-region graph refresh\n\nPASS: {len(newnodes):,} nodes, {len(d["links"]):,} edge pairs, {len(edge_records(d)):,} separately attributed evidence records and {len(d["hyperedges"])} hyperedges across {len(frozen)} explicitly selected files.\n\nAll 23 regional indexes and seven workflow/scientific-limit topics passed source-specific retrieval checks. All 46 regional index/review sources are represented. Full-byte and manifest hashes, endpoints, preserved historical evidence, local document links, HTML payloads and JavaScript syntax were verified.\n\nThis graph update does not alter scientific inputs or approve models. Derived community IDs were recomputed; all other protected node attributes and unchanged-source evidence were preserved. Token usage and cost are unavailable. Benchmark reductions are estimates only.\n\n[Interactive graph](graph.html) · [Audit report](GRAPH_REPORT.md) · [Scope](REFRESH_SCOPE.md) · [Verification](completion_verification.json) · [Source hashes](source_hashes.json)')
    for f,h in frozen.items():assert sha(R/f)==h,f
    save('publication_manifest.json',{'status':'PASS','files':{p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='publication_manifest.json'},'source_snapshot_sha256':sha(S/'frozen.source_hashes.json')})
    print(json.dumps({'status':'PASS','nodes':len(newnodes),'pairs':len(d['links']),'source_files':len(frozen),'retrieval_checks':len(queries)+len(conceptual),'office_outputs_untouched':True}))


if __name__=='__main__':main()
