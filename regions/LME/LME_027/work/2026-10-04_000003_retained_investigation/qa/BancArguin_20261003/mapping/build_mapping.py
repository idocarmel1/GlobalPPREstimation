from pathlib import Path
import json,csv,math,hashlib,sys,copy,collections
P=Path(__file__).resolve().parent; ROOT=P.parents[4]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def num(x):
 try:v=float(x);return v if math.isfinite(v) else None
 except (TypeError,ValueError):return None
def records(sheet,table):
 h,rows=book[sheet][table];return [dict(zip(h,r)) for r in rows]
book=load(P/'frozen_workbook_evidence.json');membership=load(P/'membership_decisions.json')
catch=records('Catch','Catch');classic={r['taxon']:r for r in records('Classic PPR','Taxa')}
oldannual=records('Classic PPR','Annual');settings=dict(book['Overview']['Settings'][1]);years=list(range(1950,2020))
bases=sorted(set(x['catch_basis'] for x in catch));conforder=['High','Medium','Low','Very low','Unresolved']
assert len(catch)==len({(r['taxon'],r['catch_basis']) for r in catch})
assert all({r['taxon'] for r in catch if r['catch_basis']==b}=={r['taxon'] for r in membership} for b in bases)
save('universe_identity.json',{'region':'LME_027','source_workbook':'../../../LME_027.xlsx','source_workbook_sha256':hashlib.sha256((ROOT/'regions/LME_027/LME_027.xlsx').read_bytes()).hexdigest(),'source_model_selection_preserved':settings['selected_model_id'],'assessment_type':'candidate-specific, no model-selection adoption','taxon_count':512,'bases':bases,'years':[int(y) for y in years],'reference_year':settings['taxon_detail_year'],'reference_basis':settings['catch_basis'],'classic_method':'simple trophic chain','transfer_efficiency':settings['transfer_efficiency'],'carbon_divisor':9,'classic_coefficient_source':'Frozen Classic PPR / Taxa, exact taxon join. No model TL substitutions or missing-coefficient imputation.','zero_rule':'Recorded zero catch contributes zero annual PPR even with missing TL/coefficient.','unknown_rule':'Positive or missing catch with missing coefficient remains unknown.'})
rank={c:i for i,c in enumerate(conforder)}
outputs={};ref_summaries={};annual=[];reference_rows=[];weight_ledger=[];verification={}
xls=load(P.parent/'extraction/Table_1-f0424c0e.xls.cells.json')
source_cells={(c['row'],c['column']):c for c in xls['sheets'][0]['cells']}
xlsrow={int(c['value']):c['row'] for c in xls['sheets'][0]['cells'] if c['column']==1 and str(c['value']).isdigit() and 1<=int(c['value'])<=51}
sourcehash=xls['source_sha256']
s8_rows={int(row[0]):row for row in load(P/'source_supplement_tables.json')[9]['rows'][3:] if row[0].strip().isdigit()}
for variant in ['Base','M30','P30']:
 modelid=f'Guenette2014_BancArguin_{variant}_1991';v=load(P.parent/f'extraction/{variant}_vectors.json');gs={g['n']:g for g in v['groups']};mapping=[]
 for m in membership:
  d=copy.deepcopy(m);d['variant']=variant;d['model_id']=modelid;ids=d['candidate_ids'];cv=[];bv=[];candidates=[]
  for i in ids:
   raw=v['reported_total_catches'][str(i)];cv.append(num(raw));bv.append(num(gs[i]['biomass']))
   candidates.append({'seq':i,'group':gs[i]['name'],'source_catch_raw':raw,'source_catch':num(raw),'catch_field':f'Table1 N{xlsrow[i]} (reported Total catch)','catch_fleets_raw':v['landings'][str(i)],'catch_units':'t wet weight km-2 yr-1','catch_period':1991,'catch_basis':'source reported catch, three fleets; source states discard information unavailable','catch_missing':num(raw) is None,'catch_genuine_reported_zero':num(raw)==0,'catch_assumption':None,'source_catch_inherited_from_Base':variant!='Base','source_biomass_raw':gs[i]['biomass'],'source_biomass':num(gs[i]['biomass']),'biomass_field':f'Table1 D{xlsrow[i]}' if variant=='Base' else f'Table S8 {variant} biomass, exact group ID {i}','biomass_units':'t wet weight km-2','biomass_missing':num(gs[i]['biomass']) is None,'biomass_source_status':gs[i]['source_status'],'inclusion_reason':d['membership_reason']})
  for c in candidates:
   i=c['seq']
   c['source_catch_original_cell_value']=source_cells[(xlsrow[i],14)]['value']
   c['source_biomass_original_cell_value']=source_cells[(xlsrow[i],4)]['value'] if variant=='Base' else s8_rows[i][5 if variant=='M30' else 9]
   c['raw_value_note']='Vector raw strings have publisher HTML markup removed; original cell values above retain the source text/markup exactly.'
  catchvalid=all(x is not None and x>=0 for x in cv) and sum(cv)>0
  biomassvalid=all(x is not None and x>=0 for x in bv) and sum(bv)>0
  if len(ids)==1:rule='W1';ac='High';weights=[1.0];basis='no split';reason='Single reviewed candidate; complete weight is 1. This does not raise membership confidence.';total=None;rejected=None
  elif catchvalid:
   rule='W4';ac='Medium';total=sum(cv);weights=[x/total for x in cv];basis='source reported Total catch';reason='1991 source-model reported total catches normalized across every independently eligible candidate. Explicit reported zeros retained. Transfer to target taxon, LME, all years and catch bases is assumed; source has no discard observations.';rejected=None
  elif biomassvalid:
   rule='W9';ac='Medium';total=sum(bv);weights=[x/total for x in bv];basis='source biomass';reason='Complete candidate catch vector has zero total or a missing/invalid entry. Normalize complete nonnegative model biomass instead, assuming target caught composition/catchability proportional to those pools. This is not measured fishery composition.';rejected={'values':cv,'reason':'zero total' if all(x is not None for x in cv) and sum(cv)==0 else 'missing or invalid catch','total':sum(cv) if all(x is not None for x in cv) else None}
  else:raise ValueError(('No usable numerical allocation',variant,d['taxon'],cv,bv))
  for c,w in zip(candidates,weights):c['weight']=w;c['zero_weight']=w==0
  d.update({'candidates':candidates,'allocation_rule':rule,'allocation_confidence':ac,'allocation_reason':reason,'weight_basis':basis,'source_total':total,'rejected_catch_attempt':rejected,'allocation_assumed':rule!='W1','overall_confidence':max([d['membership_confidence'],ac],key=rank.get),'assumed':d['membership_assumed'] or rule!='W1','assumption_types':([d['membership_rule']] if d['membership_assumed'] else [])+([rule] if rule!='W1' else []),'source_catch_table_sha256':sourcehash,'proxy_source_variant_note':'Base reported catch and membership inherited; variant-specific biomass used only when W9 applies.' if variant!='Base' else 'Base source vectors.','allocation_search_ids':['SEARCH_STAGE_1','SEARCH_STAGE_2','SEARCH_STAGE_3','SEARCH_GEOGRAPHY'] if len(ids)>1 else [],'allocation_references':['SRC_T1'] if rule=='W4' else ['SRC_S8' if variant!='Base' else 'SRC_T1'] if rule=='W9' else [],'fixed_mapping_applicability':{'years':[1950,2019],'bases':bases,'region':'LME_027, broader than modeled Mauritanian shelf','time_transfer':'Source1991 composition proxy held fixed; not reconstruction of annual ecological composition.','basis_transfer':'Same mapping for landings, total catch and discards; source contains no discard data, and regional discard study shows young meagre can be caught.'},'prior_decision':{'same_candidate_mapping':'not available in assessed original sources','current_workbook_model_id':settings['selected_model_id'],'comparison':'Selected Northwest Africa1987 mapping is a different model; group/weight equality is not a scientifically valid baseline. No prior High labels inherited.'}})
  assert abs(sum(weights)-1)<1e-12 and all(x>=0 for x in weights)
  mapping.append(d)
 save(f'{variant}_mapping_evidence.json',{'schema_version':1,'model_id':modelid,'variant':variant,'region_id':'LME_027','adoption':'unadopted candidate mapping','mapping':mapping})
 fields=['model_id','taxon','group','seq','weight','confidence','membership_rule','membership_confidence','allocation_rule','allocation_confidence','assumed','evidence','explanation']
 with (P/f'{variant}_matching.csv').open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for d in mapping:
   for c in d['candidates']:w.writerow({'model_id':modelid,'taxon':d['taxon'],'group':c['group'],'seq':c['seq'],'weight':c['weight'],'confidence':d['overall_confidence'],'membership_rule':d['membership_rule'],'membership_confidence':d['membership_confidence'],'allocation_rule':d['allocation_rule'],'allocation_confidence':d['allocation_confidence'],'assumed':d['assumed'],'evidence':';'.join(d['membership_references']+d['allocation_references']),'explanation':d['membership_reason']+' '+d['allocation_reason']})
 outputs[variant]=mapping
 bytax={d['taxon']:d for d in mapping}
 for basis in bases:
  cr=[r for r in catch if r['catch_basis']==basis]
  for y in years:
   yr=[]
   for r in cr:
    d=bytax[r['taxon']];c=r[y];tl=classic.get(r['taxon'],{}).get('tl');s=classic.get(r['taxon'],{}).get('sppr');ppr=0.0 if c==0 else c*s/9 if finite(c) and finite(s) else None
    yr.append({'taxon':r['taxon'],'catch_t':c,'tl':tl,'classic_sppr':s,'simple_chain_ppr_tC':ppr,'missing_catch':not finite(c),'missing_tl':not finite(tl),'missing_coefficient':not finite(s),'annual_contribution_unknown':ppr is None,'genuine_zero_catch':c==0,'overall_confidence':d['overall_confidence'],'membership_rule':d['membership_rule'],'membership_confidence':d['membership_confidence'],'allocation_rule':d['allocation_rule'],'allocation_confidence':d['allocation_confidence'],'assumed':d['assumed'],'allocation_assumed':d['allocation_assumed'],'variant':variant,'model_id':modelid,'year':int(y),'basis':basis})
   ct=sum(r['catch_t'] for r in yr if finite(r['catch_t']));pt=sum(r['simple_chain_ppr_tC'] for r in yr if finite(r['simple_chain_ppr_tC']));unknown=[r['taxon'] for r in yr if r['annual_contribution_unknown']]
   summ={'model_id':modelid,'variant':variant,'year':int(y),'basis':basis,'taxa_n':len(yr),'catch_t':ct,'simple_chain_ppr_tC':pt,'known_PPR_subtotal':bool(unknown),'unknown_ppr_taxa':unknown,'missing_catch_n':sum(r['missing_catch'] for r in yr),'zero_catch_n':sum(r['genuine_zero_catch'] for r in yr),'missing_coefficient_n':sum(r['missing_coefficient'] for r in yr),'resolved_membership_allocation_taxa':512,'resolved_mapping_catch_pct':100.0 if ct>0 else None,'finite_GE_TE_coefficient_coverage':'computed separately by root from exact variant diagnostics; no inference from mapping coverage','assumption_dependent_catch_pct':100*sum(r['catch_t'] for r in yr if finite(r['catch_t']) and r['assumed'])/ct if ct else None,'allocation_assumed_catch_pct':100*sum(r['catch_t'] for r in yr if finite(r['catch_t']) and r['allocation_assumed'])/ct if ct else None}
   summ['confidence']=[]
   for co in conforder:
    q=[r for r in yr if r['overall_confidence']==co];cn=sum(r['catch_t'] for r in q if finite(r['catch_t']));pn=sum(r['simple_chain_ppr_tC'] for r in q if finite(r['simple_chain_ppr_tC']))
    summ['confidence'].append({'confidence':co,'taxa_n':len(q),'catch_t':cn,'catch_pct':100*cn/ct if ct else None,'simple_chain_ppr_tC':pn,'ppr_pct':100*pn/pt if pt else None})
   for component in ['membership','allocation']:
    rs=[]
    for rule,co in sorted({(r[component+'_rule'],r[component+'_confidence']) for r in yr}):
     q=[r for r in yr if r[component+'_rule']==rule and r[component+'_confidence']==co];pn=sum(r['simple_chain_ppr_tC'] for r in q if finite(r['simple_chain_ppr_tC']))
     rs.append({'rule':rule,'confidence':co,'taxa_n':len(q),'simple_chain_ppr_tC':pn,'ppr_pct':100*pn/pt if pt else None})
    summ[component+'_rules']=sorted(rs,key=lambda r:-r['simple_chain_ppr_tC'])
   annual.append(summ)
   if int(y)==int(settings['taxon_detail_year']):
    for r in yr:
     d=bytax[r['taxon']];r['mapped_groups_weights']='; '.join(f"{x['group']} ({x['weight']:.12%})" for x in d['candidates']);r['reason']=d['membership_reason']+' '+d['allocation_reason'];r['source_ids']=';'.join(d['membership_references']+d['allocation_references'])
    if basis==settings['catch_basis']:
     ref_summaries[variant]=summ;reference_rows.append((variant,sorted(yr,key=lambda r:(r['simple_chain_ppr_tC'] is None,-(r['simple_chain_ppr_tC'] or 0),r['taxon']))))
    save(f'{variant}_{basis}_{y}_taxa.json',sorted(yr,key=lambda r:(r['simple_chain_ppr_tC'] is None,-(r['simple_chain_ppr_tC'] or 0),r['taxon'])))
 verification[variant]={'labels_exact_match':len(bytax)==512 and set(bytax)=={r['taxon'] for r in catch},'unique_taxa':len(bytax)==len(mapping),'group_ids_names_match_source':all(c['group']==gs[c['seq']]['name'] for d in mapping for c in d['candidates']),'weight_sums_pass':all(abs(sum(c['weight'] for c in d['candidates'])-1)<1e-12 for d in mapping),'all_nonnegative_weights':all(c['weight']>=0 for d in mapping for c in d['candidates']),'zero_candidates_retained':sum(c['zero_weight'] for d in mapping for c in d['candidates']),'w9_taxa':[d['taxon'] for d in mapping if d['allocation_rule']=='W9'],'unresolved':[],'rule_tables_partition':all(abs(sum(x['ppr_pct'] for x in s[component+'_rules'])-100)<1e-8 for s in annual if s['variant']==variant for component in ['membership','allocation'] if s['simple_chain_ppr_tC']>0)}
