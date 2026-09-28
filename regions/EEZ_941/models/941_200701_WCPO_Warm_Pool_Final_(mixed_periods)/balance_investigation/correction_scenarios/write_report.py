from pathlib import Path
import json,hashlib
import pandas as pd
p=Path(__file__).resolve().parent
d=json.loads((p/'RESULTS.json').read_text())
lines=['# Experimental juvenile-tuna corrections — not adopted','',
'The unmodified model already returns numerical PPR, but all three diagnoses are FAIL. Five isolated sensitivity scenarios remove the two large juvenile inconsistencies: every scenario returns WARN for GE, TE and With Egestion, and OK for the primary-production budget check. None makes the entire model exactly mass-balanced. No canonical/source file, selection, regional workbook or central workbook was changed.','',
'## Most interpretable accounting hypothesis: D, preserve other mortality','',
'Keep biomass, Q/B, diet, catch and the original other-mortality flow M0 unchanged. For each juvenile set Pnew = predation + catch + M0old, PBnew = Pnew/B, and EEnew = (predation + catch)/Pnew. Biomass accumulation remains the published zero. This closes the missing production with higher turnover without also inventing extra other mortality. It is an artificial independent-group sensitivity, not a recovered native model.','',
'| Group | Published P/B | Experimental P/B | Change | Published EE | Experimental EE | New P/Q |',
'|---|---:|---:|---:|---:|---:|---:|']
for c in d['D_fixed_M0']['changes']:
 lines.append(f"| {c['group']} | {c['old_PB']:.3f} | {c['new_PB']:.9f} | +{c['PB_percent_change']:.2f}% | {c['old_EE']:.3f} | {c['new_EE']:.9f} | {c['new_P_over_Q']:.5f} |")
lines+=['','P/Q remains below the available assimilated fraction (0.8), with positive juvenile respiration and no negative respiration anywhere. Direct Q = P + egestion + respiration still closes. The original other-mortality flows are 0.00071553864 and 0.0038327424 tons/km²/year. Seven pre-existing negative biomass-accumulation estimates in other groups remain loader completions, not published evidence. No new negative accumulation occurs in D.','',
'D is close to simply adding fishing mortality catch/B to the printed P/B (1.413875519 for Small BET and 2.527765625 for Small YFT). This supports an omitted-fishing-turnover hypothesis as an interpretation worth investigating; it does not demonstrate that this is what happened in the original source.','',
'The paper used multistanza tuna groups. The official [EwE input guide](https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/) identifies stanza P/B as total mortality Z and jointly derives non-leading stanza biomass and Q/B under age-structure assumptions. Holding B and Q/B fixed while editing P/B therefore does not establish native stanza consistency. Neither these values nor their biological plausibility can be validated without the native model or independently justified turnover estimates.','',
'## Alternatives tested','',
'| Scenario | Small BET P/B; EE | Small YFT P/B; EE | Assumption |',
'|---|---|---|---|']
meaning={'A_fixed_EE':'Preserve printed EE: also increases M0 by 107.80% / 32.52%.','B_EE095':'Set both EE to an arbitrary 0.95: lower required production, much lower other mortality.','B_EE1_boundary':'EE=1 lower bound: zero other mortality; mathematical boundary, not a preferred ecological case.','C_negative_BA':'Keep PB/EE but fund catches through biomass decline; contradicts printed zero BA.','D_fixed_M0':'Preserve original M0; increase production and recompute EE.'}
for s in ['D_fixed_M0','A_fixed_EE','B_EE095','B_EE1_boundary','C_negative_BA']:
 a,b=d[s]['changes'];lines.append(f"| {s} | {a['new_PB']:.9f}; {a['new_EE']:.9f} | {b['new_PB']:.9f}; {b['new_EE']:.9f} | {meaning[s]} |")
