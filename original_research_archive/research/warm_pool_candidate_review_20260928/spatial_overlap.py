"""Reproducible comparison of published study rectangles with stored region polygons.

This measures the explicitly stated study domain, not an inferred study polygon.
Area uses WGS84 geodesic rings after densifying straight lon/lat segments to 0.05°.
It retains the gross domain denominator; land is not silently subtracted.
"""
import hashlib
import json
from pathlib import Path

from pyproj import Geod
from shapely import segmentize
from shapely.geometry import box, shape
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GEOD = Geod(ellps="WGS84")


def area(geom, step=0.05):
    if geom.is_empty:
        return 0.0
    if geom.geom_type != "Polygon":
        return sum(area(g, step) for g in geom.geoms)
    ringed = orient(segmentize(geom, step), sign=1)
    return abs(GEOD.geometry_area_perimeter(ringed)[0]) / 1e6


def main():
    regions = {}
    for uid, file, rid in [("HS_071", "HighSeas.geojson", 71),
                           ("EEZ_941", "EEZs.geojson", 941),
                           ("EEZ_598", "EEZs.geojson", 598)]:
        path = ROOT / "common_reference_data/geography" / file
        raw = path.read_bytes()
        f = next(f for f in json.loads(raw)["features"]
                 if f["properties"].get("region_id") == rid)
        geom = shape(f["geometry"])
        assert geom.is_valid
        regions[uid] = (geom, {"title": f["properties"]["title"],
                             "source": path.relative_to(ROOT).as_posix(),
                             "sha256": hashlib.sha256(raw).hexdigest(),
                             "area_km2": area(geom)})
    # Negative-longitude EEZ fragment lies east of 180E, outside both rectangles.
    domains = {
        "Griffiths2019": {"bounds": [140, -15, 180, 10],
                          "source": "doi:10.1111/fog.12389; study area text and Figure 1",
                          "reported_ocean_area_km2": 11543000},
        "WCP2007": {"bounds": [110, -15, 180, 15],
                    "source": "SC3-EB-IP-8, study area"},
    }
    results = {"method": __doc__, "regions": {k: v[1] for k, v in regions.items()},
               "domains": {}}
    for name, spec in domains.items():
        domain = box(*spec["bounds"])
        total = area(domain)
        row = {**spec, "computed_gross_area_km2": total, "overlap": {}}
        for uid, (geom, meta) in regions.items():
            intersect = geom.intersection(domain)
            a = area(intersect)
            a_fine = area(intersect, 0.01)
            row["overlap"][uid] = {
                "intersection_km2": a,
                "percent_target_region_covered": 100*a/meta["area_km2"],
                "percent_gross_model_domain_in_region": 100*a/total,
                "area_refinement_difference_percent": 100*(a_fine-a)/a if a else 0,
            }
            if spec.get("reported_ocean_area_km2"):
                row["overlap"][uid]["percent_reported_model_ocean_area_in_region"] = (
                    100*a/spec["reported_ocean_area_km2"])
        results["domains"][name] = row
    (OUT/"SPATIAL_OVERLAP.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
