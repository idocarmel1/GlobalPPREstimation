from pathlib import Path
import json, hashlib, shutil, math, sys, re
from collections import defaultdict
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
import pypdfium2 as pdf

ROOT=Path.cwd(); REGION=ROOT/'regions/LME_036'; OUT=Path(__file__).resolve().parent.parent
MID=OUT.name; MODEL=REGION/'models'/MID; QA=OUT/'qa'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=json.loads((QA/'workbook_snapshot.json').read_text(encoding='utf-8'))
def rec(s,t):
 h,rs=b[s][t]; return [dict(zip(map(str,h),r)) for r in rs]
o=dict(b['Overview']['Settings'][1]); provenance=[]
def copy(src,dest):
 src=ROOT/src; dst=OUT/dest; dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists() and sha(dst)!=sha(src): raise RuntimeError('Copy collision '+str(dst))
 shutil.copy2(src,dst)
 provenance.append({'original':src.relative_to(ROOT).as_posix(),'copy':dst.relative_to(OUT).as_posix(),'sha256':sha(src)})
 return dst
mapping=MODEL/'source_evidence/mapping'
for p in mapping.glob(MID+'.*'):
 suffix=p.name[len(MID)+1:]; copy(p,'mapping/'+suffix)
copy(mapping/'SPPR_REGENERATION_LOG.txt','mapping/SPPR_REGENERATION_LOG.txt')
copy(MODEL/'model.json','model/selected_model.json')
copy(MODEL/'sppr_source.xlsx','diagnostics/sppr_source.xlsx')
copy(REGION/'papers/SCS-2007/metadata.json','source/article_metadata.json')
src=REGION/'papers/SCS-2007/extracted'
copy(src/'SOURCE_CONFLICTS.md','source/SOURCE_CONFLICTS.md')
copy(src/'MULTISTANZA.md','source/MULTISTANZA.md')
copy(src/'SOURCE_INVENTORY.json','source/SOURCE_INVENTORY.json')
# The source-faithful reconstruction is supporting source evidence, not the selected runtime.
for p in (src/'SCS-2007_Northern_South_China_Sea_2000s').iterdir():
 if p.is_file(): copy(p,'source/reconstruction_2000s/'+p.name)
for p in ['RESULTS.md','WORKFLOW_REVIEW.md','FINAL_VERIFICATION.json','baseline_manifest.json','lme_east/REVIEW.md','lme_east/LME_036_audit.json','lme_east/online_search_audit.json','lme_east/proposals.json']:
 copy(ROOT/'original_research_archive/research/size_allocation_20260929'/p,'allocation/'+p)
copy(ROOT/'original_research_archive/research/sppr_baseline_2026_09/output/top10/sppr_export_report.txt','diagnostics/historical_sppr_export_report.txt')
copy(ROOT/'common_reference_data/geography/LMEs.geojson','geography/LMEs.geojson')
copy(ROOT/'common_reference_data/geography/basemaps/provenance.json','geography/basemap_provenance.json')
copy(REGION/'papers/SCS-2007/ubc_2007-317501-87ea9ea0.pdf','source/Cheung_2007.pdf')

# Snapshots are labelled as new exports from saved evidence, never new solver returns.
snap={'created_during_template_test':'2026-09-29','source':'regions/LME_036/LME_036.xlsx','source_sha256':sha(REGION/'LME_036.xlsx'),
 'description':'Read-only transcription of existing GE/TE saved fields; not a new diagnostic run or complete raw diagnose_sppr return.',
 'model_id':MID,'model_health':[r for r in rec('Diagnostics','model_health') if r['TE_option'] in ['GE','TE']],
 'groups':rec('Selected model groups','Groups'),
 'group_sppr':[r for r in rec('Selected model groups','Group SPPR') if r['method'] in ['new_GE','new_TE_EEfix','new_TE_noEEfix']],
 'allocation_assumptions':rec('PPR','Allocation assumptions'),
 'mapping':rec('PPR','Matching'),'allocation_unresolved':rec('Diagnostics','Size allocation unresolved')}
