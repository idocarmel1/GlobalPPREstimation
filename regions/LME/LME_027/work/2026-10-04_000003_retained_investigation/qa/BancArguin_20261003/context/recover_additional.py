from pathlib import Path
import urllib.request,json,hashlib,datetime,time
out=Path(__file__).resolve().parents[5]/'regions/LME_027/papers/CAN-2014/recovery_20261003'
logs=[]
def fetch(name,url,data=None):
 rec={'filename':name,'source_url':url,'request_body':data,'access_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json','User-Agent':'Scientific evidence review'})
  with urllib.request.urlopen(req,timeout=50) as r:
   b=r.read();rec.update(status_code=r.status,content_type=r.headers.get('content-type'),final_url=r.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='downloaded')
  (out/name).write_bytes(b);logs.append(rec);return b
 except Exception as e:rec.update(status='failed',error=str(e));logs.append(rec);return None
for q,tag in [('10.1371/journal.pone.0094742','doi'),('Banc Arguin','place')]:
 b=fetch('figshare_search_'+tag+'.json','https://api.figshare.com/v2/articles/search',{'search_for':q,'limit':100})
 if b:
  hits=json.loads(b);print([(h['id'],h['title']) for h in hits])
  for h in hits:
   if '2014' in h.get('published_date','') or '0094742' in str(h):
    time.sleep(1)
    fetch('figshare_record_'+str(h['id'])+'.json',h['url'])
 time.sleep(1)
fetch('Meissa2013_thesis.pdf','https://www.imrop.mr/wp-content/uploads/2021/01/these_-beyah-VF-1.pdf')
fetch('Meissa2014_conference.pdf','https://halieutique.institut-agro.fr/files/fichiers/pdf/4892.pdf')
(out/'additional_retrieval_log.json').write_text(json.dumps(logs,indent=2),encoding='utf8')
print([(x['filename'],x['status'],x.get('bytes'),x.get('error')) for x in logs])
