"""Execute and verify the installed Graphify pipeline within its canonical home.

This program never runs scientific calculations or approves scientific evidence.
Semantic fragments must first be produced by the installed skill's agent prompt.
"""
import argparse, collections, copy, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
GRAPH = ROOT/'tools/knowledge_graph'
PROV = GRAPH/'provenance'
RUN = PROV/'.runtime'
os.environ['GRAPHIFY_OUT'] = str(RUN)
os.environ['GRAPHIFY_NO_BACKUP'] = '1'
sys.path.insert(0, str(ROOT))
from refresh import load, save, sha, stem

def now(): return datetime.now(timezone.utc).isoformat()
def relative(value):
    if not value: return None
    p = Path(value)
    return p.relative_to(ROOT).as_posix() if p.is_absolute() else p.as_posix()
def build_exact(extraction):
    from graphify.build import build_from_json
    working=copy.deepcopy(extraction)
    # The installed ghost deduper keys semantic locations by basename and label,
    # conflating unrelated same-named notes. Full IDs already identify our nodes.
    # Hide locations only during that library pass, then restore exact citations.
    for n in working['nodes']:
        if n.get('_origin')=='semantic': n['source_location']=None
    G=build_from_json(working,root=ROOT)
    wanted={n['id'] for n in extraction['nodes']}
    assert set(G)==wanted, 'Library unexpectedly merged a full-source identity'
    for n in extraction['nodes']:
        if n.get('_origin')=='semantic':G.nodes[n['id']]['source_location']=n.get('source_location')
    return G
