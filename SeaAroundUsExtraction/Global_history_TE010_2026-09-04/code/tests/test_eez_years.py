import zipfile
import json
import pytest
import ppr_pipeline.years as years


def test_all_area_common_year_includes_comparison_archives(tmp_path):
    assert hasattr(years,'common_year_for_archives'), 'cross-system common-year selection missing'
    files = {}
    for unit,dates in {'EEZ_001':[2018,2019,2020],'LME_001':[2018,2019],'HS_001':[]}.items():
        path = tmp_path/f'{unit}.zip'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('catch.csv','year\n'+''.join(f'{d}\n' for d in dates) if dates else '')
        files[unit] = path
    year,audit = years.common_year_for_archives(files)
    assert year==2019
    assert len(audit)==3
    assert audit['HS_001']['constrains_common_year'] is False
    assert json.loads(json.dumps(audit))['EEZ_001']['available_years'] == [2018,2019,2020]
    assert years.common_year_for_archives(files,requested=2018)[0]==2018
    with pytest.raises(ValueError):
        years.common_year_for_archives(files,requested=2020)
