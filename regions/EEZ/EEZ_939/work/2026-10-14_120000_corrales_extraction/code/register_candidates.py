"""Serialize a narrow, guarded metadata registration; no regional adoption."""
from pathlib import Path
import sys,json,hashlib,datetime,os,tempfile,copy
ROOT=Path(__file__).resolve().parents[6];WORK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,update_book,records,digest_tables
PAPER=ROOT/'regions/EEZ/EEZ_939/papers/Corrales-2010';BASE=PAPER/'models';PROJECT=ROOT/'Project.xlsx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
assert digest_tables(load(WORK/'inputs/region_tables.json'))==digest_tables(read_book(ROOT/'regions/EEZ/EEZ_939/EEZ_939.xlsx'))
expected_sha=sha(PROJECT);book=read_book(PROJECT);assert sha(PROJECT)==expected_sha
original=copy.deepcopy(book);ph,pr=book['Papers']['Papers'];mh,mr=book['Models & coverage']['Models']
article_id='Corrales-2017-ICS__EEZ_939';manifest=load(PAPER/'source_manifest.json')
assert not any(dict(zip(ph,r)).get('article_id')==article_id for r in pr),'Refusing to overwrite an existing registered article'
paper={'article_id':article_id,'source_article_id':'Corrales-2017-ICS','unit_id':'EEZ_939','region_name':'Israel (Mediterranean)','authors':'Corrales X; Ofir E; Coll M; Goren M; Edelist D; Heymans JJ; Gal G','publication_year':2017,'title':'Modeling the role and impact of alien species and fisheries on the Israeli marine continental shelf ecosystem','doi':manifest['doi'],'landing_page':'https://doi.org/'+manifest['doi'],'model_years':'1990–1994; 2008–2012','functional_groups':'39; 41','coverage_class':'partial shelf','geometry_method':'reported study area and approximate coastal containment scenario; no measured study polygon','geometry_confidence':'approximate','geometry_note':'Article Fig.1 depicts wider bathymetry; modeled domain is Israeli 0–200 m shelf, 3,725 km². A≈13–14%, B≈90–100% are explicitly approximate containment scenarios.','loadability_class':'source JSON loadable; native multi-detritus construction blocked without fate; assumed variants construct and return WARN/FAIL','full_model_loadable':False,'quality_rationale':'Published rounded tables and diet censoring do not restore a mass-balanced native model. No quality score or researcher approval inferred.','extraction_readiness':'Both periods extracted; source/fate/gray-fit/F-removal variants and direct diagnostics retained. Strict mass balance remains false.','download_status':'researcher-provided local article and author supplement verified','main_file_status':'verified original 15-page publisher PDF','supplement_status':'verified author DOCX with eight source tables','model_file_status':'eight canonical source/experimental JSON candidates retained; no native EwE export obtained','downloaded_file_count':2,'language':'English','recommendation':'Use the candidate validation reports; do not publish annual Ecopath PPR as validated. Recover unrounded native catches/parameters and explicit discard returns to resolve remaining constraints.','region_dir':'regions/EEZ/EEZ_939','article_dir':rel(PAPER),'provenance':rel(PAPER/'source_manifest.json'),'selected':False,'correction_notes':'Supplied Corrales-2010 folder alias retained; actual publication year 2017 and exact two periods verified.','loadability_evidence':'Model-local diagnostic_manifest.json, CURRENT_VARIANT_CHECK.json, model_notes.md and two candidate validation reports.','documentation_evidence':'Article Tables 1–3, author supplement sections 1–5 and all table companions with cell locators and exact source hashes.','source_urls':'https://doi.org/'+manifest['doi'],'coverage_note':'Model shelf area is 3,725 km², not the full Mediterranean EEZ. No exact target coverage ratio stored from approximate containment.','notes':'No regional selection, mapping adoption, signed review, annual model results or map refresh authorized by this candidate preparation.'}
pr.append([paper.get(k) for k in ph]);model_records=[]
for m in sorted(BASE.iterdir()):
 if not (m/'model.json').exists():continue
 assert (m/'model_notes.md').exists();data=load(m/'model.json');d=load(m/'results/diagnostics/diagnostic_manifest.json');period='1990–1994' if '1990_1994' in m.name else '2008–2012';source=m.name.endswith(('1994','2012'))
 grades={k:v.get('diagnostics',{}).get('status',v.get('status')) for k,v in d['methods'].items()};modelhash=sha(m/'model.json');variant='published source' if source else ('assumed fate + fitted gray diet + F×B removals' if 'F_removals' in m.name else ('assumed fate + fitted gray diet' if 'gray_fit' in m.name else 'assumed detritus fate'))
 assert not any(dict(zip(mh,r)).get('model_id')==m.name and dict(zip(mh,r)).get('unit_id')=='EEZ_939' for r in mr),'Refusing overwrite of an existing registered model'
 md={'unit_id':'EEZ_939','model_id':m.name,'model_path':rel(m/'model.json'),'source_filename':'model.json','selected':False,'paper_ids':article_id,'model_year':period,'variant':variant,'model_area_km2':3725,'availability':'Source-preserving JSON loads; direct construction blocked by missing native fate; all methods NOT_RUN' if source else 'Audited constructor with explicit fate restoration succeeds; GE/TE/With Egestion '+('/'.join(grades.values()))+'; strict mass balance false; unapproved candidate','publication_year':2017,'model_years':period,'coverage_class':'partial shelf','doi':manifest['doi'],'coverage_note':'Israeli continental shelf 0–200 m; approximate A13–14%, B90–100% containment scenario; 2019 catch lies outside modeled period.','validation_report_path':rel(m/'model_validation/validation.docx') if (m/'model_validation/validation.docx').exists() else None,'configuration':d.get('constructor_settings',d.get('settings')),'computational_input_sha256':d.get('source_sha256',d.get('input_sha256')),'canonical_source_path':rel(m/'model.json'),'canonical_source_sha256':modelhash,'engine_hashes':d['engine_hashes'],'diagnostic_manifest':rel(m/'results/diagnostics/diagnostic_manifest.json'),'production_eligible':False,'diagnostic_grades':grades}
 mr.append([md.get(k) for k in mh]);model_records.append(md)
