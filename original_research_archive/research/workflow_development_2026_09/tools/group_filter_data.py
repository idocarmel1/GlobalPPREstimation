"""Prepare embedded group filters from stored source values, without a solver."""
from copy import deepcopy

from ppr_scopes import SCOPES, finite


def build_group_data(groups, source_scopes, taxa, mappings, provenance=None):
    """Keep authoritative names, full stored precision, and exact Final weights."""
    names = [group['group_name'] for group in groups]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate group identity in source workbook')
    indexes = {name: index for index, name in enumerate(names)}
    metadata = []
    for group in groups:
        ge, ee = finite(group.get('ge')), finite(group.get('ee'))
        metadata.append({'id': group['group_name'], 'name': group['group_name'],
                         'te': finite(ge * ee) if ge is not None and ee is not None else None,
                         'tl': finite(group.get('tl'))})
    methods = list(dict.fromkeys(method for scope in SCOPES
                                for method in source_scopes.get(scope, ([], {}))[0]))
    scopes = {}
    for scope in SCOPES:
        source_methods, by_group = source_scopes.get(scope, ([], {}))
        if set(by_group) - indexes.keys():
            raise ValueError(f'Unknown SPPR group in {scope}')
        matrix = []
        for name in names:
            values = dict(zip(source_methods, by_group.get(name, [])))
            matrix.append([finite(values.get(method)) for method in methods])
        scopes[scope] = matrix
    weights = []
    for taxon in taxa:
        pairs = []
        for name, weight in mappings.get(taxon, []):
            if name not in indexes:
                raise ValueError(f'Unknown mapped group: {name}')
            if finite(weight) is None or weight < 0:
                raise ValueError(f'Invalid mapping weight: {taxon}/{name}')
            pairs.append([indexes[name], weight])
        weights.append(pairs)
    return {'groups': metadata, 'methods': methods, 'scopes': scopes, 'mappings': weights,
            'te_definition': 'Stored source-group GE × EE; no EE repair or solver recalculation.',
            'provenance': {**(provenance or {}), 'groups_sheet': 'groups_df',
                           'sppr_sheets': ['sppr_' + scope for scope in SCOPES],
                           'mapping_sheet': 'Final mappings',
                           'precision': 'Source cell values and exact final weights; no additional rounding.'}}


def annual_group_inputs(network_unit):
    """Copy taxon vectors once, retaining their own source-year coordinate system."""
    if not any(model.get('verified') and model.get('group_data')
               for model in network_unit.get('models', [])):
        return None
    years, taxa = network_unit['years'], network_unit['taxa']
    if len(years) != len(set(years)) or len(taxa) != len(set(taxa)):
        raise ValueError('Duplicate group-input year or taxon')
    fields = ('years', 'taxa', 'full_precision_catch', 'catch', 'landings', 'discards',
              'simple_sppr', 'unidentified', 'catch_basis_policy', 'catch_accounting')
    result = {key: deepcopy(network_unit[key]) for key in fields if key in network_unit}
    for field in ('full_precision_catch', 'catch', 'landings', 'discards'):
        if field in result and (len(result[field]) != len(taxa)
                               or any(len(row) != len(years) for row in result[field])):
            raise ValueError(f'Group-input {field} dimensions do not agree')
    if 'simple_sppr' in result and len(result['simple_sppr']) != len(taxa):
        raise ValueError('Group-input simple SPPR dimensions do not agree')
    return result
