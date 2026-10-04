from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from collections import Counter
import json, hashlib, math, sys
from urllib.parse import unquote, urlsplit
from lxml import etree as E
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[6]
REGION = ROOT / 'regions/LME_035'
EVIDENCE = REGION / 'validation_reports/35_412_Gulf_of_Thailande_(1963)'
QA = Path(__file__).resolve().parent
DOC = REGION / 'Model_validation_35_412_Gulf_of_Thailande_(1963).docx'
BASE = QA / ('baseline_' + DOC.name)
TEMPLATE = ROOT / 'tools/templates/Model_validation_template.docx'
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W = '{' + NS['w'] + '}'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text(e): return ''.join(e.xpath('.//w:t/text()',namespaces=NS))
def canonical(e): return E.tostring(e, method='c14n')
def set_text(e, value):
    drawings=[deepcopy(r) for r in e.findall(W+'r') if r.find(W+'drawing') is not None]
    runs=e.findall(W+'r'); first=runs[0] if runs else None
    props=deepcopy(first.find(W+'rPr')) if first is not None and first.find(W+'rPr') is not None else None
    for ch in list(e):
        if ch.tag != W+'pPr': e.remove(ch)
    r=E.SubElement(e,W+'r')
    if props is not None: r.append(props)
    t=E.SubElement(r,W+'t'); t.text=value
    t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    for r in drawings: e.append(r)
def set_cell(e, lines):
    p=e.find(W+'p'); pattern=deepcopy(p)
    for ch in list(e):
        if ch.tag!=W+'tcPr': e.remove(ch)
    for line in lines:
        np=deepcopy(pattern); set_text(np,line); e.append(np)
def load_json(n): return json.loads((EVIDENCE/n).read_text('utf-8'))

if not BASE.exists(): BASE.write_bytes(DOC.read_bytes())
protected=[REGION/'LME_035.xlsx', REGION/'LME035_taxon_mapping_appendix.xlsx',
           REGION/'models/35_412_Gulf_of_Thailande_(1963)/model.json',
           ROOT/'Project.xlsx', ROOT/'interactive_map/index.html',
           ROOT/'tools/knowledge_graph/graph.json', TEMPLATE]
hash_file=QA/'protected_hashes.json'
if not hash_file.exists():
    hash_file.write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in protected},indent=2),encoding='utf-8')
before=json.loads(hash_file.read_text('utf-8'))
audit=load_json('taxon_audit.json'); summary=load_json('coverage_summary.json')
assert len(audit)==247 and len({r['taxon'] for r in audit})==247
assert sha(REGION/'LME_035.xlsx')==load_json('canonical_reader_verification.json')['workbook_sha256']
assert sha(REGION/'models/35_412_Gulf_of_Thailande_(1963)/model.json')==load_json('direct_diagnostics/execution_evidence.json')['canonical_sha256']
# Reopen the retained appendix and verify all rows and exact unrounded arithmetic.
book=load_workbook(REGION/'LME035_taxon_mapping_appendix.xlsx',read_only=True,data_only=False)
rows=list(book['Taxon mapping'].values)
assert rows[6][:7]==('Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason')
data=[r[:7] for r in rows[7:] if r[0] is not None]
assert len(data)==247
by_taxon={r['taxon']:r for r in audit}
for row in data:
    r=by_taxon[row[0]]
    assert row[5]==r['overall_confidence']
    assert row[4]==r['mapping_display']
    assert math.isclose(row[2],r['catch_tonnes'],rel_tol=1e-14,abs_tol=1e-12)
    assert math.isclose(row[3],r['simple_chain_ppr_tC'],rel_tol=1e-14,abs_tol=1e-12)
    expected=0 if r['catch_tonnes']==0 else r['catch_tonnes']*r['classic_sppr']/9
    assert math.isclose(row[3],expected,rel_tol=1e-13,abs_tol=1e-12)
assert [r[0] for r in data]==[r['taxon'] for r in sorted(audit,key=lambda r:(-r['simple_chain_ppr_tC'],r['taxon']))]
assert math.isclose(sum(r[3] for r in data),summary['total_simple_chain_ppr_tC'],rel_tol=1e-14)
assert Counter(r[5] for r in data)==Counter({r['label']:r['taxa'] for r in summary['confidence_summary'] if r['taxa']})
for name in ['membership_summary','allocation_summary']:
    assert abs(sum(r['ppr_percentage'] for r in summary[name])-100)<1e-8
