"""Adopt exact audited coefficients and evidence-supported matches; expose coverage gaps."""
from pathlib import Path
import sys,json,csv,math,shutil,hashlib
import pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_050';MID='50_502013_Coastal_Kyoto_Inoue_(2013)';DEST=REG/'models'/MID;EV=DEST/'selected_pipeline';P=REG/'LME_050.xlsx'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting,recalculate,set_result_hash
b=read_book(P);assert overview(b)['selected_model_id']==MID
before=read_book(REG/'models/previous_results/LME_050_before_user_2013_selection_b4fdf13039c1.xlsx')
assert b['Catch']==before['Catch'] and b['NPP']==before['NPP']
def dump(name,x):(EV/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
g=pd.read_csv(EV/'loaded_groups.csv').fillna('')
b['Selected model groups']['Groups']=(list(g.columns),g.values.tolist())
options={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'};names=dict(zip(g.group_seq,g.group_name));coeff=[];health=[];annual=[]
for opt,method in options.items():
 label=opt.replace(' ','_');s=pd.read_csv(EV/f'SPPR_{label}.csv',index_col=0);s.columns=s.columns.astype(int)
 r=json.loads((EV/f'diagnose_sppr_{label}.json').read_text(encoding='utf8'))['direct_diagnose_sppr_return']
 assert r['status']=='WARN' and r['divergence']['status']=='OK' and r['balance']['status']=='OK' and (s.values>=0).all()
 health.append([MID,opt,r['status'],json.dumps(r,ensure_ascii=False),f'models/{MID}/selected_pipeline/diagnose_sppr_{label}.json'])
 for scope,cols in [('all',[39,40,41]),('inner',[39,40]),('PP',[39])]:
  for seq,value in s[cols].sum(axis=1).items():coeff.append([MID,names[seq],scope,method,float(value)])
  annual.append([MID,scope,method,'landings','method','ppr','ok',*[None]*70])
b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],coeff)
b['Diagnostics']['direct_diagnose_sppr']=(['model_id','TE_option','status','complete_return_json','evidence_path'],health)
source=json.loads((DEST/'model.json').read_text(encoding='utf8'))['group'];members={};member_rows=[]
for group in source:
 for name in group['taxon_descr'].split(';')[0].split(','):
  name=name.strip()
  if len(name.split())==2 and name[0].isupper() and not any(ch.isdigit() for ch in name):
   member_rows.append({'source_taxon':name,'group':group['group_name'],'group_seq':int(group['group_seq']),'evidence':'SOJ-2023 publisher supplement Table S3; representative list, not exhaustive'})
   if group['group_name']!='Tuna':members[name]=(group['group_name'],'explicit_member','high','Exact representative species in publisher Table S3.')
pd.DataFrame(member_rows).to_csv(EV/'source_members.csv',index=False)
for filename in ['sardine','oyster','stingray']:
 rec=json.loads((EV/'taxonomy'/f'{filename}.json').read_text());rec=rec[0] if isinstance(rec,list) else rec
 assert rec['scientificname'] in members
 group=members[rec['scientificname']][0]
 members[rec['valid_name']]=(group,'synonym','high',f"Source Table S3 {rec['scientificname']}; WoRMS AphiaID {rec['AphiaID']} explicitly resolves to {rec['valid_name']} ({rec['valid_AphiaID']}). {rec['url']}; retained response selected_pipeline/taxonomy/{filename}.json.")
catch=records(b,'Catch','Catch');taxa=sorted({r['taxon'] for r in catch});mapping=[];review=[]
missing_groups={'Gadus chalcogrammus':'No pollock or general cod group in the coastal Kyoto model.','Gadus macrocephalus':'No Pacific cod or general cod group.','Cololabis saira':'No saury group or documented assignment to another source group.','Clupea pallasii':'No Pacific herring group; source Round herring is Etrumeus micropus, not Clupea.','Marine fishes not identified':'Coarse unidentified fish span unrepresented whole-LME stocks; no supported closed candidate set or catch-composition split.','Sardinops sagax':'', 'Scomber':'Source Mackerel lists Scomber japonicus and printed S. austlasicus, but this genus aggregate lacks source-supported regional species composition; no blanket assignment.','Scomber australasicus':'Source prints Scomber austlasicus; likely spelling discrepancy retained, not silently repaired for matching.','Thunnus orientalis':'Main text identifies T. orientalis but S3 gives T. thynnus; source identity conflict unresolved.'}
for t in taxa:
 if t in members:
  group,rule,confidence,why=members[t];mapping.append([MID,t,group,1.,confidence,rule+'; Table S3',why])
 else:
  why=missing_groups.get(t,'No exact source membership or verified synonym; representative species do not establish exhaustive coverage of this taxon. A proxy or coarse split needs additional evidence.')
  mapping.append([MID,t,None,None,'unresolved','none',why])
 r=next(r for r in catch if r['taxon']==t and r['catch_basis']=='catch')
 review.append({'taxon':t,'group':mapping[-1][2],'confidence':mapping[-1][4],'catch_2019':r.get(2019),'catch_1950_2019':math.fsum(r[y] for y in YEARS if finite(r.get(y))),'explanation':mapping[-1][-1]})
