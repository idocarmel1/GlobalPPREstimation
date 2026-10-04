from pathlib import Path
import json,urllib.request,urllib.parse,concurrent.futures,time
C=Path(__file__).resolve().parents[1]; M=C/'mapping'
ref=json.loads((C/'calculations/reference_inputs.json').read_text(encoding='utf-8'))
genera={'Sphyraena','Tylosurus','Chelon','Liza','Mugil','Eucinostomus','Gerres','Argyrosomus','Sciaena','Umbrina','Pteroscion','Pseudotolithus','Alectis','Campogramma','Caranx','Decapterus','Elagatis','Lichia','Pseudocaranx','Scyris','Selene','Seriola','Trachinotus','Trachurus','Chloroscombrus','Dasyatis','Bathytoshia','Psettodes','Plectorhinchus','Pomadasys','Carlarius','Elops','Cynoglossus'}
benthicmolluscs={'Acanthocardia','Bivalvia','Callista','Cerastoderma','Chamelea','Crassostrea','Cymbium','Donax','Gastropoda','Haliotis','Murex','Mytilidae','Patella','Pteriomorphia','Veneridae'}
families={'Carangidae','Sciaenidae','Mugilidae','Sphyraenidae','Psettodidae','Dasyatidae','Haemulidae'}
names=sorted({r['taxon'] for r in ref if r['taxon'].split()[0] in genera|benthicmolluscs|families or r['functional_group']=='Cephalopods'})
names=sorted(set(names)|{'Tylosorus crocodilus','Tylosurus crocodilus','Decapterus rhonchus','Pomadasys rogeri','Arius heudeloti','Arius heudelotii','Sphyraena guachancho','Sphyraena guanchancho','Liza grandisquamis','Liza falcipinnis','Penaeus duorarum','Penaeus notialis','Portunidae','Echinoidea','Paracentrotus lividus'})
cache=M/'authoritative_taxonomy_raw.json'
existing=json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
def fetch(name):
 url='https://www.marinespecies.org/rest/AphiaRecordsByName/'+urllib.parse.quote(name,safe='')+'?like=false&marine_only=true'
 try:
  with urllib.request.urlopen(url,timeout=30) as f:
   raw=f.read().decode();records=json.loads(raw) if raw else []
  return name,{'url':url,'retrieved':'2026-10-03','records':records,'error':None}
 except Exception as e: return name,{'url':url,'retrieved':'2026-10-03','records':[],'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for name,result in ex.map(fetch,[n for n in names if n not in existing]):
  existing[name]=result
  cache.write_text(json.dumps(existing,ensure_ascii=False,indent=2),encoding='utf-8')
selected={}
for name,entry in existing.items():
 recs=[r for r in entry['records'] if r.get('scientificname','').casefold()==name.casefold() and r.get('rank') not in ['Subgenus','Subspecies','Variety','Form','Unranked']]
 if len(recs)==1: selected[name]=recs[0]
 elif len(recs)>1:
  accepted=[r for r in recs if r.get('status')=='accepted']
  if len(accepted)==1: selected[name]=accepted[0]
(M/'authoritative_taxonomy_selected.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'requested':len(names),'returned':len(existing),'selected_unique':len(selected),'unresolved':sorted(set(names)-set(selected))},ensure_ascii=False,indent=2))
