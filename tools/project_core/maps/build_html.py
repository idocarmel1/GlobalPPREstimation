from tools.project_core.registry.discovery import project_root, region_directory, discover_regions, discover_models, resolve_model
"""Rebuild the original map, time-series and source pages from the project workbooks."""
import argparse,copy,csv,hashlib,html,importlib.util,io,json,os,re,shutil,tempfile,zipfile
from pathlib import Path
from tools.project_core.workbooks.workbooks import sha,records
from tools.project_core.maps.original_atlas_data import datasets,add_group_efficiencies,add_group_catch
from tools.project_core.maps.provisional_display import provisional_layout
from tools.project_core.validation.researcher_review import reviewed_layout,approved_review,review_display,_register_review,table_rows,unavailable_review_model,calculation_review_book,attach_payload_review
from tools.project_core.maps.map_cumulative_ppr import cumulative_ppr_layout
from tools.project_core.maps.available_results_layout import available_results_layout
from tools.project_core.maps.group_catch_layout import group_catch_layout
from tools.project_core.maps.trend_extras_layout import trend_extras_layout

DISPLAY_FIELDS=['title','authors','region_name','recommendation','coverage_note','quality_rationale','geometry_note','geometry_method','search_notes','loadability_class','download_failure_reason']
LINK_UPDATES={"../data/unidentified_taxa.json":"data/unidentified_taxa.json"}
OSM_BASEMAP="L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:10,opacity:.55,attribution:'© OpenStreetMap · Sea Around Us polygons'}).addTo(map);"

def linked_layout(template):
    template=template.replace('\r\n','\n')
    template=template.replace('Browse article archive','Browse article sources').replace('in the curated article archive','in the curated article inventory')
    # Unrated source assessments carry null scores, which are not zero ratings.
    template=template.replace('${a.quality_score_100}</div>',"${a.quality_score_100??'—'}</div>")
    template=template.replace('width:${a.quality_score_100}%', 'width:${a.quality_score_100??0}%')
    for field in ('model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10'):
        template=template.replace('${a.'+field+'}', '${a.'+field+"??'—'}")
    for old,new in LINK_UPDATES.items():template=template.replace(old,new)
    template=template.replace('<span>Verified files</span>','<span>Local files</span>')
    template=template.replace("files.filter(f=>f.status==='downloaded_verified').map(f=>f.sha256)","files.map(f=>f.sha256||f.relative_path)")
    if OSM_BASEMAP in template:
        source=project_root(Path(__file__))/'common_reference_data/geography/basemaps/ne_50m_land.geojson'
        land=json.dumps(json.loads(source.read_text(encoding='utf-8')),ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')
        # Streets require a real web origin; bundled land remains the file-mode
        # and service-failure fallback. The frozen historical template is untouched.
        basemap=Path(__file__).with_name('map_basemap.js').read_text(encoding='utf-8').replace('__LAND_DATA__',land)
        template=template.replace('zoomControl:true,minZoom:1}',
            "zoomControl:true,minZoom:1,maxZoom:['http:','https:'].includes(location.protocol)?18:10}",1)
        template=template.replace(OSM_BASEMAP,basemap,1)
    current=cumulative_ppr_layout(reviewed_layout(provisional_layout(template)))
    return trend_extras_layout(group_catch_layout(available_results_layout(current)))

def atomic_text(path,text):
    atomic_bytes(path,text.encode('utf-8'))

def atomic_bytes(path,data):
    from tools.project_core.registry.publication import publication_write
    path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,suffix=path.suffix);os.close(fd)
    try:
        Path(tmp).write_bytes(data)
        with publication_write(path,fingerprint=hashlib.sha256(data).hexdigest()):os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def relayout(workbook,directory=None,group_efficiencies=False,group_catch=False):
    """Validate retained data first, then complete registered method coverage."""
    from tools.project_core.registry.writes import central_lock
    from tools.project_core.registry.publication import publication_transaction
    workbook=Path(workbook).resolve()
    with central_lock(workbook.parent):
        _relayout(workbook,directory,group_efficiencies,group_catch,publish=False)
        with publication_transaction(workbook.parent) as publication:
            changed=_prepare_coverage(workbook.parent,publication)
            if changed:
                return _build(workbook,directory,changed)
            return _relayout(workbook,directory,group_efficiencies,group_catch)


