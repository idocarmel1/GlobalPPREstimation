from pathlib import Path
import sys,json,math,csv,collections
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import inputs,result_hash
p=HERE.parent.parent/'LME_022.xlsx';b=read_book(p);o=validate_region(b,p)
assert o['calculation_result_sha256']==result_hash(b)
taxa,catch,unidentified,simple=inputs(b)
groups={(r['group'],r['scope'],r['method']):r['sppr'] for r in records(b,'Selected model groups','Group SPPR')}
mapping=collections.defaultdict(list)
for r in records(b,'PPR','Matching'):
    if r['group']:mapping[r['taxon']].append((r['group'],r['weight']))
for t,v in mapping.items():assert math.isclose(sum(w for _,w in v),1,abs_tol=1e-12)
coeff={}
for r in records(b,'PPR','Taxon SPPR'):
    pairs=mapping.get(r['taxon'],[]);vals=[groups[g,r['scope'],r['method']] for g,_ in pairs]
    exp=round(math.fsum(w*v for (_,w),v in zip(pairs,vals)),6) if pairs and all(finite(x) for x in vals) else None
    assert r['sppr']==exp
    coeff[r['taxon'],r['scope'],r['method']]=exp
checked=0
for r in records(b,'PPR','Annual'):
    for i,y in enumerate(YEARS):
        total=[];pairs=[]
        for t in taxa:
            c=catch[t,r['catch_basis']][i];v=coeff[t,r['scope'],r['method']]
            if unidentified[t] and r['unidentified']=='zero':v=0.
            if unidentified[t] and r['unidentified']=='simple':v=simple.get(t)
            total.append(c)
            if finite(c) and finite(v):pairs.append((c,v))
        expected=math.fsum(total) if r['metric']=='catch' and all(finite(c) for c in total) else None
        if numeric_status(r['status']) and pairs and r['metric']!='catch':expected=math.fsum(c*v if r['metric']=='ppr' else c for c,v in pairs)
        assert r[y] is None if expected is None else math.isclose(r[y],expected,rel_tol=2e-14,abs_tol=1e-6),(r,y,expected)
        checked+=1
annual={(r['model_id'],r['scope'],r['method'],r['catch_basis'],r['unidentified']):r for r in records(b,'PPR','Annual') if r['metric']=='ppr'}
npp={r['method']:r for r in records(b,'NPP','NPP')};ratio_checks=0
for r in records(b,'PPR–NPP','Ratios'):
    if not r['model_id']:continue
    num=annual[tuple(r[k] for k in ['model_id','scope','method','catch_basis','unidentified'])]
    for y in YEARS:
        x=num[y];n=npp[r['npp_method']][y];expected=100*x/9/n if finite(x) and finite(n) and n>0 else None
        assert r[y] is None if expected is None else math.isclose(r[y],expected,rel_tol=1e-13,abs_tol=1e-10)
        ratio_checks+=1
