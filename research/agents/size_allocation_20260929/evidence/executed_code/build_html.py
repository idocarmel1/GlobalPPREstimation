"""Rebuild the original map, time-series and archive pages from the project workbooks."""
import argparse,copy,csv,html,importlib.util,json,os,re,shutil,tempfile
from pathlib import Path
from workbooks import sha,records
from original_atlas_data import datasets
from provisional_display import provisional_layout

DISPLAY_FIELDS=['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']
LINK_UPDATES={"../data/unidentified_taxa.json":"data/unidentified_taxa.json"}
OSM_BASEMAP="L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:10,opacity:.55,attribution:'© OpenStreetMap · Sea Around Us polygons'}).addTo(map);"

def linked_layout(template):
    for old,new in LINK_UPDATES.items():template=template.replace(old,new)
    template=template.replace('<span>Verified files</span>','<span>Local files</span>')
    template=template.replace("files.filter(f=>f.status==='downloaded_verified').map(f=>f.sha256)","files.map(f=>f.sha256||f.relative_path)")
    if OSM_BASEMAP in template:
        source=Path(__file__).resolve().parents[1]/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
        land=json.dumps(json.loads(source.read_text(encoding='utf-8')),ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')
        # Streets require a real web origin; bundled land remains the file-mode
        # and service-failure fallback. The frozen historical template is untouched.
        basemap=Path(__file__).with_name('map_basemap.js').read_text(encoding='utf-8').replace('__LAND_DATA__',land)
        template=template.replace('zoomControl:true,minZoom:1}',
            "zoomControl:true,minZoom:1,maxZoom:['http:','https:'].includes(location.protocol)?18:10}",1)
        template=template.replace(OSM_BASEMAP,basemap,1)
    return provisional_layout(template)

def atomic_text(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix=path.suffix);os.close(fd)
    try:Path(tmp).write_text(text,encoding='utf-8',newline='\n');os.replace(tmp,path)
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
        template=linked_layout((layouts/name).read_text(encoding='utf-8'))
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
    context=root/'common_reference_data/atlas_source_context'
    for name in ['eez_searches.csv','lme_searches.csv']:
        shutil.copy2(context/name,data/name)
    for name,rr in [('articles.csv',catalog['articles']),('files.csv',catalog.get('files',[]))]:
        headers=list(dict.fromkeys(k for r in rr for k in r))
        with (data/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=headers,lineterminator='\n');w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rr)
    print(f'Original-format pages rebuilt: {directory}/index.html, trends.html and archive/index.html',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workbook',type=Path,default=Path(__file__).resolve().parents[1]/'Project.xlsx');ap.add_argument('--output',type=Path,help='Output directory, or a map filename with sibling trends.html and archive/index.html');a=ap.parse_args();build(a.workbook.resolve(),a.output.resolve() if a.output else None)