def _relayout(workbook,directory=None,group_efficiencies=False,group_catch=False,*,publish=True):
    """Refresh presentation, optionally exposing saved group metadata."""
    directory=directory or workbook.parent/'interactive_map'
    fingerprint=sha(workbook);layouts=Path(__file__).with_name('original_html_layout')
    outputs=[];catch_sources={}
    for name,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
        old=(directory/name).read_text(encoding='utf-8')
        recorded=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',old)
        if not recorded or recorded.group(1)!=fingerprint:
            raise ValueError(name+': embedded data does not match Project.xlsx; run a full build')
        start=old.index('const '+variable+'=')+len('const '+variable+'=')
        payload,end=json.JSONDecoder().raw_decode(old,start)
        value=old[start:end]
        if group_efficiencies or group_catch:
            units=payload['network']['units'] if variable=='DB' else payload['units']
            if group_efficiencies:add_group_efficiencies(workbook.parent,units)
            if group_catch:
                for source,digest in add_group_catch(workbook.parent,units).items():
                    if source in catch_sources and catch_sources[source]!=digest:raise ValueError('Model-catch source changed between pages: '+str(source))
                    catch_sources[source]=digest
            value=json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')
        template=linked_layout((layouts/name).read_text(encoding='utf-8'))
        page=template.replace('__PPR_DATA__',value)
        page=page.replace('</head>',f'<meta name="ppr-project-sha256" content="{fingerprint}"></head>',1)
        outputs.append((directory/name,page))
    if sha(workbook)!=fingerprint:raise ValueError('Project.xlsx changed during layout refresh')
    if any(sha(path)!=digest for path,digest in catch_sources.items()):raise ValueError('Model-catch source changed before layout publication')
    if not publish:return
    for path,page in outputs:atomic_text(path,page)
    additions=('stored group GE/EE added; ' if group_efficiencies else '')+('stored group catch metadata added; ' if group_catch else '')
    print('Map and trends layouts refreshed; '+(additions or 'embedded data preserved; ')+'project fingerprint preserved.',flush=True)

def refresh_reviews(workbook,previous_workbook,unit_ids,directory=None,*,model_ids=None):
    """Publish exact model reviews under the shared writer lock; keep map defaults."""
    from tools.project_core.registry.writes import central_lock
    from tools.project_core.registry.publication import publication_transaction
    with central_lock(workbook.resolve().parent):
        _refresh_reviews(workbook,previous_workbook,unit_ids,directory,model_ids=model_ids,publish=False)
        with publication_transaction(workbook.resolve().parent) as publication:
            changed=_prepare_coverage(workbook.resolve().parent,publication)
            if changed:
                return _build(workbook,directory,changed|set(unit_ids))
            return _refresh_reviews(workbook,previous_workbook,unit_ids,directory,model_ids=model_ids)

