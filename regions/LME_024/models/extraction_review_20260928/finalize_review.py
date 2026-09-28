from pathlib import Path
import json,csv,hashlib,shutil,math
from decimal import Decimal
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[4];R=Path(__file__).resolve().parent
MID='Hernvann_2020_Celtic_Sea_1985';MD=ROOT/'regions/LME_024/models'/MID;ED=MD/'extracted_tables'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
inp=read(R/'extraction_input.json');db=read(MD/'model.json');ev=read(R/'cell_evidence.json')
for e in ev:
 e['source_file']='Data_Sheet_1_TheCelticSeaThroughTimeandSpa-165f24b6.docx'
 e['rendered_page']={'B4':17,'B3':16,'B2':14 if e.get('docx_table')==2 else 15}[e['table']]
save(R/'cell_evidence.json',ev)
shutil.copy2(R/'cell_evidence.json',ED/'cell_evidence.json')
shutil.copy2(R/'taxonomy_evidence.json',ED/'taxonomy_evidence.json')
checks=[]
def check(label,actual,expected):
 ok=actual==expected;checks.append({'check':label,'passed':ok,'actual':actual,'expected':expected});assert ok,label
check('group_count',len(db['group']),54)
for sg,g in zip(db['group'],inp['groups']):
 for source,target in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('pq','ge'),('unassim','gs'),('tl','tl'),('ba_rate','biomass_accum_rate')]:
  check(f'group {g["n"]}: source {source} preserved',sg[target],g[source] or '-9999')
 if g['n']<=50:
  diets={d['prey_seq']:d['proportion'] for d in sg['diet_descr']['diet']}
  for prey,value in inp['diet'][str(g['n'])].items():
   actual=sg['diet_imp'] if prey=='import' else diets.get(prey,'-9999')
   check(f'diet predator {g["n"]} prey {prey}',actual,value or '-9999')
 check(f'catch group {g["n"]}',Decimal(sg['export'])==sum((Decimal(inp[k][str(g['n'])]['Total fishery']) for k in ['landings','discards']),Decimal(0)),True)
names=['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']
for name in names:check('required import '+name,(ED/name).exists(),True)
w=load_workbook(next(R.glob('*_reconstructed.xlsx')),read_only=True,data_only=True)
br=list(w['Basic input'].values)
for row,g in zip(br[1:],inp['groups']):
 for ix,field in [(3,'biomass'),(4,'pb'),(5,'qb'),(6,'ee'),(8,'unassim')]:
  check(f'reconstruction basic {g["n"]} {field}',row[ix],float(g[field]) if g[field] is not None else None)
