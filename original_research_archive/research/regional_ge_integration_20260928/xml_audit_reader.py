"""Read project-authored inline-string tables directly for an independent audit."""
import zipfile,posixpath
from lxml import etree as E
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
RNS='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
TAG='{'+NS+'}'

def read_book(path):
    result={}
    with zipfile.ZipFile(path) as z:
        rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[''.join(n.itertext()) for n in E.fromstring(z.read('xl/sharedStrings.xml'))]
        for sheet in E.fromstring(z.read('xl/workbook.xml')).find(TAG+'sheets'):
            target=rels[sheet.get('{'+RNS+'}id')]
            name=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            blocks={};table=None;header=None;data=[]
            with z.open(name) as f:
                for _,row in E.iterparse(f,events=('end',),tag=TAG+'row'):
                    cells={}
                    for cell in row:
                        ref=cell.get('r','');column=0
                        for c in ref:
                            if not c.isalpha():break
                            column=column*26+ord(c)-64
                        assert cell.find(TAG+'f') is None,'Formula in audit input'
                        typ=cell.get('t');v=cell.find(TAG+'v')
                        if typ=='inlineStr':
                            inline=cell.find(TAG+'is')
                            value=None if inline is None else ''.join(inline.itertext())
                        elif v is None:value=None
                        elif typ=='s':value=shared[int(v.text)]
                        elif typ=='b':value=v.text=='1'
                        elif typ in ('str','e'):value=v.text
                        else:
                            raw=v.text
                            value=float(raw) if any(c in raw.lower() for c in '.e') else int(raw)
                        cells[column-1]=value
                    vals=[cells.get(i) for i in range(max(cells,default=-1)+1)]
                    while vals and vals[-1] is None:vals.pop()
                    if vals:
                        if vals[0]=='@table':
                            if table is not None:blocks[table]=(header or [],data)
                            table=vals[1];header=None;data=[]
                        elif table is not None:
                            if header is None:header=[int(v) if isinstance(v,str) and v.isdigit() and 1950<=int(v)<=2019 else v for v in vals]
                            else:data.append((vals+[None]*len(header))[:len(header)])
                    row.clear()
                    while row.getprevious() is not None:del row.getparent()[0]
            if table is not None:blocks[table]=(header or [],data)
            result[sheet.get('name')]=blocks
    return result
