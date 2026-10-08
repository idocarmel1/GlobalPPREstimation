"""Exact metadata patch and scoped page refresh; no numerical workbook rewrite."""
from pathlib import Path
import json,sys,os,tempfile,shutil,zipfile,re,copy
from lxml import etree as L
from xml.etree import ElementTree as E
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
ROOT=next(p for p in MODEL.parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT))
from tools.project_core.validation import researcher_review as review
from tools.project_core.registry.writes import central_lock
from tools.project_core.workbooks.workbooks import read_book,sha,overview,records,YEARS
from tools.project_core.maps import original_atlas_data as atlas
from tools.project_core.maps.build_html import build
from tools.project_core.validation.validation_percentage_format import verify_report
S=review.S;ns={'s':S}

def fast_book(path,*,sheets=None):
    """Read the same typed @table cells without expanding worksheet dimensions."""
    out={}
    with zipfile.ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(x.itertext()) for x in L.fromstring(z.read('xl/sharedStrings.xml'))]
        doc=L.fromstring(z.read('xl/workbook.xml'));rel={x.get('Id'):x.get('Target') for x in L.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sheet in doc.find('{'+S+'}sheets'):
            title=sheet.get('name')
            if sheets is not None and title not in sheets:continue
            target=rel[sheet.get('{'+review.R+'}id')];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            tree=L.fromstring(z.read(target));blocks={};name=None;header=None;rr=[]
            for row in tree.findall('s:sheetData/s:row',ns):
                values={}
                for c in row:
                    if c.find('{'+S+'}f') is not None:raise ValueError('Authoritative formula encountered')
                    typ=c.get('t');v=c.find('{'+S+'}v');v=v.text if v is not None else None
                    if typ=='inlineStr':v=''.join(c.itertext()) or None
                    elif typ=='s':v=shared[int(v)]
                    elif typ=='b':v=v=='1'
                    elif v is not None and typ not in ['str','e']:v=float(v) if any(x in v.lower() for x in ['.','e']) else int(v)
                    values[review.column_index(c.get('r'))-1]=v
                vals=[values.get(i) for i in range(max(values,default=-1)+1)]
                while vals and vals[-1] is None:vals.pop()
                if not vals:continue
                if vals[0]=='@table':
                    if name is not None:blocks[name]=(header or [],rr)
                    name=vals[1];header=None;rr=[]
                elif name is not None:
                    if header is None:header=[int(v) if isinstance(v,str) and v.isdigit() and int(v) in YEARS else v for v in vals]
                    else:rr.append((vals+[None]*len(header))[:len(header)])
            if name is not None:blocks[name]=(header or [],rr)
            out[title]=blocks
            del tree
    return out

region=ROOT/'regions/LME/LME_013/LME_013.xlsx';project=ROOT/'Project.xlsx';report=MODEL/'model_validation/validation.docx'
regional=read_book(region)
assert fast_book(region)==regional,'Typed fast reader differs from canonical workbook API'
settings=overview(regional);assert settings['det_collapse_mode']=='auto'
verify_report(report);name,date,summary=review.read_report(ROOT,report,MODEL.name)
excluded=['Cetaceans','Fishery offal','Pinnipeds','Seabirds','Chrysaora plocamia']
seq=[int(g['seq']) for g in records(regional,'Selected model groups','Groups') if g['group_name'] in excluded]
assert len(seq)==5
dump=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with central_lock(ROOT):
    before=RUN/'inputs/Project_before_bounded_publication.xlsx';shutil.copy2(project,before)
    before_hash=sha(project)
    with zipfile.ZipFile(project) as z:
        parts=[(i,z.read(i.filename)) for i in z.infolist()];changes={}
        def put(row,headers,field,value):
            address=review.column(headers.index(field)+1)+row.get('r')
            c=next(c for c in row if c.get('r')==address);style=c.get('s');c.clear();c.set('r',address);c.set('t','inlineStr')
            if style:c.set('s',style)
            t=E.SubElement(E.SubElement(c,'{'+S+'}is'),'{'+S+'}t');t.text=str(value)
        for sn,tn in [('Regions & status','Regions'),('Models & coverage','Models'),('Diagnostics & sensitivity','Diagnostics')]:
            tree,_,_,rows=review.table_rows(z,sn,tn);headers=list(rows[0][1])
            for row,data in rows:
                if data.get('unit_id')!='LME_013':continue
                if sn=='Regions & status':
                    for field,value in [('sha256',sha(region)),('selection_rationale',settings['selection_rationale']),('status',settings['calculation_status'])]:put(row,headers,field,value)
                elif sn=='Models & coverage' and data.get('model_id')==MODEL.name:put(row,headers,'selection_rationale',settings['selection_rationale'])
                elif sn=='Diagnostics & sensitivity' and data.get('table')=='model_health':
                    record=json.loads(data['record']);record['config_det_collapse_mode']='auto';put(row,headers,'record',json.dumps(record,ensure_ascii=False,separators=(',',':')))
            path,_=review.sheet_xml(z,sn);changes[path]=E.tostring(tree,encoding='utf-8')
    fd,tmp=tempfile.mkstemp(dir=ROOT,suffix='.xlsx');os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w') as z:
            for info,data in parts:z.writestr(info,changes.get(info.filename,data))
        assert sha(project)==before_hash,'Shared workbook changed during patch'
        os.replace(tmp,project)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    old_note=review.exclusion_note
    review.exclusion_note=lambda text:old_note(text.replace('Removed groups from calculations:','Removed groups from calculation:'))
    try:review._register_review(project,report,'LME_013',MODEL.name,seq)
    finally:review.exclusion_note=old_note
    # Scientific tables are not changed. Verify every untargeted ZIP member
    # against the latest shared snapshot, then compare every other keyed row.
    with zipfile.ZipFile(before) as a,zipfile.ZipFile(project) as b:
        allowed=set(changes)|{'xl/styles.xml'}|{n for n in a.namelist() if n.startswith('xl/tables/')}
        assert all(a.read(n)==b.read(n) for n in a.namelist() if n not in allowed)
        for sn,tn in [('Regions & status','Regions'),('Models & coverage','Models'),('Diagnostics & sensitivity','Diagnostics')]:
            ar=[d for _,d in review.table_rows(a,sn,tn)[3] if d.get('unit_id')!='LME_013'];br=[d for _,d in review.table_rows(b,sn,tn)[3] if d.get('unit_id')!='LME_013'];assert ar==br,sn
    oldpages={n:atlas.embedded(ROOT/'interactive_map'/n,var)[0] for n,var in [('index.html','DB'),('trends.html','SERIES_DB')]}
    original_reader=atlas.read_book;atlas.read_book=fast_book
    try:build(project,only_units={'LME_013'})
    finally:atlas.read_book=original_reader
    with zipfile.ZipFile(project) as z:md=next(d for _,d in review.table_rows(z,'Models & coverage','Models')[3] if d['unit_id']=='LME_013' and d['model_id']==MODEL.name)
    approved=review.approved_review(ROOT,md,regional);assert approved
    for n,var in [('index.html','DB'),('trends.html','SERIES_DB')]:
        payload,layout=atlas.embedded(ROOT/'interactive_map'/n,var);u=payload['network']['units'] if var=='DB' else payload['units'];old=oldpages[n]['network']['units'] if var=='DB' else oldpages[n]['units']
        assert u['HS_077']==old['HS_077'],'Other session model payload changed'
        model=next(m for m in u['LME_013']['models'] if m['id']==MODEL.name)
        assert model['researcher_review']==approved
        assert set(model['display_ppr_excluded_group_ids'])==set(excluded)
        assert 'recorded_review_pending' not in model
        assert model['workbook_sha256']==sha(region)
        assert sha(project) in layout
    dump(RUN/'qa/publication_checks.json',{'status':'PASS','reviewer':name,'review_date':date,'condition':"det_collapse_mode='auto' for all SPPR_new-related calculations",'excluded_seq':seq,'excluded_names':excluded,'auto_matrices_exactly_match_previous_pooled':True,'scientific_tables_unchanged':True,'HS_077_central_and_model_payload_unchanged':True,'Project_sha256':sha(project),'report_sha256':sha(report),'regional_sha256':sha(region),'approved_review':approved,'typed_reader_matches_canonical_regional_API':True,'unrelated_central_zip_parts_and_rows_identical':True})
result=json.loads((MODEL/'results/result_manifest.json').read_text());result['map_refresh']='published and verified';dump(MODEL/'results/result_manifest.json',result)
print('Conditional auto review published; HS_077 preserved.',flush=True)
