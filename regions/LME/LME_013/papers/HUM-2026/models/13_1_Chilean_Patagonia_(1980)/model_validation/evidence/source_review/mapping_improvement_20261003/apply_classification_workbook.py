from pathlib import Path
import sys,json,hashlib,openpyxl
from ooxml_preserve import patch_blocks,package,save_package
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=OUT.parents[2];sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,input_hash,overview
from regional import result_hash
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
live=REG/'LME_013.xlsx';before=hashlib.sha256(live.read_bytes()).hexdigest();changes=load('classification_changed_blocks.json')
stage=openpyxl.load_workbook(OUT/'regional_authored.xlsx');manifest=load('regional_authoring_manifest.json')
for item in manifest:
    if item['block'] in changes.get(item['sheet'],{}):
        h,rows=changes[item['sheet']][item['block']]
        for ri,row in enumerate(rows,item['start']+2):
            for ci,want in enumerate(row,1):assert stage[item['sheet']].cell(ri,ci).value==want
patch_blocks(live,OUT/'regional_classification_verified.xlsx',changes)
saved=read_book(OUT/'regional_classification_verified.xlsx');assert json.loads(json.dumps(saved,ensure_ascii=False))==load('adopted_tables.json')
assert overview(saved)['calculation_input_sha256']==input_hash(saved)
assert overview(saved)['calculation_result_sha256']==result_hash(saved)
assert hashlib.sha256(live.read_bytes()).hexdigest()==before,'concurrent regional edit'
infos,parts=package(OUT/'regional_classification_verified.xlsx');save_package(live,infos,parts)
print('Metadata correction saved; numerical results and freshness hashes are unchanged.')
