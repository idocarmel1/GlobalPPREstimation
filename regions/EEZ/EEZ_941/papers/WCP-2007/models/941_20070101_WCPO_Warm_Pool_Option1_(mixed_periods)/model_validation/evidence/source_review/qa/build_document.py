import json,copy,zipfile,urllib.parse,shutil
from pathlib import Path
from lxml import etree
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
Q=Path(__file__).resolve().parent;OUT=Q.parent;REG=OUT.parents[1];ROOT=REG.parents[1];MID=OUT.name
# CURRENT_RESIDUAL_SCOPE_GUARD: preserve adopted current Office/manual content.
if __name__ == '__main__' and (OUT/'residual_fish_scope_followup.json').exists():
 raise SystemExit('Current residual scope follow-up exists; do not regenerate baseline Office artifacts or handoff. Use bounded current-state edits.')

REF=ROOT/'tools/templates/Model_validation_template.docx';OUTPUT=REG/f'Model_validation_{MID}.docx';TEMP=Q/'generated.docx'
shutil.copy2(REF,Q/'template_reference.docx')
(Q/'artifact.md').write_text('Design authority: Model_validation_template.docx v7. Preserve section dimensions/margins, fonts, all styles/themes and field order. Preserve full manual SPPR/Open issues/Review row XML and researcher placeholders. Automatic text/cell replacements only; clone rule-table body rows. Explicit blue-underlined hyperlinks, relative local targets. Figures from independent geographic/source evidence. No researcher name/date or approval inferred.',encoding='utf-8')
d=Document(REF);a=json.loads((OUT/'taxon_audit.json').read_text(encoding='utf-8'));diag=json.loads((OUT/'diagnostics_verification.json').read_text(encoding='utf-8'));geo=json.loads((OUT/'geographic_estimate.json').read_text(encoding='utf-8'));p=d.paragraphs
manual=[copy.deepcopy(d.tables[0].rows[9]._tr),copy.deepcopy(d.tables[1].rows[6]._tr),copy.deepcopy(d.tables[1].rows[7]._tr)]
def clear(par):
 for n in list(par._p):
  if n.tag!=qn('w:pPr'):par._p.remove(n)
 return par
def text(par,value):clear(par);par.add_run(value);return par
def cell(c,value):
 first=c.paragraphs[0]
 for pp in list(c._tc):
  if pp.tag==qn('w:p') and pp is not first._p:c._tc.remove(pp)
 text(first,value);return first
def link(par,label,target):
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),par.part.relate_to(urllib.parse.quote(target,safe='/:?=&%#'),RT.HYPERLINK,is_external=True))
 r=OxmlElement('w:r');rp=OxmlElement('w:rPr');co=OxmlElement('w:color');co.set(qn('w:val'),'0563C1');rp.append(co);u=OxmlElement('w:u');u.set(qn('w:val'),'single');rp.append(u);r.append(rp);t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);par._p.append(h)
def addlinks(par,links):
 for i,(label,target) in enumerate(links):
  par.add_run(' | ' if i else ' ');link(par,label,target)
def put(t,r,v,links=[]):par=cell(d.tables[t].cell(r,1),v);addlinks(par,links)
def pct(x):return '0.0000%' if x==0 else f'{x:.4f}%' if x>=.00005 else '<0.0001%'
ev='validation_reports/'+MID+'/'
put(0,1,'Kiribati (Gilbert Islands), EEZ_941.', [('Regional workbook','EEZ_941.xlsx')])
put(0,2,'Sea Around Us regional catch, 1950–2019; landings reference year 2019. Exact Gilbert Islands reporting unit, including unidentified categories; historical download retained.', [('Catch inputs','raw'),('Workbook catch','EEZ_941.xlsx')])
put(0,3,'Allain, V.; Nicol, S.; Essington, T.; Okey, T.; Olson, B.; Kirby, D. (2007). An Ecopath with Ecosim model of the Western and Central Pacific Ocean warm pool pelagic ecosystem. WCPFC-SC3-EB SWG/IP-8. DOI: not recorded.', [('Source PDF','papers/WCP-2007/download-0adcf55e.pdf'),('WCPFC article','https://meetings.wcpfc.int/node/6157'),('Paper folder','papers/WCP-2007')])
put(0,4,'Griffiths, S.P.; Allain, V.; Hoyle, S.D.; Lawson, T.A.; Nicol, S.J. (2019). Just a FAD? Ecosystem impacts of tuna purse-seine fishing associated with fish aggregating devices in the western Pacific Warm Pool Province. 2005 source and pooled experiment retained for investigation; not selected.', [('DOI 10.1111/fog.12389','https://doi.org/10.1111/fog.12389'),('Retained article','papers/Griffiths-2019')])
put(0,5,MID+'; mixed source periods. Final 31 ecological groups plus one computational import. Pelagic study domain 110–180°E, 15°S–15°N.', [('Selected JSON',f'models/{MID}/{MID}.json'),('Model folder',f'models/{MID}'),('Loaded state','evidence/2026-09-28_integration/loaded_state.json')])
put(0,6,'Initial 24-group WCPO warm-pool model and final 31-group source model, both mixed periods and the same broad domain; final adds stages and forage detail. The adopted D_fixed_M0 option1 is an extraction/parameter variant of the final model. Three Ecosim perturbations are scenarios, not distinct Ecopath inputs.', [('Initial model','models/941_200702_WCPO_Warm_Pool_Initial_(mixed_periods)'),('Final source','models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)')])
put(0,7,'Article: ? — comparative article-selection reason is unrecorded. Model: the recorded selection adopts D_fixed_M0 to preserve juvenile other-mortality flows and improve juvenile production consistency. It remains a surrogate; Griffiths 2019 is deferred for investigation.', [('Recorded rationale',f'models/{MID}/SELECTION_REPORT.md')])
put(0,8,'Initial/final table scope is distinguished. Accepted Small BET/YFT P/B and EE differ from the paper. Source YFT/piscivorous diet sums 0.998/1.002 are normalized by the retained loader. GS exceptions are retained; missing BA is derived for 24 groups. Unknown baby/forage catch becomes runtime zero; detritus EE is forced to 1 and synthetic import is added. Native stanza dynamics are not reproduced.', [('Source and runtime review',ev+'source_review.md#source-layers-and-scientific-limitations'),('Transformation ledger','evidence/2026-09-28_integration/transformation_ledger.json')])
for idx,method in [(1,'GE'),(2,'TE')]:
 z=next(x['direct']['divergence'] for x in diag if x['method']==method)
 v=f"No negative SPPR entries across the basal-source columns. rho_living = {z['rho_living']:.8f}; "
 if method=='GE':v+=f"b = {z['b']:.8f}; "
 v+=f"Detritus (31) SPPR = {z['sppr_det']['31']:.8f}."
 put(1,idx,v)
