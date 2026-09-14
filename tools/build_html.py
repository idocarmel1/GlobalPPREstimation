"""Rebuild the original map, time-series and archive pages from the project workbooks."""
import argparse,copy,csv,html,importlib.util,json,os,re,shutil,tempfile
from pathlib import Path
from workbooks import sha,records
from original_atlas_data import datasets

DISPLAY_FIELDS=['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']
LINK_UPDATES={"../data/unidentified_taxa.json":"data/unidentified_taxa.json"}

def linked_layout(template):
    for old,new in LINK_UPDATES.items():template=template.replace(old,new)
    return template

def atomic_text(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix=path.suffix);os.close(fd)
    try:Path(tmp).write_text(text,encoding='utf-8');os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def build(workbook,output=None):
    root=workbook.parent;directory=(output.parent if output and output.suffix=='.html' else output) or root/'interactive_map'
    catalog,series,project=datasets(workbook);layouts=Path(__file__).with_name('original_html_layout')
    fingerprint=sha(workbook)
    display=copy.deepcopy(catalog)
    for collection in ['regions','articles']:
        for r in display[collection]:
            for k in DISPLAY_FIELDS:
                if isinstance(r.get(k),str):r[k]=html.escape(r[k],quote=True)
            for f in r.get('material_files',[]):
                for k in ['filename','file_label']:
                    if isinstance(f.get(k),str):f[k]=html.escape(f[k],quote=True)
    for name,payload in [('index.html',display),('trends.html',series)]:
        template=linked_layout((layouts/name).read_text())
        value=json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')
        page=template.replace('__PPR_DATA__',value)
        page=page.replace('</head>',f'<meta name="ppr-project-sha256" content="{fingerprint}"></head>',1)
        atomic_text(directory/name,page)
        if name=='index.html' and output and output.suffix=='.html' and output.name!='index.html':atomic_text(output,page)
    spec=importlib.util.spec_from_file_location('original_archive_layout',layouts/'archive_layout.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    atomic_text(directory/'archive/index.html',module.archive_index(catalog))
    # Preserve the original download links, using current metadata where appropriate.
    data=directory/'data';data.mkdir(exist_ok=True)
    atomic_text(data/'unidentified_taxa.json',json.dumps({'description':'Current unidentified-catch metadata embedded in these atlas pages.','units':{u:r.get('unidentified') for u,r in catalog['network']['simple_units'].items()}},ensure_ascii=False,separators=(',',':')))
    old=root/'original_research_archive/legacy/PPRAtlas/data'
    for name in ['eez_searches.csv','lme_searches.csv']:
        if (old/name).exists():shutil.copy2(old/name,data/name)
    for name,rr in [('articles.csv',records(project,'Papers','Papers')),('files.csv',catalog.get('files',[]))]:
        headers=list(dict.fromkeys(k for r in rr for k in r))
        with (data/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rr)
    print(f'Original-format pages rebuilt: {directory}/index.html, trends.html and archive/index.html',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workbook',type=Path,default=Path(__file__).resolve().parents[1]/'Project.xlsx');ap.add_argument('--output',type=Path,help='Output directory, or a map filename with sibling trends.html and archive/index.html');a=ap.parse_args();build(a.workbook.resolve(),a.output.resolve() if a.output else None)
