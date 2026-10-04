"""Add native OOXML hyperlinks/filters omitted by the artifact library; do not alter data."""
from pathlib import Path
import json,zipfile,posixpath,copy
from lxml import etree as E
C=Path(__file__).resolve().parents[1];P=C/'LME027_candidate_taxon_mapping_appendix.xlsx'
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
sources=json.loads((C/'mapping/appendix_sources.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(P) as z:parts={n:z.read(n) for n in z.namelist()}
root=E.fromstring(parts['xl/worksheets/sheet2.xml'])
links=root.find(f'{{{S}}}hyperlinks')
if links is None:links=E.Element(f'{{{S}}}hyperlinks')
else:root.remove(links);links.clear()
relpath='xl/worksheets/_rels/sheet2.xml.rels'
rels=E.fromstring(parts[relpath]) if relpath in parts else E.Element(f'{{{PKG}}}Relationships',nsmap={None:PKG})
for old in list(rels):
    if old.get('Type','').endswith('/hyperlink'):rels.remove(old)
for i,s in enumerate(sources):
    target=s['target'] if s['target'].startswith(('https://','http://')) else posixpath.normpath('mapping/'+s['target'])
    rid='rIdCandidateLink'+str(i+1)
    E.SubElement(rels,f'{{{PKG}}}Relationship',Id=rid,Type=R+'/hyperlink',Target=target,TargetMode='External')
    el=E.SubElement(links,f'{{{S}}}hyperlink',ref='C'+str(i+5));el.set(f'{{{R}}}id',rid)
    # Enforce blue and underlined appearance through the existing cell's font.
root.append(links)
# Place hyperlinks before print/page/drawing controls per SpreadsheetML sequence.
after_tags={'printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst'}
root.remove(links)
index=next((i for i,e in enumerate(root) if E.QName(e).localname in after_tags),len(root));root.insert(index,links)
parts['xl/worksheets/sheet2.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
parts[relpath]=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
for name,ref in [('xl/tables/table1.xml','A7:G519'),('xl/tables/table2.xml','A4:D16')]:
    t=E.fromstring(parts[name]);af=t.find(f'{{{S}}}autoFilter')
    if af is None:t.insert(0,E.Element(f'{{{S}}}autoFilter',ref=ref))
    else:af.set('ref',ref)
    parts[name]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
# Preserve displayed source-cell style; repair unsupported underline export if needed.
styles=E.fromstring(parts['xl/styles.xml']);fonts=styles.find(f'{{{S}}}fonts');xfs=styles.find(f'{{{S}}}cellXfs')
for c in root.findall(f'.//{{{S}}}c'):
    if c.get('r') in {'C'+str(i+5) for i in range(len(sources))}:
        xf=xfs[int(c.get('s','0'))];font=fonts[int(xf.get('fontId','0'))]
        color=font.find(f'{{{S}}}color')
        if color is None:color=E.SubElement(font,f'{{{S}}}color')
        color.attrib.clear();color.set('rgb','FF0563C1')
        u=font.find(f'{{{S}}}u')
        if u is None:u=E.SubElement(font,f'{{{S}}}u')
        u.set('val','single')
parts['xl/styles.xml']=E.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
    for n,v in parts.items():z.writestr(n,v)
print('Patched 12 native hyperlinks and two native filters; no scientific cell changes.')