put(1,3,'Approximate A: 99.7% of the Gilbert Islands EEZ lies in the reported study rectangle. B: about 3.9–4.6% of the study area lies in this EEZ; the range reflects the published-area versus land-excluded coordinate-domain denominator. Broad pelagic overlap does not resolve coastal/reef-fish representativeness.', [('Boundary estimate',ev+'geographic_estimate.json')])
put(1,4,'Mixed source inputs: skipjack/forage 1993–2002, yellowfin/bigeye/bycatch 1995–2004 and diet 2001–2007; 2005–2006 assessment editions are not model years. Fixed ecosystem coefficients and composition proxies are transferred across 1950–2019; the 2019 estimate is not an annual ecosystem reconstruction.')
put(1,5,'The accepted variant retains overall WARN and strict mass balance false (adult BET production residual ≈0.728%); PP-budget status is OK. Original source/native-model validity and author confirmation remain unestablished. Geographic coverage and nonnegative coefficients do not resolve these limitations.', [('Exact diagnostic evidence',ev+'diagnostics_verification.json')])
text(p[3],'Reference: 2019 landings; all catch labels and source-group scope, including zero catch and unidentified categories.')
text(p[4],'31 source ecological groups (+1 computational import); 63 catch labels.')
text(p[5],f"Simple-chain PPR totals {a['simple_chain_ppr_tC']:,.2f} t C in 2019.")
text(p[6],f"{len(a['missing_tl_taxa'])} labels lack a saved TL/coefficient. All have zero 2019 landings and therefore zero annual contribution; their missing inputs remain unknown.")
text(p[7],'Method: independent simple trophic chain using saved classic taxon coefficients.')
clear(p[8]);link(p[8],'Taxon mapping appendix','EEZ941_taxon_mapping_appendix.xlsx');p[8].add_run(' and ');link(p[8],'descriptive Sources sheet','EEZ941_taxon_mapping_appendix.xlsx#Sources!A1')
for r,ss in zip(d.tables[2].rows[1:],a['confidence_summary']):
 for c,v in zip(r.cells,[ss['label'],str(ss['taxa']),pct(ss['catch_percentage']),pct(ss['ppr_percentage'])]):cell(c,v)
descriptions={
 'Explicit source assignment':'Explicit final source membership in the group or stage union.',
 'Unambiguous documented group fit':'Documented family identity fits the complete source group set.',
 'Verified synonym':'Verified historical/current synonym fits the named source stages.',
 'Assumed eligible group set':'Supported candidate set requires an explicit membership inference.',
 'Partial or conflicting ecological fit':'Source lineage partly fits the habitat or stage definition.',
 'Extension from listed representatives':'Related small-pelagic taxa extend final listed representatives.',
 'Supported ecological assignment':'Supported ecological extension for an unlisted pelagic piscivore.',
 'Broad-category approximation':'Broad catch label uses an assumed represented-pool composition.',
 'Closest represented analogue':'Weak usable taxonomic/functional analogue; habitat/stage mismatch.',
 'No meaningful assignment':'No meaningful taxonomic/feeding guild or usable analogue.',
 'Source-model catch proportions':'Historical source landings proportions supply an assumed regional composition; genuine zeros and the accepted infant exception are explicit.',
 'Approved model-biomass fallback':'Incomplete raw source catch rejects the catch proxy; complete biomass proportions assume regional composition/catchability.',
 'No split required':'One eligible group receives the entire taxon; this adds no allocation uncertainty.',
 'No usable allocation':'No eligible compartment supplies a numerical allocation.'}
