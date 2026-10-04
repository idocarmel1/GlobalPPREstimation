"""Independent source/canonical checks and review deliverables; no workbook adoption."""
from pathlib import Path
import json,csv,hashlib,sys,re
from decimal import Decimal
from openpyxl import load_workbook
import numpy as np
ROOT=Path(__file__).resolve().parents[3];REVIEW=Path(__file__).parent
MODEL=ROOT/'regions/LME_003/models/CAL-2016_California_Current_2000-2014';T=MODEL/'extracted_tables';D=MODEL/'diagnostics'
P=ROOT/'regions/LME_003/papers/CAL-2016';S=P/'author_archive_extracted/CalCurFoodWebModelECOMOD-master'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
pars=list(csv.DictReader((S/'Koehn.et.al.2016_parameters.csv').open()));source=load(T/'model.json');can=load(MODEL/'model.json')
paper=load(T/'paper_table1_coordinate_rows.json');order=list(range(1,71))+list(range(86,93))+list(range(71,86))+[93]
assert len(paper)==len(order)==93
fields=['density','CV_bio','PB','PB_CV','QB','QB_CV','EE','Yield','Y_CV'];comparisons=[];diff=[]
for row,seq in zip(paper,order):
 for j,k in enumerate(fields,1):
  printed=row['cells'][j];v=Decimal(pars[seq-1][k]);ok=(v<0) if printed=='–' else abs(v-Decimal(printed))<=Decimal('0.5')*Decimal(10)**Decimal(printed).as_tuple().exponent
  rec={'seq':seq,'group_name':source['groups'][seq-1]['name'],'paper_name':row['cells'][0],'pdf_page':row['pdf_page'],'field':k,'paper_value':printed,'author_csv_value':str(v),'matches_at_printed_precision':bool(ok)}
  comparisons.append(rec)
  if not ok:diff.append(rec)
dump(T/'paper_vs_author_parameters.json',{'cells_checked':len(comparisons),'differences':diff,'all_cells':comparisons})
assert len(can['group'])==93
numeric_checks=0
for g,s in zip(can['group'],source['groups']):
 assert int(g['group_seq'])==s['n'] and g['group_name']==s['name']
 for key,sk in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('biomass_accum','ba')]:
  expected=s.get(sk)
  assert (g[key]=='-9999') if expected is None else Decimal(g[key])==Decimal(expected),(g['group_name'],key)
  numeric_checks+=1
 assert g['gs']=='-9999'
 assert Decimal(g['export'])==Decimal(pars[s['n']-1]['Yield'])
 assert g['taxon_descr']
 if 2<=s['n']<=92:
  diets=g['diet_descr']['diet'];diets=diets if isinstance(diets,list) else [diets]
  prop={int(x['prey_seq']):Decimal(x['proportion']) for x in diets}
  for j in range(1,94):assert prop.get(j,Decimal(0))==Decimal(source['diet'][str(s['n'])][str(j)])
  assert Decimal(g['diet_imp'])==Decimal(source['diet'][str(s['n'])]['import'])
raw=load(T/next(T.glob('3_California*.json')).name)
wb=load_workbook(next(T.glob('*_reconstructed.xlsx')),data_only=True)
rows=list(wb['Basic input'].values)[1:]
for row,g in zip(rows,raw['group']):
 assert str(row[0])==g['group_seq'] and row[1]==g['group_name']
 for idx,k in [(3,'biomass_habitat_area'),(4,'pb'),(5,'qb'),(6,'ee'),(8,'gs')]:
  assert row[idx] is None if g[k]=='-9999' else np.isclose(float(row[idx]),float(g[k]),rtol=1e-14,atol=0)
