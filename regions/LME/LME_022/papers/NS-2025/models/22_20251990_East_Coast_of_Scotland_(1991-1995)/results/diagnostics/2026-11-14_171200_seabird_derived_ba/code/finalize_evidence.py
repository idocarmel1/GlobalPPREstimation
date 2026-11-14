"""Label a retained intermediate state explicitly and finalize evidence (no solver)."""
from pathlib import Path
import hashlib
import json
from datetime import datetime,timezone

RUN=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

path=RUN/'inputs/intervention.json'
before=sha(path)
ledger=load(path)
previous_finalization=load(RUN/'qa/evidence_metadata_finalization.json') if (RUN/'qa/evidence_metadata_finalization.json').exists() else None
if 'experiment_state_fields' in ledger:
    ledger['diet_only_intermediate_state_fields']=ledger.pop('experiment_state_fields')
if 'protected_fields_unchanged' in ledger:
    ledger['diet_only_intermediate_protected_fields_unchanged']=ledger.pop('protected_fields_unchanged')
ledger['state_field_roles']={
    'archived_state_fields':'Exact baseline scientific state from the preserved archive.',
    'diet_only_intermediate_state_fields':'Intermediate after diet redistribution and predation refresh but BEFORE eligible BA recomputation. Never the final variant.',
    'corrected_state_fields':'Effective final variant scientific state used for all three fresh diagnostics.'}
save(path,ledger)
save(RUN/'qa/evidence_metadata_finalization.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
    purpose='Clarify inherited intermediate-state label without modifying any values or scientific execution code.',
    path='inputs/intervention.json',before_sha256=before,after_sha256=sha(path),
    renamed_fields={'experiment_state_fields':'diet_only_intermediate_state_fields',
                    'protected_fields_unchanged':'diet_only_intermediate_protected_fields_unchanged'},numerical_values_unchanged=True,
    executed_scientific_code_sha256=sha(RUN/'code/run_correction.py'),metadata_script_sha256=sha(Path(__file__)),
    prior_metadata_finalization=previous_finalization))
save(RUN/'qa/multiplier_precision.json',dict(
    archived_diet_sum=ledger['diet_before_sum'],corrected_diet_sum=ledger['diet_after_sum'],
    retained_run_ledger_factor=ledger['remaining_prey_multiplier'],
    value_in_carried_forward_investigation=1.0002001200720432,
    absolute_difference=ledger['remaining_prey_multiplier']-1.0002001200720432,
    explanation='One double-precision ULP from floating summation/normalization; no biological difference or tolerance change. Exact before/after cells remain authoritative.',
    before_after_cells='inputs/intervention.json#changed_diet_cells'))

comparison=load(RUN/'outputs/comparison.json')
summary=['# Scotland candidate: seabird diet and derived BA correction','',
    'This is an unadopted derived runtime variant for researcher review. The canonical source model, its missing values and original diet, publications/native inputs, historical diagnostics and old result manifest are preserved. LME_022 remains selected to ICES_WGSAM2015_North_Sea_1991; this package concerns only the explicitly named Scotland candidate.','',
    '## Correction and provenance','',
    'All 25 ecological groups and the synthetic diet-import group remain. Only the Seabirds (22) consumer diet changes. Source Table S3!W24 self-feeding is 0.0002; the exact archived normalized entry is 0.0002000800320128051. It is set to zero in the runtime copy, and all remaining prey (including Detritus 25) are proportionally normalized. The retained factor is 1.0002001200720434; the carried-forward value 1.0002001200720432 differs by one double-precision ULP (2.220446049250313e-16), without a biological difference. The archived diet sum is 0.9999999999999998 and the resulting sum is 1. Exact before/after cells are listed below and in the linked ledger. All other consumers’ diets are byte-equivalent at the typed-state level. This user-authorized derived scenario does not establish that the published self-diet was a typographical error.','',
    'All prey predation was recomputed from the changed diet and retained consumption. Only 13 affected BA entries were recomputed. Each has a source -9999 missing marker, explicit loader-derived evidence in LOADER_TRANSFORMATIONS.csv, and an archived value matching that ledger within 1e-12 absolute/relative tolerance. No affected BA has observed/manual/uncertain provenance; there are no skipped affected entries. Unaffected BA is preserved exactly. BA remains a derived balancing residual, not measured accumulation or an author-confirmed biological correction.','',
    'The equation is BA = P - M0 - catch - predation - net migration. Production, consumption, mortality, EE, catch, migration, egestion, respiration, biomass, routing and all other protected biological fields are unchanged. The historical broad balance_model routine and constructors are never called. No EE floor is introduced.','',
    'Detritus receives the same routed M0 + egestion inflow (1879.1437 t wet weight km^-2 year^-1). Its predation removal rises from 220.72839973232996 to 220.72842765756852, and its proven-derived BA falls by the same amount, from 1658.41530026767 to the exact value in the table below. Detritus catch, M0, net migration and external export remain zero.','',
    '## Exact changed diet cells','',
    '| Publication cell | Prey ID/name | Canonical source | Archived runtime before | Corrected runtime after |',
    '|---|---|---:|---:|---:|']
for row in ledger['changed_diet_cells']:
    summary.append(f"| {row['publication_cell']} | {row['prey_id']} {row['prey_name']} | {row['canonical_source_value']:.17g} | {row['before']:.17g} | {row['after']:.17g} |")
