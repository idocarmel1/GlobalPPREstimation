import zipfile
import pytest
import ppr_pipeline.provenance as provenance


@pytest.mark.parametrize('name', ['SAU EEZ 9 v50-1.csv', 'SAU EEZ 8 v51-0.csv', 'unknown.csv'])
def test_eez_archive_rejects_wrong_identity_or_version(tmp_path, name):
    assert hasattr(provenance, 'inspect_eez_archive'), 'EEZ identity audit missing'
    path = tmp_path / 'archive.zip'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(name, 'year,tonnes\n2019,1\n')
    with pytest.raises(ValueError):
        provenance.inspect_eez_archive(path, 8, '50.1')


def test_eez_archive_retains_official_empty_csv(tmp_path):
    assert hasattr(provenance, 'inspect_eez_archive'), 'EEZ identity audit missing'
    path = tmp_path / 'archive.zip'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('SAU EEZ 8 v50-1.csv', '')
    result = provenance.inspect_eez_archive(path, 8, '50.1')
    assert result['empty_catch_csv'] is True
    assert result['data_version'] == '50.1'
    assert result['sau_region_id'] == 8
