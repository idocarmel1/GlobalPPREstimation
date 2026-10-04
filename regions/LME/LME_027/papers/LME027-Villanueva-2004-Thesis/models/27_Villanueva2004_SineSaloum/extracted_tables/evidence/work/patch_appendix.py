from pathlib import Path
import json,zipfile,posixpath
from lxml import etree as E
C=Path(__file__).resolve().parents[1];P=C/'LME027_Villanueva2004_thesis_taxon_mapping_appendix.xlsx'
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships'
sources=json.loads((C/'mapping/appendix_sources.json').read_text(encoding='utf8'))
with zipfile.ZipFile(P) as z:parts={n:z.read(n) for n in z.namelist()}
root=E.fromstring(parts['xl/worksheets/sheet2.xml']);links=root.find(f'{{{S}}}hyperlinks')
if links is None:links=E.Element(f'{{{S}}}hyperlinks')
else:root.remove(links);links.clear()
relpath='xl/worksheets/_rels/sheet2.xml.rels';rels=E.fromstring(parts[relpath]) if relpath in parts else E.Element(f'{{{PKG}}}Relationships',nsmap={None:PKG})
for old in list(rels):
 if old.get('Type','').endswith('/hyperlink'):rels.remove(old)
for i,s in enumerate(sources):
 target=s['target'] if s['target'].startswith(('https://','http://')) else posixpath.normpath('mapping/'+s['target'])
 if not target.startswith(('https://','http://')):
  assert (C/target.split('#')[0]).exists(),(s['id'],target)
 rid='rIdSourceLink'+str(i+1);E.SubElement(rels,f'{{{PKG}}}Relationship',Id=rid,Type=R+'/hyperlink',Target=target,TargetMode='External');el=E.SubElement(links,f'{{{S}}}hyperlink',ref='C'+str(i+5));el.set(f'{{{R}}}id',rid)
after={'printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst'}
index=next((i for i,e in enumerate(root) if E.QName(e).localname in after),len(root));root.insert(index,links)
parts['xl/worksheets/sheet2.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True);parts[relpath]=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
for name in [n for n in parts if n.startswith('xl/tables/table') and n.endswith('.xml')]:
 t=E.fromstring(parts[name]);af=t.find(f'{{{S}}}autoFilter')
 if af is None:t.insert(0,E.Element(f'{{{S}}}autoFilter',ref=t.get('ref')))
 else:af.set('ref',t.get('ref'))
 parts[name]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
styles=E.fromstring(parts['xl/styles.xml']);fonts=styles.find(f'{{{S}}}fonts');xfs=styles.find(f'{{{S}}}cellXfs')
for c in root.findall(f'.//{{{S}}}c'):
 if c.get('r') in {'C'+str(i+5) for i in range(len(sources))}:
  font=fonts[int(xfs[int(c.get('s','0'))].get('fontId','0'))];color=font.find(f'{{{S}}}color')
  if color is None:color=E.SubElement(font,f'{{{S}}}color')
  color.attrib.clear();color.set('rgb','FF0563C1');u=font.find(f'{{{S}}}u')
  if u is None:u=E.SubElement(font,f'{{{S}}}u')
  u.set('val','single')
parts['xl/styles.xml']=E.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in parts.items():z.writestr(n,v)
print(f'{len(sources)} relative/external native hyperlinks and native filters added; scientific data unchanged.')
