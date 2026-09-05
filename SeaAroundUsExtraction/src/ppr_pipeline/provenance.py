from __future__ import annotations

from collections.abc import Iterable, Mapping

from .download import catch_url, exploited_url


def unit_source_urls(
    base_url: str,
    units: Iterable[Mapping[str, str | int]],
) -> dict[str, str]:
    """Map frozen unit input filenames to their authoritative API URLs."""
    urls: dict[str, str] = {}
    for unit in units:
        unit_id = str(unit["unit_id"])
        region = str(unit["sau_region"])
        region_id = int(unit["sau_region_id"])
        urls[f"{unit_id}-catch.zip"] = catch_url(base_url, region, region_id)
        urls[f"{unit_id}-exploited.json"] = exploited_url(
            base_url, region, region_id
        )
    return urls
