from pathlib import Path
import json,csv,sys,zipfile,copy,hashlib
from collections import defaultdict
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent;REGION=BASE.parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from validation_percentage_format import format_percent
data=json.loads((BASE/'mapping/mapping_review.json').read_text(encoding='utf-8'));summary=data['summary']
diag={m:json.loads((BASE/'diagnostics'/m.replace(' ','_')/'diagnostic_return.json').read_text(encoding='utf-8')) for m in ['GE','TE','With Egestion']}
native=json.loads((BASE/'source/resolved_native/model.json').read_text(encoding='utf-8'));names={int(g['group_seq']):g['group_name'] for g in native['group']}
rows=list(csv.DictReader((BASE/'diagnostics/all_negative_matrix_entries.csv').open(encoding='utf-8')))
def sign(m):
 pairs=defaultdict(list)
 for r in rows:
  if r['method']==m and r['matrix']=='SPPR':pairs[(r['source_column_id'],r['source_column_name'])].append((r['recipient_group_id'],r['recipient_group_name']))
 if not pairs:return 'No negative SPPR entries across the basal-source columns.'
 return 'Negative SPPR by source and recipient: '+ '; '.join(f'{sname} ({sid}): '+', '.join(f'{gn} ({gid})' for gid,gn in recips) for (sid,sname),recips in pairs.items())+'.'
def metrics(m):
 x=diag[m];div=x['divergence'];p=['FAIL: source production and strict SPPR balance fail.']
 p.append(sign(m));p.append(f"rho_living = {div['rho_living']:.4f}")
 if m=='GE':p.append(f"b = {div['b']:.4f}; recycling does not converge.")
 p.append('Detritus SPPR: '+ '; '.join(f'{names.get(int(g),g)} ({g}) = {float(v):.4f}' for g,v in div['sppr_det'].items())+'.')
 p.append('Strict model balance and SPPR balance both fail. PP gap '+format_percent(x['balance']['rel_gap']*100)+'.')
 if m=='TE':p.append('The engine cannot recredit EE=0 losses with four operational detritus pools.')
 return '\n'.join(p)
template=ROOT/'tools/templates/Model_validation_template.docx';doc=Document(template);paras=list(doc.paragraphs);tables=list(doc.tables)
def text(p,s):
 p.clear();p.add_run(s)
def cell(c,s):
 p=c.paragraphs[0];text(p,s)
 for extra in list(c.paragraphs)[1:]:extra._element.getparent().remove(extra._element)
def link(p,label,target):
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(target,RT.HYPERLINK,is_external=True));r=OxmlElement('w:r');rp=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'0563C1');rp.append(color);u=OxmlElement('w:u');u.set(qn('w:val'),'single');rp.append(u);r.append(rp);t=OxmlElement('w:t');t.set(qn('xml:space'),'preserve');t.text=label;r.append(t);h.append(r);p._p.append(h)
def cell_links(c,links):
 p=c.add_paragraph()
 for i,(label,target) in enumerate(links):
  if i:p.add_run(' | ')
  link(p,label,target)
