from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from lxml import etree as E
import hashlib, json, sys

RUN = Path(__file__).resolve().parents[1]
V = RUN.parents[1]
ROOT = next(p for p in V.parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.validation_percentage_format import format_percent, verify_report

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'w': W, 'r': R}
q = lambda n: '{' + W + '}' + n
tx = lambda e: ''.join(e.xpath('.//w:t/text()', namespaces=NS))
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
m = read(RUN / 'outputs/mapping_review.json')
vl_input = read(RUN / 'outputs/very_low_table.json')
vl = vl_input if isinstance(vl_input, list) else vl_input['rows']
diag_dir = V.parent / 'results/diagnostics/validation_20261114'
d = read(diag_dir / 'direct_reports.json')
assert [d[k]['status'] for k in ['GE', 'TE', 'With Egestion']] == ['OK', 'WARN', 'OK']
assert m['taxa'] == 181 and not m['discrepancy_ledger']
expected_vl = {x['taxon'] for x in m['very_low_decisions']}
all_vl = [t for row in vl for t in row['taxa']]
assert len(all_vl) == len(set(all_vl)) == 36 and set(all_vl) == expected_vl

before = RUN / 'inputs/validation_before.docx'
with ZipFile(before) as z:
    parts = [(i, z.read(i.filename)) for i in z.infolist()]
partmap = {i.filename: data for i, data in parts}
doc = E.fromstring(partmap['word/document.xml'])
body = doc.find('w:body', NS)
rels = E.fromstring(partmap['word/_rels/document.xml.rels'])
with ZipFile(ROOT / 'tools/templates/validation.docx') as z:
    template = E.fromstring(z.read('word/document.xml'))
template_tables = template.findall('w:body/w:tbl', NS)
tables = body.findall('w:tbl', NS)
main, second, confidence, membership, allocation = tables[:5]
fields = {tx(row.find('w:tc', NS)): row for table in (main, second) for row in table.findall('w:tr', NS)[1:]}
protected_names = ['SPPR calculation', 'Open issues and next action', 'Review and reproducibility', 'Selection rationale']
protected = {n: E.tostring(fields[n].findall('w:tc', NS)[1]) for n in protected_names}

def r(text, bold=False, link=False):
    n = E.Element(q('r')); pr = E.SubElement(n, q('rPr'))
    E.SubElement(pr, q('rFonts'), {q('ascii'): 'Calibri', q('hAnsi'): 'Calibri'})
    E.SubElement(pr, q('sz'), {q('val'): '21'})
    if bold: E.SubElement(pr, q('b'))
    if link:
        E.SubElement(pr, q('color'), {q('val'): '0563C1'})
        E.SubElement(pr, q('u'), {q('val'): 'single'})
    E.SubElement(n, q('t'), {'{http://www.w3.org/XML/1998/namespace}space': 'preserve'}).text = text
    return n

def p(text='', style=None, keep=False):
    n = E.Element(q('p')); pr = E.SubElement(n, q('pPr'))
    if style: E.SubElement(pr, q('pStyle'), {q('val'): style})
    if keep: E.SubElement(pr, q('keepNext'))
    E.SubElement(pr, q('spacing'), {q('after'): '60', q('before'): '0', q('line'): '240', q('lineRule'): 'auto'})
    if text: n.append(r(text))
    return n

def link(parent, label, target):
    rid = 'rIdRefresh' + str(len(rels))
    E.SubElement(rels, '{'+PKG+'}Relationship', {'Id': rid, 'Type': R+'/hyperlink', 'Target': target, 'TargetMode': 'External'})
    h = E.SubElement(parent, q('hyperlink'), {'{'+R+'}id': rid}); h.append(r(label, link=True))

def cell(label, paragraphs, links=None):
    tc = fields[label].findall('w:tc', NS)[1]
    for n in list(tc):
        if n.tag != q('tcPr'): tc.remove(n)
    for text in paragraphs: tc.append(p(text))
    if links:
        n = p()
        for i, (label, target) in enumerate(links):
            if i: n.append(r(' | '))
            link(n, label, target)
        tc.append(n)