basic=load(T/'author_equation_solution.json');returns={o:load(D/f'{o.lower().replace(" ","_")}_direct_return.json') for o in ['GE','TE','With Egestion']}
summary={'model_id':MODEL.name,'paper_id':'CAL-2016','unit_id':'LME_003','period':'2000-2014','groups':93,'living_groups':92,'model_count':1,'extraction_status':'complete with source qualifications','source_unknown_B_count':26,'source_unknown_EE_count':67,'source_GS_unknown_count':93,'canonical_checks':{'scalar_cells':numeric_checks,'all_8463_internal_consumer_diet_cells_unchanged':True,'all_91_diet_import_cells_unchanged':True,'all_93_catches_unchanged':True,'all_93_taxonomy_rows_present':True,'basic_input_roundtrip_93_rows_5_numeric_fields_passed':True},'paper_table_checks':{'cells':837,'differences':diff},'source_balance':{'living_equations_max_absolute_residual':basic['max_abs_production_residual'],'author_detritus_EE':basic['author_detritus_EE'],'strict_source_admission':'qualified: source GS unknown; total catch includes discards but split unavailable; author detritus accounting omits egestion'},'diagnostics':{},'production_eligible':False,'selected':False}
for o,r in returns.items():summary['diagnostics'][o]={'status':r['status'],'model_input':r['model_input'],'divergence':r['divergence'],'balance':r['balance'],'raw_return_path':(D/f'{o.lower().replace(" ","_")}_direct_return.json').relative_to(ROOT).as_posix()}
dump(REVIEW/'results_record.json',summary)

