"""Refresh only the assessed CAN-2014 record in secondary active catalog views."""
from pathlib import Path
import csv,html,json,hashlib
csv.field_size_limit(10000000)
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'interactive_map/index.html';t=p.read_text(encoding='utf-8');i=t.index('const DB=')+len('const DB=');d,_=json.JSONDecoder().raw_decode(t,i)
a=next(a for a in d['articles'] if a['article_id']=='CAN-2014__LME_027')
p=ROOT/'interactive_map/data/articles.csv'
with p.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
old=[r for r in rows if r['article_id']=='CAN-2014__LME_027'];assert len(old)==1
(HERE/'baseline/articles_csv_CAN2014_before.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
untouched=[r.copy() for r in rows if r['article_id']!='CAN-2014__LME_027']
for r in rows:
    if r['article_id']!='CAN-2014__LME_027':continue
    for k in headers:
        value=a.get(k);r[k]=json.dumps(value,ensure_ascii=False) if isinstance(value,(dict,list)) else '' if value is None else str(value)
with p.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
with p.open(encoding='utf-8-sig',newline='') as f:assert [r for r in csv.DictReader(f) if r['article_id']!='CAN-2014__LME_027']==untouched
p=ROOT/'interactive_map/archive/index.html';t=p.read_text(encoding='utf-8');original=t;i=t.index('../../regions/LME_027/papers/CAN-2014/');start=t.rfind('<article>',0,i);end=t.index('</article>',i)+len('</article>');old=t[start:end]
assert '10.1371/journal.pone.0094742' in old
(HERE/'baseline/archive_CAN2014_before.html').write_text(old,encoding='utf-8')
e=lambda x:html.escape(str(x or ''),quote=True)
prefix=f'<article><h2>{e(a["title"])}</h2><p>{e(a["authors"])} · {a["publication_year"]}</p><p><b>{e(a["coverage_class"])}</b> — {e(a["coverage_note"])}</p><p>Quality: not rated. {e(a["quality_rationale"])}</p><p>{e(a["full_model_loadable"])}</p>'
tail=old[old.index('<a href="https://doi.org/10.1371/journal.pone.0094742"'):]
new=prefix+tail
t=t[:start]+new+t[end:];p.write_text(t,encoding='utf-8',newline='\n')
assert t[:start]+old+t[start+len(new):]==original
out={'CAN2014_article_record_only':True,'unrelated_csv_rows_unchanged':True,'archive_prefix_suffix_unchanged':True,'articles_csv_sha256':sha(ROOT/'interactive_map/data/articles.csv'),'archive_html_sha256':sha(p)}
(HERE/'qa/secondary_catalog_reconciliation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Secondary archive and CSV candidate records reconciled.')
