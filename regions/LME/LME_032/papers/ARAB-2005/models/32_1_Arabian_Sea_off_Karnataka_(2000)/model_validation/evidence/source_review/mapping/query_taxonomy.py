from pathlib import Path
import csv,json,urllib.request,urllib.parse,concurrent.futures,datetime
R=Path(__file__).resolve().parent.parent
ROOT=next(p for p in R.parents if (p/'Project.xlsx').exists())
p=next((ROOT/'regions/LME_032').glob('models/*/source_evidence/mapping/*(2000).csv'))
rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
names=sorted(set(x['taxon'] for x in rows if not any(t in x['taxon'].lower() for t in ['not identified','miscellaneous'])))
members=list(csv.DictReader(next(p.parent.glob('*.members.csv')).open(encoding='utf-8-sig')))
names=sorted(set(names+[x['printed_name'].replace(' sp.','').replace(' spp.','') for x in members if len(x['printed_name'].split())<=2 and not any(c in x['printed_name'] for c in ['Jelly','larvae','elvers'])]))
def query(batch):
 url='https://www.marinespecies.org/rest/AphiaRecordsByNames?'+urllib.parse.urlencode([('scientificnames[]',s) for s in batch]+[('marine_only','true')])
 try:
  data=json.loads(urllib.request.urlopen(url,timeout=50).read())
  return {'names':batch,'url':url,'retrieved':'2026-09-30','results':data}
 except Exception as e:return {'names':batch,'url':url,'error':repr(e)}
batches=[names[i:i+20] for i in range(0,len(names),20)]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:result=list(ex.map(query,batches))
(R/'mapping/WoRMS_response.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
flat={}
for x in result:
 for name,recs in zip(x['names'],x.get('results',[])):
  exact=[z for z in recs if z.get('scientificname','').lower()==name.lower()]
  if exact:flat[name]=sorted(exact,key=lambda z:(z.get('status')!='accepted',z['AphiaID']))[0]
(R/'mapping/taxonomy_lookup.json').write_text(json.dumps(flat,ensure_ascii=False,indent=2),encoding='utf-8')
print('queried',len(names),'exact',len(flat),'failed_batches',sum('error' in x for x in result))
print('missing',[s for s in names if s not in flat])
