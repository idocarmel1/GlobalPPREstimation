"""Bounded, full-byte verified graph refresh for the canonical reorganized corpus.

The canonical graph is an evidence index, never a scientific approval authority.
Runtime fragments/caches are temporary and excluded from the corpus.
"""
import argparse,collections,copy,hashlib,json,math,os,re,sys,time
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
GRAPH=ROOT/'tools/knowledge_graph';PROV=GRAPH/'provenance';RUN=PROV/'.runtime'
os.environ['GRAPHIFY_OUT']=str(RUN)
os.environ['GRAPHIFY_NO_BACKUP']='1'
from tools.project_core.registry.paths import SourcePaths
CODE={'.py','.js'}
DOC={'.md','.txt','.rst'}
NOISE={'.git','.venv','venv','env','__pycache__','.pytest_cache','node_modules','vendor','_deps','cache','converted','output','outputs','raw','work','qa','renders','rendered','dist','build'}
def load(p):return json.loads(p.read_text('utf8'))
def save(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files(folder,extensions):
 out=[]
 for dp,dn,fn in os.walk(folder):
  dn[:]=[n for n in dn if n not in NOISE and not n.startswith('.')and not(Path(dp)/n).is_symlink()]
  out.extend(Path(dp)/n for n in fn if Path(n).suffix.lower()in extensions and not(Path(dp)/n).is_symlink())
 return out
def stem(path):
 # Use the installed extractor's actual immediate-parent identity, including
 # collapsed punctuation/underscores, rather than a divergent local imitation.
 from graphify.extract import _file_node_id
 value=_file_node_id(Path(path))
 assert re.fullmatch(r'[a-z0-9_]+',value),f'Non-ASCII source stem needs explicit review: {path}'
 return value
def prepare(final=False):
 RUN.mkdir(parents=True,exist_ok=True)
 hash_path=GRAPH/'source_hashes.json'
 if not hash_path.is_file():hash_path=PROV/'source_hashes.json'
 oldhash=load(hash_path);old=load(GRAPH/'graph.json');paths=SourcePaths(ROOT)
 decisions=[];existing={}
 for oldpath,wanted in oldhash.items():
  try:new=paths.resolve(oldpath)
  except ValueError as e:decisions.append({'original_path':oldpath,'disposition':'unresolved_reference','reason':str(e)});continue
  p=ROOT/new if new else None
  if not p or not p.is_file()or p.suffix.lower()not in CODE|DOC or any(x in NOISE for x in p.relative_to(ROOT).parts):
   decisions.append({'original_path':oldpath,'retained_path':new,'disposition':'excluded_removed_or_out_of_final_scope'});continue
  rel=p.relative_to(ROOT).as_posix();actual=sha(p);existing[oldpath]={'path':rel,'old_sha256':wanted,'sha256':actual,'exact':actual==wanted}
  decisions.append({'original_path':oldpath,'retained_path':rel,'old_sha256':wanted,'actual_sha256':actual,'disposition':'eligible_exact_reuse'if actual==wanted else 'changed_requires_reextraction'})
 mandatory=set()
 for folder in ['tools/project_core','tools/cli','tools/scientific_helpers','tools/scientific_code']:
  mandatory.update(p.relative_to(ROOT).as_posix()for p in files(ROOT/folder,CODE))
 docs={p.relative_to(ROOT).as_posix()for p in files(ROOT/'explainers',DOC)}|{'AGENTS.md','README.md'}
 for folder in ['tools/skills/paper-to-ppr','tools/skills/ecopath-model-validation']:
  docs.update(p.relative_to(ROOT).as_posix()for p in files(ROOT/folder,DOC))
  mandatory.update(p.relative_to(ROOT).as_posix()for p in files(ROOT/folder/'scripts',CODE))
 for kind in ['LME','EEZ','HS']:
  for region in (ROOT/'regions'/kind).glob('*'):
   for pattern in ['papers/*/models/*/model_notes.md','ecobase/*/model_notes.md']:
    docs.update(p.relative_to(ROOT).as_posix()for p in region.glob(pattern))
 # Retain previously curated current scientific review evidence; no fixture/work copies.
 docs.update(item['path']for item in existing.values()if Path(item['path']).suffix.lower()in DOC and '/model_validation/'in item['path'])
 docs.update(p.relative_to(ROOT).as_posix()for p in files(ROOT/'common_reference_data',DOC)if p.name=='README.md')
 for study in (ROOT/'research').glob('*'):
  if(study/'README.md').is_file():docs.add((study/'README.md').relative_to(ROOT).as_posix())
 # Existing substantive study findings/methods remain historical, omitting old implementation/test detail.
 docs.update(item['path']for item in existing.values()if item['path'].startswith('research/')and Path(item['path']).suffix.lower()in DOC and any(word in Path(item['path']).stem.lower()for word in ['method','finding','numerical','source_evidence']))
 docs={p for p in docs if(ROOT/p).is_file()and not any(x in NOISE for x in Path(p).parts)}
 # Workflow checks are current preservation/selection contracts; frozen study code is indexed by its guides.
 checks={p.relative_to(ROOT).as_posix()for p in files(ROOT/'tools/workflow_checks',CODE)}
 room=500-len(mandatory)-len(docs)
 if room<0:raise ValueError(f'Mandatory bounded corpus exceeds500: {len(mandatory)} code + {len(docs)} documents; revisit scientific scope explicitly')
 prioritized=sorted(checks,key=lambda p:(not any(s in p for s in ['/selection/','/structure/']),p))
 code=mandatory|set(prioritized[:room]);scope=sorted(code|docs)
 hashes={p:sha(ROOT/p)for p in scope}
 # Only exact full-byte unchanged semantic evidence with compliant deterministic IDs is reusable.
 candidates={oldpath:v for oldpath,v in existing.items()if v['exact']and v['path']in docs}
 nodes_by=collections.defaultdict(list)
 for n in old['nodes']:
  source=n.get('source_file')
  if source in candidates and n.get('_origin')!='ast':nodes_by[source].append(n)
 accepted={};rejected={}
 for oldpath,v in candidates.items():
  expected=stem(oldpath)+'_';items=nodes_by.get(oldpath,[])
  bad=[n for n in items if not n['id'].startswith(expected)or re.search(r'_rationale_\d+$',n['id'])]
  if items and not bad and stem(oldpath)==stem(v['path']):accepted[oldpath]=v
  else:rejected[oldpath]={'path':v['path'],'reason':'No compliant cached semantic fragment, changed source-stem identity, or obsolete rationale-fragment nodes'}
 reused_nodes=[];used_ids=set()
 for oldpath,v in accepted.items():
  for node in nodes_by[oldpath]:
   n=copy.deepcopy(node);n['source_file']=v['path'];n.pop('community',None);n.pop('norm_label',None)
   n['historical']=v['path'].startswith('research/');reused_nodes.append(n);used_ids.add(n['id'])
 reused_edges=[]
 for e in old['links']:
  source=e.get('source_file')
  if source in accepted and e['source']in used_ids and e['target']in used_ids:
   n=copy.deepcopy(e);n['source_file']=accepted[source]['path'];reused_edges.append(n)
 reused_hyper=[]
 for h in old.get('hyperedges',[]):
  source=h.get('source_file')
  if source in accepted and all(n in used_ids for n in h.get('nodes',[])):
   n=copy.deepcopy(h);n['source_file']=accepted[source]['path'];reused_hyper.append(n)
 reused_paths={v['path']for v in accepted.values()};uncached=sorted(docs-reused_paths)
 chunk_count=math.ceil(len(uncached)/22)if uncached else 0
 size,extra=divmod(len(uncached),chunk_count)if chunk_count else(0,0)
 chunks=[];offset=0
 for i in range(chunk_count):
  count=size+(1 if i<extra else 0);chunks.append(uncached[offset:offset+count]);offset+=count
 save(RUN/'reused_semantic.json',{'nodes':reused_nodes,'edges':reused_edges,'hyperedges':reused_hyper,'input_tokens':None,'output_tokens':None})
 save(PROV/'corpus.json',{'schema_version':1,'status':'final_sources_confirmed'if final else 'provisional_pending_final_sources','files':{'code':sorted(code),'document':sorted(docs)},'sha256':hashes,'total_files':len(scope),'total_words':sum(len((ROOT/p).read_text('utf8',errors='replace').split())for p in scope),'omitted_workflow_checks':sorted(checks-code),'policy':'All current core/CLI/scientific helper/engine implementation;2active skill instructions/resources;61modelnotes; retained curated scientific reviews; current reference guides and historical study purpose/findings. Work/fixtures, dependency trees, raw binaries, obsolete payloads and graph self-content excluded.'})
 save(PROV/'refresh_dispositions.json',{'prior_files':len(oldhash),'decisions':decisions,'reuse_accepted':accepted,'reuse_rejected':rejected,'semantic_reuse_count':len(reused_paths),'semantic_changed_or_new':len(uncached),'semantic_chunks':chunks})
 # Gitignore parent inclusion is explicit, so detection does not descend excluded branches.
 dirs=set()
 for p in scope:
  dirs.update(a.as_posix()for a in Path(p).parents if a!=Path('.'))
 lines=['# Canonical curated graph corpus; see tools/knowledge_graph/provenance/corpus.json','/*']
 for d in sorted(dirs,key=lambda d:(d.count('/'),d)):lines+=['!/'+d+'/','/'+d+'/*']
 lines+=['!/'+p for p in scope];(ROOT/'.graphifyignore').write_text('\n'.join(lines)+'\n',encoding='utf8')
 # Use the installed detector as an independent check of the exact allowlist.
 from graphify.detect import detect
 cached=load(RUN/'detect.json')if(RUN/'detect.json').is_file()else None
 cached_scope={Path(p).relative_to(ROOT).as_posix()for group in cached.get('files',{}).values()for p in group}if cached else set()
 if cached and cached_scope==set(scope):
  detected=cached;detected['total_words']=sum(len((ROOT/p).read_text('utf8',errors='replace').split())for p in scope)
  detected['detection_reuse']='Exact explicit allowlist membership previously checked by installed detector; every current allowed path and full-byte hash checked again. No broad directory re-scan.'
 else:detected=detect(ROOT,follow_symlinks=False,google_workspace=False)
 save(RUN/'detect.json',detected)
 actual={Path(p).relative_to(ROOT).as_posix()for group in detected.get('files',{}).values()for p in group}
 if actual!=set(scope):save(PROV/'detection_mismatch.json',{'missing':sorted(set(scope)-actual),'unexpected':sorted(actual-set(scope))});raise ValueError('Installed detector disagrees with exact curated allowlist')
 print('Corpus:',len(code),'code,',len(docs),'documents,',len(scope),'files; ~',sum(len((ROOT/p).read_text('utf8',errors='replace').split())for p in scope),'words')
 print('Semantic: exact compliant reuse',len(reused_paths),';',len(uncached),'files require extraction;',len(chunks),'chunks')
 print('Source status:', 'final confirmed'if final else 'provisional; final graph NOT refreshed')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare']);parser.add_argument('--final',action='store_true');args=parser.parse_args();prepare(args.final)
