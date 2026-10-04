from pathlib import Path
import requests,concurrent.futures,json,hashlib,time
BASE=Path(__file__).resolve().parent
urls={
'Griffiths2019/Griffiths2019_Appendices.pdf':'https://www.researchgate.net/profile/Shane-Griffiths/publication/325700136_Griffiths_FOG-17-1431_Early_View_Supp_Info/data/5b9feef0299bf13e6038a3f9/Warm-Pool-Ecopath-FAD-Griffiths-et-al-2018-APPENDICES.pdf',
'Griffiths2019/Griffiths2019_Appendices.docx':'https://onlinelibrary.wiley.com/doi/suppl/10.1111/fog.12389/supinfo/fog12389-sup-0001-appendixs1-s4.docx',
'Griffiths2019/Griffiths2019_main.pdf':'https://www.bmis-bycatch.org/system/files/zotero_attachments/library_1/MQDAAXEY%20-%20Griffiths%20et%20al.%20-%202019%20-%20Just%20a%20FAD%20Ecosystem%20impacts%20of%20tuna%20purse-seine%20.pdf',
}
def get(pair):
    name,url=pair
    record={'file':name,'url':url,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    try:
        r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=(8,15))
        record.update(status=r.status_code,bytes=len(r.content),content_type=r.headers.get('Content-Type'))
        if r.ok and (r.content.startswith(b'%PDF') or r.content.startswith(b'PK')):
            p=BASE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.content)
            record['sha256']=hashlib.sha256(r.content).hexdigest()
    except Exception as e: record['error']=str(e)
    print(json.dumps(record),flush=True)
    return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e: rows=list(e.map(get,urls.items()))
(BASE/'download_log.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
