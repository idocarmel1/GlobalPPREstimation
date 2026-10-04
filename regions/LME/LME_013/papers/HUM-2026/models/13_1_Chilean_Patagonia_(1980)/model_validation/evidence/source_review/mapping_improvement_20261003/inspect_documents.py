from pathlib import Path
import json,sys
from docx import Document
from lxml import etree
import zipfile
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records
b=json.loads((OUT/'baseline_tables.json').read_text(encoding='utf-8'))
print('BASELINE CONFIDENCE')
print('See retained coverage_summary.json; report below')
d=Document(REG/'Model_validation_13_1_Chilean_Patagonia_(1980).docx')
print('DOC PARAGRAPHS')
for i,p in enumerate(d.paragraphs):
    if p.text: print(i,p.text)
print('DOC TABLES')
for ti,t in enumerate(d.tables):
    print('TABLE',ti,len(t.rows))
    for ri,r in enumerate(t.rows):
        if ti==0 or ti in [1,2,3]:print(ri,[c.text for c in r.cells])
        elif ri==0:print([c.text for c in r.cells])
w=openpyxl.load_workbook(REG/'LME013_taxon_mapping_appendix.xlsx');print('APPENDIX')
for s in w:
    print(s.title,s.max_row,s.max_column,s.freeze_panes,s.auto_filter.ref)
    for r in list(s.values)[:9]:print(r)
print('GROUPS')
for r in records(b,'Selected model groups','Groups'):print({k:r.get(k) for k in ['seq','group_name','taxon_descr','catch','biomass']})
