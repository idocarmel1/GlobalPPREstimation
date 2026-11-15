"""Bounded report edit: preserve original ZIP parts and manual OOXML verbatim."""
from pathlib import Path
from zipfile import ZipFile
from xml.sax.saxutils import escape
from lxml import etree as E
from unittest.mock import patch
import hashlib, json, re, sys

ROOT = Path.cwd().resolve()
MODEL = ROOT / 'regions/LME/LME_013/papers/HUM-2018/models/Chiaverano2018_detailed_Northern_Humboldt_1995_1998'
RUN = MODEL / 'model_validation/work/2026-11-15_011000_ee_floor_docx'
SOURCE = MODEL / 'model_validation/validation.docx'
STAGED = RUN / 'outputs/validation.docx'
EXPECTED = 'b356cb1f7891659dd15aae44caf8561c8c122709506234255e3bb7b9f384669d'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(SOURCE.read_bytes()) == EXPECTED, 'Canonical source changed; stop instead of overwriting new edits.'

with ZipFile(SOURCE) as z:
    parts = [(i, z.read(i.filename)) for i in z.infolist()]
original = dict((i.filename, b) for i, b in parts)
xml = original['word/document.xml'].decode('utf8')
rels = original['word/_rels/document.xml.rels'].decode('utf8')

def plain(fragment):
    return ''.join(E.fromstring(('<root xmlns:w="'+W+'" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">'+fragment+'</root>').encode()).xpath('.//w:t/text()', namespaces=NS))

rows = {}
for match in re.finditer(r'<w:tr(?:\s[^>]*)?>.*?</w:tr>', xml, re.S):
    cells = re.findall(r'<w:tc(?:\s[^>]*)?>.*?</w:tc>', match.group(), re.S)
    if len(cells) == 2:
        rows[plain(cells[0])] = match.group()

def paragraph(text, bold=False, keep=False, break_before=False):
    props = '<w:spacing w:after="60"/>'
    if keep: props = '<w:keepNext/>' + props
    if break_before: props = '<w:pageBreakBefore/>' + props
    return '<w:p><w:pPr>'+props+'</w:pPr><w:r><w:rPr>'+('<w:b/>' if bold else '')+'<w:sz w:val="21"/></w:rPr><w:t xml:space="preserve">'+escape(text)+'</w:t></w:r></w:p>'

def link_paragraph(label, rid):
    return '<w:p><w:pPr><w:spacing w:after="60"/></w:pPr><w:hyperlink r:id="'+rid+'"><w:r><w:rPr><w:color w:val="0563C1"/><w:sz w:val="21"/><w:u w:val="single"/></w:rPr><w:t>'+escape(label)+'</w:t></w:r></w:hyperlink></w:p>'

def new_diag_row(label, paragraphs, rid):
    old = rows[label]
    cells = list(re.finditer(r'<w:tc(?:\s[^>]*)?>.*?</w:tc>', old, re.S))
    second = cells[1]
    cell = second.group()
    first_p = re.search(r'<w:p(?:\s[^>]*)?>', cell).start()
    content = ''.join(paragraph(t, bold=(i==0)) for i,t in enumerate(paragraphs))
    content += link_paragraph('Current '+label[:2]+' full return', rid)
    content += paragraph('Historical reviewed entry and numerical comparison are retained in the EE floor calculation update at the end of this report.')
    new_cell = cell[:first_p] + content + '</w:tc>'
    return old[:second.start()] + new_cell + old[second.end():]

