"""Source routing, missingness and identity survive the generic JSON loader."""
import copy
import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ModelData import ModelData, get_DC


def group(seq, role, **fields):
    value = dict(group_seq=str(seq), group_name=f"group_{seq}", pp=str(role),
                 biomass="1", pb="2", qb="4", ee="0.5", other_mort="-9999",
                 gs="0.2", export="0", biomass_accum="0", immigration="0",
                 emigration="0", tl="-9999", diet_descr=None)
    value.update(fields)
    return value


def source():
    return {"group": [
        group(1, 0, tl="3.25", diet_imp="0", diet_descr={"diet": [
            {"prey_seq": "2", "proportion": "0.8", "detritus_fate": "-9999"},
            {"prey_seq": "3", "proportion": "0.2", "detritus_fate": "0.6"},
            {"prey_seq": "4", "proportion": "0", "detritus_fate": "0.4"}]}),
        group(2, 1, tl="1", detritus_fate_by_pool={"3": "0.45", "4": "0.55"}),
        group(3, 2, tl="1", detritus_fate_by_pool={"3": "0", "4": "0"}),
        group(4, 2, tl="1", detritus_fate_by_pool={"3": "0", "4": "0"}),
    ]}


def load(tmp_path, data, relative="model.json"):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    before = path.read_bytes()
    model = ModelData(str(path))
    assert path.read_bytes() == before
    assert model.data_json == data
    return model


def test_separate_pool_mapping_routes_nonfeeding_producer(tmp_path):
    model = load(tmp_path, source())
    assert model.det_fate.loc[2, [3, 4]].tolist() == [0.45, 0.55]
    assert model.det_fate.loc[1, [3, 4]].tolist() == [0.6, 0.4]


@pytest.mark.parametrize("routing,expected", [
    ({"3": "0", "4": "0"}, [0., 0.]),
    ({"3": 0.25, "4": 0.75}, [0.25, 0.75]),
])
def test_explicit_detritus_routing_is_not_replaced_by_identity(tmp_path, routing, expected):
    data = source()
    data["group"][2]["detritus_fate_by_pool"] = routing
    model = load(tmp_path, data)
    assert model.det_fate.loc[3, [3, 4]].tolist() == expected


def test_separate_pool_values_take_precedence_over_embedded_values(tmp_path):
    data = source()
    data["group"][0]["detritus_fate_by_pool"] = {"3": "0", "4": "1"}
    model = load(tmp_path, data)
    assert model.det_fate.loc[1, [3, 4]].tolist() == [0., 1.]


def test_embedded_detritus_zero_is_also_explicit(tmp_path):
    data = source()
    data["group"][2].pop("detritus_fate_by_pool")
    data["group"][2]["diet_descr"] = {"diet": {
        "prey_seq": "3", "proportion": "0", "detritus_fate": "0"}}
    model = load(tmp_path, data)
    assert model.det_fate.loc[3, [3, 4]].tolist() == [0., 0.]


def test_only_missing_legacy_detritus_rows_get_identity(tmp_path):
    data = source()
    data["group"][2].pop("detritus_fate_by_pool")
    model = load(tmp_path, data)
    assert model.det_fate.loc[3, [3, 4]].tolist() == [1., 0.]
    assert model.det_fate.loc[4, [3, 4]].tolist() == [0., 0.]


def single_pool_source(*, explicit):
    data = {"group": [group(1, 0, diet_imp="0", diet_descr={"diet": {
        "prey_seq": "2", "proportion": "1", "detritus_fate": "-9999"}}),
        group(2, 1), group(3, 2)]}
    if explicit:
        for item in data["group"]:
            item["detritus_fate_by_pool"] = {"3": "0"}
    return data


def test_explicit_zero_single_pool_routing_is_open_export(tmp_path):
    model = load(tmp_path, single_pool_source(explicit=True))
    assert model.det_fate.loc[[1, 2, 3], 3].tolist() == [0., 0., 0.]
    with pytest.warns(RuntimeWarning, match="export"):
        ModelData.validate_det_fate(model.det_fate, model.groups_data)


def test_missing_legacy_single_pool_routing_retains_closed_default(tmp_path):
    model = load(tmp_path, single_pool_source(explicit=False))
    assert model.det_fate.loc[[1, 2, 3], 3].tolist() == [1., 1., 1.]


@pytest.mark.parametrize("unknown", [None, "", "-9999", -9999])
def test_explicit_unknown_routing_stays_unknown_and_cannot_validate(tmp_path, unknown):
    data = source()
    data["group"][1]["detritus_fate_by_pool"]["3"] = unknown
    model = load(tmp_path, data)
    assert np.isnan(model.det_fate.loc[2, 3])
    with pytest.raises(ValueError, match="missing|nonfinite|finite"):
        ModelData.validate_det_fate(model.det_fate, model.groups_data)


