import copy, hashlib, json, os, re, sys, zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from lxml import etree as E

RUN=Path(__file__).resolve().parents[1]
VAL=RUN.parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import format_percent, format_report
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'w':W,'r':R}
q=lambda t:f'{{{W}}}{t}'
text=lambda e:''.join(e.itertext())
with zipfile.ZipFile(RUN/'inputs/validation_before.docx') as z:
    parts={n:z.read(n) for n in z.namelist()}
doc=E.fromstring(parts['word/document.xml'])
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
with zipfile.ZipFile(ROOT/'tools/templates/validation.docx') as z:
    template=E.fromstring(z.read('word/document.xml'))
body=doc.find('w:body',NS)
tb=template.find('w:body',NS)
old_children=list(body)
old_tables=body.findall('w:tbl',NS)
template_tables=tb.findall('w:tbl',NS)
fields={}
for t in old_tables[:2]:
    for r in t.findall('w:tr',NS)[1:]:
        cells=r.findall('w:tc',NS)
        fields[text(cells[0])]=copy.deepcopy(r)
def paragraph(s='',style=None):
    p=E.Element(q('p'))
    pp=E.SubElement(p,q('pPr'))
    if style: E.SubElement(pp,q('pStyle')).set(q('val'),style)
    run=E.SubElement(p,q('r')); t=E.SubElement(run,q('t')); t.text=s
    t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    return p
def link(p,label,target):
    rid='rIdReview'+str(len(rels)+1)
    item=E.SubElement(rels,f'{{{PKG}}}Relationship',Id=rid,Type=R+'/hyperlink',Target=target,TargetMode='External')
    h=E.SubElement(p,q('hyperlink'));h.set(f'{{{R}}}id',rid)
    r=E.SubElement(h,q('r'));pr=E.SubElement(r,q('rPr'))
    E.SubElement(pr,q('color')).set(q('val'),'0563C1');E.SubElement(pr,q('u')).set(q('val'),'single')
    E.SubElement(r,q('t')).text=label
def cell_set(cell,lines):
    original=cell.find('w:p',NS)
    pprop=copy.deepcopy(original.find('w:pPr',NS)) if original is not None else None
    rp=original.find('w:r/w:rPr',NS) if original is not None else None
    rprop=copy.deepcopy(rp) if rp is not None else None
    for e in list(cell):
        if e.tag!=q('tcPr'):cell.remove(e)
    for s in lines:
        if isinstance(s,E._Element):cell.append(s);continue
        p=paragraph(s)
        if pprop is not None:p.replace(p.find('w:pPr',NS),copy.deepcopy(pprop))
        if rprop is not None:p.find('w:r',NS).insert(0,copy.deepcopy(rprop))
        cell.append(p)
def field_set(label,lines):cell_set(fields[label].findall('w:tc',NS)[1],lines)
def table_rows(base,headers,rows):
    t=copy.deepcopy(base)
    rr=t.findall('w:tr',NS)
    for r in rr[1:]:t.remove(r)
    for c,s in zip(rr[0].findall('w:tc',NS),headers):cell_set(c,[s])
    for vals in rows:
        row=copy.deepcopy(rr[1]);props=row.find('w:trPr',NS)
        if props is None:props=E.Element(q('trPr'));row.insert(0,props)
        E.SubElement(props,q('cantSplit'))
        for c,s in zip(row.findall('w:tc',NS),vals):cell_set(c,[str(s)])
        t.append(row)
    return t

summary=json.loads((RUN/'qa/mapping_validation_summary.json').read_text(encoding='utf-8'))
coverage=summary['coverage']
diag_path=RUN/'outputs/report_diagnostics.json'
diagnostics=json.loads(diag_path.read_text(encoding='utf-8')) if diag_path.exists() else None
if diagnostics is None:raise RuntimeError('Fresh diagnostic report text is required before authoring')