ge = [
    "WARN: successful pooled-detritus GE result with EE floor 0.1 and det_collapse_mode='auto'.",
    'Pooled groups 36–39: SPPR = 4.9871. No negative entries across any basal-source column or recipient. rho_living = 0.7000; PP budget check: OK.',
    'Unpooled option: FAIL (b = 1.6236 > 1). The saved engine aggregate grade remains FAIL because it carries the unpooled recycling check; it is distinct from the pooled-result WARN reported here. A current pooled b was not retained.',
    'Seabirds (31) remains near-singular. Both current methods retain an unexplained negative Benthic detritus (39) stock residual of −4337.3803. No missing source supply has been invented; budget closure does not establish ecological validity.',
]
te = [
    'WARN: EE-floor TE result. The PP budget check is now OK (gap = 0.0000077%); the historical result was FAIL with a 14% gap.',
    'No negative SPPR entries across any basal-source column or recipient. rho_living = 0.7316.',
    'Detritus SPPR: Anchovy eggs (36) = 0.0000; Fishery offal (37) = 0.0000; Pelagic detritus (38) = 0.3050; Benthic detritus (39) = 0.0000.',
    'Near-singular groups remain: Cetaceans (33), Pinnipeds (32) and Seabirds (31). The negative detritus stock residual described above also remains. The five formerly EE=0 living groups and Chrysaora plocamia now have effective EE = 0.1; their source values are unchanged.',
    "Settings retain use_ee_floor=True, ee_floor=0.1, det_collapse_mode='auto' and fix_EE_0_cases=True. TE does not pool in this run. Its b = 0 denotes no detritus recycling matrix, rather than evidence of ecological validity.",
]
replacements = {
    rows['GE diagnostics']: new_diag_row('GE diagnostics', ge, 'rIdFloorGE'),
    rows['TE diagnostics']: new_diag_row('TE diagnostics', te, 'rIdFloorTE'),
}
for old,new in replacements.items():
    assert xml.count(old) == 1
    xml = xml.replace(old,new,1)

def heading(text, page_break=False):
    return '<w:p><w:pPr><w:pStyle w:val="Heading1"/>'+('<w:pageBreakBefore/>' if page_break else '')+'<w:keepNext/><w:spacing w:before="180" w:after="120"/></w:pPr><w:r><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="26"/></w:rPr><w:t>'+escape(text)+'</w:t></w:r></w:p>'

def table(headers, data, widths):
    out='<w:tbl><w:tblPr><w:tblW w:w="10037" w:type="dxa"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>'
    out+=''.join('<w:gridCol w:w="'+str(v)+'"/>' for v in widths)+'</w:tblGrid>'
    for i,row in enumerate([headers]+data):
        out+='<w:tr><w:trPr><w:cantSplit/>'+('<w:tblHeader/>' if i==0 else '')+'</w:trPr>'
        for text,width in zip(row,widths):
            out+='<w:tc><w:tcPr><w:tcW w:w="'+str(width)+'" w:type="dxa"/><w:tcBorders>'
            out+=''.join('<w:'+side+' w:val="single" w:sz="5" w:color="D9D9D9"/>' for side in ['top','left','bottom','right'])
            out+='</w:tcBorders><w:shd w:val="clear" w:fill="'+('EAEFF4' if i==0 else 'FFFFFF')+'"/><w:tcMar><w:top w:w="70" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar></w:tcPr>'+paragraph(str(text),bold=i==0)+'</w:tc>'
        out+='</w:tr>'
    return out+'</w:tbl>'

