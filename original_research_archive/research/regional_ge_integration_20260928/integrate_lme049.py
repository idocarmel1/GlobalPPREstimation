from pathlib import Path
import sys,json,math,shutil,csv,hashlib
import pandas as pd
ROOT=Path.cwd();ARCH=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import recalculate,set_setting,result_hash

def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
for rid in ['LME_049']:
 R=ROOT/'regions'/rid;p=R/f'{rid}.xlsx';D=R/'models/regional_ge_integration_20260928';b=read_book(p);o=overview(b);mid=o['selected_model_id'];source=R/o['model_path'];before=sha(p);canon=sha(source)
 assert not records(b,'PPR','Matching') and not records(b,'PPR','Annual'),'Expected pending workbook only'
 ver=json.loads((D/'runtime_verification.json').read_text(encoding='utf-8'));assert ver['canonical_sha256']==canon
 assert all(x['retained_health_matches'] and x['exact_runtime_reload_matches'] for x in ver['methods'])
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
 taxa=sorted({r['taxon'] for r in records(b,'Catch','Catch')});decisions=[];maps=[]
 prep=source.parent/'evidence/source_supported_matching_preparation.csv'
 with prep.open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):
   decisions.append({k:(float(row[k]) if k=='weight' and row[k] else row[k] or None) for k in ['taxon','group','weight','confidence','evidence','explanation']})
 assert set(x['taxon'] for x in decisions)==set(taxa)
 assert sum(bool(x['group']) for x in decisions)==7
 caveat='PROVISIONAL UNVALIDATED: user authorized numeric display before scientific validation. Exact selected39-group detritus-pooled Watari2013 experiment and retained runtime reproduced. Seabirds missing living biomass defaults B=1 and PB/QB=0; GS/default completion, rounded-diet normalization, assumed common detritus routing, and residual-solved BA remain material. GE/Egestion overall OK are threshold grades only, strict SPPR balance false. TE overall FAIL: negative basal-source coefficients in unfished Seabirds and near singularity remain; negative group contributions are retained, not repaired or hidden. Only seven exact source members mapped; all others unresolved. Whole-region spatial suitability and species proportions are not validated.'
 headers=['model_id','taxon','group','weight','confidence','evidence','explanation']
 for d in decisions:maps.append([mid,*[d[k] for k in headers[1:]]])
 b['PPR']['Matching']=(headers,maps)
 health=json.loads((D/'health.json').read_text(encoding='utf-8'));hh=list(health[0]);b['Diagnostics']['model_health']=(hh,[[x.get(k) for k in hh] for x in health])
 b['Diagnostics']['run_notes']=(['topic','note','status'],[['Scientific admission',caveat,'PROVISIONAL - not validated'],['Provenance','models/regional_ge_integration_20260928/runtime_verification.json; computational_state.json; source-preserving input and constructor','verified'],['Mapping','Conservative direct source membership; all missing labels retained unresolved. No proxy stocks or invented allocation weights.','partial'],['Sensitivity','Historical discard sensitivity unavailable after current calculations; no new Monte Carlo performed.','unavailable']])
 b['PPR']['Annual']=(ANNUAL_HEADER,[[mid,scope,method,'landings','method','ppr','provisional: '+({'new_GE':'GE overall OK; strict SPPR balance false; missing Seabirds B=1/PB=QB=0','new_TE_EEfix':'TE FAIL; negative unfished Seabirds sources; near-singular; source/default problems','new_WithEgestion':'With Egestion overall OK; strict SPPR balance false; missing Seabirds B=1/PB=QB=0'}[method])+'; scientific validation pending',*[None]*70] for scope in ['all','inner','PP'] for method in ['new_GE','new_TE_EEfix','new_WithEgestion']])
 set_setting(b,'results_model_id',mid);set_setting(b,'results_model_sha256',canon)
 staged=D/'staged_inputs.xlsx';write_book(staged,b);b=read_book(staged)
 recalculate(b,p)
 set_setting(b,'production_eligible',False)
 set_setting(b,'calculation_status','PROVISIONAL numeric mapped-catch PPR displayed by user instruction; GE/Egestion OK thresholds only; TE FAIL; serious source/default issues unresolved; scientific validation pending')
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
   terms=[r[year]*round(coeff[mapping[r['taxon']],row['scope'],row['method']],6) for r in cr if r['catch_basis']==row['catch_basis'] and r['taxon'] in mapping and finite(r.get(year))]
   expected=math.fsum(terms) if terms else None;actual=row[year]
   assert expected is None and actual is None or math.isclose(expected,actual,rel_tol=1e-8,abs_tol=.02),(rid,year,expected,actual)
   checks+=1
 summary={'unit_id':rid,'selected_model_id':mid,'canonical_sha256':canon,'before_workbook_sha256':before,'after_workbook_sha256':sha(p),'backup':backup.relative_to(ROOT).as_posix(),'year':2019,'basis':'total catch (landings plus discards)','source_scope':'all','unidentified_treatment':'method','ge_ppr_wet_tonnes':val['ppr'],'ge_ppr_carbon_tonnes':val['ppr']/9,'total_catch_tonnes':val['catch'],'covered_catch_tonnes':val['covered_catch'],'coverage_fraction':val['covered_catch']/val['catch'],'mapped_taxa':len(mapping),'catch_taxa':len(taxa),'full_region_eligible':False,'conditional_supported_subtotal':True,'caveats':caveat,'regional_validation':'PASS','independent_annual_cells_verified':checks,'source_selection_catch_classic_inputs_npp_preserved':True,'all_methods':'GE OK, TE FAIL, With Egestion OK; provisional numeric outputs; no global/MC'}
 save(D/'integration_verification.json',summary);save(D/'mapping_decisions.json',decisions)
 with (D/'mapping_decisions.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(decisions[0]));w.writeheader();w.writerows(decisions)
 (D/'INTEGRATION_REPORT.md').write_text(f'# {rid}: conditional supported-catch integration\n\n{caveat}\n\n2019 all-source GE carbon: {summary["ge_ppr_carbon_tonnes"]:,.3f} tonnes carbon, covering {summary["coverage_fraction"]:.2%} of {val["catch"]:,.3f} tonnes total catch. {len(mapping)}/{len(taxa)} taxon labels mapped. Unsupported catches excluded, never presented as zero.\n\nAll three direct full returns exactly reproduced retained results and saved-state reload; this is a numerical identity check, not scientific validation. Actual TE grade remains FAIL. Current regional validation passed; {checks} annual cells independently reconstructed. Selection, source JSON, Catch, Classic taxon inputs and NPP unchanged; previous workbook retained. No global or Monte Carlo run. Full-region eligibility remains false.\n\nSee mapping_decisions.csv for every unresolved label. Only the seven previously prepared exact source-member matches were used. No broad-guild analogue or new ecological repair was introduced.\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=True),flush=True)