report=f'''# California Current, Koehn et al. (2016), 2000–2014

Extracted 2026-09-28. One author baseline model: **93 groups, comprising 92 living groups and one detritus pool**. Model ID: `{MODEL.name}`. Canonical source JSON preserves 26 unknown biomasses and 67 unknown EEs as -9999. All eight EwE import files and all 93 taxonomy rows are retained. This candidate is **not selected or approved for regional production**.

## Source tables and provenance

Koehn, L.E., Essington, T.E., Marshall, K.N., Kaplan, I.C., Sydeman, W.J., Szoboszlai, A.I., and Thayer, J.A. (2016). Developing a high taxonomic resolution food web model to assess the functional role of forage fish in the California Current ecosystem. Ecological Modelling 335:87–100. DOI: 10.1016/j.ecolmodel.2016.05.010.

The supplied PDF and ZIP remain unchanged. ZIP extraction checked resolved paths against the destination and verified bytes on repeated extraction. All six archive members were hashed. Publisher Appendix A (`mmc1.xlsx`) and Appendix B (`mmc2.docx`) were recovered from ars.els-cdn.com and archived exactly; actual retrieval results and SHA-256 hashes are in the review folder. Appendix A has one visible sheet, no hidden sheets. It contains 94 prey/import rows and 93 predator columns; the final two rows are diet pedigree and Dirichlet multipliers, not prey. Its 8,742 numeric diet cells match the author CSV exactly.

Author groupinfo gives B, EE, PB, QB, group type, BA and diet import. Author parameters repeats B/EE/PB/QB and provides total Yield and parameter CVs. All 372 repeated parameter cells agree numerically. Source `-1` means an input to be solved, never observed negative biomass. GCE=0 is an unused placeholder: author R computes PB/QB at output, so it is not imported as a true GE of zero. Source data are biomass density in t/km², rates per year, and catch in t/km²/year (Appendix B individual parameter explanations).

Table 1 (PDF pages 3–4, printed 89–90) has columns B, B CV, PB, PB CV, QB, QB CV, EE, C, C CV. Caption states dashes are model-solved parameters. Both pages were rendered; numerical cells were separately extracted by coordinates with page-specific boundaries. All 837 printed parameter/CV cells were compared at printed precision; **{len(diff)} differences** are listed in `paper_vs_author_parameters.json`. The machine-readable author values are retained without averaging or adjustment. The manuscript is not numbered: sequence follows groupinfo and both diet sources; a crosswalk handles its different bird/mammal display order.

`parameters.csv` reverses Shelf/Slope rockfish names at rows 39 and 55 relative to groupinfo and manuscript Table 1. Groupinfo + Table 1 identities agree on B/PB/QB values and are retained; labels, matrix aliases and source cell positions are preserved in evidence files. This discrepancy is not concealed by matching names alone. Appendix B provides the separate Shelf Rockfish and Slope Rockfish sections used for membership.

## Biomass accumulation and migration

All 93 groupinfo BA cells explicitly equal zero, also enforced by author Monte Carlo code. These are source zeros. The paper PDF page 2 / printed 88 explicitly assumes steady state and excludes migration; canonical immigration/emigration are consequently zero. Imported feeding is retained separately, exactly matching groupinfo Import, the last CSV diet row and Appendix A Input Consumption. No time-series slopes were inferred.

## Values from prose and taxonomy

The model averages 2000–2014 (PDF page 2 / printed 88). Model area is 302,000 km²: northern Vancouver Island to Punta Eugenia, offshore to the 2,000-m isobath (PDF page 4 / printed 90, Fig. 1). These do not establish a measured percentage of LME_003 coverage. Prior inherited target-polygon geometry is contextual only.

Appendix B was read by paragraph, with full group sections retained in `taxonomy_source_evidence.json`; `Taxonomy.xlsx`, taxonomy.csv and canonical taxon_descr carry the section heading and first descriptive paragraph for every living group. Original scientific spellings, author examples and broad guild definitions are retained. The evidence artifact retains additional membership and diet paragraphs; diet examples do not establish exhaustive membership or catch allocation. No species matching/weights were inferred.

## Conventions applied

No source diet normalization, undocumented pooling, balancing correction or default B=1 was applied. Author R explicitly routes unused living production to the sole detritus pool; the 92 living fate rows record that single destination. The detritus self-row remains blank in the imports; the downstream loader inserts its self-identity. Habitat-area 1 in the converter is a representation convention because author biomass already refers to the whole model area.

The author code's detritus inflow omits egestion. GS is not parameterized anywhere in the retrieved bundle; canonical GS stays unknown. For numerical diagnostics only, the documented loader supplies GS=0.2 for 91 consumers and applies the same single-pool routing to egestion. This is an explicit extension of the author's accounting, not an author estimate. The loader builds derived detritus flows/EE and an external diet-import group; it does not normalize the diet. Complete source-to-staging changes and loaded group values are retained.

## Deliberate blanks

Biomass (26 groups), EE (67), GS (93), TL (93), total mortality as a separate input, source GE, and separate landings/discards remain absent where unreported. Author Yield is total catch including bycatch and discards (PDF page 2, Eq. 1); it is carried in Landings.csv under the explicitly labeled `Total catch including discards` column, per import convention. Discards.csv stays blank and no discard return to detritus is invented. Missing detritus import remains unknown in canonical; loader zero is a diagnostic default.

## Validation

The bundled validator reports 6 quote-character errors because it rejects literal apostrophes in authentic group labels (Cassin's auklet, Leach's S. Petrel, Brandt's corm.) in each of the six CSVs. These are label characters, not CSV quoting: exact names are intentionally preserved. A separate source-cell verification passes all scalar and diet checks. Its three warnings are blank GS, the unreported detritus self-fate row, and unknown TL. These are source/convention limitations, not silently filled source observations.

Canonical/source comparison verifies 465 scalar parameter cells, 8,463 internal consumer diet cells, 91 diet imports, 93 catches, and all taxonomy rows. The reconstructed workbook independently matches all 93 basic-input rows and their five numerical/missing fields. The converter round trip loses original metadata structure, blank-vs-zero diet cells, separate fleet/discard structure and unresolved detritus self-routing; those remain authoritative in the eight original imports. Canonical is copied from conversion with only explicit no-migration values and source metadata added. Roundtrip is not claimed as a byte-identical eight-file rebuild.

## Mass balance

The source-only bundled checker reports 0 errors, 32 warnings and 2 notes, but has incomplete B/EE and therefore cannot certify the source's solved balance. Warnings include very small P/Q of birds/mammals, which agree with the reported high Q/B; they were not adjusted. Its automated verdict is not substituted for admission review.

A separate audited transcription of the author R linear equations solves the 26 unknown B and 66 unknown living EE simultaneously. A second reduced system gives identical B. Maximum production-equation residual is {basic['max_abs_production_residual']:.3g} t/km²/year; all living EE lie in [0, {basic['max_living_EE']:.8f}]. Author detritus input is {basic['author_detritus_inflow_unused_production_only']:.9f}, consumption {basic['author_detritus_consumption']:.9f}, EE {basic['author_detritus_EE']:.9f}; these explicitly exclude egestion. Derived values live in a separate solution and diagnostic staging, never overwrite canonical unknowns, and retain source input flags.

## Direct SPPR diagnostics

Only `PPRCalculator.diagnose_sppr(TE_option=..., short=False, flat=False)` was invoked for GE, TE and With Egestion. Each returned a full nested report; each complete unmodified return is retained in diagnostics. No global exporter, 22-method run, Monte Carlo run or regional PPR was performed. The adapter filename uses 2016 only as a required numeric loader token, not an EcoBase accession; its year string remains 2000–2014. Loader's hard-coded lme=13 was corrected to 3 in memory, without changing equations or canonical source.

'''
for o,r in returns.items():
 report+=f"- **{o}: {r['status']}**; input {r['model_input']['status']}; model balanced={r['model_input']['is_model_balanced']}; recycling b={r['divergence']['b']:.9g}; living spectral radius={r['divergence']['rho_living']:.9g}; PP-balance {r['balance']['status']}, relative gap={r['balance']['rel_gap']:.3g}; negative sources={r['divergence']['n_negative_sources']}.\n"
