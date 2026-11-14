"""Targeted OOXML update of user-authorized LME014 review; no scientific writes."""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import hashlib,json
from lxml import etree as E

WORK=Path(__file__).resolve().parents[1]
MODEL=WORK.parents[2]
FINAL=MODEL/'model_validation/validation.docx'
SOURCE=WORK/'inputs/validation_before.docx'
OUT=WORK/'outputs/validation.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'w':W,'r':R}
def text(el):return ''.join(el.xpath('.//w:t/text()',namespaces=NS))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tag(n):return '{'+W+'}'+n
assert sha(SOURCE)==sha(FINAL),'Researcher original changed since inventory.'
with ZipFile(SOURCE) as z: parts={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
doc=E.fromstring(parts['word/document.xml']);original=deepcopy(doc)
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
cells={text(cs[0]):cs[1] for row in doc.xpath('//w:body/w:tbl[1]/w:tr',namespaces=NS)
       if len(cs:=row.findall(tag('tc')))>=2}
allowed=['Selection rationale','Model extraction','GE diagnostics','TE diagnostics','SPPR calculation','Other','Open issues and next action','Review and reproducibility']
old_cells={k:E.tostring(cells[k]) for k in allowed}
def relation(target):
    for r in rels:
        if r.get('Target')==target:return r.get('Id')
    ids={r.get('Id') for r in rels};n=1
    while 'rId'+str(n) in ids:n+=1
    rid='rId'+str(n)
    E.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=R+'/hyperlink',Target=target,TargetMode='External')
    return rid