c=d['C_negative_BA']['changes']
lines+=['',f"Scenario C requires BA = {c[0]['BA']:.12g} / {c[1]['BA']:.12g} tons/km²/year: declines of {-100*c[0]['BA_over_B_per_year']:.2f}% / {-100*c[1]['BA_over_B_per_year']:.2f}% of standing biomass per year. Its catch footprints stay exactly at baseline because this closes the budget with a negative stock-change term. It is a contrast case, not a reasonable steady-state correction. EE-only edits cannot suffice: at original production the required EE is 1.33821 / 1.12510, above 1.",'',
'## Direct diagnostic comparison','',
'All calls use the same frozen engine and original loader settings, all source groups, short=False and flat=False; return_sppr=True additionally retains the coefficients. There are no global, Monte Carlo or regional annual-PPR runs. Total source catch remains 0.0540203 tons/km²/year. Footprints below are source-model catch primary-production equivalents in tons/km²/year; they are not annual EEZ totals.','',
'| Scenario | Method | Overall | PP budget gap | Catch footprint | Change vs baseline |',
'|---|---|---|---:|---:|---:|']
for s,v in d.items():
 for method,r in v['methods'].items():
  assert 'exception' not in r,(s,method,r)
  base=d['baseline']['methods'][method]['ppr_all']
  lines.append(f"| {s} | {method} | {r['status']} | {100*r['PP_relative_gap']:.6f}% | {r['ppr_all']:.6f} | {100*(r['ppr_all']/base-1):+.3f}% |")
lines+=['','Every experimental PP budget is OK and every solver converges with zero negative SPPR sources. Overall WARN remains because the maximum production residual is 0.727940% (adult BET), compared with 69.421026% at baseline. Diagnostic consumption residual falls from 2.213278% to 0.046103%. Remaining residuals also occur in adult YFT, SKJ, Small SKJ and baby SKJ. These unchanged discrepancies are consistent with source precision/input mismatches; they were not repaired. Exact is_model_balanced remains false.','',
'TE retains its original warning that mortality-derived SPPR is written off, and its spectral-radius proximity warning. With Egestion retains a detritus-recycling proximity warning. These method warnings are separate from the removed juvenile imbalance.','',
'| Method | Small BET baseline → D SPPR | Small YFT baseline → D SPPR |',
'|---|---:|---:|']
for method in ['GE','TE','With Egestion']:
 a=d['baseline']['methods'][method]['juvenile_SPPR'];b=d['D_fixed_M0']['methods'][method]['juvenile_SPPR']
 lines.append(f"| {method} | {a['11']:.6f} → {b['11']:.6f} | {a['12']:.6f} → {b['12']:.6f} |")
lines+=['','## Published versus computational diet','',
'Source values were never normalized or overwritten. The existing computational loader normalizes rounded diet rows. Formula results using the raw published diet are separately retained in RESULTS.json. For D, raw-diet P/B and EE would be 1.412986407 / 0.789874836 (Small BET) and 2.531160175 / 0.881701283 (Small YFT). The runs above use the normalized computational predation, so the intended juvenile equation closes under the actual engine.','',
'Each scenario folder contains an isolated engine-compatible input, full raw diagnose_GE.json / diagnose_TE.json / diagnose_With_Egestion.json, SPPR matrices, loaded groups and per-group flow audit. RESULTS.json includes all coefficient comparisons and exact alternative formula targets. PROVENANCE.json records settings, code hashes and the unchanged canonical hash. The baseline raw diagnoses were verified equal to the prior diagnoses after JSON key serialization. artifact_manifest.json covers the final outputs. No scenario was adopted.']
(p/'CORRECTION_SCENARIOS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest={str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file() and f.name not in ['artifact_manifest.json','VERIFICATION.json']}
(p/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
assert all(sha(p/f)==h for f,h in manifest.items())
assert sha(p.parent.parent/'model.json')==json.loads((p/'PROVENANCE.json').read_text())['canonical_sha256_before']
(p/'VERIFICATION.json').write_text(json.dumps({'artifact_count':len(manifest),'artifact_hashes_verified':True,'canonical_unchanged':True,'direct_calls_returned':18,'baseline_matches_previous':True,'no_negative_SPPR_sources':True,'scenario_count_including_baseline':6},indent=2),encoding='utf-8')
print(json.dumps({'report':str(p/'CORRECTION_SCENARIOS.md'),'verified_artifacts':len(manifest)}))