def _refresh_reviews(workbook,previous_workbook,unit_ids,directory=None,*,model_ids=None,publish=True):
    """Refresh only registered review metadata after a bounded central registration.

    The pre-registration workbook is required evidence that all other central
    scientific data is identical to the workbook used by the existing pages.
    """
    root=workbook.resolve().parent;directory=directory or root/'interactive_map'
    previous_fingerprint=sha(previous_workbook);fingerprint=sha(workbook)
    # Read only the small Models sheet. Loading every sheet through openpyxl
    # would unnecessarily traverse the complete scientific results archive.
    with zipfile.ZipFile(workbook) as archive:
        newrows={(r['unit_id'],r['model_id']):r for _,r in table_rows(archive,'Models & coverage','Models')[3]}
    reviews={};registrations=[];review_books={}
    for unit_id in unit_ids:
        # The approval gate needs only source identity settings and group IDs;
        # avoid traversing the regional workbook's complete result tables.
        book={}
        with zipfile.ZipFile(region_directory(root,unit_id)/(unit_id+'.xlsx')) as regional:
            for sheet,table in [('Overview','Settings'),('Selected model groups','Groups')]:
                _,headers,_,rows=table_rows(regional,sheet,table)
                # A trailing @table marker can reset the scanner's current
                # header after it has already captured the requested rows.
                headers=list(rows[0][1]) if rows else (headers or [])
                book.setdefault(sheet,{})[table]=(headers,[[r.get(h) for h in headers] for _,r in rows])
        from tools.project_core.workbooks.workbooks import overview
        model_id=(model_ids or {}).get(unit_id) or overview(book).get('selected_model_id');key=(unit_id,model_id)
        if key not in newrows:raise ValueError('Review refresh cannot add a model')
        review=approved_review(root,newrows[key],book)
        if not review:raise ValueError('Review refresh requires a registered researcher decision: '+unit_id)
        reviews[key]=review
        review_books[key]=book
        if review.get('review_scope') != 'model_source':book=calculation_review_book(root,newrows[key],book)
        groups=records(book,'Selected model groups','Groups')
        excluded=review['excluded_group_ids']
        seq=[int(float(r['seq'])) for r in groups if r['group_name'] in excluded]
        if len(seq)!=len(excluded):raise ValueError('Approved exclusions do not resolve uniquely')
        registrations.append((root/newrows[key]['validation_report_path'],unit_id,model_id,seq))
    # Replay the exact bounded registration against the prior workbook, then
    # compare every decompressed ZIP part. This validates native green styles
    # and table definitions as well as review fields, while requiring every
    # unrelated sheet, formula, value, drawing and document property to remain
    # byte-identical. The temporary copy sits beside Project so source paths
    # resolve identically; the real workbook is never modified here.
    fd,expected=tempfile.mkstemp(prefix='.review-refresh-',suffix='.xlsx',dir=root);os.close(fd)
    try:
        shutil.copyfile(previous_workbook,expected)
        for report,unit_id,model_id,seq in registrations:
            # Replay writes only this isolated temporary copy; the outer lock
            # already serializes the real Project and HTML publication.
            _register_review(Path(expected),report,unit_id,model_id,seq)
        with zipfile.ZipFile(expected) as reference,zipfile.ZipFile(workbook) as current:
            if reference.namelist()!=current.namelist() or any(reference.read(name)!=current.read(name) for name in reference.namelist()):
                raise ValueError('Central data changed beyond the targeted researcher review metadata; run a full build')
    finally:
        if os.path.exists(expected):os.unlink(expected)
    outputs=[];layouts=Path(__file__).with_name('original_html_layout')
    for name,variable in [('index.html','DB'),('trends.html','SERIES_DB')]:
        old=(directory/name).read_text(encoding='utf-8')
        recorded=re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',old)
        if not recorded or recorded.group(1)!=previous_fingerprint:
            raise ValueError(name+': embedded data does not match the pre-registration Project workbook')
        start=old.index('const '+variable+'=')+len('const '+variable+'=')
        payload,_=json.JSONDecoder().raw_decode(old,start);original=copy.deepcopy(payload)
        units=payload['network']['units'] if variable=='DB' else payload['units']
        original_units=original['network']['units'] if variable=='DB' else original['units']
        for (unit_id,model_id),review in reviews.items():
            models=[m for m in units[unit_id]['models'] if m['id']==model_id]
            originals=[m for m in original_units[unit_id]['models'] if m['id']==model_id]
            if not models:
                candidate=unavailable_review_model(newrows[(unit_id,model_id)],review)
                units[unit_id]['models'].append(candidate)
                original_units[unit_id]['models'].append(copy.deepcopy(candidate))
                models=[candidate];originals=[original_units[unit_id]['models'][-1]]
            if len(models)!=1:raise ValueError('Embedded model identity is ambiguous: '+unit_id)
            attach_payload_review(root,newrows[(unit_id,model_id)],review_books[(unit_id,model_id)],models[0],review)
            for field in ['researcher_review','display_ppr_excluded_group_ids','recorded_review_pending']:
                originals[0].pop(field,None)
                if field in models[0]:originals[0][field]=copy.deepcopy(models[0][field])
        if payload!=original:raise ValueError('Review refresh changed unrelated embedded data')
        value=json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('</',r'<\/')
        page=linked_layout((layouts/name).read_text(encoding='utf-8')).replace('__PPR_DATA__',value)
        page=page.replace('</head>',f'<meta name="ppr-project-sha256" content="{fingerprint}"></head>',1)
        outputs.append((directory/name,page))
    if sha(workbook)!=fingerprint or sha(previous_workbook)!=previous_fingerprint:
        raise ValueError('A Project workbook changed during review refresh')
    if not publish:return
    for path,page in outputs:atomic_text(path,page)
    print('Map and trends researcher metadata refreshed; all other embedded data preserved.',flush=True)