book.close()
solutions=load_json('direct_diagnostics/direct_solutions.json')
diagnostics=load_json('matrix_inspection.json')
matrix_checks={}
for method in ['GE','TE']:
    m=solutions[method]['SPPR']
    assert len(m['index'])==len(set(m['index']))==30
    assert len(m['columns'])==len(set(m['columns']))==3
    assert len(m['data'])==30 and all(len(row)==3 for row in m['data'])
    assert all(isinstance(x,(float,int)) and math.isfinite(x) and x>=0 for row in m['data'] for x in row)
    match=next(r for r in diagnostics['methods'] if r['method']==method)
    assert match['full_return']['divergence']['n_negative_sources']==0
    matrix_checks[method]={'shape':[30,3],'negative_entries':0,'nonfinite_entries':0,'status':match['status']}

with ZipFile(BASE) as z:
    parts={n:z.read(n) for n in z.namelist()}; infos=z.infolist()
doc=E.fromstring(parts['word/document.xml']); body=doc.find(W+'body')
tables=body.findall(W+'tbl'); main,second,confidence,membership,allocation=tables[:5]
original_rows={text(row.findall(W+'tc')[0]):row for t in [main,second] for row in t.findall(W+'tr')[1:]}
manual_keys=['SPPR calculation','Open issues and next action','Review and reproducibility','Selection rationale']
manual={k:canonical(original_rows[k]) for k in manual_keys}
header=main.find(W+'tr')
for row in list(main.findall(W+'tr'))[1:]: main.remove(row)
order=['Region','Catch source','Selected article','Other known articles','Selected model',
       'Other models from the same article','Selection rationale','Model extraction','GE diagnostics',
       'TE diagnostics','SPPR calculation','Geographic fit','Temporal fit','Other',
       'Open issues and next action','Review and reproducibility']
for name in order: main.append(original_rows[name])
# Remove only the old table separator and second table.
separator=main.getnext()
assert separator.tag==W+'p' and not text(separator)
body.remove(separator); body.remove(second)
for row in main.findall(W+'tr'):
    if text(row.findall(W+'tc')[0]) in manual_keys: continue
    prop=row.find(W+'trPr')
    if prop is not None:
        for item in list(prop):
            if item.tag in [W+'cantSplit',W+'trHeight']: prop.remove(item)
hp=header.find(W+'trPr')
if hp is None: hp=E.SubElement(header,W+'trPr')
if hp.find(W+'tblHeader') is None: E.SubElement(hp,W+'tblHeader')
set_text(body.find(W+'p'),'Gulf of Thailand model validation')
for method in ['GE','TE']:
    r=next(v for v in diagnostics['methods'] if v['method']==method)
    lines=['WARN: Jellyfish (18) and M. mammals (1) have EE = 0.',
           'No negative SPPR entries across the basal-source columns.',
           f"rho_living = {r['rho_living']:.4f}"]
    if method=='GE': lines.append(f"b = {r['b']:.4f}")
    lines.append(f"Detritus (29): SPPR = {r['detritus_sppr']['29']:.4f}")
    set_cell(original_rows[method+' diagnostics'].findall(W+'tc')[1],lines)
set_cell(original_rows['Geographic fit'].findall(W+'tc')[1],[
    'A. Region covered by the focal 10–50 m study: not determined.',
    'B. Focal study area covered by the region: not determined.',
    'The original focal boundary is unavailable; the contextual estimates are shown with the figures below.'])
set_cell(original_rows['Catch source'].findall(W+'tc')[1],[
    'Sea Around Us v50.1; local 1950–2019 catch; reference: 2019 landings. '])
