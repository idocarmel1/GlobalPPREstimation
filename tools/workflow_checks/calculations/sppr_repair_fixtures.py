"""Immutable v1 source for derivative tests after the canonical helper advances."""
import hashlib
from pathlib import Path


V1_SOURCE = (Path(__file__).resolve().parents[3]/'regions/LME/LME_003/papers/CAL-2016/models/'
             'CAL-2016_California_Current_2000-2014/results/diagnostics/'
             'engine_comparison_20261114/current_engine/PPRCalculator.py')
V1_SHA256 = '3b6d2266b532adb496644c59725fcb86a34923b5a212e38bee0931505f3568f8'


def v1_source_bytes():
    raw = V1_SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != V1_SHA256:
        raise AssertionError('Pinned v1 calculator fixture changed')
    return raw
