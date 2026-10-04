from pathlib import Path
import json,sys,hashlib,math,openpyxl
from ooxml_preserve import patch_cells,package,save_package
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent;REG=OUT.parents[2]
updates=json.loads((OUT/'appendix_updates.json').read_text(encoding='utf-8'))
stage=openpyxl.load_workbook(OUT/'appendix_authored.xlsx')
for sheet,cells in updates.items():
    for a,want in cells.items():assert stage[sheet][a].value==want
live=REG/'LME013_taxon_mapping_appendix.xlsx';before=hashlib.sha256(live.read_bytes()).hexdigest()
patch_cells(live,OUT/'appendix_presentation_verified.xlsx',updates)
check=openpyxl.load_workbook(OUT/'appendix_presentation_verified.xlsx')
for sheet,cells in updates.items():
    for a,want in cells.items():assert check[sheet][a].value==want
assert hashlib.sha256(live.read_bytes()).hexdigest()==before,'concurrent appendix edit'
infos,parts=package(OUT/'appendix_presentation_verified.xlsx');save_package(live,infos,parts)
print('Appendix presentation corrections saved after staged-value verification.')
