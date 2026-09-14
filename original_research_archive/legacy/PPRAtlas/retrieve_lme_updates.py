"""Retrieve expanded LME source routes, preserving every real outcome."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from download_sources import retrieve
ROOT=Path(__file__).resolve().parent

def run(entries):
    todo=[]
    for aid,a in entries.items():
        path=ROOT/'research/downloads'/f'{aid}.json'
        old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'files':[],'attempts':[]}
        tried={x['url'] for x in old['attempts']}
        urls=[x for x in a.get('download_urls',[]) if x['url'] not in tried]
        if urls:todo.append(dict(a,download_urls=urls))
    print('Sources with untried routes:',len(todo),flush=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures=[pool.submit(retrieve,a) for a in todo]
        for future in as_completed(futures):
            result=future.result()
            path=ROOT/'research/downloads'/f"{result['article_id']}.json"
            old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'files':[],'attempts':[]}
            old['article_id']=result['article_id'];old['files']+=result['files'];old['attempts']+=result['attempts']
            path.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
            print(result['article_id'],len(result['files']),'new files',len(result['attempts']),'new attempts',flush=True)

if __name__=='__main__':
    entries={}
    for path in sorted((ROOT/'research').glob('lme_*.json')):
        result=json.loads(path.read_text(encoding='utf-8'))
        rows=result.get('existing_source_updates',[])+(result['articles'] if path.stem=='lme_root' else [])
        for row in rows:
            a=entries.setdefault(row['article_id'],{'article_id':row['article_id'],'download_urls':[]})
            a['download_urls']+=row.get('download_urls',[])
    run(entries)
