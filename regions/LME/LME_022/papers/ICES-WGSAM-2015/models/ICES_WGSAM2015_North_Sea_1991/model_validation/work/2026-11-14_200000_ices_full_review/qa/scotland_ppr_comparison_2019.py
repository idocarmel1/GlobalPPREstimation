"""Report arithmetic from retained Scotland coefficients and exact mapping weights."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview

S = ROOT / 'regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)'
D = S / 'results/diagnostics/2026-11-14_171200_seabird_derived_ba'
OUTPUT = Path(__file__).with_suffix('.json')
HASHES = {}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    data = p.read_bytes()
    HASHES[p.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
    return json.loads(data)


def close(a, b):
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-9)


def main():
    audit = read(S / 'model_validation/evidence/source_review/taxon_audit.json')
    mapping_verification = read(S / 'model_validation/work/2026-11-14_180000_appendix_review/outputs/mapping_verification.json')
    handoff = read(S / 'model_validation/work/2026-11-14_180000_appendix_review/outputs/report_handoff.json')
    manifest = read(D / 'run_manifest.json')
    model = read(S / 'model.json')
    group_names = {int(g['group_seq']): g['group_name'] for g in model['group']}
    protected = [S / 'model_validation/validation.docx', S / 'model_validation/taxon_mapping.xlsx', S / 'results/regional_snapshot.xlsx', ROOT / 'regions/LME/LME_022/LME_022.xlsx']
    for p in protected:
        HASHES[p.relative_to(ROOT).as_posix()] = sha(p)
    assert HASHES[(S / 'model_validation/validation.docx').relative_to(ROOT).as_posix()] == '500a5734b3e6de8924af64c5b0abf59ed0c368f91fd1b817dabda4ff79e3fbf5'
    assert HASHES[(S / 'model_validation/taxon_mapping.xlsx').relative_to(ROOT).as_posix()] == 'c3cbe2fd6ba79229dbfb446ab196a5f39b00eed3705c3540da56e3dc8b6a091c'
    assert sha(S / 'model.json') == manifest['canonical_model_sha256'] == mapping_verification['canonical_sha256']
    assert sha(S / 'results/regional_snapshot.xlsx') == mapping_verification['snapshot_sha256']
    assert sha(S / 'model_validation/evidence/source_review/taxon_audit.json') == mapping_verification['retained_audit_sha256']
    assert mapping_verification['snapshot_matching_differences'] == []
    workbook = read_book(protected[-1], sheets=['Catch', 'Classic PPR', 'Overview'])
    catch_records = [r for r in records(workbook, 'Catch', 'Catch') if r['catch_basis'] == 'catch']
    catch = {r['taxon']: r[2019] for r in catch_records}
    classic = {r['taxon']: r for r in records(workbook, 'Classic PPR', 'Taxa')}
    assert len(catch_records) == len(catch) == len(audit) == 384
    assert set(catch) == {r['taxon'] for r in audit}
    assert all(close(r['catch_tonnes'], catch[r['taxon']]) for r in audit)
    assert all(close(r['classic_coefficient_wet'], classic.get(r['taxon'], {}).get('sppr')) for r in audit)
    assert overview(workbook)['selected_model_id'] == 'ICES_WGSAM2015_North_Sea_1991'

    coefficients, diagnostics = {}, {}
    for method in ['GE', 'TE']:
        full = read(D / f'outputs/corrected_{method}.json')
        scope = read(D / f'outputs/corrected_{method}_scopes.json')['all']
        coefficients[method] = dict(zip(scope['index'], scope['values']))
        matrix = full['SPPR']
        assert matrix['columns'] == [26, 25, 1]
        assert all(close(sum(values), coefficients[method][group]) for group, values in zip(matrix['index'], matrix['values']))
        assert all(math.isfinite(x) and x >= 0 for values in matrix['values'] for x in values)
        diagnostics[method] = {'status': full['diagnostic']['status'], 'rho_living': full['diagnostic']['divergence']['rho_living'], 'b': full['diagnostic']['divergence']['b'], 'warnings': full['diagnostic']['warnings'], 'strict_model_balanced': full['diagnostic']['model_input']['is_model_balanced'], 'strict_sppr_balanced': full['diagnostic']['balance']['is_balanced'], 'method_options': full['options']}

    exclusions = {22, 23, 24}
    rows = []
    for item in audit:
        taxon = item['taxon']
        c = catch[taxon]
        gs = item['groups']
        assert not gs or close(sum(g['weight'] for g in gs), 1)
        assert all(group_names[g['seq']] == g['group_name'] and g['weight'] >= 0 for g in gs)
        included = [g for g in gs if g['seq'] not in exclusions]
        removed_weight = sum(g['weight'] for g in gs if g['seq'] in exclusions)
        row = {'taxon': taxon, 'catch_tonnes': c, 'classic_ppr_tC': item['simple_chain_ppr_tC'], 'confidence': item['overall_confidence'], 'membership_confidence': item['membership_confidence'], 'allocation_confidence': item['allocation_confidence'], 'groups': gs, 'mapping_resolved': bool(gs), 'signed_excluded_allocation_weight': removed_weight, 'signed_excluded_catch_tonnes': c * removed_weight, 'signed_included_catch_tonnes': c * sum(g['weight'] for g in included) if gs else None, 'methods': {}}
        for method in coefficients:
            coef = sum(g['weight'] * coefficients[method][g['seq']] for g in gs) if gs else None
            signed_coef = sum(g['weight'] * coefficients[method][g['seq']] for g in included) if gs else None
            ppr = c * coef / 9 if coef is not None else (0.0 if c == 0 else None)
            signed_ppr = c * signed_coef / 9 if signed_coef is not None else (0.0 if c == 0 else None)
            row['methods'][method] = {'weighted_all_source_sppr_wet': coef, 'ppr_tC_before_signed_exclusions': ppr, 'signed_included_weighted_sppr_wet': signed_coef, 'ppr_tC_after_signed_exclusions': signed_ppr}
        rows.append(row)

    unresolved = [r for r in rows if not r['mapping_resolved']]
    positive_unknown = [r for r in unresolved if r['catch_tonnes'] > 0]
    total_catch = sum(r['catch_tonnes'] for r in rows)
    mapped_catch = sum(r['catch_tonnes'] for r in rows if r['mapping_resolved'])
    totals = {}
    for method in coefficients:
        before = sum(r['methods'][method]['ppr_tC_before_signed_exclusions'] or 0 for r in rows)
        after = sum(r['methods'][method]['ppr_tC_after_signed_exclusions'] or 0 for r in rows)
        confidence = []
        for conf in ['High', 'Medium', 'Low', 'Very low', 'Unresolved']:
            rr = [r for r in rows if r['confidence'] == conf]
            known = sum(r['methods'][method]['ppr_tC_after_signed_exclusions'] or 0 for r in rr)
            confidence.append({'confidence': conf, 'taxa': len(rr), 'catch_tonnes': sum(r['catch_tonnes'] for r in rr), 'known_ppr_tC': known, 'known_ppr_percent': known / after * 100, 'unknown_positive_catch_taxa': sum(r['methods'][method]['ppr_tC_after_signed_exclusions'] is None for r in rr)})
        top = sorted((r for r in rows if r['methods'][method]['ppr_tC_after_signed_exclusions'] is not None), key=lambda r: r['methods'][method]['ppr_tC_after_signed_exclusions'], reverse=True)[:10]
        totals[method] = {'known_subtotal_tC_before_signed_exclusions': before, 'known_subtotal_tC_after_signed_exclusions': after, 'removed_ppr_tC': before - after, 'total_is_complete': not positive_unknown, 'mapped_support_taxa': sum(r['mapping_resolved'] for r in rows), 'confidence_exposure': confidence, 'top_taxa': [{'taxon': r['taxon'], 'ppr_tC': r['methods'][method]['ppr_tC_after_signed_exclusions'], 'ppr_percent': r['methods'][method]['ppr_tC_after_signed_exclusions'] / after * 100, 'confidence': r['confidence']} for r in top]}

    report = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'operation': 'Read-only report arithmetic from retained source-resolved GE/TE coefficients, exact existing candidate mapping weights, and current 2019 catch; no scientific-engine call or adoption.', 'model_id': S.name, 'coefficient_variant_id': manifest['variant_id'], 'year': 2019, 'catch_basis': 'catch = landings plus discards', 'scope': 'all basal sources: diet_import26 + Detritus25 + Phytoplankton1', 'formula': 'sum over taxa(catch_tonnes * sum over mapped groups(weight * all-source coefficient)) / 9; unresolved positive-catch coefficients remain unknown.', 'mapping_source': (S / 'model_validation/evidence/source_review/taxon_audit.json').relative_to(ROOT).as_posix(), 'mapping_scope': handoff['scope'], 'mapping_snapshot_check': 'Existing saved exact-key weight comparison is hash-eligible: canonical, retained audit and full snapshot hashes match verification with zero snapshot_matching_differences.', 'current_regional_selection': overview(workbook)['selected_model_id'], 'runtime': {'use_ee_floor': manifest['use_ee_floor'], 'constructor': manifest['constructor'], 'historical_engine_sha256': manifest['historical_engine_sha256'], 'historical_constructor_record': manifest['historical_constructor_record'], 'method_options': manifest['method_options'], 'biological_changes': manifest['biological_parameters_changed'], 'dependent_changes': manifest['dependent_derived_fields_changed'], 'not_common_engine_with_ices': True}, 'diagnostics': diagnostics, 'signed_review': {'verdict': 'MODEL VALIDATED', 'researcher': 'Ido Carmel', 'date': '14/11/2026', 'excluded_groups': [{'id': x, 'name': group_names[x]} for x in sorted(exclusions)], 'reason_exact': 'All due to GE<0.01', 'application': 'Omit allocated catches and PPR for excluded recipient groups without redistributing weights; source matrices retain all groups and trophic pathways. No post-exclusion network solve.', 'affected_taxa': [r['taxon'] for r in rows if r['signed_excluded_allocation_weight'] > 0], 'excluded_catch_tonnes': sum(r['signed_excluded_catch_tonnes'] for r in rows)}, 'coverage': {'taxa': len(rows), 'total_catch_tonnes': total_catch, 'mapped_catch_tonnes': mapped_catch, 'mapped_catch_percent': mapped_catch / total_catch * 100, 'unresolved_catch_tonnes': sum(r['catch_tonnes'] for r in unresolved), 'unresolved_catch_percent': sum(r['catch_tonnes'] for r in unresolved) / total_catch * 100, 'unresolved_taxa': [r['taxon'] for r in unresolved], 'positive_catch_unknown_ecopath_ppr': [{'taxon': r['taxon'], 'catch_tonnes': r['catch_tonnes'], 'known_classic_ppr_tC': r['classic_ppr_tC']} for r in positive_unknown], 'unresolved_known_classic_ppr_tC': sum(r['classic_ppr_tC'] for r in unresolved), 'common_support_taxa_for_ices_comparison': [r['taxon'] for r in rows if r['mapping_resolved']]}, 'totals': totals, 'rows': rows, 'source_sha256': HASHES}
    report['inputs_unchanged_during_arithmetic'] = all(sha(ROOT / p) == value for p, value in HASHES.items())
    assert report['inputs_unchanged_during_arithmetic']
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'output': OUTPUT.relative_to(ROOT).as_posix(), 'GE_tC': totals['GE']['known_subtotal_tC_after_signed_exclusions'], 'TE_tC': totals['TE']['known_subtotal_tC_after_signed_exclusions'], 'total_catch_tonnes': total_catch, 'mapped_catch_tonnes': mapped_catch, 'unresolved_catch_tonnes': report['coverage']['unresolved_catch_tonnes'], 'positive_unknown_taxa': report['coverage']['positive_catch_unknown_ecopath_ppr'], 'excluded_taxa': report['signed_review']['affected_taxa'], 'excluded_catch_tonnes': report['signed_review']['excluded_catch_tonnes'], 'protected_inputs_unchanged': report['inputs_unchanged_during_arithmetic']}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