summary=json.loads((HERE/'integration_verification.json').read_text(encoding='utf-8'))
summary.update(all_annual_cells_independently_checked=checked,ratio_cells_single_carbon_conversion_checked=ratio_checks,weighted_taxon_coefficients_checked=len(coeff))
(HERE/'integration_verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
coverage=list(csv.DictReader((HERE/'coverage_by_year_basis.csv').open(encoding='utf-8')))
lines=['# North Sea conditional regional GE integration — 28 September 2026','',
f"Selected model: `{summary['model_id']}`. Overview selection and rationale are unchanged.",'',
f"**2019, total catch (landings + discards), all sources, default unidentified treatment:** {summary['ge_ppr_tC']:,.3f} tC/year ({summary['ge_ppr_wet_tonnes']:,.3f} wet-weight-equivalent tonnes/year before division by nine). This is a supported-catch subtotal, not a whole-North-Sea estimate.",'',
f"Mapping covers {summary['mapped_taxa']} of {summary['total_taxa']} catch labels and {summary['coverage_2019']['supported_catch_tonnes']:,.3f} of {summary['coverage_2019']['total_catch_tonnes']:,.3f} total catch tonnes in 2019 ({summary['coverage_2019']['coverage_pct']:.5f}%). Unsupported coefficients remain blank. Full-region production_eligible remains false; method availability is based on reviewed direct diagnostic and numerical records.",'',
'## Source, computational state and admission','',
'The canonical model.json hash is `'+summary['canonical_sha256']+'`. Canonical evidence and published values were not edited. `audit_runtime.py` verifies the retained executed-code hashes, loads an exact canonical copy with the recorded constructor, compares every loaded group field to the historical export, saves all calculator attributes to typed JSON, restores that saved state, and exactly reproduces full GE, TE and With Egestion diagnostic returns. Coefficients for each source scope agree with the retained export, joined by native group ID. The export helper uses a positional join that cannot safely consume a differently ordered direct return, so this integration explicitly reindexes direct coefficients by group ID. No engine change was made.','',
'Constructor: normalize_DC=True, DC_tol=0.001, underdetermined=True, zero_biomass_accum=False; zero_catch=True, default_gs=True, flow/guess weights 1. Diagnostics: det_collapse_mode=never, det_external_sppr=0, det_open_mode=none, det_theta=1. These are the previously retained settings, not a newly introduced repair. Diet rounding is normalized, missing GS defaults to 0.2, unknown BA is completed from residual flows, and detritus EE/rates/defaults are engine transformations. The complete post-ModelData ledger and the earlier source-to-loader ledger remain distinguishable. All real living B/PB/QB/EE are published final values; no new living biomass placeholder was introduced. Computational BA is not measured biomass change. Source mass balance remains indeterminate for Turbot and Ling.','',
'GE: OK, living spectral radius 0.2120896741, overall flow gap 0, zero returned warnings. With Egestion: OK. TE: FAIL, living spectral radius 1.1127784 and negative contributions including an unfished group. Failed TE coefficients are preserved only in diagnostic evidence; regional TE group/taxon/annual numerical results remain unavailable. No global or Monte Carlo run was performed.','',
'## Mapping and geographic limits','',
'The old mapping was reviewed against this exact selected model and the author XLSX Table S2, not accepted from its historical 99.597% coverage claim. That percentage included ecological analogues and unobserved composite weights. Sixty-nine exact source-member labels plus Argentina (source explicitly says Argentina sp.), common cockle and common whelk are retained. All accepted weights are 1 in a uniquely supported group. Representative Main Species lists support inclusion of named taxa but do not prove exhaustive composition. Other historical analogues, genus/family extensions and composite splits remain unresolved in this conservative result; this does not assert that every unlisted taxon is biologically excluded.','',
'Cockle category identity: [WoRMS Cerastoderma edule](https://www.marinespecies.org/introduced/aphia.php?id=138998&p=taxdetails). Whelk category identity: [WoRMS Buccinum undatum](https://marinespecies.org/berms/aphia.php?id=138878&p=taxdetails). Source spelling Bussinum undatum is retained and not silently corrected in the model. Per-label accepted/rejected evidence and original assignments are in mapping_review.csv. Largest unsupported 2019 label is Marine fishes not identified, 318,308.913 tonnes; no composition weights are known.','',
'The model describes East-coast Scotland shelf grounds, including Orkney/Shetland, rather than the whole North Sea. No validated overlap percentage is available. Catch mapping coverage is not geographic coverage. Fixed 1991–1995 coefficients across 1950–2019 catch do not reconstruct annual food webs. The source excludes discards; applying the coefficients to regional discards is an explicit removals-basis extrapolation and does not model discard recycling. No area scaling was applied.','',
'## 2019 coverage by catch basis','', '| Basis | Supported tonnes | Total tonnes | Coverage |','|---|---:|---:|---:|']
for r in coverage:
    if r['year']=='2019':lines.append(f"| {r['basis']} | {float(r['supported_catch_tonnes']):,.3f} | {float(r['total_catch_tonnes']):,.3f} | {float(r['coverage_pct']):.3f}% |")
lines+=['','## Verification and reproduction','',f'Independent checks cover {len(coeff):,} weighted taxon coefficients, {checked:,} annual cells across all methods/scopes/bases/unidentified treatments, and {ratio_checks:,} PPR/NPP cells with division by nine exactly once. Total-catch PPR equals landings plus discards. Regional freshness validation passes. Catch, Classic PPR including historical sensitivity rows, NPP, selection and canonical JSON are preserved. The before workbook is retained.','',
'Run `python regions/LME_022/models/regional_ge_integration_20260928/audit_runtime.py` to reproduce direct science and `python regions/LME_022/models/regional_ge_integration_20260928/verify_and_report.py` to verify the current regional workbook. `integrate.py` deliberately refuses to overwrite a newer workbook. Central/map verification is recorded in the project-wide integration report.','',
'Files: runtime_verification.json; computational_state.json; direct_new_GE.json/.txt; direct_new_TE_EEfix.json/.txt; direct_new_WithEgestion.json/.txt; loader_transformations.json; mapping_review.csv; coverage_by_year_basis.csv; integration_verification.json.']
if summary.get('display_state'):
    lines.insert(2,'**Superseding user instruction:** show traceable numeric SPPR as provisional PPR and flag diagnosis problems for later validation. All three direct methods now have explicit provisional Annual status; TE FAIL numbers are displayed as failed research previews, never relabeled valid. The earlier admission discussion below describes the initial integration before this instruction. `adopt_provisional.py` implements that later authorized display policy.')
    lines=[line.replace('Failed TE coefficients are preserved only in diagnostic evidence; regional TE group/taxon/annual numerical results remain unavailable.','TE numeric coefficients and annual subtotals are retained as explicitly flagged provisional FAIL results under the superseding user instruction.') for line in lines]
(HERE/'INTEGRATION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['ge_ppr_tC','weighted_taxon_coefficients_checked','all_annual_cells_independently_checked','ratio_cells_single_carbon_conversion_checked']}))
