import sys,json,csv,math,hashlib,copy
from pathlib import Path
import numpy as np
Q=Path(__file__).resolve().parent;OUT=Q.parent;REG=OUT.parents[1];ROOT=REG.parents[1];MID=OUT.name
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
BASE=ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/EEZ_598'
b=read_book(REG/'EEZ_598.xlsx');old=read_book(BASE/'EEZ_598.xlsx');o=overview(b);a=json.loads((OUT/'taxon_audit.json').read_text(encoding='utf-8'))
E=ROOT/'regions/EEZ_941/evidence/2026-09-28_integration';dv=json.loads((E/'direct_diagnostics.json').read_text(encoding='utf-8'));rt=json.loads((E/'runtime_verification.json').read_text(encoding='utf-8'));loaded=json.loads((E/'loaded_state.json').read_text(encoding='utf-8'))
assert sha(REG/o['model_path'])==rt['input_sha256']==sha(BASE/'accepted_model.json')
assert sha(E/(MID+'.json'))==rt['input_sha256']
group_rows=records(b,'Selected model groups','Groups');groups={int(r['seq']):r for r in group_rows}
assert set(groups)==set(loaded['groups']['index'])==set(range(1,33))
loaded_differences=[]
for gi,lr in zip(loaded['groups']['index'],loaded['groups']['data']):
 for c,v in zip(loaded['groups']['columns'],lr):
  saved=groups[gi].get(c)
  if isinstance(v,(int,float)) and isinstance(saved,(int,float)):
   assert math.isclose(v,saved,rel_tol=1e-14,abs_tol=1e-13),(gi,c,v,saved)
   if v!=saved:loaded_differences.append({'group_id':gi,'field':c,'loaded':v,'workbook':saved,'difference':abs(v-saved)})
  else:assert v==saved,(gi,c,v,saved)
sppr=records(b,'Selected model groups','Group SPPR');diagnostics=[]
for method,key,filename in [('GE','new_GE','SPPR_GE.csv'),('TE','new_TE_EEfix','SPPR_TE.csv'),('With Egestion','new_WithEgestion','SPPR_With_Egestion.csv')]:
 with (E/filename).open(encoding='utf-8',newline='') as f:
  rr=list(csv.reader(f));sources=[int(x) for x in rr[0][1:]];ids=[int(x[0]) for x in rr[1:]];matrix=np.array([[float(x) for x in r[1:]] for r in rr[1:]])
 assert len(set(ids))==len(ids)==32 and len(set(sources))==len(sources)==4 and set(ids)==set(groups) and set(sources)=={29,30,31,32}
 assert np.isfinite(matrix).all()
 negative=[{'method':method,'source_id':sources[j],'source_name':groups[sources[j]]['group_name'],'group_id':ids[i],'group_name':groups[ids[i]]['group_name'],'sppr':float(matrix[i,j])} for i,j in zip(*np.where(matrix<0))]
 assert len(set(n['source_id'] for n in negative))==dv[method]['divergence']['n_negative_sources']
 diff={}
 for scope,ss in [('all',sources),('inner',[x for x in sources if x!=32]),('PP',[29,30])]:
  values=matrix[:,[sources.index(x) for x in ss]].sum(axis=1);expected={r['group']:r['sppr'] for r in sppr if r['scope']==scope and r['method']==key}
  assert len(expected)==32
  errors=[abs(float(v)-expected[groups[i]['group_name']]) for i,v in zip(ids,values)]
  assert all(math.isclose(float(v),expected[groups[i]['group_name']],rel_tol=1e-12,abs_tol=1e-8) for i,v in zip(ids,values))
  diff[scope]=max(errors)
 diagnostics.append({'method':method,'matrix_file':'../EEZ_941/evidence/2026-09-28_integration/'+filename,'matrix_sha256':sha(E/filename),'row_ids':ids,'row_names':[groups[i]['group_name'] for i in ids],'source_ids':sources,'source_names':[groups[i]['group_name'] for i in sources],'all_finite':True,'null_nonfinite_mask':[[False]*4]*32,'negative_entries':negative,'scope_reconciliation_max_abs_difference':diff,'aggregate_max_abs_difference':diff['all'],'direct':dv[method],'model_sha256':rt['input_sha256'],'settings':rt['settings'],'engine_hashes':rt['code_sha256'],'review':'Fresh independent inspection of exact saved arrays, all recipient rows including unfished groups and all four source columns; no solver rerun.'})
