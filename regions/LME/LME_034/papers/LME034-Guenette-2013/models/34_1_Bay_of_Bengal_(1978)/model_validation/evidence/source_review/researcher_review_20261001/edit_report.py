"""Narrow authorized replacements, with reversible byte-level scope proof."""
import copy, hashlib, json, os, re, tempfile, zipfile
from pathlib import Path
from lxml import etree as E
from openpyxl import load_workbook

QA = Path(__file__).resolve().parent
ROOT = next(p for p in QA.parents if (p/'Project.xlsx').exists())
REPORT = next((ROOT/'regions/LME_034').glob('Model_validation*.docx'))
BASELINE = QA/('baseline_'+REPORT.name)
REFERENCE = next((ROOT/'regions/LME_032').glob('Model_validation*.docx'))
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
text = lambda e: ''.join(t.text or '' for t in e.iter(W+'t'))
sha = lambda b: hashlib.sha256(b).hexdigest()

decisions = [
 ('Marine fishes not identified', 'Unknown bony-fish composition is approximated by all 23 compatible named and residual fish pools. Separately reported tunas and billfishes do not establish their absence from unidentified catches. Source-zero S bathy remains eligible; Maldives shelf-fish pools are excluded without excluding region 1 open water. Whole-guild 1978 catches proxy unknown constituent fractions, assumed transferable across years, fisheries and catch bases.'),
 ('Perciformes', 'The provider label is interpreted as a historical fisheries reporting concept with unknown composition. Compatible piscivore, invertebrate-feeder, carangid and small-pelagic guilds are retained; source-listed Lactarius and Atropus support the small-pelagic candidates. Eligible guilds also contain other orders, so their whole catches approximate the reporting mixture. Pooled 1978 catch proportions are assumed transferable across years and catch bases.'),
 ('Marine pelagic fishes not identified', 'Unknown pelagic bony-fish composition is approximated by 21 compatible named and residual pools, including tunas, billfishes and source-zero S bathy. Predominantly reef/demersal commercial piscivores are excluded. Maldives shelf-fish pools are excluded without excluding region 1 open water. Whole-guild 1978 catches proxy unknown constituent fractions, assumed transferable across years, fisheries and catch bases.'),
 ('Scombroidei', 'The provider common name and commercial class support a tunas, bonitos and billfishes reporting scope. Tuna-like, Coastal scombrids, Bigeye tuna, Yellowfin tuna and Marlins approximate the unknown mixture. Indian mackerel is excluded under the commercial-category assumption; shelf demersal pools are excluded. Pooled 1978 source-model catch proportions supply an assumed split across years and catch bases.'),
 ('Malacostraca', 'The provider common name includes lobsters, crabs, shrimps and krill. Crustaceans, Macrobenthos and all three Zooplankton pools approximate that broad mixture, consistent with the source-listed small benthic crustaceans and euphausiids. Zooplankton candidates retain genuine zero catch and zero weight; region 1 open water remains eligible. Pooled 1978 catches supply an assumed split across years and catch bases.')]

book = load_workbook(ROOT/'regions/LME_034/LME034_taxon_mapping_appendix.xlsx',read_only=True,data_only=True)
very_low = {r[0]:r[6] for r in book['Taxon mapping'].values if len(r)>6 and r[5]=='Very low'}
book.close()
assert len(decisions)==5 and set(dict(decisions))==set(very_low)
with zipfile.ZipFile(REFERENCE) as z:
    ns = list(E.fromstring(z.read('word/document.xml')).find(W+'body'))
    i = next(i for i,n in enumerate(ns) if n.tag==W+'p' and text(n)=='Very low decisions')
    heading, table = copy.deepcopy(ns[i]), copy.deepcopy(ns[i+1])
row_template = copy.deepcopy(table.findall(W+'tr')[1])
for row in table.findall(W+'tr')[1:]: table.remove(row)
for taxon, reason in decisions:
    row = copy.deepcopy(row_template)
    for cell, value in zip(row.findall(W+'tc'), [taxon, reason]):
        p = cell.find(W+'p'); ppr = copy.deepcopy(p.find(W+'pPr')); rpr = copy.deepcopy(p.find(W+'r/'+W+'rPr'))
        for child in list(cell):
            if child.tag != W+'tcPr': cell.remove(child)
        p = E.SubElement(cell,W+'p'); p.append(ppr)
        r = E.SubElement(p,W+'r'); r.append(rpr); E.SubElement(r,W+'t').text=value
    table.append(row)
