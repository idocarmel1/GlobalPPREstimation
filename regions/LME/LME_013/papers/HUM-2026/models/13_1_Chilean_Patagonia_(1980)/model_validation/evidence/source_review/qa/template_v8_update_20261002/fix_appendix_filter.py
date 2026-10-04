from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import shutil,json,hashlib
QA=Path(__file__).resolve().parent
ROOT=QA.parents[5]
path=ROOT/'regions/LME_013/LME013_taxon_mapping_appendix.xlsx'
backup=QA/'baseline_appendix.xlsx'
if not backup.exists():shutil.copy2(path,backup)
with ZipFile(backup) as z:
    infos=z.infolist();parts={i.filename:z.read(i.filename) for i in infos}
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
changed=[]
for name,value in list(parts.items()):
    if not name.startswith('xl/tables/') or not name.endswith('.xml'):continue
    node=etree.fromstring(value)
    if node.get('name')!='HumboldtMappingTable':continue
    assert node.get('ref')=='A7:G225'
    assert node.find('{'+S+'}autoFilter') is None
    af=etree.Element('{'+S+'}autoFilter',ref=node.get('ref'))
    node.insert(0,af)
    parts[name]=etree.tostring(node,encoding='UTF-8',xml_declaration=True,standalone=True)
    changed.append(name)
assert len(changed)==1
candidate=QA/'appendix_filter_updated.xlsx'
with ZipFile(candidate,'w') as z:
    for i in infos:z.writestr(i,parts[i.filename])
with ZipFile(backup) as a,ZipFile(candidate) as b:
    assert [n for n in a.namelist() if a.read(n)!=b.read(n)]==changed
shutil.copy2(candidate,path)
result={'changed_package_parts':changed,'all_worksheet_values_styles_links_unchanged':True,'change':'Enable native table filter A7:G225','baseline_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'updated_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(QA/'appendix_filter_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
