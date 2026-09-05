from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
import re
import zipfile

from .download import catch_url, exploited_url


def inspect_eez_archive(path: str | Path, region_id: int, expected_version: str) -> dict:
    """Verify the source's own CSV identity/version, including empty archives."""
    with zipfile.ZipFile(path) as archive:
        csvs = [info for info in archive.infolist() if info.filename.lower().endswith('.csv')]
        if len(csvs) != 1:
            raise ValueError(f'Expected one EEZ catch CSV in {path}')
        info = csvs[0]
        match = re.fullmatch(r'SAU EEZ (\d+) v(\d+)-(\d+)\.csv', Path(info.filename).name)
        if not match or int(match[1]) != int(region_id):
            raise ValueError(f'EEZ archive identity mismatch: {info.filename}')
        version = f'{match[2]}.{match[3]}'
        if version != expected_version:
            raise ValueError(f'EEZ archive version {version} != {expected_version}')
        return {'sau_region_id': int(region_id), 'catch_csv': info.filename,
                'data_version': version, 'csv_bytes': info.file_size,
                'empty_catch_csv': info.file_size == 0}


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
