"""Targeted OOXML update; no scientific recomputation or regional publication."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,zipfile,sys
from lxml import etree as E
RUN=Path(__file__).resolve().parents[1]; BASE=RUN.parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
OLD=BASE/'work/2026-11-14_200000_ices_full_review'
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report,format_percent
from tools.project_core.validation.researcher_review import read_report
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W='{'+NS['w']+'}';R='{'+NS['r']+'}';PK='{http://schemas.openxmlformats.org/package/2006/relationships}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(n):return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
inv=json.loads((RUN/'inputs/report_inventory.json').read_text(encoding='utf8'))
for name in inv:assert sha(BASE/name)==inv[name]['sha256'],'Concurrent report change: '+name
source=RUN/'inputs/validation_review.docx'; target=RUN/'outputs/validation.docx'
data=json.loads((OLD/'qa/report_comparison_handoff.json').read_text(encoding='utf8'))
with zipfile.ZipFile(source) as z:parts={i.filename:(i,z.read(i)) for i in z.infolist()}
doc=E.fromstring(parts['word/document.xml'][1]);rels=E.fromstring(parts['word/_rels/document.xml.rels'][1]);body=doc.find(W+'body')
first=body.find(W+'tbl'); fields={txt(c[0]):c[1] for row in first.findall(W+'tr')[1:] for c in [row.findall(W+'tc')]}
preserved={k:E.tostring(v) for k,v in fields.items() if k not in ['Selection rationale','SPPR calculation']}
ch=next(p for p in body.findall(W+'p') if txt(p)=='Comparison of the two candidates')
textproto=deepcopy(ch.getnext());headingproto=deepcopy(ch);tableproto=deepcopy(ch.getnext().getnext())
after=next(p for p in body.findall(W+'p') if txt(p)=='Taxon mapping and coverage')
tail=[E.tostring(n) for n in list(body)[body.index(after):]]
def p(text,heading=False,page=False):
 q=deepcopy(headingproto if heading else textproto)
 for n in list(q):
  if n.tag!=W+'pPr':q.remove(n)
 pr=q.find(W+'pPr')
 if pr is None:pr=E.SubElement(q,W+'pPr')
 for tag in ['pageBreakBefore','keepNext']:
  for n in pr.findall(W+tag):pr.remove(n)
 if page:E.SubElement(pr,W+'pageBreakBefore')
 if heading:E.SubElement(pr,W+'keepNext')
 rr=E.SubElement(q,W+'r');rp=E.SubElement(rr,W+'rPr');E.SubElement(rp,W+'color',{W+'val':'000000'})
 E.SubElement(rp,W+'sz',{W+'val':'24' if heading else '22'})
 if heading:E.SubElement(rp,W+'b')
 t=E.SubElement(rr,W+'t');t.text=text;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 return q
def cell_text(cell,text,header=False):
 for n in list(cell):
  if n.tag!=W+'tcPr':cell.remove(n)
 q=p(text);pr=q.find(W+'pPr')
 for style in pr.findall(W+'pStyle'):pr.remove(style)
 spacing=pr.find(W+'spacing')
 if spacing is None:spacing=E.SubElement(pr,W+'spacing')
 spacing.set(W+'after','40');spacing.set(W+'before','40')
 for rp in q.xpath('.//w:rPr',namespaces=NS):
  rp.find(W+'sz').set(W+'val','21')
  if header:E.SubElement(rp,W+'b')
 cell.append(q)
def set_field(key,lines):
 cell=fields[key]
 oldp=deepcopy(cell.find(W+'p'))
 for n in cell.findall(W+'p'):cell.remove(n)
 for text in lines:
  q=deepcopy(oldp)
  for n in list(q):
   if n.tag!=W+'pPr':q.remove(n)
  rr=E.SubElement(q,W+'r');t=E.SubElement(rr,W+'t');t.text=text
  cell.append(q)
def table(headers,rows,widths):
 tb=deepcopy(tableproto)
 for n in tb.findall(W+'tr'):tb.remove(n)
 grid=tb.find(W+'tblGrid')
 for n in list(grid):grid.remove(n)
 for width in widths:E.SubElement(grid,W+'gridCol',{W+'w':str(width)})
 proto=tableproto.findall(W+'tr')[1].findall(W+'tc')[0]
 for idx,vals in enumerate([headers]+rows):
  tr=E.SubElement(tb,W+'tr');trpr=E.SubElement(tr,W+'trPr');E.SubElement(trpr,W+'cantSplit')
  if idx==0:E.SubElement(trpr,W+'tblHeader')
  for value,width in zip(vals,widths):
   cell=deepcopy(proto);cp=cell.find(W+'tcPr')
   for n in cp.findall(W+'gridSpan'):cp.remove(n)
   cw=cp.find(W+'tcW');cw.set(W+'w',str(width));cw.set(W+'type','dxa')
   sh=cp.find(W+'shd')
   if sh is None:sh=E.SubElement(cp,W+'shd')
   sh.set(W+'fill','E3ECF0' if idx==0 else 'FFFFFF')
   cell_text(cell,str(value),idx==0);tr.append(cell)
 return tb
def link(q,label,target):
 rid='rIdPrimary'+str(len(rels)+1)
 E.SubElement(rels,PK+'Relationship',Id=rid,Type=NS['r']+'/hyperlink',Target=target,TargetMode='External')
 rr=E.SubElement(q,W+'r');gap=E.SubElement(rr,W+'t');gap.text=' | ';gap.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 h=E.SubElement(q,W+'hyperlink',{R+'id':rid});r=E.SubElement(h,W+'r');pr=E.SubElement(r,W+'rPr')
 E.SubElement(pr,W+'color',{W+'val':'0563C1'});E.SubElement(pr,W+'u',{W+'val':'single'});E.SubElement(r,W+'t').text=label
set_field('Selection rationale',[
 'Article — No separate article-choice rationale is recorded.',
 'Model — On 14/11/2026 the researcher chose ICES as the LME_022 primary model, with separate detritus and EE floor ON at 0.1. Its broader North Sea coverage supports this choice despite source-version, diagnostic and mapping uncertainty. Pooled ICES and Scotland remain sensitivity cases. This choice is not validation sign-off.'
])
set_field('SPPR calculation',[
 'Primary: ICES; separate DOM (67), sediment POM (68) and Discards (69); EE floor ON, threshold 0.1. GE and TE comparisons are below.',
 'Sensitivities: ICES with shared detritus cost and the same floor; corrected Scotland with the floor OFF and ON at 0.1. Regional results and mapping adoption remain pending.'
])
nodes=[]
nodes.append(p('Primary configuration and PPR comparisons',True,False))
nodes.append(p('Use ICES North Sea 1991 with separate detritus and EE floor ON at 0.1 as the primary configuration. Retain pooled ICES and corrected East Coast Scotland as sensitivity cases. ICES is already the locally selected model; this report records the analytical choice for researcher review.'))
nodes.append(p('Comparison basis: 2019 landings plus discards, using the same 372 mapped catch labels and 2,717,197.286 t of catch. Scotland leaves 12 labels unresolved; their 63.412 t of catch is excluded from both models here and their Scotland PPR remains unknown. Values below are million tonnes carbon per year (Mt C/year).'))
rows=[]
labels=['ICES separate — primary','ICES pooled — sensitivity','Scotland — sensitivity','Scotland — sensitivity']
for label,c in zip(labels,data['cases']):
 rows.append([label,'ON 0.1' if c['EE_floor_ON'] else 'OFF']+[f"{c['methods'][m]['scopes'][s]['common372_MtC']:.3f}" for s,m in [('all','GE'),('all','TE'),('PP','GE'),('PP','TE')]])
nodes.append(table(['Case','EE floor','GE all sources','TE all sources','GE PP only','TE PP only'],rows,[2570,1000,1210,1210,1210,1210]))
nodes.append(p('All-source PPR sums the returned primary-producer (PP), detritus and synthetic-import columns. PP-only is the producer component of the same food-web calculation, not a detritus-free rerun. ICES is higher than Scotland on the all-source measure but lower on PP-only; neither comparison establishes which model is more accurate. Wet-weight requirements are converted to carbon by dividing by 9 once.'))
nodes.append(p('Pooling reduces ICES all-source PPR by 8.1% with GE and 0.70% with TE, with PP-only unchanged. It assigns one shared detritus cost to DOM, POM and Discards while retaining all groups, diets, fate routing and internal discard returns. It is a common-cost sensitivity, not a literal merger of the source groups.'))
nodes.append(p('The small pooled TE change conceals offsetting changes: the Discards contribution falls by 22.676 Mt C/year, while POM and DOM rise by 11.552 and 10.123 Mt C/year. Separate detritus therefore remains the primary choice: it preserves distinct source-compartment costs without adding an equal-cost assumption.'))
nodes.append(p('Turning Scotland’s EE floor ON reduces GE all-source PPR by 0.14%; TE rises by only 2.658 t C/year (0.0000061%). PP-only is unchanged. These small effects do not resolve the models’ structural differences. For the full 384-label ICES mapping, primary GE and TE all-source totals are 81.996 and 142.092 Mt C/year; Scotland has no complete 384-label total.'))
nodes.append(p('Evidence and limits of the choice',True,True))
nodes.append(p('Geographic fit favors ICES for the whole LME: the declared IVa–IVb–IVc footprint covers approximately 87% of LME_022, compared with Scotland’s 37–42% source-map range. These are boundary interpretations, not statistical intervals or recovered native model grids. Both transfer historical coefficients to 2019 catch: ICES represents 1991 and Scotland 1991–1995.'))
nodes.append(p('Source fidelity remains a limitation. The deposited ICES Rpath port materially differs from the accepted native EwE Key Run, whose database was not recovered. Broad geographic coverage and closed numerical budgets do not establish native-model equivalence. Scotland’s narrower shelf and fleet domain also limits its application to all North Sea catches.'))
nodes.append(table(['Case','GE grade','TE grade'],[[labels[i]+(' — floor ON' if i==3 else ' — floor OFF' if i==2 else ''),c['methods']['GE']['grade'],c['methods']['TE']['grade']] for i,c in enumerate(data['cases'])],[5610,1400,1400]))
nodes.append(p('All four cases pass strict model mass-balance and SPPR-budget checks and have finite, nonnegative coefficients. ICES nevertheless retains WARN grades: its separate diet-normalization check has a maximum deviation of 8.325 × 10⁻⁵, GE detritus feedback remains high, and TE has five near-zero-efficiency groups. Pooling removes the extreme detritus-cost warning but does not clear the remaining warnings. Scotland’s TE warning also persists.'))
nodes.append(p('The EE floor is a runtime mortality-export assumption, coupled with effective detritus stock closure and operational detritus EE = 1; it is not an observed parameter correction. At 0.1 it affects eight ICES living groups, versus only Seabirds, Seals and Cetaceans in Scotland. It does not place a floor on GE or TE. Same-engine Scotland OFF controls exactly reproduce the corrected historical matrices, so that engine-version difference has been checked.'))
conf=[]
for label,c in [('ICES separate',data['cases'][0]),('Scotland floor OFF',data['cases'][2])]:
 values=[]
 for cls in ['High','Very low']:
  for method in ['GE','TE']:
   value=c['methods'][method]['scopes']['all']['confidence_exposure']['common372']['percent_by_overall_confidence'][cls]
   values.append(format_percent(value))
 conf.append([label]+values)
nodes.append(table(['Mapping exposure','High GE','High TE','Very low GE','Very low TE'],conf,[2810,1400,1400,1400,1400]))
nodes.append(p('Shares above use the same common-372 all-source PPR denominator. Scotland’s coarser groups need fewer stage splits, giving a larger High share, but this does not establish whole-LME applicability. ICES allocations based on historical model catches affect about 72% of full-universe GE PPR and 68% of TE PPR. Confidence categories are review judgments, not probabilities; the simple-chain percentages in the mapping section below use a different method.'))
nodes.append(p('Scotland’s signed review excludes Seabirds, Seals and Cetaceans as calculation recipients because GE < 0.01. No mapped regional catch uses them, so these exclusions remove zero regional catch or PPR; their trophic nodes remain. The signature does not approve the new floor-ON sensitivity. The ICES review and mapping adoption remain pending. Project.xlsx, map and trends publication are deferred as requested.'))
evidence=p('Reproducibility: saved runs, exact totals, diagnostic assumptions and mapping exposure are linked below.')
link(evidence,'Four-case comparison','work/2026-11-14_200000_ices_full_review/qa/report_comparison_handoff.json')
link(evidence,'Pooled ICES audit','../results/diagnostics/2026-11-14_193500_pooled_detritus/qa/independent_pooled_review.json')
link(evidence,'Scotland floor audit','../../../../NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)/results/diagnostics/2026-11-14_184500_ee_floor_on_control/qa/independent_ee_floor_review.json')
nodes.append(evidence)
start=body.index(ch);end=body.index(after)
for n in list(body)[start:end]:body.remove(n)
for offset,n in enumerate(nodes):body.insert(start+offset,n)
assert all(E.tostring(fields[k])==v for k,v in preserved.items())
assert [E.tostring(n) for n in list(body)[body.index(after):]]==tail
clarifications={
 'Tuna, bonito and billfish labels use Mackerel':'Bonito and billfish labels use Mackerel',
 'No diet normalization, pooling or open-detritus adjustment was used.':'In the primary runs, no diet normalization, pooling or open-detritus adjustment was used.'
}
clarification_counts={k:0 for k in clarifications}
for textnode in doc.xpath('.//w:t',namespaces=NS):
 for old,new in clarifications.items():
  if old in (textnode.text or ''):
   textnode.text=textnode.text.replace(old,new);clarification_counts[old]+=1
assert all(v==1 for v in clarification_counts.values()),clarification_counts
updated={'word/document.xml':E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True),'word/_rels/document.xml.rels':E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
with zipfile.ZipFile(target,'w') as z:
 for name,(info,b) in parts.items():z.writestr(info,updated.get(name,b))
verify_report(target)
# Relative links intentionally resolve at BASE, not the staging directory.
# The canonical review parser runs after publication to that directory.
assert E.tostring(fields['Review and reproducibility'])==preserved['Review and reproducibility']
linkchecks=[]
from urllib.parse import unquote
for rel in rels:
 if rel.get('Type','').endswith('/hyperlink'):
  dest=unquote(rel.get('Target','').split('#')[0])
  if dest and not dest.startswith(('http:','https:','mailto:')):linkchecks.append({'target':dest,'exists':(BASE/dest).exists()})
assert all(x['exists'] for x in linkchecks),linkchecks
proof={'reference_sha256':sha(source),'staged_sha256':sha(target),'changed_package_parts':list(updated),'preserved_fields':[k for k in preserved if k!='Other'],'mapping_geography_tail_xml_unchanged_except_documented_clarification':True,'documented_wording_clarifications':clarifications,'percentage_format_passed':True,'unsigned_review_preserved':True,'links':linkchecks,'source_handoff_sha256':sha(OLD/'qa/report_comparison_handoff.json'),'primary':{'model_id':BASE.parent.name,'det_collapse_mode':'never','EE_floor_ON':True,'ee_floor':0.1},'regional_publication_deferred':True}
(RUN/'qa/report_patch_verification.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
(RUN/'outputs/report_text.txt').write_text('\n\n'.join(txt(n) for n in body),encoding='utf8')
print(json.dumps({'output':str(target),'sha256':sha(target),'percentage_check':True,'preserved_manual_review':True,'links':len(linkchecks)},indent=2))
