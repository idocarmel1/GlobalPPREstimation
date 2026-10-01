"""Coordinator's independent check of the source-prose Java Sea bounds."""
import hashlib
import json
from pathlib import Path

from pyproj import Geod
from shapely.geometry import Point, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGION = ROOT / "regions/LME_038"
EVIDENCE = REGION / "validation_reports/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/geography"
geod = Geod(ellps="WGS84")


def area(geometry):
    if geometry.is_empty:
        return 0.0
    if geometry.geom_type == "Polygon":
        return abs(geod.geometry_area_perimeter(orient(geometry, sign=1))[0]) / 1e6
    return sum(area(part) for part in geometry.geoms)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    target_path = ROOT / "common_reference_data/geography/LMEs.geojson"
    target = shape(next(f for f in read(target_path)["features"]
                        if str(f["properties"].get("region_id")) == "38")["geometry"])
    land_path = ROOT / "common_reference_data/geography/basemaps/ne_50m_land.geojson"
    bounds = box(105 + 50 / 60, -6 - 50 / 60, 117.5, -3)
    land = unary_union([g for f in read(land_path)["features"]
                        if (g := shape(f["geometry"])).intersects(bounds)])
    proposed = read(EVIDENCE / "geographic_assessment.json")
    scenarios = []
    for east in (116.5, 117.5):
        study = box(105 + 50 / 60, -6 - 50 / 60, east, -3).difference(land)
        intersection = study.intersection(target)
        result = dict(east=east, area=area(study), intersection_area=area(intersection),
                      A=100 * area(intersection) / area(target),
                      B=100 * area(intersection) / area(study))
        old = next(s for s in proposed["scenarios"] if s["east"] == east)
        assert all(abs(result[k] - old[k]) < 1e-7 for k in result), (result, old)
        assert study.is_valid and intersection.is_valid
        scenarios.append(result)
    retained = shape(read(EVIDENCE / "reconstructed_study_bounds.geojson")["geometry"])
    assert retained.equals(study), "Retained geometry differs from the eastern117.5 scenario"
    assert shape(read(EVIDENCE / "target_region.geojson")["geometry"]).equals(target)
    controls = []
    for control in proposed["controls"]:
        actual = retained.covers(Point(control["longitude"], control["latitude"]))
        assert actual == control["expected"] == control["actual"], control
        controls.append({**control, "independent_actual": actual})
    sources = [target_path, land_path,
               REGION / "papers/BUCHARY-1991/ubc_1999-0254.pdf.pdf",
               EVIDENCE / "source_figure2_1_landscape.png",
               EVIDENCE / "geographic_assessment.json",
               EVIDENCE / "reconstructed_study_bounds.geojson",
               EVIDENCE / "target_region.geojson"]
    output = {
        "status": "PASS independent source-prose bounds, retained geometries, geodesic areas and controls; final regional package pending",
        "source_review": "Coordinator read Buchary1999 PDF29/printed20 and visually inspected Figure2.1/PDF30. Approximate prose bounds are3S–6deg50minS,105deg50minE and116deg30min–117deg30minE. Figure is bathymetry/context, not an explicit study polygon.",
        "method": "Independent WGS84 ellipsoidal areas; Natural Earth1:50million land mask. Target calculation boundary is unchanged.",
        "target_area_km2": area(target), "scenarios": scenarios, "controls": controls,
        "limits": "Source471000km2 is reported context. Latitudinal bounds may truncate coastline-following waters; east-bound scenarios are sensitivity bounds, not statistical uncertainty. A/B describe an approximate reconstruction and do not scale catch/PPR.",
        "files": [{"path": p.relative_to(ROOT).as_posix(),
                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
    }
    destination = HERE / "verification/LME_038_geography_coordinator_review.json"
    destination.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "scenarios": scenarios, "controls": len(controls)}))


if __name__ == "__main__":
    main()
