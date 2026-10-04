from pathlib import Path
import urllib.request,json,hashlib,datetime
from concurrent.futures import ThreadPoolExecutor

root=Path(__file__).resolve().parents[5]
out=root/'regions/LME_027/papers/CAN-2014/recovery_20261003'
out.mkdir(parents=True,exist_ok=True)
jobs=[
 ('ecobase689_input.xml','https://ecobase.ecopath.org/php/webser/soap-client.php?no_model=689'),
 ('ecobase689_output.xml','https://ecobase.ecopath.org/php/webser/soap-client_output.php?no_model=689'),
 ('ecobase_metadata.xml','https://ecobase.ecopath.org/php/webser/soap-client_3.php'),
 ('ecobase689_card.html','https://ecobase.ecopath.org/php/protect/base_model.php?action=base&ident=&lang=&model=689&pass=&provenance=web'),
 ('publisher_article.html','https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0094742'),
 ('publisher_article.xml','https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0094742&type=manuscript'),
 ('publisher_s001.docx','https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0094742.s001&type=supplementary'),
]
def fetch(job):
 name,url=job; rec={'filename':name,'source_url':url,'access_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=45) as r:
   body=r.read(); rec.update(status_code=r.status,content_type=r.headers.get('content-type'),final_url=r.url,bytes=len(body))
  (out/name).write_bytes(body); rec['sha256']=hashlib.sha256(body).hexdigest(); rec['status']='downloaded'
 except Exception as e:rec.update(status='failed',error=str(e))
 return rec
results=list(ThreadPoolExecutor(max_workers=5).map(fetch,jobs))
(out/'retrieval_log.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print(json.dumps(results,indent=2))
