from pathlib import Path
import sys,json,csv,math,hashlib,shutil,collections
import numpy as np
ROOT=Path(__file__).resolve().parents[3];REG=ROOT/'regions/LME_003';MODEL=REG/'models/CAL-2016_California_Current_2000-2014';OUT=MODEL/'selected_pipeline'
sys.path.insert(0,str(ROOT/'tools'));from workbooks import *
book=read_book(REG/'LME_003.xlsx');o=validate_region(book,REG/'LME_003.xlsx')
oldpath=next(p for p in sorted((REG/'models/previous_results').glob('LME_003_before_CAL2016_selection_*.xlsx')) if not overview(read_book(p)).get('selected_model_id'))
old=read_book(oldpath)
assert book['Catch']==old['Catch'];assert book['NPP']==old['NPP'];assert book['Classic PPR']['Taxa']==old['Classic PPR']['Taxa']
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
admit=load(OUT/'coefficient_verification.json');assert sha(MODEL/'model.json')==admit['canonical_sha256'];assert sha(REG/o['model_path'])==admit['runtime_sha256']
assert o['selected_model_id']==MODEL.name
groups={r['group']:r for r in records(book,'Selected model groups','Groups') if 'group' in r}
group_coeff={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(book,'Selected model groups','Group SPPR')}
assert len(group_coeff)==846 and all(finite(v) and v>=0 for v in group_coeff.values())
mapping=collections.defaultdict(list)
for r in records(book,'PPR','Matching'):
 if r['group']:mapping[r['taxon']].append((r['group'],r['weight']))
catch={(r['taxon'],r['catch_basis']):r for r in records(book,'Catch','Catch')};taxa=sorted({t for t,b in catch})
unidentified={r['taxon']:r['unidentified'] for r in records(book,'Catch','Catch')};simple={r['taxon']:r['sppr'] for r in records(book,'Classic PPR','Taxa')}
assert {r['taxon'] for r in records(book,'PPR','Matching')}==set(taxa)
assert all(math.isclose(sum(w for g,w in a),1,abs_tol=1e-9,rel_tol=0) for a in mapping.values())
coeff={};ncoeff=0
for r in records(book,'PPR','Taxon SPPR'):
 a=mapping.get(r['taxon'],[]);v=round(math.fsum(w*group_coeff[g,r['scope'],r['method']] for g,w in a),6) if a else None
 assert r['sppr']==v,(r['taxon'],r['sppr'],v)
 coeff[r['taxon'],r['scope'],r['method']]=v;ncoeff+=1
