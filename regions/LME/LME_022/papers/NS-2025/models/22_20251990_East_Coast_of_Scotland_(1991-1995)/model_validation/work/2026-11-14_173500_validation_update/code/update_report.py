from pathlib import Path
from copy import deepcopy
from urllib.parse import urlsplit,unquote
import hashlib,json,sys,zipfile
from lxml import etree as E
sys.stdout.reconfigure(encoding='utf-8')
run=Path(__file__).resolve().parents[1]; model=run.parents[2]
root=next(p for p in run.parents if (p/'Project.xlsx').exists()); sys.path.insert(0,str(root))
from tools.project_core.validation.validation_percentage_format import format_report,verify_report,format_percent
from tools.project_core.validation.researcher_review import read_report
original=run/'inputs/validation_before.docx'; report=model/'model_validation/validation.docx'
handoff=json.loads((model/'model_validation/work/2026-11-14_180000_appendix_review/outputs/report_handoff.json').read_text(encoding='utf-8'))
diagnostics=model/'results/diagnostics/2026-11-14_171200_seabird_derived_ba'
relrun='../results/diagnostics/2026-11-14_171200_seabird_derived_ba/'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W=ns['w']; R=ns['r']; REL='http://schemas.openxmlformats.org/package/2006/relationships'
def q(s): return '{'+W+'}'+s
def text(e): return ''.join(e.itertext())
with zipfile.ZipFile(original) as z:
    parts=[(i,z.read(i.filename)) for i in z.infolist()]
partmap={i.filename:d for i,d in parts}
x=E.fromstring(partmap['word/document.xml']); rels=E.fromstring(partmap['word/_rels/document.xml.rels']); body=x.find('w:body',ns)
tables=body.findall('w:tbl',ns); first,second=tables[:2]
rows={text(c[0]):r for t in tables[:2] for r in t.findall('w:tr',ns) if len(c:=r.findall('w:tc',ns))==2 and text(c[0])!='Field'}
manual_keys=['SPPR calculation','Open issues and next action','Review and reproducibility']
manual_before={k:E.tostring(rows[k].findall('w:tc',ns)[1]) for k in manual_keys}
existing_body_paragraphs=body.findall('w:p',ns)
def newrun(value,bold=False):
    r=E.Element(q('r')); pr=E.SubElement(r,q('rPr'))
    if bold: E.SubElement(pr,q('b'))
    t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=value
    return r
def paragraph(value='',prototype=None):
    p=E.Element(q('p'))
    if prototype is not None and (pr:=prototype.find('w:pPr',ns)) is not None:p.append(deepcopy(pr))
    p.append(newrun(value)); return p
def set_paragraph(p,value):
    for c in list(p):
        if c.tag!=q('pPr'):p.remove(c)
    p.append(newrun(value))
def link(p,label,target):
    ids={r.get('Id') for r in rels}; i=100
    while 'rId'+str(i) in ids:i+=1
    rid='rId'+str(i)
    E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/hyperlink',Target=target,TargetMode='External')
    h=E.SubElement(p,q('hyperlink'));h.set('{'+R+'}id',rid)
    r=newrun(label);rp=r.find('w:rPr',ns);E.SubElement(rp,q('color')).set(q('val'),'0563C1');E.SubElement(rp,q('u')).set(q('val'),'single');h.append(r)
def set_cell(row,paragraphs,links=None):
    c=row.findall('w:tc',ns)[1]; proto=c.find('w:p',ns)
    for child in list(c):
        if child.tag!=q('tcPr'):c.remove(child)
    for s in paragraphs:c.append(paragraph(s,proto))
    if links:
        p=paragraph('',proto)
        for i,(label,target) in enumerate(links):
            if i:p.append(newrun(' | '))
            link(p,label,target)
        c.append(p)
def change_label(old,new):
    set_paragraph(rows[old].findall('w:tc',ns)[0].find('w:p',ns),new)
change_label('Selected model','Candidate model');change_label('Selected article','Candidate article')
set_paragraph(existing_body_paragraphs[0],'Scotland candidate model validation')
set_cell(rows['Selected model'],[
    model.name+'; East Coast of Scotland, 1991–1995. 25 ecological groups plus synthetic diet_import, all retained.',
    'Candidate correction review. Overview currently selects ICES_WGSAM2015_North_Sea_1991; this report and its runtime correction concern Scotland only.'],
    [('Canonical source model','../model.json'),('Model folder','..')])
