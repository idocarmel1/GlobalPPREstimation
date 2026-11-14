"""Build the explicitly authorized pooled-detritus variant; never run a solver.

Only this variant's model, notes, input provenance and aggregation ledger are
written. The source model and regional/project workbooks are read-only inputs.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from collections import Counter
from decimal import Decimal
from pathlib import Path


SOURCE_ID = "Piroddi_2022_Mediterranean_1995"
TARGET_ID = "Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114"
SOURCE_SHA256 = "f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e"
POOL_NAME = "Pooled Discards and Detritus"
MISSING = "-9999"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path, directory: Path) -> str:
    return os.path.relpath(path, directory).replace("\\", "/")


def decimal_sum(values: list[str]) -> str:
    """Add exact serialized values only when every operand is known."""
    if any(value == MISSING for value in values):
        return MISSING
    result = sum((Decimal(value) for value in values), Decimal(0))
    return format(result, "f")


def masks(groups: list[dict]) -> list[dict]:
    result = []
    for group in groups:
        result.append({
            "group_seq": group["group_seq"],
            "missing_scalar_fields": sorted(
                key for key, value in group.items() if value == MISSING
            ),
            "missing_diet_proportion_prey_ids": [
                row["prey_seq"] for row in group["diet_descr"]["diet"]
                if row["proportion"] == MISSING
            ],
            "missing_detritus_fate_prey_ids": [
                row["prey_seq"] for row in group["diet_descr"]["diet"]
                if row["detritus_fate"] == MISSING
            ],
        })
    return result


def merge_diet(group: dict) -> tuple[list[dict], dict]:
    rows = group["diet_descr"]["diet"]
    by_id = {row["prey_seq"]: row for row in rows}
    assert len(by_id) == len(rows), "Duplicate original diet IDs"
    assert set(by_id) >= {"70", "71"}
    old_70, old_71 = by_id["70"], by_id["71"]
    assert set(old_70) == set(old_71) == {
        "prey_seq", "proportion", "detritus_fate"
    }
    merged = {
        "prey_seq": "70",
        "proportion": decimal_sum([
            old_70["proportion"], old_71["proportion"]
        ]),
        "detritus_fate": "1",
    }
    new_rows = [
        copy.deepcopy(merged if row["prey_seq"] == "70" else row)
        for row in rows if row["prey_seq"] != "71"
    ]
    old_known_sum = sum(
        (Decimal(row["proportion"]) for row in rows
         if row["proportion"] != MISSING), Decimal(0)
    )
    new_known_sum = sum(
        (Decimal(row["proportion"]) for row in new_rows
         if row["proportion"] != MISSING), Decimal(0)
    )
    assert old_known_sum == new_known_sum
    return new_rows, {
        "source_group_seq": group["group_seq"],
        "source_group_name": group["group_name"],
        "source_entries": copy.deepcopy([old_70, old_71]),
        "derived_entry": copy.deepcopy(merged),
        "source_known_diet_proportion_sum": str(old_known_sum),
        "derived_known_diet_proportion_sum": str(new_known_sum),
        "diet_import_preserved": group["diet_imp"],
        "all_other_diet_entries_exact": True,
        "normalization_applied": False,
        "routing_is_authorized_assumption_not_published_measurement": True,
    }


def write_once_or_identical(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise RuntimeError(f"Refusing to replace a differing existing file: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def main() -> None:
    model_dir = Path(__file__).resolve().parents[4]
    assert model_dir.name == TARGET_ID
    source_path = model_dir.parent / SOURCE_ID / "model.json"
    source_bytes = source_path.read_bytes()
    assert sha(source_bytes) == SOURCE_SHA256, "Source identity changed"
    source = json.loads(source_bytes.decode("utf-8-sig"))
    assert set(source) == {"group", "source_metadata", "source_fisheries"}
    original = source["group"]
    assert [g["group_seq"] for g in original] == [str(i) for i in range(1, 72)]
    assert original[69]["group_name"] == "Discards"
    assert original[70]["group_name"] == "Detritus"
    assert all(g["pp"] == "2" for g in original[69:])
    assert all(row["detritus_fate"] == MISSING
               for g in original for row in g["diet_descr"]["diet"])

    derived = copy.deepcopy(source)
    diet_changes = []
    for group in derived["group"][:69]:
        group["diet_descr"]["diet"], change = merge_diet(group)
        diet_changes.append(change)

    pool = copy.deepcopy(original[69])
    pool["group_name"] = POOL_NAME
    pool["group_seq"] = "70"
    for field in ["biomass", "biomass_habitat_area"]:
        pool[field] = decimal_sum([g[field] for g in original[69:]])
        assert pool[field] == "0.51582324"
    pool["ee"] = MISSING
    pool["ee_input"] = "false"
    pool["taxon_descr"] = (
        "Derived nonliving pool combining source groups 70 Discards and 71 "
        "Detritus; no taxonomic membership applies."
    )
    pool["source_landings"] = decimal_sum(
        [g["source_landings"] for g in original[69:]]
    )
    pool["source_discards"] = decimal_sum(
        [g["source_discards"] for g in original[69:]]
    )
    pool["diet_descr"]["diet"], pool_diet_change = merge_diet(original[69])
    # Neither original nonfeeding pool has measured dietary proportions.
    assert original[69]["diet_descr"] == original[70]["diet_descr"]
    assert pool["diet_descr"]["diet"][0]["proportion"] == MISSING
    derived["group"] = derived["group"][:69] + [pool]

    fisheries = derived["source_fisheries"]
    assert len(fisheries["fleets"]) == 37
    assert "70" not in fisheries["landings"] and "71" not in fisheries["landings"]
    old_discard_rows = {
        key: copy.deepcopy(fisheries["discards"][key]) for key in ["70", "71"]
    }
    assert all(set(row) == set(fisheries["fleets"]) for row in old_discard_rows.values())
    assert all(value == "0" for row in old_discard_rows.values() for value in row.values())
    fisheries["discards"]["70"] = {
        fleet: decimal_sum([old_discard_rows[key][fleet] for key in ["70", "71"]])
        for fleet in fisheries["fleets"]
    }
    del fisheries["discards"]["71"]

    old_metadata = copy.deepcopy(derived["source_metadata"])
    derived["source_metadata"]["model_id"] = TARGET_ID
    derived["source_metadata"]["routing"] = (
        "Not reported by source. Derived assumption authorized 14 November 2026: "
        "all detritus-directed mortality/egestion routes 100% to pooled group 70; "
        "retain the separate runtime EE-floor external sink."
    )
    derived["source_metadata"]["missing_landing_groups"] = list(dict.fromkeys(
        70 if value == 71 else value
        for value in old_metadata["missing_landing_groups"]
    ))
    removed_admin = {
        key: derived["source_metadata"].pop(key)
        for key in ["selected", "production_eligible"]
        if key in derived["source_metadata"]
    }

    # Verify every retained scalar, prey identity and fleet value independently
    # of the summary flags placed in the ledger.
    for old, new in zip(original[:69], derived["group"][:69]):
        assert {k: v for k, v in old.items() if k != "diet_descr"} == {
            k: v for k, v in new.items() if k != "diet_descr"
        }
        assert [r for r in old["diet_descr"]["diet"] if int(r["prey_seq"]) < 70] == [
            r for r in new["diet_descr"]["diet"] if int(r["prey_seq"]) < 70
        ]
    assert fisheries["landings"] == source["source_fisheries"]["landings"]
    for seq in map(str, range(1, 70)):
        assert fisheries["discards"][seq] == source["source_fisheries"]["discards"][seq]
    assert fisheries["fleets"] == source["source_fisheries"]["fleets"]
    assert fisheries["units"] == source["source_fisheries"]["units"]
    assert pool["source_landings"] == MISSING and pool["source_discards"] == "0"
    assert [g["group_seq"] for g in derived["group"]] == [str(i) for i in range(1, 71)]
    for group in derived["group"]:
        rows = group["diet_descr"]["diet"]
        assert len({r["prey_seq"] for r in rows}) == len(rows)
        assert all(1 <= int(r["prey_seq"]) <= 70 for r in rows)
        assert next(r for r in rows if r["prey_seq"] == "70")["detritus_fate"] == "1"

    model_bytes = (json.dumps(derived, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    source_model_hash_after = sha(source_path.read_bytes())
    assert source_model_hash_after == SOURCE_SHA256
    ledger_path = model_dir / "results/diagnostics/pooled_20261114/aggregation_ledger.json"
    ledger = {
        "schema_version": 1,
        "date": "2026-11-14",
        "source_model_id": SOURCE_ID,
        "derived_model_id": TARGET_ID,
        "source_model": relative(source_path, ledger_path.parent),
        "source_sha256_before": SOURCE_SHA256,
        "source_sha256_after": source_model_hash_after,
        "derived_model": relative(model_dir / "model.json", ledger_path.parent),
        "derived_model_sha256": sha(model_bytes),
        "authorization": {
            "request": "Separate pooled Discards70+Detritus71 model and diagnostics.",
            "routing": "100% of detritus-directed flows to the pooled compartment, including pool self-routing.",
            "external_sink": "Retain the separate EE-floor external nonfishery sink; do not route it into detritus.",
            "ee_runtime": "Record any authorized runtime live-group EE update as 1 - detritus-directed M0 / P separately; source live EE values remain unchanged here.",
            "scope_of_this_builder": "Canonical aggregation and evidence only; no solver, selection, review registration or publication.",
        },
        "crosswalk": [
            {"source_group_seq": g["group_seq"], "source_group_name": g["group_name"],
             "derived_group_seq": "70" if int(g["group_seq"]) >= 70 else g["group_seq"],
             "derived_group_name": POOL_NAME if int(g["group_seq"]) >= 70 else g["group_name"]}
            for g in original
        ],
        "counts": {
            "source_groups": 71, "derived_groups": 70,
            "source_detrital_groups": 2, "derived_detrital_groups": 1,
            "unchanged_non_detrital_group_scalar_records": 69,
            "retained_fleets": 37,
            "source_fleet_landings_group_records": len(source["source_fisheries"]["landings"]),
            "derived_fleet_landings_group_records": len(fisheries["landings"]),
            "source_fleet_discards_group_records": len(source["source_fisheries"]["discards"]),
            "derived_fleet_discards_group_records": len(fisheries["discards"]),
            "consumer_rows_with_positive_pooled_diet": sum(
                Decimal(c["derived_entry"]["proportion"]) > 0
                for c in diet_changes if c["derived_entry"]["proportion"] != MISSING
            ),
        },
        "non_detrital_diet_changes": diet_changes,
        "source_detrital_group_records": copy.deepcopy(original[69:]),
        "pooled_group_record": copy.deepcopy(pool),
        "pooled_group_changes_from_source_70": {
            key: {"before": original[69].get(key), "after": pool.get(key)}
            for key in sorted(set(original[69]) | set(pool))
            if original[69].get(key) != pool.get(key)
        },
        "pool_diet_change": pool_diet_change,
        "pool_field_policy": {
            "biomass_and_biomass_habitat_area": "Exact sum in shared t/km2 basis: 0.07582324 + 0.44 = 0.51582324.",
            "ee": "Unknown, input flag false. Published values retained in source records; neither averaging nor biomass weighting is justified.",
            "tl_and_pp": "Common values TL=1 and pp=2 retained without averaging.",
            "other_equal_fields": "Exact common serialized values retained, including unknown BA/import/export and flags.",
            "missingness": "Unknown plus unknown stays -9999. No unknown source landings or diet proportions are replaced with zero.",
        },
        "fisheries_change": {
            "original_detrital_discard_rows": old_discard_rows,
            "derived_detrital_discard_row": copy.deepcopy(fisheries["discards"]["70"]),
            "landings": "Both detrital source groups absent; pooled landings remain absent and scalar source_landings remains -9999.",
            "all_living_fleet_values_and_text_exact": True,
            "fleet_discards_return_added_by_builder": False,
            "one_time_return_requirement": "Runtime may return living fishery discards to the sole detritus pool once; these are not additional source_discards for group70 or additional biomass.",
        },
        "metadata_changes": {
            key: {"before": old_metadata.get(key), "after": derived["source_metadata"].get(key),
                  "present_after": key in derived["source_metadata"]}
            for key in sorted(set(old_metadata) | set(derived["source_metadata"]))
            if old_metadata.get(key) != derived["source_metadata"].get(key)
            or (key in old_metadata) != (key in derived["source_metadata"])
        },
        "removed_administrative_source_metadata": removed_admin,
        "source_missing_masks": masks(original),
        "derived_missing_masks": masks(derived["group"]),
        "review_and_selection": "New derived model; no researcher review, selection, prior diagnostics or approvals inherited.",
        "scientific_limit": "Retaining exact original records permits provenance reconstruction; collapsing two compartments is not an assertion of equivalent two-pool dynamics or published routing.",
    }
    provenance_path = model_dir / "inputs/provenance.json"
    provenance = {
        "schema_version": 1,
        "model_id": TARGET_ID,
        "derivation_date": "2026-11-14",
        "source": {"model_id": SOURCE_ID, "path": relative(source_path, provenance_path.parent),
                   "sha256": SOURCE_SHA256},
        "derived_model_sha256": sha(model_bytes),
        "aggregation_ledger": relative(ledger_path, provenance_path.parent),
        "builder": relative(Path(__file__).resolve(), provenance_path.parent),
        "builder_sha256": sha(Path(__file__).read_bytes()),
        "new_model_has_no_inherited_researcher_approval": True,
        "source_administrative_metadata_retained_as_history": removed_admin,
        "authorized_assumptions": ledger["authorization"],
        "canonical_build_only": True,
    }
    notes = f"""# {TARGET_ID}

