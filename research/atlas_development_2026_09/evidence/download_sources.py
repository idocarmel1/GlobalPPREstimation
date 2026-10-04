"""Retrieve curated public URLs; record failures and validate actual response bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from io import BytesIO
import json, re, argparse, mimetypes, hashlib
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from atlas.files import save_material

ROOT=Path(__file__).resolve().parent

def suffix_for(response):
    data=response.content
    if data.lstrip().startswith(b'%PDF-'): return '.pdf'
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return '.png'
    if data.startswith(b'\xff\xd8\xff'): return '.jpg'
    if data.startswith((b'II*\x00',b'MM\x00*')):return '.tif'
    path=urlparse(response.url).path.lower()
    if data.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):
        import olefile
        with olefile.OleFileIO(BytesIO(data)) as doc:
            if doc.exists('WordDocument'):return '.doc'
            if doc.exists('Workbook') or doc.exists('Book'):return '.xls'
    content=response.headers.get('Content-Type','').lower()
    if data.startswith(b'PK'):
        import zipfile
        with zipfile.ZipFile(BytesIO(data)) as z:
            if 'xl/workbook.xml' in z.namelist(): return '.xlsx'
            if 'word/document.xml' in z.namelist(): return '.docx'
        return '.zip'
    if 'text/csv' in content or path.endswith('.csv'): return '.csv'
    return None

def unwrap_archived_pdf(response):
    """Recover a PDF wrapped in literal archived HTTP headers, preserving provenance."""
    raw=response.content
    marker=raw.find(b'%PDF-',0,4096)
    if raw.startswith((b'HTTP/1.0 ',b'HTTP/1.1 ')) and marker>0 and b'%%EOF' in raw[-4096:]:
        raw_hash=hashlib.sha256(raw).hexdigest()
        path=ROOT/'research/http_wrappers'/f'{raw_hash[:20]}.http'
        path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(raw)
        response._content=raw[marker:]
        return {'transformation':'Removed literal archived HTTP response headers preceding the PDF payload','removed_prefix_bytes':marker,'raw_response_sha256':raw_hash,'raw_response_path':path.relative_to(ROOT).as_posix()}
    return {}

def retrieve(article):
    aid=article['article_id']; queue=list(article.get('download_urls',[]))
    if not queue and article.get('landing_page'):
        queue=[{'url':article['landing_page'],'role':'main'}]
    tried=set(); attempts=[]; files=[]; session=requests.Session()
    while queue and len(tried)<16:
        candidate=queue.pop(0); url=candidate['url']; role=candidate.get('role','main')
        if url in tried or not url.startswith(('http://','https://')): continue
        tried.add(url)
        attempt={'article_id':aid,'url':url,'role':role,'attempted_on':'2026-09-04','discovered_via':candidate.get('discovered_via','curated source or source-page link')}
        try:
            response=session.get(url,timeout=(12,35),headers={'User-Agent':'Mozilla/5.0 (research source archive)'})
            attempt.update(http_status=response.status_code,final_url=response.url,size_bytes=len(response.content))
            response.raise_for_status()
            transformation=unwrap_archived_pdf(response)
            suffix=suffix_for(response)
            if suffix:
                record=save_material(ROOT,response.content,suffix)
                record.update(transformation)
                filename=candidate.get('filename') or Path(urlparse(response.url).path).name or (aid+suffix)
                record.update(article_id=aid,role=role,source_url=url,final_url=response.url,filename=filename,retrieval_origin='public_web')
                if suffix=='.pdf':
                    reader=PdfReader(BytesIO(response.content))
                    text_parts=[]
                    for p in reader.pages:
                        try:text_parts.append(p.extract_text() or '')
                        except Exception:text_parts.append('[Text extraction failed for this page; PDF structure verified]')
                    text='\n'.join(text_parts)
                    textpath=ROOT/'research/text'/f"{record['sha256'][:20]}.txt"
                    textpath.parent.mkdir(parents=True,exist_ok=True)
                    textpath.write_text(text,encoding='utf-8')
                    record['text_preview']=text[:1800]
                    record['text_path']=textpath.relative_to(ROOT).as_posix()
                files.append(record);attempt['result']='downloaded_verified'
            else:
                attempt['result']='landing_page_only'
                soup=BeautifulSoup(response.content,'html.parser')
                candidates=[]
                for meta in soup.find_all('meta'):
                    if meta.get('name','').lower()=='citation_pdf_url' and meta.get('content'):
                        candidates.append(meta['content'])
                for link in soup.find_all('a',href=True):
                    href=link['href']; label=link.get_text(' ',strip=True).lower()
                    filelike=re.search(r'\.pdf(?:$|\?)|/bitstreams/.*/download|/article-pdf/|/download/(?:file|pdf)|/pdf(?:$|\?)',href,re.I)
                    if filelike and any(term in label for term in ['pdf','download','full text','full-text']): candidates.append(urljoin(response.url,href))
                for href in dict.fromkeys(candidates[:5]):
                    if href not in tried: queue.append({'url':href,'role':role})
        except Exception as exc:
            attempt.update(result='failed',error=str(exc)[:700])
            if url.startswith('http://'):
                queue.append(dict(candidate,url='https://'+url[7:],discovered_via='HTTPS variant of indexed public URL'))
        attempts.append(attempt)
    return {'article_id':aid,'files':files,'attempts':attempts}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--retry',action='store_true');args=parser.parse_args()
    original=json.loads((ROOT/'inputs/original_catalog.json').read_text(encoding='utf-8'))
    catalog={a['article_id']:dict(a) for a in original['articles']}
    for path in sorted(list((ROOT/'research').glob('eez_*.json'))+list((ROOT/'research').glob('lme_*.json'))):
        result=json.loads(path.read_text(encoding='utf-8'))
        for a in result['articles']: catalog[a['article_id']]=a
        for update in result.get('existing_source_updates',[]):
            if update.get('download_urls'):
                catalog.setdefault(update['article_id'],{'article_id':update['article_id']}).setdefault('download_urls',[]).extend(update['download_urls'])
    catalog['ECS-2022']={'article_id':'ECS-2022','download_urls':[{'url':'https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.865645/pdf','role':'main'}]}
    zotero=ROOT/'research/zotero_sources.json'
    for discovered in ['supplement_discovery.json','alternate_discovery.json']:
        path=ROOT/'research'/discovered
        if path.exists():
            for item in json.loads(path.read_text(encoding='utf-8')):
                if item['article_id'] in catalog:catalog[item['article_id']].setdefault('download_urls',[]).extend(item.get('download_urls',[]))
    if zotero.exists():
        for item in json.loads(zotero.read_text(encoding='utf-8')).get('items',[]):
            if item.get('match_status')=='mismatch':continue
            if item['article_id'] not in catalog:continue
            entry=catalog[item['article_id']]
            entry.setdefault('download_urls',[])
            if item.get('url'):entry['download_urls'].append({'url':item['url'],'role':'main','discovered_via':'Zotero URL'})
            if item.get('doi'):entry['download_urls'].append({'url':'https://doi.org/'+item['doi'].replace('https://doi.org/',''),'role':'main','discovered_via':'Zotero DOI'})
            html_enclosures={detail.get('enclosure_url') for detail in item.get('attachment_details',[]) if detail.get('content_type')=='text/html'}
            entry['download_urls'].extend({'url':u,'role':'main','discovered_via':'Zotero attachment'} for u in item.get('attachment_urls',[]) if u not in html_enclosures)
    for a in catalog.values():
        urls=list(a.get('download_urls',[]))
        if a.get('landing_page'):urls.append({'url':a['landing_page'],'role':'main'})
        if a.get('doi'):urls.append({'url':'https://doi.org/'+a['doi'].replace('https://doi.org/',''),'role':'main'})
        a['download_urls']=list({x['url']:x for x in urls}.values())
    directory=ROOT/'research/downloads';directory.mkdir(parents=True,exist_ok=True)
    todo=[]
    for aid,a in catalog.items():
        previous=directory/f'{aid}.json'
        old=json.loads(previous.read_text(encoding='utf-8')) if previous.exists() else None
        attempted={x['url'] for x in old['attempts']} if old else set()
        candidates=a.get('download_urls',[]) or [{'url':a['landing_page'],'role':'main'}]
        pending=[x for x in candidates if x['url'] not in attempted]
        if args.retry or pending or not old:
            item=dict(a,download_urls=candidates if args.retry or not old else pending)
            item['_previous']=old;todo.append(item)
    print('Articles to retrieve:',len(todo),flush=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(retrieve,a):a for a in todo}
        for future in as_completed(futures):
            result=future.result();old=futures[future].get('_previous')
            if old:
                result['files']=old['files']+result['files'];result['attempts']=old['attempts']+result['attempts']
            (directory/f"{result['article_id']}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            print(result['article_id'],len(result['files']),'files,',len(result['attempts']),'attempts',flush=True)

if __name__=='__main__':main()
