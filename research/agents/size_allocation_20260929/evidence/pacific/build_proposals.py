import csv, hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'original_research_archive/research/regional_ge_integration_20260928'))
from xml_audit_reader import read_book
OUT=Path(__file__).resolve().parent
REGIONS=['HS_077','EEZ_941','EEZ_598','HS_071']
def records(table):
 h,rows=table
 return [dict(zip(h,row)) for row in rows]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
wcpo={'Katsuwonus pelamis':['SKJ','Small SKJ','baby SKJ'],'Thunnus albacares':['YFT','Small YFT'],'Thunnus obesus':['BET','Small BET'],'Prionace glauca':['Blue Shark','Small Sharks'],'Xiphias gladius':['Swordfish','Small Billfish']}
for t in ['Alopias','Carcharhinus falciformis','Carcharhinus longimanus','Isurus','Isurus oxyrinchus','Lamnidae','Sphyrna','Galeocerdo cuvier']:
 wcpo[t]=['Other Sharks','Small Sharks']
for t in ['Istiophorus platypterus','Tetrapturus angustirostris']:wcpo[t]=['Other Billfish','Small Billfish']
pairs=[]
for region in REGIONS:
 path=ROOT/'regions'/region/(region+'.xlsx');book=read_book(path)
 settings=dict(book['Overview']['Settings'][1]);model_id=settings['selected_model_id'];model_path=path.parent/settings['model_path']
 canonical=json.loads(model_path.read_text(encoding='utf8'));cg={g['group_name']:g for g in canonical['group']}
 groups={g['group_name']:g for g in records(book['Selected model groups']['Groups'])};matches=records(book['PPR']['Matching'])
 taxpath=ROOT/('regions/HS_077/evidence/2026-09-28_integration_audit/taxonomy.csv' if region=='HS_077' else 'regions/EEZ_941/evidence/2026-09-28_integration/taxonomy.csv')
 tax={g['group_name']:g['taxon_descr'] for g in csv.DictReader(taxpath.open(encoding='utf8'))}
 proposals=[];unresolved=[]
 for m in matches:
  if m['group']:continue
  t=m['taxon'];names=[]
  if region=='HS_077' and 'Candidate groups: ' in m['explanation']:names=m['explanation'].split('Candidate groups: ')[1].split('; ')
  elif region!='HS_077':names=wcpo.get(t,[])
  if not names:
   unresolved.append({'taxon':t,'existing_mapping':m,'reason':'Outside verified size-only assignments: source membership, synonym reconciliation, multi-guild or geographic applicability remains unresolved.'});continue
  candidates=[]
  for name in names:
   g=groups[name];c=cg[name];raw=float(c.get('export',-9999));missing=raw==-9999
   assert int(c['group_seq'])==int(g['seq'])
   assert missing or math.isclose(raw,float(g['catch']),rel_tol=1e-12,abs_tol=1e-15)
   candidates.append({'group':name,'seq':g['seq'],'source_catch':None if missing else raw,'canonical_export_raw':c.get('export'),'loaded_catch':g['catch'],'catch_state':'missing canonical value; explicit assumed zero for un-recruited infant group' if missing else 'canonical numeric export equals loaded catch','definition':tax[name]})
  total=sum(c['loaded_catch'] for c in candidates)
  assert total>0
  for c in candidates:c['weight']=c['loaded_catch']/total
  assert abs(sum(c['weight'] for c in candidates)-1)<1e-12
  infant=t=='Katsuwonus pelamis' and region!='HS_077'
  rule='historical_model_catch_proxy_with_assumed_uncaught_infant' if infant else 'historical_model_catch_proxy'
  evidence=('Olson & Watters (2003), Table 1a, printed pp.152-153/PDF22-23; selected canonical JSON export and Selected model groups/Groups catch, verified equal.' if region=='HS_077' else 'Allain et al. (2007), Table 1 PDF9 definitions and Table 5 PDF14 fisheries landings (t/km2/year); selected option1 canonical JSON export and Selected model groups/Groups catch, verified equal except baby SKJ missing/default.')
  limits=['Explicit assumed allocation; historical model catch composition is not observed regional/year catch-size composition. One constant mapping per selected model-region pair applies across retained years and catch bases.','No gear or mesh inference; SAU functional-group maximum size is not a caught-fish measurement.','Source geography differs from the regional catch polygon; existing model diagnostic/provisional restrictions remain.']
  if any('shark' in n.lower() for n in names):limits.append('Pooled shark-group catch ratio is assumed transferable to the supported taxon; source gives no numerical WCPO shark cutoff.' if region!='HS_077' else 'Pooled shark-group catch ratio is assumed transferable to each supported species/genus; source small/large boundary 150 cm.')
  if infant:limits.append('baby SKJ export is missing (-9999), not an observed zero. Explicit assumption: none of regional catch belongs to un-recruited 0-3-month baby stage; normalize reported adult and Small SKJ catches. Table 1 <24 cm definition conflicts with p15 <10 cm prose; retained without numerical reconciliation.')
  if any(n in ['Small Billfish','Small Sharks'] for n in names):limits.append('Small pool is explicit source/model zero; adult weight 1 is a model-catch proxy, not evidence that all regional fish are adult. Small pooled group includes other adult taxa, so zero is carried as historical-pool proxy only.')
  proposals.append({'taxon':t,'rule':'model_catch_proxy','rule_details':rule,'online_search_completed':True,'evidence':evidence,'definition':' | '.join(n+': '+tax[n] for n in names),'limitations':limits,'source_period':'1993-1997' if region=='HS_077' else 'mixed periods; Allain et al. 2007 historical WCPO warm-pool fisheries, not regional-year observations','candidates':candidates,'existing_mapping':m,'source_paths':[model_path.relative_to(ROOT).as_posix(),taxpath.relative_to(ROOT).as_posix(),path.relative_to(ROOT).as_posix()],'confidence':'assumed','observed_regional_size_shares_available':False})
 catches=records(book['Catch']['Catch']);baseline={m['taxon'] for m in matches if m['group']};new={p['taxon'] for p in proposals};coverage={}
 for basis in ['catch','landings','discards']:
  rows=[c for c in catches if c['catch_basis']==basis];total=sum(c.get(2019) or 0 for c in rows);before=sum(c.get(2019) or 0 for c in rows if c['taxon'] in baseline);added=sum(c.get(2019) or 0 for c in rows if c['taxon'] in new)
  coverage[basis]={'year':2019,'total_tonnes':total,'before_tonnes':before,'new_assumed_tonnes':added,'after_tonnes':before+added,'before_pct':100*before/total if total else None,'after_pct':100*(before+added)/total if total else None}
 pair={'unit_id':region,'model_id':model_id,'workbook_sha256':digest(path),'workbook_path':path.relative_to(ROOT).as_posix(),'canonical_model_path':model_path.relative_to(ROOT).as_posix(),'canonical_model_sha256':digest(model_path),'review_status':'ready; assumed allocation with existing model limitations retained','proposals':proposals,'unresolved':unresolved,'coverage_2019':coverage,'numeric_model_availability':{'available':True,'coefficient_source':'Selected model groups/Group SPPR','existing_calculation_status':settings.get('calculation_status'),'model_source_note':settings.get('source_note')},'online_search_audit':'original_research_archive/research/size_allocation_20260929/pacific/online_search_audit.json','observed_size_data_review':'Targeted primary-source online search completed; no usable region/year/gear-aligned mass fractions recovered. See retained online search audit; WCPFC size dataset requires registration.'}
 pairs.append(pair)
 (OUT/(region+'_proposals.json')).write_text(json.dumps({'pairs':[pair]},indent=2,ensure_ascii=False),encoding='utf8')
(OUT/'proposals.json').write_text(json.dumps({'schema_version':1,'scope':'selected models only; one mapping per model-region pair','pairs':pairs},indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps([{ 'unit_id':p['unit_id'],'proposals':len(p['proposals']),'remaining_unresolved':len(p['unresolved']),'catch_coverage':p['coverage_2019']['catch']} for p in pairs],indent=2))