fragment = E.tostring(heading)+E.tostring(table)
QA.mkdir(parents=True,exist_ok=True)
if not BASELINE.exists(): BASELINE.write_bytes(REPORT.read_bytes())
assert REPORT.read_bytes()==BASELINE.read_bytes(), 'Report changed since source snapshot'
with zipfile.ZipFile(BASELINE) as z: parts = [(info,z.read(info.filename)) for info in z.infolist()]
original = dict((i.filename,b) for i,b in parts)['word/document.xml']

# Find only the one top-level Very low explanatory paragraph.
anchor = original.index(b'No unresolved mappings remain. Very low assignments')
start = list(re.finditer(rb'<w:p(?:\s|>)',original[:anchor]))[-1].start()
end = original.index(b'</w:p>',anchor)+len(b'</w:p>')
replacements = [(start,end,fragment, 'Very low paragraph')]
diagnostic_changes = {}
for label,rho,b,det in [('GE', '0.59','0.17','1.31'),('TE','0.63','0 (structural convention)','0.80')]:
    pos = original.index(f'<w:t>{label} diagnostics</w:t>'.encode())
    row_start = list(re.finditer(rb'<w:tr(?:\s|>)', original[:pos]))[-1].start()
    row_end = original.index(b'</w:tr>',pos)+len(b'</w:tr>')
    old = original[row_start:row_end]
    substitutions = [(b'WARN: High recycling in living compartments (',b'OK: Recycling in living compartments ('),
                     (b'&gt;0.7).', b'&lt;0.7).'),
                     (b' = 0.74' if label=='GE' else b' = 0.78', f' = {rho}'.encode()),
                     (b'b = 0.31 ',f'b = {b} '.encode()) if label=='GE' else (b'b = 0.31.', f'b = {b}.'.encode())]
    if label=='GE': substitutions.append((b'Detritus (49) SPPR = 1.68',b'Detritus (49) SPPR = 1.31'))
    new = old
    for a,z in substitutions:
        assert new.count(a)==1, (label,a)
        new=new.replace(a,z,1)
    old_tree,new_tree=E.fromstring(b'<root xmlns:w="'+W[1:-1].encode()+b'" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">'+old+b'</root>'),E.fromstring(b'<root xmlns:w="'+W[1:-1].encode()+b'" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">'+new+b'</root>')
    # Formatting, paragraph structure, breaks and run properties are invariant.
    for tree in [old_tree,new_tree]:
        for t in tree.iter(W+'t'): t.text=''
    assert E.tostring(old_tree)==E.tostring(new_tree)
    replacements.append((row_start,row_end,new,label+' diagnostic values'))
    diagnostic_changes[label]={'rho_living':rho,'b':b,'detritus_sppr':det,'paragraphs_and_breaks_preserved':True,'substitutions':[(a.decode(),z.decode()) for a,z in substitutions]}
patched=original
for a,z,new,label in sorted(replacements,reverse=True): patched=patched[:a]+new+patched[z:]
E.fromstring(patched)
recovered=patched
offset=0
for a,z,new,label in sorted(replacements):
    loc=a+offset
    assert patched[loc:loc+len(new)]==new
    offset+=len(new)-(z-a)
# Prove every byte outside the three authorized replacement spans is unchanged.
recovered=patched
for a,z,new,label in sorted(replacements,reverse=True):
    prior_shift=sum(len(n)-(q-p) for p,q,n,l in replacements if p<a)
    loc=a+prior_shift
    recovered=recovered[:loc]+original[a:z]+recovered[loc+len(new):]
assert recovered==original
fd,tmp=tempfile.mkstemp(suffix='.docx',dir=REPORT.parent); os.close(fd)
try:
    with zipfile.ZipFile(tmp,'w') as z:
        for info,data in parts: z.writestr(info,patched if info.filename=='word/document.xml' else data)
    os.replace(tmp,REPORT)
finally:
    if os.path.exists(tmp): os.unlink(tmp)
with zipfile.ZipFile(REPORT) as z: changed=[info.filename for info,data in parts if z.read(info.filename)!=data]
assert changed==['word/document.xml']
proof={'baseline_sha256':sha(BASELINE.read_bytes()),'report_sha256':sha(REPORT.read_bytes()),'changed_zip_parts':changed,
 'original_xml_restored_by_reversing_only_authorized_replacements':True,'all_other_report_content_byte_identical':True,
 'very_low_taxa_count':5,'very_low_decision_rows':5,'diagnostic_changes':diagnostic_changes,
 'rows':[{'taxon':t,'reason':r,'appendix_reason':very_low[t]} for t,r in decisions],
 'authorized_spans':[{'label':l,'start':a,'end':z,'new_bytes':len(n)} for a,z,n,l in sorted(replacements)]}
(QA/'word_preservation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:proof[k] for k in ['report_sha256','changed_zip_parts','very_low_taxa_count','original_xml_restored_by_reversing_only_authorized_replacements']},indent=2))