# Restore the existing local catch link without changing its relationship.
oldcatch=E.fromstring(parts['word/document.xml']).xpath('.//w:hyperlink[@r:id="rId10"]',namespaces=NS)[0]
original_rows['Catch source'].findall(W+'tc')[1].find(W+'p').append(deepcopy(oldcatch))
for node in body.findall(W+'p'):
    s=text(node)
    if s.startswith('Reference:2019'):
        set_text(node,'Reference: 2019 landings; all taxon labels, including zero catch and unidentified categories; no group filter.')
    elif s.startswith('29 source ecological'):
        set_text(node,'29 source ecological groups (+1 computational import); 247 catch taxa.')
    elif s.startswith('33 labels lack'):
        set_text(node,'33 labels lack a classic TL/coefficient; all have zero 2019 landings and contribute zero annual PPR.')
    elif s.startswith('Method: independent'):
        set_text(node,'Method: independent simple trophic chain.')
    elif s.startswith('The summary uses'):
        set_text(node,'Overall confidence uses the weaker required membership or allocation component.')
    elif s.startswith('Membership evidence:'):
        for t in node.xpath('.//w:t',namespaces=NS):
            if t.text=='focalp130 and identity': t.text='Christensen (1998), p.130 and model identity'
            elif t.text=='predecessor Table2': t.text='Pauly & Christensen (1993), Table 2'
    elif s.startswith('Percentages are simple-chain'):
        # Keep the existing evidence hyperlink, shorten only its explanatory prose.
        first=node.find(W+'r')
        first.find(W+'t').text=('Each percentage is the independent simple-chain PPR associated with taxa using that rule. '
            'The 1980 model-catch proportions, including zero candidates, are fixed composition proxies. '
            'Historical identified-catch proxies remain Low because donor populations and gear differ. ')
    elif s.startswith('Unresolved: none.'):
        for t in node.findall('.//'+W+'t'):
            if t.text and t.text.startswith('Unresolved: none.'):
                t.text=('Unresolved taxa: none. The 34 Very low decisions cover 12.9493% of landings and 12.0040% of '
                        'simple-chain PPR. Their specific uncertainties appear below. Very low decisions contribute '
                        '14.12% of GE, 12.01% of TE and 13.86% of With Egestion all-source PPR; '
                        'Carangidae alone contributes 7.93% of GE. ')
    elif s.startswith('R is the Sea Around Us target.'):
        set_text(node,'Target region R is the Sea Around Us LME. The focal source specifies a 10–50 m shelf domain, '
                 'but its original study boundary is unavailable. Pauly & Chuenpagdee (2003), Figure 14-1, '
                 'provides contextual geography; its illustrative trace does not establish the focal study extent.')
    elif s.startswith('Target R:387'):
        for t in node.findall('.//'+W+'t'):
            if t.text and t.text.startswith('Target R:387'):
                t.text=('Target R: 387,239 km². Blue shows the target; orange shows an approximate contextual shelf '
                        'trace within the lineage map boundary. Coastline and islands are simplified. ')
    elif s.startswith('Contextual trace:112'):
        for t in node.findall('.//'+W+'t'):
            if t.text and t.text.startswith('Contextual trace:112'):
                t.text=('Contextual trace: 112,695 km²; intersection: 102,520 km². Contextual A ≈ 26.5%; B ≈ 91.0%. '
                        'The reported larger 0–50 m band (≈150,000 km², ≈38.7% of R) is separate area context. '
                        'Neither identifies the missing focal 10 m boundary or full study extent. ')
    elif s.startswith('Original lineage Figure'):
        set_text(node,'Contextual Figure 14-1 from Pauly & Chuenpagdee (2003), printed p.338 / PDF p.2. '
                 'Its 50 m contour and angular location boundary do not constitute the original focal study map.')
for c,label in zip(confidence.find(W+'tr').findall(W+'tc'),['Overall confidence','Taxa (n)','Catch (%)','Simple-chain PPR (%)']):
    set_cell(c,[label])
# Correct inherited spacing in automatic fields without rebuilding links or manual rows.
replacements={'V.(1998)':'V. (1998)','53(Suppl. A):128':'53 (Suppl. A): 128',
              'Christensen(1993)':'Christensen (1993)','al.(2003)':'al. (2003)',
              'Premcharoen(2012)':'Premcharoen (2012)','TableII':'Table II',
              '1980.29':'1980. 29','groups(+1':'groups (+1',
              'import);10':'import); 10','supplied.1993':'supplied. 1993','twoEE 0':'two EE = 0'}
for key,row in original_rows.items():
    if key in manual_keys: continue
    for t in row.xpath('.//w:t',namespaces=NS):
        if t.text:
            for a,b in replacements.items(): t.text=t.text.replace(a,b)