summary += ['', '## Exact eligible BA changes','',
    'Units: t wet weight km^-2 year^-1. Every row below is a retained missing-source, loader-derived value.','',
    '| Group | Before | After | Change | Provenance CSV line |', '|---|---:|---:|---:|---:|']
for row in ledger['ba_changes']:
    summary.append(f"| {row['group_id']} {row['group_name']} | {row['before']:.17g} | {row['after']:.17g} | {row['difference']:.17g} | {row['provenance_ledger_line']} |")
summary += ['', '## Actual diagnostics','',
    '| State | Method | Grade | rho living | PP budget gap (%) | Strict model / SPPR balance | Negative SPPR entries |',
    '|---|---|---|---:|---:|---|---:|']
for row in comparison:
    state={'baseline':'Retained reproduced baseline','remove_redistribute':'Retained diet-only, BA fixed',
           'seabird_no_self_loop_proportional_prey_derived_ba':'Fresh corrected variant'}[row['scenario']]
    summary.append(f"| {state} | {row['method']} | {row['status']} | {row['rho']:.17g} | {row['pp_budget_gap_percent']:.17g} | {row['strict_model_balanced']} / {row['strict_sppr_balanced']} | {row['negative_sppr_entries']} |")
summary += ['',
    'The baseline TE self-loop A[22,22] = 1.1127784447112168 caused living-network divergence; no other consumer eats seabirds. It generated negative Phytoplankton (1) → Seabirds (22) = -1916160.3191561818 and Detritus (25) → Seabirds (22) = -460709.19237909134. The corrected A[22,22] is zero, rho living is 0.2757420229532071, and every SPPR contribution is nonnegative in all three fresh methods.','',
    'TE remains WARN because Cetaceans (24), Seals (23) and Seabirds (22) have near-zero transfer efficiencies. This is distinct from the removed feedback divergence and from budget balance. TE reports b=0 by convention because mortality-derived requirements are written off; that value does not establish absence of physical recycling. No overall OK claim is made for TE.','',
    'Fresh GE b = 0.0698576437258916; With Egestion b = 0.09711476293526844. Fresh seabird total SPPR: GE 5506.446079035624, TE 268113.2909082857, With Egestion 1908.2357402357948. Detritus (25) total SPPR: GE 1.0828711378491187; TE 0.8104489294778254; With Egestion 1.2093390220288438. Full named basal-source coefficients, detritus coefficients, masks, axes, negative entries (including operator entries), thresholds and exact returns are retained in each method artifact.','',
    '## Reproduction and limitations','',
    'Run code/run_correction.py using the scientific Python environment in run_manifest.json, then code/finalize_evidence.py. The first script restores persisted typed attributes via __new__ without rerunning defaults; verifies the unchanged 47-artifact prior experiment; writes exact before/corrected/all-method before-and-after state; and runs only GE, TE and With Egestion. The second script clarifies the name of the intermediate diet-only state and creates this summary, without running a solver or changing values.','',
    'The prior nine-run baseline evidence is reused after hash verification, not claimed to have been executed again in this package. Its matching original source matrices support the comparison. The original direct-return loss and the old result manifest’s unknown historical execution remain historical limitations; this fresh execution does not rewrite them. This package does not establish publication-native equivalence, whole-North-Sea geographic applicability, researcher approval, selection, or adoption of regional coefficients.','',
    'Actual diagnostic configuration: historical engine PPRCalculator.py SHA-256 b2bb08f0564c8cd0fcc873eb1c681fd924c3dd113e22d6b388456248fc0162a7; canonical model SHA-256 5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691; det_collapse_mode=never, det_open_mode=none, det_theta=1, det_external_sppr=0, fix_EE_0_cases=True; full (short=False, flat=False) returns, with SPPR/A/L from the same calls. EE floor OFF; historical thresholds unchanged. Exact runtime/code/source hashes and interpreter/dependency versions are in the manifest.','',
    'Evidence navigation: [manifest](run_manifest.json), [correction/BA ledger](inputs/intervention.json), [comparison](outputs/comparison.json), [matrix QA](qa/reopened_matrix_checks.json), [evidence index](evidence_index.json), [completeness](qa/completeness.json).']
(RUN/'correction_summary.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')

index=load(RUN/'evidence_index.json')
# Keep all external preserved artifacts exactly; rebuild only the current package inventory.
index['artifacts']=[a for a in index['artifacts'] if a['path'].startswith('../')]
for p in sorted(RUN.rglob('*')):
    if not p.is_file() or p.name in ('evidence_index.json','completeness.json'):continue
    role='execution_evidence'
    if p.name=='intervention.json':role='correction_and_ba_provenance'
    elif p.name=='reopened_matrix_checks.json':role='matrix_verification'
    elif p.name=='comparison.json':role='before_after_comparison'
    elif p.name.startswith('runtime_state_'):role='exact_runtime_state'
    elif p.suffix=='.py':role='reproduction_code'
    elif p.name in ('corrected_GE.json','corrected_TE.json','corrected_With_Egestion.json'):role='full_direct_return'
    elif p.name=='correction_summary.md':role='readable_correction_report'
    index['artifacts'].append(dict(role=role,path=p.relative_to(RUN).as_posix(),sha256=sha(p),availability='present'))
index['reconciliation']['intermediate_and_effective_state_roles_explicit']=True
save(RUN/'evidence_index.json',index)
print('Finalized metadata and evidence inventory without modifying numerical results.')
