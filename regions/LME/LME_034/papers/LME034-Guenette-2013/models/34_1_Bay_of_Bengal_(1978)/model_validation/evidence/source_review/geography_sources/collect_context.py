from pathlib import Path
import json, sys
import openpyxl
import pypdfium2

root = Path.cwd()
out = root / 'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/geography_sources'
source = root / 'regions/LME_034/papers/LME034-Guenette-2013/009031359-84f3dc3d.pdf'
pdf = pypdfium2.PdfDocument(str(source))
texts = [pdf[i].get_textpage().get_text_range() for i in range(len(pdf))]
(out / 'source_text_by_page.txt').write_text('\n\n'.join(f'=== PDF AND PRINTED PAGE {i+1} ===\n{t}' for i,t in enumerate(texts)), encoding='utf8')

w = openpyxl.load_workbook(root/'Project.xlsx', read_only=True, data_only=False)
central = {}
for sheet_name in ['Papers', 'Models & coverage']:
    sheet = w[sheet_name]
    headers = None
    relevant = []
    for row in sheet.values:
        values = list(row)
        if not values or not any(x is not None for x in values): continue
        if values[0] == '@table':
            headers = None
            continue
        if headers is None:
            headers = values
            continue
        d = dict(zip(headers,values))
        if d.get('unit_id') == 'LME_034': relevant.append(d)
    central[sheet_name] = relevant
w.close()
(out/'central_context.json').write_text(json.dumps(central,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(central,ensure_ascii=False,indent=2))
for i,t in enumerate(texts):
    if any(s in t.lower() for s in ['scenario','another model','alternative model','model was fitted','fitted model','unfitted','initial model']):
        lines = [l for l in t.splitlines() if any(s in l.lower() for s in ['scenario','another model','alternative model','fitted','unfitted','initial model'])]
        print(f'PAGE {i+1}: '+' / '.join(lines))
