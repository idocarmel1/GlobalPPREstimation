from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,sys,hashlib,math,openpyxl
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,validate_region,overview,input_hash
from regional import result_hash
from ooxml_preserve import package,patch_blocks,patch_cells,save_package,sheet_paths,q,NS
def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=load('baseline_tables.json');adopted=load('adopted_tables.json');changes=load('regional_changed_blocks.json')
manifest=load('baseline_manifest.json')
# Reject concurrent edits instead of replacing researcher changes.
for name in ['LME_013.xlsx','LME013_taxon_mapping_appendix.xlsx']:
    assert sha(REG/name)==sha(OUT/'baseline'/name),('concurrent edit',name)
# Check every authored value against the calculated mutation before splicing.
stage=openpyxl.load_workbook(OUT/'regional_authored.xlsx',data_only=False)
for item in load('regional_authoring_manifest.json'):
    sh=stage[item['sheet']];header,rows=changes[item['sheet']][item['block']]
    for offset,row in enumerate([['@table',item['block']],header,*rows,[]]):
        for ci,want in enumerate(row,1):
            got=sh.cell(item['start']+offset,ci).value
            if isinstance(want,(int,float)) and not isinstance(want,bool):assert isinstance(got,(int,float)) and math.isclose(got,want,rel_tol=1e-14,abs_tol=1e-14),(item,offset,ci,got,want)
            else:assert got==want,(item,offset,ci,got,want)
patch_blocks(OUT/'baseline/LME_013.xlsx',OUT/'regional_verified.xlsx',changes)
saved=read_book(OUT/'regional_verified.xlsx')
assert json.loads(json.dumps(saved,ensure_ascii=False))==adopted,'regional OOXML round trip changed values'
validate_region(saved,REG/'LME_013.xlsx')
assert overview(saved)['calculation_input_sha256']==input_hash(saved)
assert overview(saved)['calculation_result_sha256']==result_hash(saved)
updates=load('appendix_updates.json');links=load('appendix_links.json')
staged=openpyxl.load_workbook(OUT/'appendix_authored.xlsx',data_only=False)
for sheet,cells in updates.items():
    for address,want in cells.items():assert staged[sheet][address].value==want,(sheet,address)
patch_cells(OUT/'baseline/LME013_taxon_mapping_appendix.xlsx',OUT/'appendix_verified.xlsx',updates,links)
# Match existing uncertainty shading to the changed confidence, without editing styles.
infos,parts=package(OUT/'appendix_verified.xlsx');p=sheet_paths(parts)['Taxon mapping'];xml=etree.fromstring(parts[p])
for c in xml.xpath('.//s:c',namespaces=NS):
    if c.get('r') in updates['Taxon mapping'] and c.get('r').startswith('F'):
        v=updates['Taxon mapping'][c.get('r')];c.set('s','9' if v in ['Very low','Low','Unresolved'] else '6')
parts[p]=etree.tostring(xml,encoding='utf-8');save_package(OUT/'appendix_verified.xlsx',infos,parts)
check=openpyxl.load_workbook(OUT/'appendix_verified.xlsx')
for sheet,cells in updates.items():
    for address,want in cells.items():assert check[sheet][address].value==want
assert check['Taxon mapping'].max_column==7 and check['Taxon mapping'].max_row==225
# All proofs precede the authorized replacement.
for scratch,name in [('regional_verified.xlsx','LME_013.xlsx'),('appendix_verified.xlsx','LME013_taxon_mapping_appendix.xlsx')]:
    infos,parts=package(OUT/scratch);save_package(REG/name,infos,parts)
print('Regional and appendix saved; regional values round-trip exactly and fresh hashes agree.')
