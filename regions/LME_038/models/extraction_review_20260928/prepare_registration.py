"""Reconcile source identity and portable candidate paths before central registration."""
from pathlib import Path
import json,hashlib,zipfile,os,copy
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent;REG=ROOT/'regions/LME_038'
aliases={'BUCHARY1999_JavaSea_mid1970s':'38_38001_Java_Sea_(mid1970s)','NURHAKIM2003_NorthCentralJava_1979':'38_38002_North_Coast_Central_Java_(1979)'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
expected={'38_38001_Java_Sea_(mid1970s)':'1740de76fad9cabab2791209cf96c73e8271e431ae4d6e5b858fa9fa6329b4ef','38_38002_North_Coast_Central_Java_(1979)':'5b75b4031a2fe321efce78645d6b8a59e332c30fcbe007eb091c70e499318318'}
changes=[]
for p in (REG/'models').rglob('*'):
 if not p.is_file() or p==Path(__file__):continue
 if p.suffix.lower() in ['.json','.md','.py','.log','.csv','.txt']:
  text=p.read_text(encoding='utf8',errors='strict');new=text
  for old,now in aliases.items():new=new.replace(old,now)
  if new!=text:p.write_text(new,encoding='utf8');changes.append(p.relative_to(ROOT).as_posix())
 elif p.name=='candidate_diagnostics.xlsx':
  with zipfile.ZipFile(p) as z:infos=z.infolist();parts={i.filename:z.read(i.filename) for i in infos}
  updated={}
  for k,v in parts.items():
   n=v
   for old,now in aliases.items():n=n.replace(old.encode(),now.encode())
   if n!=v:updated[k]=n
  if updated:
   temp=p.with_suffix('.repair.xlsx')
   with zipfile.ZipFile(temp,'w') as z:
    for i in infos:z.writestr(i,updated.get(i.filename,parts[i.filename]))
   os.replace(temp,p);changes.append(p.relative_to(ROOT).as_posix())
for mid,h in expected.items():assert sha(REG/'models'/mid/'model.json')==h
for folder in ['BUCHARY-1991','LME038-Nurhakim-2003']:
 pdf=next((REG/'papers'/folder).glob('*.pdf'));mid=list(expected)[folder!='BUCHARY-1991'];manifest=json.loads((REG/'models'/mid/'evidence/source_manifest.json').read_text(encoding='utf8'));assert sha(pdf)==manifest['sha256']
# Fix replay helper branch conditions following folder identity alignment.
p=OUT/'validate_and_stage.py';text=p.read_text(encoding='utf8').replace("mid.startswith('BUCH')","mid.startswith('38_38001')").replace("mid.startswith('NUR')","mid.startswith('38_38002')");p.write_text(text,encoding='utf8')
proposal=json.loads((OUT/'metadata_proposal.json').read_text(encoding='utf8'));bp,np=proposal['paper_upserts'];bp['article_id']='INDO-1999__LME_038';bp['source_article_id']='INDO-1999'
reconciliation=('The existing INDO-1999 Buchary1999/Java Sea/thesis placeholder is reconciled to the supplied UBC MSc thesis (April1999, Eny Anggraini Buchary), not added as a second paper. Legacy archive contained no source PDF/hash, degree/institution or verified full title, so placeholder association is inferred from matching author/year/place and explicit thesis-recovery note. Full citation now comes from inspected title page. Supplied folder BUCHARY-1991 remains an alias;1991 is prior degree year. The preserved EcoBase410 link is unverified as the same numerical variant. Legacy36% was a bbox estimate, is not verified source coverage and is cleared from target_coverage_ratio; its history remains here and in frozen metadata. No duplicate publication identity is claimed.')
bp['correction_notes']=reconciliation;bp['legacy_title']='Marine ecosystem and fisheries in the Java Sea: an Ecopath assessment';bp['legacy_authors']='Buchary';bp['legacy_landing_page']='https://ecobase.ecopath.org/php/protect/base_model.php?action=base&model=410';bp['geometry_note']='Legacy bbox-based target fraction0.36 retained in archive only; not verified and not used. Supplied thesis describes Java Sea471000 km2, not a digital LME intersection.';bp['download_failure_reason']=None;bp['notes']+='; '+reconciliation;bp['quality_rationale']='Legacy scores retained unchanged for historical continuity; source now extracted but incomplete Macrozoobenthos diet prevents strict admission. Loader-normalized diagnostics are not source validity.'
for m in proposal['model_upserts']:
 if m['model_id'].startswith('38_38001'):m['paper_ids']='INDO-1999__LME_038'
for p in [REG/'models'/list(expected)[0]/'extracted_tables/REPORT.md',OUT/'source_use_audit.json']:
 txt=p.read_text(encoding='utf8');txt=txt.replace('Existing INDO-1999 catalog\'s36% and EcoBase410 link are unverified legacy claims and are not inherited here.','Existing INDO-1999 is the reconciled bibliographic placeholder for this supplied thesis; its former36% and EcoBase410 numeric linkage remain unverified legacy claims and are not inherited here.')
 if p.suffix=='.md':txt+='\nCentral citation reconciliation: '+reconciliation+'\n'
 else:
  d=json.loads(txt);d['legacy_relationship']=reconciliation;txt=json.dumps(d,indent=2,ensure_ascii=False)
 p.write_text(txt,encoding='utf8')
save(OUT/'central_metadata_proposal.json',{'paper_updates':[{'article_id':r['article_id'],'changes':{k:v for k,v in r.items() if k not in ['article_id','unit_id','selected']}} for r in [bp,np]],'model_rows_to_register':proposal['model_upserts']})
proposal['paper_upserts']=[bp,np];proposal['identity_reconciliation']=reconciliation;save(OUT/'metadata_proposal.json',proposal)
save(OUT/'IDENTITY_AND_PATH_RECONCILIATION.json',{'identity_decision':reconciliation,'legacy_evidence':['regions/LME_038/papers/INDO-1999/metadata.json','original_research_archive/research/atlas_development_2026_09/inputs/legacy/0928.json','original_research_archive/research/atlas_development_2026_09/research/downloads/INDO-1999.json'],'external_corroboration':'https://www.seaaroundus.org/wp-content/uploads/2025/09/Pauly-CV-to-September-2025.pdf','external_check':'EcoBase410 request returned internal error; no numerical equivalence established. Thesis-supervisor bibliography matches title/author/year/MSc/UBC.','folder_aliases':aliases,'canonical_hashes_before_and_after_identical':expected,'source_pdf_hashes_unchanged':True,'portable_links_repaired':changes})
# Adapt the established OOXML-only registrar; no workbook resave via openpyxl.
helper=(ROOT/'regions/LME_049/models/extraction_review_20260928/register_central_metadata.py').read_text(encoding='utf8').replace('LME_049','LME_038').replace('LME049','LME038').replace('rank==12','rank==13').replace('atlas rank12','atlas rank13').replace(" and item['selection_rationale'] is None",'')
(OUT/'register_central_metadata.py').write_text(helper,encoding='utf8')
print('Reconciled existing INDO-1999; two existing paper updates, two unselected model additions; canonical/source bytes unchanged.')