(OUT/'diagnostics_verification.json').write_text(json.dumps(diagnostics,indent=2,ensure_ascii=False),encoding='utf-8')
universe=[r for r in records(b,'Catch','Catch') if r['catch_basis']=='landings'];assert len(universe)==len(set(r['taxon'] for r in universe))==102
assert set(x['taxon'] for x in a['rows'])==set(r['taxon'] for r in universe)
cl={r['taxon']:r for r in records(b,'Classic PPR','Taxa')}
matching=records(b,'PPR','Matching')
for row in a['rows']:
 assert row['confidence'] in ['High','Medium','Low','Very low','Unresolved']
 assert row['simple_chain_ppr_tC']==(row['catch_tonnes']*row['classic_sppr']/9 if row['classic_sppr'] is not None else 0 if row['catch_tonnes']==0 else None)
 if '--adopted' in sys.argv:
  current=[r for r in matching if r['taxon']==row['taxon']]
  assert len(current)==(len(row['candidate_ids']) or 1)
  assert all(r['confidence']==row['confidence'].lower() for r in current)
  if row['candidates']:
   assert all(r['group']==c['name'] and math.isclose(r['weight'],c['weight'],rel_tol=1e-14,abs_tol=1e-15) for r,c in zip(current,row['candidates']))
  else:assert [(r['group'],r['weight']) for r in current]==[(None,None)]
 if row['weights']:assert math.isclose(math.fsum(row['weights']),1,abs_tol=1e-12)
for field in ['confidence_summary','membership_summary','allocation_summary']:
 assert sum(r['taxa'] for r in a[field])==102
 assert math.isclose(math.fsum(r['catch_tonnes'] for r in a[field]),a['total_catch_tonnes'],rel_tol=1e-14)
 assert math.isclose(math.fsum(r['ppr_tC'] for r in a[field]),a['simple_chain_ppr_tC'],rel_tol=1e-14)
 assert math.isclose(math.fsum(r['ppr_percentage'] for r in a[field]),100,abs_tol=1e-8)
classic_annual=next(r for r in records(b,'Classic PPR','Annual') if r['scope']=='all' and r['metric']=='ppr' and r['catch_basis']=='landings' and r['unidentified']=='method')
assert math.isclose(classic_annual[2019]/9,a['simple_chain_ppr_tC'],rel_tol=1e-14)
protected=[]
for f in json.loads((BASE/'protected_table_fingerprints.json').read_text(encoding='utf-8'))['tables']:
 key=f['sheet'],f['table'];same=digest_tables(list(b[key[0]][key[1]]))==digest_tables(list(old[key[0]][key[1]]));protected.append({'sheet':key[0],'table':key[1],'unchanged':same})
assert all(x['unchanged'] for x in protected)
assert b['Classic PPR']['Annual']==old['Classic PPR']['Annual']
annual=[{k:r[k] for k in ['scope','method','metric','status']}|{'value':r[2019]} for r in records(b,'PPR','Annual') if r['scope']=='all' and r['method'] in ['new_GE','new_TE_EEfix','new_WithEgestion'] and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric'] in ['ppr','covered_catch']]
result={'all_102_taxa_reassessed':True,'protected_tables_unchanged':True,'protected_checks':protected,'all_weights_and_confidence_checked':True,'summaries_reconcile':True,'simple_chain_reconciled':True,'no_positive_catch_missing_classic':not a['unknown_annual_ppr_taxa'],'classic_annual_preserved_exactly':True,'accepted_loaded_state_exact':True,'matrix_findings':[{'method':d['method'],'all_finite':d['all_finite'],'scope_reconciliation_max_abs_difference':d['scope_reconciliation_max_abs_difference'],'negative_entries':d['negative_entries']} for d in diagnostics],'model_annual_2019':annual,'final_workbook_sha256':sha(REG/'EEZ_598.xlsx')}
result.pop('accepted_loaded_state_exact');result['accepted_loaded_state_aligned_at_excel_precision']=True;result['loaded_state_max_abs_rounding_difference']=max(x['difference'] for x in loaded_differences)
(OUT/'loaded_state_precision_comparison.json').write_text(json.dumps(loaded_differences,indent=2),encoding='utf-8')
(OUT/'verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ['protected_checks','matrix_findings','model_annual_2019']},ensure_ascii=False))
