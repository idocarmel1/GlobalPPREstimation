"""Hand-derived whole-region selection contracts; no catch-area assumptions."""
import importlib
import importlib.util
import json

import pytest
from shapely.geometry import MultiPolygon, box, mapping, shape


def module():
    assert importlib.util.find_spec("ppr_pipeline.selection") is not None, "Spatial selection implementation missing"
    return importlib.import_module("ppr_pipeline.selection")


def unit(uid, geometry):
    return dict(unit_id=uid, region_name=uid, region_type=uid.split("_")[0], geometry=geometry)


def planar(geometry):
    return geometry.area


def test_exact_metrics_distinguish_duplicate_multiplicity_from_twice_covered_area():
    regions = [unit("LME_001", box(0, 0, 4, 1)), unit("HS_001", box(2, 0, 6, 1)),
               unit("EEZ_001", box(3, 0, 5, 1)), unit("EEZ_002", box(8, 0, 10, 1))]
    metrics, overlays = module().coverage_metrics(regions, {"LME_001", "HS_001", "EEZ_001"}, area_fn=planar)
    assert metrics["source_union_area_km2"] == 8
    assert metrics["selected_union_area_km2"] == 6
    assert metrics["selected_sum_area_km2"] == 10
    assert metrics["sum_minus_union_area_km2"] == 4
    assert metrics["area_covered_at_least_twice_km2"] == 3
    assert metrics["gap_area_km2"] == 2
    assert metrics["coverage_fraction"] == .75
    assert overlays["overlaps"].area == 3


def test_lme_preferred_identical_eez_excluded_disjoint_eez_added():
    regions = [unit("LME_001", box(0, 0, 4, 1)), unit("EEZ_001", box(0, 0, 4, 1)),
               unit("HS_001", box(10, 0, 20, 1)), unit("EEZ_002", box(5, 0, 6, 1))]
    result = module().select_regions(regions, area_fn=planar)
    assert result["selected_ids"] == {"LME_001", "HS_001", "EEZ_002"}
    assert result["converged"] is True


def test_addition_requires_unique_coverage_strictly_greater_than_duplicate_area():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("EEZ_001", box(8, 0, 12, 1)),
               unit("EEZ_002", box(20, 0, 21, 1))]
    result = module().select_regions(regions, area_fn=planar)
    assert result["selected_ids"] == {"LME_001", "EEZ_002"}


@pytest.mark.parametrize("east,start,want", [(12, 0, {"EEZ_001"}), (11.9, 0, {"LME_001"}),
    (13, 1.01, {"LME_001"}), (13, 1, {"EEZ_001"})])
def test_replacements_require_containment_and_size_endpoints(east, start, want):
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("EEZ_001", box(start, 0, east, 1))]
    result = module().select_regions(regions, area_fn=planar)
    assert result["selected_ids"] == want


def test_qualifying_replacement_rejected_if_it_worsens_coverage_overlap_balance():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("HS_001", box(10, 0, 30, 1)),
               unit("EEZ_001", box(0, 0, 20, 1))]
    result = module().select_regions(regions, area_fn=planar)
    assert result["selected_ids"] == {"LME_001", "HS_001"}


def test_stricter_penalty_declines_eez_that_default_adds_without_forcing_coverage():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("EEZ_001", box(9, 0, 12, 1))]
    assert module().select_regions(regions, penalty=1, area_fn=planar)["selected_ids"] == {"LME_001", "EEZ_001"}
    assert module().select_regions(regions, penalty=2, area_fn=planar)["selected_ids"] == {"LME_001"}


def test_full_coverage_scenario_retains_every_positive_unique_gap():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("EEZ_001", box(5, 0, 10.01, 1))]
    assert module().select_regions(regions, penalty=0, area_fn=planar)["selected_ids"] == {"LME_001", "EEZ_001"}


def test_region_order_cannot_change_deterministic_selection():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("EEZ_001", box(9, 0, 12, 1)),
               unit("EEZ_002", box(11, 0, 14, 1))]
    m = module()
    assert m.select_regions(regions, area_fn=planar)["selected_ids"] == m.select_regions(regions[::-1], area_fn=planar)["selected_ids"]


