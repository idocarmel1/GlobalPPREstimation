from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import pandas as pd
from shapely import make_valid
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, mapping, shape
from shapely.ops import unary_union


def unwrap_feature_collection(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = payload.get("data", payload)
    if candidate.get("type") != "FeatureCollection" or not isinstance(
        candidate.get("features"), list
    ):
        raise ValueError("Sea Around Us response does not contain a GeoJSON FeatureCollection.")
    return {"type": "FeatureCollection", "features": candidate["features"]}


def _polygonal_geometry(geometry: Any) -> Polygon | MultiPolygon:
    if isinstance(geometry, (Polygon, MultiPolygon)):
        return geometry
    if isinstance(geometry, GeometryCollection):
        polygons = []
        for part in geometry.geoms:
            if isinstance(part, Polygon):
                polygons.append(part)
            elif isinstance(part, MultiPolygon):
                polygons.extend(part.geoms)
        if polygons:
            merged = unary_union(polygons)
            if isinstance(merged, (Polygon, MultiPolygon)):
                return merged
    raise ValueError("Geometry repair did not yield a polygonal Sea Around Us region.")


def repair_feature_collection(collection: dict[str, Any]) -> dict[str, Any]:
    """Return valid polygonal GeoJSON while retaining source properties."""
    repaired = deepcopy(collection)
    for feature in repaired.get("features", []):
        geometry_json = feature.get("geometry")
        properties = feature.setdefault("properties", {})
        properties["geometry_repaired"] = False
        if not geometry_json:
            continue
        geometry = shape(geometry_json)
        if not geometry.is_valid:
            fixed = _polygonal_geometry(make_valid(geometry))
            if not fixed.is_valid:
                raise ValueError("Sea Around Us geometry remains invalid after repair.")
            feature["geometry"] = mapping(fixed)
            properties["geometry_repaired"] = True
    return repaired


def build_spatial_index(
    lmes: dict[str, Any],
    highseas: dict[str, Any],
    pilot_units: list[dict[str, Any]],
) -> pd.DataFrame:
    pilot_lookup = {
        (str(item["sau_region"]), int(item["sau_region_id"])): item for item in pilot_units
    }
    seen_pilots: set[tuple[str, int]] = set()
    rows: list[dict[str, Any]] = []
    for region, collection, prefix in [
        ("lme", lmes, "LME"),
        ("highseas", highseas, "HS"),
    ]:
        for feature in collection.get("features", []):
            props = feature.get("properties", {})
            region_id = int(props["region_id"])
            title = str(props["title"])
            key = (region, region_id)
            configured = pilot_lookup.get(key)
            if configured and configured["name"] != title:
                raise ValueError(
                    f"Pilot name mismatch for {region} {region_id}: "
                    f"configured {configured['name']!r}, API {title!r}."
                )
            if configured:
                seen_pilots.add(key)
            rows.append(
                {
                    "unit_id": configured["unit_id"] if configured else f"{prefix}_{region_id:03d}",
                    "name": title,
                    "type": "LME" if region == "lme" else "High Seas",
                    "sau_region": region,
                    "sau_region_id": region_id,
                    "geometry_type": (feature.get("geometry") or {}).get("type", ""),
                    "geometry_repaired": bool(props.get("geometry_repaired", False)),
                    "crs": "EPSG:4326",
                    "is_pilot": configured is not None,
                }
            )
    missing = set(pilot_lookup) - seen_pilots
    if missing:
        raise ValueError(f"Pilot regions missing from spatial data: {sorted(missing)}")
    return pd.DataFrame(rows).sort_values(["type", "sau_region_id"]).reset_index(drop=True)


def write_spatial_outputs(
    lme_wrapper_path: str | Path,
    highseas_wrapper_path: str | Path,
    pilot_units: list[dict[str, Any]],
    output_dir: str | Path,
) -> pd.DataFrame:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    lmes = repair_feature_collection(
        unwrap_feature_collection(json.loads(Path(lme_wrapper_path).read_text(encoding="utf-8")))
    )
    highseas = repair_feature_collection(
        unwrap_feature_collection(
            json.loads(Path(highseas_wrapper_path).read_text(encoding="utf-8"))
        )
    )
    (out / "LMEs.geojson").write_text(
        json.dumps(lmes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (out / "HighSeas.geojson").write_text(
        json.dumps(highseas, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    index = build_spatial_index(lmes, highseas, pilot_units)
    index.to_csv(out / "spatial_units.csv", index=False, encoding="utf-8-sig")
    return index
