import sys,json,math,pickle,collections,zipfile,re
from pathlib import Path
from lxml import etree as X
Q=Path(__file__).parent;ROOT=Q.parents[4];sys.path.insert(0,str(ROOT/'tools'));import workbooks as W;import regional
R=ROOT/'regions/LME_038';MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)';E=R/'validation_reports'/MID
def dump(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
b=W.read_book(R/'LME_038.xlsx');o=W.validate_region(b,R/'LME_038.xlsx')
with(Q/'fresh_read_book.pkl').open('wb')as f:pickle.dump(b,f)
with(Q/'book.pkl').open('rb')as f:old=pickle.load(f)
protected={s:b[s]==old[s]for s in ['Catch','Classic PPR','NPP','Selected model groups']};assert all(protected.values()),protected
diag_protected={k:b['Diagnostics'][k]==old['Diagnostics'][k]for k in old['Diagnostics']};assert all(diag_protected.values()),diag_protected
assert o['selected_model_id']==MID and o['results_model_sha256']==W.sha(R/'models'/MID/'model.json')=='db0bc803ea5a068e346b82df8d8b4e4b13f8351bf61103c6507997cb6996ae35';assert o['calculation_input_sha256']==W.input_hash(b)and o['calculation_result_sha256']==regional.result_hash(b)
a=json.loads((E/'taxon_audit.json').read_text(encoding='utf-8'));by={r['taxon']:r for r in a};catch={(r['taxon'],r['catch_basis']):r for r in W.records(b,'Catch','Catch')};simple={r['taxon']:r['sppr']for r in W.records(b,'Classic PPR','Taxa')};flags={r['taxon']:r['unidentified']for r in W.records(b,'Catch','Catch')};taxa=sorted(by);assert len(taxa)==181
allmaps=collections.defaultdict(list)
for m in W.records(b,'PPR','Matching'):allmaps[m['taxon']].append(m)
rank=['Unresolved','Very low','Low','Medium','High'];weights=0
for r in a:
 assert r['overall_confidence']==min([r['membership_confidence'],r['allocation_confidence']],key=rank.index);assert math.isclose(math.fsum(r['weights']),1,abs_tol=1e-12)
 mm=allmaps[r['taxon']];positive=[(g,w)for g,w in zip(r['group_names'],r['weights'])if w>0];assert [x['group']for x in mm]==[g for g,w in positive];assert all(math.isclose(x['weight'],w,abs_tol=2e-15,rel_tol=0)for x,(g,w)in zip(mm,positive)),(r['taxon'],mm,positive);weights+=len(r['weights'])
 c=catch[r['taxon'],'landings'][2019];v=simple.get(r['taxon']);pp=0. if c==0 else c*v/9 if W.finite(v)else None;assert pp==r['simple_chain_ppr_tC']or math.isclose(pp,r['simple_chain_ppr_tC'],rel_tol=1e-12,abs_tol=1e-7)
stage_old={}
for r in W.records(old,'PPR','Allocation assumptions'):stage_old.setdefault(r['taxon'],{})[r['group']]=r['weight']
stage_exact={t:set(gw)==set(by[t]['group_names'])and all(by[t]['weights'][by[t]['group_names'].index(g)]==w for g,w in gw.items())for t,gw in stage_old.items()};stage_changed=[t for t,v in stage_exact.items()if not v]
assert set(stage_changed)=={'Dendrobranchiata','Miscellaneous marine crustaceans'},stage_changed
gs={(r['group'],r['scope'],r['method']):r['sppr']for r in W.records(b,'Selected model groups','Group SPPR')};coeff={};cn=0
for r in W.records(b,'PPR','Taxon SPPR'):
 rr=by[r['taxon']];vs=[gs[g,r['scope'],r['method']]for g in rr['group_names']];ex=round(math.fsum(w*v for w,v in zip(rr['weights'],vs)),6)if all(W.finite(v)for v in vs)else None
 assert ex==r['sppr'];coeff[r['taxon'],r['scope'],r['method']]=ex;cn+=1
checks=0;maxdiff=0.;unavailable=0;statuses=collections.Counter();contamination=[]
for r in W.records(b,'PPR','Annual'):
 statuses[str(r['status'])]+=1
 if r['unidentified']in ['method','zero']and'simple reference has no source decomposition'in str(r['status']):contamination.append(str(r))
 for y in range(1950,2020):
  terms=[];covered=[];allc=[]
  for t in taxa:
   c=catch[t,r['catch_basis']][y];v=coeff[t,r['scope'],r['method']]
   if flags[t]and r['unidentified']=='zero':v=0.
   if flags[t]and r['unidentified']=='simple':v=simple.get(t)
   allc.append(c)
   if W.finite(c)and W.finite(v):terms.append(c*v);covered.append(c)
  ex=(math.fsum(allc)if all(W.finite(c)for c in allc)else None)if r['metric']=='catch'else(math.fsum(terms if r['metric']=='ppr'else covered)if terms and W.numeric_status(r['status'])else None)
  actual=r[y]
  if ex is None:assert actual is None;unavailable+=1
  else:
   diff=abs(ex-actual);maxdiff=max(maxdiff,diff);assert math.isclose(ex,actual,abs_tol=1e-7,rel_tol=1e-12),(r['method'],r['scope'],y,ex,actual)
  checks+=1
assert not contamination
annual={(r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for s in ['Classic PPR','PPR']for r in W.records(b,s,'Annual')if r['metric']=='ppr'};npp={r['method']:r for r in W.records(b,'NPP','NPP')};rc=0
for r in W.records(b,'PPR–NPP','Ratios'):
 ar=annual[tuple(r[k]for k in ['model_id','scope','method','catch_basis','unidentified'])];nr=npp[r['npp_method']]
 for y in range(1950,2020):
  pv,nv=ar[y],nr[y];ex=100*pv/9/nv if W.finite(pv)and W.finite(nv)and nv>0 else None;actual=r[y];assert ex==actual or(ex is not None and actual is not None and math.isclose(ex,actual,abs_tol=1e-10,rel_tol=1e-12));rc+=1
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};bad=[];rowcounts={}
def col(a):
 n=0
 for c in re.match('[A-Z]+',a)[0]:n=n*26+ord(c)-64
 return n
with zipfile.ZipFile(R/'LME_038.xlsx')as z:
 for n in z.namelist():
  if re.fullmatch(r'xl/worksheets/sheet\d+.xml',n):
   x=X.fromstring(z.read(n));rows=x.findall('.//s:sheetData/s:row',ns);rowcounts[n]=len(rows);nums=[int(r.get('r'))for r in rows];assert nums==sorted(set(nums))
   for r in rows:
    cc=[col(c.get('r'))for c in r.findall('s:c',ns)]
    if cc!=sorted(set(cc)):bad.append([n,r.get('r')])
assert not bad,bad
result=dict(canonical_reader='W.read_book unmodified in fresh process; W.validate_region; regional.result_hash',workbook_sha256=W.sha(R/'LME_038.xlsx'),input_hash=W.input_hash(b),result_hash=regional.result_hash(b),validate_region_passed=True,protected_blocks_exact=protected,protected_diagnostics_exact=diag_protected,prior_stage_weights_unchanged_except_source_candidate_correction=stage_changed,all181_taxa_once=True,weakest_confidence_passed=True,weighted_coefficients_checked=cn,annual_cells_checked=checks,unavailable_annual_cells_explicit=unavailable,max_annual_wet_difference=maxdiff,npp_ratio_cells_checked=rc,status_contamination=[],all_XML_addresses_ascending_unique=True,worksheet_rows=rowcounts)
dump('canonical_reader_verification.json',result);dump('accepted_input_verification.json',dict(canonical_model_identical=True,workbook_protected_blocks=protected,diagnostics=diag_protected,prior_stage_weights_exact_by_taxon=stage_exact,protected_settings={k:o[k]==W.overview(old)[k]for k in ['selected_model_id','transfer_efficiency','npp_policy','production_eligible','catch_basis','taxon_detail_year']}))
dump('browser_expected_values.json',dict(unit_id='LME_038',selected_model_id=MID,selected_article_id='INDO-1999__LME_038',year=2019,basis='landings',scope='all',unidentified='method',taxon_filter='all',group_filter='none',taxa=181,mapped_taxa=181,production_eligible=False,classic_ppr_tC=math.fsum(r['simple_chain_ppr_tC']for r in a),annual_rows=[{**{k:r[k]for k in ['model_id','scope','method','catch_basis','unidentified','metric','status']},'value2019':r[2019]}for r in W.records(b,'PPR','Annual')],ratios2019=[{**{k:v for k,v in r.items()if not isinstance(k,int)},'value2019':r[2019]}for r in W.records(b,'PPR–NPP','Ratios')],expected_controls=['LME038 and exact selected derived model; mid1970s source','All/PP/inner,landings/catch/discards,method/zero/simple treatments','Classic2019 total177164712.36289582tC;39missing coefficients allzero2019','GE/Egestion OK and TE WARN stay provisional; historical symbolic status retained','Geography approximate A19–22%,B99–100%; two prose-bound scenarios'],shared_integration_pending=True,browser_verified=False))
with(Q/'final_book.pkl').open('wb')as f:pickle.dump(b,f)
print(json.dumps(result,indent=2))