def assert_sources():
    corpus = load(PROV/'corpus.json')
    assert corpus['status'] == 'final_sources_confirmed', 'Parent has not confirmed final sources'
    different = [p for p,h in corpus['sha256'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    assert not different, f'Sources changed after final capture: {different}'
    return corpus

def assert_current_citations(items, corpus):
    """Merged source evidence must be current before canonical export, too."""
    for item in items:
        for citation in [item] + item.get('source_evidence', []):
            sf = relative(citation.get('source_file'))
            assert sf in corpus['sha256'] and citation.get('source_sha256') == corpus['sha256'][sf], 'Stale reused semantic evidence'

def assert_endpoints(extraction):
    ids = {node['id'] for node in extraction['nodes']}
    assert len(ids) == len(extraction['nodes']), 'Duplicate node identity before export'
    for edge in extraction['edges']:
        assert edge['source'] in ids and edge['target'] in ids, 'Unresolved edge endpoint before export'
    for hyperedge in extraction.get('hyperedges', []):
        assert len(set(hyperedge['nodes'])) >= 3 and all(endpoint in ids for endpoint in hyperedge['nodes']), 'Unresolved or invalid hyperedge before export'

def ast():
    corpus = assert_sources()
    from graphify.extract import extract
    result = extract([Path(p) for p in corpus['files']['code']], cache_root=ROOT, parallel=True, max_workers=2)
    # AST consumes no LLM tokens. These zeros describe only deterministic AST work.
    result['extraction_method'] = 'installed_graphify_ast'
    save(RUN/'ast.json', result)
    print(f"AST: {len(result['nodes'])} nodes, {len(result['edges'])} edges", flush=True)

def ast_preview():
    corpus=load(PROV/'corpus.json')
    code=[p for p in corpus['files']['code'] if (ROOT/p).is_file()]
    from graphify.extract import extract
    result=extract([Path(p) for p in code],cache_root=ROOT,parallel=True,max_workers=2)
    result['status']='provisional_readiness_check_not_final_graph'
    result['code_sha256']={p:sha(ROOT/p) for p in code}
    save(RUN/'ast_preview.json',result)
    print(f"Provisional AST: {len(code)} files, {len(result['nodes'])} nodes, {len(result['edges'])} edges; canonical graph unchanged",flush=True)

def refresh_ast_source():
    corpus=assert_sources()
    targets=args.source or ['tools/workflow_checks/structure/test_region_discovery.py']
    assert all(sf in corpus['files']['code'] for sf in targets)
    from graphify.extract import extract
    fresh=extract([Path(sf) for sf in targets],cache_root=ROOT,parallel=False)
    old=load(RUN/'ast.json')
    previous=[n for n in old['nodes'] if relative(n.get('source_file')) in targets]
    eof_only=targets==['tools/workflow_checks/structure/test_region_discovery.py']
    unchanged_ids={n['id'] for n in previous}=={n['id'] for n in fresh['nodes']}
    assert not eof_only or unchanged_ids, 'EOF-only AST extraction changed symbol identities'
    old['nodes']=[n for n in old['nodes'] if relative(n.get('source_file')) not in targets]+fresh['nodes']
    old['edges']=[e for e in old['edges'] if relative(e.get('source_file')) not in targets]+fresh['edges']
    save(RUN/'ast.json',old)
    old_validation=load(PROV/'ast_validation.json') if (PROV/'ast_validation.json').is_file() else {}
    records=old_validation.get('changed_source_extractions',[])
    if 'changed_source' in old_validation:records.append({k:old_validation[k] for k in ['checked_at','changed_source','source_sha256','symbol_ids_unchanged']})
    records.append({'checked_at':now(),'sources':targets,'sha256':{sf:corpus['sha256'][sf] for sf in targets},'fresh_nodes':len(fresh['nodes']),'fresh_edges':len(fresh['edges']),'symbol_ids_unchanged':unchanged_ids})
    save(PROV/'ast_validation.json',{'checked_at':now(),'method':f'Installed AST extraction of all{len(corpus["files"]["code"])} current scoped code files, including actual bounded re-extraction of subsequently changed/new sources.','changed_source_extractions':records,'code_sha256':{p:corpus['sha256'][p] for p in corpus['files']['code']},'input_tokens':0,'output_tokens':0,'usage_note':'These zero values describe only deterministic AST work; semantic agent usage is unavailable.'})
    print(f'Actually re-extracted {len(targets)} AST sources: {len(fresh["nodes"])} nodes, {len(fresh["edges"])} edges')

def prompts():
    corpus = assert_sources()
    chunks = load(PROV/'refresh_dispositions.json')['semantic_chunks']
    spec = (Path.home()/'.agents/skills/graphify/references/extraction-spec.md').read_text('utf8')
    template = spec.split('```',2)[1].strip()
    for i, files in enumerate(chunks,1):
        text = template.replace('FILE_LIST','\n'.join('- '+p for p in files))
        text = text.replace('CHUNK_NUM',str(i)).replace('TOTAL_CHUNKS',str(len(chunks)))
        text = text.replace('DEEP_MODE','false').replace('CHUNK_PATH',str(RUN/f'chunk_{i:02d}.json'))
        (RUN/f'prompt_{i:02d}.txt').write_text(text+'\n',encoding='utf8')
    save(PROV/'extraction_method.json', {'started_at':now(),'method':'installed_graphify_ast_and_general_writable_semantic_agents','prompt_source':'~/.agents/skills/graphify/references/extraction-spec.md','prompt_sha256':sha(Path.home()/'.agents/skills/graphify/references/extraction-spec.md'),'deep_mode':False,'semantic_chunks':len(chunks),'semantic_chunk_sizes':[len(c) for c in chunks],'input_tokens':None,'output_tokens':None,'usage_status':'Host collaboration tools do not expose actual token usage. Placeholder zeros in agent fragments are not measurements.','benchmark_status':'Actual bounded skill-efficiency traces are recorded in the 2026-10-04_000009_skill_efficiency work QA; graph extraction is not a scientific or full-pipeline benchmark.'})
    print(f'{len(chunks)} exact installed-skill prompts written')

def capture_updates():
    corpus=load(PROV/'corpus.json')
    qa_path='regions/LME/LME_028/work/2026-10-04_000002_reorganization/qa/final_graph_navigation_reconciliation.json'
    navigation=load(ROOT/qa_path)
    consistency_docs={'explainers/sppr_methods.md','explainers/PPREstimation/USER_GUIDE.md','tools/skills/paper-to-ppr/resources/extraction/references/parameter-conventions.md'}
    allowed={x['path'] for x in navigation['files']}|consistency_docs|{'explainers/plans/project_reorganization_plan.md','explainers/workflow.md','README.md','tools/workflow_checks/structure/test_region_discovery.py','tools/workflow_checks/selection/test_snapshot_access.py'}
    plain_path=ROOT/'regions/LME/LME_028/work/2026-10-04_000002_reorganization/qa/notes_plaintext_navigation.json'
    if plain_path.is_file():
        plain=load(plain_path)
        allowed|={x.get('path',x.get('file')) for x in plain.get('files',[])}
    actual={p:sha(ROOT/p) for p in corpus['sha256']}
    changed={p for p,h in actual.items() if h!=corpus['sha256'][p]}
    assert changed<=allowed,f'Unannounced source changes after parent source handoff: {changed-allowed}'
    records=[{'source_file':p,'before_sha256':corpus['sha256'][p],'after_sha256':actual[p],'method':'Actually re-extract the changed AST source.' if p.endswith('.py') else 'Changed passages must be re-read and re-extracted by writable semantic agent; source hash update alone is insufficient.','reason':'Actual verified execution record update' if p=='explainers/plans/project_reorganization_plan.md' else 'Removal of newly authored EOF blank; unchanged semantic/AST body verified by root' if p in {'README.md','tools/workflow_checks/structure/test_region_discovery.py'} else 'Verified administrative navigation/locator reconciliation' if p not in consistency_docs else 'Scientific descriptions corrected against unchanged actual method bodies'} for p in sorted(changed)]
    corpus['sha256']=actual
    corpus['total_words']=sum(len((ROOT/p).read_text('utf8',errors='replace').split()) for p in actual)
    corpus['semantic_refresh_state']='Changed-source semantic re-extraction in progress; canonical graph not yet refreshed.'
    save(PROV/'corpus.json',corpus)
    chunks=load(PROV/'refresh_dispositions.json')['semantic_chunks']
    previous=load(PROV/'source_updates.json')if(PROV/'source_updates.json').is_file()else {}
    history=previous.get('records',[])+records
    all_changed={r['source_file'] for r in history}
    save(PROV/'source_updates.json',{'captured_at':now(),'navigation_qa':qa_path,'navigation_qa_sha256':sha(ROOT/qa_path),'documentation_qa':'regions/LME/LME_028/work/2026-10-04_000006_contract_audit/qa/scientific_documentation_consistency.json','records':history,'completion_history':previous.get('completion_history',[]),'changed_count':len(all_changed),'latest_capture_changed_count':len(changed),'affected_by_chunk':{str(i):sorted(all_changed&set(c)) for i,c in enumerate(chunks,1)},'status':'Source bytes captured; changed passages still require actual semantic re-extraction.'})
    detection=load(RUN/'detect.json');detection['total_words']=corpus['total_words'];save(RUN/'detect.json',detection)
    print(f'Captured {len(changed)} explicitly authorized changed sources; ~{corpus["total_words"]} words. No freshness claim yet.')

def canonicalize_ids():
    from graphify.extract import _make_id
    changes=[]
    chunks=load(PROV/'refresh_dispositions.json')['semantic_chunks']
    for p in [RUN/f'chunk_{i:02d}.json' for i in range(1,len(chunks)+1)]:
        fragment=load(p)
        mapping={n['id']:_make_id(n['id']) for n in fragment['nodes']}
        assert len(set(mapping.values()))==len(mapping),f'Canonical ID collision in {p.name}'
        for n in fragment['nodes']:
            before=n['id'];n['id']=mapping[before]
            if before!=n['id']:changes.append({'chunk':p.name,'source_file':n['source_file'],'label':n['label'],'before_id':before,'canonical_id':n['id']})
            expected=stem(n['source_file'])
            assert n['id']==expected or n['id'].startswith(expected+'_'),f'Actual installed-extractor prefix mismatch: {n}'
        for e in fragment['edges']:
            e['source']=mapping[e['source']];e['target']=mapping[e['target']]
        for h in fragment.get('hyperedges',[]):h['nodes']=[mapping[n] for n in h['nodes']]
        save(p,fragment)
    previous=load(PROV/'id_normalization.json')if(PROV/'id_normalization.json').is_file()else{}
    save(PROV/'id_normalization.json',{'checked_at':now(),'normalizer':'Installed graphify.extract._make_id and _file_node_id','reason':'Two agents interpreted punctuation replacement differently. Use the actual installed AST/build canonical identity (collapsed underscores and trimmed boundaries), retaining every named concept, source citation and endpoint. The first local prefix validator imitated the rule incorrectly and was corrected against installed code.','records':previous.get('records',[])+changes,'identities_lost':0,'collisions':0,'scientific_attributes_changed':False})
    print(f'Canonical installed-extractor IDs: {len(changes)} syntactic normalizations, zero collisions/lost entities')

def collect():
    corpus = assert_sources()
    chunks = load(PROV/'refresh_dispositions.json')['semantic_chunks']
    reused = load(RUN/'reused_semantic.json')
    assert_current_citations(reused['nodes'] + reused['edges'] + reused.get('hyperedges', []), corpus)
    nodes, edges, hypers = list(reused['nodes']), list(reused['edges']), list(reused.get('hyperedges', []))
    validation = []
    for i, files in enumerate(chunks,1):
        p = RUN/f'chunk_{i:02d}.json'
        fragment = load(p)
        ids = {n['id'] for n in fragment['nodes']}
        assert len(ids)==len(fragment['nodes']), f'Duplicate node IDs within chunk {i}'
        covered = set()
        for n in fragment['nodes']:
            sf = relative(n.get('source_file')); n['source_file']=sf
            assert sf in files, f'Chunk {i} node outside assigned sources: {sf}'
            assert re.fullmatch(r'[a-z0-9_]+',n['id']), n['id']
            assert n['id'].startswith(stem(sf)+'_') or n['id']==stem(sf), f'Wrong semantic ID: {n["id"]} ({sf})'
            assert not re.search(r'_rationale_\d+$|_chunk\d+$|_c\d+$', n['id']), n['id']
            assert n.get('file_type') in {'code','document','paper','image','rationale','concept'}, n
            n['_origin']='semantic'; n['historical']=bool(n.get('historical')) or sf.startswith('research/')
            n['source_sha256']=corpus['sha256'][sf]
            covered.add(sf)
        assert covered==set(files), f'Chunk {i} omitted sources: {set(files)-covered}'
        for e in fragment['edges']+fragment.get('hyperedges',[]):
            sf = relative(e.get('source_file')); e['source_file']=sf
            assert sf in files, f'Chunk {i} edge source outside assigned files: {sf}'
            cf=e.get('confidence'); sc=e.get('confidence_score')
            assert (cf=='EXTRACTED' and sc==1) or (cf=='INFERRED' and sc in [.95,.85,.75,.65,.55]) or (cf=='AMBIGUOUS' and .1<=sc<=.3), f'Invalid confidence rubric {cf} {sc}'
            ends = e['nodes'] if 'nodes' in e else [e['source'],e['target']]
            assert all(n in ids for n in ends), f'Chunk {i} dangling endpoint: {ends}'
            e['_origin']='semantic'; e['historical']=bool(e.get('historical')) or sf.startswith('research/')
            e['source_sha256']=corpus['sha256'][sf]
        fragment['input_tokens']=None; fragment['output_tokens']=None
        fragment['usage_status']='Unavailable from host agent tool'
        save(p,fragment)
        nodes+=fragment['nodes']; edges+=fragment['edges']; hypers+=fragment.get('hyperedges',[])
        validation.append({'chunk':i,'files':len(files),'nodes':len(fragment['nodes']),'edges':len(fragment['edges']),'hyperedges':len(fragment.get('hyperedges',[])),'fragment_sha256':sha(p),'source_coverage':True,'schema':True,'input_tokens':None,'output_tokens':None})
    save(PROV/'semantic_validation.json',{'checked_at':now(),'chunks':validation,'reuse':{'full_hash_checked':True,'sources':load(PROV/'refresh_dispositions.json')['semantic_reuse_count'],'nodes':len(reused['nodes']),'independent_edge_records':len(reused['edges']),'hyperedges':len(reused.get('hyperedges',[]))},'pass':True})
    result={'nodes':nodes,'edges':edges,'hyperedges':hypers,'input_tokens':None,'output_tokens':None}
    save(RUN/'semantic.json',result)
    from graphify.cache import save_semantic_cache
    saved=save_semantic_cache(nodes,edges,hypers,root=ROOT)
    print(f'Semantic: {len(nodes)} nodes, {len(edges)} edges; {saved} source fragments cached')

def merge():
    corpus=assert_sources(); a=load(RUN/'ast.json'); s=load(RUN/'semantic.json')
    explicit_score_count=0; ambiguous_score_count=0
    for e in a['edges']:
        if 'confidence_score' not in e:
            if e.get('confidence')=='EXTRACTED':
                e['confidence_score']=1.0;explicit_score_count+=1
            else:
                # The installed exporter defaults missing inference scores to0.5,
                # forbidden by the extraction rubric. Preserve the missingness and
                # original category, and expose the relation as uncertain instead.
                e['original_confidence']=e.get('confidence')
                e['confidence_score_unavailable']=True
                e['confidence']='AMBIGUOUS';e['confidence_score']=.2;ambiguous_score_count+=1
    for n in a['nodes']:
        if not n.get('source_file'):
            cited=[e for e in a['edges'] if e['target']==n['id'] and e.get('source_file') and e.get('confidence')=='EXTRACTED']
            assert cited,f'Uncited installed AST node: {n}'
            n['original_source_file']=n.get('source_file');n['source_file']=cited[0]['source_file']
            n['source_location']=cited[0].get('source_location');n['external_stub']=True
            n['rationale']='Symbol explicitly referenced by current code; implementation is outside the scoped corpus.'
    node_list=a['nodes']+s['nodes']; edge_list=a['edges']+s['edges']
    rationale={n['id']:n for n in node_list if n.get('_origin')=='ast' and n.get('file_type')=='rationale'}
    targets=collections.defaultdict(list)
    for e in edge_list:
        if e.get('relation')=='rationale_for' and e['source'] in rationale: targets[e['target']].append(rationale[e['source']])
    for n in node_list:
        if n['id'] in targets:
            n['rationale']=[{'text':x.get('label'),'source_location':x.get('source_location')} for x in targets[n['id']]]
    node_list=[n for n in node_list if n['id'] not in rationale]
    edge_list=[e for e in edge_list if e['source'] not in rationale and e['target'] not in rationale]
    ids={n['id'] for n in node_list}
    reused = load(RUN/'reused_semantic.json')
    assert all(e['source'] in ids and e['target'] in ids for e in reused['edges']), 'Unchanged-source relationship endpoint needs explicit fresh reconciliation'
    assert all(all(n in ids for n in h['nodes']) for h in reused.get('hyperedges', [])), 'Unchanged-source hyperedge endpoint needs explicit fresh reconciliation'
    missing=collections.defaultdict(list)
    for e in edge_list:
        for endpoint in [e['source'],e['target']]:
            if endpoint not in ids: missing[endpoint].append(e)
    # Explicit external import references are stubs; they make no implementation claim.
    excluded=[]
    for endpoint, evidence in missing.items():
        imports=[e for e in evidence if e.get('relation') in {'imports','imports_from'} and e.get('confidence')=='EXTRACTED' and e.get('source_file')]
        if not imports: excluded+=evidence; continue
        citation=imports[0]; sf=relative(citation['source_file'])
        node_list.append({'id':endpoint,'label':endpoint,'file_type':'code','source_file':sf,'source_location':citation.get('source_location'),'external_stub':True,'rationale':'Imported name referenced by current source; implementation not included in graph corpus.','_origin':'ast'})
        ids.add(endpoint)
    by_id={}; collisions=[]
    for n in node_list:
        sf=relative(n.get('source_file')); n['source_file']=sf
        assert sf in corpus['sha256'], f'Node has no indexed current citation: {n}'
        n['source_sha256']=corpus['sha256'][sf]
        n['historical']=bool(n.get('historical')) or sf.startswith('research/')
        if '/model_validation/evidence/source_review/' in sf:
            n['scientific_currency']='Not established by graph refresh; consult adjacent model_notes.md and recorded review provenance.'
        if n['id'] not in by_id: by_id[n['id']]=n; continue
        previous=by_id[n['id']]
        assert previous.get('label')==n.get('label'), f'ID collision between different concepts: {previous} / {n}'
        fields={'id','source_file','source_sha256','source_location','source_evidence'}
        sources=previous.setdefault('source_evidence',[{'source_file':previous['source_file'],'source_sha256':previous['source_sha256'],'source_location':previous.get('source_location'),'attributes':{k:v for k,v in previous.items() if k not in fields}}])
        entry={'source_file':sf,'source_sha256':n['source_sha256'],'source_location':n.get('source_location'),'attributes':{k:v for k,v in n.items() if k not in fields}}
        if entry not in sources:sources.append(entry)
        if sf!=previous['source_file']:collisions.append({'id':n['id'],'sources':[previous['source_file'],sf],'disposition':'Same deterministically named entity retains separate current source evidence'})
    edges=[]; seen=set(); omitted=[]; cross_language=[]
    for e in edge_list:
        if e['source'] not in ids or e['target'] not in ids:
            omitted.append(e); continue
        sf=relative(e.get('source_file'))
        assert sf in corpus['sha256'], f'Edge has no indexed current citation: {e}'
        e['source_file']=sf; e['source_sha256']=corpus['sha256'][sf]
        e['historical']=bool(e.get('historical')) or sf.startswith('research/'); e.setdefault('_origin','ast')
        if e.get('relation')=='calls':
            left=by_id[e['source']];right=by_id[e['target']]
            langs={Path(left['source_file']).suffix.lower(),Path(right['source_file']).suffix.lower()}
            if not left.get('external_stub') and not right.get('external_stub') and langs=={'.py','.js'}:
                cross_language.append(e);continue
        if '/model_validation/evidence/source_review/' in sf:
            e['scientific_currency']='Not established by graph refresh; consult adjacent model_notes.md and recorded review provenance.'
        if e.get('confidence')=='EXTRACTED': assert e.get('confidence_score')==1.0, e
        key=json.dumps(e,sort_keys=True,ensure_ascii=False)
        if key not in seen:edges.append(e);seen.add(key)
    save(PROV/'merge_dispositions.json',{'rationale_fragments_folded_into_attributes':len(rationale),'unresolved_nonimport_edges_omitted':omitted,'phantom_cross_language_calls_rejected':cross_language,'same_named_entity_multi_source_evidence':collisions,'external_import_stubs':len([n for n in by_id.values() if n.get('external_stub')]),'edge_records':len(edges),'installed_ast_missing_EXTRACTED_scores_set_to_rubric_1':explicit_score_count,'installed_ast_unscored_inferences_marked_ambiguous':ambiguous_score_count,'inference_missingness_policy':'Original INFERRED category and unavailable-score flag are retained; an unscored installed-AST inference is presented as AMBIGUOUS at rubric score0.2 rather than inventing certainty or accepting the exporter default0.5.','library_ghost_deduplication':'Semantic source locations are temporarily hidden during the library basename/label ghost-deduplication pass, then restored exactly. Full deterministic node IDs and all source evidence remain authoritative; unrelated same-basename source notes cannot be silently merged.','input_tokens':None,'output_tokens':None})
    result={'nodes':list(by_id.values()),'edges':edges,'hyperedges':s.get('hyperedges',[]),'input_tokens':None,'output_tokens':None}
    assert_endpoints(result)
    save(RUN/'extraction.json',result)
    from graphify.cluster import cluster,score_all
    from graphify.analyze import god_nodes,surprising_connections
    G=build_exact(result)
    assert set(G.nodes())==set(by_id), 'Library unexpectedly dropped/merged a node; inspect exact evidence'
    communities=cluster(G); cohesion=score_all(G,communities)
    save(RUN/'analysis.json',{'communities':{str(k):v for k,v in communities.items()},'cohesion':{str(k):v for k,v in cohesion.items()},'gods':god_nodes(G),'surprises':surprising_connections(G,communities),'top_labels':{str(k):[G.nodes[n].get('label') for n in sorted(v,key=lambda n:G.degree(n),reverse=True)[:12]] for k,v in communities.items()},'nodes':G.number_of_nodes(),'topology_edges':G.number_of_edges()})
    print(f'Merged {len(by_id)} nodes, {len(edges)} independently attributed edges, {len(communities)} communities')

def export():
    corpus=assert_sources(); extraction=load(RUN/'extraction.json'); analysis=load(RUN/'analysis.json')
    assert_current_citations(extraction['nodes'] + extraction['edges'] + extraction.get('hyperedges', []), corpus)
    assert_endpoints(extraction)
    dispositions=load(PROV/'refresh_dispositions.json')
    labels={int(k):v for k,v in load(PROV/'community_labels.json').items()}
    communities={int(k):v for k,v in analysis['communities'].items()}
    assert set(labels)==set(communities), 'Every community needs a human-readable label'
    assert all(2<=len(s.split())<=5 for s in labels.values()), 'Community labels must be 2–5 words'
    from graphify.cluster import score_all
    from graphify.analyze import god_nodes,surprising_connections,suggest_questions
    from graphify.report import generate
    from graphify.export import to_json,to_html
    from graphify.detect import save_manifest
    G=build_exact(extraction)
    if G.number_of_nodes()>5000 and not (RUN/'html_aggregation_notice.json').is_file():
        raise RuntimeError('Tell the parent/user that HTML will aggregate communities above5000nodes, then record the notice before exporting.')
    for cid,members in communities.items():
        for n in members:G.nodes[n]['community_label']=labels[cid]
    base=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    checked=now()
    source_hash_file='provenance/source_hashes.json'
    save(PROV/'source_hashes.json',corpus['sha256'])
    save_manifest({kind:[ROOT/p for p in paths] for kind,paths in corpus['files'].items()},manifest_path=PROV/'manifest.json',kind='both',root=ROOT)
    assert to_json(G,communities,str(GRAPH/'graph.json'),force=True,built_at_commit=base)
    data=load(GRAPH/'graph.json')
    evidence=collections.defaultdict(list)
    for e in extraction['edges']:evidence[tuple(sorted([e['source'],e['target']]))].append(e)
    for link in data['links']:
        link['evidence']=evidence[tuple(sorted([link['source'],link['target']]))]
    data['freshness']={'status':'current_for_recorded_curated_sources','checked_at':checked,'base_commit':base,'working_tree_snapshot':True,'source_hashes_file':source_hash_file,'source_manifest_sha256':sha(PROV/'source_hashes.json'),'corpus_file':'provenance/corpus.json','note':'Every indexed source was checked by full SHA256, including frontmatter. Historical scientific studies remain explicitly historical. Base commit does not imply an unchanged checkout or scientific approval.'}
    data['communities']={str(k):{'label':labels[k],'members':v,'cohesion':analysis['cohesion'][str(k)]} for k,v in communities.items()}
    data['extraction_usage']={'input_tokens':None,'output_tokens':None,'monetary_cost':None,'status':'Unavailable from host tools; not estimated as zero.'}
    save(GRAPH/'graph.json',data)
    detection=load(RUN/'detect.json')
    report=generate(G,communities,score_all(G,communities),labels,god_nodes(G),surprising_connections(G,communities),detection,{'input':0,'output':0},'.',suggested_questions=suggest_questions(G,communities,labels),built_at_commit=base)
    report=re.sub(r'^- Token cost:.*$', '- Token cost: unavailable; the host agent tools did not expose actual input/output usage.',report,flags=re.M)
    report+='\n\nThe graph indexes the explicit curated scope in [REFRESH_SCOPE.md](REFRESH_SCOPE.md). Freshness uses full source SHA256 hashes, including frontmatter; it is not evidence of scientific readiness or researcher approval. Every independently attributed relationship is retained in each JSON link’s `evidence` array, while clustering and HTML use one edge per node pair. Historical research nodes and edges are marked `historical`. Bounded skill-efficiency trials are recorded separately in the model-local work QA; they do not establish full pipeline equivalence.\n'
    (GRAPH/'GRAPH_REPORT.md').write_text(report,encoding='utf8')
    to_html(G,communities,str(GRAPH/'graph.html'),community_labels=labels,node_limit=5000 if G.number_of_nodes()>5000 else None)
    if G.number_of_nodes()<=5000:
        # Native export omits source currency attributes from its information
        # panel. Carry through existing graph evidence, without changing it.
        hp=GRAPH/'graph.html';html=hp.read_text('utf8')
        match=re.search(r'const RAW_NODES = (\[.*?\]);\nconst RAW_EDGES = ',html,re.S)
        assert match, 'Unexpected installed HTML export format'
        raw_nodes=json.loads(match.group(1))
        for item in raw_nodes:
            evidence=G.nodes[item['id']]
            item['historical']=bool(evidence.get('historical'))
            item['source_location']=evidence.get('source_location')
            item['scientific_currency']=evidence.get('scientific_currency')
        payload=json.dumps(raw_nodes,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        html=html[:match.start(1)]+payload+html[match.end(1):]
        old='_source_file: n.source_file, _file_type: n.file_type, _degree: n.degree,'
        assert old in html
        html=html.replace(old,old+'\n  _historical: n.historical, _source_location: n.source_location, _scientific_currency: n.scientific_currency,')
        old='<div class="field">Source: ${esc(n._source_file || \'-\')}</div>'
        assert old in html
        html=html.replace(old,old+'\n    <div class="field">Location: ${esc(n._source_location || \'not specified\')}</div>\n    ${n._historical ? `<div class="field">Historical evidence</div>` : \'\'}\n    ${n._scientific_currency ? `<div class="field">${esc(n._scientific_currency)}</div>` : \'\'}')
        # Native neighbor handler inserts a quoted JSON string inside a double
        # quoted HTML attribute; escape it so browser parsing preserves the ID.
        old='onclick="focusNode(${JSON.stringify(nid)})"'
        assert old in html
        html=html.replace(old,'onclick="focusNode(${esc(JSON.stringify(nid))})"')
        hp.write_text(html,encoding='utf8')
        save(PROV/'html_export_adjustments.json',{'checked_at':now(),'native_export':'Installed graphify.export.to_html','evidence_attributes_preserved':['historical','source_location','scientific_currency'],'neighbor_handler':'HTML-escaped the existing JSON string node ID inside its onclick attribute to preserve valid quoting. No node/relationship identity changed.','reason':'Retained historical studies and source reviews must expose their recorded scientific currency; generated navigation must preserve actual IDs.'})
    (GRAPH/'REFRESH_SCOPE.md').write_text(f'''# Current reorganized knowledge graph

This graph was refreshed at {checked} from the full-byte source manifest in [provenance/corpus.json](provenance/corpus.json). It covers {corpus['total_files']} explicitly selected supported files ({len(corpus['files']['code'])} code, {len(corpus['files']['document'])} documents; approximately {corpus['total_words']:,} words). All {len([p for p in corpus['files']['document'] if p.endswith('/model_notes.md')])} canonical model notes, the project contract/explainers, both active skills and their resources, current core/CLI/scientific helper/engine implementations, retained curated source reviews, reference guides and historical study purpose/findings are included.

The graph is an architectural and evidence index. Model selection, loadability, scientific readiness, diagnostic permission and researcher approval are separate. A relationship extracted from a report does not certify that report’s scientific conclusion. Historical study files retain their original research role and are marked historical, even when their text describes a then-current result.

The scope excludes dependency trees, temporary work/QA copies, raw binary scientific data, publication binaries, XLSX/DOCX packages, runtime products, obsolete extraction packages, graph self-content and frozen research implementation/test detail. Native publication/workbook evidence is accessed through indexed model notes and source review references; this graph does not claim an exhaustive extraction of those binaries. Historical research is represented by its guides/findings. The exact allowlist is [.graphifyignore](../../.graphifyignore); no second graph directory is used.

Semantic evidence for {dispositions['semantic_reuse_count']} unchanged documents was reused only after full-byte/source-ID eligibility checks; {dispositions['semantic_changed_or_new']} documents requiring fresh extraction were re-extracted by writable agents using the installed Graphify extraction prompt. Every independently attributed reused edge record is preserved. AST extraction used the installed deterministic extractor and its content cache on every current scoped code file. AST rationale fragments were folded into rationale attributes; explicitly imported external names remain citation-backed stubs whose implementations are outside scope. The installed AST extractor may qualify IDs with the source path only when actual same-stem IDs collide; those are extractor identities, not invented semantic duplicates.

[Source hashes](provenance/source_hashes.json), [prior-source dispositions](provenance/refresh_dispositions.json), [merge dispositions](provenance/merge_dispositions.json), [semantic validation](provenance/semantic_validation.json) and [extraction method](provenance/extraction_method.json) provide the audit trail. Actual token usage and monetary cost are unavailable. Bounded efficiency traces and scientific replication limits are recorded in `regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency/qa/`; this graph excludes those temporary trial artifacts.

Clustering uses {G.number_of_nodes():,} nodes and {G.number_of_edges():,} node pairs. Each graph JSON link retains all its independently attributed `evidence` records ({len(extraction['edges']):,} total); the visualization displays clustering topology. Confidence values preserve the distinction between explicit, inferred and ambiguous relationships. Source existence/full hashes/endpoints and representative retrieval/HTML behavior are recorded in [provenance/completion_verification.json](provenance/completion_verification.json).

Query only this graph: `graphify query "question" --graph tools/knowledge_graph/graph.json`.
''',encoding='utf8')
    print(f'Exported current graph JSON/report/scope/HTML: {G.number_of_nodes()} nodes, {G.number_of_edges()} pairs')

def verify():
    corpus=assert_sources(); graph=load(GRAPH/'graph.json'); hashes=load(PROV/'source_hashes.json')
    assert hashes==corpus['sha256'], 'Final full-byte source manifest differs from captured corpus'
    assert sha(PROV/'source_hashes.json')==graph['freshness']['source_manifest_sha256']
    assert graph['freshness']['status']=='current_for_recorded_curated_sources'
    ids={n['id'] for n in graph['nodes']}
    assert len(ids)==len(graph['nodes']), 'Duplicate final IDs'
    covered=set(); citation_count=0
    for n in graph['nodes']:
        assert re.fullmatch(r'[a-z0-9_]+',n['id']), n['id']
        assert not re.search(r'_rationale_\d+$|_chunk\d+$',n['id']),n['id']
        assert n.get('file_type') in {'code','document','paper','image','rationale','concept'},n
        evidence=[n]+n.get('source_evidence',[])
        for item in evidence:
            sf=item['source_file'];assert sf in hashes and item.get('source_sha256')==hashes[sf],item
            covered.add(sf);citation_count+=1
        if n.get('_origin')=='semantic':
            assert n['id'].startswith(stem(n['source_file'])+'_') or n['id']==stem(n['source_file']),n['id']
        assert not n['source_file'].startswith('research/') or n.get('historical',False),n
    assert covered==set(hashes),f'Indexed sources missing node coverage: {set(hashes)-covered}'
    pairs=set();edge_records=0
    for link in graph['links']:
        assert link['source'] in ids and link['target'] in ids,link
        pair=tuple(sorted([link['source'],link['target']]));assert pair not in pairs,pair;pairs.add(pair)
        assert link.get('evidence'),link
        for e in link['evidence']:
            assert e['source'] in ids and e['target'] in ids,e
            assert tuple(sorted([e['source'],e['target']]))==pair,e
            sf=e['source_file'];assert sf in hashes and e.get('source_sha256')==hashes[sf],e
            assert e.get('confidence') in {'EXTRACTED','INFERRED','AMBIGUOUS'},e
            assert isinstance(e.get('confidence_score'),(int,float)) and 0<=e['confidence_score']<=1,e
            assert not sf.startswith('research/') or e.get('historical',False),e
            edge_records+=1
    for h in graph.get('hyperedges',[]):
        assert len(h['nodes'])>=3 and all(n in ids for n in h['nodes']),h
        assert h['source_file'] in hashes and h['source_sha256']==hashes[h['source_file']],h
    assert graph['extraction_usage']['input_tokens'] is None and graph['extraction_usage']['output_tokens'] is None
    assert edge_records==len(load(RUN/'extraction.json')['edges']), 'Library omitted a separately attributed edge record'
    result={'checked_at':now(),'pass':False,'integrity_pass':True,'source_full_sha256':True,'including_frontmatter':True,'all_source_paths_exist':True,'all_scoped_sources_have_nodes':True,'supported_file_types':True,'deterministic_semantic_ids':True,'no_rationale_fragment_nodes':True,'all_endpoints_valid':True,'all_edge_evidence_preserved':True,'historical_evidence_explicit':True,'scope_files':len(hashes),'nodes':len(ids),'topology_pairs':len(pairs),'independent_edge_evidence':edge_records,'hyperedges':len(graph.get('hyperedges',[])),'node_citations':citation_count,'graph_sha256':sha(GRAPH/'graph.json'),'html_sha256':sha(GRAPH/'graph.html'),'report_sha256':sha(GRAPH/'GRAPH_REPORT.md'),'source_manifest_sha256':sha(PROV/'source_hashes.json'),'input_tokens':None,'output_tokens':None,'retrieval_probes':'pending','html_interaction':'pending','scientific_scope_limit':'This verifies the architecture/evidence index and its recorded curated sources. It does not rerun scientific calculations, read all publication/workbook binaries, or grant researcher approval.'}
    save(PROV/'completion_verification.json',result)
    print(f'Verified {len(hashes)} full-byte sources, {len(ids)} nodes, {len(pairs)} pairs, {edge_records} evidence records')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['ast','ast_preview','refresh_ast_source','prompts','capture_updates','canonicalize_ids','collect','merge','export','verify'])
    parser.add_argument('--source',action='append',help='Explicit scoped AST file for a bounded re-extraction')
    args=parser.parse_args();globals()[args.action]()