b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],mapping)
pd.DataFrame(mapping,columns=b['PPR']['Matching'][0]).to_csv(EV/'source_supported_matching.csv',index=False)
pd.DataFrame(review).sort_values('catch_1950_2019',ascending=False).to_csv(EV/'all_taxa_membership_review.csv',index=False)
resolved={r[1] for r in mapping if r[2]};coverage=[]
for basis in ['landings','catch','discards']:
 rr=[r for r in catch if r['catch_basis']==basis]
 for year in YEARS:
  total=math.fsum(r[year] for r in rr if finite(r.get(year)));covered=math.fsum(r[year] for r in rr if r['taxon'] in resolved and finite(r.get(year)))
  coverage.append({'catch_basis':basis,'year':year,'available_total_tonnes':total,'supported_tonnes':covered,'supported_fraction':covered/total if total else None,'all_taxon_years_present':all(finite(r.get(year)) for r in rr)})
pd.DataFrame(coverage).to_csv(EV/'annual_mapping_coverage.csv',index=False)
summary={'selected_model':MID,'n_taxa':len(taxa),'resolved_exact_or_verified_synonym':len(resolved),'unresolved':len(taxa)-len(resolved),'mapping_rule':'Exact Table S3 members and three verified WoRMS synonym links only; no proxy stocks or unsupported coarse allocations','coverage_2019':[r for r in coverage if r['year']==2019],'top_unresolved_2019':sorted([r for r in review if r['group'] is None],key=lambda r:r['catch_2019'] or 0,reverse=True)[:20],'full_region_ppr_supported':False,'covered_subset_calculation':'Supported mapped catches only; unrepresented catch remains excluded/missing, never zeroed under method treatment','production_eligible':False}
dump('MAPPING_REVIEW.json',summary)
b['Diagnostics']['mapping_review']=(['model_id','status','record'],[[MID,'PARTIAL; complete regional PPR needs additional mapping evidence',json.dumps(summary,ensure_ascii=False)]])
b['Diagnostics']['source_review']=(['model_id','source_admission','loader','selection','comparison'],[[MID,'Unverified original year-specific diet reconstruction; one published matrix for both years','Exact original audited load retained: normalized diet, GS=0.2 defaults, missing catch/migration/routing completion, solved BA; all three method statuses WARN','User chose 2013 because newer','1985 remains a good comparison model; no claim of numerical inferiority']])
b['PPR']['Annual']=(ANNUAL_HEADER,annual)
set_setting(b,'results_model_id',MID);set_setting(b,'results_model_sha256',sha(DEST/'model.json'))
recalculate(b,P)
# Recalculation is the current covered-catch contract, not an extrapolation to unresolved taxa.
set_setting(b,'production_eligible',False)
set_setting(b,'calculation_status','2013 selected because newer; 3 SPPR configurations complete (WARN); exact/synonym mapping partial; annual values are supported-catch subtotals only; full-region model PPR pending additional evidence')
set_setting(b,'source_note',overview(b)['source_note']+' Whole-LME catch support is incomplete: annual model PPR covers only explicitly mapped taxa; production eligibility remains false. No proxy assignments or whole-LME extrapolation adopted.')
assert b['Catch']==before['Catch'] and b['NPP']==before['NPP'] and b['Classic PPR']['Taxa']==before['Classic PPR']['Taxa']
validate_region(b,P);write_book(P,b);validate_region(read_book(P),P)
pd.DataFrame(records(b,'PPR','Annual')).to_csv(EV/'supported_catch_annual_ppr.csv',index=False)
pd.DataFrame(records(b,'PPR–NPP','Ratios')).query('model_id == @MID').to_csv(EV/'supported_catch_ppr_npp_ratios.csv',index=False)
dump('PIPELINE_SUMMARY.json',summary|{'group_rows':len(g),'SPPR_rows':len(coeff),'options':list(options),'regional_validation':'PASS','original_Catch_NPP_ClassicTaxa_unchanged':True,'classic_previous_outputs':'Retained in pre-selection workbook; current calculate stage recomputes classic annual series and invalidates historical sensitivity bounds per project contract','regional_sha256':sha(P),'canonical_sha256':sha(DEST/'model.json')})
print(json.dumps({'n_taxa':len(taxa),'resolved':len(resolved),'coverage_2019':summary['coverage_2019'],'regional_validation':'PASS','production_eligible':False},indent=2))