(OUT/'saved_evidence_snapshot.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2),encoding='utf-8')

catch={r['taxon']:r for r in rec('Catch','Catch') if r['catch_basis']=='catch'}
assumed={r['taxon'] for r in rec('PPR','Allocation assumptions')}
cov={}
for method in ['new_GE','new_TE_EEfix','new_TE_noEEfix']:
 coeff={r['taxon']:r['sppr'] for r in rec('PPR','Taxon SPPR') if r['scope']=='all' and r['method']==method}
 supported={t for t,v in coeff.items() if isinstance(v,(float,int)) and math.isfinite(v)}
 total=sum(r['2019'] for r in catch.values()); covered=sum(r['2019'] for t,r in catch.items() if t in supported)
 assumed_catch=sum(r['2019'] for t,r in catch.items() if t in supported and t in assumed)
 saved={r['metric']:r['2019'] for r in rec('PPR','Annual') if r['scope']=='all' and r['method']==method and r['catch_basis']=='catch' and r['unidentified']=='method'}
 assert abs(total-saved['catch'])<1e-6 and abs(covered-saved['covered_catch'])<1e-6
 impact=next(r for r in rec('Diagnostics','Size allocation impact') if r['scope']=='all' and r['method']==method and r['catch_basis']=='catch' and r['year']==2019)
 assert abs(assumed_catch-impact['assumed_covered_catch'])<1e-6
 cov[method]={'total':total,'covered':covered,'pct':100*covered/total,'assumed':assumed_catch,'assumed_pct':100*assumed_catch/total,'unsupported':sorted([(t,r['2019']) for t,r in catch.items() if t not in supported],key=lambda x:-x[1]),'supported_taxa':len(supported)}
assert cov['new_GE']['covered']==cov['new_TE_EEfix']['covered']
model=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
raw={int(g['group_seq']):g for g in model['group']}; loaded={r['seq']:r for r in rec('Selected model groups','Groups')}
for n,g in raw.items(): assert g['group_name']==loaded[n]['group_name']
assert sha(MODEL/'model.json')==o['results_model_sha256']
assert sha(REGION/'papers/SCS-2007/ubc_2007-317501-87ea9ea0.pdf')=='87ea9ea00b6b71b896f89c0364bba09071f1683a71f5a66c71ea4da6bdbe3468'
assert sha(REGION/'raw/LME_036-catch.zip')=='93243a516dea2bad5aa8d64a7253bc66277db79827c510e6efd20a3633286e5f'
sys.path.insert(0,str(ROOT/'tools'));from workbooks import input_hash
assert input_hash(b)==o['calculation_input_sha256']
# Read-only direct comparison; no loader construction or scientific solver execution.
transform=[]
for n,g in raw.items():
 for field in ['biomass','pb','qb','ee','gs','biomass_accum','immigration','emigration','detritus_import']:
  val=g.get(field); saved=loaded[n].get(field)
  if str(val)=='-9999' or (saved is not None and val is not None and abs(float(val)-float(saved))>1e-10):
   transform.append({'seq':n,'group':g['group_name'],'field':field,'canonical':val,'saved_loaded':saved,'classification':'source unknown sentinel to runtime completion/default' if str(val)=='-9999' else 'canonical versus saved loaded difference'})
(OUT/'canonical_saved_state_comparison.json').write_text(json.dumps({'created_during_template_test':'2026-09-29','method':'Direct field comparison of selected JSON and saved workbook Groups; does not rerun loader or establish all historical transformations.','differences':transform},ensure_ascii=False,indent=2),encoding='utf-8')
(QA/'coverage_arithmetic.json').write_text(json.dumps(cov,indent=2),encoding='utf-8')

v=cov['new_GE']; gaps='\n'.join(f'| {t} | {v:,.6f} |' for t,v in v['unsupported'])
note=f'''# Coverage and geographic evidence check

Created during this template test on 29 September 2026. This is a new read-only arithmetic/evidence note, not a historical report, model approval, new extraction or SPPR calculation.

## Identity and reference coverage

Selected model: `{MID}`. [Regional workbook](../../../../LME_036/LME_036.xlsx) Overview supplies the exact selection and rationale. Source workbook SHA-256: `{sha(REGION/'LME_036.xlsx')}`.

Reference: year 2019; `catch` = landings plus discards; `new_GE`; scope `all` = every basal-source contribution including detritus and import; default unidentified treatment `method` = use the method's saved taxon coefficient. All catch records in the region are included; no fleet, sector or source subset was selected. The Overview's landings setting controls an inspected view and is not this reference basis.

Numerator: sum 2019 tonnes for taxa with finite saved all-source GE taxon SPPR = {v['covered']:,.9f} t. Denominator: sum all 374 catch rows = {v['total']:,.9f} t. Ratio = **{v['pct']:.8f}%**. Values agree with PPR / Annual covered_catch and catch within 0.000001 t. No missing coefficient is treated as zero. A measured zero catch contributes zero; unsupported coefficients remain unavailable.

Recorded stage assumptions: 135 unique taxa, 270 candidate rows; supported catch relying on these assumptions = {v['assumed']:,.9f} t / {v['total']:,.9f} t = **{v['assumed_pct']:.8f}% of total catch** ({100*v['assumed']/v['covered']:.8f}% of covered catch). This reproduces Diagnostics / Size allocation impact. Existing weights were documented with zero numerical coverage gain. This is the recorded stage-allocation share; it excludes additional low-confidence taxonomic/guild composites and is not the total share of all scientific assumptions.

TE (`new_TE_EEfix` and `new_TE_noEEfix`) has exactly the same supported taxa and coverage; no second, different TE coverage is claimed. Native treatment retains mapped unidentified labels. Results remain provisional.

Unsupported catch = {v['total']-v['covered']:,.9f} t ({100-v['pct']:.8f}%). Twelve labels are unresolved in the retained mapping; some contribute zero in 2019:

| Taxon | 2019 total catch t |
|---|---:|
{gaps}

The older mapping notes' 99.7884% uses the entire 1950–2019 series, not this reference year. [Copied mapping notes](mapping/notes.md), [adopted-allocation results](allocation/RESULTS.md), [saved field snapshot](saved_evidence_snapshot.json), [arithmetic record](qa/coverage_arithmetic.json).

## Geographic fit

R = LME_036 South China Sea; S = the 2000s northern shelf model domain. A = 100 × area(R ∩ S) / area(R); B = 100 × area(R ∩ S) / area(S).

**A: Not determined. B: Not determined.** R has an existing Sea Around Us EPSG:4326 GeoJSON boundary. S has no verified digital study polygon in current project records. Cheung (2007), Figure 6.1, printed p.170 / PDF p.185, describes the area from the coast to a broken line, mainly the Chinese EEZ shelf shallower than 200 m. The figure does not supply georeferenced vertices or enough cartographic control to establish a compatible polygon. Broad coordinate bounds do not supply that footprint. The source metadata explicitly says the legacy approximate footprint was removed pending geographic verification. No area or overlap percentage was manufactured; no bounding rectangle or map marker was used.

Required missing input is a verified model-domain polygon or defensible georeferencing and digitization of the study boundary, including the shelf/EEZ and Gulf of Tonkin treatment. A compatible equal-area or geodesic area method would then be needed. No overlap calculation was performed in this test.

[Boundary copy](geography/LMEs.geojson); [article metadata](source/article_metadata.json); [article PDF](source/Cheung_2007.pdf#page=185). The generated boundary view draws original GeoJSON vertices in a longitude/latitude display with cosine adjustment at 15°N; it is illustrative and is not an area calculation. Natural Earth 1:50m land is display context only. [Basemap provenance](geography/basemap_provenance.json).

## Limits and identity checks

Selected model SHA-256 matches Overview results_model_sha256: `{sha(MODEL/'model.json')}`. Current calculation-input fingerprint matches Overview. Thesis PDF and raw catch ZIP match their retained source hashes. All 38 canonical group IDs/names match the saved Groups records, with an additional synthetic import group 39. These checks do not independently validate every extraction cell or reproduce the historical solver environment.

[Saved-state comparison](canonical_saved_state_comparison.json) was created during this test. It records canonical unknown GS/BA/migration/import markers versus numeric runtime values, detritus EE 0.005 versus saved loaded EE 1, and synthetic import in the snapshot. The source reconstruction report is for the separately retained `36_South_China_Sea...` candidate; its source findings are useful context, but its INDETERMINATE verdict is not substituted for selected-model GE/TE statuses.

No full selected-model direct-diagnostic Markdown report or complete historical loader transformation ledger was located. Use [saved SPPR workbook](diagnostics/sppr_source.xlsx), [GE/TE saved-field transcription](saved_evidence_snapshot.json) and [retained verification](mapping/verification.json). The [historical export report](diagnostics/historical_sppr_export_report.txt) supplies matching warning text, but is an earlier run (75 Monte Carlo draws versus 100 in current notes); its configuration and coefficients are not silently adopted as a new run. The current flattened diagnostic record does not preserve the full original warnings/return object or executed-engine hash.

Template test scope: document evidence and saved calculations; no scientific source, workbook, mapping, selection, method status or map was edited; no extraction, SPPR solver or Monte Carlo was run. Manual research decisions remain for the researcher.
'''
# correct relative route from supporting folder to active workbook
note=note.replace('../../../../LME_036/LME_036.xlsx','../../LME_036.xlsx')
(OUT/'coverage_geography_test_note.md').write_text(note,encoding='utf-8')

# Original article figure, rendered from the verified source PDF, with full original caption.
d=pdf.PdfDocument(str(OUT/'source/Cheung_2007.pdf')); page=d[184].render(scale=3).to_pil()
sx=page.width/1199;sy=page.height/1583
page.crop((int(230*sx),int(795*sy),int(1060*sx),int(1425*sy))).save(OUT/'article_figure_6_1.png')

# Source-boundary illustration from retained vertices, with latitude/longitude and legend.
geo=json.loads((OUT/'geography/LMEs.geojson').read_text(encoding='utf-8'))
f=next(f for f in geo['features'] if int(f['properties']['region_id'])==36)
land=json.loads((ROOT/'common_reference_data/geography/basemaps/ne_50m_land.geojson').read_text(encoding='utf-8'))
W,H=1100,1170; im=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(im)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/calibri.ttf',n)
x0,y0,x1,y1=95,100,1000,965
allpoints=[p for poly in (f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]) for ring in poly for p in ring]
lon0=min(p[0] for p in allpoints)-1.5;lon1=max(p[0] for p in allpoints)+1.5
lat0=min(p[1] for p in allpoints)-1.0;lat1=max(p[1] for p in allpoints)+1.0
scale=min((x1-x0)/((lon1-lon0)*math.cos(math.radians(15))),(y1-y0)/(lat1-lat0))
pw=(lon1-lon0)*math.cos(math.radians(15))*scale; ph=(lat1-lat0)*scale
left=(W-pw)/2;top=y0
def xy(p):return (left+(p[0]-lon0)*math.cos(math.radians(15))*scale,top+(lat1-p[1])*scale)
def polys(g):return g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
dr.rectangle((left,top,left+pw,top+ph),fill='#edf6fa',outline='#586a72',width=2)
for feat in land['features']:
 for poly in polys(feat['geometry']):
  ring=poly[0]
  if max(p[0] for p in ring)<lon0 or min(p[0] for p in ring)>lon1 or max(p[1] for p in ring)<lat0 or min(p[1] for p in ring)>lat1:continue
  dr.polygon([xy(p) for p in ring],fill='#d8ddda',outline='#8e9992')
