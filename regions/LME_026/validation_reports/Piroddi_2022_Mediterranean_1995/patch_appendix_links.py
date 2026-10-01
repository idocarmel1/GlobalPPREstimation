from pathlib import Path
from copy import deepcopy
import json,zipfile
from lxml import etree as E
OUT=Path(__file__).parent; REGION=OUT.parents[1];dest=REGION/'LME026_taxon_mapping_appendix.xlsx'
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main';rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships';pkg='http://schemas.openxmlformats.org/package/2006/relationships'
with zipfile.ZipFile(dest) as z:data={n:z.read(n) for n in z.namelist()}
styles=E.fromstring(data['xl/styles.xml']);fonts=styles.find('{'+ns+'}fonts');xfs=styles.find('{'+ns+'}cellXfs');sheet=E.fromstring(data['xl/worksheets/sheet2.xml']);maps={}
for c in sheet.findall('.//{'+ns+'}c'):
    if c.get('r','').startswith('E') and int(c.get('r')[1:])>=5:
        old=int(c.get('s','0'))
        if old not in maps:
            xf=deepcopy(xfs[old]);font=deepcopy(fonts[int(xf.get('fontId','0'))])
            for n in list(font):
                if E.QName(n).localname in ['color','u']:font.remove(n)
            E.SubElement(font,'{'+ns+'}color',rgb='FF0563C1');E.SubElement(font,'{'+ns+'}u',val='single');fonts.append(font);fonts.set('count',str(len(fonts)))
            xf.set('fontId',str(len(fonts)-1));xf.set('applyFont','1');xfs.append(xf);xfs.set('count',str(len(xfs)));maps[old]=len(xfs)-1
        c.set('s',str(maps[old]))
links=E.SubElement(sheet,'{'+ns+'}hyperlinks');rels=E.fromstring(data['xl/worksheets/_rels/sheet2.xml.rels']) if 'xl/worksheets/_rels/sheet2.xml.rels' in data else E.Element('{'+pkg+'}Relationships',nsmap={None:pkg})
sources=json.loads((OUT/'appendix_sources.json').read_text(encoding='utf-8'))
for i,s in enumerate(sources,5):
    rid='rIdSource'+str(i);E.SubElement(links,'{'+ns+'}hyperlink',ref='E'+str(i),attrib={'{'+rel+'}id':rid},display='Open source');E.SubElement(rels,'{'+pkg+'}Relationship',Id=rid,Type=rel+'/hyperlink',Target=s['target'],TargetMode='External')
# hyperlinks must precede later drawing/table elements under worksheet schema.
sheet.remove(links);later=next((x for x in sheet if E.QName(x).localname in ['printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst']),None)
if later is None:sheet.append(links)
else:sheet.insert(sheet.index(later),links)
for n,x in [('xl/styles.xml',styles),('xl/worksheets/sheet2.xml',sheet),('xl/worksheets/_rels/sheet2.xml.rels',rels)]:data[n]=E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in data.items():z.writestr(n,b)
print(json.dumps({'native_hyperlinks':len(sources),'blue_underlined_effective_styles':len(maps),'no_hyperlink_formula_cache':True}))
