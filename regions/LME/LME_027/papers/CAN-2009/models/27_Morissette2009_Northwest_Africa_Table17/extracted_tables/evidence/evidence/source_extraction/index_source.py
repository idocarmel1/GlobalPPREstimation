from pathlib import Path
from decimal import Decimal
import hashlib,json,os,re,sys
OUT=Path(__file__).resolve().parent
CAND=OUT.parents[1]
ROOT=OUT.parents[5]
def save(name,value): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()

source=ROOT/'regions/LME_027/papers/FCRR_2009_17-2.pdf.pdf'
table17=json.loads((OUT/'table17_cells.json').read_text(encoding='utf-8'))
for cell in table17:
 n=cell['group_id']; f=cell['field']
 estimated=(f=='tl' or f=='ee' and n!=14 or f=='biomass' and n==14 or f=='qb' and n in [14,18] or f=='pq' and n not in [14,18,24,26,27])
 cell['provenance']='model_estimated_bold' if estimated and cell['adopted_literal'] is not None else 'source_input' if cell['adopted_literal'] is not None else 'not_applicable'
save('table17_cells.json',table17)

series=json.loads((OUT/'catch_time_series.json').read_text(encoding='utf-8'))
check=[]
for fleet in ['Local fleets','Foreign fleets']:
 for year in range(1987,2005):
  rows=[r for r in series if r['year']==year and r['fleet']==fleet]
  summed=sum((Decimal(r['source_literal']) for r in rows if r['group_id']!='Total'),Decimal(0))
  total=next(Decimal(r['source_literal']) for r in rows if r['group_id']=='Total')
  check.append({'year':year,'fleet':fleet,'sum_components_1000t':str(summed),'printed_total_1000t':str(total),'difference':str(summed-total),'within_12_component_rounding_bound':abs(summed-total)<=Decimal('.0065')})
save('catch_time_series_sums.json',check)

save('source_bundle.json',{'scope':'Final Northwest Africa paper-only Table17/18 extraction','documents':[{'path':'../../../../papers/FCRR_2009_17-2.pdf.pdf','role':'primary_publication','sha256':hashfile(source),'model_coverage':['Northwest Africa late1980s','Caribbean separate model (excluded from this extraction)'],'numerically_used':'Table17;Table18;partial1990s catch prose','retained_context':'Tables1,2,3,15,16;balancing prose;study area;time series','pages_used_pdf':[10,11,14,15,16,17,18,19,20,31,32,33,34,35,36,37,38,39,40,41,42,43]},{'path':'../identity/ecobase118_official_native.json','role':'official_native_lineage_comparison','numerically_used':False,'recovered_missing_source_fields':'Zooplankton diet;other native parameters are separate variant only','authority':'Official EcoBase118 export independently retrieved by identity reviewer'},{'path':'../identity/MEPS2010_supplement.pdf','role':'adjacent_later_publication','numerically_used':False,'decision':'Identity reviewer owns comparison; not assumed same as paper Table17'}]})

artifacts=[]
def add(role,p):
 artifacts.append({'role':role,'path':os.path.relpath(p,OUT).replace('\\','/'),'sha256':hashfile(p),'availability':'present'})
add('source_pdf',source)
add('canonical_model',CAND/'model.json')
for p in sorted((CAND/'extracted_tables').iterdir()):
 if p.is_file():add('import_'+p.stem if p.name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx'] else 'extraction_support',p)
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name not in ['evidence_index.json','evidence_completeness.json'] and '__pycache__' not in p.parts:add('source_extraction_evidence',p)
for role,reason in [('complete_paper_consumer_diet','Table18 omits consumer25; official native values retained as separate variant'),('paper_routing_parameters','No numerical detritus fate/import or assimilation statement in full chapter sweep'),('complete_paper_baseline_catch','Tables1/2 have time series; partial prose means are1990s, baseline late1980s not fully specified')]:
 artifacts.append({'role':role,'availability':'missing','reason':reason,'acquisition_status':'Full chapter searched; official native lineage recovered separately; not filled in paper-only extraction'})
roles=['source_pdf','canonical_model','source_extraction_evidence']+['import_'+s for s in ['Basic_input','Diet_composition','Landings','Discards','Detritus_fate','Biomass_accumulation','TL','Metadata']]+['complete_paper_consumer_diet','paper_routing_parameters','complete_paper_baseline_catch']
roundtrip=json.loads((OUT/'roundtrip_verification.json').read_text(encoding='utf-8'))
comparison=json.loads((OUT/'paper_native_diet_comparison.json').read_text(encoding='utf-8'))
save('evidence_index.json',{'schema_version':1,'run_id':'20261003_LME027_Table17_source_extraction','region_id':'LME_027','model_id':CAND.name,'variant_id':'paper_only_Table17_Table18_partial','source_identity':{'sha256':hashfile(source),'file':'FCRR_2009_17-2.pdf.pdf'},'computational_input_identity':{'status':'not_created_in_source_extraction','canonical_sha256':hashfile(CAND/'model.json')},'methods':[],'required_roles':roles,'artifacts':artifacts,'reconciliation':{'eight_table_roundtrip':roundtrip['pass'],'native_printed_diet_consistency':comparison['inconsistent_count']==0},'scientific_status':'incomplete_source_input; evidence record complete for known extraction and identified omissions'})
sys.path.insert(0,str(ROOT/'tools/skills/original_skill_resources/combined-src/scripts'))
from check_evidence import check as check_index
result=check_index(OUT/'evidence_index.json')
save('evidence_completeness.json',result)
print(json.dumps({'verified_artifacts':len(result['verified_artifacts']),'integrity_errors':result['errors'],'missing_roles':result['missing_roles'],'catch_sum_outside_rounding':[r for r in check if not r['within_12_component_rounding_bound']]},ensure_ascii=False,indent=2))
