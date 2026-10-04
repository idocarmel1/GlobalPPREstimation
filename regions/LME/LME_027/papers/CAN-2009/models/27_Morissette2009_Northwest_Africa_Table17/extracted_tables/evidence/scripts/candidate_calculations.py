"""Unadopted candidate mapping applied to the source-audited native companion."""
from pathlib import Path
import json,csv,math
C=Path(__file__).resolve().parents[1];OUT=C/'calculations'
def read(p):return json.loads((C/p).read_text(encoding='utf-8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def write(n,rows):
    with (OUT/n).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
snap=read('calculations/regional_input_snapshot.json');audit=read('mapping/taxon_audit.json')
coeff=read('diagnostics/group_coefficients.json');diag=read('diagnostics/direct_reports.json')
taxa={r['taxon']:r for r in audit};assert len(taxa)==len(audit)
classic={r['taxon']:r.get('sppr') for r in snap['classic_taxa']}
native=read('computational_inputs/official_EcoBase118.json')['group'];native_by_name={g['group_name']:int(g['group_seq']) for g in native}
lookup={(r['method'],r['scope'],r['group_seq']):r['sppr'] for r in coeff}
mapping={r['taxon']:[(native_by_name[g['group_name']],g['weight']) for g in r['groups']] for r in audit}
for tax,groups in mapping.items():assert abs(math.fsum(v for _,v in groups)-1)<1e-12,tax
annual=[];details=[];ratios=[];methods=('GE','TE','With Egestion')
for method in methods:
    for scope in ('all','inner','PP'):
        for basis in ('landings','catch','discards'):
            catches=[r for r in snap['catch'] if r['catch_basis']==basis]
            for treatment in ('method','zero','simple'):
                for year in range(1950,2020):
                    values=[];unknown=[];covered=[]
                    for r in catches:
                        tax=r['taxon'];catch=r.get(str(year))
                        coefficient=math.fsum(w*lookup[(method,scope,g)] for g,w in mapping[tax])
                        missing_reason=None
                        if r.get('unidentified') and treatment=='zero':coefficient=0.
                        elif r.get('unidentified') and treatment=='simple':
                            if scope=='all':coefficient=classic.get(tax)
                            else:coefficient=None;missing_reason='Independent simple-chain PPR has no source decomposition'
                        if not finite(catch):ppr=None;missing_reason='Missing catch'
                        elif catch==0:ppr=0.
                        elif not finite(coefficient):ppr=None;missing_reason=missing_reason or 'Missing coefficient'
                        else:ppr=catch*coefficient/9.
                        if ppr is None:unknown.append(tax)
                        else:values.append(ppr);covered.append(catch)
                        if year==2019 and basis=='landings' and treatment=='method':
                            details.append({'taxon':tax,'method':method,'scope':scope,'catch_t':catch,'sppr_wet':coefficient,'ppr_tC':ppr,
                                            'mapping_confidence':taxa[tax]['overall_confidence'],
                                            'status':'Unadopted diagnostic calculation; same researcher-disqualified model'})
                    total=math.fsum(values)
                    row={'year':year,'method':method,'scope':scope,'catch_basis':basis,'unidentified':treatment,
                         'known_ppr_tC':total,'total_ppr_tC':None if unknown else total,'covered_catch_t':math.fsum(covered),
                         'unknown_taxa':len(unknown),'diagnostic_status':diag[method]['status'],'production_eligible':False,
                         'status':'Unadopted diagnostic calculation; EcoBase118 disqualification retained'}
                    annual.append(row)
                    for n in snap['npp']:
                        v=n.get(str(year))
                        ratios.append({'year':year,'method':method,'scope':scope,'catch_basis':basis,'unidentified':treatment,
                                       'npp_method':n['method'],'npp_tC':v,'ppr_tC':row['total_ppr_tC'],
                                       'ppr_npp_pct':100*total/v if not unknown and finite(v) and v>0 else None,
                                       'production_eligible':False,'status':row['status']})
write('candidate_model_annual.csv',annual);write('candidate_model_npp_ratios.csv',ratios);write('candidate_reference_taxon_ppr.csv',details)
exposure=[]
for method in methods:
    selected=[r for r in details if r['method']==method and r['scope']=='all']
    total=math.fsum(r['ppr_tC'] for r in selected if r['ppr_tC'] is not None)
    weak=math.fsum(r['ppr_tC'] for r in selected if r['mapping_confidence']=='Very low' and r['ppr_tC'] is not None)
    exposure.append({'method':method,'total_2019_landings_ppr_tC':total,'very_low_ppr_pct':100*weak/total,
                     'largest_taxa':sorted(selected,key=lambda x:x['ppr_tC'] or 0,reverse=True)[:10]})
save('candidate_calculation_summary.json',{'variant':'official_EcoBase118_same_model_with_candidate_mappings',
     'reference_year':2019,'catch_basis':'landings','annual_rows':len(annual),'ratio_rows':len(ratios),'taxon_detail_rows':len(details),
     'methods':exposure,'production_eligible':False,'selected_model_changed':False,
     'limits':'Numbers are a local diagnostic scenario, not an approved replacement. Same EcoBase118 native coefficients; fresh candidate mappings and explicit model-catch proportions. Paper-only reconstruction lacks required inputs and has no coefficients. Native group IDs joined by exact group names against Table17 mapping IDs.'})
print(json.dumps({'annual_rows':len(annual),'ratio_rows':len(ratios),'totals':[{k:v for k,v in e.items() if k!='largest_taxa'} for e in exposure]}))