set_cell(rows['Other models from the same article'],[
    'The article also presents an 1890–1895 East Coast Scotland static model with the same 25-group topology. It is a separate unselected candidate. Historical data do not support multistanza groups.'],
    [('1890s canonical model','../../22_20251890_East_Coast_of_Scotland_(1890-1895)/model.json'),('Source review','evidence/source_review/source_review.md')])
set_cell(rows['Selection rationale'],[
    'Article: ? (no separate article-choice rationale recorded).',
    'Model: explicitly named candidate for the seabird correction. The earlier report records: “User previously preferred this exact model for the least SPPR failures.” That historical preference does not describe the current ICES selection.'])
set_cell(rows['Model extraction'],[
    'The publication and canonical model are preserved. The retained audit matched 97 core parameters, 232 diet cells and 775 roundtrip values; prior diet normalization, GS defaults and residual BA completion remain documented.',
    'Derived runtime correction: source seabird self-diet 0.0002 (Table S3!W24), normalized to 0.000200080032, is set to zero. All remaining seabird prey, including detritus, are multiplied by 1.000200120072; diet sum is 1. Every other diet and all groups are retained. This is an authorized scenario, not a claim that the published cell is a typographical error.',
    'Predation is recomputed from unchanged consumption. Only 13 affected BA entries with matching loader-derived provenance are recomputed from P − M0 − catch − predation − net migration. Seabird BA changes from −0.0000135334 to 0.0001200000; detritus BA from 1658.41530027 to 1658.41527234 t km⁻² year⁻¹. All other BA and biological parameters are preserved. Detritus inflow and fate routing are unchanged.'],
    [('Source/runtime audit','evidence/source_review/source_review.md'),('Model notes','../model_notes.md'),('Correction and exact cells',relrun+'correction_summary.md')])
set_cell(rows['GE diagnostics'],[
    'OK — corrected runtime variant; baseline GE was also OK.',
    'No negative SPPR entries across the basal-source columns (78 entries). rho_living = 0.21208967; b = 0.06985764; Detritus (25) SPPR = 1.08287114.',
    'Strict model and SPPR balance: true; PP-budget gap 0%.'])
set_cell(rows['TE diagnostics'],[
    'WARN — corrected runtime variant. Near-zero TE remains for Seabirds (22), Seals (23) and Cetaceans (24).',
    'No negative SPPR entries across the basal-source columns (78 entries). rho_living = 0.27574202; Detritus (25) SPPR = 0.81044893. Strict model and SPPR balance: true; PP-budget gap is numerical roundoff (2.1 × 10⁻¹⁴%).',
    'Original FAIL: the seabird self-loop alone gave A[22,22] = rho_living = 1.11277844; no other consumer eats seabirds. At P/B = 0.4, Q/B = 66.74 and EE = 0.03, seabird TE is 0.0001798022. Original negative pairings were Phytoplankton (1) → Seabirds (22), −1,916,160.319156, and Detritus (25) → Seabirds (22), −460,709.192379. Both are removed; corrected seabird total TE SPPR is 268,113.29.',
    'Loop removal with fixed BA already removed divergence but left a 1.7% PP-budget gap and 3.3% maximum production residual. Selective derived-BA recomputation removes that imbalance. Strict balance alone did not prevent the original TE FAIL.'],
    [('Before/after diagnostics',relrun+'outputs/comparison.json')])
set_cell(rows['Other'],[
    'With Egestion: OK; no negative SPPR entries across 78 entries. rho_living = 0.16967174; b = 0.09711476; Detritus (25) SPPR = 1.20933902. Strict model and SPPR balance: true; PP-budget gap 0%.',
    'Fresh runs on 14 November 2026 use the restored archived state and historical engine, with no EE floor or relaxed thresholds. Reproduced baseline evidence is reused after verification. The older result manifest’s unknown historical execution remains a limitation. TE reports b = 0 by its no-detritus-recycling convention, not as evidence of absent ecological recycling.',
    'Source landings exclude discards; regional catch includes them. Source Turbot/Ling balance is indeterminate without BA; derived balance does not establish observed BA or whole-region validity. The corrected variant has not been adopted into regional results.'],
    [('Execution and full evidence',relrun+'evidence_index.json')])
