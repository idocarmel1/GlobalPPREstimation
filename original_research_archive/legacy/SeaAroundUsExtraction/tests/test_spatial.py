from __future__ import annotations

import pandas as pd
import pytest

from shapely.geometry import shape

from ppr_pipeline.spatial import (
    build_spatial_index,
    repair_feature_collection,
    unwrap_feature_collection,
)


def test_unwrap_feature_collection_preserves_geojson_geometry() -> None:
    payload = {
        "data": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"region_id": 13, "title": "Humboldt Current", "region": "lme"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                }
            ],
        }
    }
    result = unwrap_feature_collection(payload)
    assert result["type"] == "FeatureCollection"
    assert result["features"][0]["geometry"]["type"] == "Polygon"


def test_repair_feature_collection_fixes_source_self_intersection() -> None:
    bow_tie = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"region_id": 1},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [2, 2], [0, 2], [2, 0], [0, 0]]],
                },
            }
        ],
    }
    assert not shape(bow_tie["features"][0]["geometry"]).is_valid
    repaired = repair_feature_collection(bow_tie)
    assert shape(repaired["features"][0]["geometry"]).is_valid
    assert repaired["features"][0]["properties"]["geometry_repaired"] is True


def test_spatial_index_marks_configured_pilot_units() -> None:
    lmes = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"region_id": 13, "title": "Humboldt Current", "region": "lme"},
                "geometry": {"type": "Polygon", "coordinates": []},
            }
        ],
    }
    highseas = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"region_id": 71, "title": "Pacific, Western Central", "region": "highseas"},
                "geometry": {"type": "MultiPolygon", "coordinates": []},
            }
        ],
    }
    pilots = [
        {"unit_id": "LME_013", "sau_region": "lme", "sau_region_id": 13, "name": "Humboldt Current"},
        {"unit_id": "HS_071", "sau_region": "highseas", "sau_region_id": 71, "name": "Pacific, Western Central"},
    ]
    index = build_spatial_index(lmes, highseas, pilots)
    assert set(index["unit_id"]) == {"LME_013", "HS_071"}
    assert index["is_pilot"].all()
    assert set(index["geometry_type"]) == {"Polygon", "MultiPolygon"}


def test_spatial_index_rejects_name_mismatch() -> None:
    lmes = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"region_id": 13, "title": "Humboldt Current", "region": "lme"},
                "geometry": {"type": "Polygon", "coordinates": []},
            }
        ],
    }
    with pytest.raises(ValueError, match="name mismatch"):
        build_spatial_index(
            lmes,
            {"type": "FeatureCollection", "features": []},
            [{"unit_id": "LME_013", "sau_region": "lme", "sau_region_id": 13, "name": "Wrong"}],
        )