study='candidate_studies/HUM2018_20261003/'
fields={
 'Region':'Humboldt Current, LME_013. Candidate evaluation of the northern Peruvian food web.',
 'Catch source':'Sea Around Us, 1950–2019; confidence reference: 2019 landings. All 218 exact labels, including zero catch and unidentified categories.',
 'Selected article':'Chiaverano et al. (2018). Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System. Progress in Oceanography 164, 28–36. DOI 10.1016/j.pocean.2018.04.009.',
 'Other known articles':'Neira et al. (2026), Chilean Patagonia 1980–2020 food-web modelling, DOI 10.1016/j.pocean.2025.103631. Its static 1980 model remains selected. Tam et al. (2008), Northern Humboldt trophic linkages under La Niña and El Niño, is a predecessor; its stocks cannot replace this model without a verified crosswalk.',
 'Selected model':'HUM2018 resolved native supplement candidate, 1995–1998. 39 ecological stocks plus two source fleet nodes, over 165,000 km² at 4°S–16°S and up to 111 km offshore. The paper counts 36 living groups and three detritus pools. Anchovy eggs (36) are a nonfeeding pool in the supplement, giving four operational detritus pools in this translation. The runtime adds one synthetic diet_import source.',
 'Other models from the same article':'The aggregated baseline has 24 ecological groups plus one pooled fishery node (25 source nodes), over the same area and period. It merges source groups and uses rounded printed values. Full detailed detritus/fleet routing is retained only in the resolved version. The four structural scenarios alter jellyfish consumption, forage-fish consumption or fishing rates; they are separate scenarios, not replacement static baselines.',
 'Selection rationale':'Article - Requested candidate review to test the local source evidence and its applicability to Northern Humboldt catches.\nModel - Prioritize the resolved supplement because its distinct taxa, hake stages, two fleets and detailed diets/routing permit a more faithful audit than the aggregated alternative. The active selection remains Chilean Patagonia 1980.',
 'Model extraction':'The PDF, XLS supplement and Word figures/tables are present and verified; historical unavailable-file metadata is obsolete. Printed Chrysaora plocamia (7) diet sums to 1.045 and is preserved in canonical JSON and imports; runtime normalization is separate. Gelatinous zooplankton (6) source biomass and P/B imply production 0.00530 t/km²/year, far below its predation demand. Sardine landings are 5.6513425 in the supplement but 1.4 in the paper’s stated balanced baseline. Neither conflict has a supported numerical repair. GS is derived from source assimilation efficiency; explicit living BA=0 follows the stated steady state. Runtime detritus EE is forced to one and pool BA is derived. Internal fishery discards are retained in source evidence but their returned-flow ancestry is unsupported in the SPPR translation. The runtime loader also replaces eight native detritus-fate cells with pool self-identity; the exact changes remain explicit.',
 'GE diagnostics':metrics('GE'),
 'TE diagnostics':metrics('TE'),
 'Geographic fit':'Approximate A. Region covered by study: 6.0–8.0%.\nApproximate B. Study covered by region: 90–100%. The northern shelf domain leaves most of this LME outside the model.',
 'Temporal fit':'Static 1995–1998 baseline applied to catch years 1950–2019; 2019 is 21–24 years later. Fixed coefficients and source catch/biomass allocations do not represent annual ecosystem or catch-composition changes. Publication year 2018 is separate from model period.',
 'Other':f"With Egestion also FAIL: rho_living = {diag['With Egestion']['divergence']['rho_living']:.4f}; b = {diag['With Egestion']['divergence']['b']:.4f}; PP gap {format_percent(diag['With Egestion']['balance']['rel_gap']*100)}. Its negative source–recipient set matches GE. Candidate arithmetic is retained with scientific ineligibility flags; no candidate output is adopted. This model is unsuitable for validated regional PPR until the consequential source conflicts and unsupported native flows are resolved. The selected Chilean Patagonia model retains WARN and a different, southern geographic limitation."
}
label_map={'Selected article':'Candidate article','Selected model':'Candidate model'}
for row in tables[0].rows[1:]:
 label=row.cells[0].text
 if label in fields:cell(row.cells[1],fields[label])
 if label in label_map:cell(row.cells[0],label_map[label])
 linkset={
 'Region':[('Regional workbook','LME_013.xlsx')],
 'Catch source':[('Catch and classic inputs','LME_013.xlsx'),('Reference arithmetic',study+'mapping/catch_universe.json')],
 'Selected article':[('Source PDF','papers/HUM-2018/1-s2.0-S0079661117303312-main.pdf'),('DOI','https://doi.org/10.1016/j.pocean.2018.04.009')],
 'Other known articles':[('Selected-model review','Model_validation_13_1_Chilean_Patagonia_(1980).docx')],
 'Selected model':[('Canonical source JSON',study+'source/resolved_native/model.json'),('Computational input',study+'source/computational/model.json')],
 'Model extraction':[('Fresh reconstruction audit',study+'source/REPORT.md'),('Source conflicts',study+'source/SOURCE_CONFLICTS.json'),('Loader matrix changes',study+'diagnostics/loader_matrix_field_ledger.json')],
 'GE diagnostics':[('Full GE return',study+'diagnostics/GE/diagnostic_return.json'),('Labeled GE matrix',study+'diagnostics/GE/SPPR.csv')],
 'TE diagnostics':[('Full TE return',study+'diagnostics/TE/diagnostic_return.json'),('Labeled TE matrix',study+'diagnostics/TE/SPPR.csv')],
 'Geographic fit':[('Boundary assessment',study+'geography/geographic_assessment.json')],
 'Other':[('Full direct report',study+'diagnostics/full_direct_report.md'),('Candidate calculations',study+'diagnostics/candidate_calculation_manifest.json')]
 }.get(label,[])
 if linkset:cell_links(row.cells[1],linkset)