for poly in polys(f['geometry']):
 for ring in poly:dr.line([xy(p) for p in ring],fill='#aa2840',width=5)
# clip geographically distant land drawing to map box
im2=Image.new('RGB',(W,H),'white'); im2.paste(im.crop((int(left),int(top),int(left+pw+1),int(top+ph+1))),(int(left),int(top)));im=im2;dr=ImageDraw.Draw(im)
for lon in range(100,125,5):
  x,y=xy([lon,lat0]);dr.text((x-22,y+8),f'{lon}°E',font=font(24),fill='#253640')
for lat in range(0,26,5):
 x,y=xy([lon0,lat]);dr.text((x-65,y-14),f'{lat}°N',font=font(24),fill='#253640')
for name,lon,lat in [('China',110,24),('Vietnam',103.5,17),('Philippines',119.5,14),('Borneo',113,1.5),('Taiwan',119.5,25)]:dr.text(xy([lon,lat]),name,font=font(24),fill='#293b3c')
dr.text((70,25),'LME_036  South China Sea',font=font(40),fill='#182c37')
dr.line((70,1020,140,1020),fill='#aa2840',width=5);dr.text((155,1003),'Sea Around Us LME boundary',font=font(28),fill='#233942')
dr.text((70,1050),'Natural Earth land context. Generated from retained GeoJSON.',font=font(25),fill='#354955')
dr.text((70,1100),'Display only; no numerical overlap inferred.',font=font(25),fill='#354955')
im.save(OUT/'LME_036_boundary.png')