appendix = heading('EE floor calculation update', True)
appendix += paragraph("Calculation configuration adopted by the user on 15 November 2026: use_ee_floor=True, ee_floor=0.1, det_collapse_mode='auto'. The floor is applied after audited initialization. It moves part of nonpredatory mortality from detritus inflow to a hypothetical external nonfishery sink, while preserving living biological flows and catch. It is a calculation assumption, not a correction to published parameters.")
appendix += paragraph('The researcher’s MODEL VALIDATED verdict, Ido Carmel signature and 8 October 2026 review date are retained. This update records the subsequent calculation choice; it does not present the historical signature as renewed approval of transformed diagnostic outcomes. Researcher validation and numerical diagnostic success remain separate.')
appendix += paragraph('The source extraction, manual notes, mapping and four display exclusions are unchanged: Fishery offal, Pinnipeds, Seabirds and Chrysaora plocamia. Their original EE annotations in the signed SPPR calculation notes describe the historical state. The original Other entry also records its historical publication context.')
appendix += table(['Affected living group', 'EE before floor', 'Effective EE'], [
    ['Leatherback turtle (35)', '0', '0.1'],
    ['Green sea turtle (34)', '0', '0.1'],
    ['Cetaceans (33)', '0', '0.1'],
    ['Pinnipeds (32)', '0', '0.1'],
    ['Seabirds (31)', '0', '0.1'],
    ['Conger (25)', '0.01129067317', '0.1'],
    ['Chrysaora plocamia (7)', '0.00006117805', '0.1'],
], [5100,2700,2237])
appendix += paragraph('The canonical source values are retained. Fishery offal is detritus and is not one of the seven living groups changed by the floor.')
appendix += heading('Effect on 2019 PPR')
appendix += paragraph('Comparison uses the same saved 2019 landings, all sources, mapping, original allocation shares and the four researcher exclusions, with the same carbon conversion. These are arithmetic comparisons of saved coefficients; no new scientific run was performed for this report.')
appendix += table(['Method', 'Reviewed PPR\n(million t C/year)', 'EE-floor PPR\n(million t C/year)', 'Change'], [
    ['GE', '244.047', '227.510', '−6.8%'],
    ['TE', '835.806', '302.009', '−64%'],
], [1300,3200,3200,2337])
appendix += paragraph('Relative to the same global atlas NPP denominator, GE changes from 0.58% to 0.54% and TE from 2.0% to 0.72%. The fixed atlas-union reference is coverage-limited. These ratios do not use the model-domain NPP as their denominator.')
appendix += paragraph('Conger TE SPPR decreases from 447,435.87 to 50,518.52. The material PPR change is particularly large for TE; it reflects the changed EE assumption and associated accounting, not a fixed-settings comparison of engine versions.')
appendix += heading('Historical diagnostic entries', True)
appendix += paragraph('The following entries are retained verbatim from the report signed on 8 October 2026. They describe the reviewed configuration without the later EE floor. Their values and source links are historical evidence, not the current calculation.')
appendix += paragraph('In the historical GE entry, WARN refers to successful pooling; its saved aggregate engine grade was FAIL from the unpooled divergence check. The historical pooled b = 0.7459 is not a current estimate. The current pooled GE result is WARN, while its raw engine aggregate and the unpooled option remain FAIL. Historical TE overall and budget grades were FAIL; current TE overall is WARN and its budget check is OK.')
first_table = re.search(r'<w:tbl(?:\s[^>]*)?>.*?</w:tbl>', original['word/document.xml'].decode('utf8'), re.S).group()
start = first_table[:first_table.index('<w:tr')]
header = re.search(r'<w:tr(?:\s[^>]*)?>.*?</w:tr>', first_table, re.S).group()
historical_rows = {}
for label in ['GE diagnostics', 'TE diagnostics']:
    assert ('>'+label+'<') in rows[label]
    historical_rows[label] = rows[label].replace('>'+label+'<', '>Historical '+label+'<', 1)
appendix += start + header + historical_rows['GE diagnostics'] + historical_rows['TE diagnostics'] + '</w:tbl>'
appendix += paragraph('Current matrices are finite and nonnegative in all 40 recipient rows and seven source columns. Historical unpooled negative source-to-group pairings remain in the unchanged linked appendix; no historical negative result has been recast as a current one.')

# Use manual line breaks for newly created header text only.
appendix = appendix.replace('\n','</w:t><w:br/><w:t>')
end = xml.rfind('<w:sectPr')
assert end > 0 and xml.rfind('</w:tbl>') < end
xml = xml[:end]+appendix+xml[end:]