# Concise region-specific explanations, keyed to the exact current appendix taxa.
decision_groups=[
(['Carangidae'],'Scad explicitly includes Decapterus; larger predators use the large-piscivore stage pair as an analogue. The reported jacks/pompanos mixture is unknown. Model-catch proportions assume fixed 1980 composition.'),
(['Marine fishes not identified'],'Unidentified bony fish may span named, residual and juvenile pools. Separate reported categories do not establish exclusions; species and stage composition is unknown. Model-catch proportions are a fixed 1980 proxy.'),
(['Serranidae'],'The historical basses/groupers category includes Epinephelus, now Epinephelidae, while other basses are unlisted. The grouper/snapper stage union is a proxy for an unresolved taxonomic and feeding mixture; model-catch proportions are assumed.'),
(['Alepes'],'Scad provides a coastal schooling Decapterus connection, but reef habitat, feeding and species composition differ. No direct source membership is documented; the whole taxon is placed in Scad.'),
(['Marine groundfishes not identified'],'Plausible demersal and juvenile pools are retained, but the large-piscivore pool also contains pelagic Chirocentrus/Sphyraena. Unknown residual composition and mixed guilds require fixed 1980 model-catch proportions.'),
(['Caesio','Caesionidae'],'Small pelagics provides a coastal schooling sardine/anchovy connection. Reef habitat, feeding and species composition differ; fusiliers are not directly named. The whole taxon is placed in that analogue.'),
(['Acanthurus','Mugil','Mugilidae','Scarus','Scatophagus','Scatophagus argus','Siganidae','Siganus','Siganus canaliculatus'],'These unlisted coastal herbivores/omnivores have a residual-catch connection to O.fish (trash fish). Its species composition and feeding fit are unverified. Named piscivore/benthivore pools offer weaker connections; each whole taxon is assigned to O.fish.'),
(['Perciformes'],'The historical perch-like reporting category spans scombrids, carangids and reef/demersal guilds; the current narrow order does not define that mixture. Source piscivore pools also include other orders. Model-catch proportions assume fixed composition.'),
(['Chondrichthyes'],'Shark stages and rays approximate the reporting category; chimaeras have no documented source group. Species/stage composition is unknown. Historical whole-guild donor fractions have country, gear and period mismatches and remain Low allocation proxies.'),
(['Decapoda','Malacostraca','Miscellaneous aquatic invertebrates','Miscellaneous marine crustaceans','Mollusca'],'Compatible named invertebrate, benthic and planktonic stage pools provide a practical connection. The full reported composition is unenumerated, so eligible pools and species/stage mix are approximate. Fixed 1980 model-catch proportions are assumed.'),
(['Coryphaena hippurus'],'The large-predator stage pair connects to source coastal piscivores, but dolphinfish is unlisted and Tuna is a plausible competing pelagic analogue. Surface habitat and source composition differ. The accepted stage split uses fixed 1980 model-catch proportions.'),
(['Istiompax indica','Istiophoridae','Istiophorus','Istiophorus platypterus','Kajikia audax','Makaira','Makaira mazara','Tetrapturus angustirostris','Xiphias gladius'],'The 1993 predecessor places billfish with tuna in Large pelagics, supporting a crosswalk to focal Tuna. Focal members are coastal tuna examples; oceanic/deeper habitat and narrower taxonomy limit the analogy. No focal billfish membership or donor coefficients are implied.'),
(['Marine pelagic fishes not identified'],'Named pelagic pools and mixed guilds containing Chirocentrus/Sphyraena or Pampus provide positive source connections. The full residual species/stage mixture is unknown; explicit demersal exclusions do not remove mixed-guild uncertainty. Fixed 1980 model-catch proportions are assumed.')]
listed=[t for taxa,reason in decision_groups for t in taxa]
assert len(listed)==len(set(listed))==34
assert set(listed)=={r[0] for r in data if r[5]=='Very low'}
with ZipFile(TEMPLATE) as z: td=E.fromstring(z.read('word/document.xml'))
vlt=next(t for t in td.findall('.//'+W+'tbl') if text(t.find(W+'tr')).startswith('Affected taxa'))
newtable=deepcopy(vlt); rowpattern=deepcopy(newtable.findall(W+'tr')[1])
for row in list(newtable.findall(W+'tr'))[1:]: newtable.remove(row)
for taxa,reason in decision_groups:
    row=deepcopy(rowpattern)
    for c,value in zip(row.findall(W+'tc'),['; '.join(taxa),reason]): set_cell(c,[value])
    rp=row.find(W+'trPr')
    if rp is None: rp=E.SubElement(row,W+'trPr')
    if rp.find(W+'cantSplit') is None: E.SubElement(rp,W+'cantSplit')
    newtable.append(row)
