"""Check retained Kyoto study geometry against native evidence and root trace."""
from pathlib import Path
import hashlib
import io
import json
import math
import numpy as np
import pymupdf
from PIL import Image
from pyproj import Geod
from shapely.geometry import shape, Point
from shapely.geometry.polygon import orient

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
EVIDENCE = ROOT / "regions/LME_050/validation_reports/50_502013_Coastal_Kyoto_Inoue_(2013)"
GEO = EVIDENCE / "geography"
WORK = BASE / "work/LME_050/coordinator_geography"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assessment = json.loads((GEO / "geographic_assessment.json").read_text(encoding="utf-8"))
source = ROOT / assessment["source"]
assert sha(source) == assessment["source_sha256"]
with pymupdf.open(source) as doc:
    native = np.asarray(Image.open(io.BytesIO(doc.extract_image(23)["image"])).convert("RGB"))
assert np.array_equal(native, np.asarray(Image.open(GEO / "original_figure1.jpg").convert("RGB")))
retained = json.loads((GEO / "study_area_reconstructed.geojson").read_text(encoding="utf-8"))
draft = json.loads((WORK / "Figure1_study_trace_draft.geojson").read_text(encoding="utf-8"))
assert retained["geometry"] == draft["geometry"]
s = shape(retained["geometry"])
layer = ROOT / "common_reference_data/geography/LMEs.geojson"
r = shape(next(f["geometry"] for f in json.loads(layer.read_text(encoding="utf-8"))["features"]
               if f["properties"]["region_id"] == 50))
g = Geod(ellps="WGS84")
def area(x):
    if x.is_empty:
        return 0.0
    if x.geom_type == "Polygon":
        return abs(g.geometry_area_perimeter(orient(x, sign=1))[0]) / 1e6
    return sum(area(p) for p in x.geoms)
assert s.is_valid
R, S, I = area(r), area(s), area(s.intersection(r))
values = dict(target_area_km2=R, study_area_km2=S, intersection_km2=I,
              A_percent=100*I/R, B_percent=100*I/S)
reported = next(x for x in assessment["scenarios"] if x["buffer_degrees"] == 0)
for key, value in values.items():
    assert math.isclose(value, reported[key], rel_tol=1e-12, abs_tol=1e-8), key
controls = []
for c in assessment["ordered_water_land_controls"]:
    actual = s.covers(Point(c["longitude"], c["latitude"]))
    assert actual == c["expected_inside"]
    controls.append({**c, "coordinator_actual_inside": actual})
assert sha(GEO / "native_area_source_check.json") == sha(WORK / "native_area_source_check.json")
record = {
    "status": "PASS coordinator native-source, retained-geometry and numerical checks; independent QA and shared display remain separately tracked",
    "source_review": "Coordinator read native main PDF 2 Figure 1 and PDF 4 methods: coastal Kyoto model extends from the coast to 240 m, reported 2,230 km². Native supplemental S1 Table 2 and paragraphs 26/32/34 independently confirm seven depth-bin areas sum to 1,223 km² with whole-CAK denominator language; no source reconciliation was identified.",
    "visual_review": "Native Figure 1, source-overlay trace, target-overlay trace and retained Word geographic pages inspected. Ordered northern bends, narrow bathymetric loop, Tango Bay water, mainland and two source islands retained. No fitting to a reported area.",
    "native_raster_pixel_exact": True,
    "retained_geometry_equals_root_trace": True,
    "independent_geodesic_results": values,
    "water_land_controls": controls,
    "reported_main_area_km2": 2230,
    "supplementary_depth_bins_sum_km2": 1223,
    "limits": "Low-confidence graphical reconstruction, not author GIS or an independently verified 240 m contour. Only two ticks per axis. The 24.62% trace/main area discrepancy exceeds the ±0.005° graphical sensitivity. Indicative A 0.15–0.23% and B 95–100% are descriptive, not statistical or rigorous bounds. The 1,223 km² source sum does not establish a substitute polygon or overlap bound. No biomass rescaling or catch/PPR multiplier.",
    "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in [
        source, GEO / "original_figure1.jpg", GEO / "study_area_reconstructed.geojson",
        GEO / "native_trace_overlay.png", GEO / "geographic_assessment.json",
        GEO / "native_area_source_check.json"]],
}
out = BASE / "verification/LME_050_geography_coordinator_review.json"
out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "PASS", "controls": len(controls), **values}))