# Current template: one main grid, diagnostics before the preserved manual SPPR cell.
sppr=rows['SPPR calculation'];first.remove(sppr)
for key in ['GE diagnostics','TE diagnostics']:first.append(rows[key])
first.append(sppr)
for key in ['Geographic fit','Temporal fit','Other','Open issues and next action','Review and reproducibility']:first.append(rows[key])
start=body.index(first); end=body.index(second)
for e in list(body)[start+1:end+1]:body.remove(e)
# Candidate mapping is retained in the exact-model snapshot, not in current ICES tables.
set_paragraph(existing_body_paragraphs[3],'Reference: 2019 total catch (landings plus discards); all catch labels, including zero catch and unidentified categories; no group filter.')
set_paragraph(existing_body_paragraphs[4],'25 source ecological groups (+1 computational import); 384 catch labels. Candidate mapping comes from the retained Scotland snapshot; current regional Matching is empty.')
set_paragraph(existing_body_paragraphs[5],'Independent simple-chain PPR totals 188,909,420.83 t C in 2019.')
set_paragraph(existing_body_paragraphs[7],'Method: independent simple trophic chain, using the retained classic coefficients.')
set_paragraph(existing_body_paragraphs[9],'Overall confidence follows the weakest necessary membership or allocation component. Rule percentages are shares of independent simple-chain PPR.')
# Preserve evidence links while removing obsolete numerical exposure shares.
p=existing_body_paragraphs[13]; oldlinks=[deepcopy(h) for h in p.findall('w:hyperlink',ns)]
set_paragraph(p,'Weights and assumptions: multi-group splits use complete 1991–1995 source-landings proportions; missing Infauna/Large zooplankton catches trigger complete biomass fallback. Historical Scottish composition is assumed for the wider region, all years and total catch including discards. ')
for h in oldlinks:p.append(h)
unresolved=', '.join(handoff['summary']['unresolved_taxa'])
set_paragraph(existing_body_paragraphs[14],'Very low: 110 labels, 12% of catch and 3.8% of simple-chain PPR. Unresolved: 12 freshwater labels, 0.0023% of catch and 0.0034% of PPR: '+unresolved+'. No meaningful marine analogue was established. These candidate mapping decisions have not been adopted into the current regional tables.')
conf=tables[2]
for cell,txt in zip(conf.findall('w:tr',ns)[0].findall('w:tc',ns),['Overall confidence','Taxa (n)','Catch (%)','Simple-chain PPR (%)']):set_paragraph(cell.find('w:p',ns),txt)
for row,item in zip(conf.findall('w:tr',ns)[1:],handoff['confidence_rows']):
    for cell,value in zip(row.findall('w:tc',ns),[item['label'],str(item['taxa']),format_percent(item['catch_percentage']),format_percent(item['ppr_percentage'])]):set_paragraph(cell.find('w:p',ns),value)
for table,items in [(tables[3],handoff['membership_rows']),(tables[4],handoff['allocation_rows'])]:
    assert abs(sum(v['ppr_percentage'] for v in items)-100)<1e-8
    for row,item in zip(table.findall('w:tr',ns)[1:],items):
        cells=row.findall('w:tc',ns)
        # Keep existing substantive rule descriptions, update exact shares only.
        set_paragraph(cells[2].find('w:p',ns),format_percent(item['ppr_percentage']))
