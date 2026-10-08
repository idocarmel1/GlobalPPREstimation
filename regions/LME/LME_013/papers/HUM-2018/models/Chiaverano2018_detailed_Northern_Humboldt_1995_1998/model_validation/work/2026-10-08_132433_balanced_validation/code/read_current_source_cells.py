from pathlib import Path
import sys,tempfile,hashlib,json,re
sys.path.insert(0,str(Path(tempfile.gettempdir())/'lme013_validation_xlrd'))
import xlrd
RUN=Path(__file__).resolve().parents[1];MODEL=Path(__file__).resolve().parents[4]
p=MODEL.parents[1]/'sources/Supplementary material revised and final.xls'
w=xlrd.open_workbook(p,formatting_info=True)
selected={1:['C14','D14','H14','J14','L14','H41'],2:['H4','H7','H8','H9','H39'],8:['F14','I14','J14','K14']}
cells=[]
for index,addresses in selected.items():
    s=w.sheet_by_index(index)
    for address in addresses:
        row=int(re.search(r'\d+',address)[0])-1;col=ord(address[0])-65
        cells.append(dict(sheet=s.name,cell=address,value=s.cell_value(row,col),
          bold=bool(w.font_list[w.xf_list[s.cell_xf_index(row,col)].font_index].bold)))
sourcehash=hashlib.sha256(p.read_bytes()).hexdigest()
assert sourcehash=='fd28a9367e20bfc9ed3d136460e22c476155ae5bf61ce75b4b17ebf8a9b7aef2'
assert cells[3]['value']==5.6513425 and cells[4]['value']==.17462648325000002
(RUN/'qa/current_source_cells.json').write_text(json.dumps(dict(source_sha256=sourcehash,cells=cells),ensure_ascii=False,indent=2),encoding='utf-8')
print('Fresh source cells verified and saved:',len(cells))
