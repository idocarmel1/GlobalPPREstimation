from pathlib import Path
import json,hashlib,re,zipfile
ROOT=Path.cwd();HERE=ROOT/'regions/LME_027/validation_reports/BancArguin_20261003'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
replacements={'complete2026':'complete 2026','three1991source-faithful':'three 1991 source-faithful','Existing1987selection':'Existing 1987 selection','in14consumers':'in 14 consumers','source Ecosim1991':'source Ecosim 1991','area33224km':'area 33,224 km','legacy9%':'legacy 9%','removed9%':'removed 9%','source-faithful extraction2026':'source-faithful extraction 2026','assessment2026':'assessment 2026','retained in baseline; current candidate assessment2026':'retained in baseline; current candidate assessment 2026','Base/M30/P30 assessed independently;512catchlabels each':'Base/M30/P30 assessed independently; 512 catch labels each','legacy9%coverage':'legacy 9% coverage','legacy 9%coverage':'legacy 9% coverage'}
def polish(t):
    for a,b in replacements.items():t=t.replace(a,b)
    return t
p=ROOT/'Project.xlsx';tmp=p.with_suffix('.polish.tmp.xlsx')
with zipfile.ZipFile(p) as z,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
    for info in z.infolist():
        data=z.read(info.filename)
        if info.filename in ('xl/worksheets/sheet2.xml','xl/worksheets/sheet3.xml'):data=polish(data.decode('utf-8')).encode('utf-8')
        out.writestr(info,data)
tmp.replace(p)
for name in ('metadata.json','README.md'):
    p=ROOT/'regions/LME_027/papers/CAN-2014'/name;p.write_text(polish(p.read_text(encoding='utf-8')),encoding='utf-8')
p=HERE/'inventory_after.json';p.write_text(polish(p.read_text(encoding='utf-8')),encoding='utf-8')
r=json.loads((HERE/'inventory_reconciliation.json').read_text(encoding='utf-8'));r['after_project_sha256']=sha(ROOT/'Project.xlsx')
for name,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
    p=ROOT/'interactive_map'/name;t=p.read_text(encoding='utf-8');i=t.index('const '+var+'=')+len('const '+var+'=');d,end=json.JSONDecoder().raw_decode(t,i)
    before=json.dumps(d,separators=(',',':'),sort_keys=True)
    if name=='index.html':
        a=next(a for a in d['articles'] if a.get('article_id')=='CAN-2014__LME_027')
        for k,v in a.items():
            if isinstance(v,str):a[k]=polish(v)
        t=t[:i]+json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')+t[end:]
        # Match linked_layout's bounded null-score display fix, without a rebuild.
        t=t.replace('${a.quality_score_100}</div>',"${a.quality_score_100??'Unrated'}</div>").replace('width:${a.quality_score_100}%','width:${a.quality_score_100??0}%')
        for field in ('model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10'):t=t.replace('${a.'+field+'}', '${a.'+field+"??'—'}")
    t=re.sub(r'(<meta name="ppr-project-sha256" content=")[0-9a-f]{64}(">)',lambda m:m.group(1)+sha(ROOT/'Project.xlsx')+m.group(2),t)
    p.write_text(t,encoding='utf-8',newline='\n');r['map_cleanup'][name]['sha256']=sha(p)
(HERE/'inventory_reconciliation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('Polished candidate metadata and unrated-score display; scientific values unchanged.')
