from pathlib import Path
from decimal import Decimal
import json,csv,hashlib,shutil,zipfile
import numpy as np
from openpyxl import load_workbook
R=Path(__file__).resolve().parent;ROOT=R.parents[3]
REG=ROOT/'regions/LME_037';MID='Bacalso2026_Visayan_Sea_1997_baseline';M=REG/'models'/MID;E=M/'extracted_tables';D=M/'diagnostics/zero_import_default'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
inp=load(R/'extraction_input.json');source=load(M/'model.json');checks=[]
def check(name,okay):
    checks.append({'check':name,'passed':bool(okay)});assert okay,name
check('33 source groups',len(source['group'])==33)
for raw,g in zip(source['group'],inp['groups']):
    for f,k in [('biomass','biomass'),('pb','pb'),('qb','qb'),('ee','ee'),('pq','ge'),('tl','tl')]:check(f'group {g["n"]} {f}',raw[k]==(g.get(f) or '-9999'))
    for k in ['gs','biomass_accum','biomass_accum_rate','diet_imp']:check(f'group {g["n"]} unknown {k}',raw[k]=='-9999')
    entries={x['prey_seq']:x for x in raw['diet_descr']['diet']}
    for prey,val in inp['diet'].get(str(g['n']),{}).items():check(f'diet {g["n"]} {prey} source exact',entries[prey]['proportion']==val)
    check(f'routing unknown {g["n"]}',all(x['detritus_fate']=='-9999' for x in entries.values()))
    expected=inp['landings'][str(g['n'])]['Published total catch']
    check(f'catch {g["n"]}',Decimal(raw['export'])==Decimal(expected))
for name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx','Taxonomy.xlsx']:check('required file '+name,(E/name).exists())
for row in load(R/'WORD_RENDER_CELL_CROSSCHECK.json'):check(f'DOCX rendered page {row["page"]}',not row['mismatches'])
check('191 baseline numeric cells independently agree',sum(x['agrees_at_printed_precision'] is True for x in load(R/'BASELINE_PARAMETER_CROSSWALK.json'))==191)
S=REG/'papers/LME037-Bacalso-2026/recovered_sources_20260928'
for a in load(S/'DOWNLOAD_MANIFEST.json'):check('source hash '+a['file'],hashlib.sha256((S/a['file']).read_bytes()).hexdigest()==a['sha256'])
original_metadata=load(S.parent/'metadata.json')
for a in original_metadata['material_files']:check('original unchanged '+a['local_filename'],hashlib.sha256((S.parent/a['local_filename']).read_bytes()).hexdigest()==a['sha256'])
wb=load_workbook(next(E.glob('*_reconstructed.xlsx')),read_only=True,data_only=True)
basic=list(wb['Basic input'].values)
for row,g in zip(basic[1:],inp['groups']):
    for col,key in [(3,'biomass'),(4,'pb'),(5,'qb'),(6,'ee')]:check(f'roundtrip group {g["n"]} {key}',row[col] is None if g.get(key) is None else abs(float(row[col])-float(g[key]))<1e-10)
wb.close()

DC=np.zeros((33,33))
for predator,preys in inp['diet'].items():
    for prey,val in preys.items():DC[int(predator)-1,int(prey)-1]=float(val)
B=np.array([float(g['biomass']) for g in inp['groups']]);PB=np.array([float(g.get('pb') or 0) for g in inp['groups']]);QB=np.array([float(g.get('qb') or 0) for g in inp['groups']]);Y=np.array([float(g['export']) for g in source['group']]);pred=(B*QB)@DC
balance=[]
for i,g in enumerate(inp['groups']):
    ee=(Y[i]+pred[i])/(B[i]*PB[i]) if PB[i] else None
    balance.append({'seq':i+1,'name':g['name'],'predation':float(pred[i]),'published_total_catch':float(Y[i]),'EE_printed':float(g['ee']),'conditional_EE_BA0_migration0':ee,'delta_EE':ee-float(g['ee']) if ee is not None else None})
save(R/'SOURCE_BALANCE_CONDITIONAL.json',balance)

