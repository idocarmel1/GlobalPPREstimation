"""Audit retained source/canonical/loaded states and render direct diagnostics."""
from pathlib import Path
import json,hashlib,csv,math,shutil
from decimal import Decimal
import pandas as pd
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_050';SRC=REG/'papers/SOJ-2023';REV=Path(__file__).parent
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def num(x):
 try:
  n=float(x)
  return n if math.isfinite(n) else None
 except (ValueError,TypeError):return None
def scalar(x):
 if pd.isna(x):return None
 if hasattr(x,'item'):return x.item()
 return x
def flat(x,prefix=''):
 out={}
 for k,v in x.items():
  p=f'{prefix}.{k}' if prefix else k
  if isinstance(v,dict) and v:out.update(flat(v,p))
  else:out[p]=v
 return out
def fmt(x):
 if isinstance(x,float):return format(x,'.10g')
 if isinstance(x,(list,dict)):return json.dumps(x,ensure_ascii=False).replace('|','\\|')
 return str(x).replace('|','\\|').replace('\n',' ')
results=read(REV/'DIAGNOSE_SPPR_RESULTS.json')
paper={'article_id':'SOJ-2023__LME_050','unit_id':'LME_050','source_article_id':'SOJ-2023','title':'Impacts of regime shift on the fishery ecosystem in the coastal area of Kyoto prefecture, Sea of Japan, assessed using the Ecopath model','authors':'Hiroshi Inoue; Shingo Watari; Hideki Sawada; Edouard Lavergne; Yoh Yamashita','publication_year':2023,'published_online':'2023-06-12','doi':'10.1007/s12562-023-01691-9','citation':'Fisheries Science 89:573–593','model_years':'1985 and 2013','functional_groups':40,'paper_preference':'USER-PREFERRED/SPECIFIED SOURCE','preference_reason':'only available paper','model_selection':'pending; paper preference is not model adoption','source_identity_verified':'Local PDF is the publisher article (21 pages, printed pp.573–593), not a thesis chapter. Previous catalog assertion is contradicted by the exact local bytes.','coverage_class':'partial','model_area_km2':2230,'coverage_note':'Coastal Kyoto, coastline to 240 m bathymetry, 134°8 to 135°5 E as printed; no defensible whole-LME fraction computed. Inherited 0.01 is not validated coverage.'}
old=SRC/'evidence/source_metadata_before_review.json'
if not old.exists():shutil.copy2(SRC/'metadata.json',old)
meta=read(SRC/'metadata.json');meta['verified_review_20260928']=paper;meta['paper_preference']='USER-PREFERRED/SPECIFIED SOURCE';meta['preference_reason']='only available paper';dump(SRC/'metadata.json',meta)
dump(REV/'verified_paper_identity.json',paper)
s6={1985:['2.085','.004','2.257','.192','1.050','1.309','.098','.049','.019','1.838','.000','.039','.031','.090','.032','.129','.322','.051','.632','.189','.645','.097','.00002','.203','.102','.008','.015','.425','.0004','.001','.001','.080','.144','29.994','9.533','.041','.008','15','64.829','43'],2013:['.855','.004','1.953','.126','.817','1.415','.149','.076','.029','1.987','.000','.036','.033','.096','.034','.139','.251','.051','.491','.509','1.734','.260','.000','.203','.102','.008','.015','.425','.007','.020','.011','.139','.066','10.898','8.738','.019','.013','5.820','28.061','43']}
overall=['# SOJ-2023 source extraction review','',f"**USER-PREFERRED/SPECIFIED SOURCE:** {paper['title']} ({paper['publication_year']}); reason: **only available paper**.",'','Two tabulated reconstructions are retained. Neither is adopted as the original year-specific model. The one published diet matrix is captioned for both years, but the Results explicitly state that sardine was the main prey in 1985 and anchovy in 2013. Distinct original year-specific diets cannot be recovered from these files without further author evidence.','', 'The model area is 2,230 km² of coastal Kyoto, from the coastline to 240 m depth. This is partial spatial coverage of LME_050. The inherited 1% estimate was not verified and is not used.','', 'The local PDF is the complete publisher article, not a thesis chapter. Its first page verifies the five authors, DOI, receipt/acceptance dates, and online publication on 12 June 2023. The publisher landing page was retrieved successfully; its sole DOCX supplement was re-downloaded and exactly matches the retained SHA-256. No native EwE model is linked there.','', '## Model evidence']
proposals=[];audits=[]
for year in [1985,2013]:
 mid=f'50_50{year}_Coastal_Kyoto_Inoue_({year})';dest=REG/'models'/mid;et=dest/'extracted_tables';ev=dest/'evidence';source=read(et/'model.json');canonical=read(dest/'model.json');loaded=pd.read_csv(ev/'loaded_groups.csv',index_col=0);before=pd.read_csv(ev/'modeldata_groups.csv',index_col=0)
 changes=[]
 for seq in loaded.index:
  for col in loaded.columns:
   a=scalar(before.loc[seq,col]) if col in before else None;b=scalar(loaded.loc[seq,col])
   same=a==b
   if isinstance(a,(int,float)) and isinstance(b,(int,float)):same=math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
   if not same:changes.append({'seq':int(seq),'group_name':loaded.loc[seq,'group_name'],'field':col,'ModelData':a,'loaded':b})
 dump(ev/'loader_parameter_changes.json',changes)
 diet_changes=[];d0=pd.read_csv(ev/'modeldata_diet.csv',index_col=0);d1=pd.read_csv(ev/'loaded_diet.csv',index_col=0)
 for row in d0.index:
  for col in d0.columns:
   a=scalar(d0.loc[row,col]);b=scalar(d1.loc[row,col])
   if a!=b:diet_changes.append({'predator_seq':int(row),'prey_seq':int(col),'source_loaded_before_normalization':a,'after_normalization':b})
 dump(ev/'loader_diet_changes.json',diet_changes)
 strict={'source_admission':'NOT_ADMITTED_AS_VERIFIED_ORIGINAL_MODEL','reason':['Year-specific diet matrices unresolved: one table labeled both years contradicts prose statement of changed diets.','Diet consumer columns 11 and 12 sum to 1.01; other nonunit sums are preserved.','BA, migration rates, GS, detritus imports and routing fractions are not numerically reported.','Embedded Table S6-1 biomass values conflict with final main Table1; main final output table takes precedence.'],'diet_sums':{n:str(sum(Decimal(v) for v in d.values())) for n,d in source['diet'].items()},'canonical_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest(),'loaded_success':True,'production_adopted':False,'model_selection_pending':True,'loader_changed_parameter_cells':len(changes),'loader_changed_diet_cells':len(diet_changes),'loader_nonzero_BA_groups':[{'seq':int(i),'name':r['group_name'],'biomass_accum':r['biomass_accum']} for i,r in loaded.iterrows() if abs(r['biomass_accum'])>1e-12]}
 dump(ev/'SOURCE_ADMISSION_AND_LOADER_AUDIT.json',strict)
 s6audit=[{'seq':g['n'],'group_name':g['name'],'main_Table1_biomass':g['biomass'],'S6_1_embedded_biomass':s6[year][g['n']-1],'embedded_image':f'../../../papers/SOJ-2023/evidence/supplement_media/image{1 if year==1985 else 2}.png','choice':'main article final Table1; supplement provenance table is conflicting, not a separately balanced parameter set'} for g in source['groups']]
 dump(et/'supplement_biomass_conflicts.json',s6audit)
 catch=[]
 totals=read(et/'source_reported_catch_totals.json')
 for n,rr in source['landings'].items():
  sm=sum(Decimal(v) for v in rr.values());pr=totals.get(n)
  catch.append({'seq':int(n),'source_fleet_sum':str(sm) if rr else None,'source_printed_total':pr or None,'difference':str(sm-Decimal(pr)) if pr else None,'choice':'sum of source fleet cells in import file; printed rounded total retained separately'})
 dump(et/'catch_total_comparison.json',catch)
 # Roundtrip compares every authoritative numeric cell and blank in canonical.
 checks=[]
 for g,c in zip(source['groups'],canonical['group']):
  assert str(g['n'])==c['group_seq'] and g['name']==c['group_name']
  for sf,cf in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('pq','ge'),('tl','tl')]:
   a=g.get(sf);b=c[cf];assert (a is None and b=='-9999') or (a is not None and Decimal(a)==Decimal(b)),(year,g['n'],sf,a,b)
   checks.append(1)
  for d in c['diet_descr']['diet']:
   a=source['diet'].get(c['group_seq'],{}).get(d['prey_seq']);assert d['proportion']==(a if a is not None else '-9999')
  assert c['diet_imp']==source['diet'].get(c['group_seq'],{}).get('import','-9999')
  assert all(c[k]=='-9999' for k in ['gs','biomass_accum','immigration','emigration','detritus_import'])
 w=openpyxl.load_workbook(dest/'model_reconstructed.xlsx',read_only=True,data_only=False)
 rec=list(w['Basic input'].values)[1:]
 for g,row in zip(source['groups'],rec):
  assert row[0]==g['n'] and row[1]==g['name']
  for index,field in [(3,'biomass'),(4,'pb'),(5,'qb'),(6,'ee')]:assert row[index]==(float(g[field]) if g[field] is not None else None)
  assert row[2] is None and row[8] is None and row[9] is None
 drows=list(w['Diet composition'].values);dh=drows[0]
 for n,ds in source['diet'].items():
  ci=dh.index(n)
  for prey,v in ds.items():
   matching=[r for r in drows[1:] if str(r[0]).lower()==prey or (prey=='import' and str(r[1]).lower()=='import')]
   assert len(matching)==1,(prey,matching)
   assert math.isclose(float(matching[0][ci]),float(v),rel_tol=1e-12)
 w.close()
 rt={'canonical_source_numeric_fields_checked':len(checks),'all_40_group_identities_match':True,'all_explicit_diet_cells_match_source':True,'all_missing_source_fields_preserved_as_sentinel':True,'reconstructed_basic_and_explicit_diet_cells_match':True,'lossy_converter_reconstruction':['Blank diet cells render as zero in reconstructed workbook; original blank vs printed zero remains in import CSV and cell evidence.','Unknown detritus fates render as zero in reconstructed workbook; source canonical retains -9999.','Metadata sheet uses input filename model; authoritative model identity is folder and extracted Metadata.xlsx.','Fleet-level catches, discards and unknown BA are not fully represented by reconstructed workbook; eight original tables remain authoritative.'],'status':'PASS_FOR_SUPPORTED_FIELDS_WITH_DOCUMENTED_RECONSTRUCTION_LIMITS'}
 dump(ev/'ROUNDTRIP_VERIFICATION.json',rt)
 model_report=f'''# Coastal Kyoto ({year}) source extraction

**Status:** tabulated reconstruction; source admission unresolved; exact model selection pending. Local model ID `{mid}` is not an EcoBase accession.

Source: Inoue, Watari, Sawada, Lavergne and Yamashita (2023), Fisheries Science 89:573–593, DOI 10.1007/s12562-023-01691-9. Paper chosen by the user because it is the only available paper. Both publication-defined model periods, 1985 and 2013, are retained separately.

## Source tables and numerical meaning

Table 1, PDF pp.5–6 / printed pp.577–578, gives 40 groups in exact order: 38 consumers, phytoplankton (#39), detritus (#40). Columns map TL→tl, B→biomass (t/km²), P/B→pb (/year), Q/B→qb (/year), P/Q→ge, EE→ee. Bold cells are author inputs; regular-font cells are Ecopath estimates. Font status and bounding boxes are retained for all 240 parameter cells per model. The main article's final Table1 is preferred over supplementary input-source tables, with conflicts retained.

Table 2, PDF pp.7–8 / printed pp.579–580, has prey rows 1–40 and predator columns 1–38, plus Import and printed Sum rows. Pages were rotated +90° for reading. Tokens were reconstructed from raw PDF characters; numerical LEFT edges match numbered column headers within 0.3 pt, and prey row anchors were checked visually. This avoids fused adjacent cells. Printed zeros remain separate from blank cells. Nine columns have exact nonunit totals; #11 and #12 total 1.01, although the printed Sum row is 1. Canonical source diets were not normalized.

**Year ambiguity:** this single table is captioned for both years, yet p.585 says diets differed, with sardine dominant in 1985 and anchovy dominant in 2013. The table is preserved in both caption-linked reconstructions. No year-specific swap or invented alternative diet was made. These files cannot be represented as a verified recovery of either original model.

Supplement Table S4 (DOCX table {4 if year==1985 else 5}) gives {len(source['fleets'])} fleet columns: {', '.join(source['fleets'])}. Source fleet cells are preserved without renaming. The narrative calls these six methods, but the 1985 table has seven columns including `others`. Total catch is placed in Landings as the import-format convention; no landings/discards split was stated. Printed row totals and recomputed fleet sums differ because of source precision and are retained in catch_total_comparison.json. Rounded printed 0.000 totals are not substituted for positive detailed fleet cells. Missing nonfishery catch stays blank.

## Deliberate blanks and prose sweep

The complete 21-page main article, all nine online resources in the DOCX, 12 XML tables, and embedded S6-1 / S9 images were checked. No numeric GS/unassimilated consumption, per-group BA, immigration/emigration, detritus import or detritus-routing fraction was found. Those fields remain blank in imports and -9999 in canonical JSON. A static mass-balanced description is not an explicit BA=0 statement. No zooplankton GS convention was added. Habitat-area proportion is unreported: Table1 B is model-area biomass; canonical biomass is the printed B while habitat fraction stays missing. The Basic_input importer places B in its only biomass column, with this semantic limitation recorded.

Methods pp.576/578/581 and Discussion p.590 explain diet imports for migrating fish; diet imports are prey consumption outside the modeled system, not numeric immigration or emigration fluxes. The discussion mentions discarded fish and recreational catch as statistical error sources without a numeric discard amount, survival or return destination. Discards and routing therefore remain unknown. No offal group or fleet-return pathway was invented.

Supplementary S6-1 is an embedded image, not a native model. Its panel labeled 1985 contains catches resembling 2013 and many biomasses conflicting with final Table1 (e.g. sardine 2.085 versus 114.92 for 1985). The 2013 panel also has rounding/detailed-value differences. Both images and all 40 biomass comparisons per panel are retained; they do not define another complete balanced model. The publisher site lists one DOCX supplement containing nine resources, verified byte-identical on 2026-09-28; no native EwE file was found.

## Taxonomy and structure

Supplement S3 provides representative taxa, not an exhaustive membership list. Its #6 Amberjack is associated with main #6 Yellowtail through Seriola quinqueradiata and the main prose. S3 reverses #29 Sole and #30 Dragonet relative to Table1 (#29 Dragonet, #30 Tongue sole); taxonomy was reconciled by names, with both source numbers retained. S3 Tuna says Thunnus thynnus but main p.585 says Thunnus orientalis; the conflict is retained without treating the names as synonyms. Source spellings, including apparent typographical errors, remain unchanged. Three basal groups have no species list; Polychaeta points to 29 species in an earlier reference without listing them. Taxonomy.xlsx has exactly one row per source group.

The model is a mixture of named taxa and species pools, with no spatial strata. Coastal Kyoto area is 2,230 km² to 240 m depth, a local portion of the Sea of Japan. No whole-LME coverage percentage was derived and no annual regional PPR was calculated.

## Validation and loader audit

All eight import tables exist. Format validation returned 0 errors and 42 warnings (unreported GS, BA, routing); this is a format result, not scientific admission. The separate massbalance_check returned {'5 errors and 22 warnings' if year==1985 else '0 errors and 6 warnings'} under its conditional treatment of unknown BA/migration as zero and defaults. {'The EE>1 groups are #10 Spanish mackerel, #20 Flying squid, #28 Bivalve, #29 Dragonet, #31 Goby.' if year==1985 else 'EE discrepancies >0.05 occur for #12 Flounder, #13 Black porgy, #23 Ivory shell, #26 Crab, #27 Prawn, #37 Mysid.'} Flagged values were checked against rendered Table1 and Table2; no values were repaired. Inference from these checks must retain the unknown BA/migration caveat.

The converter's normalized database output is retained only as a conversion artifact in extracted_tables. All its diet normalization and undocumented defaults were reversed in source model.json, with a field-level reversal audit. Supported source numeric fields and explicit diet cells roundtrip successfully. The converter reconstruction is lossy for blank diets/routing and fleet detail; those losses are documented in evidence/ROUNDTRIP_VERIFICATION.json and never overwrite the eight import files.

The current regional loader successfully built the source JSON for diagnostics, normalizing diet totals, defaulting missing consumer GS to 0.2 and catch/migration terms, closing the single-detritus routing, recalculating TL and GE, and solving unreported BA/flows. It changed {len(changes)} recorded parameter/flow cells and {len(diet_changes)} diet cells relative to the retained ModelData state. Exact loaded matrices, parameters, all solved BA values and field-by-field changes are under evidence/. Its numerically balanced state is not source validation. Direct SPPR return values are reported separately in SPPR_DIAGNOSTICS.md.

## Provenance and decision

Main PDF SHA-256 eaca3b45c0e93645aa071099876a4490ac5cac4418a3eb4472ef8a85188a46c3.
Supplement SHA-256 8d668bb077ed7149b8bd83a862d46911fabb16c3b34bb3553b399ecc7071602e.
Source URLs, byte counts, retrieval results, extraction code and exact diagnostic-code hashes are retained. No source bytes were changed. Project.xlsx and the regional workbook were not edited. Central registration is proposed, with model adoption pending. Author/native year-specific files would resolve the principal source-admission blocker; a repaired or pooled experiment would require a separate explicit decision.
'''
 (dest/'REPORT.md').write_text(model_report,encoding='utf8')
 (et/'MODEL_PROFILE.md').write_text(f'# Coastal Kyoto {year}\n\n40 groups: 38 consumers, phytoplankton, detritus. Mixed species and taxonomic pools; no spatial strata. Model area 2230 km², coastline to 240 m off Kyoto. S3 membership is representative, with group-number and tuna-identity conflicts documented in ../REPORT.md. Exact production model selection pending.\n',encoding='utf8')
 overall.extend([f'- [{mid}](../{mid}/REPORT.md): 40 groups; source admission unresolved; all requested diagnostic calls returned WARN.'])
 proposals.append({'unit_id':'LME_050','model_id':mid,'model_path':f'regions/LME_050/models/{mid}/model.json','source_filename':'Inoue_et_al_2023_Sea_of_Japan-eaca3b45.pdf','selected':False,'selection_rationale':'Paper USER-PREFERRED/SPECIFIED SOURCE: only available paper. Exact model selection pending.','paper_ids':'SOJ-2023__LME_050','model_year':year,'variant':'Published Table1/S4 year-specific parameters with shared Table2 caption-linked diet; original diet version unresolved','model_area_km2':2230,'availability':'extracted; bounded direct diagnostics complete; source admission unresolved','publication_year':2023,'model_years':str(year),'target_coverage_ratio':None,'coverage_class':'partial','doi':paper['doi'],'coverage_note':paper['coverage_note']})
 audits.append({'model_id':mid,**strict,'roundtrip':rt})
 # Report only direct method returns, with every returned leaf retained and compared.
 selected=[r for r in results if r['model_id']==mid];f=[flat(r['direct_diagnose_sppr_return']) for r in selected]
 lines=[f'# Direct SPPR diagnostics — Coastal Kyoto {year}','','Calls: `PPRCalculator.diagnose_sppr(short=False, flat=False, return_sppr=False)`, with GE, TE, and With Egestion. Complete values below are returned diagnostics; displayed floats are abbreviated to 10 significant digits. JSON retains full precision. Footprints are model-internal quantities, not regional annual PPR.','', '| Returned field | GE | TE | With Egestion |','|---|---:|---:|---:|']
 for key in dict.fromkeys(k for d in f for k in d):lines.append('| '+key+' | '+' | '.join(fmt(d.get(key)) for d in f)+' |')
 lines.extend(['','Raw JSON: '+', '.join(f'[{r["TE_option"]}](evidence/diagnose_sppr_{r["TE_option"].replace(" ","_")}.json)' for r in selected)+'.'])
 (dest/'SPPR_DIAGNOSTICS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
overall.extend(['','## Separate diagnostic report','', '[Direct GE / TE / With Egestion diagnostics](SPPR_DIAGNOSTICS_REPORT.md). Raw method returns are retained in DIAGNOSE_SPPR_RESULTS.json.','', '## Registration and selection','', 'Existing paper row SOJ-2023__LME_050 was found; no existing LME_050 model rows were found. Reuse that paper row and add the two local model IDs. Preserve existing scores, rankings, filter tables and preferences of other regions. The central proposal is unregistered until the parent grants a serialized Project.xlsx write slot. Regional Overview remains unchanged and exact model selection remains pending.'])
(REV/'REPORT.md').write_text('\n'.join(overall)+'\n',encoding='utf8')
dump(REV/'CENTRAL_REGISTRATION_PROPOSAL.json',{'status':'prepared_not_registered','paper_existing_key':{'article_id':'SOJ-2023__LME_050','unit_id':'LME_050'},'paper_fields_to_update':{'title':paper['title'],'authors':paper['authors'],'model_years':'1985 and 2013','functional_groups':'40','supplement_status':'One publisher DOCX, nine resources, exact-byte verified','notes':'USER-PREFERRED/SPECIFIED SOURCE; reason: only available paper. Exact model choice pending. Source/diet conflicts in regions/LME_050/models/extraction_review_20260928/REPORT.md; direct diagnostics in SPPR_DIAGNOSTICS_REPORT.md.','correction_notes':paper['source_identity_verified']+' Prior correction text retained in regional evidence/source_metadata_before_review.json.','full_model_loadable':'Both tabulated reconstructions load with transformations; original year-specific diet versions unresolved','loadability_evidence':'regions/LME_050/models/extraction_review_20260928/REPORT.md'},'models_to_append':proposals,'preserve':['all scores','region_rank','atlas_region_rank','existing paper selection status until agreed schema for source preference','all other region rows','all 13 native table/filter definitions'],'production_model_selection':'pending'})
dump(REV/'EXTRACTION_AUDIT.json',audits)
lines=['# LME_050 direct SPPR diagnostics','','Only the complete direct `diagnose_sppr()` returns for GE, TE and With Egestion are represented. Footprint quantities belong to the loaded coastal-Kyoto models; they are not regional annual PPR.','', '| Year | Configuration | Status | b | Living spectral radius | Balance relative gap | PPR all | PPR inner | PPR PP only |','|---|---|---|---:|---:|---:|---:|---:|---:|']
for r in results:
 d=r['direct_diagnose_sppr_return'];fp=d['footprint'];lines.append('| '+' | '.join(fmt(v) for v in [r['model_id'][-5:-1],r['TE_option'],d['status'],d['divergence']['b'],d['divergence']['rho_living'],d['balance']['rel_gap'],fp['ppr_all'],fp['ppr_inner'],fp['ppr_pp_only']])+' |')
lines.extend(['','Complete readable returned fields:',''])
for year in [1985,2013]:
 mid=f'50_50{year}_Coastal_Kyoto_Inoue_({year})';lines.append(f'- [{year}: model_input, divergence, balance, footprint, config, warnings](../{mid}/SPPR_DIAGNOSTICS.md)')
lines.extend(['','[Complete full-precision method-return JSON](DIAGNOSE_SPPR_RESULTS.json). All six calls returned `WARN`; all report zero negative sources. EE=0 groups are #23 Ivory shell and #34 Brittle star in 1985, and #30 Tongue sole in 2013. The TE return warns that its recycling matrix is absent and b=0 by construction.'])
(REV/'SPPR_DIAGNOSTICS_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('Verified',len(audits),'models; wrote separate source and direct-diagnostic reports; central registration pending.')
