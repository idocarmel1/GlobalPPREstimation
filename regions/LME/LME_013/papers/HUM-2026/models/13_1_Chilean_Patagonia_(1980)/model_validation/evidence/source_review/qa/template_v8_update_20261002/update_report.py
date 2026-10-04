from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from collections import defaultdict
import hashlib, json, math, re, shutil
from lxml import etree
import openpyxl

QA=Path(__file__).resolve().parent
ROOT=QA.parents[5]
REGION=ROOT/'regions/LME_013'
EVIDENCE=QA.parent.parent
REPORT=REGION/'Model_validation_13_1_Chilean_Patagonia_(1980).docx'
TEMPLATE=ROOT/'tools/templates/Model_validation_template.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
def tag(n): return '{'+W+'}'+n
def text(n): return ''.join(n.itertext()) if False else ''.join(n.xpath('.//w:t/text()',namespaces=NS))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(n): return etree.tostring(n,method='c14n')

audit=json.loads((EVIDENCE/'taxon_audit.json').read_text(encoding='utf-8'))
summary=json.loads((EVIDENCE/'coverage_summary.json').read_text(encoding='utf-8'))
matrix=json.loads((EVIDENCE/'matrix_inspection.json').read_text(encoding='utf-8'))
SOURCE=QA/'baseline.docx' if (QA/'baseline.docx').exists() else REPORT
with ZipFile(SOURCE) as z:
    infos=z.infolist(); parts={i.filename:z.read(i.filename) for i in infos}
xml=etree.fromstring(parts['word/document.xml'])
with ZipFile(TEMPLATE) as z: template=etree.fromstring(z.read('word/document.xml'))
body=xml.find('w:body',NS)
tables=body.findall('w:tbl',NS)
first,second,confidence,membership,allocation=tables[:5]
all_rows=first.findall('w:tr',NS)+second.findall('w:tr',NS)[1:]
rows={text(r.find('w:tc',NS)):r for r in all_rows[1:]}
manual=['SPPR calculation','Open issues and next action','Review and reproducibility']
manual_before={k:canonical(rows[k]) for k in manual}
science=[REGION/'LME_013.xlsx',REGION/'LME013_taxon_mapping_appendix.xlsx',REGION/'models/13_1_Chilean_Patagonia_(1980)/model.json']
protected={str(p.relative_to(ROOT)):sha(p) for p in science}
if not (QA/'baseline.docx').exists():shutil.copy2(REPORT,QA/'baseline.docx')

