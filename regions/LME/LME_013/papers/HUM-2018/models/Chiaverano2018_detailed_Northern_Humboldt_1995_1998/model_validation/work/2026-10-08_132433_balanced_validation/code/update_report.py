"""Patch only authorized validation cells and diagnostic links in the DOCX ZIP."""
from pathlib import Path
import copy,json,zipfile,hashlib
from lxml import etree as E
from docx import Document

RUN=Path(__file__).resolve().parents[1]
MODEL=Path(__file__).resolve().parents[4]
OUT=RUN/'outputs'
path=MODEL/'model_validation/validation.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS={'w':W,'r':R}
def tag(x):return '{'+W+'}'+x
def txt(e):return ''.join(e.itertext()) if False else ''.join(e.xpath('.//w:t/text()',namespaces=NS))
def load(p):return json.loads(p.read_text(encoding='utf-8'))
summary=load(OUT/'validation_summary.json')
reports=summary['full_diagnostics']
names={int(g['group_seq']):g['group_name'] for g in load(MODEL/'model.json')['group']}

with zipfile.ZipFile(path) as z:
    parts={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
doc=E.fromstring(parts['word/document.xml'][1])
rels=E.fromstring(parts['word/_rels/document.xml.rels'][1])
table=doc.find('.//'+tag('tbl'))
rows={txt(r.find(tag('tc'))):r for r in table.findall(tag('tr'))}
manual=['SPPR calculation','Open issues and next action','Review and reproducibility']
protected={k:E.tostring(rows[k]) for k in manual}
other_tables=[E.tostring(t) for t in doc.findall('.//'+tag('tbl'))[1:]]
paragraphs=[E.tostring(p) for p in doc.find(tag('body')).findall(tag('p'))]

def cell(label,lines,attachment=False):
    c=rows[label].findall(tag('tc'))[1]
    old_p=c.find(tag('p'))
    ppr=copy.deepcopy(old_p.find(tag('pPr'))) if old_p is not None and old_p.find(tag('pPr')) is not None else None
    links=[copy.deepcopy(p) for p in c.findall(tag('p')) if p.find('.//'+tag('hyperlink')) is not None]
    for child in list(c):
        if child.tag!=tag('tcPr'):c.remove(child)
    for line in lines:
        p=E.SubElement(c,tag('p'))
        if ppr is not None:p.append(copy.deepcopy(ppr))
        r=E.SubElement(p,tag('r'));t=E.SubElement(r,tag('t'));t.text=line
    for p in links:c.append(p)
    if attachment:
        p=E.SubElement(c,tag('p'));h=E.SubElement(p,tag('hyperlink'));h.set('{'+R+'}id','rIdCurrentNegativePairs')
        r=E.SubElement(h,tag('r'));pr=E.SubElement(r,tag('rPr'))
        color=E.SubElement(pr,tag('color'));color.set(tag('val'),'0563C1')
        u=E.SubElement(pr,tag('u'));u.set(tag('val'),'single')
        t=E.SubElement(r,tag('t'));t.text='Complete negative source-to-group pairings (Excel)'

def detline(report):
    return 'Detritus SPPR: '+'; '.join(f"{names[int(k)]} ({k}) = {v:.4f}" for k,v in report['divergence']['sppr_det'].items())+'.'

ge=reports['unpooled']['GE'];pool=reports['pooled']['GE']
gsummary=next(r for r in summary['methods'] if r['configuration']=='pooled' and r['method']=='GE')
cell('Model extraction',[
    'Accepted corrections: Chrysaora plocamia (7) diet is 68% mesozooplankton, 17% macrozooplankton and 15% anchovy eggs, with zero direct diatom/small-gelatinous links. Author Table H I14/J14 reconstructs the 68/17 fractions; F14/K14 are zero and Table B H39 retains the egg fraction. This resolves the contradictory Table B diet totaling 1.045 without changing small-gelatinous biomass.',
    'Sardine (9) landings follow the article’s explicit 1.4 t/km2/year correction; reported discards 0.17462648325 remain. Total JSON export is 1.57462648325; estimated EE is recalculated to 0.68720654. Article Table 1 and Scenario III still support the older high-catch branch. These are documented reconstructions/derived corrections, not newly printed author values.',
    'The corrected model passes mass balance with living BA=0 and normalization compensation disabled. GS retains source assimilation efficiencies. Runtime normalization of the remaining diets is separate; pool EE/BA and detritus-fate identity replacement remain computational transformations. Native fleet discard-return ancestry is unsupported in the SPPR translation.'
])
cell('GE diagnostics',[
    'FAIL: unpooled detritus recycling diverges. Pooled coefficients are nonnegative and budget-balanced, but the overall diagnostic retains the unpooled divergence failure.',
    'Unpooled negative SPPR sources: Anchovy eggs (36), Pelagic detritus (38) and Benthic detritus (39). Every affected recipient, including unfished groups, is listed separately under its source in the linked Excel attachment.',
    f"rho_living = {ge['divergence']['rho_living']:.4f}; unpooled b = {ge['divergence']['b']:.4f}.",
    'Unpooled '+detline(ge),
    f"Pooled b = {gsummary['pooled_b']:.4f}. No negative pooled SPPR entries across any basal-source column or recipient.",
    'Pooled '+detline(pool),
    'Strict model balance and SPPR budget balance pass in both configurations.'
],attachment=True)
te=reports['unpooled']['TE']
cell('TE diagnostics',[
    'FAIL: primary-production budget does not close despite the corrected model passing mass balance.',
    'No negative SPPR entries across any basal-source column or recipient, including unfished groups.',
    f"rho_living = {te['divergence']['rho_living']:.4f}.",detline(te),
    'PP budget gap = 14%. Five EE=0 living groups and very small jellyfish EE remain formulation concerns. The engine has no pooled-detritus scaling for TE: explicitly requesting pooling returns the same TE matrix and gap.'
])
wg=reports['unpooled']['With Egestion'];wp=reports['pooled']['With Egestion']
wsummary=next(r for r in summary['methods'] if r['configuration']=='pooled' and r['method']=='With Egestion')
cell('Other',[
    'Both unpooled (never) and pooled (always) configurations were run on the corrected canonical model. Living BA remains zero; remaining source diets are normalized at runtime.',
    f"With Egestion remains FAIL overall: rho_living = {wg['divergence']['rho_living']:.4f}; unpooled b = {wg['divergence']['b']:.4f}; pooled b = {wsummary['pooled_b']:.4f}. Unpooled negative sources are Anchovy eggs (36), Pelagic detritus (38) and Benthic detritus (39); complete recipient pairings are in the linked attachment.",
    'Unpooled '+detline(wg),
    'Pooled '+detline(wp),
    'Pooled With Egestion has no negative entries and passes SPPR budget balance, while detritus SPPR exceeds 10 and the overall unpooled-divergence failure remains.',
    'Taxon allocations retain their documented published native-landings proxies; the sardine correction does not silently alter those assumptions. Updated regional estimates remain provisional and production-ineligible. Map refresh awaits researcher review.'
],attachment=True)

newbase='work/'+RUN.name+'/outputs/'
targets={'rId19':newbase+'unpooled/GE/diagnostic_return.json',
         'rId20':newbase+'unpooled/GE/SPPR.csv','rId21':newbase+'unpooled/TE/diagnostic_return.json',
         'rId22':newbase+'unpooled/TE/SPPR.csv','rId24':newbase+'validation_summary.json',
         'rId25':newbase+'workbook_integration.json'}
for r in rels:
    if r.get('Id') in targets:r.set('Target',targets[r.get('Id')])
new=E.SubElement(rels,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
new.set('Id','rIdCurrentNegativePairs');new.set('Type',R+'/hyperlink')
new.set('Target',"../sppr_source.xlsx#'Negative SPPR'!A1");new.set('TargetMode','External')
# Preserve existing useful links while identifying their historical/source role.
for t in doc.xpath('//w:t',namespaces=NS):
    if t.text=='Canonical source JSON':t.text='Published source representation'
    elif t.text=='Computational input':t.text='Corrected model JSON'
    elif t.text=='Fresh reconstruction audit':t.text='Published-source extraction audit'
    elif t.text=='Loader matrix changes':t.text='Prior loader matrix audit'
    elif t.text=='Candidate calculations':t.text='Updated workbook calculations'

assert protected=={k:E.tostring(rows[k]) for k in manual}
assert other_tables==[E.tostring(t) for t in doc.findall('.//'+tag('tbl'))[1:]]
assert paragraphs==[E.tostring(p) for p in doc.find(tag('body')).findall(tag('p'))]
changed={'word/document.xml':E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True),
         'word/_rels/document.xml.rels':E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
with zipfile.ZipFile(path,'w') as z:
    for name,(info,data) in parts.items():z.writestr(info,changed.get(name,data))
with zipfile.ZipFile(path) as z:
    assert all(z.read(name)==data for name,(info,data) in parts.items() if name not in changed)
    final=E.fromstring(z.read('word/document.xml'))
    rr={txt(r.find(tag('tc'))):r for r in final.find('.//'+tag('tbl')).findall(tag('tr'))}
    assert protected=={k:E.tostring(rr[k]) for k in manual}
Document(path)
(RUN/'qa/document_preservation.json').write_text(json.dumps(dict(status='PASS',
    changed_zip_parts=list(changed),manual_rows_preserved=manual,
    coverage_tables_and_geographic_figures_preserved=True,all_other_package_parts_identical=True,
    researcher_verdict_registered=False,sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2),encoding='utf-8')
print('Updated validation.docx; preserved manual rows, coverage tables, figures and all unaffected package parts.')
