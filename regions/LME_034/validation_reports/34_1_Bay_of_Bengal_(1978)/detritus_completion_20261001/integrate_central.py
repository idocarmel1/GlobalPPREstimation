"""Integrate LME034 only, preserving other records and their original numeric XML."""
import copy, json, os, shutil, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
sys.path.insert(0,str(ROOT/'tools'))
import update_project
from workbooks import read_book,write_book,records,sha

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
UNIT='LME_034'

def blocks(xml):
    tree=ET.fromstring(xml);data=tree.find('m:sheetData',NS)
    result={};name=None;header=None;rr=[]
    def vals(row):
        out={}
        for c in row:
            col=c.attrib['r'].rstrip('0123456789')
            out[col]=''.join(c.itertext())
        return out
    for row in data:
        v=vals(row)
        if v.get('A')=='@table':
            if name is not None:result[name]=(header,rr)
            name=v['B'];header=None;rr=[]
        elif name is not None and v:
            if header is None:header=v
            else:rr.append(row)
    if name is not None:result[name]=(header,rr)
    return tree,data,result,vals

def preserve_xml(original,current,expected,before):
    replacements={}
    with zipfile.ZipFile(original) as old,zipfile.ZipFile(current) as new:
        old_styles=ET.fromstring(old.read('xl/styles.xml'));new_styles=ET.fromstring(new.read('xl/styles.xml'))
        ox=old_styles.find('m:cellXfs',NS);nx=new_styles.find('m:cellXfs',NS)
        assert len(nx)==4 and all(ET.tostring(ox[i])==ET.tostring(nx[i]) for i in range(3))
        # The prior central release has researcher-added green fonts and styles.
        # Preserve those definitions and all original record styles exactly.
        replacements['xl/styles.xml']=old.read('xl/styles.xml')
        for i,sheet in enumerate(expected,1):
            path=f'xl/worksheets/sheet{i}.xml'
            a,ad,ab,vals=blocks(old.read(path));b,bd,bb,_=blocks(new.read(path))
            assert set(ab)==set(bb)
            if expected[sheet]==before[sheet]:
                replacements[path]=old.read(path);continue
            rr={int(row.attrib['r']):row for row in bd}
            # Preserve table headers and all existing layout metadata.
            old_marks={int(row.attrib['r']) for row in ad if vals(row).get('A')=='@table'}
            new_marks={int(row.attrib['r']) for row in bd if vals(row).get('A')=='@table'}
            old_headers=[row for row in ad if int(row.attrib['r']) in old_marks or int(row.attrib['r'])-1 in old_marks]
            new_headers=[row for row in bd if int(row.attrib['r']) in new_marks or int(row.attrib['r'])-1 in new_marks]
            assert len(old_headers)==len(new_headers)
            for source,target in zip(old_headers,new_headers):
                row=copy.deepcopy(source);number=target.attrib['r'];row.attrib['r']=number
                for cell in row:cell.attrib['r']=cell.attrib['r'].rstrip('0123456789')+number
                rr[int(number)]=row
            for table,(header,new_rows) in bb.items():
                old_header,old_rows=ab[table]
                assert header==old_header
                unitcol=next((col for col,value in header.items() if value=='unit_id'),None)
                if unitcol:
                    old_keep=[row for row in old_rows if vals(row).get(unitcol)!=UNIT]
                    new_keep=[row for row in new_rows if vals(row).get(unitcol)!=UNIT]
                elif expected[sheet][table]==before[sheet][table]:
                    old_keep=old_rows;new_keep=new_rows
                else:continue
                assert len(old_keep)==len(new_keep),(sheet,table)
                for source,target in zip(old_keep,new_keep):
                    # String identities must match in the same preserved record order.
                    def strings(row):return {c.attrib['r'].rstrip('0123456789'):''.join(c.itertext()) for c in row if c.attrib.get('t')=='inlineStr'}
                    assert strings(source)==strings(target),(sheet,table,strings(source),strings(target))
                    source=copy.deepcopy(source);number=target.attrib['r'];source.attrib['r']=number
                    for cell in source:cell.attrib['r']=cell.attrib['r'].rstrip('0123456789')+number
                    rr[int(number)]=source
            bd[:]=[rr[n] for n in sorted(rr)]
            for child in list(b):
                label=child.tag.rsplit('}',1)[-1]
                if label not in ['sheetData','dimension','tableParts']:
                    original_child=a.find(child.tag)
                    if original_child is not None:
                        position=list(b).index(child);b.remove(child);b.insert(position,copy.deepcopy(original_child))
            replacements[path]=ET.tostring(b,encoding='utf-8')
        fd,tmp=tempfile.mkstemp(suffix='.xlsx',dir=current.parent);os.close(fd)
        try:
            with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as result:
                for info in new.infolist():result.writestr(info,replacements.get(info.filename,new.read(info.filename)))
            new.close();old.close();os.replace(tmp,current)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)

