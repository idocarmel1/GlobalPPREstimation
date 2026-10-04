"""Candidate-only PPR arithmetic from frozen regional inputs and exact direct returns.

Does not write the regional workbook, selected results, Project or maps.
"""
from pathlib import Path
import csv,hashlib,json,math,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview,YEARS,sha
REGION=ROOT/'regions/LME_027'
book=read_book(REGION/'LME_027.xlsx');ov=overview(book)
catch=records(book,'Catch','Catch');classic=records(book,'Classic PPR','Taxa');npp=records(book,'NPP','NPP')
catch={(r['taxon'],r['catch_basis']):r for r in catch}
assert len(catch)==len(records(book,'Catch','Catch')),'Duplicate catch keys'
simple={r['taxon']:r for r in classic};taxa=sorted({t for t,b in catch})
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def csvsave(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def finite(v):return isinstance(v,(int,float)) and math.isfinite(v)
METHODS=['GE','TE','With Egestion'];SCOPES=['all','inner','PP'];BASES=['landings','catch','discards'];TREATMENTS=['method','zero','simple']
all_summaries={}
for variant in ['Base','M30','P30']:
    model_id=f'Guenette2014_BancArguin_{variant}_1991'
    modeldir=REGION/'models'/model_id;out=modeldir/'regional_assessment';out.mkdir(exist_ok=True)
    mapping_path=HERE/'mapping'/f'{variant}_mapping_evidence.json';mapping=load(mapping_path)
    rows={r['taxon']:r for r in mapping['mapping']}
    assert set(rows)==set(taxa)
    for r in rows.values():
        assert abs(math.fsum(c['weight'] for c in r['candidates'])-1)<1e-12
        assert all(c['weight']>=0 for c in r['candidates'])
    configs=[('published_source',None)]
    if variant=='Base':configs.append(('Base_runtime_PQ_approximation',HERE/'runtime/Base_runtime_PQ_approximation/group_coefficients.json'))
    for config,coefpath in configs:
        dest=out if config=='published_source' else HERE/'runtime'/config/'regional_assessment';dest.mkdir(exist_ok=True)
        gcoeff=load(coefpath) if coefpath else []
        gc={(r['group_seq'],r['scope'],r['method']):r['sppr'] for r in gcoeff}
        taxcoeff=[];lookup={}
        for scope in SCOPES:
            for method in METHODS:
                for taxon in taxa:
                    candidates=[c for c in rows[taxon]['candidates'] if c['weight']>0]
                    vals=[gc.get((c['seq'],scope,method)) for c in candidates]
                    coeff=math.fsum(c['weight']*v for c,v in zip(candidates,vals)) if candidates and all(finite(v) for v in vals) else None
                    lookup[taxon,scope,method]=coeff
                    taxcoeff.append({'model_id':model_id,'configuration':config,'taxon':taxon,'scope':scope,'method':method,'sppr_wet':coeff,'coefficient_available':finite(coeff),'overall_mapping_confidence':rows[taxon]['overall_confidence'],'assumed':rows[taxon]['assumed'],'production_eligible':False})
        annual=[];ratios=[]
        for scope in SCOPES:
            for method in METHODS:
                for basis in BASES:
                    for treatment in TREATMENTS:
                        for year in YEARS:
                            known=[];allcatch=[];supported=[];missing_mass=[];negative=[];unknown_catch=0;unknown_positive_n=0
                            for taxon in taxa:
                                cr=catch.get((taxon,basis),{});c=cr.get(year);s=lookup[taxon,scope,method]
                                if cr.get('unidentified') and treatment=='zero':s=0.
                                if cr.get('unidentified') and treatment=='simple':s=simple.get(taxon,{}).get('sppr') if scope=='all' else None
                                if not finite(c):unknown_catch+=1;continue
                                allcatch.append(c)
                                if finite(s):supported.append(c)
                                if c==0:known.append(0.);continue
                                if not finite(s):missing_mass.append(c);unknown_positive_n+=1;continue
                                v=c*s;known.append(v)
                                if v<0:negative.append(v)
                            full=unknown_catch==0 and unknown_positive_n==0
                            total=math.fsum(known) if known else None
                            totalcatch=math.fsum(allcatch) if unknown_catch==0 else None
                            # No source model result is claimed from all-zero or fallback-only support.
                            unavailable=config=='published_source' or (treatment=='simple' and scope!='all')
                            status=('NOT_RUN: published-source coefficients unavailable' if config=='published_source' else 'provisional experiment; direct diagnostic FAIL; not production eligible')
                            if treatment=='simple' and scope!='all':status='unavailable: simple reference has no source decomposition'
                            record={'model_id':model_id,'configuration':config,'scope':scope,'method':method,'catch_basis':basis,'unidentified_treatment':treatment,'year':year,'status':status,'catch_t':totalcatch,'covered_catch_t':math.fsum(supported) if not unavailable else None,'coverage_pct':100*math.fsum(supported)/totalcatch if totalcatch and not unavailable else None,'known_ppr_wet_t':None if unavailable else total,'ppr_wet_t':None if unavailable or not full else total,'ppr_tC':None if unavailable or not full else total/9,'missing_positive_catch_taxa_n':unknown_positive_n,'missing_catch_taxa_n':unknown_catch,'unsupported_catch_t':math.fsum(missing_mass),'negative_ppr_wet_t':math.fsum(negative),'production_eligible':False}
                            annual.append(record)
                            for nr in npp:
                                n=nr.get(year);p=record['ppr_tC']
                                ratios.append({'model_id':model_id,'configuration':config,'scope':scope,'method':method,'catch_basis':basis,'unidentified_treatment':treatment,'year':year,'npp_method':nr['method'],'npp_tC':n,'ppr_tC':p,'ppr_npp_pct':100*p/n if finite(p) and finite(n) and n>0 else None,'status':status,'production_eligible':False})
        csvsave(dest/'taxon_coefficients.csv',taxcoeff);csvsave(dest/'annual_PPR.csv',annual);csvsave(dest/'annual_PPR_NPP.csv',ratios)
        reference=[r for r in annual if r['year']==int(ov.get('taxon_detail_year',2019)) and r['catch_basis']==ov.get('catch_basis','landings') and r['scope']=='all' and r['unidentified_treatment']=='method']
        reference_ratios=[r for r in ratios if r['year']==int(ov.get('taxon_detail_year',2019)) and r['catch_basis']==ov.get('catch_basis','landings') and r['scope']=='all' and r['unidentified_treatment']=='method']
        meta={'model_id':model_id,'variant':variant,'configuration':config,'source_model_sha256':sha(modeldir/'model.json'),'regional_workbook_sha256':sha(REGION/'LME_027.xlsx'),'mapping_sha256':sha(mapping_path),'coefficient_file_sha256':sha(coefpath) if coefpath else None,'reference_year':2019,'reference_basis':ov.get('catch_basis','landings'),'reference_results':reference,'reference_ratios':reference_ratios,'production_eligible':False,'selection_changed':False,'precision':'Full saved direct coefficient precision, no six-decimal project taxon rounding; weighted sums evaluated with math.fsum','carbon_conversion':'Wet PPR divided by9 exactly once; ratio100×PPR_tC/NPP_tC','source_support':'M30/P30 missing diets prevent independent model results; no baseline coefficients inherited.' if variant!='Base' else 'Published-source Base fails constructor diet admission; numerical experiment retains known conflicting P/B zeros and rounded-ratio reconstruction, with FAIL diagnosis.','annual_rows':len(annual),'ratio_rows':len(ratios),'missing_policy':'Zero recorded catch contributes0 without inventing a coefficient. Positive catch with unavailable coefficient makes full PPR unknown. Unavailable published-source model results never replaced by an independent simple-chain fallback.'}
        save(dest/'assessment.json',meta);all_summaries[model_id+':'+config]=meta
    # Independent simple-chain results use existing authoritative coefficients only.
    independent=[]
    for basis in BASES:
        for year in YEARS:
            contrib=[];unavailable=[]
            for t in taxa:
                c=catch.get((t,basis),{}).get(year);s=simple.get(t,{}).get('sppr')
                if c==0:contrib.append(0.)
                elif finite(c) and finite(s):contrib.append(c*s/9)
                else:unavailable.append(t)
            p=math.fsum(contrib)
            for nr in npp:
                n=nr.get(year)
                independent.append({'model_id':model_id,'method':'independent simple trophic chain','catch_basis':basis,'year':year,'ppr_tC':p if not unavailable else None,'known_subtotal_tC':p,'missing_taxa_n':len(unavailable),'npp_method':nr['method'],'npp_tC':n,'ppr_npp_pct':100*p/n if not unavailable and finite(n) and n>0 else None,'model_dependent':False})
    csvsave(out/'independent_classic_PPR_NPP.csv',independent)
save(HERE/'regional_comparison.json',all_summaries)
print(json.dumps({k:{'reference_results':v['reference_results'],'reference_ratios':v['reference_ratios']} for k,v in all_summaries.items()},ensure_ascii=False))