def paragraph(value, source=None, bold=False):
    old_rp=source.find('w:r/w:rPr',NS) if source is not None else None
    p=deepcopy(source) if source is not None else etree.Element(tag('p'))
    for child in list(p):
        if child.tag!=tag('pPr'): p.remove(child)
    r=etree.SubElement(p,tag('r'))
    if old_rp is not None:r.append(deepcopy(old_rp))
    if bold:
        rp=r.find('w:rPr',NS)
        if rp is None:rp=etree.SubElement(r,tag('rPr'))
        etree.SubElement(rp,tag('b'))
    t=etree.SubElement(r,tag('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=value
    return p

def replace_paragraph(p,value,keep_links=False):
    links=[deepcopy(n) for n in p.findall('w:hyperlink',NS)] if keep_links else []
    new=paragraph(value,p)
    for i,link in enumerate(links):
        gap=etree.SubElement(new,tag('r'));t=etree.SubElement(gap,tag('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text='  ' if i==0 else ' | '
        new.append(link)
    p.getparent().replace(p,new)
    return new

def fill_cell(cell,values,keep_links=False):
    old=cell.find('w:p',NS)
    links=[deepcopy(n) for n in cell.xpath('.//w:hyperlink',namespaces=NS)] if keep_links else []
    for n in list(cell):
        if n.tag!=tag('tcPr'):cell.remove(n)
    for value in values:cell.append(paragraph(value,old))
    if links:
        p=cell[-1]
        for i,link in enumerate(links):
            r=etree.SubElement(p,tag('r'));t=etree.SubElement(r,tag('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text='  ' if i==0 else ' | '
            p.append(link)

def entry(key):return rows[key].findall('w:tc',NS)[1]

# Preserve whole researcher rows and opaque package parts; move only existing rows.
order=['Region','Catch source','Selected article','Other known articles','Selected model','Other models from the same article','Selection rationale','Model extraction','GE diagnostics','TE diagnostics','SPPR calculation','Geographic fit','Temporal fit','Other','Open issues and next action','Review and reproducibility']
for r in first.findall('w:tr',NS)[1:]: first.remove(r)
for key in order:first.append(rows[key])
separator=second.getprevious()
if separator is not None and separator.tag==tag('p') and not text(separator):body.remove(separator)
body.remove(second)
replace_paragraph(body.find('w:p',NS),'Humboldt Current model validation')

old_rationale=text(entry('Selection rationale'))
fill_cell(entry('Selection rationale'),['Article - ?','Model - '+old_rationale])
for method in ['GE','TE']:
    saved=next(m for m in matrix['methods'] if m['method']==method)
    values=saved['source_matrix']['values']
    assert len(values)==16 and all(len(r)==3 for r in values)
    assert all(math.isfinite(v) and v>=0 for r in values for v in r)
    lines=['WARN: source reconstruction and accepted runtime transformations remain limitations.',
           'No negative SPPR entries across the basal-source columns.',
           f"rho_living = {saved['rho_living']:.4f}"]
    if method=='GE':lines.append(f"b = {saved['b']:.4f}")
    lines.extend([f"Detritus (15): SPPR = {saved['detritus_sppr']['Detritus']:.4f}",
                  'Strict mass balance passes in the accepted runtime.'])
    fill_cell(entry(method+' diagnostics'),lines)
fill_cell(entry('Geographic fit'),['Approximate A. Region covered by study: 7–11%.','Approximate B. Study covered by region: 60–95%.'],keep_links=True)
fill_cell(entry('Other'),['With Egestion also retains WARN: rho_living = 0.2863; b = 0.0213; Detritus (15) SPPR = 1.0509. Strict mass balance passes. Skates source EE cannot be interpreted without missing BA.'],keep_links=True)

# Shorten only automatic coverage prose, retaining existing links and scientific values.
for p in list(body.findall('w:p',NS)):
    value=text(p)
    if value.startswith('Simple-chain PPR totals'):
        replace_paragraph(p,f"Simple-chain PPR totals {summary['total_simple_chain_ppr_tC']:,.2f} t C in 2019.")
    elif value.startswith('Method: independent simple trophic chain'):
        replace_paragraph(p,'Method: simple trophic chain.')
    elif value.startswith('The summary uses the weaker'):
        replace_paragraph(p,'Overall confidence uses the weaker required membership or allocation component.')
    elif value.startswith('Each percentage uses the same complete'):
        replace_paragraph(p,'Weights and assumptions: Hoki uses 1980 model landings proportions, transferred to regional catch years. Other split labels use model biomass proportions because source catches are incomplete; composition and catchability are assumed constant across years and catch bases.',keep_links=True)
    elif value.startswith('Unresolved: none.'):
        replace_paragraph(p,'Unresolved taxa: none. The 121 Very low decisions account for 16.8066% of landings and 60.2188% of simple-chain PPR. Dosidicus gigas alone contributes 38.8770% of simple-chain PPR. Full mapping coverage does not establish ecological validity. Residual fish candidate sets and their reporting limits are retained in the evidence.',keep_links=True)

headers=['Overall confidence','Taxa (n)','Catch (%)','Simple-chain PPR (%)']
for c,value in zip(confidence.find('w:tr',NS).findall('w:tc',NS),headers):fill_cell(c,[value])
for table in [membership,allocation]:
    for row in table.findall('w:tr',NS)[1:]:
        cell=row.find('w:tc',NS)
        for t in cell.findall('.//w:t',NS):
            t.text=re.sub(r'^[MW]\d+:\s*','',t.text or '')
    for row in table.findall('w:tr',NS):
        rp=row.find('w:trPr',NS)
        if rp is None:rp=etree.SubElement(row,tag('trPr'))
        if rp.find('w:cantSplit',NS) is None:etree.SubElement(rp,tag('cantSplit'))

# Current seven-column appendix is the decision-table authority.
wb=openpyxl.load_workbook(REGION/'LME013_taxon_mapping_appendix.xlsx',read_only=True,data_only=False)
appendix=list(wb['Taxon mapping'].values)[7:]
wb.close()
assert len(appendix)==218 and len({r[0] for r in appendix})==218
assert set(r[0] for r in appendix)==set(r['taxon'] for r in audit)
assert math.isclose(sum(r[3] for r in appendix if isinstance(r[3],(int,float))),summary['total_simple_chain_ppr_tC'],rel_tol=1e-12)
verylow=[r for r in appendix if r[5]=='Very low']
assert len(verylow)==121
grouped=defaultdict(list)
for r in verylow:
    reason=re.sub(r'^M\d+ / W\d+:\s*','',r[6])
    reason=re.sub(r'\s*Sources:.*$','',reason)
    grouped[reason].append(r)
short_reasons={
 'Acanthocybium solandri':'Small pelagic fish is the only explicitly pelagic fish pool. Large oceanic predators and broad-family labels extend beyond its small/medium source definition; size, feeding and composition are uncertain.',
 'Alopias':'Skates contains the named Dipturus/Zearaja chilensis stock. Sharks, other rays and chimaeras share cartilaginous taxonomy but differ in feeding, form and habitat; broad-label composition is unknown.',
 'Aplodactylus punctatus':'Other demersal fish is specifically a Seriolella pool. Unlisted demersal, reef and benthopelagic fish use a weak bottom-associated analogue, with taxonomic, depth, size or habitat mismatch.',
 'Chrysaora plocamia':'Macrozooplankton explicitly represents euphausiids. The jellyfish shares a pelagic invertebrate role but differs in body size, gelatinous composition and feeding.',
 'Doryteuthis gahi':'Shelf squid uses Small pelagic fish as a partial active-nekton analogue. It is not a source-listed fish; taxonomy, feeding and shelf/demersal movements differ.',
 'Dosidicus gigas':'Oceanic predatory squid uses Small pelagic fish as a partial active-nekton analogue. Its large size, feeding level, taxonomy and offshore habitat exceed the forage-fish definition.',
 'Elasmobranchii':'The shark/ray/skate reporting category excludes chimaeras. Skates supplies only a weak analogue for its unknown mixture, with feeding, form and habitat differences.',
 'Galaxias maculatus':'The diadromous and estuarine fish has no freshwater compartment. The Seriolella-defined Other demersal fish pool is only a weak coastal-fish analogue, with size and habitat mismatch.',
 'Hoplostethus atlanticus':'Deep-water pelagic fish use Small pelagic fish as the only pelagic fish analogue. Their depth and size are poorly represented by the source pool.',
 'Marine pelagic fishes not identified':'The reporting category is bony fish; Small pelagic fish is the only explicitly pelagic pool. Unknown mixture and unrepresented large predators make the assumed composition uncertain.',
 'Scorpaeniformes':'Historical fisheries scope differs from modern orders. Other demersal fish supplies a weak demersal analogue rather than explicit source membership.',
 'Teuthida':'The historical squid label has unknown species and size composition. Small pelagic fish is a partial active-nekton surrogate with taxonomic, size and feeding mismatch.'
}
fallback='1980 model biomass proportions replace incomplete source catches, assuming regional composition and catchability across years and catch bases.'
for reason,items in grouped.items():
    names={r[0] for r in items}
    concise=next((v for k,v in short_reasons.items() if k in names),None)
    if concise is None:
        if names=={'Actinopterygii'}:concise='Ray-finned fish have unknown composition across named and pooled bony-fish groups; Skates is excluded. '+fallback
        elif names=={'Gadiformes'}:concise='The broad cod-like label mixes named hoki, whiting and hake with unrepresented grenadiers represented only by a demersal analogue. '+fallback
        elif names=={'Malacostraca'}:concise='Unknown crustacean composition spans euphausiid Macrozooplankton and Benthos; copepods are excluded. '+fallback
        elif names=={'Marine groundfishes not identified'}:concise='Bony groundfish have unknown composition across named and pooled demersal groups. Skates and explicitly pelagic Small pelagic fish are excluded. '+fallback
        elif names<={'Marine fishes not identified','Marine finfishes not identified'}:concise='Verified bony-fish reporting scope excludes Skates, but composition across named and pooled fish groups and unrepresented taxa remains unknown. '+fallback
        elif names=={'Mollusca'}:concise='Unknown mollusc composition mixes benthic members with pelagic squid, which uses only a weak fish analogue. '+fallback
        elif names=={'Perciformes'}:concise='Historical fisheries scope is broader than modern orders. Brama-like pelagic and Seriolella-like demersal pools approximate an unknown mixture. '+fallback
        else:raise AssertionError(('Unrecognized exact appendix reason',names))
    grouped[reason]=(items,concise)

template_tables=template.findall('w:body/w:tbl',NS)
decision_template=next(t for t in template_tables if text(t.find('w:tr',NS))=='Affected taxaWhy confidence is very low')
decision=deepcopy(decision_template)
for r in decision.findall('w:tr',NS)[1:]:decision.remove(r)
row_template=decision_template.findall('w:tr',NS)[1]
covered=[]
decision_record=[]
for items,reason in sorted(grouped.values(),key=lambda v:(-sum(r[3] for r in v[0]),v[0][0][0])):
    names=sorted(r[0] for r in items)
    # Bounded rows keep every named decision readable without splitting a row across pages.
    for start in range(0,len(names),18):
        chunk=names[start:start+18]
        row=deepcopy(row_template)
        for c,value in zip(row.findall('w:tc',NS),['; '.join(chunk),reason]):fill_cell(c,[value])
        decision.append(row)
        covered.extend(chunk)
        decision_record.append({'taxa':chunk,'reason':reason})
assert sorted(covered)==sorted(r[0] for r in verylow) and len(set(covered))==121
geo=next(p for p in body.findall('w:p',NS) if text(p)=='Geographic evidence screenshots')
heading=paragraph('Very low decisions',next(p for p in template.findall('w:body/w:p',NS) if text(p)=='Very low decisions'))
percent=paragraph('Each percentage is the independent simple-chain PPR associated with taxa using that rule.',next(p for p in body.findall('w:p',NS) if text(p).startswith('Reference:')))
# Percent definition belongs before the uncertainty paragraph and decision table.
uncertainty=next(p for p in body.findall('w:p',NS) if text(p).startswith('Unresolved taxa:'))
body.insert(body.index(uncertainty),percent)
body.insert(body.index(geo),heading)
body.insert(body.index(geo),decision)

# Retain all original link targets, pictures, styles and manual row XML.
for k in manual:assert canonical(rows[k])==manual_before[k],k
assert sum(r['ppr_percentage'] for r in summary['membership_summary'])-100 < 1e-8
assert abs(sum(r['ppr_percentage'] for r in summary['allocation_summary'])-100)<1e-8
for table in [first,confidence,membership,allocation,decision]:
    header=table.find('w:tr',NS)
    rp=header.find('w:trPr',NS)
    if rp is None:rp=etree.SubElement(header,tag('trPr'))
    if rp.find('w:tblHeader',NS) is None:etree.SubElement(rp,tag('tblHeader'))

out=etree.tostring(xml,encoding='UTF-8',xml_declaration=True,standalone=True)
relpart='word/_rels/document.xml.rels'
rels=etree.fromstring(parts[relpart])
used=set(xml.xpath('//@r:id',namespaces={'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}))
for rel in list(rels):
    if rel.get('Target')=='[Excel_appendix.xlsx]':
        assert rel.get('Id') not in used
        rels.remove(rel)
newparts={**parts,'word/document.xml':out,relpart:etree.tostring(rels,encoding='UTF-8',xml_declaration=True,standalone=True)}
candidate=QA/'updated.docx'
with ZipFile(candidate,'w') as z:
    for info in infos:z.writestr(info,newparts[info.filename])
with ZipFile(candidate) as z:
    changed=[k for k,v in parts.items() if z.read(k)!=v]
assert changed==['word/document.xml',relpart]
assert all(sha(ROOT/k)==v for k,v in protected.items())
shutil.copy2(candidate,REPORT)
record={'unit_id':'LME_013','model_id':'13_1_Chilean_Patagonia_(1980)','template_version':8,'update_date':'2026-10-02','baseline_sha256':sha(QA/'baseline.docx'),'updated_sha256':sha(REPORT),'template_sha256':sha(TEMPLATE),'changed_package_parts':changed,'manual_rows_xml_identical':manual,'protected_inputs_sha256':protected,'very_low_decisions':decision_record,'very_low_taxa_exactly_once':len(covered),'scientific_execution':False,'project_or_map_updated':False,'retained_warning_statuses':{m['method']:m['overall_status'] for m in matrix['methods']},'article_rationale':'not separately recorded; ?','model_rationale_original_text_preserved':True}
(QA/'update_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'changed_package_parts':changed,'manual_rows_preserved':manual,'very_low_taxa':len(covered),'decision_rows':len(decision_record),'report':str(REPORT)},ensure_ascii=False),flush=True)
