"""Artifact-tool lacks HYPERLINK calculation; add native hyperlinks via OOXML.
No table values, scientific numbers, formulas or layout are changed.
"""
import json,zipfile,copy,urllib.parse
from pathlib import Path
from lxml import etree as E
Q=Path(__file__).resolve().parent;REG=Q.parents[2];path=REG/'HS071_taxon_mapping_appendix.xlsx'
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';P='http://schemas.openxmlformats.org/package/2006/relationships';N={'s':NS}
links=json.loads((Q/'hyperlinks.json').read_text(encoding='utf-8'));z=zipfile.ZipFile(path);parts={n:z.read(n) for n in z.namelist()};z.close()
style=E.fromstring(parts['xl/styles.xml']);fonts=style.find('s:fonts',N);xfs=style.find('s:cellXfs',N);cache={}
for si in [1,2]:
 sn=f'xl/worksheets/sheet{si}.xml';doc=E.fromstring(parts[sn]);hn=doc.find('s:hyperlinks',N)
 if hn is not None:doc.remove(hn)
 hn=E.Element('{'+NS+'}hyperlinks');rp=f'xl/worksheets/_rels/sheet{si}.xml.rels'
 rel=E.fromstring(parts[rp]) if rp in parts else E.Element('{'+P+'}Relationships')
 for rr in list(rel):
  if rr.get('Id','').startswith('rIdValidationLink'):rel.remove(rr)
 for li,l in enumerate([l for l in links if l['sheet']==si],1):
  target=l['target'];h=E.SubElement(hn,'{'+NS+'}hyperlink',ref=l['ref'])
  if target.startswith('#'):h.set('location',target[1:])
  else:
   rid='rIdValidationLink'+str(li);h.set('{'+R+'}id',rid);E.SubElement(rel,'{'+P+'}Relationship',Id=rid,Type=R+'/hyperlink',Target=urllib.parse.quote(target,safe='/:?=&%#'),TargetMode='External')
  cell=doc.find(f".//s:c[@r='{l['ref']}']",N);assert cell is not None
  old=int(cell.get('s','0'))
  if old not in cache:
   xf=copy.deepcopy(xfs[old]);font=copy.deepcopy(fonts[int(xf.get('fontId','0'))])
   for tag in ['color','u']:
    for n in list(font):
     if E.QName(n).localname==tag:font.remove(n)
   E.SubElement(font,'{'+NS+'}color',rgb='FF0563C1');E.SubElement(font,'{'+NS+'}u',val='single');fid=len(fonts);fonts.append(font);fonts.set('count',str(len(fonts)));xf.set('fontId',str(fid));xf.set('applyFont','1');cache[old]=len(xfs);xfs.append(xf);xfs.set('count',str(len(xfs)))
  cell.set('s',str(cache[old]))
 # Hyperlinks occur after merges, before print/drawing/extension elements.
 after={'mergeCells','conditionalFormatting','dataValidations','autoFilter','sheetData','sheetProtection','protectedRanges','scenarios'}
 index=max([i+1 for i,n in enumerate(doc) if E.QName(n).localname in after],default=len(doc));doc.insert(index,hn)
 parts[sn]=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True);parts[rp]=E.tostring(rel,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['xl/styles.xml']=E.tostring(style,xml_declaration=True,encoding='UTF-8',standalone=True)
temp=path.with_suffix('.native.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as out:
 for n,v in parts.items():out.writestr(n,v)
temp.replace(path);print('Native blue-underlined hyperlinks',len(links))