def replace_p(starts, text, links=None):
    old = next(n for n in body.findall('w:p', NS) if tx(n).startswith(starts))
    new = p(text)
    if links:
        new.append(r(' '))
        for i, (label, target) in enumerate(links):
            if i: new.append(r(' | '))
            link(new, label, target)
    body.replace(old, new)
    return new

# Current template field order; preserve all researcher-owned cells verbatim.
order = [tx(row.find('w:tc', NS)) for row in template_tables[0].findall('w:tr', NS)[1:]]
for row in list(main.findall('w:tr', NS))[1:]: main.remove(row)
for name in order: main.append(fields[name])
body.remove(second)
for n in list(body.findall('w:p', NS)):
    if tx(n) == 'Regional review completed': body.remove(n)

cell('Catch source', ['Sea Around Us v50.1; 1950-2019. Reference: 2019 landings, including all 181 catch labels and zero-catch records.'], [('Original catch', '../../../../../raw/catch/LME_038-catch.zip')])
cell('Selected article', ['Buchary, E. A. (1999). Evaluating the effect of the 1980 trawl ban in the Java Sea, Indonesia: An ecosystem-based approach. MSc thesis, University of British Columbia.'], [('Original thesis', '../../../../BUCHARY-1991/sources/ubc_1999-0254.pdf.pdf')])
cell('Selected model', ['38_38003_Java_Sea_normalized_BA_completed_(mid1970s). Mid-1970s Java Sea model, principally 1974-1976; 28 source groups plus one runtime import. Reported study area: 471,000 km2. The retained identifier predates the six-cell source restoration.'], [('Current model', '../model.json'), ('Model notes', '../model_notes.md')])
cell('Other models from the same article', ['The printed-source reconstruction (38001) and selected computational variant (38003) represent one mid-1970s static baseline. Ecosim trawl-ban scenarios are not a second independently verified complete static model.'])
cell('Model extraction', ['Six Macrozoobenthos diet entries match the printed Table 3.10 values, which sum to 0.660 despite its unit-sum caption; the missing 0.340 remains unexplained. Twenty-eight retained BA values are computational completions, not measured stock changes.', 'The diagnostic runtime normalizes a separate diet copy and applies the audited defaults. Whole-matrix fidelity to the primary source remains unverified.'], [('Model notes and departures', '../model_notes.md'), ('Six-cell restoration', 'evidence/source_review/diet_reextraction_20261002/changed_cells_ledger.json'), ('Runtime transformations', '../results/diagnostics/validation_20261114/runtime_transformation_ledger.json')])
ge, te = d['GE'], d['TE']
cell('GE diagnostics', ['OK', 'No negative SPPR entries across the basal-source columns.', f"rho_living = {ge['divergence']['rho_living']:.4f}; b = {ge['divergence']['b']:.4f}.", f"Detritus (28): SPPR = {ge['divergence']['sppr_det']['28']:.4f}.", 'Runtime production/consumption and global flow balances meet the diagnostic thresholds.'])
cell('TE diagnostics', ['WARN: Marine mammals (27) have near-zero transfer efficiency.', 'No negative SPPR entries across the basal-source columns.', f"rho_living = {te['divergence']['rho_living']:.4f}.", f"Detritus (28): SPPR = {te['divergence']['sppr_det']['28']:.4f}.", 'Finite coefficients retain this warning; convergence does not establish ecological suitability.'])
cell('Geographic fit', ['A. Region covered by study: approximately 19-22%.', 'B. Study area covered by region: approximately 99-100%.'])
cell('Temporal fit', ['The model represents the mid-1970s, principally 1974-1976. Fixed coefficients and composition proxies transferred to 1950-2019 catches, including the 2019 landings reference, assume persistence across decades and the wider LME. They do not reconstruct annual ecosystem dynamics.'])
cell('Other', ['GE, TE and With Egestion were run on the current canonical input on 14/11/2026 using the audited baseline engine and settings, with no EE floor. With Egestion is OK. The report evaluates this configuration; regional numerical outputs remain pending adoption.'], [('Current full diagnostics', '../results/diagnostics/validation_20261114/direct_reports.json'), ('Execution and input identity', '../results/diagnostics/validation_20261114/execution_evidence.json')])