def _prepare_coverage(root,publication):
    """Extend authorized model methods before any central/page inputs are read."""
    from tools.project_core.calculations.coverage import ensure_validated_coverage
    from tools.project_core.registry.update_project import _update
    coverage=ensure_validated_coverage(root,lock_held=True)
    publication.checkpoint(coverage.get('written_paths',coverage.get('written_region_paths',[])),fingerprints=coverage.get('written_hashes'))
    changed=set(coverage['changed_units'])
    if changed:
        _update(root,[region_directory(root,unit)/(unit+'.xlsx') for unit in sorted(changed)],False)
        publication.checkpoint([root/'Project.xlsx'])
    return changed


def build(workbook,output=None,only_units=None,*,lock_held=False):
    from tools.project_core.registry.writes import central_lock
    workbook=Path(workbook).resolve()
    if not lock_held:
        with central_lock(workbook.parent):return build(workbook,output,only_units,lock_held=True)
    from tools.project_core.registry.publication import publication_transaction
    with publication_transaction(workbook.parent) as publication:
        changed=_prepare_coverage(workbook.parent,publication)
        if only_units:only_units=set(only_units)|changed
        return _build(workbook,output,only_units)


def ensure_map_publication(root):
    """A launcher may reuse its server only after coverage and pages are current."""
    from tools.project_core.registry.writes import central_lock
    from tools.project_core.registry.publication import publication_transaction
    root=Path(root).resolve();workbook=root/'Project.xlsx';directory=root/'interactive_map'
    with central_lock(root),publication_transaction(root) as publication:
        changed=_prepare_coverage(root,publication)
        fingerprint=sha(workbook)
        pages=[directory/name for name in ['index.html','trends.html']]
        current=all(page.is_file() and f'<meta name="ppr-project-sha256" content="{fingerprint}">' in page.read_text(encoding='utf-8') for page in pages)
        if current and publication.models:
            changed.update(_stale_reviewed_payload_units(root,directory,publication.models))
        if changed or not current or not (directory/'sources.html').is_file():
            _build(workbook,None,changed if changed and all(page.is_file() for page in pages) else None)


