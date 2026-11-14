from pathlib import Path
import json, shutil, hashlib, csv
ROOT=Path.cwd()
M=ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
V=M/'model_validation'; W=V/'work/2026-11-14_200000_ices_full_review'; E=V/'evidence/mapping'
for name in ['catch_crosswalk.json','group_definitions.json','source_findings.json','ices2015_context_pages.json']:
    shutil.copy2(W/'inputs/source_research'/name,E/('source_'+name))
search={'reviewed_date':'2026-11-14','purpose':'Observed caught-mass fractions for the five focal juvenile/adult stocks and shark/skate pools before choosing a model proxy','queries':['ICES 2019 North Sea cod catch at age landings discards age0 1 2 haddock whiting saithe herring WGNSSK','ICES2019 herring North Sea catch at age0 1 HAWG'],
 'sources':[{'url':'https://standardgraphs.ices.dk/ViewCharts.aspx?key=13211','read':'Stock identity and annual landings/discards table','finding':'Cod stock includes Subarea4, Division7.d, Subdivision20. Annual totals do not identify mass at the exact 24-month stanza threshold and do not isolate LME022.'},
 {'url':'https://standardgraphs.ices.dk/ViewCharts.aspx?key=13422','read':'Search index; full open timed out','finding':'North Sea herring stock extends through3.a and7.d. No matched LME-specific caught-mass fraction read.'},
 {'url':'https://backend.orbit.dtu.dk/ws/portalfiles/portal/234543035/01_HAWG_Report_2020.pdf','read':'Search index identifies catch-at-age numbers; full PDF fetch failed','finding':'Numbers require weight-at-age and fishery/area aggregation before mass shares. No fraction inferred from numbers or legal size.'},
 {'url':'https://www.gov.scot/publications/evaluation-multispecies-management-approaches/pages/5/','read':'Methods and materials, stock/fleet and age-assessment setup','finding':'Confirms age-structured WGNSSK/STECF input availability but provides no directly applicable LME022 catch-mass split at all five Rpath stage boundaries.'}],
 'decision':'No compatible measured 2019 LME caught-mass split was recovered in this bounded search. Use exact model1991 landings+discards proportions for independently identified candidates, W4 Medium; this is a historical composition/catchability transfer, not observed 2019 proportions. No claim that underlying ICES age data do not exist.',
 'stage_source':'extracted_tables/companions/Rpath_stanza_individuals.csv; model1991 groups',
 'source_stanza_cutoffs_months':{'Cod':24,'Whiting':12,'Haddock':12,'Saithe':36,'Herring':12},
 'other_stage_definitions':{'JuvenileSharks':'predecessor <40cm; length type not specified in passage','JuvenileRays':'predecessor all skates <30cm; length type not specified in passage'},
 'cutoff_warning':'Predecessor printed annual age/length labels and focal Rpath month transitions are not interchangeable. Proxy uses focal group catches without constructing a new age/length conversion.'}
(E/'allocation_search.json').write_text(json.dumps(search,indent=2,ensure_ascii=False),encoding='utf8')
model=json.loads((M/'model.json').read_text(encoding='utf8'))
defs=json.loads((W/'inputs/source_research/group_definitions.json').read_text(encoding='utf8'))
inventory=[]
for g in model['group']:
    inventory.append({'group_id':int(g['group_seq']),'group_name':g['group_name'],'canonical_taxon_descr':g.get('taxon_descr'),'source':'ICES2015 Table2.1 pp106–109; model.json','source_role':'focal inventory; predecessor dictionaries are evidence, not canonical changes','biomass':g.get('biomass'),'landings_total':g.get('landings_total'),'discards_total':g.get('discards_total'),'total_removals':g.get('total_removals')})
(E/'group_inventory.json').write_text(json.dumps({'groups':inventory,'source_group_count':69,'predecessor_group_definitions':'source_group_definitions.json','shape':'Species/stock groups, pooled taxonomic and habitat/feeding guilds; five focal month-based juvenile/adult stanzas, plus separate shark/skate size pools. No geographic strata. The11 native fleets are not ecological groups.','taxon_descr_status':'All canonical taxon_descr fields remain missing; reviewed inferred membership is held only in this proposed mapping.'},indent=2,ensure_ascii=False),encoding='utf8')
assert len(inventory)==69
# Record original current appendix before any authoring; no comments/manual fields existed.
from openpyxl import load_workbook
before=W/'inputs/taxon_mapping_before.xlsx'
if not before.exists():shutil.copy2(V/'taxon_mapping.xlsx',before)
b=load_workbook(before,data_only=False)
mapping=list(b['Taxon mapping'].values)
manual={'source_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'sheet_names':b.sheetnames,'comments':[(s.title,c.coordinate,c.comment.text) for s in b for row in s for c in row if c.comment],
'mapping_header':mapping[6],'old_taxon_count':len(mapping)-7,'old_all_groups_unresolved':all(r[4]=='Unresolved' for r in mapping[7:]),'old_all_confidence_unresolved':all(r[5]=='Unresolved' for r in mapping[7:]),'diagnostics_policy':'SPPR diagnostics and all original workbook package dependencies retained; author only the first two worksheets.'}
(W/'qa/appendix_before_inventory.json').write_text(json.dumps(manual,indent=2,ensure_ascii=False,default=str),encoding='utf8')
assert not manual['comments'] and manual['old_taxon_count']==384
print('Evidence, source inventory and appendix preservation record written')