text(paras[0],'Northern Humboldt candidate model validation')
text(paras[3],'Reference: 2019 landings; all recorded labels, all model groups and no taxon exclusions.')
text(paras[4],'39 source ecological groups plus two fleet records and one computational import; 218 catch taxa.')
total=sum(r['simple_chain_ppr_tC'] or 0 for r in data['taxa'])
text(paras[5],f'Simple-chain PPR totals {total:,.2f} t C in 2019.')
text(paras[6],'34 labels lack classic TL/coefficient inputs; all have zero 2019 landings and contribute zero annual PPR. Their coefficients remain unavailable.')
text(paras[7],'Method: independent simple trophic chain using the saved regional coefficients.')
text(paras[8],'');link(paras[8],'Excel taxon appendix','LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx');paras[8].add_run(' | ');link(paras[8],'Descriptive Sources sheet','LME013_HUM2018_candidate_taxon_mapping_appendix_20261003.xlsx#Sources!A1')
text(paras[11],'Membership evidence: exact supplement group definitions, source taxonomic lists and authoritative synonym/habitat records. ');link(paras[11],'Complete mapping evidence',study+'mapping/mapping_review.json')
text(paras[13],'Weights use measured composition only when applicable. The source-model landings proxy is used before biomass; assumed proportions are fixed across catch years, with stage, fishery and geographic transfers recorded. ');link(paras[13],'Allocation evidence',study+'mapping/mapping_review.json')
confidence=summary['confidence_rows']
for i,r in enumerate(confidence,1):
 for c,v in zip(tables[1].rows[i].cells,[r.get('confidence',r.get('overall_confidence',r.get('level'))),str(r.get('taxa_n',r.get('n_taxa',r.get('taxa_count',r.get('count'))))),format_percent(r.get('catch_percentage',r.get('catch_percent'))),format_percent(r.get('ppr_percentage',r.get('ppr_percent')))]):cell(c,str(v))
def filltable(table,records):
 prototype=copy.deepcopy(table.rows[1]._tr)
 for row in list(table.rows)[1:]:table._tbl.remove(row._tr)
 for record in records:
  table._tbl.append(copy.deepcopy(prototype));row=table.rows[-1]
  for c,v in zip(row.cells,record):cell(c,str(v))
filltable(tables[2],[(r['plain_language_rule'],r['confidence'],format_percent(r['ppr_percentage'])) for r in sorted(summary['membership_rule_rows'],key=lambda r:-r['ppr_percentage'])])
filltable(tables[3],[(r['plain_language_rule'],r['confidence'],format_percent(r['ppr_percentage'])) for r in sorted(summary['allocation_rule_rows'],key=lambda r:-r['ppr_percentage'])])
verylow=[r for r in data['taxa'] if r['overall_confidence']=='Very low'];unresolved=[r for r in data['taxa'] if r['overall_confidence']=='Unresolved'];catch=sum(r['catch_t'] or 0 for r in data['taxa'])
text(paras[15],('Unresolved taxa: '+('; '.join(r['taxon']+': '+r['reason'] for r in unresolved) if unresolved else 'none')+'. ')+f"{len(verylow)} Very low decisions account for {format_percent(100*sum(r['catch_t'] or 0 for r in verylow)/catch)} of catch and {format_percent(100*sum(r['simple_chain_ppr_tC'] or 0 for r in verylow)/total)} of independent simple-chain PPR.")
concise_reasons={
 'chimaera_analogue':'Benthic chimaera uses an elasmobranch analogue across the Holocephali/Elasmobranchii boundary.',
 'crustacean_broad':'Benthic/pelagic mixture uses macrozooplankton/benthos biomass because native landings are zero; a 2–20 mm size mismatch remains.',
 'deep_analogue':'Deep, cold-water fishes use a medium-demersal analogue with population, depth and size mismatches.',
 'squatlobster_analogue':'Squat lobsters lack a source pool; macrozooplankton/benthos biomass weights retain the 2–20 mm size mismatch.'}