p=paragraph('Koen-Alonso & Yodzis (2005), Multispecies modelling of northern and central Patagonia, Argentina; 1990s. ')
link(p,'DOI','https://doi.org/10.1139/f05-087')
p2=paragraph('Ocampo Reinaldo et al. (2016), Assessing the effects of demersal fishing and conservation strategies of marine mammals over a Patagonian food web; San Matías Gulf, 1970 baseline. ')
link(p2,'Source PDF','../../../../LME014-OcampoReinaldo-2016/sources/Assessing-the-effects-of-demersal-fishing--e228101d.pdf')
field_set('Other known articles',[p,p2])
field_set('Selection rationale',[
    'Article: ?',
    'Model: The researcher selected the native-source reconstruction because it did not FAIL. The recorded GE, TE and With Egestion diagnostics were WARN, not OK. The audited coupled Ecopath solution completes only source-missing living/producer B and EE. Native discard routing, loader-derived detritus accumulation and transfer from the Falkland shelf subregion remain limitations.'
])
# Keep existing selected-model links and clarify that the software version describes the database.
c=fields['Selected model'].findall('w:tc',NS)[1]
for n in c.findall('.//w:t',NS):
    if n.text:n.text=n.text.replace('EwE 6.6.8.18072','native database EwE 6.6.8.18072')
field_set('GE diagnostics',diagnostics['GE'])
field_set('TE diagnostics',diagnostics['TE'])
p=paragraph('EE floor ON at 0.1 after the audited initialization; this introduces a hypothetical external nonfishery mortality sink. The diagnostics above describe this configuration. Saved regional results and the earlier With Egestion diagnostic retain their historical configuration. ')
link(p,'EE-floor findings and complete diagnostic evidence','evidence/ee_floor_on_review/review_summary.json')
field_set('Other',[p,'The floor affects eight groups and redirects 65.52 model flow units to the external sink, principally from Kelp; living biological flows and catch are preserved. Sharks (27) retains the largest TE coefficient, 399,038.26. Historical regional exposure percentages do not describe this configuration.'])
field_set('Geographic fit',[
    'A — region covered by study: approximately 17%.',
    'B — study covered by region: approximately 100% (conditional estimates).'
])
field_set('Temporal fit',['The model represents 2020. Applying fixed coefficients and allocation weights to regional catch for 1950–2019 assumes that trophic relationships and catch composition are transferable across years; annual historical ecosystem changes are not represented.'])

# One flowing main table, current template order; manual row XML is retained intact.
main=copy.deepcopy(template_tables[0])
for r in main.findall('w:tr',NS)[1:]:main.remove(r)
order=[text(r.findall('w:tc',NS)[0]) for r in template_tables[0].findall('w:tr',NS)[1:]]
for label in order:
    row=fields[label]
    if label not in ['SPPR calculation','Open issues and next action','Review and reproducibility']:
        for e in row.findall('w:trPr/w:cantSplit',NS):e.getparent().remove(e)
        for p in row.findall('.//w:p',NS):
            for e in p.findall('w:pPr/w:pageBreakBefore',NS):e.getparent().remove(e)
    main.append(row)
    if label in ['GE diagnostics','TE diagnostics']:
        paragraphs=row.findall('w:tc',NS)[1].findall('w:p',NS)
        for p in paragraphs[:-1]:
            pp=p.find('w:pPr',NS)
            if pp is None:pp=E.Element(q('pPr'));p.insert(0,pp)
            E.SubElement(pp,q('keepNext'))

membership={
'M1':'Explicit named member of the final source model.',
'M11':'Closest represented taxonomic or ecological analogue, with a documented mismatch.',
'M9':'Supported broader reporting label or combination of named source taxa.',
'M10':'Broad reporting category approximated across plausible represented groups.',
'M4':'Supported extension from related source genera, families or orders.',
'M3':'Unambiguous fit to the explicit bivalve and scallop definition of Small Zoobenthos.'}
allocation={'W1':'One supported group; no allocation split is required.','W4':'Complete native 2020 catch proportions; Doryteuthis gahi retains the source cohort landings split.','W5':'Identified regional hake proportions transferred across differing reporting populations.'}
confidence=table_rows(template_tables[1],['Overall confidence','Taxa (n)','Catch (%)','Simple-chain PPR (%)'],[
    [r['label'],r['taxa'],format_percent(r['catch_percentage']),format_percent(r['ppr_percentage'])] for r in coverage['confidence_summary']])
