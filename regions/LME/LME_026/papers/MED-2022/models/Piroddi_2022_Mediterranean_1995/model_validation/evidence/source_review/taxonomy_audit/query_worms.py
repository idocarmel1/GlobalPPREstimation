from pathlib import Path
import json,urllib.request,urllib.parse,concurrent.futures,datetime,re,sys
O=Path(__file__).resolve().parent
labels=json.loads((O/'catch_label_universe.json').read_text(encoding='utf-8'))
source_mode='source' in sys.argv
names=[r['taxon'] for r in labels]+['Liza aurata','Liza ramada','Liza saliens','Trigloporus lastoviza','Crassostrea gigas','Scomberesox saurus saurus','Oblada melanura','Naucrates doctor','Carcharia taurus','Spicara maena','Trisopterus capelanus']
if source_mode:
    groups=json.loads((O/'source_group_definitions.json').read_text(encoding='utf-8'))
    names=sorted(set(t.strip() for g in groups for t in re.findall(r'\b[A-Z][a-z]+\s+[a-z][a-z-]+(?:\s+[a-z]+)?',g['description'].split(':',1)[-1]) if 'not documented' not in t))
chunks=[names[i:i+25] for i in range(0,len(names),25)]
def fetch(chunk):
    url='https://www.marinespecies.org/rest/AphiaRecordsByNames?'+urllib.parse.urlencode([('scientificnames[]',n) for n in chunk]+[('marine_only','false')])
    record={'query_names':chunk,'url':url,'retrieval_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'access':'full_API_response'}
    try:
        with urllib.request.urlopen(url,timeout=35) as response: record['results']=json.loads(response.read());record['status']='read'
    except Exception as exc:record.update(status='failed',error=str(exc),results=[])
    return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: batches=list(pool.map(fetch,chunks))
(O/('worms_source_api_evidence.json' if source_mode else 'worms_api_evidence.json')).write_text(json.dumps(batches,indent=2,ensure_ascii=True),encoding='utf-8')
lookup={}
for b in batches:
    for n,r in zip(b['query_names'],b['results']):lookup[n]=r or []
(O/('worms_source_name_lookup.json' if source_mode else 'worms_name_lookup.json')).write_text(json.dumps(lookup,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'batches':len(batches),'read':sum(b['status']=='read' for b in batches),'failed':[b['query_names'] for b in batches if b['status']!='read'],'names':len(lookup),'found':sum(bool(v) for v in lookup.values())},ensure_ascii=True))
