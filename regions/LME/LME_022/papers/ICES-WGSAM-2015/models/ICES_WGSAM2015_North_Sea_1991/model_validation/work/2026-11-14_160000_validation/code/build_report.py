from pathlib import Path
from copy import deepcopy
import sys, json, hashlib, zipfile, os
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve()
while not (ROOT/'Project.xlsx').exists(): ROOT = ROOT.parent
BASE = ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991/model_validation'
RUN = BASE/'work/2026-11-14_160000_validation'
REVIEW = ROOT/'regions/LME/LME_022/work/2026-11-14_160000_validation/outputs'
TEMPLATE = ROOT/'tools/templates/validation.docx'
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import format_percent, verify_report

audit=json.loads((REVIEW/'mapping_audit.json').read_text(encoding='utf-8'))
content=json.loads((RUN/'inputs/report_content.json').read_text(encoding='utf-8'))
doc=Document(TEMPLATE)
paras=list(doc.paragraphs)
tables=list(doc.tables)

def text(paragraph, value):
    ppr=deepcopy(paragraph._p.pPr) if paragraph._p.pPr is not None else None
    paragraph.clear()
    paragraph.add_run(value)

def cell(c, value):
    paragraphs=value.split('\n')
    template_p=deepcopy(c.paragraphs[0]._p)
    template_rpr=deepcopy(c.paragraphs[0].runs[0]._r.rPr) if c.paragraphs[0].runs and c.paragraphs[0].runs[0]._r.rPr is not None else None
    c.text=''
    for i, line in enumerate(paragraphs):
        p=c.paragraphs[0] if i==0 else c.add_paragraph()
        if template_p.pPr is not None:
            p._p.insert(0,deepcopy(template_p.pPr))
        run=p.add_run(line)
        if template_rpr is not None:run._r.insert(0,deepcopy(template_rpr))