memtable=table_rows(template_tables[2],['Plain-language rule','Confidence','PPR percentage'],[
    [membership[r['rule']],r['confidence'],format_percent(r['ppr_percentage'])] for r in sorted(coverage['membership_summary'],key=lambda x:-x['ppr_percentage'])])
alloctable=table_rows(template_tables[3],['Plain-language rule','Confidence','PPR percentage'],[
    [allocation[r['rule']],r['confidence'],format_percent(r['ppr_percentage'])] for r in coverage['allocation_summary']])
vl_rows=[]
for row in summary['very_low_reason_groups']:
    # Preserve the exact model-specific evidence, removing only internal rule-code/source navigation prose.
    reason=row['reason']
    reason=re.sub(r'\b(?:allocation )?W4 is Medium\.', 'The source-catch allocation has Medium confidence.',reason)
    reason=re.sub(r'\s*Sources:.*$', '',reason)
    reason=reason.replace('native2020','native 2020').replace('across1950','across 1950').replace('Myctophidae18','Myctophidae 18')
    reason=reason.replace('juvenileToothfish','juvenile Toothfish').replace('in24 and29','in groups 24 and 29').replace('; The source-catch','; the source-catch')
    reason=reason.replace('Extreme source TE coefficient is preserved and exposure disclosed.', 'The Sharks TE coefficient remains large under the EE floor; historical exposure is a separate result.')
    vl_rows.append(['; '.join(row['taxa']),reason])
verylow=table_rows(template_tables[4],['Affected taxa','Why confidence is very low'],vl_rows)
# Balance the long scientific taxon lists and the reasons while retaining template typography.
for col,width in zip(verylow.findall('w:tblGrid/w:gridCol',NS),[4320,5717]):col.set(q('w'),str(width))
for row in verylow.findall('w:tr',NS):
    for cell,width in zip(row.findall('w:tc',NS),[4320,5717]):
        cell.find('w:tcPr/w:tcW',NS).set(q('w'),str(width))

