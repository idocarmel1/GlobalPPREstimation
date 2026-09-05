import importlib.util
import json
from pathlib import Path
import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location('eez_runner',Path(__file__).resolve().parents[1]/'run_eez_pipeline.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


@pytest.mark.parametrize('baseline_year,baseline_te,requested',[(2019,.1,2018),(2019,.05,2019)])
def test_comparison_recalculates_separate_scope_for_wrong_year_or_te(tmp_path,monkeypatch,baseline_year,baseline_te,requested):
    assert hasattr(runner,'comparison_for_year'), 'comparison selection helper missing'
    tables = tmp_path/'global_output/tables'
    tables.mkdir(parents=True)
    (tables/'run_metadata.json').write_text(json.dumps({'year':baseline_year,'transfer_efficiency':baseline_te}))
    pd.DataFrame([{'year':baseline_year,'ppr_species':999}]).to_csv(tables/'global_summary.csv',index=False)
    def calculate(root,config,*,requested_year):
        assert root==tmp_path and config==tmp_path/'config/global_eez_comparison.yml'
        assert requested_year==requested
        return {'summary':pd.DataFrame([{'year':requested,'ppr_species':100}])}
    monkeypatch.setattr(runner,'run_analysis',calculate)
    frame,directory = runner.comparison_for_year(tmp_path,requested)
    assert directory=='eez_comparison_output'
    assert frame.ppr_species.tolist()==[100]
    assert pd.read_csv(tables/'global_summary.csv').ppr_species.tolist()==[999]


def test_matching_baseline_is_reused_without_modification(tmp_path):
    assert hasattr(runner,'comparison_for_year'), 'comparison selection helper missing'
    tables = tmp_path/'global_output/tables'
    tables.mkdir(parents=True)
    (tables/'run_metadata.json').write_text(json.dumps({'year':2019,'transfer_efficiency':.1}))
    pd.DataFrame([{'year':2019,'ppr_species':100}]).to_csv(tables/'global_summary.csv',index=False)
    frame,directory = runner.comparison_for_year(tmp_path,2019)
    assert directory=='global_output' and frame.ppr_species.tolist()==[100]
