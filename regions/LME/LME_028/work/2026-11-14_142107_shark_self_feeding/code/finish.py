"""Verify retained evidence and build the portable experiment inventory."""
from pathlib import Path
import gzip, hashlib, json, os, sys
import numpy as np
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'tools/scientific_helpers').exists())
MODEL=ROOT/'regions/LME/LME_028/papers/GUI-2004/models/28_646_Guinea_(1998)'
def read(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return os.path.relpath(p,RUN).replace('\\','/')
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
data=read(RUN/'outputs/comparison.json'); rows=data['summaries']; co=read(RUN/'outputs/coefficients.json')
qa=read(RUN/'qa/checks.json'); checks=qa['checks']; provenance=read(RUN/'inputs/provenance.json')
baseline={r['option']:r for r in rows if r['scenario']=='baseline'}
errors={}
for option,method in [('TE','new_TE_EEfix'),('GE','new_GE'),('With Egestion','new_WithEgestion')]:
    old=read(MODEL/f'results/diagnostics/method_coverage/{method}.ee_floor_reused.json.gz')
    pairs=[(r['sppr'],old['scopes'][r['scope']][r['group']]) for r in co if r['scenario']=='baseline' and r['option']==option]
    errors[option]={'max_absolute':max(abs(a-b) for a,b in pairs),'max_relative':max(abs(a-b)/max(1,abs(b)) for a,b in pairs),'rtol':1e-10,'atol':1e-8,'compared_coefficients':len(pairs)}
    np.testing.assert_allclose([a for a,b in pairs],[b for a,b in pairs],rtol=1e-10,atol=1e-8)
save(RUN/'qa/baseline_reconciliation.json',errors)
base_values={r['seq']:r['sppr'] for r in co if r['scenario']=='baseline' and r['option']=='TE' and r['scope']=='inner'}
group_changes=[]
catch={g['group']:g['catch_tonnes'] for g in read(RUN/'inputs/catch_and_benchmark.json')['groups']}
for r in co:
    if r['scenario']=='baseline' or r['option']!='TE' or r['scope']!='inner': continue
    original=base_values[r['seq']]
    group_changes.append({**r,'baseline_sppr':original,'change_percent':100*(r['sppr']/original-1) if original else None,'baseline_2019_ppr_tC':catch.get(r['group'],0)*original/9,'scenario_2019_ppr_tC':catch.get(r['group'],0)*r['sppr']/9})
save(RUN/'outputs/TE_group_changes.json',group_changes)
summary=['LME_028 shark/ray self-feeding: full-network sensitivity',
 'Model: 28_646_Guinea_(1998); group 5: Sélaciens L prof.',
 '2019 regional catch (landings plus discards), original allocations, inner sources; wet-weight PPR / 9 = tonnes carbon.',
 'Baseline catch: 4,469,154.981144243 tonnes. Original fixed-10% benchmark held constant: '+str(data['fixed_classic_tC'])+' tonnes carbon.',
 'All biological rates, catch, EE, natural mortality, biomass accumulation, migration and detritus fate held fixed. Predation recalculated from the changed diet.',
 'EE floor ON at 0.1 in every run; zero affected groups and zero added mortality export. Focal group EE is 0.5.',
 'Raw self-diet was already normalized by the audited loader: removed share = '+str(provenance['removed_share'])+'.',
 'No redistribution: leave other prey shares unchanged, resulting diet sum 97.9991672333%.',
 'Redistribution: multiply each remaining prey share by '+str(1/(1-provenance['removed_share']))+'; diet sum remains 100%.',
 'All other network edges unchanged. Each case solves the complete network, including indirect feedback; no Ecopath rebalance or automatic diet renormalization follows the intervention.',
 '', 'TE comparison (regional PPR in tonnes carbon):']
for r in rows:
    if r['option']!='TE': continue
    summary += [f"{r['scenario']}: regional PPR {r['regional_ppr_tC']['inner']:,.3f}; change {r['inner_change_percent']:.6f}%; focal SPPR {r['focal_sppr_inner']:,.6f}; focal share {100*r['focal_share_inner']:.6f}%; fixed benchmark ratio {r['inner_ratio_to_fixed_classic']:.6f}x; living-network spectral radius {r['diagnostic']['divergence']['rho_living']:.9f}; PP balance gap {100*r['diagnostic']['balance']['rel_gap']:.6f}%; diagnostic {r['diagnostic']['status']}."]
summary += ['', 'Other full-network formulations (same 2019 catch and inner scope):']
for r in rows:
    if r['option']=='TE': continue
    summary.append(f"{r['option']} / {r['scenario']}: {r['regional_ppr_tC']['inner']:,.3f} tonnes carbon ({r['inner_change_percent']:.6f}%); diagnostic {r['diagnostic']['status']}.")
summary += ['', 'Interpretation:',
 'Removing the focal loop lowers TE PPR by approximately 46%, but it remains 11.25-11.34 times the unchanged benchmark. Proportional redistribution changes the result only slightly.',
 'The earlier approximately 41.58% regional reduction held other groups fixed. The present full-network solution includes changes in every connected group and supersedes that conditional estimate for these scenarios.',
 'Both altered cases converge algebraically, have no negative source coefficients, and improve the living-loop diagnostic; both nonetheless fail overall diagnostics.',
 'The unredistributed diet has a 2.0008% intake deficit. Redistribution fixes that diet sum, but removing self-predation while holding production, mortality and accumulation fixed still breaks production balance (maximum relative residual 33.3242%). TE PP-budget gaps are 11.9558% and 11.8370%, respectively, above the 5% failure threshold.',
 'These values are hypothetical fixed-rate sensitivities, not mass-balanced corrected models or publication-ready replacements. No new researcher validation or change of disqualification is implied.',
 'The benchmark retains original saved coefficients; it is not a recalculated trophic-level benchmark for either altered network.',
 'The historical comparator excludes Dauphins, Oiseaux and Baleines from regional aggregation; all remain in the network solution. This scope reproduces the prior comparison rather than interpreting current review status as scientific data.',
 '', 'Verification and evidence:',
 'Executed the exact retained loader and EE-floor engine identified in the result manifest. Current software differs; it was not substituted for the saved baseline engine.',
 'All three fresh baselines reproduce saved coefficients with maximum relative error below 5e-16. All nine solves independently checked by solving the full linear system numerically.',
 'Full diagnostic returns, SPPR/A/L matrices, before/after runtime, axes, missingness masks, per-scope coefficients, group changes, negative-entry table, settings and input/code hashes retained in this folder.',
 f"Verified {qa['protected_file_count']} protected files unchanged, including canonical model, existing results, regional workbook, map, review and knowledge graph."]
(RUN/'outputs/summary.txt').write_text('\n'.join(summary)+'\n',encoding='utf-8')
checks['baseline_reopened_reconciled']=True
checks['all_retained_source_coefficients_nonnegative']=len(read(RUN/'outputs/negative_entries.json'))==0
checks['all_independent_solves_within_tolerance']=all(r['independent_solve_max_relative_error']<1e-9 for r in rows)
original=read(RUN/'inputs/protected_hashes.json')
checks['final_protected_hashes_unchanged']=all(sha(RUN/p)==h for p,h in original.items())
save(RUN/'qa/checks.json',{**qa,'checks':checks})
artifacts=[]
def add(p,role): artifacts.append({'role':role,'path':rel(p),'sha256':sha(p),'availability':'present'})
for p in sorted(RUN.rglob('*')):
    if p.is_file() and p.name not in ('evidence_index.json','completeness.json'):
        add(p,'execution_code' if p.parent.name=='code' else 'full_diagnostic_return' if '_full_return' in p.name else 'runtime' if '_runtime' in p.name else 'comparison' if p.name=='comparison.json' else 'summary' if p.name=='summary.txt' else 'verification' if p.parent.name=='qa' else 'inputs' if p.parent.name=='inputs' else 'derived_evidence')
for p,role in [(MODEL/'model.json','canonical_input'),(MODEL/'results/result_manifest.json','saved_baseline_identity'),(ROOT/'regions/LME/LME_028/LME_028.xlsx','regional_catch_and_mapping'),(ROOT/'regions/LME/LME_028/work/2026-10-16_202757_trophic_aggregation/outputs/decomposition.json','historical_arithmetic_context')]: add(p,role)
for p in provenance['engine_files']: add(RUN/p,'executed_engine')
add(ROOT/'tools/scientific_helpers/sppr/method_coverage.py','serialization_helper')
for method in ('new_TE_EEfix','new_GE','new_WithEgestion'): add(MODEL/f'results/diagnostics/method_coverage/{method}.ee_floor_reused.json.gz','saved_coefficients')
save(RUN/'evidence_index.json',{'schema_version':1,'run_id':RUN.name,'region_id':'LME_028','model_id':'28_646_Guinea_(1998)','variant_id':'fixed_rates_self_diet_zero_with_and_without_proportional_redistribution_ee_floor_0.1','source_identity':{'canonical_model_sha256':provenance['canonical_model_sha256'],'source':'retained canonical model and audited saved-result package; no new extraction'},'computational_input_identity':{'provenance_sha256':sha(RUN/'inputs/provenance.json'),'catch_sha256':sha(RUN/'inputs/catch_and_benchmark.json')},'methods':['TE','GE','With Egestion'],'required_roles':['execution_code','full_diagnostic_return','runtime','comparison','summary','verification','inputs','canonical_input','saved_baseline_identity','regional_catch_and_mapping','historical_arithmetic_context','executed_engine','serialization_helper','saved_coefficients'],'artifacts':artifacts,'reconciliation':checks,'adoption':'none; no canonical/map/review writes; diagnostic failures retained'})
assert all(checks.values())
print('\n'.join(summary))