annual={};checked=0
for r in records(book,'PPR','Annual'):
 key=(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric']);annual[key]=r
 for y in YEARS:
  allcatch=[];pairs=[]
  for t in taxa:
   c=catch.get((t,r['catch_basis']),{}).get(y);v=coeff[t,r['scope'],r['method']]
   if unidentified[t] and r['unidentified']=='zero':v=0.
   if unidentified[t] and r['unidentified']=='simple':v=simple.get(t)
   allcatch.append(c)
   if finite(c) and finite(v):pairs.append((c,v))
  expected=None
  if r['metric']=='catch':expected=math.fsum(allcatch) if all(finite(c) for c in allcatch) else None
  elif r['status']=='ok' and pairs:expected=math.fsum(c*v if r['metric']=='ppr' else c for c,v in pairs)
  actual=r[y]
  assert actual is None if expected is None else math.isclose(actual,expected,rel_tol=2e-14,abs_tol=1e-6),(key,y,actual,expected)
  checked+=1
npp={r['method']:r for r in records(book,'NPP','NPP')};ratio_checks=0
classic={(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric']):r for r in records(book,'Classic PPR','Annual')}
for r in records(book,'PPR–NPP','Ratios'):
 lookup=annual if r['model_id'] else classic
 ar=lookup[r['scope'],r['method'],r['catch_basis'],r['unidentified'],'ppr']
 for y in YEARS:
  p=ar[y];n=npp[r['npp_method']][y];expected=100*p/9/n if finite(p) and finite(n) and n>0 else None
  assert r[y] is None if expected is None else math.isclose(r[y],expected,rel_tol=2e-14,abs_tol=1e-12)
  ratio_checks+=1
cov=load(OUT/'mapping_coverage.json');by_year=[]
for y in YEARS:
 total=math.fsum(catch[t,'catch'][y] for t in taxa);covered=math.fsum(catch[t,'catch'][y] for t in taxa if t in mapping)
 by_year.append({'year':y,'total_catch_tonnes':total,'mapped_catch_tonnes':covered,'coverage':covered/total if total else None})
with (OUT/'annual_mapping_coverage.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(by_year[0]));w.writeheader();w.writerows(by_year)
results=[]
for r in records(book,'PPR','Annual'):
 if r['scope']=='all' and r['unidentified']=='method' and r['metric']=='ppr':results.append({'method':r['method'],'basis':r['catch_basis'],'2019_ppr_wet_tonnes':r[2019],'status':r['status']})
summary={'selected_model_id':o['selected_model_id'],'selected_runtime_path':o['model_path'],'selected_runtime_sha256':sha(REG/o['model_path']),'canonical_source_sha256':sha(MODEL/'model.json'),'original_regional_workbook':oldpath.relative_to(REG).as_posix(),'current_workbook_sha256':sha(REG/'LME_003.xlsx'),'coefficient_records_checked':ncoeff,'annual_cells_checked':checked,'ratio_cells_checked':ratio_checks,'all_group_coefficients_nonnegative_finite':True,'catch_classic_taxa_NPP_unchanged':True,'canonical_source_unchanged':True,'direct_diagnostic_reproduction':admit['configurations'],'mapping_coverage':cov,'NPP_years_by_method':{k:[y for y in YEARS if finite(v[y])] for k,v in npp.items()},'2019_results':results,'interpretation':'Partial mapped-catch PPR from fixed 2000–2014 model; no full-region coverage claim, no MC, no new NPP extraction','checks_passed':True}
(OUT/'REGIONAL_VERIFICATION.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
unresolved=load(OUT/'unresolved_taxa.json')
text=f'''# Selected California Current model: regional calculation

User selection of `{MODEL.name}` is recorded in LME_003.xlsx / Overview. The original source canonical JSON is unchanged. Overview points to an explicitly labeled runtime JSON containing the independently checked author-equation solution for the 26 unknown biomasses and 67 EEs. The original regional workbook is archived at `{oldpath.relative_to(REG).as_posix()}`.

## Results and scientific scope

Only full direct GE, TE and With Egestion calculations were run, with source-resolved coefficients from the same calls. All three complete reports reproduce the previously audited results at 1e-12 tolerance. All 846 group/scope/method coefficients and all raw source contributions are finite and nonnegative, including unfished groups. Each configuration remains **WARN**, retaining zero-EE and near-zero-transfer-efficiency warnings. Standard method health permits these convergent, balanced configurations; WARN is not represented as an error-free source model.

Source and loader caveats remain: GS was unreported and is supplied as 0.2 for consumers; runtime routes egestion to the sole detritus pool in addition to author unused production, sets detritus EE to 1 and appends diet import. Total source catch includes bycatch/discards without a split. The runtime does not invent a discard return or reassign observed source values. Source diet values are not normalized. Model source area is 302,000 km²; the fraction of LME_003 represented geographically has not been established.

The regional workbook now includes matching, taxon coefficients, annual PPR (1950–2019), all/inner/PP source scopes, three catch bases, three unidentified treatments, and PPR/NPP where that year's retained NPP exists. Unsupported NPP years stay blank. The 2000–2014 model is held fixed across the catch history; these are historical catch-footprint calculations, not annual reconstructions of food-web change. No Monte Carlo, broad-method export or new NPP extraction was run.

## Catch mapping and coverage

Mapped **{cov['taxa_mapped']} of {cov['taxa_total']} taxa**; **{cov['taxa_unresolved']} remain explicit unresolved rows**. Mapped-catch coverage is **{cov['historical_tonnage_coverage']:.2%}** for 1950–2019 and **{cov['2019_tonnage_coverage']:.2%}** for 2019. The 95% review target is not met. Annual PPR totals are **partial mapped-catch totals**, not whole-region estimates. Use the covered_catch series and `annual_mapping_coverage.csv` alongside PPR; missing model coefficients were never replaced by zero except the explicitly requested unidentified=zero view.

Appendix B group definitions provide direct membership and higher-taxon containment. Life-stage weighting uses author model catch; zero juvenile catch concentrates weights on adults, a source selectivity convention with uncertain applicability to regional juvenile discards. Coarse taxa receive constrained candidates and constant weights from identified regional catches, filtered by higher-taxon containment where pools mix taxa. Candidate groups, exact weights and confidence are retained in catch_mapping.csv and the workbook. Broad medium-demersal unidentified/ray-finned-fish records use pooled demersal groups, excluding named commercial single stocks and pelagic groups. This is a low-confidence catch-composition projection, not observed unidentified-catch composition. It cannot resolve missing geographic information.

Key deliberate exclusions: Albacore represents T. alalunga, not yellowfin or skipjack; Pacific Mackerel is Scomber japonicus, not Trachurus; Hake is Merluccius, not pollock/cod; Salmon explicitly contains Chinook/coho, not all salmonids. Source cephalopod prose excludes large predatory jumbo squid despite a broader initial class description. Pandalid/caridean definitions do not establish penaeid membership. Unsupported ray groups are not merged into Skates. Names and reasons for every unresolved taxon remain in unresolved_taxa.json.

Scientific-name checks: NOAA Pacific Mackerel profile confirms Scomber japonicus; NOAA InPort item24030 confirms Pacific Squalus suckleyi was formerly reported as S. acanthias. WoRMS Aphia836033 confirms Magallana gigas as an oyster. Source spelling remains unchanged in archived taxonomy; these checks only support matching.

## Independent verification

Fresh regional validation passes. Independently recomputed {ncoeff:,} taxon coefficients, {checked:,} annual cells and {ratio_checks:,} PPR/NPP cells agree within stated floating-point tolerances. Mapping weights sum to one; every catch taxon has a decision; no basal or synthetic-import group takes catch. Original Catch, Classic PPR taxon inputs and all NPP data/provenance are unchanged. Canonical source SHA-256 is unchanged. Runtime coefficients reproduce the audited direct results. Executed scientific and workbook code snapshots and hashes are retained in selected_pipeline/code and coefficient_verification.json.

No Project.xlsx or map files were written by this worker. Central registration is prepared separately for the parent coordinator.

## Largest unresolved historical catches

| Taxon | 1950–2019 catch (tonnes) | Reason |
|---|---:|---|
'''
for r in unresolved[:15]:text+=f"| {r['taxon']} | {r['total']:,.0f} | {r['reason']} |\n"
(OUT/'SELECTED_REGIONAL_REPORT.md').write_text(text,encoding='utf-8')
proposal=load(REG/'extraction_review_20260928/central_metadata_proposal.json')
proposal.update({'selected':True,'production_eligible':True,'production_eligibility_scope':'Numerically admitted three configurations under documented runtime assumptions; mapped-catch partial annual PPR only; below95% catch coverage','selected_runtime_path':o['model_path'],'source_model_path':f'models/{MODEL.name}/model.json','selection_rationale':o['selection_rationale'],'mapping_coverage':cov,'regional_workbook_sha256':sha(REG/'LME_003.xlsx'),'regional_report':(OUT/'SELECTED_REGIONAL_REPORT.md').relative_to(ROOT).as_posix(),'regional_verification':(OUT/'REGIONAL_VERIFICATION.json').relative_to(ROOT).as_posix(),'notes':'User-selected; audited solved B/EE runtime, GS0.2 and detritus extension retained. GE/TE/With Egestion WARN and no negative/nonfinite contributions. All historical annual PPR values are mapped-catch partial estimates. Source canonical unchanged. No full-geographic-coverage or complete-taxon-coverage claim.'})
(OUT/'central_registration_proposal.json').write_text(json.dumps(proposal,indent=2,ensure_ascii=False),encoding='utf-8')
for f in [Path(__file__),REG/'extraction_review_20260928/build_selected_mapping.py']:shutil.copy2(f,OUT/'code'/f.name)
manifest=[{'path':p.relative_to(REG).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='selected_output_manifest.json']
(OUT/'selected_output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'coefficients':ncoeff,'annual_cells':checked,'ratio_cells':ratio_checks,'coverage':cov,'2019':results},indent=2))
