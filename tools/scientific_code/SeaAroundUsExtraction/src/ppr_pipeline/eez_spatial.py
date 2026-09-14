"""Advisory EEZ/LME overlap flags; no region replacement or catch allocation.

Topology follows the straight lon/lat edges of the supplied GeoJSON. Area is
measured on WGS84 with an ellipsoidal cylindrical equal-area projection after
linear edge densification (maximum 0.05 degree segment). The geographic overlay
does NOT measure square degrees. Densification is internal, never exported.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path

import pandas as pd
from pyproj import CRS, Geod, Transformer
from shapely import get_coordinates, make_valid, segmentize
from shapely.affinity import translate
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, box, mapping, shape
from shapely.geometry.polygon import orient
from shapely.ops import transform, unary_union
from shapely.validation import explain_validity

from .spatial import unwrap_feature_collection

AREA_CRS = "+proj=cea +lat_ts=0 +lon_0=0 +datum=WGS84 +units=m +no_defs"
_TRANSFORM = Transformer.from_crs("EPSG:4326", CRS.from_proj4(AREA_CRS), always_xy=True)
_GEOD = Geod(ellps="WGS84")
_MAX_SEGMENT_DEGREES = 0.05
_AREA_REL_TOL = 1e-5
_AREA_ABS_TOL_KM2 = 1e-5


def _polygons(geometry):
    if isinstance(geometry, Polygon):
        if not geometry.is_empty:
            yield geometry
    elif isinstance(geometry, (MultiPolygon, GeometryCollection)):
        for part in geometry.geoms:
            yield from _polygons(part)


def _polygonal(geometry):
    parts = list(_polygons(geometry))
    if not parts:
        raise ValueError("Geometry has no positive-area polygonal component.")
    result = unary_union(parts)
    if result.is_empty or not result.is_valid or result.area <= 0:
        raise ValueError("Geometry repair did not yield a valid positive-area polygon.")
    return result


def _crosses_dateline(ring):
    points = list(ring.coords)
    return any(abs(a[0] - b[0]) > 180 and not (abs(a[1]) == 90 and a[1] == b[1])
               for a, b in zip(points, points[1:]))


def _unwrap_ring(ring):
    points = list(ring.coords)
    unwrapped = [points[0]]
    for point in points[1:]:
        lon, lat = point[:2]
        previous = unwrapped[-1][0]
        lon += 360 * round((previous - lon) / 360)
        unwrapped.append((lon, lat))
    if abs(unwrapped[-1][0] - unwrapped[0][0]) > 1e-8:
        raise ValueError("Ambiguous pole-winding dateline ring: explicit pole closure required.")
    return unwrapped


def prepare_geometry(geometry):
    """Return valid EPSG:4326 polygonal geometry and explicit repair audit.

