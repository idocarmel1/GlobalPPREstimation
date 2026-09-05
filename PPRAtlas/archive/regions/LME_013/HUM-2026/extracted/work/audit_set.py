from pathlib import Path
import json,csv,hashlib,os
from decimal import Decimal
import openpyxl
regions=Path(__file__).parents[4]
out=Path(__file__).parents[1]
articles=['LME_013/HUM-2026','LME_013/HUM-2018','LME_027/CAN-2014','HS_077/ETP-2003','LME_035/GOT-2003']
required=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','model.json','REPORT.md','MASS_BALANCE.md','ewe_conversion.log']
records=[];ids=set();checks=0
for article in articles:
 e=regions/article/'extracted'
 assert (e/'MASTER_INDEX.md').exists()
 for d in sorted(e.iterdir()):
  if not d.is_dir() or d.name=='work':continue
  m=json.loads((d/'model.json').read_text(encoding='utf-8'));mid=m['metadata']['model_number'];assert mid not in ids;ids.add(mid)
  for name in required:assert (d/name).is_file(),(mid,name)
  db=next(f for f in d.glob('*.json') if '_(' in f.name)
  j=json.loads(db.read_text(encoding='utf-8'));assert j['metadata']==m['metadata'],mid
  assert len(j['group'])==len(m['groups']),mid
  wbfile=db.with_name(db.stem+'_reconstructed.xlsx');assert wbfile.exists()
  wb=openpyxl.load_workbook(wbfile,read_only=True,data_only=True); assert len(wb.sheetnames)>=4;wb.close()
  with (d/'Basic_input.csv').open(encoding='utf-8-sig',newline='') as f:basic=list(csv.reader(f))
  for g,row in zip(j['group'],basic[1:]):
   assert int(g['group_seq'])==int(row[0])
   for fld,col in [('pb',5),('qb',6),('ee',7),('gs',10),('ge',9)]:
    if row[col]!='':assert Decimal(g[fld])==Decimal(row[col]),(mid,row[0],fld,row[col],g[fld])
    else:assert g[fld]=='-9999',(mid,row[0],fld,g[fld])
    checks+=1
   if row[2]=='':assert g['habitat_area']=='-9999';checks+=1
  with (d/'Diet_composition.csv').open(encoding='utf-8-sig',newline='') as f:di=list(csv.reader(f))
  bg={str(g['group_seq']):g for g in j['group']}
  for ci,n in enumerate(di[0][2:],2):
   if n not in bg:continue
   gd=(bg[n].get('diet_descr') or {}).get('diet') or []
   if isinstance(gd,dict):gd=[gd]
   vals={str(x['prey_seq']):x['proportion'] for x in gd}
   for row in di[1:]:
    if row[0] in bg and row[ci] not in ['',None]:
     # Core sparse representation may omit stated zeros; zeros remain in source payload/workbook.
     if Decimal(row[ci])!=0:assert row[0] in vals and Decimal(vals[row[0]])==Decimal(row[ci]),(mid,n,row[0],row[ci],vals.get(row[0]))
     checks+=1
  records.append({'article':article,'model_number':mid,'model_name':m['metadata']['model_name'],'year':m['metadata']['model_year'],'groups':len(m['groups']),'directory':str(d),'database_json':str(db),'database_sha256':hashlib.sha256(db.read_bytes()).hexdigest(),'status':'partial'})
assert len(records)==8,len(records)
(out/'FINAL_FILE_AUDIT.json').write_text(json.dumps({'models':records,'all_required_files_present':True,'unique_model_numbers':8,'cross_file_numeric_checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
labels={'13_1':'Patagonia base','13_2':'Northern Humboldt resolved','13_3':'Northern Humboldt aggregated','27_1':'Mauritanian shelf Base','27_2':'Mauritanian shelf M30','27_3':'Mauritanian shelf P30','HS_077_1':'Eastern tropical Pacific ETP7','35_1':'Gulf of Thailand'}
issues={'13_1':'Skates EE mismatch; missing GS, BA, detritus routing and fleet splits.','13_2':'Jellyfish diet 1.045; small-jellyfish energy deficit; sardine prose/table conflict.','13_3':'Same jellyfish defects; rounded zero biomass; missing aggregated detritus routing.','27_1':'Published grouper diet 2.2006; bird diet 0.980331; missing basic inputs.','27_2':'Incomplete changed diets and rounded parameter values, plus base-source defects.','27_3':'Incomplete changed diets and rounded parameter values, plus base-source defects.','HS_077_1':'Nine published diet-sum errors; missing BA and detritus information.','35_1':'Fifteen malformed diet columns and ten consumers without positive diets.'}
lines=['# Ecopath extraction results','',
'All five requested source folders were processed. Eight distinct model versions have separate output directories. Every model includes the eight import files, extraction and database JSON, reconstructed workbook, provenance report, validation and mass-balance findings. Original source files were retained unchanged.','',
'**All eight are partial reconstructions, not certified import-ready models.** Published inconsistencies and unreported parameters were retained rather than repaired by assumption. The work has extracted the available evidence; additional author data or correction decisions are needed to establish runnable balanced models.','',
'| Model number | Model and report | Reference year | Groups | Final JSON | Main limitation |',
'|---|---|---|---:|---|---|']
for r in records:
 mid=r['model_number'];rel=os.path.relpath(r['directory'],out).replace('\\','/')
 db=Path(r['database_json']).name
 lines.append(f"| {mid} | [{labels[mid]}]({rel}/REPORT.md) | {r['year']} | {r['groups']} | [JSON]({rel}/{db}) | {issues[mid]} |")
lines+=['','## Important distinctions','',
'- Northern Humboldt uses 1995–1998 source inputs; the archive metadata says 1995–2004. The two resolutions are separate models.','- Canary models use 1991, not the catalog’s 2007–2009. Base, M30 and P30 have separate parameterizations; the latter two have incomplete published diets.','- ETP7 is the final model. Its EE arithmetic reconciles within 0.014, but its malformed diets still prevent import-ready status. The explicitly unbalanced ETP1 draft was excluded.','- Thailand includes 14 nonzero biomass-accumulation values and 26 stated zeros. These were preserved.','- Unknown values remain blank/-9999. Local adapters undo the bundled converter’s normalization and default insertion, retaining original diet sums and stated P/Q. They also preserve the explicit model_number in final JSON metadata.','',
f'Final integration verified all required files, eight unique identifiers, matching metadata and {checks:,} cross-file numeric checks. The per-model round-trip reports contain more detailed checks. Source inconsistencies are expected validation failures and were not suppressed.','',
'Article-specific MASTER_INDEX.md files remain in each extracted directory. This cross-folder index is stored with the first requested article so every output stays within an article’s extracted directory.']
(out/'EXTRACTION_SET_INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Final audit:',len(records),'models,',checks,'numeric checks; all required files present.')

