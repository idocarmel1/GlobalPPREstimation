from __future__ import annotations

from collections.abc import Iterable


def latest_common_year(
    year_sets: Iterable[Iterable[int]], requested: int | None = None
) -> int:
    """Return a validated configured year or the latest year in the intersection."""

    normalized = [set(map(int, years)) for years in year_sets]
    if not normalized:
        raise ValueError("No pilot datasets were supplied.")
    common = set.intersection(*normalized)
    if requested is not None:
        requested = int(requested)
        if requested not in common:
            raise ValueError(f"Requested year {requested} is not present in every pilot dataset.")
        return requested
    if not common:
        raise ValueError("No common year exists across the pilot datasets.")
    return max(common)