def unrelated(book):
    result={}
    for sheet,tables in book.items():
        for name,(header,rr) in tables.items():
            if sheet=='Definitions & build' and name=='Last build':continue
            if 'unit_id' in header:
                ui=header.index('unit_id');rows=[r for r in rr if r[ui]!=UNIT]
            else:rows=rr
            result[sheet,name]=(header,rows)
    return result

def main():
    path=ROOT/'Project.xlsx'
    expected_sha='665e870a4f34c6859eeda65efb3ca59c0c4076440c21aa8eddef503402fe98fc'
    assert sha(path)==expected_sha,'Project changed since coordinated handoff; stop and rebase'
    baseline=OUT/'baseline/Project.xlsx';shutil.copy2(path,baseline)
    protected={p.relative_to(ROOT).as_posix():sha(p) for unit in ['LME_032','LME_036'] for p in (ROOT/'regions'/unit).rglob('*') if p.is_file() and p.suffix.lower()=='.xlsx'}
    before=read_book(path)
    original_read=update_project.read_book
    update_project.read_book=lambda p:copy.deepcopy(before) if Path(p)==path else original_read(p)
    captured={}
    update_project.write_book=lambda p,b:captured.update({'book':b})
    update_project.update(ROOT,[ROOT/'regions/LME_034/LME_034.xlsx'])
    book=captured['book'];patch=json.loads((OUT/'central_metadata_patch.json').read_text(encoding='utf-8'))
    for change in patch['central_changes']:
        h,rr=book[change['sheet']][change['table']]
        matches=[r for r in rr if r[h.index(change['key_field'])]==change['key']]
        assert len(matches)==1
        for field,value in change['values'].items():
            assert field in h,field
            matches[0][h.index(field)]=value
    assert unrelated(book)==unrelated(before),'Unrelated records changed in integration'
    assert sha(path)==expected_sha
    write_book(path,book)
    preserve_xml(baseline,path,book,before)
    saved=read_book(path)
    assert unrelated(saved)==unrelated(before),'Unrelated records changed after serialization'
    for p,h in protected.items():assert sha(ROOT/p)==h,p
    result={'project_sha256':sha(path),'prior_project_sha256':expected_sha,'regional_workbook_sha256':sha(ROOT/'regions/LME_034/LME_034.xlsx'),
        'all_other_regional_records_exactly_unchanged':True,'protected_files_unchanged':protected,
        'LME032_LME036_researcher_review_metadata_unchanged':True,'changed_units':[UNIT],
        'user_document_policy':'No DOCX or notebook writer is invoked; concurrent researcher edits are allowed and never restored or blocked',
        'metadata_patch':'central_metadata_patch.json','central_build_status':'workbook integrated; HTML build and verification pending'}
    (OUT/'central_integration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['project_sha256','all_other_regional_records_exactly_unchanged','changed_units']}),flush=True)

def finish_saved():
    path=ROOT/'Project.xlsx';baseline=OUT/'baseline/Project.xlsx'
    before=read_book(baseline);book=read_book(path)
    protected={p.relative_to(ROOT).as_posix():sha(p) for unit in ['LME_032','LME_036'] for p in (ROOT/'regions'/unit).rglob('*') if p.is_file() and p.suffix.lower()=='.xlsx'}
    preserve_xml(baseline,path,book,before)
    saved=read_book(path);assert unrelated(saved)==unrelated(before),'Unrelated records changed after serialization'
    for p,h in protected.items():assert sha(ROOT/p)==h,p
    result={'project_sha256':sha(path),'prior_project_sha256':sha(baseline),'regional_workbook_sha256':sha(ROOT/'regions/LME_034/LME_034.xlsx'),
        'all_other_regional_records_exactly_unchanged':True,'original_central_review_styles_and_headers_preserved':True,
        'protected_files_unchanged':protected,'LME032_LME036_researcher_review_metadata_unchanged':True,'changed_units':[UNIT],
        'metadata_patch':'central_metadata_patch.json','central_build_status':'workbook integrated; HTML build and verification pending',
        'user_document_policy':'No DOCX or notebook writer is invoked; concurrent researcher edits are allowed and never restored or blocked'}
    (OUT/'central_integration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['project_sha256','all_other_regional_records_exactly_unchanged','changed_units']}),flush=True)

if __name__=='__main__':
    if '--finish-saved' in sys.argv:finish_saved()
    else:main()