tax=list(w['Taxonomy'].values)[1:]
check('reconstructed taxonomy group count',len(tax),54)
for row,g in zip(tax,db['group']):check('taxonomy '+g['group_seq'],row[2],g['taxon_descr'])
tl=list(w['TL'].values)[1:]
for row,g in zip(tl,inp['groups']):check('reconstructed TL '+str(g['n']),row[2],float(g['tl']))
inv=read(R/'source_inventory.json')
for f in inv:check('source SHA256 '+f['file'],hashlib.sha256((ROOT/'regions/LME_024/papers/LME024-Hernvann-2020'/f['file']).read_bytes()).hexdigest(),f['sha256'])
save(R/'verification_checks.json',checks)
save(R/'verification_summary.json',{'passed':sum(x['passed'] for x in checks),'failed':0,'source_unchanged':True,'source_json_sha256':hashlib.sha256((MD/'model.json').read_bytes()).hexdigest(),'reconstruction_limits':['Standard converter merges landings and discards as export and removes zero-catch rows. Original separate import tables remain authoritative.','Standard reconstructed diet/fate sheets zero-fill blanks. Blank/explicit-zero identity remains in source CSV, extraction JSON and cell evidence.','Standard reconstructed basic sheet omits printed P/Q even though source model.json ge preserves it.','Habitat-area default and diet normalization in converter_raw.json were restored to source values in model.json; all changes logged.']})
profile='''# Celtic Sea, 1985 — structural profile

54 numbered groups: 50 consumers, two primary producers, two detritus pools. The article reports 50 functional groups and then describes life-stage splits, but its headline count does not fully reconcile with B4; the definitive extracted spine is B4 numbers 1–54. Cod, hake and anglerfish each have separate adult/juvenile rows. No spatial strata or group-number prefixes. The other axes are taxon, feeding guild and plankton size; B1 gives species and guild definitions. B1 merged cells were followed explicitly. Two seal rows exchange the common/Latin columns; source spelling and correction evidence are retained. No taxonomic synonym modernization or catch matching was performed.

Area: Celtic Sea shelf shallower than 200 m, matching ICES 7.e, 7.f, 7.g, 7.h and 7.j.2 (article Fig. 1, p. 3). This is a subregion of LME_024, not its complete Celtic–Biscay Shelf. No defensible numeric model area or target coverage percentage was located; neither is inferred from the map.

B1 has no dedicated bacterial composition row. Bacteria and the two detritus groups therefore carry explicit `not documented` descriptions. All other groups carry B1 members or guild descriptions. Life-stage thresholds are not specified in the supplied table.
'''
(ED/'MODEL_PROFILE.md').write_text(profile,encoding='utf8')
report='''# Hernvann et al. (2020): Celtic Sea 1985 extraction and diagnostic review

**Status: source extraction completed; numerical SPPR admission blocked.** Model ID: `Hernvann_2020_Celtic_Sea_1985`. No selection, regional PPR publication or workbook changes were made.

## Sources and model identity

Hernvann P.-Y., Gascuel D., Grüss A., Druon J.-N., Kopp D., Perez I., Piroddi C. and Robert M. (2020), *The Celtic Sea Through Time and Space: Ecosystem Modeling to Unravel Fishing and Climate Change Impacts on Food-Web Structure and Dynamics*, Frontiers in Marine Science 7:578717. DOI: 10.3389/fmars.2020.578717.

The 26-page article and the complete 70-page Word supplement were inventoried and hashed alongside metadata and README. The article is `pdf-fbcccb63.pdf`; the supplement is `Data_Sheet_1_TheCelticSeaThroughTimeandSpa-165f24b6.docx`. Exact hashes are in `source_inventory.json`. The skill renderer failed because bundled LibreOffice is unavailable; read-only Microsoft Word export produced `supplement_word_render.pdf`. Its printed page numbers match the page locators below. XML table-cell extraction retained decimal text, blank cells, explicit zeros and bold runs. Relevant table layouts and prose were checked in rendered images in `visual_evidence/`.

The sole fully tabulated Ecopath parameterization is the **1985 baseline**. B4 combines its input parameters and post-balancing estimates (bold); it is not a second initial model. B2 is explicitly the 1985 diet, derived from 2016 EcoDiet information using relative prey-abundance changes (supplement pp. 7–8). Neither the 2016 diet prior nor the inherited 1980/2013 Moullec models is a complete separate parameterization in this bundle. The 1985–2016 simulation is not 32 independent Ecopath models.

The article p. 6 reports six additional Ecosim-generated mean-period Ecopath snapshots, used for Ecospace. The supplied supplement contains environmental maps, dispersal parameters and vulnerabilities, but no complete B/PB/QB/EE/diet/fishery sets for those six snapshots. These are recorded as unavailable parameterizations in `model_inventory.json`; no synthetic model.json is made for them. Source period labels conflict: article p. 6 says 2005–2010 and 2011–2016; maps/table 8 use 2005–2009 and 2010–2016. This conflict remains recorded.

## Source tables and mapping

| Source | Rendered page | Structure and extraction |
|---|---|---|
| B1, DOCX table 1 | 9–13 | 214 body rows, species composition and guild definitions; 54-row Taxonomy.xlsx after explicit group-name/life-stage crosswalk |
| B2, tables 2–3 | 14–15 | Prey rows 1–54 and Import; predator columns 1–25 and 26–50; all 2,750 source cells retained |
| B3, table 4 | 16 | Landings/discards, 54 groups; Anglerfish/Hake/Cod aggregate headings and final Sum are not groups |
| B4, table 5 | 17 | ID, group, TL, B, P/B, C/B, EE, P/C, BA, Unassim; C/B→QB, P/C→PQ, BA(y−1)→BA rate, Unassim→GS |
| B5/B6 and Fig. B1–B8 | 18–26 | Pedigree and PREBAL context; not additional final input matrices |
| F1–F3; G1 | 61–66; 68 | Ecosim controls, time-series inventory, vulnerabilities and Ecospace dispersal; not additional Ecopath baselines |

Biomass is printed t/km²; annual rates are kept as printed. B3 omits units in its local caption; its values are carried as the Ecopath fishery density inputs, conventionally t/km²/year, without conversion. This unit interpretation is distinguished from an explicit caption statement. No numeric study area or wet/dry conversion was supplied, so none was invented. B4 sometimes labels rates redundantly as /y−1; their intended annual-rate interpretation follows the table and model context.

Exact numerical precision is kept in the eight import tables. Decimal commas were converted to decimal points only. `0.00` bird biomass is a **printed zero**, not an unknown solved to an arbitrary positive number. All catch rows include explicit zeros. Source spelling differences are retained in `group_name_crosswalk.json`, including carnivorous/piscivorous demersal elasmobranchs.

## Biomass accumulation, assimilation and deliberate blanks

B4 supplies BA rate for every group: zero except Plaice −0.01/year, Discards 0.40/year and Detritus 3.88/year. Those rates stay in the rate column; the converter's absolute BA is an explicitly derived rate × printed B (Plaice −0.0004, Discards 0.1, Detritus 481.12 t/km²/year). No balance-check suggested BA was adopted. The large detritus value follows the published BA column and is not reclassified as an import. Article and complete supplement prose, tables and PREBAL figures were searched for alternatives.

All 50 consumers have source GS values; no default GS was needed. B4 PB is blank for six adult/juvenile groups 9–14, EE is blank for Megrim (18), producer/detritus QB is blank, and habitat-area fractions, detritus imports and numeric detritus-fate fractions are absent. B1–B6, SA equations, SF stability discussion and SG were checked. SF p. 57 links the discard pool to fishing, but does not provide a numeric mortality/egestion routing matrix; this qualitative statement is not expanded into invented fractions.

`computable_unknowns.json` and `computational_copy.json` document Megrim EE from the production equation, and the algebraic PB=PQ×QB candidates for six life stages. There are **no missing biomasses** for a coupled B/EE solve; all B values are present, including the printed zeros. These derivations do not replace source fields. Multistanza transfers and the consistency of rounded source PQ remain unresolved, so the computational copy is not a validated EwE reconstruction.

## Source balance and internal conflicts

The import validator reports **0 errors and 54 warnings**, all for missing detritus fate. The independent source mass-balance check reports **2 errors, 15 warnings and 44 notes**; full per-group values are in `source_massbalance.log` and `independent_source_balance.json`.

With the published diet, catch and BA, reconstructed EE is **1.0124673643 for Haddock** and **1.0264833333 for Plaice**. Printed B4 values were visually confirmed and retained. Eleven printed/recomputed EE differences exceed 0.05; the largest is Carnivores/Necrophages, about 0.247. These are reconstruction findings, not evidence that the authors' full-precision native model necessarily failed. Missing transfers/migration, precision and differing source parameter stages can matter. No rates, catches or diets were changed to force balance.

Printed PQ is also inconsistent with PB/QB beyond simple two-decimal rounding for groups 46–48 and Bacteria (50): bacteria prints 0.31 but PB/QB=0.40. PREBAL figures have additional apparent differences from B4 (for example juvenile hake PB). Graph axes are logarithmic and were not digitized into replacements. Both source forms remain available for review.

## Converter and round-trip checks

The maintained writer produced all eight EwE import files and the maintained converter generated its original JSON and reconstructed workbook. `converter_raw.json` preserves that result. The converter normalizes rounded diets, defaults habitat area to 1, drops PQ/TL and explicit-zero diet cells, and combines landings+discards. These transformations are not accepted as source data. `model.json` restores source diets, explicit zeros, source PQ/TL and unknown habitat/routing sentinels; each restoration is recorded in `converter_source_restoration.json`.

A second reconstructed workbook was generated from the restored source database JSON. Automated checks compare every source parameter, all 2,750 diet/import cells, all total catches, reconstructed basic parameters, taxonomy and TL, and unchanged source hashes. See `verification_summary.json` and `verification_checks.json`. The converter's workbook still collapses blank diets to zeros, merges landings/discards into export and omits PQ: it is a numerical cross-check, not a lossless replacement for the authoritative eight tables and evidence. The local serialization number 2402020 is not an EcoBase accession; its filename is solely required by the loader. Run reconstruction and diagnostics with Python UTF-8 mode (python -X utf8) because the preserved loader/converter use the Windows default text encoding; an initial taxonomy-encoding mismatch was detected by verification and corrected by rerunning in UTF-8 mode.

## Requested direct diagnostics

| Requested call | Outcome | Raw return |
|---|---|---|
| diagnose_sppr(TE_option='GE', short=False, flat=False) | NOT_RUN: constructor admission failed | None |
| diagnose_sppr(TE_option='TE', short=False, flat=False) | NOT_RUN: constructor admission failed | None |
| diagnose_sppr(TE_option='With Egestion', short=False, flat=False) | NOT_RUN: constructor admission failed | None |

Strict source admission and standard defaults both raise on diet sums, which range **0.996–1.002**. At a 0.001 tolerance the actual loader flags 19 consumers, including floating-point boundary cases. A separate, explicitly documented use of the loader's `normalize_DC=True` option confirms the deeper blocker. Its exact exception is:

> det_fate carries no detritus routing for any living group. For a multi-DET model the per-pool split cannot be inferred -- supply DetritusFate data for model with detritus groups [53, 54].

`loader_audit.json` retains exact exceptions/tracebacks; `diagnostics_results.json` retains the three NOT_RUN records. Loader tables document sentinel conversion, synthetic import group 55 and forced detritus self-routing identity. The source JSON remains unchanged. No full calculator exists after this exception, so convergence, residuals, negative coefficients/contributions and configuration health are unavailable rather than zero or passing. No global diagnostic, broad 22-method inventory or Monte Carlo was run. No detritus pooling/routing repair was attempted.

## Eligibility and registration

Extraction is complete for what is published; the candidate is **not production eligible**. The first missing numerical requirement is the authors' detritus routing; native/full-precision parameters and life-stage configuration would also resolve remaining source conflicts. The model covers the Celtic Sea shelf part of LME_024 only, with no supported coverage percentage. Taxonomy was captured for future matching, not matched to regional catches. `central_registration_proposal.json` contains one paper update and one candidate model row for the parent's controlled central registration. Selected model and regional results remain untouched.
'''
(R/'REPORT.md').write_text(report,encoding='utf8')
(ED/'REPORT.md').write_text(report,encoding='utf8')
periods=['1985-1989','1990-1994','1995-1999','2000-2004','2005-2009','2010-2016']
inventory=[{'model_id':MID,'period':'1985','status':'extracted_admission_blocked','source':'B2/B3/B4','model_path':str((MD/'model.json').relative_to(ROOT)).replace('\\','/')}]
inventory += [{'model_id':f'Hernvann_2020_Celtic_Sea_Ecosim_mean_{p.replace("-","_")}', 'period':p,'status':'reported_not_extractable','source':'article p.6; supplement maps','missing':'No complete mean-period B/PB/QB/EE/diet/fishery input table','period_caveat':'Article p.6 instead prints 2005-2010 and 2011-2016 for last two periods' if p in periods[-2:] else None} for p in periods]
save(R/'model_inventory.json',inventory)
proposal={'instruction':'Upsert existing paper record and candidate model only; preserve all other fields. Do not select a model or replace regional results.','paper_key':{'article_id':'LME024-Hernvann-2020__LME_024','unit_id':'LME_024'},'paper_updates':{'functional_groups':54,'model_years':'1985 baseline; 1985-2016 Ecosim; six mean-period snapshots reported without complete inputs','extraction_readiness':'1985 source-faithful extraction completed; SPPR blocked by missing multi-detritus routing','full_model_loadable':'No: source diet rounding fails strict admission; loader normalization exposes absent detritus-fate matrix for pools 53/54','model_file_status':'Source database JSON and eight EwE import tables extracted locally','loadability_evidence':'B1 pp9-13 taxonomy; B2 pp14-15 diet; B3 p16 fishery; B4 p17 parameters. See regions/LME_024/models/extraction_review_20260928/REPORT.md','coverage_note':'Celtic Sea shelf <200m, ICES 7.e/7.f/7.g/7.h/7.j.2; subregional to LME_024; no numeric area/coverage fraction.','target_coverage_ratio':None},'model_row':{'unit_id':'LME_024','model_id':MID,'model_path':str((MD/'model.json').relative_to(ROOT)).replace('\\','/'),'source_filename':'Data_Sheet_1_TheCelticSeaThroughTimeandSpa-165f24b6.docx','selected':False,'selection_rationale':None,'paper_ids':'LME024-Hernvann-2020__LME_024','model_year':1985,'variant':'Published baseline B2-B4; 54 groups; source-faithful extraction','model_area_km2':None,'availability':'extracted; all three direct SPPR diagnostics NOT_RUN (detritus routing admission blocker)','publication_year':2020,'model_years':'1985','target_coverage_ratio':None,'coverage_class':'subregional','doi':'10.3389/fmars.2020.578717','coverage_note':'Shelf <200m within ICES 7.e, 7.f, 7.g, 7.h and 7.j.2; no supported coverage percentage.'}}
save(R/'central_registration_proposal.json',proposal)
index='# LME_024 extraction review, 2026-09-28\n\n| Model | Period | Status |\n|---|---|---|\n'+'\n'.join(f'| {m["model_id"]} | {m["period"]} | {m["status"]} |' for m in inventory)+'\n\nSee REPORT.md and central_registration_proposal.json. No model selection or regional PPR publication.\n'
(R/'MASTER_INDEX.md').write_text(index,encoding='utf8')
per=R/MID;per.mkdir(exist_ok=True)
for f in ['REPORT.md','diagnostics_results.json','loader_audit.json','independent_source_balance.json','verification_summary.json','computable_unknowns.json']:shutil.copy2(R/f,per/f)
print('Verified',len(checks),'checks; reports and registration proposal written.')
