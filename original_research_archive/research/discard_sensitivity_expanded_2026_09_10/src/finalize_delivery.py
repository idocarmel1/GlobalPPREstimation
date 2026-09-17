"""Write a verified handoff and hash the reviewable delivery artifacts."""
from pathlib import Path
from collections import Counter
import json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def run():
    output=read('verification/output_checks.json');browser=read('verification/browser_checks.json');runtime=read('verification/report_runtime_checks.json');counts=read('verification/summary_counts.json');findings=read('results/scientific_findings.json')
    assert output['passed'] and browser['passed'] and runtime['passed']
    assert '34 passed' in (ROOT/'verification/tests.log').read_text(encoding='utf-8')
    selected=read('results/selected_models.json');screen=read('results/candidate_screening.json')
    df=pd.read_csv(ROOT/'results/ecosystem_ppr.csv');added=df[df.cohort=='additional']
    coverage=added.groupby(['method','scope','route','fraction'],dropna=False).agg(n_cases=('valid','size'),n_valid=('valid','sum')).reset_index()
    coverage.to_csv(ROOT/'results/method_scenario_coverage.csv',index=False)
    checks=sum(output['check_counts'].values())
    text=f'''# Verified expansion handoff

Exactly 20 additional source-valid existing marine Ecopath JSONs, representing 18 named ecosystems, have been evaluated at all 27 solved fractions. The four original references are separate and use the same dense grid. Okhotsk remains a zero-harvest null control. All writes stayed in this research namespace; no Git/index/branch operation, production export, NPP edit or shared-engine mutation was performed.

## Verification

- {counts['scenario_records']:,} final scenario records and {counts['group_coefficient_rows']:,} group-coefficient rows.
- All eight required methods and applicable all/inner/PP scopes are retained. SC/SM/SE use every grid point; unsupported added-model SR and chain source scopes stay unavailable. The 52,320 added-model records contain 25,621 valid, 26,120 unavailable, 531 failed method-conservation checks and 48 other invalid cases; nothing is replaced with zero. Detailed support is in method_scenario_coverage.csv.
- {checks:,} independent output checks, zero failures; 34 focused tests pass.
- All 3,936 overlapping original records match coefficients, PPR and validity masks.
- 551 baseline comparisons: 486 strict matches, 16 unavailable, 49 strict saved-workbook differences. All 49 reproduce under raw-diet replay. The experiment preserves normalized diets within the recorded source-rounding tolerance.
- Actual in-app browser checks cover controls, dense fractions, original versus added models, source scopes, retained landings, invalid methods, source-compatible PP ratios, aggregate support, screening/hashes and screenshots. Browser-displayed values match the numerical CSV. The same embedded JavaScript passes nine runtime/export cases and full compact-JSON equality.
- CSV/JSON Save file links completed the browser's supported downloadMedia action without error; the API returns no destination path. The initial native-download-event probe timed out, so persistent explicit save links were added and verified. Export lengths and contents match the independently checked numerical payloads.

## Main findings

At 20% SM discard on the same original H, the new_GE median coefficient increase is +0.9628% (20/20; range +0.0001% to +20.9640%). With egestion it is +0.2522% (20/20); TE_EEfix is +24.9853% (18/20), and Ulanowicz_TE is +18.8469% (20/20). The retained-landings GE median is -19.2298%, showing why coefficient and numerator effects must remain separate. Prince William Sound's TEmean case has +68.6679% coefficients and +34.9343% retained-landings PPR at 20% discard.

The fixed standard is above new_GE in 5 of 20 cases and below it in 15 at 20% SM. Against WithEgestion, signs split 12 above and 8 below. There is no universal standard overestimation. SC is invariant; SC and SE agree below the zero-catch endpoint. There are no validity transitions inside the 0–20% grid. The largest low-range second difference is 0.180611 response percentage points near 19% for Prince William Sound / TEmean; no unsolved point is presented as solved.

At 100%, method support can fall sharply: GE and WithEgestion retain 17/20, TE_EEfix 4/20, and Ulanowicz 14/20 for SM/all-source paired changes. SPPR_1986 is undefined at zero catch; TEmean uses biomass weights. Some finite flow-method endpoint coefficients are extremely large and sensitive to source rounding as remaining removal approaches zero. They are stress diagnostics, not robust ecological forecasts. Invalid cases remain missing.

## Source and inference limits

All 252 corpus files are inventoried; 20 qualify after the first 52 queued candidates. The original ordering was fixed before sensitivity results. A documented source-fidelity amendment, following input review of provisional runs, replaced Santa Pola Bay (marine fish farm), Western Channel, Moreton Bay and Western Bering Sea. The first two erase nonzero documented onward routes; the latter two need unobserved detritus stock draw. Their completed exploratory results remain in results/excluded_provisional_models and enter no valid aggregates. All four replacements follow the unchanged candidate queue.

Nineteen final models change zero DET fate rows to identity, a disclosed representation change with zero DET M0/egestion; one is unchanged. No nonzero documented detritus onward fate is overwritten in the final cohort. Dependent detritus accumulation remains the original accounting convention, not an observed dynamics claim. Central and North Atlantic each have two dependent time observations. Native currency is WetWeight; unknown mass/area/time normalization stays unknown, and absolute native totals are not pooled. Scenario spread is a sensitivity range, not a confidence interval or global model-validity estimate.

## Artifacts and proposed interface

- Report: {ROOT.as_posix()}/report.html
- Scientific methods/findings: {ROOT.as_posix()}/METHODS_AND_FINDINGS.md
- Source catalog/screening: {ROOT.as_posix()}/results/selected_models.json and candidate_screening.json
- Numerical outputs: {ROOT.as_posix()}/results/ecosystem_ppr.csv, group_sppr.csv, effect_decomposition.csv, scenario_envelopes.csv, aggregate_distributions.csv, method_scenario_coverage.csv
- Verification: {ROOT.as_posix()}/verification/output_checks.json and browser_checks.json
- Response data: {ROOT.as_posix()}/results/discard_responses.v2.json
- Consumer contract: {ROOT.as_posix()}/RESPONSE_INTERFACE.md

The versioned response file is a proposal for later ownership-coordinated integration. It requires an exact source hash/group identity, unchanged retained-landings support, valid baseline/endpoints, explicit scope and /9 convention, fixed annual selected/global NPP denominator across compared endpoints, and preserved missing-data masks. It does not authorize a global donor proxy, new mappings, yearly Ecopath reconstruction, interpolation across invalid points/weight changes, or installation into the live atlas. Parent task coordinates handoff to Complete all-ecosystem PPR and NPP integration (01a08d18-5b20-7b80-8ba3-5dfac3b22cac).
'''
    (ROOT/'FINAL_HANDOFF.md').write_text(text,encoding='utf-8')
    (ROOT/'EXECUTION_STATE.md').write_text('# Complete — verified numerical and browser delivery\n\nAll requested expansion work is complete. See FINAL_HANDOFF.md, METHODS_AND_FINDINGS.md, verification/output_checks.json and verification/browser_checks.json. The original study and production files were preserved. No Git/index/branch mutations occurred. The loopback preview used its own dynamically assigned port and can be stopped after review.\n',encoding='utf-8')
    paths=[ROOT/p for p in ['report.html','README.md','SELECTION_POLICY.md','METHODS_AND_FINDINGS.md','RESPONSE_INTERFACE.md','FINAL_HANDOFF.md','input_manifest.json','workbook_input_manifest.json','workbook_input_manifest.v2.json']]
    paths+=list((ROOT/'src').rglob('*.py'))+list((ROOT/'src').glob('*.cjs'))+list((ROOT/'src').glob('*.html'))+list((ROOT/'tests').glob('*.py'))
    paths+=list((ROOT/'results').glob('*.json'))+list((ROOT/'results').glob('*.csv'))
    paths+=[ROOT/'verification'/p for p in ['output_checks.json','browser_checks.json','browser_observations.json','report_runtime_checks.json','original_overlap.json','summary_counts.json','tests.log','static_checks.json','saved_workbook_differences.json']]
    paths+=list((ROOT/'results/excluded_provisional_models').glob('*/study.json'))
    files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(paths))]
    (ROOT/'artifact_manifest.json').write_text(json.dumps(dict(study_version='2026-09-10.discard-routing.expanded.v2',files=files),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Verified delivery:',len(files),'hashed artifacts;',len(selected),'additions;',counts)
if __name__=='__main__':run()
