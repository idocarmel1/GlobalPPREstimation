import json, pathlib, hashlib, csv
ROOT=pathlib.Path(__file__).resolve().parents[4]
OUT=pathlib.Path(__file__).resolve().parent
x=json.loads((OUT/'inspection.json').read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def evidence(p,note=''):
 return {'path':rel(p),'sha256':sha(p),'locator':note}
pairs=[]
for rid,v in x.items():
 mid=v['inventory']['model_id']; wb=ROOT/v['inventory']['workbook']; m=ROOT/'regions'/rid/'models'/mid/'model.json'
 canonical=json.loads(m.read_text(encoding='utf8'))
 groups={g['group_name']:g for g in canonical['group']}
 loaded={g['group_name']:g for g in v['tables'].get('Groups',[])}
 pair={'unit_id':rid,'model_id':mid,'workbook_sha256':sha(wb),'review_status':'reviewed_no_new_applicable_same_taxon_split','numericSPPR_exists':bool(v['tables'].get('Group SPPR')),'proposals':[],'preserved':[],'unresolved':[],'sources':[evidence(m,'Canonical group definitions/export'),evidence(wb,'Overview; Selected model groups/Groups; PPR/Matching')],'online_search_audit':'original_research_archive/research/size_allocation_20260929/lme_west/online_search_audit.json'}
 def add(taxon,names,definition,period,extra='',field='export',action='new_mapping'):
  cs=[]
  for name in names:
   g=groups[name];n=float(g[field]); assert n>=0
   cand={'group':name,'seq':int(g['group_seq']),'source_catch':n,'source_catch_field':field,'source_catch_raw':g[field],'loaded_catch':loaded.get(name,{}).get('catch'),'taxon_definition':g.get('taxon_descr')}
   for f in ['source_landings','source_discards','landings_total','discards_total']:
    if f in g:cand[f]=g[f]
   cs.append(cand)
  total=sum(c['source_catch'] for c in cs);assert total>0
  for c in cs:c['weight']=c['source_catch']/total
  assert abs(sum(c['weight'] for c in cs)-1)<1e-12
  pair['proposals'].append({'taxon':taxon,'rule':'assumed_model_catch_share','allocation_rule':'assumed_model_catch_share','action':action,'evidence':[evidence(m,'group export / source catches'),{'path':pair['online_search_audit'],'locator':rid+' online primary-source search; no compatible observed mass fractions adopted'}],'definition':definition,'limitations':'Model catch proportions are an explicitly assumed proxy for unsized regional catches, not observed regional size distributions. One fixed mapping is reused across catch years and bases. '+extra,'source_period':period,'source_catch_basis':'total removals (landings plus reported discards)' if rid in ['LME_024','LME_026'] else 'source model recorded catch/landings; missing discards not invented','numericSPPR_exists':pair['numericSPPR_exists'],'candidates':cs})
 if rid=='LME_013':
  add('Macruronus magellanicus',['Hoki (j)','Hoki (a)'],'Hoki juveniles <3 years; adults >=3 years. Paper methods and group table explicitly name Macruronus magellanicus.','1980','Chilean Patagonia model transferred to Humboldt LME; geographical mismatch remains unresolved.')
  p=ROOT/'regions/LME_013/papers/HUM-2026/extracted/work/paper.txt';pair['sources'].append(evidence(p,'Lines 262-263 and 290-296; Table landings Y'))
 elif rid=='LME_024':
  for t,a,j in [('Gadus morhua','Cod adult','Cod juvenile'),('Merluccius merluccius','Hake adult','Hake juvenile'),('Lophius budegassa','Anglerfish adult','Anglerfish juvenile'),('Lophius piscatorius','Anglerfish adult','Anglerfish juvenile')]:
   add(t,[a,j],'B1 species membership and B4 adult/juvenile labels; no numerical age/length boundary supplied in retained source definition.','1985','For each Lophius species, the same two-species anglerfish pool stage shares are assumed applicable within species; no taxonomic composition weights are introduced. Source diagnostic FAIL remains.' if t.startswith('Lophius') else 'Source diagnostic FAIL remains.')
  for name in ['Landings.csv','Discards.csv','taxonomy.csv','REPORT.md']:
   pair['sources'].append(evidence(m.parent/'extracted_tables'/name,'Supplement B1/B3/B4; source fishery densities conventionally t/km2/year'))
 elif rid=='LME_026':
  for t,a,j in [('Sardina pilchardus','E. sardine Adult','E. sardine Recruit'),('Engraulis encrasicolus','E. anchovy Adult','E. Anchovy Recruit'),('Merluccius merluccius','E. Hake Adult','E. Hake Recruit'),('Mullus barbatus','Red mullet Adult','Red mullet Recruit')]:
   assert t in json.loads((OUT/'med_catch_taxa.json').read_text())
   add(t,[a,j],'Source Table S2 explicitly combines adults and juveniles of this species; XLSX input has the stated Adult/Recruit pair. No quantitative stage cutoff recovered.','1995 (supplement label: 1990s)','Documentation only until loaded groups are published: no numeric SPPR; constructor routing blocked. No annual numerical model estimate may be generated from this map.',action='document_mapping_without_numeric_sppr')
  for name in ['Landings.csv','Discards.csv','taxonomy.csv','REPORT.md']:
   pair['sources'].append(evidence(m.parent/'extracted_tables'/name,'Source XLSX Catches=landings and Discards; Word Table S2'))
  pair['sources'].append(evidence(m.parent/'diagnostics/loader_groups_before_defaults.csv','Constructor-stage groups, not a complete loaded calculator'))
 elif rid=='LME_029':
  add('Sardinops sagax',['Juvenile sardine','Adult sardine'],'Main Table 1: recruits <1 year; adults >=1 year.','1978','Southern Benguela source transferred across larger LME; all source direct diagnostics FAIL remain.')
  add('Merluccius capensis',['Small M. capensis','Large M. capensis'],'Main Table 1: small <3 years; large >=3 years.','1978','Southern Benguela source transferred across larger LME; all source direct diagnostics FAIL remain.')
  add('Trachurus capensis',['Juvenile Hmack','Adult Hmack'],'Main Table 1 source Trachurus trachurus capensis: juveniles <2 years; adults >=2 years. WoRMS accepts this source subspecies name as Trachurus capensis.','1978','Southern Benguela source transferred across larger LME; all source direct diagnostics FAIL remain.')
  pair['proposals'][-1]['evidence'].append({'url':'https://www.marinespecies.org/aphia.php?p=taxlist&tName=Trachurus+trachurus','locator':'Source-name synonym crosswalk'})
  pair['unresolved'].append({'taxon':'Engraulis capensis','reason':'Source stage pair names Engraulis encrasicolus. Primary 2003 Southern Benguela paper explicitly treats E. capensis as former name of regional E. encrasicolus, but current WoRMS returns separate E. capensis record and FishBase calls name ambiguous. Do not silently assert a current accepted synonym. Parent may review historical regional naming crosswalk separately.','candidate_groups':[{'group':n,'seq':int(groups[n]['group_seq']),'source_catch':float(groups[n]['export']),'conditional_weight':float(groups[n]['export'])/0.952} for n in ['Anchovy recruits','Anchovy spawners']],'evidence_urls':['https://www.brest.ird.fr/personnel/ppenven/publications/hugget_meps2003.pdf','https://www.marinespecies.org/aphia.php?p=taxlist&tName=Engraulis','https://www.fishbase.se/Nomenclature/66']})
  pair['unresolved'].append({'taxon':'Merluccius paradoxus','reason':'Unambiguous same-taxon <3/>=3 split, but no exact catch label in this selected-region Matching inventory. Do not assign generic Merluccius/Merlucciidae or Merluccius polli to it.','candidate_groups':[{'group':n,'seq':int(groups[n]['group_seq']),'source_catch':float(groups[n]['export'])} for n in ['Small M. paradoxus','Large M. paradoxus']]})
  pair['unresolved'].append({'taxon':'Emmelichthys nitidus','reason':'Source membership overlaps trophic guilds; not a clean same-taxon age/size split. No arbitrary allocation.'})
  for name in ['Landings.csv','REPORT.md','MODEL_PROFILE.md']:pair['sources'].append(evidence(m.parent/'extracted_tables'/name,'Main Table1; supplement S2/S4; catch includes explicitly enumerated source fleets'))
 elif rid=='LME_014':
  existing=[a for a in v['tables']['Matching'] if a['taxon']=='Doryteuthis gahi']
  pair['preserved'].append({'taxon':'Doryteuthis gahi','rule':'existing_documented_native_2020_landings_cohort_share','rows':existing,'reason':'Already documented source-specific cohort landing proportions; preserve supported mapping, including ASC 0.4923774713888611 / SSC 0.507622528611139.'})
  pair['unresolved'].append({'taxon':'Dissostichus eleginoides','reason':'Juvenile-only source group excludes adults and longline fishery. Whole-LME unsized catches cannot be allocated without missing adult structure. Large-only fallback cannot create an adult group.'})
 elif rid=='LME_003':
  rows=[a for a in v['tables']['Matching'] if a.get('group') and ('juvenile' in a.get('explanation','').lower() or 'juvenile-flat' in a.get('explanation','').lower())]
  pair['preserved'].append({'rule':'existing_documented_zero_juvenile_model_catch','rows':rows,'reason':'Existing supported assignments already explicitly document model zero-juvenile catch; retain. Multi-taxon composite proportions are separately based on identified regional catches and are not replaced by model size weights.'})
  pair['zero_catch_juvenile_candidates']=[{'group':n,'seq':int(g['group_seq']),'source_catch':float(g['export']),'definition':g.get('taxon_descr')} for n,g in groups.items() if n.startswith('Juv.')]
  pair['unresolved'].append({'taxon':None,'reason':'Other unresolved taxa lack adult source membership or complete taxonomic candidate sets; size assumptions do not repair those gaps.'})
 elif rid in ['LME_022','LME_027','LME_028']:
  pair['unresolved'].append({'taxon':None,'reason':'No exact same-taxon life-stage pair identified. Size words in pelagic/demersal guild names describe different species pools (and sometimes habitat or diet); allocating across them would add taxonomic/spatial assumptions.'})
 if pair['proposals']:pair['review_status']='proposals_ready' if pair['numericSPPR_exists'] else 'mapping_documentation_ready_numeric_sppr_blocked'
 elif pair['preserved']:pair['review_status']='existing_documented_mappings_preserved'
 pairs.append(pair)
out={'policy':'Prefer observed compatible catch mass fractions; after documented online search use model recorded catch shares within supported same-taxon stages only. No biomass, gear invention, or speciesmaxsize inference. No production writes.','pairs':pairs}
(OUT/'proposals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print([(p['unit_id'],len(p['proposals']),p['review_status']) for p in pairs])
