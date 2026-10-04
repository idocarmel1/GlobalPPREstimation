"""Read-only independent byte/table preservation audit. No scientific repair."""
import collections,csv,gzip,hashlib,json,math,sys,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,overview,records,rows
from tools.project_core.registry.discovery import discover_regions
QA=Path(__file__).parent.parent/'qa'
BQ=ROOT/'regions/LME_028/work/2026-10-04_000002_reorganization/qa'
def load(name):return json.loads((BQ/name).read_text('utf8'))
def dump(name,obj):(QA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
def normal(x):
 if isinstance(x,(tuple,list)):return [normal(v)for v in x]
 if isinstance(x,dict):return {k:normal(v)for k,v in x.items()}
 return x
def summaries(book):
 return {s:{t:{'rows':len(r),'headers':h}for t,(h,r)in b.items()}for s,b in book.items()}
files=load('files.json'); manifest={x['path']:x for x in files}
moves=list(csv.DictReader((BQ/'file_moves.csv').open(encoding='utf8',newline='')))
byold={r['original_path']:r for r in moves}
canonical=load('canonical_models.json'); lookup={(m['unit_id'],m['model_id']):ROOT/m['directory']for m in canonical['destinations']}
office={r['path']:r for r in load('office_link_edits.json')}
report={'timestamp':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'limitations':[
 'Snapshot/current numerical provenance is checked as recorded; this administrative audit does not regenerate extraction or SPPR.',
 'The baseline records workbook table semantics and file hashes. Original Word text/style preservation is supported by the migration operation assertions and changed-part records; no independent pre-edit Word XML baseline was captured.',
 'Raw shared NPP full-byte verification was run separately against its versioned manifest; this audit checks that result rather than reading 32 GB again.'
 ]}
checked=[]
for old,new in canonical['canonical'].items():
 p=ROOT/new; wanted=manifest[old]['sha256'];got=sha(p)if p.is_file()else None
 checked.append({'unit_id':new.split('/')[2],'model_id':p.parent.name,'path':new,'baseline_path':old,'expected_sha256':wanted,'actual_sha256':got,'pass':got==wanted})
report['canonical_models']={'count':len(checked),'all_exact':all(x['pass']for x in checked),'failures':[x for x in checked if not x['pass']]};dump('canonical_hashes.json',checked)
print('Canonical byte equality:',len(checked),report['canonical_models']['all_exact'],flush=True)
if not report['canonical_models']['all_exact']:raise RuntimeError('Unexpected canonical scientific bytes changed')
code_ext={'.py','.js','.ps1','.cmd','.md','.html','.txt','.yaml','.yml','.toml','.ini','.skill'}
def check_file(r):
 p=ROOT/r['retained_path'];old=r['original_path'];source=manifest.get(old,{})
 if not r['retained_path']:return ('removed_planned',old)
 if source.get('verification')=='deferred_raw_npp' or (old.startswith('common_reference_data/npp/raw/') and not source.get('sha256')):return ('npp_separate_verification',old)
 if not p.is_file():return ('missing',{'original_path':old,'retained_path':r['retained_path']})
 wanted=source.get('sha256') or r['sha256']
 if not wanted:return ('hash_unavailable',old)
 got=sha(p)
 if got==wanted:return ('exact',old)
 out={'original_path':old,'retained_path':r['retained_path'],'baseline_sha256':wanted,'actual_sha256':got}
 if r['retained_path']in office:return ('office_administrative',dict(out,changed_parts=office[r['retained_path']]['changed_parts']))
 if old=='Project.xlsx' or (old.startswith('regions/') and old.count('/')==2 and old.endswith('.xlsx')):return ('authoritative_workbook_semantics_required',out)
 if p.suffix.lower()in code_ext or old in {'.gitignore','.gitattributes','.graphifyignore','AGENTS.md'}:return ('implementation_or_documentation_changed',out)
 if p.name=='provenance.json' or p.name=='source_manifest.json':return ('administrative_provenance_changed',out)
 return ('unexpected_data_changed',out)
print('Checking retained original hashes...',flush=True)
with ThreadPoolExecutor(max_workers=4)as pool: checks=list(pool.map(check_file,moves))
counts=collections.Counter(k for k,_in in checks)
findings={k:[v for kind,v in checks if kind==k]for k in counts if k!='exact'}
dump('retained_file_findings.json',{'counts':dict(counts),'findings':findings})
report['retained_files']={'counts':dict(counts),'unexpected_data_changes':findings.get('unexpected_data_changed',[]),'missing':findings.get('missing',[])}
print('Retained original hashes:',dict(counts),flush=True)
with gzip.open(BQ/'workbooks.json.gz','rt',encoding='utf8')as f:base=json.load(f)
print('Semantic baseline loaded:',len(base),flush=True)
regions=discover_regions(ROOT);diffs=[]; allowed=[];sel=[]; snapshots=[]
allowed38={'results_model_id','results_model_sha256','production_eligible','calculation_status','calculation_input_sha256','calculation_result_sha256','historical_results_model_sha256'}
for i,(unit,p)in enumerate(sorted(regions.items()),1):
 old=base['regions/'+unit+'/'+unit+'.xlsx'];current=normal(read_book(p)); old=normal(old)
 old_over=overview(old); new_over=overview(current)
 sel.append({'unit_id':unit,'before':old_over.get('selected_model_id'),'after':new_over.get('selected_model_id'),'same':old_over.get('selected_model_id')==new_over.get('selected_model_id')})
 for sheet in set(old)|set(current):
  for table in set(old.get(sheet,{}))|set(current.get(sheet,{})):
   before=old.get(sheet,{}).get(table);after=current.get(sheet,{}).get(table)
   if before==after:continue
   entry={'unit_id':unit,'sheet':sheet,'table':table,'before_rows':len(before[1])if before else None,'after_rows':len(after[1])if after else None}
   if sheet=='Overview'and table=='Settings':
    bs=dict(before[1]);ns=dict(after[1]); changed={k:{'before':bs.get(k),'after':ns.get(k)}for k in set(bs)|set(ns)if bs.get(k)!=ns.get(k)}
    expected={'model_path'}|(allowed38 if unit=='LME_038'else set())
    entry['changes']=changed
    if set(changed)<=expected:allowed.append(entry)
    else:diffs.append(entry)
   elif sheet=='Overview'and table=='Available models'and before is None:allowed.append(dict(entry,reason='Generated administrative discovery list'))
   elif unit=='LME_038'and ((sheet=='Selected model groups'and table=='Group SPPR')or(sheet=='PPR'and table in {'Annual','Taxon SPPR','Taxon PPR inspected year'})):
    if before and after and before[0]==after[0]and not after[1]:allowed.append(dict(entry,reason='Explicit old-extraction-dependent numerical invalidation'))
    else:diffs.append(entry)
   elif unit=='LME_038'and sheet=='PPR–NPP'and table=='Ratios':
    expected=[r for r in before[1]if not r[0]]
    if after==[before[0],expected]:allowed.append(dict(entry,reason='Only model-dependent ratios removed'))
    else:diffs.append(entry)
   else:
    entry['first_difference']=next(({'row':j,'before':a,'after':b}for j,(a,b)in enumerate(zip(before[1],after[1]))if a!=b),None)if before and after else None
    diffs.append(entry)
 if i%40==0:print('Regions compared:',i,flush=True)
report['regional_workbooks']={'count':len(regions),'selected_unchanged':all(r['same']for r in sel),'unexpected_table_changes':diffs,'explicit_administrative_or_invalidation_changes':allowed}
dump('regional_table_comparison.json',report['regional_workbooks'])
oldproj=normal(base['Project.xlsx']);proj=normal(read_book(ROOT/'Project.xlsx'))
before_models={(r['unit_id'],r['model_id']):r for r in records(oldproj,'Models & coverage','Models')}
current_models={(r['unit_id'],r['model_id']):r for r in records(proj,'Models & coverage','Models')}
central_diffs=[];review=[];adminfields={'model_path','validation_report_path','validation_report_sha256','researcher_review_summary'}
for key,row in before_models.items():
 if key not in lookup:continue
 after=current_models.get(key)
 if after is None:central_diffs.append({'identity':key,'finding':'Missing retained registered model'});continue
 changed={k:{'before':row.get(k),'after':after.get(k)}for k in set(row)|set(after)if row.get(k)!=after.get(k)}
 unexpected={k:v for k,v in changed.items()if k not in adminfields}
 if unexpected:central_diffs.append({'identity':key,'changes':unexpected})
 review.append({'unit_id':key[0],'model_id':key[1],'status':after.get('researcher_review_status'),'decision_fields_equal':all(row.get(k)==after.get(k)for k in ['researcher_review_status','researcher_name','researcher_review_date','reviewed_model_sha256','reviewed_calculation_input_sha256'])})
newkeys=sorted(set(current_models)-set(before_models));removedkeys=sorted(set(before_models)-set(current_models))
report['central_model_metadata']={'before':len(before_models),'after':len(current_models),'new_distinct_variants':newkeys,'removed_alias_or_missing_model_rows':removedkeys,'unexpected_changes':central_diffs,'review_decisions_unchanged':all(x['decision_fields_equal']for x in review)}
dump('central_review_preservation.json',{'summary':report['central_model_metadata'],'decisions':review})
prev=[]
for r in moves:
 if '/previous_results/'not in r['original_path'] or not r['original_path'].endswith('.xlsx'):continue
 p=ROOT/r['original_path']
 if not p.is_file():prev.append({'path':r['original_path'],'finding':'already missing'});continue
 b=read_book(p);o=overview(b);unit=o.get('unit_id');mid=o.get('results_model_id');home=lookup.get((unit,mid));numeric=sum(1 for row in rows(b,'Selected model groups','Group SPPR')if any(isinstance(v,(int,float))and not isinstance(v,bool)and math.isfinite(v)for v in row))
 useful={'group_sppr_rows':len(rows(b,'Selected model groups','Group SPPR')),'numeric_coefficient_rows':numeric,'matching_rows':len(rows(b,'PPR','Matching')),'annual_rows':len(rows(b,'PPR','Annual')),'groups_rows':len(rows(b,'Selected model groups','Groups')),'sheets':list(b)}
 entry={'path':r['original_path'],'sha256':sha(p),'unit_id':unit,'selected_model_id':o.get('selected_model_id'),'results_model_id':mid,'results_model_sha256':o.get('results_model_sha256'),'input_hash':o.get('calculation_input_sha256'),'canonical_model':home.relative_to(ROOT).as_posix()if home else None,'useful':useful,'snapshot_exists':bool(home and(home/'results/regional_snapshot.xlsx').is_file())}
 if home:
  entry['current_model_sha256']=sha(home/'model.json');entry['source_hash_matches_current_model']=o.get('results_model_sha256')==entry['current_model_sha256']
  if entry['snapshot_exists']:
   existing=read_book(home/'results/regional_snapshot.xlsx');eo=overview(existing)
   entry['existing_snapshot_identity']={'selected_model_id':eo.get('selected_model_id'),'results_model_id':eo.get('results_model_id'),'results_model_sha256':eo.get('results_model_sha256'),'group_sppr_rows':len(rows(existing,'Selected model groups','Group SPPR')),'matching_rows':len(rows(existing,'PPR','Matching')),'annual_rows':len(rows(existing,'PPR','Annual'))}
 prev.append(entry)
report['previous_results_candidates']=prev;dump('previous_results_candidates.json',prev)
for key,home in lookup.items():
 p=home/'results/regional_snapshot.xlsx';mp=home/'results/result_manifest.json'
 if not p.exists():continue
 m=json.loads(mp.read_text('utf8'))if mp.is_file()else {};b=read_book(p);o=overview(b)
 snapshots.append({'unit_id':key[0],'model_id':key[1],'path':p.relative_to(ROOT).as_posix(),'actual_sha256':sha(p),'manifest_snapshot_sha256':m.get('snapshot_sha256'),'overview_results_id':o.get('results_model_id'),'manifest_results_id':m.get('model_id'),'overview_results_hash':o.get('results_model_sha256'),'current_model_hash':sha(home/'model.json'),'sheet_count':len(b),'manifest_keys':list(m)})
dump('full_snapshot_identities.json',snapshots);report['snapshots']={'count':len(snapshots),'identity_findings':snapshots}
report['raw_npp_verification']=load('npp_verification.json')
report['pass']=report['canonical_models']['all_exact']and not report['retained_files']['unexpected_data_changes']and not report['retained_files']['missing']and not diffs and not central_diffs and report['regional_workbooks']['selected_unchanged']and report['central_model_metadata']['review_decisions_unchanged']
dump('preservation_report.json',report)
print('Audit complete:',report['pass'],'unexpected regional tables',len(diffs),'unexpected data files',len(report['retained_files']['unexpected_data_changes']),'missing retained paths',len(report['retained_files']['missing']),flush=True)
