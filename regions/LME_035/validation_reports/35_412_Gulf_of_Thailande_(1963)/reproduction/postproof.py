from pathlib import Path
import sys,json,pickle,math,collections,hashlib
Q=Path(__file__).parent; ROOT=Q.parents[4]; sys.path.insert(0,str(ROOT/'tools')); import workbooks as W
MID='35_412_Gulf_of_Thailande_(1963)'; R=ROOT/'regions/LME_035'; E=R/'validation_reports'/MID
def dump(n,v): (E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
with (Q/'final_book.pkl').open('rb') as f:b=pickle.load(f)
o=W.overview(b); assert o['selected_paper_ids']=='Christensen-1998__LME_035'; assert W.sha(R/'LME_035.xlsx')==json.loads((E/'canonical_reader_verification.json').read_text(encoding='utf-8'))['workbook_sha256']
a=json.loads((E/'taxon_audit.json').read_text(encoding='utf-8')); by={r['taxon']:r for r in a}; taxa=sorted(by)
catch={(r['taxon'],r['catch_basis']):r for r in W.records(b,'Catch','Catch')}; flags={r['taxon']:r['unidentified'] for r in W.records(b,'Catch','Catch')}; classic={r['taxon']:r for r in W.records(b,'Classic PPR','Taxa')}
tlchecks=[]
for t,r in classic.items():
 if W.finite(r['tl']) and W.finite(r['sppr']):
  expected=o['transfer_efficiency']**(1-r['tl']); assert math.isclose(expected,r['sppr'],rel_tol=1e-12,abs_tol=1e-10); tlchecks.append(t)
checks=0; maxdiff=0.; incomplete=[]; available_rows=[]
for r in W.records(b,'Classic PPR','Annual'):
 if r['metric'] not in ['ppr','catch','covered_catch']:continue
 for y in range(1950,2020):
  terms=[];covered=[];missing=[];allc=[]
  for t in taxa:
   c=catch[t,r['catch_basis']][y];v=classic.get(t,{}).get('sppr')
   if flags[t] and r['unidentified']=='zero': v=0.
   allc.append(c)
   if W.finite(c) and W.finite(v):terms.append(c*v);covered.append(c)
   elif W.finite(c) and c>0:missing.append(t)
  ex=math.fsum(allc) if r['metric']=='catch' else math.fsum(terms if r['metric']=='ppr' else covered)
  actual=r[y];assert math.isclose(ex,actual,abs_tol=1e-7,rel_tol=1e-12),(r,y,ex,actual);maxdiff=max(maxdiff,abs(ex-actual));checks+=1
  if missing and r['metric']=='ppr':incomplete.append(dict(catch_basis=r['catch_basis'],unidentified=r['unidentified'],year=y,taxa=missing,available_wet_subtotal=ex,status=r['status']))
 available_rows.append({k:r[k] for k in ['scope','method','catch_basis','unidentified','metric','status']})
dump('independent_classic_verification.json',dict(source='Exact protected Classic PPR Taxa; independent TE**(1-TL) and raw annual Catch multiplication, no Ecopath group TL',classic_coefficients_from_TL_checked=len(tlchecks),annual_base_cells_checked=checks,maximum_wet_difference=maxdiff,carbon_divisor=9,reference_year=2019,reference_basis='landings',reference_zero_catch_missing_coefficients=[t for t in taxa if not W.finite(classic.get(t,{}).get('sppr'))],reference_all_contributions_known=True,historical_missing_positive_catch_subtotals=incomplete,valid_bounds_preserved_by_full_exact_Classic_PPR_comparison=True,limitations='Historical nonzero catch with absent Classic coefficient remains an available subtotal; this review does not fill coefficients or alter protected Classic statuses/bounds.'))
coef={(r['taxon'],r['scope'],r['method']):r['sppr'] for r in W.records(b,'PPR','Taxon SPPR')}; methods=[]
for ar in W.records(b,'PPR','Annual'):
 if ar['metric']!='ppr' or ar['catch_basis']!='landings' or ar['unidentified']!='method':continue
 rows=[]
 for t in taxa:
  c=catch[t,'landings'][2019];v=coef[t,ar['scope'],ar['method']]
  if W.finite(v):rows.append(dict(taxon=t,catch_tonnes=c,weighted_coefficient_wet=v,ppr_tC=c*v/9,overall_confidence=by[t]['overall_confidence'],membership_confidence=by[t]['membership_confidence'],allocation_confidence=by[t]['allocation_confidence'],groups=by[t]['group_names'],weights=by[t]['weights']))
 total=math.fsum(r['ppr_tC'] for r in rows) if W.numeric_status(ar['status']) else None
 if total is not None:
  assert math.isclose(total,ar[2019]/9,abs_tol=1e-7,rel_tol=1e-12)
  for r in rows:r['share_percent']=100*r['ppr_tC']/total if total>0 else 0.
  summary=[dict(confidence=cf,taxa=sum(r['overall_confidence']==cf for r in rows),ppr_tC=math.fsum(r['ppr_tC'] for r in rows if r['overall_confidence']==cf),share_percent=100*math.fsum(r['ppr_tC'] for r in rows if r['overall_confidence']==cf)/total if total>0 else 0.) for cf in ['High','Medium','Low','Very low','Unresolved']]
 else: summary=[]
 methods.append(dict(method=ar['method'],scope=ar['scope'],status=ar['status'],total_ppr_tC=total,coverage_taxa_with_coefficient=len(rows),confidence_summary=summary,largest_contributors=sorted(rows,key=lambda r:(-r['ppr_tC'],r['taxon']))[:15],largest_very_low_contributors=sorted([r for r in rows if r['overall_confidence']=='Very low'],key=lambda r:(-r['ppr_tC'],r['taxon']))[:10],largest_coefficient=max(rows,key=lambda r:r['weighted_coefficient_wet']) if rows else None))
dump('method_specific_mapping_exposure.json',dict(workbook_sha256=W.sha(R/'LME_035.xlsx'),input_hash=W.input_hash(b),result_hash=o['calculation_result_sha256'],year=2019,basis='landings',unidentified='method',taxon_filter='all',carbon_divisor=9,denominator='Each saved model method and source scope separately; not the independent Classic PPR confidence denominator',methods=methods,interpretation='Finite coefficients and matrix sign checks do not establish approval. Weak residual membership, historical family and fixed donor/stage allocations remain consequential where method-specific shares show exposure; no mapping was selected to lower a coefficient or result.'))
solutions=json.loads((E/'direct_diagnostics/direct_solutions.json').read_text(encoding='utf-8')); groupnames={r['seq']:r['group_name'] for r in W.records(b,'Selected model groups','Groups')}; masks=[]; neg=[]
for method,matrices in solutions.items():
 for name,mat in matrices.items():
  assert len(mat['index'])==len(set(mat['index'])) and len(mat['columns'])==len(set(mat['columns']))
  assert len(mat['data'])==len(mat['index']);assert all(len(row)==len(mat['columns']) for row in mat['data']);assert all(isinstance(v,(int,float)) and math.isfinite(v) for row in mat['data'] for v in row)
  masks.append(dict(method=method,matrix=name,recipient_ids=mat['index'],recipient_names=[groupnames[i] for i in mat['index']],column_ids=mat['columns'],column_names=[groupnames[i] for i in mat['columns']],shape=[len(mat['index']),len(mat['columns'])],orientation='row recipient, column basal source' if name=='SPPR' else 'row/column groups as returned by accepted engine',units='t wet primary-source requirement per t wet recipient' if name=='SPPR' else 'dimensionless accepted solver operator',null_mask=[[False for v in row] for row in mat['data']],nan_mask=[[False for v in row] for row in mat['data']],positive_infinity_mask=[[False for v in row] for row in mat['data']],negative_infinity_mask=[[False for v in row] for row in mat['data']],zero_entries=sum(v==0 for row in mat['data'] for v in row),all_entries_finite=True))
  if name=='SPPR':
   for i,row in enumerate(mat['data']):
    for j,v in enumerate(row):
     if v<0:neg.append(dict(method=method,matrix=name,source_id=mat['columns'][j],source_name=groupnames[mat['columns'][j]],recipient_id=mat['index'][i],recipient_name=groupnames[mat['index'][i]],value=v,tolerance=0))
dump('matrix_masks_and_axes.json',dict(original_serialization='All retained SPPR/A/L entries are numeric and finite; serializer maps any original null/NaN/infinity to null, so absence of null proves all four masks are false. No nonfinite distinctions were collapsed in these matrices.',source_file='direct_diagnostics/direct_solutions.json',source_sha256=W.sha(E/'direct_diagnostics/direct_solutions.json'),synthetic_group_ids=[30],source_scope_definitions=dict(all=[30,29,28],inner=[29,28],PP=[28]),matrices=masks))
dump('negative_source_entries.json',dict(comparison_tolerance=0,all270_source_entries_inspected=True,entries=neg))
dump('regional_metadata_verification.json',dict(selected_model_id=o['selected_model_id'],selected_paper_ids=o['selected_paper_ids'],scientific_year=1980,inherited_id_year=1963,canonical_reader_current_workbook_sha256=W.sha(R/'LME_035.xlsx'),source_tables_pending_coordinator=True))
for method in ['new_GE','new_TE_EEfix','new_WithEgestion']:
 r=next(r for r in methods if r['method']==method and r['scope']=='all'); print(method,'total',r['total_ppr_tC'],'Very low',next(x['share_percent'] for x in r['confidence_summary'] if x['confidence']=='Very low'),'top',[(x['taxon'],x['share_percent']) for x in r['largest_contributors'][:4]])
print('Independent Classic cells',checks,'coefficient checks',len(tlchecks),'matrices',len(masks),'negative',len(neg))