## Source identity

This is a separate, explicitly authorized derived model of the [canonical 71-group model](../{SOURCE_ID}/model.json), SHA-256 `{SOURCE_SHA256}`. The original model and its review remain unchanged. The original source is Piroddi et al. (2022), Mediterranean Sea baseline for 1995 (supplement label: 1990s). Source values and exact aggregation changes are retained in the [aggregation ledger](results/diagnostics/pooled_20261114/aggregation_ledger.json).

## Modeled period and area

The source baseline remains 1995, basin-wide Mediterranean Sea; the source dynamic simulation period is 1995–2016. Pooling does not change geographic or temporal coverage. The derived model has 69 unchanged non-detrital groups and one nonliving pooled compartment.

## Departures from the publication

- Source group 70 Discards and group 71 Detritus become group 70 **{POOL_NAME}**. Biomass and biomass_habitat_area are summed in their common t/km² basis: 0.07582324 + 0.44 = **0.51582324**.
- Each feeding consumer retains its original diet entries for prey 1–69 and its diet-import value. Published prey-70 and prey-71 proportions are summed exactly, without normalization. Unknown nonfeeding diet proportions remain unknown. Living-group parameters, source strings and fisheries values are preserved.
- The source does not report detritus routing. On 14 November 2026 the researcher explicitly authorized **100% of detritus-directed flows to pooled group 70**, including its own routing. This is a calculation assumption, not a recovered source value. The runtime EE-floor external nonfishery sink remains separate and must not be redirected into this pool.
- The two published detrital EE values, 0.4894103 and 0.03464372, cannot be averaged into a justified pooled EE. The canonical pooled EE remains unknown (`-9999`, input flag false); source values remain in the ledger. Shared TL=1 and pp=2 are retained. BA, imports, exports and other unknown inputs remain unknown.
- Both detrital groups lack source landings; the pooled source landings remain missing. Their 37 fleet-discard values are explicit zeros and sum to zero. Living fishery-discard quantities remain unchanged. No discard return is added by this builder; a runtime return to the single pool must occur exactly once.
- Any authorized runtime EE adjustment to `1 - M0_to_detritus / P` must retain the source living EE values here and document its before/after values and the separate external sink in runtime evidence. This builder does not calculate or change runtime EE.
- The inherited administrative `selected=false` and `production_eligible=false` fields are removed from scientific JSON and retained in [input provenance](inputs/provenance.json). This is a distinct model with no inherited researcher decision, exclusions, selection or numerical eligibility.

