"""Deterministic LME-first whole-region spatial selection, never catch proration.

Objective: union area - penalty * (sum of region areas - union area).
All overlays retain normalized source lon/lat topology. Areas use the existing
WGS84 ellipsoidal cylindrical equal-area method; final overlays are independently
cross-checked by the existing geodesic area audit.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil

import pandas as pd
from shapely import STRtree, segmentize, transform as vector_transform
from shapely.geometry import GeometryCollection, mapping
from shapely.ops import unary_union

from .eez_spatial import AREA_CRS, _TRANSFORM, _area_audit, _load_regions, flags_for_pair


def quick_area_km2(geometry):
    """Equal-area measurement, reserving the slower geodesic check for outputs."""
    if geometry.is_empty or geometry.area == 0:
        return 0.0
    return vector_transform(segmentize(geometry, .05), _TRANSFORM.transform, interleaved=False).area / 1e6


def project_working_regions(regions):
    """Cached equal-area search approximation; original source polygons untouched."""
    return [dict(r, geometry=vector_transform(segmentize(r["geometry"], .05), _TRANSFORM.transform,
                                               interleaved=False)) for r in regions]


def coverage_metrics(regions, selected_ids, *, area_fn=quick_area_km2, source_union=None):
    """Exact polygon overlays; multiplicity excess differs from twice-covered area."""
    selected = [r for r in regions if r["unit_id"] in selected_ids]
    geometries = [r["geometry"] for r in selected]
    selected_union = unary_union(geometries)
    if source_union is None:
        source_union = unary_union([r["geometry"] for r in regions])
    overlaps = []
    tree = STRtree(geometries)
    for i, geometry in enumerate(geometries):
        for j in tree.query(geometry, predicate="intersects"):
            if j > i:
                overlap = geometry.intersection(geometries[j])
                if not overlap.is_empty and overlap.area > 0:
                    overlaps.append(overlap)
    overlaps = unary_union(overlaps)
    gaps = source_union.difference(selected_union)
    total = area_fn(source_union)
    covered = area_fn(selected_union)
    summed = sum(area_fn(g) for g in geometries)
    duplicated = summed - covered
    twice = area_fn(overlaps)
    gap = area_fn(gaps)
    metrics = dict(selected_count=len(selected), selected_counts_by_type=dict(Counter(r["region_type"] for r in selected)),
        source_union_area_km2=total, selected_union_area_km2=covered, selected_sum_area_km2=summed,
        sum_minus_union_area_km2=duplicated, area_covered_at_least_twice_km2=twice,
        gap_area_km2=gap, coverage_fraction=covered / total if total else 0,
        duplicate_excess_fraction_of_union=duplicated / covered if covered else 0,
        twice_covered_fraction_of_union=twice / covered if covered else 0,
        gap_fraction=gap / total if total else 0,
        union_plus_gap_minus_source_km2=covered + gap - total)
    return metrics, dict(selected_union=selected_union, source_union=source_union, overlaps=overlaps, gaps=gaps)


def replacement_pairs(regions, *, area_fn=quick_area_km2):
    """Retain both >=1.2 replacement candidates and 1.1–1.2 review flags."""
    pairs = []
    areas = {r["unit_id"]:area_fn(r["geometry"]) for r in regions if r["region_type"] in ("EEZ", "LME")}
    lmes = [r for r in regions if r["region_type"] == "LME"]
    for eez in regions:
        if eez["region_type"] != "EEZ":
            continue
        for lme in lmes:
            if not eez["geometry"].intersects(lme["geometry"]):
                continue
            intersection = area_fn(eez["geometry"].intersection(lme["geometry"]))
            flags = flags_for_pair(areas[eez["unit_id"]], areas[lme["unit_id"]], intersection)
            if flags["flag_prefer_eez_candidate"] or flags["flag_review_110_120"]:
                pairs.append(dict(eez_unit_id=eez["unit_id"], lme_unit_id=lme["unit_id"], **flags))
    return pairs


def audit_replacement_groups(regions, selected_ids, *, pairs=None, area_fn=quick_area_km2):
    """Explain every eligible group with actual geographic gained/lost coverage."""
    by_id = {r["unit_id"]:r for r in regions}
    areas = {uid:area_fn(r["geometry"]) for uid,r in by_id.items()}
    if pairs is None:
        pairs = replacement_pairs(regions, area_fn=area_fn)
    groups = {}
    for pair in pairs:
        if pair["flag_prefer_eez_candidate"]:
            groups.setdefault(pair["eez_unit_id"], set()).add(pair["lme_unit_id"])
    def subtract(geometry, ids):
        for uid in sorted(ids):
            if geometry.intersects(by_id[uid]["geometry"]):
                geometry = geometry.difference(by_id[uid]["geometry"])
        return geometry
    audits = []
    for uid, candidates in sorted(groups.items()):
        removed = candidates & set(selected_ids)
        if not removed:
            continue
        gain_shape = subtract(by_id[uid]["geometry"], selected_ids)
        loss_shape = subtract(unary_union([by_id[x]["geometry"] for x in sorted(removed)]), set(selected_ids)-removed)
        loss_shape = loss_shape.difference(by_id[uid]["geometry"])
        gained, lost = area_fn(gain_shape), area_fn(loss_shape)
        delta_union = gained-lost
        delta_sum = (0 if uid in selected_ids else areas[uid])-sum(areas[x] for x in removed)
        objective_change = 2*delta_union-delta_sum
        audits.append(dict(eez_unit_id=uid, eez_name=by_id[uid]["region_name"], removed_lme_ids=";".join(sorted(removed)),
            gained_coverage_km2=gained, lost_coverage_km2=lost, union_area_change_km2=delta_union,
            summed_area_change_km2=delta_sum, duplicate_area_change_km2=delta_sum-delta_union,
            objective_change_km2=objective_change, beneficial_at_penalty_1=objective_change > 1e-9))
    return audits


def select_regions(regions, *, penalty=1.0, area_fn=quick_area_km2, pairs=None, progress=None):
    """LME/HS seed, beneficial approved replacements, greedy EEZ additions.

