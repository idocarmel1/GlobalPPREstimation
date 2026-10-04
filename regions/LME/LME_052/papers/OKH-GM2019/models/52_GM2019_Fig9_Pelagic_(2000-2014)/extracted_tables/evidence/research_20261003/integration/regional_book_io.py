"""Fast exact-type XML reader for existing regional @table workbooks.

Same authority/schema as tools.workbooks.read_book; this avoids openpyxl's
expansion of the wide historical Diagnostics sheets. Uses no formula caches.
"""
import re,zipfile
from xml.etree import ElementTree as ET

S="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
YEARS=set(range(1950,2020))

def read_fast(path):
    book={}
    with zipfile.ZipFile(path)as archive:
        shared=[]
        if "xl/sharedStrings.xml"in archive.namelist():
            shared=["".join(t.text or""for t in node.iter(f"{{{S}}}t"))for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        rel={r.get("Id"):r.get("Target")for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        xml=ET.fromstring(archive.read("xl/workbook.xml"))
        for meta in xml.find(f"{{{S}}}sheets"):
            target=rel[meta.get(f"{{{R}}}id")]
            target=target.lstrip("/")if target.startswith("/")else"xl/"+target
            blocks={};name=None;header=None;records=[]
            for row in ET.fromstring(archive.read(target)).find(f"{{{S}}}sheetData"):
                values={}
                for cell in row:
                    if cell.tag!=f"{{{S}}}c":continue
                    if cell.find(f"{{{S}}}f")is not None:raise ValueError("Authoritative regional tables cannot contain formulas")
                    col=0
                    for letter in re.match("[A-Z]+",cell.get("r")).group():col=26*col+ord(letter)-64
                    typ=cell.get("t")
                    node=cell.find(f"{{{S}}}v")
                    raw=node.text if node is not None else None
                    if typ=="inlineStr":value="".join(t.text or""for t in cell.iter(f"{{{S}}}t"))
                    elif typ=="s":value=shared[int(raw)]if raw is not None else None
                    elif typ=="b":value=raw=="1"if raw is not None else None
                    elif typ in {"str","e"}:value=raw
                    else:
                        if raw is None:value=None
                        elif re.fullmatch(r"-?\d+",raw):value=int(raw)
                        else:value=float(raw)
                    values[col-1]=value
                if not values:continue
                vals=[values.get(i)for i in range(max(values)+1)]
                while vals and vals[-1]is None:vals.pop()
                if not vals:continue
                if vals[0]=="@table":
                    if name is not None:blocks[name]=(header or[],records)
                    name=vals[1];header=None;records=[]
                elif name is not None:
                    if header is None:header=[int(v)if isinstance(v,str)and v.isdigit()and int(v)in YEARS else v for v in vals]
                    else:records.append((vals+[None]*len(header))[:len(header)])
            if name is not None:blocks[name]=(header or[],records)
            book[meta.get("name")]=blocks
    return book

if __name__=="__main__":
    import json,sys
    from pathlib import Path
    ROOT=Path(__file__).resolve().parents[6]
    sys.path.insert(0,str(ROOT/"tools"))
    from workbooks import overview,input_hash
    p=ROOT/"regions/LME_052/LME_052.xlsx"
    book=read_fast(p)
    print(json.dumps({"overview":overview(book),"input_hash":input_hash(book),"stored_input_hash":overview(book).get("calculation_input_sha256"),"table_count":sum(map(len,book.values()))},ensure_ascii=False,indent=2))
