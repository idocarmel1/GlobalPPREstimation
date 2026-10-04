"""Independently read the original Guenette et al. 2014 source bundle."""
from pathlib import Path
import sys, json, hashlib, zipfile, xml.etree.ElementTree as ET, re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT/'regions/LME_027/papers/CAN-2014'
sys.path.insert(0,str(HERE/'_deps'))
import xlrd, pdfplumber, pypdfium2
def save(name,data): (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
inventory=[]
for p in sorted(SOURCE.iterdir()):
    if p.is_file(): inventory.append({'file':str(p.relative_to(ROOT)).replace('\\','/'),'size':p.stat().st_size,'sha256':digest(p),'role': 'original_source' if p.suffix.lower() in ['.pdf','.xls','.docx','.tif'] else 'source_metadata'})
save('original_source_inventory.json',inventory)
for p in SOURCE.glob('*.xls'):
    book=xlrd.open_workbook(p,formatting_info=True); sheets=[]
    for sheet in book.sheets():
        cells=[]
        for r in range(sheet.nrows):
            for c in range(sheet.ncols):
                cell=sheet.cell(r,c)
                if cell.ctype==xlrd.XL_CELL_EMPTY: continue
                xf=book.xf_list[cell.xf_index]; fmt=book.format_map.get(xf.format_key)
                cells.append({'row':r+1,'column':c+1,'cell':xlrd.formula.colname(c)+str(r+1),'value':cell.value,'ctype':cell.ctype,'number_format':fmt.format_str if fmt else None,'font_bold':bool(book.font_list[xf.font_index].bold)})
        sheets.append({'sheet':sheet.name,'visibility':sheet.visibility,'rows':sheet.nrows,'columns':sheet.ncols,'cells':cells})
    save(p.name+'.cells.json',{'source_sha256':digest(p),'sheets':sheets})
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
p=SOURCE/'pone.0094742.s001-eb18ca66.docx'
with zipfile.ZipFile(p) as z: root=ET.fromstring(z.read('word/document.xml'))
tables=[];paragraphs=[];blocks=[]
for el in root.find('w:body',ns):
    if el.tag.endswith('}p'):
        s=''.join(t.text or '' for t in el.findall('.//w:t',ns));paragraphs.append(s);blocks.append(s)
    elif el.tag.endswith('}tbl'):
        rows=[[''.join(t.text or '' for t in c.findall('.//w:t',ns)) for c in r.findall('w:tc',ns)] for r in el.findall('w:tr',ns)]
        tables.append(rows); blocks.append('TABLE '+str(len(tables))+'\n'+'\n'.join('\t'.join(r) for r in rows))
save('original_docx_tables.json',{'source_sha256':digest(p),'tables':tables})
(HERE/'original_supplement.txt').write_text('\n'.join(blocks),encoding='utf-8')
with pdfplumber.open(SOURCE/'file-e30dfe50.pdf') as pdf:
    texts=[];words=[]
    for n,page in enumerate(pdf.pages,1):
        texts.append(f'=== PDF/printed page {n} ===\n'+(page.extract_text() or ''))
        if n in [4,5]:words.append({'page':n,'width':page.width,'height':page.height,'words':page.extract_words(x_tolerance=0.4)})
(HERE/'original_article_text.txt').write_text('\n\n'.join(texts),encoding='utf-8');save('article_table1_coordinate_words.json',words)
doc=pypdfium2.PdfDocument(str(SOURCE/'file-e30dfe50.pdf'))
for n in [4,5]: doc[n-1].render(scale=250/72).to_pil().save(HERE/f'original_article_page_{n}_250dpi.png')
pattern=re.compile(r'assimil|egest|accumul|discard|stanza|equilibrium|mortality|detrit|pBA|M30|P30|habitat|import|transition',re.I)
hits=[{'source':'article','line':i+1,'text':x} for i,x in enumerate('\n'.join(texts).splitlines()) if pattern.search(x)]
hits += [{'source':'supplement','paragraph':i+1,'text':x} for i,x in enumerate(paragraphs) if pattern.search(x)]
save('prose_sweep.json',hits)
print('Original files',len(inventory),'DOCX tables',[(i+1,len(x),len(x[0])) for i,x in enumerate(tables)])
