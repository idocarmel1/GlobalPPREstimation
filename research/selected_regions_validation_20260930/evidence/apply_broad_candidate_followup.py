"""Coordinator-owned current-state mapping followup for California/Bay of Bengal."""
import argparse
import copy
import json
import math
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W
import regional as R
from bounded_workbook_update import update_blocks

EXPECTED = {'LME_003': 'c65835207ecd6a476befa5158a0292bd8ef4370074974f08d9ac9bc425a639b8',
            'LME_034': '4d7e5eb6e2b973e837a5c6f2e55016c819a6dec54d263584187b4c2fd0530f27'}
FISH = 'Marine fishes not identified'
PELAGIC = 'Marine pelagic fishes not identified'


def readj(p):
    return json.loads(p.read_text(encoding='utf-8'))


def writej(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def table_rows(book, sheet, table, rows):
    h = book[sheet][table][0]
    book[sheet][table] = (h, [[W.clean(r.get(k)) for k in h] for r in rows])


def replace_keyed(rows, replacements):
    done, output = set(), []
    for row in rows:
        taxon = row.get('taxon')
        if taxon not in replacements:
            output.append(row)
        elif taxon not in done:
            output.extend(replacements[taxon])
            done.add(taxon)
    assert done == set(replacements), ('Missing target keys', set(replacements) - done)
    return output


def run(unit):
    p = ROOT / 'regions' / unit / (unit + '.xlsx')
    assert W.sha(p) == EXPECTED[unit], 'Regional release changed; re-review the expected-old identity'
    before = W.read_book(p)
    b = copy.deepcopy(before)
    o = W.overview(b)
    assert W.input_hash(b) == o['calculation_input_sha256']
    assert R.result_hash(b) == o['calculation_result_sha256']
    mid = o['selected_model_id']
    ev = p.parent / 'validation_reports' / mid
    audit_path = ev / ('taxon_audit.json' if unit == 'LME_003' else 'adopted_taxon_audit.json')
    audit = readj(audit_path)
    rows = audit['rows' if unit == 'LME_003' else 'records']
    by = {r['taxon']: r for r in rows}
    proposed = next(r for r in readj(HERE / 'work/qa_residual_fish_scope/broad_scope_candidate_proposals.json') if r['unit_id'] == unit)
    assert proposed['model_id'] == mid
    assert W.sha(p.parent / o['model_path']) == proposed['source_model_sha256']
    for source in proposed['source_paths_and_hashes']:
        assert W.sha(ROOT / source['path']) == source['sha256'], source['path']
    groups = {int(g.get('seq', g.get('group_seq'))): g for g in W.records(b, 'Selected model groups', 'Groups')}
    broad = [c['seq'] for c in proposed['complete_broad_candidate_vector']]
    sets = ({t: broad for t in [FISH, 'Marine finfishes not identified', 'Actinopterygii', 'Osteichthyes']}
            if unit == 'LME_003' else {FISH: broad, PELAGIC: proposed['pelagic_candidate_ids']})
    evidence = 'validation_reports/' + mid + '/broad_candidate_followup.json'
    scratch = HERE / 'work/coordinator_broad_followup' / unit
    scratch.mkdir(parents=True, exist_ok=True)
    backup_paths = [p, audit_path, ev / 'coordination_handoff.json']
    if unit == 'LME_003':
        backup_paths.append(ev / 'allocation_evidence.json')
    for source in backup_paths:
        destination = scratch / source.name
        assert not destination.exists(), 'Do not overwrite first followup baseline'
        shutil.copy2(source, destination)
    source_yield = {c['seq']: c['source_yield'] for c in proposed['complete_broad_candidate_vector']}
    if unit == 'LME_003':
        provenance = readj(ev / 'source_catch_provenance.json')
        assert W.sha(ROOT / provenance['source']) == provenance['sha256']
        yields = {r['seq']: r for r in provenance['records']}
        for seq, value in source_yield.items():
            assert value == yields[seq]['author_Yield'] == groups[seq]['catch']
        locations = {c['seq']: c for a in rows for c in a['source_locators']}
    else:
        yields = None
        for seq, value in source_yield.items():
            assert value == groups[seq]['catch']
    changes, matching, ledger_updates = [], {}, {}
    for taxon, ids in sets.items():
        a = by[taxon]
        previous = copy.deepcopy(a)
        values = [float(source_yield[g]) for g in ids]
        assert all(W.finite(v) and v >= 0 for v in values)
        denominator = math.fsum(values)
        assert denominator > 0
        weights = [v / denominator for v in values]
        assert math.isclose(math.fsum(weights), 1, abs_tol=1e-14)
        if unit == 'LME_003':
            membership = ('The broad bony-fish label includes all 40 source-listed bony-bearing groups 15–17, 20–48 and 50–57, '
                          'including mesopelagics, named forage fish, albacore, salmon and juvenile stages. The provider medium-demersal '
                          'functional bin is not an exhaustive taxonomic definition. Benthic fish16 remains eligible through its actual '
                          'bony members despite a pooled ratfish component; dedicated Dogfish49, Skates58 and Sharks59 are excluded. '
                          'Unobserved residual composition, unrepresented taxa and mixed-pool transfer keep membership Very low.')
            allocation = ('Complete author total Yield proportions (denominator ' + repr(denominator) +
                          ' t/km²/year) are an assumed fixed caught-composition proxy across 1950–2019 and all catch bases. '
                          'All genuine source-zero candidates remain in the ledger; zeros are model uncaught assumptions, not observed absence. Allocation W4 Medium.')
            a.update(candidate_ids=ids, weights={str(g): w for g, w in zip(ids, weights)},
                     membership_reason=membership, allocation_reason=allocation,
                     source_locators=[locations[g] for g in ids],
                     excluded_candidates=[x for x in a['excluded_candidates'] if x['seq'] not in ids],
                     zero_weight_candidates=[g for g, v in zip(ids, values) if v == 0],
                     assignments=[{'seq': g, 'group': groups[g]['group_name'], 'weight': w} for g, w in zip(ids, weights)])
            a['reason'] = membership + ' ' + allocation
            a['mapping_display'] = '; '.join(groups[g]['group_name'] + f' ({w * 100:.4f}%)' for g, w in zip(ids, weights))
            candidates = [{'taxon': taxon, 'seq': g, 'group': groups[g]['group_name'], 'weight': w,
                           'source_catch': values[i], 'source_catch_provenance': yields[g]['source_catch_provenance'],
                           'accepted_biomass': groups[g]['biomass'], 'rule': 'W4', 'allocation_confidence': 'Medium',
                           'membership_confidence': 'Very low', 'assumed': True, 'limitations': allocation}
                          for i, (g, w) in enumerate(zip(ids, weights))]
            ledger_updates[taxon] = candidates
        else:
            membership = ('All source-listed named and residual bony-fish pools compatible with this broad reporting scope are retained. '
                          'Separately reported tuna/billfish categories do not establish their absence from unidentified fish. '
                          'The provider functional bin does not override actual A1.3 membership. '
                          + ('The pelagic approximation includes named tunas/billfish3,46–48 and source-zero small bathypelagics7; '
                             'predominantly reef/demersal commercial piscivores21/34 remain outside this pelagic set. ' if taxon == PELAGIC else
                             'Named tunas/billfish3,46–48, coastal scombrids4, small bathypelagics7, Hilsa29 and Indian mackerel30 are included. ')
                          + 'Dedicated elasmobranchs1/2 are outside FAO Osteichthyes scope. Maldives shelf9–14 remain excluded on source '
                          'p7–9/A1.2 geography, without excluding region1 open water. Mixed large-piscivore18/31 pools retain their actual '
                          'bony members despite Pristis. Unmeasured composition and full-guild transfer keep membership Very low.')
            allocation = ('Complete A2.1 1978 landings plus discards normalized to the common whole-study-area denominator are used '
                          'as W4 Medium pooled catch weights. Sum=' + repr(denominator) +
                          ' t/km²/year. Source-zero7 is retained. The proportions are assumed fixed across 1950–2019, geographic fisheries '
                          'and all catch bases; they are not observed constituent fractions. Accepted biological parameters remain unchanged.')
            template = a['proposed_groups'][0]
            candidates = []
            for g, w, value in zip(ids, weights, values):
                c = copy.deepcopy(template)
                c.update(group=groups[g]['group_name'], seq=g, weight=w,
                         source_printed_catch_density=value, native_model_catch_density=value,
                         loaded_model_catch_density=value, source_caught_mass_t=value * c['common_area_km2'],
                         source_biomass_density=groups[g]['biomass'], zero_candidate=value == 0)
                candidates.append(c)
            exclusions = [x for x in a['candidate_exclusions'] if x['seq'] not in ids]
            for x in exclusions:
                if x['seq'] in [1, 2]:
                    x['reason'] = 'Dedicated cartilaginous group is outside the verified ISSCAAP39/FAO Osteichthyes target scope.'
                elif x['seq'] not in range(9, 15) and x['seq'] not in [21, 34]:
                    x['reason'] = 'Source group has no compatible landed bony fish for this reporting scope; actual A1.3 definition reviewed. Fish eggs alone do not establish a landed-fish pool.'
            a.update(proposed_groups=candidates, candidate_inclusion_rationale=membership, candidate_exclusions=exclusions,
                     allocation_total=denominator, reason=membership + ' ' + allocation,
                     readable_reason=membership + ' ' + allocation)
            a['catch_attempt'].update(candidate_values=[{'group': groups[g]['group_name'], 'catch': v} for g, v in zip(ids, values)], total=denominator)
        a['broad_candidate_followup'] = 'broad_candidate_followup.json'
        old_matching = [r for r in W.records(before, 'PPR', 'Matching') if r['taxon'] == taxon]
        assert old_matching and all(r['confidence'].lower() == 'very low' for r in old_matching)
        matching[taxon] = [{'model_id': mid, 'taxon': taxon, 'group': groups[g]['group_name'], 'weight': w,
                            'confidence': old_matching[0]['confidence'], 'evidence': evidence, 'explanation': a['reason']}
                           for g, w in zip(ids, weights)]
        changes.append({'taxon': taxon, 'previous_audit': previous, 'before_matching': old_matching,
                        'after_matching': matching[taxon], 'candidate_ids': ids, 'source_values': values,
                        'denominator': denominator, 'weights': weights, 'zero_candidates': [g for g, v in zip(ids, values) if v == 0]})
    if unit == 'LME_003':
        a = by[PELAGIC]
        before_pelagic = copy.deepcopy(a)
        note = (' Sablefish/lingcod eligibility here refers to the pelagic juvenile Roundfish31, whose source catch is genuinely zero. '
                'Adult Sablefish45 remains outside the pelagic approximation on documented adult demersal habitat; the pelagic candidate set and weights are unchanged.')
        a['membership_reason'] += note
        a['reason'] = a['membership_reason'] + ' ' + a['allocation_reason']
        a['broad_candidate_followup'] = 'broad_candidate_followup.json'
        for r in W.records(b, 'PPR', 'Matching'):
            if r['taxon'] == PELAGIC:
                matching.setdefault(PELAGIC, []).append({**r, 'explanation': a['reason'], 'evidence': evidence})
        ledger = replace_keyed(readj(ev / 'allocation_evidence.json'), ledger_updates)
        table_rows(b, 'PPR', 'Validation allocation candidates', ledger)
    table_rows(b, 'PPR', 'Matching', replace_keyed(W.records(b, 'PPR', 'Matching'), matching))
    reviews = W.records(b, 'PPR', 'Mapping review')
    for r in reviews:
        if r['taxon'] not in sets:
            continue
        a = by[r['taxon']]
        r['membership_evidence'] = evidence
        if unit == 'LME_003':
            r['allocation_evidence'] = a['allocation_reason']
        else:
            r.update(candidate_selection=a['proposed_groups'], candidate_exclusions=a['candidate_exclusions'],
                     allocation_calculation=a['catch_attempt'], reason=a['reason'],
                     allocation_evidence='A2.1p46 complete source catch; ' + evidence)
    table_rows(b, 'PPR', 'Mapping review', reviews)
    if unit == 'LME_034':
        allocation_replacements = {}
        existing = W.records(b, 'PPR', 'Allocation assumptions')
        for taxon in sets:
            template = next(r for r in existing if r['taxon'] == taxon)
            a = by[taxon]
            allocation_replacements[taxon] = []
            for c in a['proposed_groups']:
                r = copy.deepcopy(template)
                r.update(group=c['group'], seq=c['seq'],
                         source_printed_catch_density=c['loaded_model_catch_density'],
                         source_model_catch_density=c['loaded_model_catch_density'],
                         loaded_catch_density=c['loaded_model_catch_density'],
                         candidate_total=a['allocation_total'], weight=c['weight'], zero_candidate=c['zero_candidate'],
                         candidates=[c['group'] for c in a['proposed_groups']],
                         candidate_inclusion=a['candidate_inclusion_rationale'], candidate_exclusions=a['candidate_exclusions'],
                         evidence=evidence, review_run_id='complete_broad_candidates_20260930')
                for key in ['source_catch', 'catch', 'loaded_model_catch_density']:
                    if key in r:
                        r[key] = c['loaded_model_catch_density']
                allocation_replacements[taxon].append(r)
        table_rows(b, 'PPR', 'Allocation assumptions', replace_keyed(existing, allocation_replacements))
    R.recalculate(b, p)
    # Independent reference and its legitimate uncertainty bounds are protected.
    b['Classic PPR'] = copy.deepcopy(before['Classic PPR'])
    precision_preservation = {}
    for tn, nkey in [('Taxon SPPR', 4), ('Taxon PPR inspected year', 6)]:
        keyed = {tuple(r[:nkey]): r for r in before['PPR'][tn][1]}
        restored, max_relative = 0, 0.0
        for i, row in enumerate(b['PPR'][tn][1]):
            if row[1] in sets:
                continue
            saved = keyed[tuple(row[:nkey])]
            for actual, wanted in zip(row, saved):
                if actual == wanted:
                    continue
                assert W.finite(actual) and W.finite(wanted) and math.isclose(actual, wanted, rel_tol=1e-14, abs_tol=1e-6), (tn, row[:nkey], actual, wanted)
                max_relative = max(max_relative, abs(actual - wanted) / max(abs(wanted), 1))
            if row != saved:
                b['PPR'][tn][1][i] = copy.deepcopy(saved)
                restored += 1
        precision_preservation[tn] = {'retained_old_unrelated_rows': restored, 'max_relative_recalculation_tail': max_relative}
    h, ratios = b['PPR–NPP']['Ratios']
    b['PPR–NPP']['Ratios'] = (h, [copy.deepcopy(r) for r in before['PPR–NPP']['Ratios'][1] if not r[0]] + [r for r in ratios if r[0]])
    R.set_setting(b, 'calculation_status', o['calculation_status'])
    R.set_result_hash(b)
    for s in ['Catch', 'Classic PPR', 'Selected model groups', 'NPP', 'Diagnostics']:
        assert b[s] == before[s], ('Protected tables', s)
    unchanged = lambda book: [r for r in W.records(book, 'PPR', 'Matching') if r['taxon'] not in matching]
    assert unchanged(b) == unchanged(before)
    touched = update_blocks(p, before, b, expected_sha256=EXPECTED[unit])
    W.validate_region(b, p)
    assert W.input_hash(b) == W.overview(b)['calculation_input_sha256']
    assert R.result_hash(b) == W.overview(b)['calculation_result_sha256']
    writej(audit_path, audit)
    if unit == 'LME_003':
        writej(ev / 'allocation_evidence.json', ledger)
    receipt = {'unit_id': unit, 'model_id': mid, 'status': 'Mapping and dependent arithmetic adopted; Office and handoff refresh pending',
               'before_workbook_sha256': EXPECTED[unit], 'after_workbook_sha256': W.sha(p),
               'source_proposal': proposed, 'changes': changes, 'changed_package_parts': touched,
               'protected_tables_exact': ['Catch', 'Classic PPR', 'Selected model groups', 'NPP', 'Diagnostics'],
               'current_input_sha256': W.overview(b)['calculation_input_sha256'],
               'current_result_sha256': W.overview(b)['calculation_result_sha256'],
               'scientific_solver_rerun': False,
               'independent_classic_and_valid_bounds_preserved': True,
               'unrelated_derived_precision_preservation': precision_preservation,
               'review_limits': 'Evidence-supported candidate correction; composition remains unmeasured and Very low. All prior scientific limitations remain.'}
    if unit == 'LME_003':
        receipt['pelagic_prose_only'] = {'before': before_pelagic, 'after': by[PELAGIC], 'weights_unchanged': True}
    writej(ev / 'broad_candidate_followup.json', receipt)
    print(json.dumps({'unit': unit, 'sha256': W.sha(p), 'taxa_numerically_changed': list(sets), 'protected_exact': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('unit', choices=EXPECTED)
    run(parser.parse_args().unit)