save('coverage_all_years_bases.json',annual);save('reference_summaries.json',ref_summaries)
for variant,rs in reference_rows:
 with (P/f'{variant}_reference_taxa.csv').open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
 # Useful final 7-column appendix input, preserving numeric types.
 save(f'{variant}_appendix_rows.json',[[r['taxon'],r['tl'] if r['tl'] is not None else '?',r['catch_t'] if r['catch_t'] is not None else '?',r['simple_chain_ppr_tC'] if r['simple_chain_ppr_tC'] is not None else '?',r['mapped_groups_weights'],r['overall_confidence'],r['reason']+' ['+r['source_ids']+']'] for r in rs])
recon=[]
for s in annual:
 if s['variant']!='Base':continue
 old=[r for r in oldannual if r['catch_basis']==s['basis'] and r['metric']=='ppr' and r['scope']=='all' and r['unidentified']=='method']
 if len(old)==1:
  val=old[0].get(s['year']);actual=s['simple_chain_ppr_tC'];expected=val/9 if finite(val) else None
  recon.append({'year':s['year'],'basis':s['basis'],'computed_tC':actual,'saved_tC':expected,'difference_tC':actual-expected if expected is not None else None,'within_tolerance':expected is not None and math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-6),'contribution_complete':not s['known_PPR_subtotal']})
save('classic_reconciliation.json',recon)
verification['classic_annual_reconciliation_all_210']=len(recon)==210 and all(r['within_tolerance'] for r in recon)
verification['source_sheets_frozen']='Overview, Catch, Classic PPR, NPP snapshots in frozen_workbook_evidence.json; source workbook remains read-only'
save('mapping_verification.json',verification)
print(json.dumps({'reference':ref_summaries,'verification':verification},ensure_ascii=False,indent=2))
