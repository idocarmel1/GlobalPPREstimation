"""Read-only independent candidate arithmetic audit from saved direct matrices.

Uses decimal source-column/weight arithmetic and vectorized annual products,
without importing or executing calculate_candidates.py or its result builder.
"""
from pathlib import Path
from decimal import Decimal,localcontext
import csv,json,math,hashlib,os,itertools
import numpy as np
P=Path(__file__).resolve().parent;H=P.parent;R=P.parents[2]
hashes={};errors=[];max_differences={};counts={};metadata_notes=[]
def track(path):
    path=Path(path);hashes[Path(os.path.relpath(path,P)).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest();return path
def load(path):return json.loads(track(path).read_text(encoding='utf8'))
def rows(path):
    with track(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def number(x):
    if x is None or x=='':return None
    x=float(x);return x if math.isfinite(x) else None
def finite(x):return x is not None and math.isfinite(x)
def same(label,actual,expected,key,rtol=5e-13,atol=1e-6):
    a=number(actual);e=number(expected)
    if a is None or e is None:
        if a is not None or e is not None:errors.append({'check':label,'key':key,'actual':a,'expected':e})
        return
    delta=abs(a-e);max_differences[label]=max(max_differences.get(label,0),delta)
    if not math.isclose(a,e,rel_tol=rtol,abs_tol=atol):errors.append({'check':label,'key':key,'actual':a,'expected':e,'difference':delta})
def table(book,sheet,name):
    header,body=book[sheet][name];return [dict(zip(header,r)) for r in body]
frozen=load(P/'frozen_workbook_evidence.json')
catch=table(frozen,'Catch','Catch');classic={r['taxon']:r['sppr'] for r in table(frozen,'Classic PPR','Taxa')}
npp={r['method']:r for r in table(frozen,'NPP','NPP')}
taxa=sorted({r['taxon'] for r in catch});years=list(range(1950,2020));bases=['catch','landings','discards'];scopes=['all','inner','PP'];methods=['GE','TE','With Egestion'];treatments=['method','zero','simple']
assert len(taxa)==512 and len(catch)==1536
catch_records={(r['taxon'],r['catch_basis']):r for r in catch}
C={b:np.array([[number(catch_records[t,b].get(y)) for y in years] for t in taxa],dtype=float) for b in bases}
unidentified=np.array([bool(catch_records[t,'catch']['unidentified']) for t in taxa])
assert all(bool(catch_records[t,b]['unidentified'])==bool(unidentified[i]) for i,t in enumerate(taxa) for b in bases)
simple=np.array([number(classic.get(t)) for t in taxa],dtype=float)
assert all(not (a[np.isfinite(a)]<0).any() for a in C.values())
runtime=H/'runtime/Base_runtime_PQ_approximation'
solutions=load(runtime/'direct_solutions.json');coeffrows=load(runtime/'group_coefficients.json');computational=load(runtime/'computational_input.json')
gsource={int(g['group_seq']):g for g in computational['group']};pp={i for i,g in gsource.items() if str(g.get('pp'))=='1'}
assert pp=={48,49,50},pp
direct={}
with localcontext() as ctx:
 ctx.prec=50
 for method,d in solutions.items():
    matrix=d['SPPR'];ids=matrix['index'];columns=matrix['columns'];assert len(ids)==len(set(ids)) and len(columns)==len(set(columns))
    assert set(columns)=={48,49,50,51,52}
    for scope in scopes:
        selected=[j for j,x in enumerate(columns) if scope=='all' or scope=='inner' and x!=52 or scope=='PP' and x in pp]
        for i,row in zip(ids,matrix['data']):
            values=[number(row[j]) for j in selected]
            direct[i,scope,method]=sum((Decimal(str(v)) for v in values),Decimal(0)) if all(v is not None for v in values) else None
 for r in coeffrows:same('direct_matrix_to_group',r['sppr'],direct[r['group_seq'],r['scope'],r['method']],str((r['group_seq'],r['scope'],r['method'])),rtol=1e-13,atol=1e-11)
counts['group_coefficients']=len(coeffrows)
configs=[(v,'published_source',R/f'models/Guenette2014_BancArguin_{v}_1991/regional_assessment') for v in ['Base','M30','P30']]+[('Base','Base_runtime_PQ_approximation',runtime/'regional_assessment')]
for variant,configuration,out in configs:
    mapping=load(P/f'{variant}_mapping_evidence.json')['mapping'];m={r['taxon']:r for r in mapping};assert set(m)==set(taxa)
    coeff={};published=configuration=='published_source'
    with localcontext() as ctx:
      ctx.prec=50
      for scope,method in itertools.product(scopes,methods):
        vector=[]
        for t in taxa:
            cs=[c for c in m[t]['candidates'] if c['weight']>0]
            vs=[None if published else direct[c['seq'],scope,method] for c in cs]
            weighted=None if any(v is None for v in vs) else sum((Decimal(str(c['weight']))*v for c,v in zip(cs,vs)),Decimal(0))
            coeff[t,scope,method]=None if weighted is None else float(weighted)
    tc=rows(out/'taxon_coefficients.csv');assert len(tc)==512*9
    assert len({(r['taxon'],r['scope'],r['method']) for r in tc})==len(tc)
    for r in tc:
        key=(r['taxon'],r['scope'],r['method']);e=coeff[key]
        same('taxon_full_precision_weighted_coefficient',r['sppr_wet'],e,str((configuration,*key)),rtol=1e-13,atol=1e-10)
        assert (r['coefficient_available']=='True')==finite(e)
        assert r['production_eligible']=='False' and r['overall_mapping_confidence']==m[r['taxon']]['overall_confidence']
    annual=rows(out/'annual_PPR.csv');assert len(annual)==5670
    index={(r['scope'],r['method'],r['catch_basis'],r['unidentified_treatment'],int(r['year'])):r for r in annual};assert len(index)==5670
    expectations={}
    for scope,method,basis,treatment in itertools.product(scopes,methods,bases,treatments):
        a=C[basis];s=np.array([coeff[t,scope,method] for t in taxa],dtype=float)
        if treatment=='zero':s[unidentified]=0
        elif treatment=='simple':s[unidentified]=simple[unidentified] if scope=='all' else np.nan
        c_ok=np.isfinite(a);s_ok=np.isfinite(s);positive=c_ok & (a>0)
        unknown_count=(~c_ok).sum(axis=0);unknown_positive=(positive & ~s_ok[:,None]).sum(axis=0)
        missing=np.where(positive & ~s_ok[:,None],a,0).sum(axis=0,dtype=np.longdouble)
        total_c=np.where(c_ok,a,0).sum(axis=0,dtype=np.longdouble)
        supported=np.where(c_ok & s_ok[:,None],a,0).sum(axis=0,dtype=np.longdouble)
        products=np.where(c_ok & s_ok[:,None],a*np.where(s_ok,s,0)[:,None],0)
        known=products.sum(axis=0,dtype=np.longdouble);negative=np.where(products<0,products,0).sum(axis=0,dtype=np.longdouble)
        unavailable=published or treatment=='simple' and scope!='all'
        for j,y in enumerate(years):
            key=(scope,method,basis,treatment,y);actual=index[key]
            full=unknown_count[j]==0 and unknown_positive[j]==0
            expected={'catch_t':None if unknown_count[j] else float(total_c[j]),'covered_catch_t':None if unavailable else float(supported[j]),'coverage_pct':None if unavailable or not total_c[j] else 100*float(supported[j]/total_c[j]),'known_ppr_wet_t':None if unavailable else float(known[j]),'ppr_wet_t':None if unavailable or not full else float(known[j]),'ppr_tC':None if unavailable or not full else float(known[j]/9),'missing_positive_catch_taxa_n':int(unknown_positive[j]),'missing_catch_taxa_n':int(unknown_count[j]),'unsupported_catch_t':float(missing[j]),'negative_ppr_wet_t':float(negative[j])}
            for field,e in expected.items():same('annual_'+field,actual[field],e,str((configuration,*key)))
            assert actual['production_eligible']=='False'
            expectations[key]=expected
    ratios=rows(out/'annual_PPR_NPP.csv');assert len(ratios)==5670*len(npp)
    assert len({(r['scope'],r['method'],r['catch_basis'],r['unidentified_treatment'],r['year'],r['npp_method']) for r in ratios})==len(ratios)
    unsupported_npp=0
    for r in ratios:
        key=(r['scope'],r['method'],r['catch_basis'],r['unidentified_treatment'],int(r['year']));p=expectations[key]['ppr_tC'];n=number(npp[r['npp_method']][int(r['year'])]);ratio=100*p/n if finite(p) and finite(n) and n>0 else None
        same('ratio_npp_source',r['npp_tC'],n,str((configuration,key,r['npp_method'])))
        same('ratio_ppr_carbon',r['ppr_tC'],p,str((configuration,key,r['npp_method'])))
        same('ratio_100_PPR_over_NPP',r['ppr_npp_pct'],ratio,str((configuration,key,r['npp_method'])),atol=1e-9)
        if n is None:unsupported_npp+=1;assert r['ppr_npp_pct']==''
    counts[f'{variant}:{configuration}']={'taxon_coefficients':len(tc),'annual_rows':len(annual),'NPP_ratio_rows':len(ratios),'unsupported_NPP_rows_stay_blank':unsupported_npp,'scope_method_basis_treatment_year_grid_complete':True}
    assessment=load(out/'assessment.json')
    if assessment['mapping_sha256']!=hashes[f'{variant}_mapping_evidence.json']:metadata_notes.append(f'{variant}:{configuration}: assessment mapping hash needs final refresh after mapping original-cell provenance addition.')
    if variant!='Base' or published:
        classic_rows=rows(out/'independent_classic_PPR_NPP.csv');assert len(classic_rows)==1260
        for r in classic_rows:
            y=int(r['year']);j=years.index(y);c=C[r['catch_basis']][:,j];supported=np.isfinite(c)&np.isfinite(simple);unknown=~np.isfinite(c)|((c!=0)&~np.isfinite(simple));known=np.where(supported,c*np.nan_to_num(simple,nan=0),0).sum(dtype=np.longdouble)/9
            p=None if unknown.any() else float(known);n=number(npp[r['npp_method']][y]);q=100*p/n if finite(p) and finite(n) and n>0 else None
            for field,e in [('known_subtotal_tC',float(known)),('ppr_tC',p),('missing_taxa_n',int(unknown.sum())),('npp_tC',n),('ppr_npp_pct',q)]:same('independent_classic_'+field,r[field],e,str((variant,r['catch_basis'],y,r['npp_method'])))
        counts[variant+':independent_classic_rows']=len(classic_rows)
changed=[p for p,h in hashes.items() if hashlib.sha256((P/p).read_bytes()).hexdigest()!=h]
if changed:errors.append({'check':'input_changed_during_audit','files':changed})
result={'schema_version':1,'complete':not errors,'checked_files_sha256':hashes,'checks':counts,'maximum_absolute_differences':max_differences,'errors':errors[:100],'error_count':len(errors),'metadata_refresh_notes':metadata_notes,'method':'Independent Decimal(50) basal-source/weight arithmetic from direct_solutions; NumPy vectorized catch products, complete support masks, one division by9 and ratio×100. No execution/import of calculate_candidates.py.','scope_definitions':{'all':[48,49,50,51,52],'inner':[48,49,50,51],'PP':[48,49,50]},'negative_values':'Preserved, not clipped. No negative source catch present; negative PPR contribution totals independently recomputed.','unavailable_policy':'Published-source candidate coefficients/results remain unavailable. Simple treatment has no inner/PP decomposition. Zero catch contributes zero without inventing a coefficient. Positive unsupported catches suppress full totals. Missing/nonpositive NPP never supplies a ratio.','limitations':'Arithmetic and current output-identity audit; scientific validity of direct SPPR remains governed by FAIL diagnostics. Metadata hashes flagged for root final refresh; no candidate adopted.','outputs_modified':'Only this audit report; candidate numeric results not regenerated.'}
(P/'candidate_arithmetic_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checked_files_sha256'},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