# Add current template's Very low decisions table; split only exceptionally long
# shared-reason groups into manageable complete rows, retaining every taxon once.
heading=paragraph('Very low decisions',existing_body_paragraphs[10]); pos=body.index(existing_body_paragraphs[14])+1;body.insert(pos,heading)
tbl=deepcopy(first)
for r in list(tbl.findall('w:tr',ns)):tbl.remove(r)
grid=tbl.find('w:tblGrid',ns);widths=[6200,3900]
for c,width in zip(grid,widths):c.set(q('w'),str(width))
proto_header=tables[3].findall('w:tr',ns)[0]; proto_row=tables[3].findall('w:tr',ns)[1]
def make_row(values,head=False):
    rr=E.Element(q('tr')); trpr=E.SubElement(rr,q('trPr'));E.SubElement(trpr,q('cantSplit'))
    if head:E.SubElement(trpr,q('tblHeader'))
    prototype=proto_header if head else proto_row
    for i,value in enumerate(values):
        cc=deepcopy(prototype.findall('w:tc',ns)[0]);tcpr=cc.find('w:tcPr',ns)
        if (cw:=tcpr.find('w:tcW',ns)) is not None:cw.set(q('w'),str(widths[i]))
        for child in list(cc):
            if child.tag!=q('tcPr'):cc.remove(child)
        pp=paragraph(value);pr=E.SubElement(pp,q('pPr'));E.SubElement(pr,q('spacing')).set(q('after'),'70')
        if head:pp.find('w:r/w:rPr',ns).append(E.Element(q('b')))
        cc.append(pp);rr.append(cc)
    return rr
tbl.append(make_row(['Affected taxa','Why confidence is very low'],True))
seen=[]
for item in handoff['very_low_decisions_compact']:
    taxa=item['taxa'];seen.extend(taxa)
    for i in range(0,len(taxa),20):tbl.append(make_row(['; '.join(taxa[i:i+20]),item['reason']]))
assert len(seen)==len(set(seen))==110
body.insert(pos+1,tbl)
# Fix the verified stale regional raw link, retaining its label.
for rel in rels:
    if rel.get('Id')=='rId7':rel.set('Target','../../../../../raw/catch')
# Effective formatting for all existing/new visible hyperlinks.
for h in x.findall('.//w:hyperlink',ns):
    for r in h.findall('w:r',ns):
        pr=r.find('w:rPr',ns)
        if pr is None:pr=E.Element(q('rPr'));r.insert(0,pr)
        for tag,val in [('color','0563C1'),('u','single')]:
            e=pr.find('w:'+tag,ns)
            if e is None:e=E.SubElement(pr,q(tag))
            e.set(q('val'),val)
changed={'word/document.xml':E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True),'word/_rels/document.xml.rels':E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
with zipfile.ZipFile(report,'w') as z:
    for info,data in parts:z.writestr(info,changed.get(info.filename,data))
percentage_changes=format_report(report);verify_report(report)
with zipfile.ZipFile(report) as z:
    final=E.fromstring(z.read('word/document.xml'))
    unchanged=[name for name,data in partmap.items() if name not in changed and z.read(name)==data]
    assert len(unchanged)==len(partmap)-2
final_fields={text(c[0]):r for r in final.findall('.//w:body/w:tbl/w:tr',ns) if len(c:=r.findall('w:tc',ns))==2}
for key in manual_keys:assert E.tostring(final_fields[key].findall('w:tc',ns)[1])==manual_before[key],key
links=[]
for r in rels:
    if r.get('Type','').endswith('/hyperlink'):
        target=r.get('Target'); u=urlsplit(target)
        if not u.scheme:
            resolved=(report.parent/unquote(u.path)).resolve(); ok=resolved.exists() and resolved.is_relative_to(root);links.append({'target':target,'exists_inside_repository':ok});assert ok,target
try:parsed={'parsed':read_report(root,report,model.name)}
except Exception as e:parsed={'exception':type(e).__name__,'message':str(e)}
assert parsed.get('message')=='The report needs an explicit researcher identity, date and one unambiguous decision',parsed
qa={'edited_parts':list(changed),'unchanged_parts':unchanged,'manual_cells_preserved':manual_keys,'percentage_changes':percentage_changes,'links':links,'very_low_taxa_count':len(seen),'signoff_parser':parsed,'parser_difference_note':'Pre-edit parser stopped at an inherited broken catch link; this path is corrected. Candidate identity now recognized. Unchanged manual cell remains unsigned.','sha256':hashlib.sha256(report.read_bytes()).hexdigest()}
(run/'qa/report_structure.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'report':str(report),'all_local_links_valid':True,'manual_cells_unchanged':True,'very_low_taxa':len(seen),'signoff':parsed},ensure_ascii=False))
