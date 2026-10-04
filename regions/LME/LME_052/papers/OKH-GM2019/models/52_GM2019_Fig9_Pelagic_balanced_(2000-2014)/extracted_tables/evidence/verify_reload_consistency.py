"""Check frozen native reload state and retained direct diagnostic reproducibility."""
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import io, json
import numpy as np
import reconstruct_and_verify as r

H = Path(__file__).resolve().parent
frozen = r.sha(H / 'model.json')
assert frozen == '9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656'
retained = r.read(H / 'native_reload_result.json')
final = r.read(H / 'final_verification.json')['actual_main_return']
fields = ['P', 'Q', 'EE', 'GS', 'GE', 'BA', 'D', 'M0', 'R', 'U',
          'catch', 'immigration', 'emigration', 'net_migration', 'detritus_export']
saved_rows = {row['group_id']: row for row in retained['rows']}
final_rows = {row['group_id']: row for row in final['rows']}
log = io.StringIO()
with redirect_stdout(log), redirect_stderr(log):
    calc = r.PPRCalculator(str(H / 'model.json'), **r.SETTINGS)
state = r.snapshot(calc)
fresh_rows = {row['group_id']: row for row in state['rows']}
checks = {}
for field in fields:
    checks[field] = {
        'fresh_vs_retained_max_abs_difference': max(abs(fresh_rows[n][field] - saved_rows[n][field]) for n in saved_rows),
        'final_vs_retained_max_abs_difference': max(abs(final_rows[n][field] - saved_rows[n][field]) for n in saved_rows)}
diagnostics = {}
for option in ['GE', 'TE', 'With Egestion']:
    tag = option.replace(' ', '_')
    saved = r.read(H / 'diagnostics' / f'{tag}_full_return.json')
    with redirect_stdout(log), redirect_stderr(log):
        report, sppr, A, L = calc.diagnose_sppr(TE_option=option, short=False, flat=False, return_sppr=True)
    expected = saved['SPPR']
    same_axes = list(sppr.index) == expected['index'] and list(sppr.columns) == expected['columns']
    diagnostics[option] = {
        'retained_return_sha256': r.sha(H / 'diagnostics' / f'{tag}_full_return.json'),
        'same_axes': same_axes,
        'max_abs_SPPR_difference': float(np.max(np.abs(sppr.to_numpy() - np.asarray(expected['data'])))),
        'same_status': report['status'] == saved['report']['status']}
result = {
    'model_sha256': frozen,
    'retained_native_state_sha256': r.sha(H / 'native_reload_result.json'),
    'retained_diagnostic_state_detritus_BA_tC_km2_year': saved_rows[22]['BA'],
    'final_independent_state_detritus_BA_tC_km2_year': final_rows[22]['BA'],
    'fresh_repeat_detritus_BA_tC_km2_year': fresh_rows[22]['BA'],
    'actual_main_is_model_balanced': state['main_is_model_balanced'],
    'field_comparisons': checks,
    'direct_diagnostic_comparisons': diagnostics,
    'all_values_exactly_reproduced': all(v == 0 for check in checks.values() for v in check.values()) and all(d['same_axes'] and d['same_status'] and d['max_abs_SPPR_difference'] == 0 for d in diagnostics.values()),
    'solver_initialization': 'Engine apply_lim uses deterministic coordinated biological x0 and ordered cols_to_solve; no random initialization.',
    'interpretation': 'The earlier approximate 242.537 detritus BA in commentary was stale. Saved frozen-model state and independent reload agree at 242.50886238380988. No repeat-reload nonuniqueness was observed; this does not claim GS is empirically identified.',
    'no_model_or_engine_mutation': r.sha(H / 'model.json') == frozen}
r.save(H / 'reload_consistency.json', result)
(H / 'reload_consistency.log').write_text(log.getvalue(), encoding='utf-8')
assert result['all_values_exactly_reproduced']
provenance = r.read(H / 'runtime_provenance.json')
provenance['execution_scripts_sha256'][Path(__file__).name] = r.sha(Path(__file__))
provenance['reload_consistency'] = {
    'evidence': 'reload_consistency.json',
    'retained_diagnostic_state_detritus_BA_tC_km2_year': saved_rows[22]['BA'],
    'all_saved_and_reloaded_values_exactly_reproduced': result['all_values_exactly_reproduced'],
    'initialization': result['solver_initialization'],
    'interpretation': result['interpretation'],
    'regional_coefficient_state': 'Regional coefficients use the retained native state and direct method returns. Independent reload checks prove this state is reproducible; they do not substitute coefficients.'}
r.save(H / 'runtime_provenance.json', provenance)
print(json.dumps({'all_values_exactly_reproduced': result['all_values_exactly_reproduced'], 'detritus_BA': saved_rows[22]['BA']}))
