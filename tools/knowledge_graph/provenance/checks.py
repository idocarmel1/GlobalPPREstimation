"""Focused retrieval/JavaScript checks of the exported canonical graph."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from pipeline import ROOT,GRAPH,PROV,RUN,load,save,sha,now,assert_sources

def template_hash(html, include_hyperedges=True):
    masked=html
    def data_only(match):
        value=json.loads(match.group(2))
        assert isinstance(value,list),'Native graph binding is not a JSON array'
        return match.group(1)+'PAYLOAD'+match.group(3)
    for name,next_name in [('RAW_NODES','RAW_EDGES'),('RAW_EDGES','LEGEND')]:
        masked,count=re.subn(r'(const '+name+r' = )(\[.*?\])(;\nconst '+next_name+r' = )',data_only,masked,count=1,flags=re.S)
        assert count==1,name
    masked,count=re.subn(r'(const LEGEND = )(\[.*?\])(;\n)',data_only,masked,count=1,flags=re.S)
    assert count==1
    masked,count=re.subn(r'(<div id="stats">)\d+ nodes &middot; \d+ edges &middot; \d+ communities(</div>)',r'\1GRAPH_COUNTS\2',masked,count=1)
    assert count==1
    if include_hyperedges:
        masked,count=re.subn(r'(const hyperedges = )(\[.*?\])(;\n// afterDrawing)',data_only,masked,count=1,flags=re.S)
        assert count==1,'Unexpected native hyperedge data binding'
    return hashlib.sha256(masked.encode('utf8')).hexdigest()

def browser_template_baseline():
    proof=load(PROV/'browser_verification.json')
    assert proof['html_sha256']==sha(GRAPH/'graph.html'),'Browser-tested artifact already changed'
    save(PROV/'browser_template_baseline.json',{'checked_at':now(),'browser_tested_html_sha256':proof['html_sha256'],'browser_tested_graph_sha256':proof['graph_sha256'],'template_sha256':template_hash((GRAPH/'graph.html').read_text('utf8')),'masking':'Only native RAW_NODES, RAW_EDGES, LEGEND and hyperedges JSON payloads and graph-count footer are replaced. All HTML, CSS, JavaScript functions and dependency tags remain in the template hash.'})
    print('Exact browser-tested HTML script/template baseline retained')

def browser_template_payload_baseline():
    """Recover the exact prior tested artifact to include its fourth data binding."""
    baseline=load(PROV/'browser_template_baseline.json')
    proof=load(PROV/'browser_verification.json')
    tested=subprocess.check_output(['git','show','768dffbe:tools/knowledge_graph/graph.html'],cwd=ROOT)
    assert hashlib.sha256(tested).hexdigest()==proof['html_sha256']==baseline['browser_tested_html_sha256']
    html=tested.decode('utf8').replace('\r\n','\n')
    prior_three=baseline.get('prior_three_payload_template_sha256',baseline['template_sha256'])
    assert template_hash(html,include_hyperedges=False)==prior_three
    if 'prior_three_payload_template_sha256' in baseline:
        assert template_hash(html)==baseline['template_sha256']
    baseline.update({'checked_at':now(),'prior_three_payload_template_sha256':prior_three,
                     'template_sha256':template_hash(html),'tested_artifact_recovered_from':'768dffbe:tools/knowledge_graph/graph.html',
                     'tested_artifact_full_sha256_matches_actual_browser_proof':True,
                     'masked_bindings_validated_as_strict_json_arrays':True,'masked_footer_validated_as_plain_count_markup':True,
                     'masking':'Only native RAW_NODES, RAW_EDGES, LEGEND and hyperedges JSON payloads and graph-count footer are replaced. All HTML, CSS, JavaScript functions and dependency tags remain in the template hash.',
                     'reason':'The native hyperedges JSON is graph data; the prior three-payload mask left that data binding unmasked. Recovery checks the exact previously browser-tested full artifact before adjusting the data-only mask.'})
    save(PROV/'browser_template_baseline.json',baseline)
    print('Exact prior tested artifact recovered; all four native JSON data bindings masked')

def browser_delta():
    baseline=load(PROV/'browser_template_baseline.json')
    current=template_hash((GRAPH/'graph.html').read_text('utf8'))
    assert current==baseline['template_sha256'],'HTML script/template changed; actual browser retest required'
    static=load(PROV/'html_static_verification.json')
    assert static['pass'] and static['html_sha256']==sha(GRAPH/'graph.html')
    graph=load(GRAPH/'graph.json')
    assert static['hyperedge_payload_matches_json']
    assert static['legend_payload_matches_json'] and static['stats_plain_counts_match_json']
    save(PROV/'html_delta_verification.json',{'checked_at':now(),'pass':True,'current_html_sha256':sha(GRAPH/'graph.html'),'current_graph_sha256':sha(GRAPH/'graph.json'),'browser_tested_html_sha256':baseline['browser_tested_html_sha256'],'template_sha256':current,'script_template_unchanged':True,'current_payload_syntax_endpoint_id_checks':True,'current_hyperedge_payload_matches_json':True,'current_nodes':len(graph['nodes']),'current_pairs':len(graph['links']),'current_communities':len(graph['communities']),'limitation':'Actual full browser interaction is preserved against the initial tested artifact. The bounded current-source delta changed only verified JSON data/legend/count payloads; no new browser interaction or current-HTML screenshot is invented.'})
    print('Bounded HTML data delta PASS: exact tested script/template unchanged; current static payload verified')

def syntax():
    html=(GRAPH/'graph.html').read_text('utf8')
    scripts=re.findall(r'<script\b[^>]*>(.*?)</script>',html,re.S|re.I)
    script=RUN/'html_inline.js'
    script.write_text('\n'.join(scripts),encoding='utf8')
    node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    result=subprocess.run([str(node),'--check',str(script)],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
    assert result.returncode==0,result.stderr
    graph=load(GRAPH/'graph.json')
    matches=re.search(r'const RAW_NODES = (\[.*?\]);\nconst RAW_EDGES = (\[.*?\]);\nconst LEGEND = ',html,re.S)
    assert matches,'Unexpected installed HTML payload format'
    nodes=json.loads(matches.group(1));edges=json.loads(matches.group(2))
    ids={n['id'] for n in nodes}
    assert ids=={n['id'] for n in graph['nodes']}
    assert len(edges)==len(graph['links'])
    assert all(e['from'] in ids and e['to'] in ids for e in edges)
    assert all('historical' in n and 'source_location' in n for n in nodes)
    match=re.search(r'const hyperedges = (\[.*?\]);\n// afterDrawing',html,re.S)
    assert match,'Unexpected installed hyperedge payload format'
    hyperedges=json.loads(match.group(1))
    assert hyperedges==graph.get('hyperedges',[]),'HTML hyperedge data differs from graph JSON'
    legend=json.loads(re.search(r'const LEGEND = (\[.*?\]);\n',html,re.S).group(1))
    assert len(legend)==len(graph['communities'])
    assert {str(item['cid']) for item in legend}==set(graph['communities'])
    for item in legend:
        community=graph['communities'][str(item['cid'])]
        assert item['label']==community['label'] and item['count']==len(community['members'])
    assert f'<div id="stats">{len(nodes)} nodes &middot; {len(edges)} edges &middot; {len(legend)} communities</div>' in html
    assert 'onclick="focusNode(${esc(JSON.stringify(nid))})"' in html
    save(PROV/'html_static_verification.json',{'checked_at':now(),'pass':True,'html_sha256':sha(GRAPH/'graph.html'),'node_syntax_check':True,'payload_node_ids_match_json':True,'payload_edge_count_matches_json':True,'all_payload_endpoints_valid':True,'hyperedge_payload_matches_json':True,'legend_payload_matches_json':True,'stats_plain_counts_match_json':True,'historical_and_source_attributes_present':True,'neighbor_attribute_id_encoding':True,'browser_interaction':'Separately required; static syntax validation does not establish interactive behavior.'})
    print(f'HTML syntax and exact payload: {len(nodes)} nodes, {len(edges)} pairs')

def probes():
    assert_sources()
    cli=Path.home()/'miniconda3/Scripts/graphify.exe'
    prior=PROV/'retrieval_verification.json'
    previous=load(prior) if prior.is_file() else {}
    initial=previous.get('initial_attempts',[])
    if not initial and previous.get('probes'):
        for entry in previous['probes']:
            original=PROV/entry['output_file'];target=PROV/('probe_initial_'+entry['name']+'.txt')
            target.write_bytes(original.read_bytes())
            entry=dict(entry,output_file=target.name,output_sha256=sha(target),review='Initial broad ranking/budget limitation: structure retrieved map AST regions variables; refresh retrieved APIs but truncated contract semantics; skills showed contract but truncated actual skill-source nodes. No full retrieval PASS claimed.')
            initial.append(entry)
    questions=[('structure','explainers_structure_regional_paper_and_candidate_layout'),('refresh','One-command regional refresh'),('restore','Selective compatible restoration'),('paper_skill','paper_to_ppr_skill_ecopath_paper_to_regional_ppr'),('validation_skill','ecopath_model_validation_skill_ecopath_model_validation')]
    records=[]
    for key,question in questions:
        args=[str(cli),'query',question,'--graph','tools/knowledge_graph/graph.json','--budget','3500']
        result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf8')
        assert result.returncode==0,result.stderr
        assert result.stdout.strip(),f'Empty {key} retrieval'
        target=PROV/f'probe_{key}.txt';target.write_text(result.stdout,encoding='utf8')
        records.append({'name':key,'question':question,'command':['graphify']+args[1:],'exit_code':result.returncode,'output_file':target.name,'output_sha256':sha(target),'review':'pending semantic assessment'})
        print(f'{key}: {len(result.stdout)} characters')
    save(PROV/'retrieval_verification.json',{'checked_at':now(),'pass':False,'graph_sha256':sha(GRAPH/'graph.json'),'initial_attempts':initial,'probe_suites':{'structure':['structure'],'refresh_snapshots':['refresh','restore'],'two_active_skills':['paper_skill','validation_skill']},'probes':records,'status':'Exact concept-anchor CLI traversals completed; relevance/source claims require independent assessment before PASS. Initial broad ranking limitations are retained explicitly.'})

def usage():
    p=PROV/'cost.json'
    if p.is_file():data=load(p)
    else:
        previous=GRAPH/'cost.json'
        data={'historical_usage_as_previously_recorded':load(previous) if previous.is_file() else None,'historical_measurement_status':'Preserved as previously reported; not independently measured by this session.','runs':[],'total_input_tokens':None,'total_output_tokens':None,'total_monetary_cost':None,'total_status':'Unavailable because host semantic tools do not provide token/cost telemetry.'}
    graph=load(GRAPH/'graph.json');corpus=assert_sources()
    data['runs'].append({'date':now(),'graph_sha256':sha(GRAPH/'graph.json'),'source_files':len(corpus['sha256']),'input_tokens':None,'output_tokens':None,'monetary_cost':None,'status':'Actual host semantic-agent usage unavailable; no estimate presented as a measurement. Deterministic AST extraction is separately recorded.'})
    save(p,data);print('Usage metadata recorded as unavailable; prior reported history identified explicitly.')

def add_scope():
    corpus=assert_sources()
    sf='tools/workflow_checks/selection/test_snapshot_access.py'
    assert sf not in corpus['sha256'], 'Native ACL test is already scoped'
    assert (ROOT/sf).is_file()
    corpus['files']['code']=sorted(corpus['files']['code']+[sf])
    corpus['sha256'][sf]=sha(ROOT/sf)
    corpus['sha256']=dict(sorted(corpus['sha256'].items()))
    corpus['total_files']=len(corpus['sha256'])
    corpus['total_words']+=len((ROOT/sf).read_text('utf8').split())
    save(PROV/'corpus.json',corpus)
    ignore=ROOT/'.graphifyignore'
    ignore.write_text(ignore.read_text('utf8').rstrip()+'\n!'+sf+'\n',encoding='utf8')
    from graphify.detect import detect
    found=detect(ROOT,follow_symlinks=False,google_workspace=False)
    actual={Path(p).relative_to(ROOT).as_posix() if Path(p).is_absolute() else Path(p).as_posix() for paths in found['files'].values() for p in paths}
    assert actual==set(corpus['sha256']),f'Curated detector disagreement: {actual^set(corpus["sha256"])}'
    found['total_words']=corpus['total_words'];save(RUN/'detect.json',found)
    save(PROV/'scope_updates.json',{'checked_at':now(),'added_source':sf,'source_sha256':corpus['sha256'][sf],'reason':'Meaningful native regression verifies repeated snapshot promotion, inherited Windows ACL, and exact workbook/manifest bytes in both installed Python runtimes. Actual production saver already passes and was not changed.','verification_evidence':'regions/LME/LME_028/work/2026-10-04_000005_final_checks/qa/native_snapshot_access_verification.json','scope_files':corpus['total_files'],'code_files':len(corpus['files']['code']),'document_files':len(corpus['files']['document']),'detector_exact_membership':True,'semantic_chunks_unchanged':True})
    print(f'Native ACL regression added: {corpus["total_files"]} sources, {len(corpus["files"]["code"])} code, {len(corpus["files"]["document"])} documents')

def relabel():
    previous=load(PROV/'community_label_members.json')['communities']
    analysis=load(RUN/'analysis.json');labels={};records=[]
    for cid,members in analysis['communities'].items():
        current=set(members)
        matches=[]
        for old_id,old in previous.items():
            old_members=set(old['members']);overlap=len(current&old_members)
            if overlap:matches.append((overlap/len(current),overlap/len(current|old_members),old_id,old))
        assert matches,f'New community requires manual label: {cid}'
        share,jaccard,old_id,best=max(matches,key=lambda x:(x[0],x[1]))
        labels[cid]=best['label']
        records.append({'community':cid,'label':best['label'],'prior_community':old_id,'member_overlap_share':share,'jaccard':jaccard,'top_labels':analysis['top_labels'][cid]})
        if share<.7:print(f'MANUAL REVIEW {cid}: {share:.3f} {best["label"]} | '+ ' | '.join(analysis['top_labels'][cid][:8]))
    save(PROV/'community_labels.json',labels)
    save(PROV/'community_label_delta.json',{'checked_at':now(),'mapping':'Existing human labels transferred by actual member overlap after bounded semantic delta; lower-overlap communities require manual topical assessment.','records':records})
    print(f'{len(labels)} current communities mapped to actual prior member evidence')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['syntax','probes','usage','add_scope','relabel','browser_template_baseline','browser_template_payload_baseline','browser_delta'])
    globals()[parser.parse_args().action]()
