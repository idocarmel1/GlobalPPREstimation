"""Rebuild the atlas, selected-region archive and machine-readable catalogs."""
from pathlib import Path
from collections import Counter
import csv, hashlib, html, json, re, shutil
from atlas.catalog import build_catalog
from atlas.render import render_map
from atlas.archive import archive_index

ROOT=Path(__file__).resolve().parent

def write_csv(path,rows,excluded=()):
    keys=list(dict.fromkeys(k for r in rows for k in r if k not in excluded))
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader()
        for r in rows:
            writer.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(list,dict)) else r.get(k) for k in keys})

def main():
    db=build_catalog(ROOT)
    for a in db['articles']:
        a['footprint_key']=a['source_article_id']+'_'+hashlib.sha256(json.dumps(a.get('geometry'),sort_keys=True).encode()).hexdigest()[:12]
        directory=ROOT/a['article_dir'];directory.mkdir(parents=True,exist_ok=True)
        local_files=[]
        for original in a['material_files']:
            f=dict(original);source=ROOT/f['relative_path']
            suffix=source.suffix
            stem=re.sub(r'[^A-Za-z0-9._-]+','_',Path(f.get('filename') or f['role']).stem).strip('._')[:42] or f['role']
            filename=f"{stem}-{f['sha256'][:8]}{suffix}"
            destination=directory/filename
            if destination.exists():
                assert hashlib.sha256(destination.read_bytes()).hexdigest()==f['sha256'], 'Existing local article file differs'
            else:shutil.copyfile(source,destination)
            f['canonical_relative_path']=f['relative_path'];f['relative_path']=destination.relative_to(ROOT).as_posix()
            f['local_filename']=filename;local_files.append(f)
        a['material_files']=local_files
    data=ROOT/'data';data.mkdir(exist_ok=True)
    (data/'catalog.json').write_text(json.dumps(db,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    for name,rows,excluded in [('regions',db['regions'],('geometry',)),('articles',db['articles'],('geometry','material_files')),('files',db['files'],('text_preview',)),('eez_searches',[s for s in db['searches'] if s['unit_id'].startswith('EEZ_')],()),('lme_searches',[s for s in db['searches'] if s['unit_id'].startswith('LME_')],()),('download_attempts',db['download_attempts'],())]:
        write_csv(data/f'{name}.csv',rows,excluded)
    source_rows={}
    for a in db['articles']:
        source_rows[a['source_article_id']]={k:a.get(k) for k in ['source_article_id','title','doi','landing_page','zotero_key','zotero_doi','zotero_url','download_attempt_count','download_status','main_file_status','downloaded_file_count','download_failure_reason']}
    write_csv(data/'retrieval_summary.csv',list(source_rows.values()))
    write_csv(data/'unretrieved_main_sources.csv',[r for r in source_rows.values() if r['main_file_status']!='downloaded_verified'])
    write_csv(data/'article_files.csv',[dict(unit_id=a['unit_id'],source_article_id=a['source_article_id'],title=a['title'],role=f['role'],file_label=f.get('file_label'),relative_path=f['relative_path'],sha256=f['sha256'],source_url=f.get('source_url')) for a in db['articles'] for f in a['material_files']])
    # Remove stale generated metadata after a source merge or geometry correction.
    region_root=(ROOT/'archive/regions').resolve()
    assert region_root == ROOT.resolve()/'archive'/'regions'
    active_dirs={region_root/a['unit_id']/a['source_article_id'] for a in db['articles']}
    if region_root.exists():
        for stale in region_root.glob('*/*/*'):
            if stale.is_file() and stale.name in {'README.md','metadata.json','footprint.geojson'} and stale.parent not in active_dirs:
                stale.unlink()
        for empty in region_root.glob('*/*'):
            if empty.is_dir() and not any(empty.iterdir()):
                empty.rmdir()
    for r in db['regions']:
        directory=ROOT/'archive/regions'/r['unit_id'];directory.mkdir(parents=True,exist_ok=True)
        articles=[a for a in db['articles'] if a['unit_id']==r['unit_id']]
        lines=[f"# {r['unit_id']} — {r['region_name']}",'',f"{r['region_type']}. PPR rank ({db['year']}): {r['ppr_rank']}. Search status: {r['search_status']}.",'',r.get('search_notes','Inherited LME/High Seas assessment; see original catalog provenance.'),'']
        for a in articles:
            ad=directory/a['source_article_id'];ad.mkdir(exist_ok=True)
            lines.append(f"- [{a['title']}]({a['source_article_id']}/README.md)")
            details=[f"# {a['title']}",'',f"{a.get('authors','')} ({a.get('publication_year','')})",'',f"Source: {a.get('landing_page','')}",'',f"Coverage: {a['coverage_class']}. {a.get('coverage_note',a.get('recommendation',''))}",'',f"Quality: {a['quality_score_100']}/100. {a.get('quality_rationale','')}",'',f"Full Ecopath model loadable: {a.get('full_model_loadable','Not tested')}",'',f"Geometry: {a.get('geometry_method','')}. {a.get('geometry_note','')}",'','## Source files','']
            for f in a['material_files']:
                details.append(f"- [{f.get('file_label') or f['role']}: {f['filename']}]({Path(f['relative_path']).name}) — {f['status']}; SHA-256 `{f['sha256']}`")
            if not a['material_files']:details.append('No verified local file. See the public source link and retrieval log.')
            (ad/'README.md').write_text('\n'.join(details),encoding='utf-8')
            (ad/'metadata.json').write_text(json.dumps({k:v for k,v in a.items() if k!='geometry'},ensure_ascii=False,indent=2),encoding='utf-8')
            if a.get('geometry'):(ad/'footprint.geojson').write_text(json.dumps({'type':'Feature','properties':{'geometry_method':a['geometry_method'],'geometry_confidence':a['geometry_confidence']},'geometry':a['geometry']}),encoding='utf-8')
            elif (ad/'footprint.geojson').exists():(ad/'footprint.geojson').unlink()
        if not articles:lines.append('No defensible recommended model located in the completed search.')
        (directory/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    # Escape display strings before the inherited template uses innerHTML.
    display=json.loads(json.dumps(db))
    for records in [display['regions'],display['articles']]:
        for record in records:
            for key in ['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']:
                if isinstance(record.get(key),str):record[key]=html.escape(record[key],quote=True)
            for material in record.get('material_files',[]):
                for key in ['filename','file_label']:
                    if isinstance(material.get(key),str):material[key]=html.escape(material[key],quote=True)
    (ROOT/'index.html').write_text(render_map(ROOT,display),encoding='utf-8')
    (ROOT/'archive/index.html').write_text(archive_index(db),encoding='utf-8')
    report={'ecosystems':len(db['regions']),'types':dict(Counter(r['region_type'] for r in db['regions'])),'eez_searches':sum(s['unit_id'].startswith('EEZ_') for s in db['searches']),'lme_searches':sum(s['unit_id'].startswith('LME_') for s in db['searches']),'article_assignments':len(db['articles']),'distinct_sources':len({a['source_article_id'] for a in db['articles']}),'eezs_with_sources':len({a['unit_id'] for a in db['articles'] if a['unit_id'].startswith('EEZ_')}),'verified_unique_files':len({f['sha256'] for f in db['files'] if f['status']=='downloaded_verified'}),'selected_ppr_total':db['selected_total_ppr'],'years':len(db['annual'])}
    (data/'build_summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))

if __name__=='__main__':main()
