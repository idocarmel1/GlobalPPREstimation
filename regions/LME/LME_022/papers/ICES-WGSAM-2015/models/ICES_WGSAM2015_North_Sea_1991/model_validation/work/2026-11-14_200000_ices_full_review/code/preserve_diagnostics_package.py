"""Graft two Artifact-authored sheets while preserving unrelated package parts.
New strings become inline strings; new styles are appended with remapped IDs.
Original style/string indexes used by the diagnostic sheet are never changed.
"""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,copy,json,hashlib,os
ROOT=Path.cwd();M=ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
V=M/'model_validation';W=V/'work/2026-11-14_200000_ices_full_review'
before=W/'inputs/taxon_mapping_before.xlsx';authored=W/'outputs/edited_mapping_artifact.xlsx'
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('',NS);ET.register_namespace('r',REL)
q=lambda s:'{'+NS+'}'+s
old=zipfile.ZipFile(before);new=zipfile.ZipFile(authored)
oldstyle=ET.fromstring(old.read('xl/styles.xml'));newstyle=ET.fromstring(new.read('xl/styles.xml'))
def element(root,tag):
    found=root.find(q(tag))
    if found is None:
        found=ET.Element(q(tag),{'count':'0'});root.append(found)
    return found
maps={}
for tag in ['fonts','fills','borders']:
    target=element(oldstyle,tag);source=element(newstyle,tag);offset=len(target)
    maps[tag]={i:offset+i for i in range(len(source))}
    target.extend(copy.deepcopy(list(source)));target.set('count',str(len(target)))
target=element(oldstyle,'numFmts');source=element(newstyle,'numFmts')
numbycode={n.get('formatCode'):int(n.get('numFmtId')) for n in target}
nextnum=max([163]+[int(n.get('numFmtId')) for n in target])+1;num_map={}
for n in source:
    code=n.get('formatCode');nid=int(n.get('numFmtId'))
    if code in numbycode:num_map[nid]=numbycode[code]
    else:
        item=copy.deepcopy(n);item.set('numFmtId',str(nextnum));target.append(item)
        num_map[nid]=nextnum;numbycode[code]=nextnum;nextnum+=1
target.set('count',str(len(target)))
def remap_xf(item,stylemap=None):
    x=copy.deepcopy(item)
    for attr,tag in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
        if attr in x.attrib:x.set(attr,str(maps[tag][int(x.get(attr))]))
    n=int(x.get('numFmtId','0'));x.set('numFmtId',str(num_map.get(n,n)))
    if stylemap is not None and 'xfId' in x.attrib:x.set('xfId',str(stylemap[int(x.get('xfId'))]))
    return x
target=element(oldstyle,'cellStyleXfs');source=element(newstyle,'cellStyleXfs');off=len(target)
stylemap={i:off+i for i in range(len(source))};target.extend(remap_xf(x) for x in source);target.set('count',str(len(target)))
target=element(oldstyle,'cellXfs');source=element(newstyle,'cellXfs');off=len(target)
cellmap={i:off+i for i in range(len(source))};target.extend(remap_xf(x,stylemap) for x in source);target.set('count',str(len(target)))
target=element(oldstyle,'dxfs');source=element(newstyle,'dxfs');off=len(target)
dxfmap={i:off+i for i in range(len(source))};target.extend(copy.deepcopy(list(source)));target.set('count',str(len(target)))
strings=ET.fromstring(new.read('xl/sharedStrings.xml')) if 'xl/sharedStrings.xml' in new.namelist() else []
replacements={'xl/styles.xml':ET.tostring(oldstyle,encoding='utf-8',xml_declaration=True)}
# Namespace-equivalent serialization is needed by Artifact Tool's OPC reader.
replacements['[Content_Types].xml']=old.read('[Content_Types].xml').replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
for sheetnum in [1,2]:
    name=f'xl/worksheets/sheet{sheetnum}.xml';sheet=ET.fromstring(new.read(name))
    for c in sheet.iter(q('c')):
        c.set('s',str(cellmap[int(c.get('s','0'))]))
        if c.get('t')=='s':
            v=c.find(q('v'));si=strings[int(v.text)];c.remove(v);c.set('t','inlineStr')
            ins=ET.Element(q('is'));ins.extend(copy.deepcopy(list(si)));c.append(ins)
    for col in sheet.iter(q('col')):
        if col.get('style') is not None:col.set('style',str(cellmap[int(col.get('style'))]))
    for row in sheet.iter(q('row')):
        if row.get('s') is not None:row.set('s',str(cellmap[int(row.get('s'))]))
    for rule in sheet.iter(q('cfRule')):
        if rule.get('dxfId') is not None:rule.set('dxfId',str(dxfmap[int(rule.get('dxfId'))]))
    relname=f'xl/worksheets/_rels/sheet{sheetnum}.xml.rels'
    if relname in new.namelist():
        nr=ET.fromstring(new.read(relname));orel=ET.fromstring(old.read(relname)) if relname in old.namelist() else []
        assert all(r.get('Type').endswith('/table') for r in nr), 'Unexpected generated sheet relationship'
        oldtabs=[r for r in orel if r.get('Type').endswith('/table')];newtabs=list(nr)
        assert len(oldtabs)==len(newtabs)
        relmap={n.get('Id'):o.get('Id') for n,o in zip(newtabs,oldtabs)}
        for tp in sheet.iter(q('tablePart')):tp.set('{'+REL+'}id',relmap[tp.get('{'+REL+'}id')])
    replacements[name]=ET.tostring(sheet,encoding='utf-8',xml_declaration=True)
staging=W/'outputs/taxon_mapping_package.xlsx'
with zipfile.ZipFile(staging,'w',zipfile.ZIP_DEFLATED) as z:
    for info in old.infolist():z.writestr(copy.deepcopy(info),replacements.get(info.filename,old.read(info.filename)))
final=V/'taxon_mapping.xlsx'
try:os.replace(staging,final)
except PermissionError:
    final=V/'taxon_mapping_review.xlsx';os.replace(staging,final)
zf=zipfile.ZipFile(final)
changed=[n for n in old.namelist() if old.read(n)!=zf.read(n)]
assert set(changed)==set(replacements),changed
# Check source style prefixes: every existing element remains in the same slot.
finalstyle=ET.fromstring(zf.read('xl/styles.xml'));originalstyle=ET.fromstring(old.read('xl/styles.xml'))
for tag in ['fonts','fills','borders','cellStyleXfs','cellXfs','numFmts','dxfs']:
    a=originalstyle.find(q(tag));b=finalstyle.find(q(tag))
    if a is not None:
        assert all(ET.tostring(x)==ET.tostring(y) for x,y in zip(a,b)),tag
result={'final_file':str(final),'changed_package_parts':changed,'unrelated_parts_byte_identical':True,'original_style_indexes_preserved':True,'original_shared_strings_preserved':('xl/sharedStrings.xml' not in old.namelist() or old.read('xl/sharedStrings.xml')==zf.read('xl/sharedStrings.xml')),'diagnostic_sheet_byte_identical':old.read('xl/worksheets/sheet3.xml')==zf.read('xl/worksheets/sheet3.xml'),'sha256':hashlib.sha256(final.read_bytes()).hexdigest()}
(W/'qa/appendix_package_preservation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