def link(p,label,target):
    if not target.startswith(('http://','https://','#')):
        target=os.path.relpath(ROOT/target,BASE).replace('\\','/')
    e=OxmlElement('w:hyperlink')
    e.set(qn('r:id'),p.part.relate_to(target,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r'); pr=OxmlElement('w:rPr')
    color=OxmlElement('w:color');color.set(qn('w:val'),'0563C1');pr.append(color)
    under=OxmlElement('w:u');under.set(qn('w:val'),'single');pr.append(under)
    r.append(pr);t=OxmlElement('w:t');t.set(qn('xml:space'),'preserve');t.text=label;r.append(t);e.append(r);p._p.append(e)

def after_heading(anchor,title):
    p=doc.add_paragraph(title,'Heading 1');anchor.addnext(p._p);return p

text(paras[0],'North Sea model validation draft')
for break_paragraph,heading_paragraph in [(paras[1],paras[2]),(paras[17],paras[18])]:
    break_paragraph._p.getparent().remove(break_paragraph._p)
    heading_paragraph.paragraph_format.page_break_before=True
entries=content['fields']
for row in tables[0].rows[1:]:
    label=row.cells[0].text
    if label in entries:cell(row.cells[1],entries[label])
    for label_text,target in content.get('field_links',{}).get(label,[]):
        p=row.cells[1].add_paragraph();link(p,label_text,target)

# The source layout stays intact; the requested candidate comparison adds a
# compact source-styled section before the original coverage section.
heading=after_heading(tables[0]._tbl,'Comparison of the two candidates')
p=doc.add_paragraph(content['recommendation']);heading._p.addnext(p._p)
comparison=deepcopy(tables[2]._tbl)
p._p.addnext(comparison)
from docx.table import Table
ct=Table(comparison,doc._body)
prototype=deepcopy(ct.rows[1]._tr)
for i,value in enumerate(['Assessment','ICES North Sea 1991','East Coast Scotland 1991–1995']):cell(ct.rows[0].cells[i],value)
for row in list(ct.rows)[1:]:ct._tbl.remove(row._tr)
for values in content['comparison_rows']:
    ct._tbl.append(deepcopy(prototype))
    cells=ct.rows[-1].cells
    for c,value in zip(cells,values):cell(c,value)
for col,width in zip(ct.columns,[1.35,2.8,2.8]):col.width=Inches(width)
for row in ct.rows:
    row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for c,width in zip(row.cells,[1.35,2.8,2.8]):c.width=Inches(width)
p=doc.add_paragraph(content['comparison_note']);ct._tbl.addnext(p._p)
for label,target in content.get('comparison_links',[]):
    p.add_run(' ');link(p,label,target)

text(paras[3],'Reference: 2019 total catch (landings plus discards); all recorded catch labels, including zero-catch labels.')
text(paras[4],f"{audit['source_group_count']} source ecological groups; {audit['totals']['taxa']} catch taxa. A synthetic import group is separate from the source inventory.")
text(paras[5],f"Simple-chain PPR totals {audit['totals']['known_simple_chain_ppr_tC']:,.0f} t C in 2019.")
text(paras[6],'All 72 labels with missing TL/coefficient have zero recorded catch and contribute zero annual PPR. The 2019 total is complete; their coefficients remain unknown.')
text(paras[7],'Method: simple trophic chain.')
text(paras[8],'Excel taxon appendix and descriptive Sources sheet: ')
link(paras[8],'All 384 taxa and source references',(BASE/'taxon_mapping.xlsx').relative_to(ROOT).as_posix())
text(paras[9],'Overall confidence uses the weaker required membership or allocation component.')
for row, data in zip(tables[1].rows[1:],audit['confidence_summary']):
    vals=[data['confidence'],str(data['taxa']),format_percent(data['catch_percentage']),format_percent(data['ppr_percentage'])]
    for c,v in zip(row.cells,vals):cell(c,v)
for tbl,key in [(tables[2],'membership_rules'),(tables[3],'allocation_rules')]:
    prototype=deepcopy(tbl.rows[1]._tr)
    for row in list(tbl.rows)[1:]:tbl._tbl.remove(row._tr)
    for r in audit[key]:
        tbl._tbl.append(deepcopy(prototype))
        cells=tbl.rows[-1].cells
        for c,v in zip(cells,[r['rule'],r['confidence'],format_percent(r['ppr_percentage'])]):cell(c,v)
text(paras[11],'Membership evidence: the source has 69 groups but no retained catch-taxon crosswalk. Exact-model assignments remain unassessed.')
link(paras[11],' Source group inventory','regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991/model.json')
text(paras[13],'Weights and assumptions: no exact-model allocations are retained. The Scotland mappings cannot be transferred without a group-definition crosswalk and separate weight evidence.')
text(paras[14],'Each percentage is the independent simple-chain PPR associated with taxa using that rule.')
text(paras[15],'Unresolved: all 384 taxa, individually named in the linked appendix, because no selected-model assignment or allocation is retained. This is an evidence gap, not a finding that biological mapping is impossible. No Very low decisions have been assessed or adopted.')
paras[16]._p.getparent().remove(paras[16]._p)
tables[4]._tbl.getparent().remove(tables[4]._tbl)

text(paras[18],'Geographic evidence')
text(paras[19],content['geography_intro'])
text(paras[20],'Region and study domain')
cell(tables[5].cell(0,0),'North Sea LME and reconstructed ICES divisions IVa–IVc')
cell(tables[5].cell(1,0),'')
tables[5].cell(1,0).paragraphs[0].add_run().add_picture(str(ROOT/content['map_image']),width=Inches(6.65))
text(paras[21],content['map_caption'])
link(paras[21],' Boundary analysis',(BASE/'evidence/geography/geographic_assessment.json').relative_to(ROOT).as_posix())
text(paras[22],'Study domain in the source report')
paras[22].paragraph_format.page_break_before=True
cell(tables[6].cell(0,0),'ICES WGSAM report Annex 6 area statement')
cell(tables[6].cell(1,0),'')
tables[6].cell(1,0).paragraphs[0].add_run().add_picture(str(ROOT/content['source_image']),width=Inches(6.5))
text(paras[23],content['source_caption'])
link(paras[23],' ICES report (PDF page 104)','regions/LME/LME_022/papers/ICES-WGSAM-2015/sources/ICES_WGSAM_2015.pdf#page=104')
text(paras[24],content['geography_limit'])

# Keep headings with their following content and repeat every table header.
for table in doc.tables:
    trpr=table.rows[0]._tr.get_or_add_trPr()
    if trpr.find(qn('w:tblHeader')) is None:trpr.append(OxmlElement('w:tblHeader'))
    for row in table.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs:
                    if r.font.size is None:r.font.size=Pt(10)

staged=RUN/'outputs/validation.docx'
doc.save(staged)
# Preserve opaque/template-only package parts exactly; only authored document,
# relationships, images and content types may differ.
with zipfile.ZipFile(TEMPLATE) as z: original={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
with zipfile.ZipFile(staged) as z: authored={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
editable={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml'}
final=BASE/'validation.docx'
with zipfile.ZipFile(final,'w') as out:
    for name,(info,data) in authored.items():
        if name in original and name not in editable and not name.startswith('word/media/'):
            info,data=original[name]
        out.writestr(info,data)
verify_report(final)
print(final)
