"""Narrow OOXML update of this review's existing report; preserve manual content."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, zipfile, sys
from lxml import etree as E

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN = Path(__file__).resolve().parents[1]
BASE = RUN.parents[1]
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W = '{'+NS['w']+'}'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = RUN/'inputs/validation.docx'
final = BASE/'validation.docx'
content = json.loads((RUN/'inputs/report_update.json').read_text(encoding='utf-8'))
prior_proof = RUN/'qa/report_patch_verification.json'
allowed = {sha(source)}
if prior_proof.exists():allowed.add(json.loads(prior_proof.read_text())['after_sha256'])
assert sha(final) in allowed, 'Report changed since our last edit; preserve researcher edits.'
with zipfile.ZipFile(source) as z:
    parts = {i.filename:(i,z.read(i.filename)) for i in z.infolist()}
xml = E.fromstring(parts['word/document.xml'][1])
rels = E.fromstring(parts['word/_rels/document.xml.rels'][1])
body = xml.find(W+'body')
def txt(node): return ''.join(node.xpath('.//w:t/text()',namespaces=NS))
def paragraph(proto, value):
    p=deepcopy(proto)
    for node in list(p):
        if node.tag != W+'pPr': p.remove(node)
    r=E.SubElement(p,W+'r')
    old=proto.find('./'+W+'r/'+W+'rPr')
    if old is not None:r.append(deepcopy(old))
    t=E.SubElement(r,W+'t');t.text=value
    t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    return p
first = body.find(W+'tbl')
fields = {txt(row.findall(W+'tc')[0]): row.findall(W+'tc')[1]
          for row in first.findall(W+'tr')[1:]}
manual = ['Selection rationale','SPPR calculation','Open issues and next action','Review and reproducibility']
preserved = {key:E.tostring(fields[key]) for key in manual}
for key,value in content['fields'].items():
    assert key not in manual
    cell=fields[key]
    old=cell.findall(W+'p')
    links=[deepcopy(p) for p in old if p.find('.//'+W+'hyperlink') is not None]
    for p in old:cell.remove(p)
    for line in value.split('\n'):cell.append(paragraph(old[0],line))
    cell.extend(links)
heading=next(p for p in body.findall(W+'p') if txt(p)=='Comparison of the two candidates')
recommendation=heading.getnext()
body.replace(recommendation,paragraph(recommendation,content['recommendation']))
comparison=heading.getnext().getnext()
for p in comparison.findall(W+'tr')[0].xpath('.//w:p',namespaces=NS):
    ppr=p.find(W+'pPr')
    if ppr is None:ppr=E.Element(W+'pPr');p.insert(0,ppr)
    keep=ppr.find(W+'keepNext')
    if keep is None:keep=E.SubElement(ppr,W+'keepNext')
    keep.set(W+'val','1')
rows=comparison.findall(W+'tr')[1:]
assert len(rows)==len(content['comparison_rows'])
for row,values in zip(rows,content['comparison_rows']):
    for cell,value in zip(row.findall(W+'tc'),values):
        old=cell.findall(W+'p')
        for p in old:cell.remove(p)
        cell.append(paragraph(old[0],value))
note=comparison.getnext()
replacement=paragraph(note,content['comparison_note'])
for link in note.findall(W+'hyperlink'):
    r=E.SubElement(replacement,W+'r');t=E.SubElement(r,W+'t')
    t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=' '
    replacement.append(deepcopy(link))
body.replace(note,replacement)
for rel in rels:
    target=rel.get('Target','')
    if '2026-11-14_validation/structural_zero/report_ready.json' in target:
        rel.set('Target',target.replace('2026-11-14_validation/structural_zero/report_ready.json','2026-11-14_loader_repair/report_ready.json'))
    if target.endswith('source_review/candidate_review.json'):
        rel.set('Target',target.replace('candidate_review.json','candidate_review_loader_repair.json'))
for h in fields['GE diagnostics'].xpath('.//w:hyperlink',namespaces=NS):
    if 'negative source' in txt(h):
        textnodes=h.xpath('.//w:t',namespaces=NS)
        textnodes[0].text='Three-method diagnostics in the appendix'
        for node in textnodes[1:]:node.text=''
assert all(E.tostring(fields[key])==before for key,before in preserved.items())
updated={'word/document.xml':E.tostring(xml,xml_declaration=True,encoding='UTF-8',standalone=True),
         'word/_rels/document.xml.rels':E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
with zipfile.ZipFile(final,'w') as out:
    for name,(info,data) in parts.items():out.writestr(info,updated.get(name,data))
verify_report(final)
with zipfile.ZipFile(final) as z:
    assert all(z.read(name)==data for name,(_,data) in parts.items() if name not in updated)
proof={'before_sha256':sha(source),'after_sha256':sha(final),'changed_parts':list(updated),
       'manual_cells_unchanged':manual,'other_package_parts_identical':True,
       'updated_fields':list(content['fields']),'percentage_format_passed':True}
(RUN/'qa/report_patch_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print(json.dumps(proof,indent=2))
