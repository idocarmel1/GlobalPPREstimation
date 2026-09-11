import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from external_audit import evaluate


def test_taxon_composition_prevents_region_wide_landings_scaling():
    catches = {'low': {'catch': 9, 'landings': 9, 'discards': 0},
               'high': {'catch': 1, 'landings': 0, 'discards': 1}}
    mass, covered = evaluate(catches, {'low': 10, 'high': 1000})
    assert mass['landings'] == 10
    assert mass['discards'] == pytest.approx(1000 / 9)
    assert mass['landings'] != pytest.approx(mass['catch'] * .9)
    assert covered == {'catch': 10, 'landings': 9, 'discards': 1}


def test_unknown_coefficient_keeps_identical_support_for_all_boundaries():
    catches = {'known': {'catch': 4, 'landings': 3, 'discards': 1},
               'unknown': {'catch': 90, 'landings': 80, 'discards': 10}}
    mass, covered = evaluate(catches, {'known': 9, 'unknown': None})
    assert mass == covered == {'catch': 4, 'landings': 3, 'discards': 1}
