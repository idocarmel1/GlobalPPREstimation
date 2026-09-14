import pandas as pd
import pytest
import ppr_pipeline.pipeline as pipeline


def test_comparison_shares_and_ranks_use_only_each_spatial_type():
    assert hasattr(pipeline, 'summarize_spatial_alternatives'), 'type-specific summary missing'
    raw = pd.DataFrame([
        {'unit_id':'EEZ_002','region_type':'EEZ','ppr_species':10.,'year':2019},
        {'unit_id':'LME_001','region_type':'LME','ppr_species':100.,'year':2019},
        {'unit_id':'EEZ_001','region_type':'EEZ','ppr_species':30.,'year':2019},
        {'unit_id':'HS_018','region_type':'High Seas','ppr_species':0.,'year':2019},
    ])
    result = pipeline.summarize_spatial_alternatives(raw).set_index('unit_id')
    assert result.loc['EEZ_001','fraction_type_ppr'] == .75
    assert result.loc['EEZ_002','fraction_type_ppr'] == .25
    assert result.loc['EEZ_002','accumulated_fraction_type'] == 1.
    assert result.loc['LME_001','fraction_type_ppr'] == 1.
    assert result.loc['EEZ_002','rank_type_ppr'] == 2
    assert pd.isna(result.loc['HS_018','fraction_type_ppr'])


def test_comparison_rejects_different_analysis_years():
    assert hasattr(pipeline, 'summarize_spatial_alternatives'), 'type-specific summary missing'
    with pytest.raises(ValueError, match='year'):
        pipeline.summarize_spatial_alternatives(pd.DataFrame([
            {'unit_id':'EEZ_001','region_type':'EEZ','ppr_species':1.,'year':2018},
            {'unit_id':'LME_001','region_type':'LME','ppr_species':1.,'year':2019},
        ]))