report+='\nThe exact method WARN results are distinct from source qualifications. Twenty-one zero-EE groups and near-singular TE groups include unfished predators; full group IDs and warnings are retained. Good completed balance includes documented loader defaults and does not validate missing source GS or authorize adoption.\n'
(T/'REPORT.md').write_text(report,encoding='utf-8')
diag='# Full direct SPPR diagnostic returns\n\nModel: '+MODEL.name+'\n\nSource admission and loader transformations are documented in extracted_tables/REPORT.md and staging_transformations.json. Returns below are verbatim serialized nested outputs; no extra configurations were invoked.\n'
for o,r in returns.items():diag+=f'\n## {o}\n\n```json\n'+json.dumps(r,indent=2,ensure_ascii=False)+'\n```\n'
(D/'DIRECT_SPPR_REPORT.md').write_text(diag,encoding='utf-8')
(T/'MODEL_PROFILE.md').write_text('''# California Current (2000–2014)

Axis: mainly taxonomic; includes juvenile/adult life stages and several feeding guilds.
Prefixes: Juv. are life stages; no geographic stratum prefixes.
Area: 302,000 km², northern Vancouver Island–Punta Eugenia, offshore to 2,000 m; no validated percentage of LME_003.
Single groups: explicit forage taxa; numerous species-specific fish, birds and mammals.
Pools: plankton, benthic invertebrates, cephalopods excluding market squid, grouped rockfish, sharks, cetaceans and other groups as defined in Appendix B.
Membership: Appendix B sections retained with paragraph coordinates; original taxonomy unmodified.
Catch: author total removals available, without landings/discards split; taxonomy is prepared but catch mapping is not authorized or performed.
Selection: no model selected. Canonical unknowns and independently solved diagnostic input remain separate.
''',encoding='utf-8')
(REVIEW/'MASTER_INDEX.md').write_text(f'''# LME_003 extraction review, 2026-09-28

| Model | Period | Groups | Status | Direct diagnostics |
|---|---|---:|---|---|
| {MODEL.name} | 2000–2014 | 93 | Extracted and verified, source qualifications retained | GE WARN; TE WARN; With Egestion WARN |

Full extraction: ../models/{MODEL.name}/extracted_tables/REPORT.md

Full direct returns: ../models/{MODEL.name}/diagnostics/DIRECT_SPPR_REPORT.md

Machine-readable review: results_record.json. Source hashes: source_manifest.json. Supplement retrieval: supplement_retrieval.json. No regional model selection, annual PPR or Project.xlsx write performed.
''',encoding='utf-8')
proposal={'unit_id':'LME_003','paper_id':'CAL-2016','model_id':MODEL.name,'model_path':(MODEL/'model.json').relative_to(ROOT).as_posix(),'publication_year':2016,'model_years':'2000-2014','model_name':'California Current','title':'Developing a high taxonomic resolution food web model to assess the functional role of forage fish in the California Current ecosystem','doi':'10.1016/j.ecolmodel.2016.05.010','groups':93,'living_groups':92,'area_km2':302000,'coverage_pct':None,'coverage_evidence':'PDF p4/printed90 and Fig1, northern Vancouver Island to Punta Eugenia, offshore 2000m; no measured LME overlap fraction','extraction_status':'complete with source qualifications','diagnostic_status':'GE WARN; TE WARN; With Egestion WARN','production_eligible':False,'selected':False,'notes':'93-group source canonical preserves 26 B and 67 EE unknowns; independently solved diagnostic staging uses audited loader GS defaults. Full publisher Appendix A/B recovered. No adoption authorized.','review_path':(T/'REPORT.md').relative_to(ROOT).as_posix()}
dump(REVIEW/'central_metadata_proposal.json',proposal)
print(json.dumps({'paper_differences':diff,'checks':'passed','diagnostics':{k:v['status'] for k,v in returns.items()}},indent=2))
