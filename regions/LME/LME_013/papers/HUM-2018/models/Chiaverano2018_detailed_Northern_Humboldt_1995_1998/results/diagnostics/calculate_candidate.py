"""Candidate-only regional arithmetic from retained coefficients and mapping.

No calculator run or active workbook write. All returned FAIL arithmetic stays
ineligible. Wet-weight PPR is divided by nine once to carbon; NPP is already C.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, math, os
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
YEARS=range(1950,2020)
SCOPES=('PP','inner','all')
TREATMENTS=('method','zero','simple')
METHODS=('GE','TE','With Egestion')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)
def number(v):
    try: v=float(v)
    except (TypeError,ValueError): return None
    return v if math.isfinite(v) else None
def namespaced(rows):
    return {r['taxon']:r for r in rows}

def main(mapping_path):
    snapshot_path=HERE.parent/'mapping/regional_arithmetic_snapshot.json'
    snapshot=json.loads(snapshot_path.read_text(encoding='utf-8'))
    mapping=json.loads(mapping_path.read_text(encoding='utf-8'))
    mapping_rows=mapping['taxa'] if isinstance(mapping,dict) else mapping
    mapping_by_taxon=namespaced(mapping_rows)
    universe=json.loads((HERE.parent/'mapping/catch_universe.json').read_text(encoding='utf-8'))
    classic={r['taxon']:number(r.get('sppr',r.get('classic_sppr_wet'))) for r in snapshot['classic_taxa']}
    classic_universe={r['taxon']:r for r in universe['taxa']}
    for t,r in classic_universe.items():
        if not finite(classic.get(t)):
            classic[t]=number(r.get('classic_sppr_wet',r.get('sppr_wet',r.get('classic_sppr'))))
    method_summaries=json.loads((HERE/'methods_summary.json').read_text(encoding='utf-8'))
    coeff={}
    coeff_path=HERE/'group_scope_coefficients.csv'
    if coeff_path.exists() and coeff_path.stat().st_size>2:
        with coeff_path.open(encoding='utf-8',newline='') as f:
            for r in csv.DictReader(f):
                coeff[(r['method'],r['scope'],int(r['group_id']))]=number(r['sppr_wet'])
    catch_rows=snapshot['catch']
    taxa=sorted(set(r['taxon'] for r in catch_rows))
    bases=sorted(set(r['catch_basis'] for r in catch_rows))
    catch={(r['taxon'],r['catch_basis']):r for r in catch_rows}
    assert len(catch)==len(catch_rows),'Duplicate taxon/basis keys'
    missing_mappings=[t for t in taxa if t not in mapping_by_taxon]
    if missing_mappings: raise ValueError(f'Missing candidate mappings: {missing_mappings}')
    mapped_coeff={};membership={}
    for t in taxa:
        r=mapping_by_taxon[t]
        candidates=r.get('candidates',r.get('assignments',[]))
        positive=[c for c in candidates if finite(c.get('weight')) and c['weight']>0]
        sum_weights=sum(c['weight'] for c in candidates if finite(c.get('weight')))
        resolved=bool(positive) and math.isclose(sum_weights,1.0,rel_tol=1e-10,abs_tol=1e-12)
        membership[t]={'resolved':resolved,'sum_weights':sum_weights,'n_candidates':len(candidates),
                       'confidence':r.get('overall_confidence'),
                       'assumed':r.get('assumed',True),'unidentified':bool(catch.get((t,bases[0]),{}).get('unidentified'))}
        for method in METHODS:
            for scope in SCOPES:
                vals=[coeff.get((method,scope,int(c['group_id']))) for c in positive] if resolved else []
                value=sum(c['weight']*v for c,v in zip(positive,vals)) if vals and all(finite(v) for v in vals) else None
                mapped_coeff[(t,method,scope)]=value
    taxon_coeff=[{'taxon':t,'method':m,'scope':s,'sppr_wet':mapped_coeff[(t,m,s)],
                 'coefficient_available':finite(mapped_coeff[(t,m,s)]),'classic_sppr_wet':classic.get(t),
                 **membership[t],'production_eligible':False} for t in taxa for m in METHODS for s in SCOPES]
    save(HERE/'taxon_scope_coefficients.json',taxon_coeff)
    annual=[];reference=[];reconciliation=[]
    detail_fields=['year','taxon','method','scope','catch_basis','unidentified_treatment','recorded_unidentified',
         'catch_t_wet','coefficient_wet','coefficient_available','contribution_available','ppr_t_wet_equivalent',
         'ppr_tC','status','production_eligible','mapping_resolved','mapping_confidence','assumed']
    with gzip.open(HERE/'candidate_taxon_annual.csv.gz','wt',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=detail_fields);writer.writeheader()
        for method in METHODS:
            diagnosed=method_summaries.get(method,{})
            grade=diagnosed.get('overall_status')
            executed=diagnosed.get('execution_status')=='RETURNED'
            for scope in SCOPES:
                for basis in bases:
                    for treatment in TREATMENTS:
                        unsupported=treatment=='simple' and scope!='all'
                        for year in YEARS:
                            rows=[];wet=[];catches=[];covered=[];positive_unknown=[];missing_catch=[];negative=[]
                            for t in taxa:
                                source=catch.get((t,basis),{})
                                ct=number(source.get(str(year)))
                                unidentified=bool(source.get('unidentified'))
                                v=mapped_coeff.get((t,method,scope))
                                if unidentified and treatment=='zero': v=0.0
                                if unidentified and treatment=='simple': v=classic.get(t)
                                if unsupported:
                                    contribution=None;status='unavailable: simple reference has no source decomposition'
                                elif not executed:
                                    contribution=None;status='unavailable: direct method '+diagnosed.get('execution_status','NOT_RUN')
                                elif not finite(ct):
                                    contribution=None;status='unavailable: catch missing';missing_catch.append(t)
                                elif ct==0:
                                    contribution=0.0;status='arithmetic-only candidate; diagnostic '+str(grade)
                                elif finite(v):
                                    contribution=ct*v;status='arithmetic-only candidate; diagnostic '+str(grade)
                                else:
                                    contribution=None;status='unavailable: positive catch coefficient unknown';positive_unknown.append(t)
                                carbon=contribution/9 if finite(contribution) else None
                                r={'year':year,'taxon':t,'method':method,'scope':scope,'catch_basis':basis,
                                   'unidentified_treatment':treatment,'recorded_unidentified':unidentified,
                                   'catch_t_wet':ct,'coefficient_wet':v,'coefficient_available':finite(v),
                                   'contribution_available':finite(contribution),'ppr_t_wet_equivalent':contribution,
                                   'ppr_tC':carbon,'status':status,'production_eligible':False,
                                   'mapping_resolved':membership[t]['resolved'],'mapping_confidence':membership[t]['confidence'],
                                   'assumed':membership[t]['assumed']}
                                writer.writerow(r)
                                if year==2019: reference.append(r)
                                rows.append(r)
                                if finite(contribution): wet.append(contribution)
                                if finite(ct):
                                    catches.append(ct)
                                    if finite(contribution): covered.append(ct)
                                if finite(v) and v<0: negative.append(t)
                            subtotal=math.fsum(wet)/9 if executed and not unsupported else None
                            complete=executed and not unsupported and not positive_unknown and not missing_catch
                            total=subtotal if complete else None
                            annual.append({'year':year,'method':method,'scope':scope,'catch_basis':basis,
                                'unidentified_treatment':treatment,'diagnostic_grade':grade,
                                'status':'unavailable: simple reference has no source decomposition' if unsupported else ('arithmetic-only candidate; diagnostic '+str(grade) if executed else 'unavailable: '+diagnosed.get('execution_status','NOT_RUN')),
                                'ppr_tC':total,'known_ppr_subtotal_tC':subtotal,
                                'catch_t_wet':math.fsum(catches) if not missing_catch else None,
                                'covered_catch_t_wet':math.fsum(covered),'positive_unknown_taxa_count':len(positive_unknown),
                                'missing_catch_taxa_count':len(missing_catch),'negative_coefficient_taxa_count':len(negative),
                                'contribution_complete':complete,'production_eligible':False,
                                'carbon_conversion':'sum(catch_t_wet*SPPR_wet)/9 exactly once'})
                            if complete:
                                source_sum=math.fsum(r['ppr_tC'] for r in rows)
                                reconciliation.append({'method':method,'scope':scope,'basis':basis,'treatment':treatment,'year':year,
                                    'taxon_sum_tC':source_sum,'annual_total_tC':total,
                                    'reconciles':math.isclose(source_sum,total,rel_tol=1e-12,abs_tol=1e-7)})
    def write_csv(name,rows):
        with (HERE/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
    write_csv('candidate_reference_2019_taxa.csv',reference)
    write_csv('candidate_annual_totals.csv',annual)
    ratios=[]
    for r in annual:
        for n in snapshot['npp']:
            denominator=number(n.get(str(r['year'])))
            numerator=r['ppr_tC']
            ratios.append({k:r[k] for k in ['year','method','scope','catch_basis','unidentified_treatment','diagnostic_grade','production_eligible']}|
               {'npp_method':n['method'],'npp_tC_year':denominator,'ppr_tC_year':numerator,
                'ppr_npp_ratio':numerator/denominator if finite(numerator) and finite(denominator) and denominator>0 else None,
                'availability':'arithmetic-only ineligible candidate ratio' if finite(numerator) and finite(denominator) and denominator>0 else 'unavailable numerator or annual NPP',
                'missing_npp_proxy':'none; unsupported years remain unknown'})
    write_csv('candidate_annual_npp_ratios.csv',ratios)
    save(HERE/'candidate_arithmetic_reconciliation.json',reconciliation)
    ref=[r for r in annual if r['year']==2019 and r['catch_basis']=='landings' and r['unidentified_treatment']=='method']
    save(HERE/'candidate_calculation_manifest.json',{'schema_version':1,'region_id':'LME_013',
        'candidate_id':'HUM2018_20261003_detailed','timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'mapping_path':os.path.relpath(mapping_path,HERE).replace('\\','/'),'mapping_sha256':sha(mapping_path),
        'catch_classic_npp_snapshot_sha256':sha(snapshot_path),'coefficient_sha256':sha(coeff_path) if coeff_path.exists() else None,
        'direct_methods_summary_sha256':sha(HERE/'methods_summary.json'),'script_sha256':sha(Path(__file__)),
        'methods':list(METHODS),'scopes':list(SCOPES),'catch_bases':bases,'unidentified_treatments':list(TREATMENTS),
        'years':[1950,2019],'taxa':len(taxa),'annual_rows':len(annual),'npp_ratio_rows':len(ratios),
        'taxon_annual_rows':len(taxa)*len(annual),'reference2019_taxon_rows':len(reference),
        'all_reconciliations_passed':all(r['reconciles'] for r in reconciliation),'production_eligible':False,
        'reference_2019_landings_method_totals':ref,
        'limitations':['Fixed1995–1998 source-candidate coefficients extended over1950–2019 catch; no annual ecosystem reconstruction.',
                       'FAIL coefficients retained for arithmetic-only investigation; no active adoption or publication.',
                       'Mapping assumptions, geographic transfer and unidentified treatments remain explicit.',
                       'Missing coefficients remain unknown, including recorded zero-catch rows; recorded zero annual contribution is zero.',
                       'ScopePP/inner unidentified=simple unavailable because classic has no source decomposition.',
                       'Regional NPP retained from independent snapshot; absent annual values have no substitute.']})
    print(json.dumps({'annual_rows':len(annual),'taxon_annual_rows':len(taxa)*len(annual),
                      'npp_ratio_rows':len(ratios),'reconciliations':all(r['reconciles'] for r in reconciliation)}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mapping',type=Path,required=True)
    main(p.parse_args().mapping)
