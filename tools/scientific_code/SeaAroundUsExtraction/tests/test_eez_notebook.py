import importlib.util
import json
from pathlib import Path
import sys
import types

import nbformat
import pytest


@pytest.fixture(autouse=True)
def isolated_html_dependency(monkeypatch):
    # Tests deliberately control the slow execution/export boundary; no real notebook is run.
    if importlib.util.find_spec('nbconvert') is None:
        dependency=types.ModuleType('nbconvert')
        dependency.HTMLExporter=object
        monkeypatch.setitem(sys.modules,'nbconvert',dependency)


def builder():
    path=Path(__file__).parents[1]/'build_eez_notebook.py'
    spec=importlib.util.spec_from_file_location('eez_builder_test',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(tmp_path):
    output=tmp_path/'eez_output'
    (output/'tables').mkdir(parents=True)
    (output/'tables/spatial_validation.json').write_text(json.dumps({'thresholds':{
        'low_overlap_threshold':.07,'containment_threshold':.85,'prefer_ratio':1.3,'review_ratio':1.05}}))
    (output/'spatial').mkdir()
    (output/'spatial/EEZs.geojson').write_text('{}')
    (output/'summary.xlsx').write_text('xlsx fixture')
    return output


def test_nondefault_thresholds_appear_in_generated_rule_narrative(tmp_path,monkeypatch):
    api=builder(); output=prepare(tmp_path)
    assert hasattr(api,'build_notebook'), 'Notebook construction must be separate from execution/publication'
    notebook=api.build_notebook(tmp_path)
    narrative=next(cell.source for cell in notebook.cells if cell.cell_type=='markdown' and 'Advisory spatial rules' in cell.source)
    assert '7%' in narrative and '85%' in narrative and '1.30' in narrative and '1.05' in narrative
    assert '10%' not in narrative and '90%' not in narrative and '1.20' not in narrative


def test_generated_notebook_has_no_jensen_comparison(tmp_path):
    api=builder(); prepare(tmp_path)
    notebook=api.build_notebook(tmp_path)
    text='\n'.join(''.join(cell.source) for cell in notebook.cells)
    assert 'jensen_comparison.csv' not in text
    assert 'jensen_violations' not in text
    assert 'Jensen' not in text
    assert 'ppr_correct' not in text
    assert 'ppr_jensen' not in text


@pytest.mark.parametrize('failure',['execute','html','unexecuted','changed_inputs'])
def test_failed_rerun_preserves_old_artifacts_but_invalidates_success(tmp_path,monkeypatch,failure):
    api=builder(); output=prepare(tmp_path)
    assert hasattr(api,'record_execution'), 'Builder must record successful execution'
    old=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('print(1)',execution_count=1)])
    nbformat.write(old,output/'PPR_EEZ_validation_executed.ipynb')
    html=output/'PPR_EEZ_validation_executed.html'; html.write_text('old successful html')
    api.record_execution(output)
    before=(output/'PPR_EEZ_validation_executed.ipynb').read_bytes()
    class Client:
        def __init__(self,notebook,**kwargs): self.notebook=notebook
        def execute(self):
            assert (output/'PPR_EEZ_validation_executed.ipynb').read_bytes()==before
            if failure=='execute': raise RuntimeError('execution failed')
            if failure=='unexecuted': return
            if failure=='changed_inputs': (output/'summary.xlsx').write_text('changed during execution')
            for i,cell in enumerate(self.notebook.cells,1):
                if cell.cell_type=='code': cell.execution_count=i
    class Exporter:
        def from_notebook_node(self,notebook):
            if failure=='html': raise RuntimeError('HTML failed')
            return '<html>new export</html>',{}
    monkeypatch.setattr(api,'NotebookClient',Client)
    monkeypatch.setattr(api,'HTMLExporter',Exporter)
    with pytest.raises((RuntimeError,ValueError)): api.main(tmp_path)
    assert (output/'PPR_EEZ_validation_executed.ipynb').read_bytes()==before
    assert html.read_text()=='old successful html'
    with pytest.raises((ValueError,AssertionError,FileNotFoundError)): api.verify_execution(output)


def test_successful_builder_publishes_executed_notebook_html_and_record(tmp_path,monkeypatch):
    api=builder(); output=prepare(tmp_path)
    assert hasattr(api,'verify_execution')
    class Client:
        def __init__(self,notebook,**kwargs): self.notebook=notebook
        def execute(self):
            assert not (output/'PPR_EEZ_validation_executed.ipynb').exists()
            for i,cell in enumerate(self.notebook.cells,1):
                if cell.cell_type=='code': cell.execution_count=i
    class Exporter:
        def from_notebook_node(self,notebook): return '<html>current successful notebook</html>',{}
    monkeypatch.setattr(api,'NotebookClient',Client)
    monkeypatch.setattr(api,'HTMLExporter',Exporter)
    api.main(tmp_path)
    assert api.verify_execution(output)['status']=='passed'
    assert 'current successful notebook' in (output/'PPR_EEZ_validation_executed.html').read_text()
