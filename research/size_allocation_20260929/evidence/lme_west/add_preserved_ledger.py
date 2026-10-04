import json,pathlib,hashlib,csv,collections
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[3]
x=json.loads((OUT/'inspection.json').read_text(encoding='utf8'));out=json.loads((OUT/'proposals.json').read_text(encoding='utf8'))
def ev(p,locator):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'locator':locator}
for pair in out['pairs']:
 rid=pair['unit_id']
 if rid not in ['LME_003','LME_014']:continue
 m=ROOT/'regions'/rid/'models'/pair['model_id']/'model.json';g={a['group_name']:a for a in json.loads(m.read_text(encoding='utf8'))['group']}
 bytax=collections.defaultdict(list)
 for r in x[rid]['tables']['Matching']:
  if r.get('group'):bytax[r['taxon']].append(r)
 if rid=='LME_003':
  stage={'Hake':'Juv. hake','Sablefish':'Juv. round.','Lingcod':'Juv. round.','Flatfish':'Juv. flat.','Halibut':'Juv. flat.','Petrale sole':'Juv. flat.','Arrowtooth':'Juv. flat.','Longspine thorny.':'Juv. thorny.','Shortspine thorny.':'Juv. thorny.'}
  for n in ['Yellowtail rock.','Black rock.','Nearshore rock.','Yelloweye rock.','Greenstriped','Shelf rock.','Shortbelly','Canary rock.','P. Ocean Perch','Widow rock.','Splitnose rock.','Slope rock.']:stage[n]='Juv. rock.'
  for taxon,rows in bytax.items():
   if not all(r['group'] in stage for r in rows):continue
   cand=[{'group':r['group'],'seq':int(g[r['group']]['group_seq']),'source_catch':float(g[r['group']]['export']),'weight':r['weight']} for r in rows]
   marker='Full candidate set including zero-weight groups: '
   if marker in rows[0].get('explanation',''):
    for n in rows[0]['explanation'].split(marker)[1].split(', '):
     if n in g and n not in {c['group'] for c in cand}:cand.append({'group':n,'seq':int(g[n]['group_seq']),'source_catch':float(g[n]['export']),'weight':0.0})
   for n in sorted({stage[r['group']] for r in rows}):
    assert float(g[n]['export'])==0
    cand.append({'group':n,'seq':int(g[n]['group_seq']),'source_catch':0.0,'weight':0.0})
   composite=len(rows)>1
   pair['proposals'].append({'taxon':taxon,'rule':'preserved_regional_taxonomic_composition_with_model_zero_juvenile' if composite else 'preserved_assumed_model_catch_share','action':'document_preserve_exact_weights','evidence':[ev(m,'Author model export and AppendixB taxon_descr'),{'path':'regions/LME_003/LME_003.xlsx','locator':'PPR/Matching existing evidence: '+str(rows[0]['evidence'])}],'definition':'Exact source counterpart stage groups; '+ '; '.join(n+': '+str(g[n].get('taxon_descr')) for n in sorted({stage[r['group']] for r in rows})),'limitations':'Existing mapping preserved bit-for-bit. Source zero juvenile catch is a model selectivity proxy, not observed regional stage composition. '+('Existing identified-regional-catch adult composition weights retained, not recomputed from model catches. Zero adult groups, if any, were excluded by the original regional composition workflow and remain documented in its candidate-set explanation.' if composite else ''),'source_period':'2000-2014 model; composite regional composition 1950-2019 where applicable','numericSPPR_exists':True,'candidates':cand,'existing_mapping_rows':rows})
 else:
  table=m.parent/'extracted_tables/Landings.csv';ls={a['Group name']:float(a['Total']) for a in csv.DictReader(table.open(encoding='utf-8-sig'))}
  rows=bytax['Doryteuthis gahi']
  cand=[{'group':r['group'],'seq':int(g[r['group']]['group_seq']),'source_catch':ls[r['group']],'source_catch_basis':'landings','source_total_removals':float(g[r['group']]['export']),'weight':r['weight']} for r in rows]
  pair['proposals'].append({'taxon':'Doryteuthis gahi','rule':'preserved_assumed_native_cohort_landings_share','action':'document_preserve_exact_weights','evidence':[ev(table,'Groups16/17 native2020 landings'),ev(m.parent/'selection_report.md','Source cohort Table2 p7 and selection split weights'),ev(m.parent/'selection_20260928/split_weights.csv','Already adopted cohort ratio')],'definition':'D. gahi ASC = autumn-spawning cohort; D. gahi SSC = spring-spawning cohort. Both source-defined cohorts of the same species.','limitations':'Fixed2020 native landing mixture is an explicit temporal/geographic proxy, not observed annual whole-LME cohort composition. Preserve previously supported mapping exactly.','source_period':'2020','numericSPPR_exists':True,'candidates':cand,'existing_mapping_rows':rows})
 pair['review_status']='existing_documented_mappings_preserved_ledger_proposals_added'
 for p in pair['proposals']:assert abs(sum(c['weight'] for c in p['candidates'])-1)<1e-12
(OUT/'proposals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print([(p['unit_id'],len(p['proposals'])) for p in out['pairs']])
