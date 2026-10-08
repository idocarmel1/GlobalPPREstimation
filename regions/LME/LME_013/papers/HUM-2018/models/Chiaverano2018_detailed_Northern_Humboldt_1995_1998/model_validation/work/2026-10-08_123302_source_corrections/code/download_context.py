"""Bounded acquisition of two primary contextual sources; retain successful PDFs."""
from pathlib import Path
import hashlib
import json
try:
    from pip._vendor import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass
import requests
from bs4 import BeautifulSoup
import pymupdf

RUN = Path(__file__).resolve().parents[1]
MODEL = Path(__file__).resolve().parents[4]
SOURCES = MODEL.parents[1] / 'sources'
CONTEXT = SOURCES / 'context'
session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 academic source verification'
attempts = []

def retrieve(url, name, role):
    record = {'url': url, 'filename': name, 'role': role}
    try:
        response = session.get(url, timeout=(15, 35))
        record.update(http_status=response.status_code, final_url=response.url)
        response.raise_for_status()
        data = response.content
        if len(data)>50_000_000 or not data.startswith(b'%PDF'):
            raise ValueError('Response is not a bounded PDF.')
        pdf = pymupdf.open(stream=data, filetype='pdf')
        record.update(pages=len(pdf), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        CONTEXT.mkdir(parents=True, exist_ok=True)
        target = CONTEXT / name
        if target.exists() and target.read_bytes()!=data:
            raise ValueError('Existing contextual source has different bytes; not overwritten.')
        target.write_bytes(data)
        record.update(status='verified_pdf', path=str(target.relative_to(SOURCES)).replace('\\','/'))
    except Exception as error:
        record.update(status='unavailable', error=str(error))
    attempts.append(record)
    print(name, record['status'], flush=True)

retrieve('https://repositorio.imarpe.gob.pe/bitstreams/e3542f35-f499-4be6-8db8-a544556b50cd/download',
         'Quinones2018_doctoral_thesis.pdf',
         'Primary author thesis; examine focal model chapter for earlier parameter versions; not replacement baseline.')
try:
    page = session.get('https://www.nature.com/articles/srep12037', timeout=(15,35))
    page.raise_for_status()
    soup = BeautifulSoup(page.text, 'html.parser')
    links = [a for a in soup.find_all('a',href=True)
             if 'Supplementary Information' in a.get_text() and '.pdf' in a['href']]
    if not links:
        raise ValueError('Publisher supplement link absent from retrieved page.')
    from urllib.parse import urljoin
    retrieve(urljoin(page.url, links[0]['href']), 'Ceh2015_supplement_srep12037.pdf',
             'Primary cited dietary observations; check source support for reconstructed jellyfish diet.')
except Exception as error:
    attempts.append({'url':'https://www.nature.com/articles/srep12037',
                     'status':'unavailable','error':str(error),
                     'role':'Resolve primary dietary supplement link'})

out = RUN/'outputs/source_downloads.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(attempts,ensure_ascii=False,indent=2),encoding='utf-8')