geo=next(p for p in body.findall(W+'p') if text(p)=='Geographic evidence screenshots')
heading=deepcopy(next(p for p in body.findall(W+'p') if text(p)=='Group assignment rules'))
set_text(heading,'Very low decisions'); geo.addprevious(heading); geo.addprevious(newtable)
# Page breaks outside the main table, following the v8 template.
pagebreak=E.Element(W+'p'); E.SubElement(E.SubElement(pagebreak,W+'r'),W+'br').set(W+'type','page')
coverage=next(p for p in body.findall(W+'p') if text(p)=='Taxon mapping and coverage')
coverage.addprevious(deepcopy(pagebreak)); geo.addprevious(deepcopy(pagebreak))
for key in manual_keys:
    assert canonical(original_rows[key])==manual[key],key
baseline_xml=E.fromstring(parts['word/document.xml'])
assert [canonical(d) for d in baseline_xml.findall('.//'+W+'drawing')]==[canonical(d) for d in doc.findall('.//'+W+'drawing')]
# Explicit hyperlink appearance and remove only an unused template placeholder relationship.
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
used={h.get('{'+NS['r']+'}id') for h in doc.findall('.//'+W+'hyperlink')}
for rel in list(rels):
    if rel.get('Id')=='rIdValidation1' and rel.get('Id') not in used: rels.remove(rel)
for h in doc.findall('.//'+W+'hyperlink'):
    for r in h.findall(W+'r'):
        rp=r.find(W+'rPr')
        if rp is None: rp=E.Element(W+'rPr'); r.insert(0,rp)
        for tag,val in [('color','0563C1'),('u','single')]:
            node=rp.find(W+tag)
            if node is None: node=E.SubElement(rp,W+tag)
            node.set(W+'val',val)
            for attr in list(node.attrib):
                if 'theme' in attr.lower(): del node.attrib[attr]
link_checks=[]
for rel in rels:
    if not rel.get('Type','').endswith('/hyperlink'): continue
    target=rel.get('Target'); scheme=urlsplit(target).scheme
    if scheme in ['https','http','mailto']: continue
    assert not scheme and not target.startswith(('/', '\\'))
    path=unquote(target.split('#')[0]); resolved=(REGION/path).resolve()
    assert resolved.is_relative_to(ROOT) and resolved.exists(),target
    link_checks.append(target)
for n in ['docProps/app.xml','docProps/custom.xml']:
    if n in parts: assert b'HyperlinkBase' not in parts[n] or b'<HyperlinkBase/>' in parts[n]
changed={'word/document.xml':E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True),
         'word/_rels/document.xml.rels':E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
with ZipFile(DOC,'w') as z:
    for info in infos: z.writestr(info,changed.get(info.filename,parts[info.filename]))
with ZipFile(DOC) as z:
    unchanged_parts=[n for n in parts if n not in changed]
    assert all(z.read(n)==parts[n] for n in unchanged_parts)
after={str(p.relative_to(ROOT)):sha(p) for p in protected}; assert before==after
proof={'date':'2026-10-02','scope':'DOCX template-v8 update only; saved evidence and report arithmetic; no scientific run or map refresh',
       'model_id':summary['model_id'],'scientific_period':1980,'year':2019,'basis':'landings',
       'template_sha256':sha(TEMPLATE),'baseline_docx_sha256':sha(BASE),'output_docx_sha256':sha(DOC),
       'manual_rows_preserved':manual_keys,'unchanged_package_parts':unchanged_parts,
       'only_edited_package_parts':list(changed),'protected_inputs_and_outputs_unchanged':before,
       'all_three_original_drawings_preserved':True,
       'appendix_rows_verified':247,'very_low_taxa_exactly_once':34,'very_low_decision_rows':13,
       'total_simple_chain_ppr_tC':summary['total_simple_chain_ppr_tC'],'component_tables_sum_to_100':True,
       'saved_matrix_checks':matrix_checks,'portable_local_links_verified':link_checks,
       'scientific_gaps_preserved':['Original focal PDF','Complete published input and diet tables','Original focal study boundary','Original EwE archive'],
       'visual_qa':'pending'}
(QA/'verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:proof[k] for k in ['manual_rows_preserved','only_edited_package_parts','appendix_rows_verified','very_low_taxa_exactly_once','total_simple_chain_ppr_tC','saved_matrix_checks']},indent=2))
