"""Patch only authorized report XML, consuming the single mapping handoff."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,zipfile,sys
from lxml import etree as E

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN=Path(__file__).resolve().parents[1]
BASE=RUN.parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report,format_percent
from tools.project_core.validation.researcher_review import read_report
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W='{'+NS['w']+'}'
R='{'+NS['r']+'}'
P='{http://schemas.openxmlformats.org/package/2006/relationships}'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(n): return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
source=RUN/'inputs/validation_before.docx'
final=BASE/'validation_review.docx'
config=json.loads((RUN/'inputs/report_narrative.json').read_text(encoding='utf8'))
mapping=json.loads((RUN/'outputs/report_mapping_content.json').read_text(encoding='utf8'))
proof_path=RUN/'qa/report_patch_verification.json'
allowed={sha(source)}
if proof_path.exists(): allowed.add(json.loads(proof_path.read_text(encoding='utf8'))['after_sha256'])
assert sha(BASE/'validation.docx')==sha(source),'Concurrent original report change detected'
if final.exists():assert sha(final) in allowed,'Concurrent review-copy change detected'
with zipfile.ZipFile(source) as z: parts={i.filename:(i,z.read(i)) for i in z.infolist()}
doc=E.fromstring(parts['word/document.xml'][1])
rels=E.fromstring(parts['word/_rels/document.xml.rels'][1])
body=doc.find(W+'body')
before_children=list(body)
first=body.find(W+'tbl')
fields={txt(r.findall(W+'tc')[0]):r.findall(W+'tc')[1] for r in first.findall(W+'tr')[1:]}
manual=['Selection rationale','SPPR calculation','Open issues and next action','Review and reproducibility']
preserved={k:E.tostring(fields[k]) for k in manual}

def paragraph(proto,value,links=False):
    p=deepcopy(proto)
    for node in list(p):
        if node.tag!=W+'pPr': p.remove(node)
    r=E.SubElement(p,W+'r')
    old=proto.find('./'+W+'r/'+W+'rPr')
    if old is not None: r.append(deepcopy(old))
    t=E.SubElement(r,W+'t');t.text=value;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    if links:
        for link in proto.findall(W+'hyperlink'):
            rr=E.SubElement(p,W+'r');tt=E.SubElement(rr,W+'t');tt.text=' ';tt.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
            p.append(deepcopy(link))
    return p
def set_cell(cell,lines,preserve_links=False):
    old=cell.findall(W+'p')
    links=[deepcopy(p) for p in old if p.find('.//'+W+'hyperlink') is not None] if preserve_links else []
    for p in old:cell.remove(p)
    for value in lines if isinstance(lines,list) else lines.split('\n'):cell.append(paragraph(old[0],value))
    cell.extend(links)
def replace_para(old,value,links=False):
    new=paragraph(old,value,links);body.replace(old,new);return new
def para(value): return next(p for p in body.findall(W+'p') if txt(p)==value)
def add_link(p,label,target):
    ids={r.get('Id') for r in rels}
    index=1
    while 'rId'+str(index) in ids:index+=1
    rid='rId'+str(index)
    E.SubElement(rels,P+'Relationship',Id=rid,Type=NS['r']+'/hyperlink',Target=target,TargetMode='External')
    rr=E.SubElement(p,W+'r');tt=E.SubElement(rr,W+'t');tt.text=' ';tt.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    h=E.SubElement(p,W+'hyperlink');h.set(R+'id',rid)
    r=E.SubElement(h,W+'r');t=E.SubElement(r,W+'t');t.text=label
def set_rows(table,rows):
    old=table.findall(W+'tr')
    proto=deepcopy(old[1])
    for r in old[1:]:table.remove(r)
    for values in rows:
        row=deepcopy(proto)
        for cell,value in zip(row.findall(W+'tc'),values):set_cell(cell,str(value))
        # Keep each decision/rule together, without linking the entire table.
        prop=row.find(W+'trPr')
        if prop is None:prop=E.Element(W+'trPr');row.insert(0,prop)
        if prop.find(W+'cantSplit') is None:E.SubElement(prop,W+'cantSplit')
        for p in row.xpath('.//w:p',namespaces=NS):
            pp=p.find(W+'pPr')
            if pp is not None:
                for keep in pp.findall(W+'keepNext'):pp.remove(keep)
        table.append(row)
    hp=old[0].find(W+'trPr')
    if hp is None:hp=E.Element(W+'trPr');old[0].insert(0,hp)
    if hp.find(W+'tblHeader') is None:E.SubElement(hp,W+'tblHeader')

replace_para(body.findall(W+'p')[0],config['title'])
for key,value in config['fields'].items():set_cell(fields[key],value,True)
comparison_heading=para('Comparison of the two candidates')
replace_para(comparison_heading.getnext(),config['comparison_intro'])
comparison_table=comparison_heading.getnext().getnext()
comparison_rows=config['comparison_rows']
comparison_rows[4][1]=mapping['comparison_mapping']
set_rows(comparison_table,comparison_rows)
replace_para(comparison_table.getnext(),config['comparison_note'],True)

heading=para('Taxon mapping and coverage')
old_reference=heading.getnext()
new_reference=replace_para(old_reference,mapping['reference'])
# This precise label distinguishes proposals from adopted regional confidence.
body.insert(body.index(new_reference),paragraph(new_reference,config['proposal_label']))
confidence=next(t for t in body.findall(W+'tbl') if txt(t.findall(W+'tr')[0].findall(W+'tc')[0])=='Overall confidence')
set_rows(confidence,mapping['confidence_rows'])
member_heading=para('Group assignment rules')
member_table=member_heading.getnext()
set_rows(member_table,mapping['membership_rule_rows'])
membership_para=replace_para(member_table.getnext(),mapping['membership_evidence'],True)
add_link(membership_para,'Mapping decisions and evidence',mapping['mapping_evidence_target'])
add_link(membership_para,'Descriptive Sources sheet',"taxon_mapping.xlsx#'Sources'!A1")
mpp=membership_para.find(W+'pPr')
if mpp is None:mpp=E.Element(W+'pPr');membership_para.insert(0,mpp)
if mpp.find(W+'keepLines') is None:E.SubElement(mpp,W+'keepLines')
weight_heading=para('Allocation weight rules')
weight_table=weight_heading.getnext()
set_rows(weight_table,mapping['allocation_rule_rows'])
replace_para(weight_table.getnext(),mapping['allocation_evidence'])
uncertainty=next(p for p in body.findall(W+'p') if txt(p).startswith('Unresolved: all 384 taxa'))
uncertainty=replace_para(uncertainty,mapping['uncertainty'])
if mapping['very_low_rows']:
    with zipfile.ZipFile(RUN/'inputs/template_reference.docx') as z:template=E.fromstring(z.read('word/document.xml'))
    vb=template.find(W+'body')
    vh=next(p for p in vb.findall(W+'p') if txt(p)=='Very low decisions')
    table=deepcopy(vh.getnext())
    set_rows(table,mapping['very_low_rows'])
    for p in table.xpath('.//w:tr[position()>1]/w:tc/w:p',namespaces=NS):
        pp=p.find(W+'pPr')
        if pp is None:pp=E.Element(W+'pPr');p.insert(0,pp)
        spacing=pp.find(W+'spacing')
        if spacing is None:spacing=E.SubElement(pp,W+'spacing')
        spacing.set(W+'after','0')
    pos=body.index(uncertainty)+1
    body.insert(pos,deepcopy(vh));body.insert(pos+1,table)

# Preserve existing link labels and anchors, while directing obsolete comparison
# evidence to this review's current diagnostic/comparison record.
for rel in rels:
    target=rel.get('Target','')
    if target.endswith('source_review/candidate_review_loader_repair.json'):
        rel.set('Target','evidence/source_review/validation_comparison_20261114.json')
    if target.endswith('source_review/mapping_audit.json'):
        rel.set('Target',mapping['mapping_evidence_target'])
for h in doc.xpath('.//w:hyperlink',namespaces=NS):
    for r in h.findall(W+'r'):
        pr=r.find(W+'rPr')
        if pr is None:pr=E.Element(W+'rPr');r.insert(0,pr)
        color=pr.find(W+'color')
        if color is None:color=E.SubElement(pr,W+'color')
        color.set(W+'val','0563C1')
        under=pr.find(W+'u')
        if under is None:under=E.SubElement(pr,W+'u')
        under.set(W+'val','single')

assert all(E.tostring(fields[k])==b for k,b in preserved.items()),'Manual XML changed'
updated={'word/document.xml':E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True),'word/_rels/document.xml.rels':E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
with zipfile.ZipFile(final,'w') as out:
    for name,(info,data) in parts.items():out.writestr(info,updated.get(name,data))
verify_report(final)
with zipfile.ZipFile(final) as z:assert all(z.read(n)==d for n,(_,d) in parts.items() if n not in updated)
try:read_report(ROOT,final,BASE.parent.name);raise AssertionError('Unexpected signed report')
except ValueError as exc:
    parser=str(exc)
    assert parser=='The report needs an explicit researcher identity, date and one unambiguous decision'
proof={'before_sha256':sha(source),'after_sha256':sha(final),'changed_parts':list(updated),'manual_cells_unchanged':manual,'other_package_parts_identical':True,'updated_fields':list(config['fields']),'percentage_format_passed':True,'parser_unsigned_before_after':parser,'source_template_unchanged':sha(ROOT/'tools/templates/validation.docx')==sha(RUN/'inputs/template_reference.docx')}
proof_path.write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(proof,indent=2))