# Copied reports retain their original scientific text. Add explicit navigation for old/plain paths.
nav={
 'mapping/notes.md':[('Sibling review','mapping/review.json'),('Source conflicts','source/SOURCE_CONFLICTS.md'),('Regeneration comparison','mapping/regeneration-comparison.json'),('Current coverage note','coverage_geography_test_note.md')],
 'mapping/MODEL_PROFILE.md':[('Sibling notes','mapping/notes.md')],
 'allocation/RESULTS.md':[('Eastern LME review','allocation/lme_east/REVIEW.md'),('LME036 audit','allocation/lme_east/LME_036_audit.json'),('Proposals','allocation/lme_east/proposals.json'),('Search audit','allocation/lme_east/online_search_audit.json')],
 'allocation/lme_east/REVIEW.md':[('Proposals','allocation/lme_east/proposals.json'),('Search audit','allocation/lme_east/online_search_audit.json')]
}
import os
for key,links in nav.items():
 p=OUT/key; txt=p.read_text(encoding='utf-8');txt+='\n\n---\nCopy navigation added during the template test; historical text above is unchanged.\n\n'
 txt+=' · '.join(f'[{label}]({quote(os.path.relpath(OUT/target,p.parent).replace(chr(92),"/"),safe="/.")})' for label,target in links)+'\n'
 p.write_text(txt,encoding='utf-8')
