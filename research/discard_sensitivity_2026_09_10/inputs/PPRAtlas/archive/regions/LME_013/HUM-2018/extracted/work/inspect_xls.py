from pathlib import Path
import json,openpyxl
w=Path(__file__).parent
b=openpyxl.load_workbook(w/'supplement.xlsx',data_only=False)
for sh in b:
 print(sh.title,sh.max_row,sh.max_column,sh.sheet_state)
 vals=[[c.value for c in row] for row in sh]
 (w/(sh.title.replace('/','_')+'.json')).write_text(json.dumps(vals,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
 for i,row in enumerate(vals[:12]):print(i+1,str(row)[:400])

