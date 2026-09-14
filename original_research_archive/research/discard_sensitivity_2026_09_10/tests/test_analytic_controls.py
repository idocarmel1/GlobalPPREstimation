import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from metrics import solve_recycling_control


def test_recycling_control_matches_independent_series():
    # Fish x=5+2*d; detritus d=.2+.1*x -> d=.875, x=6.75.
    result=solve_recycling_control(5.,2.,.2,.1)
    assert result['fish']==pytest.approx(6.75)
    assert result['detritus']==pytest.approx(.875)
    d=0.
    for _ in range(100): d=.2+.1*(5+2*d)
    assert result['detritus']==pytest.approx(d)


def test_no_return_path_is_invariant():
    assert solve_recycling_control(5.,0.,.2,.1)['fish']==5
    assert solve_recycling_control(5.,0.,.2,.7)['fish']==5


def test_divergent_control_is_invalid():
    with pytest.raises(ValueError,match='diverg'):
        solve_recycling_control(5.,2.,.2,.6)

