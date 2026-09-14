"""Synthetic, independently derived geometry and policy checks for EEZ selection."""
import csv
import importlib
import importlib.util
import json
import math

import pytest
from shapely.geometry import MultiPolygon, Polygon, box, mapping, shape


def module():
    # A missing implementation is an explicit test failure, not a collection error.
    assert importlib.util.find_spec("ppr_pipeline.eez_spatial") is not None, "EEZ spatial implementation missing"
    return importlib.import_module("ppr_pipeline.eez_spatial")


@pytest.mark.parametrize("fraction,want", [(0, True), (0.099999, True), (0.10, False), (0.100001, False)])
def test_low_overlap_is_strict_at_ten_percent(fraction, want):
    assert module().flags_for_eez(fraction, [])["flag_add_low_lme_overlap"] is want


@pytest.mark.parametrize("eez,lme,intersection,mostly,prefer,review", [
    (120, 100, 90, True, True, False),
    (120, 100, 89.999, False, False, False),
    (110, 100, 90, True, False, True),
    (109.999, 100, 90, True, False, False),
    (119.999, 100, 90, True, False, True),
    (120, 100, 0, False, False, False),
])
def test_pair_policy_inclusive_containment_and_ratio_endpoints(eez, lme, intersection, mostly, prefer, review):
    result = module().flags_for_pair(eez, lme, intersection)
    assert result["lme_mostly_contained"] is mostly
    assert result["flag_prefer_eez_candidate"] is prefer
    assert result["flag_review_110_120"] is review
    assert result["intersection_fraction_of_eez"] == intersection / eez
    assert result["intersection_fraction_of_lme"] == intersection / lme
    assert result["eez_to_lme_area_ratio"] == eez / lme


def test_independent_candidate_flags_retain_all_corresponding_lmes():
    m = module()
    pairs = [dict(lme_unit_id="LME_001", **m.flags_for_pair(120, 100, 90)),
             dict(lme_unit_id="LME_002", **m.flags_for_pair(120, 105, 100))]
    row = m.flags_for_eez(0.8, pairs)
    assert row["flag_prefer_eez_candidate"] is True
    assert row["flag_review_110_120"] is True
    assert row["prefer_eez_lme_ids"] == "LME_001"
    assert row["review_110_120_lme_ids"] == "LME_002"
    assert row["mostly_contained_lme_count"] == 2
    assert row["max_lme_containment_fraction"] == 100 / 105
    assert row["max_eez_to_lme_area_ratio"] == 1.2


def test_custom_thresholds_change_policy_without_rounding():
    m = module()
    pair = m.flags_for_pair(130, 100, 80, containment_threshold=.8, prefer_ratio=1.3, review_ratio=1.15)
    assert pair["flag_prefer_eez_candidate"] is True
    assert m.flags_for_eez(.15, [], low_overlap_threshold=.2)["flag_add_low_lme_overlap"] is True


def strip_area_km2(west, east, south, north):
    # Independent integral of WGS84 surface element, not a library polygon-area call.
    a, f = 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    e = math.sqrt(e2)
    def primitive(latitude):
        u = math.sin(math.radians(latitude))
        return (u / (1 - e2 * u * u) + math.atanh(e * u) / e) / 2
    return math.radians(east-west) * a*a*(1-e2) * (primitive(north)-primitive(south)) / 1e6


def test_areas_are_ellipsoidal_km2_not_square_degrees():
    value = module().area_km2(box(0, 0, 1, 1))
    assert value == pytest.approx(strip_area_km2(0, 1, 0, 1), rel=1e-8)
    assert 12000 < value < 13000


def test_dateline_crossing_equals_presplit_geometry():
    m = module()
    wrapped = Polygon([(179, 10), (-179, 10), (-179, 11), (179, 11)])
    split = MultiPolygon([box(179, 10, 180, 11), box(-180, 10, -179, 11)])
    fixed, audit = m.prepare_geometry(wrapped)
    assert fixed.is_valid
    assert fixed.bounds == (-180, 10, 180, 11)
    assert audit["dateline_normalized"] is True
    assert m.area_km2(fixed) == pytest.approx(m.area_km2(split), rel=1e-10)
    assert m.area_km2(fixed) == pytest.approx(strip_area_km2(179, 181, 10, 11), rel=1e-8)


def test_unwrapped_longitudes_are_split_not_discarded():
    m = module()
    unwrapped = box(-181, 10, -179, 11)
    fixed, audit = m.prepare_geometry(unwrapped)
    assert fixed.bounds == (-180, 10, 180, 11)
    assert fixed.is_valid
    assert audit["dateline_normalized"] is True
    assert m.area_km2(fixed) == pytest.approx(strip_area_km2(179,181,10,11), rel=1e-8)
    assert m.area_km2(fixed.intersection(box(179,10,180,11))) == pytest.approx(strip_area_km2(179,180,10,11),rel=1e-8)


def test_polar_cap_keeps_pole_closure_and_ellipsoidal_area():
    m = module()
    polar = Polygon([(-180,80), (0,80), (180,80), (180,90), (-180,90)])
    fixed, audit = m.prepare_geometry(polar)
    assert fixed.is_valid
    assert audit["dateline_normalized"] is False
    assert m.area_km2(fixed) == pytest.approx(strip_area_km2(-180,180,80,90), rel=1e-7)


