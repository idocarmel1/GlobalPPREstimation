import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from metrics import fixed_support_ppr, decompose


def test_failed_positive_harvest_coefficient_invalidates_total():
    assert fixed_support_ppr(pd.Series([2.,np.nan]),pd.Series([1.,1.])) is None


def test_missing_uncaught_coefficient_does_not_create_missing_catch():
    assert fixed_support_ppr(pd.Series([2.,np.nan]),pd.Series([1.,0.]))==pytest.approx(2/9)


def test_decomposition_reconstructs_total():
    d=decompose(100.,130.,80.,104.)
    assert d['coefficient_effect']==30
    assert d['catch_effect']==-20
    assert d['interaction']==-6
    assert sum(d[k] for k in ['coefficient_effect','catch_effect','interaction'])==d['total_change']==4
