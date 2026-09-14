"""Execution records bind a successful notebook to the exact current release files."""
import importlib.util
import json
from pathlib import Path

import pytest


def module():
    path=Path(__file__).parents[1]/'tools/eez_execution.py'
    assert path.exists(), 'Missing execution safeguard'
    spec=importlib.util.spec_from_file_location('eez_execution_test',path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def release(tmp_path):
    for name,contents in {'tables/species.csv':'catch,tl\n2,3\n',
        'spatial/EEZs.geojson':'{}','regional_calculations/EEZ_001.xlsx':'xlsx fixture',
        'PPR_EEZ_validation_executed.html':'<html>Success</html>'}.items():
        path=tmp_path/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(contents)
    notebook={'cells':[{'cell_type':'code','source':'print(1)','execution_count':1,'outputs':[]},
                       {'cell_type':'code','source':'  ','execution_count':None,'outputs':[]}]}
    (tmp_path/'PPR_EEZ_validation_executed.ipynb').write_text(json.dumps(notebook))
    return tmp_path


def test_successful_execution_record_verifies_and_excludes_itself(tmp_path):
    api=module(); output=release(tmp_path)
    api.record_execution(output)
    result=api.verify_execution(output)
    assert result['status']=='passed'
    api.record_execution(output)
    assert api.verify_execution(output)['status']=='passed'


@pytest.mark.parametrize('change',['unexecuted','error','no_code'])
def test_refuse_unsuccessful_notebook(tmp_path,change):
    api=module(); output=release(tmp_path)
    path=output/'PPR_EEZ_validation_executed.ipynb'
    data=json.loads(path.read_text())
    if change=='unexecuted': data['cells'][0]['execution_count']=None
    if change=='error': data['cells'][0]['outputs']=[{'output_type':'error','ename':'ValueError','evalue':'bad'}]
    if change=='no_code': data['cells']=[]
    path.write_text(json.dumps(data))
    with pytest.raises((AssertionError,ValueError)): api.record_execution(output)


@pytest.mark.parametrize('filename',['tables/species.csv','spatial/EEZs.geojson',
    'regional_calculations/EEZ_001.xlsx','PPR_EEZ_validation_executed.ipynb',
    'PPR_EEZ_validation_executed.html','tables/additional.csv','extra.xlsx','spatial/additional.geojson'])
def test_changed_or_added_release_file_invalidates_record(tmp_path,filename):
    api=module(); output=release(tmp_path)
    api.record_execution(output)
    target=output/filename
    target.write_bytes(target.read_bytes()+b' ' if target.exists() else b'new')
    with pytest.raises((AssertionError,ValueError)): api.verify_execution(output)


def test_deleted_file_or_missing_record_is_rejected(tmp_path):
    api=module(); output=release(tmp_path)
    with pytest.raises((AssertionError,ValueError,FileNotFoundError)): api.verify_execution(output)
    api.record_execution(output)
    (output/'regional_calculations/EEZ_001.xlsx').unlink()
    with pytest.raises((AssertionError,ValueError,FileNotFoundError)): api.verify_execution(output)
