import pytest

from ppr_pipeline.pipeline import build_unit_manifest
import ppr_pipeline.download as download


def test_eez_manifest_is_not_mislabeled_as_high_seas():
    unit = {'unit_id': 'EEZ_008', 'name': 'Albania', 'sau_region': 'eez', 'sau_region_id': 8}
    assert build_unit_manifest([unit])[0]['region_type'] == 'EEZ'


def test_unknown_region_type_is_rejected():
    unit = {'unit_id': 'X_001', 'name': 'Wrong', 'sau_region': 'wrong', 'sau_region_id': 1}
    with pytest.raises(ValueError, match='region'):
        build_unit_manifest([unit])


def test_catalog_keeps_all_eezs_and_uses_official_ids():
    assert hasattr(download, 'eez_units_from_catalog'), 'EEZ catalog conversion not implemented'
    payload = {'data': [{'id': 917, 'title': 'Yemen (Arabian Sea)'}, {'id': 8, 'title': 'Albania'}]}
    result = download.eez_units_from_catalog(payload)
    assert result == [
        {'unit_id': 'EEZ_008', 'name': 'Albania', 'sau_region': 'eez', 'sau_region_id': 8},
        {'unit_id': 'EEZ_917', 'name': 'Yemen (Arabian Sea)', 'sau_region': 'eez', 'sau_region_id': 917},
    ]


def test_duplicate_eez_ids_are_rejected_not_silently_dropped():
    assert hasattr(download, 'eez_units_from_catalog'), 'EEZ catalog conversion not implemented'
    with pytest.raises(ValueError, match='duplicate'):
        download.eez_units_from_catalog({'data': [{'id': 8, 'title': 'A'}, {'id': 8, 'title': 'B'}]})
