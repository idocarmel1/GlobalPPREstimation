"""Discover publisher-deposited supplements by exact source DOI in Figshare."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,requests
ROOT=Path(__file__).resolve().parent

def discover(source):
    aid=source['article_id'];doi=(source.get('doi') or '').lower().replace('https://doi.org/','').strip()
    record={'article_id':aid,'doi':doi,'routes':[],'download_urls':[]}
    if not doi:return record
    try:
        response=requests.post('https://api.figshare.com/v2/articles/search',json={'search_for':doi,'limit':100},timeout=30)
        record['routes'].append({'url':response.url,'query':doi,'status':response.status_code})
        response.raise_for_status()
        for item in response.json():
            if str(item.get('resource_doi','')).lower()!=doi:continue
            rr=requests.get(item['url'],timeout=30);rr.raise_for_status()
            for f in rr.json().get('files',[]):
                record['download_urls'].append({'url':f['download_url'],'filename':f['name'],'role':'supplement','discovered_via':item['url_public_html']})
    except Exception as exc:record['error']=str(exc)
    return record

if __name__=='__main__':
    sources={a['article_id']:a for a in json.loads((ROOT/'inputs/original_catalog.json').read_text(encoding='utf-8'))['articles']}
    for pattern in ('eez_*.json','lme_*.json'):
        for path in (ROOT/'research').glob(pattern):
            result=json.loads(path.read_text(encoding='utf-8'));sources.update({a['article_id']:a for a in result['articles']})
            for update in result.get('existing_source_updates',[]):
                if update.get('doi') and update['article_id'] in sources:sources[update['article_id']]=dict(sources[update['article_id']],doi=update['doi'])
    cached_path=ROOT/'research/supplement_discovery.json'
    cached=json.loads(cached_path.read_text(encoding='utf-8')) if cached_path.exists() else []
    done={(r['article_id'],r['doi']) for r in cached if not r.get('error')}
    todo=[s for s in sources.values() if s.get('doi') and (s['article_id'],s['doi'].lower().replace('https://doi.org/','').strip()) not in done]
    with ThreadPoolExecutor(max_workers=5) as pool:
        for record in pool.map(discover,todo):
            cached=[r for r in cached if r['article_id']!=record['article_id']]+[record]
            cached_path.write_text(json.dumps(cached,indent=2),encoding='utf-8')
            print(record['article_id'],len(record['download_urls']),'supplement routes discovered; retrieval pending',flush=True)