Original LME units are protected except approved replacement groups; HS units
are nonpreferred and may be removed or re-added when beneficial. A
replacement EEZ stays protected to preserve the justification for excluded LMEs.
EEZ addition stops when unique added area <= penalty * new duplicated area.
Deterministic ties follow lexical unit ID. This is a heuristic, not global proof.
"""
    if not math.isfinite(penalty) or penalty < 0:
        raise ValueError("Penalty must be finite and nonnegative.")
    regions = sorted(regions, key=lambda r: r["unit_id"])
    by_id = {r["unit_id"]: r for r in regions}
    if len(by_id) != len(regions):
        raise ValueError("Duplicate candidate unit ID.")
    areas = {uid: area_fn(r["geometry"]) for uid, r in by_id.items()}
    if any(a <= 0 or not math.isfinite(a) for a in areas.values()):
        raise ValueError("Every candidate must have finite positive area.")
    selected = {uid for uid, r in by_id.items() if r["region_type"] in ("LME", "HS")}
    protected = {uid for uid in selected if by_id[uid]["region_type"] == "LME"}
    reasons = {uid: "LME preferred whole-region baseline" if by_id[uid]["region_type"] == "LME"
               else "High Seas baseline" for uid in selected}
    actions = []
    def union(ids):
        return unary_union([by_id[uid]["geometry"] for uid in sorted(ids)])
    all_ids = list(by_id)
    tree = STRtree([by_id[uid]["geometry"] for uid in all_ids])
    neighbors = {uid:{all_ids[int(i)] for i in tree.query(by_id[uid]["geometry"], predicate="intersects")} - {uid}
                 for uid in all_ids}
    unique_cache = {}
    def difference_regions(geometry, ids):
        for other in sorted(ids):
            geometry = geometry.difference(by_id[other]["geometry"])
            if geometry.is_empty:
                break
        return geometry
    def unique_geometry(uid):
        key = uid, frozenset(neighbors[uid] & selected)
        if key not in unique_cache:
            unique_cache[key] = difference_regions(by_id[uid]["geometry"], key[1])
        return unique_cache[key]
    if pairs is None:
        pairs = replacement_pairs(regions, area_fn=area_fn)
    eligibility = {}
    for pair in pairs:
        if pair["flag_prefer_eez_candidate"]:
            eligibility.setdefault(pair["eez_unit_id"], set()).add(pair["lme_unit_id"])
    # Coverage-only sensitivity retains all LMEs: replacing a partly-contained LME
    # can otherwise introduce a gap that no remaining EEZ can restore.
    if penalty > 0:
        while True:
            proposals = []
            for uid, eligible_lmes in sorted(eligibility.items()):
                removed = eligible_lmes & selected
                if not removed or uid in selected:
                    continue
                added_shape = unique_geometry(uid)
                removed_neighbors = set().union(*(neighbors[x] for x in removed))
                lost_shape = difference_regions(union(removed), (selected - removed) & removed_neighbors).difference(by_id[uid]["geometry"])
                delta_union = area_fn(added_shape) - area_fn(lost_shape)
                delta_sum = areas[uid] - sum(areas[x] for x in removed)
                score = (1 + penalty) * delta_union - penalty * delta_sum
                if score > max(1e-9, 1e-12 * areas[uid]):
                    proposals.append((score, uid, removed, lost_shape, delta_union, delta_sum))
            if not proposals:
                break
            score, uid, removed, lost_shape, delta_union, delta_sum = sorted(proposals, key=lambda x: (-x[0], x[1]))[0]
            selected.difference_update(removed)
            selected.add(uid)
            protected.difference_update(removed)
            protected.add(uid)
            for old in removed:
                reasons[old] = f"Excluded: approved >=90% containment and >=1.2 area-ratio replacement by {uid}"
            reasons[uid] = "Approved EEZ replacement of " + ";".join(sorted(removed)) + "; improves coverage-overlap objective"
            actions.append(dict(action="replace_lmes", added=uid, removed=sorted(removed), objective_gain_km2=score,
                union_area_change_km2=delta_union, duplicate_area_change_km2=delta_sum-delta_union))
            if progress:
                progress(f"Replacement {uid}: removed {len(removed)} LMEs; objective gain {score:,.0f} km2")
    available = {uid for uid, r in by_id.items() if r["region_type"] == "EEZ" and uid not in selected}
    unique_shapes = {uid: unique_geometry(uid) for uid in available}
    unique_areas = {uid: area_fn(g) for uid, g in unique_shapes.items()}
    while available:
        scores = {uid: (1 + penalty) * unique_areas[uid] - penalty * areas[uid] for uid in available}
        uid = min(available, key=lambda x: (-scores[x], x))
        tolerance = 0 if penalty == 0 else max(1e-9, 1e-12 * areas[uid])
        if scores[uid] <= tolerance:
            break
        added_shape = unique_shapes[uid]
        added_area = unique_areas[uid]
        duplicate = areas[uid] - added_area
        selected.add(uid)
        available.remove(uid)
        reasons[uid] = f"EEZ addition: unique added coverage exceeds {penalty:g} x new duplicated area"
        actions.append(dict(action="add_eez", added=uid, removed=[], objective_gain_km2=scores[uid],
                            union_area_change_km2=added_area, duplicate_area_change_km2=duplicate))
        if progress and len(actions) % 20 == 0:
            progress(f"Greedy addition progress: {len(selected)} selected whole regions")
        for other in available:
            if unique_shapes[other].intersects(added_shape):
                unique_shapes[other] = unique_shapes[other].difference(added_shape)
                unique_areas[other] = area_fn(unique_shapes[other])
    # Converge over additions, nonpreferred removals and one-for-one EEZ swaps.
    # A swap can improve a greedy seed even when neither single action helps.
    removals = swaps = 0
    nonpreferred_ids = {uid for uid in by_id if by_id[uid]["region_type"] != "LME"}
    while True:
        outside = nonpreferred_ids - selected
        unique_selected = {uid:unique_geometry(uid) for uid in sorted(selected - protected)}
        unique_outside = {uid:unique_geometry(uid) for uid in sorted(outside)}
        lost_areas = {uid:area_fn(g) for uid,g in unique_selected.items()}
        gain_areas = {uid:area_fn(g) for uid,g in unique_outside.items()}
        choices = []
        for uid, lost in lost_areas.items():
            gain = penalty * areas[uid] - (1 + penalty) * lost
            if gain > max(1e-9, 1e-12 * areas[uid]) or lost == 0:
                action = "remove_eez" if by_id[uid]["region_type"] == "EEZ" else "remove_high_seas"
                choices.append((gain, action, uid, None, -lost, -areas[uid]))
        for uid, gained in gain_areas.items():
            gain = (1 + penalty) * gained - penalty * areas[uid]
            if gain > (0 if penalty == 0 else max(1e-9, 1e-12 * areas[uid])):
                action = "add_eez" if by_id[uid]["region_type"] == "EEZ" else "readd_high_seas"
                choices.append((gain, action, None, uid, gained, areas[uid]))
        if not choices:
            for old, unique in unique_selected.items():
                for new in sorted(neighbors[old] & outside):
                    lost_after_swap = area_fn(unique.difference(by_id[new]["geometry"]))
                    delta_union = gain_areas[new] - lost_after_swap
                    delta_sum = areas[new] - areas[old]
                    gain = (1 + penalty) * delta_union - penalty * delta_sum
                    if gain > max(1e-9, 1e-12 * max(areas[old], areas[new])):
                        action = "swap_eez" if by_id[old]["region_type"] == by_id[new]["region_type"] == "EEZ" else "swap_nonpreferred"
                        choices.append((gain, action, old, new, delta_union, delta_sum))
        if not choices:
            break
        gain, action, old, new, delta_union, delta_sum = sorted(choices, key=lambda x: (-x[0], x[1], x[2] or "", x[3] or ""))[0]
        if old:
            selected.remove(old)
            reasons[old] = "Excluded: later coverage made this nonpreferred whole region objective-redundant" if not new else f"Excluded: improving whole-region swap to {new}"
        if new:
            selected.add(new)
            reasons[new] = f"Improving whole-region swap from {old}" if old else f"Region addition after local improvement: coverage exceeds {penalty:g} x duplicated area"
        actions.append(dict(action=action, added=new, removed=[old] if old else [], objective_gain_km2=gain,
                            union_area_change_km2=delta_union, duplicate_area_change_km2=delta_sum-delta_union))
        removals += int(action == "remove_eez")
        swaps += int(action in ("swap_eez", "swap_nonpreferred"))
        if progress:
            progress(f"Local improvement {action}: {old} -> {new}; objective gain {gain:,.6f} km2")
    for uid in by_id:
        reasons.setdefault(uid, "Excluded: added coverage does not exceed overlap penalty; LME-first preference retained")
    return dict(selected_ids=selected, protected_ids=protected, reasons=reasons, actions=actions,
                penalty=penalty, converged=True, redundant_eez_removals=removals, improving_eez_swaps=swaps)


def _write_geojson(path, features):
    path.write_text(json.dumps(dict(type="FeatureCollection", features=features), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def build_selection_outputs(root: Path, *, expected_count=366, penalties=(1, 5, 0), progress=print):
    root = Path(root)
    regions, features, source_files = [], {}, []
    for filename, kind in (("EEZs.geojson", "EEZ"), ("LMEs_normalized.geojson", "LME"), ("HighSeas_normalized.geojson", "HS")):
        path = root / "eez_output/spatial" / filename
        if not path.exists() and kind == "EEZ":
            path = root / "spatial" / filename
        collection, loaded, audits = _load_regions(path, kind)
        source_files.append(path)
        for r in loaded:
            regions.append(dict(unit_id=r["unit_id"], region_name=r["name"], region_type=kind, geometry=r["geometry"], area_km2=r["area_km2"]))
        features.update({f["properties"]["unit_id"]:f for f in collection["features"]})
        if progress:
            progress(f"Loaded and area-verified {len(loaded)} {kind} polygons")
    if expected_count is not None and len(regions) != expected_count:
        raise ValueError(f"Expected {expected_count} candidates, found {len(regions)}")
    tables, spatial = root / "history_output/tables", root / "history_output/spatial"
    tables.mkdir(parents=True, exist_ok=True)
    spatial.mkdir(parents=True, exist_ok=True)
    if progress:
        progress("Computing approved replacement flags")
    existing_pairs = root / "eez_output/tables/eez_lme_intersections.csv"
    if existing_pairs.exists():
        pair_frame = pd.read_csv(existing_pairs)
        pairs = pair_frame[pair_frame.flag_prefer_eez_candidate | pair_frame.flag_review_110_120].to_dict("records")
    else:
        pairs = replacement_pairs(regions)
    if progress:
        progress("Caching equal-area working polygons and computing source union")
    working_regions = project_working_regions(regions)
    source_union = unary_union([r["geometry"] for r in regions])
    baseline_ids = {r["unit_id"] for r in regions if r["region_type"] != "EEZ"}
    scenarios = []
    scenario_results = {}
    chosen = None
    for penalty in penalties:
        name = "practical_lme_first" if penalty == 1 else "maximum_coverage" if penalty == 0 else f"strict_overlap_{penalty:g}"
        if progress:
            progress(f"Selecting scenario {name}")
        result = select_regions(working_regions, penalty=penalty, area_fn=lambda g:g.area / 1e6, pairs=pairs, progress=progress)
        if penalty == 1:
            # Publish fixed membership before slower sensitivity and final overlays.
            # Final export below adds the audited marginal geometry columns.
            early_rows = [dict(unit_id=r["unit_id"], region_name=r["region_name"], region_type=r["region_type"],
                area_km2=r["area_km2"], selected=r["unit_id"] in result["selected_ids"],
                selection_reason=result["reasons"][r["unit_id"]]) for r in regions]
            early = pd.DataFrame(early_rows).sort_values("unit_id")
            early.to_csv(tables / "selection_candidates.csv", index=False, encoding="utf-8-sig")
            early[early.selected].to_csv(tables / "selected_regions.csv", index=False, encoding="utf-8-sig")
            if progress:
                progress(f"Practical membership exported: {len(result['selected_ids'])} units")
        metrics, overlays = coverage_metrics(regions, result["selected_ids"], source_union=source_union)
        scenarios.append(dict(scenario=name, overlap_penalty=penalty, recommended=penalty == 1, **metrics))
        scenario_results[name] = dict(selected_unit_ids=sorted(result["selected_ids"]), actions=result["actions"],
            converged=result["converged"], redundant_eez_removals=result["redundant_eez_removals"], improving_eez_swaps=result["improving_eez_swaps"])
        if progress:
            progress(f"{name}: {metrics['selected_count']} units, coverage {metrics['coverage_fraction']:.6%}, duplicate excess {metrics['duplicate_excess_fraction_of_union']:.6%}, twice-covered {metrics['twice_covered_fraction_of_union']:.6%}")
        pd.DataFrame([{k:json.dumps(v) if isinstance(v,dict) else v for k,v in row.items()} for row in scenarios]).to_csv(tables / "selection_scenarios.csv", index=False, encoding="utf-8-sig")
        if penalty == 1:
            chosen = result, metrics, overlays
    baseline, _ = coverage_metrics(regions, baseline_ids, source_union=source_union)
    scenarios.insert(0, dict(scenario="lme_hs_baseline", overlap_penalty=None, recommended=False, **baseline))
    pd.DataFrame([{k:json.dumps(v) if isinstance(v,dict) else v for k,v in row.items()} for row in scenarios]).to_csv(tables / "selection_scenarios.csv", index=False, encoding="utf-8-sig")
    if chosen is None:
        raise ValueError("The practical penalty=1 scenario is required.")
    result, metrics, overlays = chosen
    by_id = {r["unit_id"]:r for r in regions}
    selected_ids = result["selected_ids"]
    rows = []
    for uid, r in sorted(by_id.items()):
        selected = uid in selected_ids
        context_ids = selected_ids - {uid}
        unique_shape = r["geometry"]
        for other in sorted(context_ids):
            if by_id[other]["geometry"].intersects(unique_shape):
                unique_shape = unique_shape.difference(by_id[other]["geometry"])
        unique = quick_area_km2(unique_shape)
        overlap = r["area_km2"] - unique
        relevant = [p for p in pairs if p["eez_unit_id"] == uid]
        row = dict(unit_id=uid, region_name=r["region_name"], region_type=r["region_type"], area_km2=r["area_km2"],
            selected=selected, selection_reason=result["reasons"][uid], unique_area_vs_other_selected_km2=unique,
            overlap_area_with_other_selected_km2=overlap, overlap_fraction_with_other_selected=overlap/r["area_km2"],
            marginal_objective_km2=unique-overlap,
            replacement_eligible_lme_ids=";".join(sorted(p["lme_unit_id"] for p in relevant if p["flag_prefer_eez_candidate"])),
            review_110_120_lme_ids=";".join(sorted(p["lme_unit_id"] for p in relevant if p["flag_review_110_120"])))
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(tables / "selection_candidates.csv", index=False, encoding="utf-8-sig")
    df[df.selected].to_csv(tables / "selected_regions.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(pairs).to_csv(tables / "selection_replacement_pairs.csv", index=False, encoding="utf-8-sig")
    group_review = audit_replacement_groups(regions, selected_ids, pairs=pairs)
    pd.DataFrame(group_review).to_csv(tables / "selection_replacement_groups.csv", index=False, encoding="utf-8-sig")
    audits = {name:_area_audit(geometry) for name, geometry in overlays.items()}
    tolerance = max(1e-5, metrics["source_union_area_km2"] * 1e-5)
    if abs(metrics["union_plus_gap_minus_source_km2"]) > tolerance:
        raise ValueError("Selected union + gaps does not equal source union.")
    if metrics["area_covered_at_least_twice_km2"] > metrics["sum_minus_union_area_km2"] + tolerance:
        raise ValueError("Twice-covered area exceeds multiplicity-weighted duplicated area.")
    output = dict(created_at_utc=datetime.now(timezone.utc).isoformat(), **metrics,
        recommended_scenario="practical_lme_first", candidate_count=len(regions),
        candidate_counts_by_type=dict(Counter(r["region_type"] for r in regions)),
        membership_fixed_across_years=True, ppr_coverage_fraction=None,
        objective="Maximize union_km2 - penalty * (sum_region_km2 - union_km2), subject to LME preference and approved replacement exceptions; nonpreferred EEZ/HS units can be removed or re-added",
        practical_overlap_penalty=1, replacement_containment_threshold=.9, replacement_area_ratio_threshold=1.2,
        review_area_ratio_interval="[1.1, 1.2)", area_crs=AREA_CRS,
        topology_method="Exact Shapely geographic planar overlay of normalized source GeoJSON linear lon/lat edges; no rasterization or polygon simplification",
        area_method="WGS84 ellipsoidal cylindrical equal-area; linear geographic edges densified <=0.05 degrees; final geodesic cross-check",
        working_search_method="Cached WGS84 equal-area projected polygons after <=0.05-degree geographic densification; projected overlays are a numerical working approximation used only to select whole regions. All reported final union/gap/overlap metrics use original normalized geographic polygon overlays.",
        replacement_flags_source=str(existing_pairs.relative_to(root)) if existing_pairs.exists() else "Recomputed from input geographic polygons",
        replacement_flags_sha256=hashlib.sha256(existing_pairs.read_bytes()).hexdigest() if existing_pairs.exists() else None,
        converged_search_neighborhood="Single additions/removals and one-for-one swaps among nonpreferred EEZ/High Seas units, after initial eligible LME replacement phase",
        post_selection_replacement_review=group_review,
        post_selection_replacement_review_file="tables/selection_replacement_groups.csv",
        lme_priority_review="Retain the higher-coverage LME-priority recommendation; marginal post-addition alternatives are disclosed, not automatically substituted.",
        global_optimality_certified=False,
        limitations=["Coverage denominator is the union of the 366 available source polygons, not an independently defined global ocean mask.",
            "Geographic coverage is not catch or PPR coverage; no claim of certified 99% PPR coverage is possible.",
            "Whole-region PPR sums retain unknown duplicated catch/PPR wherever selected polygons overlap; overlap area cannot quantify the PPR duplication.",
            "No catch/PPR clipping, subtraction, area proration, or uniform-within-region assumption is used.",
            "Greedy selection is deterministic but is not a certified global mathematical optimum; preferred LMEs and accepted replacement EEZs remain protected, while High Seas units are removable/re-addable.",
            "Approved LME replacement groups are considered in the initial phase. Post-addition replacement alternatives are audited separately so that small objective gains do not silently override the preferred LME structure.",
            "Tiny source-boundary slivers and positive overlaps are retained; areas are numerical equal-area measurements, not mathematically exact real numbers."],
        scenarios=scenarios, scenario_details=scenario_results,
        validation=dict(status="passed", final_overlay_area_audits=audits, area_identity_tolerance_km2=tolerance,
            all_geometries_valid=all(g.is_valid for g in overlays.values()),
            selected_ids_unique=len(selected_ids)==len(df[df.selected]),
            source_files=[dict(path=str(p.relative_to(root)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in source_files]))
    (tables / "selection_metrics.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    selected_features = []
    for row in rows:
        if row["selected"]:
            feature = deepcopy(features[row["unit_id"]])
            feature["properties"].update(row)
            selected_features.append(feature)
    _write_geojson(spatial / "selected_regions.geojson", selected_features)
    for name in ("gaps", "overlaps", "selected_union", "source_union"):
        _write_geojson(spatial / f"{name}.geojson", [dict(type="Feature", properties=dict(layer=name,
            area_km2=audits[name]["area_km2"]), geometry=mapping(overlays[name]))])
    for path in source_files:
        shutil.copy2(path, spatial / path.name)
    return output