def paragraph(cell,body,bold=False):
    p=E.Element(tag('p'))
    template=cell.find(tag('p'))
    if template is not None and template.find(tag('pPr')) is not None:p.append(deepcopy(template.find(tag('pPr'))))
    if isinstance(body,str):body=[body]
    for item in body:
        parent=p
        if isinstance(item,tuple):
            label,target=item
            parent=E.SubElement(p,tag('hyperlink'),{'{'+R+'}id':relation(target)})
            content=label
        else:content=item
        run=E.SubElement(parent,tag('r'));rp=E.SubElement(run,tag('rPr'))
        template_r=cell.find('.//'+tag('rPr'))
        if template_r is not None:
            for child in template_r:
                if E.QName(child).localname not in ['color','u','b','i']:rp.append(deepcopy(child))
        if bold:E.SubElement(rp,tag('b'))
        if isinstance(item,tuple):
            E.SubElement(rp,tag('color'),{tag('val'):'0563C1'})
            E.SubElement(rp,tag('u'),{tag('val'):'single'})
        else:E.SubElement(rp,tag('color'),{tag('val'):'000000'})
        t=E.SubElement(run,tag('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=content
    return p
def replace(label,items):
    cell=cells[label]
    paragraphs=[paragraph(cell,item,bold=(label=='Review and reproducibility' and item=='MODEL VALIDATED')) for item in items]
    for child in list(cell):
        if child.tag!=tag('tcPr'):cell.remove(child)
    cell.extend(paragraphs)

# Preserve the researcher's article rationale exactly; update only the chosen-run explanation.
rationale=cells['Selection rationale']
paras=rationale.findall(tag('p'))
assert len(paras)==2 and text(paras[0])=='Article: ?'
new_model=paragraph(rationale,'Model: Source-reconciled native 2020 reconstruction with separate Discards and Detritus pools and EE floor ON at 0.1. GE and TE remain WARN because the Discards supply is unresolved; both strict balance checks pass. The physical merge is retained as sensitivity only.')
rationale.replace(paras[1],new_model)
replace('Model extraction',[
    'The native 36-group reconstruction retains the audited completion of source-missing B and EE. Verified fishery returns total 0.005859525 t/km²/year and enter Detritus (36), not Discards (35). The original native model already carries the Discards deficit as negative calculated Export; conversion omitted that field and reconstruction expresses the deficit as negative accumulation.',
    [('Source/runtime review','evidence/source_review/source_review.md'),' | ',('Discards reconciliation','evidence/discards_reconciliation_20261114/discards_reconciliation.md'),' | ',('Model notes','../model_notes.md')]])
replace('GE diagnostics',[
    'WARN: Discards (35) retains an unexplained negative stock residual of −0.207504 t/km²/year.',
    'No negative SPPR across basal-source columns; all 185 entries are finite, including unfished groups.',
    'rho_living = 0.281907; b = 0.038859. Discards (35): SPPR = 0; Detritus (36): SPPR = 1.091559.',
    ['Strict balance passes (relative gap 3.51 × 10⁻¹⁶). ',('Full GE diagnostic','evidence/discards_reconciliation_20261114/outputs/diagnostics/source_exact_returns_to_36/GE_full_return.json')]])
replace('TE diagnostics',[
    'WARN: Discards (35) retains the same unexplained negative stock residual.',
    'No negative SPPR across basal-source columns; all 185 entries are finite, including unfished groups.',
    'rho_living = 0.309794; b = 0.001467. Discards (35): SPPR = 0; Detritus (36): SPPR = 0.941069.',
    ['Strict balance passes (reported relative gap 0). No zero-EE or near-zero-TE flags. ',('Full TE diagnostic','evidence/discards_reconciliation_20261114/outputs/diagnostics/source_exact_returns_to_36/TE_full_return.json')]])
replace('SPPR calculation',[
    'Selected run: separate Discards (35) and Detritus (36); EE floor ON at 0.1, with selection threshold 0.1. Verified fishery returns enter Detritus (36) once. No detritus pooling or external-source dilution is applied.',
    ['The physical merge remains a sensitivity scenario only: source-model catch PPR increases by 0.018% (GE) and 0.0069% (TE), with OK diagnostics under complete mixing. ',('Physical-merge sensitivity','evidence/physical_detritus_merge_20261114/physical_detritus_merge.md')],
    'No groups were removed from the calculation.'])
replace('Other',[
    'The EE floor affects eight groups and directs 65.52 model flow units to a hypothetical external nonfishery mortality sink, principally from Kelp. Living biological flows and catch are preserved.',
    'The native Detritus calculated EE is 0.04784, which rounds to the paper’s 0.05; its stored input EE of zero is not a source disagreement. Sharks (27) retains the largest TE coefficient, 399,525.33.'
])
replace('Open issues and next action',[
    'Clarify the intended Discards inflow and any processing-offal supply. Retain the separate-pool warning and use the physical merge only to assess sensitivity; mixing does not establish the missing source-specific supply.'
])
replace('Review and reproducibility',[
    'Researcher name: Ido Carmel | review date: 14/11/2026','', 'MODEL VALIDATED'])

def outside_allowed(tree):
    copy=deepcopy(tree)
    for row in copy.xpath('//w:body/w:tbl[1]/w:tr',namespaces=NS):
        cs=row.findall(tag('tc'))
        if len(cs)>=2 and text(cs[0]) in allowed:
            c=cs[1]
            for child in list(c):
                if child.tag!=tag('tcPr'):c.remove(child)
    return E.tostring(copy)
assert outside_allowed(doc)==outside_allowed(original),'Unexpected OOXML change outside authorized cells.'
parts['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/_rels/document.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(OUT,'w') as z:
    for info in infos:z.writestr(info,parts[info.filename])
with ZipFile(SOURCE) as a,ZipFile(OUT) as b:
    changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
assert set(changed)<= {'word/document.xml','word/_rels/document.xml.rels'}
qa={'source_sha256':sha(SOURCE),'output_sha256':sha(OUT),'changed_parts':changed,'allowed_entry_cells':allowed,
    'all_other_document_XML_exact':True,'all_other_package_parts_exact':True,'article_rationale_preserved':True,
    'signature_authorization':'Explicit user instruction in this chat: sign validated, Ido Carmel, 14/11/2026.',
    'primary_scenario':'source_exact_returns_to_36; use_ee_floor=True; ee_floor=0.1; ee_threshold=0.1; det_collapse_mode=never; det_open_mode=none',
    'sensitivity_only':'physical_detritus_merge_20261114','excluded_group_seq':[],
    'review_fields':{k:[text(p) for p in cells[k].findall(tag('p'))] for k in allowed}}
(WORK/'qa/document_patch.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
(WORK/'qa/artifact.md').write_text('Reference: existing LME014 validation.docx, SHA256 '+sha(SOURCE)+'\nFormat reference: Validate LME037 uses the LME036 compact diagnostic paragraphs, Removed groups from calculation list, researcher/date line and MODEL VALIDATED marker.\nAll sections, page geometry, styles, images, coverage tables, mapping rationale, relationships and unrelated manual content remain source-derived. Authorized edit slots: '+', '.join(allowed)+'.\nOnly document.xml entry fragments and added hyperlink relationships may change.\n',encoding='utf-8')
print(json.dumps({'staged_docx':str(OUT),'changed_parts':changed,'unrelated_XML_preserved':True}))