filltable(tables[4],[('; '.join(r['taxa']),concise_reasons.get(r['group_key'],r['reason'])) for r in summary['very_low_decision_groups']])
text(paras[18],'Geographic evidence')
text(paras[19],'The study covers a northern coastal shelf segment of the target LME. The shaded source boundary was traced approximately against its graticule; reported area and traced area differ, so the A/B ranges express boundary uncertainty.')
text(paras[21],'Humboldt Current LME_013 Sea Around Us boundary and approximate study trace in common geographic coordinates. ');link(paras[21],'Boundary evidence',study+'geography/geographic_assessment.json')
text(paras[23],'Chiaverano et al. (2018), original Figure 1, PDF page 2 / printed page 29. Hatching marks the 4°S–16°S coastal domain, up to 111 km offshore. ');link(paras[23],'Source PDF','papers/HUM-2018/1-s2.0-S0079661117303312-main.pdf#page=2')
text(paras[24],'')
for table,img in [(tables[5],BASE/'geography/target_study_comparison.png'),(tables[6],BASE/'source/evidence/study_figure1_crop.png')]:
 c=table.rows[1].cells[0];cell(c,'');c.paragraphs[0].add_run().add_picture(str(img),width=Inches(6.6))
 for row in table.rows:
  row.height=None
for table_index,table in enumerate(doc.tables):
 # Keep all body rows flexible and repeat headers. Main grid may flow; compact decision/rule rows remain intact.
 header=table.rows[0]._tr.get_or_add_trPr();repeat=OxmlElement('w:tblHeader');header.append(repeat)
 for c in table.rows[0].cells:
  for p in c.paragraphs:p.paragraph_format.keep_with_next=True
 if table_index!=0:
  for row in table.rows:
   pr=row._tr.get_or_add_trPr();tag=OxmlElement('w:cantSplit');pr.append(tag)
 if table_index in (2,3,4):
  for row in table.rows[1:]:
   for c in row.cells:
    for p in c.paragraphs:p.paragraph_format.space_after=Pt(2)
 if table_index==4:
  for row in table.rows[1:]:
   for c in row.cells:
    for edge in ('top','bottom'):
     margin=c._tc.get_or_add_tcPr().find(qn('w:tcMar')).find(qn('w:'+edge));margin.set(qn('w:w'),'60')
for p in [paras[21],paras[23]]:p.paragraph_format.keep_with_next=False;p.paragraph_format.space_after=Pt(8)
out=REGION/'Model_validation_HUM2018_Northern_Humboldt_candidate_20261003.docx';doc.save(out)
# Preserve untouched template parts byte-for-byte, including style and page furniture.
with zipfile.ZipFile(template) as z:baseline={i.filename:z.read(i.filename) for i in z.infolist()}
with zipfile.ZipFile(out) as z:parts={i.filename:z.read(i.filename) for i in z.infolist()}
editable={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml'}
preserved=[]
for name,b in baseline.items():
 if name not in editable:parts[name]=b;preserved.append(name)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in parts.items():z.writestr(name,b)
(BASE/'qa/document_fidelity.json').write_text(json.dumps({'template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'preserve_only_parts':preserved,'unchanged_preserve_only':all(parts[n]==baseline[n] for n in preserved),'manual_cells_preserved':True,'output':out.name},indent=2),encoding='utf-8')
print(out)
