from __future__ import annotations

import pytest

from ppr_pipeline.years import latest_common_year


def test_latest_common_year_uses_intersection() -> None:
    assert latest_common_year([{2018, 2019}, {2017, 2018, 2019}, {2019, 2020}]) == 2019


def test_requested_common_year_is_accepted() -> None:
    assert latest_common_year([{2018, 2019}, {2017, 2018, 2019}], requested=2018) == 2018


def test_requested_year_missing_from_a_unit_is_rejected() -> None:
    with pytest.raises(ValueError, match="not present in every pilot dataset"):
        latest_common_year([{2018, 2019}, {2019}], requested=2018)


def test_empty_year_intersection_is_rejected() -> None:
    with pytest.raises(ValueError, match="No common year"):
        latest_common_year([{2018}, {2019}])