report='''# Visayan Sea baseline 1997 — extraction report

The 33-group baseline is extracted as `Bacalso2026_Visayan_Sea_1997_baseline`. Bacalso et al. (2026) Table 1 provides the final 1997 parameters; the explicitly cited 2023 predecessor supplies the recovered diet and catch tables. All 191 populated baseline parameter cells agree between those papers at printed precision, after the documented reef-habitat conversion. The 2018 Ecosim endpoint is **not reconstructed**: its realized diets, accumulation/flow export and precise small-group biomass are unavailable.

## Sources and table layout

- 2026 main PDF, Table 1, page 5: 33 groups, paired 1997/2018 columns for TL, B, PB, QB, EE and PQ. Only 1997 columns feed this baseline. Column positions and every numeric bounding box are retained in `BASELINE_PARAMETER_CROSSWALK.json`. Source commas in three group names are replaced by ` -` for unquoted CSV compatibility; group numbering and identity are unchanged.
- 2023 official Frontiers Word supplement, Table S2, pages 7–8: 33 prey rows and 30 predator columns, continued by columns 1–16 then 17–30. All 990 numeric/zero entries are retained; `--` represents no diet link. Five sums differ from one: 1.001, 0.9996, 1.001, 1.001 and 1.002 for predators 1, 2, 5, 13 and 16. No source normalization.
- 2023 Table S3, pages 9–11: 34 fishing fleets with published per-group totals. The imports use one explicitly named `Published total catch` column holding those totals (15.160 t/km²/year overall). All 1,122 original fleet cells are retained separately, including censored `0.000*` values below 0.001; no fabricated zeros or reconstructed fleet shares. Catch is stored in Landings according to the extraction format's convention for unsplit published catches; no claim is made that discards are independently known.
- 2023 main Table 1: representative group taxa and catch size ranges, with XML rowspan expansion verified by group number. These are representative taxa, not exhaustive memberships. The 2026 supplementary Table S3 adds ECOIND trait/catch records and remains available for later detailed taxon mapping; no catch mapping was performed here.

Word was rendered read-only using a separate hidden Microsoft Word instance. Independent rendered-PDF table extraction agrees with every one of the 990 diet and 1,155 catch/total cells checked. The source PDF page and diet/catch render images are retained. Source bytes and publisher attachment checksum pass verification.

## Spatial and temporal identity

The Visayan Sea model includes municipal waters outside the immediate Visayan Sea domain: 2023 section 2.1 reports 12,521.8 km² for the sea and 16,728.5 km² including those waters, which the model covers. Figure 1 delineates the study area. This is a local candidate associated with LME037, not a whole-LME model, and no unverified coverage percentage is assigned. 2023 names the survey baseline 1996–1997; 2026 output labels it 1997, despite an inconsistent 1997–1998 phrase in its methods.

2023 Table 3 reports habitat-area densities. Its prose specifies 0.2 habitat fraction for reef groups; values for groups 16–20 convert exactly to the 2026 full-area B values at published precision (1.653 × 0.2 = 0.3306, printed 0.331, for group 16). The canonical model uses the 2026 full-area densities, with habitat multiplier 1 to encode that density basis. This does not assert full-area ecological occupancy. Serialization number 3702026 is project-local, not an EcoBase accession.

## Biomass accumulation and deliberate blanks

The complete 2026 main/supplement and 2023 main/supplement were searched. The equations define BA and migration but provide no per-group numeric baseline values. Canonical BA, BA rate, migration, unassimilated consumption, diet import and detritus routing remain unknown. Detritus and primary-producer QB cells remain missing where the table is blank. No unknown B or EE is completed: all baseline B/EE values are published final-model values. Many are model estimates rather than field measurements; 2023 Table 3 identifies estimated parameters in bold.

All four final parameters are retained for consumers. Rounded PQ values are retained too; e.g. Seabirds PQ 0.01, whereas PB/QB = 0.4/64 = 0.00625. The calculator uses its documented parameter handling, not an invented physiological correction.

## Converter audit and verification

The standard converter silently normalizes some diet columns, omits displayed PQ/TL precision, and inserts default diet import zero. Its original output is archived as `converter_raw.json` in the review folder. The canonical database JSON restores exact published diet values, PQ/TL and unknown sentinels. `converter_source_restoration.json` records every restoration. The eight imports are source-faithful throughout. The canonical named JSON and `model.json` agree; the reconstructed workbook was regenerated from that canonical JSON. The converter's earlier MASS_BALANCE report concerns its internally normalized conversion and is not evidence of strict canonical admission.

The import validator reports 0 errors and 35 warnings: unknown detritus-fate rows, unknown BA, and unknown diet imports. Source-table mass-balance check reports 0 errors, 1 Seabirds PQ warning, and notes on model-estimated parameters. `SOURCE_BALANCE_CONDITIONAL.json` independently retains balances under explicitly conditional BA=0 and migration=0; it does not replace missing values. `VERIFICATION.json` verifies source hashes, every core parameter, all diets, unknowns, catches and reconstructed workbook core parameters.

## Calculator admission and computational assumptions

Strict loading and normal default loading reject the rounded diet columns. A separately documented tolerance 0.0021 admits the original matrix without normalization. With unknown diet-import sentinels the constructor loads but all three diagnostics raise `[33] not found in axis`; this is a missing-import/identity handling issue, not evidence of a missing detritus group. An isolated diagnostic input sets unknown diet imports to the documented software default zero. The remaining loading configuration is `zero_catch=True, zero_biomass_accum=True, default_gs=True, DC_tol=0.0021, normalize_DC=False`. The existing single-detritus routing fallback is used; it is a computational assumption, not recovered author routing. The canonical source JSON remains unchanged.

The exact diagnostic input, full returns, and before/after loaded tables are under `diagnostics/zero_import_default/`. They return GE **WARN**, TE **WARN**, and With Egestion **WARN**. Maximum production residual is 0.9387101%; maximum consumption residual is 0.4362013%. PP budget status is OK for all three, but strict input/budget balance booleans remain false. TE additionally identifies Seabirds as near-singular (EE=0.02). No source biological parameters were repaired, no detritus groups were merged, no global/Monte Carlo methods were run, and no model was selected. See the separate direct-return report for the full method outputs.

These are candidate diagnostics, not authorization to publish regional production results. Central registration remains a proposal for the parent agent.
'''
(E/'REPORT.md').write_text(report,encoding='utf8')
direct=['# Direct SPPR diagnostics — Visayan Sea 1997','', 'Only full returns from `PPRCalculator.diagnose_sppr(TE_option=..., short=False, flat=False)` are shown below. The exact computational input and defaults are saved beside these returns; source/admission evidence is in the separate extraction report. No global option.','']
summary=[]
for method in ['GE','TE','With Egestion']:
    raw=load(D/(method.replace(' ','_')+'_raw.json'))
    direct += ['## '+method,'','```json',json.dumps(raw,indent=2),'```','']
    summary.append({'method':method,'status':raw['status'],'input_status':raw['model_input']['status'],'balance_status':raw['balance']['status'],'strict_input_balanced':raw['model_input']['is_model_balanced'],'strict_budget_balanced':raw['balance']['is_balanced'],'PP_relative_gap':raw['balance']['rel_gap']})
