from pathlib import Path
import sys,json,math,shutil,csv,hashlib
import pandas as pd
ROOT=Path.cwd();ARCH=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,result_hash

def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
for rid in ['LME_013','LME_037']:
 R=ROOT/'regions'/rid;p=R/f'{rid}.xlsx';D=R/'models/regional_ge_integration_20260928';b=read_book(p);o=overview(b);mid=o['selected_model_id'];source=R/o['model_path'];before=sha(p);canon=sha(source)
 assert not records(b,'PPR','Matching') and not records(b,'PPR','Annual'),'Expected pending workbook only'
 ver=json.loads((D/'runtime_verification.json').read_text(encoding='utf-8'));assert ver['canonical_sha256']==canon
 assert all(x['status']=='WARN' and x['all_source_coefficients_finite_nonnegative'] for x in ver['methods'])
 backup=D/f'{rid}_before_integration_{before[:12]}.xlsx';shutil.copy2(p,backup)
 keep={('Catch','Catch'):digest_tables(b['Catch']['Catch']),('Classic PPR','Taxa'):digest_tables(b['Classic PPR']['Taxa'])};npp=digest_tables(list(b['NPP'].items()))
 g=pd.read_csv(D/'loaded_groups.csv').where(pd.notnull(pd.read_csv(D/'loaded_groups.csv')),None)
 b['Selected model groups']['Groups']=(list(g.columns),g.values.tolist())
 groupdict={int(row[0]):row[1] for row in g.values.tolist()};sp=[]
 for scope in ['all','inner','PP']:
  t=pd.read_csv(D/f'group_sppr_{scope}.csv')
  for row in t.to_dict('records'):
   for method in ['new_GE','new_TE_EEfix','new_WithEgestion']:sp.append([mid,row['group_name'],scope,method,row[method]])
 b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],sp)
 taxa=sorted({r['taxon'] for r in records(b,'Catch','Catch')});decisions=[];maps=[];members={}
 if rid=='LME_013':
  for tax in ['Brama australis','Strangomera bentincki','Engraulis ringens','Sprattus fuegensis']:members[tax]=6
  for tax,seq in [('Seriolella punctata',7),('Micromesistius australis',10),('Genypterus blacodes',11),('Zearaja chilensis',12),('Merluccius australis',13),('Otaria byronia',14)]:members[tax]=seq
  evidence='papers/HUM-2026/extracted/work/page-04.txt; Neira et al. 2026 Table 1 (PDF p4). Exact named source members only.'
  caveat='Conditional Chilean Patagonia 1980 coefficients applied to exact member catches in Humboldt LME. Geographic mismatch remains unquantified. Retained runtime normalizes Sea lions diet1.002, solves residual BA for unknown BA, defaults consumer GS0.2/migration0, detritus B1 and routing; these are computational assumptions, not recovered observations. All three direct configurations WARN, strict computational balance true. Historical ecosystem unchanged across catch years.'
  for tax in taxa:
   seq=members.get(tax);reason='Exact source Table1 membership.' if seq else 'No exact unambiguous source member match; representative group names do not establish membership or regional species composition.'
   if tax=='Macruronus magellanicus':reason='Named species occurs in juvenile and adult groups; no independently supported regional catch age allocation. Source model fleet mixture is not assumed to represent LME catch.'
   if tax=='Seriolella caerulea':reason='Source Table1 prints Seriolella cearulea; spelling requires an explicit taxonomic verification before synonym admission.'
   if tax in ['Marine fishes not identified','Marine finfishes not identified','Clupeidae','Scombridae','Marine pelagic fishes not identified']:reason='Coarse label spans unsupported taxa; no closed membership set or supported apportionment.'
   decisions.append({'taxon':tax,'group':groupdict.get(seq),'weight':1. if seq else None,'confidence':'direct source' if seq else 'unresolved','evidence':evidence,'explanation':reason})
 else:
  # Direct source family labels or explicitly listed genera, only where the source offers a unique group.
  exact={'Dasyatidae':3,'Engraulidae':6,'Synodontidae':13,'Sciaenidae':13,'Sparidae':13,'Trichiuridae':13,'Chirocentridae':13,'Polynemidae':13,'Megalopidae':13,'Leiognathidae':14,'Gerreidae':14,'Sillaginidae':14,'Scolopsis taenioptera':14,'Serranidae':16,'Lethrinidae':16,'Lutjanidae':16,'Muraenidae':16,'Apogonidae':17,'Chaetodontidae':17,'Gobiidae':17,'Holocentridae':17,'Labridae':17,'Scaridae':18,'Siganidae':19,'Caesionidae':20,'Scyphozoa':21,'Hydrozoa':21,'Cubozoa':21,'Octopodidae':22,'Loliginidae':23,'Sepioteuthis lessoniana':23,'Portunidae':24,'Penaeidae':25,'Sergestidae':25}
  genus={'Aetobatus':3,'Sphyraena':15,'Caranx':15,'Carangoides':15,'Scomberoides':15,'Uroteuthis':23}
  # Upeneus and Nemipterus occur in source demersal group14 and family-level reef group17: retain unresolved.
  evidence='models/Bacalso2026_Visayan_Sea_1997_baseline/extracted_tables/taxonomy.csv; recovered Bacalso et al. 2023 Table1. Representative memberships are not exhaustive.'
  caveat='Conditional Visayan Sea1997 baseline applied to supported LME037 catch. Geographic fraction is unknown. Exact documented zero-import input and loader defaults retained: unknown diet imports0, living BA0, GS0.2, migration0, single-detritus routing, detritus EE0.44->1, detritus BA682.68614643. Diet unnormalized with DC_tol0.0021. GE/TE/Egestion WARN with strict input/budget balance false; TE Seabirds near-singular. These are conditional mapped-catch subtotals, not whole-region or source-balanced ecosystem claims.'
  for tax in taxa:
   seq=exact.get(tax) or genus.get(tax.split()[0]);reason='Exact source higher-taxon label or explicitly listed genus in one unique source group.' if seq else 'No unique direct source membership; representative lists do not establish all members, habitat/size assignment or composite shares.'
   if tax.split()[0] in ['Sardinella','Rastrelliger','Decapterus','Scomberomorus','Selaroides','Atule']:reason='Source pool includes immature/adult stages; regional catch stage weights absent, or taxon is not an explicitly listed representative. No source-model stage mixture imposed on LME catches.'
   if tax.split()[0] in ['Nemipterus','Upeneus'] or tax in ['Nemipteridae','Mullidae','Pomacentridae']:reason='Membership overlaps demersal and reef or multiple reef groups. Source habitat/size or species fractions unavailable for regional catch.'
   if tax in ['Marine fishes not identified','Marine finfishes not identified','Miscellaneous aquatic invertebrates','Mollusca','Carangidae','Scombridae']:reason='Composite includes multiple unsupported source pools or taxa; no complete membership and allocation evidence.'
   decisions.append({'taxon':tax,'group':groupdict.get(seq),'weight':1. if seq else None,'confidence':'source taxon containment' if seq else 'unresolved','evidence':evidence,'explanation':reason})
 headers=['model_id','taxon','group','weight','confidence','evidence','explanation']
 for d in decisions:maps.append([mid,*[d[k] for k in headers[1:]]])
 b['PPR']['Matching']=(headers,maps)
 health=json.loads((D/'health.json').read_text(encoding='utf-8'));hh=list(health[0]);b['Diagnostics']['model_health']=(hh,[[x.get(k) for k in hh] for x in health])
 b['Diagnostics']['run_notes']=(['topic','note','status'],[['Scientific admission',caveat,'conditional WARN'],['Provenance','models/regional_ge_integration_20260928/runtime_verification.json; computational_state.json; source-preserving input and constructor','verified'],['Mapping','Conservative direct source membership; all missing labels retained unresolved. No proxy stocks or invented allocation weights.','partial'],['Sensitivity','Historical discard sensitivity unavailable after current calculations; no new Monte Carlo performed.','unavailable']])
 b['PPR']['Annual']=(ANNUAL_HEADER,[[mid,scope,method,'landings','method','ppr','ok',*[None]*70] for scope in ['all','inner','PP'] for method in ['new_GE','new_TE_EEfix','new_WithEgestion']])
 set_setting(b,'results_model_id',mid);set_setting(b,'results_model_sha256',canon)
 staged=D/'staged_inputs.xlsx';write_book(staged,b);b=read_book(staged)
 recalculate(b,p)
 set_setting(b,'production_eligible',False)
 set_setting(b,'calculation_status','Conditional direct GE/TE/With Egestion WARN runtime verified; supported-catch annual subtotals calculated; full-region eligibility false; see Diagnostics and regional_ge_integration_20260928 evidence')
 set_setting(b,'source_note',caveat)
 set_setting(b,'computational_runtime_evidence','models/regional_ge_integration_20260928/runtime_verification.json')
 set_setting(b,'computational_state_sha256',ver['computational_state_sha256'])
 for (sheet,table),h in keep.items():assert digest_tables(b[sheet][table])==h
 assert digest_tables(list(b['NPP'].items()))==npp
 assert overview(b)['selected_model_id']==o['selected_model_id'] and overview(b)['selection_rationale']==o['selection_rationale'] and overview(b)['model_path']==o['model_path']
 assert sha(p)==before and sha(source)==canon
 validate_region(b,p);write_book(p,b)
 saved=read_book(p);validate_region(saved,p);assert overview(saved)['calculation_result_sha256']==result_hash(saved)
 for (sheet,table),h in keep.items():assert digest_tables(saved[sheet][table])==h
 assert digest_tables(list(saved['NPP'].items()))==npp
 annual=records(saved,'PPR','Annual');val={r['metric']:r.get(2019) for r in annual if r['scope']=='all' and r['method']=='new_GE' and r['catch_basis']=='catch' and r['unidentified']=='method'}
 # Independent taxon coefficients and annual sums, all methods/scopes/bases/years, method treatment.
 coeff={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(saved,'Selected model groups','Group SPPR')};mapping={r['taxon']:r['group'] for r in records(saved,'PPR','Matching') if r['group']};cr=records(saved,'Catch','Catch');checks=0
 for row in annual:
  if row['unidentified']!='method' or row['metric']!='ppr':continue
  for year in YEARS:
   terms=[r[year]*coeff[mapping[r['taxon']],row['scope'],row['method']] for r in cr if r['catch_basis']==row['catch_basis'] and r['taxon'] in mapping and finite(r.get(year))]
   expected=math.fsum(terms) if terms else None;actual=row[year]
   assert expected is None and actual is None or math.isclose(expected,actual,rel_tol=1e-8,abs_tol=.02),(rid,year,expected,actual)
   checks+=1
 summary={'unit_id':rid,'selected_model_id':mid,'canonical_sha256':canon,'before_workbook_sha256':before,'after_workbook_sha256':sha(p),'backup':backup.relative_to(ROOT).as_posix(),'year':2019,'basis':'total catch (landings plus discards)','source_scope':'all','unidentified_treatment':'method','ge_ppr_wet_tonnes':val['ppr'],'ge_ppr_carbon_tonnes':val['ppr']/9,'total_catch_tonnes':val['catch'],'covered_catch_tonnes':val['covered_catch'],'coverage_fraction':val['covered_catch']/val['catch'],'mapped_taxa':len(mapping),'catch_taxa':len(taxa),'full_region_eligible':False,'conditional_supported_subtotal':True,'caveats':caveat,'regional_validation':'PASS','independent_annual_cells_verified':checks,'source_selection_catch_classic_inputs_npp_preserved':True,'all_methods':'GE/TE/With Egestion WARN; no global/MC'}
 save(D/'integration_verification.json',summary);save(D/'mapping_decisions.json',decisions)
 with (D/'mapping_decisions.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(decisions[0]));w.writeheader();w.writerows(decisions)
 (D/'INTEGRATION_REPORT.md').write_text(f'# {rid}: conditional supported-catch integration\n\n{caveat}\n\n2019 all-source GE carbon: {summary["ge_ppr_carbon_tonnes"]:,.3f} tonnes carbon, covering {summary["coverage_fraction"]:.2%} of {val["catch"]:,.3f} tonnes total catch. {len(mapping)}/{len(taxa)} taxon labels mapped. Unsupported catches excluded, never presented as zero.\n\nAll three direct full returns and exact saved-state reload passed. Current regional validation passed; {checks} annual cells independently reconstructed. Selection, source JSON, Catch, Classic taxon inputs and NPP unchanged; previous workbook retained. No global or Monte Carlo run. Full-region eligibility remains false.\n\nSee mapping_decisions.csv for every unresolved label. Stage-split species remain unresolved without source-supported regional allocations. No broad-guild analogue or new ecological repair was introduced.\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=True),flush=True)