def _stale_reviewed_payload_units(root,directory,metadata):
    """Saved calculations and signed sources can change without changing Project."""
    from tools.project_core.maps.original_atlas_data import embedded
    catalog,_=embedded(directory/'index.html','DB');series,_=embedded(directory/'trends.html','SERIES_DB')
    collections=[catalog['network']['units'],series['units']];changed=set();books={}
    for row in metadata:
        unit=row['unit_id'];model=row['model_id'];regional=region_directory(root,unit)/(unit+'.xlsx')
        if unit not in books:
            with zipfile.ZipFile(regional) as archive:
                books[unit]={}
                for sheet,table in [('Overview','Settings'),('Selected model groups','Groups')]:
                    _,header,_,rows=table_rows(archive,sheet,table)
                    header=list(rows[0][1]) if rows else (header or [])
                    books[unit].setdefault(sheet,{})[table]=(header,[[record.get(key) for key in header] for _,record in rows])
        current=dict(books[unit]['Overview']['Settings'][1])
        path=regional if current.get('selected_model_id')==model and current.get('results_model_id')==model else (root/row['model_path']).parent/'results/regional_snapshot.xlsx'
        fingerprint=sha(path) if path.is_file() else None
        current_review,current_pending=review_display(root,row,books[unit])
        for collection in collections:
            saved=next((item for item in collection.get(unit,{}).get('models',[]) if item['id']==model),None)
            if saved is None or fingerprint is None or saved.get('workbook_sha256')!=fingerprint:
                changed.add(unit)
                continue
            # Recheck the signed model decision independently of calculation
            # packages. This also repairs pages cached under the old PPR gate.
            if (saved.get('researcher_review')!=current_review or
                    saved.get('recorded_review_pending')!=current_pending):
                changed.add(unit)
    return changed


def _build(workbook,output=None,only_units=None):
    root=workbook.parent;directory=(output.parent if output and output.suffix=='.html' else output) or root/'interactive_map'
    fingerprint=sha(workbook)
    catalog,series,project=datasets(workbook,only_units=only_units) if only_units else datasets(workbook)
    layouts=Path(__file__).with_name('original_html_layout')
    if sha(workbook)!=fingerprint:raise ValueError('Project.xlsx changed during map data construction; reload current inputs')
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
    atomic_text(directory/'sources.html',module.archive_index(catalog).replace('Quality: None/100.', 'Quality: not rated.'))
    # Preserve the original download links, using current metadata where appropriate.
    data=directory/'data';data.mkdir(exist_ok=True)
    atomic_text(data/'unidentified_taxa.json',json.dumps({'description':'Current unidentified-catch metadata embedded in these atlas pages.','units':{u:r.get('unidentified') for u,r in catalog['network']['simple_units'].items()}},ensure_ascii=False,separators=(',',':')))
    context=root/'common_reference_data/atlas_source_context'
    for name in ['eez_searches.csv','lme_searches.csv']:
        atomic_bytes(data/name,(context/name).read_bytes())
    for name,rr in [('articles.csv',catalog['articles']),('files.csv',catalog.get('files',[]))]:
        headers=list(dict.fromkeys(k for r in rr for k in r))
        output=io.StringIO(newline='')
        w=csv.DictWriter(output,fieldnames=headers,lineterminator='\n');w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rr)
        atomic_text(data/name,output.getvalue())
    print(f'Original-format pages rebuilt: {directory}/index.html, trends.html and sources.html',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workbook',type=Path,default=project_root(Path(__file__))/'Project.xlsx');ap.add_argument('--output',type=Path,help='Output directory, or a map filename with sibling trends.html and sources.html');ap.add_argument('--layout-only',action='store_true',help='Refresh map/trends presentation only, retaining data that matches the project fingerprint');ap.add_argument('--group-efficiencies',action='store_true',help='Also expose stored GE/EE during a layout-only refresh');ap.add_argument('--group-catch',action='store_true',help='Also expose saved native group catch and documented unit conversion during a layout-only refresh');ap.add_argument('--region',nargs='+',help='Refresh only these regional details; retain other displays only when registered selection, workbook hash, annual values and NPP still match');a=ap.parse_args()
    if a.layout_only:
        directory=(a.output.parent if a.output and a.output.suffix=='.html' else a.output)
        relayout(a.workbook.resolve(),directory.resolve() if directory else None,a.group_efficiencies,a.group_catch)
    else:build(a.workbook.resolve(),a.output.resolve() if a.output else None,set(a.region) if a.region else None)
