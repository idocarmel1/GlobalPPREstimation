"""Read sparse OOXML values directly; same table contract as workbooks.read_book.
Use only for read-only verification/current identity work, no writer or solver.
"""
import re,posixpath
from zipfile import ZipFile
from lxml import etree as E
N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}';R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
def read_book(path):
 with ZipFile(path) as z:
  ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
  targets={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};result={}
  for sh in E.fromstring(z.read('xl/workbook.xml')).find(N+'sheets'):
   target=targets[sh.get(R+'id')];member=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target);sheet=E.fromstring(z.read(member));blocks={};name=None;header=None;records=[]
   for row in sheet.find(N+'sheetData'):
    vals=[]
    for c in row:
     if c.find(N+'f') is not None:raise ValueError('Formula in authoritative workbook')
     letters=re.match(r'[A-Z]+',c.get('r')).group();col=0
     for a in letters:col=col*26+ord(a)-64
     v=c.find(N+'v');t=c.get('t');value=None
     if t=='inlineStr':value=''.join(c.find(N+'is').itertext()) if c.find(N+'is') is not None else None
     elif v is not None and v.text is not None:
      raw=v.text
      if t=='s':value=ss[int(raw)]
      elif t=='b':value=bool(int(raw))
      elif t in ['str','e']:value=raw
      else:value=int(raw) if re.fullmatch(r'-?\d+',raw) else float(raw)
     if len(vals)<col:vals.extend([None]*(col-len(vals)))
     vals[col-1]=value
    while vals and vals[-1] is None:vals.pop()
    if not vals:continue
    if vals[0]=='@table':
     if name is not None:blocks[name]=(header or [],records)
     name=vals[1];header=None;records=[]
    elif name is not None:
     if header is None:header=[int(v) if isinstance(v,str) and v.isdigit() and 1950<=int(v)<=2019 else v for v in vals]
     else:records.append((vals+[None]*len(header))[:len(header)])
   if name is not None:blocks[name]=(header or [],records)
   result[sh.get('name')]=blocks
  return result

def block_edits(path,old,new):
 import openpyxl
 changes=[]
 with ZipFile(path) as z:
  targets={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};shs=E.fromstring(z.read('xl/workbook.xml')).find(N+'sheets')
  for sh in shs:
   sn=sh.get('name')
   if old[sn]==new[sn]:continue
   target=targets[sh.get(R+'id')];member=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target);positions={};active=None;header=False
   for row in E.fromstring(z.read(member)).find(N+'sheetData'):
    first=next((c for c in row if c.get('r')=='A'+row.get('r')),None);value=''.join(first.find(N+'is').itertext()) if first is not None and first.find(N+'is') is not None else first.find(N+'v').text if first is not None and first.find(N+'v') is not None else None
    if value=='@table':
     cell=next(c for c in row if c.get('r')=='B'+row.get('r'));active=''.join(cell.find(N+'is').itertext());positions[active]=[];header=True
    elif any(c.find(N+'is') is not None or c.find(N+'v') is not None for c in row):
     if header:header=False
     elif active:positions[active].append(int(row.get('r')))
   for tn,(h,rr) in old[sn].items():
    nh,nr=new[sn][tn];assert h==nh and len(nr)<=len(rr)
    if (h,rr)==(nh,nr):continue
    assert len(positions[tn])==len(rr),(sn,tn,len(positions[tn]),len(rr))
    for i,ri in enumerate(positions[tn]):
     after=nr[i] if i<len(nr) else [None]*len(h)
     for ci,(a,b) in enumerate(zip(rr[i],after),1):
      if a!=b:changes.append((sn,openpyxl.utils.get_column_letter(ci)+str(ri),a,b))
 return changes