for rid,target in [('rIdFloorGE','../results/diagnostics/method_coverage/deterministic_completion_20261114/controls/new_GE.json.gz'),('rIdFloorTE','../results/diagnostics/method_coverage/deterministic_completion_20261114/controls/new_TE_EEfix.json.gz')]:
    assert rid not in rels
    rels=rels.replace('</Relationships>','<Relationship Id="'+rid+'" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="'+target+'" TargetMode="External"/></Relationships>')
changed={'word/document.xml':xml.encode('utf8'),'word/_rels/document.xml.rels':rels.encode('utf8')}
for data in changed.values(): E.fromstring(data)
with ZipFile(STAGED,'w') as out:
    for info,data in parts: out.writestr(info,changed.get(info.filename,data))

# Parse the staged bytes at their intended canonical location without writing there.
# This is necessary because the unchanged hyperlinks are canonical-relative.
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.researcher_review import read_report
from tools.project_core.validation.validation_percentage_format import verify_report
verify_report(STAGED)
original_zipfile=ZipFile
def redirected(path,*args,**kwargs):
    if Path(path).resolve()==SOURCE.resolve(): path=STAGED
    return original_zipfile(path,*args,**kwargs)
before=read_report(ROOT,SOURCE,MODEL.name)
with patch('tools.project_core.validation.researcher_review.zipfile.ZipFile',redirected):
    after=read_report(ROOT,SOURCE,MODEL.name)
assert before[:2]==after[:2]
assert before[2]['note']==after[2]['note']
changed_sections=[]
for b,a in zip(before[2]['sections'],after[2]['sections']):
    if b!=a: changed_sections.append(b['heading'])
assert changed_sections==['GE and TE diagnostics'],changed_sections
assert len(json.dumps(after[2],ensure_ascii=False,separators=(',',':'))) < 32000
for name in ['Selection rationale','Model extraction','SPPR calculation','Geographic fit','Other','Open issues and next action','Review and reproducibility']:
    assert rows[name] in xml, name+' was modified'
# All original non-diagnostic row fragments still appear. Historical diagnostic
# entry cells are exact; their labels have a prefix to avoid shadowing the
# current fields in the existing source parser.
for name,row in rows.items():
    if name not in historical_rows: assert row in xml,name
for name,row in historical_rows.items():
    assert xml.count(row)==1
    assert re.findall(r'<w:tc(?:\s[^>]*)?>.*?</w:tc>', row, re.S)[1] == re.findall(r'<w:tc(?:\s[^>]*)?>.*?</w:tc>', rows[name], re.S)[1]
with ZipFile(STAGED) as z:
    actual_changed=[n for n,b in original.items() if z.read(n)!=b]
assert actual_changed==['word/document.xml','word/_rels/document.xml.rels'] or set(actual_changed)==set(changed)
for label,obj in [('signoff_after_projected',after),('intended_parser_changes',{'mode':'Read staged ZIP bytes at intended canonical path, with no canonical mutation','changed_sections':changed_sections,'unchanged_signer_date':before[:2],'unchanged_exclusion_note':after[2]['note'],'diagnostic_rows_before':before[2]['sections'][1]['rows'],'diagnostic_rows_after':after[2]['sections'][1]['rows']}),('package_preservation',{'changed_parts':actual_changed,'other_parts_byte_identical':True,'manual_and_non_diagnostic_row_fragments_byte_identical':True,'canonical_source_sha256':sha(SOURCE.read_bytes()),'staged_sha256':sha(STAGED.read_bytes()),'historical_GE_TE_entry_cells_preserved_verbatim_in_appendix':True,'historical_field_labels_prefixed_to_avoid_parser_shadowing':True,'percentage_format':'PASS','new_links_canonical_relative':True})]:
    (RUN/'qa'/f'{label}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'staged':str(STAGED),'sha256':sha(STAGED.read_bytes()),'parser_changed_sections':changed_sections,'summary_chars':len(json.dumps(after[2],ensure_ascii=False,separators=(',',':')))},ensure_ascii=False))