lines=['# Supporting reports index','',f'Completed-template test for `{MID}`, 29 September 2026. Originals were copied, never moved. Scientific text is preserved; explicit navigation was added only to selected copies. Hashes below describe original bytes. Source reconstruction is a separate candidate, not the selected runtime.','', '| Original path (project-relative) | Supporting copy | Original SHA-256 |','|---|---|---|']
for e in provenance:
 rel=os.path.relpath(ROOT/e['original'],OUT).replace('\\','/'); lines.append(f'| [{e["original"]}]({quote(rel,safe="/.")}) | [{e["copy"]}]({quote(e["copy"],safe="/.")}) | `{e["sha256"]}` |')
lines+=['','## New material created during this test','','[Coverage and geographic note](coverage_geography_test_note.md); [saved-field transcription](saved_evidence_snapshot.json); [canonical to saved-state comparison](canonical_saved_state_comparison.json); [region view](LME_036_boundary.png); [Figure 6.1 render](article_figure_6_1.png). These are new documentation artifacts, not historical reports or rerun science.','',f'Boundary view source SHA-256 `{sha(ROOT/"common_reference_data/geography/LMEs.geojson")}`. Figure source SHA-256 `{sha(OUT/"source/Cheung_2007.pdf")}`, PDF p.185 / printed p.170. Rendering/QA intermediates are in qa/.','', 'No existing regional validation record was found; no researcher-reviewed document was replaced.']
(OUT/'reports_index.md').write_text('\n'.join(lines),encoding='utf-8')
(QA/'source_provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
protected=[ROOT/'Project.xlsx',REGION/'LME_036.xlsx',ROOT/'tools/templates/Model_validation_template.docx',MODEL/'model.json',ROOT/'interactive_map/index.html']
(QA/'protected_hashes.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in protected},indent=2),encoding='utf-8')
print(json.dumps({'coverage':cov['new_GE'],'copied_files':len(provenance),'output':str(OUT)},ensure_ascii=False,indent=2))