Valid source shapes remain untouched. Wrapped antimeridian rings are unwrapped
by the shortest longitude step then split into [-180,180]. A +/-180 bridge at
the same pole is preserved, as it closes a polar cap rather than crossing land.
"""
    if not isinstance(geometry, (Polygon, MultiPolygon)) or geometry.is_empty:
        raise ValueError("Expected a nonempty polygonal EPSG:4326 geometry.")
    coords = get_coordinates(geometry)
    if not all(math.isfinite(float(v)) for row in coords for v in row):
        raise ValueError("Non-finite geographic coordinate.")
    if any(abs(float(x)) > 540 or abs(float(y)) > 90 for x, y in coords):
        raise ValueError("Geometry coordinates are outside EPSG:4326 domain.")
    invalid_before = not geometry.is_valid
    audit = {"geometry_repaired": invalid_before,
             "source_validity": explain_validity(geometry), "dateline_normalized": False,
             "source_vertex_count": len(coords), "source_bounds": list(geometry.bounds)}
    parts = list(_polygons(geometry))
    if any(abs(float(x)) > 180 for x,y in coords) or any(
            _crosses_dateline(ring) for p in parts for ring in [p.exterior, *p.interiors]):
        pieces = []
        for part in parts:
            crosses = any(_crosses_dateline(r) for r in [part.exterior, *part.interiors])
            if not crosses and part.bounds[0] >= -180 and part.bounds[2] <= 180:
                pieces.append(part if part.is_valid else _polygonal(make_valid(part)))
                continue
            exterior = _unwrap_ring(part.exterior) if crosses else list(part.exterior.coords)
            midpoint = sum(p[0] for p in exterior) / len(exterior)
            holes = []
            for ring in part.interiors:
                hole = _unwrap_ring(ring) if crosses else list(ring.coords)
                shift = 360 * round((midpoint - sum(p[0] for p in hole) / len(hole)) / 360)
                holes.append([(x+shift, y) for x, y in hole])
            unwrapped = Polygon(exterior, holes)
            if not unwrapped.is_valid:
                unwrapped = _polygonal(make_valid(unwrapped))
                audit["geometry_repaired"] = True
            left, _, right, _ = unwrapped.bounds
            for k in range(math.floor((left+180)/360), math.floor((right+180)/360)+1):
                clipped = unwrapped.intersection(box(-180+360*k,-90,180+360*k,90))
                pieces.extend(translate(p,xoff=-360*k) for p in _polygons(clipped))
        geometry = _polygonal(GeometryCollection(pieces))
        audit["dateline_normalized"] = True
    elif invalid_before:
        geometry = _polygonal(make_valid(geometry))
    if not geometry.is_valid or geometry.area <= 0:
        raise ValueError("Invalid or zero-area geometry after preparation.")
    audit["output_vertex_count"] = len(get_coordinates(geometry))
    audit["repair_method"] = "shapely.make_valid(linework); retain and union polygonal components" if audit["geometry_repaired"] else "none"
    return geometry, audit


def _geodesic_area_km2(geometry, step):
    # Split into <=90-degree longitude sectors before applying Geod, whose signed
    # polygon area is ambiguous for polygons larger than a hemisphere.
    total = 0.0
    for west in (-180,-90,0,90):
        if geometry.bounds[2] <= west or geometry.bounds[0] >= west+90:
            continue
        piece = geometry.intersection(box(west,-90,west+90,90))
        for part in _polygons(piece):
            dense = orient(segmentize(part, step), sign=1.0)
            value, _ = _GEOD.geometry_area_perimeter(dense)
            total += abs(value) / 1e6
    return total


def _area_audit(geometry):
    if geometry.is_empty or geometry.area == 0:
        return {"area_km2":0.0, "geodesic_area_km2":0.0, "area_relative_difference":0.0,
                "area_absolute_difference_km2":0.0, "max_segment_degrees":_MAX_SEGMENT_DEGREES}
    if not geometry.is_valid:
        raise ValueError("Area requested for invalid geometry.")
    for step in (_MAX_SEGMENT_DEGREES, _MAX_SEGMENT_DEGREES/10):
        dense = segmentize(geometry, step)
        equal_area = transform(_TRANSFORM.transform, dense).area / 1e6
        geodesic = _geodesic_area_km2(geometry, step)
        difference = abs(equal_area-geodesic)
        if not math.isfinite(equal_area) or equal_area <= 0:
            raise ValueError("Equal-area result is nonpositive or non-finite.")
        if difference <= max(_AREA_ABS_TOL_KM2, _AREA_REL_TOL*equal_area):
            return {"area_km2":equal_area, "geodesic_area_km2":geodesic,
                    "area_relative_difference":difference/equal_area,
                    "area_absolute_difference_km2":difference, "max_segment_degrees":step}
    raise ValueError(f"Equal-area/geodesic verification failed: {equal_area=} {geodesic=} km2.")


def area_km2(geometry):
    """Verified WGS84 ellipsoidal area of prepared geographic geometry, in km2."""
    return _area_audit(geometry)["area_km2"]


def _validate_thresholds(low, containment, prefer, review):
    if not all(math.isfinite(v) for v in (low, containment, prefer, review)):
        raise ValueError("Thresholds must be finite.")
    if not (0 <= low <= 1 and 0 <= containment <= 1 and 0 < review < prefer):
        raise ValueError("Fractions must be within [0,1] and 0 < review_ratio < prefer_ratio.")


def flags_for_pair(eez_area_km2, lme_area_km2, intersection_km2, *, containment_threshold=.9,
                   prefer_ratio=1.2, review_ratio=1.1):
    """Pure, unrounded policy comparisons; endpoints follow the specification."""
    _validate_thresholds(.1, containment_threshold, prefer_ratio, review_ratio)
    if not all(math.isfinite(v) for v in (eez_area_km2,lme_area_km2,intersection_km2)):
        raise ValueError("Areas must be finite.")
    if min(eez_area_km2,lme_area_km2) <= 0 or intersection_km2 < 0:
        raise ValueError("Region areas must be positive and intersection nonnegative.")
    fraction = intersection_km2/lme_area_km2
    ratio = eez_area_km2/lme_area_km2
    mostly = fraction >= containment_threshold
    return {"intersection_fraction_of_eez":intersection_km2/eez_area_km2,
            "intersection_fraction_of_lme":fraction, "eez_to_lme_area_ratio":ratio,
            "lme_mostly_contained":mostly,
            "flag_prefer_eez_candidate":mostly and ratio >= prefer_ratio,
            "flag_review_110_120":mostly and review_ratio <= ratio < prefer_ratio}


def flags_for_eez(lme_overlap_fraction, pairs, *, low_overlap_threshold=.1):
    if not math.isfinite(lme_overlap_fraction) or not 0 <= low_overlap_threshold <= 1:
        raise ValueError("Invalid overlap or threshold.")
    contained = [p for p in pairs if p["lme_mostly_contained"]]
    prefer = [p["lme_unit_id"] for p in pairs if p["flag_prefer_eez_candidate"]]
    review = [p["lme_unit_id"] for p in pairs if p["flag_review_110_120"]]
    return {"flag_add_low_lme_overlap":lme_overlap_fraction < low_overlap_threshold,
            "flag_prefer_eez_candidate":bool(prefer), "flag_review_110_120":bool(review),
            "prefer_eez_lme_ids":";".join(prefer), "review_110_120_lme_ids":";".join(review),
            "mostly_contained_lme_ids":";".join(p["lme_unit_id"] for p in contained),
            "mostly_contained_lme_count":len(contained),
            "max_lme_containment_fraction":max((p["intersection_fraction_of_lme"] for p in pairs),default=0),
            "max_eez_to_lme_area_ratio":max((p["eez_to_lme_area_ratio"] for p in pairs),default=0),
            "max_eez_to_mostly_contained_lme_area_ratio":max((p["eez_to_lme_area_ratio"] for p in contained),default=0)}


def _load_regions(path, prefix):
    collection = unwrap_feature_collection(json.loads(path.read_text(encoding="utf-8-sig")))
    collection = deepcopy(collection)
    regions, audits, seen = [], [], set()
    for feature in collection["features"]:
        properties = feature["properties"]
        region_id = int(properties["region_id"])
        if region_id in seen:
            raise ValueError(f"Duplicate {prefix} region ID {region_id}.")
        seen.add(region_id)
        unit_id = f"{prefix}_{region_id:03d}"
        geometry, audit = prepare_geometry(shape(feature["geometry"]))
        audit["previously_repaired"] = bool(properties.get("geometry_repaired",False))
        audit.update(unit_id=unit_id, name=properties["title"], **_area_audit(geometry))
        feature["geometry"] = mapping(geometry)
        properties.update(geometry_repaired=audit["geometry_repaired"] or audit["previously_repaired"],
                          dateline_normalized=audit["dateline_normalized"],unit_id=unit_id)
        regions.append(dict(unit_id=unit_id,name=properties["title"],region_id=region_id,
                            geometry=geometry,area_km2=audit["area_km2"],
                            geometry_repaired=properties["geometry_repaired"]))
        audits.append(audit)
    regions.sort(key=lambda r:r["region_id"])
    return collection, regions, audits


def build_eez_spatial_outputs(root: Path, *, low_overlap_threshold=.10, containment_threshold=.90,
                              prefer_ratio=1.20, review_ratio=1.10) -> dict:
    """Build every EEZ and advisory overlap tables; never alter LME/HS files."""
    _validate_thresholds(low_overlap_threshold,containment_threshold,prefer_ratio,review_ratio)
    root = Path(root)
    exported, eezs, eez_audits = _load_regions(root/"raw_data/SAU_downloads/eez_regions_spatial.json","EEZ")
    normalized_lmes, lmes, lme_audits = _load_regions(root/"spatial/LMEs.geojson","LME")
    normalized_hs, highseas, hs_audits = _load_regions(root/"spatial/HighSeas.geojson","HS")
    if not eezs or not lmes or not highseas:
        raise ValueError("EEZ, LME and High Seas inputs must each contain regions.")
    lme_union = unary_union([r["geometry"] for r in lmes])
    hs_union = unary_union([r["geometry"] for r in highseas])
    coverage_union = lme_union.union(hs_union)
    flag_rows, pair_rows = [], []
    for eez in eezs:
        geometry = eez["geometry"]
        eez_area = eez["area_km2"]
        local_pairs = []
        for lme in lmes:
            if not geometry.intersects(lme["geometry"]):
                continue
            overlap = geometry.intersection(lme["geometry"])
            if overlap.is_empty or overlap.area == 0:
                continue
            intersection = area_km2(overlap)
            if intersection > min(eez_area,lme["area_km2"]) * (1+2*_AREA_REL_TOL) + _AREA_ABS_TOL_KM2:
                raise ValueError("Intersection exceeds its denominator beyond numerical tolerance.")
            row = dict(eez_unit_id=eez["unit_id"],eez_name=eez["name"],
                       lme_unit_id=lme["unit_id"],lme_name=lme["name"],
                       eez_area_km2=eez_area,lme_area_km2=lme["area_km2"],intersection_km2=intersection)
            row.update(flags_for_pair(eez_area,lme["area_km2"],intersection,
                                      containment_threshold=containment_threshold,
                                      prefer_ratio=prefer_ratio,review_ratio=review_ratio))
            local_pairs.append(row)
        pair_rows.extend(local_pairs)
        lme_area = area_km2(geometry.intersection(lme_union))
        hs_area = area_km2(geometry.intersection(hs_union))
        uncovered = area_km2(geometry.difference(coverage_union))
        row = dict(unit_id=eez["unit_id"],eez_unit_id=eez["unit_id"],eez_name=eez["name"],
                   sau_region_id=eez["region_id"],area_km2=eez_area,
                   lme_union_intersection_km2=lme_area,lme_overlap_fraction_of_eez=lme_area/eez_area,
                   hs_union_intersection_km2=hs_area,hs_overlap_fraction_of_eez=hs_area/eez_area,
                   uncovered_by_lme_or_hs_km2=uncovered,geometry_repaired=eez["geometry_repaired"])
        row.update(flags_for_eez(lme_area/eez_area,local_pairs,low_overlap_threshold=low_overlap_threshold))
        flag_rows.append(row)
    audit_union = _area_audit(unary_union([r["geometry"] for r in eezs]))
    summed_area = sum(r["area_km2"] for r in eezs)
    all_audits = eez_audits+lme_audits+hs_audits
    validation = {
        "status":"passed", "eez_count":len(eezs),"lme_count":len(lmes),"highseas_count":len(highseas),
        "positive_eez_lme_pair_count":len(pair_rows),
        "thresholds":dict(low_overlap_threshold=low_overlap_threshold,containment_threshold=containment_threshold,
                          prefer_ratio=prefer_ratio,review_ratio=review_ratio),
        "flag_counts":{key:sum(row[key] for row in flag_rows) for key in
                       ("flag_add_low_lme_overlap","flag_prefer_eez_candidate","flag_review_110_120")},
        "area_method":"WGS84 ellipsoidal cylindrical equal-area; linear lon/lat edges densified <=0.05 degrees; geodesic cross-check in <=90-degree longitude sectors",
        "area_crs":AREA_CRS,"geometry_crs":"EPSG:4326","topology_method":"Geographic planar overlay of source GeoJSON linear edges; dateline normalized and pole closures preserved",
        "area_relative_tolerance":_AREA_REL_TOL,"area_absolute_tolerance_km2":_AREA_ABS_TOL_KM2,
        "max_source_area_relative_difference":max(a["area_relative_difference"] for a in all_audits),
        "new_eez_repair_count":sum(a["geometry_repaired"] for a in eez_audits),
        "dateline_normalized_unit_ids":[a["unit_id"] for a in all_audits if a["dateline_normalized"]],
        "normalized_overlay_exports":["eez_output/spatial/LMEs_normalized.geojson","eez_output/spatial/HighSeas_normalized.geojson"],
        "eez_sum_area_km2":summed_area,"eez_union_area_km2":audit_union["area_km2"],
        "eez_sum_minus_union_area_km2":summed_area-audit_union["area_km2"],
        "eez_union_area_audit":audit_union,
        "limitations":["Advisory flags only: no replacements, catch allocation or proration.",
                       "Source precision and boundary definitions govern results; repaired slivers and tiny positive overlaps are retained.",
                       "EEZ sum-minus-union is a multiplicity-weighted overlap audit, not a list of disputed boundaries.",
                       "Numeric thresholds use unrounded computed areas; borderline results require scientific review.",
                       "GeoJSON linear lon/lat edges are preserved, not reinterpreted as long geodesic boundary arcs."],
        "source_geometry_audits":all_audits,
    }
    # No output is written until all regions and all area checks succeed.
    spatial = root/"spatial"
    tables = root/"eez_output/tables"
    tables.mkdir(parents=True,exist_ok=True)
    spatial.mkdir(parents=True,exist_ok=True)
    (spatial/"EEZs.geojson").write_text(json.dumps(exported,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    normalized_dir = root/"eez_output/spatial"
    normalized_dir.mkdir(parents=True,exist_ok=True)
    for name,collection in (("LMEs_normalized.geojson",normalized_lmes),("HighSeas_normalized.geojson",normalized_hs)):
        (normalized_dir/name).write_text(json.dumps(collection,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    units = [dict(unit_id=r["unit_id"],name=r["name"],type="EEZ",sau_region="eez",sau_region_id=r["region_id"],
                  crs="EPSG:4326",geometry_repaired=r["geometry_repaired"]) for r in eezs]
    pd.DataFrame(units).to_csv(spatial/"eez_units.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(flag_rows).to_csv(tables/"eez_selection_flags.csv",index=False,encoding="utf-8-sig")
    pair_columns = ["eez_unit_id","eez_name","lme_unit_id","lme_name","eez_area_km2","lme_area_km2",
                    "intersection_km2","intersection_fraction_of_eez","intersection_fraction_of_lme",
                    "eez_to_lme_area_ratio","lme_mostly_contained","flag_prefer_eez_candidate","flag_review_110_120"]
    pd.DataFrame(pair_rows,columns=pair_columns).to_csv(tables/"eez_lme_intersections.csv",index=False,encoding="utf-8-sig")
    (tables/"spatial_validation.json").write_text(json.dumps(validation,indent=2,ensure_ascii=False),encoding="utf-8")
    return validation