# Serialize this write and check both initial and writer-internal live identities.
assert sha(PROJECT)==expected_sha,'Concurrent Project edit observed; do not overwrite'
update_book(PROJECT,{'Papers':{'Papers':(ph,pr)},'Models & coverage':{'Models':(mh,mr)}})
after=read_book(PROJECT)
for s,blocks in original.items():
 for t,(h,r) in blocks.items():
  if (s,t) in [('Papers','Papers'),('Models & coverage','Models')]:
   old=[dict(zip(h,x)) for x in r];new=[dict(zip(after[s][t][0],x)) for x in after[s][t][1]]
   for record in old:assert record in new,(s,t,record)
  else:assert digest_tables({s:{t:after[s][t]}})==digest_tables({s:{t:(h,r)}}),(s,t)
assert len([r for r in records(after,'Models & coverage','Models') if r.get('unit_id')=='EEZ_939' and r['model_id'].startswith('Corrales_2017_ICS_')])==8
assert all(r.get('researcher_review_status') is None and r.get('researcher_name') is None and r.get('selected') is False and r.get('production_eligible') is False for r in records(after,'Models & coverage','Models') if r.get('unit_id')=='EEZ_939' and r['model_id'].startswith('Corrales_2017_ICS_'))
receipt={'schema_version':1,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Narrow source metadata and eight candidate rows only','article_id':article_id,'model_ids':[m['model_id'] for m in model_records],'before_project_sha256':expected_sha,'after_project_sha256':sha(PROJECT),'unrelated_blocks_and_prior_records_preserved':True,'regional_selection_mapping_review_annual_data_unchanged':True,'researcher_approval_inferred':False,'map_refresh_performed':False}
dump(WORK/'outputs/registry_receipt.json',receipt)
for m in BASE.iterdir():
 if (m/'model.json').exists():dump(m/'extracted_tables/evidence/registry_receipt.json',receipt)
# Exact-byte source-role additions preserve the current registry and unrelated rows.
rolepath=ROOT/'common_reference_data/provenance/paper_file_roles.json';rolehash=sha(rolepath);roles=load(rolepath)
for f in manifest['files']:
 record={'path':rel(PAPER/f['path']),'sha256':f['sha256'],'role':'main' if f['role']=='article' else 'supplement','file_label':'Corrales et al. (2017) Israeli continental shelf '+('publisher article' if f['role']=='article' else 'author supplement'),'evidence':rel(PAPER/'source_manifest.json')+'; publication identity verified despite retained Corrales-2010 folder alias.'}
 assert not any(x.get('path')==record['path'] for x in roles['files']);roles['files'].append(record)
assert sha(rolepath)==rolehash
fd,tmp=tempfile.mkstemp(suffix='.json',dir=rolepath.parent);os.close(fd)
Path(tmp).write_text(json.dumps(roles,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert sha(rolepath)==rolehash;os.replace(tmp,rolepath)
print('Registered one article and eight unselected, unapproved candidates; unrelated project records preserved.',flush=True)
