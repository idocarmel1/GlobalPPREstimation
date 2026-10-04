from pathlib import Path
import concurrent.futures,json,urllib.request,urllib.parse,datetime,csv
OUT=Path(__file__).parent
names=['Gadidae','Gadiformes','Clupeidae','Clupeiformes','Scophthalmidae','Pleuronectiformes','Pollachius pollachius','Trisopterus esmarkii','Micromesistius poutassou','Molva molva','Brosme brosme','Phycis blennoides','Enchelyopus cimbrius','Gaidropsarus vulgaris','Clupea harengus','Sprattus sprattus','Sardina pilchardus','Alosa alosa','Scophthalmus rhombus','Lepidorhombus whiffiagonis','Scophthalmus maximus','Lithodes maja','Magallana gigas','Buccinum undatum','Chimaera monstrosa','Hydrolagus','Rhinochimaera atlantica','Perciformes','Scombridae','Thunnus thynnus','Coregonus','Salmo salar','Salmo trutta','Lota lota','Rutilus rutilus','Cyprinidae','Meganyctiphanes norvegica']
names=list(dict.fromkeys(names+[r['taxon'] for r in csv.DictReader((OUT.parent/'taxa_review.tsv').open(encoding='utf-8'),delimiter='\t')]))
def one(n):
 u='https://www.marinespecies.org/rest/AphiaRecordsByName/'+urllib.parse.quote(n,safe='')+'?like=false&marine_only=false'
 try:
  with urllib.request.urlopen(u,timeout=35) as r:d=json.load(r)
  return {'query':n,'url':u,'records':d,'error':None}
 except Exception as e:return {'query':n,'url':u,'records':None,'error':str(e)}
cache_path=OUT/'taxonomy_primary_records.json'
cached=json.loads(cache_path.read_text(encoding='utf-8'))['rows'] if cache_path.exists() else []
byname={r['query']:r for r in cached if not r.get('error')}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e: newrows=list(e.map(one,[n for n in names if n not in byname]))
byname.update({r['query']:r for r in newrows})
rows=[byname[n] for n in names]
(OUT/'taxonomy_primary_records.json').write_text(json.dumps({'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authority':'WoRMS Aphia REST records','rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
for row in newrows:
 records=row.get('records') or []
 r=next((r for r in records if r.get('scientificname')==row['query']),records[0] if records else {})
 print(json.dumps({'query':row['query'],'accepted':r.get('valid_name'),'status':r.get('status'),'family':r.get('family'),'order':r.get('order'),'url':r.get('url'),'error':row.get('error')},ensure_ascii=True))