Pooling preserves the documented aggregate diet and biomass quantities, but it is not evidence that the two original compartments have equivalent dynamics or that their unpublished routing has been recovered. Source balance conflicts and missing inputs remain relevant. The original diagnostics do not establish this variant's diagnostic outcome.

## Evidence links

- [Original model notes](../{SOURCE_ID}/model_notes.md)
- [Original parameter and diet workbook](../../sources/41598_2022_18017_MOESM1_ESM-75e4d6d3.xlsx)
- [Input provenance](inputs/provenance.json)
- [Complete aggregation, crosswalk and missingness ledger](results/diagnostics/pooled_20261114/aggregation_ledger.json)
- [Reproducible canonical builder](results/diagnostics/pooled_20261114/code/build_pooled_model.py)

The canonical builder performs no solver run, selection, regional arithmetic, researcher registration or publication. Diagnostic evidence produced separately applies only to its explicitly recorded configuration.
"""
    outputs = {
        model_dir / "model.json": model_bytes,
        model_dir / "model_notes.md": notes.encode("utf-8"),
        provenance_path: (json.dumps(provenance, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        ledger_path: (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    }
    # Preflight every destination before the first write, including provenance.
    for path, content in outputs.items():
        if path.exists() and path.read_bytes() != content:
            raise RuntimeError(f"Refusing to replace a differing existing file: {path}")
    for path, content in outputs.items():
        write_once_or_identical(path, content)
    assert sha(source_path.read_bytes()) == SOURCE_SHA256
    print(json.dumps({"model_id": TARGET_ID, "source_unchanged": True,
                      "derived_sha256": sha(model_bytes), "counts": ledger["counts"],
                      "outputs": [str(path) for path in outputs]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
