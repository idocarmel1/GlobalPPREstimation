"""Calculations from the regional workbook contract, independent of legacy directory names."""
import math
from collections import defaultdict
from workbooks import *

def set_setting(book,key,value):
    rr=book['Overview']['Settings'][1]
    for r in rr:
        if r[0]==key:r[1]=value;return
    rr.append([key,value])

def result_hash(book):
    return digest_tables([(s,k,h,r) for s in ['Classic PPR','PPR','PPR–NPP'] for k,(h,r) in book.get(s,{}).items() if k in ['Annual','Taxon SPPR','Ratios']])
def set_result_hash(book):set_setting(book,'calculation_result_sha256',result_hash(book))

def inputs(book):
    catch={}; identified={}; taxa=[]
    for r in records(book,'Catch','Catch'):
        t=r['taxon'];taxa.append(t);identified[t]=bool(r.get('unidentified'))
        key=(t,r['catch_basis'])
        if key in catch:raise ValueError(f'Duplicate catch row {key}')
        a=[r.get(y) for y in YEARS]
        if any(v is not None and (not finite(v) or v<0) for v in a):raise ValueError(f'Invalid catch: {key}')
        catch[key]=a
    simple={r['taxon']:r['sppr'] for r in records(book,'Classic PPR','Taxa')}
    return sorted(set(taxa)),catch,identified,simple

def taxon_detail(book):
    o=overview(book); year=int(o.get('taxon_detail_year',2019));basis=o.get('catch_basis','landings')
    _,catch,_,_=inputs(book); detail=[]
    for r in records(book,'PPR','Taxon SPPR'):
        c=catch.get((r['taxon'],basis),[None]*70)[year-1950];v=r['sppr']
        detail.append([r['model_id'],r['taxon'],r['scope'],r['method'],year,basis,c,v,c*v if finite(c) and finite(v) else None])
    book['PPR']['Taxon PPR inspected year']=(['model_id','taxon','scope','method','year','catch_basis','catch_tonnes','sppr','ppr_wet_tonnes'],detail)

