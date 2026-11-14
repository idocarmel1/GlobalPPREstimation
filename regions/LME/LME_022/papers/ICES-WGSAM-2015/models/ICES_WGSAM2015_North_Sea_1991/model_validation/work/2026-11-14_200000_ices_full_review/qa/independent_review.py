"""Read-only verification of the mapping stage's own decisions; no reassignment."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records

MODEL = ROOT / 'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'
RUN = MODEL / 'model_validation/work/2026-11-14_200000_ices_full_review'
CONFIDENCE = ['High', 'Medium', 'Low', 'Very low', 'Unresolved']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b):
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-8)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true', help='Use only after mapping author confirms final handoff.')
    parser.add_argument('--final-decisions', action='store_true', help='Confirmed final decision/handoff; appendix still being authored.')
    args = parser.parse_args()
    decision_path = MODEL / 'model_validation/evidence/mapping/mapping_decisions.json'
    handoff_path = MODEL / 'model_validation/evidence/mapping/report_handoff.json'
    narrative_path = RUN / 'inputs/report_narrative.json'
    workbook_path = ROOT / 'regions/LME/LME_022/LME_022.xlsx'
    paths = [decision_path, handoff_path, narrative_path, MODEL / 'model.json', workbook_path,
             RUN / 'inputs/source_research/source_findings.json',
             RUN / 'inputs/source_research/group_definitions.json',
             ROOT / 'research/agents/selected_regions_validation_20260930/evidence/verification/residual_fish_reporting_scope_review.json']
    input_hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in paths}
    decisions = json.loads(decision_path.read_bytes())
    handoff = json.loads(handoff_path.read_bytes())
    model = json.loads((MODEL / 'model.json').read_bytes())
    groups = {int(g['group_seq']): g for g in model['group']}
    book = read_book(workbook_path, sheets=['Catch', 'Classic PPR'])
    catches = [r for r in records(book, 'Catch', 'Catch') if r['catch_basis'] == decisions['catch_basis']]
    classic = records(book, 'Classic PPR', 'Taxa')
    errors, scope_findings = [], []

    def require(value, code, taxon=None, detail=None):
        if not value:
            errors.append({'code': code, 'taxon': taxon, 'detail': detail})

    require(len(catches) == len({r['taxon'] for r in catches}), 'duplicate_catch_keys')
    require(len(classic) == len({r['taxon'] for r in classic}), 'duplicate_classic_keys')
    catch_by_taxon = {r['taxon']: r for r in catches}
    classic_by_taxon = {r['taxon']: r for r in classic}
    rows = decisions['rows']
    row_by_taxon = {r['taxon']: r for r in rows}
    require(len(rows) == len(row_by_taxon), 'duplicate_mapping_taxa')
    require(set(row_by_taxon) == set(catch_by_taxon), 'catch_universe_mismatch', detail={
        'missing': sorted(set(catch_by_taxon) - set(row_by_taxon)),
        'extra': sorted(set(row_by_taxon) - set(catch_by_taxon))})
    require(decisions['taxon_count'] == len(rows), 'taxon_count_mismatch')
    source_ids = {s['id'] for s in decisions['sources']}
    group_count, zero_candidates, missing_coefficients, unknown_annual = 0, 0, 0, 0
    for r in rows:
        t = r['taxon']
        require(r['model_id'] == MODEL.name and r['unit_id'] == 'LME_022', 'identity', t)
        require(r['proposal_status'] == 'proposed_not_adopted', 'proposal_boundary', t)
        require(r['year'] == decisions['year'] and r['catch_basis'] == decisions['catch_basis'], 'year_basis', t)
        cr = classic_by_taxon.get(t, {})
        observed = catch_by_taxon.get(t, {}).get(decisions['year'])
        coefficient = cr.get('sppr')
        expected_ppr = 0.0 if observed == 0 else (observed * coefficient / 9 if observed is not None and coefficient is not None else None)
        for key, expected in [('catch_tonnes', observed), ('classic_sppr', coefficient), ('tl', cr.get('tl')), ('simple_chain_ppr_tC', expected_ppr)]:
            require(close(r[key], expected), 'source_arithmetic_' + key, t, {'actual': r[key], 'expected': expected})
        require(r['missing_coefficient'] == (coefficient is None), 'missing_coefficient_flag', t)
        require(r['missing_tl'] == (cr.get('tl') is None), 'missing_tl_flag', t)
        missing_coefficients += coefficient is None
        unknown_annual += expected_ppr is None
        ids = [g['group_id'] for g in r['groups']]
        require(len(ids) == len(set(ids)) and set(ids) == set(r['candidate_group_ids']), 'candidate_group_identity', t)
        require(set(ids) <= set(groups), 'unknown_model_group', t)
        weights = [g['weight'] for g in r['groups']]
        require(all(isinstance(w, (float, int)) and math.isfinite(w) and w >= 0 for w in weights), 'invalid_weights', t)
        require(math.isclose(sum(weights), 1, rel_tol=0, abs_tol=1e-12), 'weight_total', t, sum(weights))
        for g in r['groups']:
            canonical = groups[g['group_id']]
            require(g['group_name'] == canonical['group_name'], 'group_id_name', t)
            for field, source in [('source_landings_t_km2_year', 'landings_total'), ('source_discards_t_km2_year', 'discards_total'), ('source_catch_t_km2_year', 'total_removals'), ('source_biomass_t_km2', 'biomass')]:
                require(close(g[field], float(canonical[source])), 'allocation_quantity_' + source, t)
            group_count += 1
            zero_candidates += g['weight'] == 0
        require(all(r[k] in CONFIDENCE for k in ['membership_confidence', 'allocation_confidence', 'overall_confidence']), 'invalid_confidence', t)
        expected_confidence = max([r['membership_confidence'], r['allocation_confidence']], key=CONFIDENCE.index)
        require(r['overall_confidence'] == expected_confidence, 'weaker_component_confidence', t)
        require(set(r['membership_sources']) <= source_ids, 'missing_source_id', t)
        require(bool(r['membership_rationale']) and bool(r['membership_locator']) and bool(r['allocation_rationale']), 'missing_decision_evidence', t)
        if r['allocation_rule'] == 'W1':
            require(len(ids) == 1 and weights == [1.0] and r['allocation_confidence'] == 'High', 'single_group_allocation', t)
        if r['allocation_rule'] == 'W4':
            total = sum(g['source_catch_t_km2_year'] for g in r['groups'])
            require(total > 0, 'catch_proxy_denominator', t)
            require(all(close(g['weight'], g['source_catch_t_km2_year'] / total) for g in r['groups']), 'catch_proxy_weights', t)
            require(r['allocation_confidence'] == 'Medium', 'catch_proxy_confidence', t)
            require(r['assumptions']['allocation_assumed'] and r['assumptions']['fixed_across_years_not_verified'], 'allocation_transfer_flag', t)
        if t in ['Marine fishes not identified', 'Marine finfishes not identified', 'Osteichthyes'] and 49 in ids:
            scope_findings.append({'taxon': t, 'finding': 'SquidAndCuttlefish (49) contradicts the explicit fish-only membership scope; returned to mapping owner for resolution.'})

    total_catch = sum(r['catch_tonnes'] for r in rows if r['catch_tonnes'] is not None)
    total_ppr = sum(r['simple_chain_ppr_tC'] for r in rows if r['simple_chain_ppr_tC'] is not None)
    require(close(total_catch, decisions['totals']['catch_tonnes']), 'catch_denominator')
    require(close(total_ppr, decisions['totals']['simple_chain_ppr_tC']), 'ppr_denominator')
    require(missing_coefficients == decisions['totals']['missing_coefficients'], 'missing_coefficient_count')
    require(unknown_annual == decisions['totals']['unknown_annual_contributions'], 'unknown_annual_count')
    for summary in decisions['confidence_counts_shares']:
        chosen = [r for r in rows if r['overall_confidence'] == summary['confidence']]
        c = sum(r['catch_tonnes'] or 0 for r in chosen)
        p = sum(r['simple_chain_ppr_tC'] or 0 for r in chosen)
        require(len(chosen) == summary['taxa'] and close(c, summary['catch_tonnes']) and close(p, summary['simple_chain_ppr_tC']), 'confidence_summary_totals', summary['confidence'])
        require(close(c / total_catch * 100, summary['catch_percent']) and close(p / total_ppr * 100, summary['ppr_percent']), 'confidence_summary_shares', summary['confidence'])
    for component in ['membership', 'allocation']:
        ledger = defaultdict(lambda: [0, 0.0])
        for r in rows:
            v = ledger[(r[component + '_rule'], r[component + '_confidence'])]
            v[0] += 1
            v[1] += r['simple_chain_ppr_tC'] or 0
        summaries = decisions[component + '_rule_summaries']
        require(set(ledger) == {(s['rule'], s['confidence']) for s in summaries}, component + '_rule_universe')
        for s in summaries:
            n, p = ledger[(s['rule'], s['confidence'])]
            require(n == s['taxa'] and close(p / total_ppr * 100, s['ppr_percent']), component + '_rule_summary', detail=s)
        require(close(sum(s['ppr_percent'] for s in summaries), 100), component + '_rule_total')
    listed_vl = [t for row in decisions['very_low_decisions'] for t in row['taxa']]
    require(Counter(listed_vl) == Counter(r['taxon'] for r in rows if r['overall_confidence'] == 'Very low'), 'very_low_table_exact_coverage')
    for key in ['taxon_count', 'totals', 'confidence_counts_shares', 'membership_rule_summaries', 'allocation_rule_summaries', 'very_low_decisions', 'unresolved']:
        require(handoff.get(key) == decisions.get(key), 'handoff_' + key)
    appendix_check = {'status': 'not_checked_until_mapping_owner_final_confirmation'}
    if args.final:
        import openpyxl
        appendix = MODEL / 'model_validation/taxon_mapping.xlsx'
        input_hashes[str(appendix.relative_to(ROOT)).replace('\\', '/')] = sha(appendix)
        w = openpyxl.load_workbook(appendix, read_only=True, data_only=False)
        try:
            data = list(w['Taxon mapping'].iter_rows(values_only=True))
            header_index = next(n for n, row in enumerate(data) if row and row[0] == 'Taxon name')
            appendix_rows = [r for r in data[header_index + 1:] if r and r[0]]
            appendix_taxa = [r[0] for r in appendix_rows]
            require(Counter(appendix_taxa) == Counter(row_by_taxon.keys()), 'appendix_taxon_universe')
            expected_order = sorted(rows, key=lambda r: (r['simple_chain_ppr_tC'] is None, -(r['simple_chain_ppr_tC'] or 0), r['taxon']))
            require(appendix_taxa == [r['taxon'] for r in expected_order], 'appendix_unrounded_sort')
            for row in appendix_rows:
                r = row_by_taxon[row[0]]
                require(close(row[2], r['catch_tonnes']) and close(row[3], r['simple_chain_ppr_tC']), 'appendix_arithmetic', row[0])
                require(row[5] == r['overall_confidence'], 'appendix_confidence', row[0])
                require(bool(row[6]), 'appendix_missing_reason', row[0])
                require(row[1] in [None, '?'] if r['tl'] is None else close(row[1], r['tl']), 'appendix_tl', row[0])
                displayed = re.findall(r'([^;]+?) \(([-+0-9.eE]+)%\)(?:; |$)', row[4])
                actual_groups = {name.strip(): float(value) for name, value in displayed}
                expected_groups = {g['group_name']: float(format(g['weight'] * 100, '.4g')) for g in r['groups']}
                require(len(displayed) == len(expected_groups) and actual_groups == expected_groups, 'appendix_group_names_rounded_weights', row[0])
            require(sha(appendix) == input_hashes[str(appendix.relative_to(ROOT)).replace('\\', '/')], 'appendix_changed_during_review')
            appendix_check = {'status': 'read_only_rows_checked', 'taxon_count': len(appendix_rows), 'sha256': sha(appendix), 'tl_group_names_and_four_significant_digit_weights_checked': True, 'no_render_or_layout_claim': True}
        finally:
            w.close()
    require(all(sha(p) == input_hashes[str(p.relative_to(ROOT)).replace('\\', '/')] for p in paths), 'input_changed_during_review')
    report = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'review_stage': ('final_hash_verified' if args.final else 'final_decision_hash_verified_appendix_pending' if args.final_decisions else 'draft_checks_waiting_for_mapping_owner_final_hash'),
        'authority': 'Independent read-only QA of the mapping stage; no mapping, source parameter, workbook or publication changes.',
        'input_hashes': input_hashes,
        'narrative_review': {'necessary_diagnostic_or_signed_review_corrections': [], 'assessment': 'Values, strict balance flags, warnings, EE-floor/DET assumptions and current Scotland signed exclusions agree with diagnostic_review.json; comparisons retain differing-configuration and pre-exclusion caveats.'},
        'mapping_checks': {'taxa': len(rows), 'group_allocations': group_count, 'zero_weight_candidates_preserved': zero_candidates, 'catch_tonnes': total_catch, 'simple_chain_ppr_tC': total_ppr, 'missing_coefficients': missing_coefficients, 'unknown_annual_contributions': unknown_annual, 'confidence_counts': dict(Counter(r['overall_confidence'] for r in rows)), 'structural_arithmetic_errors': errors, 'source_scope_findings': scope_findings},
        'appendix_check': appendix_check,
        'biological_candidate_set_review': {'scope': 'All 54 original M9/M10 sets compared by exact canonical group names against retained source definitions, not just numeric ID existence. Stable revised sets rechecked.', 'confirmed_defect_returned_to_mapping_owner': 'SquidAndCuttlefish 49 in three explicitly fish-only broad rows.', 'other_keyed_questions_returned': ['JuvenileSharks 5 omission where broad habitat categories retain adult sharks.', 'Miscellaneous marine crustaceans is broader than Decapoda; account for source-listed krill, small sediment crustaceans and Balanus, or document provider exclusions.', 'Clupeidae rationale must distinguish anchovy as a non-clupeid co-member of mixed group48.'], 'owner_resolution_verified': ['Fish residuals exclude49 and dedicated cartilaginous groups5-12. Read retained reporting-scope evidence: exact LME022 source hash and keys100039/100139/100239/100339 match; historical FAO Osteichthyes/39 scope supports shark/ray exclusions while mixed pool46 is disclosed.', 'Miscellaneous marine crustaceans now includes51,52,54,55,56,58,59,60,61. Malacostraca includes60 and excludes non-malacostracan copepods/barnacles.', 'Clupeidae now explicitly identifies anchovy/Maurolicus as non-clupeid co-members of the mixed group48 composition proxy.'], 'no_additional_cross_domain_inclusion_found': True},
        'scotland_appendix_comparison': {'sha256': 'c3cbe2fd6ba79229dbfb446ab196a5f39b00eed3705c3540da56e3dc8b6a091c', 'taxa': 384, 'confidence_counts': {'High': 99, 'Medium': 160, 'Low': 3, 'Very low': 110, 'Unresolved': 12}, 'very_low_ppr_percent': 3.8482612919683215, 'unresolved_ppr_percent': 0.0033504549607603724, 'narrative_rounding_correct': True},
        'source_scope_review_boundary': 'Compared retained source findings and explicit candidate rationales; no independent taxon reassignment or second research stage. Mapping owner resolves keyed source conflicts.',
        'passed': not errors and not scope_findings,
    }
    target = RUN / 'qa/independent_review.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'stage': report['review_stage'], 'passed': report['passed'], 'errors': errors, 'scope_findings': scope_findings, 'taxa': len(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
