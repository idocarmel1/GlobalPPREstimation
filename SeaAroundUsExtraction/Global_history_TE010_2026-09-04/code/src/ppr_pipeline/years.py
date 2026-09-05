from __future__ import annotations

from collections.abc import Iterable
from .ingest import available_years_from_archive


def common_year_for_archives(archives, requested=None, progress=None):
    """Choose a common year across spatial alternatives, excluding audited empty sources."""
    sets, audit = [], {}
    for i,(unit_id,path) in enumerate(archives.items(),1):
        available = available_years_from_archive(path)
        if available:
            sets.append(available)
        audit[unit_id] = {'available_years':sorted(map(int,available)),
            'constrains_common_year':bool(available),'empty_archive':not available}
        if progress:
            progress(f'Common-year scan [{i}/{len(archives)}] {unit_id}',flush=True)
    return latest_common_year(sets,requested=requested),audit


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