# Copy only automatic table formatting from the current template.
for name in order:
    if name in protected_names: continue
    row = fields[name]
    sample = template_tables[0].findall('w:tr', NS)[1]
    for tc, stc in zip(row.findall('w:tc', NS), sample.findall('w:tc', NS)):
        old = tc.find('w:tcPr', NS)
        if old is not None: tc.remove(old)
        tc.insert(0, deepcopy(stc.find('w:tcPr', NS)))

replace_p('Reference:', 'Reference: 2019 landings; all recorded catch labels, including zero catch and residual categories; no group filter.')
replace_p('28 source groups', '28 source groups (+1 computational import); 181 catch taxa.')
replace_p('Simple-chain PPR totals', f"Simple-chain PPR totals {m['total_simple_chain_ppr_tC']:,.2f} t C in 2019.")
replace_p('39 labels lack', '39 labels lack a classic TL/coefficient; all have zero 2019 landings and zero annual PPR. Their TL and coefficient remain unavailable.')
replace_p('Method:', 'Method: simple trophic chain using the saved taxon coefficients.')
replace_p('The summary uses', 'Overall confidence uses the weaker required membership or allocation component.')

def fill_table(table, rows):
    sample = deepcopy(table.findall('w:tr', NS)[1])
    for row in list(table.findall('w:tr', NS))[1:]: table.remove(row)
    for values in rows:
        row = deepcopy(sample)
        for tc, value in zip(row.findall('w:tc', NS), values):
            for n in list(tc):
                if n.tag != q('tcPr'): tc.remove(n)
            tc.append(p(str(value)))
        table.append(row)

for tc, label in zip(confidence.findall('w:tr', NS)[0].findall('w:tc', NS), ['Overall confidence', 'Taxa (n)', 'Catch (%)', 'Simple-chain PPR (%)']):
    texts = tc.findall('.//w:t', NS)
    texts[0].text = label
    for t in texts[1:]: t.text = ''
fill_table(confidence, [[x['label'], x['taxa'], format_percent(x['catch_percentage']), format_percent(x['ppr_percentage'])] for x in m['confidence_summary']])
fill_table(membership, [[x['plain_language_rule'], x['confidence'], format_percent(x['ppr_percentage'])] for x in m['membership_summary']])
fill_table(allocation, [[x['plain_language_rule'], x['confidence'], format_percent(x['ppr_percentage'])] for x in m['allocation_summary']])
replace_p('Membership evidence:', 'Membership evidence:', [('Source group definitions', '../../../../BUCHARY-1991/sources/ubc_1999-0254.pdf.pdf#page=58'), ('Taxon decisions and Sources', 'taxon_mapping.xlsx#Sources%21A1')])
replace_p('Percentages are each', 'Weights and assumptions: complete historical model catches provide fixed composition proxies, including genuine zeros and author-assumed juvenile catches. Living bottom structure uses assumed trawl bycatch. Identified-catch donor fractions include taxa outside the target lineage and differ in reporting population and catch basis; their allocation confidence remains Low.', [('Allocation evidence', 'evidence/source_review/identified_catch_proxy_review.json')])
low = next(x for x in m['confidence_summary'] if x['label'] == 'Very low')
uncertainty = replace_p('Unresolved:', f"Unresolved taxa: none. The 36 Very low decisions account for {format_percent(low['catch_percentage'])} of landings and {format_percent(low['ppr_percentage'])} of simple-chain PPR. Their specific limitations follow below.")
body.insert(body.index(uncertainty), p('Each rule percentage is the share of independent simple-chain PPR associated with taxa using that rule.'))
coefficients = read(diag_dir / 'group_scope_coefficients.json')
exposure = {}
for method in ['GE', 'TE', 'With Egestion']:
    co = {x['group_id']: x['sppr'] for x in coefficients if x['method'] == method and x['scope'] == 'all'}
    values = {x['taxon']: x['catch_tonnes'] * sum(co[g] * w for g, w in zip(x['group_ids'], x['weights'])) / 9 for x in m['rows']}
    total = sum(values.values())
    exposure[method] = {'total_tC': total, 'very_low_percentage': 100 * sum(values[t] for t in expected_vl) / total, 'taxon_percentages': {t: 100 * n / total for t, n in values.items()}}