def test_one_for_one_eez_swap_improves_greedy_seed_without_removing_preferred_lme():
    # Initial objective gains: A=10, B=9, C=8. Greedy takes A then C (+2).
    # With C present, replacing A by B gains 2 union and saves 1 sum => +5.
    regions = [unit("LME_001", box(30, 0, 40, 1)), unit("EEZ_001", box(0, 0, 10, 1)),
        unit("EEZ_002", MultiPolygon([box(0, 0, 6, 1), box(20, 0, 23, 1)])),
        unit("EEZ_003", MultiPolygon([box(7, 0, 17, 1), box(30, 0, 32, 1)]))]
    result = module().select_regions(regions, area_fn=planar)
    assert result["selected_ids"] == {"LME_001", "EEZ_002", "EEZ_003"}
    assert any(a["action"] == "swap_eez" for a in result["actions"])


def test_whole_region_export_preserves_geometry_and_all_candidate_rows(tmp_path):
    m = module()
    root = tmp_path
    src = root / "eez_output/spatial"
    src.mkdir(parents=True)
    for filename, uid, geometry in [("LMEs_normalized.geojson", "LME_001", box(0, 0, 4, 1)),
            ("HighSeas_normalized.geojson", "HS_001", box(10, 0, 20, 1)),
            ("EEZs.geojson", "EEZ_001", box(0, 0, 4, 1))]:
        fc = dict(type="FeatureCollection", features=[dict(type="Feature", properties=dict(unit_id=uid,
            region_id=1, title=uid), geometry=mapping(geometry))])
        (src / filename).write_text(json.dumps(fc), encoding="utf-8")
    metrics = m.build_selection_outputs(root, expected_count=3, penalties=(1, 2, 0))
    import pandas as pd
    candidates = pd.read_csv(root / "history_output/tables/selection_candidates.csv")
    selected = pd.read_csv(root / "history_output/tables/selected_regions.csv")
    assert len(candidates) == 3
    assert set(selected.unit_id) == {"LME_001", "HS_001"}
    collection = json.loads((root / "history_output/spatial/selected_regions.geojson").read_text())
    assert len(collection["features"]) == 2
    original = {"LME_001":box(0, 0, 4, 1), "HS_001":box(10, 0, 20, 1)}
    assert all(shape(f["geometry"]).equals(original[f["properties"]["unit_id"]]) for f in collection["features"])
    assert metrics["ppr_coverage_fraction"] is None
    assert metrics["membership_fixed_across_years"] is True
    assert metrics["validation"]["status"] == "passed"
    assert (root / "history_output/tables/selection_replacement_groups.csv").exists()
    assert metrics["post_selection_replacement_review"] == []
    assert metrics["global_optimality_certified"] is False
    assert "nonpreferred" in metrics["converged_search_neighborhood"]


def test_projected_working_copy_preserves_source_and_ellipsoidal_area():
    regions = [unit("LME_001", box(0, 0, 1, 1))]
    projected = module().project_working_regions(regions)
    assert regions[0]["geometry"].bounds == (0, 0, 1, 1)
    # Independent WGS84 equal-latitude strip integral at 0..1 degrees.
    assert projected[0]["geometry"].area / 1e6 == pytest.approx(12308.463893975243, rel=1e-10)
    assert projected[0]["unit_id"] == "LME_001"


def test_nonpreferred_high_seas_can_be_removed_but_lme_is_protected():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("HS_001", box(5, 0, 11, 1))]
    result = module().select_regions(regions, area_fn=planar)
    assert result["selected_ids"] == {"LME_001"}
    assert any(a["removed"] == ["HS_001"] and a["union_area_change_km2"] == -1 for a in result["actions"])
    assert module().select_regions(regions, penalty=0, area_fn=planar)["selected_ids"] == {"LME_001", "HS_001"}


def test_full_coverage_can_drop_truly_redundant_high_seas():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("HS_001", box(0, 0, 2, 1))]
    assert module().select_regions(regions, penalty=0, area_fn=planar)["selected_ids"] == {"LME_001"}


def test_replacement_audit_explains_eligible_but_harmful_proposal():
    regions = [unit("LME_001", box(0, 0, 10, 1)), unit("HS_001", box(10, 0, 30, 1)),
               unit("EEZ_001", box(0, 0, 20, 1))]
    audit = module().audit_replacement_groups(regions, {"LME_001", "HS_001"}, area_fn=planar)
    assert len(audit) == 1
    assert audit[0]["eez_unit_id"] == "EEZ_001"
    assert audit[0]["union_area_change_km2"] == 0
    assert audit[0]["duplicate_area_change_km2"] == 10
    assert audit[0]["objective_change_km2"] == -10
    assert audit[0]["beneficial_at_penalty_1"] is False