def test_invalid_bowtie_is_repaired_without_losing_lobes():
    m = module()
    bowtie = Polygon([(0,0), (2,2), (0,2), (2,0), (0,0)])
    fixed, audit = m.prepare_geometry(bowtie)
    assert fixed.is_valid
    assert fixed.geom_type == "MultiPolygon"
    assert fixed.area == 2
    assert audit["geometry_repaired"] is True


def test_valid_source_shape_is_not_simplified_or_densified_on_export():
    source = Polygon([(0,0), (.12345,.2), (.3,.1), (1,1), (1,0)])
    fixed, audit = module().prepare_geometry(source)
    assert fixed.equals_exact(source, 0)
    assert audit["geometry_repaired"] is False


@pytest.mark.parametrize("geometry", [Polygon(), Polygon([(0,91),(1,91),(1,92),(0,91)])])
def test_empty_or_out_of_domain_geometry_fails_explicitly(geometry):
    with pytest.raises(ValueError):
        module().prepare_geometry(geometry)


def write_collection(path, regions, wrapper=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"type":"FeatureCollection", "features":[
        {"type":"Feature", "properties":{"region_id":rid,"title":name}, "geometry":mapping(geometry)}
        for rid, name, geometry in regions]}
    path.write_text(json.dumps({"data":data} if wrapper else data), encoding="utf-8")


def test_outputs_keep_all_eezs_use_union_and_denominators_and_audit(tmp_path):
    m = module()
    # All shapes share the same latitude span: areas scale exactly with longitude width.
    write_collection(tmp_path / "raw_data/SAU_downloads/eez_regions_spatial.json",
                     [(1,"Test",box(0,0,10,1)), (2,"No overlap",box(20,0,21,1)),
                      (3,"Overlapping EEZ",box(5,0,15,1))], True)
    write_collection(tmp_path / "spatial/LMEs.geojson",
                     [(1,"First",box(0,0,6,1)), (2,"Second",box(4,0,8,1))])
    write_collection(tmp_path / "spatial/HighSeas.geojson", [(1,"HS",box(8,0,9,1))])
    result = m.build_eez_spatial_outputs(tmp_path)
    with (tmp_path / "eez_output/tables/eez_selection_flags.csv").open(encoding="utf-8-sig",newline="") as f:
        flags = list(csv.DictReader(f))
    assert len(flags) == 3
    row = flags[0]
    assert [r["unit_id"] for r in flags] == ["EEZ_001","EEZ_002","EEZ_003"]
    assert row["eez_unit_id"] == "EEZ_001"
    assert float(row["lme_overlap_fraction_of_eez"]) == pytest.approx(.8, abs=1e-9)
    assert float(row["hs_overlap_fraction_of_eez"]) == pytest.approx(.1, abs=1e-9)
    assert float(row["uncovered_by_lme_or_hs_km2"]) / float(row["area_km2"]) == pytest.approx(.1, abs=1e-9)
    assert flags[1]["flag_add_low_lme_overlap"] == "True"
    assert float(flags[1]["lme_union_intersection_km2"]) == 0
    with (tmp_path / "eez_output/tables/eez_lme_intersections.csv").open(encoding="utf-8-sig",newline="") as f:
        pairs = list(csv.DictReader(f))
    assert len(pairs) == 4
    for pair in pairs:
        assert float(pair["intersection_fraction_of_eez"]) == pytest.approx(float(pair["intersection_km2"]) / float(pair["eez_area_km2"]))
        assert float(pair["intersection_fraction_of_lme"]) == pytest.approx(float(pair["intersection_km2"]) / float(pair["lme_area_km2"]))
    export = json.loads((tmp_path / "spatial/EEZs.geojson").read_text(encoding="utf-8"))
    assert len(export["features"]) == 3
    assert all(shape(f["geometry"]).is_valid for f in export["features"])
    with (tmp_path / "spatial/eez_units.csv").open(encoding="utf-8-sig",newline="") as f:
        units = list(csv.DictReader(f))
    assert [u["unit_id"] for u in units] == ["EEZ_001","EEZ_002","EEZ_003"]
    assert all(u["crs"] == "EPSG:4326" and u["sau_region"] == "eez" for u in units)
    assert len({r["unit_id"] for r in flags}) == len(units)
    assert {r["unit_id"] for r in flags} == {u["unit_id"] for u in units}
    for name in ("LMEs_normalized.geojson", "HighSeas_normalized.geojson"):
        normalized = json.loads((tmp_path / "eez_output/spatial" / name).read_text(encoding="utf-8"))
        assert all(shape(f["geometry"]).is_valid for f in normalized["features"])
    assert result["eez_count"] == 3
    audit = json.loads((tmp_path / "eez_output/tables/spatial_validation.json").read_text(encoding="utf-8"))
    assert audit["eez_sum_area_km2"] > audit["eez_union_area_km2"]
    assert audit["eez_sum_minus_union_area_km2"] == pytest.approx(strip_area_km2(5,10,0,1), rel=1e-8)