(M/'diagnostics/DIRECT_SPPR_REPORT.md').write_text('\n'.join(direct),encoding='utf8')
save(R/'results_record.json',{'unit_id':'LME_037','model_id':MID,'year':1997,'source_groups':33,'methods':summary,'selected':False,'production_eligible':False,'2018_status':'NOT_RUN: missing realized diet/flow and BA export; censored group15 biomass','diagnostic_input_sha256':hashlib.sha256(next(D.glob('37_*.json')).read_bytes()).hexdigest(),'source_model_sha256':hashlib.sha256((M/'model.json').read_bytes()).hexdigest()})
save(R/'central_registration_proposal.json',{'unit_id':'LME_037','paper_id':'LME037-Bacalso-2026','selected':False,'extracted_models':[{'model_id':MID,'year':1997,'groups':33,'model_path':str((M/'model.json').relative_to(ROOT)),'model_area_km2':16728.5,'coverage_class':'subregional','coverage_ratio':None,'diagnostic_status':'GE WARN; TE WARN; With Egestion WARN; exact source rounded diets retained, diagnostic tolerance0.0021 and defaults documented'}],'source_link_additions':['https://frontiersin.figshare.com/articles/dataset/21959183','https://ndownloader.figshare.com/files/38954888','https://doi.org/10.3389/fmars.2023.1099400'],'2018_candidate_status':'blocked: no realized endpoint diet/flow export; do not substitute baseline diets'})
(R/'MASTER_INDEX.md').write_text('# LME037 Bacalso source recovery and baseline extraction\n\n- [Diet source search](DIET_SOURCE_SEARCH_REPORT.md) — official Word supplement recovered and verified.\n- [1997 extraction report](../Bacalso2026_Visayan_Sea_1997_baseline/extracted_tables/REPORT.md).\n- [Direct GE / TE / With Egestion report](../Bacalso2026_Visayan_Sea_1997_baseline/diagnostics/DIRECT_SPPR_REPORT.md): WARN for all three under documented computational defaults; strict source admission blocked by rounding.\n- 2018 endpoint: not extracted; missing realized diets/flows and accumulation.\n- No selected model or published regional PPR; registration proposal awaits parent consolidation.\n',encoding='utf8')
save(R/'VERIFICATION.json',{'status':'PASS','checks_count':len(checks),'checks':checks})
print('PASS',len(checks),'checks')
