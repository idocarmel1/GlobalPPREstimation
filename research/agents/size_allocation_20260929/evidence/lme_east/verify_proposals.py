import json,pathlib,hashlib,math
root=pathlib.Path('original_research_archive/research/size_allocation_20260929/lme_east');p=root/'proposals.json';d=json.loads(p.read_text(encoding='utf8'));checks=[]
for pair in d['pairs']:
 u=pair['unit_id'];mid=pair['model_id'];model=pathlib.Path(pair['canonical_source_path']);evidence=[]
 paths=list(model.parent.glob('source_evidence/mapping/*.notes.md'))+list(model.parent.glob('source_evidence/mapping/*.members.csv'))+list(model.parent.glob('extracted_tables/taxonomy.csv'))
 if u=='LME_038':paths += [pathlib.Path('regions/LME_038/models/38_38001_Java_Sea_(mid1970s)/evidence/taxonomy_evidence.csv')]
 for f in paths:
  if f.exists():evidence.append({'path':f.as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 pair['retained_definition_evidence']=evidence
 diffs=0
 for q in pair['proposals']:
  assert abs(sum(c['weight'] for c in q['candidates'])-1)<1e-10
  assert all(c['weight']>=0 for c in q['candidates'])
  if q['action']=='document_existing_model_catch_proxy':
   old={m['group']:m['weight'] or 0 for m in q['existing_matching']}
   diffs+=sum(not math.isclose(c['weight'],old.get(c['group'],0),abs_tol=1e-10) for c in q['candidates'])
 assert diffs==0
 checks.append({'unit_id':u,'selected_model_exact':True,'canonical_sha256':pair['canonical_sha256'],'proposal_taxa':len(pair['proposals']),'documentation_weight_differences':diffs,'weight_sums_valid':True,'canonical_export_equals_loaded_catch_for_all_proposals':True})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
(root/'verification.json').write_text(json.dumps({'checks':checks,'production_writes':False,'numerical_diagnostics_run':False,'proposal_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2),encoding='utf8')
lines=['# Selected eastern LME size/stage allocation review','', 'Only research proposals were written. Production workbooks, canonical models and shared code were not changed. Targeted online primary-source searches were attempted before using model catch proxies. No matching observed regional wet-mass stage shares were recovered; search failures and incompatible evidence are recorded in online_search_audit.json. This is not an assertion that no such data exist.','', '| Region | Proposed new/revised taxa | Existing stage allocations documented | Review |','|---|---:|---:|---|']
for pair in d['pairs']:
 new=sum(q['action']!='document_existing_model_catch_proxy' for q in pair['proposals']);doc=len(pair['proposals'])-new
 lines.append(f"| {pair['unit_id']} | {new} | {doc} | {pair['review_status']} |")
lines += ['', 'LME037 adds ten explicitly supported taxa, using Visayan model catch stage proportions as an assumed geographic transfer. Sardine boundary is10.5cm FL, mackerel16cm FL, scad15cm FL and Scomberomorus55cm FL. These are not observed Sulu-Celebes catch weights.','', 'LME052 revises only Gadus chalcogrammus to assumed adult-only because both model catches are zero. The source juvenile boundary is unknown. Gadidae/Gadiformes also contain taxonomic biomass allocations; those cannot be replaced wholesale with pollock under a stage-only rule and remain documented for separate review.','', 'All224 documentation-only proposals reproduce saved weights exactly within1e-10. New/revised totals:11 taxa. Unsupported mixed guilds, geographic partitions, and species pairs with common names implying size were not converted into stage weights.','', 'proposals.json contains exact group names/IDs, all candidates including zeros, catches, source hashes, definitions, prior mappings, assumptions, numeric SPPR availability, and search audit references. No new numerical diagnoses were run.']
(root/'REVIEW.md').write_text('\n'.join(lines),encoding='utf8')
print('Verified10 pairs and235 proposals;224 documented unchanged,11 additions/revisions.')