@pytest.mark.parametrize("unknown", [None, "", "-9999", -9999, "absent"])
def test_missing_nonfeeding_imports_are_structural_zero_but_consumer_unknown_is_kept(tmp_path, unknown):
    data = source()
    for item in data["group"]:
        item.pop("diet_imp", None)
        if unknown != "absent":
            item["diet_imp"] = unknown
    model = load(tmp_path, data)
    assert np.isnan(model.DC.loc[1, 5])
    assert model.DC.loc[[2, 3, 4, 5], 5].tolist() == [0., 0., 0., 0.]
    with pytest.raises(ValueError, match="missing|nonfinite|finite"):
        ModelData.validate_DC(model.DC, model.groups_data, normalize=False)


def test_known_imports_and_explicit_unknown_consumer_prey_are_not_overwritten(tmp_path):
    data = source()
    data["group"][1]["diet_imp"] = "0.25"
    data["group"][0]["diet_descr"]["diet"][0]["proportion"] = "-9999"
    model = load(tmp_path, data)
    assert model.DC.loc[2, 5] == 0.25
    assert np.isnan(model.DC.loc[1, 2])


def test_source_trophic_levels_and_unknowns_survive_loading(tmp_path):
    data = source()
    data["group"][3]["tl"] = -9999
    model = load(tmp_path, data)
    assert model.groups_data.loc[1, "tl"] == 3.25
    assert model.groups_data.loc[2, "tl"] == 1.
    assert np.isnan(model.groups_data.loc[4, "tl"])


@pytest.mark.parametrize("metadata,relative,lme,country", [
    ({"metadata": {"LME": "22 North Sea", "country": "UK"}}, "model.json", 22, "UK"),
    ({"source_metadata": {"lme": "27", "country": "Mauritania"}}, "model.json", 27, "Mauritania"),
    ({"metadata": {"unit_id": "LME_026"}}, "model.json", 26, None),
    ({}, "regions/LME/LME_022/papers/P/models/M/model.json", 22, None),
    ({}, "457_457_North_Sea_(1991).json", None, None),
    ({"metadata": {"LME": "EEZ_939 Israel Mediterranean"}}, "model.json", None, None),
])
def test_location_identity_uses_actual_metadata_or_canonical_region(tmp_path, metadata, relative, lme, country):
    data = source()
    data.update(metadata)
    model = load(tmp_path, data, relative)
    assert np.isnan(model.lme) if lme is None else model.lme == lme
    assert np.isnan(model.model_country) if country is None else model.model_country == country


def test_legacy_dictionary_diet_reader_has_same_source_preservation():
    data = source()
    before = copy.deepcopy(data)
    dc, fate = get_DC(42, {"42": data})
    assert fate.loc[2, [3, 4]].tolist() == [0.45, 0.55]
    assert dc.loc[1, [2, 3]].tolist() == [0.8, 0.2]
    assert data == before


def test_standalone_legacy_diet_records_need_no_group_role_metadata():
    data = source()
    for item in data['group']:
        item.pop('pp')
    dc, fate = get_DC(42, {'42': data})
    assert dc.loc[1, 2] == 0.8
    assert fate.loc[2, 3] == 0.45


def test_embedded_unknown_detritus_target_remains_unknown(tmp_path):
    data = source()
    data['group'][2].pop('detritus_fate_by_pool')
    data['group'][2]['diet_descr'] = {'diet': {
        'prey_seq': '3', 'proportion': '0', 'detritus_fate': '-9999'}}
    model = load(tmp_path, data)
    assert np.isnan(model.det_fate.loc[3, 3])
    with pytest.raises(ValueError, match='missing|nonfinite'):
        ModelData.validate_det_fate(model.det_fate, model.groups_data)


def test_source_detritus_catch_is_not_silently_zeroed(tmp_path):
    data = source()
    data['group'][2]['export'] = '0.75'
    model = load(tmp_path, data)
    assert model.groups_data.loc[3, 'catch'] == 0.75


def fleet_source():
    data = source()
    for item in data['group']:
        item['discards_by_fleet'] = {'Fleet A': '0', 'Fleet B': '0'}
        item['landings_by_fleet'] = {'Fleet A': '0', 'Fleet B': '0'}
    data['group'][0].update(export='10',
        discards_by_fleet={'Fleet A': '3', 'Fleet B': '1'},
        landings_by_fleet={'Fleet A': '6', 'Fleet B': '0'})
    data['published_companions'] = {'Rpath_parameter_model.csv': {'rows': [
        ['Group', 'Type', 'group_3', 'group_4'],
        ['Fleet A', '3.0', '0.25', '0.5'],
        ['Fleet B', '3', '0', '1'],
    ]}}
    return data


