"""Find indexed repository copies for blocked main sources; downloads remain separate."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,requests
ROOT=Path(__file__).resolve().parent

def discover(a):
    doi=a['doi'].replace('https://doi.org/','').strip()
    record={'article_id':a['article_id'],'doi':doi,'download_urls':[]}
    try:
        url='https://api.openalex.org/works/https://doi.org/'+doi
        rr=requests.get(url,timeout=25);record['lookup_url']=url;record['http_status']=rr.status_code;rr.raise_for_status()
        data=rr.json();record['indexed_title']=data.get('title')
        for location in data.get('locations',[]):
            for key in ['pdf_url','landing_page_url']:
                if location.get(key):record['download_urls'].append({'url':location[key],'role':'main','discovered_via':url})
    except Exception as exc:record['error']=str(exc)
    return record

if __name__=='__main__':
    sources={a['article_id']:dict(a) for a in json.loads((ROOT/'inputs/original_catalog.json').read_text(encoding='utf-8'))['articles']}
    for pattern in ('eez_*.json','lme_*.json'):
        for path in (ROOT/'research').glob(pattern):
            d=json.loads(path.read_text(encoding='utf-8'))
            for a in d['articles']:sources.setdefault(a['article_id'],a)
            for update in d.get('existing_source_updates',[]):
                if update.get('doi') and update['article_id'] in sources:sources[update['article_id']]['doi']=update['doi']
    todo=[]
    for a in sources.values():
        if not a.get('doi'):continue
        p=ROOT/'research/downloads'/f"{a['article_id']}.json"
        log=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'files':[]}
        if not any(f.get('role')=='main' and f['status']=='downloaded_verified' for f in log['files']):todo.append(a)
    with ThreadPoolExecutor(max_workers=5) as pool:result=list(pool.map(discover,todo))
    (ROOT/'research/alternate_discovery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Repository metadata lookups',len(result),'candidate routes',sum(len(x['download_urls']) for x in result))