exposure_file = V / 'evidence/mapping/current_method_exposure_20261114.json'
exposure_file.parent.mkdir(parents=True, exist_ok=True)
exposure_file.write_text(json.dumps({'scope': 'Review arithmetic only, all-source 2019 landings with all adopted groups; not adopted regional results', 'methods': exposure}, indent=2), encoding='utf-8')
exposure_p = p(f"Very low assignments account for {format_percent(exposure['TE']['very_low_percentage'])} of all-source TE PPR. Marine fishes not identified contribute {format_percent(exposure['TE']['taxon_percentages']['Marine fishes not identified'])}, and Lates calcarifer contributes {format_percent(exposure['TE']['taxon_percentages']['Lates calcarifer'])}. These model-based contributions remain sensitive to the stated mapping assumptions. ")
link(exposure_p, 'Method-specific exposure', 'evidence/mapping/current_method_exposure_20261114.json')
body.insert(body.index(uncertainty) + 1, exposure_p)
heading = p('Very low decisions', 'Heading2', True)
vt = deepcopy(template_tables[4])
fill_table(vt, [['; '.join(x['taxa']), x['reason']] for x in vl])
index = body.index(exposure_p) + 1
body.insert(index, heading); body.insert(index + 1, vt)

# Keep existing readable figures/captions, with historical control tests attributed.
for n in body.findall('w:p', NS):
    for t in n.findall('.//w:t', NS):
        if t.text and 'All seven stated water/land controls pass.' in t.text:
            t.text = t.text.replace('All seven stated water/land controls pass.', 'The retained reconstruction records seven water/land controls.')

# Header repetition and current template flow. Preserve manual row internals.
for table in body.findall('w:tbl', NS):
    head = table.find('w:tr', NS)
    pr = head.find('w:trPr', NS)
    if pr is None: pr = E.SubElement(head, q('trPr'))
    if pr.find('w:tblHeader', NS) is None: E.SubElement(pr, q('tblHeader'))
for n in body.findall('w:p', NS):
    if tx(n) == 'Allocation weight rules':
        for b in n.findall('w:pPr/w:pageBreakBefore', NS): b.getparent().remove(b)

# All visible links must be blue and underlined; remove unused dead relationships.
used = {n.get('{'+R+'}id') for n in doc.findall('.//w:hyperlink', NS)}
for rel in list(rels):
    if rel.get('Type') == R+'/hyperlink' and rel.get('Id') not in used: rels.remove(rel)
for h in doc.findall('.//w:hyperlink', NS):
    for run in h.findall('.//w:r', NS):
        pr = run.find('w:rPr', NS)
        if pr is None: pr = E.SubElement(run, q('rPr'))
        for tag, value in [('color', '0563C1'), ('u', 'single')]:
            el = pr.find('w:'+tag, NS)
            if el is None: el = E.SubElement(pr, q(tag))
            el.set(q('val'), value)

for name, data in protected.items():
    assert E.tostring(fields[name].findall('w:tc', NS)[1]) == data, name
changed = {'word/document.xml': E.tostring(doc, xml_declaration=True, encoding='utf-8'), 'word/_rels/document.xml.rels': E.tostring(rels, xml_declaration=True, encoding='utf-8')}
out = V / 'validation.docx'
with ZipFile(out, 'w') as z:
    for info, data in parts: z.writestr(info, changed.get(info.filename, data))
verify_report(out)
with ZipFile(out) as z:
    differences = [info.filename for info, data in parts if z.read(info.filename) != data]
assert differences == ['word/document.xml', 'word/_rels/document.xml.rels'], differences
(RUN/'qa/report_structure.json').write_text(json.dumps({'changed_parts': differences, 'manual_cells_preserved': protected_names, 'very_low_taxa_once': len(all_vl), 'main_field_order': order, 'docx_sha256': hashlib.sha256(out.read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
print(out)
