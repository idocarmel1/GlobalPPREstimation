"""Exact review-only candidate metadata insertion. Caller holds central lock.

Proposal for tools/project_core/registry/review_candidates.py. No scientific
registration inference: supplied paper identity/year/DOI must match Project.
"""
import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as etree
from tools.project_core.validation.researcher_review import S, column, sha, sheet_xml, table_rows
from tools.project_core.registry.discovery import region_directory, resolve_model

ALLOWED={'unit_id','model_id','model_path','selected','paper_ids','model_year','model_years','publication_year','doi','variant'}

def add_review_candidate(project, root, row, canonical_sha256):
    project=Path(project); root=Path(root).resolve()
    if set(row)-ALLOWED or row.get('selected') is not False:
        raise ValueError('Only unselected review candidate metadata is allowed')
    required=ALLOWED-{'variant'}
    if required-set(row):raise ValueError('Candidate source identity is incomplete')
    canonical=resolve_model(region_directory(root,row['unit_id']),row['model_id']).resolve()
    if not canonical.is_relative_to(root) or canonical.relative_to(root).as_posix()!=row['model_path']:
        raise ValueError('Candidate must use its exact canonical discovered path')
    if sha(canonical)!=canonical_sha256:raise ValueError('Candidate source changed')
    before=sha(project)
    with zipfile.ZipFile(project) as archive:
        sheet,headers,header,rows=table_rows(archive,'Models & coverage','Models')
        if any(r.get('unit_id')==row['unit_id'] and r.get('model_id')==row['model_id'] for _,r in rows):
            raise ValueError('Candidate already registered')
        if set(row)-set(headers):raise ValueError('Candidate columns absent from current schema')
        papers=[p for _,p in table_rows(archive,'Papers','Papers')[3] if p.get('article_id')==row['paper_ids']]
        if len(papers)!=1:raise ValueError('Candidate requires an exact existing paper')
        paper=papers[0]
        for field in ['unit_id','publication_year','doi']:
            if str(paper.get(field))!=str(row[field]):raise ValueError('Candidate paper source mismatch: '+field)
        sheet_path,_=sheet_xml(archive,'Models & coverage')
        parts=[(info,archive.read(info.filename)) for info in archive.infolist()]
    data=sheet.find(f'{{{S}}}sheetData')
    last=max(int(element.get('r')) for element,_ in rows)
    if any(int(element.get('r'))>last and len(element) for element in data):
        raise ValueError('Models must be the final block; refuse shifting other content')
    newrow=next((element for element in data if int(element.get('r'))==last+1),None)
    if newrow is None:newrow=etree.SubElement(data,f'{{{S}}}row',r=str(last+1))
    for index,field in enumerate(headers,1):
        if field not in row:continue
        value=row[field]; cell=etree.SubElement(newrow,f'{{{S}}}c',r=column(index)+str(last+1))
        if isinstance(value,bool):
            cell.set('t','b');etree.SubElement(cell,f'{{{S}}}v').text='1' if value else '0'
        elif isinstance(value,(int,float)):
            etree.SubElement(cell,f'{{{S}}}v').text=str(value)
        else:
            cell.set('t','inlineStr');text=etree.SubElement(etree.SubElement(cell,f'{{{S}}}is'),f'{{{S}}}t')
            text.set('{http://www.w3.org/XML/1998/namespace}space','preserve');text.text=str(value)
    dimension=sheet.find(f'{{{S}}}dimension')
    if dimension is not None:dimension.set('ref',re.sub(r'\d+$',str(last+1),dimension.get('ref')))
    replacements={sheet_path:etree.tostring(sheet,encoding='utf-8')};matched=[]
    for info,content in parts:
        if not info.filename.startswith('xl/tables/') or not info.filename.endswith('.xml'):continue
        table=etree.fromstring(content);columns=table.find(f'{{{S}}}tableColumns')
        if columns is None or [c.get('name') for c in columns]!=headers:continue
        if int(re.search(r'\d+$',table.get('ref'))[0])!=last:raise ValueError('Unexpected Models table extent')
        ref=re.sub(r'\d+$',str(last+1),table.get('ref'));table.set('ref',ref)
        auto=table.find(f'{{{S}}}autoFilter')
        if auto is not None:auto.set('ref',ref)
        replacements[info.filename]=etree.tostring(table,encoding='utf-8');matched.append(info.filename)
    if len(matched)!=1:raise ValueError('Require exactly one Models native Excel table')
    fd,temporary=tempfile.mkstemp(suffix='.xlsx',dir=project.parent);os.close(fd)
    try:
        with zipfile.ZipFile(temporary,'w') as archive:
            for info,content in parts:archive.writestr(info,replacements.get(info.filename,content))
        if sha(project)!=before or sha(canonical)!=canonical_sha256:raise ValueError('Registration source changed')
        os.replace(temporary,project)
    finally:
        Path(temporary).unlink(missing_ok=True)




