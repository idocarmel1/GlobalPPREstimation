from pathlib import Path
from lxml import etree as E
import json,zipfile,copy
B=Path(__file__).resolve().parent;P=B.parent.parent/'LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx'
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships';ns={'s':S}
with zipfile.ZipFile(P) as z:parts={i.filename:z.read(i.filename) for i in z.infolist()}
sheet=E.fromstring(parts['xl/worksheets/sheet2.xml']);styles=E.fromstring(parts['xl/styles.xml'])
fonts=styles.find('s:fonts',ns);xfs=styles.find('s:cellXfs',ns);changed={}
links=E.Element('{'+S+'}hyperlinks')
relationship_path='xl/worksheets/_rels/sheet2.xml.rels'
rels=E.fromstring(parts[relationship_path]) if relationship_path in parts else E.Element('{'+PKG+'}Relationships',nsmap={None:PKG})
for old in list(rels):
 if old.get('Type')==R+'/hyperlink':rels.remove(old)
for i,record in enumerate(json.loads((B/'qa/appendix_links.json').read_text()),1):
 c=sheet.find(f".//s:c[@r='{record['cell']}']",ns);sid=int(c.get('s','0'))
 if sid not in changed:
  xf=copy.deepcopy(xfs[sid]);font=copy.deepcopy(fonts[int(xf.get('fontId','0'))])
  for t in ['u','color']:
   for old in font.findall('s:'+t,ns):font.remove(old)
  E.SubElement(font,'{'+S+'}u',val='single');E.SubElement(font,'{'+S+'}color',rgb='FF0563C1');fonts.append(font);xf.set('fontId',str(len(fonts)-1));xf.set('applyFont','1');xfs.append(xf);changed[sid]=len(xfs)-1
 c.set('s',str(changed[sid]));h=E.SubElement(links,'{'+S+'}hyperlink',ref=record['cell']);h.set('{'+R+'}id',f'rIdCandidateLink{i}')
 E.SubElement(rels,'{'+PKG+'}Relationship',Id=f'rIdCandidateLink{i}',Type=R+'/hyperlink',Target=record['target'],TargetMode='External')
existing=sheet.find('s:hyperlinks',ns)
if existing is not None:sheet.remove(existing)
# hyperlink nodes belong after autoFilter/mergeCells, before page margins or other trailing nodes
later=sheet.find('s:pageMargins',ns)
if later is not None:sheet.insert(list(sheet).index(later),links)
else:sheet.append(links)
fonts.set('count',str(len(fonts)));xfs.set('count',str(len(xfs)))
parts['xl/worksheets/sheet2.xml']=E.tostring(sheet,encoding='utf-8',xml_declaration=True)
parts['xl/styles.xml']=E.tostring(styles,encoding='utf-8',xml_declaration=True)
parts['xl/worksheets/_rels/sheet2.xml.rels']=E.tostring(rels,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in parts.items():z.writestr(name,b)
print('Native portable hyperlinks written',len(links),'without HYPERLINK formula caches')