def test_multiple_fleets_route_absolute_returns_once_and_preserve_catch(tmp_path):
    model = load(tmp_path, fleet_source())
    assert model.discard_returns.loc[1, [3, 4]].tolist() == [0.75, 2.5]
    assert model.discard_returns.loc[[2, 3, 4]].to_numpy().sum() == 0.
    assert model.groups_data.loc[1, 'catch'] == 10.
    assert model.discard_returns_metadata['status'] == 'complete'
    assert model.discard_returns_metadata['total_discards'] == 4.
    assert model.discard_returns_metadata['total_returned'] == 3.25
    assert model.discard_returns_metadata['external_discard_remainder'] == 0.75


@pytest.mark.parametrize('fractions', [('-0.1', '1'), ('1.1', '0'), ('0.7', '0.7')])
def test_invalid_fleet_fractions_are_rejected(tmp_path, fractions):
    data = fleet_source()
    data['published_companions']['Rpath_parameter_model.csv']['rows'][1][2:] = fractions
    with pytest.raises(ValueError, match='discard|fleet'):
        load(tmp_path, data)


@pytest.mark.parametrize('incomplete', ['no_companion', 'missing_fleet', 'missing_pool', 'unknown_fraction', 'unknown_amount'])
def test_nonzero_discard_unknowns_are_explicitly_incomplete(tmp_path, incomplete):
    data = fleet_source()
    rows = data['published_companions']['Rpath_parameter_model.csv']['rows']
    if incomplete == 'no_companion':
        data.pop('published_companions')
    elif incomplete == 'missing_fleet':
        rows.pop()
    elif incomplete == 'missing_pool':
        for row in rows:
            row.pop()
    elif incomplete == 'unknown_fraction':
        rows[1][2] = ''
    else:
        data['group'][0]['discards_by_fleet']['Fleet A'] = '-9999'
    model = load(tmp_path, data)
    assert model.discard_returns is None
    assert model.discard_returns_metadata['status'] == 'incomplete'
    assert model.discard_returns_metadata['unresolved']


def test_no_declared_discard_schema_does_not_invent_return_data(tmp_path):
    model = load(tmp_path, source())
    assert model.discard_returns is None
    assert model.discard_returns_metadata['status'] == 'not_supplied'


def test_declared_zero_discards_need_no_destination_assumption(tmp_path):
    data = fleet_source()
    data.pop('published_companions')
    data['group'][0]['discards_by_fleet'] = {'Fleet A': '0', 'Fleet B': '0'}
    data['group'][0]['landings_by_fleet']['Fleet A'] = '10'
    model = load(tmp_path, data)
    assert model.discard_returns_metadata['status'] == 'complete'
    assert model.discard_returns.to_numpy().sum() == 0.


@pytest.mark.parametrize('change', ['negative_amount', 'exceeds_catch', 'inconsistent_landings'])
def test_inconsistent_source_discard_amounts_are_rejected(tmp_path, change):
    data = fleet_source()
    if change == 'negative_amount':
        data['group'][0]['discards_by_fleet']['Fleet A'] = '-1'
    elif change == 'exceeds_catch':
        data['group'][0]['discards_by_fleet']['Fleet A'] = '11'
    else:
        data['group'][0]['landings_by_fleet']['Fleet A'] = '5'
    with pytest.raises(ValueError, match='discard|catch|landing'):
        load(tmp_path, data)


@pytest.mark.parametrize('duplicate', ['fleet', 'header', 'group'])
def test_ambiguous_discard_routing_identities_are_rejected(tmp_path, duplicate):
    data = fleet_source()
    rows = data['published_companions']['Rpath_parameter_model.csv']['rows']
    if duplicate == 'fleet':
        rows.append(rows[1][:])
    elif duplicate == 'header':
        rows[0][3] = rows[0][2]
    else:
        data['group'][3]['group_name'] = data['group'][2]['group_name']
    with pytest.raises(ValueError, match='duplicate|ambiguous'):
        load(tmp_path, data)


@pytest.mark.parametrize('scope,complete', [(None, False), ('landings only', False),
    ('landings plus discards; unknown when either component incomplete', True)])
def test_returned_discards_require_total_catch_scope_evidence(tmp_path, scope, complete):
    data = fleet_source()
    data['group'][0].pop('landings_by_fleet')
    if scope is not None:
        data['group'][0]['export_scope'] = scope
    model = load(tmp_path, data)
    assert model.discard_returns_metadata['status'] == ('complete' if complete else 'incomplete')
    assert (model.discard_returns is not None) == complete
