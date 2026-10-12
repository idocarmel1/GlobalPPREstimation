"""Refresh candidate-independent inputs without revising authored allocations."""
import copy
import json
import math

from tools.project_core.calculations.regional import set_setting, set_result_hash
from tools.project_core.workbooks.workbooks import digest_tables, finite, input_hash, overview, records


STATE_FIELD = 'candidate_arithmetic_state'
INDEPENDENT_SETTINGS = ('catch_basis', 'taxon_detail_year', 'unidentified_treatment')


def independent_dependencies(book):
    settings = overview(book)
    return {**{sheet: digest_tables(book.get(sheet, {})) for sheet in ('Catch', 'Classic PPR', 'NPP')},
            'settings': digest_tables([(key, settings[key]) for key in INDEPENDENT_SETTINGS if key in settings])}


def candidate_arithmetic_state(book):
    value = overview(book).get(STATE_FIELD)
    try:
        state = json.loads(value) if isinstance(value, str) else value
    except (ValueError, TypeError):
        return {}
    return state if isinstance(state, dict) and state.get('schema_version') == 1 else {}


def _mapping_problem(book):
    expected = overview(book).get('results_model_id')
    taxa = {row.get('taxon') for row in records(book, 'Catch', 'Catch')}
    groups = {row.get('group_name') for row in records(book, 'Selected model groups', 'Groups')}
    grouped = {}
    seen = set()
    for row in records(book, 'PPR', 'Matching'):
        if row.get('model_id') != expected:
            return 'retained matching belongs to another model'
        if not row.get('group'):
            continue
        pair = row.get('taxon'), row['group']
        if pair in seen or pair[0] not in taxa or pair[1] not in groups:
            return 'retained matching has duplicate or unknown taxon/group identities'
        seen.add(pair)
        weight = row.get('weight')
        if not finite(weight) or weight < 0:
            return 'retained matching contains invalid weights'
        grouped.setdefault(pair[0], []).append(weight)
    if any(not math.isclose(math.fsum(weights), 1, rel_tol=0, abs_tol=1e-9) for weights in grouped.values()):
        return 'retained mapping weights do not sum to one'
    return None


def prepare_candidate_book(saved_book, current_book):
    """Copy current independent inputs, preserving candidate choices and evidence.

    A pending allocation remains pending on later launches while the authored
    matching is unchanged. Copying new Catch rows is not a matching review.
    """
    prepared = copy.deepcopy(saved_book)
    prior_state = candidate_arithmetic_state(saved_book)
    current = independent_dependencies(current_book)
    saved = independent_dependencies(saved_book)
    matching = digest_tables(saved_book.get('PPR', {}).get('Matching', ([], [])))
    prior_taxa = {row.get('taxon') for row in records(saved_book, 'Catch', 'Catch')}
    current_taxa = {row.get('taxon') for row in records(current_book, 'Catch', 'Catch')}
    pending = prior_state.get('pending_reason') if prior_state.get('matching_sha256') == matching else None
    if not pending and prior_taxa != current_taxa:
        pending = 'Catch taxon set changed; review the retained candidate matching before calculating annual PPR'
    if not pending and saved['Catch'] != current['Catch'] and any(
            row.get('group') and row.get('weight') not in (0, 1) for row in records(saved_book, 'PPR', 'Matching')):
        pending = 'Catch changed with split allocation weights; review the retained candidate allocation assumptions before calculating annual PPR'
    for sheet in ('Catch', 'Classic PPR', 'NPP'):
        if sheet in current_book:
            prepared[sheet] = copy.deepcopy(current_book[sheet])
        else:
            prepared.pop(sheet, None)
    settings = overview(current_book)
    entries = prepared['Overview']['Settings'][1]
    for key in INDEPENDENT_SETTINGS:
        if key in settings:
            set_setting(prepared, key, copy.deepcopy(settings[key]))
        else:
            entries[:] = [row for row in entries if row[0] != key]
    # Independent ratios travel with their current saved Classic/NPP series.
    ratios = current_book.get('PPR–NPP', {}).get('Ratios')
    if ratios:
        old = prepared.get('PPR–NPP', {}).get('Ratios', (ratios[0], []))[1]
        prepared.setdefault('PPR–NPP', {})['Ratios'] = (
            copy.deepcopy(ratios[0]), copy.deepcopy([row for row in ratios[1] if not row[0]] + [row for row in old if row[0]]))
    pending = pending or _mapping_problem(prepared)
    state = {'schema_version': 1, 'current_dependencies': current,
             'matching_sha256': matching, 'pending_reason': pending}
    set_setting(prepared, STATE_FIELD, json.dumps(state, ensure_ascii=False, sort_keys=True))
    changed = saved != current or state != prior_state
    return {'book': prepared, 'changed': changed, 'pending_reason': pending, 'state': state}


def suppress_candidate_arithmetic(book, reason):
    """Retain coefficients and authored tables, removing unsafe model arithmetic."""
    tables = book.setdefault('PPR', {})
    for name in ('Annual', 'Taxon SPPR', 'Taxon PPR inspected year'):
        if name in tables:
            tables[name] = (tables[name][0], [])
    ratios = book.get('PPR–NPP', {}).get('Ratios')
    if ratios:
        book['PPR–NPP']['Ratios'] = (ratios[0], [row for row in ratios[1] if not row[0]])
    set_setting(book, 'calculation_status', 'Candidate arithmetic unavailable: ' + str(reason))
    set_setting(book, 'calculation_input_sha256', input_hash(book))
    set_result_hash(book)