for ti,field in [(3,'membership_summary'),(4,'allocation_summary')]:
 table=d.tables[ti];proto=copy.deepcopy(table.rows[1]._tr)
 for rr in list(table.rows)[1:]:table._tbl.remove(rr._tr)
 for ss in a[field]:
  table._tbl.append(copy.deepcopy(proto));rr=table.rows[-1]
  for c,v in zip(rr.cells,[descriptions[ss['label']],ss['confidence'],pct(ss['ppr_percentage'])]):cell(c,v)
clear(p[11]);p[11].add_run('Membership evidence: ');link(p[11],'final source definitions and taxonomic/ecological review',ev+'source_review.md#membership-and-reporting-scope')
text(p[13],'Each percentage is the simple-chain PPR associated with taxa using that rule. Weights and assumptions: ');link(p[13],'candidate/catch/biomass evidence',ev+'source_review.md#stage-allocation')
text(p[14],'Unresolved: Bivalvia and Echinodermata — no meaningful represented feeding/taxonomic guild; both have zero 2019 catch. Very low: broad marine fish/shark/crustacean/mollusc categories and closest coastal, octopod or unlisted-tuna analogues; all 27 exact labels are flagged in the appendix. They account for 1.2901% of landings and 0.4170% of simple-chain PPR.')
text(p[16],'Target region R and selected model study area S. Approximate WGS84 boundary comparison with consistent land exclusion; the reported model area gives an alternate B denominator.')
for ti,title,img in [(5,'Kiribati (Gilbert Islands) EEZ_941',OUT/'region_boundary.png'),(6,'Study rectangle from Allain et al. (2007), Section 2.2 PDF7',OUT/'study_domain.png')]:
 cell(d.tables[ti].cell(0,0),title);pp=cell(d.tables[ti].cell(1,0),'');pp.add_run().add_picture(str(img),width=Inches(6.5))
text(p[18],'Gilbert Islands EEZ boundary: repaired repository Sea Around Us polygon; Natural Earth 1:50m land. ');addlinks(p[18],[('Boundary source','../../common_reference_data/geography/EEZs.geojson'),('Image',ev+'region_boundary.png')])
text(p[20],'Reported bounds: 110–180°E, 15°S–15°N; reconstructed study boundary. Figure 1 PDF3 shows the broader warm-pool/cold-tongue context. ');addlinks(p[20],[('Source PDF7','papers/WCP-2007/download-0adcf55e.pdf#page=7'),('Source Figure 1',ev+'article_figure1_crop.png'),('Image',ev+'study_domain.png')])
clear(p[21]);p[21].add_run().add_picture(str(OUT/'article_figure1_crop.png'),width=Inches(6.5))
# Keep source figures and captions together; repeated headers without changing style.
for t in d.tables:
 pp=t.rows[0]._tr.get_or_add_trPr();h=OxmlElement('w:tblHeader');pp.append(h)
 for row in t.rows:
  trpr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
for idx in [2,12,15,19]:p[idx].paragraph_format.page_break_before=True
for idx in [17,19]:p[idx].paragraph_format.keep_with_next=True
for ti in [5,6]:
 for pp in d.tables[ti].cell(1,0).paragraphs:pp.paragraph_format.keep_with_next=True
# These full rows must remain byte-for-byte unchanged by all formatting passes.
for t,r,original in [(0,9,manual[0]),(1,6,manual[1]),(1,7,manual[2])]:d.tables[t].rows[r]._tr.getparent().replace(d.tables[t].rows[r]._tr,original)
d.save(TEMP)
# Reference-preserving repack: retain all original package parts except body,
# body relationships and added image content types/media.
with zipfile.ZipFile(REF) as ref,zipfile.ZipFile(TEMP) as gen,zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED) as dest:
 changed={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml'}
 for item in ref.infolist():dest.writestr(item,gen.read(item.filename) if item.filename in changed else ref.read(item.filename))
 for item in gen.infolist():
  if item.filename not in ref.namelist():dest.writestr(item,gen.read(item.filename))
check=Document(OUTPUT)
assert [etree.tostring(check.tables[t].rows[r]._tr) for t,r in [(0,9),(1,6),(1,7)]]==[etree.tostring(x) for x in manual]
assert etree.tostring(check.sections[0]._sectPr)==etree.tostring(Document(REF).sections[0]._sectPr)
with zipfile.ZipFile(REF) as ref,zipfile.ZipFile(OUTPUT) as out:
 preserved=[n for n in ref.namelist() if n not in {'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml'}]
 assert all(ref.read(n)==out.read(n) for n in preserved)
(Q/'document_fidelity.json').write_text(json.dumps({'manual_rows_identical':True,'section_dimensions_identical':True,'unchanged_reference_package_parts':preserved,'template_sha256':__import__('hashlib').sha256(REF.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
print('DOCX',OUTPUT)
