"""Download and freeze the Sea Around Us inputs used by the pilot."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import urlencode
import zipfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yaml


def eez_units_from_catalog(payload: dict) -> list[dict[str, str | int]]:
    """Retain every official EEZ ID, including separate territories/facades."""
    rows = payload["data"]
    units = [
        {"unit_id": f"EEZ_{int(row['id']):03d}", "name": row["title"],
         "sau_region": "eez", "sau_region_id": int(row["id"])}
        for row in rows
    ]
    if len({unit["unit_id"] for unit in units}) != len(units):
        raise ValueError("EEZ catalog contains duplicate region IDs")
    return sorted(units, key=lambda unit: unit["sau_region_id"])


def load_units_from_spatial_index(path: str | Path) -> list[dict[str, str | int]]:
    """Load every LME and High Seas unit from the normalized spatial index."""
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        {
            "unit_id": row["unit_id"],
            "name": row["name"],
            "sau_region": row["sau_region"],
            "sau_region_id": int(row["sau_region_id"]),
        }
        for row in rows
    ]


def _endpoint(base_url: str, path: str, params: dict | None = None) -> str:
    url = f"{base_url.rstrip('/')}/{path.strip('/')}/"
    return f"{url}?{urlencode(params)}" if params else url


def catch_url(base_url: str, region: str, region_id: int) -> str:
    return _endpoint(
        base_url,
        f"{region}/tonnage/taxon",
        {
            "format": "csv",
            "limit": 10,
            "sciname": "false",
            "region_id": int(region_id),
        },
    )


def exploited_url(base_url: str, region: str, region_id: int) -> str:
    return _endpoint(
        base_url,
        f"{region}/exploited-organisms",
        {"region_id": int(region_id)},
    )


def regions_url(base_url: str, region: str, *, spatial: bool) -> str:
    params = None if spatial else {"nospatial": "true"}
    return _endpoint(base_url, region, params)


def _download(session: requests.Session, url: str, destination: Path, *, overwrite: bool) -> bool:
    if destination.exists() and not overwrite:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f"{destination.name}.partial")
    try:
        with session.get(url, timeout=180, stream=True) as response:
            response.raise_for_status()
            with temporary.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        temporary.replace(destination)
        return True
    finally:
        temporary.unlink(missing_ok=True)


def _session_with_retries() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "PPR-global/1.0 (reproducible research download)"})
    return session


def download_unit_inputs(
    units: list[dict[str, str | int]],
    base_url: str,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
    progress=print,
) -> list[Path]:
    """Download resumable catch and exploited-organism inputs for many units."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    with _session_with_retries() as session:
        for index, unit in enumerate(units, start=1):
            unit_id = str(unit["unit_id"])
            region = str(unit["sau_region"])
            region_id = int(unit["sau_region_id"])
            catch_target = output_dir / f"{unit_id}-catch.zip"
            tl_target = output_dir / f"{unit_id}-exploited.json"

            if catch_target.exists() and not zipfile.is_zipfile(catch_target):
                catch_target.unlink()
            catch_changed = _download(
                session,
                catch_url(base_url, region, region_id),
                catch_target,
                overwrite=overwrite,
            )
            if not zipfile.is_zipfile(catch_target):
                raise ValueError(f"Downloaded catch archive is not a valid ZIP: {catch_target}")

            try:
                if tl_target.exists():
                    payload = json.loads(tl_target.read_text(encoding="utf-8"))
                    if not isinstance(payload.get("data", []), list):
                        raise ValueError("invalid data payload")
            except (ValueError, TypeError):
                tl_target.unlink(missing_ok=True)
            tl_changed = _download(
                session,
                exploited_url(base_url, region, region_id),
                tl_target,
                overwrite=overwrite,
            )
            payload = json.loads(tl_target.read_text(encoding="utf-8"))
            if not isinstance(payload.get("data", []), list):
                raise ValueError(f"Invalid exploited-organisms JSON: {tl_target}")
            outputs.extend((catch_target, tl_target))
            action = "downloaded" if catch_changed or tl_changed else "reused"
            if progress:
                progress(f"[{index}/{len(units)}] {unit_id} {action}")
    return outputs


def download_pilot_inputs(
    config_path: str | Path,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> list[Path]:
    """Download region catalogs, polygons, catches, and regional TL data."""
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    base_url = config["sea_around_us"]["api_base_url"]
    output_dir = Path(output_dir)
    outputs: list[Path] = []

    with requests.Session() as session:
        session.headers.update({"User-Agent": "PPR-pilot/1.0 (reproducible research download)"})
        for region in ("lme", "highseas"):
            for spatial in (False, True):
                suffix = "_spatial" if spatial else ""
                target = output_dir / f"{region}_regions{suffix}.json"
                _download(session, regions_url(base_url, region, spatial=spatial), target, overwrite=overwrite)
                outputs.append(target)

        for pilot in config["pilot_units"]:
            unit_id = pilot["unit_id"]
            region = pilot["sau_region"]
            region_id = pilot["sau_region_id"]
            catch_target = output_dir / f"{unit_id}-catch.zip"
            tl_target = output_dir / f"{unit_id}-exploited.json"
            _download(session, catch_url(base_url, region, region_id), catch_target, overwrite=overwrite)
            if not zipfile.is_zipfile(catch_target):
                raise ValueError(f"Downloaded catch archive is not a valid ZIP: {catch_target}")
            _download(session, exploited_url(base_url, region, region_id), tl_target, overwrite=overwrite)
            outputs.extend((catch_target, tl_target))

    return outputs