for child in list(body):body.remove(child)
body.append(paragraph('Patagonian Shelf model validation','Title'))
body.append(paragraph('LME_014 · Falkland Shelf 2020 · EE floor ON at 0.1'))
body.append(main)
h=paragraph('Taxon mapping and coverage','Heading1');E.SubElement(h.find('w:pPr',NS),q('pageBreakBefore'));body.append(h)
body.append(paragraph('Reference: 2019 landings; all catch labels, including zero and unidentified categories; no group filter.'))
body.append(paragraph('36 source groups (+1 computational import); 250 exact catch labels.'))
body.append(paragraph('Simple-chain PPR totals 142,458,248.78 t C in 2019.'))
body.append(paragraph('55 labels lack a saved classic coefficient/TL; all have zero 2019 landings and contribute zero annual PPR. Their TL remains unavailable.'))
body.append(paragraph('Method: independent simple trophic chain.'))
p=paragraph();link(p,'Taxon mapping appendix and descriptive Sources sheet','taxon_mapping.xlsx');body.append(p)
body.append(confidence)
body.append(paragraph('Overall confidence is the weaker required membership or allocation component.'))
body.append(paragraph('Group assignment rules','Heading2'));body.append(memtable)
p=paragraph('Membership evidence: ');link(p,'source definitions and all candidate decisions','evidence/source_review/taxon_audit.json');body.append(p)
body.append(paragraph('Allocation weight rules','Heading2'));body.append(alloctable)
p=paragraph('Weights and assumptions: complete native fleet landings plus discards provide the fixed composition proxy, retaining genuine zero candidates. Doryteuthis gahi retains the cohort landings split. The Merluccius split has Low confidence because target and donor country, gear and reporting populations differ. ')
link(p,'Allocation evidence','evidence/source_review/allocation_evidence.json');body.append(p)
body.append(paragraph('Each rule percentage is the share of independent simple-chain PPR associated with taxa using that rule.'))
body.append(paragraph('Unresolved taxa: none. The 196 Very low decisions represent 33% of landings and 6.2% of simple-chain PPR. Broad reporting composition and weak taxonomic, habitat or geographic analogues remain assumptions; complete mapping does not establish ecological validity.'))
body.append(paragraph('Very low decisions','Heading2'));body.append(verylow)
h=paragraph('Geographic evidence','Heading1');E.SubElement(h.find('w:pPr',NS),q('pageBreakBefore'));body.append(h)
body.append(paragraph('Target region R and selected model study area S. The overlap estimates are conditional on the reported study area lying nearly wholly within the target region.'))
body.append(paragraph('Region area','Heading2'));body.append(copy.deepcopy(old_tables[5]))
p=paragraph('Sea Around Us Patagonian Shelf boundary; geodesic area 1,170,516 km². The blue outline is the target region and the point locates the Falkland Islands. ')
link(p,'Target boundary','evidence/source_review/geography/target_region_boundary.geojson');body.append(p)
h=paragraph('Study area in the article','Heading2');E.SubElement(h.find('w:pPr',NS),q('pageBreakBefore'));body.append(h);body.append(copy.deepcopy(old_tables[6]))
p=paragraph('Büring et al. (2024), Figure 1, PDF p.3: sampling locations and conservation zones. These outlines do not delimit the ≤300 m Ecopath model domain. Source p.6 reports approximately 200,000 km²; assuming nearly all lies in the target gives A ≈ 17% and B ≈ 100%. These are reported-area estimates, not measured polygon intersections. ')
link(p,'Source domain','evidence/source_review/geography/source_domain_passage.txt');body.append(p)
p=paragraph('A verified study polygon remains unavailable. The inherited rectangle is not the source shelf boundary. ')
link(p,'Geographic assessment','evidence/source_review/geography/geographic_assessment.json');body.append(p)
body.append(copy.deepcopy(old_children[-1]))

# Every visible link is explicitly styled; preserve all existing targets except verified relocations.
for h in doc.findall('.//w:hyperlink',NS):
    label=''.join(h.itertext())
    if label in ['Canonical source','Model folder','Model inventory']:
        rel=next(x for x in rels if x.get('Id')==h.get(f'{{{R}}}id'))
        rel.set('Target',{'Canonical source':'../model.json','Model folder':'..','Model inventory':'../../../source_manifest.json'}[label])
    for r in h.findall('.//w:r',NS):
        pr=r.find('w:rPr',NS)
        if pr is None:pr=E.Element(q('rPr'));r.insert(0,pr)
        for tag,val in [('color','0563C1'),('u','single')]:
            e=pr.find('w:'+tag,NS)
            if e is None:e=E.SubElement(pr,q(tag))
            e.set(q('val'),val)
            for k in list(e.attrib):
                if 'theme' in k:del e.attrib[k]
for rel in rels:
    target=rel.get('Target','')
    if target=='../../../../../../../LME_014/raw':
        rel.set('Target',os.path.relpath(ROOT/'regions/LME/LME_014/raw',VAL).replace('\\','/'))
    if '/research/' in target and '/research/agents/' not in target:
        repaired=target.replace('/research/','/research/agents/')
        if (VAL/unquote(repaired)).exists():rel.set('Target',repaired)
used={h.get(f'{{{R}}}id') for h in doc.findall('.//w:hyperlink',NS)}
for rel in list(rels):
    if rel.get('Type','').endswith('/hyperlink') and rel.get('Id') not in used:rels.remove(rel)

parts['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/_rels/document.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
out=VAL/'validation.docx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in parts.items():z.writestr(name,data)
format_report(out)
print(out)