def recalculate(book,path):
    o=overview(book);selected=o.get('selected_model_id'); old_inputs=o.get('calculation_input_sha256')
    if selected:
        model=Path(path).parent/str(o.get('model_path',''))
        if not model.is_file():raise ValueError('Selected model JSON missing')
        if o.get('results_model_sha256') and o['results_model_sha256']!=sha(model):raise ValueError('Model changed: run SPPR before PPR')
    taxa,catch,unidentified,simple=inputs(book)
    groups={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR') if r['model_id']==selected}
    mappings=defaultdict(list)
    for r in records(book,'PPR','Matching'):
        if r['model_id']!=selected:raise ValueError('Mapping belongs to another model; prepare matching for the selection')
        if r.get('group'):
            if not finite(r['weight']) or r['weight']<0:raise ValueError('Mapping weights must be nonnegative numbers')
            mappings[r['taxon']].append((r['group'],r['weight']))
    known={g for g,s,m in groups}
    for t,assign in mappings.items():
        if t not in taxa:raise ValueError(f'Mapped taxon absent from Catch: {t}')
        if len({g for g,w in assign})!=len(assign):raise ValueError(f'Duplicate group mapping for {t}')
        if any(g not in known for g,w in assign):raise ValueError(f'Unknown group for {t}')
        if not math.isclose(math.fsum(w for g,w in assign),1,abs_tol=1e-9,rel_tol=0):raise ValueError(f'Weights do not sum to one: {t}')
    coeff={};out=[]
    for scope,method in sorted({(s,m) for g,s,m in groups}):
        for t in taxa:
            assign=mappings.get(t,[]); vals=[groups.get((g,scope,method)) for g,w in assign]
            v=round(math.fsum(w*value for (g,w),value in zip(assign,vals)),6) if assign and all(finite(x) for x in vals) else None
            coeff[t,scope,method]=v;out.append([selected,t,scope,method,v])
    book['PPR']['Taxon SPPR']=(['model_id','taxon','scope','method','sppr'],out)
    oldstatus={(r[1],r[2]):r[6] for r in rows(book,'PPR','Annual') if r[5]=='ppr'}
    # An unfished negative group still invalidates the configuration.
    bad={(s,m) for (g,s,m),v in groups.items() if finite(v) and v<0}
    for is_simple,sheet in [(True,'Classic PPR'),(False,'PPR')]:
        annual=[]
        for scope,method in ([('all',SIMPLE)] if is_simple else sorted({(s,m) for g,s,m in groups})):
            status='ok' if is_simple else oldstatus.get((scope,method),'unavailable: method status has not been reviewed')
            if (scope,method) in bad:status='DIVERGED: negative source-group SPPR'
            for basis in ['landings','catch','discards']:
                for treatment in ['method','zero','simple']:
                    actual=status
                    if treatment=='simple' and scope!='all':actual='unavailable: simple reference has no source decomposition'
                    pp=[];covered=[];total=[]
                    for i in range(70):
                        pairs=[];allcatch=[]
                        for t in taxa:
                            c=catch.get((t,basis),[None]*70)[i];v=simple.get(t) if is_simple else coeff.get((t,scope,method))
                            if unidentified.get(t) and treatment=='zero':v=0.
                            if unidentified.get(t) and treatment=='simple':v=simple.get(t)
                            allcatch.append(c)
                            if finite(c) and finite(v):pairs.append((c,v))
                        total.append(math.fsum(allcatch) if allcatch and all(finite(c) for c in allcatch) else None)
                        pp.append(math.fsum(c*v for c,v in pairs) if pairs and actual=='ok' else None)
                        covered.append(math.fsum(c for c,v in pairs) if pairs and actual=='ok' else None)
                    for metric,values in [('ppr',pp),('catch',total),('covered_catch',covered)]:annual.append([selected if not is_simple else '',scope,method,basis,treatment,metric,actual,*values])
        book[sheet]['Annual']=(ANNUAL_HEADER,annual)
    den={r['method']:[r[y] for y in YEARS] for r in records(book,'NPP','NPP')};ratios=[]
    for r in rows(book,'Classic PPR','Annual')+rows(book,'PPR','Annual'):
        if r[5]!='ppr':continue
        for name,nn in den.items():ratios.append([*r[:5],name,*[100*p/9/n if finite(p) and finite(n) and n>0 else None for p,n in zip(r[7:],nn)]])
    book['PPR–NPP']['Ratios']=(['model_id','scope','method','catch_basis','unidentified','npp_method',*YEARS],ratios)
    set_setting(book,'results_model_id',selected)
    if selected:set_setting(book,'results_model_sha256',sha(Path(path).parent/o['model_path']))
    set_setting(book,'calculation_input_sha256',input_hash(book))
    set_setting(book,'calculation_status','recalculated; historical sensitivity bounds invalidated and require reassessment')
    taxon_detail(book);set_result_hash(book)

def comparison_tables(book):
    """Deduplicate common-taxon masks; Project.xlsx receives no taxon identities."""
    import numpy as np
    o=overview(book);unit=o['unit_id'];selected=o.get('selected_model_id') or ''
    taxa,catch,unidentified,simple=inputs(book); n=len(taxa)
    if not n:return [],[],[]
    ci={t:i for i,t in enumerate(taxa)}
    coeff={('all',SIMPLE):np.array([simple.get(t) if finite(simple.get(t)) else np.nan for t in taxa])}
    statuses={}
    for r in rows(book,'Classic PPR','Annual')+rows(book,'PPR','Annual'):
        if r[5]=='ppr':statuses[(r[1],r[2],r[4])]=r[6]
    for r in records(book,'PPR','Taxon SPPR'):
        key=(r['scope'],r['method']);coeff.setdefault(key,np.full(n,np.nan))[ci[r['taxon']]]=r['sppr'] if finite(r['sppr']) else np.nan
    matrices={basis:np.array([catch.get((t,basis),[None]*70) for t in taxa],dtype=float) for basis in ['landings','catch','discards']}
    matches=[]; series=[]; masks={}; emitted=set()
    for scope in ['all','inner','PP']:
        methods=sorted(m for s,m in coeff if s==scope)
        for treatment in ['method','zero','simple']:
            values={}
            for m in methods:
                if statuses.get((scope,m,treatment))!='ok':continue
                a=coeff[scope,m].copy()
                for i,t in enumerate(taxa):
                    if unidentified.get(t) and treatment=='zero':a[i]=0.
                    if unidentified.get(t) and treatment=='simple':a[i]=simple.get(t) if finite(simple.get(t)) else np.nan
                values[m]=a
            for i,a in enumerate(sorted(values)):
                for b in sorted(values)[i:]:
                    mask=np.isfinite(values[a])&np.isfinite(values[b]);mk=mask.tobytes()
                    mid=masks.setdefault(mk,f'cohort_{len(masks)+1}')
                    matches.append([unit,selected,scope,treatment,a,b,mid])
                    for basis,matrix in matrices.items():
                        for m in {a,b}:
                            key=(scope,treatment,basis,mid,m)
                            if key in emitted:continue
                            emitted.add(key); sub=matrix[mask];v=values[m][mask]
                            if len(v):
                                valid=np.isfinite(sub);p=np.where(valid,sub,0).T@v;c=np.where(valid,sub,0).sum(axis=0);present=valid.any(axis=0)
                                pp=[float(x) if ok else None for x,ok in zip(p,present)];cc=[float(x) if ok else None for x,ok in zip(c,present)]
                            else:pp=cc=[None]*70
                            series.append([unit,selected,scope,treatment,basis,mid,m,'ppr',*pp]);series.append([unit,selected,scope,treatment,basis,mid,m,'covered_catch',*cc])
    return matches,series,[]
